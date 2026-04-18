"""Verdichtung — LLM-Call zur Kern-Erzeugung.

Erzeugt einen konkreten Satz mit ALLEN Namen, Orten, Zahlen.
Inhalt, nicht Emotion.
"""

import logging

from agents.base import AgentState
from config import get_node_config, PROMPTS
from services.llm_provider import get_chat_provider

logger = logging.getLogger("ki_server.agents.kzg.verdichtung")


def _build_verdichtung_prompt() -> str:
    return "\n\n".join([
        PROMPTS["kzg_verdichtung.identity"],
        PROMPTS["kzg_verdichtung.task"],
        PROMPTS["kzg_verdichtung.rules"],
    ])


def verdichten(state: AgentState) -> dict:
    """LLM-Call: Erzeugt den kern aus dem User-Prompt."""

    user_prompt: str = state["parameter"].get("user_prompt", "")
    response:    str = state["parameter"].get("response", "")

    user_message: str = (
        "[LAGEBILD]\n"
        "Hintergrund — dient nur zum Verstaendnis.\n\n"
        f"{response}\n\n"
        "[BEWERTUNGSOBJEKT]\n"
        "Fasse NUR den folgenden Teil zusammen.\n"
        f"Eingabe des Nutzers:\n{user_prompt}"
    )

    node_cfg = get_node_config("kzg_verdichtung")
    provider = get_chat_provider()
    antwort  = provider.chat(
        messages          = [{"role": "user", "content": user_message}],
        system            = _build_verdichtung_prompt(),
        temperature       = node_cfg.get("temperature", 0.1),
        format_json       = False,
        max_output_tokens = node_cfg.get("max_output_tokens", 256),
        caller            = "kzg/verdichtung",
    )

    kern: str = antwort.content.strip()
    logger.info(f"KZG-Verdichtung: kern='{kern}'")

    return {
        "parameter": {
            **state["parameter"],
            "kern": kern,
        },
        "schritte": state["schritte"] + [
            {"node": "verdichten", "ergebnis": "ok", "kern": kern}
        ],
    }
