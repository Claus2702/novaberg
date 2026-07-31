"""Tests: Umlaute und ihre ASCII-Umschreibungen fuehren zum selben Datum.

Ziel: "15. März" loest auf. Bis zum 31.07.2026 tat es das nicht — und der
Grund war die eigene Fuzzy-Korrektur.

Befund: `_MONATE` fuehrte nur die ASCII-Form "maerz". Die Fuzzy-Korrektur
fand "März" deshalb nicht als bekanntes Wort, suchte den naechsten Nachbarn,
landete auf Distanz 2 bei "maerz" — und dateparser liefert dafuer None,
waehrend es "15. März" direkt versteht. Ein Zwoelftel aller Datumsangaben
fiel durch, verursacht von dem Schritt, der Tippfehler reparieren soll.

Zeugen dieser Datei:
  * **dateparser selbst ist der Massstab**, nicht unsere Erwartung: Direkt
    befragt liefert es fuer "15. März" ein Datum und fuer "15. Maerz" None.
    Daraus folgt, welche Schreibweise die massgebliche ist — die Umlautform.
  * **Die Zuordnung wird abgeleitet, nicht gefuehrt.** Deshalb prueft ein
    Test ihren Inhalt gegen die Quelllisten statt gegen eine Literalliste;
    ein neues Wort mit Umlaut muss automatisch mitkommen.
  * **Die Nichtberuehrung ist der wichtigere Teil.** Eine Ersetzung der
    blossen Buchstabenfolge machte aus "heute" ein "heüte". Die Tests dazu
    stehen deshalb gleichberechtigt neben denen fuer die Ersetzung.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import date, datetime, timezone
from typing import Optional

from utils.zeitparser import (
    _ASCII_ZU_UMLAUT,
    _MONATE,
    _RELATIVE,
    _WOCHENTAGE,
    _ZAHLWOERTER,
    _ascii_umschrift,
    _umlaute_herstellen,
    zeit_parsen_vektor,
)

REF: datetime = datetime(2026, 7, 30, 12, 0, 0, tzinfo=timezone.utc)


def _datum(ausdruck: str) -> Optional[date]:
    """Loest auf und gibt das Datum, oder None."""
    vektor = zeit_parsen_vektor(ausdruck, REF)
    return vektor.datum.date() if vektor.datum else None


class BeideSchreibweisenErgebenDasselbe(unittest.TestCase):
    """Der Kern: Umschrift und Umlautform sind austauschbar."""

    def test_maerz(self) -> None:
        """Der Fall, der ein Zwoelftel aller Datumsangaben betraf."""
        self.assertEqual(_datum("15. März"), _datum("15. Maerz"))
        self.assertIsNotNone(_datum("15. März"))

    def test_fuenf_wochen(self) -> None:
        """Eine Dauer mit Zahlwort."""
        self.assertEqual(_datum("fünf Wochen"), _datum("fuenf Wochen"))
        self.assertIsNotNone(_datum("fuenf Wochen"))

    def test_zwoelf_tage(self) -> None:
        """Das zweite Zahlwort mit Umlaut."""
        self.assertEqual(_datum("zwölf Tage"), _datum("zwoelf Tage"))
        self.assertIsNotNone(_datum("zwoelf Tage"))

    def test_halb_fuenf(self) -> None:
        """Auch in einer Uhrzeit-Konstruktion."""
        self.assertEqual(_datum("halb fünf"), _datum("halb fuenf"))
        self.assertIsNotNone(_datum("halb fuenf"))


class NichtsAnderesWirdAngefasst(unittest.TestCase):
    """Die Gegenprobe. Ohne sie waere die Ersetzung gefaehrlicher als der Fehler."""

    def test_heute_bleibt_heute(self) -> None:
        """Eine Ersetzung der blossen Buchstabenfolge machte daraus 'heüte'."""
        self.assertEqual(_umlaute_herstellen("heute"), "heute")
        self.assertIsNotNone(_datum("heute"))

    def test_woerter_mit_ue_im_inneren(self) -> None:
        """"neue", "Freude", "steuern" enthalten die Folge und sind keine Treffer."""
        for wort in ("neue Woche", "Freude am Freitag", "steuern"):
            with self.subTest(wort=wort):
                self.assertEqual(_umlaute_herstellen(wort), wort)

    def test_nur_ganze_woerter(self) -> None:
        """"maerzlich" ist kein Monat und bleibt unberuehrt."""
        self.assertEqual(_umlaute_herstellen("maerzlich"), "maerzlich")

    def test_grossschreibung_bleibt(self) -> None:
        """Ein Satzanfang darf nicht kleingeschrieben zurueckkommen."""
        self.assertEqual(_umlaute_herstellen("Maerz"), "März")
        self.assertEqual(_umlaute_herstellen("maerz"), "märz")


class DieZuordnungWirdAbgeleitet(unittest.TestCase):
    """Sie darf keine zweite, von Hand gepflegte Liste sein.

    Genau diese Drift war die Ursache: `_MONATE` und `_ZAHLWOERTER` fuehrten
    verschiedene Konventionen, und niemand bemerkte es.
    """

    def test_jedes_umlautwort_der_quelllisten_ist_erfasst(self) -> None:
        """Ein neues Wort mit Umlaut muss automatisch mitkommen."""
        quellen = (list(_WOCHENTAGE) + list(_MONATE) + list(_RELATIVE)
                   + list(_ZAHLWOERTER.keys()))
        for wort in quellen:
            umschrift = _ascii_umschrift(wort)
            if umschrift == wort:
                continue
            with self.subTest(wort=wort):
                self.assertIn(umschrift, _ASCII_ZU_UMLAUT)

    def test_keine_umschrift_zeigt_auf_sich_selbst(self) -> None:
        """Ein Eintrag ohne Umlaut im Ziel waere eine wirkungslose Regel."""
        for umschrift, ziel in _ASCII_ZU_UMLAUT.items():
            with self.subTest(umschrift=umschrift):
                self.assertNotEqual(umschrift, ziel)

    def test_maerz_ist_darin(self) -> None:
        """Der Anlass, ausdruecklich festgehalten."""
        self.assertEqual(_ASCII_ZU_UMLAUT.get("maerz"), "märz")


if __name__ == "__main__":
    unittest.main()
