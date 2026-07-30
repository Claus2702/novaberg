"""Pixie-Scheduler — Heartbeat fuer kompetitives Scheduling.

Wird alle PIXIE_INTERVALL_SEKUNDEN vom APScheduler aufgerufen.
Sammelt Kandidaten aus Queues und periodischen Aufgaben,
der mit der hoechsten Prioritaet gewinnt, EIN Agent wird ausgefuehrt.
"""

import json
import logging
import time

from config import redis_client, PIXIE_LOCK_TTL_SEKUNDEN
from services.pixie.kandidaten import kandidaten_sammeln
from services.pixie.router import route
from services.pixie.dispatch import agent_ausfuehren, abschluss

logger = logging.getLogger("ki_server.pixie")


async def pixie_heartbeat(app_state) -> None:
    """Pixie-Heartbeat: Ein Zyklus des kompetitiven Schedulers.

    1. Lock pruefen (pixie:running) — laeuft noch ein Zyklus? -> Verwerfen
    2. Pause pruefen (pixie:paused) — Admin-API hat pausiert? -> Verwerfen
    3. Kandidaten sammeln (Queue-Peek + faellige periodische Aufgaben)
    4. Hoechste Prioritaet gewinnt
    5. Router: Agent-Name bestimmen
    6. Agent ausfuehren
    7. Abschluss: Queue-Pop oder next_run aktualisieren, Lock freigeben
    """
    # Guard: Lauf-Schutz
    if redis_client.exists("pixie:running"):
        logger.debug("Pixie: Letzter Zyklus laeuft noch — Heartbeat verworfen")
        return

    # Guard: Pause (Admin-API Kompatibilitaet)
    if redis_client.exists("pixie:paused"):
        logger.debug("Pixie: Pausiert — Heartbeat verworfen")
        return

    # Lock setzen mit TTL als Deadlock-Schutz
    redis_client.set("pixie:running", "1", ex=PIXIE_LOCK_TTL_SEKUNDEN)

    try:
        # Kandidaten sammeln
        kandidaten: list[dict] = kandidaten_sammeln()

        if not kandidaten:
            logger.debug("Pixie: Keine Kandidaten — Zyklus beendet")
            return

        # Hoechste Prioritaet gewinnt
        gewinner: dict = max(kandidaten, key=lambda k: k["prioritaet"])

        # Die Gewinner-Zeile nennt beide Werte: gewaehlt wurde nach der
        # effektiven Prioritaet, entschieden hat bei einer gealterten Aufgabe
        # der Zuschlag. Stuende hier nur eine Zahl, waere aus dem Log nicht
        # mehr erkennbar, ob der Verhungerungsschutz gegriffen hat.
        _basis:       float        = gewinner.get("prioritaet_basis", gewinner["prioritaet"])
        _ueberfaellig: float | None = gewinner.get("ueberfaellig_s")
        _aging_text:  str          = (
            f", gealtert von {_basis:.2f} nach {_ueberfaellig:.0f}s Ueberfaelligkeit"
            if _ueberfaellig is not None and gewinner["prioritaet"] > _basis
            else ""
        )
        logger.info(
            f"Pixie: Gewinner — {gewinner['name']} "
            f"(Prio {gewinner['prioritaet']:.2f}, Quelle: {gewinner['quelle']}{_aging_text})"
        )

        # Status setzen (fuer Health-Endpoint / Client-Statusleiste)
        redis_client.set("shadow_status", json.dumps({
            "task": gewinner["name"],
            "thema": gewinner.get("themen", ""),
            "seit": time.time(),
        }))

        # Router: Agent-Name bestimmen
        agent_name: str | None = route(gewinner)

        if not agent_name:
            logger.warning(f"Pixie: Kein Agent fuer Kandidat '{gewinner['name']}' gefunden")
            return

        # Agent ausfuehren
        erfolg: bool = await agent_ausfuehren(agent_name, gewinner, app_state)

        # Abschluss
        abschluss(gewinner, erfolg)

    except Exception as ex:
        logger.error(f"Pixie: Fehler im Heartbeat — {ex}", exc_info=True)
    finally:
        # Lock freigeben + Status zuruecksetzen
        redis_client.delete("pixie:running")
        redis_client.set("shadow_status", json.dumps({
            "task": "idle", "thema": "", "seit": time.time(),
        }))
