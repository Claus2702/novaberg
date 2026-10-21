"""Magneten-Helper — leitet Themen-Liste und Verhaltens-Flags aus event_type ab.

M2.5a-Variante: themen_aus_event_type liefert ARRAY[event_type]; reichere
thematische Anreicherung (z.B. aus Entitaeten-Map) folgt in M3.

Mapping nach Magneten-Convention §5. Die Merkmale je Typ stehen in der
Typquelle (`memory/timeline_types.py::EVENT_TYPES`); hier werden sie nur
gelesen.
"""

import logging

from memory.timeline_types import ANCHOR_TYPE, EventType, event_type

logger = logging.getLogger("ki_server.agents.timeline.magneten")

# Der Anker-Typ hat eine Quelle; ein zweites Literal liefe auseinander.
EVENT_TYPES_ERINNERUNGS_ANKER = frozenset({ANCHOR_TYPE})


def themen_aus_event_type(event_type: str) -> list[str]:
    """Liefert die initiale Themen-Liste fuer einen Timeline-Eintrag.

    M2.5a-Variante: ARRAY[event_type]. Reichere thematische Anreicherung
    (z.B. aus Entitaeten-Map) folgt in M3.

    Sonderfall erinnerungs_anker (Klasse Bezug, Synapsen P3): leere Liste,
    weil der Anker keine inhaltliche Thematik traegt — er ist eine
    Klassen-Markierung fuer KZG-Magnete, kein semantischer Tag.
    """
    if event_type in EVENT_TYPES_ERINNERUNGS_ANKER:
        logger.debug(f"themen_aus_event_type: event_type='{event_type}' -> [] (Klasse Bezug)")
        return []
    themen: list[str] = [event_type]
    logger.debug(f"themen_aus_event_type: event_type='{event_type}' -> {themen}")
    return themen


def verhaltens_flags_aus_event_type(name: str) -> tuple[bool, bool, bool]:
    """Die Merkmale (binding, remind, conflict_check) eines Typs aus der Typquelle.

    Bis zum Umzug in die Typquelle stand das Mapping hier als eigene Listen,
    und ein unbekannter Typ bekam still (False, False, False).

    Vorbedingung: `name` ist ein Typ aus `EVENT_TYPES`.
    Nachbedingung: das Tripel der drei Merkmale dieses Typs.
    Fehlerfaelle: ein unbekannter Typ wirft `ValueError` (laut protokolliert
        in `event_type`) — ein Eintrag mit Merkmalen, die niemand fuer ihn
        entschieden hat, entsteht nicht.
    """
    # ── Eingabe-Validierung ─────────────────────
    kind: EventType = event_type(name)

    # ── Verarbeitung ────────────────────────────
    flags: tuple[bool, bool, bool] = (kind.binding, kind.remind, kind.conflict_check)

    # ── Ausgabe-Verifikation ────────────────────
    if not all(isinstance(flag, bool) for flag in flags):
        msg: str = (
            f"verhaltens_flags_aus_event_type: Merkmale von '{name}' sind keine bool: {flags}"
        )
        raise TypeError(msg)
    logger.debug(
        f"verhaltens_flags_aus_event_type: event_type='{name}' -> "
        f"binding={flags[0]}, remind={flags[1]}, conflict_check={flags[2]}"
    )
    return flags
