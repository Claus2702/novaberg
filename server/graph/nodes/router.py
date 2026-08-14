"""
Router Node — Entscheidet ueber Ressourcen-Routing.

Liest die Perzeption-Ergebnisse aus dem State und entscheidet,
welche Datenquellen und Aktionen fuer die Verarbeitung noetig sind.

Plugin-Erweiterung (A1.2):
  Der Router-Prompt wird dynamisch um Erkennungsregeln aller
  registrierten Manager-Plugins erweitert.

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).
"""

import json
import logging
from datetime import datetime

from graph.reiz  import reiz_text
from graph.state import ConversationState
from plugins     import get_combined_router_prompt
from config import redis_client, get_node_config, PROMPTS
from memory.session import session_turns_retrieve, format_session_turns_numbered
from services.model_services import model_service, ChatRequest

logger = logging.getLogger("ki_server.router")


def _build_router_prompt(
    state: ConversationState,
    session_turns: str | None = None,
) -> str:
    """Baut den Router-System-Prompt aus [BLOCKNAME]-Bloecken zusammen.

    Reihenfolge nach Primacy/Recency (nova-01-t-d):
    OBEN:   [IDENTITAET] -> [AUFGABE]
    MITTE:  [KONTEXT] (Session-Turns) -> [AGENTEN] (Plugin-Regeln)
    UNTEN:  [REGELN] (direkt vor der User-Message)
    """
    external = state.get("external")
    bloecke: list[str] = [
        PROMPTS["router.identity"].format(
            today              = datetime.now().strftime("%d.%m.%Y, %H:%M Uhr"),
            intent             = external.emotion.intent               if external else "smalltalk",
            emotion            = external.emotion.emotion              if external else "neutral",
            arousal            = external.emotion.arousal              if external else 0.5,
            modus              = external.emotion.mode                 if external else "alltag",
            beziehungs_dynamik = external.emotion.relationship_dynamic if external else "neutral",
        ),
        PROMPTS["router.task"],
    ]

    if session_turns:
        bloecke.append(
            "[KONTEXT]\n"
            "Nutze den Verlauf fuer Rueckbezug-Aufloesung und "
            "Management-Target-Erkennung. "
            "Hoehere Nummern sind aktueller — loese Bezuege "
            "bevorzugt ueber die hoechsten Nummern auf.\n"
            f"\n{session_turns}"
        )

    plugin_additions: str = get_combined_router_prompt()
    if plugin_additions:
        bloecke.append(
            "[AGENTEN]\n"
            "Die folgenden Regeln stammen von registrierten Agenten. "
            "Nur diese Regeln duerfen die Management-Felder setzen.\n"
            f"\n{plugin_additions}"
        )

    bloecke.append(PROMPTS["router.rules"])

    return "\n\n".join(bloecke)


def route(
    state: ConversationState,
) -> ConversationState:
    """Entscheidet ueber Ressourcen-Routing basierend auf Perzeption-Ergebnissen.

    Geroutet wird der Reiz dieses Durchlaufs, nicht der Reiz-Platz: Auf einem
    Impuls-Turn steht dort nichts, und ein Router ohne Text entscheidet ueber
    Gedaechtnis, Web und Zeitachse auf einer leeren Zeichenkette.
    """
    reiz: str = reiz_text(state)
    logger.info(f"Router: Route Prompt ({len(reiz)} Zeichen)")

    # ── Pending Agent Check (Resume-Flow) ──────────
    # Wenn ein Agent auf Antwort wartet, ueberspringen wir den LLM-Call.
    # Die User-Antwort geht direkt als Resume an den wartenden Agent.
    from tools.redis_manager import redis_manager

    user_id = state.get("user_id", "")
    pending_key = f"pending_agent:{user_id}"
    pending = redis_manager.get_json(pending_key)

    if pending:
        agent_name = pending.get("agent_name", "")
        logger.info(f"Router: Pending Agent erkannt — '{agent_name}', Resume-Flow aktiviert")
        state["management_action"] = "resume"
        state["management_target"] = ""
        state["needs_memory"]      = True
        state["needs_web"]         = False
        state["needs_timeline"]    = False
        state["timeline_query"]    = {}
        state["momentum"]          = "mid"
        return state

    # ── Session-Kontext laden (leichtgewichtig, Redis-Read) ──
    character_id: str = state.get("character_id", "")
    session_turns: str | None = None
    if user_id:
        try:
            raw_turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)
            session_turns = format_session_turns_numbered(raw_turns, max_turns=5) or None
            if session_turns:
                logger.info("Router: Session-Kontext geladen (nummeriert)")
        except Exception as e:
            logger.warning(f"Router: Session-Kontext konnte nicht geladen werden: {e}")

    system_prompt: str = _build_router_prompt(state, session_turns)

    logger.info(f"Router: System-Prompt:\n{system_prompt}")

    node_cfg = get_node_config("router")

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 3) ──
    # route() laeuft im FastAPI-Threadpool (api/chat.py:chat_senden ist eine
    # sync def). Kein Event-Loop im aufrufenden Thread → submit_sync nutzt
    # die Bruecke ueber asyncio.run_coroutine_threadsafe in den Haupt-Loop
    # des Workers (Loop-Binding-Lesson, novaberg-lesson_l_loop-binding.md).
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": reiz}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "router",
    )

    try:
        response = model_service.chat.submit_sync(chat_request)
        logger.debug(f"Router RAW: '{response.text[:500]}'")
        routing: dict = response.parsed

        state["needs_memory"]   = routing.get("needs_memory", False)
        state["needs_web"]      = routing.get("needs_web", False)
        state["needs_timeline"] = routing.get("needs_timeline", False)
        state["timeline_query"] = routing.get("timeline_query") or {}
        state["momentum"]       = routing.get("momentum", "mid")

        # Management-Felder
        state["management_action"]     = routing.get("management_action", "") or ""
        state["management_target"]     = routing.get("management_target", "") or ""
        state["management_target_typ"] = routing.get("management_target_typ", "titel") or "titel"

    except (json.JSONDecodeError, KeyError) as fehler:
        logger.warning(f"Router: JSON-Parsing fehlgeschlagen ({fehler}), Fallback")
        state["needs_memory"]          = False
        state["needs_web"]             = False
        state["needs_timeline"]        = False
        state["timeline_query"]        = {}
        state["momentum"]              = "mid"
        state["management_action"]     = ""
        state["management_target"]     = ""
        state["management_target_typ"] = "titel"

    # Guard: Management-Intent ueberschreibt Low-Momentum
    if state["management_action"] and state["momentum"] == "low":
        state["momentum"] = "mid"
        logger.info("Router: Momentum low->mid korrigiert (Management-Intent aktiv)")

    logger.info(
        f"Router: memory={state['needs_memory']}, web={state['needs_web']}, "
        f"timeline={state['needs_timeline']}, momentum={state['momentum']}, "
        f"mgmt={state['management_action']}/{state['management_target']}"
    )

    return state
