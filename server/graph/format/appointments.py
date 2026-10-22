"""Der Inhalt des `[TERMINE]`-Blocks: gelesener Zeitraum und je Termin eine Zeile.

**Warum der Bezug zu heute hier gerechnet wird und nicht im Modell.** Ein
Sprachmodell rechnet Wochentage und Abstaende unzuverlaessig, und ein
abgelaufener Termin wurde als kommender genannt. Hier steht deshalb je Termin
Wochentag, Datum und Uhrzeit in Ortszeit und der Abstand nach Kalendertagen:
*heute*, *morgen*, *in 3 Tagen*, *vor 9 Tagen*.

**Ein leerer Zeitraum steht ausdruecklich da.** Ein fehlender Block waere von
einem Turn ohne Leseweg nicht zu unterscheiden; *keine Termine vom ... bis
...* ist eine Aussage, die das Modell weitergeben kann.

**Ein Ereignis einer anderen Person ist kein Termin von Person B.** Es steht
nach den Terminen unter einer eigenen Kopfzeile und traegt die Kennzeichnung
seines Typs und die Person: *Ereignis (Lena): Umzug nach Kassel — November
2026*. Ist nur der Monat bekannt, steht der Monat und kein Tag, der Bezug zu
heute nach Monaten.
"""

from __future__ import annotations

from datetime import datetime

from graph.appointments import (
    DIRECTION_BACKWARD,
    DIRECTION_FORWARD,
    KIND_PROACTIVE,
    KIND_SEARCH,
    PROACTIVE_DAYS_AHEAD,
    PROACTIVE_DAYS_BACK,
    Appointment,
    AppointmentReading,
)
from memory.repositories.timeline_repository import MONTH_PRECISION
from memory.timeline_types import EVENT_TYPES
from utils.local_time import month_label, weekday_name

#: Der Satz fuer einen Turn, in dem die Timeline nicht gelesen wurde — er
#: nennt Termine und Ereignisse getrennt, wie der Block sie trennt.
FAILED_SENTENCE: str = (
    "Die Timeline konnte in diesem Turn nicht gelesen werden — ueber die Termine "
    "von Person B ist nichts bekannt, ebenso wenig ueber Ereignisse in ihrem Umfeld."
)

#: Die Kopfzeile ueber den Ereignissen anderer Personen.
EVENTS_HEADER: str = "Ereignisse im Umfeld von Person B — keine Termine von Person B:"


def relative_day(moment: datetime, now: datetime) -> str:
    """Der Abstand eines Termins zu heute, nach Kalendertagen in Ortszeit.

    Gerechnet in der Zone von `now`: Kurz nach Mitternacht Ortszeit ist der
    Vortag *vor 1 Tag*, auch wenn er in UTC noch derselbe Tag ist.

    Vorbedingung: beide Zeitpunkte zeitzonenbewusst; `now` in Ortszeit.
    Nachbedingung: *heute*, *morgen*, *in N Tagen*, *vor 1 Tag* oder
        *vor N Tagen*.
    Fehlerfaelle: ein naiver Zeitpunkt wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if moment.tzinfo is None or now.tzinfo is None:
        msg: str = "relative_day: Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    days: int = (moment.astimezone(now.tzinfo).date() - now.date()).days
    if days == 0:
        text: str = "heute"
    elif days == 1:
        text = "morgen"
    elif days > 1:
        text = f"in {days} Tagen"
    elif days == -1:
        text = "vor 1 Tag"
    else:
        text = f"vor {-days} Tagen"

    # ── Ausgabe-Verifikation ────────────────────
    if not text:
        msg = f"relative_day: kein Text fuer {days} Tage"
        raise RuntimeError(msg)
    return text


def date_label(moment: datetime) -> str:
    """Wochentag und Datum, etwa *Freitag, 16.10.2026*.

    Vorbedingung: `moment` ist ein Zeitpunkt in Ortszeit.
    Nachbedingung: deutscher Wochentag aus `weekday_name`, Datum TT.MM.JJJJ.
    Fehlerfaelle: ein anderer Typ wirft `TypeError` (aus `weekday_name`).
    """
    # ── Eingabe-Validierung ─────────────────────
    name: str = weekday_name(moment)

    # ── Verarbeitung ────────────────────────────
    label: str = f"{name}, {moment.strftime('%d.%m.%Y')}"

    # ── Ausgabe-Verifikation ────────────────────
    if not label.startswith(name):
        msg: str = f"date_label: {label!r} beginnt nicht mit dem Wochentag"
        raise RuntimeError(msg)
    return label


def appointment_line(appointment: Appointment, now: datetime) -> str:
    """Eine Zeile des Blocks: wann, was, und der Bezug zu heute.

    Form: ``- Freitag, 16.10.2026, 14:30 Uhr — Titel — Details (morgen)``.
    Ohne Uhrzeit steht *ohne Uhrzeit*, ein vergangener Termin traegt
    *(vergangen, vor 9 Tagen)*. Ein gekennzeichneter Eintrag — das Ereignis
    einer anderen Person — bekommt die Zeile von `event_line`: Jeder Leser,
    der diese Zeile setzt (Block, Suche, Angebot), nennt es so nie als Termin
    von Person B.

    Vorbedingung: `appointment.moment` und `now` in Ortszeit.
    Nachbedingung: eine Zeile, die mit ``- `` beginnt und mit dem Bezug in
        Klammern endet.
    Fehlerfaelle: ein naiver Zeitpunkt wirft `ValueError` (aus `relative_day`).
    """
    # ── Eingabe-Validierung ─────────────────────
    if is_marked(appointment):
        return event_line(appointment, now)
    relation: str = relative_day(appointment.moment, now)

    # ── Verarbeitung ────────────────────────────
    clock: str = (
        f"{appointment.moment.strftime('%H:%M')} Uhr" if appointment.has_time
        else "ohne Uhrzeit"
    )
    title: str = appointment.title or "(ohne Titel)"
    details: str = f" — {appointment.details}" if appointment.details else ""
    marker: str = f"vergangen, {relation}" if appointment.past else relation
    line: str = f"- {date_label(appointment.moment)}, {clock} — {title}{details} ({marker})"

    # ── Ausgabe-Verifikation ────────────────────
    if not line.endswith(f"({marker})"):
        msg: str = f"appointment_line: Zeile ohne Bezug zu heute: {line!r}"
        raise RuntimeError(msg)
    return line


def relative_month(moment: datetime, now: datetime) -> str:
    """Der Abstand eines Monats zu heute, nach Kalendermonaten in Ortszeit.

    Vorbedingung: beide Zeitpunkte zeitzonenbewusst; `now` in Ortszeit.
    Nachbedingung: *diesen Monat*, *naechsten Monat*, *in N Monaten*,
        *vor 1 Monat* oder *vor N Monaten*.
    Fehlerfaelle: ein naiver Zeitpunkt wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if moment.tzinfo is None or now.tzinfo is None:
        msg: str = "relative_month: Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    local: datetime = moment.astimezone(now.tzinfo)
    months: int = (local.year - now.year) * 12 + local.month - now.month
    if months == 0:
        text: str = "diesen Monat"
    elif months == 1:
        text = "naechsten Monat"
    elif months > 1:
        text = f"in {months} Monaten"
    elif months == -1:
        text = "vor 1 Monat"
    else:
        text = f"vor {-months} Monaten"

    # Die Fallunterscheidung ist vollstaendig und jeder Zweig setzt einen Text —
    # es gibt nichts, was erst hier zu pruefen waere (Nachbedingung im Docstring).
    return text


def is_marked(appointment: Appointment) -> bool:
    """Ob ein Eintrag gekennzeichnet steht — das Ereignis einer anderen Person.

    Vorbedingung: `appointment.event_type` ist ein Text.
    Nachbedingung: wahr, wenn der Typ in `EVENT_TYPES` eine Kennzeichnung
        traegt; ein unbekannter Typ meldet der Leser (`to_appointment`) und
        steht hier wie ein Termin. Ein gekennzeichneter Typ ist nie ein
        Termin des Menschen (`is_appointment` falsch).
    Fehlerfaelle: ein Typ, der kein Text ist, wirft `TypeError`; ein Typ mit
        Kennzeichnung, der zugleich als Termin gilt, wirft `RuntimeError` —
        die Typquelle widerspraeche sich, und der Block wuesste nicht, ob er
        ihn als Termin von Person B nennen darf.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(appointment.event_type, str):
        msg: str = f"is_marked: Typ ist kein Text ({appointment.event_type!r})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    kind = EVENT_TYPES.get(appointment.event_type)
    marked: bool = kind is not None and bool(kind.label)

    # ── Ausgabe-Verifikation ────────────────────
    if marked and kind.is_appointment:
        msg = (
            f"is_marked: Typ {appointment.event_type!r} traegt die Kennzeichnung "
            f"{kind.label!r} und gilt zugleich als Termin"
        )
        raise RuntimeError(msg)
    return marked


def event_line(appointment: Appointment, now: datetime) -> str:
    """Eine Zeile fuer das Ereignis einer anderen Person: Kennzeichnung, Person, was, wann.

    Form: ``- Ereignis (Lena): Umzug nach Kassel — November 2026 (naechsten
    Monat)``; mit Tag ``— Samstag, 14.11.2026 (in 9 Tagen)``, mit Uhrzeit
    dahinter ``, 10:00 Uhr``. Ohne Person entfaellt die Klammer. Ein
    vergangenes traegt *(vergangen, ...)*. `details` steht nicht da: Es traegt
    beim Ereignis die Person.

    Vorbedingung: `appointment` ist gekennzeichnet (`is_marked`); Zeitpunkte
        in Ortszeit.
    Nachbedingung: eine Zeile, die mit ``- <Kennzeichnung>`` beginnt und mit
        dem Bezug in Klammern endet — beides setzt der f-String selbst, die
        Kennzeichnung ist oben geprueft.
    Fehlerfaelle: ein Eintrag ohne Kennzeichnung wirft `ValueError` — er
        gehoert in `appointment_line`; ein naiver Zeitpunkt wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not is_marked(appointment):
        msg: str = f"event_line: Eintrag ohne Kennzeichnung ({appointment.event_type!r})"
        raise ValueError(msg)
    label: str = EVENT_TYPES[appointment.event_type].label

    # ── Verarbeitung ────────────────────────────
    if appointment.precision == MONTH_PRECISION:
        when: str = month_label(appointment.moment)
        relation: str = relative_month(appointment.moment, now)
    else:
        when = date_label(appointment.moment)
        if appointment.has_time:
            when = f"{when}, {appointment.moment.strftime('%H:%M')} Uhr"
        relation = relative_day(appointment.moment, now)
    persons: str = f" ({', '.join(appointment.persons)})" if appointment.persons else ""
    title: str = appointment.title or "(ohne Titel)"
    marker: str = f"vergangen, {relation}" if appointment.past else relation
    # Die Zeile ist die Verarbeitung selbst; Kennzeichnung und Bezug stehen per
    # Konstruktion an Anfang und Ende — es gibt nichts, was erst hier zu pruefen waere.
    return f"- {label}{persons}: {title} — {when} ({marker})"


def header_line(reading: AppointmentReading) -> str:
    """Die Kopfzeile: was gelesen wurde und warum.

    Vorbedingung: `reading` ist nicht `failed`; bei `range` und `proactive`
        tragen `start` und `end` den Zeitraum.
    Nachbedingung: ein Satz, der Zeitraum oder Suchbegriff nennt; bei einer
        unlesbaren Anfrage sagt er, dass nicht der gefragte Zeitraum dasteht.
    Fehlerfaelle: ein Fenster ohne Zeitraum ausserhalb einer Suche wirft
        `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    window = reading.window
    if window.kind != KIND_SEARCH and (window.start is None or window.end is None):
        msg: str = f"header_line: Fenster der Art {window.kind} ohne Zeitraum"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    only: str = {
        DIRECTION_FORWARD: " — nur kommende Termine",
        DIRECTION_BACKWARD: " — nur vergangene Termine",
    }.get(window.direction, "")
    if window.kind == KIND_SEARCH:
        header: str = (
            f"Gelesen: Suche nach \"{window.keyword}\" in den Titeln, "
            f"hoechstens {window.limit} Treffer{only}."
        )
    else:
        header = (
            f"Gelesen: Zeitraum {date_label(window.start)} bis {date_label(window.end)}{only}."
        )
    if window.kind == KIND_PROACTIVE:
        prefix: str = (
            "Die Frage nach Terminen liess sich keinem Zeitraum zuordnen. "
            if window.unusable_query else "Nach Terminen wurde nicht gezielt gefragt. "
        )
        header = (
            f"{prefix}{header[:-1]} (die letzten {PROACTIVE_DAYS_BACK} und die "
            f"naechsten {PROACTIVE_DAYS_AHEAD} Tage)."
        )

    # ── Ausgabe-Verifikation ────────────────────
    if "Gelesen:" not in header:
        msg = f"header_line: Kopfzeile ohne Angabe des Gelesenen: {header!r}"
        raise RuntimeError(msg)
    return header


def empty_line(reading: AppointmentReading) -> str:
    """Der Satz fuer einen Zeitraum oder eine Suche ohne Termin.

    Vorbedingung: `reading` traegt keine Termine und ist nicht `failed`.
    Nachbedingung: *keine Termine vom TT.MM.JJJJ bis TT.MM.JJJJ*, bei
        `forward` *keine kommenden Termine ...*, bei einer Suche
        *keine Termine zu "X"*.
    Fehlerfaelle: ein Fenster ohne Zeitraum ausserhalb einer Suche wirft
        `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    window = reading.window
    if window.kind != KIND_SEARCH and (window.start is None or window.end is None):
        msg: str = f"empty_line: Fenster der Art {window.kind} ohne Zeitraum"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    which: str = {
        DIRECTION_FORWARD: "keine kommenden Termine",
        DIRECTION_BACKWARD: "keine vergangenen Termine",
    }.get(window.direction, "keine Termine")
    if window.kind == KIND_SEARCH:
        line: str = f"{which} zu \"{window.keyword}\""
    else:
        line = (
            f"{which} vom {window.start.strftime('%d.%m.%Y')} "
            f"bis {window.end.strftime('%d.%m.%Y')}"
        )

    # ── Ausgabe-Verifikation ────────────────────
    if not line.startswith("keine "):
        msg = f"empty_line: {line!r} sagt nicht *keine*"
        raise RuntimeError(msg)
    return line


def appointments_body(reading: AppointmentReading) -> str:
    """Der ganze Inhalt des Blocks: Kopfzeile und Termine, oder *keine*; danach die Ereignisse.

    Die Termine von Person B und die Ereignisse anderer Personen stehen
    getrennt: zuerst die Termine (oder *keine Termine ...*, auch wenn es
    Ereignisse gibt — Person B hat dann keinen Termin), danach, nur wenn es
    welche gibt, `EVENTS_HEADER` und je Ereignis eine Zeile. Ohne Ereignis ist
    der Block derselbe wie vor der Kennzeichnung.

    Vorbedingung: `reading` ist das Leseergebnis dieses Turns.
    Nachbedingung: Bei `failed` der Ausfallsatz und kein *keine Termine*.
        Sonst die Kopfzeile und je Termin eine Zeile, oder ausdruecklich
        der Satz *keine Termine ...*; je Ereignis eine gekennzeichnete Zeile
        unter eigener Kopfzeile.
    Fehlerfaelle: siehe `header_line`, `empty_line`, `appointment_line`,
        `event_line`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if reading.failed:
        return FAILED_SENTENCE

    # ── Verarbeitung ────────────────────────────
    own: list[Appointment] = [a for a in reading.appointments if not is_marked(a)]
    events: list[Appointment] = [a for a in reading.appointments if is_marked(a)]
    lines: list[str] = [header_line(reading)]
    lines.extend(appointment_line(a, reading.now) for a in own)
    if not own:
        lines.append(empty_line(reading))
    if events:
        lines.append(EVENTS_HEADER)
        lines.extend(event_line(a, reading.now) for a in events)

    # ── Ausgabe-Verifikation ────────────────────
    expected: int = 1 + max(1, len(own)) + (1 + len(events) if events else 0)
    if len(lines) != expected:
        msg: str = (
            f"appointments_body: {len(lines)} Zeilen fuer {len(own)} Termine und "
            f"{len(events)} Ereignisse"
        )
        raise RuntimeError(msg)
    return "\n".join(lines)
