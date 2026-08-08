"""
ChatWorker — bedient die Rolle `chat` (interaktive Chat-Antworten).

Verantwortlich fuer die Chat-Calls aller Konsumenten (Nova-Antwortpfad,
Pixie-Sprach-Calls nach Konsolidierung in Block 4). Im Gegensatz zu Embed
ist Chat textproduzierend und kann strikt-JSON-Output erwarten (Klassifika-
tionen, strukturierte Tools). JSON-Post-Processing lebt im Worker, nicht im
Provider — damit der Provider dumb bleibt und alle Workarounds an einer
Stelle stehen (`services.postprocess`).

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
from services import postprocess
from services.model_services.types import ChatRequest, ChatResponse
from services.model_services.worker_base import ModelWorker

logger = logging.getLogger(__name__)


def _leere_antwort_melden(
    worker: str, caller: str, text: str, antwort: object,
) -> None:
    """Meldet eine Antwort ohne Zeichen — und was die Ursache entscheidet.

    Steht als eigene Funktion, weil eine Waechterkette die Zweigzahl ihres
    Aufrufers bestimmt und dort nichts erklaert.

    **`thinking` gehoert in die Meldung.** Ist es gefuellt, hat das Modell
    gedacht und nichts gesagt; ist es ebenfalls leer, liegt es an der
    Aufbereitung. Bis zum 01.08.2026 lag dieser Beleg im Antwortobjekt und
    wurde verworfen — zwei verlorene Turns lang war die Ursache deshalb nicht
    entscheidbar (novaberg-bugs.md -> RESPONDER-LEERE-ANTWORT-STILL).

    Vorbedingung: keine.
    Nachbedingung: Bei nicht-leerem Text geschieht nichts.
    """
    if text.strip():
        return

    denkspur: str = (getattr(antwort, "thinking", "") or "").strip()
    logger.error(
        "ChatWorker '%s': LEERE Antwort (caller=%s, tokens=%d, "
        "thinking_len=%d, thinking_anfang='%s') — kein Text trotz verbrauchter "
        "Token. Der Aufrufer bekommt eine leere Zeichenkette und muss sie als "
        "Fehlschlag behandeln.",
        worker, caller, getattr(antwort, "token_total", -1),
        len(denkspur), denkspur[:160].replace("\n", " "),
    )


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
        `start()` ruft die Registry beim lifespan).
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
            "ChatWorker '%s': caller=%s, messages=%d, expect_json=%s, "
            "think=%s, backend=%s",
            self._name,
            caller_label,
            len(request.messages),
            request.expect_json,
            request.think,
            type(self._backend).__name__,
        )

        # ── Verarbeitung ────────────────────────────
        # think wird IMMER mitgegeben (bool, Default False) — der Provider-
        # Default-Pfad ist damit eindeutig: ohne think-Override sieht der
        # Provider explizit think=False. Die optionalen Sampling-Parameter
        # (system, temperature, top_p, ...) hingegen nur dann, wenn der
        # Konsument sie wirklich gesetzt hat — so greifen Provider-Defaults
        # bei None.
        kwargs: dict[str, Any] = {
            "messages":    request.messages,
            "think":       request.think,
            "caller":      caller_label,
        }
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
        if request.num_ctx is not None:
            kwargs["num_ctx"] = request.num_ctx

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
                logger.exception(
                    "ChatWorker '%s': JSON-Parsing fehlgeschlagen (caller=%s, "
                    "fehler=%s, preview='%s...')",
                    self._name,
                    caller_label,
                    exc,  # noqa: TRY401  — Blatt-Typ
                    preview,
                )
                raise

        # ── Ausgabe-Verifikation ────────────────────
        # **Eine leere Antwort ist kein Ergebnis.** Bis zum 01.08.2026 stand
        # unter dieser Marke ausschliesslich die Logzeile unten: Sie MELDETE
        # die Laenge, ohne sie zu pruefen, und `text_len=0` lief als INFO durch
        # wie jeder Erfolg. Zwei Turns gingen so verloren — der Responder gab
        # den leeren Text weiter, Thinker und Tribunal bewerteten ihn, und erst
        # die Salienz zwei Knoten spaeter brach ab
        # (novaberg-bugs.md -> RESPONDER-LEERE-ANTWORT-STILL).
        #
        # `thinking` wird dabei mitgemeldet, weil es die Ursache entscheidet:
        # Ist es gefuellt, hat das Modell gedacht und nichts gesagt; ist es
        # ebenfalls leer, liegt es an der Aufbereitung. Der Beleg lag bisher im
        # Antwortobjekt und wurde verworfen.
        _leere_antwort_melden(self._name, caller_label, text, antwort)

        logger.info(
            "ChatWorker '%s': Antwort erhalten (caller=%s, tokens=%d, "
            "text_len=%d, parsed=%s)",
            self._name,
            caller_label,
            antwort.token_total,
            len(text),
            parsed is not None,
        )

        # thinking aus LLMAntwort uebernehmen — Anschluss fuer ThinkingNormalizer
        # (Teil B). Bei think=False oder Anthropic-Backend immer "" (Provider
        # liefert das so). Kein eigenes Post-Processing auf thinking.
        return ChatResponse(
            text=text,
            parsed=parsed,
            token_total=antwort.token_total,
            thinking=antwort.thinking,
        )
