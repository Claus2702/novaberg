# Novaberg — The Nova Anima Resonance System

**Eine kognitive Architektur für persönliche KI — mit emergenter Persönlichkeit, intrinsischer Neugier und emotionaler Intelligenz. Lokal, privat, deins.**

🇬🇧 [English version](README.md)

---

**Nova** ist ein lokaler, privatsphäre-orientierter persönlicher KI-Assistent mit einer kognitiven Architektur. Kein einfacher Chatbot, sondern ein System aus spezialisierten Agenten, geschichtetem Gedächtnis, emotionaler Intelligenz und einem autonomen Hintergrundagenten.

**Leitgedanke:** Das LLM ist ein Sprachprozessor, kein Wissensspeicher. Echtes Wissen liegt in PostgreSQL, Redis und im Web. Intelligenz entsteht aus der parallelen Bewertung durch spezialisierte Perspektiven.

---

## Überblick

Nova besteht aus zwei parallelen Graphen:

- **Human Graph** (Vordergrund) — Perzeption → Router → Enricher → Planner → Agent-Dispatch → Gesprächsvektor → Responder → Tribunal. Reagiert auf User-Eingaben in Echtzeit.
- **Pixie Graph** (Hintergrund) — der autonome Hintergrundagent. Führt Promotion, Decay, Charakter-Destillation, Wiedervorlage, Recherche und Vertiefung aus. Läuft kompetitiv nach Priorität.

Geschichtetes Gedächtnis:

| Schicht | Technologie | Zweck |
|---------|-------------|-------|
| Kurzzeit (KZG) | Redis + Vektorsuche | Aktive Gedanken, TTL-basiert |
| Langzeit (LZG) | PostgreSQL | Verfestigte Erinnerungen mit Ebbinghaus-Decay |
| Knowledge Graph | PostgreSQL | Entitäten, Fakten, bi-temporales Modell |
| Charakter-Hash | PostgreSQL | Destillierte Persönlichkeitsprofile |

Multi-Channel: Desktop-Client (PySide6) und Telegram-Bot nutzen dieselbe FastAPI-Server-Instanz.

---

## Technologie-Stack

- **Backend:** Python 3.12, FastAPI, LangGraph, APScheduler
- **Datenbanken:** PostgreSQL 16 mit pgvector, Redis Stack
- **LLM:** Ollama (lokal) mit Gemma 4 oder Mistral Small 3.2; optional Anthropic Claude API
- **Embedding:** `nomic-embed-text` via Ollama
- **Suchmaschine:** SearXNG (Docker)
- **Desktop-Client:** PySide6 mit SSE-Pipeline-Visualisierung
- **Chat-Integration:** Telegram Bot (Long Polling, Whitelist)

---

## Voraussetzungen

- **OS:** Linux (entwickelt auf Nobara). Windows/Mac technisch möglich, nicht getestet.
- **Hardware:**
  - **GPU** mit ≥ 24 GB VRAM (getestet: AMD Radeon 7900 XTX)
  - **RAM** ≥ 64 GB — erforderlich, nicht nur empfohlen
  - **CPU** mit vielen Kernen (getestet: Ryzen 9 7900X3D)
- **Software:**
  - Docker + Docker Compose
  - Ollama (host-native, nicht containerisiert)
  - Python 3.12 für den Desktop-Client

### Modell-Footprint

Nova betreibt parallel drei Sprachmodelle plus ein Embedding-Modell:

| Modell | Ausführung | Zweck | Größe |
|--------|-----------|-------|-------|
| `gemma4-gpu` | GPU (VRAM) | Chat, Agenten, Responder | ~17 GB |
| `nomic-embed-text` | GPU (VRAM) | Embeddings für KZG/LZG/Entity Resolution | ~0,6 GB |
| `gemma4-cpu` | CPU (RAM) | Pixie — Sprachaufgaben im Hintergrund | ~17 GB |
| `qwen3-32b-cpu` | CPU (RAM) | Pixie — Analyseaufgaben (Promotion, Recherche-Bewertung) | ~20 GB |

Beide CPU-Modelle liegen gleichzeitig im RAM, zusätzlich zu PostgreSQL, Redis und dem Server-Prozess. Deshalb sind 64 GB RAM keine Empfehlung, sondern Voraussetzung. Mit weniger wird das System anfangen zu swappen, was den Pixie-Durchsatz zerstört.

Ollama läuft bewusst host-native, damit die GPU direkt ansprechbar ist. Die Dienste im Container verbinden sich über `host.docker.internal`.

---

## Quick Start

### 1. Repo klonen

```bash
git clone https://codeberg.org/ClausVomBerg/novaberg.git
cd novaberg
```

### 2. Projektverzeichnis einrichten

Das Repository liegt in einem Projektverzeichnis neben den Runtime-Dateien:

```
<projekt-verzeichnis>/
├── novaberg/             # geklont
├── searxng/              # Runtime-State für SearXNG (leer anlegen, wird beim ersten Start befüllt)
├── .env                  # Secrets (aus Template erzeugen)
└── docker-compose.yml    # (aus Template erzeugen)
```

```bash
cd ..
mkdir searxng
cp novaberg/.env.template .env
cp novaberg/docker-compose.example.yml docker-compose.yml
```

### 3. `.env` ausfüllen

Mindestens diese Werte setzen:

- `TELEGRAM_BOT_TOKEN` — vom [BotFather](https://t.me/BotFather)
- `TELEGRAM_USER_MAP` — Deine Telegram-User-ID (bei [@userinfobot](https://t.me/userinfobot))
- `ANTHROPIC_API_KEY` — nur falls `LLM_PROFILE=claude` genutzt wird

### 4. Ollama einrichten

Zwei Ollama-Instanzen auf unterschiedlichen Ports (GPU + CPU):

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve &    # GPU
OLLAMA_HOST=0.0.0.0:11435 ollama serve &    # CPU
```

Modelle laden:

```bash
# GPU — Chat und Embedding
ollama pull gemma4-gpu
ollama pull nomic-embed-text

# CPU — Pixie-Hintergrundarbeit
ollama pull gemma4-cpu
ollama pull qwen3-32b-cpu
```

Die Modelfiles (Quantisierung, Kontextgröße, System-Prompts) liegen in `ollama/modelfiles/` als Referenz.

### 5. Dienste starten

```bash
docker compose up -d
```

Dienste:

- PostgreSQL auf `:5432`
- Redis auf `:6379`
- SearXNG auf `:8080`
- Nova-Server auf `:8000`
- Telegram-Bot (im Hintergrund)

### 6. Desktop-Client starten (optional)

```bash
cd novaberg/client
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## Konfiguration

Die zentrale Konfiguration liegt in `server/config.py`. Alle Parameter sind über Umgebungsvariablen überschreibbar (siehe `.env.template`).

**Wichtige Schalter:**

| Variable | Werte | Effekt |
|----------|-------|--------|
| `LLM_PROFILE` | `lokal`, `claude` | Umschaltung zwischen Ollama und Anthropic API |
| `OLLAMA_CONNECTOR` | `mistral`, `gemma4` | Modell-Stack innerhalb von `lokal` |

Feingranulare Parameter (Pixie-Intervalle, KZG-Thresholds, Such-Limits etc.) sind ebenfalls in `config.py` dokumentiert und über `PIXIE_*`-, `KZG_*`-, `NOTIZEN_*`-Variablen steuerbar.

> **Sicherheitshinweis (Dev-Only-Defaults):**
> Die Default-Werte in `config.py` und `docker-compose.example.yml` enthalten PostgreSQL-Credentials `ki:ki`. Diese sind ausschließlich für die lokale Entwicklungsumgebung gedacht. Für einen Produktionsbetrieb müssen `POSTGRES_URL` bzw. `POSTGRES_PASSWORD` zwingend in der `.env` auf eigene, sichere Werte gesetzt werden. Die `.env` darf nicht ins Repository eingecheckt werden.

---

## Dokumentation

Die Architektur ist ausführlich dokumentiert in `Dokumentation/`:

- `nova-architecture.md` — Gesamtübersicht
- `nova-graph.md` — Human Graph Pipeline
- `nova-pixie.md` — Hintergrundagent
- `nova-memory.md` — Gedächtnis-Schichten
- `nova-ei.md` — Emotionale Intelligenz
- `nova-node-*.md` — Einzelne Pipeline-Knoten
- `nova-thinking-curiosity.md` — Neugier und intrinsische Motivation
- `nova-roadmap.md` — Projektchronik
- `nova-backlog.md` — Zukunftskonzepte

---

## Troubleshooting

**Ollama nicht erreichbar aus Container:**
Prüfen ob `host.docker.internal` aufgelöst wird. Unter Linux ist `extra_hosts: - "host.docker.internal:host-gateway"` in der Compose-Datei nötig (bereits eingetragen).

**SearXNG liefert keine Ergebnisse:**
Engines können durch Rate-Limits blockiert sein. Settings-Datei unter `searxng/settings.yml` anpassen — nach dem ersten Start hat SearXNG sie dort abgelegt.

**PostgreSQL-Verbindung schlägt fehl:**
Der Server hat `depends_on.postgres.condition: service_healthy`. Wenn der Healthcheck fehlschlägt, prüfen ob Port 5432 auf dem Host bereits belegt ist.

**Gemma 4 JSON-Output bricht ab:**
Bekanntes Problem (Ollama #15260). Workaround ist im Code implementiert (Cleanup-Pipeline in `config.py`).

---

## Status

Nova ist aktiv in Entwicklung. Einzelentwicklung, keine externen Beiträge vorgesehen. Die Roadmap in `Dokumentation/nova-roadmap.md` zeigt den historischen Fortschritt, `nova-backlog.md` die offenen Konzepte.

---

## Lizenz
Lizenziert unter der Apache License, Version 2.0.