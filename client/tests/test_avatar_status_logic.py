"""Zeugen der Lese-Sicht des Leerlaufs: `IdleLogic.status` und `puppet_status`.

Die Lese-Sicht ändert keine Planung: Zwei Logiken mit demselben Startwert und denselben
Ereignissen verhalten sich gleich, auch wenn eine davon in jedem Schritt fragt. Dazu die
Angabe je Zustand, die nächste Form, die gemerkte Spanne und die Puppe.
"""

import dataclasses
import math
import random
import unittest

from avatar.idle import (
    AnswerArrives,
    IdleFrame,
    IdleLogic,
    IdleTrace,
    Mood,
    PixieJob,
    TurnBegins,
)
from avatar.idle_catalog import FORMS, IdleState
from avatar.idle_status import (
    NOTE_AFTERGLOW,
    NOTE_INHALING,
    NOTE_PLAYBACK,
    NOTE_WAITING,
    SOURCE_NOVA,
    SOURCE_PIXIE,
    IdleStatus,
    StatusSpan,
)
from avatar.puppet import new_puppet, puppet_status, puppet_step
from tests.test_avatar_idle import REFERENCE, STEP_MS, _event, _playbacks, _sorted_inputs

CASES = (0, 10, 20)  # drei Läufe der Referenz mit Ereignissen und Zustandswechseln
ARRIVAL_MS = 1000.0
PLAYBACK_MS = 2000.0


def _logic_of_run(index: int, trace: IdleTrace | None = None) -> tuple[IdleLogic, int]:
    """Die Logik des Referenzlaufs `index` mit allen Ereignissen vorgemerkt, und seine Dauer."""
    run = REFERENCE["laeufe"][index]
    inputs = _sorted_inputs(run)
    playbacks = _playbacks(run, inputs)
    events = [_event(t, e, playbacks.get(i, 1000.0)) for i, (t, e) in enumerate(inputs)]
    running = 0
    while running < len(events) and isinstance(events[running], PixieJob) and (
            events[running].at_ms <= 0):
        running += 1
    nova = Mood(run["nova_beginn"]["emotion"], run["nova_beginn"]["arousal"])
    logic = IdleLogic(run["seed"], nova, events[:running], trace)
    for event in events[running:]:
        logic.post(event)
    return logic, run["sim_ms"]


def _run_frames(index: int, ask: bool) -> tuple[list[IdleFrame], IdleTrace, int]:
    """Alle Bilder des Laufs; mit `ask` fragt die Logik nach jedem Schritt `status`."""
    trace = IdleTrace()
    logic, sim_ms = _logic_of_run(index, trace)
    frames = []
    for t in range(STEP_MS, sim_ms + 1, STEP_MS):
        frames.append(logic.step(float(t), 0.0, 0.0))
        if ask:
            logic.status(float(t))
    return frames, trace, logic._rng.draws


def _answered(emotion: str = "freude", arousal: float = 0.6) -> IdleLogic:
    """Ein Turn bei 20 ms, eine Antwort bei 1 s mit zwei Sekunden Wiedergabe."""
    logic = IdleLogic(5)
    logic.post(TurnBegins(20.0))
    logic.post(AnswerArrives(ARRIVAL_MS, emotion, arousal, PLAYBACK_MS))
    return logic


def _status_at(logic: IdleLogic, t_ms: int) -> IdleStatus:
    """Schritte in 20-ms-Takt bis `t_ms`, dann der Status zu dieser Zeit."""
    if t_ms < STEP_MS or t_ms % STEP_MS:
        raise AssertionError(f"Zeit {t_ms} nicht im Takt")
    for t in range(STEP_MS, t_ms + 1, STEP_MS):
        logic.step(float(t), 0.0, 0.0)
    return logic.status(float(t_ms))


def _first_difference(left: list, right: list) -> str | None:
    """Meldet die erste Abweichung zweier langer Folgen, ohne sie ganz zu vergleichen.

    `assertEqual` auf Listen rechnet für die Meldung einen vollständigen, quadratischen Diff.

    Nachbedingung: Bei gleicher Länge und gleichem Inhalt None; bei ungleicher Länge die
    beiden Längen; sonst genau die erste Stelle mit der Zeit (wenn das Element eine
    `at_ms` trägt) und den abweichenden Feldern.
    """
    if len(left) != len(right):
        return f"Längen {len(left)} und {len(right)}"
    for index, (one, other) in enumerate(zip(left, right)):
        if one == other:
            continue
        where = f"Stelle {index}"
        if hasattr(one, "at_ms"):
            where += f", Zeit {one.at_ms} ms"
        if not dataclasses.is_dataclass(one):
            return f"{where}: {one!r} != {other!r}"
        fields = [
            f"{f.name}: {getattr(one, f.name)!r} != {getattr(other, f.name)!r}"
            for f in dataclasses.fields(one)
            if getattr(one, f.name) != getattr(other, f.name)
        ]
        return f"{where}: " + "; ".join(fields)
    return None


class FirstDifferenceTest(unittest.TestCase):
    """Die Hilfe meldet nichts bei Gleichheit und bei Abweichung genau die erste Stelle."""

    def test_equal_lists_report_nothing(self) -> None:
        self.assertIsNone(_first_difference([1, 2, 3], [1, 2, 3]))
        self.assertIsNone(_first_difference([], []))

    def test_the_first_difference_is_named_with_its_place(self) -> None:
        message = _first_difference([1, 2, 3, 4], [1, 2, 9, 8])
        self.assertEqual(message, "Stelle 2: 3 != 9")

    def test_a_record_names_its_time_and_the_differing_field(self) -> None:
        one = TurnBegins(20.0)
        other = AnswerArrives(20.0, "freude", 0.5, 1000.0)
        same = [one, one]
        self.assertEqual(
            _first_difference(same, [one, dataclasses.replace(one, at_ms=40.0)]),
            "Stelle 1, Zeit 20.0 ms: at_ms: 20.0 != 40.0",
        )
        self.assertIn("Stelle 0", _first_difference([one], [other]))

    def test_unequal_lengths_report_the_lengths(self) -> None:
        self.assertEqual(_first_difference([1, 2], [1, 2, 3]), "Längen 2 und 3")


class ReadOnlyTest(unittest.TestCase):
    """`status` ändert nichts: nicht die Ziele, nicht die Formen, nicht die Lidschläge."""

    def test_asking_does_not_change_the_plan(self) -> None:
        for index in CASES:
            with self.subTest(run=index):
                quiet, quiet_trace, quiet_draws = _run_frames(index, ask=False)
                asking, asking_trace, asking_draws = _run_frames(index, ask=True)
                self.assertIsNone(_first_difference(quiet, asking))
                self.assertIsNone(_first_difference(quiet_trace.forms, asking_trace.forms))
                self.assertIsNone(_first_difference(quiet_trace.blinks, asking_trace.blinks))
                self.assertEqual(quiet_draws, asking_draws)

    def test_asking_draws_no_random_number(self) -> None:
        logic = IdleLogic(3)
        logic.step(20.0, 0.0, 0.0)
        before = logic._rng.draws
        for _ in range(5):
            logic.status(20.0)
        self.assertEqual(logic._rng.draws, before)

    def test_the_run_of_the_reference_has_forms_to_compare(self) -> None:
        for index in CASES:
            with self.subTest(run=index):
                _, trace, draws = _run_frames(index, ask=False)
                self.assertGreater(len(trace.forms), 3)
                self.assertGreater(draws, 0)

    def test_time_before_the_last_step_is_refused(self) -> None:
        logic = IdleLogic(3)
        logic.step(100.0, 0.0, 0.0)
        with self.assertRaises(ValueError):
            logic.status(80.0)

    def test_time_not_finite_is_refused(self) -> None:
        logic = IdleLogic(3)
        for value in (math.nan, math.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                logic.status(value)


class StateNoteTest(unittest.TestCase):
    """In jedem der vier Zustände steht die richtige Angabe."""

    def test_noise_has_no_note_and_pixies_source(self) -> None:
        status = _status_at(IdleLogic(1), 20)
        self.assertIs(status.state, IdleState.NOISE)
        self.assertIsNone(status.note)
        self.assertIsNone(status.note_s)
        self.assertEqual(status.source, SOURCE_PIXIE)

    def test_noise_shows_the_fallback_of_pixie(self) -> None:
        job = PixieJob(0.0, "beginn", "llm", "research", "freude", 0.8)
        status = _status_at(IdleLogic(1, running_jobs=[job]), 20)
        self.assertEqual((status.source, status.sector_name), (SOURCE_PIXIE, "Freude"))
        self.assertAlmostEqual(status.arousal, 0.8)

    def test_thinking_waits_until_the_answer_arrives(self) -> None:
        logic = _answered()
        status = _status_at(logic, 600)
        self.assertIs(status.state, IdleState.THINKING)
        self.assertEqual(status.note, NOTE_WAITING)
        self.assertIsNone(status.note_s)
        self.assertEqual(status.source, SOURCE_NOVA)

    def test_thinking_inhales_when_the_answer_has_arrived(self) -> None:
        logic = _answered()
        _status_at(logic, 980)
        status = _status_at_next(logic, 1000)
        self.assertIs(status.state, IdleState.THINKING)
        self.assertEqual(status.note, NOTE_INHALING)
        self.assertTrue(0.7 <= status.note_s <= 0.9, status.note_s)

    def test_inhale_counts_down(self) -> None:
        logic = _answered()
        _status_at(logic, 1000)
        first = logic.status(1000.0)
        later = _status_at_next(logic, 1100)
        self.assertEqual(later.note, NOTE_INHALING)
        self.assertAlmostEqual(first.note_s - later.note_s, 0.1, places=6)

    def test_answer_names_the_playback_and_novas_emotion(self) -> None:
        logic = _answered()
        early = _status_at(logic, 3000)
        late = _status_at_next(logic, 3200)
        self.assertIs(early.state, IdleState.ANSWER)
        self.assertEqual(early.note, NOTE_PLAYBACK)
        self.assertEqual((early.source, early.sector_name), (SOURCE_NOVA, "Freude"))
        self.assertAlmostEqual(early.arousal, 0.6)
        self.assertAlmostEqual(early.note_s - late.note_s, 0.2, places=6)

    def test_afterglow_names_the_way_back_with_its_duration(self) -> None:
        logic = _answered()
        status = _status_at(logic, 4400)
        self.assertIs(status.state, IdleState.AFTERGLOW)
        self.assertEqual(status.note, NOTE_AFTERGLOW)
        self.assertIsNotNone(status.note_total_s)
        self.assertAlmostEqual(status.note_s + status.elapsed_s, status.note_total_s, places=6)
        self.assertEqual(status.source, SOURCE_NOVA)

    def test_the_state_carries_its_beginning(self) -> None:
        status = _status_at(_answered(), 600)
        self.assertEqual(status.since_ms, 20.0)
        self.assertAlmostEqual(status.elapsed_s, 0.58, places=6)


def _status_at_next(logic: IdleLogic, t_ms: int) -> IdleStatus:
    """Weiter im 20-ms-Takt von der letzten Zeit bis `t_ms`; dann der Status."""
    if t_ms % STEP_MS:
        raise AssertionError(f"Zeit {t_ms} nicht im Takt")
    start = int(logic._now) + STEP_MS
    for t in range(start, t_ms + 1, STEP_MS):
        logic.step(float(t), 0.0, 0.0)
    return logic.status(float(t_ms))


class NextFormTest(unittest.TestCase):
    """Die nächste Form ist die folgende des Plans; an der letzten steht neuer Zyklus."""

    def _walk(self, seconds: int) -> list[IdleStatus]:
        logic = IdleLogic(3)
        statuses = []
        for t in range(STEP_MS, seconds * 1000 + 1, STEP_MS):
            logic.step(float(t), 0.0, 0.0)
            statuses.append(logic.status(float(t)))
        return statuses

    def test_next_is_the_following_form_of_the_band(self) -> None:
        checked = 0
        for status in self._walk(60):
            if status.position + 1 < len(status.band):
                checked += 1
                self.assertIsNotNone(status.next_form)
                self.assertEqual(status.next_form.form_id,
                                 status.band[status.position + 1].form_id)
                self.assertGreaterEqual(status.next_form.in_s, 0.0)
                self.assertLessEqual(status.next_form.in_s, status.form.duration_s + 1e-6)
        self.assertGreater(checked, 100)

    def test_at_the_last_form_a_new_cycle_follows(self) -> None:
        last = [s for s in self._walk(60) if s.position == len(s.band) - 1]
        self.assertGreater(len(last), 0)
        self.assertTrue(all(s.next_form is None for s in last))

    def test_the_running_form_is_the_band_position_and_has_a_name(self) -> None:
        for status in self._walk(30):
            self.assertEqual(status.band[status.position].form_id, status.form.form_id)
            self.assertEqual(status.form.name, FORMS[status.form.form_id].name)
            self.assertTrue(0.0 <= status.form.elapsed_s <= status.form.duration_s + 1e-6)

    def test_every_form_of_the_band_has_a_duration(self) -> None:
        for status in self._walk(10):
            self.assertTrue(all(item.duration_s > 0 for item in status.band))


class SpanTest(unittest.TestCase):
    """Die Spanne ist die beim Planen gemerkte; eine Antwort hat keine."""

    def test_the_span_is_the_one_stored_at_planning(self) -> None:
        logic = IdleLogic(3)
        for t in range(STEP_MS, 40001, STEP_MS):
            logic.step(float(t), 0.0, 0.0)
            stored = logic._plan.span
            status = logic.status(float(t))
            self.assertIsNotNone(stored)
            self.assertEqual(status.span, StatusSpan(stored.xc, stored.lo, stored.hi, stored.count))
        self.assertIn(status.span.count, (4, 5))
        self.assertLessEqual(status.span.lo, status.span.hi)

    def test_an_answer_plan_has_no_span(self) -> None:
        status = _status_at(_answered(), 3000)
        self.assertIs(status.state, IdleState.ANSWER)
        self.assertEqual(status.plan_kind, "answer")
        self.assertIsNone(status.span)

    def test_a_cycle_plan_has_a_span(self) -> None:
        status = _status_at(IdleLogic(3), 20)
        self.assertEqual(status.plan_kind, "cycle")
        self.assertIsNotNone(status.span)


class StatusValueTest(unittest.TestCase):
    """Der Wert ist unveränderlich und weist Widersprüche ab."""

    def test_the_value_is_frozen(self) -> None:
        status = _status_at(IdleLogic(1), 20)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            status.position = 3  # type: ignore[misc]

    def test_a_position_outside_the_band_is_refused(self) -> None:
        status = _status_at(IdleLogic(1), 20)
        with self.assertRaises(ValueError):
            dataclasses.replace(status, position=len(status.band))

    def test_an_unknown_note_is_refused(self) -> None:
        status = _status_at(IdleLogic(1), 20)
        with self.assertRaises(ValueError):
            dataclasses.replace(status, note="unbekannt")


class PuppetStatusTest(unittest.TestCase):
    """Die Puppe gibt den Wert der Logik auf ihrer Uhr weiter, ohne etwas zu ändern."""

    def test_the_puppet_passes_the_status_on(self) -> None:
        puppet = new_puppet(10.0, random.Random(4))
        puppet_step(puppet, 10.5)
        self.assertEqual(puppet_status(puppet, 10.5), puppet.idle.status(500.0))

    def test_asking_does_not_change_the_puppet(self) -> None:
        asked = new_puppet(10.0, random.Random(4))
        quiet = new_puppet(10.0, random.Random(4))
        for i in range(1, 200):
            now = 10.0 + i * 0.25
            self.assertEqual(puppet_step(asked, now), puppet_step(quiet, now))
            puppet_status(asked, now)
        self.assertEqual(asked.idle._rng.draws, quiet.idle._rng.draws)

    def test_time_before_the_last_step_is_refused(self) -> None:
        puppet = new_puppet(10.0, random.Random(4))
        puppet_step(puppet, 10.5)
        with self.assertRaises(ValueError):
            puppet_status(puppet, 10.25)

    def test_no_puppet_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            puppet_status(object(), 1.0)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
