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
from config import shutdown_event, ASSISTANT_USER_ID
from services.events import (
    event_naechstes,
    event_erzeugen,
    event_self_trigger_erlaubt,
)

logger = logging.getLogger("ki_server.event_consumer")

# ─────────────────────────────────────────────
# Konstanten
# ─────────────────────────────────────────────
POLL_INTERVAL:  float = 1.0     # Sekunden zwischen Queue-Checks
DEBOUNCE_DELAY: float = 2.0     # Sekunden warten nach User-Event (Tippen abwarten)

# Node-Labels für CharacterGraph (Pfad 2) — angezeigt als Stage im Client.
CHARACTER_NODE_LABELS: dict[str, str] = {
    "enricher":             "Enricher — Kontext laden",
    "ei_calc":              "EI-Calc — Emotionale Intelligenz",
    "router":               "Router — Entscheidung",
    "planner":              "Planner — Aufgabenplanung",
    "agent_dispatch":       "Agent — Ausführung",
    "gv_node":              "Gesprächsvektor — Tonalität",
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
    if node_name == "enricher":
        hat_kontext: bool = bool(node_state.get("memory_context", ""))
        modus:       str  = (node_state.get("gespraechs_modus") or "").capitalize()
        emotion:     str  = (node_state.get("user_emotion") or "").capitalize()
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
        vektor:     str = node_state.get("emotions_vektor", "") or ""
        stil:       str = node_state.get("sprach_stil", "") or ""
        modus_korr: str = node_state.get("gespraechs_modus", "") or ""
        has_bez:   bool = bool(node_state.get("beziehungs_kontext", ""))

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
            f"Intent: {node_state.get('intent', '?')}, "
            f"Ton: {node_state.get('tone', '?')}, "
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
            neugier:   float = float(gv_detail.get("effektive_neugier", 0.0) or 0.0)
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

    if node_name == "perzeption_assistant":
        emotion: str   = (node_state.get("current_emotion") or "").capitalize()
        arousal: float = node_state.get("current_arousal", 0.0)
        modus:   str   = (node_state.get("gespraechs_modus") or "").capitalize()

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


def _graph_streamen(
    compiled_character,
    state: dict,
    loop: asyncio.AbstractEventLoop,
    user_id: str,
    character_id: str = "",
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

    for chunk in compiled_character.stream(state):
        # LangGraph liefert nach Subgraph-Return manchmal Listen statt Dicts.
        if not isinstance(chunk, dict):
            logger.debug(
                f"Stream: Überspringe Nicht-Dict-Chunk "
                f"(Typ: {type(chunk).__name__})"
            )
            continue

        for node_name, node_state in chunk.items():
            letzter_state = node_state

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

    return letzter_state


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

                # ── CharacterGraph ausführen ──
                await _event_verarbeiten(
                    event, user_id, character_id,
                    redis_client, character_graph, compiled_character,
                    websocket_map, llm_lock,
                )

        except asyncio.CancelledError:
            logger.info("Event-Consumer beendet.")
            break

        except Exception as fehler:
            logger.error(f"Event-Consumer: Unerwarteter Fehler — {fehler}")
            await asyncio.sleep(POLL_INTERVAL)


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

    # ── State erzeugen ──
    state: dict = character_graph.create_state(
        user_prompt   = user_prompt,
        user_id       = user_id,
        character_id  = character_id,
        event_source  = event.get("source", "user"),
        event_payload = payload,
    )

    # ── Perzeption-Daten aus Pfad 1 in den State seeden ──
    # Die Perzeption lief in Pfad 1 (HumanGraph). Ihre Ergebnisse wurden
    # im Event-Payload transportiert und werden hier in den Pfad-2-State
    # übernommen, damit EI-Calc, Router und GV-Node sie sehen.
    perzeption_felder: list[str] = [
        "current_emotion", "current_arousal", "gespraechs_modus",
        "intent", "tone", "sprach_stil", "beziehungs_dynamik",
        "emotions_vektor",
    ]
    for feld in perzeption_felder:
        wert = payload.get(feld)
        if wert is not None:
            state[feld] = wert

    logger.debug(
        f"Event-Consumer: Perzeption-Daten geseedet — "
        f"emotion={state.get('current_emotion', '')}, "
        f"arousal={state.get('current_arousal', 0.0)}, "
        f"modus={state.get('gespraechs_modus', '')}"
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

    try:
        result: dict = await asyncio.to_thread(
            _graph_streamen,
            compiled_character, state, loop, user_id, character_id,
        )
    except Exception as fehler:
        logger.error(f"Event-Consumer: Graph-Fehler — {fehler}")
        return
    finally:
        llm_lock.release()

    # ── Antwort per WebSocket senden ──
    response: str = result.get("response", "")

    if response and websocket_map.get(user_id):
        response_payload: str = json.dumps({
            "typ":                "character_response",
            "nachricht":          response,
            "modell":             result.get("model", ""),
            "token_total":        result.get("token_total", 0),
            "emotion":            result.get("current_emotion", ""),
            "arousal":            result.get("current_arousal", 0.0),
            "emotions_vektor":    result.get("emotions_vektor", ""),
            "emotions_verlauf":   result.get("emotions_verlauf", []),
            "sprach_stil":        result.get("sprach_stil", ""),
            "beziehungs_dynamik": result.get("beziehungs_dynamik", ""),
            "nova_emotion":           result.get("nova_emotions_verlauf", [{}])[0].get("emotion", "") if result.get("nova_emotions_verlauf") else "",
            "nova_arousal":           result.get("nova_emotions_verlauf", [{}])[0].get("arousal", 0.0) if result.get("nova_emotions_verlauf") else 0.0,
            "nova_emotions_verlauf":  result.get("nova_emotions_verlauf", []),
            "nova_emotions_vektor":   result.get("nova_emotions_vektor", ""),
            "nova_emotion_konflikt":  result.get("nova_emotion_konflikt", False),
            "intent":             result.get("intent", ""),
            "tone":               result.get("tone", ""),
            "gespraechs_modus":   result.get("gespraechs_modus", ""),
            "user_intentionen":   result.get("user_intentionen", []),
            "momentum":           result.get("momentum", ""),
            "gespraechsvektor":   result.get("gespraechsvektor", ""),
        }, ensure_ascii=False)

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
        return

    # Platzhalter für spätere Erweiterung:
    #
    # if result.get("self_trigger"):
    #     event_erzeugen(
    #         redis_client, user_id, character_id,
    #         source="character",
    #         typ="continue",
    #         payload=result.get("self_trigger_payload", {}),
    #         trigger_count=trigger_count + 1,
    #     )

    logger.info("Event-Consumer: Durchlauf abgeschlossen, kein Self-Trigger")
