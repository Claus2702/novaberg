"""Tests fuer das Schema der Wissens-Bibliothek (Wissensspeicher, WIS-2).

Ziel: Ein Schreiber, der eine Wissensdatei ohne Gegenueber, ohne Beobachter
oder ohne Salienz ablegen will, scheitert laut an der Datenbank — statt eine
Zeile mit erfundenem Vorgabewert abzulegen. Und zu einem Dateipfad gibt es
genau eine Metadatenzeile.

Hintergrund: `autonomous_wissen` traegt die Metadaten der Bibliothek, nicht
ihren Inhalt — der liegt als Datei ausserhalb des Git-Roots. Die Tabelle ist
die einzige Stelle, an der die Paar-Trennung des Wissens durchgesetzt werden
kann; ohne sie fiele Novas Wissen ueber den einen in ein Gespraech mit dem
anderen. Die Salienz ohne Vorgabewert stammt aus derselben Fehlerklasse, die
in der Shadow-Queue messbar ist: Dort trugen am 04.08.2026 49 von 650
Auftraegen Prioritaet 0.0, obwohl sie das Hochsalienz-Tor passiert hatten.

Die Zeugen:

  * Die erwartete Spaltenliste ist ein Literal, von Hand aus
    `novaberg-autonomous-wissen_k.md` §7.2 und §11 abgeleitet — nicht aus
    `db/init.sql` gelesen. Sonst prueft der Test die Schemadatei gegen sich
    selbst und bliebe auch dann gruen, wenn sie nie ausgefuehrt wurde.
  * Die Verstoesse werden LIVE versucht, nicht aus dem Katalog erschlossen.
    Eine Spalte, die im Katalog NOT NULL heisst, ist erst dann eine Sperre,
    wenn ein Schreibversuch ohne Wert tatsaechlich scheitert.

Beide Haelften werden gebraucht: Der Katalog belegt, dass die Spalte keinen
Vorgabewert hat (ein Weglassen also nicht still gefuellt wird), der Live-Lauf
belegt, dass der fehlende Wert abgewiesen wird.

Die DB-Tests bringen ihr Fixture selbst mit (eigener Dateipfad-Praefix), lesen
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

TABELLE:     str = "autonomous_wissen"
INDEX_AKTIV: str = "idx_autonomous_wissen_aktiv"

# Spaltenname -> (darf NULL sein, hat einen Vorgabewert).
# Von Hand aus dem Konzept abgeleitet, nicht aus db/init.sql gelesen.
ERWARTETE_SPALTEN: dict[str, tuple[bool, bool]] = {
    "id":               (False, True),
    "dateipfad":        (False, False),
    "user_id":          (False, False),
    "character_id":     (False, False),
    "beobachter":       (False, False),
    "thema":            (False, False),
    "zusammenfassung":  (False, False),
    "themen_embedding": (True,  False),
    "typ":              (False, False),
    "modus":            (False, False),
    "status":           (True,  False),
    "salienz_anfang":   (False, False),
    "gewicht_roh":      (False, False),
    "gewicht_absolut":  (False, False),
    "gewicht_decay":    (False, False),
    "haeufigkeit":      (False, True),
    "aktiv":            (False, True),
    "erstellt_am":      (False, True),
    "verstaerkt_am":    (False, True),
    "decay_am":         (False, True),
    # Die drei Kanaele, seit dem 18.08.2026 (Konzept §4.1). Alle vier
    # NULL-faehig und ohne Vorgabewert: NULL heisst "noch nicht erhoben".
    # **Noch ohne Schreiber** — die Spalten sind die Vorbedingung des
    # Kanal-Umbaus, nicht seine Umsetzung.
    "entitaet_ids":     (True,  False),
    "timeline_id":      (True,  False),
    "stichwoerter":     (True,  False),
    "suchtext":         (True,  False),
}

# Die vier Spalten, deren fehlender Vorgabewert die eigentliche Zusicherung
# ist: drei Teile des Paar-Schemas plus die ausloesende Salienz.
OHNE_VORGABEWERT: tuple[str, ...] = ("user_id", "character_id", "beobachter", "salienz_anfang")

# Die Reihenfolge der Platzhalter in EINFUEGE_SQL. Beides wird gemeinsam
# geaendert oder gar nicht.
EINFUEGE_SPALTEN: tuple[str, ...] = (
    "dateipfad", "user_id", "character_id", "beobachter", "thema",
    "zusammenfassung", "typ", "modus", "status", "salienz_anfang",
    "gewicht_roh", "gewicht_absolut", "gewicht_decay",
)

EINFUEGE_SQL: str = """
    INSERT INTO autonomous_wissen
        (dateipfad, user_id, character_id, beobachter, thema, zusammenfassung,
         typ, modus, status, salienz_anfang,
         gewicht_roh, gewicht_absolut, gewicht_decay)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Der Praefix trennt das Fixture vom Bestand. Die Kennungen sind bewusst keine
# echten: Ein Test unter einer produktiven Kennung faende spaeter fremde Zeilen
# mit und raeumte sie in tearDown ab.
PFAD_PRAEFIX: str = "/knowledge/autonomous/test_wis2_"
MENSCH:       str = "test_wis2_mensch"
CHARAKTER:    str = "test_wis2_nova"


class SchemaGestaltTest(unittest.TestCase):
    """Die Tabelle existiert im laufenden Schema und hat die vereinbarte Gestalt."""

    def setUp(self) -> None:
        """Liest den Spaltenkatalog der Tabelle einmal fuer alle Faelle."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT column_name, is_nullable, column_default, udt_name,
                           format_type(a.atttypid, a.atttypmod)
                    FROM   information_schema.columns c
                    JOIN   pg_attribute a
                      ON   a.attrelid = %s::regclass AND a.attname = c.column_name
                    WHERE  c.table_schema = 'public' AND c.table_name = %s
                    """,
                    (TABELLE, TABELLE),
                )
                self.katalog: dict[str, tuple[bool, bool, str, str]] = {
                    zeile[0]: (zeile[1] == "YES", zeile[2] is not None, zeile[3], zeile[4])
                    for zeile in cur.fetchall()
                }
        finally:
            conn.close()

    def test_a_tabelle_existiert(self) -> None:
        """Die Tabelle ist im laufenden Schema angelegt, nicht nur in der Datei."""
        self.assertTrue(
            self.katalog,
            f"{TABELLE} existiert nicht in der laufenden Datenbank. Die Schemadatei "
            f"zuendet nicht selbst — sie wird erst beim naechsten Serverstart angewandt.",
        )

    def test_b_spaltenmenge_stimmt(self) -> None:
        """Kein Feld fehlt und keines ist ueber das Konzept hinaus dazugekommen."""
        self.assertEqual(
            sorted(ERWARTETE_SPALTEN),
            sorted(self.katalog),
            "Die Spaltenmenge weicht vom Konzept ab (novaberg-autonomous-wissen_k.md §7.2, §11).",
        )

    def test_c_nullbarkeit_und_vorgabewerte(self) -> None:
        """Jede Spalte traegt die vereinbarte Nullbarkeit und den vereinbarten Vorgabewert."""
        for spalte, (darf_null, hat_default) in ERWARTETE_SPALTEN.items():
            with self.subTest(spalte=spalte):
                self.assertIn(spalte, self.katalog)
                self.assertEqual(darf_null, self.katalog[spalte][0], f"Nullbarkeit: {spalte}")
                self.assertEqual(hat_default, self.katalog[spalte][1], f"Vorgabewert: {spalte}")

    def test_d_kein_vorgabewert_fuer_paar_und_salienz(self) -> None:
        """Paar-Schema und Salienz haben keinen Vorgabewert — ein Weglassen wird nicht gefuellt.

        Steht als eigener Fall neben test_c, weil genau diese vier Spalten die
        Zusicherung des Bauteils tragen: Ein Vorgabewert an dieser Stelle
        saehe spaeter wie ein Messwert aus (§11.4).
        """
        for spalte in OHNE_VORGABEWERT:
            with self.subTest(spalte=spalte):
                self.assertIn(spalte, self.katalog)
                self.assertFalse(self.katalog[spalte][0], f"{spalte} muss NOT NULL sein")
                self.assertFalse(self.katalog[spalte][1], f"{spalte} darf keinen Default haben")

    def test_e_embedding_hat_die_dimension_des_bestands(self) -> None:
        """Das Themen-Embedding ist ein Vektor mit 768 Dimensionen wie im uebrigen Bestand."""
        self.assertIn("themen_embedding", self.katalog)
        self.assertEqual("vector", self.katalog["themen_embedding"][2])
        self.assertEqual("vector(768)", self.katalog["themen_embedding"][3])

    def test_f_partieller_index_auf_paar_und_typ(self) -> None:
        """Der Lesepfad kann auf Paar, Typ und aktiv filtern, ohne die Tabelle zu lesen."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT indexdef FROM pg_indexes WHERE tablename = %s AND indexname = %s",
                    (TABELLE, INDEX_AKTIV),
                )
                treffer = cur.fetchone()
        finally:
            conn.close()

        self.assertIsNotNone(treffer, f"Index {INDEX_AKTIV} fehlt")
        definition: str = treffer[0]
        for bestandteil in ("user_id", "character_id", "typ", "aktiv"):
            with self.subTest(bestandteil=bestandteil):
                self.assertIn(bestandteil, definition)


class LauteSperrenTest(unittest.TestCase):
    """Die Sperren sind live wirksam, nicht nur im Katalog verzeichnet."""

    def setUp(self) -> None:
        """Erzeugt einen testeigenen Dateipfad."""
        self.marke:     str = uuid.uuid4().hex
        self.dateipfad: str = f"{PFAD_PRAEFIX}{self.marke}.md"

    def tearDown(self) -> None:
        """Loescht alle Zeilen, die dieser Test erzeugt haben koennte."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM autonomous_wissen WHERE dateipfad LIKE %s", (
                    f"{PFAD_PRAEFIX}%",
                ))
            conn.commit()
        finally:
            conn.close()

    def _werte(self) -> list[object]:
        """Baut einen vollstaendigen, gueltigen Parametersatz in der Reihenfolge der Spalten."""
        return [
            self.dateipfad, MENSCH, CHARAKTER, "nova",
            "Testthema WIS-2", "Zusammenfassung des Testthemas",
            "wissen", "recherche", "echte_tiefe", 0.72,
            1.0, 1.56, 1.56,
        ]

    def _einfuegen(self, werte: list[object]) -> None:
        """Fuehrt genau einen INSERT aus und schliesst die Verbindung in jedem Fall.

        Eine eigene Verbindung je Versuch, weil ein gescheiterter INSERT die
        laufende Transaktion abbricht und jeden folgenden Befehl derselben
        Verbindung mit einer Folgemeldung quittieren wuerde.
        """
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(EINFUEGE_SQL, werte)
            conn.commit()
        finally:
            conn.close()

    def test_a_vollstaendige_zeile_wird_geschrieben(self) -> None:
        """Die Gegenprobe: Mit allen Pflichtfeldern gelingt der Schreibvorgang.

        Ohne diesen Fall belegten die vier Verstoss-Faelle auch eine Tabelle,
        die ueberhaupt nichts annimmt.
        """
        self._einfuegen(self._werte())

        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT user_id, character_id, beobachter, salienz_anfang,
                           haeufigkeit, aktiv
                    FROM   autonomous_wissen
                    WHERE  dateipfad = %s
                    """,
                    (self.dateipfad,),
                )
                zeile = cur.fetchone()
        finally:
            conn.close()

        self.assertIsNotNone(zeile, "Die Zeile wurde nicht geschrieben")
        self.assertEqual((MENSCH, CHARAKTER, "nova"), zeile[0:3])
        self.assertAlmostEqual(0.72, zeile[3])
        self.assertEqual(1, zeile[4], "haeufigkeit startet bei 1")
        self.assertTrue(zeile[5], "aktiv startet auf TRUE")

    def test_b_fehlender_pflichtwert_scheitert_laut(self) -> None:
        """Paar-Schema und Salienz ohne Wert werden abgewiesen, nicht gefuellt."""
        for spalte in OHNE_VORGABEWERT:
            with self.subTest(spalte=spalte):
                werte: list[object] = self._werte()
                werte[EINFUEGE_SPALTEN.index(spalte)] = None
                with self.assertRaises(errors.NotNullViolation):
                    self._einfuegen(werte)

    def test_c_zweite_zeile_zum_selben_pfad_ist_unmoeglich(self) -> None:
        """Eine Wissensdatei hat genau eine Metadatenzeile — die zweite scheitert.

        Die Verstaerkung eines Themas aktualisiert die vorhandene Zeile
        (§11.5). Ohne diese Sperre waere der Unterschied zwischen Verstaerken
        und Doppelt-Anlegen nicht bemerkbar.
        """
        self._einfuegen(self._werte())
        with self.assertRaises(errors.UniqueViolation):
            self._einfuegen(self._werte())


if __name__ == "__main__":
    unittest.main()
