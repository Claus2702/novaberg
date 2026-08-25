"""Klassifikation-Node -- bestimmt Aktion und Anweisung per LLM.

Erweitert in Chat 44 (Epic 15): [FACHSPRACHE]-Block + normalisiert-Feld (Domain-Language-Normalisierung).
Erweitert in Chat 42 (CRUD-Haertung):
- Keyword-Hints + lernende Verb-Mappings vor dem LLM-Call
- Erweiterte Taxonomie: create, read, update, delete, reactivate, replace, konsolidieren
- Konfidenz-Berechnung nach LLM-Antwort
- [ERKENNUNGSHILFE]-Block im Classify-Prompt

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).
"""

import json
import logging

from agents.base import AgentState
from agents.charakter_identitaet.crud import _read_aktive, _read_inaktive
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

logger = logging.getLogger("ki_server.agents.charakter_identitaet.klassifikation")


GUELTIGE_AKTIONEN: set[str] = {"create", "read", "update", "delete", "reactivate", "replace", "konsolidieren", "rejected"}


def _build_classify_prompt(
    aktive_anweisungen: str,
    inaktive_anweisungen: str,
    anzahl_aktiv: int,
    erkennungshilfe: str | None = None,
    session_turns: str | None = None,
) -> str:
    """Baut den Klassifikation-System-Prompt."""
    aktionen_text = " | ".join(f'"{a}"' for a in sorted(GUELTIGE_AKTIONEN))

    bloecke: list[str] = [
        PROMPTS["classify_charakter.identity"].format(),
        PROMPTS["classify_charakter.task"].format(
            aktionen_text=aktionen_text,
            anzahl_aktiv=anzahl_aktiv,
            aktive_anweisungen=aktive_anweisungen,
            inaktive_anweisungen=inaktive_anweisungen,
        ),
    ]

    if erkennungshilfe:
        bloecke.append(erkennungshilfe)

    if session_turns:
        bloecke.append(
            "[KONTEXT]\n"
            "Nutze den Verlauf fuer Kontext-Aufloesung.\n"
            f"\n{session_turns}"
        )

    bloecke.append(PROMPTS["classify_charakter.fachsprache"].format())
    bloecke.append(PROMPTS["classify_charakter.rules"].format())

    return "\n\n".join(bloecke)


def klassifizieren(state: AgentState) -> dict:
    """Bestimmt Aktion und Anweisung per Keyword-Hints + LLM-Call."""
    prompt = state["aufgabe"]
    user_id = state["kontext"].get("user_id", "")
    character_id = state["kontext"].get("character_id", "")

    logger.info(f"klassifizieren: Einstieg — prompt='{prompt[:80]}', user_id='{user_id}'")

    # --- Stufe A: Statische Keyword-Hints ---
    kw_hints = keyword_hints_ermitteln(prompt)

    # --- Stufe B: Lernende Verb-Mappings ---
    vm_raw = verb_mappings_laden(user_id, "charakter_identitaet")
    vm_hints = verb_mapping_pruefen(prompt, user_id, "charakter_identitaet")

    logger.info(f"klassifizieren: keyword_hints={kw_hints}, verb_hints={vm_hints}")

    # --- Erkennungshilfe-Block bauen ---
    hilfe_block = erkennungshilfe_block(kw_hints, vm_hints, vm_raw)

    # --- Aktive + Inaktive Anweisungen laden ---
    aktive = _read_aktive(user_id)
    anzahl_aktiv = len(aktive)
    aktive_text = "\n".join(f"  [{a['id']}] {a['anweisung']}" for a in aktive) if aktive else "(keine)"

    inaktive = _read_inaktive(user_id)
    inaktive_text = "\n".join(f"  [{a['id']}] {a['anweisung']}" for a in inaktive) if inaktive else "(keine)"

    # --- Session-Kontext laden ---
    session_turns: str | None = None
    if user_id:
        try:
            raw_turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)
            session_turns = format_session_turns_numbered(raw_turns, max_turns=5) or None
        except Exception as e:
            logger.warning(f"klassifizieren: Session-Kontext fehlt: {e}")

    # --- Stufe C: LLM-Klassifikation ---
    system_prompt: str = _build_classify_prompt(aktive_text, inaktive_text, anzahl_aktiv, hilfe_block, session_turns)
    logger.info(f"klassifizieren: System-Prompt:\n{system_prompt}")

    node_cfg = get_node_config("router")

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G3) ──
    # klassifizieren() laeuft im CharakterIdentitaetAgent (sync invoke),
    # aufgerufen aus CharacterGraph agent_dispatch oder services/pixie/
    # dispatch.py — beide Pfade nutzen asyncio.to_thread. Kein Event-Loop
    # im aufrufenden Thread → submit_sync.
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": prompt}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "agent/charakter_identitaet/klassifikation",
    )

    # --- JSON parsen ---
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

        anweisung = ergebnis.get("anweisung", "")
        target_id = ergebnis.get("target_id")
        normalisiert = ergebnis.get("normalisiert", "")

        if action not in GUELTIGE_AKTIONEN:
            logger.warning(f"klassifizieren: Ungueltige Aktion '{action}' — Fallback 'read'")
            action = "read"

        # Konsolidierungs-Check: create bei >=3 aktiven → konsolidieren
        if action == "create" and anzahl_aktiv >= 3:
            logger.info(f"klassifizieren: {anzahl_aktiv} aktive Anweisungen — konsolidieren")
            action = "konsolidieren"

        # --- Konfidenz berechnen ---
        alle_hints = kw_hints + vm_hints
        konfidenz = konfidenz_berechnen(action, kw_hints, vm_hints, vm_raw)

        logger.info(
            f"klassifizieren: action='{action}', anweisung='{anweisung[:60]}', "
            f"target_id={target_id}, konfidenz={konfidenz}, "
            f"normalisiert='{normalisiert[:80]}'"
        )

        return {
            "parameter": {
                **state["parameter"],
                "action": action,
                "anweisung": anweisung,
                "target_id": target_id,
                "normalisiert": normalisiert,
                "konfidenz": konfidenz,
                "keyword_hints": alle_hints,
            },
            "schritte": state["schritte"] + [{
                "node": "klassifizieren",
                "ergebnis": f"{action}/{anweisung[:40]}/konfidenz={konfidenz}",
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
