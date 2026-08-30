"""WebSearchManager — Web-Suche ueber Serper, mit SearXNG als Rueckfall.

Serper liefert Google-Treffer ueber eine HTTP-API und braucht einen Schluessel;
SearXNG ist die lokale Metasuche ohne eigenen Index. Der Manager fragt die
Anbieter in dieser Reihenfolge und nimmt den ersten, der Treffer liefert —
damit deckt ein Umbau alle vier Konsumenten (Thinker, Sachlage-Recherche,
RechercheAgent, VertiefungsAgent).
"""

import logging

import httpx

from config import (
    SEARXNG_MAX_RESULTS,
    SEARXNG_TIMEOUT,
    SEARXNG_URL,
    SERPER_API_KEY,
    SERPER_TIMEOUT,
    SERPER_URL,
)

logger = logging.getLogger(__name__)


class SerperProvider:
    """Google-Treffer ueber die Serper-HTTP-API.

    Vorbedingung: `query` ist nicht leer, `limit` ist positiv — geprueft beim
    Aufrufer (`WebSearchManager.suchen`).
    Nachbedingung: Liste von Dicts mit `title`, `url`, `content`; bei jedem
    Ausfall eine leere Liste, und der Ausfall steht als `error` im Log.
    """

    name = "Serper"

    def __init__(self, api_key: str, url: str, timeout: float) -> None:
        """Haelt Schluessel, Endpunkt und Frist des Anbieters."""
        self._api_key = api_key
        self._url = url
        self._timeout = timeout

    @property
    def configured(self) -> bool:
        """Wahr, sobald ein Schluessel gesetzt ist — ohne ihn antwortet die API 403."""
        return bool(self._api_key)

    def search(self, query: str, limit: int) -> list[dict]:
        """Fragt Serper und bildet `organic` auf die gemeinsame Trefferform ab."""
        # ── Eingabe-Validierung ──────────────────────
        if not self._api_key:
            logger.error(
                f"Serper: Suche '{query[:60]}' ohne Schluessel aufgerufen — "
                f"der Aufrufer haette `configured` pruefen muessen"
            )
            return []

        try:
            response = httpx.post(
                self._url,
                headers={"X-API-KEY": self._api_key, "Content-Type": "application/json"},
                json={"q": query, "gl": "de", "hl": "de", "num": limit},
                timeout=self._timeout,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.exception(f"{type(e).__name__}: Serper-Suche '{query[:60]}' fehlgeschlagen")
            return []

        # ── Ausgabe-Verifikation ─────────────────────
        organic = data.get("organic")
        if organic is None:
            logger.error(
                f"Serper: Antwort ohne Feld 'organic' zu '{query[:60]}', "
                f"Felder vorhanden: {sorted(data.keys())}"
            )
            return []
        if not isinstance(organic, list):
            logger.error(
                f"Serper: Feld 'organic' ist {type(organic).__name__} statt Liste "
                f"zu '{query[:60]}' — verworfen"
            )
            return []

        treffer: list[dict] = [
            {
                "title": eintrag.get("title", ""),
                "url": eintrag.get("link", ""),
                "content": eintrag.get("snippet", ""),
            }
            for eintrag in organic[:limit]
            if isinstance(eintrag, dict) and eintrag.get("link")
        ]
        if organic and not treffer:
            logger.error(
                f"Serper: {len(organic)} Eintraege zu '{query[:60]}', keiner mit 'link' — "
                f"verworfen"
            )
        return treffer


class SearxngProvider:
    """Treffer der lokalen SearXNG-Metasuche.

    Vorbedingung: `query` ist nicht leer, `limit` ist positiv — geprueft beim
    Aufrufer (`WebSearchManager.suchen`).
    Nachbedingung: Liste von Dicts mit `title`, `url`, `content`; bei jedem
    Ausfall eine leere Liste, und der Ausfall steht im Log.
    """

    name = "SearXNG"

    def __init__(self, base_url: str, timeout: float) -> None:
        """Haelt Basis-URL und Frist der lokalen Metasuche."""
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def configured(self) -> bool:
        """Wahr, sobald eine Basis-URL steht — SearXNG braucht keinen Schluessel."""
        return bool(self._base_url)

    def search(self, query: str, limit: int) -> list[dict]:
        """Fragt SearXNG und bildet `results` auf die gemeinsame Trefferform ab."""
        # ── Eingabe-Validierung ──────────────────────
        if not self._base_url:
            logger.error(f"SearXNG: Suche '{query[:60]}' ohne Basis-URL aufgerufen")
            return []

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
        except Exception as e:
            logger.exception(f"{type(e).__name__}: SearXNG-Suche '{query[:60]}' fehlgeschlagen")
            return []

        # ── Ausgabe-Verifikation ─────────────────────
        results = data.get("results")
        if not isinstance(results, list):
            logger.error(
                f"SearXNG: Feld 'results' ist {type(results).__name__} statt Liste "
                f"zu '{query[:60]}' — verworfen"
            )
            return []

        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
            }
            for r in results[:limit]
            if isinstance(r, dict)
        ]


class WebSearchManager:
    """Fragt die Anbieter der Reihe nach und nimmt den ersten mit Treffern.

    Zustandslos pro Aufruf. Die Reihenfolge steht im Konstruktor; ein Anbieter
    ohne Konfiguration wird uebersprungen, einer ohne Treffer faellt an den
    naechsten durch — beides mit einer Zeile im Log, damit ein leeres Ergebnis
    nicht von einem stillen Ausfall zu unterscheiden ist.
    """

    def __init__(self, providers: list, max_results: int) -> None:
        """Haelt die Anbieter in ihrer Rangfolge und die Vorgabe fuer die Trefferzahl."""
        self._providers = providers
        self._max_results = max_results

    def suchen(self, query: str, max_results: int | None = None) -> list[dict]:
        """Web-Suche, gibt Liste von Ergebnis-Dicts zurueck.

        Jedes Ergebnis: {"title": str, "url": str, "content": str}

        Vorbedingung: keine — leere Suchbegriffe und unbrauchbare Grenzen
        werden hier gemeldet und verworfen.
        Nachbedingung: Liste der Treffer des ersten liefernden Anbieters,
        hoechstens `max_results` lang; leer, wenn keiner geliefert hat.
        """
        # ── Eingabe-Validierung ──────────────────────
        if not query or not query.strip():
            logger.error("Web-Suche: leerer Suchbegriff — verworfen")
            return []

        limit = max_results or self._max_results
        if limit <= 0:
            logger.error(f"Web-Suche: Grenze {limit} zu '{query[:60]}' nicht positiv — verworfen")
            return []

        for provider in self._providers:
            if not provider.configured:
                logger.info(
                    f"Web-Suche: {provider.name} nicht konfiguriert — uebersprungen "
                    f"('{query[:60]}')"
                )
                continue

            logger.info(f"Web-Suche ueber {provider.name}: '{query[:60]}', bis zu {limit} Treffer")
            treffer: list[dict] = provider.search(query, limit)

            # ── Ausgabe-Verifikation ─────────────────
            if treffer:
                logger.info(f"Web-Suche: {provider.name} lieferte {len(treffer)} Treffer")
                return treffer

            logger.warning(
                f"Web-Suche: {provider.name} ohne Treffer zu '{query[:60]}' — "
                f"Rueckfall auf den naechsten Anbieter"
            )

        logger.error(
            f"Web-Suche: kein Anbieter lieferte Treffer zu '{query[:60]}' "
            f"({len(self._providers)} befragt)"
        )
        return []


# Modul-Level-Instanz — die Reihenfolge ist die Rangfolge: Google zuerst,
# die lokale Metasuche als Rueckfall.
web_search_manager = WebSearchManager(
    providers=[
        SerperProvider(
            api_key=SERPER_API_KEY,
            url=SERPER_URL,
            timeout=SERPER_TIMEOUT,
        ),
        SearxngProvider(
            base_url=SEARXNG_URL,
            timeout=SEARXNG_TIMEOUT,
        ),
    ],
    max_results=SEARXNG_MAX_RESULTS,
)
