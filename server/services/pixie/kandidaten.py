"""Kandidaten-Sammlung fuer Pixie-Heartbeat.

Zwei Quellen:
  1. Queue-Peek: shadow_queue:{user_id} + queue:{user_id}
  2. Faellige periodische Aufgaben: pixie:schedule:*
"""

import json
import logging
import time

from config import redis_client

logger = logging.getLogger("ki_server.pixie")


def kandidaten_sammeln() -> list[dict]:
    """Sammelt Kandidaten aus Queue-Peek und faelligen periodischen Aufgaben.

    Rueckgabe: Liste von Kandidaten-Dicts mit:
        - name: str
        - prioritaet: float
        - quelle: "queue" | "periodisch"
        - daten: dict
        - queue_key: str | None
        - queue_raw: bytes | None (fuer exaktes LREM)
        - schedule_key: str | None
        - themen: str
    """
    kandidaten: list[dict] = []

    # Quelle 1: Queue-Peek
    for user_id in _aktive_user_ids():
        queue_kandidat = _queue_peek(user_id)
        if queue_kandidat:
            kandidaten.append(queue_kandidat)

    # Quelle 2: Faellige periodische Aufgaben
    kandidaten.extend(_periodische_faellig())

    return kandidaten


def _aktive_user_ids() -> list[str]:
    """Gibt alle aktiven User-IDs zurueck.

    Aktuell: Alle User mit last_activity in Redis (TTL 2h).
    Fallback: leere Liste.
    """
    user_ids: list[str] = []

    for key in redis_client.scan_iter(match="last_activity:*"):
        if isinstance(key, bytes):
            key = key.decode("utf-8")
        uid = key.split(":", 1)[1] if ":" in key else ""
        if uid:
            user_ids.append(uid)

    return user_ids


def _queue_peek(user_id: str) -> dict | None:
    """Peek auf shadow_queue und queue (Promotion) fuer einen User.

    Gibt den Eintrag mit der hoechsten Prioritaet zurueck, ohne ihn zu entfernen.
    """
    bester: dict | None = None
    beste_prio: float = -1.0

    for queue_key in [f"shadow_queue:{user_id}", f"queue:{user_id}"]:
        eintraege = redis_client.lrange(queue_key, 0, -1)

        for raw in eintraege:
            try:
                eintrag = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue

            prio: float = float(eintrag.get("prioritaet", eintrag.get("salienz", 0.0)))

            if prio > beste_prio:
                beste_prio = prio
                bester = {
                    "name": eintrag.get("aufgabe", "unbekannt"),
                    "prioritaet": prio,
                    "quelle": "queue",
                    "daten": eintrag,
                    "queue_key": queue_key,
                    "queue_raw": raw,
                    "schedule_key": None,
                    "themen": eintrag.get("themen", ""),
                }

    return bester


def _periodische_faellig() -> list[dict]:
    """Sammelt alle faelligen periodischen Aufgaben aus Redis.

    Redis-Keys: pixie:schedule:{agent_name} -> Hash mit priority, interval, next_run, description
    """
    jetzt: float = time.time()
    faellige: list[dict] = []

    for key in redis_client.scan_iter(match="pixie:schedule:*"):
        if isinstance(key, bytes):
            key = key.decode("utf-8")

        daten = redis_client.hgetall(key)
        if not daten:
            continue

        # Byte-Keys decodieren
        if daten and isinstance(list(daten.keys())[0], bytes):
            daten = {
                k.decode(): v.decode() if isinstance(v, bytes) else v
                for k, v in daten.items()
            }

        next_run: float = float(daten.get("next_run", 0))

        if next_run <= jetzt:
            agent_name: str = key.split(":")[-1]
            faellige.append({
                "name": daten.get("description", agent_name),
                "prioritaet": float(daten.get("priority", 0.0)),
                "quelle": "periodisch",
                "daten": daten,
                "queue_key": None,
                "queue_raw": None,
                "schedule_key": key,
                "themen": "",
            })

    return faellige
