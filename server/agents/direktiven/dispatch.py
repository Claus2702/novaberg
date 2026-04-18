"""Dispatch fuer DirektivenAgent — ConversationState <-> AgentState Transformation.

Resume-Flow:
  - Bei status='rueckfrage' wird der pending State in Redis gespeichert (TTL 300s)
  - Bei management_action='resume' wird der Redis-Kontext geladen und der Agent
    mit der User-Antwort + original Kontext neu gestartet
"""

import logging
from agents import AgentRegistry
from agents.base import AgentState, AgentResult
from tools.redis_manager import redis_manager

logger = logging.getLogger("ki_server.agents.direktiven.dispatch")

PENDING_TTL_SECONDS = 300  # 5 Minuten


def dispatch_direktiven(state: dict) -> dict:
    """ConversationState -> DirektivenAgent -> ConversationState."""

    user_id = state.get("user_id", "")
    pending_key = f"pending_agent:{user_id}"

    logger.debug(f"dispatch_direktiven: Einstieg — action='{state.get('management_action')}', "
                 f"target='{state.get('management_target')}'")

    # Resume-Flow
    if state.get("management_action") == "resume":
        pending = redis_manager.get_json(pending_key)
        if pending and pending.get("agent_name") == "direktiven":
            return _handle_resume(state, pending, pending_key)
        else:
            logger.warning("dispatch_direktiven: Resume angefordert aber kein pending State")

    # Normaler Flow
    agent_state: AgentState = {
        "aufgabe": state.get("user_prompt", ""),
        "aufgabe_typ": "workflow",
        "agent_name": "direktiven",
        "kontext": {
            "user_id": user_id,
            "memory_context": state.get("memory_context", ""),
        },
        "parameter": {
            "action": state.get("management_action", ""),
            "target": state.get("management_target", ""),
        },
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }

    logger.debug(f"dispatch_direktiven: AgentState gebaut — "
                 f"aufgabe='{agent_state['aufgabe'][:80]}', action='{agent_state['parameter']['action']}'")

    # Agent ausfuehren
    agent = AgentRegistry.finden("direktiven")
    if not agent:
        logger.error("DirektivenAgent nicht in Registry gefunden")
        result = AgentResult(
            agent_name="direktiven",
            ergebnis=None,
            status="fehler",
            fehler="DirektivenAgent nicht registriert",
        )
        bisherige = state.get("agent_results", [])
        return {"agent_results": bisherige + [result], "agent_name": ""}

    logger.debug("dispatch_direktiven: Agent gefunden, starte invoke()")
    result_state = agent.invoke(agent_state)

    logger.debug(f"dispatch_direktiven: Agent-Ergebnis — status='{result_state.get('status')}', "
                 f"ergebnis='{result_state.get('ergebnis', '?')}'")

    # --- REJECTED: Classify hat Prompt als Nicht-Auftrag erkannt ---
    if result_state.get("status") == "rejected":
        grund = result_state.get("schritte", [{}])[-1].get("ergebnis", "unbekannt")
        logger.info(f"Agent 'direktiven': Classify rejected — {grund}")
        bisherige = list(state.get("agent_results", []))
        result = AgentResult(
            agent_name="direktiven",
            ergebnis=None,
            status="rejected",
        )
        return {"agent_results": bisherige + [result], "agent_name": None}

    # AgentState -> AgentResult
    result = AgentResult(
        agent_name="direktiven",
        ergebnis=result_state.get("ergebnis"),
        status=result_state.get("status", "fehler"),
        fehler=result_state.get("fehler"),
        rueckfrage=result_state.get("rueckfrage"),
        schritte=result_state.get("schritte", []),
        meta={},
    )

    # Bei Rueckfrage: Pending State in Redis speichern
    if result.status == "rueckfrage":
        pending_data = {
            "agent_name": "direktiven",
            "action": state.get("management_action", ""),
            "target": state.get("management_target", ""),
            "rueckfrage": result.rueckfrage,
            "parameter": result_state.get("parameter", agent_state["parameter"]),
        }
        redis_manager.set_json(pending_key, pending_data, ttl_seconds=PENDING_TTL_SECONDS)
        logger.info(f"dispatch_direktiven: Pending Agent gespeichert (TTL={PENDING_TTL_SECONDS}s)")

    return _build_return(state, result)


def _handle_resume(state: dict, pending: dict, pending_key: str) -> dict:
    """Resume-Flow: User hat auf eine Rueckfrage geantwortet."""

    user_answer = state.get("user_prompt", "")
    original_action = pending.get("action", "")
    original_parameter = pending.get("parameter", {})
    rueckfrage = pending.get("rueckfrage", "")

    logger.info(f"dispatch_direktiven: Resume-Flow — action='{original_action}', "
                f"user_answer='{user_answer[:80]}'")

    redis_manager.delete(pending_key)

    agent_state: AgentState = {
        "aufgabe": user_answer,
        "aufgabe_typ": "workflow",
        "agent_name": "direktiven",
        "kontext": {
            "user_id": state.get("user_id", ""),
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

    agent = AgentRegistry.finden("direktiven")
    if not agent:
        logger.error("DirektivenAgent nicht in Registry gefunden (Resume)")
        result = AgentResult(
            agent_name="direktiven", ergebnis=None, status="fehler",
            fehler="DirektivenAgent nicht registriert",
        )
        bisherige = state.get("agent_results", [])
        return {"agent_results": bisherige + [result], "agent_name": ""}

    result_state = agent.invoke(agent_state)

    logger.debug(f"dispatch_direktiven: Resume-Ergebnis — status='{result_state.get('status')}', "
                 f"ergebnis='{result_state.get('ergebnis', '?')}'")

    result = AgentResult(
        agent_name="direktiven",
        ergebnis=result_state.get("ergebnis"),
        status=result_state.get("status", "fehler"),
        fehler=result_state.get("fehler"),
        rueckfrage=result_state.get("rueckfrage"),
        schritte=result_state.get("schritte", []),
        meta={"resume": True},
    )

    if result.status == "rueckfrage":
        pending_data = {
            "agent_name": "direktiven",
            "action": original_action,
            "target": pending.get("target", ""),
            "rueckfrage": result.rueckfrage,
            "parameter": agent_state["parameter"],
        }
        redis_manager.set_json(pending_key, pending_data, ttl_seconds=PENDING_TTL_SECONDS)
        logger.info("dispatch_direktiven: Erneute Rueckfrage — pending State aktualisiert")

    return _build_return(state, result)


def _build_return(state: dict, result: AgentResult) -> dict:
    """Baut das Return-Dict fuer den ConversationState."""
    bisherige = state.get("agent_results", [])

    management_result = ""
    management_detail = ""
    if result.status == "abgeschlossen" and result.ergebnis:
        management_result = str(result.ergebnis)
        management_detail = str(result.ergebnis)
    elif result.status == "rueckfrage" and result.rueckfrage:
        management_result = result.rueckfrage
        management_detail = "Rueckfrage: Disambiguierung erforderlich"
    elif result.status == "fehler" and result.fehler:
        management_result = f"Fehler: {result.fehler}"
        management_detail = result.fehler

    return {
        "agent_results": bisherige + [result],
        "agent_name": "",
        "management_result": management_result,
        "management_detail": management_detail,
    }
