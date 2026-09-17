"""Tests: Der Objektbezug reist mit (Scheibe 12 D2b).

Ziel: Der Dienst, den der Planner fragt, bekommt die akuten Objekte, die an
seinem Zettel stehen, mit ihren bekannten Eigenschaften — und seine
Klassifikation sieht sie. Ein "Gerne" nennt weder Sache noch Zeitpunkt; die Lage
kennt beides.

Zeugen dieser Datei:
  * **Nur was am Zettel steht:** Objekte, die das Urteil einem anderen Dienst
    zuordnet, reisen nicht mit; ohne gerechnetes Urteil oder nach einem Ausfall
    reist nichts mit.
  * **Die Verdrahtung, Glied fuer Glied:** Planner setzt `objekt_bezug`, der
    Dispatch legt ihn in den Kontext des Agenten, die Klassifikation baut den
    `[OBJEKT]`-Block — und ohne Bezug keinen Block.

Was dieser Test NICHT kann: ob das Modell aus "Gerne" einen Auftrag mit Datum
macht. Das misst die Reihe in labor/.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.notizen import klassifikation as notizen_klass
from agents.object_nearness import objects_for_service, render_object_reference
from agents.timeline import dispatch as timeline_dispatch
from agents.timeline import klassifikation as timeline_klass
from graph.nodes import planner

ZAHNARZT = {"name": "Zahnarzttermin", "klasse": "vorgang", "akut": True,
            "gedeckt": {"Tag": "Donnerstag", "Uhrzeit": "15 Uhr"}, "offen": ["Ort"]}
MEHL = {"name": "Mehl", "klasse": "objekt", "akut": True, "gedeckt": {"Bedarf": "morgen"}, "offen": []}
SACHLAGE = {"herkunft": "fortgeschrieben", "objekte": [ZAHNARZT, MEHL, {**MEHL, "name": "Latent", "akut": False}]}
URTEIL = {"ergebnis": "gerechnet", "herkunft": "fortgeschrieben", "objekte": [
    {"name": "Zahnarzttermin", "empfaenger": ["timeline"], "naehe": {"timeline": 0.52, "notizen": 0.3}},
    {"name": "Mehl", "empfaenger": ["notizen"], "naehe": {"notizen": 0.6, "timeline": 0.2}},
]}


class BezugTest(unittest.TestCase):

    def test_nur_die_objekte_am_zettel_des_dienstes(self) -> None:
        self.assertEqual([o["name"] for o in objects_for_service(SACHLAGE, URTEIL, "timeline")], ["Zahnarzttermin"])
        self.assertEqual([o["name"] for o in objects_for_service(SACHLAGE, URTEIL, "notizen")], ["Mehl"])

    def test_der_bezug_traegt_das_bekannte_nicht_das_offene(self) -> None:
        bezug = objects_for_service(SACHLAGE, URTEIL, "timeline")[0]
        self.assertEqual(bezug, {"name": "Zahnarzttermin", "klasse": "vorgang",
                                 "gedeckt": {"Tag": "Donnerstag", "Uhrzeit": "15 Uhr"}})

    def test_kein_bezug_ohne_urteil_oder_nach_ausfall(self) -> None:
        for urteil in (None, {}, {"ergebnis": "ohne_merkmale"}, {**URTEIL, "herkunft": "ausfall_uebernommen"}):
            with self.subTest(urteil=urteil):
                self.assertEqual(objects_for_service(SACHLAGE, urteil, "timeline"), [])

    def test_zeile(self) -> None:
        self.assertEqual(render_object_reference(objects_for_service(SACHLAGE, URTEIL, "timeline")),
                         "- Zahnarzttermin (vorgang) — Tag: Donnerstag; Uhrzeit: 15 Uhr")


class VerdrahtungTest(unittest.TestCase):

    def test_der_planner_setzt_den_bezug_des_gefragten_dienstes(self) -> None:
        registry = {"timeline": SimpleNamespace(ziel="timeline", router_intents=[]),
                    "notizen": SimpleNamespace(ziel="notizen", router_intents=[])}
        agenten = {n: SimpleNamespace(name=n, objekt_merkmal="x") for n in registry}
        state = {"management_action": "agent", "management_target": "", "needs_timeline": False,
                 "objekt_urteil": URTEIL, "sachlage": SACHLAGE, "agent_results": [], "node_annotations": [],
                 "user_id": "u", "external": None}
        with patch.object(planner, "get_registry", return_value=registry), \
             patch.object(planner.AgentRegistry, "finden", side_effect=lambda n: agenten.get(n)):
            ergebnis = planner.plan(state, "postgres://test")
        self.assertEqual(ergebnis["agent_name"], "notizen")
        self.assertEqual([o["name"] for o in ergebnis["objekt_bezug"]], ["Mehl"])

    def test_der_dispatch_legt_den_bezug_in_den_kontext(self) -> None:
        gesehen = {}

        class _Agent:
            def invoke(self, agent_state):
                gesehen.update(agent_state)
                return {**agent_state, "status": "abgeschlossen", "ergebnis": {"ok": True}}

        state = {"user_id": "u", "character_id": "c", "user_prompt": "Gerne", "event_payload": {},
                 "management_action": "agent", "management_target": "timeline",
                 "objekt_bezug": objects_for_service(SACHLAGE, URTEIL, "timeline"), "agent_results": []}
        with patch.object(timeline_dispatch.AgentRegistry, "finden", return_value=_Agent()), \
             patch.object(timeline_dispatch, "redis_manager"):
            try:
                timeline_dispatch.dispatch_timeline(state)
            except Exception:  # noqa: BLE001 — geprueft wird nur, was der Agent bekam
                pass
        self.assertEqual([o["name"] for o in gesehen["kontext"]["objekt_bezug"]], ["Zahnarzttermin"])

    def test_die_klassifikation_baut_den_block_nur_mit_bezug(self) -> None:
        bezug = objects_for_service(SACHLAGE, URTEIL, "timeline")
        mit = timeline_klass._build_classify_prompt(None, None, bezug)
        ohne = timeline_klass._build_classify_prompt(None, None, [])
        self.assertIn("[OBJEKT]", mit)
        self.assertIn("- Zahnarzttermin (vorgang) — Tag: Donnerstag; Uhrzeit: 15 Uhr", mit)
        self.assertNotIn("[OBJEKT]", ohne)
        self.assertIn("[OBJEKT]", notizen_klass._build_classify_prompt(None, None, objects_for_service(SACHLAGE, URTEIL, "notizen")))


if __name__ == "__main__":
    unittest.main()
