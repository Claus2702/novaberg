"""
Dispatcher Node — Verteilt pending_writes an die zustaendigen Manager/Agenten.

Letzter Node im Graph (nach Salienz, vor END).
Liest pending_writes aus dem State, gruppiert nach Ziel,
und ruft den jeweiligen Manager oder Agent auf.

Kein LLM-Aufruf — reine Logik + DB-Writes ueber Manager/Agenten.

Position im Graph:
  ... -> Salience -> Dispatcher -> END

KZG-Agent (Chat 29):
  ziel="kzg" -> dispatch_kzg() statt KzgManager.execute()

DelegationsAgent (Chat 32, VENT1):
  ODER-Trigger (Effektivwert / Vektor / Salienz) -> dispatch_delegation()
"""

import json
import logging
from datetime import datetime, timezone

import redis

from graph.state import ConversationState
from plugins     import get_registry
from agents.kzg.dispatch import dispatch_kzg
from agents.delegation.dispatch import dispatch_delegation
from config import (
    ASSISTANT_USER_ID,
    DELEGATION_EFFEKTIVWERT_SCHWELLE,
    DELEGATION_SALIENZ_SCHWELLE,
    EI_AROUSAL_DOMINANZ,
    redis_client as cfg_redis_client,
)
from memory.session import session_turn_store, session_summarize_if_needed

logger = logging.getLogger("ki_server.dispatcher")


def _delegation_trigger_pruefen(state: ConversationState) -> str:
    """ODER-Verknuepfung: Effektivwert / Vektor / Salienz."""
    if state.get("user_id") == ASSISTANT_USER_ID:
        return ""

    emotions_verlauf: list = state.get("emotions_verlauf", [])
    emotions_vektor:  str  = state.get("emotions_vektor", "")
    valenz:        str   = ""
    salienz_score: float = 0.0

    for write in (state.get("pending_writes", []) or []):
        salienz_obj: dict = write.get("daten", {}).get("salienz_obj", {})
        if salienz_obj:
            valenz        = salienz_obj.get("emotionen", {}).get("valenz", "")
            salienz_score = salienz_obj.get("salienz", 0.0)
            break

    # Kriterium 1: Effektivwert
    if emotions_verlauf:
        top          = emotions_verlauf[0]
        gewicht      = top.get("gewicht", 0.0)
        arousal      = top.get("arousal", 0.5)
        effektivwert = gewicht * (arousal ** EI_AROUSAL_DOMINANZ)
        if effektivwert >= DELEGATION_EFFEKTIVWERT_SCHWELLE:
            return "effektivwert"

    # Kriterium 2: Emotions-Vektor
    if (emotions_vektor and emotions_vektor != "plateau"
            and valenz and valenz != "neutral"):
        return "vektor"

    # Kriterium 3: Salienz
    if (salienz_score >= DELEGATION_SALIENZ_SCHWELLE
            and valenz and valenz != "neutral"):
        return "salienz"

    return ""


def _persist_short_term_drive(state: ConversationState) -> None:
    """Schreibt den kurzfristigen Drive-Zustand nach Redis.

    Snapshot der drei Felder, die nach einem Turn das aktuelle Drive-Bild
    ergeben: Gespraechsvektor (GV-Hypothese), aktivierte Ziele (mit
    Gravitation), Gravitationsterm. Wird vom Drive-Endpoint gelesen, damit
    das Ziele-Panel die Live-Lage zeigen kann.

    Key: drive:short_term:{user_id}:{character_id}
    Wert: JSON mit englischen Feldnamen (conversation_vector,
    activated_goals, gravity_term, timestamp). Kein TTL — wird beim
    naechsten Turn ueberschrieben.
    """
    user_id:      str = state.get("user_id", "")
    character_id: str = state.get("character_id", "")

    if not user_id or not character_id:
        logger.debug(
            "Dispatcher: Short-Term-Drive nicht persistiert — "
            "user_id oder character_id fehlt"
        )
        return

    aktivierte: list = state.get("aktivierte_ziele") or []
    activated_goals: list[dict] = []
    for ziel in aktivierte:
        # aktivierte_ziele sind plain dicts (siehe enricher); robust gegen
        # versehentliche ActivatedGoal-Objekte mit getattr-Fallback.
        if isinstance(ziel, dict):
            zielsatz    = ziel.get("zielsatz", "")
            similarity  = ziel.get("similarity", 0.0)
            motivation  = ziel.get("motivation", 0.0)
            gravitation = ziel.get("gravitation", 0.0)
        else:
            zielsatz    = getattr(ziel, "zielsatz", "")
            similarity  = getattr(ziel, "similarity", 0.0)
            motivation  = getattr(ziel, "motivation", 0.0)
            gravitation = getattr(ziel, "gravitation", 0.0)

        activated_goals.append({
            "goal_text":        zielsatz,
            "similarity":       float(similarity),
            "motivation":       float(motivation),
            "gravity_strength": float(gravitation),
        })

    conversation_vector: str = state.get("gespraechsvektor", "") or ""
    gravity_term_raw         = state.get("gravitationsterm", 0.0)
    gravity_term: float | None
    if gravity_term_raw is None:
        gravity_term = None
    else:
        try:
            gravity_term = float(gravity_term_raw)
        except (TypeError, ValueError):
            gravity_term = None

    payload: dict = {
        "conversation_vector": conversation_vector,
        "activated_goals":     activated_goals,
        "gravity_term":        gravity_term,
        "timestamp":           datetime.now(timezone.utc).isoformat(),
    }

    key: str = f"drive:short_term:{user_id}:{character_id}"

    try:
        cfg_redis_client.set(key, json.dumps(payload, ensure_ascii=False))
        logger.info(
            f"Dispatcher: Short-Term-Drive geschrieben — "
            f"{len(activated_goals)} aktivierte Ziele, "
            f"gravity_term={gravity_term}, "
            f"vector={'gefuellt' if conversation_vector else 'leer'}"
        )
    except Exception as fehler:
        logger.warning(f"Dispatcher: Short-Term-Drive-Persist fehlgeschlagen — {fehler}")


def _persist_gv_detail(state: ConversationState) -> None:
    """Schreibt das GV-Detail (Sprünge, Neugier, Wissensluecken, Farbton)
    nach Redis, damit das GV-Panel den aktuellen Stand auch ohne
    WebSocket-Broadcast (Initial-Load) abfragen kann.

    Key: gv:detail:{user_id}:{character_id}. Kein TTL — wird beim naechsten
    Turn ueberschrieben.
    """
    user_id:      str  = state.get("user_id", "")
    character_id: str  = state.get("character_id", "")
    gv_detail:    dict = state.get("gv_detail") or {}

    if not user_id or not character_id or not gv_detail:
        return

    key: str = f"gv:detail:{user_id}:{character_id}"

    try:
        cfg_redis_client.set(key, json.dumps(gv_detail, ensure_ascii=False))
        logger.debug(f"Dispatcher: gv_detail nach Redis geschrieben ({key})")
    except Exception as fehler:
        logger.warning(f"Dispatcher: gv_detail-Persist fehlgeschlagen — {fehler}")


def _session_turn_schreiben(state: ConversationState) -> None:
    """Schreibt den aktuellen Turn vollständig in die Session.

    Bestimmt die Rolle automatisch: Wenn eine Response vorhanden ist,
    wird ein Assistant-Turn geschrieben. Sonst ein User-Turn.
    Alle Metadaten kommen aus dem State — kein nachträgliches Annotieren.
    """
    user_id:      str = state.get("user_id", "")
    character_id: str = state.get("character_id", "")

    if not user_id or not character_id:
        logger.warning("Dispatcher: Session-Turn nicht geschrieben — user_id oder character_id fehlt")
        return

    response: str = state.get("response", "")

    if response:
        # Pfad 2: Charakter hat geantwortet
        rolle:  str = "assistant"
        inhalt: str = response
    else:
        # Pfad 1: User hat geschrieben
        rolle  = "user"
        inhalt = state.get("user_prompt", "")

    if not inhalt:
        logger.warning(f"Dispatcher: Session-Turn nicht geschrieben — kein Inhalt (rolle={rolle})")
        return

    # Embedding nur fuer User-Turns durchreichen — der Enricher berechnet
    # eines fuer Novas eigene Antworten nicht, und der Gravitationsgraph
    # braucht es auch nur fuer die User-Punkte.
    embedding: list[float] | None = None
    themen: list[str] | None = None
    if rolle == "user":
        embedding = state.get("prompt_embedding") or None
        # Perzeption setzt ``prompt_thema`` als String (Singular). Wir
        # heben das auf eine Liste, weil session_turn_store ein themen-
        # Array erwartet und der Gravitationsgraph mehrere Topics pro
        # Turn unterstuetzt.
        prompt_thema: str = (state.get("prompt_thema") or "").strip()
        if prompt_thema:
            themen = [prompt_thema]

    session_turn_store(
        redis_client       = cfg_redis_client,
        user_id            = user_id,
        character_id       = character_id,
        rolle              = rolle,
        inhalt             = inhalt,
        intentionen        = state.get("user_intentionen", []),
        emotion            = state.get("current_emotion", "neutral"),
        arousal            = state.get("current_arousal", 0.5),
        modus              = state.get("gespraechs_modus", ""),
        kern               = state.get("session_turn_kern", ""),
        emotions_vektor    = state.get("emotions_vektor", ""),
        sprach_stil        = state.get("sprach_stil", ""),
        beziehungs_dynamik = state.get("beziehungs_dynamik", ""),
        tone               = state.get("tone", "sachlich"),
        themen             = themen,
        embedding          = embedding,
    )

    logger.info(f"Dispatcher: Session-Turn geschrieben — rolle={rolle}, {len(inhalt)} Zeichen")

    # Zusammenfassung prüfen (älteste Turns komprimieren wenn Stack zu groß)
    session_summarize_if_needed(cfg_redis_client, user_id, character_id)


def dispatch(
    state:         ConversationState,
    redis_client:  redis.Redis,
    postgres_url:  str,
    embed_client = None,
    embed_model:   str = ""
) -> ConversationState:
    """
    Verteilt alle pending_writes an die zustaendigen Manager/Agenten.
    Jeder Manager/Agent bekommt nur seine eigenen Writes.
    """

    writes: list = state.get("pending_writes", []) or []

    if not writes:
        logger.info("Dispatcher: Keine pending_writes — Durchlauf")
        # Auch ohne Writes wollen wir den kurzfristigen Drive-Snapshot
        # persistieren, damit das Ziele-Panel z.B. nach Begruessungs-Turns
        # nicht auf veraltete Daten zeigt.
        _persist_short_term_drive(state)
        return state

    user_id:  str  = state["user_id"]
    registry: dict = get_registry()

    # Nach Ziel gruppieren
    nach_ziel: dict[str, list[dict]] = {}
    for write in writes:
        ziel: str = write.get("ziel", "")
        if ziel:
            nach_ziel.setdefault(ziel, []).append(write)

    # An zustaendige Manager/Agenten verteilen
    gesamt: int = 0

    for ziel, ziel_writes in nach_ziel.items():

        # ── KZG-Agent (ersetzt KzgManager seit Chat 29) ──
        if ziel == "kzg":
            try:
                result: dict = dispatch_kzg(
                    state, ziel_writes,
                    embed_client=embed_client,
                    embed_model=embed_model,
                )
                count: int = result.get("kzg_verarbeitet", 0)
                gesamt += count
                logger.info(f"Dispatcher: 'kzg' -> KZG-Agent, {count} Segmente verarbeitet")
            except Exception as fehler:
                logger.error(f"Dispatcher: Fehler bei KZG-Agent — {fehler}")
            continue

        # ── Legacy: Manager-Pfad ──
        manager = registry.get(ziel)

        if not manager:
            logger.warning(f"Dispatcher: Kein Manager fuer '{ziel}' registriert — {len(ziel_writes)} Writes verworfen")
            continue

        try:
            count: int = manager.execute(
                writes        = ziel_writes,
                user_id       = user_id,
                redis_client  = redis_client,
                postgres_url  = postgres_url,
                embed_client = embed_client,
                embed_model   = embed_model,
            )

            gesamt += count
            logger.info(f"Dispatcher: '{ziel}' -> {count} Operationen ausgefuehrt")

        except Exception as fehler:
            logger.error(f"Dispatcher: Fehler bei '{ziel}' — {fehler}")

    # ── DelegationsAgent (VENT1, Chat 32) ──
    trigger: str = _delegation_trigger_pruefen(state)
    if trigger:
        try:
            state["_delegation_trigger"] = trigger
            for write in writes:
                salienz_obj = write.get("daten", {}).get("salienz_obj", {})
                if salienz_obj:
                    state["salienz_obj_aktuell"] = salienz_obj
                    break
            dispatch_delegation(state, embed_client=embed_client, embed_model=embed_model)
            logger.info(f"Dispatcher: DelegationsAgent gefeuert (trigger={trigger})")
        except Exception as fehler:
            logger.error(f"Dispatcher: Fehler bei DelegationsAgent — {fehler}")

    # ── Session-Turn schreiben (nach allen Writes, damit kern verfügbar ist) ──
    _session_turn_schreiben(state)

    logger.info(
        f"Dispatcher: gv_detail={'vorhanden' if state.get('gv_detail') else 'LEER'}, "
        f"Keys: {list(state.get('gv_detail', {}).keys())}"
    )

    # ── Short-Term-Drive nach Redis (fuers Ziele-Panel) ──
    _persist_short_term_drive(state)

    # ── GV-Detail nach Redis (fuers GV-Panel Initial-Load) ──
    _persist_gv_detail(state)

    # pending_writes leeren
    state["pending_writes"] = []

    logger.info(f"Dispatcher: {gesamt} Operationen total, {len(nach_ziel)} Ziele angesprochen")

    return state
