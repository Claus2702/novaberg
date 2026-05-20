"""
ChatWorker — bedient die Rolle `chat` (interaktive Chat-Antworten).

Verantwortlich fuer die Chat-Calls aller Konsumenten (Nova-Antwortpfad,
Pixie-Sprach-Calls nach Konsolidierung in Block 4). Im Gegensatz zu Embed
ist Chat textproduzierend und kann strikt-JSON-Output erwarten (Klassifika-
tionen, strukturierte Tools). JSON-Post-Processing lebt im Worker, nicht im
Provider — damit der Provider dumb bleibt und alle Workarounds an einer
Stelle stehen (`services.model_services.postprocess`).

CJK-Guard: bewusst NICHT im ChatWorker. CJK ist ein Qwen-Problem
(Reasoning-Backend); GPU-Chat-Modelle (Mistral/Gemma) leaken kein CJK,
und Anthropic schon gar nicht. Der Schutz liegt im BackgroundWorker, wo
das Analyse-Backend Qwen ist.

Architektur-Doku: docs/novaberg-microservice-modell-queue_k.md §3.
"""

from __future__ import annotations

import asyncio
import logging
from json import JSONDecodeError
from typing import Any

from services.llm_provider import LLMAntwort, LLMProvider
from services.model_services import postprocess
from services.model_services.types import ChatRequest, ChatResponse
from services.model_services.worker_base import ModelWorker

logger = logging.getLogger(__name__)


class ChatWorker(ModelWorker[ChatRequest, ChatResponse]):
    """FIFO-Worker fuer Chat-Anfragen.

    Konsumenten rufen `model_service.chat.submit(ChatRequest(...))` auf und
    bekommen ueber das Future einen ChatResponse zurueck. Der Worker
    serialisiert die Calls (eine Anfrage zur Zeit pro Worker-Instanz) und
    haelt seinen Backend-LLMProvider als Konstruktor-Injektion — der
    Backend-Typ (Ollama-GPU/CPU/Anthropic) wird in der Registry per
    `MODEL_WORKER_BACKENDS["chat"]` ausgewaehlt.
    """

    def __init__(self, name: str, backend: LLMProvider) -> None:
        """Initialisiert den ChatWorker mit einem konkreten Backend.

        Vorbedingung: `backend` ist ein initialisierter LLMProvider
        (OllamaProvider oder AnthropicProvider). `name` ist ein nicht-leerer
        Logical-Name (z.B. "chat").
        Nachbedingung: Worker ist instanziiert (aber noch nicht gestartet —
        `start()` ruft die Registry beim Lifespan).
        Fehlerfaelle: keine — Validierung des Backends erfolgt im
        Konfigurations-Pfad (Registry-Factory).
        """

        # ── Eingabe-Validierung ─────────────────────
        if not name:
            raise ValueError("ChatWorker: 'name' darf nicht leer sein")
        if backend is None:
            raise ValueError("ChatWorker: 'backend' (LLMProvider) ist Pflicht")

        # ── Verarbeitung ────────────────────────────
        super().__init__(name=name)
        self._backend: LLMProvider = backend

        # Modell-Name zum Loggen extrahieren — best effort
        backend_modell: str = getattr(backend, "_model", "?")
        logger.info(
            "ChatWorker '%s' konfiguriert: Backend=%s, Modell=%s",
            name,
            type(backend).__name__,
            backend_modell,
        )

    async def _call_model(self, request: ChatRequest) -> ChatResponse:
        """Fuehrt den Chat-Call gegen das konfigurierte Backend aus.

        Vorbedingung: `request.messages` ist eine nicht-leere Liste von
        Chat-Messages. Worker laeuft (sonst greift die Pruefung in submit).
        Nachbedingung: ChatResponse mit Text und ggf. geparstem JSON.
        Fehlerfaelle:
            - Backend wirft → Exception propagiert (Future-Exception, kein
              silent skip).
            - expect_json + invalid JSON → JSONDecodeError propagiert.
        """

        # ── Eingabe-Validierung ─────────────────────
        if not request.messages:
            raise ValueError(
                f"ChatWorker '{self._name}': 'messages' darf nicht leer sein "
                f"(caller={request.caller!r})"
            )

        caller_label: str = request.caller or "chat_worker"
        logger.info(
            "ChatWorker '%s': caller=%s, messages=%d, expect_json=%s, backend=%s",
            self._name,
            caller_label,
            len(request.messages),
            request.expect_json,
            type(self._backend).__name__,
        )

        # ── Verarbeitung ────────────────────────────
        kwargs: dict[str, Any] = {
            "messages":    request.messages,
            "format_json": False,             # Worker besitzt JSON-Post-Processing
            "caller":      caller_label,
        }
        # Nur explizit gesetzte Overrides durchreichen — sonst greift der
        # Provider-Default (LLMProvider.chat hat system="" und temperature=0.7
        # als Default, die wir nicht ueberschreiben wollen, wenn die Anfrage
        # die Werte nicht spezifiziert).
        if request.system is not None:
            kwargs["system"] = request.system
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.top_p is not None:
            kwargs["top_p"] = request.top_p
        if request.repeat_penalty is not None:
            kwargs["repeat_penalty"] = request.repeat_penalty
        if request.presence_penalty is not None:
            kwargs["presence_penalty"] = request.presence_penalty
        if request.max_output_tokens is not None:
            kwargs["max_output_tokens"] = request.max_output_tokens

        # Provider-chat ist sync — in Thread auslagern, damit die Worker-
        # Schleife nicht blockiert (gleiches Muster wie EmbedWorker).
        antwort: LLMAntwort = await asyncio.to_thread(self._backend.chat, **kwargs)

        text:   str         = antwort.content
        parsed: dict | None = None

        if request.expect_json:
            try:
                parsed = postprocess.parse_json_strict(text)
            except JSONDecodeError as exc:
                preview: str = text[:200].replace("\n", " ")
                logger.error(
                    "ChatWorker '%s': JSON-Parsing fehlgeschlagen (caller=%s, "
                    "fehler=%s, preview='%s...')",
                    self._name,
                    caller_label,
                    exc,
                    preview,
                )
                raise

        # ── Ausgabe-Verifikation ────────────────────
        logger.info(
            "ChatWorker '%s': Antwort erhalten (caller=%s, tokens=%d, "
            "text_len=%d, parsed=%s)",
            self._name,
            caller_label,
            antwort.token_total,
            len(text),
            parsed is not None,
        )

        return ChatResponse(
            text=text,
            parsed=parsed,
            token_total=antwort.token_total,
        )
