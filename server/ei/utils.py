"""
EI-Hilfsfunktionen — gemeinsam genutzt von Neugier, Wissensluecken, Dreischicht.
"""

import math

import numpy as np

from config import EMOTION_SEKTOR_MAP, SEKTOR_GRUPPE


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
