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
    PIXIE_INTERVALL_MIN, PIXIE_AKTIV, shutdown_event,
    DEFAULT_USER_ID, ASSISTANT_USER_ID,
)
from services.llm_provider import init_providers
from graph.builder              import build_human_graph, build_agent_graph, build_character_graph

# API-Router
from api.health                 import router as health_router,      ollama_testen, redis_testen, postgres_testen
from api.chat                   import router as chat_router, entitaeten_embeddings_sicherstellen
from memory.ziele               import ziele_embeddings_sicherstellen
from api.gedaechtnis            import router as gedaechtnis_router
from api.session                import router as session_router
from api.websocket              import router as websocket_router, aktive_verbindungen
from api.admin                  import router as admin_router
from api.drive                  import router as drive_router

from services.shadow_delivery   import shadow_delivery_loop
from services.event_consumer    import event_consumer_loop

logger    = logging.getLogger("ki_server")
scheduler = AsyncIOScheduler()


def schema_migrieren(postgres_url: str) -> None:
    """Stellt sicher, dass alle Schema-Erweiterungen vorhanden sind (idempotent)."""

    migrationen: list[str] = [
        # langzeitgedaechtnis
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS arousal DOUBLE PRECISION NOT NULL DEFAULT 0.5",
        # emotions_vektor entfernt (PROMO-CLUSTER-EI): Trajektorie passt
        # semantisch nicht zu einer verdichteten LZG-Erinnerung.
        "ALTER TABLE langzeitgedaechtnis DROP COLUMN IF EXISTS emotions_vektor",
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
        # charakter_hash — Paar-Schema (Chat 66)
        "ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS character_id TEXT NOT NULL DEFAULT ''",
        # Bestehende Daten: user_id='meister' gehoert zu character_id='nova' und umgekehrt
        f"UPDATE charakter_hash SET character_id = '{ASSISTANT_USER_ID}' WHERE user_id = '{DEFAULT_USER_ID}' AND character_id = ''",
        f"UPDATE charakter_hash SET character_id = '{DEFAULT_USER_ID}' WHERE user_id = '{ASSISTANT_USER_ID}' AND character_id = ''",
        # PK auf Paar erweitern (nur wenn noch alter PK)
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'charakter_hash_pkey'
                AND conrelid = 'charakter_hash'::regclass
            ) THEN
                ALTER TABLE charakter_hash DROP CONSTRAINT charakter_hash_pkey;
                ALTER TABLE charakter_hash ADD CONSTRAINT charakter_hash_pkey PRIMARY KEY (user_id, character_id);
            END IF;
        END $$
        """,
        # hintergrund_log
        "ALTER TABLE hintergrund_log ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'offen'",
        "ALTER TABLE hintergrund_log ADD COLUMN IF NOT EXISTS verarbeitet_am TIMESTAMPTZ",
        # Ebbinghaus-Decay (E1)
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS aktiv BOOLEAN NOT NULL DEFAULT TRUE",
        # Paar-Schema (Chat 62): Gespraech = (user_id, character_id) + Beobachter
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS character_id VARCHAR(50) NOT NULL DEFAULT 'nova'",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS beobachter VARCHAR(20) NOT NULL DEFAULT 'user'",
        # Nova-Eintraege (user_id='nova') ins Paar meister:nova mit Beobachter 'assistant' umschreiben.
        # Idempotent: nach erstem Lauf matcht WHERE nichts mehr.
        "UPDATE langzeitgedaechtnis SET user_id = 'meister', character_id = 'nova', beobachter = 'assistant' WHERE user_id = 'nova'",
        # Partial-Index auf das Paar — loest den alten aktiv-only-Index ab.
        "DROP INDEX IF EXISTS idx_lzg_aktiv",
        "CREATE INDEX IF NOT EXISTS idx_lzg_aktiv ON langzeitgedaechtnis (user_id, character_id) WHERE aktiv = TRUE",
        # M2: Magnet-Spalten LZG (Chat 78 — Spiegelung von db/init.sql).
        # Schiene fuer M3 (Promotion-Code) und M5 (Salienz-Pfad).
        # Alle Spalten bewusst nullable — Befuellung gestaffelt ueber M3, M4, M5.
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS themen TEXT[]",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS gedaechtnistyp VARCHAR(20)",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS kzg_erstellt_am TIMESTAMPTZ",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS entitaet_ids INTEGER[]",
        "ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS timeline_id INTEGER REFERENCES timeline(id) ON DELETE SET NULL",
        "CREATE INDEX IF NOT EXISTS idx_lzg_themen ON langzeitgedaechtnis USING GIN (themen)",
        "CREATE INDEX IF NOT EXISTS idx_lzg_entitaet_ids ON langzeitgedaechtnis USING GIN (entitaet_ids)",
        "CREATE INDEX IF NOT EXISTS idx_lzg_kzg_erstellt_am ON langzeitgedaechtnis (kzg_erstellt_am)",
        "CREATE INDEX IF NOT EXISTS idx_lzg_timeline_id ON langzeitgedaechtnis (timeline_id)",
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
        # Ziele-Tabelle (Drive, Chat 68)
        """
        CREATE TABLE IF NOT EXISTS ziele (
            id              SERIAL PRIMARY KEY,
            user_id         VARCHAR(50) NOT NULL DEFAULT 'nova',
            ziel_typ        VARCHAR(20) NOT NULL DEFAULT 'mittelfristig',
            zielsatz        TEXT NOT NULL,
            motivation      DOUBLE PRECISION NOT NULL DEFAULT 0.5,
            emotion         VARCHAR(30) NOT NULL DEFAULT '',
            arousal         DOUBLE PRECISION NOT NULL DEFAULT 0.5,
            embedding       vector(768),
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            erstellt_am     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            aktualisiert_am TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_ziele_aktiv ON ziele (user_id) WHERE aktiv = TRUE",
        # Themen-Stichwort fuer den Gravitationsgraph (Region-Label)
        "ALTER TABLE ziele ADD COLUMN IF NOT EXISTS thema VARCHAR(100) NOT NULL DEFAULT ''",
        # Seed-Ziele für Nova (idempotent — nur einfügen wenn Tabelle leer)
        """
        INSERT INTO ziele (user_id, ziel_typ, zielsatz, motivation, emotion, arousal)
        SELECT 'nova', 'langfristig',
               'Ich möchte die Verbindungen zwischen Natur und menschlicher Kultur verstehen — wie Pflanzen, Jahreszeiten und Landschaften das Leben der Menschen formen.',
               0.8, 'neugierig', 0.6
        WHERE NOT EXISTS (SELECT 1 FROM ziele WHERE user_id = 'nova' AND ziel_typ = 'langfristig')
        """,
        """
        INSERT INTO ziele (user_id, ziel_typ, zielsatz, motivation, emotion, arousal)
        SELECT 'nova', 'langfristig',
               'Ich möchte meinen Menschen wirklich kennenlernen — seine Gedanken, seine Sorgen, was ihn antreibt und was ihn glücklich macht.',
               0.9, 'neugierig', 0.5
        WHERE NOT EXISTS (SELECT 1 FROM ziele WHERE user_id = 'nova' AND ziel_typ = 'langfristig' AND id > 1)
        """,
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

    # Event-Loop-Referenz für synchrone Endpoints (broadcast_threadsafe)
    app.state.loop = asyncio.get_running_loop()

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
        ziele_embeddings_sicherstellen(POSTGRES_URL, ollama_gpu_client, EMBED_MODEL)

    # Epic 11: Agent-Discovery
    from agents import discover_agents, AgentRegistry
    discover_agents()
    for agent in AgentRegistry.alle().values():
        agent.setup(POSTGRES_URL)
    logger.info(f"Agent-Discovery: {len(AgentRegistry.alle())} Agenten registriert")

    # Periodische Pixie-Aufgaben registrieren (aus Agent periodic_task())
    if PIXIE_AKTIV:
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
    else:
        logger.debug("main: Periodic-Task-Discovery uebersprungen (PIXIE_AKTIV=False)")

    # Scheduler starten — Pixie-Heartbeat (kompetitives Scheduling)
    from config import PIXIE_INTERVALL_SEKUNDEN

    if PIXIE_AKTIV:
        from services.pixie.scheduler import pixie_heartbeat

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
    else:
        logger.debug("main: Pixie-Heartbeat-Job uebersprungen (PIXIE_AKTIV=False)")
        logger.info("Pixie-Master-Switch: AKTIV=False — alle Pixie-Pfade ruhen")

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

    compiled_character, character_graph = build_character_graph(
        embed_client = ollama_gpu_client,
        embed_model  = EMBED_MODEL,
        redis_client = redis_client,
        postgres_url = POSTGRES_URL,
    )
    app.state.character_graph          = character_graph
    app.state.compiled_character_graph = compiled_character
    logger.info("CharacterGraph initialisiert.")

    # ── NEU: Shadow Delivery Service starten ──
    if PIXIE_AKTIV:
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
    else:
        delivery_task = None
        logger.debug("main: Shadow Delivery Service uebersprungen (PIXIE_AKTIV=False)")

    # ── Event-Consumer starten ──
    consumer_task = asyncio.create_task(
        event_consumer_loop(
            redis_client       = redis_client,
            character_graph    = character_graph,
            compiled_character = compiled_character,
            websocket_map      = aktive_verbindungen,
            llm_lock           = llm_lock,
        )
    )
    logger.info("Event-Consumer gestartet.")

    yield

    # ── Shutdown: Event setzen, dann aufräumen ──
    shutdown_event.set()
    if PIXIE_AKTIV:
        scheduler.shutdown(wait=False)
    if delivery_task is not None:
        delivery_task.cancel()
    consumer_task.cancel()
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
app.include_router(drive_router)
