"""Die Ausführung der Schreibaufträge an den FactsAgent — gerufen vom Dispatcher.

Der Dienst ist passiv: Seinen Auftrag stellt die Sachlage in jedem gerechneten
Turn mit Verlaufszeile aus (`graph.nodes.sachlage.build_fact_order`), und der
Dispatcher führt ihn nach der Antwort aus. Router und Planner sind nicht
beteiligt.

**Die Funktion heißt nicht `dispatch_fakten`:** `discover_agents` trägt jede
Funktion `dispatch_<ordner>` als Dispatch des Planners ein, und der Dienst wäre
wieder über den Empfang erreichbar.

Je Auftrag liest der Agent die Kandidaten des Turns. Trägt er Kandidaten des
Menschen, geht **ein** Modellaufruf hinaus (`klassifikation.classify_candidates`)
— mit der Äußerung des Turns und nur diesen Kandidaten; jedes Tripel der
Antwort wird geprüft (`vet_triple`) und läuft einzeln durch den Graphen des
Agenten (`FactsAgent`). Kandidaten anderer Sprecher gehen nicht ins Modell.

Jeder Auftrag hat genau einen Ausgang (`OUTCOMES`) und genau einen Eintrag
`log_db_write`; jedes Tripel darin einen eigenen (`TRIPLE_OUTCOMES`). Ein
Ausfall des Modells ist ein eigener Ausgang, nie *kein Tripel*.
"""

import logging
from collections import Counter

from agents.fakten.agent import FactsAgent
from agents.fakten.klassifikation import (
    SPEAKER_ORIGIN,
    AnswerFormError,
    ModelCallError,
    Verdict,
    classify_candidates,
    link_event,
    vet_triple,
)
from agents.fakten.suche import binding_for
from graph.reiz import reiz_text
from memory.pipeline_log import log_db_write
from memory.sachlage_properties import turn_candidates

logger = logging.getLogger("ki_server.agents.fakten.dispatch")

OUTCOME_EMPTY:          str = "leer"
OUTCOME_NOT_STORED:     str = "ausgefallen"
OUTCOME_ERROR:          str = "fehler"
OUTCOME_REJECTED:       str = "verworfen"
OUTCOME_OTHER_SPEAKERS: str = "nur_andere_sprecher"
OUTCOME_MODEL_FAILED:   str = "modell_ausfall"
OUTCOME_ANSWER_BROKEN:  str = "antwort_defekt"
OUTCOME_NO_TRIPLE:      str = "kein_tripel"
OUTCOME_CLASSIFIED:     str = "klassifiziert"
NO_SPEAKER:             str = "ohne"
OUTCOMES: frozenset[str] = frozenset({
    OUTCOME_EMPTY, OUTCOME_NOT_STORED, OUTCOME_ERROR, OUTCOME_REJECTED, OUTCOME_OTHER_SPEAKERS,
    OUTCOME_MODEL_FAILED, OUTCOME_ANSWER_BROKEN, OUTCOME_NO_TRIPLE, OUTCOME_CLASSIFIED,
})

# Die Ausgänge je Tripel; dazu `verworfen:<grund>` mit einem Grund aus
# `klassifikation.REJECT_REASONS`.
TRIPLE_CREATED:   str = "angelegt"
TRIPLE_REPLACED:  str = "abgeloest"
TRIPLE_SAME:      str = "identisch"
TRIPLE_AMBIGUOUS: str = "mehrdeutig"
TRIPLE_ERROR:     str = "fehler"
TRIPLE_REJECTED:  str = "verworfen"
TRIPLE_OUTCOMES: frozenset[str] = frozenset({
    TRIPLE_CREATED, TRIPLE_REPLACED, TRIPLE_SAME, TRIPLE_AMBIGUOUS, TRIPLE_ERROR,
})

# Die Maengel eines Auftrags (`_order_defect`), eine geschlossene Menge.
DEFECT_NO_DATA:         str = "daten fehlen"
DEFECT_NO_TURN:         str = "turn_id fehlt"
DEFECT_NO_STORING:      str = "Ausgang des Ablegens fehlt"
DEFECT_NO_HISTORY:      str = "verlauf_id fehlt"
ORDER_DEFECTS: frozenset[str] = frozenset({
    DEFECT_NO_DATA, DEFECT_NO_TURN, DEFECT_NO_STORING, DEFECT_NO_HISTORY,
})


def _speaker_counts(candidates: list[dict]) -> dict[str, int]:
    """Die Zahl der Kandidaten je Sprecher.

    Vorbedingung: `candidates` sind Zeilen aus `turn_candidates`.
    Nachbedingung: je Sprecher eine Zahl; ein fehlender Sprecher zählt unter
        `ohne`, damit die Summe gleich der Zahl der Kandidaten bleibt.
    Fehlerfälle: keine — eine Summe, die nicht aufgeht, ist ein Defekt und wirft.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(candidates, list):
        raise TypeError(f"Kandidaten keine Liste: {type(candidates).__name__}")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    counts: Counter[str] = Counter(
        str(zeile.get("sprecher") or NO_SPEAKER) for zeile in candidates
    )

    # ── Ausgabe-Verifikation ────────────────────
    if sum(counts.values()) != len(candidates):
        raise ValueError("Zählung je Sprecher geht nicht auf")  # noqa: TRY003
    return dict(counts)


def _order_defect(daten: object) -> str:
    """Was an einem Auftrag fehlt — leer, wenn er vollständig ist.

    Vorbedingung: keine; `daten` ist, was im Auftrag unter `daten` steht.
    Nachbedingung: ein Text aus `ORDER_DEFECTS`, der den ersten Mangel nennt,
        oder "".
    Fehlerfälle: ein Mangel außerhalb von `ORDER_DEFECTS` ist ein Defekt
        dieser Funktion und wirft ValueError.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(daten, dict):
        return DEFECT_NO_DATA

    # ── Verarbeitung ────────────────────────────
    turn_id:    object = daten.get("turn_id")
    verlauf_id: object = daten.get("verlauf_id")
    defects: list[str] = [
        mangel for mangel, fehlt in (
            (DEFECT_NO_TURN, not isinstance(turn_id, str) or not turn_id),
            (DEFECT_NO_STORING, not isinstance(daten.get("abgelegt"), bool)),
            (DEFECT_NO_HISTORY, not isinstance(verlauf_id, int) or isinstance(verlauf_id, bool)),
        ) if fehlt
    ]
    defect: str = defects[0] if defects else ""

    # ── Ausgabe-Verifikation ────────────────────
    if defect and defect not in ORDER_DEFECTS:
        raise ValueError(f"Fakten-Auftrag: unbekannter Mangel {defect!r}")  # noqa: TRY003
    return defect


def _record(state: dict, daten: dict, outcome: dict) -> None:
    """Der eine Eintrag `log_db_write` je Auftrag (Knoten dispatcher, Quelle fakten).

    Vorbedingung: `outcome` trägt `ausgang`, `kandidaten`, `je_sprecher`.
    Nachbedingung: ein Eintrag mit Ausgang, Zahlen, den Tripeln mit ihren
        Ausgängen und der Salienz aus dem Auftrag (sie reist mit und ist kein
        Tor); auch ohne Tripel steht der Eintrag — sonst wäre ein Turn ohne
        Kandidaten von einem ohne Auftrag nicht zu unterscheiden.
    Fehlerfälle: ein Ausgang außerhalb von `OUTCOMES` wirft ValueError. Ein
        Eintrag, der nicht zählbar ist — ohne turn_id, oder Zahl und Zählung
        je Sprecher gehen nicht auf —, steht trotzdem und wird mit
        `logger.error` gemeldet: Die Zählung gegen die Verlaufszeilen hätte
        sonst eine stille Lücke.
    """
    # ── Eingabe-Validierung ─────────────────────
    if outcome.get("ausgang") not in OUTCOMES:
        raise ValueError(  # noqa: TRY003
            f"Fakten-Auftrag: Eintrag mit unbekanntem Ausgang {outcome.get('ausgang')!r}"
        )

    # ── Verarbeitung ────────────────────────────
    turn_id: str = state.get("turn_id", "unbekannt")
    log_db_write(
        turn_id      = turn_id,
        node         = "dispatcher",
        quelle       = "fakten",
        inhalt       = {
            **outcome,
            "verlauf_id":       daten.get("verlauf_id"),
            "salienz_human":    daten.get("salienz_human"),
            "user_intentionen": daten.get("user_intentionen"),
        },
        user_id      = state.get("user_id", ""),
        character_id = state.get("character_id", ""),
    )

    # ── Ausgabe-Verifikation ────────────────────
    total:  object = outcome.get("kandidaten")
    counts: object = outcome.get("je_sprecher")
    sums_up: bool = (total is None and counts is None) or (
        isinstance(total, int) and isinstance(counts, dict) and sum(counts.values()) == total
    )
    if not turn_id or turn_id == "unbekannt" or not sums_up:
        logger.error(
            f"Fakten-Auftrag: Eintrag nicht zählbar — turn={turn_id!r}, "
            f"Ausgang {outcome['ausgang']}, kandidaten={total!r}, je_sprecher={counts!r}"
        )
        return
    logger.info(f"Fakten-Auftrag: Ausgang {outcome['ausgang']}, {total} Kandidaten {counts}")


def _write_triple(state: dict, triple: dict, candidate: dict, utterance: str) -> str:
    """Schreibt ein geprüftes Tripel über den Graphen des Agenten.

    Vorbedingung: `triple` kommt aus `vet_triple` (mit `herkunft`);
        `candidate` ist der Kandidat, auf den seine Nummer zeigt; `state`
        trägt das Paar.
    Nachbedingung: ein Ausgang aus `TRIPLE_OUTCOMES` — die Art der
        Schreibung (`angelegt`, `abgeloest`, `identisch`) nur nach dem
        verifizierten `abgeschlossen` des Graphen.
    Fehlerfälle: Ein `fehler` des Graphen und ein Endstatus, den er nicht
        setzen darf, ergeben `fehler` mit `logger.error`; eine Art der
        Schreibung außerhalb der drei ebenso. Ein Tripel ohne Herkunft aus
        `SPEAKER_ORIGIN` wirft ValueError — es kam nicht aus `vet_triple`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if triple.get("herkunft") not in SPEAKER_ORIGIN.values():
        raise ValueError(f"Fakten-Auftrag: Tripel ohne Herkunft {triple!r:.120}")  # noqa: TRY003
    gebunden: int | None = binding_for(triple["subjekt"], candidate)

    # ── Verarbeitung ────────────────────────────
    aus: dict = FactsAgent().invoke({
        "aufgabe": utterance, "aufgabe_typ": "workflow", "agent_name": "fakten",
        "kontext": {"user_id": state["user_id"], "character_id": state["character_id"]},
        "parameter": {**triple, "subjekt_entitaet_id": gebunden},
        "schritte": [], "ergebnis": None, "status": "laufend",
        "rueckfrage": None, "fehler": None,
    })
    status: str = aus.get("status", "")
    art: object = (aus.get("parameter") or {}).get("art")

    # ── Ausgabe-Verifikation ────────────────────
    if status == "abgeschlossen" and art in (TRIPLE_CREATED, TRIPLE_REPLACED, TRIPLE_SAME):
        return str(art)
    if status == "mehrdeutig":
        return TRIPLE_AMBIGUOUS
    logger.error("Fakten-Auftrag: Tripel %s %s %s nicht geschrieben — Status %r, Art %r: %s",
                 triple["subjekt"], triple["beziehung"], triple["objekt"], status, art,
                 aus.get("fehler"))
    return TRIPLE_ERROR


def _classify_and_write(state: dict, numbered: dict[int, dict],
                        events: dict[int, int | None]) -> dict:
    """Der Modellaufruf eines Auftrags und das Schreiben seiner Tripel.

    Vorbedingung: `numbered` sind **alle** Kandidaten des Turns, nummeriert ab
        1 in der Reihenfolge von `turn_candidates`, mindestens einer davon
        vom Menschen (`SPEAKER_ORIGIN`). `events` bildet die Nummer eines
        Kandidaten auf die Timeline-Zeile seines Ereignisses ab (None:
        gescheitert); ein Tripel darauf trägt `timeline_id` (`link_event`).
    Nachbedingung: ein Teil des Ausgangs — `ausgang` aus `modell_ausfall`,
        `antwort_defekt`, `kein_tripel` oder `klassifiziert`; bei einer
        Antwort dazu `dauerhaft`, `grund`, `tripel_zahl` und `tripel` (je
        Tripel `kandidat`, `subjekt`, `beziehung`, `objekt`, `ausgang`, bei
        einer Verwerfung `detail`). Ins Modell gehen nur die Kandidaten des
        Menschen.
    Fehlerfälle: ValueError bei leerer Äußerung — der Aufrufer trägt sie als
        `fehler` ein. Eine Ausnahme beim Schreiben eines Tripels ergibt für
        dieses Tripel `fehler` mit `logger.exception`; die übrigen laufen weiter.
    """
    # ── Eingabe-Validierung ─────────────────────
    utterance: str = reiz_text(state)
    if not utterance.strip():
        raise ValueError("Fakten-Auftrag: Kandidaten des Menschen, aber keine Äußerung")  # noqa: TRY003
    human: dict[int, dict] = {
        nummer: k for nummer, k in numbered.items() if k["sprecher"] in SPEAKER_ORIGIN
    }

    # ── Verarbeitung ────────────────────────────
    try:
        antwort: dict = classify_candidates(utterance, human, events)
    except ModelCallError as fehler:
        logger.exception("Fakten-Auftrag: Modell ausgefallen")
        return {"ausgang": OUTCOME_MODEL_FAILED, "fehler": str(fehler)}
    except AnswerFormError as fehler:
        logger.exception("Fakten-Auftrag: Antwort des Modells defekt")
        return {"ausgang": OUTCOME_ANSWER_BROKEN, "fehler": str(fehler)}
    tripel: list[dict] = []
    for roh in antwort["tripel"]:
        urteil: Verdict = link_event(
            vet_triple(roh, numbered, utterance, antwort["dauerhaft"]), events,
        )
        zeile: dict = {k: roh.get(k) for k in ("kandidat", "subjekt", "beziehung", "objekt")} \
            if isinstance(roh, dict) else {"roh": repr(roh)[:200]}
        if urteil.tripel is None:
            tripel.append({**zeile, "ausgang": f"{TRIPLE_REJECTED}:{urteil.grund}",
                           "detail": urteil.detail})
            continue
        try:
            ausgang: str = _write_triple(state, urteil.tripel, numbered[urteil.tripel["kandidat"]],
                                         utterance)
        except Exception:
            logger.exception("Fakten-Auftrag: Tripel %r nicht geschrieben", urteil.tripel)
            ausgang = TRIPLE_ERROR
        # Ein Tripel auf ein eingetragenes Ereignis nennt dessen Zeile im Eintrag.
        verweis: dict = {k: v for k, v in urteil.tripel.items() if k == "timeline_id"}
        tripel.append({**zeile, **{k: urteil.tripel[k] for k in ("subjekt", "beziehung", "objekt")},
                       **verweis, "ausgang": ausgang})

    # ── Ausgabe-Verifikation ────────────────────
    if len(tripel) != len(antwort["tripel"]):
        raise ValueError("Fakten-Auftrag: nicht jedes Tripel hat einen Ausgang")  # noqa: TRY003
    fremd: list[str] = [
        t["ausgang"] for t in tripel if t["ausgang"] not in TRIPLE_OUTCOMES
        and not t["ausgang"].startswith(f"{TRIPLE_REJECTED}:")
    ]
    if fremd:
        raise ValueError(f"Fakten-Auftrag: Tripel mit unbekanntem Ausgang {fremd}")  # noqa: TRY003
    return {
        "ausgang":     OUTCOME_CLASSIFIED if tripel else OUTCOME_NO_TRIPLE,
        "dauerhaft":   antwort["dauerhaft"],
        "grund":       antwort["grund"],
        "tripel_zahl": len(tripel),
        "tripel":      tripel,
    }


def _events_of(daten: dict, numbered: dict[int, dict]) -> dict[int, int | None]:
    """Die Abbildung Kandidat → Timeline-Zeile, die der Dispatcher in den Auftrag legte.

    Vorbedingung: `numbered` sind die Kandidaten des Turns unter ihrer Nummer.
    Nachbedingung: die Einträge unter `daten["ereignisse"]`, deren Nummer im
        Turn steht und deren Zeile eine positive ganze Zahl oder None ist;
        leer, wenn der Auftrag keine trägt (kein Ereignis-Auftrag im Turn).
    Fehlerfälle: Ein Eintrag, der das verfehlt, fällt mit `logger.error`
        heraus — sein Kandidat wird behandelt wie einer ohne Ereignis (P4).
    """
    # ── Eingabe-Validierung ─────────────────────
    roh: object = daten.get("ereignisse")
    if roh is None:
        return {}
    if not isinstance(roh, dict):
        logger.error(f"Fakten-Auftrag: ereignisse kein dict: {roh!r:.200}")
        return {}

    # ── Verarbeitung ────────────────────────────
    events: dict[int, int | None] = {
        k: v for k, v in roh.items()
        if k in numbered and (v is None or (isinstance(v, int) and not isinstance(v, bool)
                                            and v > 0))
    }

    # ── Ausgabe-Verifikation ────────────────────
    if len(events) != len(roh):
        logger.error(f"Fakten-Auftrag: Ereignisse ausserhalb des Turns verworfen: {roh!r:.200}")
    return events


def _run_one(state: dict, daten: dict, postgres_url: str) -> dict:
    """Führt einen vollständigen Auftrag aus und gibt seinen Ausgang zurück.

    Vorbedingung: `_order_defect(daten)` ist leer; `state` trägt das Paar.
    Nachbedingung: Ausgang `ausgefallen` (das Ablegen fiel aus, nichts wird
        gelesen), `leer`, `nur_andere_sprecher` (kein Kandidat des Menschen,
        kein Modellaufruf) oder einer aus `_classify_and_write`; der Eintrag
        ist geschrieben.
    Fehlerfälle: Ein Fehler beim Lesen der Kandidaten wird als Ausgang
        `fehler` eingetragen und weitergeworfen — nie als `leer` gemeldet.
        Eine gelesene Zeile ohne Feld `sprecher` ebenso: Ausgang `fehler`,
        dann ValueError — sie wäre sonst still unter `ohne` gezählt. Ein
        Fehler vor dem Modellaufruf (leere Äußerung, ein Kandidat ohne Feld)
        ebenso: Ausgang `fehler`, dann weitergeworfen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if daten["abgelegt"] is False:
        # Die Kandidaten fehlen, nicht die Aussagen: Was gelesen würde, wäre
        # die Lücke des Ablegens, und sie sähe aus wie ein Turn ohne Neues.
        outcome: dict = {"ausgang": OUTCOME_NOT_STORED, "kandidaten": None, "je_sprecher": None}
        _record(state, daten, outcome)
        return outcome

    # ── Verarbeitung ────────────────────────────
    try:
        candidates: list[dict] = turn_candidates(
            postgres_url, state["user_id"], state["character_id"], daten["turn_id"],
        )
    except Exception as fehler:
        _record(state, daten, {
            "ausgang": OUTCOME_ERROR, "kandidaten": None, "je_sprecher": None,
            "fehler": type(fehler).__name__,
        })
        raise

    # ── Ausgabe-Verifikation ────────────────────
    # Das Gelesene traegt das Feld, nach dem gezaehlt wird: Eine Zeile ohne
    # `sprecher` zaehlte sonst still unter `ohne`.
    broken: int = sum(1 for z in candidates if not isinstance(z, dict) or "sprecher" not in z)
    if broken:
        _record(state, daten, {
            "ausgang": OUTCOME_ERROR, "kandidaten": None, "je_sprecher": None,
            "fehler": f"{broken} Kandidat(en) ohne Feld sprecher",
        })
        raise ValueError(  # noqa: TRY003
            f"Fakten-Auftrag: {broken} von {len(candidates)} Kandidaten ohne Feld sprecher"
        )
    counted: dict = {"kandidaten": len(candidates), "je_sprecher": _speaker_counts(candidates)}
    numbered: dict[int, dict] = dict(enumerate(candidates, start=1))
    events: dict[int, int | None] = _events_of(daten, numbered)
    if not candidates:
        outcome = {"ausgang": OUTCOME_EMPTY, **counted}
    elif not any(k["sprecher"] in SPEAKER_ORIGIN for k in candidates):
        outcome = {"ausgang": OUTCOME_OTHER_SPEAKERS, **counted}
    else:
        try:
            outcome = {**_classify_and_write(state, numbered, events), **counted}
        except Exception as fehler:
            _record(state, daten, {"ausgang": OUTCOME_ERROR, **counted,
                                   "fehler": f"{type(fehler).__name__}: {fehler}"[:300]})
            raise
    _record(state, daten, outcome)
    return outcome


def process_fact_orders(state: dict, writes: list[dict], postgres_url: str) -> list[dict]:
    """Führt die Schreibaufträge an den Fakten-Agenten aus — je Auftrag ein Ausgang.

    Vorbedingung: `writes` sind die `PendingWrite` mit `ziel="fakten"`;
        `state` trägt `user_id`, `character_id` und `turn_id`.
    Nachbedingung: je Auftrag genau ein Ausgang und genau ein Eintrag
        `log_db_write`; nichts geht in `agent_results`, `management_result`
        oder die Antwort.
    Fehlerfälle: Ein unvollständiger Auftrag oder ein Turn ohne Paar wird mit
        `logger.error` als `verworfen` eingetragen. Ein Fehler beim Lesen oder
        vor dem Modellaufruf wirft (nach seinem Eintrag) — der Dispatcher
        meldet ihn und schließt ab. Ein Ausfall des Modells wirft nicht; er
        ist der Ausgang `modell_ausfall` oder `antwort_defekt`.
        Ein Auftrag ohne Ausgang oder ein Ausgang außerhalb von `OUTCOMES`
        wirft ValueError.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(writes, list):
        raise TypeError(f"Fakten-Aufträge keine Liste: {type(writes).__name__}")  # noqa: TRY003
    pair_missing: bool = not state.get("user_id") or not state.get("character_id")

    # ── Verarbeitung ────────────────────────────
    outcomes: list[dict] = []
    for write in writes:
        daten: object = write.get("daten") if isinstance(write, dict) else None
        defect: str = "Paar fehlt im Turn" if pair_missing else _order_defect(daten)
        if defect:
            logger.error(f"Fakten-Auftrag verworfen: {defect} — {write!r:.200}")
            outcome: dict = {
                "ausgang": OUTCOME_REJECTED, "kandidaten": None, "je_sprecher": None,
                "mangel": defect,
            }
            _record(state, daten if isinstance(daten, dict) else {}, outcome)
            outcomes.append(outcome)
            continue
        outcomes.append(_run_one(state, daten, postgres_url))

    # ── Ausgabe-Verifikation ────────────────────
    if len(outcomes) != len(writes):
        raise ValueError("Nicht jeder Fakten-Auftrag hat einen Ausgang")  # noqa: TRY003
    unknown: list[object] = [o.get("ausgang") for o in outcomes if o.get("ausgang") not in OUTCOMES]
    if unknown:
        raise ValueError(f"Fakten-Aufträge mit unbekanntem Ausgang: {unknown}")  # noqa: TRY003
    return outcomes
