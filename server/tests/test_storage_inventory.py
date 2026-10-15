"""Zeugen dafuer, dass eine wahre Wiederholung unkorrigiert bleibt.

Ziel: Behauptet die Antwort eine Speicherung, ohne dass ein Dienst dieses Turns
`abgeschlossen` meldet, fragt der Riegel vor der Korrektur die Timeline mit Tag
und Uhrzeit des akuten Objekts der Lage. Steht dort ein aktiver Termin zu genau
dieser Zeit, kein Erinnerungs-Anker, bleibt das Urteil und es gibt weder
Korrekturauftrag noch Korrektursatz. Fehlt der Termin, fehlt das akute Objekt
mit Tag und Uhrzeit, oder scheitert die Abfrage, wird korrigiert wie ohne
Abgleich — und der Ausgang steht im dauerhaften Eintrag.

**Ohne Datenbank:** Ersetzt ist nur der Lesezugriff
`TimelineRepository.find_by_date_range`, durch eine Attrappe, die wie die
Abfrage nach dem Zeitraum filtert. Die Auswahl dahinter — Uhrzeit, Anker,
Genauigkeit — laeuft echt. Termine und Lage sind erfunden, kein Wortlaut aus
einem Gespraech.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from config import TIMEZONE
from memory.repositories.timeline_repository import TimelineRepository
from memory.timeline_inventory import (
    ANCHOR_TYPE,
    TIME_PRECISIONS,
    find_at_moment,
    is_appointment_at,
)
from utils.storage_claims import CORRECTION_NOTE, ORDER_HEADER
from utils.storage_inventory import FALLBACK_ORIGIN, acute_moments, object_moment

_TZ = ZoneInfo(TIMEZONE)
_CLAIM: str = "Morgen um 10 Uhr ist notiert."
_USER: str = "zeuge-bestandsabgleich"


def _row(
    hour: int, minute: int = 0, day: int = 17,
    event_type: str = "termin", precision: str = "minute",
) -> dict:
    """Ein erfundener Timeline-Eintrag im November 2027, lokal und zeitzonenbewusst."""
    return {
        "id": hour * 100 + minute,
        "user_id": _USER,
        "title": "Probetermin",
        "event_type": event_type,
        "precision": precision,
        "aktiv": True,
        "event_time": datetime(2027, 11, day, hour, minute, tzinfo=_TZ),
    }


def _situation(*gedeckt: dict, akut: bool = True, herkunft: str = "frisch") -> dict:
    """Eine erfundene Lage mit je einem Objekt pro `gedeckt`."""
    return {
        "herkunft": herkunft,
        "objekte": [
            {"name": f"Sache {i}", "klasse": "vorgang", "akut": akut, "gedeckt": g, "offen": []}
            for i, g in enumerate(gedeckt)
        ],
    }


_ON_17TH_AT_10: dict = {"Tag": "17.11.2027", "Uhrzeit": "10 Uhr"}


class _Inventory:
    """Die Attrappe des Lesezugriffs: filtert ihre Zeilen nach dem Zeitraum wie die Abfrage."""

    def __init__(self, rows: list, error: Exception | None = None) -> None:
        self.rows = rows
        self.error = error
        self.calls: list[tuple] = []

    def __call__(self, url: str, user_id: str, start: datetime, end: datetime) -> list:
        self.calls.append((user_id, start, end))
        if self.error is not None:
            raise self.error
        return [r for r in self.rows if not isinstance(r, dict) or start <= r["event_time"] <= end]


class InventoryInStorageStepTest(unittest.TestCase):
    """Die Zeugen an `_storage_claim_step` — dort entscheidet sich, ob korrigiert wird."""

    def _step(
        self, situation: dict | None, inventory: _Inventory, correction_round: int = 0,
    ) -> tuple[dict, list[str], dict]:
        """Ruft den Schritt mit Urteil `ok` und ohne Dienst; liefert Zustand, Auftraege, Eintrag."""
        from graph.nodes import tribunal
        state: dict = {
            "turn_id":          "zeuge",
            "user_id":          _USER,
            "response":         _CLAIM,
            "agent_results":    [],
            "correction_round": correction_round,
            "max_corrections":  2,
            "tribunal_verdict": "ok",
        }
        if situation is not None:
            state["sachlage"] = situation
        feedback: list[str] = []
        with patch.object(TimelineRepository, "find_by_date_range", side_effect=inventory), \
                patch.object(tribunal, "log_berechnung") as record:
            tribunal._storage_claim_step(state, feedback)
        self.assertEqual(record.call_count, 1)
        return state, feedback, record.call_args.kwargs["inhalt"]

    def test_repetition_in_inventory_keeps_the_verdict(self) -> None:
        inventory = _Inventory([_row(10)])
        state, feedback, entry = self._step(_situation(_ON_17TH_AT_10), inventory)
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(feedback, [])
        self.assertEqual(entry["bestandsabgleich"], "gefunden")
        self.assertEqual(entry["abgleich_zeitpunkte"], 1)
        self.assertFalse(entry["urteil_gehoben"])
        # Gezaehlt wie die Nulllinie: kein Dienst hat gedeckt.
        self.assertEqual(entry["ergebnis"], "nicht_belegt")
        # Die Abfrage fragt den Tag des Objekts fuer diesen Nutzer.
        self.assertEqual(len(inventory.calls), 1)
        user_id, start, end = inventory.calls[0]
        self.assertEqual(user_id, _USER)
        self.assertEqual((start.date(), start.hour, end.date()), (datetime(2027, 11, 17).date(), 0,
                                                                  datetime(2027, 11, 17).date()))

    def test_repetition_in_the_last_round_gets_no_correction_note(self) -> None:
        state, _, _ = self._step(
            _situation(_ON_17TH_AT_10), _Inventory([_row(10)]), correction_round=2
        )
        self.assertEqual(state["response"], _CLAIM)
        self.assertNotIn(CORRECTION_NOTE, state["response"])

    def test_not_found_is_corrected(self) -> None:
        state, feedback, entry = self._step(_situation(_ON_17TH_AT_10), _Inventory([]))
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))
        self.assertEqual(entry["bestandsabgleich"], "nicht_gefunden")
        self.assertTrue(entry["urteil_gehoben"])

    def test_not_found_in_the_last_round_gets_the_correction_note(self) -> None:
        """Der Zwilling zum Zeugen ohne Korrektursatz: derselbe Weg, kein Treffer."""
        with self.assertLogs("ki_server.tribunal", level="ERROR"):
            state, _, _ = self._step(
                _situation(_ON_17TH_AT_10), _Inventory([]), correction_round=2
            )
        self.assertTrue(state["response"].endswith(CORRECTION_NOTE))

    def test_same_day_other_time_is_not_found(self) -> None:
        """Der Tag allein genuegt nicht — 10:30 ist eine andere Behauptung als 10:00."""
        inventory = _Inventory([_row(10, 30), _row(11)])
        state, _, entry = self._step(_situation(_ON_17TH_AT_10), inventory)
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertEqual(entry["bestandsabgleich"], "nicht_gefunden")

    def test_same_time_other_day_is_not_found(self) -> None:
        inventory = _Inventory([_row(10, day=18)])
        state, _, entry = self._step(_situation(_ON_17TH_AT_10), inventory)
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertEqual(entry["bestandsabgleich"], "nicht_gefunden")

    def test_only_a_reminder_anchor_is_not_found(self) -> None:
        inventory = _Inventory([_row(10, event_type=ANCHOR_TYPE)])
        state, feedback, entry = self._step(_situation(_ON_17TH_AT_10), inventory)
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))
        self.assertEqual(entry["bestandsabgleich"], "nicht_gefunden")

    def test_entry_without_clock_time_is_not_found(self) -> None:
        """Ein Eintrag mit Genauigkeit Tag traegt keine Uhrzeit, auch wenn er auf 10:00 steht."""
        inventory = _Inventory([_row(10, precision="day")])
        state, _, entry = self._step(_situation(_ON_17TH_AT_10), inventory)
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertEqual(entry["bestandsabgleich"], "nicht_gefunden")

    def test_acute_object_without_clock_time_is_corrected(self) -> None:
        inventory = _Inventory([_row(10)])
        state, feedback, entry = self._step(_situation({"Tag": "17.11.2027"}), inventory)
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))
        self.assertEqual(entry["bestandsabgleich"], "kein_akutes_objekt_mit_zeit")
        self.assertEqual(inventory.calls, [])

    def test_without_acute_object_is_corrected(self) -> None:
        for name, situation in (
            ("keine Lage", None),
            ("latentes Objekt", _situation(_ON_17TH_AT_10, akut=False)),
            ("Lage nach Ausfall", _situation(_ON_17TH_AT_10, herkunft=FALLBACK_ORIGIN)),
        ):
            with self.subTest(name):
                inventory = _Inventory([_row(10)])
                state, _, entry = self._step(situation, inventory)
                self.assertEqual(state["tribunal_verdict"], "warnung")
                self.assertEqual(entry["bestandsabgleich"], "kein_akutes_objekt_mit_zeit")
                self.assertEqual(inventory.calls, [])

    def test_failed_query_is_corrected_and_loud(self) -> None:
        inventory = _Inventory([_row(10)], error=RuntimeError("synthetischer Lesefehler"))
        with self.assertLogs("ki_server.tribunal", level="ERROR") as logs:
            state, feedback, entry = self._step(_situation(_ON_17TH_AT_10), inventory)
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))
        self.assertEqual(entry["bestandsabgleich"], "abfrage_gescheitert")
        self.assertEqual(entry["abgleich_fehler"], "RuntimeError")
        self.assertTrue(any("Bestandsabgleich gescheitert" in line for line in logs.output))

    def test_every_moment_must_be_found(self) -> None:
        """Zwei Termine in der Lage, einer im Bestand: welche Sache der Satz meint, ist offen."""
        situation = _situation(_ON_17TH_AT_10, {"Tag": "18.11.2027", "Uhrzeit": "15 Uhr"})
        state, _, entry = self._step(situation, _Inventory([_row(10)]))
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertEqual(entry["bestandsabgleich"], "nicht_gefunden")
        self.assertEqual(entry["abgleich_zeitpunkte"], 2)

    def test_every_moment_found_is_found(self) -> None:
        situation = _situation(_ON_17TH_AT_10, {"Tag": "18.11.2027", "Uhrzeit": "15 Uhr"})
        state, _, entry = self._step(situation, _Inventory([_row(10), _row(15, day=18)]))
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(entry["bestandsabgleich"], "gefunden")

    def test_completed_service_does_not_ask_the_inventory(self) -> None:
        from types import SimpleNamespace

        from graph.nodes import tribunal
        inventory = _Inventory([_row(10)])
        state: dict = {
            "turn_id": "zeuge", "user_id": _USER, "response": _CLAIM,
            "agent_results": [SimpleNamespace(agent_name="timeline", status="abgeschlossen")],
            "correction_round": 0, "max_corrections": 2, "tribunal_verdict": "ok",
            "sachlage": _situation(_ON_17TH_AT_10),
        }
        with patch.object(TimelineRepository, "find_by_date_range", side_effect=inventory), \
                patch.object(tribunal, "log_berechnung") as record:
            tribunal._storage_claim_step(state, [])
        self.assertEqual(inventory.calls, [])
        self.assertEqual(record.call_args.kwargs["inhalt"]["bestandsabgleich"], "nicht_gefragt")


class InventoryInEvaluateTest(unittest.TestCase):
    """Die Verdrahtung bis zur Zusammenfassung: eine Wiederholung meldet keinen Auftrag."""

    def _evaluate(self, inventory: _Inventory) -> dict:
        from graph.nodes import tribunal
        state: dict = {
            "turn_id": "zeuge", "user_id": _USER, "response": _CLAIM, "agent_results": [],
            "correction_round": 0, "max_corrections": 2,
            "sachlage": _situation(_ON_17TH_AT_10),
            "tribunal_votes": [
                {"agent": a, "vote": "ok", "reasoning": ""}
                for a in ("jurist", "psychologe", "ethik")
            ],
        }
        with patch.object(TimelineRepository, "find_by_date_range", side_effect=inventory), \
                patch.object(tribunal, "log_berechnung"):
            return tribunal.evaluate(state)

    def test_repetition_leaves_summary_empty_without_error(self) -> None:
        with self.assertNoLogs("ki_server.tribunal", level="ERROR"):
            state = self._evaluate(_Inventory([_row(10)]))
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(state["tribunal_summary"], "")

    def test_not_found_reaches_the_summary(self) -> None:
        with self.assertLogs("ki_server.tribunal", level="ERROR"):
            state = self._evaluate(_Inventory([]))
        self.assertTrue(state["tribunal_summary"].startswith(ORDER_HEADER))


class MomentFromLageTest(unittest.TestCase):
    """Tag und Uhrzeit kommen aus dem Zeitparser, nicht aus dem Namen der Eigenschaft."""

    def test_day_and_time_in_one_value(self) -> None:
        moment = object_moment({"name": "x", "gedeckt": {"Wann": "17.11.2027 um 10 Uhr"}})
        self.assertEqual(moment, datetime(2027, 11, 17, 10, 0, tzinfo=_TZ))

    def test_day_and_time_in_two_values_with_any_name(self) -> None:
        moment = object_moment({"name": "x", "gedeckt": {"Anlass": "17.11.2027", "b": "10 Uhr"}})
        self.assertEqual(moment, datetime(2027, 11, 17, 10, 0, tzinfo=_TZ))

    def test_two_clock_times_are_no_moment(self) -> None:
        obj = {"name": "x", "gedeckt": {"Tag": "17.11.2027", "von": "10 Uhr", "bis": "11 Uhr"}}
        self.assertIsNone(object_moment(obj))

    def test_a_value_without_time_is_no_moment(self) -> None:
        self.assertIsNone(object_moment({"name": "x", "gedeckt": {"Farbe": "blau"}}))

    def test_broken_form_is_loud(self) -> None:
        with self.assertLogs("ki_server.storage_inventory", level="ERROR"):
            self.assertEqual(acute_moments(["kein", "dict"]), [])

    def test_same_moment_twice_is_asked_once(self) -> None:
        self.assertEqual(len(acute_moments(_situation(_ON_17TH_AT_10, _ON_17TH_AT_10))), 1)


class TimelineMomentTest(unittest.TestCase):
    """Der Leseweg: wirft beim Lesefehler, statt ihn als leeren Bestand auszugeben."""

    def test_read_error_reaches_the_caller(self) -> None:
        inventory = _Inventory([], error=RuntimeError("synthetischer Lesefehler"))
        with patch.object(TimelineRepository, "find_by_date_range", side_effect=inventory), \
                self.assertRaises(RuntimeError):
            find_at_moment(_USER, datetime(2027, 11, 17, 10, 0, tzinfo=_TZ))

    def test_found_row_is_returned(self) -> None:
        inventory = _Inventory([_row(10), _row(10, 30)])
        with patch.object(TimelineRepository, "find_by_date_range", side_effect=inventory), \
                self.assertNoLogs("ki_server.memory.timeline_inventory", level="ERROR"):
            matches = find_at_moment(_USER, datetime(2027, 11, 17, 10, 0, tzinfo=_TZ))
        self.assertEqual([m["id"] for m in matches], [1000])

    def test_row_that_is_no_dict_is_loud_and_dropped(self) -> None:
        """Der Zwilling zu `test_found_row_is_returned`: dieselbe Zeile, daneben eine kaputte."""
        inventory = _Inventory([_row(10), "keine Zeile"])
        with patch.object(TimelineRepository, "find_by_date_range", side_effect=inventory), \
                self.assertLogs("ki_server.memory.timeline_inventory", level="ERROR") as logs:
            matches = find_at_moment(_USER, datetime(2027, 11, 17, 10, 0, tzinfo=_TZ))
        self.assertEqual([m["id"] for m in matches], [1000])
        self.assertTrue(any("1 Timeline-Zeile(n)" in line for line in logs.output))

    def test_invalid_input_raises(self) -> None:
        with self.assertRaises(ValueError):
            find_at_moment("", datetime(2027, 11, 17, 10, 0, tzinfo=_TZ))
        with self.assertRaises(ValueError):
            find_at_moment(_USER, datetime(2027, 11, 17, 10, 0))

    def test_row_without_aware_time_is_loud_and_no_match(self) -> None:
        row = _row(10)
        row["event_time"] = datetime(2027, 11, 17, 10, 0)
        with self.assertLogs("ki_server.memory.timeline_inventory", level="ERROR"):
            self.assertFalse(is_appointment_at(row, datetime(2027, 11, 17, 10, 0, tzinfo=_TZ)))


class CopiesBoundToSourceTest(unittest.TestCase):
    """Die drei Kopien des Abgleichs gegen ihre Quelle gehalten.

    Laeuft eine Kopie auseinander, gilt ein Anker als Termin, ein Eintrag mit
    Genauigkeit Tag als Uhrzeit oder eine Lage nach Ausfall als frisch — jedes
    Mal ein moegliches falsches *gefunden*, und kein Zeuge des Verhaltens saehe
    es, weil sie die Kopie selbst benutzen. Importiert wird die Quelle erst hier,
    damit nur diese Zeugen von `agents` und vom Lage-Knoten abhaengen.
    """

    def test_anchor_type_is_the_kzg_anchor(self) -> None:
        from agents.kzg.magnete import EVENT_TYPE_ERINNERUNGS_ANKER
        self.assertEqual(ANCHOR_TYPE, EVENT_TYPE_ERINNERUNGS_ANKER)

    def test_time_precisions_are_the_timeline_ones(self) -> None:
        from agents.timeline.event_time import _TIME_PRECISION
        self.assertEqual(TIME_PRECISIONS, frozenset(_TIME_PRECISION))

    def test_fallback_origin_is_the_situation_node_one(self) -> None:
        from graph.nodes.sachlage import HERKUNFT_AUSFALL
        self.assertEqual(FALLBACK_ORIGIN, HERKUNFT_AUSFALL)


if __name__ == "__main__":
    unittest.main()
