"""Zeugen: Eine Stunde ohne "Uhr" ist eine Uhrzeit — nie der Tag des Monats.

Ziel: Nach "um", mit Tagesangabe und ohne, neben einer Tageszeit davor oder
dahinter, liest der Parser eine Stunde 0..23 als Uhrzeit — so, wie er sie mit
"Uhr" liest. Mengen und Monate hinter der Zahl bleiben, was sie waren.

Der Fall im Betrieb, 14.09.2026: Ein Terminauftrag mit Tageswort, "um" und
nackter Stunde kam woertlich beim Parser an. Die Normalisierung liess *„um H"*
stehen, und der Rueckfall auf den Originaltext lieferte den Folgetag **zur
aktuellen Uhrzeit**. Ohne Tagesangabe wurde die Zahl zum Monatstag, auch neben
einem Wochentag. Die Stunden unten sind gewaehlt, nicht die des Auftrags.

Bezugszeit ist die des Korpus: Freitag, 31.07.2026, 14:00 Europe/Berlin. Sie
wird als `referenz` UND als `sprechzeitpunkt` uebergeben — das Tageswort haengt
am zweiten, und ohne ihn liefe jeder Fall gegen die echte Uhr.

Zeugen dieser Datei:
  * Die erwarteten Zeitpunkte sind von Hand gerechnet und stehen als Literale.
  * **Jeder Verbotszeuge hat einen Zwilling**, der dieselbe Regel feuern sieht
    (*„um 10 Minuten"* neben *„um 10"*, *„um 24"* neben *„um 23"*) — sonst waere
    er auch bei einem Parser gruen, der nie eine Stunde liest.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
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


class TestHourAfterUm(unittest.TestCase):
    """Die Stunde nach "um" ist eine Uhrzeit."""

    def test_day_word_and_bare_hour_is_that_hour_not_the_current_time(self) -> None:
        """Die Form des Betriebsfalls: bis zum 15.09.2026 morgen um 14:00, der Sprechzeit."""
        self.assertEqual("2026-08-01 09:00", _local("morgen um 9"))
        self.assertTrue(_parse("morgen um 9").uhrzeit_erkannt)

    def test_weekday_hour_is_not_the_day_of_month(self) -> None:
        """Der naechste Donnerstag nach Freitag, dem 31.07., ist der 06.08. — nicht der 14.07."""
        self.assertEqual("2026-08-06 14:00", _local("Donnerstag um 14"))

    def test_hour_still_to_come_stays_today(self) -> None:
        """22:00 liegt um 14:00 noch vor uns."""
        self.assertEqual("2026-07-31 22:00", _local("um 22"))

    def test_hour_already_past_is_tomorrow(self) -> None:
        """10:00 ist vorbei — das naechste Mal ist morgen. Bis zum 15.09.2026 der 10.07."""
        self.assertEqual("2026-08-01 10:00", _local("um 10"))

    def test_hour_zero_is_midnight(self) -> None:
        """Die untere Kante der Stundenspanne."""
        self.assertEqual("2026-08-01 00:00", _local("um 0"))

    def test_hour_23_is_read(self) -> None:
        """Die obere Kante — Zwilling von `test_hour_24_is_not_read`."""
        self.assertEqual("2026-07-31 23:00", _local("um 23"))

    def test_full_stop_after_the_hour_ends_the_sentence(self) -> None:
        """*„Wir sehen uns um 10."* — der Punkt ist ein Satzende, keine Ordinalzahl."""
        self.assertEqual("2026-08-01 10:00", _local("um 10."))

    def test_approximate_hour(self) -> None:
        """*„um 10 rum"* bleibt eine Uhrzeit."""
        self.assertEqual("2026-08-01 10:00", _local("um 10 rum"))


class TestDaypartShiftsTheHour(unittest.TestCase):
    """Eine Tageszeit verschiebt die Stunde ohne "Uhr" wie die mit "Uhr"."""

    def test_evening_after_day_word(self) -> None:
        """Die Einzahl *„abend"* nach dem Tageswort; bis zum 15.09.2026 nicht aufgeloest."""
        self.assertEqual("2026-07-31 20:00", _local("heute abend um 8"))

    def test_evening_after_day_word_with_uhr(self) -> None:
        """Der Zwilling mit "Uhr" — bis zum 15.09.2026 08:00 morgens."""
        self.assertEqual("2026-07-31 20:00", _local("heute abend um 8 Uhr"))

    def test_daypart_before_um(self) -> None:
        """Korpus REG-024, bis zum 15.09.2026 als Luecke gefuehrt: der 03.07."""
        self.assertEqual("2026-07-31 15:00", _local("nachmittags um 3"))

    def test_daypart_before_um_with_uhr(self) -> None:
        """Korpus REG-023, bis zum 15.09.2026 als Luecke gefuehrt: 03:00 am Folgetag."""
        self.assertEqual("2026-07-31 15:00", _local("nachmittags um 3 Uhr"))

    def test_day_word_daypart_and_hour(self) -> None:
        """*„morgen nachmittag um 3"* — Tag, Tageszeit, Stunde."""
        self.assertEqual("2026-08-01 15:00", _local("morgen nachmittag um 3"))

    def test_hour_before_daypart(self) -> None:
        """Korpus REG-011: bis zum 15.09.2026 der 03. des Monats um 15:00."""
        self.assertEqual("2026-07-31 15:00", _local("3 nachmittags"))

    def test_twelve_at_night_is_midnight_as_with_uhr(self) -> None:
        """*„nachts um 12"* liest wie *„12 Uhr nachts"* — beide 00:00, nicht Mittag."""
        self.assertEqual("2026-08-01 00:00", _local("nachts um 12"))
        self.assertEqual("2026-08-01 00:00", _local("12 Uhr nachts"))

    def test_morning_does_not_shift(self) -> None:
        """Eine Tageszeit vor Mittag verschiebt nichts; 07:00 ist vorbei, also morgen."""
        self.assertEqual("2026-08-01 07:00", _local("morgens um 7"))


class TestNotAnHour(unittest.TestCase):
    """Verbotszeugen: Was keine Stunde ist, wird nicht zu einer."""

    def test_minutes_after_um_stay_a_duration(self) -> None:
        """Unveraendert gegen die Fassung vor dem 15.09.2026. Zwilling: "um 10"."""
        vector = _parse("um 10 Minuten")

        self.assertEqual("2026-07-31 14:10", _local("um 10 Minuten"))
        self.assertFalse(vector.uhrzeit_erkannt)

    def test_percent_after_um_is_no_time(self) -> None:
        """*„um 10 Prozent"* ist eine Menge — keine Uhrzeit, kein Datum."""
        vector = _parse("um 10 Prozent")

        self.assertIsNone(vector.datum)
        self.assertFalse(vector.uhrzeit_erkannt)

    def test_number_before_month_is_a_day(self) -> None:
        """*„um 15. Mai"* ist der 15. Mai; der naechste liegt 2027. Zwilling: "um 22"."""
        vector = _parse("um 15. Mai")

        self.assertEqual("2027-05-15 00:00", _local("um 15. Mai"))
        self.assertFalse(vector.uhrzeit_erkannt)

    def test_minutes_after_uhr_are_not_an_hour_before_daypart(self) -> None:
        """In *„3 Uhr 15 nachmittags"* ist die 15 der Minutenteil. Zwilling: "3 nachmittags"."""
        self.assertEqual("2026-07-31 15:15", _local("3 Uhr 15 nachmittags"))

    def test_hour_24_is_not_read(self) -> None:
        """Keine Stunde der Spanne 0..23. Zwilling: `test_hour_23_is_read`."""
        self.assertFalse(_parse("um 24").uhrzeit_erkannt)


class TestShiftRule(unittest.TestCase):
    """Die Verschieberegel selbst, an ihrer Stelle im Modul."""

    def test_afternoon_shifts_a_morning_hour(self) -> None:
        """3 nachmittags ist 15."""
        self.assertEqual(15, zeitparser._shift_hour_by_daypart(3, "nachmittags"))

    def test_afternoon_leaves_an_afternoon_hour(self) -> None:
        """15 nachmittags bleibt 15 — nicht 27."""
        self.assertEqual(15, zeitparser._shift_hour_by_daypart(15, "nachmittags"))

    def test_without_daypart_unchanged(self) -> None:
        """Ohne Tageszeit entscheidet die Regel keine Tageshaelfte."""
        self.assertEqual(3, zeitparser._shift_hour_by_daypart(3, ""))

    def test_morning_unchanged(self) -> None:
        """Eine Tageszeit vor Mittag verschiebt nicht."""
        self.assertEqual(7, zeitparser._shift_hour_by_daypart(7, "morgens"))

    def test_twelve_at_night_is_zero_twelve_at_noon_is_twelve(self) -> None:
        """Dieselbe Zahl, zwei Tageszeiten, zwei Ergebnisse."""
        self.assertEqual(0, zeitparser._shift_hour_by_daypart(12, "nachts"))
        self.assertEqual(12, zeitparser._shift_hour_by_daypart(12, "mittags"))

    def test_hour_outside_range_is_a_programming_error(self) -> None:
        """Die Aufrufer pruefen die Spanne vorher — hier anzukommen ist ein Fehler."""
        with self.assertRaises(zeitparser._HourReadingError):
            zeitparser._shift_hour_by_daypart(24, "")

    def test_unknown_daypart_is_a_programming_error(self) -> None:
        """Ein Wort ausserhalb der Tabelle wird nicht still als "keine Tageszeit" gelesen."""
        with self.assertRaises(zeitparser._HourReadingError):
            zeitparser._shift_hour_by_daypart(3, "gestern")


class TestCaseFolding(unittest.TestCase):
    """Die Tageszeit wird mit derselben Faltung aufgeloest, mit der das Muster sie traf.

    `re.IGNORECASE` laesst `ı` (U+0131) und `İ` (U+0130) ein `i` treffen, `ſ`
    (U+017F) ein `s`; `str.lower()` fuehrt von dort nicht zum Tabellenschluessel
    zurueck. Bis zum 15.09.2026 warf der Leser dann `_HourReadingError` — die
    Ausnahme, die nur einen Programmfehler anzeigen soll. Gefunden von der
    zweiten Kontrolle ueber erzeugte Eingaben.
    """

    def test_case_folded_dotless_i_is_read(self) -> None:
        """*„nachmıttags"* trifft das Muster — also gilt es als *„nachmittags"*."""
        self.assertEqual("2026-08-01 15:00", _local("morgen um 3 nachmıttags"))

    def test_case_folded_long_s_is_read(self) -> None:
        """Das lange s am Wortende: *„abendſ"* ist *„abends"*."""
        self.assertEqual("2026-08-01 15:00", _local("morgen um 3 abendſ"))

    def test_daypart_key_follows_the_regex_folding(self) -> None:
        """Das grosse I mit Punkt: `lower()` ergibt zwei Zeichen, der Schluessel bleibt einer."""
        self.assertEqual("nachmittags", zeitparser._daypart_key("nachmİttags"))

    def test_daypart_key_rejects_a_word_outside_the_table(self) -> None:
        """Was keinen Schluessel trifft, ist hier ein Programmfehler, kein stilles Leer."""
        with self.assertRaises(zeitparser._HourReadingError):
            zeitparser._daypart_key("gestern")


class TestTablesAgree(unittest.TestCase):
    """Die gemerkte Tageszeit muss verschiebbar sein."""

    def test_every_fallback_daypart_has_a_shift(self) -> None:
        """Jedes Wort der Rueckfall-Tabelle steht, kleingeschrieben, in der Verschiebetabelle.

        Die Extraktion merkt sich das Wort aus `_TAGESZEIT_UHRZEITEN`, die
        Verschiebung liest `_TAGESZEITEN`. Bis zum 15.09.2026 stand *„Abend"*
        nur in der ersten — *„heute abend um 8 Uhr"* wurde 08:00.
        """
        missing = [
            word for word in zeitparser._TAGESZEIT_UHRZEITEN
            if word.lower() not in zeitparser._TAGESZEITEN
        ]

        self.assertEqual([], missing)


class TestCountCheckBites(unittest.TestCase):
    """Die Nachzaehlung in `_replace_hours` schlaegt an, wenn ein Treffer nicht ankommt."""

    def test_hit_inside_an_existing_clock_time_raises(self) -> None:
        """Ein Muster, das die 5 aus "5:30" greift, schreibt "5:00:30" — eine Uhrzeit."""
        with self.assertRaises(zeitparser._HourReadingError):
            zeitparser._replace_hours("5:30", re.compile(r"(\d{1,2})(?=:)"), "")

    def test_ordinary_hit_passes(self) -> None:
        """Zwilling: dasselbe Werkzeug mit dem echten Muster."""
        self.assertEqual("5:00", zeitparser._replace_hours("um 5", zeitparser._HOUR_AFTER_UM, ""))


if __name__ == "__main__":
    unittest.main()
