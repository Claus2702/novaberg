"""Zeugen für das ganze Bild: Ebenen laden, Gesichtsebene verzerren, alles zusammensetzen.

Gezeichnet wird auf `RecordingContext`, der jeden Aufruf mit seinen Argumenten
mitschreibt — so wie ein Cairo-Kontext ihn empfinge. Statt PNG stehen
`FakeSurface`-Flächen, statt Cairo-Matrizen und neuer Flächen `FakeCanvas`, statt
des Dateisystems `FakeSource`. Kein Zeuge braucht pycairo, GTK, eine Datei oder
einen Bildschirm.

Die Zahlen der Verzerrung sind aus der Formel des Prototyps (`warpShift`) von Hand
gerechnet; die Rechnung steht jeweils daneben. Die Stichstellen liegen in
Gesichtsachsen um die Mundmitte: `lx` quer, `ly` längs nach unten, so gewählt,
dass jeder Smoothstep einen glatten Wert annimmt.
"""

import importlib
import math
import sys
import types
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

import avatar
from avatar import compose
from avatar.base_image import (
    JAW_TOLERANCE,
    WARP_TRIANGLES,
    WarpCache,
    affine,
    grown_triangle,
    render_warped,
    smooth01,
    warp_shift,
    warp_triangles,
    warped_face,
)
from avatar.compose import FaceTools, check_pose, draw_face
from avatar.drawing import MOUTH_CENTER
from avatar.drawing_tools import SRC, UX, UY
from avatar.face import NEUTRAL
from avatar.head_turn import YAW_TRIANGLES, draw_turned, yaw_grid, yaw_triangles
from avatar.layers import AvatarLayers, LayerError, load_layers
from avatar.pose import Pose

EXACT = 1e-9
SIZE = 600
IMAGE_DIR = Path("/avatar-bilder")  # synthetisch; FakeSource kennt nur diesen Pfad
COMPOSE_MODULES = (
    "avatar.base_image",
    "avatar.compose",
    "avatar.head_turn",
    "avatar.layers",
    "avatar.pose",
)


class RecordingContext:
    """Ein Ersatz für `cairo.Context`, der jeden Aufruf als (Name, Argumente) mitschreibt."""

    def __init__(self) -> None:
        """Beginnt mit leerer Aufrufliste."""
        self.calls: list[tuple[str, tuple]] = []

    def __getattr__(self, name: str) -> object:
        """Jede Methode des Kontexts: schreibt Name und Argumente mit, gibt nichts zurück."""
        if name.startswith("__"):
            raise AttributeError(name)

        def record(*args: object) -> None:
            self.calls.append((name, args))

        return record

    def names(self) -> list[str]:
        """Die Namen aller Aufrufe in Reihenfolge."""
        return [name for name, _ in self.calls]


class FakeSurface:
    """Eine Fläche mit Größe und Format, wie `cairo.ImageSurface` sie meldet."""

    def __init__(self, label: str, width: int = 900, height: int = 900, fmt: int = 0) -> None:
        """Merkt Name, Größe und Format (0 = ARGB32, 1 = RGB24)."""
        self.label, self.width, self.height, self.fmt = label, width, height, fmt

    def get_width(self) -> int:
        """Breite in Pixeln."""
        return self.width

    def get_height(self) -> int:
        """Höhe in Pixeln."""
        return self.height

    def get_format(self) -> int:
        """Format als Zahl."""
        return self.fmt

    def __repr__(self) -> str:
        """Der Name, damit Meldungen lesbar bleiben."""
        return f"FakeSurface({self.label})"


class FakeCanvas:
    """Ersatz für `CairoCanvas`: neue Flächen mit aufzeichnendem Kontext, Matrizen als Tupel."""

    def __init__(self) -> None:
        """Beginnt ohne Flächen."""
        self.surfaces: list[FakeSurface] = []
        self.contexts: list[RecordingContext] = []

    def new_surface(self, width: int, height: int) -> tuple[FakeSurface, RecordingContext]:
        """Eine neue Fläche und ihr Kontext; beide werden gemerkt."""
        surface = FakeSurface(f"warped{len(self.surfaces)}", width, height)
        ctx = RecordingContext()
        self.surfaces.append(surface)
        self.contexts.append(ctx)
        return surface, ctx

    def matrix(self, coefficients: tuple) -> tuple:
        """Die Matrix als markiertes Tupel."""
        return ("matrix", coefficients)


class RecordingGradients:
    """Ersatz für `CairoGradients`: ein Verlauf ist ein markiertes Tupel."""

    def radial(self, inner: tuple, outer: tuple, stops: tuple) -> tuple:
        """Radialer Verlauf als Tupel."""
        return ("radial", inner, outer, tuple(stops))

    def linear(self, start: tuple, end: tuple, stops: tuple) -> tuple:
        """Linearer Verlauf als Tupel."""
        return ("linear", start, end, tuple(stops))


class FakeSource:
    """Ersatz für `CairoPngSource`: ein Verzeichnis mit Flächen statt Dateien."""

    def __init__(self, surfaces: dict[str, object], directories: set[str]) -> None:
        """`surfaces` nach Dateiname; ein Wert `None` heißt: Datei da, aber kein PNG."""
        self.surfaces, self.directories = surfaces, directories

    def is_dir(self, path: Path) -> bool:
        """Wahr für die bekannten Verzeichnisse."""
        return str(path) in self.directories

    def is_file(self, path: Path) -> bool:
        """Wahr für die bekannten Dateien im bekannten Verzeichnis."""
        return path.parent == IMAGE_DIR and path.name in self.surfaces

    def read(self, path: Path) -> object:
        """Die Fläche zur Datei; `None` meldet sich wie ein unlesbares PNG."""
        surface = self.surfaces[path.name]
        if surface is None:
            raise LayerError(f"read: {path} ist kein lesbares PNG")
        return surface


def _nine() -> dict[str, object]:
    """Neun passende Flächen; die Halsebenen ohne Alphakanal, wie es erlaubt ist."""
    images: dict[str, object] = {}
    for kind in ("base", "neck", "face"):
        for i in range(3):
            images[f"{kind}{i}.png"] = FakeSurface(f"{kind}{i}", fmt=1 if kind == "neck" else 0)
    return images


def _layers() -> AvatarLayers:
    return load_layers(IMAGE_DIR, FakeSource(_nine(), {str(IMAGE_DIR)}))


def _tools() -> FaceTools:
    return FaceTools(RecordingGradients(), FakeCanvas(), WarpCache())


def _pose(**changes: object) -> Pose:
    pose = Pose(face=NEUTRAL, tongue=0.0, blink=1.0, breath=0.0, boil_tick=0)
    return replace(pose, **changes)


def _at(lx: float, ly: float) -> tuple[float, float]:
    """Der Punkt in Gesichtsachsen um die Mundmitte: quer `lx`, längs `ly` nach unten."""
    return (
        MOUTH_CENTER[0] + lx * UX - ly * UY,
        MOUTH_CENTER[1] + lx * UY + ly * UX,
    )


def _clips(ctx: RecordingContext) -> list[tuple]:
    """Die Ecken jedes Clips in Reihenfolge: je ein `move_to` und zwei `line_to`."""
    points = [args for name, args in ctx.calls if name in ("move_to", "line_to")]
    return [tuple(points[k : k + 3]) for k in range(0, len(points), 3)]


def _assert_grown(test: unittest.TestCase, clip: tuple, dest: tuple) -> None:
    """Jede Ecke des Clips liegt 1,6 weiter vom Schwerpunkt, auf der Geraden durch die Ecke."""
    cx, cy = sum(p[0] for p in dest) / 3, sum(p[1] for p in dest) / 3
    for (gx, gy), (dx, dy) in zip(clip, dest, strict=True):
        before, after = math.hypot(dx - cx, dy - cy), math.hypot(gx - cx, gy - cy)
        test.assertAlmostEqual(after - before, 1.6, delta=EXACT)
        test.assertAlmostEqual((dx - cx) * (gy - cy) - (dy - cy) * (gx - cx), 0.0, delta=1e-6)


class SmoothTest(unittest.TestCase):
    """`smooth01` ist der Smoothstep des Prototyps, begrenzt auf 0..1."""

    def test_inside_is_smoothstep(self) -> None:
        self.assertEqual(smooth01(0, 130, 65), 0.5)  # t = 0,5 → 0,25 · 2
        # t = 65/80 = 0,8125 → 0,66015625 · 1,375
        self.assertAlmostEqual(smooth01(60, 140, 125), 0.90771484375, delta=EXACT)

    def test_clamped_outside(self) -> None:
        self.assertEqual(smooth01(0, 130, -10), 0.0)
        self.assertEqual(smooth01(0, 130, 200), 1.0)
        self.assertEqual(smooth01(260, 340, 0), 0.0)

    def test_equal_bounds_or_nan_rejected(self) -> None:
        with self.assertRaises(ValueError):
            smooth01(5, 5, 1)
        with self.assertRaises(ValueError):
            smooth01(0, 1, math.nan)


class WarpShiftTest(unittest.TestCase):
    """`warp_shift` an Stichstellen, von Hand nach `warpShift` gerechnet."""

    def test_mouth_axis_half_way(self) -> None:
        # ly = 65: Kinn-Gewicht smooth01(0, 130, 65) = 0,5; Hals und Seite 1; Nase voll 5
        self.assertAlmostEqual(warp_shift(*_at(0, 65), 40), 10.0, delta=EXACT)  # 10 · 0,5 + 5
        self.assertAlmostEqual(warp_shift(*_at(0, 65), 0), -10.0, delta=EXACT)  # −30 · 0,5 + 5

    def test_neck_fade(self) -> None:
        # ly = 300: Hals smooth01(260, 340, 300) = 0,5 → Faktor 0,5 auf Kinn (10) und Nase (5)
        self.assertAlmostEqual(warp_shift(*_at(0, 300), 40), 7.5, delta=EXACT)

    def test_side_fade(self) -> None:
        # lx = 125: Kinn 10 · 0,5 · (1 − smooth01(80, 170, 125) = 0,5) = 2,5;
        # Nase 5 · (1 − 0,90771484375) = 0,46142578125
        self.assertAlmostEqual(warp_shift(*_at(125, 65), 40), 2.96142578125, delta=EXACT)

    def test_template_jaw_leaves_only_the_nose(self) -> None:
        # jaw = JAW_TEMPLATE: der Anteil des Kinns verschwindet, die Nase bleibt (5)
        self.assertAlmostEqual(warp_shift(*_at(0, 65), 30), 5.0, delta=EXACT)
        self.assertAlmostEqual(warp_shift(*_at(0, 200), 30), 5.0, delta=EXACT)

    def test_far_regions_stay_unmoved(self) -> None:
        # Über der Nase (ly −200), im Hals (ly 400) und seitlich (lx 200) ist es die Identität
        for jaw in (0.0, 40.0, 80.0):
            for point in (_at(0, -200), _at(0, 400), _at(200, 65), _at(-200, 65)):
                self.assertEqual(warp_shift(*point, jaw), 0.0, (point, jaw))

    def test_non_finite_rejected(self) -> None:
        with self.assertRaises(ValueError):
            warp_shift(500.0, 500.0, math.inf)


class TrianglesTest(unittest.TestCase):
    """Gitter, affine Abbildung und Clip je Dreieck."""

    def test_every_triangle_maps_source_onto_dest(self) -> None:
        triangles = warp_triangles(40.0)
        self.assertEqual(len(triangles), 338)  # 13 · 13 Zellen, je zwei Dreiecke
        self.assertEqual(WARP_TRIANGLES, 338)
        for triangle in triangles:
            a, b, c, d, e, f = affine(triangle.source, triangle.dest)
            for (sx, sy), (dx, dy) in zip(triangle.source, triangle.dest, strict=True):
                self.assertAlmostEqual(a * sx + c * sy + e, dx, delta=1e-6)
                self.assertAlmostEqual(b * sx + d * sy + f, dy, delta=1e-6)

    def test_source_is_dest_shifted_up_the_face_axis(self) -> None:
        # Gitterpunkt i = 6, j = 5: (360 + 520 · 6/13, 380 + 500 · 5/13) = (600, 572,307…)
        triangles = warp_triangles(40.0)
        cell = triangles[2 * (5 * 13 + 6)]
        x, y = cell.dest[0]
        self.assertAlmostEqual(x, 600.0, delta=EXACT)
        self.assertAlmostEqual(y, 380 + 500 * 5 / 13, delta=EXACT)
        shift = warp_shift(x, y, 40.0)
        self.assertGreater(shift, 5.0)  # Kinn und Nase schieben hier beide nach unten
        self.assertAlmostEqual(cell.source[0][0], x + UY * shift, delta=EXACT)
        self.assertAlmostEqual(cell.source[0][1], y - UX * shift, delta=EXACT)

    def test_affine_of_a_known_triangle(self) -> None:
        # (0,0) → (2,3), (1,0) → (4,3), (0,1) → (2,6): x' = 2x + 2, y' = 3y + 3
        result = affine(((0, 0), (1, 0), (0, 1)), ((2, 3), (4, 3), (2, 6)))
        for got, want in zip(result, (2, 0, 0, 3, 2, 3), strict=True):
            self.assertAlmostEqual(got, want, delta=EXACT)

    def test_flat_source_rejected(self) -> None:
        with self.assertRaises(ValueError):
            affine(((0, 0), (1, 1), (2, 2)), ((0, 0), (1, 0), (0, 1)))

    def test_clip_grows_away_from_the_centroid(self) -> None:
        # Angepasst mit der radialen Nahtkorrektur: Bis dahin rückte jede Koordinate je
        # Achse um 0,6 (Math.sign), erwartet waren (−0,6, −0,6), (2,6, −0,6), (1, 3,6).
        # Schwerpunkt (1, 1); jede Ecke rückt 1,6 entlang der Geraden vom Schwerpunkt
        # weg: (0, 0) und (2, 0) liegen √2 von ihm, (1, 3) genau 2 über ihm.
        g = 1.6 / math.sqrt(2)
        grown = grown_triangle(((0, 0), (2, 0), (1, 3)))
        want = ((-g, -g), (2 + g, -g), (1.0, 4.6))
        for got_point, want_point in zip(grown, want, strict=True):
            for got, expected in zip(got_point, want_point, strict=True):
                self.assertAlmostEqual(got, expected, delta=EXACT)

    def test_clip_widens_the_diagonal_too(self) -> None:
        # Die halbe Gitterzelle (0, 0), (1, 0), (0, 1) mit der Diagonale x + y = 1.
        # Achsenweise um 0,6 blieben (1, 0) → (1,6, −0,6) und (0, 1) → (−0,6, 1,6) auf
        # ihr; radial rücken beide um 1,6/√5 ≈ 0,72 über sie hinaus.
        grown = grown_triangle(((0, 0), (1, 0), (0, 1)))
        for x, y in grown[1:]:
            self.assertAlmostEqual(x + y - 1, 1.6 / math.sqrt(5), delta=EXACT)

    def test_chin_clip_corners_grow_radially(self) -> None:
        canvas = FakeCanvas()
        render_warped(canvas, FakeSurface("face0"), 40.0)
        triangles = warp_triangles(40.0)
        clips = _clips(canvas.contexts[0])
        self.assertEqual(len(clips), len(triangles))
        for clip, triangle in zip(clips, triangles, strict=True):
            _assert_grown(self, clip, triangle.dest)

    def test_render_draws_all_triangles_clipped(self) -> None:
        canvas, layer = FakeCanvas(), FakeSurface("face0")
        surface = render_warped(canvas, layer, 40.0)
        self.assertIs(surface, canvas.surfaces[0])
        self.assertEqual((surface.width, surface.height), (900, 900))
        ctx = canvas.contexts[0]
        self.assertEqual(ctx.calls[0], ("scale", (900 / SRC, 900 / SRC)))
        names = ctx.names()
        self.assertEqual(names.count("clip"), 338)
        self.assertEqual(names.count("paint"), 338)
        self.assertEqual(names.count("save"), names.count("restore"))
        sources = [args for name, args in ctx.calls if name == "set_source_surface"]
        self.assertTrue(all(args == (layer, 0, 0) for args in sources))
        # Jede Abbildung wird vor dem Malen gesetzt, und zwar die des Dreiecks
        first = warp_triangles(40.0)[0]
        transforms = [args[0] for name, args in ctx.calls if name == "transform"]
        self.assertEqual(transforms[0], ("matrix", affine(first.source, first.dest)))


class CacheTest(unittest.TestCase):
    """Die verzerrte Ebene wird nur bei anderem Kiefer oder anderer Ebene neu gerechnet."""

    def setUp(self) -> None:
        self.cache, self.canvas, self.layer = WarpCache(), FakeCanvas(), FakeSurface("face0")

    def test_same_jaw_renders_once(self) -> None:
        first = warped_face(self.cache, self.canvas, self.layer, 0, 40.0)
        second = warped_face(self.cache, self.canvas, self.layer, 0, 40.0)
        self.assertIs(first, second)
        self.assertEqual(self.cache.renders, 1)
        self.assertEqual(len(self.canvas.surfaces), 1)

    def test_change_within_tolerance_renders_once(self) -> None:
        warped_face(self.cache, self.canvas, self.layer, 0, 40.0)
        warped_face(self.cache, self.canvas, self.layer, 0, 40.0 + JAW_TOLERANCE / 2)
        self.assertEqual(self.cache.renders, 1)

    def test_other_jaw_renders_again(self) -> None:
        first = warped_face(self.cache, self.canvas, self.layer, 0, 40.0)
        second = warped_face(self.cache, self.canvas, self.layer, 0, 40.0 + 2 * JAW_TOLERANCE)
        self.assertIsNot(first, second)
        self.assertEqual(self.cache.renders, 2)
        self.assertEqual(self.cache.entries[0].jaw, 40.0 + 2 * JAW_TOLERANCE)

    def test_other_layer_renders_again(self) -> None:
        warped_face(self.cache, self.canvas, self.layer, 0, 40.0)
        warped_face(self.cache, self.canvas, FakeSurface("face0-neu"), 0, 40.0)
        self.assertEqual(self.cache.renders, 2)

    def test_variants_are_cached_separately(self) -> None:
        layers, tools = _layers(), _tools()
        for tick in range(6):
            draw_face(RecordingContext(), SIZE, _pose(boil_tick=tick), layers, tools)
        self.assertEqual(tools.warp_cache.renders, 3)  # Takt 3–5 nutzen die Fassungen 0–2


class LayersTest(unittest.TestCase):
    """`load_layers`: neun Ebenen oder ein lauter Fehler mit Pfad."""

    def test_all_nine_loaded(self) -> None:
        images = _nine()
        layers = load_layers(IMAGE_DIR, FakeSource(images, {str(IMAGE_DIR)}))
        for kind in ("base", "neck", "face"):
            got = getattr(layers, kind)
            self.assertEqual(got, tuple(images[f"{kind}{i}.png"] for i in range(3)))

    def test_missing_directory_is_loud(self) -> None:
        with self.assertRaises(LayerError) as caught:
            load_layers(IMAGE_DIR, FakeSource(_nine(), set()))
        self.assertIn(str(IMAGE_DIR), str(caught.exception))

    def test_missing_image_is_loud(self) -> None:
        images = _nine()
        del images["neck2.png"]
        with self.assertRaises(LayerError) as caught:
            load_layers(IMAGE_DIR, FakeSource(images, {str(IMAGE_DIR)}))
        self.assertIn(str(IMAGE_DIR / "neck2.png"), str(caught.exception))

    def test_wrong_size_is_loud(self) -> None:
        images = _nine()
        images["base1.png"] = FakeSurface("base1", width=899)
        with self.assertRaises(LayerError) as caught:
            load_layers(IMAGE_DIR, FakeSource(images, {str(IMAGE_DIR)}))
        self.assertIn(str(IMAGE_DIR / "base1.png"), str(caught.exception))
        self.assertIn("899", str(caught.exception))

    def test_face_without_alpha_is_loud(self) -> None:
        # Zwilling: die Halsebenen in _nine() sind RGB24 und laden (test_all_nine_loaded)
        images = _nine()
        images["face0.png"] = FakeSurface("face0", fmt=1)
        with self.assertRaises(LayerError) as caught:
            load_layers(IMAGE_DIR, FakeSource(images, {str(IMAGE_DIR)}))
        self.assertIn(str(IMAGE_DIR / "face0.png"), str(caught.exception))

    def test_unreadable_png_is_loud(self) -> None:
        images = _nine()
        images["face2.png"] = None
        with self.assertRaises(LayerError) as caught:
            load_layers(IMAGE_DIR, FakeSource(images, {str(IMAGE_DIR)}))
        self.assertIn(str(IMAGE_DIR / "face2.png"), str(caught.exception))

    def test_directory_must_be_a_path(self) -> None:
        with self.assertRaises(ValueError):
            load_layers(str(IMAGE_DIR), FakeSource(_nine(), {str(IMAGE_DIR)}))


class ComposeTest(unittest.TestCase):
    """`draw_face` setzt das Bild in der Reihenfolge von `frame` zusammen."""

    def _events(self, cr: RecordingContext, layers: AvatarLayers, tools: FaceTools) -> list:
        """Die Schritte des Bildes: Hintergrund, Ebenen, Teile — ohne die einzelnen Striche."""
        warped = set(map(id, tools.canvas.surfaces))
        events = []
        for name, args in cr.calls:
            if name == "rectangle":
                events.append("background")
            elif name == "set_source_surface" and args[0] in layers.neck:
                events.append("neck")
            elif name == "set_source_surface" and id(args[0]) in warped:
                events.append("face")
            elif name == "part":
                events.append(args[0])
        return events

    def test_order_like_frame(self) -> None:
        def marker(part: str) -> object:
            return lambda cr, *args: cr.calls.append(("part", (part,)))

        layers, tools, cr = _layers(), _tools(), RecordingContext()
        with (
            mock.patch.object(compose, "draw_brows", marker("brows")),
            mock.patch.object(compose, "draw_eyes", marker("eyes")),
            mock.patch.object(compose, "draw_mouth", marker("mouth")),
            mock.patch.object(compose, "draw_extras", marker("extras")),
        ):
            draw_face(cr, SIZE, _pose(), layers, tools)
        self.assertEqual(
            self._events(cr, layers, tools),
            ["background", "neck", "face", "brows", "eyes", "mouth", "extras"],
        )

    def test_real_parts_draw_on_top_of_the_face(self) -> None:
        layers, tools, cr = _layers(), _tools(), RecordingContext()
        face = replace(NEUTRAL, jaw=20.0, mouth_open=12.0, tear=0.8, blush=0.5)
        draw_face(cr, SIZE, _pose(face=face, tongue=0.5, blink=0.6, boil_tick=4), layers, tools)
        names = cr.names()
        face_paint = self._events(cr, layers, tools).index("face")
        self.assertEqual(face_paint, 2)
        last_surface = max(i for i, n in enumerate(names) if n == "set_source_surface")
        self.assertGreater(names[last_surface:].count("stroke"), 100)
        self.assertLess(names.index("set_line_cap"), names.index("stroke"))
        self.assertIn(("set_line_cap", (1,)), cr.calls)
        self.assertIn(("set_line_join", (1,)), cr.calls)
        self.assertEqual(names.count("save"), names.count("restore"))
        self.assertEqual(names[0], "save")
        self.assertEqual(names[-1], "restore")

    def test_background_colour(self) -> None:
        cr = RecordingContext()
        draw_face(cr, SIZE, _pose(), _layers(), _tools())
        rect = cr.names().index("rectangle")
        colour = (251 / 255, 251 / 255, 248 / 255, 1)  # #fbfbf8, deckend
        self.assertEqual(cr.calls[rect - 1], ("set_source_rgba", colour))
        self.assertEqual(cr.calls[rect], ("rectangle", (0, 0, SIZE, SIZE)))

    def test_variant_follows_the_tick(self) -> None:
        layers, tools = _layers(), _tools()
        for tick in range(6):
            cr = RecordingContext()
            draw_face(cr, SIZE, _pose(boil_tick=tick), layers, tools)
            painted = [args[0] for name, args in cr.calls if name == "set_source_surface"]
            self.assertIs(painted[0], layers.neck[tick % 3], tick)
            entry = tools.warp_cache.entries[tick % 3]
            self.assertIs(entry.source, layers.face[tick % 3], tick)
            self.assertIs(painted[1], entry.surface, tick)

    def test_breath_stretches_about_the_bottom_centre(self) -> None:
        for breath, sx, sy in ((1.0, 1.003, 1.005), (-1.0, 0.997, 0.995)):
            cr = RecordingContext()
            draw_face(cr, SIZE, _pose(breath=breath), _layers(), _tools())
            start = cr.names().index("translate")
            self.assertEqual(cr.calls[start], ("translate", (300.0, 600)))
            got_sx, got_sy = cr.calls[start + 1][1]
            self.assertAlmostEqual(got_sx, sx, delta=EXACT)
            self.assertAlmostEqual(got_sy, sy, delta=EXACT)
            self.assertEqual(cr.calls[start + 2], ("translate", (-300.0, -600)))
            self.assertEqual(cr.calls[start + 3], ("scale", (SIZE / SRC, SIZE / SRC)))

    def test_negative_jaw_warps_as_closed(self) -> None:
        tools, pose = _tools(), _pose(face=replace(NEUTRAL, jaw=-5.0))
        draw_face(RecordingContext(), SIZE, pose, _layers(), tools)
        self.assertEqual(tools.warp_cache.entries[0].jaw, 0.0)

    def test_tear_time_follows_the_tick(self) -> None:
        seen = []
        record = lambda cr, face, ms, tick: seen.append(ms)  # noqa: E731
        with mock.patch.object(compose, "draw_extras", record):
            draw_face(RecordingContext(), SIZE, _pose(boil_tick=7), _layers(), _tools())
        self.assertEqual(seen, [770.0])  # 7 Takte zu 110 ms

    def test_invalid_input_rejected(self) -> None:
        layers, tools = _layers(), _tools()
        for pose in (
            _pose(blink=1.5),
            _pose(breath=-1.1),
            _pose(tongue=math.nan),
            _pose(boil_tick=-1),
            _pose(face=replace(NEUTRAL, jaw=math.inf)),
        ):
            with self.assertRaises(ValueError, msg=repr(pose)):
                draw_face(RecordingContext(), SIZE, pose, layers, tools)
        for size in (0, 600.0, True):
            with self.assertRaises(ValueError, msg=repr(size)):
                draw_face(RecordingContext(), size, _pose(), layers, tools)
        self.assertEqual(tools.warp_cache.renders, 0)  # abgewiesen vor jeder Rechnung


class HeadYawPoseTest(unittest.TestCase):
    """Die Pose trägt den Kopf in Grad; `check_pose` lässt ±15° zu, endlich, als Zahl."""

    def test_head_yaw_outside_15_degrees_or_not_a_number_is_rejected(self) -> None:
        for yaw in (15.01, -15.01, math.nan, math.inf):
            with self.subTest(yaw=yaw), self.assertRaises(ValueError):
                check_pose(_pose(head_yaw=yaw), "Zeuge")
        for yaw in (True, "3"):
            with self.subTest(yaw=yaw), self.assertRaises(TypeError):
                check_pose(_pose(head_yaw=yaw), "Zeuge")

    def test_head_yaw_up_to_15_degrees_passes(self) -> None:
        """Zwilling: die Grenzen selbst, ganze Zahlen und der Vorgabewert 0 gehen durch."""
        for yaw in (15.0, -15.0, 7, 0.0):
            with self.subTest(yaw=yaw):
                check_pose(_pose(head_yaw=yaw), "Zeuge")
        self.assertEqual(_pose().head_yaw, 0.0)


class HeadTurnPathTest(unittest.TestCase):
    """`draw_face` bis 0,05° auf dem ungedrehten Weg, darüber durch das Drehgitter."""

    def test_up_to_0_05_degrees_the_path_is_unchanged(self) -> None:
        layers, tools = _layers(), _tools()
        straight = RecordingContext()
        draw_face(straight, SIZE, _pose(breath=0.4), layers, tools)
        for yaw in (0.05, -0.05):
            cr = RecordingContext()
            draw_face(cr, SIZE, _pose(breath=0.4, head_yaw=yaw), layers, tools)
            self.assertEqual(cr.calls, straight.calls, yaw)
        self.assertEqual(len(tools.canvas.surfaces), 1)  # nur die Kinnverzerrung

    def test_above_0_05_degrees_the_head_goes_through_an_intermediate_surface(self) -> None:
        """Zwilling: Bei 0,06° zeichnen die Züge auf die Zwischenfläche, nicht auf `cr`."""
        layers, tools, cr = _layers(), _tools(), RecordingContext()
        with mock.patch.object(compose, "_draw_head", wraps=compose._draw_head) as head:
            draw_face(cr, SIZE, _pose(breath=1.0, head_yaw=0.06), layers, tools)
        canvas = tools.canvas
        self.assertEqual(len(canvas.surfaces), 2)  # Kinnverzerrung, dann die Zwischenfläche
        surface, ctx = canvas.surfaces[1], canvas.contexts[1]
        self.assertEqual((surface.width, surface.height), (SIZE, SIZE))
        self.assertEqual(head.call_count, 1)
        self.assertIs(head.call_args.args[0], ctx)
        # Die Zwischenfläche: im Maßstab der Vorlage, ohne Atem; Hals, Gesicht, Züge
        self.assertEqual(ctx.calls[0], ("scale", (SIZE / SRC, SIZE / SRC)))
        self.assertNotIn(("translate", (300.0, 600)), ctx.calls)
        painted = [args[0] for name, args in ctx.calls if name == "set_source_surface"]
        self.assertIs(painted[0], layers.neck[0])
        self.assertIs(painted[1], canvas.surfaces[0])
        self.assertGreater(ctx.names().count("stroke"), 100)
        # Auf `cr`: Hintergrund, Atem, Maßstab, dann nur noch die Zwischenfläche
        names = cr.names()
        start = names.index("translate")
        got_sx, got_sy = cr.calls[start + 1][1]
        self.assertAlmostEqual(got_sx, 1.003, delta=EXACT)
        self.assertAlmostEqual(got_sy, 1.005, delta=EXACT)
        self.assertEqual(cr.calls[start + 3], ("scale", (SIZE / SRC, SIZE / SRC)))
        self.assertNotIn("stroke", names)
        self.assertEqual(names.count("save"), names.count("restore"))
        sources = [args[0] for name, args in cr.calls if name == "set_source_surface"]
        self.assertTrue(all(s is surface for s in sources))

    def test_above_0_05_degrees_only_the_moved_triangles_are_drawn(self) -> None:
        moved = sum(t.moved for t in yaw_triangles(yaw_grid(0.06)))
        self.assertGreater(moved, 0)
        self.assertLess(moved, YAW_TRIANGLES)
        cr = RecordingContext()
        draw_face(cr, SIZE, _pose(head_yaw=0.06), _layers(), _tools())
        names = cr.names()
        self.assertEqual(names.count("clip"), moved)
        self.assertEqual(names.count("set_source_surface"), moved + 1)  # dazu die Unterlage


class DrawTurnedTest(unittest.TestCase):
    """`draw_turned`: erst die Unterlage, dann nur die verschobenen Dreiecke, radial begrenzt."""

    def setUp(self) -> None:
        self.canvas, self.cr = FakeCanvas(), RecordingContext()
        self.head = FakeSurface("head", SIZE, SIZE)
        self.triangles = yaw_triangles(yaw_grid(12.0))
        self.moved = [t for t in self.triangles if t.moved]

    def test_underlay_then_only_the_moved_triangles(self) -> None:
        drawn = draw_turned(self.cr, self.canvas, self.head, self.triangles)
        self.assertEqual(drawn, len(self.moved))
        underlay = [
            ("save", ()),
            ("scale", (SRC / SIZE, SRC / SIZE)),
            ("set_source_surface", (self.head, 0, 0)),
            ("paint", ()),
            ("restore", ()),
        ]
        self.assertEqual(self.cr.calls[:5], underlay)
        self.assertEqual(self.cr.names().count("clip"), len(self.moved))
        transforms = [args[0] for name, args in self.cr.calls if name == "transform"]
        want = [("matrix", affine(t.warp.source, t.warp.dest)) for t in self.moved]
        self.assertEqual(transforms, want)

    def test_turn_clip_corners_grow_radially(self) -> None:
        draw_turned(self.cr, self.canvas, self.head, self.triangles)
        clips = _clips(self.cr)
        self.assertEqual(len(clips), len(self.moved))
        for clip, triangle in zip(clips, self.moved, strict=True):
            _assert_grown(self, clip, triangle.warp.dest)

    def test_empty_surface_or_wrong_count_rejected(self) -> None:
        with self.assertRaises(ValueError):
            draw_turned(self.cr, self.canvas, FakeSurface("leer", 0, 0), self.triangles)
        with self.assertRaises(ValueError):
            draw_turned(self.cr, self.canvas, self.head, self.triangles[:-1])
        self.assertEqual(self.cr.calls, [])  # abgewiesen vor dem ersten Strich


class WithoutCairoTest(unittest.TestCase):
    """Die Module laden ohne pycairo und ohne GTK; Cairo kommt erst mit dem ersten Objekt."""

    def _load_blocked(self) -> types.ModuleType:
        saved = {name: getattr(avatar, name.split(".")[1], None) for name in COMPOSE_MODULES}
        self.addCleanup(self._restore, saved)
        for name in COMPOSE_MODULES:
            sys.modules.pop(name, None)
        return importlib.import_module("avatar.compose")

    @staticmethod
    def _restore(saved: dict) -> None:
        for name, module in saved.items():
            if module is None:
                vars(avatar).pop(name.split(".")[1], None)
            else:
                setattr(avatar, name.split(".")[1], module)

    def test_modules_load_and_warp_without_cairo(self) -> None:
        with mock.patch.dict(sys.modules, {"cairo": None, "gi": None}):
            fresh = self._load_blocked()
            self.assertIsNot(fresh, compose)
            for name in COMPOSE_MODULES:
                self.assertNotIn("cairo", vars(sys.modules[name]))
            base_image = sys.modules["avatar.base_image"]
            self.assertEqual(len(base_image.warp_triangles(40.0)), 338)
            # Erst die echte Matrix braucht Cairo — und meldet sein Fehlen laut
            with self.assertRaises(ImportError):
                base_image.CairoCanvas().matrix((1.0, 0.0, 0.0, 1.0, 0.0, 0.0))

    def test_the_block_stops_a_cairo_import(self) -> None:
        # Zwilling: unter derselben Sperre scheitert ein Modul, das Cairo oben importiert
        with mock.patch.dict(sys.modules, {"cairo": None, "gi": None}):
            probe = types.ModuleType("probe")
            with self.assertRaises(ImportError):
                exec("import cairo", vars(probe))  # noqa: S102 — fester Text, kein fremder


if __name__ == "__main__":
    unittest.main()
