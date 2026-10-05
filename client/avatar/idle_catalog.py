"""Katalog des Leerlaufs: Formen, Gewichte, Regelmengen und Konstanten als Daten.

Der Leerlauf (`avatar.idle`) plant aus diesem Katalog, was das Gesicht zwischen
zwei Antworten tut: Rauschen, Nachdenken, Antwort und Nachklang. Die Werte folgen
dem Referenzgenerator; die Gleichheit prüfen die Referenzwerte unter
`tests/avatar_reference/idle.json`.

Die Formen tragen ihre Kennung (F1–F17, E1, A0–A2): `deviation` ist die
Abweichung je Gesichtskanal zur Emotionsbasis bei voller Stärke (Kurznamen wie im
Prototyp, Brauen positiv = tiefer), `gaze` der Blickpunkt oder der Name eines
Blickprogramms, `nominal` der Blickpunkt, mit dem die Regeln der Abfolge rechnen.

Alles hier ist unveränderlich: `MappingProxyType`, `frozenset`, Tupel.
"""

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType


class IdleState(str, Enum):
    """Die vier Zustände des Leerlaufs; der Wert ist der Name in der Referenz."""

    NOISE = "rauschen"
    THINKING = "nachdenken"
    ANSWER = "antwort"
    AFTERGLOW = "nachklang"


@dataclass(frozen=True)
class GazePoint:
    """Ein Blickpunkt: x zur Seite (Vorzeichen = Seite), y nach unten positiv."""

    x: float
    y: float


# Blickprogramme: Formen, deren Blickpunkt erst beim Planen gezogen wird.
GAZE_RECALL = "recall"  # Erinnern: oben, unten oder seitlich
GAZE_BLANK = "blank"  # ins Leere
GAZE_BLANK_UP = "blank_up"  # ins Leere, oben
GAZE_PENDULUM = "pendulum"  # Abwägen zwischen zwei Punkten
GAZE_INSIGHT = "insight"  # Einfall: weg, dann zurück zum Betrachter
GAZE_CONTINUE = "continue"  # der Blick der vorigen Form, wenn er abgewandt ist
GAZE_SPEAKING = "speaking"  # Wegsehen beim Sprechen

GAZE_PROGRAMS = frozenset({
    GAZE_RECALL, GAZE_BLANK, GAZE_BLANK_UP, GAZE_PENDULUM, GAZE_INSIGHT, GAZE_CONTINUE,
    GAZE_SPEAKING,
})


@dataclass(frozen=True)
class FormSpec:
    """Eine Form des Leerlaufs.

    `saccade_interval` ist der Abstand der kleinen Sakkaden in ms (None = fester
    Blick), `saccade_jump` ihre Weite. `pupil` wirkt auf die Pupille, ohne mit der
    Amplitude zu skalieren. `asymmetric`: die Seite des Gesichts wird mit der
    Blickseite gespiegelt. `opens`: die Form hebt die Grenze der Mundöffnung auf.
    `accent`: F16 als Akzent am Schluss eines Zyklus.
    """

    form_id: str
    name: str
    deviation: Mapping[str, float]
    gaze: GazePoint | str
    nominal: GazePoint
    saccade_interval: tuple[float, float] | None
    saccade_jump: float
    pupil: float
    asymmetric: bool
    opens: bool
    accent: bool


def _form(
    form_id: str, name: str, deviation: dict, gaze: GazePoint | str, **extra: object
) -> FormSpec:
    """Baut eine Form; `nominal` folgt dem festen Blickpunkt oder wird mitgegeben.

    Vorbedingung: `gaze` ist ein Blickpunkt oder ein Name aus `GAZE_PROGRAMS`;
    `extra` nennt nur Felder von `FormSpec`.
    Nachbedingung: eine unveränderliche Form mit endlichen Abweichungen.
    Fehlerfälle: unbekanntes Blickprogramm, unbekanntes Feld, nicht endlicher Wert.
    """
    # ── Eingabe-Validierung ──
    if isinstance(gaze, str) and gaze not in GAZE_PROGRAMS:
        raise ValueError(f"Form {form_id}: unbekanntes Blickprogramm {gaze!r}")
    allowed = {"nominal", "saccade_interval", "saccade_jump", "pupil", "asymmetric", "opens",
               "accent"}
    unknown = set(extra) - allowed
    if unknown:
        raise ValueError(f"Form {form_id}: unbekannte Felder {sorted(unknown)}")

    # ── Verarbeitung ──
    fixed = gaze if isinstance(gaze, GazePoint) else GazePoint(0.0, 0.0)
    spec = FormSpec(
        form_id=form_id,
        name=name,
        deviation=MappingProxyType(dict(deviation)),
        gaze=gaze,
        nominal=extra.get("nominal", fixed),
        saccade_interval=extra.get("saccade_interval"),
        saccade_jump=float(extra.get("saccade_jump", 0.0)),
        pupil=float(extra.get("pupil", 0.0)),
        asymmetric=bool(extra.get("asymmetric", False)),
        opens=bool(extra.get("opens", False)),
        accent=bool(extra.get("accent", False)),
    )

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for v in spec.deviation.values()):
        raise ValueError(f"Form {form_id}: Abweichung mit nicht endlichem Wert")
    if not isinstance(spec.nominal, GazePoint):
        raise TypeError(f"Form {form_id}: nominal ist kein GazePoint")
    return spec


_P = GazePoint

FORMS: Mapping[str, FormSpec] = MappingProxyType({f.form_id: f for f in (
    _form("F1", "Konzentration",
          {"bli": 8, "bri": 8, "blo": 3, "bro": 3, "eo": -0.12, "arc": 0.25, "au23": 0.2},
          _P(0.25, 0.15), saccade_interval=(1500, 3000), saccade_jump=0.05),
    _form("F2", "Erinnern", {"bli": -3, "bri": -3, "blo": -3, "bro": -3, "eo": 0.03},
          GAZE_RECALL, nominal=_P(0.5, 0), saccade_interval=(800, 1200), saccade_jump=0.12),
    _form("F3", "Vorstellen", {}, _P(0.35, -0.2), pupil=0.05, saccade_interval=(500, 900),
          saccade_jump=0.15),
    _form("F4", "Ins Leere", {"lidU": 0.2, "eo": -0.06}, GAZE_BLANK, pupil=-0.05,
          nominal=_P(0.2, 0.05), saccade_interval=(3000, 7000), saccade_jump=0.1),
    # Fester Blick ins Leere, seitlich unten — geradeaus las er sich als Blickkontakt.
    # 0,3 liegt deutlich außerhalb des Kastens um den Betrachter (|x| ≤ 0,12, |y| ≤ 0,15).
    _form("F5", "Denklast", {"bli": 3, "bri": 3, "blo": 3, "bro": 3}, _P(0.3, 0.3), pupil=0.12),
    _form("F6", "Verwirrung",
          {"bli": 5, "bri": -2, "blo": 2, "bro": 2, "eo": -0.08, "arc": 0.15, "ma": 3},
          _P(0.2, 0), asymmetric=True, saccade_interval=(1500, 2500), saccade_jump=0.08),
    _form("F7", "Unsicherheit",
          {"au24": 0.25, "au20L": 0.2, "au15L": 0.15, "au15R": 0.15, "mc": -3, "eo": -0.08,
           "arc": 0.15},
          GAZE_PENDULUM, asymmetric=True, nominal=_P(0.28, 0.05), saccade_interval=(900, 1400)),
    _form("F8", "Skepsis", {"bro": -8, "bli": 2, "bri": 2, "ma": 4, "au12R": 0.1}, _P(0.2, 0),
          asymmetric=True, saccade_interval=(2000, 3000), saccade_jump=0.05),
    _form("F9", "Einfall", {"mc": 6, "arc": 0.15}, GAZE_INSIGHT, opens=True, nominal=_P(0, 0)),
    _form("F10", "Sorge",
          {"bli": -6, "bri": -6, "blo": 4, "bro": 4, "au15L": 0.2, "au15R": 0.2, "mc": -3,
           "lidU": 0.15},
          _P(0.3, 0.4), saccade_interval=(2000, 4000), saccade_jump=0.06),
    _form("F11", "Formulieren", {"au18": 0.1}, _P(0.3, 0.1), saccade_interval=(2000, 4000),
          saccade_jump=0.05),
    _form("F12", "Nachsinnen", {"mc": 8, "arc": 0.2, "au12L": 0.15, "au12R": 0.15},
          GAZE_BLANK_UP, nominal=_P(0.17, -0.1), saccade_interval=(3000, 5000),
          saccade_jump=0.08),
    _form("F13", "Kinn hoch", {"au17": 0.3, "au23": 0.25, "bli": -3, "bri": -3}, _P(0.2, 0.45),
          saccade_interval=(2000, 4000), saccade_jump=0.05),
    # „Leicht offen": +4 über der begrenzten Basis, ohne die Grenze aufzuheben — sonst
    # öffnete er unter Freude auf die volle Öffnung der Emotion und läse sich als Staunen.
    _form("F14", "Mund offen", {"mo": 4, "eo": -0.03}, _P(0.3, 0.05),
          saccade_interval=(3000, 6000), saccade_jump=0.06),
    _form("F15", "Lächeln kontrolliert", {"mc": 6, "au12L": 0.2, "au12R": 0.2, "au24": 0.3},
          _P(0.3, 0.3), saccade_interval=(2000, 3000), saccade_jump=0.05),
    _form("F16", "Blick zum Betrachter", {"eo": 0.03}, _P(0, 0), accent=True),
    _form("F17", "Fixieren", {"eo": -0.1, "bli": 6, "bri": 6, "au24": 0.2}, _P(0.15, 0)),
    # Ende des Nachdenkens: Einatmen mit leicht geöffnetem Mund vor dem ersten Laut, die
    # Augen etwas weiter — mehrere kleine Zeichen statt eines großen (mo 10,5 · k ≈ 7,6).
    _form("E1", "Einatmen", {"mo": 10.5, "eo": 0.05}, GAZE_CONTINUE),
    # Antwort: keine Denkformen, sondern die Blickregelung des Sprechers.
    _form("A0", "Wegsehen fortgesetzt (spricht)", {}, GAZE_CONTINUE),
    _form("A1", "Zuwenden (spricht)", {}, _P(0, 0), saccade_interval=(1500, 2500),
          saccade_jump=0.04),
    _form("A2", "Wegsehen beim Sprechen", {}, GAZE_SPEAKING, nominal=_P(0.4, 0)),
)})

# Die Formen, die ein Zyklus ziehen kann, in der Reihenfolge der Ziehung.
DRAWABLE: tuple[str, ...] = (
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14",
    "F15", "F17",
)

# Grundgewichte je Sektor; Spalten Neutral, Freude, Zuversicht, Angst, Überraschung,
# Trauer, Enttäuschung, Ärger, Neugier.
BASE_WEIGHTS: Mapping[str, tuple[float, ...]] = MappingProxyType({
    "F1": (2, 1, 1, 2, 1, 1, 2, 3, 2), "F2": (3, 2, 2, 1, 2, 2, 2, 1, 3),
    "F3": (2, 3, 2, 1, 2, 1, 1, 0, 3), "F4": (2, 1, 3, 1, 1, 3, 2, 0, 1),
    "F5": (1, 1, 1, 2, 1, 0, 1, 2, 2), "F6": (1, 0, 0, 1, 3, 0, 2, 1, 2),
    "F7": (1, 0, 0, 3, 1, 1, 3, 2, 1), "F8": (1, 1, 0, 0, 2, 0, 2, 1, 2),
    "F9": (1, 3, 2, 0, 2, 0, 0, 0, 3), "F10": (1, 0, 0, 3, 0, 3, 2, 0, 0),
    "F11": (1, 1, 1, 1, 0, 1, 1, 1, 1), "F12": (1, 3, 3, 0, 1, 0, 0, 0, 1),
    "F13": (1, 0, 1, 1, 0, 2, 3, 2, 0), "F14": (1, 1, 1, 1, 3, 0, 0, 0, 2),
    "F15": (0, 1, 1, 1, 0, 1, 0, 0, 0), "F17": (0, 0, 0, 1, 0, 0, 1, 3, 1),
})

# Die Gruppe je Zustand: Faktor auf das Grundgewicht, 0 = gehört nicht dazu.
# Rauschen breit, leicht zu inneren, weiten Formen geneigt; Nachdenken Anstrengung,
# Prüfen und Formulieren, kein Abschweifen (F4), kein offener Mund (F14); Nachklang
# Nachsinnen, ins Leere, gebremstes Lächeln, keine Last, kein Einfall.
GROUP_FACTORS: Mapping[IdleState, Mapping[str, float]] = MappingProxyType({
    IdleState.NOISE: MappingProxyType({
        "F1": 0.8, "F2": 1, "F3": 1.2, "F4": 1.2, "F5": 0.8, "F6": 0.8, "F7": 0.8, "F8": 0.8,
        "F9": 1, "F10": 1, "F11": 0.5, "F12": 1.2, "F13": 1, "F14": 1.1, "F15": 1, "F17": 0.7,
    }),
    IdleState.THINKING: MappingProxyType({
        "F1": 1.3, "F2": 1, "F3": 0.6, "F4": 0, "F5": 1.3, "F6": 1, "F7": 1, "F8": 0.8,
        "F9": 1.2, "F10": 0.6, "F11": 1.5, "F12": 0.4, "F13": 1, "F14": 0, "F15": 0.5,
        "F17": 1,
    }),
    IdleState.AFTERGLOW: MappingProxyType({
        "F1": 0.3, "F2": 0.8, "F3": 0.6, "F4": 1.2, "F5": 0, "F6": 0, "F7": 0.5, "F8": 0,
        "F9": 0, "F10": 0.8, "F11": 0, "F12": 1.4, "F13": 0.8, "F14": 0.5, "F15": 1,
        "F17": 0.3,
    }),
})

# Modifikatoren, multiplikativ; die Reihenfolge der Anwendung steht in `avatar.idle`.
MOD_DEEP = frozenset({"F1", "F2", "F3", "F5", "F11"})  # Tiefe ↑
MOD_LIGHT = frozenset({"F4", "F8", "F12", "F14"})  # Tiefe ↓
MOD_LIVELY = frozenset({"F2", "F3", "F6", "F8", "F9"})  # Energie ↑
MOD_CALM = frozenset({"F4", "F10", "F12", "F13"})  # Energie ↓
MOD_LOAD = frozenset({"F1", "F2", "F3", "F5"})  # Aktivität ↑; auch Pupille unter Last
MOD_DRIFT = frozenset({"F4", "F12"})  # Aktivität ↓
MOD_PRIVATE = frozenset({"F4", "F12", "F14"})  # Nähe ↑
MOD_CONTROLLED = frozenset({"F1", "F11", "F17"})  # Nähe ↓

# Die Mengen der Abfolgeregeln.
ASYMMETRIC = frozenset({"F6", "F7", "F8"})  # R4: höchstens zwei
PRECURSORS = frozenset({"F1", "F2", "F3", "F5", "F6", "F7"})  # R2: F9 nur nach diesen
DOWNWARD = frozenset({"F4", "F10", "F13"})  # R7: Schluss abwärts
POSITIVE = frozenset({"F3", "F9", "F12"})  # Familie, die eine positive Valenz hebt
NEGATIVE = frozenset({"F7", "F10", "F13"})  # Familie, die eine negative Valenz hebt
OPENERS = frozenset({"F1", "F2", "F3", "F4", "F10", "F13"})  # R1: Eröffnung mit Blickwechsel
OPENERS_ANGER = OPENERS | {"F17"}  # bei Ärger eröffnet auch das Fixieren

# Valenz je Sektor (moderat, intensiv); der Begriff wechselt bei MOD_AROUSAL.
VALENCE: tuple[tuple[float, float], ...] = (
    (0, 0), (0.8, 1), (0.6, 0.75), (-0.55, -0.7), (0.05, 0.1), (-0.8, -1), (-0.65, -0.75),
    (-0.7, -0.9), (0.35, 0.5),
)
# Δ_S der Spanne je Sektor.
DELTA_S: tuple[float, ...] = (0, 0, 0.5, -0.6, -0.5, 1.5, 0.8, -0.6, -0.3)
SECTOR_ANXIETY = 3
SECTOR_SADNESS = 5
SECTOR_ANGER = 7

# Name der Emotion -> Sektor (0 = neutral), je Sektor das `hi` und das `lo` der
# Schlüsselbilder des Prototyps.
SECTOR_BY_NAME: Mapping[str, int] = MappingProxyType({
    "neutral": 0,
    "begeisterung": 1, "freude": 1,
    "dankbarkeit": 2, "zufriedenheit": 2,
    "stress": 3, "unsicherheit": 3,
    "ueberrascht": 4, "verwundert": 4,
    "verzweiflung": 5, "traurigkeit": 5,
    "frustration": 6, "enttaeuschung": 6,
    "wut": 7, "aerger": 7,
    "hoffnung": 8, "neugierig": 8,
})

# Grundlage der Emotion je Zustand: face_target(Sektor, Arousal · Faktor). In der
# Antwort 0,75 — mit 1 las sich Freude 0,5 beim Sprechen als Grinsen mit Zähnen. Der
# Nachklang klingt von 0,7 auf 0,35 aus (Faktor 1 − 0,5 · Anteil) und blendet dann zu
# Pixie über; die Energie klingt mit aus.
BASE_FACTOR: Mapping[IdleState, float] = MappingProxyType({
    IdleState.NOISE: 0.5, IdleState.THINKING: 0.5, IdleState.ANSWER: 0.75,
})
AFTERGLOW_START_FACTOR = 0.7
AFTERGLOW_FADE_SHARE = 0.5  # 0,7 · (1 − 0,5) = 0,35 am Ende des Ausklingens
AFTERGLOW_BLEND_FROM = 0.6  # Anteil der Dauer, ab dem zu Pixie überblendet wird

# Aktivität a je Zustand: Rauschen 0,6 mit laufendem Auftrag, sonst 0,2; im Turn
# feste Last, im Nachklang Ruhe. In der Antwort 0,25: leises Rauschen statt eines
# eingefrorenen Gesichts, nur auf Brauen und Mundwinkeln (NOISE_IN_ANSWER).
ACTIVITY_THINKING = 0.7
ACTIVITY_AFTERGLOW = 0.2
ACTIVITY_JOB = 0.6
ACTIVITY_IDLE = 0.2
ACTIVITY_ANSWER = 0.25

# Einfall F9 im Nachdenken ist ein Akzent: Phase a und b 1,0 s, dann Lächeln und Blick
# zurück 1,0–2,0 s — Dauer F9_THINKING_MS[0] + U(F9_THINKING_MS[1], F9_THINKING_MS[2]).
# Im Rauschen behält F9 die Spanne.
F9_THINKING_MS: tuple[float, float, float] = (1000.0, 1000.0, 2000.0)
# F9 sieht in Phase a und b mindestens so weit zur Seite.
F9_AWAY_MIN = 0.2

# R7 im Nachdenken: F16 mit halber Wahrscheinlichkeit und kurz.
ACCENT_THINKING_SHARE = 0.5
ACCENT_THINKING_MS: tuple[float, float] = (1000.0, 1500.0)
ACCENT_MS: tuple[float, float] = (1000.0, 2000.0)

# Erregung weitet die Pupille: + 0,12·E auf den Radius, mit E ungedämpft.
PUPIL_ENERGY = 0.12
# Das Oberlid hebt sich beim Blick nach oben: + 0,08 auf eo je Einheit −gy.
EYE_OPEN_GAZE_UP = 0.08

# Faktor der Spanne je Zustand; Nachdenken konvergent = wenige, längere Formen.
SPAN_FACTOR: Mapping[IdleState, float] = MappingProxyType({
    IdleState.NOISE: 1.0, IdleState.THINKING: 1.3, IdleState.AFTERGLOW: 1.3,
    IdleState.ANSWER: 1.0,
})
SPAN_MIN_S = 1.5
SPAN_MAX_S = 10.0

# Grundrate der Lidschläge je Minute, dazu + 12·E; Angst +6, Trauer −2, F4 +3,
# begrenzt auf 8–32.
BLINK_BASE_RATE: Mapping[IdleState, float] = MappingProxyType({
    IdleState.NOISE: 15.0, IdleState.THINKING: 12.0, IdleState.ANSWER: 20.0,
    IdleState.AFTERGLOW: 15.0,
})
BLINK_ENERGY_RATE = 12.0
BLINK_RATE_MIN = 8.0
BLINK_RATE_MAX = 32.0
BLINK_REFRACTORY_MS = 800.0
# Nach dem langen Lidschlag des Einfalls deckt die Sperre Phase a und b; nach dem am
# Ende der Antwort den Blick zum Gegenüber (F16) bis zu seinem frühesten Ende.
BLINK_REFRACTORY_INSIGHT_MS = 1000.0
BLINK_REFRACTORY_END_MS = 1500.0
# Geschlossene Phase zwischen Schließen und Öffnen, × Lidform: Das geschlossene Auge
# erscheint in mindestens einem Bild.
BLINK_HOLD_MS = 40.0
BLINK_FIRST_MS = 1200.0  # der erste Lidschlag nach dem Start
# Art eines Lidschlags; gekoppelt ist jeder außer dem aus dem Poisson-Prozess.
BLINK_POISSON = "poisson"
BLINK_GAZE_SHIFT = "r8"
BLINK_INSIGHT = "f9"
BLINK_SERIES = "f5"
BLINK_ANXIETY = "angst"
BLINK_END = "ende"
BLINK_KINDS = frozenset({BLINK_POISSON, BLINK_GAZE_SHIFT, BLINK_INSIGHT, BLINK_SERIES,
                         BLINK_ANXIETY, BLINK_END})
# Wahrscheinlichkeit eines Lidschlags am Blickwechsel über 0,4; im Nachdenken
# seltener, Konzentration senkt die Rate.
BLINK_AT_GAZE_SHIFT = 0.7
BLINK_AT_GAZE_SHIFT_THINKING = 0.3
GAZE_SHIFT_FOR_BLINK = 0.4

# Einatmen vor dem ersten Laut, Wächter des Nachdenkens, Nachlauf der Antwort.
INHALE_MS: tuple[float, float] = (700.0, 900.0)
WATCHDOG_MS = 600000.0
PLAYBACK_TAIL_MS = 400.0
ANSWER_CLOSING_MS = 1500.0  # die letzten 1,5 s der Antwort beim Betrachter

# Nachklang: (6 + 24·N) s · U(0,8; 1,2), begrenzt auf 5–60 s.
AFTERGLOW_BASE_MS = 6000.0
AFTERGLOW_NEAR_MS = 24000.0
AFTERGLOW_LIMITS_MS: tuple[float, float] = (5000.0, 60000.0)

# Die Lage im Raum in v1: Tiefe und Nähe fest, Richtung offen (Kaltstart des Raums).
DIRECTION_UP = "up"
DIRECTION_OPEN = "open"
DIRECTION_DOWN = "down"
SPACE_DEPTH = 0.3
SPACE_NEARNESS = 0.5
SPACE_DIRECTION = DIRECTION_OPEN

# Pixies Aufträge: zwei Spuren; die Art (geschlossene Menge des Servers) gewichtet
# das Rauschen, jede andere Art gewichtet nicht.
TRACKS: tuple[str, ...] = ("llm", "cpu")
PHASE_BEGIN = "beginn"
PHASE_END = "ende"
WEIGHTING_RESEARCH = "research"
WEIGHTING_REFLECTION = "reflection"
WEIGHTING_KNOWLEDGE_GAP = "knowledge_gap"
JOB_WEIGHTING: Mapping[str, str] = MappingProxyType({
    "recherche": WEIGHTING_RESEARCH,
    "vertiefen": WEIGHTING_RESEARCH,
    "wissen_verweis": WEIGHTING_RESEARCH,
    "wissen_rueckweg": WEIGHTING_RESEARCH,
    "nachfragen": WEIGHTING_REFLECTION,
})
JOB_WEIGHT_BOOST = 1.5

# Abschweifen ohne Färbung (Neutral, kaum Aktivität): Tagtraum-Verteilung.
DAYDREAM_ACTIVITY = 0.15
DAYDREAM_GROUPS: tuple[tuple[tuple[str, ...], float], ...] = (
    (("F12", "F3"), 0.425), (("F10", "F7"), 0.265), (("F2", "F4"), 0.31),
)
REPEAT_DAMPING = 0.5  # Wiederholung über Zyklen gedämpft

# Glattes Rauschen auf Brauen und Mund, Stärke ∝ a; die Reihenfolge bestimmt die
# Phase je Kanal.
NOISE_AMPLITUDES: tuple[tuple[str, float], ...] = (
    ("bli", 4), ("bri", 4), ("blo", 2), ("bro", 2), ("ma", 3), ("mc", 3), ("au23", 0.15),
    ("au18", 0.1),
)
# In der Antwort rauscht es nur auf Brauen und Mundwinkeln; die Lippen gehören der Stimme.
NOISE_IN_ANSWER = frozenset({"bli", "bri", "blo", "bro", "mc"})

# Kopfdrehung (Gierwinkel in Grad, plus = nach rechts aus Sicht des Betrachters wie gx).
# Der Kopf folgt dem Blick der Form 200 ms später, meist wenig, nachdenklich zur Seite
# etwa 10°; zum Betrachter zurück nach 150 ms. h je Form aus einer eigenen Zufallsquelle.
HEAD_PER_GAZE = 10.0  # Grad je Einheit gx ('klein', höchstens 5°)
HEAD_DEEP = 10.0  # nachdenklich zur Seite ('tief', 9–11°)
HEAD_SIDE = 0.12  # bis hier gilt der Blick als beim Betrachter
HEAD_SIDE_DEEP = 0.25  # erst deutlich seitlich dreht der Kopf tief mit
# F7 pendelt — tief wäre ein Kopfschütteln; der Weg von F9 dauert nur 1 s.
HEAD_DEEP_FORMS = frozenset(DRAWABLE) - {"F7", "F9"}
HEAD_FOLLOWS_MS = 200.0
HEAD_RETURN_MS = 150.0
HEAD_WANDER = 1.0  # Grad, glattes Rauschen wie auf Brauen und Mund
HEAD_WANDER_CHANNEL = 11  # Phase des Rauschens
YAW_MAX = 15.0  # harte Grenze des Ziels, Grad
HEAD_SMALL = "klein"
HEAD_DEEP_KIND = "tief"
HEAD_BACK = "zurueck"

# Die Mundmuskeln nach FACS, begrenzt auf 0..1.
MOUTH_AU: tuple[str, ...] = (
    "au10L", "au10R", "au12L", "au12R", "au15L", "au15R", "au16L", "au16R", "au20L", "au20R",
    "au17", "au18", "au22", "au23", "au24", "au28",
)
BROWS: tuple[str, ...] = ("bli", "bri", "blo", "bro")
BROW_MIRROR: Mapping[str, str] = MappingProxyType({
    "bli": "bri", "bri": "bli", "blo": "bro", "bro": "blo",
})
MOUTH_OPEN_IDLE_MAX = 2.0  # Öffnung der Basis im Leerlauf, sonst liest es sich als Sprechen


def _check_catalog() -> None:
    """Prüft den Katalog beim Laden: jede genannte Form ist beschrieben und gewichtet.

    Vorbedingung: die Tabellen oben sind gebaut.
    Nachbedingung: jede ziehbare Form hat neun Grundgewichte und steht in jeder
    Gruppe; jede Gruppe nennt nur ziehbare Formen; jede Regelmenge nennt nur Formen
    des Katalogs.
    Fehlerfälle: eine Lücke oder ein fremder Name — der Import scheitert laut.
    """
    # ── Eingabe-Validierung ──
    if not DRAWABLE or not FORMS:
        raise RuntimeError("Leerlauf-Katalog: keine Formen")

    # ── Verarbeitung ──
    problems = [f"{f}: ohne Beschreibung" for f in DRAWABLE if f not in FORMS]
    problems += [f"{f}: Grundgewichte fehlen oder unvollständig" for f in DRAWABLE
                 if len(BASE_WEIGHTS.get(f, ())) != len(VALENCE)]
    for state, group in GROUP_FACTORS.items():
        problems += [f"{state.value}: {f} fehlt" for f in DRAWABLE if f not in group]
        problems += [f"{state.value}: {f} nicht ziehbar" for f in group if f not in DRAWABLE]
    named = (MOD_DEEP | MOD_LIGHT | MOD_LIVELY | MOD_CALM | MOD_LOAD | MOD_DRIFT | MOD_PRIVATE
             | MOD_CONTROLLED | ASYMMETRIC | PRECURSORS | DOWNWARD | POSITIVE | NEGATIVE
             | OPENERS_ANGER | HEAD_DEEP_FORMS)
    problems += [f"{f}: in einer Regelmenge, nicht im Katalog" for f in named if f not in FORMS]
    problems += [f"{k}: Rauschen der Antwort ohne Amplitude" for k in NOISE_IN_ANSWER
                 if k not in dict(NOISE_AMPLITUDES)]

    # ── Ausgabe-Verifikation ──
    if problems:
        raise RuntimeError(f"Leerlauf-Katalog unvollständig: {sorted(problems)}")


_check_catalog()
