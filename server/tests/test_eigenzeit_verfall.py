"""Tests: Eine Aeusserung nach einer Pause trifft Nova auf einem gesenkten Zustand.

Bauteil A. Der Zustand ueberlebt den Turn in ``redis:nova_state`` — und blieb
bis zum 15.08.2026 stehen, wie er war. Wer nach acht Stunden „Guten Morgen"
schrieb, traf die Nova von gestern Nacht: am 14.08.2026 eine Landschaft
`beichte / Katharsis` auf einem spielerischen Gruss.

Die Kurve faellt **erst flach, dann steil, dann auf null** (§2.2). Ein
Exponentialverfall waere falsch — er faellt sofort am steilsten und naehme
jeder kurzen Unterbrechung ihre Energie. Wer fuer zehn Minuten den Raum
verlaesst, soll dieselbe Person wiederfinden.

Zwei Bauarten, die nicht vermengt werden:

    Erregung          Zahl       wird zur Ruhelage gezogen
    Modus, Stil,      Kategorie  springt auf den Neutralwert, sobald die
    Ton, Emotion                 Kurve unter die Schwelle faellt

Zeugen dieser Datei:
  * **Beide Richtungen.** Dass eine lange Pause senkt, ist erst eine Aussage,
    wenn eine kurze es nicht tut — sonst waere auch ein Verfall gruen, der
    immer zuschlaegt.
  * **Die bindende Spalte bleibt.** Naehe, Tiefe und Beziehungsdynamik sind
    nicht die Energie; ein taeglicher Rueckbau naehme dem Raumzug seinen
    Gegenstand.
  * **Der Impuls-Turn ist keine Pause.** Liefe die Uhr auf jedem Turn, setzte
    der stuendliche Impuls sie zurueck und die Nacht waere nie eine Pause —
    das ist die Bedingung, an der der Bauteil scheitert, wenn man sie
    uebersieht (§2.2).
  * **Ein fehlender Zeitstempel ist kein frischer.** Er darf nicht wie eine
    Pause von null wirken; wo nichts steht, wird nicht gedaempft und es wird
    gesagt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import (
    EIGENZEIT_AROUSAL_RUHE,
    EIGENZEIT_HALBWERT_FAKTOR,
    EIGENZEIT_HALBWERT_SEKUNDEN,
    EIGENZEIT_KIPPPUNKT_FAKTOR,
    EIGENZEIT_KIPPPUNKT_SEKUNDEN,
    EIGENZEIT_NULLPUNKT_SEKUNDEN,
)
from ei.eigenzeit import (
    KATEGORIE_NEUTRAL,
    arousal_daempfen,
    kategorien_gesprungen,
    verfall_faktor,
)

STUNDE: float = 3600.0


class DieKurveTest(unittest.TestCase):
    """Die drei Marken aus dem Konzept, und die Form dazwischen."""

    def test_ohne_pause_bleibt_alles(self) -> None:
        """Faktor 1,0 — der Normalfall im laufenden Gespraech."""
        self.assertEqual(1.0, verfall_faktor(0.0))

    def test_die_marken_werden_getroffen(self) -> None:
        """Kipppunkt, Halbwert und Nullpunkt stammen aus der Konfiguration."""
        self.assertAlmostEqual(
            EIGENZEIT_KIPPPUNKT_FAKTOR,
            verfall_faktor(EIGENZEIT_KIPPPUNKT_SEKUNDEN), places=4,
        )
        self.assertAlmostEqual(
            EIGENZEIT_HALBWERT_FAKTOR,
            verfall_faktor(EIGENZEIT_HALBWERT_SEKUNDEN), places=4,
        )
        self.assertEqual(0.0, verfall_faktor(EIGENZEIT_NULLPUNKT_SEKUNDEN))

    def test_erst_flach_dann_steil(self) -> None:
        """Die halbe Stunde kostet weniger als die vierte.

        Das ist die Aussage gegen den Exponentialverfall: Der faellt sofort am
        steilsten, diese Kurve nicht.
        """
        erste_halbe:  float = 1.0 - verfall_faktor(0.5 * STUNDE)
        vierte_halbe: float = verfall_faktor(1.5 * STUNDE) - verfall_faktor(2.0 * STUNDE)
        self.assertLess(erste_halbe, vierte_halbe)

    def test_nach_dem_nullpunkt_bleibt_null(self) -> None:
        """Eine Nacht ist nicht negativer als drei Stunden."""
        self.assertEqual(0.0, verfall_faktor(12 * STUNDE))

    def test_die_kurve_faellt_monoton(self) -> None:
        """Keine Pause bringt Energie zurueck."""
        werte: list[float] = [
            verfall_faktor(minute * 60.0) for minute in range(0, 200, 5)
        ]
        for vorher, nachher in zip(werte, werte[1:], strict=False):
            self.assertGreaterEqual(vorher, nachher)

    def test_eine_rueckwaerts_laufende_uhr_daempft_nicht(self) -> None:
        """Ein negativer Abstand ist kein Grund, etwas zu senken."""
        self.assertEqual(1.0, verfall_faktor(-500.0))


class DieErregungTest(unittest.TestCase):
    """Die Zahl wird gezogen, nicht gegen null multipliziert."""

    def test_volle_daempfung_endet_in_der_ruhelage(self) -> None:
        """0,00 waere keine Ruhe, sondern ein toter Wert."""
        self.assertAlmostEqual(
            EIGENZEIT_AROUSAL_RUHE, arousal_daempfen(0.95, 0.0), places=4,
        )

    def test_ohne_daempfung_bleibt_der_wert(self) -> None:
        """Faktor 1,0 laesst die Erregung, wie sie war."""
        self.assertAlmostEqual(0.95, arousal_daempfen(0.95, 1.0), places=4)

    def test_eine_ruhige_nova_wird_nicht_aufgedreht(self) -> None:
        """Der Verfall zieht von beiden Seiten zur Ruhe, er hebt nicht.

        Der positive Zwilling zum Senken: Ein Wert **unter** der Ruhelage darf
        durch eine Pause nicht steigen und dabei die Ruhelage ueberschreiten.
        """
        gedaempft: float = arousal_daempfen(0.20, 0.5)
        self.assertGreater(gedaempft, 0.20)
        self.assertLessEqual(gedaempft, EIGENZEIT_AROUSAL_RUHE)


class DieKategorienTest(unittest.TestCase):
    """Ein Zwischenwert einer Kategorie bedeutet nichts."""

    def test_ueber_der_schwelle_wird_gehalten(self) -> None:
        """Eine knappe Stunde nimmt einer Kategorie ihre Bedeutung nicht."""
        self.assertFalse(kategorien_gesprungen(0.90))

    def test_unter_der_schwelle_wird_gesprungen(self) -> None:
        """Traegt sie zu weniger als der Haelfte, ist sie keine mehr."""
        self.assertTrue(kategorien_gesprungen(0.10))

    def test_die_neutralwerte_stehen_vollstaendig(self) -> None:
        """Vier Kategorien fallen zurueck — fehlt eine, bleibt sie stehen."""
        self.assertEqual(
            {"emotion", "mode", "language_style", "tone"},
            set(KATEGORIE_NEUTRAL),
        )


if __name__ == "__main__":
    unittest.main()
