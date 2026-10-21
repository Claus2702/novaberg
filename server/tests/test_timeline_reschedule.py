"""Tests: Ein Termin laesst sich mit einer neuen Uhrzeit allein verschieben.

Ziel: *„Verschieb den Zahnarzt bitte auf 11 Uhr."* verschiebt den Termin am
selben Tag auf 11:00 Ortszeit. Bis dahin endete der Satz in der Rueckfrage
nach dem Datum: Der Zeitparser las die Uhrzeit (`uhrzeit_erkannt`), lieferte
aber kein Datum, und `_update` brach bei `datum is None` ab — der Zweig
„Uhrzeit neu, Tag vom alten Termin" stand dahinter und wurde nie erreicht.

Dazu: Ein genannter Tag allein behaelt die Uhrzeit des Termins; faellt er auf
den Tag des Termins selbst und nennt der Satz dessen Wochentag, zaehlt die
naechste Woche. Weder Tag noch Uhrzeit bleibt der Fehler mit Rueckfrage — und
dieser Fehler erreicht den Prompt der Antwort mit dem Satz, dass nichts
geaendert ist.

Ohne Datenbank: Repository und Verifikation sind ersetzt, die Uhr des
Zeitparsers steht auf Donnerstag, 15.10.2026, 08:00 Ortszeit. Die Termine und
Saetze sind synthetisch.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from dataclasses import replace
from datetime import date, datetime, time, timezone
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from agents.base import AgentResult
from agents.timeline import crud as timeline_crud
from agents.timeline import positive_form
from graph.nodes import planner as planner_mod
from graph.nodes.responder import _build_system_prompt
from utils import zeitparser
from utils.zeitparser import TimeReading, ZeitVektor, zeit_parsen_vektor

TZ: ZoneInfo = ZoneInfo("Europe/Berlin")

#: Donnerstag, 15.10.2026, 08:00 in Berlin (Sommerzeit, UTC+2).
FROZEN_UTC: datetime = datetime(2026, 10, 15, 6, 0, tzinfo=timezone.utc)

#: Freitag, 16.10.2026, 10:00 Ortszeit — der Termin der meisten Faelle.
FRIDAY_10: datetime = datetime(2026, 10, 16, 10, 0, tzinfo=TZ)

#: Der Tag der eingefrorenen Uhr, fuer die Tage des Monats in `_read_time`.
TODAY: date = date(2026, 10, 15)

#: Lesungen fuer die Helfer: eine Stunde ("11 Uhr"); zwei ohne Lage (b); zwei
#: als "von 10 auf 11"; ein Tag des Monats ("auf den 20.").
ELEVEN: TimeReading = TimeReading(hours=frozenset({(11, 0)}), stated=frozenset({(11, 0)}))
TEN_OR_ELEVEN: TimeReading = TimeReading(hours=frozenset({(10, 0), (11, 0)}), undecided=True)
TEN_TO_ELEVEN: TimeReading = replace(TEN_OR_ELEVEN, stated=frozenset({(11, 0)}),
                                     undecided=False)
DAY_20: TimeReading = TimeReading(days=frozenset({date(2026, 10, 20)}))

SENTENCE_CLOCK_ONLY: str = "Verschieb den Zahnarzt bitte auf 11 Uhr."

#: Alte und neue Uhrzeit in einem Satz; die hinter "auf" ist die neue.
SENTENCE_FROM_TO: str = "Verschieb den Zahnarzt von 10 Uhr auf 11 Uhr."

#: Der Text, mit dem `_update` ohne Datum endet; synthetischer Titel.
AGENT_ERROR: str = "Konnte das neue Datum nicht erkennen. Wann soll 'Wartung' stattfinden?"


def _frozen(utc: datetime) -> type:
    """Baut eine `datetime`-Klasse, deren `now()` den Zeitpunkt `utc` liefert."""
    class Frozen(datetime):
        @classmethod
        def now(cls, tz: ZoneInfo | None = None) -> datetime:
            return utc.astimezone(tz) if tz else utc.replace(tzinfo=None)

    return Frozen


def _state(prompt: str, time_expression: str, event_time: datetime) -> dict:
    """Ein Auftrag `reschedule` an den Timeline-Agenten, wie ihn `_update` liest."""
    return {
        "aufgabe": prompt,
        "kontext": {"user_id": "pruefer", "character_id": "nova"},
        "parameter": {
            "action": "reschedule",
            "zeitausdruck": time_expression,
            "termin": {
                "id": 41,
                "title": "Zahnarzt",
                "event_type": "termin",
                "event_time": event_time,
            },
        },
        "schritte": [],
    }


class _RescheduleCase(unittest.TestCase):
    """Friert die Uhr des Zeitparsers ein und ersetzt Repository und Verifikation."""

    def setUp(self) -> None:
        self.insert: MagicMock = MagicMock(return_value=4712)
        self.invalidate: MagicMock = MagicMock()
        for p in (
            patch.object(zeitparser, "datetime", _frozen(FROZEN_UTC)),
            patch.object(zeitparser, "TIMEZONE", "Europe/Berlin"),
            patch.object(timeline_crud, "TIMEZONE", "Europe/Berlin"),
            patch.object(timeline_crud, "_verifizieren_termin", return_value=True),
            patch("memory.repositories.timeline_repository.TimelineRepository.insert",
                  self.insert),
            patch("memory.repositories.timeline_repository.TimelineRepository.invalidate",
                  self.invalidate),
        ):
            p.start()
            self.addCleanup(p.stop)

    def _new_time(self, state: dict) -> datetime:
        """Faehrt `_update` und liefert die Zeit, mit der der neue Termin entsteht."""
        result: dict = timeline_crud._update(state)
        self.assertEqual(result["status"], "abgeschlossen", result)
        self.insert.assert_called_once()
        return self.insert.call_args.kwargs["event_time"]

    def _assert_error(self, state: dict) -> dict:
        """Faehrt `_update` und prueft: Fehler, kein Schreiben."""
        result: dict = timeline_crud._update(state)
        self.assertEqual(result["status"], "fehler", result)
        self.insert.assert_not_called()
        self.invalidate.assert_not_called()
        return result


class ThePairStaysTest(_RescheduleCase):
    """Der verschobene Termin gehoert demselben Paar; ohne Figur wird nichts angefasst."""

    def test_without_a_character_nothing_is_invalidated(self) -> None:
        """Geprueft vor `invalidate` — sonst waere der alte Termin weg und kein neuer da."""
        state: dict = _state(SENTENCE_CLOCK_ONLY, "", FRIDAY_10)
        state["kontext"]["character_id"] = ""

        result: dict = self._assert_error(state)

        self.assertEqual(result["schritte"][-1]["ergebnis"], "ohne_character_id")

    def test_twin_the_new_appointment_is_written_in_the_pair(self) -> None:
        self._new_time(_state(SENTENCE_CLOCK_ONLY, "", FRIDAY_10))

        self.assertEqual(self.insert.call_args.kwargs["character_id"], "nova")
        self.invalidate.assert_called_once()


class ClockTimeOnlyTest(_RescheduleCase):
    """Nur eine neue Uhrzeit: Der Tag des Termins bleibt."""

    def test_clock_time_alone_moves_on_the_same_day(self) -> None:
        """Der Ausgangsfall: kein Zeitausdruck, die Uhrzeit nur im Satz."""
        new_time: datetime = self._new_time(_state(SENTENCE_CLOCK_ONLY, "", FRIDAY_10))

        self.assertEqual(new_time.astimezone(TZ), datetime(2026, 10, 16, 11, 0, tzinfo=TZ))
        self.assertEqual(self.insert.call_args.kwargs["precision"], "minute")
        self.invalidate.assert_called_once()

    def test_every_form_of_the_time_expression_gives_the_same_time(self) -> None:
        """Mit Zeitausdruck lief schon ein anderer Zweig — er muss dasselbe ergeben."""
        for expression in ("", "11 Uhr", "auf 11 Uhr"):
            with self.subTest(zeitausdruck=expression):
                self.insert.reset_mock()
                new_time: datetime = self._new_time(
                    _state(SENTENCE_CLOCK_ONLY, expression, FRIDAY_10)
                )
                self.assertEqual(new_time.astimezone(TZ),
                                 datetime(2026, 10, 16, 11, 0, tzinfo=TZ))

    def test_the_clock_time_is_local_time_not_utc(self) -> None:
        """Ein Termin, der in UTC ankommt: 11 Uhr heisst 11 Uhr hier, nicht 11:00Z."""
        in_utc: datetime = FRIDAY_10.astimezone(timezone.utc)

        new_time: datetime = self._new_time(_state(SENTENCE_CLOCK_ONLY, "", in_utc))

        self.assertEqual(new_time.astimezone(TZ), datetime(2026, 10, 16, 11, 0, tzinfo=TZ))

    def test_an_appointment_without_time_keeps_its_local_day(self) -> None:
        """Mitternacht Ortszeit ist in UTC der Vortag — der Tag kommt aus der Ortszeit."""
        midnight_utc: datetime = datetime(2026, 10, 16, 0, 0, tzinfo=TZ).astimezone(timezone.utc)

        new_time: datetime = self._new_time(_state(SENTENCE_CLOCK_ONLY, "", midnight_utc))

        self.assertEqual(new_time.astimezone(TZ), datetime(2026, 10, 16, 11, 0, tzinfo=TZ))
        self.assertEqual(self.insert.call_args.kwargs["precision"], "minute")


class DayOnlyTest(_RescheduleCase):
    """Nur ein neuer Tag: Die Uhrzeit des Termins bleibt."""

    def test_own_weekday_means_the_next_one(self) -> None:
        """Der 16.10.2026 ist ein Freitag; "auf Freitag" verschiebt ihn um eine Woche."""
        new_time: datetime = self._new_time(
            _state("Verschieb den Zahnarzt auf Freitag.", "Freitag", FRIDAY_10)
        )

        self.assertEqual(new_time.astimezone(TZ), datetime(2026, 10, 23, 10, 0, tzinfo=TZ))

    def test_another_weekday_keeps_its_week(self) -> None:
        """Zwilling: Ein Termin am Donnerstag geht auf den Freitag derselben Woche."""
        thursday_18: datetime = datetime(2026, 10, 15, 18, 0, tzinfo=TZ)

        new_time: datetime = self._new_time(
            _state("Verschieb den Zahnarzt auf Freitag.", "Freitag", thursday_18)
        )

        self.assertEqual(new_time.astimezone(TZ), datetime(2026, 10, 16, 18, 0, tzinfo=TZ))

    def test_a_day_word_for_the_same_day_does_not_move_a_week(self) -> None:
        """Zwilling: Nur der genannte Wochentag schiebt — "morgen" ist der 16.10."""
        new_time: datetime = self._new_time(
            _state("Verschieb den Zahnarzt auf morgen.", "morgen", FRIDAY_10)
        )

        self.assertEqual(new_time.astimezone(TZ), datetime(2026, 10, 16, 10, 0, tzinfo=TZ))

    def test_a_day_in_the_sentence_counts_like_the_same_expression(self) -> None:
        """Ohne Zeitausdruck zaehlt der Tag des Satzes wie derselbe als Zeitausdruck.

        dateparser liest den Satz nicht; der Tagesausdruck allein rechnet vom
        Termin aus, ein Montag spaeter als der naechste Freitag ab heute.
        """
        monday_26: datetime = datetime(2026, 10, 26, 10, 0, tzinfo=TZ)
        moved: dict = {}
        for expression in ("", "Freitag"):
            with self.subTest(zeitausdruck=expression):
                self.insert.reset_mock()
                moved[expression] = self._new_time(
                    _state("Verschieb den Zahnarzt auf Freitag.", expression, monday_26)
                ).astimezone(TZ)
                self.assertEqual(moved[expression].weekday(), 4)
                self.assertEqual(moved[expression].time(), time(10, 0))
                self.assertGreater(moved[expression], monday_26)
        self.assertEqual(moved[""], moved["Freitag"])

    def test_a_further_day_word_in_the_sentence_asks_back(self) -> None:
        """Abweisung: Ein weiteres Wort am Tag macht den Tag ungewiss — Rueckfrage."""
        for sentence in (
            "Verschieb den Zahnarzt auf Freitag nächste Woche.",
            "Verschieb den Zahnarzt auf heute Freitag.",
        ):
            with self.subTest(satz=sentence):
                self._assert_error(_state(sentence, "", FRIDAY_10))


class NoTimeTest(_RescheduleCase):
    """Weder Tag noch brauchbare Uhrzeit: der Fehler mit Rueckfrage wie bisher."""

    def test_neither_day_nor_time_asks_back(self) -> None:
        result: dict = self._assert_error(_state("Verschieb den Zahnarzt bitte.", "", FRIDAY_10))

        self.assertIn("Wann soll 'Zahnarzt' stattfinden?", result["fehler"])

    def test_an_impossible_time_asks_back(self) -> None:
        self._assert_error(_state("Verschieb den Zahnarzt auf 25 Uhr.", "", FRIDAY_10))

    def test_a_contradicting_day_is_not_rescued_by_the_time(self) -> None:
        """Ein Tag, der nicht aufgeht, faellt nicht still auf den Tag des Termins zurueck."""
        self._assert_error(_state(
            "Verschieb den Zahnarzt auf heute Freitag um 11 Uhr.",
            "heute Freitag um 11 Uhr", FRIDAY_10,
        ))


class FromToTest(_RescheduleCase):
    """Zwei Uhrzeiten im Satz: Die hinter "auf" oder "nach" ist die neue."""

    def test_the_time_after_auf_or_nach_is_the_new_one(self) -> None:
        for sentence, expression in (
            (SENTENCE_FROM_TO, ""),
            (SENTENCE_FROM_TO, "von 10 Uhr auf 11 Uhr"),
            ("Verschieb den Zahnarzt von 10 Uhr nach 11 Uhr.", ""),
        ):
            with self.subTest(satz=sentence, zeitausdruck=expression):
                self.insert.reset_mock()
                new_time: datetime = self._new_time(_state(sentence, expression, FRIDAY_10))
                self.assertEqual(new_time.astimezone(TZ),
                                 datetime(2026, 10, 16, 11, 0, tzinfo=TZ))

    def test_from_ten_to_half_past_eleven(self) -> None:
        """Die alte Zeit ohne "Uhr", die neue mit Minuten."""
        new_time: datetime = self._new_time(
            _state("Verschieb den Zahnarzt von 10 auf 11:30.", "", FRIDAY_10)
        )

        self.assertEqual(new_time.astimezone(TZ), datetime(2026, 10, 16, 11, 30, tzinfo=TZ))

    def test_two_times_without_auf_or_nach_ask_back(self) -> None:
        """Zwilling der beiden oben: Ohne "auf"/"nach" waere die Wahl geraten."""
        for expression in ("", "zwischen 10 Uhr und 11 Uhr"):
            with self.subTest(zeitausdruck=expression):
                self._assert_error(_state(
                    "Verschieb den Zahnarzt zwischen 10 Uhr und 11 Uhr.", expression, FRIDAY_10,
                ))

    def test_a_span_or_a_choice_asks_back(self) -> None:
        """Zwei Stunden ohne "auf"/"nach" oder eine Spanne: Rueckfrage, kein Schreiben.

        Jede Form zaehlt als Stunde, auch die nackte "10" — in Satz und Zeitausdruck.
        """
        for phrase in (
            "zwischen 10 und 11 Uhr", "10 bis 12 Uhr", "von 10 bis 12 Uhr",
            "von 10 Uhr bis 12 Uhr", "um 10 oder 11 Uhr", "10–12 Uhr",
        ):
            for expression in ("", phrase):
                with self.subTest(satz=phrase, zeitausdruck=expression):
                    self._assert_error(
                        _state(f"Verschieb den Zahnarzt {phrase}.", expression, FRIDAY_10)
                    )

    def test_one_hour_or_one_after_auf_is_written(self) -> None:
        """Zwilling: Genau eine Stunde, oder genau eine hinter "auf" — geschrieben wird sie."""
        for phrase, expression, expected in (
            ("auf 11 Uhr", "auf 11 Uhr", datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("von 10 auf 11 Uhr", "von 10 auf 11 Uhr", datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("von 10 auf 11:30", "von 10 auf 11:30", datetime(2026, 10, 16, 11, 30, tzinfo=TZ)),
            ("auf den 20. um 11 Uhr", "auf den 20. um 11 Uhr",
             datetime(2026, 10, 20, 11, 0, tzinfo=TZ)),
            ("auf Freitag", "Freitag", datetime(2026, 10, 23, 10, 0, tzinfo=TZ)),
        ):
            for given in ("", expression):
                with self.subTest(satz=phrase, zeitausdruck=given):
                    self.insert.reset_mock()
                    new_time: datetime = self._new_time(
                        _state(f"Verschieb den Zahnarzt {phrase}.", given, FRIDAY_10)
                    )
                    self.assertEqual(new_time.astimezone(TZ), expected)

    def test_two_hours_after_auf_or_a_choice_ask_back(self) -> None:
        """Hinter "auf"/"nach" zwei Stunden, oder ein "oder" dazwischen: Rueckfrage.

        Massgeblich ist der Bereich hinter dem Wort bis zum Satzende, nicht nur
        die Stunde direkt dahinter — "auf 10 oder 11 Uhr" schrieb sonst 10:00.
        """
        for phrase in (
            "auf 10 oder 11 Uhr", "auf 10 Uhr oder 11 Uhr", "nach 10 oder 11 Uhr",
            "auf 11 oder 12", "auf 10, 11 Uhr", "von 10 auf 11 oder 12 Uhr",
        ):
            for expression in ("", phrase):
                with self.subTest(satz=phrase, zeitausdruck=expression):
                    self._assert_error(
                        _state(f"Verschieb den Zahnarzt {phrase}.", expression, FRIDAY_10)
                    )

    def test_a_choice_in_the_time_expression_asks_back(self) -> None:
        """Ein "oder" im Zeitausdruck zaehlt, auch bei einer Stunde hinter "auf" im Satz."""
        for sentence in ("Verschieb den Zahnarzt.", "Verschieb den Zahnarzt auf 11 Uhr."):
            with self.subTest(satz=sentence):
                self._assert_error(_state(sentence, "10 oder 11 Uhr", FRIDAY_10))

    def test_an_auf_for_each_hour_asks_back(self) -> None:
        """Jede Stunde mit eigenem "auf", Wahl, Verneinung, zweiter Termin: Rueckfrage.

        Mehr als eine Stunde gilt nur in der Form "von X auf Y" — jede andere
        Form fragt zurueck, auch eine, die der Code nicht kennt.
        """
        for phrase in (
            "auf 11, nicht auf 10 Uhr", "auf 11 statt auf 10 Uhr", "auf 10 Uhr, sonst auf 11 Uhr",
            "auf 10 Uhr bzw. auf 11 Uhr", "auf 11 Uhr und den Friseur auf 14 Uhr",
        ):
            for expression in ("", phrase):
                with self.subTest(satz=phrase, zeitausdruck=expression):
                    self._assert_error(
                        _state(f"Verschieb den Zahnarzt {phrase}.", expression, FRIDAY_10)
                    )

    def test_a_spelled_hour_counts_like_a_digit(self) -> None:
        """Ein Zahlwort ist eine Stunde: Mit einer zweiten ausserhalb "von X auf Y" fragt Nova.

        Vorher zaehlte nur "elf Uhr" — "auf zehn, nicht auf elf Uhr" schrieb 11:00.
        """
        for phrase in (
            "auf zehn, nicht auf elf Uhr", "auf elf oder zwölf Uhr", "auf zehn Uhr oder elf",
            "von 10 auf 11 Uhr, lieber zwölf", "auf halb elf oder elf",
        ):
            for expression in ("", phrase):
                with self.subTest(satz=phrase, zeitausdruck=expression):
                    self._assert_error(
                        _state(f"Verschieb den Zahnarzt {phrase}.", expression, FRIDAY_10)
                    )

    def test_one_spelled_hour_or_an_ordinal_day_is_written(self) -> None:
        """Zwilling: Ein Zahlwort allein ist die neue Stunde, eine Ordinalzahl ist ein Tag."""
        for phrase, expected in (
            ("auf elf Uhr", datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("von zehn auf elf Uhr", datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("auf den zehnten um 11 Uhr", datetime(2026, 11, 10, 11, 0, tzinfo=TZ)),
        ):
            for expression in ("", phrase):
                with self.subTest(satz=phrase, zeitausdruck=expression):
                    self.insert.reset_mock()
                    new_time: datetime = self._new_time(
                        _state(f"Verschieb den Zahnarzt {phrase}.", expression, FRIDAY_10)
                    )
                    self.assertEqual(new_time.astimezone(TZ), expected)

    def test_a_doubtful_spelled_form_asks_back(self) -> None:
        """Eine Form, deren Stunde allein eine andere Zeit waere, oder ein Tag ohne Artikel.

        Zwillinge: "auf elf Uhr" und "auf den zehnten um 11 Uhr" oben.
        "bitte" haelt den Satzpunkt von der Zahl fern — "11." waere schon als Tag ein Zweifel.
        """
        for phrase in (
            "auf viertel nach 11 bitte", "auf elf Uhr dreißig", "am zehnten um 11 Uhr",
            "auf dreizehn Uhr 30 bitte",
        ):
            for expression in ("", phrase):
                with self.subTest(satz=phrase, zeitausdruck=expression):
                    self._assert_error(
                        _state(f"Verschieb den Zahnarzt {phrase}.", expression, FRIDAY_10)
                    )

    def test_one_hour_in_the_range_after_auf_is_still_written(self) -> None:
        """Zwilling der Rueckfragen oben: eine Stunde, oder genau "von X auf/nach Y"."""
        for phrase, expected in (
            ("auf 11 Uhr", datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("von 10 auf 11 Uhr", datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("von 10 nach 11 Uhr", datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("von 10 auf 11:30", datetime(2026, 10, 16, 11, 30, tzinfo=TZ)),
            ("auf den 20. um 11 Uhr", datetime(2026, 10, 20, 11, 0, tzinfo=TZ)),
            ("auf Freitag", datetime(2026, 10, 23, 10, 0, tzinfo=TZ)),
        ):
            with self.subTest(satz=phrase):
                self.insert.reset_mock()
                new_time: datetime = self._new_time(
                    _state(f"Verschieb den Zahnarzt {phrase}.", "", FRIDAY_10)
                )
                self.assertEqual(new_time.astimezone(TZ), expected)

    def test_a_dated_guess_does_not_decide_the_time(self) -> None:
        """Rechnet der Parser ein Datum mit der alten Uhrzeit dazu, gilt die Lesung."""
        guess = ZeitVektor(datum=datetime(2026, 10, 15, 10, 0, tzinfo=TZ), tag_erkannt=False,
                           uhrzeit_erkannt=True, referenz_modus="relativ")
        with patch.object(zeitparser, "zeit_parsen_vektor", return_value=guess):
            new_time: datetime = self._new_time(_state(SENTENCE_FROM_TO, "", FRIDAY_10))

        self.assertEqual(new_time.astimezone(TZ), datetime(2026, 10, 16, 11, 0, tzinfo=TZ))

    def test_a_dated_guess_without_a_clear_time_asks_back(self) -> None:
        """Zwilling: Dasselbe Datum bei unklarer Lesung wird nicht still geschrieben."""
        guess = ZeitVektor(datum=datetime(2026, 10, 15, 10, 0, tzinfo=TZ), tag_erkannt=False,
                           uhrzeit_erkannt=True, referenz_modus="relativ")
        with patch.object(zeitparser, "zeit_parsen_vektor", return_value=guess):
            self._assert_error(
                _state("Verschieb den Zahnarzt zwischen 10 und 11 Uhr.", "", FRIDAY_10)
            )

    def test_a_named_day_with_two_times_takes_the_one_after_auf(self) -> None:
        """Ein Tag vom Parser, die Uhrzeit aus der Lesung: Freitag 11:00, nicht 10:00."""
        new_time: datetime = self._new_time(_state(
            "Verschieb den Zahnarzt auf Freitag von 10 auf 11 Uhr.", "", datetime(
                2026, 10, 15, 18, 0, tzinfo=TZ),
        ))

        self.assertEqual(new_time.astimezone(TZ), datetime(2026, 10, 16, 11, 0, tzinfo=TZ))


class ReadTimeTest(_RescheduleCase):
    """Die Lesung zaehlt jede Stunde und jeden Tag des Monats — der Parser tut es nicht."""

    def test_the_sentence_has_a_clock_time_and_no_date(self) -> None:
        """Der Parser liefert fuer den Ausgangssatz kein Datum; die Lesung liefert 11:00."""
        vector: ZeitVektor = zeit_parsen_vektor(SENTENCE_CLOCK_ONLY)

        self.assertIsNone(vector.datum)
        self.assertTrue(vector.uhrzeit_erkannt)
        self.assertEqual(zeitparser.read_time(SENTENCE_CLOCK_ONLY).clock_time(), time(11, 0))

    def test_an_impossible_time_gives_no_clock_time(self) -> None:
        reading: TimeReading = zeitparser.read_time("Verschieb den Zahnarzt auf 25 Uhr.")

        self.assertIsNone(reading.clock_time())
        self.assertTrue(reading.unclear())

    def test_read_time_on_normalized_texts(self) -> None:
        """Die neue Uhrzeit aus dem Text, wie die Normalisierung ihn schreibt."""
        for normalized, expected in (
            ("verschieb den zahnarzt bitte auf 11:00.", time(11, 0)),
            ("um 9:30 und nochmal 9:30", time(9, 30)),
            ("von 10:00 bis 12:00", None),
            ("um 25:00", None),
            ("um 10:75", None),
            ("ohne uhrzeit", None),
            ("von 10:00 auf 11:00", time(11, 0)),
            ("von 10:00 nach 11:30", time(11, 30)),
            ("zwischen 10:00 und 11:00", None),
            ("von 10:00 auf 11:00 oder auf 12:00", None),
            ("von 10:00auf 11:00.", time(11, 0)),
            ("von 10:00nach 11:30.", time(11, 30)),
            ("ablauf 11:00 und 10:00", None),
            ("von 10 bis 12:00.", None),
            ("auf 10 bis 12:00", None),
            ("von 10 auf 11:00.", time(11, 0)),
            ("von 10 nach 11:30.", time(11, 30)),
            ("nach 3 tagen, 11:00", time(11, 0)),
            ("auf 16.10. um 11:00", time(11, 0)),
            ("zwischen 10 und 11:00", None),
            ("10 bis 12:00", None),
            ("10–12:00", None),
            ("10:00 oder 11:00", None),
            ("auf 11", time(11, 0)),
            ("meeting 2 auf freitag", None),
            ("auf 11.", None),
            ("10:002026-10-16", time(10, 0)),
            ("auf 2026-10-16 11:00", time(11, 0)),
            ("auf den 20. 11:00", time(11, 0)),
        ):
            with self.subTest(text=normalized):
                self.assertEqual(zeitparser._read_time(normalized, TODAY).clock_time(), expected)

    def test_a_day_of_the_month_or_a_doubt(self) -> None:
        """Eine Zahl mit Punkt ist ein Tag hinter einem Artikel, sonst ein Zweifel."""
        named: TimeReading = zeitparser._read_time("auf den 20. 11:00", TODAY)
        self.assertEqual(named.day(), date(2026, 10, 20))
        self.assertFalse(named.unclear())
        self.assertEqual(zeitparser._read_time("auf 20. oktober", TODAY).day(), date(2026, 10, 20))
        doubt: TimeReading = zeitparser._read_time("auf 11.", TODAY)
        self.assertTrue(doubt.doubtful)
        self.assertIsNone(doubt.day())
        self.assertTrue(doubt.unclear())
        self.assertTrue(zeitparser._read_time("vom 16. auf den 20.", TODAY).unclear())

    def test_a_lone_bare_number_asks_back_and_after_auf_it_is_the_time(self) -> None:
        """Eine nackte Zahl allein ist im Zweifel; hinter "auf" ist sie die neue Uhrzeit."""
        alone: TimeReading = zeitparser._read_time("meeting 2 auf freitag", TODAY)
        self.assertEqual(alone.hours, frozenset({(2, 0)}))
        self.assertTrue(alone.unclear())
        self.assertFalse(zeitparser._read_time("auf 11", TODAY).unclear())

    def test_the_sentences_through_the_normalization(self) -> None:
        """Gelesen wird der Text der Normalisierung — sie klebt "10:00" an "auf"."""
        for sentence, expected in (
            (SENTENCE_FROM_TO, time(11, 0)),
            ("Verschieb den Zahnarzt von 10 Uhr nach 11 Uhr.", time(11, 0)),
            ("Verschieb den Zahnarzt von 10 Uhr 30 auf 11 Uhr.", time(11, 0)),
            ("Verschieb den Zahnarzt von 10 auf 11 Uhr.", time(11, 0)),
            ("Verschieb den Zahnarzt von 10 auf 11:30.", time(11, 30)),
            ("Verschieb den Zahnarzt auf den 20. um 11 Uhr.", time(11, 0)),
            ("Verschieb den Zahnarzt zwischen 10 Uhr und 11 Uhr.", None),
            ("Verschieb den Zahnarzt zwischen 10 und 11 Uhr.", None),
            ("Verschieb den Zahnarzt von 10 bis 12 Uhr.", None),
            ("Verschieb den Zahnarzt von 10 Uhr bis 12 Uhr.", None),
            ("Verschieb den Zahnarzt 10 bis 12 Uhr.", None),
            ("Verschieb den Zahnarzt um 10 oder 11 Uhr.", None),
            ("Verschieb den Zahnarzt 10–12 Uhr.", None),
        ):
            with self.subTest(sentence=sentence):
                self.assertEqual(zeitparser.read_time(sentence).clock_time(), expected)

    def test_stated_hour_takes_only_the_two_forms(self) -> None:
        """`stated` nur in Lage (a) oder in der Form "von X auf/nach Y" — sonst unentschieden."""
        for normalized, stated in (
            ("auf 11:00", {(11, 0)}),
            ("auf 11", {(11, 0)}),
            ("von 10 auf 11:00", {(11, 0)}),
            ("von 10 nach 11:00", {(11, 0)}),
            ("von 10:00auf 11:30.", {(11, 30)}),
            ("auf freitag von 10 auf 11:00", {(11, 0)}),
            ("auf 10 oder 11:00", set()),
            ("auf 10, 11:00", set()),
            ("auf 11, nicht auf 10:00", set()),
            ("auf 11 statt auf 10:00", set()),
            ("auf 10:00, sonst auf 11:00", set()),
            ("auf 10:00 bzw. auf 11:00", set()),
            ("auf 11:00 und den friseur auf 14:00", set()),
            ("von 10 auf 11:00 oder spaeter", set()),
            ("von 10 auf 11:00 und nicht frueher", set()),
            ("vom termin 10 auf 11:00", set()),
            ("von 10 und dann auf 11:00", set()),
            ("von 10 bis 12:00", set()),
            ("meeting 2 auf freitag", set()),
        ):
            with self.subTest(text=normalized):
                reading: TimeReading = zeitparser._read_time(normalized, TODAY)
                self.assertEqual(reading.stated, frozenset(stated))
                self.assertIs(reading.undecided, not stated)

    def test_undecided_gives_no_clock_time(self) -> None:
        """Ein unentschiedener Text haelt auch eine Stunde des anderen Textes an."""
        self.assertEqual(TEN_TO_ELEVEN.clock_time(), time(11, 0))
        self.assertIsNone(replace(TEN_TO_ELEVEN, undecided=True).clock_time())
        self.assertIsNone(TEN_TO_ELEVEN.merged(TEN_OR_ELEVEN).clock_time())
        self.assertTrue(TEN_TO_ELEVEN.merged(TEN_OR_ELEVEN).undecided)

    def test_stated_hour_rejects_a_position_outside_the_text(self) -> None:
        """Eine Stelle hinter dem Text ist ein Programmierfehler; Zwilling: die Stelle im Text."""
        with self.assertRaises(ValueError):
            zeitparser._stated_hour("auf 11", [(4, 9, (11, 0), False)])
        self.assertEqual(zeitparser._stated_hour("auf 11", [(4, 6, (11, 0), False)]),
                         frozenset({(11, 0)}))

    def test_the_from_to_sentence_has_no_day_and_reads_eleven(self) -> None:
        """Der Vektor erkennt eine Uhrzeit ohne Tag; die neue liefert die Lesung."""
        vector: ZeitVektor = zeit_parsen_vektor(SENTENCE_FROM_TO)

        self.assertTrue(vector.uhrzeit_erkannt)
        self.assertFalse(vector.tag_erkannt)
        self.assertEqual(zeitparser.read_time(SENTENCE_FROM_TO).clock_time(), time(11, 0))

    def test_the_patterns_at_their_borders(self) -> None:
        """Die Muster der Lesung, mit Zwilling je Abweisung."""
        self.assertEqual(zeitparser._BARE_NUMBER.findall("von 10 bis 12"), ["10", "12"])
        for text in ("nach 3 tagen", "11:00", "10 euro", "meeting2", "2,5"):
            with self.subTest(bare=text):
                self.assertEqual(zeitparser._BARE_NUMBER.findall(text), [])
        self.assertEqual(zeitparser._DATE_DIGITS.findall("am 16.10. und 2026-10-16"),
                         ["16.10.", "2026-10-16"])
        self.assertIsNone(zeitparser._DATE_DIGITS.search("11:00"))
        self.assertEqual(zeitparser._DAY_OF_MONTH.search("den 20. um").group(1), "20")
        self.assertEqual(zeitparser._DAY_OF_MONTH.search("20 oktober").group(2), "oktober")
        self.assertIsNone(zeitparser._DAY_OF_MONTH.search("um 11 uhr 10.30"))
        self.assertIsNotNone(zeitparser._ARTICLE_BEFORE.search("auf den "))
        self.assertIsNone(zeitparser._ARTICLE_BEFORE.search("auf "))
        self.assertIsNotNone(zeitparser._NEW_TIME_WORD_BEFORE.search("bitte auf "))
        self.assertIsNotNone(zeitparser._NEW_TIME_WORD_BEFORE.search("nach "))
        for text in ("ablauf ", "danach ", "auf freitag "):
            with self.subTest(new_time_word=text):
                self.assertIsNone(zeitparser._NEW_TIME_WORD_BEFORE.search(text))
        self.assertIsNotNone(zeitparser._FROM_BEFORE.search("verschieb ihn von "))
        self.assertIsNone(zeitparser._FROM_BEFORE.search("vom "))
        for text in ("auf ", " auf ", " nach "):
            with self.subTest(between=text):
                self.assertIsNotNone(zeitparser._TO_BETWEEN.fullmatch(text))
        for text in (" bis ", " oder ", ", ", " uhr auf "):
            with self.subTest(between=text):
                self.assertIsNone(zeitparser._TO_BETWEEN.fullmatch(text))
        for text in ("oder spaeter", "bzw. 12", "und den friseur", ":00nicht", "statt 10"):
            with self.subTest(tail=text):
                self.assertIsNotNone(zeitparser._AFTER_TO_BREAK.search(text))
        for text in (".", " bitte verschieben.", " vorder", " hund"):
            with self.subTest(tail=text):
                self.assertIsNone(zeitparser._AFTER_TO_BREAK.search(text))

    def test_what_counts_as_a_spelled_hour(self) -> None:
        """Zahlwoerter null bis vierundzwanzig zaehlen; Ordinalzahl, Menge und "ein" nicht."""
        self.assertEqual(len(set(zeitparser._HOUR_WORDS.values())), 25)
        for text, hours in (
            ("auf elf", [11]), ("null oder vierundzwanzig", [0, 24]), ("zwoelf", [12]),
            ("fünfzehn und zwo", [15, 2]), ("auf zehn, nicht auf elf", [10, 11]),
            ("am zehnten", []), ("der elfte", []), ("zwei stunden", []), ("drei tage", []),
            ("ein termin", []), ("vierzehnmal", []),
        ):
            with self.subTest(text=text):
                found, doubt = zeitparser._spelled_hours(text)
                self.assertEqual([hour for _, _, (hour, _), _ in found], hours)
                self.assertFalse(doubt)
        written, doubt = zeitparser._spelled_hours("von dreizehn uhr auf")
        self.assertEqual(written, [(4, 16, (13, 0), True)])
        self.assertFalse(doubt)
        self.assertTrue(zeitparser._spelled_hours("auf dreizehn uhr 30")[1])
        self.assertTrue(zeitparser._spelled_hours("auf dreizehn uhr dreissig")[1])
        with self.assertRaises(TypeError):
            zeitparser._spelled_hours(None)

    def test_an_ordinal_is_a_day_or_a_doubt(self) -> None:
        """Eine Ordinalzahl ist ein Tag mit Artikel oder Monat, ohne beides ein Zweifel."""
        for text, days in (
            ("auf den zehnten 11:00", [date(2026, 11, 10)]),
            ("auf den zwanzigsten.", [date(2026, 10, 20)]),
            ("zum einunddreissigsten", [date(2026, 10, 31)]),
            ("einunddreissigsten november", [None]),
            ("einundzwanzigsten oktober", [date(2026, 10, 21)]),
            ("zehnten 11:00", [None]),
            ("den ersten termin auf 11:00", []),
        ):
            with self.subTest(text=text):
                self.assertEqual(zeitparser._ordinal_days(text, TODAY), days)
        self.assertEqual(len(set(zeitparser._ORDINAL_DAYS.values())), 31)
        with self.assertRaises(TypeError):
            zeitparser._ordinal_days(None, TODAY)

    def test_spelled_forms_through_read_time(self) -> None:
        """Zahlwort, Ordinalzahl und Zweifel im Text der Normalisierung — mit Zwillingen."""
        for normalized, expected, doubtful in (
            ("auf elf", time(11, 0), False),
            ("auf zehn, nicht auf 11:00", None, False),
            ("von zehn auf 11:00", time(11, 0), False),
            ("auf den zehnten 11:00", time(11, 0), False),
            ("auf viertel nach 11 bitte", None, True),
            ("auf 11:00dreißig", None, True),
            ("auf 11:00 dreissig", None, True),
            ("auf 11:15", time(11, 15), False),
            ("zehnten 11:00", None, True),
        ):
            with self.subTest(text=normalized):
                reading: TimeReading = zeitparser._read_time(normalized, TODAY)
                self.assertEqual(reading.clock_time(), expected)
                self.assertIs(reading.doubtful, doubtful)
        self.assertEqual(zeitparser._read_time("auf den zehnten 11:00", TODAY).day(),
                         date(2026, 11, 10))

    def test_the_spelled_patterns_at_their_borders(self) -> None:
        """Die Muster der Zahlwoerter, je mit Abweisung und Zwilling."""
        self.assertEqual(zeitparser._HOUR_WORD.findall("vierzehn vier"), ["vierzehn", "vier"])
        for text in ("elfte", "zwei wochen", "ein", "achtung"):
            with self.subTest(hour_word=text):
                self.assertEqual(zeitparser._HOUR_WORD.findall(text), [])
        self.assertIsNotNone(zeitparser._ORDINAL_DAY.search("den zehnten."))
        self.assertEqual(zeitparser._ORDINAL_DAY.search("dritten okt").group(2), "okt")
        self.assertIsNone(zeitparser._ORDINAL_DAY.search("den ersten termin"))
        self.assertIsNotNone(zeitparser._UHR_AFTER_WORD.match(" uhr"))
        self.assertIsNotNone(zeitparser._UHR_AFTER_WORD.match(" uhr 30").group(1))
        self.assertIsNone(zeitparser._UHR_AFTER_WORD.match(" uhr bitte").group(1))
        self.assertIsNotNone(zeitparser._MINUTES_AFTER_CLOCK.match("fünfundvierzig"))
        for text in (" bitte", "oder elf", ""):
            with self.subTest(minutes=text):
                self.assertIsNone(zeitparser._MINUTES_AFTER_CLOCK.match(text))
        for text in ("halb ", "viertel nach ", "dreiviertel "):
            with self.subTest(fraction=text):
                self.assertIsNotNone(zeitparser._FRACTION_BEFORE.search("auf " + text))
        self.assertIsNone(zeitparser._FRACTION_BEFORE.search("auf "))
        self.assertEqual(zeitparser._UNIT_WORDS[-1], "neun")

    def test_day_of_month(self) -> None:
        """Der naechste solche Tag ab heute; einen Tag, den es nicht gibt, gibt es nicht."""
        for day, month_word, today, expected in (
            (20, None, TODAY, date(2026, 10, 20)),
            (3, None, date(2026, 12, 15), date(2027, 1, 3)),
            (1, "oktober", TODAY, date(2027, 10, 1)),
            (20, "okt", TODAY, date(2026, 10, 20)),
            (31, None, date(2026, 11, 15), None),
            (0, None, TODAY, None),
        ):
            with self.subTest(day=day, month=month_word, today=today):
                self.assertEqual(zeitparser._day_of_month(day, month_word, today), expected)

    def test_reading_rejects_what_is_no_text(self) -> None:
        with self.assertRaises(TypeError):
            zeitparser._read_time(None, TODAY)
        with self.assertRaises(TypeError):
            zeitparser.read_time(None)
        with self.assertRaises(TypeError):
            TimeReading().merged("11:00")
        self.assertEqual(zeitparser.read_time("  "), TimeReading())

    def test_day_phrase_cuts_the_day_out_of_the_sentence(self) -> None:
        """Der Tagesausdruck allein — nur, wenn kein weiteres Wort am Tag mitrechnet."""
        for sentence, expected in (
            ("Verschieb den Zahnarzt auf Freitag.", "Freitag"),
            ("Verschieb den Zahnarzt auf Freitag von 10 auf 11 Uhr.", "Freitag"),
            ("Verschieb ihn auf nächsten Freitag.", "nächsten Freitag"),
            ("Verschieb ihn auf naechsten Freitag.", "naechsten Freitag"),
            ("Verschieb ihn auf morgen um 9 Uhr.", "morgen"),
            ("Verschieb ihn auf heute Freitag.", ""),
            ("Verschieb ihn auf Freitag nächste Woche.", ""),
            ("Verschieb ihn auf Freitag abends.", ""),
            ("Verschieb ihn auf Freitag, den 23.10.", ""),
            ("Verschieb ihn auf Freitag in drei Tagen.", ""),
            ("Verschieb ihn bitte.", ""),
        ):
            with self.subTest(satz=sentence):
                self.assertEqual(zeitparser.day_phrase(sentence), expected)
        with self.assertRaises(TypeError):
            zeitparser.day_phrase(None)

    def test_merged_counts_both_texts(self) -> None:
        """Aeusserung und Zeitausdruck zusammen: Eine Stunde, die nur einer nennt, zaehlt mit."""
        expression: TimeReading = TimeReading(hours=frozenset({(11, 0)}),
                                              stated=frozenset({(11, 0)}))
        prompt: TimeReading = TimeReading(hours=frozenset({(10, 0)}), stated=frozenset({(10, 0)}))

        self.assertEqual(expression.clock_time(), time(11, 0))
        self.assertIsNone(expression.merged(prompt).clock_time())
        self.assertTrue(expression.merged(prompt).unclear())


class HelperTest(unittest.TestCase):
    """Die Helfer von `_update` an ihren Grenzen."""

    def test_decided_by_reading(self) -> None:
        """Ein Tag des Monats, oder eine Uhrzeit ohne Tag vom Parser — sonst nicht."""
        no_day = ZeitVektor(datum=FRIDAY_10, tag_erkannt=False, uhrzeit_erkannt=True,
                            referenz_modus="relativ")
        with_day = replace(no_day, tag_erkannt=True)
        for name, vector, reading, expected in (
            ("Uhrzeit ohne Tag", no_day, ELEVEN, True),
            ("Tag des Monats", with_day, DAY_20, True),
            ("Uhrzeit mit Tag", with_day, ELEVEN, False),
            ("leere Lesung", no_day, TimeReading(), False),
            ("unklare Lesung", no_day, TEN_OR_ELEVEN, False),
        ):
            with self.subTest(fall=name):
                self.assertIs(timeline_crud._decided_by_reading(vector, reading), expected)
        with self.assertRaises(TypeError):
            timeline_crud._decided_by_reading(no_day, None)

    def test_no_new_time(self) -> None:
        """Rueckfrage, wo eine Zeit geraten waere; Zwilling je Lage."""
        nothing = ZeitVektor(datum=None, tag_erkannt=False, uhrzeit_erkannt=False,
                             referenz_modus="relativ")
        guessed = ZeitVektor(datum=FRIDAY_10, tag_erkannt=False, uhrzeit_erkannt=True,
                             referenz_modus="relativ")
        day = ZeitVektor(datum=FRIDAY_10, tag_erkannt=True, uhrzeit_erkannt=False,
                         referenz_modus="absolut")
        for name, vector, reading, expected in (
            ("nichts", nothing, TimeReading(), True),
            ("zwei Uhrzeiten, Datum geschaetzt", guessed, TEN_OR_ELEVEN, True),
            ("Uhrzeit im Parser, keine in der Lesung", guessed, TimeReading(), True),
            ("reine Uhrzeit", replace(nothing, uhrzeit_erkannt=True), ELEVEN, False),
            ("Uhrzeit, Datum geschaetzt", guessed, ELEVEN, False),
            ("Datum ohne Uhrzeit", replace(guessed, uhrzeit_erkannt=False), TimeReading(), False),
            ("Tag ohne Datum", replace(day, datum=None), ELEVEN, True),
            ("Tag, anderer Tag des Monats", day, DAY_20, True),
            ("Tag, derselbe Tag des Monats", day,
             TimeReading(days=frozenset({date(2026, 10, 16)})), False),
            ("Tag mit Uhrzeit hinter auf", replace(day, uhrzeit_erkannt=True), TEN_TO_ELEVEN,
             False),
            ("nur Tag des Monats", nothing, DAY_20, False),
        ):
            with self.subTest(fall=name):
                self.assertIs(timeline_crud._no_new_time(vector, reading), expected)

    def test_no_new_time_rejects_a_date_without_zone(self) -> None:
        """Ein Datum ohne Zone ist ein Programmierfehler."""
        naive = ZeitVektor(datum=FRIDAY_10.replace(tzinfo=None), tag_erkannt=True,
                           uhrzeit_erkannt=False, referenz_modus="relativ")
        with self.assertRaises(ValueError):
            timeline_crud._no_new_time(naive, TimeReading())

    def test_on_day_of(self) -> None:
        """Was die Lesung nennt, gilt; der Rest kommt vom Termin."""
        for name, reading, expected in (
            ("Uhrzeit", TimeReading(hours=frozenset({(11, 30)}), stated=frozenset({(11, 30)})),
             datetime(2026, 10, 16, 11, 30, tzinfo=TZ)),
            ("Tag", DAY_20, datetime(2026, 10, 20, 10, 0, tzinfo=TZ)),
            ("beides", replace(DAY_20, hours=ELEVEN.hours, stated=ELEVEN.stated),
             datetime(2026, 10, 20, 11, 0, tzinfo=TZ)),
        ):
            with self.subTest(fall=name):
                self.assertEqual(timeline_crud._on_day_of(reading, FRIDAY_10), expected)
        for name, reading, old_time in (
            ("ohne Zone", ELEVEN, FRIDAY_10.replace(tzinfo=None)),
            ("weder Tag noch Uhrzeit", TimeReading(), FRIDAY_10),
        ):
            with self.subTest(fall=name), self.assertRaises(ValueError):
                timeline_crud._on_day_of(reading, old_time)
        with self.assertRaises(TypeError):
            timeline_crud._on_day_of(None, FRIDAY_10)

    def test_choose_vector_keeps_the_hour_of_the_expression(self) -> None:
        """Gilt der Vektor der Aeusserung, zaehlt die Stunde des Zeitausdrucks trotzdem."""
        clock = ZeitVektor(datum=None, tag_erkannt=False, uhrzeit_erkannt=True,
                           referenz_modus="relativ")
        empty = ZeitVektor(datum=None, tag_erkannt=False, uhrzeit_erkannt=False,
                           referenz_modus="relativ")
        by_text: dict = {"11 Uhr": clock, "Bitte verschieben.": empty}
        with patch.object(zeitparser, "zeit_parsen_vektor", side_effect=by_text.__getitem__):
            vector, source_text, reading = timeline_crud._choose_vector(
                "11 Uhr", "Bitte verschieben.",
            )

        self.assertEqual((vector, source_text), (empty, "Bitte verschieben."))
        self.assertEqual(reading.clock_time(), time(11, 0))

    def test_choose_vector_takes_the_prompt_without_a_date(self) -> None:
        """Zwilling: Ohne Datum im Zeitausdruck entscheidet die Aeusserung, mit Datum nicht."""
        empty = ZeitVektor(datum=None, tag_erkannt=False, uhrzeit_erkannt=False,
                           referenz_modus="relativ")
        dated = ZeitVektor(datum=FRIDAY_10, tag_erkannt=True, uhrzeit_erkannt=True,
                           referenz_modus="absolut")
        by_text: dict = {"irgendwann": empty, "Freitag um 10 Uhr.": dated, "Freitag": dated,
                         "Bitte verschieben.": empty}
        with patch.object(zeitparser, "zeit_parsen_vektor", side_effect=by_text.__getitem__):
            self.assertEqual(
                timeline_crud._choose_vector("irgendwann", "Freitag um 10 Uhr.")[:2],
                (dated, "Freitag um 10 Uhr."),
            )
            self.assertEqual(timeline_crud._choose_vector(None, "Freitag um 10 Uhr.")[:2],
                             (dated, "Freitag um 10 Uhr."))
            self.assertEqual(timeline_crud._choose_vector("Freitag", "Bitte verschieben.")[:2],
                             (dated, "Freitag"))

    def test_choose_vector_takes_the_day_phrase_of_a_sentence(self) -> None:
        """Ein Tag ohne Datum im Satz: Es gilt der Tagesausdruck allein, wenn er eines ergibt."""
        day_only = ZeitVektor(datum=None, tag_erkannt=True, uhrzeit_erkannt=False,
                              referenz_modus="relativ")
        dated = replace(day_only, datum=FRIDAY_10)
        by_text: dict = {"Verschieb ihn auf Freitag.": day_only, "Freitag": dated,
                         "Verschieb ihn auf heute Freitag.": day_only}
        with patch.object(zeitparser, "zeit_parsen_vektor", side_effect=by_text.__getitem__):
            self.assertEqual(timeline_crud._choose_vector("", "Verschieb ihn auf Freitag.")[:2],
                             (dated, "Freitag"))
            self.assertEqual(
                timeline_crud._choose_vector(None, "Verschieb ihn auf heute Freitag.")[:2],
                (day_only, "Verschieb ihn auf heute Freitag."),
            )
            by_text["Freitag"] = day_only
            self.assertEqual(timeline_crud._choose_vector("", "Verschieb ihn auf Freitag.")[:2],
                             (day_only, "Verschieb ihn auf Freitag."))

    def test_choose_vector_rejects_a_non_text(self) -> None:
        with self.assertRaises(TypeError):
            timeline_crud._choose_vector("11 Uhr", None)

    def test_own_weekday_rejects_naive_times(self) -> None:
        with self.assertRaises(ValueError):
            timeline_crud._own_weekday_means_next_week(
                FRIDAY_10.replace(tzinfo=None), FRIDAY_10, "Freitag",
            )


class RawFormTest(_RescheduleCase):
    """Geschrieben wird nur, wenn Lesung und Positivform des Rohtexts einig sind.

    Die Positivform (`raw_time_form`) liest den Text vor jeder Normalisierung.
    Vorher schrieb die Lesung allein, und eine Schreibweise, die die
    Normalisierung umsetzt, verschluckt oder stehen laesst ("11h", "vom
    Vormittag auf den Nachmittag"), ergab still eine geratene Zeit.
    """

    def test_what_lies_outside_the_form_asks_back(self) -> None:
        """Weitere Stunde, "h", Tageszeitwort, Spanne mit Zahlwort: Rueckfrage, kein Schreiben."""
        for phrase in (
            "auf 11.30, nicht auf 12 Uhr", "auf 11.30 oder 12 Uhr", "auf 11h",
            "vom Vormittag auf den Nachmittag", "auf nachmittags statt vormittags",
            "auf abends, nicht auf 11 Uhr", "auf Freitag nachmittag", "von ein bis zwei Uhr",
            "zwischen ein und zwei Uhr",
        ):
            for expression in ("", phrase):
                with self.subTest(satz=phrase, zeitausdruck=expression):
                    self._assert_error(
                        _state(f"Verschieb den Zahnarzt {phrase}.", expression, FRIDAY_10)
                    )

    def test_a_fraction_of_an_hour_asks_back(self) -> None:
        """Ein Bruchteil ("halb", "viertel") liegt ausserhalb der Form — bisher 10:30 und 11:15."""
        for phrase in ("auf halb elf", "auf viertel nach elf"):
            for expression in ("", phrase):
                with self.subTest(satz=phrase, zeitausdruck=expression):
                    result: dict = self._assert_error(
                        _state(f"Verschieb den Zahnarzt {phrase}.", expression, FRIDAY_10)
                    )
                    self.assertIn("Wann soll 'Zahnarzt' stattfinden?", result["fehler"])

    def test_the_forms_are_written(self) -> None:
        """Zwilling der Rueckfragen: jede der fuenf Formen, mit Satz und mit Zeitausdruck."""
        thursday_18: datetime = datetime(2026, 10, 15, 18, 0, tzinfo=TZ)
        for phrase, expression, old_time, expected in (
            ("auf 11 Uhr", "auf 11 Uhr", FRIDAY_10, datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("auf 11.30", "auf 11.30", FRIDAY_10, datetime(2026, 10, 16, 11, 30, tzinfo=TZ)),
            ("auf elf Uhr", "elf Uhr", FRIDAY_10, datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("von 10 auf 11 Uhr", "von 10 auf 11 Uhr", FRIDAY_10,
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("von zehn auf elf Uhr", "von zehn auf elf Uhr", FRIDAY_10,
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("auf den 20. um 11 Uhr", "auf den 20. um 11 Uhr", FRIDAY_10,
             datetime(2026, 10, 20, 11, 0, tzinfo=TZ)),
            ("auf Freitag", "Freitag", FRIDAY_10, datetime(2026, 10, 23, 10, 0, tzinfo=TZ)),
            ("auf Freitag um 11", "Freitag um 11", thursday_18,
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("auf Freitag von 10 auf 11 Uhr", "Freitag", thursday_18,
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
        ):
            for given in ("", expression):
                with self.subTest(satz=phrase, zeitausdruck=given):
                    self.insert.reset_mock()
                    new_time: datetime = self._new_time(
                        _state(f"Verschieb den Zahnarzt {phrase}.", given, old_time)
                    )
                    self.assertEqual(new_time.astimezone(TZ), expected)

    def test_raw_time_form(self) -> None:
        """Die Form auf dem Rohtext: Uhrzeit, keine Uhrzeit, oder None — je mit Zwilling."""
        no_clock = positive_form.RawTimeForm()
        for text, expected in (
            ("Verschieb den Zahnarzt auf 11 Uhr.", time(11, 0)),
            ("Verschieb den Zahnarzt auf 11h.", None),
            ("auf elf Uhr", time(11, 0)),
            ("auf elf Uhr dreißig", None),
            ("Verschieb den Zahnarzt auf 11.30.", time(11, 30)),
            ("auf 11.30 oder 12 Uhr", None),
            ("von 10 auf 11:30", time(11, 30)),
            ("von 10 bis 11:30", None),
            ("von zehn auf elf Uhr", time(11, 0)),
            ("von ein bis zwei Uhr", None),
            ("Verschieb einen Zahnarzt auf ein Uhr.", time(1, 0)),
            ("auf mittags", None),
            ("auf den 20. um 11 Uhr", time(11, 0)),
            ("auf den zehnten um 11 Uhr", time(11, 0)),
            ("Freitag um 11", time(11, 0)),
            ("auf Freitag von 10 auf 11 Uhr", time(11, 0)),
            ("auf Freitag von 10 auf 11 oder 12 Uhr", None),
            ("auf 23:59", time(23, 59)),
            ("auf 25 Uhr", None),
            ("auf 11:75", None),
            ("auf halb elf", None),
        ):
            with self.subTest(text=text):
                form = positive_form.raw_time_form(text, "Zahnarzt")
                if expected is None:
                    self.assertIsNone(form)
                else:
                    self.assertEqual(form, positive_form.RawTimeForm(clock=expected))
        for text in ("Verschieb den Zahnarzt auf Freitag.", "Freitag", "auf morgen", "", "bitte"):
            with self.subTest(text=text):
                self.assertEqual(positive_form.raw_time_form(text, "Zahnarzt"), no_clock)
        with self.assertRaises(TypeError):
            positive_form.raw_time_form(None, "Zahnarzt")
        with self.assertRaises(TypeError):
            positive_form.raw_time_form("auf 11 Uhr", None)

    def test_only_what_is_admitted_stands_outside_the_form(self) -> None:
        """Ausserhalb der Form nur Verb, Fuellwort und Titel — jedes andere Wort: None.

        Bisher verbot die Pruefung, was zeitartig ist; "Fr." und "vorm." kannte
        keine Liste, und "auf Fr. um 11 Uhr" schrieb den alten Tag mit 11:00.
        """
        eleven = positive_form.RawTimeForm(clock=time(11, 0))
        for text, title, expected in (
            ("Verschieb ein Treffen auf 11 Uhr.", "Treffen", eleven),
            ("Verschieb ein Treffen auf 11 Uhr.", "Zahnarzt", None),
            ("Mittagessen auf 13 Uhr", "Mittagessen", positive_form.RawTimeForm(clock=time(13, 0))),
            ("Mittagessen auf 13 Uhr", "", None),
            ("Verschieb meinen Zahnarzttermin auf 11 Uhr.", "Zahnarzt Dr. Berger", eleven),
            # "Dr" hat keine vier Buchstaben, ist also kein Inhaltswort des Titels.
            ("Verschieb den Termin bei Dr. Berger auf 11 Uhr.", "Zahnarzt Dr. Berger", None),
            ("Verschieb den Termin bei Berger auf 11 Uhr.", "Zahnarzt Dr. Berger", eleven),
            ("Kannst du den Zahnarzt bitte auf 11 Uhr verschieben?", "Zahnarzt", eleven),
            ("Könntest du mir den Termin beim Zahnarzt noch auf 11 Uhr legen?", "Zahnarzt",
             eleven),
            ("Verschieb den Zahnarzt auf 11 Uhr flimmerig.", "Zahnarzt", None),
            ("Verschieb den Zahnarzt auf Fr. um 11 Uhr.", "Zahnarzt", None),
            ("Verschieb den Zahnarzt auf Mo um 11.", "Zahnarzt", None),
            ("Verschieb den Zahnarzt um 11 Uhr vorm.", "Zahnarzt", None),
            ("Verschieb den Zahnarzt auf 11 Uhr und den Friseur.", "Zahnarzt", None),
            ("Verschieb den Zahnarzt auf 11 Uhr.", "A", None),
            ("Verschieb den Geburtstag auf 11 Uhr.", "Geburtstag Oma", None),
            ("Verschieb den Zahnarzt auf 11 Uhr 2", "Zahnarzt 2", None),
        ):
            with self.subTest(text=text, titel=title):
                self.assertEqual(positive_form.raw_time_form(text, title), expected)

    def test_raw_outside_admitted(self) -> None:
        """Die Zulassung je Wortart, mit Zwilling; Satzzeichen sind keine Woerter."""
        for outside, title, expected in (
            ("Verschieb den Zahnarzt bitte .", "Zahnarzt", True),
            ("Verlegst du ihn ?", "", True),
            ("Ändere es mal", "", True),
            ("Pack diesen Termin doch", "", True),
            ("verschieblich", "", False),
            ("vom Zahnarzt", "Zahnarzt", False),
            ("Zahnärztin", "Zahnaerztin", True),
            ("Arzt", "A", False),
            ("Dr", "Zahnarzt Dr. Berger", False),
            ("Berger", "Zahnarzt Dr. Berger", True),
            ("Drei", "Zahnarzt Dr. Berger", False),
            ("Berger2", "Zahnarzt Dr. Berger", False),
            ("Arzt", "Arzt", True),
            ("Ort", "Ort", False),
            ("Fahrt", "Fahrt nach Hause", True),
            ("nach", "Fahrt nach Hause", False),
            ("nachm", "Fahrt nach Hause", False),
            ("Fahrten", "Fahrt nach Hause", False),
            ("Fahrttermin", "Fahrt nach Hause", True),
            ("Hausetermin", "Fahrt nach Hause", True),
            ("Nachtermin", "Fahrt nach Hause", False),
            ("Treffen", "Treffen vor Ort", True),
            ("vorm", "Treffen vor Ort", False),
            ("Zahnarztpraxis", "Zahnarzt", False),
            ("Zahnarzt2termin", "Zahnarzt", False),
            ("Zahnarztstermin", "Zahnarzt", True),
            ("Zahnarztxtermin", "Zahnarzt", False),
            ("Zahnarztnachmittagstermin", "Zahnarzt", False),
            ("Kaffee", "Kaffee nachm.", True),
            ("nachm", "Kaffee nachm.", False),
            ("vorm", "Kaffee vorm.", False),
            ("Blanc", "Mont Blanc", True),
            ("Mont", "Mont Blanc", False),
            ("Kaffee", "Kaffee oder Tee", True),
            ("oder", "Kaffee oder Tee", False),
            ("Runde", "Freitag Runde", True),
            ("Freitag", "Freitag Runde", False),
            ("", "", True),
            (" , . ? –", "", True),
        ):
            with self.subTest(ausserhalb=outside, titel=title):
                self.assertIs(positive_form._raw_outside_admitted(outside, title), expected)
        self.assertIn("beim", positive_form._RAW_ADMITTED_WORDS)
        self.assertNotIn("um", positive_form._RAW_ADMITTED_WORDS)
        self.assertIsNotNone(positive_form._RAW_ADMITTED_VERB.fullmatch("verschieben"))
        self.assertEqual(positive_form._RAW_TITLE_WORD.findall("Dr. Berger 2"), ["Dr", "Berger"])
        self.assertEqual(positive_form._RAW_TITLE_MIN_LETTERS, 4)
        self.assertEqual(positive_form._RAW_TITLE_COMPOUND_END, "termin")
        self.assertEqual(positive_form._RAW_TITLE_COMPOUND_JOINTS, ("", "s"))
        self.assertIn("nachmittag", positive_form._RAW_PARSER_WORDS)
        self.assertIn("vormittag", positive_form._RAW_PARSER_WORDS)
        for word in ("nach", "vor", "oder", "ueber", "zwischen", "meinem"):
            with self.subTest(funktionswort=word):
                self.assertIn(word, positive_form._RAW_FUNCTION_WORDS)
        self.assertIn("nach", positive_form._RAW_PARSER_WORDS)
        self.assertIn("freitag", positive_form._RAW_PARSER_WORDS)
        self.assertTrue(positive_form._RAW_TIME_WORDS < positive_form._RAW_PARSER_WORDS)
        self.assertTrue(all(word.lower() in positive_form._RAW_PARSER_WORDS
                            for word in zeitparser.TIME_VOCABULARY.words))
        with self.assertRaises(TypeError):
            positive_form._raw_outside_admitted(None, "")

    def test_a_unit_or_a_relative_word_outside_the_form_asks_back(self) -> None:
        """Zeiteinheit, relatives Praefix, "halbe", "Viertelstunde" — bisher alter Tag, 11:00."""
        for phrase in (
            "auf nächste Woche um 11 Uhr", "um 11 Uhr in einer Woche", "eine Stunde vor 11 Uhr",
            "eine Viertelstunde vor 11 Uhr", "eine halbe Stunde nach 11 Uhr",
        ):
            for expression in ("", phrase):
                with self.subTest(satz=phrase, zeitausdruck=expression):
                    self._assert_error(
                        _state(f"Verschieb den Zahnarzt {phrase}.", expression, FRIDAY_10)
                    )
        for sentence in ("Verschieb den Zahnarzt auf 11 Uhr.",
                         "Verschieb den Zahnarzt auf nächste Woche um 11 Uhr."):
            with self.subTest(satz=sentence, zeitausdruck="nächste Woche um 11 Uhr"):
                self._assert_error(_state(sentence, "nächste Woche um 11 Uhr", FRIDAY_10))

    def test_a_word_that_is_not_admitted_asks_back(self) -> None:
        """Kurzformen aus dateparser und ein erfundenes Wort: Rueckfrage, kein Schreiben.

        Bisher schrieb "auf Fr. um 11 Uhr" den alten Tag mit 11:00 — "Fr." stand
        in keiner Liste des Zeitparsers.
        """
        for phrase in (
            "auf Fr. um 11 Uhr", "auf Mo um 11", "um 11 Uhr vorm.", "um 11 Uhr, 2 Std. später",
            "um 11 Uhr in einer Woche", "auf 11 Uhr flimmerig",
        ):
            for expression in ("", phrase):
                with self.subTest(satz=phrase, zeitausdruck=expression):
                    result: dict = self._assert_error(
                        _state(f"Verschieb den Zahnarzt {phrase}.", expression, FRIDAY_10)
                    )
                    self.assertIn("Wann soll 'Zahnarzt' stattfinden?", result["fehler"])

    def test_admitted_sentences_are_written(self) -> None:
        """Zwilling: Bitte, Pronomen, Titel im Wort, anderes Verb — geschrieben."""
        thursday_18: datetime = datetime(2026, 10, 15, 18, 0, tzinfo=TZ)
        for sentence, expression, old_time, expected in (
            ("Verschieb den Zahnarzt auf 11 Uhr.", "auf 11 Uhr", FRIDAY_10,
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("Kannst du den Zahnarzt bitte auf 11 Uhr verschieben?", "11 Uhr", FRIDAY_10,
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("Verschieb meinen Zahnarzttermin auf 11 Uhr.", "auf 11 Uhr", FRIDAY_10,
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("Leg den Termin beim Zahnarzt auf Freitag um 11.", "Freitag um 11", thursday_18,
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("Verschieb den Zahnarzt von 10 auf 11 Uhr.", "von 10 auf 11 Uhr", FRIDAY_10,
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("Verschieb den Zahnarzt auf Freitag.", "Freitag", FRIDAY_10,
             datetime(2026, 10, 23, 10, 0, tzinfo=TZ)),
            ("Verschieb den Zahnarzt auf den 20. um 11 Uhr.", "auf den 20. um 11 Uhr", FRIDAY_10,
             datetime(2026, 10, 20, 11, 0, tzinfo=TZ)),
        ):
            for given in ("", expression):
                with self.subTest(satz=sentence, zeitausdruck=given):
                    self.insert.reset_mock()
                    new_time: datetime = self._new_time(_state(sentence, given, old_time))
                    self.assertEqual(new_time.astimezone(TZ), expected)

    def test_a_part_or_a_function_word_of_the_title_asks_back(self) -> None:
        """Ueber den Titel nur ganze Inhaltswoerter — bisher liess "nach" das Wort "nachm." zu.

        Mit dem Titel "Fahrt nach Hause" schrieb "auf 3 Uhr nachm." still 03:00,
        gemeint war 15:00.
        """
        for title, sentence, expression in (
            ("Fahrt nach Hause", "Leg die Fahrt nach Hause auf 3 Uhr nachm.", "auf 3 Uhr nachm."),
            ("Fahrt nach Hause", "Leg die Fahrt auf 3 Uhr vorm.", "auf 3 Uhr vorm."),
            ("Treffen vor Ort", "Verschieb das Treffen auf 11 Uhr vorm.", "auf 11 Uhr vorm."),
        ):
            for given in ("", expression):
                with self.subTest(titel=title, satz=sentence, zeitausdruck=given):
                    state: dict = _state(sentence, given, FRIDAY_10)
                    state["parameter"]["termin"]["title"] = title
                    result: dict = self._assert_error(state)
                    self.assertIn(f"Wann soll '{title}' stattfinden?", result["fehler"])

    def test_a_whole_content_word_of_the_title_is_written(self) -> None:
        """Zwilling: ein ganzes Inhaltswort des Titels und sein Kompositum auf "termin"."""
        for title, sentence, expression, expected in (
            ("Zahnarzt", "Verschieb meinen Zahnarzttermin auf 11 Uhr.", "auf 11 Uhr",
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("Zahnarzt Dr. Berger", "Verschieb meinen Zahnarzttermin auf 11 Uhr.", "auf 11 Uhr",
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("Fahrt nach Hause", "Leg die Fahrt auf 15 Uhr.", "auf 15 Uhr",
             datetime(2026, 10, 16, 15, 0, tzinfo=TZ)),
        ):
            for given in ("", expression):
                with self.subTest(titel=title, satz=sentence, zeitausdruck=given):
                    self.insert.reset_mock()
                    state: dict = _state(sentence, given, FRIDAY_10)
                    state["parameter"]["termin"]["title"] = title
                    new_time: datetime = self._new_time(state)
                    self.assertEqual(new_time.astimezone(TZ), expected)

    def test_a_title_word_that_begins_a_parser_word_or_a_free_middle_asks_back(self) -> None:
        """Ein Titelwort, das ein Parser-Wort beginnt, und ein Kompositum mit Mitte: Rueckfrage.

        Bisher machte der Titel "Kaffee nachm." das Wort "nachm" zum Inhaltswort,
        und "auf 3 Uhr nachm." schrieb still 03:00; ein Kompositum liess jede
        Mitte zu ("Zahnarztnachmittagstermin").
        """
        for title, sentence, expression in (
            ("Kaffee nachm.", "Verschieb den Kaffee auf 3 Uhr nachm.", "auf 3 Uhr nachm."),
            ("Kaffee vorm.", "Verschieb den Kaffee auf 9 Uhr vorm.", "auf 9 Uhr vorm."),
            ("Zahnarzt", "Verschieb den Zahnarztnachmittagstermin auf 11 Uhr", "auf 11 Uhr"),
        ):
            for given in ("", expression):
                with self.subTest(titel=title, satz=sentence, zeitausdruck=given):
                    state: dict = _state(sentence, given, FRIDAY_10)
                    state["parameter"]["termin"]["title"] = title
                    result: dict = self._assert_error(state)
                    self.assertIn(f"Wann soll '{title}' stattfinden?", result["fehler"])

    def test_a_compound_with_or_without_joint_s_is_written(self) -> None:
        """Zwilling: Kompositum mit und ohne Fugen-s, ein Inhaltswort neben einem Funktionswort."""
        for title, sentence, expression, expected in (
            ("Zahnarzt", "Verschieb meinen Zahnarzttermin auf 11 Uhr.", "auf 11 Uhr",
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("Zahnarzt", "Verschieb den Zahnarztstermin auf 11 Uhr", "auf 11 Uhr",
             datetime(2026, 10, 16, 11, 0, tzinfo=TZ)),
            ("Kaffee mit Ilva", "Verschieb den Kaffee auf 15 Uhr.", "auf 15 Uhr",
             datetime(2026, 10, 16, 15, 0, tzinfo=TZ)),
        ):
            for given in ("", expression):
                with self.subTest(titel=title, satz=sentence, zeitausdruck=given):
                    self.insert.reset_mock()
                    state: dict = _state(sentence, given, FRIDAY_10)
                    state["parameter"]["termin"]["title"] = title
                    new_time: datetime = self._new_time(state)
                    self.assertEqual(new_time.astimezone(TZ), expected)

    def test_every_parser_word_outside_the_form_asks_back(self) -> None:
        """Jedes Wort aus den Listen des Zeitparsers hinter der Form: None; Zwilling ohne Wort."""
        lists: dict[str, object] = {
            "_WOCHENTAGE": zeitparser._WOCHENTAGE, "_MONATE": zeitparser._MONATE,
            "_RELATIVE": zeitparser._RELATIVE, "_RELATIVE_DAYS": zeitparser._RELATIVE_DAYS,
            "_TAGESZEITEN": zeitparser._TAGESZEITEN,
            "_TAGESZEIT_UHRZEITEN": zeitparser._TAGESZEIT_UHRZEITEN,
            "_ZEITEINHEITEN": zeitparser._ZEITEINHEITEN,
            "_RELATIVE_PRAEFIXE": zeitparser._RELATIVE_PRAEFIXE,
            "_GESCHUETZTE_WOERTER": zeitparser._GESCHUETZTE_WOERTER,
            "_ZAHLWOERTER": zeitparser._ZAHLWOERTER, "_HOUR_WORDS": zeitparser._HOUR_WORDS,
            "_ORDINAL_DAYS": zeitparser._ORDINAL_DAYS,
            "_MONTHS_AFTER_UM": zeitparser._MONTHS_AFTER_UM.split("|"),
        }
        eleven = positive_form.RawTimeForm(clock=time(11, 0))
        self.assertEqual(
            positive_form.raw_time_form("Verschieb den Zahnarzt auf 11 Uhr", "Zahnarzt"), eleven
        )
        cases: list[tuple[str, str, str]] = [
            (name, word, form)
            for name, words in lists.items()
            for word in words
            for form in (word, zeitparser._ascii_umschrift(word))
        ]
        for name, word, form in cases:
            text: str = f"Verschieb den Zahnarzt auf 11 Uhr {form}"
            with self.subTest(liste=name, wort=form):
                if form.lower() in positive_form._RAW_ADMITTED_WORDS:
                    # Nur der Artikel "ein": zugelassen, und keine Zeit.
                    self.assertIn(word, positive_form._RAW_NO_TIME_WORDS)
                    self.assertEqual(positive_form.raw_time_form(text, "Zahnarzt"), eleven)
                else:
                    self.assertIsNone(positive_form.raw_time_form(text, "Zahnarzt"))
                    self.assertTrue(word in positive_form._RAW_NO_TIME_WORDS
                                    or form.lower() in positive_form._RAW_TIME_WORDS)

    def test_a_prefixed_weekday_is_a_day_a_week_is_not(self) -> None:
        """Ein Wochentag mit Praefix ist ein <Tag> der Form, "naechste Woche" nicht."""
        for text, expected in (
            ("auf nächsten Freitag", positive_form.RawTimeForm()),
            ("auf naechsten Freitag um 11", positive_form.RawTimeForm(clock=time(11, 0))),
            ("auf nächste Woche", None),
            ("auf Freitag in drei Tagen", None),
            ("auf 11 Uhr, Geburtstag", None),
        ):
            with self.subTest(text=text):
                self.assertEqual(positive_form.raw_time_form(text, "Zahnarzt"), expected)

    def test_raw_new_hour_rejects_what_is_no_match_of_the_form(self) -> None:
        with self.assertRaises(ValueError):
            positive_form._raw_new_hour(None)
        with self.assertRaises(ValueError):
            positive_form._raw_new_hour(zeitparser._BARE_NUMBER.search("auf 11"))

    def test_dotted_clock_times(self) -> None:
        """Nur eine Uhrzeit mit Punkt, die kein Datum sein kann, bekommt den Doppelpunkt."""
        for text, expected in (
            ("auf 11.30.", "auf 11:30."),
            ("auf 9.45 bitte", "auf 9:45 bitte"),
            ("auf den 20.10.", "auf den 20.10."),
            ("auf 11.10", "auf 11.10"),
            ("am 11.30.2026", "am 11.30.2026"),
            ("um 2.50 Euro", "um 2.50 Euro"),
            ("auf 11.30h", "auf 11.30h"),
        ):
            with self.subTest(text=text):
                self.assertEqual(zeitparser.dotted_clock_times(text), expected)
        with self.assertRaises(TypeError):
            zeitparser.dotted_clock_times(None)

    def test_raw_form_agrees(self) -> None:
        """Jeder Zweig: Form und Lesung einig, uneins, ausserhalb der Form, ohne Uhrzeit."""
        eleven: datetime = datetime(2026, 10, 16, 11, 0, tzinfo=TZ)
        friday_23_10: datetime = datetime(2026, 10, 23, 10, 0, tzinfo=TZ)
        for name, texts, reading_clock, new_time, expected in (
            ("einig", ("", "auf 11 Uhr"), time(11, 0), eleven, True),
            ("Lesung ohne Uhrzeit", ("", "auf 11 Uhr"), None, eleven, False),
            ("anders geschrieben", ("", "auf 11 Uhr"), time(11, 0),
             eleven.replace(hour=12), False),
            ("zwei Uhrzeiten", ("11 Uhr", "auf 12 Uhr"), time(11, 0), eleven, False),
            ("ausserhalb der Form", ("", "auf 11h"), time(11, 0), eleven, False),
            ("Titel zugelassen", ("", "Verschieb den Zahnarzt auf 11 Uhr."), time(11, 0),
             eleven, True),
            ("nur Tag", ("Freitag", "auf Freitag"), None, friday_23_10, True),
            ("nur Tag, andere Uhrzeit", ("Freitag", "auf Freitag"), None,
             friday_23_10.replace(hour=11), False),
            ("nur Tag, Lesung mit Uhrzeit", ("Freitag", "auf Freitag"), time(10, 0),
             friday_23_10, False),
        ):
            with self.subTest(fall=name):
                self.assertIs(
                    timeline_crud._raw_form_agrees(
                        texts, "Zahnarzt", reading_clock, new_time, FRIDAY_10,
                    ),
                    expected,
                )
        self.assertIs(
            timeline_crud._raw_form_agrees(
                ("", "Verschieb den Zahnarzt auf 11 Uhr."), "", time(11, 0), eleven, FRIDAY_10,
            ),
            False,
        )
        with self.assertRaises(ValueError):
            timeline_crud._raw_form_agrees(("auf 11 Uhr",), "Zahnarzt", time(11, 0),
                                           eleven.replace(tzinfo=None), FRIDAY_10)
        with self.assertRaises(TypeError):
            timeline_crud._raw_form_agrees((None,), "Zahnarzt", time(11, 0), eleven, FRIDAY_10)
        with self.assertRaises(TypeError):
            timeline_crud._raw_form_agrees(("auf 11 Uhr",), None, time(11, 0), eleven, FRIDAY_10)


class ErrorReachesTheAnswerTest(unittest.TestCase):
    """Ein gescheiterter Auftrag steht im Prompt der Antwort desselben Turns.

    Der Weg: Der Planner schreibt aus `agent_results` den `[AUFGABE]`-Block,
    der Responder haengt ihn an. Geprueft wird die Verdrahtung, nicht der
    Wortlaut des Blocks — den bezeugt `test_task_block_fehler.py`.
    """

    def test_the_error_and_its_question_reach_the_responder_prompt(self) -> None:
        state: dict = {
            "user_prompt":      SENTENCE_CLOCK_ONLY,
            "event_source":     "user",
            "event_payload":    {},
            "external":         None,
            "internal":         None,
            "task_block":       "",
            "emotions_verlauf": [],
            "user_intentionen": [],
            "gv_hypothese":     "",
            "memory_context":   "",
            "web_context":      "",
            "agent_results":    [AgentResult(agent_name="timeline", ergebnis=None,
                                             status="fehler", fehler=AGENT_ERROR)],
        }

        planner_mod._write_task_block(state)
        prompt: str = _build_system_prompt(state)

        self.assertIn(AGENT_ERROR, prompt)
        self.assertRegex(prompt, r"nichts\s+(eingetragen|geaendert)")
        self.assertTrue(state["task_context_cut"])

    def test_without_a_result_there_is_no_such_sentence(self) -> None:
        """Zwilling: Der Satz kommt aus dem Fehler, nicht aus dem Prompt selbst."""
        state: dict = {
            "user_prompt":      SENTENCE_CLOCK_ONLY,
            "event_source":     "user",
            "event_payload":    {},
            "external":         None,
            "internal":         None,
            "task_block":       "",
            "emotions_verlauf": [],
            "user_intentionen": [],
            "gv_hypothese":     "",
            "memory_context":   "",
            "web_context":      "",
            "agent_results":    [],
        }

        planner_mod._write_task_block(state)
        prompt: str = _build_system_prompt(state)

        self.assertNotIn(AGENT_ERROR, prompt)
        self.assertNotRegex(prompt, r"nichts\s+(eingetragen|geaendert)")


if __name__ == "__main__":
    unittest.main()
