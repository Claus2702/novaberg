# Novaberg — The Nova Anima Resonance System

**A cognitive architecture for personal AI — with emergent personality, intrinsic curiosity, and emotional intelligence. Local, private, yours.**

🇩🇪 [Deutsche Version](README.de.md)

---

**Nova** is a local, privacy-focused personal AI assistant built around a cognitive architecture. Not a chatbot — a system of specialized agents, layered memory, emotional intelligence, and an autonomous background agent that keeps thinking when nobody is chatting. Nova develops her own interests, goals, and emotions that shape her conversations and thinking — with her own emotional stream alongside the user's.

**Core principle:** The LLM is a language processor, not a knowledge store. Real knowledge lives in PostgreSQL, Redis, and on the web. Intelligence emerges from simultaneous evaluation across specialized perspectives.

---

## Overview

A single conversational turn runs through **two** graphs, not one:

- **Human Graph** (5 nodes) — Perception → Enricher → EI-Calc → Salience → Dispatcher. Classifies what the user said, loads context, computes emotion and salience, and stores what is worth keeping. It deliberately produces no answer.
- **Character Graph** (18 nodes) — DB-Access → EI-Calc → Enricher → Emotional Gravitation → Reducer → Router → Planner → Agent-Dispatch → Conversational Vector → Responder → Thinker → Tribunal → Evaluate, then Nova's own perception, salience and storage. This is where the answer forms — and where Nova perceives and remembers her own turn the same way she does the user's.

The two are joined by a Redis event queue: the Human Graph leaves an event, a consumer starts a Character Graph run, and the answer reaches the client over a WebSocket. A third graph, the **Agent Graph** (3 nodes), handles turns that agents produce rather than people.

- **Pixie** (background) — the autonomous background agent. Sixteen agents compete by priority: promotion and decay across both memory layers, character distillation, reminders, research, calibration, knowledge gaps, timeline and notes.

Layered memory:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Short-term (STM) | Redis + vector search | Active thoughts, TTL-based |
| Long-term (LTM) | PostgreSQL | Consolidated memories with Ebbinghaus decay |
| Knowledge Graph | PostgreSQL | Entities, facts, bi-temporal model |
| Character Hash | PostgreSQL | Distilled personality profiles and the character wheels derived from them |

Multi-channel: Desktop client (GTK4) and Telegram bot share the same FastAPI server instance.

---

## Screenshots

### Chat — Cognitive Pipeline in Real Time

![Chat with pipeline stages](images/nova-ui-chat-1.png)

Every message passes through the full cognitive pipeline. The stage indicators below the conversation show each processing step as it happens: Perception classifies intent and emotion, the Router determines the processing path, the Enricher loads relevant context from memory, the Conversational Vector shapes Nova's own conversational intention, and the Responder generates the final answer. This is not decoration — it is the live trace of the cognitive pipeline: five nodes on the perception path, eighteen more on the path that forms the answer.

![Chat — clean conversation](images/nova-ui-chat-2.png)

The same conversation after the pipeline stages fade. Markdown rendering, native emoji support, and distinct visual separation between user and assistant messages. Nova's personality emerges from layered character distillation, not from a static system prompt.

### Emotional Intelligence — Plutchik Octagon

![Emotions panel with radar diagrams](images/nova-ui-emotion-2.png)

Nova's own emotional state across the 8 Plutchik sectors (Joy, Trust, Fear, Surprise, Sadness, Disgust, Anger, Anticipation) — the perspective selector switches between hers and the user's, and both are tracked separately throughout. Two radar diagrams compare the current session profile against the longer-run emotional landscape held in short-term memory. Below, all 16 canonical emotions are listed with their current values. The session radar shows what is happening now; the STM radar shows the emotional fingerprint across weeks of conversation.

### Session — Turn-Level Analysis

![Session panel](images/nova-ui-session-1.png)

Each conversation turn is stored with its analytical metadata: classified intent, detected emotion, and conversational mode. The summary at the top is auto-generated from the session context. This is the raw material the Enricher uses to build situational awareness for the Responder — visible here for calibration and debugging.

### Short-Term Memory (STM)

![STM panel](images/nova-ui-shorttermmemory-1.png)

Nova's short-term memory entries, shown here for user "nova" — Nova's own thoughts. Each entry carries a salience score, thematic tags, a dimension classification, and a TTL countdown. Entries above the promotion gate — 0.94 on the scale shown here, which is 0.7 before the salience curve is applied — are candidates for consolidation into long-term memory via the Pixie background agent. The content is Nova's own perspective: "For Nova, there is hardly anything better than a ripe tomato fresh from the bush."

### Long-Term Memory (LTM)

![LTM panel](images/nova-ui-longtermmemory-1.png)

Consolidated memories that survived the promotion process. Each entry has a weight (reinforced by retrieval — the Testing Effect), a knowledge dimension, and timestamps for creation and last reinforcement. This is the persistent layer — memories here decay according to the Ebbinghaus forgetting curve but are strengthened each time they are retrieved by the Enricher.

### Character — Emergent Personality Profiles

![Character panel — Nova's self-model](images/nova-ui-character-1.png)

Five distilled personality profiles, shown here for Nova herself. These are not hand-written descriptions but the output of Pixie's character distillation agent, which periodically compresses short-term and long-term memory into structured profiles. The Core profile captures who Nova has become; the Adaptive profile reflects her current preoccupations; Intentions and Emotions describe her communication patterns and emotional baseline; the Relationship profile models her perception of the user. All five layers feed into the Responder's identity block.

### Character Wheels — the part that acts

![Character panel — the two character wheels](images/nova-ui-character-2.png)

Two **character wheels** are derived from those profiles, and they are the part that acts rather than describes. Each asks a set of single questions against the distilled character — twelve for attachment, ten for initiative — which an LLM rates as absent, hinted or pronounced; the resulting factor is then *computed*, never estimated. Attachment weighs how much the other person's concerns count when Nova decides what to remember; initiative shifts the axis that decides who is leading the conversation.

Every rating is stored alongside the number, so each factor can be recalculated by hand — the spoke list under each chart is that derivation, not a decoration. The orange marker shows how far the result sits from the hub, scaled against the span on its own side. That matters: a wheel can land *exactly* on its neutral point while the shape leans clearly to one side, which means two groups of spokes are cancelling each other out. Both wheels therefore carry a provenance field, because a measured neutral value must not look like a value that was never taken at all.

### Conversational Vector — how Nova decides what kind of turn to make

![Conversational vector panel](images/nova-ui-vector-1.png)

Before the Responder writes anything, the conversation is placed in a space of 64 sectors grouped into 14 clusters, and the cluster decides which rhetorical strategies are even available. Here the sector is *Werkstatt* — a working, constructive register — and the seven strategies are ranked against it: two fit, two are rare, two are ruled out, and one is the cluster's core. The percentages are Nova's own affinity from her character; the labels are what the landscape permits. Where the two disagree, the landscape wins, and the panel says whether the corridor was kept.

Below it, the initiative axis is broken into the three measures it is computed from, plus the character offset from the wheel above. This is the number that decides whether Nova treats the turn as the user leading or herself leading — and the threshold beside it is the constant still in force, not the one the calibration agent has measured since.

The remaining blocks are the working material: knowledge gaps that qualified this turn, memories the gravitational pull brought in, and the tone the Responder is handed. Nothing here is written by a prompt. All of it is computed, and all of it is visible while it happens.

### Drive — goals that decay

![Goals panel](images/nova-ui-goals-1.png)

Nova's own long-term goals, each with the emotion that carries it and a motivation value that falls over time. Faded entries have decayed past the threshold and no longer pull. These are not configuration — they emerge from what she has been thinking about, and they feed back into what she finds worth remembering.

### Gravity Map — what pulls on what

![Gravity map panel](images/nova-ui-gravitation-1.png)

The same goals as a force-directed map, with the turns of the current conversation drawn against them. A line means the turn's embedding came close enough to a goal to exert pull; solid lines are long-term goals, dashed ones mid-term. The shaded regions are thematic clusters the goals fall into.

This is the clearest picture of why Nova remembers unevenly. A turn that lands inside a region she is already pulled toward is weighted differently from one that does not — not because a rule says so, but because the distance in the embedding space is smaller.

---

## Technology Stack

- **Backend:** Python, FastAPI, LangGraph, APScheduler
- **Databases:** PostgreSQL 16 with pgvector, Redis Stack
- **LLM:** Ollama (local) with Gemma 4 or Mistral Small 3.2; optional Anthropic Claude API
- **Embedding:** `nomic-embed-text-v2-moe` via Ollama
- **Search engine:** SearXNG (Docker)
- **Desktop client:** GTK4 (PyGObject) + WebKitGTK with SSE pipeline visualization
- **Chat integration:** Telegram Bot (long polling, whitelist)

---

## Requirements

- **OS:** Linux (developed on Nobara). Windows/Mac technically possible, untested.
- **Hardware:**
  - **GPU** with ≥ 24 GB VRAM (tested: AMD Radeon 7900 XTX)
  - **RAM** ≥ 64 GB — required, not merely recommended
  - **CPU** with many cores (tested: Ryzen 9 7900X3D)
- **Software:**
  - Docker + Docker Compose
  - Ollama (host-native, not containerized)
  - GTK4, WebKitGTK, PyGObject (pre-installed on Fedora/Nobara)

### Model Footprint

Nova runs three models in parallel — two language models and one for embeddings:

| Model | Execution | Purpose | Size |
|-------|----------|---------|------|
| `gemma4-gpu` | GPU (VRAM) | Chat, agents, responder | ~17 GB |
| `nomic-embed-text-v2-moe` | GPU (VRAM) | Embeddings for STM/LTM/entity resolution | ~1.0 GB |
| `qwen36-cpu` | CPU (RAM) | Pixie — everything in the background, language and analysis alike | ~24 GB |

Gemma runs on the GPU only. The background agent used to split its work across two CPU models, one for language and one for analysis; it now uses a single one for both, which is why the count went from four models to three.

The CPU model sits in RAM alongside PostgreSQL, Redis and the server process, and it is the large one. This is why 64 GB is a requirement rather than a recommendation — with less, the system starts swapping, and swapping destroys Pixie throughput.

Ollama runs host-native by design so the GPU is directly accessible. Containerized services connect via `host.docker.internal`.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Claus2702/novaberg.git
cd novaberg
```

### 2. Set up the project directory

The repository goes inside a project directory alongside runtime files:

```
<project-directory>/
├── novaberg/             # cloned repository
├── searxng/              # SearXNG runtime state (create empty, populated on first start)
├── matrix/               # Matrix runtime state — only for the Matrix channel (step 6)
│   ├── config/           #   AS registration + tokens (fill in from templates)
│   ├── data/             #   Synapse data, homeserver.yaml, signing key
│   └── state/            #   room id and avatar fingerprint (create empty)
├── .env                  # secrets (generate from template)
└── docker-compose.yml    # (generate from template)
```

```bash
cd ..
mkdir searxng
cp novaberg/.env.template .env
cp novaberg/docker-compose.template.yml docker-compose.yml

# Only if you want the Matrix channel (step 6):
cp -r novaberg/matrix matrix
mkdir -p matrix/state
```

### 3. Configure `.env`

Set at minimum:

- `ANTHROPIC_API_KEY` — only if using `LLM_PROFILE=claude`

The Telegram keys (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_USER_MAP`) are **no longer
required**: the Telegram channel was switched off on 2026-08-24 and the service
is gone from the Compose file. `telegram_bot/` is still in the repository — the
service is off, the code is not deleted. Set them only if you restore the
channel; the Compose block is commented in at its old place in
`docker-compose.template.yml`.

### 4. Set up Ollama

Two Ollama instances on different ports (GPU + CPU):

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve &    # GPU
OLLAMA_HOST=0.0.0.0:11435 ollama serve &    # CPU
```

Pull all three models:

```bash
# GPU — chat and embedding
ollama pull gemma4-gpu
ollama pull nomic-embed-text-v2-moe

# CPU — Pixie background work
ollama pull qwen36-cpu
```

Modelfiles (quantization, context size, system prompts) are in `ollama/modelfiles/` for reference.

### 5. Start services

```bash
docker compose up -d
```

Services:

- PostgreSQL on `:5432`
- Redis on `:6379`
- SearXNG on `:8080`
- Nova server on `:8000`
- Synapse on `:8008` and the Matrix connector — **only after step 6**; without
  it both containers restart in a loop

The Telegram channel was switched off on 2026-08-24 and is no longer part of
the stack. `telegram_bot/` is still in the repository — the service is off, the
code is not deleted, and the compose block sits as a comment in its old place.

### 6. Matrix channel (optional)

This is the remote channel: Nova reachable from a phone over a VPN, in a real
Matrix client. **It is not a bot.** A bot has exactly one sender, so anything
you type on the desktop would show up in the channel as `[Du] ...` out of
Nova's mouth. Novaberg registers an *application service* instead, which may
send in the name of any user in its namespace — so a desktop utterance appears
as a message from **you**, and Nova's answer as a message from **Nova**. The
reasoning is in `docs/novaberg-matrix-kanal_k.md`.

Four things have to exist before the first start. Nothing here is optional.

**a) The database.** Synapse insists on `C` collation, and this cannot be
changed later without rebuilding the database — do it now, not after the first
error:

```bash
docker compose up -d postgres
docker compose exec -T postgres psql -U ki -d postgres -c \
  "CREATE DATABASE synapse WITH OWNER ki TEMPLATE template0 LC_COLLATE='C' LC_CTYPE='C';"
```

**b) The homeserver config.** Let Synapse generate its secrets and signing key,
then put the template over it and copy the three generated values in:

```bash
docker run --rm -v "$(pwd)/matrix/data:/data" \
  -e SYNAPSE_SERVER_NAME=novaberg.de -e SYNAPSE_REPORT_STATS=no \
  ghcr.io/element-hq/synapse:latest generate

cp matrix/data/homeserver.template.yaml matrix/data/homeserver.yaml
# then edit: registration_shared_secret, macaroon_secret_key, form_secret
```

`server_name` sits inside **every** user and room id and cannot be changed
afterwards. Use a domain, not the host's address — the address comes from DHCP
and moves.

**c) The application service.** Two tokens, freely chosen but long, random and
different from each other. They go into **two** files: the homeserver reads one,
the connector the other, and if they disagree each side rejects the other.

```bash
cp matrix/config/novaberg-as.template.yaml matrix/config/novaberg-as.yaml
cp matrix/config/as-tokens.env.template     matrix/config/as-tokens.env
openssl rand -hex 32   # as_token  -> both files
openssl rand -hex 32   # hs_token  -> both files
```

**d) The two accounts.** One for you, one for Nova:

```bash
docker compose up -d synapse
docker compose exec -T synapse register_new_matrix_user \
  -c /data/homeserver.yaml -u meister -p '<password>' --no-admin
docker compose exec -T synapse register_new_matrix_user \
  -c /data/homeserver.yaml -u nova -p "$(openssl rand -base64 24)" --no-admin
```

Nova's password is never needed — the application service speaks for her
through its `as_token`. Yours is what you log in with.

Then `docker compose up -d` and point a client (FluffyChat, Fractal, Element)
at `http://<host>:8008`, logging in as `meister`. The room is created on the
connector's first run and its id is kept in `matrix/state/` — **without that
volume every restart creates a new room** and the old history stays behind
without anything raising an alarm.

Two things this setup does not do: there is **no TLS** in front of Synapse, so
outside a VPN tunnel your password and every message travel in the clear; and
`matrix/config/avatar-nova.png` is not shipped — drop any image there to give
the character a picture, or leave it out.

### 7. Start the desktop client (optional)

```bash
# Install dependencies (Fedora/Nobara — most are pre-installed)
sudo dnf install -y python3-requests python3-websocket-client python3-markdown

# Start
python3 novaberg/client/main.py
```

---

## Configuration

Central configuration lives in `server/config.py`. All parameters can be overridden via environment variables (see `.env.template`).

**Key switches:**

| Variable | Values | Effect |
|----------|--------|--------|
| `LLM_PROFILE` | `lokal`, `claude` | Switch between Ollama and Anthropic API |
| `OLLAMA_CONNECTOR` | `mistral`, `gemma4`, `qwen36` | Model stack within `lokal`. Default is `qwen36`, which is the set listed above. **The name refers to the background model, not the one that answers** — `gemma4` and `qwen36` both run Gemma on the GPU and differ only on the CPU side. The other two connectors expect CPU models that have to be built first. |

Fine-grained parameters (Pixie intervals, STM thresholds, search limits, etc.) are also documented in `config.py` and controllable via `PIXIE_*`, `KZG_*`, `NOTIZEN_*` variables.

> **Security note (dev-only defaults):**
> Default values in `config.py` and `docker-compose.template.yml` contain PostgreSQL credentials `ki:ki`. These are intended for local development only. For any other deployment, set `POSTGRES_URL` / `POSTGRES_PASSWORD` to secure values in your `.env`. The `.env` file must never be committed to the repository.

---

## Documentation

The architecture is extensively documented in `docs/`:

- `novaberg-architecture.md` — System overview
- `novaberg-graph.md` — Graph architecture and pipeline
- `novaberg-pixie.md` — Background agent
- `novaberg-memory.md` — Memory layers
- `novaberg-ei.md` — Emotional intelligence
- `novaberg-node-*.md` — Individual pipeline nodes (23 documents)
- `novaberg-thinking-curiosity_k.md` — Curiosity and intrinsic motivation
- `novaberg-thinking-drive_k.md` — Drive, goals, and dual-emotion architecture
- `novaberg-roadmap.md` — Project chronicle
- `novaberg-backlog.md` — Future concepts

Architecture documents are in German with English module names.

---

## Troubleshooting

**Ollama unreachable from container:**
Check if `host.docker.internal` resolves. On Linux, `extra_hosts: - "host.docker.internal:host-gateway"` is needed in the Compose file (already included).

**SearXNG returns no results:**
Engines may be blocked by rate limits. Edit the settings file at `searxng/settings.yml` — SearXNG generates it on first start.

**PostgreSQL connection fails:**
The server uses `depends_on.postgres.condition: service_healthy`. If the health check fails, check whether port 5432 is already in use on the host.

**Gemma 4 JSON output truncated:**
Known issue (Ollama #15260). Workaround is implemented in the code (cleanup pipeline in `config.py`).

---

## Status

Nova is under active development. Solo project, no external contributions planned. The roadmap in `docs/novaberg-roadmap.md` shows historical progress, `novaberg-backlog.md` lists open concepts.

---

## License
Licensed under the Apache License, Version 2.0.
