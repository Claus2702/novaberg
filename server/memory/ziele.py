"""
Ziele — Novas Antrieb aus PostgreSQL.

Langfristige Ziele (aus der Charakter-Destillation) und mittelfristige
Ziele (aus Pixie-Aktivitäten) mit Embedding für Gravitationsberechnung.
"""

import logging
from datetime import datetime, timezone

import psycopg2

from services.model_services import model_service, EmbedRequest
from memory.utils import embedding_zu_pgvector_str

logger = logging.getLogger("ki_server.memory.ziele")


def ziele_aktive_laden(postgres_url: str, user_id: str = "nova") -> list[dict]:
    """Lädt alle aktiven Ziele eines Users mit Embedding.

    Args:
        postgres_url: PostgreSQL-Verbindungs-URL.
        user_id: User-ID (default "nova" — Ziele sind Novas eigene).

    Returns:
        Liste von Ziel-Dicts mit id, ziel_typ, zielsatz, motivation,
        emotion, arousal, embedding, erstellt_am.
    """
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, ziel_typ, zielsatz, motivation, emotion, arousal,
                   embedding::text, erstellt_am, COALESCE(thema, '')
            FROM ziele
            WHERE user_id = %s AND aktiv = TRUE
            ORDER BY ziel_typ, motivation DESC
            """,
            (user_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        ziele: list[dict] = []
        for row in rows:
            # Embedding aus PostgreSQL-Text-Format parsen: "[0.1,0.2,...]" → list[float]
            embedding_raw: str | None = row[6]
            embedding: list[float] | None = None
            if embedding_raw:
                embedding = [
                    float(x) for x in embedding_raw.strip("[]").split(",")
                ]

            ziele.append({
                "id":          row[0],
                "ziel_typ":    row[1],
                "zielsatz":    row[2],
                "motivation":  row[3],
                "emotion":     row[4],
                "arousal":     row[5],
                "embedding":   embedding,
                "erstellt_am": row[7],
                "thema":       row[8] or "",
            })

        logger.info(
            f"Ziele geladen: {len(ziele)} aktive Ziele für '{user_id}' "
            f"({sum(1 for z in ziele if z['ziel_typ'] == 'langfristig')} lang, "
            f"{sum(1 for z in ziele if z['ziel_typ'] == 'mittelfristig')} mittel)"
        )
        return ziele

    except Exception as fehler:
        logger.error(f"Ziele laden fehlgeschlagen: {fehler}")
        return []


def ziel_speichern(
    postgres_url: str,
    user_id:      str,
    ziel_typ:     str,
    zielsatz:     str,
    motivation:   float,
    emotion:      str = "",
    arousal:      float = 0.5,
    thema:        str = "",
    embedding:    list[float] | None = None,
) -> int | None:
    """Speichert ein neues Ziel in PostgreSQL.

    Args:
        postgres_url: PostgreSQL-Verbindungs-URL.
        user_id: User-ID (typisch "nova").
        ziel_typ: "langfristig" oder "mittelfristig".
        zielsatz: Der Ziel-Text (1-2 Sätze).
        motivation: Motivationsstärke (0.0-1.0).
        emotion: Emotionale Valenz des Ziels.
        arousal: Emotionale Intensität.
        thema: Kurzes Themen-Label (2-3 Wörter) für das Gravitationsgraph-Panel.
        embedding: Vorberechnetes Embedding (768-dim), oder None.

    Returns:
        ID des neuen Eintrags, oder None bei Fehler.
    """
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        embedding_str: str | None = None
        if embedding:
            embedding_str = embedding_zu_pgvector_str(embedding)

        cursor.execute(
            """
            INSERT INTO ziele (user_id, ziel_typ, zielsatz, motivation,
                               emotion, arousal, thema, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector)
            RETURNING id
            """,
            (user_id, ziel_typ, zielsatz, motivation,
             emotion, arousal, thema, embedding_str),
        )

        ziel_id: int = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        logger.info(
            f"Ziel gespeichert: id={ziel_id}, typ={ziel_typ}, "
            f"motivation={motivation:.2f}, '{zielsatz[:60]}'"
        )
        return ziel_id

    except Exception as fehler:
        logger.error(f"Ziel speichern fehlgeschlagen: {fehler}")
        return None


def ziel_motivation_anpassen(
    postgres_url: str,
    ziel_id:      int,
    neue_motivation: float,
) -> bool:
    """Passt die Motivation eines Ziels an.

    Args:
        postgres_url: PostgreSQL-Verbindungs-URL.
        ziel_id: ID des Ziels.
        neue_motivation: Neuer Motivationswert (0.0-1.0).

    Returns:
        True bei Erfolg, False bei Fehler.
    """
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE ziele
            SET motivation = %s, aktualisiert_am = NOW()
            WHERE id = %s
            """,
            (neue_motivation, ziel_id),
        )

        conn.commit()
        conn.close()

        logger.info(f"Ziel-Motivation angepasst: id={ziel_id}, motivation={neue_motivation:.2f}")
        return True

    except Exception as fehler:
        logger.error(f"Ziel-Motivation anpassen fehlgeschlagen: {fehler}")
        return False


def ziel_deaktivieren(postgres_url: str, ziel_id: int) -> bool:
    """Deaktiviert ein Ziel (soft delete).

    Args:
        postgres_url: PostgreSQL-Verbindungs-URL.
        ziel_id: ID des Ziels.

    Returns:
        True bei Erfolg, False bei Fehler.
    """
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE ziele SET aktiv = FALSE, aktualisiert_am = NOW() WHERE id = %s",
            (ziel_id,),
        )

        conn.commit()
        conn.close()

        logger.info(f"Ziel deaktiviert: id={ziel_id}")
        return True

    except Exception as fehler:
        logger.error(f"Ziel deaktivieren fehlgeschlagen: {fehler}")
        return False


async def ziele_embeddings_sicherstellen(
    postgres_url: str,
) -> None:
    """Erzeugt Embeddings für Ziele die noch keins haben (Startup-Repair).

    Analog zu entitaeten_embeddings_sicherstellen in chat.py.

    Läuft im FastAPI-Lifespan im Haupt-Event-Loop und nutzt deshalb die
    async-API des EmbedWorkers direkt (submit), nicht die sync-Brücke
    (submit_sync würde den eigenen Loop blockierend belauern → Deadlock).

    Args:
        postgres_url: PostgreSQL-Verbindungs-URL.
    """
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, zielsatz FROM ziele WHERE embedding IS NULL AND aktiv = TRUE"
        )

        rows = cursor.fetchall()
        conn.close()

    except Exception as fehler:
        logger.warning(f"Ziele Embedding-Repair: DB-Abfrage fehlgeschlagen — {fehler}")
        return

    if not rows:
        logger.debug("Ziele Embedding-Repair: Alle Ziele haben Embeddings")
        return

    for ziel_id, zielsatz in rows:
        try:
            request = EmbedRequest(text=zielsatz)
            embed_response = await model_service.embed.submit(request)
            embedding: list[float] = embed_response.embedding
            logger.debug(
                "Ziele-Repair: Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(embedding),
                embed_response.duration_seconds,
            )

            conn   = psycopg2.connect(postgres_url)
            cursor = conn.cursor()

            embedding_str: str = embedding_zu_pgvector_str(embedding)
            cursor.execute(
                "UPDATE ziele SET embedding = %s::vector WHERE id = %s",
                (embedding_str, ziel_id),
            )

            conn.commit()
            conn.close()

            logger.info(
                f"Ziel id={ziel_id}: Embedding nachträglich erzeugt — "
                f"'{zielsatz[:60]}'"
            )

        except Exception as fehler:
            logger.warning(f"Ziele Embedding-Repair für id={ziel_id} fehlgeschlagen: {fehler}")
