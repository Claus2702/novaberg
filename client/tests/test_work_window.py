"""Zeugen für die Speisung der Arbeitszyklen im Hauptfenster.

Ohne Fenster: Die Methoden von `MainWindow` laufen ungebunden auf einem Ersatzobjekt, das nur
trägt, was sie lesen — Registry, Chat, Statuszeile, Stream und Eingabefeld sind Attrappen.
Die Registry hält Verteilungen und Sendungen in einer gemeinsamen Liste, damit auch die
Reihenfolge prüfbar ist.
"""

import time
import types
import unittest
from unittest.mock import MagicMock

from ui.main_window import MainWindow
from ui.work_events import ImpulseThinking, PixieWork, TurnFailure, TurnStarted
from ui.work_state import IDLE_TEXT, THINKING_TEXT, WATCHDOG_SECONDS, WorkState, advance


class _Log:
    """Die gemeinsame Liste: was die Registry und der Stream bekamen, in der Reihenfolge."""

    def __init__(self) -> None:
        self.entries: list[tuple] = []


class _FakeRegistry:
    def __init__(self, log: _Log, child: object = None) -> None:
        self._log = log
        self._child = child

    def open_panel(self, panel_id: str, parent: object) -> object:
        return self._child

    def broadcast_work_event(self, event: object) -> None:
        self._log.entries.append(("work", event))

    def broadcast_turn(self, turn_data: dict) -> None:
        self._log.entries.append(("turn", turn_data["antwort"]))

    def broadcast_impulse(self, turn_data: dict) -> None:
        self._log.entries.append(("impulse", turn_data["antwort"]))


class _FakeStream:
    def __init__(self, log: _Log) -> None:
        self._log = log

    def send_message(self, text: str) -> None:
        self._log.entries.append(("send", text))


def _window(
    text: str = "", child: object = None,
) -> tuple[types.SimpleNamespace, _Log]:
    """Ein Ersatz für das Fenster mit den echten Methoden von `MainWindow`."""
    log = _Log()
    entry = MagicMock()
    entry.get_text.return_value = text
    window = types.SimpleNamespace(
        _registry=_FakeRegistry(log, child),
        _stream=_FakeStream(log),
        _entry=entry,
        _chat_view=MagicMock(),
        _status_bar=MagicMock(),
        _awaiting_response=False,
        _work_state=WorkState(),
        _preis_warnung_zeigen=MagicMock(),
    )
    for name in ("_handle_work_event", "_set_work_state", "_handle_message_open"):
        setattr(window, name, types.MethodType(getattr(MainWindow, name), window))
    return window, log


def _shown(window: types.SimpleNamespace) -> tuple[str, str]:
    """Text und Tooltip, die die Statuszeile zuletzt bekam."""
    return window._status_bar.set_work_status.call_args.args


def _work_events(log: _Log) -> list:
    return [entry[1] for entry in log.entries if entry[0] == "work"]


class WorkEventInputTest(unittest.TestCase):
    """Der Eingang gibt das Ereignis an die Registry."""

    def test_the_event_goes_to_the_registry(self) -> None:
        window, log = _window()
        MainWindow._handle_work_event(window, TurnFailure())
        self.assertEqual(log.entries, [("work", TurnFailure())])


class SendTest(unittest.TestCase):
    """Senden ergibt „Turn beginnt“, und zwar bevor die Nachricht den Server erreicht."""

    def test_sending_gives_turn_started_before_the_message_leaves(self) -> None:
        window, log = _window("Hallo Nova")
        MainWindow._send_current_input(window)
        self.assertEqual(log.entries, [("work", TurnStarted()), ("send", "Hallo Nova")])

    def test_an_empty_input_gives_no_turn_started_and_sends_nothing(self) -> None:
        window, log = _window("   ")
        MainWindow._send_current_input(window)
        self.assertEqual(log.entries, [])


class UserMessageTest(unittest.TestCase):
    """Die Nachricht des Nutzers aus einem anderen Client beginnt einen Turn."""

    def test_user_message_of_another_client_gives_turn_started(self) -> None:
        window, log = _window()
        MainWindow._handle_impulse(window, "Hallo", {"typ": "user_message", "nachricht": "Hallo"})
        window._chat_view.add_user_message.assert_called_once_with("Hallo")
        self.assertEqual(_work_events(log), [TurnStarted()])

    def test_an_impulse_of_nova_gives_no_turn_started(self) -> None:
        window, log = _window()
        data = {"typ": "character_response", "reiz_herkunft": "eigener_impuls", "nachricht": "Hm"}
        MainWindow._handle_impulse(window, "Hm", data)
        self.assertEqual(_work_events(log), [])
        self.assertEqual(log.entries, [("impulse", "Hm")])

    def test_another_event_in_the_chat_gives_no_turn_started(self) -> None:
        window, log = _window()
        MainWindow._handle_impulse(window, "Etwas", {"typ": "shadow_delivery"})
        self.assertEqual(_work_events(log), [])


class ErrorTest(unittest.TestCase):
    """Ein Fehler beim Senden ist ein gescheiterter Turn."""

    def test_an_error_while_sending_gives_turn_failure(self) -> None:
        window, log = _window()
        with self.assertLogs("ui.main_window", level="ERROR"):
            MainWindow._handle_error(window, "Netzwerkfehler: weg")
        self.assertEqual(_work_events(log), [TurnFailure()])
        window._chat_view.add_assistant_message.assert_called_once()

    def test_send_then_error_gives_started_then_failure(self) -> None:
        window, log = _window("Hallo")
        MainWindow._send_current_input(window)
        with self.assertLogs("ui.main_window", level="ERROR"):
            MainWindow._handle_error(window, "Netzwerkfehler: weg")
        self.assertEqual(_work_events(log), [TurnStarted(), TurnFailure()])


class StatusLineTest(unittest.TestCase):
    """Die Statuszeile bekommt ihren Text aus dem Arbeitszustand, und nur von dort."""

    def test_sending_shows_the_character_calculation(self) -> None:
        window, _ = _window("Hallo")
        MainWindow._send_current_input(window)
        self.assertEqual(_shown(window)[0], f"Nova: {THINKING_TEXT}")

    def test_a_pixie_job_shows_its_kind_and_the_topic_only_in_the_tooltip(self) -> None:
        window, _ = _window()
        MainWindow._handle_work_event(
            window, PixieWork("beginn", "llm", "recherche", topic="Seidenraupen"),
        )
        text, tooltip = _shown(window)
        self.assertEqual(text, "Pixie: Recherche")
        self.assertIn("Seidenraupen", tooltip)

    def test_the_end_of_the_job_shows_idle(self) -> None:
        window, _ = _window()
        MainWindow._handle_work_event(window, PixieWork("beginn", "llm", "recherche"))
        MainWindow._handle_work_event(window, PixieWork("ende", "llm", "recherche"))
        self.assertEqual(_shown(window)[0], IDLE_TEXT)

    def test_the_state_is_written_before_the_panels_get_the_event(self) -> None:
        window, log = _window()
        window._status_bar.set_work_status.side_effect = (
            lambda *args: log.entries.append(("status", args[0]))
        )
        MainWindow._handle_work_event(window, TurnStarted())
        self.assertEqual(
            log.entries, [("status", f"Nova: {THINKING_TEXT}"), ("work", TurnStarted())],
        )

    def test_a_kind_without_a_text_logs_an_error_and_does_not_show_the_key(self) -> None:
        window, log = _window()
        with self.assertLogs("ui.main_window", level="ERROR"):
            MainWindow._handle_work_event(window, PixieWork("beginn", "llm", "geheimart"))
        self.assertNotIn("geheimart", _shown(window)[0])
        self.assertEqual(_work_events(log), [PixieWork("beginn", "llm", "geheimart")])

    def test_the_answer_to_one_of_two_messages_keeps_the_character_calculation(self) -> None:
        window, _ = _window("Hallo")
        MainWindow._send_current_input(window)
        MainWindow._handle_message_open(window, "a")
        MainWindow._handle_message_open(window, "b")
        MainWindow._handle_answer(window, "Antwort", {"nachrichten_ids": ["a"]})
        self.assertEqual(_shown(window)[0], f"Nova: {THINKING_TEXT}")
        MainWindow._handle_answer(window, "Antwort", {"nachrichten_ids": ["b"]})
        self.assertEqual(_shown(window)[0], IDLE_TEXT)

    def test_the_answer_of_an_impulse_ends_the_impulse(self) -> None:
        window, _ = _window()
        MainWindow._handle_work_event(window, ImpulseThinking("beginn"))
        data = {"typ": "character_response", "reiz_herkunft": "eigener_impuls", "nachricht": "Hm"}
        MainWindow._handle_impulse(window, "Hm", data)
        self.assertEqual(_shown(window)[0], IDLE_TEXT)

    def test_the_momentum_no_longer_writes_to_the_status_line(self) -> None:
        window, _ = _window()
        MainWindow._handle_answer(window, "Antwort", {"momentum": "hoch", "nachrichten_ids": []})
        self.assertNotIn("momentum", str(window._status_bar.mock_calls))
        window._status_bar.set_work_status.assert_called_once_with(IDLE_TEXT, "")


class WatchdogAndGuardTest(unittest.TestCase):
    """Der Takt beendet einen alten Turn; die privaten Methoden weisen Falsches laut ab."""

    def test_the_tick_ends_an_old_turn_and_the_status_line_shows_idle(self) -> None:
        window, _ = _window()
        window._on_watchdog_tick = types.MethodType(MainWindow._on_watchdog_tick, window)
        old = time.monotonic() - WATCHDOG_SECONDS - 1
        window._work_state = advance(WorkState(), TurnStarted(), old)
        self.assertTrue(window._on_watchdog_tick())
        self.assertEqual(_shown(window)[0], IDLE_TEXT)

    def test_the_tick_leaves_a_fresh_turn_alone(self) -> None:
        window, _ = _window()
        window._on_watchdog_tick = types.MethodType(MainWindow._on_watchdog_tick, window)
        window._work_state = advance(WorkState(), TurnStarted(), time.monotonic())
        self.assertTrue(window._on_watchdog_tick())
        window._status_bar.set_work_status.assert_not_called()

    def test_the_tick_rejects_a_missing_state(self) -> None:
        window, _ = _window()
        window._on_watchdog_tick = types.MethodType(MainWindow._on_watchdog_tick, window)
        window._work_state = None
        with self.assertRaises(TypeError):
            window._on_watchdog_tick()

    def test_a_state_that_is_no_work_state_is_rejected_and_the_old_one_stays(self) -> None:
        window, _ = _window()
        with self.assertRaises(TypeError):
            MainWindow._set_work_state(window, "idle")
        self.assertEqual(window._work_state, WorkState())
        MainWindow._set_work_state(window, WorkState())

    def test_an_empty_or_non_text_message_id_is_rejected(self) -> None:
        window, _ = _window()
        with self.assertRaises(ValueError):
            MainWindow._handle_message_open(window, "")
        with self.assertRaises(TypeError):
            MainWindow._handle_message_open(window, 7)
        window._status_bar.set_work_status.assert_not_called()


class _FakePanel:
    REACTS_TO_WORK = True
    PANEL_ID = "avatar"

    def __init__(self) -> None:
        self.events: list = []

    def on_work_event(self, event: object) -> None:
        self.events.append(event)


class _FakeChild:
    def __init__(self) -> None:
        self.panel = _FakePanel()
        self.presented = 0

    def present(self) -> None:
        self.presented += 1


class OpeningTest(unittest.TestCase):
    """Ein Panel, das während des Nachdenkens öffnet, bekommt den Beginn nachgereicht."""

    def _open(self, *events: object) -> _FakeChild:
        child = _FakeChild()
        window, _ = _window(child=child)
        for event in events:
            MainWindow._handle_work_event(window, event)
        MainWindow._on_panel_button_clicked(window, None, "avatar")
        return child

    def test_opening_during_a_turn_gives_turn_started(self) -> None:
        child = self._open(TurnStarted())
        self.assertEqual(child.panel.events, [TurnStarted()])
        self.assertEqual(child.presented, 1)

    def test_opening_during_an_impulse_gives_its_begin(self) -> None:
        child = self._open(ImpulseThinking("beginn"))
        self.assertEqual(child.panel.events, [ImpulseThinking("beginn")])

    def test_opening_without_thinking_gives_nothing(self) -> None:
        child = self._open()
        self.assertEqual(child.panel.events, [])
        self.assertEqual(child.presented, 1)

    def test_a_running_pixie_job_is_not_handed_on(self) -> None:
        child = self._open(PixieWork("beginn", "llm", "recherche"))
        self.assertEqual(child.panel.events, [])

    def test_opening_after_the_turn_ended_gives_nothing(self) -> None:
        child = self._open(TurnStarted(), TurnFailure())
        self.assertEqual(child.panel.events, [])


if __name__ == "__main__":
    unittest.main()
