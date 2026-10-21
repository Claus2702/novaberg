"""Leseweg des Bestandsabgleichs: die Termine des Menschen zu einem Zeitpunkt.

Gefragt vom Riegel der Speicherbehauptung (`graph/nodes/tribunal.py`), bevor
er korrigiert: Steht zu Tag und Uhrzeit des akuten Objekts ein Termin in der
Timeline, wiederholt die Antwort eine echte Schreibung.

**Warum nicht `agents/timeline/suche.py::find_duplicates`:** Dort zaehlt ein
gemeinsames Wort des Titels am selben Tag, hier zaehlen Tag und Uhrzeit, und
der Titel ist unbekannt. Und `find_duplicates` macht aus einem Lesefehler
*keine Duplikate*, weil das Anlegen dann eher doppelt als gar nicht schreibt —
fuer den Abgleich waere dieselbe Uebersetzung still: Ein gebrochener Zugriff
saehe aus wie ein leerer Bestand. Hier geht der Lesefehler an den Aufrufer.

**Warum nicht unter `agents/`:** Jeder Import aus dem Paket `agents` laedt
`agents.base` und damit den Verbindungspool der Datenbank beim Import. Der
Riegel laeuft im Graphen und soll beim Laden keine Verbindung oeffnen.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import POSTGRES_URL, TIMEZONE
from memory.repositories.timeline_repository import TimelineRepository
from memory.timeline_types import ANCHOR_TYPE, NOT_APPOINTMENTS

logger = logging.getLogger("ki_server.memory.timeline_inventory")

#: Die Genauigkeiten eines Timeline-Eintrags, die eine Uhrzeit tragen — dieselbe
#: Menge wie `agents/timeline/event_time.py::_TIME_PRECISION`, hier gefuehrt aus
#: dem Grund im Kopf dieser Datei. Ein Zeuge haelt die Kopie gegen ihre Quelle
#: (`tests/test_storage_inventory.py`, `CopiesBoundToSourceTest`).
TIME_PRECISIONS: frozenset[str] = frozenset({"minute", "hour"})

#: Der Typ des Erinnerungs-Ankers kommt aus der Typquelle
#: (`memory/timeline_types.py`) und wird hier fuer die bestehenden Leser
#: weitergereicht.
__all__: list[str] = ["ANCHOR_TYPE", "TIME_PRECISIONS", "find_at_moment", "is_appointment_at"]


def is_appointment_at(row: dict, moment: datetime) -> bool:
    """Ist die Zeile ein Termin des Menschen genau zu diesem Zeitpunkt?

    Gezaehlt werden Tag, Stunde und Minute in der lokalen Zeit. **Ohne
    Toleranz:** Beide Seiten kommen aus demselben Zeitparser, der jede
    Uhrzeitform auf Stunde und Minute bringt; eine Abweichung um eine halbe
    Stunde ist eine andere Behauptung. Mit Toleranz ginge *„10:30 ist
    eingetragen"* gegen einen Termin um 10:00 unkorrigiert hinaus.

    Vorbedingung: `row` ist eine Zeile von `TimelineRepository` (lokale,
        zeitzonenbewusste `event_time`), `moment` zeitzonenbewusst.
    Nachbedingung: wahr genau dann, wenn die Zeile aktiv ist, ein Termin des
        Menschen (kein Typ aus `NOT_APPOINTMENTS` — weder Erinnerungs-Anker
        noch Ereignis einer anderen Person), ihre Zeit eine Uhrzeit traegt
        (`precision` minute oder hour) und Tag, Stunde und Minute mit
        `moment` uebereinstimmen.
    Fehlerfaelle: eine Zeile ohne zeitzonenbewusste `event_time` ist defekt —
        laut gemeldet, kein Treffer.
    """
    # ── Eingabe-Validierung ─────────────────────
    event_time: object = row.get("event_time")
    if not isinstance(event_time, datetime) or event_time.tzinfo is None:
        logger.error(
            f"Bestandsabgleich: Timeline-Zeile id={row.get('id')} ohne "
            f"zeitzonenbewusste event_time ({type(event_time).__name__}) — kein Treffer"
        )
        return False

    # ── Verarbeitung ────────────────────────────
    tz = ZoneInfo(TIMEZONE)
    local: datetime = event_time.astimezone(tz)
    wanted: datetime = moment.astimezone(tz)
    same_minute: bool = (
        local.date() == wanted.date()
        and (local.hour, local.minute) == (wanted.hour, wanted.minute)
    )

    # Die Rueckgabe ist die Verarbeitung selbst; die Eingabe ist oben geprueft, und `astimezone`
    # liefert immer eine zeitzonenbewusste Zeit — es gibt nichts, was erst hier zu pruefen waere.
    return (
        row.get("aktiv") is True
        and row.get("event_type") not in NOT_APPOINTMENTS
        and str(row.get("precision") or "") in TIME_PRECISIONS
        and same_minute
    )


def find_at_moment(user_id: str, character_id: str, moment: datetime) -> list[dict]:
    """Die Termine des Paares genau zu einem Zeitpunkt.

    Gelesen wird der lokale Tag von `moment` ueber
    `TimelineRepository.find_by_date_range`; die Auswahl trifft
    `is_appointment_at` in Python, damit sie ohne Datenbank bezeugbar ist.
    Ein Termin, den der Mensch bei einer anderen Figur eingetragen hat, deckt
    keine Behauptung dieser Figur.

    Vorbedingung: `user_id` und `character_id` nicht leer; `moment`
        zeitzonenbewusst.
    Nachbedingung: die Zeilen des Paares an diesem Tag, fuer die
        `is_appointment_at` gilt — leer, wenn keine.
    Fehlerfaelle: leere `user_id`, leere `character_id` oder naiver `moment`
        → `ValueError`; ein Lesefehler des Bestands geht unveraendert an den
        Aufrufer; eine Antwort, die keine Liste ist → `TypeError`. Gefangen
        wird beim Aufrufer, der mit der Korrektur kompensiert. Eine Zeile, die
        kein dict ist, wird laut gemeldet und verworfen — sie ist kein Treffer.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        raise ValueError("Bestandsabgleich ohne user_id")
    if not character_id:
        msg: str = "Bestandsabgleich ohne character_id"
        raise ValueError(msg)
    if moment.tzinfo is None:
        raise ValueError("Bestandsabgleich mit naivem Zeitpunkt")

    # ── Verarbeitung ────────────────────────────
    local_moment: datetime = moment.astimezone(ZoneInfo(TIMEZONE))
    day_start: datetime = local_moment.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end: datetime = day_start + timedelta(days=1) - timedelta(seconds=1)
    day_rows: object = TimelineRepository.find_by_date_range(
        POSTGRES_URL, user_id, character_id, day_start, day_end
    )

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(day_rows, list):
        raise TypeError(f"Bestand lieferte {type(day_rows).__name__} statt list")
    rows: list[dict] = [r for r in day_rows if isinstance(r, dict)]
    if len(rows) != len(day_rows):
        logger.error(
            f"Bestandsabgleich: {len(day_rows) - len(rows)} Timeline-Zeile(n) "
            f"ohne dict-Form verworfen — kein Treffer"
        )
    return [r for r in rows if is_appointment_at(r, local_moment)]
