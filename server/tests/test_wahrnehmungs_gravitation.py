"""Tests fuer die Wahrnehmungs-Gravitation (Konzept §8.5).

Ziel: Der Suchschluessel der LZG-Suche ist nicht mehr allein die Frage des
Turns, sondern die Frage plus Novas aktivierte Ziele — cluster-abhaengig stark,
und bei einer direkten Anweisung gar nicht.

Hintergrund: Bis P10 suchte der Enricher mit dem rohen Anfrage-Embedding. Die
Verschiebung ist der letzte Sprint des Synapsen-Umbaus und beruehrt die
LZG-Tabellen nicht — sie aendert nur, womit gesucht wird.

Die Zeugen:

  * Die erwarteten Vektoren sind von Hand nach der Formel aus §8.5.1 gerechnet,
    nicht mit `wahrnehmung_verschieben` erzeugt. Der Cluster-Faktor geht dabei
    als Konstante ein und nicht als Zahl: Er ist ausdruecklich zur
    Live-Kalibrierung bestimmt, und ein Literal wuerde danach still etwas
    anderes pruefen, als sein Name behauptet.
  * Die Schluesselmenge der neuen Tabelle wird gegen die **bestehenden**
    Cluster-Tabellen geprueft, nicht gegen sich selbst.
  * Die Verdrahtung wird am Aufrufer geprueft, nicht am Baustein: Der Defekt,
    der hier moeglich ist, sitzt nicht in der Rechnung, sondern darin, dass ihr
    Ergebnis die Suche nie erreicht.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
import uuid
from contextlib import ExitStack
from unittest.mock import MagicMock, patch

import graph.nodes.enricher as enricher_mod
from ei.dreischicht import (
    CLUSTER_BESCHREIBUNGEN,
    CLUSTER_ENRICHER_SPRUENGE,
    CLUSTER_GRAVITATION_FAKTOR,
    GRAVITATION_FAKTOR_ANWEISUNG,
    INTENTION_ANWEISUNG,
)
from ei.gravitation import ActivatedGoal, wahrnehmung_verschieben

GRAVITATION_LOGGER: str = "ki_server.ei.gravitation"

# Vier Dimensionen statt 768 — die Formel ist dimensionsunabhaengig, und mit
# vier Werten laesst sich das Ergebnis von Hand hinschreiben.
ROH: list[float] = [1.0, 0.0, 0.0, 0.0]
QUER: list[float] = [0.0, 1.0, 0.0, 0.0]
GEGEN: list[float] = [-1.0, 0.0, 0.0, 0.0]

# Zwei Cluster mit ausdruecklich verschiedener Faerbung (Abnahme-Test 4).
CLUSTER_FOKUS: str = "werkstatt"
CLUSTER_FREI: str = "glut"


def _ziel(
    staerke:   float,
    embedding: list[float] | None,
    ziel_id:   int = 1,
) -> ActivatedGoal:
    """Ein aktiviertes Ziel als Fixture.

    Die Aktivierungs-Staerke wird gesetzt, nicht gerechnet: Wie sie entsteht,
    ist Sache von `ziel_gravitation_berechnen` und hier nicht der Gegenstand.
    """
    return ActivatedGoal(
        ziel_id=ziel_id,
        ziel_typ="langfristig",
        zielsatz=f"Testziel {ziel_id}",
        motivation=1.0,
        emotion="",
        arousal=0.5,
        similarity=staerke,
        aktivierungs_staerke=staerke,
        embedding=embedding,
    )


class FaktorTabelleTest(unittest.TestCase):
    """Die Cluster-Tabelle als Struktur — der Zeuge sind die Nachbartabellen."""

    def test_schluesselmenge_wie_die_uebrigen_cluster_tabellen(self) -> None:
        """Ein Cluster ohne Faktor faellt in den Fehlerpfad statt zu faerben."""
        self.assertEqual(
            set(CLUSTER_GRAVITATION_FAKTOR),
            set(CLUSTER_ENRICHER_SPRUENGE),
        )
        self.assertEqual(
            set(CLUSTER_GRAVITATION_FAKTOR),
            set(CLUSTER_BESCHREIBUNGEN),
        )

    def test_jeder_faktor_liegt_in_der_konzept_spanne(self) -> None:
        """Konzept §11.4 nennt 0.05 bis 0.30.

        Ein Wert darueber faerbt staerker, als die Phaenomenologie es an
        irgendeiner Stelle vorsieht.
        """
        for cluster, faktor in CLUSTER_GRAVITATION_FAKTOR.items():
            with self.subTest(cluster=cluster):
                self.assertGreaterEqual(faktor, 0.0)
                self.assertLessEqual(faktor, 0.30)

    def test_werkstatt_verschiebt_weniger_als_glut(self) -> None:
        """Abnahme-Test 4: Die Faerbung haengt am Cluster.

        Fokus-Cluster halten Nova bei der Sache, freie lassen sie treiben.
        Eine globale Konstante wuerde diesen Test nicht bestehen.
        """
        self.assertLess(
            CLUSTER_GRAVITATION_FAKTOR[CLUSTER_FOKUS],
            CLUSTER_GRAVITATION_FAKTOR[CLUSTER_FREI],
        )

    def test_der_imperativ_faktor_unterdrueckt_vollstaendig(self) -> None:
        """Konzept §8.5.3 nennt eine Spanne von 0.0 bis 0.05.

        Nur die untere Grenze traegt die Zusicherung, dass mit dem rohen
        Embedding gesucht wird.
        """
        self.assertEqual(GRAVITATION_FAKTOR_ANWEISUNG, 0.0)


class VerschiebungRechnungTest(unittest.TestCase):
    """Die Formel aus §8.5.1, gegen von Hand gerechnete Erwartungen."""

    def test_ein_ziel_wird_nach_der_formel_gemischt(self) -> None:
        """Ein Ziel quer zur Frage zieht den Suchschluessel anteilig zu sich."""
        faktor: float = CLUSTER_GRAVITATION_FAKTOR[CLUSTER_FREI]
        # Zusicherung ueber die Lage: Bei Faktor 0 pruefte der Fall nichts.
        self.assertGreater(faktor, 0.0)

        # e_nova = [1,0,0,0] x (1-f) + [0,0.5,0,0] x f
        erwartet: list[float] = [1.0 * (1.0 - faktor), 0.5 * faktor, 0.0, 0.0]

        with self.assertLogs(GRAVITATION_LOGGER, level="INFO"):
            ergebnis = wahrnehmung_verschieben(
                anfrage_embedding=ROH,
                aktivierte_ziele=[_ziel(0.5, QUER)],
                cluster=CLUSTER_FREI,
                ist_anweisung=False,
            )

        self.assertEqual(ergebnis.herkunft, "verschoben")
        self.assertEqual(ergebnis.faktor, faktor)
        for gemessen, soll in zip(ergebnis.vektor, erwartet, strict=True):
            self.assertAlmostEqual(gemessen, soll, places=9)

    def test_zwei_ziele_verstaerken_sich(self) -> None:
        """Die Summe wird nicht normiert — zwei Ziele ziehen staerker als eins.

        Das ist die Formel des Konzepts und zugleich der Grund, warum es die
        Spannenpruefung ueberhaupt braucht.
        """
        faktor: float = CLUSTER_GRAVITATION_FAKTOR[CLUSTER_FREI]
        erwartet_quer: float = (0.5 + 0.4) * faktor

        with self.assertLogs(GRAVITATION_LOGGER, level="INFO"):
            ergebnis = wahrnehmung_verschieben(
                anfrage_embedding=ROH,
                aktivierte_ziele=[_ziel(0.5, QUER, 1), _ziel(0.4, QUER, 2)],
                cluster=CLUSTER_FREI,
                ist_anweisung=False,
            )

        self.assertAlmostEqual(ergebnis.vektor[1], erwartet_quer, places=9)
        self.assertEqual(ergebnis.ziel_anteile, [0.5, 0.4])

    def test_fokus_cluster_verschiebt_weniger_als_freier_cluster(self) -> None:
        """Dieselbe Lage, zwei Cluster.

        Der Cosinus zum rohen Vektor sagt, wie weit der Suchschluessel von der
        Frage weggewandert ist.
        """
        with self.assertLogs(GRAVITATION_LOGGER, level="INFO"):
            fokus = wahrnehmung_verschieben(ROH, [_ziel(0.5, QUER)], CLUSTER_FOKUS, False)
            frei = wahrnehmung_verschieben(ROH, [_ziel(0.5, QUER)], CLUSTER_FREI, False)

        self.assertGreater(fokus.cosinus_zu_roh, frei.cosinus_zu_roh)
        self.assertLess(frei.cosinus_zu_roh, 1.0)

    def test_dimension_bleibt_erhalten(self) -> None:
        """Der Suchschluessel muss zur Spalte passen, gegen die er sucht."""
        with self.assertLogs(GRAVITATION_LOGGER, level="INFO"):
            ergebnis = wahrnehmung_verschieben(
                [0.5] * 768, [_ziel(0.5, [0.1] * 768)], CLUSTER_FREI, False,
            )
        self.assertEqual(len(ergebnis.vektor), 768)


class VerschiebungRandfaelleTest(unittest.TestCase):
    """Die Ausgaenge. Jeder liefert das rohe Embedding und sagt, warum."""

    def test_leeres_anfrage_embedding_meldet_und_verschiebt_nicht(self) -> None:
        """Ohne Frage gibt es nichts zu faerben — und das ist ein Defekt."""
        with self.assertLogs(GRAVITATION_LOGGER, level="ERROR") as protokoll:
            ergebnis = wahrnehmung_verschieben([], [_ziel(0.5, QUER)], CLUSTER_FREI, False)

        self.assertEqual(ergebnis.herkunft, "kein_anfrage_embedding")
        self.assertEqual(ergebnis.vektor, [])
        self.assertIn("leeres Anfrage-Embedding", protokoll.output[0])

    def test_unbekannter_cluster_meldet_und_verschiebt_nicht(self) -> None:
        """Zugehoerigkeit zum Kanon.

        Ein 15. Cluster darf nicht still wie 'paradox' faerben — sonst waere
        ein unbekannter Wert von einem gueltigen nicht zu unterscheiden.
        """
        with self.assertLogs(GRAVITATION_LOGGER, level="ERROR") as protokoll:
            ergebnis = wahrnehmung_verschieben(
                ROH, [_ziel(0.5, QUER)], "kneipe", False,
            )

        self.assertEqual(ergebnis.herkunft, "cluster_unbekannt")
        self.assertEqual(ergebnis.vektor, ROH)
        self.assertIn("kneipe", protokoll.output[0])

    def test_anweisung_unterdrueckt_die_verschiebung(self) -> None:
        """Abnahme-Test 2: Bei einer direkten Aufgabe sucht die rohe Frage."""
        with self.assertLogs(GRAVITATION_LOGGER, level="INFO") as protokoll:
            ergebnis = wahrnehmung_verschieben(
                ROH, [_ziel(0.9, QUER)], CLUSTER_FREI, True,
            )

        self.assertEqual(ergebnis.herkunft, "anweisung")
        self.assertEqual(ergebnis.vektor, ROH)
        self.assertEqual(ergebnis.faktor, 0.0)
        self.assertIn("Imperativ-Override", protokoll.output[0])

    def test_ohne_ziele_bleibt_das_embedding_roh(self) -> None:
        """Ein Turn ohne aktives Ziel sucht wie vor P10."""
        with self.assertLogs(GRAVITATION_LOGGER, level="INFO"):
            ergebnis = wahrnehmung_verschieben(ROH, [], CLUSTER_FREI, False)

        self.assertEqual(ergebnis.herkunft, "keine_ziele")
        self.assertEqual(ergebnis.vektor, ROH)
        self.assertEqual(ergebnis.ziel_anteile, [])

    def test_ziel_ohne_embedding_ist_ein_anderer_fall_als_kein_ziel(self) -> None:
        """Leer und nicht vorhanden sind zwei Faelle.

        Ein Ziel ohne Embedding ist aktiv und traegt trotzdem nichts bei; das
        ist etwas anderes als ein Turn ganz ohne Ziele.
        """
        with self.assertLogs(GRAVITATION_LOGGER, level="INFO"):
            ergebnis = wahrnehmung_verschieben(
                ROH, [_ziel(0.5, None)], CLUSTER_FREI, False,
            )

        self.assertEqual(ergebnis.herkunft, "kein_ziel_embedding")
        self.assertEqual(ergebnis.ziel_anteile, [0.5])

    def test_ziel_mit_falscher_dimension_meldet_und_verschiebt_nicht(self) -> None:
        """Ein Ziel aus einem anderen Embedding-Modell bricht die Rechnung."""
        with self.assertLogs(GRAVITATION_LOGGER, level="ERROR") as protokoll:
            ergebnis = wahrnehmung_verschieben(
                ROH, [_ziel(0.5, [0.1, 0.2])], CLUSTER_FREI, False,
            )

        self.assertEqual(ergebnis.herkunft, "dimension_ungleich")
        self.assertEqual(ergebnis.vektor, ROH)
        self.assertIn("Dimension 2", protokoll.output[0])

    def test_umgedrehte_frage_wird_verworfen_statt_gekappt(self) -> None:
        """Drei gegenlaeufige Ziele ueberwiegen den Anfrage-Anteil.

        Das Ergebnis zeigt von der Frage weg und ist keine Faerbung mehr,
        sondern ein Austausch der Frage. Es wird gemeldet und verworfen —
        eine Kappung machte den Rechenfehler von einer Randbedingung
        ununterscheidbar.
        """
        ziele = [_ziel(0.9, GEGEN, i) for i in (1, 2, 3)]

        with self.assertLogs(GRAVITATION_LOGGER, level="ERROR") as protokoll:
            ergebnis = wahrnehmung_verschieben(ROH, ziele, CLUSTER_FREI, False)

        self.assertEqual(ergebnis.herkunft, "verworfen_ausser_spanne")
        self.assertEqual(ergebnis.vektor, ROH)
        self.assertIn("ausserhalb der Spanne", protokoll.output[0])

    def test_dieselben_ziele_in_geringerer_zahl_bleiben_gueltig(self) -> None:
        """Der positive Zwilling zur Verwerfung.

        Ein einzelnes gegenlaeufiges Ziel dreht die Frage nicht um — die
        Verwerfung oben ist eine Grenze, keine Blockade.
        """
        with self.assertLogs(GRAVITATION_LOGGER, level="INFO"):
            ergebnis = wahrnehmung_verschieben(
                ROH, [_ziel(0.9, GEGEN)], CLUSTER_FREI, False,
            )

        self.assertEqual(ergebnis.herkunft, "verschoben")
        self.assertGreater(ergebnis.cosinus_zu_roh, 0.0)


class EnricherVerdrahtungTest(unittest.TestCase):
    """Die Verdrahtung, nicht der Baustein.

    Eine Rechnung mit gruenen Tests, deren Ergebnis die Suche nie erreicht,
    besteht jeden Modul-Test. Geprueft wird deshalb, was `spreading_lesen`
    tatsaechlich als Suchschluessel bekommt.
    """

    def _lauf(
        self,
        intentionen: list[str],
        ziele:       list[ActivatedGoal],
        has_lzg:     bool = True,
    ) -> tuple[list[float] | None, list[dict]]:
        """Faehrt `_enrich_character` und liefert (Suchschluessel, Protokoll).

        Der Suchschluessel ist das Argument, das der Enricher an
        `embedding_zu_pgvector_str` reicht — die letzte Stelle, an der der
        Vektor noch ein Vektor ist. Laeuft keine LZG-Suche, bleibt er None.
        """
        gesucht: list = []
        protokoll: list[dict] = []

        cursor = MagicMock()
        cursor.fetchone.return_value = (has_lzg,)
        verbindung = MagicMock()
        verbindung.cursor.return_value = cursor
        psycopg2_attrappe = MagicMock()
        psycopg2_attrappe.connect.return_value = verbindung

        redis_attrappe = MagicMock()
        redis_attrappe.get.return_value = None
        redis_attrappe.keys.return_value = []

        state: dict = {
            "turn_id":          "test-turn",
            "character_id":     "test_charakter",
            "user_prompt":      "Wie entsteht Hawking-Strahlung?",
            "user_intentionen": intentionen,
            "ei_calc_rolle":    "character",
        }

        with ExitStack() as stack:
            p = stack.enter_context
            p(patch.object(enricher_mod, "psycopg2", psycopg2_attrappe))
            p(patch.object(enricher_mod, "get_registry", return_value={}))
            p(patch.object(enricher_mod, "_load_raw_turns", return_value=[]))
            p(patch.object(enricher_mod, "_create_prompt_embedding", return_value=ROH))
            p(patch.object(
                enricher_mod, "_compute_ziele_und_gravitation",
                return_value=(ziele, 0.5),
            ))
            p(patch.object(enricher_mod, "_vorturn_cluster_lesen", return_value=CLUSTER_FREI))
            p(patch.object(enricher_mod, "spreading_lesen", return_value=[]))
            p(patch.object(enricher_mod, "kzg_entries_retrieve", return_value=[]))
            p(patch.object(enricher_mod, "emotionale_gravitation_scannen", return_value=[]))
            p(patch.object(
                enricher_mod, "embedding_zu_pgvector_str",
                side_effect=lambda v: gesucht.append(v) or "[]",
            ))
            p(patch.object(enricher_mod, "span_start", return_value=uuid.uuid4()))
            p(patch.object(enricher_mod, "span_end"))
            p(patch.object(enricher_mod, "log_eingang"))
            p(patch.object(enricher_mod, "log_switch"))
            p(patch.object(enricher_mod, "log_ausgabe"))
            p(patch.object(
                enricher_mod, "log_berechnung",
                side_effect=lambda **kw: protokoll.append(kw),
            ))

            enricher_mod._enrich_character(
                state, redis_attrappe, "postgresql://test", "test_mensch",
            )

        return (gesucht[0] if gesucht else None), protokoll

    def _verschiebungs_eintrag(self, protokoll: list[dict]) -> dict:
        """Der eine Eintrag der Wahrnehmungs-Gravitation aus dem Protokoll."""
        eintraege = [
            e for e in protokoll if e.get("quelle") == "wahrnehmungs_gravitation"
        ]
        self.assertEqual(len(eintraege), 1, "genau ein Eintrag je Durchlauf")
        return eintraege[0]["inhalt"]

    def test_die_suche_bekommt_den_verschobenen_vektor(self) -> None:
        """Abnahme-Test 1: Bei aktiven Zielen sucht nicht mehr die rohe Frage."""
        faktor: float = CLUSTER_GRAVITATION_FAKTOR[CLUSTER_FREI]
        erwartet: list[float] = [1.0 * (1.0 - faktor), 0.5 * faktor, 0.0, 0.0]

        gesucht, _ = self._lauf(intentionen=[], ziele=[_ziel(0.5, QUER)])

        self.assertIsNotNone(gesucht)
        for gemessen, soll in zip(gesucht, erwartet, strict=True):
            self.assertAlmostEqual(gemessen, soll, places=9)

    def test_bei_anweisung_sucht_die_rohe_frage(self) -> None:
        """Abnahme-Test 2 am Aufrufer: Der Marker muss die Rechnung erreichen."""
        gesucht, _ = self._lauf(
            intentionen=[INTENTION_ANWEISUNG], ziele=[_ziel(0.5, QUER)],
        )
        self.assertEqual(gesucht, ROH)

    def test_ohne_anweisung_wird_derselbe_turn_verschoben(self) -> None:
        """Der positive Zwilling zum Override.

        Ohne ihn waere ein Test, der immer das rohe Embedding sieht, ebenfalls
        gruen — und die Zusicherung ueber den Marker damit leer.
        """
        gesucht, _ = self._lauf(intentionen=["planung"], ziele=[_ziel(0.5, QUER)])
        self.assertNotEqual(gesucht, ROH)

    def test_das_protokoll_traegt_die_zerlegung(self) -> None:
        """Abnahme-Test 6: Die Eingangsgroessen stehen einzeln im Eintrag.

        Ein zusammengesetzter Wert ohne seine Zerlegung ist spaeter nicht
        nachrechenbar.
        """
        _, protokoll = self._lauf(
            intentionen=[], ziele=[_ziel(0.5, QUER, 1), _ziel(0.4, QUER, 2)],
        )
        inhalt = self._verschiebungs_eintrag(protokoll)

        self.assertEqual(inhalt["herkunft"], "verschoben")
        self.assertEqual(inhalt["cluster"], CLUSTER_FREI)
        self.assertEqual(inhalt["faktor"], CLUSTER_GRAVITATION_FAKTOR[CLUSTER_FREI])
        self.assertEqual(inhalt["ziel_anteile"], [0.5, 0.4])
        self.assertEqual(inhalt["ziele_count"], 2)
        self.assertEqual(inhalt["anfrage_dim"], len(ROH))
        self.assertLess(inhalt["cosinus_zu_roh"], 1.0)

    def test_das_protokoll_nennt_den_imperativ(self) -> None:
        """Der unterdrueckte Turn ist im Protokoll als solcher erkennbar."""
        _, protokoll = self._lauf(
            intentionen=[INTENTION_ANWEISUNG], ziele=[_ziel(0.5, QUER)],
        )
        self.assertEqual(self._verschiebungs_eintrag(protokoll)["herkunft"], "anweisung")

    def test_ohne_lzg_steht_der_uebersprung_im_protokoll(self) -> None:
        """Ein Durchlauf ohne Suche schreibt trotzdem einen Eintrag.

        Sonst waere er von einem Durchlauf ohne Verschiebung nicht zu
        unterscheiden, und der Leser saehe den Stand des Vorturns.
        """
        gesucht, protokoll = self._lauf(
            intentionen=[], ziele=[_ziel(0.5, QUER)], has_lzg=False,
        )

        self.assertIsNone(gesucht)
        self.assertEqual(
            self._verschiebungs_eintrag(protokoll)["herkunft"], "keine_lzg_suche",
        )


if __name__ == "__main__":
    unittest.main()
