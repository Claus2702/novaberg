# Nova — Systemarchitektur

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Systemarchitektur, Tech-Stack, Plugin-System
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-architecture.md
**Quellen:** nova-00-a.md (Architektur-Übersicht), nova-07-a.md (Tech-Stack), nova-07-m-a.md (Plugin-System)

---

## 1. Technologie-Stack

### 1.1 Hardware

| Komponente | Spezifikation | Rolle |
|------------|---------------|-------|
| CPU | AMD Ryzen 9 7900X3D (12 Kerne) | Pixie-LLM (CPU-Modell), allgemeine Verarbeitung |
| RAM | 64 GB DDR5 6000MT/s | CPU-Modell (~36 GB), OS, Docker-Services |
| GPU | AMD Radeon RX 7900 XTX (24 GB VRAM) | Chat-LLM (~14 GB), Embeddings (~0.6 GB) |
| OS | Nobara Linux (Fedora-basiert) | ROCm-Kompatibilität für AMD-GPU |

**VRAM-Budget:** 14 GB (Chat Q4) + 0.6 GB (Embeddings) = ~14.6 GB von 24 GB.

### 1.2 Docker-Services

| Service | Technologie | Port | Rolle |
|---------|------------|------|-------|
| **server** | Python 3.12, FastAPI + LangGraph | 8000 | API-Server, Graph-basierte Agenten, Pixie |
| **postgres** | PostgreSQL 16 + pgvector | 5432 | LZG, Entitäten, Fakten, Timeline, Notizen |
| **redis** | Redis 7 Stack (mit RediSearch) | 6379 | KZG, Session, Queues, Stacks, Vektorsuche |
| **searxng** | SearXNG | 8080 | Lokale Metasuchmaschine (JSON-API) |
| **telegram-bot** | Python, Long Polling | — | Multi-Channel-Zugang (seit Chat 41) |

### 1.3 Host-native Services (Ollama)

| Instanz | Port | Hardware | Warum nicht Docker? |
|---------|------|----------|---------------------|
| **Ollama GPU** | 11434 | VRAM (ROCm) | ROCm-Versionsinkompatibilität zwischen Docker-Image und Host |
| **Ollama CPU** | 11435 | RAM | Separate Instanz fuer Pixie |

ROCm-Versionen im Docker-Image und auf dem Host sind inkompatibel. Ollama muss daher direkt auf dem Host laufen, alle anderen Services (FastAPI, PostgreSQL, Redis, SearXNG) laufen in Docker.

### 1.4 Client

| Komponente | Technologie | Rolle |
|------------|------------|-------|
| Desktop-Client | PyQt6 | Chat-UI, Panels (Fakten, Gedaechtnis, Timeline, Schatten, Status, System, Emotions-Radar), WebSocket-Empfang |

---

## 2. LLM-Architektur

### 2.1 Tri-LLM + Claude API

| Modell | Ollama-Name | Hardware | Context | Verbrauch | Zweck |
|--------|-------------|----------|---------|-----------|-------|
| Gemma4 26B-A4B (MoE, Q4) | `gemma4-gpu` | VRAM | 32768 | ~17 GB (Q4) | Chat (HumanGraph) — Standard |
| Gemma4 26B-A4B (MoE, Q4) | `gemma4-cpu` | RAM | 32768 | — | Pixie Sprache (Fliesstext, Charakter-Treue) |
| Qwen3-32B | `qwen3-32b-cpu` | RAM | 32768 | ~19 GB (Q4) | Pixie Analyse (Reasoning, JSON, Planung) |
| Mistral Small 3.2 (24B) | `mistral-small3.2-gpu` | VRAM | 16384 | ~14 GB (Q4) | Chat (HumanGraph) — Fallback-Connector |
| Mistral Small 3.2 (24B) | `mistral-small3.2-cpu` | RAM | 32768 | ~17 GB (Q5) | Pixie Sprache — Fallback-Connector |
| Nomic Embed Text | `nomic-embed-text` | VRAM | 2048 | ~0.6 GB | Embedding-Erzeugung |
| Claude Sonnet | — (API) | extern | — | ~$0.02/Turn | Alternativer Chat-Provider (Profil `claude`) |

Modelle werden ueber das **Connector-System** in `config.py` gesteuert (`OLLAMA_CONNECTOR`). Aktuell verfuegbar: `gemma4` (Standard) und `mistral` (Fallback). Umschalten ueber Env-Variable, Neustart genuegt. Mistral bleibt als Connector verfuegbar und wird nicht geloescht.

GPU-Modell (Chat) und CPU-Modelle (Pixie) laufen auf getrennter Hardware. Kein Lock, kein Warten, echte Parallelitaet. Pixie nutzt Qwen3-32B fuer Analyse/Reasoning und das CPU-Sprachmodell fuer Sprachausgabe — statisches Routing pro Workflow-Schritt.

**Modelfiles:** `ollama/modelfiles/` enthaelt die Modelfile-Definitionen mit `num_ctx` und `num_gpu`-Konfiguration. Single Source of Truth fuer Context-Groesse.

### 2.1.1 Connector-System (Chat 46)

`OLLAMA_CONNECTORS` in `config.py` definiert Modell-Profile. Jeder Connector legt fest: GPU-Modell, CPU-Modell, Analyse-Modell, Context-Groessen, Think-Default. Die bestehenden Variablen (`OLLAMA_MODEL`, `SHADOW_MODEL` etc.) werden beim Start aus dem aktiven Connector aufgeloest.

Umschalten: `OLLAMA_CONNECTOR=gemma4|mistral` in `.env`, Neustart.

| Connector | GPU-Modell | CPU-Modell | Analyse-Modell | GPU ctx |
|-----------|------------|------------|----------------|---------|
| `gemma4`  | `gemma4-gpu` | `gemma4-cpu` | `qwen3-32b-cpu` | 32768 |
| `mistral` | `mistral-small3.2-gpu` | `mistral-small3.2-cpu` | `qwen3-32b-cpu` | 16384 |

### 2.1.2 Prompt-Segregation (Chat 46-47)

Statische Prompt-Bloecke sind aus den Node-Dateien in Textdateien extrahiert. Verzeichnisstruktur:

```
server/prompts/
  default/     — 51 Bloecke (alle Nodes)
  gemma4/      — 7 Overrides (JSON-Regeln, Tribunal-Prompts)
  mistral/     — leer (nutzt Defaults)
```

Lademechanismus: `prompt_loader.py` liest beim Start alle `.txt` aus `default/`, dann ueberschreibt der aktive Connector. Dictionary auf `PROMPTS` in `config.py`. Nodes greifen ueber `PROMPTS["node.block"]` zu.

Namenskonvention: `{node}.{block}.txt` — Beispiel: `router.identity.txt`, `salienz.rules.txt`, `tribunal_jurist.system.txt`.

Alle LLM-Prompts aus Python-Code extrahiert (Chat 46: Perzeption, Router, Salienz, Tribunal; Chat 47: Responder, Thinker, Corrector, GV, KZG-Verdichtung, 4x Classify-Nodes). 0 hardcoded Prompts in Python. Konvention: Alle PROMPTS[]-Zugriffe durch `.format()`, literale Klammern in LLM-Beispielen als `{{ }}` escaped.

### 2.2 Provider-Architektur

```
Nodes / Manager
    -> get_chat_provider()        # Chat-Pipeline (GPU oder Claude API)
    -> get_background_provider()  # Pixie-Tasks (CPU Mistral)
    -> embed_client               # Embedding (immer Ollama, nicht abstrahiert)

Pixie-Agenten (seit Chat 38)
    -> pixie_llm_call(modus="analyse")   # Qwen3-32B (Reasoning, JSON)
    -> pixie_llm_call(modus="sprache")   # Mistral CPU (Fliesstext, Deutsch)
```

### 2.3 Klassen

| Klasse | Beschreibung |
|--------|-------------|
| `LLMProvider` (ABC) | Abstrakte Basisklasse mit `generate()` und `chat()` |
| `OllamaProvider` | Wrapper um `ollama.Client` — kapselt model, num_ctx, options. `think=False` nativ. |
| `AnthropicProvider` | Wrapper um `anthropic.Anthropic` — Token-Logging mit Kosten, `[AUSGABEFORMAT]`-Block provider-intern, `top_p`-Ignorierung (Anthropic erlaubt nicht `temperature` + `top_p` gleichzeitig). |

### 2.4 Profile

Umschaltbar ueber `LLM_PROFILE` in `config.py` / `.env`:

| Profil | Chat-Provider | Background-Provider | Use Case |
|--------|--------------|--------------------|---------|
| `lokal` | OllamaProvider (GPU, Mistral) | OllamaProvider (CPU, Mistral) | Produktivbetrieb (Standard) |
| `claude` | AnthropicProvider (Sonnet) | OllamaProvider (CPU, Mistral) | Evaluierung, Prompt-Tuning, Vergleichstests |

### 2.5 Pixie Dual-Modell-Routing (seit Chat 38)

```python
def pixie_llm_call(prompt: str, modus: str = "analyse", ...) -> str:
    """modus: 'analyse' -> Qwen3-32B, 'sprache' -> Mistral Q5"""
```

Statisches Routing pro Workflow-Schritt. CJK-Guard fuer Qwen-Output. JSON-Fallback bei Parse-Fehlern.

### 2.6 Embedding

Embedding (`nomic-embed-text`) ist bewusst **nicht** Teil der Provider-Abstraktion. Es bleibt direkt auf Ollama via `embed_client`. Grund: Vektorkonsistenz — ein Wechsel des Embedding-Modells wuerde alle gespeicherten Vektoren invalidieren.

### 2.7 Konfigurationsvariablen (LLM)

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| `LLM_PROFILE` | `"lokal"` | Aktives Profil (`lokal` oder `claude`) |
| `ANTHROPIC_API_KEY` | `""` | API-Key fuer Claude (aus `.env`) |
| `ANTHROPIC_MODEL` | `"claude-sonnet-4-6"` | Claude-Modell |
| `PIXIE_MODELL_ANALYSE` | `"qwen3-32b-cpu"` | Pixie Analyse-Modell |
| `PIXIE_MODELL_SPRACHE` | `"mistral-small3.2-cpu"` | Pixie Sprach-Modell |
| `OLLAMA_CONNECTOR` | `"gemma4"` | Aktiver Modell-Connector (`gemma4` oder `mistral`) |

### 2.8 Bekannter Bug: Ollama think+format (Chat 46)

Ollama Issue #15260: Bei Gemma4 (und Qwen3.5) bricht `think=false` den `format="json"`-Constraint — JSON wird stillschweigend ignoriert.

Workaround: `think=False` immer senden, `format="json"` NICHT senden. JSON-Einhaltung erfolgt ueber Prompt-Overrides (Gemma4-spezifische `[REGELN]`) + Cleanup-Pipeline (`_clean_json_response` + `_deduplicate_repetition` + `_repair_truncated_json`) im `OllamaProvider`.

Status: Ollama-Bug offen (Stand 15.04.2026).

---

## 3. Projektstruktur

```
project/
├── client/
│   ├── main.py                          # PyQt6 Einstieg
│   └── ui/                              # Chat, Fakten, Gedaechtnis, Timeline, Schatten,
│                                        #   Status, System-Panels, Hauptfenster,
│                                        #   Emotions-Radar (QPainter)
├── server/
│   ├── main.py                          # App-Start, Lifespan, Router-Includes (~60 Zeilen)
│   ├── config.py                        # Zentrale Konfiguration, Umgebungsvariablen
│   │
│   ├── api/                             # REST + WebSocket Endpoints
│   │   ├── chat.py                      #   /chat, /chat/stream, SSE
│   │   ├── health.py                    #   /health (5 Dienste + Pixie), /modelle
│   │   ├── gedaechtnis.py               #   /gedaechtnis/*, /fakten/*, /emotionen/*
│   │   ├── session.py                   #   /session/*
│   │   ├── websocket.py                 #   WebSocket-Endpoint
│   │   ├── admin.py                     #   /admin/pixie/* (Pause, Resume, Flush)
│   │   └── models.py                    #   Pydantic-Modelle
│   │
│   ├── graph/                           # LangGraph Graphen + State
│   │   ├── base.py                      #   GraphBase (abstrakt)
│   │   ├── human_graph.py               #   HumanGraph (Chat-Pipeline)
│   │   ├── agent_graph.py               #   AgentGraph (Pixie-Pipeline)
│   │   ├── builder.py                   #   Fassade, Plugin-Init
│   │   ├── state.py                     #   State-Definition, PendingWrite
│   │   ├── memory.py                    #   Graph-Checkpoint-Memory
│   │   └── nodes/                       #   12 Graph-Nodes
│   │       ├── perzeption.py            #     → nova-node-perception.md
│   │       ├── router.py                #     → nova-node-router.md
│   │       ├── enricher.py              #     → nova-node-enricher.md
│   │       ├── planner.py               #     → nova-node-planner.md
│   │       ├── responder.py             #     → nova-node-responder.md
│   │       ├── thinker.py               #     → nova-node-thinker.md
│   │       ├── salience.py              #     → nova-node-salience.md
│   │       ├── dispatcher.py            #     → nova-node-dispatcher.md
│   │       ├── tribunal.py              #     → nova-node-tribunal.md
│   │       ├── corrector.py             #     → nova-node-corrector.md
│   │       ├── agent_dispatch.py        #     Agent-Dispatch (Epic 11)
│   │       └── gespraechsvektor.py      #     → nova-ei-conversation-vector.md
│   │
│   ├── agents/                         # Agent-System (Epic 11 + Epic 5)
│   │   ├── __init__.py                 #   AgentRegistry, Auto-Discovery
│   │   ├── base.py                     #   BaseAgent, AgentState, AgentResult, PeriodicTask
│   │   ├── notizen/                    #   NotizenAgent (6 Module)
│   │   ├── timeline/                   #   TimelineAgent (6 Module)
│   │   ├── kzg/                        #   KZG-Agent (LangGraph-Subgraph, 5 Nodes)
│   │   ├── delegation/                 #   DelegationsAgent (Halluzinations-Ventil)
│   │   ├── recherche/                  #   RechercheAgent (Web-Recherche fuer Pixie)
│   │   ├── promotion/                  #   PromotionAgent (KZG -> LZG)
│   │   ├── decay/                      #   DecayAgent (Ebbinghaus)
│   │   ├── charakter/                  #   CharakterAgent (Hash-Destillation)
│   │   └── wiedervorlage/              #   WiedervorlageAgent
│   │
│   ├── tools/                          # Tool-Manager (Epic 11)
│   │   ├── db_manager.py              #   PostgreSQL + Connection Pool
│   │   ├── redis_manager.py           #   Redis (nativ threadsafe)
│   │   ├── embedding_manager.py       #   Ollama Embeddings
│   │   ├── file_manager.py            #   Dateisystem + Lock-Dict
│   │   ├── time_parser.py             #   Zeitparser-Proxy
│   │   └── web/                       #   Web-Infrastruktur (Chat 35)
│   │       ├── __init__.py            #     Package-Init
│   │       ├── search.py              #     WebSearchManager (SearXNG)
│   │       └── fetch.py               #     PageFetcher (trafilatura + BS4)
│   │
│   ├── memory/                          # Gedaechtnis-Schicht
│   │   ├── embedding.py                 #   Embedding-Erzeugung (nomic-embed-text)
│   │   ├── kzg.py                       #   Kurzzeitgedaechtnis (Redis)
│   │   ├── lzg.py                       #   Langzeitgedaechtnis (PostgreSQL)
│   │   ├── charakter.py                 #   Charakter-Hash
│   │   ├── session.py                   #   Session/Gespraechskontext
│   │   ├── fakten.py                    #   Deklaratives Wissen
│   │   ├── timeline.py                  #   Temporale Fakten
│   │   └── kontext.py                   #   Session-Kontext-Extraktion (LLM-gestuetzt)
│   │
│   ├── utils/                           # Hilfsfunktionen
│   │   └── zeitparser.py                #   Zeitaufloesung (Fuzzy + Normalisierung + Vektor)
│   │
│   ├── plugins/                         # Manager-Plugins
│   │   ├── base.py                      #   BaseManager Interface
│   │   ├── kzg_manager/                 #   KZG-Schreiboperationen
│   │   ├── fakten_manager/              #   Fakten + Entity Resolution
│   │   ├── timeline_manager/            #   Termine + Zeitparser
│   │   ├── notizen_manager/             #   Merkzettel, Listen
│   │   ├── charakter_identitaet_manager/#   Charakter-Identität (Selbstbeschreibung)
│   │   └── direktiven_manager/          #   Direktiven (Verhaltensregeln)
│   │
│   └── services/                        # Dienste
│       ├── llm_provider.py             #   → nova-tool-llm-abstraction.md
│       ├── shadow_delivery.py           #   Pixie -> Chat-Einspeisung
│       ├── shadow_agent/                #   Alter Pixie-Runner (wird bei PIX-CLEAN entfernt)
│       └── pixie/                       #   Neues Pixie-System (Chat 33+)
│           ├── scheduler.py             #     APScheduler-Heartbeat
│           ├── kandidaten.py            #     Queue-Peek + periodische Aufgaben
│           ├── router.py                #     Aufgabe -> Agent-Name
│           ├── dispatch.py              #     Agent-Ausfuehrung
│           └── stack.py                 #     Shadow-Stack Push
│
├── db/
│   └── init.sql                         # Kern-Schema (LZG, Entitaeten)
│
├── ollama/
│   └── modelfiles/                      # GPU + CPU Modelfiles
│
└── docker-compose.yml
```

---

## 4. Plugin-System

### 4.1 Ueberblick

Das Plugin-System ist Novas Erweiterungsmechanismus fuer strukturiertes Wissen. Jeder Manager ist ein eigenstaendiges Plugin, das sich beim System registriert und dem Router, Enricher, der Salienz und dem Planner mitteilt, was es kann. Neue Faehigkeiten entstehen durch neue Ordner in `plugins/`, nicht durch Aenderungen am Graph.

### 4.2 BaseManager — Das Interface

`plugins/base.py` definiert die abstrakte Basisklasse. Alle Methoden sind optional — ein Manager implementiert nur, was er braucht:

| Methode / Property | Rueckgabe | Aufgabe | Aufrufer |
|-------------------|----------|---------|----------|
| `name` | `str` | Eindeutiger Name (z.B. `"fakten"`) | Logging, Registry |
| `router_intents` | `set[str]` | Intents, die dieser Manager bedient | Planner (Prioritaet 2) |
| `router_prompt` | `str` | Ergaenzung zum Router-Prompt | Router |
| `salienz_prompt` | `str` | Ergaenzung zum Salienz-Prompt | Salienz |
| `enricher_prompt` | `str` | Kontext-Beschreibung | Enricher |
| `enrich(state, postgres_url)` | `str` | Kontext liefern (Fakten, Termine, Notizen) | Enricher |
| `plan(state, postgres_url)` | `dict` | Management-Aktion planen (LLM via `get_chat_provider()`) | Planner |
| `execute(writes, user_id, redis_client, postgres_url, embed_client, embed_model)` | `int` | DB-Writes ausfuehren | Dispatcher |
| `setup(postgres_url)` | — | Schema anlegen (`init.sql` ausfuehren) | GraphBase beim Start |

### 4.3 Selbstbeschreibende Prompts

Die drei Prompt-Properties (`router_prompt`, `salienz_prompt`, `enricher_prompt`) sind der Kern des Plugin-Prinzips: Der Manager beschreibt sich selbst, statt dass der Router oder Enricher ihn kennen muss. Wenn ein neuer Manager hinzukommt, lernt der Router automatisch seine Trigger-Phrasen — weil der Router-Prompt dynamisch aus allen registrierten Managern zusammengesetzt wird.

### 4.4 Auto-Discovery

`plugins/__init__.py` enthaelt `discover_managers()`:

1. Scannt alle Unterordner von `plugins/` mit `_manager` im Namen
2. Importiert das Package (erwartet `__init__.py`)
3. Findet alle `BaseManager`-Subklassen
4. Instanziiert und registriert sie in der Plugin-Registry (ein Dict: `name -> Manager-Instanz`)

Kein manuelles Registrieren, keine Import-Liste. Neuer Ordner = neuer Manager.

### 4.5 Die sechs Manager

| Manager | Ordner | Verantwortung |
|---------|--------|---------------|
| **KzgManager** | `plugins/kzg_manager/` | KZG-Schreiboperationen (Store, Verstaerkung) |
| **FaktenManager** | `plugins/fakten_manager/` | Fakten + Entity Resolution (Typ 1 + 2, bi-temporal) |
| **TimelineManager** | `plugins/timeline_manager/` | Termine + Zeitparser (CRUD) |
| **NotizenManager** | `plugins/notizen_manager/` | Merkzettel, Listen, Snippets (CRUD + Append) |
| **CharakterIdentitaetManager** | `plugins/charakter_identitaet_manager/` | Router-Prompt für Identitätszuweisungen (CRUD via CharakterIdentitaetAgent) |
| **DirektivenManager** | `plugins/direktiven_manager/` | Router-Prompt für Verhaltensdirektiven (CRUD via DirektivenAgent) |

| Manager | `enrich()` | `plan()` | `execute()` | Besonderheit |
|---------|-----------|---------|-------------|-------------|
| **KzgManager** | — | — | KZG Store/Verstaerkung | Kein LLM, kein Plan. Nur Write. |
| **FaktenManager** | Relevante Fakten laden | — | Fakten CRUD + Entity Resolution | Bi-temporal, Typ 1 + 2 |
| **TimelineManager** | Termine im Zeitraum laden | LLM plant CRUD | Zeitparser + DB-Write | Datum-Inferenz via `utils/zeitparser.py` |
| **NotizenManager** | Aktive Notizen als Uebersicht | LLM plant CRUD + Append | Text-Updates via LLM | Rueckfrage-Logik |

### 4.6 PendingWrite — Das Austauschformat

```python
PendingWrite = TypedDict("PendingWrite", {
    "ziel":         str,   # "kzg", "fakten", "timeline", "notizen"
    "aktion":       str,   # "create", "update", "delete"
    "daten":        dict,  # Manager-spezifische Payload
    "beschreibung": str,   # Menschenlesbar fuer Logging
})
```

**Salienz-Guard (P5/P6):** Wenn der Planner in diesem Turn aktiv war, unterdrueckt die Salienz ihre eigenen Writes fuer `fakten` und `timeline`. Sonst entstehen Doppeleintraege — zwei Zahnarzttermine, einmal vom Planner, einmal von der Salienz. KZG-Writes bleiben aktiv.

### 4.7 Koexistenz mit Agent-System (seit Chat 22, Epic 11)

Seit Epic 11 ersetzen Agenten die Manager schrittweise:

| Manager | Agent | Status |
|---------|-------|--------|
| NotizenManager | NotizenAgent | Agent fuehrt aus, Manager liefert router_prompt + enrich() |
| TimelineManager | TimelineAgent | Agent fuehrt aus, Manager liefert router_prompt + enrich() |
| FaktenManager | — | Noch nicht migriert |
| KzgManager | — | Noch nicht migriert |

Die Manager bleiben als duenne Huellen bestehen fuer drei Aufgaben:
- `router_prompt` — Domaenen-Erkennung fuer den Router
- `enrich()` — Kontext-Hook fuer den Enricher
- `salienz_prompt` — Salienz-Erweiterung

`plan()` und `execute()` sind fuer migrierte Manager toter Code — der Planner erkennt den Agent und ueberspringt den Manager.

**Ziel:** Wenn alle Manager migriert sind, bekommen Agenten die Selbstbeschreibung (`BaseAgent.router_prompt` etc.) und das Plugin-System wird optional.

---

## 5. Zentrale Architekturprinzipien

### Entscheider/Arbeiter-Trennung
Die Salienz entscheidet *was* gespeichert wird, fuehrt aber *nichts* aus. Sie schreibt `pending_writes`. Der Dispatcher verteilt an die zustaendigen Manager-Plugins. Kein Node hat gleichzeitig Bewertungs- und Schreibverantwortung.

### Trust Boundary
Public-Methoden (Graph-Entry-Points, API-Endpoints) validieren Eingaben. Die Business-Logik in Nodes und Managern arbeitet mit bereits validierten Daten. Gleicher Grundsatz wie im Entwicklerhandbuch — auf Architekturebene angewendet.

### Tri-LLM + Claude API — Spezialisierung statt Generalismus
GPU-Modell (Chat) und zwei CPU-Modelle (Pixie) laufen auf getrennter Hardware. Kein Lock, kein Warten, echte Parallelitaet. Pixie nutzt Qwen3-32B fuer Analyse/Reasoning und Mistral fuer Sprachausgabe — statisches Routing pro Workflow-Schritt. Anthropic Claude API als alternativer Provider fuer den Chat-Graph (Profil `claude` in config.py, Token/Kosten-Logging).

### Plugin-System mit Auto-Discovery
Manager registrieren sich selbst. Jeder Manager beschreibt dem Router, Enricher und der Salienz per Property, was er kann. Neue Faehigkeiten entstehen durch neue Ordner in `plugins/`, nicht durch Aenderungen am Graph.

### Bi-temporales Modell
Nichts wird ueberschrieben. Update = Invalidieren + Neu Anlegen. Die Historie bleibt erhalten. Gilt fuer Fakten und Timeline gleichermassen.

### Soft-Delete ueberall
Nichts wird geloescht. Inaktive Eintraege bleiben erhalten (`aktiv = FALSE`). Partial Indexes sorgen fuer Performance. Speicherplatz ist vernachlaessigbar, Reaktivierung moeglicherweise wertvoll.

### Prompt-Hierarchie: Persoenlichkeit entsteht, sie wird nicht programmiert
Der System-Prompt ist eine Stellenbeschreibung, keine Persoenlichkeit. Er definiert nur die technische Rahmenbedingung: Rolle, Sprache, Grenzen. Alles andere kommt aus dynamischen, gewachsenen Quellen. Die Verhaltensregeln kommen nicht aus einem statischen Prompt — der Nutzer gibt sie. Der Nutzer praegt den Assistenten durch Interaktion, nicht durch Programmierung.

### Berechnung in Python, nicht im LLM
Deterministische Operationen (Decay-Kurven, Emotions-Vektoren, Stilanalyse, Zeitparser) sind Python-Funktionen. Das LLM bekommt nur die Ergebnisse als Klartext. Schneller, exakter, reproduzierbar.

### Session-Kontext in fruehen Nodes
Perzeption und Router bekommen die letzten 5 Session-Turns als Hintergrund-Kontext (Redis-Read, <5ms). Ermoeglicht Pronomen-Aufloesung ("die Liste"), Emotions-Kontinuitaet und Kontext-Routing. Klar abgegrenzt im Prompt: "Analysiere NUR den aktuellen Prompt." Validiert: keine Kontamination bei Themenwechsel. Perzeption ist kontext-*informiert*, aber prompt-*fokussiert*.

---

## 6. Feature-Matrix

| Feature | Status | Referenz |
|---------|--------|----------|
| Graph-Pipeline (HumanGraph, 12 Nodes) | Implementiert & getestet | nova-graph.md, nova-node-*.md |
| Graph-Pipeline (AgentGraph, 3 Nodes) | Implementiert & getestet | nova-graph.md, nova-pixie.md |
| Kurzzeitgedaechtnis (Redis + Vektor) | Implementiert & getestet | nova-mem-kzg.md |
| Langzeitgedaechtnis (PostgreSQL) | Implementiert & getestet | nova-mem-lzg.md |
| Ebbinghaus-Decay + Soft-Delete | Implementiert & getestet | nova-pixie-decay.md |
| Salienz als Entscheider | Implementiert & getestet | nova-node-salience.md |
| Fakten-Pipeline (Typ 1 + 2, bi-temporal) | Implementiert & getestet | nova-mem-knowledge-graph.md |
| Timeline (CRUD + Vektor-Modus) | Implementiert & getestet | nova-agent-timeline.md |
| Zeitparser Vektor-Modus (P8) | Implementiert & getestet | nova-tool-timeparser.md |
| Notizen (Create + Read) | Implementiert & getestet | nova-agent-notes.md |
| Zeitparser (47/47 Tests) | Implementiert & getestet | nova-tool-timeparser.md |
| Knowledge Graph (Entitaeten + Edges) | Implementiert & getestet | nova-mem-knowledge-graph.md |
| Entity Resolution | Implementiert & getestet | nova-pattern-entity-resolution.md |
| Zwei-Call-Promotion | Implementiert & getestet | nova-pixie-promotion.md |
| Emotionale Intelligenz (9 Vektoren, Arousal-Decay, Normalisierung, EI-MIKRO) | Implementiert & validiert | nova-ei.md, nova-node-perception.md |
| Charakter-Profile (5 destilliert, alle im Prompt genutzt) | Implementiert & getestet | nova-ei-character-profiles.md |
| Perzeption-Node | Implementiert & getestet | nova-node-perception.md |
| Pixie (9 Tasks, CPU-Runner) | Implementiert & getestet | nova-pixie.md, nova-pixie.md |
| Shadow Delivery Service | Implementiert & getestet | nova-pixie.md |
| Plugin-System (6 Manager) | Implementiert & getestet | nova-architecture.md |
| LLM-Abstraktionsschicht (Provider, Profile, Anthropic Claude API) | Implementiert | nova-architecture.md |
| Tri-LLM-Architektur (GPU Chat + CPU Analyse + CPU Sprache) | Implementiert | nova-pixie_l_spezialisierung.md |
| Gespraechsvektor-Node (GV1+GV2) | Implementiert | nova-node-gv_k.md |
| CharakterIdentitaetAgent + DirektivenAgent | Implementiert | nova-agent-directives.md |
| Tribunal Score-System (T1, Dual-Score Jurist) | Implementiert | nova-node-tribunal.md |
| Health-Check (5 Dienste + SearXNG) | Implementiert | nova-architecture.md |
| Client: Charakter-Visualisierung (5 Profile, Meister/Nova) | Implementiert | — |
| Client: Emotions-Radar (QPainter, Session + KZG) | Implementiert | — |
| Client: Kompakte KZG/LZG-Listen | Implementiert | — |
| EI-Plausibilitaets-Gate (8 Plutchik-Sektoren) | Implementiert | nova-node-perception.md |
| EI-MIKRO (situative Mikro-Anweisungen) | Implementiert | nova-node-responder.md |
| Arousal-basierter Decay (Emotions-Persistenz) | Implementiert | nova-pixie-decay.md |
| Admin-API (Pixie Pause/Resume/Flush) | Implementiert | nova-architecture.md |
| Sprachadaption (CAT): Feature-Scoring + Profil-Pipeline | Implementiert & validiert | nova-ei-character-profiles.md, nova-ei-language-adaptation.md |
| Novas eigener Charakter-Hash im Responder | Implementiert & validiert | nova-ei-character-profiles.md |
| System-Prompt-Hierarchie (5-Schichten-Modell) | Konzipiert & teilweise implementiert | nova-ei-character-profiles.md |
| Agent-System (Epic 11, 11 Agenten) | Implementiert & validiert | nova-graph.md |
| pg_trgm Fuzzy-Suche (Notizen) | Implementiert | nova-agent-notes_l.md |
| Session-Kontext in Perzeption + Router | Implementiert & validiert | nova-node-perception.md, nova-node-router.md |
| Rueckfrage-Kette (Redis-Pending Resume) | Implementiert & validiert | nova-graph.md |
| Web-Integration (SearXNG + PageFetcher) | Implementiert | Chat 35 |
| TimelineAgent (CRUD + bi-temporal + ZeitVektor) | Implementiert & validiert | nova-agent-timeline.md |
| KZG-Agent (LangGraph-Subgraph, 5 Nodes) | Implementiert & validiert | nova-mem-kzg.md |
| DelegationsAgent (Halluzinations-Ventil) | Implementiert & validiert | nova-pixie-delegation.md |
| RechercheAgent (Pixie Web-Recherche) | Implementiert | nova-pixie-research.md |
| Gespraechsvektor (GV1+GV2: Node, Farbmisch, Entity-Hop) | Implementiert & validiert | nova-node-gv_k.md |
| Session-Kontext-Extraktion (memory/kontext.py) | Implementiert | Chat 35 |
| Auto-Fetch (web_search -> page_fetch automatisch) | Implementiert | Chat 35 |
| Prompt-Schema [BLOCKNAME] auf allen Nodes | Implementiert | nova-pattern-prompt-schema.md |
| Test-Runner (Prompt-Ketten) | Implementiert & getestet | TEST0 |
| EI/Routing in API-Response (12 Felder) | Implementiert & getestet | nova-node-responder.md |
| Kognitive Anreicherung (Epic 8) | Konzipiert | Roadmap Epic 8 |
| Erinnerungsfunktion | Geplant | Roadmap ERN1 |
| Telemetrie | Geplant | Roadmap TEL1 |
| Voice (TTS/STT) | Vision | Roadmap |

---

## 7. Dokumentenverzeichnis

Das Handbuch ist nach Betrachtungstiefen organisiert. Tiefe 0 ist der Einstiegspunkt, jede weitere Tiefe geht ins Detail. **72 Dateien** im Verzeichnis `novaberg/docs/`.

### Tiefe 0 — Projekt

| Dokument | Beschreibung |
|----------|-------------|
| nova-project_k.md | Konzept, Vision, Leitprinzipien, Persoenlichkeit |

### Tiefe 1 — Architektur & Subsysteme

| Dokument | Beschreibung |
|----------|-------------|
| nova-architecture.md | Systemarchitektur, Tech-Stack, Plugin-System (dieses Dokument) |
| nova-graph.md | Graph-Architektur, HumanGraph, AgentGraph, Agent-System, State |
| nova-memory.md | Gedaechtnis-Ueberblick (Session → KZG → LZG → KG) |
| nova-ei.md | Emotionale Intelligenz Ueberblick |
| nova-pixie.md | Pixie-System, Scheduling, Queue/Stack/Delivery |

### Tiefe 2 — Pipeline-Nodes (12)

| Dokument | Beschreibung |
|----------|-------------|
| nova-node-perception.md | Perzeption (Emotion, Arousal, Intent, Plutchik-Oktagon) |
| nova-node-router.md | Router (Routing, Agenten-Delegation) |
| nova-node-enricher.md | Enricher (Kontext, EI-Gate, Charakter-Hash) |
| nova-node-planner.md | Planner (Agent-Loop, Resume-Flow) |
| nova-node-agent-dispatch.md | Agent-Dispatch (Zentraler Entry-Point) |
| nova-node-gv_k.md | Gespraechsvektor (Farbmisch-System, Entity-Hop) |
| nova-node-responder.md | Responder (Antwortgenerierung, EI-MIKRO) |
| nova-node-thinker.md | Thinker (Faktenpruefung, Web-Suche) |
| nova-node-tribunal.md | Tribunal (Drei-Perspektiven-Bewertung, Score-System) |
| nova-node-corrector.md | Corrector (Korrekturschleife) |
| nova-node-salience.md | Salienz (Bewertung, pending_writes, Segmentierung) |
| nova-node-dispatcher.md | Dispatcher (Schreiboperationen verteilen) |

### Tiefe 2 — User-Agenten (4)

| Dokument | Beschreibung |
|----------|-------------|
| nova-agent-notes.md | NotizenAgent (CRUD, pg_trgm-Suche, Domain Language) |
| nova-agent-timeline.md | TimelineAgent (Zeitparser, bi-temporal, ZeitVektor) |
| nova-agent-directives.md | DirektivenAgent (Verhaltensanweisungen, HITL-Gate) |
| nova-agent-character.md | CharakterIdentitaetAgent (Persoenlichkeits-Saatgut) |

### Tiefe 2 — Pixie-Agenten (8)

| Dokument | Beschreibung |
|----------|-------------|
| nova-pixie-kzg.md | KZG-Agent (5-Node-Subgraph, Verdichtung, Aehnlichkeit) |
| nova-pixie-promotion.md | PromotionAgent (Zwei-Call-Promotion, KZG → LZG) |
| nova-pixie-decay.md | DecayAgent (Ebbinghaus-Vergessenskurve) |
| nova-pixie-character-hash.md | CharakterAgent (5-Profil-Destillation, alle im Prompt genutzt) |
| nova-pixie-reminder.md | WiedervorlageAgent (4-Tabellen-Scan, Snooze) |
| nova-pixie-research.md | RechercheAgent (Web-Recherche, Dual-Modell) |
| nova-pixie-delegation.md | DelegationsAgent (Halluzinations-Ventil, Yin-Yang) |
| nova-pixie-deepdive_k.md | VertiefungsAgent (Konzept, nicht implementiert) |

### Tiefe 2 — Gedaechtnis-Module (4)

| Dokument | Beschreibung |
|----------|-------------|
| nova-mem-session.md | Session-Gedaechtnis (Redis, Turn-Formatierung) |
| nova-mem-kzg.md | Kurzzeitgedaechtnis (Redis, TTL, Vektorsuche) |
| nova-mem-lzg.md | Langzeitgedaechtnis (PostgreSQL, Ebbinghaus-Decay) |
| nova-mem-knowledge-graph.md | Knowledge Graph (Entitaeten, Fakten, Entity Resolution) |

### Tiefe 2 — EI-Module (3)

| Dokument | Beschreibung |
|----------|-------------|
| nova-ei-plutchik.md | Plutchik-Emotionsmodell (Oktagon, Normalisierung) |
| nova-ei-character-profiles.md | Charakter-Profile & Hash (5 Dimensionen, alle im Prompt, Pipeline) |
| nova-ei-language-adaptation.md | Sprachadaption (CAT, Feature-Scoring) |

### Tiefe 2 — Kognition (2)

| Dokument | Beschreibung |
|----------|-------------|
| nova-thinking-curiosity_k.md | Neugier (Charakter-Resonanz, intrinsische Motivation, Reflexion) |
| nova-thinking-drive_k.md | Antrieb (Ziele, Motivation, Gravitation, Dual-Emotion) |

### Tiefe 2 — Technik & Tools (3)

| Dokument | Beschreibung |
|----------|-------------|
| nova-tool-timeparser.md | Zeitparser (Fuzzy, Normalisierung, ZeitVektor) |
| nova-tool-web.md | Web-Infrastruktur (SearXNG, PageFetcher) |
| nova-tool-multi-channel.md | Multi-Channel (Telegram Bot, Formatierung) |

### Tiefe 3 — Querschnittsmuster (4)

| Dokument | Beschreibung |
|----------|-------------|
| nova-pattern-crud-hardening.md | CRUD-Haertungs-Pattern (4-Phasen-Transaktion) |
| nova-pattern-domain-language.md | Domain-Language-Normalisierung ([FACHSPRACHE]) |
| nova-pattern-prompt-schema.md | Prompt-Schema [BLOCKNAME] (Konvention) |
| nova-pattern-entity-resolution.md | Entity Resolution (Name-Match, Embedding) |

### Lessons (20)

Lessons leben als `{modul}_l.md` oder `{modul}_l_{thema}.md` neben ihrem Modul-Dokument:

| Dokument | Thema |
|----------|-------|
| nova-graph_l.md | Kontextuelle Kontamination |
| nova-graph_l_kontextualisierung.md | Strukturierte Kontextualisierung |
| nova-graph_l_datentransport.md | Daten vollstaendig transportieren |
| nova-node-thinker_l.md | Suchbegriff-Verzerrung |
| nova-node-salience_l.md | Salienz-Mittlung |
| nova-node-dispatcher_l.md | Doppelspeicherung Salienz + Planner |
| nova-node-responder_l.md | Unsichtbarer Default (System-Prompt) |
| nova-node-router_l.md | "NIEMALS" ist kein Proxy |
| nova-agent-notes_l.md | Namens-Identitaet |
| nova-ei_l.md | Blindflug (EI ohne Sichtbarkeit) |
| nova-ei-plutchik_l.md | Arousal-basierter Decay |
| nova-ei-character-profiles_l.md | Persona-Isolation (Yin-Yang) |
| nova-architecture_l.md | ROCm-Versionsinkompatibilitaet |
| nova-pixie_l_feedback.md | Feedback-Loop Pixie |
| nova-pixie_l_kontamination.md | Session-Kontamination durch Delivery |
| nova-pixie_l_spezialisierung.md | Spezialisierung schlaegt Generalisierung |
| nova-pixie_l_arbeitspaket.md | Enges Arbeitspaket (OpenClaw) |
| nova-tool-timeparser_l_timezone.md | Timezone UTC vs. Lokal |
| nova-tool-timeparser_l_evolution.md | Zeitparser-Evolution |
| nova-tool-timeparser_l_vektor.md | Vektor-Modus Zeitparser |

### Uebergreifend

| Dokument | Beschreibung |
|----------|-------------|
| nova-roadmap.md | Projektchronik (nur abgeschlossene Arbeit) |
| nova-backlog.md | Offene Features, Konzepte, Bugs |
| nova-bugs.md | Bekannte Probleme & Limitationen |

---

## 8. Deployment

### 8.1 Docker Compose

```yaml
services:
  server:
    build: ./server
    ports: ["8000:8000"]
    depends_on: [postgres, redis]
    environment:
      - OLLAMA_GPU_URL=http://host.docker.internal:11434
      - OLLAMA_CPU_URL=http://host.docker.internal:11435
      - POSTGRES_URL=postgresql://ki:***@postgres:5432/gedaechtnis
      - REDIS_URL=redis://redis:6379
      - SEARXNG_URL=http://searxng:8080

  postgres:
    image: pgvector/pgvector:pg16
    volumes:
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis/redis-stack-server:latest
    command: redis-stack-server --appendonly yes --dir /data
    volumes:
      - redisdata:/data

  searxng:
    image: searxng/searxng:latest
    volumes:
      - ./searxng:/etc/searxng:rw
    ports: ["8080:8080"]

  telegram-bot:
    build: ./telegram_bot
    container_name: ki_telegram
    depends_on: [server]
    env_file: .env
    restart: unless-stopped
```

### 8.2 Ollama (Host-native)

Zwei systemd-Services, getrennte Instanzen:

```bash
# GPU-Instanz (Port 11434)
OLLAMA_HOST=0.0.0.0:11434 ollama serve

# CPU-Instanz (Port 11435)
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

Docker-Container erreichen den Host via `host.docker.internal`. Ollama muss explizit auf `0.0.0.0` gebunden werden (systemd-Override), da der Default `127.0.0.1` nur lokalen Zugriff erlaubt.

### 8.3 Startup-Reihenfolge

```
1. systemd -> Ollama GPU (Port 11434)
2. systemd -> Ollama CPU (Port 11435)
3. docker compose up -> postgres, redis, searxng
4. docker compose up -> server
   ├── Lifespan: init_providers() -> LLM-Abstraktion
   ├── Lifespan: Plugin Discovery + Manager Setup
   ├── init.sql -> Schema-Migrationen (idempotent)
   ├── build_human_graph() + build_agent_graph()
   ├── APScheduler -> SchattenArbeit (alle 10 Min)
   └── API bereit auf :8000
5. docker compose up -> telegram-bot (Long Polling, wartet auf server)
6. Client -> PyQt6 App verbindet sich via HTTP + WebSocket
```

### 8.4 Admin-API

Vier Endpoints zur Steuerung des Pixie-Schedulers:

| Endpoint | Methode | Beschreibung |
|----------|---------|-------------|
| `/admin/pixie/pause` | POST | Setzt Redis-Key `pixie:paused` — Runner ueberspringt |
| `/admin/pixie/resume` | POST | Loescht `pixie:paused` — Runner arbeitet wieder |
| `/admin/pixie/status` | GET | Gibt `paused: true/false` zurueck |
| `/admin/pixie/flush` | POST | Fuehrt alle Pixie-Tasks synchron aus bis nichts mehr uebrig ist |

### 8.5 Health-Check

```bash
curl http://localhost:8000/health
```

Prueft 5 Dienste + Pixie-Status:

| Feld | Prueft | Methode |
|------|-------|---------|
| `server` | FastAPI erreichbar | Implizit (Endpoint antwortet) |
| `redis` | Redis-Verbindung | `redis_client.ping()` |
| `postgres` | PostgreSQL + pgvector-Extension + Schema | SQL-Query |
| `ollama` | GPU-Ollama + Modellverfuegbarkeit | `ollama_gpu_client.list()` |
| `searxng` | SearXNG erreichbar | HTTP GET auf `SEARXNG_URL` (Timeout 3s) |
| `shadow` | Pixie-Status (idle/aktiv + Thema) | Redis-Key `shadow_status` |

Client-Statusleiste pollt `/health` alle 5 Sekunden. Zeigt 5 Dienste mit gruen/rot-Indikatoren.

---

## 9. Konfiguration

Alles Konfigurierbare lebt in `config.py`, gelesen aus Umgebungsvariablen mit Defaults:

| Kategorie | Beispiele |
|-----------|-----------|
| Verbindungen | `OLLAMA_GPU_URL`, `OLLAMA_CPU_URL`, `POSTGRES_URL`, `REDIS_URL` |
| Modelle | `OLLAMA_GPU_MODEL`, `OLLAMA_CPU_MODEL`, `EMBED_MODEL` |
| Context | `OLLAMA_GPU_NUM_CTX` (16384), `OLLAMA_CPU_NUM_CTX` (32768) |
| Pixie | `PIXIE_INTERVALL_MIN` (10), `PIXIE_PROMOTION_PRIORITAET` (0.9), `PIXIE_PROMOTION_INTERVALL_SEKUNDEN` (300), `PROMOTION_THRESHOLD` (0.8, in `memory/kzg.py` — Salienz-Schwelle, nicht in config.py) |
| EI | `EMOTION_DECAY_FACTOR` (0.8), `EMOTION_DECAY_BASE` (10) |
| Decay | `EBBINGHAUS_DECAY_RATE` (0.0015), `EBBINGHAUS_MIN_GEWICHT` (0.1) |
| Namen | `ASSISTANT_NAME` ("Nova"), `BACKGROUND_NAME` ("Pixie") |
| Zeitzonen | `TIMEZONE` ("Europe/Berlin") |
| LLM-Profil | `LLM_PROFILE` (lokal), `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` |
| Web-Suche | `SEARXNG_URL` (http://searxng:8080), `SEARXNG_TIMEOUT` (10.0), `SEARXNG_MAX_RESULTS` (10) |

**Keine Magic Numbers im Code.** Alle Schwellwerte, Raten und Gewichtungen sind konfigurierbar.

---

## 10. Datenbankschema

Das Kern-Schema lebt in `db/init.sql`. Manager-spezifische Tabellen bei den Plugins.

| Tabelle | Quelle | Beschreibung |
|---------|--------|-------------|
| `langzeitgedaechtnis` | `db/init.sql` | LZG mit Ebbinghaus-Decay |
| `charakter_hash` | `db/init.sql` | 5 Persoenlichkeitsprofile (kern_hash, adaptive_hash, beziehungsprofil, intentions_profil, emotions_profil), alle im Prompt injiziert (seit Chat 52) |
| `hintergrund_log` | `db/init.sql` | Pixie-Aufgabenprotokoll |
| `gespraech_archiv` | `db/init.sql` | Session-Archivierung |
| `entitaeten` | `db/init.sql` | Knowledge Graph Nodes |
| `fakten` | `db/init.sql` | Knowledge Graph Edges |
| `timeline` | `db/init.sql` | Termine und Ereignisse |
| `notizen` | `db/init.sql` | Merkzettel und Listen |

Alle Migrationen sind idempotent (`IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`). Wiederholtes Ausfuehren von init.sql ist sicher. Manager-spezifische Tabellen liegen bei den Plugins (z.B. `plugins/fakten_manager/init.sql`), das Kern-Schema (LZG, Charakter-Hash, Hintergrund-Log) in `db/init.sql`.

---

*Konsolidiert aus nova-00-a.md, nova-07-a.md, nova-07-m-a.md.*
