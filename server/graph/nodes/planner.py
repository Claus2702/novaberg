"""
Planner Node — Management Plan-Phase.

Wird nur aktiviert wenn der Router einen Management-Intent erkannt hat
(management_action != ""). Findet den zuständigen Manager und lässt ihn
die Operation planen. Der Manager erzeugt pending_writes und eine
Beschreibung für den Responder.

Kein direkter DB-Write — alles geht über pending_writes → Dispatcher.

Position im Graph:
  Router → Enricher → [Planner]* → Responder → ...
"""

import json
import logging

from config       import PROMPTS
from graph.format.agent_results import format_success_lines
from graph.state  import ConversationState
from plugins      import get_registry
from agents       import AgentRegistry

logger = logging.getLogger("ki_server.planner")


# ─────────────────────────────────────────────
# Task-Block: Ergebnis-Aufbereitung fuer Responder
# ─────────────────────────────────────────────
# Der Planner interpretiert Agent-Ergebnisse und baut einen
# fertigen [AUFGABE]-Block. Der Responder konsumiert nur noch.
# "Daten vollstaendig transportieren, Formatierung am Konsumenten."


def _build_task_block(
    agent_results: list,
    mgmt_result:   str = "",
    mgmt_detail:   str = "",
) -> tuple[str, bool]:
    """Erstellt den [AUFGABE]-Block und entscheidet ueber Kontext-Schnitt.

    Prueft agent_results nach Prioritaet:
      1. Rueckfrage  → Block mit Frage, KEIN Kontext-Schnitt
      2. Fehler      → Block mit Fehlermeldung, Kontext-Schnitt
      3. Dismissed   → Block mit Ablehnung, Kontext-Schnitt
      4. Erfolg      → Block mit Ergebnis, Kontext-Schnitt
      5. Legacy-Mgmt → Block mit Management-Ergebnis, Kontext-Schnitt
      rejected (Classify) wird ignoriert — ist ein Nicht-Ereignis.

    Returns:
        (block_text, context_cut) — block_text ist leer wenn kein Block noetig.
    """
    if not agent_results and not mgmt_result:
        return ("", False)

    # Ergebnisse nach Status gruppieren (rejected bewusst ignoriert)
    inquiries: list = [
        r for r in agent_results
        if hasattr(r, "status") and r.status == "rueckfrage" and hasattr(r, "rueckfrage") and r.rueckfrage
    ]
    errors: list = [
        r for r in agent_results
        if hasattr(r, "status") and r.status == "fehler"
    ]
    dismissed: list = [
        r for r in agent_results
        if hasattr(r, "status") and r.status == "dismissed"
    ]
    successes: list = [
        r for r in agent_results
        if hasattr(r, "status") and r.status == "abgeschlossen"
    ]

    # Prioritaet 1: Rueckfrage (kein Kontext-Schnitt — User braucht Kontext fuer Antwort)
    if inquiries:
        return (_build_task_inquiry(inquiries[0]), False)

    # Prioritaet 2: Fehler
    if errors:
        return (_build_task_error(errors), True)

    # Prioritaet 3: Dismissed (User hat abgelehnt)
    if dismissed:
        return (_build_task_dismissed(dismissed), True)

    # Prioritaet 4: Erfolg
    if successes:
        return (_build_task_success(successes), True)

    # Prioritaet 5: Legacy-Management (kein Agent, alter Manager-Pfad)
    if mgmt_result:
        return (_build_task_legacy(mgmt_result, mgmt_detail), True)

    return ("", False)


def _build_task_inquiry(result) -> str:
    """[AUFGABE] fuer Pflicht-Rueckfrage (inkl. Disambiguierung)."""
    rueckfrage_text: str = result.rueckfrage

    # Disambiguierung-JSON erkennen
    if rueckfrage_text.startswith("{"):
        try:
            disamb: dict = json.loads(rueckfrage_text)
            if disamb.get("typ") == "disambiguierung":
                return PROMPTS["responder.aufgabe_disambiguierung"].format(
                    rueckfrage_text=rueckfrage_text
                )
        except (json.JSONDecodeError, TypeError):
            pass

    return PROMPTS["responder.aufgabe_rueckfrage"].format(
        rueckfrage_text=rueckfrage_text
    )


def _build_task_success(results: list) -> str:
    """[AUFGABE] fuer erfolgreiche Agent-Aktionen."""
    ergebnis_texte: str = format_success_lines(results)
    return PROMPTS["responder.aufgabe_erfolg"].format(
        ergebnis_texte=ergebnis_texte
    )


def _build_task_dismissed(results: list) -> str:
    """[AUFGABE] fuer abgelehnte Aktionen (User hat Nein gesagt)."""
    ergebnis_texte: str = "\n".join(
        f"- Agent '{r.agent_name}': {r.ergebnis}" for r in results
    )
    return PROMPTS["responder.aufgabe_verworfen"].format(
        ergebnis_texte=ergebnis_texte
    )


def _build_task_error(results: list) -> str:
    """[AUFGABE] fuer fehlgeschlagene Agent-Aktionen."""
    fehler_texte: str = "\n".join(
        f"- Agent '{r.agent_name}': {r.fehler}" for r in results if hasattr(r, "fehler")
    )
    return PROMPTS["responder.aufgabe_fehler"].format(
        fehler_texte=fehler_texte
    )


def _build_task_legacy(mgmt_result: str, mgmt_detail: str) -> str:
    """[AUFGABE] fuer Legacy-Management (alter Manager-Pfad ohne Agent)."""
    detail_text: str = f"\nErgebnis:\n{mgmt_detail}" if mgmt_detail else ""
    return PROMPTS["responder.aufgabe_mgmt"].format(
        mgmt_result=mgmt_result,
        detail_text=detail_text
    )


def _write_task_block(state: ConversationState) -> None:
    """Schreibt task_block und task_context_cut in den State.

    Wird an jedem Planner-Austrittspunkt aufgerufen, an dem
    Agent-Ergebnisse vorliegen koennten.
    """
    agent_results: list = state.get("agent_results", [])
    mgmt_result:   str  = state.get("management_result", "")
    mgmt_detail:   str  = state.get("management_detail", "")

    block, cut = _build_task_block(agent_results, mgmt_result, mgmt_detail)
    state["task_block"]       = block
    state["task_context_cut"] = cut

    if block:
        logger.info(f"Planner: task_block erstellt (context_cut={cut}, {len(block)} Zeichen)")


def _agent_bereits_gelaufen(state: ConversationState, agent_name: str):
    """Prüft, ob ein Agent in diesem Turn bereits gelaufen ist.

    Schleifen-Schutz (AGT-FIX3, Chat 22). Liest die in diesem Turn
    angefallenen `agent_results` und liefert das Ergebnis des Agenten
    zurück, falls er bereits lief.

    Args:
        state: Der ConversationState des laufenden Turns.
        agent_name: Name des Agenten, der geprüft wird.

    Returns:
        Das vorherige AgentResult, oder None wenn der Agent noch nicht lief.
    """
    if not agent_name:
        logger.warning("Planner/Guard: Leerer agent_name übergeben — behandle als 'nicht gelaufen'")
        return None

    bisherige = state.get("agent_results", [])
    bereits_gelaufen = {r.agent_name: r for r in bisherige if hasattr(r, "agent_name")}
    vorheriges = bereits_gelaufen.get(agent_name)

    logger.debug(
        "Planner/Guard: agent='%s', results_im_turn=%d, bereits_gelaufen=%s",
        agent_name, len(bisherige), vorheriges is not None,
    )
    return vorheriges


def plan(
    state:        ConversationState,
    postgres_url: str
) -> ConversationState:
    """
    Delegiert die Plan-Phase an den zuständigen Manager.
    Der Manager erzeugt pending_writes + management_result/detail.
    """

    action: str = state.get("management_action", "")

    if not action:
        logger.info("Planner: Kein Management-Intent — Durchlauf")
        return state

    # ── Resume-Flow: Agent wartet auf Antwort ──────
    if action == "resume":
        from tools.redis_manager import redis_manager

        user_id = state.get("user_id", "")
        pending = redis_manager.get_json(f"pending_agent:{user_id}")

        if pending:
            agent_name = pending.get("agent_name", "")
            agent = AgentRegistry.finden(agent_name)
            if agent:
                # Schleifen-Schutz im Resume-Pfad (AGENT-RUECKFRAGE-LOOP):
                # Der Dispatch schreibt bei erneuter Rückfrage den Pending-Key
                # sofort wieder nach Redis. Ohne diese Prüfung läse der Planner
                # ihn im SELBEN Turn erneut und dispatchte mit identischem
                # user_prompt → Rekursion bis Recursion-Limit 25.
                vorheriges = _agent_bereits_gelaufen(state, agent_name)
                if vorheriges:
                    logger.info(
                        "Planner: Resume — Agent '%s' lief bereits in diesem Turn (status=%s) — Turn beenden, weiter zum Responder",
                        agent_name, vorheriges.status,
                    )
                    _write_task_block(state)
                    return state

                logger.info(f"Planner: Resume-Flow — Agent '{agent_name}'")
                state["agent_name"] = agent_name
                state["management_result"] = ""
                state["management_detail"] = ""
                return state
            else:
                logger.warning(f"Planner: Resume-Flow — Agent '{agent_name}' nicht in Registry")
        else:
            logger.warning("Planner: Resume-Flow aber kein pending Agent in Redis")

        # Fallback: Kein Resume möglich — normalen Durchlauf machen
        _write_task_block(state)
        state["management_action"] = ""
        return state

    external = state.get("external")
    user_intent: str = external.emotion.intent if external else ""
    logger.info(
        f"Planner: action={action}, target={state.get('management_target', '')}, "
        f"intent={user_intent}"
    )

    # ── Manager finden ──────────────────────────
    registry: dict = get_registry()
    zustaendiger = None

    # Priorität 1: Timeline-Flag aus Router
    if state.get("needs_timeline") and state.get("management_action"):
        for manager in registry.values():
            if manager.ziel == "timeline":
                zustaendiger = manager
                logger.info(f"Planner: Match via needs_timeline → {manager.ziel}")
                break

    # Priorität 2: Intent-Match
    if not zustaendiger:
        intent: str = user_intent
        if intent:
            for manager in registry.values():
                if intent in manager.router_intents:
                    zustaendiger = manager
                    logger.info(f"Planner: Match via intent '{intent}' → {manager.ziel}")
                    break

    # Priorität 3: management_target enthält Manager-Ziel
    if not zustaendiger:
        target_lower: str = state.get("management_target", "").lower()
        if target_lower:
            for name, manager in registry.items():
                if manager.ziel in target_lower or target_lower in manager.ziel:
                    zustaendiger = manager
                    logger.info(f"Planner: Match via target '{target_lower}' → {manager.ziel}")
                    break

    # Priorität 4: Fallback — NotizenManager als Auffangbecken
    # Timeline-Kontext allein reicht NICHT — ohne Datumsbezug im Prompt
    # ist der TimelineManager der falsche Empfänger (Bug P12).
    if not zustaendiger and state.get("management_action"):
        if state.get("needs_timeline"):
            # Nur wenn der Router explizit Timeline-Bedarf erkannt hat
            for manager in registry.values():
                if manager.ziel == "timeline":
                    zustaendiger = manager
                    logger.info(f"Planner: Fallback via needs_timeline → {manager.ziel}")
                    break

        if not zustaendiger:
            for manager in registry.values():
                if manager.ziel == "notizen":
                    zustaendiger = manager
                    logger.info(f"Planner: Fallback → {manager.ziel}")
                    break

    if not zustaendiger:
        logger.warning(
            f"Planner: Kein Manager gefunden "
            f"(intent='{user_intent}', target='{state.get('management_target')}', "
            f"action='{state.get('management_action')}')"
        )
        state["node_annotations"].append(f"Planner: Kein Manager gefunden")
        return state

    logger.info(f"Planner: Delegiere an '{zustaendiger.ziel}'")

    # Epic 11: Prüfe ob ein Agent den Manager ersetzt
    agent = AgentRegistry.finden(zustaendiger.ziel)
    if agent:
        vorheriges = _agent_bereits_gelaufen(state, agent.name)
        if vorheriges:
            # Agent ist schon gelaufen — nicht nochmal aufrufen
            # Ergebnis liegt bereits in agent_results, management_result ist gesetzt
            # → Kein Manager-Aufruf, kein Agent-Aufruf, weiter zum Responder
            logger.info(f"Planner: Agent '{agent.name}' bereits gelaufen (status={vorheriges.status}) — weiter zum Responder")
            _write_task_block(state)
            return state
        else:
            # Agent noch nicht gelaufen — Agent-Pfad
            logger.info(f"Planner: Agent-Pfad — {agent.name} ersetzt Manager '{zustaendiger.ziel}'")
            state["agent_name"] = agent.name
            state["management_result"] = ""
            state["management_detail"] = ""
            return state

    # Manager plant die Operation
    try:
        ergebnis: dict = zustaendiger.plan(
            state        = state,
            postgres_url = postgres_url,
        )

        # pending_writes aus Planner an bestehende anhängen
        neue_writes: list = ergebnis.get("pending_writes", [])
        pending:     list = state.get("pending_writes", []) or []
        pending.extend(neue_writes)
        state["pending_writes"] = pending

        # Management-Ergebnis für Responder
        state["management_result"] = ergebnis.get("management_result", "")
        state["management_detail"] = ergebnis.get("management_detail", "")

        logger.info(
            f"Planner: {len(neue_writes)} pending_writes, "
            f"result='{state['management_result'][:60]}...'"
        )

    except Exception as fehler:
        logger.error(f"Planner: Fehler bei '{zustaendiger.ziel}' — {fehler}")
        state["node_annotations"].append(f"Planner-Fehler: {fehler}")

    _write_task_block(state)
    return state
