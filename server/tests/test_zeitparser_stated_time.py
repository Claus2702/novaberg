"""Zeugen: Die genannte Uhrzeit wird gelesen, wie sie dasteht — oder gar nicht.

Ziel, Teil A: Eine Uhrzeit mit Punkt als Trenner wird gelesen wie mit
Doppelpunkt — vor "Uhr" immer, nach "um", wenn sie eine Uhrzeit sein kann.

Der Fall im Betrieb, 14.09.2026: Eine Zeitangabe mit Punkt als Trenner kam
woertlich beim Parser an. Block 2 las in *„H.00 Uhr"* die `00 Uhr` als Stunde,
und der Rueckfall auf den Originaltext lieferte den Tag zur aktuellen Uhrzeit.
Mit anderen Minuten stuerzte der Parser ab: In *„9.30 Uhr"* wurde `30 Uhr` die
Stunde 30. Die Stunden unten sind gewaehlt, nicht die des Auftrags.

Bezugszeit ist die des Korpus: Freitag, 31.07.2026, 14:00 Europe/Berlin, als
`referenz` UND `sprechzeitpunkt`.

Zeugen dieser Datei:
  * Die erwarteten Zeitpunkte sind von Hand gerechnet und stehen als Literale.
  * **Jeder Verbotszeuge hat einen Zwilling**, der dieselbe Regel feuern sieht
    (*„um 31.12"* neben *„um 12.10"*, *„um 2.50 Euro"* neben *„um 9.30"*).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from config import TIMEZONE
from utils import zeitparser
from utils.zeitparser import ZeitVektor, zeit_parsen_vektor

_ZONE = ZoneInfo(TIMEZONE)
_REF = datetime(2026, 7, 31, 14, 0, tzinfo=_ZONE)


def _parse(text: str) -> ZeitVektor:
    """Parst gegen die feste Bezugszeit, Tageswort und Dauer am selben Anker."""
    return zeit_parsen_vektor(text, referenz=_REF, sprechzeitpunkt=_REF)


def _local(text: str) -> Optional[str]:
    """Das Ergebnis als lokale Wanduhr, oder None, wenn nichts aufgeloest wurde."""
    result = _parse(text).datum
    return result.astimezone(_ZONE).strftime("%Y-%m-%d %H:%M") if result else None


class TestDottedClockTime(unittest.TestCase):
    """Der Punkt als Trenner liest wie der Doppelpunkt."""

    def test_dotted_time_before_uhr_reads_like_colon(self) -> None:
        """*„9.30 Uhr"* stuerzte bis zum 15.09.2026 ab — Stunde 30."""
        self.assertEqual("2026-08-01 09:30", _local("9.30 Uhr"))
        self.assertEqual(_local("9:30 Uhr"), _local("9.30 Uhr"))

    def test_day_word_and_dotted_full_hour(self) -> None:
        """Die Form des Betriebsfalls: bis zum 15.09.2026 der Tag zur Sprechzeit, 14:00."""
        self.assertEqual("2026-08-02 09:00", _local("übermorgen um 9.00 Uhr"))

    def test_weekday_and_dotted_time_with_uhr(self) -> None:
        """Bis zum 15.09.2026 der 14. des Monats um 15:00."""
        self.assertEqual("2026-08-06 14:15", _local("Donnerstag um 14.15 Uhr"))

    def test_dotted_time_after_um_without_uhr(self) -> None:
        """*„heute um 20.15"* — bis zum 15.09.2026 heute um 14:00."""
        self.assertEqual("2026-07-31 20:15", _local("heute um 20.15"))

    def test_dotted_time_after_um_that_can_be_a_time(self) -> None:
        """12.10 kann eine Uhrzeit sein — Zwilling des Zeugen fuer *„um 31.12"*."""
        self.assertEqual("2026-08-01 12:10", _local("um 12.10"))

    def test_leading_zero_hour(self) -> None:
        """*„09.05 Uhr"* — bis zum 15.09.2026 der 9. des Monats um 05:00."""
        self.assertEqual("2026-08-01 09:05", _local("um 09.05 Uhr"))

    def test_date_with_dotted_time(self) -> None:
        """Ein ausgeschriebenes Datum mit Punkt-Uhrzeit — der Punkt des Datums bleibt."""
        self.assertEqual("2026-09-15 10:00", _local("15.09.2026 10.00 Uhr"))

    def test_date_after_um_stays_a_date(self) -> None:
        """*„um 1.10."* ist der 1. Oktober: Der Punkt dahinter macht es zum Datum."""
        self.assertEqual("2026-10-01 00:00", _local("um 1.10."))
        self.assertFalse(_parse("um 1.10.").uhrzeit_erkannt)

    def test_impossible_hour_after_um_stays_a_date(self) -> None:
        """*„um 31.12"* kann keine Uhrzeit sein — es bleibt der 31. Dezember."""
        self.assertEqual("2026-12-31 00:00", _local("um 31.12"))
        self.assertFalse(_parse("um 31.12").uhrzeit_erkannt)

    def test_amount_after_um_is_no_time(self) -> None:
        """*„um 2.50 Euro"* ist ein Betrag. Zwilling: `test_dotted_time_after_um_without_uhr`."""
        vector = _parse("um 2.50 Euro")

        self.assertIsNone(vector.datum)
        self.assertFalse(vector.uhrzeit_erkannt)

    def test_decimal_duration_is_untouched(self) -> None:
        """*„um 1.5 Stunden"* hat eine Nachkommastelle, keine Minuten — unveraendert."""
        self.assertEqual("2026-07-31 15:30", _local("um 1.5 Stunden"))
        self.assertFalse(_parse("um 1.5 Stunden").uhrzeit_erkannt)

    def test_reader_does_not_count_um_with_uhr_twice(self) -> None:
        """*„um 9.30 Uhr"* passt auf beide Muster; gelesen und gezaehlt wird es einmal.

        Die erste Fassung zaehlte die Stelle unter beiden Mustern, und die
        Nachzaehlung warf — gefunden in der Messung vor dem ersten Zeugen.
        """
        self.assertEqual("um 9:30 Uhr", zeitparser._read_dotted_clock_time("um 9.30 Uhr"))


class TestImpossibleValues(unittest.TestCase):
    """Teil B: Was es nicht gibt, ergibt kein Datum — und keinen Absturz.

    Bis zum 15.09.2026 bauten die Pfade ihr `datetime` ungeprueft, und die
    `ValueError` erreichte den Termindienst, der sie nicht faengt. Jeder Zeuge
    hat einen gueltigen Zwilling auf demselben Pfad.
    """

    def test_invalid_day_with_bare_hour_gives_no_date(self) -> None:
        """Der 31. September, Pfad 1b. Zwilling: der 30."""
        self.assertIsNone(_parse("am 31.09. um 10").datum)
        self.assertEqual("2026-09-30 10:00", _local("am 30.09. um 10"))

    def test_invalid_day_alone_gives_no_date(self) -> None:
        """Ohne Uhrzeit derselbe Pfad, dieselbe Ausnahme bis zum 15.09.2026."""
        self.assertIsNone(_parse("31.09.").datum)

    def test_february_29_only_in_a_leap_year(self) -> None:
        """2027 ist kein Schaltjahr, 2028 schon."""
        self.assertIsNone(_parse("29.02.2027").datum)
        self.assertEqual("2028-02-29 10:00", _local("29.02.2028 10:00"))

    def test_hour_24_gives_no_date(self) -> None:
        """*„24 Uhr"* als Mitternacht kann der Parser nicht; bis zum 15.09.2026 Absturz."""
        self.assertIsNone(_parse("morgen um 24 Uhr").datum)

    def test_impossible_minute_gives_no_date(self) -> None:
        """Pfad 1 mit Minute 75. Zwilling: 23:59, die letzte gueltige Minute."""
        self.assertIsNone(_parse("morgen 14:75").datum)
        self.assertEqual("2026-08-01 23:59", _local("morgen um 23:59"))

    def test_impossible_value_is_logged_with_its_wording(self) -> None:
        """Kein stilles Leer: Die Warnzeile nennt den Wert, den es nicht gibt."""
        with self.assertLogs("ki_server.zeitparser", level="WARNING") as log:
            _parse("am 31.09. um 10")

        self.assertTrue(any("31.09.2026" in zeile for zeile in log.output), log.output)

    def test_impossible_values_names_each_kind(self) -> None:
        """Datum in beiden Schreibungen und Uhrzeit — und nichts bei gueltigen Werten."""
        self.assertEqual(["31.09.2026"], zeitparser._impossible_values("31.09.2026 10:00"))
        self.assertEqual(["2026-02-30", "24:00"], zeitparser._impossible_values("2026-02-30 24:00"))
        self.assertEqual([], zeitparser._impossible_values("29.02.2028 23:59"))

    def test_glued_digits_are_checked_as_path_2_reads_them(self) -> None:
        """Pfad 2 sucht eine Uhrzeit ohne Grenzen; die Pruefung muss dasselbe lesen.

        Die erste Fassung las mit Grenzen und uebersah `38:99` in *„9838:99"* —
        gefunden ueber 12 000 erzeugte Eingaben, von denen 17 weiter warfen.
        """
        self.assertIsNone(_parse("Donnerstag 9838:99").datum)
        self.assertEqual(["38:99"], zeitparser._impossible_values("Donnerstag 9838:99"))


class TestStatedTimeMustBeInTheResult(unittest.TestCase):
    """Teil C: Ein Ergebnis traegt eine erkannte Uhrzeit — oder es gibt keins.

    Scheitern die Pfade am normalisierten Text, bekommt dateparser den
    Originaltext, und der verwirft eine Uhrzeit, die er nicht lesen kann, still.
    Bis zum 15.09.2026 kam dann der Tag zur Sprechzeit zurueck, mit
    `uhrzeit_erkannt` — ein Termin zur falschen Zeit mit Genauigkeit Minute.
    """

    def test_fallback_that_drops_the_time_gives_no_date(self) -> None:
        """Ein doppeltes Tageswort laesst die Pfade scheitern; der Rueckfall lieferte 14:00."""
        self.assertIsNone(_parse("morgen um 3 morgen").datum)
        self.assertEqual("2026-08-01 03:00", _local("morgen um 3"))

    def test_dropped_time_is_logged(self) -> None:
        """Die Warnzeile nennt die Uhrzeit, die im Ergebnis fehlte."""
        with self.assertLogs("ki_server.zeitparser", level="WARNING") as log:
            _parse("morgen um 3 morgen")

        self.assertTrue(any("3:00" in zeile for zeile in log.output), log.output)

    def test_stated_time_missing_compares_the_local_wall_clock(self) -> None:
        """Leer, wenn eine genannte Uhrzeit im Ergebnis steht oder keine genannt ist."""
        result = datetime(2026, 8, 1, 14, 0, tzinfo=_ZONE)

        self.assertEqual("10:00", zeitparser._stated_time_missing("2026-08-01 10:00", result))
        self.assertEqual("", zeitparser._stated_time_missing("10:00 bis 14:00", result))
        self.assertEqual("", zeitparser._stated_time_missing("2026-08-01", result))



class TestIsoDateGoesToDateparserAsDmy(unittest.TestCase):
    """Teil D: Ein Datum, das die Normalisierung schreibt, liest dateparser richtig herum.

    Block 0b schreibt ein Tageswort als ISO-Datum. Bekommt dateparser es in
    Pfad 2 oder 3, liest er es unter `DATE_ORDER: DMY` als Jahr-Tag-Monat:
    `2026-08-01` wurde der 8. Januar, `2026-07-31` gar nichts. Getroffen hat es
    jeden Ausdruck mit der Uhrzeit vor dem Tageswort — gefunden von der zweiten
    Kontrolle ueber erzeugte Eingaben.
    """

    def test_hour_before_day_word_keeps_the_day(self) -> None:
        """*„9 Uhr morgen"* — bis zum 15.09.2026 der 08.01.2026 um 09:00."""
        self.assertEqual("2026-08-01 09:00", _local("9 Uhr morgen"))

    def test_dotted_time_before_day_word_reads_like_colon(self) -> None:
        """*„9.15 Uhr heute"* liest wie *„9:15 Uhr heute"* — vorher nur der Zwilling."""
        self.assertEqual("2026-07-31 09:15", _local("9.15 Uhr heute"))
        self.assertEqual(_local("9:15 Uhr heute"), _local("9.15 Uhr heute"))

    def test_iso_dates_as_dmy_rewrites_each_iso_date(self) -> None:
        """Jedes ISO-Datum wird Tag.Monat.Jahr; der Rest des Textes bleibt."""
        self.assertEqual(
            "01.08.2026 Freitag bis 02.08.2026",
            zeitparser._iso_dates_as_dmy("2026-08-01 Freitag bis 2026-08-02"),
        )

    def test_contradicting_weekday_gives_no_date(self) -> None:
        """Am Freitag gesagt ist morgen Samstag — mit *„Montag"* daneben gibt es kein Datum.

        Im Betrieb kam am 14.09.2026, einem Montag, ein Termin mit Tageswort und
        einem anderen Wochentag beim Parser an. Solange das ISO-Datum falsch
        herum gelesen wurde, ergab er zufaellig nichts; richtig gelesen haette
        er den Dienstag gewaehlt. Der Ausdruck unten ist gewaehlt.
        """
        self.assertIsNone(_parse("morgen, Montag um 8 Uhr").datum)

    def test_contradiction_is_logged(self) -> None:
        """Die Warnzeile nennt den Tag, den das Tageswort ergibt."""
        with self.assertLogs("ki_server.zeitparser", level="WARNING") as log:
            _parse("morgen, Montag um 8 Uhr")

        self.assertTrue(any("Samstag" in zeile for zeile in log.output), log.output)

    def test_weekday_contradiction_names_the_day(self) -> None:
        """Leer, wenn der Wochentag zum Datum passt oder keiner genannt ist."""
        self.assertIn("Samstag", zeitparser._weekday_contradiction("2026-08-01 Montag 8:00"))
        self.assertEqual("", zeitparser._weekday_contradiction("2026-08-01 Samstag 8:00"))
        self.assertEqual("", zeitparser._weekday_contradiction("2026-08-01 9:00"))

    def test_consistent_day_word_and_weekday_keeps_the_date(self) -> None:
        """Zwilling: Stimmen Tageswort und Wochentag ueberein, bleibt das Datum."""
        self.assertEqual("2026-08-01 08:00", _local("morgen, Samstag um 8 Uhr"))
        self.assertEqual("2026-07-31 00:00", _local("heute Freitag"))

    def test_iso_date_glued_to_a_number_stays_untouched(self) -> None:
        """Hinter einem Punkt ist `2026-07-31` Teil eines Wortsalats, kein Datum.

        Die erste Fassung schrieb es um, und die Nachzaehlung warf — gefunden
        ueber 12 000 erzeugte Eingaben, von denen 19 so endeten.
        """
        self.assertEqual("43.2026-07-31", zeitparser._iso_dates_as_dmy("43.2026-07-31"))
        _parse("um 43.heute")

if __name__ == "__main__":
    unittest.main()
