"""
KI-Server — Einstiegspunkt.
FastAPI + APScheduler + Router-Integration.
"""

import logging
import asyncio

from contextlib import asynccontextmanager

from fastapi                        import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import (
    redis_client, ollama_gpu_client, ollama_cpu_client, llm_lock,
    OLLAMA_MODEL, OLLAMA_GPU_NUM_CTX, OLLAMA_CPU_NUM_CTX,
    SHADOW_MODEL, EMBED_MODEL, POSTGRES_URL,
    LLM_PROFILE, ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    PIXIE_ANALYSE_MODEL, PIXIE_ANALYSE_NUM_CTX,
    PIXIE_INTERVALL_MIN, shutdown_event,
)
from services.llm_provider import init_providers
from graph.builder              import build_human_graph, build_agent_graph
from services.shadow_agent      import schatten_arbeit_ausfuehren, discover_tasks

# API-Router
from api.health                 import router as health_router,      ollama_testen, redis_testen, postgres_testen
from api.chat                   import router as chat_router, entitaeten_embeddings_sicherstellen
from api.gedaechtnis            import router as gedaechtnis_router
from api.session                import router as session_router
from api.websocket              import router as websocket_router, aktive_verbindungen
from api.admin                  import router as admin_router

from services.shadow_delivery   import shadow_delivery_loop

logger        = logging.getLogger("ki_server")
scheduler     = AsyncIOScheduler()
task_registry = {}


def schema_migrieren(postgres_url: str) -> None:
    """Stellt sicher, dass alle Schema-Erweiterungen vorhanden sind (idempotent)."""

    migrationen: list[str] = [
        # langzeitgedaechtnis
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS arousal DOUBLE PRECISION NOT NULL DEFAULT 0.5",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS emotions_vektor TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS intentionen TEXT NOT NULL DEFAULT '[]'",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS emotion TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS modus TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS sprach_stil TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS beziehungs_dynamik TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS tone TEXT NOT NULL DEFAULT ''",
        # charakter_hash
        "ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS intentions_profil TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS emotions_profil TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beziehungsprofil TEXT NOT NULL DEFAULT ''",
        # hintergrund_log
        "ALTER TABLE hintergrund_log ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'offen'",
        "ALTER TABLE hintergrund_log ADD COLUMN IF NOT EXISTS verarbeitet_am TIMESTAMPTZ",
        # Ebbinghaus-Decay (E1)
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS aktiv BOOLEAN NOT NULL DEFAULT TRUE",
        "CREATE INDEX IF NOT EXISTS idx_lzg_aktiv ON langzeitgedaechtnis (aktiv) WHERE aktiv = TRUE",
        # M2: Entitäten + Fakten Tabellen
        # CREATE TABLE IF NOT EXISTS wird in init.sql behandelt.
        # DROP alter Tabellen + Neuanlage ebenfalls in init.sql (Migrations-Block).
        # Hier nur zukünftige ALTER TABLE Migrationen.
        # M5: Timeline-Erweiterungen
        "ALTER TABLE timeline ADD COLUMN IF NOT EXISTS aktiv BOOLEAN NOT NULL DEFAULT TRUE",
        "ALTER TABLE timeline ADD COLUMN IF NOT EXISTS last_touched TIMESTAMPTZ NOT NULL DEFAULT NOW()",
        "ALTER TABLE timeline ADD COLUMN IF NOT EXISTS wiedervorlage_am TIMESTAMPTZ",
        "ALTER TABLE timeline ADD COLUMN IF NOT EXISTS entitaet_ids INTEGER[]",
        # M6: Notizen-Erweiterungen
        "ALTER TABLE notizen ADD COLUMN IF NOT EXISTS zusammenfassung VARCHAR(200)",
        "ALTER TABLE notizen ADD COLUMN IF NOT EXISTS themen TEXT[]",
        "ALTER TABLE notizen ADD COLUMN IF NOT EXISTS entitaet_ids INTEGER[]",
        "ALTER TABLE notizen ADD COLUMN IF NOT EXISTS aktiv BOOLEAN NOT NULL DEFAULT TRUE",
        "ALTER TABLE notizen ADD COLUMN IF NOT EXISTS last_touched TIMESTAMPTZ NOT NULL DEFAULT NOW()",
        "ALTER TABLE notizen ADD COLUMN IF NOT EXISTS wiedervorlage_am TIMESTAMPTZ",
        "ALTER TABLE notizen ADD COLUMN IF NOT EXISTS suchtext TSVECTOR",
    ]

    import psycopg2

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()
        for sql in migrationen:
            cursor.execute(sql)
        conn.commit()
        conn.close()
        logger.info(f"Schema-Migration: {len(migrationen)} Statements ausgeführt.")
    except Exception as fehler:
        logger.warning(f"Schema-Migration fehlgeschlagen: {fehler}")


# ─────────────────────────────────────────────
# Shadow Agent (Scheduler-Job)
# ─────────────────────────────────────────────
async def PixieArbeit():
    """Pixie — Legacy Background-Worker auf CPU (wird durch Heartbeat ersetzt)."""
    if shutdown_event.is_set():
        return
    logger.info("Pixie-Legacy: Starte...")
    try:
        verarbeitet: int = await asyncio.to_thread(
            schatten_arbeit_ausfuehren,
            redis_client   = redis_client,
            postgres_url   = POSTGRES_URL,
            embed_client   = ollama_gpu_client,
            embed_model    = EMBED_MODEL,
            task_registry  = task_registry,
            shutdown_event = shutdown_event,
        )
        logger.info(f"Pixie-Legacy: {verarbeitet} Aufträge verarbeitet.")
    except Exception as fehler:
        logger.error(f"Pixie-Legacy: Fehler — {fehler}")


# ─────────────────────────────────────────────
# Lifespan (Start / Stop)
# ─────────────────────────────────────────────
@asynccontextmanager
async def Lifespan(app: FastAPI):
    # Health-Check-Spam aus dem Access-Log filtern
    class HealthCheckFilter(logging.Filter):
        def filter(self, record):
            return "/health" not in record.getMessage()

    logging.getLogger("uvicorn.access").addFilter(HealthCheckFilter())

    logger.info("Server startet...")

    # LLM-Provider initialisieren (Ollama oder Claude)
    init_providers(
        profile               = LLM_PROFILE,
        ollama_gpu_client     = ollama_gpu_client,
        ollama_cpu_client     = ollama_cpu_client,
        ollama_gpu_model      = OLLAMA_MODEL,
        ollama_cpu_model      = SHADOW_MODEL,
        ollama_gpu_num_ctx    = OLLAMA_GPU_NUM_CTX,
        ollama_cpu_num_ctx    = OLLAMA_CPU_NUM_CTX,
        anthropic_api_key     = ANTHROPIC_API_KEY,
        anthropic_model       = ANTHROPIC_MODEL,
        pixie_analyse_model   = PIXIE_ANALYSE_MODEL,
        pixie_analyse_num_ctx = PIXIE_ANALYSE_NUM_CTX,
    )

    # Verbindungstests
    ollama_ok:   bool = ollama_testen()
    redis_ok:    bool = redis_testen()
    postgres_ok: bool = postgres_testen()

    if not all([redis_ok, postgres_ok]):
        logger.error("Kritische Verbindung fehlgeschlagen — degradierter Modus.")

    # Schema-Migrationen (idempotent)
    if postgres_ok:
        schema_migrieren(POSTGRES_URL)

    if not ollama_ok:
        logger.warning("Ollama nicht bereit — Antworten nicht möglich bis Modell geladen.")

    # Embedding-Repair: Entitäten ohne Embedding nachträglich versorgen
    if postgres_ok and ollama_ok:
        entitaeten_embeddings_sicherstellen()

    # Task-Registry initialisieren
    global task_registry
    task_registry = discover_tasks()
    logger.info(f"Pixie: {len(task_registry)} Tasks registriert.")

    # Epic 11: Agent-Discovery
    from agents import discover_agents, AgentRegistry
    discover_agents()
    for agent in AgentRegistry.alle().values():
        agent.setup(POSTGRES_URL)
    logger.info(f"Agent-Discovery: {len(AgentRegistry.alle())} Agenten registriert")

    # Periodische Pixie-Aufgaben registrieren (aus Agent periodic_task())
    import time as _time
    for _agent in AgentRegistry.alle().values():
        _task = _agent.periodic_task()
        if _task:
            _key = f"pixie:schedule:{_task.name}"
            if not redis_client.exists(_key):
                redis_client.hset(_key, mapping={
                    "priority":    str(_task.priority),
                    "interval":    str(_task.interval),
                    "next_run":    str(_time.time()),
                    "description": _task.description,
                })
                logger.info(
                    f"Pixie: Periodische Aufgabe registriert — {_task.name} "
                    f"(Prio {_task.priority}, alle {_task.interval}s)"
                )

    # Scheduler starten — Pixie-Heartbeat (kompetitives Scheduling)
    from services.pixie.scheduler import pixie_heartbeat
    from config import PIXIE_INTERVALL_SEKUNDEN

    async def _pixie_job():
        await pixie_heartbeat(app.state)

    scheduler.add_job(
        _pixie_job,
        trigger       = "interval",
        seconds       = PIXIE_INTERVALL_SEKUNDEN,
        id            = "pixie_heartbeat",
        name          = "Pixie Heartbeat",
        max_instances = 1,
        coalesce      = True,
    )

    scheduler.start()
    logger.info(f"Scheduler gestartet (Pixie-Heartbeat: {PIXIE_INTERVALL_SEKUNDEN}s).")

    # Graphen kompilieren
    compiled_human, human_graph = build_human_graph(
        embed_client = ollama_gpu_client,
        embed_model  = EMBED_MODEL,
        redis_client = redis_client,
        postgres_url = POSTGRES_URL,
    )
    app.state.conversation_graph = compiled_human
    app.state.human_graph        = human_graph
    logger.info("HumanGraph initialisiert.")

    compiled_agent, agent_graph = build_agent_graph(
        embed_client = ollama_gpu_client,
        embed_model  = EMBED_MODEL,
        redis_client = redis_client,
        postgres_url = POSTGRES_URL,
    )
    app.state.agent_graph          = agent_graph
    app.state.compiled_agent_graph = compiled_agent
    logger.info("AgentGraph initialisiert.")

    # ── NEU: Shadow Delivery Service starten ──
    delivery_task = asyncio.create_task(
        shadow_delivery_loop(
            redis_client         = redis_client,
            embed_client         = ollama_gpu_client,
            embed_model          = EMBED_MODEL,
            websocket_map        = aktive_verbindungen,
            llm_lock             = llm_lock,
            compiled_agent_graph = compiled_agent,
            agent_graph          = agent_graph,
        )
    )
    logger.info("Shadow Delivery Service gestartet.")

    yield

    # ── Shutdown: Event setzen, dann aufräumen ──
    shutdown_event.set()
    scheduler.shutdown(wait=False)
    delivery_task.cancel()
    logger.info("Server gestoppt.")


# ─────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────
app = FastAPI(
    title       = "KI-Server",
    description = "Persönlicher KI-Assistent mit Gedächtnis und Hintergrund-Rauschen",
    version     = "0.3.0",
    lifespan    = Lifespan,
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(gedaechtnis_router)
app.include_router(session_router)
app.include_router(websocket_router)
app.include_router(admin_router)
