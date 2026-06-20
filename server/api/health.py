"""
Health-Check und Modellverwaltung.
"""

import json
import logging

from fastapi           import APIRouter
from fastapi.responses import JSONResponse

from config import redis_client, ollama_gpu_client, OLLAMA_MODEL, postgres_verbinden, SEARXNG_URL

logger = logging.getLogger("ki_server.health")
router = APIRouter()


# ─────────────────────────────────────────────
# Verbindungstests
# ─────────────────────────────────────────────
def ollama_testen() -> bool:
    """Ollama-Verbindung und Modellverfügbarkeit prüfen."""
    try:
        models       = ollama_gpu_client.list()
        model_namen: list = [m.model for m in models.models]
        logger.debug(f"Ollama erreichbar. Modelle: {model_namen}")

        if not any(OLLAMA_MODEL in name for name in model_namen):
            logger.warning(f"Modell '{OLLAMA_MODEL}' nicht gefunden.")
            return False

        return True

    except Exception as fehler:
        logger.error(f"Ollama nicht erreichbar: {fehler}")
        return False


def redis_testen() -> bool:
    """Redis-Verbindung prüfen."""
    try:
        redis_client.ping()
        logger.debug("Redis erreichbar.")
        return True
    except Exception as fehler:
        logger.error(f"Redis nicht erreichbar: {fehler}")
        return False


def postgres_testen() -> bool:
    """PostgreSQL-Verbindung und pgvector prüfen."""
    try:
        conn   = postgres_verbinden()
        cursor = conn.cursor()

        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        ergebnis = cursor.fetchone()

        if not ergebnis:
            logger.error("pgvector-Extension nicht installiert.")
            conn.close()
            return False

        cursor.execute("SELECT COUNT(*) FROM lzg_knoten;")
        logger.debug("PostgreSQL + pgvector erreichbar. Schema vorhanden.")
        conn.close()
        return True

    except Exception as fehler:
        logger.error(f"PostgreSQL nicht erreichbar: {fehler}")
        return False


def searxng_testen() -> bool:
    """SearXNG-Erreichbarkeit prüfen."""
    try:
        import urllib.request
        req = urllib.request.Request(SEARXNG_URL, method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                logger.debug("SearXNG erreichbar.")
                return True
        return False
    except Exception as fehler:
        logger.error(f"SearXNG nicht erreichbar: {fehler}")
        return False


# ─────────────────────────────────────────────
# Endpunkte
# ─────────────────────────────────────────────
@router.get("/health")
def Health():
    """Systemstatus aller Komponenten + Shadow Agent."""

    # Shadow-Status aus Redis lesen
    shadow: dict = {"zustand": "idle", "thema": ""}

    try:
        raw: str = redis_client.get("shadow_status") or ""
        if raw:
            import json
            shadow = json.loads(raw)
    except Exception:
        pass

    return {
        "server":   "ok",
        "redis":    "ok" if redis_testen()    else "fehler",
        "postgres": "ok" if postgres_testen() else "fehler",
        "ollama":   "ok" if ollama_testen()   else "fehler",
        "searxng":  "ok" if searxng_testen()  else "fehler",
        "shadow":   shadow,
    }


@router.get("/modelle")
def ModelleAuflisten():
    """Verfügbare Ollama-Modelle."""
    try:
        models = ollama_gpu_client.list()
        return {"modelle": [m.model for m in models.models]}
    except Exception as fehler:
        return JSONResponse(status_code=503, content={"fehler": str(fehler)})


@router.post("/modell/laden/{modell_name}")
def ModellLaden(modell_name: str):
    """Ollama-Modell herunterladen."""
    try:
        logger.info(f"Lade Modell: {modell_name}")
        ollama_gpu_client.pull(modell_name)
        return {"status": "ok", "modell": modell_name}
    except Exception as fehler:
        return JSONResponse(status_code=500, content={"fehler": str(fehler)})
