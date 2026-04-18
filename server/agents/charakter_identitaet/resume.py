"""Resume-Node fuer CharakterIdentitaetAgent.

Verarbeitet die Antwort auf eine Pflicht-Rueckfrage (HITL-Gate aus db_validieren).

Phase 0: Standard ja/nein/unklar-Interpretation.
Phase 1 (geplant, Fachabteilungs-Epic): Differenzierte Interpretation pro
  rueckfrage_typ (widerspruch, ergaenzung, subtraktiv, konsolidierung).
"""

import logging

from agents.base import AgentState

logger = logging.getLogger("ki_server.agents.charakter_identitaet.resume")


ABLEHNUNG = "abgelehnt"
BESTAETIGUNG = "bestaetigt"
UNKLAR = "unklar"


def resume(state: AgentState) -> dict:
    """Resume-Node: User-Antwort auf Pflicht-Rueckfrage interpretieren.

    Returns:
      - status='abgeschlossen' → User hat abgelehnt, Aktion verworfen
      - status='rueckfrage'    → Antwort unklar, erneut fragen
      - status='laufend'       → User hat bestaetigt, weiter zu ausfuehren
    """
    user_answer = state["parameter"].get("user_answer", "")
    original_rueckfrage = state["parameter"].get("original_rueckfrage", "")
    rueckfrage_typ = state["parameter"].get("rueckfrage_typ", "standard")
    action = state["parameter"].get("action", "")

    logger.debug(
        f"resume: Einstieg -- action='{action}', typ='{rueckfrage_typ}', "
        f"user_answer='{user_answer[:80]}'"
    )

    interpretation = _antwort_interpretieren(rueckfrage_typ, user_answer)

    if interpretation == ABLEHNUNG:
        logger.info(f"resume: User lehnt ab -- action='{action}' verworfen")
        return {
            "status": "dismissed",
            "ergebnis": "Benutzer hat die Aktion abgelehnt. Keine Aenderung vorgenommen.",
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "abgelehnt"}],
        }

    if interpretation == UNKLAR:
        logger.info("resume: Antwort unklar -- erneute Rueckfrage")
        return {
            "status": "rueckfrage",
            "rueckfrage": original_rueckfrage or "Soll ich die Aktion ausfuehren?",
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "unklar"}],
        }

    logger.info(f"resume: User bestaetigt -- action='{action}' wird ausgefuehrt")
    return {
        "parameter": {
            **state["parameter"],
            "resume": False,
        },
        "status": "laufend",
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "bestaetigt"}],
    }


def _antwort_interpretieren(rueckfrage_typ: str, user_answer: str) -> str:
    """Klassifiziert die User-Antwort.

    Strategy-Hook fuer Phase 1: Hier spaeter Dispatch nach rueckfrage_typ
    ('widerspruch', 'ergaenzung', 'subtraktiv', 'konsolidierung').
    Phase 0 nutzt ausschliesslich den 'standard'-Pfad.
    """
    # Phase 1-Andockpunkt:
    # if rueckfrage_typ == "widerspruch": return _widerspruch_interpretieren(user_answer)
    return _standard_interpretieren(user_answer)


def _standard_interpretieren(user_answer: str) -> str:
    """Standard ja/nein-Parsing analog notizen/resume.py (Substring-Match, lower)."""
    text = user_answer.lower().strip()

    if not text:
        return UNKLAR

    ablehnungs_keywords = (
        "nein", "ne", "nee", "nicht",
        "lass", "abbruch", "abbrechen", "stopp", "stop",
    )
    if any(kw in text for kw in ablehnungs_keywords):
        return ABLEHNUNG

    bestaetigungs_keywords = (
        "ja", "jo", "jep", "jepp", "yes",
        "ok", "okay", "klar", "bitte", "mach", "los", "gerne",
    )
    if any(kw in text for kw in bestaetigungs_keywords):
        return BESTAETIGUNG

    return UNKLAR
