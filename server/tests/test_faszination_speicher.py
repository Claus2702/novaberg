"""Zeugen: die Traegerseite der Faszination liest, was die Rechnung braucht.

Ziel: Anker-Zaehler und **verfallenes** Qualitaetsprofil je Traeger, und zwar
so, dass ein Aufrufer den Verfall nicht vergessen kann.

Diese Zeugen fassen den Produktivbestand nicht an: Der Speicher ist ersetzt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from config import POSTGRES_URL
from memory import fascination_store

MODUL: str = "memory.fascination_store"


def _verbindung(anker: list, profil: list) -> MagicMock:
    """Eine Datenbank, die auf die beiden Abfragen der Reihe nach antwortet."""
    zeiger = MagicMock()
    zeiger.fetchall.side_effect = [anker, profil]
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = zeiger
    verbindung = MagicMock(return_value=conn)
    return verbindung


class DerSpeicherLiestBeideHaelftenTest(unittest.TestCase):
    """Zwei Abfragen, nicht eine — ein JOIN verloere eine Haelfte stumm."""

    def test_ein_knoten_ohne_bruecke_behaelt_sein_profil(self) -> None:
        """Er hat kein `verbindung`-Ergebnis und trotzdem Qualitaeten."""
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([], [(11, "komplexitaet", 1.0, 0.0)])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertEqual(0, daten[11]["turns"])
        self.assertIn("komplexitaet", daten[11]["profil"])

    def test_ein_knoten_ohne_profil_behaelt_seine_zaehler(self) -> None:
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([(11, 3, 5, 2, 4)], [])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertEqual(3, daten[11]["tage"])
        self.assertEqual({}, daten[11]["profil"])

    def test_eine_leere_anfrage_oeffnet_keine_verbindung(self) -> None:
        """Ein Turn ohne gelesene Erinnerungen ist der Normalfall."""
        with patch(f"{MODUL}.psycopg2.connect") as verbindung:
            self.assertEqual({}, fascination_store.traegerdaten_lesen(POSTGRES_URL, []))
        verbindung.assert_not_called()


class UnbekannteHerkunftBleibtNoneTest(unittest.TestCase):
    """§10.2 — *unbekannt* ist nicht *vom Nutzer*."""

    def test_ohne_bekannte_herkunft_steht_none(self) -> None:
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([(11, 1, 1, 0, 0)], [])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertIsNone(daten[11]["eigenimpuls"])

    def test_mit_bekannter_herkunft_steht_der_anteil(self) -> None:
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([(11, 1, 4, 1, 4)], [])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertAlmostEqual(0.25, daten[11]["eigenimpuls"], 9)


class DerVerfallLaeuftImLesepfadTest(unittest.TestCase):
    """Sonst koennte ein zweiter Leser ihn vergessen (§10.4).

    Ein unverfallenes Profil ist von einem frischen nicht zu unterscheiden —
    und der Unterschied ist genau die Aussage der Groesse.
    """

    def test_das_profil_kommt_verfallen_zurueck(self) -> None:
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([], [(11, "komplexitaet", 1.0, 3650.0)])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertLess(daten[11]["profil"]["komplexitaet"], 1.0)

    def test_der_rohwert_steht_daneben(self) -> None:
        """Sonst ist nicht zu trennen, ob niedrig bewertet oder verfallen."""
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([], [(11, "komplexitaet", 1.0, 3650.0)])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertEqual(1.0, daten[11]["roh_profil"]["komplexitaet"])

    def test_ungewissheit_verfaellt_ueber_die_beruehrungen_des_traegers(self) -> None:
        """Wer den Knoten ansieht, sieht seine Qualitaeten an."""
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([(11, 1, 20, 0, 0)],
                               [(11, "ungewissheit", 1.0, 0.0)])):
            viele = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([(11, 1, 1, 0, 0)],
                               [(11, "ungewissheit", 1.0, 0.0)])):
            wenige = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertLess(
            viele[11]["profil"]["ungewissheit"],
            wenige[11]["profil"]["ungewissheit"],
        )


class EineQualitaetAusserhalbDesKanonsWirdUebergangenTest(unittest.TestCase):
    """Und gemeldet — sonst rechnete die Faszination auf fremdem Vokabular."""

    def test_sie_faellt_heraus_und_meldet_sich(self) -> None:
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([], [(11, "erhabenheit", 1.0, 0.0)])), \
             self.assertLogs("ki_server.memory.fascination_store", "WARNING"):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertEqual({}, daten[11]["profil"])


if __name__ == "__main__":
    unittest.main()
