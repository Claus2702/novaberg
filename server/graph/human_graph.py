"""
HumanGraph — Vollständiger Gesprächsgraph für menschliche User.

Flow:
  Perzeption → Router → Enricher → [Planner]* → Responder → Thinker → Tribunal → Evaluate
                                                                        ↓
                                                          ok → Salience → Dispatcher → END
                                                          ↓
                                                   Corrector → Tribunal (max 2 Runden)

  [Planner]* = nur wenn Router management_action gesetzt hat
"""

import logging

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from config      import ASSISTANT_NAME
from graph.base  import GraphBase
from graph.state import ConversationState

logger = logging.getLogger("ki_server.graph.human")


class HumanGraph(GraphBase):
    """Vollständiger Gesprächsgraph für menschliche User."""

    def build(self) -> CompiledStateGraph:
        """Baut den vollständigen Gesprächsgraphen und gibt ihn kompiliert zurück."""

        graph = StateGraph(ConversationState)

        # ── Nodes registrieren ─────────────────
        graph.add_node("perzeption", self._node_perceive)
        graph.add_node("router",     self._node_route)
        graph.add_node("enricher",   self._node_enrich)
        graph.add_node("planner",    self._node_plan)
        graph.add_node("responder",  self._node_respond)
        graph.add_node("thinker",    self._node_think)
        graph.add_node("tribunal",   self._node_judge)
        graph.add_node("evaluate",   self._node_evaluate)
        graph.add_node("corrector",  self._node_correct)
        graph.add_node("salience",        self._node_salience)
        graph.add_node("dispatcher",      self._node_dispatch)
        graph.add_node("agent_dispatch",  self._node_agent_dispatch)
        graph.add_node("gv_node", self._node_gespraechsvektor)

        # ── Kanten ─────────────────────────────
        graph.set_entry_point("perzeption")
        graph.add_edge("perzeption", "router")
        graph.add_edge("router", "enricher")

        # Enricher → Planner oder Gesprächsvektor
        graph.add_conditional_edges(
            "enricher",
            self._after_enricher,
            {
                "planner":           "planner",
                "gv_node":  "gv_node",
            },
        )

        # Planner → Agent-Dispatch (wenn agent_name gesetzt) oder Gesprächsvektor
        graph.add_conditional_edges(
            "planner",
            self._after_planner,
            {
                "agent_dispatch":    "agent_dispatch",
                "gv_node":  "gv_node",
            },
        )
        graph.add_edge("agent_dispatch", "planner")        # Schleife zurueck zum Planner
        graph.add_edge("gv_node", "responder")    # GV → Responder (immer)
        graph.add_edge("responder", "thinker")
        graph.add_edge("thinker",   "tribunal")
        graph.add_edge("tribunal",  "evaluate")

        # Bedingte Kante nach Auswertung
        graph.add_conditional_edges(
            "evaluate",
            self._after_evaluate,
            {
                "output":   "salience",
                "correct":  "corrector",
                "fallback": END,
            },
        )

        graph.add_edge("corrector",  "tribunal")
        graph.add_edge("salience",   "dispatcher")
        graph.add_edge("dispatcher", END)

        # ── Kompilieren ────────────────────────
        compiled = graph.compile()
        logger.info("Gesprächsgraph kompiliert und bereit.")

        return compiled

    def create_state(
        self,
        user_prompt:   str,
        user_id:       str,
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
            system_prompt = system_prompt,
            temperature   = temperature,

            # Perzeption
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

            # Emotionale Intelligenz
            emotions_verlauf     = [],
            emotions_vektor      = "",
            sprach_stil          = "",
            beziehungs_kontext   = "",

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

    # ── Bedingte Kanten ────────────────────────

    def _after_planner(self, state: ConversationState) -> str:
        """Entscheidet nach dem Planner: Agent ausfuehren oder weiter zum GV-Node."""
        if state.get("agent_name", ""):
            logger.info(f"Graph: Agent '{state['agent_name']}' angefordert — Dispatch")
            return "agent_dispatch"
        return "gv_node"

    def _after_enricher(self, state: ConversationState) -> str:
        """Planner nur wenn Router einen Management-Intent erkannt hat."""
        if state.get("management_action"):
            logger.info("Graph: Management-Intent erkannt — Planner aktiviert")
            return "planner"
        return "gv_node"

    def _after_evaluate(self, state: ConversationState) -> str:
        """Entscheidet ob Korrektur nötig oder Ausgabe erfolgt."""

        verdict: str = state["tribunal_verdict"]

        # ok → Salienz → Dispatcher → Ende
        if verdict == "ok":
            logger.info("Graph: Tribunal akzeptiert — Salienz + Dispatcher")
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
