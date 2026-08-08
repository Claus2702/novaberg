"""
Admin-Endpunkte — Pixie-Steuerung für Tests und Wartung.
"""

import logging

from fastapi import APIRouter

from config import redis_client

logger = logging.getLogger("ki_server.admin")

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/pixie/pause")
def pixie_pausieren():
    """Pausiert Pixie. Scheduler-Job läuft weiter, aber überspringt die Arbeit."""
    redis_client.set("pixie:paused", "1")
    logger.info("Admin: Pixie pausiert")
    return {"status": "paused"}


@router.post("/pixie/resume")
def pixie_fortsetzen():
    """Setzt Pixie fort."""
    redis_client.delete("pixie:paused")
    logger.info("Admin: Pixie fortgesetzt")
    return {"status": "resumed"}


@router.get("/pixie/status")
def pixie_status():
    """Gibt den Pixie-Status zurück."""
    paused: bool = redis_client.exists("pixie:paused") > 0
    return {"paused": paused}
