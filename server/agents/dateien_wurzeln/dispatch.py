"""Dispatch fuer den Wurzeln-Dienst — ConversationState <-> AgentState.

Tor-Fluss:
  - Bei `status='rueckfrage'` wandert der offene Auftrag nach Redis (TTL 300s)
  - Bei `management_action='resume'` wird er geladen und der Agent mit der
    Antwort des Menschen fortgesetzt — ueber `resume.py`, nie unmittelbar in
    die Ausfuehrung
"""

import logging

from graph.reiz import reiz_text
from tools.redis_manager import redis_manager

from agents import AgentRegistry
from agents.base import AgentResult, AgentState, Korrektur
from agents.dateien_wurzeln.aussenrand import rand_text

logger = logging.getLogger("ki_server.agents.dateien_wurzeln.dispatch")

DIENST: str = "dateien_wurzeln"

#: Lebensdauer eines offenen Tor-Auftrags. Fuenf Minuten wie bei den
#: uebrigen Torwaechtern — ein Auftrag ohne Endzustand ist kein Auftrag.
PENDING_TTL_SECONDS: int = 300


def dispatch_dateien_wurzeln(state: dict) -> dict:
    """ConversationState -> DateienWurzelnAgent -> ConversationState.

    Vorbedingung: `state` traegt `user_id`; `management_action` benennt den
    Vorgang.
    Nachbedingung: `agent_results` traegt genau ein AgentResult mehr, und
    `agent_name` ist zurueckgesetzt, damit der Planner neu entscheidet.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id: str = state.get("user_id", "")
    if not user_id:
        logger.error(
            "dispatch_dateien_wurzeln: Auftrag ohne user_id — eine Freigabe "
            "ohne Paar hat keinen Eigentuemer und wird nicht angelegt"
        )
        return _mit_ergebnis(state, AgentResult(
            agent_name=DIENST, ergebnis=None, status="fehler",
            fehler="Auftrag ohne user_id",
        ))

    pending_key: str = f"pending_agent:{user_id}"
    logger.debug(
        "dispatch_dateien_wurzeln: Einstieg — action='%s', target='%s'",
        state.get("management_action"), state.get("management_target"),
    )

    # ── Verarbeitung ────────────────────────────
    if state.get("management_action") == "resume":
        offen: dict | None = redis_manager.get_json(pending_key)
        if offen and offen.get("agent_name") == DIENST:
            return _fortsetzen(state, offen, pending_key)
        logger.warning(
            "dispatch_dateien_wurzeln: Fortsetzung angefordert, aber kein "
            "offener Auftrag unter '%s'", pending_key,
        )

    agent_state: AgentState = _agent_state_bauen(
        state,
        aufgabe=reiz_text(state),
        parameter={
            "action": state.get("management_action", ""),
            "target": state.get("management_target", ""),
        },
    )

    return _laufen_lassen(state, agent_state, pending_key, fortsetzung=False)


def _fortsetzen(state: dict, offen: dict, pending_key: str) -> dict:
    """Setzt einen Auftrag fort, auf dessen Torfrage der Mensch geantwortet hat."""
    antwort: str = state.get("user_prompt", "")
    logger.info(
        "dispatch_dateien_wurzeln: Fortsetzung — action='%s', antwort='%s'",
        offen.get("action", ""), antwort[:80],
    )

    redis_manager.delete(pending_key)

    agent_state: AgentState = _agent_state_bauen(
        state,
        aufgabe=antwort,
        parameter={
            **offen.get("parameter", {}),
            "resume": True,
            "user_answer": antwort,
            "original_rueckfrage": offen.get("rueckfrage", ""),
        },
    )

    return _laufen_lassen(state, agent_state, pending_key, fortsetzung=True)


def _agent_state_bauen(state: dict, aufgabe: str, parameter: dict) -> AgentState:
    """Baut den AgentState aus dem ConversationState.

    Das Paar wandert vollstaendig mit: Eine Freigabe gehoert einem Menschen
    **und** einer Figur (§2.2), und ein fehlendes `character_id` machte aus
    zwei Freigaben eine.
    """
    return {
        "aufgabe": aufgabe,
        "aufgabe_typ": "workflow",
        "agent_name": DIENST,
        "kontext": {
            "user_id": state.get("user_id", ""),
            "character_id": state.get("character_id", "") or "nova",
        },
        "parameter": parameter,
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }


def _laufen_lassen(
    state: dict, agent_state: AgentState, pending_key: str, fortsetzung: bool,
) -> dict:
    """Fuehrt den Agenten aus und uebersetzt sein Ergebnis zurueck."""
    agent = AgentRegistry.finden(DIENST)
    if not agent:
        logger.error("dispatch_dateien_wurzeln: '%s' nicht in der Registry", DIENST)
        return _mit_ergebnis(state, AgentResult(
            agent_name=DIENST, ergebnis=None, status="fehler",
            fehler=f"{DIENST} nicht registriert",
        ))

    ergebnis_state = agent.invoke(agent_state)
    status: str = ergebnis_state.get("status", "fehler")
    logger.debug(
        "dispatch_dateien_wurzeln: Agent-Ergebnis — status='%s'", status,
    )

    # ── Der vierte Ausgang ──────────────────────
    if status == "rejected":
        return _mit_ergebnis(state, _ablehnung(ergebnis_state))

    # Ein Urteil des Dienstes traegt seine drei Teile im Zustand mit; ohne
    # sie waere `abgelehnt` formal unzulaessig — und genau das ist der
    # Riegel, der eine Sackgasse verhindert (`agents/base.py`).
    korrektur: Korrektur | None = ergebnis_state.get("parameter", {}).get("korrektur")
    if status == "abgelehnt" and korrektur is None:
        logger.error(
            "dispatch_dateien_wurzeln: Ablehnung ohne Korrektur — als Stoerung "
            "gemeldet, weil eine Ablehnung ohne Vorschlag eine Sackgasse ist"
        )
        status = "fehler"

    ergebnis = AgentResult(
        agent_name=DIENST,
        ergebnis=ergebnis_state.get("ergebnis"),
        status=status,
        fehler=ergebnis_state.get("fehler"),
        rueckfrage=ergebnis_state.get("rueckfrage"),
        korrektur=korrektur if status == "abgelehnt" else None,
        schritte=ergebnis_state.get("schritte", []),
        meta={"fortsetzung": fortsetzung},
    )

    if ergebnis.status == "rueckfrage":
        redis_manager.set_json(
            pending_key,
            {
                "agent_name": DIENST,
                "action": ergebnis_state.get("parameter", {}).get("action", ""),
                "rueckfrage": ergebnis.rueckfrage,
                "parameter": ergebnis_state.get("parameter", agent_state["parameter"]),
            },
            ttl_seconds=PENDING_TTL_SECONDS,
        )
        logger.info(
            "dispatch_dateien_wurzeln: Tor offen, Auftrag gemerkt (TTL=%ds)",
            PENDING_TTL_SECONDS,
        )

    return _mit_ergebnis(state, ergebnis)


def _ablehnung(ergebnis_state: dict) -> AgentResult:
    """Baut den vierten Ausgang: Befund, Beleg, Vorschlag.

    Der Vorschlag geht an den Auftraggeber und **nicht** in den Bestand —
    ein Dienst, der seine eigene Korrektur ausfuehrt, hat den Auftrag
    ersetzt statt ihn beurteilt.
    """
    schritte: list[dict] = ergebnis_state.get("schritte", [])
    grund: str = schritte[-1].get("ergebnis", "unbekannt") if schritte else "unbekannt"
    rand: str = rand_text()

    logger.info("dispatch_dateien_wurzeln: abgelehnt — %s", grund)
    return AgentResult(
        agent_name=DIENST,
        ergebnis=None,
        status="abgelehnt",
        korrektur=Korrektur(
            befund="Das habe ich nicht als Auftrag ueber ein Verzeichnis verstanden.",
            beleg=f"Klassifikation: {grund}",
            vorschlag=(
                f"Nenn mir das Verzeichnis als Ganzes, etwa 'du darfst in "
                f"{rand.split(',')[0].strip()} nachsehen' — oder frag mich mit "
                f"'worauf hast du Zugriff', was schon freigegeben ist."
            ),
        ),
    )


def _mit_ergebnis(state: dict, ergebnis: AgentResult) -> dict:
    """Haengt ein AgentResult an und setzt die Anzeigefelder.

    **Jeder Rueckkehrpfad setzt `management_result`** — wer nur bei Erfolg
    schreibt, macht "nicht gelaufen" von "so gelaufen" ununterscheidbar
    (`22_STILLE_FEHLER` §5).
    """
    bisherige: list = state.get("agent_results", [])

    if ergebnis.status == "abgeschlossen" and ergebnis.ergebnis:
        anzeige: str = str(ergebnis.ergebnis)
        detail: str = str(ergebnis.ergebnis)
    elif ergebnis.status == "rueckfrage" and ergebnis.rueckfrage:
        anzeige = ergebnis.rueckfrage
        detail = "Rueckfrage: Bestaetigung am Tor erforderlich"
    elif ergebnis.status == "dismissed":
        anzeige = str(ergebnis.ergebnis or "Abgelehnt — nichts geaendert.")
        detail = "Der Mensch hat am Tor abgelehnt"
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
            "dispatch_dateien_wurzeln: Status '%s' ohne Anzeigetext — der "
            "Turn zeigte sonst nichts an", ergebnis.status,
        )

    return {
        "agent_results": bisherige + [ergebnis],
        "agent_name": "",
        "management_result": anzeige,
        "management_detail": detail,
    }
