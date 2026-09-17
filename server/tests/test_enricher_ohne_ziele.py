"""Tests: Ein Paar ohne aktive Ziele bekommt seinen Turn.

Anlass (17.09.2026, Betriebsmessung): Ein neuer Nutzer verlor jeden Turn im
Enricher — `AttributeError: 'float' object has no attribute 'normiert'`. Der
Zweig ohne Ziele gab die Zahl `0.0` zurueck, beide Aufrufer lesen dort
`.normiert`. Die Antwort blieb leer (20 Vorfaelle im Serverlog).

Der Zeuge prueft den Typ des zweiten Rueckgabewerts, nicht seinen Wert: Ein
Nullwert, der aussieht wie ein echter, ist der Fehler selbst.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from ei.gravitation import GRAVITATIONSTERM_CAP, Gravitationsterm
from graph.nodes import enricher


class NullTermTest(unittest.TestCase):

    def test_ohne_ziele_kommt_ein_gravitationsterm_zurueck(self) -> None:
        with patch.object(enricher, "ziele_aktive_laden", return_value=[]):
            aktiviert, term, sog = enricher._compute_ziele_und_gravitation(
                [0.1] * 768, "postgresql://unbenutzt", "neues_paar", "nova",
            )
        self.assertEqual(aktiviert, [])
        self.assertIsInstance(term, Gravitationsterm)
        self.assertEqual((term.roh, term.normiert, term.cap), (0.0, 0.0, GRAVITATIONSTERM_CAP))
        self.assertEqual(sog, 0.0)

    def test_der_aufrufer_kommt_an_den_normierten_wert(self) -> None:
        """Was den Turn abbrach: `.normiert` auf dem zweiten Rueckgabewert."""
        with patch.object(enricher, "ziele_aktive_laden", return_value=[]):
            _, term, _ = enricher._compute_ziele_und_gravitation(
                [0.1] * 768, "postgresql://unbenutzt", "neues_paar", "nova",
            )
        self.assertEqual(term.normiert, 0.0)


if __name__ == "__main__":
    unittest.main()
