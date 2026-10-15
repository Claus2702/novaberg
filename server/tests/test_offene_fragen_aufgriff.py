"""Zeugen: Je Turn ist ablesbar, ob eine angebotene offene Frage aufgegriffen wurde.

Ziel: Der Eintrag `offene_fragen_aufgriff` im `pipeline_log` unterscheidet
*nicht angeboten*, *angeboten, nicht aufgegriffen*, *aufgegriffen* und *nicht
beurteilbar* — und verwechselt nie einen Ausfall mit *nicht aufgegriffen*.

Datenbank und Embed-Dienst sind ersetzt; die Zeugen laufen ohne Modell. Was die
Doubles nicht sehen: die Naehe selbst, die in der Datenbank gerechnet wird. Sie
wird in der Messreihe des Betriebs gelesen, nicht hier.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from graph.nodes import aufgriff
from graph.nodes.aufgriff import (
    NOT_JUDGEABLE,
    NOT_OFFERED,
    NOT_TAKEN_UP,
    TAKE_UP_MIN_PROXIMITY,
    TAKEN_UP,
    judge_take_up,
    offene_fragen_aufgriff,
)
from memory.repositories import wissensluecken_repository as repo

VEC: list[float] = [0.1, 0.2, 0.3]
DB_SELECT: str = "memory.repositories.wissensluecken_repository.db_manager.select"


def make_state(ids: list[int] | str | None, response: str = "Eine Antwort.") -> dict:
    """Ein Zustand hinter der Freigabe; `ids=None` laesst den Schluessel weg."""
    state: dict = {
        "user_id": "meister", "character_id": "nova", "turn_id": "t-1",
        "response": response, "correction_round": 0,
    }
    if ids is not None:
        state["offene_fragen_ids"] = ids
    return state


def run_node(
    state: dict,
    proximities: dict[int, float] | None = None,
    embedding: list[float] = VEC,
    embed_error: Exception | None = None,
    read_error: Exception | None = None,
) -> tuple[dict, MagicMock, MagicMock]:
    """Faehrt den Knoten mit Doubles; liefert (Eintrag, Embed-Double, Lese-Double)."""
    embed = MagicMock()
    if embed_error is not None:
        embed.submit_sync.side_effect = embed_error
    else:
        embed.submit_sync.return_value = SimpleNamespace(embedding=embedding)
    service = SimpleNamespace(embed=embed)
    read = MagicMock(return_value=proximities or {})
    if read_error is not None:
        read.side_effect = read_error
    with patch.object(aufgriff, "model_service", service), \
            patch.object(aufgriff, "gap_proximities", read), \
            patch.object(aufgriff, "log_berechnung") as log:
        result = offene_fragen_aufgriff(state)
    assert result is state, "der Knoten gibt den Zustand zurueck"
    assert log.call_count == 1, f"genau ein Eintrag je Turn, nicht {log.call_count}"
    return log.call_args.kwargs["inhalt"], embed, read


class IdTravelsTest(unittest.TestCase):
    """`staerkste_luecken` liefert die `id`; der GV-Node gibt sie an die Spur."""

    def test_query_selects_the_id(self) -> None:
        with patch(DB_SELECT, return_value=[]) as db:
            repo.staerkste_luecken("meister", "nova", VEC)
        self.assertIn("SELECT id, thema", db.call_args.args[0])

    def test_row_carries_the_id_on(self) -> None:
        row = {"id": 41, "thema": "Wurmloecher", "neugier_vektor": 0.1, "neuheit": 0.6,
               "resonanz": 0.3, "herkunft": "turn", "alter_tage": 2, "naehe": 0.6}
        with patch(DB_SELECT, return_value=[row]):
            self.assertEqual(repo.staerkste_luecken("meister", "nova", VEC)[0]["id"], 41)

    def test_gv_node_sets_the_ids_before_the_trace(self) -> None:
        from graph.nodes import gespraechsvektor as gv

        source = inspect.getsource(gv)
        assign = source.index('state["offene_fragen_ids"] = offene_fragen_ids')
        trace = source.index('"schritt":              "strategie_tor"')
        self.assertGreater(assign, source.index("offene_fragen = staerkste_luecken"))
        self.assertLess(assign, trace)
        self.assertIn('"offene_fragen_ids":    offene_fragen_ids', source[trace:])


class ProximityQueryTest(unittest.TestCase):
    """`gap_proximities`: nur die gefragten Kennungen, Fehler werden geworfen."""

    def test_filter_and_parameters(self) -> None:
        with patch(DB_SELECT, return_value=[{"id": 5, "naehe": 0.7}]) as db:
            result = repo.gap_proximities("meister", "nova", [5, 6], VEC)
        self.assertEqual(result, {5: 0.7})
        self.assertIn("user_id = %s AND character_id = %s AND id = ANY(%s)", db.call_args.args[0])
        self.assertEqual(db.call_args.args[1][-1], [5, 6])

    def test_a_database_error_is_raised_instead_of_becoming_empty(self) -> None:
        with patch(DB_SELECT, side_effect=OSError("weg")):
            with self.assertRaises(OSError):
                repo.gap_proximities("meister", "nova", [5], VEC)

    def test_an_id_that_was_not_asked_for_is_an_error(self) -> None:
        with patch(DB_SELECT, return_value=[{"id": 99, "naehe": 0.9}]):
            with self.assertRaises(RuntimeError):
                repo.gap_proximities("meister", "nova", [5], VEC)

    def test_invalid_inputs(self) -> None:
        for args in (("", "nova", [5], VEC), ("meister", "", [5], VEC),
                     ("meister", "nova", [], VEC), ("meister", "nova", [True], VEC),
                     ("meister", "nova", [5], []), ("meister", "nova", [5], [float("nan")])):
            with self.subTest(args=args), self.assertRaises(ValueError):
                repo.gap_proximities(*args)


class VerdictTest(unittest.TestCase):
    """Die reine Entscheidung aus den gerechneten Naehen."""

    def test_the_threshold_is_spelled_out(self) -> None:
        self.assertEqual(TAKE_UP_MIN_PROXIMITY, 0.55)

    def test_exactly_on_the_threshold_is_taken_up_below_it_is_not(self) -> None:
        self.assertEqual(judge_take_up([1, 2], {1: 0.55, 2: 0.549}, 0.55), (TAKEN_UP, [1], ""))
        self.assertEqual(judge_take_up([1], {1: 0.549}, 0.55), (NOT_TAKEN_UP, [], ""))

    def test_missing_proximity_is_not_judgeable_never_not_taken_up(self) -> None:
        outcome, taken, reason = judge_take_up([1, 2], {1: 0.1}, 0.55)
        self.assertEqual((outcome, taken), (NOT_JUDGEABLE, []))
        self.assertIn("2", reason)

    def test_a_taken_up_question_counts_despite_another_missing(self) -> None:
        self.assertEqual(judge_take_up([1, 2], {1: 0.9}, 0.55)[0], TAKEN_UP)

    def test_a_topic_that_was_not_offered_never_counts(self) -> None:
        with self.assertRaises(ValueError):
            judge_take_up([1], {1: 0.1, 7: 0.99}, 0.55)


class NodeWritesOneEntryTest(unittest.TestCase):
    """Der Knoten schreibt je Turn genau einen Eintrag mit dem passenden Ausgang."""

    def test_taken_up_with_exactly_its_id(self) -> None:
        entry, _, _ = run_node(make_state([11, 12, 13]), {11: 0.2, 12: 0.7, 13: 0.3})
        self.assertEqual(entry["schritt"], "offene_fragen_aufgriff")
        self.assertEqual(entry["ausgang"], TAKEN_UP)
        self.assertEqual(entry["aufgegriffen"], [12])
        self.assertEqual(entry["angeboten"], [11, 12, 13])
        self.assertEqual(entry["naehen"], {"11": 0.2, "12": 0.7, "13": 0.3})
        self.assertEqual(entry["schwelle"], 0.55)
        self.assertEqual(entry["mass"], "cosinus_antwort_thema")

    def test_offered_not_taken_up(self) -> None:
        entry, _, _ = run_node(make_state([11, 12]), {11: 0.2, 12: 0.3})
        self.assertEqual(entry["ausgang"], NOT_TAKEN_UP)
        self.assertEqual(entry["aufgegriffen"], [])
        self.assertEqual(entry["grund"], "")

    def test_only_offered_ids_are_asked_for(self) -> None:
        _, _, read = run_node(make_state([11]), {11: 0.1})
        self.assertEqual(read.call_args.args[2], [11])

    def test_an_id_not_offered_in_the_query_result_does_not_count(self) -> None:
        entry, _, _ = run_node(make_state([11]), {11: 0.1, 99: 0.99})
        self.assertEqual(entry["ausgang"], NOT_JUDGEABLE)
        self.assertEqual(entry["aufgegriffen"], [])

    def test_no_offer_empty_list_and_missing_key(self) -> None:
        for ids in ([], None):
            with self.subTest(ids=ids):
                entry, embed, read = run_node(make_state(ids))
                self.assertEqual(entry["ausgang"], NOT_OFFERED)
                self.assertEqual(entry["angeboten"], [])
                self.assertEqual(entry["aufgegriffen"], [])
                embed.submit_sync.assert_not_called()
                read.assert_not_called()


class NotJudgeableIsLoudTest(unittest.TestCase):
    """Jeder Ausfall ergibt den vierten Ausgang mit Grund — und der Turn laeuft weiter."""

    def check(self, entry: dict, reason_prefix: str) -> None:
        self.assertEqual(entry["ausgang"], NOT_JUDGEABLE)
        self.assertTrue(entry["grund"].startswith(reason_prefix), entry["grund"])
        self.assertEqual(entry["aufgegriffen"], [])
        self.assertEqual(entry["angeboten"], [11])

    def test_embed_service_fails(self) -> None:
        entry, _, _ = run_node(make_state([11]), embed_error=OSError("aus"))
        self.check(entry, "embedding_fehlgeschlagen:OSError")

    def test_empty_vector(self) -> None:
        entry, _, _ = run_node(make_state([11]), embedding=[])
        self.check(entry, "embedding_leer")

    def test_empty_answer(self) -> None:
        entry, embed, _ = run_node(make_state([11], response="  "))
        self.check(entry, "antwort_leer")
        embed.submit_sync.assert_not_called()

    def test_read_error(self) -> None:
        entry, _, _ = run_node(make_state([11]), read_error=OSError("db"))
        self.check(entry, "lesefehler:OSError")

    def test_missing_proximity(self) -> None:
        entry, _, _ = run_node(make_state([11]), {})
        self.check(entry, "kennung_ohne_naehe")

    def test_invalid_ids(self) -> None:
        entry, _, _ = run_node(make_state("11"))
        self.assertEqual(entry["ausgang"], NOT_JUDGEABLE)
        self.assertEqual(entry["grund"], "kennungen_ungueltig")

    def test_an_unexpected_error_does_not_stop_the_turn(self) -> None:
        with patch.object(aufgriff, "judge_take_up", side_effect=KeyError("x")):
            entry, _, _ = run_node(make_state([11]), {11: 0.9})
        self.check_unexpected(entry)

    def check_unexpected(self, entry: dict) -> None:
        self.assertEqual(entry["ausgang"], NOT_JUDGEABLE)
        self.assertEqual(entry["grund"], "unerwartet:KeyError")


class GraphNodeCallsTheNodeTest(unittest.TestCase):
    """`GraphBase._node_aufgriff` reicht den Zustand an den Knoten weiter."""

    def test_node_aufgriff_calls_the_node_and_returns_its_result(self) -> None:
        from graph.base import GraphBase

        state = make_state([11])
        answer: dict = {"anderer": "zustand"}
        with patch.object(aufgriff, "offene_fragen_aufgriff", return_value=answer) as node:
            result = GraphBase._node_aufgriff(None, state)
        node.assert_called_once_with(state)
        self.assertIs(result, answer)


class FinalAnswerTest(unittest.TestCase):
    """Das Urteil liest die Antwort nach der letzten Korrekturrunde."""

    def test_the_vector_comes_from_the_text_in_the_state_at_the_call(self) -> None:
        state = make_state([11], response="Erste Fassung ohne das Thema.")
        state["response"] = "Korrigierte Fassung mit dem Thema Wurmloecher."  # der Corrector
        _, embed, _ = run_node(state, {11: 0.8})
        text = embed.submit_sync.call_args.args[0].text
        self.assertEqual(text, "Korrigierte Fassung mit dem Thema Wurmloecher.")

    def test_the_node_sits_behind_the_release(self) -> None:
        from graph import character_graph

        source = inspect.getsource(character_graph)
        self.assertIn('graph.add_edge("praegung",            "aufgriff")', source)
        self.assertIn('graph.add_edge("aufgriff",            "dispatcher")', source)
        self.assertEqual(source.count('"aufgriff"'), 3, "nur Knoten und zwei Kanten")
        self.assertIn('"output":    "perzeption_assistant"', source)
        self.assertIn('graph.add_edge("corrector",           "tribunal")', source)


if __name__ == "__main__":
    unittest.main()
