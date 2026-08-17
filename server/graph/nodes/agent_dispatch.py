"""Agent-Dispatch — Zentraler Entry-Point für Agent-Aufrufe im Graph.

Liest agent_name aus dem State, findet den agenten-spezifischen Dispatch,
delegiert die ConversationState → AgentState → ConversationState Transformation.

Dieser Node ist generisch — er ist nur ein Router. Die eigentliche
Transformation passiert in der agenten-spezifischen dispatch.py.

**Und er ist die einzige Stelle, durch die jede Handlung eines Agenten läuft.**
Deshalb steht hier der Protokolleintrag, der den Initiator nennt: Ein Termin,
den Nova aus einem eigenen Gedanken angelegt hat, ist in der Fachtabelle von
einem erbetenen nicht zu unterscheiden — dort steht keine Herkunft, und sie
gehört auch nicht dorthin. Sie gehört ins Protokoll, wo der ganze Turn
nachvollziehbar ist.
"""

import logging

from agents import get_dispatch
from agents.base import AgentResult
from agents.nmcp_quote import REGISTER
from memory.pipeline_log import log_ausgabe

from graph.reiz import reiz_text
from graph.state import reiz_herkunft

logger = logging.getLogger("ki_server.agent_dispatch")


def _handlung_protokollieren(
    state:      dict,
    agent_name: str,
    rueckgabe:  dict,
) -> None:
    """Schreibt einen Protokolleintrag über die Handlung und ihren Initiator.

    **Warum `ausgabe` und nicht `db_write`.** Dieser Knoten steht eine Schicht
    über der Datenbank: Er sieht, dass ein Agent gelaufen ist und mit welchem
    Ausgang, nicht welche Zeilen dabei entstanden. Ein `db_write` an dieser
    Stelle behauptete mehr, als hier bekannt ist — eine Rückfrage und ein
    Fehlschlag schreiben nichts. Der Ausgang steht deshalb als Feld daneben,
    und *„was hat sie selbst angelegt"* ist die Frage nach `initiator` **und**
    `status` zusammen.

    **Es wird in jedem Ausgang protokolliert, nicht nur beim Erfolg.** Nur den
    Erfolg zu schreiben machte „nicht gelaufen" von „gelaufen und nichts
    geschrieben" ununterscheidbar — und ein abgewiesener Versuch ist genau die
    Zeile, die man sucht, wenn etwas nicht passiert ist.

    Vorbedingung: `agent_name` ist gesetzt, `rueckgabe` ist das Ergebnis des
        agentenspezifischen Dispatch.
    Nachbedingung: genau ein Eintrag der Art `ausgabe` unter dem Knoten
        `agent_dispatch`, mit Initiator und Ausgang.
    Fehlerfälle: Ein gescheiterter Protokolleintrag darf den Turn nicht
        reißen — er wird gemeldet und verschluckt nicht.

    Args:
        state:      der Zustand des Durchlaufs.
        agent_name: der Agent, der gelaufen ist.
        rueckgabe:  was sein Dispatch zurückgegeben hat.
    """
    # ── Eingabe-Validierung ─────────────────────
    ergebnisse: list = rueckgabe.get("agent_results") or []
    letztes = ergebnisse[-1] if ergebnisse else None

    # ── Verarbeitung ────────────────────────────
    reiz: str = reiz_text(state)

    inhalt: dict = {
        "agent":     agent_name,
        # Wer diesen Turn ausgelöst hat — "nutzer_turn" oder "eigener_impuls".
        # Die einzige Angabe, an der später erkennbar ist, wessen Handlung ein
        # Eintrag in der Fachtabelle war.
        "initiator": reiz_herkunft(state),
        "status":    getattr(letztes, "status", "unbekannt") if letztes else "ohne_ergebnis",
        # Der Auftrag im Wortlaut, gekappt: Ohne ihn ist im Nachhinein nicht
        # zu sehen, worauf der Agent reagiert hat — und genau das ist die
        # Frage bei einem Eintrag, den niemand erwartet hat.
        "aufgabe":   reiz[:300],
        "aufgabe_zeichen": len(reiz),
        "ergebnis":  str(rueckgabe.get("management_result", ""))[:300],
    }

    # ── Ausgabe-Verifikation ────────────────────
    try:
        log_ausgabe(
            turn_id      = state.get("turn_id", "unbekannt"),
            node         = "agent_dispatch",
            quelle       = agent_name,
            inhalt       = inhalt,
            user_id      = state.get("user_id", ""),
            character_id = state.get("character_id", ""),
        )
    except Exception:
        # Breit gefangen mit Absicht: Der Turn ist wichtiger als sein Protokoll,
        # und was den Schreibvorgang reissen kann, ist von hier aus nicht
        # aufzaehlbar. Gemeldet wird mit Spur, damit die Luecke auffindbar ist.
        logger.exception(
            "Agent-Dispatch: Handlung nicht protokolliert — der Agent '%s' ist "
            "gelaufen, sein Initiator '%s' ist damit nicht nachvollziehbar",
            agent_name, inhalt["initiator"],
        )
        return

    logger.info(
        "Agent-Dispatch: '%s' gelaufen — initiator=%s, status=%s",
        agent_name, inhalt["initiator"], inhalt["status"],
    )


def agent_dispatch_node(state: dict) -> dict:
    """Zentraler Dispatch-Node im Graph. Delegiert an den agenten-spezifischen Dispatch."""
    agent_name = state.get("agent_name", "")
    if not agent_name:
        # Kein Agent angefordert — nichts zu tun
        return {}

    dispatch_fn = get_dispatch(agent_name)
    if not dispatch_fn:
        # Agent existiert, aber kein Dispatch gefunden
        logger.error(f"Kein Dispatch für Agent '{agent_name}' gefunden")
        result = AgentResult(
            agent_name=agent_name,
            ergebnis=None,
            status="fehler",
            fehler=f"Kein Dispatch für Agent '{agent_name}' registriert",
        )
        bisherige = state.get("agent_results", [])
        rueckgabe: dict = {
            "agent_results": bisherige + [result],
            "agent_name": "",  # Reset — Planner soll neu entscheiden
        }
        _handlung_protokollieren(state, agent_name, rueckgabe)
        return rueckgabe

    # Der Quotenzaehler sitzt hier, weil nur der Empfang weiss, WAS er
    # zugestellt hat. Gezaehlt wird die Zustellung und nicht der Erfolg:
    # Die Differenz zu `bearbeitet` ist ein Zustellverlust und hat mit dem
    # Aushang nichts zu tun — wer nur den Erfolg zaehlt, liest einen
    # Pipeline-Defekt als Routing-Problem.
    _graph = "pixie" if state.get("graph_rolle") == "pixie" else "user"
    REGISTER.zustellung_zaehlen(agent_name, _graph)

    logger.info(f"Agent-Dispatch: {agent_name}")
    try:
        rueckgabe = dispatch_fn(state)
    except Exception as e:
        logger.exception(f"{type(e).__name__}: Agent-Dispatch Fehler für '{agent_name}'")
        result = AgentResult(
            agent_name=agent_name,
            ergebnis=None,
            status="fehler",
            fehler=str(e),
        )
        bisherige = state.get("agent_results", [])
        rueckgabe = {
            "agent_results": bisherige + [result],
            "agent_name": "",
        }

    # Bearbeitung samt Ausgang zaehlen. Die Ablehnungsquote ist das zweite
    # Signal des Abgleichs: Trifft die Zustellquote und wird trotzdem viel
    # abgelehnt, ist der Aushang richtig und die Grenzangabe fehlt.
    for _r in rueckgabe.get("agent_results", [])[len(state.get("agent_results", [])):]:
        REGISTER.bearbeitung_zaehlen(
            agent_name, _graph, getattr(_r, "status", "")
        )

    _handlung_protokollieren(state, agent_name, rueckgabe)
    return rueckgabe
