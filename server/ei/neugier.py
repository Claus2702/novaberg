"""
GV4: Effektive Neugier — 6 Saeulen × Persoenlichkeit → [0, 1].

Berechnet Novas aktuelle Neugier aus ihrem emotionalen Zustand,
dem Gespraechsregister und ihrer Grundpersoenlichkeit.
Konzept: Chat 71 — 6 Saeulen × NOVA_NEUGIER, gedeckelt.
"""

import logging

from config import (
    EMOTION_SEKTOR_MAP,
    NOVA_NEUGIER,
    GV_AUFNAHMEBEREITSCHAFT_CAP,
    GV_SESSION_AKT_CAP,
    GV_AUFNAHMEBEREITSCHAFT_EMOTION,
    GV_AUFNAHMEBEREITSCHAFT_STIMMUNG,
    GV_AUFNAHMEBEREITSCHAFT_MODUS,
    GV_AUFNAHMEBEREITSCHAFT_DYNAMIK,
    GV_AUFNAHMEBEREITSCHAFT_STIL,
    GV_REGISTER_SACHLICH_EMOTIONAL,
    GV_REGISTER_SACHLICH_MILD,
    GV_REGISTER_SACHLICH_NEUTRAL,
    GV_REGISTER_OFFEN_EMOTIONAL,
)
from graph.state import ConversationState
from ei.utils import modus_pruefen, sin_sqrt_norm

logger = logging.getLogger("ki_server.ei.neugier")


def sektor_distanz(sektor_a: int, sektor_b: int) -> int:
    """Kuerzeste Distanz auf dem Plutchik-Oktagon (0-4)."""
    d: int = abs(sektor_a - sektor_b)
    return min(d, 8 - d)


def aufnahmebereitschaft_berechnen(state: ConversationState) -> float:
    """Berechnet Novas aktuelle Neugier aus 6 EI-Dimensionen.

    Basis: NOVA_NEUGIER (0.5, Persoenlichkeitsparameter)
    Moduliert durch:
      E — Emotion (Sektor-Distanz zu Neugier/Sektor 8)
      A — Arousal (Energielevel, Krise = Kill)
      V — Vektor (Richtung der Stimmung)
      M — Modus (Fach/Spielerisch/Emotional)
      D — Dynamik (Vertrauen/Distanz)
      S — Stil (Locker/Formell)

    Ergebnis: sin^0.5 normiert auf [0, 1].
    Hohe Neugier (P1/P2) → ~0.96-0.99
    Neutral (P3) → ~0.56
    Traurig (P4) → ~0.32
    Krise (P5) → 0.00
    """
    # Novas Emotion (aus Dual-Emotion, falls vorhanden)
    nova_verlauf: list = state.get("nova_emotions_verlauf", [])
    internal = state.get("internal")
    if nova_verlauf:
        nova_emotion: str = nova_verlauf[0].get("emotion", "neutral")
        nova_arousal: float = nova_verlauf[0].get("arousal", 0.5)
    else:
        # Fallback: Nova-eigener Zustand aus internal.emotion
        nova_emotion = internal.emotion.emotion if internal else "neutral"
        nova_arousal = internal.emotion.arousal if internal else 0.5

    vektor:  str = internal.emotion.emotions_vector      if internal else ""
    modus:   str = internal.emotion.mode                 if internal else "alltag"
    dynamik: str = internal.emotion.relationship_dynamic if internal else "neutral"
    stil:    str = internal.emotion.language_style       if internal else "neutral"

    modus_pruefen(modus, "GV4-Neugier")

    # ── Krise: sofortiger Kill ──
    if vektor in ("spirale", "absturz") and nova_arousal >= 0.7:
        logger.info("GV4-Neugier: 0.00 (Krise)")
        return 0.0

    # ── E: Emotion → Sektor-Distanz zu Neugier (Sektor 8) ──
    sektor: int | None = EMOTION_SEKTOR_MAP.get(nova_emotion)
    if sektor is not None:
        distanz: int = sektor_distanz(sektor, 8)
        logger.debug(
            f"GV4-Neugier Detail: emotion='{nova_emotion}' → sektor={sektor}, "
            f"distanz_zu_8={distanz if sektor is not None else 'n/a'}"
        )
        faktor_e: float = GV_AUFNAHMEBEREITSCHAFT_EMOTION.get(distanz, 1.0)
    else:
        faktor_e = 1.0  # neutral — keine Modulation

    # ── A: Arousal ──
    if nova_arousal >= 0.7:
        faktor_a: float = 1.25
    elif nova_arousal >= 0.5:
        faktor_a = 1.15
    elif nova_arousal >= 0.3:
        faktor_a = 1.00
    else:
        faktor_a = 0.85

    # ── V, M, D, S: Lookup ──
    faktor_v: float = GV_AUFNAHMEBEREITSCHAFT_STIMMUNG.get(vektor, 1.0)
    faktor_m: float = GV_AUFNAHMEBEREITSCHAFT_MODUS.get(modus, 1.0)
    faktor_d: float = GV_AUFNAHMEBEREITSCHAFT_DYNAMIK.get(dynamik, 1.0)
    faktor_s: float = GV_AUFNAHMEBEREITSCHAFT_STIL.get(stil, 1.0)

    # ── Rohwert → sin^0.5 → [0, 1] ──
    produkt: float = faktor_e * faktor_a * faktor_v * faktor_m * faktor_d * faktor_s
    rohwert: float = NOVA_NEUGIER * produkt
    effektiv: float = sin_sqrt_norm(rohwert, GV_AUFNAHMEBEREITSCHAFT_CAP)

    logger.info(
        f"GV4-Neugier: {effektiv:.3f} "
        f"(roh={rohwert:.2f}, produkt={produkt:.2f}, "
        f"emotion='{nova_emotion}' sektor={sektor} dist={distanz if sektor is not None else 'n/a'}, "
        f"E={faktor_e:.2f}, A={faktor_a:.2f}, V={faktor_v:.2f}, "
        f"M={faktor_m:.2f}, D={faktor_d:.2f}, S={faktor_s:.2f})"
    )

    return effektiv


def register_kompatibilitaet(
    gap_arousal: float,
    modus:       str,
    dynamik:     str,
) -> float:
    """Passt die emotionale Ladung der Luecke zum Gespraechsregister?

    Sachlich (Fachgespraech/Arbeit/Lernen/Beratung/Bericht oder Distanz):
      → Emotionale Luecken gedaempft, sachliche bevorzugt.
    Offen (Spielerisch/Kreativ/Philosophisch oder Vertrauen):
      → Emotionale Luecken willkommen.
    Neutral (Alltag, emotional): Keine Modulation.

    Die Modus-Listen decken zusammen alle zehn Werte aus MODUS_KANON ab —
    ein nicht zugeordneter Modus liefe als "neutral" durch, ohne dass es
    jemandem auffiele.
    """
    ist_sachlich: bool = (
        modus in ("fachgespraech", "arbeitsmodus", "lernmodus", "beratend", "berichtend")
        or dynamik == "distanz"
    )
    ist_offen: bool = (
        modus in ("spielerisch", "kreativ", "philosophischer_austausch")
        or dynamik == "vertrauen"
    )

    if ist_sachlich:
        if gap_arousal >= 0.6:
            return GV_REGISTER_SACHLICH_EMOTIONAL   # 0.60
        elif gap_arousal >= 0.3:
            return GV_REGISTER_SACHLICH_MILD         # 0.90
        else:
            return GV_REGISTER_SACHLICH_NEUTRAL      # 1.15

    if ist_offen:
        if gap_arousal >= 0.4:
            return GV_REGISTER_OFFEN_EMOTIONAL       # 1.20
        else:
            return 1.0

    return 1.0


def session_aktualitaet(turn_abstand: int) -> float:
    """Berechnet die Frische eines Session-Turns.

    Invertierte sin^0.5: Steil am Anfang (schnelles Vergessen),
    lang nachhallend (noch praesent nach vielen Turns).
    Nach GV_SESSION_AKT_CAP Turns = 0.

    Turn 0: 1.00, Turn 1: 0.75, Turn 5: 0.44,
    Turn 10: 0.23, Turn 15: 0.10, Turn 20: 0.03
    """
    return 1.0 - sin_sqrt_norm(turn_abstand, GV_SESSION_AKT_CAP)
