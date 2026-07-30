"""Migration: KZG-Key-Schema von Zweiteilig zu Paar-basiert.

Alt:  kzg:{user_id}:{entry_id}
Neu:  kzg:{user_id}:{character_id}:{entry_id}

Regeln:
  - kzg:meister:* (ohne nova-Segment) -> kzg:meister:nova:*       (beobachter=user)
  - kzg:nova:*    (Novas eigene Eintraege) -> kzg:meister:nova:*   (beobachter=assistant)

Aufruf:
    docker exec ki_server python tools/migrate_kzg_keys.py
oder:
    docker exec -it ki_server python -c "from tools.migrate_kzg_keys import migrate; migrate()"
"""

from __future__ import annotations

import logging

import redis

from config import ASSISTANT_USER_ID, DEFAULT_USER_ID, REDIS_URL, redis_client

logger = logging.getLogger("ki_server.tools.migrate_kzg")

# Eigener Client ohne Auto-Decode: HGETALL liefert sonst bei Embedding-Bytes
# einen UnicodeDecodeError. Fuer Hash-Operationen benutzen wir raw_redis,
# KEYS/SCAN laufen weiter ueber den globalen redis_client.
raw_redis: redis.Redis = redis.from_url(REDIS_URL, decode_responses=False)


def _ist_zweiteilig(key: str) -> bool:
    """True, wenn der Key genau zwei Doppelpunkte enthaelt (kzg:X:Y).

    Dreiteilige Keys (kzg:X:Y:Z) werden ausgeschlossen, auch wenn der
    Redis-Glob sie matcht.
    """
    return key.startswith("kzg:") and key.count(":") == 2


def _migriere_key(
    alt_key:      str,
    neuer_key:    str,
    user_id:      str,
    character_id: str,
    beobachter:   str,
) -> bool:
    """Migriert einen einzelnen Key. Gibt True zurueck wenn migriert."""
    if raw_redis.exists(neuer_key):
        logger.warning(f"Kollision: Zielkey '{neuer_key}' existiert bereits — uebersprungen")
        return False

    roh: dict = raw_redis.hgetall(alt_key)
    if not roh:
        logger.warning(f"Leerer oder fehlender Hash: '{alt_key}' — uebersprungen")
        return False

    # bytes-Keys zu str decodieren, Values (inkl. Embedding-Bytes) unveraendert lassen
    mapping: dict = {
        (k.decode() if isinstance(k, bytes) else k): v
        for k, v in roh.items()
    }

    mapping["user_id"]      = user_id
    mapping["character_id"] = character_id
    mapping["beobachter"]   = beobachter

    raw_redis.hset(neuer_key, mapping=mapping)

    # TTL uebernehmen, falls vorhanden
    ttl_ms: int = raw_redis.pttl(alt_key)
    if ttl_ms and ttl_ms > 0:
        raw_redis.pexpire(neuer_key, ttl_ms)

    raw_redis.delete(alt_key)

    return True


def migrate(
    user_id:      str = DEFAULT_USER_ID,
    character_id: str = ASSISTANT_USER_ID,
) -> dict:
    """Migriert alle alten zweiteiligen KZG-Keys in das neue Paar-Schema."""
    logger.info(
        f"KZG-Migration startet — Zielpaar {user_id}:{character_id}"
    )

    user_migriert:  int = 0
    nova_migriert:  int = 0
    uebersprungen: int = 0

    # ── 1. User-Eintraege: kzg:{user_id}:{entry_id}  (Beobachter: user) ──
    for key in redis_client.scan_iter(match=f"kzg:{user_id}:*", count=200):
        if not _ist_zweiteilig(key):
            continue

        entry_id:  str = key.split(":", 2)[2]
        neuer_key: str = f"kzg:{user_id}:{character_id}:{entry_id}"

        if _migriere_key(key, neuer_key, user_id, character_id, beobachter="user"):
            user_migriert += 1
            logger.info(f"Migriert (user): {key} -> {neuer_key}")
        else:
            uebersprungen += 1

    # ── 2. Nova-Eintraege: kzg:{character_id}:{entry_id}  (Beobachter: assistant) ──
    for key in redis_client.scan_iter(match=f"kzg:{character_id}:*", count=200):
        if not _ist_zweiteilig(key):
            continue

        entry_id:  str = key.split(":", 2)[2]
        neuer_key: str = f"kzg:{user_id}:{character_id}:{entry_id}"

        if _migriere_key(key, neuer_key, user_id, character_id, beobachter="assistant"):
            nova_migriert += 1
            logger.info(f"Migriert (assistant): {key} -> {neuer_key}")
        else:
            uebersprungen += 1

    gesamt: int = user_migriert + nova_migriert

    logger.info(
        f"KZG-Migration abgeschlossen — "
        f"user={user_migriert}, assistant={nova_migriert}, "
        f"uebersprungen={uebersprungen}, gesamt={gesamt}"
    )

    return {
        "user":          user_migriert,
        "assistant":     nova_migriert,
        "uebersprungen": uebersprungen,
        "gesamt":        gesamt,
    }


if __name__ == "__main__":
    ergebnis: dict = migrate()
    print(
        f"Migration fertig: {ergebnis['gesamt']} Keys migriert "
        f"(user={ergebnis['user']}, assistant={ergebnis['assistant']}, "
        f"uebersprungen={ergebnis['uebersprungen']})"
    )
