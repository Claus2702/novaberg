"""
Chat-Endpunkte — Synchron und SSE-Streaming.
"""

import json
import logging
import time
import uuid

from fastapi                    import APIRouter, Request
from fastapi.responses          import JSONResponse, StreamingResponse

from config                     import redis_client, ollama_gpu_client, EMBED_MODEL, POSTGRES_URL, llm_lock, ASSISTANT_USER_ID
from api.models                 import GespraechAnfrage
from api.websocket              import broadcast_threadsafe
from services.events            import event_erzeugen
from services.model_services    import model_service, EmbedRequest
from memory.repositories.entitaeten_repository import EntitaetenRepository

from services.shadow_delivery   import shadow_cooldown_reset

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
            request = EmbedRequest(text=f"{user_id} {zusammenfassung}")
            embed_response = model_service.embed.submit_sync(request)
            embedding: list[float] | None = embed_response.embedding
            logger.debug(
                "Chat: User-Entität Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(embedding),
                embed_response.duration_seconds,
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


async def entitaeten_embeddings_sicherstellen() -> None:
    """Erzeugt Embeddings für alle Entitäten die noch keins haben (Startup-Repair).

    Läuft im FastAPI-Lifespan im Haupt-Event-Loop und nutzt deshalb die
    async-API des EmbedWorkers direkt (submit), nicht die sync-Brücke
    (submit_sync würde den eigenen Loop blockierend belauern → Deadlock).
    Identisches Muster wie ziele_embeddings_sicherstellen.
    """
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
            request = EmbedRequest(text=embed_text)
            embed_response = await model_service.embed.submit(request)
            embedding: list[float] = embed_response.embedding
            logger.debug(
                "Chat: Entitäten-Repair Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(embedding),
                embed_response.duration_seconds,
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
    "salience":   "Salienz — Bewertung",
    "dispatcher": "Dispatcher — Speichern",
}


def _sse_event(event_type: str, data: dict) -> str:
    """Formatiert ein Server-Sent Event."""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# ─────────────────────────────────────────────
# Synchroner Chat
# ─────────────────────────────────────────────
@router.post("/chat")
def ChatSenden(anfrage: GespraechAnfrage, request: Request):
    """Prompt durch den Gesprächsgraphen verarbeiten."""
    try:
        # turn_id: korreliert HumanGraph- und CharacterGraph-Spans desselben
        # Konversations-Turns im Pipeline-Log. Vor allen Pfaden erzeugt, damit
        # beide Graphen denselben Wert in den State bekommen.
        turn_id: str = uuid.uuid4().hex

        _user_entitaet_sicherstellen(anfrage.user_id)
        character_id: str = ASSISTANT_USER_ID

        # Shadow Delivery: Aktivität melden + Cooldown zurücksetzen
        redis_client.set(f"last_activity:{anfrage.user_id}", str(time.time()), ex=7200)
        shadow_cooldown_reset(redis_client, anfrage.user_id)

        # ── Pfad 1: HumanGraph (Perzeption → Enricher → EI-Calc → Salienz → Dispatcher) ──
        with llm_lock:
            initial_state: dict = request.app.state.human_graph.create_state(
                user_prompt   = anfrage.prompt,
                user_id       = anfrage.user_id,
                character_id  = character_id,
                system_prompt = anfrage.system,
                temperature   = anfrage.temperatur,
                turn_id       = turn_id,
            )

            result: dict = request.app.state.conversation_graph.invoke(initial_state)

        # ── Event erzeugen — löst CharacterGraph (Pfad 2) im Consumer aus ──
        result_external = result.get("external")
        event_erzeugen(
            redis_client = redis_client,
            user_id      = anfrage.user_id,
            character_id = character_id,
            source       = "user",
            typ          = "message",
            payload      = {
                "turn_id":            turn_id,
                "user_prompt":        anfrage.prompt,
                "current_emotion":    result_external.emotion.emotion              if result_external else "",
                "current_arousal":    result_external.emotion.arousal              if result_external else 0.0,
                "gespraechs_modus":   result_external.emotion.mode                 if result_external else "",
                "intent":             result_external.emotion.intent               if result_external else "",
                "tone":               result_external.emotion.tone                 if result_external else "",
                "sprach_stil":        result_external.emotion.language_style       if result_external else "",
                "beziehungs_dynamik": result_external.emotion.relationship_dynamic if result_external else "",
                "emotions_vektor":    result_external.emotion.emotions_vector      if result_external else "",
                "prompt_thema":       result_external.emotion.prompt_topic         if result_external else "",
            },
        )

        # ── User-Nachricht an andere Clients broadcasten ──
        if anfrage.client_id:
            try:
                user_msg_payload: str = json.dumps({
                    "typ":          "user_message",
                    "nachricht":    anfrage.prompt,
                    "user_id":      anfrage.user_id,
                    "character_id": character_id,
                    "client_id":    anfrage.client_id,
                }, ensure_ascii=False)

                broadcast_threadsafe(
                    user_id=anfrage.user_id,
                    nachricht=user_msg_payload,
                    loop=request.app.state.loop,
                    character_id=character_id,
                    exclude_client=anfrage.client_id,
                )

                logger.debug(
                    f"User-Message Broadcast: '{anfrage.prompt[:60]}' "
                    f"(exclude={anfrage.client_id})"
                )
            except Exception as broadcast_fehler:
                logger.warning(f"User-Message Broadcast fehlgeschlagen: {broadcast_fehler}")

        # Momentum für Shadow Delivery Service
        redis_client.set(f"momentum:{anfrage.user_id}", result.get("momentum", "mid"), ex=300)

        return {
            "status":    "processing",
            "nachricht": "Nachricht empfangen, Charakter-Antwort folgt per WebSocket.",
            "emotion":   result_external.emotion.emotion if result_external else "",
            "arousal":   result_external.emotion.arousal if result_external else 0.0,
        }

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
            character_id: str = ASSISTANT_USER_ID

            # turn_id: korreliert HumanGraph- und CharacterGraph-Spans desselben
            # Konversations-Turns im Pipeline-Log. Analog zu ChatSenden:116 —
            # vor allen Pfaden erzeugt, damit beide Graphen denselben Wert in
            # den State und ins Event-Payload bekommen.
            turn_id: str = uuid.uuid4().hex

            # Shadow Delivery: Aktivität melden + Cooldown zurücksetzen
            redis_client.set(f"last_activity:{anfrage.user_id}", str(time.time()), ex=7200)
            shadow_cooldown_reset(redis_client, anfrage.user_id)

            with llm_lock:
                initial_state: dict = request.app.state.human_graph.create_state(
                    user_prompt   = anfrage.prompt,
                    user_id       = anfrage.user_id,
                    character_id  = character_id,
                    system_prompt = anfrage.system,
                    temperature   = anfrage.temperatur,
                    turn_id       = turn_id,
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

                        node_external = node_state.get("external")
                        node_internal = node_state.get("internal")

                        if node_name == "perzeption":
                            emotion:  str = (node_external.emotion.emotion              if node_external else "").capitalize()
                            arousal: float = node_external.emotion.arousal              if node_external else 0.0
                            modus:    str = (node_external.emotion.mode                 if node_external else "").capitalize()
                            dynamik:  str = (node_external.emotion.relationship_dynamic if node_external else "").capitalize()

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

                        elif node_name == "enricher":
                            hat_kontext: bool = bool(node_state.get("memory_context", ""))
                            modus:       str  = (node_external.emotion.mode    if node_external else "").capitalize()
                            emotion:     str  = (node_external.emotion.emotion if node_external else "").capitalize()
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
                            vektor:         str = node_external.emotion.emotions_vector if node_external else ""
                            stil:           str = node_external.emotion.language_style  if node_external else ""
                            modus_korr:     str = node_external.emotion.mode            if node_external else ""
                            has_bez:       bool = bool(node_external.character.relationship if node_external else "")

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

                        yield _sse_event("stage", {
                            "node":   node_name,
                            "label":  label,
                            "detail": detail,
                        })

                        letzter_state = node_state

            # ── Event erzeugen — löst CharacterGraph (Pfad 2) im Consumer aus ──
            # User-Werte aus state["external"].emotion ins Payload — db_zugriff
            # liest sie dort wieder und befuellt damit external.emotion im CG.
            letzter_external = letzter_state.get("external")
            event_erzeugen(
                redis_client = redis_client,
                user_id      = anfrage.user_id,
                character_id = character_id,
                source       = "user",
                typ          = "message",
                payload      = {
                    "turn_id":            turn_id,
                    "user_prompt":        anfrage.prompt,
                    "current_emotion":    letzter_external.emotion.emotion              if letzter_external else "",
                    "current_arousal":    letzter_external.emotion.arousal              if letzter_external else 0.0,
                    "gespraechs_modus":   letzter_external.emotion.mode                 if letzter_external else "",
                    "intent":             letzter_external.emotion.intent               if letzter_external else "",
                    "tone":               letzter_external.emotion.tone                 if letzter_external else "",
                    "sprach_stil":        letzter_external.emotion.language_style       if letzter_external else "",
                    "beziehungs_dynamik": letzter_external.emotion.relationship_dynamic if letzter_external else "",
                    "emotions_vektor":    letzter_external.emotion.emotions_vector      if letzter_external else "",
                    "prompt_thema":       letzter_external.emotion.prompt_topic         if letzter_external else "",
                },
            )

            # ── User-Nachricht an andere Clients broadcasten ──
            if anfrage.client_id:
                try:
                    user_msg_payload: str = json.dumps({
                        "typ":          "user_message",
                        "nachricht":    anfrage.prompt,
                        "user_id":      anfrage.user_id,
                        "character_id": character_id,
                        "client_id":    anfrage.client_id,
                    }, ensure_ascii=False)

                    broadcast_threadsafe(
                        user_id=anfrage.user_id,
                        nachricht=user_msg_payload,
                        loop=request.app.state.loop,
                        character_id=character_id,
                        exclude_client=anfrage.client_id,
                    )

                    logger.debug(
                        f"User-Message Broadcast: '{anfrage.prompt[:60]}' "
                        f"(exclude={anfrage.client_id})"
                    )
                except Exception as broadcast_fehler:
                    logger.warning(f"User-Message Broadcast fehlgeschlagen: {broadcast_fehler}")

            # Momentum für Shadow Delivery Service
            redis_client.set(
                f"momentum:{letzter_state['user_id']}",
                letzter_state.get("momentum", "mid"),
                ex=300,
            )

            yield _sse_event("processing", {
                "status":    "event_created",
                "nachricht": "Charakter-Antwort folgt per WebSocket.",
                "emotion":   letzter_external.emotion.emotion if letzter_external else "",
                "arousal":   letzter_external.emotion.arousal if letzter_external else 0.0,
            })

        except Exception as fehler:
            logger.error(f"Stream-Fehler: {fehler}")
            yield _sse_event("error", {"fehler": str(fehler)})

    return StreamingResponse(
        event_generator(),
        media_type = "text/event-stream",
        headers    = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
