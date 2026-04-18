"""
LZG Decay — Markiert verblasste Einträge als inaktiv.

Berechnet das effektive Gewicht für alle aktiven LZG-Einträge.
Einträge unter dem Schwellwert werden als inaktiv markiert (nicht gelöscht).
Inaktive Einträge können durch erneute Verstärkung reaktiviert werden.
"""

import logging
import threading

import psycopg2
import redis

from config                          import EBBINGHAUS_MIN_GEWICHT
from memory.lzg                      import effektives_gewicht_berechnen
from services.shadow_agent.base_task import BaseTask

logger = logging.getLogger("ki_server.shadow")


class LzgDecayTask(BaseTask):
    """Verblasste LZG-Einträge als inaktiv markieren."""

    TASK_NAME    = "lzg_decay"
    BESCHREIBUNG = "Verblasste LZG-Einträge als inaktiv markieren (Ebbinghaus)"
    BRAUCHT_LLM  = False
    BRAUCHT_DB   = True
    PRIORITAET   = 50
    INTENTIONEN  = []

    def execute(
        self,
        auftrag:        dict,
        redis_client:   redis.Redis,
        embed_client,
        embed_model:    str,
        postgres_url:   str,
        user_id:        str,
        shutdown_event: threading.Event | None = None,
    ) -> dict | None:

        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, gewicht, verstaerkt_am
            FROM langzeitgedaechtnis
            WHERE aktiv = TRUE
        """)

        rows = cursor.fetchall()

        inaktiv_ids: list[int] = []

        for row_id, gewicht, verstaerkt_am in rows:
            if shutdown_event and shutdown_event.is_set():
                logger.info("Pixie-Task lzg_decay: Shutdown — breche ab")
                conn.close()
                return None

            eff: float = effektives_gewicht_berechnen(gewicht, verstaerkt_am)
            if eff < EBBINGHAUS_MIN_GEWICHT:
                inaktiv_ids.append(row_id)

        if inaktiv_ids:
            cursor.execute(
                "UPDATE langzeitgedaechtnis SET aktiv = FALSE WHERE id = ANY(%s)",
                (inaktiv_ids,),
            )
            conn.commit()

        conn.close()

        if inaktiv_ids:
            logger.info(
                f"LZG-Decay: {len(inaktiv_ids)} Einträge inaktiv markiert "
                f"(Schwellwert: {EBBINGHAUS_MIN_GEWICHT})"
            )
        else:
            logger.info("LZG-Decay: Keine Einträge unter Schwellwert.")

        return None
