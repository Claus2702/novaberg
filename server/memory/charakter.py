"""
Charakter-Hash — Kern + Adaptiv aus PostgreSQL.
"""

import logging

import psycopg2

logger = logging.getLogger("ki_server.memory.charakter")


def charakter_hash_retrieve(postgres_url: str, user_id: str) -> str:
    """Holt den aktuellen Charakter-Hash des Users."""

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT kern_hash, adaptive_hash FROM charakter_hash WHERE user_id = %s",
            (user_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            kern, adaptiv = row
            parts: list[str] = []
            if kern:
                parts.append(f"Kern-Persönlichkeit: {kern}")
            if adaptiv:
                parts.append(f"Aktuelle Phase: {adaptiv}")
            logger.info(f"Charakter-Hash gefunden für user '{user_id}'")
            return "\n".join(parts)

        return ""

    except Exception as fehler:
        logger.error(f"Charakter-Hash Abruf fehlgeschlagen: {fehler}")
        return ""


def charakter_hash_retrieve_dict(postgres_url: str, user_id: str) -> dict:
    """Holt den Charakter-Hash als Dict (kern, adaptiv, beziehungsprofil, intentions_profil, emotions_profil)."""

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT kern_hash, adaptive_hash, beziehungsprofil, intentions_profil, emotions_profil "
            "FROM charakter_hash WHERE user_id = %s",
            (user_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "kern":              row[0] or "",
                "adaptiv":           row[1] or "",
                "beziehungsprofil":  row[2] or "",
                "intentions_profil": row[3] or "",
                "emotions_profil":   row[4] or "",
            }

        return {}

    except Exception as fehler:
        logger.error(f"Charakter-Hash-Dict Abruf fehlgeschlagen: {fehler}")
        return {}
