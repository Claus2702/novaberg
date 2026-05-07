"""Pixie-Dispatch — Agent-Ausfuehrung und Abschluss.

Fuehrt den Gewinner-Agenten aus und raumt danach auf
(Queue-Pop oder next_run aktualisieren).
"""

import json
import logging
import time

from agents.base import AgentState
from config import redis_client, PIXIE_AKTIV, DEFAULT_USER_ID
from services.llm_provider import set_aktiver_pixie_user

logger = logging.getLogger("ki_server.pixie")


async def agent_ausfuehren(agent_name: str, kandidat: dict, app_state) -> bool:
    """Fuehrt einen Pixie-Agenten aus.

    Args:
        agent_name: Name des Agenten in der Registry
        kandidat: Gewinner-Kandidat mit Daten
        app_state: FastAPI app.state

    Returns:
        True bei Erfolg, False bei Fehler
    """
    import asyncio
    from agents import AgentRegistry

    agent = AgentRegistry.finden(agent_name)
    if not agent:
        logger.error(f"Pixie-Dispatch: Agent '{agent_name}' nicht in Registry")
        return False

    # AgentState aufbauen
    if kandidat["quelle"] == "queue":
        eintrag: dict = kandidat["daten"]
        agent_state: AgentState = {
            "aufgabe":     eintrag.get("aufgabe", ""),
            "aufgabe_typ": "workflow",
            "agent_name":  agent_name,
            "kontext": {
                "user_id": eintrag.get("user_id", ""),
                "themen":  eintrag.get("themen", ""),
                "emotion": eintrag.get("emotion", ""),
                "salienz": eintrag.get("salienz", 0.0),
            },
            "parameter":   eintrag,
            "schritte":    [],
            "ergebnis":    None,
            "status":      "laufend",
            "rueckfrage":  None,
            "fehler":      None,
        }
    else:
        # Periodische Aufgabe
        agent_state = {
            "aufgabe":     agent_name,
            "aufgabe_typ": "workflow",
            "agent_name":  agent_name,
            "kontext":     {},
            "parameter":   {},
            "schritte":    [],
            "ergebnis":    None,
            "status":      "laufend",
            "rueckfrage":  None,
            "fehler":      None,
        }

    # PIX-GPU-IDLE: aktiven User fuer pixie_llm_call() vermerken, damit
    # _ist_pixie_gpu_idle() den richtigen last_activity-Key liest.
    user_id_pixie: str = (
        agent_state["kontext"].get("user_id", "") or DEFAULT_USER_ID
    )
    set_aktiver_pixie_user(user_id_pixie)

    try:
        result_state = await asyncio.to_thread(agent.invoke, agent_state)

        if result_state.get("status") == "fehler":
            logger.warning(
                f"Pixie-Dispatch: Agent '{agent_name}' meldet Fehler: "
                f"{result_state.get('fehler')}"
            )
            return False

        logger.info(f"Pixie-Dispatch: Agent '{agent_name}' abgeschlossen")
        return True

    except Exception as ex:
        logger.error(f"Pixie-Dispatch: Exception bei Agent '{agent_name}': {ex}", exc_info=True)
        return False

    finally:
        set_aktiver_pixie_user("")


def abschluss(kandidat: dict, erfolg: bool) -> None:
    """Abschluss-Routine nach Agent-Ausfuehrung.

    - Queue-Eintrag: Pop bei Erfolg, Retry-Counter bei Fehler
    - Periodische Aufgabe: next_run aktualisieren (auch bei Fehler)
    """
    if kandidat["quelle"] == "queue":
        if erfolg:
            redis_client.lrem(kandidat["queue_key"], 1, kandidat["queue_raw"])
            logger.debug(f"Pixie: Queue-Eintrag entfernt aus {kandidat['queue_key']}")
        else:
            try:
                eintrag = json.loads(kandidat["queue_raw"])
                retries: int = eintrag.get("_retries", 0) + 1

                if retries >= 3:
                    redis_client.lrem(kandidat["queue_key"], 1, kandidat["queue_raw"])
                    logger.warning(
                        f"Pixie: Queue-Eintrag nach 3 Fehlversuchen verworfen: "
                        f"{eintrag.get('aufgabe')}"
                    )
                else:
                    eintrag["_retries"] = retries
                    redis_client.lrem(kandidat["queue_key"], 1, kandidat["queue_raw"])
                    if PIXIE_AKTIV:
                        redis_client.rpush(kandidat["queue_key"], json.dumps(eintrag))
                        logger.info(f"Pixie: Retry {retries}/3 fuer {eintrag.get('aufgabe')}")
                    else:
                        logger.debug("pixie.dispatch: Retry-Push uebersprungen (PIXIE_AKTIV=False)")
            except Exception:
                pass  # Im Fehlerfall einfach stehen lassen

    elif kandidat["quelle"] == "periodisch" and kandidat["schedule_key"]:
        daten = redis_client.hgetall(kandidat["schedule_key"])
        if daten:
            if isinstance(list(daten.keys())[0], bytes):
                daten = {
                    k.decode(): v.decode() if isinstance(v, bytes) else v
                    for k, v in daten.items()
                }
            interval: int = int(daten.get("interval", 3600))
            redis_client.hset(kandidat["schedule_key"], "next_run", str(time.time() + interval))
            logger.debug(f"Pixie: next_run fuer {kandidat['schedule_key']} auf +{interval}s gesetzt")
