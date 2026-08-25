"""Tests fuer die Paar-Bindung der Ziele.

Ziel: Ein Ziel, das aus der Beziehung zu einem Menschen destilliert wurde, ist
nur in Turns dieser Beziehung sichtbar und wird nur von ihrer eigenen
Destillation deaktiviert.

Hintergrund: `ziele` trug bis Chat 125 ausschliesslich `user_id`, und alle
Zeilen standen unter `nova`. Der Enricher las sie in jeden Turn, und die
Destillation deaktiviert vor dem Schreiben ALLE aktiven langfristigen Ziele
(agents/charakter/agent.py). Bei einem einzigen Paar ist das die vorgesehene
Fortschreibung; bei zweien ist es ein Wettlauf, den der zuletzt destillierte
gewinnt — Novas Ziele im produktiven Paar kaemen dann aus dem
Kurzzeitgedaechtnis einer Testperson.

Die Zeugen:

  * Die erwarteten Paare sind Literale, von Hand aus
    `novaberg-convention-paar-schema.md` §2 abgeleitet — nicht aus dem Code.
  * Die Fixture-Zeilen entstehen per direktem SQL, nicht ueber
    `ziel_speichern`. Sonst liefe die Erwartung durch dieselbe Funktion wie das
    Ergebnis, und der Test verglichen zwei Ableitungen derselben Eingabe.
  * Beide Zielsaetze tragen unverwechselbare Marker. Ein Lesepfad, der das
    Gegenueber ignoriert, liefert den fremden Satz mit und wird rot.

Die DB-Tests bringen ihr Fixture selbst mit (eigene Kennungen), lesen
ausschliesslich darin und raeumen es in tearDown ab: Die Suite laeuft gegen die
Produktiv-Datenbank.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import unittest
from pathlib import Path
from unittest.mock import patch

import psycopg2

import graph.nodes.enricher as enricher_mod
from config import ASSISTANT_USER_ID, DEFAULT_USER_ID, POSTGRES_URL
from memory.ziele import ziel_paar_bestimmen, ziel_speichern, ziele_aktive_laden

ZIELE_LOGGER: str = "ki_server.memory.ziele"

# Zwei Menschen, beide Fixture. Die Kennungen sind bewusst keine echten:
# Ein Test, der 'meister' benutzt, laese die produktiven Ziele mit.
MENSCH_A: str = "test_ziele_paar_a"
MENSCH_B: str = "test_ziele_paar_b"

ZIELSATZ_A: str = "Testziel Paar A — Marker 7f3c1e"
ZIELSATZ_B: str = "Testziel Paar B — Marker 91ba44"


class ZielPaarBestimmenTest(unittest.TestCase):
    """Die Ableitung des Ziel-Paares aus dem Paar eines Turns."""

    def test_human_pfad_dreht_das_paar_um(self) -> None:
        """(mensch, nova) ist das Turn-Paar; das Ziel-Paar ist (nova, mensch)."""
        self.assertEqual(
            ziel_paar_bestimmen(MENSCH_A, ASSISTANT_USER_ID),
            (ASSISTANT_USER_ID, MENSCH_A),
        )

    def test_nova_pfad_ergibt_dasselbe_paar(self) -> None:
        """Der Zeuge fuer die ganze Funktion.

        Novas eigener Pfad fuehrt sein Paar andersherum. Beide Pfade muessen
        auf dieselbe Zeile zeigen — sonst liest der eine die Ziele und der
        andere nichts.
        """
        self.assertEqual(
            ziel_paar_bestimmen(ASSISTANT_USER_ID, MENSCH_A),
            ziel_paar_bestimmen(MENSCH_A, ASSISTANT_USER_ID),
        )

    def test_nur_das_gegenueber_genannt(self) -> None:
        """Eine leere Subjektseite verwirft den genannten Menschen nicht."""
        self.assertEqual(
            ziel_paar_bestimmen("", MENSCH_B), (ASSISTANT_USER_ID, MENSCH_B),
        )

    def test_beide_kennungen_leer_meldet_und_faellt_zurueck(self) -> None:
        """Ein Turn ohne jede Kennung ist ein Defekt, kein Sonderfall."""
        with self.assertLogs(ZIELE_LOGGER, level="ERROR") as protokoll:
            paar: tuple = ziel_paar_bestimmen("", "")
        self.assertEqual(paar, (ASSISTANT_USER_ID, DEFAULT_USER_ID))
        self.assertIn("beide Kennungen leer", "\n".join(protokoll.output))

    def test_paar_ohne_menschen_meldet_und_faellt_zurueck(self) -> None:
        """(nova, nova) ist ein Migrationsrest, kein Selbstgespraech."""
        with self.assertLogs(ZIELE_LOGGER, level="ERROR") as protokoll:
            paar: tuple = ziel_paar_bestimmen(ASSISTANT_USER_ID, ASSISTANT_USER_ID)
        self.assertEqual(paar, (ASSISTANT_USER_ID, DEFAULT_USER_ID))
        self.assertIn("kein Gegenueber", "\n".join(protokoll.output))

    def test_gueltiges_paar_schweigt(self) -> None:
        """Positiver Zwilling: Der Regelfall meldet nichts.

        Ohne ihn bestuenden die Fehlerfaelle auch dann, wenn die Funktion bei
        jedem Aufruf protokollierte.
        """
        with self.assertNoLogs(ZIELE_LOGGER, level="ERROR"):
            ziel_paar_bestimmen(MENSCH_A, ASSISTANT_USER_ID)


class ZieleLesenPaarTest(unittest.TestCase):
    """Der Lesepfad trennt die Beziehungen."""

    def setUp(self) -> None:
        """Legt das Fixture beider Paare an."""
        self.conn = psycopg2.connect(POSTGRES_URL)
        self._aufraeumen()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ziele (user_id, character_id, ziel_typ, zielsatz,
                                   motivation, motivation_basis, motivation_basis_am)
                VALUES (%s, %s, 'langfristig', %s, 0.8, 0.8, NOW()),
                       (%s, %s, 'langfristig', %s, 0.8, 0.8, NOW())
                """,
                (ASSISTANT_USER_ID, MENSCH_A, ZIELSATZ_A,
                 ASSISTANT_USER_ID, MENSCH_B, ZIELSATZ_B),
            )
        self.conn.commit()

    def tearDown(self) -> None:
        """Raeumt das Fixture ab — die Suite laeuft gegen den Produktivbestand."""
        self._aufraeumen()
        self.conn.close()

    def _aufraeumen(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM ziele WHERE character_id IN (%s, %s)",
                (MENSCH_A, MENSCH_B),
            )
        self.conn.commit()

    def test_paar_a_sieht_nur_sein_ziel(self) -> None:
        """Der Lesepfad liefert das eigene Ziel und nicht das der anderen Beziehung."""
        saetze: list[str] = [
            z["zielsatz"] for z in ziele_aktive_laden(
                POSTGRES_URL, ASSISTANT_USER_ID, MENSCH_A,
            )
        ]
        self.assertIn(ZIELSATZ_A, saetze)
        self.assertNotIn(ZIELSATZ_B, saetze)

    def test_paar_b_sieht_nur_sein_ziel(self) -> None:
        """Die Gegenrichtung. Ein Filter, der immer auf A steht, faellt hier."""
        saetze: list[str] = [
            z["zielsatz"] for z in ziele_aktive_laden(
                POSTGRES_URL, ASSISTANT_USER_ID, MENSCH_B,
            )
        ]
        self.assertIn(ZIELSATZ_B, saetze)
        self.assertNotIn(ZIELSATZ_A, saetze)

    def test_unvollstaendiges_paar_liest_nichts_und_meldet(self) -> None:
        """Ohne Gegenueber waere jede Zeile ein Treffer — also kein Zugriff."""
        with self.assertLogs(ZIELE_LOGGER, level="ERROR") as protokoll:
            ziele: list[dict] = ziele_aktive_laden(POSTGRES_URL, ASSISTANT_USER_ID, "")
        self.assertEqual(ziele, [])
        self.assertIn("unvollstaendiges Paar", "\n".join(protokoll.output))


class ZielSchreibenPaarTest(unittest.TestCase):
    """Der Schreibpfad legt das Gegenueber ab — oder schreibt gar nicht."""

    def setUp(self) -> None:
        """Legt das Fixture beider Paare an."""
        self.conn = psycopg2.connect(POSTGRES_URL)
        self._aufraeumen()

    def tearDown(self) -> None:
        """Raeumt das Fixture ab — die Suite laeuft gegen den Produktivbestand."""
        self._aufraeumen()
        self.conn.close()

    def _aufraeumen(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM ziele WHERE zielsatz IN (%s, %s)",
                        (ZIELSATZ_A, ZIELSATZ_B))
        self.conn.commit()

    def _zeilen(self, zielsatz: str) -> list[tuple]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, character_id FROM ziele WHERE zielsatz = %s",
                (zielsatz,),
            )
            return cur.fetchall()

    def test_gespeichertes_ziel_traegt_das_gegenueber(self) -> None:
        """Der Regelfall: Die geschriebene Zeile nennt beide Seiten des Paares."""
        ziel_id = ziel_speichern(
            postgres_url=POSTGRES_URL,
            user_id=ASSISTANT_USER_ID,
            character_id=MENSCH_A,
            ziel_typ="langfristig",
            zielsatz=ZIELSATZ_A,
            motivation=0.8,
        )
        self.assertIsNotNone(ziel_id)
        self.assertEqual(self._zeilen(ZIELSATZ_A), [(ASSISTANT_USER_ID, MENSCH_A)])

    def test_ohne_gegenueber_wird_nichts_geschrieben(self) -> None:
        """Negativ-Zusicherung. Der positive Zwilling steht darueber."""
        with self.assertLogs(ZIELE_LOGGER, level="ERROR") as protokoll:
            ziel_id = ziel_speichern(
                postgres_url=POSTGRES_URL,
                user_id=ASSISTANT_USER_ID,
                character_id="",
                ziel_typ="langfristig",
                zielsatz=ZIELSATZ_B,
                motivation=0.8,
            )
        self.assertIsNone(ziel_id)
        self.assertEqual(self._zeilen(ZIELSATZ_B), [])
        self.assertIn("unvollstaendiges Paar", "\n".join(protokoll.output))


class EnricherReichtDasPaarDurchTest(unittest.TestCase):
    """Die Verdrahtung, nicht der Baustein.

    Der Defekt sass nie in der Ladefunktion — er sass darin, dass ihr niemand
    ein Gegenueber gab. Geprueft wird deshalb das Argument, das der Enricher
    weiterreicht, nicht das Ergebnis der Ladefunktion.
    """

    def _gelesenes_paar(self, turn_user_id: str, turn_character_id: str) -> tuple:
        with patch.object(enricher_mod, "ziele_aktive_laden", return_value=[]) as lade:
            enricher_mod._compute_ziele_und_gravitation(
                [0.0] * 768, POSTGRES_URL, turn_user_id, turn_character_id,
            )
        self.assertEqual(lade.call_count, 1)
        # (postgres_url, user_id, character_id) — die beiden hinteren sind das Paar.
        return lade.call_args.args[1], lade.call_args.args[2]

    def test_human_turn_liest_das_paar_des_turns(self) -> None:
        """Der Human-Pfad reicht sein Turn-Paar umgedreht weiter."""
        self.assertEqual(
            self._gelesenes_paar(MENSCH_A, ASSISTANT_USER_ID),
            (ASSISTANT_USER_ID, MENSCH_A),
        )

    def test_nova_turn_liest_dasselbe_paar(self) -> None:
        """Novas Pfad landet auf derselben Zeile wie der Human-Pfad."""
        self.assertEqual(
            self._gelesenes_paar(ASSISTANT_USER_ID, MENSCH_A),
            (ASSISTANT_USER_ID, MENSCH_A),
        )

    def test_ein_zweiter_mensch_bekommt_seine_eigenen_ziele(self) -> None:
        """Der Fall, um den es geht: zwei Paare, zwei Lesevorgaenge."""
        self.assertEqual(
            self._gelesenes_paar(MENSCH_B, ASSISTANT_USER_ID),
            (ASSISTANT_USER_ID, MENSCH_B),
        )


class KeinSchreiberOhneGegenueberTest(unittest.TestCase):
    """Struktur als Zeuge: Jeder Aufruf von `ziel_speichern` nennt das Paar.

    Die Datenbank faengt einen vergessenen Schreiber erst zur Laufzeit ab (die
    Spalte hat keinen Default mehr), und zwar in einem Hintergrundagenten, wo
    die Ausnahme im Log endet. Diese Pruefung findet ihn ohne Lauf.

    Der Bereich ist `server/` ohne `tests/`: Ein Test darf einen unvollstaendigen
    Aufruf absichtlich bauen — genau das tut `ZielSchreibenPaarTest`.
    """

    def test_jeder_aufruf_nennt_character_id(self) -> None:
        """Kein Schreibpfad in `server/` laesst das Gegenueber weg."""
        wurzel: Path = Path(__file__).resolve().parent.parent
        ohne_paar: list[str] = []
        gepruefte_aufrufe: int = 0

        for pfad in sorted(wurzel.rglob("*.py")):
            if "tests" in pfad.relative_to(wurzel).parts:
                continue

            baum = ast.parse(pfad.read_text(encoding="utf-8"), filename=str(pfad))
            for knoten in ast.walk(baum):
                if not isinstance(knoten, ast.Call):
                    continue
                if getattr(knoten.func, "id", "") != "ziel_speichern":
                    continue

                gepruefte_aufrufe += 1
                schluessel: set[str] = {
                    kw.arg for kw in knoten.keywords if kw.arg
                }
                # Drei Stellungsargumente reichen bis einschliesslich
                # character_id (postgres_url, user_id, character_id).
                if "character_id" not in schluessel and len(knoten.args) < 3:
                    ohne_paar.append(
                        f"{pfad.relative_to(wurzel)}:{knoten.lineno}"
                    )

        self.assertEqual(ohne_paar, [], f"Schreiber ohne Gegenueber: {ohne_paar}")
        # Findet der Durchlauf gar keinen Aufruf, prueft er nichts und waere
        # trotzdem gruen — derselbe Fall wie ein leerer Grep.
        self.assertGreaterEqual(gepruefte_aufrufe, 2)


if __name__ == "__main__":
    unittest.main()
