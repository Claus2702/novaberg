# Novaberg — Systemarchitektur

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Systemarchitektur, Tech-Stack, Plugin-System
**Stand:** 28. August 2026 (`memory/kurzziel.py` im Baum — Scheibe 2; `memory/sachlage_history.py` im Baum, `sachlage_verlauf` und `shadow_auftrag.ausloeser_turn_id` in der Tabellenliste — Scheibe 4 des Lage-Konzepts). Davor: 25. August 2026, 20:10 UTC (das Backlog ist nach Gegenstand geteilt — sechs Kategoriedateien, die Rangordnung eigens, das Findemittel darueber; alle im Dokumenten-Index §7). Davor, 12:00 UTC: die Chronik ist nach Monaten geteilt — `novaberg-roadmap.md` traegt den laufenden Zeitraum, vier `novaberg-roadmap-2026-*.md` die abgeschlossenen, und `novaberg-roadmap-index.md` spannt als erzeugtes Findemittel darueber; alle im Dokumenten-Index §7). Davor: das Bugregister ist geteilt — `novaberg-bugs-archiv.md` neu im Dokumenten-Index §7, `novaberg-bugs.md` traegt nur noch die nicht abgeschlossenen Eintraege). Davor: 24. August 2026 (Telegram-Kanal abgeschaltet — Dienstetabelle §1.2, Compose-Auszug §8.1, Startreihenfolge §8.3). Davor: 23. August 2026 (`shadow_auftrag.grund` in der Tabellenliste; davor am selben Tag: Prompt-Segregation dreistufig — `default` → `{modell}` → `{connector}`; `utils/etikett.py` und der `tools/dateien/`-Baum berichtigt; Connector-Tabelle um `qwen36` ergaenzt; *0 hardcoded Prompts* gegen 33 gemessene Literale widerlegt). Davor: 19. August 2026 (`agents/wissen/` — die Bibliothek als **bestellbarer** Dienst: Aushang in `plugins/wissen_manager/`, vier Ausgaenge, und die Abfrage liegt geteilt im Repository, weil Quelle und Zettel denselben Bestand lesen. **Der Manager fehlt weiterhin in der Plugin-Tabelle unten** — der Bestandsbefund von §5 ist damit aelter geworden, nicht erledigt; davor 18. August 2026 (`agents/wissen_rueckweg/` — der Rueckweg vom Gespraech in die Wissensdatei, ausgeloest von der Promotion; dazu `agents/dateien/` **vollstaendig** — Suche, Zoom und der Aufrufer (Aushang in `plugins/dateien_manager/`, Klassifikation, Dispatch, Auskunft); davor am selben Tag ohne Aufrufer; dazu `agents/dateien_index/aufzeichnungen.py`; die Zaehlaussage „sechste Kontextquelle“ bei `autonomous_wissen` um den Dateien-Index ergaenzt — eine weitere Quelle des Enrichers, die ausdruecklich **kein** Plugin ist); davor 16. August 2026 (gegen den Code geprüft: die Modelle kommen aus der **Connector-Tabelle**, nicht aus `OLLAMA_GPU_MODEL`/`OLLAMA_CPU_MODEL`; der Baum unter `memory/` nannte `embedding.py` und `lzg.py`, die es beide nicht gibt — §2.5 und §4 nachgezogen); davor 15. August 2026 (`services/pixie/riegel.py` und `memory/haltung.py` im Baum, `shadow_auftrag.arousal` in der Tabellenliste); davor 8. August 2026 (`novaberg-graph-rechenkette.md` im Dokumenten-Index Tiefe 1 ergänzt — das Register der 34 Rechensysteme des Charakter-Pfads, zerlegt entlang der Rechnungen statt entlang der Knoten. Zuvor: 31. Juli 2026, abends — `graph/nodes/haltung.py` im Verzeichnisbaum ergänzt, Knotenzahlen des CharacterGraph und des Node-Verzeichnisses neu gezählt — beide standen älter als der Verfasser da. Zuvor: `ei/haltung.py` im Verzeichnisbaum ergänzt und der Eintrag zum Haltungsraum im Dokumenten-Index auf das Beitragsmodell umgestellt — die Rechnung ist gebaut, der Knoten fehlt. Zuvor: `novaberg-node-verfasser_k.md` im Dokumenten-Index ergänzt — Konzept, nicht gebaut. Zuvor: `ruff-hart.toml` im Verzeichnisbaum ergänzt, §3 — die harte Teilmenge ohne geduldeten Bestand. Zuvor: `ruff.toml` im Verzeichnisbaum ergänzt, §3. Zuvor: Verzeichnisbaum nachgezogen — `ei/` vollständig, vier fehlende Agenten ergänzt. Kern: Chat 94, Microservice-Welle Block 2+3; Embedding-Modellwechsel Chat 107, §2.4)
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
| ~~**telegram-bot**~~ | Python, Long Polling | — | **abgeschaltet am 24.08.2026** — von Matrix abgeloest; Behaelter entfernt, Compose-Block genommen. `telegram_bot/` liegt weiter im Repositorium. **Die Zeilen fuer `synapse` und `matrix-bot` fehlen in dieser Tabelle** (Fundliste 24.08.2026) |

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
| Nomic Embed Text v2 MoE | `nomic-embed-text-v2-moe` | VRAM | 512 (Modell-Limit) | ~1.0 GB (netto +351 MB ggü. v1) | Embedding-Erzeugung (seit 12.07.2026; v1 war casing-blind, siehe §2.4) |
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
| `qwen36` | `gemma4-gpu` | `qwen36-cpu` | `qwen36-cpu` | 32768 |

> **`qwen36` teilt sich sein GPU-Modell mit `gemma4`** — die Zeile fehlte hier bis zum 23.08.2026, und genau an ihr wäre die Modellteilung ablesbar gewesen, die `OVERRIDE-NACH-CONNECTOR-STATT-MODELL` verursacht hat. Er ist seit dem 24.05.2026 der aktive Connector.

### 2.1.2 Prompt-Segregation (Chat 46-47)

Statische Prompt-Bloecke sind aus den Node-Dateien in Textdateien extrahiert. Verzeichnisstruktur:

```
server/prompts/
  default/     — 91 Bloecke (alle Nodes)
  gemma4-gpu/  — 7 Overrides (JSON-Regeln, Tribunal-Prompts)
```

**Drei Ebenen, seit dem 23.08.2026:** `prompt_loader.py` liest beim Start `default/`, dann `{gpu_model}/`, dann `{connector}/` — jede spaetere ueberschreibt. Dictionary auf `PROMPTS` in `config.py`; Nodes greifen ueber `PROMPTS["node.block"]` zu.

**Die mittlere Ebene ist der Gespraechspfad.** Er haengt am GPU-Modell, nicht am Connector, und zwei der drei Connectoren fahren dort dasselbe (`gemma4` und `qwen36` beide `gemma4-gpu`). Bis zum Umbau lagen die sieben Overrides deshalb unter dem aktiven Connector `qwen36` still, waehrend Gemma4 antwortete — `OVERRIDE-NACH-CONNECTOR-STATT-MODELL`. Der Connector bleibt die **letzte** Ebene, weil er der engere Schluessel ist; fuer Hintergrund-Bloecke ist er die richtige, dort unterscheiden sich die Connectoren wirklich.

**Ein Verzeichnis `mistral/` hat es nie gegeben** — die Zeile stand hier, weil sie erwartet wurde. Erreichbar ist heute jeder Name aus `default`, den drei Connectoren und ihren Modellen; ein Zeuge haelt das fest (`test_jedes_verzeichnis_ist_erreichbar`).

Namenskonvention: `{node}.{block}.txt` — Beispiel: `router.identity.txt`, `salienz.rules.txt`, `tribunal_jurist.system.txt`.

Die Prompts der **Graph-Knoten** sind aus dem Python-Code extrahiert (Chat 46: Perzeption, Router, Salienz, Tribunal; Chat 47: Responder, Thinker, Corrector, GV, KZG-Verdichtung, 4x Classify-Nodes). ~~0 hardcoded Prompts in Python.~~ → **Am 23.08.2026 gemessen und widerlegt: 33 Prompt-Literale ab 100 Zeichen im Produktivcode**, davon 17 mit der `[BLOCKNAME]`-Konvention — Schwerpunkte `agents/charakter/destillation.py` (9), `agents/recherche/` (7), `memory/kontext.py` (einer mit 1714 Zeichen). Die Aussage galt fuer die Graph-Knoten und ist mit den Agenten-Diensten unwahr geworden; die Fundliste traegt es. Konvention: Alle PROMPTS[]-Zugriffe durch `.format()`, literale Klammern in LLM-Beispielen als `{{ }}` escaped.

### 2.2 Provider-Architektur

Seit der Microservice-Welle (Chat 92-94) laufen alle Modell-Aufrufe über eine
Worker-Schicht (`services/model_services/`). Konsumenten rufen nicht mehr Provider
direkt, sondern reichen typisierte Requests an einen der drei Worker — `submit(...)`
async aus dem Haupt-Loop, `submit_sync(...)` aus Worker-Threads (CharacterGraph via
`asyncio.to_thread`). Jeder Worker besitzt eine FIFO-Queue (`worker_base.py`).

```
Producers ──submit / submit_sync──▶  model_service.{ embed | chat | background }
                                          │           │            │
                                          ▼           ▼            ▼
                                     EmbedWorker  ChatWorker  BackgroundWorker
                                     (GPU fix)    (1 Backend)  (analyse + sprache)
                                          │           │            │
                                          └───────────┴────────────┘
                                                       │
                                              _build_backend(kind)
                                          kind ← MODEL_WORKER_BACKENDS (Config)
                                                       │
                  ┌────────────────────────────────────┼──────────────────────────┐
                  ▼                                    ▼                          ▼
          ollama_gpu_client                    ollama_cpu_client          AnthropicProvider
          (OLLAMA_MODEL)            (PIXIE_ANALYSE_MODEL / SHADOW_MODEL)  (ANTHROPIC_MODEL)
```

Backend-Wahl pro Worker ist config-gesteuert (`MODEL_WORKER_BACKENDS`), nicht
hartverdrahtet: `ChatWorker` ist single-backend, `BackgroundWorker` dual-backend
(`analyse` für Reasoning/JSON, `sprache` für Fliesstext), `EmbedWorker` fest auf GPU.
Der JSON-Workaround (Ollama #15260) ist im Worker konzentriert: `expect_json` →
`parse_json_strict` (`services/postprocess.py`), kein `format="json"` an Ollama.

### 2.3 Klassen

| Klasse | Beschreibung |
|--------|-------------|
| `LLMProvider` (ABC) | Abstrakte Basisklasse mit `chat()` (die `generate()`-Methode wurde in der MS-Welle entfernt — alle Pfade nutzen `chat`) |
| `OllamaProvider` | Wrapper um `ollama.Client` — kapselt model, num_ctx, options. `think=False` nativ. |
| `AnthropicProvider` | Wrapper um `anthropic.Anthropic` — Token-Logging mit Kosten, `[AUSGABEFORMAT]`-Block provider-intern, `top_p`-Ignorierung (Anthropic erlaubt nicht `temperature` + `top_p` gleichzeitig). |

### 2.4 Embedding

Embedding (`nomic-embed-text-v2-moe` seit 12.07.2026) ist bewusst **nicht** Teil der Backend-Wahl. Es läuft fest auf GPU über den `EmbedWorker` (Rolle `embed`, siehe §2.7). Grund: Vektorkonsistenz — ein Wechsel des Embedding-Modells invalidiert alle gespeicherten Vektoren, daher kein Config-Hook.

**Modellwechsel Chat 107 (EMBEDDING-CASING-BLIND):** `nomic-embed-text` v1 war durch einen GGUF-Konvertierungsfehler casing-blind (Großbuchstaben-Wörter kollabierten zu `[UNK]`-Skeletten; `embed("Hund") == embed("Katze")` bit-identisch). Der Wechsel auf v2-moe erforderte genau das, wovor dieser Absatz immer gewarnt hat: Re-Embedding des gesamten Bestands bei gestopptem Server, plus Gewichts-Reset und Kanten-Rebuild (Befund: `novaberg-embedding-casing-blind_k.md`).

⚠ **`EMBED_MODEL` steht an DREI Orten** — wer nur einen ändert, tauscht das Modell nicht:

| Ort | Rolle |
|---|---|
| `~/ki-assistent/docker-compose.yml` | **WIRKSAM** — Env schlägt Config-Default. Liegt **außerhalb** dieses Repos! |
| `novaberg/docker-compose.template.yml` | Vorlage, muss mitgezogen werden |
| `novaberg/server/config.py` | nur der Default (`os.getenv`-Fallback) |

### 2.5 Konfigurationsvariablen (LLM)

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| `OLLAMA_CONNECTOR` | `"gemma4"` | Aktiver Modell-Connector (`gemma4` oder `mistral`) — bestimmt die geladenen Ollama-Modelle |
| `PIXIE_ANALYSE_MODEL` | aus Connector (`qwen3-32b-cpu`) | Pixie Analyse-Modell (Backend `ollama_cpu_analyse`) |
| `SHADOW_MODEL` | aus Connector (`gemma4-cpu`) | Pixie Sprach-Modell (Backend `ollama_cpu_sprache`) |
| `WORKER_BACKEND_CHAT` | `"ollama_gpu"` | Backend des ChatWorker (siehe §2.7) |
| `WORKER_BACKEND_BG_ANALYSE` | `"ollama_cpu_analyse"` | Analyse-Backend des BackgroundWorker |
| `WORKER_BACKEND_BG_SPRACHE` | `"ollama_cpu_sprache"` | Sprach-Backend des BackgroundWorker |
| `LLM_PROFILE` | `"lokal"` | Nur noch Schalter für den ThinkingNormalizer: bei `!= "lokal"` läuft dieser als No-Op (kein Ollama-`<think>`-Split nötig). Die alte globale Profil-Umschaltung ist durch `WORKER_BACKEND_*` ersetzt. |
| `ANTHROPIC_API_KEY` | `""` | API-Key für Claude (aus `.env`) |
| `ANTHROPIC_MODEL` | `"claude-sonnet-4-6"` | Claude-Modell (Backend `anthropic`) |

### 2.6 Bekannter Bug: Ollama think+format (Chat 46)

Ollama Issue #15260: Bei Gemma4 (und Qwen 3.6) bricht `think=false` den `format="json"`-Constraint — JSON wird stillschweigend ignoriert.

Workaround: `think=False` senden, `format="json"` NICHT senden. JSON-Einhaltung erfolgt über Prompt-Overrides (Gemma4-spezifische `[REGELN]`) + die Cleanup-Pipeline in `services/postprocess.py` (`clean_json_response` → `deduplicate_repetition` → `repair_truncated_json`, gebündelt in `parse_json_strict`). Die Pipeline läuft seit der MS-Welle im Worker (`expect_json`-Pfad), nicht mehr im Provider.

Status: Ollama-Bug offen (Stand 15.04.2026).

### 2.7 Model-Service-Schicht (seit Chat 92, erweitert Chat 94)

Alle Modell-Aufrufe laufen über eine In-Process-Microservice-Architektur in `server/services/model_services/`. Konsumenten kennen keine Modelle, nur drei abstrakte Rollen; ein Worker pro Rolle vermittelt zwischen Konsument-Absicht und Modell-Aufruf über eine FIFO-Queue. Die Provider-Klassen (`OllamaProvider`/`AnthropicProvider`, §2.3) werden nur noch von der Registry instanziiert — kein Konsument ruft sie direkt.

**Drei Rollen:**

| Rolle | Worker | Backend(s) | Modell (Connector `gemma4`) |
|-------|--------|-----------|------------------------------|
| `embed` | `EmbedWorker` | fest GPU | `nomic-embed-text-v2-moe` |
| `chat` | `ChatWorker` | single, `WORKER_BACKEND_CHAT` | `gemma4-gpu` |
| `background` | `BackgroundWorker` | dual: `analyse` + `sprache` | `qwen3-32b-cpu` / `gemma4-cpu` |

**Backend-Wahl** ist config-gesteuert über `MODEL_WORKER_BACKENDS` (`config.py`), nicht hartverdrahtet. `_build_backend(kind)` in `registry.py` baut aus dem Schlüssel die Provider-Instanz; gültige Schlüssel: `ollama_gpu`, `ollama_cpu_analyse`, `ollama_cpu_sprache`, `anthropic` (fail-loud bei unbekanntem Schlüssel). Das ersetzt das alte globale `LLM_PROFILE`-Schema feinkörnig — eine Rolle kann auf Claude laufen, während die anderen lokal bleiben (z. B. Chat-Eval auf `anthropic`, Background weiter lokal).

**Komponenten:**

- `types.py` — typisierte Requests/Responses: `EmbedRequest`/`EmbedResponse`, `ChatRequest`/`ChatResponse`, `BackgroundRequest`/`BackgroundResponse`
- `worker_base.py` — `ModelWorker`-Basisklasse mit FIFO-Queue, `submit` (async, aus dem Haupt-Loop) und `submit_sync` (Brücke für Worker-Thread-Konsumenten)
- `embed_worker.py` — `EmbedWorker` (Rolle `embed`, GPU-fix), geteilt von Nova und Pixie
- `chat_worker.py` — `ChatWorker` (Rolle `chat`, single-backend), `expect_json` → `parse_json_strict`
- `background_worker.py` — `BackgroundWorker` (Rolle `background`, dual-backend analyse/sprache), CJK-Guard für Qwen-Output, `expect_json`-Pfad
- `registry.py` — `ModelServiceRegistry`, Lifecycle (`startup`/`shutdown` im FastAPI-Lifespan), Singleton `model_service`, `_build_backend`

JSON-Post-Processing liegt in `services/postprocess.py` (zustandsloser Util, bewusst außerhalb des `model_services`-Pakets — siehe Lesson `paket-init-zyklus`).

**Aufruf-Konvention:**

Konsumenten im Worker-Thread (LangGraph-Nodes, die meisten Agenten):

  `model_service.chat.submit_sync(ChatRequest(...))`

Konsumenten im Haupt-Event-Loop (Lifespan-Repair, `shadow_delivery_loop`):

  `await model_service.chat.submit(ChatRequest(...))`

**Stand Chat 94:** Block 1 (`embed`), Block 2 (`chat` + `background`) und Block 3 (`think` pro Call) abgeschlossen. Backend-Switch zu Qwen 3.6 (`qwen36-cpu`) folgt in Block 4. Details: `novaberg-microservice-modell-queue_k.md`.

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
│   ├── prompt_loader.py                 # Laedt PROMPTS-Dict (default/ + Modell + Connector)
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
│   │   ├── character_graph.py           #   CharacterGraph (Pfad 2, 20 Nodes — gezählt 31.07.2026; die frühere Angabe 17 ist älter als Verfasser und Haltungsraum)
│   │   ├── agent_graph.py               #   AgentGraph (Pixie-Pipeline, 3 Nodes)
│   │   ├── builder.py                   #   Fassade, Plugin-Init
│   │   ├── personality.py               #   Personality-Klassen (Character, Emotion, Personality, InternalPersonality)
│   │   ├── state.py                     #   State-Definition, PendingWrite
│   │   └── nodes/                       #   20 Node-Dateien, von den drei Graphen geteilt (gezählt 31.07.2026)
│   │       ├── haltung.py               #     Knoten `haltungsraum`: lädt Landschaft + Rad, rechnet, schreibt state["haltung"] (→ novaberg-haltungsraum_k.md §2)
│   │       ├── perzeption.py            #     → novaberg-node-perception.md (rolle user/assistant)
│   │       ├── db_zugriff.py            #     → novaberg-node-db-zugriff.md (CG-Entry, lädt Personality)
│   │       ├── enricher.py              #     → novaberg-node-enricher.md (Methodensplit nach Phase 4)
│   │       ├── emotionale_gravitation.py #     → novaberg-node-emotionale-gravitation.md (CG, zwischen Enricher und Reducer)
│   │       ├── reducer.py               #     Dedupliziert memory_entries → memory_context (nur CG, seit Chat 75)
│   │       ├── sachlage.py              #     → novaberg-thinking-lage_k.md (CG, reducer→sachlage_node→router: fortgeschriebenes Verstehen je Turn, seit 28.08.2026)
│   │       ├── ei_calc.py               #     → novaberg-node-ei-calc.md (rolle user/character)
│   │       ├── ei_calc_persist.py       #     → novaberg-node-ei-calc-persist.md (CG-Ausgang, nova_state-Persistierung)
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
│   ├── agents/                          # Agent-System (Epic 11 + Epic 5) — 17 Agenten
│   │   ├── __init__.py                  #   AgentRegistry, Auto-Discovery
│   │   ├── base.py                      #   BaseAgent, AgentState, AgentResult, PeriodicTask
│   │   ├── crud_validation.py           #   Gemeinsame CRUD-Haertung (Chat 42)
│   │   ├── notizen/                     #   NotizenAgent (User-Agent, Resume + Bestaetigung)
│   │   ├── timeline/                    #   TimelineAgent (User-Agent, Zeitparser + Resume)
│   │   ├── charakter_identitaet/        #   CharakterIdentitaetAgent (User-Agent, Resume + init.sql)
│   │   ├── direktiven/                  #   DirektivenAgent (User-Agent, HITL-Gate + init.sql)
│   │   ├── dateien_index/               #   DateienIndexAgent (Waechter, ohne Takt, init.sql)
│   │   │   ├── wandern.py               #     neu | geaendert | unveraendert | verschwunden | ausserhalb
│   │   │                           #     Hash: neu/geaendert. Blick auf die Platte: fort/ausserhalb
│   │   │   ├── indizieren.py            #     Thema, Stichwoerter, Blockkarte, Einbettung
│   │   │   ├── speicher.py              #     Zeilen ueber Dateien, nie Dateien
│   │   │   └── aufzeichnungen.py        #     der Enricher-Weg: Treffer je Turn (seit 18.08.2026)
│   │   ├── dateien/                    #   DateienAgent (lesend, Empfang, vier Ausgaenge, seit 18.08.2026)
│   │   │   ├── klassifikation.py        #     wonach gesucht wird und wie tief (finden | lesen)
│   │   │   ├── suche.py                 #     drei Kanaele, scharf vor unscharf
│   │   │   ├── zoom.py                  #     Karte (aus dem Index), Block, Nadel
│   │   │   ├── auskunft.py              #     die Beschriftung: jede Zeile traegt ihre Fundstelle
│   │   │   └── dispatch.py              #     kein Tor, kein Rueckweg — der Dienst aendert nichts
│   │   ├── dateien_wurzeln/             #   DateienWurzelnAgent (User-Agent, Tor + Aussenrand + init.sql)
│   │   │   ├── aussenrand.py            #     Die Schranke: aufloesen, dann pruefen (→ novaberg-agent-dateien_k.md §7)
│   │   │   ├── resume.py                #     Rueckweg der Rueckfrage — nein und unklar fuehren nie zur Ausfuehrung
│   │   │   └── init.sql                 #     Tabelle dateien_wurzeln (seit 18.08.2026)
│   │   ├── kzg/                         #   KZG-Agent (LangGraph-Subgraph, 5 Nodes inkl. magnete_aufloesen)
│   │   ├── delegation/                  #   DelegationsAgent (Halluzinations-Ventil, init.sql)
│   │   ├── recherche/                   #   RechercheAgent (Pixie, Web-Recherche)
│   │   ├── promotion/                   #   PromotionAgent (Pixie, KZG -> LZG)
│   │   ├── charakter/                   #   CharakterAgent (Pixie, Hash-Destillation + zwei Charakter-Raeder)
│   │   │   ├── rad_messreihe.py         #     Messreihe der Raeder: rohe Messungen + gewichtetes Mittel (→ novaberg-charakter-rad-messreihe_k.md)
│   │   │   └── init.sql                 #     Tabelle charakter_rad_messung (seit 01.08.2026)
│   │   ├── wiedervorlage/               #   WiedervorlageAgent (Pixie)
│   │   ├── synapsen_promotion/          #   Synapsen P4 (Pixie, KZG -> lzg_knoten)
│   │   ├── synapsen_decay/              #   Synapsen P6 (Pixie, Knoten-Decay + pipeline_log-Retention)
│   │   ├── wissen/                      #   WissenAgent — die eigene Bibliothek als bestellbarer Dienst (Empfang, CPU-Spur, seit 19.08.2026)
│   │   ├── wissen_rueckweg/             #   Rueckweg: zwei Auftragsarten — 'wissen_rueckweg' schneidet ein, 'wissen_verweis' verstaerkt nur (Pixie, LLM-Spur, seit 18.08.2026)
│   │   │   ├── herkunft.py              #     roh vor verdichtet — die Marke reist mit
│   │   │   ├── zuordnung.py             #     Pflegbarkeit statt Naehe; keine Datei ist eine Antwort
│   │   │   └── einarbeitung.py          #     Absatz an die Stelle, versioniert, umkehrbar
│   │   ├── wissensluecken/              #   WissensluckenAgent (Pixie, Chat 112)
│   │   └── ziel_decay/                  #   Motivations-Verfall der Ziele (Pixie, Anker + Uhr seit Chat 113)
│   │
│   ├── ei/                              # EI-Berechnungsmodul (Chat 58 ausgelagert, Chat 61 Refactor)
│   │   ├── berechnung.py                #   Verlauf, Vektor, Nova-Empathie, sin^0.5-Glaettung
│   │   ├── dreischicht.py               #   6 Achsen → 64 Sektoren → 13 Cluster → Strategie (→ novaberg-gv-strategie_k.md)
│   │   ├── raum.py                      #   Novas Gespraechsraum, Zug zum Register des Sprechers (Chat 114)
│   │   ├── initiative.py                #   Achse I: wer im Turn die Richtung setzt (Chat 116, → novaberg-gv-initiative.md)
│   │   ├── neugier.py                   #   GV4: sechs Saeulen × Persoenlichkeit → Aufnahmebereitschaft
│   │   ├── wissensluecken.py            #   GV4: semantisch nahe, aber unbesprochene Konzepte
│   │   ├── gravitation.py               #   Emotionale Gravitation: Erinnerungen als Attraktoren (→ novaberg-node-emotionale-gravitation.md)
│   │   ├── salienz.py                   #   Salienz-Formel (→ novaberg-salienz-berechnung_k.md)
│   │   ├── haltung.py                   #   Landschaft + Zuwendungsrad → fuenf Verhaltensgroessen (→ novaberg-haltungsraum_k.md)
│   │   ├── farbton.py                   #   Farbmisch-System: 8 Dimensionen → Landschaftsbeschreibung
│   │   └── utils.py                     #   Gemeinsam genutzt von Neugier, Wissensluecken, Dreischicht (u.a. modus_pruefen)
│   │
│   ├── tools/                           # Tool-Manager (Epic 11)
│   │   ├── db_manager.py                #   PostgreSQL + Connection Pool
│   │   ├── redis_manager.py             #   Redis (nativ threadsafe)
│   │   ├── web/                         #   Web-Infrastruktur (Chat 35)
│   │   │   ├── search.py                #     WebSearchManager (SearXNG)
│   │   │   └── fetch.py                 #     PageFetcher (trafilatura + BS4)
│   │   └── dateien/                     #   Datei-Werkzeuge (WIS-3)
│   │       └── schreiben.py             #     Pfadwaechter + Modusbits (F-WISSEN-1)
│   │                                    #     die uebrigen Dateien dieses Verzeichnisses
│   │                                    #     fehlen im Baum — siehe novaberg-fundliste.md
│   │
│   ├── memory/                          # Gedaechtnis-Schicht
│   │   ├── kzg.py                       #   Kurzzeitgedaechtnis (Redis, RediSearch-Index, Magnet-Felder P3)
│   │   ├── lzg_knoten.py                #   Langzeitgedaechtnis: Knoten (PostgreSQL, Ebbinghaus)
│   │   ├── lzg_kanten.py                #   Langzeitgedaechtnis: Kanten
│   │   ├── pipeline_log.py              #   Forensik-Sink (Synapsen P1, asynchroner Writer-Task)
│   │   ├── sachlage_verlauf.py          #   Sachlage-Gedaechtnis je Turn, ohne Verfall (→ novaberg-thinking-lage_k.md §4)
│   │   ├── charakter.py                 #   Charakter-Hash (Read)
│   │   ├── haltung.py                   #   Haltungsstand je Paar (Zustand, nicht Verlauf)
│   │   ├── session.py                   #   Session (_session_key mit character_id, Chat 60)
│   │   ├── kontext.py                   #   Session-Kontext-Extraktion (LLM-gestuetzt)
│   │   ├── ziele.py                     #   Ziele: lang-, mittel- und (seit 28.08.2026) kurzfristig; Verfall — beim Lesen gerechnet (ziele_live_bewerten)
│   │   ├── kurzziel.py                  #   Das kurzfristige Ziel aus der Sachlage (→ novaberg-thinking-lage_k.md §4, Scheibe 2)
│   │   ├── utils.py                     #   Gemeinsame Helfer der Schicht
│   │   ├── repositories/                #   Daten-Repositories (CRUD gegen PostgreSQL)
│   │   │   ├── entitaeten_repository.py #     Knowledge Graph Nodes
│   │   │   ├── fakten_repository.py     #     Knowledge Graph Edges (bi-temporal)
│   │   │   ├── timeline_repository.py   #     Termine und Ereignisse
│   │   │   ├── notizen_repository.py    #     Merkzettel und Listen
│   │   │   ├── autonomous_wissen_repository.py # Metadaten der Wissens-Bibliothek (WIS-2/3)
│   │   │   ├── verbindung_repository.py #     KZG-Verbindungen
│   │   │   └── shadow_auftrag_repository.py # Shadow-Queue samt Verfall (→ novaberg-queue-verfall_k.md)
│   │   └── services/
│   │       └── entity_resolution.py     #   Entity Resolution (Name + Fuzzy + Embedding)
│   │
│   ├── utils/                           # Hilfsfunktionen — reine Rechnung, kein Zugriff
│   │   ├── zeitparser.py                #   Zeitaufloesung (Fuzzy + Normalisierung + Vektor)
│   │   ├── datum_pruefung.py            #   Wochentag gegen Datum
│   │   └── etikett.py                   #   was ein Pfad ueber die Geltung sagt (23.08.2026)
│   │
│   ├── plugins/                         # Manager-Plugins
│   │   ├── base.py                      #   BaseManager Interface
│   │   ├── kzg_manager/                 #   KZG-Schreiboperationen
│   │   ├── fakten_manager/              #   Fakten + Entity Resolution
│   │   ├── timeline_manager/            #   Termine + Zeitparser
│   │   ├── notizen_manager/             #   Merkzettel, Listen
│   │   ├── charakter_identitaet_manager/#   Charakter-Identitaet (Router-Prompt)
│   │   ├── dateien_manager/             #   Der Aushang des lesenden Dienstes (seit 18.08.2026, kein Schreibpfad)
│   │   └── direktiven_manager/          #   Direktiven (Router-Prompt)
│   │
│   └── services/                        # Dienste
│       ├── llm_provider.py              #   LLM-Provider-Klassen (LLMProvider-ABC, OllamaProvider, AnthropicProvider) — nur Instanziierung durch Registry
│       ├── postprocess.py               #   JSON/CJK-Postprocess-Util (zustandslos, aus model_services gelöst — Lesson paket-init-zyklus)
│       ├── model_services/              #   Model-Service-Schicht (In-Process-Microservice, §2.7)
│       │   ├── types.py                 #     Typisierte Requests/Responses (Embed/Chat/Background)
│       │   ├── worker_base.py           #     ModelWorker-Basis (FIFO-Queue, submit / submit_sync)
│       │   ├── embed_worker.py          #     EmbedWorker (Rolle embed, GPU-fix)
│       │   ├── chat_worker.py           #     ChatWorker (Rolle chat, single-backend)
│       │   ├── background_worker.py     #     BackgroundWorker (Rolle background, dual analyse/sprache, CJK-Guard)
│       │   └── registry.py              #     ModelServiceRegistry, _build_backend, Singleton model_service
│       ├── events.py                    #   Event-Queue (Redis FIFO, Self-Trigger-Schutz, Chat 60)
│       ├── event_consumer.py            #   Event-Consumer (async-Loop, WebSocket-Delivery, Chat 60)
│       ├── prompt_eingang.py           #   Eingangs-Queue vor Pfad 1, Blockbildung, Turn-Marker (Chat 124)
│       ├── prompt_consumer.py          #   Prompt-Consumer (async-Loop, faehrt Pfad 1 hinter der Queue, Chat 124)
│       ├── shadow_delivery.py           #   Pixie -> Chat-Einspeisung
│       ├── shadow_agent/                #   Alter Pixie-Runner (extern aufruflos, PIX-CLEAN)
│       └── pixie/                       #   Neues Pixie-System (Chat 33+)
│           ├── scheduler.py             #     APScheduler-Heartbeat
│           ├── kandidaten.py            #     Queue-Peek + periodische Aufgaben
│           ├── router.py                #     Aufgabe -> Agent-Name
│           ├── dispatch.py              #     Agent-Ausfuehrung
│           ├── riegel.py                #     Riegelkette der Zustellung (Riegel 1 gebaut)
│           └── stack.py                 #     Shadow-Stack Push
│
├── db/
│   └── init.sql                         # Kern-Schema (LZG, Entitaeten)
│
├── ollama/
│   └── modelfiles/                      # GPU + CPU Modelfiles
│
├── ruff.toml                            # Linter-Konfiguration, gilt fuer allen Python-Code
├── ruff-hart.toml                       # engere Auswahl: Familien ohne geduldeten Bestand
└── docker-compose.yml
```

**Zur `ruff.toml`:** Sie steht in der Wurzel, weil es keine `pyproject.toml` gibt — der Server wird nicht als Paket installiert, sondern als Quellbaum in den Behaelter gemountet. Zielversion ist `py312` aus der Bildbasis des Servers, nicht die Python-Version des Hosts. Jeder gesetzte Grenzwert traegt in der Datei seine Herleitung und seine Messzahlen; jede abgeschaltete Regel ihre Begruendung. Vier Regeln sind abgeschaltet, weil sie einer im Projekt vorgeschriebenen Bauart widersprechen — darunter das f-String-Verbot im Logging und die Zaehlung der Rueckkehrpunkte, die mit der EVA-Disziplin unvereinbar ist.

**Zur `ruff-hart.toml`:** Die `ruff.toml` duldet den Bestand — ihr Lauf endet mit Treffern, die gezaehlt und nicht behoben werden. Die `ruff-hart.toml` fuehrt die Familien, fuer die das nicht mehr gilt: Sie erbt die erste ueber `extend` vollstaendig und ersetzt davon nur die Regelauswahl, und **ihr Lauf muss sauber sein**. Aufruf aus der Repo-Wurzel: `ruff check --config ruff-hart.toml server/`, Rueckgabewert 0 ist die Bedingung. Die Trennung ist noetig, weil Ruff keine Schweregrade kennt — in einer gemeinsamen Datei waere ein neuer Treffer der harten Familie von den geduldeten nicht zu unterscheiden. Aufgenommen wird eine Familie, wenn sie ueber `server/` null Treffer hat, keine ihrer Regeln im Preview-Status steht und geprueft ist, dass das Werkzeug jedes Exemplar im Bestand sehen kann. Stand 30.07.2026: `LOG`.

### Event-Modell (Chat 60)

Seit Chat 60 sind User und Charakter zwei unabhängige Akteure:

| Pfad | Graph | Nodes | Aufgabe |
|------|-------|-------|---------|
| Pfad 1 | HumanGraph | 5 | User schreibt: Wahrnehmung + Speicherung |
| Pfad 2 | CharacterGraph | 17 | Charakter reagiert: Identität laden + Lesen + Entscheiden + Antworten + Perzeption(Nova) + Konsolidieren + Speichern |

Verbunden durch eine Redis-Event-Queue (`event_queue:{user_id}:{character_id}`). Ein Event-Consumer (`services/event_consumer.py`) pollt die Queue und startet CharacterGraph-Durchlaeufe. Antworten erreichen den Client per WebSocket.

**Neue Services:**

| Service | Datei | Aufgabe |
|---------|-------|---------|
| Event-Queue | `services/events.py` | Event erzeugen, lesen, Self-Trigger-Schutz |
| Event-Consumer | `services/event_consumer.py` | Queue-Polling, Debouncing, Graph-Aufruf, WebSocket-Delivery, Turn-Marker loeschen |
| Prompt-Consumer | `services/prompt_consumer.py` | Eingangs-Queue-Polling, Blockbildung, Pfad-1-Lauf, Turn-Marker setzen |

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
| `plan(state, postgres_url)` | `dict` | Management-Aktion planen (LLM via `model_service.chat`) | Planner |
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

### 4.5 Die acht Manager

> **Acht sind registriert, sieben stehen in der Tabelle.** `ls -d server/plugins/*_manager | wc -l` → **8**; die Tabelle unten trägt **7** Zeilen. Es fehlt `WissenManager` (`plugins/wissen_manager/`) — er ist seit dem 04.08.2026 im Bestand und hat nie eine Zeile bekommen. **Bestandsbefund, hier benannt und nicht im Vorbeigehen aufgefüllt** (Fundliste, 18.08.2026).

| Manager | Ordner | Verantwortung |
|---------|--------|---------------|
| **KzgManager** | `plugins/kzg_manager/` | KZG-Schreiboperationen (Store, Verstaerkung) |
| **FaktenManager** | `plugins/fakten_manager/` | Fakten + Entity Resolution (Typ 1 + 2, bi-temporal) |
| **TimelineManager** | `plugins/timeline_manager/` | Termine + Zeitparser (CRUD) |
| **NotizenManager** | `plugins/notizen_manager/` | Merkzettel, Listen, Snippets (CRUD + Append) |
| **CharakterIdentitaetManager** | `plugins/charakter_identitaet_manager/` | Router-Prompt für Identitätszuweisungen (CRUD via CharakterIdentitaetAgent) |
| **DirektivenManager** | `plugins/direktiven_manager/` | Router-Prompt für Verhaltensdirektiven (CRUD via DirektivenAgent) |
| **DateienWurzelnManager** | `plugins/dateien_wurzeln_manager/` | Router-Prompt für Verzeichnis-Freigaben (CRUD via DateienWurzelnAgent) |

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
| Graph-Pipeline (HumanGraph: 5 Nodes Pfad 1 | CharacterGraph: 17 Nodes Pfad 2 | AgentGraph: 3 Nodes) | Implementiert & getestet | novaberg-graph.md, novaberg-node-*.md |
| PFAD2-PERZEPTION-FIX Phase 2 (db_zugriff + ei_calc_persist als CG-Klammer) | Implementiert & validiert (Chat 89) | novaberg-node-db-zugriff.md, novaberg-node-ei-calc-persist.md, novaberg-path2-perzeption_k.md |
| PFAD2-PERZEPTION-FIX Phase 3 (Personality-Klassen-Schicht: external/internal mit emotion/character/identities/directives) | Implementiert & validiert (Chat 89) | novaberg-personality.md, DEVELOPER_HANDBOOK.md §6, novaberg-lesson_l_klassen-statt-flache-keys.md |
| HumanGraph-Slimming Phase 4 (Enricher-Methodensplit, Reducer aus HG raus, kein KZG/LZG-Lauf im HG) | Implementiert & validiert (Chat 90) | novaberg-graph.md §3.1, novaberg-node-enricher.md |
| EI-Calc-Node (reine Python-Berechnung, Dual-Modus User + Nova) | Implementiert & validiert | novaberg-node-ei-calc.md |
| Dual-Emotion Phase 2 (Nova-Empathie, Konflikt-Erkennung) | Implementiert (AP1–3, AP7, AP4 teilw., AP8 teilw.) | novaberg-ei-dual-emotion_k.md |
| Graph-Pipeline (AgentGraph, 3 Nodes) | Implementiert & getestet | novaberg-graph.md, novaberg-pixie.md |
| Kurzzeitgedaechtnis (Redis + Vektor) | Implementiert & getestet | novaberg-mem-kzg.md |
| Kurzzeitgedaechtnis Magnet-Felder (entitaet_ids, timeline_id, Synapsen P3) | Implementiert | novaberg-mem-kzg.md, novaberg-pixie-kzg.md |
| Langzeitgedaechtnis (PostgreSQL) | **Abgeloest durch das Synapsen-Modell (P9, 02.08.2026)** | novaberg-memory-synapsen_k.md · archive/novaberg-mem-lzg.md |
| Pipeline-Log-Forensik (asynchroner Writer, JSONB-Inhalt, Span-Korrelation, turn_id über /chat + /chat/stream + fail-loud bei leerem turn_id) | Implementiert (Chat 88 P1.1, vervollständigt Chat 90 TURN-ID-FIX) | novaberg-memory-synapsen_k.md §10 |
| Synapsen-Tabellen (lzg_knoten, lzg_kanten, parallel zum LZG) | Schema angelegt, leer | novaberg-memory-synapsen_k.md §4 |
| Ebbinghaus-Decay + Soft-Delete | **Abgeloest: `SynapsenDecayAgent` materialisiert `gewicht_decay`** (P9) | novaberg-memory-synapsen_k.md §9 · archive/novaberg-pixie-decay.md |
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
| Plugin-System (8 Manager) | Implementiert & getestet | novaberg-architecture.md |
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
| Arousal-basierter Decay (Emotions-Persistenz) | Implementiert | archive/novaberg-pixie-decay.md |
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
| Gespraechsvektor (GV1+GV2: Node, Farbmisch, ~~Entity-Hop~~ Resonanz-Kontext) | Implementiert & validiert | novaberg-node-gv_k.md |
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

Das Handbuch ist nach Betrachtungstiefen organisiert. Tiefe 0 ist der Einstiegspunkt, jede weitere Tiefe geht ins Detail. **131 Dateien** im Verzeichnis `novaberg/docs/` (gezaehlt 28.07.2026 — eine Zaehlung ohne Messdatum veraltet zwischen zwei Sitzungen).

### Tiefe 0 — Projekt

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-project_k.md | Konzept, Vision, Leitprinzipien, Persoenlichkeit |

### Tiefe 1 — Architektur & Subsysteme

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-architecture.md | Systemarchitektur, Tech-Stack, Plugin-System (dieses Dokument) |
| novaberg-graph.md | Graph-Architektur, HumanGraph, AgentGraph, Agent-System, State |
| novaberg-graph-rechenkette.md | **Rechenkette des CharacterGraph** — Register der 34 Rechensysteme in sechs Stufen: was jedes aus welchen Eingängen berechnet und auf welchem Weg es die Antwort erreicht. Zerlegt entlang der Rechnungen statt entlang der Knoten (ein Knoten trägt bis zu sechs Systeme, ein System läuft über zwei Knoten) und weist je System Reinheit und Prüfstand aus; §11 nennt die drei Größen, die erst im Folgeturn wirken |
| novaberg-memory.md | Gedaechtnis-Ueberblick (Session → KZG → LZG → KG) |
| novaberg-ei.md | Emotionale Intelligenz Ueberblick |
| novaberg-pixie.md | Pixie-System, Scheduling, Queue/Stack/Delivery |
| novaberg-queue-verfall_k.md | **Verfall der Shadow-Queue** — Konzept: Ein Auftrag ist ein Vorsatz und verliert seinen Anlass; die Queue kannte bis dahin keinen Weg hinaus außer Ausführung. Übernimmt die Bauart von `lzg_knoten` (Sinus-Sättigung im Aufbau, exponentieller Verfall, **Soft-Delete statt Löschen**, Halbreaktivierung auf 50 % des Bandes über der Schwelle) mit eigener Rate: 30 Tage bis Schwelle 0,3. **Die Queue zieht dafür nach PostgreSQL um, der Stapel nicht** — gemessen an der Lesefrequenz, nicht an der Datenmenge (⬜ nicht gebaut, Bestand 1036 am 15.08.2026 gemessen) |

### Tiefe 2 — Pipeline-Nodes (15)

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-node-perception.md | Perzeption (Emotion, Arousal, Intent, Plutchik-Oktagon, Dual-Modus User/Nova) |
| novaberg-node-db-zugriff.md | db_zugriff (CG-Entry, lädt Personality-Klassen aus PostgreSQL/Redis) |
| novaberg-node-enricher.md | Enricher (Methodensplit nach Phase 4: _enrich_human schlank, _enrich_character voll, Plugin-Hooks im CG) |
| novaberg-node-ei-calc.md | EI-Calc (Python-Berechnung: Verlauf, Vektor, Nova-Empathie, kein LLM) |
| novaberg-node-emotionale-gravitation.md | Emotionale Gravitation (CG, injiziert reaktivierte Erinnerungen in Novas Emotions-Verlauf) |
| novaberg-node-ei-calc-persist.md | ei_calc_persist (CG-Ausgang, konsolidiert internal.emotion, persistiert nova_state) |
| novaberg-node-router.md | Router (Routing, Agenten-Delegation) |
| novaberg-node-planner.md | Planner (Agent-Loop, Resume-Flow) |
| novaberg-node-agent-dispatch.md | Agent-Dispatch (Zentraler Entry-Point) |
| novaberg-node-gv_k.md | Gespraechsvektor (Farbmisch-System, zweite Wissensquelle: ~~Entity-Hop~~ Resonanz-Kontext seit Chat 115) |
| novaberg-gv-initiative_k.md | Initiative-Achse — Konzept: Herleitung, verworfene Wege, Kalibrier-Agent (Entwurf) |
| novaberg-gv-initiative.md | Initiative-Achse — Modul: Datenfluss, Konstanten mit Kalibrierungsstand, Messungen |
| novaberg-charakter-rad-messreihe_k.md | Die Charakter-Räder als Messreihe — Konzept: Das Rad misst einen akuten Zustand und wird durch die Messungen der letzten Tage stabilisiert; rohe Messungen in `charakter_rad_messung`, gelesener Wert als gewichtetes Mittel (🔶 gebaut für das Zuwendungs-Rad) |
| novaberg-erreichbarkeit_k.md | **Erreichbarkeit** — Konzept: Eine Landschaft, die nie betreten wird, und eine, die immer betreten wird, sind derselbe Defekt. Überträgt das für die GV-Sektoren entschiedene Kriterium *Erreichbarkeit statt Häufigkeit* auf die vierzehn Gesprächslandschaften; der Charakter verschiebt die Verteilung, schließt aber keine Landschaft, und nachgeregelt wird nicht zur Laufzeit (⬜ nicht gebaut, alle vierzehn erreichbar gemessen, Ablesung fällt in 14 % aus) |
| novaberg-haltungsraum_k.md | Haltungsraum — Konzept: Landschaft setzt Grundwerte für fünf Verhaltensgrößen, das Zuwendungsrad modifiziert sie; Grenzen multiplizieren, Neigungen addieren, und ein **Zug** nach der Rechnung lässt eine extrem ausgeprägte Speiche die Lage überstimmen (🔶 Rechnung, Knoten und Protokoll gebaut und im Betrieb, **Prompt offen — kein Leser der Haltung**) |
| novaberg-kalibrierung_k.md | **Kalibrierung** — Konzept über alle Stellschrauben: sechs Klassen (Naben, Beiträge, Schwellen, Verfall, Glättung, Kennlinien), der Erwartungskorridor als Pflicht vor jedem Dreh, die Trennung von Ablesung und Wirkgröße — eine gestreckte Skala ist kein Befund —, und **die Trennung von Kalibrier- und Validierungsmenge** (§5): Eine Zahl, gegen die eingestellt wurde, ist als Beleg verbraucht (⬜ Verfahren steht, kein Korridor geschrieben, keine Validierungsmenge erhoben) |
| novaberg-node-verfasser_k.md | Verfasser — Konzept: ein Node vor dem Responder, der den fachlichen Inhalt bestimmt; Inhalt und Wesen werden getrennt (⬜ nicht gebaut) |
| novaberg-node-responder.md | Responder (Antwortgenerierung, EI-MIKRO) |
| novaberg-node-thinker.md | Thinker (Faktenpruefung, Web-Suche) |
| novaberg-node-tribunal.md | Tribunal (Drei-Perspektiven-Bewertung, Score-System) |
| novaberg-node-corrector.md | Corrector (Korrekturschleife) |
| novaberg-node-salience.md | Salienz (Bewertung, pending_writes, Input-Switch nach graph_rolle) |
| novaberg-node-dispatcher.md | Dispatcher (Session-Turn-Schreiben, KZG-Dispatch, Schreiboperationen verteilen) |

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
| archive/novaberg-pixie-decay.md | DecayAgent — **archiviert (P9)**, Agent geloescht |
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
| archive/novaberg-mem-lzg.md | Langzeitgedaechtnis — **archiviert (P9)**, Tabelle und Modul geloescht |
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
| novaberg-thinking-erkenntniszyklus_k.md | **Der Erkenntniszyklus** — die Folge, in der Nova ein Thema durchdringt: Nachdenken vor Nachschlagen. Übergeordnet über Meinung, Neugier, Wissenslücken und Wissensspeicher |

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

### Lessons

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
| novaberg-lesson_l_miss-als-sicherung.md | Der Miss ist manchmal die Sicherung (Router-Miss als Schutz vor defektem Pfad) |
| novaberg-lesson_l_default-wie-fehlschlag.md | Ein Default darf nie wie ein Fehlschlag aussehen (nie geladen vs. leer geladen) |
| novaberg-lesson_l_log-behauptet-was-es-weiss.md | Ein Log darf nur behaupten, was es weiß (lügende Logs, broadcast-Wurzel) |
| novaberg-lesson_l_stichprobe-trifft-den-pfad.md | Die Stichprobe ist repräsentativ für den Pfad, den sie trifft |
| novaberg-lesson_l_fehlschlag-als-absicht.md | Ein Fehlschlag darf nie wie eine Absicht aussehen (der getarnte Miss) |
| novaberg-lesson_l_analyse-ersetzt-keine-messung.md | Ein Analyse-Upgrade ersetzt keine Messung |
| novaberg-lesson_l_konzept-spricht-code.md | Ein Konzept, das in Code-Sprache spricht, wird für einen Befund gehalten |
| novaberg-lesson_l_ableitung-als-messung.md | Eine Ableitung ist keine Messung — auch wenn sie stimmt |
| novaberg-lesson_l_gelesen-ist-nicht-wirksam.md | Die gelesene Quelle ist nicht die wirksame (zwei Speicher, einer gilt) |
| novaberg-lesson_l_gegenprobe-misst-den-cache.md | Eine Gegenprobe, die den Bytecode-Cache erwischt, misst gar nichts |
| novaberg-lesson_l_weg-vor-wortschatz.md | Erst messen, ob der Weg befahren wird — sonst erweitert man einen toten Pfad |
| novaberg-lesson_l_parst-nicht-schlaegt-parst-falsch.md | Eine zu breite Regel macht aus dem harmlosen Ausfall den schädlichen |
| novaberg-lesson_l_meldung-im-bestand-ertrinkt.md | Eine Regel, deren Verletzung ein Absturz ist, gehört nicht in eine geduldete Trefferzahl |

### Uebergreifend

| Dokument | Beschreibung |
|----------|-------------|
| novaberg-roadmap.md | Projektchronik, **laufender Zeitraum** (nur abgeschlossene Arbeit) |
| novaberg-roadmap-2026-*.md | Chronik abgeschlossener Zeitraeume — je Monat eine Datei |
| novaberg-roadmap-index.md | Findemittel ueber alle Chronikteile — eine Zeile je Abschnitt, **erzeugt** |
| novaberg-backlog.md | Backlog: Kopf, Wegweiser und der Verlauf des Standes |
| novaberg-backlog-{gegenstand}.md | Backlog nach Gegenstand — sechs Dateien: Gedaechtnis, Hintergrund, Charakter, Antwortpfad, Wissen, Bauart |
| novaberg-backlog-rangordnung.md | Baender und laufende Reihen — quer zu allen Gegenstaenden |
| novaberg-backlog-index.md | Findemittel ueber alle Backlog-Teile, mit der Rangordnung, **erzeugt** |
| novaberg-bugs.md | Bekannte Probleme & Limitationen — **nur die nicht abgeschlossenen** |
| novaberg-bugs-archiv.md | Abgeschlossene Defekte: behoben, geschlossen, gegenstandslos, verworfen |
| novaberg-fundliste.md | Rohe, noch unklassifizierte Funde aus laufender Arbeit |

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

  # telegram-bot: abgeschaltet am 24.08.2026, Block entfernt
```

> **Der Auszug ist unvollstaendig:** `synapse` und `matrix-bot` laufen seit dem 23.08.2026
> und stehen hier nicht. Die Betriebsdatei ist `docker-compose.yml` im Arbeitsverzeichnis,
> das Muster im Repositorium `docker-compose.template.yml`.

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
   ├── Lifespan: model_service.startup() -> Worker-Schicht (embed, chat, background)
   ├── Lifespan: Plugin Discovery + Manager Setup
   ├── init.sql -> Schema-Migrationen (idempotent)
   ├── build_human_graph() + build_agent_graph()
   ├── APScheduler -> SchattenArbeit (alle 10 Min)
   └── API bereit auf :8000
5. docker compose up -> matrix-bot (Application Service, wartet auf server + synapse)
   (bis 24.08.2026 stand hier telegram-bot, Long Polling — der Kanal ist abgeschaltet)
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
| Modelle | `OLLAMA_CONNECTOR` (aktiv: `qwen36`), `EMBED_MODEL` — ~~`OLLAMA_GPU_MODEL`, `OLLAMA_CPU_MODEL`~~ existieren nicht mehr, siehe unten |
| Context | `OLLAMA_GPU_NUM_CTX`, `OLLAMA_CPU_NUM_CTX` — **abgeleitet, nicht gesetzt** |
| Pixie | `PIXIE_INTERVALL_MIN` (10), `PIXIE_PROMOTION_PRIORITAET` (0.9), `PIXIE_PROMOTION_INTERVALL_SEKUNDEN` (300), `PROMOTION_THRESHOLD` (0.8, in `memory/kzg.py` — Salienz-Schwelle, nicht in config.py) |
| EI | `EMOTION_DECAY_FACTOR` (0.8), `EMOTION_DECAY_BASE` (10) |
| Decay | `EBBINGHAUS_DECAY_RATE` (0.0015), `EBBINGHAUS_MIN_GEWICHT` (0.1) |
| Namen | `ASSISTANT_NAME` ("Nova"), `BACKGROUND_NAME` ("Pixie") |

> **Am 16.08.2026 gegen den Code geprueft: Die Modelle werden nicht mehr einzeln gesetzt.**
>
> `config.py` fuehrt eine **Connector-Tabelle** `OLLAMA_CONNECTORS` mit je einem Satz aus `gpu_model`, `gpu_num_ctx`, `cpu_model`, `cpu_num_ctx`, `analyse_model` und `analyse_num_ctx`. Eine einzige Umgebungsvariable waehlt aus:
>
> ```python
> OLLAMA_CONNECTOR = os.getenv("OLLAMA_CONNECTOR", "qwen36")
> _connector = OLLAMA_CONNECTORS[OLLAMA_CONNECTOR]
> OLLAMA_MODEL          = _connector["gpu_model"]
> SHADOW_MODEL          = _connector["cpu_model"]
> PIXIE_ANALYSE_MODEL   = _connector["analyse_model"]
> ```
>
> **Was daraus folgt und in der alten Tabelle nicht stand:** Modell und Kontextgroesse sind **zusammen** gewaehlt und koennen nicht einzeln verstellt werden — genau der Fehler, den getrennte Variablen erlauben (ein Modell mit dem Fenster eines anderen). Die Klammerwerte der Zeile `Context` waren deshalb ebenfalls falsch: `(16384)` ist der Wert des Connectors `mistral`, waehrend `qwen36` aktiv ist und 32768 fuehrt.
>
> Die drei Verbraucher heissen `OLLAMA_MODEL` (GPU), `SHADOW_MODEL` (CPU) und `PIXIE_ANALYSE_MODEL` (Analyse).
| Zeitzonen | `TIMEZONE` ("Europe/Berlin") |
| LLM-Backends | `WORKER_BACKEND_CHAT` (ollama_gpu), `WORKER_BACKEND_BG_ANALYSE`, `WORKER_BACKEND_BG_SPRACHE`, `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `LLM_PROFILE` (lokal — nur noch ThinkingNormalizer-Schalter, siehe §2.5/§2.7) |
| Web-Suche | `SEARXNG_URL` (http://searxng:8080), `SEARXNG_TIMEOUT` (10.0), `SEARXNG_MAX_RESULTS` (10) |

**Keine Magic Numbers im Code.** Alle Schwellwerte, Raten und Gewichtungen sind konfigurierbar.

---

## 10. Datenbankschema

Das Kern-Schema lebt in `db/init.sql` als Single Source of Truth (Synapsen P0). Agent-spezifische Tabellen liegen in `server/agents/<agent>/init.sql` und werden beim Agent-Discovery aufgesetzt.

| Tabelle | Quelle | Beschreibung |
|---------|--------|-------------|
| `lzg_knoten` | `db/init.sql` | Synapsen-Knoten — **das Langzeitgedaechtnis** seit P9 (02.08.2026); 1108 Knoten am 02.08. |
| `lzg_kanten` | `db/init.sql` | Synapsen-Kanten-Cache (Synapsen P2, abgeleiteter Cache; drei Trigger zur Neuberechnung) |
| `pipeline_log` | `db/init.sql` | Forensik-Tabelle für Node-Entscheidungen pro Turn (Synapsen P1, JSONB-Inhalt) |
| `sachlage_verlauf` | `db/init.sql` | **Das Sachlage-Gedaechtnis** (28.08.2026) — je gerechnetem Turn eine Zeile: `turn_id`, Paar, `thema`, `gegenstand`, `nutzerziel`, `ausdrucksweise`, `objekte` (JSONB), `herkunft`, `embedding VECTOR(768)` ueber den Gegenstand-Satz (`F-EMBED-1`), `erstellt_am`. **Verfaellt nicht** — ein Faktum, und Turns verfallen auch nicht (`F-VERFALL-1`). Kein Fremdschluessel. Zweites Ende der Sachlage-Bruecke bei Zustellungen; Konzept `novaberg-thinking-lage_k.md` §4 |
| `autonomous_wissen` | `db/init.sql` | Metadaten der Wissens-Bibliothek (WIS-2, 04.08.2026) — **nicht der Inhalt**: Der liegt als Datei ausserhalb des Git-Roots. Paar-Schema und `salienz_anfang` ohne Vorgabewert; gelesen vom `WissenManager` als sechste Kontextquelle des Enrichers. **Seit dem 18.08.2026 ist der Dateien-Index eine weitere Quelle des Enrichers — aber kein Plugin und kein Beitrag zu diesem Pool:** Er schreibt in den eigenen Zustandskanal `aufzeichnungen`, weil alles aus dem Plugin-Pool unter `[GEDAECHTNIS]` gerendert wird und Dateiinhalt dort nicht hineindarf |
| `shadow_auftrag` | `db/init.sql` | **Die Shadow-Queue** (15.08.2026) — bis dahin eine Redis-Liste. Traegt die Auftraege des Pixie-Heartbeats samt Verfallsmodell nach dem Muster von `lzg_knoten`: drei Salienz-Staende, `haeufigkeit`, `aktiv` als Soft-Delete, zwei Uhren. **Acht Spalten ohne Vorgabewert** — Paar-Tripel, Gegenstand und die drei Salienz-Staende; die Sperre wanderte aus der Signatur hierher. Uebernommen wurden 1036 Auftraege. **Seit dem 15.08.2026 zusaetzlich `arousal`** (NULL-faehig, ohne Vorgabewert): die dritte Groesse der Lage neben `emotion` und `modus`. NULL heisst unbekannt — Bestandszeilen tragen sie nicht, und ein Vorgabewert waere ein Messwert, den nie jemand gemessen hat. **Seit dem 23.08.2026 zusaetzlich `grund`** (`VARCHAR(20) NOT NULL DEFAULT ''`): warum die Zeile ist, wie sie ist. `aktiv` sagt, **ob** sie gesucht wird, `grund` sagt, **warum** sie stillliegt (`F-STILLLEGUNG-1`) — Kanon `''` · `verfall` · `fehlversuch`. Anlass war der Fehlversuchspfad, der bis dahin hart loeschte; die 247 stillgelegten Altzeilen tragen `''` und sind daran als Altbestand erkennbar. **Seit dem 28.08.2026 zusaetzlich `ausloeser_turn_id`** (`TEXT`, NULL-faehig, ohne Vorgabewert): der Turn, aus dem der Auftrag entstand — erstes Glied der Sachlage-Bruecke; NULL heisst unbekannt, der Altbestand traegt es. Konzept: `novaberg-queue-verfall_k.md` |
| `charakter_hash` | `db/init.sql` | 5 Persoenlichkeitsprofile (kern_hash, adaptive_hash, beziehungsprofil, intentions_profil, emotions_profil), alle im Prompt injiziert (seit Chat 52) |
| `hintergrund_log` | `db/init.sql` | Pixie-Aufgabenprotokoll |
| `gespraech_archiv` | `db/init.sql` | Session-Archivierung |
| `entitaeten` | `db/init.sql` | Knowledge Graph Nodes |
| `fakten` | `db/init.sql` | Knowledge Graph Edges |
| `timeline` | `db/init.sql` (CREATE) / `agents/timeline/init.sql` (FK + Indizes) | Termine und Ereignisse |
| `notizen` | `db/init.sql` (CREATE) / `agents/timeline/init.sql` (FK auf `timeline_id`) | Merkzettel und Listen |

Alle Migrationen sind idempotent (`IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`). Wiederholtes Ausfuehren von `init.sql` ist sicher. Konvention seit Synapsen P0: Neue Schema-Änderungen werden als ALTER-Statements im Migrations-Block am Ende von `db/init.sql` ergänzt, NICHT direkt in die ursprüngliche CREATE TABLE-Definition eingearbeitet — damit bleibt nachvollziehbar, was wann hinzugekommen ist. Bei späteren Reviews werden die akkumulierten ALTER-Statements in die CREATE-Definitionen konsolidiert.

Foreign-Key-Spalten von Kern-Tabellen auf Agent-Tabellen (z.B. `timeline_id`) sind in `db/init.sql` als nackte INTEGER-Spalten definiert; der FK-Constraint wird in der jeweiligen Agent-`init.sql` gesetzt, damit die Abhängigkeit erst nach Anlage der Agent-Tabelle realisiert wird.

Das Plugin-System lebt weiter parallel (siehe §4) — `plugins/*/init.sql` für Plugin-spezifische Hilfstabellen ist weiterhin möglich, das primäre Datenbankschema ist aber `db/init.sql` plus die Agent-init-SQL.

---

*Konsolidiert aus nova-00-a.md, nova-07-a.md, nova-07-m-a.md.*

---

## Befunde aus dem Betrieb — nachgetragen am 20.08.2026

Aus `novaberg-fundliste.md` hierher gezogen: Aussagen ueber den **Zustand** dieses Gegenstands, die dort als rohe Funde standen und in kein Defekt- oder Vorhabenregister gehoeren. Der Wortlaut ist unveraendert, das Datum steht an jedem Befund — geprueft ist keiner von ihnen gegen den heutigen Code.

- **19.08.2026** — **Ollama 0.32.14 schaltet Thinking per Default ein; ein Aufrufer, der `think` wegläßt, verliert den Großteil seiner Ausgabe in einen ungelesenen Kanal.** Gemessen an `gemma4-gpu` mit derselben Frage: ohne das Feld `content=214, thinking=1467` bei 425 Token — mit `think=false` `content=248, thinking=0` bei **60** Token. Der Bestand ist nicht betroffen (`services/llm_provider.py` setzt `"think": think` unbedingt), aber jeder neue Aufrufweg, der das Payload selbst baut, ist es. **Der Nebenbefund ist der Preis:** derselbe Inhalt kostet ohne das Feld das Siebenfache an Ausgabe-Token.

- **19.08.2026** — **Mehrfachvorhersage (MTP) ist in diesem System weder eingeschaltet noch einschaltbar noch in den Gewichten vorhanden — und ein Update änderte daran nichts.** Geprüft auf drei Ebenen: Der Bestand sendet keine Draft-Option; Ollama 0.20.7 kennt keine (vollständige Variablenliste durchgesehen); und in beiden GGUF-Blobs findet sich über `/api/show verbose` **kein einziger** Metadatenschlüssel mit `nextn`, `mtp`, `draft`, `specul` oder `predict` — 53 bzw. 56 Schlüssel geprüft. **Der Grund, warum ein Update es nicht bringt, steht in den Release Notes:** Jede der sieben Nennungen von MTP oder spekulativem Dekodieren hängt am **MLX-Runner**, also Apple Silicon (v0.23.1 *„supported on Macs"*, v0.31.1 *„on Apple Silicon"*, v0.32.6 *„on Apple GPUs"*). Diese Maschine fährt AMD unter Linux. **Nicht widerlegt ist die Aussage über die Modelle selbst:** MTP steckt in eigenen Varianten (`gemma4:31b-coding-mtp-bf16`), nicht in den normalen Q4-Quantisierungen.

- **18.08.2026** — **Der Verzeichnisbaum der Architektur kennt zwei Manager nicht, die seit Tagen laufen.** Beim Nachzug des Aufrufers aufgefallen: `plugins/` listet sieben Einträge; im Baum fehlen `dateien_wurzeln_manager/` (seit 18.08. vormittags) und `wissen_manager/` (seit dem 04.08.). **Beidseitig gezählt:** `ls server/plugins/` → 9 Verzeichnisse plus `base.py`, der Baum nennt 7. Dieselbe Klasse wie die drei Register vom selben Tag — ein Register, das seinen Gegenstand nicht kennt, und es fällt nur auf, wenn jemand daneben etwas einträgt.

- **18.08.2026** — **Der Architektur-Bauplan kennt einen Manager nicht und der veröffentlichte Compose-Bauplan vier Mounts nicht.** Beides beidseitig gezählt. **Manager:** `ls -d server/plugins/*_manager | wc -l` → **8**, die Tabelle in `novaberg-architecture.md` §4.5 trägt **7** Zeilen — `WissenManager` fehlt, seit er am 04.08.2026 entstand. **Mounts:** `docker-compose.template.yml` gibt dem `server`-Dienst **1** Volume, die betriebene `docker-compose.yml` hat **5** (`/app`, `/app/db:ro`, `/knowledge`, `/logs`, `/files:ro`). Die READMEs weisen an, das Template zu kopieren — wer das tut, bekommt ein System ohne Wissensspeicher, ohne dauerhaftes Log und mit einem Dateien-Dienst, der geschlossen ausfällt, weil `DATEIEN_AUSSENRAND` per Vorgabe auf `/files` steht und dort nichts liegt. **Drei der vier fehlenden Mounts sind älter als heute**, `files` kam am 18.08.2026 dazu. **Gefunden hat es die zweite Kontrolle über einen Zugriff, den der Bau nicht hatte** — den Diff zwischen veröffentlichtem Bauplan und betriebener Umgebung; kein Werkzeug des Nachzugs zieht ihn, weil das Template außerhalb jeder Bezeichner-Suche liegt.
