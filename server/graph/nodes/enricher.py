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
from graph.state       import ConversationState
from memory.charakter  import charakter_hash_retrieve, charakter_hash_retrieve_dict
from memory.embedding  import embedding_create
from memory.kzg        import kzg_context_retrieve, _kzg_prefix
from memory.lzg        import lzg_context_retrieve
from memory.session    import session_turns_retrieve, _session_key
from plugins           import get_registry

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

    context_parts: list[str] = []

    # ─────────────────────────────────────────
    # 1. Session-Kontext (immer, als erstes)
    # ─────────────────────────────────────────

    # Session-Summary in den Kontext (ältere Turns, zusammengefasst)
    character_id: str = state.get("character_id", "")
    summary_key: str = _session_key(user_id, character_id, "summary")
    summary:     str = redis_client.get(summary_key) or ""

    if summary:
        context_parts.append(f"═══ BISHERIGER GESPRÄCHSVERLAUF ═══\n{summary}")
        logger.info("Enricher: Session-Summary geladen")

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

    state["gespraechs_modus"]  = letzter_modus
    state["user_intentionen"]  = letzte_intentionen
    state["user_emotion"]      = letzte_emotion

    if letzter_modus:
        logger.info(
            f"Enricher: Gesprächsmodus={letzter_modus}, "
            f"emotion={letzte_emotion}, intentionen={letzte_intentionen}"
        )

    # ─────────────────────────────────────────
    # 2. Plugin-Hooks: enrich() aller Manager
    # ─────────────────────────────────────────
    registry: dict = get_registry()

    for name, manager in registry.items():
        try:
            plugin_context: str = manager.enrich(state, postgres_url)

            if plugin_context:
                context_parts.append(plugin_context)
                logger.info(f"Enricher: Plugin '{name}' lieferte Kontext")

        except Exception as fehler:
            logger.error(f"Enricher: Plugin '{name}' Fehler — {fehler}")

    # ─────────────────────────────────────────
    # 2b. Charakter-Anweisungen + Direktiven laden
    # ─────────────────────────────────────────
    from tools.db_manager import db_manager

    try:
        charakter_rows = db_manager.select(
            "SELECT anweisung FROM charakter_anweisungen "
            "WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am",
            (user_id,),
        )
        state["charakter_anweisungen"] = [r["anweisung"] for r in charakter_rows] if charakter_rows else []
        if state["charakter_anweisungen"]:
            logger.info(f"Enricher: {len(state['charakter_anweisungen'])} Charakter-Anweisungen geladen")
    except Exception as fehler:
        logger.warning(f"Enricher: Charakter-Anweisungen laden fehlgeschlagen: {fehler}")
        state["charakter_anweisungen"] = []

    try:
        direktiven_rows = db_manager.select(
            "SELECT anweisung, kontext FROM direktiven "
            "WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am",
            (user_id,),
        )
        state["direktiven"] = [
            {"anweisung": r["anweisung"], "kontext": r.get("kontext", "")}
            for r in direktiven_rows
        ] if direktiven_rows else []
        if state["direktiven"]:
            logger.info(f"Enricher: {len(state['direktiven'])} Direktiven geladen")
    except Exception as fehler:
        logger.warning(f"Enricher: Direktiven laden fehlgeschlagen: {fehler}")
        state["direktiven"] = []

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

    if kzg_keys or has_lzg:
        logger.info(
            f"Enricher: {len(kzg_keys)} KZG, LZG={'ja' if has_lzg else 'nein'} — suche Kontext..."
        )

        embedding: list[float] = embedding_create(
            state["user_prompt"], embed_client, embed_model,
        )

        if kzg_keys:
            kzg_context: str = kzg_context_retrieve(redis_client, user_id, character_id, embedding)
            if kzg_context:
                context_parts.append(kzg_context)
                logger.info("Enricher: KZG-Kontext gefunden")

        if has_lzg:
            lzg_context: str = lzg_context_retrieve(postgres_url, user_id, character_id, embedding)
            if lzg_context:
                context_parts.append(lzg_context)
                logger.info("Enricher: LZG-Kontext gefunden")

    # ─────────────────────────────────────────
    # 4. Charakter-Hash (immer)
    # ─────────────────────────────────────────
    char_hash: str = charakter_hash_retrieve(postgres_url, user_id, character_id)
    char_hash_dict: dict = charakter_hash_retrieve_dict(postgres_url, user_id, character_id)
    state["char_hash_dict"] = char_hash_dict or {}

    if char_hash:
        context_parts.append(f"[Charakter] {char_hash}")
        logger.info("Enricher: Charakter-Hash gefunden")

    # ── Novas eigener Charakter-Hash ──────────
    nova_hash_dict: dict = charakter_hash_retrieve_dict(postgres_url, ASSISTANT_USER_ID, user_id)

    if nova_hash_dict:
        nova_kern:      str = nova_hash_dict.get("kern", "")
        nova_beziehung: str = nova_hash_dict.get("beziehungsprofil", "")

        state["nova_kern"]         = nova_kern
        state["nova_beziehung"]    = nova_beziehung
        state["nova_adaptiv"]      = nova_hash_dict.get("adaptiv", "")
        state["nova_intentionen"]  = nova_hash_dict.get("intentions_profil", "")
        state["nova_emotions"]     = nova_hash_dict.get("emotions_profil", "")

        if nova_kern or nova_beziehung:
            logger.info("Enricher: Novas Charakter-Hash geladen")
    else:
        state["nova_kern"]         = ""
        state["nova_beziehung"]    = ""
        state["nova_adaptiv"]      = ""
        state["nova_intentionen"]  = ""
        state["nova_emotions"]     = ""

    # ─────────────────────────────────────────
    # State aktualisieren
    # ─────────────────────────────────────────
    state["memory_context"] = "\n".join(context_parts)

    if not context_parts:
        logger.info("Enricher: Kein relevanter Kontext gefunden")
    else:
        logger.info(f"Enricher: {len(context_parts)} Kontextquellen angereichert")

    return state
