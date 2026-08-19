"""Dispatch für den Bibliotheks-Dienst — ConversationState <-> AgentState.

Spezifikation: docs/novaberg-convention-nmcp.md §5.4, §6.7 ·
docs/novaberg-autonomous-wissen_k.md §7.3.

**Kein Tor, kein Rückweg.** Dieser Dienst ändert nichts, also gibt es nichts
zu bestätigen; ein offener Auftrag in Redis hätte keinen Gegenstand. Was er
nicht beantworten kann, geht durch den vierten Ausgang und trägt einen
Vorschlag.

**Der Suchschlüssel wandert als angemeldeter Bedarf mit.** `such_vektor` ist
der Vektor, mit dem in diesem Turn auch die Gedächtnisschichten und die
Bibliothek als Quelle gesucht haben — dieselbe Suche, zweiter Eingang
(§6a.1).
"""

import logging

from graph.reiz import reiz_text

from agents import AgentRegistry
from agents.base import AgentResult, AgentState, Korrektur

logger = logging.getLogger("ki_server.agents.wissen.dispatch")

DIENST: str = "wissen"


def dispatch_wissen(state: dict) -> dict:
    """ConversationState -> WissenAgent -> ConversationState.

    Vorbedingung: `state` trägt `user_id`; `such_vektor` trägt den
    Suchschlüssel des Turns.
    Nachbedingung: `agent_results` trägt genau ein AgentResult mehr, und
    `agent_name` ist zurückgesetzt, damit der Planner neu entscheidet.
    Fehlerfaelle: fehlende `user_id`, unbekannter Dienst — beide mit
    gesetztem `management_result`.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id: str = state.get("user_id", "")
    if not user_id:
        logger.error(
            "dispatch_wissen: Auftrag ohne user_id — ohne Paar gibt es keine "
            "Bibliothek, in der gesucht werden duerfte"
        )
        return _mit_ergebnis(state, AgentResult(
            agent_name=DIENST, ergebnis=None, status="fehler",
            fehler="Auftrag ohne user_id",
        ))

    such_vektor: list = state.get("such_vektor") or []
    if not such_vektor:
        # Gemeldet, nicht verschluckt: Anders als beim lesenden Dienst gibt es
        # hier keinen scharfen Kanal, der einspringt — die Bibliothek trägt
        # allein `themen_embedding`. Ohne Schlüssel scheitert der Dienst, und
        # das soll im Protokoll stehen, bevor er es tut.
        logger.warning(
            "dispatch_wissen: kein such_vektor im Turn — die Bibliothek hat "
            "nur den Bedeutungskanal, der Dienst wird als Stoerung enden"
        )

    logger.debug(
        "dispatch_wissen: Einstieg — action='%s', target='%s'",
        state.get("management_action"), state.get("management_target"),
    )

    # ── Verarbeitung ────────────────────────────
    agent_state: AgentState = {
        "aufgabe": reiz_text(state),
        "aufgabe_typ": "workflow",
        "agent_name": DIENST,
        "kontext": {
            "user_id": user_id,
            "character_id": state.get("character_id", "") or "nova",
            "such_vektor": such_vektor,
        },
        "parameter": {
            "action": state.get("management_action", ""),
            "target": state.get("management_target", ""),
        },
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }

    agent = AgentRegistry.finden(DIENST)
    if not agent:
        logger.error("dispatch_wissen: '%s' nicht in der Registry", DIENST)
        return _mit_ergebnis(state, AgentResult(
            agent_name=DIENST, ergebnis=None, status="fehler",
            fehler=f"{DIENST} nicht registriert",
        ))

    ergebnis_state = agent.invoke(agent_state)
    status: str = ergebnis_state.get("status", "fehler")
    logger.debug("dispatch_wissen: Agent-Ergebnis — status='%s'", status)

    # ── Der vierte Ausgang ──────────────────────
    #
    # Ein Urteil des Dienstes trägt seine drei Teile im Zustand mit; ohne sie
    # wäre `abgelehnt` formal unzulässig — und genau das ist der Riegel, der
    # eine Sackgasse verhindert (`agents/base.py`).
    korrektur: Korrektur | None = ergebnis_state.get("parameter", {}).get("korrektur")
    fehlertext: str | None = ergebnis_state.get("fehler")
    if status == "abgelehnt" and korrektur is None:
        logger.error(
            "dispatch_wissen: Ablehnung ohne Korrektur — als Stoerung "
            "gemeldet, weil eine Ablehnung ohne Vorschlag eine Sackgasse ist"
        )
        status = "fehler"
        # Der Ausgang trägt seinen Pflichtteil selbst: `AgentResult` verlangt
        # bei "fehler" eine Begründung und wirft sonst.
        fehlertext = fehlertext or "Ablehnung ohne Korrektur — Vorschlag fehlt"

    # ── Ausgabe-Verifikation ────────────────────
    return _mit_ergebnis(state, AgentResult(
        agent_name=DIENST,
        ergebnis=ergebnis_state.get("ergebnis"),
        status=status,
        fehler=fehlertext,
        rueckfrage=ergebnis_state.get("rueckfrage"),
        korrektur=korrektur if status == "abgelehnt" else None,
        schritte=ergebnis_state.get("schritte", []),
    ))


def _mit_ergebnis(state: dict, ergebnis: AgentResult) -> dict:
    """Hängt ein AgentResult an und setzt die Anzeigefelder.

    Vorbedingung: `ergebnis` ist vollständig.
    Nachbedingung: `agent_results` um eins länger, `agent_name` zurückgesetzt,
    `management_result` und `management_detail` gesetzt.

    **Jeder Rückkehrpfad setzt `management_result`** — wer nur bei Erfolg
    schreibt, macht „nicht gelaufen" von „so gelaufen" ununterscheidbar.
    """
    # ── Verarbeitung ────────────────────────────
    bisherige: list = state.get("agent_results", [])

    if ergebnis.status == "abgeschlossen" and ergebnis.ergebnis:
        anzeige: str = str(ergebnis.ergebnis)
        detail:  str = str(ergebnis.ergebnis)
    elif ergebnis.status == "abgelehnt" and ergebnis.korrektur:
        anzeige = ergebnis.korrektur.befund
        detail = f"{ergebnis.korrektur.beleg} — {ergebnis.korrektur.vorschlag}"
    elif ergebnis.status == "fehler" and ergebnis.fehler:
        anzeige = f"Fehler: {ergebnis.fehler}"
        detail = ergebnis.fehler
    else:
        anzeige = ""
        detail = f"Status '{ergebnis.status}' ohne Anzeigetext"
        logger.error(
            "dispatch_wissen: Status '%s' ohne Anzeigetext — der Turn zeigte "
            "sonst nichts an", ergebnis.status,
        )

    # ── Ausgabe-Verifikation ────────────────────
    return {
        "agent_results": bisherige + [ergebnis],
        "agent_name": "",
        "management_result": anzeige,
        "management_detail": detail,
    }
