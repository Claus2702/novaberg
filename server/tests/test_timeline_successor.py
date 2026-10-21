"""Zeugen fuer den Nachfolger eines verschobenen Termins.

Was diese Datei zusichert:
  * **Schema** — die Schemadatei legt `nachfolger_id` an, mit einem
    Fremdschluessel auf `timeline(id)`, der beim Loeschen des Nachfolgers auf
    `NULL` faellt, und einem Teilindex ueber die gesetzten Werte. Ein Bestand
    ohne die Spalte bekommt sie, seine Zeilen bleiben `NULL`; ein zweiter
    Start aendert nichts.
  * **Verschieben** — `TimelineRepository.verschieben` legt eine neue Zeile
    mit Paar, Typ, `entitaet_ids` und der Dauer der alten an und legt die
    alte mit `nachfolger_id` auf die neue ab. Scheitert ein Schritt, bleiben
    beide Zeilen, wie sie waren.
  * **Aktive Zeile** — `aktive_zeile` folgt dem Verweis bis zur aktiven
    Zeile; eine Zeile ohne Nachfolger ist ihre eigene. Ein Zyklus oder mehr
    als zehn Schritte sind laut.

Die Suite laeuft gegen eine Wegwerf-Datenbank aus den Schemadateien des Baums.
Der Schema-Zeuge arbeitet in einem eigenen Schema, das er danach entfernt; die
Zeugen des Verschiebens bringen eine eigene Kennung mit und raeumen in
tearDown ab. Die Beispiele sind synthetisch.

Kein skipUnless, kein skipIf: Fehlt die Spalte, wird diese Datei rot.
"""

import unittest
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

import psycopg2
import psycopg2.extras
from psycopg2 import sql

from config import POSTGRES_URL
from memory.repositories.timeline_repository import TimelineRepository

BERLIN: ZoneInfo = ZoneInfo("Europe/Berlin")

#: Der Termin vor dem Verschieben, weit hinter jedem Lauf.
START: datetime = datetime(2030, 3, 4, 10, 0, tzinfo=BERLIN)
#: Der Zeitpunkt nach dem Verschieben.
MOVED: datetime = datetime(2030, 3, 6, 14, 30, tzinfo=BERLIN)
#: Nicht `nova`: Eine Vorgabe-Figur faellt nur bei einer anderen auf.
CHARACTER: str = "figur-b"

_REPO: str = "memory.repositories.timeline_repository"

INIT_SQL: Path = Path(__file__).resolve().parents[1] / "agents" / "timeline" / "init.sql"

#: Die Tabelle, wie sie vor dem Nachfolger im Bestand steht — ohne
#: `nachfolger_id`. Von Hand gesetzt, nicht aus der Schemadatei gelesen: Sonst
#: pruefte der Zeuge die Datei gegen sich selbst.
_STOCK_TIMELINE: str = """
    CREATE TABLE timeline (
        id               SERIAL       PRIMARY KEY,
        user_id          TEXT         NOT NULL,
        character_id     VARCHAR(50)  NOT NULL,
        event_time       TIMESTAMPTZ  NOT NULL,
        event_ende       TIMESTAMPTZ,
        event_type       VARCHAR(50)  NOT NULL,
        title            VARCHAR(255) NOT NULL,
        details          TEXT,
        recurring        BOOLEAN      NOT NULL DEFAULT FALSE,
        precision        VARCHAR(15)  NOT NULL DEFAULT 'day',
        binding          BOOLEAN      NOT NULL DEFAULT FALSE,
        remind           BOOLEAN      NOT NULL DEFAULT FALSE,
        conflict_check   BOOLEAN      NOT NULL DEFAULT FALSE,
        themen           TEXT[],
        created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
        aktiv            BOOLEAN      NOT NULL DEFAULT TRUE,
        last_touched     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
        wiedervorlage_am TIMESTAMPTZ,
        entitaet_ids     INTEGER[]
    )
"""

#: Die Tabellen des Kerns, an die die Schemadatei ihre Fremdschluessel haengt —
#: als Stummel im eigenen Schema, damit die Datei nichts ausserhalb trifft.
_CORE_STUBS: tuple[str, ...] = ("notizen", "lzg_knoten", "sachlage_eigenschaft", "fakten")

_FOREIGN_KEY: str = "timeline_nachfolger_id_fkey"
_INDEX: str = "idx_timeline_nachfolger"


class _OwnSchema(unittest.TestCase):
    """Ein eigenes Schema mit den Stummeln des Kerns, danach entfernt."""

    #: Steht hier eine Tabelle, legt `setUp` sie vor dem ersten Start an.
    stock: str = ""

    def setUp(self) -> None:
        self.schema: str = f"test_tl_succ_{uuid.uuid4().hex[:8]}"
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
                cur.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema)))
                for table in _CORE_STUBS:
                    cur.execute(
                        sql.SQL("CREATE TABLE {} (id SERIAL PRIMARY KEY, timeline_id INTEGER)")
                        .format(sql.Identifier(table)),
                    )
                if self.stock:
                    cur.execute(self.stock)
                    cur.execute(
                        """INSERT INTO timeline
                               (user_id, character_id, event_time, event_type, title)
                           VALUES ('mensch', 'nova', NOW(), 'termin', 'Altbestand') RETURNING id""",
                    )
                    self.old_row: int = cur.fetchone()[0]
            conn.commit()
        finally:
            conn.close()

    def tearDown(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(self.schema)),
                )
            conn.commit()
        finally:
            conn.close()

    def _execute(self, statement: str, params: tuple = ()) -> list[tuple]:
        """Fuehrt eine Anweisung im eigenen Schema aus und liefert ihre Zeilen."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema)))
                cur.execute(statement, params or None)
                rows: list[tuple] = cur.fetchall() if cur.description else []
            conn.commit()
        finally:
            conn.close()
        return rows

    def _start(self) -> None:
        """Ein Start des Servers: die ganze Schemadatei, wie sie im Baum steht."""
        self._execute(INIT_SQL.read_text(encoding="utf-8"))

    def _column(self) -> list[tuple]:
        return self._execute(
            """SELECT data_type, is_nullable, column_default FROM information_schema.columns
               WHERE table_schema = current_schema()
                 AND table_name = 'timeline' AND column_name = 'nachfolger_id'""",
        )

    def _foreign_keys(self) -> list[tuple]:
        """Die Fremdschluessel der Spalte in diesem Schema: (Name, Zieltabelle, Loeschregel)."""
        return self._execute(
            """SELECT c.conname, c.confrelid::regclass::text, c.confdeltype
               FROM pg_constraint c
               JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
               WHERE c.contype = 'f' AND c.conrelid = 'timeline'::regclass
                 AND a.attname = 'nachfolger_id'""",
        )

    def _index(self) -> list[tuple]:
        return self._execute(
            """SELECT indexdef FROM pg_indexes
               WHERE schemaname = current_schema() AND indexname = %s""",
            (_INDEX,),
        )


class TheSchemaCarriesTheSuccessorTest(_OwnSchema):
    """Eine frische Installation: die Schemadatei allein."""

    def test_the_column_is_a_nullable_integer(self) -> None:
        self._start()
        self.assertEqual(self._column(), [("integer", "YES", None)])

    def test_the_foreign_key_sets_null_on_delete(self) -> None:
        self._start()
        # `n` ist in `pg_constraint.confdeltype` die Regel ON DELETE SET NULL.
        self.assertEqual(self._foreign_keys(), [(_FOREIGN_KEY, "timeline", "n")])

    def test_deleting_the_successor_empties_the_reference(self) -> None:
        self._start()
        first: int = self._execute(
            """INSERT INTO timeline (user_id, character_id, event_time, event_type, title)
               VALUES ('mensch', 'nova', NOW(), 'termin', 'Alt') RETURNING id""",
        )[0][0]
        second: int = self._execute(
            """INSERT INTO timeline (user_id, character_id, event_time, event_type, title)
               VALUES ('mensch', 'nova', NOW(), 'termin', 'Neu') RETURNING id""",
        )[0][0]
        self._execute("UPDATE timeline SET nachfolger_id = %s WHERE id = %s", (second, first))
        self._execute("DELETE FROM timeline WHERE id = %s", (second,))
        self.assertEqual(
            self._execute("SELECT nachfolger_id FROM timeline WHERE id = %s", (first,)), [(None,)],
        )

    def test_twin_an_existing_successor_stays_referenced(self) -> None:
        self._start()
        first: int = self._execute(
            """INSERT INTO timeline (user_id, character_id, event_time, event_type, title)
               VALUES ('mensch', 'nova', NOW(), 'termin', 'Alt') RETURNING id""",
        )[0][0]
        second: int = self._execute(
            """INSERT INTO timeline (user_id, character_id, event_time, event_type, title)
               VALUES ('mensch', 'nova', NOW(), 'termin', 'Neu') RETURNING id""",
        )[0][0]
        self._execute("UPDATE timeline SET nachfolger_id = %s WHERE id = %s", (second, first))
        self.assertEqual(
            self._execute("SELECT nachfolger_id FROM timeline WHERE id = %s", (first,)),
            [(second,)],
        )

    def test_the_index_covers_only_set_successors(self) -> None:
        self._start()
        rows: list[tuple] = self._index()
        self.assertEqual(len(rows), 1)
        self.assertIn("(nachfolger_id)", rows[0][0])
        self.assertIn("WHERE (nachfolger_id IS NOT NULL)", rows[0][0])

    def test_a_second_start_changes_nothing(self) -> None:
        self._start()
        self._start()
        self.assertEqual(self._column(), [("integer", "YES", None)])
        self.assertEqual(self._foreign_keys(), [(_FOREIGN_KEY, "timeline", "n")])
        self.assertEqual(len(self._index()), 1)


class TheStockKeepsNullTest(_OwnSchema):
    """Ein Bestand ohne die Spalte: der Start legt sie an, die Zeilen bleiben leer."""

    stock = _STOCK_TIMELINE

    def test_the_old_row_has_no_successor(self) -> None:
        self._start()
        self.assertEqual(
            self._execute("SELECT nachfolger_id FROM timeline WHERE id = %s", (self.old_row,)),
            [(None,)],
        )

    def test_twin_the_stock_gets_the_column_and_the_key(self) -> None:
        """Ohne diesen Zwilling bewiese das `NULL` oben nichts; ohne Spalte kaeme auch kein Wert."""
        self._start()
        self.assertEqual(self._column(), [("integer", "YES", None)])
        self.assertEqual(self._foreign_keys(), [(_FOREIGN_KEY, "timeline", "n")])


class _MoveFixture(unittest.TestCase):
    """Ein eigener Mensch mit einem Termin der Figur `figur-b`, zwei Stunden lang."""

    def setUp(self) -> None:
        self.user: str = f"test-tl-succ-{uuid.uuid4().hex[:8]}"
        self.old: int = self._insert("Wartung")

    def tearDown(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM timeline WHERE user_id = %s", (self.user,))
            conn.commit()
        finally:
            conn.close()

    def _insert(self, title: str) -> int:
        return TimelineRepository.insert(
            POSTGRES_URL, self.user, CHARACTER, START, "termin", title,
            precision="minute", entitaet_ids=[7, 9], themen=["termin"],
            binding=True, remind=True, conflict_check=True,
            event_ende=START + timedelta(hours=2),
            wiedervorlage_am=START + timedelta(days=7),
        )

    def _move(self, row_id: int) -> int:
        return TimelineRepository.verschieben(
            POSTGRES_URL, row_id, event_time=MOVED, precision="minute",
            wiedervorlage_am=MOVED + timedelta(days=7),
        )

    def _rows(self) -> dict[int, dict]:
        """Alle Zeilen des Menschen nach `id`."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM timeline WHERE user_id = %s", (self.user,))
                return {row["id"]: dict(row) for row in cur.fetchall()}
        finally:
            conn.close()

    def _link(self, pairs: list[tuple[int, int]]) -> None:
        """Setzt Verweise von Hand: je (Zeile, Nachfolger), die Zeile wird inaktiv."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                for row_id, successor in pairs:
                    cur.execute(
                        "UPDATE timeline SET aktiv = FALSE, nachfolger_id = %s WHERE id = %s",
                        (successor, row_id),
                    )
            conn.commit()
        finally:
            conn.close()

    def _chain(self, length: int) -> list[int]:
        """Eine Kette aus `length` Zeilen, jede zeigt auf die naechste; die letzte ist aktiv."""
        ids: list[int] = [self.old] + [self._insert(f"Glied {i}") for i in range(1, length)]
        self._link(list(zip(ids, ids[1:], strict=False)))
        return ids


class MovingKeepsTheAppointmentTest(_MoveFixture):
    """Nach dem Verschieben zeigt die alte Zeile auf die neue, und die neue ist derselbe Termin."""

    def test_the_old_row_points_to_the_new_one(self) -> None:
        new: int = self._move(self.old)
        rows: dict[int, dict] = self._rows()

        self.assertEqual(sorted(rows), sorted([self.old, new]))
        self.assertEqual((rows[self.old]["aktiv"], rows[self.old]["nachfolger_id"]), (False, new))
        self.assertEqual((rows[new]["aktiv"], rows[new]["nachfolger_id"]), (True, None))

    def test_the_new_row_keeps_pair_type_entities_and_duration(self) -> None:
        new_id: int = self._move(self.old)
        new: dict = self._rows()[new_id]

        self.assertEqual(
            (new["user_id"], new["character_id"], new["event_type"], new["title"]),
            (self.user, CHARACTER, "termin", "Wartung"),
        )
        self.assertEqual(new["entitaet_ids"], [7, 9])
        self.assertEqual(new["event_time"], MOVED)
        self.assertEqual(new["event_ende"], MOVED + timedelta(hours=2))
        self.assertEqual(new["wiedervorlage_am"], MOVED + timedelta(days=7))
        self.assertEqual((new["binding"], new["remind"], new["conflict_check"]), (True, True, True))

    def test_a_failure_after_the_insert_changes_neither_row(self) -> None:
        """Das Ablegen scheitert, nachdem die neue Zeile geschrieben ist: beide Schritte zurueck."""
        before: dict[int, dict] = self._rows()
        with patch(f"{_REPO}._retire_row", side_effect=RuntimeError("Abbruch")), \
                self.assertRaises(RuntimeError):
            self._move(self.old)

        self.assertEqual(self._rows(), before)

    def test_a_failure_of_the_insert_leaves_the_old_row_active(self) -> None:
        """Stuende das Ablegen vor dem Anlegen, ohne Transaktion, waere der Termin weg."""
        before: dict[int, dict] = self._rows()
        with patch(f"{_REPO}._insert_row", side_effect=RuntimeError("Abbruch")), \
                self.assertRaises(RuntimeError):
            self._move(self.old)

        self.assertEqual(self._rows(), before)

    def test_an_inactive_row_is_not_moved_again(self) -> None:
        self._move(self.old)
        with self.assertRaises(ValueError):
            self._move(self.old)
        self.assertEqual(len(self._rows()), 2)


class TheActiveRowTest(_MoveFixture):
    """`aktive_zeile` folgt dem Verweis — hoechstens zehn Schritte, nie im Kreis."""

    def test_twin_a_row_without_successor_is_its_own_active_row(self) -> None:
        self.assertEqual(TimelineRepository.aktive_zeile(POSTGRES_URL, self.old)["id"], self.old)

    def test_the_old_id_finds_the_row_after_two_moves(self) -> None:
        last: int = self._move(self._move(self.old))
        self.assertEqual(TimelineRepository.aktive_zeile(POSTGRES_URL, self.old)["id"], last)

    def test_a_cycle_is_loud(self) -> None:
        other: int = self._insert("Gegenueber")
        self._link([(self.old, other), (other, self.old)])
        with self.assertLogs("ki_server.memory.repositories.timeline", level="ERROR"), \
                self.assertRaises(RuntimeError):
            TimelineRepository.aktive_zeile(POSTGRES_URL, self.old)

    def test_eleven_steps_are_loud(self) -> None:
        ids: list[int] = self._chain(12)
        with self.assertLogs("ki_server.memory.repositories.timeline", level="ERROR"), \
                self.assertRaises(RuntimeError):
            TimelineRepository.aktive_zeile(POSTGRES_URL, ids[0])

    def test_twin_ten_steps_reach_the_end(self) -> None:
        ids: list[int] = self._chain(11)
        self.assertEqual(TimelineRepository.aktive_zeile(POSTGRES_URL, ids[0])["id"], ids[-1])

    def test_an_unknown_id_has_no_active_row(self) -> None:
        self.assertIsNone(TimelineRepository.aktive_zeile(POSTGRES_URL, 2_000_000_000))


if __name__ == "__main__":
    unittest.main()
