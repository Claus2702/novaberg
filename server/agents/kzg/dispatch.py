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
) -> dict:
    """Verarbeitet alle KZG-Writes als Batch.

    Fuer jedes Segment: Agent aufrufen (Schwelle -> Verdichtung -> Store).
    Am Ende: Session-Turn einmalig annotieren (hoechste Salienz).

    Args:
        state: ConversationState (fuer user_prompt, response, EI-Felder)
        writes: Liste von pending_writes mit ziel="kzg"

    Returns:
        Dict mit:
          kzg_verarbeitet:      Anzahl verarbeiteter Segmente
          kzg_neue_keys:        Redis-Keys der in diesem Lauf neu angelegten
                                KZG-Eintraege, in Segment-Reihenfolge
          kzg_verstaerkte_keys: Redis-Keys der thematisch verstaerkten
                                Nachbar-Eintraege, ueber alle Segmente
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
        return {
            "kzg_verarbeitet":      0,
            "kzg_neue_keys":        [],
            "kzg_verstaerkte_keys": [],
        }

    hoechste_salienz: float = 0.0
    bestes_ergebnis:  dict  = {}
    bester_kern:      str   = ""
    verarbeitet:      int   = 0

    # Transport der geschriebenen Redis-Keys an den aufrufenden Dispatcher.
    # Der Subgraph kennt sie (speicher.py), der Dispatcher bisher nicht.
    new_keys:         list[str] = []
    reinforced_keys:  list[str] = []

    for write_idx, write in enumerate(writes):
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

        # ── Geschriebene Keys einsammeln ──
        # speichern() legt kzg_key und verstaerkte_eintraege im parameter-Kanal
        # ab; queues_befuellen fasst den Kanal nicht an, der Wert steht also
        # noch. Fehlt der Key, gibt es zwei Ursachen: regulaere Ablehnung
        # unter der Salienz-Schwelle (status="abgelehnt", speichern() lief
        # nie) oder ein Defekt im Schreibpfad. Nur Letzteres ist laut.
        result_parameter: dict = result_state.get("parameter", {}) or {}
        result_status:    str  = result_state.get("status", "")
        new_key:          str  = result_parameter.get("kzg_key", "")
        reinforced:       list = result_parameter.get("verstaerkte_eintraege", []) or []

        if new_key:
            new_keys.append(new_key)
        elif result_status == "abgelehnt":
            logger.info(
                "KZG-Dispatch: Segment %d/%d unter Salienz-Schwelle abgelehnt, "
                "kein KZG-Eintrag — turn_id=%s",
                write_idx + 1,
                len(writes),
                state.get("turn_id", ""),
            )
        else:
            logger.warning(
                "KZG-Dispatch: kein kzg_key aus Segment %d/%d — turn_id=%s, "
                "status=%s, speicher_status='%s'",
                write_idx + 1,
                len(writes),
                state.get("turn_id", ""),
                result_status,
                result_parameter.get("speicher_status", ""),
            )

        for verstaerkt_eintrag in reinforced:
            verstaerkt_key: str = verstaerkt_eintrag.get("key", "")
            if verstaerkt_key:
                reinforced_keys.append(verstaerkt_key)
            else:
                logger.warning(
                    "KZG-Dispatch: verstaerkter Eintrag ohne key aus Segment %d/%d — "
                    "turn_id=%s",
                    write_idx + 1,
                    len(writes),
                    state.get("turn_id", ""),
                )

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

    logger.info(
        "KZG-Dispatch: Keys eingesammelt — turn_id=%s, beobachter=%s, "
        "%d neue Keys, %d verstaerkte Keys",
        state.get("turn_id", ""),
        beobachter,
        len(new_keys),
        len(reinforced_keys),
    )

    return {
        "kzg_verarbeitet":      verarbeitet,
        "kzg_neue_keys":        new_keys,
        "kzg_verstaerkte_keys": reinforced_keys,
    }
