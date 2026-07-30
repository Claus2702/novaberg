"""Queues — Promotion-Queue, Shadow-Queue und Dirty-Flag.

Befuellt die Redis-Queues fuer Pixie basierend auf Salienz-Schwellen.
"""

import json
import logging

from agents.base import AgentState
from services.shadow_agent.utils import shadow_queue_push, promotion_queue_push
from config import ASSISTANT_USER_ID, redis_client, KZG_SALIENZ_HIGH, PIXIE_AKTIV

logger = logging.getLogger("ki_server.agents.kzg.queues")


# Intention -> Shadow-Aufgabe Mapping
_INTENTION_AUFGABE_MAP: dict[str, str] = {
    "emotionaler_ausdruck": "nachfragen",
    "information_teilen":   "vertiefen",
    "recherche_vertiefen":  "recherche",
    "reflexion":            "recherche",
    "gemeinsam_eruieren":   "recherche",
    "hilferuf":             "nachfragen",
    "information_erfragen": "recherche",
    "feedback_geben":       "",
    "feedback_erfragen":    "",
    "smalltalk":            "",
    "bestaetigung":         "",
    "abschluss":            "",
    "anweisung":            "",
    "planung":              "",
    "humor":                "",
    "widerspruch":          "",
}


def queues_befuellen(state: AgentState) -> dict:
    """Befuellt Promotion-Queue, Shadow-Queue und setzt Dirty-Flag."""
    if not PIXIE_AKTIV:
        logger.debug("kzg.queues: queues_befuellen uebersprungen (PIXIE_AKTIV=False)")
        return {
            "status":   "abgeschlossen",
            "ergebnis": state["parameter"].get("speicher_status", ""),
            "schritte": state["schritte"] + [
                {"node": "queues", "ergebnis": "pixie_off", "aktionen": []}
            ],
        }

    salienz_obj:     dict  = state["parameter"].get("salienz_obj", {})
    speicher_status: str   = state["parameter"].get("speicher_status", "")
    user_id:         str   = state["kontext"].get("user_id", "")
    character_id:    str   = state["kontext"].get("character_id", "")

    salienz:     float = salienz_obj.get("salienz", 0.0)
    intentionen: list  = salienz_obj.get("intentionen", [])
    emotion:     str   = salienz_obj.get("emotion", "neutral")
    modus:       str   = salienz_obj.get("modus", "")

    # Exakte Werte aus speicher.py. `neue_salienz` steht auf der gekruemmten
    # Skala, gegen die auch KZG_SALIENZ_HIGH prueft; `salienz` aus dem
    # salienz_obj ist die rohe Modellbewertung. Ein Fallback auf den rohen Wert
    # waere ein Default, der wie ein echter Wert aussieht — er pruefte gegen ein
    # Tor auf der anderen Skala und traefe es nie. Fehlt der Wert, ist der
    # Speicher-Node nicht gelaufen; das ist ein Fehler, kein Ersatzfall.
    if speicher_status == "neu" and "neue_salienz" not in state["parameter"]:
        logger.error(
            f"KZG-Queues: speicher_status='neu', aber keine neue_salienz im State "
            f"(paar={user_id}:{character_id}) — Promotion und Shadow uebersprungen"
        )
        return {
            "parameter": state["parameter"],
            "schritte": state["schritte"] + [
                {"node": "queues", "ergebnis": "fehler", "grund": "neue_salienz fehlt"}
            ],
        }

    neue_salienz:     float = state["parameter"].get("neue_salienz", 0.0)
    kzg_key:          str   = state["parameter"].get("kzg_key", "")
    kzg_themen_str:   str   = state["parameter"].get("kzg_themen_str", "")
    kzg_dimension:    str   = state["parameter"].get("kzg_dimension", "")

    aktionen: list[str] = []

    # Promotion + Shadow fuer den frisch angelegten Eintrag.
    if speicher_status == "neu":
        kern: str = state["parameter"].get("kern", "")

        if neue_salienz >= KZG_SALIENZ_HIGH:
            # Der Helfer prueft auf einen bestehenden Auftrag fuer denselben
            # Key. `aktionen` meldet nur, was wirklich eingereiht wurde —
            # sonst behauptete die Sammelzeile eine Wirkung, die ausblieb.
            if promotion_queue_push(
                redis_client, user_id, kzg_key, neue_salienz,
                kzg_themen_str, kzg_dimension,
            ):
                aktionen.append("promotion")

            aufgabe: str = _aufgabe_aus_intention(intentionen)
            if aufgabe and user_id != ASSISTANT_USER_ID:
                shadow_queue_push(
                    redis_client=redis_client, user_id=user_id,
                    aufgabe=aufgabe, thema=kzg_themen_str,
                    kontext=kern, prioritaet=neue_salienz,
                    intentionen=intentionen,
                    emotion=emotion, modus=modus,
                )
                aktionen.append(f"shadow_{aufgabe}")

    # Promotion fuer thematisch verstaerkte Nachbarn, die durch den Boost
    # ueber KZG_SALIENZ_HIGH gestiegen sind (PROMO-VERSTAERKT-BLIND-Fix).
    # Laeuft unabhaengig vom speicher_status: ein Turn legt einen neuen
    # Eintrag an UND hebt ggf. mehrere Nachbarn ueber die Schwelle.
    for verstaerkt_eintrag in state["parameter"].get("verstaerkte_eintraege", []):
        if verstaerkt_eintrag["salienz"] >= KZG_SALIENZ_HIGH:
            if promotion_queue_push(
                redis_client, user_id, verstaerkt_eintrag["key"],
                verstaerkt_eintrag["salienz"],
                verstaerkt_eintrag.get("themen", ""), "",
            ):
                aktionen.append("promotion_verstaerkt")

    # Dirty-Flag fuer Hash-Destillation
    redis_client.set(f"hash_dirty:{user_id}:{character_id}", "1")
    aktionen.append("dirty_flag")

    logger.info(f"KZG-Queues: {', '.join(aktionen)}")

    return {
        "status": "abgeschlossen",
        "ergebnis": speicher_status,
        "schritte": state["schritte"] + [
            {"node": "queues", "ergebnis": speicher_status, "aktionen": aktionen}
        ],
    }


def _aufgabe_aus_intention(intentionen: list) -> str:
    if not intentionen:
        return "recherche"
    aufgabe: str = _INTENTION_AUFGABE_MAP.get(intentionen[0], "recherche")
    return aufgabe if aufgabe else ""
