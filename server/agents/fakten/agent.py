"""FactsAgent — schreibt ein geprüftes Tripel als Fakt.

Der Dienst ist passiv: Die Klassifikation läuft je Turn mit Kandidaten in
`dispatch.py` (ein Modellaufruf, `klassifikation.py`), und jedes Tripel, das
die Prüfung besteht, läuft einzeln durch diesen Graphen:

  validieren → suchen → ausfuehren → bestaetigen

  suche.py          — Subjekt aus der Bindung des Objekts oder über den Namen;
                      `mehrdeutig` bei zwei Treffern, ohne Text
  crud.py           — Schreiben in einer Transaktion, danach Verifikation
  bestaetigung.py   — Abschluss ohne erfundenen Erfolg

**Kein Wartezustand und kein Resume.** **Kein Objekt-Merkmal:** Der Dienst
bedient kein Objekt der Lage, sondern die Kandidaten eines Turns.
"""

import logging

from langgraph.graph import END, StateGraph

from agents.base import AgentState, BaseAgent
from agents.fakten.bestaetigung import confirm
from agents.fakten.crud import execute
from agents.fakten.klassifikation import NEGATIVE_CASES
from agents.fakten.suche import search

logger = logging.getLogger("ki_server.agents.fakten")


class FactsAgent(BaseAgent):
    """Die Fachabteilung für Fakten über Personen, Orte und Sachen des Menschen."""

    @property
    def name(self) -> str:
        """Der Name des Dienstes, gleich dem Verzeichnis."""
        return "fakten"

    @property
    def faehigkeiten(self) -> list[str]:
        """Was der Dienst kann, für den Planner."""
        return ["fakt_merken"]

    @property
    def graph_eignung(self) -> list[str]:
        """Nur im Gespräch: Ein Fakt entsteht aus den Worten des Menschen.

        Bleibt `["user"]`, auch ohne Platz am Empfang: Der Dispatcher bedient
        den Dienst im Nutzergraphen.
        """
        return ["user"]

    @property
    def negativfaelle(self) -> list[str]:
        """Äußerungen, die nach einem Fakt klingen und keiner sind.

        Dieselbe Liste steht im Prompt der Klassifikation (`NEGATIVE_CASES`).
        """
        return list(NEGATIVE_CASES)

    @property
    def grenze(self) -> list[str]:
        """Was dieser Dienst nicht tut."""
        return [
            "nur Beziehungen aus seinem Kanon, keine Einordnung 'ist ein'",
            "kein Löschen eines Fakts auf Bitte",
            "keine Auskunft über gemerkte Fakten",
        ]

    @property
    def zustellart(self) -> str:
        """Läuft auf Auftrag des Dispatchers, ohne Zustellentscheidung.

        Der Auftrag kommt vom Dispatcher, nie vom Router oder Planner: Es
        gibt keine Entscheidung, ob der Dienst gewählt wird. Damit hat er
        auch keinen Aushang und keine Quote — ein Abgleich hätte nichts zu
        vergleichen.
        """
        return "queue"

    @property
    def ausgaenge(self) -> frozenset[str]:
        """Die vier Ausgänge des Handshakes (`nmcp._ausgaenge_pruefen`).

        Im passiven Weg setzt der Graph nur `abgeschlossen`, `fehler` und
        `mehrdeutig`; was die Klassifikation verwirft, ist ein Ausgang des
        Auftrags in `dispatch.py`, nicht dieses Graphen.
        """
        return frozenset({"abgeschlossen", "fehler", "rueckfrage", "abgelehnt"})

    def build_graph(self):  # noqa: ANN201 — CompiledStateGraph wie im Muster
        """Baut den Subgraphen des Agenten.

        Vorbedingung: keine.
        Nachbedingung: ein kompilierter Graph mit dem Einstieg `validieren`.
        Fehlerfälle: Fehler von LangGraph beim Kompilieren gehen nach oben.
        """
        # ── Verarbeitung ────────────────────────────
        graph = StateGraph(AgentState)
        graph.add_node("validieren",  self._validate)
        graph.add_node("suchen",      search)
        graph.add_node("ausfuehren",  execute)
        graph.add_node("bestaetigen", confirm)

        graph.set_entry_point("validieren")
        graph.add_conditional_edges("validieren", self._after_validation)
        graph.add_conditional_edges("suchen",     self._after_search)
        graph.add_edge("ausfuehren",  "bestaetigen")
        graph.add_edge("bestaetigen", END)
        return graph.compile()

    # --- Routing ---

    def _after_validation(self, state: AgentState) -> str:
        """Nach der Validierung: bei `fehler` zum Ende, sonst zur Suche."""
        # ── Verarbeitung ────────────────────────────
        return END if state["status"] == "fehler" else "suchen"

    def _after_search(self, state: AgentState) -> str:
        """Nach der Suche: `mehrdeutig` und `fehler` enden, ohne zu schreiben."""
        # ── Verarbeitung ────────────────────────────
        return END if state["status"] in ("fehler", "mehrdeutig") else "ausfuehren"

    # --- Validierung ---

    def _validate(self, state: AgentState) -> dict:
        """Prüft, ob ein geprüftes Tripel und das Paar für einen Fakt vorliegen.

        Vorbedingung: `state` ist ein AgentState; die Parameter kommen aus
            `klassifikation.vet_triple`, dazu `subjekt_entitaet_id`.
        Nachbedingung: `status = "laufend"`, wenn die Parameter `subjekt`,
            `beziehung`, `objekt` und `herkunft` nicht leer tragen,
            `subjekt_entitaet_id` gesetzt ist (auch als None) und der Kontext
            `user_id` und `character_id` trägt.
        Fehlerfälle: Sonst `status = "fehler"` — ohne Paar wüsste die
            Schreibung nicht, wem der Fakt gehört, ohne Herkunft nicht, woher.
        """
        # ── Eingabe-Validierung ─────────────────────
        parameter: dict = state.get("parameter") or {}
        kontext: dict = state.get("kontext") or {}
        fehlend: list[str] = [
            schluessel for schluessel in ("user_id", "character_id") if not kontext.get(schluessel)
        ]
        fehlend += [
            schluessel for schluessel in ("subjekt", "beziehung", "objekt", "herkunft")
            if not str(parameter.get(schluessel) or "").strip()
        ]
        if "subjekt_entitaet_id" not in parameter:
            fehlend.append("subjekt_entitaet_id")
        if fehlend:
            logger.error("validieren: Auftrag ohne %s — verworfen", fehlend)
            return {
                "status": "fehler",
                "fehler": f"Auftrag an fakten ohne {', '.join(fehlend)}",
                "schritte": state["schritte"]
                + [{"node": "validieren", "ergebnis": f"fehlt/{','.join(fehlend)}"}],
            }

        # ── Verarbeitung ────────────────────────────
        return {
            "status": "laufend",
            "schritte": state["schritte"] + [{"node": "validieren", "ergebnis": "ok"}],
        }
