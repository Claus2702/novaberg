"""Tests: Das Tor der GV-Strategie hinterlaesst eine Spur.

ZIEL: Wie oft das Tor der Wissensluecken und offenen Fragen oeffnet, ist am
Bestand ablesbar — ohne Nachrechnung und ohne Container-Log.

**Der Befund, gemessen am 09.09.2026:** Ueber 119 Turns einer Messreihe stand
`laenge` **116-mal auf 1**, und der `[OFFENE FRAGEN]`-Block erschien dreimal.
Beide Bedingungen des Tores — `max_laenge >= GV_STRATEGIE_MIN_LAENGE` und
`aufnahmebereitschaft > 0` — standen dabei **nur im `gv_detail`-Schnappschuss
in Redis**, den jeder Turn ueberschreibt.

> **Eine Groesse, die eine Entscheidung traegt und keine Spur hinterlaesst, ist
> im Nachhinein nur zu schaetzen.** `max_laenge` liess sich aus `turn_roh`
> nachrechnen; `aufnahmebereitschaft` nicht, weil sie Novas Emotionsverlauf
> liest, der dort nicht steht.

**Die Zeile traegt beide Bedingungen und beide Ergebnisse.** Ohne die Ergebnisse
waere nicht trennbar, ob das Tor geschlossen war oder ob es offen stand und
nichts zu finden war — zwei Faelle mit derselben leeren Antwort.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import GV_STRATEGIE_MIN_LAENGE


class StrategieTorSchwelleTest(unittest.TestCase):
    """Die Schwelle steht in der Konfiguration, nicht im Rumpf."""

    def test_die_schwelle_ist_zwei(self) -> None:
        """Ausgeschrieben statt aus dem Prueflung gerechnet: Ein Zeuge, der
        seine Erwartung aus der Konstante bezieht, macht jede Aenderung mit.
        """
        self.assertEqual(GV_STRATEGIE_MIN_LAENGE, 2)


class StrategieTorProtokollTest(unittest.TestCase):
    """Die Zeile steht im Knoten und traegt die sechs Felder.

    Geprueft am Quelltext, weil sie in einem grossen Knotenrumpf entsteht und
    von keinem Zeugen erreichbar waere, ohne den ganzen GV-Knoten zu fahren —
    er ruft dabei das Sprachmodell.
    """

    def _quelltext(self) -> str:
        import inspect

        from graph.nodes import gespraechsvektor as gv_mod

        return inspect.getsource(gv_mod)

    def test_der_knoten_schreibt_das_tor(self) -> None:
        self.assertIn('"schritt":              "strategie_tor"', self._quelltext())

    def test_die_zeile_traegt_beide_bedingungen(self) -> None:
        """Ohne sie waere die Zahl nicht nachrechenbar, nur ablesbar."""
        quelltext = self._quelltext()
        for feld in ('"max_laenge"', '"min_laenge"', '"aufnahmebereitschaft"'):
            self.assertIn(feld, quelltext, f"{feld} fehlt in der Tor-Zeile")

    def test_die_zeile_traegt_beide_ergebnisse(self) -> None:
        """*Tor zu* und *Tor offen, nichts gefunden* erzeugen dieselbe leere
        Antwort — nur die Ergebniszahlen trennen sie.
        """
        quelltext = self._quelltext()
        for feld in ('"wissensluecken"', '"offene_fragen"'):
            self.assertIn(feld, quelltext, f"{feld} fehlt in der Tor-Zeile")

    def test_sie_steht_hinter_beiden_suchen(self) -> None:
        """Sonst zaehlte sie Ergebnisse, die es beim Schreiben noch nicht gibt."""
        quelltext = self._quelltext()
        self.assertLess(
            quelltext.index("offene_fragen = staerkste_luecken"),
            quelltext.index('"schritt":              "strategie_tor"'),
            "Die Tor-Zeile steht vor der Suche nach offenen Fragen",
        )


if __name__ == "__main__":
    unittest.main()
