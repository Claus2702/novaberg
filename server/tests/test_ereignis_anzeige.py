"""Zeugen: Ein Ereignis wird gekennzeichnet gelesen, als Monat gelesen, verwiesen und geklärt.

Was diese Datei zusichert:
  * **Kennzeichnung:** In `[TERMINE]` steht ein Ereignis einer anderen Person
    unter eigener Kopfzeile als *Ereignis (Lena): … — November 2026*, nie als
    Termin des Menschen; ein Termin steht davor, zeichengleich wie bisher,
    und ohne Ereignis gibt es keine zweite Kopfzeile. Ein gekennzeichneter
    Typ, der zugleich als Termin gilt, bricht `is_marked` laut.
  * **Monat:** Ein Eintrag mit `month` ist erst nach dem Monatsende
    vergangen und steht in jedem Fenster, das seinen Monat überlappt; ein
    Termin am Ersten ist am Fünften vergangen und fehlt im Fenster 10.–20.
    Die Abfrage trägt den Monatsbeginn als untere Grenze.
  * **Mappe:** Ein Fakt mit Verweis auf ein Ereignis zeigt *ab <Titel>,
    <Monat|Datum>* über die heute aktive Zeile, ein abgelöster Wert *bis*;
    eine Zeile eines anderen Paares gibt weder *ab* noch *bis*, laut im Log.
  * **Klärung:** Eine genaue Angabe zu einem Monats-Ereignis derselben
    Person im Paar verschiebt die Zeile; eine andere Person oder eine andere
    Figur bekommt eine neue Zeile.

Die Datenbank ist die Wegwerf-Datenbank der Suite; jedes Fixture bringt einen
eigenen Menschen mit und räumt in tearDown ab. Das Modell antwortet aus einem
festen Ausgang. Die Uhr steht am 05.11.2026, 10:00 Ortszeit. Die Beispiele
sind synthetisch.
"""

import unittest
import uuid
from dataclasses import replace
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import psycopg2
import psycopg2.extras

from agents.timeline import ereignis as ereignis_mod
from config import POSTGRES_URL
from graph.appointments import Appointment, AppointmentReading, AppointmentWindow
from graph.format.appointments import EVENTS_HEADER, appointments_body, is_marked
from memory.fakten_mappe import MappeEntry, load_mappe
from memory.repositories.fakten_repository import FaktenRepository, NewFact
from memory.repositories.timeline_repository import TimelineRepository
from memory.timeline_reading import read_appointments, to_appointment
from memory.timeline_types import EVENT_TYPES, EventType

BERLIN: ZoneInfo = ZoneInfo("Europe/Berlin")
NOW: datetime = datetime(2026, 11, 5, 10, 0, tzinfo=BERLIN)
CHAR: str = "nova-test"
LINE_EVENT: str = "- Ereignis (Lena): Umzug nach Kassel — November 2026 (diesen Monat)"
LINE_APPOINTMENT: str = "- Donnerstag, 12.11.2026, ohne Uhrzeit — Zahnarzt (in 7 Tagen)"

_AUFTRAG: dict = {"ziel": "timeline", "aktion": "ereignis", "daten": {
    "turn_id": "probe-turn", "verlauf_id": 42, "salienz_human": 0.80,
    "user_intentionen": ["mitteilen"], "abgelegt": True,
}}


def _ausfuehren(sql: str, params: tuple) -> list[dict]:
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            zeilen: list[dict] = [dict(r) for r in cur.fetchall()] if cur.description else []
        conn.commit()
        return zeilen
    finally:
        conn.close()


def _fenster(start: datetime, ende: datetime, richtung: str = "both") -> AppointmentWindow:
    return AppointmentWindow(kind="range", direction=richtung, start=start, end=ende)


class _Fixture(unittest.TestCase):
    """Ein eigener Mensch; Fakten, Zeilen und Entitäten werden danach gelöscht."""

    def setUp(self) -> None:
        self.user: str = f"test-anzeige-{uuid.uuid4().hex[:8]}"

    def tearDown(self) -> None:
        _ausfuehren("DELETE FROM fakten WHERE user_id = %s", (self.user,))
        _ausfuehren("DELETE FROM timeline WHERE user_id = %s", (self.user,))
        _ausfuehren("DELETE FROM entitaeten WHERE user_id = %s", (self.user,))

    def _zeile(self, typ: str, tag: datetime, titel: str, precision: str = "day",
               details: str | None = None) -> int:
        return TimelineRepository.insert(
            POSTGRES_URL, self.user, CHAR, tag, typ, titel, details=details, precision=precision,
        )

    def _ereignis_november(self, titel: str = "Umzug nach Kassel", person: str = "Lena") -> int:
        return self._zeile("ereignis", datetime(2026, 11, 1, tzinfo=BERLIN), titel,
                           precision="month", details=person)

    def _lesen(self, fenster: AppointmentWindow) -> AppointmentReading:
        return read_appointments(fenster, self.user, CHAR, POSTGRES_URL, NOW)


class TheEventStandsMarkedTest(_Fixture):
    """`[TERMINE]`: das Ereignis unter eigener Kopfzeile, der Termin davor wie bisher."""

    NOVEMBER: tuple[datetime, datetime] = (
        datetime(2026, 11, 1, tzinfo=BERLIN), datetime(2026, 11, 30, 23, 59, 59, tzinfo=BERLIN),
    )

    def test_the_event_stands_marked_under_its_own_header(self) -> None:
        self._ereignis_november()
        self._zeile("termin", datetime(2026, 11, 12, tzinfo=BERLIN), "Zahnarzt")
        zeilen: list[str] = appointments_body(self._lesen(_fenster(*self.NOVEMBER))).split("\n")
        self.assertEqual(zeilen[1:], [LINE_APPOINTMENT, EVENTS_HEADER, LINE_EVENT])

    def test_the_twin_without_an_event_the_block_has_no_second_header(self) -> None:
        self._zeile("termin", datetime(2026, 11, 12, tzinfo=BERLIN), "Zahnarzt")
        rumpf: str = appointments_body(self._lesen(_fenster(*self.NOVEMBER)))
        self.assertEqual(rumpf.split("\n")[1:], [LINE_APPOINTMENT])
        self.assertNotIn(EVENTS_HEADER, rumpf)

    def test_an_event_alone_is_no_appointment_of_the_human(self) -> None:
        self._ereignis_november()
        zeilen: list[str] = appointments_body(self._lesen(_fenster(*self.NOVEMBER))).split("\n")
        self.assertEqual(
            zeilen[1:], ["keine Termine vom 01.11.2026 bis 30.11.2026", EVENTS_HEADER, LINE_EVENT],
        )


class AMonthLastsUntilItsEndTest(_Fixture):
    """Ein Monat ist am Fünften nicht vergangen und steht im Fenster 10.–20."""

    MITTE: tuple[datetime, datetime] = (
        datetime(2026, 11, 10, tzinfo=BERLIN), datetime(2026, 11, 20, 23, 59, 59, tzinfo=BERLIN),
    )

    def _termin(self, zeilen_id: int) -> object:
        return to_appointment(TimelineRepository.find_by_id(POSTGRES_URL, zeilen_id), NOW)

    def test_the_month_is_not_past_on_the_fifth(self) -> None:
        self.assertIs(self._termin(self._ereignis_november()).past, False)

    def test_the_twin_a_day_on_the_first_is_past_on_the_fifth(self) -> None:
        termin = self._zeile("termin", datetime(2026, 11, 1, tzinfo=BERLIN), "Zahnarzt")
        self.assertIs(self._termin(termin).past, True)

    def test_the_window_in_the_middle_of_the_month_holds_the_month(self) -> None:
        ereignis = self._ereignis_november()
        termin = self._zeile("termin", datetime(2026, 11, 1, tzinfo=BERLIN), "Zahnarzt")
        ids: list[int] = [a.timeline_id for a in self._lesen(_fenster(*self.MITTE)).appointments]
        self.assertEqual(ids, [ereignis])
        self.assertNotIn(termin, ids)

    def test_forward_keeps_the_month_and_drops_the_first(self) -> None:
        ereignis = self._ereignis_november()
        self._zeile("termin", datetime(2026, 11, 1, tzinfo=BERLIN), "Zahnarzt")
        fenster = _fenster(datetime(2026, 11, 1, tzinfo=BERLIN),
                           datetime(2026, 11, 30, 23, 59, 59, tzinfo=BERLIN), "forward")
        self.assertEqual([a.timeline_id for a in self._lesen(fenster).appointments], [ereignis])


class _RecordingCursor:
    """Ein Cursor, der jede Abfrage mit ihren Parametern mitschreibt."""

    def __init__(self, log: list[tuple[str, tuple]]) -> None:
        self.log: list[tuple[str, tuple]] = log

    def execute(self, sql: str, params: tuple) -> None:
        self.log.append((sql, params))

    def fetchall(self) -> list:
        return []


class _RecordingConnection:
    """Eine Verbindung, die nichts verbindet und ihre Cursor mitschreiben lässt."""

    def __init__(self) -> None:
        self.log: list[tuple[str, tuple]] = []

    def cursor(self, cursor_factory: object = None) -> _RecordingCursor:
        return _RecordingCursor(self.log)

    def close(self) -> None:
        """Nichts zu schließen."""


class TheQueryStartsAtTheMonthTest(unittest.TestCase):
    """`find_by_date_range` schickt den Monatsbeginn von `von` als untere Grenze."""

    def test_the_month_start_and_the_window_start_are_both_sent(self) -> None:
        verbindung = _RecordingConnection()
        with patch("memory.repositories.timeline_repository.psycopg2.connect",
                   return_value=verbindung):
            TimelineRepository.find_by_date_range(
                "postgresql://attrappe", "u", "c",
                datetime(2026, 11, 10, tzinfo=BERLIN),
                datetime(2026, 11, 20, 23, 59, 59, tzinfo=BERLIN),
            )
        (sql, params), = verbindung.log
        self.assertIn("event_time BETWEEN %s AND %s", sql)
        self.assertIn("(COALESCE(precision, '') = %s OR event_time >= %s)", sql)
        self.assertEqual(params, (
            "u", "c", datetime(2026, 10, 31, 23, 0, tzinfo=UTC),
            datetime(2026, 11, 20, 22, 59, 59, tzinfo=UTC), [], "month",
            datetime(2026, 11, 9, 23, 0, tzinfo=UTC),
        ))


class TheMappeShowsSinceAndUntilTest(_Fixture):
    """Liska zieht von Bautzen nach Görlitz; der Fakt verweist auf das Ereignis."""

    def setUp(self) -> None:
        super().setUp()
        self.liska: int = _ausfuehren(
            "INSERT INTO entitaeten (user_id, name, typ) VALUES (%s, 'Liska', 'person') "
            "RETURNING id", (self.user,),
        )[0]["id"]
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                FaktenRepository.insert(cur, self.user, CHAR, self.liska, "wohnort", NewFact(
                    fakt_text="Liska wohnt in Bautzen", herkunft="mensch", einwertig=True,
                    objekt_wert="Bautzen"))
            conn.commit()
            self.monat: int = self._ereignis_november("Umzug nach Görlitz", "Liska")
            with conn.cursor() as cur:
                self.neu: int = FaktenRepository.abloesen(
                    cur, self.user, CHAR, self.liska, "wohnort", NewFact(
                        fakt_text="Liska wohnt in Görlitz", herkunft="mensch", einwertig=True,
                        objekt_wert="Görlitz", timeline_id=self.monat))
            conn.commit()
        finally:
            conn.close()

    def _eintrag(self) -> MappeEntry:
        mappe = load_mappe(POSTGRES_URL, self.user, CHAR, self.liska)
        eintraege: list[MappeEntry] = [e for e in mappe.entries if e.fact_id == self.neu]
        self.assertEqual(len(eintraege), 1)
        return eintraege[0]

    def test_after_the_move_since_shows_the_day_and_the_old_value_until(self) -> None:
        TimelineRepository.verschieben(
            POSTGRES_URL, self.monat, event_time=datetime(2026, 11, 14, tzinfo=BERLIN),
            precision="day", wiedervorlage_am=None,
        )
        eintrag = self._eintrag()
        self.assertEqual(eintrag.since, "ab Umzug nach Görlitz, 14.11.2026")
        self.assertEqual(eintrag.previous, "Liska wohnt in Bautzen — bis Umzug nach Görlitz")

    def test_the_twin_before_the_move_since_shows_the_month(self) -> None:
        eintrag = self._eintrag()
        self.assertEqual(eintrag.since, "ab Umzug nach Görlitz, November 2026")
        self.assertEqual(eintrag.timeline_id, self.monat)

    def test_a_row_of_another_pair_gives_neither_since_nor_until(self) -> None:
        fremd: int = TimelineRepository.insert(
            POSTGRES_URL, self.user, "andere-test", datetime(2026, 11, 1, tzinfo=BERLIN),
            "ereignis", "Umzug nach Görlitz", details="Liska", precision="month",
        )
        _ausfuehren("UPDATE fakten SET timeline_id = %s WHERE id = %s", (fremd, self.neu))
        with self.assertLogs("ki_server.memory.fakten_mappe", level="ERROR") as protokoll:
            eintrag = self._eintrag()
        self.assertEqual((eintrag.timeline_id, eintrag.since, eintrag.previous), (fremd, "", ""))
        self.assertIn("eines anderen Paares", "\n".join(protokoll.output))

    def test_the_twin_a_row_of_the_own_pair_gives_since_and_until(self) -> None:
        eigen: int = self._ereignis_november("Umzug nach Görlitz", "Liska")
        _ausfuehren("UPDATE fakten SET timeline_id = %s WHERE id = %s", (eigen, self.neu))
        eintrag = self._eintrag()
        self.assertEqual(eintrag.since, "ab Umzug nach Görlitz, November 2026")
        self.assertEqual(eintrag.previous, "Liska wohnt in Bautzen — bis Umzug nach Görlitz")


class AMarkedTypeIsNoAppointmentTest(unittest.TestCase):
    """`is_marked`: Ein gekennzeichneter Typ, der zugleich als Termin gilt, bricht laut."""

    EREIGNIS: Appointment = Appointment(
        moment=datetime(2026, 11, 1, tzinfo=BERLIN), has_time=False, title="Umzug nach Kassel",
        details="Lena", past=False, timeline_id=1, event_type="ereignis", precision="month",
        persons=("Lena",),
    )

    def test_a_marked_type_that_counts_as_appointment_raises(self) -> None:
        tabelle: dict[str, EventType] = {
            **EVENT_TYPES, "ereignis": replace(EVENT_TYPES["ereignis"], is_appointment=True),
        }
        with (patch("graph.format.appointments.EVENT_TYPES", tabelle),
              self.assertRaisesRegex(RuntimeError, "zugleich als Termin")):
            is_marked(self.EREIGNIS)

    def test_the_twin_the_real_table_marks_the_event(self) -> None:
        self.assertIs(is_marked(self.EREIGNIS), True)
        self.assertIs(EVENT_TYPES["ereignis"].is_appointment, False)


class AnExactDateClarifiesTheMonthTest(_Fixture):
    """*im November 2026*, dann *am 14.11.2026* — dieselbe Person im Paar verschiebt."""

    def setUp(self) -> None:
        super().setUp()
        self.modell = MagicMock()
        for ersatz in (patch.object(ereignis_mod, "model_service", self.modell),
                       patch.object(ereignis_mod, "now_local", return_value=NOW)):
            ersatz.start()
            self.addCleanup(ersatz.stop)

    def _laufen(self, zeitausdruck: str, person: str = "Ilva",
                char: str = CHAR) -> tuple[dict, dict]:
        """(Abbildung, Inhalt des einen Eintrags `log_db_write`)."""
        self.modell.chat.submit_sync.return_value.parsed = {"ereignisse": [{
            "kandidat": 1, "person": person, "titel": "Umzug nach Ostheim",
            "zeitausdruck": zeitausdruck,
        }]}
        zustand: dict = {"user_id": self.user, "character_id": char, "turn_id": "probe-turn",
                         "user_prompt": f"{person} zieht {zeitausdruck} nach Ostheim."}
        kandidat: dict = {"id": 1, "objekt_id": 1, "objekt": person, "klasse": "person",
                          "entitaet_id": None, "entitaet_bindung": None,
                          "eigenschaft": "Wohnort", "wert": "Ostheim", "sprecher": "nutzer"}
        with patch.object(ereignis_mod, "turn_candidates", return_value=[kandidat]), \
             patch.object(ereignis_mod, "log_db_write") as eintrag:
            abbildung = ereignis_mod.process_event_orders(zustand, [_AUFTRAG], POSTGRES_URL)
        eintrag.assert_called_once()
        return abbildung, eintrag.call_args.kwargs["inhalt"]

    def _zeilen(self) -> list[dict]:
        return _ausfuehren(
            "SELECT id, character_id, aktiv, nachfolger_id, precision, event_time "
            "FROM timeline WHERE user_id = %s ORDER BY id", (self.user,),
        )

    def test_the_exact_date_moves_the_month_row(self) -> None:
        erste, _ = self._laufen("im November 2026")
        abbildung, inhalt = self._laufen("am 14.11.2026")
        zeilen = self._zeilen()
        self.assertEqual([e["ausgang"] for e in inhalt["ereignisse"]], ["verschoben"])
        self.assertEqual(abbildung, erste)
        self.assertEqual(len(zeilen), 2)
        alt, neu = zeilen
        self.assertEqual(alt["id"], erste[1])
        self.assertEqual((alt["aktiv"], alt["nachfolger_id"]), (False, neu["id"]))
        tag = neu["event_time"].astimezone(BERLIN)
        self.assertEqual((neu["aktiv"], neu["precision"], tag.month, tag.day),
                         (True, "day", 11, 14))

    def test_the_twin_another_person_gets_a_new_row(self) -> None:
        self._laufen("im November 2026")
        _, inhalt = self._laufen("am 14.11.2026", person="Lena")
        self.assertEqual([e["ausgang"] for e in inhalt["ereignisse"]], ["eingetragen"])
        zeilen = self._zeilen()
        self.assertEqual([(z["aktiv"], z["nachfolger_id"]) for z in zeilen],
                         [(True, None), (True, None)])

    def test_the_twin_another_character_gets_a_new_row(self) -> None:
        self._laufen("im November 2026")
        _, inhalt = self._laufen("am 14.11.2026", char="andere-test")
        self.assertEqual([e["ausgang"] for e in inhalt["ereignisse"]], ["eingetragen"])
        zeilen = self._zeilen()
        self.assertEqual([(z["character_id"], z["aktiv"]) for z in zeilen],
                         [(CHAR, True), ("andere-test", True)])


if __name__ == "__main__":
    unittest.main()
