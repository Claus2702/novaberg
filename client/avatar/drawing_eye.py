"""Das Auge: Lider, Lidfalte, Augapfel mit Iris und Pupille, Wimpern, Grafitschatten.

Formen und Maße folgen `drawEye` des Prototyps. Der Zufall (`pen.rng`) verwackelt
nur; wo eine Strichlage fest bleiben muss, zieht sie aus `eye_hash` — sonst
würde das Linien-Zittern die Striche umverteilen statt sie zu verwackeln.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from avatar.drawing_tools import (
    INK,
    UX,
    UY,
    Gradients,
    Pen,
    Point,
    fine,
    js_round,
    lerp2,
    local_point,
    park_miller_next,
    point_on,
    quad,
    set_rgba,
    trace_path,
)
from avatar.face import FaceState

if TYPE_CHECKING:
    import cairo

EYE_SEGMENTS = 20  # Stützpunkte je Lidkurve minus eins (`N` im Prototyp)
# Unter dieser Öffnung ist das Auge geschlossen gezeichnet. Bei 0,12 wechselte die
# Zeichnung früh: Ein Lidschlag zeigte länger das dünne geschlossene Auge als das
# offene mit seiner Wimpernlinie. Ein Lidschlag des Leerlaufs hält das Auge
# mindestens 40 ms ganz zu, das geschlossene Bild bleibt also sichtbar.
CLOSED_BELOW = 0.06
CLOSED_LASH_CLUMPS = 8  # Wimpernbüschel des geschlossenen Auges
CLUMP_STRANDS = (-1, 0, 1)  # drei Wimpern je Büschel: Versatz der Wurzel in Schritten
# Weg der Iris je Einheit Blick, als Anteil der halben Augenbreite. Bei 0,3 rückte
# ein Blick von 0,25 zur Seite die Iris nur um 0,075 · hw, und das liest ein
# Betrachter noch als Blick zu ihm. Bei 0,9 Blick bleibt der Irisrand mit 0,5 noch
# in der Lidspalte (0,45 + 0,46 = 0,91 · hw).
IRIS_TRAVEL_X = 0.5
IRIS_TRAVEL_Y = 0.26
CREASE_GAP = 14  # Abstand der Lidfalte zum Oberlid in der Mitte, in Pixeln
LASH_CLUMPS = 10
LOWER_LASHES = 13
LOWER_LASH_SKIP = (3, 7)  # festes Auslassmuster, damit nichts flackert
SMOKE = (40.0, 40.0, 44.0)
LASH_INK = (30.0, 32.0, 36.0)
FULL_TURN = 2 * math.pi


@dataclass(frozen=True)
class EyeGeometry:
    """Lage eines Auges in der Vorlage: Mitte, halbe Breite, Seite (−1 links, 1 rechts)."""

    center: Point
    half_width: float
    side: int


@dataclass(frozen=True)
class Lids:
    """Die Lidkurven eines offenen Auges und die Höhe des Oberlids."""

    upper: list[Point]
    lower: list[Point]
    crease: list[Point]
    up: float


EYE_LEFT = EyeGeometry(center=(521.0, 366.0), half_width=50.0, side=-1)
EYE_RIGHT = EyeGeometry(center=(727.0, 400.0), half_width=60.0, side=1)


def eye_hash(i: int, side: int) -> float:
    """Fester Pseudozufall in [0, 1) je Index und Auge (`hsh` im Prototyp).

    Vorbedingung: `i` ganzzahlig, `side` −1 oder 1.
    Nachbedingung: Bruchteil von `sin((i + 1) · 12,9898 + side · 78,233) · 43758,5453`.
    Fehlerfälle: ValueError bei unbekannter Seite.
    """
    # ── Eingabe-Validierung ──
    if side not in (-1, 1):
        raise ValueError(f"eye_hash: Seite {side!r} nicht −1 oder 1")

    # ── Verarbeitung ──
    v = math.sin((i + 1) * 12.9898 + side * 78.233) * 43758.5453
    result = v - math.floor(v)

    # ── Ausgabe-Verifikation ──
    if not 0.0 <= result < 1.0:
        raise RuntimeError(f"eye_hash: {result} außerhalb [0, 1)")
    return result


def eye_opening(face: FaceState, blink: float) -> float:
    """Die Öffnung des Auges: Augenöffnung des Gesichts mal Blinzelwert (1 offen, 0 zu).

    Vorbedingung: `blink` in 0..1, `face.eye_open` endlich.
    Nachbedingung: das Produkt; unter `CLOSED_BELOW` zeichnet das Auge geschlossen.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    if not 0.0 <= blink <= 1.0:
        raise ValueError(f"eye_opening: Blinzelwert {blink!r} außerhalb 0..1")
    if not math.isfinite(face.eye_open):
        raise ValueError(f"eye_opening: eye_open {face.eye_open!r} nicht endlich")

    # ── Verarbeitung ──
    opening = face.eye_open * blink

    # ── Ausgabe-Verifikation ──
    if not math.isfinite(opening):
        raise RuntimeError(f"eye_opening: {opening} nicht endlich")
    return opening


def lid_extent(
    eye: EyeGeometry, face: FaceState, opening: float, blink: float
) -> tuple[float, float]:
    """Wie weit Ober- und Unterlid auseinanderstehen: `(up, lo)` in Pixeln.

    `up = hw · 0,5 · opening · (1 − 0,35 · lidU)`,
    `lo = hw · 0,27 · min(eye_open, 1) · blink − arc · hw · 0,22`.
    Weitung hebt nur das Oberlid (AU5): das Unterlid folgt der Öffnung bis 1, der
    Lidschlag schließt es weiter mit. `blink` kommt eigens, weil sich `min(eye_open, 1)`
    aus dem Produkt `opening` nicht zurückrechnen lässt.
    Vorbedingung: `opening` endlich, `blink` in 0..1.
    Nachbedingung: beide Werte endlich.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(opening):
        raise ValueError(f"lid_extent: Öffnung {opening!r} nicht endlich")
    if not 0.0 <= blink <= 1.0:
        raise ValueError(f"lid_extent: Blinzelwert {blink!r} außerhalb 0..1")

    # ── Verarbeitung ──
    hw = eye.half_width
    up = hw * 0.5 * opening * (1 - 0.35 * face.lid_upper)
    # Susskind 2008: Weitung hebt nur das Oberlid.
    lo = hw * 0.27 * min(face.eye_open, 1.0) * blink - face.eye_arc * hw * 0.22

    # ── Ausgabe-Verifikation ──
    if not (math.isfinite(up) and math.isfinite(lo)):
        raise RuntimeError(f"lid_extent: {up}, {lo} nicht endlich")
    return up, lo


def iris_center(eye: EyeGeometry, face: FaceState, up: float) -> Point:
    """Mitte der Iris: Blick verschiebt sie, ein weit offenes Oberlid hebt sie leicht.

    Der Weg je Einheit Blick ist `IRIS_TRAVEL_X` und `IRIS_TRAVEL_Y` (siehe dort):
    weit genug, dass ein abgewandter Blick als abgewandt gelesen wird.
    Vorbedingung: `up` endlich.
    Nachbedingung: `L(E, gx · hw · 0,5, gy · hw · 0,26 − up · 0,12)`.
    Fehlerfälle: ValueError aus `local_point` bei nicht endlicher Eingabe.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(up):
        raise ValueError(f"iris_center: up {up!r} nicht endlich")

    # ── Verarbeitung ──
    hw = eye.half_width
    center = local_point(
        eye.center,
        face.gaze_x * hw * IRIS_TRAVEL_X,
        face.gaze_y * hw * IRIS_TRAVEL_Y - up * 0.12,
    )

    # Keine Ausgabe-Verifikation: local_point prüft seinen Punkt.
    return center


def iris_radius(eye: EyeGeometry) -> float:
    """Radius der Iris: 46 % der halben Augenbreite."""
    # ── Eingabe-Validierung ──
    if eye.half_width <= 0:
        raise ValueError(f"iris_radius: halbe Breite {eye.half_width!r} ≤ 0")

    # ── Verarbeitung ──
    radius = eye.half_width * 0.46

    # ── Ausgabe-Verifikation ──
    if not radius > 0:
        raise RuntimeError(f"iris_radius: {radius}")
    return radius


def pupil_radius(eye: EyeGeometry, face: FaceState) -> float:
    """Radius der Pupille: 38 % des Irisradius mal Pupillengröße `ps`.

    Vorbedingung: `face.pupil_size` endlich und nicht negativ.
    Nachbedingung: ein Radius ≥ 0.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(face.pupil_size) or face.pupil_size < 0:
        raise ValueError(f"pupil_radius: Pupillengröße {face.pupil_size!r} ungültig")

    # ── Verarbeitung ──
    radius = iris_radius(eye) * 0.38 * face.pupil_size

    # ── Ausgabe-Verifikation ──
    if radius < 0:
        raise RuntimeError(f"pupil_radius: {radius} negativ")
    return radius


def closed_lid(eye: EyeGeometry) -> list[Point]:
    """Die Lidlinie des geschlossenen Auges, vom inneren zum äußeren Winkel.

    Vorbedingung: keine über die Geometrie hinaus.
    Nachbedingung: `EYE_SEGMENTS + 1` Punkte, Kontrollpunkt `L(E, 0, hw · 0,16)`.
    Fehlerfälle: keine eigenen; `quad` prüft seine Punkte.
    """
    # ── Eingabe-Validierung ──
    inner, outer = _corners(eye)

    # ── Verarbeitung ──
    ctrl = local_point(eye.center, 0.0, eye.half_width * 0.16)
    lid = quad(inner, ctrl, outer, EYE_SEGMENTS)

    # ── Ausgabe-Verifikation ──
    if len(lid) != EYE_SEGMENTS + 1:
        raise RuntimeError(f"closed_lid: {len(lid)} Punkte")
    return lid


def draw_eye(
    pen: Pen, gradients: Gradients, eye: EyeGeometry, face: FaceState, blink: float
) -> None:
    """Ein Auge, offen oder geschlossen, in der Reihenfolge des Prototyps.

    Vorbedingung: `face` geprüft (endliche Kanäle), `blink` in 0..1.
    Nachbedingung: das Auge steht auf `pen.cr`; Speichern und Wiederherstellen des
    Kontexts sind ausgeglichen.
    Fehlerfälle: ValueError aus den Prüfungen der Werkzeuge.
    """
    # ── Eingabe-Validierung ──
    opening = eye_opening(face, blink)

    # ── Verarbeitung ──
    if opening < CLOSED_BELOW:
        _closed_eye(pen, eye)
        return
    lids = _open_lids(eye, face, opening, blink)
    _lid_hatching(pen, eye, lids)
    _smoky_corner(pen, gradients, eye)
    _graphite_below(pen, eye)
    _eyeball(pen, gradients, eye, face, lids)
    _upper_lash_line(pen, lids.upper)
    _lash_clumps(pen, eye, lids.upper)
    _crease_lines(pen, lids.crease)
    _outer_lashes(pen, eye, lids.upper)
    _lower_lid(pen, eye, lids.lower)

    # Keine Ausgabe-Verifikation: Jeder Punkt wird in trace_path geprüft, bevor er den
    # Kontext erreicht.


def _corners(eye: EyeGeometry) -> tuple[Point, Point]:
    """Innerer und äußerer Augenwinkel."""
    # ── Eingabe-Validierung ──
    hw, side = eye.half_width, eye.side

    # ── Verarbeitung ──
    inner = local_point(eye.center, -side * hw, hw * 0.05)
    outer = local_point(eye.center, side * hw, -hw * 0.08)

    # Keine Ausgabe-Verifikation: local_point prüft seine Punkte.
    return inner, outer


def _closed_eye(pen: Pen, eye: EyeGeometry) -> None:
    """Geschlossenes Auge: Lidlinie, Wimpernbüschel nach unten, flache Falte.

    Die Lidlinie hat das Gewicht der Wimpernlinie des offenen Auges, nach außen
    kräftiger. Vorher war sie ein Strich von 1,6 mit Deckkraft 0,5 und Wimpern von
    0,9 — das geschlossene Auge war damit dünner als die Wimpernlinie des offenen.
    """
    # ── Eingabe-Validierung ──
    lid = closed_lid(eye)
    hw, side = eye.half_width, eye.side

    # ── Verarbeitung ──
    _closed_lid_line(pen, lid)
    _closed_lash_clumps(pen, side, lid)
    crease = quad(
        local_point(eye.center, -side * hw * 0.75, -6),
        local_point(eye.center, side * hw * 0.1, -hw * 0.2),
        local_point(eye.center, side * hw * 0.98, -8),
        EYE_SEGMENTS,
    )
    fine(pen, crease, 1.0, 0.3, 0.8)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _closed_lid_line(pen: Pen, lid: Sequence[Point]) -> None:
    """Die Lidlinie des geschlossenen Auges in sieben Strichen, nach außen kräftiger.

    Innen ein feiner Strich (1,2), ab Punkt 4 vier Lagen von 2,2, deren Abstand nach
    außen wächst, ab Punkt 6 einer von 3,6 und ab Punkt 12 einer von 5.
    Vorbedingung: `lid` aus `closed_lid`, `EYE_SEGMENTS + 1` Punkte.
    Nachbedingung: sieben Striche auf `pen.cr`.
    Fehlerfälle: ValueError bei einer Lidlinie anderer Länge.
    """
    # ── Eingabe-Validierung ──
    if len(lid) != EYE_SEGMENTS + 1:
        raise ValueError(f"_closed_lid_line: {len(lid)} Punkte statt {EYE_SEGMENTS + 1}")

    # ── Verarbeitung ──
    fine(pen, lid[:8], 1.2, 0.65, 0.3)
    for k in range(4):
        layer = [
            (x, y + k * 0.7 * (0.25 + 0.75 * (i + 4) / EYE_SEGMENTS))
            for i, (x, y) in enumerate(lid[4:])
        ]
        fine(pen, layer, 2.2, 0.7, 0.4)
    fine(pen, lid[6:], 3.6, 0.78, 0.3)
    fine(pen, lid[12:], 5.0, 0.7, 0.3)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _closed_lash_clumps(pen: Pen, side: int, lid: Sequence[Point]) -> None:
    """`CLOSED_LASH_CLUMPS` Büschel zu je drei Wimpern nach unten, innen dünner und kürzer.

    Die drei Wimpern eines Büschels haben getrennte Wurzeln (1,2 px Abstand) und
    laufen zur Spitze zusammen; jede ist ein kräftiger Ansatz und ein feiner Strich.
    Vorbedingung: `lid` aus `closed_lid`, `side` −1 oder 1.
    Nachbedingung: `CLOSED_LASH_CLUMPS · 3 · 2` Striche auf `pen.cr`.
    Fehlerfälle: ValueError bei einer Lidlinie anderer Länge oder einer anderen Seite.
    """
    # ── Eingabe-Validierung ──
    if len(lid) != EYE_SEGMENTS + 1 or side not in (-1, 1):
        raise ValueError(f"_closed_lash_clumps: {len(lid)} Punkte, Seite {side!r}")

    # ── Verarbeitung ──
    for i in range(CLOSED_LASH_CLUMPS):
        f = i / (CLOSED_LASH_CLUMPS - 1)
        weight, length = 0.55 + 0.55 * f, 6 + 9 * f
        p = lid[min(EYE_SEGMENTS - 1, 6 + js_round(f * 13))]
        tip = (p[0] + side * length * 0.7, p[1] + length * 0.85)
        for strand in CLUMP_STRANDS:
            root = (p[0] + strand * 1.2, p[1])
            mid = (root[0] + side * length * 0.35, root[1] + length * 0.6)
            curve = quad(root, mid, (tip[0] + strand * 0.8, tip[1] + strand * 0.5), 6)
            fine(pen, curve[:4], 1.8 * weight, 0.8, 0.15)
            fine(pen, curve, 1.1 * weight, 0.8, 0.15)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _open_lids(eye: EyeGeometry, face: FaceState, opening: float, blink: float) -> Lids:
    """Ober- und Unterlid und die Lidfalte, die dem Oberlid in festem Abstand folgt."""
    # ── Eingabe-Validierung ──
    up, lo = lid_extent(eye, face, opening, blink)
    inner, outer = _corners(eye)
    hw, side = eye.half_width, eye.side

    # ── Verarbeitung ──
    upper = quad(inner, local_point(eye.center, side * hw * 0.12, -2 * up), outer, EYE_SEGMENTS)
    lower = quad(inner, local_point(eye.center, -side * hw * 0.1, 2 * lo), outer, EYE_SEGMENTS)
    crease: list[Point] = []
    for i, p in enumerate(upper):
        t = i / EYE_SEGMENTS
        # nahezu parallel, nur an den Enden kurz auslaufend; schwere Lider rücken näher
        taper = math.sin(math.pi * (0.02 + 0.96 * t)) ** 0.25
        d = (CREASE_GAP - face.lid_upper * 4) * taper + 1
        crease.append((p[0] + UY * d, p[1] - UX * d))

    # ── Ausgabe-Verifikation ──
    if not len(upper) == len(lower) == len(crease) == EYE_SEGMENTS + 1:
        raise RuntimeError("_open_lids: Lidkurven ungleich lang")
    return Lids(upper=upper, lower=lower, crease=crease, up=up)


def _lid_hatching(pen: Pen, eye: EyeGeometry, lids: Lids) -> None:
    """Lidschatten zwischen Lidfalte und Wimpernkranz: feine Schraffur."""
    # ── Eingabe-Validierung ──
    side = eye.side

    # ── Verarbeitung ──
    for i in range(2, EYE_SEGMENTS):
        for _ in range(2):
            a, b = lids.upper[i], lids.crease[i]
            s0 = 0.08 + park_miller_next(pen.rng) * 0.1
            s1 = 0.5 + park_miller_next(pen.rng) * 0.4
            end = lerp2(a, b, s1)
            alpha = 0.09 + (i / EYE_SEGMENTS) * 0.08
            fine(pen, [lerp2(a, b, s0), (end[0] + side * 3, end[1])], 0.7, alpha)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _smoky_corner(pen: Pen, gradients: Gradients, eye: EyeGeometry) -> None:
    """Rauchige Fläche um den äußeren Augenwinkel, darüber 46 feste Grafitstriche."""
    # ── Eingabe-Validierung ──
    hw, side = eye.half_width, eye.side

    # ── Verarbeitung ──
    corner = local_point(eye.center, side * hw * 0.95, -hw * 0.05)
    radius = hw * 0.9
    stops = ((0.0, (*SMOKE, 0.6)), (0.45, (*SMOKE, 0.3)), (1.0, (*SMOKE, 0.0)))
    pen.cr.set_source(gradients.radial((*corner, 0.0), (*corner, radius), stops))
    pen.cr.new_path()
    pen.cr.arc(corner[0], corner[1], radius, 0, FULL_TURN)
    pen.cr.fill()
    for i in range(46):
        r = math.sqrt(eye_hash(i, side))
        a = eye_hash(i + 100, side) * FULL_TURN
        lx = side * hw * 0.95 + math.cos(a) * r * hw * 0.55
        ly = -hw * 0.05 + math.sin(a) * r * hw * 0.42
        start = local_point(eye.center, lx, ly)
        end = local_point(eye.center, lx + side * 7, ly + 6)
        alpha = (0.18 + 0.24 * eye_hash(i + 200, side)) * (0.4 + 1 - r)
        fine(pen, [start, end], 0.8, alpha, 0.6)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _graphite_below(pen: Pen, eye: EyeGeometry) -> None:
    """Dunkles Band unter dem Unterlid, äußere Hälfte, und 30 kurze feste Striche."""
    # ── Eingabe-Validierung ──
    hw, side = eye.half_width, eye.side
    n = EYE_SEGMENTS

    # ── Verarbeitung ──
    edge = quad(
        local_point(eye.center, -side * hw, hw * 0.05),
        local_point(eye.center, -side * hw * 0.1, 2 * (hw * 0.27)),
        local_point(eye.center, side * hw, -hw * 0.08),
        n,
    )
    tail = edge[math.floor(n * 0.4) :]
    for k in range(4):
        d = 2 + k * 2.2
        band = [
            (p[0] - UY * d, p[1] + UX * d * (0.6 + 0.4 * i / (len(tail) - 1)))
            for i, p in enumerate(tail)
        ]
        fine(pen, band, 2.4 - k * 0.4, 0.22 - k * 0.04, 0.5)
    for i in range(30):
        t = 0.4 + 0.6 * eye_hash(i + 300, side)
        p = point_on(edge, t)
        d = 2 + eye_hash(i + 400, side) * 8
        start = (p[0] - UY * d, p[1] + UX * d)
        alpha = (0.13 + 0.15 * eye_hash(i + 500, side)) * (t - 0.3)
        fine(pen, [start, (start[0] + side * 5, start[1] + 5)], 0.75, alpha, 0.5)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _eyeball(
    pen: Pen, gradients: Gradients, eye: EyeGeometry, face: FaceState, lids: Lids
) -> None:
    """Augapfel, Iris und Pupille, beschnitten auf die Lidöffnung, mit Schatten des Lids."""
    # ── Eingabe-Validierung ──
    hw, side = eye.half_width, eye.side
    cr = pen.cr

    # ── Verarbeitung ──
    cr.save()
    cr.new_path()
    trace_path(cr, lids.upper)
    trace_path(cr, lids.lower[::-1])
    cr.close_path()
    set_rgba(cr, (247.0, 247.0, 244.0), 1.0)
    cr.fill_preserve()
    cr.clip()
    center = eye.center
    corner = (center[0] - hw * 1.2, center[1] - hw)
    shade = ((0.0, (*SMOKE, 0.0)), (1.0, (*SMOKE, 0.22)))
    cr.set_source(gradients.radial((*center, hw * 0.3), (*center, hw * 1.05), shade))
    cr.new_path()
    cr.rectangle(corner[0], corner[1], hw * 2.4, hw * 2)
    cr.fill()
    outer = local_point(center, side * hw, 0.0)
    side_shade = ((0.0, (*SMOKE, 0.0)), (0.3, (*SMOKE, 0.04)), (1.0, (*SMOKE, 0.55)))
    cr.set_source(gradients.linear(center, outer, side_shade))
    cr.new_path()
    cr.rectangle(corner[0], corner[1], hw * 2.4, hw * 2)
    cr.fill()
    iris = iris_center(eye, face, lids.up)
    _iris(pen, gradients, eye, iris)
    _pupil(cr, gradients, eye, face, iris)
    for k in range(3):
        cr.new_path()
        trace_path(cr, lids.upper)
        cr.set_line_width(lids.up * (0.35 + k * 0.35))
        set_rgba(cr, INK, 0.16 - k * 0.04)
        cr.stroke()
    cr.restore()

    # Keine Ausgabe-Verifikation: save und restore stehen in derselben Funktion ohne
    # Rückkehr dazwischen.


def _iris(pen: Pen, gradients: Gradients, eye: EyeGeometry, iris: Point) -> None:
    """Iris mit Verlauf, 110 dunklen Fasern, 40 hellen Streifen, 8 Krypten, Krause und Rand."""
    # ── Eingabe-Validierung ──
    side = eye.side
    ir = iris_radius(eye)
    cr = pen.cr

    # ── Verarbeitung ──
    stops = (
        (0.0, (58.0, 61.0, 64.0, 1.0)),
        (0.35, (125.0, 129.0, 133.0, 1.0)),
        (0.75, (95.0, 99.0, 103.0, 1.0)),
        (1.0, (42.0, 44.0, 48.0, 1.0)),
    )
    cr.new_path()
    cr.arc(iris[0], iris[1], ir, 0, FULL_TURN)
    cr.set_source(gradients.radial((*iris, 0.0), (*iris, ir), stops))
    cr.fill()
    _iris_fibers(pen, eye, iris)
    for i in range(8):
        a = eye_hash(i + 2000, side) * FULL_TURN
        r = ir * (0.55 + eye_hash(i + 2100, side) * 0.25)
        cr.new_path()
        cr.save()
        cr.translate(iris[0] + math.cos(a) * r, iris[1] + math.sin(a) * r)
        cr.rotate(a)
        cr.scale(2.2, 1.2)
        cr.arc(0.0, 0.0, 1.0, 0, FULL_TURN)
        cr.restore()
        set_rgba(cr, LASH_INK, 0.35)
        cr.fill()
    collar: list[Point] = []
    for i in range(29):
        a = i / 28 * FULL_TURN
        r = ir * (0.5 + eye_hash(i + 2200, side) * 0.07)
        collar.append((iris[0] + math.cos(a) * r, iris[1] + math.sin(a) * r))
    fine(pen, collar, 1.0, 0.5, 0.15)
    rims = ((ir * 0.92, 4.0, LASH_INK, 0.3), (ir, 2.6, (24.0, 26.0, 30.0), 0.85))
    for radius, width, color, alpha in rims:
        cr.new_path()
        cr.arc(iris[0], iris[1], radius, 0, FULL_TURN)
        cr.set_line_width(width)
        set_rgba(cr, color, alpha)
        cr.stroke()

    # Keine Ausgabe-Verifikation: save und restore der Krypten sind je Durchlauf
    # ausgeglichen.


def _iris_fibers(pen: Pen, eye: EyeGeometry, iris: Point) -> None:
    """Maserung: dunkle radiale Fasern, dazwischen helle Streifen; Lage fest über `eye_hash`."""
    # ── Eingabe-Validierung ──
    side = eye.side
    ir = iris_radius(eye)
    cr = pen.cr

    # ── Verarbeitung ──
    for i in range(110):
        a = (i + eye_hash(i + 1000, side) * 0.6) / 110 * FULL_TURN
        r0 = ir * (0.38 + eye_hash(i + 1100, side) * 0.1)
        r1 = ir * (0.68 + eye_hash(i + 1200, side) * 0.3)
        bend = (eye_hash(i + 1300, side) - 0.5) * 0.22
        mid = (r0 + r1) / 2
        fiber = [
            (iris[0] + math.cos(a) * r0, iris[1] + math.sin(a) * r0),
            (iris[0] + math.cos(a + bend) * mid, iris[1] + math.sin(a + bend) * mid),
            (iris[0] + math.cos(a) * r1, iris[1] + math.sin(a) * r1),
        ]
        width = 0.6 + eye_hash(i + 1400, side) * 0.5
        fine(pen, fiber, width, 0.22 + eye_hash(i + 1500, side) * 0.3, 0.15)
    for i in range(40):
        a = (i + 0.5) / 40 * FULL_TURN + eye_hash(i + 1600, side) * 0.1
        r0 = ir * (0.45 + eye_hash(i + 1700, side) * 0.1)
        r1 = ir * (0.7 + eye_hash(i + 1800, side) * 0.15)
        cr.new_path()
        cr.move_to(iris[0] + math.cos(a) * r0, iris[1] + math.sin(a) * r0)
        cr.line_to(iris[0] + math.cos(a) * r1, iris[1] + math.sin(a) * r1)
        cr.set_line_width(0.9)
        set_rgba(cr, (232.0, 232.0, 228.0), 0.14 + eye_hash(i + 1900, side) * 0.16)
        cr.stroke()

    # Keine Ausgabe-Verifikation: Fasern prüft fine; die Streifen liegen auf Kreisen um die
    # geprüfte Irismitte.


def _pupil(
    cr: "cairo.Context", gradients: Gradients, eye: EyeGeometry, face: FaceState, iris: Point
) -> None:
    """Pupille mit weichem Rand und zwei Glanzlichter."""
    # ── Eingabe-Validierung ──
    ir = iris_radius(eye)
    pr = pupil_radius(eye, face)

    # ── Verarbeitung ──
    stops = ((0.0, (27.0, 29.0, 32.0, 1.0)), (1.0, (27.0, 29.0, 32.0, 0.0)))
    cr.new_path()
    cr.arc(iris[0], iris[1], pr * 1.08, 0, FULL_TURN)
    cr.set_source(gradients.radial((*iris, pr * 0.7), (*iris, pr * 1.08), stops))
    cr.fill()
    glints = (
        (iris[0] - ir * 0.32, iris[1] - ir * 0.36, ir * 0.16, 0.95),
        (iris[0] + ir * 0.34, iris[1] + ir * 0.3, ir * 0.06, 0.8),
    )
    for x, y, radius, alpha in glints:
        cr.new_path()
        cr.arc(x, y, radius, 0, FULL_TURN)
        set_rgba(cr, (252.0, 252.0, 250.0), alpha)
        cr.fill()

    # Keine Ausgabe-Verifikation: Die Radien sind in iris_radius und pupil_radius geprüft.


def _upper_lash_line(pen: Pen, upper: Sequence[Point]) -> None:
    """Wimpernkranz: Keil ab 35 % der Lidlänge nach außen bis 6 px breiter, dazu Lidlinien."""
    # ── Eingabe-Validierung ──
    n = EYE_SEGMENTS
    if len(upper) != n + 1:
        raise ValueError(f"_upper_lash_line: {len(upper)} Punkte")

    # ── Verarbeitung ──
    top: list[Point] = []
    for i, p in enumerate(upper):
        w = 6 * max(0.0, (i / n - 0.35) / 0.65) ** 1.3
        top.append((p[0] + UY * w, p[1] - UX * w))
    # ein zusammenhängender Pfad: Lidlinie hin, Keiloberkante zurück
    ring = list(upper) + top[::-1]
    _check_ring(ring)
    pen.cr.new_path()
    pen.cr.move_to(ring[0][0], ring[0][1])
    for x, y in ring:
        pen.cr.line_to(x, y)
    pen.cr.close_path()
    set_rgba(pen.cr, LASH_INK, 0.82)
    pen.cr.fill()
    fine(pen, top[math.floor(n * 0.4) :], 1.0, 0.5, 0.4)
    fine(pen, upper[0:8], 1.2, 0.65, 0.3)
    for k in range(4):
        layer = [
            (p[0], p[1] + k * 0.7 * (0.25 + 0.75 * (i + 4) / n)) for i, p in enumerate(upper[4:])
        ]
        fine(pen, layer, 2.2, 0.7, 0.4)
    fine(pen, upper[6:], 3.6, 0.78, 0.3)
    fine(pen, upper[12:], 5.0, 0.7, 0.3)
    corner, prev = upper[n], upper[n - 2]
    wx, wy = corner[0] - prev[0], corner[1] - prev[1]
    wl = math.hypot(wx, wy) or 1.0
    swing = (corner[0] + wx / wl * 9, corner[1] + wy / wl * 9 - 3.5)
    fine(pen, [corner, swing], 3.0, 0.65, 0.3)

    # Keine Ausgabe-Verifikation: Der Keil ist vor dem Füllen in _check_ring geprüft, die
    # Striche in fine.


def _lash_clumps(pen: Pen, eye: EyeGeometry, upper: Sequence[Point]) -> None:
    """Zehn verklebte Wimpernbüschel aus je drei Wimpern, die zur Spitze zusammenlaufen."""
    # ── Eingabe-Validierung ──
    side = eye.side

    # ── Verarbeitung ──
    for i in range(LASH_CLUMPS):
        f = i / (LASH_CLUMPS - 1)
        t = 0.34 + f * 0.64 + (eye_hash(i + 3000, side) - 0.5) * 0.03
        wf = 0.55 + 0.55 * f  # innen dünner
        length = (8 + 23 * f**1.15) * (0.88 + eye_hash(i + 3100, side) * 0.24)
        ang = -math.pi / 2 + side * (0.15 + f * 1.05)
        k = 0.08 + 0.32 * f
        root = point_on(upper, t)
        tip_c = (root[0] + math.cos(ang) * length, root[1] + math.sin(ang) * length)
        for s3 in (-1, 0, 1):
            p = point_on(upper, max(0.0, min(1.0, t + s3 * 0.014)))
            a0 = ang + side * k
            reach = length * 0.5 / math.cos(k)
            mid = (p[0] + math.cos(a0) * reach, p[1] + math.sin(a0) * reach)
            curve = quad(p, mid, (tip_c[0] + s3 * 0.8, tip_c[1] + s3 * 0.5), 8)
            fine(pen, curve[:4], 1.8 * wf, 0.8, 0.15)
            fine(pen, curve[:7], 1.1 * wf, 0.78, 0.15)
            fine(pen, curve, 0.6, 0.75, 0.15)
        # verklebte Spitze: kurzer kräftiger Strich am Ende
        fine(pen, [lerp2(root, tip_c, 0.55), lerp2(root, tip_c, 0.85)], 1.2 * wf, 0.55, 0.1)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _crease_lines(pen: Pen, crease: Sequence[Point]) -> None:
    """Lidfalte nach den Wimpern: Schattierung zum Lid hin, Faltenlinie, heller Saum."""
    # ── Eingabe-Validierung ──
    n = EYE_SEGMENTS
    if len(crease) != n + 1:
        raise ValueError(f"_crease_lines: {len(crease)} Punkte")

    # ── Verarbeitung ──
    for k in range(3):
        d = 1.5 + k * 1.6
        shade = [(p[0] - UY * d, p[1] + UX * d) for p in crease[2 : n - 1]]
        fine(pen, shade, 2.4, 0.1 - k * 0.025, 0.5)
    fine(pen, crease[1:n], 1.3, 0.55, 0.6)
    fine(pen, [(p[0] + UY * 1.5, p[1] - UX * 1.5) for p in crease[4 : n - 3]], 0.8, 0.25, 0.6)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _outer_lashes(pen: Pen, eye: EyeGeometry, upper: Sequence[Point]) -> None:
    """Verdichtung am äußeren Winkel: fünf kurze, dunkle Wimpern."""
    # ── Eingabe-Validierung ──
    side = eye.side

    # ── Verarbeitung ──
    for i in range(5):
        f = 0.7 + 0.3 * i / 4
        p = point_on(upper, f)
        length = (9 + 10 * (f - 0.68) / 0.32) * (0.8 + park_miller_next(pen.rng) * 0.4)
        ang = -math.pi / 2 + side * (0.95 + 0.5 * (f - 0.68) / 0.32)
        a0 = ang + side * 0.3
        mid = (p[0] + math.cos(a0) * length * 0.55, p[1] + math.sin(a0) * length * 0.55)
        tip = (p[0] + math.cos(ang) * length, p[1] + math.sin(ang) * length)
        curve = quad(p, mid, tip, 6)
        fine(pen, curve[:4], 3.2, 0.8, 0.15)
        fine(pen, curve, 1.6, 0.75, 0.15)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _lower_lid(pen: Pen, eye: EyeGeometry, lower: Sequence[Point]) -> None:
    """Unterlid: Wasserlinie, Lidkante, Unterwimpern, Schatten, Tränenkarunkel."""
    # ── Eingabe-Validierung ──
    hw, side = eye.half_width, eye.side
    n = EYE_SEGMENTS

    # ── Verarbeitung ──
    fine(pen, [(x, y - 1.5) for x, y in lower[3:]], 0.8, 0.22, 0.3)
    fine(pen, lower[5:], 1.1, 0.5, 0.4)
    fine(pen, lower[1:7], 0.8, 0.28, 0.4)
    fine(pen, lower[9:], 1.9, 0.6, 0.4)
    fine(pen, lower[14:], 2.4, 0.5, 0.3)
    _lower_lashes(pen, eye, lower)
    for i in range(4, n - 2):
        p = lower[i]
        d = 6 + park_miller_next(pen.rng) * 8
        alpha = 0.035 + park_miller_next(pen.rng) * 0.025
        start = (p[0] - UY * d, p[1] + UX * d)
        end = (p[0] - UY * (d + 7) + side * 4, p[1] + UX * (d + 7))
        fine(pen, [start, end], 0.6, alpha)
    ci = local_point(eye.center, -side * hw * 0.9, hw * 0.06)
    caruncle = [
        (ci[0] - side * 3, ci[1] - 2),
        (ci[0] + side * 2, ci[1]),
        (ci[0] - side * 3, ci[1] + 3),
    ]
    fine(pen, caruncle, 0.9, 0.45, 0.2)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _lower_lashes(pen: Pen, eye: EyeGeometry, lower: Sequence[Point]) -> None:
    """Elf Unterwimpern, nach außen länger und dichter, leicht nach außen gebogen."""
    # ── Eingabe-Validierung ──
    side = eye.side
    if len(lower) != EYE_SEGMENTS + 1:
        raise ValueError(f"_lower_lashes: {len(lower)} Punkte")

    # ── Verarbeitung ──
    for i in range(LOWER_LASHES):
        if i in LOWER_LASH_SKIP:
            continue
        f = i / 12
        # Math.round: bei i = 6 ist f · 13 = 6,5 und muss auf 7 runden, nicht auf 6
        p = lower[min(EYE_SEGMENTS, 7 + js_round(f * 13))]
        length = (4 + 14 * f**1.5) * (0.9 + eye_hash(i + 3500, side) * 0.2)
        tip = (p[0] + side * length * 0.5, p[1] + length)
        mid = (p[0] + side * length * 0.15, p[1] + length * 0.55)
        curve = quad(p, mid, tip, 6)
        fine(pen, curve[:4], 1.4 + f * 0.6, 0.55 + f * 0.25, 0.15)
        fine(pen, curve, 0.8, 0.5 + f * 0.25, 0.15)

    # Keine Ausgabe-Verifikation: Jeder Strich ist in fine geprüft.


def _check_ring(ring: Sequence[Point]) -> None:
    """Wirft RuntimeError, wenn ein Punkt des Wimpernkeils nicht endlich ist."""
    # ── Eingabe-Validierung ──
    if not ring:
        raise RuntimeError("_check_ring: leerer Keil")

    # ── Verarbeitung ──
    bad = [p for p in ring if not (math.isfinite(p[0]) and math.isfinite(p[1]))]

    # ── Ausgabe-Verifikation ──
    if bad:
        raise RuntimeError(f"_check_ring: Punkte nicht endlich: {bad[:3]!r}")
