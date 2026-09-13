"""Zeugen: Scheibe 11 liest zurueck — gespeicherte Eigenschaften im Angebot des Aufloesers.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 11. Ablegen allein
aendert kein Gespraech. Der Rueckweg ist der Frame-Aufloeser (Scheibe 6): Er
bekommt die aktiven, gespeicherten Werte der akuten Objekte mit offenen
Eigenschaften als eigene Quelle **vor** dem Pool angeboten und urteilt wie
bisher, ob ein Eintrag genau eine offene Eigenschaft beantwortet. So kehrt ein
Wert zurueck, den die Blase verloren hat — nach vier Stunden Verfall, nach
einem Themenwechsel, oder weil das Modell ihn beim Fortschreiben vergass.

Zeugen dieser Datei:
  * wer angeboten bekommt (akut, offene Eigenschaft) und was (nicht schon
    gedeckt, gekappt),
  * die Nummerierung, wenn die gespeicherten Eintraege vor den Pool treten,
  * die Verdrahtung in `_derive`: der Aufloeser sieht das Angebot, und eine
    Deckung traegt die Quelle `eigenschaft`,
  * das Herkunftslabel, das der Verfasser hoert,
  * die Prompt-Regel, dass ein fortgefuehrter Wert woertlich bleibt.
"""

import unittest
from unittest.mock import patch

from graph.nodes import sachlage as sachlage_mod
from graph.nodes import sachlage_resolver as resolver_mod
from graph.nodes.sachlage import SACHLAGE_PROMPT, _derive
from graph.nodes.sachlage_resolver import (
    SOURCE_LABELS,
    SOURCE_PROPERTIES,
    MemoryHit,
    combine_offer,
    property_hits,
)

STORED: list[dict] = [
    {"id": 12, "objekt_id": 3, "name": "Vela Pulsar", "eigenschaft": "Rotationsperiode",
     "wert": "89 Millisekunden", "sprecher": "nova", "turn_id": "alt"},
    {"id": 13, "objekt_id": 3, "name": "Vela Pulsar", "eigenschaft": "Entfernung",
     "wert": "rund 900 Lichtjahre", "sprecher": None, "turn_id": "alt"},
]


def _artifact(**objekt: object) -> dict:
    basis: dict = {"name": "Vela Pulsar", "akut": True,
                   "gedeckt": {"Entfernung": "rund 900 Lichtjahre"},
                   "offen": ["Rotationsperiode"]}
    basis.update(objekt)
    return {"thema": "Pulsar", "gegenstand": "Der Vela-Pulsar", "nutzerziel": "wissen",
            "ausdrucksweise": "fragend", "objekte": [basis]}


class PropertyHitsTest(unittest.TestCase):
    def test_an_acute_object_with_open_properties_gets_its_stored_values(self) -> None:
        with patch.object(resolver_mod, "active_properties", return_value=STORED) as lesen:
            hits = property_hits(_artifact(), "u", "c")
        self.assertEqual(lesen.call_args.args[1:4], ("u", "c", ["vela pulsar"]))
        self.assertEqual(hits, [(SOURCE_PROPERTIES, "sachlage_eigenschaft#12",
                                 "Vela Pulsar — Rotationsperiode: 89 Millisekunden",
                                 "89 Millisekunden")])

    def test_a_latent_object_gets_nothing(self) -> None:
        with patch.object(resolver_mod, "active_properties", return_value=STORED) as lesen:
            self.assertEqual(property_hits(_artifact(akut=False, offen=[]), "u", "c"), [])
        lesen.assert_not_called()

    def test_an_object_without_open_properties_gets_nothing(self) -> None:
        with patch.object(resolver_mod, "active_properties", return_value=STORED) as lesen:
            self.assertEqual(property_hits(_artifact(offen=[]), "u", "c"), [])
        lesen.assert_not_called()

    def test_without_a_pair_nothing_is_read(self) -> None:
        with patch.object(resolver_mod, "active_properties") as lesen:
            self.assertEqual(property_hits(_artifact(), "", "c"), [])
        lesen.assert_not_called()


class CombineOfferTest(unittest.TestCase):
    def test_stored_values_come_first_and_everything_is_renumbered(self) -> None:
        pool = [MemoryHit("G1", "kzg", "kognition", "Pulsare drehen schnell")]
        stored = [(SOURCE_PROPERTIES, "sachlage_eigenschaft#12", "Vela Pulsar — x: y")]
        combined = combine_offer(stored, pool)
        self.assertEqual([(h.key, h.source) for h in combined],
                         [("G1", SOURCE_PROPERTIES), ("G2", "kzg")])

    def test_no_stored_values_leave_the_pool_unchanged(self) -> None:
        pool = [MemoryHit("G1", "kzg", "kognition", "Pulsare drehen schnell")]
        self.assertEqual(combine_offer([], pool), pool)


class DeriveOffersStoredValuesTest(unittest.TestCase):
    """Die Verdrahtung: der Aufloeser bekommt das Gespeicherte, die Deckung traegt die Quelle."""

    def test_a_stored_value_covers_the_open_property(self) -> None:
        artefakt = _artifact()

        class _Antwort:
            parsed = artefakt

        # Der Aufloeser umschreibt — `[gemessen 13.09.2026]` »Die
        # Rotationsperiode betraegt 33 Millisekunden.« wurde als Abloesung des
        # gespeicherten »33 Millisekunden« abgelegt. Der Wert bleibt woertlich.
        claims = {"Vela Pulsar": {"Rotationsperiode": {
            "eintrag": "G1", "inhalt": "Die Periode betraegt 89 Millisekunden."}}}
        with patch.object(sachlage_mod.model_service.chat, "submit_sync", return_value=_Antwort()), \
             patch.object(resolver_mod, "active_properties", return_value=STORED), \
             patch.object(sachlage_mod, "resolve_open_properties", return_value=claims) as aufloeser, \
             patch.object(sachlage_mod, "assess_plausibility", return_value={}), \
             patch.object(sachlage_mod, "research_open_property", side_effect=lambda a: a):
            ergebnis = _derive(None, [], "Wie schnell dreht er sich?", pair=("u", "c"))
        angebot: list[MemoryHit] = aufloeser.call_args.args[1]
        self.assertEqual(angebot[0].source, SOURCE_PROPERTIES)
        objekt = ergebnis["objekte"][0]
        self.assertEqual(objekt["gedeckt"]["Rotationsperiode"], "89 Millisekunden")
        self.assertEqual(objekt["quellen"]["Rotationsperiode"]["quelle"], SOURCE_PROPERTIES)

    def test_without_a_pair_the_offer_is_the_pool(self) -> None:
        artefakt = _artifact()

        class _Antwort:
            parsed = artefakt

        with patch.object(sachlage_mod.model_service.chat, "submit_sync", return_value=_Antwort()), \
             patch.object(resolver_mod, "active_properties") as lesen, \
             patch.object(sachlage_mod, "resolve_open_properties", return_value={}), \
             patch.object(sachlage_mod, "assess_plausibility", return_value={}), \
             patch.object(sachlage_mod, "research_open_property", side_effect=lambda a: a):
            _derive(None, [], "Wie schnell dreht er sich?")
        lesen.assert_not_called()


class TheAuthorHearsTheOriginTest(unittest.TestCase):
    def test_the_label_names_earlier_conversations_about_the_thing(self) -> None:
        self.assertIn("frueheren Gespraechen", SOURCE_LABELS[SOURCE_PROPERTIES])


class TheValueStaysLiteralTest(unittest.TestCase):
    def test_the_prompt_keeps_a_carried_value_literally(self) -> None:
        self.assertIn("behaelt ihren Wert WOERTLICH", SACHLAGE_PROMPT)


if __name__ == "__main__":
    unittest.main()
