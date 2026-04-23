"""
Chat-Endpunkte — Synchron und SSE-Streaming.
"""

import json
import logging
import time

from fastapi                    import APIRouter, Request
from fastapi.responses          import JSONResponse, StreamingResponse

from config                     import redis_client, ollama_gpu_client, EMBED_MODEL, POSTGRES_URL, llm_lock, ASSISTANT_USER_ID
from api.models                 import GespraechAnfrage
from services.events            import event_erzeugen
from memory.embedding           import embedding_create
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
            )

            result: dict = request.app.state.conversation_graph.invoke(initial_state)

        # ── Event erzeugen — löst CharacterGraph (Pfad 2) im Consumer aus ──
        event_erzeugen(
            redis_client = redis_client,
            user_id      = anfrage.user_id,
            character_id = character_id,
            source       = "user",
            typ          = "message",
            payload      = {
                "user_prompt":        anfrage.prompt,
                "current_emotion":    result.get("current_emotion", ""),
                "current_arousal":    result.get("current_arousal", 0.0),
                "gespraechs_modus":   result.get("gespraechs_modus", ""),
                "intent":             result.get("intent", ""),
                "tone":               result.get("tone", ""),
                "sprach_stil":        result.get("sprach_stil", ""),
                "beziehungs_dynamik": result.get("beziehungs_dynamik", ""),
            },
        )

        # Momentum für Shadow Delivery Service
        redis_client.set(f"momentum:{anfrage.user_id}", result.get("momentum", "mid"), ex=300)

        return {
            "status":    "processing",
            "nachricht": "Nachricht empfangen, Charakter-Antwort folgt per WebSocket.",
            "emotion":   result.get("current_emotion", ""),
            "arousal":   result.get("current_arousal", 0.0),
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

                        yield _sse_event("stage", {
                            "node":   node_name,
                            "label":  label,
                            "detail": detail,
                        })

                        letzter_state = node_state

            # ── Event erzeugen — löst CharacterGraph (Pfad 2) im Consumer aus ──
            event_erzeugen(
                redis_client = redis_client,
                user_id      = anfrage.user_id,
                character_id = character_id,
                source       = "user",
                typ          = "message",
                payload      = {
                    "user_prompt":        anfrage.prompt,
                    "current_emotion":    letzter_state.get("current_emotion", ""),
                    "current_arousal":    letzter_state.get("current_arousal", 0.0),
                    "gespraechs_modus":   letzter_state.get("gespraechs_modus", ""),
                    "intent":             letzter_state.get("intent", ""),
                    "tone":               letzter_state.get("tone", ""),
                    "sprach_stil":        letzter_state.get("sprach_stil", ""),
                    "beziehungs_dynamik": letzter_state.get("beziehungs_dynamik", ""),
                },
            )

            # Momentum für Shadow Delivery Service
            redis_client.set(
                f"momentum:{letzter_state['user_id']}",
                letzter_state.get("momentum", "mid"),
                ex=300,
            )

            yield _sse_event("processing", {
                "status":    "event_created",
                "nachricht": "Charakter-Antwort folgt per WebSocket.",
                "emotion":   letzter_state.get("current_emotion", ""),
                "arousal":   letzter_state.get("current_arousal", 0.0),
            })

        except Exception as fehler:
            logger.error(f"Stream-Fehler: {fehler}")
            yield _sse_event("error", {"fehler": str(fehler)})

    return StreamingResponse(
        event_generator(),
        media_type = "text/event-stream",
        headers    = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
