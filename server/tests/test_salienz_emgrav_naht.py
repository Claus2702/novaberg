"""Zeugen ueber die Naht zwischen emotionaler Gravitation und Salienz.

Ziel: Eine Erinnerung, die Nova emotional anzieht, macht ihre Aeusserung dazu
wichtiger — und der Weg vom Kanal zur Formel ist bezeugt, nicht nur die
Rechnung darin.

**Der Antrieb stand seit jeher als „nicht angeschlossen" im Ergebnis**, mit dem
Grund *unnormiert, Werte weit ueber 1.0*. `[gemessen 11.09.2026 ueber 888
Kandidaten aus 447 Turns]` Die Spanne liegt bei **0,184 bis 0,708**, kein
einziger Wert ueber 1,0 — seit `gravitation_lzg_berechnen` am 30.08.2026 durch
`LZG_KNOTEN_GEWICHT_CAP` teilt. **Der Grund war elf Tage hinfaellig, bevor ihn
jemand nachgeprueft hat**; der Eintrag stand unveraendert weiter.

**Vor dem Anschliessen wurde am 11.09.2026 nachgerechnet, ob er sichtbar wird.**
`[gerechnet 11.09.2026 ueber 488 Turns mit beiden Groessen]` Die emotionale Gravitation
gewaenne das `max()` in **44 Faellen (9,0 %)**. Das ist der Unterschied zum
Zielsog, der in 4 von 2786 Zeilen entschied (0,14 %) und deshalb vom `max()` in
einen Zug umgebaut wurde — ein Antrieb, der rechnet und unter einem `max()`
verschwindet, sieht von aussen aus wie einer, der nicht angeschlossen ist.

Zeugen dieser Datei:
  * **Die Verdrahtung, nicht die Rechnung.** Geprueft wird der Weg aus
    `state["emotionale_gravitationspunkte"]` bis in `ergebnis.antriebe` — der
    Kanal hatte seit dem 30.08.2026 einen Schreiber und keinen Leser fuer
    diesen Zweck.
  * **Das Maximum, nicht die Summe.** Eine Summe ueber aktivierte Punkte ist
    unbeschraenkt und traegt den Vergleich mit den uebrigen Antrieben nicht —
    derselbe Fehler, der `ziel_gravitation` bis zum 09.09.2026 auf 4,097 trieb.
  * **Ein fehlender Wert ist kein Nullzug.** Ein Punkt ohne Zahl wird gemeldet,
    nicht still zu 0.0 gemacht.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from graph.nodes.salience import (
    _formel_aus_dem_state,
    _staerkste_emotionale_gravitation,
)

SALIENZ_LOGGER: str = "ki_server.salience"


def _state(*gravitationen: float) -> dict:
    """Ein Zustand mit aktivierten emotionalen Gravitationspunkten."""
    return {
        "emotionale_gravitationspunkte": [
            {"knoten_id": i, "gravitation": g}
            for i, g in enumerate(gravitationen)
        ],
    }


class DerKanalErreichtDieFormel(unittest.TestCase):
    """Vom State bis in die Antriebe — der Weg, den es nicht gab."""

    def test_der_wert_steht_als_antrieb_im_ergebnis(self) -> None:
        ergebnis = _formel_aus_dem_state(
            _state(0.31, 0.62), sprachlich=0.2,
            gravitationsterm=0.1, arousal=0.5, nutzer_gewichtung=None,
        )

        self.assertEqual(ergebnis.antriebe["emotionale_gravitation"], 0.62)

    def test_er_hebt_den_eigen_pfad_wenn_er_gewinnt(self) -> None:
        mit = _formel_aus_dem_state(
            _state(0.62), sprachlich=0.2,
            gravitationsterm=0.1, arousal=0.5, nutzer_gewichtung=None,
        )
        ohne = _formel_aus_dem_state(
            {}, sprachlich=0.2,
            gravitationsterm=0.1, arousal=0.5, nutzer_gewichtung=None,
        )

        self.assertGreater(mit.eigen_pfad, ohne.eigen_pfad)

    def test_er_steht_nicht_mehr_unter_den_fehlenden(self) -> None:
        ergebnis = _formel_aus_dem_state(
            {}, sprachlich=0.2, gravitationsterm=0.0,
            arousal=0.5, nutzer_gewichtung=None,
        )

        self.assertNotIn("emotionale_gravitation", ergebnis.nicht_angeschlossen)
        self.assertIn("neugier", ergebnis.nicht_angeschlossen)


class DasMaximumNichtDieSumme(unittest.TestCase):
    """Drei Punkte ergeben den staerksten, nicht ihre Summe."""

    def test_drei_punkte_ergeben_den_staerksten(self) -> None:
        self.assertEqual(
            _staerkste_emotionale_gravitation(_state(0.21, 0.55, 0.33)), 0.55)

    def test_eine_summe_laege_ueber_eins_und_tut_es_nicht(self) -> None:
        """0,4 + 0,5 + 0,6 = 1,5 — das Maximum bleibt 0,6."""
        self.assertEqual(
            _staerkste_emotionale_gravitation(_state(0.4, 0.5, 0.6)), 0.6)

    def test_ohne_punkte_kein_zug(self) -> None:
        self.assertEqual(_staerkste_emotionale_gravitation({}), 0.0)
        self.assertEqual(_staerkste_emotionale_gravitation(_state()), 0.0)


class EinFehlenderWertIstKeinNullzug(unittest.TestCase):
    """Der teuerste Fall waere der stille: ein Punkt ohne Zahl als 0.0."""

    def test_ein_punkt_ohne_zahl_wird_gemeldet(self) -> None:
        zustand: dict = {"emotionale_gravitationspunkte": [
            {"knoten_id": 1, "gravitation": None},
            {"knoten_id": 2, "gravitation": 0.44},
        ]}

        with self.assertLogs(SALIENZ_LOGGER, level="WARNING") as log:
            wert: float = _staerkste_emotionale_gravitation(zustand)

        self.assertEqual(wert, 0.44)
        self.assertTrue(
            any("ohne brauchbaren" in z for z in log.output),
            f"Keine Meldung: {log.output}",
        )


if __name__ == "__main__":
    unittest.main()
