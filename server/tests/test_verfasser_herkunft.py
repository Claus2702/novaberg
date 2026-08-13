"""Tests: Der Verfasser weiss, von wem der Reiz stammt.

Ziel: Ein eigener Impuls wird nicht dem Nutzer zugeschrieben — und zwar in der
Stufe, die den Text schreibt.

Hintergrund (`VERFASSER-KENNT-DIE-QUELLE-NICHT`, gemessen am 13.08.2026): Der
Responder unterschied den Fall seit dem 26.07. und trug einen Block dagegen.
Der Verfasser hatte die Pruefung nicht, und seit der Trennung von Inhalt und
Form schreibt er den Text. Von **14 eigenen Impulsen** eines Tages begannen
**13** mit „Du hast …", fuenf davon wortgleich — der Schutzblock des Responders
lief ins Leere, weil die Zuschreibung schon im Material stand.

Zeugen dieser Datei:
  * **Beide Faelle werden geprueft, nicht nur der Defekt.** Dass beim Impuls
    ein Herkunftsblock steht, ist erst eine Aussage, wenn beim Nutzer-Turn der
    andere steht — sonst waere ein Prompt, der immer denselben Satz traegt,
    ebenfalls gruen.
  * **Geprueft wird der Wortlaut der Vorgabe, nicht ihre Ueberschrift.** Ein
    Test auf `[HERKUNFT DES REIZES]` bliebe gruen, wenn beide Fassungen
    denselben Text traegen.
  * **Die Abgrenzung gegen den Thinker-Retry gehoert dazu:** gleiche
    `event_source`, aber eine wiederholte Nutzer-Aeusserung.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from graph.nodes import verfasser as verf_mod
from graph.reiz import reiz_ist_eigener_gedanke


def _state(payload: dict | None = None, event_source: str = "user") -> dict:
    """Ein Zustand, wie ihn der Verfasser liest."""
    return {
        "user_prompt":      "Ein Reiz.",
        "event_source":     event_source,
        "event_payload":    payload if payload is not None else {},
        "user_id":          "u", "character_id": "c", "turn_id": "t",
        "memory_context":   "", "web_context": "",
        "session_turns":    [], "task_block": "",
        "gespraechsvektor": "", "gv_detail": {},
        "node_annotations": {},
    }


class HerkunftTest(unittest.TestCase):
    """Die Auskunft selbst — sie liegt jetzt an einem Ort für beide Stufen."""

    def test_eigener_impuls_wird_erkannt(self) -> None:
        self.assertTrue(reiz_ist_eigener_gedanke(
            _state({"reiz_herkunft": "eigener_impuls"}, "character")))

    def test_nutzer_turn_ist_kein_eigener_gedanke(self) -> None:
        self.assertFalse(reiz_ist_eigener_gedanke(_state()))

    def test_thinker_retry_ist_kein_eigener_gedanke(self) -> None:
        """Gleiche Quelle, aber eine wiederholte NUTZER-Aeusserung."""
        self.assertFalse(reiz_ist_eigener_gedanke(
            _state({"thinker_unsicher_retry": True}, "character")))


class VerfasserPromptTest(unittest.TestCase):
    """Der Block steht im Prompt der Stufe, die den Text schreibt."""

    def test_beim_impuls_steht_die_eigene_herkunft(self) -> None:
        prompt: str = verf_mod._build_system_prompt(
            _state({"reiz_herkunft": "eigener_impuls"}, "character"))

        self.assertIn("hat der Nutzer NICHT gesagt", prompt)
        self.assertIn("eigener Gedanke des Charakters", prompt)

    def test_der_block_verbietet_die_zuschreibung_woertlich(self) -> None:
        """Die gemessene Formulierung war „Du hast …" — sie steht im Verbot."""
        prompt: str = verf_mod._build_system_prompt(
            _state({"reiz_herkunft": "eigener_impuls"}, "character"))

        self.assertIn('Kein "du hast"', prompt)

    def test_beim_nutzer_turn_steht_die_fremde_herkunft(self) -> None:
        """Der positive Zwilling: Sonst wäre ein immer gleicher Satz auch grün."""
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertIn("hat der Nutzer gesagt", prompt)
        self.assertNotIn("hat der Nutzer NICHT gesagt", prompt)

    def test_der_thinker_retry_bekommt_die_fremde_herkunft(self) -> None:
        prompt: str = verf_mod._build_system_prompt(
            _state({"thinker_unsicher_retry": True}, "character"))

        self.assertIn("hat der Nutzer gesagt", prompt)


if __name__ == "__main__":
    unittest.main()
