"""Zeugen: der [SACHLAGE]-Block spricht in den Namen seines Lesers.

Das Modell ist der Schauspieler, der Charakter ist der Auftrag — nirgends
wird das Modell als der Charakter angesprochen (Verfasser-Auftrag, 14.08.2026;
bekraeftigt 29.08.2026). Der Verfasser kennt PERSON A und PERSON B; der
Gespraechsvektor analysiert in dritter Person und nennt Nova und den Nutzer.
Bis zum 29.08.2026 trug der Block »der Nutzer«, »Nova« und »beantworte es aus
deinem Wissen« in den Verfasser-Prompt — ein zweites und drittes
Namenssystem, die am 13.08.2026 gemessene Fehlerklasse.

Zeugen dieser Datei:
  * **Der Block fuer den Verfasser kennt nur Person A und Person B** — kein
    »Nova«, kein »Nutzer«, kein »du«/»dein«; derselbe Block fuer den
    Gespraechsvektor nennt Nova und den Nutzer.
  * **Ein unbekannter Leser ist ein Fehler**, kein Rueckfall.
  * **Die Bruecke spricht ueber Person A**, nicht mit ihr.
  * **Der Verfasser bekommt den Block in seinen Namen** (Verdrahtung); der
    Gespraechsvektor in seinen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
import unittest

from ei.haltung import haltung_berechnen
from graph.nodes import verfasser as verf_mod
from graph.nodes.sachlage import (
    LESER_GV,
    LESER_VERFASSER,
    SPRECHER_NOVA,
    SPRECHER_NUTZER,
    TRAEGER_WELT,
    sachlage_block,
    sachlage_bridge_block,
    speaker_lines,
)

_CHARAKTER_ANSPRACHE = re.compile(
    r"\bNova\b|\bNutzer\b|\bdu\b|\bdein\w*\b|\bdir\b|\bdich\b", re.I,
)


def _artifact() -> dict:
    return {
        "thema": "Kollaps", "gegenstand": "Der Kollaps",
        "nutzerziel": "eine Einschaetzung erhalten",
        "ausdrucksweise": "beilaeufig",
        "objekte": [{
            "name": "Kollaps", "klasse": "vorgang", "akut": True,
            "gedeckt": {"Energieentladung": "muss knallen", "Rekord": "716 Hz",
                        "Struktur": "Entartungsdruck"},
            "sprecher": {"Energieentladung": SPRECHER_NUTZER, "Rekord": SPRECHER_NOVA},
            "quellen": {"Struktur": {"quelle": "kzg", "herkunft": "G5", "eintrag": "..."}},
            "offen": ["Dauer"], "traeger": {"Dauer": TRAEGER_WELT},
        }],
        "wiederaufnahme": {"thema": "Pulsar", "erstellt_am": ""},
    }


class ReaderNamesTest(unittest.TestCase):
    """Person A und Person B beim Verfasser, Nova und der Nutzer beim Gespraechsvektor."""

    def test_the_writer_block_names_person_a_and_person_b_only(self) -> None:
        block: str = sachlage_block(_artifact(), leser=LESER_VERFASSER)
        self.assertIn("Was Person B vermutlich will", block)
        self.assertIn("Person B hat zu Kollaps gesagt: Energieentladung", block)
        self.assertIn("Person A hat schon zu Kollaps gesagt: Rekord", block)
        self.assertIn("Dazu weiss Person A schon (", block)
        self.assertIn(
            "Person B will zu Kollaps wissen: Dauer — Person A beantwortet es aus ihrem Wissen",
            block,
        )
        self.assertIn("Person B kommt auf Pulsar zurueck", block)
        self.assertIsNone(_CHARAKTER_ANSPRACHE.search(block), block)

    def test_the_vector_block_names_nova_and_the_user(self) -> None:
        block: str = sachlage_block(_artifact(), leser=LESER_GV)
        self.assertIn("Was der Nutzer vermutlich will", block)
        self.assertIn("Der Nutzer hat zu Kollaps gesagt", block)
        self.assertIn("Nova hat schon zu Kollaps gesagt", block)
        self.assertIn(
            "Der Nutzer will zu Kollaps wissen: Dauer — Nova beantwortet es aus ihrem Wissen",
            block,
        )
        self.assertNotIn("Person A", block)

    def test_an_unknown_reader_is_an_error(self) -> None:
        with self.assertRaises(ValueError):
            sachlage_block(_artifact(), leser="responder")
        with self.assertRaises(ValueError):
            speaker_lines(_artifact()["objekte"][0], leser="responder")

    def test_the_bridge_speaks_about_person_a(self) -> None:
        block: str = sachlage_bridge_block({
            "via": "turn_id", "ausloeser_turn_id": "t1",
            "damals": {"thema": "Pulsar", "gegenstand": "Der Rekord", "nutzerziel": "wissen"},
            "aktuell": {"gegenstand": "Der Kollaps"},
        })
        self.assertIn("Person As Gedanke entstand frueher", block)
        self.assertIn("Was Person B damals wollte", block)
        self.assertIsNone(_CHARAKTER_ANSPRACHE.search(block), block)


class WiringTest(unittest.TestCase):
    """Der Verfasser bekommt den Block in seinen Namen."""

    def test_the_writer_prompt_carries_the_block_in_person_names(self) -> None:
        state: dict = {
            "user_prompt": "Das muss knallen.", "event_source": "user", "event_payload": {},
            "user_id": "u", "character_id": "c", "turn_id": "t",
            "memory_context": "", "web_context": "", "session_turns": [], "task_block": "",
            "gespraechsvektor": "", "gv_detail": {}, "node_annotations": {},
            "sachlage": {**_artifact(), "herkunft": "frisch"},
            "haltung": haltung_berechnen("werkstatt", {"wissbegier": 0.87, "aufmerksamkeit": 0.91}),
        }
        prompt: str = verf_mod._build_system_prompt(state)
        block: str = prompt.split("\n[SACHLAGE]\n", 1)[1].split("\n[", 1)[0]
        self.assertIn("Person B will zu Kollaps wissen", block)
        self.assertIsNone(_CHARAKTER_ANSPRACHE.search(block), block)


if __name__ == "__main__":
    unittest.main()
