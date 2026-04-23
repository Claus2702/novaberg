"""
CharacterGraph — Pfad 2: Charakter reagiert.

Wird durch ein Event ausgelöst (User hat geschrieben oder Self-Trigger).
Liest den Chat, entscheidet, handelt optional, antwortet, speichert.

Flow:
  Enricher → EI-Calc → Router → [Planner ⇄ Agent]* →
  GV-Node → Responder → Thinker → Tribunal → Evaluate →
  [Corrector]* → Salienz → Dispatcher → END

  [Planner ⇄ Agent]* = nur wenn Router management_action gesetzt hat (sternförmig)
  [Corrector]* = nur wenn Tribunal ablehnt (max 2 Runden)
"""

import logging

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from graph.base  import GraphBase
from graph.state import ConversationState

logger = logging.getLogger("ki_server.graph.character")


class CharacterGraph(GraphBase):
    """Pfad 2: Charakter reagiert — Lesen + Entscheiden + Antworten + Speichern."""

    def create_state(self, user_prompt: str, user_id: str, **kwargs) -> ConversationState:
        """Erzeugt einen frischen State für einen CharacterGraph-Durchlauf.

        Setzt `ei_calc_rolle="character"` und `perzeption_rolle="assistant"`,
        damit EI-Calc nur die Nova-Seite berechnet und Perzeption Novas
        finale Antwort analysiert (nicht den User-Prompt).
        """
        kwargs.setdefault("ei_calc_rolle", "character")
        kwargs.setdefault("perzeption_rolle", "assistant")
        return super().create_state(user_prompt=user_prompt, user_id=user_id, **kwargs)

    def build(self) -> CompiledStateGraph:
        """Baut den Charakter-Pfad und gibt ihn kompiliert zurück."""

        graph = StateGraph(ConversationState)

        # ── Nodes registrieren ─────────────────
        graph.add_node("enricher",        self._node_enrich)
        graph.add_node("ei_calc",         self._node_ei_calc)
        graph.add_node("router",          self._node_route)
        graph.add_node("planner",         self._node_plan)
        graph.add_node("agent_dispatch",  self._node_agent_dispatch)
        graph.add_node("gv_node",         self._node_gespraechsvektor)
        graph.add_node("responder",       self._node_respond)
        graph.add_node("thinker",         self._node_think)
        graph.add_node("tribunal",        self._node_judge)
        graph.add_node("evaluate",        self._node_evaluate)
        graph.add_node("corrector",          self._node_correct)
        graph.add_node("perzeption_assistant", self._node_perceive)
        graph.add_node("salience",           self._node_salience)
        graph.add_node("dispatcher",         self._node_dispatch)

        # ── Kanten ─────────────────────────────
        graph.set_entry_point("enricher")
        graph.add_edge("enricher",  "ei_calc")
        graph.add_edge("ei_calc",   "router")

        # Router → Planner oder GV-Node
        graph.add_conditional_edges(
            "router",
            self._after_router,
            {
                "planner": "planner",
                "gv_node": "gv_node",
            },
        )

        # Planner → Agent-Dispatch (wenn agent_name gesetzt) oder GV-Node
        graph.add_conditional_edges(
            "planner",
            self._after_planner,
            {
                "agent_dispatch": "agent_dispatch",
                "gv_node":        "gv_node",
            },
        )
        graph.add_edge("agent_dispatch", "planner")  # Schleife zurück zum Planner

        graph.add_edge("gv_node",    "responder")
        graph.add_edge("responder",  "thinker")
        graph.add_edge("thinker",    "tribunal")
        graph.add_edge("tribunal",   "evaluate")

        # Bedingte Kante nach Auswertung
        graph.add_conditional_edges(
            "evaluate",
            self._after_evaluate,
            {
                "output":    "perzeption_assistant",
                "correct":   "corrector",
                "fallback":  "perzeption_assistant",
            },
        )

        graph.add_edge("corrector",           "tribunal")
        graph.add_edge("perzeption_assistant", "salience")
        graph.add_edge("salience",            "dispatcher")
        graph.add_edge("dispatcher",          END)

        # ── Kompilieren ────────────────────────
        compiled = graph.compile()
        logger.info("CharacterGraph (Pfad 2) kompiliert und bereit.")

        return compiled

    # ── Bedingte Kanten ────────────────────────

    def _after_planner(self, state: ConversationState) -> str:
        """Entscheidet nach dem Planner: Agent ausführen oder weiter zum GV-Node."""
        if state.get("agent_name", ""):
            logger.info(f"Graph: Agent '{state['agent_name']}' angefordert — Dispatch")
            return "agent_dispatch"
        return "gv_node"

    def _after_router(self, state: ConversationState) -> str:
        """Planner nur wenn Router einen Management-Intent erkannt hat."""
        if state.get("management_action"):
            logger.info("Graph: Management-Intent erkannt — Planner aktiviert")
            return "planner"
        return "gv_node"

    def _after_evaluate(self, state: ConversationState) -> str:
        """Entscheidet ob Korrektur nötig oder weiter zur Salienz."""

        verdict: str = state["tribunal_verdict"]

        # ok → Salienz + Dispatcher
        if verdict == "ok":
            logger.info("Graph: Tribunal akzeptiert — weiter zu Salienz")
            return "output"

        # Max Korrekturen erreicht
        if state["correction_round"] >= state["max_corrections"]:

            if verdict == "warnung":
                logger.warning("Graph: Max Korrekturen, verdict=warnung — Ausgabe mit Einschränkung")
                return "output"

            logger.warning("Graph: Max Korrekturen, verdict=ablehnen — Fallback")
            state["response"] = (
                "Ich kann diese Anfrage leider nicht beantworten. "
                "Bitte formuliere deine Frage anders."
            )
            return "fallback"

        logger.info(f"Graph: verdict={verdict} — Korrektur-Runde {state['correction_round'] + 1}")
        return "correct"
