"""
CharacterGraph — Pfad 2: Charakter reagiert.

Wird durch ein Event ausgelöst (User hat geschrieben oder Self-Trigger).
Liest den Chat, entscheidet, handelt optional, antwortet, speichert.

Flow (PFAD2-PERZEPTION-FIX Phase 2):
  db_zugriff → EI-Calc → Enricher → Reducer → Router → [Planner ⇄ Agent]* →
  GV-Node → Haltungsraum → [Verfasser]* → Responder → Thinker → Tribunal →
  Evaluate → [Corrector]* → perzeption_assistant → ei_calc_persist → Salienz →
  Dispatcher → END

  Haltungsraum rechnet die fuenf Verhaltensgroessen aus der Landschaft des
  GV-Nodes und Novas Zuwendungsrad. Sie steht vor der Verzweigung, weil der
  Verfasser bei `task_context_cut` uebersprungen wird
  (novaberg-haltungsraum_k.md §2).

  db_zugriff laedt Identitaeten und Nova-State, befuellt external/internal.
  EI-Calc steht vor dem Enricher, damit Enricher Novas modifizierten
  Zustand fuer die Memory-Auswahl kennt.
  ei_calc_persist wendet Plausibilitaeten auf Novas Perzeption an und
  persistiert Novas neun EI-Dimensionen in Redis (nova_state).

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
        kwargs.setdefault("graph_rolle",      "character")
        return super().create_state(user_prompt=user_prompt, user_id=user_id, **kwargs)

    def build(self) -> CompiledStateGraph:
        """Baut den Charakter-Pfad und gibt ihn kompiliert zurück."""
        graph = StateGraph(ConversationState)

        # ── Nodes registrieren ─────────────────
        graph.add_node("db_zugriff",      self._node_db_zugriff)
        graph.add_node("ei_calc",         self._node_ei_calc)
        graph.add_node("enricher",        self._node_enrich)
        graph.add_node("emotionale_gravitation", self._node_emotionale_gravitation)
        graph.add_node("reducer",         self._node_reduce)
        graph.add_node("router",          self._node_route)
        graph.add_node("planner",         self._node_plan)
        graph.add_node("agent_dispatch",  self._node_agent_dispatch)
        graph.add_node("gv_node",         self._node_gespraechsvektor)
        # Der Node heisst nach dem Raum, der Kanal nach seinem Ergebnis. Nicht
        # nur der Lesbarkeit wegen: LangGraph lehnt einen Node ab, der wie ein
        # State-Key heisst ("'haltung' is already being used as a state key").
        graph.add_node("haltungsraum",    self._node_haltung)
        graph.add_node("verfasser",       self._node_verfassen)
        graph.add_node("responder",       self._node_respond)
        graph.add_node("thinker",         self._node_think)
        graph.add_node("tribunal",        self._node_judge)
        graph.add_node("evaluate",        self._node_evaluate)
        graph.add_node("corrector",          self._node_correct)
        graph.add_node("perzeption_assistant", self._node_perceive)
        graph.add_node("ei_calc_persist",    self._node_ei_calc_persist)
        graph.add_node("salience",           self._node_salience)
        graph.add_node("dispatcher",         self._node_dispatch)

        # ── Kanten ─────────────────────────────
        # Reihenfolge geaendert (PFAD2-PERZEPTION-FIX Phase 2):
        # db_zugriff -> ei_calc -> enricher -> reducer -> router
        graph.set_entry_point("db_zugriff")
        graph.add_edge("db_zugriff", "ei_calc")
        graph.add_edge("ei_calc",    "enricher")
        # Die Gravitation sitzt zwischen Enricher und Reducer: Der Enricher
        # findet die Punkte, und alles Nachfolgende — GV-Node wie Responder —
        # soll Novas gefaerbte Lage sehen. Vor dem Enricher ginge es nicht, denn
        # dort entstehen die Punkte erst; nach dem GV-Node bliebe nur noch der
        # Ton der Antwort, nicht ihre Denkrichtung (Chat 113).
        graph.add_edge("enricher",   "emotionale_gravitation")
        graph.add_edge("emotionale_gravitation", "reducer")
        graph.add_edge("reducer",    "router")

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

        # GV-Node → Haltung: Der Haltungsraum braucht die Landschaft, und die
        # setzt erst der GV-Node (`gv_detail["cluster"]`).
        graph.add_edge("gv_node", "haltungsraum")

        # Haltungsraum → Verfasser oder direkt Responder.
        #
        # Die Verzweigung haengt an der Haltung und nicht mehr am GV-Node,
        # damit die Rechnung in JEDEM Turn laeuft. Im Verfasser stuende sie
        # falsch: Er wird beim Kontext-Schnitt uebersprungen, und der Responder
        # braucht den Umfang gerade dort, wo er allein steht
        # (novaberg-haltungsraum_k.md §2 "Wer rechnet").
        #
        # Bei `task_context_cut` sieht der Responder absichtlich fast nichts —
        # kein Gedaechtnis, kein Web, nur Identitaet, Stil und das Ergebnis der
        # Aufgabe. Diese Beschraenkung war die Loesung nach vier
        # Fix-Iterationen. Ein Verfasser, der in dieser Lage Gedaechtnis und
        # Web zusammenfasst, holt genau den Input zurueck, der entfernt wurde —
        # nur einen Node frueher und verdichtet. Deshalb laeuft er dort nicht
        # (novaberg-node-verfasser_k.md §5.1).
        graph.add_conditional_edges(
            "haltungsraum",
            self._after_haltung,
            {
                "verfasser": "verfasser",
                "responder": "responder",
            },
        )
        graph.add_edge("verfasser",  "responder")
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
        # ei_calc_persist konsolidiert und persistiert Nova-EI nach der
        # Perzeption-Assistant (PFAD2-PERZEPTION-FIX Phase 2).
        graph.add_edge("perzeption_assistant", "ei_calc_persist")
        graph.add_edge("ei_calc_persist",     "salience")
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

    def _after_haltung(self, state: ConversationState) -> str:
        """Verfasser überspringen, wenn der Kontext-Schnitt gilt.

        Hieß bis zum 31.07.2026 `_after_gv` und hing am GV-Node. Die
        Verzweigung sitzt jetzt einen Node später, weil die Haltungsrechnung
        dazwischen steht; das Kriterium ist unverändert.

        Bei `task_context_cut` ist der schmale Kontext des Responders Absicht,
        nicht Mangel. Ein Verfasser würde dort Gedächtnis und Web wieder
        einsammeln und verdichtet weiterreichen — genau den Input, dessen
        Entfernung die Halluzination bei Agent-Erfolg beendet hat.
        """
        if state.get("task_context_cut"):
            logger.info(
                "Graph: Kontext-Schnitt aktiv — Verfasser übersprungen, "
                "der Responder verarbeitet den Aufgaben-Block direkt"
            )
            return "responder"
        return "verfasser"

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
