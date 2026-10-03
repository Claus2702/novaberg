"""Zeugen für den Weg eines Impulses Novas zum Avatar.

Die Verteilung liegt in ``ui.turn_routing`` und braucht weder GTK noch cairo:
Ersatz-Panels tragen nur die Attribute, die die Verteilung liest.
"""

import unittest

from ui.turn_routing import deliver_turn, impulse_turn_data


class FakePanel:
    """Ein Panel, das seine Turns nur sammelt."""

    def __init__(self, panel_id: str, *, reacts_to_impulse: bool, category="turn_reactive"):
        self.PANEL_ID = panel_id
        self.CATEGORY = category
        self.REACTS_TO_IMPULSE = reacts_to_impulse
        self.received: list[dict] = []

    def on_turn_received(self, turn_data: dict) -> None:
        self.received.append(turn_data)


class BrokenPanel(FakePanel):
    """Ein Panel, dessen Annahme scheitert."""

    def on_turn_received(self, turn_data: dict) -> None:
        raise ValueError("kaputt")


def _impulse_payload(**extra) -> dict:
    payload = {
        "typ": "character_response",
        "reiz_herkunft": "eigener_impuls",
        "nachricht": "Der Igel ist wieder da.",
        "nova_emotion": "Freude",
        "nova_arousal": 0.6,
    }
    payload.update(extra)
    return payload


class ImpulseTurnDataTest(unittest.TestCase):
    """Aus der Nutzlast eines Impulses werden die Turn-Daten einer Antwort."""

    def test_text_arrives_under_antwort_with_all_fields(self) -> None:
        data = _impulse_payload()
        turn_data = impulse_turn_data(data["nachricht"], data)
        self.assertEqual(turn_data["antwort"], "Der Igel ist wieder da.")
        self.assertEqual(turn_data["nova_emotion"], "Freude")
        self.assertEqual(turn_data["nova_arousal"], 0.6)

    def test_text_wins_over_a_field_named_antwort(self) -> None:
        data = _impulse_payload(antwort="anderer Text")
        turn_data = impulse_turn_data("Der Text", data)
        self.assertEqual(turn_data["antwort"], "Der Text")

    def test_the_payload_is_not_changed(self) -> None:
        data = _impulse_payload()
        impulse_turn_data(data["nachricht"], data)
        self.assertNotIn("antwort", data)

    def test_user_message_of_another_client_is_none(self) -> None:
        data = {"typ": "user_message", "nachricht": "Hallo"}
        self.assertIsNone(impulse_turn_data("Hallo", data))

    def test_user_message_is_none_even_with_impulse_origin(self) -> None:
        data = _impulse_payload(typ="user_message")
        self.assertIsNone(impulse_turn_data("Hallo", data))

    def test_other_events_without_impulse_origin_are_none(self) -> None:
        data = {"typ": "shadow_delivery", "nachricht": "Etwas"}
        self.assertIsNone(impulse_turn_data("Etwas", data))

    def test_non_text_is_rejected_loudly(self) -> None:
        with self.assertRaises(TypeError):
            impulse_turn_data(None, _impulse_payload())

    def test_non_mapping_is_rejected_loudly(self) -> None:
        with self.assertRaises(TypeError):
            impulse_turn_data("Text", ["kein", "Mapping"])


class DeliverTurnTest(unittest.TestCase):
    """Wer einen Impuls bekommt und wer eine gewöhnliche Antwort."""

    def setUp(self) -> None:
        self.avatar = FakePanel("avatar", reacts_to_impulse=True)
        self.goals = FakePanel("goals", reacts_to_impulse=False)
        self.panels = [self.avatar, self.goals]

    def test_impulse_reaches_the_avatar_with_text_and_fields(self) -> None:
        data = _impulse_payload()
        turn_data = impulse_turn_data(data["nachricht"], data)
        self.assertEqual(deliver_turn(self.panels, turn_data, impulse=True), 1)
        self.assertEqual(self.avatar.received, [turn_data])
        self.assertEqual(self.avatar.received[0]["antwort"], "Der Igel ist wieder da.")

    def test_impulse_does_not_reach_the_other_turn_reactive_panel(self) -> None:
        deliver_turn(self.panels, {"antwort": "x"}, impulse=True)
        self.assertEqual(self.goals.received, [])

    def test_ordinary_answer_reaches_both(self) -> None:
        turn_data = {"antwort": "Hallo", "nova_emotion": "Freude", "nova_arousal": 0.2}
        self.assertEqual(deliver_turn(self.panels, turn_data, impulse=False), 2)
        self.assertEqual(self.avatar.received, [turn_data])
        self.assertEqual(self.goals.received, [turn_data])

    def test_panel_of_another_category_gets_nothing_even_if_it_reacts_to_impulse(self) -> None:
        log_panel = FakePanel("log", reacts_to_impulse=True, category="log_stream")
        deliver_turn([log_panel], {"antwort": "x"}, impulse=True)
        deliver_turn([log_panel], {"antwort": "x"}, impulse=False)
        self.assertEqual(log_panel.received, [])

    def test_a_failing_panel_does_not_stop_the_others(self) -> None:
        broken = BrokenPanel("broken", reacts_to_impulse=True)
        with self.assertLogs("ui.turn_routing", level="ERROR") as logged:
            count = deliver_turn([broken, self.avatar], {"antwort": "x"}, impulse=True)
        self.assertEqual(count, 1)
        self.assertEqual(len(self.avatar.received), 1)
        self.assertIn("broken", logged.output[0])

    def test_non_dict_turn_data_is_rejected_loudly(self) -> None:
        with self.assertRaises(TypeError):
            deliver_turn(self.panels, "Text", impulse=True)


if __name__ == "__main__":
    unittest.main()
