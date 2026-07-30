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

from agents.kalibrierung.korpus import _intentionen_laden, rohturns_laden
from config import GV_INITIATIVE_FUEHREND, KALIBRIERUNG_MAX_TURN_ZEICHEN

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


class IntentionenLesen(unittest.TestCase):
    """Das Intentionen-Feld ist eine JSON-Liste und wird geparst.

    Der Defekt, gegen den diese Klasse steht: Ein Split an Kommas liefert
    `["reflexion"` statt `reflexion`. Solche Bruchstuecke treffen
    `GV_INITIATIVE_FUEHREND` nie — und weil die Liste dabei **nicht leer** ist,
    gilt M1 als „nicht fuehrend" statt als „fehlend" und traegt ein hartes
    -1.0 in jeden Turn. Gemessen am 30.07.2026 hatte damit **keiner** von 144
    Turns eine fuehrende Intention; geparst sind es 40 von 99.
    """

    def _laden(self, roh: object) -> list:
        """Ruft `_intentionen_laden` gegen einen vorgegebenen Redis-Wert."""
        with patch(
            "agents.kalibrierung.korpus.db_manager.select_one",
            return_value={"kzg_id": "kzg:test:test:1"},
        ), patch(
            "agents.kalibrierung.korpus.redis_manager"
        ) as rm:
            rm.client.hget.return_value = roh
            return _intentionen_laden("turn-1")

    def test_json_liste_wird_geparst(self) -> None:
        """Aus der JSON-Liste kommen die nackten Werte."""
        self.assertEqual(
            self._laden('["reflexion", "information_teilen"]'),
            ["reflexion", "information_teilen"],
        )

    def test_keine_klammern_und_anfuehrungszeichen_im_wert(self) -> None:
        """Kein Wert traegt Syntax des Transportformats.

        Der direkte Anschlag gegen den alten Split: Er lieferte genau diese
        Zeichen im Wert.
        """
        for wert in self._laden('["reflexion", "information_teilen"]'):
            self.assertNotIn("[", wert, f"Klammer im Wert: {wert!r}")
            self.assertNotIn("]", wert, f"Klammer im Wert: {wert!r}")
            self.assertNotIn('"', wert, f"Anfuehrungszeichen im Wert: {wert!r}")

    def test_fuehrende_intention_trifft_die_menge(self) -> None:
        """Der Test, der den Defekt gefangen haette.

        Eine fuehrende Intention muss nach dem Lesen in
        `GV_INITIATIVE_FUEHREND` gefunden werden. Genau das war zwei Monate
        lang nicht der Fall, und keine Zahl im Kalibrierbericht hat es gezeigt:
        Der Defekt sah aus wie ein Paar, das nie die Initiative nimmt.
        """
        fuehrend: str = sorted(GV_INITIATIVE_FUEHREND)[0]
        gelesen = self._laden(f'["{fuehrend}", "reflexion"]')
        self.assertTrue(
            any(i in GV_INITIATIVE_FUEHREND for i in gelesen),
            f"{gelesen} trifft GV_INITIATIVE_FUEHREND nicht — M1 ist blind",
        )

    def test_unlesbares_feld_gilt_als_fehlend(self) -> None:
        """Kaputtes JSON ergibt die leere Liste, nicht Bruchstuecke.

        Leer heisst fuer `fuehrung_messen` „fehlend" und wird benannt. Eine
        gefuellte Liste mit unpassenden Werten hiesse „nicht fuehrend" und
        waere ein stiller Beitrag von -1.0.
        """
        self.assertEqual(self._laden('["reflexion", '), [])

    def test_nichtliste_gilt_als_fehlend(self) -> None:
        """Gueltiges JSON, das keine Liste ist, ergibt ebenfalls leer."""
        self.assertEqual(self._laden('{"reflexion": true}'), [])

    def test_leeres_feld_gilt_als_fehlend(self) -> None:
        """Fehlendes Feld ist der legitime Leerfall."""
        self.assertEqual(self._laden(None), [])


if __name__ == "__main__":
    unittest.main()
