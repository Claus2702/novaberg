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
    FASZ_MAXIMUM,
    FASZ_MODUS_FAKTOREN,
    FASZ_VERLAUF_FAKTOREN,
    MODUS_KANON,
    QUALITAET_KANON,
    QUALITAET_VERFALL_BODEN,
    QUALITAET_VERFALL_UEBER_BERUEHRUNGEN,
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


class DerAnkerNormiertOhneBezugspunktTest(unittest.TestCase):
    """§10.2 — Saettigung statt Min-Max, damit der Massstab nicht wandert."""

    def test_die_halbstrecke_steht_auf_der_haelfte(self) -> None:
        """Die definierende Eigenschaft der Kurve."""
        self.assertAlmostEqual(
            0.5, fascination.norm_saettigung(3.0, 3.0), 9,
        )

    def test_null_bleibt_null_und_die_kurve_erreicht_nie_eins(self) -> None:
        self.assertEqual(0.0, fascination.norm_saettigung(0.0, 3.0))
        self.assertLess(fascination.norm_saettigung(1_000_000.0, 3.0), 1.0)

    def test_die_kurve_steigt_streng(self) -> None:
        """Ein Zaehler mehr darf nie weniger bedeuten."""
        werte = [fascination.norm_saettigung(n, 3.0) for n in range(12)]
        self.assertTrue(all(werte[i] < werte[i + 1] for i in range(len(werte) - 1)))

    def test_eine_halbstrecke_von_null_meldet_sich(self) -> None:
        """Sie waere eine leere Konfiguration, kein Grenzfall."""
        with self.assertLogs("ki_server.ei.fascination", "ERROR"):
            self.assertEqual(0.0, fascination.norm_saettigung(5.0, 0.0))


class UnbekannteHerkunftSenktNichtTest(unittest.TestCase):
    """Der Kern von `bindung_roh`: None ist nicht 0.

    Die Bruecke `verbindung` traegt keine Herkunftsspalte, und **318 von 1027
    Rohturns tragen keine Herkunft** `[gemessen 04.09.2026]`. Wer daraus 0.0
    machte, zaehlte *unbekannt* wie *der Nutzer hat es aufgebracht*.
    """

    def test_none_liegt_ueber_null(self) -> None:
        self.assertGreater(
            fascination.bindung_roh(1, 1, None),
            fascination.bindung_roh(1, 1, 0.0),
        )

    def test_bei_none_werden_die_gewichte_renormiert(self) -> None:
        """Der Wert bleibt auf derselben Skala, nur auf weniger Belegen.

        Ohne Renormierung faehle er um genau das Gewicht des fehlenden Terms
        — und waere mit einem vollstaendigen Wert nicht mehr vergleichbar.
        """
        voll: float = fascination.bindung_roh(3, 3, 0.5)
        ohne: float = fascination.bindung_roh(3, 3, None)
        self.assertAlmostEqual(0.5, ohne, 9, "Zwei Terme auf 0,5 ergeben 0,5")
        self.assertAlmostEqual(0.5, voll, 9)

    def test_der_volle_anker_bleibt_in_der_spanne(self) -> None:
        self.assertAlmostEqual(0.0, fascination.bindung_roh(0, 0, 0.0), 9)
        self.assertLess(fascination.bindung_roh(10_000, 10_000, 1.0), 1.0 + 1e-9)

    def test_ein_anteil_ausserhalb_wird_geklemmt_und_gemeldet(self) -> None:
        with self.assertLogs("ki_server.ei.fascination", "ERROR"):
            fascination.bindung_roh(1, 1, 1.4)

    def test_die_wiederkehr_wiegt_am_schwersten(self) -> None:
        """§10.2 — sie trennt Faszination von Neugier.

        **Verglichen wird bei gleicher normierter Auspraegung**, nicht bei
        gleicher Rohzahl. Die erste Fassung dieses Zeugen stellte die
        Wiederkehr auf ihrer Halbstrecke (norm = 0,5) gegen einen
        Eigenimpuls von 1,0 und schlug fehl — sie mass die Auspraegung und
        nannte es Gewicht. Beide Terme stehen hier auf 0,5.
        """
        auf_halb: float = 0.5
        drei_tage: float = 3.0   # BINDUNG_HALBSTRECKE_WIEDERKEHR -> norm 0,5
        nur_wiederkehr:   float = fascination.bindung_roh(drei_tage, 0, 0.0)
        nur_verweildauer: float = fascination.bindung_roh(0, drei_tage, 0.0)
        nur_eigenimpuls:  float = fascination.bindung_roh(0, 0, auf_halb)
        self.assertGreater(nur_wiederkehr, nur_eigenimpuls)
        self.assertGreater(nur_eigenimpuls, nur_verweildauer)


class DieZusammenfuehrungTest(unittest.TestCase):
    """§10.6 — neun Faktoren, eine Glaettung, der Rohwert bleibt."""

    def test_der_deckel_ergibt_exakt_eins(self) -> None:
        wert, roh = fascination.faszination(FASZ_MAXIMUM, 1.0, 1.0, None)
        self.assertAlmostEqual(1.0, wert, 9)
        self.assertAlmostEqual(FASZ_MAXIMUM, roh, 9)

    def test_der_rohwert_ueberlebt_die_deckelung(self) -> None:
        """Ohne ihn misst eine spaetere Kalibrierung die Kurve, nicht den Bestand.

        Zwei Traeger weit ueber dem Deckel stehen beide auf 1,0 — der
        Unterschied steckt dann nur noch im Rohwert.
        """
        _, roh_a = fascination.faszination(2.0, 2.0, 1.0, None)
        _, roh_b = fascination.faszination(2.0, 2.0, 2.0, None)
        self.assertAlmostEqual(4.0, roh_a, 9)
        self.assertAlmostEqual(8.0, roh_b, 9)
        self.assertNotEqual(roh_a, roh_b)

    def test_die_kurve_ist_steil_unten(self) -> None:
        """Eine entstehende Faszination soll sichtbar werden (§10.6)."""
        wert, _ = fascination.faszination(0.1, 1.0, 1.0, None)
        self.assertGreater(
            wert, 0.1 / FASZ_MAXIMUM,
            "sin^0.5 muss schwache Werte anheben, sonst verschwinden sie",
        )

    def test_ein_fehlender_zug_loescht_alles(self) -> None:
        """Ein Traeger ohne Bindung hat keine Faszination — das ist gewollt.

        Regel (a) aus §10.0 verbietet die Null aus einem **Modulator**, nicht
        aus einem Zug: Die drei Zuege sind die Sache selbst.
        """
        wert, roh = fascination.faszination(0.0, 1.0, 1.0, None)
        self.assertEqual(0.0, wert)
        self.assertEqual(0.0, roh)

    def test_ein_modulator_auf_null_wird_uebergangen_und_gemeldet(self) -> None:
        """Er waere ein Baufehler — und darf die Bindung nicht loeschen."""
        with self.assertLogs("ki_server.ei.fascination", "ERROR"):
            wert, _ = fascination.faszination(
                0.5, 1.0, 1.0, {"f_kaputt": 0.0},
            )
        self.assertGreater(wert, 0.0)

    def test_negative_zuege_werden_gemeldet(self) -> None:
        with self.assertLogs("ki_server.ei.fascination", "ERROR"):
            fascination.faszination(-1.0, 1.0, 1.0, None)

    def test_die_klammer_liefert_genau_sechs_modulatoren(self) -> None:
        """Keiner darf vergessen werden — ein fehlender waere stumm 1.0."""
        m = fascination.modulatoren_aus_turn(
            0.65, "neugierig", "eskalation", "knowledge", "lernmodus", 0.8,
        )
        self.assertEqual(6, len(m))
        self.assertTrue(all(f > 0.0 for f in m.values()))
        self.assertEqual(
            {"f_arousal", "f_besetzung", "f_verlauf",
             "f_intent", "f_modus", "f_anlage"},
            set(m),
        )


class DerVerfallIstJeDimensionVerschiedenTest(unittest.TestCase):
    """§10.4 — Faszination erlischt, wenn ihre Dimension erschoepfbar ist."""

    def test_ungewissheit_verfaellt_ueber_beruehrungen(self) -> None:
        """Wer oft genug hingesehen hat, weiss, wie es ausgeht."""
        frisch: float = fascination.qualitaet_verfall("ungewissheit", 1.0, 0, 0)
        oft:    float = fascination.qualitaet_verfall("ungewissheit", 1.0, 0, 20)
        self.assertAlmostEqual(1.0, frisch, 9)
        self.assertLess(oft, frisch)

    def test_ungewissheit_ignoriert_die_zeit(self) -> None:
        """Eine offene Frage wird nicht dadurch beantwortet, dass Zeit vergeht."""
        self.assertAlmostEqual(
            1.0, fascination.qualitaet_verfall("ungewissheit", 1.0, 3650, 0), 9,
        )

    def test_komplexitaet_verfaellt_ueber_die_zeit(self) -> None:
        lange: float = fascination.qualitaet_verfall("komplexitaet", 1.0, 3650, 0)
        self.assertLess(lange, 1.0)

    def test_komplexitaet_ignoriert_beruehrungen(self) -> None:
        """Sie erschoepft sich nicht durch Hinsehen — der Kern von §10.4."""
        self.assertAlmostEqual(
            1.0, fascination.qualitaet_verfall("komplexitaet", 1.0, 0, 500), 9,
        )

    def test_die_beiden_regime_sind_wirklich_getrennt(self) -> None:
        """Sonst waere die Unterscheidung eine Behauptung im Kommentar."""
        for dimension in QUALITAET_KANON:
            ueber_zeit = fascination.qualitaet_verfall(dimension, 1.0, 3650, 0)
            ueber_ber  = fascination.qualitaet_verfall(dimension, 1.0, 0, 500)
            if dimension in QUALITAET_VERFALL_UEBER_BERUEHRUNGEN:
                self.assertAlmostEqual(1.0, ueber_zeit, 9, dimension)
                self.assertLess(ueber_ber, 1.0, dimension)
            else:
                self.assertLess(ueber_zeit, 1.0, dimension)
                self.assertAlmostEqual(1.0, ueber_ber, 9, dimension)

    def test_der_boden_wird_nie_unterschritten(self) -> None:
        """Was verfaellt, ist die Zugkraft — nicht der Bestand der Eigenschaft."""
        tief: float = fascination.qualitaet_verfall("komplexitaet", 1.0, 10**9, 0)
        self.assertGreaterEqual(tief, QUALITAET_VERFALL_BODEN - 1e-9)

    def test_der_verfall_hebt_nie_an(self) -> None:
        """Er ist ein Verfall — die Nachbedingung ist [0, auspraegung]."""
        for tage in (0, 1, 10, 400):
            self.assertLessEqual(
                fascination.qualitaet_verfall("weite", 0.5, tage, 0), 0.5 + 1e-9,
            )

    def test_eine_unbekannte_dimension_meldet_sich(self) -> None:
        """Sie faellt in den Zeitverfall — den Regelfall — und wird gemeldet."""
        with self.assertLogs("ki_server.ei.fascination", "WARNING"):
            fascination.qualitaet_verfall("erhabenheit", 1.0, 0, 0)

    def test_das_ganze_profil_verfaellt_je_nach_regel(self) -> None:
        """Die Klammer darf die Trennung nicht auf halbem Weg vergessen."""
        profil = {"komplexitaet": 1.0, "ungewissheit": 1.0}
        verfallen = fascination.profil_verfallen(profil, tage=3650, beruehrungen=0)
        self.assertEqual(set(profil), set(verfallen))
        self.assertLess(verfallen["komplexitaet"], 1.0)
        self.assertAlmostEqual(1.0, verfallen["ungewissheit"], 9)


class DerStrangzugMisstDieLageDesTraegersTest(unittest.TestCase):
    """§10.3a — in der Mitte stark, am Rand schwach.

    Vorgabe des Eigentuemers (05.09.2026): *„Ein Strang ist ein kleiner
    Bereich im 768-dimensionalen Raum und hat ein Einflussgebiet. Liegt das
    Embedding eines Knotens darin, wird dafuer Faszination empfunden."*

    **Nicht zu verwechseln mit dem Praegungszug**, der die Lage des **Turns**
    misst und je Turn einen Wert liefert — alle Traeger bekommen denselben.
    """

    def test_naeher_zieht_staerker(self) -> None:
        self.assertGreater(
            fascination.strangzug(0.9, 5), fascination.strangzug(0.4, 5),
        )

    def test_ein_starker_strang_zieht_weiter(self) -> None:
        """Die Gravitation: dieselbe Naehe, mehr Faeden, mehr Zug."""
        self.assertGreater(
            fascination.strangzug(0.6, 20), fascination.strangzug(0.6, 1),
        )

    def test_ohne_strangbezug_ist_er_neutral(self) -> None:
        """1.0, **nicht 0** — Regel (a) aus §10.0 gilt auch hier."""
        self.assertEqual(1.0, fascination.strangzug(None, 0))

    def test_gegenlage_zieht_nicht_und_stoesst_nicht_ab(self) -> None:
        """Eine negative Naehe heisst: hat mit dieser Praegung nichts zu tun."""
        self.assertEqual(1.0, fascination.strangzug(-0.5, 7))

    def test_die_spanne_wird_eingehalten(self) -> None:
        for naehe in (0.0, 0.25, 0.5, 0.75, 1.0):
            for faeden in (0, 1, 5, 100):
                wert = fascination.strangzug(naehe, faeden)
                self.assertGreaterEqual(wert, 1.0)
                self.assertLessEqual(wert, 1.0 + 0.60 + 1e-9)

    def test_eine_unmoegliche_naehe_meldet_sich(self) -> None:
        with self.assertLogs("ki_server.ei.fascination", "ERROR"):
            fascination.strangzug(1.8, 5)

    def test_er_hebt_die_faszination_eines_nahen_traegers(self) -> None:
        """Der Zweck: Zwei gleich profilierte Traeger, verschiedene Lage."""
        mitte, _ = fascination.faszination(
            0.5, 1.0, 1.0, {"strangzug": fascination.strangzug(0.9, 7)},
        )
        rand, _ = fascination.faszination(
            0.5, 1.0, 1.0, {"strangzug": fascination.strangzug(0.2, 7)},
        )
        self.assertGreater(mitte, rand)


if __name__ == "__main__":
    unittest.main()
