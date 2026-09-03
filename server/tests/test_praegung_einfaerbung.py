"""Zeugen ueber die Einfaerbung: wie stark ein Faden noch **fuehlt**.

Ziel: Ein Faden aus einem negativen Sektor verliert seine Einfaerbung schneller
als ein gleich alter positiver — waehrend sein **Ausschlag** gleich bleibt.
Konzept §7.9, §8.4.

    ausschlag_aktuell : Faltung mit t                  → Ladung, Faszination
    einfaerbung       : Faltung mit t x sektor_faktor  → Ziele, LZG, EI-Calc

**Der Fading-Affect-Bias, und ausdruecklich nur auf der zweiten Zeile.** Walker
& Skowronski und Ritchie et al. (2016): Die emotionale Intensitaet negativer
Erinnerungen verblasst schneller als die positiver. Wirkte das auf die Ladung,
verloere Kriegsgeschichte ueber Monate gegen Gartenkraeuter und die
Valenzblindheit der Faszination fiele **durch Absicht** statt durch einen
Rechenfehler (§2.5). Das alte Unrecht zieht schwaecher am Gefuehl und gleich
stark an der Aufmerksamkeit.

Die Zusicherungen:

  1. **Eine Faltung, zwei Uhren** — bei Faktor 1,0 sind beide Groessen gleich.
  2. **Ein negativer Sektor verblasst schneller**, und zwar messbar in der
     Einfaerbung **und nicht** im Ausschlag. Das ist der Kern.
  3. **Die Zeit wirkt auf die Abstaende, nicht auf den Boden** — auch die
     Einfaerbung faellt nie unter `ausschlag_absolut x PRAEGUNG_BODEN`.
  4. **Eine Beruehrung hebt beide Stimmen**, die schneller verfallende bleibt
     trotzdem unter der langsameren.
  5. **Eine unbekannte Emotion ergibt die neutrale Achse**, nicht eine
     erfundene Beschleunigung — und meldet es.
  6. **Sektor 4 steht auf 1,0.** Der Bias spricht ueber Valenz, Ueberraschung
     traegt keine; alles darueber waere eine unbelegte Behauptung.
  7. **Der Tageslauf ruft die Reihe** — die Verdrahtung, nicht die Funktion.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from config import PRAEGUNG_BODEN, PRAEGUNG_SEKTOR_FAKTOR
from memory.praegung import einfaerbung_falten, sektor_faktor
from tests.test_praegung_strang import _Cursor, _mit_cursor

AGENT_MODUL: str = "agents.synapsen_decay.agent"

JETZT:     datetime = datetime(2026, 9, 3, 12, 0, tzinfo=timezone.utc)
VOR_60:    datetime = JETZT - timedelta(days=60)

#: Je eine Emotion aus einem positiven und einem negativen Sektor.
FREUDE:  str = "freude"        # Sektor 1, Faktor 1,0
TRAUER:  str = "traurigkeit"   # Sektor 5, Faktor 1,5


def _falten(emotion: str, entstanden: datetime = VOR_60,
            beruehrungen: list | None = None,
            absolut: float = 0.9) -> dict:
    return einfaerbung_falten(
        ausschlag_absolut = absolut,
        emotion           = emotion,
        entstanden_am     = entstanden,
        beruehrungen      = beruehrungen or [],
        jetzt             = JETZT,
    )


class EineFaltungZweiUhrenTest(unittest.TestCase):
    """Zusicherung 1 und 2 — der Kern der ganzen Groesse."""

    def test_bei_faktor_eins_sind_beide_stimmen_gleich(self) -> None:
        """Ein positiver Sektor laeuft auf derselben Uhr wie der Ausschlag."""
        teile = _falten(FREUDE)

        self.assertAlmostEqual(teile["faktor"], 1.0, places=9)
        self.assertAlmostEqual(
            teile["einfaerbung"], teile["ausschlag_aktuell"], places=12,
            msg="Bei Faktor 1,0 sind es zwei Rechnungen statt einer Kurve mit "
                "zwei Zeitachsen",
        )
        self.assertAlmostEqual(teile["abstand"], 0.0, places=12)

    def test_ein_negativer_sektor_verblasst_schneller(self) -> None:
        teile = _falten(TRAUER)

        self.assertGreater(teile["faktor"], 1.0)
        self.assertLess(
            teile["einfaerbung"], teile["ausschlag_aktuell"],
            "Der Fading-Affect-Bias wirkt nicht — das Gefuehl verblasst so "
            "langsam wie die Ladung",
        )
        self.assertGreater(teile["abstand"], 0.0)

    def test_der_ausschlag_bleibt_vom_sektor_unberuehrt(self) -> None:
        """**Die Trennung ist die Aussage.** Wirkte der Bias auf die Ladung,
        verloere Kriegsgeschichte ueber Monate gegen Gartenkraeuter."""
        positiv = _falten(FREUDE)
        negativ = _falten(TRAUER)

        self.assertAlmostEqual(
            positiv["ausschlag_aktuell"], negativ["ausschlag_aktuell"], places=12,
            msg="Der Sektorfaktor ist in den Ausschlag durchgeschlagen — genau "
                "das verbietet §2.5",
        )
        self.assertLess(negativ["einfaerbung"], positiv["einfaerbung"])


class DerBodenGiltFuerBeideTest(unittest.TestCase):
    """Zusicherung 3 — der Faktor streckt die Zeit, er senkt nicht den Boden."""

    def test_auch_die_einfaerbung_faellt_nie_unter_den_boden(self) -> None:
        uralt = JETZT - timedelta(days=100000)
        teile = _falten(TRAUER, entstanden=uralt, absolut=0.9)

        self.assertGreaterEqual(
            teile["einfaerbung"], 0.9 * PRAEGUNG_BODEN - 1e-9,
            "Ein Faden wird leiser, nie deaktiviert — der Boden gilt fuer beide "
            "Stimmen",
        )


class EineBeruehrungHebtBeideTest(unittest.TestCase):
    """Zusicherung 4 — die Auffuellung wirkt auf beiden Zeitachsen."""

    def test_die_beruehrung_hebt_und_die_ordnung_bleibt(self) -> None:
        ohne = _falten(TRAUER)
        mit  = _falten(TRAUER, beruehrungen=[JETZT - timedelta(days=5)])

        self.assertGreater(
            mit["einfaerbung"], ohne["einfaerbung"],
            "Eine Beruehrung hebt die Einfaerbung nicht",
        )
        self.assertLess(
            mit["einfaerbung"], mit["ausschlag_aktuell"],
            "Nach der Beruehrung steht das Gefuehl nicht mehr unter der Ladung",
        )


class DieUnbekannteEmotionTest(unittest.TestCase):
    """Zusicherung 5 und 6 — wo keine Aussage vorliegt, wird keine erfunden."""

    def test_ohne_sektor_laeuft_die_neutrale_achse_und_es_wird_gemeldet(self) -> None:
        with self.assertLogs("ki_server.praegung", level="WARNING") as protokoll:
            faktor, sektor = sektor_faktor("gibtsnicht")

        self.assertEqual((faktor, sektor), (1.0, None))
        self.assertIn("neutralen Zeitachse", "".join(protokoll.output))

    def test_sektor_vier_traegt_keine_beschleunigung(self) -> None:
        """Der Bias spricht ueber Valenz; Ueberraschung traegt keine."""
        self.assertAlmostEqual(PRAEGUNG_SEKTOR_FAKTOR[3], 1.0, places=9)

    def test_jeder_negative_sektor_liegt_ueber_eins(self) -> None:
        """Sektoren 3, 5, 6, 7 — Angst, Trauer, Enttaeuschung, Aerger."""
        for sektor in (3, 5, 6, 7):
            self.assertGreater(
                PRAEGUNG_SEKTOR_FAKTOR[sektor - 1], 1.0,
                f"Sektor {sektor} ist negativ und verblasst nicht schneller",
            )
        for sektor in (1, 2, 8):
            self.assertAlmostEqual(PRAEGUNG_SEKTOR_FAKTOR[sektor - 1], 1.0, places=9)


class DerBestandslaufTest(unittest.TestCase):
    """Die Reihe ueber den Bestand — Vollstaendigkeit ist die Zusicherung."""

    def test_gerechnet_und_gesamt_stehen_nebeneinander(self) -> None:
        from memory.praegung import alle_einfaerbungen
        zeilen = [
            (1, FREUDE, 0.9, VOR_60, []),
            (2, TRAUER, 0.9, VOR_60, []),
        ]
        with _mit_cursor(_Cursor([zeilen])):
            bilanz = alle_einfaerbungen("postgresql://nachgebildet", JETZT)

        self.assertEqual((bilanz["gerechnet"], bilanz["gesamt"]), (2, 2))
        self.assertIsNone(bilanz["error"])
        self.assertEqual(bilanz["je_sektor"], {1: 1, 5: 1})
        self.assertGreater(
            bilanz["abstand_max"], 0.0,
            "Der groesste Abstand ist null — kein Faden verblasst schneller, "
            "obwohl einer aus Sektor 5 kommt",
        )

    def test_ein_lesefehler_meldet_und_nimmt_den_tageslauf_nicht_mit(self) -> None:
        from memory.praegung import alle_einfaerbungen
        with patch("memory.praegung.psycopg2.connect", side_effect=RuntimeError("weg")):
            bilanz = alle_einfaerbungen("postgresql://nachgebildet", JETZT)

        self.assertEqual(bilanz["gesamt"], 0)
        self.assertIn("weg", bilanz["error"])


class DerTageslaufRuftDieReiheTest(unittest.TestCase):
    """Zusicherung 7 — die Verdrahtung, nicht die Funktion.

    Eine gebaute und ungerufene Funktion war in dieser Schicht binnen drei Tagen
    viermal der Befund.
    """

    def test_der_siebte_schritt_laeuft(self) -> None:
        from agents.base import AgentState
        from agents.synapsen_decay.agent import SynapsenDecayAgent

        leer: dict = {"error": None, "total_processed": 0, "deactivated_count": 0,
                      "deleted_count": 0, "verarbeitet": 0, "deaktiviert": 0}
        bilanz: dict = {"gerechnet": 3, "gesamt": 3, "je_sektor": {1: 3},
                        "abstand_max": 0.25, "error": None}
        with patch(f"{AGENT_MODUL}.SYNAPSEN_DECAY_AKTIV", True), \
             patch(f"{AGENT_MODUL}.lzg_knoten.run_node_decay", return_value=leer), \
             patch(f"{AGENT_MODUL}.pipeline_log.delete_expired_entries", return_value=leer), \
             patch(f"{AGENT_MODUL}.ShadowAuftragRepository.verfall_lauf", return_value=leer), \
             patch(f"{AGENT_MODUL}.db_manager"), \
             patch(f"{AGENT_MODUL}.praegung.alle_faeden_nachfuehren",
                   return_value={"gefaltet": 0, "gesamt": 0, "error": None}), \
             patch(f"{AGENT_MODUL}.praegung.faeden_ohne_strang_zuordnen",
                   return_value=(0, 0)), \
             patch.object(SynapsenDecayAgent, "_richtungen_protokollieren",
                          return_value=0), \
             patch(f"{AGENT_MODUL}.praegung.alle_einfaerbungen",
                   return_value=bilanz) as gerufen:
            zustand = SynapsenDecayAgent().invoke(AgentState(auftrag="", kontext={}))

        self.assertEqual(
            gerufen.call_count, 1,
            "Der Tageslauf rechnet die Einfaerbungen nicht — die Reihe, an der "
            "der Sektorfaktor kalibrierbar wird, entsteht nie",
        )
        self.assertEqual(
            zustand["ergebnis"]["praegung_einfaerbung"], bilanz,
            "Die Bilanz erreicht das Ergebnis des Laufs nicht",
        )


if __name__ == "__main__":
    unittest.main()
