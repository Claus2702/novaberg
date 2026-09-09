"""Zeugen: Ein lokales Modell kostet keinen Anbieter Geld.

Ziel: `cost_usd` rechnete bis zum 09.09.2026 **jeden** Aufruf mit den
OpenRouter-Preisen — sie bekam das Modell nicht einmal als Argument.

`[gemessen 09.09.2026]` An einem Tag mit lokalem Gespraechspfad standen
**1,16 USD** fuer 5210 Aufrufe von `gemma4-a4b-gpu` in der Kostenspalte,
gegen **0,0116 USD** fuer die 57 echten Fernaufrufe. Die Zahl im Client
stammte fast vollstaendig aus Aufrufen, die nichts kosten.

**Warum es unsichtbar war, und warum ausgerechnet jetzt nicht mehr.** Bis
zum 07.09.2026 buchte der lokale Pfad ueberhaupt nicht: `record_usage` hatte
einen einzigen Aufrufer, und der lag im Fern-Weg. Erst als die Buchung beide
Pfade erfasste, schlug die fehlende Modellunterscheidung durch — **die
Abhilfe des einen Defekts machte den anderen sichtbar.**

Zeugen dieser Datei:
  * **Die Menge der lokalen Modelle ist abgeleitet, nicht gepflegt.** Sie
    kommt aus `OLLAMA_CONNECTORS`; ein neuer Connector bringt sein Modell von
    selbst mit. Eine Zweitliste altert lautlos — diese Klasse hat das Projekt
    fuenfmal getroffen.
  * **Keine Namensheuristik.** Ein Fernmodell am Schraegstrich zu erkennen
    waere eine Annahme ueber Namen statt ueber Herkunft.
  * **Eine fehlende Modellangabe ist nicht kostenlos.** Sie bucht zum
    Fernpreis und meldet sich — eine stille Null machte einen defekten
    Aufrufer von einem lokalen Modell ununterscheidbar.
  * **Der Aufrufer reicht das Modell durch.** Ohne das nuetzt der Parameter
    nichts, und der Zustand von vor dem 09.09.2026 waere zurueck.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from config import OLLAMA_CONNECTORS
from services.model_costs import LOKALE_MODELLE, cost_usd


class LokaleModelleKostenNichts(unittest.TestCase):
    """Der Kern: wer auf dieser Maschine antwortet, kostet keinen Anbieter."""

    def test_lokales_modell_kostet_null(self):
        """Auch bei sehr vielen Token."""
        for modell in sorted(LOKALE_MODELLE):
            self.assertEqual(
                cost_usd(1_000_000, 1_000_000, modell), 0.0,
                f"{modell} laeuft lokal und darf nichts kosten",
            )

    def test_fernmodell_kostet_weiterhin(self):
        """Die Gegenprobe — sonst wuerde gar nichts mehr gebucht."""
        self.assertGreater(cost_usd(1_000_000, 0, "deepseek/deepseek-v4-flash-0731"), 0.0)

    def test_das_laufende_modell_ist_erfasst(self):
        """`gemma4-a4b-gpu` steht im Gespraechspfad und muss dabei sein."""
        self.assertIn("gemma4-a4b-gpu", LOKALE_MODELLE)


class DieMengeIstAbgeleitet(unittest.TestCase):
    """Sie kommt aus der Konfiguration, nicht aus einer gepflegten Liste."""

    def test_deckt_alle_connectoren(self):
        """Jedes `*_model` jedes Connectors ist enthalten."""
        erwartet = {
            wert
            for eintrag in OLLAMA_CONNECTORS.values()
            for schluessel, wert in eintrag.items()
            if schluessel.endswith("_model") and isinstance(wert, str)
        }
        self.assertEqual(
            LOKALE_MODELLE, frozenset(erwartet),
            "Die Menge muss aus OLLAMA_CONNECTORS folgen. Weicht sie ab, ist "
            "eine Zweitliste entstanden, und die altert lautlos.",
        )

    def test_nicht_leer(self):
        """Eine leere Menge wuerde jeden Aufruf als fern buchen — still."""
        self.assertGreater(len(LOKALE_MODELLE), 0)


class FehlendeAngabeIstNichtKostenlos(unittest.TestCase):
    """Ein defekter Aufrufer darf nicht wie ein lokales Modell aussehen."""

    def test_leeres_modell_bucht_zum_fernpreis(self):
        self.assertGreater(cost_usd(1_000_000, 0), 0.0)

    def test_leeres_modell_meldet_sich(self):
        with self.assertLogs("ki_server.services.model_costs", level="ERROR") as protokoll:
            cost_usd(1000, 100)
        self.assertTrue(
            any("ohne Modellangabe" in z for z in protokoll.output),
            "Ein Aufruf ohne Modell muss sich melden — sonst ist ein defekter "
            "Aufrufer von einem lokalen Modell nicht zu unterscheiden",
        )

    def test_unbekanntes_modell_bucht_zum_fernpreis(self):
        """Ein neues Ollama-Modell ausserhalb der Connectoren faellt auf."""
        self.assertGreater(cost_usd(1_000_000, 0, "irgendein-neues-gpu"), 0.0)


class DerAufruferReichtDurch(unittest.TestCase):
    """Ohne das nuetzt der Parameter nichts."""

    def test_record_usage_gibt_das_modell_weiter(self):
        from services.model_costs import record_usage

        # `log_token` wird in `record_usage` lokal importiert — der Patch
        # muss deshalb am Herkunftsmodul greifen, nicht am Aufrufer.
        with patch("services.model_costs.cost_usd", return_value=0.0) as rechnung, \
             patch("memory.pipeline_log.log_token"):
            record_usage("test", "gemma4-a4b-gpu", 100, 50)

        rechnung.assert_called_once()
        self.assertIn(
            "gemma4-a4b-gpu", rechnung.call_args.args,
            "Das Modell muss in die Rechnung gehen — sonst ist der Zustand "
            "von vor dem 09.09.2026 zurueck",
        )


if __name__ == "__main__":
    unittest.main()
