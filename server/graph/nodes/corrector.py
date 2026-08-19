"""
Corrector Node — Überarbeitet die Antwort basierend auf Tribunal-Feedback.
Wird nur aufgerufen wenn das Tribunal warnung oder ablehnen meldet.
"""

import logging

from graph.reiz  import reiz_text
from graph.state import ConversationState
from graph.antwort_spur import antwort_setzen
from config import get_node_config, PROMPTS
from services.model_services import model_service, ChatRequest

logger = logging.getLogger("ki_server.corrector")


def correct(state: ConversationState) -> ConversationState:
    """Überarbeitet die Antwort basierend auf Tribunal-Feedback."""
    state["correction_round"] += 1

    logger.info(f"Corrector: Korrektur-Runde {state['correction_round']} "
                f"(verdict={state['tribunal_verdict']})")

    external = state.get("external")
    user_intent: str = external.emotion.intent if external else "smalltalk"
    user_tone:   str = external.emotion.tone   if external else "sachlich"

    korrektur_prompt: str = (
        f"═══ LAGEBILD (Hintergrund) ═══\n"
        f"Intent: {user_intent}\n"
        f"Gewünschter Ton: {user_tone}\n"
    )

    if state.get("memory_context"):
        korrektur_prompt += (
            f"Persönlicher Kontext des Nutzers:\n"
            f"{state['memory_context']}\n"
        )

    # Direktiven fuer den Corrector (aus internal.directives)
    internal = state.get("internal")
    direktiven: list = list(internal.directives) if internal else []
    if direktiven:
        korrektur_prompt += "\n[DIREKTIVEN]\n"
        korrektur_prompt += "ACHTUNG — Verhaltensregeln vom Nutzer (Arbeitsvertrag).\n"
        korrektur_prompt += "Diese MUESSEN in der korrigierten Antwort eingehalten werden:\n"
        for d in direktiven:
            if isinstance(d, dict):
                korrektur_prompt += f"- {d.get('anweisung', '')}\n"
                kontext = d.get("kontext", "")
                if kontext:
                    korrektur_prompt += f"  (Kontext: {kontext})\n"
            else:
                korrektur_prompt += f"- {d}\n"

    korrektur_prompt += (
        f"\n═══ BEWERTUNGSOBJEKT ═══\n"
        f"BENUTZERANFRAGE:\n{reiz_text(state)}\n\n"
        f"DEINE BISHERIGE ANTWORT:\n{state['response']}\n\n"
        f"TRIBUNAL-FEEDBACK:\n{state['tribunal_summary']}\n\n"
        f"Überarbeite die Antwort basierend auf dem Tribunal-Feedback.\n"
        f"Das Lagebild erklärt den Hintergrund — die Korrektur bezieht sich nur auf das Bewertungsobjekt."
    )

    node_cfg = get_node_config("corrector")

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G2) ──
    # correct() laeuft im CharacterGraph (services/event_consumer.py ruft
    # den Graphen via asyncio.to_thread(_graph_streamen, ...) im Worker-
    # Thread). Kein Event-Loop im aufrufenden Thread → submit_sync bruckt in
    # den Worker-Loop (Loop-Binding-Lesson).
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": korrektur_prompt}],
        system            = PROMPTS["corrector.system"],
        temperature       = node_cfg.get("temperature", 0.5),
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "corrector",
    )
    response = model_service.chat.submit_sync(chat_request)

    antwort_setzen(state, response.text, "corrector")
    state["token_total"] += response.token_total

    logger.info(f"Corrector: Antwort überarbeitet ({state['token_total']} Tokens gesamt)")

    return state
