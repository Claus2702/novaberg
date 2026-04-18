"""Klassifikation-Node -- bestimmt Aktion, Anweisung und Kontext per LLM.

Erweitert in Chat 44 (Epic 15): [FACHSPRACHE]-Block + normalisiert-Feld (Domain-Language-Normalisierung).
Erweitert in Chat 42 (CRUD-Haertung):
- Keyword-Hints + lernende Verb-Mappings vor dem LLM-Call
- Erweiterte Taxonomie: create, read, update, delete, reactivate
- Konfidenz-Berechnung nach LLM-Antwort
- [ERKENNUNGSHILFE]-Block im Classify-Prompt

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
from agents.direktiven.crud import _read_aktive, _read_inaktive
from config import redis_client, get_node_config, PROMPTS
from memory.session import session_turns_retrieve, format_session_turns_numbered
from services.llm_provider import get_chat_provider

logger = logging.getLogger("ki_server.agents.direktiven.klassifikation")


GUELTIGE_AKTIONEN: set[str] = {"create", "read", "update", "delete", "reactivate", "rejected"}


def _build_classify_prompt(
    aktive_direktiven: str,
    inaktive_direktiven: str,
    erkennungshilfe: str | None = None,
    session_turns: str | None = None,
) -> str:
    """Baut den Klassifikation-System-Prompt."""
    aktionen_text = " | ".join(f'"{a}"' for a in sorted(GUELTIGE_AKTIONEN))

    bloecke: list[str] = [
        PROMPTS["classify_direktiven.identity"].format(),
        PROMPTS["classify_direktiven.task"].format(
            aktionen_text=aktionen_text,
            aktive_direktiven=aktive_direktiven,
            inaktive_direktiven=inaktive_direktiven,
        ),
    ]

    if erkennungshilfe:
        bloecke.append(erkennungshilfe)

    if session_turns:
        bloecke.append(
            "[KONTEXT]\n"
            "Nutze den Verlauf fuer Kontext-Aufloesung — besonders bei impliziten Direktiven.\n"
            f"\n{session_turns}"
        )

    bloecke.append(PROMPTS["classify_direktiven.fachsprache"].format())
    bloecke.append(PROMPTS["classify_direktiven.rules"].format())

    return "\n\n".join(bloecke)


def klassifizieren(state: AgentState) -> dict:
    """Bestimmt Aktion, Anweisung und Kontext per Keyword-Hints + LLM-Call."""
    prompt = state["aufgabe"]
    user_id = state["kontext"].get("user_id", "")

    logger.info(f"klassifizieren: Einstieg — prompt='{prompt[:80]}', user_id='{user_id}'")

    # --- Stufe A: Statische Keyword-Hints ---
    kw_hints = keyword_hints_ermitteln(prompt)

    # --- Stufe B: Lernende Verb-Mappings ---
    vm_raw = verb_mappings_laden(user_id, "direktiven")
    vm_hints = verb_mapping_pruefen(prompt, user_id, "direktiven")

    logger.info(f"klassifizieren: keyword_hints={kw_hints}, verb_hints={vm_hints}")

    # --- Erkennungshilfe-Block bauen ---
    hilfe_block = erkennungshilfe_block(kw_hints, vm_hints, vm_raw)

    # --- Aktive + Inaktive Direktiven laden ---
    aktive = _read_aktive(user_id)
    aktive_text = "\n".join(
        f"  [{d['id']}] {d['anweisung']}" + (f" ({d['kontext']})" if d.get("kontext") else "")
        for d in aktive
    ) if aktive else "(keine)"

    inaktive = _read_inaktive(user_id)
    inaktive_text = "\n".join(
        f"  [{d['id']}] {d['anweisung']}" for d in inaktive
    ) if inaktive else "(keine)"

    # --- Session-Kontext laden ---
    session_turns: str | None = None
    if user_id:
        try:
            raw_turns: list[dict] = session_turns_retrieve(redis_client, user_id)
            session_turns = format_session_turns_numbered(raw_turns, max_turns=5) or None
        except Exception as e:
            logger.warning(f"klassifizieren: Session-Kontext fehlt: {e}")

    # --- Stufe C: LLM-Klassifikation ---
    system_prompt: str = _build_classify_prompt(aktive_text, inaktive_text, hilfe_block, session_turns)
    logger.info(f"klassifizieren: System-Prompt:\n{system_prompt}")

    node_cfg = get_node_config("router")
    provider = get_chat_provider()
    antwort = provider.chat(
        messages=[{"role": "user", "content": prompt}],
        system=system_prompt,
        temperature=node_cfg.get("temperature", 0.05),
        format_json=True,
        max_output_tokens=node_cfg.get("max_output_tokens"),
        caller="agent/direktiven/klassifikation",
    )

    # --- JSON parsen ---
    try:
        ergebnis: dict = json.loads(antwort.content)
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
        kontext = ergebnis.get("kontext", "")
        target_id = ergebnis.get("target_id")
        normalisiert = ergebnis.get("normalisiert", "")

        if action not in GUELTIGE_AKTIONEN:
            logger.warning(f"klassifizieren: Ungueltige Aktion '{action}' — Fallback 'read'")
            action = "read"

        # --- Konfidenz berechnen ---
        alle_hints = kw_hints + vm_hints
        konfidenz = konfidenz_berechnen(action, kw_hints, vm_hints, vm_raw)

        logger.info(
            f"klassifizieren: action='{action}', anweisung='{anweisung[:60]}', "
            f"kontext='{(kontext or '')[:40]}', target_id={target_id}, konfidenz={konfidenz}, "
            f"normalisiert='{normalisiert[:80]}'"
        )

        return {
            "parameter": {
                **state["parameter"],
                "action": action,
                "anweisung": anweisung,
                "kontext": kontext or None,
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
        logger.error(f"klassifizieren: JSON-Fehler — {fehler}")
        return {
            "status": "fehler",
            "fehler": f"Klassifikation fehlgeschlagen: {fehler}",
            "schritte": state["schritte"] + [{
                "node": "klassifizieren",
                "ergebnis": "json_fehler",
            }],
        }
