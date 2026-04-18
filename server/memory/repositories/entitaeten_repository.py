"""
Datenzugriffsschicht für die entitaeten-Tabelle (Knowledge Graph Nodes).
Keine Business-Logik — reine CRUD-Operationen.
"""

import logging
from datetime import datetime

import psycopg2
import psycopg2.extras

logger = logging.getLogger("ki_server.memory.repositories.entitaeten")


class EntitaetenRepository:
    """Datenzugriffsschicht für die entitaeten-Tabelle. Keine Business-Logik."""

    @staticmethod
    def insert(
        postgres_url:    str,
        user_id:         str,
        name:            str,
        typ:             str = "sonstiges",
        zusammenfassung: str | None = None,
        embedding:       list[float] | None = None,
        t_valid:         datetime | None = None,
    ) -> int:
        """
        Neue Entität anlegen. Gibt die neue ID zurück.
        Setzt last_touched und t_created auf NOW().
        """
        embedding_str: str | None = (
            "[" + ",".join(str(x) for x in embedding) + "]"
            if embedding else None
        )

        # Suchtext manuell erzeugen (to_tsvector ist stable, nicht immutable)
        suchtext_sql = "to_tsvector('german', %s)"
        suchtext_input = " ".join(filter(None, [name, typ, zusammenfassung or ""]))

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO entitaeten
                    (user_id, name, typ, zusammenfassung, embedding, suchtext, t_valid)
                VALUES (%s, %s, %s, %s, %s::vector, {suchtext_sql}, %s)
                RETURNING id
            """, (user_id, name, typ, zusammenfassung, embedding_str,
                  suchtext_input, t_valid))
            entitaet_id: int = cursor.fetchone()[0]
            conn.commit()
            return entitaet_id
        finally:
            conn.close()

    @staticmethod
    def find_by_id(
        postgres_url: str,
        entitaet_id:  int,
    ) -> dict | None:
        """
        Entität per ID laden. Nur aktive Einträge.
        Setzt last_touched auf NOW().
        Gibt dict mit allen Spalten zurück oder None.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                UPDATE entitaeten
                SET last_touched = NOW()
                WHERE id = %s AND aktiv = TRUE
                RETURNING *
            """, (entitaet_id,))
            row = cursor.fetchone()
            conn.commit()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def find_by_user(
        postgres_url: str,
        user_id:      str,
    ) -> list[dict]:
        """
        Alle aktiven Entitäten eines Users laden.
        Setzt last_touched NICHT (Bulk-Abfrage).
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM entitaeten
                WHERE user_id = %s AND aktiv = TRUE
                ORDER BY name
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def find_by_type(
        postgres_url: str,
        user_id:      str,
        typ:          str,
    ) -> list[dict]:
        """Entitäten per Typ suchen (aktive). Für ICH→User-Auflösung."""
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM entitaeten
                WHERE user_id = %s AND lower(typ) = lower(%s) AND aktiv = TRUE
                ORDER BY id
            """, (user_id, typ))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def find_by_name(
        postgres_url: str,
        user_id:      str,
        name:         str,
    ) -> list[dict]:
        """
        Entitäten per Name suchen (case-insensitive, aktive).
        Setzt last_touched auf NOW() für alle Treffer.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                UPDATE entitaeten
                SET last_touched = NOW()
                WHERE user_id = %s AND lower(name) = lower(%s) AND aktiv = TRUE
                RETURNING *
            """, (user_id, name))
            rows = cursor.fetchall()
            conn.commit()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def find_similar(
        postgres_url: str,
        user_id:      str,
        embedding:    list[float],
        threshold:    float = 0.80,
        limit:        int = 5,
    ) -> list[dict]:
        """
        Ähnliche Entitäten per Embedding-Similarity suchen (aktive).
        Gibt Liste von dicts mit zusätzlichem Feld 'similarity' zurück.
        Sortiert nach Similarity absteigend.
        """
        embedding_str: str = "[" + ",".join(str(x) for x in embedding) + "]"

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT *,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM entitaeten
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
    def update_zusammenfassung(
        postgres_url:    str,
        entitaet_id:     int,
        zusammenfassung: str,
        embedding:       list[float] | None = None,
    ) -> None:
        """
        Zusammenfassung und optional Embedding aktualisieren.
        Setzt last_touched auf NOW(). Aktualisiert suchtext.
        """
        embedding_str: str | None = (
            "[" + ",".join(str(x) for x in embedding) + "]"
            if embedding else None
        )

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()

            if embedding_str:
                cursor.execute("""
                    UPDATE entitaeten
                    SET zusammenfassung = %s,
                        embedding = %s::vector,
                        suchtext = to_tsvector('german',
                            name || ' ' || typ || ' ' || %s),
                        last_touched = NOW()
                    WHERE id = %s
                """, (zusammenfassung, embedding_str, zusammenfassung, entitaet_id))
            else:
                cursor.execute("""
                    UPDATE entitaeten
                    SET zusammenfassung = %s,
                        suchtext = to_tsvector('german',
                            name || ' ' || typ || ' ' || %s),
                        last_touched = NOW()
                    WHERE id = %s
                """, (zusammenfassung, zusammenfassung, entitaet_id))

            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def update_embedding(
        postgres_url: str,
        entitaet_id:  int,
        embedding:    list[float],
    ) -> None:
        """Aktualisiert das Embedding einer Entität."""
        embedding_str: str = "[" + ",".join(str(x) for x in embedding) + "]"

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE entitaeten SET embedding = %s::vector WHERE id = %s",
                (embedding_str, entitaet_id),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def invalidate(
        postgres_url: str,
        entitaet_id:  int,
    ) -> None:
        """
        Entität invalidieren (Soft-Delete).
        Setzt aktiv=FALSE und t_invalid=NOW().
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE entitaeten
                SET aktiv = FALSE, t_invalid = NOW()
                WHERE id = %s
            """, (entitaet_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def reactivate(
        postgres_url: str,
        entitaet_id:  int,
    ) -> None:
        """
        Inaktive Entität reaktivieren.
        Setzt aktiv=TRUE, t_invalid=NULL, last_touched=NOW().
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE entitaeten
                SET aktiv = TRUE, t_invalid = NULL, last_touched = NOW()
                WHERE id = %s
            """, (entitaet_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def set_wiedervorlage(
        postgres_url:    str,
        entitaet_id:     int,
        wiedervorlage_am: datetime | None,
    ) -> None:
        """Wiedervorlage-Datum setzen oder löschen (None = unterdrücken)."""
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE entitaeten
                SET wiedervorlage_am = %s
                WHERE id = %s
            """, (wiedervorlage_am, entitaet_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def find_wiedervorlage_faellig(
        postgres_url: str,
        user_id:      str,
    ) -> list[dict]:
        """
        Alle Entitäten mit fälliger Wiedervorlage (wiedervorlage_am <= NOW()).
        Für den Butler-Task.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM entitaeten
                WHERE user_id = %s
                  AND aktiv = TRUE
                  AND wiedervorlage_am IS NOT NULL
                  AND wiedervorlage_am <= NOW()
                ORDER BY wiedervorlage_am
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
