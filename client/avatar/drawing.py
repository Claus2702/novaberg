"""Zeichnen des Gesichts ohne Mund: Brauen, Augen, Brauenfalten, Röte, Träne, Schweiß.

Jede Funktion zeichnet auf einen übergebenen Cairo-Kontext `cr`, in Pixeln der
Vorlage (`SRC` × `SRC`). Skalierung, Grundbild, Hintergrund und runde
Linienenden (`frame` im Prototyp) setzt der Aufrufer, bevor er hier zeichnet.

Der Zufall der Strichlage ist je Teil eigen: Der Seed eines Teils folgt aus dem
Boil-Takt und der Konstante des Teils (`part_seed`). Gleiche Kanäle, gleicher
Blinzelwert und gleicher Takt ergeben deshalb dieselbe Zeichnung, und eine
Änderung an einem Teil verschiebt die Striche der anderen nicht.

Das Modul importiert weder Cairo noch GTK; Verläufe baut ein `Gradients`-Adapter
(`CairoGradients` im Client).
"""

import math
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from avatar.drawing_eye import EYE_LEFT, EYE_RIGHT, draw_eye
from avatar.drawing_tools import (
    PART_BROW_LEFT,
    PART_BROW_RIGHT,
    PART_EXTRAS,
    PART_EYE_LEFT,
    PART_EYE_RIGHT,
    PART_WRINKLES,
    UX,
    UY,
    Gradients,
    ParkMiller,
    Pen,
    Point,
    check_tick,
    fine,
    js_round,
    local_point,
    park_miller_next,
    part_seed,
    pencil,
    quad,
    set_rgba,
)
from avatar.face import FaceState
from avatar.pose import Pose

if TYPE_CHECKING:
    import cairo

BROW_SEGMENTS = 30
BROW_HAIRS = 190
BROW_JITTER = 0.8  # Verwackeln der Brauenfläche, ohne BOIL_AMP wie im Prototyp
BROW_INK = (52.0, 54.0, 58.0)
BROW_LAYERS = ((1.1, 0.1), (0.9, 0.15), (0.55, 0.2))  # Breite, Deckkraft je Fläche
MOUTH_CENTER = (590.2, 566.0)
GLABELLA = (621.0, 314.0)
BLUSH_STROKES = 22  # Striche je Wange bei voller Röte
BLUSH_CHEEKS = ((-150.0, -95.0), (140.0, -80.0))
DROP_VISIBLE = 0.25  # ab dieser Stärke erscheinen Träne und Schweißtropfen


@dataclass(frozen=True)
class BrowGeometry:
    """Lage einer Braue: drei Ankerpunkte, ihre Kanäle, Stärke, Wuchsrichtung der Haare."""

    inner: Point
    peak: Point
    outer: Point
    inner_channel: str
    outer_channel: str
    thick: float
    hair_side: int


BROW_LEFT = BrowGeometry(
    inner=(575.0, 306.0),
    peak=(500.0, 284.0),
    outer=(455.0, 301.0),
    inner_channel="brow_left_inner",
    outer_channel="brow_left_outer",
    thick=16.0,
    hair_side=1,
)
BROW_RIGHT = BrowGeometry(
    inner=(668.0, 322.0),
    peak=(735.0, 316.0),
    outer=(797.0, 337.0),
    inner_channel="brow_right_inner",
    outer_channel="brow_right_outer",
    thick=18.0,
    hair_side=-1,
)


def check_face(face: FaceState, where: str) -> None:
    """Wirft ValueError, wenn `face` kein `FaceState` ist oder ein Kanal nicht endlich ist."""
    # ── Eingabe-Validierung ──
    if not isinstance(face, FaceState):
        raise ValueError(f"{where}: {type(face).__name__} statt FaceState")

    # ── Verarbeitung ──
    bad = [f.name for f in fields(FaceState) if not math.isfinite(getattr(face, f.name))]

    # ── Ausgabe-Verifikation ──
    if bad:
        raise ValueError(f"{where}: Kanäle nicht endlich: {', '.join(bad)}")


def brow_points(brow: BrowGeometry, face: FaceState) -> tuple[Point, Point, Point]:
    """Innen-, Scheitel- und Außenpunkt einer Braue, senkrecht zur Gesichtsachse verschoben.

    Innen um den inneren Kanal, außen um den äußeren, der Scheitel um deren Mittel
    minus 1 plus `barch`; negativ heißt nach oben.
    Vorbedingung: `face` mit endlichen Kanälen.
    Nachbedingung: drei endliche Punkte.
    Fehlerfälle: RuntimeError bei nicht endlichem Ergebnis.
    """
    # ── Eingabe-Validierung ──
    inner_off = getattr(face, brow.inner_channel)
    outer_off = getattr(face, brow.outer_channel)

    # ── Verarbeitung ──
    offsets = (inner_off, (inner_off + outer_off) / 2 - 1 + face.brow_arch, outer_off)
    vx, vy = -UY, UX
    anchors = (brow.inner, brow.peak, brow.outer)
    p0, p1, p2 = ((p[0] + o * vx, p[1] + o * vy) for p, o in zip(anchors, offsets, strict=True))

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for v in (*p0, *p1, *p2)):
        raise RuntimeError(f"brow_points: nicht endlich: {p0}, {p1}, {p2}")
    return p0, p1, p2


def draw_brows(cr: "cairo.Context", face: FaceState, boil_tick: int) -> None:
    """Beide Brauen: drei verwackelte Flächen und 190 Haarstriche je Braue.

    Vorbedingung: `face` mit endlichen Kanälen, `boil_tick` ganze Zahl ≥ 0.
    Nachbedingung: beide Brauen auf `cr`, jede mit dem Zufall ihres Teils.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    check_face(face, "draw_brows")
    check_tick(boil_tick, "draw_brows")

    # ── Verarbeitung ──
    used = []
    for brow, part in ((BROW_LEFT, PART_BROW_LEFT), (BROW_RIGHT, PART_BROW_RIGHT)):
        seed = part_seed(boil_tick, part)
        pen = Pen(cr=cr, rng=ParkMiller(state=seed))
        _brow(pen, brow, face)
        used.append(pen.rng.state != seed)

    # ── Ausgabe-Verifikation ──
    if not all(used):
        raise RuntimeError("draw_brows: eine Braue hat keinen Zufall gezogen")


def draw_eyes(cr: "cairo.Context", gradients: Gradients, pose: Pose) -> None:
    """Beide Augen; `pose.blink` 1 heißt offen, 0 geschlossen.

    Vorbedingung: `pose.face` mit endlichen Kanälen, `pose.blink` in 0..1,
    `pose.boil_tick` ganze Zahl ≥ 0, `pose.head_yaw` endlich; `gradients` baut die
    Verläufe (`CairoGradients` im Client).
    Nachbedingung: beide Augen auf `cr`, jedes mit dem Zufall seines Teils; die Iris
    um den Kopfwinkel zurückgenommen.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(pose, Pose):
        raise ValueError(f"draw_eyes: {pose!r} ist keine Pose")
    check_face(pose.face, "draw_eyes")
    check_tick(pose.boil_tick, "draw_eyes")
    blink, yaw = pose.blink, pose.head_yaw
    if isinstance(blink, bool) or not isinstance(blink, int | float):
        raise ValueError(f"draw_eyes: Blinzelwert {blink!r} keine Zahl")
    if not 0.0 <= blink <= 1.0:
        raise ValueError(f"draw_eyes: Blinzelwert {blink!r} außerhalb 0..1")
    if isinstance(yaw, bool) or not isinstance(yaw, int | float) or not math.isfinite(yaw):
        raise ValueError(f"draw_eyes: head_yaw {yaw!r} keine endliche Zahl")

    # ── Verarbeitung ──
    used = []
    for eye, part in ((EYE_LEFT, PART_EYE_LEFT), (EYE_RIGHT, PART_EYE_RIGHT)):
        seed = part_seed(pose.boil_tick, part)
        pen = Pen(cr=cr, rng=ParkMiller(state=seed))
        draw_eye(pen, gradients, eye, pose)
        used.append(pen.rng.state != seed)

    # ── Ausgabe-Verifikation ──
    if not all(used):
        raise RuntimeError("draw_eyes: ein Auge hat keinen Zufall gezogen")


def draw_brow_wrinkles(cr: "cairo.Context", face: FaceState, boil_tick: int) -> None:
    """Falten über der Nasenwurzel: senkrecht beim Zusammenziehen, quer beim Hochziehen.

    Das Mittel der inneren Brauen entscheidet: über 8 px gesenkt beginnen die
    Zornesfalten (voll bei 24), über 12 px gehoben die Sorgenfalten (voll bei 26).
    Vorbedingung: `face` mit endlichen Kanälen, `boil_tick` ganze Zahl ≥ 0.
    Nachbedingung: keine, eine oder beide Faltenarten auf `cr`.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    check_face(face, "draw_brow_wrinkles")
    check_tick(boil_tick, "draw_brow_wrinkles")

    # ── Verarbeitung ──
    pen = Pen(cr=cr, rng=ParkMiller(state=part_seed(boil_tick, PART_WRINKLES)))
    inner = (face.brow_left_inner + face.brow_right_inner) / 2
    frown = max(0.0, min(1.0, (inner - 8) / 16))
    if frown > 0.02:
        for sd in (-1, 1):
            line = quad(
                local_point(GLABELLA, sd * 13, -16),
                local_point(GLABELLA, sd * 8, 0),
                local_point(GLABELLA, sd * 10, 16),
                8,
            )
            fine(pen, line, 1.2, 0.45 * frown, 0.5)
            fine(pen, [(x + sd * 1.5, y) for x, y in line], 0.7, 0.22 * frown, 0.5)
    worry = max(0.0, min(1.0, (-inner - 12) / 14))
    if worry > 0.02:
        for k in range(3):
            y, half = -50 - k * 13, 46 - k * 6
            line = quad(
                local_point(GLABELLA, -half, y + 4),
                local_point(GLABELLA, 0, y - 6),
                local_point(GLABELLA, half, y + 4),
                12,
            )
            fine(pen, line, 1.0, 0.32 * worry, 0.6)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft; ohne Falte bleibt cr
    # unberührt.


def draw_extras(cr: "cairo.Context", face: FaceState, elapsed_ms: float, boil_tick: int) -> None:
    """Brauenfalten, Röte auf beiden Wangen, Träne unter dem linken Auge, Schweißtropfen.

    `elapsed_ms` ist die Zeit seit Beginn in Millisekunden; an ihr fällt die Träne
    (70 px in 2,1 s, dann von vorn).
    Vorbedingung: `face` mit endlichen Kanälen, `elapsed_ms` endlich und ≥ 0,
    `boil_tick` ganze Zahl ≥ 0.
    Nachbedingung: Falten wie `draw_brow_wrinkles`; `js_round(blush · 22)` Striche je
    Wange; Träne und Schweiß ab `tear` bzw. `sweat` über 0,25.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    check_face(face, "draw_extras")
    check_tick(boil_tick, "draw_extras")
    if not math.isfinite(elapsed_ms) or elapsed_ms < 0:
        raise ValueError(f"draw_extras: Zeit {elapsed_ms!r} ms ungültig")

    # ── Verarbeitung ──
    draw_brow_wrinkles(cr, face, boil_tick)
    pen = Pen(cr=cr, rng=ParkMiller(state=part_seed(boil_tick, PART_EXTRAS)))
    strokes = js_round(face.blush * BLUSH_STROKES)
    _blush(pen, strokes)
    if face.tear > DROP_VISIBLE:
        p = local_point(EYE_LEFT.center, 12, 34 + (elapsed_ms / 30) % 70)
        drop = [(p[0], p[1] - 9), (p[0] - 5, p[1] + 3), (p[0], p[1] + 7), (p[0] + 5, p[1] + 3)]
        pencil(pen, [*drop, drop[0]], 1.2, 0.75 * face.tear, 0.3)
    if face.sweat > DROP_VISIBLE:
        p = local_point(EYE_RIGHT.center, 30, -150)
        drop = [(p[0], p[1] - 12), (p[0] - 7, p[1] + 4), (p[0], p[1] + 10), (p[0] + 7, p[1] + 4)]
        pencil(pen, [*drop, drop[0]], 1.2, 0.7 * face.sweat, 0.3)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine bzw. pencil geprüft; Deckkraft
    # über 1 weist set_rgba ab.


def _blush(pen: Pen, strokes: int) -> None:
    """Röte: auf jeder Wange `strokes` kurze Schrägstriche, zur Mitte der Wange dichter."""
    # ── Eingabe-Validierung ──
    if strokes < 0:
        raise ValueError(f"_blush: {strokes} Striche")

    # ── Verarbeitung ──
    for lx, ly in BLUSH_CHEEKS:
        for _ in range(strokes):
            ox = (park_miller_next(pen.rng) - 0.5) * 60
            oy = (park_miller_next(pen.rng) - 0.5) * 26
            p = local_point(MOUTH_CENTER, lx + ox, ly + oy)
            fall = 1 - min(1.0, math.hypot(ox / 30, oy / 13))
            alpha = (0.06 + park_miller_next(pen.rng) * 0.1) * (0.4 + fall)
            fine(pen, [(p[0], p[1] - 7), (p[0] - 7, p[1] + 7)], 0.7, alpha, 0.4)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _brow(pen: Pen, brow: BrowGeometry, face: FaceState) -> None:
    """Eine Braue: drei übereinanderliegende Flächen, darüber die Haarstruktur."""
    # ── Eingabe-Validierung ──
    p0, p1, p2 = brow_points(brow, face)

    # ── Verarbeitung ──
    ctrl = (2 * p1[0] - (p0[0] + p2[0]) / 2, 2 * p1[1] - (p0[1] + p2[1]) / 2)
    path = quad(p0, ctrl, p2, BROW_SEGMENTS)
    for scale, alpha in BROW_LAYERS:
        poly = _brow_band(pen, path, brow.thick, scale)
        pen.cr.new_path()
        pen.cr.move_to(poly[0][0], poly[0][1])
        for x, y in poly:
            pen.cr.line_to(x, y)
        pen.cr.close_path()
        set_rgba(pen.cr, BROW_INK, alpha)
        pen.cr.fill()
    _brow_hairs(pen, path, brow)

    # Keine Ausgabe-Verifikation: Die Flächen prüft _brow_band, die Haare fine.


def _half_width(t: float, thick: float) -> float:
    """Halbe Brauenbreite bei `t`: innen voll, am Scheitel (35 %) am breitesten, Ende spitz."""
    # ── Eingabe-Validierung ──
    if not 0.0 <= t <= 1.0:
        raise ValueError(f"_half_width: t = {t!r} außerhalb 0..1")

    # ── Verarbeitung ──
    if t < 0.35:
        factor = 0.5 + 0.2 * (t / 0.35)
    else:
        factor = 0.7 * (1 - (t - 0.35) / 0.65) ** 0.8 + 0.06

    # ── Ausgabe-Verifikation ──
    if not factor > 0:
        raise RuntimeError(f"_half_width: Faktor {factor}")
    return thick * factor


def _brow_band(pen: Pen, path: list[Point], thick: float, scale: float) -> list[Point]:
    """Umriss einer Brauenfläche: Oberkante hin, Unterkante zurück, je Punkt verwackelt."""
    # ── Eingabe-Validierung ──
    n = len(path) - 1
    if n < 1:
        raise ValueError(f"_brow_band: {len(path)} Punkte")

    # ── Verarbeitung ──
    upper: list[Point] = []
    lower: list[Point] = []
    shift = -thick * 0.12
    for i in range(n + 1):
        p, q, r = path[i], path[min(n, i + 1)], path[max(0, i - 1)]
        tx, ty = q[0] - r[0], q[1] - r[1]
        tl = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / tl, tx / tl
        w = _half_width(i / n, thick) * scale
        upper.append(
            (
                p[0] + nx * (w + shift) + (park_miller_next(pen.rng) - 0.5) * BROW_JITTER,
                p[1] + ny * (w + shift) + (park_miller_next(pen.rng) - 0.5) * BROW_JITTER,
            )
        )
        lower.append(
            (
                p[0] - nx * (w - shift) + (park_miller_next(pen.rng) - 0.5) * BROW_JITTER,
                p[1] - ny * (w - shift) + (park_miller_next(pen.rng) - 0.5) * BROW_JITTER,
            )
        )
    outline = upper + lower[::-1]

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for point in outline for v in point):
        raise RuntimeError("_brow_band: Umriss nicht endlich")
    return outline


def _brow_hairs(pen: Pen, path: list[Point], brow: BrowGeometry) -> None:
    """Haarstruktur: schräg in Wuchsrichtung, innen steiler, dezent."""
    # ── Eingabe-Validierung ──
    n = len(path) - 1
    if n < 1:
        raise ValueError(f"_brow_hairs: {len(path)} Punkte")

    # ── Verarbeitung ──
    s = brow.hair_side
    for i in range(BROW_HAIRS):
        t = i / BROW_HAIRS
        j = min(n - 1, math.floor(t * n))
        p, q = path[j], path[j + 1]
        tx, ty = q[0] - p[0], q[1] - p[1]
        tl = math.hypot(tx, ty) or 1.0
        nx, ny, ax, ay = -ty / tl, tx / tl, tx / tl, ty / tl
        offset = (park_miller_next(pen.rng) - 0.5) * 1.6 * _half_width(t, brow.thick)
        length = 7 + park_miller_next(pen.rng) * 6
        lift = (0.9 if t < 0.2 else 0.35) * s * length * 0.5
        sx, sy = p[0] + nx * offset, p[1] + ny * offset
        end = (sx + ax * length - nx * lift, sy + ay * length - ny * lift)
        width = 0.6 + park_miller_next(pen.rng) * 0.5
        alpha = 0.3 + park_miller_next(pen.rng) * 0.3
        fine(pen, [(sx, sy), end], width, alpha, 0.3)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.
