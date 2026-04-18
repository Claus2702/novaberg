"""Dispatch fuer KzgAgent — Salienz-Ergebnis -> AgentState -> Batch-Verarbeitung.

Wird vom Dispatcher aufgerufen (nicht vom Planner wie NotizenAgent).
Verarbeitet alle KZG-Writes als Batch. Annotiert den Session-Turn
einmalig fuer das Segment mit der hoechsten Salienz.
"""

import logging

from agents import AgentRegistry
from agents.base import AgentState
from memory.session import session_turn_annotate
from config import redis_client as cfg_redis_client

logger = logging.getLogger("ki_server.agents.kzg.dispatch")


def dispatch_kzg(
    state: dict,
    writes: list[dict],
    embed_client=None,
    embed_model: str = "",
) -> dict:
    """Verarbeitet alle KZG-Writes als Batch.

    Fuer jedes Segment: Agent aufrufen (Schwelle -> Verdichtung -> Store).
    Am Ende: Session-Turn einmalig annotieren (hoechste Salienz).

    Args:
        state: ConversationState (fuer user_prompt, response, EI-Felder)
        writes: Liste von pending_writes mit ziel="kzg"
        embed_client: Ollama-Client fuer Embeddings
        embed_model: Embedding-Modell-Name

    Returns:
        Dict mit kzg_verarbeitet (Anzahl verarbeiteter Segmente)
    """

    user_id: str = state.get("user_id", "")
    agent = AgentRegistry.finden("kzg")

    if not agent:
        logger.error("KzgAgent nicht in Registry gefunden")
        return {"kzg_verarbeitet": 0}

    hoechste_salienz: float = 0.0
    bestes_ergebnis:  dict  = {}
    bester_kern:      str   = ""
    verarbeitet:      int   = 0

    for write in writes:
        daten:       dict = write.get("daten", {})
        salienz_obj: dict = daten.get("salienz_obj", {})

        if not salienz_obj:
            logger.warning("KZG-Dispatch: salienz_obj fehlt — uebersprungen")
            continue

        # EI-Felder aus State in salienz_obj einfuegen
        salienz_obj["arousal"]            = state.get("current_arousal", 0.5)
        salienz_obj["emotions_vektor"]    = state.get("emotions_vektor", "")
        salienz_obj["sprach_stil"]        = state.get("sprach_stil", "neutral")
        salienz_obj["beziehungs_dynamik"] = state.get("beziehungs_dynamik", "neutral")
        salienz_obj["tone"]               = state.get("tone", "sachlich")

        # AgentState bauen
        agent_state: AgentState = {
            "aufgabe":     "kzg_verarbeitung",
            "aufgabe_typ": "workflow",
            "agent_name":  "kzg",
            "kontext": {
                "user_id":      user_id,
                "embed_client": embed_client,
                "embed_model":  embed_model,
            },
            "parameter": {
                "salienz_obj":  salienz_obj,
                "user_prompt":  state.get("user_prompt", ""),
                "response":     state.get("response", ""),
            },
            "schritte": [],
            "ergebnis": None,
            "status":     "laufend",
            "rueckfrage": None,
            "fehler":     None,
        }

        # Agent ausfuehren
        result_state = agent.invoke(agent_state)
        verarbeitet += 1

        # Hoechste Salienz tracken fuer Session-Annotation
        score: float = salienz_obj.get("salienz", 0.0)
        if score > hoechste_salienz and result_state.get("status") != "abgelehnt":
            hoechste_salienz = score
            bestes_ergebnis  = salienz_obj
            bester_kern      = result_state.get("parameter", {}).get("kern", "")

    # ── Session-Turn einmalig annotieren (hoechstes Segment) ──
    if bestes_ergebnis and bester_kern:
        session_turn_annotate(
            redis_client       = cfg_redis_client,
            user_id            = user_id,
            intentionen        = bestes_ergebnis.get("intentionen", []),
            emotion            = state.get("current_emotion", "neutral"),
            modus              = bestes_ergebnis.get("modus", ""),
            kern               = bester_kern,
            arousal            = state.get("current_arousal", 0.5),
            emotions_vektor    = state.get("emotions_vektor", ""),
            sprach_stil        = state.get("sprach_stil", "neutral"),
            beziehungs_dynamik = state.get("beziehungs_dynamik", "neutral"),
            tone               = state.get("tone", "sachlich"),
            themen             = bestes_ergebnis.get("themen", []),
        )
        logger.info(f"KZG-Dispatch: Session annotiert — kern='{bester_kern[:60]}'")

    logger.info(f"KZG-Dispatch: {verarbeitet} Segmente verarbeitet")

    return {"kzg_verarbeitet": verarbeitet}
