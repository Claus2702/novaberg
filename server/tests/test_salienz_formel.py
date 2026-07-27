"""Tests fuer die Salienz-Formel — Bauteil 1b.

    salienz_effektiv  = max( salienz_human × nutzer_gewichtung , salienz_charakter )
    salienz_charakter = max( antriebe ) × (1 + erregungs_zuschlag)

Zwei Fragen stehen im Mittelpunkt.

**Keine Ausloeschung durch Multiplikation.** Ein Faktor, der nur modulieren
soll, darf das Ergebnis nicht allein auf null ziehen. Deshalb stehen die
Antriebe in einem max() und nicht in einem Produkt, deshalb wirkt die Erregung
als (1 + z), und deshalb enthaelt die Gewichtung die Null nicht. Wird die
Salienz null, dann weil alle Gruende null waren — das ist ein Messergebnis und
wird als solches geprueft.

**Welche Zeile die Formel liest.** `charakter_hash` traegt beide Richtungen mit
denselben Spaltennamen; nur die Schluesselreihenfolge unterscheidet sie. Wer
die falsche liest, bekommt die Gewichtung auf dem Kopf. Der Fall hat einen
eigenen Test mit zwei gleichzeitig existierenden Zeilen.

Die DB-Faelle bringen ihr Fixture selbst mit und raeumen es wieder ab —
kein skipUnless, kein skipIf, kein try/except um Importe. Fehlt die Datenbank,
wird der Test rot.
"""

import unittest
from unittest.mock import patch

import psycopg2

from config import ASSISTANT_USER_ID, POSTGRES_URL, RAD_MIN, RAD_MAX
from ei.salienz import salienz_effektiv_berechnen, ANTRIEBE_NICHT_ANGESCHLOSSEN
from memory.charakter import nutzer_gewichtung_laden
from tests.test_salienz_human_transport import _lauf

LOGGER: str = "ki_server.ei.salienz"


def _formel_zeilen(eintraege: list) -> list:
    """Filtert die pipeline_log-Zeilen der Salienz-Formel."""
    return [
        e for e in eintraege
        if e.art == "berechnung" and e.inhalt.get("schritt") == "salienz_formel"
    ]


def _rechne(
    sprachlich: float = 0.0,
    ziel: float = 0.0,
    arousal: float = 0.0,
    human=None,
    gewichtung=None,
):
    """Kurzform fuer den Formel-Aufruf mit benannten Vorgaben."""
    return salienz_effektiv_berechnen(
        sprachlich        = sprachlich,
        ziel_gravitation  = ziel,
        arousal           = arousal,
        salienz_human     = human,
        nutzer_gewichtung = gewichtung,
    )


class FormelAusDemKonzeptTest(unittest.TestCase):
    """Die drei Faelle, die das Konzept als TEST-Zeile vorgibt."""

    def test_gewichtung_unter_eins_daempft(self):
        """max(0.5 × 0.9, 0.0) = 0.45"""
        self.assertEqual(_rechne(human=0.5, gewichtung=0.9).effektiv, 0.45)

    def test_gewichtung_ueber_eins_hebt(self):
        """max(0.5 × 1.5, 0.0) = 0.75"""
        self.assertEqual(_rechne(human=0.5, gewichtung=1.5).effektiv, 0.75)

    def test_eigen_pfad_gewinnt(self):
        """max(0.2 × 0.9, 0.8) = 0.8 — ihr Antrieb schlaegt seinen."""
        ergebnis = _rechne(sprachlich=0.8, human=0.2, gewichtung=0.9)
        self.assertEqual(ergebnis.effektiv, 0.8)
        self.assertEqual(ergebnis.gewinner, "eigen")

    def test_idempotenz(self):
        """Zweimal rechnen liefert bitgleich."""
        a = _rechne(sprachlich=0.37, ziel=0.21, arousal=0.63, human=0.44, gewichtung=1.04)
        b = _rechne(sprachlich=0.37, ziel=0.21, arousal=0.63, human=0.44, gewichtung=1.04)
        self.assertEqual(a, b)


class KeineAusloeschungTest(unittest.TestCase):
    """Kein einzelner Faktor darf das Ergebnis allein umlegen."""

    def test_arousal_null_loescht_den_eigen_pfad_nicht(self):
        """Der Verstaerker wirkt als (1 + z) — bei z=0 bleibt der Wert stehen."""
        self.assertEqual(_rechne(sprachlich=0.6, arousal=0.0).eigen_pfad, 0.6)

    def test_ein_antrieb_bei_null_loescht_den_anderen_nicht(self):
        """max() statt Produkt: ein schweigender Antrieb nimmt nichts weg."""
        self.assertEqual(_rechne(sprachlich=0.7, ziel=0.0).eigen_pfad, 0.7)
        self.assertEqual(_rechne(sprachlich=0.0, ziel=0.7).eigen_pfad, 0.7)

    def test_kleinste_gewichtung_halbiert_hoechstens(self):
        """RAD_MIN ist 0.5 und enthaelt die Null nicht."""
        ergebnis = _rechne(human=0.8, gewichtung=RAD_MIN)
        self.assertEqual(ergebnis.effektiv, 0.4)
        self.assertGreater(ergebnis.effektiv, 0.0)

    def test_alles_null_ergibt_ehrliche_null(self):
        """Der positive Zwilling: eine 0.0 aus lauter Nullen ist ein Ergebnis."""
        ergebnis = _rechne(sprachlich=0.0, ziel=0.0, arousal=0.0, human=0.0, gewichtung=0.9)
        self.assertEqual(ergebnis.effektiv, 0.0)
        self.assertEqual(ergebnis.pflicht_pfad, 0.0)

    def test_erregung_hebt_aber_erschafft_nicht(self):
        """Aus einer belanglosen Aussage macht Erregung keine bedeutsame."""
        self.assertEqual(_rechne(sprachlich=0.0, arousal=1.0).eigen_pfad, 0.0)
        self.assertGreater(_rechne(sprachlich=0.5, arousal=1.0).eigen_pfad, 0.5)


class FehlenderPflichtPfadTest(unittest.TestCase):
    """None ist kein Wert — und 0.0 ist keiner zu wenig."""

    def test_ohne_nutzeraeusserung_kein_pflicht_pfad(self):
        ergebnis = _rechne(sprachlich=0.6, human=None, gewichtung=1.04)
        self.assertIsNone(ergebnis.pflicht_pfad)
        self.assertEqual(ergebnis.gewinner, "eigen")
        self.assertEqual(ergebnis.effektiv, 0.6)

    def test_ohne_gewichtung_kein_pflicht_pfad(self):
        ergebnis = _rechne(sprachlich=0.6, human=0.9, gewichtung=None)
        self.assertIsNone(ergebnis.pflicht_pfad)

    def test_nutzersalienz_null_ist_ein_pflicht_pfad(self):
        """Der positive Zwilling zu den beiden Faellen darueber."""
        ergebnis = _rechne(sprachlich=0.6, human=0.0, gewichtung=1.04)
        self.assertIsNotNone(ergebnis.pflicht_pfad)
        self.assertEqual(ergebnis.pflicht_pfad, 0.0)


class SkalaTest(unittest.TestCase):
    """Die Skala endet bei 1.0, und die Kappung wird vermerkt."""

    def test_ueber_eins_wird_gekappt_und_markiert(self):
        ergebnis = _rechne(human=1.0, gewichtung=1.5)
        self.assertEqual(ergebnis.effektiv, 1.0)
        self.assertTrue(ergebnis.gekappt)

    def test_im_bereich_bleibt_ungekappt(self):
        """Positiver Zwilling: gekappt ist nicht immer True."""
        self.assertFalse(_rechne(human=0.5, gewichtung=0.9).gekappt)

    def test_gewichtung_ausserhalb_wird_gekappt_und_genannt(self):
        with self.assertLogs(LOGGER, level="WARNING") as protokoll:
            ergebnis = _rechne(human=0.4, gewichtung=2.0)
        self.assertIn("2.0000", "\n".join(protokoll.output))
        self.assertEqual(ergebnis.pflicht_pfad, round(0.4 * RAD_MAX, 4))

    def test_arousal_ausserhalb_wird_gekappt_und_genannt(self):
        with self.assertLogs(LOGGER, level="WARNING") as protokoll:
            ergebnis = _rechne(sprachlich=0.5, arousal=1.5)
        self.assertIn("1.500", "\n".join(protokoll.output))
        self.assertEqual(ergebnis.erregungs_zuschlag, 0.3)


class HerkunftImErgebnisTest(unittest.TestCase):
    """Das Ergebnis traegt, woraus es entstand."""

    def test_gewinner_wird_benannt(self):
        self.assertEqual(_rechne(sprachlich=0.1, human=0.9, gewichtung=1.0).gewinner, "pflicht")
        self.assertEqual(_rechne(sprachlich=0.9, human=0.1, gewichtung=1.0).gewinner, "eigen")

    def test_antriebe_stehen_benannt_nicht_gezaehlt(self):
        antriebe: dict = _rechne(sprachlich=0.4, ziel=0.25).antriebe
        self.assertEqual(antriebe, {"sprachlich": 0.4, "ziel_gravitation": 0.25})

    def test_fehlende_antriebe_werden_mitgefuehrt(self):
        """Zwei von vier Antrieben schweigen — das gehoert ins Ergebnis, sonst
        sieht ein max() ueber zwei aus wie eines ueber vier."""
        ergebnis = _rechne(sprachlich=0.4)
        self.assertEqual(ergebnis.nicht_angeschlossen, ANTRIEBE_NICHT_ANGESCHLOSSEN)
        self.assertIn("emotionale_gravitation", ergebnis.nicht_angeschlossen)
        self.assertIn("neugier", ergebnis.nicht_angeschlossen)


class NutzerGewichtungLadenTest(unittest.TestCase):
    """Welche Zeile gelesen wird — die Vorbedingung aus dem Konzept §8."""

    GEGENUEBER: str = "__test_gegenueber_salienz__"

    def setUp(self) -> None:
        """Legt beide Richtungen des Paares an, mit verschiedenen Faktoren.

        Novas Zeile (ASSISTANT_USER_ID, GEGENUEBER) traegt 1.31, die Gegenzeile
        (GEGENUEBER, ASSISTANT_USER_ID) traegt 0.62. Wuerde die falsche gelesen,
        koennte kein Test das je bemerken, wenn nur eine existierte.
        """
        self._schreiben(ASSISTANT_USER_ID, self.GEGENUEBER, 1.31, "destilliert")
        self._schreiben(self.GEGENUEBER, ASSISTANT_USER_ID, 0.62, "destilliert")

    def tearDown(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM charakter_hash WHERE user_id = %s OR character_id = %s",
                    (self.GEGENUEBER, self.GEGENUEBER),
                )
        finally:
            conn.close()

    @staticmethod
    def _schreiben(user_id: str, character_id: str, faktor: float, quelle: str) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO charakter_hash (user_id, character_id, "
                    "nutzer_gewichtung, nutzer_gewichtung_quelle) VALUES (%s, %s, %s, %s) "
                    "ON CONFLICT (user_id, character_id) DO UPDATE SET "
                    "nutzer_gewichtung = EXCLUDED.nutzer_gewichtung, "
                    "nutzer_gewichtung_quelle = EXCLUDED.nutzer_gewichtung_quelle",
                    (user_id, character_id, faktor, quelle),
                )
        finally:
            conn.close()

    def test_liest_novas_zuwendung_nicht_die_gegenrichtung(self):
        faktor, quelle = nutzer_gewichtung_laden(POSTGRES_URL, self.GEGENUEBER)
        self.assertEqual(faktor, 1.31)
        self.assertEqual(quelle, "destilliert")
        # Der eigentliche Beweis: Es ist nicht der Wert der Gegenzeile.
        self.assertNotEqual(faktor, 0.62)

    def test_fehlendes_paar_liefert_none_statt_nabe(self):
        """Nicht (0.9, 'default') — sonst saehe ein Lesefehler aus wie ein
        Charakter ohne Auspraegung."""
        faktor, quelle = nutzer_gewichtung_laden(POSTGRES_URL, "__gibt_es_nicht__")
        self.assertIsNone(faktor)
        self.assertEqual(quelle, "fehlt")

    def test_leere_user_id_wird_abgelehnt(self):
        with self.assertLogs("ki_server.memory.charakter", level="ERROR"):
            faktor, quelle = nutzer_gewichtung_laden(POSTGRES_URL, "")
        self.assertIsNone(faktor)
        self.assertEqual(quelle, "fehlt")

    def test_gelesener_faktor_liegt_im_radbereich(self):
        faktor, _ = nutzer_gewichtung_laden(POSTGRES_URL, self.GEGENUEBER)
        self.assertGreaterEqual(faktor, RAD_MIN)
        self.assertLessEqual(faktor, RAD_MAX)


class FormelImNodeTest(unittest.TestCase):
    """Wer die Formel rechnet — und wer ausdruecklich nicht."""

    def _mit_faktor(self, rolle: str, salienzen: list, faktor: float = 1.04, **kw):
        """Fuehrt analyze() aus, mit dem Charakter-Faktor als Vorgabe.

        Der Faktor wird gestellt statt aus der Datenbank gelesen: Geprueft wird
        hier die Verdrahtung im Node, nicht der Leser — der hat seine eigenen
        Tests eine Klasse weiter oben.
        """
        with patch("graph.nodes.salience.nutzer_gewichtung_laden",
                   return_value=(faktor, "destilliert")):
            return _lauf(rolle, salienzen, postgres_url="postgres://attrappe", **kw)

    def test_charactergraph_rechnet_die_formel(self):
        """0.7 × 1.04 = 0.728 schlaegt den Eigen-Pfad von 0.5."""
        _, ergebnis = self._mit_faktor("character", [0.5], salienz_human=0.7)
        gespeichert: float = ergebnis["pending_writes"][0]["daten"]["salienz_obj"]["salienz"]
        self.assertEqual(gespeichert, 0.728)

    def test_humangraph_rechnet_die_formel_nicht(self):
        """Der Nutzer-Eintrag behaelt seine Salienz — dort greift weiter der
        alte Gravitationsboost, bis Bauteil 1 ihn ausbaut."""
        _, ergebnis = self._mit_faktor("human", [0.5], salienz_human=0.7, gravitationsterm=0.3)
        gespeichert: float = ergebnis["pending_writes"][0]["daten"]["salienz_obj"]["salienz"]
        self.assertEqual(gespeichert, 0.8)

    def test_agentgraph_faellt_auf_den_eigen_pfad(self):
        """Ein eigener Gedanke hat keine Nutzeraeusserung — und trotzdem eine
        Salienz. Nicht null, weil die Lesung seines Textes ein Antrieb ist."""
        eintraege, ergebnis = self._mit_faktor("agent", [0.6])
        gespeichert: float = ergebnis["pending_writes"][0]["daten"]["salienz_obj"]["salienz"]
        self.assertEqual(gespeichert, 0.6)

        zeile: dict = _formel_zeilen(eintraege)[0].inhalt
        self.assertIsNone(zeile["pflicht_pfad"])
        self.assertEqual(zeile["gewinner"], "eigen")

    def test_gravitation_zaehlt_nicht_zweimal(self):
        """Im CharacterGraph ist die Gravitation ein Antrieb im max(), kein
        Zuschlag obendrauf. 0.5 und Gravitation 0.3 ergeben 0.5, nicht 0.8."""
        _, ergebnis = self._mit_faktor("character", [0.5], gravitationsterm=0.3)
        gespeichert: float = ergebnis["pending_writes"][0]["daten"]["salienz_obj"]["salienz"]
        self.assertEqual(gespeichert, 0.5)

    def test_pipeline_log_traegt_beide_operanden(self):
        eintraege, _ = self._mit_faktor("character", [0.5], salienz_human=0.7)
        zeilen: list = _formel_zeilen(eintraege)

        self.assertEqual(len(zeilen), 1)
        inhalt: dict = zeilen[0].inhalt
        self.assertEqual(inhalt["salienz_effektiv"],  0.728)
        self.assertEqual(inhalt["gewinner"],          "pflicht")
        self.assertEqual(inhalt["pflicht_pfad"],      0.728)
        self.assertEqual(inhalt["eigen_pfad"],        0.5)
        self.assertEqual(inhalt["salienz_human"],     0.7)
        self.assertEqual(inhalt["nutzer_gewichtung"], 1.04)
        self.assertEqual(inhalt["gewichtung_quelle"], "destilliert")
        # Die schweigenden Antriebe stehen mit drin — sonst saehe ein max()
        # ueber zwei aus wie eines ueber vier.
        self.assertEqual(
            set(inhalt["nicht_angeschlossen"]), set(ANTRIEBE_NICHT_ANGESCHLOSSEN),
        )

    def test_ohne_datenbank_kein_pflicht_pfad_und_eine_fehlerzeile(self):
        """Kein stiller Ruecktritt auf die Nabe 0.9."""
        with self.assertLogs("ki_server.salience", level="ERROR") as protokoll:
            eintraege, _ = _lauf("character", [0.5], salienz_human=0.7)

        self.assertIn("nutzer_gewichtung nicht ladbar", "\n".join(protokoll.output))
        zeile: dict = _formel_zeilen(eintraege)[0].inhalt
        self.assertIsNone(zeile["pflicht_pfad"])
        self.assertEqual(zeile["gewichtung_quelle"], "fehlt")


if __name__ == "__main__":
    unittest.main()
