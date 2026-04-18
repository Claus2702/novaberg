"""
Admin-Endpunkte — Pixie-Steuerung für Tests und Wartung.
"""

import asyncio
import logging

from fastapi          import APIRouter, Request
from fastapi.responses import JSONResponse

from config import redis_client, ollama_gpu_client, EMBED_MODEL, POSTGRES_URL
from services.shadow_agent import schatten_arbeit_ausfuehren, discover_tasks

logger = logging.getLogger("ki_server.admin")

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/pixie/pause")
def PixiePausieren():
    """Pausiert Pixie. Scheduler-Job läuft weiter, aber überspringt die Arbeit."""
    redis_client.set("pixie:paused", "1")
    logger.info("Admin: Pixie pausiert")
    return {"status": "paused"}


@router.post("/pixie/resume")
def PixieFortsetzen():
    """Setzt Pixie fort."""
    redis_client.delete("pixie:paused")
    logger.info("Admin: Pixie fortgesetzt")
    return {"status": "resumed"}


@router.get("/pixie/status")
def PixieStatus():
    """Gibt den Pixie-Status zurück."""
    paused: bool = redis_client.exists("pixie:paused") > 0
    return {"paused": paused}


@router.post("/pixie/flush")
def PixieFlush(request: Request):
    """
    Führt alle Pixie-Tasks synchron aus und kehrt erst zurück
    wenn alle Queues leer sind. Für kontrollierte Testläufe.

    Wiederholt den kompletten Durchlauf bis keine Arbeit mehr anfällt
    (Promotion kann neue hash_dirty-Flags erzeugen → zweiter Durchlauf nötig).
    """
    logger.info("Admin: Pixie-Flush gestartet")

    task_registry: dict = discover_tasks()
    gesamt: int = 0
    durchlauf: int = 0
    max_durchlaeufe: int = 5

    while durchlauf < max_durchlaeufe:
        durchlauf += 1

        verarbeitet: int = schatten_arbeit_ausfuehren(
            redis_client   = redis_client,
            postgres_url   = POSTGRES_URL,
            embed_client   = ollama_gpu_client,
            embed_model    = EMBED_MODEL,
            task_registry  = task_registry,
            shutdown_event = None,
        )

        gesamt += verarbeitet
        logger.info(f"Admin: Flush Durchlauf {durchlauf} — {verarbeitet} Aufträge")

        if verarbeitet == 0:
            break

    logger.info(f"Admin: Pixie-Flush abgeschlossen — {gesamt} Aufträge in {durchlauf} Durchläufen")

    return {
        "status": "flushed",
        "auftraege_gesamt": gesamt,
        "durchlaeufe": durchlauf,
    }
