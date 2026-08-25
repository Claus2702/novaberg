"""Dispatch fuer KzgAgent — Salienz-Ergebnis -> AgentState -> Batch-Verarbeitung.

Wird vom Dispatcher aufgerufen (nicht vom Planner wie NotizenAgent).
Verarbeitet alle KZG-Writes als Batch. Annotiert den Session-Turn
einmalig fuer das Segment mit der hoechsten Salienz.
"""

import logging

from agents import AgentRegistry
from agents.base import AgentState
from config import ASSISTANT_USER_ID
from config import redis_client as cfg_redis_client
from graph.reiz import reiz_text

logger = logging.getLogger("ki_server.agents.kzg.dispatch")


def abgelehnte_ausgaenge(state: dict) -> list[dict]:
    """Die Dienste, die in diesem Turn abgelehnt haben, mit ihrem Befund.

    **Warum das ueberhaupt hier steht.** Der Verdichter sieht bisher `reiz` und
    `response` — den Text der Aeusserung und den Text der Antwort. Was in dem
    Turn tatsaechlich *geschah*, sieht er nicht. Behauptet die Antwort eine
    Handlung, die ein Dienst abgelehnt hat, verdichtet er die Behauptung: Am
    18.08.2026 wurde aus einem misslungenen Notizauftrag der Gedaechtnisinhalt
    *„Nova hat notiert, dass der Gasvertrag gekuendigt werden soll"* — und beim
    naechsten Abruf steht er ohne den widersprechenden Nachsatz da
    (`FALSCHE-BESTAETIGUNG-WIRD-ERINNERUNG`).

    **Nur `abgelehnt`, nicht `fehler`.** Eine Ablehnung ist ein Urteil ueber den
    Auftrag und gehoert in den Gedaechtnisinhalt; eine Stoerung geht den
    Betreiber an und haette dort nichts zu suchen (`agents/base.py:158`).

    Vorbedingung: `state` traegt `agent_results` als Liste von `AgentResult`.
    Fehlt der Schluessel, ist die Antwort die leere Liste — kein Turn muss
    Agenten gerufen haben.
    Nachbedingung: je abgelehntem Dienst ein Dict mit `agent` und `befund`.
    Die Reihenfolge ist die der Ergebnisse.
    """
    # ── Eingabe-Validierung ─────────────────────
    ergebnisse: list = state.get("agent_results") or []

    # ── Verarbeitung ────────────────────────────
    ausgaenge: list[dict] = []
    for r in ergebnisse:
        if getattr(r, "status", "") != "abgelehnt":
            continue
        korrektur = getattr(r, "korrektur", None)
        if korrektur is None:
            # `AgentResult.__post_init__` erzwingt die Korrektur bei dieser
            # Lage. Fehlt sie doch, ist das Objekt an der Pruefung vorbei
            # entstanden — laut melden statt einen Ausgang ohne Grund bauen.
            logger.error(
                "KZG-Ausgaenge: '%s' meldet 'abgelehnt' ohne Korrektur — "
                "der Ausgang bleibt aussen vor, der Kern kann die Ablehnung "
                "damit nicht tragen", getattr(r, "agent_name", "?"),
            )
            continue
        ausgaenge.append({
            "agent":  getattr(r, "agent_name", ""),
            "befund": getattr(korrektur, "befund", ""),
        })

    # ── Ausgabe ─────────────────────────────────
    if ausgaenge:
        logger.info(
            "KZG-Ausgaenge: %d Dienst(e) haben abgelehnt — %s",
            len(ausgaenge), ", ".join(a["agent"] for a in ausgaenge),
        )
    return ausgaenge


def dispatch_kzg(
    state: dict,
    writes: list[dict],
) -> dict:
    """Verarbeitet alle KZG-Writes als Batch.

    Fuer jedes Segment: Agent aufrufen (Schwelle -> Verdichtung -> Store).
    Am Ende: Session-Turn einmalig annotieren (hoechste Salienz).

    Args:
        state: ConversationState (fuer user_prompt, response, EI-Felder)
        writes: Liste von pending_writes mit ziel="kzg"

    Returns:
        Dict mit:
          kzg_verarbeitet:      Anzahl verarbeiteter Segmente
          kzg_neue_keys:        Redis-Keys der in diesem Lauf neu angelegten
                                KZG-Eintraege, in Segment-Reihenfolge
          kzg_verstaerkte_keys: Redis-Keys der thematisch verstaerkten
                                Nachbar-Eintraege, ueber alle Segmente
    """
    user_id:      str = state.get("user_id", "")
    character_id: str = state.get("character_id", ASSISTANT_USER_ID)

    # Beobachter: User-Graph (Pfad 1) vs. Character-Graph (Pfad 2).
    # ei_calc_rolle ist "user" im HumanGraph und "character" im CharacterGraph.
    beobachter: str = "assistant" if state.get("ei_calc_rolle") == "character" else "user"

    logger.info(f"KZG-Dispatch: Paar={user_id}:{character_id}, Beobachter={beobachter}")

    agent = AgentRegistry.finden("kzg")

    if not agent:
        logger.error("KzgAgent nicht in Registry gefunden")
        return {
            "kzg_verarbeitet":      0,
            "kzg_neue_keys":        [],
            "kzg_verstaerkte_keys": [],
        }

    hoechste_salienz: float = 0.0
    bestes_ergebnis:  dict  = {}
    bester_kern:      str   = ""
    verarbeitet:      int   = 0

    # Transport der geschriebenen Redis-Keys an den aufrufenden Dispatcher.
    # Der Subgraph kennt sie (speicher.py), der Dispatcher bisher nicht.
    new_keys:         list[str] = []
    reinforced_keys:  list[str] = []

    # Einmal je Batch, nicht je Segment: Der Ausgang gehoert dem Turn.
    ausgaenge: list[dict] = abgelehnte_ausgaenge(state)

    for write_idx, write in enumerate(writes):
        daten:       dict = write.get("daten", {})
        salienz_obj: dict = daten.get("salienz_obj", {})

        if not salienz_obj:
            logger.warning("KZG-Dispatch: salienz_obj fehlt — uebersprungen")
            continue

        # EI-Felder aus Personality-Klassen einfuegen. Assistant-Beobachter
        # liest aus internal (Novas Wahrnehmung der eigenen Antwort), sonst
        # aus external (User-Wahrnehmung). Behebt PFAD2-EMO-MIX strukturell.
        if beobachter == "assistant":
            quelle = state.get("internal")
        else:
            quelle = state.get("external")

        salienz_obj["arousal"]            = quelle.emotion.arousal              if quelle else 0.5
        salienz_obj["emotions_vektor"]    = quelle.emotion.emotions_vector      if quelle else ""
        salienz_obj["sprach_stil"] = quelle.emotion.language_style if quelle else "neutral"
        salienz_obj["beziehungs_dynamik"] = (
            quelle.emotion.relationship_dynamic if quelle else "neutral"
        )
        salienz_obj["tone"] = quelle.emotion.tone if quelle else "sachlich"

        # AgentState bauen
        agent_state: AgentState = {
            "aufgabe":     "kzg_verarbeitung",
            "aufgabe_typ": "workflow",
            "agent_name":  "kzg",
            "kontext": {
                "user_id":      user_id,
                "character_id": character_id,
                "beobachter":   beobachter,
                # Zwei verschiedene Fragen, zwei Felder: `beobachter` sagt, WESSEN
                # Sicht der Eintrag traegt (Subjekt im Verdichtungs-Prompt),
                # `graph_rolle` sagt, WAS verdichtet wird (Reiz oder Reaktion).
                # Fuer HumanGraph und CharacterGraph fallen beide zusammen, fuer
                # den AgentGraph nicht: Novas Sicht auf einen Reiz.
                "graph_rolle":  state.get("graph_rolle", "human"),
                "turn_id":      state.get("turn_id", ""),
                # Clipboard: vom TimelineAgent in diesem Turn gesetzte ID;
                # vom magnete_aufloesen-Node uebernommen statt eigenen
                # Erinnerungs-Anker anzulegen.
                "timeline_id":  state.get("timeline_id"),
            },
            "parameter": {
                "salienz_obj":  salienz_obj,
                # Der Reiz dieses Turns, nicht der Reiz-Platz: Auf einem
                # Impuls-Turn hat niemand gesprochen, und der Gegenstand ist
                # Novas eigener Gedanke. Das Feld heisst deshalb `reiz` und
                # nicht `user_prompt` — ein Name, der auf einem von zwei Wegen
                # falsch ist, verleitet den naechsten Leser zur falschen Frage.
                "reiz":         reiz_text(state),
                "response":     state.get("response", ""),
                # Das Segment, das die Salienz bewertet hat. Der Verdichter
                # zieht es dem Turn-Volltext vor; fehlt es — etwa bei einem
                # pending_write aus dem RechercheAgenten —, faellt er sichtbar
                # auf den Volltext zurueck. Leerstring statt None, damit die
                # Rueckfall-Bedingung eine einzige Form hat.
                "segment":        daten.get("segment", ""),
                "segment_index":  daten.get("segment_index", 0),
                "segment_gesamt": daten.get("segment_gesamt", 0),
                # Was in diesem Turn tatsaechlich geschah, soweit ein Dienst
                # widersprochen hat. Einmal je Batch berechnet und an jedes
                # Segment gereicht: Der Ausgang gehoert dem Turn, nicht dem
                # Segment — und ein Kernsatz aus Segment 2 darf so wenig eine
                # abgelehnte Handlung behaupten wie einer aus Segment 1.
                "agent_ausgaenge": ausgaenge,
            },
            "schritte": [],
            "ergebnis": None,
            "status":     "laufend",
            "rueckfrage": None,
            "fehler":     None,
        }

        # Agent ausfuehren
        result_state = agent.invoke(agent_state)
        verarbeitet += 1

        # ── Geschriebene Keys einsammeln ──
        # speichern() legt kzg_key und verstaerkte_eintraege im parameter-Kanal
        # ab; queues_befuellen fasst den Kanal nicht an, der Wert steht also
        # noch. Fehlt der Key, gibt es zwei Ursachen: regulaere Ablehnung
        # unter der Salienz-Schwelle (status="abgelehnt", speichern() lief
        # nie) oder ein Defekt im Schreibpfad. Nur Letzteres ist laut.
        result_parameter: dict = result_state.get("parameter", {}) or {}
        result_status:    str  = result_state.get("status", "")
        new_key:          str  = result_parameter.get("kzg_key", "")
        reinforced:       list = result_parameter.get("verstaerkte_eintraege", []) or []

        if new_key:
            new_keys.append(new_key)
        elif result_status == "abgelehnt":
            logger.info(
                "KZG-Dispatch: Segment %d/%d unter Salienz-Schwelle abgelehnt, "
                "kein KZG-Eintrag — turn_id=%s",
                write_idx + 1,
                len(writes),
                state.get("turn_id", ""),
            )
        else:
            logger.warning(
                "KZG-Dispatch: kein kzg_key aus Segment %d/%d — turn_id=%s, "
                "status=%s, speicher_status='%s'",
                write_idx + 1,
                len(writes),
                state.get("turn_id", ""),
                result_status,
                result_parameter.get("speicher_status", ""),
            )

        for verstaerkt_eintrag in reinforced:
            verstaerkt_key: str = verstaerkt_eintrag.get("key", "")
            if verstaerkt_key:
                reinforced_keys.append(verstaerkt_key)
            else:
                logger.warning(
                    "KZG-Dispatch: verstaerkter Eintrag ohne key aus Segment %d/%d — "
                    "turn_id=%s",
                    write_idx + 1,
                    len(writes),
                    state.get("turn_id", ""),
                )

        # Hoechste Salienz tracken fuer Session-Annotation
        score: float = salienz_obj.get("salienz", 0.0)
        if score > hoechste_salienz and result_state.get("status") != "abgelehnt":
            hoechste_salienz = score
            bestes_ergebnis  = salienz_obj
            bester_kern      = result_state.get("parameter", {}).get("kern", "")

    # ── Kern in State schreiben (Dispatcher schreibt den Session-Turn komplett) ──
    if bestes_ergebnis and bester_kern:
        state["session_turn_kern"] = bester_kern
        logger.info(f"KZG-Dispatch: Kern in State geschrieben — '{bester_kern[:60]}'")

    logger.info(f"KZG-Dispatch: {verarbeitet} Segmente verarbeitet")

    logger.info(
        "KZG-Dispatch: Keys eingesammelt — turn_id=%s, beobachter=%s, "
        "%d neue Keys, %d verstaerkte Keys",
        state.get("turn_id", ""),
        beobachter,
        len(new_keys),
        len(reinforced_keys),
    )

    return {
        "kzg_verarbeitet":      verarbeitet,
        "kzg_neue_keys":        new_keys,
        "kzg_verstaerkte_keys": reinforced_keys,
    }
