"""BaseAgent, AgentState, AgentResult — Fundament des Agent-Systems."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypedDict
import inspect
import logging

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State eines einzelnen Agenten. Der Agent sieht nie den ConversationState."""
    aufgabe: str                  # Was soll getan werden (Freitext)
    aufgabe_typ: str              # "workflow" | "kognitiv"
    agent_name: str               # Name des ausführenden Agenten
    kontext: dict                 # user_id, session_id, memory_context, ...
    parameter: dict               # Agent-spezifische Parameter
    schritte: list[dict]          # Bisherige Schritte + Ergebnisse (Audit-Trail)
    ergebnis: Any                 # Finales Ergebnis
    status: str                   # "laufend" | "abgeschlossen" | "fehler" | "rueckfrage"
    rueckfrage: str | None        # Rückfrage-Text bei status="rueckfrage"
    fehler: str | None            # Fehler-Beschreibung bei status="fehler"


@dataclass
class PeriodicTask:
    """Beschreibung einer periodischen Pixie-Aufgabe."""
    name: str
    priority: float     # 0.0 – 1.0
    interval: int       # Abklingzeit in Sekunden
    description: str


@dataclass
class AgentResult:
    """Typisiertes Ergebnis-Objekt, das der Dispatch in den ConversationState schreibt."""
    agent_name: str
    ergebnis: Any                          # Agent-spezifisches Ergebnis
    status: str                            # "abgeschlossen" | "fehler" | "rueckfrage"
    fehler: str | None = None
    rueckfrage: str | None = None
    schritte: list[dict] = field(default_factory=list)   # Audit-Trail
    meta: dict = field(default_factory=dict)              # Dauer, Token, Telemetrie


class BaseAgent(ABC):
    """Abstrakte Basisklasse für alle Agenten."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Eindeutiger Name, identisch mit dem Verzeichnisnamen."""
        ...

    @property
    def beschreibung(self) -> str:
        """Lädt AGENT.md aus dem eigenen Verzeichnis."""
        pfad = Path(inspect.getfile(self.__class__)).parent / "AGENT.md"
        if pfad.exists():
            return pfad.read_text(encoding="utf-8")
        return ""

    @property
    def typ(self) -> str:
        """'workflow' (Typ 1) oder 'kognitiv' (Typ 2)."""
        return "workflow"

    @property
    def faehigkeiten(self) -> list[str]:
        """Liste der Fähigkeiten für den Planner-Prompt."""
        return []

    @property
    def graph_eignung(self) -> list[str]:
        """In welchen Graphen darf dieser Agent laufen: ['user'], ['pixie'], oder beide."""
        return ["user", "pixie"]

    def periodic_task(self) -> PeriodicTask | None:
        """Periodische Aufgabe dieses Agenten fuer Pixie-Scheduling.
        None = Agent arbeitet nur Queue-basiert.
        """
        return None

    @property
    def context_user(self) -> str:
        """Wessen Gedaechtnis wird gelesen/geschrieben?
        'user' = Gedaechtnis des Users (KZG/LZG/Fakten).
        'nova' = Novas eigenes Gedaechtnis.
        """
        return "user"

    @property
    def identity_user(self) -> str:
        """Wessen Charakter wird fuer LLM-Calls verwendet?
        Immer 'nova' — Pixie denkt als Nova.
        """
        return "nova"

    @abstractmethod
    def build_graph(self):
        """Baut den LangGraph-Subgraph des Agenten. Gibt CompiledStateGraph zurück."""
        ...

    def setup(self, postgres_url: str) -> None:
        """Schema anlegen via init.sql, falls vorhanden."""
        sql_pfad = Path(inspect.getfile(self.__class__)).parent / "init.sql"
        if sql_pfad.exists():
            from tools.db_manager import db_manager
            sql = sql_pfad.read_text(encoding="utf-8")
            db_manager.execute_script(sql)
            logger.info(f"Schema für Agent '{self.name}' angelegt")

    def invoke(self, state: AgentState) -> AgentState:
        """Führt den Subgraph aus und gibt den finalen State zurück."""
        graph = self.build_graph()
        return graph.invoke(state)
