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

from agents.wissen_rueckweg.einarbeitung import (
    AEHNLICH_GENUG,
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

    def test_wer_ein_drittel_weglaesst_kommt_durch(self):
        """Die Grenze des Riegels, ausdruecklich festgehalten statt verschwiegen.

        Bei 0,65 laesst eine Fassung, die rund ein Drittel des Satzes
        weglaesst, den Riegel passieren — sie ist dann keine Umformulierung
        mehr, sondern eine kuerzere Aussage, und der Riegel kann nicht
        entscheiden, ob das Absicht ist. **Das ist bewusst die billigere
        Seite des Irrtums:** Ein durchgelassener Doppelgaenger ist ein
        sichtbarer doppelter Absatz; ein abgewiesener Fund ist fort, denn
        `steht_schon_da` reiht nicht wieder ein.
        """
        stark_gekuerzt: str = (
            "Die Umstellung des vegetativen Nervensystems senkt die "
            "Herzfrequenz ab."
        )
        self.assertLess(len(stark_gekuerzt) / len(SATZ_A), 0.70)
        self.assertTrue(bringt_neues(stark_gekuerzt, BESTAND))

    def test_andere_zeichensetzung_gilt_als_vorhanden(self):
        self.assertFalse(bringt_neues(SATZ_B.upper().replace(",", ""), BESTAND))

    def test_eine_echte_ergaenzung_kommt_trotz_aehnlichkeit_durch(self):
        """Derselbe Satzanfang, aber mit neuer Aussage am Ende."""
        ergaenzt: str = (
            f"{SATZ_A[:-1]}, waehrend die Atemfrequenz unveraendert bleibt "
            "und der Blutdruck erst mit Verzoegerung folgt."
        )
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


if __name__ == "__main__":
    unittest.main()
