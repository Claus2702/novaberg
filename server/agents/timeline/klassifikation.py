"""Klassifikation-Node — bestimmt Aktion, Ziel, Zeitausdruck und Event-Typ per LLM.

Erweitert in Chat 44 (Epic 15): [FACHSPRACHE]-Block + normalisiert-Feld (Domain-Language-Normalisierung).
Erweitert in Chat 42 (CRUD-Haertung):
- Keyword-Hints + lernende Verb-Mappings vor dem LLM-Call
- Erweiterte Taxonomie: create, read, update, delete, reschedule
- Konfidenz-Berechnung nach LLM-Antwort
- reschedule als eigene Aktion (statt update+zeitausdruck)

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).
"""

import json
import logging

from agents.base import AgentState
from agents.crud_validation import (
    keyword_hints_ermitteln,
    verb_mapping_pruefen,
    verb_mappings_laden,
    konfidenz_berechnen,
    erkennungshilfe_block,
)
from config import redis_client, get_node_config, PROMPTS
from memory.session import session_turns_retrieve, format_session_turns_numbered
from services.model_services import model_service, ChatRequest

logger = logging.getLogger("ki_server.agents.timeline.klassifikation")


GUELTIGE_AKTIONEN: set[str] = {"create", "read", "update", "delete", "reschedule", "rejected"}

GUELTIGE_TYPEN: set[str] = {"termin", "geburtstag", "deadline", "jahrestag", "erinnerung"}


def _build_classify_prompt(
    erkennungshilfe: str | None = None,
    session_turns: str | None = None,
) -> str:
    """Baut den Klassifikation-System-Prompt aus [BLOCKNAME]-Bloecken zusammen."""
    aktionen_text = " | ".join(f'"{a}"' for a in sorted(GUELTIGE_AKTIONEN))

    bloecke: list[str] = [
        PROMPTS["classify_timeline.identity"].format(),
        PROMPTS["classify_timeline.task"].format(aktionen_text=aktionen_text),
    ]

    if erkennungshilfe:
        bloecke.append(erkennungshilfe)

    if session_turns:
        bloecke.append(
            "[KONTEXT]\n"
            "Nutze den Verlauf AUSSCHLIESSLICH fuer Target-Aufloesung. "
            "Hoehere Nummern sind aktueller.\n"
            f"\n{session_turns}"
        )

    bloecke.append(PROMPTS["classify_timeline.fachsprache"].format())
    bloecke.append(PROMPTS["classify_timeline.rules"].format())

    return "\n\n".join(bloecke)


def klassifizieren(state: AgentState) -> dict:
    """Bestimmt Aktion, Target, Zeitausdruck und Event-Typ per Keyword-Hints + LLM-Call."""
    prompt = state["aufgabe"]
    user_id = state["kontext"].get("user_id", "")
    character_id = state["kontext"].get("character_id", "")

    logger.info(f"klassifizieren: Einstieg — prompt='{prompt[:80]}', user_id='{user_id}'")

    # --- Stufe A: Statische Keyword-Hints ---
    kw_hints = keyword_hints_ermitteln(prompt)

    # --- Stufe B: Lernende Verb-Mappings ---
    vm_raw = verb_mappings_laden(user_id, "timeline")
    vm_hints = verb_mapping_pruefen(prompt, user_id, "timeline")

    logger.info(f"klassifizieren: keyword_hints={kw_hints}, verb_hints={vm_hints}")

    # --- Erkennungshilfe-Block bauen ---
    hilfe_block = erkennungshilfe_block(kw_hints, vm_hints, vm_raw)

    # ── Session-Kontext laden ──
    session_turns: str | None = None
    if user_id:
        try:
            raw_turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)
            session_turns = format_session_turns_numbered(raw_turns, max_turns=5) or None
        except Exception as e:
            logger.warning(f"klassifizieren: Session-Kontext fehlt: {e}")

    # --- Stufe C: LLM-Klassifikation ---
    system_prompt: str = _build_classify_prompt(hilfe_block, session_turns)
    logger.info(f"klassifizieren: System-Prompt:\n{system_prompt}")

    node_cfg = get_node_config("router")

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G3) ──
    # klassifizieren() laeuft im TimelineAgent (sync invoke), aufgerufen aus
    # CharacterGraph agent_dispatch oder services/pixie/dispatch.py — beide
    # Pfade nutzen asyncio.to_thread. Kein Event-Loop im aufrufenden Thread
    # → submit_sync.
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": prompt}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "agent/timeline/klassifikation",
    )

    # ── JSON parsen ──
    try:
        response = model_service.chat.submit_sync(chat_request)
        ergebnis: dict = response.parsed
        action = ergebnis.get("action", "")

        # --- REJECTED: Classify hat Prompt als Nicht-Auftrag erkannt ---
        if action == "rejected":
            grund = ergebnis.get("grund", "kein Grund angegeben")
            logger.info(f"klassifizieren: REJECTED — {grund}")
            return {
                "parameter": {**state["parameter"], "action": "rejected"},
                "status": "rejected",
                "schritte": state["schritte"] + [{
                    "node": "klassifizieren",
                    "ergebnis": f"rejected/{grund}",
                }],
            }

        target = ergebnis.get("target", "")
        zeitausdruck = ergebnis.get("zeitausdruck", "")
        event_type = ergebnis.get("event_type", "termin")
        normalisiert = ergebnis.get("normalisiert", "")

        if action not in GUELTIGE_AKTIONEN:
            logger.warning(f"klassifizieren: Ungueltige Aktion '{action}' — Fallback 'read'")
            action = "read"

        if event_type not in GUELTIGE_TYPEN:
            event_type = "termin"

        # --- Konfidenz berechnen ---
        alle_hints = kw_hints + vm_hints
        konfidenz = konfidenz_berechnen(action, kw_hints, vm_hints, vm_raw)

        logger.info(
            f"klassifizieren: action='{action}', target='{target}', "
            f"zeit='{zeitausdruck}', typ='{event_type}', konfidenz={konfidenz}, "
            f"normalisiert='{normalisiert[:80]}'"
        )

        return {
            "parameter": {
                **state["parameter"],
                "action": action,
                "target": target,
                "zeitausdruck": zeitausdruck,
                "event_type": event_type,
                "normalisiert": normalisiert,
                "konfidenz": konfidenz,
                "keyword_hints": alle_hints,
            },
            "schritte": state["schritte"] + [{
                "node": "klassifizieren",
                "ergebnis": f"{action}/{target}/{zeitausdruck}/{event_type}/konfidenz={konfidenz}",
            }],
        }

    except (json.JSONDecodeError, KeyError) as fehler:
        logger.exception(f"klassifizieren: JSON-Fehler — {fehler}")
        return {
            "status": "fehler",
            "fehler": f"Klassifikation fehlgeschlagen: {fehler}",
            "schritte": state["schritte"] + [{
                "node": "klassifizieren",
                "ergebnis": "json_fehler",
            }],
        }
