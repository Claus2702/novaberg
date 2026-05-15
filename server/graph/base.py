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
from graph.nodes.perzeption import perceive
from graph.nodes.router     import route
from graph.nodes.enricher  import enrich
from graph.nodes.ei_calc   import ei_calc
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

            # Perzeption
            perzeption_rolle    = kwargs.get("perzeption_rolle", "user"),
            ei_calc_rolle       = kwargs.get("ei_calc_rolle", "user"),
            intent              = "",
            tone                = "sachlich",
            prompt_thema        = "",
            current_emotion     = "neutral",
            current_arousal     = 0.5,
            beziehungs_dynamik  = "neutral",

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
            gespraechs_modus   = "",
            user_intentionen   = [],
            user_emotion       = "",
            raw_turns          = [],
            char_hash_dict     = {},
            session_turn_kern  = "",

            # Emotionale Intelligenz
            emotions_verlauf     = [],
            emotions_vektor      = "",
            sprach_stil          = "",
            beziehungs_kontext   = "",
            nova_kern            = "",
            nova_beziehung       = "",
            nova_adaptiv         = "",
            nova_intentionen     = "",
            nova_emotions        = "",

            # Nova-Emotion (Dual-Emotion Phase 2)
            nova_emotions_verlauf  = [],
            nova_emotions_vektor   = "",
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

            # Tribunal
            tribunal_votes   = [],
            tribunal_verdict = "",
            tribunal_summary = "",

            # Korrektur-Loop
            correction_round = 0,
            max_corrections  = self.MAX_CORRECTIONS,

            # Pending Writes (Salienz + Planner → Dispatcher)
            pending_writes = [],

            # Agent-System (Epic 11)
            agent_name    = "",
            agent_results = [],

            # Charakter-Identität + Direktiven
            charakter_anweisungen = [],
            direktiven = [],

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

    def _node_reduce(self, state: ConversationState) -> ConversationState:
        return reduce_memory(state)

    # Gesprächsvektor
    def _node_gespraechsvektor(self, state: ConversationState) -> ConversationState:
        from graph.nodes.gespraechsvektor import gespraechsvektor as _gv_fn
        return _gv_fn(state)
