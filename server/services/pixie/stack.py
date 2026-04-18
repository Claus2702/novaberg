"""Pixie Stack — Ergebnis auf den Shadow-Stack schreiben.

Extrahiert aus: services/shadow_agent/utils.py (stack_push)
"""

import json
import logging
from datetime import datetime

import redis

logger = logging.getLogger("ki_server.pixie.stack")


def stack_push(
    redis_client:  redis.Redis,
    user_id:       str,
    aufgabe:       str,
    thema:         str,
    inhalt:        str,
    embed_client,
    embed_model:   str,
    intentionen:   list = None,
    emotion:       str  = "",
    modus:         str  = "",
) -> None:
    """Legt ein Ergebnis mit Embedding und Meta-Daten auf den Shadow-Stack."""

    embed_text: str = f"{thema} {inhalt[:200]}"

    try:
        embedding: list[float] = embed_client.embed(
            model = embed_model,
            input = embed_text,
        )["embeddings"][0]
    except Exception as fehler:
        logger.warning(f"Shadow-Stack: Embedding fehlgeschlagen — {fehler}")
        embedding = []

    eintrag: dict = {
        "aufgabe":     aufgabe,
        "thema":       thema,
        "inhalt":      inhalt,
        "erstellt":    datetime.now().isoformat(),
        "embedding":   embedding,
        "intentionen": intentionen or [],
        "emotion":     emotion,
        "modus":       modus,
    }

    redis_client.rpush(
        f"shadow_stack:{user_id}",
        json.dumps(eintrag, ensure_ascii=False),
    )

    logger.info(f"Shadow-Stack: '{aufgabe}' für '{user_id}' abgelegt (Embedding: {len(embedding)} dims).")
