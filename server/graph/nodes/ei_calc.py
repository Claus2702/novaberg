"""
EI-Calc Node — Berechnet Emotionale Intelligenz aus den geladenen Daten.

Reiner Berechnungs-Node. Kein LLM-Call, kein I/O.
Liest aus dem State, was der Enricher geladen hat.
Schreibt EI-Ergebnisse zurück in den State.

Position im Graph: Nach Enricher, vor Router.
"""

import logging

from ei.berechnung import (
    _emotions_verlauf_berechnen,
    _emotions_vektor_bestimmen,
    _sprach_stil_erkennen,
    _ei_arousal_berechnen,
    _modus_plausibilitaet,
    _stil_plausibilitaet,
    _nova_empathie_berechnen,
)
from graph.state import ConversationState

logger = logging.getLogger("ki_server.ei_calc")


def ei_calc(state: ConversationState) -> ConversationState:
    """Berechnet EI-Werte aus den vom Enricher geladenen Daten."""

    logger.info("EI-Calc: Starte Berechnung")

    # ── Eingangsdaten aus dem State ──
    raw_turns:      list[dict] = state.get("raw_turns", [])
    char_hash_dict: dict       = state.get("char_hash_dict", {})

    current_emotion:    str   = state.get("current_emotion", "neutral")
    current_arousal:    float = state.get("current_arousal", 0.5)
    beziehungs_dynamik: str   = state.get("beziehungs_dynamik", "neutral")
    intent:             str   = state.get("intent", "smalltalk")
    tone:               str   = state.get("tone", "sachlich")
    perzeption_modus:   str   = state.get("gespraechs_modus", "alltag")
    perzeption_stil:    str   = state.get("sprach_stil", "neutral")

    # ── 1. Emotions-Verlauf (logarithmischer Decay) ──
    emotions_verlauf: list[dict] = _emotions_verlauf_berechnen(
        raw_turns, current_emotion, current_arousal,
    )
    state["emotions_verlauf"] = emotions_verlauf

    # ── 2. Emotions-Vektor (Richtung) ──
    emotions_vektor: str = _emotions_vektor_bestimmen(
        raw_turns, current_emotion,
    )
    state["emotions_vektor"] = emotions_vektor

    # ── 3. EI-Arousal (gewichteter Kombinationsfaktor) ──
    ei_arousal: float = _ei_arousal_berechnen(
        current_arousal, beziehungs_dynamik, intent, tone,
    )

    # ── 4. Modus-Plausibilität (Matrix-Lookup) ──
    korrigierter_modus: str = _modus_plausibilitaet(
        current_emotion, ei_arousal, perzeption_modus,
    )
    state["gespraechs_modus"] = korrigierter_modus

    # ── 5. Stil-Plausibilität (regelbasiert + Gegencheck) ──
    regelbasiert_stil: str = _sprach_stil_erkennen(
        raw_turns, char_hash_dict or None,
    )
    sprach_stil: str = _stil_plausibilitaet(
        current_emotion, ei_arousal, perzeption_stil,
        regelbasiert_stil, tone,
    )
    state["sprach_stil"] = sprach_stil

    # ── 6. Beziehungs-Kontext aus Hash ──
    state["beziehungs_kontext"] = char_hash_dict.get("beziehungsprofil", "")

    # ── Logging ──
    if emotions_verlauf:
        top_emotions: str = ", ".join(
            f"{e['emotion']}({e['gewicht']:.2f},a={e.get('arousal', 0.5):.2f})"
            for e in emotions_verlauf[:4]
        )
        logger.info(f"EI-Calc: Emotions-Verlauf — {top_emotions}")

    if emotions_vektor and emotions_vektor != "plateau":
        logger.info(f"EI-Calc: Emotions-Vektor — {emotions_vektor}")

    if sprach_stil and sprach_stil != "neutral":
        logger.info(f"EI-Calc: Sprachstil — {sprach_stil}")

    if state.get("beziehungs_kontext"):
        logger.info("EI-Calc: Beziehungs-Kontext gesetzt")

    # ── Nova-Emotion (Dual-Emotion Phase 2) ──────────────
    # Kraft 1: Novas vorheriger Zustand mit Decay
    # Novas Turns haben aktuell keine Emotions-Metadaten (bis AP4-7 den
    # async-Pfad baut). _emotions_verlauf_berechnen() auf Novas Turns
    # liefert daher einen leeren Verlauf → Nova startet neutral.
    # Sobald der async-Pfad existiert, füllt sich die Historie und der
    # Decay wirkt automatisch.

    nova_turns: list[dict] = [
        t for t in raw_turns if t.get("rolle") == "assistant"
    ]
    nova_verlauf_basis: list[dict] = _emotions_verlauf_berechnen(
        nova_turns, rolle="assistant",
    )

    # Kraft 2: Asymmetrische Empathie vom User-Vektor
    empathie_ergebnis: dict = _nova_empathie_berechnen(
        nova_verlauf_basis,
        current_emotion,
        current_arousal,
    )

    state["nova_emotions_verlauf"] = empathie_ergebnis["nova_verlauf_modifiziert"]
    state["nova_emotion_konflikt"] = empathie_ergebnis["nova_konflikt"]

    # Novas Emotions-Vektor (Richtung ihres eigenen Bogens)
    nova_emotions_vektor: str = _emotions_vektor_bestimmen(
        nova_turns, rolle="assistant",
    )
    state["nova_emotions_vektor"] = nova_emotions_vektor

    if empathie_ergebnis["nova_verlauf_modifiziert"]:
        nova_top: str = ", ".join(
            f"{e['emotion']}({e['gewicht']:.2f})"
            for e in empathie_ergebnis["nova_verlauf_modifiziert"][:3]
        )
        logger.info(f"EI-Calc: Nova-Emotion — {nova_top}")

    if empathie_ergebnis["nova_konflikt"]:
        logger.info("EI-Calc: Nova-Emotion — Konflikt erkannt (gegenüberliegende Sektoren)")

    logger.info("EI-Calc: Berechnung abgeschlossen")

    return state
