"""Zeugen: die sechs Turn-Modulatoren der Faszination (§10.5).

Ziel: Ein Turn moduliert die Faszination eines Traegers, ohne sie je zu
loeschen — alle sechs Faktoren liegen in ihrer zugesagten Spanne und werden
nie 0 (Regel (a) aus §10.0: keine Null aus einer Multiplikation).

**Der wichtigste Zeuge ist die Kanon-Deckung.** Eine Tabelle, die einen
Kanonwert nicht kennt, liefert stumm den neutralen Faktor — und ein
Vorgabewert in einem Produkt ist von einem gesetzten nicht zu unterscheiden.

Reine Funktionen: keine Datenbank, kein Modell, kein Zustand.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import (
    EMOTIONS_VEKTOREN,
    FASZ_ANLAGE_MAX,
    FASZ_ANLAGE_MIN,
    FASZ_AROUSAL_MAX,
    FASZ_AROUSAL_MIN,
    FASZ_AROUSAL_SCHEITEL,
    FASZ_BESETZUNG_AWE,
    FASZ_BESETZUNG_NEUTRAL,
    FASZ_BESETZUNG_SEKTOR,
    FASZ_INTENT_FAKTOREN,
    FASZ_MODUS_FAKTOREN,
    FASZ_VERLAUF_FAKTOREN,
    MODUS_KANON,
)
from ei import fascination

INTENT_KANON: frozenset[str] = frozenset({
    "smalltalk", "knowledge", "personal", "task", "creative", "meta",
})


class DieTabellenDeckenIhrenKanonTest(unittest.TestCase):
    """Ohne Deckung liefert ein gueltiger Wert stumm den Vorgabefall."""

    def test_der_verlauf_kennt_jeden_emotionsvektor(self) -> None:
        """Alle neun Werte aus `EMOTIONS_VEKTOREN`, keiner mehr."""
        self.assertEqual(
            set(EMOTIONS_VEKTOREN), set(FASZ_VERLAUF_FAKTOREN),
            "Die Verlaufstabelle deckt den Kanon nicht — ein fehlender Wert "
            "faende stumm den neutralen Faktor",
        )

    def test_der_modus_kennt_jeden_kanonwert(self) -> None:
        """Alle zehn Werte aus `MODUS_KANON`, keiner mehr."""
        self.assertEqual(set(MODUS_KANON), set(FASZ_MODUS_FAKTOREN))

    def test_der_intent_kennt_jeden_kanonwert(self) -> None:
        """Die sechs Werte des Perzeptions-Enums."""
        self.assertEqual(INTENT_KANON, set(FASZ_INTENT_FAKTOREN))

    def test_keine_tabelle_traegt_eine_null(self) -> None:
        """Regel (a) aus §10.0 — eine Null loeschte die ganze Bindung."""
        for name, tabelle in (
            ("verlauf", FASZ_VERLAUF_FAKTOREN),
            ("intent", FASZ_INTENT_FAKTOREN),
            ("modus", FASZ_MODUS_FAKTOREN),
        ):
            for wert, faktor in tabelle.items():
                self.assertGreater(faktor, 0.0, f"{name}/{wert} ist 0")

    def test_die_spannen_des_konzepts_werden_eingehalten(self) -> None:
        """§10.5 nennt je Tabelle eine Spanne — sie ist bindend."""
        self.assertEqual(0.80, min(FASZ_VERLAUF_FAKTOREN.values()))
        self.assertEqual(1.25, max(FASZ_VERLAUF_FAKTOREN.values()))
        self.assertEqual(0.85, min(FASZ_INTENT_FAKTOREN.values()))
        self.assertEqual(1.20, max(FASZ_INTENT_FAKTOREN.values()))
        self.assertEqual(0.90, min(FASZ_MODUS_FAKTOREN.values()))
        self.assertEqual(1.15, max(FASZ_MODUS_FAKTOREN.values()))


class DasUmgekehrteUTest(unittest.TestCase):
    """`f_arousal` — Berlyne: beide Extreme binden nicht."""

    def test_der_scheitel_traegt_das_maximum(self) -> None:
        self.assertAlmostEqual(
            FASZ_AROUSAL_MAX, fascination.f_arousal(FASZ_AROUSAL_SCHEITEL), 6,
        )

    def test_beide_raender_erreichen_das_minimum(self) -> None:
        """Der Zeuge, der den Baufehler vom 05.09.2026 gefunden hat.

        Die erste Fassung normierte beide Flanken ueber die **linke** Breite.
        Links stimmte das Minimum, rechts stand der Faktor bei 1,1615 — in
        der Spanne, also von der Ausgabe-Verifikation nicht zu fassen, und
        trotzdem falsch: Ueberreizung haette fast so stark gebunden wie der
        Scheitel.
        """
        self.assertAlmostEqual(FASZ_AROUSAL_MIN, fascination.f_arousal(0.0), 6)
        self.assertAlmostEqual(FASZ_AROUSAL_MIN, fascination.f_arousal(1.0), 6)

    def test_die_rechte_flanke_faellt_steiler(self) -> None:
        """§10.5: *ueber 0,85 fallend* — und schneller als links."""
        links:  float = fascination.f_arousal(FASZ_AROUSAL_SCHEITEL - 0.2)
        rechts: float = fascination.f_arousal(FASZ_AROUSAL_SCHEITEL + 0.2)
        self.assertLess(rechts, links)

    def test_die_kurve_steigt_bis_zum_scheitel_und_faellt_danach(self) -> None:
        """Ein umgekehrtes U hat genau einen Hochpunkt."""
        werte = [fascination.f_arousal(x / 20) for x in range(21)]
        hoch = werte.index(max(werte))
        self.assertTrue(all(werte[i] < werte[i + 1] for i in range(hoch)))
        self.assertTrue(
            all(werte[i] > werte[i + 1] for i in range(hoch, len(werte) - 1))
        )

    def test_ein_wert_ausserhalb_wird_geklemmt_und_gemeldet(self) -> None:
        """Er deutet auf eine andere Skala beim Aufrufer."""
        with self.assertLogs("ki_server.ei.fascination", "ERROR"):
            self.assertAlmostEqual(
                FASZ_AROUSAL_MIN, fascination.f_arousal(1.7), 6,
            )


class DieBesetzungIstValenzblindTest(unittest.TestCase):
    """§10.5 — `SEKTOR_GRUPPE` wird bewusst ignoriert."""

    def test_neutral_daempft(self) -> None:
        self.assertEqual(FASZ_BESETZUNG_NEUTRAL, fascination.f_besetzung("neutral"))

    def test_ein_leerer_wert_zaehlt_wie_neutral(self) -> None:
        """Ein Turn ohne Emotionsurteil ist nicht besetzt."""
        self.assertEqual(FASZ_BESETZUNG_NEUTRAL, fascination.f_besetzung(""))

    def test_positiv_und_negativ_besetzt_wiegen_gleich(self) -> None:
        """Der Kern der Valenzblindheit — Gartenkraeuter und Kriegsgeschichte."""
        self.assertEqual(
            fascination.f_besetzung("freude"), fascination.f_besetzung("trauer"),
        )
        self.assertEqual(FASZ_BESETZUNG_SEKTOR, fascination.f_besetzung("freude"))

    def test_die_awe_dyade_traegt_am_meisten(self) -> None:
        self.assertEqual(FASZ_BESETZUNG_AWE, fascination.f_besetzung("ehrfurcht"))
        self.assertGreater(FASZ_BESETZUNG_AWE, FASZ_BESETZUNG_SEKTOR)


class DerVerlaufMisstBewegungTest(unittest.TestCase):
    """Nicht die Richtung — `eskalation` ist negativ und steht oben."""

    def test_eskalation_wiegt_wie_aufbluehen(self) -> None:
        self.assertEqual(
            fascination.f_verlauf("aufbluehen"), fascination.f_verlauf("eskalation"),
        )

    def test_plateau_daempft_staerker_als_jede_bewegung(self) -> None:
        self.assertLess(
            fascination.f_verlauf("plateau"), fascination.f_verlauf("erholung"),
        )

    def test_ein_unbekannter_wert_meldet_sich(self) -> None:
        """Der Kanonbruch ist ein Befund, kein Vorgabefall.

        Gemessen am 04.09.2026: Der Bestand traegt in `intent` 28-mal
        `philosophischer_austausch` — einen Modus-Wert.
        """
        with self.assertLogs("ki_server.ei.fascination", "WARNING"):
            self.assertEqual(1.0, fascination.f_verlauf("schwingung"))

    def test_ein_leerer_wert_meldet_sich_nicht(self) -> None:
        """Er ist der Normalfall eines Turns ohne Urteil, kein Bruch."""
        self.assertEqual(1.0, fascination.f_verlauf(""))


class DieAnlageKommtAusEinerSpeicheTest(unittest.TestCase):
    """Von zwoelf Radspeichen traegt genau `wissbegier <-> langeweile`."""

    def test_die_spanne_wird_ausgeschoepft(self) -> None:
        self.assertAlmostEqual(FASZ_ANLAGE_MIN, fascination.f_anlage(0.0), 6)
        self.assertAlmostEqual(FASZ_ANLAGE_MAX, fascination.f_anlage(1.0), 6)

    def test_ohne_radmessung_moduliert_nichts(self) -> None:
        """None ist der ehrliche Fall und darf weder heben noch senken."""
        self.assertEqual(1.0, fascination.f_anlage(None))

    def test_null_ist_nicht_none(self) -> None:
        """Langeweile ist eine Messung, keine fehlende Messung."""
        self.assertNotEqual(fascination.f_anlage(0.0), fascination.f_anlage(None))


class KeinFaktorLoeschtDieBindungTest(unittest.TestCase):
    """Regel (a) aus §10.0, ueber alle sechs zusammen."""

    def test_das_produkt_der_schlechtesten_faelle_bleibt_positiv(self) -> None:
        produkt: float = (
            fascination.f_arousal(0.0)
            * fascination.f_besetzung("neutral")
            * fascination.f_verlauf("absturz")
            * fascination.f_intent("task")
            * fascination.f_modus("berichtend")
            * fascination.f_anlage(0.0)
        )
        self.assertGreater(produkt, 0.0)
        self.assertLess(produkt, 1.0, "Der schlechteste Fall muss daempfen")

    def test_das_produkt_der_besten_faelle_hebt(self) -> None:
        produkt: float = (
            fascination.f_arousal(FASZ_AROUSAL_SCHEITEL)
            * fascination.f_besetzung("ehrfurcht")
            * fascination.f_verlauf("eskalation")
            * fascination.f_intent("knowledge")
            * fascination.f_modus("lernmodus")
            * fascination.f_anlage(1.0)
        )
        self.assertGreater(produkt, 1.0)


if __name__ == "__main__":
    unittest.main()
