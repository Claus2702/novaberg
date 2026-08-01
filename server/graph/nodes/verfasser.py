"""
Verfasser Node — bestimmt den fachlichen Inhalt der Antwort.

Sitzt zwischen GV-Node und Responder. Er sieht das Wissen — Gedaechtnis,
Web-Recherche, Aufgabe, Gespraechsvektor — und entscheidet, WAS gesagt wird.
Der Responder bekommt das Ergebnis fertig und gibt ihm Novas Form.

**Warum die Trennung.** Der Responder entschied bisher in einem Zug ueber
Substanz und Klang. Der Preis steht als Kommentar in `responder.py`: Der
Sprachstil-Block musste ans Ende der Nutzer-Nachricht wandern, "dort, wo eine
Anweisung gegen 8.400 Tokens fremder Prosa noch etwas ausrichtet". Eine
Stilanweisung, die sich ihren Platz erkaempfen muss, steht nicht dort, wo sie
hingehoert, sondern dort, wo sie ueberlebt.

**Was der Responder dadurch verliert, ist der tragende Teil:** Gedaechtnis und
Web-Recherche sieht er nicht mehr. Er kann dann nichts aus einem Wissen
erfinden, das ihm gar nicht vorliegt.

**Die Bloecke werden verschoben, nicht umformuliert.** `[GEDAECHTNIS]`,
`[WEB-RECHERCHE]` und die `[AUFGABE]`-Varianten sind dieselben Prompt-
Bausteine, die der Responder benutzt hat. Eine Umformulierung im selben Zug
haette den Schnitt mit einer Prompt-Ueberarbeitung vermischt: Bei einer
Verschlechterung waere nicht mehr trennbar, welche der beiden es war.

Konzept: novaberg-node-verfasser_k.md
"""

import logging
from datetime import datetime

from config import PROMPTS, get_node_config
from services.model_services import ChatRequest, model_service

from graph.state import ConversationState

logger = logging.getLogger("ki_server.verfasser")


def _gespraechsvektor_block(state: ConversationState) -> str:
    """Baut den [GESPRAECHSVEKTOR]-Block aus dem Ergebnis des GV-Node.

    Traegt Landschaft, Strategie, Absicht, Vehikel und den Leitgedanken —
    alle vier gehoeren zum Inhalt. Auch das Vehikel: Ob geantwortet,
    zurueckgefragt oder geschwiegen wird, ist eine Entscheidung ueber die
    Substanz und laesst sich nicht stilistisch nachformen
    (novaberg-node-verfasser_k.md §2.1).

    Der Zusatz "Finde deine eigenen Worte" des alten Responder-Blocks
    entfaellt: Das ist ab jetzt die Aufgabe der zweiten Stufe und keine Bitte
    mehr (§2.4).

    Vorbedingung: `state` stammt aus dem CharacterGraph.
    Nachbedingung: Leerer String genau dann, wenn der GV-Node nichts geliefert
    hat.
    Fehlerfaelle: keine — ein fehlender Gespraechsvektor ist kein Defekt,
    sondern der Zustand vor dem ersten Turn.

    Returns:
        Der Block oder ein leerer String.
    """
    # ── Eingabe-Validierung ─────────────────────
    hypothese: str = state.get("gespraechsvektor", "")
    if not hypothese:
        return ""

    # ── Verarbeitung ────────────────────────────
    detail:    dict = state.get("gv_detail", {})
    cluster:   str  = detail.get("cluster", "")
    strategie: str  = detail.get("strategie", "")
    vehikel:   str  = detail.get("vehikel", "")
    impuls:    str  = detail.get("impuls", "")

    rahmen: str = ""
    if cluster:
        from ei.dreischicht import (
            CLUSTER_BESCHREIBUNGEN,
            CLUSTER_FRAGEN,
            STRATEGIE_NAMEN,
        )
        rahmen = (
            f"Gespraechslandschaft: {cluster.capitalize()} — "
            f"{CLUSTER_BESCHREIBUNGEN.get(cluster, '')}\n"
            f"Fragen: {CLUSTER_FRAGEN.get(cluster, '')}\n"
        )
        if strategie:
            rahmen += f"Die gewaehlte Strategie: {STRATEGIE_NAMEN.get(strategie, strategie)}"
            if vehikel:
                rahmen += f" als {vehikel.capitalize()}"
            rahmen += ".\n"

    leitgedanke: str = f"\nLeitgedanke fuer diese Antwort: {impuls}\n" if impuls else ""

    # ── Ausgabe ─────────────────────────────────
    return (
        f"[GESPRAECHSVEKTOR]\n"
        f"{rahmen}"
        f"So bewegt sich das Gespraech gerade.\n\n"
        f"{hypothese}"
        f"{leitgedanke}"
    )


def _build_system_prompt(state: ConversationState) -> str:
    """Baut den System-Prompt des Verfassers: Auftrag plus Wissen.

    Enthaelt ausdruecklich KEINE Identitaet, keine Emotion, keinen Sprachstil
    und keine Direktiven — die gehoeren zur Form und damit zum Responder.

    Vorbedingung: `state` traegt `memory_context` und `web_context` (moeglich
    leer).
    Nachbedingung: Der Auftragsblock steht immer, die Wissensbloecke nur, wenn
    sie Inhalt haben.
    Fehlerfaelle: keine.

    Returns:
        Der System-Prompt.
    """
    # ── Verarbeitung ────────────────────────────
    jetzt = datetime.now()

    # Die drei Saetze stammen woertlich aus dem [IDENTITAET]-Block des
    # Responders. Sie sprechen ueber Gedaechtnis, Kontext und Web-Zugriff —
    # also ueber das Wissen, das seit der Trennung hier liegt. Verschoben,
    # nicht umformuliert: Eine Ueberarbeitung im selben Zug haette den Schnitt
    # mit einer Prompt-Aenderung vermischt.
    teile: list[str] = [
        PROMPTS["verfasser.auftrag"],
        f"Heute ist {jetzt.strftime('%A, %d.%m.%Y')}, es ist {jetzt.strftime('%H:%M')} Uhr.\n"
        "Der Charakter-Kontext im Gedaechtnis beschreibt den NUTZER — verwechsle\n"
        "seine Eigenschaften nicht mit deinen.\n"
        "Erwaehne nur Informationen die im Kontext stehen. Erfinde keine Details.\n"
        "Du hast Zugriff auf aktuelle Informationen aus dem Internet ueber eine lokale\n"
        "Suchmaschine. Sage niemals du haettest keinen Internetzugang.",
    ]

    # Der fertige [AUFGABE]-Block des Planners — unveraendert uebernommen.
    # Die Interpretation gehoert zum Produzenten; der Verfasser setzt ihn ein
    # wie der Responder es tat.
    task_block: str = state.get("task_block", "")
    if task_block:
        teile.append(task_block)

    gv_block: str = _gespraechsvektor_block(state)
    if gv_block:
        teile.append(gv_block)

    if state.get("memory_context"):
        teile.append(
            PROMPTS["responder.gedaechtnis"].format(
                memory_context=state["memory_context"]
            )
        )

    if state.get("web_context"):
        teile.append(
            PROMPTS["responder.web"].format(web_context=state["web_context"])
        )

    # ── Ausgabe ─────────────────────────────────
    return "\n\n".join(teile)


def verfassen(state: ConversationState) -> ConversationState:
    """Bestimmt den fachlichen Inhalt der Antwort und legt ihn in den State.

    Vorbedingung: `user_prompt` ist gesetzt. Der Aufrufer stellt sicher, dass
    dieser Node bei `task_context_cut=True` gar nicht erst laeuft — dort ist
    das Wenig-Kontext-Verhalten Absicht (novaberg-node-verfasser_k.md §5.1).
    Nachbedingung: `antwort_inhalt` traegt einen nicht-leeren Text.
    Fehlerfaelle: Leerer Prompt oder leere Modellantwort — beides laut
    gemeldet, `antwort_inhalt` bleibt leer. **Kein Ersatztext und kein
    Rueckfall auf die alte Responder-Bauart:** Ein Ausfall darf nicht wie eine
    Antwort aussehen (§5.3).

    Returns:
        Der State mit gesetztem `antwort_inhalt`.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_prompt: str = state.get("user_prompt", "")
    if not user_prompt.strip():
        logger.error(
            "Verfasser: leerer user_prompt — es gibt nichts zu beantworten, "
            "antwort_inhalt bleibt leer"
        )
        state["antwort_inhalt"] = ""
        return state

    # ── Verarbeitung ────────────────────────────
    system_prompt: str = _build_system_prompt(state)

    # Der Verlauf gibt dem Inhalt seinen Bezug: Ohne ihn beantwortet der
    # Verfasser jede Rueckfrage als staende sie allein.
    messages: list[dict] = []
    for turn in state.get("session_turns", []):
        rolle: str = "user" if turn.get("rolle") == "user" else "assistant"
        inhalt: str = turn.get("inhalt", "")
        if inhalt:
            messages.append({"role": rolle, "content": inhalt})

    if not messages or messages[-1].get("content") != user_prompt:
        messages.append({"role": "user", "content": user_prompt})

    # Log: Inhalt direkt ausgeben, ohne JSON-Wrapping — dieselbe Form wie beim
    # Responder, damit sich beide Stufen im Log gegenueberstellen lassen.
    messages_text: str = "\n\n".join(
        f"═══ {m['role'].upper()} ═══\n{m['content']}" for m in messages
    )

    logger.info(
        "=== VERFASSER LLM-INPUT ===\n"
        "═══ SYSTEM-PROMPT ═══\n%s\n\n"
        "%s\n"
        "=== ENDE VERFASSER LLM-INPUT ===",
        system_prompt,
        messages_text,
    )

    node_cfg = get_node_config("verfasser")

    antwort = model_service.chat.submit_sync(ChatRequest(
        messages          = messages,
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.4),
        top_p             = node_cfg.get("top_p"),
        repeat_penalty    = node_cfg.get("repeat_penalty"),
        presence_penalty  = node_cfg.get("presence_penalty"),
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "verfasser",
    ))

    # ── Ausgabe-Verifikation ────────────────────
    inhalt: str = (antwort.text or "").strip()
    if not inhalt:
        logger.error(
            "Verfasser: Modell lieferte keinen Inhalt (Tokens: %s) — "
            "antwort_inhalt bleibt leer, der Responder hat nichts zu formen",
            antwort.token_total,
        )
        state["antwort_inhalt"] = ""
        return state

    state["antwort_inhalt"] = inhalt

    # Die Kosten dieser Stufe gehoeren in die Anzeige. `token_total` scheidet
    # aus — das Feld gehoert dem Responder und wuerde ueberschrieben. Der
    # bestehende Anmerkungs-Kanal traegt es, ohne dass ein weiterer noetig ist.
    anmerkungen: list = state.get("node_annotations") or []
    anmerkungen.append(f"[Verfasser] {antwort.token_total} Tokens")
    state["node_annotations"] = anmerkungen

    logger.info(
        "Verfasser: Inhalt bestimmt (%s Zeichen, %s Tokens, "
        "Wissen: Gedaechtnis=%s Web=%s)",
        len(inhalt), antwort.token_total,
        bool(state.get("memory_context")), bool(state.get("web_context")),
    )
    return state
