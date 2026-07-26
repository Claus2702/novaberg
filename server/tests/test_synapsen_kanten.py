"""
Unit-Tests fuer die Synapsen-Kanten-Mathematik (Synapsen P4, Abnahme §13.6 #3).

Reproduziert die drei durchgerechneten Beispiele aus Konzept §7.5 und prueft
Zusatzfaelle: Themen-Tiefe (max straft Breite), Timeline-Praezisions-Ungleichheit
(harte Filter-Regel), Embedding-Schwellwert.
"""

import unittest
from datetime import datetime, timedelta, timezone

from config import LZG_EMBEDDING_SCHWELLWERT, LZG_TIMELINE_TOLERANZ_TAG
from memory.lzg_kanten import (
    kanten_staerke_berechnen,
    themen_tiefe,
    embedding_tiefe,
    timeline_tiefe,
    SCHICHT_ENTITAET,
    SCHICHT_EMBEDDING,
    SCHICHT_THEMEN,
    SCHICHT_TIMELINE,
)

# Konzept §7.5 rechnet seine drei Beispiele mit den Konstanten durch, die zur
# Dokumentationszeit galten. Sie stehen hier bewusst als Fixtures und NICHT aus
# config: zoege man sie aus config, waeren die Erwartungswerte unten nicht mehr
# die des Konzepts, und der Test pruefte nichts Dokumentiertes mehr.
#
# Der Live-Schwellwert ist seit der Embedding-Migration (Chat 107) ein anderer
# — LZG_EMBEDDING_SCHWELLWERT steht auf 0.55. Genau deshalb die Trennung: Tests,
# die eine ueber config definierte FUNKTION pruefen, lesen aus config (siehe
# TestTiefeFaktoren); Tests, die ein dokumentiertes Rechenbeispiel reproduzieren,
# tragen die Zahlen des Beispiels.
KONZEPT_TIMELINE_TOLERANZ_TAG: int   = 21
KONZEPT_EMBEDDING_SCHWELLWERT: float = 0.85


class TestKantenStaerke(unittest.TestCase):
    """Die drei Konzept-Beispiele aus §7.5 (Toleranz 0.005 wegen Konzept-Rundung)."""

    def test_beispiel_1_timeline_only(self):
        # Praezision Tag, Distanz 4, Toleranz 21 (Konzept-Fixture, s.o.)
        tiefe_timeline = (
            (KONZEPT_TIMELINE_TOLERANZ_TAG - 4) / KONZEPT_TIMELINE_TOLERANZ_TAG
        )
        roh_ab, roh_ba = kanten_staerke_berechnen(0.7, 5.0, {SCHICHT_TIMELINE: tiefe_timeline})
        self.assertAlmostEqual(roh_ab, 0.899, delta=0.005)
        self.assertAlmostEqual(roh_ba, 1.259, delta=0.005)

    def test_beispiel_2_timeline_und_embedding(self):
        tiefe_timeline = (
            (KONZEPT_TIMELINE_TOLERANZ_TAG - 4) / KONZEPT_TIMELINE_TOLERANZ_TAG
        )
        tiefe_embedding = (
            (0.90 - KONZEPT_EMBEDDING_SCHWELLWERT) / (1.0 - KONZEPT_EMBEDDING_SCHWELLWERT)
        )
        roh_ab, roh_ba = kanten_staerke_berechnen(
            0.7, 5.0, {SCHICHT_TIMELINE: tiefe_timeline, SCHICHT_EMBEDDING: tiefe_embedding}
        )
        # Embedding gewinnt (Faktor 0.8 > Timeline 0.4), Bonus 0.1 fuer 2 Schichten
        self.assertAlmostEqual(roh_ab, 1.169, delta=0.005)
        self.assertAlmostEqual(roh_ba, 1.466, delta=0.005)

    def test_beispiel_3_entitaet_only(self):
        roh_ab, roh_ba = kanten_staerke_berechnen(0.7, 5.0, {SCHICHT_ENTITAET: 1.0})
        self.assertAlmostEqual(roh_ab, 2.609, delta=0.005)
        self.assertAlmostEqual(roh_ba, 3.723, delta=0.005)

    def test_symmetrie_gleicher_knoten(self):
        # Bei gleichen Anker-Staerken kollabiert die Asymmetrie: A->B == B->A.
        roh_ab, roh_ba = kanten_staerke_berechnen(3.0, 3.0, {SCHICHT_ENTITAET: 1.0})
        self.assertAlmostEqual(roh_ab, roh_ba, delta=1e-9)

    def test_richtung_unabhaengig_von_argument_reihenfolge(self):
        # Egal ob der neue Knoten staerker oder schwaecher ist: die A->B-Kante
        # muss konsistent bleiben, wenn man die Argumente vertauscht.
        ab1, ba1 = kanten_staerke_berechnen(0.7, 5.0, {SCHICHT_ENTITAET: 1.0})
        ab2, ba2 = kanten_staerke_berechnen(5.0, 0.7, {SCHICHT_ENTITAET: 1.0})
        # (0.7,5.0) A->B entspricht (5.0,0.7) B->A
        self.assertAlmostEqual(ab1, ba2, delta=1e-9)
        self.assertAlmostEqual(ba1, ab2, delta=1e-9)


class TestTiefeFaktoren(unittest.TestCase):

    def test_themen_max_straft_breite(self):
        # Schmaler Knoten (1 Thema) vs. breiter (10 Themen), 1 geteilt -> 1/10
        tiefe, geteilt = themen_tiefe(["Geburtstag"], ["Geburtstag"] + [f"t{i}" for i in range(9)])
        self.assertEqual(geteilt, ["Geburtstag"])
        self.assertAlmostEqual(tiefe, 0.1, delta=1e-9)

    def test_themen_kein_overlap(self):
        tiefe, geteilt = themen_tiefe(["A"], ["B"])
        self.assertEqual(geteilt, [])
        self.assertEqual(tiefe, 0.0)

    def test_embedding_tiefe_linear(self):
        # embedding_tiefe ist ueber LZG_EMBEDDING_SCHWELLWERT definiert. Ein
        # hartcodierter Schwellwert misst nur, was zur Schreibzeit der Zeile
        # galt — er wird beim naechsten Tuning still falsch oder dauerhaft rot.
        schwelle: float = LZG_EMBEDDING_SCHWELLWERT
        mitte:    float = schwelle + (1.0 - schwelle) / 2

        self.assertAlmostEqual(embedding_tiefe(schwelle), 0.0, delta=1e-9)  # am Schwellwert
        self.assertAlmostEqual(embedding_tiefe(1.0), 1.0, delta=1e-9)       # maximal
        self.assertAlmostEqual(embedding_tiefe(mitte), 0.5, delta=1e-9)     # Mitte

    def test_embedding_tiefe_unter_schwellwert_klemmt_auf_null(self):
        # Unterhalb des Schwellwerts greift die Schicht nicht.
        unter: float = LZG_EMBEDDING_SCHWELLWERT / 2
        self.assertEqual(embedding_tiefe(unter), 0.0)

    def test_timeline_praezisions_ungleichheit_sperrt(self):
        t = datetime(2026, 5, 1, tzinfo=timezone.utc)
        tiefe, distanz = timeline_tiefe("minute", "day", t, t)
        self.assertEqual(tiefe, 0.0)
        self.assertIsNone(distanz)

    def test_timeline_ausserhalb_toleranz_sperrt(self):
        # Abstand aus config abgeleitet: bei angehobener Toleranz waere ein
        # fester Abstand irgendwann INNERHALB und der Test still wertlos.
        a = datetime(2026, 1, 1, tzinfo=timezone.utc)
        b = a + timedelta(days=LZG_TIMELINE_TOLERANZ_TAG + 1)
        tiefe, distanz = timeline_tiefe("day", "day", a, b)
        self.assertEqual(tiefe, 0.0)
        self.assertIsNone(distanz)

    def test_timeline_innerhalb_toleranz_traegt(self):
        # Positiver Zwilling zum Sperr-Test: sonst bliebe unbemerkt, wenn
        # timeline_tiefe fuer JEDEN Abstand 0.0 lieferte.
        a = datetime(2026, 1, 1, tzinfo=timezone.utc)
        b = a + timedelta(days=1)
        tiefe, distanz = timeline_tiefe("day", "day", a, b)
        self.assertGreater(tiefe, 0.0)
        self.assertEqual(distanz, 1)


if __name__ == "__main__":
    unittest.main()
