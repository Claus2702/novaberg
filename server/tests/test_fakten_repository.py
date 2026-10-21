"""Zeugen für Schema und Repository von `fakten` — die Kanten des Faktengedächtnisses.

Was diese Datei zusichert:
  * **Die Spaltenliste ist ein Literal**, nicht aus `db/init.sql` gelesen — sonst
    prüfte der Test die Schemadatei gegen sich selbst.
  * **Jeder Fakt trägt seine Herkunft und seine Einwertigkeit**, beide Pflicht
    und ohne Vorgabewert; die Datenbank weist eine unbekannte Herkunft ab.
  * **Höchstens ein aktiver Wert je Paar, Subjekt und einwertiger Beziehung** —
    die Datenbank erzwingt es, nicht nur der Code.
  * **Jede Abfrage filtert nach dem Paar** (`user_id`, `character_id`).
  * **Kein Lesen schreibt**: `last_touched` ist der Anker des Verfalls.
  * **Eine Ablösung gilt ganz oder gar nicht**: Scheitert das Anlegen, bleibt
    nach dem Rollback der alte Wert aktiv.
  * **Die Stärke einer Kante setzt ihr Schreiber**: `staerke_decay` ist Pflicht
    ohne Vorgabewert, und `insert` schreibt 1.0.
  * **Jede Lesefunktion prüft ihre Zeilen**: Eine Zeile eines anderen Paares
    oder eine inaktive, wo die Abfrage aktive verlangt, ist ein Fehler.

Die Suite läuft gegen eine Wegwerf-Datenbank aus den Schemadateien des Baums.
Jedes Fixture bringt trotzdem ein eigenes Paar mit und räumt in tearDown ab.

Kein skipUnless, kein skipIf: Fehlt eine Spalte, wird dieser Test rot.
"""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.errors
import psycopg2.extras

from config import POSTGRES_URL
from memory.repositories.fakten_repository import FaktenRepository, NewFact, _verify_rows

# Spaltenname -> (darf NULL sein, hat einen Vorgabewert). Von Hand gesetzt.
FAKTEN_COLUMNS: dict[str, tuple[bool, bool]] = {
    "id":               (False, True),
    "user_id":          (False, False),
    "character_id":     (False, True),
    "subjekt_id":       (False, False),
    "attribut":         (False, False),
    "objekt_id":        (True,  False),
    "objekt_wert":      (True,  False),
    "fakt_text":        (False, False),
    "embedding":        (True,  False),
    "t_created":        (False, True),
    "t_valid":          (True,  False),
    "t_invalid":        (True,  False),
    "aktiv":            (False, True),
    "last_touched":     (False, True),
    "wiedervorlage_am": (True,  False),
    "herkunft":         (False, False),
    "einwertig":        (False, False),
    "timeline_id":      (True,  False),
    "staerke_decay":    (False, False),
    "decay_am":         (False, True),
}
# Spalte -> (Zieltabelle, Löschregel)
FAKTEN_FOREIGN_KEYS: dict[str, tuple[str, str]] = {
    "subjekt_id":  ("entitaeten", "NO ACTION"),
    "objekt_id":   ("entitaeten", "NO ACTION"),
    "timeline_id": ("timeline", "SET NULL"),
}
# Ein Zeitpunkt weit vor jedem Lauf: Ein Lesen, das last_touched nachzieht,
# schiebt ihn sichtbar auf heute.
ALTER_ANKER: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)
# Eine ID, die keine Entität trägt — das Anlegen scheitert am Fremdschlüssel.
FEHLENDE_ENTITAET: int = 2_000_000_000
VEKTOR: list[float] = [1.0] + [0.0] * 767
REPO_MODUL: str = "memory.repositories.fakten_repository"


def _columns() -> dict[str, tuple[bool, bool]]:
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT column_name, is_nullable = 'YES', column_default IS NOT NULL
                   FROM information_schema.columns WHERE table_name = 'fakten'""",
            )
            return {r[0]: (r[1], r[2]) for r in cur.fetchall()}
    finally:
        conn.close()


def _neu(
    text: str,
    wert: str | None = None,
    einwertig: bool = True,
    herkunft: str = "mensch",
    objekt_id: int | None = None,
    embedding: list[float] | None = None,
    timeline_id: int | None = None,
) -> NewFact:
    return NewFact(
        fakt_text=text, herkunft=herkunft, einwertig=einwertig,
        objekt_id=objekt_id, objekt_wert=wert, embedding=embedding,
        timeline_id=timeline_id,
    )


class TheColumnsExistTest(unittest.TestCase):
    """Spalten, Fremdschlüssel und der eindeutige Teilindex, gegen Literale gehalten."""

    def test_columns_with_nullability_and_default(self) -> None:
        self.assertEqual(_columns(), FAKTEN_COLUMNS)

    def test_foreign_keys_and_delete_rules(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT kcu.column_name, ccu.table_name, rc.delete_rule
                    FROM information_schema.referential_constraints rc
                    JOIN information_schema.key_column_usage kcu
                      ON kcu.constraint_name = rc.constraint_name
                    JOIN information_schema.constraint_column_usage ccu
                      ON ccu.constraint_name = rc.constraint_name
                    WHERE kcu.table_name = 'fakten'
                    """
                )
                gefunden = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
        finally:
            conn.close()
        self.assertEqual(gefunden, FAKTEN_FOREIGN_KEYS)

    def test_the_partial_index_is_unique(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT indexdef FROM pg_indexes WHERE indexname = %s",
                    ("uq_fakten_einwertig_aktiv",),
                )
                zeilen = cur.fetchall()
        finally:
            conn.close()
        self.assertEqual(len(zeilen), 1)
        self.assertIn("CREATE UNIQUE INDEX", zeilen[0][0])
        self.assertIn("(user_id, character_id, subjekt_id, attribut)", zeilen[0][0])
        self.assertIn("WHERE (aktiv AND einwertig)", zeilen[0][0])


class _PairFixture(unittest.TestCase):
    """Ein eigenes Paar, ein zweites Gegenüber, eine Entität und ein Termin."""

    def setUp(self) -> None:
        self.user = f"test-fakt-{uuid.uuid4().hex[:8]}"
        self.char = "nova-test"
        self.anderer = "andere-test"
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO entitaeten (user_id, name) VALUES (%s, 'Michael') RETURNING id",
                    (self.user,),
                )
                self.subjekt: int = cur.fetchone()[0]
                cur.execute(
                    """INSERT INTO timeline (user_id, event_time, event_type, title)
                       VALUES (%s, NOW(), 'termin', 'Umzug') RETURNING id""",
                    (self.user,),
                )
                self.termin: int = cur.fetchone()[0]
            conn.commit()
        finally:
            conn.close()

    def tearDown(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM fakten WHERE user_id = %s", (self.user,))
                cur.execute("DELETE FROM timeline WHERE user_id = %s", (self.user,))
                cur.execute("DELETE FROM entitaeten WHERE user_id = %s", (self.user,))
            conn.commit()
        finally:
            conn.close()

    def _anlegen(self, char: str, attribut: str, neu: NewFact) -> int:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                fakt_id = FaktenRepository.insert(
                    cur, self.user, char, self.subjekt, attribut, neu,
                )
            conn.commit()
        finally:
            conn.close()
        return fakt_id

    def _ausfuehren(self, sql: str, params: tuple) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
            conn.commit()
        finally:
            conn.close()

    def _zeilen(self) -> list[dict]:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM fakten WHERE user_id = %s ORDER BY id", (self.user,))
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def _roh_einfuegen(self, spalten: str, werte: str) -> None:
        """Schreibt mit rohem SQL an Repository und Python-Prüfung vorbei."""
        self._ausfuehren(
            f"INSERT INTO fakten (user_id, subjekt_id, attribut, objekt_wert, fakt_text"
            f"{spalten}) VALUES (%s, %s, 'wohnt_in', 'Kassel', 'roh'{werte})",
            (self.user, self.subjekt),
        )


class TheDatabaseChecksOriginAndValencyTest(_PairFixture):
    """Herkunft und Einwertigkeit prüft die Datenbank, nicht nur das Repository."""

    def test_a_complete_row_is_accepted(self) -> None:
        self._roh_einfuegen(", herkunft, einwertig, staerke_decay", ", 'mensch', TRUE, 1.0")
        self.assertEqual(len(self._zeilen()), 1)

    def test_altbestand_is_rejected(self) -> None:
        with self.assertRaises(psycopg2.IntegrityError):
            self._roh_einfuegen(
                ", herkunft, einwertig, staerke_decay", ", 'altbestand', TRUE, 1.0",
            )

    def test_a_row_without_herkunft_is_rejected(self) -> None:
        with self.assertRaises(psycopg2.IntegrityError):
            self._roh_einfuegen(", einwertig, staerke_decay", ", TRUE, 1.0")

    def test_a_row_without_einwertig_is_rejected(self) -> None:
        with self.assertRaises(psycopg2.IntegrityError):
            self._roh_einfuegen(", herkunft, staerke_decay", ", 'mensch', 1.0")


class TheStrengthIsSetByItsWriterTest(_PairFixture):
    """`staerke_decay` hat keinen Vorgabewert — wer schreibt, setzt sie."""

    def test_a_row_without_staerke_decay_is_rejected(self) -> None:
        with self.assertRaises(psycopg2.errors.NotNullViolation) as fehler:
            self._roh_einfuegen(", herkunft, einwertig", ", 'mensch', TRUE")
        self.assertIn("staerke_decay", str(fehler.exception))
        self.assertEqual(self._zeilen(), [])

    def test_a_row_with_staerke_decay_keeps_its_value(self) -> None:
        self._roh_einfuegen(", herkunft, einwertig, staerke_decay", ", 'mensch', TRUE, 0.25")
        self.assertEqual([z["staerke_decay"] for z in self._zeilen()], [0.25])

    def test_insert_writes_the_strength_of_a_new_edge(self) -> None:
        self._anlegen(self.char, "wohnt_in", _neu("Michael wohnt in Kassel", "Kassel"))
        # exp(−rate · 0) = 1: Die neue Kante hat noch nichts verloren.
        self.assertEqual([z["staerke_decay"] for z in self._zeilen()], [1.0])


class OneActiveValuePerSingleValuedRelationTest(_PairFixture):
    """Der eindeutige Teilindex — mit seinen zwei Zwillingen."""

    def test_a_second_active_single_value_is_rejected(self) -> None:
        self._anlegen(self.char, "wohnt_in", _neu("Michael wohnt in Kassel", "Kassel"))
        with self.assertRaises(psycopg2.IntegrityError):
            self._anlegen(self.char, "wohnt_in", _neu("Michael wohnt in Hamburg", "Hamburg"))
        self.assertEqual(len(self._zeilen()), 1)

    def test_two_active_multi_values_both_stand(self) -> None:
        self._anlegen(self.char, "hat_haustier", _neu("Michael hat Bello", "Bello", False))
        self._anlegen(self.char, "hat_haustier", _neu("Michael hat Mia", "Mia", False))
        self.assertEqual([z["aktiv"] for z in self._zeilen()], [True, True])

    def test_single_values_of_another_pair_both_stand(self) -> None:
        self._anlegen(self.char, "wohnt_in", _neu("Michael wohnt in Kassel", "Kassel"))
        self._anlegen(self.anderer, "wohnt_in", _neu("Michael wohnt in Hamburg", "Hamburg"))
        self.assertEqual([z["aktiv"] for z in self._zeilen()], [True, True])


class TheTimelineReferenceIsReleasedTest(_PairFixture):
    """Ein Fakt überlebt seinen Termin; nur der Verweis verschwindet."""

    def test_deleting_the_event_sets_null_and_keeps_the_fact(self) -> None:
        fakt_id = self._anlegen(
            self.char, "zieht_um", _neu("Michael zieht um", "Hamburg", timeline_id=self.termin),
        )
        self.assertEqual(self._zeilen()[0]["timeline_id"], self.termin)
        self._ausfuehren("DELETE FROM timeline WHERE id = %s", (self.termin,))
        zeilen = self._zeilen()
        self.assertEqual([(z["id"], z["timeline_id"]) for z in zeilen], [(fakt_id, None)])


class _TwoPairsFixture(_PairFixture):
    """Derselbe Fakt in zwei Paaren eines Menschen, mit Vektor und fälliger Wiedervorlage."""

    def setUp(self) -> None:
        super().setUp()
        kassel: NewFact = _neu("Michael wohnt in Kassel", "Kassel", embedding=VEKTOR)
        self.eigen = self._anlegen(self.char, "wohnt_in", kassel)
        self.fremd = self._anlegen(self.anderer, "wohnt_in", kassel)
        self._ausfuehren(
            """UPDATE fakten SET wiedervorlage_am = NOW() - INTERVAL '1 day', last_touched = %s
               WHERE user_id = %s""",
            (ALTER_ANKER, self.user),
        )

    def _alle_lesen(self) -> dict[str, list[int]]:
        """Ruft jede Lesefunktion im eigenen Paar und gibt die gelieferten IDs zurück."""
        url, user, char = POSTGRES_URL, self.user, self.char
        eigen = FaktenRepository.find_by_id(url, user, char, self.eigen)
        fremd = FaktenRepository.find_by_id(url, user, char, self.fremd)
        aktiv = FaktenRepository.find_aktiv(url, user, char, self.subjekt, "wohnt_in")
        return {
            "find_by_id": [z["id"] for z in (eigen, fremd) if z],
            "find_by_subjekt": [
                z["id"] for z in FaktenRepository.find_by_subjekt(url, user, char, self.subjekt)
            ],
            "find_aktiv": [aktiv["id"]] if aktiv else [],
            "find_similar": [
                z["id"] for z in FaktenRepository.find_similar(url, user, char, VEKTOR, 0.0)
            ],
            "find_historie": [
                z["id"] for z in FaktenRepository.find_historie(
                    url, user, char, self.subjekt, "wohnt_in",
                )
            ],
            "find_wiedervorlage_faellig": [
                z["id"] for z in FaktenRepository.find_wiedervorlage_faellig(url, user, char)
            ],
        }


class EveryQueryFiltersByThePairTest(_TwoPairsFixture):
    """Ein Fakt desselben Menschen mit anderem Gegenüber erreicht keine Funktion."""

    def test_no_read_returns_the_fact_of_another_character(self) -> None:
        gelesen = self._alle_lesen()
        self.assertEqual(gelesen, {name: [self.eigen] for name in gelesen})

    def test_writes_do_not_reach_another_character(self) -> None:
        url, user, char = POSTGRES_URL, self.user, self.char
        self.assertFalse(FaktenRepository.invalidate(url, user, char, self.fremd))
        self.assertFalse(FaktenRepository.set_wiedervorlage(url, user, char, self.fremd, None))
        fremd = [z for z in self._zeilen() if z["id"] == self.fremd][0]
        self.assertTrue(fremd["aktiv"])
        self.assertIsNotNone(fremd["wiedervorlage_am"])
        # Der Zwilling: im eigenen Paar treffen beide.
        self.assertTrue(FaktenRepository.set_wiedervorlage(url, user, char, self.eigen, None))
        self.assertTrue(FaktenRepository.invalidate(url, user, char, self.eigen))

    def test_an_incomplete_pair_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            FaktenRepository.find_by_subjekt(POSTGRES_URL, self.user, "", self.subjekt)


class NoReadWritesTest(_TwoPairsFixture):
    """Der Anker des Verfalls bewegt sich nur beim Schreiben."""

    def test_last_touched_is_unchanged_after_every_read(self) -> None:
        vorher = {z["id"]: (z["last_touched"], z["aktiv"]) for z in self._zeilen()}
        gelesen = self._alle_lesen()
        nachher = {z["id"]: (z["last_touched"], z["aktiv"]) for z in self._zeilen()}
        # Die Lesefunktionen haben den Fakt wirklich gefunden — sonst wäre
        # ein unverändertes last_touched kein Befund.
        self.assertTrue(all(ids == [self.eigen] for ids in gelesen.values()), gelesen)
        self.assertEqual(vorher[self.eigen], (ALTER_ANKER, True))
        self.assertEqual(nachher, vorher)


class ASingleValueIsReplacedWhollyTest(_PairFixture):
    """Ablösen auf dem Cursor des Aufrufers: ganz oder gar nicht."""

    def _abloesen(self, neu: NewFact) -> int:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                neue_id = FaktenRepository.abloesen(
                    cur, self.user, self.char, self.subjekt, "wohnt_in", neu,
                )
            conn.commit()
            return neue_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def test_kassel_is_replaced_by_hamburg(self) -> None:
        kassel = self._abloesen(_neu("Michael wohnt in Kassel", "Kassel"))
        hamburg = self._abloesen(_neu("Michael wohnt in Hamburg", "Hamburg"))
        zeilen = {z["id"]: z for z in self._zeilen()}
        self.assertEqual(sorted(zeilen), [kassel, hamburg])
        self.assertEqual(
            [i for i, z in zeilen.items() if z["aktiv"]], [hamburg],
        )
        self.assertIsNotNone(zeilen[kassel]["t_invalid"])
        self.assertIsNone(zeilen[hamburg]["t_invalid"])

    def test_a_failed_insert_keeps_kassel_active(self) -> None:
        kassel = self._abloesen(_neu("Michael wohnt in Kassel", "Kassel"))
        # Einmal an der Prüfung der Herkunft, einmal am Fremdschlüssel — beide
        # scheitern nach dem Invalidieren, im Anlegen.
        with self.assertRaises(ValueError):
            self._abloesen(_neu("Michael wohnt in Hamburg", "Hamburg", herkunft="altbestand"))
        with self.assertRaises(psycopg2.IntegrityError):
            self._abloesen(_neu("Michael wohnt woanders", objekt_id=FEHLENDE_ENTITAET))
        zeilen = self._zeilen()
        self.assertEqual([(z["id"], z["aktiv"], z["t_invalid"]) for z in zeilen],
                         [(kassel, True, None)])

    def test_a_multi_valued_relation_is_not_replaced(self) -> None:
        with self.assertRaises(ValueError):
            self._abloesen(_neu("Michael hat Bello", "Bello", einwertig=False))
        self.assertEqual(self._zeilen(), [])


class EveryReadVerifiesItsRowsTest(unittest.TestCase):
    """Jede Lesefunktion weist eine Zeile ab, die ihre Abfrage nicht liefern dürfte.

    Die Datenbank liefert eine solche Zeile nur, wenn eine Abfrage ihren Filter
    verliert; die Attrappe der Verbindung liefert sie hier mit Absicht. Der
    Zwilling im selben Aufbau: Eine Zeile des Paares geht durch jede Funktion.
    """

    USER: str = "test-fakt-attrappe"
    CHAR: str = "nova-test"

    def _zeile(self, **abweichung: object) -> dict:
        zeile: dict = {"id": 7, "user_id": self.USER, "character_id": self.CHAR, "aktiv": True}
        zeile.update(abweichung)
        return zeile

    def _lesen(self, funktion: str, zeile: dict) -> object:
        """Ruft eine Lesefunktion, deren Verbindung genau `zeile` liefert."""
        conn = MagicMock()
        conn.cursor.return_value.fetchone.return_value = zeile
        conn.cursor.return_value.fetchall.return_value = [zeile]
        url, user, char = "postgresql://attrappe", self.USER, self.CHAR
        aufrufe = {
            "find_by_id": lambda: FaktenRepository.find_by_id(url, user, char, 7),
            "find_by_subjekt": lambda: FaktenRepository.find_by_subjekt(url, user, char, 3),
            "find_aktiv": lambda: FaktenRepository.find_aktiv(url, user, char, 3, "wohnt_in"),
            "find_similar": lambda: FaktenRepository.find_similar(url, user, char, VEKTOR),
            "find_historie": lambda: FaktenRepository.find_historie(
                url, user, char, 3, "wohnt_in",
            ),
            "find_wiedervorlage_faellig": lambda: FaktenRepository.find_wiedervorlage_faellig(
                url, user, char,
            ),
        }
        with patch(f"{REPO_MODUL}.psycopg2.connect", return_value=conn) as verbinden:
            ergebnis = aufrufe[funktion]()
        # Die Attrappe wurde wirklich gerufen — sonst prüfte der Zeuge nichts.
        verbinden.assert_called_once_with(url)
        return ergebnis

    def _abgewiesen(self, funktion: str, zeile: dict, merkmal: str) -> None:
        with self.assertRaisesRegex(RuntimeError, f"fakten.{funktion}: .*{merkmal}"):
            self._lesen(funktion, zeile)

    def test_find_by_id_rejects_another_character(self) -> None:
        self._abgewiesen("find_by_id", self._zeile(character_id="andere"), "character_id")

    def test_find_by_subjekt_rejects_another_character(self) -> None:
        self._abgewiesen("find_by_subjekt", self._zeile(character_id="andere"), "character_id")

    def test_find_aktiv_rejects_another_character(self) -> None:
        self._abgewiesen("find_aktiv", self._zeile(character_id="andere"), "character_id")

    def test_find_similar_rejects_another_character(self) -> None:
        self._abgewiesen("find_similar", self._zeile(character_id="andere"), "character_id")

    def test_find_historie_rejects_another_character(self) -> None:
        self._abgewiesen("find_historie", self._zeile(character_id="andere"), "character_id")

    def test_find_wiedervorlage_faellig_rejects_another_character(self) -> None:
        self._abgewiesen(
            "find_wiedervorlage_faellig", self._zeile(character_id="andere"), "character_id",
        )

    def test_every_read_rejects_another_user(self) -> None:
        for funktion in ("find_by_id", "find_by_subjekt", "find_aktiv", "find_similar",
                         "find_historie", "find_wiedervorlage_faellig"):
            with self.subTest(funktion=funktion):
                self._abgewiesen(funktion, self._zeile(user_id="anderer"), "user_id")

    def test_an_inactive_row_is_rejected_where_the_query_wants_active(self) -> None:
        for funktion in ("find_by_id", "find_by_subjekt", "find_aktiv", "find_similar",
                         "find_wiedervorlage_faellig"):
            with self.subTest(funktion=funktion):
                self._abgewiesen(funktion, self._zeile(aktiv=False), "aktiv")

    def test_the_history_keeps_an_inactive_row(self) -> None:
        zeile = self._zeile(aktiv=False)
        self.assertEqual(self._lesen("find_historie", zeile), [zeile])

    def test_a_row_of_the_pair_passes_every_read(self) -> None:
        zeile = self._zeile()
        for funktion in ("find_by_id", "find_aktiv"):
            with self.subTest(funktion=funktion):
                self.assertEqual(self._lesen(funktion, zeile), zeile)
        for funktion in ("find_by_subjekt", "find_similar", "find_historie",
                         "find_wiedervorlage_faellig"):
            with self.subTest(funktion=funktion):
                self.assertEqual(self._lesen(funktion, zeile), [zeile])


class TheRowCheckTest(unittest.TestCase):
    """Der Prüfhelfer der Lesefunktionen für sich."""

    def test_a_missing_column_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "aktiv=keine Spalte"):
            _verify_rows("probe", [{"id": 1}], {"aktiv": True})

    def test_no_condition_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _verify_rows("probe", [{"id": 1}], {})

    def test_matching_and_empty_rows_pass_unchanged(self) -> None:
        zeilen = [{"id": 1, "aktiv": True}, {"id": 2, "aktiv": True}]
        self.assertIs(_verify_rows("probe", zeilen, {"aktiv": True}), zeilen)
        self.assertEqual(_verify_rows("probe", [], {"aktiv": True}), [])


if __name__ == "__main__":
    unittest.main()
