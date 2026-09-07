"""Tests: Die Faszination macht `wissbegier` themengebunden.

Ziel: Derselbe Charakter in derselben Landschaft fragt bei einem Thema, an das
Nova gebunden ist, anders als bei einem fremden — und gar nicht anders, wenn
ueber die Bindung nichts bekannt ist.

Zeugen dieser Datei:
  * **Die drei Stuetzstellen der Abbildung stehen als Literale** und sind aus
    den Konstanten gerechnet, nicht aus einem Lauf der Funktion.
  * **Die Gegenprobe gegen Mitmodulation steht neben jeder Wirkungspruefung.**
    Ein Faktor, der versehentlich alle zwoelf Speichen traefe, machte den
    Wirkungszeugen ebenfalls gruen — er ist allein nicht aussagekraeftig.
  * **Die Eingaben erreichen den Eingriff.** Geprueft wird in `werkstatt`, wo
    `fragen` eine Neigung mit Grundwert 0.45 ist. In einer Grenzzelle mit
    Grundwert 0.00 bliebe das Ergebnis unter jedem Faktor null, und der Zeuge
    waere gruen per Konstruktion.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import (
    HALTUNG_FASZINATION_MAX,
    HALTUNG_FASZINATION_MIN,
    HALTUNG_FASZINATION_NEUTRAL,
)
from ei.haltung import (
    FASZINATION_SPEICHE,
    SPEICHEN_BEITRAG,
    faszinations_faktor,
    haltung_berechnen,
)

# Ein Rad mit genau zwei Speichen: der modulierten und einer Kontrollspeiche,
# die auf dieselben Groessen traegt. `aufmerksamkeit` traegt `fragen` und
# `naehe` — damit ist eine Mitmodulation an `naehe` unmittelbar sichtbar.
RAD: dict[str, float] = {"wissbegier": 0.80, "aufmerksamkeit": 0.60}
LANDSCHAFT: str = "werkstatt"


class FaszinationsFaktor(unittest.TestCase):
    """Die Naht zwischen Faszination [0,1] und Haltungsbeitrag."""

    def test_der_neutrale_punkt_ergibt_exakt_eins(self):
        """Am neutralen Punkt aendert die Faszination nichts."""
        self.assertAlmostEqual(
            faszinations_faktor(HALTUNG_FASZINATION_NEUTRAL), 1.0, places=10
        )

    def test_null_ergibt_das_minimum(self):
        """Keine Bindung an das Thema daempft bis auf das Minimum."""
        self.assertAlmostEqual(
            faszinations_faktor(0.0), HALTUNG_FASZINATION_MIN, places=10
        )

    def test_eins_ergibt_das_maximum(self):
        """Volle Bindung hebt bis auf das Maximum."""
        self.assertAlmostEqual(
            faszinations_faktor(1.0), HALTUNG_FASZINATION_MAX, places=10
        )

    def test_fehlende_faszination_wirkt_neutral(self):
        """`None` heisst 'keine Bindung bekannt' und darf weder heben noch senken.

        **Das ist der haeufigste Fall und nicht der Randfall.** Gemessen am
        07.09.2026 tragen 38 von 95 je Turn gelesenen Knoten ein Profil; ein
        Turn ohne profilierten Traeger ist damit die Mehrheit.
        """
        self.assertEqual(faszinations_faktor(None), 1.0)

    def test_die_abbildung_ist_monoton(self):
        """Mehr Faszination ergibt nie einen kleineren Faktor."""
        vorher: float = 0.0
        for schritt in range(0, 101):
            faktor: float = faszinations_faktor(schritt / 100.0)
            self.assertGreaterEqual(faktor, vorher)
            vorher = faktor

    def test_werte_ausserhalb_werden_geklemmt_nicht_durchgereicht(self):
        """Ein Wert jenseits der Skala endet am Rand, nicht im Ergebnis."""
        self.assertAlmostEqual(
            faszinations_faktor(1.5), HALTUNG_FASZINATION_MAX, places=10
        )
        self.assertAlmostEqual(
            faszinations_faktor(-0.5), HALTUNG_FASZINATION_MIN, places=10
        )

    def test_ein_wahrheitswert_ist_keine_faszination(self):
        """`True` ist in Python ein `int` und waere sonst der volle Ausschlag.

        Die bekannte Klasse — `isinstance(True, (int, float))` ist wahr,
        und `True` landet als 1.0 in der Rechnung: auf dem Erfolgspfad, in der
        Spanne, ohne eine Zeile im Log.
        """
        self.assertEqual(faszinations_faktor(True), 1.0)
        self.assertEqual(faszinations_faktor(False), 1.0)


    def test_der_neutrale_punkt_liegt_in_der_gemessenen_spanne(self):
        """Ein Modulator neben der Verteilung verschiebt, statt zu modulieren.

        **Die Zahlen sind Literale aus einer Messung**, nicht aus der
        Konfiguration: `[gemessen 07.09.2026]` ueber die letzten 25 echten
        Turns liefert `faszination_der_gelesenen` in 15 einen Wert, und der
        liegt zwischen 0.2704 und 0.5177.

        Die uebrigen Zeugen dieser Klasse fuehren den neutralen Punkt
        **symbolisch** — sie halten die Abbildung und wandern mit jeder
        Aenderung mit. Genau deshalb steht hier einer, der es nicht tut: Wer
        den Punkt aus der Verteilung schiebt, macht aus dem Faktor eine
        einseitige Daempfung, und kein anderer Zeuge wuerde rot. Die erste
        Fassung stand auf 0.50 und war genau dieser Fall — 12 von 15 Turns
        darunter.
        """
        gemessen_min: float = 0.2704
        gemessen_max: float = 0.5177
        self.assertGreaterEqual(HALTUNG_FASZINATION_NEUTRAL, gemessen_min)
        self.assertLessEqual(HALTUNG_FASZINATION_NEUTRAL, gemessen_max)


class WirkungAufDieHaltung(unittest.TestCase):
    """Was der Faktor in der fertigen Haltung anrichtet — und was nicht."""

    def test_hohe_faszination_fragt_mehr_als_niedrige(self):
        """Der Kern des Auftrags: Das Thema entscheidet ueber die Fragenlust."""
        hoch = haltung_berechnen(LANDSCHAFT, RAD, 1.0)
        tief = haltung_berechnen(LANDSCHAFT, RAD, 0.0)
        self.assertIsNotNone(hoch)
        self.assertIsNotNone(tief)
        self.assertGreater(
            hoch.werte["fragen"].ergebnis, tief.werte["fragen"].ergebnis
        )

    def test_beide_zellen_der_speiche_werden_moduliert(self):
        """Der Faktor trifft die **Zeile**, nicht eine ausgewaehlte Zelle.

        `wissbegier` traegt auf `fragen` und auf `draengen`. Wer den Faktor
        nur an der einen Stelle anwendet, macht den Zeugen darueber gruen und
        laesst die zweite Zelle unveraendert — die Speiche wirkte dann halb
        themengebunden und halb themenblind.
        """
        self.assertEqual(
            {"fragen", "draengen"}, set(SPEICHEN_BEITRAG[FASZINATION_SPEICHE])
        )
        hoch = haltung_berechnen(LANDSCHAFT, RAD, 1.0)
        tief = haltung_berechnen(LANDSCHAFT, RAD, 0.0)
        for name in ("fragen", "draengen"):
            self.assertGreater(
                hoch.werte[name].ergebnis,
                tief.werte[name].ergebnis,
                msg=f"{name} folgt der Faszination nicht",
            )

    def test_ohne_faszination_bleibt_es_beim_bisherigen_wert(self):
        """Der Zustand vor dem 07.09.2026 ist der Rueckfall, nicht ein Sonderfall.

        Die Gegenprobe zum Auftrag: Wer `None` reicht, bekommt exakt die
        Haltung, die die Rechnung vor dem Umbau geliefert hat.
        """
        ohne     = haltung_berechnen(LANDSCHAFT, RAD, None)
        neutral  = haltung_berechnen(LANDSCHAFT, RAD, HALTUNG_FASZINATION_NEUTRAL)
        self.assertIsNotNone(ohne)
        for name in ohne.werte:
            self.assertAlmostEqual(
                ohne.werte[name].ergebnis,
                neutral.werte[name].ergebnis,
                places=10,
                msg=f"{name} weicht zwischen None und neutralem Punkt ab",
            )

    def test_nur_die_eine_speiche_wird_moduliert(self):
        """Die Gegenprobe gegen Mitmodulation — sonst waere jeder Zeuge gruen.

        `waerme` bekommt in diesem Rad **keinen** Beitrag von
        `FASZINATION_SPEICHE`, wohl aber von der Kontrollspeiche. Aendert sie
        sich mit der Faszination, trifft der Faktor das ganze Rad statt einer
        Zeile.
        """
        self.assertNotIn("waerme", SPEICHEN_BEITRAG[FASZINATION_SPEICHE])
        hoch = haltung_berechnen(LANDSCHAFT, RAD, 1.0)
        tief = haltung_berechnen(LANDSCHAFT, RAD, 0.0)
        self.assertAlmostEqual(
            hoch.werte["waerme"].ergebnis,
            tief.werte["waerme"].ergebnis,
            places=10,
        )

    def test_eine_groesse_ohne_die_speiche_bleibt_unberuehrt(self):
        """`umfang` traegt seit dem 08.08.2026 keinen `wissbegier`-Beitrag.

        **Der Zeuge haelt einen Befund fest, nicht nur eine Rechnung.** Das
        Faszinationskonzept §11 beschreibt den Ersatz am *Umfang*; die Zelle
        ist gestrichen. Wer sie wieder eintraegt, macht diesen Zeugen rot und
        weiss dann, dass er zugleich §11 einloest.
        """
        self.assertNotIn("umfang", SPEICHEN_BEITRAG[FASZINATION_SPEICHE])
        hoch = haltung_berechnen(LANDSCHAFT, RAD, 1.0)
        tief = haltung_berechnen(LANDSCHAFT, RAD, 0.0)
        self.assertAlmostEqual(
            hoch.werte["umfang"].ergebnis,
            tief.werte["umfang"].ergebnis,
            places=10,
        )

    def test_ein_rad_ohne_die_speiche_bleibt_unveraendert(self):
        """Kein `wissbegier` im Rad, keine Wirkung — gleich welcher Faktor."""
        rad: dict[str, float] = {"aufmerksamkeit": 0.60, "wohlwollen": 0.50}
        hoch = haltung_berechnen(LANDSCHAFT, rad, 1.0)
        tief = haltung_berechnen(LANDSCHAFT, rad, 0.0)
        for name in hoch.werte:
            self.assertAlmostEqual(
                hoch.werte[name].ergebnis,
                tief.werte[name].ergebnis,
                places=10,
                msg=f"{name} bewegt sich ohne die modulierte Speiche",
            )

    def test_rohwert_und_faktor_stehen_beide_im_ergebnis(self):
        """Ein Faktor von 1.0 hat zwei Ursachen; nur der Rohwert trennt sie."""
        ohne    = haltung_berechnen(LANDSCHAFT, RAD, None)
        neutral = haltung_berechnen(LANDSCHAFT, RAD, HALTUNG_FASZINATION_NEUTRAL)
        self.assertEqual(ohne.fasz_faktor, 1.0)
        self.assertAlmostEqual(neutral.fasz_faktor, 1.0, places=10)
        self.assertIsNone(ohne.faszination)
        self.assertIsNotNone(neutral.faszination)

    def test_die_kurzfassung_zeigt_den_faktor_nur_wenn_er_traegt(self):
        """Eine Zeile, die in jedem Turn 'fasz 1.00' traegt, verbirgt den Fall."""
        self.assertNotIn("fasz", haltung_berechnen(LANDSCHAFT, RAD, None).kurzfassung())
        self.assertIn("fasz", haltung_berechnen(LANDSCHAFT, RAD, 0.8).kurzfassung())


if __name__ == "__main__":
    unittest.main()
