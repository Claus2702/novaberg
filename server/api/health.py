"""
health-Check und Modellverwaltung.
"""

import json
import logging

from fastapi           import APIRouter
from fastapi.responses import JSONResponse

from config import redis_client, ollama_gpu_chat, OLLAMA_MODEL, postgres_verbinden, SEARXNG_URL

logger = logging.getLogger("ki_server.health")
router = APIRouter()


# ─────────────────────────────────────────────
# Verbindungstests
# ─────────────────────────────────────────────
def ollama_testen() -> bool:
    """Ollama-Verbindung und Modellverfügbarkeit prüfen."""
    try:
        models       = ollama_gpu_chat.list()
        model_namen: list = [m.model for m in models.models]
        logger.debug(f"Ollama erreichbar. Modelle: {model_namen}")

        if not any(OLLAMA_MODEL in name for name in model_namen):
            logger.warning(f"Modell '{OLLAMA_MODEL}' nicht gefunden.")
            return False

        return True

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Ollama nicht erreichbar")
        return False


def redis_testen() -> bool:
    """Redis-Verbindung prüfen."""
    try:
        redis_client.ping()
        logger.debug("Redis erreichbar.")
        return True
    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Redis nicht erreichbar")
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
        logger.exception(f"{type(fehler).__name__}: PostgreSQL nicht erreichbar")
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
        logger.exception(f"{type(fehler).__name__}: SearXNG nicht erreichbar")
        return False


# ─────────────────────────────────────────────
# Endpunkte
# ─────────────────────────────────────────────
def _nmcp_stand() -> dict:
    """Sammelt den NMCP-Zustand: Einbindung, Quoten und Zaehlerstaende.

    Vorbedingung: keine — vor dem Handshake ist der Zustand leer.

    Nachbedingung: ein Dict mit `verweigert`, `ohne_zweifelsfaelle` und je
    Empfangsdienst dem Paar aus geschaetzter und gemessener Quote.

    **Der Grund fuer diesen Lesepfad steht in der Konvention:** Eine
    verweigerte Einbindung muss zur LAUFZEIT sichtbar bleiben, nicht nur in
    einer Startmeldung. Eine Zeile beim Hochlauf ist nach zehn Minuten aus
    dem Blick, und danach verhaelt sich der fehlende Dienst wie einer, den
    niemand braucht — genau der stille Zustand, gegen den der
    Quotenabgleich gebaut ist.
    """
    from agents import AgentRegistry
    from agents.nmcp import anmelden
    from agents.nmcp_quote import REGISTER

    # Der Anmeldebefund wird hier NEU gerechnet, nicht aus dem Startzustand
    # gelesen. Zwei Gruende: Ein Schnappschuss vom Hochlauf altert, und ein
    # Feld, das nur beim Start geschrieben und hier gelesen wuerde, waere ein
    # zweiter Kanal fuer dieselbe Auskunft. Die Anmeldung ist zustandslos und
    # billig — sie liest Deklarationen, nichts sonst.
    verweigert: list[str] = []
    ohne_zweifel: list[str] = []
    for _name, _agent in sorted(AgentRegistry.alle().items()):
        try:
            _b = anmelden(_agent)
        except (TypeError, ValueError):
            verweigert.append(_name)
            continue
        if not _b.eingebunden:
            verweigert.append(_name)
        elif not _b.zweifel_erlaubt:
            ohne_zweifel.append(_name)

    dienste: dict = {}
    for name, agent in sorted(AgentRegistry.alle().items()):
        if getattr(agent, "zustellart", "") != "empfang":
            continue
        for graph, geschaetzt in getattr(agent, "quote", {}).items():
            stand = REGISTER.stand(name, graph)
            nenner = REGISTER.turns(graph)
            dienste[f"{name}/{graph}"] = {
                "geschaetzt":  geschaetzt,
                "zugestellt":  stand.zugestellt,
                "bearbeitet":  stand.bearbeitet,
                "abgelehnt":   stand.abgelehnt,
                "nenner":      nenner,
                "gemessen":    round(stand.zugestellt / nenner * 100, 1) if nenner else None,
            }

    return {
        "verweigert":         verweigert,
        "ohne_zweifelsfaelle": ohne_zweifel,
        "nenner":             {g: REGISTER.turns(g) for g in ("user", "pixie")},
        "dienste":            dienste,
    }


@router.get("/health")
def health():
    """Systemstatus aller Komponenten + Shadow Agent + NMCP-Stand."""
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
        "nmcp":     _nmcp_stand(),
    }


@router.get("/modelle")
def modelle_auflisten():
    """Verfügbare Ollama-Modelle."""
    try:
        models = ollama_gpu_chat.list()
        return {"modelle": [m.model for m in models.models]}
    except Exception as fehler:
        return JSONResponse(status_code=503, content={"fehler": str(fehler)})


@router.post("/modell/laden/{modell_name}")
def modell_laden(modell_name: str):
    """Ollama-Modell herunterladen."""
    try:
        logger.info(f"Lade Modell: {modell_name}")
        ollama_gpu_chat.pull(modell_name)
        return {"status": "ok", "modell": modell_name}
    except Exception as fehler:
        return JSONResponse(status_code=500, content={"fehler": str(fehler)})
