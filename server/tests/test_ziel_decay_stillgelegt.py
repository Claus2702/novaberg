"""Tests fuer die Stilllegung des ZielDecayAgent.

Ziel: Solange ZIEL_DECAY_AKTIV false ist, meldet der Agent keine periodische
Aufgabe und schreibt auch bei direktem Aufruf keine Motivation zurueck.

Hintergrund: Die Formel multipliziert die bereits verfallene Motivation erneut
mit einem Faktor aus dem GESAMTALTER des Ziels und schreibt das Ergebnis in
dasselbe Feld (ZIEL-DECAY-FORMEL-KUMULATIV). Belegt am Lauf vom 27.07.2026,
18:39:58 UTC: Ziel 3 von 0.65 auf 0.640, Ziel 4 von 0.70 auf 0.690.

Bis Chat 112 war der fehlende Router-Eintrag die faktische Sicherung. Sie ist
entfallen, seit der Router unbekannte Namen ueber Namensgleichheit aufloest.
Deshalb pruefen diese Tests BEIDE Gates: Ein Gate im Scheduling allein liesse
einen direkt gerouteten Aufruf weiter schreiben.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.ziel_decay.agent import ZielDecayAgent

ZIEL_DECAY_LOGGER: str = "ki_server.agents.ziel_decay"


class TestZielDecayStillgelegt(unittest.TestCase):
    """Beide Gates, gegen den stillgelegten Zustand."""

    def test_meldet_keine_periodische_aufgabe(self) -> None:
        with patch("agents.ziel_decay.agent.ZIEL_DECAY_AKTIV", False):
            with self.assertLogs(ZIEL_DECAY_LOGGER, level="INFO"):
                self.assertIsNone(ZielDecayAgent().periodic_task())

    def test_invoke_schreibt_nichts(self) -> None:
        """Der direkte Aufruf laedt keine Ziele und ruft keinen Schreiber.

        Geprueft wird die Wirkung, nicht die Absicht: Waeren die drei
        memory.ziele-Funktionen erreichbar, wuerde der Lauf Motivation
        anpassen. Die Zusicherung ist, dass keine davon gerufen wird.
        """
        with patch("agents.ziel_decay.agent.ZIEL_DECAY_AKTIV", False), \
             patch("agents.ziel_decay.agent.ziele_aktive_laden") as laden, \
             patch("agents.ziel_decay.agent.ziel_motivation_anpassen") as anpassen, \
             patch("agents.ziel_decay.agent.ziel_deaktivieren") as deaktivieren:

            with self.assertLogs(ZIEL_DECAY_LOGGER, level="INFO"):
                ergebnis = ZielDecayAgent().invoke({})

        laden.assert_not_called()
        anpassen.assert_not_called()
        deaktivieren.assert_not_called()
        self.assertEqual(ergebnis["status"], "abgeschlossen")
        self.assertFalse(ergebnis["ergebnis"]["aktiv"])

    def test_eingeschaltet_meldet_wieder_eine_aufgabe(self) -> None:
        """Positiver Zwilling: Das Gate ist ein Schalter, keine Entfernung.

        Ohne diesen Fall bestuende der Test oben auch dann, wenn jemand die
        periodische Aufgabe ersatzlos geloescht haette.
        """
        with patch("agents.ziel_decay.agent.ZIEL_DECAY_AKTIV", True):
            aufgabe = ZielDecayAgent().periodic_task()

        self.assertIsNotNone(aufgabe)
        self.assertEqual(aufgabe.name, "ziel_decay")


if __name__ == "__main__":
    unittest.main()
