"""Zeugen für den Ereignis-Auftrag der Sachlage (`build_event_order`).

Was diese Datei zusichert:
  * **Das Tor liegt auf der gekrümmten Skala:** `salienz_human` 0,70 gibt
    einen Auftrag, 0,69 keinen, 0,75 einen — der rohe Vergleich gegen
    `KZG_SALIENZ_HIGH` (0,88078) gäbe bei 0,70 und 0,75 keinen. Die Werte
    stehen als Zahlen da, nicht aus der Konstante gerechnet.
  * **Eine Salienz, die keine Zahl ist, gibt laut keinen Auftrag.**
  * **Der Auftrag trägt die Daten des Fakten-Auftrags**, mit `ziel="timeline"`
    und `aktion="ereignis"`.
  * **`sachlage_assess` hängt ihn an**, über der Grenze neben dem
    Fakten-Auftrag, unter ihr nicht.

Kein Zeuge öffnet eine Datenbank: Die Sachlage ist bis auf ihre Bausteine
ersetzt, wie in `test_sachlage_memory.py`.
"""

import unittest
from unittest.mock import patch

from graph.nodes import sachlage as sachlage_mod

_DERIVED: dict = {"thema": "Familie", "gegenstand": "Umzug", "nutzerziel": "mitteilen",
                  "ausdrucksweise": "erzaehlend", "objekte": []}


def _state(salienz: object) -> dict:
    """Ein Zustand mit Turn, Salienz und Intention, wie ihn die Sachlage liest."""
    return {"user_id": "u", "character_id": "c", "turn_id": "t1",
            "salienz_human": salienz, "user_intentionen": ["mitteilen"]}


class EventOrderThresholdTest(unittest.TestCase):
    """Die Grenze: `salienz_berechnen(salienz_human, 1) >= KZG_SALIENZ_HIGH`."""

    def test_salience_070_gives_an_order(self) -> None:
        order = sachlage_mod.build_event_order(_state(0.70), 42, True)
        self.assertIsNotNone(order)
        self.assertEqual((order["ziel"], order["aktion"]), ("timeline", "ereignis"))

    def test_the_twin_salience_069_gives_none(self) -> None:
        self.assertIsNone(sachlage_mod.build_event_order(_state(0.69), 42, True))

    def test_salience_075_gives_an_order_the_raw_comparison_would_not(self) -> None:
        # 0,75 < 0,88078: Der rohe Vergleich gäbe hier keinen Auftrag.
        order = sachlage_mod.build_event_order(_state(0.75), 42, True)
        self.assertIsNotNone(order)

    def test_the_order_carries_the_data_of_the_fact_order(self) -> None:
        order = sachlage_mod.build_event_order(_state(0.80), 42, False)
        fakten = sachlage_mod.build_fact_order(_state(0.80), 42, False)
        self.assertEqual(order["daten"], fakten["daten"])
        self.assertEqual(order["daten"], {
            "turn_id": "t1", "verlauf_id": 42, "salienz_human": 0.80,
            "user_intentionen": ["mitteilen"], "abgelegt": False,
        })

    def test_a_salience_that_is_no_number_gives_none_loudly(self) -> None:
        for salienz in (None, True, "0.9", 1.5):
            with self.subTest(salienz=salienz), \
                 self.assertLogs("ki_server.sachlage", level="ERROR") as protokoll:
                self.assertIsNone(sachlage_mod.build_event_order(_state(salienz), 42, True))
            self.assertIn("keine Zahl in [0, 1]", "\n".join(protokoll.output))


class SachlageAssessIssuesTheEventOrderTest(unittest.TestCase):
    """Die Verdrahtung: der Knoten hängt den Ereignis-Auftrag neben den Fakten-Auftrag."""

    def _assess(self, salienz: float) -> dict:
        state = {**_state(salienz),
                 "user_prompt": "Meine Schwester zieht im November nach Wernau.",
                 "session_turns": [], "event_payload": {}, "event_source": "user",
                 "pending_writes": [{"ziel": "notizen", "aktion": "create", "daten": {}}]}
        with patch.object(sachlage_mod, "sachlage_load", return_value=(None, False)), \
             patch.object(sachlage_mod, "reiz_ist_eigener_gedanke", return_value=False), \
             patch.object(sachlage_mod, "_resume_lookup", return_value=None), \
             patch.object(sachlage_mod, "memory_offer", return_value=[]), \
             patch.object(sachlage_mod, "_derive", return_value=_DERIVED), \
             patch.object(sachlage_mod, "_sachlage_store"), \
             patch.object(sachlage_mod, "_track_short_goal"), \
             patch.object(sachlage_mod, "sachlage_bridge_build", return_value={}), \
             patch.object(sachlage_mod, "log_berechnung"), \
             patch.object(sachlage_mod, "history_write", return_value=42), \
             patch.object(sachlage_mod.model_service.embed, "submit_sync"), \
             patch.object(sachlage_mod, "remember_objects", return_value={"abgelegt": True}):
            sachlage_mod.sachlage_assess(state)
        return state

    def test_above_the_threshold_the_node_issues_both_orders(self) -> None:
        state = self._assess(0.80)
        self.assertEqual([(w["ziel"], w["aktion"]) for w in state["pending_writes"]],
                         [("notizen", "create"), ("fakten", "pruefen"), ("timeline", "ereignis")])
        self.assertEqual(state["pending_writes"][2]["daten"]["verlauf_id"], 42)

    def test_the_twin_below_the_threshold_only_the_fact_order(self) -> None:
        state = self._assess(0.62)
        self.assertEqual([w["ziel"] for w in state["pending_writes"]], ["notizen", "fakten"])


if __name__ == "__main__":
    unittest.main()
