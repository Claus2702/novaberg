"""Verdichtung — LLM-Call zur Kern-Erzeugung.

Erzeugt einen konkreten Satz mit ALLEN Namen, Orten, Zahlen.
Inhalt, nicht Emotion.
"""

import logging

from agents.base import AgentState
from config import ASSISTANT_NAME, get_node_config, PROMPTS
from services.model_services import model_service, ChatRequest

logger = logging.getLogger("ki_server.agents.kzg.verdichtung")


def _build_verdichtung_prompt(beobachter: str) -> str:
    """Baut den System-Prompt fuer die Verdichtung, besetzt nach Beobachter.

    Zwei getrennte Aufgaben-Bloecke statt eines mit Ausnahmeregel: Jeder traegt
    Few-Shot-Beispiele in der Person, die er meint. Ein Beispiel schlaegt eine
    Anweisung — die sechs Beispiele des Nutzer-Blocks legen das Subjekt auf den
    Nutzer fest, und keine Regel im selben Prompt haette dagegen bestanden.
    Vorbild fuer die Auswahl nach Rolle: graph/nodes/perzeption.py:42.

    Vorbedingung: beobachter ist "user" oder "assistant"; andere Werte werden
    wie "user" behandelt (der Nutzer-Block ist der haeufigere Fall).
    Nachbedingung: Identitaet, rollenrichtiger Aufgaben-Block und Regeln, in
    dieser Reihenfolge.
    """

    # ── Eingabe-Validierung ─────────────────────
    ist_assistent: bool = beobachter == "assistant"

    # ── Verarbeitung ────────────────────────────
    # Nur der Assistenten-Block traegt {traeger} als Platzhalter, damit der
    # Name aus der Konfiguration kommt und nicht im Prompt-Text festklebt
    # (Vorbild: agents/charakter/destillation.py:198-225). Der Nutzer-Block
    # wird nicht formatiert — er braucht keinen Platzhalter, und ein spaeter
    # eingefuegtes Zeichen darf dort keinen KeyError ausloesen.
    if ist_assistent:
        aufgabe: str = PROMPTS["kzg_verdichtung.assistant_task"].format(
            traeger=ASSISTANT_NAME,
        )
    else:
        aufgabe = PROMPTS["kzg_verdichtung.task"]

    # ── Ausgabe ─────────────────────────────────
    return "\n\n".join([
        PROMPTS["kzg_verdichtung.identity"],
        aufgabe,
        PROMPTS["kzg_verdichtung.rules"],
    ])


def verdichten(state: AgentState) -> dict:
    """LLM-Call: Erzeugt den kern aus der Aeusserung, die dieser Lauf bewertet.

    Welche der beiden Aeusserungen eines Turns bewertet wird, haengt am
    Beobachter: Pfad 1 (beobachter="user") verdichtet den User-Prompt und
    legt Novas Antwort ins Lagebild, Pfad 2 (beobachter="assistant") genau
    andersherum. Spiegelt den Input-Switch aus graph/nodes/salience.py:114-129;
    ohne ihn verdichtete Pfad 2 denselben User-Prompt wie Pfad 1 und legte
    zweimal denselben Satz ab (gemessen Chat 110).

    Vorbedingung: state["kontext"]["beobachter"] ist gesetzt — dispatch_kzg
    legt ihn dort ab. Fehlt er, wird laut gewarnt und wie Pfad 1 verfahren.
    Nachbedingung: state["parameter"]["kern"] traegt den verdichteten Satz.
    """

    # ── Eingabe-Validierung ─────────────────────
    user_prompt: str = state["parameter"].get("user_prompt", "")
    response:    str = state["parameter"].get("response", "")

    beobachter: str = (state.get("kontext") or {}).get("beobachter", "")
    if not beobachter:
        logger.warning(
            "KZG-Verdichtung: beobachter fehlt im kontext-Kanal — verdichte als "
            "Pfad 1 (user). Der Kern kann damit das falsche Subjekt tragen."
        )
        beobachter = "user"

    # ── Verarbeitung ────────────────────────────
    if beobachter == "assistant":
        bewertungs_text: str = response
        lagebild_text:   str = user_prompt
        lagebild_label:  str = "Dies ist die Eingabe des Nutzers."
        eingabe_label:   str = "Antwort der Assistentin"
    else:
        bewertungs_text = user_prompt
        lagebild_text   = response
        lagebild_label  = "Dies ist die Antwort des Assistenten."
        eingabe_label   = "Eingabe des Nutzers"

    lagebild: str = ""
    if lagebild_text:
        lagebild = (
            "[LAGEBILD]\n"
            f"Hintergrund — dient nur zum Verstaendnis. {lagebild_label}\n\n"
            f"{lagebild_text}\n\n"
        )

    user_message: str = (
        f"{lagebild}"
        "[BEWERTUNGSOBJEKT]\n"
        "Fasse NUR den folgenden Teil zusammen.\n"
        f"{eingabe_label}:\n{bewertungs_text}"
    )

    logger.info(
        f"KZG-Verdichtung: beobachter={beobachter}, "
        f"bewertungs_laenge={len(bewertungs_text)}, "
        f"lagebild_laenge={len(lagebild_text)}"
    )

    node_cfg = get_node_config("kzg_verdichtung")

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G2) ──
    # verdichten() laeuft im KzgAgent-Subgraphen, der vom CharacterGraph-
    # dispatcher-Node aus aufgerufen wird; der CharacterGraph wiederum
    # laeuft in services/event_consumer.py via asyncio.to_thread(...) im
    # Worker-Thread. Kein Event-Loop im aufrufenden Thread → submit_sync
    # bruckt in den Worker-Loop (Loop-Binding-Lesson). expect_json bleibt
    # False — die Verdichtung erwartet Fliesstext, kein JSON.
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": user_message}],
        system            = _build_verdichtung_prompt(beobachter),
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
