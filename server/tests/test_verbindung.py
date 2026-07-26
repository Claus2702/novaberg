"""Tests fuer die verbindung-Zeilen des Dispatchers (Charakter-Resonanz, Bauteil 1b).

Ziel: Jeder neu angelegte KZG-Key eines Turns erzeugt genau eine
verbindung-Zeile mit gueltiger turn_id.

Die Faelle a, d und e pruefen den Datenbank-Zustand nach der Verarbeitung
(Handbuch §12, Nachbedingungs-Tests) und schreiben dafuer echte Zeilen in die
verbindung-Tabelle. Jede Zeile traegt eine testeigene turn_id und testeigene
kzg_ids (uuid4); tearDown raeumt genau diese wieder ab.

Kein skipUnless, kein skipIf, kein try/except um Importe: Fehlt die Datenbank
oder die Tabelle, wird dieser Test rot — er ueberspringt sich nicht.
"""

import unittest
import uuid
from unittest.mock import patch

import psycopg2

from config import ASSISTANT_USER_ID, POSTGRES_URL, redis_client
from graph.nodes.dispatcher import _verbindung_schreiben, dispatch
from memory.repositories.verbindung_repository import VerbindungRepository

DISPATCHER_LOGGER: str = "ki_server.dispatcher"


class VerbindungSchreibenTest(unittest.TestCase):
    """Vier Faelle des Schreibpfads plus die E8-Abgrenzung im Mischfall."""

    def setUp(self) -> None:
        """Erzeugt eine testeigene turn_id und zwei testeigene KZG-Keys."""
        marke: str = uuid.uuid4().hex
        self.turn_id: str = f"test-verbindung-{marke}"
        self.key_a:   str = f"kzg:test:verbindung:{marke}:a"
        self.key_b:   str = f"kzg:test:verbindung:{marke}:b"
        self.key_v:   str = f"kzg:test:verbindung:{marke}:v"
        self.alle_keys: list[str] = [self.key_a, self.key_b, self.key_v]

    def tearDown(self) -> None:
        """Loescht alle Zeilen, die dieser Test erzeugt haben koennte."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM verbindung WHERE kzg_id = ANY(%s) OR turn_id = %s",
                    (self.alle_keys, self.turn_id),
                )
            conn.commit()
        finally:
            conn.close()

    def _zeilen(self) -> list[dict]:
        """Liest alle verbindung-Zeilen dieses Tests, aelteste zuerst."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, turn_id, kzg_id, lzg_id
                    FROM   verbindung
                    WHERE  kzg_id = ANY(%s) OR turn_id = %s
                    ORDER  BY id
                    """,
                    (self.alle_keys, self.turn_id),
                )
                return [
                    {"id": r[0], "turn_id": r[1], "kzg_id": r[2], "lzg_id": r[3]}
                    for r in cur.fetchall()
                ]
        finally:
            conn.close()

    # ── a) turn_id gesetzt, 2 neue Keys -> 2 Zeilen ──────────────

    def test_a_zwei_neue_keys_ergeben_zwei_zeilen(self) -> None:
        anzahl: int = _verbindung_schreiben(
            turn_id      = self.turn_id,
            rolle        = "user",
            neue_keys    = [self.key_a, self.key_b],
            postgres_url = POSTGRES_URL,
        )

        self.assertEqual(anzahl, 2)

        zeilen: list[dict] = self._zeilen()
        self.assertEqual(len(zeilen), 2)
        self.assertEqual([z["kzg_id"] for z in zeilen], [self.key_a, self.key_b])
        self.assertEqual([z["turn_id"] for z in zeilen], [self.turn_id, self.turn_id])
        self.assertEqual([z["lzg_id"] for z in zeilen], [None, None])

    # ── b) turn_id leer -> 0 Zeilen, genau 1 WARNING ─────────────

    def test_b_leere_turn_id_schreibt_nichts_und_warnt_genau_einmal(self) -> None:
        with self.assertLogs(DISPATCHER_LOGGER, level="WARNING") as log:
            anzahl: int = _verbindung_schreiben(
                turn_id      = "",
                rolle        = "character",
                neue_keys    = [self.key_a, self.key_b],
                postgres_url = POSTGRES_URL,
            )

        self.assertEqual(anzahl, 0)
        self.assertEqual(self._zeilen(), [])

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, "WARNING")
        meldung: str = log.records[0].getMessage()
        self.assertIn("turn_id leer", meldung)
        self.assertIn("2 neue Keys", meldung)

    # ── c) DB-Insert wirft -> genau 1 ERROR, keine Exception ─────

    def test_c_db_fehler_loggt_genau_einen_error_und_wirft_nicht(self) -> None:
        fehler = psycopg2.OperationalError("Verbindung zur Datenbank verloren")

        with patch.object(VerbindungRepository, "insert", side_effect=fehler):
            with self.assertLogs(DISPATCHER_LOGGER, level="ERROR") as log:
                anzahl: int = _verbindung_schreiben(
                    turn_id      = self.turn_id,
                    rolle        = "user",
                    neue_keys    = [self.key_a, self.key_b],
                    postgres_url = POSTGRES_URL,
                )

        self.assertEqual(anzahl, 0)
        self.assertEqual(self._zeilen(), [])

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, "ERROR")
        self.assertIn("verbindung-Insert fehlgeschlagen", log.records[0].getMessage())

    def test_c_dispatcher_rueckgabe_bleibt_bei_db_fehler_unveraendert(self) -> None:
        """Der Turn laeuft weiter: dispatch() liefert seinen State wie sonst."""
        state: dict = {
            # user_id = Assistent -> _delegation_trigger_pruefen kehrt sofort
            # zurueck; ohne character_id steigen Session-Turn, turn_roh und die
            # Redis-Snapshots regulaer frueh aus. Uebrig bleibt der KZG-Block.
            "user_id":        ASSISTANT_USER_ID,
            "turn_id":        self.turn_id,
            "ei_calc_rolle":  "user",
            "pending_writes": [
                {"ziel": "kzg", "aktion": "create", "daten": {"salienz_obj": {}}},
            ],
        }

        kzg_ergebnis: dict = {
            "kzg_verarbeitet":      2,
            "kzg_neue_keys":        [self.key_a, self.key_b],
            "kzg_verstaerkte_keys": [],
        }

        with patch("graph.nodes.dispatcher.dispatch_kzg", return_value=kzg_ergebnis):
            with patch.object(
                VerbindungRepository, "insert",
                side_effect=psycopg2.OperationalError("Verbindung zur Datenbank verloren"),
            ):
                with self.assertLogs(DISPATCHER_LOGGER, level="ERROR") as log:
                    ergebnis = dispatch(
                        state        = state,
                        redis_client = redis_client,
                        postgres_url = POSTGRES_URL,
                    )

        self.assertIs(ergebnis, state)
        self.assertEqual(ergebnis["pending_writes"], [])
        self.assertEqual(self._zeilen(), [])

        self.assertEqual(len(log.records), 1)
        self.assertIn("verbindung-Insert fehlgeschlagen", log.records[0].getMessage())

    # ── d) nur verstaerkte Keys -> 0 Zeilen (E8) ─────────────────

    def test_d_nur_verstaerkte_keys_ergeben_keine_zeile(self) -> None:
        """E8: Der Dispatcher reicht verstaerkte Keys gar nicht erst weiter."""
        anzahl: int = _verbindung_schreiben(
            turn_id      = self.turn_id,
            rolle        = "user",
            neue_keys    = [],
            postgres_url = POSTGRES_URL,
        )

        self.assertEqual(anzahl, 0)
        self.assertEqual(self._zeilen(), [])

    def test_e_mischfall_schreibt_nur_den_neuen_key(self) -> None:
        """E8 mit Biss: ein neuer und ein verstaerkter Key im selben Turn.

        Fall d allein kann nicht rot werden, wenn der Insert verschwindet — er
        erwartet ohnehin null Zeilen. Dieser Fall prueft dieselbe Regel mit einer
        positiven Erwartung: genau eine Zeile, und zwar die des neuen Keys.
        """
        state: dict = {
            "user_id":        ASSISTANT_USER_ID,
            "turn_id":        self.turn_id,
            "ei_calc_rolle":  "character",
            "pending_writes": [
                {"ziel": "kzg", "aktion": "create", "daten": {"salienz_obj": {}}},
            ],
        }

        kzg_ergebnis: dict = {
            "kzg_verarbeitet":      1,
            "kzg_neue_keys":        [self.key_a],
            "kzg_verstaerkte_keys": [self.key_v],
        }

        with patch("graph.nodes.dispatcher.dispatch_kzg", return_value=kzg_ergebnis):
            dispatch(
                state        = state,
                redis_client = redis_client,
                postgres_url = POSTGRES_URL,
            )

        zeilen: list[dict] = self._zeilen()
        self.assertEqual(len(zeilen), 1)
        self.assertEqual(zeilen[0]["kzg_id"], self.key_a)
        self.assertEqual(zeilen[0]["turn_id"], self.turn_id)
        self.assertNotIn(self.key_v, [z["kzg_id"] for z in zeilen])


if __name__ == "__main__":
    unittest.main()
