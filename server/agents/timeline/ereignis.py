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
(`zeit_parsen_vektor`, `read_time`); ohne Tag oder Monat kein Eintrag. Ist
der Ausdruck ein Datum ohne Jahr (*im Mai*, *am 3. März*, *am 12.2.*, auch mit
Uhrzeit), gibt die Zeitlage des Modells das Jahr: angekündigt das nächste
solche Datum ab heute, berichtet das letzte bis heute. Die
Person über `resolve_by_name`: eindeutig → `entitaet_ids=[id]`, sonst ohne,
der Eintrag entsteht trotzdem. Geschrieben mit dem Paar und dem Typ `ereignis`
aus `memory.timeline_types`, ohne Wiedervorlage und ohne Duplikatprüfung.

Eine Ausnahme vom neuen Eintrag ist die Klärung: Nennt ein Ereignis einen Tag,
und steht im Paar schon dasselbe Ereignis derselben Person mit `month` in
diesem Monat, wird diese Zeile auf den Tag verschoben (`verschieben`), statt
eine zweite anzulegen. Die Abbildung zeigt dann auf die erste Zeile.

Die Rückgabe bildet jede Kandidaten-Nummer eines erkannten Ereignisses auf
seine Timeline-Zeile ab — oder auf None, wenn das Schreiben scheiterte: Dann
schreibt der Fakten-Agent für diesen Kandidaten keinen Fakt (`ereignis_fehlt`).
Jeder Auftrag hat genau einen Eintrag `log_db_write` (Quelle `timeline`).
"""

import logging
import re
from datetime import date, datetime, time, timedelta

from config import PROMPTS, get_node_config
from graph.reiz import reiz_text
from memory.pipeline_log import log_db_write
from memory.repositories.timeline_repository import MONTH_PRECISION, TimelineRepository
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
EVENT_MOVED:             str = "verschoben"
EVENT_OUTCOMES: frozenset[str] = frozenset({
    EVENT_WRITTEN, EVENT_NO_TIME, EVENT_UNKNOWN_CANDIDATE, EVENT_FORM, EVENT_FAILED,
    EVENT_MOVED,
})

# Die Genauigkeiten, die ein Ereignis tragen kann. Der Monat kommt aus der Quelle,
# mit der die Leser (`find_by_date_range`, `[TERMINE]`, die Mappe) vergleichen:
# Eine eigene Kopie driftete still von ihnen weg.
PRECISION_MINUTE: str = "minute"
PRECISION_DAY:    str = "day"
PRECISION_MONTH:  str = MONTH_PRECISION

# Die Zeitlage eines Ereignisses, wie das Modell sie nennt.
TENSE_ANNOUNCED: str = "angekuendigt"
TENSE_REPORTED:  str = "berichtet"
TENSES: frozenset[str] = frozenset({TENSE_ANNOUNCED, TENSE_REPORTED})

# Woher die Zeitlage eines Ereignisses kommt: aus der Antwort oder die Vorgabe.
TENSE_FROM_MODEL:   str = "modell"
TENSE_FROM_DEFAULT: str = "vorgabe"

# Die Monatsnamen eines Ausdrucks ohne Jahr, ausgeschrieben und kurz, mit ihrer Nummer.
_MONTH_NUMBERS: dict[str, int] = {
    "januar": 1, "jänner": 1, "jan": 1, "februar": 2, "feb": 2, "märz": 3, "maerz": 3,
    "mär": 3, "april": 4, "apr": 4, "mai": 5, "juni": 6, "jun": 6, "juli": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sept": 9, "sep": 9, "oktober": 10, "okt": 10,
    "november": 11, "nov": 11, "dezember": 12, "dez": 12,
}

# Ein Kalenderdatum ohne Jahr, sonst nichts: ein Monat ("im Mai") oder ein Tag und
# Monat in Worten oder Ziffern ("am 3. März", "am 12.2."), dieser mit einer Uhrzeit
# ("am 3. März um 10 Uhr", "am 12.2. um 9"). Eine Uhrzeit steht hinter "um"/"gegen"
# oder vor "Uhr" — eine nackte Zahl dahinter ist ein Jahr ("am 12.2.27").
_WITHOUT_YEAR: re.Pattern[str] = re.compile(
    r"(?:(?:im|am|den|der|zum)\s+)?(?:"
    r"(?P<day>\d{1,2})\.\s*(?:(?P<month_number>\d{1,2})\.|(?P<month_word>[a-zäöü]+)\.?)"
    r"(?:\s*,?\s*(?=(?:um|gegen)\s|\d{1,2}(?:[:.]\d{2})?\s*uhr\b)(?:(?:um|gegen)\s+)?"
    r"(?P<hour>\d{1,2})(?:[:.](?P<minute>\d{2}))?(?:\s*uhr)?)?"
    r"|(?P<month_only>[a-zäöü]+)\.?)",
)

# So viele Jahre sucht die Zeitlage höchstens ab — ein 29. Februar kommt in
# acht Jahren mindestens einmal vor.
_YEARS_SEARCHED: int = 9


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


def _date_without_year(expression: str) -> tuple[int, int | None, time | None] | None:
    """Monat, Tag und Uhrzeit eines Zeitausdrucks, der ein Datum ohne Jahr ist.

    Das Kriterium: Der ganze Ausdruck ist ein Kalenderdatum ohne Jahr — ein
    Monat oder ein Tag und Monat, in Worten oder Ziffern, dieser auch mit
    Uhrzeit — und sonst nur eine Präposition oder ein Artikel davor. *im
    Mai*, *am 3. März*, *am 12.2.*, *den 14.11.*, *am 3. März um 10 Uhr*: ja.
    Nein, wenn das Jahr im Ausdruck steht (*im Mai 2027*, *am 12.2.2027*)
    oder er relativ zu heute ist — sein Datum zählt dann von heute aus: mit
    einer Richtung (*nächsten Mai*, *diesen März*), einem Abstand (*in drei
    Wochen*), einem Tag, den heute festlegt (*morgen*, *am Freitag*), oder
    ohne Monat (*am 14.*). Jedes davon trägt ein Wort mehr oder einen Monat
    weniger, als die Form erlaubt; es bleibt, wie der Parser es liest.

    Vorbedingung: `expression` ist ein Text.
    Nachbedingung: `(monat, tag, uhrzeit)` mit Monat 1–12, Tag 1–31 oder None
        (ganzer Monat), Uhrzeit oder None; None, wenn der Ausdruck kein Datum
        ohne Jahr ist. Ob es den Tag in diesem Monat gibt, prüft `_year_by_tense`.
    Fehlerfälle: TypeError bei falschem Typ.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(expression, str):
        raise TypeError("_date_without_year: Text erwartet")  # noqa: TRY003
    match: re.Match[str] | None = _WITHOUT_YEAR.fullmatch(expression.strip().casefold())
    if match is None:
        return None

    # ── Verarbeitung ────────────────────────────
    parts: dict[str, str | None] = match.groupdict()
    word: str = parts["month_word"] or parts["month_only"] or ""
    month: int = int(parts["month_number"]) if parts["month_number"] else \
        _MONTH_NUMBERS.get(word, 0)
    day: int | None = int(parts["day"]) if parts["day"] else None
    hour: int = int(parts["hour"]) if parts["hour"] else 0
    minute: int = int(parts["minute"]) if parts["minute"] else 0

    # ── Ausgabe-Verifikation ────────────────────
    # Das Muster nimmt jedes Wort (*am Freitag*) und jede Zahl (*am 3.13.*, *um 25*);
    # ein Datum ist es nur mit einem Monat, einem möglichen Tag und einer möglichen Uhrzeit.
    if not 1 <= month <= 12 or (day is not None and not 1 <= day <= 31):
        return None
    if hour > 23 or minute > 59:
        return None
    clock: time | None = time(hour, minute) if parts["hour"] else None
    return month, day, clock


def _year_by_tense(parts: tuple[int, int | None, time | None], tense: str,
                   today: date) -> tuple[datetime, str] | None:
    """Zeitpunkt eines Datums ohne Jahr, das Jahr aus der Zeitlage des Satzes.

    Angekündigt: das nächste solche Datum ab heute — ein Monat ab dem
    laufenden (*im Oktober*, gesagt im Oktober, ist dieser), ein Tag ab
    heute, auch mit Uhrzeit. Berichtet: das letzte solche Datum bis heute.
    Monat, Tag und Uhrzeit bleiben, nur das Jahr wird gewählt.

    Vorbedingung: `parts` aus `_date_without_year`; `tense` aus `TENSES`;
        `today` der heutige Tag in Ortszeit.
    Nachbedingung: `(zeitpunkt, genauigkeit)` — `month` ohne Tag (der Erste),
        `minute` mit Uhrzeit, sonst `day`; angekündigt nie vor dem laufenden
        Monat (Tag), berichtet nie danach; None, wenn es den Tag in diesem Monat
        nicht gibt (*am 31. April*), laut im Log.
    Fehlerfälle: ValueError bei unbekannter Zeitlage.
    """
    # ── Eingabe-Validierung ─────────────────────
    month, day, clock = parts
    if tense not in TENSES:
        raise ValueError(f"_year_by_tense: unbekannte Zeitlage {tense!r}")  # noqa: TRY003
    announced: bool = tense == TENSE_ANNOUNCED
    reference: date = today if day is not None else today.replace(day=1)
    precision: str = PRECISION_MONTH if day is None else \
        PRECISION_MINUTE if clock is not None else PRECISION_DAY

    # ── Verarbeitung ────────────────────────────
    found: date | None = None
    for offset in range(_YEARS_SEARCHED):
        year: int = today.year + offset if announced else today.year - offset
        try:
            candidate: date = date(year, month, day or 1)
        except ValueError:
            continue
        fits: bool = candidate >= reference if announced else candidate <= reference
        if fits:
            found = candidate
            break

    # ── Ausgabe-Verifikation ────────────────────
    if found is None:
        logger.error("Ereignis: den %s.%s. gibt es nicht — keine Zeit", day, month)
        return None
    return datetime.combine(found, clock or time()), precision


def _read_moment(expression: str, today: date) -> tuple[datetime, str] | None:
    """Zeitpunkt und Genauigkeit eines Ausdrucks, wie der Parser ihn liest.

    Zuerst der Zeitraum (`named_period`): Ein Kalendermonat gibt den Ersten
    des Monats mit `month`; ein anderer Zeitraum (Woche, Wochenende) gibt
    keinen Zeitpunkt, laut im Log. Sonst ein Tag: `zeit_parsen_vektor` mit
    erkanntem Tag (`minute` mit Uhrzeit, sonst `day`), oder der eine Tag des
    Monats aus `read_time`. Das Jahr ist das des Parsers.

    Vorbedingung: `expression` ist ein nicht leerer Text; `today` ein Datum.
    Nachbedingung: `(zeitpunkt, genauigkeit)` oder None ohne Tag oder Monat.
    Fehlerfälle: TypeError bei falschem Typ.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(expression, str) or not isinstance(today, date):
        raise TypeError("_read_moment: Text und Datum erwartet")  # noqa: TRY003

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
    if found is not None and found[1] not in (PRECISION_MINUTE, PRECISION_DAY, PRECISION_MONTH):
        raise RuntimeError(f"_read_moment: unbekannte Genauigkeit {found!r}")  # noqa: TRY003
    return found


def event_time_of(expression: str, today: date, tense: str) -> tuple[datetime, str] | None:
    """Zeitpunkt und Genauigkeit eines Ereignisses aus seinem Zeitausdruck.

    Ist der Ausdruck ein Datum ohne Jahr (`_date_without_year`: *im Mai*, *am
    3. März*, *am 12.2.*, *am 3. März um 10 Uhr*), setzt die Zeitlage das Jahr
    (`_year_by_tense`) — der Parser gäbe das laufende Jahr, auch für einen
    vorbeigegangenen Monat oder Tag. Sonst liest ihn der Parser
    (`_read_moment`): ein Kalendermonat mit `month`, ein Tag mit `day` oder
    `minute`; ein Ausdruck mit Jahr oder relativ zu heute (*im Mai 2027*,
    *nächsten Monat*) bleibt so, wie er gelesen wird. Eine Woche oder ein
    Jahr allein (*2019*) nennt weder Tag noch Monat.

    Vorbedingung: `expression` ist ein Text; `today` der heutige Tag in
        Ortszeit; `tense` aus `TENSES`.
    Nachbedingung: `(zeitpunkt, genauigkeit)` mit einer Genauigkeit aus
        `minute`, `day`, `month`; None ohne Tag oder Monat und für einen Tag,
        den es im Monat nicht gibt.
    Fehlerfälle: TypeError bei falschem Typ; ValueError bei unbekannter Zeitlage.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(expression, str) or not isinstance(today, date):
        raise TypeError("event_time_of: Text und Datum erwartet")  # noqa: TRY003
    if tense not in TENSES:
        raise ValueError(f"event_time_of: unbekannte Zeitlage {tense!r}")  # noqa: TRY003
    if not expression.strip():
        return None

    # ── Verarbeitung ────────────────────────────
    found: tuple[datetime, str] | None
    parts: tuple[int, int | None, time | None] | None = _date_without_year(expression)
    if parts is not None:
        found = _year_by_tense(parts, tense, today)
        logger.info("Ereignis: %r %s → %s", expression, tense, found[0] if found else None)
    else:
        found = _read_moment(expression, today)

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


def _tense_of(raw: dict) -> tuple[str, str]:
    """Die Zeitlage eines Ereignisses der Antwort und woher sie kommt.

    Ein Ereignis wird in der Regel gemeldet, bevor es eintritt. Fehlt die
    Zeitlage oder ist sie keine aus `TENSES`, gilt deshalb `angekuendigt` —
    laut im Log und mit der Herkunft `vorgabe` im Eintrag des Auftrags, damit
    sich zählen lässt, wie oft das Modell sie nicht nennt.

    Vorbedingung: `raw` ist ein Ereignis der Antwort (ein Objekt).
    Nachbedingung: `(zeitlage, herkunft)`, die Zeitlage aus `TENSES`, die
        Herkunft `modell` oder `vorgabe`.
    Fehlerfälle: keine nach außen — eine fehlende Zeitlage ist die Vorgabe.
    """
    # ── Eingabe-Validierung ─────────────────────
    value: object = raw.get("zeitlage")
    stated: str = value.strip().casefold().replace("ü", "ue") if isinstance(value, str) else ""

    # ── Verarbeitung ────────────────────────────
    known: bool = stated in TENSES
    tense: str = stated if known else TENSE_ANNOUNCED

    # ── Ausgabe-Verifikation ────────────────────
    if not known:
        logger.error("Ereignis: Zeitlage %.40r fehlt oder unbekannt — angekündigt angenommen",
                     value)
    return tense, TENSE_FROM_MODEL if known else TENSE_FROM_DEFAULT


def _event_fields(raw: object, human: dict[int, dict]) -> tuple[dict | None, str]:
    """Prüft ein Ereignis der Antwort: Nummer eines Kandidaten des Menschen und Titel.

    Vorbedingung: `human` sind die Kandidaten des Menschen unter ihrer Nummer.
    Nachbedingung: `(fields, "")` mit `kandidat` (int), `person`, `titel`,
        `zeitausdruck` (Texte, `titel` nicht leer), `zeitlage` und
        `zeitlage_herkunft` (`_tense_of`) — oder `(None, ausgang)` mit
        `form` oder `kandidat_unbekannt`.
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
    fields["zeitlage"], fields["zeitlage_herkunft"] = _tense_of(raw)
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


def _month_row_to_move(state: dict, fields: dict, moment: tuple[datetime, str],
                       postgres_url: str) -> int | None:
    """Die eine Monatszeile desselben Ereignisses, die eine genaue Angabe klärt.

    *„Liska zieht im November um“*, dann *„am 14. November“*: Die zweite
    Angabe ist dasselbe Ereignis, genauer. Gesucht wird im Paar ein aktives
    `ereignis` mit `month`, dessen Monat den neuen Tag enthält und dessen
    Person (`details`) dieselbe ist, ohne Groß- und Kleinschreibung. Eine
    andere Figur sieht die Zeile nicht: `find_by_date_range` liest nur das
    Paar.

    Vorbedingung: `fields` aus `_event_fields`; `moment` aus `event_time_of`;
        `state` trägt das Paar.
    Nachbedingung: die id der einen passenden Zeile; None bei `month`, ohne
        Person, ohne oder mit mehreren passenden Zeilen (dann entsteht eine
        neue Zeile).
    Fehlerfälle: ein Fehler beim Lesen geht an den Aufrufer.
    """
    # ── Eingabe-Validierung ─────────────────────
    event_time, precision = moment
    person: str = fields["person"].strip().casefold()
    if precision == PRECISION_MONTH or not person:
        return None

    # ── Verarbeitung ────────────────────────────
    rows: list[dict] = TimelineRepository.find_by_date_range(
        postgres_url, state["user_id"], state["character_id"], event_time, event_time,
    )
    matches: list[dict] = [
        r for r in rows
        if r.get("event_type") == OCCURRENCE_TYPE and r.get("precision") == PRECISION_MONTH
        and (r["event_time"].year, r["event_time"].month) == (event_time.year, event_time.month)
        and str(r.get("details") or "").strip().casefold() == person
    ]

    # ── Ausgabe-Verifikation ────────────────────
    if len(matches) > 1:
        logger.info("Ereignis: %d Monatszeilen für %r — neue Zeile", len(matches), person)
        return None
    if matches and not isinstance(matches[0].get("id"), int):
        raise RuntimeError(f"Ereignis: Monatszeile ohne id {matches[0]!r:.200}")  # noqa: TRY003
    return matches[0]["id"] if matches else None


def _move_event(state: dict, fields: dict, moment: tuple[datetime, str],
                postgres_url: str) -> tuple[int | None, bool]:
    """Verschiebt die Monatszeile desselben Ereignisses auf den genauen Tag, wenn es sie gibt.

    Der Verweis eines Fakts bleibt auf der ersten Zeile; zurück kommt deshalb
    die id der Monatszeile, nicht die der neuen — Leser folgen ihr über
    `aktive_zeile`.

    Vorbedingung: wie `_month_row_to_move`.
    Nachbedingung: `(id, True)` nach dem Verschieben; `(None, False)`, wenn
        es nichts zu verschieben gibt; `(None, True)`, wenn Suche oder
        Verschieben scheiterten (laut im Log).
    Fehlerfälle: keine nach außen — ein Fehler der Datenbank ist ein Ausgang.
    """
    # ── Eingabe-Validierung ─────────────────────
    event_time, precision = moment
    kind: EventType = event_type(OCCURRENCE_TYPE)

    # ── Verarbeitung ────────────────────────────
    try:
        old_id: int | None = _month_row_to_move(state, fields, moment, postgres_url)
        if old_id is None:
            return None, False
        new_id: int = TimelineRepository.verschieben(
            postgres_url, old_id, event_time=event_time, precision=precision,
            wiedervorlage_am=resubmission_at(kind.remind, event_time),
        )
    except Exception:
        logger.exception("Ereignis: %r nicht verschoben", fields["titel"])
        return None, True

    # ── Ausgabe-Verifikation ────────────────────
    if new_id == old_id:
        logger.error("Ereignis: Verschieben von %s lieferte dieselbe Zeile", old_id)
        return None, True
    logger.info("Ereignis: %s auf %s verschoben (%s, %s)", old_id, new_id, event_time, precision)
    return old_id, True


def _handle_event(state: dict, raw: object, human: dict[int, dict], today: date,
                  postgres_url: str) -> tuple[dict, int | None]:
    """Ein Ereignis der Antwort: prüfen, Zeit lesen, verschieben oder schreiben.

    Gibt es zu einer genauen Angabe (Tag, Uhrzeit) eine Monatszeile desselben
    Ereignisses derselben Person im Paar, wird sie verschoben statt eine
    zweite Zeile anzulegen (`_move_event`).

    Vorbedingung: wie `_event_fields` und `_write_event`.
    Nachbedingung: `(result, timeline_id)` — `result` trägt `ausgang` aus
        `EVENT_OUTCOMES`; `timeline_id` nur bei `eingetragen` und
        `verschoben` (dann die erste Zeile des Ereignisses).
    Fehlerfälle: ein Ausgang außerhalb der Menge wirft ValueError.
    """
    # ── Eingabe-Validierung ─────────────────────
    fields, defect = _event_fields(raw, human)
    if fields is None:
        return {"roh": repr(raw)[:200], "ausgang": defect}, None

    # ── Verarbeitung ────────────────────────────
    moment: tuple[datetime, str] | None = event_time_of(
        fields["zeitausdruck"], today, fields["zeitlage"],
    )
    timeline_id: int | None = None
    if moment is None:
        outcome: str = EVENT_NO_TIME
    else:
        timeline_id, handled = _move_event(state, fields, moment, postgres_url)
        if handled:
            outcome = EVENT_MOVED if timeline_id is not None else EVENT_FAILED
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
        `eingetragen` die Zeile, mit `verschoben` die erste Zeile des
        Ereignisses, mit `ereignis_fehlt` None.
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
        if result["ausgang"] in (EVENT_WRITTEN, EVENT_MOVED, EVENT_FAILED):
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
