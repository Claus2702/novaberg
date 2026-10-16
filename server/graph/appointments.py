"""Die Termine des Menschen in einem Turn: welcher Zeitraum, welche Termine.

**Warum ein eigenes Modul ohne Datenbank.** Der Zustand eines Turns traegt
das Leseergebnis als Kanal (`graph/state.py`), und der Zustand wird ueberall
importiert. Was hier steht, sind Datencontainer und die Rechnung des
Zeitraums aus der Anfrage des Routers — beides ohne Verbindung bezeugbar.
Gelesen wird in `memory/timeline_reading.py`, gesetzt wird der Block in
`graph/format/appointments.py`.

**Warum das Fenster hinter dem Router entsteht.** `needs_timeline` und
`timeline_query` setzt erst der Router. Ein Leseweg davor sieht nur ihre
Vorbelegung, und sein gezielter Zweig ist nie erreichbar.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger("ki_server.graph.appointments")

KIND_RANGE: str = "range"
KIND_SEARCH: str = "search"
KIND_PROACTIVE: str = "proactive"

DIRECTION_FORWARD: str = "forward"
DIRECTION_BACKWARD: str = "backward"
DIRECTION_BOTH: str = "both"
DIRECTIONS: tuple[str, ...] = (DIRECTION_FORWARD, DIRECTION_BACKWARD, DIRECTION_BOTH)

#: Das Fenster ohne gezielte Anfrage: drei Tage zurueck, vierzehn voraus —
#: derselbe Umfang wie bisher im Gedaechtnisblock.
PROACTIVE_DAYS_BACK: int = 3
PROACTIVE_DAYS_AHEAD: int = 14

#: Treffer einer Suche nach Titel, wenn die Anfrage keine Zahl nennt, und
#: die Obergrenze, die der Router-Prompt vorgibt (`limit: 1-10`).
SEARCH_LIMIT_DEFAULT: int = 5
SEARCH_LIMIT_MAX: int = 10

#: Laenge einer Datumsangabe ohne Uhrzeit (`YYYY-MM-DD`).
_DATE_ONLY_LENGTH: int = 10


@dataclass(frozen=True)
class AppointmentWindow:
    """Was in diesem Turn gelesen wird.

    `kind` ist `range`, `search` oder `proactive`. Bei `range` und
    `proactive` tragen `start` und `end` den Zeitraum in Ortszeit, bei
    `search` sind beide `None` und `keyword` und `limit` gesetzt.
    `unusable_query` ist wahr, wenn der Router nach Terminen gefragt hat,
    seine Anfrage aber nicht lesbar war — dann gilt das proaktive Fenster,
    und der Block sagt das.
    """

    kind: str
    direction: str
    start: datetime | None = None
    end: datetime | None = None
    keyword: str = ""
    limit: int = 0
    unusable_query: bool = False


@dataclass(frozen=True)
class Appointment:
    """Ein Termin des Menschen, so wie er im Block steht.

    `moment` ist zeitzonenbewusst in Ortszeit. `has_time` ist falsch fuer
    einen Termin, der nur einen Tag traegt. `past` ist vorgerechnet: mit
    Uhrzeit vor dem Zeitpunkt des Turns, ohne Uhrzeit vor dem heutigen Tag.
    """

    moment: datetime
    has_time: bool
    title: str
    details: str
    past: bool


@dataclass(frozen=True)
class AppointmentReading:
    """Das Leseergebnis eines Turns: Fenster, Uhr des Turns, Termine.

    `failed` heisst: Die Timeline wurde nicht gelesen. Dann sagt
    `appointments` nichts aus — ein Ausfall ist kein leerer Zeitraum.
    `discarded` zaehlt die gelesenen Zeilen, die nicht in `appointments`
    stehen: von der Ausgabe-Verifikation oder nach der Richtung verworfen.
    """

    window: AppointmentWindow
    now: datetime
    appointments: tuple[Appointment, ...] = ()
    failed: bool = False
    discarded: int = 0


def proactive_window(now: datetime, unusable_query: bool = False) -> AppointmentWindow:
    """Das Fenster ohne gezielte Anfrage: drei Tage zurueck, vierzehn voraus.

    Vorbedingung: `now` ist zeitzonenbewusst.
    Nachbedingung: ein Fenster der Art `proactive`, Richtung `both`, mit
        `start < now < end`.
    Fehlerfaelle: ein naiver Zeitpunkt wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if now.tzinfo is None:
        msg: str = "proactive_window: Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    window = AppointmentWindow(
        kind=KIND_PROACTIVE,
        direction=DIRECTION_BOTH,
        start=now - timedelta(days=PROACTIVE_DAYS_BACK),
        end=now + timedelta(days=PROACTIVE_DAYS_AHEAD),
        unusable_query=unusable_query,
    )

    # ── Ausgabe-Verifikation ────────────────────
    if not (window.start < now < window.end):
        msg = f"proactive_window: Fenster {window.start} bis {window.end} umfasst jetzt nicht"
        raise RuntimeError(msg)
    return window


def query_direction(query: dict) -> str:
    """Die Richtung einer Anfrage: `forward`, `backward` oder `both`.

    Fehlt sie (der Router-Prompt erlaubt `null`), gilt `both` — dann stehen
    vergangene Termine gekennzeichnet da und fehlen nicht. Eine Richtung, die
    keiner der drei ist, wird laut gemeldet und gilt ebenfalls als `both`.

    Vorbedingung: `query` ist ein dict.
    Nachbedingung: einer der drei Werte aus `DIRECTIONS`.
    Fehlerfaelle: keine — eine unbekannte Richtung ist ein Befund im Log.
    """
    # ── Eingabe-Validierung ─────────────────────
    raw: object = query.get("direction")
    if raw is None or raw == "":
        return DIRECTION_BOTH

    # ── Verarbeitung ────────────────────────────
    direction: str = str(raw).strip().lower()

    # ── Ausgabe-Verifikation ────────────────────
    if direction not in DIRECTIONS:
        logger.error(
            f"Termine: unbekannte Richtung {raw!r} in der Anfrage des Routers — "
            f"gelesen wird in beide Richtungen"
        )
        return DIRECTION_BOTH
    return direction


def parse_local_moment(text: object, now: datetime, end_of_day: bool) -> datetime | None:
    """Liest eine Zeitangabe des Routers als Zeitpunkt in Ortszeit.

    Eine Angabe ohne Zeitzone gilt als Ortszeit (die Zone von `now`). Eine
    Angabe ohne Uhrzeit (`YYYY-MM-DD`) ist der Beginn des Tages oder, mit
    `end_of_day`, sein Ende (23:59:59).

    Vorbedingung: `now` ist zeitzonenbewusst; `text` ist der Wert aus der
        Anfrage, moeglicherweise `None`.
    Nachbedingung: ein zeitzonenbewusster Zeitpunkt in der Zone von `now`,
        oder `None`, wenn `text` leer ist.
    Fehlerfaelle: eine Angabe, die kein ISO-Datum ist, wirft `ValueError`;
        eine Angabe, die kein Text ist, wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if text is None or (isinstance(text, str) and not text.strip()):
        return None
    if not isinstance(text, str):
        msg: str = f"Zeitangabe ist kein Text: {type(text).__name__}"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    cleaned: str = text.strip()
    moment: datetime = datetime.fromisoformat(cleaned)
    if len(cleaned) == _DATE_ONLY_LENGTH and end_of_day:
        moment = moment.replace(hour=23, minute=59, second=59)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=now.tzinfo)
    local: datetime = moment.astimezone(now.tzinfo)

    # ── Ausgabe-Verifikation ────────────────────
    if local.tzinfo is None:
        msg = f"Zeitangabe {text!r} ohne Zeitzone nach der Umrechnung"
        raise RuntimeError(msg)
    return local


def range_window(query: dict, now: datetime) -> AppointmentWindow:
    """Das Fenster einer Zeitraum-Anfrage (`type: range`).

    `from` und `to` bilden den Zeitraum. Fehlen beide und steht `date` da,
    gilt dieser Tag. Fehlt `from`, beginnt der Zeitraum heute um 00:00;
    fehlt `to`, endet er am Ende des Tages von `from`.

    Vorbedingung: `query` ist ein dict, `now` zeitzonenbewusst.
    Nachbedingung: ein Fenster der Art `range` mit `start <= end`.
    Fehlerfaelle: unlesbare Zeitangaben oder ein Ende vor dem Beginn werfen
        `ValueError`, eine Zeitangabe, die kein Text ist, `TypeError` — der
        Aufrufer ersetzt dann das Fenster und meldet es.
    """
    # ── Eingabe-Validierung ─────────────────────
    start: datetime | None = parse_local_moment(query.get("from"), now, end_of_day=False)
    end: datetime | None = parse_local_moment(query.get("to"), now, end_of_day=True)
    if start is None and end is None:
        start = parse_local_moment(query.get("date"), now, end_of_day=False)
        end = parse_local_moment(query.get("date"), now, end_of_day=True)

    # ── Verarbeitung ────────────────────────────
    if start is None:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if end is None:
        end = start.replace(hour=23, minute=59, second=59, microsecond=0)

    # ── Ausgabe-Verifikation ────────────────────
    if end < start:
        msg: str = f"Zeitraum endet vor seinem Beginn: {start} bis {end}"
        raise ValueError(msg)
    return AppointmentWindow(
        kind=KIND_RANGE, direction=query_direction(query), start=start, end=end,
    )


def search_window(query: dict) -> AppointmentWindow:
    """Das Fenster einer Suche nach Titel (`type: search`).

    Vorbedingung: `query` ist ein dict.
    Nachbedingung: ein Fenster der Art `search` mit nicht leerem `keyword`
        und `1 <= limit <= SEARCH_LIMIT_MAX`. Fehlt `limit`, gilt
        `SEARCH_LIMIT_DEFAULT`.
    Fehlerfaelle: ein fehlendes `keyword` oder ein `limit` ausserhalb von
        1 bis 10 wirft `ValueError`, ein `limit`, das keine ganze Zahl ist,
        `TypeError`. **Kein Ersatz aus `title`:** Ein Suchbegriff, den der
        Router nicht gesetzt hat, ist keine Anfrage.
    """
    # ── Eingabe-Validierung ─────────────────────
    keyword: object = query.get("keyword")
    if not isinstance(keyword, str) or not keyword.strip():
        msg: str = f"Suche ohne Suchbegriff: keyword={keyword!r}"
        raise ValueError(msg)
    raw_limit: object = query.get("limit")
    limit: int = SEARCH_LIMIT_DEFAULT if raw_limit is None else raw_limit
    if isinstance(limit, bool) or not isinstance(limit, int):
        msg = f"Suche mit unlesbarer Trefferzahl: limit={raw_limit!r}"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    window = AppointmentWindow(
        kind=KIND_SEARCH, direction=query_direction(query),
        keyword=keyword.strip(), limit=limit,
    )

    # ── Ausgabe-Verifikation ────────────────────
    if not 1 <= window.limit <= SEARCH_LIMIT_MAX:
        msg = f"Suche mit Trefferzahl ausserhalb von 1 bis {SEARCH_LIMIT_MAX}: {limit}"
        raise ValueError(msg)
    return window


def appointment_window(state: dict, now: datetime) -> AppointmentWindow:
    """Welcher Zeitraum in diesem Turn gelesen wird — aus der Anfrage des Routers.

    Ohne `needs_timeline` oder ohne Anfrage gilt das proaktive Fenster. Eine
    Anfrage, die sich nicht lesen laesst, wird laut gemeldet und ebenfalls
    durch das proaktive Fenster ersetzt; das Fenster traegt dann
    `unusable_query`, und der Block sagt, dass nicht der gefragte Zeitraum
    dasteht.

    Vorbedingung: `state` ist der Zustand nach dem Router; `now` ist
        zeitzonenbewusst in Ortszeit.
    Nachbedingung: ein gueltiges Fenster — nie `None`.
    Fehlerfaelle: ein naiver Zeitpunkt wirft `ValueError`. Eine unlesbare
        Anfrage wirft nicht, sie wird gemeldet und ersetzt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if now.tzinfo is None:
        msg: str = "appointment_window: Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)
    query: object = state.get("timeline_query")
    if not state.get("needs_timeline") or not query:
        return proactive_window(now)
    if not isinstance(query, dict):
        logger.error(
            f"Termine: Anfrage des Routers ist kein dict ({type(query).__name__}) — "
            f"gelesen wird das proaktive Fenster"
        )
        return proactive_window(now, unusable_query=True)

    kind: object = query.get("type")
    if kind not in (KIND_RANGE, KIND_SEARCH):
        logger.error(
            f"Termine: Anfrage des Routers nicht lesbar (unbekannte Art {kind!r}; "
            f"{query!r}) — gelesen wird das proaktive Fenster"
        )
        return proactive_window(now, unusable_query=True)

    # ── Verarbeitung ────────────────────────────
    window: AppointmentWindow | None = None
    unreadable: str = ""
    try:
        window = range_window(query, now) if kind == KIND_RANGE else search_window(query)
    except (ValueError, TypeError) as error:
        # Die Meldung steht hinter dem try: Ein Lesefehler der Anfrage ist ein
        # Befund ueber den Router, kein Absturz — der Turn liest proaktiv.
        unreadable = str(error)
    if window is None:
        logger.error(
            f"Termine: Anfrage des Routers nicht lesbar ({unreadable}; {query!r}) — "
            f"gelesen wird das proaktive Fenster"
        )
        return proactive_window(now, unusable_query=True)

    # ── Ausgabe-Verifikation ────────────────────
    if window.kind not in (KIND_RANGE, KIND_SEARCH):
        msg = f"appointment_window: Art {window.kind!r} aus einer gezielten Anfrage"
        raise RuntimeError(msg)
    return window
