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
import re

from agents.base import AgentState
from agents.crud_validation import (
    erkennungshilfe_block,
    keyword_hints_ermitteln,
    konfidenz_berechnen,
    verb_mapping_pruefen,
    verb_mappings_laden,
)
from agents.direktiven.crud import _read_aktive, _read_inaktive
from config import PROMPTS, get_node_config, redis_client
from memory.session import format_session_turns_numbered, session_turns_retrieve
from services.model_services import ChatRequest, model_service

logger = logging.getLogger("ki_server.agents.direktiven.klassifikation")


GUELTIGE_AKTIONEN: set[str] = {"create", "read", "update", "delete", "reactivate", "rejected"}

# Die Schreibweisen, in denen die Listen des Prompts eine Kennung zeigen:
# `[13]` (Aufbau der Listen in `klassifizieren`) und ihre Ziffern `13` — genau
# `f"[{n}]"` und `str(n)` fuer eine Ganzzahl `n > 0`. Die Liste schreibt die
# Ganzzahl der Spalte, also nie eine fuehrende Null: `"013"` ist keine ihrer
# Schreibweisen. Nur ASCII-Ziffern — `str.isdigit` naehme auch `²` oder `١٣` an.
_LIST_FORM: re.Pattern[str] = re.compile(r"\[([1-9][0-9]*)\]|([1-9][0-9]*)")


def _read_target_id(roh: object) -> tuple[int | None, str | None]:
    """Liest die Kennung aus der Modellangabe — als Nummer, als keine oder als Fehler.

    Die Modellausgabe ist die unzuverlaessigste Quelle im System, und die
    Liste zeigt die Kennung in einer anderen Form (`[13]`) als die Spalte
    (`13`): Das Modell gibt zurueck, was es gesehen hat. Bis zum 25.10.2026
    ging der Wert ungeprueft an SQL und endete mit `invalid input syntax for
    type integer: "[13]"`. Vorbild ist `dateien_wurzeln/klassifikation.py::
    _ziffer_oder_nichts` — hier mit dem Unterschied, dass ein unbrauchbarer
    Wert nicht zu `None` wird: `None` hiesse hier *keine Kennung* und fuehrte
    auf den Weg ueber das Stichwort, also zu einem geratenen Ziel. Eine Kopie
    je Dienst, kein gemeinsames Modul.

    Vorbedingung: `roh` ist, was das Sprachmodell unter `target_id` geliefert
    hat — beliebigen Typs.
    Nachbedingung: `(kennung, None)` mit einer Ganzzahl > 0 bei einer JSON-Zahl
    oder einer Schreibweise der Liste (`"[13]"`, `"13"`, Leerraum aussen
    erlaubt); `(None, None)`, wenn das Modell keine nannte (`null`);
    `(None, grund)` bei jedem anderen Wert.
    Fehlerfaelle: Wahrheitswert, Kommazahl, Zahl <= 0, Wort, leerer Text,
    zwei Kennungen, Liste, fuehrende Null, andere Klammer, Vorsilbe — alles
    mit Grund, nichts geraten.
    """
    # ── Eingabe-Validierung ─────────────────────
    if roh is None:
        return None, None
    if isinstance(roh, bool):
        # bool ist eine Unterklasse von int — True waere sonst Direktive 1.
        return None, f"target_id ist ein Wahrheitswert: {roh!r}"

    # ── Verarbeitung ────────────────────────────
    kennung: int | None = None
    if isinstance(roh, int):
        kennung = roh
    elif isinstance(roh, str):
        treffer: re.Match[str] | None = _LIST_FORM.fullmatch(roh.strip())
        if treffer:
            kennung = int(treffer.group(1) or treffer.group(2))

    # ── Ausgabe-Verifikation ────────────────────
    if kennung is None:
        return None, f"target_id ist keine Kennung der Liste: {roh!r} ({type(roh).__name__})"
    if kennung <= 0:
        return None, f"target_id ist keine gueltige Kennung: {roh!r}"
    return kennung, None


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
    character_id = state["kontext"].get("character_id", "")

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
            raw_turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)
            session_turns = format_session_turns_numbered(raw_turns, max_turns=5) or None
        except Exception as e:
            logger.warning(f"klassifizieren: Session-Kontext fehlt: {e}")

    # --- Stufe C: LLM-Klassifikation ---
    system_prompt: str = _build_classify_prompt(
        aktive_text, inaktive_text, hilfe_block, session_turns
    )
    logger.info(f"klassifizieren: System-Prompt:\n{system_prompt}")

    node_cfg = get_node_config("router")

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G3) ──
    # klassifizieren() laeuft im DirektivenAgent (sync invoke), aufgerufen
    # aus CharacterGraph agent_dispatch oder services/pixie/dispatch.py —
    # beide Pfade nutzen asyncio.to_thread. Kein Event-Loop im aufrufenden
    # Thread → submit_sync.
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": prompt}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "agent/direktiven/klassifikation",
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
        kontext = ergebnis.get("kontext", "")
        target_id, kennung_fehler = _read_target_id(ergebnis.get("target_id"))
        normalisiert = ergebnis.get("normalisiert", "")

        if kennung_fehler:
            logger.error(
                f"klassifizieren: {kennung_fehler} — kein Lesen, kein Schreiben, keine Frage"
            )
            return {
                "status": "fehler",
                "fehler": f"Klassifikation unbrauchbar: {kennung_fehler}",
                "schritte": state["schritte"] + [{
                    "node": "klassifizieren",
                    "ergebnis": "kennung_unlesbar",
                }],
            }

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
        logger.exception(f"{type(fehler).__name__}: klassifizieren: JSON-Fehler")
        return {
            "status": "fehler",
            "fehler": f"Klassifikation fehlgeschlagen: {fehler}",
            "schritte": state["schritte"] + [{
                "node": "klassifizieren",
                "ergebnis": "json_fehler",
            }],
        }
