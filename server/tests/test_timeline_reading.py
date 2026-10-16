"""Zeugen: Eine Frage nach Terminen bringt die Termine im selben Turn in den Prompt.

Der gezielte Leseweg stand im Enricher, und der laeuft vor dem Router. Erst
der Router setzt `needs_timeline` und `timeline_query` — der gezielte Zweig
war deshalb nie erreichbar. Gelesen wird jetzt hinter dem Router
(`graph/base.py::_node_route`), der Verfasser setzt daraus den
`[TERMINE]`-Block.

Zeugen dieser Datei:
  * **Die Verdrahtung laeuft durch das echte Framework**: Router-Knoten und
    Verfasser als zwei Knoten eines `StateGraph(ConversationState)`. Ein
    Zeuge am Block allein bewiese nur, dass der Block kann — nicht, dass er
    im Prompt ankommt.
  * **Ohne Datenbank**: Die Timeline ist ein Doppel, das nach Zeitraum,
    Titel und Typausschluss filtert und jeden Aufruf mitschreibt. Die Uhr
    steht auf Donnerstag, 15.10.2026, 18:00 Ortszeit.
  * **Der Erinnerungs-Anker im Bestand** liegt im gefragten Zeitraum. Ein
    Leseweg ohne Typfilter braechte ihn als Termin.
  * Die Beispiele sind synthetisch.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import logging
import unittest
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

from langgraph.graph import END, StateGraph

from ei.haltung import haltung_berechnen
from graph.appointments import AppointmentReading, AppointmentWindow, proactive_window
from graph.format.appointments import (
    FAILED_SENTENCE,
    appointment_line,
    appointments_body,
    relative_day,
)
from graph.nodes import verfasser
from graph.state import ConversationState
from memory.timeline_reading import read_for_turn, to_appointment

BERLIN: ZoneInfo = ZoneInfo("Europe/Berlin")

#: Die eingefrorene Uhr: Donnerstag, 15.10.2026, 18:00 Ortszeit.
NOW: datetime = datetime(2026, 10, 15, 18, 0, tzinfo=BERLIN)

URL: str = "postgresql://attrappe"
ANCHOR_TITLE: str = "Erinnerungs-Anker 17.10.2026 Rufus"

#: Die Woche, nach der gefragt wird: Montag bis Sonntag.
WEEK_QUERY: dict = {"type": "range", "from": "2026-10-12 00:00", "to": "2026-10-18 23:59"}

LINE_PAST: str = "- Mittwoch, 14.10.2026, 09:00 Uhr — Fahrradwerkstatt (vergangen, vor 1 Tag)"
LINE_TODAY: str = "- Donnerstag, 15.10.2026, 20:00 Uhr — Chorprobe (heute)"
LINE_TOMORROW: str = "- Freitag, 16.10.2026, 14:30 Uhr — Zahnarzt — Praxis Ostheim (morgen)"
LINE_DAY_ONLY: str = "- Sonntag, 18.10.2026, ohne Uhrzeit — Geburtstag Merten (in 3 Tagen)"


def _row(  # noqa: PLR0913 — eine Zeile der Tabelle, ein Argument je Feld
    row_id: int, moment: datetime, title: str, *, event_type: str = "termin",
    precision: str = "minute", details: str | None = None,
) -> dict:
    """Eine Timeline-Zeile, wie das Repository sie liefert (Ortszeit, aktiv)."""
    return {
        "id": row_id, "event_time": moment, "title": title, "event_type": event_type,
        "precision": precision, "details": details, "aktiv": True,
    }


def _stock(anchor_type: str = "erinnerungs_anker") -> list[dict]:
    """Der Bestand: fuenf Termine und ein Anker mitten in der gefragten Woche."""
    return [
        _row(1, datetime(2026, 10, 14, 9, 0, tzinfo=BERLIN), "Fahrradwerkstatt"),
        _row(2, datetime(2026, 10, 15, 20, 0, tzinfo=BERLIN), "Chorprobe"),
        _row(3, datetime(2026, 10, 16, 14, 30, tzinfo=BERLIN), "Zahnarzt",
             details="Praxis Ostheim"),
        _row(4, datetime(2026, 10, 18, 0, 0, tzinfo=BERLIN), "Geburtstag Merten",
             precision="day"),
        _row(5, datetime(2026, 10, 22, 10, 0, tzinfo=BERLIN), "Probe mit Ilva"),
        _row(6, datetime(2026, 10, 17, 9, 0, tzinfo=BERLIN), ANCHOR_TITLE, event_type=anchor_type),
    ]


class FakeTimeline:
    """Doppel des Repositorys: filtert wie die Abfrage und schreibt jeden Aufruf mit.

    Die Mitschrift macht den Typausschluss selbst pruefbar. Ohne sie finge
    die Ausgabe-Verifikation (`to_appointment`) den Anker ab, und ein
    Leseweg ohne Ausschluss in der Abfrage bliebe unbemerkt.
    """

    def __init__(self, rows: list[dict], failure: Exception | None = None) -> None:
        """Der Bestand; `failure` wird bei jedem Lesen geworfen, wenn gesetzt."""
        self.rows: list[dict] = rows
        self.failure: Exception | None = failure
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def find_by_date_range(
        self, postgres_url: str, user_id: str, von: datetime, bis: datetime,
        exclude_event_types: tuple[str, ...] = (),
    ) -> list[dict]:
        """Die Zeilen im Zeitraum, ohne die ausgeschlossenen Typen."""
        self.calls.append(("range", exclude_event_types))
        if self.failure is not None:
            raise self.failure
        return [
            dict(r) for r in sorted(self.rows, key=lambda r: r["event_time"])
            if von <= r["event_time"] <= bis and r["event_type"] not in exclude_event_types
        ]

    def find_by_keyword(  # noqa: PLR0913 — dieselbe Unterschrift wie das Repository
        self, postgres_url: str, user_id: str, keyword: str,
        direction: str = "forward", limit: int = 5, *,
        exclude_event_types: tuple[str, ...] = (),
        now: datetime | None = None, timed_precisions: frozenset[str] = frozenset(),
    ) -> list[dict]:
        """Die Zeilen, deren Titel den Suchbegriff traegt, in der Richtung zur Uhr.

        Wie die Abfrage: Mit `now` ist *vergangen* je Genauigkeit abgegrenzt
        (`_KEYWORD_PAST_SQL`), ohne `now` gilt die Uhr der Datenbank wie bisher —
        ein Termin ohne Uhrzeit von heute zaehlt dann bei `backward` mit.
        `backward` liefert absteigend, `LIMIT` schneidet danach.
        """
        self.calls.append(("keyword", exclude_event_types))
        if self.failure is not None:
            raise self.failure

        def in_direction(r: dict) -> bool:
            if direction not in ("forward", "backward"):
                return True
            if now is None:
                return r["event_time"] >= NOW if direction == "forward" else r["event_time"] <= NOW
            bound: datetime = now if r["precision"] in timed_precisions else now.replace(
                hour=0, minute=0, second=0, microsecond=0,
            )
            return (r["event_time"] < bound) == (direction == "backward")

        hits: list[dict] = [
            dict(r) for r in sorted(
                self.rows, key=lambda r: r["event_time"], reverse=direction == "backward",
            )
            if keyword.lower() in r["title"].lower() and r["event_type"] not in exclude_event_types
            and in_direction(r)
        ]
        return hits[:limit]


def _initial_state() -> dict:
    """Ein Zustand, mit dem der Verfasser seinen Systemprompt baut."""
    return {
        "user_prompt": "Welche Termine habe ich diese Woche?", "user_id": "pruefer",
        "character_id": "c", "turn_id": "t", "memory_context": "", "web_context": "",
        "session_turns": [], "task_block": "", "event_payload": {}, "event_source": "user",
        "gespraechsvektor": "", "gv_detail": {},
        "sachlage": {"herkunft": "impuls_uebernommen"},
        "haltung": haltung_berechnen("werkstatt", {}),
        "needs_timeline": False, "timeline_query": {}, "node_annotations": [],
    }


def _prompt_of_turn(router_fields: dict, timeline: FakeTimeline) -> str:
    """Faehrt Router-Knoten und Verfasser durch einen echten Graphen.

    Der Router selbst ist ersetzt: Er setzt die Felder, die ein Modell fuer
    die Frage gesetzt haette. Alles danach — Lesen, Kanal, Block — ist echt.
    """
    def route_node(state: ConversationState) -> ConversationState:
        from graph.base import GraphBase

        return GraphBase._node_route(SimpleNamespace(postgres_url=URL), state)

    def writer_node(state: ConversationState) -> dict:
        return {"node_annotations": [verfasser._build_system_prompt(state)]}

    graph = StateGraph(ConversationState)
    graph.add_node("route", route_node)
    graph.add_node("writer", writer_node)
    graph.set_entry_point("route")
    graph.add_edge("route", "writer")
    graph.add_edge("writer", END)
    compiled = graph.compile()

    with patch("graph.base.route", side_effect=lambda s: {**s, **router_fields}), \
            patch("graph.base.now_local", return_value=NOW), \
            patch("memory.timeline_reading.TimelineRepository", timeline):
        result: dict = compiled.invoke(_initial_state())
    return result["node_annotations"][-1]


def _read(query: dict, timeline: FakeTimeline, now: datetime = NOW) -> AppointmentReading:
    """Das Leseergebnis eines Turns mit gezielter Anfrage, ohne Graph."""
    with patch("memory.timeline_reading.TimelineRepository", timeline):
        return read_for_turn(
            {"user_id": "pruefer", "needs_timeline": True, "timeline_query": query}, URL, now,
        )


def _raised(records: list[logging.LogRecord]) -> str:
    """Die Texte der Ausnahmen, die mit den Protokollzeilen gemeldet wurden."""
    return "\n".join(str(r.exc_info[1]) for r in records if r.exc_info)


class TargetedReadingReachesThePromptTest(unittest.TestCase):
    """Die Frage nach der Woche bringt die Termine der Woche in den Prompt."""

    def test_range_over_the_week_puts_its_appointments_into_the_prompt(self) -> None:
        """Bis zum Umbau rot: Der gezielte Zweig war im Turn nie erreichbar."""
        prompt: str = _prompt_of_turn(
            {"needs_timeline": True, "timeline_query": WEEK_QUERY}, FakeTimeline(_stock()),
        )

        self.assertIn("[TERMINE]", prompt)
        self.assertIn("Gelesen: Zeitraum Montag, 12.10.2026 bis Sonntag, 18.10.2026.", prompt)
        for line in (LINE_PAST, LINE_TODAY, LINE_TOMORROW, LINE_DAY_ONLY):
            self.assertIn(line, prompt)
        self.assertNotIn("Probe mit Ilva", prompt, "ein Termin ausserhalb der Woche")

    def test_the_block_sits_in_the_system_prompt_not_in_the_memory_block(self) -> None:
        """Die Termine stehen im eigenen Block, nach seinem Kopf."""
        prompt: str = _prompt_of_turn(
            {"needs_timeline": True, "timeline_query": WEEK_QUERY}, FakeTimeline(_stock()),
        )

        self.assertLess(prompt.index("[TERMINE]"), prompt.index(LINE_TOMORROW))
        self.assertIn("nennt der Inhalt nur aus diesem Block", prompt)

    def test_search_by_title_puts_the_hit_into_the_block(self) -> None:
        reading: AppointmentReading = _read(
            {"type": "search", "keyword": "Zahnarzt"}, FakeTimeline(_stock()),
        )
        body: str = appointments_body(reading)

        self.assertIn('Gelesen: Suche nach "Zahnarzt" in den Titeln, hoechstens 5 Treffer.', body)
        self.assertIn(LINE_TOMORROW, body)
        self.assertNotIn("Chorprobe", body)

    def test_without_needs_timeline_the_proactive_window_stands_in_the_same_form(self) -> None:
        prompt: str = _prompt_of_turn({"needs_timeline": False}, FakeTimeline(_stock()))

        self.assertIn("Nach Terminen wurde nicht gezielt gefragt.", prompt)
        self.assertIn("- Donnerstag, 22.10.2026, 10:00 Uhr — Probe mit Ilva (in 7 Tagen)", prompt)
        self.assertIn(LINE_PAST, prompt)
        self.assertNotIn("Rufus", prompt)


class AnchorIsNoAppointmentTest(unittest.TestCase):
    """Ein Erinnerungs-Anker steht nicht als Termin im Block."""

    def test_anchor_in_the_week_does_not_appear(self) -> None:
        """Bis zum Umbau rot: Das Fenster las ohne Typfilter."""
        body: str = appointments_body(_read(WEEK_QUERY, FakeTimeline(_stock())))

        self.assertNotIn("Rufus", body)

    def test_twin_the_same_row_as_appointment_appears(self) -> None:
        """Der Zwilling: Derselbe Eintrag als Termin steht da — der Bestand traegt ihn."""
        body: str = appointments_body(_read(WEEK_QUERY, FakeTimeline(_stock(anchor_type="termin"))))

        self.assertIn(f"- Samstag, 17.10.2026, 09:00 Uhr — {ANCHOR_TITLE} (in 2 Tagen)", body)

    def test_the_query_itself_excludes_the_anchor(self) -> None:
        """Ausgeschlossen in der Abfrage, nicht dahinter — sonst belegt er Plaetze einer Suche."""
        timeline = FakeTimeline(_stock())
        _read(WEEK_QUERY, timeline)
        _read({"type": "search", "keyword": "Zahnarzt"}, timeline)

        self.assertEqual(
            timeline.calls,
            [("range", ("erinnerungs_anker",)), ("keyword", ("erinnerungs_anker",))],
        )

    def test_an_anchor_row_that_arrives_is_discarded_loudly(self) -> None:
        anchor: dict = _stock()[5]

        with self.assertLogs("ki_server.memory.timeline_reading", level="ERROR"):
            self.assertIsNone(to_appointment(anchor, NOW))

    def test_twin_the_same_row_as_appointment_is_converted(self) -> None:
        row: dict = {**_stock()[5], "event_type": "termin"}

        appointment = to_appointment(row, NOW)

        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.title, ANCHOR_TITLE)


class EmptyAndFailedTest(unittest.TestCase):
    """Ein leerer Zeitraum sagt *keine*; ein Ausfall sagt es nicht."""

    def test_empty_range_says_no_appointments_from_to(self) -> None:
        query: dict = {"type": "range", "from": "2026-10-19", "to": "2026-10-19"}
        reading = _read(query, FakeTimeline(_stock()))

        self.assertEqual(reading.appointments, ())
        self.assertIn("keine Termine vom 19.10.2026 bis 19.10.2026", appointments_body(reading))

    def test_a_read_failure_is_no_empty_range(self) -> None:
        timeline = FakeTimeline(_stock(), failure=RuntimeError("Verbindung getrennt"))

        with self.assertLogs("ki_server.memory.timeline_reading", level="ERROR"):
            reading = _read(WEEK_QUERY, timeline)
        body: str = appointments_body(reading)

        self.assertTrue(reading.failed)
        self.assertEqual(body, FAILED_SENTENCE)
        self.assertNotIn("keine Termine vom", body)

    def test_an_unusable_query_falls_back_to_the_proactive_window_loudly(self) -> None:
        with self.assertLogs("ki_server.graph.appointments", level="ERROR"):
            reading = _read({"type": "kalender"}, FakeTimeline(_stock()))

        self.assertTrue(appointments_body(reading).startswith(
            "Die Frage nach Terminen liess sich keinem Zeitraum zuordnen."
        ))


class DirectionTest(unittest.TestCase):
    """Fassung c: Bei einer Frage nach kommenden fehlen abgelaufene Termine."""

    @staticmethod
    def _body(direction: str) -> str:
        """Der Block fuer die Woche in der gegebenen Richtung."""
        reading = _read({**WEEK_QUERY, "direction": direction}, FakeTimeline(_stock()))
        return appointments_body(reading)

    def test_forward_leaves_out_yesterday(self) -> None:
        body: str = self._body("forward")

        self.assertNotIn("Fahrradwerkstatt", body)
        self.assertIn("— nur kommende Termine", body)
        self.assertIn(LINE_TODAY, body)

    def test_both_marks_yesterday_as_past(self) -> None:
        body: str = self._body("both")

        self.assertIn(LINE_PAST, body)
        self.assertIn(LINE_TOMORROW, body)

    def test_backward_marks_yesterday_as_past_and_leaves_out_the_coming(self) -> None:
        body: str = self._body("backward")

        self.assertIn(LINE_PAST, body)
        self.assertIn("— nur vergangene Termine", body)
        self.assertNotIn("Zahnarzt", body)


class SearchBoundaryTest(unittest.TestCase):
    """Abfrage und Leser grenzen *vergangen* gleich ab — kein Platz des LIMIT geht verloren.

    Der Bestand: ein Termin ohne Uhrzeit von heute und ein frueherer. Ohne
    Uhrzeit ist der heutige nicht vergangen (`to_appointment`); eine Abfrage
    mit `event_time <= NOW()` gaebe ihm bei `backward` trotzdem den einzigen
    Platz, und der Leser verwuerfe ihn danach.
    """

    @staticmethod
    def _stock() -> list[dict]:
        return [
            _row(11, datetime(2026, 10, 15, 0, 0, tzinfo=BERLIN), "Zahnarzt Kontrolle",
                 precision="day"),
            _row(12, datetime(2026, 10, 8, 10, 0, tzinfo=BERLIN), "Zahnarzt Fuellung"),
        ]

    def _reading(self, direction: str) -> AppointmentReading:
        query: dict = {"type": "search", "keyword": "Zahnarzt", "direction": direction, "limit": 1}
        with self.assertNoLogs("ki_server.memory.timeline_reading", level="ERROR"):
            return _read(query, FakeTimeline(self._stock()))

    def test_backward_with_limit_one_puts_the_earlier_into_the_block(self) -> None:
        reading: AppointmentReading = self._reading("backward")
        body: str = appointments_body(reading)

        self.assertIn("08.10.2026, 10:00 Uhr — Zahnarzt Fuellung (vergangen, vor 7 Tagen)", body)
        self.assertNotIn("Kontrolle", body)
        self.assertEqual(reading.discarded, 0)

    def test_twin_forward_with_limit_one_keeps_today_without_time(self) -> None:
        """Der Zwilling: Bei `forward` belegt der heutige den Platz und steht da."""
        reading: AppointmentReading = self._reading("forward")
        body: str = appointments_body(reading)

        self.assertIn("15.10.2026, ohne Uhrzeit — Zahnarzt Kontrolle (heute)", body)
        self.assertNotIn("Fuellung", body)
        self.assertEqual(reading.discarded, 0)

    def test_a_dropped_search_hit_counts_as_discarded_loudly(self) -> None:
        """Liefert die Abfrage einen Treffer der anderen Richtung, zaehlt er und wird gemeldet."""
        timeline = FakeTimeline(self._stock())
        timeline.find_by_keyword = lambda *a, **k: [dict(r) for r in self._stock()]
        query: dict = {"type": "search", "keyword": "Zahnarzt", "direction": "backward", "limit": 2}

        with self.assertLogs("ki_server.memory.timeline_reading", level="ERROR") as logs:
            reading: AppointmentReading = _read(query, timeline)

        self.assertEqual(reading.discarded, 1)
        self.assertIn("verschieden ab", "\n".join(logs.output))
        self.assertEqual([a.title for a in reading.appointments], ["Zahnarzt Fuellung"])


class OutputAgainstTheWindowTest(unittest.TestCase):
    """Die Ausgabe-Verifikation prueft gegen das Fenster, nicht gegen den eigenen Filter.

    Zeitraum und Obergrenze setzt die Abfrage. Verfehlt sie eins von beiden,
    ist das Ergebnis ein Ausfall und kein Block mit fremden Terminen.
    """

    def test_a_row_outside_the_range_fails_the_reading(self) -> None:
        timeline = FakeTimeline(_stock())
        timeline.find_by_date_range = lambda *a, **k: [dict(r) for r in _stock()]

        with self.assertLogs("ki_server.memory.timeline_reading", level="ERROR") as logs:
            reading: AppointmentReading = _read(WEEK_QUERY, timeline)

        self.assertTrue(reading.failed)
        self.assertEqual(reading.appointments, ())
        self.assertIn("ausserhalb des Fensters", _raised(logs.records))

    def test_twin_a_row_on_the_window_start_stays(self) -> None:
        """Der Zwilling: Das Fenster schliesst seine Grenze ein."""
        on_start: dict = _row(21, datetime(2026, 10, 12, 0, 0, tzinfo=BERLIN), "Fruehschicht")

        with self.assertNoLogs("ki_server.memory.timeline_reading", level="ERROR"):
            reading: AppointmentReading = _read(WEEK_QUERY, FakeTimeline([on_start]))

        self.assertFalse(reading.failed)
        self.assertEqual([a.title for a in reading.appointments], ["Fruehschicht"])

    def test_a_search_over_its_limit_fails_the_reading(self) -> None:
        """Mehr Zeilen als `limit` sind ein Ausfall.

        Der Zwilling ist `test_a_dropped_search_hit_counts_as_discarded_loudly`:
        zwei Zeilen bei limit 2, gelesen ohne Ausfall.
        """
        rows: list[dict] = [
            _row(31, datetime(2026, 10, 8, 10, 0, tzinfo=BERLIN), "Zahnarzt Fuellung"),
            _row(32, datetime(2026, 10, 16, 14, 30, tzinfo=BERLIN), "Zahnarzt Kontrolle"),
        ]
        timeline = FakeTimeline(rows)
        timeline.find_by_keyword = lambda *a, **k: [dict(r) for r in rows]
        query: dict = {"type": "search", "keyword": "Zahnarzt", "direction": "both", "limit": 1}

        with self.assertLogs("ki_server.memory.timeline_reading", level="ERROR") as logs:
            reading: AppointmentReading = _read(query, timeline)

        self.assertTrue(reading.failed)
        self.assertIn("limit=1", _raised(logs.records))


class RelationToTodayTest(unittest.TestCase):
    """Der Bezug zu heute nach Kalendertagen in Ortszeit, an den Grenzen."""

    def test_today_and_tomorrow(self) -> None:
        self.assertEqual(relative_day(datetime(2026, 10, 15, 23, 59, tzinfo=BERLIN), NOW), "heute")
        self.assertEqual(relative_day(datetime(2026, 10, 16, 0, 0, tzinfo=BERLIN), NOW), "morgen")

    def test_across_the_end_of_the_month(self) -> None:
        now: datetime = datetime(2026, 10, 31, 12, 0, tzinfo=BERLIN)

        self.assertEqual(relative_day(datetime(2026, 11, 1, 10, 0, tzinfo=BERLIN), now), "morgen")
        self.assertEqual(
            relative_day(datetime(2026, 11, 3, 10, 0, tzinfo=BERLIN), now), "in 3 Tagen",
        )

    def test_shortly_after_local_midnight_yesterday_is_one_day_ago(self) -> None:
        """In UTC ist es noch der 15. — in Ortszeit ist der Termin von gestern."""
        now: datetime = datetime(2026, 10, 16, 0, 10, tzinfo=BERLIN)
        moment: datetime = datetime(2026, 10, 15, 21, 0, tzinfo=UTC)

        self.assertEqual(relative_day(moment, now), "vor 1 Tag")

        appointment = to_appointment(_row(9, moment, "Spaetschicht"), now)
        self.assertEqual(
            appointment_line(appointment, now),
            "- Donnerstag, 15.10.2026, 23:00 Uhr — Spaetschicht (vergangen, vor 1 Tag)",
        )

    def test_several_days_ago(self) -> None:
        self.assertEqual(
            relative_day(datetime(2026, 10, 6, 9, 0, tzinfo=BERLIN), NOW), "vor 9 Tagen",
        )


class ChannelAndBlockTest(unittest.TestCase):
    """Der Kanal ueberlebt die Knotengrenze; ein fehlendes Ergebnis ist laut."""

    def test_the_channel_is_declared(self) -> None:
        self.assertIn("appointment_reading", ConversationState.__annotations__)

    def test_the_channel_is_not_preset(self) -> None:
        """Ein Startwert loeschte den Unterschied zu *nicht gelesen*."""
        from graph.base import GraphBase

        self.assertNotIn("appointment_reading", str(GraphBase.create_state.__code__.co_consts))

    def test_missing_reading_gives_no_block_and_an_error(self) -> None:
        with self.assertLogs("ki_server.verfasser", level="ERROR"):
            self.assertEqual(verfasser._appointments_block({}), "")

    def test_twin_a_reading_gives_the_block(self) -> None:
        window: AppointmentWindow = proactive_window(NOW)
        block: str = verfasser._appointments_block(
            {"appointment_reading": AppointmentReading(window=window, now=NOW)},
        )

        self.assertTrue(block.startswith("[TERMINE]"))
        self.assertIn("keine Termine vom 12.10.2026 bis 29.10.2026", block)


if __name__ == "__main__":
    unittest.main()
