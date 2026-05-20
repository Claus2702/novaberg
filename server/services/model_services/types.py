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
