"""Task: Thema recherchieren."""

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


class RechercheTask(BaseTask):
    """Thema recherchieren und Ergebnis auf Stack legen."""

    TASK_NAME    = "recherche"
    BESCHREIBUNG = "Thema recherchieren und Ergebnis auf Stack legen"
    BRAUCHT_LLM  = True
    BRAUCHT_DB   = False
    PRIORITAET   = 40
    INTENTIONEN  = ["recherche_vertiefen", "reflexion", "gemeinsam_eruieren", "information_erfragen"]

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

        prompt: str = f"""Recherchiere zum folgenden Thema aus einem Gespräch.

Thema: {thema}
Kontext: {kontext}
User-Intentionen: {intentionen_str}
User-Emotion: {emotion}
Gesprächsmodus: {modus}

Passe deine Recherche an die Intention und Emotion an:
- emotionaler_ausdruck + begeisterung → Finde staunenswerte Zusammenhänge, keine trockenen Fakten
- recherche_vertiefen + neugier → Finde tiefe Details, Mechanismen, Quellen
- gemeinsam_eruieren → Finde alternative Perspektiven und überraschende Ideen
- reflexion + nachdenklich → Finde philosophische Zugänge und Denkanstöße

Formuliere:
1. Eine kurze Zusammenfassung (2-3 Sätze), passend zum Ton des Gesprächs
2. Den wichtigsten Punkt für den Benutzer
3. Einen Vorschlag, wie das Thema weiterverfolgt werden könnte

WICHTIG: Formuliere so, dass Nova das Ergebnis direkt als Chat-Nachricht
verwenden kann. Kein "Der Benutzer sollte..." — schreibe FÜR den Benutzer.

Antworte strukturiert aber knapp."""

        if shutdown_event and shutdown_event.is_set():
            logger.info("Pixie-Task recherche: Shutdown — breche ab")
            return None

        node_cfg = get_node_config("recherche")
        provider = get_background_provider()
        antwort  = provider.chat(
            messages = [
                {"role": "user", "content": prompt},
            ],
            system            = SHADOW_SYSTEM_PROMPT,
            temperature       = node_cfg.get("temperature", 0.5),
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "pixie/recherche",
        )

        ergebnis: str = antwort.content.strip()

        return {"inhalt": ergebnis, "thema": thema}
