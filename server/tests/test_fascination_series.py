"""Zeugen: die Reihe des Bestandslaufs wird gelesen, nicht nachgerechnet.

Ziel: Wer die Reihe abfragt, erfaehrt, **ob sie kalibrieren kann** — und wenn
nicht, warum. Eine Ampel ohne Grund waere ein Urteil ohne Eingangsgroesse.

Der teure Fall ist nicht die falsche Zahl, sondern die stille: eine Reihe, die
sich nicht bewegt und trotzdem wie eine Messung aussieht.

Diese Zeugen fassen den Produktivbestand nicht an: Die Verbindung ist ersetzt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from config import POSTGRES_URL
from tools import fascination_series

MODUL: str = "tools.fascination_series"


def _verbindung(zeilen: list[dict]) -> MagicMock:
    """Eine Datenbank, die genau diese Zeilen liefert."""
    zeiger = MagicMock()
    zeiger.fetchall.return_value = zeilen
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = zeiger
    return MagicMock(return_value=conn)


def _zeile(minuten: int, **felder: object) -> dict:
    """Eine Protokollzeile des Bestandslaufs, `minuten` nach dem Nullpunkt."""
    inhalt: dict = {
        "phase": "faszination_bestand", "traeger": 50, "gerechnet": 50,
        "ohne_bindung": 7, "ohne_strang": 0, "roh_min": 0.0,
        "roh_median": 0.3, "roh_max": 0.6, "werte": {},
    }
    inhalt.update(felder)
    return {
        "erstellt_am": datetime(2026, 9, 5, tzinfo=timezone.utc)
                       + timedelta(minutes=minuten),
        "inhalt": inhalt,
    }


class DieReiheWirdVorwaertsGelesenTest(unittest.TestCase):
    """Die Abfrage holt rueckwaerts, die Reihe wird vorwaerts gebraucht."""

    def test_die_juengste_zeile_steht_am_ende(self) -> None:
        # Die Datenbank liefert absteigend — so lautet das ORDER BY.
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([_zeile(60), _zeile(0)])):
            gelesen = fascination_series.series_load(POSTGRES_URL)
        zeitpunkte = [lauf["zeitpunkt"] for lauf in gelesen["laeufe"]]
        self.assertEqual(
            sorted(zeitpunkte), zeitpunkte,
            "Eine rueckwaerts gelesene Reihe kehrt jedes Delta im Vorzeichen "
            "um — der Verlauf saehe fallend aus, wo er steigt",
        )


class EinFehlenderStrangzaehlerBleibtNoneTest(unittest.TestCase):
    """Vor dem 05.09.2026 trug die Zeile das Feld nicht.

    **Ein Default von 0 waere hier der stille Fehler**: Er sagt *kein Traeger
    ohne Strangbezug* und meint *nicht gemessen*. Beide sehen in der Tabelle
    gleich aus, und nur einer ist eine Auskunft.
    """

    def test_alte_zeile_meldet_none_statt_null(self) -> None:
        alt: dict = _zeile(0)
        del alt["inhalt"]["ohne_strang"]
        with patch(f"{MODUL}.psycopg2.connect", _verbindung([alt])):
            gelesen = fascination_series.series_load(POSTGRES_URL)
        self.assertIsNone(
            gelesen["laeufe"][0]["ohne_strang"],
            "Eine Zeile ohne den Zaehler darf nicht als 'null Traeger ohne "
            "Strangbezug' gelesen werden",
        )


class EinUngueltigerDeckelWirdVerworfenTest(unittest.TestCase):
    """Kein Default, kein stiller Ersatz — die Abfrage laeuft gar nicht."""

    def test_null_als_deckel_meldet_und_verwirft(self) -> None:
        with patch(f"{MODUL}.psycopg2.connect") as verbindung:
            gelesen = fascination_series.series_load(POSTGRES_URL, 0)
        verbindung.assert_not_called()
        self.assertIn("0", gelesen["error"])
        self.assertEqual([], gelesen["laeufe"])

    def test_wahr_ist_keine_zahl(self) -> None:
        """`True` ist in Python eine 1 — als Deckel ist es ein Tippfehler."""
        with patch(f"{MODUL}.psycopg2.connect") as verbindung:
            gelesen = fascination_series.series_load(POSTGRES_URL, True)
        verbindung.assert_not_called()
        self.assertIsNotNone(gelesen["error"])


class DerBerichtNenntImmerSeinenGrundTest(unittest.TestCase):
    """Eine Ampel ohne Begruendung ist ein Urteil ohne Eingangsgroesse."""

    def test_ein_einzelner_lauf_ist_keine_reihe(self) -> None:
        bericht = fascination_series.series_report(
            [dict(_zeile(0)["inhalt"], zeitpunkt=datetime.now(timezone.utc))],
        )
        self.assertFalse(bericht["kalibrierfaehig"])
        self.assertIn("Punkte", bericht["grund"])

    def test_eine_leere_reihe_ist_kein_fehler(self) -> None:
        """Der Zustand vor dem ersten Tageslauf."""
        bericht = fascination_series.series_report([])
        self.assertEqual(0, bericht["punkte"])
        self.assertFalse(bericht["kalibrierfaehig"])
        self.assertTrue(bericht["grund"])

    def test_eine_flache_reihe_meldet_dass_sie_nichts_misst(self) -> None:
        """Der teure Fall: Zeilen sind da, Bewegung ist keine."""
        werte: dict = {"11": 0.25, "12": 0.31}
        laeufe = [
            dict(_zeile(0)["inhalt"], werte=werte,
                 zeitpunkt=datetime(2026, 9, 5, tzinfo=timezone.utc)),
            dict(_zeile(60)["inhalt"], werte=dict(werte),
                 zeitpunkt=datetime(2026, 9, 6, tzinfo=timezone.utc)),
        ]
        bericht = fascination_series.series_report(laeufe)
        self.assertEqual(0, bericht["traeger_bewegt"])
        self.assertFalse(
            bericht["kalibrierfaehig"],
            "Eine Reihe ohne einen einzigen bewegten Traeger misst nichts — "
            "sie darf nicht als kalibrierfaehig gelten",
        )
        self.assertIn("bewegt sich kein einziger", bericht["grund"])

    def test_eine_bewegte_reihe_nennt_den_unerreichten_deckel(self) -> None:
        laeufe = [
            dict(_zeile(0)["inhalt"], roh_median=0.28, roh_max=0.52,
                 werte={"11": 0.25},
                 zeitpunkt=datetime(2026, 9, 5, tzinfo=timezone.utc)),
            dict(_zeile(60)["inhalt"], roh_median=0.34, roh_max=0.64,
                 werte={"11": 0.31},
                 zeitpunkt=datetime(2026, 9, 6, tzinfo=timezone.utc)),
        ]
        bericht = fascination_series.series_report(laeufe)
        self.assertEqual(1, bericht["traeger_bewegt"])
        self.assertTrue(bericht["kalibrierfaehig"])
        self.assertFalse(bericht["deckel_erreicht"])
        self.assertIn("Halbstrecken", bericht["grund"])
        self.assertAlmostEqual(0.06, bericht["median_spanne"], places=4)

    def test_ein_erreichter_deckel_wird_als_pruefbar_gemeldet(self) -> None:
        """Erst hier ist `FASZ_MAXIMUM` ueberhaupt eine pruefbare Setzung."""
        laeufe = [
            dict(_zeile(0)["inhalt"], roh_median=0.9, roh_max=1.4,
                 werte={"11": 0.5},
                 zeitpunkt=datetime(2026, 9, 5, tzinfo=timezone.utc)),
            dict(_zeile(60)["inhalt"], roh_median=1.2,
                 roh_max=fascination_series.FASZ_MAXIMUM,
                 werte={"11": 0.9},
                 zeitpunkt=datetime(2026, 9, 6, tzinfo=timezone.utc)),
        ]
        bericht = fascination_series.series_report(laeufe)
        self.assertTrue(bericht["deckel_erreicht"])
        self.assertIn("pruefbar", bericht["grund"])


class NurTraegerAusBeidenLaeufenZaehlenTest(unittest.TestCase):
    """Ein neu hinzugekommener Traeger hat sich nicht bewegt — er ist neu."""

    def test_ein_neuer_traeger_gilt_nicht_als_bewegung(self) -> None:
        laeufe = [
            dict(_zeile(0)["inhalt"], werte={"11": 0.25},
                 zeitpunkt=datetime(2026, 9, 5, tzinfo=timezone.utc)),
            dict(_zeile(60)["inhalt"], werte={"11": 0.25, "12": 0.40},
                 zeitpunkt=datetime(2026, 9, 6, tzinfo=timezone.utc)),
        ]
        bericht = fascination_series.series_report(laeufe)
        self.assertEqual(
            0, bericht["traeger_bewegt"],
            "Ein Traeger, den es im ersten Lauf nicht gab, ist Zuwachs und "
            "keine Bewegung — sonst meldet jeder Profil-Lauf eine bewegte Reihe",
        )


if __name__ == "__main__":
    unittest.main()
