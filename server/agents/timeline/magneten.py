"""Magneten-Helper — leitet Themen-Liste und Verhaltens-Flags aus event_type ab.

M2.5a-Variante: themen_aus_event_type liefert ARRAY[event_type]; reichere
thematische Anreicherung (z.B. aus Entitaeten-Map) folgt in M3.

Mapping nach Magneten-Convention §5.
"""

import logging

logger = logging.getLogger("ki_server.agents.timeline.magneten")

EVENT_TYPES_TERMIN       = frozenset({"termin", "deadline"})
EVENT_TYPES_WIEDERVORLAGE = frozenset({"geburtstag", "jahrestag", "erinnerung"})


def themen_aus_event_type(event_type: str) -> list[str]:
    """Liefert die initiale Themen-Liste fuer einen Timeline-Eintrag.

    M2.5a-Variante: ARRAY[event_type]. Reichere thematische Anreicherung
    (z.B. aus Entitaeten-Map) folgt in M3.
    """
    themen: list[str] = [event_type]
    logger.debug(f"themen_aus_event_type: event_type='{event_type}' -> {themen}")
    return themen


def verhaltens_flags_aus_event_type(event_type: str) -> tuple[bool, bool, bool]:
    """Mapping event_type -> (binding, remind, conflict_check).

    Mapping nach Magneten-Convention §5:
      - termin, deadline                       -> (True,  True,  True)
      - geburtstag, jahrestag, erinnerung      -> (False, True,  False)
      - alle anderen                           -> (False, False, False)  (sicherer Default)
    """
    if event_type in EVENT_TYPES_TERMIN:
        flags = (True, True, True)
    elif event_type in EVENT_TYPES_WIEDERVORLAGE:
        flags = (False, True, False)
    else:
        logger.warning(
            f"verhaltens_flags_aus_event_type: unbekannter event_type='{event_type}' "
            f"-> Default-Mapping (False, False, False)"
        )
        flags = (False, False, False)

    logger.debug(
        f"verhaltens_flags_aus_event_type: event_type='{event_type}' -> "
        f"binding={flags[0]}, remind={flags[1]}, conflict_check={flags[2]}"
    )
    return flags
