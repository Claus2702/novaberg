"""Zeugen fuer die Entscheidungs-Eintraege der Knoten im `pipeline_log`.

Anlass: Die Featureliste fuehrte am 20.08.2026 **9 von 20 Knoten** mit
Pipeline-Eintrag; Thinker, Responder und Perzeption belegten ihre Weichen
nicht. Beim Thinker war damit nicht erhebbar, wie oft er ueberhaupt anlaeuft
und wie oft er korrigiert (`SYK-B-1-THINKER-WEICHE`).

Zeugen dieser Datei:
  * **`log_decision` hat eine Form**: `switch` mit `entscheidung`, `ausgang`,
    `eingang`, `massstab`; ein Name ohne Knotenpraefix und ein leerer
    Ausgang werfen.
  * **Der Thinker belegt den Schnell-Check** in beiden Ausgaengen, mit den
    Indikatoren, die ihn ausgeloest haben.
  * **Der Thinker belegt jeden Ausgang der Reasoning-Schleife** — OK,
    Korrektur, Korrektur ohne Text, Obergrenze, Self-Trigger, Nachfass im
    Retry — samt Zaehlern.
  * **Der Responder belegt die Form der Nachricht** — Verlauf mit Reiz, mit
    Auftrag, Auftrag allein, Reiz allein — und **das Ergebnis auf beiden
    Pfaden**, auch dem leeren, auf dem die Ist-Laenge bisher fehlte.
  * **Die Perzeption belegt den Kontext** (geladen, leer, ohne Nutzer,
    ausgefallen) **und die Herkunft der Wahrnehmung** — gelesen oder die
    Standardwerte, die in der Spanne echter Werte liegen.
  * **Ein Schreibfehler der Forensik toetet den Turn nicht.**

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from graph.nodes import perzeption as perz_mod
from graph.nodes import responder as resp_mod
from graph.nodes import thinker as thinker_mod
from graph.nodes.thinker import MAX_ITERATIONEN, NACHFASS_MAX, think
from memory import pipeline_log


class LogDecisionFormTest(unittest.TestCase):
    """Die gemeinsame Form des Entscheidungs-Eintrags."""

    def test_writes_switch_with_four_fields(self) -> None:
        with patch.object(pipeline_log, "_log_eintrag") as schreiben:
            pipeline_log.log_decision(
                turn_id="t1", node="thinker", quelle="character",
                decision="thinker.schnellcheck", outcome="reasoning",
                inputs={"needs_web": True}, scale={"indikatoren": 3},
                user_id="u", character_id="c",
            )
        args = schreiben.call_args.args
        self.assertEqual(args[0], "switch")
        self.assertEqual(args[1:4], ("t1", "thinker", "character"))
        self.assertEqual(args[4], {
            "entscheidung": "thinker.schnellcheck",
            "ausgang":      "reasoning",
            "eingang":      {"needs_web": True},
            "massstab":     {"indikatoren": 3},
        })

    def test_missing_scale_is_empty_dict(self) -> None:
        with patch.object(pipeline_log, "_log_eintrag") as schreiben:
            pipeline_log.log_decision("t1", "x", "user", "x.y", "z", {})
        self.assertEqual(schreiben.call_args.args[4]["massstab"], {})

    def test_name_without_node_prefix_raises(self) -> None:
        for name in ("schnellcheck", "thinker.", ""):
            with self.subTest(name=name), self.assertRaises(ValueError):
                pipeline_log.log_decision("t1", "thinker", "user", name, "a", {})

    def test_empty_outcome_raises(self) -> None:
        with self.assertRaises(ValueError):
            pipeline_log.log_decision("t1", "thinker", "user", "thinker.x", "", {})


class ThinkerDecisionTest(unittest.TestCase):
    """Die Weichen des Thinkers stehen im Protokoll."""

    @staticmethod
    def _state(response: str, needs_web: bool = False, retry: bool = False) -> dict:
        return {
            "turn_id":          "turn-1",
            "user_id":          "u",
            "response":         response,
            "user_prompt":      "Erzaehl mir etwas ueber Neutronensterne.",
            "needs_web":        needs_web,
            "event_payload":    {"thinker_unsicher_retry": True} if retry else {},
            "node_annotations": [],
            "token_total":      0,
            "character_id":     "nova",
            "agent_results":    [],
            "memory_context":   "",
            "sachlage":         None,
            "graph_rolle":      "character",
        }

    def _run(
        self,
        state: dict,
        texte: list[str],
        nachfass: bool = False,
    ) -> list[dict]:
        """Faehrt `think` mit festen Modellantworten, liefert die Eintraege."""
        antworten = [MagicMock(text=t, thinking="", token_total=0) for t in texte]
        normalizer = MagicMock()
        normalizer.pruefen.return_value = MagicMock(
            braucht_nachfass=nachfass, thinking_material="gedacht",
        )
        with patch.object(thinker_mod, "log_decision") as belegen, \
                patch.object(thinker_mod, "create_tools", return_value=[]), \
                patch.object(thinker_mod, "_execute_tool_call", return_value="ok"), \
                patch.object(thinker_mod, "_retry_nutzlast", return_value={}), \
                patch.object(thinker_mod.model_service.chat, "submit_sync",
                             side_effect=antworten) as modell, \
                patch.object(thinker_mod, "get_thinking_normalizer",
                             return_value=normalizer):
            think(state, redis_client=MagicMock(),
                  postgres_url="postgresql://unbenutzt", user_id="u")
        self.modell_aufrufe = modell.call_count
        return [c.kwargs for c in belegen.call_args_list]

    def _named(self, eintraege: list[dict], name: str) -> dict:
        treffer = [e for e in eintraege if e["decision"] == name]
        self.assertEqual(len(treffer), 1, eintraege)
        return treffer[0]

    def test_no_facts_passes_through_and_is_recorded(self) -> None:
        eintraege = self._run(self._state("Das klingt schoen."), [])
        self.assertEqual(len(eintraege), 1)
        check = eintraege[0]
        self.assertEqual(check["decision"], "thinker.schnellcheck")
        self.assertEqual(check["outcome"], "durchlauf")
        self.assertEqual(check["inputs"]["treffer_antwort"], [])
        self.assertEqual(check["inputs"]["treffer_reiz"], [])
        self.assertFalse(check["inputs"]["needs_web"])
        self.assertEqual(check["node"], "thinker")
        self.assertEqual(check["turn_id"], "turn-1")
        self.assertEqual(check["quelle"], "character")
        self.assertEqual(self.modell_aufrufe, 0)

    def test_indicator_triggers_reasoning_and_names_the_hit(self) -> None:
        eintraege = self._run(self._state("Er liegt 9000 km tief."), ["ERGEBNIS: OK"])
        check = self._named(eintraege, "thinker.schnellcheck")
        self.assertEqual(check["outcome"], "reasoning")
        self.assertIn("km", check["inputs"]["treffer_antwort"])
        ergebnis = self._named(eintraege, "thinker.ergebnis")
        self.assertEqual(ergebnis["outcome"], "ok")
        self.assertEqual(ergebnis["inputs"]["iterationen"], 1)
        self.assertEqual(ergebnis["scale"],
                         {"max_iterationen": MAX_ITERATIONEN, "nachfass_max": NACHFASS_MAX})

    def test_needs_web_forces_reasoning(self) -> None:
        eintraege = self._run(self._state("Schoen.", needs_web=True), ["ERGEBNIS: OK"])
        check = self._named(eintraege, "thinker.schnellcheck")
        self.assertEqual(check["outcome"], "reasoning")
        self.assertTrue(check["inputs"]["needs_web"])

    def test_tool_calls_are_counted(self) -> None:
        eintraege = self._run(self._state("Er liegt 9000 km tief."),
                              ["TOOL: web_search(Magnetar)", "ERGEBNIS: OK"])
        ergebnis = self._named(eintraege, "thinker.ergebnis")
        self.assertEqual(ergebnis["inputs"]["tool_aufrufe"], 1)
        self.assertEqual(ergebnis["inputs"]["iterationen"], 2)

    def test_correction_with_text(self) -> None:
        text = ("ERGEBNIS: KORREKTUR\nPROBLEME:\n- Zahl falsch\n"
                "KORRIGIERTE ANTWORT: Er liegt 20 km tief.")
        eintraege = self._run(self._state("Er liegt 9000 km tief."), [text])
        ergebnis = self._named(eintraege, "thinker.ergebnis")
        self.assertEqual(ergebnis["outcome"], "korrektur")

    def test_correction_without_text_is_its_own_outcome(self) -> None:
        eintraege = self._run(self._state("Er liegt 9000 km tief."),
                              ["ERGEBNIS: KORREKTUR"])
        ergebnis = self._named(eintraege, "thinker.ergebnis")
        self.assertEqual(ergebnis["outcome"], "korrektur_ohne_text")

    def test_iteration_limit(self) -> None:
        eintraege = self._run(self._state("Er liegt 9000 km tief."),
                              ["ich denke noch"] * MAX_ITERATIONEN)
        ergebnis = self._named(eintraege, "thinker.ergebnis")
        self.assertEqual(ergebnis["outcome"], "max_iterationen")
        self.assertEqual(ergebnis["inputs"]["iterationen"], MAX_ITERATIONEN)

    def test_double_failure_sets_self_trigger(self) -> None:
        eintraege = self._run(self._state("Er liegt 9000 km tief."),
                              [""] * (2 * NACHFASS_MAX + 1), nachfass=True)
        ergebnis = self._named(eintraege, "thinker.ergebnis")
        self.assertEqual(ergebnis["outcome"], "self_trigger")
        self.assertEqual(ergebnis["inputs"]["nachfass_versuche"], NACHFASS_MAX)

    def test_double_failure_in_retry(self) -> None:
        eintraege = self._run(self._state("Er liegt 9000 km tief.", retry=True),
                              [""] * (2 * NACHFASS_MAX + 1), nachfass=True)
        ergebnis = self._named(eintraege, "thinker.ergebnis")
        self.assertEqual(ergebnis["outcome"], "nachfass_erschoepft_im_retry")
        self.assertTrue(ergebnis["inputs"]["unsicher_retry"])

    def test_forensic_failure_does_not_kill_the_turn(self) -> None:
        state = self._state("Das klingt schoen.")
        with patch.object(thinker_mod, "log_decision", side_effect=RuntimeError("weg")), \
                self.assertLogs("ki_server.thinker", level="WARNING") as logs:
            ergebnis = think(state, redis_client=MagicMock(),
                             postgres_url="postgresql://unbenutzt", user_id="u")
        self.assertIs(ergebnis, state)
        self.assertTrue(any("thinker.schnellcheck" in z for z in logs.output), logs.output)


class ResponderDecisionTest(unittest.TestCase):
    """Die Weichen des Responders stehen im Protokoll."""

    VERLAUF: list[dict] = [
        {"rolle": "user", "inhalt": "Was ist ein Pulsar?"},
        {"rolle": "assistant", "inhalt": "Ein rotierender Neutronenstern."},
        {"rolle": "user", "inhalt": "Wie schnell dreht er?"},
    ]

    @staticmethod
    def _state(**felder: object) -> dict:
        basis: dict = {
            "user_prompt": "Wie schnell dreht er?",
            "user_id": "u", "character_id": "nova", "turn_id": "turn-2",
            "memory_context": "", "web_context": "", "session_turns": [],
            "task_block": "", "task_context_cut": False,
            "gespraechsvektor": "", "gv_detail": {},
            "antwort_inhalt": "x" * 40,
            "emotions_verlauf": [], "nova_emotions_verlauf": [],
            "user_intentionen": [], "agent_results": [],
            "external": None, "internal": None,
            "response": "", "token_total": 0, "graph_rolle": "character",
        }
        basis.update(felder)
        return basis

    def _run(self, state: dict, text: str = "Sehr schnell.") -> dict[str, dict]:
        antwort = SimpleNamespace(text=text, token_total=7, model="m")
        with patch.object(resp_mod, "log_decision") as belegen, \
                patch.object(resp_mod.model_service.chat, "submit_sync",
                             return_value=antwort):
            resp_mod.respond(state)
        eintraege = [c.kwargs for c in belegen.call_args_list]
        namen = [e["decision"] for e in eintraege]
        self.assertEqual(namen, ["responder.nachricht", "responder.ergebnis"], eintraege)
        return {e["decision"]: e for e in eintraege}

    def test_history_with_stimulus(self) -> None:
        e = self._run(self._state(session_turns=list(self.VERLAUF)))
        nachricht = e["responder.nachricht"]
        self.assertEqual(nachricht["outcome"], "verlauf_mit_reiz")
        self.assertEqual(nachricht["inputs"]["turns_gelesen"], 3)
        self.assertTrue(nachricht["inputs"]["reiz_aus_verlauf"])
        self.assertGreater(nachricht["inputs"]["gruppen"], 0)
        self.assertEqual(nachricht["node"], "responder")
        self.assertEqual(nachricht["turn_id"], "turn-2")

    def test_stimulus_without_history(self) -> None:
        e = self._run(self._state())
        self.assertEqual(e["responder.nachricht"]["outcome"], "reiz_ohne_verlauf")
        self.assertEqual(e["responder.nachricht"]["inputs"]["turns_gelesen"], 0)

    def test_impulse_without_history(self) -> None:
        e = self._run(self._state(
            user_prompt="", eigener_gedanke="Ein Gedanke ueber Pulsare.",
            event_payload={"reiz_herkunft": "eigener_impuls"},
        ))
        self.assertEqual(e["responder.nachricht"]["outcome"], "auftrag_ohne_verlauf")
        self.assertTrue(e["responder.nachricht"]["inputs"]["eigener_gedanke"])

    def test_impulse_with_history(self) -> None:
        e = self._run(self._state(
            user_prompt="", eigener_gedanke="Ein Gedanke ueber Pulsare.",
            event_payload={"reiz_herkunft": "eigener_impuls"},
            session_turns=list(self.VERLAUF),
        ))
        self.assertEqual(e["responder.nachricht"]["outcome"], "verlauf_mit_auftrag")

    def test_result_recorded_with_length(self) -> None:
        e = self._run(self._state(), text="Sehr schnell.")
        ergebnis = e["responder.ergebnis"]
        self.assertEqual(ergebnis["outcome"], "antwort")
        self.assertEqual(ergebnis["inputs"]["ist_zeichen"], 13)
        self.assertEqual(ergebnis["inputs"]["tokens"], 7)

    def test_empty_result_is_recorded_too(self) -> None:
        with self.assertLogs("ki_server.responder", level="ERROR"):
            e = self._run(self._state(), text="  ")
        ergebnis = e["responder.ergebnis"]
        self.assertEqual(ergebnis["outcome"], "leer")
        self.assertEqual(ergebnis["inputs"]["inhalt_zeichen"], 40)


class PerzeptionDecisionTest(unittest.TestCase):
    """Die Weichen der Perzeption stehen im Protokoll."""

    # Kanonische Werte in allen sechs Feldern, damit der saubere Fall null
    # Ausreisser hat (die Fixtur in `test_perzeption.py` hat drei).
    GELESEN: dict = {
        "rational":      {"intent": "knowledge", "tone": "sachlich",
                          "thema": "Pulsare"},
        "emotional":     {"emotion": "neugierig", "arousal": 0.4},
        "psychologisch": {"modus": "fachgespraech", "sprach_stil": "fachlich",
                          "beziehungs_dynamik": "vertrauen"},
    }

    def _run(
        self,
        state: dict | None = None,
        verlauf: str = "1. Nutzer: Was ist ein Pulsar?",
        turns_wirft: bool = False,
        parse_wirft: bool = False,
    ) -> dict[str, dict]:
        zustand: dict = state if state is not None else {
            "user_prompt": "Wie schnell dreht ein Pulsar?", "response": "Sehr schnell.",
            "user_id": "u", "character_id": "nova", "turn_id": "turn-3",
            "graph_rolle": "human",
        }
        dienst = MagicMock()
        if parse_wirft:
            dienst.chat.submit_sync.side_effect = json.JSONDecodeError("kaputt", "", 0)
        else:
            dienst.chat.submit_sync.return_value = MagicMock(parsed=self.GELESEN)

        def _turns(*_a: object, **_k: object) -> list:
            if turns_wirft:
                raise RuntimeError("redis weg")
            return [{"rolle": "user"}]

        with patch.object(perz_mod, "log_decision") as belegen, \
                patch.object(perz_mod, "model_service", dienst), \
                patch.object(perz_mod, "redis_client", MagicMock()), \
                patch.object(perz_mod, "get_node_config", return_value={}), \
                patch.object(perz_mod, "session_turns_retrieve", side_effect=_turns), \
                patch.object(perz_mod, "format_session_turns_numbered",
                             return_value=verlauf):
            perz_mod.perceive(zustand)
        eintraege = [c.kwargs for c in belegen.call_args_list]
        namen = [e["decision"] for e in eintraege]
        self.assertEqual(namen, ["perzeption.kontext", "perzeption.wahrnehmung"], eintraege)
        return {e["decision"]: e for e in eintraege}

    def test_context_loaded_and_perception_read(self) -> None:
        e = self._run()
        self.assertEqual(e["perzeption.kontext"]["outcome"], "geladen")
        self.assertGreater(e["perzeption.kontext"]["inputs"]["kontext_zeichen"], 0)
        wahr = e["perzeption.wahrnehmung"]
        self.assertEqual(wahr["outcome"], "gelesen")
        self.assertEqual(wahr["inputs"]["ziel"], "external")
        self.assertEqual(wahr["inputs"]["ausreisser"], 0)
        self.assertEqual(wahr["node"], "perzeption")
        self.assertEqual(wahr["turn_id"], "turn-3")
        self.assertEqual(wahr["quelle"], "user")

    def test_empty_history(self) -> None:
        e = self._run(verlauf="")
        self.assertEqual(e["perzeption.kontext"]["outcome"], "leer")

    def test_failed_history_is_not_empty_history(self) -> None:
        with self.assertLogs("ki_server.perzeption", level="WARNING"):
            e = self._run(turns_wirft=True)
        self.assertEqual(e["perzeption.kontext"]["outcome"], "ausgefallen")

    def test_without_user(self) -> None:
        e = self._run(state={"user_prompt": "Hallo", "user_id": "", "turn_id": "t"})
        self.assertEqual(e["perzeption.kontext"]["outcome"], "ohne_nutzer")

    def test_parse_failure_is_marked_as_defaults(self) -> None:
        with self.assertLogs("ki_server.perzeption", level="WARNING"):
            e = self._run(parse_wirft=True)
        self.assertEqual(e["perzeption.wahrnehmung"]["outcome"], "standardwerte")

    def test_nova_role_targets_internal(self) -> None:
        e = self._run(state={
            "user_prompt": "Frage", "response": "Novas Antwort.",
            "user_id": "u", "character_id": "nova", "turn_id": "t",
            "perzeption_rolle": "assistant",
        })
        self.assertEqual(e["perzeption.wahrnehmung"]["inputs"]["ziel"], "internal")
        self.assertEqual(e["perzeption.wahrnehmung"]["inputs"]["eingabe_zeichen"], 14)

    def test_outlier_count_reaches_the_entry(self) -> None:
        kaputt = json.loads(json.dumps(self.GELESEN))
        kaputt["rational"]["tone"] = "voellig_unbekannt"
        self.GELESEN, alt = kaputt, self.GELESEN
        try:
            with patch.object(perz_mod, "log_berechnung"):
                e = self._run()
        finally:
            self.GELESEN = alt
        self.assertEqual(e["perzeption.wahrnehmung"]["inputs"]["ausreisser"], 1)


if __name__ == "__main__":
    unittest.main()
