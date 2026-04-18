"""PageFetcher — URL abrufen und Artikeltext extrahieren."""

import logging
import httpx
from config import PAGE_FETCH_TIMEOUT, PAGE_FETCH_MAX_CHARS

logger = logging.getLogger(__name__)


def page_fetch(url: str, max_chars: int | None = None) -> str:
    """Laedt eine URL und extrahiert den Text-Inhalt.

    Primaer: trafilatura (entfernt Navigation, Werbung, Footer).
    Fallback: BeautifulSoup get_text() wenn trafilatura scheitert.

    Returns: Sauberer Text oder leerer String bei Fehler.
    """
    limit: int = max_chars or PAGE_FETCH_MAX_CHARS

    try:
        response: httpx.Response = httpx.get(
            url,
            timeout=PAGE_FETCH_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Nova/1.0)"},
        )
        response.raise_for_status()
        html: str = response.text

    except Exception as e:
        logger.warning(f"PageFetch HTTP-Fehler fuer {url}: {e}")
        return ""

    # Primaer: trafilatura
    try:
        import trafilatura
        text: str | None = trafilatura.extract(html, include_comments=False, include_tables=True)
        if text:
            logger.info(f"PageFetch: trafilatura OK — {len(text)} Zeichen von {url}")
            return text[:limit]
    except Exception as e:
        logger.warning(f"PageFetch: trafilatura fehlgeschlagen fuer {url}: {e}")

    # Fallback: BeautifulSoup
    try:
        from bs4 import BeautifulSoup
        soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        if text:
            logger.info(f"PageFetch: BeautifulSoup-Fallback — {len(text)} Zeichen von {url}")
            return text[:limit]
    except Exception as e:
        logger.warning(f"PageFetch: BeautifulSoup-Fallback fehlgeschlagen fuer {url}: {e}")

    return ""
