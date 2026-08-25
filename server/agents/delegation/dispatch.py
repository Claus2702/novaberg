"""Dispatch fuer DelegationsAgent — Back-end-Dispatch via Dispatcher.

Wird vom Dispatcher aufgerufen wenn mindestens ein Trigger zuendet.
Baut AgentState aus ConversationState, ruft den Agent auf,
und schreibt das Beruhigungs-Signal als AgentResult in den State.
"""

import logging

from agents import AgentRegistry
from agents.base import AgentResult, AgentState
from config import DELEGATION_SIGNALE, DELEGATION_SIGNALE_FALLBACK
from graph.reiz import reiz_text

logger = logging.getLogger("ki_server.agents.delegation.dispatch")


def _beruhigungs_signal(trigger: str, emotions_vektor: str) -> str:
    """Situationsbeschreibung fuer den Responder.

    Primaer: (vektor, trigger) Kombination aus DELEGATION_SIGNALE.
    Fallback: Trigger-Default aus DELEGATION_SIGNALE_FALLBACK.
    """
    signal: str = DELEGATION_SIGNALE.get((emotions_vektor, trigger), "")
    if signal:
        return signal
    return DELEGATION_SIGNALE_FALLBACK.get(trigger, "")


def dispatch_delegation(state: dict) -> None:
    """Baut AgentState, ruft DelegationsAgent auf, schreibt AgentResult.

    Mutiert state["agent_results"] direkt (wie dispatch_kzg).

    Args:
        state: ConversationState
    """
    user_id: str = state.get("user_id", "")
    trigger: str = state.get("_delegation_trigger", "")
    salienz_obj: dict = state.get("salienz_obj_aktuell", {})

    agent = AgentRegistry.finden("delegation")
    if not agent:
        logger.error("DelegationsAgent nicht in Registry gefunden")
        return

    # Session-Turns (letzte 10) fuer Seiten-Auszug
    session_turns: list = state.get("session_turns", [])[-10:]

    # Delegations-Trigger arbeitet immer mit User-Werten (external).
    external = state.get("external")

    # AgentState bauen
    agent_state: AgentState = {
        "aufgabe":     "delegation",
        "aufgabe_typ": "workflow",
        "agent_name":  "delegation",
        "kontext": {
            "user_id":      user_id,
            "character_id": state.get("character_id", ""),
        },
        "parameter": {
            "salienz_obj":         salienz_obj,
            "trigger":             trigger,
            # Der Reiz dieses Turns. Der Feldname bleibt, weil er so in die
            # persistierte Akte wandert; auf einem Impuls-Turn traegt er
            # Novas eigenen Gedanken statt einer Aeusserung des Menschen.
            "user_prompt":         reiz_text(state),
            "response":            state.get("response", ""),
            "current_emotion":     external.emotion.emotion              if external else "neutral",
            "current_arousal":     external.emotion.arousal              if external else 0.5,
            "emotions_vektor":     external.emotion.emotions_vector      if external else "",
            "emotions_verlauf":    state.get("emotions_verlauf", []),
            "sprach_stil":         external.emotion.language_style       if external else "neutral",
            "beziehungs_dynamik":  external.emotion.relationship_dynamic if external else "neutral",
            "tone":                external.emotion.tone                 if external else "sachlich",
            "gespraechs_modus":    external.emotion.mode                 if external else "",
            "user_intentionen":    state.get("user_intentionen", []),
            "session_turns":       session_turns,
        },
        "schritte": [],
        "ergebnis": None,
        "status":     "laufend",
        "rueckfrage": None,
        "fehler":     None,
    }

    # Agent ausfuehren
    result_state = agent.invoke(agent_state)

    # Anreicherung erkennen
    ergebnis_dict: dict = result_state.get("ergebnis") or {}
    anreicherung: bool = ergebnis_dict.get("aktion") == "angereichert" if isinstance(ergebnis_dict, dict) else False

    # Beruhigungs-Signal: nur bei neuer Akte, nicht bei Anreicherung
    signal: str = ""
    if not anreicherung:
        emotions_vektor: str = external.emotion.emotions_vector if external else ""
        signal = _beruhigungs_signal(trigger, emotions_vektor)

    # AgentResult bauen
    agent_result = AgentResult(
        agent_name="delegation",
        ergebnis=signal,
        status=result_state.get("status", "abgeschlossen"),
        meta={
            "trigger": trigger,
            "anreicherung": anreicherung,
            "akte_id": ergebnis_dict.get("akte_id") if isinstance(ergebnis_dict, dict) else None,
        },
    )

    # In State schreiben
    if "agent_results" not in state or state["agent_results"] is None:
        state["agent_results"] = []
    state["agent_results"].append(agent_result)

    logger.info(
        f"DelegationsAgent: trigger={trigger}, anreicherung={anreicherung}, "
        f"akte_id={agent_result.meta.get('akte_id')}"
    )
