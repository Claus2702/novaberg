"""Leerlauf des Avatars: was das Gesicht zwischen zwei Antworten tut.

Rein — kein GTK, kein Cairo, kein Netz, keine Uhr. Die Zeit kommt als Zahl (ms ab
dem Start des Leerlaufs), die Ereignisse des Clients kommen über `IdleLogic.post`,
und `IdleLogic.step` liefert je Bild die Ziele aller Kanäle, die Öffnung des Lids,
ω des Gesichts und den Zustand. Ein Ereignis wird im ersten Schritt behandelt, der
nicht vor ihm liegt.

Der Leerlauf plant wie der Referenzgenerator: derselbe Zufall (mulberry32), dieselbe
Reihenfolge der Ziehungen, dieselben Regeln und Zahlen (`avatar.idle_catalog`). Bei
gleichem Startwert und gleichen Ereignissen plant er dieselben Zustände, Formen,
Dauern, Blickpunkte und Lidschläge; das prüfen die Referenzwerte unter
`tests/avatar_reference/idle.json`. Wer hier eine Rechnung umstellt, ändert die
Ziehungen — auch eine Summe in anderer Reihenfolge rundet anders.
"""

import logging
import math
import re
from bisect import bisect_right
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import ClassVar

from avatar import idle_catalog as catalog
from avatar.expression import JAW_FACTOR_DEFAULT, MOD_AROUSAL, SECTORS, face_target
from avatar.face import PROTOTYPE_KEYS, FaceState
from avatar.idle_catalog import FORMS, FormSpec, GazePoint, IdleState
from avatar.idle_status import (
    NOTE_AFTERGLOW,
    NOTE_INHALING,
    NOTE_PLAYBACK,
    NOTE_WAITING,
    SOURCE_NOVA,
    SOURCE_PIXIE,
    BandItem,
    IdleStatus,
    StatusForm,
    StatusNext,
    StatusSpan,
)

logger = logging.getLogger(__name__)

_UINT32 = 0xFFFFFFFF
_TWO_POW_32 = 4294967296.0
_KEYS: tuple[str, ...] = tuple(PROTOTYPE_KEYS.values())
_AU_SIDE = re.compile(r"au\d+[LR]")

ORIGIN_TURN = "turn"
ORIGIN_IMPULSE = "impulse"
_PLAN_CYCLE = "cycle"
_PLAN_ANSWER = "answer"
_PLAN_INHALE = "inhale"
_Note = tuple[str | None, float | None, float | None]
_MAX_FORMS_PER_STEP = 60
_FALLBACK_REPLAN_MS = 3000.0  # hängt der Plan weiter zurück, beginnt der nächste jetzt

# Lockerungen der Abfolgeregeln, in dieser Reihenfolge versucht.
_ALL_RULES = ("R1", "R2", "R4", "R5", "R7", "WL")
_RELAXATIONS: tuple[tuple[str, ...], ...] = (
    (), ("R5",), ("R7",), ("R4",), ("R5", "R7"), ("R5", "R4"), ("R4", "R7"), ("R5", "R4", "R7"),
    ("R5", "R4", "R7", "R2"), _ALL_RULES,
)


# ---------------------------------------------------------------- Zufall -------


def _imul(a: int, b: int) -> int:
    """Multiplikation modulo 2³² wie `Math.imul`, auf vorzeichenlosen Werten.

    Vorbedingung: a und b liegen in 0..2³²−1.
    Nachbedingung: das Bitmuster des Produkts, vorzeichenlos.
    Fehlerfälle: ein Wert außerhalb 32 Bit.
    """
    # ── Eingabe-Validierung ──
    if not (0 <= a <= _UINT32 and 0 <= b <= _UINT32):
        raise ValueError(f"_imul: Wert außerhalb 32 Bit ({a}, {b})")

    # ── Verarbeitung ──
    product = (a * b) & _UINT32

    # ── Ausgabe-Verifikation ──
    if product > _UINT32:
        raise RuntimeError(f"_imul: Produkt {product} außerhalb 32 Bit")
    return product


class Mulberry32:
    """Der Zufall des Leerlaufs: mulberry32 mit Startwert, wiederholbar.

    `draws` zählt die Ziehungen. Ihre Reihenfolge ist Teil des Vertrags mit dem
    Referenzgenerator: Eine Ziehung mehr oder weniger verschiebt alles danach.
    """

    def __init__(self, seed: int) -> None:
        """Setzt den Startwert; wie im Generator wird er vorzeichenlos, 0 wird 1.

        Vorbedingung: seed ist eine ganze Zahl.
        Nachbedingung: der Zustand liegt in 1..2³²−1, noch keine Ziehung.
        Fehlerfälle: seed ist keine ganze Zahl.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError(f"Mulberry32: Startwert {seed!r} ist keine ganze Zahl")

        # ── Verarbeitung ──
        self.state = (seed & _UINT32) or 1
        self.draws = 0

        # ── Ausgabe-Verifikation ──
        if not 1 <= self.state <= _UINT32:
            raise RuntimeError(f"Mulberry32: Zustand {self.state} außerhalb 32 Bit")

    def next(self) -> float:
        """Die nächste Zahl in [0, 1) — dieselbe Folge wie der Generator.

        Vorbedingung: der Zustand liegt in 32 Bit.
        Nachbedingung: eine Zahl in [0, 1); `draws` ist um eins gewachsen.
        Fehlerfälle: ein Zustand außerhalb 32 Bit (von außen überschrieben).
        """
        # ── Eingabe-Validierung ──
        if not 0 <= self.state <= _UINT32:
            raise RuntimeError(f"Mulberry32: Zustand {self.state} außerhalb 32 Bit")

        # ── Verarbeitung ──
        self.state = (self.state + 0x6D2B79F5) & _UINT32
        t = self.state
        t = _imul(t ^ (t >> 15), t | 1)
        t ^= (t + _imul(t ^ (t >> 7), t | 61)) & _UINT32
        value = ((t ^ (t >> 14)) & _UINT32) / _TWO_POW_32
        self.draws += 1

        # ── Ausgabe-Verifikation ──
        if not 0.0 <= value < 1.0:
            raise RuntimeError(f"Mulberry32: Zahl {value} außerhalb [0, 1)")
        return value

    def uniform(self, lo: float, hi: float) -> float:
        """Gleichverteilt zwischen lo und hi, eine Ziehung.

        Vorbedingung: lo und hi sind endlich.
        Nachbedingung: ein Wert zwischen lo und hi.
        Fehlerfälle: nicht endliche Grenzen.
        """
        # ── Eingabe-Validierung ──
        if not (math.isfinite(lo) and math.isfinite(hi)):
            raise ValueError(f"uniform: Grenzen nicht endlich ({lo}, {hi})")

        # ── Verarbeitung ──
        value = lo + (hi - lo) * self.next()

        # ── Ausgabe-Verifikation ──
        if not min(lo, hi) <= value <= max(lo, hi):
            raise RuntimeError(f"uniform: {value} außerhalb [{lo}, {hi}]")
        return value

    def coin(self) -> int:
        """Eine Seite, −1 oder 1, eine Ziehung.

        Vorbedingung: keine.
        Nachbedingung: −1 bei einer Zahl unter 0,5, sonst 1.
        Fehlerfälle: keine über `next` hinaus.
        """
        # ── Eingabe-Validierung ──
        draws_before = self.draws

        # ── Verarbeitung ──
        side = -1 if self.next() < 0.5 else 1

        # ── Ausgabe-Verifikation ──
        if self.draws != draws_before + 1:
            raise RuntimeError("coin: nicht genau eine Ziehung")
        return side

    def exponential(self, mean: float) -> float:
        """Exponentialverteilt mit Mittel `mean`, eine Ziehung.

        Vorbedingung: mean ist endlich und positiv.
        Nachbedingung: ein Wert ≥ 0.
        Fehlerfälle: ein Mittel ≤ 0 oder nicht endlich.
        """
        # ── Eingabe-Validierung ──
        if not (math.isfinite(mean) and mean > 0):
            raise ValueError(f"exponential: Mittel {mean} nicht positiv")

        # ── Verarbeitung ──
        value = -math.log(1 - self.next()) * mean

        # ── Ausgabe-Verifikation ──
        if not (math.isfinite(value) and value >= 0):
            raise RuntimeError(f"exponential: {value} nicht ≥ 0")
        return value

    def gamma3(self, mean: float) -> float:
        """Gamma mit Form 3 und Mittel `mean`: drei Exponentialziehungen mit mean/3, summiert.

        Gleicher Mittelwert wie eine Exponentialziehung, aber seltener sehr kurz oder
        sehr lang. Die Summe läuft von links, wie im Generator.
        Vorbedingung: mean ist endlich und positiv.
        Nachbedingung: ein Wert ≥ 0; `draws` ist um drei gewachsen.
        Fehlerfälle: ein Mittel ≤ 0 oder nicht endlich.
        """
        # ── Eingabe-Validierung ──
        if not (math.isfinite(mean) and mean > 0):
            raise ValueError(f"gamma3: Mittel {mean} nicht positiv")
        draws_before = self.draws

        # ── Verarbeitung ──
        third = mean / 3
        value = self.exponential(third) + self.exponential(third) + self.exponential(third)

        # ── Ausgabe-Verifikation ──
        if self.draws != draws_before + 3:
            raise RuntimeError("gamma3: nicht genau drei Ziehungen")
        return value

    def triangle(self, lo: float, peak: float, hi: float) -> float:
        """Dreiecksverteilung über lo..hi mit Gipfel bei `peak`; ohne Spanne lo.

        Vorbedingung: lo ≤ hi, alle endlich.
        Nachbedingung: ein Wert in [lo, hi]; ohne Spanne (unter 1e-6) lo, ohne Ziehung.
        Fehlerfälle: hi < lo oder nicht endliche Werte.
        """
        # ── Eingabe-Validierung ──
        if not all(math.isfinite(v) for v in (lo, peak, hi)) or hi < lo:
            raise ValueError(f"triangle: ungültige Grenzen ({lo}, {peak}, {hi})")

        # ── Verarbeitung ──
        if hi - lo < 1e-6:
            return lo
        c = _clamp(peak, lo, hi)
        u = self.next()
        share = (c - lo) / (hi - lo)
        if u < share:
            value = lo + math.sqrt(u * (hi - lo) * (c - lo))
        else:
            value = hi - math.sqrt((1 - u) * (hi - lo) * (hi - c))

        # ── Ausgabe-Verifikation ──
        if not lo - 1e-9 <= value <= hi + 1e-9:
            raise RuntimeError(f"triangle: {value} außerhalb [{lo}, {hi}]")
        return value


def head_seed(seed: int) -> int:
    """Der Startwert der Zufallsquelle des Kopfs, aus dem des Leerlaufs wie im Generator.

    Der Startwert wird vorzeichenlos (0 wird 1), dann imul mit 0x9E3779B1, xor
    0x85EBCA6B; 0 wird 1. So zieht der Plan aus seiner Quelle genau wie ohne Kopf.
    Vorbedingung: seed ist eine ganze Zahl.
    Nachbedingung: ein Startwert in 1..2³²−1.
    Fehlerfälle: seed ist keine ganze Zahl.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise TypeError(f"head_seed: Startwert {seed!r} ist keine ganze Zahl")

    # ── Verarbeitung ──
    base = (seed & _UINT32) or 1
    value = ((_imul(base, 0x9E3779B1) ^ 0x85EBCA6B) & _UINT32) or 1

    # ── Ausgabe-Verifikation ──
    if not 1 <= value <= _UINT32:
        raise RuntimeError(f"head_seed: {value} außerhalb 32 Bit")
    return value


# ---------------------------------------------------------------- Rechnen ------


def _clamp(x: float, lo: float, hi: float) -> float:
    """Begrenzt x auf lo..hi wie `Math.max(lo, Math.min(hi, x))`.

    Vorbedingung: lo ≤ hi.
    Nachbedingung: ein Wert in [lo, hi].
    Fehlerfälle: lo > hi.
    """
    # ── Eingabe-Validierung ──
    if lo > hi:
        raise ValueError(f"_clamp: Grenzen vertauscht ({lo}, {hi})")

    # ── Verarbeitung ──
    value = max(lo, min(hi, x))

    # ── Ausgabe-Verifikation ──
    if not lo <= value <= hi:
        raise RuntimeError(f"_clamp: {value} außerhalb [{lo}, {hi}] (x = {x})")
    return value


def _smoothstep(x: float) -> float:
    """Glatter Übergang 0 → 1 über x in 0..1, außerhalb begrenzt.

    Vorbedingung: x ist endlich.
    Nachbedingung: ein Wert in [0, 1].
    Fehlerfälle: x nicht endlich.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(x):
        raise ValueError(f"_smoothstep: {x} nicht endlich")

    # ── Verarbeitung ──
    t = _clamp(x, 0.0, 1.0)
    value = t * t * (3 - 2 * t)

    # ── Ausgabe-Verifikation ──
    if not 0.0 <= value <= 1.0:
        raise RuntimeError(f"_smoothstep: {value} außerhalb [0, 1]")
    return value


def _hypot(dx: float, dy: float) -> float:
    """Länge eines Vektors, gerechnet wie `Math.hypot` im Referenzbrowser.

    Normiert auf den größeren Betrag und kompensiert summiert; so fällt ein
    Vergleich gegen eine Schwelle (0,25 oder 0,4) wie im Generator aus, auch wo
    `math.hypot` im letzten Bit anders rundete.
    Vorbedingung: dx und dy sind endlich.
    Nachbedingung: eine Länge ≥ 0.
    Fehlerfälle: nicht endliche Werte.
    """
    # ── Eingabe-Validierung ──
    if not (math.isfinite(dx) and math.isfinite(dy)):
        raise ValueError(f"_hypot: nicht endlich ({dx}, {dy})")

    # ── Verarbeitung ──
    values = (abs(dx), abs(dy))
    peak = max(values)
    if peak == 0:
        return 0.0
    total = 0.0
    compensation = 0.0
    for value in values:
        n = value / peak
        summand = n * n - compensation
        preliminary = total + summand
        compensation = (preliminary - total) - summand
        total = preliminary
    length = math.sqrt(total) * peak

    # ── Ausgabe-Verifikation ──
    if not length >= peak:
        raise RuntimeError(f"_hypot: {length} kürzer als der größere Betrag {peak}")
    return length


def _valence(sector: int, arousal: float) -> float:
    """Valenz einer Emotion: moderat unter, intensiv ab MOD_AROUSAL; neutral und kaum erregt 0.

    Vorbedingung: sector in 0–8.
    Nachbedingung: eine Valenz in −1..1.
    Fehlerfälle: ein Sektor außerhalb 0–8.
    """
    # ── Eingabe-Validierung ──
    if not 0 <= sector < len(catalog.VALENCE):
        raise ValueError(f"_valence: Sektor {sector} unbekannt")

    # ── Verarbeitung ──
    if sector == 0 or arousal < 0.05:
        value = 0.0
    else:
        value = catalog.VALENCE[sector][1 if arousal >= MOD_AROUSAL else 0]

    # ── Ausgabe-Verifikation ──
    if not -1.0 <= value <= 1.0:
        raise RuntimeError(f"_valence: {value} außerhalb −1..1")
    return value


def _basis(sector: int, arousal: float) -> dict[str, float]:
    """Die Emotionsbasis: `face_target` als Werte je Kurzname des Prototyps.

    Vorbedingung: sector in 0–8, arousal in 0..1.
    Nachbedingung: ein Wert je Kanal, alle endlich.
    Fehlerfälle: ein Kanal fehlt.
    """
    # ── Eingabe-Validierung ──
    if not 0 <= sector < len(catalog.VALENCE):
        raise ValueError(f"_basis: Sektor {sector} unbekannt")

    # ── Verarbeitung ──
    target = face_target(sector, arousal)
    values = {key: getattr(target, name) for name, key in PROTOTYPE_KEYS.items()}

    # ── Ausgabe-Verifikation ──
    if len(values) != len(_KEYS):
        raise RuntimeError(f"_basis: {len(values)} statt {len(_KEYS)} Kanäle")
    return values


def _noise(t: float, k: int) -> float:
    """Glattes Rauschen eines Kanals: drei Sinus, Phase je Kanal aus k.

    Vorbedingung: t endlich, k ≥ 1.
    Nachbedingung: ein Wert in −1..1.
    Fehlerfälle: k < 1.
    """
    # ── Eingabe-Validierung ──
    if k < 1:
        raise ValueError(f"_noise: Kanal {k} < 1")

    # ── Verarbeitung ──
    s = k * 1.618
    value = (math.sin(t * 0.00071 + s) + 0.6 * math.sin(t * 0.00173 + 2.3 * s)
             + 0.35 * math.sin(t * 0.00419 + 4.1 * s)) / 1.95

    # ── Ausgabe-Verifikation ──
    if not -1.0 <= value <= 1.0:
        raise RuntimeError(f"_noise: {value} außerhalb −1..1")
    return value


def blink_rate(state: IdleState, sector: int, energy: float, form_id: str) -> float:
    """Die Rate der Lidschläge je Minute in einem Zustand.

    Grundrate des Zustands + 12·E; Angst +6, Trauer −2, während F4 +3; begrenzt
    auf 8–32. Ärger beschleunigt nicht.
    Vorbedingung: ein Zustand, sector in 0–8, energy in 0..1.
    Nachbedingung: eine Rate in 8..32.
    Fehlerfälle: unbekannter Zustand oder Sektor.
    """
    # ── Eingabe-Validierung ──
    if state not in catalog.BLINK_BASE_RATE:
        raise ValueError(f"blink_rate: Zustand {state!r} unbekannt")
    if not 0 <= sector < len(catalog.VALENCE):
        raise ValueError(f"blink_rate: Sektor {sector} unbekannt")

    # ── Verarbeitung ──
    rate = catalog.BLINK_BASE_RATE[state] + catalog.BLINK_ENERGY_RATE * energy
    if sector == catalog.SECTOR_ANXIETY:
        rate += 6
    if sector == catalog.SECTOR_SADNESS:
        rate -= 2
    if form_id == "F4":
        rate += 3
    rate = _clamp(rate, catalog.BLINK_RATE_MIN, catalog.BLINK_RATE_MAX)

    # ── Ausgabe-Verifikation ──
    if not catalog.BLINK_RATE_MIN <= rate <= catalog.BLINK_RATE_MAX:
        raise RuntimeError(f"blink_rate: {rate} außerhalb 8..32")
    return rate


def _sector_of(name: object) -> int:
    """Der Sektor eines kanonischen Namens; ein unbekannter ergibt eine Error-Zeile und 0.

    Vorbedingung: keine — der Name kommt von außen.
    Nachbedingung: ein Sektor in 0–8.
    Fehlerfälle: ein Name außerhalb des Kanons — laut ins Protokoll, neutral.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(name, str) or name not in catalog.SECTOR_BY_NAME:
        logger.error(f"Leerlauf: Emotion {name!r} nicht im Kanon — neutral")
        return 0

    # ── Verarbeitung ──
    sector = catalog.SECTOR_BY_NAME[name]

    # ── Ausgabe-Verifikation ──
    if not 0 <= sector < len(catalog.VALENCE):
        raise RuntimeError(f"_sector_of: Sektor {sector} für {name!r} außerhalb 0–8")
    return sector


def _arousal_of(value: object, source: str) -> float:
    """Ein Arousal von außen: begrenzt auf 0..1; keine endliche Zahl ergibt 0 und eine Error-Zeile.

    Vorbedingung: keine — der Wert kommt von außen.
    Nachbedingung: ein Wert in 0..1.
    Fehlerfälle: keine endliche Zahl — Error-Zeile, 0; außerhalb 0..1 — Warning-Zeile.
    """
    # ── Eingabe-Validierung ──
    is_number = isinstance(value, int | float) and not isinstance(value, bool)
    if not is_number or not math.isfinite(value):
        logger.error(f"Leerlauf: Arousal {value!r} ({source}) keine endliche Zahl — 0")
        return 0.0

    # ── Verarbeitung ──
    clamped = max(0.0, min(1.0, float(value)))
    if clamped != value:
        logger.warning(f"Leerlauf: Arousal {value!r} ({source}) außerhalb 0..1, begrenzt")

    # ── Ausgabe-Verifikation ──
    if not 0.0 <= clamped <= 1.0:
        raise RuntimeError(f"_arousal_of: {clamped} außerhalb 0..1")
    return clamped


# ---------------------------------------------------------------- Ereignisse ---


@dataclass(frozen=True)
class Mood:
    """Eine Emotion als kanonischer Name mit Arousal in 0..1."""

    emotion: str
    arousal: float


NEUTRAL_MOOD = Mood("neutral", 0.0)


@dataclass(frozen=True)
class TurnBegins:
    """Der Client sendet eine Nachricht des Nutzers."""

    event_type: ClassVar[str] = "turn_beginnt"
    at_ms: float


@dataclass(frozen=True)
class TurnFailed:
    """Der Turn ist gescheitert; es kommt keine Antwort."""

    event_type: ClassVar[str] = "turn_gescheitert"
    at_ms: float


@dataclass(frozen=True)
class AnswerArrives:
    """Eine Antwort trifft ein: Emotion, Arousal und die Dauer ihrer Wiedergabe in ms.

    Der Leerlauf braucht keinen Text; das Ende der Wiedergabe folgt aus der Dauer.
    """

    event_type: ClassVar[str] = "antwort"
    at_ms: float
    emotion: str
    arousal: float
    playback_ms: float


@dataclass(frozen=True)
class ImpulseThinks:
    """Ein Impuls geht in den CharacterGraph (`beginn`) oder ist dort fertig (`ende`)."""

    event_type: ClassVar[str] = "impuls_denkt"
    at_ms: float
    phase: str


@dataclass(frozen=True)
class PixieJob:
    """Pixie beginnt oder beendet einen Auftrag in einer Spur.

    `emotion` und `arousal` sind None, wenn der Auftrag keine trägt.
    """

    event_type: ClassVar[str] = "pixie_auftrag"
    at_ms: float
    phase: str
    track: str
    job_kind: str
    emotion: str | None = None
    arousal: float | None = None


IdleEvent = TurnBegins | TurnFailed | AnswerArrives | ImpulseThinks | PixieJob
_EVENT_TYPES = (TurnBegins, TurnFailed, AnswerArrives, ImpulseThinks, PixieJob)


# ---------------------------------------------------------------- Ausgabe ------


@dataclass(frozen=True)
class IdleFrame:
    """Was der Leerlauf je Schritt liefert.

    `targets` sind die Ziele aller Kanäle, `lid_open` die Öffnung des Lids (1 offen),
    `face_omega` ω der Feder des Gesichts, `amplitude` die Amplitude k der Formen,
    `activity` die Aktivität a. `answer_at_ms` ist im Zustand Antwort die Zeit
    (`at_ms`) der Antwort, die gesprochen wird, sonst None — daran erkennt der
    Aufrufer, welche Antwort beginnt. `head_yaw` ist das Ziel der Kopfdrehung in Grad
    (plus = nach rechts aus Sicht des Betrachters, wie gx), in ±`YAW_MAX`; die Feder
    des Kopfs führt der Aufrufer. Ist die Drehung abgeschaltet, ist es 0.
    """

    state: IdleState
    form_id: str
    targets: FaceState
    lid_open: float
    face_omega: float
    amplitude: float
    activity: float
    answer_at_ms: float | None
    head_yaw: float


@dataclass
class TracedState:
    """Ein Zustandswechsel: Schritt, Zustand, Grund und, wo es eine gibt, die Grenze."""

    at_ms: float
    state: IdleState
    reason: str
    until_ms: float | None


@dataclass
class TracedForm:
    """Eine Form, wie sie beginnt: Schritt, Zustand, Kennung, Plan, Blickpunkt.

    Dazu die größte Mundöffnung, die ihre Ziele während der Form setzen.
    """

    at_ms: float
    state: IdleState
    form_id: str
    t0: float
    duration: float
    gaze_x: float
    gaze_y: float
    mouth_open_max: float = 0.0


@dataclass
class TracedBlink:
    """Ein Lidschlag: Schritt, Zustand, Art, gekoppelt (nicht Poisson), Beginn und Form.

    `begin_ms` ist der Beginn des Schließens — vor `at_ms`, wenn er an einen
    laufenden ansetzt; `hold_ms` die geschlossene Phase.
    """

    at_ms: float
    state: IdleState
    kind: str
    coupled: bool
    begin_ms: float
    close_ms: float
    hold_ms: float
    open_ms: float


@dataclass
class TracedHead:
    """Ein Kopfziel, das gültig wird: Schritt, Ziel ohne Wandern, Art, Blick, Blickwechsel."""

    at_ms: float
    target: float
    kind: str
    gaze_x: float
    gaze_change_ms: float


@dataclass
class TracedEvent:
    """Ein behandeltes Ereignis: seine Zeit, sein Typ, der Schritt der Behandlung."""

    at_ms: float
    event_type: str
    handled_ms: float


@dataclass
class IdleTrace:
    """Der Verlauf eines Leerlaufs — für Zeugen und Prüfungen, nicht für den Betrieb."""

    states: list[TracedState] = field(default_factory=list)
    forms: list[TracedForm] = field(default_factory=list)
    blinks: list[TracedBlink] = field(default_factory=list)
    events: list[TracedEvent] = field(default_factory=list)
    heads: list[TracedHead] = field(default_factory=list)


# ---------------------------------------------------------------- Innen --------


@dataclass
class _Gaze:
    """Blickpunkt einer Form; `x2` ist der zweite Punkt des Pendels (F7)."""

    x: float
    y: float
    x2: float | None = None


@dataclass
class _FormInstance:
    """Eine geplante Form: Beginn, Dauer, Seite, Blick, Sakkade, Pendel, Kopf.

    `head_h` ist die Ziehung des Kopfs (eigene Quelle); `head_inherits`: die Form setzt
    den Blick der vorigen fort und behält auch deren Kopfziel (E1, A0).
    """

    form_id: str
    t0: float
    duration: float
    side: int
    gaze: _Gaze
    saccade: tuple[float, float] = (0.0, 0.0)
    pendulum: int = 0
    next_saccade: float = math.inf
    previous_gaze: _Gaze | None = None
    head_h: float = 0.0
    head_inherits: bool = False


@dataclass
class _Plan:
    """Ein Plan: Zyklus, Antwort oder nur das Einatmen; `drawn` die gezogenen Formen.

    `span` ist die Spanne, mit der ein Zyklus geplant wurde; Antwort und Einatmen haben keine.
    """

    kind: str
    forms: list[_FormInstance]
    drawn: frozenset[str]
    span: "_Span | None" = None


@dataclass(frozen=True)
class _Answer:
    """Eine Antwort, die wartet oder gesprochen wird; `at_ms` die Zeit ihres Eintreffens."""

    sector: int
    arousal: float
    playback_ms: float
    at_ms: float


@dataclass
class _Emotion:
    """Sektor und Arousal einer Seite — Nova oder Pixies Rückfall."""

    sector: int
    arousal: float


@dataclass(frozen=True)
class _Job:
    """Ein laufender Auftrag Pixies; `sector` None, wenn er keine Emotion trägt."""

    number: int
    job_kind: str
    sector: int | None
    arousal: float


@dataclass
class _Situation:
    """Der Zustand und was an ihm hängt: Herkunft, Einatmen, Antwort, Nachklang.

    `blink_since`: ab hier zählen die gekoppelten Lidschläge — im Nachklang ab dem
    Beginn der Antwort. `glide_basis`, `glide_noise`: Basis und Rauschen vor dem ersten
    Laut, aus denen die Antwort über `glide_ms` (die Dauer von A0) gleitet.
    """

    state: IdleState = IdleState.NOISE
    since: float = 0.0
    blink_since: float = 0.0
    glide_basis: Mapping[str, float] | None = None
    glide_noise: Mapping[str, float] | None = None
    glide_ms: float = math.inf
    origin: str | None = None
    inhaling: bool = False
    answer_from: float = math.inf
    waiting: _Answer | None = None
    playback_end: float = math.inf
    playback_reported: bool = True
    answer_end: float = math.inf
    afterglow_end: float = math.inf
    afterglow_duration: float = 1.0


@dataclass
class _Lid:
    """Der Prozess der Lidschläge: laufender Lidschlag, Sperrzeit, Serie, Protokoll.

    `series` trägt je fälligem Lidschlag Zeit und Art.
    """

    start: float = -1.0
    close: float = 90.0
    hold: float = 0.0
    open: float = 200.0
    next_ms: float = 0.0
    blocked_until: float = 0.0
    series: list[tuple[float, str]] = field(default_factory=list)
    log: list[tuple[float, bool]] = field(default_factory=list)
    scale: float = 1.0
    rate: float = 15.0
    poisson: float = 15.0


@dataclass(frozen=True)
class _Inputs:
    """Was im Augenblick als Eingang anliegt: Emotion, Basis, Lage im Raum, Aktivität.

    `noise` ist die Stärke des Rauschens je Kanal von `NOISE_AMPLITUDES`.
    """

    state: IdleState
    sector: int
    arousal: float
    basis: Mapping[str, float]
    noise: Mapping[str, float]
    energy: float
    valence: float
    sector_valence: float
    activity: float
    amplitude: float
    anger: bool
    avoiding: bool
    paradox: bool


@dataclass(frozen=True)
class _Span:
    """Die Spanne der Formdauer in s und die Zahl der Formen je Zyklus."""

    xc: float
    lo: float
    hi: float
    count: int


@dataclass(frozen=True)
class _Deviation:
    """Die Abweichung einer Form im Augenblick u ihrer Dauer."""

    dev: Mapping[str, float]
    gaze: tuple[float, float]
    smooth_brow: bool
    opens: bool
    pupil: float


@dataclass
class _EventQueue:
    """Die wartenden Ereignisse, stabil nach ihrer Zeit geordnet."""

    _events: list[IdleEvent] = field(default_factory=list)

    def push(self, event: IdleEvent) -> None:
        """Reiht ein; gleiche Zeiten bleiben in der Reihenfolge des Eintreffens.

        Vorbedingung: ein Ereignis des Leerlaufs mit endlicher Zeit.
        Nachbedingung: das Ereignis steht nach seiner Zeit hinter allen gleichzeitigen.
        Fehlerfälle: ein fremder Typ, eine nicht endliche Zeit.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(event, _EVENT_TYPES) or not math.isfinite(event.at_ms):
            raise ValueError(f"_EventQueue.push: kein Ereignis mit endlicher Zeit: {event!r}")

        # ── Verarbeitung ──
        position = bisect_right([e.at_ms for e in self._events], event.at_ms)
        self._events.insert(position, event)

        # ── Ausgabe-Verifikation ──
        if self._events[position] is not event:
            raise RuntimeError("_EventQueue.push: Ereignis nicht an seiner Stelle")

    def pop_due(self, now: float) -> list[IdleEvent]:
        """Nimmt jedes Ereignis heraus, dessen Zeit nicht nach `now` liegt, in Reihenfolge.

        Vorbedingung: now endlich.
        Nachbedingung: kein fälliges Ereignis wartet mehr.
        Fehlerfälle: nicht endliche Zeit.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(now):
            raise ValueError(f"_EventQueue.pop_due: Zeit {now} nicht endlich")

        # ── Verarbeitung ──
        count = bisect_right([e.at_ms for e in self._events], now)
        due = self._events[:count]
        del self._events[:count]

        # ── Ausgabe-Verifikation ──
        if self._events and self._events[0].at_ms <= now:
            raise RuntimeError("_EventQueue.pop_due: ein fälliges Ereignis wartet noch")
        return due


def _nominal_of(spec: FormSpec) -> tuple[float, float, float, float, float]:
    """Die Merkmale einer Form für den Kontrast: Brauen innen, außen, Mund, Blick x, y.

    Vorbedingung: eine Form des Katalogs.
    Nachbedingung: fünf endliche Werte; x als Betrag.
    Fehlerfälle: ein nicht endlicher Wert.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(spec, FormSpec):
        raise TypeError(f"_nominal_of: keine Form: {type(spec).__name__}")

    # ── Verarbeitung ──
    g = spec.deviation
    inner = (g.get("bli", 0) + g.get("bri", 0)) / 2
    outer = (g.get("blo", 0) + g.get("bro", 0)) / 2
    values = (inner, outer, g.get("mc", 0), abs(spec.nominal.x), spec.nominal.y)

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for v in values):
        raise RuntimeError(f"_nominal_of: {spec.form_id} mit nicht endlichem Merkmal")
    return values


_NOMINALS: Mapping[str, tuple[float, float, float, float, float]] = MappingProxyType(
    {form_id: _nominal_of(spec) for form_id, spec in FORMS.items()}
)


def _contrast(a: str, b: str, k: float, gaze_a: _Gaze | None, gaze_b: _Gaze | None) -> bool:
    """R6: Kontrast zwischen Nachbarn — Brauen oder Mund um 3 px, oder Blick um 0,25.

    Mit beiden Blickpunkten zählt deren Abstand, sonst der der Nennwerte.
    Vorbedingung: a und b sind Formen des Katalogs.
    Nachbedingung: True, wenn eine Hauptgruppe sich genug unterscheidet.
    Fehlerfälle: eine unbekannte Form.
    """
    # ── Eingabe-Validierung ──
    if a not in _NOMINALS or b not in _NOMINALS:
        raise ValueError(f"_contrast: unbekannte Form ({a}, {b})")

    # ── Verarbeitung ──
    na, nb = _NOMINALS[a], _NOMINALS[b]
    if gaze_a is not None and gaze_b is not None:
        gaze = _hypot(gaze_a.x - gaze_b.x, gaze_a.y - gaze_b.y)
    else:
        gaze = _hypot(na[3] - nb[3], na[4] - nb[4])
    differs = any(abs(na[i] - nb[i]) * k >= 3 for i in range(3)) or gaze >= 0.25

    # ── Ausgabe-Verifikation ──
    if not math.isfinite(gaze):
        raise RuntimeError(f"_contrast: Blickabstand {gaze} nicht endlich")
    return differs


def _contrast_points(sequence: Sequence[str], k: float) -> int:
    """Wie viele Nachbarn einer Folge im Kontrast stehen.

    Vorbedingung: eine Folge von Formen des Katalogs.
    Nachbedingung: eine Zahl in 0..len−1.
    Fehlerfälle: eine unbekannte Form (über `_contrast`).
    """
    # ── Eingabe-Validierung ──
    if not isinstance(sequence, Sequence):
        raise TypeError(f"_contrast_points: keine Folge: {type(sequence).__name__}")

    # ── Verarbeitung ──
    points = 0
    for i in range(1, len(sequence)):
        if _contrast(sequence[i - 1], sequence[i], k, None, None):
            points += 1

    # ── Ausgabe-Verifikation ──
    if not 0 <= points <= max(0, len(sequence) - 1):
        raise RuntimeError(f"_contrast_points: {points} Punkte bei {len(sequence)} Formen")
    return points


def _permutations(items: Sequence[str]) -> list[list[str]]:
    """Alle Reihenfolgen, rekursiv, das erste Element vorn — die Ordnung des Generators.

    Vorbedingung: höchstens sechs Elemente (ein Zyklus hat 4–5 Formen).
    Nachbedingung: len! Reihenfolgen; für die leere Folge eine leere.
    Fehlerfälle: mehr als sechs Elemente.
    """
    # ── Eingabe-Validierung ──
    if len(items) > 6:
        raise ValueError(f"_permutations: {len(items)} Elemente — zu viele")

    # ── Verarbeitung ──
    if len(items) <= 1:
        return [list(items)]
    result: list[list[str]] = []
    for i, first in enumerate(items):
        rest = list(items[:i]) + list(items[i + 1:])
        result.extend([first, *tail] for tail in _permutations(rest))

    # ── Ausgabe-Verifikation ──
    if len(result) != math.factorial(len(items)):
        raise RuntimeError(f"_permutations: {len(result)} statt {math.factorial(len(items))}")
    return result


def _openers(inputs: _Inputs) -> frozenset[str]:
    """R1: die Formen, die einen Zyklus mit Blickwechsel eröffnen; bei Ärger auch F17.

    Vorbedingung: eine Lage.
    Nachbedingung: eine nicht leere Menge.
    Fehlerfälle: keine Lage.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(inputs, _Inputs):
        raise TypeError(f"_openers: keine Lage: {type(inputs).__name__}")

    # ── Verarbeitung ──
    openers = catalog.OPENERS_ANGER if inputs.anger else catalog.OPENERS

    # ── Ausgabe-Verifikation ──
    if not openers:
        raise RuntimeError("_openers: leere Menge")
    return openers


def _span(inputs: _Inputs) -> _Span:
    """Die Spanne x der Formdauer: `x_c = max(0,5; (6 − 4·E + Δ_S + (T − 0,3)) · Faktor)`.

    Vorbedingung: ein Zustand mit Faktor der Spanne.
    Nachbedingung: 1,5 ≤ lo ≤ hi; 5 Formen bei x_c unter 3,5, sonst 4.
    Fehlerfälle: ein Zustand ohne Faktor.
    """
    # ── Eingabe-Validierung ──
    if inputs.state not in catalog.SPAN_FACTOR:
        raise ValueError(f"_span: Zustand {inputs.state!r} ohne Faktor")

    # ── Verarbeitung ──
    raw = (6 - 4 * inputs.energy + catalog.DELTA_S[inputs.sector]
           + (catalog.SPACE_DEPTH - 0.3))
    xc = max(0.5, raw * catalog.SPAN_FACTOR[inputs.state])
    lo = max(catalog.SPAN_MIN_S, 0.65 * xc)
    hi = max(lo, min(catalog.SPAN_MAX_S, 1.35 * xc))
    span = _Span(xc, lo, hi, 5 if xc < 3.5 else 4)

    # ── Ausgabe-Verifikation ──
    if not catalog.SPAN_MIN_S <= span.lo <= span.hi:
        raise RuntimeError(f"_span: Spanne {span} verkehrt")
    return span


def _afterglow_mix(situation: _Situation, now: float) -> tuple[float, float]:
    """Der Fortschritt p des Nachklangs und der Anteil Pixies an seiner Emotion.

    Vorbedingung: `now` endlich; die Dauer des Nachklangs in `situation` ist gesetzt.
    Nachbedingung: p und mix in 0..1; mix ist 0, solange p vor der Überblendung liegt.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(now) or situation.afterglow_duration <= 0:
        raise ValueError(f"_afterglow_mix: Zeit {now} oder Dauer {situation.afterglow_duration}")

    # ── Verarbeitung ──
    p = _clamp((now - situation.since) / situation.afterglow_duration, 0.0, 1.0)
    blend = catalog.AFTERGLOW_BLEND_FROM
    mix = _smoothstep((p - blend) / (1 - blend))

    # ── Ausgabe-Verifikation ──
    if not (0.0 <= p <= 1.0 and 0.0 <= mix <= 1.0):
        raise RuntimeError(f"_afterglow_mix: p {p} oder mix {mix} außerhalb 0..1")
    return p, mix


def _noise_strength(situation: _Situation, activity: float, glide: float) -> dict[str, float]:
    """Die Stärke des Rauschens je Kanal: die Aktivität; in der Antwort nur Brauen und Mundwinkel.

    In der Antwort gleitet sie wie die Basis aus dem Rauschen vor dem ersten Laut.
    Vorbedingung: activity und glide in 0..1.
    Nachbedingung: ein Wert in 0..1 je Kanal von `NOISE_AMPLITUDES`.
    Fehlerfälle: activity oder glide außerhalb 0..1.
    """
    # ── Eingabe-Validierung ──
    if not (0.0 <= activity <= 1.0 and 0.0 <= glide <= 1.0):
        raise ValueError(f"_noise_strength: Aktivität {activity} oder Gleiten {glide}")

    # ── Verarbeitung ──
    answering = situation.state is IdleState.ANSWER
    start = situation.glide_noise if answering else None
    strength = {}
    for key, _amplitude in catalog.NOISE_AMPLITUDES:
        goal = activity if not answering or key in catalog.NOISE_IN_ANSWER else 0.0
        strength[key] = goal if start is None else start[key] + (goal - start[key]) * glide

    # ── Ausgabe-Verifikation ──
    if not all(0.0 <= v <= 1.0 for v in strength.values()):
        raise RuntimeError(f"_noise_strength: {strength} außerhalb 0..1")
    return strength


def _status_note(situation: _Situation, now: float) -> _Note:
    """Die Angabe zum Zustand: Art, Sekunden und beim Nachklang seine Dauer.

    Vorbedingung: `now` endlich, nicht vor dem Beginn des Zustands.
    Nachbedingung: keine Angabe im Rauschen, sonst eine Art aus `NOTES`; Sekunden ≥ 0.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(now):
        raise ValueError(f"_status_note: Zeit {now} nicht endlich")

    # ── Verarbeitung ──
    state = situation.state
    note: _Note = (None, None, None)
    if state is IdleState.THINKING:
        note = ((NOTE_INHALING, max(0.0, situation.answer_from - now) / 1000, None)
                if situation.inhaling else (NOTE_WAITING, None, None))
    elif state is IdleState.ANSWER:
        note = (NOTE_PLAYBACK, max(0.0, situation.answer_end - now) / 1000, None)
    elif state is IdleState.AFTERGLOW:
        note = (NOTE_AFTERGLOW, max(0.0, situation.afterglow_end - now) / 1000,
                situation.afterglow_duration / 1000)

    # ── Ausgabe-Verifikation ──
    if (note[0] is None) is not (state is IdleState.NOISE):
        raise RuntimeError(f"_status_note: Angabe {note[0]!r} im Zustand {state.value}")
    return note


def _status_source(situation: _Situation, now: float) -> str:
    """Wessen Emotion gilt: im Rauschen Pixies, im Nachklang ab der halben Überblendung.

    Vorbedingung: `now` endlich.
    Nachbedingung: `Nova` oder `Pixie`, dieselbe Seite wie in `_inputs`.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(situation, _Situation):
        raise TypeError(f"_status_source: keine Lage: {type(situation).__name__}")

    # ── Verarbeitung ──
    source = SOURCE_NOVA
    if situation.state is IdleState.NOISE:
        source = SOURCE_PIXIE
    elif situation.state is IdleState.AFTERGLOW and _afterglow_mix(situation, now)[1] >= 0.5:
        source = SOURCE_PIXIE

    # ── Ausgabe-Verifikation ──
    if source not in (SOURCE_NOVA, SOURCE_PIXIE):
        raise RuntimeError(f"_status_source: Quelle {source!r}")
    return source


def _status_form(inst: _FormInstance, now: float) -> StatusForm:
    """Die laufende Form als Wert.

    Vorbedingung: `inst` eine Form des Katalogs, `now` endlich.
    Nachbedingung: die Dauer der Form und wie lange sie steht, in Sekunden.
    """
    # ── Eingabe-Validierung ──
    if inst.form_id not in FORMS or not math.isfinite(now):
        raise ValueError(f"_status_form: Form {inst.form_id!r} oder Zeit {now} ungültig")

    # ── Verarbeitung ──
    return StatusForm(inst.form_id, FORMS[inst.form_id].name, (now - inst.t0) / 1000,
                      inst.duration / 1000, inst.gaze.x, inst.gaze.y)


def _status_next(plan: _Plan, index: int, now: float) -> StatusNext | None:
    """Die Form nach der laufenden mit der Zeit bis zu ihrem Beginn; None an der letzten.

    Vorbedingung: `index` liegt im Plan.
    Nachbedingung: die Form mit Stelle `index + 1` und die Sekunden bis zu ihrem Beginn.
    """
    # ── Eingabe-Validierung ──
    if not 0 <= index < len(plan.forms):
        raise ValueError(f"_status_next: Stelle {index} außerhalb des Plans")

    # ── Verarbeitung ──
    if index + 1 >= len(plan.forms):
        return None
    following = plan.forms[index + 1]
    return StatusNext(following.form_id, FORMS[following.form_id].name,
                      (following.t0 - now) / 1000)


def _build_status(now: float, situation: _Situation, plan: _Plan, index: int,
                  inputs: _Inputs) -> IdleStatus:
    """Setzt die Phase aus Zustand, Plan und Lage zusammen; liest nur.

    Vorbedingung: `plan` ist der laufende Plan, `index` seine laufende Stelle, `inputs` die
    Lage zu `now`.
    Nachbedingung: ein Wert, dessen Band die Formen des Plans in ihrer Reihenfolge trägt.
    """
    # ── Eingabe-Validierung ──
    if not 0 <= index < len(plan.forms):
        raise ValueError(f"_build_status: Stelle {index} außerhalb des Plans")

    # ── Verarbeitung ──
    note, note_s, note_total_s = _status_note(situation, now)
    span = plan.span
    return IdleStatus(
        state=situation.state, since_ms=situation.since,
        elapsed_s=(now - situation.since) / 1000, note=note, note_s=note_s,
        note_total_s=note_total_s, source=_status_source(situation, now),
        sector_name=SECTORS[inputs.sector].name, arousal=inputs.arousal,
        form=_status_form(plan.forms[index], now), next_form=_status_next(plan, index, now),
        band=tuple(BandItem(f.form_id, f.duration / 1000) for f in plan.forms), position=index,
        plan_kind=plan.kind,
        span=None if span is None else StatusSpan(span.xc, span.lo, span.hi, span.count))


def _modifiers(inputs: _Inputs) -> tuple[tuple[frozenset[str], float], ...]:
    """Die Modifikatoren der Gewichte, in der Reihenfolge ihrer Anwendung.

    Ein Faktor 1 lässt ein Gewicht bitgleich; so stehen auch die bedingten
    Faktoren (Richtung, Paradox, Valenz des Raums) in der festen Reihe.
    Vorbedingung: eine Lage.
    Nachbedingung: endliche, positive Faktoren.
    Fehlerfälle: ein Faktor ≤ 0.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(inputs, _Inputs):
        raise TypeError(f"_modifiers: keine Lage: {type(inputs).__name__}")

    # ── Verarbeitung ──
    depth, near, act = catalog.SPACE_DEPTH, catalog.SPACE_NEARNESS, inputs.activity
    shift = inputs.valence - inputs.sector_valence
    direction = {catalog.DIRECTION_UP: 1.5, catalog.DIRECTION_DOWN: 0.3}.get(
        catalog.SPACE_DIRECTION, 1.0)
    factors = (
        (catalog.MOD_DEEP, 0.5 + depth), (catalog.MOD_LIGHT, 1.5 - depth),
        (catalog.MOD_LIVELY, 0.5 + inputs.energy), (catalog.MOD_CALM, 1.5 - inputs.energy),
        (catalog.MOD_LOAD, 0.3 + 1.4 * act), (catalog.MOD_DRIFT, 1.6 - 1.2 * act),
        (catalog.MOD_PRIVATE, 0.4 + near), (catalog.MOD_CONTROLLED, 1.3 - 0.6 * near),
        (frozenset({"F9"}), direction),
        (frozenset({"F15"}), 3.0 if inputs.paradox else 1.0),
        (frozenset({"F7"}), 1.5 if inputs.paradox else 1.0),
        (catalog.POSITIVE, _clamp(1 + shift, 0.2, 2)),
        (catalog.NEGATIVE, _clamp(1 - shift, 0.2, 2)),
    )

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(f) and f > 0 for _, f in factors):
        raise RuntimeError(f"_modifiers: Faktor ≤ 0 oder nicht endlich: {factors}")
    return factors


def _apply_job_weighting(weights: dict[str, float], inputs: _Inputs, weighting: str | None) -> None:
    """Die Art des Auftrags im Rauschen: Recherche hebt F2, F3, Reflexion F12 oder F10, Lücke F6.

    Vorbedingung: Gewichte des Rauschens.
    Nachbedingung: die betroffenen Gewichte × 1,5, sofern sie da und nicht 0 sind.
    Fehlerfälle: eine unbekannte Gewichtung.
    """
    # ── Eingabe-Validierung ──
    known = {None, catalog.WEIGHTING_RESEARCH, catalog.WEIGHTING_REFLECTION,
             catalog.WEIGHTING_KNOWLEDGE_GAP}
    if weighting not in known:
        raise ValueError(f"_apply_job_weighting: Gewichtung {weighting!r} unbekannt")

    # ── Verarbeitung ──
    boosted: tuple[str, ...] = ()
    if weighting == catalog.WEIGHTING_RESEARCH:
        boosted = ("F2", "F3")
    elif weighting == catalog.WEIGHTING_REFLECTION:
        boosted = ("F12",) if inputs.valence >= 0 else ("F10",)
    elif weighting == catalog.WEIGHTING_KNOWLEDGE_GAP:
        boosted = ("F6",)
    for form_id in boosted:
        if weights.get(form_id):
            weights[form_id] *= catalog.JOB_WEIGHT_BOOST

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for v in weights.values()):
        raise RuntimeError("_apply_job_weighting: Gewicht nicht endlich")


def _apply_daydream(weights: dict[str, float], inputs: _Inputs) -> None:
    """Abschweifen ohne Färbung (neutral, kaum Aktivität): die Tagtraum-Verteilung.

    Verteilt die Summe der drei Familien 42,5 / 26,5 / 31 %; eine Familie ohne
    Gewicht teilt ihren Anteil gleich. Sonst bleiben die Gewichte unverändert.
    Vorbedingung: Gewichte des Rauschens.
    Nachbedingung: die Summe der Familien ist erhalten (bis auf Rundung).
    Fehlerfälle: ein nicht endliches Gewicht.
    """
    # ── Eingabe-Validierung ──
    if inputs.sector != 0 or inputs.activity >= catalog.DAYDREAM_ACTIVITY:
        return

    # ── Verarbeitung ──
    total = 0.0
    for ids, _share in catalog.DAYDREAM_GROUPS:
        group_sum = 0.0
        for form_id in ids:
            group_sum += weights.get(form_id, 0)
        total += group_sum
    for ids, share in catalog.DAYDREAM_GROUPS:
        group_sum = 0.0
        for form_id in ids:
            group_sum += weights.get(form_id, 0)
        for form_id in ids:
            if group_sum > 0:
                weights[form_id] = weights.get(form_id, 0) / group_sum * share * total
            else:
                weights[form_id] = share * total / len(ids)

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for v in weights.values()):
        raise RuntimeError("_apply_daydream: Gewicht nicht endlich")


def _weights(inputs: _Inputs, previous: frozenset[str], weighting: str | None) -> dict[str, float]:
    """Die Gewichte eines Zyklus: Grundgewicht × Gruppe × Modifikatoren, Wiederholung gedämpft.

    Die Reihenfolge der Formen ist die von `DRAWABLE`; sie bestimmt die Ziehung.
    Vorbedingung: ein Zustand mit Gruppe (Rauschen, Nachdenken, Nachklang).
    Nachbedingung: Gewichte ≥ 0 (eine Form der Tagtraum-Verteilung kann 0 tragen).
    Fehlerfälle: ein Zustand ohne Gruppe.
    """
    # ── Eingabe-Validierung ──
    group = catalog.GROUP_FACTORS.get(inputs.state)
    if group is None:
        raise ValueError(f"_weights: keine Gruppe für {inputs.state!r}")

    # ── Verarbeitung ──
    modifiers = _modifiers(inputs)
    weights: dict[str, float] = {}
    for form_id in catalog.DRAWABLE:
        weight = catalog.BASE_WEIGHTS[form_id][inputs.sector] * group.get(form_id, 0)
        if weight <= 0:
            continue
        for members, factor in modifiers:
            if form_id in members:
                weight *= factor
        weights[form_id] = weight
    if inputs.state is IdleState.NOISE:
        _apply_job_weighting(weights, inputs, weighting)
        _apply_daydream(weights, inputs)
    for form_id in weights:
        if form_id in previous:
            weights[form_id] *= catalog.REPEAT_DAMPING

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) and v >= 0 for v in weights.values()):
        raise RuntimeError(f"_weights: Gewicht negativ oder nicht endlich: {weights}")
    return weights


def _draw(
    rng: Mulberry32, pool: Mapping[str, float], count: int,
    only: frozenset[str] | None, without: Sequence[str] | None,
) -> list[str]:
    """Zieht bis zu `count` Formen ohne Zurücklegen nach Gewicht.

    Je Ziehung eine Zahl; die Summe läuft in der Reihenfolge des Pools, wie im
    Generator (keine kompensierte Summe — sie rundete anders).
    Vorbedingung: count ≥ 0; `only` begrenzt, `without` schließt aus.
    Nachbedingung: verschiedene Formen mit Gewicht > 0, höchstens `count`.
    Fehlerfälle: count < 0.
    """
    # ── Eingabe-Validierung ──
    if count < 0:
        raise ValueError(f"_draw: Anzahl {count} < 0")

    # ── Verarbeitung ──
    excluded = set(without or ())
    left = {form_id: w for form_id, w in pool.items()
            if w > 0 and (only is None or form_id in only) and form_id not in excluded}
    drawn: list[str] = []
    while len(drawn) < count and left:
        ids = list(left)
        total = 0.0
        for form_id in ids:
            total += left[form_id]
        r = rng.next() * total
        pick = ids[-1]
        for form_id in ids:
            r -= left[form_id]
            if r <= 0:
                pick = form_id
                break
        drawn.append(pick)
        del left[pick]

    # ── Ausgabe-Verifikation ──
    if len(set(drawn)) != len(drawn) or len(drawn) > count:
        raise RuntimeError(f"_draw: Ziehung {drawn} verletzt ohne Zurücklegen")
    return drawn


def _weakest(
    chosen: Sequence[str], weights: Mapping[str, float], openers: frozenset[str],
    protected: Sequence[str],
) -> str | None:
    """Die schwächste gewählte Form, die keine Regel trägt.

    Ausgenommen sind F9, sein einziger Vorläufer, der einzige Eröffner und alles aus `protected`.

    Vorbedingung: jede gewählte Form hat ein Gewicht.
    Nachbedingung: eine gewählte Form oder None.
    Fehlerfälle: eine gewählte Form ohne Gewicht.
    """
    # ── Eingabe-Validierung ──
    if any(form_id not in weights for form_id in chosen):
        raise ValueError(f"_weakest: Form ohne Gewicht in {list(chosen)}")

    # ── Verarbeitung ──
    guard = list(protected)
    precursors = [f for f in chosen if f in catalog.PRECURSORS]
    present_openers = [f for f in chosen if f in openers]
    if "F9" in chosen:
        guard.append("F9")
        if len(precursors) == 1:
            guard.append(precursors[0])
    if len(present_openers) == 1:
        guard.append(present_openers[0])
    candidates = sorted((f for f in chosen if f not in guard), key=lambda f: weights[f])
    weakest = candidates[0] if candidates else None

    # ── Ausgabe-Verifikation ──
    if weakest is not None and weakest not in chosen:
        raise RuntimeError(f"_weakest: {weakest} nicht gewählt")
    return weakest


def _replace(chosen: list[str], old: str | None, new: str | None) -> bool:
    """Ersetzt `old` durch `new`, wenn es beide gibt; sagt, ob ersetzt wurde.

    Vorbedingung: `old` ist gewählt, wenn es nicht None ist.
    Nachbedingung: bei True steht `new` an der Stelle von `old`.
    Fehlerfälle: `old` nicht gewählt.
    """
    # ── Eingabe-Validierung ──
    if old is not None and old not in chosen:
        raise ValueError(f"_replace: {old} nicht gewählt")

    # ── Verarbeitung ──
    if old is None or new is None:
        return False
    chosen[chosen.index(old)] = new

    # ── Ausgabe-Verifikation ──
    if new not in chosen:
        raise RuntimeError(f"_replace: {new} fehlt nach dem Ersetzen")
    return True


def _mirror(dev: Mapping[str, float]) -> dict[str, float]:
    """Spiegelt die Abweichung einer asymmetrischen Form auf die andere Seite des Gesichts.

    Vorbedingung: eine Abweichung je Kurzname.
    Nachbedingung: linke und rechte Kanäle getauscht, Mundversatz `ma` umgekehrt.
    Fehlerfälle: ein Kanal ginge beim Tauschen verloren.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(dev, Mapping):
        raise TypeError(f"_mirror: keine Abweichung: {type(dev).__name__}")

    # ── Verarbeitung ──
    mirrored: dict[str, float] = {}
    for key, value in dev.items():
        if key in catalog.BROW_MIRROR:
            other = catalog.BROW_MIRROR[key]
        elif _AU_SIDE.fullmatch(key):
            other = key[:-1] + ("R" if key.endswith("L") else "L")
        else:
            other = key
        mirrored[other] = -value if key == "ma" else value

    # ── Ausgabe-Verifikation ──
    if len(mirrored) != len(dev):
        raise RuntimeError(f"_mirror: {len(dev)} Kanäle, gespiegelt {len(mirrored)}")
    return mirrored


def _deviation(inst: _FormInstance, u: float) -> _Deviation:
    """Die Abweichung einer Form im Augenblick u (ms seit ihrem Beginn).

    F7 pendelt zwischen zwei Punkten; F9 sieht erst weg und blinzelt, hebt dann kurz
    die Brauen und glättet die Stirn mit dem Blick zurück; F16 hebt am Anfang die
    Brauen kaum merklich; F11 formuliert lautlos im Silbentakt.
    Vorbedingung: eine geplante Form.
    Nachbedingung: Abweichung, Blickpunkt, Stirn glatt, Mund offen, Pupille.
    Fehlerfälle: F9 ohne den Blick der vorigen Form.
    """
    # ── Eingabe-Validierung ──
    if inst.form_id == "F9" and inst.previous_gaze is None:
        raise ValueError("_deviation: F9 ohne den Blick der vorigen Form")

    # ── Verarbeitung ──
    spec = FORMS[inst.form_id]
    dev: Mapping[str, float] = (_mirror(spec.deviation) if spec.asymmetric and inst.side < 0
                                else spec.deviation)
    smooth_brow, opens = False, spec.opens
    gaze = (inst.gaze.x + inst.saccade[0], inst.gaze.y + inst.saccade[1])
    if inst.form_id == "F7" and inst.gaze.x2 is not None:
        gaze = (inst.gaze.x2 if inst.pendulum else inst.gaze.x, inst.gaze.y)
    if inst.form_id == "F9":
        dev, gaze, smooth_brow, opens = _insight_phase(inst, u, dev, opens)
    if inst.form_id == "F16" and u < 600:
        dev = {**dev, "bli": -3, "bri": -3, "blo": -3, "bro": -3}
    if inst.form_id == "F11":
        s = u / 1000
        dev = {**dev, "mo": 1 - math.cos(2 * math.pi * (4 * s + 0.25 * math.sin(
            2 * math.pi * 0.6 * s)))}
    result = _Deviation(dev, gaze, smooth_brow, opens, spec.pupil)

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for v in (*result.dev.values(), *result.gaze)):
        raise RuntimeError(f"_deviation: {inst.form_id} mit nicht endlichem Wert")
    return result


def _insight_phase(
    inst: _FormInstance, u: float, dev: Mapping[str, float], opens: bool,
) -> tuple[Mapping[str, float], tuple[float, float], bool, bool]:
    """Die drei Phasen des Einfalls (F9): weg und blinzeln, Brauen hoch, Stirn glatt.

    Vorbedingung: F9 mit dem Blick der vorigen Form.
    Nachbedingung: Abweichung, Blick, Stirn glatt, Mund offen der Phase bei u.
    Fehlerfälle: eine andere Form oder kein voriger Blick.
    """
    # ── Eingabe-Validierung ──
    if inst.form_id != "F9" or inst.previous_gaze is None:
        raise ValueError(f"_insight_phase: {inst.form_id} ohne vorigen Blick")

    # ── Verarbeitung ──
    away = (_insight_away_x(inst), 0.15)
    if u < 500:
        phase: tuple[Mapping[str, float], tuple[float, float], bool, bool] = ({}, away, False,
                                                                             False)
    elif u < 1000:
        raised = {"bli": -10, "bri": -10, "blo": -10, "bro": -10, "eo": 0.1}
        phase = (raised, away, False, False)
    else:
        phase = (dev, (0.0, 0.0), True, opens)

    # ── Ausgabe-Verifikation ──
    if len(phase) != 4:
        raise RuntimeError("_insight_phase: unvollständige Phase")
    return phase


def _insight_away_x(inst: _FormInstance) -> float:
    """F9, Phase a und b: die Seite des Wegsehens — die der vorigen Form, mindestens 0,2.

    Liegt der vorige Blick näher an der Mitte, sieht F9 0,2 zu dessen Seite; ohne Seite
    (x = 0) zur Seite der Form. Sonst sähe das „Weg“ nach einer Form nah der Mitte den
    Betrachter an.
    Vorbedingung: F9 mit dem Blick der vorigen Form.
    Nachbedingung: |x| ≥ 0,2.
    Fehlerfälle: eine andere Form oder kein voriger Blick.
    """
    # ── Eingabe-Validierung ──
    if inst.form_id != "F9" or inst.previous_gaze is None:
        raise ValueError(f"_insight_away_x: {inst.form_id} ohne vorigen Blick")

    # ── Verarbeitung ──
    vx = inst.previous_gaze.x
    least = catalog.F9_AWAY_MIN
    if abs(vx) >= least:
        x = vx
    else:
        x = least * (math.copysign(1.0, vx) if vx else inst.side)

    # ── Ausgabe-Verifikation ──
    if not abs(x) >= least:
        raise RuntimeError(f"_insight_away_x: {x} näher an der Mitte als {least}")
    return x


def _speaking_y(r: float, avoiding: bool) -> float:
    """Die Höhe eines Wegsehens beim Sprechen: oben 40, unten 30, seitlich 30 %; meidend ab.

    Vorbedingung: r in [0, 1).
    Nachbedingung: −0,3, 0 oder 0,3.
    Fehlerfälle: r außerhalb [0, 1).
    """
    # ── Eingabe-Validierung ──
    if not 0.0 <= r < 1.0:
        raise ValueError(f"_speaking_y: {r} außerhalb [0, 1)")

    # ── Verarbeitung ──
    if avoiding:
        y = 0.3 if r < 0.7 else 0.0
    else:
        y = -0.3 if r < 0.4 else 0.3 if r < 0.7 else 0.0

    # ── Ausgabe-Verifikation ──
    if y not in (-0.3, 0.0, 0.3):
        raise RuntimeError(f"_speaking_y: {y}")
    return y


def _recall_y(r: float, inputs: _Inputs) -> float:
    """Die Höhe des Erinnerns: oben 40, unten 30, seitlich 30 %; meidend ab; Ärger seitlich.

    Vorbedingung: r in [0, 1).
    Nachbedingung: eine der Höhen −0,45, 0, 0,2, 0,35.
    Fehlerfälle: r außerhalb [0, 1).
    """
    # ── Eingabe-Validierung ──
    if not 0.0 <= r < 1.0:
        raise ValueError(f"_recall_y: {r} außerhalb [0, 1)")

    # ── Verarbeitung ──
    if inputs.anger:
        y = 0.0 if r < 0.6 else 0.2
    elif inputs.avoiding:
        y = 0.35 if r < 0.7 else 0.0
    else:
        y = -0.45 if r < 0.4 else 0.35 if r < 0.7 else 0.0

    # ── Ausgabe-Verifikation ──
    if y not in (-0.45, 0.0, 0.2, 0.35):
        raise RuntimeError(f"_recall_y: {y}")
    return y


def _gaze_program(program: str, side: int, inputs: _Inputs, rng: Mulberry32) -> _Gaze:
    """Der Blickpunkt eines Blickprogramms; die erste Ziehung fällt immer, auch ungenutzt.

    Vorbedingung: ein Programm außer `continue`, side −1 oder 1.
    Nachbedingung: ein Blickpunkt; beim Pendel mit zweitem Punkt.
    Fehlerfälle: ein unbekanntes Programm.
    """
    # ── Eingabe-Validierung ──
    if program not in catalog.GAZE_PROGRAMS or program == catalog.GAZE_CONTINUE:
        raise ValueError(f"_gaze_program: Programm {program!r} unbekannt")

    # ── Verarbeitung ──
    r = rng.next()
    if program in _DRAWING_GAZE_PROGRAMS:
        gaze = _gaze_drawn(program, side, inputs, rng)
    else:
        gaze = _gaze_fixed(program, r, side, inputs)

    # ── Ausgabe-Verifikation ──
    if not (math.isfinite(gaze.x) and math.isfinite(gaze.y)):
        raise RuntimeError(f"_gaze_program: {program} ergibt {gaze}")
    return gaze


# Die Programme, die nach der ersten Ziehung weitere ziehen; die übrigen nutzen nur sie.
_DRAWING_GAZE_PROGRAMS = frozenset({catalog.GAZE_BLANK, catalog.GAZE_BLANK_UP})


def _gaze_drawn(program: str, side: int, inputs: _Inputs, rng: Mulberry32) -> _Gaze:
    """Der Blickpunkt ins Leere: zieht nach der ersten Ziehung weiter, x vor y.

    Vorbedingung: `blank` oder `blank_up`, side −1 oder 1.
    Nachbedingung: ein Blickpunkt ohne zweiten Punkt.
    Fehlerfälle: ein anderes Programm, eine andere Seite.
    """
    # ── Eingabe-Validierung ──
    if program not in _DRAWING_GAZE_PROGRAMS or side not in (-1, 1):
        raise ValueError(f"_gaze_drawn: Programm {program!r}, Seite {side}")

    # ── Verarbeitung ──
    if program == catalog.GAZE_BLANK_UP:
        gaze = _Gaze(side * rng.uniform(0.1, 0.25), -0.1)
    elif inputs.avoiding:
        gaze = _Gaze(side * rng.uniform(0.05, 0.15), 0.35)
    else:
        x = side * rng.uniform(0.12, 0.3)
        gaze = _Gaze(x, rng.uniform(-0.05, 0.1))

    # ── Ausgabe-Verifikation ──
    if gaze.x2 is not None:
        raise RuntimeError(f"_gaze_drawn: {program} mit zweitem Punkt")
    return gaze


def _gaze_fixed(program: str, r: float, side: int, inputs: _Inputs) -> _Gaze:
    """Der Blickpunkt der Programme ohne weitere Ziehung; nur Erinnern und Sprechen nutzen r.

    Vorbedingung: ein Programm außer `continue`, `blank`, `blank_up`; side −1 oder 1.
    Nachbedingung: ein Blickpunkt; einen zweiten Punkt hat nur das Pendel.
    Fehlerfälle: ein ziehendes Programm, eine andere Seite.
    """
    # ── Eingabe-Validierung ──
    if program in _DRAWING_GAZE_PROGRAMS or side not in (-1, 1):
        raise ValueError(f"_gaze_fixed: Programm {program!r}, Seite {side}")

    # ── Verarbeitung ──
    if program == catalog.GAZE_RECALL:
        gaze = _Gaze((0.35 if inputs.anger else 0.5) * side, _recall_y(r, inputs))
    elif program == catalog.GAZE_PENDULUM:
        gaze = _Gaze(-0.3 * side, 0.05, 0.25 * side)
    elif program == catalog.GAZE_SPEAKING:
        gaze = _Gaze(0.4 * side, _speaking_y(r, inputs.avoiding))
    else:
        gaze = _Gaze(0.0, 0.0)

    # ── Ausgabe-Verifikation ──
    if (gaze.x2 is not None) != (program == catalog.GAZE_PENDULUM):
        raise RuntimeError(f"_gaze_fixed: {program} ergibt {gaze}")
    return gaze


def _averted(gaze: _Gaze) -> bool:
    """Abgewandt heißt: mehr als 0,12 zur Seite oder mehr als 0,15 nach oben oder unten.

    Vorbedingung: ein Blickpunkt.
    Nachbedingung: True, wenn der Blick nicht beim Betrachter ist.
    Fehlerfälle: nicht endlicher Blickpunkt.
    """
    # ── Eingabe-Validierung ──
    if not (math.isfinite(gaze.x) and math.isfinite(gaze.y)):
        raise ValueError(f"_averted: Blickpunkt {gaze} nicht endlich")

    # ── Verarbeitung ──
    averted = abs(gaze.x) > 0.12 or abs(gaze.y) > 0.15

    # ── Ausgabe-Verifikation ──
    if averted and abs(gaze.x) <= 0.12 and abs(gaze.y) <= 0.15:
        raise RuntimeError("_averted: Widerspruch")
    return averted


def _mirror_gaze(inst: _FormInstance) -> None:
    """R6: Die Form blickt zur anderen Seite — Blickpunkt, Pendel und Seite gespiegelt.

    Vorbedingung: eine geplante Form.
    Nachbedingung: x (und x2) mit umgekehrtem Vorzeichen, die Seite umgekehrt.
    Fehlerfälle: keine Seite ±1.
    """
    # ── Eingabe-Validierung ──
    if inst.side not in (-1, 1):
        raise ValueError(f"_mirror_gaze: Seite {inst.side}")

    # ── Verarbeitung ──
    side_before = inst.side
    inst.gaze.x = -inst.gaze.x
    if inst.gaze.x2 is not None:
        inst.gaze.x2 = -inst.gaze.x2
    inst.side = -inst.side

    # ── Ausgabe-Verifikation ──
    if inst.side != -side_before:
        raise RuntimeError("_mirror_gaze: Seite nicht gespiegelt")


def _finish_targets(target: dict[str, float], now: float, inputs: _Inputs) -> FaceState:
    """Der Schluss der Ziele: Rauschen, Kiefer, Grenzen der Mundmuskeln, Lid und Augen.

    Das Rauschen der Mikroschicht kommt mit der Stärke der Lage je Kanal dazu (in der
    Antwort nur auf Brauen und Mundwinkeln), und der Kiefer folgt der begrenzten
    Öffnung, auch in der Antwort.
    Vorbedingung: Ziele aller Kanäle unter den Schlüsseln des Prototyps.
    Nachbedingung: ein `FaceState` mit endlichen Werten; `target` ist mitgeführt.
    Fehlerfälle: ein fehlender Kanal, ein nicht endliches Ziel.
    """
    # ── Eingabe-Validierung ──
    missing = [key for key in _KEYS if key not in target]
    missing += [key for key, _ in catalog.NOISE_AMPLITUDES if key not in inputs.noise]
    if missing:
        raise ValueError(f"_finish_targets: Kanäle fehlen: {missing}")

    # ── Verarbeitung ──
    for i, (key, amp) in enumerate(catalog.NOISE_AMPLITUDES):
        target[key] += amp * inputs.noise[key] * _noise(now, i + 1)
    target["mo"] = max(0, target["mo"])
    target["jaw"] = target["mo"] * JAW_FACTOR_DEFAULT
    for key in catalog.MOUTH_AU:
        target[key] = _clamp(target[key], 0.0, 1.0)
    target["lidU"] = _clamp(target["lidU"], 0.0, 1.0)
    target["eo"] = max(0.3, target["eo"])
    state = FaceState(**{name: float(target[key]) for name, key in PROTOTYPE_KEYS.items()})

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for v in target.values()):
        raise RuntimeError(f"_finish_targets: nicht endliches Ziel bei {now} ms")
    return state


# ---------------------------------------------------------------- Kopf ---------

_HeadKey = tuple[str, float, str]


def _head_section(inst: _FormInstance, u: float) -> tuple[float, _HeadKey]:
    """Der Blickabschnitt, dem der Kopf folgt: Blick x und Schlüssel des Abschnitts.

    Der Schlüssel wechselt mit der Form, mit dem Pendel von F7 und mit der Phase von
    F9 (weg bis 1 s, dann zurück zum Betrachter). Die kleinen Sakkaden zählen nicht.
    Der erste Abschnitt einer gewöhnlichen Form trägt die Phase "".
    Vorbedingung: eine geplante Form, u ms seit ihrem Beginn.
    Nachbedingung: ein endliches x und ein Schlüssel mit Form und Beginn.
    Fehlerfälle: nicht endliches u.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(u):
        raise ValueError(f"_head_section: u {u} nicht endlich")

    # ── Verarbeitung ──
    form_id, t0 = inst.form_id, inst.t0
    if form_id == "F7":
        x2 = inst.gaze.x2 if inst.gaze.x2 is not None else inst.gaze.x
        section = (x2 if inst.pendulum else inst.gaze.x, (form_id, t0, f"p{inst.pendulum}"))
    elif form_id == "F9":
        away = u < 1000
        section = (_insight_away_x(inst) if away else 0.0,
                   (form_id, t0, "weg" if away else "zurueck"))
    else:
        section = (inst.gaze.x, (form_id, t0, ""))

    # ── Ausgabe-Verifikation ──
    if not math.isfinite(section[0]):
        raise RuntimeError(f"_head_section: {form_id} ohne endlichen Blick")
    return section


def _head_rule(inst: _FormInstance, x: float, state: IdleState) -> tuple[float, str, float]:
    """Das Kopfziel zum Blick x: Ziel in Grad, Art und Verzögerung in ms.

    |x| ≤ 0,12 → 0 nach 150 ms ('zurueck'); im Nachdenken, bei einer ziehbaren Form
    außer F7 und F9 und |x| ≥ 0,25 → Seite · 10 · (0,9 + 0,2·h) ('tief'); sonst
    Seite · 10 · |x| · (0,6 + 0,4·h) ('klein'), beide nach 200 ms.
    Vorbedingung: x endlich, h der Form in [0, 1).
    Nachbedingung: ein Ziel innerhalb ±YAW_MAX.
    Fehlerfälle: nicht endliches x, h außerhalb [0, 1).
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(x) or not 0.0 <= inst.head_h < 1.0:
        raise ValueError(f"_head_rule: x {x}, h {inst.head_h}")

    # ── Verarbeitung ──
    side = 1 if x > 0 else -1
    deep = (state is IdleState.THINKING and inst.form_id in catalog.HEAD_DEEP_FORMS
            and abs(x) >= catalog.HEAD_SIDE_DEEP)
    if abs(x) <= catalog.HEAD_SIDE:
        rule = (0.0, catalog.HEAD_BACK, catalog.HEAD_RETURN_MS)
    elif deep:
        rule = (side * catalog.HEAD_DEEP * (0.9 + 0.2 * inst.head_h), catalog.HEAD_DEEP_KIND,
                catalog.HEAD_FOLLOWS_MS)
    else:
        rule = (side * catalog.HEAD_PER_GAZE * abs(x) * (0.6 + 0.4 * inst.head_h),
                catalog.HEAD_SMALL, catalog.HEAD_FOLLOWS_MS)

    # ── Ausgabe-Verifikation ──
    if not abs(rule[0]) <= catalog.YAW_MAX:
        raise RuntimeError(f"_head_rule: Ziel {rule[0]} jenseits ±{catalog.YAW_MAX}")
    return rule


@dataclass(frozen=True)
class _HeadWaiting:
    """Ein Kopfziel, das erst ab `from_ms` gilt, mit dem, woraus es entstand."""

    from_ms: float
    target: float
    kind: str
    gaze_x: float
    gaze_change_ms: float


class _HeadTurn:
    """Die Kopfdrehung: Ziel nach der Regel, verzögert, der Reihe nach; dazu ein Wandern.

    Zieht keine Zufallszahl — h je Form zieht `IdleLogic` aus der eigenen Quelle des
    Kopfs. Abgeschaltet (`enabled` False) plant sie genau gleich, nur das Ziel ist 0:
    der Zwilling.
    """

    def __init__(self, enabled: bool, trace: IdleTrace | None) -> None:
        """Beginnt beim Betrachter, ohne Abschnitt und ohne wartendes Ziel.

        Vorbedingung: enabled ist ein Wahrheitswert; trace ein Verlauf oder None.
        Nachbedingung: Ziel 0, keine Warteschlange.
        Fehlerfälle: falsche Typen.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(enabled, bool):
            raise TypeError(f"_HeadTurn: enabled {enabled!r} ist kein Wahrheitswert")
        if trace is not None and not isinstance(trace, IdleTrace):
            raise TypeError(f"_HeadTurn: trace ist kein IdleTrace: {type(trace).__name__}")

        # ── Verarbeitung ──
        self._enabled = enabled
        self._trace = trace
        self._target = 0.0
        self._key: _HeadKey | None = None
        self._waiting: list[_HeadWaiting] = []

        # ── Ausgabe-Verifikation ──
        if self._waiting or self._target != 0.0:
            raise RuntimeError("_HeadTurn: Beginn nicht beim Betrachter")

    def step(self, now: float, inst: _FormInstance, state: IdleState) -> None:
        """Ein Schritt: ein neuer Blickabschnitt reiht sein Ziel ein; fällige werden gültig.

        Ein Abschnitt, der den Blick der vorigen Form fortsetzt (E1, A0 nach einem
        abgewandten Blick), behält auch deren Kopfziel. Die Ziele gelten der Reihe nach:
        Ein später eingereihtes mit kürzerer Verzögerung wartet auf das vor ihm.
        Vorbedingung: now endlich; die laufende Form.
        Nachbedingung: kein fälliges Ziel wartet mehr.
        Fehlerfälle: nicht endliche Zeit.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(now):
            raise ValueError(f"_HeadTurn.step: Zeit {now} nicht endlich")

        # ── Verarbeitung ──
        x, key = _head_section(inst, now - inst.t0)
        if key != self._key:
            self._key = key
            if not (key[2] == "" and inst.head_inherits):
                target, kind, delay = _head_rule(inst, x, state)
                self._waiting.append(_HeadWaiting(now + delay, target, kind, x, now))
        while self._waiting and self._waiting[0].from_ms <= now:
            due = self._waiting.pop(0)
            self._target = due.target
            if self._trace is not None:
                self._trace.heads.append(
                    TracedHead(now, due.target, due.kind, due.gaze_x, due.gaze_change_ms))

        # ── Ausgabe-Verifikation ──
        if self._waiting and self._waiting[0].from_ms <= now:
            raise RuntimeError("_HeadTurn.step: ein fälliges Ziel wartet noch")

    def target(self, now: float) -> float:
        """Das Ziel von yaw: Regel plus leises Wandern, hart begrenzt; abgeschaltet 0.

        Vorbedingung: now endlich.
        Nachbedingung: ein Ziel in ±YAW_MAX.
        Fehlerfälle: nicht endliche Zeit.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(now):
            raise ValueError(f"_HeadTurn.target: Zeit {now} nicht endlich")

        # ── Verarbeitung ──
        yaw = 0.0
        if self._enabled:
            wander = catalog.HEAD_WANDER * _noise(now, catalog.HEAD_WANDER_CHANNEL)
            yaw = _clamp(self._target + wander, -catalog.YAW_MAX, catalog.YAW_MAX)

        # ── Ausgabe-Verifikation ──
        if not abs(yaw) <= catalog.YAW_MAX:
            raise RuntimeError(f"_HeadTurn.target: {yaw} jenseits ±{catalog.YAW_MAX}")
        return yaw


# ---------------------------------------------------------------- Leerlauf -----


class IdleLogic:
    """Der Leerlauf: Zustände, Pläne, Blick und Lidschläge, Schritt für Schritt.

    Schnittstelle: `post(ereignis)` reiht ein Ereignis des Clients ein (stabil nach
    seiner Zeit), `step(now_ms, gaze_x, gaze_y)` behandelt die fälligen und liefert
    ein `IdleFrame`. `gaze_x`, `gaze_y` sind der Blick, den das Gesicht gerade zeigt
    (die Feder); gegen ihn misst der Leerlauf den Blickwechsel beim Beginn eines
    neuen Zustands. Die Lage im Raum steht in v1 fest (`idle_catalog.SPACE_*`).
    """

    def __init__(
        self, seed: int, nova: Mood = NEUTRAL_MOOD, running_jobs: Sequence[PixieJob] = (),
        trace: IdleTrace | None = None, head_turn: bool = True,
    ) -> None:
        """Beginnt im Rauschen; Aufträge, die schon laufen, setzen vorher den Rückfall.

        Vorbedingung: seed ganzzahlig; `nova` Novas Emotion zu Beginn (die ihrer
        letzten Antwort, vor der ersten neutral); `running_jobs` Pixies Aufträge mit
        at_ms ≤ 0; `trace` sammelt den Verlauf, wenn gesetzt; `head_turn` False hält
        das Ziel des Kopfs bei 0 und plant sonst genau gleich (der Zwilling).
        Nachbedingung: Zustand Rauschen mit dem ersten Zyklus, erster Lidschlag bei 1,2 s.
        Fehlerfälle: falsche Typen, ein laufender Auftrag mit at_ms > 0.
        """
        # ── Eingabe-Validierung ──
        jobs = tuple(running_jobs)
        if not isinstance(nova, Mood) or not all(isinstance(j, PixieJob) for j in jobs):
            raise TypeError("IdleLogic: nova ist kein Mood oder ein Auftrag kein PixieJob")
        if any(j.at_ms > 0 for j in jobs):
            raise ValueError("IdleLogic: ein laufender Auftrag trägt at_ms > 0")
        if trace is not None and not isinstance(trace, IdleTrace):
            raise TypeError(f"IdleLogic: trace ist kein IdleTrace: {type(trace).__name__}")

        # ── Verarbeitung ──
        self._rng = Mulberry32(seed)
        self._head_rng = Mulberry32(head_seed(seed))  # h je Form, nie aus dem Plan
        self._head = _HeadTurn(head_turn, trace)
        self._trace = trace
        self._queue = _EventQueue()
        self._nova = _Emotion(_sector_of(nova.emotion), _arousal_of(nova.arousal, "Nova"))
        self._pixie = _Emotion(0, 0.0)
        self._activity = catalog.ACTIVITY_IDLE
        self._weighting: str | None = None
        self._tracks: dict[str, _Job | None] = dict.fromkeys(catalog.TRACKS)
        self._job_count = 0
        self._situation = _Situation()
        self._plan: _Plan | None = None
        self._index = 0
        self._before_last: str | None = None
        self._last_drawn: frozenset[str] = frozenset()
        self._playback_ms = 0.0
        self._answer_at_ms: float | None = None
        self._lid = _Lid()
        self._lid_open = 1.0
        self._face_omega = 5.0
        self._gaze = _Gaze(0.0, 0.0)  # das Gesicht beginnt neutral
        self._now = 0.0
        self._handlers: Mapping[type, Callable[[IdleEvent, float, bool], None]] = {
            TurnBegins: self._on_turn_begins, TurnFailed: self._on_turn_failed,
            AnswerArrives: self._on_answer, ImpulseThinks: self._on_impulse,
            PixieJob: self._on_pixie_job,
        }
        for job in jobs:
            self._handle(job, 0.0)
        self._set_state(IdleState.NOISE, 0.0, "Start", None)
        self._lid.next_ms = catalog.BLINK_FIRST_MS

        # ── Ausgabe-Verifikation ──
        if self._plan is None or not self._plan.forms:
            raise RuntimeError("IdleLogic: kein erster Zyklus")

    # ------------------------------------------------------------ Schnittstelle

    def post(self, event: IdleEvent) -> None:
        """Reiht ein Ereignis ein; gleiche Zeiten bleiben in der Reihenfolge des Eintreffens.

        Vorbedingung: ein Ereignis mit endlicher Zeit; eine Antwort mit endlicher
        Dauer der Wiedergabe ≥ 0.
        Nachbedingung: das Ereignis steht in der Warteschlange nach seiner Zeit.
        Fehlerfälle: ein fremder Typ, eine nicht endliche Zeit oder Dauer.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(event, _EVENT_TYPES):
            raise TypeError(f"post: kein Ereignis des Leerlaufs: {type(event).__name__}")
        if not math.isfinite(event.at_ms):
            raise ValueError(f"post: Zeit {event.at_ms!r} nicht endlich")
        if isinstance(event, AnswerArrives) and not (
                math.isfinite(event.playback_ms) and event.playback_ms >= 0):
            raise ValueError(f"post: Dauer der Wiedergabe {event.playback_ms!r} ungültig")

        # ── Verarbeitung ──
        self._queue.push(event)

    def status(self, now_ms: float) -> IdleStatus:
        """Die Phase zu `now_ms`: Zustand, Form, nächste Form, Band, Spanne — nur gelesen.

        Zieht keine Zufallszahl, setzt kein Feld und behandelt kein Ereignis; die Spanne
        ist die, mit der der Plan gerechnet wurde.
        Vorbedingung: now_ms endlich und nicht vor dem letzten Schritt.
        Nachbedingung: ein Wert zum Stand des letzten Schritts, die Logik unverändert.
        Fehlerfälle: nicht endliche oder rückläufige Zeit.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(now_ms, int | float) or not math.isfinite(now_ms):
            raise ValueError(f"status: Zeit {now_ms!r} nicht endlich")
        if now_ms < self._now:
            raise ValueError(f"status: Zeit {now_ms} vor dem letzten Schritt {self._now}")

        # ── Verarbeitung ──
        now = float(now_ms)
        plan = self._plan
        if plan is None:
            raise RuntimeError("status: kein Plan")
        return _build_status(now, self._situation, plan, self._index, self._inputs(now))

    def step(self, now_ms: float, gaze_x: float, gaze_y: float) -> IdleFrame:
        """Ein Schritt: fällige Ereignisse, Zustand, Form, Sakkaden, Lidschläge, Ziele.

        Vorbedingung: now_ms endlich und nicht vor dem letzten Schritt; der Blick
        des Gesichts endlich.
        Nachbedingung: ein Bild mit den Zielen aller Kanäle und einem Lid in 0..1.
        Fehlerfälle: rückwärts laufende Zeit, nicht endliche Werte.
        """
        # ── Eingabe-Validierung ──
        values = (now_ms, gaze_x, gaze_y)
        if not all(isinstance(v, int | float) and math.isfinite(v) for v in values):
            raise ValueError(f"step: nicht endliche Eingabe {values}")
        if now_ms < self._now:
            raise ValueError(f"step: Zeit {now_ms} vor dem letzten Schritt {self._now}")

        # ── Verarbeitung ──
        now = self._now = float(now_ms)
        self._gaze = _Gaze(float(gaze_x), float(gaze_y))
        for event in self._queue.pop_due(now):
            self._handle(event, now)
        self._check_state(now)
        self._check_form(now)
        inst = self._current()
        inputs = self._inputs(now)
        self._saccades(now, inst)
        self._head.step(now, inst, inputs.state)  # nach den Sakkaden: das Pendel steht
        self._blinks(now, inputs, inst)
        targets = self._targets(now, inputs, inst)
        self._trace_mouth(inputs, targets)
        answering = inputs.state is IdleState.ANSWER
        frame = IdleFrame(inputs.state, inst.form_id, targets, self._lid_open, self._face_omega,
                          inputs.amplitude, inputs.activity,
                          self._answer_at_ms if answering else None, self._head.target(now))

        # ── Ausgabe-Verifikation ──
        if not 0.0 <= frame.lid_open <= 1.0:
            raise RuntimeError(f"step: Lid {frame.lid_open} außerhalb 0..1")
        if answering and frame.answer_at_ms is None:
            raise RuntimeError("step: Antwort ohne die Zeit der gesprochenen Antwort")
        return frame

    # ------------------------------------------------------------ Ereignisse

    def _handle(self, event: IdleEvent, now: float) -> None:
        """Der Verteiler: ein Ereignis, wie der Client es bekommt.

        Vorbedingung: ein Ereignis des Leerlaufs.
        Nachbedingung: das Ereignis ist behandelt und im Verlauf vermerkt; ein
        Einatmen gibt es nur im Nachdenken.
        Fehlerfälle: ein Typ ohne Behandlung.
        """
        # ── Eingabe-Validierung ──
        handler = self._handlers.get(type(event))
        if handler is None:
            raise TypeError(f"_handle: kein Verteiler für {type(event).__name__}")

        # ── Verarbeitung ──
        if self._trace is not None:
            self._trace.events.append(TracedEvent(event.at_ms, event.event_type, now))
        situation = self._situation
        without_answer = situation.state is IdleState.THINKING and not situation.inhaling
        handler(event, now, without_answer)

        # ── Ausgabe-Verifikation ──
        if self._situation.inhaling and self._situation.state is not IdleState.THINKING:
            raise RuntimeError("_handle: Einatmen außerhalb des Nachdenkens")

    def _on_turn_begins(self, event: IdleEvent, now: float, without_answer: bool) -> None:
        """Ein neuer Turn unterbricht jeden Zustand sofort und verwirft eine wartende Antwort.

        Vorbedingung: ein `TurnBegins`.
        Nachbedingung: Nachdenken, begonnen vom Turn.
        Fehlerfälle: ein anderes Ereignis.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(event, TurnBegins):
            raise TypeError(f"_on_turn_begins: {type(event).__name__}")

        # ── Verarbeitung ──
        self._set_state(IdleState.THINKING, now, "Turn beginnt", ORIGIN_TURN)

        # ── Ausgabe-Verifikation ──
        if self._situation.origin != ORIGIN_TURN:
            raise RuntimeError("_on_turn_begins: Herkunft nicht gesetzt")

    def _on_turn_failed(self, event: IdleEvent, now: float, without_answer: bool) -> None:
        """Der Turn scheitert: zurück ins Rauschen.

        Nur aus einem Nachdenken des Turns, auf das keine Antwort kam.
        Vorbedingung: ein `TurnFailed`.
        Nachbedingung: Rauschen, wenn das Nachdenken vom Turn kam und keine Antwort wartet.
        Fehlerfälle: ein anderes Ereignis.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(event, TurnFailed):
            raise TypeError(f"_on_turn_failed: {type(event).__name__}")

        # ── Verarbeitung ──
        applies = without_answer and self._situation.origin == ORIGIN_TURN
        if applies:
            self._set_state(IdleState.NOISE, now, "Turn gescheitert", None)

        # ── Ausgabe-Verifikation ──
        if applies and self._situation.state is not IdleState.NOISE:
            raise RuntimeError("_on_turn_failed: nicht im Rauschen")

    def _on_impulse(self, event: IdleEvent, now: float, without_answer: bool) -> None:
        """Ein Impuls denkt; er stört weder einen Turn noch das Gespräch.

        `beginn` im Nachdenken eines Turns, im Einatmen und in der Antwort bleibt
        ohne Wirkung; `ende` beendet nur ein Nachdenken, das der Impuls begann und
        auf das keine Antwort kam.
        Vorbedingung: ein `ImpulseThinks`.
        Nachbedingung: Zustand wie oben; eine unbekannte Phase ergibt eine Error-Zeile.
        Fehlerfälle: ein anderes Ereignis.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(event, ImpulseThinks):
            raise TypeError(f"_on_impulse: {type(event).__name__}")
        if event.phase not in (catalog.PHASE_BEGIN, catalog.PHASE_END):
            logger.error(f"Leerlauf: impuls_denkt mit phase {event.phase!r}")
            return

        # ── Verarbeitung ──
        situation = self._situation
        if event.phase == catalog.PHASE_BEGIN:
            busy = situation.inhaling or situation.state is IdleState.ANSWER or (
                situation.state is IdleState.THINKING and situation.origin == ORIGIN_TURN)
            if busy:
                logger.debug("Leerlauf: Impuls denkt — stört den Turn nicht")
            else:
                self._set_state(IdleState.THINKING, now, "Impuls denkt", ORIGIN_IMPULSE)
        elif without_answer and situation.origin == ORIGIN_IMPULSE:
            self._set_state(IdleState.NOISE, now, "Impuls ohne Antwort", None)

        # ── Ausgabe-Verifikation ──
        if self._situation.origin == ORIGIN_IMPULSE and self._situation.state is not (
                IdleState.THINKING):
            raise RuntimeError("_on_impulse: Herkunft Impuls außerhalb des Nachdenkens")

    def _on_answer(self, event: IdleEvent, now: float, without_answer: bool) -> None:
        """Eine Antwort trifft ein: Einatmen, dann Antwort; in der Antwort löst sie die laufende ab.

        Im Einatmen ersetzt sie die wartende; kommt sie ohne Nachdenken, besteht das
        Nachdenken nur aus dem Einatmen.
        Vorbedingung: ein `AnswerArrives`.
        Nachbedingung: Antwort oder Nachdenken mit Einatmen und wartender Antwort.
        Fehlerfälle: ein anderes Ereignis.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(event, AnswerArrives):
            raise TypeError(f"_on_answer: {type(event).__name__}")

        # ── Verarbeitung ──
        answer = _Answer(_sector_of(event.emotion), _arousal_of(event.arousal, "Antwort"),
                         float(event.playback_ms), float(event.at_ms))
        if self._situation.state is IdleState.ANSWER:
            self._begin_answer(now, answer, "eine neue Antwort löst die laufende ab")
        else:
            self._situation.waiting = answer
            if not self._situation.inhaling:
                self._inhale(now)

        # ── Ausgabe-Verifikation ──
        settled = self._situation.state is IdleState.ANSWER or (
            self._situation.inhaling and self._situation.waiting is answer)
        if not settled:
            raise RuntimeError("_on_answer: weder Antwort noch Einatmen mit wartender Antwort")

    def _on_pixie_job(self, event: IdleEvent, now: float, without_answer: bool) -> None:
        """Pixie beginnt oder beendet einen Auftrag; das setzt nur den Rückfall.

        Vorbedingung: ein `PixieJob`.
        Nachbedingung: die Spur trägt den Auftrag oder ist frei, der Rückfall ist neu
        gesetzt; eine unbekannte Spur oder Phase ergibt eine Error-Zeile.
        Fehlerfälle: ein anderes Ereignis.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(event, PixieJob):
            raise TypeError(f"_on_pixie_job: {type(event).__name__}")
        if event.track not in self._tracks:
            logger.error(f"Leerlauf: pixie_auftrag mit spur {event.track!r}")
            return
        if event.phase not in (catalog.PHASE_BEGIN, catalog.PHASE_END):
            logger.error(f"Leerlauf: pixie_auftrag mit phase {event.phase!r}")
            return

        # ── Verarbeitung ──
        if event.phase == catalog.PHASE_BEGIN:
            with_emotion = event.emotion is not None
            self._job_count += 1
            self._tracks[event.track] = _Job(
                self._job_count, str(event.job_kind or ""),
                _sector_of(event.emotion) if with_emotion else None,
                _arousal_of(event.arousal, "Auftrag") if with_emotion else 0.0)
        else:
            self._tracks[event.track] = None
        self._update_fallback()

        # ── Ausgabe-Verifikation ──
        if (self._tracks[event.track] is None) != (event.phase == catalog.PHASE_END):
            raise RuntimeError("_on_pixie_job: Spur nicht gesetzt")

    def _update_fallback(self) -> None:
        """Der Rückfall: Emotion des jüngsten laufenden Auftrags mit Emotion, Aktivität, Art.

        Ein Auftrag ohne Emotion verdrängt keinen mit; läuft keiner mit Emotion,
        neutral mit Arousal 0. Die Art kommt vom selben Auftrag, ohne Auftrag mit
        Emotion vom zuletzt begonnenen.
        Vorbedingung: die Spuren.
        Nachbedingung: Pixies Emotion, Aktivität 0,6 oder 0,2, Gewichtung gesetzt.
        Fehlerfälle: ein Sektor außerhalb 0–8.
        """
        # ── Eingabe-Validierung ──
        running = sorted((j for j in self._tracks.values() if j is not None),
                         key=lambda j: j.number, reverse=True)
        if any(j.sector is not None and not 0 <= j.sector < 9 for j in running):
            raise ValueError("_update_fallback: Sektor außerhalb 0–8")

        # ── Verarbeitung ──
        source = next((j for j in running if j.sector is not None),
                      running[0] if running else None)
        has_emotion = source is not None and source.sector is not None
        self._pixie.sector = source.sector if has_emotion else 0
        self._pixie.arousal = source.arousal if has_emotion else 0.0
        self._activity = catalog.ACTIVITY_JOB if running else catalog.ACTIVITY_IDLE
        self._weighting = catalog.JOB_WEIGHTING.get(source.job_kind) if source else None

        # ── Ausgabe-Verifikation ──
        if not 0.0 <= self._pixie.arousal <= 1.0:
            raise RuntimeError(f"_update_fallback: Arousal {self._pixie.arousal}")

    # ------------------------------------------------------------ Zustände

    def _set_state(self, name: IdleState, now: float, reason: str, origin: str | None,
                   glide_from: _Inputs | None = None) -> None:
        """Wechselt den Zustand, verwirft eine wartende Antwort und plant neu.

        Eine Antwort gleitet über A0 aus `glide_from` (dem Gesicht vor dem ersten
        Laut), ohne es aus der Lage dieses Augenblicks. Der Nachklang zählt die
        gekoppelten Lidschläge ab dem Beginn der Antwort.
        Vorbedingung: ein Zustand; `origin` sagt, wer ein Nachdenken begann.
        Nachbedingung: der Zustand gilt ab now mit neuem Plan, dessen erste Form begonnen hat.
        Fehlerfälle: kein Zustand; eine Antwort, die nicht mit A0 beginnt.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(name, IdleState):
            raise TypeError(f"_set_state: kein Zustand: {name!r}")

        # ── Verarbeitung ──
        previous = self._current() if self._plan is not None else None
        situation = self._situation
        if name is IdleState.ANSWER:
            before = glide_from if glide_from is not None else self._inputs(now)
            situation.glide_basis, situation.glide_noise = before.basis, before.noise
            situation.glide_ms = math.inf  # bis A0 geplant ist
        situation.blink_since = situation.since if name is IdleState.AFTERGLOW else now
        situation.state, situation.since = name, now
        situation.inhaling, situation.answer_from, situation.waiting = False, math.inf, None
        situation.origin = origin
        opening = None
        if name is IdleState.ANSWER:
            situation.playback_end = now + self._playback_ms
            situation.playback_reported = False
            situation.answer_end = situation.playback_end + catalog.PLAYBACK_TAIL_MS
        if name is IdleState.AFTERGLOW:
            base = catalog.AFTERGLOW_BASE_MS + catalog.AFTERGLOW_NEAR_MS * catalog.SPACE_NEARNESS
            situation.afterglow_duration = _clamp(base * self._rng.uniform(0.8, 1.2),
                                                  *catalog.AFTERGLOW_LIMITS_MS)
            situation.afterglow_end = now + situation.afterglow_duration
            opening = "F16"
        self._trace_state(now, name, reason)
        self._plan_next(now, opening, previous)
        if name is IdleState.ANSWER:
            situation.glide_ms = self._current().duration
        self._form_begins(None, self._current(), now)

        # ── Ausgabe-Verifikation ──
        if self._situation.state is not name:
            raise RuntimeError(f"_set_state: {name.value} nicht gesetzt")
        if name is IdleState.ANSWER and self._current().form_id != "A0":
            raise RuntimeError(f"_set_state: die Antwort beginnt mit {self._current().form_id}")

    def _trace_state(self, now: float, name: IdleState, reason: str) -> None:
        """Vermerkt einen Zustandswechsel im Verlauf, mit der Grenze von Antwort und Nachklang.

        Vorbedingung: ein Zustand.
        Nachbedingung: ein Eintrag mehr, wenn ein Verlauf mitläuft.
        Fehlerfälle: kein Zustand.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(name, IdleState):
            raise TypeError(f"_trace_state: kein Zustand: {name!r}")
        if self._trace is None:
            return

        # ── Verarbeitung ──
        until = {IdleState.ANSWER: self._situation.answer_end,
                 IdleState.AFTERGLOW: self._situation.afterglow_end}.get(name)
        self._trace.states.append(TracedState(now, name, reason, until))

        # ── Ausgabe-Verifikation ──
        if self._trace.states[-1].state is not name:
            raise RuntimeError("_trace_state: Eintrag fehlt")

    def _inhale(self, now: float) -> None:
        """Die Antwort ist da: das Einatmen (E1) beginnt jetzt und ersetzt den Rest des Zyklus.

        Kommt die Antwort ohne Nachdenken, gehört das Einatmen zum Nachdenken, ohne
        Zyklus davor. Im Einatmen gilt noch Novas Emotion vor der Antwort.
        Vorbedingung: eine wartende Antwort, kein Einatmen.
        Nachbedingung: Nachdenken mit Einatmen bis `answer_from`, E1 hat begonnen.
        Fehlerfälle: keine wartende Antwort oder schon im Einatmen.
        """
        # ── Eingabe-Validierung ──
        situation = self._situation
        if situation.waiting is None or situation.inhaling:
            raise RuntimeError("_inhale: keine wartende Antwort oder schon im Einatmen")

        # ── Verarbeitung ──
        duration = self._rng.uniform(*catalog.INHALE_MS)
        old = self._current()
        plan = self._plan
        if situation.state is IdleState.THINKING and plan is not None:
            old.duration = now - old.t0
            del plan.forms[self._index + 1:]
        else:
            situation.state, situation.since = IdleState.THINKING, now
            situation.blink_since = now
            self._trace_state(now, IdleState.THINKING, "Antwort ohne Nachdenken")
            plan = self._plan = _Plan(_PLAN_INHALE, [], frozenset())
        situation.inhaling, situation.answer_from = True, now + duration
        inst = self._instance("E1", self._inputs(now), (now, duration), old)
        plan.forms.append(inst)
        self._index = len(plan.forms) - 1
        self._form_begins(old, inst, now)

        # ── Ausgabe-Verifikation ──
        if self._current() is not inst:
            raise RuntimeError("_inhale: E1 ist nicht die laufende Form")

    def _begin_answer(self, now: float, answer: _Answer, reason: str) -> None:
        """Nova spricht mit der Emotion der Antwort; sie ist ab jetzt ihre aktuelle.

        Vorbedingung: eine Antwort.
        Nachbedingung: Zustand Antwort bis zum Ende der Wiedergabe + 0,4 s.
        Fehlerfälle: keine Antwort.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(answer, _Answer):
            raise TypeError(f"_begin_answer: keine Antwort: {answer!r}")

        # ── Verarbeitung ──
        before = self._inputs(now)  # das Gesicht vor dem ersten Laut, mit der Emotion von vorher
        self._nova.sector, self._nova.arousal = answer.sector, answer.arousal
        self._playback_ms = answer.playback_ms
        self._answer_at_ms = answer.at_ms
        self._set_state(IdleState.ANSWER, now, reason, None, before)

        # ── Ausgabe-Verifikation ──
        if self._situation.answer_end != now + answer.playback_ms + catalog.PLAYBACK_TAIL_MS:
            raise RuntimeError("_begin_answer: Ende der Antwort falsch gesetzt")

    def _check_state(self, now: float) -> None:
        """Zeitgesteuerte Wechsel: nach dem Einatmen, Wächter, Ende der Wiedergabe, Nachlauf.

        Vorbedingung: now endlich.
        Nachbedingung: der Zustand passt zur Zeit; das Ende der Wiedergabe ist vermerkt.
        Fehlerfälle: ein Einatmen ohne wartende Antwort.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(now):
            raise ValueError(f"_check_state: Zeit {now} nicht endlich")

        # ── Verarbeitung ──
        situation = self._situation
        thinking = situation.state is IdleState.THINKING
        if thinking and situation.inhaling and now >= situation.answer_from:
            if situation.waiting is None:
                raise RuntimeError("_check_state: Einatmen ohne wartende Antwort")
            self._begin_answer(now, situation.waiting, "nach dem Einatmen")
            return
        if thinking and not situation.inhaling and now - situation.since >= catalog.WATCHDOG_MS:
            logger.warning(f"Leerlauf: {catalog.WATCHDOG_MS / 1000:.0f} s ohne Antwort — Rauschen")
            self._set_state(IdleState.NOISE, now, "Wächter: keine Antwort", None)
            return
        answering = situation.state is IdleState.ANSWER
        if answering and not situation.playback_reported and now >= situation.playback_end:
            situation.playback_reported = True
            if self._trace is not None:
                self._trace.events.append(
                    TracedEvent(situation.playback_end, "wiedergabe_endet", now))
        if answering and now >= situation.answer_end:
            self._set_state(IdleState.AFTERGLOW, now, "Wiedergabe beendet", None)
            self._end_blink(now)

        # ── Ausgabe-Verifikation ──
        if self._situation.state is IdleState.ANSWER and now >= self._situation.answer_end:
            raise RuntimeError("_check_state: Antwort über ihr Ende hinaus")

    # ------------------------------------------------------------ Formen

    def _current(self) -> _FormInstance:
        """Die laufende Form.

        Vorbedingung: ein Plan mit einer Form an der laufenden Stelle.
        Nachbedingung: die Form an der laufenden Stelle.
        Fehlerfälle: kein Plan oder die Stelle liegt außerhalb.
        """
        # ── Eingabe-Validierung ──
        if self._plan is None or not 0 <= self._index < len(self._plan.forms):
            raise RuntimeError("_current: keine laufende Form")

        # ── Verarbeitung ──
        inst = self._plan.forms[self._index]

        # ── Ausgabe-Verifikation ──
        if inst.form_id not in FORMS:
            raise RuntimeError(f"_current: unbekannte Form {inst.form_id}")
        return inst

    def _check_form(self, now: float) -> None:
        """Wechselt zur nächsten Form, wenn die laufende endet; plant bei Bedarf neu.

        Die Dauer des Nachklangs ist eine Grenze: Die laufende Form endet an ihr.
        Vorbedingung: now endlich.
        Nachbedingung: die laufende Form läuft zu now.
        Fehlerfälle: nicht endliche Zeit; 60 Formen in einem Schritt — Error-Zeile.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(now):
            raise ValueError(f"_check_form: Zeit {now} nicht endlich")

        # ── Verarbeitung ──
        for _ in range(_MAX_FORMS_PER_STEP):
            situation = self._situation
            if situation.state is IdleState.AFTERGLOW and now >= situation.afterglow_end:
                self._set_state(IdleState.NOISE, now, "Nachklang vorbei", None)
                return
            old = self._current()
            end = old.t0 + old.duration
            if now < end:
                return
            if old.form_id == "F5":
                self._blink_series(end)
            self._index += 1
            if self._plan is not None and self._index >= len(self._plan.forms):
                self._plan_next(now if now - end > _FALLBACK_REPLAN_MS else end, None, None)
            self._form_begins(old, self._current(), now)

        # ── Ausgabe-Verifikation ──
        current = self._current()
        if now >= current.t0 + current.duration:
            logger.error(f"Leerlauf: {_MAX_FORMS_PER_STEP} Formen in einem Schritt bei {now} ms"
                         f" — {current.form_id} ist schon vorbei")

    def _form_begins(self, old: _FormInstance | None, new: _FormInstance, now: float) -> None:
        """Eine Form beginnt: Lidform der neuen Form, Lidschlag am Einfall oder am Blickwechsel.

        R8: Wechselt der Blick um mehr als 0,4, fällt mit 0,7 ein Lidschlag auf den
        Beginn, im Nachdenken mit 0,3. Beim Einfall genau ein langer Lidschlag; er
        ersetzt den am Blickwechsel und die ganze fällige Serie und sperrt 1 s.
        Vorbedingung: die neue Form; ohne vorige der Blick des Gesichts.
        Nachbedingung: Lidform gesetzt, die Form im Verlauf vermerkt.
        Fehlerfälle: keine Form.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(new, _FormInstance):
            raise TypeError(f"_form_begins: keine Form: {new!r}")

        # ── Verarbeitung ──
        a = old.gaze if old is not None else self._gaze
        b = new.gaze
        self._lid.scale = self._blink_scale(self._inputs(now), new.form_id)
        thinking = self._situation.state is IdleState.THINKING
        if new.form_id == "F9":
            # die längere Sperre hält Phase a und b frei von einem zweiten Lidschlag
            self._lid.series = []
            self._blink(now, 1.5, True, catalog.BLINK_INSIGHT)
            self._lid.blocked_until = now + catalog.BLINK_REFRACTORY_INSIGHT_MS
        elif _hypot(b.x - a.x, b.y - a.y) > catalog.GAZE_SHIFT_FOR_BLINK:
            p = catalog.BLINK_AT_GAZE_SHIFT_THINKING if thinking else catalog.BLINK_AT_GAZE_SHIFT
            if self._rng.next() < p:
                self._blink(now, 1.0, False, catalog.BLINK_GAZE_SHIFT)
        if self._trace is not None:
            self._trace.forms.append(TracedForm(now, self._situation.state, new.form_id, new.t0,
                                                new.duration, b.x, b.y))

        # ── Ausgabe-Verifikation ──
        if self._lid.scale not in (1.0, 1.2):
            raise RuntimeError(f"_form_begins: Lidform {self._lid.scale}")

    def _plan_next(self, start: float, opening: str | None,
                   previous: _FormInstance | None) -> None:
        """Plant ab `start`: in der Antwort die Blickregelung des Sprechers, sonst einen Zyklus.

        Ein Zyklus merkt sich, was er zog (gedämpft im nächsten) und seine letzte
        gezogene Form (R5); Antwort und Einatmen ändern das nicht.
        Vorbedingung: der Zustand ist gesetzt.
        Nachbedingung: ein Plan mit mindestens einer Form, die laufende Stelle 0.
        Fehlerfälle: ein leerer Plan.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(start):
            raise ValueError(f"_plan_next: Beginn {start} nicht endlich")

        # ── Verarbeitung ──
        plan = self._plan
        if plan is not None and plan.kind == _PLAN_CYCLE:
            self._last_drawn = plan.drawn
            drawn = [f for f in plan.forms if f.form_id in plan.drawn]
            self._before_last = drawn[-1].form_id if drawn else None
        inputs = self._inputs(start)
        if self._situation.state is IdleState.ANSWER:
            self._plan = self._plan_answer(start, inputs, previous)
        else:
            self._plan = self._plan_cycle(start, inputs, opening)
        self._index = 0

        # ── Ausgabe-Verifikation ──
        if not self._plan.forms:
            raise RuntimeError(f"_plan_next: leerer Plan im Zustand {inputs.state.value}")

    def _plan_cycle(self, start: float, inputs: _Inputs, opening: str | None) -> _Plan:
        """Ein Zyklus: 4–5 Formen nach Gewicht, nach R1–R7 geordnet, mit Dauer und Blick.

        Vorbedingung: ein Zustand mit Gruppe; `opening` eine Form, die vorangeht (F16
        zu Beginn des Nachklangs).
        Nachbedingung: ein Plan mit lückenlos aufeinander folgenden Formen.
        Fehlerfälle: ein Zustand ohne Gruppe (über `_weights`).
        """
        # ── Eingabe-Validierung ──
        if opening is not None and opening not in FORMS:
            raise ValueError(f"_plan_cycle: Eröffnung {opening!r} unbekannt")

        # ── Verarbeitung ──
        span = _span(inputs)
        weights = _weights(inputs, self._last_drawn, self._weighting)
        chosen = self._choose(weights, span, inputs)
        accent = self._accent(inputs)
        downward = (not accent and inputs.valence < 0
                    and catalog.SPACE_DIRECTION == catalog.DIRECTION_DOWN)
        if downward:
            self._end_downward(chosen, weights, inputs)
        sequence = self._order(chosen, inputs, downward)
        forms: list[_FormInstance] = []
        t = start
        if opening is not None:
            t = self._append(forms, opening, inputs, (t, self._rng.uniform(1500, 3000)))
        thinking = inputs.state is IdleState.THINKING
        for form_id in sequence:
            before = forms[-1] if forms else None
            if form_id == "F9" and thinking:  # F9 im Nachdenken: ein Akzent
                low, lo, hi = catalog.F9_THINKING_MS
                duration = low + self._rng.uniform(lo, hi)
            else:
                duration = self._rng.triangle(span.lo, span.xc, span.hi) * 1000
            t = self._append(forms, form_id, inputs, (t, duration))
            if before is not None and not _contrast(before.form_id, form_id, inputs.amplitude,
                                                    before.gaze, forms[-1].gaze):
                _mirror_gaze(forms[-1])
        if accent:
            span_ms = catalog.ACCENT_THINKING_MS if thinking else catalog.ACCENT_MS
            self._append(forms, "F16", inputs, (t, self._rng.uniform(*span_ms)))

        # ── Ausgabe-Verifikation ──
        gaps = [abs(b.t0 - (a.t0 + a.duration)) for a, b in zip(forms, forms[1:], strict=False)]
        if any(gap > 1e-6 for gap in gaps):
            raise RuntimeError(f"_plan_cycle: Lücke im Zyklus ({max(gaps)} ms)")
        return _Plan(_PLAN_CYCLE, forms, frozenset(chosen), span)

    def _choose(self, weights: dict[str, float], span: _Span, inputs: _Inputs) -> list[str]:
        """Zieht die Formen eines Zyklus und bessert nach R4 (Asymmetrien), R2 (Einfall), R1.

        Vorbedingung: Gewichte des Zustands.
        Nachbedingung: verschiedene Formen, höchstens zwei aus F6, F7, F8.
        Fehlerfälle: eine Form doppelt.
        """
        # ── Eingabe-Validierung ──
        if span.count < 1:
            raise ValueError(f"_choose: {span.count} Formen")

        # ── Verarbeitung ──
        ids = list(weights)
        chosen = _draw(self._rng, weights, min(span.count, len(ids)), None, None)
        while sum(1 for f in chosen if f in catalog.ASYMMETRIC) > 2:
            asymmetric = [f for f in chosen if f in catalog.ASYMMETRIC]
            old = sorted(asymmetric, key=lambda f: weights[f])[0]
            only = frozenset(f for f in ids if f not in catalog.ASYMMETRIC)
            new = next(iter(_draw(self._rng, weights, 1, only, chosen)), None)
            if not _replace(chosen, old, new):
                chosen.remove(old)
        if "F9" in chosen and (len(chosen) < 3 or not any(f in catalog.PRECURSORS for f in chosen)):
            new = next(iter(_draw(self._rng, weights, 1, None, [*chosen, "F9"])), None)
            if not _replace(chosen, "F9", new):
                chosen.remove("F9")
        self._secure_opener(chosen, weights, inputs)

        # ── Ausgabe-Verifikation ──
        if len(set(chosen)) != len(chosen):
            raise RuntimeError(f"_choose: Form doppelt in {chosen}")
        return chosen

    def _secure_opener(self, chosen: list[str], weights: dict[str, float],
                       inputs: _Inputs) -> None:
        """R1/R5: Ein Eröffner mit Blickwechsel muss dabei sein, nicht die letzte Form zuvor.

        Fehlt er, ersetzt ein gezogener Eröffner die schwächste Form ohne Regel.
        Vorbedingung: die gezogenen Formen.
        Nachbedingung: ein anderer Eröffner ist dabei, sofern die Gruppe einen hat.
        Fehlerfälle: eine Form doppelt.
        """
        # ── Eingabe-Validierung ──
        if len(set(chosen)) != len(chosen):
            raise ValueError(f"_secure_opener: Form doppelt in {chosen}")

        # ── Verarbeitung ──
        openers = _openers(inputs)
        if any(f in openers and f != self._before_last for f in chosen):
            return
        allowed = frozenset(f for f in openers if f != self._before_last)
        new = next(iter(_draw(self._rng, weights, 1, allowed, chosen)), None)
        _replace(chosen, _weakest(chosen, weights, openers, ()), new)

        # ── Ausgabe-Verifikation ──
        if len(set(chosen)) != len(chosen):
            raise RuntimeError(f"_secure_opener: Form doppelt in {chosen}")

    def _accent(self, inputs: _Inputs) -> bool:
        """R7: F16 als Akzent anhängen — bei Nähe ≥ 0,5 mit p = N, bei negativer Valenz N/2.

        Im Nachdenken halb so oft: dort las sich Blickkontakt am Ende als Warten.
        Vorbedingung: eine Lage.
        Nachbedingung: True mit der Wahrscheinlichkeit oben; ohne Nähe keine Ziehung.
        Fehlerfälle: keine Lage.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(inputs, _Inputs):
            raise TypeError(f"_accent: keine Lage: {type(inputs).__name__}")

        # ── Verarbeitung ──
        near = catalog.SPACE_NEARNESS
        if near < 0.5:
            return False
        share = catalog.ACCENT_THINKING_SHARE if inputs.state is IdleState.THINKING else 1.0
        p = (near if inputs.valence >= 0 else 0.5 * near) * share
        accent = self._rng.next() < p

        # ── Ausgabe-Verifikation ──
        if not 0.0 < p <= 1.0:
            raise RuntimeError(f"_accent: p = {p}")
        return accent

    def _end_downward(self, chosen: list[str], weights: dict[str, float],
                      inputs: _Inputs) -> None:
        """R7: abwärts enden heißt ein Eröffner vorn und eine andere Form aus F4, F10, F13 hinten.

        Höchstens zwei Ersetzungen, bis das Paar dabei ist.
        Vorbedingung: die gezogenen Formen.
        Nachbedingung: das Paar ist dabei, sofern die Gruppe es hergibt.
        Fehlerfälle: eine Form doppelt.
        """
        # ── Eingabe-Validierung ──
        if len(set(chosen)) != len(chosen):
            raise ValueError(f"_end_downward: Form doppelt in {chosen}")

        # ── Verarbeitung ──
        openers = _openers(inputs)
        protected = tuple(openers | catalog.DOWNWARD)
        for _ in range(2):
            pair = any(o in openers and o != self._before_last
                       and any(d in catalog.DOWNWARD and d != o for d in chosen) for o in chosen)
            if pair:
                return
            if any(f in catalog.DOWNWARD for f in chosen):
                allowed = frozenset(f for f in protected if f != self._before_last)
            else:
                allowed = catalog.DOWNWARD
            new = next(iter(_draw(self._rng, weights, 1, allowed, chosen)), None)
            _replace(chosen, _weakest(chosen, weights, openers, protected), new)

        # ── Ausgabe-Verifikation ──
        if len(set(chosen)) != len(chosen):
            raise RuntimeError(f"_end_downward: Form doppelt in {chosen}")

    def _order(self, chosen: list[str], inputs: _Inputs, downward: bool) -> list[str]:
        """Ordnet die Formen nach R1, R2, R4, R5, R7 und der Wissenslücke; lockert, wenn nötig.

        Unter den erlaubten Reihenfolgen gewinnen die mit dem meisten Kontrast, eine
        davon per Ziehung.
        Vorbedingung: die gewählten Formen.
        Nachbedingung: eine Reihenfolge derselben Formen.
        Fehlerfälle: mehr als sechs Formen.
        """
        # ── Eingabe-Validierung ──
        if len(chosen) > 6:
            raise ValueError(f"_order: {len(chosen)} Formen")

        # ── Verarbeitung ──
        openers, last = _openers(inputs), self._before_last
        gap = (inputs.state is IdleState.NOISE
               and self._weighting == catalog.WEIGHTING_KNOWLEDGE_GAP)
        checks: Mapping[str, Callable[[list[str]], bool]] = {
            "R1": lambda p: bool(p) and p[0] in openers,
            "R2": lambda p: "F9" not in p or (p.index("F9") >= 2 and any(
                f in catalog.PRECURSORS for f in p[:p.index("F9")])),
            "R4": lambda p: not any(i > 0 and p[i] in catalog.ASYMMETRIC
                                    and p[i - 1] in catalog.ASYMMETRIC for i in range(len(p))),
            "R5": lambda p: not p or p[0] != last,
            "R7": lambda p: not downward or (bool(p) and p[-1] in catalog.DOWNWARD),
            "WL": lambda p: not gap or "F6" not in p or "F9" not in p
            or p.index("F6") < p.index("F9"),
        }
        orders = _permutations(chosen)
        allowed: list[list[str]] = []
        for relaxed in _RELAXATIONS:
            allowed = [p for p in orders
                       if all(rule in relaxed or check(p) for rule, check in checks.items())]
            if allowed:
                break
        points = [_contrast_points(p, inputs.amplitude) for p in allowed]
        most = max(points)
        best = [p for p, n in zip(allowed, points, strict=True) if n == most]
        order = best[int(self._rng.next() * len(best))]

        # ── Ausgabe-Verifikation ──
        if sorted(order) != sorted(chosen):
            raise RuntimeError(f"_order: {order} ist keine Reihenfolge von {chosen}")
        return order

    def _plan_answer(self, start: float, inputs: _Inputs,
                     previous: _FormInstance | None) -> _Plan:
        """Die Antwort: der Denkblick läuft weiter (A0), F16, dann Zuwenden und Wegsehen.

        A0 dauert `min(2,23 s · U(0,65; 1,35); 40 % der Antwort)`; Wegsehen 1,96 s alle
        4,75 s; die letzten 1,5 s beim Betrachter, die letzte Form reicht 2 s über das
        Ende hinaus.
        Vorbedingung: Zustand Antwort mit gesetztem Ende.
        Nachbedingung: ein Plan, der mit A0 beginnt und mit A1 endet.
        Fehlerfälle: kein endliches Ende der Antwort.
        """
        # ── Eingabe-Validierung ──
        end = self._situation.answer_end
        if not math.isfinite(end):
            raise RuntimeError("_plan_answer: Antwort ohne Ende")

        # ── Verarbeitung ──
        closing = end - catalog.ANSWER_CLOSING_MS
        duration = min(2230 * self._rng.uniform(0.65, 1.35), 0.4 * (end - start))
        forms = [self._instance("A0", inputs, (start, duration), previous)]
        t = self._append(forms, "F16", inputs, (start + duration, 600.0))
        toward = True
        while t < closing:
            form_id = "A1" if toward else "A2"
            t = self._append(forms, form_id, inputs,
                             (t, (2790 if toward else 1960) * self._rng.uniform(0.65, 1.35)))
            toward = not toward
        last = forms[-1]
        if last.form_id == "A2":
            last.duration = closing - last.t0
            t = closing
            if last.duration < 400:
                forms.pop()
                t = last.t0
        if forms[-1].form_id == "A1":
            forms[-1].duration = end + 2000 - forms[-1].t0
        else:
            self._append(forms, "A1", inputs, (t, end + 2000 - t))

        # ── Ausgabe-Verifikation ──
        if forms[0].form_id != "A0" or forms[-1].form_id != "A1":
            raise RuntimeError(f"_plan_answer: {[f.form_id for f in forms]}")
        return _Plan(_PLAN_ANSWER, forms, frozenset())

    def _append(self, forms: list[_FormInstance], form_id: str, inputs: _Inputs,
                slot: tuple[float, float]) -> float:
        """Hängt eine Form an den Plan; die vorige ist die letzte im Plan. Gibt ihr Ende zurück.

        Vorbedingung: slot = (Beginn, Dauer).
        Nachbedingung: die Form steht am Ende des Plans.
        Fehlerfälle: über `_instance`.
        """
        # ── Eingabe-Validierung ──
        if len(slot) != 2:
            raise ValueError(f"_append: slot {slot!r}")

        # ── Verarbeitung ──
        forms.append(self._instance(form_id, inputs, slot, forms[-1] if forms else None))
        end = slot[0] + slot[1]

        # ── Ausgabe-Verifikation ──
        if forms[-1].form_id != form_id:
            raise RuntimeError(f"_append: {form_id} nicht angehängt")
        return end

    def _instance(self, form_id: str, inputs: _Inputs, slot: tuple[float, float],
                  previous: _FormInstance | None) -> _FormInstance:
        """Eine Form mit Seite, Blickpunkt und erster Sakkade — Ziehungen in dieser Reihenfolge.

        Vorbedingung: eine Form des Katalogs, slot = (Beginn, Dauer), endlich.
        Nachbedingung: eine geplante Form; F9 kennt den Blick der vorigen.
        Fehlerfälle: unbekannte Form, nicht endlicher Beginn oder Dauer.
        """
        # ── Eingabe-Validierung ──
        t0, duration = slot
        if form_id not in FORMS or not (math.isfinite(t0) and math.isfinite(duration)):
            raise ValueError(f"_instance: {form_id} mit ({t0}, {duration})")

        # ── Verarbeitung ──
        spec = FORMS[form_id]
        side = self._rng.coin()
        if spec.gaze == catalog.GAZE_CONTINUE:
            gaze = self._gaze_onward(previous, side, inputs)
        elif isinstance(spec.gaze, GazePoint):
            gaze = _Gaze(spec.gaze.x * side, spec.gaze.y)
        else:
            gaze = _gaze_program(spec.gaze, side, inputs, self._rng)
        inst = _FormInstance(form_id, t0, duration, side, gaze)
        # Kopf: h je Form aus der eigenen Quelle, genau eine Ziehung; „weiter“ hinter einem
        # abgewandten Blick behält auch dessen Kopfziel
        inst.head_h = self._head_rng.next()
        inst.head_inherits = (spec.gaze == catalog.GAZE_CONTINUE and previous is not None
                              and _averted(previous.gaze))
        if form_id == "F9":
            inst.previous_gaze = previous.gaze if previous is not None else _Gaze(0.2, 0.0)
        if spec.saccade_interval is not None:
            inst.next_saccade = t0 + self._rng.uniform(*spec.saccade_interval)

        # ── Ausgabe-Verifikation ──
        if not (math.isfinite(inst.gaze.x) and math.isfinite(inst.gaze.y)):
            raise RuntimeError(f"_instance: {form_id} ohne endlichen Blick")
        return inst

    def _gaze_onward(self, previous: _FormInstance | None, side: int,
                     inputs: _Inputs) -> _Gaze:
        """Der Blick der vorigen Form, wenn er abgewandt ist — sonst ein Wegsehen wie beim Sprechen.

        Vorbedingung: side −1 oder 1.
        Nachbedingung: ein Blickpunkt; ohne abgewandten vorigen Blick eine Ziehung.
        Fehlerfälle: eine Seite außer ±1.
        """
        # ── Eingabe-Validierung ──
        if side not in (-1, 1):
            raise ValueError(f"_gaze_onward: Seite {side}")

        # ── Verarbeitung ──
        if previous is not None and _averted(previous.gaze):
            pendulum = previous.form_id == "F7" and previous.pendulum
            x = previous.gaze.x2 if pendulum and previous.gaze.x2 is not None else previous.gaze.x
            gaze = _Gaze(x, previous.gaze.y)
        else:
            r = self._rng.next()
            gaze = _Gaze(0.4 * side, _speaking_y(r, inputs.avoiding))

        # ── Ausgabe-Verifikation ──
        if not (math.isfinite(gaze.x) and math.isfinite(gaze.y)):
            raise RuntimeError(f"_gaze_onward: {gaze}")
        return gaze

    # ------------------------------------------------------------ Lage

    def _inputs(self, now: float) -> _Inputs:
        """Die Lage im Augenblick: Emotion des Zustands, Basis, Energie, Valenz, Aktivität.

        Rauschen: Pixies Rückfall; Nachdenken und Antwort: Nova; Nachklang: Nova
        klingt von 0,7 auf 0,35 ihres Arousals aus und blendet in den letzten 40 % zu
        Pixie über, die Energie klingt mit aus. Die Antwort gleitet über A0 aus dem
        Gesicht vor dem ersten Laut, Basis wie Rauschen. In v1 folgen E und V der
        Emotion, die Lage im Raum steht fest.
        Vorbedingung: now endlich.
        Nachbedingung: eine Lage mit Amplitude k = (0,5 + 0,5·a) · (0,7 + 0,3·N).
        Fehlerfälle: nicht endliche Zeit.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(now):
            raise ValueError(f"_inputs: Zeit {now} nicht endlich")

        # ── Verarbeitung ──
        situation, nova, pixie = self._situation, self._nova, self._pixie
        state = situation.state
        glide = 1.0
        if state is IdleState.AFTERGLOW:
            p, mix = _afterglow_mix(situation, now)
            fade_out = 1 - catalog.AFTERGLOW_FADE_SHARE * min(1, p / catalog.AFTERGLOW_BLEND_FROM)
            nova_basis = _basis(nova.sector,
                                nova.arousal * catalog.AFTERGLOW_START_FACTOR * fade_out)
            pixie_basis = _basis(pixie.sector, pixie.arousal * catalog.BASE_FACTOR[IdleState.NOISE])
            basis = {k: nova_basis[k] + (pixie_basis[k] - nova_basis[k]) * mix for k in _KEYS}
            sector = pixie.sector if mix >= 0.5 else nova.sector
            arousal = nova.arousal + (pixie.arousal - nova.arousal) * mix
            # die Energie klingt mit aus wie die Basis: Takt, ω und Lidschlag
            energy = nova.arousal * fade_out * (1 - mix) + pixie.arousal * mix
            nova_valence = _valence(nova.sector, nova.arousal)
            sector_valence = nova_valence + (_valence(pixie.sector, pixie.arousal)
                                             - nova_valence) * mix
        else:
            source = pixie if state is IdleState.NOISE else nova
            sector, arousal = source.sector, source.arousal
            energy = arousal
            basis = _basis(sector, arousal * catalog.BASE_FACTOR[state])
            sector_valence = _valence(sector, arousal)
            if state is IdleState.ANSWER and situation.glide_basis is not None:
                # die Antwort gleitet über A0 aus dem Gesicht vor dem ersten Laut
                glide = _smoothstep((now - situation.since) / situation.glide_ms)
                start = situation.glide_basis
                basis = {k: start[k] + (basis[k] - start[k]) * glide for k in _KEYS}
        activity = {IdleState.NOISE: self._activity, IdleState.THINKING: catalog.ACTIVITY_THINKING,
                    IdleState.AFTERGLOW: catalog.ACTIVITY_AFTERGLOW,
                    IdleState.ANSWER: catalog.ACTIVITY_ANSWER}[state]
        noise = _noise_strength(situation, activity, glide)
        valence = sector_valence
        direction = catalog.SPACE_DIRECTION
        inputs = _Inputs(
            state=state, sector=sector, arousal=arousal, basis=basis, noise=noise, energy=energy,
            valence=valence, sector_valence=sector_valence, activity=activity,
            amplitude=(0.5 + 0.5 * activity) * (0.7 + 0.3 * catalog.SPACE_NEARNESS),
            anger=sector == catalog.SECTOR_ANGER,
            avoiding=valence <= -0.4 and sector != catalog.SECTOR_ANGER,
            paradox=(direction == catalog.DIRECTION_UP and valence < 0)
            or (energy >= 0.5 and direction == catalog.DIRECTION_DOWN and valence > 0),
        )

        # ── Ausgabe-Verifikation ──
        if not (0.0 <= inputs.energy <= 1.0 and 0.0 < inputs.amplitude <= 1.0):
            raise RuntimeError(f"_inputs: Energie {inputs.energy} oder k {inputs.amplitude}")
        return inputs

    # ------------------------------------------------------------ Mikroschicht

    def _saccades(self, now: float, inst: _FormInstance) -> None:
        """Kleine Sakkaden im Takt der Form; F7 pendelt statt dessen zwischen zwei Punkten.

        Vorbedingung: die laufende Form.
        Nachbedingung: die nächste Sakkade liegt nach now, sofern die Form welche hat.
        Fehlerfälle: nicht endliche Zeit.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(now):
            raise ValueError(f"_saccades: Zeit {now} nicht endlich")
        spec = FORMS[inst.form_id]
        if spec.saccade_interval is None or now < inst.next_saccade:
            return

        # ── Verarbeitung ──
        if inst.form_id == "F7":
            inst.pendulum = 1 - inst.pendulum
        else:
            jump = spec.saccade_jump
            x = self._rng.uniform(-jump, jump)
            inst.saccade = (x, self._rng.uniform(-jump, jump) * 0.6)
        inst.next_saccade = max(now, inst.next_saccade) + self._rng.uniform(
            *spec.saccade_interval)

        # ── Ausgabe-Verifikation ──
        if not inst.next_saccade > now:
            raise RuntimeError(f"_saccades: nächste Sakkade {inst.next_saccade} nicht nach {now}")

    @staticmethod
    def _blink_scale(inputs: _Inputs, form_id: str) -> float:
        """Die Lidform: länger (× 1,2) beim Abschweifen (F4) und bei Trauer.

        Vorbedingung: eine Lage und eine Form.
        Nachbedingung: 1,0 oder 1,2.
        Fehlerfälle: unbekannte Form.
        """
        # ── Eingabe-Validierung ──
        if form_id not in FORMS:
            raise ValueError(f"_blink_scale: Form {form_id!r} unbekannt")

        # ── Verarbeitung ──
        scale = 1.2 if form_id == "F4" or inputs.sector == catalog.SECTOR_SADNESS else 1.0

        # ── Ausgabe-Verifikation ──
        if scale not in (1.0, 1.2):
            raise RuntimeError(f"_blink_scale: {scale}")
        return scale

    def _blinks(self, now: float, inputs: _Inputs, inst: _FormInstance) -> None:
        """Der Prozess der Lidschläge: Serie, Poisson mit Sperrzeit, Abzug der gekoppelten.

        Gekoppelte Lidschläge (alle außer Poisson) zählen nur im laufenden Zustand, im
        Nachklang ab dem Beginn der Antwort, als Rate über diese Dauer (höchstens die
        letzte Minute, als Fenster mindestens 10 s); diese Rate wird von der
        Poisson-Rate abgezogen. Fällig in der Sperrzeit: ab ihrem Ende neu gezogen.
        Während F5 kein Poisson-Lidschlag; bei Angst manchmal eine Serie.
        Vorbedingung: Lage und laufende Form.
        Nachbedingung: Öffnung des Lids für diesen Schritt gesetzt.
        Fehlerfälle: nicht endliche Zeit.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(now):
            raise ValueError(f"_blinks: Zeit {now} nicht endlich")

        # ── Verarbeitung ──
        lid = self._lid
        lid.scale = self._blink_scale(inputs, inst.form_id)
        lid.rate = blink_rate(inputs.state, inputs.sector, inputs.energy, inst.form_id)
        lid.log = [entry for entry in lid.log if entry[0] > now - 60000]
        since = max(self._situation.blink_since, now - 60000)
        window = max(10000.0, now - since)
        coupled = sum(1 for t, is_coupled in lid.log if is_coupled and t >= since) * 60000 / window
        lid.poisson = _clamp(lid.rate - coupled, lid.rate / 4, lid.rate)
        mean = max(200.0, 60000 / lid.poisson - catalog.BLINK_REFRACTORY_MS)
        if lid.series and now >= lid.series[0][0]:
            self._blink(now, 1.0, True, lid.series.pop(0)[1])
        elif lid.blocked_until > now >= lid.next_ms:
            lid.next_ms = lid.blocked_until + self._rng.gamma3(mean)
        elif now >= lid.next_ms:
            self._poisson_blink(now, inputs, inst, mean)
        self._lid_open = self._lid_value(now)

        # ── Ausgabe-Verifikation ──
        if not 0.0 <= self._lid_open <= 1.0:
            raise RuntimeError(f"_blinks: Lid {self._lid_open} außerhalb 0..1")

    def _poisson_blink(self, now: float, inputs: _Inputs, inst: _FormInstance,
                       mean: float) -> None:
        """Ein fälliger Lidschlag des Poisson-Prozesses und der Abstand bis zum nächsten.

        Abstand: Sperrzeit + Gamma(3) mit dem Mittel `mean` — so dicht wie mit einer
        Exponentialziehung, aber ohne dicht folgende Doppelschläge.
        Vorbedingung: der nächste Lidschlag ist fällig, die Sperrzeit vorbei; mean > 0.
        Nachbedingung: der nächste liegt mindestens 0,8 s nach now.
        Fehlerfälle: eine Rate oder ein Mittel ≤ 0.
        """
        # ── Eingabe-Validierung ──
        lid = self._lid
        if not (lid.poisson > 0 and mean > 0):
            raise ValueError(f"_poisson_blink: Rate {lid.poisson}, Mittel {mean}")

        # ── Verarbeitung ──
        if inst.form_id != "F5":
            self._blink(now, 1.0, False, catalog.BLINK_POISSON)
            if inputs.sector == catalog.SECTOR_ANXIETY and self._rng.next() < 0.25:
                lid.series.append((now + self._rng.uniform(250, 400), catalog.BLINK_ANXIETY))
        lid.next_ms = now + catalog.BLINK_REFRACTORY_MS + self._rng.gamma3(mean)

        # ── Ausgabe-Verifikation ──
        if not lid.next_ms >= now + catalog.BLINK_REFRACTORY_MS:
            raise RuntimeError(f"_poisson_blink: nächster Lidschlag {lid.next_ms} zu früh")

    def _blink(self, now: float, factor: float, force: bool, kind: str) -> None:
        """Ein Lidschlag: Schließen 80–100 ms, 40 ms zu, Öffnen 150–250 ms, mal Faktor und Lidform.

        In der Sperrzeit von 0,8 s fällt er aus, außer er ist erzwungen. Läuft noch
        einer, setzt der neue an dessen Öffnung v an: sein Schließen beginnt dort,
        wo 1 − q² = v ist — sonst sähe ein Einfall kurz nach einem Lidschlag das
        Auge nie geschlossen. Gekoppelt ist jede Art außer Poisson.
        Vorbedingung: Faktor > 0, eine Art aus `BLINK_KINDS`.
        Nachbedingung: der Lidschlag läuft ab `lid.start` ≤ now, die Sperrzeit bis now + 0,8 s.
        Fehlerfälle: Faktor ≤ 0, eine unbekannte Art.
        """
        # ── Eingabe-Validierung ──
        if not factor > 0 or kind not in catalog.BLINK_KINDS:
            raise ValueError(f"_blink: Faktor {factor}, Art {kind!r}")
        lid = self._lid
        if not force and now < lid.blocked_until:
            return

        # ── Verarbeitung ──
        scale = factor * lid.scale
        v = self._lid_value(now)  # Öffnung eines laufenden Lidschlags, sonst 1
        lid.close = self._rng.uniform(80, 100) * scale
        lid.hold = catalog.BLINK_HOLD_MS * scale
        lid.open = self._rng.uniform(150, 250) * scale
        lid.start = now - math.sqrt(1 - v) * lid.close
        coupled = kind != catalog.BLINK_POISSON
        lid.blocked_until = now + catalog.BLINK_REFRACTORY_MS
        lid.log.append((now, coupled))
        if self._trace is not None:
            self._trace.blinks.append(TracedBlink(now, self._situation.state, kind, coupled,
                                                  lid.start, lid.close, lid.hold, lid.open))

        # ── Ausgabe-Verifikation ──
        if not (lid.close > 0 and lid.open > 0 and lid.start <= now):
            raise RuntimeError(f"_blink: Form ({lid.close}, {lid.open}) ab {lid.start}")

    def _end_blink(self, now: float) -> None:
        """Ende der Antwort: genau ein Lidschlag, danach die längere Sperre von 1,5 s.

        Fiel eben einer, sperrt er den am Ende, und er bleibt der eine.
        Vorbedingung: now endlich.
        Nachbedingung: gesperrt mindestens bis now + 1,5 s.
        Fehlerfälle: nicht endliche Zeit.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(now):
            raise ValueError(f"_end_blink: Zeit {now} nicht endlich")

        # ── Verarbeitung ──
        self._blink(now, 1.0, False, catalog.BLINK_END)
        lid = self._lid
        lid.blocked_until = max(lid.blocked_until, now + catalog.BLINK_REFRACTORY_END_MS)

        # ── Ausgabe-Verifikation ──
        if lid.blocked_until < now + catalog.BLINK_REFRACTORY_END_MS:
            raise RuntimeError(f"_end_blink: Sperre bis {lid.blocked_until}")

    def _blink_series(self, t: float) -> None:
        """R3: nach Denklast (F5) eine Serie aus 2–3 Lidschlägen in höchstens 1 s.

        Vorbedingung: t endlich.
        Nachbedingung: die Serie ersetzt eine noch fällige.
        Fehlerfälle: nicht endliche Zeit.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(t):
            raise ValueError(f"_blink_series: Zeit {t} nicht endlich")

        # ── Verarbeitung ──
        times = [t, t + self._rng.uniform(300, 450)]
        if self._rng.next() < 0.5:
            times.append(t + self._rng.uniform(650, 950))
        self._lid.series = [(at, catalog.BLINK_SERIES) for at in times]

        # ── Ausgabe-Verifikation ──
        if not 2 <= len(self._lid.series) <= 3:
            raise RuntimeError(f"_blink_series: {len(self._lid.series)} Lidschläge")

    def _lid_value(self, now: float) -> float:
        """Die Öffnung des Lids: quadratisch zu, geschlossen, quadratisch auf; danach offen.

        Vorbedingung: now endlich.
        Nachbedingung: ein Wert in 0..1; ein abgelaufener Lidschlag ist beendet.
        Fehlerfälle: nicht endliche Zeit.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(now):
            raise ValueError(f"_lid_value: Zeit {now} nicht endlich")

        # ── Verarbeitung ──
        lid = self._lid
        value = 1.0
        closed_until = lid.close + lid.hold
        u = now - lid.start
        if lid.start < 0:
            value = 1.0  # kein Lidschlag läuft
        elif u < lid.close:
            q = u / lid.close
            value = 1 - q * q
        elif u < closed_until:
            value = 0.0
        elif u < closed_until + lid.open:
            q = (u - closed_until) / lid.open
            value = 1 - (1 - q) * (1 - q)
        else:
            lid.start = -1.0

        # ── Ausgabe-Verifikation ──
        if not 0.0 <= value <= 1.0:
            raise RuntimeError(f"_lid_value: {value}")
        return value

    # ------------------------------------------------------------ Ziele

    def _targets(self, now: float, inputs: _Inputs, inst: _FormInstance) -> FaceState:
        """Die Ziele aller Kanäle: Basis + Abweichung · k, Blick der Form, Rauschen.

        Die Öffnung der Basis ist auf 2 begrenzt, solange keine Form sie öffnet — im
        Nachdenken öffnet keine, in der Antwort öffnet die Stimme. Der Blick ist allein
        der der Form, nicht skaliert. Das Oberlid hebt sich beim Blick nach oben; die
        Pupille folgt Basis, Form, Last und Energie.
        Vorbedingung: Lage und laufende Form.
        Nachbedingung: endliche Ziele; ω des Gesichts gesetzt.
        Fehlerfälle: ein nicht endliches Ziel.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(now) or now < inst.t0 - 1e-6:
            raise ValueError(f"_targets: Zeit {now} vor der Form ({inst.t0})")

        # ── Verarbeitung ──
        deviation = _deviation(inst, now - inst.t0)
        basis, k, answer = inputs.basis, inputs.amplitude, inputs.state is IdleState.ANSWER
        target = {key: basis[key] + deviation.dev.get(key, 0) * k for key in _KEYS}
        if answer or not deviation.opens or inputs.state is IdleState.THINKING:
            target["mo"] = (min(basis["mo"], catalog.MOUTH_OPEN_IDLE_MAX)
                            + deviation.dev.get("mo", 0) * k)
        if deviation.smooth_brow:
            for key in catalog.BROWS:
                target[key] = min(target[key], 0)
        target["gx"] = _clamp(deviation.gaze[0], -0.9, 0.9)
        target["gy"] = _clamp(deviation.gaze[1], -0.7, 0.7)
        target["lidU"] += 0.3 * max(0, target["gy"])
        target["eo"] += catalog.EYE_OPEN_GAZE_UP * max(0, -target["gy"])
        load = 0.06 * inputs.activity if inst.form_id in catalog.MOD_LOAD else 0
        target["ps"] = _clamp(basis["ps"] + deviation.pupil + load
                              + catalog.PUPIL_ENERGY * inputs.energy, 0.6, 1.3)
        state = _finish_targets(target, now, inputs)
        self._face_omega = 5 * (1 + 0.8 * inputs.energy)

        # ── Ausgabe-Verifikation ──
        if not math.isfinite(self._face_omega):
            raise RuntimeError(f"_targets: ω {self._face_omega} in {inst.form_id}")
        return state

    def _trace_mouth(self, inputs: _Inputs, targets: FaceState) -> None:
        """Vermerkt die größte Mundöffnung der laufenden Form im Verlauf, außer in der Antwort.

        Vorbedingung: Ziele dieses Schritts.
        Nachbedingung: die größte Öffnung der letzten Form ist nicht kleiner als diese.
        Fehlerfälle: nicht endliche Öffnung.
        """
        # ── Eingabe-Validierung ──
        if not math.isfinite(targets.mouth_open):
            raise ValueError(f"_trace_mouth: Öffnung {targets.mouth_open}")
        if self._trace is None or not self._trace.forms or inputs.state is IdleState.ANSWER:
            return

        # ── Verarbeitung ──
        form = self._trace.forms[-1]
        form.mouth_open_max = max(form.mouth_open_max, targets.mouth_open)

        # ── Ausgabe-Verifikation ──
        if form.mouth_open_max < targets.mouth_open:
            raise RuntimeError("_trace_mouth: größte Öffnung nicht nachgeführt")
