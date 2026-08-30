# Novaberg — Tool: Web-Infrastruktur

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Web-Infrastruktur — Suchanbieter, WebSearchManager, PageFetcher
**Stand:** 30. August 2026 (Serper als erster Anbieter, SearXNG als Rueckfall; die Sperren der uebrigen Engines gemessen); davor 29. August 2026 (Konsumententabelle: der Thinker sucht einmal je Turn, die Sachlage-Recherche als zweiter Konsument nachgetragen); davor 19. April 2026, Chat 57 (DRY-Prinzip explizit)
**Pfad:** `novaberg/docs/novaberg-tool-web.md`
**Quellen:** nova-07-a.md, Codestand

---

## 1. Zwei Anbieter, eine Reihenfolge

Die Web-Suche fragt **Serper zuerst und SearXNG als Rueckfall**. Beide liefern dieselbe Trefferform (`title`, `url`, `content`), damit ein Wechsel keinen Konsumenten beruehrt.

| Rang | Anbieter | Was er ist | Bedingung |
|---|---|---|---|
| 1 | **Serper** | Google-Ergebnisse ueber eine HTTP-API | braucht `SERPER_API_KEY`; ohne Schluessel wird er uebersprungen |
| 2 | **SearXNG** | lokale Metasuche ohne eigenen Index | immer verfuegbar, solange der Behaelter laeuft |

**Ein uebersprungener oder leer ausgehender Anbieter steht im Log**, damit ein leeres Ergebnis nicht wie ein stiller Ausfall aussieht: *»… nicht konfiguriert — uebersprungen«*, *»… ohne Treffer … — Rueckfall auf den naechsten Anbieter«*, und wenn keiner lieferte, eine `error`-Zeile.

**Warum die Reihenfolge so steht:** SearXNG hat keinen eigenen Index, sondern reicht an Bing, Google, DuckDuckGo und Wikipedia weiter — und die Quellen dahinter blocken. Seit dem 29.08.2026 antwortet aus dieser Instanz nur noch die Wikipedia-Volltextsuche; sie traegt Wissensfragen, aber nichts darueber hinaus. `[gemessen]` — 30.08.2026, dieselbe Frage nach Sonnenflecken: Serper liefert 5 Treffer, darunter Max-Planck-Institut und Wikipedia. Am selben Tag gegengeprueft, warum kein zweiter kostenloser Anbieter einspringt: Von den aktiven Engines antworteten `duckduckgo` und `startpage` mit CAPTCHA, `brave` mit *too many requests*, `karmasearch` mit *access denied*, `aol` mit HTTP-Fehler — fuenf Treffer, alle aus der Wikipedia-Volltextsuche. Die Endnutzer-API von Qwant (`api.qwant.com/v3/search/web`, in der Konfiguration vorhanden und abgeschaltet) antwortet mit **HTTP 403**. **Was ohne Index blockt, blockt fuer jeden Server ohne Wohnzimmer-Anschluss** — der Ausweg ist ein Anbieter mit bezahltem Zugang, nicht eine andere Engine (Fundliste 30.08.2026: Tavily und Staan als Optionen).

**Serper kostet je Anfrage ein Guthaben** (Startguthaben 2500, ohne Zahlungsmittel). Deshalb wiegt die Suchdisziplin der Konsumenten (§5) schwerer als bei einer lokalen Instanz.

---

## 1a. SearXNG — die lokale Metasuche

SearXNG laeuft als Docker-Container und stellt eine JSON-API fuer Web-Suchen bereit. Kein Schluessel noetig, keine Tracking-Problematik — und seit dem 30.08.2026 der zweite Anbieter, nicht mehr der erste.

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

Die eine Tuer zur Web-Suche: `web_search_manager.suchen(query, max_results)`. Der Manager haelt die Anbieter in ihrer Rangfolge, fragt sie der Reihe nach und gibt die Treffer des ersten zurueck, der welche liefert.

| Parameter | Beschreibung |
|-----------|-------------|
| `query` | Suchbegriff — leer oder nur Leerzeichen wird gemeldet und verworfen |
| `max_results` | Maximale Ergebnisanzahl (Default: `SEARXNG_MAX_RESULTS`) |

**Je Anbieter eine Klasse** mit `name`, `configured` und `search(query, limit)`:

| Klasse | Endpunkt | Antwortfeld | Abbildung |
|---|---|---|---|
| `SerperProvider` | `POST` auf `SERPER_URL`, Schluessel im Kopf `X-API-KEY`, Rumpf `{q, gl: de, hl: de, num}` | `organic` | `title` → `title`, **`link` → `url`**, `snippet` → `content` |
| `SearxngProvider` | `GET` auf `{SEARXNG_URL}/search?format=json&language=de` | `results` | `title`, `url`, `content` unveraendert |

Ein Anbieter gibt bei jedem Ausfall eine leere Liste zurueck — HTTP-Fehler, fehlendes oder falsch getyptes Antwortfeld, Eintraege ohne Adresse — und schreibt den Grund als `error` ins Log. Damit ist *»nichts gefunden«* vom Ausfall unterscheidbar.

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
| `SERPER_API_KEY` | *(leer)* | Schluessel fuer Serper. Leer heisst: Anbieter wird uebersprungen, unveraendertes Verhalten |
| `SERPER_URL` | `https://google.serper.dev/search` | Endpunkt der Serper-API |
| `SERPER_TIMEOUT` | `10.0` | HTTP-Timeout fuer Serper |
| `SEARXNG_URL` | `http://searxng:8080` | SearXNG-Basis-URL (Docker-intern) |
| `SEARXNG_TIMEOUT` | `10.0` | HTTP-Timeout fuer Suchanfragen |
| `SEARXNG_MAX_RESULTS` | `10` | Maximale Ergebnisse pro Suche |
| `PAGE_FETCH_TIMEOUT` | `10.0` | HTTP-Timeout fuer Page-Fetch |
| `PAGE_FETCH_MAX_CHARS` | `5000` | Max Zeichen pro Seite |

> **Der Schluessel steht in der `.env` und wird ueber die Compose-Datei durchgereicht.** Eine **neue** Umgebungsvariable wirkt erst nach `docker compose up -d server` — ein `restart` startet den bestehenden Behaelter neu, ohne ihn aus der geaenderten Konfiguration zu erzeugen, und die Umstellung faellt dann still aus.
