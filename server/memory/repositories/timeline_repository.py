"""
Datenzugriffsschicht für die timeline-Tabelle.
Keine Business-Logik — reine CRUD-Operationen.

Timezone-Konvention:
  - DB speichert UTC (timestamptz)
  - Alle Methoden geben lokale Zeit zurück (config.TIMEZONE)
  - Alle Methoden empfangen lokale Zeit und konvertieren zu UTC vor dem Schreiben
  - Kein Consumer muss sich um Timezone-Konvertierung kümmern
"""

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import psycopg2
import psycopg2.extras

from config import TIMEZONE

logger = logging.getLogger("ki_server.memory.repositories.timeline")

_TZ_LOCAL = ZoneInfo(TIMEZONE)
_TZ_UTC   = ZoneInfo("UTC")


def _to_utc(dt: datetime) -> datetime:
    """Lokale Zeit → UTC für DB-Schreiboperationen."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_TZ_LOCAL)
    return dt.astimezone(_TZ_UTC)


def _rows_to_local(rows: list[dict]) -> list[dict]:
    """UTC aus DB → lokale Zeit für alle Rows mit event_time."""
    for row in rows:
        et = row.get("event_time")
        if et is not None:
            if et.tzinfo is None:
                et = et.replace(tzinfo=_TZ_UTC)
            row["event_time"] = et.astimezone(_TZ_LOCAL)
    return rows


def _row_to_local(row: dict) -> dict:
    """UTC aus DB → lokale Zeit für eine einzelne Row."""
    et = row.get("event_time")
    if et is not None:
        if et.tzinfo is None:
            et = et.replace(tzinfo=_TZ_UTC)
        row["event_time"] = et.astimezone(_TZ_LOCAL)
    return row


class TimelineRepository:
    """Datenzugriffsschicht für die timeline-Tabelle. Keine Business-Logik."""

    @staticmethod
    def insert(
        postgres_url:     str,
        user_id:          str,
        event_time:       "datetime | str",
        event_type:       str,
        title:            str,
        details:          str | None = None,
        recurring:        bool = False,
        precision:        str = "day",
        entitaet_ids:     list[int] | None = None,
        wiedervorlage_am: datetime | None = None,
        themen:           list[str] | None = None,
        binding:          bool = False,
        remind:           bool = False,
        conflict_check:   bool = False,
    ) -> int:
        """
        Neuen Termin anlegen. Gibt die neue ID zurück.
        Setzt last_touched auf NOW().
        Wenn wiedervorlage_am nicht gesetzt: automatisch event_time + 7 Tage.
        event_time kann ein datetime oder ein ISO-String sein.

        Magnet-Spalten (M2.5a):
          - themen=None   -> NULL (DB-Default greift), nicht leeres Array
          - binding/remind/conflict_check default False (sicherer Default)
        """
        # String → datetime konvertieren
        if isinstance(event_time, str):
            event_time = datetime.fromisoformat(event_time)

        if wiedervorlage_am is None and event_time:
            wiedervorlage_am = event_time + timedelta(days=7)

        # Lokale Zeit → UTC für DB
        event_time_utc = _to_utc(event_time)
        wiedervorlage_utc = _to_utc(wiedervorlage_am) if wiedervorlage_am else None

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO timeline
                    (user_id, event_time, event_type, title, details,
                     recurring, precision, entitaet_ids, wiedervorlage_am,
                     themen, binding, remind, conflict_check,
                     last_touched)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
            """, (user_id, event_time_utc, event_type, title, details,
                  recurring, precision, entitaet_ids, wiedervorlage_utc,
                  themen, binding, remind, conflict_check))
            termin_id: int = cursor.fetchone()[0]
            conn.commit()
            logger.info(
                f"TimelineRepository.insert: id={termin_id}, event_type='{event_type}', "
                f"themen={themen}, binding={binding}, remind={remind}, "
                f"conflict_check={conflict_check}"
            )
            return termin_id
        finally:
            conn.close()

    @staticmethod
    def find_by_id(
        postgres_url: str,
        termin_id:    int,
    ) -> dict | None:
        """
        Termin per ID laden. Nur aktive.
        Setzt last_touched auf NOW().
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                UPDATE timeline
                SET last_touched = NOW()
                WHERE id = %s AND aktiv = TRUE
                RETURNING *
            """, (termin_id,))
            row = cursor.fetchone()
            conn.commit()
            return _row_to_local(dict(row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def find_by_date_range(
        postgres_url: str,
        user_id:      str,
        von:          datetime,
        bis:          datetime,
    ) -> list[dict]:
        """
        Termine in einem Zeitraum laden (aktive).
        Für Enricher-Kontext und Konflikt-Check.
        """
        von_utc = _to_utc(von)
        bis_utc = _to_utc(bis)

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM timeline
                WHERE user_id = %s
                  AND aktiv = TRUE
                  AND event_time BETWEEN %s AND %s
                ORDER BY event_time
            """, (user_id, von_utc, bis_utc))
            return _rows_to_local([dict(row) for row in cursor.fetchall()])
        finally:
            conn.close()

    @staticmethod
    def find_by_date(
        postgres_url: str,
        user_id:      str,
        datum:        datetime,
        precision:    str = "day",
    ) -> list[dict]:
        """
        Termine an einem bestimmten Tag laden (aktive).
        Bei precision="day": alle Termine des Tages.
        Bei precision="time": exakter Match auf Stunde/Minute.
        """
        # Lokalen Tag → UTC-Range konvertieren (korrekt über Mitternacht)
        if datum.tzinfo is None:
            datum = datum.replace(tzinfo=_TZ_LOCAL)
        tag_start = datum.replace(hour=0, minute=0, second=0, microsecond=0)
        tag_ende  = datum.replace(hour=23, minute=59, second=59, microsecond=999999)

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            if precision == "day":
                cursor.execute("""
                    SELECT * FROM timeline
                    WHERE user_id = %s
                      AND aktiv = TRUE
                      AND event_time BETWEEN %s AND %s
                    ORDER BY event_time
                """, (user_id, tag_start.astimezone(_TZ_UTC), tag_ende.astimezone(_TZ_UTC)))
            else:
                datum_utc = _to_utc(datum)
                cursor.execute("""
                    SELECT * FROM timeline
                    WHERE user_id = %s
                      AND aktiv = TRUE
                      AND event_time BETWEEN %s AND %s
                      AND EXTRACT(HOUR FROM event_time AT TIME ZONE %s) = %s
                      AND EXTRACT(MINUTE FROM event_time AT TIME ZONE %s) = %s
                    ORDER BY event_time
                """, (user_id,
                      tag_start.astimezone(_TZ_UTC), tag_ende.astimezone(_TZ_UTC),
                      TIMEZONE, datum.hour,
                      TIMEZONE, datum.minute))

            return _rows_to_local([dict(row) for row in cursor.fetchall()])
        finally:
            conn.close()

    @staticmethod
    def find_by_entitaet(
        postgres_url: str,
        user_id:      str,
        entitaet_id:  int,
    ) -> list[dict]:
        """
        Alle Termine mit einer bestimmten Entität (aktive).
        "Wann treffe ich Julia das nächste Mal?"
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM timeline
                WHERE user_id = %s
                  AND aktiv = TRUE
                  AND %s = ANY(entitaet_ids)
                ORDER BY event_time
            """, (user_id, entitaet_id))
            return _rows_to_local([dict(row) for row in cursor.fetchall()])
        finally:
            conn.close()

    @staticmethod
    def update(
        postgres_url:   str,
        termin_id:      int,
        event_time:     datetime | None = None,
        title:          str | None = None,
        details:        str | None = None,
        entitaet_ids:   list[int] | None = None,
    ) -> None:
        """
        Termin aktualisieren. Nur übergebene Felder werden geändert.
        Setzt last_touched auf NOW().
        """
        updates: list[str] = ["last_touched = NOW()"]
        params:  list      = []

        if event_time is not None:
            updates.append("event_time = %s")
            params.append(_to_utc(event_time))
        if title is not None:
            updates.append("title = %s")
            params.append(title)
        if details is not None:
            updates.append("details = %s")
            params.append(details)
        if entitaet_ids is not None:
            updates.append("entitaet_ids = %s")
            params.append(entitaet_ids)

        params.append(termin_id)

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE timeline SET {', '.join(updates)} WHERE id = %s",
                params
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def invalidate(
        postgres_url: str,
        termin_id:    int,
    ) -> None:
        """Termin deaktivieren (Soft-Delete). Setzt aktiv=FALSE."""
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE timeline
                SET aktiv = FALSE
                WHERE id = %s
            """, (termin_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def set_wiedervorlage(
        postgres_url:    str,
        termin_id:       int,
        wiedervorlage_am: datetime | None,
    ) -> None:
        """Wiedervorlage-Datum setzen oder löschen (None = unterdrücken)."""
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE timeline
                SET wiedervorlage_am = %s
                WHERE id = %s
            """, (wiedervorlage_am, termin_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def find_wiedervorlage_faellig(
        postgres_url: str,
        user_id:      str,
    ) -> list[dict]:
        """
        Alle Termine mit fälliger Wiedervorlage (wiedervorlage_am <= NOW()).
        Für den Butler-Task.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM timeline
                WHERE user_id = %s
                  AND aktiv = TRUE
                  AND wiedervorlage_am IS NOT NULL
                  AND wiedervorlage_am <= NOW()
                ORDER BY wiedervorlage_am
            """, (user_id,))
            return _rows_to_local([dict(row) for row in cursor.fetchall()])
        finally:
            conn.close()

    @staticmethod
    def find_by_keyword(
        postgres_url: str,
        user_id:      str,
        keyword:      str,
        direction:    str = "forward",
        limit:        int = 5,
    ) -> list[dict]:
        """
        Keyword-Suche (ILIKE auf title) mit Zeitrichtung.
        direction: forward | backward | both
        Nur aktive Einträge.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            search: str = f"%{keyword}%"

            if direction == "forward":
                cursor.execute("""
                    SELECT * FROM timeline
                    WHERE user_id = %s AND aktiv = TRUE
                      AND title ILIKE %s AND event_time >= NOW()
                    ORDER BY event_time ASC
                    LIMIT %s
                """, (user_id, search, limit))
            elif direction == "backward":
                cursor.execute("""
                    SELECT * FROM timeline
                    WHERE user_id = %s AND aktiv = TRUE
                      AND title ILIKE %s AND event_time <= NOW()
                    ORDER BY event_time DESC
                    LIMIT %s
                """, (user_id, search, limit))
            else:
                cursor.execute("""
                    SELECT * FROM timeline
                    WHERE user_id = %s AND aktiv = TRUE
                      AND title ILIKE %s
                    ORDER BY event_time
                    LIMIT %s
                """, (user_id, search, limit))

            return _rows_to_local([dict(row) for row in cursor.fetchall()])
        finally:
            conn.close()

    @staticmethod
    def find_vergangene_ohne_wiedervorlage(
        postgres_url: str,
        user_id:      str,
        tage_zurueck: int = 7,
    ) -> list[dict]:
        """
        Vergangene Termine ohne Wiedervorlage-Datum.
        Für initiale Wiedervorlage-Berechnung.
        """
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM timeline
                WHERE user_id = %s
                  AND aktiv = TRUE
                  AND event_time < NOW()
                  AND event_time >= NOW() - INTERVAL '%s days'
                  AND wiedervorlage_am IS NULL
                ORDER BY event_time DESC
            """, (user_id, tage_zurueck))
            return _rows_to_local([dict(row) for row in cursor.fetchall()])
        finally:
            conn.close()
