"""Zeugen für den Ereignis-Dienst (`agents.timeline.ereignis`): vom Auftrag zur Zeile.

Was diese Datei zusichert:
  * **Das Paar:** Ein Auftrag ohne `character_id` ist laut `verworfen`, ruft
    kein Modell und schreibt keine Zeile; mit Figur steht die Zeile mit
    dieser Figur da.
  * **Das Tor ist die Liste des Modells:** Eine leere Liste schreibt nichts
    (`kein_ereignis`); ein Ereignis *im November* ergibt eine Zeile
    `ereignis` mit `month`, dem Ersten des Monats und ohne Wiedervorlage,
    und die Abbildung Kandidat → Zeile.
  * **Nur die Kandidaten des Menschen** gehen ins Modell, unter ihrer Nummer
    aus `turn_candidates`; eine Nummer außerhalb ist laut
    `kandidat_unbekannt` und schreibt nichts.
  * **Die Person:** zwei gleichnamige Entitäten → ohne `entitaet_ids`, eine
    → `[id]`; die Zeile entsteht in beiden Fällen.
  * **Gescheitert:** Wirft das Eintragen, steht der Kandidat mit None in der
    Abbildung und der Ausgang ist `ereignis_fehlt`.
  * **Ohne Tag oder Monat kein Eintrag** (*2019*); eine Antwort ohne Liste
    ist `antwort_defekt`, nie *kein Ereignis*.
  * **Die Zeit:** `event_time_of` liest *im November* als Monat, *am 3.
    Dezember* als Tag, ein Jahr und eine Woche als nichts.

Das Modell antwortet aus einem festen Ausgang; die Kandidaten des Turns sind
ersetzt, der Eintrag `log_db_write` wird abgefangen. Die Datenbank ist die
Wegwerf-Datenbank der Suite; jedes Fixture bringt ein eigenes Paar mit und
räumt in tearDown ab.
"""

import unittest
import uuid
from datetime import date
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.extras

from agents.timeline import ereignis as ereignis_mod
from config import POSTGRES_URL
from memory.repositories.timeline_repository import TimelineRepository

_AUFTRAG: dict = {"ziel": "timeline", "aktion": "ereignis", "daten": {
    "turn_id": "probe-turn", "verlauf_id": 42, "salienz_human": 0.80,
    "user_intentionen": ["mitteilen"], "abgelegt": True,
}}
_AEUSSERUNG: str = "Meine Schwester Ilva zieht im November nach Ostheim."
_LOGGER: str = "ki_server.agents.timeline.ereignis"


def _ausfuehren(sql: str, params: tuple) -> list[dict]:
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            zeilen: list[dict] = [dict(r) for r in cur.fetchall()] if cur.description else []
        conn.commit()
        return zeilen
    finally:
        conn.close()


def _kandidat(objekt: str, eigenschaft: str, wert: str, sprecher: str = "nutzer") -> dict:
    """Ein Kandidat wie aus `turn_candidates`."""
    return {"id": 1, "objekt_id": 1, "objekt": objekt, "klasse": "person",
            "entitaet_id": None, "entitaet_bindung": None,
            "eigenschaft": eigenschaft, "wert": wert, "sprecher": sprecher}


def _ereignis(kandidat: object = 1, person: str = "Ilva", titel: str = "Umzug nach Ostheim",
              zeitausdruck: str = "im November") -> dict:
    """Ein Ereignis, wie das Modell es nennt."""
    return {"kandidat": kandidat, "person": person, "titel": titel,
            "zeitausdruck": zeitausdruck}


class EventServiceTest(unittest.TestCase):
    """Gegen die Datenbank: Auftrag → Modell (Doppel) → Zeit → Person → Zeile."""

    def setUp(self) -> None:
        self.user: str = f"test-ereignis-{uuid.uuid4().hex[:8]}"
        self.char: str = "nova-test"
        self.modell = MagicMock()
        ersatz = patch.object(ereignis_mod, "model_service", self.modell)
        ersatz.start()
        self.addCleanup(ersatz.stop)

    def tearDown(self) -> None:
        _ausfuehren("DELETE FROM timeline WHERE user_id = %s", (self.user,))
        _ausfuehren("DELETE FROM entitaeten WHERE user_id = %s", (self.user,))

    def _laufen(self, antwort: object, kandidaten: list[dict] | None = None,
                ohne_figur: bool = False) -> tuple[dict, dict]:
        """(Abbildung, Inhalt des einen Eintrags `log_db_write`)."""
        self.modell.chat.submit_sync.return_value.parsed = antwort
        zustand: dict = {"user_id": self.user, "character_id": self.char,
                         "turn_id": "probe-turn", "user_prompt": _AEUSSERUNG}
        if ohne_figur:
            del zustand["character_id"]
        if kandidaten is None:
            kandidaten = [_kandidat("Ilva", "Wohnort", "Ostheim")]
        with patch.object(ereignis_mod, "turn_candidates", return_value=kandidaten), \
             patch.object(ereignis_mod, "log_db_write") as eintrag:
            abbildung = ereignis_mod.process_event_orders(zustand, [_AUFTRAG], POSTGRES_URL)
        eintrag.assert_called_once()
        return abbildung, eintrag.call_args.kwargs["inhalt"]

    def _zeilen(self) -> list[dict]:
        return _ausfuehren(
            "SELECT id, character_id, event_type, precision, wiedervorlage_am, entitaet_ids, "
            "title, details FROM timeline WHERE user_id = %s ORDER BY id", (self.user,),
        )

    def _entitaet(self, name: str) -> int:
        return _ausfuehren(
            "INSERT INTO entitaeten (user_id, name, typ) VALUES (%s, %s, 'person') RETURNING id",
            (self.user, name),
        )[0]["id"]

    # --- Paar ---

    def test_without_a_character_the_order_is_rejected_loudly(self) -> None:
        with self.assertLogs(_LOGGER, level="ERROR") as protokoll:
            abbildung, inhalt = self._laufen({"ereignisse": [_ereignis()]}, ohne_figur=True)
        self.assertEqual(abbildung, {})
        self.assertEqual((inhalt["ausgang"], inhalt["mangel"]), ("verworfen", "Paar fehlt im Turn"))
        self.assertIn("Paar fehlt im Turn", "\n".join(protokoll.output))
        self.assertEqual(self.modell.chat.submit_sync.call_count, 0)
        self.assertEqual(self._zeilen(), [])

    def test_the_twin_with_a_character_the_row_carries_it(self) -> None:
        abbildung, _ = self._laufen({"ereignisse": [_ereignis()]})
        zeilen = self._zeilen()
        self.assertEqual([z["character_id"] for z in zeilen], [self.char])
        self.assertEqual(abbildung, {1: zeilen[0]["id"]})

    # --- Tor ---

    def test_an_empty_list_writes_nothing(self) -> None:
        abbildung, inhalt = self._laufen({"ereignisse": []})
        self.assertEqual(self.modell.chat.submit_sync.call_count, 1)
        self.assertEqual(abbildung, {})
        self.assertEqual(inhalt["ausgang"], "kein_ereignis")
        self.assertEqual(self._zeilen(), [])

    def test_the_twin_one_event_in_november_is_a_month_row_without_resubmission(self) -> None:
        abbildung, inhalt = self._laufen({"ereignisse": [_ereignis()]})
        zeilen = self._zeilen()
        self.assertEqual(len(zeilen), 1)
        self.assertEqual(
            {k: zeilen[0][k] for k in ("event_type", "precision", "wiedervorlage_am", "title")},
            {"event_type": "ereignis", "precision": "month", "wiedervorlage_am": None,
             "title": "Umzug nach Ostheim"},
        )
        moment = TimelineRepository.find_by_id(POSTGRES_URL, zeilen[0]["id"])["event_time"]
        self.assertEqual((moment.month, moment.day), (11, 1))
        self.assertEqual(abbildung, {1: zeilen[0]["id"]})
        self.assertEqual(inhalt["ausgang"], "klassifiziert")
        self.assertEqual([e["ausgang"] for e in inhalt["ereignisse"]], ["eingetragen"])

    def test_only_the_candidates_of_the_human_reach_the_model(self) -> None:
        kandidaten = [_kandidat("Vela-Pulsar", "Periode", "89 ms", sprecher="nova"),
                      _kandidat("Ilva", "Wohnort", "Ostheim")]
        self._laufen({"ereignisse": []}, kandidaten)
        nachricht: str = self.modell.chat.submit_sync.call_args.args[0].messages[0]["content"]
        self.assertIn("[2] Objekt: Ilva (Klasse: person) | Eigenschaft: Wohnort | Wert: Ostheim",
                      nachricht)
        self.assertNotIn("Vela-Pulsar", nachricht)
        self.assertNotIn("[1]", nachricht)

    def test_a_number_outside_the_candidates_is_loud_and_writes_nothing(self) -> None:
        with self.assertLogs(_LOGGER, level="ERROR") as protokoll:
            abbildung, inhalt = self._laufen({"ereignisse": [_ereignis(kandidat=9)]})
        self.assertIn("kein Kandidat des Menschen", "\n".join(protokoll.output))
        self.assertEqual(abbildung, {})
        self.assertEqual([e["ausgang"] for e in inhalt["ereignisse"]], ["kandidat_unbekannt"])
        self.assertEqual(self._zeilen(), [])

    def test_a_number_of_another_speaker_is_unknown_too(self) -> None:
        kandidaten = [_kandidat("Vela-Pulsar", "Periode", "89 ms", sprecher="nova"),
                      _kandidat("Ilva", "Wohnort", "Ostheim")]
        with self.assertLogs(_LOGGER, level="ERROR"):
            abbildung, _ = self._laufen({"ereignisse": [_ereignis(kandidat=1)]}, kandidaten)
        self.assertEqual(abbildung, {})
        self.assertEqual(self._zeilen(), [])

    # --- Person ---

    def test_an_ambiguous_person_gives_a_row_without_entities(self) -> None:
        self._entitaet("Ilva")
        self._entitaet("Ilva")
        self._laufen({"ereignisse": [_ereignis()]})
        zeilen = self._zeilen()
        self.assertEqual(len(zeilen), 1)
        self.assertIsNone(zeilen[0]["entitaet_ids"])
        self.assertEqual(zeilen[0]["details"], "Ilva")

    def test_the_twin_a_unique_person_gives_its_id(self) -> None:
        ilva = self._entitaet("Ilva")
        self._laufen({"ereignisse": [_ereignis()]})
        self.assertEqual([z["entitaet_ids"] for z in self._zeilen()], [[ilva]])

    # --- Gescheitert, ohne Zeit, defekt ---

    def test_a_failed_insert_maps_the_candidate_to_none(self) -> None:
        with patch.object(TimelineRepository, "insert", side_effect=RuntimeError("weg")), \
             self.assertLogs(_LOGGER, level="ERROR"):
            abbildung, inhalt = self._laufen({"ereignisse": [_ereignis()]})
        self.assertEqual(abbildung, {1: None})
        self.assertEqual([e["ausgang"] for e in inhalt["ereignisse"]], ["ereignis_fehlt"])
        self.assertEqual(self._zeilen(), [])

    def test_a_year_alone_writes_no_row(self) -> None:
        abbildung, inhalt = self._laufen({"ereignisse": [_ereignis(zeitausdruck="2019")]})
        self.assertEqual(abbildung, {})
        self.assertEqual([e["ausgang"] for e in inhalt["ereignisse"]], ["ohne_zeit"])
        self.assertEqual(self._zeilen(), [])

    def test_an_answer_without_the_list_is_broken_not_empty(self) -> None:
        with self.assertLogs(_LOGGER, level="ERROR"):
            abbildung, inhalt = self._laufen({"tripel": []})
        self.assertEqual(abbildung, {})
        self.assertEqual(inhalt["ausgang"], "antwort_defekt")
        self.assertEqual(self._zeilen(), [])


class EventTimeTest(unittest.TestCase):
    """`event_time_of`: Monat, Tag oder nichts."""

    HEUTE: date = date(2026, 10, 21)

    def _lesen(self, ausdruck: str) -> tuple[int, int, str] | None:
        gefunden = ereignis_mod.event_time_of(ausdruck, self.HEUTE)
        return None if gefunden is None else (gefunden[0].month, gefunden[0].day, gefunden[1])

    def test_a_month_is_the_first_with_precision_month(self) -> None:
        self.assertEqual(self._lesen("im November"), (11, 1, "month"))

    def test_a_date_is_a_day(self) -> None:
        self.assertEqual(self._lesen("am 3. Dezember"), (12, 3, "day"))

    def test_a_year_or_a_week_is_nothing(self) -> None:
        self.assertIsNone(self._lesen("2019"))
        with self.assertLogs(_LOGGER, level="ERROR"):
            self.assertIsNone(self._lesen("diese Woche"))


if __name__ == "__main__":
    unittest.main()
