"""FactsAgent — schreibt einen Fakt, um den der Mensch bittet.

Graph: validieren → klassifizieren → suchen → ausfuehren → bestaetigen.

  klassifikation.py — Subjekt, Beziehung des Kanons und Objekt per Modell,
                      geprüft gegen den Wortlaut der Bitte
  suche.py          — Auflösung nur über den Namen; Rückfrage bei Mehrdeutigkeit
  crud.py           — Schreiben in einer Transaktion, danach Verifikation
  bestaetigung.py   — Abschluss ohne erfundenen Erfolg

**Kein Wartezustand und kein Resume.** Eine Rückfrage endet den Lauf; die
Antwort des Menschen kommt als neue Bitte an und trägt die Unterscheidung
selbst. **Kein Objekt-Merkmal:** Der Dienst bedient kein Objekt der Lage,
sondern eine Bitte, sich etwas zu merken.
"""

import logging

from langgraph.graph import END, StateGraph

from agents.base import AgentState, BaseAgent
from agents.fakten.bestaetigung import confirm
from agents.fakten.crud import execute
from agents.fakten.klassifikation import classify
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
        """Nur im Gespräch: Ein Fakt entsteht auf Bitte des Menschen.

        Bleibt `["user"]`, auch ohne Platz am Empfang: Der Dispatcher bedient
        den Dienst im Nutzergraphen.
        """
        return ["user"]

    @property
    def negativfaelle(self) -> list[str]:
        """Äußerungen, die nach einem Fakt klingen und keiner sind."""
        return [
            "eine Anweisung an die Figur, wie sie sich verhalten oder sprechen soll "
            "('sei ab jetzt frecher') — das ist kein Fakt über den Menschen",
            "ein Satz im Rollenspiel oder in einer erfundenen Geschichte "
            "('mein Drache wohnt in der Höhle') — erfunden ist nicht der Fall",
            "eine Metapher oder Übertreibung ('mein Kopf ist ein Sieb') — "
            "gemeint ist nicht, was dasteht",
            "etwas, das auf eine Liste soll oder besorgt werden muss "
            "('merk dir, dass wir Mehl brauchen') — das ist keine Beziehung",
            "ein Vorhaben mit Zeitpunkt ('merk dir, dass ich Freitag zum Arzt gehe') "
            "— ein Fakt trägt keine Zeit",
        ]

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
        """Bedient alle vier Ausgänge, einschließlich der Ablehnung.

        Ohne Beziehung im Kanon lehnt die Klassifikation ab.
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
        graph.add_node("validieren",     self._validate)
        graph.add_node("klassifizieren", classify)
        graph.add_node("suchen",         search)
        graph.add_node("ausfuehren",     execute)
        graph.add_node("bestaetigen",    confirm)

        graph.set_entry_point("validieren")
        graph.add_conditional_edges("validieren",     self._after_validation)
        graph.add_conditional_edges("klassifizieren", self._after_classification)
        graph.add_conditional_edges("suchen",         self._after_search)
        graph.add_edge("ausfuehren",  "bestaetigen")
        graph.add_edge("bestaetigen", END)
        return graph.compile()

    # --- Routing ---

    def _after_validation(self, state: AgentState) -> str:
        """Nach der Validierung: bei `fehler` zum Ende, sonst zur Klassifikation."""
        # ── Verarbeitung ────────────────────────────
        return END if state["status"] == "fehler" else "klassifizieren"

    def _after_classification(self, state: AgentState) -> str:
        """Nach der Klassifikation: `rejected` und `fehler` enden, sonst die Suche."""
        # ── Verarbeitung ────────────────────────────
        return END if state["status"] in ("fehler", "rejected") else "suchen"

    def _after_search(self, state: AgentState) -> str:
        """Nach der Suche: `rueckfrage` und `fehler` enden, ohne zu schreiben."""
        # ── Verarbeitung ────────────────────────────
        return END if state["status"] in ("fehler", "rueckfrage") else "ausfuehren"

    # --- Validierung ---

    def _validate(self, state: AgentState) -> dict:
        """Prüft, ob Aufgabe und Paar für einen Fakt vorliegen.

        Vorbedingung: `state` ist ein AgentState.
        Nachbedingung: `status = "laufend"`, wenn die Aufgabe nicht leer ist
            und der Kontext `user_id` und `character_id` trägt.
        Fehlerfälle: Sonst `status = "fehler"` — ohne Paar wüsste die
            Schreibung nicht, wem der Fakt gehört.
        """
        # ── Eingabe-Validierung ─────────────────────
        aufgabe: str = state.get("aufgabe") or ""
        kontext: dict = state.get("kontext") or {}
        fehlend: list[str] = [
            schluessel for schluessel in ("user_id", "character_id") if not kontext.get(schluessel)
        ]
        if not aufgabe.strip():
            fehlend.insert(0, "aufgabe")

        # ── Verarbeitung ────────────────────────────
        if fehlend:
            logger.error("validieren: Auftrag ohne %s — verworfen", fehlend)
            return {
                "status": "fehler",
                "fehler": f"Auftrag an fakten ohne {', '.join(fehlend)}",
                "schritte": state["schritte"]
                + [{"node": "validieren", "ergebnis": f"fehlt/{','.join(fehlend)}"}],
            }
        return {
            "status": "laufend",
            "schritte": state["schritte"] + [{"node": "validieren", "ergebnis": "ok"}],
        }
