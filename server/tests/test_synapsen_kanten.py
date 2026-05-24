"""
Unit-Tests fuer die Synapsen-Kanten-Mathematik (Synapsen P4, Abnahme §13.6 #3).

Reproduziert die drei durchgerechneten Beispiele aus Konzept §7.5 und prueft
Zusatzfaelle: Themen-Tiefe (max straft Breite), Timeline-Praezisions-Ungleichheit
(harte Filter-Regel), Embedding-Schwellwert.
"""

import unittest

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


class TestKantenStaerke(unittest.TestCase):
    """Die drei Konzept-Beispiele aus §7.5 (Toleranz 0.005 wegen Konzept-Rundung)."""

    def test_beispiel_1_timeline_only(self):
        tiefe_timeline = (21 - 4) / 21  # Praezision Tag, Distanz 4, Toleranz 21
        roh_ab, roh_ba = kanten_staerke_berechnen(0.7, 5.0, {SCHICHT_TIMELINE: tiefe_timeline})
        self.assertAlmostEqual(roh_ab, 0.899, delta=0.005)
        self.assertAlmostEqual(roh_ba, 1.259, delta=0.005)

    def test_beispiel_2_timeline_und_embedding(self):
        tiefe_timeline = (21 - 4) / 21
        tiefe_embedding = (0.90 - 0.85) / (1.0 - 0.85)
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
        self.assertAlmostEqual(embedding_tiefe(0.85), 0.0, delta=1e-9)   # am Schwellwert
        self.assertAlmostEqual(embedding_tiefe(1.0), 1.0, delta=1e-9)    # maximal
        self.assertAlmostEqual(embedding_tiefe(0.925), 0.5, delta=1e-9)  # Mitte

    def test_timeline_praezisions_ungleichheit_sperrt(self):
        from datetime import datetime, timezone
        t = datetime(2026, 5, 1, tzinfo=timezone.utc)
        tiefe, distanz = timeline_tiefe("minute", "day", t, t)
        self.assertEqual(tiefe, 0.0)
        self.assertIsNone(distanz)

    def test_timeline_ausserhalb_toleranz_sperrt(self):
        from datetime import datetime, timezone
        a = datetime(2026, 1, 1, tzinfo=timezone.utc)
        b = datetime(2026, 3, 1, tzinfo=timezone.utc)  # ~59 Tage, > 21 (Tag)
        tiefe, distanz = timeline_tiefe("day", "day", a, b)
        self.assertEqual(tiefe, 0.0)
        self.assertIsNone(distanz)


if __name__ == "__main__":
    unittest.main()
