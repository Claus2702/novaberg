"""Queues — Promotion-Queue, Shadow-Queue und Dirty-Flag.

Befuellt die Redis-Queues fuer Pixie basierend auf Salienz-Schwellen.
"""

import json
import logging

from agents.base import AgentState
from memory.kzg import PROMOTION_THRESHOLD
from services.shadow_agent.utils import shadow_queue_push
from config import ASSISTANT_USER_ID, redis_client, KZG_SALIENZ_HIGH, KZG_VERTIEFUNG_HAEUFIGKEIT

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

    salienz_obj:     dict  = state["parameter"].get("salienz_obj", {})
    speicher_status: str   = state["parameter"].get("speicher_status", "")
    user_id:         str   = state["kontext"].get("user_id", "")

    salienz:     float = salienz_obj.get("salienz", 0.0)
    intentionen: list  = salienz_obj.get("intentionen", [])
    emotion:     str   = salienz_obj.get("emotion", "neutral")
    modus:       str   = salienz_obj.get("modus", "")

    # Exakte Werte aus speicher.py
    neue_salienz:     float = state["parameter"].get("neue_salienz", salienz)
    neue_haeufigkeit: int   = state["parameter"].get("neue_haeufigkeit", 1)
    kzg_key:          str   = state["parameter"].get("kzg_key", "")
    kzg_themen_str:   str   = state["parameter"].get("kzg_themen_str", "")
    kzg_dimension:    str   = state["parameter"].get("kzg_dimension", "")

    aktionen: list[str] = []

    if speicher_status == "verstaerkt":
        # Promotion bei hoher Salienz
        if neue_salienz >= PROMOTION_THRESHOLD:
            existing = state["parameter"].get("existing", {})
            redis_client.rpush(f"queue:{user_id}", json.dumps({
                "aufgabe":   "lzg_promotion",
                "key":       kzg_key,
                "salienz":   neue_salienz,
                "themen":    existing.get("themen", ""),
                "dimension": existing.get("dimension", ""),
            }))
            aktionen.append("promotion")

        # Shadow bei haeufiger Wiederholung
        if neue_haeufigkeit >= KZG_VERTIEFUNG_HAEUFIGKEIT and neue_salienz >= KZG_SALIENZ_HIGH and user_id != ASSISTANT_USER_ID:
            existing = state["parameter"].get("existing", {})
            shadow_queue_push(
                redis_client=redis_client, user_id=user_id,
                aufgabe="vertiefen", thema=existing.get("themen", ""),
                kontext=existing.get("inhalt", ""),
                prioritaet=neue_salienz,
                intentionen=intentionen, emotion=emotion, modus=modus,
            )
            aktionen.append("shadow_vertiefen")

    elif speicher_status == "neu":
        kern: str = state["parameter"].get("kern", "")

        if neue_salienz >= KZG_SALIENZ_HIGH:
            redis_client.rpush(f"queue:{user_id}", json.dumps({
                "aufgabe":   "lzg_promotion",
                "key":       kzg_key,
                "salienz":   neue_salienz,
                "themen":    kzg_themen_str,
                "dimension": kzg_dimension,
            }))
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

    # Dirty-Flag fuer Hash-Destillation
    redis_client.set(f"hash_dirty:{user_id}", "1")
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
