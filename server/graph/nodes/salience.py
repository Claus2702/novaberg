"""
Salienz Node — Reiner Entscheider.

Analysiert den Gespraechs-Turn und bewertet emotionale Salienz,
Themen, Gedaechtnistyp und Dimension. 8 Dimensionen, kein kern.

SCHREIBT NICHT IN DIE DB. Legt pending_writes fuer KZG an
(ohne Embedding, ohne kern — das uebernimmt der KZG-Agent).

Fakten-Extraktion (Chat 27) und Verdichtung/kern (Chat 29) entfernt.
Fakten -> WissensAgent (Epic 11 Phase 2).
Verdichtung -> KZG-Agent (Chat 29).

Entscheider-Arbeiter-Trennung (A1.1):
  Salienz -> pending_writes -> Dispatcher -> KZG-Agent

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).
"""

import json
import logging

import redis

from config import ASSISTANT_NAME, PROMPTS, get_node_config
from ei.salienz import salienz_effektiv_berechnen
from graph.reiz import reiz_text
from graph.state import ConversationState, pipeline_quelle
from memory.charakter import nutzer_gewichtung_laden
from memory.pipeline_log import (
    log_berechnung,
    log_fehler,
    log_switch,
    span_end,
    span_start,
)
from services.model_services import ChatRequest, model_service

logger = logging.getLogger("ki_server.salience")


def _prompt_segmentieren(prompt: str) -> list[str]:
    """
    Zerlegt einen Prompt in semantische Einheiten.
    Gibt eine Liste von Segment-Texten zurueck.
    Bei einfachen Prompts (1 Segment) wird der Original-Prompt zurueckgegeben.
    """
    # Kurze Prompts brauchen keine Segmentierung
    if len(prompt) < 60 or "." not in prompt:
        return [prompt]

    try:
        node_cfg = get_node_config("salienz")

        # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G1) ──
        # _prompt_segmentieren() laeuft im HumanGraph aus
        # api/chat.py:chat_senden (sync def im FastAPI-Threadpool). Kein
        # Event-Loop im aufrufenden Thread → submit_sync bruckt in den
        # Worker-Loop (Loop-Binding-Lesson).
        chat_request = ChatRequest(
            messages          = [{"role": "user", "content": prompt}],
            system            = "\n\n".join([
                PROMPTS["salienz_segment.identity"],
                PROMPTS["salienz_segment.task"],
                PROMPTS["salienz_segment.rules"],
            ]),
            temperature       = node_cfg.get("temperature", 0.05),
            expect_json       = True,
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "salienz/segment",
        )
        response = model_service.chat.submit_sync(chat_request)

        logger.debug(f"Salienz RAW: '{response.text[:500]}'")
        parsed = response.parsed

        # JSON koennte ein Array oder ein Objekt mit Array sein
        if isinstance(parsed, list):
            segmente: list[str] = [s.get("segment", "") for s in parsed if s.get("segment")]
        elif isinstance(parsed, dict) and "segments" in parsed:
            segmente = [s.get("segment", "") for s in parsed["segments"] if s.get("segment")]
        else:
            return [prompt]

        if not segmente:
            return [prompt]

        if len(segmente) == 1:
            return [prompt]  # Original beibehalten, kein Rewrite

        logger.info(f"Segmentierer: {len(segmente)} Segmente erkannt")
        for idx, seg in enumerate(segmente):
            logger.info(f"  Segment {idx + 1}: {seg[:80]}")

        return segmente

    except (json.JSONDecodeError, KeyError, Exception) as fehler:
        logger.warning(f"Segmentierer: Fehler ({fehler}) — Fallback auf ganzen Prompt")
        return [prompt]


def _aufgaben_block_name(graph_rolle: str) -> str:
    """Nennt den Aufgaben-Block, den diese Rolle zieht.

    Eine Funktion und nicht zwei Verzweigungen: Die Abbildung wird an zwei
    Stellen gebraucht — beim Bauen des Prompts und beim Protokollieren —, und
    zwei Kopien liefen beim naechsten Rollenwechsel auseinander. Dann stuende
    im Log eine Schablone, die gar nicht gezogen wurde.

    Vorbedingung: keine — unbekannte Rollen gelten als Nutzerlage.
    Nachbedingung: einer der drei PROMPTS-Schluessel.
    """
    if graph_rolle == "agent":
        return "salienz.impuls_task"
    if graph_rolle == "character":
        return "salienz.assistant_task"
    return "salienz.task"


def _build_salienz_prompt(graph_rolle: str = "human") -> tuple[str, str]:
    """Baut den Salienz-System-Prompt, besetzt nach Lage.

    Drei getrennte Aufgaben-Bloecke statt eines mit Ausnahmeregeln — Vorbild:
    `_build_verdichtung_prompt` in agents/kzg/verdichtung.py, wo Chat 110
    dieselbe Fehlerklasse eine Ebene tiefer behoben hat.

    Die drei Lagen:
      * Nutzer-Aeusserung          -> salienz.task
      * Novas Antwort              -> salienz.assistant_task
      * Novas entstehender Gedanke -> salienz.impuls_task

    Warum drei und nicht zwei: Der Assistenten-Block rahmt den Text als „sie
    hat gerade geantwortet" und verweist auf ein Lagebild. Fuer einen Impuls
    stimmt beides nicht — der Gedanke ist ihr eben erst aufgegangen, und das
    Lagebild ist leer. Das Subjekt ist in beiden Faellen Nova, die Lage nicht.

    Der Befund dahinter (SALIENZ-PROMPT-NUTZER-SCHABLONE): Bis Chat 112 ging
    derselbe, durchgehend aus der Nutzerperspektive geschriebene Prompt an alle
    drei Graphen. Im CharacterGraph wies er an, das Lagebild zu bewerten statt
    das Bewertungsobjekt — die Anweisung war exakt invertiert.

    Der geteilte Dimensionen-Block traegt die zehn Felder und das
    Antwortformat; nur Lage und Skala haengen an der Rolle. Die Skala lag bis
    Chat 112 zusaetzlich in den Regeln, dort in zwei Kopien (default und
    gemma4) — beide auf die Nutzerlage geschrieben.

    Rueckgabe ist ein Paar aus Prompt und **tatsaechlich verwendetem**
    Blocknamen. Der Name wird hier zurueckgegeben und nicht beim Aufrufer neu
    aus der Rolle abgeleitet: Sonst haengen Protokoll und Prompt an zwei
    getrennten Ableitungen, und das Log kann eine Schablone melden, die nie
    gezogen wurde. Eine erste Fassung dieser Funktion hatte genau das — die
    Gegenprobe (Node zieht fuer jede Rolle den Nutzer-Block) blieb gruen, weil
    die Log-Zeile weiterhin das Richtige behauptete
    (novaberg-lesson_l_log-behauptet-was-es-weiss.md).

    Vorbedingung: graph_rolle ist "human", "character" oder "agent".
    Nachbedingung: (Prompt, Blockname). Der Prompt traegt Identitaet,
        lagerichtigen Aufgaben-Block, Dimensionen und Regeln in dieser
        Reihenfolge; der Blockname benennt den zweiten davon.
    Fehlerfaelle: unbekannte Rollen fallen auf den Nutzer-Block zurueck — den
        haeufigeren Fall — und werden benannt, damit ein Tippfehler in einer
        Rolle nicht still die falsche Schablone zieht.
    """
    # ── Eingabe-Validierung ─────────────────────
    if graph_rolle not in ("human", "character", "agent"):
        logger.warning(
            f"Salienz: unbekannte graph_rolle '{graph_rolle}' — "
            f"Nutzer-Block verwendet"
        )
        graph_rolle = "human"

    # ── Verarbeitung ────────────────────────────
    # Nur die Nova-Bloecke tragen {traeger}, damit der Name aus der
    # Konfiguration kommt und nicht im Prompt-Text festklebt. Der Nutzer-Block
    # wird nicht formatiert — er braucht keinen Platzhalter, und eine spaeter
    # eingefuegte geschweifte Klammer duerfte dort keinen KeyError ausloesen.
    block: str = _aufgaben_block_name(graph_rolle)

    if graph_rolle == "human":
        aufgabe: str = PROMPTS[block]
    else:
        aufgabe = PROMPTS[block].format(traeger=ASSISTANT_NAME)

    # ── Ausgabe ─────────────────────────────────
    prompt: str = "\n\n".join([
        PROMPTS["salienz.identity"],
        aufgabe,
        PROMPTS["salienz.dimensionen"],
        PROMPTS["salienz.rules"],
    ])
    return prompt, block


def _salienz_wert_lesen(salienz_obj: dict) -> float | None:
    """Liest den Salienzwert eines bewerteten Segments als Zahl.

    Vorbedingung: salienz_obj ist die geparste LLM-Antwort eines Segments.
    Nachbedingung: ein float, wenn das Feld 'salienz' numerisch ist.
    Fehlerfaelle: Feld fehlt oder ist nicht in eine Zahl wandelbar — dann None
        und eine Fehlerzeile. Ein unlesbarer Wert darf ausdruecklich NICHT als
        0.0 durchgehen: Er wanderte sonst ins Maximum und senkte es still ab,
        ohne dass irgendwo steht, dass ueberhaupt etwas fehlte.
    """
    # ── Eingabe-Validierung ─────────────────────
    # **Die Modellbewertung steht in `salienz_modell`, nicht in `salienz`.**
    # `salienz` traegt ab dem ersten Lauf das **Ergebnis** der Formel
    # (`salienz_obj["salienz"] = ergebnis.effektiv`), und dieser Knoten laeuft
    # je Segment. Wer hier `salienz` liest, rechnet ab dem zweiten Segment auf
    # seinem eigenen Ausgang weiter — eine Eingabe aus dem Ergebnis, was
    # `novaberg-convention-abgeleitete-werte.md` Regel 2 ausschliesst, und die
    # Rechnung ist nicht mehr idempotent (Regel 4).
    #
    # **Latent bis zum 24.08.2026**, weil die alte Formel mit `(1 + zuschlag)`
    # multiplizierte: Bei ruhigem Turn war der Faktor 1,0 und die Wiederholung
    # unsichtbar. Bei Erregung war sie es nicht — ein Fuenf-Segment-Turn bekam
    # `(1 + z)^5`. Gemessen am 24.08.2026: **2027 Turns mit zwei oder mehr
    # Segmenten gegen 713 mit einem.** Aufgefallen ist es erst, als die
    # normierte Formel in die andere Richtung zeigte: `0.5 / 1.3² = 0.2958`.
    roh = salienz_obj.get("salienz_modell", salienz_obj.get("salienz"))

    if roh is None:
        logger.error(
            "Salienz: Segment ohne Feld 'salienz' — fuer salienz_human uebergangen"
        )
        return None

    # ── Verarbeitung ────────────────────────────
    try:
        wert: float = float(roh)
    except (TypeError, ValueError):
        logger.exception(
            f"Salienz: Feld 'salienz' nicht numerisch ({roh!r}) — "
            f"fuer salienz_human uebergangen"
        )
        return None

    # ── Ausgabe ─────────────────────────────────
    return wert


def _salienz_anzeige(wert: float | None) -> str:
    """Formatiert einen Salienzwert fuer Log-Zeilen und Beschreibungen.

    Vorbedingung: wert ist ein geprueft numerischer Salienzwert oder None.
    Nachbedingung: zwei Nachkommastellen, oder 'unlesbar'.
    Fehlerfaelle: keine — genau dafuer gibt es die Funktion. Ein ungepruefter
        `:.2f` direkt auf der Modellantwort wirft ValueError, und der faellt an
        keinem der except-Zweige dieses Nodes ab: Ein einziges "hoch" statt 0.8
        riss bis Chat 112 den ganzen Turn ab.
    """
    return f"{wert:.2f}" if wert is not None else "unlesbar"


def _intentionen_human_ermitteln(roh_intentionen: list[str]) -> list[str]:
    """Fasst die Intentionen aller Segmente einer Nutzeraeusserung zusammen.

    Die **Vereinigung**, nicht das erste Segment: Ein Turn setzt eine Richtung,
    wenn irgendein Teil von ihm sie setzt. Dieselbe Begruendung wie bei
    `_salienz_human_ermitteln`, das aus demselben Grund `max()` nimmt — und
    dieselbe wie in `_wollen_messen`, das aus der Menge die staerkste Klasse
    zieht. Ein beilaeufiger Nebensatz darf eine Frage nicht verduennen.

    Die Reihenfolge des ersten Auftretens bleibt erhalten. Sie traegt keine
    Bedeutung fuer M1 (das maximiert), macht aber die Logzeile lesbar und den
    Vergleich mit dem KZG-Eintrag desselben Turns moeglich.

    Vorbedingung: `roh_intentionen` traegt die Werte der erfolgreich
        geparsten Segmente, in Segmentreihenfolge, ungeprueft.
    Nachbedingung: Liste ohne Doppelungen und ohne Leerwerte.
    Fehlerfaelle: Keine. Eine leere Liste heisst "keine Intention erhoben" und
        wird vom Empfaenger als **fehlend** gewertet, nicht als "keine
        Richtung" — die Unterscheidung sitzt in `ei/initiative.py`.

    Returns:
        Die Intentionen des Turns.
    """
    # ── Eingabe-Validierung ─────────────────────
    # Keine: Jede Liste ist verarbeitbar, auch die leere.

    # ── Verarbeitung ────────────────────────────
    gesehen: list[str] = []
    for wert in roh_intentionen:
        sauber: str = wert.strip()
        if sauber and sauber not in gesehen:
            gesehen.append(sauber)

    # ── Ausgabe-Verifikation ────────────────────
    if len(gesehen) != len(set(gesehen)):
        logger.error(
            "Salienz: Intentionen nach der Zusammenfassung nicht eindeutig: %s",
            gesehen,
        )

    return gesehen


def _salienz_human_ermitteln(roh_salienzen: list[float]) -> float | None:
    """Bestimmt die Salienz der Nutzeraeusserung aus ihren Segmentwerten.

    Das Maximum, nicht der Mittelwert: Ein Turn ist so gewichtig wie sein
    staerkster Teil. Ein beilaeufiger Nebensatz neben einer wichtigen Aussage
    darf den Wert nicht verduennen — dieselbe Begruendung, aus der die Formel
    max() statt einer Summe nimmt (novaberg-salienz-berechnung_k.md §3).

    Vorbedingung: roh_salienzen traegt die rohen LLM-Bewertungen der
        erfolgreich geparsten Segmente, ohne Gravitationsboost.
    Nachbedingung: Rueckgabe in [0.0, 1.0].
    Fehlerfaelle: leere Liste — None, damit der Aufrufer "nicht ermittelt" von
        "ermittelt und niedrig" unterscheiden kann.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not roh_salienzen:
        return None

    # ── Verarbeitung ────────────────────────────
    hoechste: float = max(roh_salienzen)

    # ── Ausgabe-Verifikation ────────────────────
    if not 0.0 <= hoechste <= 1.0:
        # Verarbeitbar, aber ausserhalb des vereinbarten Bereichs — Warnung,
        # nicht Fehler (DEVELOPER_HANDBOOK §4). Der Wert wird benannt, damit
        # die Kappung nicht als Messung durchgeht.
        logger.warning(
            f"Salienz: salienz_human ausserhalb [0,1] — Modell lieferte "
            f"{hoechste:.2f}, auf den Rand gekappt"
        )
        hoechste = max(0.0, min(1.0, hoechste))

    return hoechste


def analyze(
    state:        ConversationState,
    redis_client: redis.Redis,
    user_id:      str,
    postgres_url: str = ""
) -> ConversationState:
    """
    Analysiert den Turn. Segmentiert bei Bedarf in Teilaussagen.
    Legt pending_writes fuer KZG an (ohne Embedding, ohne kern).
    Schreibt NICHT in die DB — das macht der KZG-Agent via Dispatcher.

    Forensik (Chat 111, SALIENZ-OHNE-PIPELINE-LOG): Der Lauf haengt in einem
    Span und schreibt fuenf Arten von Eintraegen ins pipeline_log —
    switch (welcher Text bewertet wird), berechnung/segmentierung (der
    Schnitt), berechnung/bewertung (der Salienzwert je Segment),
    berechnung/gravitationsboost (die nachtraegliche Anhebung) und fehler
    (leeres Bewertungsobjekt, verworfenes Segment). Damit ist im Nachhinein
    ohne Container-Log beantwortbar, warum etwas erinnert wurde oder nicht.

    Vorbedingung: state traegt graph_rolle, turn_id und character_id;
        fehlen sie, greifen die dokumentierten Defaults ("human",
        "unbekannt", "").
    Nachbedingung: state["pending_writes"] ist gesetzt — eine Liste mit
        einem Eintrag je erfolgreich bewertetem Segment. Der Span ist in
        jedem Rueckgabepfad geschlossen.
    Fehlerfaelle: leeres Bewertungsobjekt (kein pending_write, fehler-
        Eintrag, frueher return); JSON-Parsing je Segment (Segment
        verworfen, fehler-Eintrag, Lauf geht weiter).
    """
    # Input-Switch nach graph_rolle (PFAD2-PERZEPTION-FIX Phase 2, korrigiert
    # Chat 110). Nur der CharacterGraph bewertet eine REAKTION — er ist der
    # einzige Graph mit Responder. HumanGraph und AgentGraph bewerten beide
    # einen REIZ; sie unterscheiden sich darin, von wem er stammt.
    #
    # Vorher hing der Switch an ei_calc_rolle. Der AgentGraph setzt die auf
    # "character" (damit beobachter="assistant" wird) und landete dadurch im
    # Reaktions-Zweig — mit einer response, die er nie erzeugt. Gemessen
    # 26.07.2026: bewertungs_laenge=0 in jedem AgentGraph-Lauf, das
    # Wissensstueck lag ungelesen im [LAGEBILD].
    rolle: str = state.get("graph_rolle", "human")

    # Gelesen wird der Reiz dieses Durchlaufs, nicht der Reiz-Platz. Auf einem
    # Impuls-Turn ist `user_prompt` leer, weil niemand gesprochen hat — der
    # Gegenstand steht dort in `eigener_gedanke`. Wer den Platz liest, bewertet
    # auf einem vollstaendigen Turn ein leeres Objekt und bricht ab.
    reiz: str = reiz_text(state)

    if rolle == "character":
        bewertungs_text: str = state.get("response", "")
        lagebild_text:   str = reiz
        lagebild_label:  str = "Dies ist die Eingabe des Nutzers."
        eingabe_label:   str = "Antwort der Assistentin"
    elif rolle == "agent":
        # Novas eigener Gedanke. Kein Lagebild — es gibt kein Gegenueber, auf
        # das er antwortet, und eine leere response als Hintergrund waere eine
        # Behauptung ueber etwas, das nicht stattgefunden hat.
        bewertungs_text = reiz
        lagebild_text   = ""
        lagebild_label  = ""
        eingabe_label   = "Eigener Gedanke der Assistentin"
    else:
        bewertungs_text = reiz
        lagebild_text   = state.get("response", "")
        lagebild_label  = "Dies ist die Antwort des Assistenten."
        eingabe_label   = "Eingabe des Nutzers"

    logger.info(
        f"Salienz: graph_rolle={rolle}, bewertungs_laenge={len(bewertungs_text)}, "
        f"lagebild_laenge={len(lagebild_text)}"
    )

    # ── Pipeline-Log: Span-Start ────────────────
    # quelle traegt durchgaengig die Graph-Rolle, nicht eine semantische
    # Unterquelle wie beim Enricher. Der Salienz-Node hat nur eine Datenquelle
    # — den Turn selbst —, ein Unterlabel truege also keine Information. Die
    # Rolle dagegen ist genau der Unterscheider, der bis Chat 110 fehlte: Der
    # AgentGraph lief als "character" mit und war im Log nicht zu trennen.
    turn_id_log:  str = state.get("turn_id", "unbekannt")
    quelle_log:   str = pipeline_quelle(state)
    character_id: str = state.get("character_id", "")
    span_id           = span_start(
        turn_id = turn_id_log,
        node    = "salienz",
        quelle  = quelle_log,
        user_id      = user_id,
        character_id = character_id,
    )

    # Der Prompt wird HIER gebaut, vor der switch-Zeile, damit diese den
    # tatsaechlich verwendeten Aufgaben-Block nennen kann statt einen zweiten
    # Mal aus der Rolle abgeleiteten. Beides getrennt abzuleiten war der erste
    # Entwurf, und die Gegenprobe blieb dabei gruen: Der Node zog fuer jede
    # Rolle die Nutzer-Schablone, und das Log meldete trotzdem die richtige.
    salienz_prompt: str
    aufgaben_block: str
    salienz_prompt, aufgaben_block = _build_salienz_prompt(rolle)

    # Welcher Text bewertet wird und welcher nur Hintergrund ist, war bis
    # jetzt nur im fluechtigen Container-Log sichtbar. Genau diese Zeile haette
    # bewertungs_laenge=0 im AgentGraph sofort gezeigt (SALIENZ-OHNE-PIPELINE-LOG).
    log_switch(
        turn_id = turn_id_log,
        node    = "salienz",
        quelle  = quelle_log,
        inhalt  = {
            "graph_rolle":       rolle,
            "eingabe_label":     eingabe_label,
            "bewertungs_laenge": len(bewertungs_text),
            "lagebild_laenge":   len(lagebild_text),
            # Welche Schablone gezogen wurde. Bis Chat 112 gab es nur eine, und
            # dass sie im CharacterGraph die falsche war, stand nirgends —
            # weder im Log noch in der Datenbank (SALIENZ-PROMPT-NUTZER-SCHABLONE).
            "aufgaben_block":    aufgaben_block,
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    # Fail loud statt still bewerten: Ein leeres Bewertungsobjekt liefert
    # zwangslaeufig Unsinn — das LLM klassifiziert dann das Lagebild oder
    # halluziniert Themen. Genau so entstand "Soziale Interaktion, Begruessung"
    # fuer einen Fachtext ueber Quark-Gluon-Plasma (gemessen 26.07.2026).
    if not bewertungs_text.strip():
        logger.error(
            f"Salienz: Bewertungsobjekt leer — kein pending_write erzeugt "
            f"(graph_rolle={rolle}, lagebild_laenge={len(lagebild_text)})"
        )
        log_fehler(
            turn_id = turn_id_log,
            node    = "salienz",
            quelle  = quelle_log,
            inhalt  = {
                "grund":           "bewertungsobjekt_leer",
                "graph_rolle":     rolle,
                "lagebild_laenge": len(lagebild_text),
                "pending_writes":  0,
            },
            span_id = span_id,
            user_id      = user_id,
            character_id = character_id,
        )
        span_end(
            turn_id = turn_id_log,
            node    = "salienz",
            quelle  = quelle_log,
            span_id = span_id,
            inhalt  = {"segmente": 0, "pending_writes": 0, "abbruch": True},
            user_id      = user_id,
            character_id = character_id,
        )
        state["pending_writes"] = state.get("pending_writes", []) or []
        return state

    # ── Prompt segmentieren ──────────────────
    segmente: list[str] = _prompt_segmentieren(bewertungs_text)

    # Der Segmentschnitt entscheidet, wie viele KZG-Eintraege ein Turn
    # erzeugt — jedes Segment einen. Ohne diese Zeile ist im Nachhinein nicht
    # feststellbar, ob mehrere Eintraege auf einen langen Text zurueckgehen
    # oder auf mehrere Reize (KZG-SEGMENT-DUPLIKAT).
    log_berechnung(
        turn_id = turn_id_log,
        node    = "salienz",
        quelle  = quelle_log,
        inhalt  = {
            "schritt":         "segmentierung",
            "segmente":        len(segmente),
            "segment_laengen": [len(s) for s in segmente],
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    pending:       list[dict] = state.get("pending_writes", []) or []
    gesamt_tokens: int        = 0

    # Die rohen LLM-Bewertungen je Segment, vor dem Gravitationsboost. Nur der
    # HumanGraph wertet sie unten zu salienz_human aus; gesammelt wird in jedem
    # Lauf, damit die Sammelstelle nicht an einer Rollen-Bedingung haengt und
    # bei der naechsten Rollen-Aenderung still leer bleibt.
    roh_salienzen: list[float] = []
    roh_intentionen: list[str] = []

    # ── Zwei Groessen fuer die Salienz-Formel, einmal je Turn ──
    # Beide sind Eigenschaften des Paares bzw. des Turns, keine Merkmale eines
    # Segments — sie gehoeren deshalb vor die Schleife und nicht hinein.
    #
    # Genau darin liegt die heute noch offene Schwaeche: Ausser der Lesung des
    # Segmenttexts ist jede Eingabe der Formel turnweit. Solange das so ist,
    # unterscheidet allein `sprachlich` ein Segment von seinem Nachbarn.
    nutzer_gewichtung: float | None = None
    gewichtung_quelle: str          = "nicht_gebraucht"

    if rolle in ("character", "agent"):
        if postgres_url:
            nutzer_gewichtung, gewichtung_quelle = nutzer_gewichtung_laden(
                postgres_url, user_id,
            )
        else:
            # Kein stiller Ruecktritt auf 0.9: Ohne Datenbank ist der Faktor
            # nicht bekannt, und ein angenommener saehe aus wie ein gelesener.
            gewichtung_quelle = "fehlt"
            logger.error(
                f"Salienz: kein postgres_url — nutzer_gewichtung nicht ladbar, "
                f"der Pflicht-Pfad entfaellt fuer turn_id={state.get('turn_id', 'unbekannt')}"
            )

    # Novas eigene Erregung speist den Verstaerker (1 + zuschlag).
    internal = state.get("internal")
    if internal is not None:
        nova_arousal: float = internal.emotion.arousal
    else:
        # 0.0 statt eines mittleren 0.5: Ein erfundener Mittelwert truege 15 %
        # Zuschlag auf jedes Segment, ohne dass irgendetwas gemessen waere.
        # Kein Verstaerker ist die ehrliche Antwort auf "nicht bekannt".
        nova_arousal = 0.0
        logger.warning(
            "Salienz: kein internal im State — Erregungs-Zuschlag entfaellt (0.0)"
        )

    logger.info(f"Salienz: System-Prompt ({aufgaben_block}):\n{salienz_prompt}")

    for seg_idx, segment in enumerate(segmente):

        if len(segmente) > 1:
            logger.info(f"Salienz: Segment {seg_idx + 1}/{len(segmente)}: {segment[:60]}...")

        segment_hinweis: str = ""
        if len(segmente) > 1:
            segment_hinweis = (
                f"\nHINWEIS: Dies ist Segment {seg_idx + 1} von {len(segmente)} "
                f"aus einem laengeren Prompt. Analysiere NUR dieses Segment. "
                f"Ignoriere Inhalte aus anderen Teilen des Prompts.\n"
            )

        lagebild: str = ""
        if lagebild_text:
            lagebild = (
                "[LAGEBILD]\n"
                f"Hintergrund — nicht bewerten. {lagebild_label}\n\n"
                f"{lagebild_text}\n\n"
            )

        analyse_prompt: str = (
            f"{lagebild}"
            "[BEWERTUNGSOBJEKT]\n"
            "Analysiere und bewerte NUR den folgenden Teil.\n"
            f"{segment_hinweis}"
            f"{eingabe_label}:\n{segment}"
        )

        node_cfg = get_node_config("salienz")

        # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G1) ──
        # analyze() laeuft im HumanGraph aus api/chat.py:chat_senden (sync def
        # im FastAPI-Threadpool). Kein Event-Loop im aufrufenden Thread →
        # submit_sync bruckt in den Worker-Loop (Loop-Binding-Lesson).
        chat_request = ChatRequest(
            messages          = [{"role": "user", "content": analyse_prompt}],
            system            = salienz_prompt,
            temperature       = node_cfg.get("temperature", 0.05),
            expect_json       = True,
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "salienz",
        )

        try:
            response = model_service.chat.submit_sync(chat_request)
            gesamt_tokens += response.token_total
            logger.debug(f"Salienz RAW: '{response.text[:500]}'")
            salienz_obj: dict = response.parsed

            if "arousal" in salienz_obj:
                salienz_obj["arousal"] = max(0.0, min(1.0, float(salienz_obj.get("arousal", 0.5))))

            # Magnet-Roh-Felder defensiv normalisieren (P3, Synapsen-Sprint).
            # Salience liefert hier nur Roh-Strings; die eigentliche Aufloesung
            # zu entitaet_ids/timeline_id geschieht im magnete_aufloesen-Node
            # des KzgAgent-Subgraphen.
            roh_entitaeten = salienz_obj.get("entitaeten_roh", []) or []
            if not isinstance(roh_entitaeten, list):
                roh_entitaeten = []
            salienz_obj["entitaeten_roh"] = [
                n.strip() for n in roh_entitaeten
                if isinstance(n, str) and n.strip()
            ]
            roh_zeit = salienz_obj.get("zeitausdruck_roh", "") or ""
            salienz_obj["zeitausdruck_roh"] = str(roh_zeit).strip()

            # Den rohen Wert lesen, BEVOR der Gravitationsboost ihn veraendert.
            # salienz_human ist laut Konzept die LLM-Bewertung der
            # Nutzeraeusserung — die Gravitation wird mit der neuen Formel zu
            # einem Antrieb des Eigen-Pfads und zaehlte hier ein zweites Mal.
            #
            # Der Aufruf steht vor der Log-Zeile, nicht dahinter: Die Zeile
            # formatierte den Wert bis Chat 112 ungeprueft mit `:.2f`. Liefert
            # das Modell dort eine Zeichenkette, wirft das einen ValueError —
            # und der faellt nicht in das except unten, das nur
            # JSONDecodeError und KeyError kennt. Ein einziges "hoch" statt 0.8
            # riss damit den ganzen Turn ab.
            # Die Modellbewertung einmal festhalten — danach ist sie die
            # Eingabe jedes weiteren Segments, und `salienz` darf das Ergebnis
            # tragen, ohne die naechste Rechnung zu speisen.
            if "salienz_modell" not in salienz_obj and "salienz" in salienz_obj:
                salienz_obj["salienz_modell"] = salienz_obj["salienz"]

            roh_wert: float | None = _salienz_wert_lesen(salienz_obj)
            if roh_wert is not None:
                roh_salienzen.append(roh_wert)
                roh_intentionen.extend(
                    str(i) for i in salienz_obj.get("intentionen", []) or []
                )

            logger.info(
                f"Salienz: score={_salienz_anzeige(roh_wert)}, "
                f"themen={salienz_obj.get('themen', [])}, "
                f"dimension={salienz_obj.get('dimension', '-')}, "
                f"typ={salienz_obj.get('gedaechtnistyp', '-')}, "
                f"intentionen={salienz_obj.get('intentionen', [])}, "
                f"emotion={salienz_obj.get('emotion', '-')}, "
                f"modus={salienz_obj.get('modus', '-')}, "
                f"entitaeten_roh={salienz_obj.get('entitaeten_roh', [])}, "
                f"zeitausdruck_roh='{salienz_obj.get('zeitausdruck_roh', '')}'"
            )

            # Der Wert, der ueber Erinnern entscheidet — ab hier dauerhaft
            # und ohne Container-Log beantwortbar.
            log_berechnung(
                turn_id = turn_id_log,
                node    = "salienz",
                quelle  = quelle_log,
                inhalt  = {
                    "schritt":        "bewertung",
                    "segment_index":  seg_idx,
                    "segment_gesamt": len(segmente),
                    "segment_laenge": len(segment),
                    "segment_kurz":   segment[:60],
                    # Der geprueft numerische Wert, nicht die rohe Modellantwort:
                    # Sonst stuende im forensischen Log eine Zeichenkette, wo
                    # jede spaetere Auswertung eine Zahl erwartet.
                    "salienz":        roh_wert,
                    "themen":         salienz_obj.get("themen", []),
                    "dimension":      salienz_obj.get("dimension", ""),
                    "gedaechtnistyp": salienz_obj.get("gedaechtnistyp", ""),
                    "emotion":        salienz_obj.get("emotion", ""),
                    "arousal":        salienz_obj.get("arousal", None),
                    "modus":          salienz_obj.get("modus", ""),
                },
                span_id = span_id,
                user_id      = user_id,
                character_id = character_id,
            )

        except (json.JSONDecodeError, KeyError) as fehler:
            # Ein uebersprungenes Segment ist ein Fehler, keine Warnung
            # (DEVELOPER_HANDBOOK §3: silent skip mit warning ist verboten).
            # Der Turn verliert hier still einen Gedaechtnis-Eintrag.
            logger.exception(
                f"{type(fehler).__name__}: Salienz: JSON-Parsing fehlgeschlagen — "
                f"Segment {seg_idx + 1}/{len(segmente)} verworfen, kein pending_write"
            )
            log_fehler(
                turn_id = turn_id_log,
                node    = "salienz",
                quelle  = quelle_log,
                inhalt  = {
                    "grund":          "json_parsing",
                    "fehler_typ":     type(fehler).__name__,
                    "segment_index":  seg_idx,
                    "segment_gesamt": len(segmente),
                    "segment_laenge": len(segment),
                },
                span_id = span_id,
                user_id      = user_id,
                character_id = character_id,
            )
            continue

        # ── Gravitationsterm auf Salienz addieren (Drive) ──
        gravitationsterm: float = state.get("gravitationsterm", 0.0)

        # Der Wert, der am Ende dieses Segments gilt. None heisst, das Modell
        # lieferte nichts Lesbares.
        salienz_segment: float | None = roh_wert

        if rolle in ("character", "agent") and roh_wert is not None:
            # ── Die Salienz-Formel (Chat 112, Bauteil 1b) ──
            # Fuer Novas eigene Aeusserung wird die Salienz gerechnet, nicht
            # allein gefragt: max(sein Interesse × ihr Charakter, ihr Antrieb).
            # Der Gravitationsboost entfaellt hier — die Gravitation ist jetzt
            # einer der Antriebe des Eigen-Pfads und zaehlte sonst zweimal.
            ergebnis = salienz_effektiv_berechnen(
                sprachlich        = roh_wert,
                ziel_gravitation  = gravitationsterm,
                arousal           = nova_arousal,
                salienz_human     = state.get("salienz_human"),
                nutzer_gewichtung = nutzer_gewichtung,
            )

            salienz_obj["salienz"] = ergebnis.effektiv
            salienz_segment        = ergebnis.effektiv

            logger.info(
                f"Salienz-Formel: effektiv={ergebnis.effektiv:.4f} "
                f"(Gewinner '{ergebnis.gewinner}') — "
                f"pflicht={ergebnis.pflicht_pfad} "
                f"(human={state.get('salienz_human')} × gew={nutzer_gewichtung}, "
                f"Herkunft '{gewichtung_quelle}'), "
                f"eigen={ergebnis.eigen_pfad:.4f} "
                f"(Antriebe {ergebnis.antriebe}, Zuschlag {ergebnis.erregungs_zuschlag:.3f}), "
                f"nicht angeschlossen: {list(ergebnis.nicht_angeschlossen)}"
                + (" — GEKAPPT auf 1.0" if ergebnis.gekappt else "")
            )

            # Beide Operanden ins Log, nicht nur das Ergebnis: Sonst ist im
            # Nachhinein nicht feststellbar, ob ein Segment erinnert wurde,
            # weil es Nova etwas bedeutete oder weil es dem Nutzer etwas
            # bedeutete — und genau das ist der Zweck der Formel.
            log_berechnung(
                turn_id = turn_id_log,
                node    = "salienz",
                quelle  = quelle_log,
                inhalt  = {
                    "schritt":             "salienz_formel",
                    "segment_index":       seg_idx,
                    "salienz_effektiv":    ergebnis.effektiv,
                    "gewinner":            ergebnis.gewinner,
                    "pflicht_pfad":        ergebnis.pflicht_pfad,
                    "salienz_human":       state.get("salienz_human"),
                    "nutzer_gewichtung":   nutzer_gewichtung,
                    "gewichtung_quelle":   gewichtung_quelle,
                    "eigen_pfad":          ergebnis.eigen_pfad,
                    "antriebe":            ergebnis.antriebe,
                    "nicht_angeschlossen": list(ergebnis.nicht_angeschlossen),
                    "erregungs_zuschlag":  ergebnis.erregungs_zuschlag,
                    "gekappt":             ergebnis.gekappt,
                },
                span_id = span_id,
                user_id      = user_id,
                character_id = character_id,
            )

        # `roh_wert is not None` statt eines ungeprueften .get(): Die Addition
        # unten bricht mit TypeError ab, wenn dort eine Zeichenkette steht.
        # Dieselbe Klasse wie die Log-Zeile darueber — an einer Stelle
        # diagnostiziert, sass sie schon an der zweiten.
        elif gravitationsterm > 0.0 and roh_wert is not None:
            salienz_basis: float = roh_wert
            salienz_neu:   float = min(1.0, salienz_basis + gravitationsterm)
            salienz_obj["salienz"] = round(salienz_neu, 2)
            salienz_segment        = salienz_obj["salienz"]

            logger.info(
                f"Salienz: Gravitationsboost — "
                f"basis={salienz_basis:.2f} + grav={gravitationsterm:.3f} "
                f"= {salienz_neu:.2f}"
            )

            # Der Boost veraendert den Wert nach der Bewertung. Ohne eigene
            # Zeile waere im Nachhinein nicht trennbar, ob eine hohe Salienz
            # vom Modell kam oder von der Ziel-Gravitation.
            log_berechnung(
                turn_id = turn_id_log,
                node    = "salienz",
                quelle  = quelle_log,
                inhalt  = {
                    "schritt":          "gravitationsboost",
                    "segment_index":    seg_idx,
                    "salienz_basis":    salienz_basis,
                    "gravitationsterm": gravitationsterm,
                    "salienz_neu":      salienz_obj["salienz"],
                },
                span_id = span_id,
                user_id      = user_id,
                character_id = character_id,
            )

        # ── pending_write fuer KZG-Agent (ohne Embedding, ohne kern) ─
        # Das Segment reist mit. Bis Chat 111 trug `daten` nur das
        # salienz_obj; der Verdichter bekam den Turn-Volltext aus dem State und
        # fasste ihn je Segment erneut zusammen — drei Segmente ergaben drei
        # Paraphrasen desselben Absatzes, die uebrigen Segmente landeten nie im
        # Gedaechtnis (gemessen 27.07.2026 an Turn 975ec093...).
        #
        # salienz_obj bleibt, was das Modell gesagt hat; das Segment ist, was
        # es gelesen hat. Zwei verschiedene Dinge, zwei Felder.
        pending.append({
            "ziel":         "kzg",
            "aktion":       "create",
            "daten": {
                "salienz_obj":    salienz_obj,
                "segment":        segment,
                "segment_index":  seg_idx,
                "segment_gesamt": len(segmente),
                # Der Turn, aus dem der Eintrag entsteht. Bis zum 28.08.2026
                # kam er nie beim KZG-Store an — 0 von 300 KZG-Hashes trugen
                # eine turn_id — und damit auch nicht beim Auftrag, der aus
                # dem Eintrag entsteht (Sachlage-Bruecke, erstes Glied).
                "turn_id":        state.get("turn_id", ""),
            },
            "beschreibung": f"KZG: {', '.join(salienz_obj.get('themen', []))} "
                            f"(salienz={_salienz_anzeige(salienz_segment)}, "
                            f"Segment {seg_idx + 1}/{len(segmente)})",
        })

    state["pending_writes"] = pending

    logger.info(f"Salienz: {len(pending)} pending_writes angelegt ({len(segmente)} Segment(e))")

    # ── Salienz der Nutzeraeusserung festhalten (Chat 112) ──
    # Nur der HumanGraph bewertet eine Nutzeraeusserung. Der CharacterGraph
    # bewertet gerade Novas Antwort und bekommt salienz_human ueber das
    # Event-Payload gereicht — schriebe er hier, ueberschriebe er den Reiz mit
    # der Reaktion. Der AgentGraph hat keine Nutzeraeusserung; dort bleibt das
    # Feld None, und die Formel faellt dort bestimmungsgemaess auf den
    # Eigen-Pfad zusammen (novaberg-salienz-berechnung_k.md §9).
    #
    # Der Wert wird hier gesetzt und nicht vom Aufrufer aus den pending_writes
    # gelesen: Der Dispatcher laeuft als letzter Node und leert sie
    # (dispatcher.py, _dispatch_writes). Wer danach liest, bekommt eine leere
    # Liste und daraus still None.
    if rolle == "human":
        state["salienz_human"] = _salienz_human_ermitteln(roh_salienzen)

        # Die Intentionen desselben Reizes. Sie reisen mit demselben Ereignis
        # in den CharacterGraph wie `salienz_human` und sind dort die Quelle
        # von M1 der Initiative-Achse (`ei/initiative.py`).
        #
        # Warum sie hier entstehen und nicht im CharacterGraph: Der
        # Salienz-Node von Pfad 2 laeuft NACH dem GV-Node. Wer die Intentionen
        # erst dort holt, holt sie eine Node-Laenge zu spaet — die Achse hat
        # dann nichts. Pfad 1 hat sie bereits erhoben, bevor Pfad 2 startet.
        state["user_intentionen"] = _intentionen_human_ermitteln(roh_intentionen)

        logger.info(
            "Salienz: Intentionen des Reizes: %s (aus %d Segment(en))",
            state["user_intentionen"] or "keine",
            len(roh_salienzen),
        )

        if state["salienz_human"] is None:
            # Ohne den Wert hat der CharacterGraph keinen Boden fuer seine
            # Segmente. Das ist ein Verlust, keine Randnotiz — und er faellt
            # sonst nirgends auf, weil der Turn ansonsten sauber durchlaeuft.
            logger.error(
                f"Salienz: salienz_human nicht ermittelbar — {len(segmente)} "
                f"Segment(e) bewertet, keines lieferte einen lesbaren Wert. "
                f"Der CharacterGraph bekommt fuer turn_id={turn_id_log} keinen Boden."
            )
            log_fehler(
                turn_id = turn_id_log,
                node    = "salienz",
                quelle  = quelle_log,
                inhalt  = {
                    "grund":         "salienz_human_unermittelbar",
                    "segmente":      len(segmente),
                    "lesbare_werte": len(roh_salienzen),
                },
                span_id = span_id,
                user_id      = user_id,
                character_id = character_id,
            )
        else:
            # Den Wert nennen, nicht die Anzahl: Ein Setzer ohne Log-Zeile ist
            # nicht messbar, und eine Zeile, die nur zaehlt, macht ihre Frage
            # unbeobachtbar.
            logger.info(
                f"Salienz: salienz_human={state['salienz_human']:.2f} "
                f"(Maximum aus {len(roh_salienzen)} Segment(en): "
                f"{[round(w, 2) for w in roh_salienzen]})"
            )
            log_berechnung(
                turn_id = turn_id_log,
                node    = "salienz",
                quelle  = quelle_log,
                inhalt  = {
                    "schritt":       "salienz_human",
                    "salienz_human": state["salienz_human"],
                    "segmentwerte":  [round(w, 4) for w in roh_salienzen],
                    "segmente":      len(segmente),
                },
                span_id = span_id,
                user_id      = user_id,
                character_id = character_id,
            )

    # ── Token-Zaehler aktualisieren ───────────
    state["token_total"] += gesamt_tokens

    # ── Pipeline-Log: Span-Ende ─────────────────
    # Die Klammer zu span_start. Weniger pending_writes als Segmente heisst,
    # dass unterwegs mindestens eines verworfen wurde — die Differenz ist ohne
    # Container-Log sichtbar, die Begruendung steht in den fehler-Eintraegen.
    span_end(
        turn_id = turn_id_log,
        node    = "salienz",
        quelle  = quelle_log,
        span_id = span_id,
        inhalt  = {
            "segmente":       len(segmente),
            "pending_writes": len(pending),
            "token_total":    gesamt_tokens,
            "abbruch":        False,
        },
        user_id      = user_id,
        character_id = character_id,
    )

    return state
