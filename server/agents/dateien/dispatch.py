"""Dispatch für den lesenden Dienst — ConversationState <-> AgentState.

Spezifikation: docs/novaberg-agent-dateien_k.md §8.1.

**Kein Tor, kein Rückweg.** Dieser Dienst ändert nichts, also gibt es nichts zu
bestätigen; ein offener Auftrag in Redis hätte keinen Gegenstand. Was er nicht
beantworten kann, geht durch den vierten Ausgang und trägt einen Vorschlag.

**Der Suchschlüssel wandert als angemeldeter Bedarf mit** (§8.1): `such_vektor`
ist der Vektor, mit dem in diesem Turn auch die Gedächtnisschichten gesucht
haben. Ein eigenes Embedding wäre derselbe Text ein zweites Mal — ohne die
Verschiebung, die ihn zu diesem Turn gehören lässt.
"""

import logging

from agents import AgentRegistry
from agents.base import AgentResult, AgentState, Korrektur
from graph.reiz import reiz_text

logger = logging.getLogger("ki_server.agents.dateien.dispatch")

DIENST: str = "dateien"


def dispatch_dateien(state: dict) -> dict:
    """ConversationState -> DateienAgent -> ConversationState.

    Vorbedingung: `state` trägt `user_id`; `management_action` benennt den
    Vorgang, `such_vektor` den Suchschlüssel des Turns.
    Nachbedingung: `agent_results` trägt genau ein AgentResult mehr, und
    `agent_name` ist zurückgesetzt, damit der Planner neu entscheidet.
    Fehlerfaelle: fehlende `user_id`, unbekannter Dienst — beide mit
    gesetztem `management_result`.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id: str = state.get("user_id", "")
    if not user_id:
        logger.error(
            "dispatch_dateien: Auftrag ohne user_id — ohne Paar gibt es keine "
            "Freigabe, in der gesucht werden dürfte"
        )
        return _mit_ergebnis(state, AgentResult(
            agent_name=DIENST, ergebnis=None, status="fehler",
            fehler="Auftrag ohne user_id",
        ))

    such_vektor: list = state.get("such_vektor") or []
    if not such_vektor:
        # Kein Fehler: Die scharfen Kanäle arbeiten ohne ihn (§6.3). Aber der
        # dense Kanal fällt dann aus, und eine Frage ohne Fachbegriff findet
        # nichts mehr — das gehört ins Protokoll, nicht ins Schweigen.
        logger.warning(
            "dispatch_dateien: kein such_vektor im Turn — die Suche läuft nur "
            "über Name und Stichwort, die Bedeutung fällt aus"
        )

    logger.debug(
        "dispatch_dateien: Einstieg — action='%s', target='%s'",
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
        logger.error("dispatch_dateien: '%s' nicht in der Registry", DIENST)
        return _mit_ergebnis(state, AgentResult(
            agent_name=DIENST, ergebnis=None, status="fehler",
            fehler=f"{DIENST} nicht registriert",
        ))

    ergebnis_state = agent.invoke(agent_state)
    status: str = ergebnis_state.get("status", "fehler")
    logger.debug("dispatch_dateien: Agent-Ergebnis — status='%s'", status)

    # ── Der vierte Ausgang ──────────────────────
    if status == "rejected":
        return _mit_ergebnis(state, _ablehnung(ergebnis_state))

    # Ein Urteil des Dienstes trägt seine drei Teile im Zustand mit; ohne sie
    # wäre `abgelehnt` formal unzulässig — und genau das ist der Riegel, der
    # eine Sackgasse verhindert (`agents/base.py`).
    korrektur: Korrektur | None = ergebnis_state.get("parameter", {}).get("korrektur")
    fehlertext: str | None = ergebnis_state.get("fehler")
    if status == "abgelehnt" and korrektur is None:
        logger.error(
            "dispatch_dateien: Ablehnung ohne Korrektur — als Störung gemeldet, "
            "weil eine Ablehnung ohne Vorschlag eine Sackgasse ist"
        )
        status = "fehler"
        # Der Ausgang traegt seinen Pflichtteil selbst: `AgentResult` verlangt
        # bei "fehler" eine Begruendung und wirft sonst. Ohne diese Zeile
        # riss der Umbau des Status den ganzen Turn — und zwar genau dann,
        # wenn ohnehin schon etwas nicht stimmte.
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


def _ablehnung(ergebnis_state: dict) -> AgentResult:
    """Baut den vierten Ausgang für eine Äußerung, die kein Leseauftrag war.

    Vorbedingung: `ergebnis_state` stammt aus einer Klassifikation mit
    `status="rejected"`.
    Nachbedingung: ein AgentResult mit vollständiger Korrektur.

    Der Vorschlag geht an den Auftraggeber und **nicht** in den Bestand — ein
    Dienst, der seine eigene Korrektur ausführt, hat den Auftrag ersetzt statt
    ihn beurteilt.
    """
    # ── Eingabe-Validierung ─────────────────────
    grund: str = ergebnis_state.get("parameter", {}).get("grund", "") or "kein Grund angegeben"

    # ── Verarbeitung ────────────────────────────
    logger.info("dispatch_dateien: abgelehnt — %s", grund)

    # ── Ausgabe-Verifikation ────────────────────
    return AgentResult(
        agent_name=DIENST,
        ergebnis=None,
        status="abgelehnt",
        korrektur=Korrektur(
            befund="Das habe ich nicht als Frage an die abgelegten Unterlagen verstanden.",
            beleg=f"Klassifikation: {grund}",
            vorschlag=(
                "Wenn es in einer Datei stehen soll, nenn mir den Dateinamen "
                "oder ein Fachwort daraus — dann sehe ich nach."
            ),
        ),
    )


def _mit_ergebnis(state: dict, ergebnis: AgentResult) -> dict:
    """Hängt ein AgentResult an und setzt die Anzeigefelder.

    Vorbedingung: `ergebnis` ist vollständig.
    Nachbedingung: `agent_results` um eins länger, `agent_name` zurückgesetzt,
    `management_result` und `management_detail` gesetzt.

    **Jeder Rückkehrpfad setzt `management_result`** — wer nur bei Erfolg
    schreibt, macht „nicht gelaufen" von „so gelaufen" ununterscheidbar
    (`22_STILLE_FEHLER` §5).
    """
    # ── Verarbeitung ────────────────────────────
    bisherige: list = state.get("agent_results", [])

    if ergebnis.status == "abgeschlossen" and ergebnis.ergebnis:
        anzeige: str = str(ergebnis.ergebnis)
        detail: str = str(ergebnis.ergebnis)
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
            "dispatch_dateien: Status '%s' ohne Anzeigetext — der Turn zeigte "
            "sonst nichts an", ergebnis.status,
        )

    # ── Ausgabe-Verifikation ────────────────────
    return {
        "agent_results": bisherige + [ergebnis],
        "agent_name": "",
        "management_result": anzeige,
        "management_detail": detail,
    }
