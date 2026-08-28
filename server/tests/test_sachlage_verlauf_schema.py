"""Zeugen fuer das Sachlage-Gedaechtnis — Scheibe 4 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 4. Die Sachlage
wurde je Paar ueberschrieben (Redis, Verfall 4 h); die `pipeline_log`-Zeile
ist Forensik mit Vorhaltefrist. Damit gab es kein zweites Ende fuer die
Bruecke einer Zustellung zu ihrem Anlass. `sachlage_verlauf` protokolliert
je gerechnetem Turn ein Faktum — *die Sachlage dieses Turns war X* — und
verfaellt deshalb nicht (`F-VERFALL-1`: was als Faktum protokolliert,
bleibt; Turns verfallen auch nicht).

Zeugen dieser Datei:
  * **Die erwartete Spaltenliste ist ein Literal**, aus dem Konzept
    abgeleitet — nicht aus `db/init.sql` gelesen, sonst pruefte der Test
    die Schemadatei gegen sich selbst.
  * **`shadow_auftrag.ausloeser_turn_id` existiert** — NULL-faehig, ohne
    Vorgabewert: NULL heisst unbekannt, und der Altbestand traegt es.
  * **Der Embed-Text ist der `gegenstand`-Satz** (`F-EMBED-1`): aus der
    Zeile rekonstruierbar, eine benannte Funktion, Identitaet.
  * **Schreiben und Lesen sind ein Rundlauf** gegen die echte Tabelle: die
    Zeile traegt alle Felder, `turn_id` findet sie, die Vektorsuche findet
    die naechste und verwirft die fremde unter der Schwelle.

Die DB-Tests bringen ihr Fixture selbst mit (eigenes Paar, eigene turn_ids)
und raeumen es in tearDown ab: Die Suite laeuft gegen die Produktiv-Datenbank.

Kein skipUnless, kein skipIf, kein try/except um Importe: Fehlt die Tabelle,
wird dieser Test rot — er ueberspringt sich nicht.
"""

import unittest
import uuid

import psycopg2

from config import POSTGRES_URL
from memory.sachlage_history import (
    build_embed_text,
    history_nearest,
    history_read_turn,
    history_recent,
    history_write,
)

TABELLE: str = "sachlage_verlauf"
DIM:     int = 768

# Spaltenname -> (darf NULL sein, hat einen Vorgabewert).
# Von Hand aus `novaberg-thinking-lage_k.md` §4 (Scheibe 4) abgeleitet.
ERWARTETE_SPALTEN: dict[str, tuple[bool, bool]] = {
    "id":             (False, True),
    "turn_id":        (False, False),
    "user_id":        (False, False),
    "character_id":   (False, False),
    "thema":          (False, False),
    "gegenstand":     (False, False),
    "nutzerziel":     (False, False),
    "ausdrucksweise": (False, False),
    "objekte":        (False, False),
    "herkunft":       (False, False),
    # NULL-faehig: Faellt der Embed-Worker aus, steht das Faktum trotzdem —
    # nur die Vektorsuche findet die Zeile dann nicht. Kein Vorgabewert.
    "embedding":      (True,  False),
    "erstellt_am":    (False, True),
}


def _einheitsvektor(achse: int) -> list[float]:
    """Ein Vektor, der genau auf einer Achse liegt — Kosinus zu jedem
    anderen Achsenvektor ist 0, zu sich selbst 1.
    """
    v: list[float] = [0.0] * DIM
    v[achse] = 1.0
    return v


ARTEFAKT: dict = {
    "thema":          "Rettich-Bewaesserung",
    "gegenstand":     "Die Bewertung von Bewaesserungsmethoden fuer Rettich.",
    "nutzerziel":     "Der Nutzer will die schonendere Methode kennen.",
    "ausdrucksweise": "pruefend",
    "objekte": [
        {"name": "Bewaesserungsstrategie", "klasse": "anliegen", "akut": True,
         "gedeckt": {"Vergleichsmethoden": "genannt"}, "offen": ["Intervall"]},
    ],
    "herkunft": "fortgeschrieben",
}


class DasSchemaStehtTest(unittest.TestCase):
    """Die Tabelle und die Auftragsspalte existieren so, wie das Konzept sie nennt."""

    def _spalten(self, tabelle: str) -> dict[str, tuple[bool, bool]]:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT column_name, is_nullable, column_default
                    FROM   information_schema.columns
                    WHERE  table_schema = 'public' AND table_name = %s
                    """,
                    (tabelle,),
                )
                zeilen = cur.fetchall()
        finally:
            conn.close()
        return {
            name: (nullable == "YES", default is not None)
            for name, nullable, default in zeilen
        }

    def test_die_tabelle_traegt_genau_die_spalten_des_konzepts(self) -> None:
        """Nicht weniger — und nicht mehr: Eine ungenannte Spalte ist ein
        Bauteil ohne Konzept.
        """
        self.assertEqual(self._spalten(TABELLE), ERWARTETE_SPALTEN)

    def test_der_auftrag_traegt_die_ausloeser_turn_id(self) -> None:
        """NULL-faehig, ohne Vorgabewert: NULL heisst unbekannt."""
        spalten = self._spalten("shadow_auftrag")

        self.assertIn("ausloeser_turn_id", spalten)
        self.assertEqual(spalten["ausloeser_turn_id"], (True, False))

    def test_die_paarsuche_hat_einen_index(self) -> None:
        """Der Rueckfall sucht je Paar; ohne Index waechst die Suche mit
        jedem Turn, denn die Tabelle verfaellt nicht.
        """
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT indexname FROM pg_indexes WHERE tablename = %s",
                    (TABELLE,),
                )
                namen = {zeile[0] for zeile in cur.fetchall()}
        finally:
            conn.close()

        self.assertIn("idx_sachlage_verlauf_paar", namen)
        self.assertIn("idx_sachlage_verlauf_turn", namen)


class DerEmbedTextIstRekonstruierbarTest(unittest.TestCase):
    """F-EMBED-1: eine benannte Formel, aus der Zeile rekonstruierbar."""

    def test_der_text_ist_der_gegenstand(self) -> None:
        self.assertEqual(
            build_embed_text(ARTEFAKT["gegenstand"]), ARTEFAKT["gegenstand"],
        )

    def test_leerer_gegenstand_ist_laut(self) -> None:
        with self.assertRaises(ValueError):
            build_embed_text("   ")


class SchreibenUndLesenSindEinRundlaufTest(unittest.TestCase):
    """Gegen die echte Tabelle, mit eigenem Fixture."""

    def setUp(self) -> None:
        self.paar: tuple[str, str] = (f"zeuge-{uuid.uuid4().hex[:8]}", "nova")
        self.turn_ids: list[str] = []

    def tearDown(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"DELETE FROM {TABELLE} WHERE user_id = %s",  # noqa: S608 — Konstante
                    (self.paar[0],),
                )
            conn.commit()
        finally:
            conn.close()

    def _schreiben(
        self, achse: int, herkunft: str = "frisch",
        thema: str | None = None, vektor: list[float] | None = None,
    ) -> str:
        turn_id: str = f"zeuge-{uuid.uuid4().hex}"
        self.turn_ids.append(turn_id)
        zeilen_id = history_write(
            POSTGRES_URL,
            turn_id      = turn_id,
            user_id      = self.paar[0],
            character_id = self.paar[1],
            sachlage     = {**ARTEFAKT, "herkunft": herkunft,
                            **({"thema": thema} if thema else {})},
            embedding    = vektor if vektor is not None else _einheitsvektor(achse),
        )
        self.assertIsNotNone(zeilen_id)
        return turn_id

    def test_die_zeile_traegt_alle_felder(self) -> None:
        turn_id: str = self._schreiben(0)

        zeile = history_read_turn(POSTGRES_URL, turn_id)

        self.assertIsNotNone(zeile)
        self.assertEqual(zeile["thema"], ARTEFAKT["thema"])
        self.assertEqual(zeile["gegenstand"], ARTEFAKT["gegenstand"])
        self.assertEqual(zeile["objekte"], ARTEFAKT["objekte"])
        self.assertEqual(zeile["herkunft"], "frisch")
        self.assertEqual(zeile["turn_id"], turn_id)

    def test_unbekannte_turn_id_liefert_nichts(self) -> None:
        self.assertIsNone(history_read_turn(POSTGRES_URL, "gibt-es-nicht"))

    def test_die_vektorsuche_findet_die_naechste_zeile(self) -> None:
        """Zwei Zeilen auf zwei Achsen; die Suche mit Achse 1 trifft Zeile 1."""
        erste:  str = self._schreiben(1)
        self._schreiben(2)

        treffer = history_nearest(
            POSTGRES_URL, self.paar[0], self.paar[1],
            _einheitsvektor(1), min_kosinus=0.5,
        )

        self.assertIsNotNone(treffer)
        self.assertEqual(treffer["turn_id"], erste)
        self.assertGreater(treffer["kosinus"], 0.99)

    def test_unter_der_schwelle_gibt_es_keinen_treffer(self) -> None:
        """Die Gegenprobe: eine fremde Richtung findet nichts — sonst
        baute die Bruecke einen Uebergang zu einem Turn ohne Bezug.
        """
        self._schreiben(3)

        treffer = history_nearest(
            POSTGRES_URL, self.paar[0], self.paar[1],
            _einheitsvektor(4), min_kosinus=0.5,
        )

        self.assertIsNone(treffer)

    def test_die_suche_kann_das_eigene_thema_ausschliessen(self) -> None:
        """Scheibe 5: Wer nach einer frueheren Blase sucht, darf nicht die
        eigene finden — die naechste Zeile ist fast immer der Vorturn.
        """
        schraeg: list[float] = _einheitsvektor(6)
        schraeg[7] = 0.3
        fruehere: str = self._schreiben(6, thema="Gravitationslinse", vektor=schraeg)
        eigene:   str = self._schreiben(6, thema="Pulsare")

        ohne = history_nearest(
            POSTGRES_URL, self.paar[0], self.paar[1], _einheitsvektor(6), min_kosinus=0.5,
        )
        mit = history_nearest(
            POSTGRES_URL, self.paar[0], self.paar[1], _einheitsvektor(6), min_kosinus=0.5,
            ausser_thema="Pulsare",
        )

        self.assertEqual(ohne["turn_id"], eigene)
        self.assertEqual(mit["turn_id"], fruehere)
        self.assertEqual(mit["thema"], "Gravitationslinse")

    def test_der_verlauf_kommt_juengste_zuerst_und_begrenzt(self) -> None:
        """Scheibe 4, Nebenziel Kontext-Tab: die letzten Blasen des Paares."""
        erste  = self._schreiben(8, thema="Erste")
        zweite = self._schreiben(8, thema="Zweite")
        dritte = self._schreiben(8, thema="Dritte")

        zeilen = history_recent(POSTGRES_URL, self.paar[0], self.paar[1], limit=2)

        self.assertEqual([z["turn_id"] for z in zeilen], [dritte, zweite])
        self.assertEqual(zeilen[0]["thema"], "Dritte")
        self.assertNotIn("embedding", zeilen[0])
        self.assertEqual(history_recent(POSTGRES_URL, "anderes-paar", self.paar[1], limit=2), [])
        self.assertIsInstance(zeilen[0]["erstellt_am"], str)
        _ = erste

    def test_die_suche_bleibt_im_paar(self) -> None:
        """Die Sachlage eines anderen Paares ist kein Anlass fuer dieses."""
        self._schreiben(5)

        treffer = history_nearest(
            POSTGRES_URL, "anderes-paar", self.paar[1],
            _einheitsvektor(5), min_kosinus=0.5,
        )

        self.assertIsNone(treffer)

    def test_ohne_embedding_steht_das_faktum_trotzdem(self) -> None:
        """Ein Ausfall des Embed-Workers kostet die Vektorsuche, nicht die Zeile."""
        turn_id: str = f"zeuge-{uuid.uuid4().hex}"
        zeilen_id = history_write(
            POSTGRES_URL, turn_id=turn_id,
            user_id=self.paar[0], character_id=self.paar[1],
            sachlage=ARTEFAKT, embedding=None,
        )

        self.assertIsNotNone(zeilen_id)
        self.assertEqual(history_read_turn(POSTGRES_URL, turn_id)["turn_id"], turn_id)


if __name__ == "__main__":
    unittest.main()
