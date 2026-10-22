"""Lesen eines Termin-Fensters aus der Timeline — der eine Leseweg der Termine.

Gerufen hinter dem Router (`graph/nodes/route_reading.py::read_after_route`),
der das Fenster aus der Anfrage des Routers bildet, den Lesefehler
kompensiert und das Ergebnis als `appointment_reading` in den Zustand setzt;
ebenso vom Timeline-Agenten und vom Angebot der Sachlage
(`graph/nodes/sachlage_resolver.py`), je mit eigenem Fenster.
Dieses Modul kennt den Zustand des Graphen nicht: Aus `graph/` liest es nur
Typen und Konstanten.

**Ein Erinnerungs-Anker ist kein Termin.** Er wird in der Abfrage
ausgeschlossen und nicht dahinter: Eine Suche mit Obergrenze vergaebe ihre
Plaetze sonst an Anker, und uebrig bliebe weniger als gefragt. Die
Ausgabe-Verifikation verwirft trotzdem jeden Anker, der ankommt — laut.

**Ein Lesefehler geht an den Aufrufer.** Kompensiert wird er im Leseschritt
hinter dem Router; ein leerer Zeitraum wird er nie.

**Ein Ereignis einer anderen Person wird gelesen, nicht ausgeschlossen.** Es
traegt seinen Typ, seine Genauigkeit und seine Person ins `Appointment`; der
Block setzt es getrennt und gekennzeichnet. Ein Eintrag mit `month` gilt bis
zum Monatsende: vergangen erst im Folgemonat, im Fenster, sobald sein Monat
das Fenster ueberlappt.
"""

from __future__ import annotations

import logging
from datetime import datetime

from graph.appointments import (
    DIRECTION_BACKWARD,
    DIRECTION_FORWARD,
    KIND_SEARCH,
    Appointment,
    AppointmentReading,
    AppointmentWindow,
)
from memory.repositories.timeline_repository import MONTH_PRECISION, TimelineRepository
from memory.timeline_inventory import ANCHOR_TYPE, TIME_PRECISIONS
from memory.timeline_types import EVENT_TYPES, EventType

logger = logging.getLogger("ki_server.memory.timeline_reading")

#: Die Typen, die kein Leseweg als Termin ausgibt.
EXCLUDED_EVENT_TYPES: tuple[str, ...] = (ANCHOR_TYPE,)


def month_span(moment: datetime) -> tuple[datetime, datetime]:
    """Beginn des Monats von `moment` und Beginn des Folgemonats, in der Zone von `moment`.

    Vorbedingung: `moment` ist zeitzonenbewusst.
    Nachbedingung: `(beginn, folgebeginn)`, beginn ≤ `moment` < folgebeginn.
    Fehlerfaelle: ein naiver Zeitpunkt wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(moment, datetime) or moment.tzinfo is None:
        msg: str = f"month_span: zeitzonenbewusster Zeitpunkt erwartet ({moment!r})"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    start: datetime = moment.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    following: datetime = (
        start.replace(year=start.year + 1, month=1) if start.month == 12  # noqa: PLR2004
        else start.replace(month=start.month + 1)
    )

    # Beide Grenzen entstehen mit `replace` aus `moment` in derselben Zone und
    # umschliessen es per Konstruktion — es gibt nichts, was erst hier zu pruefen waere.
    return start, following


def _persons_of(row: dict, kind: EventType | None) -> tuple[str, ...]:
    """Die Personen eines gekennzeichneten Eintrags — aus `details`, wo der Dienst sie ablegt.

    Der Ereignis-Dienst schreibt den Namen der Person in `details`
    (`agents/timeline/ereignis.py::_write_event`). Ein Typ ohne Kennzeichnung
    ist ein Termin des Menschen und hat keine Personen.

    Vorbedingung: `row` ist eine Zeile der Timeline.
    Nachbedingung: `(name,)` fuer einen gekennzeichneten Eintrag mit Namen,
        sonst `()`.
    Fehlerfaelle: keine — ein gekennzeichneter Eintrag ohne Namen steht ohne
        Person da (der Dienst schreibt ihn so, wenn das Modell keinen nennt).
    """
    # ── Eingabe-Validierung ─────────────────────
    if kind is None or not kind.label:
        return ()

    # ── Verarbeitung ────────────────────────────
    details: object = row.get("details")
    name: str = details.strip() if isinstance(details, str) else ""

    # Ein leerer Name ergibt `()` — es gibt nichts, was erst hier zu pruefen waere.
    return (name,) if name else ()


def _overlaps(appointment: Appointment, start: datetime, end: datetime) -> bool:
    """Ob ein Eintrag im Fenster `start` bis `end` liegt — ein Monat, wenn er es ueberlappt.

    Vorbedingung: alle Zeitpunkte zeitzonenbewusst.
    Nachbedingung: mit `month` wahr, wenn Monatsbeginn ≤ `end` und
        Folgemonat > `start`; sonst wahr, wenn `start` ≤ Zeitpunkt ≤ `end`.
    Fehlerfaelle: ein naiver Zeitpunkt wirft `ValueError` (aus `month_span`).
    """
    # ── Eingabe-Validierung ─────────────────────
    is_month: bool = appointment.precision == MONTH_PRECISION

    # ── Verarbeitung ────────────────────────────
    if is_month:
        first, following = month_span(appointment.moment)
        inside: bool = first <= end and following > start
    else:
        inside = start <= appointment.moment <= end

    # Die Rueckgabe ist ein Vergleich und damit ein Wahrheitswert — es gibt
    # nichts, was erst hier zu pruefen waere (Nachbedingung im Docstring).
    return inside


def fetch_rows(
    window: AppointmentWindow, user_id: str, character_id: str, postgres_url: str, now: datetime,
) -> list:
    """Liest die Zeilen des Fensters aus der Timeline des Paares, ohne Erinnerungs-Anker.

    Ein Termin gehoert dem Paar, bei dem er eingetragen wurde: Gelesen wird
    nur, was `user_id` mit `character_id` angelegt hat — eine andere Figur
    sieht die Termine des Menschen bei Nova nicht. Eine Vorgabe-Figur gibt es
    nicht.

    Eine Suche mit Richtung bekommt `now` mit: Die Abfrage grenzt
    *vergangen* dann so ab wie `to_appointment`, und kein Platz ihres `LIMIT`
    geht an einen Termin, den `read_appointments` danach verwirft.

    Vorbedingung: `window` ist gueltig (`graph/appointments.py`), `user_id`
        und `character_id` nicht leer, `now` zeitzonenbewusst in Ortszeit.
    Nachbedingung: die Zeilen, die das Repository fuer das Paar liefert —
        Ortszeit, aktiv, ohne `EXCLUDED_EVENT_TYPES`.
    Fehlerfaelle: leere `user_id` oder leere `character_id` wirft
        `ValueError`; ein Lesefehler geht unveraendert an den Aufrufer; eine
        Antwort, die keine Liste ist, wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        msg: str = "Termine lesen ohne user_id"
        raise ValueError(msg)
    if not character_id:
        msg = "Termine lesen ohne character_id"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    if window.kind == KIND_SEARCH:
        rows: object = TimelineRepository.find_by_keyword(
            postgres_url, user_id, character_id, window.keyword, window.direction, window.limit,
            exclude_event_types=EXCLUDED_EVENT_TYPES, now=now, timed_precisions=TIME_PRECISIONS,
        )
    else:
        rows = TimelineRepository.find_by_date_range(
            postgres_url, user_id, character_id, window.start, window.end,
            exclude_event_types=EXCLUDED_EVENT_TYPES,
        )

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(rows, list):
        msg = f"Timeline lieferte {type(rows).__name__} statt list"
        raise TypeError(msg)
    return rows


def to_appointment(row: object, now: datetime) -> Appointment | None:
    """Macht aus einer Timeline-Zeile einen Termin, oder verwirft sie laut.

    Vorbedingung: `now` ist zeitzonenbewusst in Ortszeit.
    Nachbedingung: ein `Appointment` mit Ortszeit und vorgerechnetem `past`
        — mit Uhrzeit (`precision` minute oder hour) vor `now`, mit `month`
        vor dem laufenden Monat, sonst vor dem heutigen Tag —, mit Typ,
        Genauigkeit und den Personen eines gekennzeichneten Eintrags. `None`
        fuer eine verworfene Zeile.
    Fehlerfaelle: eine Zeile, die kein dict ist, eine ohne ganzzahlige `id`,
        ein Erinnerungs-Anker, eine `event_time` ohne Zeitzone oder ein Titel,
        der kein Text ist — je laut gemeldet und verworfen. Ein Typ, der nicht
        in `EVENT_TYPES` steht, wird laut gemeldet und steht ohne
        Kennzeichnung da wie bisher: Ihn zu verwerfen liesse einen Termin
        verschwinden.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(row, dict):
        logger.error(f"Termine: Timeline-Zeile ohne dict-Form verworfen ({type(row).__name__})")
        return None
    row_id: object = row.get("id")
    if isinstance(row_id, bool) or not isinstance(row_id, int):
        logger.error(f"Termine: Timeline-Zeile ohne ganzzahlige id ({row_id!r}) — verworfen")
        return None
    if row.get("event_type") in EXCLUDED_EVENT_TYPES:
        logger.error(
            f"Termine: Erinnerungs-Anker id={row.get('id')} kam trotz Ausschluss in der "
            f"Abfrage an — verworfen, er ist kein Termin"
        )
        return None
    event_time: object = row.get("event_time")
    if not isinstance(event_time, datetime) or event_time.tzinfo is None:
        logger.error(
            f"Termine: Timeline-Zeile id={row.get('id')} ohne zeitzonenbewusste "
            f"event_time ({type(event_time).__name__}) — verworfen"
        )
        return None
    title: object = row.get("title")
    if not isinstance(title, str):
        logger.error(f"Termine: Timeline-Zeile id={row.get('id')} ohne Titel — verworfen")
        return None

    type_name: str = str(row.get("event_type") or "")
    kind: EventType | None = EVENT_TYPES.get(type_name)
    if kind is None:
        logger.error(
            f"Termine: Timeline-Zeile id={row_id} mit unbekanntem Typ {type_name!r} — "
            f"steht ohne Kennzeichnung"
        )

    # ── Verarbeitung ────────────────────────────
    moment: datetime = event_time.astimezone(now.tzinfo)
    precision: str = str(row.get("precision") or "")
    has_time: bool = precision in TIME_PRECISIONS
    if has_time:
        past: bool = moment < now
    elif precision == MONTH_PRECISION:
        past = (moment.year, moment.month) < (now.year, now.month)
    else:
        past = moment.date() < now.date()
    details: object = row.get("details")

    # ── Ausgabe-Verifikation ────────────────────
    appointment = Appointment(
        moment=moment, has_time=has_time, title=title.strip(),
        details=details.strip() if isinstance(details, str) else "", past=past,
        timeline_id=row_id, event_type=type_name, precision=precision,
        persons=_persons_of(row, kind),
    )
    if appointment.moment.tzinfo is None:
        msg: str = "to_appointment: Termin ohne Zeitzone nach der Umrechnung"
        raise RuntimeError(msg)
    return appointment


def read_appointments(
    window: AppointmentWindow, user_id: str, character_id: str, postgres_url: str, now: datetime,
) -> AppointmentReading:
    """Liest die Termine eines Fensters im Paar und bereitet sie fuer den Block auf.

    Bei `direction: forward` fehlen vergangene Termine (Fassung c); sonst
    stehen sie mit `past` da. Bei `backward` fehlen die kommenden — die
    Kopfzeile sagt dann *nur vergangene Termine*, und das muss stimmen.
    Sortiert nach Zeitpunkt.

    Vorbedingung: `now` zeitzonenbewusst in Ortszeit; `user_id` und
        `character_id` nicht leer.
    Nachbedingung: ein `AppointmentReading` mit `failed=False`, das nur
        Termine des Paares traegt, keine Erinnerungs-Anker.
    Fehlerfaelle: naiver Zeitpunkt oder ein unvollstaendiges Paar →
        `ValueError` (aus `fetch_rows`); ein Lesefehler geht an den
        Aufrufer (`read_after_route` macht daraus `failed`). Liefert die Abfrage
        mehr Zeilen als `limit` oder einen Termin ausserhalb von `start` bis
        `end` (ein Eintrag mit `month`: einen, dessen Monat das Fenster nicht
        ueberlappt), ist das ein Defekt der Abfrage: `RuntimeError`, beim Aufrufer
        wie ein Lesefehler. Jede gelesene Zeile,
        die nicht im Ergebnis steht — von der Ausgabe-Verifikation oder nach
        der Richtung verworfen —, zaehlt in `discarded` und im Log unter
        `verworfen`. Verwirft die Richtung bei einer Suche etwas, grenzen
        Abfrage und Leser *vergangen* verschieden ab: ERROR.
    """
    # ── Eingabe-Validierung ─────────────────────
    if now.tzinfo is None:
        msg: str = "read_appointments: Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    rows: list = fetch_rows(window, user_id, character_id, postgres_url, now)
    converted: list[Appointment | None] = [to_appointment(row, now) for row in rows]
    valid: list[Appointment] = [a for a in converted if a is not None]
    kept: list[Appointment] = valid
    if window.direction == DIRECTION_FORWARD:
        kept = [a for a in valid if not a.past]
    elif window.direction == DIRECTION_BACKWARD:
        kept = [a for a in valid if a.past]
    if window.kind == KIND_SEARCH and len(kept) != len(valid):
        logger.error(
            f"Termine: Suche richtung={window.direction} lieferte {len(valid) - len(kept)} "
            f"Termine der anderen Richtung — Abfrage und Leser grenzen vergangen verschieden ab"
        )
    kept.sort(key=lambda a: a.moment)
    discarded: int = len(rows) - len(kept)

    # ── Ausgabe-Verifikation ────────────────────
    # Geprueft wird gegen das Fenster, nicht gegen den Richtungsfilter oben:
    # Zeitraum und Obergrenze setzt die Abfrage, und nur sie kann sie verfehlen.
    reading = AppointmentReading(
        window=window, now=now, appointments=tuple(kept), discarded=discarded,
    )
    if window.kind == KIND_SEARCH and len(rows) > window.limit:
        msg = f"read_appointments: Suche lieferte {len(rows)} Zeilen bei limit={window.limit}"
        raise RuntimeError(msg)
    outside: list[Appointment] = [
        a for a in reading.appointments
        if window.start is not None and window.end is not None
        and not _overlaps(a, window.start, window.end)
    ]
    if outside:
        msg = (
            f"read_appointments: {len(outside)} Termine ausserhalb des Fensters "
            f"{window.start} bis {window.end}, erster {outside[0].moment}"
        )
        raise RuntimeError(msg)
    logger.info(
        f"Termine: art={window.kind}, richtung={window.direction}, gelesen={len(rows)}, "
        f"geliefert={len(reading.appointments)}, verworfen={discarded}"
    )
    return reading
