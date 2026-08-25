"""Dispatch fuer CharakterIdentitaetAgent — ConversationState <-> AgentState Transformation.

Resume-Flow:
  - Bei status='rueckfrage' wird der pending State in Redis gespeichert (TTL 300s)
  - Bei management_action='resume' wird der Redis-Kontext geladen und der Agent
    mit der User-Antwort + original Kontext neu gestartet
"""

import logging

from agents import AgentRegistry
from agents.base import AgentResult, AgentState, Korrektur
from graph.reiz import reiz_text
from tools.redis_manager import redis_manager

logger = logging.getLogger("ki_server.agents.charakter_identitaet.dispatch")

PENDING_TTL_SECONDS = 300  # 5 Minuten


def dispatch_charakter_identitaet(state: dict) -> dict:
    """ConversationState -> CharakterIdentitaetAgent -> ConversationState."""
    user_id = state.get("user_id", "")
    pending_key = f"pending_agent:{user_id}"

    logger.debug(f"dispatch_charakter_identitaet: Einstieg — action='{state.get('management_action')}', "
                 f"target='{state.get('management_target')}'")

    # Resume-Flow
    if state.get("management_action") == "resume":
        pending = redis_manager.get_json(pending_key)
        if pending and pending.get("agent_name") == "charakter_identitaet":
            return _handle_resume(state, pending, pending_key)
        else:
            logger.warning(
                "dispatch_charakter_identitaet: Resume angefordert aber kein pending State"
            )

    # Normaler Flow
    agent_state: AgentState = {
        "aufgabe": reiz_text(state),
        "aufgabe_typ": "workflow",
        "agent_name": "charakter_identitaet",
        "kontext": {
            "user_id": user_id,
            "character_id": state.get("character_id", ""),
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

    logger.debug(f"dispatch_charakter_identitaet: AgentState gebaut — "
                 f"aufgabe='{agent_state['aufgabe'][:80]}', action='{agent_state['parameter']['action']}'")

    # Agent ausfuehren
    agent = AgentRegistry.finden("charakter_identitaet")
    if not agent:
        logger.error("CharakterIdentitaetAgent nicht in Registry gefunden")
        result = AgentResult(
            agent_name="charakter_identitaet",
            ergebnis=None,
            status="fehler",
            fehler="CharakterIdentitaetAgent nicht registriert",
        )
        bisherige = state.get("agent_results", [])
        return {"agent_results": bisherige + [result], "agent_name": ""}

    logger.debug("dispatch_charakter_identitaet: Agent gefunden, starte invoke()")
    result_state = agent.invoke(agent_state)

    logger.debug(f"dispatch_charakter_identitaet: Agent-Ergebnis — status='{result_state.get('status')}', "
                 f"ergebnis='{result_state.get('ergebnis', '?')}'")

    # --- REJECTED: Classify hat Prompt als Nicht-Auftrag erkannt ---
    if result_state.get("status") == "rejected":
        grund = result_state.get("schritte", [{}])[-1].get("ergebnis", "unbekannt")
        logger.info(f"Agent 'charakter_identitaet': Classify rejected — {grund}")
        bisherige = list(state.get("agent_results", []))
        # Der vierte Ausgang: eine Ablehnung mit Gegenangebot statt einer
        # Sackgasse. Der Vorschlag geht an den Auftraggeber und NICHT in
        # den Bestand — ein Dienst, der seine eigene Korrektur ausfuehrt,
        # hat den Auftrag ersetzt statt ihn beurteilt.
        result = AgentResult(
            agent_name="charakter_identitaet",
            ergebnis=None,
            status="abgelehnt",
            korrektur=Korrektur(
                befund="Das habe ich nicht als Auftrag an mich verstanden.",
                beleg=f"Klassifikation: {grund}",
                vorschlag=(
                    "Beschreibe den Zug als dauerhafte Eigenschaft, etwa 'sei grundsaetzlich "
                    "knapper in deinen "
                    "Antworten'."
                ),
            ),
        )
        return {"agent_results": bisherige + [result], "agent_name": None}

    # AgentState -> AgentResult
    result = AgentResult(
        agent_name="charakter_identitaet",
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
            "agent_name": "charakter_identitaet",
            "action": state.get("management_action", ""),
            "target": state.get("management_target", ""),
            "rueckfrage": result.rueckfrage,
            "parameter": result_state.get("parameter", agent_state["parameter"]),
        }
        redis_manager.set_json(pending_key, pending_data, ttl_seconds=PENDING_TTL_SECONDS)
        logger.info(
            f"dispatch_charakter_identitaet: Pending Agent gespeichert (TTL={PENDING_TTL_SECONDS}s)"
        )

    return _build_return(state, result)


def _handle_resume(state: dict, pending: dict, pending_key: str) -> dict:
    """Resume-Flow: User hat auf eine Rueckfrage geantwortet."""
    user_answer = state.get("user_prompt", "")
    original_action = pending.get("action", "")
    original_parameter = pending.get("parameter", {})
    rueckfrage = pending.get("rueckfrage", "")

    logger.info(f"dispatch_charakter_identitaet: Resume-Flow — action='{original_action}', "
                f"user_answer='{user_answer[:80]}'")

    redis_manager.delete(pending_key)

    agent_state: AgentState = {
        "aufgabe": user_answer,
        "aufgabe_typ": "workflow",
        "agent_name": "charakter_identitaet",
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

    agent = AgentRegistry.finden("charakter_identitaet")
    if not agent:
        logger.error("CharakterIdentitaetAgent nicht in Registry gefunden (Resume)")
        result = AgentResult(
            agent_name="charakter_identitaet", ergebnis=None, status="fehler",
            fehler="CharakterIdentitaetAgent nicht registriert",
        )
        bisherige = state.get("agent_results", [])
        return {"agent_results": bisherige + [result], "agent_name": ""}

    result_state = agent.invoke(agent_state)

    result = AgentResult(
        agent_name="charakter_identitaet",
        ergebnis=result_state.get("ergebnis"),
        status=result_state.get("status", "fehler"),
        fehler=result_state.get("fehler"),
        rueckfrage=result_state.get("rueckfrage"),
        schritte=result_state.get("schritte", []),
        meta={"resume": True},
    )

    if result.status == "rueckfrage":
        pending_data = {
            "agent_name": "charakter_identitaet",
            "action": original_action,
            "target": pending.get("target", ""),
            "rueckfrage": result.rueckfrage,
            "parameter": agent_state["parameter"],
        }
        redis_manager.set_json(pending_key, pending_data, ttl_seconds=PENDING_TTL_SECONDS)
        logger.info(
            "dispatch_charakter_identitaet: Erneute Rueckfrage — pending State aktualisiert"
        )

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
        management_detail = "Rueckfrage: Konsolidierung erforderlich"
    elif result.status == "fehler" and result.fehler:
        management_result = f"Fehler: {result.fehler}"
        management_detail = result.fehler

    return {
        "agent_results": bisherige + [result],
        "agent_name": "",
        "management_result": management_result,
        "management_detail": management_detail,
    }
