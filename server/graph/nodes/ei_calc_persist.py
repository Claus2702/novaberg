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
import time

from config import redis_client
from ei.berechnung import (
    _ei_arousal_berechnen,
    _modus_plausibilitaet,
    _sprach_stil_erkennen,
    _stil_plausibilitaet,
)
from graph.state import ConversationState, reiz_herkunft
from memory.pipeline_log import (
    log_berechnung,
    log_db_write,
    span_end,
    span_start,
)

logger = logging.getLogger("ki_server.ei_calc_persist")


def _aeusserungszeit(
    state: ConversationState, herkunft: str, turn_id: str,
) -> float | None:
    """Bestimmt, wann die Aeusserung eintraf, die diesen Turn ausgeloest hat.

    Genommen wird `empfangen_am` aus dem Ereignis — der Zeitpunkt **vor** jeder
    Verarbeitung. Die Uhr dieses Knotens taugt dafuer nicht: Er laeuft am Ende
    des Durchlaufs, hinter Perzeption, Salienz und den Modellaufrufen, und
    truege deren Dauer samt Wartezeit am `llm_lock` in den Abstand hinein.
    Dieselbe Begruendung steht an der Quelle in `api/chat.py`, wo `erstellt_am`
    aus genau diesem Grund verworfen wurde.

    Args:
        state: der Zustand des Laufs.
        herkunft: ``"nutzer_turn"`` oder ``"eigener_impuls"``.
        turn_id: fuer die Meldung.

    Returns:
        Die Empfangszeit, oder ``None`` auf einem Impuls-Turn — er ist keine
        Aeusserung und setzt die Uhr nicht.
    """
    # ── Eingabe-Validierung ─────────────────────
    if herkunft != "nutzer_turn":
        return None

    roh = (state.get("event_payload") or {}).get("empfangen_am")
    if roh is None:
        # Kein Grund, den Turn abzubrechen — aber die Uhr traegt dann die
        # Dauer dieses Durchlaufs mit, und das gehoert gesagt.
        logger.warning(
            "%s: ei_calc_persist: empfangen_am fehlt im Ereignis — "
            "nutzer_zeit traegt die Verarbeitungsdauer dieses Turns mit",
            turn_id,
        )
        return time.time()

    # ── Verarbeitung / Ausgabe ──────────────────
    try:
        return float(roh)
    except (TypeError, ValueError):
        logger.exception(
            "%s: ei_calc_persist: empfangen_am unlesbar (%r) — nutzer_zeit "
            "traegt die Verarbeitungsdauer dieses Turns mit",
            turn_id, roh,
        )
        return time.time()


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
        user_id      = user_id,
        character_id = character_id,
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
        user_id      = user_id,
        character_id = character_id,
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
        user_id      = user_id,
        character_id = character_id,
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
        user_id      = user_id,
        character_id = character_id,
    )
    internal.emotion.language_style = korrigierter_stil

    # Schritt 4: Persistierung in Redis. Kein TTL — konsistent zur
    # gv:detail:-Konvention, jeder CharacterGraph-Lauf ueberschreibt.
    jetzt:    float = time.time()
    herkunft: str   = reiz_herkunft(state)
    nutzer_zeit: float | None = _aeusserungszeit(state, herkunft, turn_id)

    nova_state_key: str  = f"nova_state:{user_id}:{character_id}"
    nova_state_mapping: dict = {
        # Novas Raum (Chat 114) — er ueberlebt den Turn, weil ein
        # Registerwechsel ueber mehrere Turns laeuft. Ohne Persistenz gaebe es
        # keinen Zwischenzustand und damit keinen Zug, nur ein Springen.
        "raum_tiefe":           str(internal.raum.tiefe),
        "raum_naehe":           str(internal.raum.naehe),
        "emotion":              internal.emotion.emotion,
        "arousal":              str(internal.emotion.arousal),
        "emotions_vector":      internal.emotion.emotions_vector,
        "mode":                 internal.emotion.mode,
        "language_style":       internal.emotion.language_style,
        "relationship_dynamic": internal.emotion.relationship_dynamic,
        "tone":                 internal.emotion.tone,
        "intent":               internal.emotion.intent,
        "prompt_topic":         internal.emotion.prompt_topic,
        # Die Uhr der Eigenzeit (Bauteil A). **Jeder** Turn setzt `turn_zeit`;
        # `nutzer_zeit` nur der, den ein Mensch ausgeloest hat.
        #
        # Die Trennung ist der Bauteil: Liefe der Verfall auf dem letzten Turn,
        # setzte der stuendliche Impuls die Uhr zurueck und die Nacht waere nie
        # eine Pause (novaberg-eigenzeit_k.md §2.2).
        #
        # Und er liegt hier statt im Session-Verlauf, obwohl der dort ein
        # `zeit`-Feld je Turn traegt: Die Session verfaellt nach zwei Stunden
        # Inaktivitaet und haelt nur zwanzig Turns. Beides greift genau dort,
        # wo dieser Wert gebraucht wird — die Kurve laeuft bis drei Stunden,
        # und eine Nacht mit stuendlichen Impulsen schoebe die letzte
        # Nutzeraeusserung aus dem Fenster, waehrend sie die Frist erneuert.
        "turn_zeit":            str(jetzt),
    }
    if nutzer_zeit is not None:
        nova_state_mapping["nutzer_zeit"] = str(nutzer_zeit)

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
        user_id      = user_id,
        character_id = character_id,
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
        user_id      = user_id,
        character_id = character_id,
    )
    return state
