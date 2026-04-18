"""Suche — Web-Suche + Auto-Fetch fuer jede Query."""

import logging

from tools.web.search import web_search_manager
from tools.web.fetch import page_fetch
from config import PIXIE_RECHERCHE_MAX_SEITEN_PRO_RUNDE

logger = logging.getLogger("ki_server.agents.recherche")

# URL-Blacklist: Seiten die keinen verwertbaren Text liefern
_URL_BLACKLIST: list[str] = [
    "youtube.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "tiktok.com", "reddit.com", "linkedin.com",
]


def suche_ausfuehren(queries: list[str]) -> list[str]:
    """Fuehrt Web-Suche + Page-Fetch fuer alle Queries aus.

    Pro Query: SearXNG-Suche -> Relevanz-Filter -> Page-Fetch auf Top-URL.
    Dedupliziert nach Domain.

    Args:
        queries: Liste von Suchbegriffen.

    Returns:
        Liste von extrahierten Texten (ein Text pro erfolgreichem Fetch).
    """
    ergebnisse: list[str] = []
    bereits_gefetcht: set[str] = set()
    max_seiten: int = PIXIE_RECHERCHE_MAX_SEITEN_PRO_RUNDE

    for query in queries:
        if len(ergebnisse) >= max_seiten:
            break

        logger.info(f"Recherche-Suche: '{query}'")

        try:
            treffer: list[dict] = web_search_manager.suchen(query, max_results=5)
        except Exception as e:
            logger.warning(f"Recherche-Suche fehlgeschlagen fuer '{query}': {e}")
            continue

        if not treffer:
            logger.info(f"Recherche-Suche: Keine Treffer fuer '{query}'")
            continue

        for t in treffer:
            if len(ergebnisse) >= max_seiten:
                break

            url: str = t.get("url", "")
            if not url:
                continue

            # URL-Blacklist
            if any(domain in url for domain in _URL_BLACKLIST):
                continue

            # Domain-Deduplizierung
            domain: str = _domain_extrahieren(url)
            if domain in bereits_gefetcht:
                continue

            # Page-Fetch
            logger.info(f"Recherche-Fetch: {url}")
            text: str = page_fetch(url)

            if text and len(text) > 100:
                ergebnisse.append(
                    f"--- Quelle: {t.get('title', url)} ---\n"
                    f"URL: {url}\n\n"
                    f"{text}"
                )
                bereits_gefetcht.add(domain)
                logger.info(f"Recherche-Fetch: OK — {len(text)} Zeichen")
                break  # Ein erfolgreicher Fetch pro Query reicht
            else:
                logger.info(f"Recherche-Fetch: Zu wenig Text von {url}")

    logger.info(f"Recherche-Suche: {len(ergebnisse)} Texte gesammelt")
    return ergebnisse


def _domain_extrahieren(url: str) -> str:
    """Extrahiert die Domain aus einer URL."""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc
    except Exception:
        return url
