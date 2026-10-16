"""Zeugen: keine Websuche der Sachlage zum eigenen Bestand des Nutzers.

Fragt der Nutzer nach seinen Terminen, Vorhaben oder Notizen, kennt das keine
Websuche. Die Sachlage-Recherche liefert dann keinen Treffer in den Block des
Verfassers, gleich welchen Traeger das Modell der Eigenschaft gibt — und das
Log sagt, dass sie deshalb unterblieb. Eine Frage nach Weltwissen wird weiter
nachgeschlagen.

Zeugen dieser Datei:
  * **`own_records_cue` erkennt die Frage nach dem eigenen Bestand** — an
    einem Wort des Bestands mit erster Person oder Besitz, an »steht … an«,
    »habe … vor«, »was ist bei mir los«, »wann … ich« und an einer Frage mit
    »ich« und Zeitbezug. Jede Form hat einen Zeugen.
  * **Die Zwillinge, Weltwissen bleibt Weltwissen:** ein »mir« als
    Empfaenger, ein Besitz ohne Wort des Bestands, »ich« im Hauptsatz und
    »wann« ohne »ich«, ein Bericht statt einer Frage, ein Nebensatz, ein
    »bei uns« am Wetter, »Terminator« ist kein Termin.
  * **`withhold_research` sucht nicht, laesst `recherche` leer und sagt es**
    — nur wenn eine Suche gelaufen waere.
  * **Die Verdrahtung in `_derive`**, mit der echten `research_open_property`
    und ersetzter Suchmaschine: die Terminfrage sucht nicht und der Block
    traegt kein »Nachgeschlagen«; die Planetariumsfrage sucht, und er traegt es.
  * Die Beispiele sind synthetisch.

Kein Netz: `web_search_manager.suchen` ist ersetzt.
Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from graph.nodes.sachlage import TRAEGER_NACHSCHLAGEN, TRAEGER_WELT, _derive, sachlage_block
from graph.nodes.sachlage_research import (
    _clause_cue,
    _is_question,
    _sentence_cue,
    own_records_cue,
    withhold_research,
)

_SEARCH: str = "graph.nodes.sachlage_research.web_search_manager.suchen"

_APPOINTMENTS_QUESTION: str = "Was habe ich diese Woche für Termine?"
_WORLD_QUESTION: str = "Wann öffnet das Planetarium?"


def _artifact(name: str, prop: str, holder: str) -> dict:
    """Ein Artefakt mit einem akuten Objekt und einer offenen Eigenschaft."""
    return {
        "thema": name, "gegenstand": f"Frage zu {name}",
        "nutzerziel": "eine Auskunft erhalten", "ausdrucksweise": "pruefend",
        "objekte": [{
            "name": name, "klasse": "vorgang", "akut": True,
            "gedeckt": {}, "offen": [prop], "traeger": {prop: holder},
        }],
    }


def _hits(name: str) -> list[dict]:
    """Treffer einer Suche, die den Objektnamen nennen — sie gingen sonst durch."""
    return [{"title": f"{name} Beispielseite", "url": "https://example.org/beispiel",
             "content": f"{name}: Beispielpunkt A, Donnerstag 19 Uhr"}]


class OwnRecordsCueTest(unittest.TestCase):
    """Wort des Bestands mit erster Person oder Besitz — eines allein reicht nicht."""

    def test_appointments_of_the_week_are_own_records(self) -> None:
        self.assertEqual(own_records_cue(_APPOINTMENTS_QUESTION), "Termine")

    def test_other_forms_of_own_records(self) -> None:
        for utterance in (
            "Was steht bei mir morgen an?",
            "Was habe ich am Freitag vor?",
            "Hab ich einen Arzttermin?",
            "Steht da was in meinem Kalender?",
            "Was hatte ich mir notiert?",
            "Mit wem bin ich verabredet?",
        ):
            with self.subTest(utterance=utterance):
                self.assertIsNotNone(own_records_cue(utterance))

    def test_world_knowledge_is_not_own_records(self) -> None:
        self.assertIsNone(own_records_cue(_WORLD_QUESTION))

    def test_cue_without_first_person_is_not_own_records(self) -> None:
        self.assertIsNone(own_records_cue("Wann sind die Termine der Bundesliga?"))

    def test_terminator_is_no_appointment(self) -> None:
        self.assertIsNone(own_records_cue("Ich mag Terminator, wann kam der raus?"))

    def test_non_text_raises(self) -> None:
        with self.assertRaises(TypeError):
            own_records_cue(None)  # type: ignore[arg-type]


class OwnDayIsRecognizedTest(unittest.TestCase):
    """Die Fragen nach dem eigenen Tag, auch ohne ein Wort des Kalenders."""

    def test_when_must_i_go_to_the_dentist(self) -> None:
        self.assertEqual(own_records_cue("Wann muss ich zum Zahnarzt?"), "Wann muss ich")

    def test_what_is_going_on_with_me_tomorrow(self) -> None:
        self.assertEqual(own_records_cue("Was ist morgen bei mir los?"), "ist morgen bei mir los")

    def test_what_do_i_do_at_the_weekend(self) -> None:
        self.assertEqual(own_records_cue("Was mache ich am Wochenende?"), "ich … Wochenende")

    def test_do_i_have_anything_tomorrow(self) -> None:
        self.assertEqual(own_records_cue("Hab ich morgen was?"), "ich … morgen")

    def test_what_is_still_pending_this_week(self) -> None:
        self.assertEqual(
            own_records_cue("Was steht diese Woche noch an?"), "steht diese Woche noch an",
        )


class WorldKnowledgeStaysTest(unittest.TestCase):
    """Die Zwillinge: Weltwissen wird weiter nachgeschlagen."""

    def test_me_as_recipient_is_no_own_records(self) -> None:
        self.assertIsNone(
            own_records_cue("Kannst du mir sagen, wann die Bundesliga-Termine sind?"),
        )

    def test_possession_without_record_word_is_no_own_records(self) -> None:
        self.assertIsNone(own_records_cue("Liegt mein Hotel an der Küste?"))

    def test_i_in_the_main_clause_and_when_without_i(self) -> None:
        self.assertIsNone(own_records_cue("Ich will wissen, wann das Planetarium öffnet."))

    def test_a_report_is_no_question(self) -> None:
        self.assertIsNone(own_records_cue("Morgen hole ich meine Schwester ab."))

    def test_own_plan_in_one_clause_world_question_in_the_other(self) -> None:
        self.assertIsNone(own_records_cue("Ich fahre morgen nach Rom, wie ist dort das Wetter?"))

    def test_subordinate_clause_is_no_question_about_the_own_day(self) -> None:
        self.assertIsNone(own_records_cue("Wie wird das Wetter, wenn wir morgen wandern?"))

    def test_with_us_at_the_weather_is_no_own_records(self) -> None:
        self.assertIsNone(own_records_cue("Wie wird das Wetter morgen bei uns?"))


class CueHelpersTest(unittest.TestCase):
    """Die Helfer je Satz und Satzteil — laut bei Nicht-Text."""

    def test_question_forms(self) -> None:
        self.assertTrue(_is_question("Hab ich morgen was"))
        self.assertTrue(_is_question("und was mache ich morgen"))
        self.assertFalse(_is_question("Morgen hole ich meine Schwester ab."))
        self.assertFalse(_is_question("wenn wir morgen wandern?"))

    def test_sentence_and_clause_cue(self) -> None:
        self.assertEqual(_sentence_cue("Was haben wir am Sonntag vor?"), "haben wir am Sonntag vor")
        self.assertIsNone(_sentence_cue("Was haben die Parteien vor?"))
        self.assertEqual(_clause_cue("Wann haben wir Training"), "Wann haben wir")
        self.assertIsNone(_clause_cue("Ich will wissen,"))

    def test_a_date_does_not_split_the_sentence(self) -> None:
        self.assertEqual(own_records_cue("Hab ich am 3.11. was?"), "ich … 3.11.")

    def test_helpers_raise_on_non_text(self) -> None:
        for helper in (_is_question, _sentence_cue, _clause_cue):
            with self.subTest(helper=helper.__name__), self.assertRaises(TypeError):
                helper(None)  # type: ignore[arg-type]


class WithholdResearchTest(unittest.TestCase):
    """Keine Suche, leeres Feld, und das Log sagt warum."""

    def test_withheld_research_is_logged_and_empty(self) -> None:
        artifact: dict = _artifact("Wochentermine", "Programmpunkte", TRAEGER_NACHSCHLAGEN)
        with patch(_SEARCH) as search, \
             self.assertLogs("ki_server.sachlage.research", level="INFO") as log:
            result: dict = withhold_research(artifact, "Termine")
        search.assert_not_called()
        self.assertEqual(result["objekte"][0]["recherche"], {})
        self.assertIn(
            "Sachlage-Recherche unterbleibt: Frage nach eigenem Bestand (Merkmal 'Termine') "
            "— 'Wochentermine Programmpunkte' nicht nachgeschlagen",
            "\n".join(log.output),
        )

    def test_without_a_lookup_target_nothing_is_logged(self) -> None:
        artifact: dict = _artifact("Wochentermine", "Programmpunkte", TRAEGER_WELT)
        with self.assertNoLogs("ki_server.sachlage.research", level="INFO"):
            result: dict = withhold_research(artifact, "Termine")
        self.assertEqual(result["objekte"][0]["recherche"], {})

    def test_empty_cue_raises(self) -> None:
        artifact: dict = _artifact("Wochentermine", "Programmpunkte", TRAEGER_NACHSCHLAGEN)
        with self.assertRaises(ValueError):
            withhold_research(artifact, " ")


class DeriveDecidesTest(unittest.TestCase):
    """`_derive` mit der echten Recherche: die Terminfrage sucht nicht, die Weltfrage schon."""

    def _derive_with(self, utterance: str, parsed: dict, hits: list[dict]) -> tuple[dict, object]:
        """Ein Lauf von `_derive` mit ersetztem Modell, Plausibilitaet und Suchmaschine."""
        with patch("graph.nodes.sachlage.model_service") as ms, \
             patch("graph.nodes.sachlage.assess_plausibility", return_value={}), \
             patch(_SEARCH, return_value=hits) as search:
            ms.chat.submit_sync.return_value.parsed = parsed
            artifact: dict | None = _derive(None, [], utterance)
        self.assertIsNotNone(artifact)
        return artifact, search

    def test_appointments_question_gets_no_web_hit(self) -> None:
        artifact, search = self._derive_with(
            _APPOINTMENTS_QUESTION,
            _artifact("Wochentermine", "Programmpunkte", TRAEGER_NACHSCHLAGEN),
            _hits("Wochentermine"),
        )
        search.assert_not_called()
        self.assertEqual(artifact["objekte"][0]["recherche"], {})
        self.assertNotIn("Nachgeschlagen", sachlage_block(artifact))

    def test_twin_world_question_is_still_looked_up(self) -> None:
        artifact, search = self._derive_with(
            _WORLD_QUESTION,
            _artifact("Planetarium", "Öffnungszeiten", TRAEGER_NACHSCHLAGEN),
            _hits("Planetarium"),
        )
        self.assertEqual(search.call_count, 1)
        self.assertEqual(search.call_args.args[0], "Planetarium Öffnungszeiten")
        self.assertEqual(list(artifact["objekte"][0]["recherche"]), ["Öffnungszeiten"])
        self.assertIn("Nachgeschlagen zu Planetarium — Öffnungszeiten", sachlage_block(artifact))


if __name__ == "__main__":
    unittest.main()
