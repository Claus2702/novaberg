"""Zeugen: Scheibe 11 im Knoten — ablegen, an Entitaet und Zeitanker binden.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 11. Je gerechnetem
Turn werden die Objekte der Sachlage mit ihren gedeckten Werten abgelegt. Die
Entitaet kommt spaeter: Die Magnete eines Turns (`magnete_aufloesen` im
KZG-Agenten) entstehen in zwei Haelften, die des Nutzers vor der Sachlage, die
von Novas Antwort danach. Ein ungebundenes Objekt wird deshalb bei jedem
Auftreten gegen die Magnete seiner juengsten Turns gehalten.

Zeugen dieser Datei:
  * die Namensregel (gleich, oder Enthaltensein ab vier Zeichen; nie bei zwei
    Kandidaten),
  * die Magnete aus KZG-Hash und, nach dessen Verfall, aus dem LZG-Knoten,
  * der Zeitanker nur bei genau einem Anker im Turn und einem Zeitausdruck,
  * die Verdrahtung im Knoten (nur auf gerechneten Wegen, mit der Verlaufs-id),
  * ein Rundlauf gegen Datenbank und Redis: `verbindung` → KZG-Hash →
    Entitaet → gebundenes Objekt.
"""

import unittest
import uuid
from unittest.mock import patch

import psycopg2

from config import POSTGRES_URL, redis_client
from graph.nodes import sachlage as sachlage_mod
from graph.nodes import sachlage_memory as memory_mod
from graph.nodes.sachlage_memory import (
    TurnMagnet,
    collect_magnets,
    match_entity,
    remember_objects,
)
from memory.sachlage_history import history_write
from memory.sachlage_properties import RecordResult


class MatchEntityTest(unittest.TestCase):
    def test_equal_names_bind(self) -> None:
        self.assertEqual(match_entity("Vela-Pulsar", {7: "vela-pulsar"}), 7)

    def test_containment_from_four_characters_binds(self) -> None:
        self.assertEqual(match_entity("Vela Pulsar", {7: "Vela Pulsar (B0833−45)"}), 7)

    def test_punctuation_does_not_separate_names(self) -> None:
        self.assertEqual(match_entity("Crab-Pulsar", {7: "Crab Pulsar (B0531+21)"}), 7)

    def test_short_containment_does_not_bind(self) -> None:
        self.assertIsNone(match_entity("Ben", {7: "Benjamin Franklin"}))

    def test_two_candidates_bind_nothing(self) -> None:
        self.assertIsNone(match_entity("Pulsar", {7: "Vela Pulsar", 8: "Crab Pulsar"}))

    def test_no_candidates(self) -> None:
        self.assertIsNone(match_entity("Geburtstag", {}))


class CollectMagnetsTest(unittest.TestCase):
    def test_the_kzg_hash_carries_the_magnets(self) -> None:
        links = [{"turn_id": "t1", "kzg_id": "k1", "lzg_id": None,
                  "lzg_entitaet_ids": None, "lzg_timeline_id": None}]
        with patch.object(memory_mod, "turn_links", return_value=links), \
             patch.object(memory_mod, "redis_client") as redis:
            redis.hmget.return_value = ["3,4", "9"]
            self.assertEqual(collect_magnets(["t1"]), [TurnMagnet("t1", (3, 4), 9)])

    def test_after_the_kzg_expired_the_lzg_node_carries_them(self) -> None:
        links = [{"turn_id": "t1", "kzg_id": "k1", "lzg_id": 5,
                  "lzg_entitaet_ids": [6], "lzg_timeline_id": None}]
        with patch.object(memory_mod, "turn_links", return_value=links), \
             patch.object(memory_mod, "redis_client") as redis:
            redis.hmget.return_value = [None, None]
            self.assertEqual(collect_magnets(["t1"]), [TurnMagnet("t1", (6,), None)])

    def test_a_turn_without_magnets_yields_nothing(self) -> None:
        links = [{"turn_id": "t1", "kzg_id": "k1", "lzg_id": None,
                  "lzg_entitaet_ids": None, "lzg_timeline_id": None}]
        with patch.object(memory_mod, "turn_links", return_value=links), \
             patch.object(memory_mod, "redis_client") as redis:
            redis.hmget.return_value = ["", None]
            self.assertEqual(collect_magnets(["t1"]), [])


def _sachlage(**objekt: object) -> dict:
    basis: dict = {"name": "Vela Pulsar", "akut": True, "gedeckt": {}, "offen": []}
    basis.update(objekt)
    return {"objekte": [basis]}


def _result(**felder: object) -> RecordResult:
    basis: dict = {"objects": 1, "new": 1, "confirmed": 0, "replaced": 0,
                   "object_ids": {"vela pulsar": 11}, "property_ids": {}}
    basis.update(felder)
    return RecordResult(**basis)


class RememberObjectsTest(unittest.TestCase):
    def _run(self, sachlage: dict, result: RecordResult | None, magnets: list,
             names: dict, unbound: list | None = None) -> tuple:
        with patch.object(memory_mod, "record_turn_objects", return_value=result), \
             patch.object(memory_mod, "unbound_objects", return_value=unbound or []), \
             patch.object(memory_mod, "collect_magnets", return_value=magnets), \
             patch.object(memory_mod, "entity_names", return_value=names), \
             patch.object(memory_mod, "bind_entity", return_value=True) as bind, \
             patch.object(memory_mod, "bind_timeline", return_value=True) as anchor:
            summary = remember_objects("u", "c", "t1", 42, sachlage)
        return summary, bind, anchor

    def test_without_a_record_nothing_is_bound(self) -> None:
        summary, bind, anchor = self._run(_sachlage(), None, [], {})
        self.assertFalse(summary["abgelegt"])
        bind.assert_not_called()
        anchor.assert_not_called()

    def test_an_unbound_object_is_bound_through_its_turns(self) -> None:
        unbound = [{"id": 11, "name": "Vela Pulsar", "turn_ids": ["t0", "t1"]}]
        summary, bind, _ = self._run(
            _sachlage(), _result(), [TurnMagnet("t0", (7,), None)],
            {7: "Vela Pulsar (B0833−45)"}, unbound,
        )
        bind.assert_called_once_with(POSTGRES_URL, 11, 7, "turn_magnet")
        self.assertEqual(summary["gebunden"], 1)

    def test_the_time_anchor_needs_exactly_one_anchor_and_a_time_expression(self) -> None:
        sachlage = _sachlage(gedeckt={"Beobachtung": "am Freitag um 21 Uhr", "Farbe": "blau"})
        result = _result(property_ids={("vela pulsar", "beobachtung"): 101,
                                       ("vela pulsar", "farbe"): 102})
        _, _, anchor = self._run(sachlage, result, [TurnMagnet("t1", (), 55)], {})
        anchor.assert_called_once_with(POSTGRES_URL, 101, 55)

    def test_two_anchors_in_the_turn_bind_no_time(self) -> None:
        sachlage = _sachlage(gedeckt={"Beobachtung": "am Freitag um 21 Uhr"})
        result = _result(property_ids={("vela pulsar", "beobachtung"): 101})
        magnets = [TurnMagnet("t1", (), 55), TurnMagnet("t1", (), 56)]
        _, _, anchor = self._run(sachlage, result, magnets, {})
        anchor.assert_not_called()

    def test_an_anchor_of_an_earlier_turn_is_not_this_turns_anchor(self) -> None:
        sachlage = _sachlage(gedeckt={"Beobachtung": "am Freitag um 21 Uhr"})
        result = _result(property_ids={("vela pulsar", "beobachtung"): 101})
        _, _, anchor = self._run(sachlage, result, [TurnMagnet("t0", (), 55)], {})
        anchor.assert_not_called()


class TheNodeRemembersTest(unittest.TestCase):
    """Die Verdrahtung: nur gerechnete Wege legen ab, mit der Verlaufs-id."""

    def _assess(self, derived: dict | None, impuls: bool = False) -> object:
        state = {"user_id": "u", "character_id": "c", "turn_id": "t1",
                 "user_prompt": "Wie schnell dreht sich der Vela-Pulsar?",
                 "session_turns": [], "event_payload": {},
                 "event_source": "pixie" if impuls else "user"}
        with patch.object(sachlage_mod, "sachlage_load", return_value=(None, False)), \
             patch.object(sachlage_mod, "reiz_ist_eigener_gedanke", return_value=impuls), \
             patch.object(sachlage_mod, "_resume_lookup", return_value=None), \
             patch.object(sachlage_mod, "memory_offer", return_value=[]), \
             patch.object(sachlage_mod, "_derive", return_value=derived), \
             patch.object(sachlage_mod, "_sachlage_store"), \
             patch.object(sachlage_mod, "_track_short_goal"), \
             patch.object(sachlage_mod, "sachlage_bridge_build", return_value={}), \
             patch.object(sachlage_mod, "log_berechnung"), \
             patch.object(sachlage_mod, "history_write", return_value=42), \
             patch.object(sachlage_mod.model_service.embed, "submit_sync"), \
             patch.object(sachlage_mod, "remember_objects",
                          return_value={"abgelegt": True}) as remember:
            sachlage_mod.sachlage_assess(state)
        return remember

    def test_a_computed_turn_remembers_with_the_history_id(self) -> None:
        derived = {"thema": "Pulsar", "gegenstand": "Rotation", "nutzerziel": "wissen",
                   "ausdrucksweise": "fragend", "objekte": []}
        remember = self._assess(derived)
        remember.assert_called_once()
        self.assertEqual(remember.call_args.args[:4], ("u", "c", "t1", 42))

    def test_a_failed_call_remembers_nothing(self) -> None:
        self._assess(None).assert_not_called()

    def test_an_impulse_remembers_nothing(self) -> None:
        self._assess(None, impuls=True).assert_not_called()


class RoundTripTest(unittest.TestCase):
    """Gegen Datenbank und Redis: vom Magneten des Turns zum gebundenen Objekt."""

    def setUp(self) -> None:
        self.user = f"test-mem-{uuid.uuid4().hex[:8]}"
        self.char = "nova-test"
        self.turn = f"{self.user}-t0"
        self.kzg_key = f"kzg:{self.user}:{self.char}:1"
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO entitaeten (user_id, name, typ)
                       VALUES (%s, 'Vela Pulsar (B0833−45)', 'sonstiges') RETURNING id""",
                    (self.user,),
                )
                self.entitaet_id = cur.fetchone()[0]
                cur.execute("INSERT INTO verbindung (turn_id, kzg_id) VALUES (%s, %s)",
                            (self.turn, self.kzg_key))
            conn.commit()
        finally:
            conn.close()
        redis_client.hset(self.kzg_key, mapping={"entitaet_ids": str(self.entitaet_id)})
        self.verlauf_id = history_write(
            POSTGRES_URL, turn_id=self.turn, user_id=self.user, character_id=self.char,
            sachlage={"thema": "Pulsar", "gegenstand": "Rotation", "nutzerziel": "wissen",
                      "ausdrucksweise": "fragend", "objekte": [], "herkunft": "frisch"},
            embedding=None,
        )

    def tearDown(self) -> None:
        redis_client.delete(self.kzg_key)
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM sachlage_eigenschaft WHERE objekt_id IN
                               (SELECT id FROM sachlage_objekt WHERE user_id = %s)""", (self.user,))
                cur.execute("""DELETE FROM sachlage_objekt_turn WHERE objekt_id IN
                               (SELECT id FROM sachlage_objekt WHERE user_id = %s)""", (self.user,))
                cur.execute("DELETE FROM sachlage_objekt WHERE user_id = %s", (self.user,))
                cur.execute("DELETE FROM sachlage_verlauf WHERE user_id = %s", (self.user,))
                cur.execute("DELETE FROM verbindung WHERE turn_id = %s", (self.turn,))
                cur.execute("DELETE FROM entitaeten WHERE user_id = %s", (self.user,))
            conn.commit()
        finally:
            conn.close()

    def test_the_object_is_bound_to_the_entity_of_its_turn(self) -> None:
        summary = remember_objects(
            self.user, self.char, self.turn, self.verlauf_id,
            _sachlage(gedeckt={"Rotationsperiode": "89 Millisekunden"}),
        )
        self.assertEqual((summary["abgelegt"], summary["gebunden"]), (True, 1))
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT entitaet_id, entitaet_bindung FROM sachlage_objekt "
                            "WHERE user_id = %s", (self.user,))
                self.assertEqual(cur.fetchone(), (self.entitaet_id, "turn_magnet"))
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
