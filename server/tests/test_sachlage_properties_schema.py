"""Zeugen fuer das Eigenschaftsgedaechtnis — Scheibe 11 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 11. Die gedeckten
Eigenschaften eines Objekts lebten nur in der Blase (Redis, 4 h) und als JSON
in `sachlage_verlauf`. Seit Scheibe 11 hat jedes Objekt des Paares eine Zeile,
jeder Turn seine Objekte, und jede Eigenschaft ihren Wert mit Historie.

Zeugen dieser Datei:
  * **Die Spaltenlisten sind Literale**, aus dem Konzept abgeleitet — nicht aus
    `db/init.sql` gelesen, sonst pruefte der Test die Schemadatei gegen sich.
  * **Das Loeschverhalten ist eine Festlegung**, keine Implementierungsfrage: Entitaet
    und Zeitanker SET NULL (F-MAGNET-1), Objekt und Verlauf RESTRICT.
  * **Ein neuer Wert loest ab, statt zu ueberschreiben** (Entscheidung des
    Eigentuemers, 13.09.2026): der alte inaktiv mit `t_invalid` und Verweis
    auf den neuen, derselbe Wert eine Bestaetigung, ein verschwundener Wert
    bleibt aktiv.
  * **Hoechstens ein aktiver Wert je Objekt und Eigenschaft** — die Datenbank
    erzwingt es, nicht nur der Code.

Die Suite laeuft gegen die Produktiv-Datenbank: Das Fixture bringt ein eigenes
Paar mit und raeumt in tearDown ab.

Kein skipUnless, kein skipIf: Fehlt eine Tabelle, wird dieser Test rot.
"""

import unittest
import uuid

import psycopg2

from config import POSTGRES_URL
from memory.sachlage_history import history_write
from memory.sachlage_properties import (
    BINDING_TURN_MAGNET,
    active_properties,
    bind_entity,
    property_history,
    record_turn_objects,
    text_key,
    unbound_objects,
)

# Spaltenname -> (darf NULL sein, hat einen Vorgabewert). Von Hand aus dem Konzept.
OBJECT_COLUMNS: dict[str, tuple[bool, bool]] = {
    "id":               (False, True),
    "user_id":          (False, False),
    "character_id":     (False, False),
    "name":             (False, False),
    "name_schluessel":  (False, False),
    "klasse":           (True,  False),
    "entitaet_id":      (True,  False),
    "entitaet_bindung": (True,  False),
    "erstellt_am":      (False, True),
    "last_touched":     (False, True),
}
TURN_COLUMNS: dict[str, tuple[bool, bool]] = {
    "id":          (False, True),
    "verlauf_id":  (False, False),
    "objekt_id":   (False, False),
    "turn_id":     (False, False),
    "akut":        (False, False),
    "erstellt_am": (False, True),
}
PROPERTY_COLUMNS: dict[str, tuple[bool, bool]] = {
    "id":                     (False, True),
    "objekt_id":              (False, False),
    "eigenschaft":            (False, False),
    "eigenschaft_schluessel": (False, False),
    "wert":                   (False, False),
    "sprecher":               (True,  False),
    "quelle":                 (True,  False),
    "turn_id":                (False, False),
    "bestaetigt_turn_id":     (False, False),
    "timeline_id":            (True,  False),
    "aktiv":                  (False, True),
    "t_valid":                (False, True),
    "t_invalid":              (True,  False),
    "abgeloest_durch":        (True,  False),
    "last_touched":           (False, True),
}
# (Tabelle, Spalte) -> (Zieltabelle, Loeschregel)
FOREIGN_KEYS: dict[tuple[str, str], tuple[str, str]] = {
    ("sachlage_objekt", "entitaet_id"):          ("entitaeten", "SET NULL"),
    ("sachlage_objekt_turn", "verlauf_id"):      ("sachlage_verlauf", "RESTRICT"),
    ("sachlage_objekt_turn", "objekt_id"):       ("sachlage_objekt", "RESTRICT"),
    ("sachlage_eigenschaft", "objekt_id"):       ("sachlage_objekt", "RESTRICT"),
    ("sachlage_eigenschaft", "timeline_id"):     ("timeline", "SET NULL"),
    ("sachlage_eigenschaft", "abgeloest_durch"): ("sachlage_eigenschaft", "SET NULL"),
}


def _columns(table: str) -> dict[str, tuple[bool, bool]]:
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT column_name, is_nullable = 'YES', column_default IS NOT NULL
                   FROM information_schema.columns WHERE table_name = %s""",
                (table,),
            )
            return {r[0]: (r[1], r[2]) for r in cur.fetchall()}
    finally:
        conn.close()


class TheTablesExistTest(unittest.TestCase):
    def test_object_columns(self) -> None:
        self.assertEqual(_columns("sachlage_objekt"), OBJECT_COLUMNS)

    def test_turn_columns(self) -> None:
        self.assertEqual(_columns("sachlage_objekt_turn"), TURN_COLUMNS)

    def test_property_columns(self) -> None:
        self.assertEqual(_columns("sachlage_eigenschaft"), PROPERTY_COLUMNS)

    def test_foreign_keys_and_delete_rules(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT kcu.table_name, kcu.column_name, ccu.table_name, rc.delete_rule
                    FROM information_schema.referential_constraints rc
                    JOIN information_schema.key_column_usage kcu
                      ON kcu.constraint_name = rc.constraint_name
                    JOIN information_schema.constraint_column_usage ccu
                      ON ccu.constraint_name = rc.constraint_name
                    WHERE kcu.table_name IN
                      ('sachlage_objekt', 'sachlage_objekt_turn', 'sachlage_eigenschaft')
                    """
                )
                gefunden = {(r[0], r[1]): (r[2], r[3]) for r in cur.fetchall()}
        finally:
            conn.close()
        self.assertEqual(gefunden, FOREIGN_KEYS)


class _PairFixture(unittest.TestCase):
    """Ein eigenes Paar und zwei Verlaufszeilen; tearDown raeumt in Abhaengigkeitsfolge."""

    def setUp(self) -> None:
        self.user = f"test-eig-{uuid.uuid4().hex[:8]}"
        self.char = "nova-test"
        self.verlauf: list[int] = []
        for i in range(3):
            vid = history_write(
                POSTGRES_URL, turn_id=f"{self.user}-t{i}", user_id=self.user,
                character_id=self.char,
                sachlage={"thema": "Geburtstag", "gegenstand": "Ein Geburtstag",
                          "nutzerziel": "Planung", "ausdrucksweise": "erzaehlend",
                          "objekte": [], "herkunft": "frisch"},
                embedding=None,
            )
            self.assertIsNotNone(vid)
            self.verlauf.append(vid)

    def tearDown(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """DELETE FROM sachlage_eigenschaft WHERE objekt_id IN
                       (SELECT id FROM sachlage_objekt WHERE user_id = %s)""", (self.user,))
                cur.execute(
                    """DELETE FROM sachlage_objekt_turn WHERE objekt_id IN
                       (SELECT id FROM sachlage_objekt WHERE user_id = %s)""", (self.user,))
                cur.execute("DELETE FROM sachlage_objekt WHERE user_id = %s", (self.user,))
                cur.execute("DELETE FROM sachlage_verlauf WHERE user_id = %s", (self.user,))
            conn.commit()
        finally:
            conn.close()

    def _record(self, turn: int, gedeckt: dict, **objekt: object) -> object:
        basis: dict = {"name": "Geburtstag", "klasse": "vorgang", "akut": True,
                       "gedeckt": gedeckt, "offen": []}
        basis.update(objekt)
        return record_turn_objects(
            POSTGRES_URL, user_id=self.user, character_id=self.char,
            turn_id=f"{self.user}-t{turn}", verlauf_id=self.verlauf[turn],
            sachlage={"objekte": [basis]},
        )


class AValueIsReplacedNotOverwrittenTest(_PairFixture):
    def test_the_correction_stays_provable(self) -> None:
        """Erst der 1.7., dann der 1.8. — beide Werte bleiben, einer aktiv."""
        erst = self._record(0, {"wann": "1. Juli"}, sprecher={"wann": "nutzer"})
        dann = self._record(1, {"wann": "1. August"}, sprecher={"wann": "nutzer"})
        self.assertEqual((erst.new, dann.replaced), (1, 1))
        objekt_id = erst.object_ids["geburtstag"]
        historie = property_history(POSTGRES_URL, objekt_id, "wann")
        self.assertEqual([h["wert"] for h in historie], ["1. Juli", "1. August"])
        self.assertEqual([h["aktiv"] for h in historie], [False, True])
        self.assertIsNotNone(historie[0]["t_invalid"])
        self.assertEqual(historie[0]["abgeloest_durch"], historie[1]["id"])

    def test_the_same_value_is_a_confirmation(self) -> None:
        self._record(0, {"wann": "1. Juli"})
        zweites = self._record(1, {"wann": "  1. juli "})
        self.assertEqual((zweites.new, zweites.confirmed, zweites.replaced), (0, 1, 0))
        historie = property_history(POSTGRES_URL, zweites.object_ids["geburtstag"], "wann")
        self.assertEqual(len(historie), 1)
        self.assertEqual(historie[0]["bestaetigt_turn_id"], f"{self.user}-t1")

    def test_two_spellings_in_one_turn_are_one_value(self) -> None:
        """Zweite Kontrolle 13.09.2026: »Größe« und »Grösse« im selben Turn loesten einander ab."""
        ergebnis = self._record(0, {"Größe": "wie die Erde", "GRÖSSE": "etwa 12000 km"})
        self.assertEqual((ergebnis.new, ergebnis.replaced), (1, 0))

    def test_a_vanished_value_stays_active(self) -> None:
        erst = self._record(0, {"wann": "1. Juli"})
        self._record(1, {"anlass": "zehnter"})
        aktiv = active_properties(POSTGRES_URL, self.user, self.char, ["geburtstag"], 10)
        self.assertEqual(sorted(a["eigenschaft"] for a in aktiv), ["anlass", "wann"])
        self.assertEqual(erst.objects, 1)

    def test_one_object_row_and_one_turn_row_per_turn(self) -> None:
        self._record(0, {"wann": "1. Juli"})
        self._record(1, {"wann": "1. Juli"}, name="GEBURTSTAG")
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*), max(name) FROM sachlage_objekt WHERE user_id = %s",
                            (self.user,))
                anzahl, name = cur.fetchone()
                cur.execute(
                    """SELECT count(*) FROM sachlage_objekt_turn t JOIN sachlage_objekt o
                       ON o.id = t.objekt_id WHERE o.user_id = %s""", (self.user,))
                turns = cur.fetchone()[0]
        finally:
            conn.close()
        self.assertEqual((anzahl, name, turns), (1, "GEBURTSTAG", 2))

    def test_the_database_allows_one_active_value(self) -> None:
        erst = self._record(0, {"wann": "1. Juli"})
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur, self.assertRaises(psycopg2.IntegrityError):
                cur.execute(
                    """INSERT INTO sachlage_eigenschaft (objekt_id, eigenschaft,
                       eigenschaft_schluessel, wert, turn_id, bestaetigt_turn_id)
                       VALUES (%s, 'wann', 'wann', 'anders', 'x', 'x')""",
                    (erst.object_ids["geburtstag"],),
                )
        finally:
            conn.rollback()
            conn.close()


class TheEntityIsBoundLaterTest(_PairFixture):
    def test_an_object_waits_unbound_and_is_bound_once(self) -> None:
        erst = self._record(0, {"wann": "1. Juli"})
        offen = unbound_objects(POSTGRES_URL, self.user, self.char, ["geburtstag"], 5)
        self.assertEqual([o["turn_ids"] for o in offen], [[f"{self.user}-t0"]])
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM entitaeten ORDER BY id LIMIT 2")
                eins, zwei = (r[0] for r in cur.fetchall())
        finally:
            conn.close()
        objekt_id = erst.object_ids["geburtstag"]
        self.assertTrue(bind_entity(POSTGRES_URL, objekt_id, eins, BINDING_TURN_MAGNET))
        self.assertFalse(bind_entity(POSTGRES_URL, objekt_id, zwei, BINDING_TURN_MAGNET))
        self.assertEqual(unbound_objects(POSTGRES_URL, self.user, self.char, ["geburtstag"], 5), [])


class TextKeyTest(unittest.TestCase):
    def test_case_and_space(self) -> None:
        self.assertEqual(text_key("  Straße  am\tSee "), "strasse am see")


if __name__ == "__main__":
    unittest.main()
