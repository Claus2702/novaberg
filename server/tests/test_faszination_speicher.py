"""Zeugen: die Traegerseite der Faszination liest, was die Rechnung braucht.

Ziel: Anker-Zaehler und **verfallenes** Qualitaetsprofil je Traeger, und zwar
so, dass ein Aufrufer den Verfall nicht vergessen kann.

Diese Zeugen fassen den Produktivbestand nicht an: Der Speicher ist ersetzt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from config import POSTGRES_URL
from memory import fascination_store

MODUL: str = "memory.fascination_store"
AGENT_MODUL: str = "agents.synapsen_decay.agent"


def _verbindung(anker: list, profil: list) -> MagicMock:
    """Eine Datenbank, die auf die beiden Abfragen der Reihe nach antwortet."""
    zeiger = MagicMock()
    zeiger.fetchall.side_effect = [anker, profil]
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = zeiger
    verbindung = MagicMock(return_value=conn)
    return verbindung


class DerSpeicherLiestBeideHaelftenTest(unittest.TestCase):
    """Zwei Abfragen, nicht eine — ein JOIN verloere eine Haelfte stumm."""

    def test_ein_knoten_ohne_bruecke_behaelt_sein_profil(self) -> None:
        """Er hat kein `verbindung`-Ergebnis und trotzdem Qualitaeten."""
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([], [(11, "komplexitaet", 1.0, 0.0)])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertEqual(0, daten[11]["turns"])
        self.assertIn("komplexitaet", daten[11]["profil"])

    def test_ein_knoten_ohne_profil_behaelt_seine_zaehler(self) -> None:
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([(11, 3, 5, 2, 4)], [])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertEqual(3, daten[11]["tage"])
        self.assertEqual({}, daten[11]["profil"])

    def test_eine_leere_anfrage_oeffnet_keine_verbindung(self) -> None:
        """Ein Turn ohne gelesene Erinnerungen ist der Normalfall."""
        with patch(f"{MODUL}.psycopg2.connect") as verbindung:
            self.assertEqual({}, fascination_store.traegerdaten_lesen(POSTGRES_URL, []))
        verbindung.assert_not_called()


class UnbekannteHerkunftBleibtNoneTest(unittest.TestCase):
    """§10.2 — *unbekannt* ist nicht *vom Nutzer*."""

    def test_ohne_bekannte_herkunft_steht_none(self) -> None:
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([(11, 1, 1, 0, 0)], [])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertIsNone(daten[11]["eigenimpuls"])

    def test_mit_bekannter_herkunft_steht_der_anteil(self) -> None:
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([(11, 1, 4, 1, 4)], [])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertAlmostEqual(0.25, daten[11]["eigenimpuls"], 9)


class DerVerfallLaeuftImLesepfadTest(unittest.TestCase):
    """Sonst koennte ein zweiter Leser ihn vergessen (§10.4).

    Ein unverfallenes Profil ist von einem frischen nicht zu unterscheiden —
    und der Unterschied ist genau die Aussage der Groesse.
    """

    def test_das_profil_kommt_verfallen_zurueck(self) -> None:
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([], [(11, "komplexitaet", 1.0, 3650.0)])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertLess(daten[11]["profil"]["komplexitaet"], 1.0)

    def test_der_rohwert_steht_daneben(self) -> None:
        """Sonst ist nicht zu trennen, ob niedrig bewertet oder verfallen."""
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([], [(11, "komplexitaet", 1.0, 3650.0)])):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertEqual(1.0, daten[11]["roh_profil"]["komplexitaet"])

    def test_ungewissheit_verfaellt_ueber_die_beruehrungen_des_traegers(self) -> None:
        """Wer den Knoten ansieht, sieht seine Qualitaeten an."""
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([(11, 1, 20, 0, 0)],
                               [(11, "ungewissheit", 1.0, 0.0)])):
            viele = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([(11, 1, 1, 0, 0)],
                               [(11, "ungewissheit", 1.0, 0.0)])):
            wenige = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertLess(
            viele[11]["profil"]["ungewissheit"],
            wenige[11]["profil"]["ungewissheit"],
        )


class EineQualitaetAusserhalbDesKanonsWirdUebergangenTest(unittest.TestCase):
    """Und gemeldet — sonst rechnete die Faszination auf fremdem Vokabular."""

    def test_sie_faellt_heraus_und_meldet_sich(self) -> None:
        with patch(f"{MODUL}.psycopg2.connect",
                   _verbindung([], [(11, "erhabenheit", 1.0, 0.0)])), \
             self.assertLogs("ki_server.memory.fascination_store", "WARNING"):
            daten = fascination_store.traegerdaten_lesen(POSTGRES_URL, [11])
        self.assertEqual({}, daten[11]["profil"])


if __name__ == "__main__":
    unittest.main()


class DerBestandslaufMisstDieTraegerseiteAlleinTest(unittest.TestCase):
    """§10.6 — ohne Turn-Modulatoren, und das ist der Zweck.

    `[gemessen 05.09.2026]` spannen die sechs Modulatoren Faktor **16,2**, die
    Traegerseite nur **2,0**. Im Turn ist deshalb nicht zu trennen, ob ein
    hoher Wert vom Traeger oder von der Lage kommt.
    """

    def test_ein_bestand_ohne_profile_ist_kein_fehler(self) -> None:
        """Der Zustand vor dem ersten Profil-Lauf."""
        with patch(f"{MODUL}.psycopg2.connect", _verbindung([], [])) as _:
            ergebnis = fascination_store.bestandslauf(POSTGRES_URL)
        self.assertEqual(0, ergebnis["traeger"])
        self.assertIsNone(ergebnis["error"])

    def test_traeger_ohne_bindung_werden_gezaehlt(self) -> None:
        """Sie sind der heutige Regelfall und der Grund fuer die flache Reihe."""
        zeiger = MagicMock()
        # 1. die Traegerliste, 2. der Anker, 3. die Profile
        zeiger.fetchall.side_effect = [
            [(11,)],
            [],                                    # keine Bruecke -> Bindung 0
            [(11, "komplexitaet", 1.0, 0.0)],
        ]
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = zeiger
        with patch(f"{MODUL}.psycopg2.connect", MagicMock(return_value=conn)):
            ergebnis = fascination_store.bestandslauf(POSTGRES_URL)
        self.assertEqual(1, ergebnis["gerechnet"])
        self.assertEqual(1, ergebnis["ohne_bindung"])
        self.assertEqual(0.0, ergebnis["roh_max"])

    def test_ein_flacher_bestand_meldet_sich(self) -> None:
        """Sonst faellt es erst auf, wenn jemand die Werte ansieht."""
        zeiger = MagicMock()
        zeiger.fetchall.side_effect = [
            [(11,)], [], [(11, "komplexitaet", 1.0, 0.0)],
        ]
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = zeiger
        with patch(f"{MODUL}.psycopg2.connect", MagicMock(return_value=conn)), \
             self.assertLogs("ki_server.memory.fascination_store", "WARNING"):
            fascination_store.bestandslauf(POSTGRES_URL)

    def test_die_verteilung_wird_berichtet(self) -> None:
        """Ohne Minimum, Median und Maximum ist die Reihe nicht auswertbar."""
        zeiger = MagicMock()
        zeiger.fetchall.side_effect = [
            [(11,), (12,)],
            [(11, 3, 3, 1, 2), (12, 1, 1, 0, 1)],
            [(11, "komplexitaet", 1.0, 0.0), (12, "weite", 0.5, 0.0)],
        ]
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = zeiger
        with patch(f"{MODUL}.psycopg2.connect", MagicMock(return_value=conn)):
            ergebnis = fascination_store.bestandslauf(POSTGRES_URL)
        self.assertEqual(2, ergebnis["gerechnet"])
        self.assertIsNotNone(ergebnis["roh_median"])
        self.assertLessEqual(ergebnis["roh_min"], ergebnis["roh_max"])
        self.assertEqual(2, len(ergebnis["werte"]))


class DerTageslaufRuftDenBestandslaufTest(unittest.TestCase):
    """Die Verdrahtung — sie ist die Lehre vom 04.09.2026.

    Dort rief kein Zeuge den Knoten, nur die Funktion; der fehlende Aufruf
    blieb unbemerkt, und die Gegenprobe sagte 0 rot voraus.
    """

    def test_der_neunte_schritt_laeuft_und_protokolliert(self) -> None:
        from agents.base import AgentState
        from agents.synapsen_decay.agent import SynapsenDecayAgent

        leer: dict = {"error": None, "total_processed": 0, "deactivated_count": 0,
                      "deleted_count": 0, "verarbeitet": 0, "deaktiviert": 0}
        fasz: dict = {"traeger": 5, "gerechnet": 5, "ohne_bindung": 2,
                      "werte": {"11": 0.5}, "roh_min": 0.0, "roh_median": 0.2,
                      "roh_max": 0.5, "error": None}
        with patch(f"{AGENT_MODUL}.SYNAPSEN_DECAY_AKTIV", True), \
             patch(f"{AGENT_MODUL}.fascination_store.bestandslauf",
                   return_value=fasz) as gerufen, \
             patch(f"{AGENT_MODUL}.lzg_knoten.run_node_decay", return_value=leer), \
             patch(f"{AGENT_MODUL}.pipeline_log.delete_expired_entries",
                   return_value=leer), \
             patch(f"{AGENT_MODUL}.ShadowAuftragRepository.verfall_lauf",
                   return_value=leer), \
             patch(f"{AGENT_MODUL}.db_manager"), \
             patch(f"{AGENT_MODUL}.praegung.alle_faeden_nachfuehren",
                   return_value={"gefaltet": 0, "gesamt": 0, "error": None}), \
             patch(f"{AGENT_MODUL}.praegung.faeden_ohne_strang_zuordnen",
                   return_value=(0, 0)), \
             patch(f"{AGENT_MODUL}.praegung.alle_einfaerbungen",
                   return_value={"gerechnet": 0, "gesamt": 0, "je_sektor": {},
                                 "abstand_max": 0.0, "error": None}), \
             patch(f"{AGENT_MODUL}.quality_profile.profil_lauf",
                   return_value={"versucht": 0, "profiliert": 0,
                                 "gescheitert": 0, "traeger_gesamt": 0,
                                 "kanten_gesamt": 0, "error": None}), \
             patch.object(SynapsenDecayAgent, "_richtungen_protokollieren",
                          return_value=0), \
             patch.object(SynapsenDecayAgent, "_log_forensik") as forensik:
            zustand = SynapsenDecayAgent().invoke(
                AgentState(auftrag="", kontext={}),
            )

        gerufen.assert_called_once()
        self.assertEqual(
            5, zustand["ergebnis"]["faszination_bestand"]["gerechnet"],
            "Der Tageslauf ruft den Bestandslauf nicht oder verwirft sein "
            "Ergebnis — die Reihe ueber die Zeit entstuende nie",
        )
        phasen = [
            ruf[0][1].get("phase") for ruf in forensik.call_args_list
            if len(ruf[0]) > 1 and isinstance(ruf[0][1], dict)
        ]
        self.assertIn(
            "faszination_bestand", phasen,
            "Ohne Protokollzeile ist die Verteilung spaeter nicht auswertbar",
        )
