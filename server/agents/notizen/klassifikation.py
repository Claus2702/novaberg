"""Klassifikation-Node — bestimmt Aktion, Target und Target-Typ per LLM.

Erweitert in Chat 42 (CRUD-Haertung):
- Keyword-Hints + lernende Verb-Mappings vor dem LLM-Call
- Erweiterte Taxonomie: create, read, update, delete, add_content, remove_content, clear_content, rename
- Konfidenz-Berechnung nach LLM-Antwort

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).
"""

import json
import logging

from agents.base import AgentState
from agents.crud_validation import (
    erkennungshilfe_block,
    keyword_hints_ermitteln,
    konfidenz_berechnen,
    verb_mapping_pruefen,
    verb_mappings_laden,
)
from config import PROMPTS, get_node_config, redis_client
from memory.session import format_session_turns_numbered, session_turns_retrieve
from services.model_services import ChatRequest, model_service

logger = logging.getLogger("ki_server.agents.notizen.klassifikation")


GUELTIGE_AKTIONEN: set[str] = {
    "create", "read", "update", "delete",
    "add_content", "remove_content", "clear_content", "rename",
    "rejected",
}


def _build_classify_prompt(
    erkennungshilfe: str | None = None,
    session_turns: str | None = None,
) -> str:
    """Baut den Klassifikation-System-Prompt aus [BLOCKNAME]-Bloecken zusammen."""
    aktionen_text = " | ".join(f'"{a}"' for a in sorted(GUELTIGE_AKTIONEN))

    bloecke: list[str] = [
        PROMPTS["classify_notizen.identity"].format(),
        PROMPTS["classify_notizen.task"].format(aktionen_text=aktionen_text),
    ]

    if erkennungshilfe:
        bloecke.append(erkennungshilfe)

    if session_turns:
        bloecke.append(
            "[KONTEXT]\n"
            "Nutze den Verlauf fuer Target-Aufloesung UND Inhalts-Aufloesung. "
            "Hoehere Nummern sind aktueller.\n"
            "\n"
            "Inhalts-Aufloesung: Wenn der aktuelle Prompt einen Bezug enthaelt "
            "('leg sie an', 'mach das', 'die Liste', 'die', 'sie', 'das'), "
            "loese ihn aus dem letzten passenden Vor-Turn auf und schreibe den "
            "vollstaendigen Inhalt ins 'normalisiert'-Feld.\n"
            "\n"
            "Beispiel: Vor-Turn enthaelt 'Halloumi, Feta, Paneer'. "
            "Aktueller Prompt: 'Leg sie bitte an'. "
            "normalisiert = \"create: Neue Notiz mit Inhalt: Halloumi, Feta, Paneer\".\n"
            f"\n{session_turns}"
        )

    bloecke.append(PROMPTS["classify_notizen.fachsprache"].format())
    bloecke.append(PROMPTS["classify_notizen.rules"].format())

    return "\n\n".join(bloecke)


def klassifizieren(state: AgentState) -> dict:
    """Bestimmt Aktion, Target und Target-Typ per Keyword-Hints + LLM-Call."""
    prompt = state["aufgabe"]
    user_id = state["kontext"].get("user_id", "")
    character_id = state["kontext"].get("character_id", "")

    logger.info(f"klassifizieren: Einstieg — prompt='{prompt[:80]}', user_id='{user_id}'")

    # --- Stufe A: Statische Keyword-Hints ---
    kw_hints = keyword_hints_ermitteln(prompt)

    # --- Stufe B: Lernende Verb-Mappings ---
    vm_raw = verb_mappings_laden(user_id, "notizen")
    vm_hints = verb_mapping_pruefen(prompt, user_id, "notizen")

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
    # klassifizieren() laeuft im NotizenAgent. Der Agent wird sync invoked,
    # entweder aus dem CharacterGraph (agent_dispatch_node → notizen/
    # dispatch.py → agent.invoke), der seinerseits in event_consumer.py via
    # asyncio.to_thread laeuft, oder aus services/pixie/dispatch.py via
    # asyncio.to_thread(agent.invoke, ...). Beide Pfade landen in einem
    # Worker-Thread ohne Event-Loop → submit_sync bruckt in den Worker-
    # Loop (Loop-Binding-Lesson).
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": prompt}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "agent/notizen/klassifikation",
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
        target_typ = ergebnis.get("target_typ", "titel")
        normalisiert = ergebnis.get("normalisiert", "")

        # Inhalts-Aufloesung-Heuristik: normalisiert deutlich laenger als aufgabe
        # = LLM hat Inhalt aus Vor-Turn ins normalisiert-Feld kopiert.
        logger.debug(f"klassifizieren: LLM-Ergebnis normalisiert='{normalisiert}'")
        if len(normalisiert) > len(prompt) * 2 and len(normalisiert) - len(prompt) > 20:
            logger.info(
                f"klassifizieren: Inhalts-Aufloesung erkannt — "
                f"aufgabe={len(prompt)} Zeichen, normalisiert={len(normalisiert)} Zeichen"
            )

        if action not in GUELTIGE_AKTIONEN:
            logger.warning(f"klassifizieren: Ungueltige Aktion '{action}' — Fallback 'read'")
            action = "read"

        # --- Konfidenz berechnen ---
        alle_hints = kw_hints + vm_hints
        konfidenz = konfidenz_berechnen(action, kw_hints, vm_hints, vm_raw)

        logger.info(
            f"klassifizieren: action='{action}', target='{target}', typ='{target_typ}', "
            f"konfidenz={konfidenz}, "
            f"normalisiert='{normalisiert}'"
        )

        return {
            "parameter": {
                **state["parameter"],
                "action": action,
                "target": target,
                "target_typ": target_typ,
                "normalisiert": normalisiert,
                "konfidenz": konfidenz,
                "keyword_hints": alle_hints,
            },
            "schritte": state["schritte"] + [{
                "node": "klassifizieren",
                "ergebnis": f"{action}/{target}/{target_typ}/konfidenz={konfidenz}",
            }],
        }

    except (json.JSONDecodeError, KeyError) as fehler:
        logger.exception(f"{type(fehler).__name__}: klassifizieren: JSON-Fehler")
        return {
            "status": "fehler",
            "fehler": f"Klassifikation fehlgeschlagen: {fehler}",
            "schritte": state["schritte"] + [{
                "node": "klassifizieren",
                "ergebnis": "json_fehler",
            }],
        }
