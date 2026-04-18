"""
BaseManager — Interface für alle Manager-Plugins.

Jeder Manager ist ein spezialisierter Arbeiter mit:
  - Identität (ziel, immer_aktiv)
  - Prompt-Erweiterungen (router, salienz, enricher)
  - Enricher-Hook (Kontext laden)
  - DB-Schema (init.sql im eigenen Ordner)
  - Ausführung (execute)

Entscheider legen pending_writes an → Dispatcher verteilt → Manager führt aus.
"""

import inspect
import logging
from abc     import ABC, abstractmethod
from pathlib import Path

import psycopg2
import redis

logger = logging.getLogger("ki_server.plugins")


class BaseManager(ABC):
    """Basisklasse für alle Manager-Plugins."""

    # ─────────────────────────────────────────
    # Identität
    # ─────────────────────────────────────────
    @property
    @abstractmethod
    def ziel(self) -> str:
        """Eindeutiger Name: 'kzg', 'fakten', 'timeline', 'notizen', ..."""
        pass

    @property
    @abstractmethod
    def immer_aktiv(self) -> bool:
        """True = läuft bei jedem Turn. False = nur bei pending_writes."""
        pass

    # ─────────────────────────────────────────
    # Prompt-Erweiterungen für Entscheider
    # ─────────────────────────────────────────
    @property
    def router_prompt(self) -> str:
        """Zusätzliche Anweisungen für den Router. Default: keine."""
        return ""

    @property
    def router_intents(self) -> list[str]:
        """Welche Intents dieser Manager behandelt. Default: keine."""
        return []

    @property
    def salienz_prompt(self) -> str:
        """Zusätzliche Anweisungen für den Salienz-Agent. Default: keine."""
        return ""

    @property
    def enricher_prompt(self) -> str:
        """Anweisungen für den Enricher. Default: keine."""
        return ""

    # ─────────────────────────────────────────
    # Enricher-Hook (Kontext laden)
    # ─────────────────────────────────────────
    def enrich(self, state: dict, postgres_url: str) -> str:
        """
        Optional: Kontext laden wenn dieser Manager betroffen ist.
        Wird vom Enricher aufgerufen. Default: nichts.
        """
        return ""

    # ─────────────────────────────────────────
    # Planner-Hook (Plan-Phase)
    # ─────────────────────────────────────────
    def plan(
        self,
        state:        dict,
        postgres_url: str
    ) -> dict:
        """
        Optional: Plan-Phase für explizite Management-Intents.
        Erzeugt pending_writes und management_result/detail.
        Default: nichts.

        Returns: {"pending_writes": [...], "management_result": "", "management_detail": ""}
        """
        return {"pending_writes": [], "management_result": "", "management_detail": ""}

    # ─────────────────────────────────────────
    # DB-Schema
    # ─────────────────────────────────────────
    def setup(self, postgres_url: str, redis_client: redis.Redis = None) -> None:
        """
        Wird beim Server-Start aufgerufen.
        Liest init.sql aus dem eigenen Ordner und führt es aus.
        """

        sql_path: Path = Path(inspect.getfile(self.__class__)).parent / "init.sql"

        if sql_path.exists():
            try:
                conn   = psycopg2.connect(postgres_url)
                cursor = conn.cursor()
                cursor.execute(sql_path.read_text())
                conn.commit()
                conn.close()
                logger.info(f"Plugin '{self.ziel}': Schema geladen ({sql_path.name})")
            except Exception as fehler:
                logger.error(f"Plugin '{self.ziel}': Schema-Fehler — {fehler}")

    # ─────────────────────────────────────────
    # Ausführung (Arbeiter)
    # ─────────────────────────────────────────
    @abstractmethod
    def execute(
        self,
        writes:       list[dict],
        user_id:      str,
        redis_client: redis.Redis,
        postgres_url: str,
        embed_client = None,
        embed_model:  str = ""
    ) -> int:
        """
        Führt die DB-Operationen aus.
        Returns: Anzahl verarbeiteter Writes.
        """
        pass
