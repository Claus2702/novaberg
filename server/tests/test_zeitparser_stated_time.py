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


if __name__ == "__main__":
    unittest.main()
