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
            [(11,)],                               # die Traegerliste
            [],                                    # keine Bruecke -> Bindung 0
            [(11, "komplexitaet", 1.0, 0.0)],      # das Profil
            [],                                    # kein Strangbezug
        ]
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = zeiger
        with patch(f"{MODUL}.psycopg2.connect", MagicMock(return_value=conn)):
            ergebnis = fascination_store.bestandslauf(POSTGRES_URL)
        self.assertEqual(1, ergebnis["gerechnet"])
        self.assertEqual(1, ergebnis["ohne_bindung"])
        self.assertEqual(1, ergebnis["ohne_strang"])
        self.assertEqual(0.0, ergebnis["roh_max"])

    def test_ein_flacher_bestand_meldet_sich(self) -> None:
        """Sonst faellt es erst auf, wenn jemand die Werte ansieht."""
        zeiger = MagicMock()
        zeiger.fetchall.side_effect = [
            [(11,)], [], [(11, "komplexitaet", 1.0, 0.0)], [],
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
            [(11, 7, 0.8, 5, 0.4)],                # nur 11 liegt bei einem Strang
        ]
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = zeiger
        with patch(f"{MODUL}.psycopg2.connect", MagicMock(return_value=conn)):
            ergebnis = fascination_store.bestandslauf(POSTGRES_URL)
        self.assertEqual(2, ergebnis["gerechnet"])
        self.assertEqual(
            1, ergebnis["ohne_strang"],
            "Ein Traeger ohne Strangbezug wird gezaehlt, nicht uebergangen",
        )
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
                      "ohne_strang": 1,
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

        # **Die Phase allein genuegt nicht.** Eine Zeile, die es gibt und die
        # gesuchte Zahl nicht traegt, sieht in jeder Zaehlung wie ein Beleg aus
        # — dieselbe Klasse wie die stumme Verwendungszeile: sechs Ausgaenge,
        # eine Zeile, kein Unterschied.
        zeile: dict = next(
            ruf[0][1] for ruf in forensik.call_args_list
            if len(ruf[0]) > 1 and isinstance(ruf[0][1], dict)
            and ruf[0][1].get("phase") == "faszination_bestand"
        )
        for feld in ("traeger", "gerechnet", "ohne_bindung", "ohne_strang",
                     "roh_min", "roh_median", "roh_max"):
            self.assertIn(
                feld, zeile,
                f"Die Buchfuehrung des Bestandslaufs verliert '{feld}' auf dem "
                f"Weg ins Protokoll — in der Reihe ueber Tage ist die Zahl "
                f"dann nicht mehr da",
            )
        self.assertEqual(
            1, zeile["ohne_strang"],
            "Ohne diese Zahl ist nicht ablesbar, ob der Strangzug (§10.3a) im "
            "Bestand ueberhaupt greift",
        )


class DieGelesenenTraegerTest(unittest.TestCase):
    """Die Traegerseite ueber die Knoten **eines Turns** — fuer den Haltungsraum.

    Gegenstand ist die **Auswahl und die Zusammenfassung**, nicht die Abfrage:
    Beide Leser sind ersetzt, damit der Zeuge ueber der Aggregation steht und
    nicht ueber SQL. Was die Abfragen selbst liefern, pruefen die Zeugen oben.
    """

    def _lauf(self, profile: dict, naehen: dict | None = None) -> dict:
        """Ruft die Funktion mit ersetzten Lesern."""
        daten: dict = {
            knoten_id: {"tage": 5, "turns": 9, "eigenimpuls": 2, "profil": profil}
            for knoten_id, profil in profile.items()
        }
        with patch(f"{MODUL}.traegerdaten_lesen", return_value=daten), \
             patch(f"{MODUL}.traeger_strangnaehe", return_value=naehen or {}):
            return fascination_store.faszination_der_gelesenen(
                POSTGRES_URL, list(profile)
            )

    def test_ohne_profilierten_traeger_ist_der_wert_none_und_nicht_null(self) -> None:
        """'Keine Bindung bekannt' und 'Bindung null' sind zwei Lagen.

        Nur die erste darf im Haltungsraum neutral wirken. Faelen beide auf
        0.0, machte ein Turn ohne Profil Nova so wortkarg wie einer ueber ein
        Thema, das sie langweilt.
        """
        ergebnis = self._lauf({11: {}, 12: {}})
        self.assertIsNone(ergebnis["faszination"])
        self.assertEqual(2, ergebnis["traeger"])
        self.assertEqual(0, ergebnis["mit_profil"])

    def test_der_hoechste_traeger_traegt_das_ergebnis(self) -> None:
        """Das Maximum, nicht das Mittel — ein starkes Thema unter schwachen.

        Die Gegenprobe steckt in den Zahlen: Das Mittel der beiden Werte laege
        unter dem hoechsten, und der Zeuge wuerde rot.
        """
        ergebnis = self._lauf({
            21: {"komplexitaet": 1.0, "ungewissheit": 1.0},
            22: {"komplexitaet": 0.1},
        })
        self.assertEqual(2, ergebnis["mit_profil"])
        werte = [ergebnis["werte"]["21"], ergebnis["werte"]["22"]]
        self.assertEqual(ergebnis["faszination"], max(werte))
        self.assertGreater(max(werte), sum(werte) / len(werte))

    def test_ein_traeger_ohne_profil_senkt_das_ergebnis_nicht(self) -> None:
        """Er faellt aus der Auswahl, er geht nicht als Null ein."""
        allein = self._lauf({31: {"komplexitaet": 0.8}})
        gemischt = self._lauf({31: {"komplexitaet": 0.8}, 32: {}})
        self.assertEqual(allein["faszination"], gemischt["faszination"])
        self.assertEqual(1, gemischt["mit_profil"])
        self.assertEqual(2, gemischt["traeger"])

    def test_ein_turn_ohne_gelesene_erinnerungen_oeffnet_keine_verbindung(self) -> None:
        """Der Normalfall darf nichts kosten."""
        with patch(f"{MODUL}.psycopg2.connect") as verbindung:
            ergebnis = fascination_store.faszination_der_gelesenen(POSTGRES_URL, [])
        verbindung.assert_not_called()
        self.assertIsNone(ergebnis["faszination"])
        self.assertEqual(0, ergebnis["traeger"])

    def test_der_wert_liegt_in_der_spanne_der_groesse(self) -> None:
        """Nachbedingung der Faszination: [0, 1]. Der Haltungsraum verlaesst sich darauf."""
        ergebnis = self._lauf(
            {41: {name: 1.0 for name in ("komplexitaet", "ungewissheit")}},
            {41: {"naehe": 0.9, "faden_zahl": 8}},
        )
        self.assertIsNotNone(ergebnis["faszination"])
        self.assertGreaterEqual(ergebnis["faszination"], 0.0)
        self.assertLessEqual(ergebnis["faszination"], 1.0)
