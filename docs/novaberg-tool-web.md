# Novaberg — Tool: Web-Infrastruktur

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Web-Infrastruktur — SearXNG, WebSearchManager, PageFetcher
**Stand:** 29. August 2026 (Konsumententabelle: der Thinker sucht einmal je Turn, die Sachlage-Recherche als zweiter Konsument nachgetragen); davor 19. April 2026, Chat 57 (DRY-Prinzip explizit)
**Pfad:** `novaberg/docs/novaberg-tool-web.md`
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

## 5. Integration (DRY — Shared Tool)

Web-Suche und Page-Fetch sind bewusst als allgemeine Tools positioniert, nicht als Pixie-Infrastruktur. Beide Graphen nutzen dieselbe Codebasis — DRY-Prinzip.

| Graph | Konsument | Nutzung |
|-------|-----------|---------|
| **Character Graph** (seit Chat 60; hier stand ~~Human Graph~~) | Thinker | `web_search` als Tool bei Wissensfragen (Auto-Fetch auf Top-URL) — **seit 29.08.2026 einmal je Turn** (`THINKER_WEBSUCHE_MAX_JE_TURN`), und hat die Sachlage-Recherche im selben Turn Treffer, bedienen sie die erste Suche ohne zweiten Aufruf der Maschine (`novaberg-node-thinker.md` §4.4) |
| **Character Graph** | Sachlage-Recherche (`graph/nodes/sachlage_research.py`, seit 29.08.2026) | `web_search_manager.suchen()` einmal je Turn fuer die erste offene `nachschlagen`-Eigenschaft, Wortlaut-Filter, kein Fetch (`novaberg-thinking-lage_k.md` §4 Scheibe 8) |
| **Pixie Graph** | RechercheAgent | `web_search_manager.suchen()` + `page_fetch()` iterativ fuer mehrstufige Recherchen |
| **Pixie Graph** | VertiefungsAgent | Gleiche Web-Infrastruktur wie RechercheAgent |

Der RechercheAgent fuehrt pro Suchrunde bis zu `PIXIE_RECHERCHE_MAX_SEITEN_PRO_RUNDE` Fetches durch, mit URL-Blacklist (Social Media, Video-Plattformen) und Domain-Deduplizierung.

> **Architektur-Entscheidung (Chat 34):** "PageFetcher und WebSearch sind allgemeine Tools (`tools/web/`), keine Pixie-Infrastruktur. Der Thinker braucht sie genauso."

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
