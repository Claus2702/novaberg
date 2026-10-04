"""Zeugen für die Speisung der Arbeitszyklen im Hauptfenster.

Ohne Fenster: Die Methoden von `MainWindow` laufen ungebunden auf einem Ersatzobjekt, das nur
trägt, was sie lesen — Registry, Chat, Statuszeile, Stream und Eingabefeld sind Attrappen.
Die Registry hält Verteilungen und Sendungen in einer gemeinsamen Liste, damit auch die
Reihenfolge prüfbar ist.
"""

import types
import unittest
from unittest.mock import MagicMock

from ui.main_window import MainWindow
from ui.work_events import TurnFailure, TurnStarted


class _Log:
    """Die gemeinsame Liste: was die Registry und der Stream bekamen, in der Reihenfolge."""

    def __init__(self) -> None:
        self.entries: list[tuple] = []


class _FakeRegistry:
    def __init__(self, log: _Log) -> None:
        self._log = log

    def broadcast_work_event(self, event: object) -> None:
        self._log.entries.append(("work", event))

    def broadcast_impulse(self, turn_data: dict) -> None:
        self._log.entries.append(("impulse", turn_data["antwort"]))


class _FakeStream:
    def __init__(self, log: _Log) -> None:
        self._log = log

    def send_message(self, text: str) -> None:
        self._log.entries.append(("send", text))


def _window(text: str = "") -> tuple[types.SimpleNamespace, _Log]:
    """Ein Ersatz für das Fenster mit den echten Methoden von `MainWindow`."""
    log = _Log()
    entry = MagicMock()
    entry.get_text.return_value = text
    window = types.SimpleNamespace(
        _registry=_FakeRegistry(log),
        _stream=_FakeStream(log),
        _entry=entry,
        _chat_view=MagicMock(),
        _status_bar=MagicMock(),
        _awaiting_response=False,
    )
    window._handle_work_event = types.MethodType(MainWindow._handle_work_event, window)
    return window, log


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


if __name__ == "__main__":
    unittest.main()
