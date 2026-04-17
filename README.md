# Novaberg — The Nova Anima Resonance System

**A cognitive architecture for personal AI — with emergent personality, intrinsic curiosity, and emotional intelligence. Local, private, yours.**

🇩🇪 [Deutsche Version](README.de.md)

---

**Nova** is a local, privacy-focused personal AI assistant built around a cognitive architecture. Not a chatbot — a system of specialized agents, layered memory, emotional intelligence, and an autonomous background agent that keeps thinking when nobody is chatting.

**Core principle:** The LLM is a language processor, not a knowledge store. Real knowledge lives in PostgreSQL, Redis, and on the web. Intelligence emerges from simultaneous evaluation across specialized perspectives.

---

## Overview

Nova runs on two parallel graphs:

- **Human Graph** (foreground) — Perception → Router → Enricher → Planner → Agent-Dispatch → Conversational Vector → Responder → Tribunal. Responds to user input in real time.
- **Pixie Graph** (background) — the autonomous background agent. Handles promotion, decay, character distillation, reminders, research, and deepening. Runs competitively by priority.

Layered memory:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Short-term (STM) | Redis + vector search | Active thoughts, TTL-based |
| Long-term (LTM) | PostgreSQL | Consolidated memories with Ebbinghaus decay |
| Knowledge Graph | PostgreSQL | Entities, facts, bi-temporal model |
| Character Hash | PostgreSQL | Distilled personality profiles |

Multi-channel: Desktop client (PySide6) and Telegram bot share the same FastAPI server instance.

---

## Technology Stack

- **Backend:** Python 3.12, FastAPI, LangGraph, APScheduler
- **Databases:** PostgreSQL 16 with pgvector, Redis Stack
- **LLM:** Ollama (local) with Gemma 4 or Mistral Small 3.2; optional Anthropic Claude API
- **Embedding:** `nomic-embed-text` via Ollama
- **Search engine:** SearXNG (Docker)
- **Desktop client:** PySide6 with SSE pipeline visualization
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
  - Python 3.12 for the desktop client

### Model Footprint

Nova runs three language models plus one embedding model in parallel:

| Model | Execution | Purpose | Size |
|-------|----------|---------|------|
| `gemma4-gpu` | GPU (VRAM) | Chat, agents, responder | ~17 GB |
| `nomic-embed-text` | GPU (VRAM) | Embeddings for STM/LTM/entity resolution | ~0.6 GB |
| `gemma4-cpu` | CPU (RAM) | Pixie — language tasks in the background | ~17 GB |
| `qwen3-32b-cpu` | CPU (RAM) | Pixie — analysis tasks (promotion, research evaluation) | ~20 GB |

Both CPU models reside in RAM simultaneously, alongside PostgreSQL, Redis, and the server process. This is why 64 GB RAM is a requirement, not a recommendation. With less, the system will start swapping, which destroys Pixie throughput.

Ollama runs host-native by design so the GPU is directly accessible. Containerized services connect via `host.docker.internal`.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://codeberg.org/<user>/novaberg.git
cd novaberg
```

### 2. Set up the project directory

The repository goes inside a project directory alongside runtime files:

```
<project-directory>/
├── novaberg/             # cloned repository
├── searxng/              # SearXNG runtime state (create empty, populated on first start)
├── .env                  # secrets (generate from template)
└── docker-compose.yml    # (generate from template)
```

```bash
cd ..
mkdir searxng
cp novaberg/.env.template .env
cp novaberg/docker-compose.example.yml docker-compose.yml
```

### 3. Configure `.env`

Set at minimum:

- `TELEGRAM_BOT_TOKEN` — from [BotFather](https://t.me/BotFather)
- `TELEGRAM_USER_MAP` — your Telegram user ID (from [@userinfobot](https://t.me/userinfobot))
- `ANTHROPIC_API_KEY` — only if using `LLM_PROFILE=claude`

### 4. Set up Ollama

Two Ollama instances on different ports (GPU + CPU):

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve &    # GPU
OLLAMA_HOST=0.0.0.0:11435 ollama serve &    # CPU
```

Pull all four models:

```bash
# GPU — chat and embedding
ollama pull gemma4-gpu
ollama pull nomic-embed-text

# CPU — Pixie background work
ollama pull gemma4-cpu
ollama pull qwen3-32b-cpu
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
- Telegram bot (background)

### 6. Start the desktop client (optional)

```bash
cd novaberg/client
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## Configuration

Central configuration lives in `server/config.py`. All parameters can be overridden via environment variables (see `.env.template`).

**Key switches:**

| Variable | Values | Effect |
|----------|--------|--------|
| `LLM_PROFILE` | `lokal`, `claude` | Switch between Ollama and Anthropic API |
| `OLLAMA_CONNECTOR` | `mistral`, `gemma4` | Model stack within `lokal` |

Fine-grained parameters (Pixie intervals, STM thresholds, search limits, etc.) are also documented in `config.py` and controllable via `PIXIE_*`, `KZG_*`, `NOTIZEN_*` variables.

> **Security note (dev-only defaults):**
> Default values in `config.py` and `docker-compose.example.yml` contain PostgreSQL credentials `ki:ki`. These are intended for local development only. For any other deployment, set `POSTGRES_URL` / `POSTGRES_PASSWORD` to secure values in your `.env`. The `.env` file must never be committed to the repository.

---

## Documentation

The architecture is extensively documented in `Dokumentation/`:

- `nova-architecture.md` — System overview
- `nova-graph.md` — Human Graph pipeline
- `nova-pixie.md` — Background agent
- `nova-memory.md` — Memory layers
- `nova-ei.md` — Emotional intelligence
- `nova-node-*.md` — Individual pipeline nodes
- `nova-thinking-curiosity.md` — Curiosity and intrinsic motivation
- `nova-roadmap.md` — Project chronicle
- `nova-backlog.md` — Future concepts

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

Nova is under active development. Solo project, no external contributions planned. The roadmap in `Dokumentation/nova-roadmap.md` shows historical progress, `nova-backlog.md` lists open concepts.

---

## License
Licensed under the Apache License, Version 2.0.
