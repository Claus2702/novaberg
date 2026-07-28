"""Tests fuer den Motivations-Verfall der Ziele als reine Funktion.

Ziel: Ein Ziel, das seit zwei Wochen niemand beruehrt hat, traegt die halbe
Motivation seines Ankers — unabhaengig davon, ob der Decay-Lauf in dieser Zeit
einmal, zehnmal oder gar nicht lief.

Hintergrund: Die Vorgaengerfassung las ihre Zeitbasis aus `erstellt_am` (dem
Gesamtalter des Ziels), multiplizierte die bereits verfallene `motivation`
erneut mit diesem Faktor und schrieb das Ergebnis zurueck. Der Verfall wuchs
dadurch quadratisch mit der Zahl der Laeufe. Belegt am Lauf vom 27.07.2026,
18:39:58 UTC: Ziel 3 von 0.65 auf 0.640, Ziel 4 von 0.70 auf 0.690. Bei
taeglichen Laeufen waeren die mittelfristigen Ziele nach sieben Tagen unter der
Deaktivierungsschwelle gewesen statt bei 0.44.

Die Erwartungswerte sind von Hand gerechnet und stehen als Literale. Sie werden
nicht aus ZIEL_MITTELFRISTIG_DECAY_TAGE abgeleitet — sonst rechnete der Test
die Formel mit derselben Zahl nach, aus der der Code sein Ergebnis bildet, und
beide Seiten des Vergleichs liefen auf dieselbe Eingabe zurueck.

    motivation(0.8, vor 14 Tagen) = 0.8 x exp(-ln2/14 x 14) = 0.8 x 0.5 = 0.4

Die DB-Tests bringen ihr Fixture selbst mit (eigene user_id), begrenzen jeden
Lauf ueber `user_id=TEST_USER` darauf und raeumen es in tearDown wieder ab. Ohne
diese Begrenzung fasst jeder Testlauf die produktiven Ziele mit an — die Suite
laeuft gegen die Produktiv-Datenbank. Genau das ist beim Bauen passiert und war
folgenlos, weil der Lauf idempotent ist; unter der alten Bauart haette jeder
Testlauf echte Motivation gekostet.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timedelta, timezone

import psycopg2

from config import POSTGRES_URL
from memory.ziele import motivation_berechnen, ziel_decay_lauf

ZIELE_LOGGER: str = "ki_server.memory.ziele"
TEST_USER:    str = "test_ziel_decay"


class TestMotivationBerechnen(unittest.TestCase):
    """Die reine Funktion, gegen handgerechnete Werte."""

    @staticmethod
    def _vor_tagen(tage: float) -> datetime:
        return datetime.now(timezone.utc) - timedelta(days=tage)

    def test_nach_einer_halbwertszeit_bleibt_die_haelfte(self) -> None:
        self.assertAlmostEqual(
            motivation_berechnen(0.8, self._vor_tagen(14)), 0.4, places=4,
        )

    def test_nach_zwei_halbwertszeiten_bleibt_ein_viertel(self) -> None:
        self.assertAlmostEqual(
            motivation_berechnen(0.8, self._vor_tagen(28)), 0.2, places=4,
        )

    def test_frisch_gesetzt_bleibt_der_anker(self) -> None:
        """Positiver Zwilling: Der Verfall ueber null Tage ist exakt 1.0.

        Ohne diesen Fall bestuende die Zusicherung oben auch dann, wenn die
        Funktion jeden Wert halbierte.
        """
        self.assertAlmostEqual(
            motivation_berechnen(0.8, self._vor_tagen(0)), 0.8, places=6,
        )

    def test_hundertmal_rechnen_aendert_nichts(self) -> None:
        """Regel (4) der Konvention: idempotent. Der Akkumulator war es nicht."""
        anker_am: datetime = self._vor_tagen(3)
        werte: set[float] = {
            motivation_berechnen(0.7, anker_am, jetzt=anker_am + timedelta(days=3))
            for _ in range(100)
        }
        self.assertEqual(len(werte), 1)

    def test_der_verfall_kann_nicht_heben(self) -> None:
        self.assertLessEqual(motivation_berechnen(0.5, self._vor_tagen(1)), 0.5)

    def test_anker_ueber_eins_meldet_fehler_und_klemmt(self) -> None:
        with self.assertLogs(ZIELE_LOGGER, level="ERROR") as protokoll:
            wert: float = motivation_berechnen(1.5, self._vor_tagen(0))
        self.assertAlmostEqual(wert, 1.0, places=6)
        self.assertIn("ausserhalb", "\n".join(protokoll.output))

    def test_ankerzeit_in_der_zukunft_erfindet_keine_motivation(self) -> None:
        zukunft: datetime = datetime.now(timezone.utc) + timedelta(days=5)
        self.assertAlmostEqual(motivation_berechnen(0.6, zukunft), 0.6, places=6)


class TestZielDecayLauf(unittest.TestCase):
    """Der Bulk-Lauf gegen echte Zeilen."""

    def setUp(self) -> None:
        self.conn = psycopg2.connect(POSTGRES_URL)
        self._aufraeumen()
        with self.conn.cursor() as cur:
            # Anker vor 14 Tagen: erwartet die Haelfte. Ein langfristiges Ziel
            # mit demselben Anker als Gegenstueck fuer die Allowlist.
            cur.execute(
                """
                INSERT INTO ziele (user_id, ziel_typ, zielsatz, motivation,
                                   motivation_basis, motivation_basis_am)
                VALUES (%s, 'mittelfristig', 'Testziel mittelfristig', 0.8, 0.8,
                        NOW() - INTERVAL '14 days'),
                       (%s, 'langfristig',   'Testziel langfristig',   0.8, 0.8,
                        NOW() - INTERVAL '14 days'),
                       (%s, 'kurzfristig',   'Testziel kurzfristig',   0.8, 0.8,
                        NOW() - INTERVAL '14 days')
                """,
                (TEST_USER, TEST_USER, TEST_USER),
            )
        self.conn.commit()

    def tearDown(self) -> None:
        self._aufraeumen()
        self.conn.close()

    def _aufraeumen(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM ziele WHERE user_id = %s", (TEST_USER,))
        self.conn.commit()

    def _motivationen(self) -> dict:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT ziel_typ, motivation, aktiv FROM ziele WHERE user_id = %s",
                (TEST_USER,),
            )
            return {typ: (wert, aktiv) for typ, wert, aktiv in cur.fetchall()}

    def test_lauf_materialisiert_die_haelfte(self) -> None:
        ziel_decay_lauf(POSTGRES_URL, user_id=TEST_USER)
        self.assertAlmostEqual(self._motivationen()["mittelfristig"][0], 0.4, places=4)

    def test_zehn_laeufe_ergeben_denselben_wert_wie_einer(self) -> None:
        """Die Zusicherung, an der die alte Fassung scheiterte.

        Unter dem Akkumulator sank der Wert mit jedem Lauf weiter; zehn Laeufe
        haetten das Ziel weit unter die Deaktivierungsschwelle gedrueckt.
        """
        ziel_decay_lauf(POSTGRES_URL, user_id=TEST_USER)
        nach_einem: float = self._motivationen()["mittelfristig"][0]

        for _ in range(9):
            ziel_decay_lauf(POSTGRES_URL, user_id=TEST_USER)
        nach_zehn: float = self._motivationen()["mittelfristig"][0]

        self.assertAlmostEqual(nach_einem, nach_zehn, places=6)

    def test_nur_der_angefragte_typ_wird_angefasst(self) -> None:
        """Allowlist statt Denylist.

        Die Vorgaengerfassung uebersprang nur `langfristig` und decayte damit
        auch `kurzfristig` mit der mittelfristigen Halbwertszeit.
        """
        ziel_decay_lauf(POSTGRES_URL, user_id=TEST_USER)
        werte: dict = self._motivationen()
        self.assertAlmostEqual(werte["langfristig"][0], 0.8, places=6)
        self.assertAlmostEqual(werte["kurzfristig"][0], 0.8, places=6)

    def test_unter_der_schwelle_wird_deaktiviert(self) -> None:
        ziel_decay_lauf(POSTGRES_URL, deaktivierungs_schwelle=0.5, user_id=TEST_USER)
        typ, aktiv = self._motivationen()["mittelfristig"]
        self.assertLess(typ, 0.5)
        self.assertFalse(aktiv)

    def test_ueber_der_schwelle_bleibt_aktiv(self) -> None:
        """Positiver Zwilling zur Deaktivierung."""
        ziel_decay_lauf(POSTGRES_URL, deaktivierungs_schwelle=0.1, user_id=TEST_USER)
        self.assertTrue(self._motivationen()["mittelfristig"][1])

    def test_ziel_ohne_anker_wird_gemeldet_und_nicht_angefasst(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE ziele SET motivation_basis = NULL, motivation_basis_am = NULL
                WHERE user_id = %s AND ziel_typ = 'mittelfristig'
                """,
                (TEST_USER,),
            )
        self.conn.commit()

        with self.assertLogs(ZIELE_LOGGER, level="ERROR") as protokoll:
            ergebnis: dict = ziel_decay_lauf(POSTGRES_URL, user_id=TEST_USER)

        self.assertGreaterEqual(ergebnis["ohne_anker"], 1)
        self.assertIn("motivation_basis", "\n".join(protokoll.output))
        self.assertAlmostEqual(self._motivationen()["mittelfristig"][0], 0.8, places=6)

    def test_unbrauchbare_halbwertszeit_schreibt_nichts(self) -> None:
        with self.assertLogs(ZIELE_LOGGER, level="ERROR"):
            ergebnis: dict = ziel_decay_lauf(POSTGRES_URL, halbwertszeit_tage=0, user_id=TEST_USER)
        self.assertIsNotNone(ergebnis["error"])
        self.assertAlmostEqual(self._motivationen()["mittelfristig"][0], 0.8, places=6)


if __name__ == "__main__":
    unittest.main()
