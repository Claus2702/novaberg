"""Zeugen dafuer, dass ein gefundener Termin nur die Behauptung deckt, die ihn nennt.

Ziel: Steht der akute Termin der Lage im Bestand, bleibt eine Speicherbehauptung
ohne abgeschlossenen Dienst nur dann unkorrigiert, wenn ihr Satz diesen Termin
unterscheidend nennt — seine Uhrzeit oder ein Titelwort, das mehr sagt als die
Art des Eintrags; ein Tag zaehlt nur zusammen mit einem von beiden. Ein Satz
ueber etwas anderes (*„notiert, dass der Ersatzschluessel beim Nachbarn
liegt"*, *„notiert, dass du morgen Mehl kaufen willst"*) wird korrigiert, und
der Ausgang `gefunden_nicht_genannt` steht im dauerhaften Eintrag.

**Ohne Datenbank, Netz und Modell:** Ersetzt ist nur der Lesezugriff
`TimelineRepository.find_by_date_range`, durch eine Attrappe, die wie die
Abfrage nach dem Zeitraum filtert; die Auswahl dahinter laeuft echt. Die
Beispiele sind nachgebildet aus einer Simulation an einem Pruef-Nutzer, nicht
aus dem Bestand eines Menschen; Tag und Titel sind erfunden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import date, datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from config import TIMEZONE
from memory.repositories.timeline_repository import TimelineRepository
from utils.storage_claims import ORDER_HEADER
from utils.storage_inventory import TitleWords, names_appointment, title_words

_TZ = ZoneInfo(TIMEZONE)
_USER: str = "zeuge-bestandsbezug"
_CHARACTER: str = "nova"

#: Der akute Termin der Lage: Mittwoch, 17.11.2027, 11:00.
_MOMENT: datetime = datetime(2027, 11, 17, 11, 0, tzinfo=_TZ)
_SITUATION: dict = {
    "herkunft": "frisch",
    "objekte": [{
        "name": "Termin beim Zahnarzt", "klasse": "vorgang", "akut": True,
        "gedeckt": {"Wann": "17.11.2027 um 11:00 Uhr"}, "offen": [],
    }],
}

_UNRELATED: str = "Alles klar! Ich habe mir notiert, dass der Ersatzschlüssel beim Nachbarn liegt."
_REPETITION: str = "Der Zahnarzt um 11 Uhr ist eingetragen."
_BY_NAME: str = "Dr. Berger morgen um elf ist eingetragen."

_DAY_ONLY: str = "Ich habe notiert, dass du morgen Mehl kaufen willst."
_KIND_ONLY: str = "Ich habe den Termin beim Friseur eingetragen."

_NONE: frozenset[str] = frozenset()
_WORDS: TitleWords = (frozenset({"zahnarzt", "berger"}), _NONE)
_TODAY: date = date(2027, 11, 16)
#: Der Turn laeuft am Vortag des Termins: *morgen* ist der 17.11.2027.
_NOW: datetime = datetime(2027, 11, 16, 9, 0, tzinfo=_TZ)


def _row(title: object = "Termin beim Zahnarzt", event_type: object = "termin") -> dict:
    """Der erfundene Timeline-Eintrag zum akuten Termin der Lage."""
    return {
        "id": 1100,
        "user_id": _USER,
        "character_id": _CHARACTER,
        "title": title,
        "event_type": event_type,
        "precision": "minute",
        "aktiv": True,
        "event_time": _MOMENT,
    }


class _Inventory:
    """Die Attrappe des Lesezugriffs: filtert ihre Zeilen nach dem Zeitraum wie die Abfrage."""

    def __init__(self, rows: list) -> None:
        self.rows = rows
        self.calls: list[tuple] = []

    def __call__(
        self, url: str, user_id: str, character_id: str, start: datetime, end: datetime,
    ) -> list:
        self.calls.append((user_id, character_id, start, end))
        return [r for r in self.rows if start <= r["event_time"] <= end]


class NamingInStorageStepTest(unittest.TestCase):
    """Am Schritt, der ueber die Korrektur entscheidet: Bestand allein deckt nicht."""

    def _step(self, response: str, rows: list) -> tuple[dict, list[str], dict]:
        """Ruft den Schritt mit Urteil `ok`, ohne Dienst, am 16.11.2027.

        Liefert Zustand, Auftraege und dauerhaften Eintrag.
        """
        from graph.nodes import tribunal
        state: dict = {
            "turn_id": "zeuge", "user_id": _USER, "character_id": _CHARACTER,
            "response": response, "agent_results": [],
            "correction_round": 0, "max_corrections": 2, "tribunal_verdict": "ok",
            "sachlage": _SITUATION,
        }
        feedback: list[str] = []
        inventory: _Inventory = _Inventory(rows)
        with patch.object(TimelineRepository, "find_by_date_range", side_effect=inventory), \
                patch.object(tribunal, "now_local", return_value=_NOW), \
                patch.object(tribunal, "log_berechnung") as record:
            tribunal._storage_claim_step(state, feedback)
        self.assertEqual(record.call_count, 1)
        return state, feedback, record.call_args.kwargs["inhalt"]

    def test_unrelated_claim_is_corrected_despite_found_appointment(self) -> None:
        """Der Termin steht im Bestand, der Satz spricht von etwas anderem."""
        state, feedback, entry = self._step(_UNRELATED, [_row()])
        self.assertEqual(entry["befunde"], [{"form": "erste_person", "wort": "notiert"}])
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))
        self.assertEqual(entry["bestandsabgleich"], "gefunden_nicht_genannt")
        self.assertEqual(entry["abgleich_zeitpunkte"], 1)
        self.assertTrue(entry["urteil_gehoben"])

    def test_unrelated_claim_without_appointment_stays_not_found(self) -> None:
        """Der Zwilling: ohne Termin im Bestand bleibt der Ausgang der alte."""
        state, _, entry = self._step(_UNRELATED, [])
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertEqual(entry["bestandsabgleich"], "nicht_gefunden")

    def test_repetition_naming_kind_and_clock_stays(self) -> None:
        state, feedback, entry = self._step(_REPETITION, [_row()])
        self.assertEqual(len(entry["befunde"]), 1)
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(feedback, [])
        self.assertEqual(entry["bestandsabgleich"], "gefunden")
        self.assertFalse(entry["urteil_gehoben"])

    def test_name_instead_of_kind_stays(self) -> None:
        state, feedback, entry = self._step(_BY_NAME, [_row("Zahnarzt Dr. Berger")])
        self.assertEqual(len(entry["befunde"]), 1)
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(feedback, [])
        self.assertEqual(entry["bestandsabgleich"], "gefunden")

    def test_two_claims_one_unnamed_is_corrected(self) -> None:
        state, feedback, entry = self._step(f"{_REPETITION} {_UNRELATED}", [_row()])
        self.assertEqual(len(entry["befunde"]), 2)
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))
        self.assertEqual(entry["bestandsabgleich"], "gefunden_nicht_genannt")

    def test_two_claims_both_named_stay(self) -> None:
        """Der Zwilling: der zweite Satz nennt den Termin nur ueber den Namen."""
        response: str = f"{_REPETITION} Dr. Berger ist notiert."
        state, feedback, entry = self._step(response, [_row("Zahnarzt Dr. Berger")])
        self.assertEqual(len(entry["befunde"]), 2)
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(feedback, [])
        self.assertEqual(entry["bestandsabgleich"], "gefunden")

    def test_day_alone_is_corrected(self) -> None:
        """Der Termin liegt morgen, der Satz nennt nur *morgen* — und spricht von Mehl."""
        state, feedback, entry = self._step(_DAY_ONLY, [_row()])
        self.assertEqual(len(entry["befunde"]), 1)
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))
        self.assertEqual(entry["bestandsabgleich"], "gefunden_nicht_genannt")

    def test_day_with_clock_time_stays(self) -> None:
        """Der Zwilling: derselbe Tag mit der Uhrzeit des Termins."""
        state, feedback, entry = self._step("Morgen um 11 ist eingetragen.", [_row()])
        self.assertEqual(len(entry["befunde"]), 1)
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(feedback, [])
        self.assertEqual(entry["bestandsabgleich"], "gefunden")

    def test_day_with_title_word_stays(self) -> None:
        """Der Zwilling: derselbe Tag mit einem unterscheidenden Wort des Titels."""
        state, feedback, entry = self._step("Der Zahnarzt morgen ist eingetragen.", [_row()])
        self.assertEqual(len(entry["befunde"]), 1)
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(feedback, [])
        self.assertEqual(entry["bestandsabgleich"], "gefunden")

    def test_kind_word_alone_is_corrected(self) -> None:
        """*Termin* steht im Titel und im Satz — der Satz spricht vom Friseur."""
        state, feedback, entry = self._step(_KIND_ONLY, [_row()])
        self.assertEqual(len(entry["befunde"]), 1)
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))
        self.assertEqual(entry["bestandsabgleich"], "gefunden_nicht_genannt")

    def test_weekday_in_the_title_is_corrected(self) -> None:
        """*Mittwoch* steht im Titel und im Satz — der Satz spricht von Mehl."""
        sentence: str = "Ich habe notiert, dass du Mittwoch Mehl kaufen willst."
        state, feedback, entry = self._step(sentence, [_row("Yoga Mittwoch")])
        self.assertEqual(len(entry["befunde"]), 1)
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))
        self.assertEqual(entry["bestandsabgleich"], "gefunden_nicht_genannt")

    def test_other_word_of_that_title_stays(self) -> None:
        """Der Zwilling: derselbe Titel, der Satz nennt sein anderes Wort."""
        state, feedback, entry = self._step("Yoga ist eingetragen.", [_row("Yoga Mittwoch")])
        self.assertEqual(len(entry["befunde"]), 1)
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(feedback, [])
        self.assertEqual(entry["bestandsabgleich"], "gefunden")

    def test_weekday_starting_a_title_word_is_corrected(self) -> None:
        """*Sonntagsbrunch* beginnt mit *Sonntag* — der Satz nennt nur den Tag."""
        sentence: str = "Ich habe notiert, dass du am Sonntag Mehl kaufen willst."
        state, feedback, entry = self._step(sentence, [_row("Sonntagsbrunch")])
        self.assertEqual(len(entry["befunde"]), 1)
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))
        self.assertEqual(entry["bestandsabgleich"], "gefunden_nicht_genannt")

    def test_compound_with_the_weekday_stays(self) -> None:
        """Der Zwilling: das Kompositum im Satz ist kein Tageswort und traegt."""
        response: str = "Der Sonntagsbrunch ist eingetragen."
        state, feedback, entry = self._step(response, [_row("Sonntagsbrunch")])
        self.assertEqual(len(entry["befunde"]), 1)
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(feedback, [])
        self.assertEqual(entry["bestandsabgleich"], "gefunden")


class NamingInEvaluateTest(unittest.TestCase):
    """Die Verdrahtung bis zur Zusammenfassung, die der Corrector liest."""

    def test_unrelated_claim_reaches_the_summary(self) -> None:
        from graph.nodes import tribunal
        state: dict = {
            "turn_id": "zeuge", "user_id": _USER, "character_id": _CHARACTER,
            "response": _UNRELATED, "agent_results": [],
            "correction_round": 0, "max_corrections": 2, "sachlage": _SITUATION,
            "tribunal_votes": [
                {"agent": a, "vote": "ok", "reasoning": ""}
                for a in ("jurist", "psychologe", "ethik")
            ],
        }
        inventory: _Inventory = _Inventory([_row()])
        with patch.object(TimelineRepository, "find_by_date_range", side_effect=inventory), \
                patch.object(tribunal, "log_berechnung"), \
                self.assertLogs("ki_server.tribunal", level="ERROR"):
            state = tribunal.evaluate(state)
        self.assertTrue(state["tribunal_summary"].startswith(ORDER_HEADER))


class NamesAppointmentTest(unittest.TestCase):
    """Die Zulassung je Weg: ein Satz, der nur diesen Weg traegt, und sein Zwilling."""

    def _ways(self, sentence: str, today: date = _TODAY) -> tuple[str, ...]:
        return names_appointment(sentence, _MOMENT, _WORDS, today)

    def test_clock_time(self) -> None:
        self.assertEqual(self._ways("Um 11 Uhr ist es eingetragen."), ("uhrzeit",))
        self.assertEqual(self._ways("Um 12 Uhr ist es eingetragen."), ())

    def test_clock_time_as_word(self) -> None:
        self.assertEqual(self._ways("Um elf ist es eingetragen."), ("uhrzeit",))
        self.assertEqual(self._ways("Um zehn ist es eingetragen."), ())

    def test_day_in_digits(self) -> None:
        """Der Tag allein nennt nichts; mit der Uhrzeit steht er neben ihr."""
        self.assertEqual(self._ways("Am 17.11. ist es eingetragen."), ())
        self.assertEqual(self._ways("Am 17.11. um 11 Uhr ist es eingetragen."), ("uhrzeit", "tag"))
        self.assertEqual(self._ways("Am 18.11. um 11 Uhr ist es eingetragen."), ("uhrzeit",))

    def test_weekday(self) -> None:
        """Der Wochentag allein nennt nichts; mit einem Titelwort steht er neben ihm."""
        self.assertEqual(self._ways("Mittwoch ist eingetragen."), ())
        self.assertEqual(self._ways("Der Zahnarzt am Mittwoch ist eingetragen."), ("tag", "titel"))
        self.assertEqual(self._ways("Der Zahnarzt am Donnerstag ist eingetragen."), ("titel",))

    def test_tomorrow_counts_from_today(self) -> None:
        """*Morgen* allein nennt nichts; mit der Uhrzeit zaehlt es vom heutigen Tag aus."""
        self.assertEqual(self._ways("Morgen ist es eingetragen."), ())
        self.assertEqual(self._ways("Morgen um 11 ist es eingetragen."), ("uhrzeit", "tag"))
        self.assertEqual(
            self._ways("Morgen um 11 ist es eingetragen.", today=date(2027, 11, 15)), ("uhrzeit",)
        )

    def test_kind_word_does_not_name(self) -> None:
        """*Termin* ist die Art des Eintrags — erst *Zahnarzt* unterscheidet ihn."""
        words: TitleWords = title_words([_row("Termin beim Zahnarzt")])
        ways: tuple[str, ...] = names_appointment(_KIND_ONLY, _MOMENT, words, _TODAY)
        self.assertEqual(ways, ())
        ways = names_appointment(
            "Ich habe den Termin beim Zahnarzt eingetragen.", _MOMENT, words, _TODAY
        )
        self.assertEqual(ways, ("titel",))

    def test_short_sentence_word_does_not_start_a_title_word(self) -> None:
        """*Klar* am Satzanfang ist kein *Klarinettenunterricht*; *Zahnarzt* bleibt einer."""
        lesson: TitleWords = (frozenset({"klarinettenunterricht"}), _NONE)
        self.assertEqual(names_appointment("Klar, notiert.", _MOMENT, lesson, _TODAY), ())
        compound: TitleWords = (frozenset({"zahnarzttermin"}), _NONE)
        ways: tuple[str, ...] = names_appointment(
            "Zahnarzt ist eingetragen.", _MOMENT, compound, _TODAY
        )
        self.assertEqual(ways, ("titel",))

    def test_reverse_prefix_from_seven_letters(self) -> None:
        """Die Grenze der Gegenrichtung: sechs Buchstaben tragen nicht, sieben schon."""
        physio: TitleWords = (frozenset({"physiotherapie"}), _NONE)
        self.assertEqual(names_appointment("Physio ist eingetragen.", _MOMENT, physio, _TODAY), ())
        hair: TitleWords = (frozenset({"friseurbesuch"}), _NONE)
        ways: tuple[str, ...] = names_appointment(
            "Friseur ist eingetragen.", _MOMENT, hair, _TODAY
        )
        self.assertEqual(ways, ("titel",))

    def test_cut_title_word_names_as_a_whole(self) -> None:
        """*Terminabsprache* im Satz nennt *„Terminabsprache"*; *Termin* allein nicht."""
        words: TitleWords = title_words([_row("Terminabsprache")])
        ways: tuple[str, ...] = names_appointment(
            "Die Terminabsprache ist eingetragen.", _MOMENT, words, _TODAY
        )
        self.assertEqual(ways, ("titel",))
        ways = names_appointment("Der Termin ist eingetragen.", _MOMENT, words, _TODAY)
        self.assertEqual(ways, ())

    def test_linking_s_falls_with_the_kind(self) -> None:
        """*Feier* nennt *„Geburtstagsfeier"* der Art `geburtstag`, *Geburtstag* nicht."""
        words: TitleWords = title_words([_row("Geburtstagsfeier", event_type="geburtstag")])
        ways: tuple[str, ...] = names_appointment(
            "Die Feier ist eingetragen.", _MOMENT, words, _TODAY
        )
        self.assertEqual(ways, ("titel",))
        ways = names_appointment("Der Geburtstag ist eingetragen.", _MOMENT, words, _TODAY)
        self.assertEqual(ways, ())

    def test_name_from_the_title(self) -> None:
        self.assertEqual(self._ways("Dr. Berger ist eingetragen."), ("titel",))
        self.assertEqual(self._ways("Herr Krause ist eingetragen."), ())

    def test_title_word_inflected_or_compounded(self) -> None:
        self.assertEqual(self._ways("Der Zahnarzttermin ist eingetragen."), ("titel",))
        compound: TitleWords = (frozenset({"zahnarzttermin"}), _NONE)
        ways: tuple[str, ...] = names_appointment(
            "Der Zahnarzt ist eingetragen.", _MOMENT, compound, _TODAY
        )
        self.assertEqual(ways, ("titel",))

    def test_unrelated_sentence_names_nothing(self) -> None:
        self.assertEqual(self._ways(_UNRELATED), ())

    def test_naive_moment_raises(self) -> None:
        with self.assertRaises(ValueError):
            names_appointment(_REPETITION, datetime(2027, 11, 17, 11, 0), _WORDS, _TODAY)


class TitleWordsTest(unittest.TestCase):
    """Die Woerter des Titels: gross, mindestens vier Buchstaben, ohne die Art des Eintrags."""

    def test_content_words_of_the_title(self) -> None:
        self.assertEqual(
            title_words([_row("Zahnarzt Dr. Berger")]),
            (frozenset({"zahnarzt", "berger"}), _NONE),
        )
        self.assertEqual(
            title_words([_row("Termin beim Zahnarzt")]), (frozenset({"zahnarzt"}), _NONE)
        )

    def test_kind_leaves_compounds(self) -> None:
        """Endet oder beginnt ein Titelwort mit der Art, bleibt der Rest — und das ganze Wort."""
        self.assertEqual(
            title_words([_row("Zahnarzttermin")]),
            (frozenset({"zahnarzt"}), frozenset({"zahnarzttermin"})),
        )
        self.assertEqual(
            title_words([_row("Terminabsprache Bank")]),
            (frozenset({"absprache", "bank"}), frozenset({"terminabsprache"})),
        )
        self.assertEqual(title_words([_row("Termine")]), (_NONE, _NONE))

    def test_linking_s_is_cut_with_the_kind(self) -> None:
        """Ein Fugen-s faellt mit der Art, vorn wie hinten — solange vier Buchstaben bleiben."""
        self.assertEqual(
            title_words([_row("Geburtstagsfeier", event_type="geburtstag")]),
            (frozenset({"feier"}), frozenset({"geburtstagsfeier"})),
        )
        self.assertEqual(
            title_words([_row("Arbeitstermin")]),
            (frozenset({"arbeit"}), frozenset({"arbeitstermin"})),
        )
        self.assertEqual(
            title_words([_row("Haustermin")]), (frozenset({"haus"}), frozenset({"haustermin"}))
        )

    def test_kind_is_read_from_the_row(self) -> None:
        """Dieselben Titel, andere Art: Gestrichen wird die Art der Zeile, keine feste Liste."""
        self.assertEqual(
            title_words([_row("Geburtstag Mama", event_type="geburtstag")]),
            (frozenset({"mama"}), _NONE),
        )
        self.assertEqual(
            title_words([_row("Geburtstag Mama", event_type="termin")]),
            (frozenset({"geburtstag", "mama"}), _NONE),
        )

    def test_title_that_is_no_text_is_loud(self) -> None:
        """Der Zwilling zu oben: dieselbe Zeile ohne Text als Titel."""
        with self.assertLogs("ki_server.storage_inventory", level="ERROR"):
            self.assertEqual(title_words([_row(None)]), (_NONE, _NONE))

    def test_row_without_kind_is_loud(self) -> None:
        """Ohne Art ist nicht zu sagen, was unterscheidet — die Zeile traegt kein Wort."""
        with self.assertLogs("ki_server.storage_inventory", level="ERROR"):
            self.assertEqual(title_words([_row(event_type=None)]), (_NONE, _NONE))


if __name__ == "__main__":
    unittest.main()
