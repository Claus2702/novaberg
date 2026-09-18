"""Tests: Der Ausgang eines Dienstes steht am Turn — Scheibe 12 A, Punkt 2.

Entschieden am 16.09.2026: Der Ausgang wird am Turn vermerkt, damit Verlauf und
Verdichtung ihn tragen. `session_turn_mark_action` und das Rendern von
`[ERLEDIGT]`/`[FEHLGESCHLAGEN]` existierten — **der Aufrufer fehlte seit dem
23.04.2026**. Ohne ihn war die Wiederholung einer echten Schreibung im naechsten
Turn nicht als solche erkennbar.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import inspect
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from graph.nodes import dispatcher
from memory.session import format_session_turns_numbered


class FakeRedis:
    def __init__(self, turns: list[dict]) -> None:
        self.liste = [json.dumps(t) for t in turns]

    def lrange(self, key: str, a: int, b: int) -> list[str]:
        return list(self.liste)

    def lset(self, key: str, idx: int, wert: str) -> None:
        self.liste[idx] = wert

    def turns(self) -> list[dict]:
        return [json.loads(t) for t in self.liste]


def _vermerken(stati: list[str]) -> list[dict]:
    speicher = FakeRedis([{"rolle": "user", "inhalt": "Trag den Zahnarzt ein"},
                          {"rolle": "assistant", "inhalt": "Erledigt."}])
    state = {"user_id": "pruefer", "character_id": "nova",
             "agent_results": [SimpleNamespace(agent_name="timeline", status=s) for s in stati]}
    with patch.object(dispatcher, "cfg_redis_client", speicher):
        dispatcher._ausgang_vermerken(state)
    return speicher.turns()


class VermerkTest(unittest.TestCase):

    def test_abgeschlossen_heisst_erledigt_und_erfolgreich(self) -> None:
        nutzer = _vermerken(["abgeschlossen"])[0]
        self.assertEqual((nutzer.get("aktion_erledigt"), nutzer.get("aktion_erfolgreich")), (True, True))

    def test_fehler_heisst_erledigt_ohne_erfolg(self) -> None:
        nutzer = _vermerken(["fehler"])[0]
        self.assertEqual((nutzer.get("aktion_erledigt"), nutzer.get("aktion_erfolgreich")), (True, False))

    def test_rueckfrage_ablehnung_oder_kein_dienst_vermerken_nichts(self) -> None:
        for stati in (["rueckfrage"], ["abgelehnt"], ["rejected"], []):
            with self.subTest(stati=stati):
                self.assertNotIn("aktion_erledigt", _vermerken(stati)[0])

    def test_der_vermerk_erscheint_im_verlauf(self) -> None:
        turns = _vermerken(["abgeschlossen"])
        self.assertIn("ERLEDIGT", format_session_turns_numbered(turns))

    def test_beide_pfade_des_dispatchers_vermerken(self) -> None:
        """Verdrahtung: der fruehe Ausstieg und der volle Lauf."""
        self.assertEqual(inspect.getsource(dispatcher.dispatch).count("_ausgang_vermerken(state)"), 2)


if __name__ == "__main__":
    unittest.main()
