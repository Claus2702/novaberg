"""Task: LZG-Duplikate finden und Konsolidierung vorschlagen."""

import logging
import threading

import psycopg2
import redis

from config                          import ASSISTANT_NAME, get_node_config
from services.shadow_agent.base_task import BaseTask
from services.llm_provider           import get_background_provider

logger = logging.getLogger("ki_server.shadow")

SHADOW_SYSTEM_PROMPT: str = f"""Du bist {ASSISTANT_NAME} — nicht im Gespräch mit einem Menschen,
sondern in deinem eigenen Denkprozess. Du verarbeitest Themen, die dir aus
Gesprächen mit deinem Benutzer aufgefallen sind.

Deine Aufgabe:
- Recherchiere und vertiefe Themen gründlich
- Formuliere Erkenntnisse als kurze, prägnante Einsichten
- Denke darüber nach, wie das Ergebnis dem Benutzer nützen könnte
- Sei ehrlich — wenn ein Thema nicht ergiebig ist, sag das

Antworte auf Deutsch. Fasse dich kurz und präzise."""


class AufraeumenTask(BaseTask):
    """LZG-Duplikate finden und Konsolidierung vorschlagen."""

    TASK_NAME    = "aufräumen"
    BESCHREIBUNG = "LZG-Duplikate finden und Konsolidierung vorschlagen"
    BRAUCHT_LLM  = True
    BRAUCHT_DB   = True
    PRIORITAET   = 80
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

        thema: str = auftrag.get("thema", "")

        if shutdown_event and shutdown_event.is_set():
            logger.info("Pixie-Task aufräumen: Shutdown — breche ab")
            return None

        # Ähnliche LZG-Einträge finden
        embedding: list[float] = embed_client.embed(
            model = embed_model,
            input = thema,
        )["embeddings"][0]

        embedding_str: str = "[" + ",".join(str(x) for x in embedding) + "]"

        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, inhalt, gewicht, haeufigkeit
            FROM   langzeitgedaechtnis
            WHERE  user_id = %s
            AND    aktiv = TRUE
            AND    1 - (embedding <=> %s::vector) > 0.75
            ORDER  BY gewicht DESC
            LIMIT  10
        """, (user_id, embedding_str))

        eintraege: list = cursor.fetchall()
        conn.close()

        if len(eintraege) < 2:
            logger.info(f"Shadow-Aufräumen: Weniger als 2 ähnliche Einträge für '{thema}' — nichts zu tun.")
            return None

        # LLM entscheiden lassen was konsolidiert werden kann
        eintraege_text: str = "\n".join(
            f"[{row[0]}] {row[1]} (Gewicht: {row[2]}, Häufigkeit: {row[3]})"
            for row in eintraege
        )

        prompt: str = f"""Analysiere diese Gedächtniseinträge zum Thema '{thema}'.
Finde Duplikate oder Einträge die zusammengefasst werden können.

Einträge:
{eintraege_text}

Antworte im Format:
ZUSAMMENFASSEN: [ID1], [ID2] → "Neuer zusammengefasster Text"
LÖSCHEN: [ID] — Grund
BEHALTEN: [ID] — Grund

Nur echte Duplikate zusammenfassen. Im Zweifel behalten."""

        if shutdown_event and shutdown_event.is_set():
            logger.info("Pixie-Task aufräumen: Shutdown — breche ab")
            return None

        node_cfg = get_node_config("aufräumen")
        provider = get_background_provider()
        antwort  = provider.chat(
            messages = [
                {"role": "user", "content": prompt},
            ],
            system            = SHADOW_SYSTEM_PROMPT,
            temperature       = node_cfg.get("temperature", 0.1),
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "pixie/aufräumen",
        )

        ergebnis: str = antwort.content.strip()

        return {"inhalt": f"Aufräumvorschlag:\n{ergebnis}", "thema": thema}
