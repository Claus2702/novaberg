"""Pixie Stack — Ergebnis auf den Shadow-Stack schreiben.

Extrahiert aus: services/shadow_agent/utils.py (stack_push)
"""

import json
import logging
from datetime import datetime

import redis

from config import PIXIE_AKTIV
from services.model_services import model_service, EmbedRequest

logger = logging.getLogger("ki_server.pixie.stack")


def stack_push(
    redis_client:  redis.Redis,
    user_id:       str,
    aufgabe:       str,
    thema:         str,
    inhalt:        str,
    intentionen:   list = None,
    emotion:       str  = "",
    modus:         str  = "",
    salienz:       float | None = None,
    arousal:       float | None = None,
) -> None:
    """Legt ein Ergebnis mit Embedding und Meta-Daten auf den Shadow-Stack.

    Args:
        redis_client: Verbindung.
        user_id: Paar-Kennung.
        aufgabe: Art des Auftrags (`recherche`, `nachfragen`, …).
        thema: Gegenstand, geht in das Embedding ein.
        inhalt: das Destillat.
        intentionen: Absichten des ausloesenden Turns.
        emotion: Gefuehlslage, in der der Auftrag entstand.
        modus: Gespraechsmodus, in dem er entstand.
        salienz: der **ausloesende** Wert, (0.0, 1.0]. Traegt die Rangfolge,
            wenn kein Bezugsvektor vorliegt — der haeufigste Fall.
        arousal: die Erregung, in der der Gedanke gefasst wurde. Sie hebt
            Novas Zustand beim Einwurf, wenn er niedriger liegt (Bauteil B).

    **`None` heisst unbekannt und wird nie zu einer Zahl.** Beide Werte stehen
    ausdruecklich im Eintrag, auch wenn sie fehlen: Ein weggelassenes Feld
    waere von einem Eintrag alter Bauart nicht zu unterscheiden, eine 0.0
    saehe aus wie eine Messung. Wer sie liest, prueft auf `None` und reiht
    einen Eintrag ohne Wert hinten ein, statt ihn mit null zu bewerten.
    """
    if not PIXIE_AKTIV:
        logger.debug("pixie.stack: stack_push uebersprungen (PIXIE_AKTIV=False)")
        return

    embed_text: str = f"{thema} {inhalt[:200]}"

    embed_response = model_service.embed.submit_sync(EmbedRequest(text=embed_text))
    embedding: list[float] = embed_response.embedding
    logger.debug(
        "Stack-Push: Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
        len(embedding),
        embed_response.duration_seconds,
    )

    eintrag: dict = {
        "aufgabe":     aufgabe,
        "thema":       thema,
        "inhalt":      inhalt,
        "erstellt":    datetime.now().isoformat(),
        "embedding":   embedding,
        "intentionen": intentionen or [],
        "emotion":     emotion,
        "modus":       modus,
        "salienz":     salienz,
        "arousal":     arousal,
    }

    redis_client.rpush(
        f"shadow_stack:{user_id}",
        json.dumps(eintrag, ensure_ascii=False),
    )

    logger.info(f"Shadow-Stack: '{aufgabe}' für '{user_id}' abgelegt (Embedding: {len(embedding)} dims).")
