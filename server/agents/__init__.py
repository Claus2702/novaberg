"""Agent-System — Registry, Auto-Discovery, Dispatch-Registry."""

import logging
from pathlib        import Path
from importlib      import import_module
from agents.base    import BaseAgent
from typing         import Callable

logger = logging.getLogger(__name__)

# Dispatch-Registry: agent_name → dispatch-Funktion
_dispatch_registry: dict[str, Callable] = {}


class AgentRegistry:
    """Zentrale Registry aller Agenten. Wird beim Serverstart befüllt."""

    _agenten: dict[str, BaseAgent] = {}

    @classmethod
    def registrieren(cls, agent: BaseAgent) -> None:
        """Registriert einen Agenten."""
        cls._agenten[agent.name] = agent
        logger.info(f"Agent registriert: {agent.name} ({agent.typ})")

    @classmethod
    def finden(cls, name: str) -> BaseAgent | None:
        """Findet einen Agenten nach Name."""
        return cls._agenten.get(name)

    @classmethod
    def alle(cls) -> dict[str, BaseAgent]:
        """Gibt alle registrierten Agenten zurück."""
        return dict(cls._agenten)

    @classmethod
    def fuer_graph(cls, graph_typ: str) -> dict[str, BaseAgent]:
        """Filtert Agenten nach Graph-Eignung ('user' oder 'pixie')."""
        return {
            name: agent
            for name, agent in cls._agenten.items()
            if graph_typ in agent.graph_eignung
        }

    @classmethod
    def beschreibungen(cls, graph_typ: str | None = None) -> str:
        """Alle Agent-Beschreibungen als String für den Planner-Prompt."""
        agenten = cls.fuer_graph(graph_typ) if graph_typ else cls._agenten
        zeilen = []
        for agent in agenten.values():
            zeilen.append(f"## {agent.name} ({agent.typ})")
            zeilen.append(f"Fähigkeiten: {', '.join(agent.faehigkeiten)}")
            beschreibung = agent.beschreibung
            if beschreibung:
                zeilen.append(beschreibung)
            zeilen.append("")
        return "\n".join(zeilen)


def discover_agents() -> None:
    """Scannt agents/-Unterordner und registriert alle BaseAgent-Subklassen + Dispatches."""
    agents_dir = Path(__file__).parent
    gefunden = 0

    for ordner in sorted(agents_dir.iterdir()):
        if not ordner.is_dir() or ordner.name.startswith("_"):
            continue

        # Agent registrieren
        try:
            agent_modul = import_module(f"agents.{ordner.name}.agent")
            for attr_name in dir(agent_modul):
                attr = getattr(agent_modul, attr_name)
                if (isinstance(attr, type)
                    and issubclass(attr, BaseAgent)
                    and attr is not BaseAgent):
                    AgentRegistry.registrieren(attr())
                    gefunden += 1
        except (ImportError, AttributeError) as e:
            logger.debug(f"Kein Agent in {ordner.name}: {e}")
            continue

        # Dispatch registrieren
        try:
            dispatch_modul = import_module(f"agents.{ordner.name}.dispatch")
            dispatch_fn = getattr(dispatch_modul, f"dispatch_{ordner.name}", None)
            if dispatch_fn:
                _dispatch_registry[ordner.name] = dispatch_fn
                logger.debug(f"Dispatch registriert: {ordner.name}")
        except (ImportError, AttributeError) as e:
            logger.debug(f"Kein Dispatch in {ordner.name}: {e}")

    logger.info(f"Agent-Discovery abgeschlossen: {gefunden} Agenten registriert")


def get_dispatch(agent_name: str) -> Callable | None:
    """Gibt die Dispatch-Funktion für einen Agenten zurück."""
    return _dispatch_registry.get(agent_name)
