"""Verdichtung — LLM-Call zur Kern-Erzeugung.

Erzeugt einen konkreten Satz mit ALLEN Namen, Orten, Zahlen.
Inhalt, nicht Emotion.
"""

import logging

from agents.base import AgentState
from config import get_node_config, PROMPTS
from services.model_services import model_service, ChatRequest

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

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G2) ──
    # verdichten() laeuft im KzgAgent-Subgraphen, der vom CharacterGraph-
    # dispatcher-Node aus aufgerufen wird; der CharacterGraph wiederum
    # laeuft in services/event_consumer.py via asyncio.to_thread(...) im
    # Worker-Thread. Kein Event-Loop im aufrufenden Thread → submit_sync
    # bruckt in den Worker-Loop (Loop-Binding-Lesson). format_json war
    # vorher explizit False (Fliesstext) → expect_json bleibt False.
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": user_message}],
        system            = _build_verdichtung_prompt(),
        temperature       = node_cfg.get("temperature", 0.1),
        max_output_tokens = node_cfg.get("max_output_tokens", 256),
        caller            = "kzg/verdichtung",
    )
    response = model_service.chat.submit_sync(chat_request)

    kern: str = response.text.strip()
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
