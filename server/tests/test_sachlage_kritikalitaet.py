"""Zeugen fuer Scheibe 10: das Gewicht einer Luecke.

Der Traeger (Scheibe 8) sagt, **wer** eine offene Eigenschaft kennen kann.
Er sagt nicht, **was es kostet**, wenn niemand sie nennt — und genau diese
Unterscheidung fehlte: Solange die erste `nutzer`-Eigenschaft in `offen` den
Rueckfrage-Gegenstand bekam, entschied die Reihenfolge einer nach Wichtigkeit
sortierten Liste darueber, ob Nova nach dem Tragenden oder nach dem Netten
fragt. Wichtigkeit ist aber nicht dasselbe wie *ohne sie muss die Antwort
raten*.

Geprueft wird die Erhebung gegen den Kanon, das Erben aus der vorigen Blase,
die Vorwahl der kritischen Luecke und ihre Zeile im Block. Ein fehlender Wert
gilt als `unkritisch` — das Verhalten vor der Scheibe bleibt damit die
Vorgabe, und die Scheibe kann nichts verschlechtern, was sie nicht erhoben hat.
"""

import ast
import unittest
from pathlib import Path

from graph.nodes.sachlage import (
    GEGENSTAND_AUS_BLASE,
    KRITIKALITAET_KANON,
    KRITISCH,
    UNKRITISCH,
    _normalize_criticality,
    carry_criticality,
    question_target_origin,
    sachlage_block,
)

SACHLAGE = Path(__file__).resolve().parents[1] / "graph" / "nodes" / "sachlage.py"


def _objekt(offen: list[str], traeger: dict, kritikalitaet: dict, akut: bool = True) -> dict:
    return {
        "name": "Gartenteich",
        "klasse": "vorgang",
        "akut": akut,
        "gedeckt": {},
        "offen": offen,
        "traeger": traeger,
        "kritikalitaet": kritikalitaet,
    }


def _sachlage(objekt: dict) -> dict:
    return {"thema": "Gartenteich", "gegenstand": "", "objekte": [objekt]}


class CriticalityIsHeldAgainstTheCanonTest(unittest.TestCase):
    """Die Erhebung: nur Kanon-Werte an Eigenschaften, die in `offen` stehen."""

    def test_canon_holds_two_values(self) -> None:
        self.assertEqual(KRITIKALITAET_KANON, frozenset({KRITISCH, UNKRITISCH}))

    def test_known_values_pass(self) -> None:
        objekt = _objekt(["Tiefe", "Bepflanzung"],
                         {}, {"Tiefe": "kritisch", "Bepflanzung": "unkritisch"})
        self.assertEqual(_normalize_criticality(objekt),
                         {"Tiefe": KRITISCH, "Bepflanzung": UNKRITISCH})

    def test_an_unknown_value_is_dropped(self) -> None:
        objekt = _objekt(["Tiefe"], {}, {"Tiefe": "sehr wichtig"})
        self.assertEqual(_normalize_criticality(objekt), {})

    def test_a_property_not_in_offen_is_dropped(self) -> None:
        objekt = _objekt(["Tiefe"], {}, {"Farbe": "kritisch"})
        self.assertEqual(_normalize_criticality(objekt), {})

    def test_a_non_dict_is_dropped(self) -> None:
        objekt = _objekt(["Tiefe"], {}, {})
        objekt["kritikalitaet"] = ["kritisch"]
        self.assertEqual(_normalize_criticality(objekt), {})

    def test_a_missing_field_stays_empty(self) -> None:
        objekt = _objekt(["Tiefe"], {}, {})
        del objekt["kritikalitaet"]
        self.assertEqual(_normalize_criticality(objekt), {})


class CriticalityIsInheritedTest(unittest.TestCase):
    """Das Erben: der Fortfuehrungsfall, in dem das Modell das Feld weglaesst."""

    def test_a_missing_weight_is_inherited(self) -> None:
        vorige = _sachlage(_objekt(["Tiefe"], {}, {"Tiefe": KRITISCH}))
        neu = _sachlage(_objekt(["Tiefe"], {}, {}))
        carry_criticality(neu, vorige)
        self.assertEqual(neu["objekte"][0]["kritikalitaet"], {"Tiefe": KRITISCH})

    def test_an_existing_weight_is_not_overwritten(self) -> None:
        vorige = _sachlage(_objekt(["Tiefe"], {}, {"Tiefe": KRITISCH}))
        neu = _sachlage(_objekt(["Tiefe"], {}, {"Tiefe": UNKRITISCH}))
        carry_criticality(neu, vorige)
        self.assertEqual(neu["objekte"][0]["kritikalitaet"], {"Tiefe": UNKRITISCH})

    def test_a_latent_object_inherits_nothing(self) -> None:
        vorige = _sachlage(_objekt(["Tiefe"], {}, {"Tiefe": KRITISCH}))
        neu = _sachlage(_objekt(["Tiefe"], {}, {}, akut=False))
        carry_criticality(neu, vorige)
        self.assertEqual(neu["objekte"][0]["kritikalitaet"], {})

    def test_without_a_previous_bubble_nothing_changes(self) -> None:
        neu = _sachlage(_objekt(["Tiefe"], {}, {}))
        carry_criticality(neu, None)
        self.assertEqual(neu["objekte"][0]["kritikalitaet"], {})


class TheCriticalGapWinsTheQuestionTest(unittest.TestCase):
    """Die Wirkung: die kritische Luecke schlaegt die Reihenfolge in `offen`."""

    def test_the_critical_gap_is_chosen_over_the_first_one(self) -> None:
        objekt = _objekt(
            ["Bepflanzung", "Tiefe"],
            {"Bepflanzung": "nutzer", "Tiefe": "nutzer"},
            {"Bepflanzung": UNKRITISCH, "Tiefe": KRITISCH},
        )
        gegenstand, herkunft = question_target_origin(_sachlage(objekt))
        self.assertIn("Tiefe", gegenstand)
        self.assertEqual(herkunft, GEGENSTAND_AUS_BLASE)

    def test_without_weights_the_order_still_decides(self) -> None:
        """Ohne erhobene Gewichte bleibt das Verhalten vor der Scheibe."""
        objekt = _objekt(["Bepflanzung", "Tiefe"],
                         {"Bepflanzung": "nutzer", "Tiefe": "nutzer"}, {})
        gegenstand, _ = question_target_origin(_sachlage(objekt))
        self.assertIn("Bepflanzung", gegenstand)

    def test_a_critical_gap_the_world_knows_is_no_question(self) -> None:
        """Kritisch macht keine Rueckfrage aus etwas, das Nova selbst weiss."""
        objekt = _objekt(
            ["Wassertemperatur", "Tiefe"],
            {"Wassertemperatur": "welt", "Tiefe": "nutzer"},
            {"Wassertemperatur": KRITISCH, "Tiefe": UNKRITISCH},
        )
        gegenstand, _ = question_target_origin(_sachlage(objekt))
        self.assertIn("Tiefe", gegenstand)

    def test_all_uncritical_keeps_the_first(self) -> None:
        objekt = _objekt(["Bepflanzung", "Tiefe"],
                         {"Bepflanzung": "nutzer", "Tiefe": "nutzer"},
                         {"Bepflanzung": UNKRITISCH, "Tiefe": UNKRITISCH})
        gegenstand, _ = question_target_origin(_sachlage(objekt))
        self.assertIn("Bepflanzung", gegenstand)


class TheBlockNamesTheCriticalGapTest(unittest.TestCase):
    """Der Block: der Verfasser erfaehrt, was zuerst zu klaeren ist."""

    def test_the_line_appears_for_a_critical_user_gap(self) -> None:
        block = sachlage_block(_sachlage(_objekt(
            ["Tiefe"], {"Tiefe": "nutzer"}, {"Tiefe": KRITISCH})))
        self.assertIn("Tiefe", block)
        self.assertIn("raten", block)

    def test_no_line_without_a_critical_gap(self) -> None:
        block = sachlage_block(_sachlage(_objekt(
            ["Tiefe"], {"Tiefe": "nutzer"}, {"Tiefe": UNKRITISCH})))
        self.assertNotIn("muesste", block)

    def test_no_line_when_the_world_knows_it(self) -> None:
        block = sachlage_block(_sachlage(_objekt(
            ["Wassertemperatur"], {"Wassertemperatur": "welt"},
            {"Wassertemperatur": KRITISCH})))
        self.assertNotIn("raten", block)


class TheSearchTakesTheCriticalGapTest(unittest.TestCase):
    """Der zweite Leser derselben Groesse — gefunden von der zweiten Kontrolle.

    Es gibt **eine** Suche je Turn. Bis zu dieser Scheibe entschied dort die
    Reihenfolge in `offen`, welche `nachschlagen`-Luecke sie bekommt — genau
    der Fall, den die Scheibe bei der Rueckfrage behebt. Der Bau hatte nur an
    die Rueckfrage gedacht.
    """

    @staticmethod
    def _artefakt(kritikalitaet: dict) -> dict:
        return {"objekte": [{
            "name": "Pulsar", "akut": True, "offen": ["Alter", "Rotationsfrequenz"],
            "traeger": {"Alter": "nachschlagen", "Rotationsfrequenz": "nachschlagen"},
            "kritikalitaet": kritikalitaet,
        }]}

    def test_the_critical_gap_is_searched_first(self) -> None:
        from graph.nodes.sachlage_research import lookup_target
        ziel = lookup_target(self._artefakt(
            {"Alter": UNKRITISCH, "Rotationsfrequenz": KRITISCH}))
        self.assertEqual(ziel[1], "Rotationsfrequenz")

    def test_without_weights_the_order_still_decides(self) -> None:
        from graph.nodes.sachlage_research import lookup_target
        self.assertEqual(lookup_target(self._artefakt({}))[1], "Alter")

    def test_a_critical_user_gap_is_not_searched(self) -> None:
        """Kritisch allein reicht nicht — gesucht wird nur, was nachzuschlagen ist."""
        from graph.nodes.sachlage_research import lookup_target
        artefakt = self._artefakt({"Alter": KRITISCH})
        artefakt["objekte"][0]["traeger"]["Alter"] = "nutzer"
        self.assertEqual(lookup_target(artefakt)[1], "Rotationsfrequenz")


class TheInheritanceIsWiredIntoTheFlowTest(unittest.TestCase):
    """Die Verdrahtung — der Zeuge, den die Gegenprobe erzwungen hat.

    Die Gegenprobe zu dieser Scheibe nahm den Aufruf `carry_criticality` aus
    dem Ablauf und **alles blieb gruen**: Die uebrigen Zeugen rufen die
    Funktion selbst und pruefen damit den Bauteil, nicht seinen Einbau.
    Dieselbe Luecke trugen die Bestandszeugen fuer `carry_holders` und
    `carry_speakers`, deshalb prueft dieser Zeuge alle drei.
    """

    def setUp(self) -> None:
        baum = ast.parse(SACHLAGE.read_text(encoding="utf-8"))
        self.derive = next(
            k for k in ast.walk(baum)
            if isinstance(k, ast.FunctionDef) and k.name == "_derive"
        )
        self.gerufen = {
            k.func.id for k in ast.walk(self.derive)
            if isinstance(k, ast.Call) and isinstance(k.func, ast.Name)
        }

    def test_the_flow_inherits_criticality(self) -> None:
        self.assertIn("carry_criticality", self.gerufen)

    def test_the_flow_inherits_holders_and_speakers(self) -> None:
        """Die Nachbarn derselben Klasse — sie waren ebenso ungedeckt."""
        self.assertIn("carry_holders", self.gerufen)
        self.assertIn("carry_speakers", self.gerufen)


if __name__ == "__main__":
    unittest.main()
