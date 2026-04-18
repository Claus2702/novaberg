"""WebSearchManager — SearXNG-Zugriff für Web-Suche."""

import logging
import httpx
from config import SEARXNG_URL, SEARXNG_TIMEOUT, SEARXNG_MAX_RESULTS

logger = logging.getLogger(__name__)


class WebSearchManager:
    """Kapselt SearXNG-Anfragen. Zustandslos pro Aufruf.

    Orientiert sich am bestehenden services/web_search.py,
    bietet aber eine synchrone, vereinfachte API für Agenten.
    """

    def __init__(self, base_url: str, timeout: float, max_results: int):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_results = max_results

    def suchen(self, query: str, max_results: int | None = None) -> list[dict]:
        """Web-Suche über SearXNG, gibt Liste von Ergebnis-Dicts zurück.

        Jedes Ergebnis: {"title": str, "url": str, "content": str}
        """
        limit = max_results or self._max_results
        try:
            response = httpx.get(
                f"{self._base_url}/search",
                params={
                    "q": query,
                    "format": "json",
                    "language": "de",
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])[:limit]
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Web-Suche fehlgeschlagen: {e}")
            return []


# Modul-Level-Instanz
web_search_manager = WebSearchManager(
    base_url=SEARXNG_URL,
    timeout=SEARXNG_TIMEOUT,
    max_results=SEARXNG_MAX_RESULTS,
)
