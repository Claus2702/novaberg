"""ei_calc_persist-Node: Konsolidierung und Persistierung der Nova-EI.

Laeuft nach perzeption_assistant, vor salience. Wendet die
Plausibilitaeten-Regeln (Modus, Sprachstil) auf die frische
Nova-Perzeption an und persistiert Novas neun EI-Dimensionen in
Redis unter ``nova_state:{user_id}:{character_id}``.

Beim naechsten CharacterGraph-Lauf liest der db_zugriff-Node diesen
Hash und befuellt ``internal.emotion`` damit. Pixie-Pfade schreiben in
denselben Hash — Novas Default Mode Network.

Konzept: docs/novaberg-path2-perzeption_k.md §4.6.
"""

import logging

from config import redis_client
from ei.berechnung import (
    _ei_arousal_berechnen,
    _modus_plausibilitaet,
    _sprach_stil_erkennen,
    _stil_plausibilitaet,
)
from graph.state import ConversationState
from memory.pipeline_log import (
    log_berechnung,
    log_db_write,
    span_end,
    span_start,
)

logger = logging.getLogger("ki_server.ei_calc_persist")


def ei_calc_persist(state: ConversationState) -> ConversationState:
    """Plausibilitaeten auf Nova-EI anwenden und in Redis persistieren.

    Vorbedingung: ``state["internal"]`` ist befuellt (durch db_zugriff) und
    die Perzeption-Assistant-Werte liegen in ``internal.emotion``
    (perzeption schreibt seit Phase 3 direkt dort hinein).

    Nachbedingung: Plausibilitaets-korrigierte Werte sind in
    ``internal.emotion`` und ``redis:nova_state:{user_id}:{character_id}``.
    """

    # ── Eingabe-Validierung ─────────────────────
    user_id:      str  = state.get("user_id", "")
    character_id: str  = state.get("character_id", "")
    turn_id:      str  = state.get("turn_id", "unbekannt")
    raw_turns:    list = state.get("raw_turns", [])

    internal = state.get("internal")
    if internal is None:
        logger.error(
            "ei_calc_persist: internal fehlt im State — Persistierung verworfen"
        )
        return state

    if not user_id or not character_id:
        logger.error(
            f"ei_calc_persist: Paar-Schluessel unvollstaendig — "
            f"user_id='{user_id}', character_id='{character_id}' — verworfen"
        )
        return state

    span_id = span_start(
        turn_id = turn_id,
        node    = "ei_calc_persist",
        quelle  = "character",
    )

    logger.info(
        f"ei_calc_persist start — paar={user_id}:{character_id}, "
        f"emotion={internal.emotion.emotion}, arousal={internal.emotion.arousal}"
    )

    # ── Verarbeitung ────────────────────────────

    # Schritt 1: EI-Arousal aus Nova-Werten berechnen.
    nova_arousal_ei: float = _ei_arousal_berechnen(
        internal.emotion.arousal,
        internal.emotion.relationship_dynamic,
        internal.emotion.intent,
        internal.emotion.tone,
    )
    log_berechnung(
        turn_id = turn_id,
        node    = "ei_calc_persist",
        quelle  = "character",
        inhalt  = {
            "schritt":     "ei_arousal",
            "arousal_roh": internal.emotion.arousal,
            "arousal_ei":  nova_arousal_ei,
            "dynamik":     internal.emotion.relationship_dynamic,
            "intent":      internal.emotion.intent,
            "tone":        internal.emotion.tone,
        },
        span_id = span_id,
    )

    # Schritt 2: Modus-Plausibilitaet anwenden.
    korrigierter_modus: str = _modus_plausibilitaet(
        internal.emotion.emotion,
        nova_arousal_ei,
        internal.emotion.mode,
    )
    log_berechnung(
        turn_id = turn_id,
        node    = "ei_calc_persist",
        quelle  = "character",
        inhalt  = {
            "schritt":    "modus_plausibilitaet",
            "perzeption": internal.emotion.mode,
            "korrigiert": korrigierter_modus,
        },
        span_id = span_id,
    )
    internal.emotion.mode = korrigierter_modus

    # Schritt 3: Sprachstil-Plausibilitaet anwenden. Tiebreaker-Quelle
    # ist Novas eigener Charakter (internal.character).
    nova_char_dict: dict = {
        "kern":              internal.character.core,
        "adaptiv":           internal.character.adaptive,
        "beziehungsprofil":  internal.character.relationship,
        "intentions_profil": internal.character.intentions,
        "emotions_profil":   internal.character.emotions,
    }
    regelbasiert_stil: str = _sprach_stil_erkennen(
        raw_turns,
        nova_char_dict if any(nova_char_dict.values()) else None,
        rolle="assistant",
    )
    korrigierter_stil: str = _stil_plausibilitaet(
        internal.emotion.emotion,
        nova_arousal_ei,
        internal.emotion.language_style,
        regelbasiert_stil,
        internal.emotion.tone,
    )
    log_berechnung(
        turn_id = turn_id,
        node    = "ei_calc_persist",
        quelle  = "character",
        inhalt  = {
            "schritt":      "stil_plausibilitaet",
            "perzeption":   internal.emotion.language_style,
            "regelbasiert": regelbasiert_stil,
            "korrigiert":   korrigierter_stil,
        },
        span_id = span_id,
    )
    internal.emotion.language_style = korrigierter_stil

    # Schritt 4: Persistierung in Redis. Kein TTL — konsistent zur
    # gv:detail:-Konvention, jeder CharacterGraph-Lauf ueberschreibt.
    nova_state_key: str  = f"nova_state:{user_id}:{character_id}"
    nova_state_mapping: dict = {
        "emotion":              internal.emotion.emotion,
        "arousal":              str(internal.emotion.arousal),
        "emotions_vector":      internal.emotion.emotions_vector,
        "mode":                 internal.emotion.mode,
        "language_style":       internal.emotion.language_style,
        "relationship_dynamic": internal.emotion.relationship_dynamic,
        "tone":                 internal.emotion.tone,
        "intent":               internal.emotion.intent,
        "prompt_topic":         internal.emotion.prompt_topic,
    }
    redis_client.hset(nova_state_key, mapping=nova_state_mapping)
    log_db_write(
        turn_id = turn_id,
        node    = "ei_calc_persist",
        quelle  = "character",
        inhalt  = {
            "tabelle":   "redis:nova_state",
            "operation": "hset",
            "key":       nova_state_key,
            "felder":    list(nova_state_mapping.keys()),
        },
        span_id = span_id,
    )

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        f"ei_calc_persist fertig — nova_state persistiert: "
        f"emotion={internal.emotion.emotion}, mode={internal.emotion.mode}, "
        f"style={internal.emotion.language_style}"
    )

    span_end(
        turn_id = turn_id,
        node    = "ei_calc_persist",
        quelle  = "character",
        span_id = span_id,
    )
    return state
