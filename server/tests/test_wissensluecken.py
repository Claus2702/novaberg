"""Tests fuer die Wissensluecken-Rechnungen.

Ziel: Der Zug zu einem Thema ist am RAND des Feldes am groessten — nicht im
Zentrum, wo Nova alles weiss, und nicht aussen, wo es sie nichts angeht.

Die umgekehrte U-Kurve faellt aus dem Produkt heraus und wird nicht eigens
modelliert. Genau das pruefen die ersten Faelle: Zentrum und Aussen muessen
BEIDE unter dem Rand liegen. Eine Summe haette diese Eigenschaft nicht.

Konzept: docs/novaberg-wissensluecken_k.md §3

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from agents.wissensluecken.berechnung import (
    LUECKE_DUBLETTE_SCHWELLE,
    STATUS_ALLE,
    STATUS_AUSGESCHLOSSEN,
    STATUS_GESCHLOSSEN,
    STATUS_OFFEN,
    ist_dublette,
    neugier_vektor_berechnen,
    neuheit_berechnen,
)
from config import NOVA_NEUGIER


class UmgekehrteUKurveTest(unittest.TestCase):
    """Der Rand zieht, Zentrum und Aussen nicht."""

    def test_rand_zieht_staerker_als_zentrum_und_aussen(self) -> None:
        zentrum: float = neugier_vektor_berechnen(0.9, 0.1)   # kennt sie
        rand:    float = neugier_vektor_berechnen(0.7, 0.7)   # der Zug
        aussen:  float = neugier_vektor_berechnen(0.1, 0.9)   # nicht ihres

        self.assertGreater(rand, zentrum)
        self.assertGreater(rand, aussen)

    def test_zentrum_und_aussen_liegen_gleichauf(self) -> None:
        """Beide sind uninteressant — aus verschiedenen Gruenden, gleich stark."""
        self.assertAlmostEqual(
            neugier_vektor_berechnen(0.9, 0.1),
            neugier_vektor_berechnen(0.1, 0.9),
            places=9,
        )

    def test_eine_summe_haette_die_eigenschaft_nicht(self) -> None:
        """Belegt, warum das Produkt gewaehlt ist und nicht die Summe.

        Bei einer Summe laege 'aussen' (0.1 + 0.9) gleichauf mit 'rand'
        (0.7 + 0.7) minus nichts — ein voellig fremdes Thema wuerde allein
        durch seine Neuheit belohnt.
        """
        self.assertAlmostEqual(0.1 + 0.9, 1.0, places=9)
        self.assertAlmostEqual(0.7 + 0.7, 1.4, places=9)
        # Produkt dreht das Verhaeltnis um:
        self.assertLess(
            neugier_vektor_berechnen(0.1, 0.9),
            neugier_vektor_berechnen(0.7, 0.7),
        )

    def test_maximum_liegt_bei_beidem_voll(self) -> None:
        self.assertAlmostEqual(
            neugier_vektor_berechnen(1.0, 1.0), NOVA_NEUGIER, places=9
        )

    def test_ein_faktor_null_loescht_den_zug(self) -> None:
        self.assertEqual(neugier_vektor_berechnen(0.0, 1.0), 0.0)
        self.assertEqual(neugier_vektor_berechnen(1.0, 0.0), 0.0)

    def test_zweimal_rechnen_liefert_bitgleich(self) -> None:
        erst: float = neugier_vektor_berechnen(0.63, 0.41)
        self.assertEqual(erst, neugier_vektor_berechnen(0.63, 0.41))


class NeuheitTest(unittest.TestCase):
    """Neuheit ist die Umkehrung der Naehe zum Bekannten."""

    def test_unbekannt_ist_maximal_neu(self) -> None:
        self.assertEqual(neuheit_berechnen(0.0), 1.0)

    def test_bereits_bekannt_ist_nicht_neu(self) -> None:
        self.assertEqual(neuheit_berechnen(1.0), 0.0)

    def test_halb_bekannt_liegt_in_der_mitte(self) -> None:
        self.assertAlmostEqual(neuheit_berechnen(0.5), 0.5, places=9)

    def test_negativer_cosine_wird_auf_eins_geklemmt(self) -> None:
        """Ein Gegensatz ist nicht 'mehr als neu' — die Skala endet bei 1.0."""
        self.assertEqual(neuheit_berechnen(-0.4), 1.0)

    def test_nicht_numerisch_wird_abgelehnt(self) -> None:
        with self.assertRaises(ValueError):
            neuheit_berechnen("sehr aehnlich")


class ValidierungTest(unittest.TestCase):
    """Ein Wert ausserhalb seines Bereichs ist ein Defekt beim Aufrufer."""

    def test_resonanz_ueber_eins_wird_abgelehnt(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            neugier_vektor_berechnen(1.2, 0.5)
        self.assertIn("resonanz", str(ctx.exception))

    def test_negative_neuheit_wird_abgelehnt(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            neugier_vektor_berechnen(0.5, -0.1)
        self.assertIn("neuheit", str(ctx.exception))

    def test_bool_gilt_nicht_als_zahl(self) -> None:
        """True ist in Python eine 1 — hier waere das ein verschleierter Defekt."""
        with self.assertRaises(ValueError):
            neugier_vektor_berechnen(True, 0.5)


class DublettenTest(unittest.TestCase):
    """Was einmal erfasst ist, wird aufgefrischt statt neu angelegt."""

    def test_knapp_unter_der_schwelle_ist_keine_dublette(self) -> None:
        self.assertFalse(ist_dublette(LUECKE_DUBLETTE_SCHWELLE - 0.01))

    def test_auf_der_schwelle_ist_eine_dublette(self) -> None:
        self.assertTrue(ist_dublette(LUECKE_DUBLETTE_SCHWELLE))

    def test_leere_tabelle_liefert_keine_dublette(self) -> None:
        """Positiver Zwilling: Die Pruefung darf nicht alles blockieren."""
        self.assertFalse(ist_dublette(0.0))

    def test_schwelle_liegt_ueber_der_lzg_dublettenschwelle(self) -> None:
        """Bewusst strenger als LZG_KNOTEN_MATCH_SCHWELLE (0.82).

        Dort wird verschmolzen, hier verworfen — und 'Dunkle Materie' gegen
        'Dunkle Materie im fruehen Universum' sollen zwei Luecken bleiben.
        """
        from config import LZG_KNOTEN_MATCH_SCHWELLE
        self.assertGreater(LUECKE_DUBLETTE_SCHWELLE, LZG_KNOTEN_MATCH_SCHWELLE)


class StatusTest(unittest.TestCase):
    """Drei Zustaende, eine Sperrwirkung."""

    def test_drei_zustaende_sind_bekannt(self) -> None:
        self.assertEqual(
            STATUS_ALLE,
            {STATUS_OFFEN, STATUS_GESCHLOSSEN, STATUS_AUSGESCHLOSSEN},
        )

    def test_zustaende_sind_verschieden(self) -> None:
        """Ein Boolean koennte das nicht: Er sagt nicht, WARUM eine Zeile
        nicht mehr zaehlt.
        """
        self.assertEqual(len(STATUS_ALLE), 3)


if __name__ == "__main__":
    unittest.main()
