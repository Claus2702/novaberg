"""
Worker-Registry — verwaltet Lifecycle aller Model-Worker.

Diese Modul stellt die zentrale Anlaufstelle fuer Konsumenten dar:

    from services.model_services.registry import model_service

    response = await model_service.embed.submit(EmbedRequest(text="..."))
    antwort  = await model_service.chat.submit(ChatRequest(messages=[...]))
    antwort  = await model_service.background.submit(BackgroundRequest(...))

Beim Server-Startup wird `model_service.startup()` gerufen, beim Shutdown
entsprechend `shutdown()`.

Backend-Wahl pro Worker: gesteuert ueber `config.MODEL_WORKER_BACKENDS`.
Jeder Wert dort waehlt einen Backend-Builder in `_build_backend`. Wechsel
zwischen Ollama-GPU/CPU und Anthropic erfolgt rein konfigurativ (Env).
"""

from __future__ import annotations

import logging

from config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    MODEL_WORKER_BACKENDS,
    OLLAMA_CPU_NUM_CTX,
    OLLAMA_GPU_NUM_CTX,
    OLLAMA_MODEL,
    PIXIE_ANALYSE_MODEL,
    PIXIE_ANALYSE_NUM_CTX,
    SHADOW_MODEL,
    ollama_cpu_client,
    ollama_gpu_client,
)
from services.llm_provider import AnthropicProvider, LLMProvider, OllamaProvider
from services.model_services.background_worker import BackgroundWorker
from services.model_services.chat_worker import ChatWorker
from services.model_services.embed_worker import EmbedWorker

logger = logging.getLogger(__name__)


def _build_backend(kind: str) -> LLMProvider:
    """Baut die LLMProvider-Instanz fuer einen Worker aus dem Config-Schluessel.

    Vorbedingung: `kind` ist einer der Werte aus `MODEL_WORKER_BACKENDS`.
    Erlaubt: "ollama_gpu", "ollama_cpu_analyse", "ollama_cpu_sprache",
    "anthropic".
    Nachbedingung: Rueckgabe ist ein einsatzbereiter LLMProvider.
    Fehlerfaelle: ValueError bei unbekanntem Schluessel (fail-loud, kein
    silent default — Developer-Handbook §3).
    """
    # ── Eingabe-Validierung & Verarbeitung ──────
    if kind == "ollama_gpu":
        return OllamaProvider(ollama_gpu_client, OLLAMA_MODEL, OLLAMA_GPU_NUM_CTX)
    if kind == "ollama_cpu_analyse":
        return OllamaProvider(
            ollama_cpu_client, PIXIE_ANALYSE_MODEL, PIXIE_ANALYSE_NUM_CTX
        )
    if kind == "ollama_cpu_sprache":
        return OllamaProvider(ollama_cpu_client, SHADOW_MODEL, OLLAMA_CPU_NUM_CTX)
    if kind == "anthropic":
        if not ANTHROPIC_API_KEY:
            raise ValueError(
                "Worker-Backend 'anthropic' gewaehlt, aber ANTHROPIC_API_KEY "
                "ist nicht gesetzt"
            )
        return AnthropicProvider(ANTHROPIC_MODEL, ANTHROPIC_API_KEY)

    # ── Fail-loud ───────────────────────────────
    raise ValueError(f"Unbekanntes Worker-Backend: {kind!r}")


class ModelServiceRegistry:
    """Container fuer alle Model-Worker.

    Worker-Set in Block 2:
        - embed (Phase 2 Block 1): nomic-embed-text-v2-moe auf GPU (A4 Chat 107)
        - chat (Phase 2 Block 2): Chat-Antworten, Backend laut Config
        - background (Phase 2 Block 2): Pixie-Hintergrund, Dual-Backend
    """

    def __init__(self) -> None:
        """Erzeugt alle Worker mit den Backends laut config.MODEL_WORKER_BACKENDS.

        Vorbedingung: config.MODEL_WORKER_BACKENDS enthaelt gueltige
        Backend-Schluessel.
        Nachbedingung: Alle Worker sind instanziiert (aber nicht gestartet).
        """
        # ── Embed-Worker (unveraendert aus Block 1) ──
        self.embed: EmbedWorker = EmbedWorker()

        # ── ChatWorker (Block 2) ─────────────────────
        chat_kind: str = MODEL_WORKER_BACKENDS["chat"]
        logger.info("Registry: chat-Worker erhaelt Backend '%s'", chat_kind)
        self.chat: ChatWorker = ChatWorker(
            name="chat",
            backend=_build_backend(chat_kind),
        )

        # ── BackgroundWorker (Block 2) ───────────────
        analyse_kind: str = MODEL_WORKER_BACKENDS["background_analyse"]
        sprache_kind: str = MODEL_WORKER_BACKENDS["background_sprache"]
        logger.info(
            "Registry: background-Worker erhaelt Backends "
            "analyse='%s', sprache='%s'",
            analyse_kind,
            sprache_kind,
        )
        self.background: BackgroundWorker = BackgroundWorker(
            name="background",
            analyse_backend=_build_backend(analyse_kind),
            sprache_backend=_build_backend(sprache_kind),
        )

        logger.info(
            "ModelServiceRegistry initialisiert (Worker: embed, chat, background)"
        )

    async def startup(self) -> None:
        """Startet alle Worker. FastAPI-Lifespan ruft das beim Server-Start."""
        logger.info("ModelServiceRegistry: startup() beginnt")
        await self.embed.start()
        await self.chat.start()
        await self.background.start()
        logger.info("ModelServiceRegistry: alle Worker gestartet")

    async def shutdown(self) -> None:
        """Beendet alle Worker sauber. FastAPI-Lifespan ruft das beim Shutdown."""
        logger.info("ModelServiceRegistry: shutdown() beginnt")
        await self.background.shutdown()
        await self.chat.shutdown()
        await self.embed.shutdown()
        logger.info("ModelServiceRegistry: alle Worker beendet")


# Singleton-Instanz fuer globalen Zugriff
model_service = ModelServiceRegistry()
