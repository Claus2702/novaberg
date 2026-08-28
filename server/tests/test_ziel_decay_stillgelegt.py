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
        """Der direkte Aufruf loest keinen Verfallslauf aus.

        Geprueft wird die Wirkung, nicht die Absicht: Waere ziel_decay_lauf
        erreichbar, schriebe er Motivation und deaktivierte Ziele. Die
        Zusicherung ist, dass er nicht gerufen wird.
        """
        with patch("agents.ziel_decay.agent.ZIEL_DECAY_AKTIV", False), \
             patch("agents.ziel_decay.agent.ziel_decay_lauf") as lauf:

            with self.assertLogs(ZIEL_DECAY_LOGGER, level="INFO"):
                ergebnis = ZielDecayAgent().invoke({})

        lauf.assert_not_called()
        self.assertEqual(ergebnis["status"], "abgeschlossen")
        self.assertFalse(ergebnis["ergebnis"]["aktiv"])

    def test_eingeschaltet_loest_den_lauf_aus(self) -> None:
        """Positiver Zwilling: Das Gate ist ein Schalter, keine Entfernung.

        Ohne diesen Fall bestuende der Test oben auch dann, wenn der Aufruf
        ersatzlos aus invoke() verschwunden waere.
        """
        with patch("agents.ziel_decay.agent.ZIEL_DECAY_AKTIV", True), \
             patch("agents.ziel_decay.agent.ziel_decay_lauf") as lauf, \
             patch.object(ZielDecayAgent, "_audit_log"), \
             patch.object(ZielDecayAgent, "_log_forensik"):
            lauf.return_value = {"verarbeitet": 0, "deaktiviert": 0,
                                 "ohne_anker": 0, "error": None}
            ZielDecayAgent().invoke({})

        # Seit dem 28.08.2026 faehrt der Agent zwei Typen (mittel- und
        # kurzfristig, Scheibe 2 des Lage-Konzepts) — ein Lauf je Typ.
        self.assertEqual(lauf.call_count, 2)

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
