# Novaberg — Systemarchitektur

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Systemarchitektur, Tech-Stack, Plugin-System
**Stand:** 21. April 2026, Chat 60 (Event-Modell, Graph-Split, Session-Trennung)
**Pfad:** novaberg/docs/novaberg-architecture.md
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
| Desktop-Client | GTK4 (PyGObject) + WebKitGTK | Chat-UI (WebView), Panel-System (System, Emotionen, KZG, LZG, Session, Charakter), WebSocket (Charakter-Antworten + Shadow Delivery) |

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

**GPU-Idle-Modus (Chat 79):** Bei User-Inaktivitaet > 300s routet `pixie_llm_call` Sprach-Calls (`modus=sprache`) auf den GPU-Provider (`gemma4-gpu`, Port 11434). Analyse-Calls bleiben auf Qwen3-32B-CPU. Vierter Provider `_pixie_idle_provider` wird in `init_providers` gebaut (`None` im Claude-Profil). Modul-Cache `_aktiver_pixie_user` transportiert die User-ID vom Dispatcher zu `pixie_llm_call` ohne Parameter-Welle. Config: `PIXIE_GPU_IDLE`, `PIXIE_IDLE_SCHWELLE_SEKUNDEN`.

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
| `PIXIE_GPU_IDLE` | `True` | Feature-Flag: Sprach-Calls auf GPU bei Inaktivitaet |
| `PIXIE_IDLE_SCHWELLE_SEKUNDEN` | `300` | Sekunden Inaktivitaet bevor GPU-Routing greift |

### 2.8 Bekannter Bug: Ollama think+format (Chat 46)

Ollama Issue #15260: Bei Gemma4 (und Qwen3.5) bricht `think=false` den `format="json"`-Constraint — JSON wird stillschweigend ignoriert.

Workaround: `think=False` immer senden, `format="json"` NICHT senden. JSON-Einhaltung erfolgt ueber Prompt-Overrides (Gemma4-spezifische `[REGELN]`) + Cleanup-Pipeline (`_clean_json_response` + `_deduplicate_repetition` + `_repair_truncated_json`) im `OllamaProvider`.

Status: Ollama-Bug offen (Stand 15.04.2026).

---

## 3. Projektstruktur

```
project/
├── client/
│   ├── main.py                          # GTK4 Application Einstieg
│   └── ui/                              # Chat, Fakten, Gedaechtnis, Timeline, Schatten,
│                                        #   Status, System-Panels, Hauptfenster,
│                                        #   Emotions-Radar (Cairo)
├── server/
│   ├── main.py                          # App-Start, Lifespan, Router-Includes
│   ├── config.py                        # Zentrale Konfiguration, Umgebungsvariablen
│   ├── prompt_loader.py                 # Laedt PROMPTS-Dict (default/ + Connector-Override)
│   │
│   ├── api/                             # REST + WebSocket Endpoints
│   │   ├── chat.py                      #   /chat, /chat/stream (Pfad 1 + Event-Erzeugung)
│   │   ├── health.py                    #   /health (5 Dienste + Pixie), /modelle
│   │   ├── gedaechtnis.py               #   /gedaechtnis/*, /fakten/*, /emotionen/*
│   │   ├── session.py                   #   /session/*
│   │   ├── websocket.py                 #   WebSocket (Charakter-Antwort + Shadow Delivery)
│   │   ├── admin.py                     #   /admin/pixie/{pause,resume,status}
│   │   └── models.py                    #   Pydantic-Modelle
│   │
│   ├── graph/                           # LangGraph Graphen + State (Chat 60: Graph-Split)
│   │   ├── base.py                      #   GraphBase (abstrakt, create_state)
│   │   ├── human_graph.py               #   HumanGraph (Pfad 1, 5 Nodes)
│   │   ├── character_graph.py           #   CharacterGraph (Pfad 2, 14 Nodes, Chat 60/61)
│   │   ├── agent_graph.py               #   AgentGraph (Pixie-Pipeline, 3 Nodes)
│   │   ├── builder.py                   #   Fassade, Plugin-Init
│   │   ├── state.py                     #   State-Definition, PendingWrite
│   │   └── nodes/                       #   13 Node-Dateien, von den drei Graphen geteilt
│   │       ├── perzeption.py            #     → novaberg-node-perception.md (rolle user/assistant)
│   │       ├── enricher.py              #     → novaberg-node-enricher.md
│   │       ├── ei_calc.py               #     → novaberg-node-ei-calc.md (rolle user/character)
│   │       ├── router.py                #     → novaberg-node-router.md
│   │       ├── planner.py               #     → novaberg-node-planner.md
│   │       ├── responder.py             #     → novaberg-node-responder.md
│   │       ├── thinker.py               #     → novaberg-node-thinker.md
│   │       ├── salience.py              #     → novaberg-node-salience.md
│   │       ├── dispatcher.py            #     → novaberg-node-dispatcher.md (zentraler Session-Turn-Schreiber)
│   │       ├── tribunal.py              #     → novaberg-node-tribunal.md
│   │       ├── corrector.py             #     → novaberg-node-corrector.md
│   │       ├── agent_dispatch.py        #     Agent-Dispatch (Epic 11)
│   │       └── gespraechsvektor.py      #     → novaberg-node-gv_k.md
│   │
│   ├── agents/                          # Agent-System (Epic 11 + Epic 5) — 11 Agenten
│   │   ├── __init__.py                  #   AgentRegistry, Auto-Discovery
│   │   ├── base.py                      #   BaseAgent, AgentState, AgentResult, PeriodicTask
│   │   ├── crud_validation.py           #   Gemeinsame CRUD-Haertung (Chat 42)
│   │   ├── notizen/                     #   NotizenAgent (User-Agent, Resume + Bestaetigung)
│   │   ├── timeline/                    #   TimelineAgent (User-Agent, Zeitparser + Resume)
│   │   ├── charakter_identitaet/        #   CharakterIdentitaetAgent (User-Agent, Resume + init.sql)
│   │   ├── direktiven/                  #   DirektivenAgent (User-Agent, HITL-Gate + init.sql)
│   │   ├── kzg/                         #   KZG-Agent (LangGraph-Subgraph, 5 Nodes)
│   │   ├── delegation/                  #   DelegationsAgent (Halluzinations-Ventil, init.sql)
│   │   ├── recherche/                   #   RechercheAgent (Pixie, Web-Recherche)
│   │   ├── promotion/                   #   PromotionAgent (Pixie, KZG -> LZG)
│   │   ├── decay/                       #   DecayAgent (Pixie, Ebbinghaus)
│   │   ├── charakter/                   #   CharakterAgent (Pixie, Hash-Destillation)
│   │   └── wiedervorlage/               #   WiedervorlageAgent (Pixie)
│   │
│   ├── ei/                              # EI-Berechnungsmodul (Chat 58 ausgelagert, Chat 61 Refactor)
│   │   └── berechnung.py                #   Verlauf, Vektor, Nova-Empathie, sin^0.5-Glaettung
│   │
│   ├── tools/                           # Tool-Manager (Epic 11)
│   │   ├── db_manager.py                #   PostgreSQL + Connection Pool
│   │   ├── redis_manager.py             #   Redis (nativ threadsafe)
│   │   ├── embedding_manager.py         #   Ollama Embeddings
│   │   └── web/                         #   Web-Infrastruktur (Chat 35)
│   │       ├── search.py                #     WebSearchManager (SearXNG)
│   │       └── fetch.py                 #     PageFetcher (trafilatura + BS4)
│   │
│   ├── memory/                          # Gedaechtnis-Schicht
│   │   ├── embedding.py                 #   Embedding-Erzeugung (nomic-embed-text)
│   │   ├── kzg.py                       #   Kurzzeitgedaechtnis (Redis, RediSearch-Index)
│   │   ├── lzg.py                       #   Langzeitgedaechtnis (PostgreSQL, Ebbinghaus)
│   │   ├── charakter.py                 #   Charakter-Hash (Read)
│   │   ├── session.py                   #   Session (_session_key mit character_id, Chat 60)
│   │   ├── kontext.py                   #   Session-Kontext-Extraktion (LLM-gestuetzt)
│   │   ├── repositories/                #   Daten-Repositories (CRUD gegen PostgreSQL)
│   │   │   ├── entitaeten_repository.py #     Knowledge Graph Nodes
│   │   │   ├── fakten_repository.py     #     Knowledge Graph Edges (bi-temporal)
│   │   │   ├── timeline_repository.py   #     Termine und Ereignisse
│   │   │   └── notizen_repository.py    #     Merkzettel und Listen
│   │   └── services/
│   │       └── entity_resolution.py     #   Entity Resolution (Name + Fuzzy + Embedding)
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
│   │   ├── charakter_identitaet_manager/#   Charakter-Identitaet (Router-Prompt)
│   │   └── direktiven_manager/          #   Direktiven (Router-Prompt)
│   │
│   └── services/                        # Dienste
│       ├── llm_provider.py              #   LLM-Provider-Abstraktion (Ollama + Anthropic)
│       ├── events.py                    #   Event-Queue (Redis FIFO, Self-Trigger-Schutz, Chat 60)
│       ├── event_consumer.py            #   Event-Consumer (async-Loop, WebSocket-Delivery, Chat 60)
│       ├── shadow_delivery.py           #   Pixie -> Chat-Einspeisung
│       ├── shadow_agent/                #   Alter Pixie-Runner (extern aufruflos, PIX-CLEAN)
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

### Event-Modell (Chat 60)

Seit Chat 60 sind User und Charakter zwei unabhängige Akteure:

| Pfad | Graph | Nodes | Aufgabe |
|------|-------|-------|---------|
| Pfad 1 | HumanGraph | 5 | User schreibt: Wahrnehmung + Speicherung |
| Pfad 2 | CharacterGraph | 14 | Charakter reagiert: Lesen + Entscheiden + Antworten + Perzeption(Nova) + Speichern |

Verbunden durch eine Redis-Event-Queue (`event_queue:{user_id}:{character_id}`). Ein Event-Consumer (`services/event_consumer.py`) pollt die Queue und startet CharacterGraph-Durchlaeufe. Antworten erreichen den Client per WebSocket.

**Neue Services:**

| Service | Datei | Aufgabe |
|---------|-------|---------|
| Event-Queue | `services/events.py` | Event erzeugen, lesen, Self-Trigger-Schutz |
| Event-Consumer | `services/event_consumer.py` | Queue-Polling, Debouncing, Graph-Aufruf, WebSocket-Delivery |

**Ersetzte Services:**

| Service | Status | Ersetzt durch |
|---------|--------|---------------|
| Nachbearbeitung | Deprecated | Event-Consumer |
| SSE-Streaming (Antwort) | Deprecated | WebSocket-Delivery |

Session-Key seit Chat 60: `session:{user_id}:{character_id}:turns` (vorher: `session:{user_id}:turns`).

→ Details: `novaberg-graph.md` §3, `novaberg-convention-event-model.md`

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
| `setup(postgres_url, redis_client=None)` | — | Schema anlegen (`init.sql` ausfuehren), optional Redis-Init | GraphBase beim Start |

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

Seit Epic 11 ergaenzen Agenten die Manager schrittweise — sie ersetzen sie nicht vollstaendig:

| Manager | Agent | Status |
|---------|-------|--------|
| NotizenManager | NotizenAgent | Agent bedient `/notizen/*`-Dispatches; Manager liefert `router_prompt`, `enrich()`, und traegt weiterhin seine eigenen `plan()`/`execute()`-Pfade |
| TimelineManager | TimelineAgent | Agent bedient `/timeline/*`-Dispatches; Manager liefert `router_prompt`, `enrich()`, `plan()` (Zeitparser + Entity Resolution) und `execute()` |
| FaktenManager | — | Kein Agent. Manager traegt vollstaendiges `execute()` (CRUD + Entity Resolution, bi-temporal) |
| KzgManager | — | Kein Agent (KZG-Schreiben geht ueber den KZG-*Subgraph-Agent*, nicht den Manager). Manager traegt nur `execute()` als Legacy-Fallback |

Die Manager bleiben **nicht** leere Huellen. Sie halten drei Aufgaben fuer Router/Enricher/Salienz und zusaetzlich ihre eigentliche Domain-Logik (LLM-Extraction, Zeitparser, Entity Resolution) in `plan()` und `execute()`. Diese Methoden werden weiter aktiv benutzt:

- `router_prompt` — Domaenen-Erkennung fuer den Router
- `enrich()` — Kontext-Hook fuer den Enricher
- `salienz_prompt` — Salienz-Erweiterung
- `plan()` — vom Planner aufgerufen, wenn kein Agent die Domaene uebernimmt (aktueller Stand: bei FaktenManager und KzgManager). Fuer NotizenManager und TimelineManager ist der Code vorhanden, wird aber vom Planner uebersprungen, sobald ein passender Agent gefunden ist.
- `execute()` — vom Dispatcher aufgerufen, wenn `pending_writes` ein Manager-Ziel (`fakten`, `kzg`, `timeline`, `notizen`) treffen. Der Agent-Pfad erzeugt `pending_writes` nur fuer `kzg`; alle anderen Ziele gehen weiter ueber den Manager-`execute()`.

**Ziel langfristig:** Wenn alle Domains einen Agenten haben, koennen Agenten die Selbstbeschreibung (`BaseAgent.router_prompt` etc.) selbst tragen, und das Plugin-System wird optional. Aktuell sind Plugin-Manager und Agent-System parallele Saeulen, die sich ergaenzen, nicht zwei Schichten, die sich ersetzen.

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
| Graph-Pipeline (HumanGraph: 5 Nodes Pfad 1 | CharacterGraph: 14 Nodes Pfad 2 | AgentGraph: 3 Nodes) | Implementiert & getestet | novaberg-graph.md, novaberg-node-*.md |
| Async-Block (Salienz + Dispatcher + Nova-Pfad) | Implementiert & validiert | novaberg-service-nachbearbeitung.md |
| EI-Calc-Node (reine Python-Berechnung, Dual-Modus User + Nova) | Implementiert & validiert | novaberg-node-ei-calc.md |
| Dual-Emotion Phase 2 (Nova-Empathie, Konflikt-Erkennung) | Implementiert (AP1–3, AP7, AP4 teilw., AP8 teilw.) | novaberg-ei-dual-emotion_k.md |
| Graph-Pipeline (AgentGraph, 3 Nodes) | Implementiert & getestet | novaberg-graph.md, novaberg-pixie.md |
| Kurzzeitgedaechtnis (Redis + Vektor) | Implementiert & getestet | novaberg-mem-kzg.md |
| Langzeitgedaechtnis (PostgreSQL) | Implementiert & getestet | novaberg-mem-lzg.md |
| Ebbinghaus-Decay + Soft-Delete | Implementiert & getestet | novaberg-pixie-decay.md |
| Salienz als Entscheider | Implementiert & getestet | novaberg-node-salience.md |
| Fakten-Pipeline (Typ 1 + 2, bi-temporal) | Implementiert & getestet | novaberg-mem-knowledge-graph.md |
| Timeline (CRUD + Vektor-Modus) | Implementiert & getestet | novaberg-agent-timeline.md |
| Zeitparser Vektor-Modus (P8) | Implementiert & getestet | novaberg-tool-timeparser.md |
| Notizen (Create + Read) | Implementiert & getestet | novaberg-agent-notes.md |
| Zeitparser (47/47 Tests) | Implementiert & getestet | novaberg-tool-timeparser.md |
| Knowledge Graph (Entitaeten + Edges) | Implementiert & getestet | novaberg-mem-knowledge-graph.md |
| Entity Resolution | Implementiert & getestet | novaberg-pattern-entity-resolution.md |
| Zwei-Call-Promotion | Implementiert & getestet | novaberg-pixie-promotion.md |
| Emotionale Intelligenz (9 Vektoren, Arousal-Decay, Normalisierung, EI-MIKRO) | Implementiert & validiert | novaberg-ei.md, novaberg-node-perception.md |
| Charakter-Profile (5 destilliert, alle im Prompt genutzt) | Implementiert & getestet | novaberg-ei-character-profiles.md |
| Perzeption-Node | Implementiert & getestet | novaberg-node-perception.md |
| Pixie (9 Tasks, CPU-Runner) | Implementiert & getestet | novaberg-pixie.md, novaberg-pixie.md |
| Shadow Delivery Service | Implementiert & getestet | novaberg-pixie.md |
| Plugin-System (6 Manager) | Implementiert & getestet | novaberg-architecture.md |
| LLM-Abstraktionsschicht (Provider, Profile, Anthropic Claude API) | Implementiert | novaberg-architecture.md |
| Tri-LLM-Architektur (GPU Chat + CPU Analyse + CPU Sprache) | Implementiert | novaberg-pixie_l_spezialisierung.md |
| Gespraechsvektor-Node (GV1+GV2) | Implementiert | novaberg-node-gv_k.md |
| CharakterIdentitaetAgent + DirektivenAgent | Implementiert | novaberg-agent-directives.md |
| Tribunal Score-System (T1, Dual-Score Jurist) | Implementiert | novaberg-node-tribunal.md |
| Health-Check (5 Dienste + SearXNG) | Implementiert | novaberg-architecture.md |
| Client: Charakter-Visualisierung (5 Profile, Meister/Nova) | Implementiert | — |
| Client: Emotions-Radar (QPainter, Session + KZG) | Implementiert | — |
| Client: Kompakte KZG/LZG-Listen | Implementiert | — |
| EI-Plausibilitaets-Gate (8 Plutchik-Sektoren) | Implementiert | novaberg-node-perception.md |
| EI-MIKRO (situative Mikro-Anweisungen) | Implementiert | novaberg-node-responder.md |
| Arousal-basierter Decay (Emotions-Persistenz) | Implementiert | novaberg-pixie-decay.md |
| Admin-API (Pixie Pause/Resume/Flush) | Implementiert | novaberg-architecture.md |
| Sprachadaption (CAT): Feature-Scoring + Profil-Pipeline | Implementiert & validiert | novaberg-ei-character-profiles.md, novaberg-ei-language-adaptation.md |
| Novas eigener Charakter-Hash im Responder | Implementiert & validiert | novaberg-ei-character-profiles.md |
| System-Prompt-Hierarchie (5-Schichten-Modell) | Konzipiert & teilweise implementiert | novaberg-ei-character-profiles.md |
| Agent-System (Epic 11, 11 Agenten) | Implementiert & validiert | novaberg-graph.md |
| pg_trgm Fuzzy-Suche (Notizen) | Implementiert | novaberg-agent-notes_l.md |
| Session-Kontext in Perzeption + Router | Implementiert & validiert | novaberg-node-perception.md, novaberg-node-router.md |
| Rueckfrage-Kette (Redis-Pending Resume) | Implementiert & validiert | novaberg-graph.md |
| Web-Integration (SearXNG + PageFetcher) | Implementiert | Chat 35 |
| TimelineAgent (CRUD + bi-temporal + ZeitVektor) | Implementiert & validiert | novaberg-agent-timeline.md |
| KZG-Agent (LangGraph-Subgraph, 5 Nodes) | Implementiert & validiert | novaberg-mem-kzg.md |
| DelegationsAgent (Halluzinations-Ventil) | Implementiert & validiert | novaberg-pixie-delegation.md |
| RechercheAgent (Pixie Web-Recherche) | Implementiert | novaberg-pixie-research.md |
| Gespraechsvektor (GV1+GV2: Node, Farbmisch, Entity-Hop) | Implementiert & validiert | novaberg-node-gv_k.md |
| Session-Kontext-Extraktion (memory/kontext.py) | Implementiert | Chat 35 |
| Auto-Fetch (web_search -> page_fetch automatisch) | Implementiert | Chat 35 |
| Prompt-Schema [BLOCKNAME] auf allen Nodes | Implementiert | novaberg-pattern-prompt-schema.md |
| Test-Runner (Prompt-Ketten) | Implementiert & getestet | TEST0 |
| EI/Routing in API-Response (12 Felder) | Implementiert & getestet | novaberg-node-responder.md |
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
| novaberg-project_k.md | Konzept, Vision, Leitprinzipien, Persoenlichkeit |

### Tiefe 1 — Architektur & Subsysteme

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-architecture.md | Systemarchitektur, Tech-Stack, Plugin-System (dieses Dokument) |
| novaberg-graph.md | Graph-Architektur, HumanGraph, AgentGraph, Agent-System, State |
| novaberg-memory.md | Gedaechtnis-Ueberblick (Session → KZG → LZG → KG) |
| novaberg-ei.md | Emotionale Intelligenz Ueberblick |
| novaberg-pixie.md | Pixie-System, Scheduling, Queue/Stack/Delivery |

### Tiefe 2 — Pipeline-Nodes (13)

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-node-perception.md | Perzeption (Emotion, Arousal, Intent, Plutchik-Oktagon, Dual-Modus User/Nova) |
| novaberg-node-enricher.md | Enricher (Kontext-Laden, Plugin-Hooks, reines I/O) |
| novaberg-node-ei-calc.md | EI-Calc (Python-Berechnung: Verlauf, Vektor, Nova-Empathie, kein LLM) |
| novaberg-node-router.md | Router (Routing, Agenten-Delegation) |
| novaberg-node-planner.md | Planner (Agent-Loop, Resume-Flow) |
| novaberg-node-agent-dispatch.md | Agent-Dispatch (Zentraler Entry-Point) |
| novaberg-node-gv_k.md | Gespraechsvektor (Farbmisch-System, Entity-Hop) |
| novaberg-node-responder.md | Responder (Antwortgenerierung, EI-MIKRO) |
| novaberg-node-thinker.md | Thinker (Faktenpruefung, Web-Suche) |
| novaberg-node-tribunal.md | Tribunal (Drei-Perspektiven-Bewertung, Score-System) |
| novaberg-node-corrector.md | Corrector (Korrekturschleife) |
| novaberg-node-salience.md | Salienz (Bewertung, pending_writes — asynchron seit Chat 59) |
| novaberg-node-dispatcher.md | Dispatcher (Schreiboperationen verteilen — asynchron seit Chat 59) |
| novaberg-service-nachbearbeitung.md | Async-Service (User-Pfad + Nova-Pfad parallel nach Antwort-Auslieferung) |

### Tiefe 2 — User-Agenten (4)

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-agent-notes.md | NotizenAgent (CRUD, pg_trgm-Suche, Domain Language) |
| novaberg-agent-timeline.md | TimelineAgent (Zeitparser, bi-temporal, ZeitVektor) |
| novaberg-agent-directives.md | DirektivenAgent (Verhaltensanweisungen, HITL-Gate) |
| novaberg-agent-character.md | CharakterIdentitaetAgent (Persoenlichkeits-Saatgut) |

### Tiefe 2 — Pixie-Agenten (8)

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-pixie-kzg.md | KZG-Agent (5-Node-Subgraph, Verdichtung, Aehnlichkeit) |
| novaberg-pixie-promotion.md | PromotionAgent (Zwei-Call-Promotion, KZG → LZG) |
| novaberg-pixie-decay.md | DecayAgent (Ebbinghaus-Vergessenskurve) |
| novaberg-pixie-character-hash.md | CharakterAgent (5-Profil-Destillation, alle im Prompt genutzt) |
| novaberg-pixie-reminder.md | WiedervorlageAgent (4-Tabellen-Scan, Snooze) |
| novaberg-pixie-research.md | RechercheAgent (Web-Recherche, Dual-Modell) |
| novaberg-pixie-delegation.md | DelegationsAgent (Halluzinations-Ventil, Yin-Yang) |
| novaberg-pixie-deepdive_k.md | VertiefungsAgent (Konzept, nicht implementiert) |

### Tiefe 2 — Gedaechtnis-Module (4)

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-mem-session.md | Session-Gedaechtnis (Redis, Turn-Formatierung) |
| novaberg-mem-kzg.md | Kurzzeitgedaechtnis (Redis, TTL, Vektorsuche) |
| novaberg-mem-lzg.md | Langzeitgedaechtnis (PostgreSQL, Ebbinghaus-Decay) |
| novaberg-mem-knowledge-graph.md | Knowledge Graph (Entitaeten, Fakten, Entity Resolution) |

### Tiefe 2 — EI-Module (3)

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-ei-plutchik.md | Plutchik-Emotionsmodell (Oktagon, Normalisierung) |
| novaberg-ei-character-profiles.md | Charakter-Profile & Hash (5 Dimensionen, alle im Prompt, Pipeline) |
| novaberg-ei-language-adaptation.md | Sprachadaption (CAT, Feature-Scoring) |

### Tiefe 2 — Kognition (2)

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-thinking-curiosity_k.md | Neugier (Charakter-Resonanz, intrinsische Motivation, Reflexion) |
| novaberg-thinking-drive_k.md | Antrieb (Ziele, Motivation, Gravitation, Dual-Emotion) |

### Tiefe 2 — Technik & Tools (3)

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-tool-timeparser.md | Zeitparser (Fuzzy, Normalisierung, ZeitVektor) |
| novaberg-tool-web.md | Web-Infrastruktur (SearXNG, PageFetcher) |
| novaberg-tool-multi-channel.md | Multi-Channel (Telegram Bot, Formatierung) |

### Tiefe 3 — Querschnittsmuster (4)

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-pattern-crud-hardening.md | CRUD-Haertungs-Pattern (4-Phasen-Transaktion) |
| novaberg-pattern-domain-language.md | Domain-Language-Normalisierung ([FACHSPRACHE]) |
| novaberg-pattern-prompt-schema.md | Prompt-Schema [BLOCKNAME] (Konvention) |
| novaberg-pattern-entity-resolution.md | Entity Resolution (Name-Match, Embedding) |

### Lessons (20)

Lessons leben als `{modul}_l.md` oder `{modul}_l_{thema}.md` neben ihrem Modul-Dokument:

| Dokument | Thema |
|----------|-------|
| novaberg-graph_l.md | Kontextuelle Kontamination |
| novaberg-graph_l_kontextualisierung.md | Strukturierte Kontextualisierung |
| novaberg-graph_l_datentransport.md | Daten vollstaendig transportieren |
| novaberg-node-thinker_l.md | Suchbegriff-Verzerrung |
| novaberg-node-salience_l.md | Salienz-Mittlung |
| novaberg-node-dispatcher_l.md | Doppelspeicherung Salienz + Planner |
| novaberg-node-responder_l.md | Unsichtbarer Default (System-Prompt) |
| novaberg-node-router_l.md | "NIEMALS" ist kein Proxy |
| novaberg-agent-notes_l.md | Namens-Identitaet |
| novaberg-ei_l.md | Blindflug (EI ohne Sichtbarkeit) |
| novaberg-ei-plutchik_l.md | Arousal-basierter Decay |
| novaberg-ei-character-profiles_l.md | Persona-Isolation (Yin-Yang) |
| novaberg-architecture_l.md | ROCm-Versionsinkompatibilitaet |
| novaberg-pixie_l_feedback.md | Feedback-Loop Pixie |
| novaberg-pixie_l_kontamination.md | Session-Kontamination durch Delivery |
| novaberg-pixie_l_spezialisierung.md | Spezialisierung schlaegt Generalisierung |
| novaberg-pixie_l_arbeitspaket.md | Enges Arbeitspaket (OpenClaw) |
| novaberg-tool-timeparser_l_timezone.md | Timezone UTC vs. Lokal |
| novaberg-tool-timeparser_l_evolution.md | Zeitparser-Evolution |
| novaberg-tool-timeparser_l_vektor.md | Vektor-Modus Zeitparser |

### Uebergreifend

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-roadmap.md | Projektchronik (nur abgeschlossene Arbeit) |
| novaberg-backlog.md | Offene Features, Konzepte, Bugs |
| novaberg-bugs.md | Bekannte Probleme & Limitationen |

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
6. Client -> GTK4 App verbindet sich via SSE + WebSocket
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
