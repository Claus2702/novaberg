"""Ausdruck: das Ziel des Gesichts aus Sektor und Arousal.

Der einzige Teil des Avatars, der Emotionen kennt. Je Sektor zwei Schlüsselbilder:
`intense` gilt bei Arousal 1,0, `moderate` bei Arousal `MOD_AROUSAL` und nennt nur
die Kanäle, deren Form sich zwischen moderat und intensiv ändert; fehlende Kanäle
liegen linear zwischen Neutral und `intense`. Dazwischen wird stückweise linear
interpoliert: Neutral -> moderat -> intensiv.

Werte, Reihenfolge der Rechnung und der Vorgabewert des Kiefers folgen dem
Prototyp; die Gleichheit prüfen Referenzwerte unter `tests/avatar_reference/`.
Die Kopfdrehung (Kanal `yaw` des Prototyps) setzt keine Emotion: Sie ist kein Feld
des Ausdrucks, sondern ein eigener Wert des Leerlaufs (`IdleFrame.head_yaw`).
"""

import logging
import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from avatar.face import NEUTRAL, PROTOTYPE_KEYS, FaceState

logger = logging.getLogger(__name__)

MOD_AROUSAL = 0.6
# Kiefer folgt der Lippenöffnung, wenn ein Schlüsselbild kein `jaw` vorgibt.
JAW_FACTOR_DEFAULT = 0.75

_NEUTRAL_BY_KEY: Mapping[str, float] = MappingProxyType(
    {key: getattr(NEUTRAL, field) for field, key in PROTOTYPE_KEYS.items()}
)


@dataclass(frozen=True)
class SectorKeyframes:
    """Die zwei Schlüsselbilder eines Sektors, Kanäle unter ihrem Kurznamen."""

    index: int
    name: str
    intense: Mapping[str, float]
    moderate: Mapping[str, float]


def _keyframes(
    index: int, name: str, intense: dict, moderate: dict | None = None
) -> SectorKeyframes:
    """Baut die Schlüsselbilder eines Sektors und ergänzt den Kiefer wie der Prototyp.

    Gibt `intense` kein `jaw` vor, folgt es `mo` mit `JAW_FACTOR_DEFAULT` (ohne `mo`
    also 0). Bei `moderate` nur dann, wenn es `mo` nennt — sonst liegt der Kiefer
    dort linear zwischen Neutral und `intense` wie jeder fehlende Kanal.
    """
    # ── Eingabe-Validierung ──
    moderate = dict(moderate or {})
    unknown = (set(intense) | set(moderate)) - set(_NEUTRAL_BY_KEY)
    if unknown:
        raise ValueError(f"Sektor {name}: unbekannte Kanäle {sorted(unknown)}")

    # ── Verarbeitung ──
    intense = dict(intense)
    if "jaw" not in intense:
        intense["jaw"] = intense.get("mo", 0) * JAW_FACTOR_DEFAULT
    if "mo" in moderate and "jaw" not in moderate:
        moderate["jaw"] = moderate["mo"] * JAW_FACTOR_DEFAULT

    # ── Ausgabe-Verifikation ──
    result = SectorKeyframes(index, name, MappingProxyType(intense), MappingProxyType(moderate))
    if not all(math.isfinite(v) for v in (*intense.values(), *moderate.values())):
        raise ValueError(f"Sektor {name}: Schlüsselbild mit nicht endlichem Wert")
    return result


# Mundmaße nach Messung an drei Personen; Schlüsselbilder wie im Prototyp.
SECTORS: tuple[SectorKeyframes, ...] = (
    _keyframes(0, "Neutral", {}),
    # Moderate Freude lächelt ohne Zähne (AU25 nur bei hoher Erregung): Campos 2013,
    # Ambadar 2009, 05.10.2026.
    _keyframes(1, "Freude", {
        "bli": -6, "blo": -6, "bri": -6, "bro": -6, "eo": 0.68, "arc": 0.9,
        "mc": 40, "mo": 32, "mw": 110, "blush": 1,
    }, {"mo": 6, "jaw": 2}),
    # Leicht gepresste Lippen (AU24): Campos 2013, 05.10.2026.
    _keyframes(2, "Zuversicht", {
        "bli": -2, "blo": -2, "bri": -2, "bro": -2, "eo": 0.85, "arc": 0.45, "lidU": 0.25,
        "mc": 16, "mo": 3, "mw": 89, "au24": 0.2,
    }),
    # Angst und Überraschung ohne eigene Pupille: Erregung weitet sie, das rechnet der
    # Leerlauf aus dem Arousal (idle_catalog.PUPIL_ENERGY).
    # Außenbrauen heben sich mit (AU2), Unterlid spannt sich (AU7): Kohler 2008,
    # Cordaro 2018, 05.10.2026.
    _keyframes(3, "Angst", {
        "bli": -20, "blo": -6, "bri": -20, "bro": -6, "barch": 5, "eo": 1.12, "arc": 0.15,
        "mc": -6, "mo": 22, "jaw": 6, "mw": 80, "au20L": 0.7, "au20R": 0.7, "sweat": 1,
    }),
    _keyframes(4, "Überraschung", {
        "bli": -30, "blo": -28, "bri": -30, "bro": -28, "barch": -7, "eo": 1.215,
        "mc": 0, "mo": 23, "mw": 73,
    }),
    _keyframes(5, "Trauer", {
        "bli": -26, "blo": 12, "bri": -26, "bro": 12, "eo": 0.7, "gy": 0.5, "lidU": 0.4,
        "mc": -20, "mo": 28, "mw": 96, "au15L": 0.7, "au15R": 0.7, "au17": 0.4, "tear": 1,
    }, {
        "bli": -20, "blo": 9, "bri": -20, "bro": 9, "mc": -14, "mo": 0, "mw": 84,
        "au15L": 0.5, "au15R": 0.5, "au17": 0.45, "tear": 0,
    }),
    _keyframes(6, "Enttäuschung", {
        "bli": 8, "blo": 8, "bri": 8, "bro": 8, "eo": 0.68, "lidU": 0.6, "gx": -0.5, "gy": 0.6,
        "mc": -12, "mo": 12, "jaw": 0, "mw": 84, "ma": 5,
        "au10L": 0.5, "au10R": 0.35, "au15L": 0.3, "au15R": 0.3,
    }, {
        "mo": 0, "mw": 80, "au10L": 0.25, "au10R": 0.15,
    }),
    _keyframes(7, "Ärger", {
        "bli": 28, "blo": -12, "bri": 28, "bro": -12, "eo": 0.8, "arc": 0.35,
        "mc": -10, "mo": 70, "mw": 76,
    }, {
        "bli": 24, "blo": -10, "bri": 24, "bro": -10, "mc": -10, "mo": 0, "mw": 68,
        "au23": 0.6, "au24": 0.35,
    }),
    _keyframes(8, "Neugier", {
        "bli": -4, "blo": -2, "bri": -16, "bro": -11, "eo": 1.08, "gx": 0.6, "gy": -0.4,
        "ps": 1.1, "mc": 8, "mw": 76, "ma": -8, "au12R": 0.35,
    }),
)


def _interpolate(keyframes: SectorKeyframes, arousal: float) -> dict[str, float]:
    """Stückweise linear je Kanal, in derselben Reihenfolge der Rechnung wie der Prototyp."""
    # ── Eingabe-Validierung ──
    if not isinstance(keyframes, SectorKeyframes):
        raise TypeError(f"_interpolate: kein SectorKeyframes: {type(keyframes).__name__}")
    if not 0 <= arousal <= 1:
        raise ValueError(f"_interpolate: Arousal {arousal!r} außerhalb 0..1")

    # ── Verarbeitung ──
    values = {}
    for key, neutral in _NEUTRAL_BY_KEY.items():
        full = keyframes.intense.get(key, neutral)
        moderate = keyframes.moderate.get(key, neutral + MOD_AROUSAL * (full - neutral))
        if arousal <= MOD_AROUSAL:
            values[key] = neutral + (arousal / MOD_AROUSAL) * (moderate - neutral)
        else:
            share = (arousal - MOD_AROUSAL) / (1 - MOD_AROUSAL)
            values[key] = moderate + share * (full - moderate)
    return values


def face_target(sector: int, arousal: float) -> FaceState:
    """Das Ziel des Gesichts für einen Sektor (0 = neutral, 1–8) und ein Arousal in 0..1.

    Ein Sektor außerhalb 0–8 oder ein Arousal, das keine endliche Zahl ist, ergibt
    eine Error-Zeile und `NEUTRAL` — das Gesicht bleibt stehen, der Client läuft weiter.
    Ein Arousal außerhalb 0..1 wird wie im Prototyp begrenzt, mit einer Warnung.
    """
    # ── Eingabe-Validierung ──
    sector_is_int = isinstance(sector, int) and not isinstance(sector, bool)
    if not sector_is_int or not 0 <= sector < len(SECTORS):
        logger.error(f"face_target: Sektor {sector!r} unbekannt (gültig 0–8), zeige Neutral")
        return NEUTRAL
    arousal_is_number = isinstance(arousal, int | float) and not isinstance(arousal, bool)
    if not arousal_is_number or not math.isfinite(arousal):
        logger.error(f"face_target: Arousal {arousal!r} keine endliche Zahl, zeige Neutral")
        return NEUTRAL
    clamped = max(0.0, min(1.0, float(arousal)))
    if clamped != arousal:
        logger.warning(f"face_target: Arousal {arousal!r} außerhalb 0..1, begrenzt auf {clamped}")

    # ── Verarbeitung ──
    values = _interpolate(SECTORS[sector], clamped)
    result = FaceState(**{field: float(values[key]) for field, key in PROTOTYPE_KEYS.items()})

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for v in values.values()):
        raise RuntimeError(f"face_target: Ziel nicht endlich (Sektor {sector}, Arousal {clamped})")
    return result
