"""Zeugen fuer die Kostenzeile der Statusleiste.

**Die Form steht in `ui/formatierung.py` und nicht in `status_bar.py`**, weil
sie dort ohne GTK pruefbar ist. Eine Anzeige, deren Format nur im Widget
lebt, ist genau so lange richtig, wie jemand hinsieht.

`[gemessen]` — 06.09.2026, erster Betriebsblick: Die Zeile zeigte
`Heute: $0.009 · Monat: $0.01`. Das waren **nicht** zwei Zahlen, sondern
$0,013799 zweimal, verschieden gerundet. Solange der Monat jung ist, sind
Tag und Monat gleich; die unterschiedliche Stellenzahl machte daraus zwei
Werte, die man gegeneinander liest.
"""

import unittest

from ui.formatierung import kosten_zeile


class GleicheGenauigkeitTest(unittest.TestCase):
    """Der Befund aus dem Betrieb, als Zeuge."""

    def test_gleiche_werte_sehen_gleich_aus(self) -> None:
        """Rot, sobald Tag und Monat wieder verschieden gerundet werden."""
        zeile: str = kosten_zeile(0.0032, 0.013799, 0.013799)
        self.assertIn("Heute: $0.0138", zeile)
        self.assertIn("Monat: $0.0138", zeile)

    def test_ein_turn_verschwindet_nicht_in_der_rundung(self) -> None:
        """Ein ganzer Graph-Durchlauf liegt bei $0,0016 bis $0,0032."""
        self.assertIn("Turn: $0.0016", kosten_zeile(0.0016, 1.0, 1.0))


class StrichStattNullTest(unittest.TestCase):
    """`None` heisst *nicht ermittelt* — nicht *kostenlos*."""

    def test_nicht_ermittelt_wird_zum_strich(self) -> None:
        self.assertEqual(
            kosten_zeile(None, None, None),
            "Turn: — · Heute: — · Monat: —",
        )

    def test_eine_echte_null_bleibt_eine_null(self) -> None:
        """Der Unterschied, auf den es ankommt."""
        self.assertIn("Turn: $0.0000", kosten_zeile(0.0, None, None))
        self.assertNotIn("Turn: —", kosten_zeile(0.0, None, None))

    def test_ein_einzelner_ausfall_nimmt_die_uebrigen_nicht_mit(self) -> None:
        zeile: str = kosten_zeile(None, 0.0222, 0.0222)
        self.assertIn("Turn: —", zeile)
        self.assertIn("Heute: $0.0222", zeile)


class FormTest(unittest.TestCase):
    """Die Zeile traegt immer drei Posten."""

    def test_drei_posten_in_fester_reihenfolge(self) -> None:
        zeile: str = kosten_zeile(1.0, 2.0, 3.0)
        self.assertEqual(zeile.count("·"), 2)
        self.assertLess(zeile.index("Turn:"), zeile.index("Heute:"))
        self.assertLess(zeile.index("Heute:"), zeile.index("Monat:"))


if __name__ == "__main__":
    unittest.main()
