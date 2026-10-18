"""Zeugen für den Verfall der Fakten-Kanten und seinen Schritt im Tageslauf.

Was diese Datei zusichert:
  * **Die Stärke folgt exp(−rate · Tage seit last_touched)**, die Erwartung
    als Literal gerechnet, nicht aus der Konstante, die sie prüft.
  * **Der Lauf ändert `aktiv` nie** — auch nicht bei einer Kante, deren
    Stärke beinahe null ist. `aktiv = FALSE` heißt *abgelöst*, nicht *verblasst*.
  * **Eine abgelöste Kante bleibt unberührt.**
  * **Ein zweiter Lauf am selben Stichtag ändert nichts.**
  * **Der Schritt im Tageslauf hat einen eigenen Audit-Eintrag**, und sein
    Fehler verdeckt die Ergebnisse der übrigen Schritte nicht.

Die Suite läuft gegen eine Wegwerf-Datenbank; der Lauf ist global über alle
Paare, die Zusicherungen gelten den Zeilen des eigenen Paares.
"""

import math
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import psycopg2
import psycopg2.extras

from config import POSTGRES_URL
from memory.repositories.fakten_repository import FaktenRepository, NewFact

AGENT_MODUL: str = "agents.synapsen_decay.agent"
STICHTAG: datetime = datetime(2026, 10, 1, 3, 0, tzinfo=timezone.utc)
ALTER_ANKER: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)
# exp(-0.0015 * 100), von Hand gerechnet.
STAERKE_100_TAGE: float = 0.8607079764250578


class TheRateTest(unittest.TestCase):
    """Der Startwert der Rate und das gerechnete Literal."""

    def test_the_start_value_is_that_of_the_node_decay(self) -> None:
        from config import FAKTEN_DECAY_RATE

        self.assertEqual(FAKTEN_DECAY_RATE, 0.0015)
        self.assertAlmostEqual(math.exp(-0.0015 * 100), STAERKE_100_TAGE, delta=1e-15)


class _EdgesFixture(unittest.TestCase):
    """Vier Kanten eines eigenen Paares, je mit eigenem Alter des Ankers."""

    def setUp(self) -> None:
        self.user = f"test-verf-{uuid.uuid4().hex[:8]}"
        self.char = "nova-test"
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO entitaeten (user_id, name) VALUES (%s, 'Michael') RETURNING id",
                    (self.user,),
                )
                subjekt: int = cur.fetchone()[0]
                self.ids: dict[str, int] = {}
                for name, attribut in (("hundert", "wohnt_in"), ("uralt", "arbeitet_bei"),
                                       ("abgeloest", "heisst"), ("kuenftig", "mag")):
                    self.ids[name] = FaktenRepository.insert(
                        cur, self.user, self.char, subjekt, attribut,
                        NewFact(fakt_text=f"Michael {attribut} {name}", herkunft="mensch",
                                einwertig=True, objekt_wert=name),
                    )
                anker: dict[str, datetime] = {
                    "hundert":   STICHTAG - timedelta(days=100),
                    "uralt":     STICHTAG - timedelta(days=10_000),
                    "abgeloest": STICHTAG - timedelta(days=100),
                    "kuenftig":  STICHTAG + timedelta(days=5),
                }
                for name, zeit in anker.items():
                    cur.execute(
                        """UPDATE fakten SET last_touched = %s, decay_am = %s,
                                  staerke_decay = 1.0
                           WHERE id = %s""",
                        (zeit, ALTER_ANKER, self.ids[name]),
                    )
                cur.execute(
                    "UPDATE fakten SET aktiv = FALSE, t_invalid = NOW() WHERE id = %s",
                    (self.ids["abgeloest"],),
                )
            conn.commit()
        finally:
            conn.close()

    def tearDown(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM fakten WHERE user_id = %s", (self.user,))
                cur.execute("DELETE FROM entitaeten WHERE user_id = %s", (self.user,))
            conn.commit()
        finally:
            conn.close()

    def _kanten(self) -> dict[str, dict]:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """SELECT id, aktiv, staerke_decay, decay_am, last_touched, t_invalid
                       FROM fakten WHERE user_id = %s""",
                    (self.user,),
                )
                nach_id = {z["id"]: dict(z) for z in cur.fetchall()}
        finally:
            conn.close()
        return {name: nach_id[i] for name, i in self.ids.items()}


class TheEdgesDecayTest(_EdgesFixture):
    """Der Lauf gegen die Datenbank, auf einen festen Stichtag gerechnet."""

    def test_a_hundred_days_give_the_exponential_strength(self) -> None:
        ergebnis = FaktenRepository.run_fakten_decay(POSTGRES_URL, stichtag=STICHTAG)
        self.assertIsNone(ergebnis["error"])
        self.assertGreaterEqual(ergebnis["verarbeitet"], 3)
        kante = self._kanten()["hundert"]
        self.assertAlmostEqual(kante["staerke_decay"], STAERKE_100_TAGE, delta=1e-9)
        self.assertEqual(kante["decay_am"], STICHTAG)

    def test_no_edge_changes_aktiv(self) -> None:
        vorher = {name: k["aktiv"] for name, k in self._kanten().items()}
        FaktenRepository.run_fakten_decay(POSTGRES_URL, stichtag=STICHTAG)
        kanten = self._kanten()
        self.assertEqual({name: k["aktiv"] for name, k in kanten.items()}, vorher)
        # Der Zwilling: Die alte Kante ist wirklich verfallen — beinahe null,
        # und trotzdem aktiv.
        self.assertLess(kanten["uralt"]["staerke_decay"], 1e-6)
        self.assertTrue(kanten["uralt"]["aktiv"])

    def test_a_replaced_edge_stays_untouched(self) -> None:
        FaktenRepository.run_fakten_decay(POSTGRES_URL, stichtag=STICHTAG)
        kante = self._kanten()["abgeloest"]
        self.assertEqual((kante["staerke_decay"], kante["decay_am"]), (1.0, ALTER_ANKER))

    def test_an_anchor_after_the_cutoff_keeps_full_strength(self) -> None:
        FaktenRepository.run_fakten_decay(POSTGRES_URL, stichtag=STICHTAG)
        kante = self._kanten()["kuenftig"]
        self.assertEqual((kante["staerke_decay"], kante["decay_am"]), (1.0, STICHTAG))

    def test_a_second_run_at_the_same_cutoff_changes_nothing(self) -> None:
        FaktenRepository.run_fakten_decay(POSTGRES_URL, stichtag=STICHTAG)
        erst = self._kanten()
        FaktenRepository.run_fakten_decay(POSTGRES_URL, stichtag=STICHTAG)
        self.assertEqual(self._kanten(), erst)

    def test_invalid_parameters_write_nothing(self) -> None:
        vorher = self._kanten()
        negativ = FaktenRepository.run_fakten_decay(POSTGRES_URL, -0.1, STICHTAG)
        naiv = FaktenRepository.run_fakten_decay(
            POSTGRES_URL, stichtag=STICHTAG.replace(tzinfo=None),
        )
        self.assertIsNotNone(negativ["error"])
        self.assertIsNotNone(naiv["error"])
        self.assertEqual(self._kanten(), vorher)


def _audits(write_audit: object) -> list[tuple[str, str]]:
    """Die (Aufgabe, Status)-Paare der gerufenen Audit-Einträge."""
    return [(ruf.args[1], ruf.args[2]) for ruf in write_audit.call_args_list]


class TheStepWritesItsOwnAuditTest(_EdgesFixture):
    """Der Schritt des Tageslaufs, mit seinem eigenen Audit-Eintrag."""

    def test_the_step_runs_against_the_database(self) -> None:
        from agents.synapsen_decay.agent import SynapsenDecayAgent

        with patch(f"{AGENT_MODUL}.write_audit") as audit:
            ergebnis = SynapsenDecayAgent()._fakten_verfall("run-test")
        self.assertIsNone(ergebnis["error"])
        self.assertNotEqual(self._kanten()["hundert"]["decay_am"], ALTER_ANKER)
        self.assertEqual(
            _audits(audit), [("fakten_verfall", "gestartet"), ("fakten_verfall", "erledigt")],
        )

    def test_a_raising_run_becomes_an_error_with_audit(self) -> None:
        from agents.synapsen_decay.agent import SynapsenDecayAgent

        with patch(f"{AGENT_MODUL}.write_audit") as audit, \
             patch(f"{AGENT_MODUL}.FaktenRepository.run_fakten_decay",
                   side_effect=psycopg2.OperationalError("keine Verbindung")):
            ergebnis = SynapsenDecayAgent()._fakten_verfall("run-test")
        self.assertIn("keine Verbindung", ergebnis["error"])
        self.assertEqual(ergebnis["verarbeitet"], 0)
        self.assertEqual(
            _audits(audit), [("fakten_verfall", "gestartet"), ("fakten_verfall", "fehler")],
        )


class TheDailyRunKeepsTheOtherResultsTest(unittest.TestCase):
    """Der Tageslauf mit ersetzten Schritten — nur der Fakten-Verfall wechselt."""

    def _lauf(self, fakten: dict) -> tuple[dict, object]:
        from agents.base import AgentState
        from agents.synapsen_decay.agent import SynapsenDecayAgent

        leer: dict = {"error": None, "total_processed": 0, "deactivated_count": 0,
                      "deleted_count": 0, "verarbeitet": 0, "deaktiviert": 0}
        queue: dict = dict(leer, verarbeitet=7)
        fasz: dict = {"traeger": 0, "gerechnet": 0, "ohne_bindung": 0, "ohne_strang": 0,
                      "werte": {}, "roh_min": None, "roh_median": None, "roh_max": None,
                      "error": None}
        with patch(f"{AGENT_MODUL}.SYNAPSEN_DECAY_AKTIV", True), \
             patch(f"{AGENT_MODUL}.lzg_knoten.run_node_decay", return_value=leer), \
             patch(f"{AGENT_MODUL}.pipeline_log.delete_expired_entries", return_value=leer), \
             patch(f"{AGENT_MODUL}.ShadowAuftragRepository.verfall_lauf", return_value=queue), \
             patch(f"{AGENT_MODUL}.FaktenRepository.run_fakten_decay", **fakten), \
             patch(f"{AGENT_MODUL}.db_manager"), \
             patch(f"{AGENT_MODUL}.write_audit") as audit, \
             patch(f"{AGENT_MODUL}.praegung.alle_faeden_nachfuehren",
                   return_value={"gefaltet": 0, "gesamt": 0, "error": None}), \
             patch(f"{AGENT_MODUL}.praegung.faeden_ohne_strang_zuordnen",
                   return_value=(0, 0)), \
             patch(f"{AGENT_MODUL}.praegung.alle_einfaerbungen",
                   return_value={"gerechnet": 0, "gesamt": 0, "je_sektor": {},
                                 "abstand_max": 0.0, "error": None}), \
             patch(f"{AGENT_MODUL}.fascination_store.bestandslauf", return_value=fasz), \
             patch(f"{AGENT_MODUL}.price_watch.pruefen",
                   side_effect=RuntimeError("kein Netz im Zeugen")), \
             patch(f"{AGENT_MODUL}.redis_client"), \
             patch.object(SynapsenDecayAgent, "_richtungen_protokollieren", return_value=0), \
             patch.object(SynapsenDecayAgent, "_log_forensik"):
            zustand = SynapsenDecayAgent().invoke(AgentState(auftrag="", kontext={}))
        return zustand, audit

    def test_a_raising_step_keeps_the_other_results(self) -> None:
        zustand, audit = self._lauf(
            {"side_effect": psycopg2.OperationalError("keine Verbindung")},
        )
        self.assertEqual(zustand["status"], "fehler")
        self.assertIn("keine Verbindung", zustand["fehler"])
        self.assertEqual(zustand["ergebnis"]["queue_verfall"]["verarbeitet"], 7)
        self.assertIn("keine Verbindung", zustand["ergebnis"]["fakten_verfall"]["error"])
        self.assertIn(("fakten_verfall", "fehler"), _audits(audit))

    def test_a_successful_step_stands_in_the_result(self) -> None:
        zustand, audit = self._lauf(
            {"return_value": {"verarbeitet": 4, "stichtag": STICHTAG, "error": None}},
        )
        self.assertEqual(zustand["status"], "abgeschlossen")
        self.assertEqual(zustand["ergebnis"]["fakten_verfall"]["verarbeitet"], 4)
        self.assertEqual(zustand["ergebnis"]["queue_verfall"]["verarbeitet"], 7)
        self.assertIn(("fakten_verfall", "erledigt"), _audits(audit))


if __name__ == "__main__":
    unittest.main()
