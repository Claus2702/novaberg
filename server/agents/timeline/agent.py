"""TimelineAgent — Orchestrator fuer temporale Eintraege (CRUD).

Erweitert in Chat 42 (CRUD-Haertung):
- Erweiterte Taxonomie: reschedule als eigene Aktion
- Keyword-Hints + Verb-Mappings + Konfidenz im Classify-Node
- Verifikation nach Writes

Graph-Aufbau und Routing-Logik. Die Business-Logik liegt in:
  klassifikation.py — Aktionsklassifikation + Zeitausdruck-Extraktion per LLM (erweitert)
  resume.py         — Rueckfrage-Aufloesung (unveraendert)
  suche.py          — Keyword-Suche, Datumsbereich-Abfrage (unveraendert)
  crud.py           — Create (Zeitparser), Update/Reschedule (bi-temporal), Delete + Verifikation
  bestaetigung.py   — State-Bereinigung (unveraendert)
"""

import logging

from langgraph.graph import END, StateGraph

from agents.base import AgentState, BaseAgent
from agents.timeline.bestaetigung import bestaetigen
from agents.timeline.crud import ausfuehren
from agents.timeline.klassifikation import klassifizieren
from agents.timeline.resume import resume
from agents.timeline.suche import suchen

logger = logging.getLogger("ki_server.agents.timeline")


class TimelineAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "timeline"

    @property
    def faehigkeiten(self) -> list[str]:
        return [
            "termin_erstellen",
            "termin_lesen",
            "termin_verschieben",
            "termin_loeschen",
            "termin_details_aendern",
        ]

    @property
    def graph_eignung(self) -> list[str]:
        return ["user"]


    @property
    def negativfaelle(self) -> list[str]:
        """Aeusserungen mit Zeitbezug, die KEIN Timeline-Auftrag sind."""
        return [
            "Zeitangaben in einer Erzaehlung ueber die Vergangenheit "
            "('letztes Jahr war ich in Rom') — es gibt nichts einzutragen",
            "Zeitangaben als Teil einer Sachfrage "
            "('wie lange braucht Licht von der Sonne') — das ist Wissen, kein Termin",
            "Zeitangaben in einer Absichtserklaerung ohne Datum "
            "('irgendwann will ich mal') — ohne Zeitpunkt kein Eintrag",
        ]

    @property
    def grenze(self) -> list[str]:
        """Was dieser Dienst nicht tut."""
        return [
            "keine Zeitraum-Arithmetik ueber mehrere Eintraege",
            "keine Termine fuer dritte Personen ohne benannten Bezug",
            "keine Wiederholungsregeln ausser jaehrlich",
        ]

    @property
    def quote(self) -> dict[str, int]:
        """Geschaetzter Anteil: ein Viertel der Nutzer-Aeusserungen."""
        return {"user": 25}


    @property
    def ausgaenge(self) -> frozenset[str]:
        """Bedient alle vier Ausgaenge, einschliesslich der Ablehnung.

        Der vierte Ausgang traegt einen Korrekturvorschlag: Erkennt die
        Klassifikation Zeitangaben ohne Ereignis oder Ereignisse ohne Zeitpunkt,
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
        if action in ("create", "read", "update", "delete", "reschedule"):
            return "suchen"
        return "klassifizieren"

    def _nach_klassifikation(self, state: AgentState) -> str:
        if state["status"] in ("fehler", "rejected"):
            return END
        return "suchen"

    def _nach_resume(self, state: AgentState) -> str:
        status = state["status"]
        if status in ("fehler", "rueckfrage", "abgeschlossen"):
            return END
        action = state["parameter"].get("action", "")
        if action in ("update", "delete", "reschedule") and not state["parameter"].get("termin"):
            return "suchen"
        return "ausfuehren"

    def _nach_suche(self, state: AgentState) -> str:
        status = state["status"]
        if status in ("fehler", "rueckfrage", "abgeschlossen"):
            return END
        return "ausfuehren"

    # --- Validierung ---

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

        gueltige_aktionen = {"create", "read", "update", "delete", "reschedule", "agent"}
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
