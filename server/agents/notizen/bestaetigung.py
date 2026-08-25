"""Bestaetigungs-Node -- Bereinigt den State fuer die Rueckgabe.

Setzt status='abgeschlossen' falls kein Fehler oder Rueckfrage vorliegt.
Ueberschreibt NICHT wenn _create/_update/_delete bereits rueckfrage/fehler gesetzt hat.
"""

import logging

from agents.base import AgentState

logger = logging.getLogger("ki_server.agents.notizen.bestaetigung")


def bestaetigen(state: AgentState) -> dict:
    """Bestaetigt die Operation -- bereinigt den State fuer die Rueckgabe."""
    aktueller_status = state.get("status", "laufend")
    logger.debug(
        f"bestaetigen: Einstieg -- status='{aktueller_status}', "
        f"ergebnis='{state.get('ergebnis', '?')}'"
    )

    # Nicht ueberschreiben wenn _create/_update/_delete bereits rueckfrage/fehler gesetzt hat
    if aktueller_status in ("rueckfrage", "fehler"):
        logger.debug(f"bestaetigen: Status bleibt '{aktueller_status}'")
        return {
            "schritte": state["schritte"] + [{"node": "bestaetigen", "ergebnis": aktueller_status}]
        }

    logger.debug("bestaetigen: status -> 'abgeschlossen'")
    return {
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "bestaetigen", "ergebnis": "ok"}],
    }
