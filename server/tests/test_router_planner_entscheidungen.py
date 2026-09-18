"""Tests: Router und Planner schreiben ihre Entscheidungen ins Pipeline-Log.

Metakognition Phase 1 verlangt: *jeder Node schreibt seine Entscheidung*. Router
und Planner schwiegen — ob ein Wartezustand griff, ob ein Angebot offen war, ob
der Riegel eine Zustimmung aufhielt, welcher Dienst gefragt und wer uebergangen
wurde, stand nur im Textlog. Form: `memory.pipeline_log.log_decision`
(`switch` mit `entscheidung`, `ausgang`, `eingang`, `massstab`) — dieselbe wie
bei Thinker, Responder und Perzeption.

Zeugen: je Weiche ein Eintrag, **auch beim Uebersprung** (kein Auftrag, kein
Wartezustand), und die Eingangsgroessen stehen im Eintrag, nicht nur der Ausgang.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents import discover_agents
from graph.nodes import planner, router
from plugins import discover_managers


class _Aufzeichnung:
    def __init__(self) -> None:
        self.eintraege: list[dict] = []

    def __call__(self, **kw: object) -> None:
        self.eintraege.append(kw)

    def von(self, entscheidung: str) -> list[dict]:
        return [e for e in self.eintraege if e["decision"] == entscheidung]


def _route(reiz: str, antwort: dict, pending: dict | None = None, angebot: object = None) -> _Aufzeichnung:
    aufz = _Aufzeichnung()
    state = {"user_id": "pruefer", "character_id": "nova", "turn_id": "t1", "user_prompt": reiz,
             "event_payload": {}, "node_annotations": [], "agent_results": [],
             "sachlage": {"herkunft": "fortgeschrieben", "objekte": []}}
    stell = SimpleNamespace(chat=SimpleNamespace(submit_sync=lambda request, timeout=None: SimpleNamespace(
        text=json.dumps(antwort), token_total=0, thinking="", parsed=dict(antwort))))
    with patch.object(router, "model_service", stell), \
         patch.object(router, "session_turns_retrieve", return_value=[]), \
         patch.object(router, "shadow_nearness", return_value={"ergebnis": "ohne_akute_objekte"}), \
         patch.object(router, "offer_load", return_value=angebot), \
         patch.object(router, "log_decision", aufz), \
         patch("tools.redis_manager.redis_manager.get_json", return_value=pending), \
         patch("tools.redis_manager.redis_manager.delete", return_value=1):
        router.route(dict(state))
    return aufz


LEER = {"needs_memory": False, "needs_web": False, "needs_timeline": False, "momentum": "mid",
        "management_action": "", "management_target": "", "management_target_typ": "titel"}
AUFTRAG = {**LEER, "management_action": "agent", "management_target": "timeline"}


class RouterTest(unittest.TestCase):

    def test_auch_ohne_auftrag_steht_die_zustellung_im_log(self) -> None:
        eintraege = _route("Wie heiss ist ein Neutronenstern?", LEER).von("router.zustellung")
        self.assertEqual(len(eintraege), 1)
        self.assertEqual(eintraege[0]["outcome"], "keine")
        self.assertIn("angebot_offen", eintraege[0]["inputs"])

    def test_der_riegel_steht_mit_seinen_eingangsgroessen_im_log(self) -> None:
        e = _route("Gerne", AUFTRAG).von("router.zustellung")[0]
        self.assertEqual(e["outcome"], "keine")
        self.assertTrue(e["inputs"]["riegel_gegriffen"])
        self.assertEqual(e["inputs"]["vom_modell"], "agent/timeline")

    def test_der_wartezustand_steht_im_log(self) -> None:
        self.assertEqual(_route("Die erste", LEER, {"agent_name": "notizen"}).von("router.rueckfrage")[0]["outcome"],
                         "resume:notizen")
        verworfen = _route("Trag mir den Zahnarzt ein.", AUFTRAG, {"agent_name": "notizen"})
        self.assertEqual(verworfen.von("router.rueckfrage")[0]["outcome"], "verworfen_eigener_auftrag")
        self.assertEqual(len(verworfen.von("router.zustellung")), 1)


class PlannerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        discover_managers()
        discover_agents()

    def _plan(self, state: dict) -> _Aufzeichnung:
        aufz = _Aufzeichnung()
        with patch.object(planner, "log_decision", aufz):
            planner.plan(state, "postgresql://unbenutzt")
        return aufz

    def test_ohne_auftrag_ein_durchlauf_eintrag(self) -> None:
        aufz = self._plan({"management_action": "", "turn_id": "t1", "node_annotations": []})
        self.assertEqual([e["outcome"] for e in aufz.eintraege], ["durchlauf"])

    def test_der_gefragte_dienst_steht_mit_reihenfolge_im_log(self) -> None:
        state = {"management_action": "agent", "management_target": "timeline", "turn_id": "t1",
                 "user_id": "pruefer", "character_id": "nova", "node_annotations": [], "agent_results": [],
                 "sachlage": {"objekte": []}, "objekt_urteil": {}, "external": None}
        aufz = self._plan(state)
        e = aufz.von("planner.dienstwahl")[-1]
        self.assertEqual(e["outcome"], "frage:timeline")
        self.assertIn("reihenfolge", e["inputs"])
        self.assertIn("objekt_bezug", e["inputs"])


if __name__ == "__main__":
    unittest.main()
