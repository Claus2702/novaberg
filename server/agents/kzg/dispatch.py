"""Dispatch fuer KzgAgent — Salienz-Ergebnis -> AgentState -> Batch-Verarbeitung.

Wird vom Dispatcher aufgerufen (nicht vom Planner wie NotizenAgent).
Verarbeitet alle KZG-Writes als Batch. Annotiert den Session-Turn
einmalig fuer das Segment mit der hoechsten Salienz.
"""

import logging

from agents import AgentRegistry
from agents.base import AgentState
from config import ASSISTANT_USER_ID, redis_client as cfg_redis_client

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

    user_id:      str = state.get("user_id", "")
    character_id: str = state.get("character_id", ASSISTANT_USER_ID)

    # Beobachter: User-Graph (Pfad 1) vs. Character-Graph (Pfad 2).
    # ei_calc_rolle ist "user" im HumanGraph und "character" im CharacterGraph.
    beobachter: str = "assistant" if state.get("ei_calc_rolle") == "character" else "user"

    logger.info(f"KZG-Dispatch: Paar={user_id}:{character_id}, Beobachter={beobachter}")

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

        # EI-Felder aus Personality-Klassen einfuegen. Assistant-Beobachter
        # liest aus internal (Novas Wahrnehmung der eigenen Antwort), sonst
        # aus external (User-Wahrnehmung). Behebt PFAD2-EMO-MIX strukturell.
        if beobachter == "assistant":
            quelle = state.get("internal")
        else:
            quelle = state.get("external")

        salienz_obj["arousal"]            = quelle.emotion.arousal              if quelle else 0.5
        salienz_obj["emotions_vektor"]    = quelle.emotion.emotions_vector      if quelle else ""
        salienz_obj["sprach_stil"]        = quelle.emotion.language_style       if quelle else "neutral"
        salienz_obj["beziehungs_dynamik"] = quelle.emotion.relationship_dynamic if quelle else "neutral"
        salienz_obj["tone"]               = quelle.emotion.tone                 if quelle else "sachlich"

        # AgentState bauen
        agent_state: AgentState = {
            "aufgabe":     "kzg_verarbeitung",
            "aufgabe_typ": "workflow",
            "agent_name":  "kzg",
            "kontext": {
                "user_id":      user_id,
                "character_id": character_id,
                "beobachter":   beobachter,
                "embed_client": embed_client,
                "embed_model":  embed_model,
                "turn_id":      state.get("turn_id", ""),
                # Clipboard: vom TimelineAgent in diesem Turn gesetzte ID;
                # vom magnete_aufloesen-Node uebernommen statt eigenen
                # Erinnerungs-Anker anzulegen.
                "timeline_id":  state.get("timeline_id"),
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

    # ── Kern in State schreiben (Dispatcher schreibt den Session-Turn komplett) ──
    if bestes_ergebnis and bester_kern:
        state["session_turn_kern"] = bester_kern
        logger.info(f"KZG-Dispatch: Kern in State geschrieben — '{bester_kern[:60]}'")

    logger.info(f"KZG-Dispatch: {verarbeitet} Segmente verarbeitet")

    return {"kzg_verarbeitet": verarbeitet}
