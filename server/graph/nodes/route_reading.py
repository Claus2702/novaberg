"""Leseschritt hinter dem Router: die Termine des Turns in den Zustand.

Gerufen im Router-Knoten (`graph/base.py::_node_route`), weil erst der Router
`needs_timeline` und `timeline_query` setzt. Kein eigener Knoten im Graphen.

Hier steht der Ablauf: das Fenster aus der Anfrage des Routers, das Lesen
ueber `memory/timeline_reading.py` und die Kompensation eines Lesefehlers.
Das Gedaechtnis liest nur ein Fenster; den Zustand des Graphen kennt es nicht.

**Ein Lesefehler ist kein leerer Zeitraum.** Er ergibt ein Ergebnis mit
`failed`, und der Block sagt, dass nichts bekannt ist.
"""

from __future__ import annotations

import logging
from datetime import datetime

from graph.appointments import AppointmentReading, AppointmentWindow, appointment_window
from graph.state import ConversationState
from memory.timeline_reading import read_appointments

logger = logging.getLogger("ki_server.graph.route_reading")


def read_after_route(
    state: ConversationState, postgres_url: str, now: datetime,
) -> ConversationState:
    """Setzt das Leseergebnis der Termine dieses Turns in den Zustand nach dem Router.

    Hier wird gefangen, weil hier kompensiert wird: Ein Lesefehler wird zum
    Ergebnis mit `failed`, und der Block sagt, dass ueber die Termine nichts
    bekannt ist — statt den Turn abzubrechen oder *keine Termine* zu sagen.

    Vorbedingung: `state` ist der Zustand nach dem Router; `now`
        zeitzonenbewusst in Ortszeit.
    Nachbedingung: derselbe Zustand, mit `appointment_reading` — nie `None`.
    Fehlerfaelle: ein Zustand, der kein dict ist, wirft `TypeError`; ein naiver
        Zeitpunkt wirft `ValueError` (Programmierfehler). Jeder Fehler beim
        Lesen wird mit Stacktrace gemeldet und ergibt `failed=True`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(state, dict):
        msg: str = f"read_after_route: Zustand ist kein dict ({type(state).__name__})"
        raise TypeError(msg)
    window: AppointmentWindow = appointment_window(state, now)
    user_id: str = str(state.get("user_id") or "")

    # ── Verarbeitung ────────────────────────────
    try:
        reading: AppointmentReading = read_appointments(window, user_id, postgres_url, now)
    except Exception:
        logger.exception(
            f"Termine: Timeline nicht gelesen (art={window.kind}) — der Block sagt, "
            f"dass ueber die Termine nichts bekannt ist"
        )
        reading = AppointmentReading(window=window, now=now, failed=True)
    state["appointment_reading"] = reading

    # ── Ausgabe-Verifikation ────────────────────
    if reading.window is not window:
        msg = "read_after_route: Leseergebnis zu einem anderen Fenster"
        raise RuntimeError(msg)
    return state
