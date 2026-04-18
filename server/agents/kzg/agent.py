"""KzgAgent -- Verdichtung und Speicherung ins Kurzzeitgedaechtnis.

Graph-Aufbau und Routing-Logik. Die Business-Logik liegt in:
  verdichtung.py  -- LLM-Call: kern erzeugen
  aehnlichkeit.py -- Embedding + Redis-Vektorsuche
  speicher.py     -- Store neu / Verstaerkung
  queues.py       -- Promotion + Shadow + Dirty-Flag
"""

import logging

from agents.base import BaseAgent, AgentState
from langgraph.graph import StateGraph, END
from agents.kzg.verdichtung import verdichten
from agents.kzg.aehnlichkeit import aehnlichkeit_pruefen
from agents.kzg.speicher import speichern
from agents.kzg.queues import queues_befuellen
from config import KZG_SALIENZ_MINIMUM

logger = logging.getLogger("ki_server.agents.kzg")


class KzgAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "kzg"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["kzg_verdichten", "kzg_speichern", "kzg_verstaerken"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["user"]

    def build_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("schwelle_pruefen", self._schwelle_pruefen)
        graph.add_node("verdichten",       verdichten)
        graph.add_node("aehnlichkeit",     aehnlichkeit_pruefen)
        graph.add_node("speichern",        speichern)
        graph.add_node("queues",           queues_befuellen)

        graph.set_entry_point("schwelle_pruefen")
        graph.add_conditional_edges("schwelle_pruefen", self._nach_schwelle)
        graph.add_edge("verdichten",   "aehnlichkeit")
        graph.add_edge("aehnlichkeit", "speichern")
        graph.add_edge("speichern",    "queues")
        graph.add_edge("queues",       END)

        return graph.compile()

    # --- Routing ---

    def _nach_schwelle(self, state: AgentState) -> str:
        if state["status"] == "abgelehnt":
            return END
        return "verdichten"

    # --- Nodes ---

    def _schwelle_pruefen(self, state: AgentState) -> dict:
        """Prueft Salienz-Score gegen Konfigurationsschwelle."""
        salienz_obj: dict = state["parameter"].get("salienz_obj", {})
        score: float = salienz_obj.get("salienz", 0.0)

        if score < KZG_SALIENZ_MINIMUM:
            logger.info(f"KZG-Agent: Salienz {score:.2f} < {KZG_SALIENZ_MINIMUM} — abgelehnt")
            return {
                "status": "abgelehnt",
                "ergebnis": f"Salienz {score:.2f} unter Schwelle",
                "schritte": state["schritte"] + [
                    {"node": "schwelle_pruefen", "ergebnis": "abgelehnt", "score": score}
                ],
            }

        logger.info(f"KZG-Agent: Salienz {score:.2f} >= {KZG_SALIENZ_MINIMUM} — angenommen")
        return {
            "status": "laufend",
            "schritte": state["schritte"] + [
                {"node": "schwelle_pruefen", "ergebnis": "angenommen", "score": score}
            ],
        }
