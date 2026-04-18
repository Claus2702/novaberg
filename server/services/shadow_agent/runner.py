"""Shadow Agent Runner — Queue-Processor + Scheduler-Logik."""

import json
import logging
import threading
from datetime import datetime

import redis

from services.shadow_agent.utils import stack_push, log_schreiben

logger = logging.getLogger("ki_server.shadow")

QUEUE_LIMIT: int = 20


def schatten_arbeit_ausfuehren(
    redis_client:  redis.Redis,
    postgres_url:  str,
    embed_client,
    embed_model:   str,
    task_registry: dict,
    shutdown_event: threading.Event | None = None,
) -> int:
    """
    Einheitlicher Worker — arbeitet alle Queues und Trigger ab.
    Wird im konfigurierten Intervall vom Scheduler aufgerufen.

    Feste Reihenfolge:
    1. LZG-Promotion     — IMMER ZUERST (Fakten gehen sonst per TTL verloren)
    2. LZG-Decay         — Housekeeping
    3. Wiedervorlage     — Butler
    4. Charakter-Hash    — nur wenn dirty
    5. Shadow-Queue      — Nachfragen, Recherche, Vertiefen etc.

    Returns: Anzahl verarbeiteter Aufträge
    """

    # Pixie pausiert? (Test-Modus)
    if redis_client.exists("pixie:paused"):
        logger.info("Pixie: Pausiert (pixie:paused gesetzt) — überspringe")
        return 0

    verarbeitet: int = 0

    # ── 1. Promotion-Queue VOLLSTÄNDIG abarbeiten ────
    verarbeitet += _promotion_abarbeiten(
        redis_client, postgres_url, embed_client,
        embed_model, task_registry, shutdown_event,
    )

    # ── 2. LZG-Decay (Ebbinghaus) ─────────────────
    verarbeitet += _singleton_task_ausfuehren(
        "lzg_decay", task_registry, redis_client, postgres_url,
        embed_client, embed_model, shutdown_event,
    )

    # ── 3. Wiedervorlage (Butler) ─────────────────
    verarbeitet += _singleton_task_ausfuehren(
        "wiedervorlage", task_registry, redis_client, postgres_url,
        embed_client, embed_model, shutdown_event,
    )

    # ── 4. Charakter-Hash prüfen ─────────────────
    verarbeitet += _charakter_hash_abarbeiten(
        redis_client, postgres_url, embed_client,
        embed_model, task_registry, shutdown_event,
    )

    # ── 5. Shadow-Queue abarbeiten ───────────────
    verarbeitet += _shadow_queue_abarbeiten(
        redis_client, postgres_url, embed_client,
        embed_model, task_registry, shutdown_event,
    )

    # Status zurücksetzen
    redis_client.set("shadow_status", json.dumps({
        "zustand":   "idle",
        "user_id":   "",
        "thema":     "",
        "gestartet": datetime.now().isoformat(),
    }, ensure_ascii=False), ex=600)

    return verarbeitet


# ─────────────────────────────────────────────
# 1. Promotion (höchste Priorität)
# ─────────────────────────────────────────────
def _promotion_abarbeiten(
    redis_client:  redis.Redis,
    postgres_url:  str,
    embed_client,
    embed_model:   str,
    task_registry: dict,
    shutdown_event: threading.Event | None,
) -> int:
    if shutdown_event and shutdown_event.is_set():
        return 0

    promotion_task = task_registry.get("lzg_promotion")
    if not promotion_task:
        return 0

    verarbeitet: int = 0
    promo_keys: list = redis_client.keys("queue:*")

    for promo_key in promo_keys:
        if shutdown_event and shutdown_event.is_set():
            logger.info("Pixie: Shutdown — breche Promotion ab")
            return verarbeitet

        key_str: str = promo_key if isinstance(promo_key, str) else promo_key.decode()
        user_id: str = key_str.split(":")[1]

        # Queue-Limit: Überschüssige Einträge trimmen
        queue_length: int = redis_client.llen(key_str)
        if queue_length > QUEUE_LIMIT:
            redis_client.ltrim(key_str, 0, QUEUE_LIMIT - 1)
            logger.warning(f"Queue {user_id}: {queue_length} → auf {QUEUE_LIMIT} getrimmt")

        while True:
            raw: str | None = redis_client.lpop(key_str)
            if not raw:
                break

            try:
                auftrag: dict = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("Promotion: Ungültiger Queue-Eintrag — übersprungen")
                continue

            if auftrag.get("aufgabe") != "lzg_promotion":
                logger.info(f"Promotion: Aufgabe '{auftrag.get('aufgabe')}' — nicht Promotion, übersprungen")
                continue

            # Status-Reporting
            redis_client.set("shadow_status", json.dumps({
                "zustand":   "lzg_promotion",
                "user_id":   user_id,
                "thema":     auftrag.get("themen", "")[:60],
                "gestartet": datetime.now().isoformat(),
            }, ensure_ascii=False), ex=600)

            if shutdown_event and shutdown_event.is_set():
                return verarbeitet

            try:
                promotion_task.execute(
                    auftrag        = auftrag,
                    redis_client   = redis_client,
                    embed_client   = embed_client,
                    embed_model    = embed_model,
                    postgres_url   = postgres_url,
                    user_id        = user_id,
                    shutdown_event = shutdown_event,
                )

                log_schreiben(
                    postgres_url, user_id,
                    f"LZG-Promotion: {auftrag.get('themen', '')}",
                    "erledigt", "erledigt",
                )

                verarbeitet += 1

            except Exception as fehler:
                logger.error(f"Promotion: Fehler — {fehler}", exc_info=True)

    return verarbeitet


# ─────────────────────────────────────────────
# Singleton-Task ausführen (Decay, Butler)
# ─────────────────────────────────────────────
def _singleton_task_ausfuehren(
    task_name:      str,
    task_registry:  dict,
    redis_client:   redis.Redis,
    postgres_url:   str,
    embed_client,
    embed_model:    str,
    shutdown_event: threading.Event | None,
) -> int:
    if shutdown_event and shutdown_event.is_set():
        return 0

    task = task_registry.get(task_name)
    if not task:
        return 0

    try:
        task.execute(
            auftrag        = {},
            redis_client   = redis_client,
            embed_client   = embed_client,
            embed_model    = embed_model,
            postgres_url   = postgres_url,
            user_id        = "",
            shutdown_event = shutdown_event,
        )
        return 1
    except Exception as fehler:
        logger.error(f"{task_name}: Fehler — {fehler}")
        return 0


# ─────────────────────────────────────────────
# 4. Charakter-Hash
# ─────────────────────────────────────────────
def _charakter_hash_abarbeiten(
    redis_client:  redis.Redis,
    postgres_url:  str,
    embed_client,
    embed_model:   str,
    task_registry: dict,
    shutdown_event: threading.Event | None,
) -> int:
    if shutdown_event and shutdown_event.is_set():
        return 0

    hash_task = task_registry.get("charakter_hash")
    if not hash_task:
        return 0

    verarbeitet: int = 0
    dirty_keys: list = redis_client.keys("hash_dirty:*")

    for dirty_key in dirty_keys:
        if shutdown_event and shutdown_event.is_set():
            return verarbeitet

        key_str: str = dirty_key if isinstance(dirty_key, str) else dirty_key.decode()
        user_id: str = key_str.split(":")[1]

        dirty: str = redis_client.get(key_str) or ""
        if not dirty:
            continue

        redis_client.set("shadow_status", json.dumps({
            "zustand":   "charakter_hash",
            "user_id":   user_id,
            "thema":     "Profil-Destillation",
            "gestartet": datetime.now().isoformat(),
        }, ensure_ascii=False), ex=600)

        try:
            hash_task.execute(
                auftrag        = {},
                redis_client   = redis_client,
                embed_client   = embed_client,
                embed_model    = embed_model,
                postgres_url   = postgres_url,
                user_id        = user_id,
                shutdown_event = shutdown_event,
            )
            verarbeitet += 1
        except Exception as fehler:
            logger.error(f"Charakter-Hash: Fehler — {fehler}")

    return verarbeitet


# ─────────────────────────────────────────────
# 5. Shadow-Queue (Nachfragen, Recherche, etc.)
# ─────────────────────────────────────────────
def _shadow_queue_abarbeiten(
    redis_client:  redis.Redis,
    postgres_url:  str,
    embed_client,
    embed_model:   str,
    task_registry: dict,
    shutdown_event: threading.Event | None,
) -> int:
    if shutdown_event and shutdown_event.is_set():
        return 0

    verarbeitet: int = 0
    queue_keys: list = redis_client.keys("shadow_queue:*")

    for queue_key in queue_keys:
        if shutdown_event and shutdown_event.is_set():
            return verarbeitet

        key_str: str = queue_key if isinstance(queue_key, str) else queue_key.decode()
        user_id: str = key_str.split(":")[1]

        while True:
            raw: str | None = redis_client.lpop(key_str)
            if not raw:
                break

            try:
                auftrag: dict = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("Shadow: Ungültiger Queue-Eintrag — übersprungen")
                continue

            aufgabe: str = auftrag.get("aufgabe", "")

            # Status-Reporting
            redis_client.set("shadow_status", json.dumps({
                "zustand":   aufgabe,
                "user_id":   user_id,
                "thema":     auftrag.get("thema", "")[:60],
                "gestartet": datetime.now().isoformat(),
            }, ensure_ascii=False), ex=600)

            task = task_registry.get(aufgabe)
            if not task:
                logger.warning(f"Shadow: Unbekannte Aufgabe '{aufgabe}' — übersprungen")
                continue

            if not task.kann_ausfuehren(auftrag):
                logger.info(f"Shadow: Task '{aufgabe}' übersprungen (Emotion-Blacklist)")
                continue

            logger.info(
                f"Shadow: Verarbeite '{aufgabe}' — {auftrag.get('thema', '')[:60]} "
                f"(emotion={auftrag.get('emotion', '')}, modus={auftrag.get('modus', '')})"
            )

            if shutdown_event and shutdown_event.is_set():
                return verarbeitet

            try:
                ergebnis: dict | None = task.execute(
                    auftrag        = auftrag,
                    redis_client   = redis_client,
                    embed_client   = embed_client,
                    embed_model    = embed_model,
                    postgres_url   = postgres_url,
                    user_id        = user_id,
                    shutdown_event = shutdown_event,
                )

                if ergebnis:
                    stack_push(
                        redis_client  = redis_client,
                        user_id       = user_id,
                        aufgabe       = aufgabe,
                        thema         = ergebnis.get("thema", ""),
                        inhalt        = ergebnis.get("inhalt", ""),
                        embed_client  = embed_client,
                        embed_model   = embed_model,
                        intentionen   = auftrag.get("intentionen", []),
                        emotion       = auftrag.get("emotion", ""),
                        modus         = auftrag.get("modus", ""),
                    )

                    # Post-Hook: Nova-Gedächtnis bei Recherche/Vertiefung
                    if aufgabe in ("recherche", "vertiefen"):
                        if not (shutdown_event and shutdown_event.is_set()):
                            nova_task = task_registry.get("nova_gedaechtnis")
                            if nova_task:
                                try:
                                    nova_task.execute(
                                        auftrag        = {
                                            "thema":    ergebnis.get("thema", ""),
                                            "ergebnis": ergebnis.get("inhalt", ""),
                                        },
                                        redis_client   = redis_client,
                                        embed_client   = embed_client,
                                        embed_model    = embed_model,
                                        postgres_url   = postgres_url,
                                        user_id        = user_id,
                                        shutdown_event = shutdown_event,
                                    )
                                except Exception as nova_fehler:
                                    logger.warning(f"Shadow: Nova-Gedächtnis fehlgeschlagen — {nova_fehler}")

                log_schreiben(
                    postgres_url, user_id, aufgabe,
                    (ergebnis.get("inhalt", "")[:200] if ergebnis else "kein Ergebnis"),
                    "ok",
                )

                verarbeitet += 1

            except Exception as fehler:
                logger.error(f"Shadow: Fehler bei '{aufgabe}' — {fehler}")
                log_schreiben(postgres_url, user_id, aufgabe, str(fehler), "fehler")

    return verarbeitet
