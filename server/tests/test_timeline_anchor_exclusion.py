"""Zeugen: Kein Leseweg gibt einen Erinnerungs-Anker als Termin aus.

Ein `erinnerungs_anker` ist ein Merkposten des Gedaechtnisses mit einem
Datum, kein Termin des Menschen. Das proaktive Fenster las ohne Typfilter, und
eine Frage nach Terminen bekam den Anker, den sie selbst angelegt hatte, als
einzigen "Termin".

Zeugen dieser Datei, je Leseweg:
  * **Repository** — der Ausschluss steht in der Abfrage und vor `LIMIT`.
    Geprueft am SQL, das die Verbindung zu sehen bekommt: Ein Zeuge, der
    den Cursor ersetzt und nur die Rueckgabe prueft, saehe die Abfrage nicht.
    Aus demselben Grund steht dort die Grenze *vergangen* einer Suche.
  * **Timeline-Agent** (`agents/timeline/suche.py`) — eine Leseabfrage
    schliesst den Anker aus, Aendern und Loeschen sehen den ganzen Bestand.
  * **TimelineManager** — das proaktive Fenster fuer die Analyse-Leser.
  * **Gedaechtnis des Verfassers** — die Termin-Zeilen stehen dort nicht
    mehr; der Verfasser liest sie im `[TERMINE]`-Block.
  * Die Beispiele sind synthetisch.

Ohne Datenbank, ohne Netz. Kein skipUnless, kein skipIf, kein try/except um
Importe.
"""

import unittest
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from agents.timeline import suche
from graph.format.memory_context import LESER_ANALYSE, LESER_VERFASSER, format_memory_entries
from memory.repositories.timeline_repository import (
    TimelineRepository,
    _excluded_types,
    _past_bounds,
)
from plugins.timeline_manager.manager import TimelineManager

BERLIN: ZoneInfo = ZoneInfo("Europe/Berlin")
NOW: datetime = datetime(2026, 10, 15, 18, 0, tzinfo=BERLIN)
URL: str = "postgresql://attrappe"
ANCHOR: tuple[str, ...] = ("erinnerungs_anker",)


class _RecordingCursor:
    """Ein Cursor, der jede Abfrage mit ihren Parametern mitschreibt."""

    def __init__(self, log: list[tuple[str, tuple]]) -> None:
        self.log: list[tuple[str, tuple]] = log

    def execute(self, sql: str, params: tuple) -> None:
        self.log.append((sql, params))

    def fetchall(self) -> list:
        return []


class _RecordingConnection:
    """Eine Verbindung, die nichts verbindet und ihre Cursor mitschreiben laesst."""

    def __init__(self) -> None:
        self.log: list[tuple[str, tuple]] = []

    def cursor(self, cursor_factory: object = None) -> _RecordingCursor:
        return _RecordingCursor(self.log)

    def close(self) -> None:
        """Nichts zu schliessen."""


def _queries(call: str, **kwargs: object) -> list[tuple[str, tuple]]:
    """Ruft eine Lesemethode des Repositorys und liefert die gesendeten Abfragen."""
    connection = _RecordingConnection()
    with patch("memory.repositories.timeline_repository.psycopg2.connect", return_value=connection):
        getattr(TimelineRepository, call)(**kwargs)
    return connection.log


class RepositoryExcludesInTheQueryTest(unittest.TestCase):
    """Der Typausschluss steht in der Abfrage, vor `LIMIT`."""

    def test_date_range_sends_the_excluded_types(self) -> None:
        (sql, params), = _queries(
            "find_by_date_range", postgres_url=URL, user_id="u", von=NOW, bis=NOW,
            exclude_event_types=ANCHOR,
        )

        self.assertIn("COALESCE(event_type, '') <> ALL(%s::text[])", sql)
        self.assertEqual(params[3], ["erinnerungs_anker"])

    def test_twin_date_range_without_exclusion_sends_an_empty_list(self) -> None:
        """Der Vorgabewert laesst alles durch — die Aufrufer ausserhalb bleiben unberuehrt."""
        (_sql, params), = _queries(
            "find_by_date_range", postgres_url=URL, user_id="u", von=NOW, bis=NOW,
        )

        self.assertEqual(params[3], [])

    def test_keyword_excludes_before_the_limit_in_every_direction(self) -> None:
        for direction in ("forward", "backward", "both"):
            with self.subTest(direction=direction):
                (sql, params), = _queries(
                    "find_by_keyword", postgres_url=URL, user_id="u", keyword="Zahnarzt",
                    direction=direction, limit=3, exclude_event_types=ANCHOR,
                )

                self.assertLess(sql.index("<> ALL(%s::text[])"), sql.index("LIMIT"))
                self.assertEqual(params[2], ["erinnerungs_anker"])
                self.assertEqual(params[3], 3)

    def test_twin_keyword_without_exclusion_sends_an_empty_list(self) -> None:
        (_sql, params), = _queries(
            "find_by_keyword", postgres_url=URL, user_id="u", keyword="Zahnarzt",
        )

        self.assertEqual(params[2], [])

    def test_a_list_instead_of_a_tuple_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            _excluded_types(["erinnerungs_anker"])

    def test_an_empty_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            _excluded_types(("",))


class KeywordPastBoundaryInTheQueryTest(unittest.TestCase):
    """Mit `now` grenzt die Suche *vergangen* in der Abfrage ab wie der Leser, vor `LIMIT`."""

    TIMED: frozenset[str] = frozenset({"minute", "hour"})

    def _keyword(self, direction: str, **kwargs: object) -> tuple[str, tuple]:
        (sql, params), = _queries(
            "find_by_keyword", postgres_url=URL, user_id="u", keyword="Zahnarzt",
            direction=direction, limit=1, exclude_event_types=ANCHOR, **kwargs,
        )
        return sql, params

    def test_backward_and_forward_bound_by_precision_and_day_start(self) -> None:
        day_start_utc: datetime = datetime(2026, 10, 14, 22, 0, tzinfo=UTC)
        for direction, clause in (("backward", "AND (CASE"), ("forward", "AND NOT (CASE")):
            with self.subTest(direction=direction):
                sql, params = self._keyword(direction, now=NOW, timed_precisions=self.TIMED)

                self.assertIn(clause, sql)
                self.assertNotIn("NOW()", sql)
                self.assertLess(sql.index("CASE"), sql.index("LIMIT"))
                self.assertEqual(
                    params,
                    ("u", "%Zahnarzt%", ["hour", "minute"], NOW.astimezone(UTC), day_start_utc,
                     ["erinnerungs_anker"], 1),
                )

    def test_twin_without_now_the_database_clock_stays(self) -> None:
        """Der Zwilling: Thinker, Sachlage und Agent rufen ohne `now` — ihre Abfrage bleibt."""
        for direction in ("forward", "backward"):
            with self.subTest(direction=direction):
                sql, params = self._keyword(direction)

                self.assertIn("NOW()", sql)
                self.assertNotIn("CASE", sql)
                self.assertEqual(len(params), 4)

    def test_both_has_no_boundary_even_with_now(self) -> None:
        sql, _params = self._keyword("both", now=NOW, timed_precisions=self.TIMED)

        self.assertNotIn("CASE", sql)

    def test_a_naive_now_is_rejected_before_connecting(self) -> None:
        with patch("memory.repositories.timeline_repository.psycopg2.connect") as connect, \
                self.assertRaises(ValueError):
            TimelineRepository.find_by_keyword(
                URL, "u", "Zahnarzt", "backward", 1,
                now=datetime(2026, 10, 15, 18, 0), timed_precisions=self.TIMED,
            )
        connect.assert_not_called()

    def test_now_without_timed_precisions_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            _past_bounds(NOW, frozenset())

    def test_twin_past_bounds_with_precisions(self) -> None:
        self.assertEqual(
            _past_bounds(NOW, self.TIMED),
            (["hour", "minute"], datetime(2026, 10, 15, 16, 0, tzinfo=UTC),
             datetime(2026, 10, 14, 22, 0, tzinfo=UTC)),
        )


class AgentSearchExcludesOnReadTest(unittest.TestCase):
    """Der Leseweg des Timeline-Agenten gibt keinen Anker aus."""

    @staticmethod
    def _search(action: str, target: str, method: str) -> MagicMock:
        state: dict = {
            "parameter": {"action": action, "target": target, "zeitausdruck": ""},
            "kontext": {"user_id": "pruefer"}, "aufgabe": "", "schritte": [],
        }
        with patch(
            f"memory.repositories.timeline_repository.TimelineRepository.{method}", return_value=[],
        ) as read:
            suche.suchen(state)
        return read

    def test_read_by_keyword_excludes_the_anchor(self) -> None:
        read = self._search("read", "Zahnarzt", "find_by_keyword")

        self.assertEqual(read.call_args.kwargs["exclude_event_types"], ANCHOR)

    def test_twin_update_by_keyword_sees_the_whole_stock(self) -> None:
        """Aendern und Loeschen sind der Schreibweg — dort bleibt alles sichtbar."""
        read = self._search("update", "Zahnarzt", "find_by_keyword")

        self.assertEqual(read.call_args.kwargs["exclude_event_types"], ())

    def test_read_overview_excludes_the_anchor(self) -> None:
        read = self._search("read", "", "find_by_date_range")

        self.assertEqual(read.call_args.kwargs["exclude_event_types"], ANCHOR)


class _Timeline:
    """Doppel des Repositorys fuer das proaktive Fenster: ein Termin, ein Anker, ein vergangener."""

    def __init__(self) -> None:
        self.excluded: list[tuple[str, ...]] = []

    def find_by_date_range(
        self, postgres_url: str, user_id: str, von: datetime, bis: datetime,
        exclude_event_types: tuple[str, ...] = (),
    ) -> list[dict]:
        self.excluded.append(exclude_event_types)
        rows: list[dict] = [
            {"id": 1, "event_time": datetime(2026, 10, 14, 9, 0, tzinfo=BERLIN),
             "title": "Fahrradwerkstatt", "event_type": "termin", "precision": "minute"},
            {"id": 2, "event_time": datetime(2026, 10, 16, 14, 30, tzinfo=BERLIN),
             "title": "Zahnarzt", "event_type": "termin", "precision": "minute"},
            {"id": 3, "event_time": datetime(2026, 10, 17, 9, 0, tzinfo=BERLIN),
             "title": "Erinnerungs-Anker 17.10.2026 Rufus", "event_type": "erinnerungs_anker",
             "precision": "minute"},
        ]
        return [r for r in rows if r["event_type"] not in exclude_event_types]


class TimelineManagerTest(unittest.TestCase):
    """Das proaktive Fenster der Analyse-Leser: ohne Anker, mit Bezug zu heute."""

    def _entries(self, state: dict) -> tuple[list[dict], _Timeline]:
        timeline = _Timeline()
        with patch("memory.timeline_reading.TimelineRepository", timeline), \
                patch("plugins.timeline_manager.manager.now_local", return_value=NOW):
            entries: list[dict] = TimelineManager().enrich_entries(state, URL)
        return entries, timeline

    def test_entries_carry_relation_and_no_anchor(self) -> None:
        entries, timeline = self._entries({"user_id": "pruefer"})

        self.assertEqual(
            [(e["meta"]["praefix"], e["inhalt"]) for e in entries],
            [
                ("Timeline/vergangen",
                 "Mittwoch, 14.10.2026, 09:00 Uhr — Fahrradwerkstatt (vergangen, vor 1 Tag)"),
                ("Timeline/anstehend", "Freitag, 16.10.2026, 14:30 Uhr — Zahnarzt (morgen)"),
            ],
        )
        self.assertEqual(timeline.excluded, [ANCHOR])

    def test_without_user_id_no_entries_and_an_error(self) -> None:
        with self.assertLogs("ki_server.plugins.timeline", level="ERROR"):
            entries, timeline = self._entries({})

        self.assertEqual(entries, [])
        self.assertEqual(timeline.excluded, [], "ohne user_id wird nicht gelesen")

    def test_entry_helper_rejects_an_empty_line(self) -> None:
        with self.assertRaises(ValueError):
            TimelineManager._appointment_entry("", False, NOW, "Zahnarzt")


class WriterMemoryWithoutAppointmentsTest(unittest.TestCase):
    """Der Verfasser liest Termine nur im `[TERMINE]`-Block, nicht im Gedaechtnis."""

    ENTRIES: list[dict] = [
        {"quelle": "plugin_timeline", "subtyp": "anstehend", "gewicht": 1.0,
         "inhalt": "Freitag, 16.10.2026, 14:30 Uhr — Zahnarzt (morgen)",
         "meta": {"praefix": "Timeline/anstehend"}},
        {"quelle": "plugin_notizen", "subtyp": "notiz", "gewicht": 1.0,
         "inhalt": "Fahrradschloss kaufen", "meta": {"praefix": "Notizen"}},
    ]

    def test_the_writer_memory_has_no_timeline_lines(self) -> None:
        text: str = format_memory_entries(self.ENTRIES, leser=LESER_VERFASSER)

        self.assertNotIn("[Timeline/", text)
        self.assertIn("[Notizen] Fahrradschloss kaufen", text)

    def test_twin_the_analysis_memory_keeps_them(self) -> None:
        """Thinker, Tribunal und Corrector lesen die Termine weiter im Gedaechtnis."""
        text: str = format_memory_entries(self.ENTRIES, leser=LESER_ANALYSE)

        self.assertIn(
            "[Timeline/anstehend] Freitag, 16.10.2026, 14:30 Uhr — Zahnarzt (morgen)", text,
        )


if __name__ == "__main__":
    unittest.main()
