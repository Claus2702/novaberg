"""Zeugen: Eine Bitte des Gegenuebers geht vor jeder Neugier (`F-GV-2`, Bauteil 4).

Ziel: Bittet der Nutzer um etwas Konkretes (`intent = task`), erfahren GV-Knoten
und Verfasser, dass die Antwort es zuerst liefert; Luecken und offene Fragen
duerfen danach anschliessen, nicht an seiner Stelle. `[gemessen 12.09.2026]` Vier
Bitten um einen Vorschlag in Folge bekamen vier Gegenfragen — der GV-Prompt
kannte die Absicht nicht und forderte daneben, Luecken einzubringen.

**Die Zusicherung ist eine Vorgabe im Prompt, nicht die Antwort.** Ob das Modell
ihr folgt, sagt nur eine Betriebsmessung (`labor/werkzeug/bitte_reihe.sh`).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from graph.nodes.gespraechsvektor import _hypothese_destillieren
from graph.nodes.verfasser import _gespraechsvektor_block
from graph.reiz import REQUEST_INTENTS, is_request


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
    }


class DieBitteIstErkennbar(unittest.TestCase):
    """`is_request` — eine Auskunft fuer beide Stufen."""

    def test_task_ist_eine_bitte(self) -> None:
        self.assertTrue(is_request(zustand("task")))

    def test_wissensfrage_ist_hier_keine(self) -> None:
        """Am Wortlaut der Entscheidung: nur `task`. `knowledge` ist offen, nicht vergessen."""
        self.assertFalse(is_request(zustand("knowledge")))
        self.assertEqual(REQUEST_INTENTS, frozenset({"task"}))

    def test_ein_impuls_ist_nie_eine_bitte(self) -> None:
        """Auf einem Impuls ist `external` eine Kopie von Novas Zustand."""
        self.assertFalse(is_request(zustand("task", impuls=True)))

    def test_ohne_perzeption_keine_bitte(self) -> None:
        self.assertFalse(is_request({"event_payload": {}}))


class DerGvPromptTraegtDieBitte(unittest.TestCase):
    """Der `[BITTE]`-Block steht genau bei einer Bitte, und nach den Luecken."""

    def prompt(self, state: dict) -> str:
        erfasst: dict = {}

        def chat(request, timeout=0):
            erfasst["text"] = request.messages[-1]["content"]
            raise RuntimeError("genug gesehen")

        with patch("graph.nodes.gespraechsvektor.model_service.chat.submit_sync", side_effect=chat), \
             patch("graph.nodes.gespraechsvektor.logger"):
            try:
                _hypothese_destillieren(
                    state, max_laenge=2, resonanz_kontext="",
                    wissensluecken=[{"konzept": "Quarkmaterie", "quelle": "kzg", "relevanz": 0.3}],
                    strategie_aktiv=True,
                )
            except RuntimeError:
                pass
        return erfasst.get("text", "")

    def test_bei_einer_bitte_steht_der_block(self) -> None:
        text = self.prompt(zustand("task"))
        self.assertIn("[BITTE]", text)
        self.assertIn("SPRUNG 1 erfuellt diese Bitte", text)

    def test_der_block_steht_nach_den_luecken(self) -> None:
        text = self.prompt(zustand("task"))
        self.assertLess(text.index("[WISSENSLUECKEN]"), text.index("[BITTE]"))

    def test_ohne_bitte_kein_block(self) -> None:
        self.assertNotIn("[BITTE]", self.prompt(zustand("knowledge")))
        self.assertIn("[WISSENSLUECKEN]", self.prompt(zustand("knowledge")))


class DerVerfasserErfaehrtEs(unittest.TestCase):
    """Die Vorgabe im `[GESPRAECHSVEKTOR]`-Block des Verfassers."""

    SATZ = "Person B hat um etwas Konkretes gebeten. Person A liefert es zuerst"

    def block(self, state: dict) -> str:
        state["gv_detail"] = {"cluster": "werkstatt", "strategie": "Im", "vehikel": "frage",
                              "vorausdenken": "gelaufen"}
        with patch("graph.nodes.verfasser.logger"):
            return _gespraechsvektor_block(state)

    def test_bei_einer_bitte_steht_die_vorgabe(self) -> None:
        self.assertIn(self.SATZ, self.block(zustand("task")))

    def test_die_vorgabe_spricht_in_den_namen_des_verfassers(self) -> None:
        """Der Verfasser nennt die beiden Person A und Person B (`F-PROMPT-2`); die
        erste Fassung schrieb *der Nutzer* und kam durch die Suite, weil der
        Namenszeuge nur drei andere Bloecke prueft."""
        block = self.block(zustand("task"))
        vorgabe = block[block.index("Person B hat um etwas Konkretes"):]
        vorgabe = vorgabe[:vorgabe.index("Stelle.") + len("Stelle.")]
        for fremd in ("Nutzer", "Nova", " du ", " dir "):
            with self.subTest(fremd=fremd):
                self.assertNotIn(fremd, vorgabe)

    def test_ohne_bitte_nicht(self) -> None:
        self.assertNotIn(self.SATZ, self.block(zustand("smalltalk")))

    def test_nicht_auf_einem_impuls(self) -> None:
        self.assertNotIn(self.SATZ, self.block(zustand("task", impuls=True)))


if __name__ == "__main__":
    unittest.main()
