"""Zeugen für das Zeichnen von Brauen, Augen, Falten und Extras.

Gezeichnet wird auf `RecordingContext`, der jeden Aufruf mit seinen Argumenten
mitschreibt — so wie ein Cairo-Kontext ihn empfinge. Kein Zeuge braucht pycairo,
GTK oder einen Bildschirm.

Die Zahlen an den Stichstellen sind aus den Formeln des Prototyps von Hand
gerechnet; die Rechnung steht jeweils daneben. Die Neigung der Gesichtsachse ist
9°: sin 9° = 0,15643446504023087, cos 9° = 0,9876883405951378. Ein Punkt in
Gesichtsachsen ist L(c, lx, ly) = (cx + lx·cos − ly·sin, cy + lx·sin + ly·cos).
"""

import importlib
import json
import math
import sys
import types
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

import avatar
from avatar import drawing
from avatar.drawing import (
    BROW_LEFT,
    brow_points,
    draw_brow_wrinkles,
    draw_brows,
    draw_extras,
    draw_eyes,
)
from avatar.drawing_eye import EYE_LEFT, closed_lid, lid_extent, pupil_radius
from avatar.drawing_tools import (
    PART_BROW_LEFT,
    PART_EYE_RIGHT,
    PARTS,
    SRC,
    ParkMiller,
    js_round,
    park_miller_next,
    part_seed,
)
from avatar.face import NEUTRAL, PROTOTYPE_KEYS, FaceState

REFERENCE_PATH = Path(__file__).parent / "avatar_reference" / "expression.json"
DRAWING_MODULES = ("avatar.drawing", "avatar.drawing_eye", "avatar.drawing_tools")
POINT_CALLS = ("move_to", "line_to", "curve_to", "translate")
EXACT = 1e-9
SHAKE_FINE = 0.1  # fine verwackelt um höchstens ±0,4 · 0,5 / 2
PART_NAMES = ("Brauen", "Augen", "Extras")


class RecordingContext:
    """Ein Ersatz für `cairo.Context`, der jeden Aufruf als (Name, Argumente) mitschreibt."""

    def __init__(self) -> None:
        """Beginnt mit leerer Aufrufliste."""
        self.calls: list[tuple[str, tuple]] = []

    def _record(self, name: str, *args: object) -> None:
        self.calls.append((name, args))

    def new_path(self) -> None:
        self._record("new_path")

    def move_to(self, x: float, y: float) -> None:
        self._record("move_to", x, y)

    def line_to(self, x: float, y: float) -> None:
        self._record("line_to", x, y)

    def curve_to(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> None:
        self._record("curve_to", x1, y1, x2, y2, x3, y3)

    def close_path(self) -> None:
        self._record("close_path")

    def arc(self, xc: float, yc: float, radius: float, angle1: float, angle2: float) -> None:
        self._record("arc", xc, yc, radius, angle1, angle2)

    def rectangle(self, x: float, y: float, width: float, height: float) -> None:
        self._record("rectangle", x, y, width, height)

    def stroke(self) -> None:
        self._record("stroke")

    def fill(self) -> None:
        self._record("fill")

    def fill_preserve(self) -> None:
        self._record("fill_preserve")

    def clip(self) -> None:
        self._record("clip")

    def save(self) -> None:
        self._record("save")

    def restore(self) -> None:
        self._record("restore")

    def translate(self, tx: float, ty: float) -> None:
        self._record("translate", tx, ty)

    def rotate(self, angle: float) -> None:
        self._record("rotate", angle)

    def scale(self, sx: float, sy: float) -> None:
        self._record("scale", sx, sy)

    def set_line_width(self, width: float) -> None:
        self._record("set_line_width", width)

    def set_source_rgba(self, red: float, green: float, blue: float, alpha: float) -> None:
        self._record("set_source_rgba", red, green, blue, alpha)

    def set_source(self, pattern: object) -> None:
        self._record("set_source", pattern)

    def names(self) -> list[str]:
        return [name for name, _ in self.calls]


class RecordingGradients:
    """Ein Ersatz für `CairoGradients`: gibt den Verlauf als Tupel zurück."""

    def radial(self, inner: tuple, outer: tuple, stops: tuple) -> tuple:
        return ("radial", inner, outer, tuple(stops))

    def linear(self, start: tuple, end: tuple, stops: tuple) -> tuple:
        return ("linear", start, end, tuple(stops))


def _face(**changes: float) -> FaceState:
    """Neutral mit den genannten Kanälen."""
    return replace(NEUTRAL, **changes)


def _eyes(face: FaceState, blink: float, tick: int = 3) -> RecordingContext:
    cr = RecordingContext()
    draw_eyes(cr, RecordingGradients(), face, blink, tick)
    return cr


def _arcs(cr: RecordingContext) -> list[tuple]:
    return [args for name, args in cr.calls if name == "arc"]


def _violations(calls: list[tuple[str, tuple]]) -> list[tuple[str, tuple]]:
    """Aufrufe mit nicht endlicher Zahl oder mit einer Koordinate außerhalb 0..SRC."""

    def inside(*values: float) -> bool:
        return all(0.0 <= v <= SRC for v in values)

    bad = []
    for name, args in calls:
        numbers = [a for a in args if isinstance(a, int | float)]
        if not all(math.isfinite(v) for v in numbers):
            bad.append((name, args))
        elif name in POINT_CALLS and not inside(*args):
            bad.append((name, args))
        elif name == "arc" and not (inside(args[0], args[1]) and args[2] >= 0):
            bad.append((name, args))
        elif name == "rectangle":
            x, y, w, h = args
            if not inside(x, y, x + w, y + h):
                bad.append((name, args))
        elif name == "set_source_rgba" and not all(0.0 <= v <= 1.0 for v in args):
            bad.append((name, args))
        elif name == "set_line_width" and args[0] < 0:
            bad.append((name, args))
    return bad


class DeterminismTest(unittest.TestCase):
    """Gleiche Kanäle, gleicher Blinzelwert, gleicher Takt → gleiche Aufrufliste."""

    face = _face(
        brow_left_inner=14.0,
        brow_right_inner=14.0,
        blush=0.5,
        tear=0.6,
        sweat=0.6,
        pupil_size=0.9,
    )

    def _record(self, tick: int) -> list[list]:
        brows, eyes, extras = RecordingContext(), RecordingContext(), RecordingContext()
        draw_brows(brows, self.face, tick)
        draw_eyes(eyes, RecordingGradients(), self.face, 0.5, tick)
        draw_extras(extras, self.face, 900.0, tick)
        return [brows.calls, eyes.calls, extras.calls]

    def test_same_input_draws_the_same_calls(self) -> None:
        first, second = self._record(41), self._record(41)
        for part, a, b in zip(PART_NAMES, first, second, strict=True):
            with self.subTest(part=part):
                self.assertGreater(len(a), 0)
                self.assertEqual(a, b)

    def test_another_tick_draws_other_strokes(self) -> None:
        first, other = self._record(41), self._record(42)
        for part, a, b in zip(PART_NAMES, first, other, strict=True):
            with self.subTest(part=part):
                # dieselbe Form, also dieselbe Folge von Aufrufen — nur die Lage zittert
                self.assertEqual([n for n, _ in a], [n for n, _ in b])
                self.assertNotEqual(a, b)


class PartSeedTest(unittest.TestCase):
    """Ein Seed je Teil, abgeleitet aus dem Boil-Takt."""

    def test_part_zero_is_the_prototype_formula(self) -> None:
        # Im Prototyp ist der Seed der Takt modulo 9973 plus 17
        self.assertEqual(part_seed(0, PART_BROW_LEFT), 17)
        self.assertEqual(part_seed(250, PART_BROW_LEFT), 267)
        self.assertEqual(part_seed(9973, PART_BROW_LEFT), 17)

    def test_each_part_has_its_own_block(self) -> None:
        # Takt 5, Teil 3: 5 + 17 + 3 · 9973 = 29941
        self.assertEqual(part_seed(5, PART_EYE_RIGHT), 29941)
        for tick in (0, 5, 9972):
            seeds = [part_seed(tick, part) for part in PARTS]
            self.assertEqual(len(set(seeds)), len(PARTS), tick)

    def test_unknown_part_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            part_seed(0, len(PARTS))
        # Zwilling: der letzte bekannte Teil geht durch
        self.assertGreater(part_seed(0, PARTS[-1]), 0)

    def test_negative_or_boolean_tick_is_rejected(self) -> None:
        for tick in (-1, True):
            with self.subTest(tick=tick), self.assertRaises(ValueError):
                draw_brows(RecordingContext(), NEUTRAL, tick)
        # Zwilling: Takt 0 zeichnet
        cr = RecordingContext()
        draw_brows(cr, NEUTRAL, 0)
        self.assertIn("fill", cr.names())


class ParkMillerTest(unittest.TestCase):
    """Die Folge des Generators ist die des Prototyps."""

    def test_seed_17_gives_the_prototype_sequence(self) -> None:
        # rnd(): seed = seed · 16807 % 2147483647, Wert seed / 2147483647.
        # 17 · 16807 = 285719
        # 285719 · 16807 = 4802079233 = 2 · 2147483647 + 507111939
        # 507111939 · 16807 = 8523030358773 = 3968 · 2147483647 + 1815247477
        # 1815247477 · 16807 = 30508864345939 = 14206 · 2147483647 + 1711656657
        # 1711656657 · 16807 = 28767813434199 = 13396 · 2147483647 + 122498987
        states = [285719, 507111939, 1815247477, 1711656657, 122498987]
        rng = ParkMiller(state=17)
        values = [park_miller_next(rng) for _ in states]
        self.assertEqual(values, [s / 2147483647 for s in states])
        self.assertAlmostEqual(values[0], 1.33048e-4, delta=1e-9)
        self.assertEqual(rng.state, 122498987)

    def test_zero_state_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            park_miller_next(ParkMiller(state=0))
        # Zwilling: der kleinste gültige Zustand geht durch und ergibt 16807
        rng = ParkMiller(state=1)
        park_miller_next(rng)
        self.assertEqual(rng.state, 16807)


class JsRoundTest(unittest.TestCase):
    """`Math.round` rundet .5 aufwärts, Pythons `round` zur geraden Zahl."""

    def test_half_rounds_up_like_the_browser(self) -> None:
        self.assertEqual(js_round(6.5), 7)  # round(6.5) wäre 6
        self.assertEqual(js_round(16.5), 17)  # round(16.5) wäre 16
        self.assertEqual(js_round(-2.5), -2)  # Math.round(-2.5) = -2
        self.assertEqual(js_round(0.49), 0)

    def test_blush_stroke_count_uses_browser_rounding(self) -> None:
        # Röte 0,75: 0,75 · 22 = 16,5 → Math.round 17 Striche je Wange, zwei Wangen = 34.
        # Innere Brauen 0: keine Falten; Träne und Schweiß 0: keine Tropfen.
        cr = RecordingContext()
        draw_extras(cr, _face(blush=0.75), 0.0, 3)
        self.assertEqual(cr.names().count("stroke"), 34)

    def test_no_blush_draws_nothing(self) -> None:
        # Zwilling zur Zählung: Röte 0 ergibt keinen Strich
        cr = RecordingContext()
        draw_extras(cr, NEUTRAL, 0.0, 3)
        self.assertEqual(cr.calls, [])

    def test_non_finite_value_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            js_round(math.nan)
        self.assertEqual(js_round(1.0), 1)


class ReferenceTargetsTest(unittest.TestCase):
    """Alle 45 Referenzziele zeichnen ohne Fehler, jede Koordinate endlich und in der Vorlage."""

    @classmethod
    def setUpClass(cls) -> None:
        with REFERENCE_PATH.open(encoding="utf-8") as handle:
            cls.entries = json.load(handle)["werte"]

    def test_all_45_targets_at_three_blink_values(self) -> None:
        self.assertEqual(len(self.entries), 45)
        for entry in self.entries:
            face = FaceState(**{f: float(entry["face"][k]) for f, k in PROTOTYPE_KEYS.items()})
            label = f"Sektor {entry['sektor']}, Arousal {entry['arousal']}"
            cr = RecordingContext()
            draw_brows(cr, face, 7)
            draw_extras(cr, face, 1234.5, 7)
            for blink in (0.0, 0.5, 1.0):
                draw_eyes(cr, RecordingGradients(), face, blink, 7)
            with self.subTest(target=label):
                self.assertGreater(cr.names().count("stroke"), 0)
                self.assertEqual(_violations(cr.calls), [])
                self.assertEqual(cr.names().count("save"), cr.names().count("restore"))

    def test_violation_check_sees_a_point_outside(self) -> None:
        # Zwilling zur leeren Liste oben: die Prüfung schlägt an
        bad = [("move_to", (-1.0, 10.0)), ("line_to", (10.0, math.inf))]
        self.assertEqual(len(_violations(bad)), 2)
        self.assertEqual(_violations([("move_to", (0.0, float(SRC)))]), [])


class ClosedEyeTest(unittest.TestCase):
    """Bei Blinzelwert 0 liegt das Lid, wo der Prototyp es hat."""

    def test_closed_lid_midpoint(self) -> None:
        # Linkes Auge: Mitte (521, 366), hw 50, Seite −1.
        # Innen L(E, 50, 2,5), Kontrolle L(E, 0, 8), außen L(E, −50, −4).
        # Punkt 10 von 20 ist t = 0,5: 0,25·innen + 0,5·Kontrolle + 0,25·außen
        # = L(E, 0, 0,625 + 4 − 1) = L(E, 0, 3,625)
        # = (521 − 3,625 · sin 9°, 366 + 3,625 · cos 9°) = (520,4329251, 369,5803702).
        x, y = closed_lid(EYE_LEFT)[10]
        self.assertAlmostEqual(x, 520.432925064229, delta=EXACT)
        self.assertAlmostEqual(y, 369.580370234657, delta=EXACT)

    def test_blink_zero_draws_the_closed_lid(self) -> None:
        cr = _eyes(NEUTRAL, 0.0)
        names = cr.names()
        # Geschlossen: kein Augapfel (kein clip, kein Verlauf), je Auge 4 Lidlinien,
        # 16 Wimpern und 1 Falte = 21 Striche, zwei Augen = 42.
        self.assertNotIn("clip", names)
        self.assertNotIn("set_source", names)
        self.assertEqual(names.count("stroke"), 42)
        # Erster Strich beginnt am inneren Winkel L(E, 50, 2,5)
        # = (521 + 50 · cos 9° − 2,5 · sin 9°, 366 + 50 · sin 9° + 2,5 · cos 9°)
        # = (569,9933309, 376,2909441), verwackelt um höchstens 0,1.
        self.assertEqual(cr.calls[1][0], "move_to")
        x, y = cr.calls[1][1]
        self.assertAlmostEqual(x, 569.9933308669, delta=SHAKE_FINE + EXACT)
        self.assertAlmostEqual(y, 376.2909441035, delta=SHAKE_FINE + EXACT)

    def test_blink_one_draws_the_open_eye(self) -> None:
        # Zwilling: offen gibt es je Auge einen Augapfel mit Beschnitt
        names = _eyes(NEUTRAL, 1.0).names()
        self.assertEqual(names.count("clip"), 2)
        self.assertIn("set_source", names)

    def test_blink_out_of_range_is_rejected(self) -> None:
        for blink in (-0.1, 1.5, math.nan, True):
            with self.subTest(blink=blink), self.assertRaises(ValueError):
                _eyes(NEUTRAL, blink)
        # Zwilling: beide Grenzen gehen durch
        self.assertGreater(len(_eyes(NEUTRAL, 0.0).calls), 0)
        self.assertGreater(len(_eyes(NEUTRAL, 1.0).calls), 0)


class PrototypeFormulaTest(unittest.TestCase):
    """Die Formeln des Prototyps an Stichstellen, je eine Zahl nachgerechnet."""

    def test_brow_point_at_inner_minus_30(self) -> None:
        # drawBrow, linke Braue, bli −30, blo 0, barch 0:
        # Verschiebung (−30, (−30 + 0)/2 − 1 + 0, 0) = (−30, −16, 0) entlang (−sin 9°, cos 9°).
        # Innen (575, 306) + (−30)·(−sin, cos) = (575 + 4,6930340, 306 − 29,6306502).
        # Scheitel (500, 284) + (−16)·(−sin, cos) = (500 + 2,5029514, 284 − 15,8030134).
        inner, peak, outer = brow_points(BROW_LEFT, _face(brow_left_inner=-30.0))
        self.assertAlmostEqual(inner[0], 579.693033951207, delta=EXACT)
        self.assertAlmostEqual(inner[1], 276.369349782146, delta=EXACT)
        self.assertAlmostEqual(peak[0], 502.502951440644, delta=EXACT)
        self.assertAlmostEqual(peak[1], 268.196986550478, delta=EXACT)
        self.assertEqual(outer, (455.0, 301.0))

    def test_pupil_size_072(self) -> None:
        # Linkes Auge: Irisradius 50 · 0,46 = 23, Pupille 23 · 0,38 · 0,72 = 6,2928;
        # gezeichnet wird der Kreis mit 6,2928 · 1,08 = 6,796224.
        face = _face(pupil_size=0.72)
        self.assertAlmostEqual(pupil_radius(EYE_LEFT, face), 6.2928, delta=EXACT)
        radii = [args[2] for args in _arcs(_eyes(face, 1.0))]
        self.assertTrue(any(abs(r - 6.796224) < EXACT for r in radii), radii[:12])

    def test_eye_open_1215(self) -> None:
        # Linkes Auge, eo 1,215, blink 1, lidU 0, arc 0:
        # up = 50 · 0,5 · 1,215 = 30,375; lo = 50 · 0,27 · 1,215 = 16,4025.
        # Die Iris hebt sich um up · 0,12 = 3,645: Mitte L(E, 0, −3,645)
        # = (521 + 3,645 · sin 9°, 366 − 3,645 · cos 9°) = (521,5702036, 362,3998760).
        face = _face(eye_open=1.215)
        up, lo = lid_extent(EYE_LEFT, face, 1.215)
        self.assertAlmostEqual(up, 30.375, delta=EXACT)
        self.assertAlmostEqual(lo, 16.4025, delta=EXACT)
        iris = [a for a in _arcs(_eyes(face, 1.0)) if abs(a[2] - 23.0) < EXACT]
        self.assertTrue(iris)
        self.assertAlmostEqual(iris[0][0], 521.570203625072, delta=EXACT)
        self.assertAlmostEqual(iris[0][1], 362.399875998531, delta=EXACT)

    def test_non_finite_channel_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            draw_brows(RecordingContext(), _face(brow_arch=math.nan), 0)
        # Zwilling: ein endlicher Wert zeichnet
        cr = RecordingContext()
        draw_brows(cr, _face(brow_arch=-3.0), 0)
        self.assertIn("stroke", cr.names())


class ExtrasTest(unittest.TestCase):
    """Falten, Träne und Schweiß erscheinen ab ihren Schwellen."""

    def test_frown_and_worry_lines(self) -> None:
        # Innere Brauen 24 gesenkt: Zorn (24 − 8)/16 = 1 → zwei Seiten × zwei Striche = 4.
        frown = RecordingContext()
        draw_brow_wrinkles(frown, _face(brow_left_inner=24.0, brow_right_inner=24.0), 3)
        self.assertEqual(frown.names().count("stroke"), 4)
        # Innere Brauen 26 gehoben: Sorge (26 − 12)/14 = 1 → drei Querfalten.
        worry = RecordingContext()
        draw_brow_wrinkles(worry, _face(brow_left_inner=-26.0, brow_right_inner=-26.0), 3)
        self.assertEqual(worry.names().count("stroke"), 3)
        # Neutral: keine Falte
        calm = RecordingContext()
        draw_brow_wrinkles(calm, NEUTRAL, 3)
        self.assertEqual(calm.calls, [])

    def test_tear_and_sweat_above_threshold(self) -> None:
        # Je Tropfen ein Bleistiftstrich in zwei Lagen
        wet = RecordingContext()
        draw_extras(wet, _face(tear=0.6, sweat=0.6), 500.0, 3)
        self.assertEqual(wet.names().count("stroke"), 4)
        dry = RecordingContext()
        draw_extras(dry, _face(tear=0.2, sweat=0.2), 500.0, 3)
        self.assertEqual(dry.names().count("stroke"), 0)

    def test_negative_time_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            draw_extras(RecordingContext(), NEUTRAL, -1.0, 3)
        draw_extras(RecordingContext(), NEUTRAL, 0.0, 3)


class WithoutCairoTest(unittest.TestCase):
    """Die Module laden ohne pycairo und ohne GTK; Cairo kommt erst mit dem ersten Verlauf."""

    def _load_blocked(self) -> types.ModuleType:
        saved = {name: getattr(avatar, name.split(".")[1], None) for name in DRAWING_MODULES}
        self.addCleanup(self._restore, saved)
        for name in DRAWING_MODULES:
            sys.modules.pop(name, None)
        return importlib.import_module("avatar.drawing")

    @staticmethod
    def _restore(saved: dict) -> None:
        for name, module in saved.items():
            setattr(avatar, name.split(".")[1], module)

    def test_modules_load_and_draw_without_cairo(self) -> None:
        with mock.patch.dict(sys.modules, {"cairo": None, "gi": None}):
            fresh = self._load_blocked()
            self.assertIsNot(fresh, drawing)
            for name in DRAWING_MODULES:
                self.assertNotIn("cairo", vars(sys.modules[name]))
            cr = RecordingContext()
            fresh.draw_brows(cr, NEUTRAL, 0)
            self.assertIn("fill", cr.names())
            # Erst der echte Verlauf braucht Cairo — und meldet sein Fehlen laut
            with self.assertRaises(ImportError):
                sys.modules["avatar.drawing_tools"].CairoGradients().linear(
                    (0.0, 0.0), (1.0, 1.0), ((0.0, (0.0, 0.0, 0.0, 1.0)),)
                )

    def test_the_block_stops_a_cairo_import(self) -> None:
        # Zwilling: unter derselben Sperre scheitert ein Modul, das Cairo oben importiert
        with mock.patch.dict(sys.modules, {"cairo": None, "gi": None}):
            probe = types.ModuleType("probe")
            with self.assertRaises(ImportError):
                exec("import cairo", vars(probe))  # noqa: S102 — fester Text, kein fremder


if __name__ == "__main__":
    unittest.main()
