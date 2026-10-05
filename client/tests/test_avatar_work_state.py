"""Zeugen für den Arbeitszustand und den Text der Statuszeile, ohne Fenster.

`ui.work_state` importiert kein GTK und liest keine Uhr; die Zeit kommt hier als Zahl.
"""

import unittest

from ui.work_events import ImpulseThinking, PixieWork, TurnFailure, TurnStarted
from ui.work_state import (
    IDLE_TEXT,
    JOB_TEXTS,
    THINKING_TEXT,
    WATCHDOG_SECONDS,
    RunningJob,
    WorkState,
    advance,
    expire,
    impulse_answered,
    job_text,
    message_opened,
    named_ids,
    opening_event,
    status_text,
    turn_answered,
)


def _begin(track: str = "llm", kind: str = "recherche", topic: str | None = None) -> PixieWork:
    return PixieWork("beginn", track, kind, topic=topic)


def _end(track: str = "llm", kind: str = "recherche") -> PixieWork:
    return PixieWork("ende", track, kind)


def _turn(*ids: str, since: float = 0.0) -> WorkState:
    """Ein denkender Turn mit den offenen Nachrichten `ids`."""
    state = advance(WorkState(), TurnStarted(), since)
    for message_id in ids:
        state = message_opened(state, message_id)
    return state


class TurnTest(unittest.TestCase):
    """Der Turn folgt der Menge der offenen Nachrichten."""

    def test_sending_makes_the_character_graph_think(self) -> None:
        self.assertEqual(status_text(_turn()).text, f"Nova: {THINKING_TEXT}")

    def test_an_answer_to_the_first_of_two_keeps_it_thinking(self) -> None:
        state = turn_answered(_turn("a", "b"), ["a"])
        self.assertEqual(status_text(state).text, f"Nova: {THINKING_TEXT}")
        self.assertEqual(state.open_ids, frozenset({"b"}))

    def test_an_answer_naming_both_ends_the_turn(self) -> None:
        state = turn_answered(_turn("a", "b"), ["a", "b"])
        self.assertEqual(status_text(state).text, IDLE_TEXT)

    def test_two_answers_one_after_the_other_end_it_at_the_second(self) -> None:
        state = turn_answered(turn_answered(_turn("a", "b"), ["a"]), ["b"])
        self.assertEqual(status_text(state).text, IDLE_TEXT)

    def test_an_answer_naming_only_a_stranger_keeps_open_messages_open(self) -> None:
        state = turn_answered(_turn("a"), ["x"])
        self.assertEqual(state.open_ids, frozenset({"a"}))
        self.assertTrue(state.thinking)

    def test_an_answer_when_the_id_was_never_known_ends_the_turn(self) -> None:
        # Die Nachricht kam aus einem anderen Client: Der Turn begann ohne bekannte Kennung.
        state = turn_answered(_turn(), ["fremd"])
        self.assertEqual(status_text(state).text, IDLE_TEXT)

    def test_an_answer_without_a_turn_changes_nothing(self) -> None:
        self.assertEqual(turn_answered(WorkState(), ["a"]), WorkState())

    def test_failure_ends_the_turn_and_clears_the_open_messages(self) -> None:
        state = advance(_turn("a", "b"), TurnFailure(), 1.0)
        self.assertEqual(status_text(state).text, IDLE_TEXT)
        self.assertEqual(state.open_ids, frozenset())

    def test_a_confirmed_id_after_the_end_is_not_taken_in(self) -> None:
        state = advance(_turn(), TurnFailure(), 1.0)
        with self.assertLogs("ui.work_state", level="INFO"):
            after = message_opened(state, "a")
        self.assertEqual(after, state)

    def test_a_second_send_keeps_the_known_ids(self) -> None:
        state = advance(_turn("a"), TurnStarted(), 5.0)
        self.assertEqual(state.open_ids, frozenset({"a"}))

    def test_named_ids_keeps_only_texts(self) -> None:
        self.assertEqual(named_ids({"nachrichten_ids": ["a", "", 3, "b"]}), {"a", "b"})

    def test_named_ids_without_a_list_is_empty_and_warns(self) -> None:
        with self.assertLogs("ui.work_state", level="WARNING"):
            self.assertEqual(named_ids({}), frozenset())

    def test_a_string_instead_of_ids_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            turn_answered(_turn("a"), "a")


class WatchdogTest(unittest.TestCase):
    """600 s ohne Antwort oder Ende beenden einen Turn oder Impuls."""

    def test_the_turn_thinks_at_599_seconds(self) -> None:
        self.assertTrue(expire(_turn("a", since=100.0), 100.0 + 599).thinking)

    def test_the_turn_is_over_at_600_seconds_with_a_warning(self) -> None:
        with self.assertLogs("ui.work_state", level="WARNING"):
            state = expire(_turn("a", since=100.0), 100.0 + WATCHDOG_SECONDS)
        self.assertEqual(status_text(state).text, IDLE_TEXT)
        self.assertEqual(state.open_ids, frozenset())

    def test_the_impulse_thinks_at_599_seconds(self) -> None:
        state = advance(WorkState(), ImpulseThinking("beginn"), 10.0)
        self.assertTrue(expire(state, 10.0 + 599).thinking)

    def test_the_impulse_is_over_at_600_seconds_with_a_warning(self) -> None:
        state = advance(WorkState(), ImpulseThinking("beginn"), 10.0)
        with self.assertLogs("ui.work_state", level="WARNING"):
            state = expire(state, 10.0 + 600)
        self.assertEqual(status_text(state).text, IDLE_TEXT)

    def test_a_new_send_restarts_the_clock(self) -> None:
        state = advance(_turn(since=0.0), TurnStarted(), 500.0)
        self.assertTrue(expire(state, 700.0).thinking)

    def test_the_watchdog_does_not_end_a_pixie_job(self) -> None:
        state = advance(WorkState(), _begin(), 0.0)
        self.assertEqual(expire(state, 10_000.0).jobs, state.jobs)

    def test_the_watchdog_ends_only_what_is_old(self) -> None:
        state = advance(_turn(since=0.0), ImpulseThinking("beginn"), 400.0)
        with self.assertLogs("ui.work_state", level="WARNING"):
            state = expire(state, 650.0)
        self.assertIsNone(state.turn_since)
        self.assertIsNotNone(state.impulse_since)

    def test_the_clock_is_an_argument_and_must_be_a_number(self) -> None:
        with self.assertRaises(TypeError):
            expire(WorkState(), "jetzt")


class ImpulseTest(unittest.TestCase):
    """Ein Impuls denkt von `beginn` bis `ende` oder bis zur Antwort aus ihm."""

    def test_begin_thinks_and_end_is_idle(self) -> None:
        state = advance(WorkState(), ImpulseThinking("beginn"), 0.0)
        self.assertEqual(status_text(state).text, f"Nova: {THINKING_TEXT}")
        state = advance(state, ImpulseThinking("ende"), 1.0)
        self.assertEqual(status_text(state).text, IDLE_TEXT)

    def test_the_answer_from_an_impulse_ends_it(self) -> None:
        state = advance(WorkState(), ImpulseThinking("beginn"), 0.0)
        self.assertEqual(status_text(impulse_answered(state)).text, IDLE_TEXT)

    def test_the_end_of_an_impulse_leaves_a_turn_thinking(self) -> None:
        state = advance(_turn("a"), ImpulseThinking("beginn"), 1.0)
        state = advance(state, ImpulseThinking("ende"), 2.0)
        self.assertEqual(status_text(state).text, f"Nova: {THINKING_TEXT}")

    def test_the_answer_to_a_turn_leaves_an_impulse_thinking(self) -> None:
        state = advance(_turn("a"), ImpulseThinking("beginn"), 1.0)
        state = turn_answered(state, ["a"])
        self.assertEqual(status_text(state).text, f"Nova: {THINKING_TEXT}")

    def test_an_unknown_phase_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            advance(WorkState(), ImpulseThinking("mitte"), 0.0)


class PixieTest(unittest.TestCase):
    """Pixies Aufträge je Spur, die Art lesbar, das Thema nur im Tooltip."""

    def test_begin_shows_the_kind_readable_and_the_topic_only_in_the_tooltip(self) -> None:
        shown = status_text(advance(WorkState(), _begin(topic="Seidenraupen"), 0.0))
        self.assertEqual(shown.text, "Pixie: Recherche")
        self.assertNotIn("Seidenraupen", shown.text)
        self.assertIn("Seidenraupen", shown.tooltip)

    def test_end_in_the_only_track_is_idle(self) -> None:
        state = advance(advance(WorkState(), _begin(), 0.0), _end(), 1.0)
        self.assertEqual(status_text(state).text, IDLE_TEXT)

    def test_two_tracks_show_both_and_are_idle_only_when_both_end(self) -> None:
        state = advance(WorkState(), _begin("llm", "recherche"), 0.0)
        state = advance(state, _begin("cpu", "wiedervorlage"), 1.0)
        self.assertEqual(status_text(state).text, "Pixie: Recherche, Wiedervorlage")
        state = advance(state, _end("llm"), 2.0)
        self.assertEqual(status_text(state).text, "Pixie: Wiedervorlage")
        state = advance(state, _end("cpu"), 3.0)
        self.assertEqual(status_text(state).text, IDLE_TEXT)

    def test_nova_and_pixie_stand_side_by_side(self) -> None:
        state = advance(_turn("a"), _begin(), 1.0)
        self.assertEqual(status_text(state).text, f"Nova: {THINKING_TEXT} · Pixie: Recherche")

    def test_the_order_of_the_tracks_does_not_depend_on_the_order_of_arrival(self) -> None:
        state = advance(WorkState(), _begin("cpu", "delegation"), 0.0)
        state = advance(state, _begin("llm", "recherche"), 1.0)
        self.assertEqual(status_text(state).text, "Pixie: Recherche, Delegation")

    def test_a_new_begin_in_a_busy_track_replaces_the_job_and_warns(self) -> None:
        state = advance(WorkState(), _begin("llm", "recherche"), 0.0)
        with self.assertLogs("ui.work_state", level="WARNING"):
            state = advance(state, _begin("llm", "vertiefen"), 1.0)
        self.assertEqual(status_text(state).text, "Pixie: Vertiefung")

    def test_an_end_without_a_job_warns_and_changes_nothing(self) -> None:
        with self.assertLogs("ui.work_state", level="WARNING"):
            state = advance(WorkState(), _end(), 0.0)
        self.assertEqual(state, WorkState())

    def test_the_end_of_a_job_leaves_the_turn_thinking(self) -> None:
        state = advance(advance(_turn("a"), _begin(), 1.0), _end(), 2.0)
        self.assertEqual(status_text(state).text, f"Nova: {THINKING_TEXT}")

    def test_the_tooltip_of_nothing_is_empty(self) -> None:
        self.assertEqual(status_text(WorkState()).tooltip, "")


class NoGapTest(unittest.TestCase):
    """An keinem Übergang steht *idle*, solange etwas läuft."""

    def test_a_mixed_sequence_is_never_idle_while_something_runs(self) -> None:
        steps = [
            (TurnStarted(), True),
            (_begin("llm", "recherche"), True),
            (ImpulseThinking("beginn"), True),
            (_begin("cpu", "lzg_promotion"), True),
            (_end("llm"), True),
            (ImpulseThinking("ende"), True),
            (TurnFailure(), True),
            (_end("cpu", "lzg_promotion"), False),
        ]
        state = WorkState()
        for number, (event, running) in enumerate(steps):
            state = advance(state, event, float(number))
            with self.subTest(step=number, event=type(event).__name__):
                self.assertEqual(status_text(state).text != IDLE_TEXT, running)

    def test_an_answer_sequence_with_a_job_in_between_is_never_idle(self) -> None:
        state = _turn("a", "b")
        state = advance(state, _begin(), 1.0)
        for number, answered in enumerate((["a"], ["b"]), start=2):
            state = turn_answered(state, answered)
            with self.subTest(step=number):
                self.assertNotEqual(status_text(state).text, IDLE_TEXT)
        state = advance(state, _end(), 4.0)
        self.assertEqual(status_text(state).text, IDLE_TEXT)


class TextTableTest(unittest.TestCase):
    """Jede Art der Tabelle hat ihren Text; eine Art ohne Text wirft."""

    EXPECTED = {
        "recherche": "Recherche",
        "vertiefen": "Vertiefung",
        "nachfragen": "Nachfrage",
        "wiedervorlage": "Wiedervorlage",
        "wissen_rueckweg": "Wissensablage",
        "wissen_verweis": "Wissensverweis",
        "lzg_promotion": "Gedächtnis-Promotion",
        "delegation": "Delegation",
    }

    def test_every_kind_has_its_text(self) -> None:
        self.assertEqual(JOB_TEXTS, self.EXPECTED)
        for kind, text in self.EXPECTED.items():
            with self.subTest(kind=kind):
                state = advance(WorkState(), _begin(kind=kind), 0.0)
                self.assertEqual(status_text(state).text, f"Pixie: {text}")
                self.assertEqual(job_text(kind), text)

    def test_a_kind_without_a_text_raises_instead_of_showing_the_key(self) -> None:
        with self.assertRaises(ValueError):
            job_text("unbekannt")
        state = advance(WorkState(), _begin(kind="unbekannt"), 0.0)
        with self.assertRaises(ValueError):
            status_text(state)


class OpeningTest(unittest.TestCase):
    """Das Panel beginnt im Nachdenken, wenn der CharacterGraph denkt."""

    def test_a_turn_gives_turn_started(self) -> None:
        self.assertEqual(opening_event(_turn("a")), TurnStarted())

    def test_an_impulse_gives_its_begin(self) -> None:
        state = advance(WorkState(), ImpulseThinking("beginn"), 0.0)
        self.assertEqual(opening_event(state), ImpulseThinking("beginn"))

    def test_nothing_thinking_gives_none_even_with_a_pixie_job(self) -> None:
        state = advance(WorkState(), _begin(), 0.0)
        self.assertIsNone(opening_event(state))


class RefusalTest(unittest.TestCase):
    """Falsche Eingaben werden laut abgewiesen."""

    def test_a_foreign_event_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            advance(WorkState(), "turn", 0.0)

    def test_a_foreign_state_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            advance({}, TurnStarted(), 0.0)

    def test_open_ids_without_a_turn_are_not_a_state(self) -> None:
        with self.assertRaises(ValueError):
            WorkState(open_ids=frozenset({"a"}))

    def test_an_empty_id_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            message_opened(_turn(), "")

    def test_a_job_in_an_unknown_track_is_not_a_state(self) -> None:
        with self.assertRaises(ValueError):
            WorkState(jobs=(RunningJob("gpu", "recherche"),))


if __name__ == "__main__":
    unittest.main()
