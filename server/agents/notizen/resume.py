"""Resume-Nodes -- Loest User-Antworten auf Rueckfragen auf.

Zwei Szenarien: Disambiguierung (User waehlt einen Kandidaten)
und Duplikat-Aufloesung (aktualisieren oder neue anlegen).
"""

import json
import logging

from agents.base import AgentState

logger = logging.getLogger("ki_server.agents.notizen.resume")


def resume(state: AgentState) -> dict:
    """Loest die User-Antwort auf eine Rueckfrage auf.

    Zwei Szenarien:
    1. Disambiguierung: User waehlt einen von mehreren Kandidaten
    2. Duplikat: User sagt 'aktualisieren' oder 'neue anlegen'
    """
    user_answer = state["parameter"].get("user_answer", "")
    rueckfrage = state["parameter"].get("original_rueckfrage", "")
    action = state["parameter"].get("action", "")

    logger.debug(f"resume: Einstieg -- action='{action}', user_answer='{user_answer[:80]}', "
                 f"rueckfrage='{rueckfrage[:80]}'")

    # Versuch: Disambiguierung-JSON parsen
    try:
        disamb = json.loads(rueckfrage)
        if disamb.get("typ") == "disambiguierung":
            return _resume_disambiguierung(state, disamb, user_answer)
        if disamb.get("typ") == "nicht_gefunden":
            return _resume_nicht_gefunden(state, disamb, user_answer)
    except (json.JSONDecodeError, TypeError):
        pass

    # Versuch: Duplikat-Rueckfrage ("aktualisieren oder neue anlegen?")
    if "aktualisier" in rueckfrage.lower() or "bereits eine" in rueckfrage.lower():
        return _resume_duplikat(state, user_answer)

    # Fallback: Konnte Rueckfrage-Typ nicht erkennen
    logger.warning(f"resume: Unbekannter Rueckfrage-Typ -- rueckfrage='{rueckfrage[:100]}'")
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

    # Einfache Zuordnung: Pruefe ob die User-Antwort einen Kandidaten-Namen enthaelt
    user_lower = user_answer.lower()
    match = None
    for k in kandidaten:
        if k["name"].lower() in user_lower:
            match = k
            logger.debug(f"_resume_disambiguierung: Match via Name -- '{k['name']}'")
            break

    # Fallback: Pruefe auf ID oder Position ("die erste", "Nummer 2")
    if not match:
        for i, k in enumerate(kandidaten):
            if str(i + 1) in user_answer or str(k.get("id", "")) in user_answer:
                match = k
                logger.debug(f"_resume_disambiguierung: Match via Index/ID -- '{k['name']}'")
                break

    # Fallback: Wenn genau 2 Kandidaten und "erste"/"zweite" im Text
    if not match and len(kandidaten) == 2:
        if any(w in user_lower for w in ["erste", "ersten", "obere", "1"]):
            match = kandidaten[0]
            logger.debug(f"_resume_disambiguierung: Match via 'erste' -- '{match['name']}'")
        elif any(w in user_lower for w in ["zweite", "zweiten", "untere", "2", "andere"]):
            match = kandidaten[1]
            logger.debug(f"_resume_disambiguierung: Match via 'zweite' -- '{match['name']}'")

    if not match:
        # User-Antwort zu ungenau fuer einfaches Matching
        logger.info("_resume_disambiguierung: Kein Match -- erneute Rueckfrage")
        return {
            "status": "rueckfrage",
            "rueckfrage": json.dumps({
                "typ": "disambiguierung",
                "agent": "notizen",
                "aktion": action,
                "kandidaten": kandidaten,
            }, ensure_ascii=False),
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "kein_match"}],
        }

    logger.info(f"_resume_disambiguierung: Kandidat gewaehlt -- id={match.get('id')}, name='{match['name']}'")

    return {
        "parameter": {
            **state["parameter"],
            "action": action,
            "notiz": match,
            "resume": False,  # Resume abgeschlossen
        },
        "status": "laufend",
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": f"gewaehlt: {match['name']}"}],
    }


def _resume_nicht_gefunden(state: AgentState, info: dict, user_answer: str) -> dict:
    """User hat auf 'Notiz existiert nicht, soll ich anlegen?' geantwortet."""
    user_lower = user_answer.lower()
    target = info.get("target", "")
    original_aufgabe = info.get("original_aufgabe", "")
    original_aktion = info.get("aktion", "add_content")

    logger.debug(f"_resume_nicht_gefunden: target='{target}', user_answer='{user_answer}', "
                 f"original_aufgabe='{original_aufgabe[:80]}'")

    if any(w in user_lower for w in ["ja", "klar", "mach", "bitte", "okay", "ok", "gerne",
                                      "sure", "jep", "jop", "auf jeden", "logo", "passt"]):
        logger.info(f"_resume_nicht_gefunden: User bestaetigt -- create '{target}' mit Originaltext")
        return {
            "aufgabe": original_aufgabe,
            "parameter": {
                **state["parameter"],
                "action": "create",
                "resume": False,
            },
            "status": "laufend",
            "schritte": state["schritte"] + [{
                "node": "resume",
                "ergebnis": f"nicht_gefunden_bestaetigt: create '{target}'",
            }],
        }

    if any(w in user_lower for w in ["nein", "ne", "nee", "nicht", "lass", "abbruch", "stopp"]):
        logger.info("_resume_nicht_gefunden: User lehnt ab")
        return {
            "status": "abgeschlossen",
            "ergebnis": f"Okay, '{target}' wird nicht angelegt.",
            "schritte": state["schritte"] + [{
                "node": "resume",
                "ergebnis": "nicht_gefunden_abgelehnt",
            }],
        }

    logger.info("_resume_nicht_gefunden: Antwort unklar -- erneute Rueckfrage")
    return {
        "status": "rueckfrage",
        "rueckfrage": json.dumps({
            "typ": "nicht_gefunden",
            "agent": "notizen",
            "aktion": original_aktion,
            "target": target,
            "original_aufgabe": original_aufgabe,
        }, ensure_ascii=False),
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "unklar"}],
    }


def _resume_duplikat(state: AgentState, user_answer: str) -> dict:
    """User hat auf Duplikat-Rueckfrage geantwortet ('aktualisieren' oder 'neu')."""
    user_lower = user_answer.lower()

    logger.debug(f"_resume_duplikat: user_answer='{user_answer}'")

    if any(w in user_lower for w in ["aktualisier", "update", "überschreib", "ersetze", "ändere"]):
        logger.info("_resume_duplikat: User will aktualisieren")
        return {
            "parameter": {
                **state["parameter"],
                "action": "update",
                "resume": False,
            },
            "status": "laufend",
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "aktualisieren"}],
        }

    if any(w in user_lower for w in ["neu", "neue", "zusätzlich", "extra", "trotzdem", "separate"]):
        logger.info("_resume_duplikat: User will neue Notiz")
        return {
            "parameter": {
                **state["parameter"],
                "action": "create",
                "skip_duplikat_check": True,
                "resume": False,
            },
            "status": "laufend",
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "neu_anlegen"}],
        }

    # Unklar -- erneute Rueckfrage
    logger.info("_resume_duplikat: Antwort unklar -- erneute Rueckfrage")
    name = state["parameter"].get("target", "Notiz")
    return {
        "status": "rueckfrage",
        "rueckfrage": (
            f"Es gibt bereits eine Notiz '{name}'. "
            "Soll ich sie aktualisieren oder eine ganz neue anlegen?"
        ),
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "unklar"}],
    }
