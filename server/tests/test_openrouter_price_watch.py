"""Zeugen: Der Preiswaechter meldet, was sich am Endpunkt geaendert hat.

Ziel: Der Rabatt von 64,3 % traegt die Wirtschaftlichkeit des Fernmodells,
und **die Schnittstelle nennt keine Frist dazu**. Ein Preis, der still auf
Listenniveau zurueckginge, faende sich in der Rechnung und sonst nirgends.

Zeugen dieser Datei:
  * **Jede Sorte Abweichung hat ihren eigenen Zeugen** — Preis, Rabatt,
    Kontextfenster, Quantisierung, gefuehrte Parameter. Ein Waechter, der nur
    auf den Preis sieht, uebersaehe, dass derselbe Anbieter morgen in fp4
    rechnet.
  * **Der Gleichstand ist eigens bezeugt.** Eine Pruefung, die immer etwas
    meldet, wird nach dem dritten Mal nicht mehr gelesen (`19_WERKZEUGE` §5).
  * **Der verschwundene Anbieter ist der interessante Fall.** Mit
    abgeschaltetem Rueckfall antwortet der Server dann gar nicht mehr; der
    Waechter sagt warum, bevor jemand einen Stacktrace liest.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from typing import Optional
from unittest.mock import patch

from tools import openrouter_price_watch as watch

EINGANG: float = 0.04998
AUSGANG: float = 0.09996
FENSTER: int = 1_048_576


def _endpunkt(
    prompt:     str = "0.00000004998",
    completion: str = "0.00000009996",
    discount:   Optional[float] = 0.643,
    context:    int = FENSTER,
    quant:      str = "fp8",
    parameter:  Optional[list[str]] = None,
    tag:        str = "baidu/fp8",
) -> dict:
    """Baut einen Endpunkt in der Form der Schnittstelle."""
    preise: dict = {"prompt": prompt, "completion": completion}
    if discount is not None:
        preise["discount"] = discount
    return {
        "tag":                  tag,
        "quantization":         quant,
        "context_length":       context,
        "pricing":              preise,
        "supported_parameters": parameter if parameter is not None else [
            "temperature", "top_p", "max_tokens", "stop", "response_format",
            "structured_outputs", "tools", "tool_choice", "reasoning",
            "include_reasoning", "reasoning_effort",
        ],
    }


class AntwortAttrappe:
    """Steht fuer eine `httpx.Response`."""

    def __init__(self, status_code: int, rumpf: object, text: str = "") -> None:
        """Haelt Status, Rumpf und Rohtext."""
        self.status_code: int    = status_code
        self._rumpf:      object = rumpf
        self.text:        str    = text or str(rumpf)

    def json(self) -> object:
        """Gibt den Rumpf."""
        return self._rumpf


class ClientAttrappe:
    """Steht fuer einen `httpx.Client` mit einer vorbereiteten Antwort."""

    def __init__(self, antwort: AntwortAttrappe) -> None:
        """Nimmt die Antwort, die jedes `get` liefern soll."""
        self._antwort: AntwortAttrappe = antwort
        self.aufrufe:  list[str]       = []

    def get(self, url: str) -> AntwortAttrappe:
        """Schreibt den Aufruf mit und gibt die vorbereitete Antwort."""
        self.aufrufe.append(url)
        return self._antwort


class TestGleichstand(unittest.TestCase):
    """Der Fall, in dem nichts zu melden ist."""

    def test_unveraenderter_endpunkt_meldet_nichts(self) -> None:
        with patch.object(watch, "OPENROUTER_PRICE_INPUT_PER_M", EINGANG), \
             patch.object(watch, "OPENROUTER_PRICE_OUTPUT_PER_M", AUSGANG), \
             patch.object(watch, "OPENROUTER_NUM_CTX", FENSTER), \
             patch.object(watch, "OPENROUTER_QUANTISIERUNG", "fp8"):
            self.assertEqual(watch.compare(_endpunkt()), [])


class TestAbweichungen(unittest.TestCase):
    """Jede Sorte Abweichung einzeln."""

    def setUp(self) -> None:
        """Setzt die Konfiguration auf den Stand vom 05.09.2026."""
        self._patches = [
            patch.object(watch, "OPENROUTER_PRICE_INPUT_PER_M", EINGANG),
            patch.object(watch, "OPENROUTER_PRICE_OUTPUT_PER_M", AUSGANG),
            patch.object(watch, "OPENROUTER_NUM_CTX", FENSTER),
            patch.object(watch, "OPENROUTER_QUANTISIERUNG", "fp8"),
        ]
        for p in self._patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in self._patches])

    def test_rueckkehr_zum_listenpreis_wird_gemeldet(self) -> None:
        """$0,14 statt $0,04998 — das Ende des Rabatts, wie es aussaehe."""
        befunde = watch.compare(_endpunkt(prompt="0.00000014", discount=None))

        self.assertTrue(any("Eingangspreis gestiegen" in b for b in befunde))
        self.assertTrue(any("Faktor 2.80" in b for b in befunde))

    def test_verschwundener_rabatt_wird_auch_ohne_preissprung_gemeldet(self) -> None:
        """Der Rabatt kann fallen, bevor der Preis es zeigt."""
        befunde = watch.compare(_endpunkt(discount=None))

        self.assertEqual(len(befunde), 1)
        self.assertIn("Rabatt ist fort", befunde[0])

    def test_gesunkener_preis_wird_ebenfalls_gemeldet(self) -> None:
        """Auch eine Verbesserung ist eine Abweichung von der Buchfuehrung."""
        befunde = watch.compare(_endpunkt(completion="0.00000005"))

        self.assertTrue(any("Ausgangspreis gesunken" in b for b in befunde))

    def test_geaenderte_quantisierung_wird_gemeldet(self) -> None:
        """fp4 statt fp8 ist ein anderes Modell, nicht ein anderer Preis."""
        befunde = watch.compare(_endpunkt(quant="fp4"))

        self.assertTrue(any("Quantisierung geaendert" in b for b in befunde))

    def test_geaendertes_kontextfenster_wird_gemeldet(self) -> None:
        befunde = watch.compare(_endpunkt(context=262_144))

        self.assertTrue(any("Kontextfenster geaendert" in b for b in befunde))

    def test_verlorenes_response_format_wird_gemeldet(self) -> None:
        """Ohne `response_format` ist `expect_json` wieder eine Bitte."""
        befunde = watch.compare(_endpunkt(parameter=["temperature", "max_tokens"]))

        self.assertTrue(any("response_format" in b for b in befunde))

    def test_fehlender_preis_ist_ein_befund_und_kein_absturz(self) -> None:
        endpunkt = _endpunkt()
        del endpunkt["pricing"]["prompt"]

        befunde = watch.compare(endpunkt)

        self.assertTrue(any("Eingangspreis fehlt" in b for b in befunde))


class TestAnbieterwahl(unittest.TestCase):
    """Welchen Endpunkt der Waechter prueft."""

    def test_der_konfigurierte_anbieter_wird_gefunden(self) -> None:
        endpunkte = [_endpunkt(tag="relace/fp4", quant="fp4"), _endpunkt()]

        self.assertEqual(
            watch.pick_provider(endpunkte, "baidu", "fp8")["tag"], "baidu/fp8",
        )

    def test_verschwundener_anbieter_wird_laut_und_nennt_die_vorhandenen(self) -> None:
        """Mit abgeschaltetem Rueckfall antwortet der Server dann gar nicht."""
        endpunkte = [_endpunkt(tag="relace/fp4", quant="fp4")]

        with self.assertRaises(RuntimeError) as gefangen:
            watch.pick_provider(endpunkte, "baidu", "fp8")

        self.assertIn("baidu", str(gefangen.exception))
        self.assertIn("relace/fp4", str(gefangen.exception))

    def test_mehrdeutiger_anbieter_wird_laut(self) -> None:
        """Zwei Endpunkte, eine Konfiguration — sie sagt nicht welcher."""
        endpunkte = [_endpunkt(), _endpunkt(context=262_144)]

        with self.assertRaises(RuntimeError):
            watch.pick_provider(endpunkte, "baidu", "fp8")

    def test_quantisierung_trennt_zwei_endpunkte_desselben_anbieters(self) -> None:
        endpunkte = [_endpunkt(), _endpunkt(tag="baidu/fp4", quant="fp4")]

        self.assertEqual(
            watch.pick_provider(endpunkte, "baidu", "fp4")["quantization"], "fp4",
        )


class TestAbruf(unittest.TestCase):
    """Der Weg zur Schnittstelle."""

    def test_endpunktliste_wird_gelesen(self) -> None:
        client = ClientAttrappe(AntwortAttrappe(200, {"data": {"endpoints": [_endpunkt()]}}))

        endpunkte = watch.fetch_endpoints(client, "anbieter/modell")

        self.assertEqual(len(endpunkte), 1)
        self.assertIn("anbieter/modell", client.aufrufe[0])

    def test_http_fehler_wird_laut(self) -> None:
        client = ClientAttrappe(AntwortAttrappe(404, {}, text="not found"))

        with self.assertRaises(RuntimeError):
            watch.fetch_endpoints(client, "anbieter/modell")

    def test_rumpf_ohne_endpunktliste_wird_laut(self) -> None:
        """Eine leere Liste hiesse *keine Anbieter* — das ist etwas anderes."""
        client = ClientAttrappe(AntwortAttrappe(200, {"data": {}}))

        with self.assertRaises(TypeError):
            watch.fetch_endpoints(client, "anbieter/modell")

    def test_ohne_modell_id_wird_laut(self) -> None:
        client = ClientAttrappe(AntwortAttrappe(200, {"data": {"endpoints": []}}))

        with self.assertRaises(ValueError):
            watch.fetch_endpoints(client, "")


if __name__ == "__main__":
    unittest.main()
