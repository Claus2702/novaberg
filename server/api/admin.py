"""Admin-Endpunkte — Pixie-Steuerung für Tests und Wartung."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

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


# `response_model=None` ist Pflicht und keine Zierde: FastAPI leitet aus der
# Rueckgabeannotation ein Antwortmodell ab und wirft beim IMPORT, wenn dort
# ein Response-Typ steht. Der Import passiert in `main.py` auf Modulebene —
# der Fehler nimmt den ganzen Server mit, nicht nur diesen Endpunkt.
#
# `[gemessen]` — 18.08.2026: Die Annotation kam als Abhilfe gegen einen
# Linter-Befund hinzu und legte den Dienst 10 Minuten lahm. Gemerkt hat es
# keine der 1780 gruenen Zeugen: **0 von 126 Testdateien importieren die
# Anwendung.** Und `uvicorn --reload` haelt den Port im Elternprozess, auch
# wenn das Kind beim Import stirbt — die Antwort ist deshalb ein Timeout und
# nicht "Verbindung abgelehnt", und der Behaelterstatus bleibt "Up".
@router.post("/dateien/index", response_model=None)
def dateien_index_lauf() -> dict | JSONResponse:
    """Stoesst einen Lauf des Dateien-Waechters an und gibt seine Bilanz zurueck.

    Vorbedingung: keine.
    Nachbedingung: Die Bilanz des Laufs — je Wurzel und in Summe, samt der
    Zahl der Dateien, die die Obergrenze stehengelassen hat.

    **Von Hand statt nach Zeitplan, und das ist Absicht.** Die Kadenz eines
    Waechters soll der Aenderungsrate des Verzeichnisses folgen; die ist
    nicht erhoben (novaberg-agent-dateien_k.md §8.3). Bis dahin gibt es
    diesen Anstoss statt einer geratenen Zahl im Scheduler.
    """
    from agents import AgentRegistry

    agent = AgentRegistry.finden("dateien_index")
    if agent is None:
        logger.error("Admin: dateien_index nicht in der Registry")
        return JSONResponse(
            status_code=503,
            content={"fehler": "dateien_index nicht registriert"},
        )

    zustand = agent.invoke({
        "aufgabe": "Indexlauf von Hand", "aufgabe_typ": "workflow",
        "agent_name": "dateien_index", "kontext": {}, "parameter": {},
        "schritte": [], "ergebnis": None, "status": "laufend",
        "rueckfrage": None, "fehler": None,
    })

    logger.info("Admin: Indexlauf beendet — status=%s", zustand.get("status"))
    return {"status": zustand.get("status"), "bilanz": zustand.get("ergebnis")}
