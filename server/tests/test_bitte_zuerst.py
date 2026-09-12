"""Zeugen: Eine Bitte des Gegenuebers geht vor jeder Neugier — bei Wissensfragen am Rad entschieden.

Ziel (`F-GV-2`, Bauteil 4 und Nachtrag vom 12.09.2026): Bittet der Nutzer um etwas
Konkretes (`intent = task`), liefert die Antwort es zuerst. **Eine Wissensfrage
(`knowledge`) ist Pflicht** und wird ebenso zuerst beantwortet — ausser das
Zuwendungsrad des Paares gibt der Neugier Anlass: `wissbegier` liegt um mehr als
die Messunsicherheit (`GV_BITTE_RAD_ABSTAND`) ueber `pflicht`.

Entscheidung des Eigentuemers, woertlich: *„Die Wissensfragen sind eher Pflicht,
Neugier dann im Gegensatz dazu eher privater Natur. Ich wuerde es am Rad
festmachen, ob eines davon in einer Relation vorkommt, die anlass dazu gibt,
eines zu bevorzugen."*

**Die Grenzfaelle stehen mit Zahlen aus dem Bestand** (12.09.2026, Zuwendungsrad
Nova → Mensch): das produktive Paar 0,761 / 0,887, ein Paar mit ueberwiegender
Pflicht 0,88 / 0,85.

**Die Zusicherung ist eine Vorgabe im Prompt, nicht die Antwort.** Ob das Modell
ihr folgt, sagt nur eine Betriebsmessung (`labor/werkzeug/bitte_reihe.sh`).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from config import GV_BITTE_RAD_ABSTAND
from graph.nodes.gespraechsvektor import (
    _bitte_entscheiden,
    _gv_detail_bauen,
    _hypothese_destillieren,
)
from graph.nodes.verfasser import _gespraechsvektor_block
from graph.reiz import request_first

PRODUKTIV = {"pflicht": 0.7607, "wissbegier": 0.8873}
PFLICHT_VORN = {"pflicht": 0.88, "wissbegier": 0.85}


def zustand(intent: str, impuls: bool = False) -> dict:
    payload = {"reiz_herkunft": "eigener_impuls"} if impuls else {}
    return {
        "external": SimpleNamespace(emotion=SimpleNamespace(
            intent=intent, emotion="neutral", arousal=0.5, emotions_vector="",
            mode="alltag", relationship_dynamic="neutral")),
        "event_payload": payload,
        "user_prompt": "" if impuls else "Gib mir eine Liste der Messmethoden.",
        "eigener_gedanke": "Ein Gedanke" if impuls else "",
        "session_turns": [],
        "user_id": "mensch",
        "character_id": "figur",
        "turn_id": "t-bitte",
    }


class DieEntscheidung(unittest.TestCase):
    """`request_first` — rein, mit dem Rad als Eingang."""

    def test_eine_aufgabe_kommt_immer_zuerst(self) -> None:
        e = request_first(zustand("task"), {"pflicht": 0.0, "wissbegier": 1.0})
        self.assertEqual((e["zuerst"], e["grund"]), (True, "aufgabe"))

    def test_wissensfrage_beim_produktiven_paar_laesst_der_neugier_den_vorzug(self) -> None:
        """0,887 − 0,761 = 0,127 — ueber der Messunsicherheit, also Anlass."""
        e = request_first(zustand("knowledge"), PRODUKTIV)
        self.assertEqual((e["zuerst"], e["grund"]), (False, "neugier_hat_anlass"))
        self.assertAlmostEqual(e["abstand"], 0.1266)

    def test_wissensfrage_bei_ueberwiegender_pflicht_kommt_zuerst(self) -> None:
        e = request_first(zustand("knowledge"), PFLICHT_VORN)
        self.assertEqual((e["zuerst"], e["grund"]), (True, "pflicht"))

    def test_ein_abstand_auf_der_unsicherheit_ist_kein_anlass(self) -> None:
        rad = {"pflicht": 0.80, "wissbegier": 0.80 + GV_BITTE_RAD_ABSTAND}
        self.assertTrue(request_first(zustand("knowledge"), rad)["zuerst"])

    def test_knapp_darueber_ist_einer(self) -> None:
        rad = {"pflicht": 0.80, "wissbegier": 0.80 + GV_BITTE_RAD_ABSTAND + 0.01}
        self.assertFalse(request_first(zustand("knowledge"), rad)["zuerst"])

    def test_die_unsicherheit_ist_die_gemessene(self) -> None:
        """Median der Laufspanne beider Speichen je Erhebung, 97 Erhebungen: 0,05."""
        self.assertEqual(GV_BITTE_RAD_ABSTAND, 0.05)

    def test_gleichstand_und_nullrad_bleiben_pflicht(self) -> None:
        self.assertTrue(request_first(zustand("knowledge"), {"pflicht": 0.5, "wissbegier": 0.5})["zuerst"])
        self.assertTrue(request_first(zustand("knowledge"), {"pflicht": 0.0, "wissbegier": 0.0})["zuerst"])

    def test_ohne_lesbares_rad_bleibt_die_pflicht(self) -> None:
        for rad in (None, {}, {"pflicht": 0.2}, {"pflicht": True, "wissbegier": 0.9}):
            with self.subTest(rad=rad):
                e = request_first(zustand("knowledge"), rad)
                self.assertEqual((e["zuerst"], e["grund"]), (True, "pflicht_ohne_rad"))

    def test_andere_absichten_sind_keine_bitte(self) -> None:
        for intent in ("smalltalk", "creative", "personal", "meta", ""):
            with self.subTest(intent=intent):
                self.assertFalse(request_first(zustand(intent), PFLICHT_VORN)["zuerst"])

    def test_ein_impuls_ist_nie_eine_bitte(self) -> None:
        e = request_first(zustand("task", impuls=True), PFLICHT_VORN)
        self.assertEqual((e["zuerst"], e["grund"]), (False, "impuls"))

    def test_die_eingangswerte_stehen_in_der_entscheidung(self) -> None:
        e = request_first(zustand("knowledge"), PFLICHT_VORN)
        self.assertEqual((e["pflicht"], e["wissbegier"], e["intent"]), (0.88, 0.85, "knowledge"))


class DerGvKnotenLaedtDasRadNurBeiWissensfragen(unittest.TestCase):
    """`_bitte_entscheiden` — die eine Stelle, die das Rad fuer diese Frage liest."""

    def rufen(self, state: dict, rad=PRODUKTIV):
        with patch("graph.nodes.gespraechsvektor.nutzer_gewichtung_rad_laden",
                   return_value=(rad, "destilliert" if rad else "fehlt")) as laden, \
             patch("graph.nodes.gespraechsvektor.log_berechnung") as spur, \
             patch("graph.nodes.gespraechsvektor.logger") as log:
            e = _bitte_entscheiden(state)
        return e, laden, spur, log

    def test_bei_einer_wissensfrage_wird_das_rad_gelesen(self) -> None:
        e, laden, _, _ = self.rufen(zustand("knowledge"))
        self.assertEqual(laden.call_count, 1)
        self.assertFalse(e["zuerst"])

    def test_bei_einer_aufgabe_nicht(self) -> None:
        e, laden, _, _ = self.rufen(zustand("task"))
        self.assertEqual(laden.call_count, 0)
        self.assertTrue(e["zuerst"])

    def test_die_entscheidung_steht_in_der_spur(self) -> None:
        _, _, spur, _ = self.rufen(zustand("knowledge"))
        inhalt = spur.call_args.kwargs["inhalt"]
        self.assertEqual(inhalt["schritt"], "bitte_zuerst")
        self.assertEqual(inhalt["grund"], "neugier_hat_anlass")
        self.assertIn("abstand", inhalt)

    def test_ein_unlesbares_rad_ist_laut_und_bleibt_pflicht(self) -> None:
        e, _, _, log = self.rufen(zustand("knowledge"), rad=None)
        self.assertTrue(log.error.called)
        self.assertEqual(e["grund"], "pflicht_ohne_rad")


class DieEntscheidungStehtInGvDetail(unittest.TestCase):
    """Auf jedem Weg — auch dem, auf dem nicht vorausgedacht wird."""

    def lage(self) -> MagicMock:
        lage = MagicMock()
        lage.achsen = {"drive": 0.0}
        return lage

    def test_mit_entscheidung(self) -> None:
        detail = _gv_detail_bauen(self.lage(), "skip", 0, bitte={"zuerst": True, "grund": "pflicht"})
        self.assertEqual(detail["bitte_zuerst"], {"zuerst": True, "grund": "pflicht"})

    def test_der_knoten_gibt_sie_auf_allen_drei_wegen_weiter(self) -> None:
        """Skip, Laenge 0 und der gelaufene Weg — der Verfasser liest sie auf jedem."""
        import inspect

        from graph.nodes import gespraechsvektor as gv
        self.assertEqual(inspect.getsource(gv.gespraechsvektor).count("bitte=bitte"), 3)

    def test_ohne_entscheidung_steht_die_marke(self) -> None:
        detail = _gv_detail_bauen(self.lage(), "skip", 0)
        self.assertEqual(detail["bitte_zuerst"], {"zuerst": False, "grund": "nicht_entschieden"})


class DerGvPromptTraegtDieBitte(unittest.TestCase):
    """Der `[BITTE]`-Block steht genau bei einer Entscheidung *zuerst*, und nach den Luecken."""

    def prompt(self, bitte_zuerst: bool) -> str:
        erfasst: dict = {}

        def chat(request, timeout=0):
            erfasst["text"] = request.messages[-1]["content"]
            raise RuntimeError("genug gesehen")

        with patch("graph.nodes.gespraechsvektor.model_service.chat.submit_sync", side_effect=chat), \
             patch("graph.nodes.gespraechsvektor.logger"):
            try:
                _hypothese_destillieren(
                    zustand("knowledge"), max_laenge=2, resonanz_kontext="",
                    wissensluecken=[{"konzept": "Quarkmaterie", "quelle": "kzg", "relevanz": 0.3}],
                    strategie_aktiv=True, bitte_zuerst=bitte_zuerst,
                )
            except RuntimeError:
                pass
        return erfasst.get("text", "")

    def test_bei_zuerst_steht_der_block(self) -> None:
        text = self.prompt(True)
        self.assertIn("[BITTE]", text)
        self.assertIn("SPRUNG 1 erfuellt diese Bitte", text)

    def test_der_block_steht_nach_den_luecken(self) -> None:
        text = self.prompt(True)
        self.assertLess(text.index("[WISSENSLUECKEN]"), text.index("[BITTE]"))

    def test_ohne_zuerst_kein_block(self) -> None:
        text = self.prompt(False)
        self.assertNotIn("[BITTE]", text)
        self.assertIn("[WISSENSLUECKEN]", text)


class DerVerfasserLiestDieEntscheidung(unittest.TestCase):
    """Die Vorgabe im `[GESPRAECHSVEKTOR]`-Block — gelesen aus `gv_detail`, nicht neu entschieden."""

    SATZ = "Person B hat um etwas Konkretes gebeten. Person A liefert es zuerst"

    def block(self, bitte) -> str:
        state = zustand("knowledge")
        state["gv_detail"] = {"cluster": "werkstatt", "strategie": "Im", "vehikel": "frage",
                              "vorausdenken": "gelaufen"}
        if bitte is not None:
            state["gv_detail"]["bitte_zuerst"] = bitte
        with patch("graph.nodes.verfasser.logger"):
            return _gespraechsvektor_block(state)

    def test_bei_zuerst_steht_die_vorgabe(self) -> None:
        self.assertIn(self.SATZ, self.block({"zuerst": True, "grund": "pflicht"}))

    def test_bei_neugier_nicht(self) -> None:
        self.assertNotIn(self.SATZ, self.block({"zuerst": False, "grund": "neugier_hat_anlass"}))

    def test_ohne_entscheidung_nicht(self) -> None:
        self.assertNotIn(self.SATZ, self.block(None))

    def test_die_vorgabe_spricht_in_den_namen_des_verfassers(self) -> None:
        """Der Verfasser nennt die beiden Person A und Person B (`F-PROMPT-2`)."""
        block = self.block({"zuerst": True, "grund": "aufgabe"})
        vorgabe = block[block.index("Person B hat um etwas Konkretes"):]
        vorgabe = vorgabe[:vorgabe.index("Stelle.") + len("Stelle.")]
        for fremd in ("Nutzer", "Nova", " du ", " dir "):
            with self.subTest(fremd=fremd):
                self.assertNotIn(fremd, vorgabe)


if __name__ == "__main__":
    unittest.main()
