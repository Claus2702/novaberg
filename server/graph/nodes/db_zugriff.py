"""DB-Zugriffs-Node am Eingang des CharacterGraphs.

Laedt vier Quellen und befuellt die Personality-Klassen im State:

1. User-Werte aus dem Event-Payload in ``external.emotion``.
2. Persistierter Nova-State aus Redis in ``internal.emotion``.
3. Charakter-Hashes aus PostgreSQL (User-Hash in ``external.character``,
   Nova-Hash in ``internal.character``).
4. Charakter-Identitaeten und Direktiven aus PostgreSQL in
   ``internal.identities`` und ``internal.directives``.

Pixie-Sonderfall: bei ``event_source != "user"`` wird ``external`` mit
einer Kopie von ``internal`` initialisiert — Nova spricht mit sich
selbst, Empathie-Differenz ist null.

Konzept: docs/novaberg-path2-perzeption_k.md §4.2.
"""

import logging

from config import POSTGRES_URL, ASSISTANT_USER_ID, redis_client
from graph.personality import (
    Character,
    Emotion,
    Personality,
    InternalPersonality,
    Raum,
)
from ei.raum import raum_ziel_bestimmen
from graph.state import ConversationState
from memory.charakter import (
    charakter_hash_retrieve_dict,
    nova_charakter_hash_retrieve_dict,
)
from memory.pipeline_log import (
    log_db_read,
    log_switch,
    span_end,
    span_start,
)
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.db_zugriff")


def _raum_aus_labels(emotion: Emotion) -> Raum:
    """Leitet Novas Raum aus ihren Register-Labels ab.

    Nur fuer den Fall, dass in ``redis:nova_state`` noch keine Raumwerte
    stehen — Cold-Start oder der erste Turn nach Einfuehrung des Raums
    (Chat 114). Der Raum, in dem sie zuletzt gesprochen hat, ist der
    ehrlichere Startwert als ein erfundener Default.

    Vorbedingung: `emotion` traegt die Registerfelder aus der Perzeption.
    Nachbedingung: Beide Achsen liegen auf denselben Skalen wie im laufenden
    Betrieb, gerundet auf zwei Stellen.
    Fehlerfaelle: Keine — unbekannte Labels nehmen den Tabellen-Default,
    und `raum_ziel_bestimmen` benennt einen Modus ausserhalb des Kanons.
    """
    # ── Verarbeitung ────────────────────────────
    tiefe, naehe = raum_ziel_bestimmen(
        Personality(emotion=emotion), quelle="Cold-Start aus Labels",
    )

    # ── Ausgabe ─────────────────────────────────
    return Raum(tiefe=tiefe, naehe=naehe)


def db_zugriff(state: ConversationState) -> ConversationState:
    """Eingangsnode des CharacterGraphs.

    Laedt Identitaets-Daten und Zustands-Daten aus PostgreSQL und Redis
    und befuellt die Personality-Klassen ``external`` und ``internal``.

    Vorbedingung: ``user_id`` und ``character_id`` sind im State gesetzt.
    Nachbedingung: ``state["external"]`` und ``state["internal"]`` sind
    befuellt; bei ``event_source != "user"`` trgt ``external`` eine Kopie
    von ``internal``.
    Fehlerfaelle: leere ``user_id``/``character_id`` werden geloggt; der
    Node bricht nicht ab, sondern faehrt mit Defaults fort, damit der
    Graph nicht im Eingangsknoten stirbt.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id:       str  = state.get("user_id", "")
    character_id:  str  = state.get("character_id", "")
    turn_id:       str  = state.get("turn_id", "unbekannt")
    event_source:  str  = state.get("event_source", "user")
    event_payload: dict = state.get("event_payload", {}) or {}
    quelle_log:    str  = state.get("ei_calc_rolle", "character")

    if not user_id or not character_id:
        logger.error(
            f"db_zugriff: Paar-Schluessel unvollstaendig — "
            f"user_id='{user_id}', character_id='{character_id}'"
        )

    span_id = span_start(
        turn_id = turn_id,
        node    = "db_zugriff",
        quelle  = quelle_log,
        user_id      = user_id,
        character_id = character_id,
    )
    logger.info(
        f"db_zugriff start — paar={user_id}:{character_id}, "
        f"event_source={event_source}"
    )

    # ── Verarbeitung ────────────────────────────

    # Schritt 1: external.emotion aus dem Event-Payload (User-Werte vom
    # HumanGraph). Bei Pixie-Events sind die Felder typischerweise leer
    # und werden im Pixie-Sonderfall am Ende ueberschrieben.
    external_emotion: Emotion = Emotion(
        emotion              = event_payload.get("current_emotion",    "neutral"),
        arousal              = float(event_payload.get("current_arousal", 0.5)),
        emotions_vector      = event_payload.get("emotions_vektor",    ""),
        mode                 = event_payload.get("gespraechs_modus",   "alltag"),
        language_style       = event_payload.get("sprach_stil",        "neutral"),
        relationship_dynamic = event_payload.get("beziehungs_dynamik", "neutral"),
        tone                 = event_payload.get("tone",               "sachlich"),
        intent               = event_payload.get("intent",             "smalltalk"),
        prompt_topic         = event_payload.get("prompt_thema",       ""),
    )
    logger.info(
        f"db_zugriff Schritt 1 — external.emotion aus Payload: "
        f"emotion={external_emotion.emotion}, arousal={external_emotion.arousal}, "
        f"mode={external_emotion.mode}"
    )

    # Schritt 2: internal.emotion aus Redis nova_state. Cold-Start liefert
    # ein leeres Dict, die Emotion-dataclass-Defaults werden dann unten
    # genutzt (Standard-Konstruktor).
    nova_state_key: str  = f"nova_state:{user_id}:{character_id}"
    nova_state_raw: dict = redis_client.hgetall(nova_state_key) or {}
    log_db_read(
        turn_id = turn_id,
        node    = "db_zugriff",
        quelle  = quelle_log,
        inhalt  = {
            "tabelle": "redis:nova_state",
            "key":     nova_state_key,
            "exists":  bool(nova_state_raw),
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    if nova_state_raw:
        try:
            arousal_persist: float = float(nova_state_raw.get("arousal", 0.5))
        except (ValueError, TypeError):
            arousal_persist = 0.5
        internal_emotion: Emotion = Emotion(
            emotion              = nova_state_raw.get("emotion",              "neutral"),
            arousal              = arousal_persist,
            emotions_vector      = nova_state_raw.get("emotions_vector",      ""),
            mode                 = nova_state_raw.get("mode",                 "alltag"),
            language_style       = nova_state_raw.get("language_style",       "neutral"),
            relationship_dynamic = nova_state_raw.get("relationship_dynamic", "neutral"),
            tone                 = nova_state_raw.get("tone",                 "sachlich"),
            intent               = nova_state_raw.get("intent",               "smalltalk"),
            prompt_topic         = nova_state_raw.get("prompt_topic",         ""),
        )
    else:
        internal_emotion = Emotion()

    # Novas Raum (Chat 114). Fehlt er im Hash — Cold-Start oder erster Turn
    # nach der Einfuehrung —, wird er aus ihren Register-Labels abgeleitet
    # statt auf einen Default gesetzt: Der Raum, in dem sie zuletzt gesprochen
    # hat, ist die ehrlichere Auskunft als ein erfundener Startwert. Dass er
    # abgeleitet und nicht geladen wurde, steht in der Log-Zeile.
    raum_geladen: bool = "raum_tiefe" in nova_state_raw and "raum_naehe" in nova_state_raw
    if raum_geladen:
        try:
            internal_raum = Raum(
                tiefe = float(nova_state_raw["raum_tiefe"]),
                naehe = float(nova_state_raw["raum_naehe"]),
            )
        except (ValueError, TypeError) as fehler:
            logger.exception(
                "%s: db_zugriff: Raumwerte in redis:nova_state unlesbar — "
                "aus den Register-Labels abgeleitet",
                type(fehler).__name__,
            )
            raum_geladen  = False
            internal_raum = _raum_aus_labels(internal_emotion)
    else:
        internal_raum = _raum_aus_labels(internal_emotion)

    logger.info(
        f"db_zugriff Schritt 2 — internal.emotion aus Redis: "
        f"cold_start={not bool(nova_state_raw)}, "
        f"emotion={internal_emotion.emotion}, arousal={internal_emotion.arousal}, "
        f"raum=({internal_raum.tiefe:.2f}, {internal_raum.naehe:.2f})"
        f"{'' if raum_geladen else ' [aus Labels abgeleitet]'}"
    )

    # Schritt 3a: external.character aus PostgreSQL (User-Hash).
    external_hash_dict: dict = charakter_hash_retrieve_dict(
        POSTGRES_URL, user_id, character_id,
    )
    log_db_read(
        turn_id = turn_id,
        node    = "db_zugriff",
        quelle  = quelle_log,
        inhalt  = {
            "tabelle":      "charakter_hash",
            "user_id":      user_id,
            "character_id": character_id,
            "rolle":        "external",
            "hat_treffer":  bool(external_hash_dict),
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )
    external_character: Character = Character(
        core         = external_hash_dict.get("kern",              ""),
        adaptive     = external_hash_dict.get("adaptiv",           ""),
        relationship = external_hash_dict.get("beziehungsprofil",  ""),
        intentions   = external_hash_dict.get("intentions_profil", ""),
        emotions     = external_hash_dict.get("emotions_profil",   ""),
    )

    # Schritt 3b: internal.character (Novas Hash) aus PostgreSQL.
    internal_hash_dict: dict = nova_charakter_hash_retrieve_dict(
        POSTGRES_URL, user_id,
    )
    log_db_read(
        turn_id = turn_id,
        node    = "db_zugriff",
        quelle  = quelle_log,
        inhalt  = {
            "tabelle":      "charakter_hash",
            "user_id":      ASSISTANT_USER_ID,
            "character_id": user_id,
            "rolle":        "internal",
            "hat_treffer":  bool(internal_hash_dict),
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )
    internal_character: Character = Character(
        core         = internal_hash_dict.get("kern",              ""),
        adaptive     = internal_hash_dict.get("adaptiv",           ""),
        relationship = internal_hash_dict.get("beziehungsprofil",  ""),
        intentions   = internal_hash_dict.get("intentions_profil", ""),
        emotions     = internal_hash_dict.get("emotions_profil",   ""),
    )
    logger.info(
        f"db_zugriff Schritt 3 — Hashes geladen: "
        f"external_treffer={bool(external_hash_dict)}, "
        f"internal_treffer={bool(internal_hash_dict)}"
    )

    # Schritt 4a: identities aus PostgreSQL (charakter_anweisungen).
    identities: list[str] = []
    try:
        identities_rows = db_manager.select(
            "SELECT anweisung FROM charakter_anweisungen "
            "WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am",
            (user_id,),
        )
        identities = (
            [r["anweisung"] for r in identities_rows] if identities_rows else []
        )
    except Exception as fehler:
        logger.warning(
            f"db_zugriff — Charakter-Anweisungen Laden fehlgeschlagen: {fehler}"
        )
    log_db_read(
        turn_id = turn_id,
        node    = "db_zugriff",
        quelle  = quelle_log,
        inhalt  = {
            "tabelle": "charakter_anweisungen",
            "user_id": user_id,
            "count":   len(identities),
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    # Schritt 4b: directives aus PostgreSQL (direktiven).
    directives: list[dict] = []
    try:
        direktiven_rows = db_manager.select(
            "SELECT anweisung, kontext FROM direktiven "
            "WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am",
            (user_id,),
        )
        directives = [
            {"anweisung": r["anweisung"], "kontext": r.get("kontext", "")}
            for r in direktiven_rows
        ] if direktiven_rows else []
    except Exception as fehler:
        logger.warning(
            f"db_zugriff — Direktiven Laden fehlgeschlagen: {fehler}"
        )
    log_db_read(
        turn_id = turn_id,
        node    = "db_zugriff",
        quelle  = quelle_log,
        inhalt  = {
            "tabelle": "direktiven",
            "user_id": user_id,
            "count":   len(directives),
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )
    logger.info(
        f"db_zugriff Schritt 4 — Anweisungen geladen: "
        f"identities={len(identities)}, directives={len(directives)}"
    )

    # Schritt 5: Personalities zusammenbauen.
    internal: InternalPersonality = InternalPersonality(
        character  = internal_character,
        emotion    = internal_emotion,
        identities = identities,
        directives = directives,
        raum       = internal_raum,
    )

    # Pixie-Sonderfall: bei event_source != "user" trgt external eine
    # Kopie von internal — Nova spricht mit sich selbst.
    if event_source != "user":
        external: Personality = Personality(
            character = Character(
                core         = internal_character.core,
                adaptive     = internal_character.adaptive,
                relationship = internal_character.relationship,
                intentions   = internal_character.intentions,
                emotions     = internal_character.emotions,
            ),
            emotion = Emotion(
                emotion              = internal_emotion.emotion,
                arousal              = internal_emotion.arousal,
                emotions_vector      = internal_emotion.emotions_vector,
                mode                 = internal_emotion.mode,
                language_style       = internal_emotion.language_style,
                relationship_dynamic = internal_emotion.relationship_dynamic,
                tone                 = internal_emotion.tone,
                intent               = internal_emotion.intent,
                prompt_topic         = internal_emotion.prompt_topic,
            ),
        )
        log_switch(
            turn_id = turn_id,
            node    = "db_zugriff",
            quelle  = quelle_log,
            inhalt  = {
                "bedingung": "event_source",
                "wert":      event_source,
                "zweig":     "pixie_pfad_external_aus_internal",
            },
            span_id = span_id,
            user_id      = user_id,
            character_id = character_id,
        )
        logger.info("db_zugriff — Pixie-Pfad: external = Kopie von internal")
    else:
        external = Personality(
            character = external_character,
            emotion   = external_emotion,
        )
        log_switch(
            turn_id = turn_id,
            node    = "db_zugriff",
            quelle  = quelle_log,
            inhalt  = {
                "bedingung": "event_source",
                "wert":      event_source,
                "zweig":     "user_pfad",
            },
            span_id = span_id,
            user_id      = user_id,
            character_id = character_id,
        )

    # ── Ausgabe-Verifikation ────────────────────
    state["external"] = external
    state["internal"] = internal

    span_end(
        turn_id = turn_id,
        node    = "db_zugriff",
        quelle  = quelle_log,
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )
    logger.info("db_zugriff fertig — external und internal befuellt")

    return state
