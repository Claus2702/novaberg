"""Zeugen fuer den Kalender im Angebot der Sachlage: ein Anker ist kein Termin.

`graph/nodes/sachlage_resolver.py::_calendar_hits` legt Zeilen »Kalender
TT.MM.JJJJ: Titel« ins Angebot des Aufloesers. Ein Erinnerungs-Anker darf
dort nicht stehen — dieselbe Regel wie im Leseweg der Termine.

Zeugen dieser Datei, gefahren ueber `memory_offer` (den Weg ins Angebot):
  * **Der Ausschluss steht in der Abfrage, vor dem LIMIT.** Die Attrappe
    bildet die Abfrage nach: Sie schliesst aus, was `exclude_event_types`
    nennt, und kappt danach. Fuellen Anker die ersten Plaetze, kommt der
    Termin dahinter trotzdem an.
  * **Ein Anker, der trotzdem ankommt, faellt laut heraus** — die Attrappe
    ignoriert hier den Ausschluss.
  * **Der Zwilling:** eine Zeile vom Typ `termin` ergibt eine Kalenderzeile,
    mit Datum, Titel und Details.
  * Die Beispiele sind synthetisch.

Keine Datenbank: `TimelineRepository.find_by_keyword` ist ersetzt.
Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from collections.abc import Callable
from datetime import datetime, timezone
from unittest.mock import patch

from config import SACHLAGE_BESTAND_KALENDER_LIMIT
from graph.nodes.sachlage_resolver import SOURCE_CALENDAR, MemoryHit, memory_offer
from memory.timeline_inventory import ANCHOR_TYPE

_FIND: str = "graph.nodes.sachlage_resolver.TimelineRepository.find_by_keyword"

_PREVIOUS: dict = {"objekte": [{"name": "Beispieltermin", "akut": True}]}
_STATE: dict = {"user_id": "u", "memory_entries": []}


def _row(row_id: int, event_type: str) -> dict:
    """Eine Timeline-Zeile, wie `SELECT *` sie liefert, mit Titel »Beispieltermin«."""
    return {
        "id": row_id, "title": "Beispieltermin", "details": "Muster",
        "event_time": datetime(2030, 1, 2, 9, 0, tzinfo=timezone.utc),
        "event_type": event_type,
    }


def _query_like(rows: list[dict]) -> Callable[..., list[dict]]:
    """Eine Attrappe der Abfrage: erst der Ausschluss, dann das LIMIT.

    Die Stellung der Argumente ist die von `find_by_keyword`: postgres_url,
    user_id, keyword, direction, limit.
    """
    def fake(*args: object, exclude_event_types: tuple[str, ...] = (), **_: object) -> list[dict]:
        limit: int = int(args[4])
        return [r for r in rows if r["event_type"] not in exclude_event_types][:limit]
    return fake


def _calendar(hits: list[MemoryHit]) -> list[MemoryHit]:
    """Nur die Kalenderzeilen des Angebots."""
    return [h for h in hits if h.source == SOURCE_CALENDAR]


class AnchorIsNoAppointmentTest(unittest.TestCase):
    """Kein Anker im Angebot; ein Termin steht darin."""

    def test_anchors_before_the_limit_do_not_take_the_places(self) -> None:
        rows: list[dict] = [
            _row(i, ANCHOR_TYPE) for i in range(1, SACHLAGE_BESTAND_KALENDER_LIMIT + 1)
        ]
        rows.append(_row(99, "termin"))
        with patch(_FIND, side_effect=_query_like(rows)) as find:
            hits: list[MemoryHit] = _calendar(memory_offer(_STATE, _PREVIOUS))
        self.assertIn(ANCHOR_TYPE, find.call_args.kwargs.get("exclude_event_types", ()))
        self.assertEqual([h.origin for h in hits], ["timeline#99"])

    def test_an_anchor_arriving_anyway_is_dropped_loudly(self) -> None:
        rows: list[dict] = [_row(1, ANCHOR_TYPE), _row(2, "termin")]
        with patch(_FIND, return_value=rows), \
             self.assertLogs("ki_server.sachlage.resolver", level="ERROR") as log:
            hits: list[MemoryHit] = _calendar(memory_offer(_STATE, _PREVIOUS))
        self.assertEqual([h.origin for h in hits], ["timeline#2"])
        self.assertIn("Erinnerungs-Anker id=1", "\n".join(log.output))

    def test_twin_an_appointment_gives_a_calendar_line(self) -> None:
        with patch(_FIND, side_effect=_query_like([_row(7, "termin")])):
            hits: list[MemoryHit] = _calendar(memory_offer(_STATE, _PREVIOUS))
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].origin, "timeline#7")
        self.assertEqual(hits[0].content, "Kalender 02.01.2030: Beispieltermin — Muster")


if __name__ == "__main__":
    unittest.main()
