"""
HumanGraph — Pfad 1: User schreibt.

Verarbeitet den User-Input: Wahrnehmung, Kontext laden, EI berechnen,
Salienz bewerten, wegschreiben. Kein Responder — der Charakter
antwortet separat über den CharacterGraph (Pfad 2).

Flow:
  Perzeption → Enricher → EI-Calc → Salienz → Dispatcher → END

Kein LLM-Responder, kein Router, kein Tribunal.
Zwei LLM-Calls: Perzeption + Salienz.

Der Reducer wurde in Phase 4 aus dem HG-Pfad entfernt — kein HG-Konsument
liest memory_entries oder memory_context. Im CharacterGraph laeuft der
Reducer weiterhin zwischen Enricher und EI-Calc.
"""

import logging

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from graph.base  import GraphBase
from graph.state import ConversationState

logger = logging.getLogger("ki_server.graph.human")


class HumanGraph(GraphBase):
    """Pfad 1: User schreibt — Wahrnehmung + Speicherung."""

    def build(self) -> CompiledStateGraph:
        """Baut den User-Pfad und gibt ihn kompiliert zurück."""
        graph = StateGraph(ConversationState)

        # ── Nodes registrieren ─────────────────
        graph.add_node("perzeption", self._node_perceive)
        graph.add_node("enricher",   self._node_enrich)
        graph.add_node("ei_calc",    self._node_ei_calc)
        graph.add_node("salience",   self._node_salience)
        graph.add_node("dispatcher", self._node_dispatch)

        # ── Kanten (gerade Linie) ──────────────
        graph.set_entry_point("perzeption")
        graph.add_edge("perzeption", "enricher")
        graph.add_edge("enricher",   "ei_calc")
        graph.add_edge("ei_calc",    "salience")
        graph.add_edge("salience",   "dispatcher")
        graph.add_edge("dispatcher", END)

        # ── Kompilieren ────────────────────────
        compiled = graph.compile()
        logger.info("HumanGraph (Pfad 1) kompiliert und bereit.")

        return compiled
