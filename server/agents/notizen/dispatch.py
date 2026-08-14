"""Dispatch fuer NotizenAgent — ConversationState <-> AgentState Transformation.

Erweiterung AGT1-Fix:
  - Bei status='rueckfrage' wird der pending State in Redis gespeichert (TTL 300s)
  - Bei management_action='resume' wird der Redis-Kontext geladen und der Agent
    mit der User-Antwort + original Kontext neu gestartet
"""

import json
import logging
from agents import AgentRegistry
from agents.base import AgentState, AgentResult
from graph.reiz import reiz_text
from tools.redis_manager import redis_manager

logger = logging.getLogger("ki_server.agents.notizen.dispatch")

PENDING_TTL_SECONDS = 300  # 5 Minuten


def dispatch_notizen(state: dict) -> dict:
    """ConversationState -> NotizenAgent -> ConversationState."""
    user_id = state.get("user_id", "")
    pending_key = f"pending_agent:{user_id}"

    logger.debug(f"dispatch_notizen: Einstieg — action='{state.get('management_action')}', target='{state.get('management_target')}'")

    # ── Resume-Flow: Agent wartet auf Antwort ──────
    if state.get("management_action") == "resume":
        pending = redis_manager.get_json(pending_key)
        if pending and pending.get("agent_name") == "notizen":
            return _handle_resume(state, pending, pending_key)
        else:
            logger.warning("dispatch_notizen: Resume angefordert aber kein pending State für 'notizen'")

    # ── Normaler Flow ──────────────────────────────

    # 1. ConversationState -> AgentState
    agent_state: AgentState = {
        "aufgabe": reiz_text(state),
        "aufgabe_typ": "workflow",
        "agent_name": "notizen",
        "kontext": {
            "user_id": user_id,
            "character_id": state.get("character_id", ""),
            "memory_context": state.get("memory_context", ""),
        },
        "parameter": {
            "action": state.get("management_action", ""),
            "target": state.get("management_target", ""),
            "target_typ": state.get("management_target_typ", "titel"),
        },
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }

    logger.debug(f"dispatch_notizen: AgentState gebaut — aufgabe='{agent_state['aufgabe'][:80]}', "
                 f"action='{agent_state['parameter']['action']}', target='{agent_state['parameter']['target']}', "
                 f"user_id='{agent_state['kontext']['user_id']}'")

    # 2. Agent ausfuehren
    agent = AgentRegistry.finden("notizen")
    if not agent:
        logger.error("NotizenAgent nicht in Registry gefunden")
        result = AgentResult(
            agent_name="notizen",
            ergebnis=None,
            status="fehler",
            fehler="NotizenAgent nicht registriert",
        )
        bisherige = state.get("agent_results", [])
        return {"agent_results": bisherige + [result], "agent_name": ""}

    logger.debug("dispatch_notizen: Agent gefunden, starte invoke()")
    result_state = agent.invoke(agent_state)

    logger.debug(f"dispatch_notizen: Agent-Ergebnis — status='{result_state.get('status')}', "
                 f"ergebnis='{result_state.get('ergebnis', '?')}', "
                 f"fehler='{result_state.get('fehler')}', "
                 f"rueckfrage='{result_state.get('rueckfrage')}', "
                 f"schritte={len(result_state.get('schritte', []))}")

    # --- REJECTED: Classify hat Prompt als Nicht-Auftrag erkannt ---
    if result_state.get("status") == "rejected":
        grund = result_state.get("schritte", [{}])[-1].get("ergebnis", "unbekannt")
        logger.info(f"Agent 'notizen': Classify rejected — {grund}")
        bisherige = list(state.get("agent_results", []))
        result = AgentResult(
            agent_name="notizen",
            ergebnis=None,
            status="rejected",
        )
        return {"agent_results": bisherige + [result], "agent_name": None}

    # 3. AgentState -> AgentResult
    result = AgentResult(
        agent_name="notizen",
        ergebnis=result_state.get("ergebnis"),
        status=result_state.get("status", "fehler"),
        fehler=result_state.get("fehler"),
        rueckfrage=result_state.get("rueckfrage"),
        schritte=result_state.get("schritte", []),
        meta={},
    )

    # 4. Bei Rückfrage: Pending State in Redis speichern
    if result.status == "rueckfrage":
        pending_data = {
            "agent_name": "notizen",
            "action": state.get("management_action", ""),
            "target": state.get("management_target", ""),
            "rueckfrage": result.rueckfrage,
            "parameter": result_state.get("parameter", agent_state["parameter"]),
        }
        redis_manager.set_json(pending_key, pending_data, ttl_seconds=PENDING_TTL_SECONDS)
        logger.info(f"dispatch_notizen: Pending Agent gespeichert in Redis (TTL={PENDING_TTL_SECONDS}s)")

    # 5. AgentResult in ConversationState schreiben
    return _build_return(state, result)


def _handle_resume(state: dict, pending: dict, pending_key: str) -> dict:
    """Resume-Flow: User hat auf eine Rückfrage geantwortet.

    Baut einen AgentState mit der User-Antwort + dem originalen Kontext
    aus Redis und startet den Agent erneut.
    """
    user_answer = state.get("user_prompt", "")
    original_action = pending.get("action", "")
    original_parameter = pending.get("parameter", {})
    rueckfrage = pending.get("rueckfrage", "")

    logger.info(f"dispatch_notizen: Resume-Flow — action='{original_action}', "
                f"user_answer='{user_answer[:80]}'")

    # Redis aufräumen (BEVOR der Agent läuft — verhindert Endlosschleifen)
    redis_manager.delete(pending_key)
    logger.debug(f"dispatch_notizen: Pending Key '{pending_key}' gelöscht")

    # Resume-AgentState bauen
    agent_state: AgentState = {
        "aufgabe": user_answer,
        "aufgabe_typ": "workflow",
        "agent_name": "notizen",
        "kontext": {
            "user_id": state.get("user_id", ""),
            "character_id": state.get("character_id", ""),
            "memory_context": state.get("memory_context", ""),
        },
        "parameter": {
            **original_parameter,
            "resume": True,
            "user_answer": user_answer,
            "original_rueckfrage": rueckfrage,
        },
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }

    logger.debug(f"dispatch_notizen: Resume-AgentState — action='{original_action}', "
                 f"resume=True, parameter_keys={list(agent_state['parameter'].keys())}")

    # Agent ausführen
    agent = AgentRegistry.finden("notizen")
    if not agent:
        logger.error("NotizenAgent nicht in Registry gefunden (Resume)")
        result = AgentResult(
            agent_name="notizen", ergebnis=None, status="fehler",
            fehler="NotizenAgent nicht registriert",
        )
        bisherige = state.get("agent_results", [])
        return {"agent_results": bisherige + [result], "agent_name": ""}

    result_state = agent.invoke(agent_state)

    logger.debug(f"dispatch_notizen: Resume-Ergebnis — status='{result_state.get('status')}', "
                 f"ergebnis='{result_state.get('ergebnis', '?')}'")

    # AgentResult bauen
    result = AgentResult(
        agent_name="notizen",
        ergebnis=result_state.get("ergebnis"),
        status=result_state.get("status", "fehler"),
        fehler=result_state.get("fehler"),
        rueckfrage=result_state.get("rueckfrage"),
        schritte=result_state.get("schritte", []),
        meta={"resume": True},
    )

    # Erneute Rückfrage? Wieder in Redis speichern
    if result.status == "rueckfrage":
        pending_data = {
            "agent_name": "notizen",
            "action": original_action,
            "target": pending.get("target", ""),
            "rueckfrage": result.rueckfrage,
            "parameter": agent_state["parameter"],
        }
        redis_manager.set_json(pending_key, pending_data, ttl_seconds=PENDING_TTL_SECONDS)
        logger.info("dispatch_notizen: Erneute Rückfrage — pending State aktualisiert")

    return _build_return(state, result)


def _build_return(state: dict, result: AgentResult) -> dict:
    """Baut das Return-Dict für den ConversationState aus einem AgentResult."""
    bisherige = state.get("agent_results", [])

    management_result = ""
    management_detail = ""
    if result.status == "abgeschlossen" and result.ergebnis:
        management_result = str(result.ergebnis)
        management_detail = str(result.ergebnis)
    elif result.status == "rueckfrage" and result.rueckfrage:
        management_result = result.rueckfrage
        management_detail = "Rückfrage: Disambiguierung erforderlich"
    elif result.status == "fehler" and result.fehler:
        management_result = f"Fehler: {result.fehler}"
        management_detail = result.fehler

    logger.debug(f"dispatch_notizen: AgentResult — status='{result.status}', "
                 f"management_result='{management_result[:100]}', "
                 f"management_detail='{management_detail[:100]}'")

    return {
        "agent_results": bisherige + [result],
        "agent_name": "",  # Reset — Planner darf neu entscheiden
        "management_result": management_result,
        "management_detail": management_detail,
    }
