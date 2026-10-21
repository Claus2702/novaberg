"""Zeugen fuer die Typen eines Timeline-Eintrags — eine Quelle, laut bei Fremdem.

Was diese Datei zusichert:
  * **Wiedervorlage** — ein `ereignis` bekommt keine Wiedervorlage, ein
    `termin` eine Woche nach seinem Zeitpunkt; `TimelineRepository.insert`
    setzt selbst keine.
  * **Kein Partner** — ein `ereignis` ist weder Duplikat eines neuen Termins
    noch Treffer im Bestandsabgleich; ein `termin` mit demselben Titel ist es.
  * **Eine Quelle** — die Typlisten der UPDATEs in `agents/timeline/init.sql`
    tragen dieselben Merkmale wie `EVENT_TYPES`; der Prompt der Klassifikation
    traegt jede Zeile der klassifizierbaren Typen und keinen offenen Platzhalter.
  * **Laut** — ein unbekannter Typ wirft und steht als `ERROR` im Log; das
    Anlegen schreibt dann nichts. Ein fremder Typ des Modells wird laut zum
    `termin`.

Die Suite laeuft gegen eine Wegwerf-Datenbank aus den Schemadateien des Baums.
Jeder Zeuge an der Datenbank bringt eine eigene Kennung mit und raeumt in
tearDown ab. Die Beispiele sind synthetisch.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import re
import unittest
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

import psycopg2

from agents.timeline import crud as timeline_crud
from agents.timeline import klassifikation
from agents.timeline.suche import find_duplicates
from config import POSTGRES_URL
from memory.repositories.timeline_repository import TimelineRepository
from memory.timeline_inventory import is_appointment_at
from memory.timeline_types import CLASSIFIABLE, EVENT_TYPES, event_type

BERLIN: ZoneInfo = ZoneInfo("Europe/Berlin")

#: Der Tag der Eintraege, weit hinter jedem Lauf.
MOMENT: datetime = datetime(2030, 3, 4, 19, 0, tzinfo=BERLIN)
TITLE: str = "Umzug nach Kassel"

INIT_SQL: Path = Path(__file__).resolve().parents[1] / "agents" / "timeline" / "init.sql"
REPO_CONNECT: str = "memory.repositories.timeline_repository.psycopg2.connect"

#: Ein UPDATE der Merkmale in der Schemadatei: drei Werte, dann die Typliste.
_FLAG_UPDATE: re.Pattern[str] = re.compile(
    r"UPDATE timeline SET binding = (TRUE|FALSE),\s*remind = (TRUE|FALSE),"
    r"\s*conflict_check = (TRUE|FALSE)\s*WHERE event_type IN \(([^)]*)\);",
)


class _OwnUser(unittest.TestCase):
    """Ein eigener Mensch im Paar mit `nova`, danach abgeraeumt."""

    def setUp(self) -> None:
        self.user: str = f"test-tl-typ-{uuid.uuid4().hex[:8]}"

    def tearDown(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM timeline WHERE user_id = %s", (self.user,))
            conn.commit()
        finally:
            conn.close()

    def _resubmission(self, row_id: int) -> tuple[datetime, datetime | None]:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT event_time, wiedervorlage_am FROM timeline WHERE id = %s", (row_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    def _create(self, kind: str) -> dict:
        """Der Anlegeweg des Timeline-Agenten mit dem Typ `kind`."""
        state: dict = {
            "aufgabe": f"Trag ein: {TITLE}",
            "kontext": {"user_id": self.user, "character_id": "nova"},
            "parameter": {"action": "create", "target": TITLE,
                          "zeitausdruck": "04.03.2030 19:00", "event_type": kind},
            "schritte": [],
        }
        with patch.object(timeline_crud, "_verifizieren_termin", return_value=True):
            return timeline_crud._create(state)


class ResubmissionTest(_OwnUser):
    """Die Wiedervorlage kommt vom Typ — das Repository setzt keine."""

    def test_an_occurrence_gets_no_resubmission(self) -> None:
        result: dict = self._create("ereignis")
        self.assertEqual(result["status"], "abgeschlossen", result)

        _, due = self._resubmission(result["schritte"][-1]["termin_id"])
        self.assertIsNone(due)

    def test_twin_an_appointment_gets_one_a_week_later(self) -> None:
        result: dict = self._create("termin")
        self.assertEqual(result["status"], "abgeschlossen", result)

        moment, due = self._resubmission(result["schritte"][-1]["termin_id"])
        self.assertEqual(moment, MOMENT)
        self.assertEqual(due - moment, timedelta(days=7))

    def test_insert_without_resubmission_writes_none(self) -> None:
        """Bis hierher setzte `insert` selbst eine Woche — auch fuer den, der keine wollte."""
        row_id: int = TimelineRepository.insert(
            POSTGRES_URL, self.user, "nova", MOMENT, "termin", TITLE, precision="minute",
        )
        self.assertEqual(self._resubmission(row_id), (MOMENT, None))


class NoPartnerTest(_OwnUser):
    """Ein Ereignis einer anderen Person ist kein Termin des Menschen."""

    def _insert(self, kind: str) -> int:
        return TimelineRepository.insert(
            POSTGRES_URL, self.user, "nova", MOMENT, kind, TITLE, precision="minute",
        )

    def _duplicates(self) -> list[int]:
        return [r["id"] for r in find_duplicates(TITLE, "04.03.2030", "", self.user, "nova")]

    def test_an_occurrence_is_no_duplicate(self) -> None:
        self._insert("ereignis")
        self.assertEqual(self._duplicates(), [])

    def test_twin_an_appointment_with_the_same_title_is_one(self) -> None:
        row_id: int = self._insert("termin")
        self.assertEqual(self._duplicates(), [row_id])

    def test_an_occurrence_is_no_appointment_at_its_moment(self) -> None:
        row: dict = {"id": 1, "aktiv": True, "event_type": "ereignis",
                     "precision": "minute", "event_time": MOMENT}
        self.assertFalse(is_appointment_at(row, MOMENT))

    def test_twin_an_appointment_is_one_at_its_moment(self) -> None:
        row: dict = {"id": 1, "aktiv": True, "event_type": "termin",
                     "precision": "minute", "event_time": MOMENT}
        self.assertTrue(is_appointment_at(row, MOMENT))


class OneSourceTest(unittest.TestCase):
    """Die Schemadatei und der Prompt sagen ueber die Typen, was die Tabelle sagt."""

    def _updates(self) -> dict[str, tuple[bool, bool, bool]]:
        found: dict[str, tuple[bool, bool, bool]] = {}
        for binding, remind, conflict, names in _FLAG_UPDATE.findall(
            INIT_SQL.read_text(encoding="utf-8"),
        ):
            flags = (binding == "TRUE", remind == "TRUE", conflict == "TRUE")
            for name in re.findall(r"'([^']+)'", names):
                found[name] = flags
        return found

    def test_the_schema_updates_match_the_table(self) -> None:
        """Ein Typ ohne jedes Merkmal steht in keinem UPDATE — die Vorgabe der Spalten passt."""
        expected: dict[str, tuple[bool, bool, bool]] = {
            name: (kind.binding, kind.remind, kind.conflict_check)
            for name, kind in EVENT_TYPES.items()
            if kind.binding or kind.remind or kind.conflict_check
        }
        self.assertEqual(self._updates(), expected)

    def test_twin_the_pattern_finds_both_updates(self) -> None:
        """Ohne diesen Zwilling bewiese ein leerer Fund auf beiden Seiten nichts."""
        self.assertEqual(len(_FLAG_UPDATE.findall(INIT_SQL.read_text(encoding="utf-8"))), 2)
        self.assertEqual(
            sorted(self._updates()),
            ["deadline", "erinnerung", "geburtstag", "jahrestag", "termin"],
        )

    def test_the_prompt_carries_every_line_and_no_placeholder(self) -> None:
        prompt: str = klassifikation._build_classify_prompt()

        for name in CLASSIFIABLE:
            with self.subTest(typ=name):
                self.assertIn(f'"{name}": {EVENT_TYPES[name].prompt_line}', prompt)
        self.assertIn('"event_type": "termin|geburtstag|deadline|jahrestag|erinnerung"', prompt)
        self.assertNotIn("{type_", prompt)
        self.assertNotIn('"ereignis"', prompt)


class UnknownTypeTest(_OwnUser):
    """Ein Typ, den die Tabelle nicht kennt, ist laut — nie still ein Termin."""

    def test_an_unknown_type_raises_and_logs(self) -> None:
        with self.assertLogs("ki_server.memory.timeline_types", level="ERROR"), \
                self.assertRaises(ValueError):
            event_type("unbekannt")

    def test_twin_a_known_type_gives_its_behaviour(self) -> None:
        kind = event_type("termin")
        self.assertEqual(
            (kind.binding, kind.remind, kind.conflict_check, kind.is_appointment),
            (True, True, True, True),
        )

    def test_creating_with_an_unknown_type_writes_nothing(self) -> None:
        with patch(REPO_CONNECT) as connect, \
                self.assertLogs("ki_server.memory.timeline_types", level="ERROR"):
            result: dict = self._create("unbekannt")

        self.assertEqual(result["status"], "fehler")
        self.assertEqual(result["schritte"][-1]["ergebnis"], "unbekannter_typ")
        connect.assert_not_called()


class TheModelTypeTest(unittest.TestCase):
    """Die Klassifikation nimmt nur klassifizierbare Typen an; Fremdes wird laut `termin`."""

    def _classify(self, model_type: str) -> str:
        answer: dict = {"action": "create", "target": TITLE, "zeitausdruck": "morgen",
                        "event_type": model_type, "normalisiert": ""}
        model = SimpleNamespace(chat=SimpleNamespace(
            submit_sync=lambda request, timeout=None: SimpleNamespace(
                text=json.dumps(answer), token_total=0, thinking="", parsed=dict(answer),
            ),
        ))
        state: dict = {
            "aufgabe": f"Trag ein: {TITLE} morgen", "aufgabe_typ": "workflow",
            "agent_name": "dienst",
            "kontext": {"user_id": "", "character_id": "nova", "memory_context": ""},
            "parameter": {"action": "agent"}, "schritte": [], "ergebnis": None,
            "status": "laufend", "rueckfrage": None, "fehler": None,
        }
        with patch.object(klassifikation, "model_service", model):
            return klassifikation.klassifizieren(state)["parameter"]["event_type"]

    def test_a_foreign_type_becomes_termin_loudly(self) -> None:
        for model_type in ("quatsch", "ereignis", "erinnerungs_anker"):
            with self.subTest(typ=model_type), \
                    self.assertLogs("ki_server.agents.timeline.klassifikation", level="WARNING"):
                self.assertEqual(self._classify(model_type), "termin")

    def test_twin_a_classifiable_type_stays(self) -> None:
        self.assertEqual(self._classify("geburtstag"), "geburtstag")


if __name__ == "__main__":
    unittest.main()
