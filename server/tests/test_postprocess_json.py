"""Tests: Gueltiges JSON wird nicht repariert, kaputtes weiterhin.

Anlass (16.09.2026): Die Wiederholungskappung hielt eine Einrueckung von 25
Leerzeichen fuer eine Endlosschleife und schnitt eine vollstaendige, gueltige
Sachlage ab; `json.loads` las den Rohtext fehlerfrei. Getroffen hat es jeden
Aufruf mit erzwungenem JSON (Chat- und Hintergrund-Worker).

Zeugen:
  * **Der Fall selbst**, in der Form, in der das Modell ihn lieferte:
    ausgerichtete Zuordnungen ueber mehrere Zeilen.
  * **Der Zwilling:** Eine echte Endloswiederholung und ein am Token-Limit
    abgeschnittenes Objekt werden weiter gerettet — die Reparatur ist nicht
    abgeschaltet, sie ist nachrangig.
  * **Fail loud:** Eine Reparatur steht im Log; unheilbarer Text wirft.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest

from services.postprocess import parse_json_strict

EINGERUECKT = """{"thema": "Regenjacke",
  "objekte": [
    {
      "name": "Regenjacke",
      "traeger": {"Stil": "nutzer",
                   "Groesse": "nutzer",
                   "Preis": "nachschlagen"},
      "kritikalitaet": {"Stil": "unkritisch",
                         "Groesse": "kritisch",
                         "Preis": "unkritisch"},
      "sprecher": {}
    },
    {
      "name": "Ausflug",
      "akut": false
    }
  ]}"""


class GueltigBleibtUnberuehrtTest(unittest.TestCase):

    def test_ausgerichtete_einrueckung_wird_nicht_gekappt(self) -> None:
        self.assertEqual(json.loads(EINGERUECKT), parse_json_strict(EINGERUECKT))
        self.assertEqual([o["name"] for o in parse_json_strict(EINGERUECKT)["objekte"]],
                         ["Regenjacke", "Ausflug"])

    def test_gueltiges_json_mit_wiederholtem_inhalt_bleibt_ganz(self) -> None:
        text = json.dumps({"liste": ["nutzer", "nutzer", "nutzer", "nutzer"], "ende": 1})
        self.assertEqual(parse_json_strict(text), {"liste": ["nutzer"] * 4, "ende": 1})

    def test_codeblock_huelle_wird_weiter_entfernt(self) -> None:
        self.assertEqual(parse_json_strict('```json\n{"a": 1}\n```'), {"a": 1})

    def test_gueltig_schreibt_keine_reparaturmeldung(self) -> None:
        with self.assertNoLogs("ki_server.postprocess", level="WARNING"):
            parse_json_strict(EINGERUECKT)


class KaputtWirdWeiterGerettetTest(unittest.TestCase):

    def test_abgeschnittenes_objekt_wird_geschlossen(self) -> None:
        with self.assertLogs("ki_server.postprocess", level="WARNING"):
            self.assertEqual(parse_json_strict('{"a": {"b": "c"'), {"a": {"b": "c"}})

    def test_endloswiederholung_wird_gekappt(self) -> None:
        text = '{"satz": "' + "und dann und dann " * 20
        with self.assertLogs("ki_server.postprocess", level="WARNING"):
            ergebnis = parse_json_strict(text)
        self.assertLess(len(ergebnis["satz"]), 40)

    def test_unheilbarer_text_wirft(self) -> None:
        with self.assertRaises(json.JSONDecodeError):
            parse_json_strict("kein json, nirgends")


if __name__ == "__main__":
    unittest.main()
