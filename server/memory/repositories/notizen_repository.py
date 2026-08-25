"""
Datenzugriffsschicht für die notizen-Tabelle.
Keine Business-Logik — reine CRUD-Operationen.
"""

import logging
from datetime import datetime

import psycopg2
import psycopg2.extras

logger = logging.getLogger("ki_server.memory.repositories.notizen")


class NotizenRepository:
    """Datenzugriffsschicht für die notizen-Tabelle. Keine Business-Logik."""

    @staticmethod
    def insert(
        postgres_url:     str,
        user_id:          str,
        name:             str,
        typ:              str,
        text:             str,
        zusammenfassung:  str | None = None,
        themen:           list[str] | None = None,
        entitaet_ids:     list[int] | None = None,
        faellig_am:       datetime | None = None,
        wiedervorlage_am: datetime | None = None,
    ) -> int:
        """
        Neue Notiz anlegen. Gibt die neue ID zurück.
        Setzt last_touched auf NOW().
        Befüllt suchtext per to_tsvector('german', name || ' ' || zusammenfassung).
        Wenn wiedervorlage_am nicht gesetzt: automatisch created_at + 30 Tage.
        """
        suchtext_input: str = " ".join(filter(None, [name, zusammenfassung or ""]))

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notizen
                    (user_id, name, typ, text, zusammenfassung, themen,
                     entitaet_ids, faellig_am, wiedervorlage_am,
                     last_touched, aktiv, suchtext)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                        COALESCE(%s, NOW() + INTERVAL '30 days'),
                        NOW(), TRUE,
                        to_tsvector('german', %s))
                RETURNING id
            """, (user_id, name, typ, text, zusammenfassung, themen,
                  entitaet_ids, faellig_am, wiedervorlage_am,
                  suchtext_input))
            notiz_id: int = cursor.fetchone()[0]
            conn.commit()
            return notiz_id
        finally:
            conn.close()

    @staticmethod
    def find_by_id(
        postgres_url: str,
        notiz_id:     int,
    ) -> dict | None:
        """
        Notiz per ID laden. Nur aktive.
        Setzt last_touched auf NOW().
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                UPDATE notizen
                SET last_touched = NOW()
                WHERE id = %s AND aktiv = TRUE
                RETURNING *
            """, (notiz_id,))
            row = cursor.fetchone()
            conn.commit()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def find_by_stichwort(
        postgres_url: str,
        user_id:      str,
        stichwort:    str,
    ) -> list[dict]:
        """
        Notizen per Stichwort suchen (case-insensitive auf name, aktive).
        Setzt last_touched auf NOW() für alle Treffer.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                UPDATE notizen
                SET last_touched = NOW()
                WHERE user_id = %s AND lower(name) = lower(%s) AND aktiv = TRUE
                RETURNING *
            """, (user_id, stichwort))
            rows = cursor.fetchall()
            conn.commit()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def find_by_volltext(
        postgres_url: str,
        user_id:      str,
        suchbegriff:  str,
    ) -> list[dict]:
        """
        Volltextsuche über suchtext-Spalte (name + zusammenfassung).
        Nur aktive Einträge.
        Setzt last_touched auf NOW() für alle Treffer.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                UPDATE notizen
                SET last_touched = NOW()
                WHERE user_id = %s
                  AND aktiv = TRUE
                  AND suchtext @@ plainto_tsquery('german', %s)
                RETURNING *
            """, (user_id, suchbegriff))
            rows = cursor.fetchall()
            conn.commit()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def find_by_thema(
        postgres_url: str,
        user_id:      str,
        thema:        str,
    ) -> list[dict]:
        """
        Notizen per Thema suchen.
        Nutzt: WHERE %s = ANY(themen)
        Nur aktive.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM notizen
                WHERE user_id = %s
                  AND aktiv = TRUE
                  AND %s = ANY(themen)
                ORDER BY updated_at DESC
            """, (user_id, thema))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def find_by_user(
        postgres_url: str,
        user_id:      str,
    ) -> list[dict]:
        """
        Alle aktiven Notizen eines Users laden.
        Setzt last_touched NICHT (Bulk-Abfrage).
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM notizen
                WHERE user_id = %s AND aktiv = TRUE
                ORDER BY updated_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def update(
        postgres_url:    str,
        notiz_id:        int,
        name:            str | None = None,
        text:            str | None = None,
        zusammenfassung: str | None = None,
        themen:          list[str] | None = None,
        entitaet_ids:    list[int] | None = None,
        faellig_am:      datetime | None = None,
    ) -> None:
        """
        Notiz aktualisieren. Nur übergebene Felder werden geändert.
        Setzt last_touched auf NOW() und updated_at auf NOW().
        Aktualisiert suchtext wenn name oder zusammenfassung geändert.
        """
        updates: list[str] = ["last_touched = NOW()", "updated_at = NOW()"]
        params:  list      = []

        suchtext_update: bool = False

        if name is not None:
            updates.append("name = %s")
            params.append(name)
            suchtext_update = True
        if text is not None:
            updates.append("text = %s")
            params.append(text)
        if zusammenfassung is not None:
            updates.append("zusammenfassung = %s")
            params.append(zusammenfassung)
            suchtext_update = True
        if themen is not None:
            updates.append("themen = %s")
            params.append(themen)
        if entitaet_ids is not None:
            updates.append("entitaet_ids = %s")
            params.append(entitaet_ids)
        if faellig_am is not None:
            updates.append("faellig_am = %s")
            params.append(faellig_am)

        if suchtext_update:
            updates.append(
                "suchtext = to_tsvector('german', "
                "COALESCE(name, '') || ' ' || COALESCE(zusammenfassung, ''))"
            )

        params.append(notiz_id)

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE notizen SET {', '.join(updates)} WHERE id = %s",
                params
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def invalidate(
        postgres_url: str,
        notiz_id:     int,
    ) -> None:
        """Notiz deaktivieren (Soft-Delete). Setzt aktiv=FALSE."""
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notizen
                SET aktiv = FALSE
                WHERE id = %s
            """, (notiz_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def set_wiedervorlage(
        postgres_url:    str,
        notiz_id:        int,
        wiedervorlage_am: datetime | None,
    ) -> None:
        """Wiedervorlage-Datum setzen oder löschen (None = unterdrücken)."""
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notizen
                SET wiedervorlage_am = %s
                WHERE id = %s
            """, (wiedervorlage_am, notiz_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def find_wiedervorlage_faellig(
        postgres_url: str,
        user_id:      str,
    ) -> list[dict]:
        """
        Alle Notizen mit fälliger Wiedervorlage (wiedervorlage_am <= NOW()).
        Für den Butler-Task.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM notizen
                WHERE user_id = %s
                  AND aktiv = TRUE
                  AND wiedervorlage_am IS NOT NULL
                  AND wiedervorlage_am <= NOW()
                ORDER BY wiedervorlage_am
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
