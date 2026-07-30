"""Agent-Dispatch — Zentraler Entry-Point für Agent-Aufrufe im Graph.

Liest agent_name aus dem State, findet den agenten-spezifischen Dispatch,
delegiert die ConversationState → AgentState → ConversationState Transformation.

Dieser Node ist generisch — er ist nur ein Router. Die eigentliche
Transformation passiert in der agenten-spezifischen dispatch.py.
"""

import logging
from agents import get_dispatch
from agents.base import AgentResult

logger = logging.getLogger("ki_server.agent_dispatch")


def agent_dispatch_node(state: dict) -> dict:
    """Zentraler Dispatch-Node im Graph. Delegiert an den agenten-spezifischen Dispatch."""
    agent_name = state.get("agent_name", "")
    if not agent_name:
        # Kein Agent angefordert — nichts zu tun
        return {}

    dispatch_fn = get_dispatch(agent_name)
    if not dispatch_fn:
        # Agent existiert, aber kein Dispatch gefunden
        logger.error(f"Kein Dispatch für Agent '{agent_name}' gefunden")
        result = AgentResult(
            agent_name=agent_name,
            ergebnis=None,
            status="fehler",
            fehler=f"Kein Dispatch für Agent '{agent_name}' registriert",
        )
        bisherige = state.get("agent_results", [])
        return {
            "agent_results": bisherige + [result],
            "agent_name": "",  # Reset — Planner soll neu entscheiden
        }

    logger.info(f"Agent-Dispatch: {agent_name}")
    try:
        return dispatch_fn(state)
    except Exception as e:
        logger.exception(f"{type(e).__name__}: Agent-Dispatch Fehler für '{agent_name}'")
        result = AgentResult(
            agent_name=agent_name,
            ergebnis=None,
            status="fehler",
            fehler=str(e),
        )
        bisherige = state.get("agent_results", [])
        return {
            "agent_results": bisherige + [result],
            "agent_name": "",
        }
