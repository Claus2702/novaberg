"""Zeugen: die Form des Sachlage-Artefakts, bevor es in den State darf.

Anlass (12.09.2026, 18:55 UTC): Das Modell lieferte `gedeckt` als **Liste**
von Eigenschaftsnamen. `_validate_artifact` pruefte die Felder nicht, eine
Lesestelle rief `.items()` und riss den Turn ab (`LAGE-FORMPRUEFUNG-UNVOLLSTAENDIG`).

Die Regel des Eigentuemers (13.09.2026): **Eine Eigenschaft ist gedeckt, wenn
sie einen Wert hat. Ohne Wert ist sie offen.** Es wird nichts verworfen, was
eine Aussage traegt — ein Name ohne Wert wandert nach `offen`.

Gefahren wird durch `_validate_artifact` (der frische Parse) und durch
`sachlage_load` (die vorige Blase aus Redis), nicht durch die Helfer allein:
Die Verdrahtung ist der Defekt, wenn einer der beiden Wege die Form nicht
herstellt. Dazu die sechs Lesestellen, an denen die falsche Form am 12.09.
gemessen wurde, auf dem geprueften Artefakt.
"""

import json
import unittest
from unittest.mock import patch

from graph.nodes import sachlage as sachlage_mod
from graph.nodes.sachlage import _validate_artifact, sachlage_block, sachlage_load
from graph.nodes.sachlage_form import normalize_object_form
from graph.nodes.sachlage_plausibility import _render_objects
from graph.nodes.sachlage_resolver import apply_memory_coverage, carry_sources


def _artifact(**objekt: object) -> dict:
    """Ein Parse mit genau einem Objekt, wie ihn das Modell liefern koennte."""
    basis: dict = {"name": "Geburtstag", "klasse": "vorgang", "akut": True}
    basis.update(objekt)
    return {
        "thema": "Geburtstag", "gegenstand": "Ein anstehender Geburtstag",
        "nutzerziel": "vermutlich Planung", "ausdrucksweise": "erzaehlend",
        "objekte": [basis],
    }


def _object(artefakt: dict | None) -> dict:
    assert artefakt is not None, "das Artefakt wurde verworfen"
    return artefakt["objekte"][0]


class CoveredNeedsAValueTest(unittest.TestCase):
    """`gedeckt`: Eigenschaft mit Wert. Ohne Wert ist sie offen."""

    def test_a_dict_with_values_stays_covered(self) -> None:
        objekt = _object(_validate_artifact(_artifact(
            gedeckt={"anlass": "Tochter wird zehn"}, offen=["wann"],
        )))
        self.assertEqual(objekt["gedeckt"], {"anlass": "Tochter wird zehn"})
        self.assertEqual(objekt["offen"], ["wann"])

    def test_a_list_of_names_is_open_not_covered(self) -> None:
        """Der Fall vom 12.09.2026: Namen ohne Werte."""
        objekt = _object(_validate_artifact(_artifact(
            gedeckt=["anlass", "wann"], offen=["geschenk"],
        )))
        self.assertEqual(objekt["gedeckt"], {})
        self.assertEqual(objekt["offen"], ["geschenk", "anlass", "wann"])

    def test_an_empty_value_is_open(self) -> None:
        objekt = _object(_validate_artifact(_artifact(
            gedeckt={"anlass": "Tochter wird zehn", "wann": "  "}, offen=[],
        )))
        self.assertEqual(objekt["gedeckt"], {"anlass": "Tochter wird zehn"})
        self.assertEqual(objekt["offen"], ["wann"])

    def test_a_structured_value_is_no_value(self) -> None:
        objekt = _object(_validate_artifact(_artifact(
            gedeckt={"wer": ["Anna", "Ben"], "wann": None}, offen=[],
        )))
        self.assertEqual(objekt["gedeckt"], {})
        self.assertEqual(objekt["offen"], ["wer", "wann"])

    def test_a_number_is_a_value(self) -> None:
        objekt = _object(_validate_artifact(_artifact(gedeckt={"alter": 10}, offen=[])))
        self.assertEqual(objekt["gedeckt"], {"alter": "10"})

    def test_a_name_already_open_is_not_doubled(self) -> None:
        objekt = _object(_validate_artifact(_artifact(
            gedeckt=["Wann"], offen=["wann"],
        )))
        self.assertEqual(objekt["offen"], ["wann"])

    def test_a_latent_object_gets_no_open_properties(self) -> None:
        """Die Smalltalk-Schranke gilt auch fuer Namen aus `gedeckt`."""
        objekt = _object(_validate_artifact(_artifact(
            akut=False, gedeckt=["anlass"], offen=[],
        )))
        self.assertEqual(objekt["gedeckt"], {})
        self.assertEqual(objekt["offen"], [])

    def test_missing_covered_is_an_empty_dict(self) -> None:
        objekt = _object(_validate_artifact(_artifact(offen=["wann"])))
        self.assertEqual(objekt["gedeckt"], {})


class OpenIsAListOfNamesTest(unittest.TestCase):
    """`offen`: eine Liste von Eigenschaftsnamen ohne Wert."""

    def test_a_dict_with_values_moves_to_covered(self) -> None:
        objekt = _object(_validate_artifact(_artifact(
            gedeckt={}, offen={"wann": "Samstag", "wer": ""},
        )))
        self.assertEqual(objekt["gedeckt"], {"wann": "Samstag"})
        self.assertEqual(objekt["offen"], ["wer"])

    def test_a_single_string_is_one_name(self) -> None:
        objekt = _object(_validate_artifact(_artifact(gedeckt={}, offen="wann")))
        self.assertEqual(objekt["offen"], ["wann"])

    def test_non_text_entries_and_duplicates_fall_out(self) -> None:
        objekt = _object(_validate_artifact(_artifact(
            gedeckt={}, offen=["wann", {"x": 1}, "", "Wann", 7],
        )))
        self.assertEqual(objekt["offen"], ["wann", "7"])

    def test_covered_wins_over_open(self) -> None:
        objekt = _object(_validate_artifact(_artifact(
            gedeckt={"wann": "Samstag"}, offen=["wann", "wer"],
        )))
        self.assertEqual(objekt["offen"], ["wer"])


class ObjectFieldsTest(unittest.TestCase):
    """Die uebrigen Felder eines Objekts und die Felder, die dem Server gehoeren."""

    def test_akut_as_text_is_read_as_bool(self) -> None:
        self.assertIs(_object(_validate_artifact(_artifact(akut="false")))["akut"], False)
        self.assertIs(_object(_validate_artifact(_artifact(akut="true")))["akut"], True)

    def test_akut_of_unknown_form_is_latent(self) -> None:
        self.assertIs(_object(_validate_artifact(_artifact(akut=["ja"])))["akut"], False)

    def test_server_owned_fields_from_the_model_are_removed(self) -> None:
        objekt = _object(_validate_artifact(_artifact(
            gedeckt={"anlass": "x"}, offen=[],
            quellen={"anlass": "erfunden"}, plausibilitaet="hoch", recherche=["x"],
        )))
        for feld in ("quellen", "plausibilitaet", "recherche"):
            self.assertNotIn(feld, objekt)

    def test_an_unknown_class_is_removed(self) -> None:
        objekt = _object(_validate_artifact(_artifact(klasse="Gegenstand")))
        self.assertNotIn("klasse", objekt)

    def test_a_head_field_that_is_not_text_rejects_the_artifact(self) -> None:
        artefakt = _artifact()
        artefakt["gegenstand"] = ["zwei", "Saetze"]
        self.assertIsNone(_validate_artifact(artefakt))

    def test_an_empty_name_rejects_the_artifact(self) -> None:
        self.assertIsNone(_validate_artifact(_artifact(name="  ")))

    def test_the_predecessor_keeps_its_server_fields(self) -> None:
        """Was der Server selbst schrieb, bleibt beim Laden stehen."""
        objekt: dict = {
            "name": "Geburtstag", "akut": True, "gedeckt": {"anlass": "x"}, "offen": [],
            "quellen": {"anlass": {"quelle": "kzg", "herkunft": "h", "eintrag": "G1"}},
        }
        normalize_object_form(objekt, from_model=False)
        self.assertIn("anlass", objekt["quellen"])

    def test_malformed_sources_of_the_predecessor_fall_out(self) -> None:
        objekt: dict = {
            "name": "Geburtstag", "akut": True, "gedeckt": {"anlass": "x"}, "offen": [],
            "quellen": {"anlass": "kein dict", "wann": {"quelle": "kzg"}},
        }
        normalize_object_form(objekt, from_model=False)
        self.assertEqual(list(objekt["quellen"]), [])


class ThePredecessorIsCheckedOnLoadTest(unittest.TestCase):
    """Die vorige Blase aus Redis ist eine externe Quelle (16_PERSISTENZ §6)."""

    def test_a_list_in_the_stored_bubble_is_repaired_on_load(self) -> None:
        gespeichert = _artifact(gedeckt=["anlass"], offen=["wann"])
        roh = {"json": json.dumps(gespeichert), "turn_zeit": str(9e12)}
        with patch.object(sachlage_mod, "redis_client") as redis, \
             patch.object(sachlage_mod.time, "time", return_value=9e12):
            redis.hgetall.return_value = roh
            vorige, verfallen = sachlage_load("u", "c")
        self.assertFalse(verfallen)
        self.assertEqual(vorige["objekte"][0]["gedeckt"], {})
        self.assertEqual(vorige["objekte"][0]["offen"], ["wann", "anlass"])


class TheReadersSurviveTheCaseOfTheTwelfthTest(unittest.TestCase):
    """Die Lesestellen, an denen die Liste am 12.09.2026 gemessen wurde."""

    def setUp(self) -> None:
        self.artefakt = _validate_artifact(_artifact(
            gedeckt=["anlass", "wann"], offen=["geschenk"],
        ))

    def test_plausibility_renders(self) -> None:
        self.assertIn("Geburtstag", _render_objects(self.artefakt))

    def test_memory_coverage_and_carry_run(self) -> None:
        ergebnis = carry_sources(apply_memory_coverage(self.artefakt, [], {}, None), None)
        self.assertEqual(ergebnis["objekte"][0]["gedeckt"], {})

    def test_the_block_renders(self) -> None:
        self.artefakt["herkunft"] = "frisch"
        self.assertIsInstance(sachlage_block(self.artefakt), str)


if __name__ == "__main__":
    unittest.main()
