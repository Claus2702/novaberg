"""
Datenzugriffsschicht für die fakten-Tabelle (Knowledge Graph Edges).
Keine Business-Logik — reine CRUD-Operationen.
"""

import logging
from datetime import datetime

import psycopg2
import psycopg2.extras

from memory.utils import embedding_zu_pgvector_str

logger = logging.getLogger("ki_server.memory.repositories.fakten")


class FaktenRepository:
    """Datenzugriffsschicht für die fakten-Tabelle. Keine Business-Logik."""

    @staticmethod
    def embed_text_bauen(fakt_text: str) -> str:
        """
        Baut den Embed-Text eines Fakts — die EINZIGE Formel für diese
        Spalte (Chat 107). Der Text ist aus der persistierten Spalte
        fakt_text vollständig rekonstruierbar.

        E: fakt_text muss nicht-leer sein.
        V: Formel ist die Identität (Live-Formel des FaktenManagers).
        A: der unveränderte fakt_text.
        """
        if not fakt_text or not fakt_text.strip():
            raise ValueError("embed_text_bauen(fakten): fakt_text ist leer — kein Embed-Text baubar")
        return fakt_text

    @staticmethod
    def insert(
        postgres_url: str,
        user_id:      str,
        subjekt_id:   int,
        attribut:     str,
        fakt_text:    str,
        objekt_id:    int | None = None,
        objekt_wert:  str | None = None,
        embedding:    list[float] | None = None,
        t_valid:      datetime | None = None,
    ) -> int:
        """
        Neuen Fakt anlegen. Gibt die neue ID zurück.
        Genau einer von objekt_id oder objekt_wert muss gesetzt sein.
        Wirft ValueError wenn keiner oder beide gesetzt sind.
        """
        if (objekt_id is None) == (objekt_wert is None):
            raise ValueError(
                "Genau einer von objekt_id oder objekt_wert muss gesetzt sein."
            )

        embedding_str: str | None = (
            embedding_zu_pgvector_str(embedding)
            if embedding else None
        )

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fakten
                    (user_id, subjekt_id, attribut, objekt_id, objekt_wert,
                     fakt_text, embedding, t_valid)
                VALUES (%s, %s, %s, %s, %s, %s, %s::vector, %s)
                RETURNING id
            """, (user_id, subjekt_id, attribut, objekt_id, objekt_wert,
                  fakt_text, embedding_str, t_valid))
            fakt_id: int = cursor.fetchone()[0]
            conn.commit()
            return fakt_id
        finally:
            conn.close()

    @staticmethod
    def find_by_id(
        postgres_url: str,
        fakt_id:      int,
    ) -> dict | None:
        """
        Fakt per ID laden. Nur aktive Einträge.
        Setzt last_touched auf NOW().
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                UPDATE fakten
                SET last_touched = NOW()
                WHERE id = %s AND aktiv = TRUE
                RETURNING *
            """, (fakt_id,))
            row = cursor.fetchone()
            conn.commit()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def find_by_subjekt(
        postgres_url: str,
        subjekt_id:   int,
    ) -> list[dict]:
        """
        Alle aktiven Fakten zu einer Entität laden.
        Setzt last_touched auf NOW() für alle Treffer.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                UPDATE fakten
                SET last_touched = NOW()
                WHERE subjekt_id = %s AND aktiv = TRUE
                RETURNING *
            """, (subjekt_id,))
            rows = cursor.fetchall()
            conn.commit()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def find_aktiv(
        postgres_url: str,
        subjekt_id:   int,
        attribut:     str,
    ) -> dict | None:
        """
        Aktiven Fakt per Subjekt + Attribut finden.
        Für Edge Invalidation: gibt es schon einen aktiven Fakt
        mit dem gleichen Subjekt und Attribut?
        Setzt last_touched auf NOW().
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                UPDATE fakten
                SET last_touched = NOW()
                WHERE subjekt_id = %s AND attribut = %s AND aktiv = TRUE
                RETURNING *
            """, (subjekt_id, attribut))
            row = cursor.fetchone()
            conn.commit()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def find_similar(
        postgres_url: str,
        user_id:      str,
        embedding:    list[float],
        # Kalibriert auf nomic-embed-text-v2-moe (Chat 107), vorher 0.80 im
        # casing-blinden Raum. Kein Live-Aufrufer — mitgezogen, damit der
        # Pfad bei Reaktivierung nicht mit einem toten Wert startet.
        # ⚠ Wachposten: nicht gemessen — begruendeter Startwert.
        threshold:    float = 0.70,
        limit:        int = 5,
    ) -> list[dict]:
        """
        Ähnliche Fakten per Embedding-Similarity suchen (aktive).
        Gibt Liste von dicts mit 'similarity' zurück.
        """
        embedding_str: str = embedding_zu_pgvector_str(embedding)

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT *,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM fakten
                WHERE user_id = %s
                  AND aktiv = TRUE
                  AND embedding IS NOT NULL
                  AND 1 - (embedding <=> %s::vector) >= %s
                ORDER BY similarity DESC
                LIMIT %s
            """, (embedding_str, user_id, embedding_str, threshold, limit))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def invalidate(
        postgres_url: str,
        fakt_id:      int,
    ) -> None:
        """
        Fakt invalidieren (nicht löschen!).
        Setzt aktiv=FALSE und t_invalid=NOW().
        Der alte Fakt bleibt für die Historie erhalten.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE fakten
                SET aktiv = FALSE, t_invalid = NOW()
                WHERE id = %s
            """, (fakt_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def find_historie(
        postgres_url: str,
        subjekt_id:   int,
        attribut:     str,
    ) -> list[dict]:
        """
        Alle Fakten (aktiv UND inaktiv) zu Subjekt+Attribut laden.
        Für historische Abfragen: "Wo hat Michael früher gewohnt?"
        Sortiert nach t_valid DESC (neueste zuerst).
        Setzt last_touched NICHT (Historien-Abfrage).
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM fakten
                WHERE subjekt_id = %s AND attribut = %s
                ORDER BY t_valid DESC NULLS LAST
            """, (subjekt_id, attribut))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def set_wiedervorlage(
        postgres_url:    str,
        fakt_id:         int,
        wiedervorlage_am: datetime | None,
    ) -> None:
        """Wiedervorlage-Datum setzen oder löschen."""
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE fakten
                SET wiedervorlage_am = %s
                WHERE id = %s
            """, (wiedervorlage_am, fakt_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def find_wiedervorlage_faellig(
        postgres_url: str,
        user_id:      str,
    ) -> list[dict]:
        """
        Alle Fakten mit fälliger Wiedervorlage.
        Für den Butler-Task.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM fakten
                WHERE user_id = %s
                  AND aktiv = TRUE
                  AND wiedervorlage_am IS NOT NULL
                  AND wiedervorlage_am <= NOW()
                ORDER BY wiedervorlage_am
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
