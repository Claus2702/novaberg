"""Tests fuer die Themenvektoren der Wissens-Bibliothek (Konvention 4).

Ziel: Jedes einzelne Thema einer Ausarbeitung traegt einen eigenen Vektor, und
eine Frage nach genau diesem Thema findet die Ausarbeitung. Nicht ein
gemittelter Vektor ueber alle Themen einer Zeile.

Hintergrund und die Zahl, die dahintersteht: `autonomous_wissen.thema` traegt
im Mittel 4,37 durch Komma getrennte Themen (Maximum 17), und der Vektor der
Zeile wird ueberdies aus dem Destillat gebaut, nicht aus dem Themenfeld. Ueber
40 Fragen nach EINEM Thema gemessen fand die Bibliothek ihre eigene Zeile in
6 von 40 Faellen auf Rang 1, mit einem Kosinus-Median von 0,2821 — unterhalb
der eigenen Abweisungsschwelle von 0,40. Die richtige Antwort wurde also im
Regelfall verworfen, nicht nur schlecht gereiht. Mit einem Vektor je Thema:
31 von 40 und Median 0,7425.

**Der Inhaltsvektor bleibt und wird nicht ersetzt.** Der zweite Konsument der
Bibliothek — der Rueckweg — fragt mit Ø 833 Zeichen und hat keine Schwelle;
gegen das Destillat findet er die richtige Zeile 25 von 25 Mal unter den ersten
acht, gegen Themenvektoren 12 von 25, und die beiden Kandidatenlisten
ueberlappen im Median mit 1 von 8. Deshalb zwei Ziele nebeneinander und keine
Ablosung. Wer diese Datei aendert, liest zuerst `novaberg-convention-embedding.md`
§5.

Die Zeugen:

  * Die erwartete Spaltenliste ist ein Literal, von Hand aus der Konvention
    abgeleitet — nicht aus `db/init.sql` gelesen. Sonst prueft der Test die
    Schemadatei gegen sich selbst und bliebe gruen, auch wenn sie nie
    ausgefuehrt wurde.
  * Die Zusicherungen werden LIVE versucht, nicht aus dem Katalog erschlossen:
    ein Thema ohne Eintrag, ein doppeltes Thema am selben Eintrag, und das
    Mitloeschen beim Loeschen des Eintrags.
  * Der Loeschtest ist der einzige, der `ON DELETE CASCADE` belegen kann. Im
    Katalog steht die Regel; ob sie greift, zeigt nur ein Loeschvorgang.

Die DB-Tests bringen ihr Fixture selbst mit (eigener Dateipfad-Praefix), lesen
ausschliesslich darin und raeumen es in tearDown ab: Die Suite laeuft gegen die
Produktiv-Datenbank.

Kein skipUnless, kein skipIf, kein try/except um Importe: Fehlt die Tabelle,
wird dieser Test rot — er ueberspringt sich nicht.
"""

import unittest

import psycopg2
from config import POSTGRES_URL
from psycopg2 import errors

TABELLE:     str = "autonomous_wissen_thema"
INDEX_WISSEN: str = "idx_autonomous_wissen_thema_wissen"

# Spaltenname -> (darf NULL sein, hat einen Vorgabewert).
# Von Hand aus `novaberg-convention-embedding.md` §5 abgeleitet.
ERWARTETE_SPALTEN: dict[str, tuple[bool, bool]] = {
    "id":         (False, True),
    "wissen_id":  (False, False),
    "thema":      (False, False),
    # NULL-faehig und ohne Vorgabewert: NULL heisst "noch nicht eingebettet".
    # Ein Default waere hier genau das Muster, das eine fehlende Messung wie
    # eine vorhandene aussehen laesst — dieselbe Klasse wie `salienz_anfang`
    # in der Elterntabelle.
    "embedding":  (True,  False),
}

PFAD_PRAEFIX: str = "/knowledge/autonomous/test_konv4_"
MENSCH:       str = "test_konv4_mensch"
CHARAKTER:    str = "test_konv4_nova"

ELTERN_SQL: str = """
    INSERT INTO autonomous_wissen
        (dateipfad, user_id, character_id, beobachter, thema, zusammenfassung,
         typ, modus, status, salienz_anfang,
         gewicht_roh, gewicht_absolut, gewicht_decay)
    VALUES (%s, %s, %s, 'assistant', %s, 'Zusammenfassung', 'wissen',
            'recherche', 'echte_tiefe', 0.5, 0.5, 0.5, 0.5)
    RETURNING id
"""


def _verbindung() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(POSTGRES_URL)
    conn.autocommit = True
    return conn


class SchemaGestaltTest(unittest.TestCase):
    """Die Tabelle existiert im laufenden Schema und hat die vereinbarte Gestalt."""

    def setUp(self) -> None:
        conn = _verbindung()
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
                    z[0]: (z[1] == "YES", z[2] is not None, z[3])
                    for z in cur.fetchall()
                }
        finally:
            conn.close()

    def test_tabelle_existiert(self) -> None:
        """Ohne die Tabelle traegt kein einziges Thema einen eigenen Vektor."""
        self.assertTrue(
            self.katalog,
            f"Tabelle '{TABELLE}' fehlt im laufenden Schema — Konvention 4 ist "
            f"damit nicht umgesetzt, und jede Frage nach EINEM Thema faellt auf "
            f"den gemittelten Vektor der Zeile zurueck (gemessen 6 von 40 auf "
            f"Rang 1)",
        )

    def test_spalten_vollstaendig_und_ohne_ueberschuss(self) -> None:
        """Genau die vereinbarten Spalten, keine mehr und keine weniger."""
        self.assertEqual(
            set(ERWARTETE_SPALTEN), set(self.katalog),
            "Die Spaltenmenge weicht von der Konvention ab",
        )

    def test_nullbarkeit_und_vorgabewerte(self) -> None:
        """`embedding` ist nullbar ohne Default, alles andere ist Pflicht."""
        for spalte, (nullbar, hat_default) in ERWARTETE_SPALTEN.items():
            with self.subTest(spalte=spalte):
                ist = self.katalog[spalte]
                self.assertEqual(nullbar, ist[0], f"{spalte}: Nullbarkeit weicht ab")
                self.assertEqual(hat_default, ist[1], f"{spalte}: Vorgabewert weicht ab")

    def test_embedding_ist_ein_vektor(self) -> None:
        """Die Spalte traegt pgvector, nicht Text — sonst rechnet niemand damit."""
        self.assertEqual(
            "vector", self.katalog["embedding"][2],
            "embedding ist kein pgvector-Typ",
        )

    def test_index_auf_der_elternspalte(self) -> None:
        """Jeder Lesepfad joint ueber `wissen_id`; ohne Index ist das ein Scan."""
        conn = _verbindung()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pg_indexes WHERE schemaname='public' "
                    "AND tablename=%s AND indexname=%s",
                    (TABELLE, INDEX_WISSEN),
                )
                self.assertIsNotNone(
                    cur.fetchone(), f"Index '{INDEX_WISSEN}' fehlt",
                )
        finally:
            conn.close()


class ZusicherungenLiveTest(unittest.TestCase):
    """Die Sperren werden versucht, nicht aus dem Katalog erschlossen."""

    def setUp(self) -> None:
        self.conn = _verbindung()
        with self.conn.cursor() as cur:
            cur.execute(ELTERN_SQL, (f"{PFAD_PRAEFIX}a.md", MENSCH, CHARAKTER,
                                     "Larvalentwicklung, Verhaltensbiologie"))
            self.wissen_id: int = cur.fetchone()[0]

    def tearDown(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM autonomous_wissen WHERE dateipfad LIKE %s",
                        (f"{PFAD_PRAEFIX}%",))
        self.conn.close()

    def test_thema_ohne_eintrag_wird_abgewiesen(self) -> None:
        """Ein Themenvektor ohne Ausarbeitung ist gegenstandslos."""
        with self.conn.cursor() as cur:
            with self.assertRaises(errors.ForeignKeyViolation):
                cur.execute(
                    f"INSERT INTO {TABELLE} (wissen_id, thema) VALUES (%s, %s)",
                    (-1, "Larvalentwicklung"),
                )

    def test_dasselbe_thema_zweimal_am_selben_eintrag(self) -> None:
        """Zweimal dasselbe Thema waere zweimal derselbe Vektor im Ergebnis."""
        with self.conn.cursor() as cur:
            cur.execute(f"INSERT INTO {TABELLE} (wissen_id, thema) VALUES (%s, %s)",
                        (self.wissen_id, "Larvalentwicklung"))
            with self.assertRaises(errors.UniqueViolation):
                cur.execute(f"INSERT INTO {TABELLE} (wissen_id, thema) VALUES (%s, %s)",
                            (self.wissen_id, "Larvalentwicklung"))

    def test_dasselbe_thema_an_zwei_eintraegen_ist_erlaubt(self) -> None:
        """Zwei Ausarbeitungen duerfen dasselbe Thema behandeln."""
        with self.conn.cursor() as cur:
            cur.execute(ELTERN_SQL, (f"{PFAD_PRAEFIX}b.md", MENSCH, CHARAKTER,
                                     "Larvalentwicklung, Oekologie"))
            zweite_id: int = cur.fetchone()[0]
            cur.execute(f"INSERT INTO {TABELLE} (wissen_id, thema) VALUES (%s, %s)",
                        (self.wissen_id, "Larvalentwicklung"))
            cur.execute(f"INSERT INTO {TABELLE} (wissen_id, thema) VALUES (%s, %s)",
                        (zweite_id, "Larvalentwicklung"))
            cur.execute(f"SELECT count(*) FROM {TABELLE} WHERE thema = %s",
                        ("Larvalentwicklung",))
            self.assertEqual(2, cur.fetchone()[0])

    def test_speichern_legt_die_themenzeilen_selbst_an(self) -> None:
        """Der Weg vom Schreibpfad zur Themenzeile — und er war unbezeugt.

        **Gefunden von der Gegenprobe, nicht vom Bau.** Mit ausgehebelter
        `themen_zerlegen` wurden 9 Tests rot, vorhergesagt waren 12; die drei
        fehlenden waren genau die Live-Zusicherungen dieser Datei, weil sie
        ihre Themenzeilen per direktem INSERT anlegen und den Schreibpfad
        damit umgehen. **Kein einziger Zeuge prüfte, dass `speichern()` sie
        erzeugt** — und daran hängt, dass keiner der beiden Schreibwege in
        die Bibliothek die Zerlegung vergessen kann.
        """
        from memory.repositories.autonomous_wissen_repository import (
            AutonomousWissenRepository,
            WissensEintrag,
        )

        pfad: str = f"{PFAD_PRAEFIX}c.md"
        wissen_id: int = AutonomousWissenRepository.speichern(
            POSTGRES_URL,
            WissensEintrag(
                dateipfad=pfad, user_id=MENSCH, character_id=CHARAKTER,
                beobachter="assistant", thema="Larvalentwicklung, Oekologie, KI",
                zusammenfassung="Zusammenfassung", typ="wissen",
                modus="recherche", status="echte_tiefe", salienz_anfang=0.5,
            ),
        )
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT thema FROM {TABELLE} WHERE wissen_id = %s ORDER BY thema",
                (wissen_id,),
            )
            gefunden: list[str] = [z[0] for z in cur.fetchall()]

        self.assertEqual(
            ["KI", "Larvalentwicklung", "Oekologie"], gefunden,
            "speichern() hat die Themenzeilen nicht angelegt — eine Ausarbeitung "
            "ueber diesen Weg waere ueber den Bestell-Weg unauffindbar, und eine "
            "kurze Trefferliste sieht aus wie ein enger Bestand",
        )

    def test_speichern_ersetzt_die_themen_bei_verstaerkung(self) -> None:
        """Ein Thema, das aus dem Feld verschwindet, verschwindet aus der Suche.

        Bliebe es stehen, faende die Bibliothek eine Ausarbeitung ueber ein
        Thema, das sie nicht mehr behandelt.
        """
        from memory.repositories.autonomous_wissen_repository import (
            AutonomousWissenRepository,
            WissensEintrag,
        )

        pfad: str = f"{PFAD_PRAEFIX}d.md"
        bauplan = dict(
            dateipfad=pfad, user_id=MENSCH, character_id=CHARAKTER,
            beobachter="assistant", zusammenfassung="Zusammenfassung",
            typ="wissen", modus="recherche", status="echte_tiefe",
            salienz_anfang=0.5,
        )
        AutonomousWissenRepository.speichern(
            POSTGRES_URL, WissensEintrag(thema="Alpha, Beta", **bauplan))
        wissen_id: int = AutonomousWissenRepository.speichern(
            POSTGRES_URL, WissensEintrag(thema="Alpha, Gamma", **bauplan))

        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT thema FROM {TABELLE} WHERE wissen_id = %s ORDER BY thema",
                (wissen_id,),
            )
            self.assertEqual(
                ["Alpha", "Gamma"], [z[0] for z in cur.fetchall()],
                "Die Themen der Verstaerkung ersetzen die alten nicht",
            )

    def test_loeschen_des_eintrags_nimmt_die_themen_mit(self) -> None:
        """Der Katalog kennt die Regel; ob sie greift, zeigt nur ein Loeschen."""
        with self.conn.cursor() as cur:
            cur.execute(f"INSERT INTO {TABELLE} (wissen_id, thema) VALUES (%s, %s)",
                        (self.wissen_id, "Verhaltensbiologie"))
            cur.execute("DELETE FROM autonomous_wissen WHERE id = %s", (self.wissen_id,))
            cur.execute(f"SELECT count(*) FROM {TABELLE} WHERE wissen_id = %s",
                        (self.wissen_id,))
            self.assertEqual(
                0, cur.fetchone()[0],
                "Themenvektoren ueberleben ihre Ausarbeitung — sie zeigen dann "
                "auf nichts und tauchen trotzdem in jeder Suche auf",
            )


if __name__ == "__main__":
    unittest.main()
