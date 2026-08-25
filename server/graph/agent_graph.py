"""
AgentGraph — Leichtgewichtiger Analyse-Graph für KI-User (Nova, etc.).

Flow:
  Enricher → Salience → Dispatcher → END

Kein Router, kein Responder, kein Tribunal, keine Korrekturschleife.
Wird vom Shadow Delivery Service genutzt, um Novas eigene Impulse
durch Salienz-Analyse und Gedächtnis-Dispatcher zu schleusen.
"""

import logging

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from graph.base import GraphBase
from graph.state import ConversationState

logger = logging.getLogger("ki_server.graph.agent")


class AgentGraph(GraphBase):
    """Leichtgewichtiger Analyse-Graph für KI-User."""

    # Analyse-Graph hat keine Korrektur-Schleife (kein Tribunal, kein Corrector)
    MAX_CORRECTIONS: int = 0

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

    def create_state(self, user_prompt: str, user_id: str, **kwargs) -> ConversationState:
        """Erzeugt einen frischen State für Analyse-Durchläufe.

        Delegiert an GraphBase.create_state(), damit alle State-Felder
        (inkl. Chat-60-Felder wie character_id, event_source, nova_*)
        konsistent mit HumanGraph/CharacterGraph gesetzt werden.
        Setzt nur die analyse-spezifischen Defaults: leerer System-Prompt,
        Temperature 0.0.
        """
        kwargs.setdefault("graph_rolle",   "agent")
        kwargs.setdefault("system_prompt", "")
        kwargs.setdefault("temperature",   0.0)
        return super().create_state(user_prompt=user_prompt, user_id=user_id, **kwargs)
