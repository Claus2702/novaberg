"""Zeugen ueber die Nachfuehrung: traegt die Beruehrung endlich in den Wert?

Ziel: Ein Faden, der aufgefrischt wurde, steht danach hoeher als vorher — und
einer, den seit Wochen niemand angesprochen hat, steht tiefer.

**Der Anlass ist ein Defekt der Klasse, die eine gruene Suite nicht sieht.**
`ausschlag_aktuell_falten` war am 01.09.2026 gebaut und gegen 18 Stuetzstellen
des Konzepts bezeugt — und hatte **keinen Aufrufer im Produktivcode**
(`FALTUNG-OHNE-AUFRUFER`). Vier Beruehrungen entstanden im Betrieb, und der
Wert, den sie haetten bewegen sollen, stand unveraendert auf
`ausschlag_absolut`. Die Zeugen der Funktion waren alle gruen.

**Diese Datei prueft deshalb die Verwendung, nicht die Rechnung.** Die Rechnung
hat ihre eigenen Zeugen in `test_praegung_faltung.py`; hier geht jeder Weg
durch `beruehrung_aus_reaktivierung` oder schreibt in die Tabelle und liest sie
zurueck (`20_TESTS/verdrahtung.md`).

Sie fahren gegen die echte Datenbank, weil die Naehe eine pgvector-Rechnung ist
und der Wert eine Spalte.

Die Zusicherungen:

  1. **Eine Beruehrung bewegt die Spalte.** Ohne diesen Zeugen bliebe die
     Faltung ohne Aufrufer, und die Suite saehe nichts davon.
  2. **Sie hebt, sie setzt nicht zurueck.** Der Wert steigt und bleibt unter
     `ausschlag_absolut` — Wiedererinnern macht nicht intensiver.
  3. **Ohne Treffer bleibt der Wert stehen.** Sonst waere Zusicherung 1 auch
     von einer Nachfuehrung erfuellt, die bei jedem Turn ueber alles laeuft.
  4. **Beide Schreibwege falten.** `beruehrung_anlegen` ist der zweite Weg in
     dieselbe Tabelle. Ohne diesen Zeugen haette der eine Weg die Nachfuehrung
     und der andere nicht — derselbe Defekt an einer anderen Tuer.
  5. **Zweimal rechnen aendert nichts** (Wertekonvention Regel 4).
  6. **Ohne Beruehrung ist es reiner Verfall** — und der Boden haelt.
  7. **Eine unbekannte Kennung ist kein Fehler**, sondern eine geloeschte
     Praegung; sie wird gezaehlt, nicht geworfen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timedelta, timezone

import psycopg2

from config import POSTGRES_URL, PRAEGUNG_BODEN, PRAEGUNG_HALBSTRECKE
from memory.praegung import (
    _verfall,
    ausschlag_aktuell_nachfuehren,
    beruehrung_anlegen,
    beruehrung_aus_reaktivierung,
)

#: Dieselbe Lage wie in `test_praegung_auffrischung.py`: der zweite Vektor
#: steht dicht am ersten (Cosinus rund 0,995), der dritte orthogonal.
NAH_A: list[float] = [1.0] + [0.0] * 767
NAH_B: list[float] = [1.0, 0.1] + [0.0] * 766
FERN:  list[float] = [0.0, 1.0] + [0.0] * 766

ABSOLUT: float = 0.9
#: Der Faden ist alt genug, dass der Verfall messbar ist. Bei einem Faden von
#: heute liegt der Unterschied in der dritten Nachkommastelle — ein Zeuge
#: darauf wuerde eine abgeschaltete Nachfuehrung nicht von einer laufenden
#: unterscheiden.
ALTER_TAGE: int = 30


def _vektor(werte: list[float]) -> str:
    return "[" + ",".join(str(x) for x in werte) + "]"


class NachfuehrungTest(unittest.TestCase):
    """Der Weg von der Beruehrung in die Spalte `ausschlag_aktuell`."""

    USER: str = "test-nachfuehrung-user"
    CHAR: str = "test-nachfuehrung-char"
    SCHWELLE: float = 0.62

    def setUp(self) -> None:
        self.entstanden: datetime = (
            datetime.now(timezone.utc) - timedelta(days=ALTER_TAGE)
        )
        self.knoten: dict[str, int] = {}
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO praegung_faden "
                "(user_id, character_id, emotion, ausschlag_eingang, "
                " ausschlag_absolut, ausschlag_aktuell, embedding, entstanden_am) "
                "VALUES (%s, %s, 'traurigkeit', 0.8, %s, %s, %s, %s) RETURNING id",
                (self.USER, self.CHAR, ABSOLUT, ABSOLUT,
                 _vektor(NAH_A), self.entstanden),
            )
            self.faden_id: int = int(cur.fetchone()[0])

            for name, vektor in (("nah", NAH_B), ("fern", FERN)):
                cur.execute(
                    "INSERT INTO lzg_knoten "
                    "(user_id, character_id, inhalt, dimension, emotion, "
                    " embedding, beobachter, kzg_quell_key, gewicht_roh, "
                    " gewicht_absolut, gewicht_decay, kzg_erstellt_am) "
                    "VALUES (%s, %s, %s, 'kognition', 'neugierig', %s, "
                    " 'assistant', %s, 1.0, 1.0, 1.0, NOW()) RETURNING id",
                    (self.USER, self.CHAR, f"Testknoten {name}",
                     _vektor(vektor), f"test-nachfuehrung-{name}"),
                )
                self.knoten[name] = int(cur.fetchone()[0])

    def tearDown(self) -> None:
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM praegung_faden WHERE user_id = %s", (self.USER,),
            )
            # Der Strang, den `faden_anlegen` seit dem 01.09.2026 mit gruendet.
            cur.execute(
                "DELETE FROM praegung_strang WHERE user_id = %s", (self.USER,),
            )
            cur.execute(
                "DELETE FROM lzg_knoten WHERE user_id = %s", (self.USER,),
            )

    def _aktuell(self) -> float:
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT ausschlag_aktuell FROM praegung_faden WHERE id = %s",
                (self.faden_id,),
            )
            return float(cur.fetchone()[0])

    # ── 1 + 2: die Verdrahtung ──────────────────

    def test_eine_beruehrung_bewegt_die_spalte(self) -> None:
        vorher: float = self._aktuell()
        beruehrung_aus_reaktivierung(
            POSTGRES_URL, self.USER, self.CHAR,
            [(f"lzg:{self.knoten['nah']}", NAH_B)], self.SCHWELLE,
        )
        nachher: float = self._aktuell()
        self.assertNotAlmostEqual(
            nachher, vorher, places=4,
            msg="Die Beruehrung ist geschrieben und der Wert steht unveraendert — "
                "die Faltung hat keinen Aufrufer (FALTUNG-OHNE-AUFRUFER)",
        )

    def test_die_beruehrung_hebt_und_setzt_nicht_zurueck(self) -> None:
        beruehrung_aus_reaktivierung(
            POSTGRES_URL, self.USER, self.CHAR,
            [(f"lzg:{self.knoten['nah']}", NAH_B)], self.SCHWELLE,
        )
        nachher: float = self._aktuell()
        reiner_verfall: float = ABSOLUT * _verfall(
            ALTER_TAGE, PRAEGUNG_BODEN, PRAEGUNG_HALBSTRECKE,
        )
        self.assertGreater(
            nachher, reiner_verfall,
            "Die Beruehrung hat die Luecke nicht aufgefuellt — ein Faden, der "
            "gerade angesprochen wurde, verblasst weiter wie einer, den "
            "niemand erwaehnt hat",
        )
        self.assertLess(
            nachher, ABSOLUT,
            "Der Wert hat `ausschlag_absolut` erreicht — die Beruehrung setzt "
            "zurueck statt aufzufuellen, und das Beruehrungsintervall wird "
            "bedeutungslos (Konzept 7.4)",
        )

    def test_ohne_treffer_bleibt_der_wert_stehen(self) -> None:
        vorher: float = self._aktuell()
        beruehrung_aus_reaktivierung(
            POSTGRES_URL, self.USER, self.CHAR,
            [(f"lzg:{self.knoten['fern']}", FERN)], self.SCHWELLE,
        )
        self.assertAlmostEqual(
            self._aktuell(), vorher, places=6,
            msg="Eine Reaktivierung ohne Treffer hat den Wert bewegt — dann "
                "laeuft die Nachfuehrung auf jedem Turn ueber alles, statt auf "
                "das Ereignis",
        )

    def test_der_zweite_schreibweg_faltet_auch(self) -> None:
        vorher: float = self._aktuell()
        self.assertTrue(
            beruehrung_anlegen(POSTGRES_URL, self.faden_id, "lzg:probe"),
        )
        self.assertNotAlmostEqual(
            self._aktuell(), vorher, places=4,
            msg="`beruehrung_anlegen` schreibt die Zeile und laesst den Wert "
                "stehen — derselbe Defekt an der anderen Tuer",
        )

    # ── 5 bis 7: die Rechnung an ihrem Ort ──────

    def test_zweimal_rechnen_aendert_nichts(self) -> None:
        bezug: datetime = datetime.now(timezone.utc)
        ausschlag_aktuell_nachfuehren(POSTGRES_URL, [self.faden_id], bezug)
        erste: float = self._aktuell()
        ausschlag_aktuell_nachfuehren(POSTGRES_URL, [self.faden_id], bezug)
        self.assertAlmostEqual(
            self._aktuell(), erste, places=9,
            msg="Der zweite Lauf liefert einen anderen Wert — dann schreibt die "
                "Nachfuehrung fort statt von Grund auf zu rechnen "
                "(Wertekonvention Regel 4)",
        )

    def test_ohne_beruehrung_ist_es_reiner_verfall(self) -> None:
        bezug: datetime = self.entstanden + timedelta(days=ALTER_TAGE)
        ausschlag_aktuell_nachfuehren(POSTGRES_URL, [self.faden_id], bezug)
        erwartet: float = ABSOLUT * _verfall(
            ALTER_TAGE, PRAEGUNG_BODEN, PRAEGUNG_HALBSTRECKE,
        )
        self.assertAlmostEqual(
            self._aktuell(), erwartet, places=6,
            msg="Ein Faden ohne Beruehrung folgt nicht der Verfallskurve",
        )

    def test_der_boden_haelt_auch_nach_jahren(self) -> None:
        bezug: datetime = self.entstanden + timedelta(days=20_000)
        ausschlag_aktuell_nachfuehren(POSTGRES_URL, [self.faden_id], bezug)
        self.assertGreater(
            self._aktuell(), ABSOLUT * PRAEGUNG_BODEN * 0.999,
            "Der Boden ist unterschritten — ein Faden wird leiser, nie "
            "deaktiviert (Konzept 7.4)",
        )

    def test_unbekannte_kennung_ist_kein_fehler(self) -> None:
        self.assertEqual(
            ausschlag_aktuell_nachfuehren(POSTGRES_URL, [-1]), 0,
            "Eine geloeschte Praegung wird als Fehler behandelt statt gezaehlt",
        )

    def test_leere_liste_faehrt_nicht_zur_datenbank(self) -> None:
        self.assertEqual(ausschlag_aktuell_nachfuehren(POSTGRES_URL, []), 0)


if __name__ == "__main__":
    unittest.main()
