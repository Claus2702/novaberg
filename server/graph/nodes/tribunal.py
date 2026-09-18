"""
Tribunal Node — Bewertet die generierte Antwort aus drei Perspektiven.
Jeder Agent ist eine eigenstaendige Funktion mit eigenem System-Prompt.
Agenten koennen ergaenzt, ersetzt oder deaktiviert werden.

Architektur:
  Responder -> Jurist -> Psychologe -> Ethik -> Auswertung -> Entscheidung

Voting-System:
  2x ablehnen  -> ablehnen
  2x warnung   -> warnung (mit Korrektur)
  sonst        -> ok

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).
"""

import json
import logging
from datetime import datetime

from config import (
    PROMPTS,
    TRIBUNAL_ETHIK_ABLEHNEN,
    TRIBUNAL_ETHIK_WARNUNG,
    TRIBUNAL_JURIST_ABLEHNEN,
    TRIBUNAL_JURIST_DIREKTIVE_ABLEHNEN,
    TRIBUNAL_JURIST_DIREKTIVE_WARNUNG,
    TRIBUNAL_JURIST_WARNUNG,
    TRIBUNAL_PSYCHOLOGE_ABLEHNEN,
    TRIBUNAL_PSYCHOLOGE_WARNUNG,
    get_node_config,
)
from graph.antwort_spur import antwort_setzen
from graph.reiz import reiz_text
from graph.state import ConversationState, TribunalVote
from memory.pipeline_log import log_berechnung
from services.model_services import ChatRequest, model_service
from utils.datum_pruefung import (
    bestaetigung_pruefen,
    bestaetigungsauftrag,
    korrekturauftrag,
    widersprueche_finden,
)
from utils.storage_claims import (
    ORDER_HEADER,
    RULE_VERSION,
    ClaimCheck,
    append_correction,
    correction_order,
    uncovered_claims,
)

logger = logging.getLogger("ki_server.tribunal")


AGENTS: list[dict[str, str]] = [
    {
        "name": "jurist",
        "system_prompt": PROMPTS["tribunal_jurist.system"],
    },
    {
        "name": "psychologe",
        "system_prompt": PROMPTS["tribunal_psychologe.system"],
    },
    {
        "name": "ethik",
        "system_prompt": PROMPTS["tribunal_ethik.system"],
    },
]


# ─────────────────────────────────────────────
# Score → Vote Ableitung (T1)
# ─────────────────────────────────────────────

_SCHWELLWERTE: dict[str, tuple[float, float]] = {
    "jurist":     (TRIBUNAL_JURIST_WARNUNG,     TRIBUNAL_JURIST_ABLEHNEN),
    "psychologe": (TRIBUNAL_PSYCHOLOGE_WARNUNG, TRIBUNAL_PSYCHOLOGE_ABLEHNEN),
    "ethik":      (TRIBUNAL_ETHIK_WARNUNG,      TRIBUNAL_ETHIK_ABLEHNEN),
}


_VOTE_RANK: dict[str, int] = {"ok": 0, "warnung": 1, "ablehnen": 2}

def _score_to_vote(agent_name: str, score: float) -> str:
    """Leitet Vote aus Score und konfigurierbaren Schwellwerten ab."""
    warnung_schwelle, ablehnen_schwelle = _SCHWELLWERTE.get(
        agent_name, (0.7, 0.9)
    )
    if score >= ablehnen_schwelle:
        return "ablehnen"
    elif score >= warnung_schwelle:
        return "warnung"
    return "ok"


def _score_to_vote_direktive(score: float) -> str:
    """Leitet Vote aus Direktiven-Score mit strengeren Schwellwerten ab."""
    if score >= TRIBUNAL_JURIST_DIREKTIVE_ABLEHNEN:
        return "ablehnen"
    elif score >= TRIBUNAL_JURIST_DIREKTIVE_WARNUNG:
        return "warnung"
    return "ok"


# ─────────────────────────────────────────────
# Einzelner Agent-Aufruf (generisch)
# ─────────────────────────────────────────────
def _agent_vote(
    agent_name:    str,
    system_prompt: str,
    state:         ConversationState,
) -> TribunalVote:
    """Fuehrt einen einzelnen Tribunal-Agenten aus und gibt sein Votum zurueck."""
    external = state.get("external")
    intent: str = external.emotion.intent if external else "smalltalk"
    tone:   str = external.emotion.tone   if external else "sachlich"

    msg_parts: list[str] = [
        "[LAGEBILD]\n"
        "Hintergrund — nicht Teil der Bewertung. "
        "Erklaert den Kontext des Nutzers.\n\n"
        f"Intent: {intent}\n"
        f"Gewuenschter Ton: {tone}"
    ]

    if state.get("memory_context"):
        msg_parts[0] += (
            f"\n\nPersoenlicher Kontext des Nutzers:\n"
            f"{state['memory_context']}"
        )

    if state.get("node_annotations"):
        msg_parts.append(
            "[ANMERKUNGEN]\n"
            "Qualifizierte Hinweise vorheriger Pruefungen.\n\n"
            + "\n".join(state["node_annotations"])
        )

    # Direktiven als Pruefkriterium (differenziert pro Agent) — aus internal.directives
    internal = state.get("internal")
    direktiven: list[dict] = list(internal.directives) if internal else []
    if direktiven:
        if agent_name == "jurist":
            # Jurist: Vertragspruefer — woertliche Pruefung
            dir_zeilen: list[str] = []
            for d in direktiven:
                if isinstance(d, dict):
                    dir_zeilen.append(f"- {d.get('anweisung', '')}")
                    kontext = d.get("kontext", "")
                    if kontext:
                        dir_zeilen.append(f"  (Kontext: {kontext})")
                else:
                    dir_zeilen.append(f"- {d}")
            dir_text: str = "\n".join(dir_zeilen)
            msg_parts.append(
                PROMPTS["tribunal_jurist.direktiven_pruefung"].format(
                    direktiven_text=dir_text
                )
            )
        # Psychologe + Ethiker: keine Direktiven-Pruefung

    msg_parts.append(
        "[BEWERTUNGSOBJEKT]\n"
        "Bewerte NUR den folgenden Teil.\n\n"
        f"Benutzeranfrage:\n{reiz_text(state)}\n\n"
        f"Antwort des Assistenten:\n{state['response']}"
    )

    bewertungs_prompt: str = "\n\n".join(msg_parts)

    logger.info(f"Tribunal [{agent_name}]: Bewerte Antwort...")
    logger.info(f"Tribunal [{agent_name}]: System-Prompt:\n{system_prompt}")
    logger.info(f"Tribunal [{agent_name}]: Bewertungs-Prompt:\n{bewertungs_prompt}")

    node_cfg = get_node_config("tribunal")

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G2) ──
    # _agent_vote() laeuft im CharacterGraph (services/event_consumer.py ruft
    # den Graphen via asyncio.to_thread(_graph_streamen, ...) im Worker-
    # Thread). Kein Event-Loop im aufrufenden Thread → submit_sync bruckt in
    # den Worker-Loop (Loop-Binding-Lesson).
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": bewertungs_prompt}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.2),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = f"tribunal/{agent_name.lower()}",
    )

    try:
        response = model_service.chat.submit_sync(chat_request)
        ergebnis: dict = response.parsed
        reasoning: str = ergebnis.get("reasoning", "")

        # Score-Auswertung mit Fallback auf altes Format
        raw_score = ergebnis.get("score")
        if raw_score is None:
            # Fallback: altes vote-Format
            old_vote: str = ergebnis.get("vote", "ok")
            score: float = {"ok": 0.0, "warnung": 0.7, "ablehnen": 1.0}.get(old_vote, 0.0)
            direktiven_score: float = 0.0
            derived_vote: str = old_vote
        else:
            score = max(0.0, min(1.0, float(raw_score)))

            if agent_name == "jurist":
                # Dual-Score: allgemein + Direktiven
                direktiven_score = max(0.0, min(1.0, float(ergebnis.get("direktiven_score", 0.0))))
                allgemein_vote: str = _score_to_vote("jurist", score)
                dir_vote: str = _score_to_vote_direktive(direktiven_score)
                derived_vote = max([allgemein_vote, dir_vote], key=lambda v: _VOTE_RANK[v])
            else:
                direktiven_score = 0.0
                derived_vote = _score_to_vote(agent_name, score)

        vote: TribunalVote = {
            "agent":     agent_name,
            "vote":      derived_vote,
            "reasoning": reasoning,
        }

    except (json.JSONDecodeError, KeyError, ValueError) as fehler:
        logger.warning(f"Tribunal [{agent_name}]: Parsing fehlgeschlagen ({fehler}), Fallback 'ok'")
        score = 0.0
        direktiven_score = 0.0
        vote: TribunalVote = {
            "agent":     agent_name,
            "vote":      "ok",
            "reasoning": f"Parsing-Fehler: {fehler}",
        }

    if agent_name == "jurist":
        logger.info(
            f"Tribunal [jurist]: score={score:.2f}, dir={direktiven_score:.2f} → "
            f"vote={vote['vote']}"
        )
    else:
        logger.info(f"Tribunal [{agent_name}]: score={score:.2f} → vote={vote['vote']}")

    return vote


# ─────────────────────────────────────────────
# Tribunal-Durchlauf (alle Agenten sequenziell)
# ─────────────────────────────────────────────
def judge(state: ConversationState) -> ConversationState:
    """Fuehrt alle Tribunal-Agenten sequenziell aus und sammelt Voten."""
    logger.info(f"Tribunal: Starte Bewertung (Runde {state['correction_round']}, "
                f"{len(AGENTS)} Agenten)")

    votes: list[TribunalVote] = []

    for agent_def in AGENTS:
        vote: TribunalVote = _agent_vote(
            agent_name    = agent_def["name"],
            system_prompt = agent_def["system_prompt"],
            state         = state,
        )
        votes.append(vote)

    state["tribunal_votes"] = votes

    return state


# ─────────────────────────────────────────────
# Die Speicherpruefung in der Auswertung
# ─────────────────────────────────────────────
def _storage_claim_step(
    state: ConversationState,
    critical_feedback: list[str],
) -> ClaimCheck:
    """Haelt die Speicherbehauptungen der Antwort gegen die Dienste des Turns.

    Behauptet die Antwort, etwas sei notiert, eingetragen oder geaendert, muss
    in diesem Turn ein Dienst `abgeschlossen` gemeldet haben. Gemessen am
    14.09.2026: vier Termin-Turns ohne Zustellung, und alle vier Antworten
    sagten *„notiert"* oder *„fest verankert"*. Wie die Datumspruefung ist das
    in Python entscheidbar und kein vierter Modellaufruf.

    Vorbedingung: `state["tribunal_verdict"]` ist gesetzt; `critical_feedback`
    ist die Liste, aus der die Zusammenfassung entsteht.
    Nachbedingung: Bei einer nicht belegten Behauptung steht das Urteil auf
    mindestens `warnung` — ein `ablehnen` bleibt — und der Korrekturauftrag an
    erster Stelle von `critical_feedback`, weil der Corrector ausschliesslich
    die Zusammenfassung liest. In jedem Fall ist genau ein dauerhafter Eintrag
    geschrieben.
    Fehlerfaelle: keine eigenen; eine defekte Eingabe meldet `uncovered_claims`.
    """
    # ── Verarbeitung ────────────────────────────
    check: ClaimCheck = uncovered_claims(
        state.get("response") or "", state.get("agent_results")
    )
    if check.uncovered:
        if state["tribunal_verdict"] == "ok":
            state["tribunal_verdict"] = "warnung"
        critical_feedback.insert(0, correction_order(check.claims))
        logger.error(
            "Tribunal: %d Speicherbehauptung(en) ohne abgeschlossenen Dienst "
            "(Ausgaenge: %s) — Urteil auf '%s' gehoben. %s",
            len(check.claims), ", ".join(check.outcomes) or "keine",
            state["tribunal_verdict"],
            "; ".join(c.line() for c in check.claims),
        )

    # ── Ausgabe-Verifikation ────────────────────
    # Die Korrekturrunden sind begrenzt. Ist die letzte verbraucht, geht eine
    # `warnung` mit der Antwort hinaus (`_after_evaluate`, mit denselben
    # Vorgaben gelesen) — und mit ihr die Behauptung. Das darf nicht still
    # geschehen.
    runde: int = state.get("correction_round", 0)
    if (check.uncovered and state["tribunal_verdict"] == "warnung"
            and runde >= state.get("max_corrections", 0)):
        logger.error(
            "Tribunal: Speicherbehauptung nach %s Korrekturrunde(n) nicht "
            "beseitigt — die Antwort geht mit ihr hinaus, mit Korrektursatz: %s",
            runde, "; ".join(c.line() for c in check.claims),
        )
        # Scheibe 12 A, Punkt 1: angehaengt statt entfernt (16.09.2026).
        antwort_setzen(state, append_correction(state.get("response") or ""), "tribunal_korrektursatz")
    _storage_check_record(state, check)
    return check


def _summary_verify(
    state: ConversationState,
    time_findings: int,
    storage_uncovered: bool,
) -> None:
    """Prueft, ob jeder Befund der Auswertung die Zusammenfassung erreicht hat.

    Ein Befund ohne Eintrag in der Zusammenfassung erreicht die Korrekturrunde
    nicht — der Corrector liest ausschliesslich sie.

    Vorbedingung: `state["tribunal_summary"]` ist gesetzt.
    Nachbedingung: Fehlt ein Korrekturauftrag, steht eine Fehlerzeile im Log.
    """
    # ── Ausgabe-Verifikation ────────────────────
    summary: str = state.get("tribunal_summary") or ""
    if time_findings and "ZEITANGABE FALSCH" not in summary:
        logger.error(
            "Tribunal: %d Zeitbefund(e) gefunden, aber der Korrekturauftrag "
            "steht nicht in der Zusammenfassung — die Korrekturrunde bekommt "
            "ihn nicht", time_findings,
        )
    if storage_uncovered and ORDER_HEADER not in summary:
        logger.error(
            "Tribunal: Speicherbehauptung gefunden, aber der Korrekturauftrag "
            "steht nicht in der Zusammenfassung — die Korrekturrunde bekommt "
            "ihn nicht",
        )


# ─────────────────────────────────────────────
# Dauerhafter Eintrag der Speicherpruefung
# ─────────────────────────────────────────────
def _storage_check_record(state: ConversationState, check: ClaimCheck) -> None:
    """Schreibt den Ausgang der Speicherpruefung in die dauerhafte Ablage.

    **Jeder Durchlauf schreibt, auch der ohne Behauptung.** Die Pruefung ist
    eine Weiche, die die Ausgabe aendert; ohne Eintrag im stillen Fall ist
    *„nicht gerechnet"* von *„gerechnet, nichts gefunden"* nicht zu trennen,
    und die Frage, wie oft sie im Betrieb anschlaegt und ob die Korrektur
    greift, waere nur aus dem rotierenden Log zu beantworten.

    Der Eintrag traegt Form und Wort der Befunde, nicht den Satz: Der Wortlaut
    der Antwort steht im Rohturn, und die Ablage soll durch ihre Zahlen
    nachvollziehbar sein, nicht durch Gespraechsinhalt.

    Vorbedingung: `check` ist das Ergebnis dieses Durchlaufs.
    Nachbedingung: genau ein Eintrag der Art `berechnung`, Knoten `evaluate`,
    Quelle `speicherbehauptung`.
    Fehlerfaelle: Ein gescheiterter Eintrag darf den Turn nicht reissen — er
    wird mit Spur gemeldet.
    """
    # ── Eingabe-Validierung ─────────────────────
    turn_id: str = state.get("turn_id") or ""
    if not turn_id:
        logger.error(
            "Tribunal: Speicherpruefung ohne turn_id im Zustand — der Eintrag "
            "ist keinem Turn zuzuordnen und wird trotzdem geschrieben",
        )

    # ── Verarbeitung ────────────────────────────
    inhalt: dict = {
        "ergebnis":         check.result,
        "urteil_gehoben":   check.uncovered,
        "runde":            state.get("correction_round", 0),
        "grenze":           state.get("max_corrections", 0),
        "befunde":          [{"form": c.form, "wort": c.word} for c in check.claims],
        "abgeschlossen":    list(check.completed),
        "ausgaenge":        list(check.outcomes),
        "regelfassung":     RULE_VERSION,
    }

    # ── Ausgabe-Verifikation ────────────────────
    try:
        log_berechnung(
            turn_id      = turn_id,
            node         = "evaluate",
            quelle       = "speicherbehauptung",
            inhalt       = inhalt,
            user_id      = state.get("user_id"),
            character_id = state.get("character_id"),
        )
    except Exception:
        # Breit gefangen mit Absicht: Der Turn ist wichtiger als sein
        # Protokoll, und was den Schreibvorgang reissen kann, ist von hier aus
        # nicht aufzaehlbar. Gemeldet wird mit Spur.
        logger.exception(
            "Tribunal: Speicherpruefung nicht dauerhaft protokolliert "
            "(turn_id=%s, ergebnis=%s)", turn_id, check.result,
        )


# ─────────────────────────────────────────────
# Tribunal-Auswertung (Mehrheitsentscheid)
# ─────────────────────────────────────────────
def evaluate(state: ConversationState) -> ConversationState:
    """Wertet die Voten aus und bildet das Gesamturteil."""
    votes: list[TribunalVote] = state["tribunal_votes"]

    rejections: list[TribunalVote] = [v for v in votes if v["vote"] == "ablehnen"]
    warnings:   list[TribunalVote] = [v for v in votes if v["vote"] == "warnung"]

    # Mehrheitsentscheid
    if len(rejections) >= 2:
        state["tribunal_verdict"] = "ablehnen"
    elif len(warnings) + len(rejections) >= 2:
        state["tribunal_verdict"] = "warnung"
    else:
        state["tribunal_verdict"] = "ok"

    # Zusammenfassung fuer den Corrector
    critical_feedback: list[str] = [
        f"[{v['agent']}] {v['reasoning']}"
        for v in votes
        if v["vote"] in ("ablehnen", "warnung")
    ]
    # Die Zeitangabe wird gerechnet, nicht beurteilt.
    #
    # Die drei Voten sind Modellurteile ueber Haltung und Inhalt. Ein
    # Wochentag, der nicht zu seinem Datum passt, ist dagegen ein
    # Rechenfehler und in Python entscheidbar — er gehoert nicht in einen
    # vierten Modellaufruf.
    #
    # Der Befund hebt das Urteil auf mindestens `warnung`, weil genau das
    # die Korrekturrunde ausloest. Er kann ein `ablehnen` nicht abschwaechen:
    # Ein falsches Datum ist ein Grund mehr zur Korrektur, nie einer weniger.
    zeit_befunde = widersprueche_finden(
        state.get("response") or "", datetime.now().date()
    )
    if zeit_befunde:
        if state["tribunal_verdict"] == "ok":
            state["tribunal_verdict"] = "warnung"
        critical_feedback.insert(0, korrekturauftrag(zeit_befunde))
        logger.error(
            "Tribunal: %d Zeitangabe(n) widersprechen sich — Urteil auf '%s' "
            "gehoben. %s",
            len(zeit_befunde), state["tribunal_verdict"],
            "; ".join(w.satz() for w in zeit_befunde),
        )

    # Die zweite Haelfte desselben Defekts: ein erfundenes Datum **ohne**
    # Wochentag. Die Pruefung oben braucht das Paar und findet dann nichts —
    # gemessen am 22.08.2026 am Originalfall: mit Wochentag 1 Befund, ohne 0.
    #
    # Hier ist der Bezug nicht der Text selbst, sondern das, was die Dienste
    # dieses Turns gemeldet haben. Nur erfolgreiche Ergebnisse zaehlen: Was ein
    # Dienst abgelehnt hat, wurde nicht eingetragen und kann nichts belegen.
    quellen: list[str] = [
        str(r.ergebnis) for r in (state.get("agent_results") or [])
        if getattr(r, "status", "") == "abgeschlossen"
        and getattr(r, "ergebnis", None) is not None
    ]
    datum_abweichungen = bestaetigung_pruefen(
        state.get("response") or "", quellen, datetime.now().date()
    )
    if datum_abweichungen:
        if state["tribunal_verdict"] == "ok":
            state["tribunal_verdict"] = "warnung"
        critical_feedback.insert(0, bestaetigungsauftrag(datum_abweichungen))
        logger.error(
            "Tribunal: %d Datumsangabe(n) der Antwort sind durch keinen Dienst "
            "belegt — Urteil auf '%s' gehoben. %s",
            len(datum_abweichungen), state["tribunal_verdict"],
            "; ".join(a.satz() for a in datum_abweichungen),
        )

    # Die Speicherbehauptung — gesagt ist nicht gespeichert (siehe
    # `_storage_claim_step`). Sie laeuft als letzte Pruefung, weil sie am Ende
    # meldet, ob eine Behauptung mit der letzten Runde hinausgeht — dazu muss
    # das Urteil feststehen.
    speicher: ClaimCheck = _storage_claim_step(state, critical_feedback)

    state["tribunal_summary"] = "\n".join(critical_feedback) if critical_feedback else ""

    # ── Ausgabe-Verifikation ────────────────────────────────────────
    _summary_verify(
        state, len(zeit_befunde) + len(datum_abweichungen), speicher.uncovered
    )

    logger.info(f"Tribunal-Auswertung: verdict={state['tribunal_verdict']} "
                f"(ablehnungen={len(rejections)}, warnungen={len(warnings)}, "
                f"zeitbefunde={len(zeit_befunde)}, "
                f"datumsabweichungen={len(datum_abweichungen)}, "
                f"speicherbehauptungen={len(speicher.claims)}/{speicher.result})")

    for vote in votes:
        logger.info(f"  [{vote['agent']}] {vote['vote']}: {vote['reasoning'][:80]}")

    return state
