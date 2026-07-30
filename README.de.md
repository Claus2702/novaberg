# Novaberg — The Nova Anima Resonance System

**Eine kognitive Architektur für persönliche KI — mit emergenter Persönlichkeit, intrinsischer Neugier und emotionaler Intelligenz. Lokal, privat, deins.**

🇬🇧 [English version](README.md)

---

**Nova** ist ein lokaler, privatsphäre-orientierter persönlicher KI-Assistent mit einer kognitiven Architektur. Kein einfacher Chatbot, sondern ein System aus spezialisierten Agenten, geschichtetem Gedächtnis, emotionaler Intelligenz und einem autonomen Hintergrundagenten. Nova entwickelt eigene Interessen, Ziele und Emotionen, die ihr Gespräch und Denken beeinflussen — mit einem eigenen Emotionsstrang neben dem des Nutzers.

**Leitgedanke:** Das LLM ist ein Sprachprozessor, kein Wissensspeicher. Echtes Wissen liegt in PostgreSQL, Redis und im Web. Intelligenz entsteht aus der parallelen Bewertung durch spezialisierte Perspektiven.

---

## Überblick

Ein einzelner Gesprächszug läuft durch **zwei** Graphen, nicht durch einen:

- **Human Graph** (5 Knoten) — Perzeption → Enricher → EI-Calc → Salienz → Dispatcher. Klassifiziert, was der Nutzer gesagt hat, lädt Kontext, berechnet Emotion und Salienz und speichert, was es wert ist. Er erzeugt bewusst keine Antwort.
- **Character Graph** (18 Knoten) — DB-Zugriff → EI-Calc → Enricher → Emotionale Gravitation → Reducer → Router → Planner → Agent-Dispatch → Gesprächsvektor → Responder → Thinker → Tribunal → Evaluate, danach Novas eigene Perzeption, Salienz und Speicherung. Hier entsteht die Antwort — und hier nimmt Nova ihren eigenen Zug genauso wahr und merkt ihn sich genauso, wie sie es mit dem des Nutzers tut.

Verbunden sind beide über eine Redis-Ereigniswarteschlange: Der Human Graph hinterlässt ein Ereignis, ein Konsument startet einen Character-Graph-Lauf, und die Antwort erreicht den Client über einen WebSocket. Ein dritter Graph, der **Agent Graph** (3 Knoten), bedient Züge, die von Agenten stammen statt von Menschen.

- **Pixie** (Hintergrund) — der autonome Hintergrundagent. Sechzehn Agenten konkurrieren nach Priorität: Promotion und Decay über beide Gedächtnisschichten, Charakter-Destillation, Wiedervorlage, Recherche, Kalibrierung, Wissenslücken, Timeline und Notizen.

Geschichtetes Gedächtnis:

| Schicht | Technologie | Zweck |
|---------|-------------|-------|
| Kurzzeit (KZG) | Redis + Vektorsuche | Aktive Gedanken, TTL-basiert |
| Langzeit (LZG) | PostgreSQL | Verfestigte Erinnerungen mit Ebbinghaus-Decay |
| Knowledge Graph | PostgreSQL | Entitäten, Fakten, bi-temporales Modell |
| Charakter-Hash | PostgreSQL | Destillierte Persönlichkeitsprofile und die daraus abgeleiteten Charakter-Räder |

Multi-Channel: Desktop-Client (GTK4) und Telegram-Bot nutzen dieselbe FastAPI-Server-Instanz.

---

## Screenshots

### Chat — Kognitive Pipeline in Echtzeit

![Chat mit Pipeline-Stages](images/nova-ui-chat-1.png)

Jede Nachricht durchläuft die vollständige kognitive Pipeline. Die Stage-Indikatoren unter der Konversation zeigen jeden Verarbeitungsschritt in Echtzeit: Die Perzeption klassifiziert Intent und Emotion, der Router bestimmt den Verarbeitungspfad, der Enricher lädt relevanten Kontext aus dem Gedächtnis, der Gesprächsvektor formt Novas eigene Gesprächsintention, und der Responder generiert die Antwort. Das ist keine Dekoration — es ist die Live-Spur der kognitiven Pipeline: fünf Knoten auf dem Wahrnehmungspfad, achtzehn weitere auf dem Pfad, der die Antwort formt.

![Chat — Gespräch ohne Stages](images/nova-ui-chat-2.png)

Dieselbe Konversation nach dem Verblassen der Pipeline-Stages. Markdown-Rendering, native Emoji-Darstellung und klare visuelle Trennung zwischen User- und Assistenten-Nachrichten. Novas Persönlichkeit entsteht aus geschichteter Charakter-Destillation, nicht aus einem statischen System-Prompt.

### Emotionale Intelligenz — Plutchik-Oktagon

![Emotions-Panel mit Radar-Diagrammen](images/nova-ui-emotion-1.png)

Novas emotionaler Zustand, visualisiert über die 8 Plutchik-Sektoren (Freude, Zuversicht, Angst, Überraschung, Trauer, Enttäuschung, Ärger, Neugier). Zwei Radar-Diagramme vergleichen das aktuelle Session-Profil mit der emotionalen Langzeit-Landschaft aus dem Kurzzeitgedächtnis. Darunter alle 16 kanonischen Emotionen mit ihren aktuellen Werten. Das Session-Radar zeigt, was jetzt passiert; das KZG-Radar zeigt den emotionalen Fingerabdruck über Wochen der Konversation.

### Session — Analyse auf Turn-Ebene

![Session-Panel](images/nova-ui-session-1.png)

Jeder Gesprächs-Turn wird mit seinen analytischen Metadaten gespeichert: klassifizierter Intent, erkannte Emotion und Gesprächsmodus. Die Zusammenfassung oben wird automatisch aus dem Session-Kontext generiert. Das ist das Rohmaterial, aus dem der Enricher situative Awareness für den Responder aufbaut — hier sichtbar für Kalibrierung und Debugging.

### Kurzzeitgedächtnis (KZG)

![KZG-Panel](images/nova-ui-shorttermmemory-1.png)

Novas Kurzzeitgedächtnis-Einträge, hier für User „nova" — Novas eigene Gedanken. Jeder Eintrag trägt einen Salienz-Score, thematische Tags, eine Dimensions-Klassifikation und einen TTL-Countdown. Einträge über dem Promotions-Tor — 0.94 auf der hier gezeigten Skala, das sind 0.7 vor der Salienz-Kurve — sind Kandidaten für die Konsolidierung ins Langzeitgedächtnis durch den Pixie-Hintergrundagenten. Der Inhalt ist Novas eigene Perspektive: „Für Nova gibt es kaum etwas Besseres als eine reife Tomate frisch vom Strauch."

### Langzeitgedächtnis (LZG)

![LZG-Panel](images/nova-ui-longtermmemory-1.png)

Konsolidierte Erinnerungen, die den Promotions-Prozess überlebt haben. Jeder Eintrag hat ein Gewicht (verstärkt durch Abruf — der Testing Effect), eine Wissens-Dimension und Zeitstempel für Erstellung und letzte Verstärkung. Das ist die persistente Schicht — Erinnerungen hier verfallen nach der Ebbinghaus-Vergessenskurve, werden aber bei jedem Abruf durch den Enricher gestärkt.

### Charakter — Emergente Persönlichkeitsprofile

![Charakter-Panel — Novas Selbstmodell](images/nova-ui-character-1.png)

Fünf destillierte Persönlichkeitsprofile, hier für Nova selbst. Das sind keine handgeschriebenen Beschreibungen, sondern das Ergebnis von Pixies Charakter-Destillationsagent, der periodisch Kurzzeit- und Langzeitgedächtnis zu strukturierten Profilen verdichtet. Das Kern-Profil erfasst, wer Nova geworden ist; das Adaptiv-Profil spiegelt ihre aktuellen Beschäftigungen; Intentionen und Emotionen beschreiben ihre Kommunikationsmuster und emotionale Grundlinie; das Beziehungs-Profil modelliert ihre Wahrnehmung des Nutzers. Alle fünf Schichten fließen in den Identitäts-Block des Responders ein.

Aus diesen Profilen werden zwei **Charakter-Räder** abgeleitet, und die sind der Teil, der handelt statt beschreibt. Jedes stellt Einzelfragen an den destillierten Charakter — zwölf für die Zuwendung, zehn für die Initiative —, die ein LLM mit *nicht erkennbar*, *angedeutet* oder *ausgeprägt* beantwortet; der Faktor daraus wird **gerechnet**, nie geschätzt. Die Zuwendung gewichtet, wie stark die Belange des Gegenübers zählen, wenn Nova entscheidet, was sie sich merkt; die Initiative verschiebt die Achse, die bestimmt, wer das Gespräch führt. Beide legen ihre Einzelbewertungen neben der Zahl ab, sodass jeder Faktor von Hand nachrechenbar ist, und beide tragen ein Herkunftsfeld — denn ein Wert, der genau auf seinem Nullpunkt landet, ist eine Messung und darf nicht aussehen wie einer, der nie erhoben wurde. *(Der Screenshot oben ist älter als die Räder.)*

---

## Technologie-Stack

- **Backend:** Python, FastAPI, LangGraph, APScheduler
- **Datenbanken:** PostgreSQL 16 mit pgvector, Redis Stack
- **LLM:** Ollama (lokal) mit Gemma 4 oder Mistral Small 3.2; optional Anthropic Claude API
- **Embedding:** `nomic-embed-text-v2-moe` via Ollama
- **Suchmaschine:** SearXNG (Docker)
- **Desktop-Client:** GTK4 (PyGObject) + WebKitGTK mit SSE-Pipeline-Visualisierung
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
  - GTK4, WebKitGTK, PyGObject (auf Fedora/Nobara vorinstalliert)

### Modell-Footprint

Nova betreibt parallel drei Sprachmodelle plus ein Embedding-Modell:

| Modell | Ausführung | Zweck | Größe |
|--------|-----------|-------|-------|
| `gemma4-gpu` | GPU (VRAM) | Chat, Agenten, Responder | ~17 GB |
| `nomic-embed-text-v2-moe` | GPU (VRAM) | Embeddings für KZG/LZG/Entity Resolution | ~1,0 GB |
| `gemma4-cpu` | CPU (RAM) | Pixie — Sprachaufgaben im Hintergrund | ~17 GB |
| `qwen3-32b-cpu` | CPU (RAM) | Pixie — Analyseaufgaben (Promotion, Recherche-Bewertung) | ~20 GB |

Beide CPU-Modelle liegen gleichzeitig im RAM, zusätzlich zu PostgreSQL, Redis und dem Server-Prozess. Deshalb sind 64 GB RAM keine Empfehlung, sondern Voraussetzung. Mit weniger wird das System anfangen zu swappen, was den Pixie-Durchsatz zerstört.

Ollama läuft bewusst host-native, damit die GPU direkt ansprechbar ist. Die Dienste im Container verbinden sich über `host.docker.internal`.

---

## Quick Start

### 1. Repo klonen

```bash
git clone https://github.com/Claus2702/novaberg.git
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
ollama pull nomic-embed-text-v2-moe

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
# Abhängigkeiten installieren (Fedora/Nobara — das meiste ist vorinstalliert)
sudo dnf install -y python3-requests python3-websocket-client python3-markdown

# Starten
python3 novaberg/client/main.py
```

---

## Konfiguration

Die zentrale Konfiguration liegt in `server/config.py`. Alle Parameter sind über Umgebungsvariablen überschreibbar (siehe `.env.template`).

**Wichtige Schalter:**

| Variable | Werte | Effekt |
|----------|-------|--------|
| `LLM_PROFILE` | `lokal`, `claude` | Umschaltung zwischen Ollama und Anthropic API |
| `OLLAMA_CONNECTOR` | `mistral`, `gemma4`, `qwen36` | Modell-Stack innerhalb von `lokal` |

Feingranulare Parameter (Pixie-Intervalle, KZG-Thresholds, Such-Limits etc.) sind ebenfalls in `config.py` dokumentiert und über `PIXIE_*`-, `KZG_*`-, `NOTIZEN_*`-Variablen steuerbar.

> **Sicherheitshinweis (Dev-Only-Defaults):**
> Die Default-Werte in `config.py` und `docker-compose.example.yml` enthalten PostgreSQL-Credentials `ki:ki`. Diese sind ausschließlich für die lokale Entwicklungsumgebung gedacht. Für einen Produktionsbetrieb müssen `POSTGRES_URL` bzw. `POSTGRES_PASSWORD` zwingend in der `.env` auf eigene, sichere Werte gesetzt werden. Die `.env` darf nicht ins Repository eingecheckt werden.

---

## Dokumentation

Die Architektur ist ausführlich dokumentiert in `docs/`:

- `novaberg-architecture.md` — Gesamtübersicht
- `novaberg-graph.md` — Graph-Architektur und Pipeline
- `novaberg-pixie.md` — Hintergrundagent
- `novaberg-memory.md` — Gedächtnis-Schichten
- `novaberg-ei.md` — Emotionale Intelligenz
- `novaberg-node-*.md` — Einzelne Pipeline-Knoten (23 Dokumente)
- `novaberg-thinking-curiosity_k.md` — Neugier und intrinsische Motivation
- `novaberg-thinking-drive_k.md` — Antrieb, Ziele und Dual-Emotion
- `novaberg-roadmap.md` — Projektchronik
- `novaberg-backlog.md` — Zukunftskonzepte

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

Nova ist aktiv in Entwicklung. Einzelentwicklung, keine externen Beiträge vorgesehen. Die Roadmap in `docs/novaberg-roadmap.md` zeigt den historischen Fortschritt, `novaberg-backlog.md` die offenen Konzepte.

---

## Lizenz
Lizenziert unter der Apache License, Version 2.0.
