"""EI-Hilfsfunktionen — gemeinsam genutzt von Neugier, Wissensluecken, Dreischicht."""

import logging
import math

import numpy as np

from config import EMOTION_SEKTOR_MAP, MODUS_KANON, SEKTOR_GRUPPE

logger = logging.getLogger("ki_server.ei.utils")


# ─────────────────────────────────────────────
# Emotions-Gruppen aus dem Plutchik-Modell
# ─────────────────────────────────────────────

POSITIVE_EMOTIONEN: set[str] = {
    emotion for emotion, sektor in EMOTION_SEKTOR_MAP.items()
    if SEKTOR_GRUPPE.get(sektor) == "positiv"
}

NEGATIVE_EMOTIONEN: set[str] = {
    emotion for emotion, sektor in EMOTION_SEKTOR_MAP.items()
    if SEKTOR_GRUPPE.get(sektor) == "negativ"
}


def modus_pruefen(modus: str, quelle: str) -> bool:
    """Meldet einen Gespraechsmodus ausserhalb von MODUS_KANON.

    Die Modus-Tabellen des GV-Pfads sind Lookups mit Default. Ein Modus, den
    die Perzeption liefern darf, der aber in keiner Tabelle steht, faellt
    lautlos auf den Wert von "alltag" — und ist von einem echten "alltag"
    hinterher nicht zu unterscheiden. Diese Pruefung macht die Luecke sichtbar,
    bevor der Default sie verdeckt.

    Vorbedingung: `modus` ist der Wert, mit dem gleich gerechnet wird;
    `quelle` benennt den Konsumenten (fuer die Log-Zeile).
    Nachbedingung: Rueckgabe True, wenn der Modus im Kanon liegt.
    Fehlerfaelle: Leerer oder unbekannter Modus — beides wird mit dem Wert
    benannt protokolliert, die Berechnung laeuft mit ihrem Default weiter.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not modus:
        logger.error(
            "Modus-Kanon: leerer Modus in '%s' — die Rechnung nimmt ihren Default",
            quelle,
        )
        return False

    # ── Verarbeitung ────────────────────────────
    bekannt: bool = modus in MODUS_KANON

    # ── Ausgabe-Verifikation ────────────────────
    if not bekannt:
        logger.error(
            "Modus-Kanon: '%s' steht nicht in MODUS_KANON (Konsument '%s') — "
            "die Rechnung nimmt ihren Default, das Ergebnis sieht aus wie 'alltag'",
            modus, quelle,
        )
    return bekannt


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Cosine-Similarity zwischen zwei Vektoren."""
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    dot: float = float(np.dot(a, b))
    norm_a: float = float(np.linalg.norm(a))
    norm_b: float = float(np.linalg.norm(b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def sin_sqrt_norm(wert: float, cap: float) -> float:
    """sin^0.5 Normalisierung: Wert/Cap -> [0, 1].

    Steil am Anfang, flach am Ende. Cap = Obergrenze
    ab der der Wert 1.0 erreicht.
    """
    if wert <= 0:
        return 0.0
    anteil: float = min(wert / cap, 1.0)
    return math.sin(anteil * math.pi / 2) ** 0.5
