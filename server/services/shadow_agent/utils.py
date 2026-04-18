"""Shadow Agent — Shared Utilities."""

import json
import logging
from datetime import datetime

import psycopg2
import redis

logger = logging.getLogger("ki_server.shadow")


# ─────────────────────────────────────────────
# Queue befüllen (wird vom Hauptgraph aufgerufen)
# ─────────────────────────────────────────────
def shadow_queue_push(
    redis_client: redis.Redis,
    user_id:      str,
    aufgabe:      str,
    thema:        str,
    kontext:      str = "",
    prioritaet:   float = 0.0,
    intentionen:  list = None,
    emotion:      str  = "",
    modus:        str  = "",
) -> None:
    """Legt einen Auftrag in die Shadow-Queue."""

    eintrag: dict = {
        "aufgabe":     aufgabe,
        "thema":       thema,
        "kontext":     kontext,
        "prioritaet":  prioritaet,
        "intentionen": intentionen or [],
        "emotion":     emotion,
        "modus":       modus,
        "erstellt":    datetime.now().isoformat(),
    }

    redis_client.rpush(
        f"shadow_queue:{user_id}",
        json.dumps(eintrag, ensure_ascii=False),
    )

    logger.info(f"Shadow-Queue: '{aufgabe}' für '{user_id}' — {thema[:60]}")


# ─────────────────────────────────────────────
# Stack lesen (wird vom Client/Chat aufgerufen)
# ─────────────────────────────────────────────
def shadow_stack_pop(
    redis_client: redis.Redis,
    user_id:      str,
) -> dict | None:
    """Holt das älteste Ergebnis vom Stack. Gibt None zurück wenn leer."""

    raw: str | None = redis_client.lpop(f"shadow_stack:{user_id}")

    if not raw:
        return None

    return json.loads(raw)


def shadow_stack_peek(
    redis_client: redis.Redis,
    user_id:      str,
    count:        int = 5,
) -> list[dict]:
    """Liest die obersten Stack-Einträge ohne sie zu entfernen."""

    raw_list: list = redis_client.lrange(f"shadow_stack:{user_id}", 0, count - 1)

    return [json.loads(r) for r in raw_list]


# ─────────────────────────────────────────────
# Stack Push (Ergebnis ablegen)
# ─────────────────────────────────────────────
def stack_push(
    redis_client:  redis.Redis,
    user_id:       str,
    aufgabe:       str,
    thema:         str,
    inhalt:        str,
    embed_client,
    embed_model:   str,
    intentionen:   list = None,
    emotion:       str  = "",
    modus:         str  = "",
) -> None:
    """Legt ein Ergebnis mit Embedding und Meta-Daten auf den Shadow-Stack."""

    embed_text: str = f"{thema} {inhalt[:200]}"

    try:
        embedding: list[float] = embed_client.embed(
            model = embed_model,
            input = embed_text,
        )["embeddings"][0]
    except Exception as fehler:
        logger.warning(f"Shadow-Stack: Embedding fehlgeschlagen — {fehler}")
        embedding = []

    eintrag: dict = {
        "aufgabe":     aufgabe,
        "thema":       thema,
        "inhalt":      inhalt,
        "erstellt":    datetime.now().isoformat(),
        "embedding":   embedding,
        "intentionen": intentionen or [],
        "emotion":     emotion,
        "modus":       modus,
    }

    redis_client.rpush(
        f"shadow_stack:{user_id}",
        json.dumps(eintrag, ensure_ascii=False),
    )

    logger.info(f"Shadow-Stack: '{aufgabe}' für '{user_id}' abgelegt (Embedding: {len(embedding)} dims).")


# ─────────────────────────────────────────────
# Nova Vorwissen laden (aus LZG)
# ─────────────────────────────────────────────
def nova_vorwissen_laden(
    postgres_url:  str,
    embed_client,
    embed_model:   str,
    thema:         str,
) -> str:
    """Lädt relevantes Vorwissen aus Novas LZG."""

    try:
        embedding: list[float] = embed_client.embed(
            model = embed_model,
            input = thema,
        )["embeddings"][0]

        embedding_str: str = "[" + ",".join(str(x) for x in embedding) + "]"

        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT inhalt
            FROM   langzeitgedaechtnis
            WHERE  user_id = 'nova'
              AND  aktiv = TRUE
              AND  1 - (embedding <=> %s::vector) > 0.7
            ORDER  BY gewicht DESC
            LIMIT  3
        """, (embedding_str,))

        treffer: list = cursor.fetchall()
        conn.close()

        if not treffer:
            return ""

        return " | ".join(row[0] for row in treffer)

    except Exception as fehler:
        logger.warning(f"Nova-Vorwissen: Fehler — {fehler}")
        return ""


# ─────────────────────────────────────────────
# Log schreiben
# ─────────────────────────────────────────────
def log_schreiben(
    postgres_url: str,
    user_id:      str,
    aufgabe:      str,
    ergebnis:     str,
    status:       str,
) -> None:
    """Schreibt einen Eintrag ins Hintergrund-Log."""

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO hintergrund_log
                (user_id, aufgabe, ergebnis, status, verarbeitet_am)
            VALUES
                (%s, %s, %s, %s, NOW())
        """, (user_id, aufgabe, ergebnis, status))

        conn.commit()
        conn.close()

    except Exception as fehler:
        logger.error(f"Shadow-Log: Schreibfehler — {fehler}")
