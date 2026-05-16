"""
Charakter-Hash — Kern + Adaptiv aus PostgreSQL.
"""

import logging

import psycopg2

from config import ASSISTANT_USER_ID

logger = logging.getLogger("ki_server.memory.charakter")


def charakter_hash_retrieve(postgres_url: str, user_id: str, character_id: str = "") -> str:
    """Holt den aktuellen Charakter-Hash fuer ein Gespraechspaar."""

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT kern_hash, adaptive_hash FROM charakter_hash WHERE user_id = %s AND character_id = %s",
            (user_id, character_id),
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
            logger.info(f"Charakter-Hash gefunden fuer Paar '{user_id}/{character_id}'")
            return "\n".join(parts)

        return ""

    except Exception as fehler:
        logger.error(f"Charakter-Hash Abruf fehlgeschlagen: {fehler}")
        return ""


def charakter_hash_retrieve_dict(postgres_url: str, user_id: str, character_id: str = "") -> dict:
    """Holt den Charakter-Hash als Dict fuer ein Gespraechspaar."""

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT kern_hash, adaptive_hash, beziehungsprofil, intentions_profil, emotions_profil "
            "FROM charakter_hash WHERE user_id = %s AND character_id = %s",
            (user_id, character_id),
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


def nova_charakter_hash_retrieve_dict(postgres_url: str, user_id: str) -> dict:
    """Laedt Novas Charakter-Hash fuer das Gespraech mit einem bestimmten User.

    Im Paar-Schema lebt Novas Charakter unter (ASSISTANT_USER_ID, user_id):
    ASSISTANT_USER_ID ist der Schreiber (Subjekt), user_id der Gegenueber.
    Diese Funktion macht die Argument-Reihenfolge logisch — ohne sie waere
    der Aufrufer auf den Vertausch von user_id und character_id angewiesen.

    Vorbedingung: user_id ist nicht leer.
    Nachbedingung: Liefert dict mit den fuenf Hash-Schichten oder {} bei
    fehlendem Datensatz.
    """

    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        logger.error("nova_charakter_hash_retrieve_dict: user_id leer — verworfen")
        return {}

    # ── Verarbeitung ────────────────────────────
    return charakter_hash_retrieve_dict(postgres_url, ASSISTANT_USER_ID, user_id)
