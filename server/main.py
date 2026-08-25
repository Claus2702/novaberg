"""
KI-Server — Einstiegspunkt.
FastAPI + APScheduler + Router-Integration.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from api.admin import router as admin_router
from api.chat import entitaeten_embeddings_sicherstellen
from api.chat import router as chat_router
from api.drive import router as drive_router
from api.gedaechtnis import router as gedaechtnis_router
from api.health import ollama_testen, postgres_testen, redis_testen

# API-Router
from api.health import router as health_router
from api.session import router as session_router
from api.websocket import aktive_verbindungen
from api.websocket import router as websocket_router
from config import (
    AKTIVES_PAAR_USER_ID,
    ASSISTANT_USER_ID,
    NMCP_ABGLEICH_INTERVALL_SEKUNDEN,
    PIXIE_AKTIV,
    POSTGRES_URL,
    llm_lock,
    redis_client,
    shutdown_event,
)
from graph.builder import build_agent_graph, build_character_graph, build_human_graph
from memory.pipeline_log import (
    init_buffer as pipeline_log_init,
)
from memory.pipeline_log import (
    writer_loop as pipeline_log_writer,
)
from memory.ziele import ziele_embeddings_sicherstellen
from services.event_consumer import event_consumer_loop
from services.prompt_consumer import prompt_consumer_loop
from services.shadow_delivery import shadow_delivery_loop

logger    = logging.getLogger("ki_server")
scheduler = AsyncIOScheduler()


def _sql_init_pfad_finden() -> Path:
    """Findet db/init.sql relativ zu dieser Datei.

    Container-Layout: /app/main.py mit Mount /app/db/init.sql.
    Host-Layout: novaberg/server/main.py mit ../db/init.sql.
    """
    hier: Path = Path(__file__).resolve().parent
    for kandidat in (hier / "db" / "init.sql", hier.parent / "db" / "init.sql"):
        if kandidat.exists():
            return kandidat
    return hier / "db" / "init.sql"  # Default fuers Logging im Fehlerfall


SQL_INIT_PFAD: Path = _sql_init_pfad_finden()


def schema_migrieren(postgres_url: str) -> None:
    """Migration: führt db/init.sql gegen die bestehende Live-Datenbank aus.

    db/init.sql ist Single Source of Truth für das Postgres-Schema und enthält
    alle Statements idempotent (CREATE ... IF NOT EXISTS, ALTER ... IF NOT
    EXISTS, INSERT ... WHERE NOT EXISTS, DO-Blöcke mit pg_constraint-Check).

    EVA
    ---
    E: postgres_url muss erreichbar sein. db/init.sql muss am erwarteten Pfad
       (server/../db/init.sql) liegen.
    V: SQL-Inhalt einmalig laden und gegen Postgres mit autocommit=True
       ausführen, damit DO-Blöcke und unabhängige Statements korrekt
       transaktioniert werden.
    A: info-Log mit Pfad und einer groben Statement-Zahl (Semikolon-Zählung).
       Bei Fehler warning-Log und Rückkehr ohne Re-Raise — Fail-Mode wie
       bisher in P0.
    """
    if not SQL_INIT_PFAD.exists():
        logger.warning(f"Migration: db/init.sql nicht gefunden unter {SQL_INIT_PFAD}")
        return

    sql_inhalt: str = SQL_INIT_PFAD.read_text(encoding="utf-8")
    anzahl_stmts: int = sql_inhalt.count(";")

    import psycopg2

    try:
        conn = psycopg2.connect(postgres_url)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql_inhalt)
        conn.close()
        logger.info(
            f"Migration: db/init.sql ausgeführt "
            f"({anzahl_stmts} Statements geparst, Pfad {SQL_INIT_PFAD})."
        )
    except Exception as fehler:
        logger.warning(f"Migration: db/init.sql fehlgeschlagen — {fehler}")


# ─────────────────────────────────────────────
# Lifespan (Start / Stop)
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Health-Check-Spam aus dem Access-Log filtern
    class HealthCheckFilter(logging.Filter):
        def filter(self, record):
            return "/health" not in record.getMessage()

    logging.getLogger("uvicorn.access").addFilter(HealthCheckFilter())

    logger.info("Server startet...")

    # Das Paar, fuer das die Hintergrundarbeit dieses Laufs stattfindet. Steht
    # hier, weil es sonst von aussen nicht feststellbar ist: Wird die Umgebung
    # fuer eine Messreihe umgestellt und greift die Umstellung nicht — etwa
    # weil `docker compose restart` den Behaelter neu startet, ohne ihn neu zu
    # erzeugen —, laeuft die Reihe dreissig Turns lang gegen das falsche Paar,
    # und nichts meldet es. Ein Wert, den niemand ablesen kann, ist keine
    # Konfiguration, sondern eine Annahme.
    logger.info(
        f"Aktives Paar: ({AKTIVES_PAAR_USER_ID}, {ASSISTANT_USER_ID}) — "
        f"Pixie bedient beide Seiten dieses Paares, sonst niemanden"
    )

    # Event-Loop-Referenz für synchrone Endpoints (broadcast_threadsafe)
    app.state.loop = asyncio.get_running_loop()

    # Pipeline-Log-Buffer initialisieren (Forensik-Infrastruktur).
    # Muss vor dem ersten Helper-Aufruf passieren, der spätestens im
    # Enricher des ersten Konversations-Turns kommt.
    pipeline_log_init(app.state.loop)

    # Model-Service-Worker starten (Phase 2: EmbedWorker)
    from services.model_services import model_service
    await model_service.startup()

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
        await entitaeten_embeddings_sicherstellen()
        await ziele_embeddings_sicherstellen(POSTGRES_URL)

    # Epic 11: Agent-Discovery
    from agents import AgentRegistry, discover_agents
    discover_agents()
    for agent in AgentRegistry.alle().values():
        agent.setup(POSTGRES_URL)
    logger.info(f"Agent-Discovery: {len(AgentRegistry.alle())} Agenten registriert")

    # NMCP-Handshake: Naht herstellen und Kompatibilitaet pruefen.
    #
    # Das ist der einzige Zeitpunkt mit einem echten Verweigerungsrecht —
    # zur Laufzeit kann niemand nein sagen, ohne das Gespraech anzuhalten.
    # Die Ablehnung trifft den einzelnen Dienst und NICHT das System: Ein
    # fehlerhaft angemeldetes Plugin darf den Start nicht verhindern.
    from agents.nmcp import anmelden, gesamtbild_pruefen
    _befunde = {}
    for _agent in AgentRegistry.alle().values():
        try:
            _befunde[_agent.name] = anmelden(_agent)
        except (TypeError, ValueError) as _fehler:
            logger.error(
                f"NMCP: Dienst '{_agent.name}' nicht anmeldbar "
                f"({type(_fehler).__name__}: {_fehler}) — nicht eingebunden"
            )

    _nicht = [b.name for b in _befunde.values() if not b.eingebunden]
    _ohne_zweifel = [
        b.name for b in _befunde.values()
        if b.eingebunden and not b.zweifel_erlaubt
    ]
    logger.info(
        f"NMCP-Handshake: {len(_befunde)} geprueft, "
        f"{len(_befunde) - len(_nicht)} eingebunden, "
        f"{len(_nicht)} verweigert, {len(_ohne_zweifel)} ohne Zweifelsfaelle"
    )
    # Eine verweigerte Einbindung muss zur LAUFZEIT sichtbar bleiben, nicht
    # nur hier. Eine Startmeldung ist nach zehn Minuten aus dem Blick, und
    # danach verhaelt sich der fehlende Dienst wie einer, den niemand
    # braucht — genau der stille Zustand, gegen den der Quotenabgleich
    # gebaut ist. `/health` rechnet den Befund dafuer neu, statt diesen
    # Startzustand mitzuschleppen: ein Schnappschuss altert.
    if _nicht:
        logger.error(f"NMCP: NICHT eingebunden — {_nicht}")
    if _ohne_zweifel:
        logger.warning(
            f"NMCP: ohne Zweifelsfaelle (vierter Ausgang fehlt) — {_ohne_zweifel}"
        )

    for _meldung in gesamtbild_pruefen(AgentRegistry.alle()):
        logger.warning(f"NMCP-Gesamtbild [{_meldung.regel}]: {_meldung.text}")

    # Periodische Pixie-Aufgaben registrieren (aus Agent periodic_task())
    if PIXIE_AKTIV:
        import time as _time
        for _agent in AgentRegistry.alle().values():
            _task = _agent.periodic_task()

            # Ein Agent, der keine periodische Aufgabe (mehr) meldet, darf keinen
            # Zeitplan-Eintrag zuruecklassen. Ein solcher Zombie bleibt faellig,
            # wird bei jedem Heartbeat als Kandidat gesammelt und waechst seit dem
            # Aging (Chat 113) bis zum Deckel — er gewaenne dann jeden Zyklus,
            # ohne je zu laufen. Abschalten muss den Kandidaten entfernen, nicht
            # nur seine Wirkung.
            if not _task:
                _zombie = f"pixie:schedule:{_agent.name}"
                if redis_client.delete(_zombie):
                    logger.info(
                        f"Pixie: Zeitplan entfernt — {_agent.name} meldet keine "
                        f"periodische Aufgabe mehr (Kandidat abgemeldet)"
                    )
                continue

            if _task:
                _key = f"pixie:schedule:{_task.name}"
                _neu: bool = not redis_client.exists(_key)

                # Takt und Prioritaet folgen der Konfiguration, next_run nicht.
                # Bis Chat 111 wurde der Eintrag nur beim ersten Mal geschrieben
                # — eine Aenderung an config.py erreichte das laufende System
                # dann nie, und niemand sah warum. next_run bleibt stehen, sonst
                # rutschte jeder Neustart den Takt nach vorn.
                if _neu:
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
                    _alt_intervall = redis_client.hget(_key, "interval")
                    _alt_prio      = redis_client.hget(_key, "priority")
                    redis_client.hset(_key, mapping={
                        "priority":    str(_task.priority),
                        "interval":    str(_task.interval),
                        "description": _task.description,
                    })
                    if (_alt_intervall and str(_alt_intervall) != str(_task.interval)) or \
                       (_alt_prio and str(_alt_prio) != str(_task.priority)):
                        logger.info(
                            f"Pixie: Zeitplan angeglichen — {_task.name}: "
                            f"Takt {_alt_intervall}s -> {_task.interval}s, "
                            f"Prio {_alt_prio} -> {_task.priority}"
                        )
    else:
        logger.debug("main: Periodic-Task-Discovery uebersprungen (PIXIE_AKTIV=False)")

    # Scheduler starten — Pixie-Heartbeat (kompetitives Scheduling)
    from config import PIXIE_CPU_INTERVALL_SEKUNDEN, PIXIE_INTERVALL_SEKUNDEN

    if PIXIE_AKTIV:
        from services.model_services.spur import SPUR_CPU, SPUR_LLM
        from services.pixie.scheduler import pixie_heartbeat

        # Zwei Spuren, zwei Jobs, zwei Sperren. Je `max_instances=1`, damit
        # innerhalb einer Spur weiterhin genau einer laeuft — darauf beruht
        # die Arbeitsliste der Promotion. Ein Agent gehoert zu genau einer
        # Spur, also kann er auch nicht doppelt laufen.
        async def _pixie_job_llm() -> None:
            await pixie_heartbeat(app.state, SPUR_LLM)

        async def _pixie_job_cpu() -> None:
            await pixie_heartbeat(app.state, SPUR_CPU)

        scheduler.add_job(
            _pixie_job_llm,
            trigger       = "interval",
            seconds       = PIXIE_INTERVALL_SEKUNDEN,
            id            = "pixie_heartbeat_llm",
            name          = "Pixie Heartbeat (LLM-Spur)",
            max_instances = 1,
            coalesce      = True,
        )
        scheduler.add_job(
            _pixie_job_cpu,
            trigger       = "interval",
            seconds       = PIXIE_CPU_INTERVALL_SEKUNDEN,
            id            = "pixie_heartbeat_cpu",
            name          = "Pixie Heartbeat (CPU-Spur)",
            max_instances = 1,
            coalesce      = True,
        )
        # Der Quotenabgleich braucht einen Aufrufer, sonst ist er selbst
        # eine Deklaration ohne Leser. Der Takt ist bewusst lang: Der
        # Abgleich braucht 30 bis 100 Aeusserungen, bevor er ueberhaupt
        # urteilen darf — haeufiger zu pruefen erzeugt nur "keine Aussage".
        async def _nmcp_abgleich() -> None:
            """Haelt die angemeldeten Quoten gegen die gezaehlten Zustellungen."""
            from agents import AgentRegistry
            from agents.nmcp_quote import abgleich_protokollieren
            abgleich_protokollieren(AgentRegistry.alle())

        scheduler.add_job(
            _nmcp_abgleich,
            trigger       = "interval",
            seconds       = NMCP_ABGLEICH_INTERVALL_SEKUNDEN,
            id            = "nmcp_quotenabgleich",
            name          = "NMCP-Quotenabgleich",
            max_instances = 1,
            coalesce      = True,
        )
        scheduler.start()
        logger.info(
            f"Scheduler gestartet — LLM-Spur {PIXIE_INTERVALL_SEKUNDEN}s, "
            f"CPU-Spur {PIXIE_CPU_INTERVALL_SEKUNDEN}s."
        )
    else:
        logger.debug("main: Pixie-Heartbeat-Job uebersprungen (PIXIE_AKTIV=False)")
        logger.info("Pixie-Master-Switch: AKTIV=False — alle Pixie-Pfade ruhen")

    # Graphen kompilieren
    compiled_human, human_graph = build_human_graph(
        redis_client = redis_client,
        postgres_url = POSTGRES_URL,
    )
    app.state.conversation_graph = compiled_human
    app.state.human_graph        = human_graph
    logger.info("HumanGraph initialisiert.")

    compiled_agent, agent_graph = build_agent_graph(
        redis_client = redis_client,
        postgres_url = POSTGRES_URL,
    )
    app.state.agent_graph          = agent_graph
    app.state.compiled_agent_graph = compiled_agent
    logger.info("AgentGraph initialisiert.")

    compiled_character, character_graph = build_character_graph(
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

    # ── Prompt-Consumer starten ──
    # Er faehrt Pfad 1 hinter der Eingangs-Queue: Der Endpunkt nimmt nur an,
    # und mehrere Aeusserungen innerhalb des Fensters werden zu einem Prompt.
    prompt_task = asyncio.create_task(
        prompt_consumer_loop(
            human_graph        = app.state.human_graph,
            conversation_graph = app.state.conversation_graph,
        )
    )
    logger.info("Prompt-Consumer gestartet.")

    # Pipeline-Log-Writer als viertes Hintergrund-Task.
    pipeline_log_task: asyncio.Task = asyncio.create_task(
        pipeline_log_writer(POSTGRES_URL, shutdown_event)
    )
    logger.info("Lifespan: Pipeline-Log-Writer gestartet.")

    yield

    # ── Shutdown: Event setzen, dann aufräumen ──
    shutdown_event.set()
    if PIXIE_AKTIV:
        scheduler.shutdown(wait=False)
    if delivery_task is not None:
        delivery_task.cancel()
    consumer_task.cancel()

    # Pipeline-Log-Writer sauber beenden: shutdown_event ist bereits gesetzt,
    # der Writer sieht das im nächsten Loop-Tick und führt einen Final-Flush
    # durch. Wir warten bis zu 30 Sekunden — generös, damit auch ein voller
    # Buffer noch in die DB kommt.
    #
    # Bewusste Abweichung von der Bestandspraxis (delivery_task, consumer_task
    # werden nur per .cancel() ohne await beendet). Pipeline-Log ist Forensik;
    # Datenverlust beim Shutdown wäre die schmerzlichste Stelle. Muster gilt
    # als Vorbild für REFAC-SHUTDOWN-DISZIPLIN (siehe Backlog).
    try:
        await asyncio.wait_for(pipeline_log_task, timeout=30.0)
        logger.info("Lifespan: Pipeline-Log-Writer beendet (regulär).")
    except asyncio.TimeoutError:
        logger.warning(
            "Lifespan: Pipeline-Log-Writer hat Timeout überschritten — Cancel."
        )
        pipeline_log_task.cancel()
        try:
            await pipeline_log_task
        except (asyncio.CancelledError, Exception):
            pass

    # Model-Service-Worker sauber beenden
    await model_service.shutdown()

    logger.info("Server gestoppt.")


# ─────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────
app = FastAPI(
    title       = "KI-Server",
    description = "Persönlicher KI-Assistent mit Gedächtnis und Hintergrund-Rauschen",
    version     = "0.3.0",
    lifespan    = lifespan,
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(gedaechtnis_router)
app.include_router(session_router)
app.include_router(websocket_router)
app.include_router(admin_router)
app.include_router(drive_router)
