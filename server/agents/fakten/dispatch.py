"""Die Ausführung der Schreibaufträge an den FactsAgent — gerufen vom Dispatcher.

Der Dienst ist passiv: Seinen Auftrag stellt die Sachlage in jedem gerechneten
Turn mit Verlaufszeile aus (`graph.nodes.sachlage.build_fact_order`), und der
Dispatcher führt ihn nach der Antwort aus. Router und Planner sind nicht
beteiligt.

**Die Funktion heißt nicht `dispatch_fakten`:** `discover_agents` trägt jede
Funktion `dispatch_<ordner>` als Dispatch des Planners ein, und der Dienst wäre
wieder über den Empfang erreichbar.

In diesem Bau zählt der Agent seine Kandidaten und protokolliert sie; er ruft
kein Modell und schreibt weder in `fakten` noch in `entitaeten`.
"""

import logging
from collections import Counter

from memory.pipeline_log import log_db_write
from memory.sachlage_properties import turn_candidates

logger = logging.getLogger("ki_server.agents.fakten.dispatch")

OUTCOME_EMPTY:          str = "leer"
OUTCOME_NOT_STORED:     str = "ausgefallen"
OUTCOME_UNCLASSIFIED:   str = "nicht_klassifiziert"
OUTCOME_ERROR:          str = "fehler"
OUTCOME_REJECTED:       str = "verworfen"
NO_SPEAKER:             str = "ohne"
OUTCOMES: frozenset[str] = frozenset({
    OUTCOME_EMPTY, OUTCOME_NOT_STORED, OUTCOME_UNCLASSIFIED, OUTCOME_ERROR, OUTCOME_REJECTED,
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
    Nachbedingung: ein Eintrag mit Ausgang, Zahlen und der Salienz aus dem
        Auftrag; der Agent schreibt nichts, der Eintrag steht trotzdem —
        sonst wäre ein Turn ohne Kandidaten von einem ohne Auftrag nicht zu
        unterscheiden.
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


def _run_one(state: dict, daten: dict, postgres_url: str) -> dict:
    """Führt einen vollständigen Auftrag aus und gibt seinen Ausgang zurück.

    Vorbedingung: `_order_defect(daten)` ist leer; `state` trägt das Paar.
    Nachbedingung: Ausgang `ausgefallen` (das Ablegen fiel aus, nichts wird
        gelesen), `leer` oder `nicht_klassifiziert`; der Eintrag ist geschrieben.
    Fehlerfälle: Ein Fehler beim Lesen der Kandidaten wird als Ausgang
        `fehler` eingetragen und weitergeworfen — nie als `leer` gemeldet.
        Eine gelesene Zeile ohne Feld `sprecher` ebenso: Ausgang `fehler`,
        dann ValueError — sie wäre sonst still unter `ohne` gezählt.
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
    outcome = {
        "ausgang":     OUTCOME_UNCLASSIFIED if candidates else OUTCOME_EMPTY,
        "kandidaten":  len(candidates),
        "je_sprecher": _speaker_counts(candidates),
    }
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
        `logger.error` als `verworfen` eingetragen. Ein Fehler beim Lesen wirft
        (nach seinem Eintrag) — der Dispatcher meldet ihn und schließt ab.
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
