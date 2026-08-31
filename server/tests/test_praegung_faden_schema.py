"""Zeuge fuer die Praegungsschicht, Scheibe 1: der Faden und seine Tabellen.

Ziel: Ein Turn mit hoher Salienz und hohem Emotionsausschlag hinterlaesst einen
Faden — mit dem Eingangswert, aus dem sich alles Weitere ableitet, und einem
Rueckbezug auf seine Quelle.

**Diese Datei ist der Zuender** (`F-DDL-1`): Sie ist eine Python-Datei und loest
denselben Neustart aus wie jede andere. Sie wird vor dem Schema-Edit angelegt,
damit die rote Phase nicht verloren geht — ein Test, den man nie hat scheitern
sehen, ist eine Behauptung ueber sich selbst.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

import psycopg2

from config import POSTGRES_URL
from memory.praegung import (
    ausschlag_absolut_berechnen,
    beruehrung_anlegen,
    faden_anlegen,
    tor_urteil,
)


class DieFadenTabellenStehenTest(unittest.TestCase):
    """Das Schema traegt beide Tabellen mit den Feldern aus dem Konzept."""

    ERWARTET_FADEN: set[str] = {
        "id", "user_id", "character_id", "beobachter", "turn_id", "embedding",
        "emotion", "ausschlag_eingang", "ausschlag_absolut", "ausschlag_aktuell",
        "ausgang", "herkunft", "entstanden_am",
    }
    ERWARTET_BERUEHRUNG: set[str] = {"id", "faden_id", "beruehrt_am", "quelle"}

    def _spalten(self, tabelle: str) -> set[str]:
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = %s", (tabelle,),
            )
            return {z[0] for z in cur.fetchall()}

    def test_praegung_faden_traegt_alle_felder(self) -> None:
        """Der Eingangswert entscheidet alles — er darf nicht fehlen."""
        vorhanden: set[str] = self._spalten("praegung_faden")
        self.assertTrue(vorhanden, "Tabelle `praegung_faden` existiert nicht")
        fehlend: set[str] = self.ERWARTET_FADEN - vorhanden
        self.assertFalse(
            fehlend, f"Felder fehlen in `praegung_faden`: {sorted(fehlend)}",
        )

    def test_praegung_beruehrung_traegt_alle_felder(self) -> None:
        """Ohne eigene Tabelle kodiert ein Zeitstempel die Verfallsfunktion."""
        vorhanden: set[str] = self._spalten("praegung_beruehrung")
        self.assertTrue(vorhanden, "Tabelle `praegung_beruehrung` existiert nicht")
        fehlend: set[str] = self.ERWARTET_BERUEHRUNG - vorhanden
        self.assertFalse(
            fehlend, f"Felder fehlen in `praegung_beruehrung`: {sorted(fehlend)}",
        )

    def test_das_paar_schema_ist_eingehalten(self) -> None:
        """`user_id` ist das Subjekt, `character_id` das Gegenueber.

        Ohne beide waere ein Faden nicht einem Paar zuzuordnen — und die
        Praegung ist eine Eigenschaft Novas gegenueber jemandem, nicht global.
        """
        vorhanden: set[str] = self._spalten("praegung_faden")
        for feld in ("user_id", "character_id", "beobachter"):
            self.assertIn(feld, vorhanden, f"`{feld}` fehlt — Paar-Schema verletzt")


if __name__ == "__main__":
    unittest.main()


class DieFormkurveTrenntWoDieFaedenLiegenTest(unittest.TestCase):
    """`sin(x * pi/2) ** 2` — die Werte stammen aus der Tabelle in §7.2.

    Nachgerechnet statt symbolisch gefuehrt: Ein Zeuge, der nur
    `f(EINGANG) == f(EINGANG)` prueft, bleibt gruen, wenn jemand den Exponenten
    angleicht — und genau davor warnt das Konzept, weil `sin^0.5` an der
    Faszination und `sin^2` am Faden nebeneinander stehen.
    """

    # Konzept §7.2, Spalte sin²
    AUS_DEM_KONZEPT: list[tuple[float, float]] = [
        (0.10, 0.024), (0.20, 0.095), (0.30, 0.206),
        (0.50, 0.500), (0.70, 0.794), (0.80, 0.905), (0.90, 0.976),
    ]

    def test_die_kurve_trifft_die_werte_des_konzepts(self) -> None:
        for eingang, erwartet in self.AUS_DEM_KONZEPT:
            with self.subTest(eingang=eingang):
                self.assertAlmostEqual(
                    ausschlag_absolut_berechnen(eingang), erwartet, places=3,
                    msg=f"Eingang {eingang} soll {erwartet} ergeben — "
                        f"pruefe den Exponenten gegen §7.2",
                )

    def test_sie_ist_punktsymmetrisch_um_0_5(self) -> None:
        """Die S-Form, die eine Intensitaetsgroesse braucht."""
        self.assertAlmostEqual(ausschlag_absolut_berechnen(0.5), 0.5, places=6)
        for d in (0.1, 0.2, 0.3):
            unten = ausschlag_absolut_berechnen(0.5 - d)
            oben  = ausschlag_absolut_berechnen(0.5 + d)
            self.assertAlmostEqual(unten + oben, 1.0, places=6)

    def test_ein_eingang_ausserhalb_der_skala_wird_abgelehnt(self) -> None:
        """EVA: Ein Wert ueber 1 hiesse, die liefernde Groesse hat eine andere Skala."""
        for schlecht in (-0.01, 1.01, 2.0):
            with self.subTest(wert=schlecht), self.assertRaises(ValueError):
                ausschlag_absolut_berechnen(schlecht)


class DasTorTraegtDieVolleLastTest(unittest.TestCase):
    """Beide Bedingungen muessen erfuellt sein, und der Grund wird genannt."""

    def test_hohe_salienz_allein_genuegt_nicht(self) -> None:
        """Salienz trennt schlecht: 43 % des Bestands liegen ueber 0,90."""
        durch, grund = tor_urteil(salienz=0.99, ausschlag=0.10)
        self.assertFalse(durch)
        self.assertIn("ausschlag", grund)

    def test_hoher_ausschlag_allein_genuegt_nicht(self) -> None:
        durch, grund = tor_urteil(salienz=0.10, ausschlag=0.99)
        self.assertFalse(durch)
        self.assertIn("salienz", grund)

    def test_beide_zusammen_kommen_durch(self) -> None:
        durch, grund = tor_urteil(salienz=0.95, ausschlag=0.85)
        self.assertTrue(durch, grund)

    def test_der_grund_nennt_den_wert_nicht_nur_das_feld(self) -> None:
        """11_EVA: »Key fehlt« ist unbrauchbar, der Wert gehoert dazu."""
        _, grund = tor_urteil(salienz=0.42, ausschlag=0.99)
        self.assertIn("0.42", grund)


class DerFadenWirdGeschriebenTest(unittest.TestCase):
    """Gegen eine echte Zeile, nicht gegen eine Attrappe."""

    USER: str = "test-praegung-user"
    CHAR: str = "test-praegung-char"

    def tearDown(self) -> None:
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM praegung_faden WHERE user_id = %s", (self.USER,))

    def test_der_faden_startet_bei_seinem_ursprungswert(self) -> None:
        """`ausschlag_aktuell` gleich `ausschlag_absolut` — die Faltung faengt dort an."""
        faden_id = faden_anlegen(
            POSTGRES_URL, user_id=self.USER, character_id=self.CHAR,
            emotion="begeisterung", ausschlag_eingang=0.80, turn_id="t-praegung-1",
        )
        self.assertIsNotNone(faden_id, "Faden nicht angelegt")
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT ausschlag_eingang, ausschlag_absolut, ausschlag_aktuell, "
                "ausgang, herkunft FROM praegung_faden WHERE id = %s", (faden_id,),
            )
            eingang, absolut, aktuell, ausgang, herkunft = cur.fetchone()
        self.assertAlmostEqual(eingang, 0.80, places=6)
        self.assertAlmostEqual(absolut, 0.905, places=3, msg="Formkurve nicht angewandt")
        self.assertAlmostEqual(aktuell, absolut, places=6)
        self.assertEqual(ausgang, "offen", "Der Ausgang faellt spaeter, nicht live")
        self.assertEqual(herkunft, "erlebt")

    def test_eine_unbekannte_herkunft_wird_abgelehnt(self) -> None:
        """Zugehoerigkeit zum Kanon — an der Herkunft haengt die Rueckwirkung."""
        self.assertIsNone(faden_anlegen(
            POSTGRES_URL, user_id=self.USER, character_id=self.CHAR,
            emotion="freude", ausschlag_eingang=0.9, herkunft="erfunden",
        ))

    def test_ein_neutraler_sektor_wird_abgelehnt(self) -> None:
        """Ohne besetzten Sektor traegt der Faden kein Histogramm."""
        self.assertIsNone(faden_anlegen(
            POSTGRES_URL, user_id=self.USER, character_id=self.CHAR,
            emotion="neutral", ausschlag_eingang=0.9,
        ))

    def test_ein_halbes_paar_wird_abgelehnt(self) -> None:
        """Eine Praegung ist Novas Eigenschaft gegenueber jemandem, nicht global."""
        self.assertIsNone(faden_anlegen(
            POSTGRES_URL, user_id=self.USER, character_id="",
            emotion="freude", ausschlag_eingang=0.9,
        ))

    def test_die_beruehrung_haengt_am_faden(self) -> None:
        """Der Rohstoff der Faltung — eine Zeile je Reaktivierung."""
        faden_id = faden_anlegen(
            POSTGRES_URL, user_id=self.USER, character_id=self.CHAR,
            emotion="neugier", ausschlag_eingang=0.75,
        )
        self.assertTrue(beruehrung_anlegen(POSTGRES_URL, faden_id, "lzg:6123"))
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT quelle FROM praegung_beruehrung WHERE faden_id = %s", (faden_id,),
            )
            self.assertEqual(cur.fetchone()[0], "lzg:6123")

    def test_eine_beruehrung_ohne_quelle_wird_abgelehnt(self) -> None:
        """Sonst waere nicht zu sagen, was den Faden aufgefrischt hat."""
        faden_id = faden_anlegen(
            POSTGRES_URL, user_id=self.USER, character_id=self.CHAR,
            emotion="freude", ausschlag_eingang=0.8,
        )
        self.assertFalse(beruehrung_anlegen(POSTGRES_URL, faden_id, ""))


class DasTorHaengtImGraphenTest(unittest.TestCase):
    """Ein Node, den niemand aufruft, besteht jeden Unit-Test.

    Dieselbe Lehre wie bei der emotionalen Gravitation: Dort stand der Aufruf
    bis Chat 113 an einer Stelle, an der er nie greifen konnte — 851 Logzeilen,
    null Anwendungen.
    """

    def test_das_tor_liegt_hinter_der_salienz(self) -> None:
        """Frueher gaebe es die Salienz noch nicht — eine der zwei Bedingungen."""
        from graph import character_graph as modul
        quelle: str = open(modul.__file__, encoding="utf-8").read()
        self.assertIn('graph.add_edge("salience",            "praegung")', quelle)

    def test_das_tor_liegt_vor_dem_dispatcher(self) -> None:
        """Danach ist der Turn vorbei."""
        from graph import character_graph as modul
        quelle: str = open(modul.__file__, encoding="utf-8").read()
        self.assertIn('graph.add_edge("praegung",            "dispatcher")', quelle)

    def test_die_alte_kante_steht_nicht_mehr_daneben(self) -> None:
        """Gegenprobe: Bliebe sie, liefe der Turn am Tor vorbei."""
        from graph import character_graph as modul
        quelle: str = open(modul.__file__, encoding="utf-8").read()
        self.assertNotIn('graph.add_edge("salience",            "dispatcher")', quelle)


class DasTorMeldetFehlendeGroessenTest(unittest.TestCase):
    """Kein stiller Ausfall: Fehlt eine Torgroesse, wird es laut."""

    @staticmethod
    def _mit_salienz(wert: float, emotion: str = "neugierig") -> list[dict]:
        """Ein `pending_writes`-Eintrag, wie ihn der Salienz-Node hinterlaesst."""
        return [{"daten": {"salienz_obj": {"salienz": wert, "emotion": emotion}}}]

    def test_ohne_salienz_faellt_das_tor_aus_und_meldet(self) -> None:
        from graph.nodes.praegung import praegung_pruefen
        zustand = {"user_id": "u", "character_id": "c", "pending_writes": [],
                   "nova_emotions_verlauf": [{"emotion": "freude", "gewicht": 0.9}]}
        with self.assertLogs("ki_server.praegung_node", level="ERROR") as protokoll:
            praegung_pruefen(zustand)
        self.assertIn("keine effektive Salienz", "".join(protokoll.output))

    def test_ohne_verlauf_faellt_das_tor_aus_und_meldet(self) -> None:
        from graph.nodes.praegung import praegung_pruefen
        zustand = {"user_id": "u", "character_id": "c",
                   "pending_writes": self._mit_salienz(0.95),
                   "nova_emotions_verlauf": []}
        with self.assertLogs("ki_server.praegung_node", level="ERROR") as protokoll:
            praegung_pruefen(zustand)
        self.assertIn("leerer nova_emotions_verlauf", "".join(protokoll.output))

    def test_die_effektive_salienz_wird_gelesen_nicht_salienz_human(self) -> None:
        """`[gemessen]` 31.08.2026: Die Verwechslung kostete sieben Betriebsturns.

        `salienz_human` steht im Mittel bei 0,41 und erreicht in **3 von 2757**
        Laeufen die Torschwelle; die effektive liegt bei 0,80 und erreicht sie in
        1188. Ein Tor auf der falschen Groesse laesst nie durch — die
        Spiegelklasse von EMGRAV-SCHWELLE-TOT.
        """
        from graph.nodes.praegung import _staerkstes_segment
        zustand = {"salienz_human": 0.41, "pending_writes": self._mit_salienz(0.97)}
        self.assertAlmostEqual(
            float(_staerkstes_segment(zustand)["salienz"]), 0.97, places=6,
            msg="Das Tor liest salienz_human statt der effektiven Salienz",
        )

    def test_das_maximum_der_segmente_entscheidet(self) -> None:
        """Ein einschneidender Satz neben drei belanglosen bleibt einschneidend."""
        from graph.nodes.praegung import _staerkstes_segment
        zustand = {"pending_writes": [
            {"daten": {"salienz_obj": {"salienz": 0.20, "emotion": "freude"}}},
            {"daten": {"salienz_obj": {"salienz": 0.95, "emotion": "traurigkeit"}}},
            {"daten": {"salienz_obj": {"salienz": 0.30, "emotion": "aerger"}}},
        ]}
        bestes = _staerkstes_segment(zustand)
        self.assertAlmostEqual(float(bestes["salienz"]), 0.95, places=6)
        self.assertEqual(
            bestes["emotion"], "traurigkeit",
            "Salienz und Emotion muessen aus demselben Segment kommen — sonst "
            "traegt der Faden die Wucht des einen und den Sektor eines anderen",
        )

    def test_der_faden_traegt_die_turn_emotion_nicht_die_des_verlaufs(self) -> None:
        """`[gemessen]` 31.08.2026: Der Verlauf hinkt dem Reiz einen Turn nach.

        Ueber acht Sektoren an einem frischen Paar erschien die perzipierte
        `zufriedenheit` erst einen Turn spaeter als Fuehrung im Verlauf, die
        `traurigkeit` ebenso. Ein Faden aus dem Verlauf traegt damit den Sektor
        des **vorigen** Turns — und darauf bauen Sektor-Histogramm und die acht
        Verfallsfaktoren.
        """
        from graph.nodes.praegung import _staerkstes_segment
        zustand = {
            "pending_writes": self._mit_salienz(0.95, emotion="frustration"),
            "nova_emotions_verlauf": [
                {"emotion": "traurigkeit", "gewicht": 0.9},   # Fuehrung, aelter
                {"emotion": "frustration", "gewicht": 0.6},   # der Turn selbst
            ],
        }
        self.assertEqual(_staerkstes_segment(zustand)["emotion"], "frustration")

    def test_der_ausschlag_gehoert_zur_emotion_des_fadens(self) -> None:
        """Sonst misst er eine Emotion, die der Faden gar nicht traegt."""
        from graph.nodes.praegung import _ausschlag_der_emotion
        verlauf = [{"emotion": "traurigkeit", "gewicht": 0.9},
                   {"emotion": "frustration", "gewicht": 0.6}]
        self.assertAlmostEqual(_ausschlag_der_emotion(verlauf, "frustration"), 0.6)
        self.assertAlmostEqual(_ausschlag_der_emotion(verlauf, "unbekannt"), 0.0)


class DerNodeSchreibtDieTurnEmotionInDenFadenTest(unittest.TestCase):
    """Nicht die Funktion, sondern ihre Verwendung.

    Ein Zeuge auf `_staerkstes_segment` allein bleibt gruen, wenn der Node
    danach doch `verlauf[0]` liest — gemessen am 31.08.2026: Beide Gegenproben
    liefen gruen durch, waehrend der Node die falsche Groesse nahm.
    """

    USER: str = "test-praegung-node"
    CHAR: str = "test-praegung-char"

    def tearDown(self) -> None:
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM praegung_faden WHERE user_id = %s", (self.USER,))

    def test_der_faden_traegt_den_sektor_des_turns(self) -> None:
        """Der Verlauf fuehrt mit `traurigkeit`, der Turn perzipiert `frustration`."""
        from graph.nodes.praegung import praegung_pruefen
        praegung_pruefen({
            "user_id": self.USER, "character_id": self.CHAR,
            "turn_id": "t-node-1",
            "pending_writes": [
                {"daten": {"salienz_obj": {"salienz": 0.95, "emotion": "frustration"}}},
            ],
            "nova_emotions_verlauf": [
                {"emotion": "traurigkeit", "gewicht": 0.90},
                {"emotion": "frustration", "gewicht": 0.85},
            ],
        })
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT emotion, ausschlag_eingang FROM praegung_faden "
                "WHERE user_id = %s", (self.USER,),
            )
            zeile = cur.fetchone()
        self.assertIsNotNone(zeile, "Kein Faden angelegt — Tor haette durchlassen muessen")
        emotion, ausschlag = zeile
        self.assertEqual(
            emotion, "frustration",
            "Der Faden traegt die Fuehrung des Verlaufs statt der Turn-Emotion — "
            "damit den Sektor des vorigen Turns",
        )
        self.assertAlmostEqual(
            ausschlag, 0.85, places=6,
            msg="Der Ausschlag gehoert zur Emotion des Fadens, nicht zur Fuehrung",
        )
