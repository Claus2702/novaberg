"""
Chat-Endpunkte — Synchron und SSE-Streaming.
"""

import json
import logging
import time
import uuid
from collections.abc import Iterator
from dataclasses import dataclass

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
            request = EmbedRequest(text=EntitaetenRepository.embed_text_bauen(user_id, zusammenfassung))
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
        # name ist Schema-Pflicht (NOT NULL) — eine leere Zeile ist ein
        # Datendefekt und wird laut gemeldet, nicht still uebersprungen.
        if not name or not name.strip():
            logger.error("Embedding-Repair: Entität id=%s ohne Namen — übersprungen", entitaet_id)
            continue

        try:
            request = EmbedRequest(text=EntitaetenRepository.embed_text_bauen(name, zusammenfassung))
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
@dataclass
class _Pfad1Abbruch:
    """Meldet der Stream-Schleife, dass Pfad 1 abgebrochen ist.

    Kein Weiterwerfen der Ausnahme: Die Schleife muss den Abbruch **sehen**,
    weil das Ereignis danach trotzdem erzeugt wird. Eine durchgereichte
    Ausnahme haette den Generator verlassen und genau das verhindert.
    """

    fehler: BaseException
    text:   str


def _stream_oder_abbruch(graph: object, zustand: dict) -> Iterator[object]:
    """Reicht die Stream-Chunks durch und macht aus einem Abbruch ein Element.

    Vorbedingung: `graph` hat eine `.stream()`-Methode.
    Nachbedingung: Dieselben Chunks wie `graph.stream()`, gefolgt von genau
        einem `_Pfad1Abbruch`, falls die Iteration mit einer Ausnahme endete.
    Fehlerfaelle: Keine — jede Ausnahme wird zum Element und nicht zum Abbruch
        des Aufrufers. Das ist der ganze Zweck.

    Returns:
        Ein Iterator ueber Chunks und hoechstens einen Abbruch-Marker.
    """
    # ── Eingabe-Validierung ─────────────────────
    # Keine: Ein Graph ohne stream() scheitert laut beim ersten Aufruf.

    # ── Verarbeitung ────────────────────────────
    try:
        yield from graph.stream(zustand)
    except Exception as fehler:
        # Der Traceback wird HIER geschrieben, im aktiven Ausnahmekontext. Beim
        # Aufrufer ist die Ausnahme nur noch ein Wert; ein `logger.exception`
        # oder ein `exc_info=` dort haette keinen Kontext mehr, auf den es sich
        # beziehen koennte.
        logger.exception(
            f"{type(fehler).__name__}: Pfad 1 abgebrochen — die Schleife "
            f"bekommt einen Abbruch-Marker, damit das Ereignis trotzdem "
            f"erzeugt wird"
        )
        yield _Pfad1Abbruch(fehler, f"{type(fehler).__name__}: {fehler}")


def _ereignis_nutzlast(
    turn_id:      str,
    empfangen_am: float,
    user_prompt:  str,
    zustand:      dict,
    ausfall:      str = "",
) -> dict:
    """Baut die Nutzlast des Ereignisses, das den CharacterGraph ausloest.

    **Eine Stelle fuer beide Endpunkte und fuer beide Ausgaenge.** Der
    synchrone und der streamende Pfad bauten dieselbe Nutzlast zweimal; eine
    dritte Kopie fuer den Ausfallweg waere die Stelle gewesen, an der die drei
    auseinanderlaufen.

    `ausfall` traegt die Ausnahme, an der Pfad 1 abgebrochen ist — leer, wenn
    er durchgelaufen ist. **Das Feld ist der Unterschied zwischen einem
    gemessenen Neutralzustand und einem Ausfall:** `db_zugriff` fuellt fehlende
    Perzeptionsfelder mit den Defaults der Datenklasse (`neutral`, 0.5,
    `alltag`), und ohne diesen Vermerk waere ein Zusammenbruch von einer
    ruhigen Nutzeraeusserung nicht zu unterscheiden.

    Vorbedingung: `zustand` ist der State nach Pfad 1 — bei einem Abbruch der
        zuletzt erreichte, notfalls der Eingangs-State.
    Nachbedingung: Ein flaches, JSON-serialisierbares Dict.
    Fehlerfaelle: Keine. Fehlt `external`, stehen leere Werte statt erfundener;
        das Feld `pfad1_ausfall` sagt dann, warum.

    Returns:
        Die Nutzlast.
    """
    # ── Eingabe-Validierung ─────────────────────
    aussen = zustand.get("external")

    # ── Verarbeitung ────────────────────────────
    nutzlast: dict = {
        "turn_id":     turn_id,
        # Der Zeitpunkt, zu dem die Aeusserung eintraf — genommen vor jeder
        # Verarbeitung. **Nicht** `erstellt_am`: Das Ereignis entsteht erst
        # nach Pfad 1, also 11 bis 13 Sekunden spaeter, und die zweite
        # Nachricht wartet in dieser Zeit am `llm_lock`. Wer Abstaende auf
        # `erstellt_am` rechnet, misst die Traegheit des Systems mit.
        "empfangen_am": empfangen_am,
        "user_prompt": user_prompt,
        # Die Salienz dieses Reizes reist mit in den CharacterGraph. Dort
        # multipliziert die Formel sie mit nutzer_gewichtung und erhaelt daraus
        # den Boden fuer Novas Segmente (novaberg-salienz-berechnung_k.md §3).
        # None heisst "nicht ermittelt" und ist von einer echten 0.0 zu
        # unterscheiden.
        "salienz_human":      zustand.get("salienz_human"),
        # Die Intentionen desselben Reizes, Quelle von M1 der Initiative-Achse.
        # Sie muessen mitreisen: Der Salienz-Node des CharacterGraph laeuft NACH
        # dem GV-Node und kaeme zu spaet.
        "user_intentionen":   zustand.get("user_intentionen", []),
        "current_emotion":    aussen.emotion.emotion              if aussen else "",
        "current_arousal":    aussen.emotion.arousal              if aussen else 0.0,
        "gespraechs_modus":   aussen.emotion.mode                 if aussen else "",
        "intent":             aussen.emotion.intent               if aussen else "",
        "tone":               aussen.emotion.tone                 if aussen else "",
        "sprach_stil":        aussen.emotion.language_style       if aussen else "",
        "beziehungs_dynamik": aussen.emotion.relationship_dynamic if aussen else "",
        "emotions_vektor":    aussen.emotion.emotions_vector      if aussen else "",
        "prompt_thema":       aussen.emotion.prompt_topic         if aussen else "",
    }
    if ausfall:
        nutzlast["pfad1_ausfall"] = ausfall

    # ── Ausgabe-Verifikation ────────────────────
    return nutzlast


def _bestaetigungs_nutzlast(turn_id: str, zustand: dict) -> dict:
    """Baut die Bestaetigung, die Pfad 1 dem Client zurueckgibt.

    **Eine Stelle fuer beide Endpunkte**, aus demselben Grund wie bei
    `_ereignis_nutzlast`: Der synchrone und der streamende Pfad bauten dieselbe
    Bestaetigung zweimal.

    Sie traegt die `turn_id`. Ohne sie hat der Client nichts, wogegen er eine
    ankommende Antwort halten koennte — er ordnet sie dann der letzten
    Nachricht zu, und nach einem ausgefallenen Turn verschiebt sich alles um
    eins (novaberg-bugs.md -> ANTWORT-OHNE-ZUORDNUNG). Die Zuordnung in der
    Antwort allein reicht nicht: Sie braucht eine Gegenprobe auf der Seite, die
    die Frage gestellt hat.

    Vorbedingung: `turn_id` ist die Kennung, die derselbe Aufruf ins Ereignis
        geschrieben hat. Eine zweite Kennung waere keine Zuordnung, sondern
        eine zweite Auskunft.
    Nachbedingung: Ein flaches, JSON-serialisierbares Dict.
    Fehlerfaelle: Keine. Fehlt `external`, stehen leere Werte statt erfundener.

    Returns:
        Die Bestaetigung.
    """
    # ── Eingabe-Validierung ─────────────────────
    aussen = zustand.get("external")

    # ── Verarbeitung ────────────────────────────
    nutzlast: dict = {
        "status":    "processing",
        "nachricht": "Nachricht empfangen, Charakter-Antwort folgt per WebSocket.",
        "turn_id":   turn_id,
        "emotion":   aussen.emotion.emotion if aussen else "",
        "arousal":   aussen.emotion.arousal if aussen else 0.0,
    }

    # ── Ausgabe-Verifikation ────────────────────
    if not nutzlast["turn_id"]:
        logger.error(
            f"Bestaetigung ohne turn_id — der Client kann die Antwort auf "
            f"diese Nachricht nicht zuordnen (Felder: {sorted(nutzlast)})"
        )

    return nutzlast


@router.post("/chat")
def ChatSenden(anfrage: GespraechAnfrage, request: Request):
    """Prompt durch den Gesprächsgraphen verarbeiten."""
    try:
        # Der Empfang, als erste Anweisung. Er ist die einzige Groesse, die den
        # Abstand zwischen zwei Nutzeraeusserungen misst — jede spaetere Uhr
        # traegt die Dauer von Pfad 1 und die Wartezeit am `llm_lock` mit.
        empfangen_am: float = time.time()

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
        initial_state: dict = request.app.state.human_graph.create_state(
            user_prompt   = anfrage.prompt,
            user_id       = anfrage.user_id,
            character_id  = character_id,
            system_prompt = anfrage.system,
            temperature   = anfrage.temperatur,
            turn_id       = turn_id,
        )

        # **Ein Abbruch in Pfad 1 darf die Nutzeraeusserung nicht loeschen.**
        # Das Ereignis unten ist der einzige Ausloeser des CharacterGraph; wird
        # es nicht erzeugt, gibt es keine Antwort — nicht spaeter, sondern nie,
        # und ohne Weg zur Wiederholung. Genau so ging am 30.07.2026 ein Turn
        # verloren, weil ein Modellaufruf sechs Millisekunden nach dem Timeout
        # zurueckkam (novaberg-bugs.md → PFAD1-TIMEOUT-TURNVERLUST).
        #
        # Was hier NICHT passiert: den Ausfall verschweigen. Der Vermerk reist
        # mit, und `db_zugriff` meldet ihn laut.
        pfad1_ausfall: str = ""
        result: dict = initial_state
        try:
            with llm_lock:
                result = request.app.state.conversation_graph.invoke(initial_state)
        except Exception as fehler:
            pfad1_ausfall = f"{type(fehler).__name__}: {fehler}"
            logger.exception(
                f"{type(fehler).__name__}: Pfad 1 abgebrochen — das Ereignis "
                f"wird trotzdem erzeugt, damit der Turn nicht verlorengeht "
                f"(turn_id={turn_id})"
            )

        # ── Event erzeugen — löst CharacterGraph (Pfad 2) im Consumer aus ──
        event_erzeugen(
            redis_client = redis_client,
            user_id      = anfrage.user_id,
            character_id = character_id,
            source       = "user",
            typ          = "message",
            payload      = _ereignis_nutzlast(
                turn_id, empfangen_am, anfrage.prompt, result, pfad1_ausfall,
            ),
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

        return _bestaetigungs_nutzlast(turn_id, result)

    except Exception as fehler:
        # Den Typ nennen, nicht nur str(fehler): Die haeufigste Exception auf
        # diesem Pfad ist concurrent.futures.TimeoutError aus submit_sync
        # (60 s Default, greift wenn der Modell-Worker noch am vorigen Turn
        # haengt) — und deren str() ist LEER. Die Zeile lautete dann
        # "Graph-Fehler: " und benannte nichts; der Client bekam ein
        # "Verarbeitungsfehler: " ohne Grund. Gemessen 29.07.2026 bei zwei
        # von fuenf Turns einer Messreihe ohne Pause.
        typ: str = type(fehler).__name__
        text: str = str(fehler) or "(Exception ohne Meldung)"
        logger.error(f"Graph-Fehler [{typ}]: {text}", exc_info=True)
        return JSONResponse(
            status_code = 503,
            content     = {"fehler": f"Verarbeitungsfehler [{typ}]: {text}"},
        )


# ─────────────────────────────────────────────
# SSE-Streaming Chat
# ─────────────────────────────────────────────
@router.post("/chat/stream")
def ChatStreamSenden(anfrage: GespraechAnfrage, request: Request):
    """Prompt mit Stage-Updates via SSE."""
    # Der Empfang, als erste Anweisung — vor der Entitaetspruefung und vor dem
    # Generator, der erst laeuft, wenn der Client zu lesen beginnt. Er misst
    # den Abstand zwischen zwei Nutzeraeusserungen; jede spaetere Uhr traegt
    # die Dauer von Pfad 1 und die Wartezeit am `llm_lock` mit.
    empfangen_am: float = time.time()

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
                pfad1_ausfall: str = ""

                for chunk in _stream_oder_abbruch(
                    request.app.state.conversation_graph, initial_state,
                ):
                    if isinstance(chunk, _Pfad1Abbruch):
                        pfad1_ausfall = chunk.text
                        logger.error(
                            f"Pfad 1 abgebrochen ({chunk.text}) — das Ereignis "
                            f"wird trotzdem erzeugt, damit der Turn nicht "
                            f"verlorengeht (turn_id={turn_id})"
                        )
                        yield _sse_event("stage", {
                            "label":  "Wahrnehmung unvollständig",
                            "detail": "Die Antwort folgt über den anderen Kanal.",
                        })
                        break
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
            # Dieselbe Nutzlast wie im synchronen Pfad, aus derselben Funktion:
            # db_zugriff liest die Perzeptionswerte dort wieder und befuellt
            # damit external.emotion im CharacterGraph.
            event_erzeugen(
                redis_client = redis_client,
                user_id      = anfrage.user_id,
                character_id = character_id,
                source       = "user",
                typ          = "message",
                payload      = _ereignis_nutzlast(
                    turn_id, empfangen_am, anfrage.prompt, letzter_state,
                    pfad1_ausfall,
                ),
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

            yield _sse_event(
                "processing", _bestaetigungs_nutzlast(turn_id, letzter_state),
            )

        except Exception as fehler:
            logger.exception(f"{type(fehler).__name__}: Stream-Fehler")
            yield _sse_event("error", {"fehler": str(fehler)})

    return StreamingResponse(
        event_generator(),
        media_type = "text/event-stream",
        headers    = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
