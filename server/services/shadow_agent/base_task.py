"""BaseTask — Abstrakte Klasse für Shadow Agent Tasks."""

import threading
from abc import ABC, abstractmethod

import redis


class BaseTask(ABC):
    """Basis für alle Shadow Agent Tasks."""

    # Jede Task-Klasse definiert diese Attribute
    TASK_NAME:    str = ""           # Eindeutiger Name (z.B. "recherche")
    BESCHREIBUNG: str = ""           # Menschenlesbar
    BRAUCHT_LLM:  bool = True        # Nutzt CPU-Modell?
    BRAUCHT_DB:   bool = False       # Braucht PostgreSQL-Zugriff?
    PRIORITAET:   int  = 50          # 0=höchste, 100=niedrigste

    # Welche Intentionen triggern diesen Task? (leer = manuell/intern)
    INTENTIONEN:  list[str] = []

    # Bei welchen Emotionen NICHT ausführen? (leer = immer erlaubt)
    EMOTION_BLACKLIST: list[str] = []

    @abstractmethod
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
        """
        Führt den Task aus.

        Args:
            auftrag: Dict mit mindestens {thema, kontext, intentionen, emotion, modus}

        Returns:
            Ergebnis-Dict für den Stack, oder None wenn nichts auf den Stack soll.
            Format: {"inhalt": str, "thema": str} — wird von runner.py auf den Stack gelegt.
        """
        ...

    def kann_ausfuehren(self, auftrag: dict) -> bool:
        """Prüft ob dieser Task den Auftrag verarbeiten kann."""

        # Emotion-Blacklist prüfen
        emotion: str = auftrag.get("emotion", "")
        if emotion and emotion in self.EMOTION_BLACKLIST:
            return False

        return True
