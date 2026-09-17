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

from agents import AgentRegistry
from agents.object_nearness import service_order
from config import PROMPTS
from graph.format.agent_results import format_success_lines
from graph.state import ConversationState
from plugins import get_registry
from plugins.base import BaseManager

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

    # Ergebnisse nach Status gruppieren.
    #
    # `rejected` bleibt bewusst unbehandelt: Es ist die Vorform des vierten
    # Ausgangs, eine Ablehnung ohne Begruendung, und ein Block darueber
    # koennte dem Nutzer nichts sagen ausser "ging nicht". Der Weg fuehrt
    # nach `abgelehnt`, wo Befund und Vorschlag mitkommen — nicht in einen
    # Block fuer den blanken Fall.
    refusals: list = [
        r for r in agent_results
        if hasattr(r, "status") and r.status == "abgelehnt"
        and getattr(r, "korrektur", None) is not None
    ]
    inquiries: list = [
        r for r in agent_results
        if hasattr(r, "status") and r.status == "rueckfrage"
        and hasattr(r, "rueckfrage") and r.rueckfrage
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

    # Prioritaet 2: Ablehnung mit Gegenangebot.
    #
    # Sie steht VOR dem Fehler: Ein Urteil ist keine Stoerung, und wer
    # beides vorliegen hat, braucht zuerst die Auskunft, was stattdessen
    # ginge.
    #
    # Der Kontext wird geschnitten, wie bei Erfolg und Fehler.
    #
    # **Hier stand zuerst `False`, mit der Begruendung, der Vorschlag sei
    # nur im Zusammenhang der Aeusserung verstaendlich. Die Begruendung war
    # falsch:** Der Schnitt entfernt Gedaechtnis und Web, nicht die
    # Aeusserung — die steht ohnehin im Prompt. Gemessen am 17.08.2026:
    # Zwei Ablehnungen mit ungeschnittenem Kontext erreichten die Antwort
    # NICHT (Nova beantwortete nur die Sachfrage), waehrend eine
    # Erfolgsmeldung mit Schnitt am selben Tag Tag, Uhrzeit und Eintrag
    # nannte. Der ungeschnittene Kontext liess den Block untergehen.
    #
    # **Hat ein anderer Dienst den Auftrag danach erledigt, gilt der Erfolg**
    # (17.09.2026, Scheibe 12 D1): Seit der Planner nach einer Ablehnung den
    # naechsten Dienst fragt, koennen beide im selben Turn stehen — und die
    # Ablehnung des ersten ist dann eine Weitergabe, keine Auskunft an den
    # Nutzer. Dasselbe gilt, wenn der zweite scheiterte oder verworfen wurde:
    # Dann gehoert sein Ausgang in den Block, nicht die Weitergabe davor.
    if refusals and not (successes or errors or dismissed):
        return (_build_task_ablehnung(refusals), True)

    # Prioritaet 3: Fehler
    if errors:
        return (_build_task_error(errors), True)

    # Prioritaet 4: Dismissed (User hat abgelehnt)
    if dismissed:
        return (_build_task_dismissed(dismissed), True)

    # Prioritaet 5: Erfolg
    if successes:
        return (_build_task_success(successes), True)

    # Prioritaet 6: Legacy-Management (kein Agent, alter Manager-Pfad)
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


def _build_task_ablehnung(results: list) -> str:
    """[AUFGABE] fuer eine begruendete Ablehnung mit Gegenangebot.

    Vorbedingung: jedes Ergebnis traegt `status == "abgelehnt"` und eine
    Korrektur — geprueft beim Aufrufer und von AgentResult erzwungen.

    Nachbedingung: nicht-leerer Text mit Befund und Vorschlag je Dienst.

    Die drei Teile der Korrektur wandern vollstaendig in den Block. Der
    Befund allein waere eine Sackgasse; der Vorschlag ist das, was den
    Unterschied zwischen "ging nicht" und "so ginge es" macht.
    """
    zeilen: list[str] = []
    for r in results:
        k = r.korrektur
        # Ohne das Wort "Agent": Der Block steht im Prompt der Figur, und
        # dort ist eine benannte Instanz eine dritte Person neben ihr.
        # Dieselbe Aenderung wie in `format_success_lines` (20.08.2026).
        zeilen.append(
            f"- {r.agent_name}: {k.befund} "
            f"Stattdessen moeglich: {k.vorschlag}"
        )
    ergebnis_texte: str = "\n".join(zeilen)

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if not ergebnis_texte.strip():
        logger.error(
            "Ablehnungs-Block: %d Ergebnisse, aber leerer Text — der "
            "Vorschlag erreicht den Nutzer nicht", len(results),
        )
        return ""

    return PROMPTS["responder.aufgabe_ablehnung"].format(
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


def _manager_zu_target(registry: dict, target_lower: str) -> BaseManager | None:
    """Waehlt den Manager, dessen Ziel zum `management_target` passt.

    Vorbedingung: `target_lower` ist nicht leer und bereits kleingeschrieben.
    Nachbedingung: Genau ein Manager oder None. **Ein exakter Treffer schlaegt
    jeden unscharfen**, und bei mehreren unscharfen wird keiner gewaehlt.
    Fehlerfaelle: Mehrdeutigkeit — laut gemeldet, None zurueckgegeben. Der
    Planner faellt dann auf seine spaeteren Prioritaeten zurueck, statt einen
    Dienst nach Verzeichnisreihenfolge zu erwischen.

    **Warum Mehrdeutigkeit nicht still auf den ersten faellt:** Der erste ist
    der alphabetisch erste, und das ist keine fachliche Aussage. Ein falsch
    zugestellter Auftrag laeuft durch und liefert ein Ergebnis, das richtig
    aussieht — die teuerste Form des Fehlers (`22_STILLE_FEHLER`).

    Args:
        registry: Die Manager-Registry.
        target_lower: Das kleingeschriebene `management_target`.

    Returns:
        Der zustaendige Manager oder None.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not target_lower:
        logger.error(
            "_manager_zu_target: leeres Ziel — der Aufrufer prueft das vorher"
        )
        return None

    # ── Verarbeitung ────────────────────────────
    for manager in registry.values():
        if manager.ziel == target_lower:
            logger.info(
                f"Planner: Match via target '{target_lower}' → {manager.ziel} (exakt)"
            )
            return manager

    unscharf: list = [
        manager for manager in registry.values()
        if manager.ziel in target_lower or target_lower in manager.ziel
    ]

    # ── Ausgabe-Verifikation ────────────────────
    if len(unscharf) > 1:
        namen: str = ", ".join(sorted(m.ziel for m in unscharf))
        logger.error(
            f"Planner: Ziel '{target_lower}' passt unscharf auf mehrere Dienste "
            f"({namen}) — keiner gewaehlt. Eine Zuordnung nach "
            f"Verzeichnisreihenfolge waere eine Muenze, kein Urteil"
        )
        return None

    if unscharf:
        logger.info(
            f"Planner: Match via target '{target_lower}' → {unscharf[0].ziel} (unscharf)"
        )
        return unscharf[0]

    return None


# Ausgaenge, nach denen der naechste Dienst gefragt wird: begruendete
# Ablehnung und die Vorform ohne Begruendung ("rejected" der Klassifikation).
DECLINED: frozenset[str] = frozenset({"abgelehnt", "rejected"})


def service_order_for(state: ConversationState, registry: dict, fallback) -> list[str]:  # noqa: ANN001
    """Die Reihenfolge der Dienste fuer diesen Auftrag.

    Vorbedingung: `registry` ist die Manager-Registry; `fallback` ist der
        Treffer der Prioritaeten 2 bis 4 oder None.
    Nachbedingung: zuerst die Dienste, deren Merkmal ein akutes Objekt erreicht
        (nach Naehe), dann der Fallback — ausser der Fallback traegt selbst kein
        Merkmal, dann steht er vorn. Jeder hoechstens einmal; nur Namen, fuer
        die es einen Manager oder Agenten gibt.
    Fehlerfaelle: keine Ausnahme; ein Name ohne Dienst wird laut verworfen.

    Protokolliert die Groessen der Weiche, bevor sie entscheidet (F-LOG-3).
    """
    # ── Eingabe-Validierung ─────────────────────
    urteil = state.get("objekt_urteil")
    aus_naehe: list[str] = service_order(urteil)
    # Nach einem Ausfall der Sachlage traegt der Zustand die Objekte des
    # Vorturns — die Naehe wuerde nach dem Gegenstand von gestern ordnen. Auf
    # einem Impuls-Turn dagegen baut der Gedanke bewusst auf dieser Lage auf
    # (Bruecke, Scheibe 4); dort ordnet sie weiter. `[gemessen 17.09.2026]`
    # 114 von 542 Sachlagen in 14 Tagen waren `ausfall_uebernommen`.
    if isinstance(urteil, dict) and urteil.get("herkunft") == "ausfall_uebernommen" and aus_naehe:
        logger.info(f"Planner-Weiche: Naehe {aus_naehe} verworfen — Sachlage vom Vorturn uebernommen (Ausfall)")
        aus_naehe = []

    # ── Verarbeitung ────────────────────────────
    # Die Naehe ordnet nur unter Diensten, die ein Objekt-Merkmal tragen. Ein
    # Dienst ohne Merkmal kann an ihr nicht teilnehmen — zeigt der Router auf
    # ihn (`dateien`, `wissen`, ...), steht er vorn, und die nahen Dienste
    # folgen nur nach einer Ablehnung. Sonst naehme die Notiz einen Auftrag an
    # den Dateien an, weil das Objekt zufaellig einer Sache aehnelt.
    fallback_name: str | None = getattr(fallback, "ziel", None)
    fallback_agent = AgentRegistry.finden(fallback_name) if fallback_name else None
    ohne_merkmal: bool = bool(fallback_name) and not (getattr(fallback_agent, "objekt_merkmal", "") or "").strip()
    kandidaten: list[str] = (
        [fallback_name, *aus_naehe] if ohne_merkmal else [*aus_naehe, *([fallback_name] if fallback_name else [])]
    )

    reihenfolge: list[str] = []
    for name in kandidaten:
        if name in reihenfolge:
            continue
        bekannt = AgentRegistry.finden(name) is not None or any(m.ziel == name for m in registry.values())
        if not bekannt:
            logger.error(f"Planner: Dienst '{name}' aus dem Urteil ist nicht angemeldet — verworfen")
            continue
        reihenfolge.append(name)

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        f"Planner-Weiche: naehe={aus_naehe} (urteil={getattr(urteil, 'get', lambda _k: None)('ergebnis')}), "
        f"fallback={getattr(fallback, 'ziel', None)}, target='{state.get('management_target', '')}', "
        f"needs_timeline={state.get('needs_timeline')}, fallback_ohne_merkmal={ohne_merkmal} → {reihenfolge}"
    )
    return reihenfolge


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
                        "Planner: Resume — Agent '%s' lief bereits in diesem Turn (status=%s) — "
                        "Turn beenden, weiter zum "
                        "Responder",
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

    # ~~Prioritaet 1: Timeline-Flag aus Router~~ — entfernt am 17.09.2026
    # (Scheibe 12 D1, `PLANNER-ZEITWORT-UEBERSTIMMT-DIENSTWAHL`). Jede
    # Zeitangabe schickte die Bitte an die Timeline, auch "Merk dir, dass ich
    # morgen Mehl brauche". Die Wahl folgt jetzt dem Objekt: zuerst die Dienste,
    # deren Merkmal das akute Objekt erreicht (`objekt_urteil`), dann der Treffer
    # der Prioritaeten unten.

    # Prioritaet 2: Intent-Match
    intent: str = user_intent
    if intent:
        for manager in registry.values():
            if intent in manager.router_intents:
                zustaendiger = manager
                logger.info(f"Planner: Match via intent '{intent}' → {manager.ziel}")
                break

    # Priorität 3: management_target gegen die Manager-Ziele
    #
    # **Exakt vor unscharf, und Mehrdeutigkeit wird gemeldet.** Die frühere
    # Fassung nahm den ersten Manager, dessen Ziel eine Teilzeichenkette des
    # Ziels war oder umgekehrt — und die Registry wird in der Reihenfolge des
    # sortierten Verzeichnis-Scans durchlaufen. Solange kein Zielname eine
    # Teilzeichenkette eines anderen war, fiel das nicht auf; bei `dateien`
    # und `dateien_wurzeln` fällt es auf, denn `"dateien" in "dateien_wurzeln"`
    # ist wahr und `dateien_manager` kommt alphabetisch zuerst. Der lesende
    # Dienst schluckte damit jede Freigabe-Anfrage, und der Fehler sähe wie
    # eine falsche Klassifikation aus statt wie eine Namenskollision.
    if not zustaendiger:
        target_lower: str = state.get("management_target", "").lower()
        if target_lower:
            zustaendiger = _manager_zu_target(registry, target_lower)

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

    reihenfolge: list[str] = service_order_for(state, registry, zustaendiger)
    if not reihenfolge:
        logger.warning(
            f"Planner: Kein Manager gefunden "
            f"(intent='{user_intent}', target='{state.get('management_target')}', "
            f"action='{state.get('management_action')}')"
        )
        state["node_annotations"].append("Planner: Kein Manager gefunden")
        return state

    # Die Dienste der Reihe nach: Wer noch nicht lief, wird gefragt. Wer
    # ablehnte, gibt an den naechsten weiter — entschieden am 16.09.2026: "fuer
    # die Grenzfaelle beide ansprechen, wenn der eine nicht will, soll der andere
    # auch gefragt werden". Jeder andere Ausgang beendet die Reihe.
    for name in reihenfolge:
        agent = AgentRegistry.finden(name)
        if agent is None:
            zustaendiger = registry.get(name) or next(
                (m for m in registry.values() if m.ziel == name), None)
            if zustaendiger is None:
                logger.error(f"Planner: '{name}' in der Reihenfolge ist weder Agent noch Manager — uebergangen")
                continue
            break
        vorheriges = _agent_bereits_gelaufen(state, agent.name)
        if vorheriges is None:
            logger.info(f"Planner: Agent-Pfad — frage '{agent.name}' (Reihenfolge {reihenfolge})")
            state["agent_name"] = agent.name
            state["management_result"] = ""
            state["management_detail"] = ""
            return state
        if vorheriges.status in DECLINED:
            logger.info(
                f"Planner: '{agent.name}' lehnte ab (status={vorheriges.status}) — "
                f"naechster in {reihenfolge}"
            )
            continue
        logger.info(
            f"Planner: Agent '{agent.name}' bereits gelaufen (status={vorheriges.status}) — "
            "weiter zum Responder"
        )
        _write_task_block(state)
        return state
    else:
        logger.info(f"Planner: alle Dienste der Reihenfolge {reihenfolge} gefragt — weiter zum Responder")
        _write_task_block(state)
        return state

    logger.info(f"Planner: Delegiere an '{zustaendiger.ziel}' (Manager ohne Agent)")

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
        logger.exception(f"{type(fehler).__name__}: Planner: Fehler bei '{zustaendiger.ziel}'")
        state["node_annotations"].append(f"Planner-Fehler: {fehler}")

    _write_task_block(state)
    return state
