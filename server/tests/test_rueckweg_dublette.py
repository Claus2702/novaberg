"""Tests: Ein eingearbeiteter Absatz muss etwas mitbringen, das noch fehlt.

Ziel: Der Rueckweg setzt keine Kopie neben ihr Original. Schlaegt das Modell
einen Absatz vor, der Satz fuer Satz schon im Text steht, ist das der Fall
*steht schon da* — und dafuer gibt es einen Ausgang, den das Modell nicht
zuverlaessig benutzt.

Hintergrund, gemessen am 24.08.2026 ueber 474 Wissensdateien: **17 woertlich
doppelte Absaetze und 7 unmittelbar wiederholte Saetze in 22 Dateien**, fuenf
der Dubletten in einem einzigen Durchgang entstanden. Der Schnitt setzt den
Absatz hinter den Anker; ist der Absatz die Fortsetzung, die dort ohnehin
schon steht, steht sie danach zweimal — mit der Marke dazwischen.

**Der Fehler ist still.** Die Paarungspruefung haelt (jede Marke hat ihren
Eintrag), die Datei waechst, die Version wird fortgeschrieben. Nur wer den
Absatz liest, sieht ihn doppelt.

Zeugen dieser Datei:
  * **Der Betriebsfall ist nachgebaut, nicht erfunden** — die Form stammt aus
    dem gemessenen Fall: ein Absatz aus zwei Saetzen, der zweite wird als
    „Fund" vorgeschlagen, der erste als Anker.
  * **Die Gegenrichtung wiegt gleich schwer.** Ein Riegel, der im Zweifel
    verwirft, verloere echte Funde; ueber die 232 Einarbeitungen des
    24.08.2026 schlug er **12** Mal an und liess **220** durch. Zwei Zeugen
    halten fest, dass ein neuer Satz durchkommt — auch neben bekannten.
  * **Marken duerfen den Vergleich nicht stoeren.** Derselbe Satz mit `[i7>]`
    und ohne ist derselbe Satz; sonst haette jede Wiederholung eines bereits
    markierten Satzes den Riegel umgangen.
  * **Zu kurze Absaetze gelten als neu.** Sie tragen kein Urteil, und ein
    Riegel, der sie verwirft, kostet mehr als er bringt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.wissen_rueckweg.einarbeitung import (
    AEHNLICH_GENUG,
    FRAGEN_AB,
    SATZ_MINDESTLAENGE,
    _aehnlichkeit,
    _bringt_neues,
    _saetze,
)


def bringt_neues(absatz: str, text: str) -> bool:
    """Nur das Urteil — die Naehe pruefen eigene Zeugen."""
    return _bringt_neues(absatz, text)[0]

#: Zwei Saetze, wie sie in einer Wissensdatei stehen — lang genug fuer das
#: Urteil, inhaltlich unverfaenglich.
SATZ_A: str = (
    "Die Umstellung des vegetativen Nervensystems auf parasympathische "
    "Dominanz senkt die Herzfrequenz messbar ab."
)
SATZ_B: str = (
    "Der beschriebene Mechanismus wirkt dabei unabhaengig von der bewussten "
    "Aufmerksamkeit der beteiligten Person."
)
SATZ_NEU: str = (
    "Eine Gegenprobe an ruhenden Probanden zeigt denselben Verlauf ohne "
    "jeden aeusseren Reiz."
)

BESTAND: str = f"{SATZ_A} {SATZ_B}"


class DerAbsatzMussEtwasMitbringenTest(unittest.TestCase):
    """Der gemessene Fall: der Fund steht schon da."""

    def test_ein_satz_der_schon_dasteht_bringt_nichts(self):
        self.assertFalse(bringt_neues(SATZ_B, BESTAND))

    def test_der_ganze_absatz_woertlich_bringt_nichts(self):
        self.assertFalse(bringt_neues(BESTAND, BESTAND))

    def test_zwei_bekannte_saetze_bringen_nichts(self):
        self.assertFalse(bringt_neues(f"{SATZ_B} {SATZ_A}", BESTAND))


class EchteFundeLaufenDurchTest(unittest.TestCase):
    """Die Gegenrichtung — ein Riegel, der zu viel faengt, kostet Funde."""

    def test_ein_neuer_satz_kommt_durch(self):
        self.assertTrue(bringt_neues(SATZ_NEU, BESTAND))

    def test_ein_neuer_satz_neben_einem_bekannten_kommt_durch(self):
        self.assertTrue(bringt_neues(f"{SATZ_B} {SATZ_NEU}", BESTAND))

    def test_ein_leerer_bestand_haelt_nichts_auf(self):
        self.assertTrue(bringt_neues(SATZ_NEU, ""))


class DerVergleichSiehtUeberMarkenHinwegTest(unittest.TestCase):
    """Sonst umginge jeder bereits markierte Satz den Riegel."""

    def test_derselbe_satz_mit_marke_gilt_als_vorhanden(self):
        self.assertFalse(bringt_neues(SATZ_B, f"{SATZ_A} {SATZ_B} [i7>]"))

    def test_derselbe_satz_ohne_marke_gilt_als_vorhanden(self):
        self.assertFalse(bringt_neues(f"{SATZ_B} [i9>]", BESTAND))

    def test_mehrfacher_leerraum_macht_keinen_unterschied(self):
        self.assertFalse(bringt_neues(SATZ_B, BESTAND.replace(" ", "  ")))


class ZuKurzGiltAlsNeuTest(unittest.TestCase):
    """Ein Absatz ohne vergleichbaren Satz traegt kein Urteil."""

    def test_ein_kurzer_absatz_kommt_durch(self):
        kurz: str = "Das gilt auch hier."
        self.assertLess(len(kurz), SATZ_MINDESTLAENGE)
        self.assertTrue(bringt_neues(kurz, BESTAND))

    def test_die_zerlegung_verwirft_zu_kurze_saetze(self):
        self.assertEqual(_saetze("Kurz. Auch kurz."), [])

    def test_die_zerlegung_findet_beide_saetze_des_bestands(self):
        self.assertEqual(len(_saetze(BESTAND)), 2)


class UmformulierungGiltAlsVorhandenTest(unittest.TestCase):
    """Der Grund fuer den Aehnlichkeitsvergleich — Gleichheit reichte nicht.

    Die erste Fassung dieses Riegels verlangte den exakten Wortlaut und fing
    damit **12 von 18** Doppelgaengern des Bestands. Die uebrigen sechs waren
    Umformulierungen desselben Satzes; ein umgestelltes Wort genuegte, um
    durchzukommen. Bei zweien sagte die *neue* Fassung sogar weniger als die
    alte — der Rueckweg haette Gehalt gegen eine aermere Kopie getauscht und
    beide stehen lassen.
    """

    def test_ein_umgestellter_satz_gilt_als_vorhanden(self):
        umgestellt: str = (
            "Die Umstellung des vegetativen Nervensystems senkt die "
            "Herzfrequenz messbar ab auf parasympathische Dominanz."
        )
        self.assertNotEqual(umgestellt, SATZ_A)
        self.assertFalse(bringt_neues(umgestellt, BESTAND))

    def test_eine_aermere_fassung_gilt_als_vorhanden(self):
        """Der teuerste Fall: die Kopie sagt WENIGER und kaeme trotzdem rein.

        Die Laenge ist am **gemessenen** Fall geeicht, nicht erfunden: Im
        Bestand steht eine Fassung mit 70 % der Zeichen des Originals bei
        Uebereinstimmung 0,72. Ein erster Entwurf dieses Zeugen liess ein
        Drittel weg, kam auf 0,61 und war damit haerter als jeder echte Fall
        — er haette eine Grenze behauptet, die der Riegel nicht zieht.
        """
        aermer: str = (
            "Die Umstellung des vegetativen Nervensystems auf "
            "parasympathische Dominanz senkt die Herzfrequenz ab."
        )
        self.assertLess(len(aermer), len(SATZ_A))
        self.assertGreater(len(aermer) / len(SATZ_A), 0.70)
        self.assertFalse(bringt_neues(aermer, BESTAND))

    @patch("agents.wissen_rueckweg.einarbeitung._ist_dasselbe_gesagt")
    def test_wer_ein_drittel_weglaesst_wird_gefragt_statt_gezaehlt(self, urteil):
        """Was die Zahl frueher entschied und heute nicht mehr entscheidet.

        Eine Fassung, die rund ein Drittel des Satzes weglaesst, liegt bei
        **0,61** — zwischen `FRAGEN_AB` und `AEHNLICH_GENUG`. Solange die
        Kennzahl allein urteilte, kam sie damit durch, und dieser Zeuge hielt
        genau das fest: *„wer ein Drittel weglaesst, kommt durch"*.

        **Seit dem 25.08.2026 stimmt der Satz nicht mehr**, und das ist der
        Zweck des Bandes: Ob eine kuerzere Fassung eine aermere Kopie oder
        eine eigene Aussage ist, kann keine Zeichenzahl entscheiden. Hier wird
        gefragt. Der Zeuge prueft deshalb die **Verdrahtung** — dass gefragt
        wird und wen die Antwort bindet —, nicht mehr das Ergebnis der Zahl.
        """
        stark_gekuerzt: str = (
            "Die Umstellung des vegetativen Nervensystems senkt die "
            "Herzfrequenz ab."
        )
        self.assertLess(len(stark_gekuerzt) / len(SATZ_A), 0.70)

        urteil.return_value = True                  # Modell: sagt dasselbe
        self.assertFalse(bringt_neues(stark_gekuerzt, BESTAND))
        self.assertEqual(urteil.call_count, 1)

        urteil.reset_mock()
        urteil.return_value = False                 # Modell: traegt Neues
        self.assertTrue(bringt_neues(stark_gekuerzt, BESTAND))
        self.assertEqual(urteil.call_count, 1)

    def test_andere_zeichensetzung_gilt_als_vorhanden(self):
        self.assertFalse(bringt_neues(SATZ_B.upper().replace(",", ""), BESTAND))

    @patch("agents.wissen_rueckweg.einarbeitung._ist_dasselbe_gesagt")
    def test_eine_echte_ergaenzung_kommt_trotz_aehnlichkeit_durch(self, urteil):
        """Derselbe Satzanfang, aber mit neuer Aussage am Ende — bei 0,60.

        Auch dieser Fall liegt im Band; die Zahl allein wuerde ihn nicht von
        einer Umformulierung trennen. **Genau das ist der gemessene Grund fuer
        das Band:** Im Bestand lag ein echter Doppelgaenger bei 0,452 und eine
        echte Ergaenzung bei 0,622 — der Doppelgaenger also unaehnlicher als
        der Fund.
        """
        ergaenzt: str = (
            f"{SATZ_A[:-1]}, waehrend die Atemfrequenz unveraendert bleibt "
            "und der Blutdruck erst mit Verzoegerung folgt."
        )
        urteil.return_value = False                 # Modell: traegt Neues
        self.assertTrue(bringt_neues(ergaenzt, BESTAND))


class DieNaeheWirdBerichtetTest(unittest.TestCase):
    """Ohne die Zahl im Log ist die Schwelle aus dem Betrieb nicht nachstellbar."""

    def test_bei_woertlicher_kopie_ist_die_naehe_eins(self):
        neu, naehe = _bringt_neues(SATZ_B, BESTAND)
        self.assertFalse(neu)
        self.assertAlmostEqual(naehe, 1.0, places=3)

    def test_bei_einem_fremden_satz_liegt_die_naehe_unter_der_schwelle(self):
        neu, naehe = _bringt_neues(SATZ_NEU, BESTAND)
        self.assertTrue(neu)
        self.assertLess(naehe, AEHNLICH_GENUG)

    def test_ohne_vergleichbaren_satz_ist_die_naehe_null(self):
        self.assertEqual(_bringt_neues("Kurz.", BESTAND), (True, 0.0))


class DieAehnlichkeitSelbstTest(unittest.TestCase):
    """Die Raender der Kennzahl, nicht nur ihre Mitte."""

    def test_derselbe_satz_ergibt_eins(self):
        self.assertEqual(_aehnlichkeit(SATZ_A, SATZ_A), 1.0)

    def test_zwei_leere_saetze_teilen_nicht_durch_null(self):
        self.assertEqual(_aehnlichkeit("", ""), 0.0)

    def test_grossschreibung_macht_keinen_unterschied(self):
        self.assertEqual(_aehnlichkeit(SATZ_A, SATZ_A.upper()), 1.0)

    def test_voellig_fremde_saetze_liegen_weit_unter_der_schwelle(self):
        fremd: str = "Der Bahnsteig war leer und der Zug hatte Verspaetung."
        self.assertLess(_aehnlichkeit(SATZ_A, fremd), AEHNLICH_GENUG)


#: Ein Satz, der dasselbe sagt wie SATZ_A, in anderen Worten.
#:
#: **Die Naehe ist am gemessenen Fall geeicht.** Der schwaechste nachgewiesene
#: Doppelgaenger des Bestandes liegt bei 0,452; dieser hier bei rund 0,54 und
#: damit im Band. Ein erster Entwurf tauschte fast jedes Wort und landete bei
#: **0,094** — weit unter dem Band und damit an dem Pfad vorbei, den er
#: pruefen sollte. Die Zusicherung in `setUp` hat ihn gefangen; ohne sie waere
#: der Zeuge gruen gewesen, ohne je einen Aufruf ausgeloest zu haben.
UMSCHRIEBEN: str = (
    "Der Uebergang des vegetativen Nervensystems in parasympathische Dominanz "
    "laesst die Herzfrequenz nachweisbar sinken."
)


class DasBandWirdGefragtTest(unittest.TestCase):
    """Der Pfad, den die Kennzahl nicht entscheiden kann.

    **Gemessen am 24.08.2026, und die Kennzahl ordnet die Faelle falsch:** Im
    Bestand lag ein echter Doppelgaenger bei **0,452** — zwei Saetze mit
    derselben Aussage und fast keinem gemeinsamen Wort — und eine echte
    Ergaenzung bei **0,622**. Der Doppelgaenger war also *unaehnlicher* als
    der Fund. Ein Nebensatz verschiebt den Wert weit genug, dass keine
    Schwelle beide trennt; zwischen `FRAGEN_AB` und `AEHNLICH_GENUG`
    entscheidet deshalb ein Aufruf.

    Diese Zeugen mocken das Urteil. Sie pruefen die **Verdrahtung** — dass
    gefragt wird, wen die Antwort bindet, und was bei ihrem Ausbleiben
    geschieht —, nicht die Urteilskraft des Modells.
    """

    def setUp(self):
        naehe = max(_aehnlichkeit(UMSCHRIEBEN, s) for s in _saetze(BESTAND))
        self.assertGreaterEqual(naehe, FRAGEN_AB, "Testsatz liegt unter dem Band")
        self.assertLess(naehe, AEHNLICH_GENUG, "Testsatz liegt ueber dem Band")

    @patch("agents.wissen_rueckweg.einarbeitung._ist_dasselbe_gesagt")
    def test_im_band_wird_gefragt(self, urteil):
        urteil.return_value = False
        bringt_neues(UMSCHRIEBEN, BESTAND)
        self.assertEqual(urteil.call_count, 1)

    @patch("agents.wissen_rueckweg.einarbeitung._ist_dasselbe_gesagt")
    def test_sagt_das_modell_dasselbe_faellt_der_absatz(self, urteil):
        urteil.return_value = True
        self.assertFalse(bringt_neues(UMSCHRIEBEN, BESTAND))

    @patch("agents.wissen_rueckweg.einarbeitung._ist_dasselbe_gesagt")
    def test_sagt_das_modell_neues_kommt_der_absatz_durch(self, urteil):
        urteil.return_value = False
        self.assertTrue(bringt_neues(UMSCHRIEBEN, BESTAND))

    @patch("agents.wissen_rueckweg.einarbeitung._ist_dasselbe_gesagt")
    def test_ohne_urteil_wird_eingearbeitet(self, urteil):
        """Ein ausgefallener Aufruf darf keinen Fund kosten."""
        urteil.return_value = None
        self.assertTrue(bringt_neues(UMSCHRIEBEN, BESTAND))

    @patch("agents.wissen_rueckweg.einarbeitung._ist_dasselbe_gesagt")
    def test_ueber_der_schwelle_wird_nicht_gefragt(self, urteil):
        """Eine woertliche Kopie braucht kein Urteil — und kostet keinen Aufruf."""
        self.assertFalse(bringt_neues(SATZ_B, BESTAND))
        self.assertEqual(urteil.call_count, 0)

    @patch("agents.wissen_rueckweg.einarbeitung._ist_dasselbe_gesagt")
    def test_unter_dem_band_wird_nicht_gefragt(self, urteil):
        self.assertTrue(bringt_neues(SATZ_NEU, BESTAND))
        self.assertEqual(urteil.call_count, 0)

    @patch("agents.wissen_rueckweg.einarbeitung._ist_dasselbe_gesagt")
    def test_ein_satz_mit_eigenem_gehalt_beendet_das_fragen(self, urteil):
        """Der erste Satz, der etwas mitbringt, macht den Absatz zum Fund."""
        urteil.return_value = False
        self.assertTrue(bringt_neues(f"{UMSCHRIEBEN} {SATZ_B}", BESTAND))
        self.assertEqual(urteil.call_count, 1)


if __name__ == "__main__":
    unittest.main()
