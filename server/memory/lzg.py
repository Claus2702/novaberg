"""
Langzeitgedächtnis — PostgreSQL + pgvector.
Embedding-basierte semantische Suche mit Ebbinghaus-Decay.
"""

import logging
import math
from datetime import datetime, timezone

import psycopg2

from config import EBBINGHAUS_DECAY_RATE

logger = logging.getLogger("ki_server.memory.lzg")


def effektives_gewicht_berechnen(
    gewicht:       float,
    verstaerkt_am: datetime,
    jetzt:         datetime | None = None,
    decay_rate:    float = EBBINGHAUS_DECAY_RATE,
) -> float:
    """
    Berechnet das effektive Gewicht unter Berücksichtigung
    des zeitlichen Verfalls nach Ebbinghaus.

    Das gespeicherte Gewicht dokumentiert die Verstärkungshistorie.
    Der Decay wird live berechnet, nie gespeichert.

    Formel: effektiv = gewicht * e^(-decay_rate * tage)
    """
    if jetzt is None:
        jetzt = datetime.now(timezone.utc)

    if verstaerkt_am.tzinfo is None:
        verstaerkt_am = verstaerkt_am.replace(tzinfo=timezone.utc)

    tage: float = max(0.0, (jetzt - verstaerkt_am).total_seconds() / 86400.0)
    decay: float = math.exp(-decay_rate * tage)

    return round(gewicht * decay, 4)


def lzg_context_retrieve(
    postgres_url: str,
    user_id:      str,
    character_id: str,
    embedding:    list[float],
    top_k:        int = 10
) -> str:
    """Holt die relevantesten LZG-Einträge eines Paares (user_id, character_id)."""

    embedding_str: str = "[" + ",".join(str(x) for x in embedding) + "]"

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT inhalt, dimension, gewicht, arousal, emotions_vektor,
                   verstaerkt_am, beobachter,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM langzeitgedaechtnis
            WHERE user_id = %s
              AND character_id = %s
              AND embedding IS NOT NULL
              AND aktiv = TRUE
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (embedding_str, user_id, character_id, embedding_str, top_k))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return ""

        logger.info(f"LZG: Paar={user_id}:{character_id}, Treffer={len(rows)}")

        context_parts: list[str] = []
        for inhalt, dimension, gewicht, arousal, emotions_vektor, verstaerkt_am, beobachter, similarity in rows:
            if similarity >= 0.5:
                eff_gewicht: float = effektives_gewicht_berechnen(gewicht, verstaerkt_am)
                meta: str = f"Gewicht: {eff_gewicht:.2f}, Arousal: {arousal:.0%}, Beobachter: {beobachter}"
                if emotions_vektor:
                    meta += f", Vektor: {emotions_vektor}"
                context_parts.append(
                    f"[LZG/{dimension}] ({meta}): {inhalt}"
                )

        return "\n".join(context_parts)

    except Exception as fehler:
        logger.error(f"LZG-Kontextabruf fehlgeschlagen: {fehler}")
        return ""
