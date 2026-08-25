"""DelegationsAgent — Halluzinations-Ventil (VENT1).

3-Node-Subgraph:
  duplikat_pruefen → akte_erstellen (keine bestehende Akte)
                   → akte_anreichern (bestehende Akte gefunden)

Kein LLM-Call. Alle Daten kommen aus dem State (Salienz, EI-Pipeline).
Schreibt in PostgreSQL (delegations_akten + delegations_seiten).
"""

import logging

from langgraph.graph import END, StateGraph

from agents.base import AgentState, BaseAgent
from agents.delegation.akte import akte_anreichern, akte_erstellen
from agents.delegation.deduplizierung import duplikat_pruefen

logger = logging.getLogger("ki_server.agents.delegation")


class DelegationsAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "delegation"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["delegation_erstellen", "delegation_anreichern"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["user"]


    @property
    def zustellart(self) -> str:
        """Laeuft ueber den Hintergrund-Router, nicht ueber den Empfang.

        Die Deklaration `graph_eignung = ["user"]` ist Bestand und
        irrefuehrend: Auf dem Nutzerpfad ist dieser Dienst nicht waehlbar,
        weil kein Manager sein Ziel traegt. Er laeuft ueber einen
        Sonderfall des Hintergrund-Routers.

        **Das ist der Fall, an dem eine ungelesene Deklaration nachweislich
        verrottet ist** — dreizehn Angaben stimmten, diese nicht, und kein
        Lauf konnte es melden. Die Zustellart traegt die Wahrheit, bis die
        Graph-Eignung selbst berichtigt wird.
        """
        return "queue"

    def build_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("duplikat_pruefen", duplikat_pruefen)
        graph.add_node("akte_erstellen",   akte_erstellen)
        graph.add_node("akte_anreichern",  akte_anreichern)

        graph.set_entry_point("duplikat_pruefen")
        graph.add_conditional_edges("duplikat_pruefen", self._nach_duplikat)
        graph.add_edge("akte_erstellen",  END)
        graph.add_edge("akte_anreichern", END)

        return graph.compile()

    # --- Routing ---

    def _nach_duplikat(self, state: AgentState) -> str:
        if state["status"] == "fehler":
            return END
        if state["parameter"].get("bestehende_akte_id"):
            logger.debug("Routing: bestehende Akte → anreichern")
            return "akte_anreichern"
        logger.debug("Routing: keine Akte → erstellen")
        return "akte_erstellen"
