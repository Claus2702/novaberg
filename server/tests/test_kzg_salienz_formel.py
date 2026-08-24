"""Tests fuer die KZG-Salienz als abgeleiteter Wert (Bauteil 1).

Ziel (novaberg-kzg-salienz_k.md §11): Ein Eintrag mit der Bewertung 0.5
erreicht die Promotionsschwelle nach genau sieben thematischen Verstaerkungen —
nach sechs noch nicht. Ein Eintrag mit 0.7 erreicht sie beim Anlegen. Kein
Eintrag traegt je einen Wert ueber 1.0.

Hintergrund: Bis Chat 113 war die Salienz ein Akkumulator mit Cap 10.0 — ein
Wertebereich, den die Eingangsgroesse nie hatte. Gemessen am 28.07.2026 standen
71 von 188 Eintraegen (38 %) ueber 1.0, der hoechste bei 5.636 nach sechzehn
Verstaerkungen; keines der drei Tore griff noch.

Die Erwartungswerte sind von Hand aus der Konzeptformel gerechnet und stehen
hier als Literale. Sie werden NICHT aus KZG_SALIENZ_BOOST, _CAP oder _EXP
abgeleitet: Rechnete der Test die Formel mit denselben Konstanten nach, aus
denen der Code sein Ergebnis bildet, liefen beide Seiten des Vergleichs auf
dieselbe Eingabe zurueck und der Vergleich pruefte nichts.

    salienz(0.5, 7 Verstaerkungen) = sin((0.5 + 7 x 0.03) x pi/2) ** 0.5
                                   = sin(0.71 x pi/2) ** 0.5
                                   = 0.89744 ** 0.5 = 0.94733  >= 0.9439

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import KZG_SALIENZ_HIGH, KZG_SALIENZ_MID, KZG_SALIENZ_MINIMUM
from memory.kzg import salienz_berechnen

KZG_LOGGER: str = "ki_server.memory.kzg"


class TestSalienzTore(unittest.TestCase):
    """Der Weg zum Tor — die Zusicherung aus §6 des Konzepts."""

    def test_bewertung_050_erreicht_das_tor_nach_sieben_verstaerkungen(self) -> None:
        # haeufigkeit = 1 + Verstaerkungen
        self.assertGreaterEqual(salienz_berechnen(0.5, 8), KZG_SALIENZ_HIGH)

    def test_bewertung_050_erreicht_es_nach_sechs_noch_nicht(self) -> None:
        self.assertLess(salienz_berechnen(0.5, 7), KZG_SALIENZ_HIGH)

    def test_bewertung_070_erreicht_das_tor_beim_anlegen(self) -> None:
        self.assertGreaterEqual(salienz_berechnen(0.7, 1), KZG_SALIENZ_HIGH)

    def test_bewertung_030_liegt_genau_auf_dem_minimum(self) -> None:
        """Die drei Tore sind Bilder der alten Rohwerte unter der neuen Kurve."""
        # **Gegen die Konstanten, nicht gegen ihre Zahlen von heute** — die
        # drei Marken sind Bilder der Rohwerte 0.3 / 0.5 / 0.7 durch dieselbe
        # Kurve, die auch die Formel benutzt. Bis zum 24.08.2026 standen hier
        # die Literale des damaligen Exponenten 0.5; mit dem Wechsel auf 1.1
        # wurden sie falsch, obwohl die Zusicherung unveraendert gilt.
        self.assertAlmostEqual(salienz_berechnen(0.3, 1), KZG_SALIENZ_MINIMUM, places=4)
        self.assertAlmostEqual(salienz_berechnen(0.5, 1), KZG_SALIENZ_MID,     places=4)
        self.assertAlmostEqual(salienz_berechnen(0.7, 1), KZG_SALIENZ_HIGH,    places=4)

    def test_die_tore_stehen_auf_derselben_skala_wie_die_werte(self) -> None:
        """Gegen KZG-SALIENZ-KONSUMENTEN-DISSENS: eine Skala, nicht zwei."""
        self.assertAlmostEqual(salienz_berechnen(0.3, 1), KZG_SALIENZ_MINIMUM, places=4)
        self.assertAlmostEqual(salienz_berechnen(0.5, 1), KZG_SALIENZ_MID, places=4)
        self.assertAlmostEqual(salienz_berechnen(0.7, 1), KZG_SALIENZ_HIGH, places=4)

    def test_wer_das_tor_genau_trifft_geht_hindurch(self) -> None:
        """Die Tore sind mit `>=` geprueft und muessen deshalb ABGERUNDET sein.

        Gemessen am Live-Turn vom 28.07.2026, 09:27 UTC: Eine Bewertung von
        exakt 0.30 wurde abgelehnt, weil die auf 0.6738 aufgerundete Konstante
        ueber ihrem eigenen Rohwert 0.6737882 lag. §6 des Konzepts fuehrt 0.30
        als gueltigen Weg mit vierzehn Verstaerkungen — sie muss durchkommen.
        """
        self.assertGreaterEqual(salienz_berechnen(0.3, 1), KZG_SALIENZ_MINIMUM)
        self.assertGreaterEqual(salienz_berechnen(0.5, 1), KZG_SALIENZ_MID)
        self.assertGreaterEqual(salienz_berechnen(0.7, 1), KZG_SALIENZ_HIGH)

    def test_knapp_darunter_wird_abgelehnt(self) -> None:
        """Positiver Zwilling: Das Tor ist eine Grenze, kein Durchlass.

        Ohne diesen Fall bestuende die Zusicherung oben auch dann, wenn die
        Tore auf 0.0 stuenden.
        """
        self.assertLess(salienz_berechnen(0.29, 1), KZG_SALIENZ_MINIMUM)
        self.assertLess(salienz_berechnen(0.49, 1), KZG_SALIENZ_MID)
        self.assertLess(salienz_berechnen(0.69, 1), KZG_SALIENZ_HIGH)


class TestSalienzDeckel(unittest.TestCase):
    """Kein Eintrag traegt je einen Wert ueber 1.0."""

    def test_hundert_verstaerkungen_ergeben_exakt_eins(self) -> None:
        self.assertEqual(salienz_berechnen(1.0, 101), 1.0)

    def test_der_hoechste_gemessene_altwert_bleibt_unter_dem_deckel(self) -> None:
        """Der Eintrag, der unter der alten Bauart auf 5.636 stand.

        Bewertung 0.6 (Migrationswert) bei sechzehn Verstaerkungen: der Anker
        laeuft mit 1.05 ueber den Deckel, das Ergebnis nicht.
        """
        self.assertLessEqual(salienz_berechnen(0.6, 17), 1.0)

    def test_zwischenwert_liegt_echt_zwischen_null_und_eins(self) -> None:
        """Positiver Zwilling zur Deckel-Zusicherung.

        Ohne ihn bestuende die Zusicherung oben auch dann, wenn die Funktion
        stumpf 1.0 zurueckgaebe oder alles auf den Deckel zoege.
        """
        wert: float = salienz_berechnen(0.5, 1)
        self.assertGreater(wert, 0.0)
        self.assertLess(wert, 1.0)
        self.assertAlmostEqual(wert, KZG_SALIENZ_MID, places=4)


class TestSalienzBauart(unittest.TestCase):
    """Die Bauart-Zusicherungen der Konvention fuer abgeleitete Werte."""

    def test_zweimal_rechnen_aendert_nichts(self) -> None:
        """Regel (4): idempotent. Der Akkumulator war es nicht."""
        erst:  float = salienz_berechnen(0.42, 5)
        zweit: float = salienz_berechnen(0.42, 5)
        self.assertEqual(erst, zweit)

    def test_reihenfolge_spielt_keine_rolle(self) -> None:
        """Regel (2)/(3): nachrechenbar ohne Kenntnis des bisherigen Werts.

        Unter der alten Bauart war das Ergebnis pfadabhaengig — derselbe
        Eintrag konnte je nach Reihenfolge der Verstaerkungen anders enden.
        """
        direkt:      float = salienz_berechnen(0.5, 4)
        schrittweise: float = salienz_berechnen(0.5, 1)
        for haeufigkeit in (2, 3, 4):
            schrittweise = salienz_berechnen(0.5, haeufigkeit)
        self.assertEqual(direkt, schrittweise)

    def test_boost_greift_am_anker_vor_der_kurve(self) -> None:
        """§3: Ein Zuwachs auf den gekruemmten Wert bedeutete unten anderes als oben.

        Unter der Kurve wachsen gleiche Anker-Zuwaechse zu ungleichen
        Ergebnis-Zuwaechsen — unten steil, oben flach. Waere der Boost hinter
        der Kurve addiert, waeren beide Differenzen gleich.
        """
        unten: float = salienz_berechnen(0.3, 2) - salienz_berechnen(0.3, 1)
        oben:  float = salienz_berechnen(0.9, 2) - salienz_berechnen(0.9, 1)
        self.assertGreater(unten, oben)


class TestSalienzFehlerpfade(unittest.TestCase):
    """Vorbedingungen melden sich laut, statt still zu rechnen."""

    def test_eingang_ueber_eins_meldet_fehler_und_klemmt(self) -> None:
        with self.assertLogs(KZG_LOGGER, level="ERROR") as protokoll:
            wert: float = salienz_berechnen(5.636, 1)
        self.assertEqual(wert, 1.0)
        self.assertIn("ausserhalb", "\n".join(protokoll.output))

    def test_haeufigkeit_null_meldet_fehler(self) -> None:
        with self.assertLogs(KZG_LOGGER, level="ERROR") as protokoll:
            wert: float = salienz_berechnen(0.5, 0)
        self.assertAlmostEqual(wert, KZG_SALIENZ_MID, places=4)
        self.assertIn("haeufigkeit=0", "\n".join(protokoll.output))


if __name__ == "__main__":
    unittest.main()
