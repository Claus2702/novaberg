"""Tests: Ein Nein haelt das Objekt fest — Scheibe 12 E3.

Die Absicht des Eigentuemers (14.09.2026): *"nach einem Nein sollte sie nicht
aufdringlich sein, das wuerde das Objekt im Gespraechskontext um die Eigenschaft
erweitern, dass es abgelehnt ist zum Speichern."*

Zeugen dieser Datei:
  * **Die blanke Ablehnung** — "Nein danke" ja, "Nein, trag lieber den Zahnarzt
    ein" nein.
  * **Das Gedaechtnis** — die Eigenschaft `Speichern = abgelehnt` steht am
    Objekt, ist lesbar, und ein zweites Nein ist eine Bestaetigung, kein
    zweiter Wert.
  * **Die Verdrahtung im Dispatcher** — ein Nein auf ein offenes Angebot
    schreibt den Vermerk und raeumt das Angebot weg; ein Nein ohne Angebot
    schreibt nichts.

Die Suite laeuft gegen die Produktiv-Datenbank: Das Fixture bringt ein eigenes
Paar mit und raeumt in tearDown ab (Muster: test_sachlage_properties_schema).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
import uuid
from unittest.mock import patch

import psycopg2

from config import POSTGRES_URL
from graph.nodes import dispatcher
from memory.sachlage_properties import declined_objects, record_declined
from utils.offers import Offer, is_bare_refusal, offer_load, offer_store


class BlankeAblehnungTest(unittest.TestCase):

    def test_ablehnungen(self) -> None:
        for text in ("Nein", "Nein danke", "Lass mal", "Nicht noetig", "Lieber nicht", "Nee, passt schon"):
            with self.subTest(text=text):
                self.assertTrue(is_bare_refusal(text))

    def test_keine_blanke_ablehnung(self) -> None:
        for text in ("Nein, trag lieber den Zahnarzt ein", "Gerne", "Ja", "Danke", "", "Nicht heute, aber morgen"):
            with self.subTest(text=text):
                self.assertFalse(is_bare_refusal(text))


class _PaarFixture(unittest.TestCase):

    def setUp(self) -> None:
        self.user = f"test-nein-{uuid.uuid4().hex[:8]}"
        self.char = "nova-test"

    def tearDown(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """DELETE FROM sachlage_eigenschaft WHERE objekt_id IN
                       (SELECT id FROM sachlage_objekt WHERE user_id = %s)""", (self.user,))
                cur.execute("DELETE FROM sachlage_objekt WHERE user_id = %s", (self.user,))
            conn.commit()
        finally:
            conn.close()

    def _aktive_werte(self, name: str) -> list[str]:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT e.wert FROM sachlage_eigenschaft e JOIN sachlage_objekt o ON o.id = e.objekt_id
                       WHERE o.user_id = %s AND o.name = %s AND e.aktiv""", (self.user, name))
                return [r[0] for r in cur.fetchall()]
        finally:
            conn.close()


class GedaechtnisTest(_PaarFixture):

    def test_das_nein_steht_am_objekt_und_ist_lesbar(self) -> None:
        n = record_declined(POSTGRES_URL, user_id=self.user, character_id=self.char,
                            turn_id="t1", object_names=["Abholung der Schwester"])
        self.assertEqual(n, 1)
        self.assertEqual(self._aktive_werte("Abholung der Schwester"), ["abgelehnt"])
        self.assertEqual(declined_objects(POSTGRES_URL, self.user, self.char,
                                          ["Abholung der Schwester", "Zahnarzttermin"]),
                         {"Abholung der Schwester"})

    def test_ein_zweites_nein_ist_eine_bestaetigung(self) -> None:
        for turn in ("t1", "t2"):
            record_declined(POSTGRES_URL, user_id=self.user, character_id=self.char,
                            turn_id=turn, object_names=["Abholung der Schwester"])
        self.assertEqual(self._aktive_werte("Abholung der Schwester"), ["abgelehnt"])

    def test_unvollstaendige_kennung_schreibt_nichts(self) -> None:
        with self.assertLogs("ki_server.memory.sachlage_properties", level="ERROR"):
            self.assertEqual(record_declined(POSTGRES_URL, user_id=self.user, character_id=self.char,
                                             turn_id="", object_names=["X"]), 0)
        self.assertEqual(self._aktive_werte("X"), [])


class FakeRedis:
    def __init__(self) -> None:
        self.inhalt: dict[str, str] = {}

    def setex(self, key: str, ttl: int, wert: str) -> None:
        self.inhalt[key] = wert

    def get(self, key: str) -> str | None:
        return self.inhalt.get(key)

    def delete(self, key: str) -> int:
        return 1 if self.inhalt.pop(key, None) is not None else 0


class VerdrahtungTest(_PaarFixture):

    def _turn(self, reiz: str, speicher: FakeRedis) -> None:
        state = {"user_prompt": reiz, "event_payload": {}, "response": "Alles klar, dann lassen wir das.",
                 "turn_id": "t2", "sachlage": {"objekte": []}, "objekt_urteil": {}}
        with patch.object(dispatcher, "cfg_redis_client", speicher):
            dispatcher._angebot_merken(state, self.user, self.char)

    def _angebot(self, speicher: FakeRedis) -> None:
        offer_store(speicher, self.user, self.char,
                    Offer(sentence="Soll ich dir die Abholung eintragen?",
                          objects=("Abholung der Schwester",), services=("timeline",),
                          turn_id="t1", time=1.0), 900)

    def test_ein_nein_auf_ein_angebot_haelt_das_objekt_fest(self) -> None:
        speicher = FakeRedis()
        self._angebot(speicher)
        self._turn("Nein danke", speicher)
        self.assertEqual(self._aktive_werte("Abholung der Schwester"), ["abgelehnt"])
        self.assertIsNone(offer_load(speicher, self.user, self.char))

    def test_ein_nein_ohne_angebot_schreibt_nichts(self) -> None:
        self._turn("Nein danke", FakeRedis())
        self.assertEqual(self._aktive_werte("Abholung der Schwester"), [])

    def test_eine_zustimmung_schreibt_kein_nein(self) -> None:
        speicher = FakeRedis()
        self._angebot(speicher)
        self._turn("Gerne", speicher)
        self.assertEqual(self._aktive_werte("Abholung der Schwester"), [])


if __name__ == "__main__":
    unittest.main()
