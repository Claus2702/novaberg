"""Zeugen für die Rechnung der Kopfdrehung: Gitter, Kinnlinie, Hals, Grenze.

Die Verschiebungen unter `avatar_reference/yaw.json` sind aus dem Prototyp erzeugt
(`yawGitter`) und tragen je Winkel die Verschiebung an allen 24 × 29 Punkten. Die
Zeichnung der Drehung bezeugt `test_avatar_compose.py`. Kein Zeuge braucht pycairo,
GTK, eine Datei außer der Referenz oder einen Bildschirm.
"""

import json
import math
import unittest
from pathlib import Path

from avatar.drawing_eye import EYE_LEFT, EYE_RIGHT
from avatar.drawing_tools import SRC, UX, UY
from avatar.head_turn import (
    HEAD_C,
    JAWLINE,
    NECK_CX,
    NECK_LEN,
    NECK_R,
    YAW_TRIANGLES,
    YAW_XS,
    YAW_YS,
    TurnPoint,
    jaw_y,
    neck_shift,
    yaw_grid,
    yaw_shift,
    yaw_triangles,
)

EXACT = 1e-9
REFERENCE_PATH = Path(__file__).parent / "avatar_reference" / "yaw.json"
HALF_DEGREES = [k / 2 for k in range(-30, 31)]  # −15 … 15 in Schritten von 0,5


def _head_point(u: float, v: float) -> tuple[float, float]:
    """Ein Punkt aus Kopfkoordinaten (quer `u`, längs `v`), wie `kopfPunkt` im Prüfanker."""
    return (HEAD_C[0] + u * UX - v * UY, HEAD_C[1] + u * UY + v * UX)


def _shift_at(point: tuple[float, float], deg: float) -> float:
    """Die Verschiebung an einem beliebigen Punkt bei `deg` Grad."""
    th = deg * math.pi / 180
    return yaw_shift(point[0], point[1], math.sin(th), th)


def _grid_without_limit(deg: float) -> list[list[TurnPoint]]:
    """Das Gitter wie `yaw_grid`, aber ohne Grenze — nur für den Zwilling von D3."""
    th = deg * math.pi / 180
    s = math.sin(th)
    rows = []
    for y in YAW_YS:
        shifts = [yaw_shift(x, y, s, th) for x in YAW_XS]
        rows.append(
            [
                TurnPoint(source=(x, y), dest=(x + UX * sh, y + UY * sh), shift=sh)
                for x, sh in zip(YAW_XS, shifts, strict=True)
            ]
        )
    return rows


def _orientation(points: tuple) -> int:
    """Umlaufsinn eines Dreiecks: 1, −1 oder 0 (ohne Fläche)."""
    (x0, y0), (x1, y1), (x2, y2) = points
    cross = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
    return (cross > 0) - (cross < 0)


def _flipped(grid: list[list[TurnPoint]]) -> int:
    """Zahl der Dreiecke, deren Ziel anders umläuft als die Quelle, wie `umgeklappt`."""
    return sum(
        _orientation(t.warp.source) != _orientation(t.warp.dest) for t in yaw_triangles(grid)
    )


class ReferenceTest(unittest.TestCase):
    """D1: das Gitter gleich `yaw.json`, an allen Punkten und allen acht Winkeln."""

    @classmethod
    def setUpClass(cls) -> None:
        with REFERENCE_PATH.open(encoding="utf-8") as handle:
            cls.reference = json.load(handle)

    def test_d1_reference_describes_the_same_grid(self) -> None:
        ref = self.reference
        self.assertEqual(ref["format"], 1)
        self.assertEqual(ref["xs"], list(YAW_XS))
        self.assertEqual(ref["ys"], list(YAW_YS))
        self.assertEqual((len(YAW_XS), len(YAW_YS)), (24, 29))
        self.assertAlmostEqual(ref["achse"]["ux"], UX, delta=1e-15)
        self.assertAlmostEqual(ref["achse"]["uy"], UY, delta=1e-15)
        self.assertEqual(ref["winkel"], [-15, -5, -1, 1, 3, 8, 12, 15])

    def test_d1_every_shift_matches_the_reference(self) -> None:
        for deg in self.reference["winkel"]:
            want = self.reference["verschiebung"][str(deg)]
            grid = yaw_grid(float(deg))
            with self.subTest(deg=deg):
                self.assertEqual([len(row) for row in want], [24] * 29)
                # Die erste Abweichung nennen, nicht die ganze Liste
                off = [
                    (p.source, p.shift, w)
                    for row, wrow in zip(grid, want, strict=True)
                    for p, w in zip(row, wrow, strict=True)
                    if abs(p.shift - w) > EXACT
                ]
                self.assertEqual(off[:1], [], f"{len(off)} Punkte weichen ab")

    def test_d1_reference_is_not_flat(self) -> None:
        """Zwilling: Verglichen werden echte Verschiebungen, nicht Nullen."""
        at_12 = self.reference["verschiebung"]["12"]
        self.assertGreater(max(abs(v) for row in at_12 for v in row), 20.0)

    def test_dest_is_source_plus_shift_along_the_axis(self) -> None:
        for row in yaw_grid(12.0):
            for p in row:
                x, y = p.source
                self.assertAlmostEqual(p.dest[0], x + UX * p.shift, delta=EXACT)
                self.assertAlmostEqual(p.dest[1], y + UY * p.shift, delta=EXACT)


class FoldTest(unittest.TestCase):
    """D3: kein Dreieck klappt um, −15 … 15 in Schritten von 0,5."""

    def test_d3_no_triangle_folds_up_to_15_degrees(self) -> None:
        self.assertEqual(len(HALF_DEGREES), 61)
        folds = {deg: _flipped(yaw_grid(deg)) for deg in HALF_DEGREES}
        self.assertEqual({deg: n for deg, n in folds.items() if n}, {})

    def test_d3_beyond_the_limit_triangles_fold(self) -> None:
        """Zwilling: Bei ±30° klappen Dreiecke um, und die Zählung sieht es."""
        for deg in (30.0, -30.0):
            with self.subTest(deg=deg):
                self.assertGreater(_flipped(_grid_without_limit(deg)), 0)


class StandingTest(unittest.TestCase):
    """D5: Rand, Schultern und Haar unter dem Kinn stehen; die Tiefe ordnet die Wanderung."""

    def test_d5_border_and_shoulders_stand(self) -> None:
        for deg in HALF_DEGREES:
            moving = [
                p.source
                for row in yaw_grid(deg)
                for p in row
                if (p.source[0] in (0, SRC) or p.source[1] in (0, SRC) or p.source[1] >= 1150)
                and abs(p.shift) > EXACT
            ]
            self.assertEqual(moving, [], f"{deg}°")

    def test_d5_hair_beside_the_neck_below_the_chin_stands(self) -> None:
        # Neben dem Hals (|x − NECK_CX| ≥ 1,25 · NECK_R) und unter dem Kinn (v ≥ 340)
        def below_chin_beside_neck(x: float, y: float) -> bool:
            """Wahr für Punkte neben dem Hals und unter dem Kinn."""
            v = -(x - HEAD_C[0]) * UY + (y - HEAD_C[1]) * UX
            return abs(x - NECK_CX) >= 1.25 * NECK_R and v >= 340

        points = [(x, y) for y in YAW_YS for x in YAW_XS if below_chin_beside_neck(x, y)]
        self.assertGreater(len(points), 50)  # Zwilling: die Menge ist nicht leer
        for deg in (-15.0, -5.0, 5.0, 12.0, 15.0):
            moving = [p for p in points if abs(_shift_at(p, deg)) > EXACT]
            self.assertEqual(moving, [], f"{deg}°")

    def test_d5_the_head_moves(self) -> None:
        """Zwilling: Bei denselben Winkeln wandern Gesicht und Haar über dem Kinn."""
        for deg in (-15.0, -5.0, 5.0, 12.0, 15.0):
            self.assertGreater(abs(_shift_at((150.0, 475.0), deg)), 1.0, f"{deg}°")
            self.assertGreater(abs(_shift_at(_head_point(0, 15), deg)), 5.0, f"{deg}°")

    def test_d5_at_12_degrees_nose_before_eyes_before_ears_before_hair(self) -> None:
        nose = [abs(_shift_at(_head_point(0, 15), 12.0))]
        eyes = [abs(_shift_at(e.center, 12.0)) for e in (EYE_LEFT, EYE_RIGHT)]
        ears = [abs(_shift_at(_head_point(u, 0), 12.0)) for u in (-235, 235)]
        hair = [abs(_shift_at(p, 12.0)) for p in ((150.0, 475.0), (1100.0, 475.0))]
        levels = [nose, eyes, ears, hair]
        for front, back in zip(levels, levels[1:], strict=False):
            self.assertGreater(min(front), max(back), levels)
        # Die Nase wandert etwa 27 Pixel der Vorlage, so viel wie im Prototyp
        self.assertGreater(nose[0], 26.5)
        self.assertLess(nose[0], 29.0)

    def test_moved_triangles_are_some_but_not_all(self) -> None:
        triangles = yaw_triangles(yaw_grid(12.0))
        self.assertEqual(len(triangles), YAW_TRIANGLES)
        self.assertEqual(YAW_TRIANGLES, 1288)
        moved = sum(t.moved for t in triangles)
        self.assertGreater(moved, 0)
        self.assertLess(moved, YAW_TRIANGLES)
        for t in triangles:
            if not t.moved:
                self.assertEqual(t.warp.source, t.warp.dest)


class LimitTest(unittest.TestCase):
    """D6: Jenseits von ±15°, bei `nan` und bei `inf` wirft das Gitter."""

    def test_d6_beyond_15_degrees_or_not_finite_is_rejected(self) -> None:
        for deg in (15.01, -15.01, math.nan, math.inf, -math.inf):
            with self.subTest(deg=deg), self.assertRaises(ValueError):
                yaw_grid(deg)
        for deg in (True, "3", None):
            with self.subTest(deg=deg), self.assertRaises(TypeError):
                yaw_grid(deg)

    def test_d6_up_to_15_degrees_passes(self) -> None:
        """Zwilling: die Grenzen selbst, eine ganze Zahl und 0 gehen durch."""
        for deg in (15.0, -15.0, 7, 0.0):
            with self.subTest(deg=deg):
                self.assertEqual(len(yaw_grid(deg)), 29)


class JawAndNeckTest(unittest.TestCase):
    """Kinnlinie und Verdrillung des Halses, von Hand gerechnet."""

    def test_jaw_line_has_35_points_sorted(self) -> None:
        self.assertEqual(len(JAWLINE), 35)
        xs = [p[0] for p in JAWLINE]
        self.assertEqual(xs, sorted(xs))

    def test_jaw_y_interpolates_and_holds_the_ends(self) -> None:
        self.assertEqual(jaw_y(0.0), 660.0)
        self.assertEqual(jaw_y(360.0), 660.0)
        self.assertAlmostEqual(jaw_y(390.0), 661.0, delta=EXACT)  # Mitte von 660 und 662
        self.assertAlmostEqual(jaw_y(585.0), 744.0, delta=EXACT)
        self.assertEqual(jaw_y(SRC), 662.0)
        with self.assertRaises(ValueError):
            jaw_y(math.nan)

    def test_neck_turns_fully_at_the_jaw_and_not_below(self) -> None:
        th = 12 * math.pi / 180
        # Halsmitte (a = 0) an der Kinnlinie: NECK_R · sin(th)
        at_jaw = neck_shift(NECK_CX, jaw_y(NECK_CX), th)
        self.assertAlmostEqual(at_jaw, NECK_R * math.sin(th), delta=EXACT)
        below = neck_shift(NECK_CX, jaw_y(NECK_CX) + NECK_LEN, th)
        self.assertAlmostEqual(below, 0.0, delta=EXACT)
        self.assertEqual(neck_shift(NECK_CX + NECK_R, 800.0, th), 0.0)  # auf der Kontur
        self.assertEqual(neck_shift(NECK_CX - 2 * NECK_R, 800.0, th), 0.0)
        with self.assertRaises(ValueError):
            neck_shift(NECK_CX, 800.0, math.inf)

    def test_yaw_shift_rejects_non_finite_input(self) -> None:
        for args in ((math.nan, 0.0, 0.1, 0.1), (0.0, 0.0, math.inf, 0.1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                yaw_shift(*args)


if __name__ == "__main__":
    unittest.main()
