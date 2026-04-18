"""Task: Thema vertiefen mit Novas Vorwissen."""

import logging
import threading

import redis

from config                          import ASSISTANT_NAME, get_node_config
from services.shadow_agent.base_task import BaseTask
from services.shadow_agent.utils     import nova_vorwissen_laden
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


class VertiefenTask(BaseTask):
    """Bekanntes Thema vertiefen mit Novas Vorwissen."""

    TASK_NAME    = "vertiefen"
    BESCHREIBUNG = "Bekanntes Thema vertiefen mit Novas Vorwissen"
    BRAUCHT_LLM  = True
    BRAUCHT_DB   = True
    PRIORITAET   = 40
    INTENTIONEN  = ["information_teilen", "recherche_vertiefen"]

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

        # Novas Vorwissen laden
        vorwissen: str = nova_vorwissen_laden(postgres_url, embed_client, embed_model, thema)

        intentionen_str: str = ", ".join(intentionen)

        prompt: str = f"""Der Benutzer arbeitet an folgendem Thema und braucht Vertiefung.

Thema: {thema}
Kontext: {kontext}
User-Intentionen: {intentionen_str}
User-Emotion: {emotion}
Gesprächsmodus: {modus}
{"Dein bisheriges Wissen dazu: " + vorwissen if vorwissen else ""}

Passe die Vertiefung an den Gesprächsmodus an:
- fachgespraech → Präzise Details, Mechanismen, Fachbegriffe
- philosophischer_austausch → Tiefere Zusammenhänge, offene Fragen
- alltag → Praktische Tipps, alltagsnahe Beispiele
- arbeitsmodus → Konkrete nächste Schritte, Lösungen

Analysiere das Thema gründlich. Finde:
- Kernkonzepte die der Benutzer kennen sollte
- Mögliche Fallstricke oder häufige Fehler
- Einen konkreten nächsten Schritt

WICHTIG: Formuliere so, dass Nova das Ergebnis direkt als Chat-Nachricht
verwenden kann. Schreibe FÜR den Benutzer, nicht ÜBER ihn.

Antworte präzise und praxisnah."""

        if shutdown_event and shutdown_event.is_set():
            logger.info("Pixie-Task vertiefen: Shutdown — breche ab")
            return None

        node_cfg = get_node_config("vertiefen")
        provider = get_background_provider()
        antwort  = provider.chat(
            messages = [
                {"role": "user", "content": prompt},
            ],
            system            = SHADOW_SYSTEM_PROMPT,
            temperature       = node_cfg.get("temperature", 0.5),
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "pixie/vertiefen",
        )

        ergebnis: str = antwort.content.strip()

        return {"inhalt": ergebnis, "thema": thema}
