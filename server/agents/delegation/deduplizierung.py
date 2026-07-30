"""Deduplizierung — Embedding + pgvector Cosine-Similarity gegen offene Akten.

Prueft ob bereits eine thematisch aehnliche Akte existiert.
Bei Treffer: bestehende_akte_id setzen → Agent reichert an.
Bei keinem Treffer: nur Embedding setzen → Agent erstellt neue Akte.
"""

import logging

import numpy as np

from agents.base import AgentState
from agents.delegation.akte import embed_text_bauen
from config import postgres_verbinden, DELEGATION_SIMILARITY_SCHWELLE
from services.model_services import model_service, EmbedRequest

logger = logging.getLogger("ki_server.agents.delegation.deduplizierung")


def duplikat_pruefen(state: AgentState) -> dict:
    """Erzeugt Embedding und sucht aehnliche offene Akte."""
    salienz_obj: dict = state["parameter"].get("salienz_obj", {})
    user_id:     str  = state["kontext"].get("user_id", "")

    themen: str = ", ".join(salienz_obj.get("themen", []))
    zusammenfassung: str = salienz_obj.get("zusammenfassung", "")
    embed_text: str = embed_text_bauen(themen, zusammenfassung)

    # Embedding erzeugen
    request = EmbedRequest(text=embed_text)
    embed_response = model_service.embed.submit_sync(request)
    embedding: list[float] = embed_response.embedding
    logger.debug(
        "Delegation-Dedup: Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
        len(embedding),
        embed_response.duration_seconds,
    )

    # pgvector Cosine-Similarity gegen offene Akten
    bestehende_akte_id: int | None = None
    conn = None

    try:
        conn = postgres_verbinden()
        cursor = conn.cursor()

        embedding_str: str = "[" + ",".join(str(v) for v in embedding) + "]"

        cursor.execute(
            """
            SELECT id, themen, 1 - (themen_embedding <=> %s::vector) AS similarity
            FROM delegations_akten
            WHERE user_id = %s AND aktiv = TRUE AND status = 'offen'
                  AND themen_embedding IS NOT NULL
            ORDER BY similarity DESC LIMIT 1
            """,
            (embedding_str, user_id),
        )

        row = cursor.fetchone()
        if row and row[2] >= DELEGATION_SIMILARITY_SCHWELLE:
            bestehende_akte_id = row[0]
            logger.info(
                f"Deduplizierung: Aehnliche Akte gefunden — id={row[0]}, "
                f"themen='{row[1]}', similarity={row[2]:.3f}"
            )
        else:
            logger.info("Deduplizierung: Keine aehnliche Akte — neue Akte wird erstellt")

    except Exception as fehler:
        logger.warning(f"Deduplizierung: DB-Fehler — {fehler}. Erstelle neue Akte.")

    finally:
        if conn:
            conn.close()

    result: dict = {
        "parameter": {
            **state["parameter"],
            "themen_embedding": embedding,
        },
        "status": "laufend",
        "schritte": state["schritte"] + [{
            "node": "duplikat_pruefen",
            "ergebnis": "anreichern" if bestehende_akte_id else "neu",
        }],
    }

    if bestehende_akte_id:
        result["parameter"]["bestehende_akte_id"] = bestehende_akte_id

    return result
