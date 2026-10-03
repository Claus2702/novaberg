"""Zeugen für das Zeichnen des Mundes.

Gezeichnet wird auf `RecordingContext`, der jeden Aufruf mit seinen Argumenten
mitschreibt — so wie ein Cairo-Kontext ihn empfinge. Kein Zeuge braucht pycairo,
GTK oder einen Bildschirm.

Die Zahlen an den Stichstellen sind aus den Formeln des Prototyps von Hand
gerechnet; die Rechnung steht jeweils daneben. Die Mitte des Mundes liegt bei
(590,2; 566), die Gesichtsachse ist um 9° geneigt: sin 9° = 0,15643446504023087,
cos 9° = 0,9876883405951378. Ein Punkt in Gesichtsachsen ist
L(lx, ly) = (590,2 + lx·cos − ly·sin, 566 + lx·sin + ly·cos).
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
from avatar import mouth_drawing
from avatar.drawing_tools import SRC
from avatar.face import NEUTRAL, PROTOTYPE_KEYS, FaceState
from avatar.mouth_drawing import MOUTH_SEGMENTS, draw_mouth, mouth_shape
from avatar.speech import SILENT, mouth_state_combine

REFERENCE_DIR = Path(__file__).parent / "avatar_reference"
DRAWING_MODULES = (
    "avatar.mouth_drawing", "avatar.drawing", "avatar.drawing_eye", "avatar.drawing_tools",
)
POINT_CALLS = ("move_to", "line_to", "curve_to", "translate")
EXACT = 1e-9
MIDDLE = MOUTH_SEGMENTS // 2  # Index 12 liegt bei t = 0,5, der Mitte der Lippe
TEETH = 28  # 7 Zähne je Seite, oben und unten


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
    """Neutral, Mundkrümmung 0, mit den genannten Kanälen."""
    return replace(NEUTRAL, **{"mouth_curve": 0.0, **changes})


def _local(lx: float, ly: float) -> tuple[float, float]:
    """L(lx, ly) um die Mitte des Mundes, unabhängig vom Modul gerechnet."""
    tilt = math.radians(9)
    return (
        590.2 + lx * math.cos(tilt) - ly * math.sin(tilt),
        566.0 + lx * math.sin(tilt) + ly * math.cos(tilt),
    )


def _draw(face: FaceState, tongue: float = 0.0, tick: int = 3) -> RecordingContext:
    cr = RecordingContext()
    draw_mouth(cr, RecordingGradients(), face, tongue, tick)
    return cr


def _patterns(cr: RecordingContext, kind: str) -> list[tuple]:
    return [args[0] for name, args in cr.calls if name == "set_source" and args[0][0] == kind]


def _teeth(cr: RecordingContext) -> list[tuple]:
    """Die Schatten der Zähne: lineare Verläufe in Grafit (40, 40, 44), einer je Zahn."""
    return [p for p in _patterns(cr, "linear") if p[3][0][1][:3] == (40.0, 40.0, 44.0)]


def _widths(cr: RecordingContext) -> list[float]:
    return [args[0] for name, args in cr.calls if name == "set_line_width"]


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
        elif name == "set_source_rgba" and not all(0.0 <= v <= 1.0 for v in args):
            bad.append((name, args))
        elif name in ("set_line_width", "scale") and min(args) < 0:
            bad.append((name, args))
    return bad


def _load(name: str) -> dict:
    with (REFERENCE_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def _reference_face(values: dict) -> FaceState:
    return FaceState(**{f: float(values[k]) for f, k in PROTOTYPE_KEYS.items()})


class DeterminismTest(unittest.TestCase):
    """Gleiche Kanäle, gleiche Zunge, gleicher Takt → gleiche Aufrufliste.

    Ein Blinzelwert geht in den Mund nicht ein; `draw_mouth` nimmt keinen.
    """

    face = _face(
        mouth_curve=18.0, mouth_open=24.0, jaw=16.0, mouth_width=96.0, mouth_asym=-3.0,
        au12_left=0.6, au10_right=0.3, au16_left=0.4, au18=0.2,
    )

    def test_same_input_draws_the_same_calls(self) -> None:
        first = _draw(self.face, 0.6, 41).calls
        self.assertGreater(len(first), 500)
        self.assertEqual(first, _draw(self.face, 0.6, 41).calls)

    def test_another_tick_draws_other_strokes(self) -> None:
        # Zwilling: derselbe Mund im nächsten Takt — gleiche Zahl der Aufrufe, andere Striche
        first, second = _draw(self.face, 0.6, 41).calls, _draw(self.face, 0.6, 42).calls
        self.assertEqual([n for n, _ in first], [n for n, _ in second])
        self.assertNotEqual(first, second)


class ReferenceTargetsTest(unittest.TestCase):
    """Alle 45 Referenzziele zeichnen ohne Fehler, jede Koordinate endlich und in der Vorlage."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = _load("expression.json")["werte"]

    def test_all_45_targets_raw_and_combined(self) -> None:
        # Roh wie das Ziel und so, wie der Mund im Client ankommt: nach mouth_state_combine
        self.assertEqual(len(self.entries), 45)
        for entry in self.entries:
            raw = _reference_face(entry["face"])
            combined, tongue = mouth_state_combine(raw, SILENT)
            label = f"Sektor {entry['sektor']}, Arousal {entry['arousal']}"
            for face in (raw, combined):
                cr = _draw(face, tongue, 7)
                with self.subTest(target=label, combined=face is combined):
                    self.assertGreater(cr.names().count("stroke"), 0)
                    self.assertEqual(_violations(cr.calls), [])
                    self.assertEqual(cr.names().count("save"), cr.names().count("restore"))

    def test_violation_check_sees_a_point_outside(self) -> None:
        # Zwilling zur leeren Liste oben: die Prüfung schlägt an
        bad = [("move_to", (-1.0, 10.0)), ("line_to", (10.0, math.inf))]
        self.assertEqual(len(_violations(bad)), 2)
        self.assertEqual(_violations([("move_to", (0.0, float(SRC)))]), [])


class SpeechStepsTest(unittest.TestCase):
    """Jeder Schritt von Satz 1 (`gemischt`: Sprechen mit Freude) zeichnet ohne Fehler."""

    def test_every_step_of_sentence_one(self) -> None:
        steps = _load("speech.json")["saetze"][0]["gemischt"]["werte"]
        self.assertGreater(len(steps), 20)
        tongues = []
        for entry in steps:
            face, tongue = _reference_face(entry["face"]), entry["face"].get("tng", 0.0)
            tongues.append(tongue)
            cr = _draw(face, tongue, 11)
            with self.subTest(t=entry["t"]):
                self.assertGreater(cr.names().count("stroke"), 0)
                self.assertEqual(_violations(cr.calls), [])
                self.assertEqual(cr.names().count("save"), cr.names().count("restore"))
        # Der Satz bewegt die Zunge: sonst prüfte er den Zungenweg nicht mit
        self.assertGreater(max(tongues), 0.0)


class ClosedLipsTest(unittest.TestCase):
    """Bei `au24` 1 sind die Lippen zu: kein Mundraum, keine Zähne, keine Zunge."""

    open_face = _face(mouth_open=30.0, jaw=20.0, mouth_width=90.0)

    def test_pressed_lips_hide_teeth_and_tongue(self) -> None:
        # mouth_state_combine setzt mo auf 30 · (1 − 1) = 0; die Öffnung 0 < 2 Pixel
        face, _ = mouth_state_combine(replace(self.open_face, au24=1.0), SILENT)
        self.assertEqual(face.mouth_open, 0.0)
        cr = _draw(face, 1.0)
        # Ohne clip kein Mundraum; Zunge (radiale Verläufe) und Zähne zeichnen nur darin
        self.assertNotIn("clip", cr.names())
        self.assertEqual(_patterns(cr, "radial"), [])
        self.assertEqual(_teeth(cr), [])
        # Die Mundlinie gepresst: Breite 2,2 + 1,4 · 1 = 3,6
        self.assertTrue(any(abs(w - 3.6) < EXACT for w in _widths(cr)))

    def test_without_pressing_teeth_and_tongue_show(self) -> None:
        # Zwilling: derselbe Mund ohne au24 ist offen
        face, _ = mouth_state_combine(self.open_face, SILENT)
        cr = _draw(face, 1.0)
        self.assertIn("clip", cr.names())
        self.assertEqual(len(_patterns(cr, "radial")), 2)  # Zungenkörper und Zungenblatt
        self.assertEqual(len(_teeth(cr)), TEETH)
        self.assertFalse(any(abs(w - 3.6) < EXACT for w in _widths(cr)))

    def test_pressing_thins_the_upper_lip(self) -> None:
        # Oberlippe bei mc 0, mo 0: 19 · (1 − 0,35 · au24); gepresst 12,35, sonst 19
        self.assertAlmostEqual(mouth_shape(_face(au24=1.0)).upper_thick, 12.35, delta=EXACT)
        self.assertAlmostEqual(mouth_shape(_face()).upper_thick, 19.0, delta=EXACT)


class TeethThresholdTest(unittest.TestCase):
    """Zähne erst ab einer Öffnung von 2 Pixeln, wie `moOpen >= 2` im Prototyp."""

    def test_below_two_pixels_no_teeth(self) -> None:
        cr = _draw(_face(mouth_open=1.9))
        self.assertNotIn("clip", cr.names())
        self.assertEqual(_teeth(cr), [])

    def test_at_two_pixels_all_teeth(self) -> None:
        # Zwilling: 0,1 Pixel mehr, und alle 28 Zähne stehen im Mundraum
        cr = _draw(_face(mouth_open=2.0))
        self.assertEqual(cr.names().count("clip"), 1)
        self.assertEqual(len(_teeth(cr)), TEETH)

    def test_lip_raisers_open_without_mouth_open(self) -> None:
        # Öffnung 9 · (0,25 + 0,25) / 2 = 2,25 ≥ 2 durch den Oberlippenheber allein
        shape = mouth_shape(_face(au10_left=0.25, au10_right=0.25))
        self.assertAlmostEqual(shape.opening, 2.25, delta=EXACT)
        self.assertEqual(len(_teeth(_draw(_face(au10_left=0.25, au10_right=0.25)))), TEETH)


class PrototypeFormulaTest(unittest.TestCase):
    """Die Formeln von `drawMouth` an Stichstellen, je Zahl von Hand nachgerechnet."""

    def _assert_point(self, actual: tuple, expected: tuple) -> None:
        self.assertAlmostEqual(actual[0], expected[0], delta=1e-9)
        self.assertAlmostEqual(actual[1], expected[1], delta=1e-9)

    def test_mouth_width_at_mw_110(self) -> None:
        # sideW = mw · (1 + 0 …) = 110 je Seite: Winkel bei L(−110, 0) und L(110, 0),
        # Abstand 220 — mw ist die halbe Breite, der Mund also 220 Pixel breit
        shape = mouth_shape(_face(mouth_width=110.0))
        self.assertEqual((shape.width_left, shape.width_right), (110.0, 110.0))
        self._assert_point(shape.corner_left, _local(-110.0, 0.0))
        self._assert_point(shape.corner_right, _local(110.0, 0.0))
        self.assertAlmostEqual(math.dist(shape.corner_left, shape.corner_right), 220.0, delta=1e-9)

    def test_mouth_corner_at_mc_40(self) -> None:
        # Winkelhöhe −mc · 0,45 · (1 + 1,2 · 0) = −18 (square 0, weil mc > 0);
        # L(−100, −18) = (590,2 − 98,76883405951378 + 2,815820370724156,
        #                 566 − 15,643446504023087 − 17,77839013071248)
        shape = mouth_shape(_face(mouth_curve=40.0, mouth_width=100.0))
        self._assert_point(shape.corner_left, (494.2469863112104, 532.5781633652644))
        # Mitte: ctrl = mid = 40 · 0,95 = 38, Tiefe (38 + 18) / 2 = 28, also −18 + 28 = 10
        self._assert_point(shape.upper[MIDDLE], _local(0.0, 10.0))

    def test_lower_lip_at_mo_70(self) -> None:
        # openK = 1, mid = 0; ctrl der Unterlippe = 70 · 2 = 140, Tiefe 70, Mitte bei ly 70:
        # L(0, 70) = (590,2 − 10,950412552816161, 566 + 69,13818384165965)
        shape = mouth_shape(_face(mouth_open=70.0, mouth_width=100.0))
        self._assert_point(shape.lower[MIDDLE], (579.2495874471838, 635.1381838416596))
        # Unterlippe 28 dick, Profil 1 in der Mitte: Außenkontur bei ly 98
        self._assert_point(shape.bottom[MIDDLE], _local(0.0, 98.0))
        # Oberlippe: ctrl = −70 · 0,35 = −24,5, Tiefe −12,25
        self._assert_point(shape.upper[MIDDLE], _local(0.0, -12.25))

    def test_closed_mouth_has_one_line(self) -> None:
        # Zwilling zu mo 70: unter 2 Pixeln Öffnung ist die Unterlippe dieselbe Kurve
        shape = mouth_shape(_face(mouth_open=1.0))
        self.assertIs(shape.lower, shape.upper)


class RejectionTest(unittest.TestCase):
    """Ungültige Eingaben werden laut abgewiesen, gültige an der Grenze nicht."""

    def test_non_positive_mouth_width_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            mouth_shape(_face(mouth_width=0.0))
        # Zwilling: die kleinste positive Breite geht durch
        self.assertGreater(mouth_shape(_face(mouth_width=1.0)).half_width, 0.0)

    def test_tongue_outside_unit_range_is_rejected(self) -> None:
        face = _face(mouth_open=20.0)
        for tongue in (-0.1, 1.5, math.nan):
            with self.subTest(tongue=tongue), self.assertRaises(ValueError):
                _draw(face, tongue)
        # Zwilling: die Grenzen 0 und 1 gelten
        self.assertIn("clip", _draw(face, 0.0).names())
        self.assertIn("clip", _draw(face, 1.0).names())

    def test_non_finite_channel_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _draw(_face(mouth_curve=math.inf))
        # Zwilling: ein großer, endlicher Wert zeichnet
        self.assertIn("stroke", _draw(_face(mouth_curve=40.0)).names())

    def test_negative_tick_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _draw(_face(), 0.0, -1)
        self.assertIn("stroke", _draw(_face(), 0.0, 0).names())


class WithoutCairoTest(unittest.TestCase):
    """Das Mundmodul lädt und zeichnet ohne pycairo und ohne GTK."""

    def _load_blocked(self) -> types.ModuleType:
        saved = {name: getattr(avatar, name.split(".")[1], None) for name in DRAWING_MODULES}
        self.addCleanup(self._restore, saved)
        for name in DRAWING_MODULES:
            sys.modules.pop(name, None)
        return importlib.import_module("avatar.mouth_drawing")

    @staticmethod
    def _restore(saved: dict) -> None:
        for name, module in saved.items():
            setattr(avatar, name.split(".")[1], module)

    def test_module_loads_and_draws_without_cairo(self) -> None:
        with mock.patch.dict(sys.modules, {"cairo": None, "gi": None}):
            fresh = self._load_blocked()
            self.assertIsNot(fresh, mouth_drawing)
            for name in DRAWING_MODULES:
                self.assertNotIn("cairo", vars(sys.modules[name]))
            cr = RecordingContext()
            fresh.draw_mouth(cr, RecordingGradients(), _face(mouth_open=20.0), 0.5, 0)
            self.assertIn("clip", cr.names())

    def test_the_block_stops_a_cairo_import(self) -> None:
        # Zwilling: unter derselben Sperre scheitert ein Modul, das Cairo oben importiert
        with mock.patch.dict(sys.modules, {"cairo": None, "gi": None}):
            probe = types.ModuleType("probe")
            with self.assertRaises(ImportError):
                exec("import cairo", vars(probe))  # noqa: S102 — fester Text, kein fremder


if __name__ == "__main__":
    unittest.main()
