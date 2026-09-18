"""
Router Node — Entscheidet ueber Ressourcen-Routing.

Liest die Perzeption-Ergebnisse aus dem State und entscheidet,
welche Datenquellen und Aktionen fuer die Verarbeitung noetig sind.

Plugin-Erweiterung (A1.2):
  Der Router-Prompt wird dynamisch um Erkennungsregeln aller
  registrierten Manager-Plugins erweitert.

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).
"""

import json
import logging
from datetime import datetime

from agents.nmcp import aushaenge_sammeln
from agents.nmcp_quote import REGISTER
from agents.object_nearness import shadow_nearness
from config import PROMPTS, get_node_config, redis_client
from graph.reiz import reiz_ist_eigener_gedanke, reiz_text
from graph.state import ConversationState, pipeline_quelle
from memory.pipeline_log import log_decision
from memory.session import format_session_turns_numbered, session_turns_retrieve
from services.model_services import ChatRequest, model_service
from utils.offers import (
    Offer,
    carries_own_request,
    is_bare_consent,
    offer_load,
    offer_matches,
)

logger = logging.getLogger("ki_server.router")


def _build_router_prompt(
    state: ConversationState,
    session_turns: str | None = None,
    offer: Offer | None = None,
) -> str:
    """Baut den Router-System-Prompt aus [BLOCKNAME]-Bloecken zusammen.

    Reihenfolge nach Primacy/Recency (nova-01-t-d):
    OBEN:   [IDENTITAET] -> [AUFGABE]
    MITTE:  [KONTEXT] (Session-Turns) -> [AGENTEN] (Plugin-Regeln)
    UNTEN:  [REGELN] (direkt vor der User-Message)
    """
    external = state.get("external")
    bloecke: list[str] = [
        PROMPTS["router.identity"].format(
            today              = datetime.now().strftime("%d.%m.%Y, %H:%M Uhr"),
            intent             = external.emotion.intent               if external else "smalltalk",
            emotion            = external.emotion.emotion              if external else "neutral",
            arousal            = external.emotion.arousal              if external else 0.5,
            modus              = external.emotion.mode                 if external else "alltag",
            beziehungs_dynamik = external.emotion.relationship_dynamic if external else "neutral",
        ),
        PROMPTS["router.task"],
    ]

    if session_turns:
        bloecke.append(
            "[KONTEXT]\n"
            "Nutze den Verlauf fuer Rueckbezug-Aufloesung und "
            "Management-Target-Erkennung. "
            "Hoehere Nummern sind aktueller — loese Bezuege "
            "bevorzugt ueber die hoechsten Nummern auf.\n"
            f"\n{session_turns}"
        )

    # Die Lage (Scheibe 12 D2a): die akuten Objekte mit dem, was ueber sie
    # bekannt ist, und den Diensten, an deren Zettel die gerechnete Naehe sie
    # stellt. Damit liest der Empfang ein "Gerne" als Zustimmung zu einem Objekt
    # — der Verlauf allein trug das Angebot, nicht aber, worauf es sich bezog.
    # Auf einem Impuls-Turn kein Block: Zustimmen kann nur der Mensch. Der Reiz
    # ist dort Novas eigener Gedanke, und der Block lehrt das Modell, eine
    # Zustimmung als Auftrag zu lesen (zweite Kontrolle, 17.09.2026).
    # Das offene Angebot des Vorturns (Teil E1) traegt den Bezug, auf den sich
    # ein "Gerne" beziehen kann. Fehlt es, bleibt der Zustimmungssatz aus dem
    # Block — dann ist eine Zustimmung Gespraech, kein Auftrag.
    lage: str = "" if reiz_ist_eigener_gedanke(state) else build_situation_block(
        state.get("sachlage"), state.get("objekt_urteil"), offer=offer,
    )
    if lage:
        bloecke.append(lage)

    # Das schwarze Brett: die Aushaenge aller Dienste am Empfang, gesammelt
    # von der Dienst-Flaeche und nicht mehr nur von der Manager-Flaeche.
    #
    # Die Anweisung "beurteile jeden Zettel fuer sich" ist Pflicht und nicht
    # Verzierung: Liegen alle Zettel in einem Aufruf, waegt das Modell sie
    # unvermeidlich gegeneinander ab, ob es soll oder nicht. Die
    # Unabhaengigkeit ist damit eine Bitte an das Modell und keine
    # Eigenschaft des Aufbaus — deshalb steht sie hier ausdruecklich und
    # wird durch einen Zeugen geprueft.
    plugin_additions: str = aushaenge_sammeln(
        "pixie" if state.get("graph_rolle") == "pixie" else "user"
    )
    if plugin_additions:
        bloecke.append(
            "[AGENTEN]\n"
            "Die folgenden Aushaenge stammen von registrierten Diensten. "
            "Nur diese Regeln duerfen die Management-Felder setzen.\n"
            "\n"
            "Beurteile JEDEN Aushang FUER SICH: Passt er auf die Aeusserung "
            "oder nicht? Vergleiche die Aushaenge NICHT gegeneinander und "
            "waehle nicht den besten Treffer — mehrere duerfen passen. "
            "Kannst du bei einem Aushang nicht klar entscheiden, gilt er als "
            "passend; die Fachabteilung urteilt selbst und kann begruendet "
            "ablehnen.\n"
            f"\n{plugin_additions}"
        )

    bloecke.append(PROMPTS["router.rules"])

    return "\n\n".join(bloecke)


def _decision(state: ConversationState, decision: str, outcome: str, inputs: dict, scale: dict | None = None) -> None:
    """Der Entscheidungs-Eintrag des Empfangs — je Weiche einer, auch beim Uebersprung.

    Nachbedingung: ein `switch` mit `entscheidung`, `ausgang`, `eingang` und
        `massstab` im Pipeline-Log (`memory.pipeline_log.log_decision`). Bis
        zum 18.09.2026 schrieb der Router keinen Eintrag: ob ein Wartezustand
        griff, ob ein Angebot offen war, ob der Riegel eine Zustimmung
        aufhielt, stand nur im Textlog.
    """
    log_decision(
        turn_id      = state.get("turn_id", "unbekannt"),
        node         = "router",
        quelle       = pipeline_quelle(state),
        decision     = decision,
        outcome      = outcome,
        inputs       = inputs,
        scale        = scale,
        user_id      = state.get("user_id", ""),
        character_id = state.get("character_id", ""),
    )


def build_situation_block(sachlage: object, verdict: object, max_objects: int = 5,
                          offer: Offer | None = None) -> str:
    """Der [LAGE]-Block des Routers: akute Objekte, ihr Bekanntes, ihre Dienste.

    **Der Satz, der eine Zustimmung zum Auftrag macht, steht nur bei offenem
    Angebot** (`offer`). Ohne Angebot fehlt der Bezug: Ein *"Gerne"* antwortet
    dann auf irgendetwas, und die Kette schriebe auf ein Wort hin. `[gemessen
    17.09.2026, Betrieb]` Zwei Dialoge, in denen Nova nach einer Nebensache
    fragte und das folgende *"Gerne"* den Termin anlegte — 2 von 2.

    Vorbedingung: keine — eine fehlende Sachlage oder ein fehlendes Urteil ist
        ein gueltiger Fall.
    Nachbedingung: leer, wenn es kein akutes Objekt gibt; sonst der Block aus
        `router.lage` mit je einer Zeile: Name, Klasse, gedeckte Eigenschaften
        mit Wert, und — wo das Urteil sie nennt — die Dienste, an deren Zettel
        das Objekt steht. Ein Objekt ohne Dienst steht ohne Dienst da, nicht mit
        einer Verneinung: Die Naehe schweigt oft, und Schweigen ist kein Nein.
        Hoechstens `max_objects` Objekte, in der Reihenfolge der Sachlage.
    Fehlerfaelle: keine Ausnahme; ein unlesbares Objekt wird laut uebergangen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(sachlage, dict) or not isinstance(sachlage.get("objekte"), list):
        return ""
    herkuenfte = {sachlage.get("herkunft"), verdict.get("herkunft") if isinstance(verdict, dict) else None}
    if "ausfall_uebernommen" in herkuenfte:
        # Dieselbe Regel wie im Planner: nach einem Ausfall sind es die Objekte
        # des Vorturns, und ein "Gerne" bezoege sich auf die falsche Sache.
        # Gelesen an BEIDEN Stellen — faellt auch die Naehe aus, traegt ihr
        # Eintrag keine Herkunft (zweite Kontrolle, 17.09.2026).
        return ""
    akute: list[dict] = [o for o in sachlage["objekte"] if isinstance(o, dict) and o.get("akut") is True]
    if not akute:
        return ""
    empfaenger: dict[str, list[str]] = {}
    if isinstance(verdict, dict) and verdict.get("ergebnis") == "gerechnet":
        for eintrag in verdict.get("objekte") or []:
            if isinstance(eintrag, dict) and eintrag.get("empfaenger"):
                empfaenger[str(eintrag.get("name") or "")] = list(eintrag["empfaenger"])

    # ── Verarbeitung ────────────────────────────
    zeilen: list[str] = []
    for objekt in akute[:max_objects]:
        name: str = str(objekt.get("name") or "").strip()
        if not name:
            logger.warning("Router: akutes Objekt ohne Namen im [LAGE]-Block uebergangen")
            continue
        teile: list[str] = [f"- {name}" + (f" ({objekt['klasse']})" if objekt.get("klasse") else "")]
        gedeckt = objekt.get("gedeckt") if isinstance(objekt.get("gedeckt"), dict) else {}
        if gedeckt:
            teile.append("bekannt: " + "; ".join(f"{k}: {v}" for k, v in gedeckt.items()))
        if empfaenger.get(name):
            teile.append("am Aushang: " + ", ".join(empfaenger[name]))
        zeilen.append(" — ".join(teile))

    # ── Ausgabe-Verifikation ────────────────────
    if not zeilen:
        return ""
    block: str = PROMPTS["router.lage"].format(objekte="\n".join(zeilen))
    namen: list[str] = [str(o.get("name") or "").strip() for o in akute[:max_objects]]
    if offer_matches(offer, namen):
        block += "\n\n" + PROMPTS["router.lage.angebot"].format(angebot=offer.sentence[:200])
    return block


def route(
    state: ConversationState,
) -> ConversationState:
    """Entscheidet ueber Ressourcen-Routing basierend auf Perzeption-Ergebnissen.

    Geroutet wird der Reiz dieses Durchlaufs, nicht der Reiz-Platz: Auf einem
    Impuls-Turn steht dort nichts, und ein Router ohne Text entscheidet ueber
    Gedaechtnis, Web und Zeitachse auf einer leeren Zeichenkette.
    """
    # Der Nenner des Quotenabgleichs: eine Aeusserung, die den Empfang
    # erreicht hat. Je Graph getrennt, weil die Impulsrate des
    # Hintergrunds keinem Fachdienst gehoert — ein gemeinsamer Nenner
    # schwankt, sobald jemand den Takt aendert.
    REGISTER.turn_zaehlen(
        "pixie" if state.get("graph_rolle") == "pixie" else "user"
    )

    reiz: str = reiz_text(state)
    logger.info(f"Router: Route Prompt ({len(reiz)} Zeichen)")

    # Scheibe 12 C2/D1: die Naehe der akuten Objekte zu den Objekt-Merkmalen der
    # Dienste. Das Urteil reist als `objekt_urteil` zum Planner, der daraus die
    # Reihenfolge der Dienste bildet; OB zugestellt wird, entscheidet weiter der
    # Aufruf unten (die Bitte). Vor dem Resume-Pfad, damit jeder Durchlauf einen
    # Eintrag hat.
    state["objekt_urteil"] = shadow_nearness(state)

    # Scheibe 12 E1: das offene Angebot des Vorturns. Es entscheidet, ob der
    # Zustimmungssatz im [LAGE]-Block steht — und der Riegel am Ende dieses
    # Knotens haengt an derselben Zahl.
    angebot: Offer | None = offer_load(
        redis_client, state.get("user_id", ""), state.get("character_id", ""),
    )
    angebot_offen: bool = angebot is not None
    # Nimmt der Mensch dieses Angebot gerade an, reisen SEINE Sachen zum Dienst
    # (E1c) — nicht alle akuten. Sonst waehlt die Fachabteilung bei mehreren
    # Objekten selbst, und im Betrieb fand sie dann kein Datum (17.09.2026).
    nimmt_an: bool = angebot_offen and is_bare_consent(reiz)
    state["angebot_objekte"] = list(angebot.objects) if nimmt_an else []
    state["angebot_bezug"] = [dict(d) for d in angebot.details] if nimmt_an else []
    # Der Satz selbst reist mit: Die Fachabteilung soll lesen, WORAUF der
    # Mensch zugestimmt hat — der Verlauf kann inzwischen anderes fuehren.
    state["angebot_satz"] = angebot.sentence if nimmt_an else ""

    # ── Pending Agent Check (Resume-Flow) ──────────
    # Wenn ein Agent auf Antwort wartet, ueberspringen wir den LLM-Call.
    # Die User-Antwort geht direkt als Resume an den wartenden Agent.
    from tools.redis_manager import redis_manager

    user_id = state.get("user_id", "")
    pending_key = f"pending_agent:{user_id}"
    pending = redis_manager.get_json(pending_key)

    if pending and carries_own_request(reiz):
        # **Eine Rueckfrage ordnet heute rein ueber die Zeit zu** — jede
        # Aeusserung binnen 300 s galt als Antwort. `[gemessen 17.09.2026,
        # Betrieb]` Die Rueckfrage der Notizen verschluckte so einen eigenen
        # Auftrag an die Timeline und meldete `abgeschlossen`, ohne zu
        # schreiben. Traegt der Turn seinen eigenen Auftrag, ist er keine
        # Antwort: Der Wartezustand faellt, der Turn wird normal geroutet.
        logger.info(
            "Router: Turn traegt einen eigenen Auftrag — die offene Rueckfrage "
            f"von '{pending.get('agent_name', '?')}' wird verworfen"
        )
        redis_manager.delete(pending_key)
        _decision(state, "router.rueckfrage", "verworfen_eigener_auftrag",
                  {"wartender_dienst": pending.get("agent_name", "")})
        pending = None

    if pending and reiz_ist_eigener_gedanke(state):
        # **Ein eigener Gedanke beantwortet keine Frage, die dem Menschen
        # gestellt wurde.** Der Wartezustand wird im Resume-Pfad geloescht,
        # bevor der Agent laeuft — ein Impuls, der dort hineinlaeuft, nimmt
        # dem Menschen also die Gelegenheit zu antworten, und der Agent
        # arbeitet mit etwas, das niemand gesagt hat.
        #
        # Handeln darf sie; an seiner Stelle antworten nicht. Das ist die
        # Grenze der Entscheidung vom 14.08.2026, und sie laesst sich nicht
        # ueber den Zeitpunkt der Zustellung sichern: Auch ein Retry oder ein
        # Selbstausloeser traegt dieselbe Herkunft.
        logger.info(
            "Router: Pending Agent '%s' bleibt stehen — der Reiz ist ein "
            "eigener Gedanke und beantwortet keine Rueckfrage",
            pending.get("agent_name", ""),
        )
        _decision(state, "router.rueckfrage", "bleibt_stehen_impuls",
                  {"wartender_dienst": pending.get("agent_name", "")})
    elif pending:
        agent_name = pending.get("agent_name", "")
        logger.info(f"Router: Pending Agent erkannt — '{agent_name}', Resume-Flow aktiviert")
        state["management_action"] = "resume"
        state["management_target"] = ""
        state["needs_memory"]      = True
        state["needs_web"]         = False
        state["needs_timeline"]    = False
        state["timeline_query"]    = {}
        state["momentum"]          = "mid"
        _decision(state, "router.rueckfrage", f"resume:{agent_name}", {"wartender_dienst": agent_name})
        return state

    # ── Session-Kontext laden (leichtgewichtig, Redis-Read) ──
    character_id: str = state.get("character_id", "")
    session_turns: str | None = None
    if user_id:
        try:
            raw_turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)
            session_turns = format_session_turns_numbered(raw_turns, max_turns=5) or None
            if session_turns:
                logger.info("Router: Session-Kontext geladen (nummeriert)")
        except Exception as e:
            logger.warning(f"Router: Session-Kontext konnte nicht geladen werden: {e}")

    system_prompt: str = _build_router_prompt(state, session_turns, offer=angebot)

    logger.info(f"Router: System-Prompt:\n{system_prompt}")

    node_cfg = get_node_config("router")

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 3) ──
    # route() laeuft im FastAPI-Threadpool (api/chat.py:chat_senden ist eine
    # sync def). Kein Event-Loop im aufrufenden Thread → submit_sync nutzt
    # die Bruecke ueber asyncio.run_coroutine_threadsafe in den Haupt-Loop
    # des Workers (Loop-Binding-Lesson, novaberg-lesson_l_loop-binding.md).
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": reiz}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "router",
    )

    try:
        response = model_service.chat.submit_sync(chat_request)
        logger.debug(f"Router RAW: '{response.text[:500]}'")
        routing: dict = response.parsed

        state["needs_memory"]   = routing.get("needs_memory", False)
        state["needs_web"]      = routing.get("needs_web", False)
        state["needs_timeline"] = routing.get("needs_timeline", False)
        state["timeline_query"] = routing.get("timeline_query") or {}
        state["momentum"]       = routing.get("momentum", "mid")

        # Management-Felder
        state["management_action"]     = routing.get("management_action", "") or ""
        state["management_target"]     = routing.get("management_target", "") or ""
        state["management_target_typ"] = routing.get("management_target_typ", "titel") or "titel"

    except (json.JSONDecodeError, KeyError) as fehler:
        logger.warning(f"Router: JSON-Parsing fehlgeschlagen ({fehler}), Fallback")
        state["needs_memory"]          = False
        state["needs_web"]             = False
        state["needs_timeline"]        = False
        state["timeline_query"]        = {}
        state["momentum"]              = "mid"
        state["management_action"]     = ""
        state["management_target"]     = ""
        state["management_target_typ"] = "titel"

    # Riegel (Scheibe 12 E1): Eine blanke Zustimmung ohne offenes Angebot
    # stellt nicht zu. Der Block oben nennt den Zustimmungssatz nur bei
    # offenem Angebot; dieser Riegel ist der deterministische Teil derselben
    # Regel — er haengt nicht daran, dass das Modell dem Prompt folgt.
    # Er greift NUR bei einer Aeusserung, die nichts weiter sagt als "ja":
    # Ein eigener Auftrag traegt seine Sache selbst und geht durch.
    vom_modell: str = f"{state['management_action']}/{state['management_target']}"
    riegel: bool = bool(state["management_action"]) and is_bare_consent(reiz) and not angebot_offen
    if riegel:
        logger.info(
            "Router: blanke Zustimmung ohne offenes Angebot — keine Zustellung "
            f"(war: {state['management_action']}/{state['management_target']})"
        )
        state["management_action"]     = ""
        state["management_target"]     = ""
        state["management_target_typ"] = "titel"

    # Guard: Management-Intent ueberschreibt Low-Momentum
    if state["management_action"] and state["momentum"] == "low":
        state["momentum"] = "mid"
        logger.info("Router: Momentum low->mid korrigiert (Management-Intent aktiv)")

    _decision(
        state, "router.zustellung",
        f"{state['management_action']}/{state['management_target']}" if state["management_action"] else "keine",
        {"vom_modell": vom_modell, "angebot_offen": angebot_offen,
         "blanke_zustimmung": is_bare_consent(reiz), "riegel_gegriffen": riegel,
         "momentum": state["momentum"]},
        {"regel": "zustimmung_nur_bei_offenem_angebot"},
    )

    logger.info(
        f"Router: memory={state['needs_memory']}, web={state['needs_web']}, "
        f"timeline={state['needs_timeline']}, momentum={state['momentum']}, "
        f"mgmt={state['management_action']}/{state['management_target']}"
    )

    return state
