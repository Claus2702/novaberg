"""Ortszeit fuer Prompt und Pruefung — ein *heute*, das alle Knoten teilen.

`datetime.now()` ohne Zeitzone liefert im Behaelter UTC: Zwischen Mitternacht
Ortszeit und Mitternacht UTC haette ein Prompt den Vortag genannt, waehrend
eine Pruefung desselben Turns schon den neuen Tag kennt. `%A` gibt in der
Locale `C` ausserdem "Monday" statt "Montag". Beides loest diese Stelle einmal,
statt es in jedem Knoten zu wiederholen: Der Tag, den ein Prompt nennt, und der
Tag, gegen den geprueft wird, kommen aus derselben Funktion.
"""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from config import TIMEZONE
from utils.datum_pruefung import NAMEN


def now_local() -> datetime:
    """Liefert den aktuellen Zeitpunkt in der Zeitzone des Systems.

    Vorbedingung: `config.TIMEZONE` nennt eine bekannte IANA-Zone.
    Nachbedingung: Das Ergebnis traegt `tzinfo` dieser Zone.
    Fehlerfaelle: Eine unbekannte Zone wirft `ZoneInfoNotFoundError` — laut.
    """
    # ── Eingabe-Validierung ─────────────────────
    zone: ZoneInfo = ZoneInfo(TIMEZONE)

    # ── Verarbeitung ────────────────────────────
    now: datetime = datetime.now(zone)

    # ── Ausgabe-Verifikation ────────────────────
    if now.tzinfo is None:
        msg: str = "now_local: Zeitpunkt ohne Zeitzone"
        raise RuntimeError(msg)
    return now


def weekday_name(moment: date) -> str:
    """Liefert den deutschen Wochentagsnamen eines Datums oder Zeitpunkts.

    Der Name kommt aus der Tabelle und nicht aus `%A`: Ein Name aus einer
    Locale, die niemand gesetzt hat, ist keine Zusicherung.

    Vorbedingung: `moment` ist ein `date` oder `datetime`.
    Nachbedingung: einer der sieben Namen aus `NAMEN`.
    Fehlerfaelle: ein anderer Typ wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(moment, date):
        msg: str = f"weekday_name: date erwartet, nicht {type(moment).__name__}"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    name: str = NAMEN[moment.weekday()]

    # ── Ausgabe-Verifikation ────────────────────
    if name not in NAMEN:
        msg = f"weekday_name: unbekannter Name {name!r}"
        raise RuntimeError(msg)
    return name
