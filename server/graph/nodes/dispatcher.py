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

import logging

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

    # pending_writes leeren
    state["pending_writes"] = []

    logger.info(f"Dispatcher: {gesamt} Operationen total, {len(nach_ziel)} Ziele angesprochen")

    return state
