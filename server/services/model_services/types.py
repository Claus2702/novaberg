"""
Datentypen für die Model-Service-Schicht.

Diese Modul definiert die Übergabe-Typen zwischen Konsument und Worker:
- ModelRequest: was der Konsument einreicht (Prompt + optionale Overrides)
- ModelResponse: was der Worker zurückgibt (Resultat + Metadaten)

Konvention: Konsumenten kennen weder Modellnamen noch Provider-Spezifika.
Sie kennen nur ihre abstrakte Rolle (chat / background / embed).
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class EmbedRequest:
    """
    Request-Objekt für den EmbedWorker.

    Der Konsument reicht den zu embeddenden Text plus optionale Overrides ein.
    Der Worker erzeugt das Future in `submit()` im laufenden Event-Loop und
    hängt es an das Request — Konsumenten dürfen `EmbedRequest` auch aus
    Worker-Threads ohne eigenen Loop instanziieren.

    Attribute:
        text: Der zu embeddende Text (Pflicht).
        request_id: Eindeutige ID für Tracing (Default: uuid4).
        submitted_at: Unix-Timestamp der Einreichung (Default: time.time()).
        future: Wird vom Worker beim Submit angelegt und mit dem Resultat
                befüllt. Bei Konstruktion None, weil das Future-Erzeugen
                einen laufenden Loop in *diesem* Thread bräuchte.
    """

    text: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    submitted_at: float = field(default_factory=time.time)
    future: asyncio.Future["EmbedResponse"] | None = None


@dataclass
class EmbedResponse:
    """
    Response-Objekt vom EmbedWorker.

    Trägt das Embedding-Vektor plus Metadaten für Logging und Tracing.

    Attribute:
        embedding: Der erzeugte Vektor (list[float]).
        model_name: Modellname, mit dem der Worker das Embedding erzeugt hat.
        duration_seconds: Zeit vom Worker-Pickup bis Antwort.
        request_id: Spiegelt die request_id aus EmbedRequest.
    """

    embedding: list[float]
    model_name: str
    duration_seconds: float
    request_id: str


# ─────────────────────────────────────────────────────
# ChatWorker (Rolle "chat")
# ─────────────────────────────────────────────────────

@dataclass
class ChatRequest:
    """Anfrage an den ChatWorker (Rolle 'chat').

    Wird von Konsumenten gefuellt und ueber `model_service.chat.submit(...)`
    eingereicht. Der Worker erzeugt das Future in `submit()` im laufenden
    Event-Loop und haengt es an das Request — Konsumenten duerfen Requests
    aus Worker-Threads ohne eigenen Loop instanziieren (Loop-Binding-Lesson,
    `docs/novaberg-lesson_l_loop-binding.md`).

    Attribute:
        messages: Chat-Verlauf im OpenAI/Ollama-Format
                  ([{"role": "system"|"user"|"assistant", "content": ...}, ...]).
        system: Optionaler System-Prompt; wird vom Provider vor `messages`
                gestellt. None = kein Override (Provider-Default greift).
        temperature: Sampling-Temperatur. None = Backend-Default.
        expect_json: True ⇒ Worker parst die Antwort strikt als JSON und
                     belegt `parsed`. Fehlerhaft → Future wirft.
        top_p, repeat_penalty, presence_penalty, max_output_tokens:
                     Optionale Sampling-Overrides. None ⇒ Provider-Default.
        caller: Freitext zur Identifikation im Token-Log (z.B. "agent.chat",
                "promotion_klassifikation"). Wird im Worker an den Provider
                durchgereicht.
        future: Wird vom Worker beim Submit angelegt — KEIN
                `field(default_factory=asyncio.Future)`, sonst entsteht eine
                Future ohne laufenden Loop (Loop-Binding-Lesson).
    """

    messages:          list[dict]
    system:            Optional[str]   = None
    temperature:       Optional[float] = None
    expect_json:       bool            = False
    top_p:             Optional[float] = None
    repeat_penalty:    Optional[float] = None
    presence_penalty:  Optional[float] = None
    max_output_tokens: Optional[int]   = None
    caller:            str             = ""
    future:            Optional[asyncio.Future] = None


@dataclass
class ChatResponse:
    """Antwort des ChatWorkers.

    Attribute:
        text: Roh-Text aus dem Provider (bei expect_json bereits gesaeubert
              durch postprocess.parse_json_strict, aber als JSON-String).
        parsed: Geparstes JSON-Dict, falls expect_json=True. Sonst None.
        token_total: Gesamt-Token-Verbrauch (input + output) aus dem Provider.
    """

    text:        str
    parsed:      Optional[dict] = None
    token_total: int            = 0


# ─────────────────────────────────────────────────────
# BackgroundWorker (Rolle "background")
# ─────────────────────────────────────────────────────

@dataclass
class BackgroundRequest:
    """Anfrage an den BackgroundWorker (Rolle 'background').

    Der Background-Worker bedient Pixie-Hintergrund-Tasks. Im Interim haelt
    er zwei Backends parallel — `analyse` (Reasoning, JSON, Klassifikationen)
    und `sprache` (Fliesstext, Deutsch). Konsumenten waehlen ueber `modus`
    pro Anfrage. In Block 4 zeigen beide Backends auf qwen36 (No-Op-Routing,
    siehe `docs/novaberg-microservice-modell-queue_k.md`).

    Attribute:
        messages: Chat-Verlauf im OpenAI/Ollama-Format.
        modus: "analyse" → Analyse-Backend, "sprache" → Sprach-Backend.
               Pflicht. Andere Werte werden vom Worker als Fehler abgelehnt.
        system: Optionaler System-Prompt. None ⇒ Provider-Default.
        temperature: Sampling-Temperatur. None ⇒ Provider-Default.
        expect_json: True ⇒ JSON-Parsing wie beim ChatWorker.
        max_output_tokens: Optionales Token-Limit fuer die Antwort.
        caller: Freitext fuer das Token-Log.
        future: Wird vom Worker beim Submit angelegt (Loop-Binding-Lesson).
    """

    messages:          list[dict]
    modus:             str             = "analyse"
    system:            Optional[str]   = None
    temperature:       Optional[float] = None
    expect_json:       bool            = False
    max_output_tokens: Optional[int]   = None
    caller:            str             = ""
    future:            Optional[asyncio.Future] = None


@dataclass
class BackgroundResponse:
    """Antwort des BackgroundWorkers.

    Attribute:
        text: Roh-Text aus dem Provider (CJK-bereinigt, falls die Schleife
              das durchgefuehrt hat).
        parsed: Geparstes JSON-Dict, falls expect_json=True. Sonst None.
        token_total: Gesamt-Token-Verbrauch (input + output) aus dem Provider.
    """

    text:        str
    parsed:      Optional[dict] = None
    token_total: int            = 0
