"""
GraphBase — Abstrakte Basisklasse für alle Gesprächsgraphen.

Kapselt gemeinsame Infrastruktur:
  - Dependency-Verwaltung (Ollama, Redis, Postgres)
  - KZG-Index-Initialisierung
  - Plugin Discovery + Manager Setup
  - Node-Wrapper als Methoden
"""

import logging
from abc import ABC, abstractmethod

import redis
from langgraph.graph import END  # noqa: F401 — re-export für Subklassen
from langgraph.graph.state import CompiledStateGraph

from graph.state           import ConversationState
from graph.nodes.perzeption import perceive
from graph.nodes.router     import route
from graph.nodes.enricher  import enrich
from graph.nodes.ei_calc   import ei_calc
from graph.nodes.planner   import plan
from graph.nodes.responder import respond
from graph.nodes.thinker   import think
from graph.nodes.tribunal  import judge, evaluate
from graph.nodes.corrector import correct
from graph.nodes.salience  import analyze
from graph.nodes.dispatcher      import dispatch
from graph.nodes.agent_dispatch  import agent_dispatch_node

from memory.kzg import kzg_index_create
from plugins    import discover_managers, get_registry

logger = logging.getLogger("ki_server.graph.base")

MAX_CORRECTIONS: int = 2


class GraphBase(ABC):
    """Abstrakte Basisklasse für Human- und Agent-Graphen."""

    MAX_CORRECTIONS: int = 2

    def __init__(
        self,
        embed_client,
        embed_model:  str,
        redis_client: redis.Redis,
        postgres_url: str,
    ) -> None:
        self.embed_client = embed_client
        self.embed_model  = embed_model
        self.redis_client = redis_client
        self.postgres_url = postgres_url

        # KZG-Index sicherstellen
        kzg_index_create(redis_client)

        # Manager-Plugins laden + Setup
        self.registry: dict = discover_managers()

        for name, manager in self.registry.items():
            manager.setup(postgres_url=postgres_url, redis_client=redis_client)
            logger.info(f"Plugin '{name}' initialisiert.")

    # ── Abstrakte Methoden ─────────────────────

    @abstractmethod
    def build(self) -> CompiledStateGraph:
        """Subklassen verdrahten ihre Nodes und geben den kompilierten Graphen zurück."""

    @abstractmethod
    def create_state(self, user_prompt: str, user_id: str, **kwargs) -> ConversationState:
        """Subklassen erzeugen ihren initialen State."""

    # ── Node-Wrapper ───────────────────────────

    def _node_perceive(self, state: ConversationState) -> ConversationState:
        return perceive(state)

    def _node_route(self, state: ConversationState) -> ConversationState:
        return route(state)

    def _node_enrich(self, state: ConversationState) -> ConversationState:
        return enrich(state, self.embed_client, self.embed_model, self.redis_client, self.postgres_url, state["user_id"])

    def _node_ei_calc(self, state: ConversationState) -> ConversationState:
        return ei_calc(state)

    def _node_plan(self, state: ConversationState) -> ConversationState:
        return plan(state, self.postgres_url)

    def _node_respond(self, state: ConversationState) -> ConversationState:
        return respond(state)

    def _node_think(self, state: ConversationState) -> ConversationState:
        return think(state, self.embed_client, self.embed_model, self.redis_client, self.postgres_url, state["user_id"])

    def _node_judge(self, state: ConversationState) -> ConversationState:
        return judge(state)

    def _node_evaluate(self, state: ConversationState) -> ConversationState:
        return evaluate(state)

    def _node_correct(self, state: ConversationState) -> ConversationState:
        return correct(state)

    def _node_salience(self, state: ConversationState) -> ConversationState:
        return analyze(state, self.embed_client, self.embed_model, self.redis_client, state["user_id"], self.postgres_url)

    def _node_dispatch(self, state: ConversationState) -> ConversationState:
        return dispatch(state, self.redis_client, self.postgres_url, self.embed_client, self.embed_model)

    def _node_agent_dispatch(self, state: ConversationState) -> ConversationState:
        return agent_dispatch_node(state)

    # Gesprächsvektor
    def _node_gespraechsvektor(self, state: ConversationState) -> ConversationState:
        from graph.nodes.gespraechsvektor import gespraechsvektor as _gv_fn
        return _gv_fn(state)
