"""Zeugen ueber die Auffrischung: welche Reaktivierung welchen Faden trifft.

Ziel: Ein Faden, dessen Thema wieder aufkommt, verblasst nicht weiter — und
einer, der nur zufaellig aehnlich aussieht, wird nicht unsterblich.

`beruehrung_anlegen()` stand seit dem 31.08.2026 **ohne Aufrufer** im Bestand;
`ausschlag_aktuell` blieb dadurch fuer immer gleich `ausschlag_absolut`. Diese
Zeugen decken den Weg von der Reaktivierung zum Faden.

**Sie fahren gegen die echte Datenbank**, weil die Naehe eine pgvector-Rechnung
ist: Eine Nachbildung im Test wuerde die Cosinus-Distanz selbst rechnen und
damit genau die Stelle ueberspringen, die gemeint ist
(`novaberg-lesson_l_zeuge-prueft-die-funktion-nicht-ihre-verwendung.md`).

Die Zusicherungen:

  1. **Ein naher Knoten frischt auf.** Ohne diesen Zeugen waere die Funktion mit
     einer auf, die nie etwas trifft.
  2. **Ein ferner Knoten frischt nicht auf.** Sonst waere Zusicherung 1 auch von
     einer Funktion erfuellt, die jeden Faden bei jeder Reaktivierung anfasst —
     und ein Faden, der alle paar Turns aufgefrischt wird, wird unsterblich
     (Konzept §7.4).
  3. **Je Knoten hoechstens ein Faden.** Eine Reaktivierung ist ein Ereignis,
     kein Aehnlichkeitsmass.
  4. **Ohne vollstaendiges Paar wird abgelehnt und gemeldet.** Eine Praegung
     gehoert einer Beziehung.
  5. **Die Quelle nennt den Knoten.** Sonst waere im Nachhinein nicht zu sagen,
     was einen Faden aufgefrischt hat.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

import psycopg2

from config import POSTGRES_URL
from memory.praegung import beruehrung_aus_reaktivierung

#: Zwei Vektoren mit bekannter Lage zueinander. Der erste steht auf einer Achse,
#: der zweite dicht daneben (Cosinus rund 0,995), der dritte orthogonal (0,0).
#: Feste Zahlen statt echter Embeddings: Die Zusicherung gilt der Schwelle und
#: der Auswahl, nicht der Qualitaet eines Sprachmodells.
NAH_A: list[float] = [1.0] + [0.0] * 767
NAH_B: list[float] = [1.0, 0.1] + [0.0] * 766
FERN:  list[float] = [0.0, 1.0] + [0.0] * 766


def _vektor(werte: list[float]) -> str:
    return "[" + ",".join(str(x) for x in werte) + "]"


class AuffrischungTest(unittest.TestCase):
    """Die Zuordnung Reaktivierung → Faden ueber Embedding-Naehe."""

    USER: str = "test-auffrischung-user"
    CHAR: str = "test-auffrischung-char"
    SCHWELLE: float = 0.62

    def setUp(self) -> None:
        self.knoten: dict[str, int] = {}
        self.faden_id: int = 0
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO praegung_faden "
                "(user_id, character_id, emotion, ausschlag_eingang, "
                " ausschlag_absolut, ausschlag_aktuell, embedding) "
                "VALUES (%s, %s, 'traurigkeit', 0.8, 0.9, 0.9, %s) RETURNING id",
                (self.USER, self.CHAR, _vektor(NAH_A)),
            )
            self.faden_id = int(cur.fetchone()[0])

            for name, vektor in (("nah", NAH_B), ("fern", FERN)):
                cur.execute(
                    "INSERT INTO lzg_knoten "
                    "(user_id, character_id, inhalt, dimension, emotion, "
                    " embedding, beobachter, kzg_quell_key, gewicht_roh, "
                    " gewicht_absolut, gewicht_decay, kzg_erstellt_am) "
                    "VALUES (%s, %s, %s, 'kognition', 'neugierig', %s, "
                    " 'assistant', %s, 1.0, 1.0, 1.0, NOW()) RETURNING id",
                    (self.USER, self.CHAR, f"Testknoten {name}",
                     _vektor(vektor), f"test-auffrischung-{name}"),
                )
                self.knoten[name] = int(cur.fetchone()[0])

    def tearDown(self) -> None:
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM praegung_faden WHERE user_id = %s", (self.USER,),
            )
            cur.execute(
                "DELETE FROM lzg_knoten WHERE user_id = %s", (self.USER,),
            )

    def _beruehrungen(self) -> list[tuple[int, str]]:
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT faden_id, quelle FROM praegung_beruehrung "
                "WHERE faden_id = %s ORDER BY id", (self.faden_id,),
            )
            return list(cur.fetchall())

    def test_ein_naher_knoten_frischt_den_faden_auf(self) -> None:
        treffer = beruehrung_aus_reaktivierung(
            POSTGRES_URL, self.USER, self.CHAR,
            [self.knoten["nah"]], self.SCHWELLE,
        )
        self.assertEqual(
            len(treffer), 1,
            "Eine Reaktivierung desselben Themas hat den Faden nicht getroffen — "
            "er verblasst weiter, obwohl er gerade angesprochen wurde",
        )
        self.assertEqual(len(self._beruehrungen()), 1, "Keine Zeile geschrieben")

    def test_ein_ferner_knoten_frischt_nicht_auf(self) -> None:
        treffer = beruehrung_aus_reaktivierung(
            POSTGRES_URL, self.USER, self.CHAR,
            [self.knoten["fern"]], self.SCHWELLE,
        )
        self.assertEqual(
            treffer, [],
            "Ein thematisch fremder Knoten hat den Faden aufgefrischt — bei "
            "genug Reaktivierungen wird er dadurch unsterblich",
        )
        self.assertEqual(self._beruehrungen(), [], "Zeile trotz Ablehnung")

    def test_je_knoten_hoechstens_ein_faden(self) -> None:
        """Ein zweiter, ebenso naher Faden bekommt nichts ab."""
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO praegung_faden "
                "(user_id, character_id, emotion, ausschlag_eingang, "
                " ausschlag_absolut, ausschlag_aktuell, embedding) "
                "VALUES (%s, %s, 'freude', 0.8, 0.9, 0.9, %s)",
                (self.USER, self.CHAR, _vektor(NAH_A)),
            )
        treffer = beruehrung_aus_reaktivierung(
            POSTGRES_URL, self.USER, self.CHAR,
            [self.knoten["nah"]], self.SCHWELLE,
        )
        self.assertEqual(
            len(treffer), 1,
            "Eine Reaktivierung hat zwei Faeden aufgefrischt — sie zaehlt als "
            "ein Ereignis, nicht als Aehnlichkeitsmass",
        )

    def test_ohne_vollstaendiges_paar_wird_abgelehnt(self) -> None:
        self.assertEqual(
            beruehrung_aus_reaktivierung(
                POSTGRES_URL, self.USER, "", [self.knoten["nah"]], self.SCHWELLE,
            ),
            [],
            "Ohne Gegenueber angelegt — eine Praegung gehoert einer Beziehung",
        )
        self.assertEqual(self._beruehrungen(), [])

    def test_die_quelle_nennt_den_knoten(self) -> None:
        beruehrung_aus_reaktivierung(
            POSTGRES_URL, self.USER, self.CHAR,
            [self.knoten["nah"]], self.SCHWELLE,
        )
        zeilen = self._beruehrungen()
        self.assertEqual(len(zeilen), 1)
        self.assertEqual(
            zeilen[0][1], f"lzg:{self.knoten['nah']}",
            "Die Quelle nennt den ausloesenden Knoten nicht — im Nachhinein "
            "waere nicht zu sagen, was den Faden aufgefrischt hat",
        )

    def test_ohne_faeden_passiert_nichts_und_es_bricht_nicht(self) -> None:
        """Der Regelfall zu Beginn: Es gibt noch keine Faeden."""
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM praegung_faden WHERE user_id = %s", (self.USER,),
            )
        self.assertEqual(
            beruehrung_aus_reaktivierung(
                POSTGRES_URL, self.USER, self.CHAR,
                [self.knoten["nah"]], self.SCHWELLE,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
