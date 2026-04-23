"""Event-Queue — Kommunikation zwischen User und Charakter.

Zwei unabhängige Akteure (User und Charakter) kommunizieren über Events
in einer Redis-Queue. Jede User×Charakter-Paarung hat ihre eigene Queue.

Queue-Key: event_queue:{user_id}:{character_id}
"""

import json
import logging
import time
import uuid

import redis

logger = logging.getLogger("ki_server.events")

# ─────────────────────────────────────────────
# Konstanten
# ─────────────────────────────────────────────
MAX_SELF_TRIGGERS: int = 3
EVENT_QUEUE_TTL:   int = 3600   # 1 Stunde — Events verfallen wenn niemand sie verarbeitet


def _queue_key(user_id: str, character_id: str) -> str:
    return f"event_queue:{user_id}:{character_id}"


# ─────────────────────────────────────────────
# Event erzeugen
# ─────────────────────────────────────────────
def event_erzeugen(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    source:       str,
    typ:          str = "message",
    payload:      dict = None,
    trigger_count: int = 0,
) -> str:
    """Erzeugt ein Event und pusht es in die Queue.

    Args:
        redis_client: Redis-Verbindung.
        user_id: User-ID (z.B. "meister").
        character_id: Charakter-ID (z.B. "nova").
        source: Wer das Event ausgelöst hat — "user" oder "character".
        typ: Event-Typ — "message", "continue" oder "awaiting_user".
        payload: Freies Dict mit Kontext für den nächsten Durchlauf.
        trigger_count: Self-Trigger-Zähler. User-Events starten bei 0.

    Returns:
        Die event_id (UUID4 als String).
    """
    event_id: str = str(uuid.uuid4())

    event: dict = {
        "event_id":      event_id,
        "user_id":       user_id,
        "character_id":  character_id,
        "source":        source,
        "typ":           typ,
        "payload":       payload or {},
        "trigger_count": trigger_count,
        "erstellt_am":   time.time(),
    }

    key: str = _queue_key(user_id, character_id)
    redis_client.rpush(key, json.dumps(event, ensure_ascii=False))

    # TTL nur setzen wenn noch keiner existiert (-1 = kein TTL, -2 = Key existiert nicht)
    if redis_client.ttl(key) < 0:
        redis_client.expire(key, EVENT_QUEUE_TTL)

    logger.info(
        f"Event: {typ} erzeugt — {source}, "
        f"user={user_id}, char={character_id}, trigger={trigger_count}"
    )

    return event_id


# ─────────────────────────────────────────────
# Nächstes Event holen
# ─────────────────────────────────────────────
def event_naechstes(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> dict | None:
    """Holt das nächste Event aus der Queue.

    Verwendet lpop (FIFO). Gibt None zurück wenn die Queue leer ist.
    Das Event wird beim Lesen aus der Queue entfernt.

    Returns:
        Event-Dict oder None.
    """
    key: str = _queue_key(user_id, character_id)
    raw = redis_client.lpop(key)

    if raw is None:
        return None

    try:
        event: dict = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as fehler:
        logger.error(f"Event: JSON-Parsing fehlgeschlagen — {fehler}")
        return None

    logger.info(
        f"Event: {event['typ']} gelesen — "
        f"{event['source']}, id={event['event_id'][:8]}"
    )

    return event


# ─────────────────────────────────────────────
# Self-Trigger-Schutz
# ─────────────────────────────────────────────
def event_self_trigger_erlaubt(trigger_count: int) -> bool:
    """Prüft ob ein weiterer Self-Trigger erlaubt ist.

    Args:
        trigger_count: Aktueller Zählerstand.

    Returns:
        True wenn trigger_count < MAX_SELF_TRIGGERS.
    """
    if trigger_count < MAX_SELF_TRIGGERS:
        return True

    logger.warning(
        f"Event: Self-Trigger-Limit erreicht ({trigger_count}/{MAX_SELF_TRIGGERS})"
    )
    return False


# ─────────────────────────────────────────────
# Queue-Monitoring
# ─────────────────────────────────────────────
def event_queue_laenge(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> int:
    """Gibt die Anzahl der wartenden Events zurück."""
    return redis_client.llen(_queue_key(user_id, character_id))


def event_queue_leeren(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> int:
    """Leert die Event-Queue. Gibt die Anzahl gelöschter Events zurück."""
    key: str = _queue_key(user_id, character_id)
    laenge: int = redis_client.llen(key)
    redis_client.delete(key)

    logger.info(
        f"Event: Queue geleert — {laenge} Events entfernt "
        f"({user_id}:{character_id})"
    )

    return laenge
