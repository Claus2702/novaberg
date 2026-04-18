"""Task: Einfühlsame Nachfrage zu offenem Thema."""

import logging
import threading

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


class NachfragenTask(BaseTask):
    """Einfühlsame Nachfrage zu offenem Thema."""

    TASK_NAME    = "nachfragen"
    BESCHREIBUNG = "Einfühlsame Nachfrage zu offenem Thema"
    BRAUCHT_LLM  = True
    BRAUCHT_DB   = False
    PRIORITAET   = 30
    INTENTIONEN  = ["emotionaler_ausdruck", "hilferuf"]
    EMOTION_BLACKLIST = ["stress"]

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

        thema:       str  = auftrag.get("thema", "")
        kontext:     str  = auftrag.get("kontext", "")
        intentionen: list = auftrag.get("intentionen", [])
        emotion:     str  = auftrag.get("emotion", "")
        modus:       str  = auftrag.get("modus", "")

        intentionen_str: str = ", ".join(intentionen)

        prompt: str = f"""Aus einem früheren Gespräch ist folgendes Thema offen geblieben:

Thema: {thema}
Kontext: {kontext}
User-Intentionen damals: {intentionen_str}
User-Emotion damals: {emotion}
Gesprächsmodus damals: {modus}

Formuliere eine natürliche Nachfrage die Nova stellen könnte.
Die Frage soll echtes Interesse zeigen, nicht aufdringlich wirken.
Verwende NICHT die Phrase "Hat dich das noch beschäftigt" — variiere!

Formuliere NUR die Frage, kein weiterer Text."""

        if shutdown_event and shutdown_event.is_set():
            logger.info("Pixie-Task nachfragen: Shutdown — breche ab")
            return None

        node_cfg = get_node_config("nachfragen")
        provider = get_background_provider()
        antwort  = provider.chat(
            messages = [
                {"role": "user", "content": prompt},
            ],
            system            = SHADOW_SYSTEM_PROMPT,
            temperature       = node_cfg.get("temperature", 0.6),
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "pixie/nachfragen",
        )

        nachfrage: str = antwort.content.strip()

        return {"inhalt": nachfrage, "thema": thema}
