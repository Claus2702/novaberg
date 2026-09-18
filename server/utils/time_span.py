"""Das Ende einer Zeitspanne — fuer Termine mit Anfang und Ende.

**Warum es das gibt** (Scheibe 12 D): Die Timeline fuehrt die Spalte
`event_ende`, und die Absicht des Eigentuemers (14.09.2026) nennt ausdruecklich
*"Zeitraeume mit Bezug zu einem Start oder Endzeitpunkt"*. Geschrieben wurde die
Spalte nie; der Zeitparser kennt Zeitpunkte, keine Spannen.

**Warum ein eigener Baustein und nicht der Zeitparser:** Der Parser ist gross
und gegen eine eigene Pruefreihe gehalten. Das Ende einer Spanne ist eine
kleinere Frage mit einer eigenen Wache — es muss **nach** dem Anfang liegen.
Damit bleibt eine Frist ohne Ende: In *"das Buch bis Freitag abgeben"* ist
Freitag der Zeitpunkt selbst, und ein Ende am selben Freitag ist keines.

Erkannte Formen: *"von 10 bis 12 Uhr"*, *"10–12 Uhr"*, *"bis 16 Uhr"*,
*"vom 3. bis 5. Oktober"*, *"bis Freitag"*, *"fuer zwei Stunden"*,
*"drei Stunden lang"*. Alles andere ergibt kein Ende — geraten wird nichts.
"""

import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger("ki_server.time_span")

_ZAHLWORTE: dict[str, float] = {
    "eine": 1, "einer": 1, "ein": 1, "eineinhalb": 1.5, "anderthalb": 1.5,
    "zwei": 2, "drei": 3, "vier": 4, "fuenf": 5, "fünf": 5, "sechs": 6, "halbe": 0.5,
}
_UHRZEIT_BIS: re.Pattern = re.compile(
    r"(?:\b(?:von\s+)?(\d{1,2})(?::(\d{2}))?\s*(?:uhr\s*)?)?(?:bis|–|-)\s*(\d{1,2})(?::(\d{2}))?\s*uhr",
    re.IGNORECASE,
)
# Eine Dauer ist nur dann die Laenge des Termins, wenn sie so gesagt ist:
# "fuer zwei Stunden", "drei Stunden lang". `[zweite Kontrolle 18.09.2026]`
# Ohne diese Bindung wurde "erinnere mich eine Stunde vorher" oder "die Anfahrt
# dauert zwei Stunden" zum Ende, und "1 1/2 Stunden" las sich als 2 Stunden.
_DAUER: re.Pattern = re.compile(
    r"\b(?P<fuer>fuer\s+|für\s+)?(?P<zahl>\d+\s+1/2|\d+(?:[.,]\d+)?|" + "|".join(_ZAHLWORTE)
    + r")\s+(?P<einheit>stunden?|minuten?)(?P<lang>\s+lang)?\b",
    re.IGNORECASE,
)
_VOM_BIS_MONAT: re.Pattern = re.compile(r"\bvom\s+(\d{1,2})\.?\s+bis\s+\d{1,2}\.?\s+([a-zäöü]+)", re.IGNORECASE)
_BIS_TAG: re.Pattern = re.compile(r"\bbis\s+(?:zum\s+|zur\s+)?(.+)$", re.IGNORECASE)


def span_end(expression: str, start: datetime, strict: bool = False) -> datetime | None:
    """Das Ende der Spanne, die `expression` nennt, oder None.

    `strict` gilt fuer die ganze Aeusserung statt fuer den Zeitausdruck: Dann
    zaehlen nur ausdrueckliche Spannen mit beiden Enden (*"von 10 bis 12 Uhr"*,
    *"10–12 Uhr"*, *"vom 3. bis 5. Oktober"*) und die gebundene Dauer — nicht
    *"bis 19 Uhr"*, denn *"die Praxis hat bis 19 Uhr offen"* ist kein Ende des
    Termins (zweite Kontrolle, 18.09.2026).

    Vorbedingung: `start` ist der aufgeloeste Anfang (mit Zeitzone).
    Nachbedingung: ein Zeitpunkt **nach** `start` in dessen Zeitzone, oder
        None, wenn der Ausdruck keine Spanne traegt. Ein Ende, das nicht nach
        dem Anfang liegt, ist keins (Frist statt Spanne) und wird gemeldet.
    Fehlerfaelle: keine Ausnahme.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(expression, str) or not expression.strip() or not isinstance(start, datetime):
        return None
    text: str = expression.strip()

    # ── Verarbeitung ────────────────────────────
    ende: datetime | None = None
    if (m := _UHRZEIT_BIS.search(text)) is not None and (not strict or m.group(1)):
        stunde, minute = int(m.group(3)), int(m.group(4) or 0)
        if 0 <= stunde <= 23 and 0 <= minute <= 59:
            ende = start.replace(hour=stunde, minute=minute, second=0, microsecond=0)
    elif (m := _DAUER.search(text)) is not None and (m.group("fuer") or m.group("lang")):
        roh: str = m.group("zahl").casefold().replace(",", ".")
        if "1/2" in roh:
            menge: float = float(roh.split()[0]) + 0.5
        else:
            menge = _ZAHLWORTE.get(roh) or float(roh)
        einheit = timedelta(hours=menge) if m.group("einheit").casefold().startswith("stunde") else timedelta(minutes=menge)
        ende = start + einheit
    elif strict and not _VOM_BIS_MONAT.search(text):
        return None
    elif (m := _BIS_TAG.search(text)) is not None:
        from utils.zeitparser import zeit_parsen_vektor
        vektor = zeit_parsen_vektor(m.group(1))
        # `tag_erkannt` ist bei "5. Oktober" falsch gesetzt (der Parser meldet
        # das Datum, aber nicht die Erkennung) — das Datum selbst entscheidet.
        if vektor.datum is not None:
            tag = vektor.datum.astimezone(start.tzinfo) if start.tzinfo else vektor.datum
            ende = tag if vektor.uhrzeit_erkannt else tag.replace(hour=23, minute=59, second=0, microsecond=0)

    # ── Ausgabe-Verifikation ────────────────────
    if ende is None:
        return None
    if ende <= start:
        logger.info("Zeitspanne: Ende %s liegt nicht nach dem Anfang %s — keine Spanne (Frist?)", ende, start)
        return None
    return ende


_ENDE_UHRZEIT: re.Pattern = re.compile(r"\s*(?:bis|–|-)\s*\d{1,2}(?::\d{2})?\s*uhr\b", re.IGNORECASE)
_VON_VOR_ZAHL: re.Pattern = re.compile(r"\bvon\s+(?=\d)", re.IGNORECASE)


def span_start_text(expression: str) -> str:
    """Der Ausdruck ohne den Endteil einer Spanne — fuer das Parsen des Anfangs.

    `[gemessen 18.09.2026]` Der Zeitparser liefert fuer *"19.09.2026 von 10 bis
    12 Uhr"* kein Datum; ein Auftrag mit Spanne scheiterte damit ganz (*"Konnte
    kein Datum erkennen"*). Ohne den Endteil — *"19.09.2026 10 Uhr"* — loest er
    auf.

    Nachbedingung: *"von 10 bis 12 Uhr"* → *"10 Uhr"*, *"vom 3. bis 5.
    Oktober"* → *"3. Oktober"*; ein Ausdruck ohne Spanne bleibt unveraendert.
    """
    if not isinstance(expression, str):
        return ""
    text: str = _VOM_BIS_MONAT.sub(r"\1. \2", expression)
    if _ENDE_UHRZEIT.search(text):
        text = _ENDE_UHRZEIT.sub(" Uhr", text)
        text = _VON_VOR_ZAHL.sub("", text)
    return " ".join(text.split())
