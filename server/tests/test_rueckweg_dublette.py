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
    SATZ_MINDESTLAENGE,
    _bringt_neues,
    _saetze,
)

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
        self.assertFalse(_bringt_neues(SATZ_B, BESTAND))

    def test_der_ganze_absatz_woertlich_bringt_nichts(self):
        self.assertFalse(_bringt_neues(BESTAND, BESTAND))

    def test_zwei_bekannte_saetze_bringen_nichts(self):
        self.assertFalse(_bringt_neues(f"{SATZ_B} {SATZ_A}", BESTAND))


class EchteFundeLaufenDurchTest(unittest.TestCase):
    """Die Gegenrichtung — ein Riegel, der zu viel faengt, kostet Funde."""

    def test_ein_neuer_satz_kommt_durch(self):
        self.assertTrue(_bringt_neues(SATZ_NEU, BESTAND))

    def test_ein_neuer_satz_neben_einem_bekannten_kommt_durch(self):
        self.assertTrue(_bringt_neues(f"{SATZ_B} {SATZ_NEU}", BESTAND))

    def test_ein_leerer_bestand_haelt_nichts_auf(self):
        self.assertTrue(_bringt_neues(SATZ_NEU, ""))


class DerVergleichSiehtUeberMarkenHinwegTest(unittest.TestCase):
    """Sonst umginge jeder bereits markierte Satz den Riegel."""

    def test_derselbe_satz_mit_marke_gilt_als_vorhanden(self):
        self.assertFalse(_bringt_neues(SATZ_B, f"{SATZ_A} {SATZ_B} [i7>]"))

    def test_derselbe_satz_ohne_marke_gilt_als_vorhanden(self):
        self.assertFalse(_bringt_neues(f"{SATZ_B} [i9>]", BESTAND))

    def test_mehrfacher_leerraum_macht_keinen_unterschied(self):
        self.assertFalse(_bringt_neues(SATZ_B, BESTAND.replace(" ", "  ")))


class ZuKurzGiltAlsNeuTest(unittest.TestCase):
    """Ein Absatz ohne vergleichbaren Satz traegt kein Urteil."""

    def test_ein_kurzer_absatz_kommt_durch(self):
        kurz: str = "Das gilt auch hier."
        self.assertLess(len(kurz), SATZ_MINDESTLAENGE)
        self.assertTrue(_bringt_neues(kurz, BESTAND))

    def test_die_zerlegung_verwirft_zu_kurze_saetze(self):
        self.assertEqual(_saetze("Kurz. Auch kurz."), [])

    def test_die_zerlegung_findet_beide_saetze_des_bestands(self):
        self.assertEqual(len(_saetze(BESTAND)), 2)


if __name__ == "__main__":
    unittest.main()
