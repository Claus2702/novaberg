"""Das Ereignis einer anderen Person — ohne Auftrag in die Timeline des Paares.

Der Dienst ist passiv wie der Fakten-Agent: Seinen Auftrag stellt die Sachlage
nur über der Grenze der Salienz (`graph.nodes.sachlage.build_event_order`), und
der Dispatcher führt ihn **vor** dem Fakten-Auftrag aus. Router und Planner
sind nicht beteiligt; die Funktion heißt nicht `dispatch_timeline`, sonst trüge
`discover_agents` sie als Dispatch des Planners ein.

Je Auftrag liest der Dienst die Kandidaten des Turns (`turn_candidates`), in
derselben Reihenfolge wie der Fakten-Agent — die Nummer eines Kandidaten ist
auf beiden Seiten dieselbe. Ins Modell gehen nur die Kandidaten des Menschen;
**eine leere Liste heißt kein Ereignis mit Gewicht** (der Prompt ist das Tor).

Je Ereignis: die Zeit aus dem Zeitausdruck — zuerst ein Kalendermonat
(`named_period`, Genauigkeit `month`, der Erste des Monats), sonst ein Tag
(`zeit_parsen_vektor`, `read_time`); ohne Tag oder Monat kein Eintrag. Die
Person über `resolve_by_name`: eindeutig → `entitaet_ids=[id]`, sonst ohne,
der Eintrag entsteht trotzdem. Geschrieben mit dem Paar und dem Typ `ereignis`
aus `memory.timeline_types`, ohne Wiedervorlage und ohne Duplikatprüfung.

Die Rückgabe bildet jede Kandidaten-Nummer eines erkannten Ereignisses auf
seine Timeline-Zeile ab — oder auf None, wenn das Schreiben scheiterte: Dann
schreibt der Fakten-Agent für diesen Kandidaten keinen Fakt (`ereignis_fehlt`).
Jeder Auftrag hat genau einen Eintrag `log_db_write` (Quelle `timeline`).
"""

import logging
from datetime import date, datetime, time, timedelta

from config import PROMPTS, get_node_config
from graph.reiz import reiz_text
from memory.pipeline_log import log_db_write
from memory.repositories.timeline_repository import TimelineRepository
from memory.sachlage_properties import turn_candidates
from memory.services.entity_resolution import EntityResolutionService
from memory.timeline_types import OCCURRENCE_TYPE, EventType, event_type, resubmission_at
from services.model_services import ChatRequest, model_service
from utils.local_time import now_local
from utils.zeitparser import named_period, read_time, zeit_parsen_vektor

logger = logging.getLogger("ki_server.agents.timeline.ereignis")

# Nur die Worte des Menschen werden ein Ereignis.
HUMAN_SPEAKER: str = "nutzer"

# Die Ausgänge eines Auftrags, eine geschlossene Menge.
OUTCOME_REJECTED:       str = "verworfen"
OUTCOME_NOT_STORED:     str = "ausgefallen"
OUTCOME_EMPTY:          str = "leer"
OUTCOME_OTHER_SPEAKERS: str = "nur_andere_sprecher"
OUTCOME_MODEL_FAILED:   str = "modell_ausfall"
OUTCOME_ANSWER_BROKEN:  str = "antwort_defekt"
OUTCOME_NO_EVENT:       str = "kein_ereignis"
OUTCOME_CLASSIFIED:     str = "klassifiziert"
OUTCOME_ERROR:          str = "fehler"
OUTCOMES: frozenset[str] = frozenset({
    OUTCOME_REJECTED, OUTCOME_NOT_STORED, OUTCOME_EMPTY, OUTCOME_OTHER_SPEAKERS,
    OUTCOME_MODEL_FAILED, OUTCOME_ANSWER_BROKEN, OUTCOME_NO_EVENT, OUTCOME_CLASSIFIED,
    OUTCOME_ERROR,
})

# Die Ausgänge je Ereignis.
EVENT_WRITTEN:           str = "eingetragen"
EVENT_NO_TIME:           str = "ohne_zeit"
EVENT_UNKNOWN_CANDIDATE: str = "kandidat_unbekannt"
EVENT_FORM:              str = "form"
EVENT_FAILED:            str = "ereignis_fehlt"
EVENT_OUTCOMES: frozenset[str] = frozenset({
    EVENT_WRITTEN, EVENT_NO_TIME, EVENT_UNKNOWN_CANDIDATE, EVENT_FORM, EVENT_FAILED,
})

# Die Genauigkeiten, die ein Ereignis tragen kann.
PRECISION_MINUTE: str = "minute"
PRECISION_DAY:    str = "day"
PRECISION_MONTH:  str = "month"


class ModelCallError(RuntimeError):
    """Der Modellaufruf ist ausgefallen — nie *kein Ereignis*."""


class AnswerFormError(ValueError):
    """Die Antwort des Modells hat nicht die verlangte Form — nie *kein Ereignis*."""


def build_event_input(utterance: str, human: dict[int, dict]) -> str:
    """Die Nachricht an das Modell: die Äußerung und die nummerierten Kandidaten.

    Vorbedingung: `utterance` nicht leer; `human` nicht leer, die Kandidaten
        des Menschen unter ihrer Nummer aus `turn_candidates`, je mit
        `objekt`, `klasse`, `eigenschaft`, `wert`.
    Nachbedingung: ein Text, der jede Nummer genau einmal als `[n]` trägt.
    Fehlerfälle: ValueError ohne Äußerung oder ohne Kandidaten; KeyError,
        wenn einem Kandidaten ein Feld fehlt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not utterance.strip() or not human:
        raise ValueError("Ereignis: ohne Äußerung oder ohne Kandidaten")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    lines: list[str] = [
        f"[{number}] Objekt: {k['objekt']} (Klasse: {k['klasse']}) | "
        f"Eigenschaft: {k['eigenschaft']} | Wert: {k['wert']}"
        for number, k in sorted(human.items())
    ]
    text: str = (
        f"AEUSSERUNG DES MENSCHEN:\n{utterance.strip()}\n\n"
        "KANDIDATEN (was aus dieser Aeusserung abgelegt wurde):\n" + "\n".join(lines)
    )

    # ── Ausgabe-Verifikation ────────────────────
    if any(text.count(f"[{number}] Objekt:") != 1 for number in human):
        raise RuntimeError("Ereignis: Nummer eines Kandidaten nicht eindeutig")  # noqa: TRY003
    return text


def parse_event_answer(answer: object) -> list[object]:
    """Die Liste der Ereignisse aus der Antwort des Modells — ungeprüft je Eintrag.

    Vorbedingung: keine; `answer` ist, was das Modell als JSON lieferte.
    Nachbedingung: die Liste unter `ereignisse`, leer erlaubt (kein Ereignis).
    Fehlerfälle: AnswerFormError, wenn die Antwort kein Objekt ist oder
        `ereignisse` fehlt oder keine Liste ist — ein Ausfall sieht nie aus
        wie *kein Ereignis*.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(answer, dict):
        raise AnswerFormError(f"Antwort kein Objekt: {answer!r:.200}")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    events: object = answer.get("ereignisse")

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(events, list):
        raise AnswerFormError(f"Antwort ohne Liste ereignisse: {answer!r:.200}")  # noqa: TRY003
    return events


def classify_events(utterance: str, human: dict[int, dict]) -> list[object]:
    """Der eine Modellaufruf eines Auftrags: 0…n Ereignisse einer anderen Person.

    Vorbedingung: wie `build_event_input`.
    Nachbedingung: die Ereignisse, wie das Modell sie nennt (`parse_event_answer`).
    Fehlerfälle: ModelCallError, wenn der Aufruf wirft; AnswerFormError aus
        `parse_event_answer`.
    """
    # ── Eingabe-Validierung ─────────────────────
    message: str = build_event_input(utterance, human)

    # ── Verarbeitung ────────────────────────────
    node_cfg: dict = get_node_config("router")
    request = ChatRequest(
        messages          = [{"role": "user", "content": message}],
        system            = PROMPTS["classify_ereignis.task"],
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "agent/timeline/ereignis",
    )
    try:
        answer: object = model_service.chat.submit_sync(request).parsed
    except Exception as exc:
        logger.exception("Ereignis: Modellaufruf fehlgeschlagen")
        raise ModelCallError(  # noqa: TRY003 — die Art des Ausfalls gehört in den Eintrag
            f"Modellaufruf fehlgeschlagen: {type(exc).__name__}",
        ) from exc

    # ── Ausgabe-Verifikation ────────────────────
    events: list[object] = parse_event_answer(answer)
    logger.info("Ereignis: %d Ereignisse aus %d Kandidaten", len(events), len(human))
    return events


def event_time_of(expression: str, today: date) -> tuple[datetime, str] | None:
    """Zeitpunkt und Genauigkeit eines Ereignisses aus seinem Zeitausdruck.

    Zuerst der Zeitraum (`named_period`): Ein Kalendermonat (*im November*)
    gibt den Ersten des Monats, 00:00 Ortszeit, mit `month`; ein anderer
    Zeitraum (Woche, Wochenende) gibt keinen Zeitpunkt — ein Ereignis in einer
    Woche hat keinen Tag und keinen Monat. Sonst ein Tag: `zeit_parsen_vektor`
    mit erkanntem Tag (`minute` mit Uhrzeit, sonst `day`), oder der eine Tag
    des Monats aus `read_time` (*am 3. Dezember*). Ein Jahr allein (*2019*)
    nennt weder Tag noch Monat.

    Vorbedingung: `expression` ist ein Text; `today` der heutige Tag in Ortszeit.
    Nachbedingung: `(zeitpunkt, genauigkeit)` mit einer Genauigkeit aus
        `minute`, `day`, `month`; None ohne Tag oder Monat.
    Fehlerfälle: TypeError bei falschem Typ.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(expression, str) or not isinstance(today, date):
        raise TypeError("event_time_of: Text und Datum erwartet")  # noqa: TRY003
    if not expression.strip():
        return None

    # ── Verarbeitung ────────────────────────────
    found: tuple[datetime, str] | None = None
    period: tuple[date, date] | None = named_period(expression, today)
    if period is not None:
        first, last = period
        whole_month: bool = first.day == 1 and first.month == last.month \
            and (last + timedelta(days=1)).day == 1
        if not whole_month:
            logger.error(f"Ereignis: Zeitraum {first}..{last} aus {expression!r} ist kein Monat")
            return None
        found = (datetime(first.year, first.month, 1), PRECISION_MONTH)
    else:
        vector = zeit_parsen_vektor(expression)
        day: date | None = read_time(expression, today).day()
        if vector.datum is not None and vector.tag_erkannt:
            found = (vector.datum,
                     PRECISION_MINUTE if vector.uhrzeit_erkannt else PRECISION_DAY)
        elif day is not None:
            found = (datetime.combine(day, time()), PRECISION_DAY)

    # ── Ausgabe-Verifikation ────────────────────
    if found is not None and not isinstance(found[0], datetime):
        raise RuntimeError(f"event_time_of: kein Zeitpunkt {found!r}")  # noqa: TRY003
    return found


def _person_ids(postgres_url: str, user_id: str, name: str) -> list[int] | None:
    """Die Entität der Person, wenn ihr Name genau eine trifft — sonst None.

    Vorbedingung: `user_id` nicht leer; `postgres_url` ist die Datenbank des Auftrags.
    Nachbedingung: `[id]` bei genau einem Treffer; None bei keinem, mehreren,
        leerem Namen oder einem Fehler der Suche (der Eintrag entsteht trotzdem).
    Fehlerfälle: ein Fehler der Suche geht mit `logger.exception` ins Log.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not name.strip() or name.strip().upper() == "ICH":
        return None

    # ── Verarbeitung ────────────────────────────
    try:
        matches: list[dict] = EntityResolutionService.resolve_by_name(
            postgres_url, user_id, name.strip(),
        )
    except Exception:
        logger.exception("Ereignis: Namenssuche für %r ausgefallen — ohne Person", name)
        return None

    # ── Ausgabe-Verifikation ────────────────────
    if len(matches) != 1:
        logger.info("Ereignis: %r trifft %d Entitäten — ohne Person", name, len(matches))
        return None
    ids: list[int] = [int(matches[0]["id"])]
    if ids[0] <= 0:
        raise RuntimeError(f"Ereignis: Entität ohne gültige id {matches[0]!r:.120}")  # noqa: TRY003
    return ids


def _event_fields(raw: object, human: dict[int, dict]) -> tuple[dict | None, str]:
    """Prüft ein Ereignis der Antwort: Nummer eines Kandidaten des Menschen und Titel.

    Vorbedingung: `human` sind die Kandidaten des Menschen unter ihrer Nummer.
    Nachbedingung: `(fields, "")` mit `kandidat` (int), `person`, `titel`,
        `zeitausdruck` (Texte, `titel` nicht leer) — oder `(None, ausgang)`
        mit `form` oder `kandidat_unbekannt`.
    Fehlerfälle: keine — eine verfehlte Form ist ein Ausgang, laut im Log.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(raw, dict):
        logger.error("Ereignis: Eintrag kein Objekt: %.200r", raw)
        return None, EVENT_FORM
    number: object = raw.get("kandidat")
    if isinstance(number, str) and number.strip().isdigit():
        number = int(number.strip())

    # ── Verarbeitung ────────────────────────────
    if not isinstance(number, int) or isinstance(number, bool) or number not in human:
        logger.error("Ereignis: Nummer %r ist kein Kandidat des Menschen", number)
        return None, EVENT_UNKNOWN_CANDIDATE
    fields: dict = {"kandidat": number}
    for field in ("person", "titel", "zeitausdruck"):
        value: object = raw.get(field)
        fields[field] = value.strip() if isinstance(value, str) else ""

    # ── Ausgabe-Verifikation ────────────────────
    if not fields["titel"]:
        logger.error("Ereignis: Eintrag ohne Titel: %.200r", raw)
        return None, EVENT_FORM
    return fields, ""


def _write_event(state: dict, fields: dict, moment: tuple[datetime, str],
                 postgres_url: str) -> int | None:
    """Schreibt ein Ereignis in die Timeline des Paares und liest es zurück.

    Vorbedingung: `fields` aus `_event_fields`; `moment` aus `event_time_of`;
        `state` trägt das Paar.
    Nachbedingung: die id der Zeile, wenn sie mit Paar und Typ `ereignis`
        zurückgelesen ist; sonst None.
    Fehlerfälle: ein Fehler beim Schreiben oder Lesen ergibt None mit
        `logger.exception`; eine Zeile, die nicht passt, None mit `logger.error`.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id: str = state["user_id"]
    character_id: str = state["character_id"]
    kind: EventType = event_type(OCCURRENCE_TYPE)
    event_time, precision = moment

    # ── Verarbeitung ────────────────────────────
    try:
        timeline_id: int = TimelineRepository.insert(
            postgres_url, user_id, character_id, event_time, OCCURRENCE_TYPE,
            fields["titel"], details=fields["person"] or None, precision=precision,
            entitaet_ids=_person_ids(postgres_url, user_id, fields["person"]),
            wiedervorlage_am=resubmission_at(kind.remind, event_time),
            binding=kind.binding, remind=kind.remind, conflict_check=kind.conflict_check,
        )
        row: dict | None = TimelineRepository.find_by_id(postgres_url, timeline_id)
    except Exception:
        logger.exception("Ereignis: %r nicht eingetragen", fields["titel"])
        return None

    # ── Ausgabe-Verifikation ────────────────────
    expected: dict = {"user_id": user_id, "character_id": character_id,
                      "event_type": OCCURRENCE_TYPE}
    if row is None or any(row.get(k) != v for k, v in expected.items()):
        logger.error("Ereignis: Zeile %s nicht wie geschrieben: %.200r", timeline_id, row)
        return None
    return timeline_id


def _handle_event(state: dict, raw: object, human: dict[int, dict], today: date,
                  postgres_url: str) -> tuple[dict, int | None]:
    """Ein Ereignis der Antwort: prüfen, Zeit lesen, schreiben.

    Vorbedingung: wie `_event_fields` und `_write_event`.
    Nachbedingung: `(result, timeline_id)` — `result` trägt `ausgang` aus
        `EVENT_OUTCOMES`; `timeline_id` nur bei `eingetragen`.
    Fehlerfälle: ein Ausgang außerhalb der Menge wirft ValueError.
    """
    # ── Eingabe-Validierung ─────────────────────
    fields, defect = _event_fields(raw, human)
    if fields is None:
        return {"roh": repr(raw)[:200], "ausgang": defect}, None

    # ── Verarbeitung ────────────────────────────
    moment: tuple[datetime, str] | None = event_time_of(fields["zeitausdruck"], today)
    timeline_id: int | None = None
    if moment is None:
        outcome: str = EVENT_NO_TIME
    else:
        timeline_id = _write_event(state, fields, moment, postgres_url)
        outcome = EVENT_WRITTEN if timeline_id is not None else EVENT_FAILED

    # ── Ausgabe-Verifikation ────────────────────
    if outcome not in EVENT_OUTCOMES:
        raise ValueError(f"Ereignis: unbekannter Ausgang {outcome!r}")  # noqa: TRY003
    result: dict = {**fields, "ausgang": outcome, "timeline_id": timeline_id,
                    "genauigkeit": moment[1] if moment else None}
    return result, timeline_id


def _classify_and_write(state: dict, human: dict[int, dict],
                        postgres_url: str) -> tuple[dict, dict[int, int | None]]:
    """Der Modellaufruf eines Auftrags und das Schreiben seiner Ereignisse.

    Vorbedingung: `human` nicht leer.
    Nachbedingung: `(outcome, mapping)` — `mapping` trägt je Kandidat mit
        `eingetragen` die Zeile, mit `ereignis_fehlt` None.
    Fehlerfälle: Ein Ausfall des Modells ist `modell_ausfall` oder
        `antwort_defekt`, die Abbildung leer. ValueError bei leerer Äußerung.
    """
    # ── Eingabe-Validierung ─────────────────────
    utterance: str = reiz_text(state)
    if not utterance.strip():
        raise ValueError("Ereignis: Kandidaten des Menschen, aber keine Äußerung")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    try:
        events: list[object] = classify_events(utterance, human)
    except ModelCallError as exc:
        return {"ausgang": OUTCOME_MODEL_FAILED, "fehler": str(exc)}, {}
    except AnswerFormError as exc:
        logger.exception("Ereignis: Antwort des Modells defekt")
        return {"ausgang": OUTCOME_ANSWER_BROKEN, "fehler": str(exc)[:300]}, {}
    today: date = now_local().date()
    results: list[dict] = []
    mapping: dict[int, int | None] = {}
    for raw in events:
        result, timeline_id = _handle_event(state, raw, human, today, postgres_url)
        results.append(result)
        if result["ausgang"] in (EVENT_WRITTEN, EVENT_FAILED):
            mapping[result["kandidat"]] = timeline_id

    # ── Ausgabe-Verifikation ────────────────────
    if len(results) != len(events):
        raise ValueError("Ereignis: nicht jedes Ereignis hat einen Ausgang")  # noqa: TRY003
    outcome: dict = {
        "ausgang":    OUTCOME_CLASSIFIED if results else OUTCOME_NO_EVENT,
        "ereignisse": results,
    }
    return outcome, mapping


def _record(state: dict, data: dict, outcome: dict) -> None:
    """Der eine Eintrag `log_db_write` je Auftrag (Knoten dispatcher, Quelle timeline).

    `log_db_write` gibt nichts zurück, das sich prüfen ließe; geprüft wird der
    Ausgang vor dem Schreiben.

    Vorbedingung: `outcome` trägt `ausgang`.
    Nachbedingung: ein Eintrag mit Ausgang, den Ereignissen und der Salienz.
    Fehlerfälle: ein Ausgang außerhalb von `OUTCOMES` wirft ValueError.
    """
    # ── Eingabe-Validierung ─────────────────────
    if outcome.get("ausgang") not in OUTCOMES:
        raise ValueError(f"Ereignis: Eintrag mit Ausgang {outcome.get('ausgang')!r}")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    log_db_write(
        turn_id      = state.get("turn_id", "unbekannt"),
        node         = "dispatcher",
        quelle       = "timeline",
        inhalt       = {**outcome, "aktion": "ereignis",
                        "verlauf_id": data.get("verlauf_id"),
                        "salienz_human": data.get("salienz_human")},
        user_id      = state.get("user_id", ""),
        character_id = state.get("character_id", ""),
    )
    logger.info(f"Ereignis-Auftrag: Ausgang {outcome['ausgang']}")


def _order_defect(state: dict, data: object) -> str:
    """Was einem Auftrag fehlt — leer, wenn er ausführbar ist.

    Vorbedingung: keine.
    Nachbedingung: ein Text, der den ersten Mangel nennt, oder "".
    Fehlerfälle: keine — der Mangel ist der Ausgang `verworfen`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not state.get("user_id") or not state.get("character_id"):
        return "Paar fehlt im Turn"

    # ── Verarbeitung ────────────────────────────
    if not isinstance(data, dict):
        return "daten fehlen"
    turn_id: object = data.get("turn_id")

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(turn_id, str) or not turn_id:
        return "turn_id fehlt"
    if not isinstance(data.get("abgelegt"), bool):
        return "Ausgang des Ablegens fehlt"
    return ""


def _run_one(state: dict, data: dict, postgres_url: str) -> tuple[dict, dict[int, int | None]]:
    """Führt einen ausführbaren Auftrag aus — Ausgang und Abbildung.

    Vorbedingung: `_order_defect(state, data)` ist leer.
    Nachbedingung: der Eintrag ist geschrieben; die Abbildung ist leer ohne
        Ereignis und trägt nur Nummern von Kandidaten des Menschen.
    Fehlerfälle: Ein Fehler beim Lesen der Kandidaten oder vor dem Modellaufruf
        wird als `fehler` eingetragen und weitergeworfen. Eine Nummer in der
        Abbildung, die kein Kandidat des Menschen ist, wird als `fehler`
        eingetragen und wirft ValueError.
    """
    # ── Eingabe-Validierung ─────────────────────
    if data["abgelegt"] is False:
        outcome: dict = {"ausgang": OUTCOME_NOT_STORED}
        _record(state, data, outcome)
        return outcome, {}

    # ── Verarbeitung ────────────────────────────
    mapping: dict[int, int | None] = {}
    try:
        candidates: list[dict] = turn_candidates(
            postgres_url, state["user_id"], state["character_id"], data["turn_id"],
        )
        numbered: dict[int, dict] = dict(enumerate(candidates, start=1))
        human: dict[int, dict] = {
            n: k for n, k in numbered.items() if k.get("sprecher") == HUMAN_SPEAKER
        }
        if not candidates:
            outcome = {"ausgang": OUTCOME_EMPTY}
        elif not human:
            outcome = {"ausgang": OUTCOME_OTHER_SPEAKERS}
        else:
            outcome, mapping = _classify_and_write(state, human, postgres_url)
    except Exception as exc:
        _record(state, data, {"ausgang": OUTCOME_ERROR,
                              "fehler": f"{type(exc).__name__}: {exc}"[:300]})
        raise

    # ── Ausgabe-Verifikation ────────────────────
    strangers: set[int] = set(mapping) - set(human)
    if strangers:
        _record(state, data, {"ausgang": OUTCOME_ERROR,
                              "fehler": f"Abbildung mit fremden Nummern {sorted(strangers)}"})
        raise ValueError(f"Ereignis: Abbildung mit fremden Nummern {sorted(strangers)}")  # noqa: TRY003
    _record(state, data, {**outcome, "kandidaten": len(candidates)})
    return outcome, mapping


def process_event_orders(state: dict, writes: list[dict],
                         postgres_url: str) -> dict[int, int | None]:
    """Führt die Ereignis-Aufträge aus — die Abbildung Kandidat → Timeline-Zeile.

    Vorbedingung: `writes` sind die Writes mit `ziel="timeline"`,
        `aktion="ereignis"`; `state` trägt `user_id`, `character_id`, `turn_id`.
    Nachbedingung: je Auftrag genau ein Eintrag `log_db_write`; zurück kommt
        je Kandidat eines erkannten Ereignisses mit Zeit die id seiner Zeile —
        oder None, wenn das Schreiben scheiterte (dann kein Fakt). Ein
        Kandidat ohne Ereignis oder ohne Zeit steht nicht in der Abbildung.
    Fehlerfälle: Ein Turn ohne Paar oder ein unvollständiger Auftrag wird mit
        `logger.error` als `verworfen` eingetragen und schreibt nichts. Ein
        Fehler beim Lesen wirft nach seinem Eintrag; der Dispatcher meldet ihn.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(writes, list):
        raise TypeError(f"Ereignis-Aufträge keine Liste: {type(writes).__name__}")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    mapping: dict[int, int | None] = {}
    for write in writes:
        data: object = write.get("daten") if isinstance(write, dict) else None
        defect: str = _order_defect(state, data)
        if defect:
            logger.error(f"Ereignis-Auftrag verworfen: {defect} — {write!r:.200}")
            _record(state, data if isinstance(data, dict) else {},
                    {"ausgang": OUTCOME_REJECTED, "mangel": defect})
            continue
        _, per_order = _run_one(state, data, postgres_url)
        mapping.update(per_order)

    # ── Ausgabe-Verifikation ────────────────────
    invalid: list[object] = [
        k for k, v in mapping.items()
        if not isinstance(k, int) or not (v is None or isinstance(v, int))
    ]
    if invalid:
        raise ValueError(f"Ereignis: Abbildung mit ungültigen Einträgen {invalid}")  # noqa: TRY003
    return mapping
