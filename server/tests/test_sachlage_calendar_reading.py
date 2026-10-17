"""Zeugen: Das Angebot der Sachlage liest Termine ueber den Leseweg der Termine.

`graph/nodes/sachlage_resolver.py::_calendar_hits` las die Kalenderzeilen
selbst, ohne Uhr des Turns: *vergangen* grenzte dort niemand ab, und ein
Zeitraum wie *November* wurde als Titel gesucht. Jetzt baut der Aufloeser je
akutem Objekt ein Fenster und liest mit `memory/timeline_reading.py::
read_appointments` — demselben Leseweg wie hinter dem Router.

Zeugen dieser Datei, gefahren ueber `memory_offer` (den Weg ins Angebot):
  * **Zeitraum** — *November* ist ein Fenster `range` vom 01.11. bis 30.11.
    des richtigen Jahres; die Termine darin stehen im Angebot, je mit
    `timeline#<id>`. Zwilling: ein Titel wird gesucht, nicht als Zeitraum.
  * **Abgrenzung** — eine Suche nach Titel mit einem vergangenen, einem
    kommenden und einem Termin von heute ohne Uhrzeit liefert im Angebot
    dieselben Zeilen wie `read_after_route` hinter dem Router; die Abfrage
    bekommt die Uhr des Turns.
  * **Anker** — ein Erinnerungs-Anker wird nie angeboten; ein `termin` am
    selben Tag schon.
  * **Ein Weg** — der Aufloeser nennt das Repository nicht mehr und ruft
    `read_appointments`; ein Lesefehler ist laut, der Turn geht weiter.
  * **Verhaltensgleich** — `time_window` liefert fuer *morgen*, *naechste
    Woche*, *am Wochenende* und *November* die Fenster von vorher, und der
    Timeline-Agent ruft dieselbe Funktion.
  * **Kennung** — `to_appointment` traegt die Kennung der Zeile und verwirft
    eine Zeile ohne ganzzahlige Kennung laut.

Ohne Datenbank, Netz und Modell: Das Repository ist am Ort des Lesewegs durch
ein Doppel ersetzt, die Uhr steht fest. Die Beispiele sind synthetisch. Kein
skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import unittest
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from agents.timeline import suche
from config import SACHLAGE_BESTAND_KALENDER_LIMIT
from graph import appointments
from graph.appointments import KIND_RANGE, KIND_SEARCH, AppointmentReading
from graph.format.appointments import appointment_line
from graph.nodes.route_reading import read_after_route
from graph.nodes.sachlage_resolver import (
    SOURCE_CALENDAR,
    MemoryHit,
    _calendar_window,
    memory_offer,
)
from memory import timeline_reading
from memory.repositories.timeline_repository import TimelineRepository
from memory.timeline_inventory import ANCHOR_TYPE, TIME_PRECISIONS

BERLIN: ZoneInfo = ZoneInfo("Europe/Berlin")

#: Die eingefrorene Uhr: Samstag, 17.10.2026, 12:00 Ortszeit.
NOW: datetime = datetime(2026, 10, 17, 12, 0, tzinfo=BERLIN)
WEDNESDAY: datetime = datetime(2026, 10, 14, 10, 0, tzinfo=BERLIN)

URL: str = "postgresql://attrappe"
SERVER_ROOT: Path = Path(__file__).resolve().parents[1]

_CLOCK: str = "graph.nodes.sachlage_resolver.now_local"
_RESOLVER_LOGGER: str = "ki_server.sachlage.resolver"
_READING_LOGGER: str = "ki_server.memory.timeline_reading"


def _row(  # noqa: PLR0913 — eine Zeile der Tabelle, ein Argument je Feld
    row_id: int, moment: datetime, title: str, *, event_type: str = "termin",
    precision: str = "minute", details: str | None = None,
) -> dict:
    """Eine Timeline-Zeile, wie das Repository sie liefert (Ortszeit, aktiv)."""
    return {
        "id": row_id, "event_time": moment, "title": title, "event_type": event_type,
        "precision": precision, "details": details, "aktiv": True,
    }


#: Der Bestand um den November: je ein Termin davor und danach, zwei darin.
NOVEMBER_STOCK: list[dict] = [
    _row(1, datetime(2026, 10, 31, 23, 30, tzinfo=BERLIN), "Halloween-Feier"),
    _row(3, datetime(2026, 11, 6, 19, 0, tzinfo=BERLIN), "Elternabend"),
    _row(4, datetime(2026, 11, 30, 20, 0, tzinfo=BERLIN), "Abschlussessen"),
    _row(5, datetime(2026, 12, 1, 0, 0, tzinfo=BERLIN), "Adventsmarkt", precision="day"),
]

#: Drei Zahnarzttermine: vergangen, heute ohne Uhrzeit, kommend.
DENTIST_STOCK: list[dict] = [
    _row(11, datetime(2026, 10, 10, 10, 0, tzinfo=BERLIN), "Zahnarzt"),
    _row(12, datetime(2026, 10, 17, 0, 0, tzinfo=BERLIN), "Zahnarzt Abholung", precision="day"),
    _row(13, datetime(2026, 10, 20, 8, 15, tzinfo=BERLIN), "Zahnarzt", details="Kontrolle"),
]


class FakeTimeline:
    """Doppel des Repositorys: filtert wie die Abfrage und schreibt jeden Aufruf mit."""

    def __init__(
        self, rows: list[dict], *, honour_exclusion: bool = True,
        failure: Exception | None = None,
    ) -> None:
        """Der Bestand; ohne `honour_exclusion` kommt ein Anker trotz Ausschluss an."""
        self.rows: list[dict] = rows
        self.honour_exclusion: bool = honour_exclusion
        self.failure: Exception | None = failure
        self.calls: list[dict] = []

    def _excluded(self, row: dict, exclude_event_types: tuple[str, ...]) -> bool:
        """Ob die Abfrage die Zeile ihres Typs wegen ausschliesst."""
        return self.honour_exclusion and row["event_type"] in exclude_event_types

    def find_by_date_range(
        self, postgres_url: str, user_id: str, von: datetime, bis: datetime,
        exclude_event_types: tuple[str, ...] = (),
    ) -> list[dict]:
        """Die Zeilen im Zeitraum, ohne die ausgeschlossenen Typen."""
        self.calls.append(
            {"art": "range", "von": von, "bis": bis, "exclude": exclude_event_types},
        )
        if self.failure is not None:
            raise self.failure
        return [
            dict(r) for r in sorted(self.rows, key=lambda r: r["event_time"])
            if von <= r["event_time"] <= bis and not self._excluded(r, exclude_event_types)
        ]

    def find_by_keyword(  # noqa: PLR0913 — dieselbe Unterschrift wie das Repository
        self, postgres_url: str, user_id: str, keyword: str,
        direction: str = "forward", limit: int = 5, *,
        exclude_event_types: tuple[str, ...] = (),
        now: datetime | None = None, timed_precisions: frozenset[str] = frozenset(),
    ) -> list[dict]:
        """Die Zeilen, deren Titel den Suchbegriff traegt; `LIMIT` schneidet danach."""
        self.calls.append({
            "art": "keyword", "keyword": keyword, "direction": direction, "limit": limit,
            "exclude": exclude_event_types, "now": now, "timed": timed_precisions,
        })
        if self.failure is not None:
            raise self.failure
        hits: list[dict] = [
            dict(r) for r in sorted(self.rows, key=lambda r: r["event_time"])
            if keyword.lower() in r["title"].lower()
            and not self._excluded(r, exclude_event_types)
        ]
        return hits[:limit]


def _repository(timeline: FakeTimeline) -> ExitStack:
    """Ersetzt die Lesemethoden an der Klasse des Repositorys, nicht an einem Namen.

    Damit erreicht auch ein Aufrufer, der das Repository selbst importiert,
    nur das Doppel — ein Eingriff, der den direkten Aufruf zurueckholt, oeffnet
    keine Verbindung.
    """
    stack = ExitStack()
    stack.enter_context(
        patch.object(TimelineRepository, "find_by_keyword", timeline.find_by_keyword),
    )
    stack.enter_context(
        patch.object(TimelineRepository, "find_by_date_range", timeline.find_by_date_range),
    )
    return stack


def _offer(names: list[str], timeline: FakeTimeline, entries: list | None = None) -> list:
    """Das Angebot eines Turns, dessen vorige Blase `names` als akute Objekte traegt."""
    previous: dict = {"objekte": [{"name": n, "akut": True} for n in names]}
    state: dict = {"user_id": "pruefer", "memory_entries": entries or []}
    with _repository(timeline), patch(_CLOCK, return_value=NOW):
        return memory_offer(state, previous)


def _calendar(hits: list[MemoryHit]) -> list[MemoryHit]:
    """Nur die Kalenderzeilen des Angebots."""
    return [h for h in hits if h.source == SOURCE_CALENDAR]


def _offer_text(line: str) -> str:
    """Die Zeile des Termin-Blocks, so wie das Angebot sie traegt."""
    return f"Kalender {line.removeprefix('- ')}"


class PeriodTest(unittest.TestCase):
    """Ein Zeitraum wie *November* liest den ganzen Zeitraum."""

    def test_november_is_the_whole_month_of_this_year(self) -> None:
        window = _calendar_window("November", NOW)

        self.assertEqual(window.kind, KIND_RANGE)
        self.assertEqual(
            (window.start, window.end),
            (datetime(2026, 11, 1, 0, 0, tzinfo=BERLIN),
             datetime(2026, 11, 30, 23, 59, 59, tzinfo=BERLIN)),
        )

    def test_the_appointments_in_november_are_offered_with_their_origin(self) -> None:
        timeline = FakeTimeline(NOVEMBER_STOCK)
        hits: list[MemoryHit] = _calendar(_offer(["November"], timeline))

        self.assertEqual([h.origin for h in hits], ["timeline#3", "timeline#4"])
        self.assertEqual(
            [h.content for h in hits],
            ["Kalender Freitag, 06.11.2026, 19:00 Uhr — Elternabend (in 20 Tagen)",
             "Kalender Montag, 30.11.2026, 20:00 Uhr — Abschlussessen (in 44 Tagen)"],
        )
        self.assertEqual([c["art"] for c in timeline.calls], ["range"])

    def test_twin_a_title_is_searched_not_read_as_a_period(self) -> None:
        window = _calendar_window("Elternabend", NOW)

        self.assertEqual(window.kind, KIND_SEARCH)
        self.assertEqual(window.keyword, "Elternabend")


class PastBoundaryTest(unittest.TestCase):
    """Im Angebot steht *vergangen* so wie im Block `[TERMINE]` hinter dem Router."""

    def test_a_title_search_gives_the_same_lines_as_behind_the_router(self) -> None:
        timeline = FakeTimeline(DENTIST_STOCK)
        hits: list[MemoryHit] = _calendar(_offer(["Zahnarzt"], timeline))
        query: dict = {
            "type": "search", "keyword": "Zahnarzt", "limit": SACHLAGE_BESTAND_KALENDER_LIMIT,
        }
        with _repository(FakeTimeline(DENTIST_STOCK)):
            routed: dict = read_after_route(
                {"user_id": "pruefer", "needs_timeline": True, "timeline_query": query},
                URL, NOW,
            )
        reading: AppointmentReading = routed["appointment_reading"]
        expected: list[str] = [_offer_text(appointment_line(a, NOW)) for a in reading.appointments]

        self.assertEqual([h.content for h in hits], expected)
        self.assertEqual(
            expected,
            ["Kalender Samstag, 10.10.2026, 10:00 Uhr — Zahnarzt (vergangen, vor 7 Tagen)",
             "Kalender Samstag, 17.10.2026, ohne Uhrzeit — Zahnarzt Abholung (heute)",
             "Kalender Dienstag, 20.10.2026, 08:15 Uhr — Zahnarzt — Kontrolle (in 3 Tagen)"],
        )

    def test_the_query_gets_the_clock_of_the_turn(self) -> None:
        timeline = FakeTimeline(DENTIST_STOCK)
        _offer(["Zahnarzt"], timeline)

        call: dict = timeline.calls[0]
        self.assertEqual(call["now"], NOW)
        self.assertEqual(call["timed"], TIME_PRECISIONS)
        self.assertEqual(call["direction"], "both")


class AnchorTest(unittest.TestCase):
    """Ein Erinnerungs-Anker ist kein Termin — auch nicht im Angebot."""

    _SAME_DAY: datetime = datetime(2026, 10, 19, 9, 0, tzinfo=BERLIN)

    def _stock(self) -> list[dict]:
        """Ein Anker und ein Termin am selben Tag, beide mit dem Suchbegriff."""
        return [
            _row(21, self._SAME_DAY, "Erinnerungs-Anker 19.10.2026 Probe",
                 event_type=ANCHOR_TYPE),
            _row(22, self._SAME_DAY, "Probe mit Ilva"),
        ]

    def test_an_anchor_is_never_offered(self) -> None:
        for honour in (True, False):
            with self.subTest(ausschluss_in_der_abfrage=honour):
                timeline = FakeTimeline(self._stock(), honour_exclusion=honour)
                with self.assertNoLogs(_RESOLVER_LOGGER, level="ERROR"):
                    hits: list[MemoryHit] = _calendar(_offer(["Probe"], timeline))
                self.assertNotIn("timeline#21", [h.origin for h in hits])
                self.assertIn(ANCHOR_TYPE, timeline.calls[0]["exclude"])

    def test_twin_an_appointment_on_the_same_day_is_offered(self) -> None:
        hits: list[MemoryHit] = _calendar(_offer(["Probe"], FakeTimeline(self._stock())))

        self.assertEqual([h.origin for h in hits], ["timeline#22"])
        self.assertEqual(
            hits[0].content, "Kalender Montag, 19.10.2026, 09:00 Uhr — Probe mit Ilva (in 2 Tagen)",
        )


def _named(path: Path) -> tuple[set[str], set[str]]:
    """Die Namen und Attribute, die ein Modul nennt, und die Module, aus denen es importiert."""
    tree: ast.Module = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.alias):
            names.add(node.name.rsplit(".", 1)[-1])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return names, modules


class OneReadingPathTest(unittest.TestCase):
    """Der Aufloeser liest nicht selbst, sondern ueber `read_appointments`."""

    _REPOSITORY_NAMES: frozenset[str] = frozenset(
        {"TimelineRepository", "find_by_keyword", "find_by_date_range"},
    )

    def test_the_resolver_names_no_repository(self) -> None:
        names, modules = _named(SERVER_ROOT / "graph" / "nodes" / "sachlage_resolver.py")

        self.assertEqual(names & self._REPOSITORY_NAMES, set())
        self.assertNotIn("memory.repositories.timeline_repository", modules)
        self.assertIn("read_appointments", names)

    def test_twin_the_reading_path_names_it(self) -> None:
        """Der Zwilling: Die Suche nach den Namen findet sie, wo sie stehen."""
        names, modules = _named(SERVER_ROOT / "memory" / "timeline_reading.py")

        self.assertEqual(names & self._REPOSITORY_NAMES, set(self._REPOSITORY_NAMES))
        self.assertIn("memory.repositories.timeline_repository", modules)

    def test_the_offer_reads_through_read_appointments(self) -> None:
        with patch(
            "graph.nodes.sachlage_resolver.read_appointments",
            wraps=timeline_reading.read_appointments,
        ) as shared:
            _offer(["Zahnarzt", "November"], FakeTimeline(DENTIST_STOCK + NOVEMBER_STOCK))

        self.assertEqual(
            [c.args[0].kind for c in shared.call_args_list], [KIND_SEARCH, KIND_RANGE],
        )
        self.assertEqual({c.args[3] for c in shared.call_args_list}, {NOW})

    def test_a_read_failure_is_loud_and_the_turn_goes_on(self) -> None:
        timeline = FakeTimeline(DENTIST_STOCK, failure=ConnectionError("Verbindung weg"))
        with self.assertLogs(_RESOLVER_LOGGER, level="ERROR") as log:
            hits: list[MemoryHit] = _offer(
                ["Zahnarzt"], timeline,
                [{"quelle": "lzg", "inhalt": "Pool", "gewicht": 0.5, "meta": {}}],
            )

        self.assertEqual([h.content for h in hits], ["Pool"])
        self.assertIn("Kalender zu 'Zahnarzt' nicht gelesen", "\n".join(log.output))
        self.assertIn("ConnectionError", "\n".join(log.output))


class SameWindowTest(unittest.TestCase):
    """`time_window` liefert die Fenster von vorher — gerechnet von Hand."""

    def _assert_window(self, text: str, now: datetime, first: tuple, last: tuple) -> None:
        window = appointments.time_window(text, now)
        self.assertEqual(window.kind, KIND_RANGE, text)
        self.assertEqual(
            (window.start, window.end),
            (datetime(*first, 0, 0, tzinfo=BERLIN), datetime(*last, 23, 59, 59, tzinfo=BERLIN)),
            text,
        )

    def test_tomorrow(self) -> None:
        self._assert_window("morgen", WEDNESDAY, (2026, 10, 15), (2026, 10, 15))

    def test_next_week(self) -> None:
        self._assert_window("nächste Woche", NOW, (2026, 10, 19), (2026, 10, 25))

    def test_weekend(self) -> None:
        self._assert_window("am Wochenende", WEDNESDAY, (2026, 10, 17), (2026, 10, 18))

    def test_november(self) -> None:
        self._assert_window("November", NOW, (2026, 11, 1), (2026, 11, 30))

    def test_the_timeline_agent_calls_the_same_function(self) -> None:
        self.assertIs(suche.time_window, appointments.time_window)


class RowIdTest(unittest.TestCase):
    """Ein Termin traegt die Kennung seiner Zeile; ohne sie wird er verworfen."""

    def test_a_row_without_an_integer_id_is_dropped_loudly(self) -> None:
        for row_id in (None, "13", True):
            with self.subTest(row_id=row_id):
                row: dict = {**DENTIST_STOCK[2], "id": row_id}
                with self.assertLogs(_READING_LOGGER, level="ERROR") as log:
                    self.assertIsNone(timeline_reading.to_appointment(row, NOW))
                self.assertIn("ohne ganzzahlige id", "\n".join(log.output))

    def test_twin_the_appointment_carries_the_row_id(self) -> None:
        appointment = timeline_reading.to_appointment(dict(DENTIST_STOCK[2]), NOW)

        self.assertEqual(appointment.timeline_id, 13)


if __name__ == "__main__":
    unittest.main()
