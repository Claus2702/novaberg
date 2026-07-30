"""Tests: Der Kalibrier-Korpus sortiert eigene Messturns aus.

Ziel: `rohturns_laden` bildet Turnpaare aus den Rohturns und laesst dabei
Nutzer-Turns ueber `KALIBRIERUNG_MAX_TURN_ZEICHEN` heraus. Die Zahl der
Aussortierten wird gezaehlt und berichtet, nicht stillschweigend abgezogen.

Hintergrund: Der erste Kalibrierlauf stand auf einem Korpus, der zu einem
Drittel aus eigenen Messturns fruehereren Sitzungen bestand. Die
Laengenverteilung trennt beide Populationen sauber — gemessen 77 Turns unter
100 Zeichen, 22 zwischen 100 und 499, **null zwischen 500 und 1499**, 48 ab
1500. Der Filter schneidet in dieser Luecke.

Zeugen dieser Datei:
  * **Die Rohturns sind konstruiert, nicht gemessen.** Jede Laenge ist per
    Bauart eindeutig ueber oder unter der Grenze, damit der Test nicht am
    Randwert haengt und nicht von der Konstante abhaengt: gerechnet wird
    gegen `KALIBRIERUNG_MAX_TURN_ZEICHEN`, nicht gegen die Zahl 500.
  * **Der Randfall steht ausdruecklich drin.** Ein Turn von genau
    `KALIBRIERUNG_MAX_TURN_ZEICHEN` Zeichen faellt heraus, weil der Filter
    `>=` prueft. Ein Test, der nur 100 gegen 2000 stellt, wuerde ein
    verrutschtes Vergleichszeichen nicht bemerken.
  * **Die Gegenprobe ist Teil des Tests, nicht ein Handgriff daneben:**
    `test_ohne_filter_waeren_alle_drin` belegt, dass derselbe Korpus ohne
    Filter drei Paare ergibt. Ohne diese Zeile wuerde ein Test, der versehentlich
    einen leeren Korpus prueft, gruen bleiben.
  * Die Paarbildung selbst — Vorantwort aus dem vorigen Rohturn, erster Turn
    ohne Vorantwort faellt heraus — ist bestehendes Verhalten und wird hier
    mitgeprueft, damit der neue Filter nicht daran vorbeischneidet.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.kalibrierung.korpus import rohturns_laden
from config import KALIBRIERUNG_MAX_TURN_ZEICHEN

# Eine Laenge klar unter und eine klar ueber der Grenze, plus der Randwert.
KURZ:  str = "k" * 40
LANG:  str = "l" * (KALIBRIERUNG_MAX_TURN_ZEICHEN * 4)
RAND:  str = "r" * KALIBRIERUNG_MAX_TURN_ZEICHEN


def _rohturn(prompt: str, antwort: str, nummer: int) -> dict:
    """Baut einen Rohturn-Satz in der Form, die `_SQL_ROHTURNS` liefert."""
    return {
        "turn_id":     f"turn-{nummer}",
        "user_prompt": prompt,
        "response":    antwort,
        "user_modus":  "fachgespraech",
        "nova_modus":  "fachgespraech",
        "erstellt_am": nummer,
    }


class KorpusLaengenfilter(unittest.TestCase):
    """Der Filter trennt Gespraechsbeitraege von eigenen Messturns."""

    def setUp(self) -> None:
        """Vier Rohturns: kurz, lang, Randwert, kurz."""
        self.rohturns = [
            _rohturn(KURZ, "Antwort 0", 0),
            _rohturn(KURZ, "Antwort 1", 1),
            _rohturn(LANG, "Antwort 2", 2),
            _rohturn(RAND, "Antwort 3", 3),
            _rohturn(KURZ, "Antwort 4", 4),
        ]

    def _laden(self) -> list:
        """Ruft `rohturns_laden` gegen die konstruierten Rohturns."""
        with patch(
            "agents.kalibrierung.korpus.db_manager.select",
            return_value=self.rohturns,
        ), patch(
            "agents.kalibrierung.korpus._intentionen_laden",
            return_value=[],
        ):
            return rohturns_laden("meister", "nova")

    def test_langer_turn_faellt_heraus(self) -> None:
        """Ein Nutzer-Turn weit ueber der Grenze kommt nicht in den Korpus."""
        paare = self._laden()
        self.assertNotIn(
            LANG, [p.user_prompt for p in paare],
            "ein Messturn ist im Korpus gelandet",
        )

    def test_randwert_faellt_heraus(self) -> None:
        """Genau auf der Grenze faellt heraus — der Filter prueft `>=`."""
        paare = self._laden()
        self.assertNotIn(
            RAND, [p.user_prompt for p in paare],
            f"ein Turn von genau {KALIBRIERUNG_MAX_TURN_ZEICHEN} Zeichen "
            f"ist drin — das Vergleichszeichen ist verrutscht",
        )

    def test_kurze_turns_bleiben(self) -> None:
        """Die Gespraechsbeitraege bleiben vollstaendig erhalten.

        Zwei Paare: Rohturn 1 (Vorantwort aus 0) und Rohturn 4 (Vorantwort
        aus 3). Rohturn 0 hat keine Vorantwort und faellt per Paarbildung
        heraus, unabhaengig vom Filter.
        """
        paare = self._laden()
        self.assertEqual(
            [p.turn_id for p in paare], ["turn-1", "turn-4"],
            "die kurzen Turns wurden nicht vollstaendig uebernommen",
        )

    def test_ohne_filter_waeren_alle_drin(self) -> None:
        """Gegenprobe: Ohne Filter ergibt derselbe Korpus vier Paare.

        Belegt, dass die Tests oben etwas messen. Faellt der Filter
        versehentlich aus, wird diese Erwartung gruen und die anderen drei rot
        — nicht umgekehrt, und nicht alle gemeinsam still.
        """
        with patch(
            "agents.kalibrierung.korpus.KALIBRIERUNG_MAX_TURN_ZEICHEN",
            len(LANG) + 1,
        ):
            paare = self._laden()

        self.assertEqual(
            [p.turn_id for p in paare],
            ["turn-1", "turn-2", "turn-3", "turn-4"],
            "ohne Filter fehlen Paare — dann prueft der Filtertest nichts",
        )


if __name__ == "__main__":
    unittest.main()
