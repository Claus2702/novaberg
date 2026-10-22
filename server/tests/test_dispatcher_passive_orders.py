"""Zeugen für die passiven Aufträge im Dispatcher: das Ereignis vor den Fakten.

Was diese Datei zusichert:
  * **Kurzer Weg:** Ein Fakten- und ein Ereignis-Auftrag ohne andere Writes
    nehmen den Weg ohne Verteilung; `process_event_orders` läuft vor
    `process_fact_orders`, gleich in welcher Reihenfolge die Writes stehen,
    und die Registry wird nicht gefragt.
  * **Die Abbildung reist mit:** Der Fakten-Auftrag trägt `daten["ereignisse"]`
    aus der Rückgabe des Ereignis-Auftrags; ohne Ereignis bleibt er, wie die
    Sachlage ihn stellte.
  * **Voller Weg:** Mit einem KZG-Write laufen die passiven Aufträge in
    derselben Reihenfolge, und der Ereignis-Auftrag erreicht keinen Manager
    `timeline`.
  * **Ausgesondert wird nach Ziel und Aktion:** Ein Manager-Write mit
    `ziel="timeline"` geht an `registry.get("timeline")`, nicht an den Dienst.

Beide Dienste sind Doppel an einem gemeinsamen Mock, der die Reihenfolge der
Aufrufe festhält; kein Zeuge öffnet eine Datenbank.
"""

import unittest
from unittest.mock import MagicMock, call, patch

from graph.nodes import dispatcher as dispatcher_mod

_DATEN: dict = {"turn_id": "probe-turn", "verlauf_id": 42, "salienz_human": 0.80,
                "user_intentionen": ["mitteilen"], "abgelegt": True}
_FAKTEN: dict = {"ziel": "fakten", "aktion": "pruefen", "daten": dict(_DATEN)}
_EREIGNIS: dict = {"ziel": "timeline", "aktion": "ereignis", "daten": dict(_DATEN)}
_KZG: dict = {"ziel": "kzg", "aktion": "create", "daten": {}}
_TERMIN: dict = {"ziel": "timeline", "aktion": "anlegen", "daten": {"titel": "Probe"}}


class _Emotion:
    """Ein Personality-Doppel mit den Feldern, die der Nachlauf liest."""

    mode:    str   = "sachlich"
    arousal: float = 0.5

    def to_dict(self) -> dict:
        return {"emotion": "ruhig", "arousal": 0.5}


class _Personality:
    def __init__(self) -> None:
        self.emotion = _Emotion()


def _zustand(writes: list) -> dict:
    """Der Zustand am Dispatcher-Eingang, so wie ihn ein echter Turn liefert."""
    return {
        "turn_id": "probe-turn", "user_id": "probe-nutzer", "character_id": "nova",
        "pending_writes": list(writes), "response": "Eine Antwort.",
        "external": _Personality(), "internal": _Personality(),
        "user_prompt": "Meine Schwester zieht im November nach Wernau.",
    }


class PassiveOrdersTest(unittest.TestCase):
    """Reihenfolge, Abbildung und Aussonderung der passiven Aufträge."""

    def _run(self, writes: list, events: dict | None = None) -> dict:
        """Fährt den Dispatcher; die Doppel nach Namen, `reihe` mit beiden Diensten."""
        reihe = MagicMock()
        reihe.events.return_value = {1: 77} if events is None else events
        reihe.facts.return_value = [{"ausgang": "leer"}]
        manager = MagicMock()
        manager.execute.return_value = 1
        registry = MagicMock(return_value={"timeline": manager})
        d: dict = {"reihe": reihe, "manager": manager, "registry": registry,
                   "reinforce": MagicMock(), "kzg": MagicMock(return_value={"kzg_verarbeitet": 1})}
        with patch.object(dispatcher_mod, "process_event_orders", reihe.events), \
             patch.object(dispatcher_mod, "process_fact_orders", reihe.facts), \
             patch.object(dispatcher_mod, "get_registry", registry), \
             patch.object(dispatcher_mod, "_verwendung_verstaerken", d["reinforce"]), \
             patch.object(dispatcher_mod, "_delegation_trigger_pruefen", return_value=""), \
             patch.object(dispatcher_mod, "dispatch_kzg", d["kzg"]), \
             patch.object(dispatcher_mod, "_verbindung_schreiben"), \
             patch.object(dispatcher_mod, "_persist_vorturn"), \
             patch.object(dispatcher_mod, "_persist_gv_detail"), \
             patch.object(dispatcher_mod, "log_db_write"), \
             patch.object(dispatcher_mod, "log_berechnung"), \
             patch.object(dispatcher_mod, "log_turn_roh"), \
             patch.object(dispatcher_mod, "_persist_short_term_drive"), \
             patch.object(dispatcher_mod, "_session_turn_schreiben"), \
             patch.object(dispatcher_mod, "reiz_text", return_value="Reiz"), \
             patch.object(dispatcher_mod, "reiz_herkunft", return_value="nutzer"):
            d["zustand"] = _zustand(writes)
            dispatcher_mod.dispatch(d["zustand"], MagicMock(), "postgresql://attrappe")
        return d

    def _order(self, reihe: MagicMock) -> list[str]:
        """Die Namen der Dienste in der Reihenfolge ihrer Aufrufe."""
        return [name for name, _, _ in reihe.mock_calls if name in ("events", "facts")]

    # --- kurzer Weg ---

    def test_short_way_the_event_runs_before_the_facts(self) -> None:
        d = self._run([_FAKTEN, _EREIGNIS])
        self.assertEqual(self._order(d["reihe"]), ["events", "facts"])
        self.assertEqual(d["reihe"].events.call_args.args[1:],
                         ([_EREIGNIS], "postgresql://attrappe"))
        d["registry"].assert_not_called()
        d["reinforce"].assert_not_called()
        self.assertEqual(d["zustand"]["pending_writes"], [])

    def test_the_twin_inserted_the_other_way_the_same_order(self) -> None:
        d = self._run([_EREIGNIS, _FAKTEN])
        self.assertEqual(self._order(d["reihe"]), ["events", "facts"])
        d["registry"].assert_not_called()

    def test_the_fact_order_carries_the_mapping_of_the_event_order(self) -> None:
        d = self._run([_FAKTEN, _EREIGNIS], events={1: 77, 2: None})
        auftraege: list = d["reihe"].facts.call_args.args[1]
        self.assertEqual(auftraege, [
            {**_FAKTEN, "daten": {**_DATEN, "ereignisse": {1: 77, 2: None}}},
        ])
        # Die Writes des Turns bleiben unverändert.
        self.assertNotIn("ereignisse", _FAKTEN["daten"])

    def test_without_an_event_the_fact_order_stays_as_issued(self) -> None:
        # Zwilling: ohne Ereignis-Auftrag kein Aufruf und keine Abbildung.
        d = self._run([_FAKTEN])
        d["reihe"].events.assert_not_called()
        self.assertEqual(d["reihe"].facts.call_args.args[1], [_FAKTEN])

    def test_an_event_order_alone_runs_without_facts(self) -> None:
        d = self._run([_EREIGNIS])
        self.assertEqual(self._order(d["reihe"]), ["events"])
        d["registry"].assert_not_called()

    # --- voller Weg ---

    def test_full_way_the_same_order_and_no_manager_for_the_event(self) -> None:
        d = self._run([_KZG, _FAKTEN, _EREIGNIS])
        self.assertEqual(self._order(d["reihe"]), ["events", "facts"])
        d["kzg"].assert_called_once()
        d["manager"].execute.assert_not_called()

    # --- Aussonderung nach Ziel und Aktion ---

    def test_a_manager_write_with_target_timeline_goes_to_the_registry(self) -> None:
        d = self._run([_TERMIN, _FAKTEN])
        d["reihe"].events.assert_not_called()
        d["registry"].assert_called_once()
        d["manager"].execute.assert_called_once()
        self.assertEqual(d["manager"].execute.call_args.kwargs["writes"], [_TERMIN])
        self.assertEqual(d["reihe"].facts.call_args, call(d["zustand"], [_FAKTEN],
                                                          "postgresql://attrappe"))

    def test_the_twin_with_both_the_manager_gets_only_its_write(self) -> None:
        d = self._run([_TERMIN, _EREIGNIS, _FAKTEN])
        self.assertEqual(d["manager"].execute.call_args.kwargs["writes"], [_TERMIN])
        self.assertEqual(d["reihe"].events.call_args.args[1], [_EREIGNIS])
        self.assertEqual(self._order(d["reihe"]), ["events", "facts"])


if __name__ == "__main__":
    unittest.main()
