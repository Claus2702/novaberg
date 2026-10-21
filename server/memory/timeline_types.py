"""Die Typen eines Timeline-Eintrags — eine Quelle fuer alle Leser.

Ein Typ traegt sein Verhalten: ob er bindet, ob er erinnert, ob er gegen
andere Eintraege geprueft wird, ob er ein Termin des Menschen ist, wie er im
Block der Termine gekennzeichnet wird und mit welcher Zeile ihn die
Klassifikation kennt. Bis hierher stand jede dieser Listen an einer eigenen
Stelle, und sie liefen auseinander.

Die Leser: die Klassifikation des Timeline-Agenten (`CLASSIFIABLE`, die Zeilen
des Prompts), die Merkmale beim Anlegen (`agents/timeline/magneten.py`), die
Duplikatpruefung und der Bestandsabgleich (`NOT_APPOINTMENTS`), der
Erinnerungs-Anker der KZG (`ANCHOR_TYPE`). Die UPDATEs der Schemadatei
(`agents/timeline/init.sql`) koennen diese Tabelle nicht lesen; ein Zeuge
haelt sie gegen sie.

Das Modul oeffnet nichts und importiert nichts aus dem Projekt: Es darf von
jeder Schicht gelesen werden, ohne beim Import eine Verbindung zu laden.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger("ki_server.memory.timeline_types")


@dataclass(frozen=True)
class EventType:
    """Das Verhalten eines Typs.

    `binding`, `remind` und `conflict_check` sind die Merkmale, die beim
    Anlegen in die Zeile gehen. `is_appointment` sagt, ob der Eintrag ein
    Termin des Menschen ist — nur dann ist er Partner der Duplikatpruefung und
    des Bestandsabgleichs. `label` kennzeichnet den Eintrag im Block der
    Termine (leer: ein gewoehnlicher Termin). `prompt_line` beschreibt den Typ
    fuer die Klassifikation; leer heisst, die Klassifikation vergibt ihn nicht.
    """

    binding: bool
    remind: bool
    conflict_check: bool
    is_appointment: bool
    label: str
    prompt_line: str


#: Der Typ, den die KZG einem Erinnerungs-Anker gibt — ein Merkposten des
#: Gedaechtnisses, kein Termin des Menschen.
ANCHOR_TYPE: str = "erinnerungs_anker"

#: Der Typ fuer das Ereignis einer anderen Person: Es erinnert nicht, bindet
#: nicht und ist kein Termin des Menschen.
OCCURRENCE_TYPE: str = "ereignis"

#: Die Tabelle der Typen. Die Reihenfolge ist die des Prompts.
EVENT_TYPES: dict[str, EventType] = {
    "termin": EventType(
        binding=True, remind=True, conflict_check=True, is_appointment=True,
        label="", prompt_line="Arzttermin, Meeting, Verabredung (Standard)",
    ),
    "geburtstag": EventType(
        binding=False, remind=True, conflict_check=False, is_appointment=True,
        label="", prompt_line="Geburtstage",
    ),
    "deadline": EventType(
        binding=True, remind=True, conflict_check=True, is_appointment=True,
        label="", prompt_line="Abgabetermine, Fristen",
    ),
    "jahrestag": EventType(
        binding=False, remind=True, conflict_check=False, is_appointment=True,
        label="", prompt_line="Wiederkehrende jaehrliche Ereignisse",
    ),
    "erinnerung": EventType(
        binding=False, remind=True, conflict_check=False, is_appointment=True,
        label="", prompt_line="Allgemeine Erinnerungen",
    ),
    ANCHOR_TYPE: EventType(
        binding=False, remind=False, conflict_check=False, is_appointment=False,
        label="", prompt_line="",
    ),
    OCCURRENCE_TYPE: EventType(
        binding=False, remind=False, conflict_check=False, is_appointment=False,
        label="Ereignis", prompt_line="",
    ),
}

#: Die Typen, die die Klassifikation des Timeline-Agenten vergibt — ohne den
#: Anker und ohne das Ereignis, in der Reihenfolge des Prompts.
CLASSIFIABLE: tuple[str, ...] = tuple(
    name for name in EVENT_TYPES if name not in (ANCHOR_TYPE, OCCURRENCE_TYPE)
)

#: Die Typen, die kein Termin des Menschen sind: kein Duplikat eines neuen
#: Termins, kein Treffer im Bestandsabgleich.
NOT_APPOINTMENTS: frozenset[str] = frozenset(
    name for name, kind in EVENT_TYPES.items() if not kind.is_appointment
)

#: Wie lange nach einem erinnernden Eintrag die Wiedervorlage faellig wird.
RESUBMISSION_DELAY: timedelta = timedelta(days=7)


def event_type(name: str) -> EventType:
    """Das Verhalten eines Typs aus der Tabelle.

    Vorbedingung: `name` ist ein Text.
    Nachbedingung: der Eintrag von `EVENT_TYPES` fuer `name`.
    Fehlerfaelle: ein Typ, der nicht in der Tabelle steht, wirft `ValueError`
        — ein Eintrag mit unbekanntem Typ bekaeme sonst Merkmale, die niemand
        fuer ihn entschieden hat.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(name, str):
        msg: str = f"event_type: Typ ist kein Text ({type(name).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    kind: EventType | None = EVENT_TYPES.get(name)

    # ── Ausgabe-Verifikation ────────────────────
    if kind is None:
        logger.error(f"event_type: unbekannter Typ '{name}' — bekannt sind {sorted(EVENT_TYPES)}")
        msg = f"unbekannter Timeline-Typ: {name!r}"
        raise ValueError(msg)
    return kind


def resubmission_at(remind: bool, event_time: datetime) -> datetime | None:
    """Die Wiedervorlage, die ein neuer Eintrag bekommt.

    Ein erinnernder Eintrag wird eine Woche nach seinem Zeitpunkt wieder
    vorgelegt; einer, der nicht erinnert — der Anker, das Ereignis einer
    anderen Person —, bekommt keine. Jeder Aufrufer von
    `TimelineRepository.insert` gibt den Wert damit selbst vor; das
    Repository setzt keinen.

    Vorbedingung: `remind` ist ein Wahrheitswert, `event_time` ein Zeitpunkt.
    Nachbedingung: `event_time + RESUBMISSION_DELAY` bei `remind`, sonst
        `None`.
    Fehlerfaelle: ein anderer Typ als `bool` oder `datetime` wirft
        `TypeError` — ein Text als `remind` gaelte sonst immer als wahr.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(remind, bool):
        msg: str = f"resubmission_at: remind ist kein bool ({type(remind).__name__})"
        raise TypeError(msg)
    if not isinstance(event_time, datetime):
        msg = f"resubmission_at: event_time ist kein datetime ({type(event_time).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    due: datetime | None = event_time + RESUBMISSION_DELAY if remind else None

    # ── Ausgabe-Verifikation ────────────────────
    if due is not None and due <= event_time:
        msg = f"resubmission_at: Wiedervorlage {due} nicht nach dem Zeitpunkt {event_time}"
        raise RuntimeError(msg)
    return due
