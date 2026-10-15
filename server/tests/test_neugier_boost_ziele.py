"""Zeugen: Der Neugier-Boost einer Wissensluecke kommt aus den aktivierten Zielen.

Ziel: Eine Wissensluecke, deren **Thema** nah an einem aktivierten Ziel liegt,
bekommt einen Neugier-Boost ueber 0, eine fern von allen Zielen keinen — je
Kandidat, nicht je Turn. Ein Ziel ohne Vektor wird gezaehlt und gemeldet.
Vorher las Schritt 4 `ziel["embedding"]`, das der Enricher absichtlich nicht in
den State legt: Der Boost war in jedem Turn 0,0.

Ohne Datenbank, ohne Redis und ohne Modell: Ziele und Vektoren sind synthetisch,
und jede Quelle, die der Luecken-Pfad liest (Kandidaten aus LZG und KZG,
Gewichtsverteilung, Themenbestand des Nutzers, Einbettung von Themen und Kern),
ist ein Doppel. Die Zeugen ergeben gegen jeden Bestand dasselbe.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import math
import unittest
import uuid
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from config import GV_NEUGIER_BOOST_SCHWELLE
from ei.gap_topics import UserTopics
from ei.gravitation import ActivatedGoal, Gravitationsterm
from ei.wissensluecken import _neugier_boosts, wissensluecken_finden
from graph.nodes import dispatcher as dispatcher_mod
from graph.nodes import enricher as enricher_mod

TURN: list[float] = [1.0] + [0.0] * 7
GOAL: list[float] = [0.0, 0.0, 0.0, 1.0] + [0.0] * 4
# Der Kern liegt zwischen Achse 1 und Ziel: Jedes Thema besteht den Charakter-Filter.
CORE: list[float] = [0.0, 1.0, 0.0, 1.0] + [0.0] * 4
# Ein zweites Ziel, zu dem kein Thema der Zeugen Naehe hat.
OTHER: list[float] = [0.0] * 5 + [1.0, 0.0, 0.0]
# Der Turn nennt keines der Themen der Zeugen, sonst gilt es als bereits erwaehnt.
PROMPT: str = "Erzaehl mir etwas ueber deinen Tag."


def topic(closeness_to_goal: float) -> list[float]:
    """Ein Einheitsvektor mit festgelegtem Cosinus zum Ziel (Achse 3) und 0,3 zum Turn."""
    rest = 1.0 - closeness_to_goal**2 - 0.09
    return [0.3, math.sqrt(max(rest, 0.0)), 0.0, closeness_to_goal] + [0.0] * 4


def goal(goal_id: int = 1, motivation: float = 0.8, kind: str = "mittelfristig") -> dict:
    """Ein aktiviertes Ziel, wie `_ziele_als_dicts` es im State ablegt (ohne Vektor)."""
    return {"ziel_id": goal_id, "ziel_typ": kind, "zielsatz": "x", "motivation": motivation,
            "emotion": "", "arousal": 0.5, "similarity": 0.5, "aktivierungs_staerke": 0.4}


def node(concept: str) -> dict:
    """Ein Kandidat aus dem Bestand, der genau ein Thema traegt."""
    return {"konzept": "Nova hat etwas erklaert", "similarity": 0.6, "gewicht": 5.0,
            "gewicht_rang": 0.8, "gap_arousal": 0.3, "quelle": "lzg", "themen": [concept]}


class BoostIsComputedPerTopic(unittest.TestCase):
    """`_neugier_boosts` — Naehe des Themas zum Ziel mal Motivation."""

    def test_topic_near_goal_carries_a_boost(self) -> None:
        """Nah am Ziel: Naehe mal Motivation."""
        boosts, _ = _neugier_boosts([topic(0.9)], [goal(motivation=0.8)], {1: GOAL})
        self.assertAlmostEqual(boosts[0], 0.9 * 0.8)

    def test_two_topics_of_one_turn_carry_different_boosts(self) -> None:
        """Je Kandidat, nicht je Turn: der ferne Kandidat bleibt bei 0."""
        boosts, _ = _neugier_boosts([topic(0.9), topic(0.1)], [goal()], {1: GOAL})
        self.assertGreater(boosts[0], 0.0)
        self.assertEqual(boosts[1], 0.0)

    def test_below_threshold_is_zero(self) -> None:
        """Unter der Schwelle gibt es keinen Boost."""
        near = (GV_NEUGIER_BOOST_SCHWELLE - 0.05) / 0.8
        boosts, _ = _neugier_boosts([topic(near)], [goal(motivation=0.8)], {1: GOAL})
        self.assertEqual(boosts, [0.0])

    def test_on_threshold_still_counts(self) -> None:
        """Zwilling zu *unter der Schwelle*: Die Grenze liegt bei `>=`."""
        motivation = GV_NEUGIER_BOOST_SCHWELLE / 0.5
        boosts, _ = _neugier_boosts([topic(0.5)], [goal(motivation=motivation)], {1: GOAL})
        self.assertAlmostEqual(boosts[0], GV_NEUGIER_BOOST_SCHWELLE)

    def test_without_active_goals_is_zero(self) -> None:
        """Ohne aktivierte Ziele: Boost 0 und nichts zu melden."""
        boosts, report = _neugier_boosts([topic(0.9)], [], {})
        self.assertEqual(boosts, [0.0])
        self.assertEqual(report["ziele"], 0)

    def test_strongest_goal_wins(self) -> None:
        """Das Maximum ueber die Ziele gilt; der Bericht zaehlt beide als beitragend."""
        goals = [goal(1, motivation=0.4), goal(2, motivation=0.9)]
        boosts, report = _neugier_boosts([topic(0.9)], goals, {1: GOAL, 2: GOAL})
        self.assertAlmostEqual(boosts[0], 0.9 * 0.9)
        self.assertEqual(report["beitragend"], 2)
        self.assertAlmostEqual(report["hoechster"], 0.81, places=4)

    def test_short_term_goal_counts_too(self) -> None:
        """Kurzfristige Ziele sind per Bauart aktiviert; die Formel trennt die Horizonte nicht."""
        boosts, _ = _neugier_boosts([topic(0.9)], [goal(kind="kurzfristig")], {1: GOAL})
        self.assertGreater(boosts[0], 0.0)


class GoalWithoutVectorIsReported(unittest.TestCase):
    """Zaehlen statt still ueberspringen — der Boost der uebrigen bleibt."""

    def test_it_is_counted_and_the_rest_still_computes(self) -> None:
        """Ziel 1 hat keinen Vektor; Ziel 2 traegt den Boost."""
        goals = [goal(1), goal(2, motivation=0.6)]
        boosts, report = _neugier_boosts([topic(0.9)], goals, {2: GOAL})
        self.assertAlmostEqual(boosts[0], 0.9 * 0.6)
        self.assertEqual(report["unbrauchbar"], 1)
        self.assertEqual(report["ziele"], 2)

    def test_empty_vector_counts_as_none(self) -> None:
        """Ein leerer Vektor ist wie keiner."""
        _, report = _neugier_boosts([topic(0.9)], [goal(1)], {1: []})
        self.assertEqual(report["unbrauchbar"], 1)

    def test_goal_without_motivation_is_unusable(self) -> None:
        """Die Motivation ist Pflichtfeld: ohne sie traegt das Ziel nichts bei."""
        broken = {k: v for k, v in goal(1).items() if k != "motivation"}
        boosts, report = _neugier_boosts([topic(0.9)], [broken], {1: GOAL})
        self.assertEqual(boosts, [0.0])
        self.assertEqual(report["unbrauchbar"], 1)

    def test_all_usable_counts_zero(self) -> None:
        """Zwilling: Der Zaehler schlaegt nicht ohne Anlass an."""
        _, report = _neugier_boosts([topic(0.9)], [goal(1)], {1: GOAL})
        self.assertEqual(report["unbrauchbar"], 0)


class TraceAndErrorThroughTheGapPath(unittest.TestCase):
    """`wissensluecken_finden` — Boost je Kandidat, Zeile in der Spur, Fehler im Log."""

    def find(
        self, extra_state: dict, topics: dict[str, list[float]],
    ) -> tuple[list[dict], MagicMock, MagicMock]:
        """Faehrt den Luecken-Pfad mit gedoppelten Quellen; liefert Ergebnis, Log und Spur."""
        emotion = SimpleNamespace(mode="alltag", relationship_dynamic="neutral")
        internal = SimpleNamespace(emotion=emotion, character=SimpleNamespace(core="ein Kern"))
        distribution = {"lzg": [5.0], "kzg": [0.5]}
        state = {"user_prompt": PROMPT, "user_id": "mensch",
                 "character_id": "figur", "prompt_embedding": TURN, "internal": internal,
                 "session_turns": [], "turn_id": "t-boost", **extra_state}
        nodes = [node(t) for t in topics]
        with patch("ei.wissensluecken.lzg_kandidaten_suchen", return_value=nodes), \
             patch("ei.wissensluecken.kzg_kandidaten_suchen", return_value=[]), \
             patch("ei.wissensluecken.load_weight_distributions", return_value=distribution), \
             patch("ei.wissensluecken.load_user_topics", return_value=UserTopics(set(), set())), \
             patch("ei.wissensluecken.embed_topics",
                   side_effect=lambda names: {name: topics[name] for name in names}), \
             patch("ei.wissensluecken.model_service.embed.submit_sync",
                   return_value=SimpleNamespace(embedding=CORE)), \
             patch("ei.wissensluecken.logger") as log, \
             patch("ei.wissensluecken.log_berechnung") as trace:
            result = wissensluecken_finden(state, aufnahmebereitschaft=1.0)
        return result, log, trace

    def test_near_carries_a_boost_far_none_in_the_same_turn(self) -> None:
        """Beide Themen liegen gleich nah am Turn (0,3); nur das Ziel trennt sie."""
        result, _, _ = self.find(
            {"aktivierte_ziele": [goal()], "ziel_vektoren": {1: GOAL}},
            {"Gamma-Kohaerenz": topic(0.9), "Kaffee": topic(0.1)},
        )
        boost = {k["konzept"]: k["neugier_boost"] for k in result}
        self.assertGreater(boost["Gamma-Kohaerenz"], 0.0)
        self.assertEqual(boost["Kaffee"], 0.0)

    def test_boost_lifts_the_relevance_of_the_near_topic(self) -> None:
        """Das nahe Thema steht an der Spitze, obwohl beide gleich nah am Turn liegen."""
        result, _, _ = self.find(
            {"aktivierte_ziele": [goal()], "ziel_vektoren": {1: GOAL}},
            {"Gamma-Kohaerenz": topic(0.9), "Kaffee": topic(0.1)},
        )
        self.assertEqual(result[0]["konzept"], "Gamma-Kohaerenz")

    def test_trace_carries_numbers_and_no_goal_texts(self) -> None:
        """Die Spurzeile nennt Zahlen (2 Ziele, 1 unbrauchbar, 1 beitragend), keinen Zieltext."""
        _, _, trace = self.find(
            {"aktivierte_ziele": [goal(1), goal(2)], "ziel_vektoren": {1: GOAL}},
            {"Gamma-Kohaerenz": topic(0.9)},
        )
        lines = [c.kwargs["inhalt"] for c in trace.call_args_list
                 if c.kwargs["inhalt"].get("schritt") == "gv4_neugier_boost"]
        self.assertEqual(len(lines), 1)
        self.assertEqual((lines[0]["ziele"], lines[0]["unbrauchbar"], lines[0]["beitragend"]),
                         (2, 1, 1))
        self.assertGreater(lines[0]["hoechster"], 0.0)
        self.assertNotIn("zielsatz", json.dumps(lines[0]))

    def test_goal_without_vector_is_an_error_in_the_log(self) -> None:
        """Ein aktiviertes Ziel ohne Vektor steht als Fehler im Log."""
        _, log, _ = self.find(
            {"aktivierte_ziele": [goal(1)], "ziel_vektoren": {}},
            {"Gamma-Kohaerenz": topic(0.9)},
        )
        self.assertTrue(log.error.called)

    def test_without_goals_no_trace_line_and_no_error(self) -> None:
        """Zwilling zu den beiden vorigen: Ohne aktivierte Ziele gibt es nichts zu melden."""
        _, log, trace = self.find({"aktivierte_ziele": []}, {"Gamma-Kohaerenz": topic(0.9)})
        steps = [c.kwargs["inhalt"].get("schritt") for c in trace.call_args_list]
        self.assertNotIn("gv4_neugier_boost", steps)
        self.assertFalse(log.error.called)


class VectorTravelsBesideTheListAndNotToRedis(unittest.TestCase):
    """Enricher legt die Vektoren in `ziel_vektoren`; der Dispatcher legt sie nicht ab."""

    @staticmethod
    def activated(goal_id: int, embedding: list[float] | None) -> SimpleNamespace:
        """Ein `ActivatedGoal`-Doppel mit den Feldern, die der Enricher liest."""
        return SimpleNamespace(
            ziel_id=goal_id, ziel_typ="mittelfristig", zielsatz="x", motivation=0.5,
            emotion="", arousal=0.5, similarity=0.5, aktivierungs_staerke=0.4,
            embedding=embedding,
        )

    def test_goal_dicts_carry_no_vector(self) -> None:
        """Das Dict im State bleibt vektorfrei."""
        dicts = enricher_mod._ziele_als_dicts([self.activated(1, GOAL)])
        self.assertNotIn("embedding", dicts[0])

    def test_vectors_come_per_goal_id(self) -> None:
        """`_ziel_vektoren` ordnet die Vektoren der `ziel_id` zu."""
        vectors = enricher_mod._ziel_vektoren([self.activated(1, GOAL), self.activated(2, [1.0])])
        self.assertEqual(vectors, {1: GOAL, 2: [1.0]})

    def test_goal_without_embedding_is_missing_and_an_error(self) -> None:
        """Ein Ziel ohne Embedding fehlt im Ergebnis und steht als Fehler im Log."""
        with patch.object(enricher_mod, "logger") as log:
            vectors = enricher_mod._ziel_vektoren(
                [self.activated(1, None), self.activated(2, GOAL)]
            )
        self.assertEqual(list(vectors), [2])
        self.assertTrue(log.error.called)

    def test_storage_to_redis_carries_no_vectors(self) -> None:
        """Die Ablage enthaelt weder Vektorwerte noch den Schluessel `ziel_vektoren`."""
        state = {"user_id": "mensch", "character_id": "figur",
                 "aktivierte_ziele": [goal()], "ziel_vektoren": {1: [0.123456, 0.0]}}
        redis = MagicMock()
        with patch.object(dispatcher_mod, "cfg_redis_client", redis):
            dispatcher_mod._persist_short_term_drive(state)
        written = redis.set.call_args.args[1]
        self.assertEqual(len(json.loads(written)["activated_goals"]), 1)
        self.assertNotIn("0.123456", written)
        self.assertNotIn("ziel_vektoren", written)


class EnricherPathsSetTheGoalVectors(unittest.TestCase):
    """Beide Pfade des Enrichers setzen `state["ziel_vektoren"]` aus den aktivierten Zielen.

    Hier sass der urspruengliche Fehler: Der Vektor erreichte den Schritt nicht. Die Gravitation
    ist gedoppelt, Datenbank, Redis und Modell sind Attrappen; geprueft wird der Zustand, den
    die Funktion setzt, die den Zustand setzt.
    """

    @staticmethod
    def activated() -> list[ActivatedGoal]:
        """Zwei aktivierte Ziele mit verschiedenen Vektoren."""
        return [
            ActivatedGoal(1, "langfristig", "x", 0.8, "", 0.5, 0.5, 0.4, embedding=GOAL),
            ActivatedGoal(2, "kurzfristig", "y", 0.6, "", 0.5, 0.5, 0.3, embedding=OTHER),
        ]

    @staticmethod
    def redis_double() -> MagicMock:
        """Redis ohne Schluessel und ohne Werte."""
        redis = MagicMock()
        redis.get.return_value = None
        redis.keys.return_value = []
        return redis

    def run_path(self, name: str, state: dict) -> dict:
        """Faehrt `_enrich_human` oder `_enrich_character` mit gedoppelten Quellen."""
        connection = MagicMock()
        connection.cursor.return_value.fetchone.return_value = (False,)
        psycopg2_double = MagicMock()
        psycopg2_double.connect.return_value = connection
        finding = SimpleNamespace(treffer=[])
        with ExitStack() as stack:
            enter = stack.enter_context
            enter(patch.object(enricher_mod, "psycopg2", psycopg2_double))
            enter(patch.object(enricher_mod, "_load_raw_turns", return_value=[]))
            enter(patch.object(enricher_mod, "_create_prompt_embedding", return_value=TURN))
            enter(patch.object(
                enricher_mod, "_compute_ziele_und_gravitation",
                return_value=(self.activated(), Gravitationsterm(1.0, 0.5, 6.0), 0.0),
            ))
            enter(patch.object(enricher_mod, "get_registry", return_value={}))
            enter(patch.object(enricher_mod, "aufzeichnungen_suchen", return_value=finding))
            enter(patch.object(enricher_mod, "emotionale_gravitation_scannen", return_value=[]))
            enter(patch.object(enricher_mod, "span_start", return_value=uuid.uuid4()))
            for logger_name in ("span_end", "log_eingang", "log_switch", "log_ausgabe",
                                "log_berechnung"):
                enter(patch.object(enricher_mod, logger_name))
            return getattr(enricher_mod, name)(state, self.redis_double(), "postgresql://t", "u")

    def test_human_path_sets_the_vectors_of_the_active_goals(self) -> None:
        """HumanGraph: je aktiviertem Ziel der Vektor, im Dict kein Vektor."""
        state = self.run_path("_enrich_human", {"turn_id": "t", "user_prompt": "Hallo"})
        self.assertEqual(state["ziel_vektoren"], {1: GOAL, 2: OTHER})
        self.assertEqual([g["ziel_id"] for g in state["aktivierte_ziele"]], [1, 2])
        self.assertTrue(all("embedding" not in g for g in state["aktivierte_ziele"]))

    def test_character_path_sets_the_vectors_of_the_active_goals(self) -> None:
        """CharacterGraph: je aktiviertem Ziel der Vektor, im Dict kein Vektor."""
        state = self.run_path("_enrich_character", {
            "turn_id": "t", "character_id": "c", "user_prompt": "Hallo",
            "ei_calc_rolle": "character",
        })
        self.assertEqual(state["ziel_vektoren"], {1: GOAL, 2: OTHER})
        self.assertTrue(all("embedding" not in g for g in state["aktivierte_ziele"]))

    def test_vectors_from_the_enricher_reach_the_boost(self) -> None:
        """Der ganze Weg in einem Zug: Zustand des Enrichers, dann `_neugier_boosts`."""
        state = self.run_path("_enrich_human", {"turn_id": "t", "user_prompt": "Hallo"})
        boosts, report = _neugier_boosts(
            [topic(0.9), topic(0.1)], state["aktivierte_ziele"], state["ziel_vektoren"],
        )
        self.assertAlmostEqual(boosts[0], 0.9 * 0.8)
        self.assertEqual(boosts[1], 0.0)
        self.assertEqual(report["unbrauchbar"], 0)


if __name__ == "__main__":
    unittest.main()
