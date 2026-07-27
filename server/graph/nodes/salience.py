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

from graph.state import ConversationState, pipeline_quelle
from config import get_node_config, PROMPTS
from memory.pipeline_log import (
    span_start,
    span_end,
    log_switch,
    log_berechnung,
    log_fehler,
)
from services.model_services import model_service, ChatRequest

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
        # api/chat.py:ChatSenden (sync def im FastAPI-Threadpool). Kein
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


def _build_salienz_prompt() -> str:
    """Baut den Salienz-System-Prompt aus [BLOCKNAME]-Bloecken zusammen."""
    return "\n\n".join([
        PROMPTS["salienz.identity"],
        PROMPTS["salienz.task"],
        PROMPTS["salienz.rules"],
    ])


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

    if rolle == "character":
        bewertungs_text: str = state.get("response", "")
        lagebild_text:   str = state.get("user_prompt", "")
        lagebild_label:  str = "Dies ist die Eingabe des Nutzers."
        eingabe_label:   str = "Antwort der Assistentin"
    elif rolle == "agent":
        # Novas eigener Gedanke. Kein Lagebild — es gibt kein Gegenueber, auf
        # das er antwortet, und eine leere response als Hintergrund waere eine
        # Behauptung ueber etwas, das nicht stattgefunden hat.
        bewertungs_text = state.get("user_prompt", "")
        lagebild_text   = ""
        lagebild_label  = ""
        eingabe_label   = "Eigener Gedanke der Assistentin"
    else:
        bewertungs_text = state.get("user_prompt", "")
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

    salienz_prompt: str = _build_salienz_prompt()

    logger.info(f"Salienz: System-Prompt:\n{salienz_prompt}")

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
        # analyze() laeuft im HumanGraph aus api/chat.py:ChatSenden (sync def
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

            logger.info(
                f"Salienz: score={salienz_obj.get('salienz', 0):.2f}, "
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
                    "salienz":        salienz_obj.get("salienz", 0.0),
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
            logger.error(
                f"Salienz: JSON-Parsing fehlgeschlagen ({type(fehler).__name__}: {fehler}) — "
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

        if gravitationsterm > 0.0:
            salienz_basis: float = salienz_obj.get("salienz", 0.0)
            salienz_neu:   float = min(1.0, salienz_basis + gravitationsterm)
            salienz_obj["salienz"] = round(salienz_neu, 2)

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
            },
            "beschreibung": f"KZG: {', '.join(salienz_obj.get('themen', []))} "
                            f"(salienz={salienz_obj.get('salienz', 0):.2f}, "
                            f"Segment {seg_idx + 1}/{len(segmente)})",
        })

    state["pending_writes"] = pending

    logger.info(f"Salienz: {len(pending)} pending_writes angelegt ({len(segmente)} Segment(e))")

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
