"""NotizenAgent -- Orchestrator fuer Freiform-Inhalte (CRUD + erweiterte Aktionen).

Erweitert in Chat 42 (CRUD-Haertung):
- Erweiterte Taxonomie: add_content, remove_content, clear_content, rename
- Keyword-Hints + Verb-Mappings + Konfidenz im Classify-Node
- Keine Pflicht-Rueckfrage (nur bei niedriger Konfidenz via bestehenden Mechanismus)

Graph-Aufbau und Routing-Logik. Die Business-Logik liegt in:
  klassifikation.py -- Aktionsklassifikation per LLM (erweitert)
  resume.py         -- Rueckfrage-Aufloesung (unveraendert)
  suche.py          -- Gewichtete Multi-Feld-Suche (unveraendert)
  crud.py           -- Create, Update, Delete, Append, ClearContent, Rename + Verifikation
  bestaetigung.py   -- State-Bereinigung (unveraendert)
"""

import logging

from langgraph.graph import END, StateGraph

from agents.base import AgentState, BaseAgent
from agents.notizen.bestaetigung import bestaetigen
from agents.notizen.crud import ausfuehren
from agents.notizen.klassifikation import klassifizieren
from agents.notizen.resume import resume
from agents.notizen.suche import suchen

logger = logging.getLogger("ki_server.agents.notizen")


class NotizenAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "notizen"

    @property
    def faehigkeiten(self) -> list[str]:
        return [
            "notiz_erstellen",
            "notiz_lesen",
            "notiz_aktualisieren",
            "notiz_loeschen",
            "notiz_anhaengen",
            "notiz_inhalt_hinzufuegen",
            "notiz_inhalt_entfernen",
            "notiz_leeren",
            "notiz_umbenennen",
        ]

    @property
    def graph_eignung(self) -> list[str]:
        return ["user"]


    @property
    def negativfaelle(self) -> list[str]:
        """Aeusserungen ueber Inhalte, die KEIN Notiz-Auftrag sind."""
        return [
            "blosse Erwaehnung eines Themas, das zufaellig auch in einer "
            "Notiz steht — Erwaehnung ist keine Aenderung",
            "eine Aufzaehlung im Gespraech ohne Speicherabsicht "
            "('mir fallen drei Gruende ein')",
            "eine Frage nach Weltwissen, die wie eine Liste klingt "
            "('welche Planeten gibt es')",
        ]

    @property
    def grenze(self) -> list[str]:
        """Was dieser Dienst nicht tut."""
        return [
            "keine Termine — Zeitgebundenes gehoert nicht hierher",
            "keine Verhaltensregeln fuer Nova",
            "keine Zusammenfassung fremder Dokumente",
        ]

    @property
    def quote(self) -> dict[str, int]:
        """Geschaetzter Anteil: ein Viertel der Nutzer-Aeusserungen."""
        return {"user": 25}


    @property
    def ausgaenge(self) -> frozenset[str]:
        """Bedient alle vier Ausgaenge, einschliesslich der Ablehnung.

        Der vierte Ausgang traegt einen Korrekturvorschlag: Erkennt die
        Klassifikation Erwaehnungen ohne Aenderungsabsicht,
        lehnt der Dienst mit Befund, Beleg und Gegenangebot ab statt mit
        einem blanken Nein. Damit darf er Zweifelsfaelle bekommen — die
        Zustellung im Zweifel setzt voraus, dass die Fachabteilung
        ablehnen **kann**.
        """
        return frozenset(
            {"abgeschlossen", "fehler", "rueckfrage", "abgelehnt"}
        )

    def build_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("validieren",     self._validieren)
        graph.add_node("resume",         resume)
        graph.add_node("klassifizieren", klassifizieren)
        graph.add_node("suchen",         suchen)
        graph.add_node("ausfuehren",     ausfuehren)
        graph.add_node("bestaetigen",    bestaetigen)

        graph.set_entry_point("validieren")
        graph.add_conditional_edges("validieren",     self._nach_validierung)
        graph.add_conditional_edges("resume",         self._nach_resume)
        graph.add_conditional_edges("klassifizieren", self._nach_klassifikation)
        graph.add_conditional_edges("suchen",         self._nach_suche)
        graph.add_edge("ausfuehren",  "bestaetigen")
        graph.add_edge("bestaetigen", END)

        return graph.compile()

    # --- Routing ---

    def _nach_validierung(self, state: AgentState) -> str:
        action = state["parameter"].get("action", "")
        if state["status"] == "fehler":
            return END
        if state["parameter"].get("resume"):
            return "resume"
        if action == "create":
            return "ausfuehren"
        if action in (
            "read",
            "update",
            "delete",
            "append",
            "add_content",
            "remove_content",
            "clear_content",
            "rename",
        ):
            return "suchen"
        return "klassifizieren"

    def _nach_klassifikation(self, state: AgentState) -> str:
        if state["status"] in ("fehler", "rejected"):
            return END
        action = state["parameter"].get("action", "")
        if action == "create":
            return "ausfuehren"
        return "suchen"

    def _nach_resume(self, state: AgentState) -> str:
        status = state["status"]
        if status in ("fehler", "rueckfrage", "abgeschlossen"):
            return END
        action = state["parameter"].get("action", "")
        if action in (
            "update",
            "delete",
            "append",
            "add_content",
            "remove_content",
            "clear_content",
        ) and not state["parameter"].get("notiz"):
            return "suchen"
        return "ausfuehren"

    def _nach_suche(self, state: AgentState) -> str:
        status = state["status"]
        if status in ("fehler", "rueckfrage", "abgeschlossen"):
            return END
        return "ausfuehren"

    # --- Nodes ---

    def _validieren(self, state: AgentState) -> dict:
        """Prueft ob die Aufgabe gueltig ist."""
        action = state["parameter"].get("action", "")

        if not action:
            return {
                "status": "fehler",
                "fehler": "Keine Aktion angegeben",
                "schritte": state["schritte"]
                + [{"node": "validieren", "ergebnis": "keine_aktion"}],
            }

        gueltige_aktionen = {
            "create", "read", "update", "delete", "append",
            "add_content", "remove_content", "clear_content", "rename",
            "agent",
        }
        if action not in gueltige_aktionen:
            return {
                "status": "fehler",
                "fehler": f"Unbekannte Aktion: {action}",
                "schritte": state["schritte"]
                + [{"node": "validieren", "ergebnis": "ungueltige_aktion"}],
            }

        return {
            "status": "laufend",
            "schritte": state["schritte"]
            + [{"node": "validieren", "ergebnis": "ok", "action": action}],
        }
