"""Tests: die Lesezeit des Prompts steht in der Verbrauchszeile.

Ziel: Der Prefix-Cache wird im Betrieb sichtbar. Die Token-Zahl zeigt ihn
nicht — sie ist bei kaltem und warmem Prefix dieselbe; nur die Zeit
unterscheidet die Faelle.

Zeugen dieser Datei:
  * **Die erwarteten Werte sind von Hand gerechnet.** 1 000 000 000 ns sind
    eine Sekunde, und 1915 Token darin sind 1915 tps.
  * **Ein fehlendes Feld wird von einer gemessenen Null getrennt.** Ein
    Fernanbieter meldet die Groesse nicht; das darf nicht wie *0 Sekunden*
    aussehen.
  * **Der Ollama-Weg wird auf seinen Aufruf geprueft, nicht nur die Rechnung.**
    `record_usage` hatte bis zum 07.09.2026 genau einen Aufrufer, und der lag
    im Fern-Weg — die Rechnung allein waere gruen und wirkungslos gewesen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from services.model_costs import _lesezeit


class DieLesezeitWirdGerechnet(unittest.TestCase):
    """Aus Nanosekunden werden Sekunden und eine Rate."""

    def test_eine_sekunde_ergibt_die_tokenzahl_als_rate(self) -> None:
        """1915 Token in 1 s sind 1915 tps — von Hand gerechnet."""
        self.assertEqual(
            {"prompt_lesen_s": 1.0, "prompt_lesen_tps": 1915.0},
            _lesezeit(1915, 1_000_000_000),
        )

    def test_der_warme_lauf_zeigt_sich_in_der_rate(self) -> None:
        """`[gemessen 07.09.2026]` 1915 Token in 92 ms — der Cache traegt.

        Kalt waren es 11,61 s fuer dieselben Token. **Der Unterschied ist
        Faktor 126 in der Rate und null in der Tokenzahl** — genau deshalb
        steht die Zeit hier.
        """
        warm = _lesezeit(1915, 92_054_000)
        kalt = _lesezeit(1915, 11_613_663_000)
        self.assertGreater(warm["prompt_lesen_tps"], kalt["prompt_lesen_tps"] * 100)
        # **Nicht auf die Tokenzahl zurueckrechnen.** Die Felder sind fuer die
        # Auswertung gerundet — Sekunden auf vier, die Rate auf eine Stelle —,
        # und das Produkt trifft dann um eins daneben. Eine Zusicherung, die
        # das verlangt, prueft die Rundung statt der Groesse.
        self.assertAlmostEqual(0.0921, warm["prompt_lesen_s"], places=4)
        self.assertAlmostEqual(11.6137, kalt["prompt_lesen_s"], places=4)

    def test_ohne_meldung_bleibt_das_feld_weg(self) -> None:
        """Nicht gemeldet ist nicht null.

        Ein Fernanbieter liefert die Groesse nicht. Stuende dort 0.0, waere
        *kein Messwert* von *in null Sekunden gelesen* nicht zu trennen — und
        jede Auswertung ueber den Bestand zoege den Mittelwert nach unten.
        """
        self.assertEqual({}, _lesezeit(1915, 0))
        self.assertEqual({}, _lesezeit(1915, None))

    def test_ohne_eingabetoken_bleibt_die_rate_weg(self) -> None:
        """Eine Rate ohne Zaehler waere eine Division durch null."""
        self.assertEqual({"prompt_lesen_s": 0.5}, _lesezeit(0, 500_000_000))


class DerLokalePfadBuchtJetztAuch(unittest.TestCase):
    """Die Verdrahtung, nicht die Rechnung.

    `record_usage` hatte bis zum 07.09.2026 **einen** Aufrufer, und der lag im
    Fern-Weg. Jede Verbrauchszeile des Bestands stammt von dort; ein
    Kostenvergleich lokal gegen fern war nicht moeglich.
    """

    def test_der_ollama_weg_ruft_record_usage_mit_der_lesezeit(self) -> None:
        """Geholt **und** durchgereicht — zwei Schritte, ein Zeuge."""
        from services import llm_provider

        client = MagicMock()
        client.chat.return_value = {
            "model": "qwen36-cpu",
            "message": {"content": "Antwort", "thinking": None},
            "prompt_eval_count": 1915,
            "eval_count": 40,
            "prompt_eval_duration": 92_054_000,
            "done": True,
        }
        anbieter = llm_provider.OllamaProvider(client, "qwen36-cpu", 32768)
        with patch.object(llm_provider, "record_usage") as bucher:
            anbieter.chat([{"role": "user", "content": "x"}], caller="probe")
        self.assertTrue(bucher.called, "der lokale Weg bucht nicht")
        args = bucher.call_args[0]
        self.assertEqual(1915, args[2])
        self.assertEqual(40, args[3])
        self.assertEqual(92_054_000, args[4], "die Lesezeit kommt nicht an")


if __name__ == "__main__":
    unittest.main()
