"""Tests: Riegel 1 — ob sie ueberhaupt zugeht (Bauteil D).

Ein Einwurf ist eine Zuwendung, die niemand erbeten hat. Eine Figur, die auf
Abstand haelt, tut das nicht — egal wie gut der Gedanke zum Thema passt. Der
Riegel entscheidet das **Ob**; die Haeufigkeit ist eine andere Groesse und hat
noch keine Schwelle.

Zeugen dieser Datei:

  * **Die Groesse ist die Haltung, nicht die Naehe-Achse der Landschaft.** Die
    Achse laege billig bereit und waere der falsche Weg: Eine dauerhaft
    distanzierte Figur duerfte dann einwerfen, sobald die Landschaft zufaellig
    warm ist. Der Riegel liest den **persistierten Haltungsstand**.
  * **Vier Gruende heissen „unbekannt", einer heisst „nein".** Nur
    `zuwendung_unter_schwelle` ist eine Aussage ueber die Figur; kein Stand,
    ein Stand ohne Rechnung, ein zu alter Stand und eine fehlende Naehe sind
    Aussagen ueber den Speicher. Alle vier blocken — **aber sie werden
    getrennt gezaehlt**, sonst sieht ein kaputter Speicher aus wie eine
    distanzierte Figur.
  * **Der erste Blocker entscheidet, die billigen Riegel werden trotzdem alle
    gerechnet.** Sonst verdeckt Riegel 1 den Riegel 2, und dessen Schwelle ist
    nie kalibrierbar — sichtbar wird das nie, weil ein Riegel ohne Daten wie
    ein Riegel ohne Faelle aussieht.
  * **Ein nicht gerechneter Riegel traegt eine Marke, keinen Leerwert.**

Konzept: novaberg-eigenzeit_k.md §2.5, §5.4.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import inspect
import unittest

from config import ZUWENDUNG_SCHWELLE, ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN
from memory.haltung import Haltungsstand
from services import shadow_delivery as delivery_modul
from services.pixie.riegel import (
    GRUENDE_UNBEKANNT,
    GRUND_KEIN_STAND,
    GRUND_NAEHE_FEHLT,
    GRUND_OHNE_RECHNUNG,
    GRUND_UNTER_SCHWELLE,
    GRUND_ZU_ALT,
    RIEGEL_KANON,
    Riegel,
    Riegelkette,
    zuwendung_pruefen,
)

JETZT: float = 1_000_000.0

# Die fuenf Groessen als Literal — aus dem Konzept, nicht aus dem Pruefobjekt.
FUENF: tuple[str, ...] = ("umfang", "fragen", "naehe", "waerme", "draengen")


def _stand(naehe: float, alter: float = 0.0, **abweichung: object) -> Haltungsstand:
    """Ein Haltungsstand mit einer bestimmten Naehe."""
    werte: dict[str, float] = {n: 0.5 for n in FUENF}
    werte["naehe"] = naehe
    felder: dict = {
        "gerechnet": True,
        "cluster":   "glut",
        "werte":     werte,
        "turn_id":   "t-1",
        "zeit":      JETZT - alter,
        "grund":     "",
    }
    felder.update(abweichung)
    return Haltungsstand(**felder)


class DieFigurEntscheidetDasObTest(unittest.TestCase):
    """Was der Riegel aus einer Haltung macht."""

    def test_eine_nahe_figur_darf_zugehen(self) -> None:
        """Der Normalfall — sie will, also wird gesucht."""
        riegel: Riegel = zuwendung_pruefen(_stand(0.91), JETZT)

        self.assertTrue(riegel.durchlaessig)
        self.assertEqual("", riegel.grund)
        self.assertAlmostEqual(0.91, riegel.wert, places=4)

    def test_eine_distanzierte_figur_geht_nicht_zu(self) -> None:
        """Die eigentliche Zusicherung des Bauteils."""
        riegel: Riegel = zuwendung_pruefen(_stand(0.20), JETZT)

        self.assertFalse(riegel.durchlaessig)
        self.assertEqual(GRUND_UNTER_SCHWELLE, riegel.grund)

    def test_auf_der_schwelle_kommt_sie_durch(self) -> None:
        """Der Randfall an der Kante, an der hier schon zweimal etwas stilllag."""
        riegel: Riegel = zuwendung_pruefen(_stand(ZUWENDUNG_SCHWELLE), JETZT)

        self.assertTrue(riegel.durchlaessig)

    def test_der_riegel_ist_immer_gerechnet(self) -> None:
        """Er kostet nichts und laeuft deshalb in jedem Fall."""
        for stand in (None, _stand(0.9), _stand(0.1)):
            with self.subTest(stand=stand):
                self.assertTrue(zuwendung_pruefen(stand, JETZT).gerechnet)


class UnbekanntIstNichtDistanziertTest(unittest.TestCase):
    """Vier Gruende heissen „unbekannt" — und keiner davon laesst durch."""

    def test_ohne_stand_wird_nicht_zugestellt(self) -> None:
        """Fuer dieses Paar hat nie eine Rechnung gelaufen."""
        riegel: Riegel = zuwendung_pruefen(None, JETZT)

        self.assertFalse(riegel.durchlaessig)
        self.assertEqual(GRUND_KEIN_STAND, riegel.grund)

    def test_ein_stand_ohne_rechnung_zaehlt_nicht_als_naehe(self) -> None:
        """Der letzte Turn hatte keine Landschaft — das ist keine Haltung."""
        riegel: Riegel = zuwendung_pruefen(
            _stand(0.9, gerechnet=False, werte={}), JETZT,
        )

        self.assertFalse(riegel.durchlaessig)
        self.assertEqual(GRUND_OHNE_RECHNUNG, riegel.grund)

    def test_ein_zu_alter_stand_beschreibt_eine_lage_die_es_nicht_gibt(self) -> None:
        """Ein Gespraech von letzter Woche sagt nichts ueber heute."""
        riegel: Riegel = zuwendung_pruefen(
            _stand(0.9, alter=ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN + 1.0), JETZT,
        )

        self.assertFalse(riegel.durchlaessig)
        self.assertEqual(GRUND_ZU_ALT, riegel.grund)

    def test_ein_stand_knapp_innerhalb_der_frist_traegt(self) -> None:
        """Der positive Zwilling — sonst prueft der Test nur das Blocken."""
        riegel: Riegel = zuwendung_pruefen(
            _stand(0.9, alter=ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN - 1.0), JETZT,
        )

        self.assertTrue(riegel.durchlaessig)

    def test_eine_fehlende_naehe_ist_ein_defekt_und_meldet_sich(self) -> None:
        """Vier von fuenf Groessen sind keine Haltung."""
        ohne_naehe: dict = {n: 0.5 for n in FUENF if n != "naehe"}

        with self.assertLogs("ki_server.pixie.riegel", level="ERROR"):
            riegel = zuwendung_pruefen(_stand(0.9, werte=ohne_naehe), JETZT)

        self.assertFalse(riegel.durchlaessig)
        self.assertEqual(GRUND_NAEHE_FEHLT, riegel.grund)

    def test_die_vier_gruende_sind_von_der_einen_aussage_getrennt(self) -> None:
        """Die Trennung ist der Zweck: Ein kaputter Speicher ist keine Figur.

        Ohne sie zaehlt eine Auswertung „sie wollte nicht", wo in Wahrheit
        nichts zu lesen war — und die Schwelle waere auf einem Ausfall
        kalibriert.
        """
        self.assertNotIn(GRUND_UNTER_SCHWELLE, GRUENDE_UNBEKANNT)
        self.assertEqual(4, len(GRUENDE_UNBEKANNT))
        for grund in (GRUND_KEIN_STAND, GRUND_OHNE_RECHNUNG,
                      GRUND_ZU_ALT, GRUND_NAEHE_FEHLT):
            self.assertIn(grund, GRUENDE_UNBEKANNT)


class DieKetteZaehltAlleTest(unittest.TestCase):
    """Der erste Blocker entscheidet — die uebrigen werden trotzdem vermerkt."""

    def test_der_erste_blocker_im_kanon_entscheidet(self) -> None:
        """Nicht der zuerst eingetragene, sondern der frueheste der Ordnung."""
        kette = Riegelkette()
        kette.gerechnet("thema",  False, 0.10)
        kette.gerechnet("wollen", False, 0.20)

        self.assertEqual("wollen", kette.entschieden_von())

    def test_ein_nicht_gerechneter_riegel_entscheidet_nie(self) -> None:
        """Er hat nichts gesehen — er kann nichts entschieden haben."""
        kette = Riegelkette()
        kette.nicht_gerechnet("frequenz", "nicht gebaut")
        kette.gerechnet("thema", False, 0.10)

        self.assertEqual("thema", kette.entschieden_von())

    def test_ohne_blocker_ist_die_kette_durchlaessig(self) -> None:
        """Der positive Zwilling."""
        kette = Riegelkette()
        kette.gerechnet("wollen", True, 0.91)

        self.assertTrue(kette.durchgelassen())
        self.assertEqual("", kette.entschieden_von())

    def test_jeder_riegel_des_kanons_steht_im_protokoll(self) -> None:
        """Auch der nie beruehrte — sonst haengt die Auswertung am Baustand."""
        kette = Riegelkette()
        kette.gerechnet("wollen", True, 0.91)

        protokoll: dict = kette.als_protokoll()

        self.assertEqual(set(RIEGEL_KANON), set(protokoll["riegel"]))

    def test_ein_nicht_erreichter_riegel_sieht_nicht_wie_ein_durchlass_aus(self) -> None:
        """Der Bauplan, der im Defektregister dieses Projekts sechsmal steht."""
        kette = Riegelkette()
        kette.gerechnet("wollen", False, 0.20)

        thema: dict = kette.als_protokoll()["riegel"]["thema"]

        self.assertFalse(thema["gerechnet"])
        self.assertIsNone(thema["durchlaessig"])
        self.assertNotEqual("", thema["grund"])

    def test_ein_fremder_name_wird_abgewiesen_und_gemeldet(self) -> None:
        """Ein stillschweigend aufgenommener Name erschiene als Riegel."""
        kette = Riegelkette()

        with self.assertLogs("ki_server.pixie.riegel", level="ERROR"):
            kette.gerechnet("stimmung", False, 0.1)

        self.assertEqual("", kette.entschieden_von())


class DieVerdrahtungTest(unittest.TestCase):
    """Der Zustellpfad ruft den Riegel — sonst ist der Bauteil tot und still.

    **Der schwaechste Zeuge dieser Datei, und das ist benannt.** Die
    Zustell-Schleife ist endlos und schlaeft fuenf Sekunden je Runde; sie ist
    nicht fahrbar. Geprueft wird deshalb die Verdrahtung am Quelltext. Die
    Gegenprobe dazu ist der Ausbau des Aufrufs — sie trifft, aber sie belegt
    nur, dass der Aufruf **dasteht**, nicht dass er wirkt.
    """

    def test_die_kette_wird_vor_der_uebergabe_gerechnet(self) -> None:
        """Riegel 1 steht vor der Suche, nicht dahinter."""
        quelle: str = inspect.getsource(delivery_modul.shadow_delivery_loop)

        self.assertIn("_riegelkette_pruefen", quelle)

    def test_die_kette_liest_den_haltungsstand(self) -> None:
        """Die Groesse ist die Haltung — nicht die Lage-Achse des Turns."""
        quelle: str = inspect.getsource(delivery_modul._riegelkette_pruefen)

        self.assertIn("haltung_lesen", quelle)
        self.assertIn("zuwendung_pruefen", quelle)

    def test_die_frequenz_wird_als_nicht_gebaut_vermerkt(self) -> None:
        """Riegel 2 fehlt, und das steht in den Daten statt in einem Kopf."""
        quelle: str = inspect.getsource(delivery_modul._riegelkette_pruefen)

        self.assertIn("nicht_gerechnet", quelle)
        self.assertIn("frequenz", quelle)


if __name__ == "__main__":
    unittest.main()
