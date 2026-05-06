"""EventTime — Wertobjekt für Timeline-Zeitwerte mit variabler Präzision.

Trägt intern immer einen vollen datetime, formatiert nach außen abhängig
von precision. Liefert Range-Anfang und Range-Ende für Such-Queries.

Konvention für die Speicherung: timestamp ist immer der ANFANG des Bereichs,
den die Präzision beschreibt. Beispiele:
    "im Mai 2026"        → timestamp=2026-05-01 00:00, precision="month"
    "2. Quartal 2026"    → timestamp=2026-04-01 00:00, precision="quarter"
    "morgen um 10 Uhr"   → timestamp=2026-05-06 10:00, precision="minute"
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import getLogger

_log = getLogger(__name__)

_TIME_PRECISION = {"minute", "hour"}
_VALID_PRECISIONS = {"minute", "hour", "day", "month", "quarter", "year"}

_MONATSNAMEN = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


def _add_months(dt: datetime, months: int) -> datetime:
    """Addiert Monate zu einem datetime, mit Jahr-Überlauf."""
    neuer_monat = dt.month - 1 + months
    neues_jahr = dt.year + neuer_monat // 12
    neuer_monat = neuer_monat % 12 + 1
    return dt.replace(year=neues_jahr, month=neuer_monat)


@dataclass(frozen=True)
class EventTime:
    """Zeitwert mit variabler Präzision für Timeline-Einträge."""
    timestamp: datetime
    precision: str

    def __post_init__(self) -> None:
        if self.precision not in _VALID_PRECISIONS:
            _log.warning(
                "EventTime mit unbekannter precision %r — fallback auf 'day'",
                self.precision,
            )

    def has_time(self) -> bool:
        """True wenn die Präzision eine Uhrzeit umfasst."""
        return self.precision in _TIME_PRECISION

    def range_anfang(self) -> datetime:
        """Inklusiver Anfang des Bereichs."""
        return self.timestamp

    def range_ende(self) -> datetime:
        """Exklusives Ende des Bereichs."""
        if self.precision == "minute":
            return self.timestamp + timedelta(minutes=1)
        if self.precision == "hour":
            return self.timestamp + timedelta(hours=1)
        if self.precision == "day":
            return self.timestamp + timedelta(days=1)
        if self.precision == "month":
            return _add_months(self.timestamp, 1)
        if self.precision == "quarter":
            return _add_months(self.timestamp, 3)
        if self.precision == "year":
            return self.timestamp.replace(year=self.timestamp.year + 1)
        return self.timestamp + timedelta(days=1)

    def format_anzeige(self) -> str:
        """Formatiert den Wert für die Anzeige gemäß precision."""
        if self.precision in _TIME_PRECISION:
            return self.timestamp.strftime("%d.%m.%Y, %H:%M")
        if self.precision == "month":
            monatsname = _MONATSNAMEN[self.timestamp.month - 1]
            return f"{monatsname} {self.timestamp.year}"
        if self.precision == "quarter":
            quartal = (self.timestamp.month - 1) // 3 + 1
            return f"Q{quartal} {self.timestamp.year}"
        if self.precision == "year":
            return str(self.timestamp.year)
        return self.timestamp.strftime("%d.%m.%Y")


def precision_has_time(precision: str) -> bool:
    """Modul-Helper für Stellen, die nur den Boolean brauchen."""
    return precision in _TIME_PRECISION


def precision_format(timestamp: datetime, precision: str) -> str:
    """Modul-Helper für Stellen, die Datum+precision direkt formatieren."""
    return EventTime(timestamp=timestamp, precision=precision).format_anzeige()
