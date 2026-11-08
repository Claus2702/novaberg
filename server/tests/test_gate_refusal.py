"""Tests: Ein Nein am Tor eines Dienstes endet als `dismissed`, nicht als `abgeschlossen`.

Die Zusicherungen:

  1. **Ein Nein ist kein Erfolg.** Direktiven und Notizen melden es mit dem
     Status des Rueckwegs, das Protokoll traegt ihn samt Text, und die Antwort
     kommt aus `responder.aufgabe_verworfen`.
  2. **Nichts laeuft weiter.** Der Notizen-Graph endet ohne `ausfuehren`; der
     Zwilling *„ja“* fuehrt aus und endet `abgeschlossen`. Nach dem Nein bleibt
     kein Wartezustand stehen; eine unklare Antwort erneuert ihn.
  3.**Die Leser behandeln das Nein nicht als Schreibung:** kein
     `[VERARBEITUNG]`-Block, kein Vermerk am Turn, keine Deckung einer
     Speicherbehauptung, keine Quelle fuer ein Datum.

Jede Menge steht hier als eigenes Literal und wird nicht aus dem Code
gerechnet: Waechst oder schrumpft sie dort, wird ihr Zeuge rot. Die Zeugen der
Leser laufen ueber den ganzen Status-Kanon, nicht nur ueber `dismissed`.

Kein Zeuge oeffnet eine Datenbank, Redis oder ein Netz: Speicher und Protokoll
sind gedoppelt.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from langgraph.graph import END

from agents.base import STATUS_KANON, AgentResult, Korrektur
from agents.direktiven import crud as directive_crud
from agents.direktiven import dispatch as directive_dispatch
from agents.direktiven import resume as directive_resume
from agents.direktiven.agent import DirektivenAgent
from agents.notizen import agent as notes_agent
from agents.notizen import dispatch as notes_dispatch
from agents.notizen.agent import NotizenAgent
from graph.nodes import agent_dispatch as dispatch_node
from graph.nodes import dispatcher, planner, thinker, tribunal
from utils.storage_claims import uncovered_claims

_USER: str = "pruef-nutzer"
_CANON: frozenset[str] = frozenset({
    "abgeschlossen", "fehler", "rueckfrage", "abgelehnt", "rejected", "dismissed",
})
_RUNNING: str = "laufend"
# Was `read_answer` setzen darf: Ein Erfolg ist nicht darunter, den setzt `ausfuehren`.
_READ_ANSWER_STATUSES: frozenset[str] = frozenset({
    "laufend", "dismissed", "rueckfrage", "fehler",
})
# Womit der Notizen-Graph nach `resume` endet, statt nach `ausfuehren` zu gehen.
_NOTES_END_AFTER_RESUME: frozenset[str] = frozenset({
    "fehler", "rueckfrage", "dismissed",
})
# Was den Direktiven-Graph nach der Deutung weiterfuehrt.
_DIRECTIVES_GO_ON: frozenset[str] = frozenset({"laufend"})
# Was als ausgefuehrte Schreibung gilt.
_SUCCESS: frozenset[str] = frozenset({"abgeschlossen"})
# Was am Turn einen Vermerk hinterlaesst.
_MARKED: frozenset[str] = frozenset({"abgeschlossen", "fehler"})
# Was die Antwort aus `responder.aufgabe_verworfen` baut.
_DISCARDED: frozenset[str] = frozenset({"dismissed"})

_SOURCE: str = "Termin 'Wartung der Anlage' eingetragen fuer 19.08.2026 14:00"
_CLAIM: str = "Morgen um 10 Uhr ist notiert."
_NOT_FOUND: dict = {
    "typ": "nicht_gefunden",
    "agent": "notizen",
    "aktion": "add_content",
    "target": "Einkauf",
    "original_aufgabe": "Schreib Milch auf die Einkaufsliste",
}
_NOTES_REFUSED_TEXT: str = "Okay, 'Einkauf' wird nicht angelegt."


def _result(status: str, text: str = "Eine Antwort des Dienstes") -> AgentResult:
    """Ein Ergebnis dieses Status mit den Pflichtfeldern, die der Betrieb setzt."""
    return AgentResult(
        agent_name="direktiven",
        ergebnis=text,
        status=status,
        fehler="Ein Fehlertext" if status == "fehler" else None,
        rueckfrage="Soll ich das tun?" if status == "rueckfrage" else None,
        korrektur=(
            Korrektur(befund="Ein Befund", beleg="Ein Beleg", vorschlag="Ein Vorschlag")
            if status == "abgelehnt" else None
        ),
    )


def _node_state(agent_name: str, answer: str) -> dict:
    """Der Zustand eines Turns, der eine Rueckfrage dieses Dienstes beantwortet."""
    return {
        "agent_name": agent_name,
        "management_action": "resume",
        "user_id": _USER,
        "character_id": "nova",
        "turn_id": "t-gate",
        "user_prompt": answer,
        "event_payload": {},
        "agent_results": [],
    }


def _run_node(module: object, function: object, agent: object, pending: dict, answer: str) -> tuple:
    """Faehrt `agent_dispatch_node` mit dem echten Dispatch und dem echten Graphen.

    Nachbedingung: die Rueckgabe des Knotens, der Inhalt des Protokolleintrags
    und das Redis-Doppel, das den Wartezustand traegt.
    """
    redis: MagicMock = MagicMock()
    redis.get_json.return_value = pending
    with patch.object(module, "redis_manager", redis), \
            patch.object(module.AgentRegistry, "finden", return_value=agent), \
            patch.object(dispatch_node, "get_dispatch", return_value=function), \
            patch.object(dispatch_node, "log_ausgabe") as log:
        returned: dict = dispatch_node.agent_dispatch_node(_node_state(agent.name, answer))
    return returned, log.call_args.kwargs["inhalt"], redis


def _task_block(returned: dict) -> tuple[str, bool]:
    """Der `[AUFGABE]`-Block, den der Planner aus der Rueckgabe des Knotens baut."""
    return planner._build_task_block(
        returned["agent_results"], returned["management_result"], returned["management_detail"],
    )


def _discarded_block(agent_name: str, text: str) -> str:
    """Der Block aus `responder.aufgabe_verworfen` fuer diesen Dienst und Text."""
    return planner.PROMPTS["responder.aufgabe_verworfen"].format(
        ergebnis_texte=f"- {agent_name}: {text}",
    )


class CanonTest(unittest.TestCase):
    """Die Zeugen der Leser laufen ueber diese Menge; sie muss der Kanon sein."""

    def test_the_canon_is_the_set_these_witnesses_run_over(self) -> None:
        self.assertEqual(STATUS_KANON, _CANON)


class DirectiveGateTest(unittest.TestCase):
    """Das Tor der Direktiven, ueber den Dispatch-Knoten bis in das Protokoll."""

    _QUESTION: str = "Soll ich das ausfuehren? Direktive loeschen: Erklaere Physik knapp"

    def _answer(self, answer: str) -> tuple[dict, dict, MagicMock]:
        """Beantwortet die Pflicht-Rueckfrage zum Loeschen; der Speicher ist gedoppelt."""
        store: MagicMock = MagicMock()
        store.execute.return_value = 1
        store.select_one.return_value = {"id": 7, "aktiv": True, "anweisung": "Erklaere Physik"}
        pending: dict = {
            "agent_name": "direktiven",
            "action": "delete",
            "target": "",
            "rueckfrage": self._QUESTION,
            "parameter": {"action": "delete", "target_id": 7},
        }
        with patch.object(directive_crud, "db_manager", store), \
                patch.object(directive_crud, "_verifizieren", return_value=True):
            returned, entry, _ = _run_node(
                directive_dispatch, directive_dispatch.dispatch_direktiven,
                DirektivenAgent(), pending, answer,
            )
        return returned, entry, store

    def test_no_is_logged_as_dismissed_with_its_text(self) -> None:
        """Das Protokoll traegt den Status und den Satz; geschrieben wurde nichts."""
        returned, entry, store = self._answer("nein")
        store.execute.assert_not_called()
        self.assertEqual(returned["agent_results"][-1].status, "dismissed")
        self.assertEqual(entry["status"], "dismissed")
        self.assertEqual(entry["ergebnis"], directive_resume.REFUSED_TEXT)

    def test_no_builds_the_answer_from_the_discarded_block(self) -> None:
        returned, _, _ = self._answer("nein")
        expected: str = _discarded_block("direktiven", directive_resume.REFUSED_TEXT)
        self.assertEqual(_task_block(returned), (expected, True))

    def test_yes_executes_and_ends_finished(self) -> None:
        """Zwilling: dieselbe Frage mit *„ja“* schreibt und endet als Erfolg."""
        returned, entry, store = self._answer("ja")
        store.execute.assert_called_once()
        self.assertEqual(entry["status"], "abgeschlossen")
        self.assertTrue(entry["ergebnis"])
        self.assertNotEqual(entry["ergebnis"], directive_resume.REFUSED_TEXT)
        self.assertNotIn("Er hat abgelehnt", _task_block(returned)[0])

    def test_read_answer_sets_only_its_statuses(self) -> None:
        self.assertEqual(directive_resume._STATUSES, _READ_ANSWER_STATUSES)

    def test_only_running_goes_on_after_the_reading(self) -> None:
        agent: DirektivenAgent = DirektivenAgent()
        go_on: set[str] = {
            status for status in _CANON | {_RUNNING}
            if agent._nach_deutung({"status": status}) != END
        }
        self.assertEqual(go_on, _DIRECTIVES_GO_ON)


class NotesGateTest(unittest.TestCase):
    """Die Frage nach einer nicht gefundenen Notiz, ueber den ganzen Graphen."""

    def _answer(self, answer: str) -> tuple[dict, dict, list[str], MagicMock]:
        """Beantwortet die Frage; `ausfuehren` ist ersetzt und zaehlt seine Aufrufe."""
        executed: list[str] = []

        def execute(state: dict) -> dict:
            executed.append(state["parameter"]["action"])
            return {
                "ergebnis": "Notiz 'Einkauf' angelegt",
                "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "erstellt"}],
            }

        pending: dict = {
            "agent_name": "notizen",
            "action": "add_content",
            "target": "Einkauf",
            "rueckfrage": json.dumps(_NOT_FOUND),
            "parameter": {"action": "add_content", "target": "Einkauf", "target_typ": "titel"},
        }
        with patch.object(notes_agent, "ausfuehren", execute):
            returned, entry, redis = _run_node(
                notes_dispatch, notes_dispatch.dispatch_notizen, NotizenAgent(), pending, answer,
            )
        return returned, entry, executed, redis

    def test_no_ends_the_graph_without_executing(self) -> None:
        """Ohne den Status im Router liefe das Nein nach `suchen`.

        Die Frage kaeme dann erneut, und angelegt wuerde nichts: Rot wird
        dieser Zeuge deshalb am Status, nicht an `executed`.
        """
        returned, entry, executed, _ = self._answer("nein")
        self.assertEqual(executed, [])
        self.assertEqual(returned["agent_results"][-1].status, "dismissed")
        self.assertEqual(entry["status"], "dismissed")
        self.assertEqual(entry["ergebnis"], _NOTES_REFUSED_TEXT)

    def test_no_leaves_no_pending_state(self) -> None:
        """Der naechste Satz des Menschen darf nicht als Antwort auf die Frage laufen."""
        _, _, _, redis = self._answer("nein")
        redis.delete.assert_called_once_with(f"pending_agent:{_USER}")
        redis.set_json.assert_not_called()

    def test_unclear_answer_renews_the_pending_state(self) -> None:
        """Zwilling: Eine unklare Antwort erneuert die Frage auf demselben Weg."""
        returned, _, executed, redis = self._answer("Wie bitte?")
        self.assertEqual(executed, [])
        self.assertEqual(returned["agent_results"][-1].status, "rueckfrage")
        redis.set_json.assert_called_once()
        key, data = redis.set_json.call_args.args
        self.assertEqual(key, f"pending_agent:{_USER}")
        self.assertEqual(json.loads(data["rueckfrage"])["typ"], "nicht_gefunden")

    def test_no_builds_the_answer_from_the_discarded_block(self) -> None:
        returned, _, _, _ = self._answer("nein")
        expected: str = _discarded_block("notizen", _NOTES_REFUSED_TEXT)
        self.assertEqual(_task_block(returned), (expected, True))

    def test_yes_executes_and_ends_finished(self) -> None:
        """Zwilling: *„ja“* geht durch `ausfuehren` und `bestaetigen`."""
        returned, entry, executed, _ = self._answer("ja")
        self.assertEqual(executed, ["create"])
        self.assertEqual(entry["status"], "abgeschlossen")
        self.assertEqual(entry["ergebnis"], "Notiz 'Einkauf' angelegt")
        self.assertNotIn("Er hat abgelehnt", _task_block(returned)[0])

    def test_the_statuses_that_end_after_resume(self) -> None:
        agent: NotizenAgent = NotizenAgent()
        ended: set[str] = {
            status for status in _CANON | {_RUNNING}
            if agent._nach_resume({"status": status, "parameter": {"action": "create"}}) == END
        }
        self.assertEqual(ended, _NOTES_END_AFTER_RESUME)


class PlannerReaderTest(unittest.TestCase):
    """Nur `dismissed` baut die Antwort aus dem Block der verworfenen Aufgabe."""

    def test_only_dismissed_chooses_the_discarded_block(self) -> None:
        chosen: set[str] = {
            status for status in _CANON
            if "Er hat abgelehnt" in planner._build_task_block([_result(status)])[0]
        }
        self.assertEqual(chosen, _DISCARDED)

    def test_finished_chooses_the_success_block(self) -> None:
        """Zwilling: Der Block des Erfolgs ist ein anderer."""
        block: str = planner._build_task_block([_result("abgeschlossen")])[0]
        self.assertIn("du hast es getan", block)


class ThinkerReaderTest(unittest.TestCase):
    """Der `[VERARBEITUNG]`-Block sagt, der Bestand sei veraendert."""

    def test_only_finished_builds_the_block(self) -> None:
        with_block: set[str] = {
            status for status in _CANON if thinker._build_verarbeitungs_block([_result(status)])
        }
        self.assertEqual(with_block, _SUCCESS)


class _FakeRedis:
    """Die Turns einer Sitzung, so weit `session_turn_mark_action` sie liest."""

    def __init__(self) -> None:
        self.turns: list[str] = [
            json.dumps({"rolle": "user", "inhalt": "Loesch die Regel"}),
            json.dumps({"rolle": "assistant", "inhalt": "Soll ich?"}),
        ]

    def lrange(self, key: str, start: int, end: int) -> list[str]:
        return list(self.turns)

    def lset(self, key: str, index: int, value: str) -> None:
        self.turns[index] = value


class TurnMarkReaderTest(unittest.TestCase):
    """Der Vermerk am Turn des Menschen."""

    def _mark(self, status: str) -> dict:
        """Der Turn des Menschen, nachdem ein Dienst mit diesem Status lief."""
        store: _FakeRedis = _FakeRedis()
        state: dict = {
            "user_id": _USER, "character_id": "nova", "agent_results": [_result(status)],
        }
        with patch.object(dispatcher, "cfg_redis_client", store):
            dispatcher._ausgang_vermerken(state)
        return json.loads(store.turns[0])

    def test_dismissed_marks_nothing(self) -> None:
        turn: dict = self._mark("dismissed")
        self.assertNotIn("aktion_erledigt", turn)
        self.assertNotIn("aktion_erfolgreich", turn)

    def test_the_statuses_that_leave_a_mark(self) -> None:
        marked: set[str] = {s for s in _CANON if "aktion_erledigt" in self._mark(s)}
        self.assertEqual(marked, _MARKED)

    def test_the_statuses_that_count_as_successful(self) -> None:
        successful: set[str] = {s for s in _CANON if self._mark(s).get("aktion_erfolgreich")}
        self.assertEqual(successful, _SUCCESS)


class StorageClaimReaderTest(unittest.TestCase):
    """Die Speicherbehauptung — `direktiven` meldet nicht, ob es schrieb, und deckte das Nein."""

    def test_dismissed_covers_no_claim(self) -> None:
        check = uncovered_claims(_CLAIM, [_result("dismissed")])
        self.assertTrue(check.uncovered)
        self.assertEqual(check.result, "nicht_belegt")
        self.assertEqual(check.outcomes, ("direktiven:dismissed",))

    def test_only_finished_covers(self) -> None:
        covering: set[str] = {
            status for status in _CANON
            if not uncovered_claims(_CLAIM, [_result(status)]).uncovered
        }
        self.assertEqual(covering, _SUCCESS)


class TribunalReaderTest(unittest.TestCase):
    """Nur ein ausgefuehrter Dienst belegt ein Datum."""

    def _summary(self, status: str) -> str:
        """Die Zusammenfassung zu einer Antwort mit einem anderen Datum als die Quelle."""
        state: dict = {
            "response": "Er steht am 20.08.2026 um 14 Uhr.",
            "agent_results": [_result(status, _SOURCE)],
            "tribunal_votes": [
                {"agent": name, "vote": "ok", "reasoning": ""}
                for name in ("jurist", "psychologe", "ethik")
            ],
        }
        with patch.object(tribunal, "log_berechnung"):
            return tribunal.evaluate(state)["tribunal_summary"]

    def test_only_finished_is_a_source(self) -> None:
        sources: set[str] = {s for s in _CANON if "ZEITANGABE FALSCH" in self._summary(s)}
        self.assertEqual(sources, _SUCCESS)


if __name__ == "__main__":
    unittest.main()
