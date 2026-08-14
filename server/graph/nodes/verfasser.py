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
from memory.pipeline_log import log_berechnung
from services.model_services import ChatRequest, model_service

from graph.einwand import kopf_anweisung, urteil_lesen
# Die Marke gehoert zum Vertrag von `gv_detail` und hat genau eine Quelle.
# Sie hier als Literal zu wiederholen waere der zweite Ort fuer denselben
# Wert — und der Fall, in dem sie gebraucht wird, ist
# genau der, in dem niemand hinsieht.
from graph.nodes.gespraechsvektor import VORAUSDENKEN_GELAUFEN
from graph.reiz  import reiz_ist_eigener_gedanke, reiz_text
from graph.state import ConversationState
from graph.vorzeichen import Vorzeichenbefund, vorzeichen_pruefen

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

    **Der Block haengt an der Landschaft, nicht an der Hypothese.** Bis zum
    14.08.2026 kehrte er bei leerem `gespraechsvektor` sofort leer zurueck —
    und nahm die Landschaft mit, obwohl sie in `gv_detail` steht. Der GV-Node
    war am 08.08.2026 ausdruecklich so umgebaut worden, dass sie **jeden**
    Turn traegt; diese Zeile hob das fuer den Verfasser wieder auf. Gemessen
    am 13.08.2026: In **15 von 26** Verfasser-Laeufen stand gar kein Block,
    waehrend der Auftrag viermal auf ihn verwies. Der Responder macht es
    richtig und liest `gv_detail` unmittelbar.

    **Der Ausfall des Vorausdenkens wird benannt, nicht verschwiegen.** Eine
    fehlende Strategie ist eine Vorgabe — naemlich die des Vorgabewerts, den
    das Modell aus der Dichte seines Materials waehlt. Welcher der beiden
    Faelle vorliegt, sagt `vorausdenken`: Der leere Strategie-String allein
    trueg den Unterschied nicht, weil `korridor_pruefen` ihn auch auf einem
    gelaufenen Turn leert.

    Vorbedingung: `state` stammt aus dem CharacterGraph.
    Nachbedingung: Leerer String genau dann, wenn keine Landschaft vermessen
    wurde — das ist der Zustand vor dem ersten Turn und der einzige Fall, in
    dem der Auftrag ins Leere zeigt.
    Fehlerfaelle: keine — ein fehlendes Vorausdenken ist kein Defekt, sondern
    eine Entscheidung des GV-Node, und der Block sagt sie an.

    Returns:
        Der Block oder ein leerer String.
    """
    # ── Eingabe-Validierung ─────────────────────
    detail:  dict = state.get("gv_detail") or {}
    cluster: str  = detail.get("cluster", "")
    if not cluster:
        return ""

    # ── Verarbeitung ────────────────────────────
    from ei.dreischicht import (
        CLUSTER_BESCHREIBUNGEN,
        CLUSTER_FRAGEN,
        STRATEGIE_NAMEN,
    )

    strategie: str = detail.get("strategie", "")
    vehikel:   str = detail.get("vehikel", "")
    impuls:    str = detail.get("impuls", "")
    hypothese: str = state.get("gespraechsvektor", "")

    zeilen: list[str] = [
        f"Gespraechslandschaft: {cluster.capitalize()} — "
        f"{CLUSTER_BESCHREIBUNGEN.get(cluster, '')}",
        f"Fragen: {CLUSTER_FRAGEN.get(cluster, '')}",
    ]

    if strategie:
        satz: str = (
            f"Die gewaehlte Strategie: "
            f"{STRATEGIE_NAMEN.get(strategie, strategie)}"
        )
        if vehikel:
            satz += f" als {vehikel.capitalize()}"
        zeilen.append(satz + ".")

    if hypothese:
        zeilen.append("")
        zeilen.append("So bewegt sich das Gespraech gerade.")
        zeilen.append("")
        zeilen.append(hypothese)

    if impuls:
        zeilen.append("")
        zeilen.append(f"Leitgedanke fuer diese Antwort: {impuls}")

    # Die Ansage des Ausfalls. Sie steht zuletzt, damit sie nicht zwischen
    # Landschaft und Hypothese gelesen wird, als gehoerte sie zur Lage.
    if detail.get("vorausdenken", "") != VORAUSDENKEN_GELAUFEN:
        zeilen.append("")
        zeilen.append(
            "Fuer diesen Turn wurde nicht vorausgedacht: Es gibt weder eine "
            "gewaehlte Strategie noch einen Leitgedanken. Die Landschaft "
            "oben ist die ganze Vorgabe."
        )
    elif not strategie:
        zeilen.append("")
        zeilen.append(
            "Fuer diesen Turn steht kein Mittel fest. Die Landschaft oben "
            "ist die Vorgabe."
        )

    # ── Ausgabe ─────────────────────────────────
    return "[GESPRAECHSVEKTOR]\n" + "\n".join(zeilen)


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
        # Der Kopfblock wird im Code gebaut, nicht im Prompttext ausgeschrieben:
        # Die gueltigen Bewertungen und Quellen stehen in `graph/einwand.py` und
        # duerfen nirgends ein zweites Mal stehen (13_DATENSTRUKTUREN §3).
        kopf_anweisung(),
        # **Die Herkunft des Reizes entscheidet ueber die Perspektive.**
        # Ein Pixie-Impuls reist auf dem Platz der Nutzereingabe; wer ihn ohne
        # diese Frage liest, schreibt Novas eigenen Gedanken ihrem Gegenueber
        # zu. Gemessen am 13.08.2026: **13 von 14 Impulsen** eines Tages
        # begannen mit "Du hast ...", fuenf davon wortgleich — obwohl der
        # Responder seinen Schutzblock gesetzt hatte. Die Zuschreibung stand
        # schon im Material, das hier entsteht
        # (`novaberg-bugs.md` -> VERFASSER-KENNT-DIE-QUELLE-NICHT).
        PROMPTS["verfasser.eigener_impuls"] if reiz_ist_eigener_gedanke(state)
        else PROMPTS["verfasser.fremder_reiz"],
        # Die Anreden folgen der Konstellation des Auftrags: "du" ist der
        # Verfasser, ueber Person A wird in dritter Person gesprochen, und der
        # Mensch heisst Person B. Vorher stand hier "den NUTZER" und "mit
        # deinen" — ein zweites Namenssystem im selben Prompt. Genau daran ist
        # der Responder am 13.08.2026 gemessen worden: In sieben von dreizehn
        # Bloecken wurde geduzt, und "du" meinte drei verschiedene Personen.
        f"Heute ist {jetzt.strftime('%A, %d.%m.%Y')}, es ist {jetzt.strftime('%H:%M')} Uhr.\n"
        "Der Charakter-Kontext im Gedaechtnis beschreibt PERSON B — verwechsle\n"
        "seine Eigenschaften nicht mit denen von Person A.\n"
        "Erwaehne nur Informationen die im Kontext stehen. Erfinde keine Details.\n"
        "Person A hat Zugriff auf aktuelle Informationen aus dem Internet ueber eine\n"
        "lokale Suchmaschine. Der Inhalt sagt nie, sie habe keinen Internetzugang.",
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

    # ── Der Gedanke als Material, nicht als Rede ──
    # Er steht **hier**, neben Gedaechtnis und Recherche, und ausdruecklich
    # nicht als Nachricht in der Rolle des Gegenuebers. Was auf jenem Platz
    # steht, wird von einem Sprachmodell beantwortet, eingeordnet und jemandem
    # zugeschrieben — vier Anlaeufe im Prompttext haben dagegen angeschrieben
    # und verloren. Gemessen am 14.08.2026, 19:15 UTC, mit bereits leerem
    # Reiz-Platz: "PERSON B stellt die physikalische Beobachtung ... in den
    # Raum", obwohl Person B nichts gesagt hatte. Eine Rollenzuweisung ist
    # keine Anweisung, sie ist eine Struktur.
    if reiz_ist_eigener_gedanke(state):
        teile.append(
            PROMPTS["verfasser.eigener_gedanke"].format(gedanke=reiz_text(state))
        )

    # ── Ausgabe ─────────────────────────────────
    return "\n\n".join(teile)


def verfassen(state: ConversationState) -> ConversationState:
    """Bestimmt den fachlichen Inhalt der Antwort und legt ihn in den State.

    Vorbedingung: Der Reiz dieses Durchlaufs ist gesetzt — die Nutzer-
    Aeusserung auf einem Nutzer-Turn, Novas Gedanke auf einem Impuls-Turn.
    **Nicht `user_prompt`:** Auf einem Impuls-Turn hat niemand gesprochen, und
    dieses Feld ist dort leer. Der Aufrufer stellt sicher, dass
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
    # Der Reiz, nicht der Reiz-Platz: Auf einem Impuls-Turn steht die Vorlage
    # in `eigener_gedanke`, und ein leerer `user_prompt` ist dort kein Ausfall,
    # sondern die Auskunft, dass niemand gesprochen hat.
    reiz: str = reiz_text(state)
    if not reiz.strip():
        # Die Meldung nennt die Herkunft: Ohne sie ist ein Nutzer-Turn ohne
        # Eingabe von einem Impuls ohne Gedanken nicht zu unterscheiden — zwei
        # Defekte an zwei verschiedenen Stellen, mit derselben Zeile.
        logger.error(
            "Verfasser: leerer Reiz (herkunft=%s) — es gibt nichts zu "
            "beantworten, antwort_inhalt bleibt leer",
            "eigener_impuls" if reiz_ist_eigener_gedanke(state) else "nutzer_turn",
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

    # **Auf einem Impuls-Turn bleibt der Platz des Gegenuebers leer.** Der
    # Gedanke steht als Block im System-Prompt; hier steht nur der Auftrag,
    # denn die Nachrichtenfolge darf nicht leer sein und ein Auftrag ist keine
    # fremde Rede. Der Zeuge dafuer prueft die Nachrichtenfolge, nicht den
    # Prompttext — eine Gegenprobe im Text war viermal gruen, waehrend das
    # Verhalten blieb.
    if reiz_ist_eigener_gedanke(state):
        messages.append({
            "role": "user", "content": PROMPTS["verfasser.auftrag_ohne_reiz"],
        })
    elif not messages or messages[-1].get("content") != reiz:
        messages.append({"role": "user", "content": reiz})

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
    roh: str = (antwort.text or "").strip()
    if not roh:
        logger.error(
            "Verfasser: Modell lieferte keinen Inhalt (Tokens: %s) — "
            "antwort_inhalt bleibt leer, der Responder hat nichts zu formen",
            antwort.token_total,
        )
        state["antwort_inhalt"] = ""
        return state

    # Kopfblock vom Inhalt trennen (B1). Misslingt der Kopf, bleibt die Prosa
    # erhalten — ein ausgefallenes Urteil darf den Turn nicht kosten.
    urteil, inhalt = urteil_lesen(roh)
    state["einwandsurteil"] = urteil

    if not inhalt:
        logger.error(
            "Verfasser: nach dem Kopfblock blieb kein Inhalt (%s Zeichen roh) — "
            "antwort_inhalt bleibt leer",
            len(roh),
        )
        state["antwort_inhalt"] = ""
        return state

    if not urteil.geliefert:
        # Laut, nicht still: Ohne diese Zeile ist ein ausgefallener Kopfblock
        # in der Fallenbatterie von einem Turn ohne Einwand nicht zu
        # unterscheiden, und die Rate zaehlte Ausfaelle als Erfolge.
        logger.error(
            "Verfasser: kein lesbares Urteil im Kopfblock — die Ausbausperre "
            "greift in diesem Turn nicht. Erste 120 Zeichen der Rohantwort: %r",
            roh[:120],
        )

    state["antwort_inhalt"] = inhalt

    # ── B4 Stufe 1: die Vorzeichenpruefung ──────
    # Zaehlt, ohne zu aendern. Sie steht hier, weil hier zum ersten und
    # einzigen Mal drei Dinge zusammen vorliegen: das Urteil, die
    # den Reiz dieses Turns und Novas Text. Nachgelagert waere sie nicht
    # baubar — das Urteil wird nirgends persistiert.
    #
    # Der Eintrag entsteht NUR bei 'abweichend'. Das ist die Gegenprobe des
    # Bauteils: Ein Turn ohne Einwand hinterlaesst keine Spur, sonst waere
    # die Rate nicht lesbar.
    befund: Vorzeichenbefund = vorzeichen_pruefen(urteil, reiz, inhalt)
    if befund.geprueft:
        log_berechnung(
            turn_id      = state.get("turn_id", ""),
            node         = "verfasser",
            quelle       = "vorzeichenpruefung",
            inhalt       = {
                "werte":            befund.werte,
                "uebernommen":      befund.uebernommen,
                "kandidat":         befund.kandidat,
                # Getrennt gefuehrt, weil "kein Wert gefunden" etwas anderes
                # ist als "kein Wert uebernommen" — sonst zaehlte eine
                # ausgeschriebene Zahl wie ein Erfolg.
                "werte_gefunden":   len(befund.werte),
                "staerke":          urteil.staerke,
                "quelle_des_urteils": urteil.quelle,
            },
            user_id      = state.get("user_id", ""),
            character_id = state.get("character_id", ""),
        )

    # Die Kosten dieser Stufe gehoeren in die Anzeige. `token_total` scheidet
    # aus — das Feld gehoert dem Responder und wuerde ueberschrieben. Der
    # bestehende Anmerkungs-Kanal traegt es, ohne dass ein weiterer noetig ist.
    anmerkungen: list = state.get("node_annotations") or []
    anmerkungen.append(f"[Verfasser] {antwort.token_total} Tokens")
    state["node_annotations"] = anmerkungen

    # Das Urteil gehoert ins Protokoll, nicht nur in den State: Ohne diese
    # Zeile ist im Nachhinein nicht feststellbar, ob der Verfasser geurteilt
    # hat — und die Anlaufquote von B1 waere so wenig messbar wie die des
    # Thinkers vor B-1.
    logger.info(
        "Verfasser: Urteil %s (Einwand=%s, Bewertung=%s, Staerke=%s, Quelle=%s) — %s",
        "gefaellt" if urteil.geliefert else "AUSGEFALLEN",
        urteil.vorhanden, urteil.bewertung, urteil.staerke, urteil.quelle,
        (urteil.geprueft or "—")[:160],
    )

    logger.info(
        "Verfasser: Inhalt bestimmt (%s Zeichen, %s Tokens, "
        "Wissen: Gedaechtnis=%s Web=%s)",
        len(inhalt), antwort.token_total,
        bool(state.get("memory_context")), bool(state.get("web_context")),
    )
    return state
