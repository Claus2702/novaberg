"""Task: Novas eigene Erkenntnisse ins KZG speichern (via kzg_store)."""

import logging
import threading

import redis

from services.shadow_agent.base_task import BaseTask
from memory.kzg import kzg_store

logger = logging.getLogger("ki_server.shadow")


class NovaGedaechtnisTask(BaseTask):
    """Novas eigene Erkenntnisse ins KZG speichern (via kzg_store)."""

    TASK_NAME    = "nova_gedaechtnis"
    BESCHREIBUNG = "Novas eigene Erkenntnisse ins KZG speichern (via kzg_store)"
    BRAUCHT_LLM  = False
    BRAUCHT_DB   = False
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

        thema:    str = auftrag.get("thema", "")
        ergebnis: str = auftrag.get("ergebnis", "")

        if not thema or not ergebnis:
            return None

        # Cooldown: max 1x pro 10 Minuten pro User
        cooldown_key: str = f"nova_gedaechtnis_cooldown:{user_id}"
        if redis_client.exists(cooldown_key):
            logger.info(f"Nova-Gedächtnis: Cooldown aktiv für '{user_id}' — übersprungen")
            return None

        if shutdown_event and shutdown_event.is_set():
            logger.info("Pixie-Task nova_gedaechtnis: Shutdown — breche ab")
            return None

        # Embedding für Novas Erkenntnis erzeugen
        try:
            embed_text: str = f"{thema} {ergebnis[:300]}"
            embedding: list[float] = embed_client.embed(
                model = embed_model,
                input = embed_text,
            )["embeddings"][0]
        except Exception as fehler:
            logger.warning(f"Nova-Gedächtnis: Embedding fehlgeschlagen — {fehler}")
            return None

        # Via kzg_store in Novas KZG schreiben (volle Pipeline: Salienz → Promotion → LZG → Hash)
        salienz_obj: dict = {
            "salienz":        0.7,
            "themen":         [thema],
            "zusammenfassung": f"Recherche zu '{thema}': {ergebnis[:300]}",
            "dimension":      "wissen",
            "gedaechtnistyp": "kurz",
            "intentionen":    [],
            "emotion":        "neutral",
            "modus":          "",
        }

        kzg_store(
            redis_client = redis_client,
            user_id      = "nova",
            salienz_obj  = salienz_obj,
            embedding    = embedding,
        )

        # Cooldown setzen (600s = 10 Minuten)
        redis_client.set(cooldown_key, "1", ex=600)

        logger.info(f"Nova-KZG: Erkenntnis zu '{thema}' via kzg_store gespeichert.")

        return None
