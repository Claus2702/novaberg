"""Tests fuer den lzg_id-Nachtrag der verbindung-Zeilen (Charakter-Resonanz, §11.2).

Ziel: Nach einer Promotion fuehrt jede verbindung-Zeile des promoteten
KZG-Keys auf ihren LZG-Knoten.

Die Faelle schreiben echte Zeilen in `verbindung`. Jede traegt eine testeigene
turn_id und testeigene kzg_ids (uuid4); tearDown raeumt genau diese ab.

Als Fremdschluessel-Ziel legt setUp sich **zwei eigene lzg_knoten an** und
raeumt sie wieder ab. Bis Chat 111 nahm der Test sich stattdessen zwei
beliebige bestehende Knoten — das lief nur, solange zufaellig welche da waren.
Der Reset vom 27.07.2026 hat die Tabelle geleert und alle neun Faelle rot
gemacht, ohne dass am Code etwas falsch war. Ein Test, der einen Bestand
voraussetzt, den er nicht selbst herstellt, prueft die Datenlage mit.

Der Knoten dient ausschliesslich als Fremdschluessel-Ziel — sein Inhalt geht
in keine Zusicherung ein. Deshalb genuegen die acht Pflichtspalten ohne
Default; Embedding, Themen und EI-Felder bleiben leer.

ABGRENZUNG: Geprueft wird der Nachtrag selbst. Dass er hinter allen drei
Promotions-Pfaden sitzt (Halbreaktivierung, Reinforcement, Neuanlage), ergibt
sich aus seiner Platzierung nach der Verzweigung und wird durch den Live-Lauf
belegt, nicht durch diese Datei.
"""

import unittest
import uuid
from unittest.mock import patch

import psycopg2

from config import POSTGRES_URL
from agents.synapsen_promotion.agent import SynapsenPromotionAgent
from memory.repositories.verbindung_repository import VerbindungRepository

PROMOTION_LOGGER: str = "ki_server.agents.synapsen_promotion"


class VerbindungNachtragTest(unittest.TestCase):

    def setUp(self) -> None:
        """Legt zwei Bruecken-Zeilen auf denselben KZG-Key an."""
        marke: str = uuid.uuid4().hex
        self.turn_id: str = f"test-nachtrag-{marke}"
        self.kzg_id:  str = f"kzg:test:nachtrag:{marke}"
        self.fremd_kzg_id: str = f"kzg:test:nachtrag:{marke}:fremd"

        self.knoten_id:  int = self._knoten_anlegen(f"{self.kzg_id}:fk1")
        self.knoten_id2: int = self._knoten_anlegen(f"{self.kzg_id}:fk2")

        # Zwei Zeilen — ein Turn kann denselben Eintrag mehrfach naehren.
        VerbindungRepository.insert(POSTGRES_URL, self.turn_id, self.kzg_id)
        VerbindungRepository.insert(POSTGRES_URL, self.turn_id, self.kzg_id)
        # Eine Zeile auf einem anderen Key — darf nie mitgeschrieben werden.
        VerbindungRepository.insert(POSTGRES_URL, self.turn_id, self.fremd_kzg_id)

    def tearDown(self) -> None:
        """Raeumt Bruecken-Zeilen und die beiden Fixture-Knoten ab.

        Reihenfolge: erst verbindung, dann lzg_knoten. Der Fremdschluessel
        traegt ON DELETE SET NULL, die Reihenfolge waere also unkritisch —
        sie steht trotzdem so da, damit sie es auch bleibt, wenn jemand die
        Regel spaeter auf CASCADE zieht.
        """
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM verbindung WHERE turn_id = %s", (self.turn_id,))
                cur.execute(
                    "DELETE FROM lzg_knoten WHERE id = ANY(%s)",
                    ([self.knoten_id, self.knoten_id2],),
                )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _knoten_anlegen(quell_key: str) -> int:
        """Legt einen Wegwerf-lzg_knoten an und liefert seine ID.

        Der Knoten ist reines Fremdschluessel-Ziel fuer verbindung.lzg_id;
        sein Inhalt geht in keine Zusicherung ein. Gesetzt werden nur die
        Pflichtspalten ohne Default.

        Vorbedingung: Postgres erreichbar, Tabelle lzg_knoten existiert.
        Nachbedingung: genau eine neue Zeile, deren ID zurueckgegeben wird.
        Fehlerfaelle: liefert das INSERT keine ID, ist die Tabelle nicht
            bespielbar — das ist ein echter Fehler und wird laut, nicht
            uebersprungen.
        """

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO lzg_knoten
                        (kzg_quell_key, user_id, inhalt, dimension,
                         gewicht_roh, gewicht_absolut, gewicht_decay,
                         kzg_erstellt_am)
                    VALUES (%s, 'test', 'Fixture fuer den lzg_id-Nachtrag.',
                            'test', 0.0, 0.0, 0.0, NOW())
                    RETURNING id
                    """,
                    (quell_key,),
                )
                zeile = cur.fetchone()
            conn.commit()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if not zeile:
            raise AssertionError(
                f"lzg_knoten-Fixture '{quell_key}' konnte nicht angelegt werden — "
                f"INSERT lieferte keine ID."
            )
        return int(zeile[0])

    def _lzg_ids(self, kzg_id: str) -> list:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT lzg_id FROM verbindung WHERE kzg_id = %s ORDER BY id",
                    (kzg_id,),
                )
                return [r[0] for r in cur.fetchall()]
        finally:
            conn.close()

    # ── Der Nachtrag schreibt ────────────────────────

    def test_alle_zeilen_des_keys_tragen_die_lzg_id(self):
        ergebnis = VerbindungRepository.lzg_id_nachtragen(
            POSTGRES_URL, self.kzg_id, self.knoten_id,
        )
        self.assertEqual(ergebnis, {"gefunden": 2, "geaendert": 2})
        self.assertEqual(self._lzg_ids(self.kzg_id), [self.knoten_id, self.knoten_id])

    def test_fremder_key_bleibt_unberuehrt(self):
        VerbindungRepository.lzg_id_nachtragen(POSTGRES_URL, self.kzg_id, self.knoten_id)
        self.assertEqual(self._lzg_ids(self.fremd_kzg_id), [None])

    def test_zweiter_lauf_schreibt_nichts_mehr(self):
        """Idempotent: gefunden bleibt, geaendert faellt auf 0."""
        VerbindungRepository.lzg_id_nachtragen(POSTGRES_URL, self.kzg_id, self.knoten_id)
        zweiter = VerbindungRepository.lzg_id_nachtragen(
            POSTGRES_URL, self.kzg_id, self.knoten_id,
        )
        self.assertEqual(zweiter, {"gefunden": 2, "geaendert": 0})

    def test_umgezogener_knoten_wird_korrigiert(self):
        """IS DISTINCT FROM statt IS NULL: ein anderes Ziel wird geschrieben."""
        VerbindungRepository.lzg_id_nachtragen(POSTGRES_URL, self.kzg_id, self.knoten_id)
        zweiter = VerbindungRepository.lzg_id_nachtragen(
            POSTGRES_URL, self.kzg_id, self.knoten_id2,
        )
        self.assertEqual(zweiter, {"gefunden": 2, "geaendert": 2})
        self.assertEqual(self._lzg_ids(self.kzg_id), [self.knoten_id2, self.knoten_id2])

    def test_leere_eingabe_wird_abgewiesen(self):
        with self.assertRaises(ValueError):
            VerbindungRepository.lzg_id_nachtragen(POSTGRES_URL, "", self.knoten_id)
        with self.assertRaises(ValueError):
            VerbindungRepository.lzg_id_nachtragen(POSTGRES_URL, self.kzg_id, 0)

    # ── Der Aufrufer in der Promotion ────────────────

    def test_agent_schreibt_und_meldet_die_zahlen(self):
        agent = SynapsenPromotionAgent()
        with self.assertLogs(PROMOTION_LOGGER, level="INFO") as log:
            geaendert: int = agent._verbindung_lzg_id_nachtragen(
                self.kzg_id, self.knoten_id, "meister", "nova",
            )
        self.assertEqual(geaendert, 2)
        self.assertEqual(self._lzg_ids(self.kzg_id), [self.knoten_id, self.knoten_id])

        meldungen = [r.getMessage() for r in log.records]
        self.assertTrue(any("2 von 2 Zeilen geschrieben" in m for m in meldungen), meldungen)

    def test_ohne_bruecken_zeile_genau_eine_info_ohne_defekt(self):
        """KZG-Eintraege ohne turn_id haben keine Zeile — kein Fehler, aber sichtbar."""
        agent = SynapsenPromotionAgent()
        unbekannt: str = f"kzg:test:nachtrag:{uuid.uuid4().hex}:ohnezeile"
        with self.assertLogs(PROMOTION_LOGGER, level="INFO") as log:
            geaendert: int = agent._verbindung_lzg_id_nachtragen(
                unbekannt, self.knoten_id, "meister", "nova",
            )
        self.assertEqual(geaendert, 0)
        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, "INFO")
        self.assertIn("ohne Treffer", log.records[0].getMessage())

    def test_db_fehler_loggt_genau_einen_error_und_wirft_nicht(self):
        agent = SynapsenPromotionAgent()
        fehler = psycopg2.OperationalError("Verbindung zur Datenbank verloren")
        with patch.object(VerbindungRepository, "lzg_id_nachtragen", side_effect=fehler):
            with self.assertLogs(PROMOTION_LOGGER, level="ERROR") as log:
                geaendert: int = agent._verbindung_lzg_id_nachtragen(
                    self.kzg_id, self.knoten_id, "meister", "nova",
                )
        self.assertEqual(geaendert, 0)
        self.assertEqual(self._lzg_ids(self.kzg_id), [None, None])
        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, "ERROR")
        self.assertIn("verbindung-Nachtrag fehlgeschlagen", log.records[0].getMessage())

    def test_fehlende_eingabe_loggt_error_statt_zu_werfen(self):
        agent = SynapsenPromotionAgent()
        with self.assertLogs(PROMOTION_LOGGER, level="ERROR") as log:
            geaendert: int = agent._verbindung_lzg_id_nachtragen(
                "", self.knoten_id, "meister", "nova",
            )
        self.assertEqual(geaendert, 0)
        self.assertEqual(len(log.records), 1)
        self.assertIn("uebersprungen", log.records[0].getMessage())


if __name__ == "__main__":
    unittest.main()
