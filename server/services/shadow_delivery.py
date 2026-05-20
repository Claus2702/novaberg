"""
Shadow Delivery Service — Novas eigenständige Stimme.

Prüft periodisch ob Nova etwas einbringen kann:
  1. Momentum "low" nach einem Request → kurze Pause → Delivery
  2. Timeout (30s+ Inaktivität) → proaktive Nachricht

Wählt den thematisch passendsten Stack-Eintrag per Cosine Similarity.
Pusht über WebSocket als eigene Chat-Nachricht.

Flood-Schutz:
  - Thematischer Cooldown: Anderes Thema → wartet auf User-Aktion
  - Burst-Limit: Max 3 aufeinanderfolgende Impulse ohne User-Reaktion
"""

import asyncio
import json
import logging
import time
from datetime import datetime

import numpy as np
import redis

from api.websocket import broadcast
from config         import ASSISTANT_NAME, ASSISTANT_USER_ID, shutdown_event
from memory.session import session_turns_retrieve, session_turn_store
from services.llm_provider import get_chat_provider
from services.model_services import model_service, EmbedRequest

logger = logging.getLogger("ki_server.shadow_delivery")

# ─────────────────────────────────────────────
# Konstanten
# ─────────────────────────────────────────────
PRÜF_INTERVALL:       float = 5.0     # Sekunden zwischen Prüfungen
MOMENTUM_PAUSE:       float = 3.0     # Pause nach Momentum-Low bevor Delivery
INAKTIVITAET_GRENZE:  float = 30.0    # Sekunden ohne User-Aktion → Timeout-Trigger
SIMILARITY_THRESHOLD: float = 0.40    # Minimum für thematischen Match
MAX_BURST:            int   = 2       # Max aufeinanderfolgende Impulse
COOLDOWN_TTL:         int   = 3600    # Cooldown-Key TTL in Sekunden

# ─────────────────────────────────────────────
# Delivery-Prompt: Wie Nova formuliert
# ─────────────────────────────────────────────
DELIVERY_SYSTEM_PROMPT: str = f"""Du bist {ASSISTANT_NAME}. Antworte auf Deutsch.
Du teilst dem Nutzer einen eigenen Gedanken mit — eine eigenständige Nachricht,
nicht als Antwort auf eine Frage.
- Schreibe direkt an den Nutzer, nicht über ihn
- 2-4 Sätze, wie eine Chat-Nachricht
- Variiere deine Einstiege — beginne NIEMALS zwei Nachrichten gleich"""


# ─────────────────────────────────────────────
# Cosine Similarity
# ─────────────────────────────────────────────
def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Berechnet die Cosine Similarity zwischen zwei Vektoren."""

    if not vec_a or not vec_b:
        return 0.0

    a: np.ndarray = np.array(vec_a)
    b: np.ndarray = np.array(vec_b)

    dot:    float = np.dot(a, b)
    norm_a: float = np.linalg.norm(a)
    norm_b: float = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot / (norm_a * norm_b))


# ─────────────────────────────────────────────
# Emotionale Kompatibilität prüfen
# ─────────────────────────────────────────────
NEGATIVE_EMOTIONEN: set = {"frustration", "aerger", "traurigkeit", "unsicherheit"}

def _emotional_kompatibel(
    stack_aufgabe: str,
    user_emotion:  str,
) -> bool:
    """Prüft ob ein Impuls zur aktuellen User-Emotion passt."""

    # Bei Stress: Grundsätzlich nichts einbringen
    if user_emotion == "stress":
        return False

    # Negative Emotionen: Nur empathische Nachfragen erlaubt
    if user_emotion in NEGATIVE_EMOTIONEN:
        return stack_aufgabe == "nachfragen"

    # Nachdenklich: Kein Humor
    if user_emotion == "nachdenklich" and stack_aufgabe == "humor":
        return False

    # Alle anderen Kombinationen: Erlaubt
    return True


def _modus_kompatibel(
    stack_modus:     str,
    gespraechs_modus: str,
) -> float:
    """
    Berechnet einen Kompatibilitäts-Score (0.0-1.0) zwischen
    Stack-Modus und aktuellem Gesprächsmodus.
    """

    if not stack_modus or not gespraechs_modus:
        return 0.5  # Unbekannt → neutral

    # Gleicher Modus = perfekt
    if stack_modus == gespraechs_modus:
        return 1.0

    # Kompatibilitäts-Gruppen
    KOMPATIBEL: dict[str, set] = {
        "fachgespraech":           {"lernmodus", "beratend", "berichtend"},
        "philosophischer_austausch": {"kreativ", "emotional"},
        "alltag":                  {"spielerisch", "emotional"},
        "arbeitsmodus":            {"beratend", "berichtend", "fachgespraech"},
        "emotional":               {"philosophischer_austausch", "alltag"},
        "spielerisch":             {"alltag", "kreativ"},
        "lernmodus":               {"fachgespraech", "beratend"},
        "kreativ":                 {"philosophischer_austausch", "spielerisch"},
        "beratend":                {"fachgespraech", "arbeitsmodus", "lernmodus"},
        "berichtend":              {"arbeitsmodus", "fachgespraech"},
    }

    kompatible: set = KOMPATIBEL.get(gespraechs_modus, set())

    if stack_modus in kompatible:
        return 0.7

    return 0.3  # Inkompatibel aber nicht verboten


# ─────────────────────────────────────────────
# Gesprächs-Embedding berechnen
# ─────────────────────────────────────────────
async def _gespraechs_embedding(
    redis_client:  redis.Redis,
    user_id:       str,
    character_id:  str = "",
) -> list[float]:
    """Berechnet ein Embedding aus den letzten Session-Turns."""

    turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id or ASSISTANT_USER_ID)

    if not turns:
        return []

    # Letzte 5 Turns konkatenieren
    letzte_turns: list[dict] = turns[-5:]
    kontext: str = " ".join(turn.get("inhalt", "") for turn in letzte_turns)

    if not kontext.strip():
        return []

    embed_response = await model_service.embed.submit(EmbedRequest(text=kontext))
    embedding: list[float] = embed_response.embedding
    logger.debug(
        "Shadow-Delivery: Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
        len(embedding),
        embed_response.duration_seconds,
    )
    return embedding


# ─────────────────────────────────────────────
# Besten Stack-Eintrag finden (semantisch)
# ─────────────────────────────────────────────
def _besten_eintrag_finden(
    redis_client:      redis.Redis,
    user_id:           str,
    gespraechs_vector: list[float],
    user_emotion:      str = "neutral",
    gespraechs_modus:  str = "",
) -> tuple[dict | None, int]:
    """
    Durchsucht den Stack nach dem thematisch und emotional passendsten Eintrag.
    Gibt (eintrag, index) zurück oder (None, -1) wenn nichts passt.
    """

    raw_list: list = redis_client.lrange(f"shadow_stack:{user_id}", 0, -1)

    if not raw_list:
        return None, -1

    bester_eintrag: dict | None = None
    bester_index:   int         = -1
    bester_score:   float       = 0.0

    for idx, raw in enumerate(raw_list):
        try:
            eintrag: dict = json.loads(raw)
        except json.JSONDecodeError:
            continue

        # Filter 1: Emotionale Kompatibilität (harter Filter)
        stack_aufgabe: str = eintrag.get("aufgabe", "")

        if not _emotional_kompatibel(stack_aufgabe, user_emotion):
            logger.debug(
                f"Delivery: '{eintrag.get('thema', '')[:30]}' emotional inkompatibel "
                f"(aufgabe={stack_aufgabe}, user_emotion={user_emotion})"
            )
            continue

        # Filter 2: Thematische Similarity
        embedding: list[float] = eintrag.get("embedding", [])

        if not embedding:
            thema_sim: float = SIMILARITY_THRESHOLD
        else:
            thema_sim = _cosine_similarity(gespraechs_vector, embedding)

        if thema_sim < SIMILARITY_THRESHOLD:
            continue

        # Filter 3: Modus-Kompatibilität (weicher Score)
        stack_modus: str   = eintrag.get("modus", "")
        modus_score: float = _modus_kompatibel(stack_modus, gespraechs_modus)

        # Gewichteter Gesamt-Score: 70% Thema + 30% Modus
        gesamt_score: float = (thema_sim * 0.7) + (modus_score * 0.3)

        if gesamt_score > bester_score:
            bester_score   = gesamt_score
            bester_eintrag = eintrag
            bester_index   = idx

    if bester_eintrag is None:
        logger.debug("Delivery: Kein kompatibler Eintrag gefunden")
        return None, -1

    logger.info(
        f"Delivery: Bester Match '{bester_eintrag.get('thema', '')[:40]}' "
        f"(score={bester_score:.2f}, idx={bester_index})"
    )

    return bester_eintrag, bester_index


# ─────────────────────────────────────────────
# Stack-Eintrag per Index entfernen
# ─────────────────────────────────────────────
def _stack_eintrag_entfernen(
    redis_client: redis.Redis,
    user_id:      str,
    index:        int,
) -> None:
    """Entfernt einen spezifischen Eintrag per Index vom Stack."""

    stack_key: str = f"shadow_stack:{user_id}"
    tombstone: str = "__REMOVED__"

    # Markieren + Aufräumen (Redis hat kein LREMOVE by index)
    redis_client.lset(stack_key, index, tombstone)
    redis_client.lrem(stack_key, 1, tombstone)

    logger.debug(f"Delivery: Stack-Eintrag {index} entfernt.")


# ─────────────────────────────────────────────
# Stack-Eintrag nach Ähnlichkeit entfernen
# ─────────────────────────────────────────────
def _stack_aehnliche_entfernen(
    redis_client:    redis.Redis,
    user_id:         str,
    referenz_vector: list[float],
    threshold:       float = 0.65,
) -> None:
    """Entfernt Stack-Einträge die dem gerade gesendeten zu ähnlich sind."""

    if not referenz_vector:
        return

    stack_key: str = f"shadow_stack:{user_id}"
    raw_list:  list = redis_client.lrange(stack_key, 0, -1)

    entfernt: int = 0

    for raw in raw_list:
        try:
            eintrag:   dict         = json.loads(raw)
            embedding: list[float]  = eintrag.get("embedding", [])

            if embedding and _cosine_similarity(referenz_vector, embedding) >= threshold:
                redis_client.lrem(stack_key, 1, raw)
                entfernt += 1
                logger.info(
                    f"Delivery: Duplikat entfernt — '{eintrag.get('thema', '')[:40]}'"
                )
        except json.JSONDecodeError:
            continue

    if entfernt:
        logger.info(f"Delivery: {entfernt} ähnliche Einträge bereinigt.")


# ─────────────────────────────────────────────
# Zeitlichen Kontext berechnen
# ─────────────────────────────────────────────
def _zeitlicher_kontext(erstellt: str) -> str:
    """Berechnet eine natürliche Zeitangabe aus dem Erstelldatum."""

    try:
        erstelldatum: datetime = datetime.fromisoformat(erstellt)
        differenz = datetime.now() - erstelldatum
        stunden: float = differenz.total_seconds() / 3600

        if stunden < 1:
            return "Dieses Thema kam gerade eben im Gespräch auf."
        elif stunden < 24:
            return "Dieses Thema kam heute im Gespräch auf."
        elif stunden < 48:
            return "Dieses Thema kam gestern im Gespräch auf."
        else:
            tage: int = int(differenz.days)
            return f"Dieses Thema kam vor {tage} Tagen im Gespräch auf."

    except (ValueError, TypeError):
        return "Dieses Thema kam kürzlich im Gespräch auf."


# ─────────────────────────────────────────────
# Cooldown-Verwaltung
# ─────────────────────────────────────────────
def _cooldown_aktiv(redis_client: redis.Redis, user_id: str) -> bool:
    """Prüft ob der thematische Cooldown aktiv ist."""

    return redis_client.exists(f"shadow_cooldown:{user_id}") == 1


def _cooldown_setzen(redis_client: redis.Redis, user_id: str) -> None:
    """Setzt den Cooldown — wird durch nächste User-Aktion gelöscht."""

    redis_client.set(f"shadow_cooldown:{user_id}", "1", ex=COOLDOWN_TTL)


def shadow_cooldown_reset(redis_client: redis.Redis, user_id: str) -> None:
    """
    Löscht Cooldown und Burst-Counter.
    Wird bei jeder User-Nachricht aufgerufen (aus dem Chat-Endpoint).
    """

    redis_client.delete(f"shadow_cooldown:{user_id}")
    redis_client.delete(f"shadow_burst_count:{user_id}")
    logger.debug(f"Delivery: Cooldown + Burst reset für '{user_id}'")


# ─────────────────────────────────────────────
# Burst-Verwaltung
# ─────────────────────────────────────────────
def _burst_erlaubt(redis_client: redis.Redis, user_id: str) -> bool:
    """Prüft ob der Burst-Limit noch nicht erreicht ist."""

    count: str | None = redis_client.get(f"shadow_burst_count:{user_id}")

    if not count:
        return True

    return int(count) < MAX_BURST


def _burst_erhoehen(redis_client: redis.Redis, user_id: str) -> None:
    """Erhöht den Burst-Counter."""

    key: str = f"shadow_burst_count:{user_id}"

    redis_client.incr(key)
    redis_client.expire(key, COOLDOWN_TTL)


# ─────────────────────────────────────────────
# Delivery formulieren (GPU-Modell)
# ─────────────────────────────────────────────
def _delivery_formulieren(eintrag: dict) -> str:
    """Lässt Nova den Impuls als natürliche Chat-Nachricht formulieren."""

    thema:    str = eintrag.get("thema", "")
    inhalt:   str = eintrag.get("inhalt", "")[:500]
    erstellt: str = eintrag.get("erstellt", "")
    aufgabe:  str = eintrag.get("aufgabe", "")

    zeit_kontext: str = _zeitlicher_kontext(erstellt)

    # Einleitungshilfe je nach Situation
    einleitung_hinweis: str = ""
    if aufgabe == "nachfragen":
        einleitung_hinweis = (
            "Du möchtest eine einfühlsame Nachfrage stellen. "
            "Zeige echtes Interesse, sei nicht aufdringlich."
        )
    elif aufgabe == "recherche":
        einleitung_hinweis = (
            "Du hast im Hintergrund über ein Thema nachgedacht "
            "und möchtest deine Erkenntnis teilen."
        )
    elif aufgabe == "vertiefen":
        einleitung_hinweis = (
            "Du hast ein bekanntes Thema vertieft "
            "und möchtest neue Einsichten teilen."
        )
    elif aufgabe == "wiedervorlage":
        einleitung_hinweis = (
            "Du erinnerst den Nutzer an etwas, das zur Wiedervorlage "
            "markiert wurde. Sei freundlich und hilfreich."
        )

    prompt: str = (
        f"{zeit_kontext}\n"
        f"{einleitung_hinweis}\n\n"
        f"Thema: {thema}\n"
        f"Deine Erkenntnis: {inhalt}\n\n"
        f"Formuliere daraus eine kurze, natürliche Chat-Nachricht an den Nutzer."
    )

    try:
        provider = get_chat_provider()
        antwort = provider.chat(
            messages = [
                {"role": "user", "content": prompt},
            ],
            system      = DELIVERY_SYSTEM_PROMPT,
            temperature = 0.6,
            caller      = "shadow/delivery",
        )

        return antwort.content.strip()

    except Exception as fehler:
        logger.error(f"Delivery: Formulierung fehlgeschlagen — {fehler}")
        return ""


# ─────────────────────────────────────────────
# Delivery ausführen (eine einzelne Nachricht)
# ─────────────────────────────────────────────
async def _delivery_ausfuehren(
    redis_client:  redis.Redis,
    user_id:       str,
    websocket_map: dict,
    compiled_agent_graph = None,
    agent_graph          = None,
) -> bool:
    """
    Führt eine einzelne Delivery aus:
    1. Gesprächs-Embedding berechnen
    2. Besten Stack-Eintrag finden
    3. Formulieren lassen
    4. Über WebSocket senden
    5. Als Session-Turn speichern

    Gibt True zurück wenn eine Nachricht gesendet wurde.
    """

    # Gesprächskontext als Embedding
    gespraechs_vector: list[float] = await _gespraechs_embedding(
        redis_client, user_id, ASSISTANT_USER_ID,
    )

    if not gespraechs_vector:
        logger.debug("Delivery: Kein Gesprächskontext — überspringe")
        return False

    # Aktuelle Emotion und Modus aus letzten Turns
    turns: list[dict] = session_turns_retrieve(redis_client, user_id, ASSISTANT_USER_ID)
    user_emotion:     str = "neutral"
    gespraechs_modus: str = ""

    for turn in reversed(turns):
        if turn.get("rolle") == "user" and turn.get("emotion"):
            user_emotion     = turn["emotion"]
            gespraechs_modus = turn.get("modus", "")
            break

    # Besten Eintrag finden (thematisch + emotional + modus)
    eintrag, index = _besten_eintrag_finden(
        redis_client, user_id, gespraechs_vector,
        user_emotion, gespraechs_modus,
    )

    if eintrag is None:
        return False

    # Formulieren
    nachricht: str = _delivery_formulieren(eintrag)

    if not nachricht:
        return False

    # Über WebSocket an alle Clients senden
    if not websocket_map.get(user_id):
        logger.warning(f"Delivery: Kein WebSocket für '{user_id}' — Nachricht verworfen")
        return False

    impuls_payload: str = json.dumps({
        "typ":       "shadow_impuls",
        "nachricht": nachricht,
        "thema":     eintrag.get("thema", ""),
        "aufgabe":   eintrag.get("aufgabe", ""),
    }, ensure_ascii=False)

    await broadcast(user_id, impuls_payload, character_id=ASSISTANT_USER_ID)

    logger.info(
        f"Delivery: Nachricht gesendet — '{eintrag.get('thema', '')[:40]}' "
        f"({len(websocket_map.get(user_id, []))} Clients)"
    )

    # Vom Stack entfernen (erst NACH erfolgreichem Senden)
    _stack_eintrag_entfernen(redis_client, user_id, index)

     # Deduplizierung: Ähnliche Einträge gleich mit entfernen
    _stack_aehnliche_entfernen(
        redis_client, user_id,
        eintrag.get("embedding", []),
    )

    # Als Session-Turn speichern (markiert als Shadow-Impuls)
    session_turn_store(
        redis_client, user_id, ASSISTANT_USER_ID, "assistant", nachricht,
        intentionen = ["eigener_impuls"],
        emotion     = eintrag.get("emotion", ""),
        modus       = eintrag.get("modus", ""),
        kern        = f"[Nova-Impuls] Thema: {eintrag.get('thema', '')}",
    )

   # AgentGraph: Salienz-Analyse + Dispatcher für Novas eigene Impulse
    logger.info(f"Delivery: AgentGraph-Check — compiled={compiled_agent_graph is not None}, instance={agent_graph is not None}")

    if compiled_agent_graph and agent_graph:
        try:
            logger.info(
                f"Delivery: AgentGraph — erzeuge State fuer user='{user_id}', "
                f"character='{ASSISTANT_USER_ID}', rolle='character'"
            )
            agent_state = agent_graph.create_state(
                user_prompt    = nachricht,
                user_id        = user_id,
                character_id   = ASSISTANT_USER_ID,
                ei_calc_rolle  = "character",
            )
            logger.info(f"Delivery: AgentGraph — State erzeugt, starte invoke...")
            compiled_agent_graph.invoke(agent_state)
            logger.info(f"Delivery: AgentGraph — Analyse abgeschlossen für '{eintrag.get('thema', '')[:40]}'")
        except Exception as agent_fehler:
            logger.error(f"Delivery: AgentGraph-Fehler — {type(agent_fehler).__name__}: {agent_fehler}", exc_info=True)
    else:
        logger.warning("Delivery: AgentGraph NICHT verfügbar — übersprungen")

    # Burst-Counter erhöhen
    _burst_erhoehen(redis_client, user_id)

    return True


# ─────────────────────────────────────────────
# Haupt-Loop: Prüft periodisch alle User
# ─────────────────────────────────────────────
async def shadow_delivery_loop(
    redis_client:  redis.Redis,
    websocket_map: dict,
    llm_lock,
    compiled_agent_graph = None,
    agent_graph          = None,
) -> None:
    """
    Endlos-Loop, läuft als asyncio-Task.
    Prüft alle 5 Sekunden ob Delivery-Bedingungen erfüllt sind.
    """

    logger.info("Shadow Delivery Service gestartet.")

    while True:
        try:
            await asyncio.sleep(PRÜF_INTERVALL)

            if shutdown_event.is_set():
                logger.info("Shadow Delivery: Shutdown erkannt — beende Loop")
                break

            # Alle User mit aktiven WebSocket-Verbindungen prüfen
            for user_id in list(websocket_map.keys()):

                # ── Prüfung 1: Burst-Limit ────────
                if not _burst_erlaubt(redis_client, user_id):
                    continue

                # ── Prüfung 2: Stack leer? ────────
                stack_laenge: int = redis_client.llen(f"shadow_stack:{user_id}")

                if stack_laenge == 0:
                    continue

                # ── Prüfung 3: Trigger ermitteln ──
                momentum: str | None = redis_client.get(f"momentum:{user_id}")
                last_raw: str | None = redis_client.get(f"last_activity:{user_id}")

                if isinstance(momentum, bytes):
                    momentum = momentum.decode()
                if isinstance(last_raw, bytes):
                    last_raw = last_raw.decode()

                trigger: str = ""

                # Trigger 1: Momentum low
                if momentum == "low":
                    # Cooldown prüfen
                    if _cooldown_aktiv(redis_client, user_id):
                        continue

                    trigger = "momentum_low"

                    # Momentum verbrauchen (nicht nochmal triggern)
                    redis_client.delete(f"momentum:{user_id}")

                    # Kurze Pause für natürliches Timing
                    await asyncio.sleep(MOMENTUM_PAUSE)

                # Trigger 2: Timeout (Inaktivität)
                elif last_raw:
                    try:
                        letzte_aktivitaet: float = float(last_raw)
                        inaktiv_seit:      float = time.time() - letzte_aktivitaet

                        if inaktiv_seit >= INAKTIVITAET_GRENZE:
                            # Nicht feuern wenn noch kein Gespräch läuft
                            turns: list = session_turns_retrieve(redis_client, user_id, ASSISTANT_USER_ID)
                            if not turns:
                                continue

                            # Cooldown prüfen
                            if _cooldown_aktiv(redis_client, user_id):
                                continue

                            trigger = "timeout"

                            # Timeout verbrauchen (last_activity aktualisieren)
                            redis_client.set(
                                f"last_activity:{user_id}",
                                str(time.time()),
                                ex=7200,
                            )

                    except (ValueError, TypeError):
                        continue
                else:
                    continue

                if not trigger:
                    continue

                logger.info(f"Delivery: Trigger '{trigger}' für '{user_id}'")

                # ── LLM-Lock prüfen (GPU-Modell nicht blockieren) ──
                acquired: bool = llm_lock.acquire(blocking=False)

                if not acquired:
                    logger.debug("Delivery: LLM belegt — verschiebe auf nächsten Zyklus")
                    continue

                try:
                    gesendet: bool = await _delivery_ausfuehren(
                        redis_client, user_id, websocket_map,
                        compiled_agent_graph, agent_graph,
                    )

                    if gesendet:
                        # Cooldown setzen — wird durch nächste User-Aktion gelöscht
                        _cooldown_setzen(redis_client, user_id)

                        # Prüfe ob thematische Fortsetzung möglich
                        # (nächster Zyklus wird das über Similarity entscheiden)
                        logger.info(f"Delivery: Erfolgreich für '{user_id}' (trigger={trigger})")

                finally:
                    llm_lock.release()

        except asyncio.CancelledError:
            logger.info("Shadow Delivery Service beendet.")
            break

        except Exception as fehler:
            logger.error(f"Delivery-Loop: Unerwarteter Fehler — {fehler}")
            await asyncio.sleep(PRÜF_INTERVALL)
