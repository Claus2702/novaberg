"""Zeugen fuer die Anbieterkette der Web-Suche.

Serper steht vorn, SearXNG faellt ein. Geprueft wird die Reihenfolge, die
Abbildung beider Antwortformen auf die gemeinsame Trefferform und jeder Weg,
auf dem ein Anbieter ausfaellt: kein Schluessel, HTTP-Fehler, kaputte Antwort,
keine Treffer.
"""

import unittest
from unittest.mock import MagicMock, patch

from tools.web.search import SearxngProvider, SerperProvider, WebSearchManager

SERPER_BODY = {
    "searchParameters": {"q": "Magnetar"},
    "organic": [
        {"title": "Magnetar", "link": "https://de.wikipedia.org/wiki/Magnetar",
         "snippet": "Ein Neutronenstern mit extrem starkem Magnetfeld.", "position": 1},
        {"title": "SGR 1935", "link": "https://example.org/sgr", "snippet": "Ein Magnetar."},
    ],
    "credits": 1,
}

SEARXNG_BODY = {
    "results": [
        {"title": "Magnetar", "url": "https://searx.example/magnetar", "content": "Metasuche."},
    ]
}


def _response(payload: dict) -> MagicMock:
    """Eine httpx-Antwort, die `payload` als JSON traegt."""
    antwort = MagicMock()
    antwort.json.return_value = payload
    antwort.raise_for_status.return_value = None
    return antwort


class SerperProviderTest(unittest.TestCase):
    """Der erste Anbieter: Schluessel, Abbildung, Ausfallwege."""

    def test_without_key_not_configured(self) -> None:
        anbieter = SerperProvider(api_key="", url="https://x/search", timeout=1.0)
        self.assertFalse(anbieter.configured)

    def test_with_key_configured(self) -> None:
        anbieter = SerperProvider(api_key="k", url="https://x/search", timeout=1.0)
        self.assertTrue(anbieter.configured)

    def test_maps_organic_to_common_shape(self) -> None:
        anbieter = SerperProvider(api_key="k", url="https://x/search", timeout=1.0)
        with patch("tools.web.search.httpx.post", return_value=_response(SERPER_BODY)):
            treffer = anbieter.search("Magnetar", 5)
        self.assertEqual(len(treffer), 2)
        self.assertEqual(treffer[0]["title"], "Magnetar")
        self.assertEqual(treffer[0]["url"], "https://de.wikipedia.org/wiki/Magnetar")
        self.assertEqual(treffer[0]["content"], "Ein Neutronenstern mit extrem starkem Magnetfeld.")

    def test_sends_key_as_header(self) -> None:
        anbieter = SerperProvider(api_key="geheim", url="https://x/search", timeout=1.0)
        with patch("tools.web.search.httpx.post", return_value=_response(SERPER_BODY)) as post:
            anbieter.search("Magnetar", 3)
        self.assertEqual(post.call_args.kwargs["headers"]["X-API-KEY"], "geheim")
        self.assertEqual(post.call_args.kwargs["json"]["q"], "Magnetar")
        self.assertEqual(post.call_args.kwargs["json"]["num"], 3)

    def test_honours_limit(self) -> None:
        anbieter = SerperProvider(api_key="k", url="https://x/search", timeout=1.0)
        with patch("tools.web.search.httpx.post", return_value=_response(SERPER_BODY)):
            treffer = anbieter.search("Magnetar", 1)
        self.assertEqual(len(treffer), 1)

    def test_without_key_returns_empty(self) -> None:
        anbieter = SerperProvider(api_key="", url="https://x/search", timeout=1.0)
        with patch("tools.web.search.httpx.post") as post:
            treffer = anbieter.search("Magnetar", 5)
        self.assertEqual(treffer, [])
        post.assert_not_called()

    def test_http_error_returns_empty(self) -> None:
        anbieter = SerperProvider(api_key="k", url="https://x/search", timeout=1.0)
        with patch("tools.web.search.httpx.post", side_effect=RuntimeError("403")):
            treffer = anbieter.search("Magnetar", 5)
        self.assertEqual(treffer, [])

    def test_answer_without_organic_returns_empty(self) -> None:
        anbieter = SerperProvider(api_key="k", url="https://x/search", timeout=1.0)
        with patch("tools.web.search.httpx.post", return_value=_response({"credits": 1})):
            treffer = anbieter.search("Magnetar", 5)
        self.assertEqual(treffer, [])

    def test_organic_of_wrong_type_returns_empty(self) -> None:
        anbieter = SerperProvider(api_key="k", url="https://x/search", timeout=1.0)
        with patch("tools.web.search.httpx.post", return_value=_response({"organic": "nichts"})):
            treffer = anbieter.search("Magnetar", 5)
        self.assertEqual(treffer, [])

    def test_entries_without_link_are_dropped(self) -> None:
        payload = {"organic": [{"title": "ohne Link", "snippet": "x"}]}
        anbieter = SerperProvider(api_key="k", url="https://x/search", timeout=1.0)
        with patch("tools.web.search.httpx.post", return_value=_response(payload)):
            treffer = anbieter.search("Magnetar", 5)
        self.assertEqual(treffer, [])


class SearxngProviderTest(unittest.TestCase):
    """Der Rueckfall: unveraenderte Abbildung, Ausfallwege."""

    def test_maps_results_to_common_shape(self) -> None:
        anbieter = SearxngProvider(base_url="http://searxng:8080", timeout=1.0)
        with patch("tools.web.search.httpx.get", return_value=_response(SEARXNG_BODY)):
            treffer = anbieter.search("Magnetar", 5)
        self.assertEqual(treffer, [{"title": "Magnetar",
                                    "url": "https://searx.example/magnetar",
                                    "content": "Metasuche."}])

    def test_http_error_returns_empty(self) -> None:
        anbieter = SearxngProvider(base_url="http://searxng:8080", timeout=1.0)
        with patch("tools.web.search.httpx.get", side_effect=RuntimeError("timeout")):
            self.assertEqual(anbieter.search("Magnetar", 5), [])

    def test_answer_without_results_returns_empty(self) -> None:
        anbieter = SearxngProvider(base_url="http://searxng:8080", timeout=1.0)
        with patch("tools.web.search.httpx.get", return_value=_response({})):
            self.assertEqual(anbieter.search("Magnetar", 5), [])


class WebSearchManagerTest(unittest.TestCase):
    """Die Kette: Reihenfolge, Ueberspringen, Rueckfall, Eingabepruefung."""

    def setUp(self) -> None:
        self.serper = MagicMock(name="Serper")
        self.serper.name = "Serper"
        self.serper.configured = True
        self.searxng = MagicMock(name="SearXNG")
        self.searxng.name = "SearXNG"
        self.searxng.configured = True
        self.manager = WebSearchManager(providers=[self.serper, self.searxng], max_results=10)

    def test_first_provider_with_hits_wins(self) -> None:
        self.serper.search.return_value = [{"title": "a", "url": "u", "content": "c"}]
        treffer = self.manager.suchen("Magnetar")
        self.assertEqual(len(treffer), 1)
        self.searxng.search.assert_not_called()

    def test_empty_first_provider_falls_through(self) -> None:
        self.serper.search.return_value = []
        self.searxng.search.return_value = [{"title": "b", "url": "u", "content": "c"}]
        treffer = self.manager.suchen("Magnetar")
        self.assertEqual(treffer[0]["title"], "b")
        self.searxng.search.assert_called_once()

    def test_unconfigured_provider_is_skipped(self) -> None:
        self.serper.configured = False
        self.searxng.search.return_value = [{"title": "b", "url": "u", "content": "c"}]
        treffer = self.manager.suchen("Magnetar")
        self.assertEqual(len(treffer), 1)
        self.serper.search.assert_not_called()

    def test_all_providers_empty_returns_empty(self) -> None:
        self.serper.search.return_value = []
        self.searxng.search.return_value = []
        self.assertEqual(self.manager.suchen("Magnetar"), [])

    def test_default_limit_is_passed(self) -> None:
        self.serper.search.return_value = [{"title": "a", "url": "u", "content": "c"}]
        self.manager.suchen("Magnetar")
        self.assertEqual(self.serper.search.call_args[0][1], 10)

    def test_explicit_limit_is_passed(self) -> None:
        self.serper.search.return_value = [{"title": "a", "url": "u", "content": "c"}]
        self.manager.suchen("Magnetar", max_results=5)
        self.assertEqual(self.serper.search.call_args[0][1], 5)

    def test_empty_query_asks_nobody(self) -> None:
        self.assertEqual(self.manager.suchen("   "), [])
        self.serper.search.assert_not_called()
        self.searxng.search.assert_not_called()

    def test_negative_limit_asks_nobody(self) -> None:
        self.assertEqual(self.manager.suchen("Magnetar", max_results=-1), [])
        self.serper.search.assert_not_called()


class ModuleInstanceTest(unittest.TestCase):
    """Die Modul-Instanz traegt beide Anbieter in der festgelegten Reihenfolge."""

    def test_serper_stands_before_searxng(self) -> None:
        from tools.web.search import web_search_manager
        namen = [p.name for p in web_search_manager._providers]
        self.assertEqual(namen, ["Serper", "SearXNG"])


if __name__ == "__main__":
    unittest.main()
