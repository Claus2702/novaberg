# Nova — Tool: Web-Infrastruktur

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Web-Infrastruktur — SearXNG, WebSearchManager, PageFetcher
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** `novaberg/docs/nova-tool-web.md`
**Quellen:** nova-07-a.md, Codestand

---

## 1. SearXNG — Lokale Metasuchmaschine

SearXNG laeuft als Docker-Container und stellt eine JSON-API fuer Web-Suchen bereit. Keine externe API-Keys noetig, keine Tracking-Problematik.

**Docker-Konfiguration:**

```yaml
searxng:
  image: searxng/searxng:latest
  volumes:
    - ./searxng:/etc/searxng:rw
  ports: ["8080:8080"]
  environment:
    - SEARXNG_BASE_URL=http://localhost:8080/
```

**Health-Check:** Der Server prueft SearXNG-Erreichbarkeit ueber HTTP GET auf `SEARXNG_URL` (Timeout 3s). Status wird im Health-Endpoint und in der Client-Statusleiste angezeigt.

---

## 2. WebSearchManager

**Datei:** `tools/web/search.py`

SearXNG-Wrapper, der die JSON-API anspricht. Liefert strukturierte Suchergebnisse (Titel, URL, Snippet).

| Parameter | Beschreibung |
|-----------|-------------|
| `query` | Suchbegriff |
| `max_results` | Maximale Ergebnisanzahl (Default: `SEARXNG_MAX_RESULTS`) |
| `timeout` | HTTP-Timeout (Default: `SEARXNG_TIMEOUT`) |

---

## 3. PageFetcher

**Datei:** `tools/web/fetch.py`

Laedt den Inhalt einer URL und extrahiert den Haupttext:

1. **Primaer:** trafilatura — spezialisiert auf Artikel-Extraktion
2. **Fallback:** BeautifulSoup4 — wenn trafilatura keinen Inhalt liefert

| Parameter | Default | Beschreibung |
|-----------|---------|-------------|
| `PAGE_FETCH_TIMEOUT` | 10.0 | HTTP-Timeout |
| `PAGE_FETCH_MAX_CHARS` | 5000 | Maximale Zeichen pro Seite |

---

## 4. Auto-Fetch

Die `web_search`-Funktion fetcht automatisch den Inhalt der Top-URL aus den Suchergebnissen. Der Thinker bekommt Suchergebnisse inklusive Seiteninhalt in einem Schritt — kein separater Fetch-Aufruf noetig.

---

## 5. Integration

| Konsument | Nutzung |
|-----------|---------|
| **Thinker** | Nutzt `web_search` als Tool bei Wissensfragen |
| **RechercheAgent (Pixie)** | Nutzt `web_search_manager.suchen()` + `page_fetch()` iterativ fuer mehrstufige Recherchen |
| **VertiefungsAgent (Pixie)** | Gleiche Web-Infrastruktur wie RechercheAgent |

Der RechercheAgent fuehrt pro Suchrunde bis zu `PIXIE_RECHERCHE_MAX_SEITEN_PRO_RUNDE` Fetches durch, mit URL-Blacklist (Social Media, Video-Plattformen) und Domain-Deduplizierung.

---

## 6. Konfiguration

Alle Variablen in `config.py`, gelesen aus Umgebungsvariablen:

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| `SEARXNG_URL` | `http://searxng:8080` | SearXNG-Basis-URL (Docker-intern) |
| `SEARXNG_TIMEOUT` | `10.0` | HTTP-Timeout fuer Suchanfragen |
| `SEARXNG_MAX_RESULTS` | `10` | Maximale Ergebnisse pro Suche |
| `PAGE_FETCH_TIMEOUT` | `10.0` | HTTP-Timeout fuer Page-Fetch |
| `PAGE_FETCH_MAX_CHARS` | `5000` | Max Zeichen pro Seite |
