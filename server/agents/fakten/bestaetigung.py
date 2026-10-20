"""Bestätigungs-Knoten — schließt den Lauf ab, ohne einen Erfolg zu erfinden.

Anders als im Muster der Timeline hebt dieser Knoten `laufend` **nicht** auf
`abgeschlossen`: `abgeschlossen` setzt allein die Ausführung, und nur nach
ihrer Verifikation (`crud.execute`). Kommt ein anderer Status hier an,
ist der Graph an der Verifikation vorbeigelaufen — das wird `fehler`.
"""

import logging

from agents.base import AgentState

logger = logging.getLogger("ki_server.agents.fakten.bestaetigung")

# Was die Ausführung oder die Suche als Endstatus setzen darf.
ENDSTATUS: frozenset[str] = frozenset({"abgeschlossen", "rueckfrage", "fehler"})


def confirm(state: AgentState) -> dict:
    """Lässt einen gesetzten Endstatus stehen und macht aus jedem anderen `fehler`.

    Vorbedingung: `state` trägt `status` und `schritte`.
    Nachbedingung: Der Status liegt in ENDSTATUS; ein `abgeschlossen` stammt
        aus der Ausführung, nie aus diesem Knoten.
    Fehlerfälle: Ein Status außerhalb von ENDSTATUS ergibt `fehler` mit dem
        vorgefundenen Status als Beleg und wird laut protokolliert.
    """
    # ── Eingabe-Validierung ─────────────────────
    status: str = state.get("status", "")
    schritte: list[dict] = state["schritte"]

    # ── Verarbeitung ────────────────────────────
    if status in ENDSTATUS:
        aenderung: dict = {"schritte": schritte + [{"node": "bestaetigen", "ergebnis": status}]}
    else:
        logger.error("bestaetigen: Status %r ohne Verifikation — fehler statt Erfolg", status)
        aenderung = {
            "status": "fehler",
            "fehler": f"Lauf endete ohne verifizierten Ausgang (Status {status!r})",
            "schritte": schritte + [{"node": "bestaetigen", "ergebnis": f"ohne_ausgang/{status}"}],
        }

    # ── Ausgabe-Verifikation ────────────────────
    if aenderung.get("status", status) not in ENDSTATUS:
        raise RuntimeError(f"bestaetigen: Endstatus {aenderung.get('status')!r} nicht erlaubt")
    return aenderung
