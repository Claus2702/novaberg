"""DateienWurzelnAgent — die Freigaben am Empfang.

Spezifikation: docs/novaberg-agent-dateien_k.md §2a und §8.2a.

Der erste Dienst dieses Projekts, dessen **Anmeldung vor dem Code stand**:
Aushang, Negativfaelle, Grenze, Kosten, Kadenz, Geltungsbereich, Datenhoheit,
Bedarf, Quote, Wiederholverhalten und Ausgaenge sind im Konzept festgelegt,
bevor die erste Zeile entstand (`novaberg-convention-nmcp.md` §3.4).

**Er schreibt in die Wurzeltabelle und nie in eine Datei.** Was er anlegt,
sind Zeilen ueber Verzeichnisse; er legt kein Verzeichnis an und loescht
keines. Der Schreibpfad ins Dateisystem liegt nicht in diesem Verbund —
nicht "wird nicht benutzt", sondern nicht importiert (§7 Regel 2).

Graph-Aufbau und Routing hier; die Fachlogik liegt in:
  klassifikation.py — welche der fuenf Aktionen gemeint ist
  aussenrand.py     — die Schranke, die kein Gespraech verschieben kann
  crud.py           — die fuenf Aktionen samt Tor und Verifikation
"""

import logging

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents.base import AgentState, BaseAgent
from agents.dateien_wurzeln.crud import AKTIONEN_KANON, ausfuehren, validieren_gegen_db
from agents.dateien_wurzeln.klassifikation import klassifizieren
from agents.dateien_wurzeln.resume import resume

logger = logging.getLogger("ki_server.agents.dateien_wurzeln")

#: Aktionen, die der Dispatch ohne Klassifikation setzen darf, plus die
#: Sammelform "agent" fuer den Weg ueber den Empfang. Geschlossene Menge —
#: ein unbekannter Wert ist ein Defekt und kein stiller Durchlauf.
EINGANGS_KANON: frozenset[str] = AKTIONEN_KANON | {"agent"}


class DateienWurzelnAgent(BaseAgent):
    """Legt Verzeichnis-Freigaben an, nimmt sie zurueck und listet sie auf."""

    @property
    def name(self) -> str:
        """Eindeutiger Name, identisch mit dem Verzeichnisnamen."""
        return "dateien_wurzeln"

    @property
    def faehigkeiten(self) -> list[str]:
        """Auskunft fuer Menschen und Anzeige — nie Auswahlkriterium.

        Die Auswahl laeuft ueber den Aushang (`novaberg-convention-nmcp.md`
        §3.4); eine Liste von Verben sagt dem Empfang nicht, welche
        Aeusserung dazu passt.
        """
        return [
            "verzeichnis_freigeben",
            "freigaben_lesen",
            "freigabe_umbenennen",
            "freigabe_zuruecknehmen",
            "freigabe_wieder_aufnehmen",
        ]

    @property
    def graph_eignung(self) -> list[str]:
        """Nur der Nutzergraph — eine Freigabe spricht ein Mensch aus.

        Der Hintergrund ist ausdruecklich ausgenommen und das ist eine
        Entscheidung, keine Auslassung: Ein eigener Impuls, der sich selbst
        ein Verzeichnis freigeben koennte, haette den Menschen aus der
        einzigen Entscheidung genommen, die ihm hier gehoert.
        """
        return ["user"]

    @property
    def negativfaelle(self) -> list[str]:
        """Aeusserungen, die oberflaechlich passen und nicht hierher gehoeren.

        Eigenschaften der Aeusserung, nie ein anderer Dienst — ein
        Ausschlussrecht verwandelte eine Fehlzustellung in eine ausgebliebene
        (`novaberg-convention-nmcp.md` §3.6b).
        """
        return [
            "eine Frage nach dem Inhalt einer Datei "
            "('was steht in der Roadmap') — das ist ein Inhalt, kein Verzeichnis",
            "die Erwaehnung eines Ordners ohne Freigabeabsicht "
            "('das liegt bei mir unter Projekte')",
            "die Bitte, etwas abzulegen — dieser Dienst schreibt keine Datei",
        ]

    @property
    def grenze(self) -> list[str]:
        """Was dieser Dienst ausdruecklich nicht tut."""
        return [
            "legt keine Verzeichnisse an und loescht keine",
            "schreibt keine Datei, in keiner Zone",
            "gibt nichts ausserhalb des konfigurierten Aussenrands frei — "
            "auch nicht auf Bestaetigung",
            "aendert nie den Pfad einer bestehenden Freigabe, nur ihre Bezeichnung",
        ]

    @property
    def quote(self) -> dict[str, int]:
        """Geschaetzter Anteil der Aeusserungen: eine Ausnahme.

        Eine Freigabe ist ein seltener Vorgang. Die Angabe ist eine
        Schaetzung und soll widerlegt werden — genau dafuer steht sie da
        (`novaberg-convention-nmcp.md` §8.2a).
        """
        return {"user": 0}

    @property
    def ausgaenge(self) -> frozenset[str]:
        """Alle vier — und der vierte traegt hier den wichtigsten Fall.

        *"liegt ausserhalb des zulaessigen Bereichs"* mit dem aufgeloesten
        Pfad als Beleg und dem geltenden Rand als Vorschlag. Ein blankes
        Nein liesse den Menschen im Unklaren, ob sein Pfad falsch war oder
        seine Bitte.
        """
        return frozenset({"abgeschlossen", "fehler", "rueckfrage", "abgelehnt"})

    def build_graph(self) -> CompiledStateGraph:
        """Baut den Subgraphen: validieren → klassifizieren → Tor → ausfuehren.

        Die Antwort auf die Torfrage laeuft ueber `resume` und **nie**
        unmittelbar in die Ausfuehrung: Der Rueckweg der Rueckfrage ist die
        Bedingung dafuer, dass das Tor eines ist (`resume.py`).
        """
        graph = StateGraph(AgentState)

        graph.add_node("validieren",     self._validieren)
        graph.add_node("resume",         resume)
        graph.add_node("klassifizieren", klassifizieren)
        graph.add_node("db_validieren",  self._db_validieren)
        graph.add_node("ausfuehren",     ausfuehren)

        graph.set_entry_point("validieren")
        graph.add_conditional_edges("validieren",     self._nach_validierung)
        graph.add_conditional_edges("resume",         self._nach_resume)
        graph.add_conditional_edges("klassifizieren", self._nach_klassifikation)
        graph.add_conditional_edges("db_validieren",  self._nach_db_validierung)
        graph.add_edge("ausfuehren", END)

        return graph.compile()

    # --- Routing ---

    def _nach_validierung(self, state: AgentState) -> str:
        """Nach der Eingangspruefung: Ende, Rueckweg oder Klassifikation."""
        if state["status"] == "fehler":
            return END
        if state["parameter"].get("resume"):
            return "resume"
        if state["parameter"].get("action", "") in AKTIONEN_KANON:
            return "db_validieren"
        return "klassifizieren"

    def _nach_resume(self, state: AgentState) -> str:
        """Nach dem Rueckweg: nur eine gedeutete Zustimmung fuehrt weiter."""
        if state["status"] in ("fehler", "rueckfrage", "dismissed", "abgeschlossen"):
            return END
        return "ausfuehren"

    def _nach_klassifikation(self, state: AgentState) -> str:
        """Nach der Klassifikation: Ende bei Fehler oder Ablehnung, sonst Tor."""
        if state["status"] in ("fehler", "rejected"):
            return END
        return "db_validieren"

    def _nach_db_validierung(self, state: AgentState) -> str:
        """Nach dem Tor: Ende bei Fehler, Ablehnung oder Rueckfrage."""
        if state["status"] in ("fehler", "rueckfrage", "abgelehnt"):
            return END
        return "ausfuehren"

    # --- Eingabe-Validierung ---

    def _validieren(self, state: AgentState) -> dict:
        """Prueft den Eingangsauftrag gegen den Kanon.

        Vorbedingung: `state["parameter"]` traegt `action`.
        Nachbedingung: Bei `status="laufend"` liegt `action` in
        EINGANGS_KANON. Ein unbekannter Wert wird gemeldet und nicht auf
        eine Vorgabe abgebildet — sonst waere eine defekte Zustellung von
        einer gueltigen nicht zu unterscheiden (`11_EVA` §2).
        """
        # ── Eingabe-Validierung ─────────────────
        action: str = state["parameter"].get("action", "")
        logger.debug("dateien_wurzeln._validieren: Einstieg — action='%s'", action)

        if not action:
            logger.error("dateien_wurzeln: Auftrag ohne Aktion — abgewiesen")
            return {
                "status": "fehler",
                "fehler": "Keine Aktion angegeben",
                "schritte": state["schritte"] + [
                    {"node": "validieren", "ergebnis": "keine_aktion"}
                ],
            }

        if action not in EINGANGS_KANON:
            logger.error(
                "dateien_wurzeln: Aktion %r nicht im Kanon %s — abgewiesen",
                action, sorted(EINGANGS_KANON),
            )
            return {
                "status": "fehler",
                "fehler": f"Unbekannte Aktion: {action}",
                "schritte": state["schritte"] + [
                    {"node": "validieren", "ergebnis": "ungueltige_aktion"}
                ],
            }

        # ── Ausgabe-Verifikation ────────────────
        return {
            "status": "laufend",
            "schritte": state["schritte"] + [
                {"node": "validieren", "ergebnis": "ok", "action": action}
            ],
        }

    # --- Das Tor ---

    def _db_validieren(self, state: AgentState) -> dict:
        """Haelt die Aktion gegen Aussenrand und Bestand und stellt das Tor.

        Vorbedingung: `action` liegt in AKTIONEN_KANON.
        Nachbedingung: Entweder `status="rueckfrage"` mit Text, oder
        `status="abgelehnt"` mit den drei Teilen der Korrektur, oder
        `status="fehler"` bei einer Stoerung, oder ein Durchlauf zur
        Ausfuehrung.
        Eine Auto-Korrektur (create → reactivate) wird in `parameter`
        geschrieben, bevor das Tor sie nennt — sonst bestaetigte der Mensch
        etwas anderes, als danach geschieht.
        """
        action: str = state["parameter"].get("action", "")

        if action == "read":
            return {
                "schritte": state["schritte"] + [
                    {"node": "db_validieren", "ergebnis": "skip_read"}
                ],
            }

        ergebnis, korrektur = validieren_gegen_db(state)
        logger.info(
            "dateien_wurzeln._db_validieren: action='%s', ok=%s, korrektur=%s, "
            "bestaetigung=%s, grund='%s'",
            action, ergebnis.ok, ergebnis.korrektur,
            ergebnis.bestaetigung_noetig, ergebnis.grund[:80],
        )

        zustand: dict = {}
        if ergebnis.korrektur:
            zustand = {
                "parameter": {**state["parameter"], "action": ergebnis.korrektur},
            }

        if not ergebnis.ok and not ergebnis.bestaetigung_noetig:
            # Der vierte Ausgang: Eine Bitte, die dieser Dienst nicht
            # erfuellen darf, ist ein **Urteil** und geht den Auftraggeber
            # an. Nur ein Betriebszustand — kein konfigurierter Rand, ein
            # Wert ausserhalb des Kanons — ist eine Stoerung.
            traeger: dict = {**state["parameter"], "korrektur": korrektur}
            if ergebnis.korrektur:
                traeger["action"] = ergebnis.korrektur
            return {
                "parameter": traeger,
                "status": "abgelehnt" if korrektur else "fehler",
                "fehler": ergebnis.grund,
                "schritte": state["schritte"] + [
                    {"node": "db_validieren",
                     "ergebnis": f"{'abgelehnt' if korrektur else 'fehler'}: {ergebnis.grund[:40]}"}
                ],
            }

        if ergebnis.bestaetigung_noetig:
            return {
                **zustand,
                "status": "rueckfrage",
                "rueckfrage": ergebnis.bestaetigung_text,
                "schritte": state["schritte"] + [
                    {"node": "db_validieren", "ergebnis": "rueckfrage"}
                ],
            }

        return {
            **zustand,
            "schritte": state["schritte"] + [
                {"node": "db_validieren", "ergebnis": "ok"}
            ],
        }
