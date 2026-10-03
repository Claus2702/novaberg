"""
Turn-Verteilung — welche Panels einen Turn oder einen Impuls Novas bekommen.

Das Modul importiert kein GTK, damit die Verteilung ohne Fenster prüfbar ist.
Die Panels kommen als Objekte mit ``PANEL_ID``, ``CATEGORY``,
``REACTS_TO_IMPULSE`` und ``on_turn_received``.
"""

import logging
from collections.abc import Iterable, Mapping


logger = logging.getLogger(__name__)

IMPULSE_ORIGIN = "eigener_impuls"


def impulse_turn_data(text: str, data: Mapping) -> dict | None:
    """Macht aus einem Impuls Novas die Turn-Daten, die ein Panel von einer Antwort kennt.

    Vorbedingung: ``text`` ist der Text des Impulses, ``data`` die Nutzlast des Ereignisses.
    Nachbedingung: ``None``, wenn die Nutzlast kein Impuls Novas ist (etwa die
    Nachricht eines anderen Clients); sonst ein Dict mit allen Feldern der Nutzlast
    und dem Text unter ``antwort`` — der Text steht dort, wo eine Antwort ihn trägt.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(text, str):
        raise TypeError(f"impulse_turn_data: text ist {type(text).__name__}, kein str")
    if not isinstance(data, Mapping):
        raise TypeError(f"impulse_turn_data: data ist {type(data).__name__}, kein Mapping")

    # ── Verarbeitung ──
    if data.get("typ") == "user_message" or data.get("reiz_herkunft") != IMPULSE_ORIGIN:
        return None
    turn_data = {**data, "antwort": text}

    # ── Ausgabe-Verifikation ──
    if turn_data["antwort"] is not text:
        raise RuntimeError("impulse_turn_data: antwort trägt nicht den Text des Impulses")
    return turn_data


def deliver_turn(panels: Iterable, turn_data: dict, *, impulse: bool) -> int:
    """Gibt Turn-Daten an die turn_reactive-Panels weiter, einen Impuls nur an die, die ihn wollen.

    Vorbedingung: ``turn_data`` ist ein Dict; ``impulse`` sagt, ob es ein Impuls Novas ist.
    Nachbedingung: Rückgabe ist die Zahl der Panels, deren ``on_turn_received`` gelaufen ist.
    Fehlerfall: Ein Panel, dessen ``on_turn_received`` scheitert, wird als Fehler
    protokolliert und zählt nicht; die übrigen bekommen den Turn trotzdem.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(turn_data, dict):
        raise TypeError(f"deliver_turn: turn_data ist {type(turn_data).__name__}, kein dict")

    # ── Verarbeitung ──
    delivered = 0
    for panel in panels:
        if panel.CATEGORY != "turn_reactive":
            continue
        if impulse and not panel.REACTS_TO_IMPULSE:
            continue
        try:
            panel.on_turn_received(turn_data)
            delivered += 1
        except Exception as error:
            logger.error(f"Panel '{panel.PANEL_ID}': on_turn_received fehlgeschlagen: {error}")

    # ── Ausgabe-Verifikation ──
    if delivered:
        logger.debug(f"{'Impuls' if impulse else 'Turn'} an {delivered} Panel(s) verteilt")
    return delivered
