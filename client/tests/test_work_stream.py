"""Zeugen für den Eingang der Arbeitszyklen im Stream-Handler.

Wie `test_stream_assignment.py`: Der Handler braucht weder Server noch Fenster, und
`GLib.idle_add` wird durch einen Aufruf auf der Stelle ersetzt.
"""

import json
import unittest
from unittest.mock import patch

from ui.stream_handler import StreamHandler
from ui.work_events import ImpulseThinking, PixieWork, TurnFailure


class _Recorder:
    """Sammelt, was die Rückrufe des Handlers bekommen."""

    def __init__(self) -> None:
        self.stages: list[tuple] = []
        self.answers: list[tuple] = []
        self.impulses: list[tuple] = []
        self.work_events: list = []

    def handler(self) -> StreamHandler:
        still = lambda *args, **kwargs: None  # noqa: E731
        return StreamHandler(
            on_stage=lambda label, detail: self.stages.append((label, detail)),
            on_answer=lambda text, data: self.answers.append((text, data)),
            on_error=still,
            on_done=still,
            on_impulse=lambda text, data: self.impulses.append((text, data)),
            on_connection=still,
            on_work_event=self.work_events.append,
        )


def _send(handler: StreamHandler, payload: dict) -> None:
    with patch("ui.stream_handler.GLib.idle_add", side_effect=lambda f, *a: f(*a)):
        handler._ws_on_message(None, json.dumps(payload))


def _pixie(**extra) -> dict:
    payload = {
        "typ": "pixie_auftrag",
        "phase": "beginn",
        "spur": "cpu",
        "art": "vertiefung",
        "thema": "Seidenraupen",
    }
    payload.update(extra)
    return payload


class MessageOpenTest(unittest.TestCase):
    """Die Bestätigung des Servers meldet die Kennung dem Beobachter."""

    def _handler(self, opened: list) -> StreamHandler:
        still = lambda *args, **kwargs: None  # noqa: E731
        return StreamHandler(
            on_stage=still, on_answer=still, on_error=still, on_done=still,
            on_impulse=still, on_connection=still, on_work_event=still,
            on_message_open=opened.append,
        )

    def _confirm(self, handler: StreamHandler, payload: dict) -> None:
        with patch("ui.stream_handler.GLib.idle_add", side_effect=lambda f, *a: f(*a)):
            handler._dispatch_sse_event("processing", json.dumps(payload))

    def test_the_confirmed_id_reaches_the_observer(self) -> None:
        opened: list = []
        self._confirm(self._handler(opened), {"nachrichten_id": "m1"})
        self.assertEqual(opened, ["m1"])

    def test_a_confirmation_without_an_id_reaches_nobody(self) -> None:
        opened: list = []
        with self.assertLogs("ui.stream_handler", level="ERROR"):
            self._confirm(self._handler(opened), {})
        self.assertEqual(opened, [])

    def test_without_an_observer_the_confirmation_still_works(self) -> None:
        handler = _Recorder().handler()
        self._confirm(handler, {"nachrichten_id": "m1"})
        self.assertEqual(handler._offene_nachrichten, {"m1"})


class WorkEventEntryTest(unittest.TestCase):
    """Die drei Typen erreichen den neuen Rückruf und sonst nichts."""

    def setUp(self) -> None:
        self.rec = _Recorder()
        self.handler = self.rec.handler()

    def test_pixie_auftrag_reaches_the_work_callback_and_not_the_chat(self) -> None:
        _send(self.handler, _pixie())
        self.assertEqual(
            self.rec.work_events,
            [PixieWork("beginn", "cpu", "vertiefung", None, None, "Seidenraupen")],
        )
        self.assertEqual(self.rec.impulses, [])
        self.assertEqual(self.rec.answers, [])

    def test_impuls_denkt_reaches_the_work_callback_and_not_the_chat(self) -> None:
        _send(self.handler, {"typ": "impuls_denkt", "phase": "beginn"})
        self.assertEqual(self.rec.work_events, [ImpulseThinking("beginn")])
        self.assertEqual(self.rec.impulses, [])

    def test_turn_gescheitert_reaches_the_work_callback_and_keeps_its_stage(self) -> None:
        _send(self.handler, {"typ": "turn_gescheitert", "nachricht": "Ausfall!"})
        self.assertEqual(self.rec.work_events, [TurnFailure()])
        self.assertEqual(self.rec.stages, [("Ausfall", "Ausfall!")])
        self.assertEqual(self.rec.impulses, [])

    def test_turn_gescheitert_still_releases_its_ids(self) -> None:
        self.handler._offene_nachrichten = {"m1", "m2"}
        _send(self.handler, {"typ": "turn_gescheitert", "nachrichten_ids": ["m1"]})
        self.assertEqual(self.handler._offene_nachrichten, {"m2"})
        self.assertEqual(self.rec.work_events, [TurnFailure()])

    def test_invalid_payload_gives_an_error_line_and_reaches_nobody(self) -> None:
        with self.assertLogs("ui.work_events", level="ERROR"):
            _send(self.handler, _pixie(phase="mitte"))
        self.assertEqual(self.rec.work_events, [])
        self.assertEqual(self.rec.impulses, [])

    def test_a_failing_work_callback_is_logged_and_does_not_escape(self) -> None:
        def broken(event: object) -> None:
            raise ValueError("kaputt")

        handler = self.rec.handler()
        handler._on_work_event = broken
        with self.assertLogs("ui.stream_handler", level="ERROR"):
            self.assertFalse(handler._invoke_work_event(TurnFailure()))


class UntouchedPathsTest(unittest.TestCase):
    """Die Zwillinge: Was nicht zu den Arbeitszyklen gehört, geht seinen alten Weg."""

    def setUp(self) -> None:
        self.rec = _Recorder()
        self.handler = self.rec.handler()

    def test_unknown_type_still_falls_into_the_catch_all(self) -> None:
        _send(self.handler, {"typ": "shadow_delivery", "nachricht": "Etwas"})
        self.assertEqual(len(self.rec.impulses), 1)
        self.assertEqual(self.rec.impulses[0][0], "Etwas")
        self.assertEqual(self.rec.work_events, [])

    def test_character_response_still_goes_to_the_answer(self) -> None:
        _send(
            self.handler,
            {"typ": "character_response", "nachricht": "Hallo", "nachrichten_ids": []},
        )
        self.assertEqual(len(self.rec.answers), 1)
        self.assertEqual(self.rec.answers[0][0], "Hallo")
        self.assertEqual(self.rec.work_events, [])

    def test_user_message_still_goes_to_the_impulse_callback(self) -> None:
        _send(self.handler, {"typ": "user_message", "nachricht": "Hallo"})
        self.assertEqual(len(self.rec.impulses), 1)
        self.assertEqual(self.rec.work_events, [])


class DispatchTest(unittest.TestCase):
    """Die Umformung steht vor `idle_add`: Ein ungültiges Ereignis erreicht den UI-Thread nie."""

    def test_dispatch_hands_the_event_not_the_payload_to_idle_add(self) -> None:
        handler = _Recorder().handler()
        with patch("ui.stream_handler.GLib.idle_add") as idle_add:
            handler._dispatch_work_event({"typ": "turn_gescheitert"})
        idle_add.assert_called_once_with(handler._invoke_work_event, TurnFailure())

    def test_dispatch_of_an_invalid_payload_hands_nothing_over(self) -> None:
        handler = _Recorder().handler()
        with patch("ui.stream_handler.GLib.idle_add") as idle_add:
            with self.assertLogs("ui.work_events", level="ERROR"):
                handler._dispatch_work_event({"typ": "impuls_denkt", "phase": "?"})
        idle_add.assert_not_called()


if __name__ == "__main__":
    unittest.main()
