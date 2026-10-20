"""Dispatch für den FactsAgent — ConversationState ↔ AgentState.

Ohne Wartezustand: Eine Rückfrage wird zurückgegeben und nirgends abgelegt;
die Antwort des Menschen erreicht den Dienst als neue Bitte.
"""

import logging

from agents import AgentRegistry
from agents.base import AgentResult, AgentState, Korrektur
from graph.reiz import reiz_text

logger = logging.getLogger("ki_server.agents.fakten.dispatch")

AGENT_NAME: str = "fakten"

# Das Gegenangebot einer Ablehnung: ein Auftrag, den dieser Dienst ausführen würde.
VORSCHLAG: str = (
    "Sage, was ich mir über wen merken soll, etwa 'merk dir, dass Ilva in Ostheim wohnt'."
)


def dispatch_fakten(state: dict) -> dict:
    """ConversationState → FactsAgent → ConversationState.

    Vorbedingung: `state` ist der ConversationState mit `user_id` und
        `character_id`.
    Nachbedingung: `agent_results` trägt genau ein AgentResult mehr; ein
        `rejected` der Klassifikation ist `abgelehnt` mit Korrektur und
        `agent_name: None`, damit der Planner den nächsten Dienst fragt.
    Fehlerfälle: Ein nicht registrierter Agent ergibt `fehler`; ein Status,
        den AgentResult nicht kennt, wirft dort ValueError.
    """
    # ── Eingabe-Validierung ─────────────────────
    bisherige: list = list(state.get("agent_results", []))
    agent = AgentRegistry.finden(AGENT_NAME)
    if not agent:
        logger.error("FactsAgent nicht in der Registry gefunden")
        result = AgentResult(agent_name=AGENT_NAME, ergebnis=None, status="fehler",
                             fehler="FactsAgent nicht registriert")
        return {"agent_results": bisherige + [result], "agent_name": ""}

    # ── Verarbeitung ────────────────────────────
    agent_state: AgentState = {
        "aufgabe": reiz_text(state),
        "aufgabe_typ": "workflow",
        "agent_name": AGENT_NAME,
        "kontext": {
            "user_id": state.get("user_id", ""),
            "character_id": state.get("character_id", ""),
        },
        "parameter": {},
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }
    result_state: dict = agent.invoke(agent_state)
    logger.debug("dispatch_fakten: status=%r, schritte=%d", result_state.get("status"),
                 len(result_state.get("schritte", [])))

    if result_state.get("status") == "rejected":
        grund: str = result_state.get("schritte", [{}])[-1].get("ergebnis", "unbekannt")
        logger.info("Agent 'fakten': Klassifikation rejected — %s", grund)
        result = AgentResult(
            agent_name=AGENT_NAME,
            ergebnis=None,
            status="abgelehnt",
            korrektur=Korrektur(
                befund="Das habe ich nicht als Bitte verstanden, mir etwas zu merken.",
                kein_auftrag=True,
                beleg=f"Klassifikation: {grund}",
                vorschlag=VORSCHLAG,
            ),
            schritte=result_state.get("schritte", []),
        )
        return {"agent_results": bisherige + [result], "agent_name": None}

    result = AgentResult(
        agent_name=AGENT_NAME,
        ergebnis=result_state.get("ergebnis"),
        status=result_state.get("status", "fehler"),
        fehler=result_state.get("fehler"),
        rueckfrage=result_state.get("rueckfrage"),
        schritte=result_state.get("schritte", []),
    )

    # ── Ausgabe-Verifikation ────────────────────
    if result.status == "abgelehnt":
        raise RuntimeError("dispatch_fakten: abgelehnt nur aus der Klassifikation")
    return _build_return(bisherige, result)


def _build_return(bisherige: list, result: AgentResult) -> dict:
    """Baut die Rückgabe für den ConversationState aus einem AgentResult.

    Vorbedingung: `result` ist kein `abgelehnt` — das gibt der Dispatch selbst zurück.
    Nachbedingung: `agent_results` um `result` verlängert, `management_result`
        und `management_detail` nach dem Status gefüllt, `agent_name` leer.
    Fehlerfälle: ValueError bei `abgelehnt`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if result.status == "abgelehnt":
        raise ValueError("_build_return: abgelehnt ohne Korrektur-Pfad")

    # ── Verarbeitung ────────────────────────────
    management_result: str = ""
    management_detail: str = ""
    if result.status == "abgeschlossen" and result.ergebnis:
        management_result = str(result.ergebnis)
        management_detail = str(result.ergebnis)
    elif result.status == "rueckfrage" and result.rueckfrage:
        management_result = result.rueckfrage
        management_detail = "Rückfrage: Unterscheidung erforderlich"
    elif result.status == "fehler" and result.fehler:
        management_result = f"Fehler: {result.fehler}"
        management_detail = result.fehler
    return {
        "agent_results": bisherige + [result],
        "agent_name": "",  # Planner darf neu entscheiden
        "management_result": management_result,
        "management_detail": management_detail,
    }
