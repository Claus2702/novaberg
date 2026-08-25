"""Tests: Das zweite Charakter-Rad rechnet den Initiative-Versatz.

Ziel: Aus zehn Einzelbewertungen entsteht ein Versatz, der von Hand
nachrechenbar ist — und ein unvollstaendiges Rad wird abgelehnt statt
ergaenzt.

Hintergrund (Chat 116): Der Versatz verschiebt den Rohwert der Initiative-
Achse. Bis dieses Rad gebaut war, stand er auf 0.0 und war nicht abgeleitet —
dieselbe Lage wie GV_RAUM_CHARAKTER_FAKTOR nach Chat 114, wo der Versuch,
einen Charakterfaktor ueber eine Cosine-Distanz zu gewinnen, gemessen
gescheitert ist (echter Charakter bei +0.036, Vorzeichenwechsel je nach
eingebetteter Schicht). Das Rad geht den anderen Weg: zehn konkrete
Einzelfragen, das Ergebnis gerechnet.

Zeugen dieser Datei:
  * Die Erwartungen sind **von Hand aus den Zug-Tabellen gerechnet** und
    stehen als Literale im Test. Keine stammt aus `initiative_versatz_berechnen`.
  * Die Bauregel "volle Auslenkung trifft die Grenze exakt" stammt aus dem
    Konzept (§6.3) und aus dem Vorbild `nutzer_gewichtung`, nicht aus dem Code.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from agents.charakter.destillation import (
    INITIATIVE_RAD_LEER,
    INITIATIVE_ZUG_HOCH,
    INITIATIVE_ZUG_RUNTER,
    initiative_versatz_berechnen,
)
from config import INITIATIVE_RAD_NABE, INITIATIVE_RAD_SPANNE


def _rad(hoch: dict | None = None, runter: dict | None = None) -> dict:
    """Baut ein vollstaendiges Rad, in dem nur die genannten Speichen tragen."""
    return {
        "hoch":   {n: (hoch or {}).get(n, 0.0)   for n in INITIATIVE_ZUG_HOCH},
        "runter": {n: (runter or {}).get(n, 0.0) for n in INITIATIVE_ZUG_RUNTER},
    }


class TestVolleAuslenkung(unittest.TestCase):
    """Die Grenzen werden exakt getroffen — die Kappung ist Sicherung."""

    def test_leeres_rad_ergibt_die_nabe(self) -> None:
        self.assertEqual(INITIATIVE_RAD_NABE,
                         initiative_versatz_berechnen(INITIATIVE_RAD_LEER))

    def test_alle_fuenf_oben_treffen_die_obere_grenze(self) -> None:
        """Von Hand: 0.08 + 0.06 + 0.05 + 0.04 + 0.02 = 0.25."""
        voll: dict = _rad(hoch={n: 1.0 for n in INITIATIVE_ZUG_HOCH})
        self.assertAlmostEqual(+0.25, initiative_versatz_berechnen(voll))
        self.assertAlmostEqual(INITIATIVE_RAD_SPANNE,
                               initiative_versatz_berechnen(voll))

    def test_alle_fuenf_unten_treffen_die_untere_grenze(self) -> None:
        voll: dict = _rad(runter={n: 1.0 for n in INITIATIVE_ZUG_RUNTER})
        self.assertAlmostEqual(-0.25, initiative_versatz_berechnen(voll))

    def test_eine_einzelne_speiche_traegt_ihren_zug(self) -> None:
        """Von Hand: Folgsamkeit allein, ausgepraegt → +0.08; angedeutet → +0.04."""
        self.assertAlmostEqual(
            +0.08, initiative_versatz_berechnen(_rad(hoch={"folgsamkeit": 1.0})))
        self.assertAlmostEqual(
            +0.04, initiative_versatz_berechnen(_rad(hoch={"folgsamkeit": 0.5})))

    def test_gegenlaeufige_speichen_heben_sich_auf(self) -> None:
        """Folgsamkeit 1.0 (+0.08) gegen Lenkungsdrang 1.0 (−0.08) = 0.0.

        Das ist der Fall, den das Herkunftsfeld von "nichts erkannt"
        unterscheiden muss: ein gerechnetes 0.0 aus zwei ausgepraegten
        Speichen, kein Ausfall.
        """
        rad: dict = _rad(hoch={"folgsamkeit": 1.0}, runter={"lenkungsdrang": 1.0})
        self.assertAlmostEqual(0.0, initiative_versatz_berechnen(rad))


class TestUnvollstaendigesRadWirdAbgelehnt(unittest.TestCase):
    """Eine fehlende Speiche als 0.0 zu ergaenzen hiesse, eine nicht
    gestellte Frage als beantwortet zu buchen.
    """

    def test_fehlende_speiche(self) -> None:
        rad: dict = _rad()
        del rad["hoch"]["behutsamkeit"]
        with self.assertRaises(ValueError) as fehler:
            initiative_versatz_berechnen(rad)
        self.assertIn("behutsamkeit", str(fehler.exception))

    def test_unbekannte_speiche(self) -> None:
        rad: dict = _rad()
        rad["runter"]["erfunden"] = 1.0
        with self.assertRaises(ValueError) as fehler:
            initiative_versatz_berechnen(rad)
        self.assertIn("erfunden", str(fehler.exception))

    def test_auspraegung_ausserhalb_von_null_bis_eins(self) -> None:
        with self.assertRaises(ValueError):
            initiative_versatz_berechnen(_rad(hoch={"folgsamkeit": 2.0}))

    def test_nicht_numerische_auspraegung(self) -> None:
        with self.assertRaises(ValueError):
            initiative_versatz_berechnen(_rad(hoch={"folgsamkeit": "viel"}))

    def test_fehlende_seite(self) -> None:
        with self.assertRaises(ValueError):
            initiative_versatz_berechnen({"hoch": {}})


class TestZugTabellen(unittest.TestCase):
    """Die Summen tragen die Bauregel — sie sind kein Zufall.

    Weicht eine Summe ab, trifft die volle Auslenkung die Grenze nicht mehr
    exakt, und die Kappung wuerde vom Sicherungsnetz zum Formteil. Das faellt
    sonst niemandem auf, weil beide Faelle denselben Wert liefern.
    """

    def test_beide_seiten_summieren_auf_die_spanne(self) -> None:
        self.assertAlmostEqual(INITIATIVE_RAD_SPANNE, sum(INITIATIVE_ZUG_HOCH.values()))
        self.assertAlmostEqual(INITIATIVE_RAD_SPANNE, sum(INITIATIVE_ZUG_RUNTER.values()))

    def test_zehn_speichen_fuenf_je_seite(self) -> None:
        self.assertEqual(5, len(INITIATIVE_ZUG_HOCH))
        self.assertEqual(5, len(INITIATIVE_ZUG_RUNTER))

    def test_die_speichennamen_ueberschneiden_sich_nicht(self) -> None:
        self.assertEqual(set(), set(INITIATIVE_ZUG_HOCH) & set(INITIATIVE_ZUG_RUNTER))


class TestMedianErhebung(unittest.TestCase):
    """Drei Erhebungen, der Median zaehlt — und das Rad bleibt nachrechenbar.

    Anlass (Chat 116, gemessen): Zwei Laeufe gegen denselben Charaktertext bei
    Temperatur 0.2 ergaben -0.18 und -0.13. Die Richtung war beide Male
    eindeutig, der Betrag nicht. Der Versatz wird bei der Destillation einmal
    geschrieben und bleibt bis zur naechsten stehen — ein ungluecklicher Lauf
    legte ihn sonst fuer Tage fest.

    Zeuge: Die erwarteten Mediane sind von Hand aus den eingespeisten Werten
    bestimmt, nicht aus der Funktion gelesen. Die Laeufe selbst sind Literale.
    """

    # Drei echte Raeder mit von Hand gerechneten Versaetzen. Kein erfundenes
    # Paar (Rad, Wert): Sonst pruefte der Nachrechen-Test die Vorrichtung
    # statt den Code.
    RAEDER: dict[str, tuple[dict, float]] = {
        # lenkungsdrang 1.0 x 0.08
        "a": (_rad(runter={"lenkungsdrang": 1.0}), -0.08),
        # lenkungsdrang 1.0 x 0.08 + eigensinn 1.0 x 0.06
        "b": (_rad(runter={"lenkungsdrang": 1.0, "eigensinn": 1.0}), -0.14),
        # folgsamkeit 1.0 x 0.08
        "c": (_rad(hoch={"folgsamkeit": 1.0}), +0.08),
    }

    @classmethod
    def _mit_laeufen(cls, kennungen: list[str | None]):
        """Ersetzt die Einzelerhebung durch eine Folge echter Raeder.

        None steht fuer einen gescheiterten Lauf.
        """
        from unittest.mock import patch

        from agents.charakter import destillation

        folge = [None if k is None else cls.RAEDER[k] for k in kennungen]
        return patch.object(destillation, "_initiative_rad_einmal",
                            side_effect=folge)

    def _erheben(self, kennungen: list[str | None], laeufe: int = 3):
        from agents.charakter.destillation import initiative_rad_destillieren

        with self._mit_laeufen(kennungen):
            return initiative_rad_destillieren("Profiltext", "test", laeufe=laeufe)

    def test_der_median_gewinnt_nicht_der_erste(self) -> None:
        """Von Hand: aus -0.14, +0.08, -0.08 ist -0.08 der mittlere Wert."""
        rad, versatz = self._erheben(["b", "c", "a"])
        self.assertAlmostEqual(-0.08, versatz)

    def test_die_streuung_wird_mitgespeichert(self) -> None:
        """Von Hand: max(+0.08) - min(-0.14) = 0.22."""
        rad, versatz = self._erheben(["b", "c", "a"])
        self.assertAlmostEqual(0.22, rad["streuung"])
        self.assertEqual([-0.14, -0.08, 0.08], sorted(rad["laeufe"]))

    def test_gespeichert_wird_ein_echtes_rad_kein_gemitteltes(self) -> None:
        """Das Rad des Median-Laufs, damit Rad x Zuege = Versatz gilt.

        Ein Durchschnitt aus drei Raedern ergaebe Auspraegungen wie 0.67, die
        kein Lauf je vergeben hat — und der Zusammenhang waere nicht mehr von
        Hand nachrechenbar.
        """
        rad, versatz = self._erheben(["b", "c", "a"])
        # Rad "a" hat gewonnen: lenkungsdrang allein, ausgepraegt.
        self.assertAlmostEqual(1.0, rad["runter"]["lenkungsdrang"])
        self.assertAlmostEqual(0.0, rad["runter"]["eigensinn"])
        for seite in ("hoch", "runter"):
            for wert in rad[seite].values():
                self.assertIn(wert, (0.0, 0.5, 1.0),
                              "Auspraegung stammt aus keinem Lauf — gemittelt?")

    def test_ein_gescheiterter_lauf_zaehlt_nicht_mit(self) -> None:
        """Von Hand: aus -0.20 und -0.05 (einer gescheitert) ist -0.20 der
        untere der beiden mittleren — ein echter Lauf, kein Mittelwert.
        """
        rad, versatz = self._erheben(["b", None, "c"])
        self.assertAlmostEqual(-0.14, versatz)
        self.assertEqual(2, len(rad["laeufe"]))

    def test_alle_laeufe_gescheitert_ergibt_keine_erhebung(self) -> None:
        """Der bestehende Versatz bleibt stehen, statt durch die Nabe ersetzt
        zu werden.
        """
        self.assertIsNone(self._erheben([None, None, None]))

    def test_ein_einzelner_lauf_ist_zulaessig(self) -> None:
        rad, versatz = self._erheben(["a"], laeufe=1)
        self.assertAlmostEqual(-0.08, versatz)
        self.assertAlmostEqual(0.0, rad["streuung"])

    def test_null_laeufe_werden_abgelehnt(self) -> None:
        self.assertIsNone(self._erheben([], laeufe=0))

    def test_die_metadaten_stoeren_die_nachrechnung_nicht(self) -> None:
        """Das gespeicherte Rad muss weiterhin durch die Rechnung gehen.

        Sonst waere der Beleg wertlos: Man koennte den Versatz nicht mehr aus
        dem gespeicherten Rad reproduzieren.
        """
        rad, versatz = self._erheben(["b", "c", "a"])
        self.assertAlmostEqual(versatz, initiative_versatz_berechnen(rad),
                               msg="Rad x Zuege ergibt nicht den gespeicherten Versatz")


if __name__ == "__main__":
    unittest.main()
