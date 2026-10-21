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


#: Die Spalten, die ein neuer Eintrag traegt; `last_touched` setzt die Abfrage.
_INSERT_COLUMNS: tuple[str, ...] = (
    "user_id", "character_id", "event_time", "event_type", "title", "details",
    "recurring", "precision", "entitaet_ids", "wiedervorlage_am",
    "themen", "binding", "remind", "conflict_check", "event_ende",
)

_COLUMN_LIST: str = ", ".join(_INSERT_COLUMNS)
_PLACEHOLDERS: str = ", ".join(["%s"] * len(_INSERT_COLUMNS))
# Eingesetzt werden nur die Konstanten oben; die Werte gehen als Parameter.
_INSERT_SQL: str = (
    f"INSERT INTO timeline ({_COLUMN_LIST}, last_touched) "  # noqa: S608
    f"VALUES ({_PLACEHOLDERS}, NOW()) RETURNING id"
)

#: Wie viele Nachfolger `aktive_zeile` hoechstens verfolgt. Eine laengere
#: Kette entsteht durch zehn Verschiebungen desselben Termins nicht — sie ist
#: ein Defekt, kein Bestand.
MAX_SUCCESSOR_DEPTH: int = 10

#: Die Kette der Nachfolger ab einer Zeile, eine Stufe ueber die Grenze hinaus,
#: damit eine zu lange Kette sichtbar wird. `cycle` markiert eine Zeile, die
#: schon im Pfad steht; dort endet die Rekursion.
_CHAIN_SQL: str = """
    WITH RECURSIVE chain (id, nachfolger_id, depth, path, cycle) AS (
        SELECT id, nachfolger_id, 0, ARRAY[id], FALSE
        FROM timeline WHERE id = %s
      UNION ALL
        SELECT t.id, t.nachfolger_id, c.depth + 1, c.path || t.id, t.id = ANY(c.path)
        FROM timeline t JOIN chain c ON t.id = c.nachfolger_id
        WHERE NOT c.cycle AND c.depth <= %s
    )
    SELECT id, nachfolger_id, depth, cycle FROM chain ORDER BY depth DESC LIMIT 1
"""


def _insert_row(cursor: "psycopg2.extensions.cursor", values: dict) -> int:
    """Schreibt eine Zeile in `timeline`, ohne zu committen.

    Geteilt von `insert` und `verschieben`: Das Commit gehoert dem Aufrufer,
    damit `verschieben` die neue Zeile und das Ablegen der alten in einer
    Transaktion haelt.

    Vorbedingung: `values` traegt genau die Schluessel `_INSERT_COLUMNS`,
        Zeitpunkte schon in UTC.
    Nachbedingung: die Zeile steht in der offenen Transaktion; zurueck kommt
        ihre `id`.
    Fehlerfaelle: fehlende oder fremde Schluessel werfen `KeyError` vor der
        Abfrage; eine Abfrage ohne `id` wirft `RuntimeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if set(values) != set(_INSERT_COLUMNS):
        msg: str = (
            f"_insert_row: Spalten passen nicht — fehlend "
            f"{sorted(set(_INSERT_COLUMNS) - set(values))}, fremd "
            f"{sorted(set(values) - set(_INSERT_COLUMNS))}"
        )
        raise KeyError(msg)

    # ── Verarbeitung ────────────────────────────
    cursor.execute(_INSERT_SQL, tuple(values[column] for column in _INSERT_COLUMNS))
    row: tuple | None = cursor.fetchone()

    # ── Ausgabe-Verifikation ────────────────────
    if row is None or not isinstance(row[0], int):
        msg = f"_insert_row: INSERT lieferte keine id ({row!r})"
        raise RuntimeError(msg)
    return row[0]


def _lock_active_row(cursor: "psycopg2.extensions.cursor", termin_id: int) -> dict:
    """Liest eine aktive Zeile und sperrt sie bis zum Ende der Transaktion.

    Die Sperre haelt ein zweites Verschieben derselben Zeile an, bis das
    erste committet ist; danach findet es sie inaktiv.

    Vorbedingung: `cursor` liefert Zeilen als Woerterbuch (`RealDictCursor`).
    Nachbedingung: die Zeile als `dict`, `aktiv` ist wahr.
    Fehlerfaelle: eine unbekannte oder inaktive Zeile wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(cursor, psycopg2.extras.RealDictCursor):
        msg: str = f"_lock_active_row: kein RealDictCursor ({type(cursor).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    cursor.execute("SELECT * FROM timeline WHERE id = %s FOR UPDATE", (termin_id,))
    row: dict | None = cursor.fetchone()

    # ── Ausgabe-Verifikation ────────────────────
    if row is None:
        msg = f"Termin {termin_id} gibt es nicht"
        raise ValueError(msg)
    if not row["aktiv"]:
        msg = f"Termin {termin_id} ist nicht aktiv (Nachfolger {row['nachfolger_id']})"
        raise ValueError(msg)
    return dict(row)


def _retire_row(cursor: "psycopg2.extensions.cursor", old_id: int, new_id: int) -> None:
    """Legt die alte Zeile ab und laesst sie auf ihren Nachfolger zeigen, ohne zu committen.

    Vorbedingung: beide Zeilen stehen in der offenen Transaktion, die alte ist
        gesperrt und aktiv.
    Nachbedingung: die alte Zeile ist inaktiv, `nachfolger_id = new_id`.
    Fehlerfaelle: trifft das UPDATE nicht genau eine Zeile, wirft es
        `RuntimeError` — der Aufrufer rollt dann beide Schritte zurueck.
    """
    # ── Eingabe-Validierung ─────────────────────
    if old_id == new_id:
        msg: str = f"_retire_row: Termin {old_id} kann nicht sein eigener Nachfolger sein"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    cursor.execute(
        """UPDATE timeline
           SET aktiv = FALSE, nachfolger_id = %s, last_touched = NOW()
           WHERE id = %s AND aktiv = TRUE""",
        (new_id, old_id),
    )

    # ── Ausgabe-Verifikation ────────────────────
    if cursor.rowcount != 1:
        msg = f"_retire_row: Termin {old_id} nicht abgelegt (rowcount={cursor.rowcount})"
        raise RuntimeError(msg)


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
        `wiedervorlage_am` schreibt die Methode, wie sie ihn bekommt — `None`
        bleibt `NULL`. Die Vorgabe gibt der Aufrufer aus dem Typ
        (`memory/timeline_types.py::resubmission_at`): Ein Eintrag, der nicht
        erinnert, bekaeme sonst still eine Wiedervorlage.
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

        # Lokale Zeit → UTC für DB
        event_time_utc = _to_utc(event_time)
        wiedervorlage_utc = _to_utc(wiedervorlage_am) if wiedervorlage_am else None
        # Scheibe 12 D (18.09.2026): das Ende einer Spanne, wo eine genannt ist.
        ende_utc = _to_utc(event_ende) if event_ende else None

        conn = psycopg2.connect(postgres_url)
        try:
            termin_id: int = _insert_row(conn.cursor(), {
                "user_id": user_id, "character_id": character_id,
                "event_time": event_time_utc, "event_type": event_type, "title": title,
                "details": details, "recurring": recurring, "precision": precision,
                "entitaet_ids": entitaet_ids, "wiedervorlage_am": wiedervorlage_utc,
                "themen": themen, "binding": binding, "remind": remind,
                "conflict_check": conflict_check, "event_ende": ende_utc,
            })
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
    def verschieben(
        postgres_url:     str,
        alte_id:          int,
        *,
        event_time:       datetime,
        precision:        str,
        wiedervorlage_am: datetime | None,
    ) -> int:
        """Verschiebt einen Termin: neue Zeile, die alte zeigt auf sie.

        Die neue Zeile uebernimmt von der alten Paar (`user_id`,
        `character_id`), Typ, Titel, Details, Merkmale, Themen und
        `entitaet_ids`; neu sind Zeitpunkt, Genauigkeit und Wiedervorlage. Ein
        Ende der alten Zeile wandert mit, um denselben Abstand wie der Beginn
        — die Dauer bleibt, und das Ende liegt nie vor dem neuen Beginn. Danach
        wird die alte Zeile inaktiv mit `nachfolger_id` auf die neue.

        Beide Schritte stehen in **einer** Transaktion: Scheitert einer,
        bleibt die alte Zeile aktiv und die neue entsteht nicht. Die
        Wiedervorlage gibt der Aufrufer vor (`resubmission_at`), wie bei
        `insert`.

        Vorbedingung: `alte_id` eine positive Ganzzahl; `event_time` ein
            Zeitpunkt (ohne Zone: Ortszeit); `precision` ein nicht leerer Text.
        Nachbedingung: die neue Zeile ist aktiv und committet, die alte
            inaktiv mit `nachfolger_id` = neue `id`; zurueck kommt die neue `id`.
        Fehlerfaelle: eine falsche Eingabe wirft `TypeError`/`ValueError`
            vor der Verbindung; eine unbekannte oder schon inaktive alte Zeile
            wirft `ValueError`; jeder Fehler danach rollt beide Schritte
            zurueck und wird weitergeworfen.
        """
        # ── Eingabe-Validierung ─────────────────────
        if isinstance(alte_id, bool) or not isinstance(alte_id, int) or alte_id <= 0:
            msg: str = f"verschieben: alte_id ist keine positive Ganzzahl ({alte_id!r})"
            raise ValueError(msg)
        if not isinstance(event_time, datetime):
            msg = f"verschieben: event_time ist kein datetime ({type(event_time).__name__})"
            raise TypeError(msg)
        if not isinstance(precision, str) or not precision:
            msg = f"verschieben: precision leer oder kein Text ({precision!r})"
            raise ValueError(msg)
        if wiedervorlage_am is not None and not isinstance(wiedervorlage_am, datetime):
            msg = f"verschieben: wiedervorlage_am ist kein datetime ({wiedervorlage_am!r})"
            raise TypeError(msg)

        # ── Verarbeitung ────────────────────────────
        start_utc: datetime = _to_utc(event_time)
        conn = psycopg2.connect(postgres_url)
        try:
            old: dict = _lock_active_row(
                conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor), alte_id,
            )
            _check_pair("verschieben", old["user_id"], old["character_id"])
            duration: timedelta | None = (
                old["event_ende"] - old["event_time"] if old["event_ende"] else None
            )
            cursor = conn.cursor()
            neue_id: int = _insert_row(cursor, {
                **{column: old[column] for column in _INSERT_COLUMNS},
                "event_time": start_utc, "precision": precision,
                "wiedervorlage_am": _to_utc(wiedervorlage_am) if wiedervorlage_am else None,
                "event_ende": start_utc + duration if duration is not None else None,
            })
            _retire_row(cursor, alte_id, neue_id)
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception(f"TimelineRepository.verschieben: Termin {alte_id} unveraendert")
            raise
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if neue_id == alte_id:
            msg = f"verschieben: neue id {neue_id} gleich der alten"
            raise RuntimeError(msg)
        logger.info(
            f"TimelineRepository.verschieben: alt={alte_id} -> neu={neue_id}, "
            f"character_id='{old['character_id']}', event_type='{old['event_type']}'"
        )
        return neue_id

    @staticmethod
    def aktive_zeile(postgres_url: str, termin_id: int) -> dict | None:
        """Die aktive Zeile, auf die ein Verweis auf `termin_id` heute zeigt.

        Folgt `nachfolger_id` ab `termin_id` bis zur letzten Zeile der Kette,
        hoechstens `MAX_SUCCESSOR_DEPTH` Schritte. Eine Zeile ohne Nachfolger
        ist ihre eigene aktive Zeile.

        Vorbedingung: `termin_id` eine positive Ganzzahl.
        Nachbedingung: die letzte Zeile der Kette (Zeit in Ortszeit), wenn sie
            aktiv ist; `None`, wenn es `termin_id` nicht gibt oder das Ende
            der Kette inaktiv ist (ein geloeschter Termin).
        Fehlerfaelle: ein Zyklus, eine Kette ueber `MAX_SUCCESSOR_DEPTH` oder
            ein Nachfolger, den es nicht gibt, wirft `RuntimeError` — ein
            Verweis darf nie still auf einer Zwischenzeile stehen bleiben.
        """
        # ── Eingabe-Validierung ─────────────────────
        if isinstance(termin_id, bool) or not isinstance(termin_id, int) or termin_id <= 0:
            msg: str = f"aktive_zeile: termin_id ist keine positive Ganzzahl ({termin_id!r})"
            raise ValueError(msg)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(_CHAIN_SQL, (termin_id, MAX_SUCCESSOR_DEPTH))
            end: dict | None = cursor.fetchone()
            row: dict | None = None
            if end is not None:
                cursor.execute(
                    "SELECT * FROM timeline WHERE id = %s AND aktiv = TRUE", (end["id"],),
                )
                row = cursor.fetchone()
            conn.commit()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if end is None:
            return None
        if end["cycle"]:
            msg = f"aktive_zeile: Zyklus in der Kette ab Termin {termin_id} (bei {end['id']})"
            logger.error(msg)
            raise RuntimeError(msg)
        if end["depth"] > MAX_SUCCESSOR_DEPTH or end["nachfolger_id"] is not None:
            msg = (
                f"aktive_zeile: Kette ab Termin {termin_id} endet nicht nach "
                f"{MAX_SUCCESSOR_DEPTH} Schritten (Tiefe {end['depth']}, bei {end['id']})"
            )
            logger.error(msg)
            raise RuntimeError(msg)
        return _row_to_local(dict(row)) if row else None

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
