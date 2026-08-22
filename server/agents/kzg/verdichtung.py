"""Verdichtung — LLM-Call zur Kern-Erzeugung.

Erzeugt einen konkreten Satz mit ALLEN Namen, Orten, Zahlen.
Inhalt, nicht Emotion.
"""

import logging

from agents.base import AgentState
from config import ASSISTANT_NAME, get_node_config, PROMPTS
from services.model_services import model_service, ChatRequest

logger = logging.getLogger("ki_server.agents.kzg.verdichtung")


def _build_verdichtung_prompt(beobachter: str, graph_rolle: str = "human") -> str:
    """Baut den System-Prompt fuer die Verdichtung, besetzt nach Lage.

    Drei getrennte Aufgaben-Bloecke statt eines mit Ausnahmeregeln: Jeder traegt
    Few-Shot-Beispiele in der Person UND der Situation, die er meint. Ein
    Beispiel schlaegt eine Anweisung — die sechs Beispiele des Nutzer-Blocks
    legen das Subjekt auf den Nutzer fest, und keine Regel im selben Prompt
    haette dagegen bestanden. Vorbild fuer die Auswahl nach Rolle:
    graph/nodes/perzeption.py:42.

    Die drei Lagen:
      * Nutzer-Aeusserung        -> kzg_verdichtung.task
      * Novas Antwort            -> kzg_verdichtung.assistant_task
      * Novas entstehender Gedanke -> kzg_verdichtung.impuls_task

    Warum der dritte Block: Der Assistenten-Block rahmt den Text als „sie hat
    gerade geantwortet". Fuer einen Pixie-Impuls stimmt das nicht — der Gedanke
    ist ihr eben erst aufgegangen und wurde niemandem gesagt. Das Subjekt ist in
    beiden Faellen Nova, die Situation nicht.

    Vorbedingung: beobachter ist "user" oder "assistant", graph_rolle ist
    "human", "character" oder "agent". Unbekannte Werte fallen auf den
    Nutzer-Block zurueck (der haeufigere Fall).
    Nachbedingung: Identitaet, lagerichtiger Aufgaben-Block und Regeln, in
    dieser Reihenfolge.
    """
    # ── Verarbeitung ────────────────────────────
    # Nur die Nova-Bloecke tragen {traeger} als Platzhalter, damit der Name aus
    # der Konfiguration kommt und nicht im Prompt-Text festklebt (Vorbild:
    # agents/charakter/destillation.py:198-225). Der Nutzer-Block wird nicht
    # formatiert — er braucht keinen Platzhalter, und ein spaeter eingefuegtes
    # Zeichen darf dort keinen KeyError ausloesen.
    if graph_rolle == "agent":
        aufgabe: str = PROMPTS["kzg_verdichtung.impuls_task"].format(
            traeger=ASSISTANT_NAME,
        )
    elif beobachter == "assistant":
        aufgabe = PROMPTS["kzg_verdichtung.assistant_task"].format(
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

    Zwei Fragen, zwei Felder — sie fallen nur in zwei von drei Graphen zusammen:

    * `graph_rolle` entscheidet, WAS verdichtet wird. Nur der CharacterGraph
      verdichtet eine Reaktion; HumanGraph und AgentGraph verdichten einen Reiz.
    * `beobachter` entscheidet, WESSEN Subjekt der Kernsatz traegt — der
      Prompt-Baustein wird danach gewaehlt.

    Der AgentGraph ist der Fall, an dem sich das trennt: Novas Sicht
    (beobachter="assistant") auf einen Reiz (graph_rolle="agent"). Haengt die
    erste Frage am `beobachter`, verdichtet er die `response`, die er nie
    erzeugt. Gemessen 26.07.2026: Der Kernsatz lautete dann woertlich „Es liegt
    kein Bewertungsobjekt vor, da die Antwort der Assistentin leer ist" — und
    wurde als Gedaechtnisinhalt abgelegt.

    Vorbedingung: state["kontext"] traegt `beobachter` und `graph_rolle`;
    dispatch_kzg legt beide dort ab. Fehlt der Beobachter, wird laut gewarnt.
    Nachbedingung: state["parameter"]["kern"] traegt den verdichteten Satz.
    Fehlerfaelle: leeres Bewertungsobjekt — dann wird nicht verdichtet, sondern
    laut abgebrochen und ein leerer Kern zurueckgegeben.
    """
    # ── Eingabe-Validierung ─────────────────────
    # `reiz` traegt, was diesen Turn ausgeloest hat — die Nutzer-Aeusserung auf
    # einem Nutzer-Turn, Novas eigenen Gedanken auf einem Impuls-Turn. Der
    # Dispatcher entscheidet das, nicht diese Funktion.
    reiz:     str = state["parameter"].get("reiz", "")
    response: str = state["parameter"].get("response", "")
    kontext:     dict = state.get("kontext") or {}

    beobachter: str = kontext.get("beobachter", "")
    if not beobachter:
        logger.warning(
            "KZG-Verdichtung: beobachter fehlt im kontext-Kanal — verdichte als "
            "Pfad 1 (user). Der Kern kann damit das falsche Subjekt tragen."
        )
        beobachter = "user"

    graph_rolle: str = kontext.get("graph_rolle", "human")

    # ── Verarbeitung ────────────────────────────
    if graph_rolle == "character":
        bewertungs_text: str = response
        lagebild_text:   str = reiz
        lagebild_label:  str = "Dies ist die Eingabe des Nutzers."
        eingabe_label:   str = "Antwort der Assistentin"
    elif graph_rolle == "agent":
        # Der entstehende Gedanke. Kein Lagebild: Es gibt keine Antwort, auf die
        # er sich bezieht, und die leere `response` als Hintergrund auszugeben
        # waere eine Behauptung ueber etwas, das nicht stattgefunden hat.
        bewertungs_text = reiz
        lagebild_text   = ""
        lagebild_label  = ""
        eingabe_label   = "Eigener Gedanke der Assistentin"
    else:
        bewertungs_text = reiz
        lagebild_text   = response
        lagebild_label  = "Dies ist die Antwort des Assistenten."
        eingabe_label   = "Eingabe des Nutzers"

    # ── Segment vor Volltext ────────────────────
    # Die Salienz hat ein Segment bewertet, nicht den ganzen Turn. Wer den
    # Volltext verdichtet, waehrend die Bewertung ein Segment betraf, legt fuer
    # jedes Segment denselben Satz ab — gemessen 27.07.2026: drei Segmente
    # (137/487/222 Zeichen), drei Paraphrasen desselben Absatzes, die anderen
    # beiden Segmente nie gespeichert.
    #
    # Das Lagebild bleibt absichtlich die andere Turn-Haelfte und wird NICHT um
    # den Volltext erweitert. Sonst stuende der ganze Text wieder im Prompt und
    # die Ursache waere reproduziert.
    segment:        str = state["parameter"].get("segment", "")
    segment_index:  int = state["parameter"].get("segment_index", 0)
    segment_gesamt: int = state["parameter"].get("segment_gesamt", 0)

    if segment.strip():
        bewertungs_text = segment
    else:
        # Kein stiller Rueckfall: Ein Volltext-Lauf muss sich vom Segment-Lauf
        # im Log unterscheiden, sonst sieht die Ausnahme aus wie der Normalfall
        # (DEVELOPER_HANDBOOK §4, Default-wie-Fehlschlag-Lesson).
        logger.warning(
            f"KZG-Verdichtung: kein Segment im parameter-Kanal — verdichte den "
            f"Volltext ({len(bewertungs_text)} Zeichen, graph_rolle={graph_rolle}). "
            f"Erwartet bei pending_writes ausserhalb des Salienz-Nodes."
        )

    logger.info(
        f"KZG-Verdichtung: graph_rolle={graph_rolle}, beobachter={beobachter}, "
        f"quelle={'segment' if segment.strip() else 'volltext'}, "
        f"segment={segment_index + 1}/{segment_gesamt if segment_gesamt else 1}, "
        f"bewertungs_laenge={len(bewertungs_text)}, "
        f"lagebild_laenge={len(lagebild_text)}"
    )

    # Fail loud statt einen Satz ueber das Fehlen des Satzes ablegen.
    if not bewertungs_text.strip():
        logger.error(
            f"KZG-Verdichtung: Bewertungsobjekt leer — kein Kern erzeugt "
            f"(graph_rolle={graph_rolle}, beobachter={beobachter}, "
            f"lagebild_laenge={len(lagebild_text)})"
        )
        return {
            "parameter": {**state["parameter"], "kern": ""},
            "schritte": state["schritte"] + [
                {"node": "verdichten", "ergebnis": "leer", "kern": ""}
            ],
        }

    lagebild: str = ""
    if lagebild_text:
        lagebild = (
            "[LAGEBILD]\n"
            f"Hintergrund — dient nur zum Verstaendnis. {lagebild_label}\n\n"
            f"{lagebild_text}\n\n"
        )

    # ── Der tatsaechliche Ausgang ───────────────
    # Bis hierher kennt die Verdichtung nur zwei Texte: was gesagt wurde und
    # was geantwortet wurde. Was *geschah*, steht in keinem von beiden — und
    # eine Antwort, die eine abgelehnte Handlung bestaetigt, wird sonst als
    # Tatsache abgelegt (`FALSCHE-BESTAETIGUNG-WIRD-ERINNERUNG`, 18.08.2026).
    #
    # Der Block traegt eine **Tatsache, keine Regel.** Eine Anweisung der Form
    # „behaupte keine Handlung" waere wieder nur eine Bitte an ein Modell; ein
    # Ausgang, der neben dem Text steht, widerspricht der falschen Haelfte der
    # Antwort direkt. Dass er steht, ist zusicherbar — was das Modell daraus
    # macht, ist die Messung.
    ausgaenge: list = state["parameter"].get("agent_ausgaenge") or []
    ausgang: str = ""
    if ausgaenge:
        zeilen: str = "\n".join(
            f"- {a.get('agent', '?')}: hat den Auftrag ABGELEHNT. "
            f"Begruendung: {a.get('befund', '')}"
            for a in ausgaenge
        )
        ausgang = (
            "[TATSAECHLICHER AUSGANG]\n"
            "Was in diesem Turn wirklich geschah. Dies sind Tatsachen und "
            "gehen dem Wortlaut der Antwort vor: Behauptet die Antwort eine "
            "Handlung, die hier als abgelehnt steht, hat sie nicht "
            "stattgefunden.\n"
            f"{zeilen}\n\n"
        )
        logger.info(
            "KZG-Verdichtung: Ausgangsblock gesetzt — %d abgelehnte(r) Dienst(e)",
            len(ausgaenge),
        )

    user_message: str = (
        f"{lagebild}"
        f"{ausgang}"
        "[BEWERTUNGSOBJEKT]\n"
        "Fasse NUR den folgenden Teil zusammen.\n"
        f"{eingabe_label}:\n{bewertungs_text}"
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
        system            = _build_verdichtung_prompt(beobachter, graph_rolle),
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
