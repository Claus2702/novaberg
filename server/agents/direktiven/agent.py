"""DirektivenAgent -- Orchestrator fuer Verhaltensanweisungen (CRUD).

Erweitert in Chat 42 (CRUD-Haertung):
- Neuer Node 'db_validieren' zwischen Klassifikation und Ausfuehrung
- Pflicht-Rueckfrage fuer alle Schreiboperationen (HITL-Gate)
- Erweiterte Taxonomie: create, read, update, delete, reactivate

Graph-Aufbau und Routing-Logik. Die Business-Logik liegt in:
  klassifikation.py -- Aktionsklassifikation + Kontext-Aufloesung per LLM
  crud.py           -- Create, Read, Update, Delete, Reactivate + Validierung + Verifikation
  resume.py         -- Deutung der Antwort auf eine Rueckfrage (Tor vor `ausfuehren`)
"""

import logging

from langgraph.graph import END, StateGraph

from agents.base import AgentState, BaseAgent
from agents.direktiven.crud import ausfuehren, validieren_gegen_db
from agents.direktiven.klassifikation import klassifizieren
from agents.direktiven.resume import read_answer

logger = logging.getLogger("ki_server.agents.direktiven")


class DirektivenAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "direktiven"

    @property
    def faehigkeiten(self) -> list[str]:
        return [
            "direktive_erstellen",
            "direktive_lesen",
            "direktive_aendern",
            "direktive_loeschen",
            "direktive_wiederherstellen",
        ]

    @property
    def graph_eignung(self) -> list[str]:
        return ["user"]


    @property
    def negativfaelle(self) -> list[str]:
        """Aeusserungen, die wie eine Regel klingen und keine sind."""
        return [
            "eine einmalige Bitte fuer den laufenden Turn "
            "('antworte kurz') — das ist keine dauerhafte Regel",
            "eine Kritik ohne Regelinhalt ('das war zu lang') — "
            "Rueckmeldung ist keine Anweisung",
            "eine Aussage ueber Nova statt an Nova "
            "('du bist manchmal zu ausfuehrlich')",
        ]

    @property
    def grenze(self) -> list[str]:
        """Was dieser Dienst nicht tut."""
        return [
            "keine Charakterzuege — die gehoeren zur Identitaet",
            "keine inhaltlichen Vorgaben zu einem einzelnen Thema",
            "keine Regeln mit Bedingung ('wenn X, dann Y')",
        ]

    @property
    def quote(self) -> dict[str, int]:
        """Geschaetzter Anteil: eine Ausnahme, unter einem Achtel."""
        return {"user": 0}


    @property
    def ausgaenge(self) -> frozenset[str]:
        """Bedient alle vier Ausgaenge, einschliesslich der Ablehnung.

        Der vierte Ausgang traegt einen Korrekturvorschlag: Erkennt die
        Klassifikation einmalige Bitten, die keine dauerhafte Regel sind,
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

        graph.add_node("validieren",      self._validieren)
        graph.add_node("klassifizieren",  klassifizieren)
        graph.add_node("db_validieren",   self._db_validieren)
        graph.add_node("read_answer",     read_answer)
        graph.add_node("ausfuehren",      ausfuehren)

        graph.set_entry_point("validieren")
        graph.add_conditional_edges("validieren",      self._nach_validierung)
        graph.add_conditional_edges("klassifizieren",  self._nach_klassifikation)
        graph.add_conditional_edges("db_validieren",   self._nach_db_validierung)
        graph.add_conditional_edges("read_answer",     self._nach_deutung)
        graph.add_edge("ausfuehren", END)

        return graph.compile()

    # --- Routing ---

    def _nach_validierung(self, state: AgentState) -> str:
        """Waehlt den Knoten nach der Eingabepruefung.

        Vorbedingung: `state` hat `status` und `parameter`.
        Nachbedingung: `END` bei Fehler; `read_answer`, wenn eine Antwort auf
        eine Rueckfrage zurueckkommt (`resume`) -- sie wird gedeutet, bevor
        etwas ausgefuehrt wird, nie direkt nach `ausfuehren`;
        `db_validieren` bei bekannter Aktion, sonst `klassifizieren`.
        """
        action = state["parameter"].get("action", "")
        if state["status"] == "fehler":
            return END
        if state["parameter"].get("resume"):
            return "read_answer"
        if action in ("create", "read", "update", "delete", "reactivate"):
            return "db_validieren"
        return "klassifizieren"

    def _nach_klassifikation(self, state: AgentState) -> str:
        if state["status"] in ("fehler", "rejected"):
            return END
        return "db_validieren"

    def _nach_db_validierung(self, state: AgentState) -> str:
        if state["status"] == "fehler":
            return END
        if state["status"] == "rueckfrage":
            return END
        return "ausfuehren"

    def _nach_deutung(self, state: AgentState) -> str:
        """Waehlt den Knoten nach der Deutung der Antwort.

        Vorbedingung: `read_answer` hat `status` gesetzt.
        Nachbedingung: `ausfuehren` nur bei `laufend` -- der Zustimmung auf eine
        Ja/Nein-Frage; Ablehnung (`abgeschlossen`), unklare Antwort
        (`rueckfrage`) und Fehler enden ohne Ausfuehrung.
        """
        if state["status"] == "laufend":
            return "ausfuehren"
        return END

    # --- Input-Validierung ---

    def _validieren(self, state: AgentState) -> dict:
        """Prueft ob die Aufgabe gueltig ist."""
        action = state["parameter"].get("action", "")
        logger.debug(f"_validieren: Einstieg — action='{action}'")

        if not action:
            return {
                "status": "fehler",
                "fehler": "Keine Aktion angegeben",
                "schritte": state["schritte"]
                + [{"node": "validieren", "ergebnis": "keine_aktion"}],
            }

        gueltige_aktionen = {"create", "read", "update", "delete", "reactivate", "agent"}
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

    # --- DB-Validierung (HITL-Gate) ---

    def _db_validieren(self, state: AgentState) -> dict:
        """Prueft die Aktion gegen den DB-Zustand. Setzt Rueckfrage bei Bedarf."""
        action = state["parameter"].get("action", "")

        if action == "read":
            return {
                "schritte": state["schritte"]
                + [{"node": "db_validieren", "ergebnis": "skip_read"}],
            }

        result = validieren_gegen_db(state)

        logger.info(
            f"db_validieren: action='{action}', ok={result.ok}, "
            f"korrektur={result.korrektur}, bestaetigung={result.bestaetigung_noetig}, "
            f"grund='{result.grund[:60]}'"
        )

        if result.korrektur:
            state_update = {
                "parameter": {
                    **state["parameter"],
                    "action": result.korrektur,
                },
            }
        else:
            state_update = {}

        if not result.ok and not result.bestaetigung_noetig:
            return {
                **state_update,
                "status": "fehler",
                "fehler": result.grund,
                "schritte": state["schritte"]
                + [{"node": "db_validieren", "ergebnis": f"fehler: {result.grund[:40]}"}],
            }

        if result.bestaetigung_noetig:
            return {
                **state_update,
                "status": "rueckfrage",
                "rueckfrage": result.bestaetigung_text,
                "schritte": state["schritte"]
                + [{"node": "db_validieren", "ergebnis": "rueckfrage"}],
            }

        return {
            **state_update,
            "schritte": state["schritte"] + [{"node": "db_validieren", "ergebnis": "ok"}],
        }
