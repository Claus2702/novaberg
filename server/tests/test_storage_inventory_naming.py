"""Zeugen dafuer, dass ein gefundener Termin nur die Behauptung deckt, die ihn nennt.

Ziel: Steht der akute Termin der Lage im Bestand, bleibt eine Speicherbehauptung
ohne abgeschlossenen Dienst nur dann unkorrigiert, wenn ihr Satz diesen Termin
nennt — seine Uhrzeit, seinen Tag oder ein Inhaltswort seines Titels. Ein Satz
ueber etwas anderes (*„notiert, dass der Ersatzschluessel beim Nachbarn
liegt"*) wird korrigiert, und der Ausgang `gefunden_nicht_genannt` steht im
dauerhaften Eintrag.

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
from utils.storage_inventory import names_appointment, title_words

_TZ = ZoneInfo(TIMEZONE)
_USER: str = "zeuge-bestandsbezug"

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

_WORDS: frozenset[str] = frozenset({"zahnarzt", "berger"})
_TODAY: date = date(2027, 11, 16)


def _row(title: object = "Termin beim Zahnarzt") -> dict:
    """Der erfundene Timeline-Eintrag zum akuten Termin der Lage."""
    return {
        "id": 1100,
        "user_id": _USER,
        "title": title,
        "event_type": "termin",
        "precision": "minute",
        "aktiv": True,
        "event_time": _MOMENT,
    }


class _Inventory:
    """Die Attrappe des Lesezugriffs: filtert ihre Zeilen nach dem Zeitraum wie die Abfrage."""

    def __init__(self, rows: list) -> None:
        self.rows = rows
        self.calls: list[tuple] = []

    def __call__(self, url: str, user_id: str, start: datetime, end: datetime) -> list:
        self.calls.append((user_id, start, end))
        return [r for r in self.rows if start <= r["event_time"] <= end]


class NamingInStorageStepTest(unittest.TestCase):
    """Am Schritt, der ueber die Korrektur entscheidet: Bestand allein deckt nicht."""

    def _step(self, response: str, rows: list) -> tuple[dict, list[str], dict]:
        """Ruft den Schritt mit Urteil `ok`, ohne Dienst; liefert Zustand, Auftraege, Eintrag."""
        from graph.nodes import tribunal
        state: dict = {
            "turn_id": "zeuge", "user_id": _USER, "response": response, "agent_results": [],
            "correction_round": 0, "max_corrections": 2, "tribunal_verdict": "ok",
            "sachlage": _SITUATION,
        }
        feedback: list[str] = []
        inventory: _Inventory = _Inventory(rows)
        with patch.object(TimelineRepository, "find_by_date_range", side_effect=inventory), \
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


class NamingInEvaluateTest(unittest.TestCase):
    """Die Verdrahtung bis zur Zusammenfassung, die der Corrector liest."""

    def test_unrelated_claim_reaches_the_summary(self) -> None:
        from graph.nodes import tribunal
        state: dict = {
            "turn_id": "zeuge", "user_id": _USER, "response": _UNRELATED, "agent_results": [],
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
        self.assertEqual(self._ways("Am 17.11. ist es eingetragen."), ("tag",))
        self.assertEqual(self._ways("Am 18.11. ist es eingetragen."), ())

    def test_weekday(self) -> None:
        self.assertEqual(self._ways("Mittwoch ist eingetragen."), ("tag",))
        self.assertEqual(self._ways("Donnerstag ist eingetragen."), ())

    def test_tomorrow_counts_from_today(self) -> None:
        self.assertEqual(self._ways("Morgen ist es eingetragen."), ("tag",))
        self.assertEqual(self._ways("Morgen ist es eingetragen.", today=date(2027, 11, 15)), ())

    def test_name_from_the_title(self) -> None:
        self.assertEqual(self._ways("Dr. Berger ist eingetragen."), ("titel",))
        self.assertEqual(self._ways("Herr Krause ist eingetragen."), ())

    def test_title_word_inflected_or_compounded(self) -> None:
        self.assertEqual(self._ways("Der Zahnarzttermin ist eingetragen."), ("titel",))
        compound: frozenset[str] = frozenset({"zahnarzttermin"})
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
    """Die Woerter des Titels: gross, mindestens vier Buchstaben."""

    def test_content_words_of_the_title(self) -> None:
        self.assertEqual(
            title_words([_row("Zahnarzt Dr. Berger")]), frozenset({"zahnarzt", "berger"})
        )
        self.assertEqual(
            title_words([_row("Termin beim Zahnarzt")]), frozenset({"termin", "zahnarzt"})
        )

    def test_title_that_is_no_text_is_loud(self) -> None:
        """Der Zwilling zu oben: dieselbe Zeile ohne Text als Titel."""
        with self.assertLogs("ki_server.storage_inventory", level="ERROR"):
            self.assertEqual(title_words([_row(None)]), frozenset())


if __name__ == "__main__":
    unittest.main()
