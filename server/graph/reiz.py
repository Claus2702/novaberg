"""Woher der Reiz dieses Durchlaufs stammt — eine Auskunft für beide Stufen.

Ein Pixie-Impuls reist als `user_prompt` durch den Graphen, auf demselben
Platz, an dem sonst die Nutzereingabe steht. Wer diesen Platz liest, ohne nach
der Herkunft zu fragen, hält Novas eigenen Gedanken für eine fremde Aeusserung.

**Warum die Funktion hier steht und nicht im Responder.** Sie stand dort, und
das war richtig, solange der Responder den Inhalt selbst formulierte. Seit der
Trennung von Inhalt und Form schreibt der **Verfasser** den Text — und er hatte
die Pruefung nicht. Gemessen am 13.08.2026: **13 von 14 eigenen Impulsen** eines
Tages begannen mit »Du hast …«, fuenf davon wortgleich, obwohl der Responder
seinen Schutzblock gesetzt hatte. Die Zuschreibung stand schon im Material.

**Die Lehre daraus ist groesser als der eine Fall:** Ein Schutz, den nur die
zweite Stufe kennt, greift ins Leere, sobald die erste den Text schreibt. Was
beide Stufen brauchen, gehoert an einen Ort — sonst laeuft die Kopie irgendwann
auseinander (`novaberg-bugs.md` → `VERFASSER-KENNT-DIE-QUELLE-NICHT`).
"""

import logging

logger = logging.getLogger("ki_server.graph.reiz")


def reiz_ist_eigener_gedanke(state: dict) -> bool:
    """Prueft, ob der Reiz dieses Durchlaufs von Nova selbst stammt.

    Der Marker steht ausdruecklich im Event-Payload; `event_source ==
    "character"` allein genuegt nicht, weil der Thinker-Retry dieselbe Quelle
    traegt und dabei eine echte Nutzer-Aeusserung wiederholt.

    Vorbedingung: keine — ein fehlender Payload heisst „nicht von Nova".
    Nachbedingung: True nur bei ausdruecklich markierter eigener Herkunft.

    Args:
        state: der Zustand des Durchlaufs.

    Returns:
        True, wenn der Reiz Novas eigener Impuls ist.
    """
    # ── Eingabe-Validierung ─────────────────────
    payload: dict = state.get("event_payload") or {}

    # ── Verarbeitung / Ausgabe ──────────────────
    return payload.get("reiz_herkunft") == "eigener_impuls"
