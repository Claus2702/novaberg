"""Zeugen fuer die Timeline je Paar — ein Termin gehoert dem Paar, das ihn angelegt hat.

Was diese Datei zusichert:
  * **Bestand** — eine Zeile ohne Figur bekommt beim Start `nova`; danach ist
    die Spalte Pflicht ohne Vorgabewert, und ein zweiter Start aendert nichts.
    Die Indexe gehen ueber das Paar.
  * **Zwei Figuren** — ein Termin des Paares (Mensch, `nova`) erscheint fuer
    dieses Paar und nicht fuer denselben Menschen mit einer anderen Figur: im
    Repository, in `read_appointments` und im Kalender-Angebot der Sachlage.
  * **Ohne Figur** — jede Methode des Repositorys, die nach dem Menschen
    liest oder schreibt, wirft bei leerer Figur `ValueError`, bevor eine
    Verbindung entsteht; mit Figur laeuft sie gegen die Datenbank.
  * **Anker** — ein Erinnerungs-Anker wird nur im eigenen Paar
    wiederverwendet, nie aus einem anderen uebernommen.
  * **Agent schreibt im Paar** — das Anlegen ueber den Timeline-Agenten
    schreibt die Figur mit; ohne Figur wird nichts geschrieben und keine
    Verbindung geoeffnet.

Die Suite laeuft gegen eine Wegwerf-Datenbank aus den Schemadateien des Baums.
Jedes Fixture bringt trotzdem eine eigene Kennung mit und raeumt in tearDown
ab; der Bestands-Zeuge arbeitet in einem eigenen Schema, das er danach
entfernt. Die Beispiele sind synthetisch.

Kein skipUnless, kein skipIf: Fehlt die Spalte, wird diese Datei rot.
"""

import unittest
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

import psycopg2
import psycopg2.errors
from psycopg2 import sql

from agents.kzg.magnete import _timeline_aufloesen
from agents.timeline import crud as timeline_crud
from config import POSTGRES_URL
from graph.appointments import DIRECTION_BOTH, KIND_RANGE, AppointmentWindow
from graph.nodes.sachlage_resolver import SOURCE_CALENDAR, memory_offer
from memory.repositories.timeline_repository import TimelineRepository
from memory.timeline_reading import read_appointments

BERLIN: ZoneInfo = ZoneInfo("Europe/Berlin")

#: Die eingefrorene Uhr der Lesewege: Mittwoch, 21.10.2026, 12:00 Ortszeit.
NOW: datetime = datetime(2026, 10, 21, 12, 0, tzinfo=BERLIN)
#: Der Termin des Paares, weit hinter jedem Lauf — er ist fuer jede Suche kommend.
MOMENT: datetime = datetime(2030, 3, 4, 10, 0, tzinfo=BERLIN)
#: Eine Wiedervorlage weit vor jedem Lauf — sie ist immer faellig.
DUE: datetime = datetime(2026, 1, 1, 9, 0, tzinfo=BERLIN)
#: Der Tag der Erinnerungs-Anker, ein anderer als der des Termins.
ANCHOR_DAY: datetime = datetime(2030, 3, 5, 0, 0, tzinfo=BERLIN)

NOVA: str = "nova"
OTHER: str = "andere-figur"

INIT_SQL: Path = Path(__file__).resolve().parents[1] / "agents" / "timeline" / "init.sql"
REPO_CONNECT: str = "memory.repositories.timeline_repository.psycopg2.connect"
_CLOCK: str = "graph.nodes.sachlage_resolver.now_local"
_PARSER: str = "agents.kzg.magnete.zeit_parsen_vektor"

#: Die Tabelle, wie sie vor dem Paar im Bestand steht — ohne `character_id`.
#: Von Hand gesetzt, nicht aus der Schemadatei gelesen: Sonst pruefte der
#: Zeuge die Datei gegen sich selbst.
_LEGACY_TIMELINE: str = """
    CREATE TABLE timeline (
        id               SERIAL       PRIMARY KEY,
        user_id          TEXT         NOT NULL,
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


class TheStockBelongsToNovaTest(unittest.TestCase):
    """Die Schemadatei am Bestand: eine Zeile ohne Figur bekommt `nova`, einmal."""

    def setUp(self) -> None:
        self.schema: str = f"test_tl_{uuid.uuid4().hex[:8]}"
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
                cur.execute(_LEGACY_TIMELINE)
                # Die Indexe des Bestands nach dem Menschen allein: Der Start
                # muss sie entfernen, nicht nur keine neuen anlegen.
                cur.execute("CREATE INDEX idx_timeline_user_time ON timeline (user_id, event_time)")
                cur.execute("CREATE INDEX idx_timeline_user_type ON timeline (user_id, event_type)")
                cur.execute(
                    """INSERT INTO timeline (user_id, event_time, event_type, title)
                       VALUES ('mensch', NOW(), 'termin', 'Altbestand') RETURNING id""",
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

    def _characters(self) -> dict[int, str]:
        return dict(self._execute("SELECT id, character_id FROM timeline"))

    def test_the_old_row_gets_nova(self) -> None:
        self._start()
        self.assertEqual(self._characters(), {self.old_row: NOVA})

    def test_the_column_is_required_without_default(self) -> None:
        self._start()
        rows: list[tuple] = self._execute(
            """SELECT is_nullable, column_default FROM information_schema.columns
               WHERE table_schema = current_schema()
                 AND table_name = 'timeline' AND column_name = 'character_id'""",
        )
        self.assertEqual(rows, [("NO", None)])

    def test_a_second_start_changes_nothing(self) -> None:
        self._start()
        new_row: int = self._execute(
            """INSERT INTO timeline (user_id, character_id, event_time, event_type, title)
               VALUES ('mensch', %s, NOW(), 'termin', 'Neu') RETURNING id""",
            (OTHER,),
        )[0][0]
        self._start()
        self.assertEqual(self._characters(), {self.old_row: NOVA, new_row: OTHER})

    def test_an_insert_without_character_is_rejected(self) -> None:
        self._start()
        with self.assertRaises(psycopg2.errors.NotNullViolation):
            self._execute(
                """INSERT INTO timeline (user_id, event_time, event_type, title)
                   VALUES ('mensch', NOW(), 'termin', 'Ohne Figur')""",
            )

    def test_twin_an_insert_with_nova_is_accepted(self) -> None:
        self._start()
        self._execute(
            """INSERT INTO timeline (user_id, character_id, event_time, event_type, title)
               VALUES ('mensch', %s, NOW(), 'termin', 'Mit Figur')""",
            (NOVA,),
        )
        self.assertEqual(sorted(self._characters().values()), [NOVA, NOVA])

    def test_the_indexes_go_over_the_pair(self) -> None:
        self._start()
        names: set[str] = {
            r[0] for r in self._execute(
                "SELECT indexname FROM pg_indexes WHERE schemaname = current_schema()",
            )
        }
        self.assertLessEqual({"idx_timeline_paar_time", "idx_timeline_paar_type"}, names)
        self.assertFalse(names & {"idx_timeline_user_time", "idx_timeline_user_type"})


class _PairFixture(unittest.TestCase):
    """Ein eigener Mensch mit einem Termin im Paar mit `nova`."""

    def setUp(self) -> None:
        tag: str = uuid.uuid4().hex[:8]
        self.user: str = f"test-tl-{tag}"
        self.title: str = f"Paartermin {tag}"
        self.appointment: int = TimelineRepository.insert(
            POSTGRES_URL, self.user, NOVA, MOMENT, "termin", self.title,
            precision="minute", wiedervorlage_am=DUE,
        )

    def tearDown(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM timeline WHERE user_id = %s", (self.user,))
            conn.commit()
        finally:
            conn.close()

    def _character_of(self, row_id: int) -> str:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT character_id FROM timeline WHERE id = %s", (row_id,))
                return cur.fetchone()[0]
        finally:
            conn.close()


class TwoCharactersTest(_PairFixture):
    """Derselbe Mensch, zwei Figuren: Jede sieht nur die Termine ihres Paares."""

    def _repository_reads(self, character: str) -> dict[str, list[int]]:
        url, user = POSTGRES_URL, self.user
        reads: dict[str, list[dict]] = {
            "find_by_date_range": TimelineRepository.find_by_date_range(
                url, user, character, MOMENT - timedelta(days=1), MOMENT + timedelta(days=1),
            ),
            "find_by_date": TimelineRepository.find_by_date(url, user, character, MOMENT),
            "find_by_keyword": TimelineRepository.find_by_keyword(
                url, user, character, self.title,
            ),
            "find_wiedervorlage_faellig": TimelineRepository.find_wiedervorlage_faellig(
                url, user, character,
            ),
        }
        return {name: [r["id"] for r in rows] for name, rows in reads.items()}

    def _reading(self, character: str) -> list[int]:
        window = AppointmentWindow(
            kind=KIND_RANGE, direction=DIRECTION_BOTH,
            start=MOMENT - timedelta(days=1), end=MOMENT + timedelta(days=1),
        )
        reading = read_appointments(window, self.user, character, POSTGRES_URL, NOW)
        return [a.timeline_id for a in reading.appointments]

    def _offer(self, character: str) -> list[str]:
        previous: dict = {"objekte": [{
            "name": self.title, "akut": True,
            "zeitbezug": {"art": "titel", "stichwort": self.title, "wortlaut": self.title},
        }]}
        state: dict = {"user_id": self.user, "character_id": character, "memory_entries": []}
        with patch(_CLOCK, return_value=NOW):
            hits = memory_offer(state, previous)
        return [h.origin for h in hits if h.source == SOURCE_CALENDAR]

    def test_the_repository_gives_another_character_nothing(self) -> None:
        self.assertEqual(
            self._repository_reads(OTHER),
            {"find_by_date_range": [], "find_by_date": [], "find_by_keyword": [],
             "find_wiedervorlage_faellig": []},
        )

    def test_twin_the_repository_gives_nova_the_appointment(self) -> None:
        self.assertEqual(
            self._repository_reads(NOVA),
            {"find_by_date_range": [self.appointment], "find_by_date": [self.appointment],
             "find_by_keyword": [self.appointment],
             "find_wiedervorlage_faellig": [self.appointment]},
        )

    def test_read_appointments_gives_another_character_nothing(self) -> None:
        self.assertEqual(self._reading(OTHER), [])

    def test_twin_read_appointments_gives_nova_the_appointment(self) -> None:
        self.assertEqual(self._reading(NOVA), [self.appointment])

    def test_the_offer_of_another_character_has_no_calendar(self) -> None:
        self.assertEqual(self._offer(OTHER), [])

    def test_twin_the_offer_of_nova_carries_the_appointment(self) -> None:
        self.assertEqual(self._offer(NOVA), [f"timeline#{self.appointment}"])

    def test_insert_writes_the_character(self) -> None:
        self.assertEqual(self._character_of(self.appointment), NOVA)


class NoCharacterTest(_PairFixture):
    """Ohne Figur keine Abfrage — die Methode wirft, bevor eine Verbindung entsteht."""

    def _calls(self, character: str) -> dict[str, Callable[[], object]]:
        url, user = POSTGRES_URL, self.user
        return {
            "insert": lambda: TimelineRepository.insert(
                url, user, character, MOMENT, "termin", f"{self.title} zwei",
            ),
            "find_by_date_range": lambda: TimelineRepository.find_by_date_range(
                url, user, character, MOMENT, MOMENT,
            ),
            "find_by_date": lambda: TimelineRepository.find_by_date(url, user, character, MOMENT),
            "find_by_entitaet": lambda: TimelineRepository.find_by_entitaet(
                url, user, character, 1,
            ),
            "find_wiedervorlage_faellig": lambda: TimelineRepository.find_wiedervorlage_faellig(
                url, user, character,
            ),
            "find_by_keyword": lambda: TimelineRepository.find_by_keyword(
                url, user, character, self.title,
            ),
            "find_vergangene_ohne_wiedervorlage": lambda: (
                TimelineRepository.find_vergangene_ohne_wiedervorlage(url, user, character)
            ),
        }

    def test_every_method_rejects_an_empty_character_without_a_connection(self) -> None:
        for name, call in self._calls("").items():
            with self.subTest(methode=name), patch(REPO_CONNECT) as connect:
                with self.assertRaises(ValueError):
                    call()
                connect.assert_not_called()

    def test_twin_every_method_runs_with_a_character(self) -> None:
        for name, call in self._calls(NOVA).items():
            with self.subTest(methode=name):
                self.assertIsInstance(call(), (int, list))


class TheAgentWritesInThePairTest(unittest.TestCase):
    """Der Timeline-Agent legt einen Termin mit der Figur aus seinem Kontext an."""

    def _create(self, character: str) -> dict:
        state: dict = {
            "aufgabe": "Trag den Elternabend ein",
            "kontext": {"user_id": "pruefer", "character_id": character},
            "parameter": {"action": "create", "target": "Elternabend",
                          "zeitausdruck": "04.03.2030 19:00", "event_type": "termin"},
            "schritte": [],
        }
        with patch.object(timeline_crud, "_verifizieren_termin", return_value=True):
            return timeline_crud._create(state)

    def test_without_a_character_nothing_is_written(self) -> None:
        with patch(REPO_CONNECT) as connect, self.assertRaises(ValueError):
            self._create("")
        connect.assert_not_called()

    def test_twin_the_appointment_carries_the_character(self) -> None:
        with patch.object(TimelineRepository, "insert", return_value=4711) as insert:
            self._create(NOVA)
        self.assertEqual(insert.call_args.kwargs["character_id"], NOVA)


class TheAnchorBelongsToThePairTest(_PairFixture):
    """Ein Erinnerungs-Anker wird nur im eigenen Paar wiederverwendet."""

    def _resolve(self, character: str) -> int | None:
        vector = SimpleNamespace(datum=ANCHOR_DAY, uhrzeit_erkannt=False)
        with patch(_PARSER, return_value=vector):
            return _timeline_aufloesen(None, "am fuenften Maerz", self.user, character)

    def test_another_character_gets_its_own_anchor(self) -> None:
        nova_anchor: int | None = self._resolve(NOVA)
        other_anchor: int | None = self._resolve(OTHER)

        self.assertIsNotNone(other_anchor)
        self.assertNotEqual(other_anchor, nova_anchor)
        self.assertEqual(self._character_of(other_anchor), OTHER)

    def test_twin_the_same_pair_reuses_its_anchor(self) -> None:
        first: int | None = self._resolve(NOVA)

        self.assertIsNotNone(first)
        self.assertEqual(self._resolve(NOVA), first)
        self.assertEqual(self._character_of(first), NOVA)

    def test_no_anchor_without_a_character(self) -> None:
        self.assertIsNone(self._resolve(""))


if __name__ == "__main__":
    unittest.main()
