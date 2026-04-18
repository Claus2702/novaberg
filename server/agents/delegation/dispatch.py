"""Dispatch fuer DelegationsAgent — Back-end-Dispatch via Dispatcher.

Wird vom Dispatcher aufgerufen wenn mindestens ein Trigger zuendet.
Baut AgentState aus ConversationState, ruft den Agent auf,
und schreibt das Beruhigungs-Signal als AgentResult in den State.
"""

import logging

from agents import AgentRegistry
from agents.base import AgentState, AgentResult
from config import DELEGATION_SIGNALE, DELEGATION_SIGNALE_FALLBACK

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


def dispatch_delegation(
    state: dict,
    embed_client=None,
    embed_model: str = "",
) -> None:
    """Baut AgentState, ruft DelegationsAgent auf, schreibt AgentResult.

    Mutiert state["agent_results"] direkt (wie dispatch_kzg).

    Args:
        state: ConversationState
        embed_client: Ollama-Client fuer Embeddings
        embed_model: Embedding-Modell-Name
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

    # AgentState bauen
    agent_state: AgentState = {
        "aufgabe":     "delegation",
        "aufgabe_typ": "workflow",
        "agent_name":  "delegation",
        "kontext": {
            "user_id":      user_id,
            "embed_client": embed_client,
            "embed_model":  embed_model,
        },
        "parameter": {
            "salienz_obj":         salienz_obj,
            "trigger":             trigger,
            "user_prompt":         state.get("user_prompt", ""),
            "response":            state.get("response", ""),
            "current_emotion":     state.get("current_emotion", "neutral"),
            "current_arousal":     state.get("current_arousal", 0.5),
            "emotions_vektor":     state.get("emotions_vektor", ""),
            "emotions_verlauf":    state.get("emotions_verlauf", []),
            "sprach_stil":         state.get("sprach_stil", "neutral"),
            "beziehungs_dynamik":  state.get("beziehungs_dynamik", "neutral"),
            "tone":                state.get("tone", "sachlich"),
            "gespraechs_modus":    state.get("gespraechs_modus", ""),
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
        emotions_vektor: str = state.get("emotions_vektor", "")
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
