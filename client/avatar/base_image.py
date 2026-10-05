"""Grundbild: Gitterverzerrung der Gesichtsebene mit dem Kiefer.

Der Kiefer öffnet sich, indem die Gesichtsebene in einem Gitter von
`WARP_NX` × `WARP_NY` Zellen verzerrt wird, je Zelle zwei Dreiecke mit einer
affinen Abbildung. Die Verschiebung jedes Gitterpunkts (`warp_shift`) läuft entlang
der geneigten Gesichtsachse nach unten:

- das Kinn um `jaw − JAW_TEMPLATE`, denn die Vorlage zeigt den Kiefer schon um
  `JAW_TEMPLATE` Pixel geöffnet; bei kleinerem Kiefer schließt er sich also;
- die Partie unter der Nase immer um `NOSE_EXTRA` Pixel, unabhängig vom Kiefer —
  eine feste Korrektur der Proportionen. Bei keinem Kieferwert ist die
  Verzerrung deshalb die Identität; nur bei `jaw = JAW_TEMPLATE` verschwindet der
  Anteil des Kinns.

Zur Seite (Kieferwinkel) und zum Hals hin klingt die Verschiebung weich aus
(`smooth01`); unter der Kinnlinie ist die Gesichtsebene durchsichtig, dort liegt
die feste Halsebene.

Die verzerrte Ebene wird nur neu gerechnet, wenn sich der Kiefer um mehr als
`JAW_TOLERANCE` ändert oder eine andere Fassung der Ebene kommt; den
Zwischenspeicher (`WarpCache`) hält der Aufrufer.

Das Modul importiert Cairo nicht: Matrizen und neue Flächen baut ein
`Canvas`-Adapter (`CairoCanvas`, der Cairo erst beim ersten Aufruf lädt).
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from avatar.drawing import MOUTH_CENTER
from avatar.drawing_tools import SRC, UX, UY, Point

if TYPE_CHECKING:
    import cairo

Triangle = tuple[Point, Point, Point]
# Koeffizienten wie `ctx.transform(a, b, c, d, e, f)` im Browser und `cairo.Matrix`:
# x' = a·x + c·y + e, y' = b·x + d·y + f
Affine = tuple[float, float, float, float, float, float]

JAW_TEMPLATE = 30.0  # um so viele Pixel ist der Kiefer in der Vorlage geöffnet
NOSE_EXTRA = 5.0  # feste Verlängerung der Partie unter der Nase, in Pixeln
WARP_X0, WARP_X1 = 360.0, 880.0  # verzerrter Ausschnitt, in Pixeln der Vorlage
WARP_Y0, WARP_Y1 = 380.0, 880.0
WARP_NX = 13
WARP_NY = 13
WARP_TRIANGLES = WARP_NX * WARP_NY * 2
# Clip je Dreieck radial um so viele Pixel vergrößert, gegen Haarrisse zwischen den Dreiecken
CLIP_GROW = 1.6
JAW_TOLERANCE = 0.05  # Kieferänderung in Pixeln, unter der die Ebene nicht neu gerechnet wird
DEGENERATE = 1e-9  # kleinere Fläche (doppelt) heißt: Dreieck ohne Fläche


@dataclass(frozen=True)
class WarpTriangle:
    """Ein Dreieck des Gitters: woher das Bild kommt und wohin es gezeichnet wird."""

    source: Triangle
    dest: Triangle


@dataclass
class WarpEntry:
    """Eine verzerrte Fassung: aus welcher Ebene, bei welchem Kiefer, mit welcher Fläche."""

    source: object
    jaw: float
    surface: object


@dataclass
class WarpCache:
    """Zwischenspeicher der verzerrten Gesichtsebene je Fassung; der Aufrufer hält ihn."""

    entries: dict[int, WarpEntry] = field(default_factory=dict)
    renders: int = 0  # wie oft eine Ebene neu verzerrt wurde


class Canvas(Protocol):
    """Baut, was Cairo als Objekt verlangt: neue Flächen und Matrizen."""

    def new_surface(self, width: int, height: int) -> tuple[object, "cairo.Context"]:
        """Eine leere, durchsichtige Fläche und ein Kontext darauf."""
        ...

    def matrix(self, coefficients: Affine) -> object:
        """Eine Matrix für `cr.transform`."""
        ...


class CairoCanvas:
    """Flächen und Matrizen mit Cairo; Cairo wird erst beim ersten Aufruf geladen."""

    def new_surface(self, width: int, height: int) -> tuple[object, "cairo.Context"]:
        """Eine `cairo.ImageSurface` im Format ARGB32 und ihr Kontext.

        Vorbedingung: Breite und Höhe ganze Zahlen > 0.
        Nachbedingung: Fläche in der verlangten Größe, ganz durchsichtig.
        Fehlerfälle: ValueError bei verletzter Vorbedingung; ImportError ohne pycairo.
        """
        # ── Eingabe-Validierung ──
        if not all(isinstance(v, int) and v > 0 for v in (width, height)):
            raise ValueError(f"new_surface: Größe {width!r} × {height!r} ungültig")

        # ── Verarbeitung ──
        import cairo  # erst hier, damit das Modul ohne pycairo lädt

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

        # ── Ausgabe-Verifikation ──
        if (surface.get_width(), surface.get_height()) != (width, height):
            raise RuntimeError("new_surface: Fläche hat nicht die verlangte Größe")
        return surface, cairo.Context(surface)

    def matrix(self, coefficients: Affine) -> object:
        """Eine `cairo.Matrix` aus den sechs Koeffizienten.

        Vorbedingung: sechs endliche Zahlen.
        Nachbedingung: die Matrix trägt sie in der Reihenfolge von `cairo.Matrix`.
        Fehlerfälle: ValueError bei verletzter Vorbedingung; ImportError ohne pycairo.
        """
        # ── Eingabe-Validierung ──
        if len(coefficients) != 6 or not all(math.isfinite(v) for v in coefficients):
            raise ValueError(f"matrix: Koeffizienten {coefficients!r} ungültig")

        # ── Verarbeitung ──
        import cairo  # erst hier, damit das Modul ohne pycairo lädt

        result = cairo.Matrix(*coefficients)

        # Keine Ausgabe-Verifikation: cairo.Matrix übernimmt die sechs Werte unverändert.
        return result


def smooth01(low: float, high: float, value: float) -> float:
    """Weicher Übergang von 0 bei `low` nach 1 bei `high` (Smoothstep), begrenzt auf 0..1.

    Vorbedingung: alle drei endlich, `low` ≠ `high`.
    Nachbedingung: Ergebnis in 0..1; 0 bis `low`, 1 ab `high` (bei `low` < `high`).
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    if not all(math.isfinite(v) for v in (low, high, value)) or low == high:
        raise ValueError(f"smooth01: {low!r}, {high!r}, {value!r} ungültig")

    # ── Verarbeitung ──
    t = max(0.0, min(1.0, (value - low) / (high - low)))
    result = t * t * (3 - 2 * t)

    # ── Ausgabe-Verifikation ──
    if not 0.0 <= result <= 1.0:
        raise RuntimeError(f"smooth01: Ergebnis {result} außerhalb 0..1")
    return result


def warp_shift(x: float, y: float, jaw: float) -> float:
    """Verschiebung des Punkts (x, y) entlang der Gesichtsachse nach unten, in Pixeln.

    Achsen: `lx` quer, `ly` längs der um 9° geneigten Gesichtsachse, gemessen von
    der Mundmitte, `ly` positiv nach unten.
    Vorbedingung: alle drei endlich; `jaw` die Kieferöffnung in Pixeln.
    Nachbedingung: Anteil des Kinns `(jaw − JAW_TEMPLATE)`, gewichtet nach `ly`
    (0..130), zum Hals hin (`ly` 260..340) und zur Seite (|`lx`| 80..170) auslaufend;
    dazu `NOSE_EXTRA` unterhalb der Nase (`ly` −150..−65), zur Seite (|`lx`| 60..140)
    und zum Hals hin auslaufend.
    Fehlerfälle: ValueError bei nicht endlicher Eingabe.
    """
    # ── Eingabe-Validierung ──
    if not all(math.isfinite(v) for v in (x, y, jaw)):
        raise ValueError(f"warp_shift: ({x!r}, {y!r}), Kiefer {jaw!r} nicht endlich")

    # ── Verarbeitung ──
    dx, dy = x - MOUTH_CENTER[0], y - MOUTH_CENTER[1]
    lx = dx * UX + dy * UY
    ly = -dx * UY + dy * UX
    neck_fade = 1 - smooth01(260, 340, ly)
    chin = (
        (jaw - JAW_TEMPLATE)
        * smooth01(0, 130, ly)
        * neck_fade
        * (1 - smooth01(80, 170, abs(lx)))
    )
    nose = NOSE_EXTRA * smooth01(-150, -65, ly) * neck_fade * (1 - smooth01(60, 140, abs(lx)))
    shift = chin + nose

    # ── Ausgabe-Verifikation ──
    if not math.isfinite(shift):
        raise RuntimeError(f"warp_shift: Verschiebung {shift} nicht endlich")
    return shift


def warp_triangles(jaw: float) -> list[WarpTriangle]:
    """Die Dreiecke des Gitters für einen Kiefer, wie `baseWarpDraw` im Prototyp.

    Das Zielgitter ist regelmäßig; der Quellpunkt ist der Zielpunkt minus der
    Verschiebung entlang der Gesichtsachse (für kleine Verschiebungen ausreichend).
    Vorbedingung: `jaw` endlich.
    Nachbedingung: `WARP_TRIANGLES` Dreiecke, zeilenweise, je Zelle erst das obere
    linke, dann das untere rechte.
    Fehlerfälle: ValueError bei nicht endlichem Kiefer.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(jaw):
        raise ValueError(f"warp_triangles: Kiefer {jaw!r} nicht endlich")

    # ── Verarbeitung ──
    grid: list[list[tuple[Point, Point]]] = []
    for j in range(WARP_NY + 1):
        row = []
        for i in range(WARP_NX + 1):
            x = WARP_X0 + (WARP_X1 - WARP_X0) * i / WARP_NX
            y = WARP_Y0 + (WARP_Y1 - WARP_Y0) * j / WARP_NY
            shift = warp_shift(x, y, jaw)
            row.append(((x, y), (x + UY * shift, y - UX * shift)))
        grid.append(row)
    triangles = []
    for j in range(WARP_NY):
        for i in range(WARP_NX):
            p, q, r, u = grid[j][i], grid[j][i + 1], grid[j + 1][i], grid[j + 1][i + 1]
            triangles.append(WarpTriangle(source=(p[1], q[1], r[1]), dest=(p[0], q[0], r[0])))
            triangles.append(WarpTriangle(source=(q[1], u[1], r[1]), dest=(q[0], u[0], r[0])))

    # ── Ausgabe-Verifikation ──
    if len(triangles) != WARP_TRIANGLES:
        raise RuntimeError(f"warp_triangles: {len(triangles)} statt {WARP_TRIANGLES} Dreiecke")
    return triangles


def affine(source: Triangle, dest: Triangle) -> Affine:
    """Die affine Abbildung, die `source` Ecke für Ecke auf `dest` legt.

    Vorbedingung: zwei Dreiecke aus endlichen Punkten, `source` mit Fläche.
    Nachbedingung: Koeffizienten (a, b, c, d, e, f) mit
    `(a·x + c·y + e, b·x + d·y + f)` = Ecke von `dest` für jede Ecke von `source`.
    Fehlerfälle: ValueError bei nicht endlichen Punkten oder flachem Quelldreieck.
    """
    # ── Eingabe-Validierung ──
    _check_triangle(source, "affine")
    _check_triangle(dest, "affine")
    (sx0, sy0), (sx1, sy1), (sx2, sy2) = source
    den = sx0 * (sy1 - sy2) + sx1 * (sy2 - sy0) + sx2 * (sy0 - sy1)
    if abs(den) < DEGENERATE:
        raise ValueError(f"affine: Quelldreieck {source!r} ohne Fläche")

    # ── Verarbeitung ──
    (dx0, dy0), (dx1, dy1), (dx2, dy2) = dest
    a = (dx0 * (sy1 - sy2) + dx1 * (sy2 - sy0) + dx2 * (sy0 - sy1)) / den
    b = (dy0 * (sy1 - sy2) + dy1 * (sy2 - sy0) + dy2 * (sy0 - sy1)) / den
    c = (dx0 * (sx2 - sx1) + dx1 * (sx0 - sx2) + dx2 * (sx1 - sx0)) / den
    d = (dy0 * (sx2 - sx1) + dy1 * (sx0 - sx2) + dy2 * (sx1 - sx0)) / den
    cross = (sx1 * sy2 - sx2 * sy1, sx2 * sy0 - sx0 * sy2, sx0 * sy1 - sx1 * sy0)
    e = (dx0 * cross[0] + dx1 * cross[1] + dx2 * cross[2]) / den
    f = (dy0 * cross[0] + dy1 * cross[1] + dy2 * cross[2]) / den
    result = (a, b, c, d, e, f)

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for v in result):
        raise RuntimeError(f"affine: Koeffizienten {result!r} nicht endlich")
    return result


def grown_triangle(dest: Triangle) -> Triangle:
    """Das Zieldreieck, jede Ecke radial um `CLIP_GROW` vom Schwerpunkt weg geschoben.

    Wie `triangleDraw` im Prototyp: So wird jede Kante verbreitert, auch die
    Diagonale einer Gitterzelle; achsenweise geschoben bliebe sie liegen, und über
    ihr bliebe eine helle Naht.
    Vorbedingung: drei endliche Punkte.
    Nachbedingung: jede Ecke liegt auf der Geraden vom Schwerpunkt durch die Ecke,
    `CLIP_GROW` weiter von ihm entfernt; eine Ecke im Schwerpunkt bleibt, wo sie ist
    (`|| 1` im Prototyp).
    Fehlerfälle: ValueError bei nicht endlichen Punkten.
    """
    # ── Eingabe-Validierung ──
    _check_triangle(dest, "grown_triangle")

    # ── Verarbeitung ──
    cx = sum(p[0] for p in dest) / 3
    cy = sum(p[1] for p in dest) / 3
    grown = []
    for px, py in dest:
        vx, vy = px - cx, py - cy
        length = math.hypot(vx, vy) or 1.0
        grown.append((px + vx / length * CLIP_GROW, py + vy / length * CLIP_GROW))

    # ── Ausgabe-Verifikation ──
    for (px, py), (gx, gy) in zip(dest, grown, strict=True):
        before = math.hypot(px - cx, py - cy)
        if before > 0 and abs(math.hypot(gx - cx, gy - cy) - before - CLIP_GROW) > 1e-6:
            raise RuntimeError(f"grown_triangle: Ecke ({px}, {py}) nicht radial gewachsen")
    return tuple(grown)


def warped_face(
    cache: WarpCache, canvas: Canvas, layer: object, variant: int, jaw: float
) -> object:
    """Die verzerrte Gesichtsebene einer Fassung, aus dem Zwischenspeicher oder neu gerechnet.

    Neu gerechnet wird, wenn für `variant` nichts gespeichert ist, die Ebene eine
    andere ist oder der Kiefer um mehr als `JAW_TOLERANCE` vom gespeicherten abweicht.
    Vorbedingung: `variant` ganze Zahl ≥ 0, `jaw` endlich, `layer` eine Fläche.
    Nachbedingung: `cache.entries[variant]` trägt die zurückgegebene Fläche;
    `cache.renders` ist genau dann um eins gewachsen, wenn neu gerechnet wurde.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    if isinstance(variant, bool) or not isinstance(variant, int) or variant < 0:
        raise ValueError(f"warped_face: Fassung {variant!r} ungültig")
    if not math.isfinite(jaw):
        raise ValueError(f"warped_face: Kiefer {jaw!r} nicht endlich")

    # ── Verarbeitung ──
    entry = cache.entries.get(variant)
    if entry is not None and entry.source is layer and abs(entry.jaw - jaw) <= JAW_TOLERANCE:
        return entry.surface
    entry = WarpEntry(source=layer, jaw=jaw, surface=render_warped(canvas, layer, jaw))
    cache.entries[variant] = entry
    cache.renders += 1

    # ── Ausgabe-Verifikation ──
    if cache.entries[variant] is not entry:
        raise RuntimeError("warped_face: Zwischenspeicher nicht beschrieben")
    return entry.surface


def render_warped(canvas: Canvas, layer: object, jaw: float) -> object:
    """Zeichnet die Ebene verzerrt auf eine neue Fläche derselben Größe, wie `baseWarpDraw`.

    Vorbedingung: `layer` eine Fläche mit Breite und Höhe > 0, `jaw` endlich.
    Nachbedingung: auf der neuen Fläche liegen alle `WARP_TRIANGLES` Dreiecke; außerhalb
    des Ausschnitts `WARP_X0..WARP_X1` × `WARP_Y0..WARP_Y1` bleibt sie durchsichtig.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    width, height = layer.get_width(), layer.get_height()
    if width <= 0 or height <= 0:
        raise ValueError(f"render_warped: Ebene {width} × {height} leer")
    triangles = warp_triangles(jaw)

    # ── Verarbeitung ──
    surface, ctx = canvas.new_surface(width, height)
    ctx.scale(width / SRC, height / SRC)
    for triangle in triangles:
        draw_triangle(ctx, canvas, layer, triangle)

    # ── Ausgabe-Verifikation ──
    if (surface.get_width(), surface.get_height()) != (width, height):
        raise RuntimeError("render_warped: Fläche hat nicht die Größe der Ebene")
    return surface


def paint_layer(cr: "cairo.Context", surface: object) -> None:
    """Malt eine Fläche auf `SRC` × `SRC` Pixel der Vorlage gestreckt, wie `drawImage`.

    Vorbedingung: `surface` mit Breite und Höhe > 0.
    Nachbedingung: `cr` steht nach dem Malen wieder wie vorher (`save`/`restore`).
    Fehlerfälle: ValueError bei leerer Fläche.
    """
    # ── Eingabe-Validierung ──
    width, height = surface.get_width(), surface.get_height()
    if width <= 0 or height <= 0:
        raise ValueError(f"paint_layer: Fläche {width} × {height} leer")

    # ── Verarbeitung ──
    cr.save()
    cr.scale(SRC / width, SRC / height)
    cr.set_source_surface(surface, 0, 0)
    cr.paint()
    cr.restore()

    # Keine Ausgabe-Verifikation: save und restore stehen paarweise; Cairo prüft die
    # Fläche beim Malen selbst.


def draw_triangle(
    ctx: "cairo.Context", canvas: Canvas, layer: object, triangle: WarpTriangle
) -> None:
    """Ein Dreieck: auf das vergrößerte Zieldreieck begrenzen, Ebene affin abgebildet malen.

    `ctx` steht in Pixeln der Vorlage; `layer` wird wie in `paint_layer` auf `SRC` ×
    `SRC` gestreckt und mit der Abbildung von `triangle.source` auf `triangle.dest`
    gemalt. Gilt für die Kinnverzerrung und die Kopfdrehung.
    Vorbedingung: Quelle mit Fläche, alle Ecken endlich, `layer` eine Fläche.
    Nachbedingung: `ctx` steht danach wieder wie vorher (`save`/`restore`).
    Fehlerfälle: ValueError aus `grown_triangle` und `affine`.
    """
    # ── Eingabe-Validierung ──
    clip = grown_triangle(triangle.dest)
    coefficients = affine(triangle.source, triangle.dest)

    # ── Verarbeitung ──
    ctx.save()
    ctx.move_to(*clip[0])
    ctx.line_to(*clip[1])
    ctx.line_to(*clip[2])
    ctx.close_path()
    ctx.clip()
    ctx.transform(canvas.matrix(coefficients))
    ctx.scale(SRC / layer.get_width(), SRC / layer.get_height())
    ctx.set_source_surface(layer, 0, 0)
    ctx.paint()
    ctx.restore()

    # Keine Ausgabe-Verifikation: save und restore stehen paarweise; die Koeffizienten
    # prüft affine.


def _check_triangle(triangle: Sequence[Point], where: str) -> None:
    """Wirft ValueError, wenn `triangle` nicht drei endliche Punkte hat."""
    # ── Eingabe-Validierung ──
    if len(triangle) != 3:
        raise ValueError(f"{where}: {len(triangle)} Ecken statt drei")

    # ── Verarbeitung ──
    for point in triangle:
        if len(point) != 2 or not all(math.isfinite(v) for v in point):
            raise ValueError(f"{where}: Ecke {point!r} nicht endlich")

    # Keine Ausgabe-Verifikation: Rückkehr heißt drei endliche Ecken.
