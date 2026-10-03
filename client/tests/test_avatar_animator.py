"""Zeugen für den Animator des Avatars: Feder je Kanal und Mundversatz.

Die Zeit treiben die Zeugen künstlich; das Modul liest keine Uhr. Erwartete Werte
kommen aus der geschlossenen Lösung der kritisch gedämpften Feder aus der Ruhe,
`x(t) = ziel + (x0 - ziel) * (1 + omega * t) * exp(-omega * t)` — nicht aus dem
Schrittverfahren, das geprüft wird.

Toleranz 1e-9 in den Einheiten der Kanäle: Der Schritt ist exakt, die Abweichung
zwischen Zerlegungen und gegenüber der geschlossenen Form ist Rundung (bei Werten
bis 110 um 1e-13). Ein Schrittverfahren erster Ordnung läge bei 0,1 s je Schritt
um Pixel daneben.
"""

import json
import math
import random
import unittest
from dataclasses import fields, replace
from pathlib import Path

from avatar import animator
from avatar.animator import MOUTH_CHANNELS, advance, set_target, spring_step, start
from avatar.expression import face_target
from avatar.face import NEUTRAL, PROTOTYPE_KEYS, FaceState

TOLERANCE = 1e-9
CHANNELS = [f.name for f in fields(FaceState)]
REFERENCE_PATH = Path(__file__).parent / "avatar_reference" / "expression.json"

# Die Mundkanäle des Prototyps unter ihren Kurznamen.
PROTOTYPE_MOUTH = {
    "mc", "mo", "jaw", "mw", "ma",
    "au10L", "au10R", "au12L", "au12R", "au15L", "au15R", "au16L", "au16R", "au20L", "au20R",
    "au17", "au18", "au22", "au23", "au24", "au28",
}

JOY = face_target(1, 1.0)
ANGER = face_target(7, 1.0)


def _from_rest(start_value: float, goal: float, omega: float, elapsed: float) -> float:
    """Geschlossene Lösung der kritisch gedämpften Feder aus der Ruhe."""
    return goal + (start_value - goal) * (1 + omega * elapsed) * math.exp(-omega * elapsed)


def _run(times: list[float], changes: dict[float, FaceState]) -> animator.AnimatorState:
    """Startet in Neutral bei 0 s, setzt die Ziele zu ihren Zeiten und schreitet über `times`."""
    state = start(NEUTRAL, 0.0)
    for time_s in times:
        if time_s in changes:
            state = set_target(state, changes[time_s], time_s)
        else:
            state = advance(state, time_s)
    return state


def _max_difference(first: FaceState, second: FaceState) -> float:
    """Größter Betrag der Differenz über alle Kanäle."""
    return max(abs(getattr(first, name) - getattr(second, name)) for name in CHANNELS)


class SpringTest(unittest.TestCase):
    """Die Feder: geschlossene Lösung, Bildrate, Unterbrechung."""

    def test_follows_the_closed_form_from_rest(self) -> None:
        self.assertEqual((JOY.brow_left_inner, JOY.mouth_open), (-6.0, 32.0))
        state = _run([0.0, *[i / 10 for i in range(1, 11)]], {0.0: JOY})
        self.assertAlmostEqual(
            state.current.brow_left_inner, _from_rest(0.0, -6.0, 5.0, 1.0), delta=TOLERANCE
        )
        # Der Mund startet 150 ms später.
        self.assertAlmostEqual(
            state.current.mouth_open, _from_rest(0.0, 32.0, 5.0, 0.85), delta=TOLERANCE
        )

    def test_one_second_in_10_and_in_60_steps_ends_in_the_same_state(self) -> None:
        coarse = _run([0.0, *[i / 10 for i in range(1, 11)]], {0.0: JOY})
        fine = _run([0.0, *[i / 60 for i in range(1, 61)]], {0.0: JOY})
        self.assertLess(_max_difference(coarse.current, fine.current), TOLERANCE)
        self.assertLess(_max_difference(coarse.velocity, fine.velocity), TOLERANCE)
        # Zwilling: Der Endzustand ist nicht der Start — die Zusicherung ist nicht leer.
        self.assertGreater(_max_difference(coarse.current, NEUTRAL), 20.0)

    def test_interruption_keeps_position_and_velocity(self) -> None:
        before = _run([0.0, 0.1, 0.2, 0.3], {0.0: JOY})
        interrupted = set_target(before, ANGER, 0.3)
        self.assertEqual(interrupted.current, before.current)
        self.assertEqual(interrupted.velocity, before.velocity)
        self.assertGreater(abs(before.velocity.brow_left_inner), 1.0)

    def test_interruption_bends_the_path_without_a_kink(self) -> None:
        # Nach 0,1 ms unterscheiden sich der unterbrochene und der ungestörte Verlauf
        # nur um die halbe Beschleunigungsdifferenz mal dt² — ein Sprung in Position
        # oder Geschwindigkeit läge um Größenordnungen darüber.
        before = _run([0.0, 0.1, 0.2, 0.3], {0.0: JOY})
        dt, omega = 1e-4, 5.0
        straight = advance(before, 0.3 + dt)
        bent = advance(set_target(before, ANGER, 0.3), 0.3 + dt)
        for name in CHANNELS:
            if name in MOUTH_CHANNELS:
                continue
            jump = abs(getattr(ANGER, name) - getattr(JOY, name))
            with self.subTest(channel=name):
                self.assertLessEqual(
                    abs(getattr(bent.current, name) - getattr(straight.current, name)),
                    omega**2 * jump * dt**2 + TOLERANCE,
                )
                self.assertLessEqual(
                    abs(getattr(bent.velocity, name) - getattr(straight.velocity, name)),
                    2 * omega**2 * jump * dt + TOLERANCE,
                )
        self.assertNotEqual(bent.current.brow_left_inner, straight.current.brow_left_inner)

    def test_larger_omega_moves_faster(self) -> None:
        slow = advance(set_target(start(NEUTRAL, 0.0), JOY, 0.0), 0.5)
        fast = advance(set_target(start(NEUTRAL, 0.0), JOY, 0.0, omega=10.0), 0.5, omega=10.0)
        self.assertAlmostEqual(
            fast.current.brow_left_inner, _from_rest(0.0, -6.0, 10.0, 0.5), delta=TOLERANCE
        )
        self.assertLess(fast.current.brow_left_inner, slow.current.brow_left_inner)

    def test_same_inputs_give_the_same_state(self) -> None:
        times = [0.0, 0.05, 0.3, 0.31, 0.7]
        self.assertEqual(_run(times, {0.0: JOY, 0.3: ANGER}), _run(times, {0.0: JOY, 0.3: ANGER}))

    def test_step_of_zero_changes_nothing(self) -> None:
        state = _run([0.0, 0.2], {0.0: JOY})
        current, velocity = spring_step(state.current, state.velocity, state.target, 5.0, 0.0)
        self.assertLess(_max_difference(current, state.current), TOLERANCE)
        self.assertLess(_max_difference(velocity, state.velocity), TOLERANCE)


class MouthDelayTest(unittest.TestCase):
    """Der Mund übernimmt ein neues Ziel 150 ms später, je Zielwechsel."""

    def test_mouth_channels_are_those_of_the_prototype(self) -> None:
        self.assertEqual({PROTOTYPE_KEYS[name] for name in MOUTH_CHANNELS}, PROTOTYPE_MOUTH)

    def test_no_mouth_channel_moves_before_150_ms(self) -> None:
        state = advance(set_target(start(NEUTRAL, 10.0), JOY, 10.0), 10.149)
        for name in MOUTH_CHANNELS:
            with self.subTest(channel=name):
                self.assertEqual(getattr(state.current, name), getattr(NEUTRAL, name))
        # Zwilling: Brauen und Augen laufen in derselben Zeit schon.
        self.assertLess(state.current.brow_left_inner, -0.1)

    def test_mouth_channels_move_after_150_ms(self) -> None:
        state = advance(set_target(start(NEUTRAL, 10.0), JOY, 10.0), 10.151)
        for name in MOUTH_CHANNELS:
            if getattr(JOY, name) == getattr(NEUTRAL, name):
                continue
            with self.subTest(channel=name):
                self.assertNotEqual(getattr(state.current, name), getattr(NEUTRAL, name))

    def test_target_of_brows_changes_at_once_and_of_mouth_later(self) -> None:
        state = set_target(start(NEUTRAL, 0.0), JOY, 0.0)
        for name in CHANNELS:
            expected = getattr(NEUTRAL if name in MOUTH_CHANNELS else JOY, name)
            with self.subTest(channel=name):
                self.assertEqual(getattr(state.target, name), expected)
        self.assertEqual(advance(state, 0.15).target, JOY)

    def test_mouth_follows_changes_faster_than_the_delay(self) -> None:
        # Alle 100 ms ein neuer Wechsel: Der Mund übernimmt jeden 150 ms später,
        # statt auf das Ende der Wechsel zu warten.
        changes = {i / 10: JOY if i % 2 == 0 else ANGER for i in range(10)}
        state = _run([*changes, 1.0], changes)
        self.assertEqual(state.target.mouth_open, JOY.mouth_open)
        self.assertGreater(state.current.mouth_open, 1.0)

    def test_split_at_the_due_time_is_independent_of_frames(self) -> None:
        # Fällig bei 0,15 s: einmal über die Spanne 0,1–0,2 s, einmal genau dort geteilt.
        coarse = _run([0.0, 0.1, 0.2], {0.0: JOY})
        fine = _run([0.0, 0.1, 0.15, 0.2], {0.0: JOY})
        self.assertLess(_max_difference(coarse.current, fine.current), TOLERANCE)
        self.assertAlmostEqual(
            coarse.current.mouth_open, _from_rest(0.0, 32.0, 5.0, 0.05), delta=TOLERANCE
        )


class ChannelBoundsTest(unittest.TestCase):
    """Beliebige Verläufe bleiben in den Grenzen der Schlüsselbilder."""

    def test_random_sequences_stay_within_the_reference_hull(self) -> None:
        with REFERENCE_PATH.open(encoding="utf-8") as handle:
            values = [entry["face"] for entry in json.load(handle)["werte"]]
        bounds = {
            field: (
                min(v[key] for v in values) - TOLERANCE,
                max(v[key] for v in values) + TOLERANCE,
            )
            for field, key in PROTOTYPE_KEYS.items()
        }
        # Fester Seed: ein Verlauf, der jedes Mal derselbe ist, kein Zufall im Zeugen.
        rng = random.Random(20261003)  # noqa: S311 — keine Kryptografie
        state, time_s, next_change = start(NEUTRAL, 0.0), 0.0, 0.0
        for frame in range(3000):
            time_s += rng.uniform(1 / 120, 1 / 20)
            if time_s >= next_change:
                target = face_target(rng.randrange(9), rng.random())
                state = set_target(state, target, time_s)
                next_change = time_s + rng.uniform(0.02, 0.4)
            else:
                state = advance(state, time_s)
            outside = [
                name for name, (low, high) in bounds.items()
                if not low <= getattr(state.current, name) <= high
            ]
            if outside:
                self.fail(f"Bild {frame} bei {time_s:.3f} s außerhalb der Grenzen: {outside}")


class RejectionTest(unittest.TestCase):
    """Falsche Eingaben werfen laut — je mit Zwilling."""

    def test_time_running_backwards_is_rejected(self) -> None:
        state = advance(start(NEUTRAL, 1.0), 2.0)
        with self.assertRaises(ValueError):
            advance(state, 1.999)
        with self.assertRaises(ValueError):
            set_target(state, JOY, 1.999)

    def test_twin_same_time_is_accepted(self) -> None:
        state = advance(set_target(start(NEUTRAL, 1.0), JOY, 1.0), 2.0)
        self.assertEqual(advance(state, 2.0), state)

    def test_non_finite_time_is_rejected(self) -> None:
        for time_s in (float("nan"), float("inf"), None, True):
            with self.subTest(time_s=time_s), self.assertRaises(ValueError):
                advance(start(NEUTRAL, 0.0), time_s)

    def test_omega_not_positive_is_rejected(self) -> None:
        for omega in (0.0, -5.0, float("nan")):
            with self.subTest(omega=omega), self.assertRaises(ValueError):
                advance(start(NEUTRAL, 0.0), 1.0, omega=omega)

    def test_twin_small_positive_omega_is_accepted(self) -> None:
        state = advance(set_target(start(NEUTRAL, 0.0), JOY, 0.0, omega=0.1), 1.0, omega=0.1)
        self.assertAlmostEqual(
            state.current.brow_left_inner, _from_rest(0.0, -6.0, 0.1, 1.0), delta=TOLERANCE
        )

    def test_target_that_is_no_face_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            set_target(start(NEUTRAL, 0.0), {"mo": 1.0}, 0.0)
        with self.assertRaises(ValueError):
            set_target(start(NEUTRAL, 0.0), replace(JOY, jaw=float("nan")), 0.0)

    def test_twin_face_target_is_accepted(self) -> None:
        self.assertEqual(set_target(start(NEUTRAL, 0.0), JOY, 0.0).pending[0].target, JOY)


if __name__ == "__main__":
    unittest.main()
