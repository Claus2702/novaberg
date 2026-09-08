"""Admin-Endpunkte — Pixie-Steuerung für Tests und Wartung."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from config import redis_client
from memory.quality_profile import profil_lauf

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


# ── Der Messschalter fuer die Umfangszeile ────────────────────────────
#
# **Wozu er da ist.** `UMFANGSREGLER-BINDET-NICHT` verlangt als Pruefform
# *„dieselbe Turnreihe desselben Reizes mit und ohne Block"*. Ohne einen
# Schalter zur Laufzeit gaebe es diese Reihe nicht: Zwei Faehrten, durch
# einen Neustart getrennt, sind nicht dieselbe Reihe — dazwischen liegen ein
# Kaltstart, ein geleerter Prefix-Cache und ein gewachsenes Gedaechtnis.
#
# **Er liegt in Redis und nicht in der Umgebung**, aus demselben Grund wie
# `pixie:paused` (`F-MESS-2`): Eine Umgebungsvariable wird beim Import
# gelesen und waere nur mit einem Neustart zu aendern — also genau das, was
# hier vermieden werden soll.
#
# **Er ist ein Instrument und kein Merkmal.** Steht er, fehlt Nova die
# einzige Laengenzahl im Prompt; das ist im Betrieb ein Defekt und nur
# waehrend einer Messreihe erwuenscht. Deshalb meldet der Responder seinen
# Stand bei JEDEM Turn als `warning` — ein vergessener Schalter soll im Log
# schreien, nicht schweigen.
REGIE_AUS_SCHLUESSEL: str = "mess:regie_aus"


@router.post("/regie/aus")
def regie_abschalten():
    """Nimmt die Umfangszeile aus dem Responder-Prompt — nur fuer Messreihen."""
    redis_client.set(REGIE_AUS_SCHLUESSEL, "1")
    logger.warning(
        "Admin: Umfangszeile abgeschaltet — Nova bekommt ab jetzt KEINE "
        "Laengenvorgabe. Das ist ein Messzustand, kein Betriebszustand."
    )
    return {"regie_aus": True}


@router.post("/regie/an")
def regie_einschalten():
    """Stellt die Umfangszeile wieder her."""
    redis_client.delete(REGIE_AUS_SCHLUESSEL)
    logger.info("Admin: Umfangszeile wieder im Prompt")
    return {"regie_aus": False}


@router.get("/regie/status")
def regie_status():
    """Sagt, ob die Umfangszeile gerade im Prompt steht."""
    aus: bool = redis_client.exists(REGIE_AUS_SCHLUESSEL) > 0
    return {"regie_aus": aus}


@router.get("/naehte")
def naht_spannen(tage: int = 0):
    """Ist-Spanne gegen Zielspanne je Naht, in zwei Zeitfenstern.

    **Fuer das Naht-Panel des Clients.** Er zeigt, welche Groesse ihre
    Zielspanne verlaesst und welche sie kaum ausschoepft — die zweite
    Richtung hat sonst keinen Waechter.

    Args:
        tage: Breite des jungen Fensters. 0 nimmt den Vorgabewert.

    Returns:
        `{"tage": int, "naehte": [...], "fehler": int}`.
    """
    from memory.naht_spannen import FENSTER_TAGE, spannen_erheben

    ergebnis: dict = spannen_erheben(tage or FENSTER_TAGE)
    logger.info(
        "Admin: Naht-Spannen abgefragt — %d Naehte, %d Fehler",
        len(ergebnis["naehte"]), ergebnis["fehler"],
    )
    return ergebnis


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


@router.post("/qualitaet/lauf")
def qualitaetsprofil_lauf(deckel: int = 0):
    """Stoesst den Profil-Lauf an, der sonst nur im Tageslauf laeuft.

    **Der Lauf braucht den Serverprozess**, und das ist der Grund fuer diesen
    Endpunkt: `traeger_profilieren` ruft den Hintergrund-Worker, und der lebt
    im Lifespan der Anwendung. Ein Labor-Skript daneben bekommt ihn nicht —
    `submit_sync` scheitert dort mit *Worker nicht gestartet*.

    Damit ist der Schritt messbar, ohne auf den naechsten Tageslauf zu warten;
    er schreibt dasselbe wie dort, nur frueher.

    Args:
        deckel: Wie viele Traeger hoechstens. 0 nimmt den Vorgabewert des
            Tageslaufs (`QUALITAET_PROFIL_JE_LAUF`).

    Returns:
        Die Buchfuehrung des Laufs — versucht, profiliert, gescheitert,
        Bestand und `error`.
    """
    ergebnis: dict = profil_lauf(deckel=deckel)
    logger.info(
        f"Admin: Qualitaetsprofil-Lauf angestossen — "
        f"{ergebnis['profiliert']} von {ergebnis['versucht']} profiliert"
    )
    if ergebnis.get("error"):
        return JSONResponse(status_code=500, content=ergebnis)
    return ergebnis
