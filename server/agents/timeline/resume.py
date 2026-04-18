"""Resume-Node — Loest User-Antworten auf Rueckfragen auf.

Ein Szenario: Disambiguierung (User waehlt einen von mehreren Termin-Kandidaten).
Kein Duplikat-Szenario wie bei Notizen — gleiche Titel sind bei Terminen normal.
"""

import json
import logging

from agents.base import AgentState

logger = logging.getLogger("ki_server.agents.timeline.resume")


def resume(state: AgentState) -> dict:
    """Loest die User-Antwort auf eine Rueckfrage auf."""
    user_answer = state["parameter"].get("user_answer", "")
    rueckfrage = state["parameter"].get("original_rueckfrage", "")
    action = state["parameter"].get("action", "")

    logger.debug(f"resume: Einstieg — action='{action}', user_answer='{user_answer[:80]}', "
                 f"rueckfrage='{rueckfrage[:80]}'")

    # Disambiguierung-JSON parsen
    try:
        disamb = json.loads(rueckfrage)
        if disamb.get("typ") == "disambiguierung":
            return _resume_disambiguierung(state, disamb, user_answer)
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback: Konnte Rueckfrage-Typ nicht erkennen
    logger.warning(f"resume: Unbekannter Rueckfrage-Typ — rueckfrage='{rueckfrage[:100]}'")
    return {
        "status": "fehler",
        "fehler": "Konnte die Rueckfrage-Antwort nicht zuordnen.",
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "unbekannt"}],
    }


def _resume_disambiguierung(state: AgentState, disamb: dict, user_answer: str) -> dict:
    """User hat einen Kandidaten aus der Disambiguierung gewaehlt."""

    kandidaten = disamb.get("kandidaten", [])
    action = disamb.get("aktion", state["parameter"].get("action", ""))

    logger.debug(f"_resume_disambiguierung: {len(kandidaten)} Kandidaten, action='{action}', "
                 f"user_answer='{user_answer}'")

    if not kandidaten:
        return {
            "status": "fehler",
            "fehler": "Keine Kandidaten in der Disambiguierung.",
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "keine_kandidaten"}],
        }

    # Zuordnung: Pruefe ob die User-Antwort einen Kandidaten-Titel enthaelt
    user_lower = user_answer.lower()
    match = None

    for k in kandidaten:
        if k["title"].lower() in user_lower:
            match = k
            logger.debug(f"_resume_disambiguierung: Match via Titel — '{k['title']}'")
            break

    # Fallback: Pruefe auf Datum-Angabe im Kandidaten
    if not match:
        for k in kandidaten:
            datum = k.get("datum", "")
            if datum and datum in user_answer:
                match = k
                logger.debug(f"_resume_disambiguierung: Match via Datum — '{datum}'")
                break

    # Fallback: Pruefe auf ID oder Position ("die erste", "Nummer 2")
    if not match:
        for i, k in enumerate(kandidaten):
            if str(i + 1) in user_answer or str(k.get("id", "")) in user_answer:
                match = k
                logger.debug(f"_resume_disambiguierung: Match via Index/ID — '{k['title']}'")
                break

    # Fallback: Bei genau 2 Kandidaten und "erste"/"zweite"
    if not match and len(kandidaten) == 2:
        if any(w in user_lower for w in ["erste", "ersten", "obere", "1"]):
            match = kandidaten[0]
            logger.debug(f"_resume_disambiguierung: Match via 'erste' — '{match['title']}'")
        elif any(w in user_lower for w in ["zweite", "zweiten", "untere", "2", "andere"]):
            match = kandidaten[1]
            logger.debug(f"_resume_disambiguierung: Match via 'zweite' — '{match['title']}'")

    if not match:
        # User-Antwort zu ungenau — erneute Rueckfrage
        logger.info("_resume_disambiguierung: Kein Match — erneute Rueckfrage")
        return {
            "status": "rueckfrage",
            "rueckfrage": json.dumps({
                "typ": "disambiguierung",
                "agent": "timeline",
                "aktion": action,
                "kandidaten": kandidaten,
            }, ensure_ascii=False),
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "kein_match"}],
        }

    logger.info(f"_resume_disambiguierung: Kandidat gewaehlt — id={match.get('id')}, title='{match['title']}'")

    return {
        "parameter": {
            **state["parameter"],
            "action": action,
            "termin": match,
            "resume": False,
        },
        "status": "laufend",
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": f"gewaehlt: {match['title']}"}],
    }
