"""Strichwerkzeuge des Avatars: Zufall je Teil, Kurven, Bleistift- und Feinstrich.

Gezeichnet wird auf einen übergebenen Cairo-Kontext `cr`, in Pixeln der Vorlage
(`SRC` × `SRC`). Skalierung, Hintergrund und Linienenden setzt der Aufrufer.

Das Modul importiert Cairo nicht: Die Formen brauchen nur die Methoden des
Kontexts (`move_to`, `curve_to`, `stroke` …), und Verläufe baut `CairoGradients`,
das Cairo erst beim ersten Verlauf lädt. So lässt sich alles ohne pycairo und
ohne Bildschirm prüfen, mit einem Kontext, der die Aufrufe mitschreibt.

Abbildung der Browser-Mittel:

- `quadraticCurveTo` → `curve_to` nach der 2/3-Regel (`quadratic_to`).
- `globalAlpha` und `rgba(…)` → die Deckkraft steht in `set_source_rgba`.
- `Math.round` → `js_round`, weil Pythons `round` .5 zur geraden Zahl rundet.
- Der Zufall der Strichlage ist der Park-Miller-Generator, exakt nachgebildet;
  statt eines geteilten Zustands bekommt jeder Teil seinen eigenen (`part_seed`).
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import cairo

Point = tuple[float, float]
Rgba = tuple[float, float, float, float]  # Rot, Grün, Blau in 0..255, Deckkraft in 0..1
ColorStop = tuple[float, Rgba]
Circle = tuple[float, float, float]  # Mittelpunkt x, y und Radius

SRC = 1254  # Kantenlänge der Vorlage in Pixeln
TILT = 9 * math.pi / 180  # Neigung der Gesichtsachse
UX = math.cos(TILT)
UY = math.sin(TILT)
BOIL_AMP = 0.5  # Stärke des Linien-Zitterns
INK = (38.0, 40.0, 44.0)  # Grafit der Striche

PARK_MILLER_MODULUS = 2147483647  # 2^31 − 1
PARK_MILLER_MULTIPLIER = 16807
BOIL_PERIOD = 9973  # der Takt läuft modulo dieser Primzahl, wie im Prototyp
SEED_BASE = 17

# Ein Seed je Teil: Takt modulo BOIL_PERIOD, plus SEED_BASE, plus ein eigener Block
# von BOIL_PERIOD Werten je Teil. Die Blöcke überschneiden sich nicht, zwei Teile
# ziehen also nie dieselbe Folge. Teil 0 ist die Formel des Prototyps.
PART_BROW_LEFT = 0
PART_BROW_RIGHT = 1
PART_EYE_LEFT = 2
PART_EYE_RIGHT = 3
PART_MOUTH = 4  # vergeben an den Mund
PART_WRINKLES = 5
PART_EXTRAS = 6
PARTS = (
    PART_BROW_LEFT,
    PART_BROW_RIGHT,
    PART_EYE_LEFT,
    PART_EYE_RIGHT,
    PART_MOUTH,
    PART_WRINKLES,
    PART_EXTRAS,
)


@dataclass
class ParkMiller:
    """Zustand des Park-Miller-Generators, ganzzahlig in 1..2^31 − 2."""

    state: int


@dataclass
class Pen:
    """Ein Kontext und der Zufall des Teils, der gerade gezeichnet wird."""

    cr: "cairo.Context"
    rng: ParkMiller


class Gradients(Protocol):
    """Baut Verläufe für `cr.set_source`; Farbstopps in 0..255 und Deckkraft 0..1."""

    def radial(self, inner: Circle, outer: Circle, stops: Sequence[ColorStop]) -> object:
        """Radialer Verlauf zwischen zwei Kreisen."""
        ...

    def linear(self, start: Point, end: Point, stops: Sequence[ColorStop]) -> object:
        """Linearer Verlauf von `start` nach `end`."""
        ...


class CairoGradients:
    """Verläufe mit Cairo; Cairo wird erst beim ersten Verlauf geladen."""

    def radial(self, inner: Circle, outer: Circle, stops: Sequence[ColorStop]) -> object:
        """Ein `cairo.RadialGradient` mit den Farbstopps `stops`.

        Vorbedingung: Radien endlich und nicht negativ, mindestens ein Farbstopp.
        Nachbedingung: das Muster trägt jeden Stopp in Cairos Einheiten (0..1).
        Fehlerfälle: ValueError bei verletzter Vorbedingung; ImportError ohne pycairo.
        """
        # ── Eingabe-Validierung ──
        _check_stops(stops, "radial")
        if not all(math.isfinite(v) for v in (*inner, *outer)) or min(inner[2], outer[2]) < 0:
            raise ValueError(f"radial: Kreise {inner!r}, {outer!r} ungültig")

        # ── Verarbeitung ──
        import cairo  # erst hier, damit das Modul ohne pycairo lädt

        pattern = cairo.RadialGradient(*inner, *outer)
        for offset, color in stops:
            pattern.add_color_stop_rgba(offset, *_unit_rgba(color))

        # ── Ausgabe-Verifikation ──
        if len(pattern.get_color_stops_rgba()) != len(stops):
            raise RuntimeError("radial: Farbstopps nicht vollständig übernommen")
        return pattern

    def linear(self, start: Point, end: Point, stops: Sequence[ColorStop]) -> object:
        """Ein `cairo.LinearGradient` mit den Farbstopps `stops`.

        Vorbedingung: Punkte endlich, mindestens ein Farbstopp.
        Nachbedingung: das Muster trägt jeden Stopp in Cairos Einheiten (0..1).
        Fehlerfälle: ValueError bei verletzter Vorbedingung; ImportError ohne pycairo.
        """
        # ── Eingabe-Validierung ──
        _check_stops(stops, "linear")
        _check_points((start, end), "linear")

        # ── Verarbeitung ──
        import cairo  # erst hier, damit das Modul ohne pycairo lädt

        pattern = cairo.LinearGradient(*start, *end)
        for offset, color in stops:
            pattern.add_color_stop_rgba(offset, *_unit_rgba(color))

        # ── Ausgabe-Verifikation ──
        if len(pattern.get_color_stops_rgba()) != len(stops):
            raise RuntimeError("linear: Farbstopps nicht vollständig übernommen")
        return pattern


def part_seed(boil_tick: int, part: int) -> int:
    """Der Seed eines Teils für einen Boil-Takt.

    Vorbedingung: `boil_tick` eine ganze Zahl ≥ 0, `part` einer der `PARTS`.
    Nachbedingung: ein gültiger Park-Miller-Zustand; gleicher Takt und Teil ergeben
    denselben Seed, verschiedene Teile im selben Takt verschiedene.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    check_tick(boil_tick, "part_seed")
    if part not in PARTS or isinstance(part, bool):
        raise ValueError(f"part_seed: Teil {part!r} unbekannt")

    # ── Verarbeitung ──
    seed = boil_tick % BOIL_PERIOD + SEED_BASE + BOIL_PERIOD * part

    # ── Ausgabe-Verifikation ──
    if not 0 < seed < PARK_MILLER_MODULUS:
        raise RuntimeError(f"part_seed: Seed {seed} außerhalb des Generators")
    return seed


def park_miller_next(rng: ParkMiller) -> float:
    """Der nächste Wert des Generators in (0, 1); rückt den Zustand weiter.

    Dieselbe Formel wie `rnd` im Prototyp: Zustand mal 16807 modulo 2^31 − 1,
    geteilt durch 2^31 − 1. Python rechnet die Ganzzahl exakt, der Browser auch,
    weil das Produkt unter 2^53 bleibt.
    Vorbedingung: Zustand ganzzahlig in 1..2^31 − 2.
    Nachbedingung: Wert in (0, 1), Zustand fortgeschrieben.
    Fehlerfälle: ValueError bei ungültigem Zustand (ein Zustand 0 bliebe für immer 0).
    """
    # ── Eingabe-Validierung ──
    state = rng.state
    if not isinstance(state, int) or isinstance(state, bool):
        raise ValueError(f"park_miller_next: Zustand {state!r} keine ganze Zahl")
    if not 0 < state < PARK_MILLER_MODULUS:
        raise ValueError(f"park_miller_next: Zustand {state} außerhalb 1..2^31−2")

    # ── Verarbeitung ──
    rng.state = state * PARK_MILLER_MULTIPLIER % PARK_MILLER_MODULUS
    value = rng.state / PARK_MILLER_MODULUS

    # ── Ausgabe-Verifikation ──
    if not 0.0 < value < 1.0:
        raise RuntimeError(f"park_miller_next: Wert {value} außerhalb (0, 1)")
    return value


def js_round(x: float) -> int:
    """Rundet wie `Math.round` im Browser: .5 immer aufwärts, auch bei negativen Zahlen.

    Vorbedingung: `x` endlich.
    Nachbedingung: die ganze Zahl `floor(x + 0.5)`.
    Fehlerfälle: ValueError bei nicht endlichem `x`.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(x):
        raise ValueError(f"js_round: {x!r} nicht endlich")

    # ── Verarbeitung ──
    result = math.floor(x + 0.5)

    # ── Ausgabe-Verifikation ──
    if abs(result - x) > 0.5:
        raise RuntimeError(f"js_round: {x} ergab {result}")
    return result


def local_point(center: Point, lx: float, ly: float) -> Point:
    """Ein Punkt in den Achsen des geneigten Gesichts (`L` im Prototyp).

    `lx` läuft quer, `ly` längs der um `TILT` gedrehten Gesichtsachse.
    Vorbedingung: alle Werte endlich.
    Nachbedingung: ein endlicher Punkt in Pixeln der Vorlage.
    Fehlerfälle: ValueError bei nicht endlicher Eingabe.
    """
    # ── Eingabe-Validierung ──
    if not all(math.isfinite(v) for v in (*center, lx, ly)):
        raise ValueError(f"local_point: {center!r}, {lx!r}, {ly!r} nicht endlich")

    # ── Verarbeitung ──
    point = (center[0] + lx * UX - ly * UY, center[1] + lx * UY + ly * UX)

    # ── Ausgabe-Verifikation ──
    _check_points((point,), "local_point")
    return point


def quad(p0: Point, ctrl: Point, p1: Point, n: int = 12) -> list[Point]:
    """`n + 1` Punkte auf der quadratischen Bézierkurve von `p0` über `ctrl` nach `p1`.

    Vorbedingung: Punkte endlich, `n` ≥ 1.
    Nachbedingung: erster Punkt `p0`, letzter `p1`, gleichmäßig im Parameter.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    _check_points((p0, ctrl, p1), "quad")
    if n < 1:
        raise ValueError(f"quad: n = {n} < 1")

    # ── Verarbeitung ──
    points: list[Point] = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        points.append(
            (
                u * u * p0[0] + 2 * u * t * ctrl[0] + t * t * p1[0],
                u * u * p0[1] + 2 * u * t * ctrl[1] + t * t * p1[1],
            )
        )

    # ── Ausgabe-Verifikation ──
    if len(points) != n + 1:
        raise RuntimeError(f"quad: {len(points)} statt {n + 1} Punkte")
    return points


def lerp2(a: Point, b: Point, t: float) -> Point:
    """Der Punkt bei `t` auf der Strecke von `a` nach `b`.

    Vorbedingung: Punkte und `t` endlich.
    Nachbedingung: ein endlicher Punkt.
    Fehlerfälle: ValueError bei nicht endlicher Eingabe.
    """
    # ── Eingabe-Validierung ──
    _check_points((a, b), "lerp2")
    if not math.isfinite(t):
        raise ValueError(f"lerp2: t = {t!r} nicht endlich")

    # ── Verarbeitung ──
    point = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    # ── Ausgabe-Verifikation ──
    _check_points((point,), "lerp2")
    return point


def point_on(points: Sequence[Point], t: float) -> Point:
    """Der Punkt beim Anteil `t` entlang einer Punktfolge, linear zwischen Nachbarn.

    Wie im Prototyp: Index `min(n − 1, floor(t · n))`, dann linear zum nächsten.
    Vorbedingung: mindestens zwei Punkte, `t` in 0..1.
    Nachbedingung: ein Punkt auf der Folge.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    if len(points) < 2:
        raise ValueError(f"point_on: {len(points)} Punkte, mindestens zwei nötig")
    if not 0.0 <= t <= 1.0:
        raise ValueError(f"point_on: t = {t!r} außerhalb 0..1")

    # ── Verarbeitung ──
    n = len(points) - 1
    j = min(n - 1, math.floor(t * n))
    point = lerp2(points[j], points[j + 1], t * n - j)

    # ── Ausgabe-Verifikation ──
    _check_points((point,), "point_on")
    return point


def quadratic_to(cr: "cairo.Context", start: Point, ctrl: Point, end: Point) -> None:
    """Eine quadratische Kurve als kubische (`quadraticCurveTo` → `curve_to`).

    2/3-Regel: Die Kontrollpunkte liegen bei `start + 2/3 · (ctrl − start)` und
    `end + 2/3 · (ctrl − end)`; die kubische Kurve ist dann dieselbe Kurve.
    Vorbedingung: `start` ist der aktuelle Punkt von `cr`, alle Punkte endlich.
    Nachbedingung: ein `curve_to` bis `end` auf `cr`.
    Fehlerfälle: ValueError bei nicht endlichen Punkten.
    """
    # ── Eingabe-Validierung ──
    _check_points((start, ctrl, end), "quadratic_to")

    # ── Verarbeitung ──
    c1 = (start[0] + 2 / 3 * (ctrl[0] - start[0]), start[1] + 2 / 3 * (ctrl[1] - start[1]))
    c2 = (end[0] + 2 / 3 * (ctrl[0] - end[0]), end[1] + 2 / 3 * (ctrl[1] - end[1]))

    # ── Ausgabe-Verifikation ──
    _check_points((c1, c2), "quadratic_to")
    cr.curve_to(c1[0], c1[1], c2[0], c2[1], end[0], end[1])


def trace_path(cr: "cairo.Context", points: Sequence[Point]) -> None:
    """Ein weicher Teilpfad durch die Punkte (`tracePath` im Prototyp).

    Beginnt mit `move_to` am ersten Punkt, legt durch die inneren Punkte
    quadratische Kurven zu den Mitten der Nachbarn und endet mit `line_to` am
    letzten Punkt. Den Pfad beginnt (`new_path`) und beendet der Aufrufer.
    Vorbedingung: mindestens zwei endliche Punkte.
    Nachbedingung: ein Teilpfad auf `cr`, dessen Punkte alle endlich sind.
    Fehlerfälle: ValueError bei weniger als zwei oder nicht endlichen Punkten.
    """
    # ── Eingabe-Validierung ──
    if len(points) < 2:
        raise ValueError(f"trace_path: {len(points)} Punkte, mindestens zwei nötig")
    _check_points(points, "trace_path")

    # ── Verarbeitung ──
    cr.move_to(points[0][0], points[0][1])
    current = points[0]
    for i in range(1, len(points) - 1):
        nxt = points[i + 1]
        end = ((points[i][0] + nxt[0]) / 2, (points[i][1] + nxt[1]) / 2)
        quadratic_to(cr, current, points[i], end)
        current = end
    last = points[-1]

    # ── Ausgabe-Verifikation ──
    # Jeder Punkt ist oben geprüft, jeder Kontrollpunkt in quadratic_to.
    cr.line_to(last[0], last[1])


def set_rgba(cr: "cairo.Context", rgb: tuple[float, float, float], alpha: float) -> None:
    """Setzt eine Farbe in 0..255 mit Deckkraft 0..1 als Quelle (`rgba(…)` im Prototyp).

    Vorbedingung: Farbkanäle in 0..255, Deckkraft in 0..1.
    Nachbedingung: `set_source_rgba` mit Kanälen in 0..1.
    Fehlerfälle: ValueError außerhalb der Bereiche — der Browser begrenzte still.
    """
    # ── Eingabe-Validierung ──
    if not all(0.0 <= c <= 255.0 for c in rgb) or not 0.0 <= alpha <= 1.0:
        raise ValueError(f"set_rgba: Farbe {rgb!r}, Deckkraft {alpha!r} außerhalb")

    # ── Verarbeitung ──
    red, green, blue, opacity = _unit_rgba((*rgb, alpha))

    # ── Ausgabe-Verifikation ──
    # _unit_rgba teilt nur durch 255; die Bereiche sind oben geprüft.
    cr.set_source_rgba(red, green, blue, opacity)


def fine(
    pen: Pen, points: Sequence[Point], width: float, alpha: float, jitter: float = 0.4
) -> None:
    """Ein einzelner feiner Strich, je Punkt verwackelt (`fine` im Prototyp).

    Jeder Punkt wird in x und y um `(Zufall − 0,5) · jitter · BOIL_AMP` verschoben,
    erst x, dann y, Punkt für Punkt — dieselbe Reihenfolge der Ziehungen wie im
    Prototyp.
    Vorbedingung: mindestens zwei endliche Punkte, Breite ≥ 0, Deckkraft 0..1.
    Nachbedingung: ein Strich in Grafit auf `pen.cr`; `pen.rng` ist um zwei Werte je
    Punkt weitergerückt.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    _check_stroke(width, alpha, jitter, "fine")

    # ── Verarbeitung ──
    shaken = _shake(pen.rng, points, jitter)
    pen.cr.new_path()
    trace_path(pen.cr, shaken)
    pen.cr.set_line_width(width)
    set_rgba(pen.cr, INK, alpha)

    # ── Ausgabe-Verifikation ──
    # Die Punkte prüft trace_path vor der Übergabe, Farbe und Breite set_rgba und oben.
    pen.cr.stroke()


def pencil(
    pen: Pen, points: Sequence[Point], width: float, alpha: float, jitter: float = 1.2
) -> None:
    """Ein Bleistiftstrich in zwei Lagen (`pencil` im Prototyp).

    Erste Lage mit voller Breite und Deckkraft, zweite neu verwackelt mit 60 %
    der Breite und 45 % der Deckkraft.
    Vorbedingung: wie `fine`.
    Nachbedingung: zwei Striche auf `pen.cr`.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    _check_stroke(width, alpha, jitter, "pencil")

    # ── Verarbeitung ──
    for layer in range(2):
        shaken = _shake(pen.rng, points, jitter)
        pen.cr.new_path()
        trace_path(pen.cr, shaken)
        pen.cr.set_line_width(width * 0.6 if layer else width)
        set_rgba(pen.cr, INK, alpha * 0.45 if layer else alpha)
        pen.cr.stroke()

    # Keine Ausgabe-Verifikation: Jede Lage ist in trace_path und set_rgba geprüft, bevor
    # sie den Kontext erreicht.


def check_tick(boil_tick: int, where: str) -> None:
    """Wirft ValueError, wenn `boil_tick` keine ganze Zahl ≥ 0 ist (ein bool zählt nicht)."""
    # ── Eingabe-Validierung ──
    if not isinstance(boil_tick, int) or isinstance(boil_tick, bool):
        raise ValueError(f"{where}: Takt {boil_tick!r} keine ganze Zahl")

    # ── Verarbeitung ──
    if boil_tick < 0:
        raise ValueError(f"{where}: Takt {boil_tick} negativ")

    # Keine Ausgabe-Verifikation: Rückkehr heißt gültig.


def _check_points(points: Sequence[Point], where: str) -> None:
    """Wirft ValueError, wenn ein Punkt nicht aus zwei endlichen Zahlen besteht."""
    # ── Eingabe-Validierung ──
    if not points:
        raise ValueError(f"{where}: keine Punkte")

    # ── Verarbeitung ──
    for point in points:
        if len(point) != 2 or not (math.isfinite(point[0]) and math.isfinite(point[1])):
            raise ValueError(f"{where}: Punkt {point!r} nicht endlich")

    # Keine Ausgabe-Verifikation: Rückkehr heißt alle Punkte endlich.


def _check_stroke(width: float, alpha: float, jitter: float, where: str) -> None:
    """Wirft ValueError bei negativer oder nicht endlicher Breite, Deckkraft oder Zittern."""
    # ── Eingabe-Validierung ──
    values = (width, alpha, jitter)

    # ── Verarbeitung ──
    if not all(math.isfinite(v) for v in values) or width < 0 or jitter < 0:
        raise ValueError(f"{where}: Breite {width!r}, Zittern {jitter!r} ungültig")
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"{where}: Deckkraft {alpha!r} außerhalb 0..1")

    # Keine Ausgabe-Verifikation: Rückkehr heißt gültig.


def _check_stops(stops: Sequence[ColorStop], where: str) -> None:
    """Wirft ValueError, wenn Farbstopps fehlen oder außerhalb ihrer Bereiche liegen."""
    # ── Eingabe-Validierung ──
    if not stops:
        raise ValueError(f"{where}: keine Farbstopps")

    # ── Verarbeitung ──
    for offset, (red, green, blue, alpha) in stops:
        in_range = all(0.0 <= c <= 255.0 for c in (red, green, blue)) and 0.0 <= alpha <= 1.0
        if not 0.0 <= offset <= 1.0 or not in_range:
            raise ValueError(f"{where}: Farbstopp {offset!r}, {(red, green, blue, alpha)!r}")

    # Keine Ausgabe-Verifikation: Rückkehr heißt gültig.


def _unit_rgba(color: Rgba) -> Rgba:
    """Rechnet Farbkanäle von 0..255 in Cairos 0..1 um; die Deckkraft bleibt."""
    # ── Eingabe-Validierung ──
    red, green, blue, alpha = color

    # ── Verarbeitung ──
    result = (red / 255.0, green / 255.0, blue / 255.0, alpha)

    # ── Ausgabe-Verifikation ──
    if not all(0.0 <= c <= 1.0 for c in result):
        raise ValueError(f"_unit_rgba: Farbe {color!r} außerhalb der Bereiche")
    return result


def _shake(rng: ParkMiller, points: Sequence[Point], jitter: float) -> list[Point]:
    """Verwackelt jeden Punkt um bis zu ±jitter·BOIL_AMP/2, erst x, dann y."""
    # ── Eingabe-Validierung ──
    _check_points(points, "_shake")

    # ── Verarbeitung ──
    shaken: list[Point] = []
    for x, y in points:
        dx = (park_miller_next(rng) - 0.5) * jitter * BOIL_AMP
        dy = (park_miller_next(rng) - 0.5) * jitter * BOIL_AMP
        shaken.append((x + dx, y + dy))

    # ── Ausgabe-Verifikation ──
    if len(shaken) != len(points):
        raise RuntimeError("_shake: Punktzahl verändert")
    return shaken
