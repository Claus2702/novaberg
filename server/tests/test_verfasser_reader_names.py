"""Zeugen: der Gedaechtnisblock und die Aufzeichnungs-Bloecke sprechen in den Namen ihres Lesers.

Das Modell ist der Schauspieler, der Charakter der Auftrag — nirgends wird
das Modell als der Charakter angesprochen (F-PROMPT-2, 29.08.2026). Bis zum
30.08.2026 sagte der [GEDAECHTNIS]-Block »Du fuehlst dazu« und »Sie ist dir
eingefallen«, und die Aufzeichnungs-Bloecke »woran du dich erinnerst« und
»das habe ich nachgelesen« — das »du« meinte den Charakter, mitten im
Prompt des Verfassers, der ueber Person A in dritter Person schreibt.

Zeugen dieser Datei:
  * **Der Formatter rendert in den Namen des Lesers**: Analyse — Nova und
    Nutzer; Verfasser — Person A und Person B; nie »du«/»dir«.
  * **Ein unbekannter Leser ist ein Fehler**, kein Rueckfall.
  * **Der Reducer schreibt beide Kanaele** (Verdrahtung).
  * **Der Kanal ist deklariert und initialisiert** — ein undeklarierter
    Schluessel faellt an der Knotengrenze still weg.
  * **Der Verfasser liest seinen Kanal**, nicht den der Analyse.
  * **Die drei Bloecke im Verfasser-Prompt** — [GEDAECHTNIS],
    [AUFZEICHNUNGEN], [EIGENE FUNDE] — kennen weder Nova noch Nutzer noch
    ein »du«; ein Verbotszeuge steht nie allein: derselbe Zeuge prueft,
    dass Person A und Person B darin vorkommen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
import unittest

from agents.dateien_index.aufzeichnungen import Aufzeichnung
from graph import base as base_mod
from graph import builder as builder_mod
from graph.format.memory_context import (
    LESER_ANALYSE,
    LESER_VERFASSER,
    format_memory_entries,
    reader_names,
    speaker_label,
)
from graph.nodes import verfasser as verf_mod
from graph.nodes.reducer import SCHREIBT, reduce_memory
from graph.state import ConversationState

ANSPRACHE = re.compile(r"\bNova\b|\bNutzer\b|\bdu\b|\bdein\w*\b|\bdir\b|\bdich\b", re.I)

KZG: dict = {
    "quelle": "kzg", "subtyp": "themen", "gewicht": 1.2,
    "inhalt": "Der Rekordwert des Pulsars liegt bei 716 Hz.",
    "meta": {"themen": ["Pulsar"], "beobachter": "assistant", "erstellt_am": 0.0},
}
RESONANZ: dict = {"erinnerungen": [
    {"inhalt": "Anna ist meine Schwester", "emotion": "vertrauen",
     "beobachter": "user", "sortier_gewicht": 0.9, "pfad": []},
    {"inhalt": "Der Kollaps war das Thema", "emotion": "neugierig",
     "beobachter": "assistant", "sortier_gewicht": 0.4,
     "pfad": [{"verbindungs_gruende": ["themen"], "geteilte_themen": ["Kollaps"]}]},
]}


def _state(**felder: object) -> dict:
    """Ein State, wie der Verfasser ihn liest."""
    basis: dict = {
        "user_prompt":      "Wie entsteht ein Gammablitz?",
        "user_id":          "u", "character_id": "c", "turn_id": "t",
        "memory_context":   "", "memory_context_verfasser": "", "web_context": "",
        "session_turns":    [], "task_block": "", "task_context_cut": False,
        "gespraechsvektor": "", "gv_detail": {}, "antwort_inhalt": "",
        "aufzeichnungen":   [],
        "external":         None, "internal": None,
        "eigener_gedanke":  "", "einwand": {},
    }
    basis.update(felder)
    return basis


def _block(prompt: str, kopf: str) -> str:
    """Der Abschnitt eines Blocks bis zum naechsten Blockkopf."""
    rest: str = prompt.split(kopf, 1)[1]
    naechster = re.search(r"\n\[(?!KZG|LZG)[A-Z ]+\]", rest)
    return rest[:naechster.start()] if naechster else rest


class FormatterInDenNamenDesLesersTest(unittest.TestCase):
    """Analyse: Nova und Nutzer. Verfasser: Person A und Person B. Nie »du«."""

    def test_analyse(self) -> None:
        text: str = format_memory_entries([KZG], lzg_resonanz=RESONANZ, leser=LESER_ANALYSE)
        self.assertIn("Sprecher: Nova): Der Rekordwert", text)
        self.assertIn("Zwei Erinnerungen sind Nova gerade da.", text)
        self.assertIn("Sprecher: Nutzer", text)
        self.assertIn("Nova fuehlt dazu: Vertrauen", text)
        self.assertIn("Sie ist Nova eingefallen ueber: gemeinsames Thema Kollaps", text)
        self.assertIn("Sie kam Nova direkt zur Frage in den Sinn", text)
        self.assertIsNone(re.search(r"\bdu\b|\bdir\b|\bdich\b|\bdein", text, re.I), text)

    def test_verfasser(self) -> None:
        text: str = format_memory_entries([KZG], lzg_resonanz=RESONANZ, leser=LESER_VERFASSER)
        self.assertIn("Sprecher: Person A): Der Rekordwert", text)
        self.assertIn("Zwei Erinnerungen sind Person A gerade da.", text)
        self.assertIn("Sprecher: Person B", text)
        self.assertIn("Person A fuehlt dazu: Vertrauen", text)
        self.assertIn("Sie ist Person A eingefallen ueber", text)
        self.assertIsNone(ANSPRACHE.search(text), text)

    def test_default_is_analyse(self) -> None:
        self.assertEqual(
            format_memory_entries([KZG]),
            format_memory_entries([KZG], leser=LESER_ANALYSE),
        )
        self.assertEqual(speaker_label("user"), "Nutzer")
        self.assertEqual(speaker_label("user", reader_names(LESER_VERFASSER, "t")), "Person B")

    def test_unknown_reader_is_an_error(self) -> None:
        with self.assertRaises(ValueError):
            format_memory_entries([KZG], leser="responder")
        with self.assertRaises(ValueError):
            reader_names("", "t")


class ReducerSchreibtBeideKanaeleTest(unittest.TestCase):
    """Die Verdrahtung: ein Inhalt, zwei Namenssysteme, auf jedem Rueckkehrpfad."""

    def test_with_entries(self) -> None:
        update: dict = reduce_memory({"memory_entries": [KZG], "lzg_resonanz": RESONANZ})
        self.assertEqual(set(update), set(SCHREIBT))
        self.assertIn("Sprecher: Nova", update["memory_context"])
        self.assertIn("Sprecher: Person A", update["memory_context_verfasser"])
        self.assertIsNone(ANSPRACHE.search(update["memory_context_verfasser"]))

    def test_resonance_only(self) -> None:
        update: dict = reduce_memory({"memory_entries": [], "lzg_resonanz": RESONANZ})
        self.assertIn("Nova gerade da", update["memory_context"])
        self.assertIn("Person A gerade da", update["memory_context_verfasser"])

    def test_empty(self) -> None:
        update: dict = reduce_memory({"memory_entries": [], "lzg_resonanz": None})
        self.assertEqual(update["memory_context"], "")
        self.assertEqual(update["memory_context_verfasser"], "")


class KanalDeklariertUndInitialisiertTest(unittest.TestCase):
    """Ein undeklarierter Schluessel faellt an der Knotengrenze still weg."""

    def test_declared(self) -> None:
        self.assertIn("memory_context_verfasser", ConversationState.__annotations__)

    def test_initialised_in_both_builders(self) -> None:
        import inspect
        for modul in (base_mod, builder_mod):
            with self.subTest(modul=modul.__name__):
                self.assertIn("memory_context_verfasser", inspect.getsource(modul))


class VerfasserLiestSeinenKanalTest(unittest.TestCase):
    """Der Verfasser nimmt den Block in seinen Namen — nicht den der Analyse."""

    def test_reads_own_channel(self) -> None:
        prompt: str = verf_mod._build_system_prompt(_state(
            memory_context="ANALYSE-FASSUNG", memory_context_verfasser="VERFASSER-FASSUNG",
        ))
        self.assertIn("[GEDAECHTNIS]", prompt)
        self.assertIn("VERFASSER-FASSUNG", prompt)
        self.assertNotIn("ANALYSE-FASSUNG", prompt)

    def test_without_own_channel_no_block(self) -> None:
        prompt: str = verf_mod._build_system_prompt(_state(memory_context="ANALYSE-FASSUNG"))
        self.assertNotIn("[GEDAECHTNIS]", prompt)
        self.assertNotIn("ANALYSE-FASSUNG", prompt)


class DreiBloeckeOhneAnspracheTest(unittest.TestCase):
    """[GEDAECHTNIS], [AUFZEICHNUNGEN], [EIGENE FUNDE] sprechen ueber Person A."""

    def setUp(self) -> None:
        self.prompt = verf_mod._build_system_prompt(_state(
            memory_context_verfasser=format_memory_entries(
                [KZG], lzg_resonanz=RESONANZ, leser=LESER_VERFASSER),
            aufzeichnungen=[
                Aufzeichnung(fundstelle="Ablage/fremd.md", thema="Ein Thema",
                             zusammenfassung="Ein Auszug.", kosinus=0.4, eigentum="nutzer"),
                Aufzeichnung(fundstelle="Ablage/figur.md", thema="Ein Fund",
                             zusammenfassung="Ein Fund.", kosinus=0.4, eigentum="figur"),
            ],
        ))

    def test_blocks(self) -> None:
        for kopf in ("[GEDAECHTNIS]", "[AUFZEICHNUNGEN]", "[EIGENE FUNDE]"):
            with self.subTest(block=kopf):
                self.assertIn(kopf, self.prompt)
                block: str = _block(self.prompt, kopf)
                self.assertIn("Person A", block)
                self.assertIsNone(ANSPRACHE.search(block), block)
        self.assertIn("Person B", _block(self.prompt, "[GEDAECHTNIS]"))


if __name__ == "__main__":
    unittest.main()
