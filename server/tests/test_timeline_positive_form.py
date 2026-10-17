"""Zeugen: Die Positivform des Verschiebens steht beim Timeline-Agenten.

Sie stand als `raw_time_form` mit den `_RAW_*`-Namen im Zeitparser
(`utils/zeitparser.py`) und hat einen einzigen Aufrufer,
`agents/timeline/crud.py::_raw_form_agrees`. Jetzt steht sie in
`agents/timeline/positive_form.py` und liest das Vokabular des Parsers ueber
einen oeffentlichen Namen (`TIME_VOCABULARY`).

Zeugen dieser Datei:
  * **Ort**: Der Parser bindet keinen Namen der Positivform mehr, das neue
    Modul bindet jeden — gelesen per `ast` aus beiden Quellen.
  * **Keine privaten Importe**: Das neue Modul importiert aus
    `utils.zeitparser` nur oeffentliche Namen, mit Zwilling an einer
    synthetischen Quelle.
  * **Das Vokabular**: unveraenderlich, laut bei leerer Liste, dieselbe
    ASCII-Umschrift wie der Parser; die Alternation des Moduls ordnet
    laengste zuerst.
  * Ohne Datenbank, Netz und Modell. Das Verhalten der Form pruefen die
    Zeugen in `test_timeline_reschedule.py`.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import unittest
from pathlib import Path
from types import MappingProxyType

from agents.timeline import positive_form
from utils import zeitparser

#: Das Wurzelverzeichnis des Servers: Hier liegen `utils/` und `agents/`.
SERVER_ROOT: Path = Path(__file__).resolve().parents[1]
PARSER_FILE: Path = SERVER_ROOT / "utils" / "zeitparser.py"
FORM_FILE: Path = SERVER_ROOT / "agents" / "timeline" / "positive_form.py"

#: Jeder Name, der mit der Positivform aus dem Parser umgezogen ist, ausdruecklich
#: genannt und nicht aus einer Quelle gerechnet.
MOVED_NAMES: frozenset[str] = frozenset({
    "RawTimeForm", "raw_time_form", "_raw_outside_admitted", "_raw_new_hour",
    "_RAW_HOUR", "_RAW_DAY", "_RAW_TIME_FORM", "_RAW_NEW_HOUR_GROUPS", "_RAW_HOUR_VALUES",
    "_RAW_NO_TIME_WORDS", "_RAW_TIME_WORDS", "_RAW_PARSER_WORDS", "_RAW_OTHER_TIME",
    "_RAW_ADMITTED_VERB", "_RAW_ADMITTED_WORDS", "_RAW_TITLE_WORD", "_RAW_TITLE_MIN_LETTERS",
    "_RAW_TITLE_COMPOUND_END", "_RAW_TITLE_COMPOUND_JOINTS", "_RAW_FUNCTION_WORDS",
})


def _bound_names(source: str) -> set[str]:
    """Jeder Name, den `source` auf Modulebene bindet: Klasse, Funktion, Zuweisung."""
    names: set[str] = set()
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            names.add(node.name)
        elif isinstance(node, ast.Assign | ast.AnnAssign):
            targets: list = node.targets if isinstance(node, ast.Assign) else [node.target]
            names |= {target.id for target in targets if isinstance(target, ast.Name)}
    return names


def _form_names(names: set[str]) -> set[str]:
    """Die Namen, die zur Positivform gehoeren: umgezogen, `_RAW_*` oder `_raw_*`."""
    return {
        name for name in names
        if name in MOVED_NAMES or name.startswith(("_RAW_", "_raw_", "raw_time_form"))
    }


def _parser_imports(source: str) -> tuple[list[str], list[str]]:
    """Die Importe aus `utils.zeitparser` in `source`: (oeffentlich, privat oder ganz).

    Jeder Import wird gezaehlt, auch einer in einer Funktion. Ein ganzes Modul
    (`import utils.zeitparser`, `from utils import zeitparser`) zaehlt als
    privat: Ueber das Modul ist jeder private Name erreichbar.
    """
    public: list[str] = []
    private: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            private += [alias.name for alias in node.names if alias.name == "utils.zeitparser"]
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module == "utils":
            private += [f"utils.{a.name}" for a in node.names if a.name == "zeitparser"]
        if node.module != "utils.zeitparser":
            continue
        for alias in node.names:
            name: str = f"{node.module}.{alias.name}"
            (private if alias.name.startswith("_") else public).append(name)
    return public, private


class PlaceTest(unittest.TestCase):
    """Die Positivform steht im neuen Modul und nicht mehr im Parser."""

    def test_the_parser_binds_no_name_of_the_form(self) -> None:
        names: set[str] = _bound_names(PARSER_FILE.read_text(encoding="utf-8"))

        self.assertEqual(_form_names(names), set(), "Positivform noch im Zeitparser")
        for kept in ("TimeReading", "read_time", "day_phrase", "dotted_clock_times",
                     "TIME_VOCABULARY"):
            with self.subTest(bleibt=kept):
                self.assertIn(kept, names, "die Pruefung sah den Parser nicht")

    def test_twin_the_new_module_binds_every_name_of_the_form(self) -> None:
        """Der Zwilling: Jeder umgezogene Name steht im neuen Modul."""
        names: set[str] = _bound_names(FORM_FILE.read_text(encoding="utf-8"))

        self.assertEqual(MOVED_NAMES - names, set())
        self.assertEqual(_form_names(names), set(MOVED_NAMES))

    def test_twin_a_form_name_in_a_source_is_found(self) -> None:
        """Dieselbe Pruefung findet einen zurueckgelassenen Namen, auch einen neuen `_RAW_*`."""
        source: str = (
            "_RAW_EXTRA: int = 1\n"
            "def raw_time_form(text, title):\n"
            "    return None\n"
            "class RawTimeForm:\n"
            "    pass\n"
            "def read_time(text):\n"
            "    return None\n"
        )

        self.assertEqual(
            _form_names(_bound_names(source)), {"_RAW_EXTRA", "raw_time_form", "RawTimeForm"},
        )


class ParserImportTest(unittest.TestCase):
    """Das neue Modul importiert aus `utils.zeitparser` nur oeffentliche Namen."""

    def test_the_new_module_imports_no_private_name_of_the_parser(self) -> None:
        public, private = _parser_imports(FORM_FILE.read_text(encoding="utf-8"))

        self.assertEqual(private, [], "privater Name des Parsers im neuen Modul")
        self.assertEqual(public, ["utils.zeitparser.TIME_VOCABULARY"], "die Pruefung sah nichts")

    def test_twin_a_private_or_whole_import_is_found(self) -> None:
        """Der Zwilling: Dieselbe Pruefung findet private Namen und das ganze Modul."""
        source: str = (
            "from utils.zeitparser import TIME_VOCABULARY, _HOUR_WORDS\n"
            "def f():\n"
            "    from utils.zeitparser import _ascii_umschrift\n"
            "import utils.zeitparser\n"
            "from utils import zeitparser\n"
        )

        public, private = _parser_imports(source)

        self.assertEqual(public, ["utils.zeitparser.TIME_VOCABULARY"])
        self.assertEqual(sorted(private), [
            "utils.zeitparser", "utils.zeitparser",
            "utils.zeitparser._HOUR_WORDS", "utils.zeitparser._ascii_umschrift",
        ])


class VocabularyTest(unittest.TestCase):
    """Das Vokabular des Parsers und die Alternation des neuen Moduls."""

    def test_the_vocabulary_is_immutable(self) -> None:
        vocabulary: zeitparser.TimeVocabulary = zeitparser.TIME_VOCABULARY

        self.assertIsInstance(vocabulary.hour_words, MappingProxyType)
        with self.assertRaises(TypeError):
            vocabulary.hour_words["dreizehn"] = 1
        with self.assertRaises(AttributeError):
            vocabulary.words = ()
        self.assertEqual(vocabulary.hour_words["zwölf"], 12)
        self.assertEqual(vocabulary.hour_words["zwoelf"], 12)
        self.assertNotIn("ein", vocabulary.hour_words)

    def test_the_vocabulary_holds_the_lists_of_the_parser(self) -> None:
        """Abgeleitet, nicht abgeschrieben: Jede Liste steht vollstaendig darin."""
        vocabulary: zeitparser.TimeVocabulary = zeitparser.TIME_VOCABULARY

        self.assertEqual(vocabulary.weekdays[0], "montag")
        self.assertEqual(len(vocabulary.weekdays), 7)
        self.assertIn("nächsten", vocabulary.relative_prefixes)
        self.assertIn("zehnten", vocabulary.ordinal_days)
        for word in ("freitag", "märz", "okt", "übermorgen", "nachmittags", "Abend", "stunden",
                     "vergangenem", "halb", "vierundzwanzig", "einunddreißigste", "mittag",
                     "nacht"):
            with self.subTest(wort=word):
                self.assertIn(word, vocabulary.words)
        self.assertNotIn("termin", vocabulary.words)

    def test_an_empty_list_or_a_wrong_hour_is_rejected(self) -> None:
        good: dict = {
            "words": ("freitag",), "hour_words": MappingProxyType({"elf": 11}),
            "ordinal_days": ("zehnten",), "relative_prefixes": ("nächste",),
            "weekdays": ("freitag",),
        }
        self.assertEqual(zeitparser.TimeVocabulary(**good).words, ("freitag",))
        for name, value in (
            ("words", ()), ("words", ("freitag", "")), ("weekdays", ()),
            ("hour_words", MappingProxyType({})), ("hour_words", MappingProxyType({"elf": 25})),
            ("hour_words", MappingProxyType({"elf": "11"})),
        ):
            with self.subTest(feld=name, wert=value):
                with self.assertRaises(ValueError):
                    zeitparser.TimeVocabulary(**{**good, name: value})

    def test_ascii_form_spells_like_the_parser(self) -> None:
        for text, expected in (("märz", "maerz"), ("Grüße", "Gruesse"), ("zwölf", "zwoelf"),
                               ("", ""), ("freitag", "freitag")):
            with self.subTest(text=text):
                self.assertEqual(zeitparser.TIME_VOCABULARY.ascii_form(text), expected)
                self.assertEqual(zeitparser.TIME_VOCABULARY.ascii_form(text),
                                 zeitparser._ascii_umschrift(text))
        with self.assertRaises(TypeError):
            zeitparser.TIME_VOCABULARY.ascii_form(None)

    def test_alternation_puts_the_longest_first(self) -> None:
        self.assertEqual(positive_form._alternation("vier", "vierzehn", "elf", "acht"),
                         "vierzehn|vier|acht|elf")
        self.assertEqual(positive_form._alternation("ab", "cd", "e"), "ab|cd|e")
        for words in ((), ("elf", ""), ("elf", None)):
            with self.subTest(woerter=words):
                with self.assertRaises(ValueError):
                    positive_form._alternation(*words)


if __name__ == "__main__":
    unittest.main()
