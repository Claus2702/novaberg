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
    erkennungshilfe_block,
    keyword_hints_ermitteln,
    konfidenz_berechnen,
    verb_mapping_pruefen,
    verb_mappings_laden,
)
from agents.object_nearness import consent_fields, render_object_reference
from config import PROMPTS, get_node_config, redis_client
from memory.session import format_session_turns_numbered, session_turns_retrieve
from memory.timeline_types import CLASSIFIABLE, EVENT_TYPES
from services.model_services import ChatRequest, model_service

logger = logging.getLogger("ki_server.agents.timeline.klassifikation")


GUELTIGE_AKTIONEN: set[str] = {"create", "read", "update", "delete", "reschedule", "rejected"}

# Die Typen, die diese Klassifikation vergibt, kommen aus der Typquelle — ohne
# den Erinnerungs-Anker und ohne das Ereignis einer anderen Person.
GUELTIGE_TYPEN: frozenset[str] = frozenset(CLASSIFIABLE)

#: Der Typ, den ein Auftrag ohne erkennbaren Typ bekommt (Prompt: *„Im Zweifel"*).
DEFAULT_TYPE: str = "termin"

# Die Textfelder der Antwort, die `klassifizieren` liest, mit dem Wert, der
# gilt, wenn das Modell nichts nennt: `grund` bei `rejected`, sonst die
# uebrigen. Gelesen in `_read_answer` ueber `_read_text_fields`.
_REASON_FIELDS: dict[str, str] = {"grund": "kein Grund angegeben"}
_TEXT_FIELDS: dict[str, str] = {
    "target": "", "zeitausdruck": "", "event_type": DEFAULT_TYPE, "normalisiert": "",
}


def _read_text_fields(
    ergebnis: dict, vorgaben: dict[str, str],
) -> tuple[dict[str, str], str | None]:
    """Liest Textfelder der Modellantwort geprueft — als Text, als nicht genannt oder als Fehler.

    Bis zum 25.10.2026 las `klassifizieren` jedes Feld mit `ergebnis.get(feld, "")`.
    Der Vorgabewert greift nur beim fehlenden Schluessel: Lieferte das Modell
    `"normalisiert": null`, kam `None` zurueck, und `normalisiert[:80]` warf
    `TypeError` — die Bitte brach erst im Dispatch ab; `null` in `target` und
    `zeitausdruck` ging still als `None` in die Parameter. Vorbild ist
    `dateien/klassifikation.py::klassifizieren`, das jedes Feld geprueft liest —
    hier mit dem Unterschied, dass ein Wert falschen Typs nicht zu `""` wird:
    Leer hiesse *das Modell nannte nichts*, und eine defekte Antwort saehe aus
    wie eine gueltige. Eine Kopie je Dienst, kein gemeinsames Modul.

    Vorbedingung: `ergebnis` ist das Objekt der Modellantwort; `vorgaben` nennt
    je Feld den Wert, der gilt, wenn das Modell nichts nannte.
    Nachbedingung: `(felder, None)` mit einem Text je Feld aus `vorgaben` — dem
    gelieferten, oder der Vorgabe bei fehlendem Schluessel und bei `null`;
    `({}, grund)` beim ersten Feld, das weder Text noch `null` ist.
    Fehlerfaelle: Zahl, Wahrheitswert, Liste, Objekt — mit Grund, nichts ersetzt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(ergebnis, dict):
        msg: str = f"_read_text_fields: Antwort ist {type(ergebnis).__name__} statt dict"
        raise TypeError(msg)
    if not vorgaben:
        msg = "_read_text_fields: kein Feld genannt"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    felder: dict[str, str] = {}
    for feld, vorgabe in vorgaben.items():
        roh: object = ergebnis.get(feld)
        if roh is None:
            felder[feld] = vorgabe
        elif isinstance(roh, str):
            felder[feld] = roh
        else:
            return {}, f"{feld} ist {type(roh).__name__} statt Text: {repr(roh)[:60]}"

    # ── Ausgabe-Verifikation ────────────────────
    if felder.keys() != vorgaben.keys():
        msg = f"_read_text_fields: gelesen {sorted(felder)}, verlangt {sorted(vorgaben)}"
        raise RuntimeError(msg)
    return felder, None


def _unusable_answer(state: AgentState, grund: str, schritt: str) -> dict:
    """Beendet `klassifizieren` laut an einer Modellantwort, die nicht lesbar ist.

    Vorbedingung: `grund` und `schritt` sind nicht leer.
    Nachbedingung: eine `ERROR`-Zeile; das Ergebnis traegt `status: fehler`, den
    Grund und `schritt` als letzten Schritt — kein Lesen, kein Schreiben, keine Frage.
    Fehlerfaelle: ein leerer Grund oder Schritt wirft `ValueError` (Programmierfehler).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not grund or not schritt:
        msg: str = f"_unusable_answer: Grund {grund!r} oder Schritt {schritt!r} leer"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    logger.error(f"klassifizieren: {grund} — kein Lesen, kein Schreiben, keine Frage")
    abbruch: dict = {
        "status": "fehler",
        "fehler": f"Klassifikation unbrauchbar: {grund}",
        "schritte": state["schritte"] + [{"node": "klassifizieren", "ergebnis": schritt}],
    }

    # ── Ausgabe-Verifikation ────────────────────
    if len(abbruch["schritte"]) != len(state["schritte"]) + 1:
        msg = "_unusable_answer: Schritt nicht angehaengt"
        raise RuntimeError(msg)
    return abbruch


def _read_answer(
    state: AgentState, ergebnis: object,
) -> tuple[object, dict[str, str], dict | None]:
    """Liest die Modellantwort geprueft: Aktion und Textfelder — oder das Ende des Knotens.

    Zieht die Objektpruefung, das Lesen der Textfelder und den Ausgang `rejected`
    aus `klassifizieren` heraus: Dort endet jede Antwort, die keinen Auftrag
    traegt, an einer einzigen Stelle, und die Pruefungen machen `klassifizieren`
    nicht verzweigter. `action` bleibt ungeprueft wie bisher.

    Vorbedingung: `ergebnis` ist die Modellantwort, wie sie kam (`response.parsed`).
    Nachbedingung: `(action, felder, None)` mit einem Text je Feld aus `_TEXT_FIELDS`;
    sonst `(action, {}, ende)`, und `ende` ist das Ergebnis von `klassifizieren`:
    `rejected/<grund>`, oder laut `kein_objekt` bzw. `feld_falscher_typ`.
    Fehlerfaelle: kein Objekt, ein Feld weder Text noch `null` — beide laut ueber
    `_unusable_answer`, nichts ersetzt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(ergebnis, dict):
        return "", {}, _unusable_answer(
            state, f"Modellantwort ist {type(ergebnis).__name__} statt Objekt", "kein_objekt",
        )

    # ── Verarbeitung ────────────────────────────
    action: object = ergebnis.get("action", "")
    felder, feld_fehler = _read_text_fields(
        ergebnis, _REASON_FIELDS if action == "rejected" else _TEXT_FIELDS,
    )
    if feld_fehler:
        return action, {}, _unusable_answer(state, feld_fehler, "feld_falscher_typ")

    # --- REJECTED: Classify hat Prompt als Nicht-Auftrag erkannt ---
    if action == "rejected":
        grund: str = felder["grund"]
        logger.info(f"klassifizieren: REJECTED — {grund}")
        return action, {}, {
            "parameter": {**state["parameter"], "action": "rejected"},
            "status": "rejected",
            "schritte": state["schritte"] + [{
                "node": "klassifizieren",
                "ergebnis": f"rejected/{grund}",
            }],
        }

    # ── Ausgabe-Verifikation ────────────────────
    if felder.keys() != _TEXT_FIELDS.keys():
        msg: str = f"_read_answer: gelesen {sorted(felder)}, verlangt {sorted(_TEXT_FIELDS)}"
        raise RuntimeError(msg)
    return action, felder, None


def _type_prompt_fields() -> dict[str, str]:
    """Die Platzhalter der Typen im Prompt, gebaut aus der Typquelle.

    Vorbedingung: jeder Typ aus `CLASSIFIABLE` traegt eine `prompt_line`.
    Nachbedingung: `type_choices` (die Typen, durch `|` getrennt) und
        `type_lines` (je Typ eine Zeile `"typ": Beschreibung`), beide in der
        Reihenfolge von `CLASSIFIABLE`.
    Fehlerfaelle: ein klassifizierbarer Typ ohne Zeile wirft `ValueError` —
        das Modell kennte ihn sonst nur dem Namen nach.
    """
    # ── Eingabe-Validierung ─────────────────────
    missing: list[str] = [name for name in CLASSIFIABLE if not EVENT_TYPES[name].prompt_line]
    if missing:
        msg: str = f"Klassifizierbare Typen ohne Zeile im Prompt: {missing}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    fields: dict[str, str] = {
        "type_choices": "|".join(CLASSIFIABLE),
        "type_lines": "\n".join(
            f'  "{name}": {EVENT_TYPES[name].prompt_line}' for name in CLASSIFIABLE
        ),
    }

    # ── Ausgabe-Verifikation ────────────────────
    if fields["type_lines"].count("\n") != len(CLASSIFIABLE) - 1:
        msg = "Zeilen der Typen: eine Beschreibung traegt einen Zeilenumbruch"
        raise ValueError(msg)
    return fields


def _build_classify_prompt(
    erkennungshilfe: str | None = None,
    session_turns: str | None = None,
    objekt_bezug: list[dict] | None = None,
    angebot_satz: str = "",
) -> str:
    """Baut den Klassifikation-System-Prompt aus [BLOCKNAME]-Bloecken zusammen."""
    aktionen_text = " | ".join(f'"{a}"' for a in sorted(GUELTIGE_AKTIONEN))

    bloecke: list[str] = [
        PROMPTS["classify_timeline.identity"].format(),
        PROMPTS["classify_timeline.task"].format(
            aktionen_text=aktionen_text, **_type_prompt_fields(),
        ),
    ]

    if erkennungshilfe:
        bloecke.append(erkennungshilfe)

    if objekt_bezug:
        bloecke.append(PROMPTS["classify_timeline.objekt"].format(objekte=render_object_reference(objekt_bezug)))
        if angebot_satz:
            # Die Zustimmung bindet an die angebotene Sache (E1c, gemessen
            # 17.09.2026): Ohne diesen Block nahm die Klassifikation Ziel und
            # Zeit aus dem Verlauf, wo eine ANDERE Sache stand.
            bloecke.append(PROMPTS["classify_timeline.zustimmung"].format(
                angebot=angebot_satz[:200], objekte=render_object_reference(objekt_bezug),
            ))

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
    objekt_bezug: list[dict] = list(state["kontext"].get("objekt_bezug") or [])
    system_prompt: str = _build_classify_prompt(
        hilfe_block, session_turns, objekt_bezug,
        angebot_satz = str(state["kontext"].get("angebot_satz") or ""),
    )
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
        ergebnis: object = response.parsed
        # Kein Objekt, ein Feld falschen Typs und `rejected` enden in `_read_answer`.
        action, felder, ende = _read_answer(state, ergebnis)
        if ende is not None:
            return ende

        target: str = felder["target"]
        zeitausdruck: str = felder["zeitausdruck"]
        event_type: str = felder["event_type"]
        normalisiert: str = felder["normalisiert"]

        # Die Zustimmung bindet — deterministisch (E1c): Was der Mensch
        # angenommen hat, steht fest. `angebot_satz` steht nur bei einer
        # BLANKEN Zustimmung ("Gerne") — die Aeusserung nennt dann nichts
        # selbst, und was das Modell als Ziel oder Zeit einsetzt, stammt aus
        # dem Verlauf. ~~Gefuellt wurde nur, was leer war~~ → seit dem
        # 18.09.2026 gewinnt die Sache: `[gemessen, Betrieb]` Das Modell nahm
        # den Titel aus dem Verlauf ("Zahnarzttermin"), die Zeit kam aus der
        # angebotenen Abholung — ein Mischtermin, der keinem Wunsch entsprach.
        if state["kontext"].get("angebot_satz") and objekt_bezug:
            aus_der_sache, zeit_der_sache = consent_fields(objekt_bezug)
            if aus_der_sache and target != aus_der_sache:
                logger.info(f"klassifizieren: Ziel aus der zugestimmten Sache — '{aus_der_sache}' (Modell: '{target}')")
                target = aus_der_sache
            if zeit_der_sache and zeitausdruck != zeit_der_sache:
                logger.info(f"klassifizieren: Zeitangabe aus der zugestimmten Sache — '{zeit_der_sache}' (Modell: '{zeitausdruck}')")
                zeitausdruck = zeit_der_sache

        if action not in GUELTIGE_AKTIONEN:
            logger.warning(f"klassifizieren: Ungueltige Aktion '{action}' — Fallback 'read'")
            action = "read"

        if event_type not in GUELTIGE_TYPEN:
            # Laut: bis hierher wurde ein fremder Typ still zum Termin.
            logger.warning(
                f"klassifizieren: Ungueltiger Typ '{event_type}' — Fallback '{DEFAULT_TYPE}'"
            )
            event_type = DEFAULT_TYPE

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
        logger.exception(f"{type(fehler).__name__}: klassifizieren: JSON-Fehler")
        return {
            "status": "fehler",
            "fehler": f"Klassifikation fehlgeschlagen: {fehler}",
            "schritte": state["schritte"] + [{
                "node": "klassifizieren",
                "ergebnis": "json_fehler",
            }],
        }
