"""Tests: Eine relative Zeitangabe gilt dem Tag, an dem sie fiel — Scheibe 12 D.

Fund vom 17.09.2026: 17 von 29 Zeitwerten akuter Objekte waren relativ
(*"morgen um 10"*); die Fortschreibung behaelt sie woertlich, die Lage verfaellt
erst nach 4 Stunden. Seit der Objektbezug Ziel und Zeit in die Klassifikation
traegt, wuerde eine Lage von vor Mitternacht auf den falschen Tag aufgeloest.

Zeugen dieser Datei:
  * **Aufgeloest, wenn sie faellt** — eine neue relative Angabe bekommt ihre
    Schwester `(aufgeloest)` mit dem Datum; der Wortlaut bleibt.
  * **Uebernommen, nicht neu gerechnet** — derselbe Wert in der Fortschreibung
    behaelt die damalige Aufloesung, auch wenn heute ein anderer Tag waere.
  * **Kein Raten** — eine absolute Angabe und eine Nicht-Zeit bleiben ohne.
  * **Die Zustimmung nimmt das Datum** — `consent_fields` bevorzugt die
    Aufloesung vor dem relativen Wort.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.object_nearness import consent_fields
from graph.nodes.sachlage import RESOLVED_SUFFIX, _derive, carry_resolved_dates
from utils.zeitparser import zeit_parsen_vektor


def _lage(gedeckt: dict) -> dict:
    return {"objekte": [{"name": "Abholung", "klasse": "vorgang", "akut": True, "gedeckt": dict(gedeckt)}]}


class AufloesungTest(unittest.TestCase):

    def test_eine_neue_relative_angabe_wird_aufgeloest_und_bleibt_wortlaut(self) -> None:
        erwartet = zeit_parsen_vektor("morgen um 10").datum.strftime("%d.%m.%Y")
        gedeckt = carry_resolved_dates(_lage({"Tag": "morgen um 10"}), None)["objekte"][0]["gedeckt"]
        self.assertEqual(gedeckt["Tag"], "morgen um 10")
        self.assertEqual(gedeckt["Tag" + RESOLVED_SUFFIX], erwartet)

    def test_die_fortschreibung_behaelt_die_damalige_aufloesung(self) -> None:
        vorige = _lage({"Tag": "morgen um 10", "Tag" + RESOLVED_SUFFIX: "01.01.2030"})
        jetzt = _lage({"Tag": "morgen um 10"})       # das Modell liess die Schwester weg
        gedeckt = carry_resolved_dates(jetzt, vorige)["objekte"][0]["gedeckt"]
        self.assertEqual(gedeckt["Tag" + RESOLVED_SUFFIX], "01.01.2030")

    def test_ein_geaenderter_wert_wird_neu_aufgeloest(self) -> None:
        vorige = _lage({"Tag": "morgen", "Tag" + RESOLVED_SUFFIX: "01.01.2030"})
        gedeckt = carry_resolved_dates(_lage({"Tag": "uebermorgen"}), vorige)["objekte"][0]["gedeckt"]
        self.assertNotEqual(gedeckt["Tag" + RESOLVED_SUFFIX], "01.01.2030")

    def test_absolute_angaben_und_nicht_zeiten_bleiben_ohne(self) -> None:
        gedeckt = carry_resolved_dates(_lage({"Tag": "24.09.2026", "Ort": "morgen im Park"}), None)["objekte"][0]["gedeckt"]
        self.assertEqual(set(gedeckt), {"Tag", "Ort"})


class VerdrahtungTest(unittest.TestCase):
    """Die Aufloesung laeuft im echten Rechenweg der Sachlage, nicht nur als Funktion."""

    def test_derive_loest_die_relative_angabe_auf(self) -> None:
        artefakt = {"thema": "Abholung", "gegenstand": "Die Schwester abholen", "nutzerziel": "planen",
                    "ausdrucksweise": "erzaehlend", "herkunft": "frisch",
                    "objekte": [{"name": "Abholung", "klasse": "vorgang", "akut": True,
                                 "gedeckt": {"Tag": "morgen"}, "offen": []}]}
        with patch("graph.nodes.sachlage.model_service") as ms, \
             patch("graph.nodes.sachlage.assess_plausibility", return_value={}), \
             patch("graph.nodes.sachlage.research_open_property", side_effect=lambda a: a):
            ms.chat.submit_sync.return_value.parsed = artefakt
            ergebnis = _derive(None, [], "Morgen hole ich meine Schwester ab.")
        self.assertIn("Tag" + RESOLVED_SUFFIX, ergebnis["objekte"][0]["gedeckt"])


class ZustimmungTest(unittest.TestCase):

    def test_die_zustimmung_nimmt_das_aufgeloeste_datum(self) -> None:
        bezug = [{"name": "Abholung", "klasse": "vorgang",
                  "gedeckt": {"Tag": "morgen", "Tag" + RESOLVED_SUFFIX: "19.09.2026", "Uhrzeit": "10 Uhr"}}]
        self.assertEqual(consent_fields(bezug), ("Abholung", "19.09.2026 10 Uhr"))


if __name__ == "__main__":
    unittest.main()
