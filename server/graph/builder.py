"""
Graph Builder — Fassade für die Graph-Konstruktion.

Stellt build_human_graph() und build_agent_graph() bereit.
Behält create_initial_state() als deprecated Wrapper bei.
"""

import logging
import warnings

import redis
from langgraph.graph.state import CompiledStateGraph

from graph.agent_graph import AgentGraph
from graph.character_graph import CharacterGraph
from graph.einwand import Einwandsurteil
from graph.human_graph import HumanGraph
from graph.state import ConversationState

logger = logging.getLogger("ki_server.graph")


def build_human_graph(
    redis_client: redis.Redis,
    postgres_url: str,
) -> tuple[CompiledStateGraph, HumanGraph]:
    """Baut den vollständigen Gesprächsgraphen für menschliche User."""
    graph = HumanGraph(redis_client, postgres_url)
    return graph.build(), graph


def build_agent_graph(
    redis_client: redis.Redis,
    postgres_url: str,
) -> tuple[CompiledStateGraph, AgentGraph]:
    """Baut den Analyse-Graphen für KI-User (Nova, etc.)."""
    graph = AgentGraph(redis_client, postgres_url)
    return graph.build(), graph


def build_character_graph(
    redis_client: redis.Redis,
    postgres_url: str,
) -> tuple[CompiledStateGraph, CharacterGraph]:
    """Baut den Charakter-Graphen (Pfad 2: Charakter reagiert)."""
    graph = CharacterGraph(redis_client, postgres_url)
    return graph.build(), graph


def create_initial_state(
    user_prompt:   str,
    user_id:       str,
    system_prompt: str = "",
    temperature:   float = 0.7,
) -> ConversationState:
    """
    DEPRECATED — Nutze stattdessen graph_instance.create_state().

    Erzeugt einen State über HumanGraph.create_state().
    Funktioniert ohne Graph-Instanz (erstellt intern keine).
    """
    warnings.warn(
        "create_initial_state() ist deprecated. Nutze graph_instance.create_state() stattdessen.",
        DeprecationWarning,
        stacklevel=2,
    )
    # Direkter Import um zirkuläre Abhängigkeit zu vermeiden
    from config import ASSISTANT_NAME


    default_prompt: str = (
        f"Du bist {ASSISTANT_NAME}. Antworte auf Deutsch."
    )

    from graph.base import MAX_CORRECTIONS

    return ConversationState(
        user_prompt   = user_prompt,
        user_id       = user_id,
        system_prompt = system_prompt if system_prompt else default_prompt,
        temperature   = temperature,
        intent         = "",
        needs_memory   = False,
        needs_web      = False,
        needs_timeline = False,
        timeline_query = {},
        tone           = "sachlich",
        management_action     = "",
        management_target     = "",
        management_target_typ = "titel",
        memory_context     = "",
        web_context        = "",
        session_turns      = [],
        gespraechs_modus   = "",
        user_intentionen   = [],
        user_emotion       = "",
        timeline_id        = None,
        management_result = "",
        management_detail = "",
        task_block       = "",
        task_context_cut = False,
        momentum = "mid",
        response    = "",
        model       = "",
        token_total = 0,
        self_trigger         = False,
        self_trigger_payload = {},
        tribunal_votes   = [],
        tribunal_verdict = "",
        tribunal_summary = "",
        correction_round = 0,
        max_corrections  = MAX_CORRECTIONS,
        pending_writes = [],
        agent_name    = "",
        agent_results = [],
        node_annotations = [],
        einwandsurteil = Einwandsurteil(),
    )
