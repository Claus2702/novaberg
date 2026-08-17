"""KzgAgent -- Verdichtung und Speicherung ins Kurzzeitgedaechtnis.

Graph-Aufbau und Routing-Logik. Die Business-Logik liegt in:
  verdichtung.py  -- LLM-Call: kern erzeugen
  speicher.py     -- Neuanlage + thematische Verstaerkung verwandter Eintraege
  queues.py       -- Promotion + Shadow + Dirty-Flag
"""

import logging

from agents.base import Bedarf, BaseAgent, AgentState
from langgraph.graph import StateGraph, END
from agents.kzg.magnete import magnete_aufloesen
from agents.kzg.verdichtung import verdichten
from agents.kzg.speicher import speichern
from agents.kzg.queues import queues_befuellen
from config import KZG_SALIENZ_MINIMUM
from memory.kzg import salienz_berechnen

logger = logging.getLogger("ki_server.agents.kzg")


class KzgAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "kzg"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["kzg_verdichten", "kzg_speichern", "kzg_thematisch_verstaerken"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["user"]


    @property
    def zustellart(self) -> str:
        """Laeuft in jedem Durchlauf, ohne Zustellentscheidung.

        Der KZG-Schreibpfad haengt am Dispatcher-Knoten und nicht am
        Aushang: Es gibt keine Entscheidung, ob er laeuft. Damit hat er
        auch keinen Aushang und keine Quote — ein Abgleich haette nichts
        zu vergleichen.
        """
        return "queue"

    @property
    def bedarf(self) -> list[Bedarf]:
        """Uebernimmt einen im selben Durchlauf angelegten Timeline-Eintrag.

        Ohne diesen Wert legt der Schreibpfad einen eigenen
        Erinnerungs-Anker fuer denselben Tag an — der Wert ist optional,
        sein Fehlen kostet eine Dublette und keinen Fehler.
        """
        return [Bedarf(
            schluessel="timeline_id",
            typ="int | None",
            bedeutung=(
                "ID des im SELBEN Durchlauf angelegten Timeline-Eintrags. "
                "NICHT die ID eines gefundenen oder gesuchten Eintrags."
            ),
        )]

    def build_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("schwelle_pruefen",  self._schwelle_pruefen)
        graph.add_node("magnete_aufloesen", magnete_aufloesen)
        graph.add_node("verdichten",        verdichten)
        graph.add_node("speichern",         speichern)
        graph.add_node("queues",            queues_befuellen)

        graph.set_entry_point("schwelle_pruefen")
        graph.add_conditional_edges("schwelle_pruefen", self._nach_schwelle)
        # Magnet-Aufloesung VOR Verdichtung — defensiv: Resolver-Fehler
        # verwerfen den teuren LLM-Call nicht; bei Abbruch danach bleibt
        # kein Waisenkind in der Timeline.
        graph.add_edge("magnete_aufloesen", "verdichten")
        graph.add_edge("verdichten",        "speichern")
        graph.add_edge("speichern",         "queues")
        graph.add_edge("queues",            END)

        return graph.compile()

    # --- Routing ---

    def _nach_schwelle(self, state: AgentState) -> str:
        if state["status"] == "abgelehnt":
            return END
        return "magnete_aufloesen"

    # --- Nodes ---

    def _schwelle_pruefen(self, state: AgentState) -> dict:
        """Prueft Salienz-Score gegen Konfigurationsschwelle.

        Verglichen wird die abgeleitete Salienz, nicht die rohe Modell-
        bewertung: Die Tore stehen seit dem Skalenumbau auf der gekruemmten
        Skala. Ein roher Wert gegen ein gekruemmtes Tor waeren zwei Skalen
        nebeneinander — genau der Zustand, den der Umbau beendet
        (novaberg-kzg-salienz_k.md §5).

        Der Eintrag existiert hier noch nicht, hat also null Verstaerkungen;
        haeufigkeit 1 ist der Zustand beim Anlegen.
        """
        salienz_obj: dict = state["parameter"].get("salienz_obj", {})
        eingang: float = salienz_obj.get("salienz", 0.0)
        score:   float = salienz_berechnen(eingang, 1)

        if score < KZG_SALIENZ_MINIMUM:
            logger.info(
                f"KZG-Agent: Salienz {score:.4f} (Eingang {eingang:.2f}) "
                f"< {KZG_SALIENZ_MINIMUM} — abgelehnt"
            )
            return {
                "status": "abgelehnt",
                "ergebnis": f"Salienz {score:.4f} unter Schwelle",
                "schritte": state["schritte"] + [
                    {"node": "schwelle_pruefen", "ergebnis": "abgelehnt", "score": score}
                ],
            }

        logger.info(
            f"KZG-Agent: Salienz {score:.4f} (Eingang {eingang:.2f}) "
            f">= {KZG_SALIENZ_MINIMUM} — angenommen"
        )
        return {
            "status": "laufend",
            "schritte": state["schritte"] + [
                {"node": "schwelle_pruefen", "ergebnis": "angenommen", "score": score}
            ],
        }
