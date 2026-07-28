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

from config                 import ASSISTANT_NAME, ASSISTANT_USER_ID
from graph.state           import ConversationState
from graph.personality     import Personality, InternalPersonality
from graph.nodes.perzeption import perceive
from graph.nodes.router     import route
from graph.nodes.enricher  import enrich
from graph.nodes.ei_calc   import ei_calc
from graph.nodes.emotionale_gravitation import emotionale_gravitation_anwenden
from graph.nodes.planner   import plan
from graph.nodes.reducer   import reduce_memory
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
        redis_client: redis.Redis,
        postgres_url: str,
    ) -> None:
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

    def create_state(
        self,
        user_prompt:   str,
        user_id:       str,
        character_id:  str = "",
        system_prompt: str = (
            f"Du bist {ASSISTANT_NAME}. Antworte auf Deutsch."
        ),
        temperature:   float = 0.7,
        **kwargs,
    ) -> ConversationState:
        """Erzeugt einen frischen State für einen neuen Gesprächs-Turn."""

        return ConversationState(
            # Eingang
            user_prompt   = user_prompt,
            user_id       = user_id,
            character_id  = character_id or ASSISTANT_USER_ID,
            turn_id       = kwargs.get("turn_id", ""),
            system_prompt = system_prompt,
            temperature   = temperature,

            # Event Context
            event_source  = kwargs.get("event_source", "user"),
            event_payload = kwargs.get("event_payload", {}),

            # Personality-Klassen (Single source of truth nach Phase 3)
            external = Personality(),
            internal = InternalPersonality(),

            # Rollen-Marker fuer Graph-Switches
            perzeption_rolle = kwargs.get("perzeption_rolle", "user"),
            ei_calc_rolle    = kwargs.get("ei_calc_rolle", "user"),
            # Default "human": entspricht dem bisherigen Verhalten fuer jeden
            # Aufrufer, der die Rolle nicht setzt. CharacterGraph und
            # AgentGraph setzen sie ausdruecklich.
            graph_rolle      = kwargs.get("graph_rolle", "human"),

            # Router
            needs_memory   = False,
            needs_web      = False,
            needs_timeline = False,
            timeline_query = {},

            # Management-Routing (Router → Planner)
            management_action     = "",
            management_target     = "",
            management_target_typ = "titel",

            # Enricher
            memory_context     = "",
            web_context        = "",
            session_turns      = [],
            user_intentionen   = [],
            raw_turns          = [],
            session_turn_kern  = "",
            timeline_id        = None,

            # Emotionale Intelligenz (berechnete Hilfsfelder, nicht in Klassen)
            emotions_verlauf     = [],

            # Nova-Emotion (bleibt flach: Liste mit Empathie-Modulation + Konflikt-Bool)
            nova_emotions_verlauf  = [],
            nova_emotion_konflikt  = False,

            # Planner (Management Plan-Phase)
            management_result = "",
            management_detail = "",
            task_block       = "",
            task_context_cut = False,

            # Momentum (für Shadow Delivery Service via Redis)
            momentum = "mid",

            # Responder
            response    = "",
            model       = "",
            token_total = 0,

            # Thinker / Self-Trigger
            self_trigger         = False,
            self_trigger_payload = {},

            # Tribunal
            tribunal_votes   = [],
            tribunal_verdict = "",
            tribunal_summary = "",

            # Korrektur-Loop
            correction_round = 0,
            max_corrections  = self.MAX_CORRECTIONS,

            # Pending Writes (Salienz + Planner → Dispatcher)
            pending_writes = [],

            # Salienz der Nutzeraeusserung (Chat 112).
            # Kein Default-Wert, sondern None: Der HumanGraph rechnet sie im
            # Salienz-Node aus, der CharacterGraph bekommt sie ueber das
            # Event-Payload gereicht, und der AgentGraph hat keine — dort
            # bleibt sie None, weil es keine Nutzeraeusserung gibt.
            salienz_human = kwargs.get("salienz_human"),

            # Agent-System (Epic 11)
            agent_name    = "",
            agent_results = [],

            # Gesprächsvektor (Epic 9)
            gespraechsvektor = "",

            # Interne Anmerkungen
            node_annotations = [],
        )

    # ── Node-Wrapper ───────────────────────────

    def _node_perceive(self, state: ConversationState) -> ConversationState:
        return perceive(state)

    def _node_route(self, state: ConversationState) -> ConversationState:
        return route(state)

    def _node_enrich(self, state: ConversationState) -> ConversationState:
        return enrich(state, self.redis_client, self.postgres_url, state["user_id"])

    def _node_ei_calc(self, state: ConversationState) -> ConversationState:
        return ei_calc(state)

    def _node_emotionale_gravitation(self, state: ConversationState) -> ConversationState:
        return emotionale_gravitation_anwenden(state)

    def _node_plan(self, state: ConversationState) -> ConversationState:
        return plan(state, self.postgres_url)

    def _node_respond(self, state: ConversationState) -> ConversationState:
        return respond(state)

    def _node_think(self, state: ConversationState) -> ConversationState:
        return think(state, self.redis_client, self.postgres_url, state["user_id"])

    def _node_judge(self, state: ConversationState) -> ConversationState:
        return judge(state)

    def _node_evaluate(self, state: ConversationState) -> ConversationState:
        return evaluate(state)

    def _node_correct(self, state: ConversationState) -> ConversationState:
        return correct(state)

    def _node_salience(self, state: ConversationState) -> ConversationState:
        return analyze(state, self.redis_client, state["user_id"], self.postgres_url)

    def _node_dispatch(self, state: ConversationState) -> ConversationState:
        return dispatch(state, self.redis_client, self.postgres_url)

    def _node_agent_dispatch(self, state: ConversationState) -> ConversationState:
        return agent_dispatch_node(state)

    def _node_reduce(self, state: ConversationState) -> ConversationState:
        return reduce_memory(state)

    # Gesprächsvektor
    def _node_gespraechsvektor(self, state: ConversationState) -> ConversationState:
        from graph.nodes.gespraechsvektor import gespraechsvektor as _gv_fn
        return _gv_fn(state)

    # CharacterGraph-Eingangsnode (PFAD2-PERZEPTION-FIX Phase 2)
    def _node_db_zugriff(self, state: ConversationState) -> ConversationState:
        from graph.nodes.db_zugriff import db_zugriff
        return db_zugriff(state)

    # CharacterGraph-Persistierungs-Node (PFAD2-PERZEPTION-FIX Phase 2)
    def _node_ei_calc_persist(self, state: ConversationState) -> ConversationState:
        from graph.nodes.ei_calc_persist import ei_calc_persist
        return ei_calc_persist(state)
