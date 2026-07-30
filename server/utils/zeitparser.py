"""
Zeitparser -- Loest natuerlichsprachliche Zeitausdruecke in datetime auf.

Dreistufig:
1. Fuzzy-Korrektur: Tippfehler in Wochentagen/Monaten erkennen
2. dateparser: Deutschsprachige relative/absolute Ausdruecke aufloesen
3. Plausibilitaets-Check: Ergebnis im sinnvollen Fenster?

Prinzip: LLM extrahiert den Zeitausdruck als String,
Python loest ihn deterministisch auf.
"""

import logging
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import dateparser

from config import TIMEZONE

logger = logging.getLogger("ki_server.zeitparser")


@dataclass
class ZeitVektor:
    """Ergebnis des Vektor-Parsings: Was wurde erkannt?"""
    datum: Optional[datetime]
    tag_erkannt: bool
    uhrzeit_erkannt: bool
    referenz_modus: str  # "absolut" | "relativ" | "relativ_rueckwaerts"

# Deutsche Wochentage und Monate fuer Fuzzy-Matching
_WOCHENTAGE: list[str] = [
    "montag", "dienstag", "mittwoch", "donnerstag",
    "freitag", "samstag", "sonntag",
]

_MONATE: list[str] = [
    "januar", "februar", "maerz", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "dezember",
]

_RELATIVE: list[str] = [
    "morgen", "uebermorgen", "übermorgen", "heute", "gestern", "vorgestern",
]

_ALLE_WOERTER: list[str] = _WOCHENTAGE + _MONATE + _RELATIVE

_GESCHUETZTE_WOERTER: set[str] = {
    "morgens", "vormittags", "mittags", "nachmittags",
    "abends", "abend", "nachts", "früh",
    "eins", "zwei", "drei", "vier", "fünf",
    "sechs", "sieben", "acht", "neun", "zehn",
    "elf", "zwölf", "halb", "viertel", "dreiviertel",
    "vor", "nach", "um", "am", "in", "an",
}


def _levenshtein(a: str, b: str) -> int:
    """Levenshtein-Distanz zwischen zwei Strings."""
    if len(a) < len(b):
        return _levenshtein(b, a)
    if len(b) == 0:
        return len(a)

    vorherige: list[int] = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        aktuelle: list[int] = [i + 1]
        for j, cb in enumerate(b):
            einfuegen: int = vorherige[j + 1] + 1
            loeschen: int = aktuelle[j] + 1
            ersetzen: int = vorherige[j] + (0 if ca == cb else 1)
            aktuelle.append(min(einfuegen, loeschen, ersetzen))
        vorherige = aktuelle

    return vorherige[-1]


def _fuzzy_korrektur(text: str, max_distanz: int = 2) -> str:
    """
    Korrigiert Tippfehler in Wochentagen und Monaten.

    'Frietag' -> 'Freitag' (Distanz 1)
    'Donerstag' -> 'Donnerstag' (Distanz 1)
    'Septmeber' -> 'September' (Distanz 2)
    """
    woerter: list[str] = text.split()
    korrigiert: list[str] = []

    for wort in woerter:
        if len(wort) <= 2:
            korrigiert.append(wort)
            continue
        wort_lower: str = wort.lower()
        if wort_lower in _GESCHUETZTE_WOERTER:
            korrigiert.append(wort)
            continue
        if wort_lower in _ALLE_WOERTER:
            korrigiert.append(wort)
            continue
        bester_match: Optional[str] = None
        beste_distanz: int = max_distanz + 1

        for kandidat in _ALLE_WOERTER:
            distanz: int = _levenshtein(wort_lower, kandidat)
            if 0 < distanz <= max_distanz and distanz < beste_distanz:
                beste_distanz = distanz
                bester_match = kandidat

        if bester_match and beste_distanz <= max_distanz:
            korrigiertes_wort: str = (
                bester_match.capitalize() if wort[0].isupper() else bester_match
            )
            logger.info(
                f"Zeitparser: '{wort}' -> '{korrigiertes_wort}' "
                f"(Distanz {beste_distanz})"
            )
            korrigiert.append(korrigiertes_wort)
        else:
            korrigiert.append(wort)

    return " ".join(korrigiert)


_ZAHLWOERTER: dict[str, int] = {
    "eins": 1, "ein": 1, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5,
    "sechs": 6, "sieben": 7, "acht": 8, "neun": 9, "zehn": 10,
    "elf": 11, "zwölf": 12,
}

_ZAHLWOERTER_PATTERN: str = "|".join(_ZAHLWOERTER.keys())

_TAGESZEITEN: dict[str, int] = {
    "morgens": 0,
    "früh": 0,
    "vormittags": 0,
    "mittags": 12,
    "nachmittags": 12,
    "abends": 12,
    "nachts": 0,
}

_TAGESZEIT_UHRZEITEN: dict[str, str] = {
    "früh": "06:00",
    "morgens": "08:00",
    "vormittags": "10:00",
    "mittags": "12:00",
    "nachmittags": "15:00",
    "abends": "18:00",
    "Abend": "18:00",
    "nachts": "22:00",
}


def _text_normalisieren(text: str) -> tuple[str, bool]:
    """
    Normalisiert deutsche Zeitausdruecke fuer dateparser-Kompatibilitaet.

    Returns:
        (normalisierter_text, hat_uebernachst)
    """
    ergebnis: str = text
    tageszeit_woerter: str = "|".join(_TAGESZEITEN.keys())

    # ── Tageszeit extrahieren (Fallback fuer spaeter) ──
    # NUR wenn das Wort NICHT direkt nach "Uhr" steht
    gemerkte_uhrzeit: str = ""
    for wort, uhrzeit in _TAGESZEIT_UHRZEITEN.items():
        if re.search(r'(?<![Uu]hr\s)\b' + wort + r'\b', ergebnis, flags=re.IGNORECASE):
            gemerkte_uhrzeit = uhrzeit
            ergebnis = re.sub(
                r'(?<![Uu]hr\s)\s*\b' + wort + r'\b\s*', ' ',
                ergebnis, flags=re.IGNORECASE,
            ).strip()
            logger.debug(
                f"Zeitparser: Tageszeit '{wort}' extrahiert, "
                f"Fallback-Uhrzeit {uhrzeit}"
            )
            break

    # ── 0. "am" entfernen — verwirrt dateparser bei deutschen Zeitausdruecken ──
    ergebnis = re.sub(r'\b[Aa]m\s+', '', ergebnis)

    # ── 0b. Relative Tage in konkrete ISO-Daten umrechnen ──
    _RELATIVE_TAGE: dict[str, int] = {
        "heute": 0,
        "morgen": 1,
        "übermorgen": 2,
        "uebermorgen": 2,
        "vorgestern": -2,
        "gestern": -1,
    }

    for wort, offset in _RELATIVE_TAGE.items():
        if re.search(r'\b' + wort + r'\b', ergebnis, flags=re.IGNORECASE):
            konkretes_datum: str = (date.today() + timedelta(days=offset)).isoformat()
            ergebnis = re.sub(
                r'\b' + wort + r'\b',
                konkretes_datum,
                ergebnis,
                flags=re.IGNORECASE,
            )

    # ── 0c. Deutsches Datum ohne Jahr: "01.07." oder "15.04." -> "01.07.2026" ──
    aktuelles_jahr: str = str(date.today().year)

    ergebnis = re.sub(
        r'\b(\d{1,2}\.\d{1,2})\.\s',
        r'\1.' + aktuelles_jahr + ' ',
        ergebnis,
    )
    ergebnis = re.sub(
        r'\b(\d{1,2}\.\d{1,2})\.$',
        r'\1.' + aktuelles_jahr,
        ergebnis,
    )

    # ── 1. Zahlwort-Uhrzeiten MIT optionalem Tageszeit-Suffix ──
    def _zahlwort_uhr_ersetzen(match: re.Match) -> str:
        zahlwort: str = match.group(1).lower()
        tageszeit: str = (match.group(2) or "").lower().strip()

        if zahlwort not in _ZAHLWOERTER:
            return match.group(0)

        stunde: int = _ZAHLWOERTER[zahlwort]

        if tageszeit and tageszeit in _TAGESZEITEN:
            offset: int = _TAGESZEITEN[tageszeit]
            if stunde < 12 and offset >= 12:
                stunde += offset

        return f"{stunde}:00"

    ergebnis = re.sub(
        r'\b(' + _ZAHLWOERTER_PATTERN + r')\s+[Uu]hr\s*(' + tageszeit_woerter + r')?\b',
        _zahlwort_uhr_ersetzen,
        ergebnis,
        flags=re.IGNORECASE,
    )

    # ── 1b. "Uhr" nach bereits formatierter HH:MM entfernen ──
    ergebnis = re.sub(r'(\d{1,2}:\d{2})\s*[Uu]hr', r'\1', ergebnis)

    # ── 2. Numerische Uhrzeiten MIT optionalem Tageszeit-Suffix ──
    def _numerisch_uhr_ersetzen(match: re.Match) -> str:
        stunde: int = int(match.group(1))
        minuten: str = match.group(2) or "00"
        tageszeit: str = (match.group(3) or "").lower().strip()

        if tageszeit and tageszeit in _TAGESZEITEN:
            offset: int = _TAGESZEITEN[tageszeit]
            if stunde < 12 and offset >= 12:
                stunde += offset
            elif stunde == 12 and offset == 0 and tageszeit == "nachts":
                stunde = 0

        return f"{stunde}:{minuten}"

    ergebnis = re.sub(
        r'(?<!:)(\d{1,2})\s*[Uu]hr\s*(\d{2})?\s*(' + tageszeit_woerter + r')?\b',
        _numerisch_uhr_ersetzen,
        ergebnis,
        flags=re.IGNORECASE,
    )

    # ── 3. Standalone Tageszeit ohne "Uhr": "3 nachmittags" -> "15:00" ──
    def _standalone_tageszeit(match: re.Match) -> str:
        stunde: int = int(match.group(1))
        tageszeit: str = match.group(2).lower()
        offset: int = _TAGESZEITEN.get(tageszeit, 0)
        if stunde < 12 and offset >= 12:
            stunde += offset
        return f"{stunde}:00"

    ergebnis = re.sub(
        r'\b(\d{1,2})\s+(' + tageszeit_woerter + r')\b',
        _standalone_tageszeit,
        ergebnis,
        flags=re.IGNORECASE,
    )

    # ── 4. Fraenkisch/Sueddeutsch ──
    def _dreiviertel(match: re.Match) -> str:
        zw: str = match.group(1).lower()
        if zw in _ZAHLWOERTER:
            return f"{_ZAHLWOERTER[zw] - 1}:45"
        return match.group(0)

    ergebnis = re.sub(
        r"[Dd]reiviertel\s+(" + _ZAHLWOERTER_PATTERN + r")\b",
        _dreiviertel,
        ergebnis,
    )

    # "halb drei" -> "2:30"
    def _halb(match: re.Match) -> str:
        zw: str = match.group(1).lower()
        if zw in _ZAHLWOERTER:
            return f"{_ZAHLWOERTER[zw] - 1}:30"
        return match.group(0)

    ergebnis = re.sub(
        r"[Hh]alb\s+(" + _ZAHLWOERTER_PATTERN + r")\b",
        _halb,
        ergebnis,
    )

    # ── 5. Viertel vor/nach ──
    def _viertel_vor_nach(match: re.Match) -> str:
        richtung: str = match.group(1).lower()
        zw: str = match.group(2).lower()
        if zw in _ZAHLWOERTER:
            stunde: int = _ZAHLWOERTER[zw]
            if richtung == "vor":
                return f"{stunde - 1}:45"
            elif richtung == "nach":
                return f"{stunde}:15"
        return match.group(0)

    ergebnis = re.sub(
        r"[Vv]iertel\s+(vor|nach)\s+(" + _ZAHLWOERTER_PATTERN + r")\b",
        _viertel_vor_nach,
        ergebnis,
    )

    # ── 6. Viertel regional: "viertel acht" -> "7:15" ──
    def _viertel_regional(match: re.Match) -> str:
        zw: str = match.group(1).lower()
        if zw in _ZAHLWOERTER:
            return f"{_ZAHLWOERTER[zw] - 1}:15"
        return match.group(0)

    ergebnis = re.sub(
        r"[Vv]iertel\s+(" + _ZAHLWOERTER_PATTERN + r")(?!\s*(?:vor|nach))\b",
        _viertel_regional,
        ergebnis,
    )

    # ── 7. Minuten vor/nach: "zehn vor acht" -> "7:50" ──
    def _minuten_vor_nach(match: re.Match) -> str:
        mw: str = match.group(1).lower()
        richtung: str = match.group(2).lower()
        sw: str = match.group(3).lower()
        m: int = _ZAHLWOERTER.get(mw, 0)
        s: int = _ZAHLWOERTER.get(sw, 0)
        if not m or not s:
            return match.group(0)
        if richtung == "vor":
            return f"{s - 1}:{60 - m:02d}"
        elif richtung == "nach":
            return f"{s}:{m:02d}"
        return match.group(0)

    ergebnis = re.sub(
        r"\b(" + _ZAHLWOERTER_PATTERN + r")\s+(vor|nach)\s+("
        + _ZAHLWOERTER_PATTERN + r")\b",
        _minuten_vor_nach,
        ergebnis,
        flags=re.IGNORECASE,
    )

    # ── 8. Relative Praefixe ──
    hat_uebernachst: bool = bool(
        re.search(r"\b[Üü]bern[äa]chste[nrs]?\b", ergebnis)
    )

    ergebnis = re.sub(r"\b[Üü]bern[äa]chste[nrs]?\s+", "", ergebnis)
    ergebnis = re.sub(r"\b[Nn]ächste[nrs]?\s+", "", ergebnis)
    ergebnis = re.sub(r"\b[Kk]ommende[nrs]?\s+", "", ergebnis)
    ergebnis = re.sub(r"\b[Ll]etzte[nrs]?\s+", "", ergebnis)
    ergebnis = re.sub(r"\b[Vv]orige[nrs]?\s+", "", ergebnis)
    ergebnis = re.sub(r"\b[Vv]ergangene[nrs]?\s+", "", ergebnis)
    # "seit" traegt die Richtung und nicht die Dauer. Bleibt es stehen, kennt
    # dateparser den Ausdruck nicht und liefert gar nichts; entfernt bleibt
    # eine Dauer uebrig, die ueber `referenz_modus` rueckwaerts aufgeloest
    # wird (siehe zeit_parsen_vektor).
    ergebnis = re.sub(r"\b[Ss]eit\s+", "", ergebnis)

    ergebnis = re.sub(r"\b[Ww]oche\s+", "", ergebnis)

    # ── 9. Orphaned "um" vor Uhrzeiten entfernen ──
    ergebnis = re.sub(r'\bum\s+(\d{1,2}:\d{2})', r'\1', ergebnis)

    # Gemerkte Tageszeit NUR als Fallback einfuegen wenn keine Uhrzeit im String
    if gemerkte_uhrzeit and not re.search(r'\d{1,2}:\d{2}', ergebnis):
        ergebnis = ergebnis.strip() + " " + gemerkte_uhrzeit
        logger.info(f"Zeitparser: Tageszeit-Fallback eingefuegt: {gemerkte_uhrzeit}")

    # Mehrfache Leerzeichen normalisieren
    ergebnis = re.sub(r'\s+', ' ', ergebnis).strip()

    if ergebnis != text:
        logger.info(f"Zeitparser: Normalisiert '{text}' -> '{ergebnis}'")

    return ergebnis, hat_uebernachst


def zeit_parsen(
    text: str,
    referenz: Optional[datetime] = None,
    zukunft_bevorzugt: bool = True,
) -> Optional[datetime]:
    """
    Loest einen natuerlichsprachlichen Zeitausdruck in ein datetime auf.

    Args:
        text: Der Zeitausdruck (z.B. "am Donnerstag um 14 Uhr", "morgen")
        referenz: Referenzzeitpunkt (default: jetzt UTC)
        zukunft_bevorzugt: Bei Mehrdeutigkeit den naechsten zukuenftigen Termin waehlen

    Returns:
        datetime (timezone-aware UTC) oder None wenn nicht aufloesbar
    """
    if not text or not text.strip():
        return None

    if referenz is None:
        referenz = datetime.now(timezone.utc)

    # Schritt 1: Fuzzy-Korrektur
    korrigiert: str = _fuzzy_korrektur(text)

    # Schritt 2: Normalisierung fuer dateparser
    normalisiert, hat_uebernachst = _text_normalisieren(korrigiert)

    # Schritt 3: Drei Parse-Pfade
    tz = ZoneInfo(TIMEZONE)
    settings: dict = {
        "RELATIVE_BASE": referenz.replace(tzinfo=None),
        "PREFER_DATES_FROM": "future" if zukunft_bevorzugt else "past",
        "TIMEZONE": TIMEZONE,
        "RETURN_AS_TIMEZONE_AWARE": True,
        "DATE_ORDER": "DMY",
        "PREFER_DAY_OF_MONTH": "first",
    }

    ergebnis: Optional[datetime] = None
    pfad: int = 0
    norm_stripped: str = normalisiert.strip()

    # Pfad 1 — Direkt-Parse (ISO-Datum + Uhrzeit)
    logger.debug(f"Zeitparser Pfad-Check: normalisiert='{norm_stripped}'")
    m = re.match(r'^(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2})$', norm_stripped)
    if m:
        ergebnis = datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}:00").replace(tzinfo=tz)
        pfad = 1

    if ergebnis is None:
        m = re.match(r'^(\d{4}-\d{2}-\d{2})$', norm_stripped)
        if m:
            ergebnis = datetime.fromisoformat(f"{m.group(1)}T00:00:00").replace(tzinfo=tz)
            pfad = 1

    # Pfad 1b — DD.MM.YYYY + optionale Uhrzeit
    if ergebnis is None:
        m = re.match(r'^(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}:\d{2})$', norm_stripped)
        if m:
            tag, monat, jahr = int(m.group(1)), int(m.group(2)), int(m.group(3))
            stunde_str, minute_str = m.group(4).split(":")
            ergebnis = datetime(jahr, monat, tag, int(stunde_str), int(minute_str), tzinfo=tz)
            pfad = 1

    if ergebnis is None:
        m = re.match(r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', norm_stripped)
        if m:
            tag, monat, jahr = int(m.group(1)), int(m.group(2)), int(m.group(3))
            ergebnis = datetime(jahr, monat, tag, tzinfo=tz)
            pfad = 1

    # Pfad 2 — Split-Parse (Uhrzeit raus, dateparser nur Datum)
    if ergebnis is None:
        m = re.search(r'(\d{1,2}:\d{2})', normalisiert)
        if m:
            uhrzeit_str: str = m.group(1)
            stunde: int = int(uhrzeit_str.split(":")[0])
            minute: int = int(uhrzeit_str.split(":")[1])
            datum_teil: str = (normalisiert[:m.start()].strip()
                               + " " + normalisiert[m.end():].strip()).strip()

            if datum_teil:
                datum_ergebnis: Optional[datetime] = dateparser.parse(
                    datum_teil, languages=["de"], settings=settings,
                )
                if datum_ergebnis:
                    ergebnis = datum_ergebnis.replace(
                        hour=stunde, minute=minute, second=0, microsecond=0,
                    )
                    pfad = 2

    # Pfad 3 — Fallback (alles an dateparser)
    if ergebnis is None:
        ergebnis = dateparser.parse(normalisiert, languages=["de"], settings=settings)
        if ergebnis:
            pfad = 3

    # Letzter Fallback: Originaler Text, falls Normalisierung dateparser verwirrt hat
    if ergebnis is None and normalisiert != korrigiert:
        logger.info(f"Zeitparser: Normalisierter Text fehlgeschlagen, versuche Original...")
        ergebnis = dateparser.parse(korrigiert, languages=["de"], settings=settings)
        if ergebnis:
            pfad = 3

    if ergebnis is None:
        logger.warning(f"Zeitparser: '{text}' konnte nicht aufgeloest werden")
        return None

    logger.info(f"Zeitparser: '{text}' -> {ergebnis.isoformat()} (Pfad {pfad})")

    # Schritt 3b: "uebernachste Woche" -> +7 Tage Offset
    if hat_uebernachst:
        ergebnis = ergebnis + timedelta(days=7)
        logger.info(f"Zeitparser: 'uebernachst' erkannt -> +7 Tage Offset")

    # Schritt 4: Plausibilitaets-Check
    diff: timedelta = ergebnis - referenz

    # Mehr als 2 Jahre in der Vergangenheit?
    if diff.days < -730:
        logger.warning(
            f"Zeitparser: '{text}' -> {ergebnis.isoformat()} "
            f"liegt > 2 Jahre in der Vergangenheit, verwerfe"
        )
        return None

    # Mehr als 5 Jahre in der Zukunft?
    if diff.days > 1825:
        logger.warning(
            f"Zeitparser: '{text}' -> {ergebnis.isoformat()} "
            f"liegt > 5 Jahre in der Zukunft, verwerfe"
        )
        return None

    return ergebnis


def zeit_parsen_vektor(
    text: str,
    referenz: Optional[datetime] = None,
    zukunft_bevorzugt: bool = True,
) -> ZeitVektor:
    """
    Parst einen Zeitausdruck und meldet zurueck, welche Komponenten erkannt wurden.

    Fuer Timeline-Updates: Ermoeglicht Kombination mit bestehendem Termin.
    'Freitag' -> tag_erkannt=True, uhrzeit_erkannt=False
    '15 Uhr' -> tag_erkannt=False, uhrzeit_erkannt=True
    'Freitag um 10 Uhr' -> tag_erkannt=True, uhrzeit_erkannt=True
    """
    if not text or not text.strip():
        return ZeitVektor(datum=None, tag_erkannt=False, uhrzeit_erkannt=False, referenz_modus="relativ")

    # Schritt 1: Fuzzy-Korrektur (bestehend)
    korrigiert: str = _fuzzy_korrektur(text)

    # Schritt 2: Normalisierung (bestehend)
    normalisiert, hat_uebernachst = _text_normalisieren(korrigiert)

    # ── Uhrzeit-Erkennung ──
    # Nach Normalisierung sind alle Uhrzeitformen (15 Uhr, halb drei, dreiviertel acht)
    # in HH:MM umgewandelt. Wenn HH:MM vorhanden ist, hat der User eine Uhrzeit angegeben.
    uhrzeit_erkannt: bool = bool(re.search(r'\d{1,2}:\d{2}', normalisiert))

    # ── Tag-Erkennung ──
    korrigiert_lower: str = korrigiert.lower()
    tag_erkannt: bool = (
        any(tag in korrigiert_lower for tag in _WOCHENTAGE)
        or any(rel in korrigiert_lower for rel in [
            "heute", "morgen", "übermorgen", "uebermorgen", "gestern", "vorgestern",
        ])
        or bool(re.search(r'\d{1,2}\.\d{1,2}\.', korrigiert))
        or bool(re.search(r'\d{4}-\d{2}-\d{2}', korrigiert))
    )

    # ── Referenz-Modus aus Praefixen bestimmen ──
    # Erkennung auf korrigiertem Text VOR Normalisierung (Block 8 entfernt Praefixe)
    if re.search(r'\b(diesen|diese[mrs]?)\b', korrigiert_lower):
        referenz_modus: str = "absolut"
    elif re.search(r'\b(letzten?|vorigen?|vergangenen?|seit)\b', korrigiert_lower):
        # `seit` gehoert hierher und nicht zu `vor`: Beide zeigen rueckwaerts,
        # aber `vor` versteht dateparser selbst, waehrend `seit` ohne diese
        # Zeile eine Dauer in die ZUKUNFT aufloest. `vor` steht bewusst NICHT
        # in dieser Liste — es kommt auch in Uhrzeiten vor ("zehn vor acht"),
        # und dort waere eine Rueckwaerts-Aufloesung falsch.
        referenz_modus: str = "relativ_rueckwaerts"
    else:
        referenz_modus: str = "relativ"

    # ── Datum parsen ──
    # **Der Modus steuert die Richtung.** Bis zum 30.07.2026 wurde er hier
    # berechnet, zurueckgegeben — und nicht uebergeben: `zeit_parsen` bekam
    # nur `zukunft_bevorzugt`, und ein rueckwaerts gerichteter Ausdruck loeste
    # trotzdem nach vorn auf. "letzte fuenf Wochen" ergab ein Datum fuenf
    # Wochen in der Zukunft, obwohl der Modus `relativ_rueckwaerts` daneben
    # stand (novaberg-bugs.md -> ZEIT-RUECKWAERTS-WIRD-ZUKUNFT).
    #
    # Ein berechneter Wert ohne Wirkung ist schlimmer als keiner: Er sieht im
    # Rueckgabewert nach einer getroffenen Entscheidung aus.
    rueckwaerts: bool = referenz_modus == "relativ_rueckwaerts"
    datum: Optional[datetime] = zeit_parsen(
        text, referenz, zukunft_bevorzugt and not rueckwaerts,
    )

    return ZeitVektor(
        datum=datum,
        tag_erkannt=tag_erkannt,
        uhrzeit_erkannt=uhrzeit_erkannt,
        referenz_modus=referenz_modus,
    )
