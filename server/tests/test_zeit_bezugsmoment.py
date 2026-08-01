"""Tests: ein Tageswort loest gegen den uebergebenen Sprechzeitpunkt auf.

`morgen` und `uebermorgen` rechneten bis zum 01.08.2026 gegen die **echte
Uhr**, auch wenn ein Bezugsmoment uebergeben war. Sichtbar wurde es beim
Ueberschreiten der lokalen Mitternacht: Bis dahin fiel der echte Kalendertag
mit dem Bezugsmoment der Tests zusammen, und drei gruene Tests prueften eine
Uebereinstimmung, die nur am Tag ihrer Entstehung galt.

**Deshalb liegt der Bezug hier bewusst in der Vergangenheit.** Ein Test, dessen
Bezugsmoment "heute" ist, kann diesen Defekt nicht sehen — er ist derselbe
Test, der ihn zwei Wochen lang uebersehen hat.

Zeugen dieser Datei:
  * Die erwarteten Daten sind von Hand gerechnet: Bezug 2026-07-10 22:30 UTC
    ist 2026-07-11 00:30 Ortszeit, also ist "uebermorgen" der 13.07.
  * Die Gleichheit von `uebermorgen` und `in zwei Tagen` steht als Zusicherung
    im Parser selbst (Kommentar an der Referenz-Drehung).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import date, datetime, timezone

from utils.zeitparser import zeit_parsen_vektor

# 22:30 UTC ist 00:30 Ortszeit des FOLGETAGS. Das Fenster zwischen lokaler und
# UTC-Mitternacht ist die Stelle, an der die beiden Uhren frueher auseinander-
# liefen — die Faelle liegen bewusst darin.
BEZUG_JULI_10: datetime = datetime(2026, 7, 10, 22, 30, tzinfo=timezone.utc)
BEZUG_JULI_20: datetime = datetime(2026, 7, 20, 22, 30, tzinfo=timezone.utc)
BEZUG_JULI_30: datetime = datetime(2026, 7, 30, 22, 30, tzinfo=timezone.utc)


class DasTageswortFolgtDemBezugsmomentTest(unittest.TestCase):
    """Derselbe Ausdruck, verschiedene Bezugsmomente, verschiedene Daten."""

    def _datum(self, ausdruck: str, bezug: datetime) -> date:
        ergebnis = zeit_parsen_vektor(ausdruck, bezug, sprechzeitpunkt=bezug)
        self.assertIsNotNone(ergebnis, f"{ausdruck!r} nicht aufgeloest")
        self.assertIsNotNone(ergebnis.datum, f"{ausdruck!r} ohne Datum")
        return ergebnis.datum.date()

    def test_uebermorgen_wandert_mit_dem_bezug(self) -> None:
        """Von Hand: Ortstag 11.07. + 2 = 13.07., 21.07. + 2 = 23.07."""
        self.assertEqual(date(2026, 7, 13), self._datum("übermorgen", BEZUG_JULI_10))
        self.assertEqual(date(2026, 7, 23), self._datum("übermorgen", BEZUG_JULI_20))

    def test_drei_bezuege_ergeben_drei_daten(self) -> None:
        """Die Gegenprobe gegen die echte Uhr: Sie liefert dreimal dasselbe."""
        daten: set[date] = {
            self._datum("übermorgen", bezug)
            for bezug in (BEZUG_JULI_10, BEZUG_JULI_20, BEZUG_JULI_30)
        }

        self.assertEqual(3, len(daten), "das Tageswort haengt an einer Uhr")

    def test_morgen_folgt_ebenso(self) -> None:
        """Nicht nur `uebermorgen` — der ganze Block rechnete gegen die Uhr."""
        self.assertEqual(date(2026, 7, 12), self._datum("morgen", BEZUG_JULI_10))

    def test_gestern_folgt_rueckwaerts(self) -> None:
        """Der negative Versatz benutzt denselben Kalendertag."""
        self.assertEqual(date(2026, 7, 10), self._datum("gestern", BEZUG_JULI_10))

    def test_tageswort_und_dauer_fallen_zusammen(self) -> None:
        """Die Zusicherung, die der Parser an seiner Referenz-Drehung gibt.

        `uebermorgen` geht ueber den lokalen Kalendertag, `in zwei Tagen` ueber
        RELATIVE_BASE. Beide muessen denselben Moment lesen, nicht nur dieselbe
        Zone.
        """
        for bezug in (BEZUG_JULI_10, BEZUG_JULI_20, BEZUG_JULI_30):
            with self.subTest(bezug=bezug.isoformat()):
                self.assertEqual(
                    self._datum("übermorgen", bezug),
                    self._datum("in zwei Tagen", bezug),
                )


if __name__ == "__main__":
    unittest.main()
