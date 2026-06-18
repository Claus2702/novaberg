"""Shadow Agent — Shared Utilities."""

import json
import logging
from datetime import datetime

import redis

from config import PIXIE_AKTIV

logger = logging.getLogger("ki_server.shadow")


# ─────────────────────────────────────────────
# Queue befüllen (wird vom Hauptgraph aufgerufen)
# ─────────────────────────────────────────────
def shadow_queue_push(
    redis_client: redis.Redis,
    user_id:      str,
    aufgabe:      str,
    thema:        str,
    kontext:      str = "",
    prioritaet:   float = 0.0,
    intentionen:  list = None,
    emotion:      str  = "",
    modus:        str  = "",
) -> None:
    """Legt einen Auftrag in die Shadow-Queue."""

    if not PIXIE_AKTIV:
        logger.debug("shadow_agent.utils: shadow_queue_push uebersprungen (PIXIE_AKTIV=False)")
        return

    eintrag: dict = {
        "aufgabe":     aufgabe,
        "user_id":     user_id,
        "thema":       thema,
        "kontext":     kontext,
        "prioritaet":  prioritaet,
        "intentionen": intentionen or [],
        "emotion":     emotion,
        "modus":       modus,
        "erstellt":    datetime.now().isoformat(),
    }

    redis_client.rpush(
        f"shadow_queue:{user_id}",
        json.dumps(eintrag, ensure_ascii=False),
    )

    logger.info(f"Shadow-Queue: '{aufgabe}' für '{user_id}' — {thema[:60]}")
