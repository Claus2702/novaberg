"""Zeugen: Das Kalender-Angebot der Sachlage liest den Zeitbezug am Objekt.

Den Namen eines Objekts vergibt das Modell frei (*Novemberereignisse*,
*Zahnarzttermin*). Ein Fenster aus dem Namen fand deshalb nichts
(`SACHLAGE-KALENDER-VERFEHLT-OBJEKTNAMEN`). Seit Nr. 36 leitet der Server
ein Feld `zeitbezug` von der Aeusserung und dem Namen ab, traegt es an akuten
Objekten weiter, und nur daraus entsteht das Fenster; ohne Feld keins.

Zeugen dieser Datei:
  1. **Zeitraum** — *Was steht im November an?* mit *Novemberereignisse*
     ergibt den November; ueber Redis bietet das Angebot genau die drei
     Novembertermine an. Zwilling: *Terminuebersicht* bekommt kein Feld.
  2. **Titel** — *Wann muss ich zum Zahnarzt?* mit *Zahnarzttermin* ergibt
     *Zahnarzt*; beide Zahnarzttermine stehen im Angebot, der vergangene
     gekennzeichnet. Zwilling: *Tee* ist kein Stichwort.
  3. **Feld des Servers** — aus dem Modell entfernt; aus Redis bleibt es.
  4. **Prompt zeichengleich** — mit und ohne Feld an der vorigen Blase.
  5. **Weitergetragen** — zwei Turns weit; ein neuer Zeitraum ersetzt es.
  6. **Falsche Form** — laut verworfen.
  7. **Ueber Mitternacht** — `von`/`bis` werden nicht neu gerechnet.
  8. **Importe** — kein `tools.` im Modul.
  9. **Ohne Zeitbezug kein Fenster** — *November* ohne Feld liest nichts.
  Dazu die Ableitung: *Wochenende* mit dem Stamm in der Fuge, die
  Tippfehlerkorrektur (*was* → *Mai*) traegt keinen Zeitraum, ein Zeitwort
  ist kein Titel, und ein Titel entsteht nur aus einer Frage nach dem
  Zeitpunkt.

Die Termine liegen in der Testdatenbank (`config.POSTGRES_URL`) unter einer
eigenen Kennung, die vor und nach jedem Zeugen abgeraeumt wird. Redis, das
Modell und die Uhr sind ersetzt. Die Beispiele sind synthetisch. Kein
skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import json
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import psycopg2

from config import POSTGRES_URL
from graph.appointments import KIND_RANGE
from graph.nodes import sachlage as sachlage_mod
from graph.nodes.sachlage import _derive, _validate_artifact, sachlage_load
from graph.nodes.sachlage_form import normalize_object_form
from graph.nodes.sachlage_resolver import SOURCE_CALENDAR, MemoryHit, memory_offer
from graph.nodes.sachlage_zeitbezug import (
    carry_time_references,
    checked_time_reference,
    derive_time_reference,
    time_reference_window,
)
from memory.repositories.timeline_repository import TimelineRepository

BERLIN: ZoneInfo = ZoneInfo("Europe/Berlin")

#: Die eingefrorene Uhr: Samstag, 17.10.2026, 12:00 Ortszeit.
NOW: datetime = datetime(2026, 10, 17, 12, 0, tzinfo=BERLIN)
TODAY: date = NOW.date()

TEST_USER: str = "test_sachlage_zeitbezug"
SERVER_ROOT: Path = Path(__file__).resolve().parents[1]

_SACHLAGE_CLOCK: str = "graph.nodes.sachlage.now_local"
_RESOLVER_CLOCK: str = "graph.nodes.sachlage_resolver.now_local"
_FORM_LOGGER: str = "ki_server.sachlage"
_TIME_REFERENCE_LOGGER: str = "ki_server.sachlage.zeitbezug"

_NOVEMBER: dict = {
    "art": "zeitraum", "von": "2026-11-01", "bis": "2026-11-30", "wortlaut": "im November",
}


def _parse(name: str, gedeckt: dict | None = None) -> dict:
    """Ein Parse des Modells mit einem akuten Objekt, offen ist *Termine*."""
    return {
        "thema": "Termine", "gegenstand": "Was ansteht", "nutzerziel": "planen",
        "ausdrucksweise": "fragend",
        "objekte": [{
            "name": name, "klasse": "vorgang", "akut": True,
            "gedeckt": dict(gedeckt or {}), "offen": ["Termine"],
        }],
    }


def _turn(
    previous: dict | None, utterance: str, parse: dict, now: datetime = NOW,
) -> tuple[dict | None, str]:
    """Ein Lauf von `_derive` mit ersetztem Modell: das Artefakt und der Prompt."""
    with patch("graph.nodes.sachlage.model_service") as model, \
         patch("graph.nodes.sachlage.assess_plausibility", return_value={}), \
         patch("graph.nodes.sachlage.own_records_cue", return_value=None), \
         patch("graph.nodes.sachlage.research_open_property", side_effect=lambda a: a), \
         patch(_SACHLAGE_CLOCK, return_value=now):
        model.chat.submit_sync.return_value.parsed = json.loads(json.dumps(parse))
        artefakt: dict | None = _derive(previous, [], utterance)
        prompt: str = model.chat.submit_sync.call_args.args[0].messages[0]["content"]
    return artefakt, prompt


def _through_redis(artefakt: dict) -> dict:
    """Die Blase so, wie der naechste Turn sie aus Redis laedt (`sachlage_load`)."""
    stored: dict = {"json": json.dumps(artefakt, ensure_ascii=False), "turn_zeit": str(9e12)}
    redis: MagicMock = MagicMock()
    redis.hgetall.return_value = stored
    with patch.object(sachlage_mod, "redis_client", redis), \
         patch.object(sachlage_mod.time, "time", return_value=9e12):
        vorige, verfallen = sachlage_load("u", "c")
    if verfallen or vorige is None:
        msg: str = "die Blase kam nicht aus Redis zurueck"
        raise AssertionError(msg)
    return vorige


def _calendar(previous: dict | None) -> list[MemoryHit]:
    """Die Kalenderzeilen im Angebot des Turns, gelesen aus der Testdatenbank."""
    with patch(_RESOLVER_CLOCK, return_value=NOW):
        hits: list[MemoryHit] = memory_offer(
            {"user_id": TEST_USER, "memory_entries": []}, previous,
        )
    return [h for h in hits if h.source == SOURCE_CALENDAR]


class _SeededTest(unittest.TestCase):
    """Termine des Pruefnutzers in der Testdatenbank, vor und nach jedem Zeugen abgeraeumt."""

    def setUp(self) -> None:
        """Raeumt ab und saet: drei im November, je einer davor und danach, zwei beim Zahnarzt."""
        self._clear()
        self.november: list[int] = [
            self._seed(datetime(2026, 11, 1, 10, 0, tzinfo=BERLIN), "Flohmarkt"),
            self._seed(datetime(2026, 11, 15, 18, 0, tzinfo=BERLIN), "Elternabend"),
            self._seed(datetime(2026, 11, 30, 20, 0, tzinfo=BERLIN), "Abschlussessen"),
        ]
        self.outside: list[int] = [
            self._seed(datetime(2026, 10, 31, 23, 30, tzinfo=BERLIN), "Halloween-Feier"),
            self._seed(datetime(2026, 12, 1, 9, 0, tzinfo=BERLIN), "Adventsmarkt"),
        ]
        self.dentist_past: int = self._seed(
            datetime(2026, 10, 10, 10, 0, tzinfo=BERLIN), "Zahnarzt",
        )
        self.dentist_next: int = self._seed(
            datetime(2026, 10, 20, 8, 15, tzinfo=BERLIN), "Zahnarzt Kontrolle",
        )

    def tearDown(self) -> None:
        """Raeumt die Zeilen des Pruefnutzers ab."""
        self._clear()

    @staticmethod
    def _seed(moment: datetime, title: str) -> int:
        """Ein Termin mit Uhrzeit fuer den Pruefnutzer; die Kennung der Zeile."""
        return TimelineRepository.insert(
            POSTGRES_URL, TEST_USER, moment, "termin", title, precision="minute",
        )

    @staticmethod
    def _clear() -> None:
        """Loescht jede Zeile des Pruefnutzers — nur seine."""
        conn = psycopg2.connect(POSTGRES_URL)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM timeline WHERE user_id = %s", (TEST_USER,))
        finally:
            conn.close()


class PeriodTest(_SeededTest):
    """Zeuge 1: ein Zeitraum der Frage liest im Folgeturn genau diesen Zeitraum."""

    def test_november_is_derived_and_offered_in_the_next_turn(self) -> None:
        artefakt, _ = _turn(None, "Was steht im November an?", _parse("Novemberereignisse"))

        self.assertEqual(artefakt["objekte"][0]["zeitbezug"], _NOVEMBER)
        hits: list[MemoryHit] = _calendar(_through_redis(artefakt))
        self.assertEqual([h.origin for h in hits], [f"timeline#{i}" for i in self.november])

    def test_twin_a_name_without_the_period_word_gets_no_field(self) -> None:
        artefakt, _ = _turn(None, "Was steht im November an?", _parse("Terminuebersicht"))

        self.assertNotIn("zeitbezug", artefakt["objekte"][0])
        self.assertEqual(_calendar(_through_redis(artefakt)), [])


class TitleTest(_SeededTest):
    """Zeuge 2: ein Termin-Titel liest in beide Richtungen, vergangene gekennzeichnet."""

    def test_the_dentist_is_derived_and_both_appointments_are_offered(self) -> None:
        artefakt, _ = _turn(None, "Wann muss ich zum Zahnarzt?", _parse("Zahnarzttermin"))

        self.assertEqual(
            artefakt["objekte"][0]["zeitbezug"],
            {"art": "titel", "stichwort": "Zahnarzt", "wortlaut": "Zahnarzt"},
        )
        hits: list[MemoryHit] = _calendar(_through_redis(artefakt))
        self.assertEqual(
            [h.origin for h in hits],
            [f"timeline#{self.dentist_past}", f"timeline#{self.dentist_next}"],
        )
        self.assertIn("vergangen", hits[0].content)
        self.assertNotIn("vergangen", hits[1].content)

    def test_twin_a_word_under_four_letters_is_no_keyword(self) -> None:
        self.assertIsNone(derive_time_reference("Teestunde", "Wann ist Tee?", TODAY))


class ServerFieldTest(unittest.TestCase):
    """Zeuge 3: das Feld gehoert dem Server."""

    def test_the_field_from_the_model_is_removed(self) -> None:
        parse: dict = _parse("Novemberereignisse")
        parse["objekte"][0]["zeitbezug"] = dict(_NOVEMBER)
        with self.assertLogs(_FORM_LOGGER, level="WARNING") as log:
            artefakt: dict | None = _validate_artifact(parse)

        self.assertNotIn("zeitbezug", artefakt["objekte"][0])
        self.assertIn("zeitbezug", "\n".join(log.output))

    def test_twin_from_redis_it_stays(self) -> None:
        stored: dict = _parse("Novemberereignisse")
        stored["objekte"][0]["zeitbezug"] = dict(_NOVEMBER)

        self.assertEqual(_through_redis(stored)["objekte"][0]["zeitbezug"], _NOVEMBER)


class PromptTest(unittest.TestCase):
    """Zeuge 4: Das Feld veraendert den Sachlage-Prompt nicht."""

    @staticmethod
    def _previous(zeitbezug: dict | None, ort: str = "Saal") -> dict:
        """Eine vorige Blase mit einem akuten Objekt, mit oder ohne Feld."""
        previous: dict = _parse("Novemberereignisse", gedeckt={"Ort": ort})
        if zeitbezug is not None:
            previous["objekte"][0]["zeitbezug"] = dict(zeitbezug)
        return previous

    def test_the_prompt_is_identical_with_and_without_the_field(self) -> None:
        parse: dict = _parse("Novemberereignisse")
        _, with_field = _turn(self._previous(_NOVEMBER), "Und wann genau?", parse)
        _, without_field = _turn(self._previous(None), "Und wann genau?", parse)

        self.assertEqual(with_field, without_field)
        self.assertNotIn("2026-11-01", with_field)

    def test_twin_another_covered_value_changes_it(self) -> None:
        parse: dict = _parse("Novemberereignisse")
        _, hall = _turn(self._previous(_NOVEMBER), "Und wann genau?", parse)
        _, garden = _turn(self._previous(_NOVEMBER, ort="Garten"), "Und wann genau?", parse)

        self.assertNotEqual(hall, garden)


class CarriedTest(_SeededTest):
    """Zeuge 5: Das Feld ueberlebt Turns ohne Zeitausdruck; ein neuer Zeitraum ersetzt es."""

    def test_the_field_survives_two_turns(self) -> None:
        first, _ = _turn(None, "Was steht im November an?", _parse("Novemberereignisse"))
        second, _ = _turn(_through_redis(first), "Und wann genau?", _parse("Novemberereignisse"))

        self.assertEqual(second["objekte"][0]["zeitbezug"], _NOVEMBER)
        hits: list[MemoryHit] = _calendar(_through_redis(second))
        self.assertEqual([h.origin for h in hits], [f"timeline#{i}" for i in self.november])

    def test_twin_a_new_period_replaces_it(self) -> None:
        first, _ = _turn(None, "Was steht diesen Monat an?", _parse("Monatsplanung"))
        second, _ = _turn(_through_redis(first), "Und nächsten Monat?", _parse("Monatsplanung"))

        self.assertEqual(
            (first["objekte"][0]["zeitbezug"]["von"], first["objekte"][0]["zeitbezug"]["bis"]),
            ("2026-10-01", "2026-10-31"),
        )
        self.assertEqual(
            second["objekte"][0]["zeitbezug"],
            {"art": "zeitraum", "von": "2026-11-01", "bis": "2026-11-30",
             "wortlaut": "nächsten Monat"},
        )


class MalformedTest(unittest.TestCase):
    """Zeuge 6: Ein falsches Feld wird laut verworfen."""

    _MALFORMED: tuple[object, ...] = (
        "im November",
        {**_NOVEMBER, "von": "2026-13-01"},
        {**_NOVEMBER, "von": "2026-12-01"},
        {**_NOVEMBER, "art": "tag"},
        {"art": "titel", "wortlaut": "Zahnarzt"},
        {**_NOVEMBER, "von": "20261101"},
    )

    def test_each_malformed_field_is_dropped_loudly(self) -> None:
        for raw in self._MALFORMED:
            with self.subTest(feld=raw), \
                 self.assertLogs(_TIME_REFERENCE_LOGGER, level="ERROR") as log:
                self.assertIsNone(checked_time_reference(raw, "Novemberereignisse"))
                self.assertIn("verworfen", "\n".join(log.output))

    def test_a_malformed_field_from_redis_is_removed(self) -> None:
        objekt: dict = {
            "name": "Novemberereignisse", "akut": True, "gedeckt": {}, "offen": [],
            "zeitbezug": {**_NOVEMBER, "bis": "2026-10-01"},
        }
        with self.assertLogs(_TIME_REFERENCE_LOGGER, level="ERROR"):
            normalize_object_form(objekt, from_model=False)

        self.assertNotIn("zeitbezug", objekt)

    def test_twin_a_wellformed_field_passes_silently(self) -> None:
        with self.assertNoLogs(_TIME_REFERENCE_LOGGER, level="ERROR"):
            checked: dict | None = checked_time_reference(dict(_NOVEMBER), "Novemberereignisse")
        self.assertEqual(checked, _NOVEMBER)


class MidnightTest(unittest.TestCase):
    """Zeuge 7: Ein Feld von vor Mitternacht liest danach denselben Zeitraum."""

    _BEFORE: datetime = datetime(2026, 10, 31, 23, 50, tzinfo=BERLIN)
    _AFTER: datetime = datetime(2026, 11, 1, 0, 10, tzinfo=BERLIN)

    def test_next_month_set_on_october_31_still_reads_november(self) -> None:
        artefakt: dict = carry_time_references(
            _parse("Monatsplanung"), None, "Was ist nächsten Monat?", self._BEFORE,
        )
        window = time_reference_window(artefakt["objekte"][0], self._AFTER, 3)

        self.assertEqual(window.kind, KIND_RANGE)
        self.assertEqual(
            (window.start, window.end),
            (datetime(2026, 11, 1, 0, 0, tzinfo=BERLIN),
             datetime(2026, 11, 30, 23, 59, 59, tzinfo=BERLIN)),
        )

    def test_twin_derived_anew_on_november_1_it_would_be_december(self) -> None:
        """Der Unterschied, den der Zeuge oben bewacht: neu gerechnet waere es der Dezember."""
        anew: dict = derive_time_reference(
            "Monatsplanung", "Was ist nächsten Monat?", self._AFTER.date(),
        )

        self.assertEqual((anew["von"], anew["bis"]), ("2026-12-01", "2026-12-31"))


class ImportTest(unittest.TestCase):
    """Zeuge 8: Das Modul ist Geschaeftsablauf und importiert kein Werkzeug."""

    @staticmethod
    def _modules() -> set[str]:
        """Die Module, aus denen `sachlage_zeitbezug.py` importiert."""
        path: Path = SERVER_ROOT / "graph" / "nodes" / "sachlage_zeitbezug.py"
        tree: ast.Module = ast.parse(path.read_text(encoding="utf-8"))
        modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
            elif isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
        return modules

    def test_no_import_from_tools(self) -> None:
        self.assertEqual({m for m in self._modules() if m.split(".")[0] == "tools"}, set())

    def test_twin_the_parser_is_seen(self) -> None:
        self.assertIn("utils.zeitparser", self._modules())


class NoReferenceNoWindowTest(_SeededTest):
    """Zeuge 9: Ohne Zeitbezug oeffnet das Angebot kein Kalenderfenster."""

    def test_an_acute_november_without_the_field_reads_nothing(self) -> None:
        previous: dict = {"objekte": [{"name": "November", "akut": True}]}
        with patch("graph.nodes.sachlage_resolver.read_appointments") as reading:
            hits: list[MemoryHit] = _calendar(previous)

        self.assertEqual(hits, [])
        reading.assert_not_called()

    def test_twin_with_the_field_the_appointments_are_offered(self) -> None:
        previous: dict = {"objekte": [
            {"name": "November", "akut": True, "zeitbezug": dict(_NOVEMBER)},
        ]}

        hits: list[MemoryHit] = _calendar(previous)
        self.assertEqual([h.origin for h in hits], [f"timeline#{i}" for i in self.november])


class DerivationTest(unittest.TestCase):
    """Die Ableitung an den Raendern: Fuge, Tippfehlerkorrektur, Zeitwort."""

    def test_the_weekend_is_found_through_its_stem(self) -> None:
        reference: dict | None = derive_time_reference(
            "Wochenendplanung", "Habe ich am Wochenende schon etwas geplant?", TODAY,
        )

        self.assertEqual(
            reference,
            {"art": "zeitraum", "von": "2026-10-17", "bis": "2026-10-18",
             "wortlaut": "am Wochenende"},
        )

    def test_a_corrected_filler_carries_no_period(self) -> None:
        """*was* wird im Zeitparser zu *Mai*; *Washington* traegt deshalb keinen Mai."""
        self.assertIsNone(derive_time_reference("Washington", "Was macht Merten?", TODAY))

    def test_twin_a_real_month_name_carries_its_period(self) -> None:
        self.assertEqual(
            derive_time_reference("Maifeier", "Was steht im Mai an?", TODAY),
            {"art": "zeitraum", "von": "2026-05-01", "bis": "2026-05-31", "wortlaut": "im Mai"},
        )

    def test_a_time_word_is_no_title(self) -> None:
        """Die Frage nach dem Zeitpunkt steht da: *morgen* scheitert am Zeitwort, nicht an ihr."""
        self.assertIsNone(
            derive_time_reference("Morgenroutine", "Wann bin ich morgen frei?", TODAY),
        )

    def test_twin_another_word_of_the_name_is_a_title(self) -> None:
        self.assertEqual(
            derive_time_reference("Morgenroutine", "Wann beginnt die Routine?", TODAY),
            {"art": "titel", "stichwort": "Routine", "wortlaut": "Routine"},
        )

    def test_a_latent_object_carries_no_field(self) -> None:
        artefakt: dict = _parse("Novemberereignisse")
        artefakt["objekte"][0]["akut"] = False
        carry_time_references(artefakt, None, "Was steht im November an?", NOW)

        self.assertNotIn("zeitbezug", artefakt["objekte"][0])


class TimeQuestionTest(unittest.TestCase):
    """Zeuge 10: Ein Titel entsteht nur aus einer Frage nach dem Zeitpunkt der Sache.

    Den Namen nimmt das Modell meist aus der Aeusserung. Ohne die Frage traege
    deshalb jede Aussage einen Titel, und im Folgeturn oeffnete er ein Fenster.
    Jeder Fall hier ergab vor der Regel einen Titel: Das Wort steht im Namen.
    """

    #: (Name, Aeusserung ohne Zeitfrage, dieselbe Sache mit Zeitfrage, Stichwort)
    _CASES: tuple[tuple[str, str, str, str], ...] = (
        ("Fahrradreparatur", "Morgen bringe ich das Fahrrad zur Werkstatt.",
         "Wann bringe ich das Fahrrad zur Werkstatt?", "Fahrrad"),
        ("Kometenbuch", "Ich lese gerade ein Buch über Kometen.",
         "Wann kommt das Buch über Kometen?", "Kometen"),
        ("Montierung", "Was kostet eine neue Montierung?",
         "Wann wird die neue Montierung geliefert?", "Montierung"),
        ("Morgenroutine", "Wie lange dauert die Routine?",
         "Um wie viel Uhr beginnt die Routine?", "Routine"),
    )

    def test_a_sentence_without_a_time_question_gets_no_field(self) -> None:
        for name, statement, _, _ in self._CASES:
            with self.subTest(aeusserung=statement):
                self.assertIsNone(derive_time_reference(name, statement, TODAY))

    def test_without_a_time_question_the_acute_object_carries_none(self) -> None:
        """Verdrahtung: derselbe Satz durch `_derive` laesst das Objekt ohne Feld."""
        artefakt, _ = _turn(None, "Morgen bringe ich das Fahrrad zur Werkstatt.",
                            _parse("Fahrradreparatur"))

        self.assertNotIn("zeitbezug", artefakt["objekte"][0])

    def test_twin_the_same_matter_asked_for_its_time_is_a_title(self) -> None:
        for name, _, question, keyword in self._CASES:
            with self.subTest(aeusserung=question):
                self.assertEqual(
                    derive_time_reference(name, question, TODAY),
                    {"art": "titel", "stichwort": keyword, "wortlaut": keyword},
                )

    def test_twin_through_derive_the_acute_object_carries_the_title(self) -> None:
        artefakt, _ = _turn(None, "Wann bringe ich das Fahrrad zur Werkstatt?",
                            _parse("Fahrradreparatur"))

        self.assertEqual(
            artefakt["objekte"][0]["zeitbezug"],
            {"art": "titel", "stichwort": "Fahrrad", "wortlaut": "Fahrrad"},
        )


if __name__ == "__main__":
    unittest.main()
