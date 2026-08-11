"""Zeugen fuer die feine Skala der beiden Charakter-Raeder.

**Warum sie fein ist — gemessen, nicht gewaehlt.** Bis zum 11.08.2026 liessen
beide Rad-Prompts nur drei Werte zu: 0.0, 0.5, 1.0. Lag ein Urteil dazwischen,
musste das Modell runden, und es rundete nach oben: `distanz` stand in sechs
von sechs Messungen ueber drei Personen und beide Paarrichtungen auf 1.00.

Gemessen am 11.08.2026 ueber drei Quellen, vier Laeufe je Fassung, gleiche
Eingabe, gleiche Temperatur, gleiche Penalty (`labor/ergebnis/rad_rauschen_*`):

    Streuung je Quelle    grob 0.18 / 0.18 / 0.22
                          fein 0.061 / 0.062 / 0.080

    Trennschaerfe         grob  2.4 bis 3.3 Sigma
                          fein 10.2 bis 12.9 Sigma

**Das Rauschen faellt um das Dreifache, die Trennschaerfe steigt um das
Vierfache.** Die Arithmetik verlangt die grobe Skala an keiner Stelle: Die
Speichengewichte summieren sich auf 0.60 und 0.40, mit der Nabe 0.9 faellt die
Faktorspanne exakt auf die Klemme 0.5 bis 1.5 — jede Speiche in [0, 1] fuellt
sie aus, feiner oder groeber aendert daran nichts.

Diese Zeugen halten den Prompt fest, damit ein Aufraeumen ihn nicht
zurueckdreht: Die Zahl waere danach wieder unlesbar, und die Suite bliebe
gruen.
"""

import unittest

from agents.charakter.destillation import (
    CHARAKTER_RAD_PROMPT,
    INITIATIVE_RAD_PROMPT,
    RAD_MAX,
    RAD_MIN,
    RAD_ZUG_HOCH,
    RAD_ZUG_RUNTER,
    nutzer_gewichtung_berechnen,
)


class SkalaTest(unittest.TestCase):
    """Beide Prompts lassen Zwischenwerte zu, und die Formel traegt sie."""

    def test_beide_prompts_erlauben_zwischenwerte(self) -> None:
        """Rot, sobald einer der beiden auf drei Werte zurueckgedreht wird."""
        for name, prompt in (("Zuwendung", CHARAKTER_RAD_PROMPT),
                             ("Initiative", INITIATIVE_RAD_PROMPT)):
            with self.subTest(rad=name):
                self.assertIn("Nachkommastelle", prompt)
                self.assertIn("Zwischenwerte sind ausdruecklich erlaubt", prompt)
                self.assertNotIn("genau einen von drei Werten", prompt)

    def test_die_drei_marken_bleiben_als_anhalt(self) -> None:
        """Die feine Skala ersetzt die Kalibrierung nicht, sie erweitert sie.

        Ohne die verbalen Marken haette »0.7« keinen Bezug mehr — das Modell
        wuesste nicht, woran es die Zahl misst.
        """
        for name, prompt in (("Zuwendung", CHARAKTER_RAD_PROMPT),
                             ("Initiative", INITIATIVE_RAD_PROMPT)):
            with self.subTest(rad=name):
                for marke in ("nicht erkennbar", "angedeutet", "ausgepraegt"):
                    self.assertIn(marke, prompt)

    def test_die_formel_traegt_zwischenwerte(self) -> None:
        """Ein Rad aus lauter 0.7 liegt in der Spanne und ist nachrechenbar.

        Die Gewichte sind so gewaehlt, dass volle Auslenkung die Klemme
        exakt trifft; ein Siebtel-Schritt kann sie deshalb nicht verlassen.
        """
        rad = {"hoch":   {n: 0.7 for n in RAD_ZUG_HOCH},
               "runter": {n: 0.7 for n in RAD_ZUG_RUNTER}}
        faktor = nutzer_gewichtung_berechnen(rad)

        erwartet = 0.9 + 0.7 * sum(RAD_ZUG_HOCH.values()) \
                       - 0.7 * sum(RAD_ZUG_RUNTER.values())
        self.assertAlmostEqual(faktor, erwartet, places=9)
        self.assertGreaterEqual(faktor, RAD_MIN)
        self.assertLessEqual(faktor, RAD_MAX)

    def test_volle_auslenkung_trifft_die_klemme_weiterhin_exakt(self) -> None:
        """Die Gegenprobe zur vorigen: Die feine Skala verschiebt die
        Konstruktion nicht, sie fuellt sie nur dichter."""
        voll_hoch = {"hoch":   {n: 1.0 for n in RAD_ZUG_HOCH},
                     "runter": {n: 0.0 for n in RAD_ZUG_RUNTER}}
        voll_runter = {"hoch":   {n: 0.0 for n in RAD_ZUG_HOCH},
                       "runter": {n: 1.0 for n in RAD_ZUG_RUNTER}}
        self.assertAlmostEqual(nutzer_gewichtung_berechnen(voll_hoch),
                               RAD_MAX, places=9)
        self.assertAlmostEqual(nutzer_gewichtung_berechnen(voll_runter),
                               RAD_MIN, places=9)


if __name__ == "__main__":
    unittest.main()
