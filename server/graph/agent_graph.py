"""
AgentGraph — Leichtgewichtiger Analyse-Graph für KI-User (Nova, etc.).

Flow:
  Enricher → Salience → Dispatcher → END

Kein Router, kein Responder, kein Tribunal, keine Korrekturschleife.
Wird vom Shadow Delivery Service genutzt, um Novas eigene Impulse
durch Salienz-Analyse und Gedächtnis-Dispatcher zu schleusen.
"""

import logging

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from graph.base  import GraphBase
from graph.state import ConversationState

logger = logging.getLogger("ki_server.graph.agent")


class AgentGraph(GraphBase):
    """Leichtgewichtiger Analyse-Graph für KI-User."""

    def build(self) -> CompiledStateGraph:
        """Baut den Analyse-Graphen mit Enricher → Salience → Dispatcher."""

        graph = StateGraph(ConversationState)

        # ── Nodes registrieren ─────────────────
        graph.add_node("enricher",   self._node_enrich)
        graph.add_node("salience",   self._node_salience)
        graph.add_node("dispatcher", self._node_dispatch)

        # ── Kanten ─────────────────────────────
        graph.set_entry_point("enricher")
        graph.add_edge("enricher",   "salience")
        graph.add_edge("salience",   "dispatcher")
        graph.add_edge("dispatcher", END)

        # ── Kompilieren ────────────────────────
        compiled = graph.compile()
        logger.info("Agent-Graph kompiliert und bereit.")

        return compiled

    def create_state(
        self,
        user_prompt: str,
        user_id:     str,
        **kwargs,
    ) -> ConversationState:
        """Erzeugt einen State für Analyse-Durchläufe (kein System-Prompt, T=0)."""

        return ConversationState(
            # Eingang
            user_prompt   = user_prompt,
            user_id       = user_id,
            system_prompt = "",
            temperature   = 0.0,

            # Perzeption (nicht genutzt, aber TypedDict erfordert alle Felder)
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

            # Management-Routing
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

            # Emotionale Intelligenz
            emotions_verlauf     = [],
            emotions_vektor      = "",
            sprach_stil          = "",
            beziehungs_kontext   = "",

            # Planner
            management_result = "",
            management_detail = "",
            task_block       = "",
            task_context_cut = False,

            # Momentum
            momentum = "mid",

            # Responder
            response    = "",
            model       = "",
            token_total = 0,

            # Tribunal
            tribunal_votes   = [],
            tribunal_verdict = "",
            tribunal_summary = "",

            # Korrektur-Loop (deaktiviert)
            correction_round = 0,
            max_corrections  = 0,

            # Pending Writes
            pending_writes = [],

            # Agent-System (Epic 11)
            agent_name    = "",
            agent_results = [],

            # Interne Anmerkungen
            node_annotations = [],
        )
