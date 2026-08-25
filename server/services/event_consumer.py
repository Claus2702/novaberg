"""
Event-Consumer — Verarbeitet Events aus der Event-Queue.

Pollt die Event-Queue, startet CharacterGraph-Durchläufe,
sendet Antworten per WebSocket. Async-Loop als asyncio-Task.

Pfad 2: Enricher → EI-Calc → Router → [Planner ⇄ Agent] →
        GV-Node → Responder → Thinker → Tribunal → [Corrector] →
        Salienz → Dispatcher → END
"""

import asyncio
import json
import logging

from api.websocket import broadcast, broadcast_threadsafe
from config import shutdown_event
from services.events import (
    MAX_SELF_TRIGGERS,
    event_erzeugen,
    event_naechstes,
    event_self_trigger_erlaubt,
)
from services.prompt_eingang import turn_beenden, turn_beginnen

logger = logging.getLogger("ki_server.event_consumer")

# ─────────────────────────────────────────────
# Konstanten
# ─────────────────────────────────────────────
POLL_INTERVAL:  float = 1.0     # Sekunden zwischen Queue-Checks
DEBOUNCE_DELAY: float = 2.0     # Sekunden warten nach User-Event (Tippen abwarten)

# Node-Labels für CharacterGraph (Pfad 2) — angezeigt als Stage im Client.
CHARACTER_NODE_LABELS: dict[str, str] = {
    "db_zugriff":           "DB-Zugriff — Identitäten laden",
    "emotionale_gravitation": "Gravitation — Erinnerungen färben",
    "reducer":              "Reducer — Kontext kürzen",
    "ei_calc_persist":      "EI-Persist — Nova-Zustand sichern",
    "enricher":             "Enricher — Kontext laden",
    "ei_calc":              "EI-Calc — Emotionale Intelligenz",
    "router":               "Router — Entscheidung",
    "planner":              "Planner — Aufgabenplanung",
    "agent_dispatch":       "Agent — Ausführung",
    "gv_node":              "Gesprächsvektor — Tonalität",
    "haltungsraum":         "Haltungsraum — fünf Verhaltensgrößen",
    "verfasser":            "Verfasser — Inhalt",
    "responder":            "Responder — Antwort",
    "thinker":              "Thinker — Reflexion",
    "tribunal":             "Tribunal — Bewertung",
    "evaluate":             "Evaluate — Entscheidung",
    "corrector":            "Corrector — Korrektur",
    "perzeption_assistant": "Perzeption — Antwort-Analyse",
    "salience":             "Salienz — Bewertung",
    "dispatcher":           "Dispatcher — Speichern",
}


def _stage_detail_bauen(node_name: str, node_state: dict) -> str:
    """Baut den Detail-String für eine Pipeline-Stage.

    Extrahiert die relevanten Felder aus dem Node-State und formatiert
    sie als kompakten Text für die Anzeige im Client.

    Args:
        node_name: Name des Nodes (z.B. "router", "responder").
        node_state: State-Dict nach Ausführung des Nodes.

    Returns:
        Formatierter Detail-String, oder "—" wenn keine Details verfügbar.
    """
    external = node_state.get("external")

    if node_name == "enricher":
        hat_kontext: bool = bool(node_state.get("memory_context", ""))
        modus:       str  = (external.emotion.mode    if external else "").capitalize()
        emotion:     str  = (external.emotion.emotion if external else "").capitalize()
        intentionen: list = node_state.get("user_intentionen", [])
        detail: str = f"Kontext: {'gefunden' if hat_kontext else 'keiner'}"
        if modus or emotion:
            detail += (
                f" | Modus: {modus or '?'}, "
                f"Emotion: {emotion or '?'}, "
                f"Intention: {', '.join(i.capitalize() for i in intentionen) if intentionen else '?'}"
            )
        return detail

    if node_name == "ei_calc":
        ev:        list = node_state.get("emotions_verlauf", [])
        vektor:     str = external.emotion.emotions_vector if external else ""
        stil:       str = external.emotion.language_style  if external else ""
        modus_korr: str = external.emotion.mode            if external else ""
        has_bez:   bool = bool(external.character.relationship if external else "")

        ei_teile: list[str] = []
        if ev:
            top3: str = ", ".join(
                f"{e.get('emotion', '?')}({e.get('gewicht', 0):.2f})"
                for e in ev[:3]
            )
            ei_teile.append(f"Verlauf: {top3}")
        if vektor:
            ei_teile.append(f"Vektor: {vektor}")
        if modus_korr:
            ei_teile.append(f"Modus: {modus_korr}")
        if stil:
            ei_teile.append(f"Stil: {stil}")
        if has_bez:
            ei_teile.append("Beziehung: geladen")

        nova_ev: list = node_state.get("nova_emotions_verlauf", [])
        if nova_ev:
            nova_top:  str   = nova_ev[0].get("emotion", "?")
            nova_ar:   float = nova_ev[0].get("arousal", 0.0)
            nova_konf: bool  = node_state.get("nova_emotion_konflikt", False)
            nova_str:  str   = f"Nova: {nova_top}(a={nova_ar:.2f})"
            if nova_konf:
                nova_str += " ⚡Konflikt"
            ei_teile.append(nova_str)

        return " | ".join(ei_teile) if ei_teile else "—"

    if node_name == "router":
        return (
            f"Intent: {external.emotion.intent if external else '?'}, "
            f"Ton: {external.emotion.tone if external else '?'}, "
            f"Momentum: {node_state.get('momentum', '?')}"
        )

    if node_name == "planner":
        planner_aktiv: bool = node_state.get("planner_aktiv", False)
        agent_name:    str  = node_state.get("agent_name", "")
        if planner_aktiv and agent_name:
            return f"Agent: {agent_name}"
        elif planner_aktiv:
            return "Agent-Dispatch vorbereitet"
        return "Kein Agent nötig"

    if node_name == "agent_dispatch":
        agent_results_list: list = node_state.get("agent_results", [])
        if agent_results_list:
            agent_teile: list[str] = []
            for a_result in agent_results_list:
                a_name:   str = getattr(a_result, "agent_name", "?") if not isinstance(a_result, dict) else a_result.get("agent_name", "?")
                a_status: str = getattr(a_result, "status", "?") if not isinstance(a_result, dict) else a_result.get("status", "?")
                agent_teile.append(f"{a_name}: {a_status}")
            return " | ".join(agent_teile)
        return "Ausführung läuft"

    if node_name == "reducer":
        # Die beiden Zahlen, die den Kuerzungsschritt beurteilbar machen: Was
        # blieb uebrig, und wie lang ist das Ergebnis. Eine der beiden allein
        # sagt nichts — zehn Eintraege koennen kuerzer sein als drei.
        kontext: str = node_state.get("memory_context", "")
        if not kontext:
            return "kein Kontext"
        return f"{len(kontext)} Zeichen Kontext"

    if node_name == "emotionale_gravitation":
        # Novas dominante Emotion nach der Faerbung. Ob sie gewechselt hat,
        # steht im Log; hier zaehlt der Zustand, mit dem alles Folgende rechnet.
        innen = node_state.get("internal")
        emotion: str = getattr(getattr(innen, "emotion", None), "emotion", "")
        verlauf: list = node_state.get("nova_emotions_verlauf") or []
        if not emotion and not verlauf:
            return "nicht gefärbt"
        return f"{emotion or '?'} · {len(verlauf)} im Verlauf"

    if node_name == "ei_calc_persist":
        innen = node_state.get("internal")
        emo = getattr(innen, "emotion", None)
        if emo is None:
            return "kein Zustand"
        return f"{getattr(emo, 'emotion', '?')} · {getattr(emo, 'mode', '?')}"

    if node_name == "db_zugriff":
        innen  = node_state.get("internal")
        aussen = node_state.get("external")
        geladen: list[str] = []
        if innen is not None:
            geladen.append("Nova")
        if aussen is not None:
            geladen.append("Nutzer")
        return " + ".join(geladen) + " geladen" if geladen else "nichts geladen"

    if node_name == "verfasser":
        # Zeichen UND Tokens: Die Zeichenzahl sagt, wie viel der Responder zu
        # formen bekommt, die Tokenzahl was es gekostet hat. Dazu, ob das
        # Wissen ueberhaupt da war — ein kurzer Inhalt aus leerem Gedaechtnis
        # ist etwas anderes als ein kurzer Inhalt trotz vollem.
        inhalt: str = node_state.get("antwort_inhalt", "")
        if not inhalt:
            return "kein Inhalt"

        quellen: list[str] = []
        if node_state.get("memory_context"):
            quellen.append("Gedächtnis")
        if node_state.get("web_context"):
            quellen.append("Web")

        teile: list[str] = [f"{len(inhalt)} Zeichen"]

        for anmerkung in node_state.get("node_annotations") or []:
            if anmerkung.startswith("[Verfasser]"):
                teile.append(anmerkung.removeprefix("[Verfasser] "))
                break

        if quellen:
            teile.append(" + ".join(quellen))
        else:
            teile.append("ohne Wissen")
        return " · ".join(teile)

    if node_name == "responder":
        return f"{node_state.get('token_total', 0)} Tokens"

    if node_name == "thinker":
        needs_web:   bool = node_state.get("needs_web", False)
        annotations: list = node_state.get("node_annotations", [])
        thinker_annotations: list[str] = [
            a for a in annotations if a.startswith("[Thinker")
        ]
        thinker_teile: list[str] = []
        if needs_web:
            thinker_teile.append("Web-Suche aktiv")
        korrigiert: bool = any("[Thinker] Korrektur" in a for a in thinker_annotations)
        if korrigiert:
            issues: list[str] = [
                a.replace("[Thinker/Issue] ", "")
                for a in thinker_annotations
                if a.startswith("[Thinker/Issue]")
            ]
            thinker_teile.append(f"Korrigiert ({len(issues)} Probleme)")
        elif needs_web:
            thinker_teile.append("Fakten geprüft")
        else:
            thinker_teile.append("Kein Web nötig")
        return " | ".join(thinker_teile)

    if node_name == "evaluate":
        verdict: str = node_state.get("tribunal_verdict", "?")
        summary: str = node_state.get("tribunal_summary", "")
        detail: str = f"Verdict: {verdict}"
        if verdict != "ok" and summary:
            detail += f" — {summary[:120]}"
        return detail

    if node_name == "corrector":
        return f"Runde {node_state.get('correction_round', 0)}"

    if node_name == "gv_node":
        gv_detail: dict = node_state.get("gv_detail") or {}
        if gv_detail:
            laenge:    int   = int(gv_detail.get("laenge", 0) or 0)
            neugier:   float = float(gv_detail.get("aufnahmebereitschaft", 0.0) or 0.0)
            strategie: str   = "aktiv" if gv_detail.get("strategie_aktiv") else "—"
            luecken:   int   = len(gv_detail.get("wissensluecken") or [])
            return (
                f"Sprünge: {laenge}/3 · "
                f"Neugier: {neugier:.2f} · "
                f"Strategie: {strategie} · "
                f"Lücken: {luecken}"
            )
        hypothese: str = node_state.get("gespraechsvektor", "") or ""
        if not hypothese:
            return "Übersprungen"
        # Erste 100 Zeichen der Hypothese anzeigen.
        if len(hypothese) > 100:
            return hypothese[:100] + " …"
        return hypothese

    if node_name == "haltungsraum":
        # `kurzfassung()` liefert die Zeile fertig — Umfang, Fragen, Nähe,
        # Wärme, Drängen, dazu Grenze, Übersteuerung und die Marke für ein
        # Ergebnis außerhalb der Spanne.
        haltung = node_state.get("haltung")
        if haltung is None:
            # **Nicht "—".** Ein Turn ohne Rechnung muss von einem mit lauter
            # Nullen unterscheidbar bleiben (novaberg-haltungsraum_k.md §2.0a);
            # der Strich ist der Vorgabewert jedes Knotens ohne Details und
            # sagt deshalb nichts.
            return "nicht gerechnet"
        return haltung.kurzfassung()

    if node_name == "perzeption_assistant":
        # Nova-Wahrnehmung der eigenen Antwort aus internal.emotion
        internal = node_state.get("internal")
        emotion: str   = (internal.emotion.emotion if internal else "").capitalize()
        arousal: float = internal.emotion.arousal if internal else 0.0
        modus:   str   = (internal.emotion.mode    if internal else "").capitalize()

        teile: list[str] = []

        if emotion and emotion != "Neutral":
            if arousal >= 0.7:
                intensitaet: str = "intensiv"
            elif arousal >= 0.4:
                intensitaet = "moderat"
            else:
                intensitaet = "mild"
            teile.append(f"Nova: {emotion} ({intensitaet})")

        if modus and modus != "Alltag":
            teile.append(modus)

        return " · ".join(teile) if teile else "—"

    # Nodes ohne spezifische Details (gespraechsvektor, salience, dispatcher, tribunal)
    return "—"


#: Der erste Knoten NACH der Freigabe durch `evaluate`.
#:
#: **Die Freigabe faellt in einer Kante, und Kanten erscheinen nicht im
#: Stream.** `_after_evaluate` entscheidet zwischen `output`, `fallback` und
#: `correct`; die ersten beiden fuehren zu diesem Knoten, der dritte zurueck
#: in den Corrector. Erscheint er also, ist entschieden und der Text steht —
#: die vier Knoten ab hier aendern ihn nicht mehr.
_KNOTEN_NACH_FREIGABE: str = "perzeption_assistant"


def _graph_streamen(
    compiled_character,
    state: dict,
    loop: asyncio.AbstractEventLoop,
    user_id: str,
    character_id: str = "",
    bei_freigabe=None,
) -> dict:
    """Führt den CharacterGraph als Stream aus und sendet Stages per WebSocket.

    Läuft in einem separaten Thread (via asyncio.to_thread). Für jede Node-
    Completion wird ein Stage-Event per asyncio.run_coroutine_threadsafe
    an den Client gesendet — dadurch sieht der User die Stages live.

    Args:
        compiled_character: Kompilierter CharacterGraph (.stream()-fähig).
        state: Initialer State-Dict für den Graph-Durchlauf.
        loop: Referenz auf den asyncio Event-Loop (für WebSocket-Sends).
        user_id: User-ID für WebSocket-Broadcast.
        character_id: Charakter-ID für WebSocket-Filterung.

    Returns:
        Letzter State-Dict nach Graph-Durchlauf.
    """
    letzter_state: dict = state

    # **Der Zwischenstand muss die Ausnahme ueberleben.**
    #
    # Nach der Freigabe (`evaluate -> output`) folgen vier Knoten, die den
    # Text nicht mehr aendern: Perzeption, EI-Persistenz, Salienz,
    # Dispatcher. Reisst einer davon, war die Antwort trotzdem fertig und
    # von Thinker und Tribunal freigegeben — sie ging bisher nur verloren,
    # weil die Ausnahme diese Funktion verliess, bevor jemand `letzter_state`
    # gelesen hatte.
    #
    # `[gemessen]` — 25.08.2026, 13:33 UTC: Antwort um :07 erzeugt, um :18
    # vom Tribunal angenommen, um :24 riss ein `TypeError` in der Salienz den
    # Graphen. Der Nutzer sah nichts, und die Eingabe wurde freigegeben, als
    # waere der Turn erledigt. Kennung: `AUSLIEFERUNG-HINTER-DEM-NACHLAUF`.
    #
    # **Gerettet wird die Antwort, nicht der Fehler.** Er wird mit Traceback
    # protokolliert, und der Stand traegt eine Marke — ein abgebrochener Lauf
    # darf nicht wie ein abgeschlossener aussehen
    # (`17_NEBENLAEUFIGKEIT/keine-stillen-uebersprunge.md`).
    traeger: list = [letzter_state]
    try:
        _knoten_streamen(compiled_character, state, loop, user_id, character_id,
                         traeger, bei_freigabe)
    except Exception as fehler:
        logger.exception(
            f"{type(fehler).__name__}: Graph-Lauf abgebrochen — der Stand bis "
            f"hierher wird ausgeliefert ({user_id}:{character_id})"
        )
        abgebrochen: dict = dict(traeger[0])
        abgebrochen["lauf_unvollstaendig"] = True
        abgebrochen["lauf_fehler"] = f"{type(fehler).__name__}: {fehler}"
        return abgebrochen

    return traeger[0]


def _knoten_streamen(
    compiled_character,
    state: dict,
    loop: asyncio.AbstractEventLoop,
    user_id: str,
    character_id: str,
    traeger: list,
    bei_freigabe=None,
) -> None:
    """Laeuft den Graphen ab und legt jeden Knotenstand in `traeger[0]`.

    **Der Traeger ist eine Liste, damit der Stand die Ausnahme ueberlebt.**
    Eine lokale Variable waere mit dem Stack fort; der Aufrufer braucht sie
    aber gerade dann, wenn der Lauf nicht bis zum Ende kam.
    """
    for chunk in compiled_character.stream(state):
        # LangGraph liefert nach Subgraph-Return manchmal Listen statt Dicts.
        if not isinstance(chunk, dict):
            logger.debug(
                f"Stream: Überspringe Nicht-Dict-Chunk "
                f"(Typ: {type(chunk).__name__})"
            )
            continue

        for node_name, node_state in chunk.items():
            traeger[0] = node_state

            # **Freigegeben heisst gesendet.** Bis zum 25.08.2026 wartete die
            # Auslieferung auf END — also hinter Perzeption, EI-Persistenz,
            # Salienz und Dispatcher. Am 25.08. um 13:33 kostete das eine
            # Antwort, die das Tribunal siebzehn Sekunden zuvor angenommen
            # hatte: Ein `TypeError` in der Salienz riss den Graphen, und der
            # Mensch sah nichts.
            #
            # **Der Nachlauf laeuft unveraendert weiter** — er schreibt Novas
            # Zustand, die Salienz und das Gedaechtnis. Nur wartet niemand
            # mehr darauf.
            if (node_name == _KNOTEN_NACH_FREIGABE
                    and bei_freigabe is not None
                    and node_state.get("response")):
                try:
                    bei_freigabe(node_state)
                except Exception as fehler:
                    # Ein Fehler beim Senden darf den Graphen nicht reissen —
                    # das waere genau der Tausch, den dieser Umbau beseitigt.
                    logger.exception(
                        f"{type(fehler).__name__}: Auslieferung bei Freigabe "
                        f"fehlgeschlagen ({user_id}:{character_id})"
                    )

            # Stage per WebSocket an alle Clients senden (live, während der Graph läuft).
            label:  str = CHARACTER_NODE_LABELS.get(node_name, node_name)
            detail: str = _stage_detail_bauen(node_name, node_state)

            stage_payload: str = json.dumps({
                "typ":    "character_stage",
                "node":   node_name,
                "label":  label,
                "detail": detail,
            }, ensure_ascii=False)

            broadcast_threadsafe(user_id, stage_payload, loop, character_id=character_id)


async def event_consumer_loop(
    redis_client,
    character_graph,
    compiled_character,
    websocket_map: dict,
    llm_lock,
) -> None:
    """Endlos-Loop: Pollt Event-Queues, verarbeitet Events, sendet Antworten.

    Args:
        redis_client: Redis-Verbindung.
        character_graph: CharacterGraph-Instanz (für create_state).
        compiled_character: Kompilierter CharacterGraph (für invoke).
        websocket_map: Dict {user_id: list[WebSocket]} für Antwort-Delivery.
        llm_lock: Threading-Lock für GPU-Zugriff.
    """
    logger.info("Event-Consumer gestartet.")

    while True:
        try:
            await asyncio.sleep(POLL_INTERVAL)

            if shutdown_event.is_set():
                logger.info("Event-Consumer: Shutdown erkannt — beende Loop")
                break

            # ── Aktive Event-Queues finden ──
            queue_keys: list = redis_client.keys("event_queue:*")

            if not queue_keys:
                continue

            for key in queue_keys:
                # Key-Format: event_queue:{user_id}:{character_id}
                key_str: str = key if isinstance(key, str) else key.decode()
                parts: list[str] = key_str.split(":")

                if len(parts) != 3:
                    continue

                _, user_id, character_id = parts

                # ── Nächstes Event holen ──
                event: dict | None = event_naechstes(redis_client, user_id, character_id)

                if not event:
                    continue

                # ── Debounce bei User-Events ──
                # Warten bis der User fertig getippt hat.
                # Weitere User-Events werden verworfen — die Turns
                # liegen bereits in der Session (Pfad 1 hat sie geschrieben).
                if event["source"] == "user":
                    await asyncio.sleep(DEBOUNCE_DELAY)

                    drained: int = 0
                    while True:
                        extra = event_naechstes(redis_client, user_id, character_id)
                        if not extra:
                            break
                        # Letztes Event übernehmen (aktuellster Payload)
                        event = extra
                        drained += 1

                    if drained:
                        logger.info(
                            f"Event-Consumer: {drained} weitere Events zusammengefasst "
                            f"(Debounce, {user_id}:{character_id})"
                        )

                logger.info(
                    f"Event-Consumer: Verarbeite {event['typ']} "
                    f"(source={event['source']}, {user_id}:{character_id})"
                )

                # Auch ein eigener Impuls ist ein Turn. Er kommt nicht aus
                # der Eingangs-Queue und hat deshalb keinen Marker — ohne
                # diesen hier bliebe die Eingabe waehrend seines Durchlaufs
                # offen, und eine gleichzeitig eingespeiste Aeusserung liefe in
                # dieselbe Zeitueberschreitung, gegen die der Marker gebaut ist.
                #
                # Das Ergebnis wird nicht geprueft: Bei einem Nutzer-Turn steht
                # der Marker bereits, und dass er steht, ist genau das
                # Gewuenschte.
                turn_beginnen(
                    redis_client, user_id, character_id,
                    event.get("event_id", "ereignis"),
                )

                # ── CharacterGraph ausführen ──
                try:
                    await _event_verarbeiten(
                        event, user_id, character_id,
                        redis_client, character_graph, compiled_character,
                        websocket_map, llm_lock,
                    )
                finally:
                    # Hier endet der Turn — nicht nach Pfad 1. Solange der
                    # Marker steht, haelt der Prompt-Consumer neue
                    # Aeusserungen in der Eingangs-Queue zurueck. Im `finally`,
                    # weil ein gescheiterter Durchlauf die Eingabe sonst
                    # dauerhaft sperrte; der Verfall des Markers waere dann die
                    # einzige Rettung, und der dauert Minuten.
                    turn_beenden(redis_client, user_id, character_id)

        except asyncio.CancelledError:
            logger.info("Event-Consumer beendet.")
            break

        except Exception as fehler:
            logger.exception(f"{type(fehler).__name__}: Event-Consumer: Unerwarteter Fehler")
            await asyncio.sleep(POLL_INTERVAL)


def _antwort_nutzlast_bauen(
    zustand: dict,
    turn_id: str,
    payload: dict,
    event: dict,
) -> str:
    """Baut die `character_response`-Nutzlast aus einem Graphenzustand.

    **Ausgelagert, weil sie an zwei Zeitpunkten gebraucht wird:** bei der
    Freigabe durch `evaluate` (der Regelfall seit dem 25.08.2026) und am Ende
    des Laufs als Rueckfall, falls die Freigabe nicht erreicht wurde.

    Die vier Felder aus `internal` beschreiben **Novas Zustand nach ihrer
    eigenen Antwort** — sie entstehen erst im Nachlauf und sind bei der
    Freigabe leer. Gemessen am 25.08.2026 liest der Client sieben der acht
    Zustandsfelder gar nicht; einzig `momentum` wird angezeigt, und das steht
    schon vor dem Responder.

    Args:
        zustand: Der Graphenzustand, aus dem gebaut wird.
        turn_id: Kennung des Reizes, auf den geantwortet wird.
        payload: Die Nutzlast des Ereignisses (traegt `nachrichten_ids`).
        event: Das Ereignis selbst (traegt `reiz_herkunft`).

    Returns:
        Die fertige JSON-Zeichenkette.
    """
    zustand_internal = zustand.get("internal")

    # **Was gefuellt war, steht im Log — nicht nur, wie lang die Antwort ist.**
    # Bis zum 25.08.2026 meldete die Zustellung `342 Zeichen, 2 Clients` und
    # sonst nichts; welches der acht Zustandsfelder gefehlt hat, war
    # hinterher nicht feststellbar (`18_NACHVOLLZIEHBARKEIT.md` §3: die
    # Eingangsgroessen einzeln).
    _belegung: dict = {
        "nova_emotion":         bool(zustand.get("nova_emotions_verlauf")),
        "nova_emotions_vektor": bool(zustand_internal),
        "intent":               bool(zustand_internal),
        "tone":                 bool(zustand_internal),
        "gespraechs_modus":     bool(zustand_internal),
        "user_intentionen":     bool(zustand.get("user_intentionen")),
        "momentum":             bool(zustand.get("momentum")),
        "gespraechsvektor":     bool(zustand.get("gespraechsvektor")),
    }
    _fehlend: list = sorted(f for f, da in _belegung.items() if not da)
    logger.info(
        "Nutzlast: %d von 8 Zustandsfeldern gefuellt%s (turn_id=%s, %d Zeichen)",
        sum(_belegung.values()),
        f" — leer: {', '.join(_fehlend)}" if _fehlend else "",
        turn_id or "(keine)",
        len(zustand.get("response", "")),
    )
    return json.dumps({
        "typ":                "character_response",
        "nachricht":          zustand.get("response", ""),
        # Der Reiz, auf den diese Antwort antwortet. Leer heisst
        # "nicht zuordenbar" und ist oben als Fehler gemeldet — der Client
        # darf daraus nicht schliessen, die Antwort gehoere zur letzten
        # Nachricht.
        "turn_id":            turn_id,
        # Die Kennungen der einzelnen Aeusserungen, die dieser Turn
        # beantwortet. Ein Turn kann mehrere umfassen: Was innerhalb des
        # Eingangsfensters eintraf, wurde zu einem Prompt zusammengefasst.
        # Der Client hat je Aeusserung eine Bestaetigung bekommen und haelt
        # sie offen, bis eine Antwort sie nennt.
        "nachrichten_ids":    payload.get("nachrichten_ids", []),
        # Herkunft des Reizes: "eigener_impuls" bei einem Pixie-Gedanken,
        # sonst leer. Der Client faerbt danach ein — vor dem Umbau erkannte
        # er einen Impuls daran, dass der Nachrichtentyp ihm unbekannt war
        # (shadow_impuls). Jetzt traegt jede Antwort denselben Typ, also
        # muss das Merkmal ausdruecklich mitreisen.
        "reiz_herkunft":      (event.get("payload") or {}).get("reiz_herkunft", ""),
        "modell":             zustand.get("model", ""),
        "token_total":        zustand.get("token_total", 0),
        "emotion":            zustand_internal.emotion.emotion              if zustand_internal else "",
        "arousal":            zustand_internal.emotion.arousal              if zustand_internal else 0.0,
        "emotions_vektor":    zustand_internal.emotion.emotions_vector      if zustand_internal else "",
        "emotions_verlauf":   zustand.get("emotions_verlauf", []),
        "sprach_stil":        zustand_internal.emotion.language_style       if zustand_internal else "",
        "beziehungs_dynamik": zustand_internal.emotion.relationship_dynamic if zustand_internal else "",
        "nova_emotion":           zustand.get("nova_emotions_verlauf", [{}])[0].get("emotion", "") if zustand.get("nova_emotions_verlauf") else "",
        "nova_arousal":           zustand.get("nova_emotions_verlauf", [{}])[0].get("arousal", 0.0) if zustand.get("nova_emotions_verlauf") else 0.0,
        "nova_emotions_verlauf":  zustand.get("nova_emotions_verlauf", []),
        "nova_emotions_vektor":   zustand_internal.emotion.emotions_vector if zustand_internal else "",
        "nova_emotion_konflikt":  zustand.get("nova_emotion_konflikt", False),
        "intent":             zustand_internal.emotion.intent if zustand_internal else "",
        "tone":               zustand_internal.emotion.tone   if zustand_internal else "",
        "gespraechs_modus":   zustand_internal.emotion.mode   if zustand_internal else "",
        "user_intentionen":   zustand.get("user_intentionen", []),
        "momentum":           zustand.get("momentum", ""),
        "gespraechsvektor":   zustand.get("gespraechsvektor", ""),
    }, ensure_ascii=False)


async def _event_verarbeiten(
    event: dict,
    user_id: str,
    character_id: str,
    redis_client,
    character_graph,
    compiled_character,
    websocket_map: dict,
    llm_lock,
) -> None:
    """Verarbeitet ein einzelnes Event — Graph-Stream + WebSocket-Delivery.

    Führt den CharacterGraph per .stream() aus. Jede Node-Completion wird
    als Stage-Event an den Client gesendet. Nach dem Durchlauf folgt die
    Charakter-Antwort als character_response-Event.

    Args:
        event: Event-Dict aus der Queue.
        user_id: User-ID.
        character_id: Charakter-ID.
        redis_client: Redis-Verbindung.
        character_graph: CharacterGraph-Instanz (für create_state).
        compiled_character: Kompilierter CharacterGraph (für stream).
        websocket_map: Dict {user_id: list[WebSocket]} für Delivery.
        llm_lock: Threading-Lock für GPU-Zugriff.
    """
    payload:     dict = event.get("payload", {})
    user_prompt: str  = payload.get("user_prompt", "")

    # Novas eigener Gedanke, wenn die Zustellung diesen Lauf angestossen hat.
    # Er reist getrennt vom Reiz-Platz, weil auf einem Impuls-Turn niemand
    # gesprochen hat — was dort steht, waere eine Aeusserung, die es nicht gab.
    eigener_gedanke: str = payload.get("eigener_gedanke", "")

    # Die Kennung des Reizes, den dieser Durchlauf beantwortet. Sie reist bis
    # in die Antwort-Nutzlast durch: Ohne sie ordnet der Client der letzten
    # Nachricht zu, was ankommt — und nach einem Ausfall verschiebt sich alles
    # um eins (novaberg-bugs.md -> ANTWORT-OHNE-ZUORDNUNG).
    #
    # Sie wird ausdruecklich **hier** gelesen und nicht spaeter aus dem
    # Ergebnis-Zustand: Der Zustand traegt dieselbe Kennung nur, solange
    # niemand sie unterwegs ueberschreibt, und was der Client braucht, ist die
    # Kennung seiner Frage — nicht die des Laufs, der geantwortet hat.
    turn_id: str = payload.get("turn_id", "")

    if not turn_id:
        # Jeder Erzeuger eines Turns setzt sie (novaberg-convention-event-model.md
        # 3.1.1). Fehlt sie, ist die Antwort nicht zuordenbar — der Durchlauf
        # laeuft trotzdem weiter, weil ein verworfener Turn teurer ist als eine
        # Antwort ohne Zuordnung.
        logger.error(
            f"Event-Consumer: Event ohne turn_id — die Antwort ist beim Client "
            f"nicht zuordenbar ({user_id}:{character_id}, source="
            f"{event.get('source', '?')}, typ={event.get('typ', '?')}, "
            f"Payload-Felder: {sorted(payload)})"
        )

    # Die Salienz des Reizes, den Nova gerade beantwortet. Bewusst ohne
    # Default: payload.get() liefert None, wenn der Schluessel fehlt — und
    # genau das ist der richtige Wert fuer einen eigenen Impuls, der gar keine
    # Nutzeraeusserung hat. Ein Default 0.0 wuerde daraus die Aussage machen,
    # der Nutzer habe etwas Belangloses gesagt.
    salienz_human = payload.get("salienz_human")

    # Die Intentionen desselben Reizes. Anders als bei `salienz_human` ist der
    # Default hier die leere Liste und nicht None: `user_intentionen` ist im
    # Zustandstyp als Liste deklariert, und ein eigener Impuls ohne
    # Nutzeraeusserung hat schlicht keine. Die Unterscheidung "nicht erhoben"
    # gegen "keine Richtung" trifft nicht dieser Default, sondern
    # `_wollen_messen` — eine leere Liste gilt dort als **fehlend**.
    user_intentionen: list = payload.get("user_intentionen", []) or []

    # ── State erzeugen ──
    state: dict = character_graph.create_state(
        user_prompt   = user_prompt,
        eigener_gedanke = eigener_gedanke,
        user_id       = user_id,
        character_id  = character_id,
        event_source  = event.get("source", "user"),
        event_payload = payload,
        turn_id       = turn_id,
        salienz_human = salienz_human,
        user_intentionen = user_intentionen,
    )

    logger.info(
        f"Event-Consumer: salienz_human={salienz_human}, "
        f"user_intentionen={user_intentionen or 'keine'} in den CharacterGraph "
        f"gereicht (turn_id={turn_id}, "
        f"herkunft={payload.get('reiz_herkunft', 'nutzer_turn')})"
    )

    # Hinweis: Die Perzeption-Daten aus dem Pfad-1-Payload werden vom
    # db_zugriff-Node direkt aus event_payload in state["external"].emotion
    # gelesen — keine separate Seeding-Bridge mehr noetig.
    logger.debug(
        f"Event-Consumer: Payload enthaelt "
        f"emotion={payload.get('current_emotion', '')}, "
        f"arousal={payload.get('current_arousal', 0.0)}, "
        f"modus={payload.get('gespraechs_modus', '')} — "
        f"wird von db_zugriff in external.emotion geladen"
    )

    # ── Event-Loop-Referenz für threadsichere WebSocket-Sends ──
    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    # ── Prüfe ob WebSocket-Clients verbunden sind ──
    hat_clients: bool = bool(websocket_map.get(user_id))

    if not hat_clients:
        logger.warning(
            f"Event-Consumer: Kein WebSocket für '{user_id}' — "
            f"Stages und Antwort nur in Session"
        )

    # ── Graph-Durchlauf mit Streaming (GPU, braucht Lock) ──
    acquired: bool = llm_lock.acquire(blocking=True, timeout=60)

    if not acquired:
        logger.warning(
            f"Event-Consumer: LLM-Lock Timeout — "
            f"Event verworfen ({user_id}:{character_id})"
        )
        return

    # **Die Auslieferung haengt an der Freigabe, nicht am Ende des Laufs.**
    # `bereits_gesendet` traegt die Auskunft aus dem Arbeitsthread zurueck —
    # der Rueckruf laeuft dort, nicht im Ereignis-Loop, und darum geht die
    # Zustellung ueber `broadcast_threadsafe`.
    bereits_gesendet: list = []

    def _bei_freigabe(zustand: dict) -> None:
        """Stellt die freigegebene Antwort zu — aus dem Arbeitsthread heraus."""
        if not websocket_map.get(user_id):
            return
        nutzlast: str = _antwort_nutzlast_bauen(zustand, turn_id, payload, event)
        broadcast_threadsafe(user_id, nutzlast, loop, character_id=character_id)
        bereits_gesendet.append(True)
        logger.info(
            f"Event-Consumer: Antwort bei Freigabe gesendet "
            f"({len(zustand.get('response', ''))} Zeichen, "
            f"{len(websocket_map.get(user_id, []))} Clients) — "
            f"der Nachlauf laeuft weiter"
        )

    try:
        result: dict = await asyncio.to_thread(
            _graph_streamen,
            compiled_character, state, loop, user_id, character_id,
            _bei_freigabe,
        )
    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Event-Consumer: Graph-Fehler")
        return
    finally:
        llm_lock.release()

    # ── Antwort per WebSocket senden ──
    response: str = result.get("response", "")

    if bereits_gesendet:
        # Der Regelfall seit dem 25.08.2026: Die Antwort ist bei der Freigabe
        # herausgegangen, der Nachlauf ist seither gelaufen. Hier bleibt
        # nichts zu tun — eine zweite Zustellung waere eine zweite Antwort.
        logger.debug(
            f"Event-Consumer: bereits bei Freigabe zugestellt "
            f"({user_id}:{character_id}) — kein zweiter Versand"
        )

    elif response and websocket_map.get(user_id):
        # WebSocket-Payload zeigt Novas Wahrnehmung ihrer eigenen Antwort
        # (internal.emotion, von perzeption_assistant + ei_calc_persist
        # gesetzt). nova_emotions_vector wandert in internal.emotion.
        # `internal` wird dabei in _antwort_nutzlast_bauen selbst gelesen; die
        # Zeile, die es hier noch einmal holte, hat nie etwas damit getan.
        response_payload: str = _antwort_nutzlast_bauen(result, turn_id, payload, event)

        await broadcast(user_id, response_payload, character_id=character_id)

        logger.info(
            f"Event-Consumer: Antwort gesendet per WebSocket "
            f"({len(response)} Zeichen, "
            f"{len(websocket_map.get(user_id, []))} Clients)"
        )

    elif response:
        logger.warning(
            f"Event-Consumer: Kein WebSocket für '{user_id}' — "
            f"Antwort nur in Session"
        )

    else:
        # **Der stille Ausgang am Ende der Kette, bis zum 19.08.2026 ohne
        # eine einzige Zeile.** Eine leere Antwort fiel hier durch: kein
        # Senden, keine Meldung, und der Client blieb auf dem letzten
        # Stufen-Ereignis stehen — vom Menschen nicht von einem Haenger zu
        # unterscheiden. Ein Rueckkehrpfad, der die Arbeit nicht tut, ist ein
        # Fehler und keine Warnung.
        logger.error(
            f"Event-Consumer: NICHTS ZUGESTELLT für '{user_id}:{character_id}' — "
            f"die Antwort ist leer (0 Zeichen). Der Turn ist gelaufen und "
            f"erreicht den Menschen nicht; welcher Schreiber sie geleert hat, "
            f"steht in den Zeilen 'Antwort-Spur' darueber"
        )

        # **Der Log allein reicht nicht — er hat keinen Leser am anderen Ende.**
        # Bis hierher wusste der Server vom Ausfall und der Mensch nicht: Der
        # Client blieb auf der letzten Stufenmeldung stehen, die Eingabe wurde
        # freigegeben, und das war von einem Haenger nicht zu unterscheiden.
        # **Ein Turn, der scheitert, darf nicht aussehen wie einer, der
        # erledigt ist.**
        if websocket_map.get(user_id):
            grund: str = result.get("lauf_fehler", "")
            await broadcast(user_id, json.dumps({
                "typ":       "turn_gescheitert",
                "nachricht": (
                    "Dieser Turn hat keine Antwort erreicht. "
                    + (f"Abbruch: {grund}. " if grund else "")
                    + "Der Fehler steht im Serverprotokoll."
                ),
                "turn_id":   turn_id,
                "grund":     grund,
                "unvollstaendig": bool(result.get("lauf_unvollstaendig")),
            }, ensure_ascii=False), character_id=character_id)

    # ── Self-Trigger prüfen ──
    trigger_count: int = event.get("trigger_count", 0)

    # Kein Self-Trigger wenn:
    # 1. Limit erreicht
    # 2. Agent wartet auf Rückfrage (pending_agent in Redis)
    pending_key: str = f"pending_agent:{user_id}"
    has_pending: bool = redis_client.exists(pending_key)

    if has_pending:
        logger.info("Event-Consumer: Pending Agent erkannt — kein Self-Trigger")
        return

    if not event_self_trigger_erlaubt(trigger_count):
        logger.warning(
            "Event-Consumer: Self-Trigger verworfen — Limit erreicht "
            "(trigger_count=%d, MAX_SELF_TRIGGERS=%d, paar=%s:%s)",
            trigger_count, MAX_SELF_TRIGGERS, user_id, character_id,
        )
        return

    # Block 3 Teil D: Self-Trigger aktiviert. Aufrufer (heute: Thinker bei
    # Doppel-Fehlschlag, siehe graph/nodes/thinker.py) signalisiert via
    # result["self_trigger"] und liefert das Payload fuer den Folge-
    # Durchlauf ueber result["self_trigger_payload"]. Die vorhandenen
    # Haertungen (pending_agent, MAX_SELF_TRIGGERS) greifen bereits oben.
    logger.info(
        "Event-Consumer: Self-Trigger im Result — vorhanden=%s, wert=%r",
        "self_trigger" in result, result.get("self_trigger"),
    )
    if result.get("self_trigger"):
        event_erzeugen(
            redis_client, user_id, character_id,
            source="character",
            typ="continue",
            payload=result.get("self_trigger_payload", {}),
            trigger_count=trigger_count + 1,
        )
        logger.info(
            "Event-Consumer: Self-Trigger gesetzt (Thinker-Unsicherheit) — "
            "Folge-Durchlauf mit trigger_count=%d",
            trigger_count + 1,
        )
        return

    logger.info("Event-Consumer: Durchlauf abgeschlossen, kein Self-Trigger")
