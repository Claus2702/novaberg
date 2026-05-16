"""
Enricher Node — Reichert den State mit Kontext aus dem Gedächtnis an.

Kern-Quellen (immer):
  1. Session-Kontext
  2. KZG/LZG (nur wenn Einträge existieren)
  3. Charakter-Hash

Plugin-Quellen (dynamisch):
  4. Jeder registrierte Manager mit enrich()-Hook
     z.B. FaktenManager → Fakten laden
          TimelineManager → anstehende Termine
          NotizenManager → betroffene Notiz bei Management-Intent

Kein LLM-Aufruf — nur Datenzugriff und Embedding-Erzeugung.
"""

import logging

import ollama
import psycopg2
import redis

from config import (
    ASSISTANT_USER_ID,
)
from graph.context_entry import ContextEntry
from graph.state         import ConversationState
from memory.embedding    import embedding_create
from memory.kzg          import kzg_entries_retrieve, _kzg_prefix
from memory.lzg          import lzg_entries_retrieve
from memory.session      import session_turns_retrieve, _session_key
from memory.ziele        import ziele_aktive_laden
from memory.pipeline_log import (
    span_start,
    span_end,
    log_eingang,
    log_berechnung,
    log_switch,
    log_ausgabe,
)
from ei.gravitation      import (
    ziel_gravitation_berechnen,
    gravitationsterm_berechnen,
    emotionale_gravitation_scannen,
)
from plugins             import get_registry

logger = logging.getLogger("ki_server.enricher")


def enrich(
    state:         ConversationState,
    embed_client: ollama.Client,
    embed_model:   str,
    redis_client:  redis.Redis,
    postgres_url:  str,
    user_id:       str
) -> ConversationState:
    """Sammelt Kontext aus Kern-Quellen und Plugin-Hooks."""

    # ── Pipeline-Log: Span-Start (Anker 1) ──────
    # Graph-Pfad-Marker fuer die Pipeline-Log-Forensik. ei_calc_rolle ist
    # der projektweit etablierte Marker — "user" im HumanGraph, "character"
    # im CharacterGraph (siehe graph/character_graph.py:37, kzg/dispatch.py:42).
    turn_id_log: str = state.get("turn_id", "unbekannt")
    quelle_log:  str = state.get("ei_calc_rolle", "user")
    span_id      = span_start(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = quelle_log,
    )

    entries: list[ContextEntry] = []

    # ─────────────────────────────────────────
    # 1. Session-Kontext (immer, als erstes)
    # ─────────────────────────────────────────

    # Session-Summary in den Kontext (ältere Turns, zusammengefasst)
    character_id: str = state.get("character_id", "")
    summary_key: str = _session_key(user_id, character_id, "summary")
    summary:     str = redis_client.get(summary_key) or ""

    if summary:
        entries.append({
            "quelle":  "summary",
            "subtyp":  "",
            "inhalt":  summary,
            "gewicht": 1.0,
            "meta":    {},
        })
        logger.info("Enricher: Session-Summary geladen (1 Eintrag)")

    # Rohe Turns laden
    raw_turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)
    state["raw_turns"] = raw_turns

    # Session-Turns vollstaendig durchreichen — kein Datenverlust.
    # Formatierung ist Sache der konsumierenden Nodes.
    gefilterte_turns: list[dict] = []

    for turn in raw_turns:
        # Shadow-Impulse ausblenden
        if turn.get("kern") and turn["kern"].startswith("[Nova-Impuls]"):
            continue

        gefilterte_turns.append(turn)

    state["session_turns"] = gefilterte_turns

    # Gesprächsmodus + Emotion aus den letzten User-Turns ableiten
    letzter_modus:   str = ""
    letzte_emotion:  str = ""
    letzte_intentionen: list = []

    for turn in reversed(raw_turns):
        if turn.get("rolle") == "user" and turn.get("modus"):
            letzter_modus      = turn["modus"]
            letzte_emotion     = turn.get("emotion", "neutral")
            letzte_intentionen = turn.get("intentionen", [])
            break

    if letzter_modus:
        state["gespraechs_modus"] = letzter_modus
    state["user_intentionen"]  = letzte_intentionen
    state["user_emotion"]      = letzte_emotion

    if letzter_modus:
        logger.info(
            f"Enricher: Gesprächsmodus={letzter_modus}, "
            f"emotion={letzte_emotion}, intentionen={letzte_intentionen}"
        )

    # ── Pipeline-Log: Eingang (Anker 2) ─────────
    # Session-Kontext geladen, vor Plugin-Loop und Memory-Suche.
    log_eingang(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "session",
        inhalt  = {
            "user_id":              user_id,
            "character_id":         character_id,
            "raw_turns_count":      len(raw_turns) if raw_turns else 0,
            "filtered_turns_count": len(gefilterte_turns) if gefilterte_turns else 0,
            "has_summary":          bool(summary),
        },
        span_id = span_id,
    )

    # ─────────────────────────────────────────
    # 2. Plugin-Hooks: enrich() aller Manager
    # ─────────────────────────────────────────
    registry: dict = get_registry()

    for name, manager in registry.items():
        # DEAKTIVIERT Chat 71 — Fakten-Enrichment produziert 130+ Rausch-Eintraege
        # Wird reaktiviert nach Fakten-Bereinigung
        if name == "fakten":
            # plugin_entries = manager.enrich_entries(state, postgres_url)
            logger.info("Enricher: Fakten-Enrichment deaktiviert (Chat 71)")
            continue

        try:
            plugin_entries: list[ContextEntry] = manager.enrich_entries(state, postgres_url)

            if plugin_entries:
                entries.extend(plugin_entries)
                logger.info(
                    f"Enricher: Plugin '{name}' lieferte {len(plugin_entries)} Eintraege"
                )

        except Exception as fehler:
            logger.error(f"Enricher: Plugin '{name}' Fehler — {fehler}")

    # ─────────────────────────────────────────
    # 2b. Charakter-Anweisungen + Direktiven: Phase-2-Bridge
    #     Laden hat sich in den db_zugriff-Node verschoben.
    #     Hier wird nur noch aus internal.identities/directives in die
    #     flachen Keys gespiegelt, damit Konsumenten in Phase 2 unverändert
    #     bleiben können (Phase 3 entfernt die Bridge).
    # ─────────────────────────────────────────
    internal_perso = state.get("internal")
    state["charakter_anweisungen"] = list(internal_perso.identities) if internal_perso else []
    state["direktiven"]            = list(internal_perso.directives) if internal_perso else []

    # ─────────────────────────────────────────
    # 3. KZG/LZG semantische Suche
    # ─────────────────────────────────────────
    kzg_keys: list = redis_client.keys(_kzg_prefix(user_id, character_id))
    has_lzg:  bool = False

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM langzeitgedaechtnis "
            "WHERE user_id = %s AND character_id = %s AND aktiv = TRUE)",
            (user_id, character_id),
        )
        has_lzg = cursor.fetchone()[0]
        conn.close()
    except Exception:
        pass

    # Prompt-Embedding (für KZG/LZG + Gravitation)
    embedding: list[float] = embedding_create(
        state["user_prompt"], embed_client, embed_model,
    )

    # In den State stellen, damit der Dispatcher es spaeter neben dem
    # User-Turn in der Session ablegen kann (Gravitationsgraph-Panel).
    state["prompt_embedding"] = embedding

    # ── Pipeline-Log: Berechnung (Anker 3) ──────
    # Prompt-Embedding erzeugt. Dimensions-Check als Plausibilitäts-Anker:
    # erwartet werden 768 (nomic-embed-text).
    log_berechnung(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "embedding",
        inhalt  = {
            "embed_model":    embed_model,
            "prompt_length":  len(state.get("user_prompt", "")),
            "embedding_dim":  len(embedding) if embedding else 0,
        },
        span_id = span_id,
    )

    # Lokale Initialisierung, damit der Switch-Inhalt unten beide Counts
    # unabhängig vom Pfad sicher referenzieren kann.
    kzg_entries: list[ContextEntry] = []
    lzg_entries: list[ContextEntry] = []

    if kzg_keys or has_lzg:
        logger.info(
            f"Enricher: {len(kzg_keys)} KZG, LZG={'ja' if has_lzg else 'nein'} — suche Kontext..."
        )

        if kzg_keys:
            kzg_entries = kzg_entries_retrieve(
                redis_client, user_id, character_id, embedding,
            )
            if kzg_entries:
                entries.extend(kzg_entries)
                logger.info(f"Enricher: KZG lieferte {len(kzg_entries)} Eintraege")

        if has_lzg:
            lzg_entries = lzg_entries_retrieve(
                postgres_url, user_id, character_id, embedding,
            )
            if lzg_entries:
                entries.extend(lzg_entries)
                logger.info(f"Enricher: LZG lieferte {len(lzg_entries)} Eintraege")

        # ── Pipeline-Log: Switch — Memory aktiv (Anker 4a) ──
        log_switch(
            turn_id = turn_id_log,
            node    = "enricher",
            quelle  = "memory",
            inhalt  = {
                "kzg_keys_count":     len(kzg_keys),
                "has_lzg":            has_lzg,
                "kzg_entries_count":  len(kzg_entries),
                "lzg_entries_count":  len(lzg_entries),
                "zweig":              "memory_aktiv",
            },
            span_id = span_id,
        )
    else:
        # ── Pipeline-Log: Switch — Memory uebersprungen (Anker 4b) ──
        log_switch(
            turn_id = turn_id_log,
            node    = "enricher",
            quelle  = "memory",
            inhalt  = {
                "kzg_keys_count":  0,
                "has_lzg":         False,
                "zweig":           "memory_uebersprungen",
            },
            span_id = span_id,
        )

    # ─────────────────────────────────────────
    # 4. Charakter-Hash: Phase-2-Bridge
    #     Laden hat sich in den db_zugriff-Node verschoben (Pfad 2). Hier
    #     wird der Hash-Text aus external.character formatiert und in den
    #     memory_context-Pfad gespiegelt, plus char_hash_dict und die
    #     fuenf nova_*-Keys aus den Personality-Klassen aufgefuellt.
    #     Im HumanGraph (Pfad 1) sind die Klassen leer — die alten Konsumenten
    #     erhalten dann leere Strings, was bis Phase 3 hinnehmbar ist.
    # ─────────────────────────────────────────
    external_perso = state.get("external")

    char_hash: str = ""
    if external_perso and (external_perso.character.core or external_perso.character.adaptive):
        parts: list[str] = []
        if external_perso.character.core:
            parts.append(f"Kern-Persönlichkeit: {external_perso.character.core}")
        if external_perso.character.adaptive:
            parts.append(f"Aktuelle Phase: {external_perso.character.adaptive}")
        char_hash = "\n".join(parts)

    state["char_hash_dict"] = {
        "kern":              external_perso.character.core         if external_perso else "",
        "adaptiv":           external_perso.character.adaptive     if external_perso else "",
        "beziehungsprofil":  external_perso.character.relationship if external_perso else "",
        "intentions_profil": external_perso.character.intentions   if external_perso else "",
        "emotions_profil":   external_perso.character.emotions     if external_perso else "",
    } if external_perso else {}

    if char_hash:
        entries.append({
            "quelle":  "charakter",
            "subtyp":  "",
            "inhalt":  char_hash,
            "gewicht": 1.0,
            "meta":    {},
        })
        logger.info("Enricher: Charakter-Hash aus external gespiegelt (1 Eintrag)")

    # ── Novas eigener Charakter-Hash (aus internal.character) ──
    if internal_perso:
        state["nova_kern"]         = internal_perso.character.core
        state["nova_beziehung"]    = internal_perso.character.relationship
        state["nova_adaptiv"]      = internal_perso.character.adaptive
        state["nova_intentionen"]  = internal_perso.character.intentions
        state["nova_emotions"]     = internal_perso.character.emotions

        if internal_perso.character.core or internal_perso.character.relationship:
            logger.info("Enricher: Novas Charakter-Hash aus internal gespiegelt")
    else:
        state["nova_kern"]         = ""
        state["nova_beziehung"]    = ""
        state["nova_adaptiv"]      = ""
        state["nova_intentionen"]  = ""
        state["nova_emotions"]     = ""

    # ─────────────────────────────────────────
    # 5. Ziele + Gravitation (Drive)
    # ─────────────────────────────────────────
    ziele: list[dict] = ziele_aktive_laden(postgres_url, user_id=ASSISTANT_USER_ID)

    if ziele:
        aktiviert: list = ziel_gravitation_berechnen(embedding, ziele)

        state["aktivierte_ziele"] = [
            {
                "ziel_id":     g.ziel_id,
                "ziel_typ":    g.ziel_typ,
                "zielsatz":    g.zielsatz,
                "motivation":  g.motivation,
                "emotion":     g.emotion,
                "arousal":     g.arousal,
                "similarity":  g.similarity,
                "gravitation": g.gravitation,
            }
            for g in aktiviert
        ]
        state["gravitationsterm"] = gravitationsterm_berechnen(aktiviert)

        if aktiviert:
            logger.info(
                f"Enricher: {len(aktiviert)} Ziele aktiviert, "
                f"Gravitationsterm={state['gravitationsterm']:.3f}"
            )
    else:
        state["aktivierte_ziele"] = []
        state["gravitationsterm"] = 0.0

    # ─────────────────────────────────────────
    # 6. Emotionale Gravitation (EI Phase 3)
    # ─────────────────────────────────────────
    emotionale_punkte: list[dict] = emotionale_gravitation_scannen(
        turn_embedding=embedding,
        redis_client=redis_client,
        postgres_url=postgres_url,
        user_id=user_id,
        character_id=character_id,
    )

    state["emotionale_gravitationspunkte"] = emotionale_punkte

    if emotionale_punkte:
        logger.info(
            f"Enricher: {len(emotionale_punkte)} emotionale Gravitationspunkte — "
            f"stärkster: {emotionale_punkte[0].get('emotion', '?')} "
            f"(grav={emotionale_punkte[0].get('gravitation', 0):.3f}, "
            f"quelle={emotionale_punkte[0].get('quelle', '?')})"
        )
    else:
        logger.debug("Enricher: Keine emotionalen Gravitationspunkte")

    # ─────────────────────────────────────────
    # State aktualisieren
    # ─────────────────────────────────────────
    state["memory_entries"] = entries

    if not entries:
        logger.info("Enricher: Pipeline abgeschlossen, 0 Eintraege gesammelt")
    else:
        logger.info(f"Enricher: Pipeline abgeschlossen, {len(entries)} Eintraege gesammelt")

    # ── Pipeline-Log: Ausgabe (Anker 5) ─────────
    # Zustand des State am Enricher-Ausgang.
    log_ausgabe(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "state",
        inhalt  = {
            "memory_entries_count":              len(state.get("memory_entries", [])),
            "aktivierte_ziele_count":            len(state.get("aktivierte_ziele", [])),
            "gravitationsterm":                  state.get("gravitationsterm", 0.0),
            "emotionale_gravitationspunkte_count": len(
                state.get("emotionale_gravitationspunkte", [])
            ),
        },
        span_id = span_id,
    )

    # ── Pipeline-Log: Span-End (Anker 6) ────────
    span_end(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = quelle_log,
        span_id = span_id,
    )

    return state
