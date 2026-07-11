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
from ei.gravitation import emotionale_gravitation_auf_verlauf_anwenden
from graph.personality import InternalPersonality, Personality
from graph.state import ConversationState

logger = logging.getLogger("ki_server.ei_calc")


def ei_calc(state: ConversationState) -> ConversationState:
    """Berechnet EI-Werte, rollenabhängig.

    Rolle "user":      Nur User-EI-Block (Pfad 1, HumanGraph).
    Rolle "character": Nur Nova-EI-Block (Pfad 2, CharacterGraph).

    Die saubere Trennung vermeidet Doppelarbeit und semantische Vermischung.
    """

    rolle: str = state.get("ei_calc_rolle", "user")
    logger.info(f"EI-Calc: Starte Berechnung (rolle={rolle})")

    if rolle == "user":
        _ei_calc_user(state)
    elif rolle == "character":
        _ei_calc_character(state)
    else:
        logger.warning(f"EI-Calc: Unbekannte rolle '{rolle}' — fallback auf user")
        _ei_calc_user(state)

    logger.info("EI-Calc: Berechnung abgeschlossen")
    return state


def _ei_calc_user(state: ConversationState) -> None:
    """User-EI-Block — für Pfad 1 (HumanGraph).

    Liest die User-Wahrnehmung aus ``state["external"]`` (von perzeption
    gesetzt) und schreibt Emotions-Verlauf, Vektor und korrigierte
    Modus-/Stil-Werte zurueck in dieselbe Personality.
    Keine Nova-Berechnung hier — das passiert in Pfad 2.
    """
    raw_turns: list[dict] = state.get("raw_turns", [])

    external = state.get("external")
    if external is None:
        external = Personality()
        state["external"] = external

    current_emotion:    str   = external.emotion.emotion
    current_arousal:    float = external.emotion.arousal
    beziehungs_dynamik: str   = external.emotion.relationship_dynamic
    intent:             str   = external.emotion.intent
    tone:               str   = external.emotion.tone
    perzeption_modus:   str   = external.emotion.mode
    perzeption_stil:    str   = external.emotion.language_style

    # 1. Emotions-Verlauf (logarithmischer Decay, mit current_emotion als Turn 0)
    emotions_verlauf: list[dict] = _emotions_verlauf_berechnen(
        raw_turns, current_emotion, current_arousal, rolle="user",
    )
    state["emotions_verlauf"] = emotions_verlauf

    # 2. Emotions-Vektor (in external.emotion.emotions_vector)
    emotions_vektor: str = _emotions_vektor_bestimmen(
        raw_turns, current_emotion, rolle="user",
    )
    external.emotion.emotions_vector = emotions_vektor

    # 3. EI-Arousal
    ei_arousal: float = _ei_arousal_berechnen(
        current_arousal, beziehungs_dynamik, intent, tone,
    )

    # 4. Modus-Plausibilität (korrigiert external.emotion.mode)
    korrigierter_modus: str = _modus_plausibilitaet(
        current_emotion, ei_arousal, perzeption_modus,
    )
    external.emotion.mode = korrigierter_modus

    # 5. Sprachstil-Plausibilität (Tiebreaker-Hash aus external.character)
    char_hash_dict: dict = {
        "kern":              external.character.core,
        "adaptiv":           external.character.adaptive,
        "beziehungsprofil":  external.character.relationship,
        "intentions_profil": external.character.intentions,
        "emotions_profil":   external.character.emotions,
    }
    regelbasiert_stil: str = _sprach_stil_erkennen(
        raw_turns,
        char_hash_dict if any(char_hash_dict.values()) else None,
        rolle="user",
    )
    sprach_stil: str = _stil_plausibilitaet(
        current_emotion, ei_arousal, perzeption_stil,
        regelbasiert_stil, tone,
    )
    external.emotion.language_style = sprach_stil

    # Logging
    if emotions_verlauf:
        top_emotions: str = ", ".join(
            f"{e['emotion']}({e['gewicht']:.2f},a={e.get('arousal', 0.5):.2f})"
            for e in emotions_verlauf[:4]
        )
        logger.info(f"EI-Calc/User: Emotions-Verlauf — {top_emotions}")

    if emotions_vektor and emotions_vektor != "plateau":
        logger.info(f"EI-Calc/User: Emotions-Vektor — {emotions_vektor}")

    if sprach_stil and sprach_stil != "neutral":
        logger.info(f"EI-Calc/User: Sprachstil — {sprach_stil}")

    if external.character.relationship:
        logger.info("EI-Calc/User: Beziehungs-Kontext (external.character.relationship) gesetzt")


def _ei_calc_character(state: ConversationState) -> None:
    """Character-EI-Block — für Pfad 2 (CharacterGraph).

    Berechnet Novas Emotion aus ihrer eigenen Turn-Historie plus
    optionaler Empathie vom User (abhängig von event_source).
    Kein virtueller Turn 0 — Novas aktuelle Emotion wird erst nach
    der Antwort-Generierung durch die Perzeption analysiert.
    """
    raw_turns: list[dict] = state.get("raw_turns", [])

    # User-Werte werden gelesen, aber NICHT als Turn 0 in Novas Verlauf injiziert.
    # Sie werden nur für die Empathie-Berechnung gebraucht.
    external = state.get("external")
    current_emotion: str   = external.emotion.emotion if external else "neutral"
    current_arousal: float = external.emotion.arousal if external else 0.5

    # Kraft 1: Novas vorheriger Zustand mit Decay (rein auf historischen Nova-Turns)
    nova_turns: list[dict] = [
        t for t in raw_turns if t.get("rolle") == "assistant"
    ]
    nova_verlauf_basis: list[dict] = _emotions_verlauf_berechnen(
        nova_turns, rolle="assistant", inject_current=False,
    )

    # Kraft 2: Asymmetrische Empathie vom User-Vektor
    event_source: str = state.get("event_source", "user")

    if event_source == "user":
        empathie_ergebnis: dict = _nova_empathie_berechnen(
            nova_verlauf_basis, current_emotion, current_arousal,
        )

        # ── Emotionale Gravitation anwenden (EI Phase 3) ──
        emotionale_punkte: list[dict] = state.get("emotionale_gravitationspunkte", [])

        if emotionale_punkte and empathie_ergebnis.get("nova_verlauf_modifiziert"):
            empathie_ergebnis["nova_verlauf_modifiziert"] = emotionale_gravitation_auf_verlauf_anwenden(
                empathie_ergebnis["nova_verlauf_modifiziert"],
                emotionale_punkte,
            )

            # Nova-Emotion nach Gravitation neu bestimmen (für Logging)
            if empathie_ergebnis["nova_verlauf_modifiziert"]:
                top: dict = empathie_ergebnis["nova_verlauf_modifiziert"][0]
                empathie_ergebnis["nova_emotion"] = top["emotion"]
                empathie_ergebnis["nova_arousal"] = top.get("arousal", 0.3)

            logger.info(
                f"EI-Calc: Emotionale Gravitation angewendet — "
                f"{len(emotionale_punkte)} Punkte, "
                f"Nova-Emotion jetzt: {empathie_ergebnis.get('nova_emotion', '?')}"
            )

        state["nova_emotions_verlauf"] = empathie_ergebnis["nova_verlauf_modifiziert"]
        state["nova_emotion_konflikt"] = empathie_ergebnis["nova_konflikt"]
        logger.info("EI-Calc/Character: Nova-Empathie berechnet (event_source=user)")
    else:
        state["nova_emotions_verlauf"] = nova_verlauf_basis
        state["nova_emotion_konflikt"] = False
        logger.info("EI-Calc/Character: Nova-Empathie übersprungen (event_source=character, nur Decay)")

    # Novas Emotions-Vektor (in internal.emotion.emotions_vector)
    nova_emotions_vektor: str = _emotions_vektor_bestimmen(
        nova_turns, rolle="assistant", inject_current=False,
    )
    internal = state.get("internal")
    if internal is None:
        internal = InternalPersonality()
        state["internal"] = internal
    internal.emotion.emotions_vector = nova_emotions_vektor
    logger.info(
        "EI-Calc/Character: Emotions-Vektor — %s (nova_turns=%d)",
        nova_emotions_vektor, len(nova_turns),
    )

    if state["nova_emotions_verlauf"]:
        nova_top: str = ", ".join(
            f"{e['emotion']}({e['gewicht']:.2f})"
            for e in state["nova_emotions_verlauf"][:3]
        )
        logger.info(f"EI-Calc/Character: Nova-Emotion — {nova_top}")

    if state["nova_emotion_konflikt"]:
        logger.info("EI-Calc/Character: Nova-Emotion — Konflikt erkannt (gegenüberliegende Sektoren)")
