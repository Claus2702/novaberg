"""Zeugen fuer die Suchdisziplin des Thinkers.

Anlass, gemessen am 29.08.2026 ueber 20 Turns: Der Thinker rief die
Suchmaschine 23-mal, bis zu dreimal je Turn, und die Wikipedia-API sperrte
zweimal fuer 180 s — die eine Suche der Sachlage-Recherche ging leer aus.
Seither: eine Suche je Turn (`THINKER_WEBSUCHE_MAX_JE_TURN`), und die
Treffer der Sachlage-Recherche sind diese Suche, wenn es sie gibt.

Zeugen dieser Datei:
  * **Das Budget zaehlt und faellt laut**: erlaubt, verbucht, verbraucht;
    ein Verbuchen ohne Rest und ein unbrauchbares Budget sind Defekte.
  * **Die Suchmaschine wird je Turn einmal gerufen** — der zweite Aufruf mit
    anderen Worten bekommt eine Fuehrung statt einer Suche, mit Logzeile;
    auch ein leerer und ein gescheiterter Aufruf zaehlen.
  * **Die Sachlage-Treffer bedienen die erste Suche** — ohne Aufruf der
    Suchmaschine, mit Nachladen des ersten Treffers, und sie zaehlen.
  * **`prior_research` liest nur akute Objekte mit Treffern** und meldet
    unbrauchbare Formen.
  * **`think` reicht die Treffer an die Werkzeuge** (die Verdrahtung).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from graph.nodes import thinker as thinker_mod
from graph.nodes.thinker import (
    create_tools,
    format_search_results,
    prior_research,
    think,
)
from graph.nodes.thinker_cache import ThinkerToolCache

HITS: list[dict] = [
    {"title": "Magnetar", "url": "https://de.wikipedia.org/wiki/Magnetar",
     "content": "Ein Magnetar ist ein Neutronenstern mit extrem starkem Magnetfeld."},
    {"title": "SGR 1806-20", "url": "https://de.wikipedia.org/wiki/SGR_1806-20",
     "content": "SGR 1806-20 ist ein Magnetar in etwa 50.000 Lichtjahren Entfernung."},
]
PRIOR: dict = {"objekt": "Magnetar", "eigenschaft": "Entfernung", "treffer": HITS}


def _tool_map(cache: ThinkerToolCache, prior: dict | None = None) -> dict:
    """Die Werkzeuge eines Turns, nach Namen."""
    tools = create_tools("postgresql://unbenutzt", "u", "c", cache, prior)
    return {t.name: t for t in tools}


class BudgetTest(unittest.TestCase):
    """Das Suchbudget des Turns zaehlt und faellt laut."""

    def test_default_budget_is_one_search(self) -> None:
        cache = ThinkerToolCache()
        self.assertTrue(cache.web_search_allowed())
        cache.web_search_spent()
        self.assertFalse(cache.web_search_allowed())

    def test_zero_budget_never_allows(self) -> None:
        self.assertFalse(ThinkerToolCache(web_search_budget=0).web_search_allowed())

    def test_two_searches_when_configured(self) -> None:
        cache = ThinkerToolCache(web_search_budget=2)
        cache.web_search_spent()
        self.assertTrue(cache.web_search_allowed())
        cache.web_search_spent()
        self.assertFalse(cache.web_search_allowed())

    def test_unusable_budget_is_rejected(self) -> None:
        for kaputt in (-1, 1.5, "1", True, None):
            with self.subTest(budget=kaputt):
                with self.assertRaises(ValueError):
                    ThinkerToolCache(web_search_budget=kaputt)

    def test_spending_without_rest_fails_loud(self) -> None:
        cache = ThinkerToolCache(web_search_budget=0)
        with self.assertRaises(RuntimeError):
            cache.web_search_spent()

    def test_spending_is_logged(self) -> None:
        with self.assertLogs("ki_server.thinker.cache", level="INFO") as logs:
            ThinkerToolCache(web_search_budget=1).web_search_spent()
        self.assertTrue(any("Rest 0" in z for z in logs.output), logs.output)


class EngineCalledOncePerTurnTest(unittest.TestCase):
    """Die Suchmaschine wird je Turn einmal gerufen — danach Fuehrung."""

    def test_second_search_gets_guidance_and_log(self) -> None:
        tools = _tool_map(ThinkerToolCache(web_search_budget=1))
        with patch.object(thinker_mod.web_search_manager, "suchen", return_value=HITS) as suchen, \
                patch.object(thinker_mod, "page_fetch", return_value="Der Volltext") as fetch:
            erste = tools["web_search"].invoke("Magnetar Entfernung")
            with self.assertLogs("ki_server.thinker", level="INFO") as logs:
                zweite = tools["web_search"].invoke("nearest magnetar distance")
        self.assertEqual(suchen.call_count, 1)
        self.assertEqual(fetch.call_count, 1)
        self.assertIn("Web-Ergebnisse fuer 'Magnetar Entfernung' (Suchmaschine)", erste)
        self.assertIn("SGR 1806-20", erste)
        self.assertIn("Der Volltext", erste)
        self.assertIn("web_fetch(url)", zweite)
        self.assertNotIn("Web-Ergebnisse", zweite)
        self.assertTrue(
            any("Suchbudget des Turns verbraucht" in z for z in logs.output), logs.output,
        )

    def test_empty_result_still_counts(self) -> None:
        tools = _tool_map(ThinkerToolCache(web_search_budget=1))
        with patch.object(thinker_mod.web_search_manager, "suchen", return_value=[]) as suchen, \
                patch.object(thinker_mod, "page_fetch", return_value="") as fetch:
            erste = tools["web_search"].invoke("Magnetar Entfernung")
            zweite = tools["web_search"].invoke("Magnetar Abstand")
        self.assertEqual(suchen.call_count, 1)
        self.assertEqual(fetch.call_count, 0)
        self.assertIn("Keine Ergebnisse", erste)
        self.assertIn("web_fetch(url)", zweite)

    def test_failed_search_still_counts(self) -> None:
        tools = _tool_map(ThinkerToolCache(web_search_budget=1))
        with patch.object(thinker_mod.web_search_manager, "suchen",
                          side_effect=ConnectionError("searxng weg")) as suchen:
            erste = tools["web_search"].invoke("Magnetar Entfernung")
            zweite = tools["web_search"].invoke("Magnetar Abstand")
        self.assertEqual(suchen.call_count, 1)
        self.assertIn("Web-Suche fehlgeschlagen", erste)
        self.assertIn("web_fetch(url)", zweite)

    def test_web_fetch_is_not_budgeted(self) -> None:
        tools = _tool_map(ThinkerToolCache(web_search_budget=0))
        with patch.object(thinker_mod, "page_fetch", return_value="Seite") as fetch:
            text = tools["web_fetch"].invoke("https://de.wikipedia.org/wiki/Magnetar")
        self.assertEqual(fetch.call_count, 1)
        self.assertIn("Seite", text)


class PriorResearchServesFirstSearchTest(unittest.TestCase):
    """Die Sachlage-Treffer sind die erste Suche — ohne die Suchmaschine."""

    def test_hits_served_without_engine_and_counted(self) -> None:
        tools = _tool_map(ThinkerToolCache(web_search_budget=1), PRIOR)
        fremd = [{"title": "fremd", "url": "https://fremd.example", "content": ""}]
        with patch.object(thinker_mod.web_search_manager, "suchen", return_value=fremd) as suchen, \
                patch.object(thinker_mod, "page_fetch", return_value="Der Volltext") as fetch, \
                self.assertLogs("ki_server.thinker", level="INFO") as logs:
            erste = tools["web_search"].invoke("naechster Magnetar")
            zweite = tools["web_search"].invoke("magnetar distance")
        self.assertEqual(suchen.call_count, 0)
        fetch.assert_called_once_with(HITS[0]["url"])
        self.assertIn("bereits nachgeschlagen zu Magnetar — Entfernung", erste)
        self.assertIn("SGR 1806-20", erste)
        self.assertIn("Der Volltext", erste)
        self.assertNotIn("fremd", erste)
        self.assertIn("web_fetch(url)", zweite)
        self.assertTrue(
            any("bedient aus der Sachlage-Recherche (2 Treffer)" in z for z in logs.output),
            logs.output,
        )

    def test_without_prior_the_engine_is_called(self) -> None:
        tools = _tool_map(ThinkerToolCache(web_search_budget=1), None)
        with patch.object(thinker_mod.web_search_manager, "suchen", return_value=HITS) as suchen, \
                patch.object(thinker_mod, "page_fetch", return_value=""):
            tools["web_search"].invoke("Magnetar")
        self.assertEqual(suchen.call_count, 1)


class PriorResearchReaderTest(unittest.TestCase):
    """`prior_research` liest nur akute Objekte mit Treffern."""

    @staticmethod
    def _state(objekte: list) -> dict:
        return {"sachlage": {"objekte": objekte, "herkunft": "frisch"}}

    def test_without_sachlage_none(self) -> None:
        self.assertIsNone(prior_research({}))
        self.assertIsNone(prior_research({"sachlage": {}}))
        self.assertIsNone(prior_research(self._state([])))

    def test_acute_object_with_hits(self) -> None:
        state = self._state([{"name": "Magnetar", "akut": True, "recherche": {"Entfernung": HITS}}])
        self.assertEqual(prior_research(state), PRIOR)

    def test_empty_research_none(self) -> None:
        self.assertIsNone(prior_research(self._state(
            [{"name": "Magnetar", "akut": True, "recherche": {}}])))
        self.assertIsNone(prior_research(self._state(
            [{"name": "Magnetar", "akut": True, "recherche": {"Entfernung": []}}])))
        self.assertIsNone(prior_research(self._state(
            [{"name": "Magnetar", "akut": True}])))

    def test_latent_object_is_ignored(self) -> None:
        state = self._state([
            {"name": "Pulsar", "akut": False, "recherche": {"Frequenz": HITS}},
            {"name": "Magnetar", "akut": True, "recherche": {}},
        ])
        self.assertIsNone(prior_research(state))

    def test_first_acute_object_with_hits_wins(self) -> None:
        state = self._state([
            {"name": "Pulsar", "akut": True, "recherche": {}},
            {"name": "Magnetar", "akut": True, "recherche": {"Entfernung": HITS}},
        ])
        self.assertEqual(prior_research(state)["objekt"], "Magnetar")

    def test_hit_without_url_is_dropped_and_reported(self) -> None:
        kaputt = [{"title": "ohne", "content": "x"}, "kein dict"]
        state = self._state(
            [{"name": "Magnetar", "akut": True, "recherche": {"E": kaputt + HITS[:1]}}])
        with self.assertLogs("ki_server.thinker", level="WARNING") as logs:
            ergebnis = prior_research(state)
        self.assertEqual(ergebnis["treffer"], HITS[:1])
        self.assertTrue(any("2 Recherche-Treffer ohne URL" in z for z in logs.output), logs.output)
        state = self._state([{"name": "Magnetar", "akut": True, "recherche": {"E": kaputt}}])
        with self.assertLogs("ki_server.thinker", level="WARNING"):
            self.assertIsNone(prior_research(state))

    def test_non_dict_sachlage_is_reported(self) -> None:
        with self.assertLogs("ki_server.thinker", level="ERROR") as logs:
            self.assertIsNone(prior_research({"sachlage": "kaputt"}))
        self.assertTrue(any("kein dict" in z for z in logs.output), logs.output)


class FormatSearchResultsTest(unittest.TestCase):
    """Die Uebersicht nennt Suchbegriff, Quelle und jeden Treffer mit URL."""

    def test_numbered_with_source(self) -> None:
        text = format_search_results("Magnetar", HITS, "Suchmaschine")
        self.assertTrue(text.startswith("Web-Ergebnisse fuer 'Magnetar' (Suchmaschine):"))
        self.assertIn("1. Magnetar\n   URL: https://de.wikipedia.org/wiki/Magnetar", text)
        self.assertIn("2. SGR 1806-20", text)


class ThinkPassesPriorResearchTest(unittest.TestCase):
    """Die Verdrahtung: `think` liest die Sachlage und reicht die Treffer weiter."""

    @staticmethod
    def _state(sachlage: dict | None) -> dict:
        return {
            "response":         "Der naechste bekannte Magnetar ist rund 9.000 Lichtjahre weg.",
            "user_prompt":      "Wie weit ist der naechste bekannte Magnetar von uns entfernt?",
            "needs_web":        True,
            "event_payload":    {},
            "node_annotations": [],
            "token_total":      0,
            "character_id":     "nova",
            "agent_results":    [],
            "memory_context":   "",
            "sachlage":         sachlage,
        }

    def _run(self, state: dict) -> MagicMock:
        antwort = MagicMock(text="ERGEBNIS: OK", thinking="", token_total=0)
        normalizer = MagicMock()
        normalizer.pruefen.return_value = MagicMock(braucht_nachfass=False)
        with patch.object(thinker_mod, "create_tools", wraps=thinker_mod.create_tools) as ct, \
                patch.object(thinker_mod.model_service.chat, "submit_sync", return_value=antwort), \
                patch.object(thinker_mod, "get_thinking_normalizer", return_value=normalizer):
            think(state, redis_client=MagicMock(),
                  postgres_url="postgresql://unbenutzt", user_id="u")
        return ct

    def test_hits_reach_create_tools_and_the_log(self) -> None:
        state = self._state({"objekte": [
            {"name": "Magnetar", "akut": True, "recherche": {"Entfernung": HITS}}]})
        with self.assertLogs("ki_server.thinker", level="INFO") as logs:
            ct = self._run(state)
        self.assertEqual(ct.call_args.args[4], PRIOR)
        self.assertTrue(
            any("2 Treffer zu 'Magnetar' (Entfernung) bedienen die erste Websuche" in z
                for z in logs.output),
            logs.output,
        )

    def test_without_hits_none_reaches_create_tools(self) -> None:
        with self.assertLogs("ki_server.thinker", level="INFO") as logs:
            ct = self._run(self._state(None))
        self.assertIsNone(ct.call_args.args[4])
        self.assertTrue(
            any("keine Treffer, die erste Websuche geht an die Suchmaschine" in z
                for z in logs.output),
            logs.output,
        )


if __name__ == "__main__":
    unittest.main()
