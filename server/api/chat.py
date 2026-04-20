"""
Chat-Endpunkte — Synchron und SSE-Streaming.
"""

import json
import logging
import time

from fastapi                    import APIRouter, Request
from fastapi.responses          import JSONResponse, StreamingResponse

from config                     import redis_client, ollama_gpu_client, OLLAMA_MODEL, EMBED_MODEL, POSTGRES_URL, llm_lock
from api.models                 import GespraechAnfrage, GespraechAntwort
from graph.memory               import (
    session_turn_store,
    session_turn_mark_action,
    session_summarize_if_needed,
)
from memory.embedding           import embedding_create
from memory.repositories.entitaeten_repository import EntitaetenRepository

from services.shadow_delivery   import shadow_cooldown_reset
from services.nachbearbeitung   import nachbearbeitung_starten

logger = logging.getLogger("ki_server.chat")


def _user_entitaet_sicherstellen(user_id: str) -> None:
    """Stellt sicher, dass eine User-Entität existiert. Gecacht via Redis."""
    cache_key: str = f"user_entity_ok:{user_id}"
    if redis_client.exists(cache_key):
        return

    bekannte: list[dict] = EntitaetenRepository.find_by_user(POSTGRES_URL, user_id)
    user_existiert: bool = any(e.get("typ") == "user" for e in bekannte)

    if not user_existiert:
        zusammenfassung: str = f"Der User. Login: {user_id}"
        try:
            embedding: list[float] = embedding_create(
                f"{user_id} {zusammenfassung}", ollama_gpu_client, EMBED_MODEL
            )
        except Exception as fehler:
            logger.warning(f"Embedding für User-Entität fehlgeschlagen: {fehler}")
            embedding = None

        EntitaetenRepository.insert(
            postgres_url=POSTGRES_URL,
            user_id=user_id,
            name=user_id,
            typ="user",
            zusammenfassung=zusammenfassung,
            embedding=embedding,
        )
        logger.info(f"User-Entität für '{user_id}' mit Embedding angelegt.")

    redis_client.set(cache_key, "1", ex=86400)


def entitaeten_embeddings_sicherstellen() -> None:
    """Erzeugt Embeddings für alle Entitäten die noch keins haben (Startup-Repair)."""
    import psycopg2

    try:
        conn = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, zusammenfassung FROM entitaeten "
            "WHERE embedding IS NULL AND aktiv = TRUE"
        )
        rows = cursor.fetchall()
        conn.close()
    except Exception as fehler:
        logger.warning(f"Embedding-Repair: DB-Abfrage fehlgeschlagen — {fehler}")
        return

    for entitaet_id, name, zusammenfassung in rows:
        embed_text: str = f"{name or ''} {zusammenfassung or ''}".strip()
        if not embed_text:
            continue

        try:
            embedding: list[float] = embedding_create(
                embed_text, ollama_gpu_client, EMBED_MODEL
            )
            EntitaetenRepository.update_embedding(POSTGRES_URL, entitaet_id, embedding)
            logger.info(f"Entität '{name}' (id={entitaet_id}): Embedding nachträglich erzeugt")
        except Exception as fehler:
            logger.warning(f"Embedding-Repair für '{name}' fehlgeschlagen: {fehler}")
router = APIRouter()

# ─────────────────────────────────────────────
# SSE-Hilfsfunktionen
# ─────────────────────────────────────────────
NODE_LABELS: dict[str, str] = {
    "perzeption": "Perzeption — Wahrnehmung",
    "enricher":   "Enricher — Kontext laden",
    "ei_calc":    "EI-Calc — Emotionale Intelligenz",
    "router":     "Router — Prompt analysieren",
    "planner":    "Planner — Operation planen",
    "responder":  "Responder — Antwort generieren",
    "thinker":    "Thinker — Nachdenken",
    "tribunal":   "Tribunal — Bewertung",
    "evaluate":   "Tribunal — Auswertung",
    "corrector":  "Corrector — Korrektur",
    "agent_dispatch":  "Agent — Ausführung",
    "gv_node": "Gesprächsvektor — Antizipation",
}


def _sse_event(event_type: str, data: dict) -> str:
    """Formatiert ein Server-Sent Event."""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# ─────────────────────────────────────────────
# Synchroner Chat
# ─────────────────────────────────────────────
@router.post("/chat", response_model=GespraechAntwort)
def ChatSenden(anfrage: GespraechAnfrage, request: Request):
    """Prompt durch den Gesprächsgraphen verarbeiten."""
    try:
        _user_entitaet_sicherstellen(anfrage.user_id)

        with llm_lock:
            session_turn_store(redis_client, anfrage.user_id, "user", anfrage.prompt)

            # Shadow Delivery: Aktivität melden + Cooldown zurücksetzen
            redis_client.set(f"last_activity:{anfrage.user_id}", str(time.time()), ex=7200)
            shadow_cooldown_reset(redis_client, anfrage.user_id)

            initial_state: dict = request.app.state.human_graph.create_state(
                user_prompt   = anfrage.prompt,
                user_id       = anfrage.user_id,
                system_prompt = anfrage.system,
                temperature   = anfrage.temperatur,
            )

            result: dict = request.app.state.conversation_graph.invoke(initial_state)

            # BUG-FIX: Original referenzierte nicht-existierendes 'letzter_state'
            session_turn_store(redis_client, anfrage.user_id, "assistant", result.get("response", ""))

            # KONTEXT1: Agent-Aktionsstatus im Session-Gedächtnis markieren
            if result.get("agent_results"):
                letztes = result["agent_results"][-1]
                status = letztes.status if hasattr(letztes, "status") else letztes.get("status")
                if status != "rueckfrage":
                    session_turn_mark_action(
                        redis_client,
                        anfrage.user_id,
                        erledigt=True,
                        erfolgreich=(status == "abgeschlossen"),
                    )

            session_summarize_if_needed(redis_client, anfrage.user_id)

            # Momentum für Shadow Delivery Service setzen (NACH Response)
            redis_client.set(f"momentum:{anfrage.user_id}", result.get("momentum", "mid"), ex=300)

        # ── Asynchrone Nachbearbeitung (User-Salienz + Nova-Pfad) ──
        nachbearbeitung_starten(
            state=result,
            human_graph=request.app.state.human_graph,
            response=result.get("response", ""),
            redis_client=redis_client,
        )

        return GespraechAntwort(
            antwort            = result["response"],
            modell             = result["model"],
            token_total        = result["token_total"],
            emotion            = result.get("current_emotion", ""),
            arousal            = result.get("current_arousal", 0.0),
            emotions_vektor    = result.get("emotions_vektor", ""),
            emotions_verlauf   = result.get("emotions_verlauf", []),
            sprach_stil        = result.get("sprach_stil", ""),
            beziehungs_dynamik = result.get("beziehungs_dynamik", ""),
            nova_emotion           = result.get("nova_emotions_verlauf", [{}])[0].get("emotion", "") if result.get("nova_emotions_verlauf") else "",
            nova_arousal           = result.get("nova_emotions_verlauf", [{}])[0].get("arousal", 0.0) if result.get("nova_emotions_verlauf") else 0.0,
            nova_emotions_verlauf  = result.get("nova_emotions_verlauf", []),
            nova_emotions_vektor   = result.get("nova_emotions_vektor", ""),
            nova_emotion_konflikt  = result.get("nova_emotion_konflikt", False),
            intent             = result.get("intent", ""),
            tone               = result.get("tone", ""),
            gespraechs_modus   = result.get("gespraechs_modus", ""),
            user_intentionen   = result.get("user_intentionen", []),
            momentum           = result.get("momentum", ""),
            needs_web          = result.get("needs_web", False),
        )

    except Exception as fehler:
        logger.error(f"Graph-Fehler: {fehler}")
        return JSONResponse(
            status_code = 503,
            content     = {"fehler": f"Verarbeitungsfehler: {fehler}"},
        )


# ─────────────────────────────────────────────
# SSE-Streaming Chat
# ─────────────────────────────────────────────
@router.post("/chat/stream")
def ChatStreamSenden(anfrage: GespraechAnfrage, request: Request):
    """Prompt mit Stage-Updates via SSE."""
    _user_entitaet_sicherstellen(anfrage.user_id)

    def event_generator():
        try:
            with llm_lock:
                session_turn_store(redis_client, anfrage.user_id, "user", anfrage.prompt)

                # Shadow Delivery: Aktivität melden + Cooldown zurücksetzen
                redis_client.set(f"last_activity:{anfrage.user_id}", str(time.time()), ex=7200)
                shadow_cooldown_reset(redis_client, anfrage.user_id)

                initial_state: dict = request.app.state.human_graph.create_state(
                    user_prompt   = anfrage.prompt,
                    user_id       = anfrage.user_id,
                    system_prompt = anfrage.system,
                    temperature   = anfrage.temperatur,
                )

                letzter_state: dict = initial_state

                for chunk in request.app.state.conversation_graph.stream(initial_state):
                    # LangGraph liefert nach Subgraph-Return manchmal Listen statt Dicts
                    if not isinstance(chunk, dict):
                        logger.debug(f"Stream: Überspringe Nicht-Dict-Chunk (Typ: {type(chunk).__name__})")
                        continue
                    for node_name, node_state in chunk.items():
                        label:  str = NODE_LABELS.get(node_name, node_name)
                        detail: str = ""

                        if node_name == "perzeption":
                            emotion:  str = (node_state.get("current_emotion") or "").capitalize()
                            arousal: float = node_state.get("current_arousal", 0.0)
                            modus:    str = (node_state.get("gespraechs_modus") or "").capitalize()
                            dynamik:  str = (node_state.get("beziehungs_dynamik") or "").capitalize()

                            arousal_text: str = (
                                "ruhig" if arousal < 0.3
                                else "moderat" if arousal < 0.6
                                else "intensiv"
                            )

                            teile: list[str] = []
                            if emotion and emotion != "Neutral":
                                teile.append(f"{emotion} ({arousal_text})")
                            elif emotion:
                                teile.append(emotion)
                            if modus:
                                teile.append(modus)
                            if dynamik and dynamik != "Neutral":
                                teile.append(dynamik)

                            detail = " · ".join(teile) if teile else "—"

                        elif node_name == "router":
                            detail = (
                                f"Intent: {node_state.get('intent', '?')}, "
                                f"Ton: {node_state.get('tone', '?')}, "
                                f"Momentum: {node_state.get('momentum', '?')}"
                            )

                        elif node_name == "enricher":
                            hat_kontext: bool = bool(node_state.get("memory_context", ""))
                            modus:       str  = (node_state.get("gespraechs_modus") or "").capitalize()
                            emotion:     str  = (node_state.get("user_emotion") or "").capitalize()
                            intentionen: list = node_state.get("user_intentionen", [])
                            detail = f"Kontext: {'gefunden' if hat_kontext else 'keiner'}"
                            if modus or emotion:
                                detail += (
                                    f" | Modus: {modus or '?'}, "
                                    f"Emotion: {emotion or '?'}, "
                                    f"Intention: {', '.join(i.capitalize() for i in intentionen) if intentionen else '?'}"
                                )

                        elif node_name == "ei_calc":
                            ev:            list = node_state.get("emotions_verlauf", [])
                            vektor:         str = node_state.get("emotions_vektor", "") or ""
                            stil:           str = node_state.get("sprach_stil", "") or ""
                            modus_korr:     str = node_state.get("gespraechs_modus", "") or ""
                            has_bez:       bool = bool(node_state.get("beziehungs_kontext", ""))

                            ei_teile: list[str] = []
                            if ev:
                                top3: str = ", ".join(
                                    f"{e.get('emotion','?')}({e.get('gewicht',0):.2f})"
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

                            # Nova-Emotion ergänzen
                            nova_ev: list = node_state.get("nova_emotions_verlauf", [])
                            if nova_ev:
                                nova_top: str = nova_ev[0].get("emotion", "?")
                                nova_ar: float = nova_ev[0].get("arousal", 0.0)
                                nova_konf: bool = node_state.get("nova_emotion_konflikt", False)
                                nova_str: str = f"Nova: {nova_top}(a={nova_ar:.2f})"
                                if nova_konf:
                                    nova_str += " ⚡Konflikt"
                                ei_teile.append(nova_str)

                            detail = " | ".join(ei_teile) if ei_teile else "—"

                        elif node_name == "responder":
                            detail = f"{node_state.get('token_total', 0)} Tokens"

                        elif node_name == "evaluate":
                            verdict: str = node_state.get("tribunal_verdict", "?")
                            summary: str = node_state.get("tribunal_summary", "")
                            detail = f"Verdict: {verdict}"
                            if verdict != "ok" and summary:
                                detail += f" — {summary[:120]}"

                        elif node_name == "corrector":
                            detail = f"Runde {node_state.get('correction_round', 0)}"

                        elif node_name == "thinker":
                            needs_web: bool = node_state.get("needs_web", False)
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
                            detail = " | ".join(thinker_teile)

                        elif node_name == "planner":
                            planner_aktiv: bool = node_state.get("planner_aktiv", False)
                            agent_name: str = node_state.get("agent_name", "")
                            if planner_aktiv and agent_name:
                                detail = f"Agent: {agent_name}"
                            elif planner_aktiv:
                                detail = "Agent-Dispatch vorbereitet"
                            else:
                                detail = "Kein Agent nötig"

                        elif node_name == "agent_dispatch":
                            agent_results_list: list = node_state.get("agent_results", [])
                            if agent_results_list:
                                agent_teile: list[str] = []
                                for a_result in agent_results_list:
                                    a_name:   str = getattr(a_result, "agent_name", "?") if not isinstance(a_result, dict) else a_result.get("agent_name", "?")
                                    a_status: str = getattr(a_result, "status", "?") if not isinstance(a_result, dict) else a_result.get("status", "?")
                                    agent_teile.append(f"{a_name}: {a_status}")
                                detail = " | ".join(agent_teile)
                            else:
                                detail = "Ausführung läuft"

                        yield _sse_event("stage", {
                            "node":   node_name,
                            "label":  label,
                            "detail": detail,
                        })

                        letzter_state = node_state

                session_turn_store(
                    redis_client,
                    letzter_state["user_id"],
                    "assistant",
                    letzter_state.get("response", ""),
                )

                # KONTEXT1: Agent-Aktionsstatus im Session-Gedächtnis markieren
                if letzter_state.get("agent_results"):
                    letztes = letzter_state["agent_results"][-1]
                    status = letztes.status if hasattr(letztes, "status") else letztes.get("status")
                    if status != "rueckfrage":
                        session_turn_mark_action(
                            redis_client,
                            anfrage.user_id,
                            erledigt=True,
                            erfolgreich=(status == "abgeschlossen"),
                        )

                session_summarize_if_needed(redis_client, anfrage.user_id)

            yield _sse_event("answer", {
                "antwort":            letzter_state.get("response", ""),
                "modell":             letzter_state.get("model", OLLAMA_MODEL),
                "token_total":        letzter_state.get("token_total", 0),
                "emotion":            letzter_state.get("current_emotion", ""),
                "arousal":            letzter_state.get("current_arousal", 0.0),
                "emotions_vektor":    letzter_state.get("emotions_vektor", ""),
                "emotions_verlauf":   letzter_state.get("emotions_verlauf", []),
                "sprach_stil":        letzter_state.get("sprach_stil", ""),
                "beziehungs_dynamik": letzter_state.get("beziehungs_dynamik", ""),
                "nova_emotion":           letzter_state.get("nova_emotions_verlauf", [{}])[0].get("emotion", "") if letzter_state.get("nova_emotions_verlauf") else "",
                "nova_arousal":           letzter_state.get("nova_emotions_verlauf", [{}])[0].get("arousal", 0.0) if letzter_state.get("nova_emotions_verlauf") else 0.0,
                "nova_emotions_verlauf":  letzter_state.get("nova_emotions_verlauf", []),
                "nova_emotions_vektor":   letzter_state.get("nova_emotions_vektor", ""),
                "nova_emotion_konflikt":  letzter_state.get("nova_emotion_konflikt", False),
                "intent":             letzter_state.get("intent", ""),
                "tone":               letzter_state.get("tone", ""),
                "gespraechs_modus":   letzter_state.get("gespraechs_modus", ""),
                "user_intentionen":   letzter_state.get("user_intentionen", []),
                "momentum":           letzter_state.get("momentum", ""),
                "needs_web":          letzter_state.get("needs_web", False),
            })

            # Momentum für Shadow Delivery Service setzen (NACH Response)
            redis_client.set(
                f"momentum:{letzter_state['user_id']}",
                letzter_state.get("momentum", "mid"),
                ex=300,
            )

            # ── Asynchrone Nachbearbeitung (User-Salienz + Nova-Pfad) ──
            nachbearbeitung_starten(
                state=letzter_state,
                human_graph=request.app.state.human_graph,
                response=letzter_state.get("response", ""),
                redis_client=redis_client,
            )

        except Exception as fehler:
            logger.error(f"Stream-Fehler: {fehler}")
            yield _sse_event("error", {"fehler": str(fehler)})

    return StreamingResponse(
        event_generator(),
        media_type = "text/event-stream",
        headers    = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
