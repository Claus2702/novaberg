"""Tests: Kein lebender Pfad liest mehr aus der abgeloesten LZG-Tabelle.

Ziel: Die Vorwissens-Pruefung des RechercheAgenten findet, was in `lzg_knoten`
steht, und die emotionale Gravitation wendet den Zeitverfall genau einmal an.

Hintergrund, zwei Befunde aus Chat 125:

  * `_lzg_vorwissen_laden` las aus `langzeitgedaechtnis` — der Tabelle, die der
    Synapsen-Umbau abgeloest hat und die seit dem Reset vom 27.07.2026 null
    Zeilen traegt. Die Pruefung meldete ausnahmslos „kenne ich nicht", ohne
    dass etwas ausfiel: Ein Lesepfad auf eine leere Tabelle liefert eine
    gueltige leere Liste.
  * `ei/gravitation.py` las `gewicht_decay` — den bereits abgewerteten Wert —
    und schickte ihn durch dieselbe Ebbinghaus-Formel mit derselben Rate.
    Jede Erinnerung wurde gewichtet, als waere sie doppelt so alt.

Die Zeugen:

  * Fuer den Lesepfad: eine Zeile, per SQL angelegt, mit einem Inhalt, der in
    keiner anderen Zeile des Bestands steht. Ein Treffer kann dann nur diese
    Zeile sein.
  * Fuer die Gravitation: eine **Handrechnung**. Der erwartete Wert stammt
    nicht aus der geprueften Funktion, sondern aus der Formel des Konzepts,
    mit gerundeten Eingaben, die sich im Kopf nachrechnen lassen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import inspect
import math
import textwrap
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import psycopg2

import agents.recherche.lagebeurteilung as lage_mod
from config import POSTGRES_URL

# Eigener Skopus: Die Suite laeuft gegen die Produktiv-Datenbank.
TEST_USER: str = "test_p9a_mensch"
TEST_CHAR: str = "test_p9a_nova"

# Unverwechselbar. Ein Treffer auf diesen Text kann nur die Fixture-Zeile sein.
MARKER: str = "Testknoten P9a — Ringwallanlage bei Otzenhausen, Marker 4c8e2f"


class VorwissenLiestDieNeueTabelleTest(unittest.TestCase):
    """Der Lesepfad des RechercheAgenten."""

    def setUp(self) -> None:
        """Legt einen Knoten mit Embedding im eigenen Paar an."""
        self.conn = psycopg2.connect(POSTGRES_URL)
        self._aufraeumen()
        # Ein Embedding, das zu jeder Anfrage denselben Abstand hat: Der Test
        # prueft, DASS gefunden wird, nicht wie gut. Die Reihenfolge ist hier
        # ohne Belang, weil nur eine Zeile im Skopus liegt.
        vektor: str = "[" + ",".join(["0.01"] * 768) + "]"
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO lzg_knoten
                    (user_id, character_id, beobachter, inhalt, dimension,
                     gewicht_roh, gewicht_absolut, gewicht_decay,
                     kzg_quell_key, kzg_erstellt_am, embedding, aktiv)
                VALUES (%s, %s, 'user', %s, 'fakt',
                        1.0, 1.0, 1.0,
                        'test-p9a-key', NOW(), %s::vector, TRUE)
                """,
                (TEST_USER, TEST_CHAR, MARKER, vektor),
            )
        self.conn.commit()

    def tearDown(self) -> None:
        """Raeumt das Fixture ab."""
        self._aufraeumen()
        self.conn.close()

    def _aufraeumen(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM lzg_knoten WHERE user_id = %s", (TEST_USER,))
        self.conn.commit()

    def _laden(self, user_id: str, character_id: str) -> list[dict]:
        """Ruft den Lesepfad mit einer Attrappe fuer den Embed-Dienst.

        Die Attrappe liefert denselben Vektor wie die Fixture. Ohne sie
        pruefte der Test die Verfuegbarkeit des Modells statt den Lesepfad.
        """
        class _Antwort:
            embedding = [0.01] * 768
            duration_seconds = 0.0

        with patch.object(lage_mod.model_service.embed, "submit_sync",
                          return_value=_Antwort()):
            return lage_mod._lzg_vorwissen_laden(
                "Ringwallanlage", user_id, character_id, 5,
            )

    def test_der_knoten_wird_gefunden(self) -> None:
        """Der Fall, um den es geht: Vorwissen existiert und wird gemeldet."""
        inhalte: list[str] = [str(t.get("inhalt", "")) for t in self._laden(TEST_USER, TEST_CHAR)]
        self.assertIn(MARKER, inhalte)

    def test_ein_fremdes_paar_findet_ihn_nicht(self) -> None:
        """`lzg_knoten` ist paar-partitioniert; der Lesepfad respektiert das."""
        inhalte: list[str] = [str(t.get("inhalt", "")) for t in self._laden(TEST_USER, "nova")]
        self.assertNotIn(MARKER, inhalte)

    def test_unvollstaendiges_paar_liest_nichts_und_meldet(self) -> None:
        """Ohne vollstaendiges Paar wird gar nicht erst abgefragt."""
        with self.assertLogs("ki_server.pixie.lagebeurteilung", level="WARNING") as protokoll:
            treffer = self._laden(TEST_USER, "")
        self.assertEqual(treffer, [])
        self.assertIn("unvollstaendiges Paar", "\n".join(protokoll.output))

    def test_die_alte_tabelle_wird_nicht_mehr_genannt(self) -> None:
        """Struktur als Zeuge: Der Lesepfad nennt `langzeitgedaechtnis` nicht.

        Ein Verhaltenstest allein faenge das nicht: Solange die alte Tabelle
        existiert und leer ist, liefert ein Zugriff auf sie eine gueltige
        leere Liste — genau die Stille, die den Befund zwei Wochen verdeckt hat.
        """
        quelle: str = textwrap.dedent(inspect.getsource(lage_mod._lzg_vorwissen_laden))
        baum = ast.parse(quelle)
        texte: list[str] = [
            k.value for k in ast.walk(baum)
            if isinstance(k, ast.Constant) and isinstance(k.value, str)
        ]
        # Der Docstring darf die alte Tabelle nennen — er begruendet die
        # Umstellung. Geprueft werden die SQL-Zeichenketten, nicht die Prosa.
        sql: list[str] = [t for t in texte if "SELECT" in t.upper()]
        self.assertTrue(sql, "keine SQL-Zeichenkette gefunden — Test prueft nichts")
        for anweisung in sql:
            self.assertNotIn("langzeitgedaechtnis", anweisung)
            self.assertIn("lzg_knoten", anweisung)


class GravitationVerfaelltEinmalTest(unittest.TestCase):
    """Der Zeitverfall der emotionalen Gravitation — am Aufrufer geprueft.

    Nicht die Formel, sondern `_lzg_emotionale_eintraege` gegen eine echte
    Zeile. Ein Test, der nur zwei Formeln vergleicht, bliebe gruen, waehrend
    der doppelte Verfall im Produktivcode steht — er faesst ihn ja nie an.

    **Das Alter der Zeile wird aus den Konstanten gerechnet, nicht gesetzt.**
    Gesucht ist der Punkt, an dem die richtige Rechnung knapp ueber der
    Aktivierungsschwelle liegt und die alte knapp darunter. Dort trennen sich
    die beiden Fassungen auf die schaerfste Art: Der Knoten wird zurueckgegeben
    oder er verschwindet. Ein Literal an dieser Stelle prueefte nach der
    naechsten Kalibrierung der Schwelle etwas anderes als seinen Namen.
    """

    # `gewicht_decay` steht auf [0, LZG_KNOTEN_GEWICHT_CAP]; die Rechnung
    # normiert es seit dem 30.08.2026 auf [0,1] (EMGRAV-SCHWELLE-TOT). Mit dem
    # frueheren Wert 1.0 erreichte ein Knoten hoechstens eine Gravitation von
    # 0,05 und konnte die Schwelle nicht mehr reissen — das Fixture haette dann
    # ein Alter in der Zukunft gebraucht. 8.0 liegt im Bestand (Median 3,77,
    # Maximum 9,98, gemessen am 30.08.2026 ueber 3266 aktive Knoten).
    GEWICHT: float = 8.0
    EMOTION: str = "freude"

    def setUp(self) -> None:
        """Legt einen alten, emotional besetzten Knoten an."""
        from config import (
            EMOTIONALE_GRAVITATION_ZEIT_HALBWERT,
            EMOTIONALE_GRAVITATIONS_SCHWELLE,
            LZG_KNOTEN_DECAY_RATE,
        )

        # Alter so, dass gravitation = SCHWELLE * 1.005 (knapp darueber).
        # Der Anteil kommt aus der **echten** Rechnung, nicht aus einer hier
        # wiederholten Formel: Seit dem 30.08.2026 normiert sie `gewicht_decay`
        # auf [0,1] (EMGRAV-SCHWELLE-TOT), und eine nachgerechnete Erwartung
        # haette das nicht mitbekommen — sie prueefte weiter die alte Skala.
        from ei.gravitation import gravitation_lzg_berechnen

        ziel: float = EMOTIONALE_GRAVITATIONS_SCHWELLE * 1.005
        # Gravitation bei zeit_decay = 1.0, also fuer einen frischen Knoten.
        grav_frisch: float = gravitation_lzg_berechnen(1.0, self.GEWICHT, 1.0)
        anteil: float = ziel / grav_frisch
        self.tage: float = -EMOTIONALE_GRAVITATION_ZEIT_HALBWERT * math.log2(anteil)

        self.erwartet_richtig: float = ziel
        self.erwartet_alt: float = ziel * math.exp(-LZG_KNOTEN_DECAY_RATE * self.tage)

        # Die Lage selbst zusichern: Ohne sie prueft der Test bei stark
        # verschobenen Konstanten zwar noch etwas, aber nicht das Beschriebene.
        self.assertGreater(self.erwartet_richtig, EMOTIONALE_GRAVITATIONS_SCHWELLE)
        self.assertLess(self.erwartet_alt, EMOTIONALE_GRAVITATIONS_SCHWELLE)

        self.conn = psycopg2.connect(POSTGRES_URL)
        self._aufraeumen()
        vektor: str = "[" + ",".join(["0.01"] * 768) + "]"
        with self.conn.cursor() as cur:
            # Das Alter als Platzhalter, nicht als Zeichenkette: Auch in einem
            # Test wird SQL nicht zusammengesetzt. Der Wert ist hier gerechnet
            # und harmlos — die Regel gilt trotzdem, sonst ist sie keine.
            cur.execute(
                """
                INSERT INTO lzg_knoten
                    (user_id, character_id, beobachter, inhalt, dimension,
                     gewicht_roh, gewicht_absolut, gewicht_decay,
                     emotion, arousal, kzg_quell_key, kzg_erstellt_am,
                     embedding, aktiv, verstaerkt_am)
                VALUES (%s, %s, 'user', %s, 'erlebnis',
                        1.0, 1.0, %s,
                        %s, 0.7, 'test-p9a-grav', NOW(),
                        %s::vector, TRUE, NOW() - (%s * INTERVAL '1 day'))
                """,
                (TEST_USER, TEST_CHAR, MARKER, self.GEWICHT, self.EMOTION,
                 vektor, self.tage),
            )
        self.conn.commit()

    def tearDown(self) -> None:
        """Raeumt das Fixture ab."""
        self._aufraeumen()
        self.conn.close()

    def _aufraeumen(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM lzg_knoten WHERE user_id = %s", (TEST_USER,))
        self.conn.commit()

    def _scannen(self) -> list[dict]:
        import ei.gravitation as grav_mod

        return grav_mod._lzg_emotionale_eintraege(
            [0.01] * 768, POSTGRES_URL, TEST_USER, TEST_CHAR,
            datetime.now(timezone.utc),
        )

    def test_der_knoten_bleibt_ueber_der_schwelle(self) -> None:
        """Unter der alten Bauart faellt genau dieser Knoten heraus."""
        treffer = [k for k in self._scannen() if k["inhalt"].startswith("Testknoten P9a")]
        self.assertEqual(
            len(treffer), 1,
            f"Knoten nicht aktiviert — erwartet {self.erwartet_richtig:.4f}, "
            f"unter doppeltem Verfall waeren es {self.erwartet_alt:.4f}",
        )

    def test_das_gewicht_ist_der_gespeicherte_wert(self) -> None:
        """Kein zweiter Abzug: Was in der Spalte steht, kommt zurueck."""
        treffer = [k for k in self._scannen() if k["inhalt"].startswith("Testknoten P9a")]
        self.assertEqual(len(treffer), 1)
        self.assertAlmostEqual(treffer[0]["gewicht"], self.GEWICHT, places=3)

    def test_gravitation_importiert_die_alte_formel_nicht_mehr(self) -> None:
        """Struktur als Zeuge — geprueft am Syntaxbaum, nicht am Text.

        Ein Textvergleich schluege am Kommentar an, der die Umstellung
        begruendet und die alte Bauart benennen muss.
        """
        import ei.gravitation as grav_mod

        baum = ast.parse(inspect.getsource(grav_mod))
        module: list[str] = []
        for knoten in ast.walk(baum):
            if isinstance(knoten, ast.ImportFrom) and knoten.module:
                module.append(knoten.module)
            elif isinstance(knoten, ast.Import):
                module.extend(alias.name for alias in knoten.names)

        self.assertNotIn("memory.lzg", module)
        # Positiver Zwilling: Die Datei importiert ueberhaupt etwas — sonst
        # bestuende die Zusicherung auch bei einer leeren Liste.
        self.assertGreater(len(module), 3)


if __name__ == "__main__":
    unittest.main()
