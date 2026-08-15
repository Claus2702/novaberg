"""Tests fuer das Schema der Shadow-Queue nach dem Umzug (`novaberg-queue-verfall_k.md` §8).

Ziel: Ein Schreiber, der einen Auftrag ohne Gegenueber, ohne Beobachter, ohne
Gegenstand oder ohne Salienz einreihen will, scheitert **laut an der
Datenbank** — statt eine Zeile mit erfundenem Vorgabewert abzulegen.

Hintergrund: Die Queue lag bis zum 15.08.2026 als Redis-Liste. Dort kann eine
Zeile nichts erzwingen, und genau das war messbar — 233 von 1036 Auftraegen
trugen Salienz 0.0, weil ein Aufrufer das Argument ausliess und die Signatur
einen Vorgabewert trug (`KANDIDATEN-PRIORITAET-STILLE-NULL`). **Die Sperre
wandert damit von der Signatur in das Schema**, wo kein zweiter Aufrufer sie
umgehen kann.

Die Tabelle traegt zusaetzlich die Verfallsfelder nach dem Vorbild von
`lzg_knoten`: drei Salienz-Staende, `haeufigkeit`, `aktiv` und zwei Uhren.
`aktiv` ist der Soft-Delete — ein verfallener Auftrag verschwindet nicht, er
ruht (§12.1).

Die Zeugen:

  * Die erwartete Spaltenliste ist ein **Literal**, von Hand aus dem Konzept
    abgeleitet — nicht aus `db/init.sql` gelesen. Sonst prueft der Test die
    Schemadatei gegen sich selbst und bliebe auch dann gruen, wenn sie nie
    ausgefuehrt wurde.
  * Die Verstoesse werden **live** versucht, nicht aus dem Katalog erschlossen.
    Eine Spalte, die im Katalog NOT NULL heisst, ist erst dann eine Sperre,
    wenn ein Schreibversuch ohne Wert tatsaechlich scheitert.

Beide Haelften werden gebraucht: Der Katalog belegt, dass die Spalte keinen
Vorgabewert hat, der Live-Lauf belegt, dass der fehlende Wert abgewiesen wird.

Die DB-Tests bringen ihr Fixture selbst mit (eigenes Paar-Tripel), lesen
ausschliesslich darin und raeumen es in tearDown ab: Die Suite laeuft gegen die
Produktiv-Datenbank.

Kein skipUnless, kein skipIf, kein try/except um Importe: Fehlt die Tabelle,
wird dieser Test rot — er ueberspringt sich nicht.
"""

import unittest
import uuid

import psycopg2
from config import POSTGRES_URL
from psycopg2 import errors

TABELLE:          str = "shadow_auftrag"
INDEX_WAHL:       str = "idx_shadow_auftrag_wahl"
INDEX_GEGENSTAND: str = "idx_shadow_auftrag_gegenstand"

# Spaltenname -> (darf NULL sein, hat einen Vorgabewert).
# Von Hand aus `novaberg-queue-verfall_k.md` §8 abgeleitet, nicht aus db/init.sql.
ERWARTETE_SPALTEN: dict[str, tuple[bool, bool]] = {
    "id":              (False, True),
    "user_id":         (False, False),
    "character_id":    (False, False),
    "beobachter":      (False, False),
    "aufgabe":         (False, False),
    "thema":           (False, False),
    "kontext":         (False, True),
    "intentionen":     (False, True),
    "emotion":         (False, True),
    "modus":           (False, True),
    # **NULL-faehig und ohne Vorgabewert, und das ist die Zusicherung.**
    # Die Erregung des ausloesenden Turns liegt nicht immer vor — die
    # Salienz-Quelle liefert stellenweise selbst `null`. Ein Vorgabewert 0.5
    # waere hier die stille Null: ein gueltig aussehender Messwert, der nie
    # gemessen wurde. NULL heisst unbekannt, und der Leser prueft darauf.
    "arousal":         (True,  False),
    "salienz_roh":     (False, False),
    "salienz_absolut": (False, False),
    "salienz_decay":   (False, False),
    "haeufigkeit":     (False, True),
    "aktiv":           (False, True),
    "erstellt_am":     (False, True),
    "verstaerkt_am":   (False, True),
    "decay_am":        (False, True),
    "versuche":        (False, True),
}

# Die acht Spalten, deren fehlender Vorgabewert die Zusicherung des Bauteils
# traegt: das Paar-Tripel, der Gegenstand und die drei Salienz-Staende.
OHNE_VORGABEWERT: tuple[str, ...] = (
    "user_id", "character_id", "beobachter", "aufgabe", "thema",
    "salienz_roh", "salienz_absolut", "salienz_decay",
)

EINFUEGE_SPALTEN: tuple[str, ...] = (
    "user_id", "character_id", "beobachter", "aufgabe", "thema",
    "salienz_roh", "salienz_absolut", "salienz_decay",
)

EINFUEGE_SQL: str = """
    INSERT INTO shadow_auftrag
        (user_id, character_id, beobachter, aufgabe, thema,
         salienz_roh, salienz_absolut, salienz_decay)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

# Das Fixture-Paar ist bewusst kein echtes: Ein Test unter einer produktiven
# Kennung faende spaeter fremde Zeilen mit und raeumte sie in tearDown ab.
MENSCH:    str = "test_queue_mensch"
CHARAKTER: str = "test_queue_nova"


class SchemaGestaltTest(unittest.TestCase):
    """Die Tabelle existiert im laufenden Schema und hat die vereinbarte Gestalt."""

    def setUp(self) -> None:
        """Liest den Spaltenkatalog der Tabelle einmal fuer alle Faelle."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT column_name, is_nullable, column_default, udt_name
                    FROM   information_schema.columns
                    WHERE  table_schema = 'public' AND table_name = %s
                    """,
                    (TABELLE,),
                )
                self.katalog: dict[str, tuple[bool, bool, str]] = {
                    zeile[0]: (zeile[1] == "YES", zeile[2] is not None, zeile[3])
                    for zeile in cur.fetchall()
                }
        finally:
            conn.close()

    def test_a_tabelle_existiert(self) -> None:
        """Die Tabelle ist im laufenden Schema angelegt, nicht nur in der Datei."""
        self.assertTrue(
            self.katalog,
            f"{TABELLE} existiert nicht in der laufenden Datenbank. Die "
            f"Schemadatei zuendet nicht selbst — sie wird erst beim naechsten "
            f"Serverstart angewandt.",
        )

    def test_b_spaltenmenge_stimmt(self) -> None:
        """Kein Feld fehlt und keines ist ueber das Konzept hinaus dazugekommen."""
        self.assertEqual(
            sorted(ERWARTETE_SPALTEN),
            sorted(self.katalog),
            "Die Spaltenmenge weicht von novaberg-queue-verfall_k.md §8 ab.",
        )

    def test_c_nullbarkeit_und_vorgabewerte(self) -> None:
        """Jede Spalte traegt die vereinbarte Nullbarkeit und den vereinbarten Vorgabewert."""
        for spalte, (darf_null, hat_default) in ERWARTETE_SPALTEN.items():
            with self.subTest(spalte=spalte):
                self.assertIn(spalte, self.katalog)
                self.assertEqual(darf_null, self.katalog[spalte][0], f"Nullbarkeit: {spalte}")
                self.assertEqual(hat_default, self.katalog[spalte][1], f"Vorgabewert: {spalte}")

    def test_d_kein_vorgabewert_fuer_paar_gegenstand_salienz(self) -> None:
        """Acht Spalten haben keinen Vorgabewert — ein Weglassen wird nicht gefuellt.

        Steht als eigener Fall neben test_c, weil genau diese acht die
        Zusicherung des Bauteils tragen. Eine 0.0 in einem Salienz-Feld saehe
        wie ein Messwert aus; genau so entstanden 233 stille Nullen.
        """
        for spalte in OHNE_VORGABEWERT:
            with self.subTest(spalte=spalte):
                self.assertIn(spalte, self.katalog)
                self.assertFalse(self.katalog[spalte][0], f"{spalte} muss NOT NULL sein")
                self.assertFalse(self.katalog[spalte][1], f"{spalte} darf keinen Default haben")

    def test_e_intentionen_ist_ein_textfeld_array(self) -> None:
        """Die Intentionen reisen als Array, nicht als JSON-Zeichenkette."""
        self.assertIn("intentionen", self.katalog)
        self.assertEqual(
            "_text", self.katalog["intentionen"][2],
            "intentionen muss TEXT[] sein — als Zeichenkette waere jede Abfrage "
            "darauf eine Textsuche.",
        )

    def test_f_index_fuer_die_auswahl(self) -> None:
        """Die Auswahl findet den dringlichsten aktiven Auftrag eines Paares ueber einen Index."""
        definition: str = self._indexdefinition(INDEX_WAHL)
        for bestandteil in ("user_id", "character_id", "aktiv", "salienz_decay"):
            with self.subTest(bestandteil=bestandteil):
                self.assertIn(bestandteil, definition)
        self.assertIn(
            "DESC", definition.upper(),
            "salienz_decay muss absteigend indiziert sein — die Auswahl nimmt "
            "den hoechsten Wert (§12.3).",
        )

    def test_g_index_fuer_den_gegenstand(self) -> None:
        """Die Reaktivierung findet denselben Gegenstand desselben Paares ueber einen Index."""
        definition: str = self._indexdefinition(INDEX_GEGENSTAND)
        for bestandteil in ("user_id", "character_id", "aufgabe", "thema"):
            with self.subTest(bestandteil=bestandteil):
                self.assertIn(bestandteil, definition)

    def _indexdefinition(self, name: str) -> str:
        """Liest die Definition eines Index — oder laesst den Fall scheitern."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT indexdef FROM pg_indexes WHERE tablename = %s AND indexname = %s",
                    (TABELLE, name),
                )
                treffer = cur.fetchone()
        finally:
            conn.close()

        self.assertIsNotNone(treffer, f"Index {name} fehlt")
        return treffer[0]


class LauteSperrenTest(unittest.TestCase):
    """Die Sperren sind live wirksam, nicht nur im Katalog verzeichnet."""

    def setUp(self) -> None:
        """Erzeugt eine testeigene Marke fuer das Thema."""
        self.marke: str = f"test_queue_{uuid.uuid4().hex}"

    def tearDown(self) -> None:
        """Loescht alle Zeilen, die dieser Test erzeugt haben koennte."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM shadow_auftrag WHERE user_id = %s OR thema = %s",
                    (MENSCH, self.marke),
                )
            conn.commit()
        finally:
            conn.close()

    def _werte(self) -> list:
        """Ein vollstaendiger, gueltiger Satz Werte in der Reihenfolge von EINFUEGE_SPALTEN."""
        return [MENSCH, CHARAKTER, "user", "recherche", self.marke, 0.80, 0.9764, 0.9764]

    def test_a_vollstaendige_zeile_gelingt(self) -> None:
        """Der positive Zwilling: Mit allen Pflichtwerten wird geschrieben.

        Ohne ihn belegte die Negativ-Reihe nur, dass irgendetwas scheitert —
        auch eine fehlende Tabelle laesst jeden Einfuegeversuch scheitern.
        """
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(EINFUEGE_SQL, self._werte())
                cur.execute(
                    "SELECT aktiv, haeufigkeit, versuche FROM shadow_auftrag WHERE thema = %s",
                    (self.marke,),
                )
                zeile = cur.fetchone()
            conn.commit()
        finally:
            conn.close()

        self.assertIsNotNone(zeile, "Die vollstaendige Zeile wurde nicht geschrieben.")
        self.assertTrue(zeile[0], "Ein neuer Auftrag ist aktiv.")
        self.assertEqual(1, zeile[1], "haeufigkeit beginnt bei 1.")
        self.assertEqual(0, zeile[2], "versuche beginnt bei 0, nicht bei NULL.")

    def test_b_jede_pflichtspalte_sperrt_einzeln(self) -> None:
        """Fuer jede der acht Spalten scheitert ein Schreibversuch ohne ihren Wert."""
        for spalte in OHNE_VORGABEWERT:
            with self.subTest(spalte=spalte):
                werte: list = self._werte()
                werte[EINFUEGE_SPALTEN.index(spalte)] = None

                conn = psycopg2.connect(POSTGRES_URL)
                try:
                    with conn.cursor() as cur, self.assertRaises(
                        errors.NotNullViolation,
                        msg=f"Ein Auftrag ohne {spalte} wurde angenommen.",
                    ):
                        cur.execute(EINFUEGE_SQL, werte)
                    conn.rollback()
                finally:
                    conn.close()


if __name__ == "__main__":
    unittest.main()
