"""CharakterIdentitaetAgent -- Orchestrator fuer Charakter-Anweisungen (CRUD).

Erweitert in Chat 42 (CRUD-Haertung):
- Neuer Node 'db_validieren' zwischen Klassifikation und Ausfuehrung
- Pflicht-Rueckfrage fuer alle Schreiboperationen (HITL-Gate)
- Erweiterte Taxonomie: create, read, update, delete, reactivate, replace, konsolidieren

Graph-Aufbau und Routing-Logik. Die Business-Logik liegt in:
  klassifikation.py -- Aktionsklassifikation per LLM
  crud.py           -- Create, Read, Update, Delete, Reactivate, Replace, Konsolidieren + Validierung + Verifikation
"""

import logging

from langgraph.graph import END, StateGraph

from agents.base import AgentState, BaseAgent
from agents.charakter_identitaet.crud import ausfuehren, validieren_gegen_db
from agents.charakter_identitaet.klassifikation import klassifizieren
from agents.charakter_identitaet.resume import resume

logger = logging.getLogger("ki_server.agents.charakter_identitaet")


class CharakterIdentitaetAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "charakter_identitaet"

    @property
    def faehigkeiten(self) -> list[str]:
        return [
            "charakter_anweisung_erstellen",
            "charakter_anweisung_lesen",
            "charakter_anweisung_aendern",
            "charakter_anweisung_loeschen",
            "charakter_anweisung_wiederherstellen",
            "charakter_ersetzen",
            "charakter_konsolidieren",
        ]

    @property
    def graph_eignung(self) -> list[str]:
        return ["user"]


    @property
    def negativfaelle(self) -> list[str]:
        """Aeusserungen, die wie Charakterzuweisung klingen und keine sind."""
        return [
            "emotionale Ausdruecke ('du bist toll') — das ist Rueckmeldung",
            "einmalige Rollenspiele ('antworte mal als Pirat') — "
            "kein dauerhafter Charakter",
            "eine Beschreibung des Nutzers statt Novas ('ich bin eher ruhig')",
        ]

    @property
    def grenze(self) -> list[str]:
        """Was dieser Dienst nicht tut."""
        return [
            "keine absoluten Verbote — die gehoeren zu den Direktiven",
            "keine Sprachwahl oder Anredeform",
            "keine Charakteraenderung fuer einen einzelnen Turn",
        ]

    @property
    def quote(self) -> dict[str, int]:
        """Geschaetzter Anteil: eine Ausnahme, unter einem Achtel."""
        return {"user": 0}


    @property
    def ausgaenge(self) -> frozenset[str]:
        """Bedient alle vier Ausgaenge, einschliesslich der Ablehnung.

        Der vierte Ausgang traegt einen Korrekturvorschlag: Erkennt die
        Klassifikation Rueckmeldungen und einmalige Rollenspiele,
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
        graph.add_node("resume",          resume)
        graph.add_node("klassifizieren",  klassifizieren)
        graph.add_node("db_validieren",   self._db_validieren)
        graph.add_node("ausfuehren",      ausfuehren)

        graph.set_entry_point("validieren")
        graph.add_conditional_edges("validieren",      self._nach_validierung)
        graph.add_conditional_edges("resume",          self._nach_resume)
        graph.add_conditional_edges("klassifizieren",  self._nach_klassifikation)
        graph.add_conditional_edges("db_validieren",   self._nach_db_validierung)
        graph.add_edge("ausfuehren", END)

        return graph.compile()

    # --- Routing ---

    def _nach_validierung(self, state: AgentState) -> str:
        action = state["parameter"].get("action", "")
        if state["status"] == "fehler":
            return END
        if state["parameter"].get("resume"):
            return "resume"
        if action in ("create", "read", "update", "delete", "delete_alle", "reactivate", "replace", "konsolidieren"):
            return "db_validieren"
        return "klassifizieren"

    def _nach_resume(self, state: AgentState) -> str:
        status = state["status"]
        if status in ("fehler", "rueckfrage", "abgeschlossen", "dismissed"):
            return END
        return "ausfuehren"

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

    # --- Input-Validierung ---

    def _validieren(self, state: AgentState) -> dict:
        """Prueft ob die Aufgabe gueltig ist."""
        action = state["parameter"].get("action", "")
        logger.debug(f"_validieren: Einstieg — action='{action}'")

        if not action:
            return {
                "status": "fehler",
                "fehler": "Keine Aktion angegeben",
                "schritte": state["schritte"] + [{"node": "validieren", "ergebnis": "keine_aktion"}],
            }

        gueltige_aktionen = {"create", "read", "update", "delete", "delete_alle", "reactivate", "replace", "konsolidieren", "agent"}
        if action not in gueltige_aktionen:
            return {
                "status": "fehler",
                "fehler": f"Unbekannte Aktion: {action}",
                "schritte": state["schritte"] + [{"node": "validieren", "ergebnis": "ungueltige_aktion"}],
            }

        return {
            "status": "laufend",
            "schritte": state["schritte"] + [{"node": "validieren", "ergebnis": "ok", "action": action}],
        }

    # --- DB-Validierung (HITL-Gate) ---

    def _db_validieren(self, state: AgentState) -> dict:
        """Prueft die Aktion gegen den DB-Zustand. Setzt Rueckfrage bei Bedarf."""
        action = state["parameter"].get("action", "")

        if action == "read":
            return {
                "schritte": state["schritte"] + [{"node": "db_validieren", "ergebnis": "skip_read"}],
            }

        result = validieren_gegen_db(state)

        logger.info(
            f"db_validieren: action='{action}', ok={result.ok}, "
            f"korrektur={result.korrektur}, bestaetigung={result.bestaetigung_noetig}, "
            f"grund='{result.grund[:60]}'"
        )

        state_update = {}
        if result.korrektur:
            state_update = {
                "parameter": {
                    **state["parameter"],
                    "action": result.korrektur,
                },
            }

        if not result.ok and not result.bestaetigung_noetig:
            return {
                **state_update,
                "status": "fehler",
                "fehler": result.grund,
                "schritte": state["schritte"] + [{"node": "db_validieren", "ergebnis": f"fehler: {result.grund[:40]}"}],
            }

        if result.bestaetigung_noetig:
            return {
                **state_update,
                "status": "rueckfrage",
                "rueckfrage": result.bestaetigung_text,
                "schritte": state["schritte"] + [{"node": "db_validieren", "ergebnis": "rueckfrage"}],
            }

        return {
            **state_update,
            "schritte": state["schritte"] + [{"node": "db_validieren", "ergebnis": "ok"}],
        }
