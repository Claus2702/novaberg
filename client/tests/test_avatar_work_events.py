"""Zeugen für die Arbeitszyklen auf ihrem Weg zum Avatar, soweit sie ohne Fenster prüfbar sind.

Drei Stücke: der Typ und seine Bildung aus der Nutzlast (`ui.work_events`), der Verteiler
(`ui.turn_routing`) und die Warteschlange des Panels (`ui.avatar_feed`). Keines importiert GTK.
Die Puppe der Warteschlange wird ersetzt, wo es um Reihenfolge und Zeit geht: Der Zeuge fragt,
was die Warteschlange ihr gibt, nicht, was die Puppe daraus macht.
"""

import random
import unittest
from unittest.mock import patch

from avatar.idle import ImpulseThinks, PixieJob, TurnBegins, TurnFailed
from avatar.puppet import Utterance, new_puppet
from ui import work_events
from ui.avatar_feed import AvatarFeed, idle_call
from ui.turn_routing import deliver_work_event
from ui.work_events import (
    ImpulseThinking,
    PixieWork,
    TurnFailure,
    TurnStarted,
    work_event_from_payload,
)


def _pixie_payload(**extra) -> dict:
    payload = {
        "typ": "pixie_auftrag",
        "phase": "beginn",
        "spur": "llm",
        "art": "recherche",
        "emotion": "Neugier",
        "arousal": 0.4,
        "thema": "Seidenraupen",
    }
    payload.update(extra)
    return payload


class WorkEventFromPayloadTest(unittest.TestCase):
    """Aus der Nutzlast wird das Ereignis; was nicht stimmt, ergibt eine Error-Zeile und None."""

    def test_valid_pixie_payload_gives_an_event_with_all_fields(self) -> None:
        event = work_event_from_payload(_pixie_payload())
        self.assertEqual(
            event,
            PixieWork("beginn", "llm", "recherche", "Neugier", 0.4, "Seidenraupen"),
        )

    def test_without_emotion_and_arousal_both_are_none(self) -> None:
        payload = _pixie_payload()
        del payload["emotion"]
        del payload["arousal"]
        event = work_event_from_payload(payload)
        self.assertIsNone(event.emotion)
        self.assertIsNone(event.arousal)

    def test_with_emotion_and_arousal_they_carry_their_values(self) -> None:
        event = work_event_from_payload(_pixie_payload(emotion="Freude", arousal=1))
        self.assertEqual(event.emotion, "Freude")
        self.assertEqual(event.arousal, 1.0)

    def test_topic_is_taken_over_and_none_when_missing(self) -> None:
        self.assertEqual(work_event_from_payload(_pixie_payload()).topic, "Seidenraupen")
        payload = _pixie_payload()
        del payload["thema"]
        self.assertIsNone(work_event_from_payload(payload).topic)

    def test_valid_impulse_and_failure_payloads_give_events(self) -> None:
        self.assertEqual(
            work_event_from_payload({"typ": "impuls_denkt", "phase": "ende"}),
            ImpulseThinking("ende"),
        )
        self.assertEqual(
            work_event_from_payload({"typ": "turn_gescheitert", "nachricht": "x"}),
            TurnFailure(),
        )

    def test_invalid_payloads_give_an_error_line_and_none(self) -> None:
        faelle = {
            "phase": _pixie_payload(phase="mitte"),
            "spur": _pixie_payload(spur="gpu"),
            "arousal zu hoch": _pixie_payload(arousal=1.5),
            "arousal negativ": _pixie_payload(arousal=-0.1),
            "arousal Text": _pixie_payload(arousal="0.4"),
            "arousal bool": _pixie_payload(arousal=True),
            "art fehlt": {k: v for k, v in _pixie_payload().items() if k != "art"},
            "art Zahl": _pixie_payload(art=7),
            "emotion Zahl": _pixie_payload(emotion=3),
            "thema Liste": _pixie_payload(thema=["x"]),
            "impuls ohne phase": {"typ": "impuls_denkt"},
            "impuls phase Zahl": {"typ": "impuls_denkt", "phase": 1},
        }
        for name, payload in faelle.items():
            with self.subTest(name), self.assertLogs("ui.work_events", level="ERROR"):
                self.assertIsNone(work_event_from_payload(payload))

    def test_unknown_type_gives_an_error_line_and_none(self) -> None:
        with self.assertLogs("ui.work_events", level="ERROR"):
            self.assertIsNone(work_event_from_payload({"typ": "shadow_delivery"}))

    def test_the_error_line_does_not_carry_the_topic(self) -> None:
        with self.assertLogs("ui.work_events", level="ERROR") as logged:
            work_event_from_payload(_pixie_payload(phase="mitte"))
        self.assertNotIn("Seidenraupen", "\n".join(logged.output))

    def test_the_error_line_does_not_carry_an_invalid_topic(self) -> None:
        for topic in (["Seidenraupen"], 5):
            with self.subTest(topic=topic), self.assertLogs(
                "ui.work_events", level="ERROR"
            ) as logged:
                self.assertIsNone(work_event_from_payload(_pixie_payload(thema=topic)))
            self.assertNotIn("Seidenraupen", "\n".join(logged.output))

    def test_non_mapping_is_rejected_loudly(self) -> None:
        with self.assertRaises(TypeError):
            work_event_from_payload(["kein", "Mapping"])

    def test_events_carry_no_time_and_are_immutable(self) -> None:
        event = work_event_from_payload(_pixie_payload())
        self.assertFalse(hasattr(event, "at_ms"))
        with self.assertRaises(AttributeError):
            event.phase = "ende"


class PayloadCheckersTest(unittest.TestCase):
    """Die Prüfer der Felder, einzeln: sie nennen das Feld; das Thema nennen sie nie."""

    def test_required_text_rejects_missing_empty_and_non_text(self) -> None:
        for data in ({}, {"k": ""}, {"k": 5}, {"k": None}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                work_events._required_text(data, "k")
        self.assertEqual(work_events._required_text({"k": "v"}, "k"), "v")

    def test_optional_text_is_none_when_missing_or_none(self) -> None:
        self.assertIsNone(work_events._optional_text({}, "k"))
        self.assertIsNone(work_events._optional_text({"k": None}, "k"))
        self.assertEqual(work_events._optional_text({"k": "v"}, "k"), "v")
        with self.assertRaises(ValueError):
            work_events._optional_text({"k": ""}, "k")

    def test_choice_accepts_only_the_allowed_values(self) -> None:
        self.assertEqual(work_events._choice({"k": "llm"}, "k", ("llm", "cpu")), "llm")
        with self.assertRaises(ValueError):
            work_events._choice({"k": "gpu"}, "k", ("llm", "cpu"))

    def test_optional_arousal_bounds(self) -> None:
        self.assertIsNone(work_events._optional_arousal({}))
        self.assertEqual(work_events._optional_arousal({"arousal": 0}), 0.0)
        self.assertEqual(work_events._optional_arousal({"arousal": 1}), 1.0)
        for value in (1.01, -0.01, float("nan"), "0.5", True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                work_events._optional_arousal({"arousal": value})

    def test_builders_make_their_event(self) -> None:
        self.assertEqual(work_events._failure_from({}), TurnFailure())
        self.assertEqual(work_events._impulse_from({"phase": "beginn"}), ImpulseThinking("beginn"))
        self.assertEqual(
            work_events._pixie_from(_pixie_payload()),
            PixieWork("beginn", "llm", "recherche", "Neugier", 0.4, "Seidenraupen"),
        )


class FakePanel:
    """Ein Panel, das seine Arbeitsereignisse nur sammelt."""

    def __init__(self, panel_id: str, *, reacts: bool, category: str = "turn_reactive") -> None:
        self.PANEL_ID = panel_id
        self.CATEGORY = category
        self.REACTS_TO_WORK = reacts
        self.received: list = []

    def on_work_event(self, event: object) -> None:
        self.received.append(event)


class BrokenPanel(FakePanel):
    """Ein Panel, dessen Annahme scheitert."""

    def on_work_event(self, event: object) -> None:
        raise ValueError("kaputt")


class DeliverWorkEventTest(unittest.TestCase):
    """Gewählt wird nach dem Merkmal allein."""

    def test_panel_with_the_trait_gets_the_event(self) -> None:
        panel = FakePanel("avatar", reacts=True)
        self.assertEqual(deliver_work_event([panel], TurnStarted()), 1)
        self.assertEqual(panel.received, [TurnStarted()])

    def test_turn_reactive_panel_without_the_trait_gets_nothing(self) -> None:
        panel = FakePanel("goals", reacts=False, category="turn_reactive")
        self.assertEqual(deliver_work_event([panel], TurnStarted()), 0)
        self.assertEqual(panel.received, [])

    def test_panel_with_the_trait_that_is_not_turn_reactive_gets_the_event(self) -> None:
        panel = FakePanel("status", reacts=True, category="log_stream")
        self.assertEqual(deliver_work_event([panel], TurnFailure()), 1)
        self.assertEqual(panel.received, [TurnFailure()])

    def test_a_failing_panel_does_not_stop_the_others(self) -> None:
        broken = BrokenPanel("broken", reacts=True)
        good = FakePanel("avatar", reacts=True)
        with self.assertLogs("ui.turn_routing", level="ERROR") as logged:
            count = deliver_work_event([broken, good], TurnStarted())
        self.assertEqual(count, 1)
        self.assertEqual(len(good.received), 1)
        self.assertIn("broken", logged.output[0])

    def test_a_dict_is_rejected_loudly(self) -> None:
        with self.assertRaises(TypeError):
            deliver_work_event([FakePanel("avatar", reacts=True)], {"typ": "impuls_denkt"})


class IdleCallTest(unittest.TestCase):
    """Jedes Ereignis wird der Typ des Leerlaufs mit seinen Feldern — ohne das Thema."""

    def test_each_event_maps_to_its_idle_type(self) -> None:
        self.assertEqual(idle_call(TurnStarted()), (TurnBegins, {}))
        self.assertEqual(idle_call(TurnFailure()), (TurnFailed, {}))
        self.assertEqual(idle_call(ImpulseThinking("ende")), (ImpulseThinks, {"phase": "ende"}))

    def test_pixie_job_carries_its_fields_but_no_topic(self) -> None:
        event_type, fields = idle_call(work_event_from_payload(_pixie_payload()))
        self.assertIs(event_type, PixieJob)
        self.assertEqual(
            fields,
            {
                "phase": "beginn",
                "track": "llm",
                "job_kind": "recherche",
                "emotion": "Neugier",
                "arousal": 0.4,
            },
        )
        self.assertNotIn("topic", fields)
        self.assertNotIn("Seidenraupen", fields.values())

    def test_a_non_event_is_rejected_loudly(self) -> None:
        with self.assertRaises(TypeError):
            idle_call({"typ": "pixie_auftrag"})


class AvatarFeedTest(unittest.TestCase):
    """Antworten und Ereignisse erreichen die Puppe in der Reihenfolge des Eintreffens."""

    def setUp(self) -> None:
        self.puppet = new_puppet(0.0, random.Random(1))
        self.calls: list[tuple] = []
        cue = patch(
            "ui.avatar_feed.puppet_cue",
            side_effect=lambda puppet, utterance, now: self.calls.append(("cue", utterance, now)),
        )
        event = patch(
            "ui.avatar_feed.puppet_event",
            side_effect=lambda puppet, kind, now, **data: self.calls.append(
                ("event", kind, now, data)
            ),
        )
        for patcher in (cue, event):
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_two_events_between_two_frames_arrive_in_order_with_the_time_of_the_next_frame(
        self,
    ) -> None:
        feed = AvatarFeed()
        feed.add(TurnStarted())
        feed.add(ImpulseThinking("beginn"))
        self.assertEqual(feed.deliver(self.puppet, 2.5), 2)
        self.assertEqual(
            self.calls,
            [("event", TurnBegins, 2.5, {}), ("event", ImpulseThinks, 2.5, {"phase": "beginn"})],
        )

    def test_an_answer_between_two_events_keeps_its_place(self) -> None:
        feed = AvatarFeed()
        answer = Utterance(3, 0.5, "Hallo")
        feed.add(TurnStarted())
        feed.add(answer)
        feed.add(ImpulseThinking("ende"))
        feed.deliver(self.puppet, 1.0)
        self.assertEqual(
            self.calls,
            [
                ("event", TurnBegins, 1.0, {}),
                ("cue", answer, 1.0),
                ("event", ImpulseThinks, 1.0, {"phase": "ende"}),
            ],
        )

    def test_pixie_job_reaches_the_puppet_without_the_topic(self) -> None:
        feed = AvatarFeed()
        feed.add(work_event_from_payload(_pixie_payload()))
        feed.deliver(self.puppet, 1.0)
        _, kind, _, data = self.calls[0]
        self.assertIs(kind, PixieJob)
        self.assertNotIn("topic", data)
        self.assertEqual(data["job_kind"], "recherche")

    def test_without_a_following_frame_nothing_reaches_the_puppet(self) -> None:
        feed = AvatarFeed()
        feed.add(TurnStarted())
        feed.add(Utterance(None, 0.0, "x"))
        self.assertEqual(self.calls, [])
        self.assertEqual(len(feed), 2)

    def test_delivery_empties_the_queue_and_a_second_frame_gives_nothing(self) -> None:
        feed = AvatarFeed()
        feed.add(TurnStarted())
        feed.deliver(self.puppet, 1.0)
        self.assertEqual(len(feed), 0)
        self.assertEqual(feed.deliver(self.puppet, 1.1), 0)
        self.assertEqual(len(self.calls), 1)

    def test_nothing_waiting_gives_zero(self) -> None:
        self.assertEqual(AvatarFeed().deliver(self.puppet, 1.0), 0)

    def test_foreign_items_and_foreign_puppets_are_rejected_loudly(self) -> None:
        feed = AvatarFeed()
        with self.assertRaises(TypeError):
            feed.add({"typ": "pixie_auftrag"})
        with self.assertRaises(TypeError):
            feed.deliver(object(), 1.0)
        self.assertEqual(len(feed), 0)


if __name__ == "__main__":
    unittest.main()
