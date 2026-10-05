"""Kopfdrehung: das ganze Bild durch ein Drehgitter verformt, wie im Prototyp.

Der Kopf dreht um die Halswirbelsäule, die hinter der Kopfmitte liegt. Deshalb
wandert der ganze Kopf ein Stück zur Drehseite, das Gesicht als vorderster Teil am
weitesten. Jeder Punkt des Bildes wird quer zur geneigten Gesichtsachse verschoben,
um seine Tiefe vor der Achse mal den Sinus des Winkels (`yaw_shift`):

- Tiefe `AXIS_DEPTH` für den ganzen Kopf mit Haaren, dazu die Wölbung
  `HAIR_DEPTH · (1 − (u/HAIR_R)²)`, im Gesicht `FACE_DEPTH · (1 − (u/r)²)` und an
  der Nasenspitze `NOSE_DEPTH`;
- ab Kinnhöhe endet die Bewegung des Kopfes; darunter verdrillt sich der Hals als
  Zylinder um seine eigene Achse (`neck_shift`): Die Vorderseite wandert, die Kontur
  steht, und nach `NECK_LEN` unter der Kinnlinie (`JAWLINE`) ist die Drehung null;
- Brust, Schultern, das Haar neben dem Hals und der Bildrand stehen.

Bei 12° wandert die Nase um etwa 27 Pixel der Vorlage, die Augen weniger, die Ohren
noch weniger; das bezeugt D5 (`test_d5_at_12_degrees_nose_before_eyes_before_ears_before_hair`,
die Nase dort zwischen 26,5 und 29).

Das Gitter (`yaw_grid`) wird in der Quelle aufgespannt, `YAW_XS` × `YAW_YS`, im
Gesicht und über dem Hals dichter, und vorwärts abgebildet; das ist für jedes Dreieck
exakt. Kein Dreieck klappt um, bezeugt bis ±15° (D3); der Kommentar des Prototyps
nennt dafür ±20°. Die Grenze ist `YAW_MAX` (15°), jenseits wirft das Gitter.

Gezeichnet wird mit Unterlage (`draw_turned`): Erst liegt das ungedrehte Bild ganz
darunter, darüber nur die Dreiecke, an denen mindestens eine Ecke verschoben ist. Ein
Dreieck ohne Verschiebung ist die Identität und deckte genau die Unterlage; außerhalb
von Kopf und Hals wird so nichts gezeichnet, und jede Naht zwischen den Dreiecken ist
verdeckt.

Die Rechnung ist die des Prototyps (`yawShift`, `neckShift`, `jawY`, `yawGitter`,
`yawWarpDraw`), Zeichen für Zeichen; die Zahlen in den Formeln stehen dort genauso.
Das Modul importiert weder Cairo noch GTK.
"""

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from avatar.base_image import Canvas, WarpTriangle, draw_triangle, paint_layer, smooth01
from avatar.drawing_tools import SRC, UX, UY, Point
from avatar.idle_catalog import YAW_MAX

if TYPE_CHECKING:
    import cairo

TURN_MIN = 0.05  # Grad; bis hierher bleibt der Zeichenweg ungedreht, wie `turn` in `frame`
HEAD_C = (607.0, 475.0)  # Mitte zwischen Augenpaar und Mund
AXIS_DEPTH = 30.0  # Kopfmitte vor der Drehachse, in Pixeln der Vorlage
HAIR_DEPTH = 60.0  # Wölbung des Kopfes mit Haaren
HAIR_R = 300.0
FACE_DEPTH = 20.0  # Gesicht vor der Kopfwölbung
NOSE_DEPTH = 25.0  # zusätzliche Tiefe der Nasenspitze
NECK_CX = 600.0  # Halsmitte, in Pixeln der Vorlage
NECK_R = 130.0  # halbe Halsbreite
NECK_LEN = 230.0  # so weit unter der Kinnlinie ist die Verdrillung abgeschlossen
NECK_FALL = 1.6  # > 1: der Winkel fällt gleich unter dem Kinn am stärksten
# Größte Tiefe vor der Achse (Kopf, Wölbung, Gesicht, Nase) und größte Verschiebung
# durch die Verdrillung (die Vorderseite läuft höchstens einmal quer über den Hals).
DEPTH_MAX = AXIS_DEPTH + HAIR_DEPTH + FACE_DEPTH + NOSE_DEPTH
NECK_SHIFT_MAX = 2 * NECK_R

# Gitter über das ganze Bild, über der Halsbreite und im Gesicht dichter:
# 24 × 29 Punkte, 1288 Dreiecke (`rangeStep(460, 740, 28)` und `rangeStep(240, 1060, 35)`).
YAW_XS = (
    (0.0, 120.0, 240.0, 330.0, 380.0, 420.0)
    + tuple(float(x) for x in range(460, 741, 28))
    + (780.0, 820.0, 860.0, 920.0, 1010.0, 1130.0, float(SRC))
)
YAW_YS = (
    (0.0, 90.0, 180.0) + tuple(float(y) for y in range(240, 1061, 35)) + (1150.0, float(SRC))
)
YAW_TRIANGLES = (len(YAW_XS) - 1) * (len(YAW_YS) - 1) * 2

# Die Kinnlinie in Pixeln der Vorlage, nach x sortiert; aus `JAWLINE` im Prototyp
# (dort aus jawline.json). Seitlich liegt sie bei y ≈ 662, in der Mitte bei 744.
JAWLINE: tuple[Point, ...] = (
    (360, 660), (420, 662), (452, 664), (460, 671), (470, 682), (480, 694), (490, 705),
    (500, 716), (510, 725), (520, 731), (530, 735), (540, 738), (550, 740), (560, 742),
    (570, 744), (580, 744), (590, 744), (600, 742), (610, 740), (620, 736), (630, 733),
    (640, 729), (650, 726), (660, 721), (670, 717), (680, 713), (690, 708), (700, 702),
    (710, 696), (720, 689), (730, 681), (740, 674), (748, 668), (790, 664), (880, 662),
)


@dataclass(frozen=True)
class TurnPoint:
    """Ein Punkt des Drehgitters: Quelle, Ziel und die Verschiebung quer zur Gesichtsachse."""

    source: Point
    dest: Point
    shift: float  # Ziel = Quelle + shift · (UX, UY)


@dataclass(frozen=True)
class TurnTriangle:
    """Ein Dreieck des Drehgitters und ob mindestens eine seiner Ecken verschoben ist."""

    warp: WarpTriangle
    moved: bool


def jaw_y(x: float) -> float:
    """Die Höhe der Kinnlinie bei `x`, linear zwischen den Punkten von `JAWLINE`, wie `jawY`.

    Vorbedingung: `x` endlich.
    Nachbedingung: links des ersten und rechts des letzten Punkts gilt dessen Höhe;
    das Ergebnis liegt zwischen der kleinsten und der größten Höhe der Linie.
    Fehlerfälle: ValueError bei nicht endlichem `x`.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(x):
        raise ValueError(f"jaw_y: x {x!r} nicht endlich")

    # ── Verarbeitung ──
    line = JAWLINE
    result = float(line[-1][1])
    if x <= line[0][0]:
        result = float(line[0][1])
    else:
        for (x0, y0), (x1, y1) in zip(line, line[1:], strict=False):
            if x <= x1:
                f = (x - x0) / (x1 - x0)
                result = y0 + f * (y1 - y0)
                break

    # ── Ausgabe-Verifikation ──
    heights = [p[1] for p in line]
    if not min(heights) <= result <= max(heights):
        raise RuntimeError(f"jaw_y: Höhe {result} außerhalb der Kinnlinie")
    return result


def neck_shift(x: float, y: float, th: float) -> float:
    """Verschiebung des Punkts (x, y) durch die Verdrillung des Halses, wie `neckShift`.

    Der Hals ist ein Zylinder um `NECK_CX` mit Halbmesser `NECK_R`. Direkt an der
    Kinnlinie dreht er um den ganzen Winkel `th`, `NECK_LEN` darunter um nichts.
    Was hinter die Kontur dreht, wird an ihr gestaucht.
    Vorbedingung: alle drei endlich, `th` im Bogenmaß.
    Nachbedingung: 0 außerhalb der Halsbreite; sonst höchstens `NECK_SHIFT_MAX` im Betrag.
    Fehlerfälle: ValueError bei nicht endlicher Eingabe.
    """
    # ── Eingabe-Validierung ──
    if not all(math.isfinite(v) for v in (x, y, th)):
        raise ValueError(f"neck_shift: {x!r}, {y!r}, {th!r} nicht endlich")

    # ── Verarbeitung ──
    a = (x - NECK_CX) / NECK_R
    result = 0.0
    if abs(a) < 1:
        t = max(0.0, min(1.0, (y - jaw_y(x)) / NECK_LEN))
        phi = th * math.pow(1 - t, NECK_FALL)
        ang = max(-math.pi / 2, min(math.pi / 2, math.asin(a) + phi))
        result = NECK_R * (math.sin(ang) - a)

    # ── Ausgabe-Verifikation ──
    if not abs(result) <= NECK_SHIFT_MAX:
        raise RuntimeError(f"neck_shift: Verschiebung {result} über {NECK_SHIFT_MAX}")
    return result


def yaw_shift(x: float, y: float, s: float, th: float) -> float:
    """Verschiebung des Punkts (x, y) quer zur Gesichtsachse, in Pixeln, wie `yawShift`.

    `s` ist der Sinus von `th`. Über dem Kinn ist es die Tiefe vor der Drehachse mal
    `s`, darunter die Verdrillung des Halses; der Übergang (`hang`) liegt über dem Hals
    genau an der Kinnlinie, daneben bei den Haaren weicher. Zum Bildrand hin klingt
    alles auf null aus (`edge`).
    Vorbedingung: alle vier endlich.
    Nachbedingung: endlich und höchstens `DEPTH_MAX · |s| + NECK_SHIFT_MAX` im Betrag;
    0 auf dem Bildrand.
    Fehlerfälle: ValueError bei nicht endlicher Eingabe.
    """
    # ── Eingabe-Validierung ──
    if not all(math.isfinite(v) for v in (x, y, s, th)):
        raise ValueError(f"yaw_shift: {x!r}, {y!r}, {s!r}, {th!r} nicht endlich")

    # ── Verarbeitung ──
    dx, dy = x - HEAD_C[0], y - HEAD_C[1]
    u = dx * UX + dy * UY  # quer zur Gesichtsachse
    v = -dx * UY + dy * UX  # längs, nach unten
    r = 195 - 45 * smooth01(60, 260, v)  # das Gesicht wird zum Kinn hin schmaler
    au = min(1.0, abs(u) / r)
    ah = min(1.0, abs(u) / HAIR_R)
    face = (
        (1 - smooth01(r * 0.92, r + 45, abs(u)))
        * smooth01(-345, -270, v)
        * (1 - smooth01(260, 330, v))
    )
    nose = NOSE_DEPTH * math.exp(
        -(u * u) / (2 * 38 * 38) - ((v - 15) * (v - 15)) / (2 * 55 * 55)
    )
    z = AXIS_DEPTH + HAIR_DEPTH * (1 - ah * ah) + face * (FACE_DEPTH * (1 - au * au) + nose)
    on_neck = 1 - smooth01(NECK_R, NECK_R * 1.25, abs(x - NECK_CX))
    jy = jaw_y(x)
    hang = (1 - on_neck) * (1 - smooth01(260, 340, v)) + on_neck * (
        1 - smooth01(jy - 6, jy + 14, y)
    )
    edge = (
        smooth01(0, 60, x)
        * (1 - smooth01(SRC - 60, SRC, x))
        * smooth01(0, 40, y)
        * (1 - smooth01(SRC - 60, SRC, y))
    )
    result = (z * s * hang + (1 - hang) * neck_shift(x, y, th)) * edge

    # ── Ausgabe-Verifikation ──
    bound = DEPTH_MAX * abs(s) + NECK_SHIFT_MAX
    if not abs(result) <= bound:
        raise RuntimeError(f"yaw_shift: Verschiebung {result} bei ({x}, {y}) über {bound}")
    return result


def yaw_grid(deg: float) -> list[list[TurnPoint]]:
    """Das Drehgitter für `deg` Grad: Zeilen über `YAW_YS`, je Zeile Punkte über `YAW_XS`.

    Wie `yawGitter`: Ein Winkel jenseits der Grenze ist ein Fehler des Aufrufers, kein
    Bild.
    Vorbedingung: `deg` eine endliche Zahl mit |`deg`| ≤ `YAW_MAX`.
    Nachbedingung: `len(YAW_YS)` Zeilen zu `len(YAW_XS)` Punkten; die Quelle ist der
    Gitterpunkt, das Ziel die Quelle plus `shift` entlang (`UX`, `UY`), `shift` endlich.
    Fehlerfälle: TypeError, wenn `deg` keine Zahl ist; ValueError bei nicht endlichem
    Winkel oder jenseits von ±`YAW_MAX`.
    """
    # ── Eingabe-Validierung ──
    if isinstance(deg, bool) or not isinstance(deg, int | float):
        raise TypeError(f"Kopfdrehung: Winkel {deg!r} ist keine Zahl")
    if not math.isfinite(deg):
        raise ValueError(f"Kopfdrehung: Winkel ist keine endliche Zahl: {deg!r}")
    if abs(deg) > YAW_MAX:
        raise ValueError(f"Kopfdrehung: |{deg}°| liegt über der Grenze {YAW_MAX:g}°")

    # ── Verarbeitung ──
    th = deg * math.pi / 180
    s = math.sin(th)
    grid = []
    for y in YAW_YS:
        row = []
        for x in YAW_XS:
            shift = yaw_shift(x, y, s, th)
            dest = (x + UX * shift, y + UY * shift)
            row.append(TurnPoint(source=(x, y), dest=dest, shift=shift))
        grid.append(row)

    # ── Ausgabe-Verifikation ──
    if len(grid) != len(YAW_YS) or any(len(row) != len(YAW_XS) for row in grid):
        raise RuntimeError("Kopfdrehung: Gitter hat nicht 24 × 29 Punkte")
    if not all(math.isfinite(p.shift) for row in grid for p in row):
        raise RuntimeError("Kopfdrehung: eine Verschiebung ist keine Zahl")
    return grid


def yaw_triangles(grid: list[list[TurnPoint]]) -> list[TurnTriangle]:
    """Die Dreiecke des Drehgitters, in der Zerlegung von `yawWarpDraw`.

    Je Zelle erst (oben links, oben rechts, unten links), dann (oben rechts, unten
    rechts, unten links); zeilenweise. Ein Dreieck gilt als verschoben, wenn an
    mindestens einer Ecke die Verschiebung nicht 0 ist.
    Vorbedingung: `grid` aus `yaw_grid`, `len(YAW_YS)` Zeilen zu `len(YAW_XS)` Punkten.
    Nachbedingung: `YAW_TRIANGLES` Dreiecke; Quelle und Ziel aus den Ecken.
    Fehlerfälle: ValueError bei einem Gitter anderer Form.
    """
    # ── Eingabe-Validierung ──
    if len(grid) != len(YAW_YS) or any(len(row) != len(YAW_XS) for row in grid):
        raise ValueError("yaw_triangles: Gitter hat nicht 24 × 29 Punkte")

    # ── Verarbeitung ──
    triangles = []
    for j in range(len(YAW_YS) - 1):
        for i in range(len(YAW_XS) - 1):
            p, q, r, u = grid[j][i], grid[j][i + 1], grid[j + 1][i], grid[j + 1][i + 1]
            for corners in ((p, q, r), (q, u, r)):
                warp = WarpTriangle(
                    source=tuple(c.source for c in corners), dest=tuple(c.dest for c in corners)
                )
                moved = any(c.shift != 0 for c in corners)
                triangles.append(TurnTriangle(warp=warp, moved=moved))

    # ── Ausgabe-Verifikation ──
    if len(triangles) != YAW_TRIANGLES:
        raise RuntimeError(f"yaw_triangles: {len(triangles)} statt {YAW_TRIANGLES} Dreiecke")
    return triangles


def draw_turned(
    cr: "cairo.Context", canvas: Canvas, head: object, triangles: list[TurnTriangle]
) -> int:
    """Legt das ungedrehte Bild `head` als Unterlage, darüber die verschobenen Dreiecke.

    `cr` steht in Pixeln der Vorlage; `head` wird auf `SRC` × `SRC` gestreckt wie in
    `paint_layer`. Jedes verschobene Dreieck wird mit `draw_triangle` gezeichnet, also
    auf das radial vergrößerte Zieldreieck begrenzt.
    Vorbedingung: `head` eine Fläche mit Breite und Höhe > 0; `triangles` aus
    `yaw_triangles`.
    Nachbedingung: Unterlage und alle verschobenen Dreiecke liegen auf `cr`, in der
    Reihenfolge von `triangles`; `cr` steht danach wieder wie vorher. Rückgabe: die Zahl
    der gezeichneten Dreiecke.
    Fehlerfälle: ValueError bei leerer Fläche oder einer anderen Zahl von Dreiecken.
    """
    # ── Eingabe-Validierung ──
    width, height = head.get_width(), head.get_height()
    if width <= 0 or height <= 0:
        raise ValueError(f"draw_turned: Fläche {width} × {height} leer")
    if len(triangles) != YAW_TRIANGLES:
        raise ValueError(f"draw_turned: {len(triangles)} statt {YAW_TRIANGLES} Dreiecke")

    # ── Verarbeitung ──
    paint_layer(cr, head)
    moved = [t for t in triangles if t.moved]
    for triangle in moved:
        draw_triangle(cr, canvas, head, triangle.warp)

    # Keine Ausgabe-Verifikation: paint_layer und draw_triangle stellen `cr` mit
    # save/restore wieder her; Cairo prüft die Fläche beim Malen selbst.
    return len(moved)
