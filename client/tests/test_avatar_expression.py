"""Zeugen für den Ausdruck des Avatars: das Ziel aus Sektor und Arousal.

Die Referenzwerte unter `avatar_reference/expression.json` sind aus dem Prototyp
erzeugt (9 Sektoren × 5 Arousal-Stufen × 35 Kanäle) und werden nicht von Hand
geändert. Eine Abweichung davon wäre im Bild still — das Gesicht sähe nur ein
wenig anders aus.

Toleranz 1e-9 in den Einheiten der Kanäle (Pixel, Faktor, 0..1): Python und der
Prototyp rechnen dieselben Operationen in derselben Reihenfolge mit IEEE-754-
Doppelgenauigkeit, die Abweichung liegt also bei null oder bei wenigen Einheiten
der letzten Stelle (bei Werten bis 110 rund 1e-14). Die kleinste fachliche
Abweichung — eine verschobene Stützstelle, ein vertauschter Kanal — liegt bei
1e-2 und mehr, sieben Größenordnungen darüber.
"""

import json
import unittest
from dataclasses import fields
from pathlib import Path

from avatar import expression
from avatar.expression import face_target
from avatar.face import NEUTRAL, PROTOTYPE_KEYS, FaceState

TOLERANCE = 1e-9
REFERENCE_PATH = Path(__file__).parent / "avatar_reference" / "expression.json"


def _load_reference() -> dict:
    """Die Referenzwerte des Prototyps."""
    with REFERENCE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _deviation(face: FaceState) -> float:
    """Summe der Beträge der Abweichung von Neutral über alle Kanäle."""
    return sum(abs(getattr(face, f.name) - getattr(NEUTRAL, f.name)) for f in fields(FaceState))


class ReferenceTest(unittest.TestCase):
    """Gleichheit mit dem Prototyp, je Kanal."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.reference = _load_reference()

    def test_channels_and_neutral_match_the_prototype(self) -> None:
        self.assertEqual(list(PROTOTYPE_KEYS), [f.name for f in fields(FaceState)])
        self.assertEqual(list(PROTOTYPE_KEYS.values()), self.reference["kanaele"])
        self.assertEqual(len(self.reference["kanaele"]), 35)
        for field, key in PROTOTYPE_KEYS.items():
            self.assertEqual(getattr(NEUTRAL, field), self.reference["neutral"][key], key)

    def test_mod_arousal_matches_the_prototype(self) -> None:
        self.assertEqual(expression.MOD_AROUSAL, self.reference["mod_arousal"])

    def test_all_45_reference_targets_match_per_channel(self) -> None:
        entries = self.reference["werte"]
        self.assertEqual(len(entries), 45)
        for entry in entries:
            with self.subTest(sector=entry["sektor"], arousal=entry["arousal"]):
                face = face_target(entry["sektor"], entry["arousal"])
                for field, key in PROTOTYPE_KEYS.items():
                    self.assertAlmostEqual(
                        getattr(face, field), entry["face"][key], delta=TOLERANCE, msg=key
                    )


class ShapeTest(unittest.TestCase):
    """Die Zusagen aus der Testbarkeit des Konzepts, unabhängig von den Referenzwerten."""

    def test_arousal_zero_is_neutral_for_all_eight_sectors(self) -> None:
        for sector in range(1, 9):
            with self.subTest(sector=sector):
                self.assertEqual(face_target(sector, 0.0), NEUTRAL)

    def test_twin_arousal_above_zero_leaves_neutral_for_all_eight_sectors(self) -> None:
        for sector in range(1, 9):
            with self.subTest(sector=sector):
                self.assertNotEqual(face_target(sector, 0.3), NEUTRAL)

    def test_moderate_is_weaker_than_intense(self) -> None:
        # Gemessen wird die Summe der Abweichungen, nicht je Kanal: Bei Ärger presst
        # der moderate Mund die Lippen (au23 0,6), der intensive schreit (au23 0).
        for sector in range(1, 9):
            deviations = [_deviation(face_target(sector, a)) for a in (0.3, 0.6, 0.85, 1.0)]
            with self.subTest(sector=sector, deviations=deviations):
                self.assertEqual(deviations, sorted(deviations))
                self.assertEqual(len(set(deviations)), 4)

    def test_neutral_sector_stays_neutral_at_every_arousal(self) -> None:
        for arousal in (0.0, 0.3, 0.6, 0.85, 1.0):
            with self.subTest(arousal=arousal):
                self.assertEqual(face_target(0, arousal), NEUTRAL)

    def test_targets_stay_within_the_reference_hull(self) -> None:
        values = [entry["face"] for entry in _load_reference()["werte"]]
        bounds = {
            field: (
                min(v[key] for v in values) - TOLERANCE,
                max(v[key] for v in values) + TOLERANCE,
            )
            for field, key in PROTOTYPE_KEYS.items()
        }
        for sector in range(9):
            for step in range(21):
                face = face_target(sector, step / 20)
                outside = [
                    field for field, (low, high) in bounds.items()
                    if not low <= getattr(face, field) <= high
                ]
                with self.subTest(sector=sector, arousal=step / 20):
                    self.assertEqual(outside, [])


class RejectionTest(unittest.TestCase):
    """Was nicht passt, ergibt eine Error-Zeile und Neutral — je mit Zwilling."""

    def test_unknown_sector_logs_error_and_returns_neutral(self) -> None:
        for sector in (-1, 9, True, None, "1", 1.0):
            with self.subTest(sector=sector), self.assertLogs("avatar.expression", "ERROR") as log:
                self.assertIs(face_target(sector, 1.0), NEUTRAL)
            self.assertIn("Sektor", log.output[0])

    def test_twin_border_sectors_are_accepted_without_log(self) -> None:
        for sector in (0, 8):
            with self.subTest(sector=sector), self.assertNoLogs("avatar.expression"):
                face_target(sector, 1.0)
        self.assertNotEqual(face_target(8, 1.0), NEUTRAL)

    def test_non_finite_arousal_logs_error_and_returns_neutral(self) -> None:
        for arousal in (float("nan"), float("inf"), None, "0.5", False):
            with self.subTest(arousal=arousal), self.assertLogs("avatar.expression", "ERROR"):
                self.assertIs(face_target(1, arousal), NEUTRAL)

    def test_twin_integer_arousal_is_accepted_without_log(self) -> None:
        with self.assertNoLogs("avatar.expression"):
            self.assertEqual(face_target(1, 1), face_target(1, 1.0))

    def test_arousal_outside_range_is_clamped_with_warning(self) -> None:
        with self.assertLogs("avatar.expression", "WARNING"):
            self.assertEqual(face_target(1, 1.5), face_target(1, 1.0))
        with self.assertLogs("avatar.expression", "WARNING"):
            self.assertEqual(face_target(1, -0.2), NEUTRAL)

    def test_twin_arousal_at_the_edges_is_not_clamped(self) -> None:
        with self.assertNoLogs("avatar.expression"):
            face_target(1, 1.0)
            face_target(1, 0.0)


if __name__ == "__main__":
    unittest.main()
