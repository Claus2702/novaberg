"""Tests: Riegel 2 — ob sie gerade dran ist (Bauteil D).

**Ein Schalter, kein Frequenzmass.** Hat Nova gerade die Initiative, darf ein
Impuls kommen; hatte der Mensch sie, nicht. Mehr entscheidet er nicht — *was*
und *wie viel* durchkommt, entscheiden die uebrigen Riegel.

Die Entscheidung vom 15.08.2026 hat eine Messung im Ruecken. Ueber sechs Paare
mit je mindestens zwanzig Turns spannen die Paar-Mediane des Fuehrungsmasses
0,318, waehrend ein einzelnes Paar im Mittel 1,436 durchlaeuft; gegluettet
ueber zwanzig Turns steigt das Verhaeltnis nur von 0,22 auf 0,38. **Das
Fuehrungsmass traegt keine Frequenz je Paar** — aber genau die Schwankung im
Paar ist das, was ein Schalter auf den Moment braucht.

Zeugen dieser Datei:

  * **Die Schwelle ist die vorhandene.** `ei/dreischicht.py` macht aus
    demselben Mass seit Langem ein Bit; Riegel 2 ruft dieselbe Funktion mit
    derselben Konstante. Eine zweite Schwelle daneben hiesse, dass zwei
    Stellen dasselbe Wort verschieden lesen.
  * **Der Ausfall schliesst den Schalter, er oeffnet ihn nicht.** Das ist die
    Gegenprobe zur naheliegenden Bauart: `dreischicht.py` setzt bei fehlendem
    Mass **Bit 1** — *Nova fuehrt* —, weil eine Achse immer ein Bit braucht.
    Wer `achsen["initiative"]` in den Riegel haengte, erbte diese Umkehrung
    und oeffnete im Moment des Ausfalls.
  * **Riegel 1 verdeckt Riegel 2 nicht.** Weder in der Kette (beide werden
    gerechnet) noch im Speicher: Eine ausgefallene Haltung darf das
    Fuehrungsmass nicht mit ausloeschen, sonst ist dessen Verteilung nie
    kalibrierbar.
  * **`frequenz` ist Pflicht-Riegel.** Seit die stuendliche Decke gefallen
    ist, ist ein nicht gerechneter Riegel 2 nicht mehr eine Luecke in den
    Daten, sondern das Fehlen der einzigen Begrenzung, die den Zeitpunkt noch
    beurteilt.

Konzept: novaberg-eigenzeit_k.md §2.5, §5.4.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import GV_INITIATIVE_SCHWELLE, ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN
from ei.initiative import initiative_bit
from memory.haltung import Haltungsstand
from services.pixie.riegel import (
    GRUENDE_UNBEKANNT_FREQUENZ,
    GRUND_INITIATIVE_FEHLT,
    GRUND_KEIN_STAND,
    GRUND_MENSCH_FUEHRT,
    GRUND_ZU_ALT,
    RIEGEL_PFLICHT,
    Riegel,
    Riegelkette,
    initiative_pruefen,
    zuwendung_pruefen,
)

JETZT: float = 1_000_000.0

FUENF: tuple[str, ...] = ("umfang", "fragen", "naehe", "waerme", "draengen")

# Zwei Werte beiderseits der Schwelle, aus ihr abgeleitet statt hingeschrieben:
# Ein Literal hier waere beim naechsten Kalibrierlauf still falsch.
SIE_TREIBT:    float = GV_INITIATIVE_SCHWELLE - 0.30
MENSCH_TREIBT: float = GV_INITIATIVE_SCHWELLE + 0.30


def _stand(
    initiative: float | None,
    alter:      float = 0.0,
    **abweichung: object,
) -> Haltungsstand:
    """Ein Haltungsstand mit einem bestimmten Fuehrungsmass."""
    felder: dict = {
        "gerechnet": True,
        "cluster":   "glut",
        "werte":     {n: 0.5 for n in FUENF},
        "turn_id":   "t-1",
        "zeit":      JETZT - alter,
        "grund":     "",
        "initiative":       initiative,
        "initiative_grund": "" if initiative is not None else "ohne_wert",
    }
    felder.update(abweichung)
    return Haltungsstand(**felder)


class DerSchalterTest(unittest.TestCase):
    """Was der Riegel aus einem Fuehrungsmass macht."""

    def test_wenn_sie_treibt_darf_ein_impuls_kommen(self) -> None:
        """Der Normalfall — sie ist dran."""
        riegel: Riegel = initiative_pruefen(_stand(SIE_TREIBT), JETZT)

        self.assertTrue(riegel.durchlaessig)
        self.assertEqual("", riegel.grund)
        self.assertAlmostEqual(SIE_TREIBT, riegel.wert, places=4)

    def test_wenn_der_mensch_treibt_kommt_keiner(self) -> None:
        """Die eigentliche Zusicherung des Riegels."""
        riegel: Riegel = initiative_pruefen(_stand(MENSCH_TREIBT), JETZT)

        self.assertFalse(riegel.durchlaessig)
        self.assertEqual(GRUND_MENSCH_FUEHRT, riegel.grund)

    def test_das_vorzeichen_steht_in_der_bauart(self) -> None:
        """Hoch heisst *der Mensch* treibt — und darf die Rate nicht heben.

        Der Zeuge gegen die Verwechslung, vor der das Konzept ausdruecklich
        warnt: Wer das Mass als „ihr Antrieb" liest, baut den Riegel verkehrt
        herum ein, und der Fehler waere still, weil beide Richtungen plausible
        Zahlen liefern.
        """
        hoch: Riegel = initiative_pruefen(_stand(+0.90), JETZT)
        tief: Riegel = initiative_pruefen(_stand(-0.90), JETZT)

        self.assertFalse(hoch.durchlaessig, "hoch = der Mensch treibt = zu")
        self.assertTrue(tief.durchlaessig,  "tief = sie treibt = offen")

    def test_die_schwelle_ist_die_vorhandene_und_keine_zweite(self) -> None:
        """Riegel und Achse lesen dasselbe Wort gleich.

        Kein Vergleich gegen ein Literal: Geprueft wird, dass der Riegel
        **dieselbe Funktion mit derselben Konstante** anwendet. Zoege jemand
        eine eigene Schwelle ein, liefe dieser Zeuge auf.
        """
        for wert in (-0.90, -0.30, GV_INITIATIVE_SCHWELLE, 0.0, +0.30, +0.90):
            with self.subTest(wert=wert):
                erwartet: bool = initiative_bit(wert, GV_INITIATIVE_SCHWELLE) == 1
                self.assertEqual(
                    erwartet, initiative_pruefen(_stand(wert), JETZT).durchlaessig,
                )

    def test_auf_der_schwelle_ist_sie_dran(self) -> None:
        """Der Randfall an der Kante — `initiative_bit` vergleicht strikt groesser."""
        riegel: Riegel = initiative_pruefen(_stand(GV_INITIATIVE_SCHWELLE), JETZT)

        self.assertTrue(riegel.durchlaessig)


class UnbekanntIstNichtDasselbeWieInOrdnungTest(unittest.TestCase):
    """Drei Gruende heissen „unbekannt", einer heisst „nein"."""

    def test_kein_stand_blockt(self) -> None:
        """Ein Paar ohne Historie ist kein Freibrief."""
        riegel: Riegel = initiative_pruefen(None, JETZT)

        self.assertFalse(riegel.durchlaessig)
        self.assertEqual(GRUND_KEIN_STAND, riegel.grund)

    def test_ein_zu_alter_stand_blockt(self) -> None:
        """Wer gestern fuehrte, fuehrt heute nicht notwendig."""
        alt: float = ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN + 1.0
        riegel: Riegel = initiative_pruefen(_stand(SIE_TREIBT, alter=alt), JETZT)

        self.assertFalse(riegel.durchlaessig)
        self.assertEqual(GRUND_ZU_ALT, riegel.grund)

    def test_ein_fehlendes_mass_blockt(self) -> None:
        """Die Gegenprobe zur Umkehrung.

        `ei/dreischicht.py` setzt bei fehlendem Mass Bit 1 — *Nova fuehrt*.
        Wuerde der Riegel das Achsen-Bit lesen statt des rohen Wertes, waere
        dieser Fall ein **Durchlass**: Der Schalter ginge im Moment des
        Ausfalls auf. Genau das darf er nicht.
        """
        riegel: Riegel = initiative_pruefen(_stand(None), JETZT)

        self.assertFalse(riegel.durchlaessig)
        self.assertEqual(GRUND_INITIATIVE_FEHLT, riegel.grund)

    def test_die_unbekannten_gruende_sind_getrennt_gezaehlt(self) -> None:
        """Ein kaputter Speicher darf nicht wie ein fuehrender Mensch aussehen."""
        self.assertIn(GRUND_KEIN_STAND, GRUENDE_UNBEKANNT_FREQUENZ)
        self.assertIn(GRUND_ZU_ALT, GRUENDE_UNBEKANNT_FREQUENZ)
        self.assertIn(GRUND_INITIATIVE_FEHLT, GRUENDE_UNBEKANNT_FREQUENZ)
        self.assertNotIn(GRUND_MENSCH_FUEHRT, GRUENDE_UNBEKANNT_FREQUENZ)

    def test_der_riegel_ist_immer_gerechnet(self) -> None:
        """Er kostet nichts und laeuft deshalb in jedem Fall."""
        for stand in (None, _stand(SIE_TREIBT), _stand(MENSCH_TREIBT), _stand(None)):
            with self.subTest(stand=stand):
                self.assertTrue(initiative_pruefen(stand, JETZT).gerechnet)


class RiegelEinsVerdecktRiegelZweiNichtTest(unittest.TestCase):
    """Weder im Speicher noch in der Kette."""

    def test_eine_ausgefallene_haltung_loescht_das_fuehrungsmass_nicht(self) -> None:
        """Der Zeuge auf die Unabhaengigkeit der beiden Messungen.

        Ein Turn, in dem das Rad nicht ladbar war, hat keine Haltung — sein
        Fuehrungsmass hat er trotzdem. Haengte der Riegel an `gerechnet`,
        bekaeme Riegel 2 fuer jeden solchen Turn keine Daten, und seine
        Verteilung waere nie kalibrierbar.
        """
        ohne_haltung = _stand(
            SIE_TREIBT, gerechnet=False, werte={}, grund="Rad nicht ladbar",
        )

        riegel: Riegel = initiative_pruefen(ohne_haltung, JETZT)

        self.assertTrue(riegel.durchlaessig)
        self.assertAlmostEqual(SIE_TREIBT, riegel.wert, places=4)

    def test_riegel_eins_blockt_und_riegel_zwei_traegt_trotzdem_seinen_wert(self) -> None:
        """Die billigen Riegel werden alle gerechnet, auch nach einem Blocker."""
        stand = _stand(SIE_TREIBT)
        stand = Haltungsstand(**{**stand.__dict__, "werte": {**stand.werte, "naehe": 0.05}})

        kette = Riegelkette()
        kette.aufnehmen(zuwendung_pruefen(stand, JETZT))
        kette.aufnehmen(initiative_pruefen(stand, JETZT))

        protokoll: dict = kette.als_protokoll()

        self.assertEqual("wollen", protokoll["entschieden_von"])
        self.assertTrue(protokoll["riegel"]["frequenz"]["gerechnet"])
        self.assertAlmostEqual(
            SIE_TREIBT, protokoll["riegel"]["frequenz"]["wert"], places=4,
        )


class DieKetteOhneRiegelZweiIstKeinUrteilTest(unittest.TestCase):
    """Seit dem Fall der stuendlichen Decke traegt er die Begrenzung mit."""

    def test_frequenz_ist_pflicht_riegel(self) -> None:
        """Sonst waere sein Ausfall das Fehlen jeder Zeitbeurteilung."""
        self.assertIn("frequenz", RIEGEL_PFLICHT)

    def test_eine_kette_ohne_frequenz_laesst_nicht_durch(self) -> None:
        """Auch dann nicht, wenn Riegel 1 zufrieden ist."""
        kette = Riegelkette()
        kette.aufnehmen(zuwendung_pruefen(_stand(SIE_TREIBT), JETZT))

        self.assertFalse(kette.vollstaendig())
        self.assertFalse(kette.durchgelassen())
        self.assertIn("frequenz", kette.fehlende_pflicht())

    def test_mit_beiden_riegeln_kommt_sie_durch(self) -> None:
        """Die Gegenrichtung — ein Riegel, der nur blockt, ist kein Riegel."""
        stand = _stand(SIE_TREIBT)

        kette = Riegelkette()
        kette.aufnehmen(zuwendung_pruefen(stand, JETZT))
        kette.aufnehmen(initiative_pruefen(stand, JETZT))

        self.assertTrue(kette.vollstaendig())
        self.assertTrue(kette.durchgelassen())


if __name__ == "__main__":
    unittest.main()
