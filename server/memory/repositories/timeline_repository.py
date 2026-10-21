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


def _excluded_types(exclude_event_types: tuple[str, ...]) -> list[str]:
    """Die auszuschliessenden Typen als Parameter einer Abfrage.

    Die Klausel `COALESCE(event_type, '') <> ALL(%s::text[])` laesst bei einer
    leeren Liste alles durch. Das `COALESCE` haelt eine Zeile ohne Typ im
    Ergebnis, falls ein Altbestand sie traegt — `NULL <> 'x'` waere unbekannt
    und schloesse sie still aus (das Schema sagt `NOT NULL`,
    `agents/timeline/init.sql`; die Klausel verlaesst sich nicht darauf).

    Vorbedingung: ein Tupel von Texten, moeglicherweise leer.
    Nachbedingung: dieselben Texte als Liste (psycopg2 bildet sie auf ein
        Array ab).
    Fehlerfaelle: ein anderer Typ als Tupel oder ein Element, das kein
        nicht leerer Text ist, wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(exclude_event_types, tuple):
        msg: str = f"exclude_event_types ist kein tuple: {type(exclude_event_types).__name__}"
        raise TypeError(msg)
    if not all(isinstance(t, str) and t for t in exclude_event_types):
        msg = f"exclude_event_types traegt einen leeren oder fremden Wert: {exclude_event_types!r}"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    excluded: list[str] = list(exclude_event_types)

    # ── Ausgabe-Verifikation ────────────────────
    if len(excluded) != len(exclude_event_types):
        msg = "exclude_event_types: Laenge nach der Umwandlung verschieden"
        raise RuntimeError(msg)
    return excluded


def _check_pair(method: str, user_id: object, character_id: object) -> None:
    """Prueft das Paar, bevor eine Abfrage es benutzt.

    Ein Termin gehoert dem Paar aus Mensch und Figur. Eine Abfrage ohne Figur
    laese ueber alle Figuren des Menschen hinweg, ein Schreiben ohne Figur
    scheiterte erst in der Datenbank — beides wird hier verworfen, bevor eine
    Verbindung entsteht. Es gibt keine Vorgabe-Figur.

    Vorbedingung: `method` nennt die rufende Methode fuer die Meldung.
    Nachbedingung: beide Teile sind nicht leere Texte.
    Fehlerfaelle: ein leerer Teil oder ein anderer Typ als Text wirft
        `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    for value in (user_id, character_id):
        if not isinstance(value, str) or not value.strip():
            msg: str = (
                f"TimelineRepository.{method}: Paar unvollstaendig (user_id={user_id!r}, "
                f"character_id={character_id!r}) — keine Abfrage ohne Paar"
            )
            raise ValueError(msg)


#: Die Suche mit der Grenze *vergangen*, wie `memory/timeline_reading.py::
#: to_appointment` sie zieht: mit Uhrzeit vor dem Zeitpunkt, ohne Uhrzeit vor
#: dem Beginn des Tages. Beide Abfragen tragen dieselbe `CASE`-Klausel, einmal
#: verneint; ihre Parameter liefert `_past_bounds`.
_KEYWORD_COMING_SQL: str = """
    SELECT * FROM timeline
    WHERE user_id = %s AND character_id = %s AND aktiv = TRUE
      AND title ILIKE %s
      AND NOT (CASE WHEN COALESCE(precision, '') = ANY(%s::text[])
                    THEN event_time < %s ELSE event_time < %s END)
      AND COALESCE(event_type, '') <> ALL(%s::text[])
    ORDER BY event_time ASC
    LIMIT %s
"""

_KEYWORD_PAST_SQL: str = """
    SELECT * FROM timeline
    WHERE user_id = %s AND character_id = %s AND aktiv = TRUE
      AND title ILIKE %s
      AND (CASE WHEN COALESCE(precision, '') = ANY(%s::text[])
                THEN event_time < %s ELSE event_time < %s END)
      AND COALESCE(event_type, '') <> ALL(%s::text[])
    ORDER BY event_time DESC
    LIMIT %s
"""


def _past_bounds(
    now: datetime, timed_precisions: frozenset[str],
) -> tuple[list[str], datetime, datetime]:
    """Die Parameter der Grenze *vergangen* in `_KEYWORD_COMING_SQL` und `_KEYWORD_PAST_SQL`.

    Der Tagesbeginn liegt in der Zone von `now`, denn `to_appointment`
    vergleicht das Datum in Ortszeit. Ein Termin ohne Uhrzeit von heute ist
    damit weder vergangen noch faellt er aus einer Suche nach Kommendem.

    Vorbedingung: `now` zeitzonenbewusst; `timed_precisions` ein nicht leeres
        frozenset nicht leerer Texte.
    Nachbedingung: (Genauigkeiten als Liste, `now` in UTC, Tagesbeginn in
        UTC), der Tagesbeginn nicht nach `now`.
    Fehlerfaelle: ein naiver Zeitpunkt wirft `ValueError`; eine leere oder
        fremde Menge wirft `TypeError` — beides vor der Verbindung.
    """
    # ── Eingabe-Validierung ─────────────────────
    if now.tzinfo is None:
        msg: str = "_past_bounds: Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)
    valid: bool = isinstance(timed_precisions, frozenset) and bool(timed_precisions)
    if not valid or not all(isinstance(p, str) and p for p in timed_precisions):
        msg = f"timed_precisions ist kein nicht leeres frozenset von Texten: {timed_precisions!r}"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    day_start: datetime = now.replace(hour=0, minute=0, second=0, microsecond=0)
    bounds: tuple[list[str], datetime, datetime] = (
        sorted(timed_precisions), now.astimezone(_TZ_UTC), day_start.astimezone(_TZ_UTC),
    )

    # ── Ausgabe-Verifikation ────────────────────
    if bounds[2] > bounds[1]:
        msg = f"_past_bounds: Tagesbeginn {bounds[2]} nach dem Zeitpunkt {bounds[1]}"
        raise RuntimeError(msg)
    return bounds


class TimelineRepository:
    """Datenzugriffsschicht für die timeline-Tabelle. Keine Business-Logik."""

    @staticmethod
    def insert(  # noqa: PLR0913, PLR0917 — eine Spalte der Tabelle je Argument
        postgres_url:     str,
        user_id:          str,
        character_id:     str,
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
        event_ende:       datetime | None = None,
    ) -> int:
        """
        Neuen Termin anlegen. Gibt die neue ID zurück.
        Setzt last_touched auf NOW().
        Wenn wiedervorlage_am nicht gesetzt: automatisch event_time + 7 Tage.
        event_time kann ein datetime oder ein ISO-String sein.

        Magnet-Spalten (M2.5a):
          - themen=None   -> NULL (DB-Default greift), nicht leeres Array
          - binding/remind/conflict_check default False (sicherer Default)

        Der Termin gehoert dem Paar (`user_id`, `character_id`); ohne einen
        Teil davon wirft die Methode `ValueError`, bevor eine Verbindung
        entsteht.

        Vorbedingung: `user_id` und `character_id` nicht leere Texte;
            `event_time` ein datetime oder ein ISO-Text.
        Nachbedingung: genau eine Zeile des Paares ist geschrieben und
            committet; zurueck kommt ihre `id` aus `RETURNING`.
        """
        _check_pair("insert", user_id, character_id)
        # String → datetime konvertieren
        if isinstance(event_time, str):
            event_time = datetime.fromisoformat(event_time)

        if wiedervorlage_am is None and event_time:
            wiedervorlage_am = event_time + timedelta(days=7)

        # Lokale Zeit → UTC für DB
        event_time_utc = _to_utc(event_time)
        wiedervorlage_utc = _to_utc(wiedervorlage_am) if wiedervorlage_am else None
        # Scheibe 12 D (18.09.2026): das Ende einer Spanne, wo eine genannt ist.
        ende_utc = _to_utc(event_ende) if event_ende else None

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO timeline
                    (user_id, character_id, event_time, event_type, title, details,
                     recurring, precision, entitaet_ids, wiedervorlage_am,
                     themen, binding, remind, conflict_check, event_ende,
                     last_touched)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
            """, (user_id, character_id, event_time_utc, event_type, title, details,
                  recurring, precision, entitaet_ids, wiedervorlage_utc,
                  themen, binding, remind, conflict_check, ende_utc))
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
    def find_by_date_range(  # noqa: PLR0913, PLR0917 — das Paar steht als zwei Argumente
        postgres_url: str,
        user_id:      str,
        character_id: str,
        von:          datetime,
        bis:          datetime,
        exclude_event_types: tuple[str, ...] = (),
    ) -> list[dict]:
        """
        Termine in einem Zeitraum laden (aktive).
        Für Enricher-Kontext und Konflikt-Check.

        `exclude_event_types` schliesst Typen in der Abfrage aus (etwa den
        Erinnerungs-Anker) — leer laesst alles durch.

        Vorbedingung: `von` und `bis` sind Zeitpunkte, ohne Zone gelten sie
            als Ortszeit; `exclude_event_types` ein Tupel nicht leerer Texte.
        Nachbedingung: alle aktiven Zeilen des Paares (`user_id`,
            `character_id`) mit `event_time` zwischen `von` und `bis` (beide
            eingeschlossen), deren Typ nicht ausgeschlossen ist, aufsteigend
            nach Zeit, `event_time` in Ortszeit.
        Fehlerfaelle: ein unvollstaendiges Paar wirft `ValueError`, ein
            falscher `exclude_event_types` `TypeError` — beides vor der
            Verbindung; ein Fehler der Datenbank steigt unveraendert auf, die
            Verbindung wird geschlossen.
        """
        _check_pair("find_by_date_range", user_id, character_id)
        excluded: list[str] = _excluded_types(exclude_event_types)
        von_utc = _to_utc(von)
        bis_utc = _to_utc(bis)

        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM timeline
                WHERE user_id = %s AND character_id = %s
                  AND aktiv = TRUE
                  AND event_time BETWEEN %s AND %s
                  AND COALESCE(event_type, '') <> ALL(%s::text[])
                ORDER BY event_time
            """, (user_id, character_id, von_utc, bis_utc, excluded))
            return _rows_to_local([dict(row) for row in cursor.fetchall()])
        finally:
            conn.close()

    @staticmethod
    def find_by_date(
        postgres_url: str,
        user_id:      str,
        character_id: str,
        datum:        datetime,
        precision:    str = "day",
    ) -> list[dict]:
        """
        Termine des Paares an einem bestimmten Tag laden (aktive).
        Bei precision="day": alle Termine des Tages.
        Bei precision="time": exakter Match auf Stunde/Minute.
        Ein unvollstaendiges Paar wirft `ValueError` vor der Verbindung.
        """
        _check_pair("find_by_date", user_id, character_id)
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
                    WHERE user_id = %s AND character_id = %s
                      AND aktiv = TRUE
                      AND event_time BETWEEN %s AND %s
                    ORDER BY event_time
                """, (user_id, character_id,
                      tag_start.astimezone(_TZ_UTC), tag_ende.astimezone(_TZ_UTC)))
            else:
                cursor.execute("""
                    SELECT * FROM timeline
                    WHERE user_id = %s AND character_id = %s
                      AND aktiv = TRUE
                      AND event_time BETWEEN %s AND %s
                      AND EXTRACT(HOUR FROM event_time AT TIME ZONE %s) = %s
                      AND EXTRACT(MINUTE FROM event_time AT TIME ZONE %s) = %s
                    ORDER BY event_time
                """, (user_id, character_id,
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
        character_id: str,
        entitaet_id:  int,
    ) -> list[dict]:
        """
        Alle Termine des Paares mit einer bestimmten Entität (aktive).
        "Wann treffe ich Julia das nächste Mal?".
        Ein unvollstaendiges Paar wirft `ValueError` vor der Verbindung.
        """
        _check_pair("find_by_entitaet", user_id, character_id)
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM timeline
                WHERE user_id = %s AND character_id = %s
                  AND aktiv = TRUE
                  AND %s = ANY(entitaet_ids)
                ORDER BY event_time
            """, (user_id, character_id, entitaet_id))
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
        character_id: str,
    ) -> list[dict]:
        """
        Alle Termine des Paares mit fälliger Wiedervorlage (wiedervorlage_am <= NOW()).
        Für den Butler-Task.
        Ein unvollstaendiges Paar wirft `ValueError` vor der Verbindung.
        """
        _check_pair("find_wiedervorlage_faellig", user_id, character_id)
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM timeline
                WHERE user_id = %s AND character_id = %s
                  AND aktiv = TRUE
                  AND wiedervorlage_am IS NOT NULL
                  AND wiedervorlage_am <= NOW()
                ORDER BY wiedervorlage_am
            """, (user_id, character_id))
            return _rows_to_local([dict(row) for row in cursor.fetchall()])
        finally:
            conn.close()

    @staticmethod
    def find_by_keyword(  # noqa: PLR0913, PLR0917 — Paar und Typausschluss gehoeren in die Abfrage
        postgres_url: str,
        user_id:      str,
        character_id: str,
        keyword:      str,
        direction:    str = "forward",
        limit:        int = 5,
        *,
        exclude_event_types: tuple[str, ...] = (),
        now:                 datetime | None = None,
        timed_precisions:    frozenset[str] = frozenset(),
    ) -> list[dict]:
        """
        Keyword-Suche (ILIKE auf title) mit Zeitrichtung.
        direction: forward | backward | both
        Nur aktive Einträge.

        `exclude_event_types` schliesst Typen in der Abfrage aus, vor dem
        LIMIT — ein Ausschluss dahinter vergaebe Plaetze an Verworfenes.
        Aus demselben Grund grenzt `now` *vergangen* in der Abfrage so ab wie
        der Leser dahinter: mit Uhrzeit (`timed_precisions`) vor `now`, ohne
        Uhrzeit vor dem Beginn des Tages von `now`. Ohne `now` gilt `NOW()`.

        Vorbedingung: `keyword` ist der Suchtext ohne Platzhalter; `direction`
            ist `forward`, `backward` oder `both` — jeder andere Wert sucht wie
            `both`; `exclude_event_types` ein Tupel nicht leerer Texte; ist
            `now` gesetzt, ist es zeitzonenbewusst und `timed_precisions`
            nicht leer.
        Nachbedingung: hoechstens `limit` aktive Zeilen des Paares
            (`user_id`, `character_id`), deren Titel `keyword` enthaelt und
            deren Typ nicht ausgeschlossen ist, `event_time` in Ortszeit; bei
            `forward` aufsteigend, nicht vergangen, bei `backward` absteigend,
            vergangen, sonst aufsteigend. Ohne `now` heisst vergangen:
            `event_time` vor bzw. bis `NOW()`.
        Fehlerfaelle: ein falscher `exclude_event_types` oder
            `timed_precisions` wirft `TypeError`, ein naives `now` oder ein
            unvollstaendiges Paar `ValueError` — alles vor der Verbindung; ein
            Fehler der Datenbank steigt unveraendert auf, die Verbindung wird
            geschlossen.
        """
        _check_pair("find_by_keyword", user_id, character_id)
        excluded: list[str] = _excluded_types(exclude_event_types)
        bounds: tuple | None = None if now is None else _past_bounds(now, timed_precisions)
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            search: str = f"%{keyword}%"

            if bounds is not None and direction in ("forward", "backward"):
                query: str = _KEYWORD_COMING_SQL if direction == "forward" else _KEYWORD_PAST_SQL
                cursor.execute(query, (user_id, character_id, search, *bounds, excluded, limit))
            elif direction == "forward":
                cursor.execute("""
                    SELECT * FROM timeline
                    WHERE user_id = %s AND character_id = %s AND aktiv = TRUE
                      AND title ILIKE %s AND event_time >= NOW()
                      AND COALESCE(event_type, '') <> ALL(%s::text[])
                    ORDER BY event_time ASC
                    LIMIT %s
                """, (user_id, character_id, search, excluded, limit))
            elif direction == "backward":
                cursor.execute("""
                    SELECT * FROM timeline
                    WHERE user_id = %s AND character_id = %s AND aktiv = TRUE
                      AND title ILIKE %s AND event_time <= NOW()
                      AND COALESCE(event_type, '') <> ALL(%s::text[])
                    ORDER BY event_time DESC
                    LIMIT %s
                """, (user_id, character_id, search, excluded, limit))
            else:
                cursor.execute("""
                    SELECT * FROM timeline
                    WHERE user_id = %s AND character_id = %s AND aktiv = TRUE
                      AND title ILIKE %s
                      AND COALESCE(event_type, '') <> ALL(%s::text[])
                    ORDER BY event_time
                    LIMIT %s
                """, (user_id, character_id, search, excluded, limit))

            return _rows_to_local([dict(row) for row in cursor.fetchall()])
        finally:
            conn.close()

    @staticmethod
    def find_vergangene_ohne_wiedervorlage(
        postgres_url: str,
        user_id:      str,
        character_id: str,
        tage_zurueck: int = 7,
    ) -> list[dict]:
        """
        Vergangene Termine des Paares ohne Wiedervorlage-Datum.
        Für initiale Wiedervorlage-Berechnung.
        Ein unvollstaendiges Paar wirft `ValueError` vor der Verbindung.
        """
        _check_pair("find_vergangene_ohne_wiedervorlage", user_id, character_id)
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM timeline
                WHERE user_id = %s AND character_id = %s
                  AND aktiv = TRUE
                  AND event_time < NOW()
                  AND event_time >= NOW() - INTERVAL '%s days'
                  AND wiedervorlage_am IS NULL
                ORDER BY event_time DESC
            """, (user_id, character_id, tage_zurueck))
            return _rows_to_local([dict(row) for row in cursor.fetchall()])
        finally:
            conn.close()
