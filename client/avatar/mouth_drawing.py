"""Zeichnen des Mundes: Lippen, Mundwinkel, Mundraum mit Zunge und Zahnreihen, Lachfalten.

Formen und Maße folgen `drawMouth` des Prototyps. Gezeichnet wird auf einen
übergebenen Cairo-Kontext `cr`, in Pixeln der Vorlage; Skalierung, Grundbild,
Hintergrund und runde Linienenden setzt der Aufrufer, wie bei `drawing.py`.

Der Mund bekommt die Kanäle nach `mouth_state_combine`: Pressen, Unterlippe
einziehen, Spannen und Kinnmuskel haben die Öffnung dort schon verkleinert; hier
wirken sie auf Breite, Dicke und Strich der Lippen. Der Prüfregler `talk` des
Prototyps entfällt.

Der Zufall der Strichlage kommt aus dem Seed des Teils `PART_MOUTH`. Feste Lagen —
Schraffur, Zahnmaße, Zungenstriche — ziehen aus `mouth_hash`, damit das
Linien-Zittern sie nur verwackelt und nicht umverteilt.

Das Modul importiert weder Cairo noch GTK und braucht keine Konstante von Cairo:
Die Linienenden setzt der Aufrufer, und die Füllregel des Browsers (nonzero) ist
Cairos Voreinstellung (`FILL_RULE_WINDING`), auch für `clip`. Verläufe baut der
übergebene `Gradients`-Adapter; `globalAlpha` des Prototyps steht als Faktor in
jeder Deckkraft.
"""

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from avatar.drawing import MOUTH_CENTER, check_face
from avatar.drawing_tools import (
    INK,
    PART_MOUTH,
    TILT,
    UX,
    UY,
    Gradients,
    ParkMiller,
    Pen,
    Point,
    check_tick,
    fine,
    js_round,
    lerp2,
    local_point,
    park_miller_next,
    part_seed,
    point_on,
    quad,
    quadratic_to,
    set_rgba,
    trace_path,
)
from avatar.face import FaceState

if TYPE_CHECKING:
    import cairo

MOUTH_SEGMENTS = 24  # Stützpunkte je Lippenkurve minus eins (`N` im Prototyp)
OPENING_SEGMENTS = 22  # Stützpunkte je Rand der Öffnung minus eins (`OPN`)
PAD_SEGMENTS = 8  # Stützpunkte je Rand des Polsters am Mundwinkel minus eins
OPEN_FROM = 2.0  # ab dieser Öffnung in Pixeln: Mundraum, Zunge und Zähne
# Je Zahn von der Mitte nach außen: Breite, Höhe in Pixeln der Vorlage
TEETH_UPPER = ((28, 27), (19, 23), (16, 22), (14, 16), (13, 13), (12, 11), (11, 9))
TEETH_LOWER = ((17, 26), (18, 26), (18, 27), (17, 24), (16, 22), (15, 20), (15, 18))
POINTED_TOOTH = 2  # der Eckzahn oben endet spitz
LOWER_ARCH_R = 85.0  # Radius des unteren Zahnbogens
LOWER_ARCH_RISE = 0.18  # Anstieg der unteren Schneidekanten zu den Seiten
UPPER_GUM_Y = -7.0  # Zahnfleischrand oben, lokal in der Mitte
LOWER_TOP_Y = 10.0  # untere Schneidekante bei geschlossenem Kiefer (Überbiss)
ARCH_CURVE = 0.0012  # der obere Zahnbogen steigt zu den Seiten an
TONGUE_HALF_W = 58.0  # halbe Breite des Zungenblatts
TONGUE_TIP_FROM = 0.02  # ab dieser Zungenhöhe erscheint das Zungenblatt
LAUGH_FROM = 10.0  # ab dieser Mundkrümmung erscheinen Lachfalten
LAUGH_DY = 14.0  # Lachfalten tiefer als die Mundwinkel
HATCH_STROKES = 130
PAD_STROKES = 14
TONGUE_STROKES = 24
CORNER_INK = (28.0, 30.0, 34.0)
OPENING_INK = (30.0, 32.0, 36.0)
FULL_TURN = 2 * math.pi
ELLIPSE_FROM = 1e-9  # kleinere Halbachsen sind keine Ellipse mehr

Profile = Callable[[float], float]


@dataclass(frozen=True)
class MouthShape:
    """Die Lippenkurven und Maße eines Mundes, berechnet aus den Kanälen.

    `upper` ist die Unterkante der Oberlippe (`upB`), `lower` die Oberkante der
    Unterlippe (`loB`, bei geschlossenem Mund dieselbe Kurve); `top` und `bottom`
    sind die Außenkonturen. `inset` ist der Anteil der Mundlinie, um den die Öffnung
    vor jedem Winkel endet (`tIn`).
    """

    width_left: float
    width_right: float
    half_width: float
    corner_left: Point
    corner_right: Point
    upper: list[Point]
    lower: list[Point]
    top: list[Point]
    bottom: list[Point]
    opening: float
    inset: float
    lip_round: float
    press: float
    upper_thick: float
    lower_thick: float
    curve: float
    asym: float


def mouth_hash(i: int) -> float:
    """Fester Pseudozufall in [0, 1) je Index (`hashAt` im Prototyp).

    Vorbedingung: `i` ganzzahlig.
    Nachbedingung: Bruchteil von `sin((i + 1) · 12,9898) · 43758,5453`.
    Fehlerfälle: ValueError bei einem Index, der keine ganze Zahl ist.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(i, int) or isinstance(i, bool):
        raise ValueError(f"mouth_hash: Index {i!r} keine ganze Zahl")

    # ── Verarbeitung ──
    v = math.sin((i + 1) * 12.9898) * 43758.5453
    result = v - math.floor(v)

    # ── Ausgabe-Verifikation ──
    if not 0.0 <= result < 1.0:
        raise RuntimeError(f"mouth_hash: {result} außerhalb [0, 1)")
    return result


def lip_upper(t: float) -> float:
    """Dickenprofil der Oberlippe (`LIP_UP`): Bogen mit der Delle des Amorbogens in der Mitte.

    Vorbedingung: `t` in 0..1.
    Nachbedingung: ein Wert in 0..1, 0 an den Winkeln, 0,72 in der Mitte.
    Fehlerfälle: ValueError bei `t` außerhalb 0..1.
    """
    # ── Eingabe-Validierung ──
    _check_unit(t, "lip_upper")

    # ── Verarbeitung ──
    arc = math.pow(max(0.0, math.sin(math.pi * t)), 0.7)
    result = arc * (1 - 0.28 * math.exp(-(((t - 0.5) / 0.07) ** 2)))

    # ── Ausgabe-Verifikation ──
    if not 0.0 <= result <= 1.0:
        raise RuntimeError(f"lip_upper: {result} außerhalb 0..1")
    return result


def lip_lower(t: float) -> float:
    """Dickenprofil der Unterlippe (`LIP_LO`): ein voller Bogen, 1 in der Mitte.

    Vorbedingung: `t` in 0..1.
    Nachbedingung: ein Wert in 0..1, 0 an den Winkeln.
    Fehlerfälle: ValueError bei `t` außerhalb 0..1.
    """
    # ── Eingabe-Validierung ──
    _check_unit(t, "lip_lower")

    # ── Verarbeitung ──
    result = math.pow(max(0.0, math.sin(math.pi * t)), 0.8)

    # ── Ausgabe-Verifikation ──
    if not 0.0 <= result <= 1.0:
        raise RuntimeError(f"lip_lower: {result} außerhalb 0..1")
    return result


def offset_curve(curve: Sequence[Point], dist: float, profile: Profile) -> list[Point]:
    """Die Kurve, senkrecht zur Gesichtsachse um `dist · profile(t)` verschoben (`offsetCurve`).

    Positiv heißt nach unten. Vorbedingung: mindestens zwei endliche Punkte, `dist` endlich.
    Nachbedingung: gleich viele endliche Punkte.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    if len(curve) < 2 or not math.isfinite(dist):
        raise ValueError(f"offset_curve: {len(curve)} Punkte, Abstand {dist!r}")

    # ── Verarbeitung ──
    n = len(curve) - 1
    vx, vy = -UY, UX
    result = []
    for i, (x, y) in enumerate(curve):
        d = dist * profile(i / n)
        result.append((x + vx * d, y + vy * d))

    # ── Ausgabe-Verifikation ──
    _check_finite(result, "offset_curve")
    return result


def side_bump(t: float, value_left: float, value_right: float) -> float:
    """Wirkung eines paarigen Muskels entlang der Lippe: null im Winkel, stark auf seiner Seite.

    Vorbedingung: `t` in 0..1 (0 linker, 1 rechter Winkel), Werte endlich.
    Nachbedingung: `sin(π t)^0,6 · ((1 − t) · links + t · rechts)`.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    _check_unit(t, "side_bump")
    if not (math.isfinite(value_left) and math.isfinite(value_right)):
        raise ValueError(f"side_bump: {value_left!r}, {value_right!r} nicht endlich")

    # ── Verarbeitung ──
    result = math.pow(max(0.0, math.sin(math.pi * t)), 0.6) * (
        (1 - t) * value_left + t * value_right
    )

    # ── Ausgabe-Verifikation ──
    if not math.isfinite(result):
        raise RuntimeError(f"side_bump: {result!r} nicht endlich")
    return result


def mouth_curve(
    widths: tuple[float, float],
    heights: tuple[float, float],
    ctrl_y: float,
    power: float,
    add: Profile,
) -> list[Point]:
    """Eine Lippenkurve von Winkel zu Winkel mit getrennten Seiten (`mouthCurve2`).

    `widths` sind die halben Breiten links und rechts, `heights` die Winkelhöhen;
    die Mitte liegt um die halbe Differenz von `ctrl_y` zur mittleren Winkelhöhe
    tiefer, der Exponent `power` macht die Kurve von 2 (Parabel) an kastenförmiger.
    `add(t)` verschiebt zusätzlich, je Anteil `t` vom linken Winkel aus.
    Vorbedingung: alle Werte endlich, `power` > 0.
    Nachbedingung: `MOUTH_SEGMENTS + 1` endliche Punkte in Pixeln der Vorlage.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    values = (*widths, *heights, ctrl_y, power)
    if not all(math.isfinite(v) for v in values) or power <= 0:
        raise ValueError(f"mouth_curve: Werte {values!r} ungültig")

    # ── Verarbeitung ──
    (wl, wr), (yl, yr) = widths, heights
    depth = (ctrl_y - (yl + yr) / 2) / 2
    points = []
    for i in range(MOUTH_SEGMENTS + 1):
        t = i / MOUTH_SEGMENTS
        ly = yl + (yr - yl) * t + depth * (1 - abs(2 * t - 1) ** power) + add(t)
        points.append(local_point(MOUTH_CENTER, -wl + (wl + wr) * t, ly))

    # ── Ausgabe-Verifikation ──
    if len(points) != MOUTH_SEGMENTS + 1:
        raise RuntimeError(f"mouth_curve: {len(points)} Punkte")
    return points


def mouth_shape(face: FaceState) -> MouthShape:
    """Lippenkurven und Maße des Mundes aus den Kanälen, wie im Kopf von `drawMouth`.

    Jeder Muskelkanal wird auf 0..1 begrenzt wie im Prototyp. `mw` ist die halbe
    Mundbreite je Seite: Jochbein und Lachmuskel ziehen nach außen, der Ringmuskel
    zusammen. Die Öffnung zählt Ober- und Unterlippenheber und das Vorstülpen dazu.
    Vorbedingung: `face` mit endlichen Kanälen, `mouth_width` > 0.
    Nachbedingung: Kurven mit `MOUTH_SEGMENTS + 1` endlichen Punkten, halbe Breiten > 0.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    check_face(face, "mouth_shape")
    if face.mouth_width <= 0:
        raise ValueError(f"mouth_shape: Mundbreite {face.mouth_width!r} nicht positiv")

    # ── Verarbeitung ──
    mus = _muscles(face)
    mc, ma = face.mouth_curve, face.mouth_asym
    mo = max(0.0, face.mouth_open)
    lip_round = min(1.0, 0.75 * mus["au18"] + 0.75 * mus["au22"])
    press, lip_under = mus["au24"], mus["au28"]
    (wl, wr), (dyl, dyr) = _sides(face.mouth_width, mus)
    opening = (
        mo + 9 * (mus["au10_left"] + mus["au10_right"]) / 2
        + 9 * (mus["au16_left"] + mus["au16_right"]) / 2 + 4 * mus["au22"]
    )
    open_k = min(mo, 10.0) / 10
    mid = mc * 0.95 - open_k * mc * 0.7
    square = min(1.0, max(0.0, -mc / 20)) * open_k
    y0 = -mc * 0.45 * (1 + 1.2 * square)
    heights = (y0 + dyl, y0 + ma + dyr)
    upper = mouth_curve(
        (wl, wr), heights,
        mid - mo * 0.35 - max(0.0, mc) * 0.3 * open_k - lip_under * 4 - lip_round * 2,
        2 + 1.5 * square, lambda t: _add_upper(t, mus),
    )
    lower = upper if opening < OPEN_FROM else mouth_curve(
        (wl, wr), heights,
        mid + mo * 2.0 + open_k * mc * 0.3 + max(0.0, -mc) * 0.25 * open_k,
        2 + 3 * square, lambda t: _add_lower(t, mus),
    )
    upper_thick = (
        19 - max(0.0, mc) * 0.12 + mo * 0.05 + 5 * lip_round + 4 * mus["au18"]
        + 3 * mus["au22"] - 3 * mus["au23"]
    ) * (1 - 0.35 * press)
    lower_thick = (
        28 - max(0.0, mc) * 0.03 + 4 * lip_round + 3 * mus["au18"] + 3 * mus["au22"]
        + 3 * mus["au17"] - 3 * mus["au23"]
    ) * (1 - 0.3 * press) * (1 - 0.3 * lip_under)
    half_width = (wl + wr) / 2
    inset_px = min(half_width * 0.3, 12 + opening * 0.35) if opening >= OPEN_FROM else 0.0
    shape = MouthShape(
        width_left=wl,
        width_right=wr,
        half_width=half_width,
        corner_left=local_point(MOUTH_CENTER, -wl, heights[0]),
        corner_right=local_point(MOUTH_CENTER, wr, heights[1]),
        upper=upper,
        lower=lower,
        top=offset_curve(upper, -upper_thick, lip_upper),
        bottom=offset_curve(lower, lower_thick, lip_lower),
        opening=opening,
        inset=inset_px / (2 * half_width),
        lip_round=lip_round,
        press=press,
        upper_thick=upper_thick,
        lower_thick=lower_thick,
        curve=mc,
        asym=ma,
    )

    # ── Ausgabe-Verifikation ──
    if min(wl, wr) <= 0 or not 0.0 <= shape.inset < 0.5:
        raise RuntimeError(f"mouth_shape: Breiten {wl}, {wr}, Einzug {shape.inset}")
    lengths = {len(c) for c in (shape.upper, shape.lower, shape.top, shape.bottom)}
    if lengths != {MOUTH_SEGMENTS + 1}:
        raise RuntimeError(f"mouth_shape: Kurven mit {sorted(lengths)} Punkten")
    return shape


def draw_mouth(
    cr: "cairo.Context", gradients: Gradients, face: FaceState, tongue: float, boil_tick: int
) -> None:
    """Der ganze Mund wie `drawMouth`: Lippen, Winkel, Mundraum mit Zunge und Zähnen, Falten.

    `face` sind die Kanäle nach `mouth_state_combine`, `tongue` die Zungenhöhe von dort
    (0 Mundboden, 1 Spitze am Gaumen). Mundraum, Zunge und Zähne erscheinen erst ab einer
    Öffnung von `OPEN_FROM` Pixeln; darunter zeichnet eine Mundlinie, die beim Pressen
    breiter und dunkler wird.
    Vorbedingung: `face` mit endlichen Kanälen und `mouth_width` > 0, `tongue` in 0..1,
    `boil_tick` ganze Zahl ≥ 0.
    Nachbedingung: der Mund auf `cr`, mit dem Zufall des Teils `PART_MOUTH`;
    jedes `save` hat sein `restore`.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    check_face(face, "draw_mouth")
    check_tick(boil_tick, "draw_mouth")
    if not isinstance(tongue, int | float) or isinstance(tongue, bool):
        raise ValueError(f"draw_mouth: Zunge {tongue!r} keine Zahl")
    if not 0.0 <= tongue <= 1.0:
        raise ValueError(f"draw_mouth: Zunge {tongue!r} außerhalb 0..1")

    # ── Verarbeitung ──
    shape = mouth_shape(face)
    seed = part_seed(boil_tick, PART_MOUTH)
    pen = Pen(cr=cr, rng=ParkMiller(state=seed))
    _lip_base(pen, shape)
    if shape.opening >= OPEN_FROM:
        _open_mouth(pen, gradients, shape, max(0.0, face.jaw), float(tongue))
    else:
        _closed_line(pen, shape)
    _corners(pen, shape)
    _lip_shading(pen, shape)
    _under_shadow(pen, shape)
    _laugh_lines(pen, shape)

    # ── Ausgabe-Verifikation ──
    if pen.rng.state == seed:
        raise RuntimeError("draw_mouth: der Mund hat keinen Zufall gezogen")


_MUSCLES = (
    "au10_left", "au10_right", "au12_left", "au12_right", "au15_left", "au15_right",
    "au16_left", "au16_right", "au20_left", "au20_right",
    "au17", "au18", "au22", "au23", "au24", "au28",
)


def _muscles(face: FaceState) -> dict[str, float]:
    """Die Mundmuskeln des Gesichts, je auf 0..1 begrenzt (`A(k)` im Prototyp)."""
    # ── Eingabe-Validierung ──
    raw = {name: getattr(face, name) for name in _MUSCLES}

    # ── Verarbeitung ──
    result = {name: min(1.0, max(0.0, value)) for name, value in raw.items()}

    # ── Ausgabe-Verifikation ──
    if not all(0.0 <= v <= 1.0 for v in result.values()):
        raise RuntimeError(f"_muscles: nicht begrenzt: {result!r}")
    return result


def _sides(
    mouth_width: float, mus: dict[str, float]
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Halbe Breite und Winkelhöhe je Seite (`sideW`, `sideDY`), erst links, dann rechts.

    Jochbein und Lachmuskel ziehen nach außen, der Ringmuskel (Spitzen, Vorstülpen,
    Spannen) zusammen; das Jochbein hebt den Winkel, der Senker senkt ihn, das Kinn hebt.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(mouth_width) or mouth_width <= 0:
        raise ValueError(f"_sides: Mundbreite {mouth_width!r} ungültig")

    # ── Verarbeitung ──
    ring = 0.30 * mus["au18"] + 0.18 * mus["au22"] + 0.08 * mus["au23"]
    widths, heights = [], []
    for s in ("left", "right"):
        zygo, laugh = mus["au12_" + s], mus["au20_" + s]
        widths.append(mouth_width * (1 + 0.16 * zygo + 0.22 * laugh - ring))
        heights.append(-10 * zygo + 11 * mus["au15_" + s] + 2 * laugh - 3 * mus["au17"])

    # ── Ausgabe-Verifikation ──
    if min(widths) <= 0:
        raise RuntimeError(f"_sides: Breiten {widths!r} nicht positiv")
    return (widths[0], widths[1]), (heights[0], heights[1])


def _add_upper(t: float, mus: dict[str, float]) -> float:
    """Zusatz der Oberlippe: Heber ziehen je Seite hoch, Vorstülpen hebt die Mitte."""
    # ── Eingabe-Validierung ──
    _check_unit(t, "_add_upper")

    # ── Verarbeitung ──
    lift = side_bump(t, 10 * mus["au10_left"], 10 * mus["au10_right"])
    result = -lift - 5 * mus["au22"] * math.pow(max(0.0, math.sin(math.pi * t)), 0.8)

    # ── Ausgabe-Verifikation ──
    if not math.isfinite(result):
        raise RuntimeError(f"_add_upper: {result!r} nicht endlich")
    return result


def _add_lower(t: float, mus: dict[str, float]) -> float:
    """Zusatz der Unterlippe: Senker ziehen je Seite hinab, Kinnmuskel schiebt hoch."""
    # ── Eingabe-Validierung ──
    _check_unit(t, "_add_lower")

    # ── Verarbeitung ──
    drop = side_bump(t, 10 * mus["au16_left"], 10 * mus["au16_right"])
    middle = (4 * mus["au22"] - 5 * mus["au17"]) * math.pow(
        max(0.0, math.sin(math.pi * t)), 0.8
    )
    result = drop + middle

    # ── Ausgabe-Verifikation ──
    if not math.isfinite(result):
        raise RuntimeError(f"_add_lower: {result!r} nicht endlich")
    return result


def _lip_base(pen: Pen, shape: MouthShape) -> None:
    """Grundton beider Lippen und die Tiefe zur Mundlinie aus breiten, blassen Strichen."""
    # ── Eingabe-Validierung ──
    cr = pen.cr

    # ── Verarbeitung ──
    # Wie im Prototyp zwei Teilpfade: Der zweite beginnt mit move_to, nicht mit line_to
    for outer, inner, rgb, alpha in (
        (shape.top, shape.upper, (118.0, 119.0, 121.0), 0.36),
        (shape.lower, shape.bottom, (138.0, 139.0, 141.0), 0.2),
    ):
        cr.new_path()
        trace_path(cr, outer)
        trace_path(cr, inner[::-1])
        cr.close_path()
        set_rgba(cr, rgb, alpha)
        cr.fill()
    for k in range(3):
        fine(pen, offset_curve(shape.upper, -(3 + k * 3), lip_upper), 5, 0.07, 0.2)
        fine(pen, offset_curve(shape.lower, 3 + k * 3, lip_lower), 5, 0.05, 0.2)

    # Keine Ausgabe-Verifikation: Pfade prüft trace_path, Farben set_rgba, Striche fine.


def _closed_line(pen: Pen, shape: MouthShape) -> None:
    """Die Mundlinie geschlossener Lippen; Pressen macht sie breiter und dunkler."""
    # ── Eingabe-Validierung ──
    line = shape.upper

    # ── Verarbeitung ──
    fine(pen, line, 2.2 + 1.4 * shape.press, 0.72 + 0.2 * shape.press, 0.4)
    fine(pen, [(x, y + 0.8) for x, y in line], 1.2, 0.45, 0.4)
    fine(pen, line[8:17], 2.6, 0.35, 0.3)

    # Keine Ausgabe-Verifikation: Die Striche prüft fine.


def _open_mouth(
    pen: Pen, gradients: Gradients, shape: MouthShape, jaw: float, tongue: float
) -> None:
    """Polster, Mundraum, Zunge, Zahnreihen und Zahnfleisch, beschnitten auf die Öffnung."""
    # ── Eingabe-Validierung ──
    cr = pen.cr
    if not math.isfinite(jaw) or jaw < 0:
        raise ValueError(f"_open_mouth: Kiefer {jaw!r} ungültig")

    # ── Verarbeitung ──
    _pads(pen, gradients, shape)
    cr.save()
    _opening_path(cr, shape)
    start = local_point(MOUTH_CENTER, 0, UPPER_GUM_Y)
    end = local_point(MOUTH_CENTER, 0, LOWER_TOP_Y + jaw + 20)
    stops = ((0.0, (38.0, 40.0, 44.0, 1.0)), (1.0, (85.0, 87.0, 91.0, 1.0)))
    cr.set_source(gradients.linear(start, end, stops))
    cr.fill_preserve()
    cr.clip()
    _tongue(pen, gradients, jaw, tongue)
    # Vorgestülpte Lippen verdecken die Zähne etwas (`globalAlpha` im Prototyp)
    veil = 1 - 0.15 * shape.lip_round
    _teeth_row(pen, gradients, TEETH_LOWER, jaw, veil)
    _gum(cr, gradients, shape.half_width, veil)
    _teeth_row(pen, gradients, TEETH_UPPER, None, veil)
    for curve, width, alpha in ((shape.upper, 5.0, 0.07), (shape.lower, 6.0, 0.08)):
        cr.new_path()
        trace_path(cr, curve)
        cr.set_line_width(width)
        set_rgba(cr, INK, alpha)
        cr.stroke()
    cr.restore()
    _opening_path(cr, shape)
    cr.set_line_width(1.6)
    set_rgba(cr, OPENING_INK, 0.7)
    cr.stroke()
    for corner, t in ((shape.corner_left, shape.inset * 0.35),
                      (shape.corner_right, 1 - shape.inset * 0.35)):
        fine(pen, [corner, lerp2(corner, _corner_in(shape, t), 0.6)], 1.4, 0.45, 0.3)

    # Keine Ausgabe-Verifikation: Das restore steht vor dem Umriss; jeder Pfad ist in den
    # Werkzeugen geprüft.


def _corner_in(shape: MouthShape, t: float) -> Point:
    """Der Punkt bei 45 % zwischen Ober- und Unterlippe beim Anteil `t` (`cornerIn`)."""
    # ── Eingabe-Validierung ──
    _check_unit(t, "_corner_in")

    # ── Verarbeitung ──
    point = lerp2(point_on(shape.upper, t), point_on(shape.lower, t), 0.45)

    # ── Ausgabe-Verifikation ──
    _check_finite([point], "_corner_in")
    return point


def _opening_path(cr: "cairo.Context", shape: MouthShape) -> None:
    """Der Pfad der Öffnung: oberer Rand, Bogen am Winkel, unterer Rand zurück, Bogen."""
    # ── Eingabe-Validierung ──
    span = 1 - 2 * shape.inset
    if span <= 0:
        raise ValueError(f"_opening_path: Einzug {shape.inset} lässt keine Öffnung")

    # ── Verarbeitung ──
    ts = [shape.inset + span * i / OPENING_SEGMENTS for i in range(OPENING_SEGMENTS + 1)]
    rim_up = [point_on(shape.upper, t) for t in ts]
    rim_lo = [point_on(shape.lower, t) for t in ts]
    right = _corner_in(shape, 1 - shape.inset * 0.35)
    left = _corner_in(shape, shape.inset * 0.35)
    cr.new_path()
    cr.move_to(*rim_up[0])
    for point in rim_up:
        cr.line_to(*point)
    quadratic_to(cr, rim_up[-1], right, rim_lo[-1])
    for point in reversed(rim_lo):
        cr.line_to(*point)
    quadratic_to(cr, rim_lo[0], left, rim_up[0])

    # ── Ausgabe-Verifikation ──
    _check_finite(rim_up + rim_lo, "_opening_path")
    cr.close_path()


def _pads(pen: Pen, gradients: Gradients, shape: MouthShape) -> None:
    """Die Polster zwischen Lippenwinkel und Öffnung: Lippenfläche, zur Öffnung dunkler."""
    # ── Eingabe-Validierung ──
    cr = pen.cr

    # ── Verarbeitung ──
    stops = (
        (0.0, (196.0, 195.0, 196.0, 1.0)),
        (0.5, (182.0, 181.0, 182.0, 1.0)),
        (1.0, (150.0, 149.0, 151.0, 1.0)),
    )
    for end, inner in ((0, shape.inset + 0.03), (1, 1 - shape.inset - 0.03)):
        ts = [end + (inner - end) * i / PAD_SEGMENTS for i in range(PAD_SEGMENTS + 1)]
        points = [point_on(shape.upper, t) for t in ts]
        points += [point_on(shape.lower, t) for t in reversed(ts)]
        cr.new_path()
        cr.move_to(*points[0])
        for point in points:
            cr.line_to(*point)
        cr.close_path()
        start = point_on(shape.upper, end)
        mid = lerp2(point_on(shape.upper, inner), point_on(shape.lower, inner), 0.5)
        cr.set_source(gradients.linear(start, mid, stops))
        cr.fill()
        for i in range(PAD_STROKES):
            t = end + (inner - end) * mouth_hash(i + 3600 + end * 50)
            u = mouth_hash(i + 3700 + end * 50)
            a, b = point_on(shape.upper, t), point_on(shape.lower, t)
            p, q = lerp2(a, b, u), lerp2(a, b, min(1.0, u + 0.3))
            fine(pen, [p, (q[0] + 2, q[1])], 0.7, 0.2, 0.3)

    # Keine Ausgabe-Verifikation: Punkte liefert point_on geprüft, die Striche prüft fine.


def _tongue(pen: Pen, gradients: Gradients, jaw: float, tongue: float) -> None:
    """Zungenkörper am Mundboden, ab `TONGUE_TIP_FROM` das Blatt zum Gaumen, Mittellinie."""
    # ── Eingabe-Validierung ──
    cr = pen.cr
    if not 0.0 <= tongue <= 1.0:
        raise ValueError(f"_tongue: Zunge {tongue!r} außerhalb 0..1")

    # ── Verarbeitung ──
    floor_y = LOWER_TOP_Y + jaw + 14
    palate_y = UPPER_GUM_Y + 22
    body = local_point(MOUTH_CENTER, 0, floor_y)
    fade = 1 - 0.45 * tongue
    stops = (
        (0.0, (150.0, 152.0, 156.0, 0.9 * fade)),
        (0.7, (112.0, 114.0, 118.0, 0.85 * fade)),
        (1.0, (70.0, 72.0, 76.0, 0.6 * fade)),
    )
    _ellipse(cr, body, 72.0, 26.0)
    cr.set_source(gradients.radial((body[0], body[1] - 4, 4.0), (*body, 72.0), stops))
    cr.fill()
    if tongue > TONGUE_TIP_FROM:
        tip_y = floor_y + (palate_y - floor_y) * tongue
        ry = max(8.0, (floor_y - tip_y) / 2 + 10)
        center = local_point(MOUTH_CENTER, 0, (floor_y + tip_y) / 2)
        tip = local_point(MOUTH_CENTER, 0, tip_y)
        stops = (
            (0.0, (164.0, 165.0, 169.0, 0.9 * tongue)),
            (0.6, (128.0, 130.0, 134.0, 0.65 * tongue)),
            (1.0, (90.0, 92.0, 96.0, 0.0)),
        )
        _ellipse(cr, center, TONGUE_HALF_W - 6 * tongue, ry)
        inner = (tip[0], tip[1] + 4, 2.0)
        cr.set_source(gradients.radial(inner, (*center, max(ry, 58.0)), stops))
        cr.fill()
    midline = [
        local_point(MOUTH_CENTER, 0, LOWER_TOP_Y + jaw - 2 - 14 * tongue),
        local_point(MOUTH_CENTER, 0, LOWER_TOP_Y + jaw + 22),
    ]
    fine(pen, midline, 1.2, 0.25 * (1 - 0.5 * tongue), 0.3)
    for i in range(TONGUE_STROKES):
        lx = (mouth_hash(i + 40) - 0.5) * 110
        ly = LOWER_TOP_Y + jaw + 4 + mouth_hash(i + 80) * 18
        stroke = [local_point(MOUTH_CENTER, lx, ly), local_point(MOUTH_CENTER, lx + 5, ly + 4)]
        fine(pen, stroke, 0.6, 0.12 + mouth_hash(i + 120) * 0.1, 0.3)

    # Keine Ausgabe-Verifikation: Ellipsen prüft _ellipse, Verläufe der Adapter, Striche
    # fine.


def _ellipse(cr: "cairo.Context", center: Point, rx: float, ry: float) -> None:
    """Eine Ellipse in der Neigung des Gesichts als neuer Pfad (`ellipse(…, TILT, …)`)."""
    # ── Eingabe-Validierung ──
    _check_finite([center], "_ellipse")
    if not (math.isfinite(rx) and math.isfinite(ry)) or min(rx, ry) < ELLIPSE_FROM:
        raise ValueError(f"_ellipse: Halbachsen {rx!r}, {ry!r} ungültig")

    # ── Verarbeitung ──
    # Cairo kennt keine Ellipse: Einheitskreis, gedreht und gestreckt; das restore
    # nimmt die Abbildung zurück, der Pfad bleibt in Pixeln der Vorlage
    cr.new_path()
    cr.save()
    cr.translate(center[0], center[1])
    cr.rotate(TILT)
    cr.scale(rx, ry)
    cr.arc(0.0, 0.0, 1.0, 0.0, FULL_TURN)

    # ── Ausgabe-Verifikation ──
    cr.restore()


def _teeth_row(
    pen: Pen,
    gradients: Gradients,
    spec: Sequence[tuple[int, int]],
    jaw: float | None,
    veil: float,
) -> None:
    """Eine Zahnreihe, beide Seiten von der Mitte nach außen; `jaw` None heißt Oberkiefer.

    Oben sitzen die Zähne fest am Kopf auf einem ansteigenden Bogen, unten auf einem
    Kreisbogen, der von vorn gesehen seitlich verkürzt, und um den Kiefer nach unten
    verschoben. Je Zahn und Seite weichen Breite und Höhe fest etwas ab.
    """
    # ── Eingabe-Validierung ──
    upper = jaw is None
    if not 0.0 < veil <= 1.0:
        raise ValueError(f"_teeth_row: Deckkraft {veil!r} außerhalb (0, 1]")

    # ── Verarbeitung ──
    for s in (-1, 1):
        x = 0.0
        for i, (tw0, th0) in enumerate(spec):
            salt = (0 if upper else 50) + (20 if s > 0 else 0) + i
            tw = tw0 * (1 + (mouth_hash(salt + 600) - 0.5) * 0.08)
            th = th0 * (1 + (mouth_hash(salt + 700) - 0.5) * 0.1)
            if upper:
                xa, xb, xm = s * x, s * (x + tw), s * (x + tw / 2)
                root = UPPER_GUM_Y - ARCH_CURVE * xm * xm
                edge = root + th
                _tooth_path(pen.cr, (xa, xb), (root - 8, edge), True, i == POINTED_TOOTH)
            else:
                r = LOWER_ARCH_R
                am = (x + tw / 2) / r
                xa = s * r * math.sin(min(x / r, 1.45))
                xb = s * r * math.sin(min((x + tw) / r, 1.5))
                xm = s * r * math.sin(min(am, 1.48))
                edge = LOWER_TOP_Y + jaw - LOWER_ARCH_RISE * r * (1 - math.cos(am))
                root = edge + th
                _tooth_path(pen.cr, (xa, xb), (root + 8, edge), False, False)
            x += tw
            _tooth_paint(pen, gradients, (xm, root, edge), 250.0 - i * 10, veil)
            inward = 1 if upper else -1
            gap = [
                local_point(MOUTH_CENTER, xb, root + 11 * inward),
                local_point(MOUTH_CENTER, xb, edge - 4 * inward),
            ]
            fine(pen, gap, 0.8, 0.2 * veil, 0.1)
            rim = edge - 1.5 * inward
            cut = [
                local_point(MOUTH_CENTER, xa + s * 2, rim),
                local_point(MOUTH_CENTER, xb - s * 2, rim),
            ]
            fine(pen, cut, 0.7, 0.1 * veil, 0.2)

    # Keine Ausgabe-Verifikation: Jeder Zahn ist in _tooth_path und _tooth_paint geprüft,
    # jede Fuge in fine.


def _tooth_paint(
    pen: Pen, gradients: Gradients, column: tuple[float, float, float], tone: float, veil: float
) -> None:
    """Füllt den Zahnpfad hell, schattiert ihn zur Wurzel und zieht den Umriss."""
    # ── Eingabe-Validierung ──
    cr = pen.cr
    xm, root, edge = column
    if not 0.0 <= tone <= 255.0:
        raise ValueError(f"_tooth_paint: Ton {tone!r} außerhalb 0..255")

    # ── Verarbeitung ──
    set_rgba(cr, (tone, tone, tone - 3), veil)
    cr.fill_preserve()
    start = local_point(MOUTH_CENTER, xm, root)
    end = local_point(MOUTH_CENTER, xm, (root + edge) / 2)
    stops = ((0.0, (40.0, 40.0, 44.0, 0.08 * veil)), (1.0, (40.0, 40.0, 44.0, 0.0)))
    cr.set_source(gradients.linear(start, end, stops))
    cr.fill_preserve()
    cr.set_line_width(0.6)
    set_rgba(cr, INK, 0.14 * veil)

    # ── Ausgabe-Verifikation ──
    # Farben prüft set_rgba, Punkte local_point.
    cr.stroke()


def _tooth_path(
    cr: "cairo.Context",
    span: tuple[float, float],
    rows: tuple[float, float],
    round_down: bool,
    pointed: bool,
) -> None:
    """Der Umriss eines Zahns (`toothPath`): Bogen am Zahnfleisch, gerundete Schneidekante.

    `span` sind die lokalen x der beiden Seiten, `rows` die lokalen y der Wurzelseite
    und der Schneidekante; zwischen den Zähnen liegen tiefere Zwickel.
    """
    # ── Eingabe-Validierung ──
    xa, xb = span
    y_gum, y_edge = rows
    if not all(math.isfinite(v) for v in (xa, xb, y_gum, y_edge)):
        raise ValueError(f"_tooth_path: {span!r}, {y_gum!r}, {y_edge!r} nicht endlich")

    # ── Verarbeitung ──
    direction = 1 if round_down else -1
    w, xm = abs(xb - xa), (xa + xb) / 2
    gum = y_gum + direction * 8
    valley = gum + direction * min(6.0, w * 0.25)
    crest = gum - direction * min(12.0, w * 0.5)
    if pointed:
        rc = min(5.0, w * 0.32)
    else:
        rc = min(3.5, w * 0.16) if round_down else min(1.5, w * 0.08)
    sx = -1 if xb < xa else 1
    tip_bulge = 4.0 if pointed else 1.0 if round_down else 0.3

    def at(lx: float, ly: float) -> Point:
        return local_point(MOUTH_CENTER, lx, ly)

    p0, c0, p1 = at(xa, valley), at(xm, crest), at(xb, valley)
    p2, c2 = at(xb, y_edge - direction * rc), at(xb, y_edge)
    p3 = at(xb - sx * rc, y_edge + direction * 0.5)
    c3 = at(xm, y_edge + direction * tip_bulge)
    p4 = at(xa + sx * rc, y_edge + direction * 0.5)
    c4, p5 = at(xa, y_edge), at(xa, y_edge - direction * rc)
    cr.new_path()
    cr.move_to(*p0)
    quadratic_to(cr, p0, c0, p1)
    cr.line_to(*p2)
    quadratic_to(cr, p2, c2, p3)
    quadratic_to(cr, p3, c3, p4)
    quadratic_to(cr, p4, c4, p5)

    # ── Ausgabe-Verifikation ──
    # Jeder Punkt kommt aus local_point, jeder Kontrollpunkt ist in quadratic_to geprüft.
    cr.close_path()


def _gum(cr: "cairo.Context", gradients: Gradients, half_width: float, veil: float) -> None:
    """Das Zahnfleisch oben: ein Band entlang des Zahnbogens, nach oben dunkler."""
    # ── Eingabe-Validierung ──
    if not math.isfinite(half_width) or half_width <= 0:
        raise ValueError(f"_gum: halbe Breite {half_width!r} ungültig")

    # ── Verarbeitung ──
    top, bottom = [], []
    for i in range(MOUTH_SEGMENTS + 1):
        x = -half_width - 10 + (2 * half_width + 20) * i / MOUTH_SEGMENTS
        lift = ARCH_CURVE * x * x
        top.append(local_point(MOUTH_CENTER, x, UPPER_GUM_Y - 24 - lift))
        bottom.append(local_point(MOUTH_CENTER, x, UPPER_GUM_Y + 9 - lift))
    start = local_point(MOUTH_CENTER, 0, UPPER_GUM_Y - 18)
    end = local_point(MOUTH_CENTER, 0, UPPER_GUM_Y + 9)
    stops = (
        (0.0, (118.0, 118.0, 120.0, veil)),
        (0.6, (168.0, 166.0, 166.0, veil)),
        (1.0, (182.0, 180.0, 180.0, veil)),
    )
    band = top + bottom[::-1]
    cr.new_path()
    cr.move_to(*band[0])
    for point in band[1:]:
        cr.line_to(*point)
    cr.close_path()
    cr.set_source(gradients.linear(start, end, stops))

    # ── Ausgabe-Verifikation ──
    _check_finite(band, "_gum")
    cr.fill()


def _corners(pen: Pen, shape: MouthShape) -> None:
    """Die dunklen Keile der Mundwinkel; bei geschlossenem Mund dazu kurze, kräftige Striche."""
    # ── Eingabe-Validierung ──
    cr, n = pen.cr, MOUTH_SEGMENTS
    is_open = shape.opening >= OPEN_FROM

    # ── Verarbeitung ──
    wedges = (
        (shape.corner_left, shape.upper[2], shape.lower[2]),
        (shape.corner_right, shape.upper[n - 2], shape.lower[n - 2]),
    )
    for corner, a, b in wedges:
        cr.new_path()
        cr.move_to(*corner)
        cr.line_to(*a)
        cr.line_to(b[0], b[1] + 2)
        cr.close_path()
        set_rgba(cr, CORNER_INK, 0.35 if is_open else 0.55)
        cr.fill()
    if not is_open:
        fine(pen, shape.upper[:3], 2.8, 0.7, 0.3)
        fine(pen, shape.upper[n - 2:], 2.8, 0.7, 0.3)

    # Keine Ausgabe-Verifikation: Die Punkte stammen aus mouth_shape, geprüft dort; Farben
    # prüft set_rgba.


def _lip_shading(pen: Pen, shape: MouthShape) -> None:
    """Schraffur beider Lippen, Kanten, Glanzlicht der Unterlippe, Andeutung des Philtrums."""
    # ── Eingabe-Validierung ──
    cr, n = pen.cr, MOUTH_SEGMENTS

    # ── Verarbeitung ──
    _lip_hatch(pen, (shape.top, shape.upper), 0.6, False, 0)
    _lip_hatch(pen, (shape.bottom, shape.lower), 0.48, True, 500)
    for k in range(3):
        rim = offset_curve(shape.bottom, -(2 + k * 2.2), lambda _t: 1.0)
        fine(pen, rim[3 : n - 2], 3, 0.09, 0.4)
    for k in range(3):
        fine(pen, [(x, y + k * 0.6) for x, y in shape.top[1:n]], 1.1, 0.42, 0.6)
    for k in range(2):
        fine(pen, [(x, y - k * 0.6) for x, y in shape.bottom[3 : n - 2]], 1.1, 0.4, 0.6)
    gloss = offset_curve(shape.lower, shape.lower_thick * 0.45, lip_lower)
    gloss = gloss[math.floor(n * 0.36) : math.ceil(n * 0.64)]
    for points, width, rgb, alpha in (
        (gloss, 5.0, (252.0, 252.0, 250.0), 0.28),
        (gloss[1:-1], 2.0, (255.0, 255.0, 255.0), 0.4),
    ):
        cr.new_path()
        trace_path(cr, points)
        cr.set_line_width(width)
        set_rgba(cr, rgb, alpha)
        cr.stroke()
    for t in (0.44, 0.56):
        x, y = shape.top[js_round(t * n)]
        stroke = [(x + UY * 2, y - UX * 2), (x + UY * 20 + (t - 0.5) * 12, y - UX * 20)]
        fine(pen, stroke, 0.7, 0.14, 0.5)

    # Keine Ausgabe-Verifikation: Pfade prüft trace_path, Striche fine.


def _lip_hatch(
    pen: Pen, edges: tuple[list[Point], list[Point]], base_alpha: float, gloss: bool, salt: int
) -> None:
    """Lippenrillen von der Außenkontur zur Mundlinie (`lipHatchSoft`), zur Mundlinie dunkler.

    Mit `gloss` bleibt in der Mitte der Unterlippe ein Glanzlicht frei.
    """
    # ── Eingabe-Validierung ──
    outer, inner = edges
    if len(outer) != len(inner) or len(outer) < 2:
        raise ValueError(f"_lip_hatch: Kurven mit {len(outer)} und {len(inner)} Punkten")

    # ── Verarbeitung ──
    for i in range(HATCH_STROKES):
        t = 0.03 + 0.94 * mouth_hash(i + salt)
        u = mouth_hash(i + salt + 1000)
        if gloss and 0.3 < t < 0.7 and 0.25 < u < 0.7:
            continue
        a, b = point_on(outer, t), point_on(inner, t)
        p, q = lerp2(a, b, u), lerp2(a, b, min(1.0, u + 0.35))
        corner = 1 - math.pow(max(0.0, math.sin(math.pi * t)), 0.5)
        alpha = (
            base_alpha * (0.35 + 0.65 * u) * (0.6 + 0.6 * corner)
            * (0.6 + 0.5 * mouth_hash(i + salt + 2000))
        )
        fine(pen, [p, (q[0] + 3, q[1])], 0.7, min(0.7, alpha), 0.3)

    # Keine Ausgabe-Verifikation: Die Striche prüft fine; das ausgesparte Glanzlicht ist
    # gewollt, kein Fehlerfall.


def _under_shadow(pen: Pen, shape: MouthShape) -> None:
    """Der Schatten unter der Unterlippe: kurze, blasse Striche mit zufälligem Abstand."""
    # ── Eingabe-Validierung ──
    n = MOUTH_SEGMENTS

    # ── Verarbeitung ──
    for i in range(5, n - 4):
        x, y = shape.bottom[i]
        for _ in range(2):
            d = 3 + park_miller_next(pen.rng) * 6
            alpha = 0.08 + park_miller_next(pen.rng) * 0.06
            stroke = [(x - UY * d, y + UX * d), (x - UY * (d + 8) + 4, y + UX * (d + 8))]
            fine(pen, stroke, 0.6, alpha)

    # Keine Ausgabe-Verifikation: Die Striche prüft fine; Abstand und Deckkraft ziehen vor
    # dem Verwackeln wie im Prototyp.


def _laugh_lines(pen: Pen, shape: MouthShape) -> None:
    """Lachfalten neben den Mundwinkeln, ab einer Mundkrümmung von `LAUGH_FROM`."""
    # ── Eingabe-Validierung ──
    mc, w = shape.curve, shape.half_width

    # ── Verarbeitung ──
    # Unter der Schwelle gibt es keine Falten: dann bleibt die Liste der Seiten leer
    sides = ((-1, 0.0), (1, shape.asym)) if mc > LAUGH_FROM else ()
    alpha = min(1.0, (mc - LAUGH_FROM) / 20) * 0.45
    base = -mc * 0.45 + LAUGH_DY
    for side, shift in sides:
        y = base + shift
        fold = quad(
            local_point(MOUTH_CENTER, side * (w + 18), y - 44),
            local_point(MOUTH_CENTER, side * (w + 30), y - 8),
            local_point(MOUTH_CENTER, side * (w + 10), y + 16),
        )
        fine(pen, fold, 1, alpha, 0.6)
        fine(pen, [(px, py + 1.5) for px, py in fold], 0.7, alpha * 0.5, 0.6)

    # Keine Ausgabe-Verifikation: Die Striche prüft fine.


def _check_unit(t: float, where: str) -> None:
    """Wirft ValueError, wenn `t` nicht in 0..1 liegt (auch bei NaN)."""
    # ── Eingabe-Validierung ──
    inside = 0.0 <= t <= 1.0

    # ── Verarbeitung ──
    if not inside:
        raise ValueError(f"{where}: t = {t!r} außerhalb 0..1")

    # Keine Ausgabe-Verifikation: Rückkehr heißt gültig.


def _check_finite(points: Sequence[Point], where: str) -> None:
    """Wirft RuntimeError, wenn ein berechneter Punkt nicht endlich ist."""
    # ── Eingabe-Validierung ──
    if not points:
        raise RuntimeError(f"{where}: keine Punkte")

    # ── Verarbeitung ──
    bad = [p for p in points if not (math.isfinite(p[0]) and math.isfinite(p[1]))]

    # ── Ausgabe-Verifikation ──
    if bad:
        raise RuntimeError(f"{where}: Punkte nicht endlich: {bad[:3]!r}")
