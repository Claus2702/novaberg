"""Tests: Die Haltung ueberlebt den Turn — und ein Ausfall loescht den Vorstand.

Die Haltung stand bis zum 15.08.2026 nur im Zustand des Durchlaufs. Ein
Hintergrunddienst ausserhalb des Graphen — die Zustellung — konnte sie nicht
sehen, und damit war der Zuwendungs-Riegel (`novaberg-eigenzeit_k.md` §2.5,
Bauteil D) nicht baubar: Er entscheidet **ob** Nova ueberhaupt zugeht, und die
Groesse dafuer ist die Haltung, nicht die Naehe-Achse der Landschaft.

**Der Speicher traegt den Zustand, nicht den Verlauf.** Die Messreihe liegt
weiterhin im `pipeline_log` — das Konzept des Haltungsraums verbietet in §2.0a
ausdruecklich, sie durch einen Redis-Schluessel zu ersetzen, weil ein Speicher,
den jeder Turn ueberschreibt, kein Protokoll ist. Genau deshalb ist er als
**Zustand** richtig: Der Riegel fragt nicht, wie es war, sondern wie es ist.

**Die scharfe Zusicherung ist die dritte:** Ein Turn ohne Rechnung hinterlaesst
**keinen** alten Stand, der aktuell aussieht. Das ist der benannte Fehler des
`gv:detail:`-Wegs — dort bleibt bei einem uebersprungenen Turn der Vorstand
ohne Kennzeichnung stehen, seit Chat 116 in der Fundliste. Ein Riegel auf einem
solchen Speicher entschiede nach der Lage von vorgestern, ohne dass es jemand
saehe.

Drei Faelle, drei Antworten — sie duerfen nicht auf einem Ergebnis liegen:

    kein Schluessel      nie gerechnet fuer dieses Paar   -> None
    gerechnet = False    letzter Turn hatte keine Lage    -> Stand mit Grund
    gerechnet = True     Werte gueltig, mit Alter         -> Stand mit Werten

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import time
import unittest
from unittest.mock import MagicMock, patch

import redis
from graph.nodes import haltung as haltung_modul
from graph.nodes.haltung import haltung_bestimmen
from memory.haltung import (
    HALTUNG_FELDER,
    Standkopf,
    haltung_lesen,
    haltung_schluessel,
    haltung_speichern,
)

# Novas Zuwendung zum Nutzer, gemessen am 31.07.2026 (Konzept §2.2a).
RAD_GEMESSEN: dict[str, float] = {
    "treue":          0.5,
    "aufmerksamkeit": 0.5,
    "wissbegier":     1.0,
    "wohlwollen":     1.0,
    "distanz":        0.5,
}

FUENF_GROESSEN: set[str] = {"umfang", "fragen", "naehe", "waerme", "draengen"}


class _Redis:
    """Ein Redis-Doppel, das genau die drei benutzten Befehle beherrscht.

    Kein MagicMock: Der Rundlauf ist der Gegenstand dieser Datei, und ein Mock
    gaebe zurueck, was man ihm vorher gesagt hat. Hier soll das Geschriebene
    tatsaechlich gelesen werden.
    """

    def __init__(self) -> None:
        """Ein leerer Speicher."""
        self.hashes: dict[str, dict[str, str]] = {}

    def hset(self, key: str, mapping: dict) -> int:
        """Setzt die uebergebenen Felder, wie Redis: bestehende bleiben."""
        ziel: dict[str, str] = self.hashes.setdefault(key, {})
        neu: int = sum(1 for feld in mapping if feld not in ziel)
        ziel.update({k: str(v) for k, v in mapping.items()})
        return neu

    def hgetall(self, key: str) -> dict[str, str]:
        """Liefert den Hash oder ein leeres Dict."""
        return dict(self.hashes.get(key, {}))


def _state(**felder: object) -> dict:
    """Ein Zustand, der fuer den Haltungs-Node ausreicht."""
    basis: dict = {
        "user_prompt":  "Wie entsteht ein Gammablitz?",
        "user_id":      "meister",
        "character_id": "nova",
        "turn_id":      "t-1",
        "gv_detail":    {"cluster": "glut"},
    }
    basis.update(felder)
    return basis


def _knoten_fahren(redis_doppel: _Redis, state: dict, rad: dict | None = None) -> dict:
    """Faehrt den Haltungs-Node gegen ein Redis-Doppel."""
    with (
        patch.object(haltung_modul, "redis_client", redis_doppel),
        patch(
            "graph.nodes.haltung.nutzer_gewichtung_rad_laden",
            return_value=(RAD_GEMESSEN if rad is None else rad, "destilliert"),
        ),
    ):
        return haltung_bestimmen(state, "postgresql://unbenutzt")


class DerStandUeberlebtDenTurnTest(unittest.TestCase):
    """Was der Knoten hinterlaesst, kann ein Fremder lesen."""

    def test_nach_dem_turn_steht_die_haltung_im_speicher(self) -> None:
        """Der Rundlauf: rechnen, dann von aussen lesen."""
        speicher = _Redis()
        _knoten_fahren(speicher, _state())

        stand = haltung_lesen(speicher, "meister", "nova")

        self.assertIsNotNone(stand)
        self.assertTrue(stand.gerechnet)
        self.assertEqual("glut", stand.cluster)
        self.assertEqual(FUENF_GROESSEN, set(stand.werte))

    def test_die_werte_kommen_als_zahlen_zurueck(self) -> None:
        """Redis speichert Zeichenketten. Ein Riegel vergleicht Zahlen."""
        speicher = _Redis()
        _knoten_fahren(speicher, _state())

        stand = haltung_lesen(speicher, "meister", "nova")

        for name, wert in stand.werte.items():
            self.assertIsInstance(wert, float, f"{name} ist keine Zahl")

    def test_der_stand_traegt_seinen_turn_und_sein_alter(self) -> None:
        """Der Stand sagt, aus welchem Turn er stammt und wie alt er ist.

        Ohne Alter ist ein Zustand von vorgestern von einem frischen nicht zu
        unterscheiden.
        """
        speicher = _Redis()
        _knoten_fahren(speicher, _state(turn_id="t-42"))

        stand = haltung_lesen(speicher, "meister", "nova")

        self.assertEqual("t-42", stand.turn_id)
        self.assertLess(stand.alter_sekunden(time.time()), 5.0)

    def test_der_schluessel_folgt_dem_paar(self) -> None:
        """Zwei Paare, zwei Staende — die Haltung gehoert einer Beziehung."""
        speicher = _Redis()
        _knoten_fahren(speicher, _state(user_id="meister"))
        _knoten_fahren(speicher, _state(user_id="falle", gv_detail={"cluster": "gewitter"}))

        self.assertEqual("glut",     haltung_lesen(speicher, "meister", "nova").cluster)
        self.assertEqual("gewitter", haltung_lesen(speicher, "falle",   "nova").cluster)


class EinAusfallLoeschtDenVorstandTest(unittest.TestCase):
    """Die scharfe Zusicherung — der benannte Fehler des `gv:detail:`-Wegs."""

    def test_ein_turn_ohne_landschaft_hinterlaesst_keine_alten_werte(self) -> None:
        """Erst rechnen, dann ausfallen: Der alte Stand darf nicht gelten.

        Bliebe er stehen, entschiede der Riegel nach der Lage des letzten
        gerechneten Turns — und niemand saehe, dass er das tut.
        """
        speicher = _Redis()
        _knoten_fahren(speicher, _state(turn_id="t-1"))
        self.assertTrue(haltung_lesen(speicher, "meister", "nova").gerechnet)

        _knoten_fahren(speicher, _state(turn_id="t-2", gv_detail={}))

        stand = haltung_lesen(speicher, "meister", "nova")
        self.assertFalse(stand.gerechnet)
        self.assertEqual({}, stand.werte)
        self.assertEqual("t-2", stand.turn_id)

    def test_der_ausfall_nennt_seinen_grund(self) -> None:
        """„Nicht gerechnet" ist keine Auskunft, solange der Grund fehlt."""
        speicher = _Redis()
        _knoten_fahren(speicher, _state(gv_detail={}))

        self.assertIn("Landschaft", haltung_lesen(speicher, "meister", "nova").grund)

    def test_ein_nicht_ladbares_rad_ist_ebenfalls_ein_ausfall(self) -> None:
        """Der zweite Weg in den Ausfall — auch er loescht den Vorstand."""
        speicher = _Redis()
        _knoten_fahren(speicher, _state(turn_id="t-1"))

        with (
            patch.object(haltung_modul, "redis_client", speicher),
            patch(
                "graph.nodes.haltung.nutzer_gewichtung_rad_laden",
                return_value=(None, "fehler"),
            ),
        ):
            haltung_bestimmen(_state(turn_id="t-2"), "postgresql://unbenutzt")

        stand = haltung_lesen(speicher, "meister", "nova")
        self.assertFalse(stand.gerechnet)
        self.assertEqual("t-2", stand.turn_id)


class DreiFaelleDreiAntwortenTest(unittest.TestCase):
    """Nie gerechnet, nicht gerechnet und gerechnet liegen nicht aufeinander."""

    def test_ohne_schluessel_gibt_es_keinen_stand(self) -> None:
        """`None` heisst: fuer dieses Paar hat noch nie eine Rechnung gelaufen."""
        self.assertIsNone(haltung_lesen(_Redis(), "unbekannt", "nova"))

    def test_ein_unlesbarer_wert_ist_ein_defekt_und_kein_leerfall(self) -> None:
        """Kaputt ist nicht dasselbe wie nie gerechnet — und es wird laut."""
        speicher = _Redis()
        haltung_speichern(
            speicher, Standkopf("meister", "nova", "t-1"),
            cluster = "glut",
            werte   = {
                "umfang": 0.5, "fragen": 0.5, "naehe": 0.5,
                "waerme": 0.5, "draengen": 0.5,
            },
            grund   = "",
        )
        speicher.hashes[haltung_schluessel("meister", "nova")]["naehe"] = "ziemlich nah"

        with self.assertLogs("ki_server.memory.haltung", level="ERROR"):
            stand = haltung_lesen(speicher, "meister", "nova")

        self.assertIsNotNone(stand)
        self.assertFalse(stand.gerechnet)
        self.assertIn("naehe", stand.grund)


class DerSpeicherSchreibtAlleFelderTest(unittest.TestCase):
    """Ein `hset` mit Teilmenge liesse die Zahlen des vorigen Turns stehen."""

    def test_jeder_schreibvorgang_setzt_jedes_feld(self) -> None:
        """Das ist die Bauart, die den Vorstand unmoeglich macht."""
        speicher = _Redis()
        haltung_speichern(
            speicher, Standkopf("meister", "nova", "t-1"),
            cluster = "", werte = {}, grund = "kein Rad",
        )

        geschrieben: dict = speicher.hashes[haltung_schluessel("meister", "nova")]

        self.assertEqual(set(HALTUNG_FELDER), set(geschrieben))


class DerSchreibfehlerToetetDenTurnNichtTest(unittest.TestCase):
    """Ein Speicherfehler ist eine Luecke in der Reihe, kein toter Turn."""

    def test_der_knoten_laeuft_weiter_und_meldet(self) -> None:
        """Die Haltung steht danach trotzdem im Zustand des Durchlaufs.

        Gefangen wird ausdruecklich nur ein **Speicherfehler**. Ein
        Programmierfehler soll laut sein — sonst ist er von einem
        ausgefallenen Redis nicht mehr zu unterscheiden.
        """
        kaputt = MagicMock()
        kaputt.hset.side_effect = redis.ConnectionError("Redis weg")

        with self.assertLogs("ki_server.memory.haltung", level="ERROR"):
            ergebnis: dict = _knoten_fahren(kaputt, _state())

        self.assertIn("haltung", ergebnis)


if __name__ == "__main__":
    unittest.main()
