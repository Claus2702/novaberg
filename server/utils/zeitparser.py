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


@dataclass(frozen=True)
class MarkerBefund:
    """Was die Richtungsmarker im Text aussagen.

    Bis Phase 2 gab es diese Struktur nicht. Die Richtung wurde von Block 8
    aus dem Text GELOESCHT und danach von einem zweiten Regex-Durchlauf in
    `zeit_parsen_vektor` aus dem *korrigierten, nicht normalisierten* Text
    rekonstruiert. Zwei Pipelines ueber demselben Text, die synchron bleiben
    mussten — und die es nicht taten: Weil die Praefixe nur in Block 8
    standen, bekamen sie keine ASCII-Umschreibung, und "naechsten Montag"
    behielt sein Praefix (B2, 31.07.2026).

    Jetzt liest ein Durchlauf die Marker und gibt zurueck, was er gefunden
    hat. Der Rumpf wird nur von dem befreit, was `dateparser` verwirren
    wuerde — was er selbst versteht, bleibt stehen.
    """
    richtung: str = "unbestimmt"       # "vorwaerts"|"rueckwaerts"|"unbestimmt"
    ankerart: str = "referenz"         # "jetzt"|"referenz"
    versatz_tage: int = 0              # "uebernaechste" -> 7
    marker: tuple[str, ...] = ()       # gefundene Marker im Wortlaut
    regel_ids: tuple[str, ...] = ()    # welche Regeln gegriffen haben

    @property
    def rueckwaerts(self) -> bool:
        return self.richtung == "rueckwaerts"

    def als_referenz_modus(self) -> str:
        """Uebersetzt den Befund in das bestehende ZeitVektor-Feld.

        Reihenfolge wie bisher: "diesen" schlaegt die Richtung.
        """
        if self.ankerart == "jetzt":
            return "absolut"
        if self.rueckwaerts:
            return "relativ_rueckwaerts"
        return "relativ"


@dataclass(frozen=True)
class MarkerRegel:
    """Eine Richtungsregel.

    `richtung` und `entfernen` sind BEWUSST unabhaengig. Ein Marker kann
    Richtung tragen und trotzdem im Rumpf bleiben muessen: `vor` versteht
    `dateparser` selbst, `seit` nicht. Wer beides in einem Flag fuehrt, muss
    fuer jeden neuen Marker den falschen Kompromiss waehlen.
    """
    kennung: str
    muster: str
    richtung: str = "unbestimmt"
    ankerart: str = "referenz"
    entfernen: bool = True
    versatz_tage: int = 0
    notiz: str = ""


def _wortgruppe(*woerter: str) -> str:
    """Alternation aus Woertern, laengste zuerst."""
    return "|".join(sorted(woerter, key=len, reverse=True))


# Zeiteinheiten fuer die "nackte Dauer"-Bedingung.
_DAUER_EINHEITEN: str = _wortgruppe(
    "tag", "tage", "tagen", "woche", "wochen", "monat", "monate", "monaten",
    "jahr", "jahre", "jahren", "stunde", "stunden", "minute", "minuten",
)


# Deutsche Wochentage und Monate fuer Fuzzy-Matching
_WOCHENTAGE: list[str] = [
    "montag", "dienstag", "mittwoch", "donnerstag",
    "freitag", "samstag", "sonntag",
]

# Die Umlautform ist die massgebliche: dateparser versteht "15. März" und
# liefert bei "15. Maerz" None. Die Liste trug bis zum 31.07.2026 nur die
# ASCII-Form — die Fuzzy-Korrektur fand "März" deshalb nicht als bekanntes
# Wort, ersetzte es auf Distanz 2 durch "Maerz", und dateparser scheiterte
# daran. Jedes Datum im Maerz fiel durch.
_MONATE: list[str] = [
    "januar", "februar", "märz", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "dezember",
]

_RELATIVE: list[str] = [
    "morgen", "uebermorgen", "übermorgen", "heute", "gestern", "vorgestern",
]

# Relative Praefixe — Staemme, nicht fertige Formen.
#
# Sie standen bis zum 31.07.2026 als sechs Literale in den Regexen von Block 8
# und damit in einer DRITTEN, von Hand gefuehrten Liste. Sie war bereits
# gedriftet: Weil kein Praefix in _WOCHENTAGE, _MONATE, _RELATIVE oder
# _ZAHLWOERTER stand, bekam keines seine ASCII-Umschreibung abgeleitet.
# "naechsten Montag" behielt sein Praefix, "uebernaechste Woche" bekam keinen
# +7-Offset. Das ist derselbe Fehler wie beim Maerz-Bug, nur eine Ebene
# hoeher: eine Liste, die neben den anderen laeuft, laeuft irgendwann
# auseinander.
#
# Deshalb stehen hier die Staemme; Endungen, Suchmuster und Umschreibung
# werden daraus erzeugt.
_RELATIVE_PRAEFIX_STAEMME: tuple[str, ...] = (
    "übernächste", "nächste", "kommende", "letzte", "vorige", "vergangene",
)

# "-m" gehoert dazu: "seit letztem Jahr", "von naechstem Monat" sind Dativ und
# im Deutschen gaengig. Die alten Regexe kannten nur [nrs].
_PRAEFIX_ENDUNGEN: tuple[str, ...] = ("", "n", "r", "s", "m")

_RELATIVE_PRAEFIXE: tuple[str, ...] = tuple(
    stamm + endung
    for stamm in _RELATIVE_PRAEFIX_STAEMME
    for endung in _PRAEFIX_ENDUNGEN
)


def _ascii_umschrift(wort: str) -> str:
    """Bildet die Umlaut-Umschreibung eines Wortes ("märz" -> "maerz")."""
    for umlaut, ersatz in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        wort = wort.replace(umlaut, ersatz)
    return wort


# ASCII-Umschreibung -> Umlautform, ABGELEITET aus den Listen selbst.
#
# Wer ohne Umlaute tippt, schreibt "maerz", "fuenf", "zwoelf". dateparser
# kennt nur die Umlautform, also wird zurueckuebersetzt, bevor er sie sieht.
#
# Abgeleitet und nicht von Hand gefuehrt: Eine zweite Liste liefe beim
# naechsten neuen Wort auseinander, und genau diese Drift ist der Grund, aus
# dem "märz" ueberhaupt fehlte. Wortweise ersetzt und nur bei vollstaendiger
# Uebereinstimmung — eine blinde Ersetzung von "ue" nach "ü" machte aus
# "heute" ein "heüte".
_ASCII_ZU_UMLAUT: dict[str, str] = {}

_ALLE_WOERTER: list[str] = _WOCHENTAGE + _MONATE + _RELATIVE

_GESCHUETZTE_WOERTER: set[str] = {
    "morgens", "vormittags", "mittags", "nachmittags",
    "abends", "abend", "nachts", "früh",
    "eins", "zwei", "drei", "vier", "fünf",
    "sechs", "sieben", "acht", "neun", "zehn",
    "elf", "zwölf", "halb", "viertel", "dreiviertel",
    "vor", "nach", "um", "am", "in", "an",
} | set(_RELATIVE_PRAEFIXE)



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


def _umlaute_herstellen(text: str) -> str:
    """Uebersetzt ASCII-Umschreibungen bekannter Woerter zurueck.

    "15. maerz" -> "15. märz", "fuenf Wochen" -> "fünf Wochen".

    Laeuft VOR der Fuzzy-Korrektur, damit die ein bekanntes Wort sieht statt
    eines unbekannten, das sie auf Distanz 2 irgendwohin zieht.

    Ersetzt wird nur bei vollstaendiger Wortuebereinstimmung. Eine blinde
    Ersetzung der Buchstabenfolge machte aus "heute" ein "heüte" und aus
    "neue" ein "neü".

    Vorbedingung: keine.
    Nachbedingung: Gleiche Wortzahl, gleiche Gross-/Kleinschreibung am
        Wortanfang.
    """
    # ── Eingabe ─────────────────────────────────
    if not text or not _ASCII_PATTERN:
        return text

    # ── Verarbeitung ────────────────────────────
    def ersetzen(treffer: re.Match) -> str:
        wort: str = treffer.group(0)
        ziel: str = _ASCII_ZU_UMLAUT[wort.lower()]
        return ziel.capitalize() if wort[0].isupper() else ziel

    # ── Ausgabe ─────────────────────────────────
    return re.sub(
        r'\b(' + _ASCII_PATTERN + r')\b', ersetzen, text, flags=re.IGNORECASE,
    )


def _fuzzy_korrektur(text: str, max_distanz: int = 2) -> str:
    """
    Korrigiert Tippfehler in Wochentagen und Monaten.

    'Frietag' -> 'Freitag' (Distanz 1)
    'Donerstag' -> 'Donnerstag' (Distanz 1)
    'Septmeber' -> 'September' (Distanz 2)
    """
    text = _umlaute_herstellen(text)
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

# Zuordnung befuellen, sobald alle Quelllisten stehen. Jedes Wort mit Umlaut
# bekommt seine ASCII-Umschreibung als Schluessel; Woerter, deren Umschreibung
# gleich dem Wort ist, fallen heraus.
for _quelle in (_WOCHENTAGE, _MONATE, _RELATIVE, list(_ZAHLWOERTER.keys()),
                list(_GESCHUETZTE_WOERTER), list(_RELATIVE_PRAEFIXE)):
    for _wort in _quelle:
        _ascii = _ascii_umschrift(_wort)
        if _ascii != _wort:
            _ASCII_ZU_UMLAUT.setdefault(_ascii, _wort)

_ASCII_PATTERN: str = "|".join(sorted(_ASCII_ZU_UMLAUT, key=len, reverse=True))

# ── Richtungsregeln ─────────────────────────────────────────────────────────
#
# Reihenfolge ist Prioritaet: Die erste Regel, die eine Richtung setzt,
# gewinnt. Alle passenden Regeln werden trotzdem angewandt, damit ihre
# `entfernen`-Wirkung und der Versatz greifen.
#
# Zur Enge von M-01: "bereits"/"schon"/"erst" sind haeufiger
# Verstaerkungspartikel als Richtungswort, und dort zeigen sie NACH VORN
# ("schon am Freitag", "bereits naechsten Montag"). Eine Regel auf das blosse
# Wort loeste diese rueckwaerts auf — gemessen am 31.07.2026 ergab "schon am
# Freitag" den vergangenen statt den kommenden Freitag. Deshalb verlangt
# M-01 unmittelbar eine Zahl und eine Zeiteinheit; alles andere faellt an
# M-08, das den Partikel entfernt OHNE eine Richtung zu behaupten.

_DAUER_VORAUS: str = (
    r"(?=(?:\d+|" + _ZAHLWOERTER_PATTERN + r")\s+(?:" + _DAUER_EINHEITEN + r")\b)"
)

_MARKER_REGELN: tuple[MarkerRegel, ...] = (
    MarkerRegel(
        kennung="M-01",
        muster=r"\b(bereits|schon|erst)\s+" + _DAUER_VORAUS,
        richtung="rueckwaerts",
        notiz="andauernde Sache: 'das dauert bereits zwei Wochen'",
    ),
    MarkerRegel(
        kennung="M-02",
        muster=r"\b(noch)\s+" + _DAUER_VORAUS,
        richtung="vorwaerts",
        notiz="Restdauer: 'noch zwei Wochen'. Die Ausnahme unter den Partikeln.",
    ),
    MarkerRegel(
        kennung="M-03",
        muster=r"\b(seit)\s+",
        richtung="rueckwaerts",
        notiz="dateparser versteht 'seit' nicht und loest es VORWAERTS auf.",
    ),
    MarkerRegel(
        kennung="M-04",
        muster=r"\b(vor)\s+" + _DAUER_VORAUS,
        richtung="rueckwaerts",
        entfernen=False,
        notiz=(
            "Bleibt stehen: dateparser versteht es selbst. Die Vorausschau "
            "haelt Uhrzeiten heraus — 'zehn vor acht' ist keine Richtung."
        ),
    ),
    MarkerRegel(
        kennung="M-05",
        muster=r"\b(" + _wortgruppe(*(s + e for s in ("übernächste",)
                                      for e in _PRAEFIX_ENDUNGEN)) + r")\s+",
        richtung="vorwaerts",
        versatz_tage=7,
    ),
    MarkerRegel(
        kennung="M-06",
        muster=r"\b(" + _wortgruppe(*(s + e for s in ("nächste", "kommende")
                                      for e in _PRAEFIX_ENDUNGEN)) + r")\s+",
        richtung="vorwaerts",
    ),
    MarkerRegel(
        kennung="M-07",
        muster=r"\b(" + _wortgruppe(*(s + e for s in ("letzte", "vorige",
                                                      "vergangene")
                                      for e in _PRAEFIX_ENDUNGEN)) + r")\s+",
        richtung="rueckwaerts",
    ),
    MarkerRegel(
        kennung="M-08",
        muster=r"\b(bereits|schon|erst|nur|bloß)\s+",
        richtung="unbestimmt",
        notiz=(
            "Verstaerkungspartikel. Traegt KEINE Richtung — entfernt wird er "
            "nur, damit dateparser den Rest versteht. Das ist der Fall "
            "'schon in zwei Wochen'."
        ),
    ),
    MarkerRegel(
        kennung="M-09",
        muster=r"\b(diese[nmrs]?)\b",
        richtung="unbestimmt",
        ankerart="jetzt",
        entfernen=False,
        notiz="'diesen Freitag' rechnet ab heute, nicht ab dem alten Termin.",
    ),
)

_MARKER_UEBERSETZT: tuple[tuple[MarkerRegel, "re.Pattern[str]"], ...] = tuple(
    (regel, re.compile(regel.muster, re.IGNORECASE))
    for regel in _MARKER_REGELN
)


def _marker_extrahieren(text: str) -> tuple[str, MarkerBefund]:
    """Liest die Richtungsmarker und befreit den Rumpf von den stoerenden.

    Ein Durchlauf, ein Ergebnis. Vorher lief die Erkennung zweimal ueber
    zwei verschiedene Textzustaende, und die beiden liefen auseinander.

    Args:
        text: Der fuzzy-korrigierte Ausdruck.

    Returns:
        (rumpf, befund) — der Rumpf geht an die Normalisierung, der Befund
        an die Aufloesung. Der Rumpf enthaelt keine Richtungsinformation
        mehr; sie steckt vollstaendig im Befund.

    Vorbedingung: `text` ist bereits durch `_fuzzy_korrektur` gelaufen,
        ASCII-Umschreibungen sind zurueckuebersetzt.
    Nachbedingung: Jeder gefundene Marker steht im Befund — auch die, die
        im Rumpf stehen bleiben.
    """
    # ── Eingabe ─────────────────────────────────
    if not text:
        return text, MarkerBefund()

    # ── Verarbeitung ────────────────────────────
    rumpf: str = text
    richtung: str = "unbestimmt"
    ankerart: str = "referenz"
    versatz: int = 0
    gefunden: list[str] = []
    kennungen: list[str] = []

    for regel, muster in _MARKER_UEBERSETZT:
        treffer = muster.search(rumpf)
        if treffer is None:
            continue

        gefunden.append(treffer.group(1))
        kennungen.append(regel.kennung)

        # Erste Regel mit einer Richtung gewinnt.
        if richtung == "unbestimmt" and regel.richtung != "unbestimmt":
            richtung = regel.richtung
        if regel.ankerart == "jetzt":
            ankerart = "jetzt"
        versatz += regel.versatz_tage

        if regel.entfernen:
            rumpf = muster.sub("", rumpf, count=1)

    # ── Ausgabe ─────────────────────────────────
    return re.sub(r"\s+", " ", rumpf).strip(), MarkerBefund(
        richtung=richtung,
        ankerart=ankerart,
        versatz_tage=versatz,
        marker=tuple(gefunden),
        regel_ids=tuple(kennungen),
    )

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


def _heute_lokal(jetzt: Optional[datetime] = None) -> date:
    """Der heutige Kalendertag in der KONFIGURIERTEN Ortszone.

    `date.today()` liest die Systemzone. Auf einem Entwicklerrechner in
    Deutschland ist das dasselbe wie `TIMEZONE`, in einem UTC-Container nicht.
    Genau dort lag der halbe Zwei-Uhren-Bug: Der Fix vom 31.07.2026 drehte die
    Referenz fuer Dauern in die Ortszone (`referenz.astimezone(tz)`), Block 0b
    rechnete aber weiter mit `date.today()`.

    Nachgemessen fuer 2026-07-30 22:30 UTC (= 2026-07-31 00:30 Berlin) bei
    TZ=UTC:

        "morgen"    ueber date.today()+1  ->  2026-07-31
        "in 1 Tag"  ueber RELATIVE_BASE   ->  2026-08-01

    Einen Tag auseinander — dieselbe Signatur, die der Fix beseitigen sollte.
    Das ist die dritte Welle des Partial-Fix-Problems aus
    novaberg-tool-timeparser_l_timezone.md: Zwei Uhren, gefixt wurde eine.

    Args:
        jetzt: Bezugsmoment. Default: jetzt in UTC. Nur fuer Tests gesetzt —
            damit die Zonengrenze pruefbar ist, ohne auf sie zu warten.

    Vorbedingung: keine.
    Nachbedingung: Der zurueckgegebene Tag ist derselbe, den auch
        `referenz.astimezone(ZoneInfo(TIMEZONE))` sieht.
    """
    # ── Eingabe ─────────────────────────────────
    if jetzt is None:
        jetzt = datetime.now(timezone.utc)

    # ── Ausgabe ─────────────────────────────────
    return jetzt.astimezone(ZoneInfo(TIMEZONE)).date()


def _text_normalisieren(
    text: str,
    heute: Optional[date] = None,
) -> str:
    """
    Normalisiert deutsche Zeitausdruecke fuer dateparser-Kompatibilitaet.

    Args:
        text: Der bereits fuzzy-korrigierte Zeitausdruck.
        heute: Kalendertag fuer die deiktischen Tagesworte. Default:
            `_heute_lokal()`. Der Parameter ist additiv — alle bestehenden
            Aufrufer bleiben unveraendert gueltig.

    Returns:
        Der normalisierte Text. Der frueher mitgelieferte
        `hat_uebernachst` steckt jetzt in `MarkerBefund.versatz_tage` —
        er wird dort erzeugt, wo er entsteht.
    """
    if heute is None:
        heute = _heute_lokal()

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
            konkretes_datum: str = (heute + timedelta(days=offset)).isoformat()
            ergebnis = re.sub(
                r'\b' + wort + r'\b',
                konkretes_datum,
                ergebnis,
                flags=re.IGNORECASE,
            )

    # ── 0c. Deutsches Datum ohne Jahr: "01.07." oder "15.04." -> "01.07.2026" ──
    aktuelles_jahr: str = str(heute.year)

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
    # ── 8. Reste fuer dateparser-Kompatibilitaet ──
    #
    # Die Richtungswoerter stehen hier nicht mehr. Sie hat
    # `_marker_extrahieren` gelesen und — soweit noetig — entfernt, BEVOR
    # dieser Text entstand. Block 8 kannte sie frueher nur, um sie
    # wegzuwerfen; die Richtung musste danach aus dem Originaltext
    # rekonstruiert werden. Genau diese zweite Pipeline ist der Punkt, an
    # dem B2 entstand.
    #
    # "Woche" faellt nur, wenn ein Wochentag folgt: In "nächste Woche
    # Dienstag" ist es nach der Markerentfernung redundant, sonst nicht.
    #
    # Die Regel loeschte bis zum 31.07.2026 jedes "Woche " mit Folgetext. Sie
    # war fuer einen Kontext gebaut und wirkte kontextfrei — gemessen:
    #
    #     "in einer Woche um 14 Uhr"  ->  "in einer 14:00"
    #     "Woche 32"                  ->  "32"
    #
    # Beides Ausdruecke, die vorher nicht falsch parsten, sondern gar nicht.
    ergebnis = re.sub(
        r"\b[Ww]oche\s+(?=(" + "|".join(_WOCHENTAGE) + r")\b)",
        "", ergebnis, flags=re.IGNORECASE,
    )

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

    return ergebnis


def zeit_parsen(
    text: str,
    referenz: Optional[datetime] = None,
    zukunft_bevorzugt: bool = True,
    sprechzeitpunkt: Optional[datetime] = None,
) -> Optional[datetime]:
    """
    Loest einen natuerlichsprachlichen Zeitausdruck in ein datetime auf.

    Args:
        text: Der Zeitausdruck (z.B. "am Donnerstag um 14 Uhr", "morgen")
        referenz: Anker fuer relative **Dauern** — "in drei Tagen" zaehlt von
            ihr aus. Default: jetzt UTC. Der Timeline-Update-Pfad reicht hier
            die Zeit des bestehenden Termins durch.
        zukunft_bevorzugt: Bei Mehrdeutigkeit den naechsten zukuenftigen Termin waehlen
        sprechzeitpunkt: Der Moment, in dem gesprochen wird — Anker fuer
            deiktische **Tagesworte** ("morgen", "uebermorgen"). Default: die
            echte Uhr, **nicht** `referenz`: "verschieb ihn auf morgen" meint
            morgen ab heute, auch wenn der Termin im August liegt. Zu setzen
            ist er, wo ein Ausdruck gegen einen anderen Moment aufzuloesen ist
            — bei der Wiederverarbeitung alter Turns und in Testkorpora.

    Returns:
        datetime (timezone-aware UTC) oder None wenn nicht aufloesbar
    """
    ergebnis, _befund, _korrigiert, _normalisiert = _aufloesen(
        text, referenz, zukunft_bevorzugt, sprechzeitpunkt,
    )
    return ergebnis


def _aufloesen(
    text: str,
    referenz: Optional[datetime],
    zukunft_bevorzugt: bool,
    sprechzeitpunkt: Optional[datetime] = None,
) -> tuple[Optional[datetime], MarkerBefund, str, str]:
    """Der gemeinsame Weg von `zeit_parsen` und `zeit_parsen_vektor`.

    Einmal Fuzzy, einmal Marker, einmal Normalisierung. Bis Phase 2 lief
    `zeit_parsen_vektor` die ersten beiden Schritte fuer die
    Komponentenerkennung und rief dann `zeit_parsen` mit dem ORIGINALTEXT,
    das beides erneut tat — doppelte Arbeit und zwei Durchlaeufe, die
    auseinanderlaufen konnten, sobald einer von ihnen Zustand bekam.

    Returns:
        (datum, befund, korrigiert, normalisiert)
    """
    if not text or not text.strip():
        return None, MarkerBefund(), "", ""

    if referenz is None:
        referenz = datetime.now(timezone.utc)

    # ZWEI BEZUGSPUNKTE, WEIL ES ZWEI FRAGEN SIND.
    #
    # `referenz` ist der Anker fuer relative DAUERN: "in drei Tagen" zaehlt von
    # ihr aus. Der Timeline-Update-Pfad reicht dort die Zeit des BESTEHENDEN
    # Termins durch (`agents/timeline/crud.py`) — "verschieb ihn um zwei Tage"
    # meint zwei Tage nach dem Termin, nicht nach heute.
    #
    # `sprechzeitpunkt` ist der Moment, in dem gesprochen wird: Ein deiktisches
    # Tageswort zeigt immer auf den Tag nach DIESEM Tag. "Verschieb ihn auf
    # morgen" heisst morgen ab heute, auch wenn der Termin im August liegt.
    #
    # **Beides in einen Parameter zu legen, geht nicht** — die beiden Faelle
    # oben verlangen gegensaetzliches Verhalten. Bis zum 01.08.2026 gab es nur
    # `referenz`, und die Tagesworte nahmen ersatzweise die echte Uhr. Das war
    # fuer den Live-Pfad richtig und fuer jede spaetere Verarbeitung falsch:
    # Ein Ausdruck, der gegen einen historischen Moment aufgeloest werden soll,
    # bekam den heutigen Kalendertag.
    #
    # Gemessen am 01.08.2026 — dreimal derselbe Ausdruck, drei Bezugsmomente:
    #
    #     Bezug 10.07. 22:30Z -> "uebermorgen" 2026-08-03, "in zwei Tagen" 13.07.
    #     Bezug 20.07. 22:30Z -> "uebermorgen" 2026-08-03, "in zwei Tagen" 23.07.
    #     Bezug 30.07. 22:30Z -> "uebermorgen" 2026-08-03, "in zwei Tagen" 02.08.
    #
    # Der Vorgabewert bleibt die echte Uhr, damit jeder Aufrufer, der nur einen
    # Termin verschiebt, unveraendert weiterlaeuft.
    #
    # Die Zone gilt vor der Persistenz-Grenze; nach UTC dreht erst das
    # Repository (novaberg-tool-timeparser_l_timezone.md §3). Gedreht wird,
    # nicht des Zonenvermerks beraubt: `RELATIVE_BASE` muss naiv sein, und
    # `settings["TIMEZONE"]` unten sagt dateparser, dass es naive Zeiten als
    # Ortszeit liest — ein blosses `.replace(tzinfo=None)` haette die
    # UTC-Wanduhr als Ortszeit ausgegeben.
    tz = ZoneInfo(TIMEZONE)
    referenz_lokal: datetime = referenz.astimezone(tz)
    heute_lokal: date = (
        _heute_lokal() if sprechzeitpunkt is None
        else sprechzeitpunkt.astimezone(tz).date()
    )

    # Schritt 1: Fuzzy-Korrektur
    korrigiert: str = _fuzzy_korrektur(text)

    # Schritt 2: Marker lesen — der Rumpf geht weiter, die Richtung in den Befund
    rumpf, befund = _marker_extrahieren(korrigiert)

    # Schritt 3: Normalisierung fuer dateparser (kennt keine Richtung mehr)
    normalisiert: str = _text_normalisieren(rumpf, heute=heute_lokal)

    # DIE RICHTUNG WIRD UEBERGEBEN, nicht nur berechnet.
    #
    # Bis zum 30.07.2026 wurde sie in `zeit_parsen_vektor` ermittelt,
    # zurueckgegeben — und nicht weitergereicht: `zeit_parsen` bekam nur
    # `zukunft_bevorzugt`, und ein rueckwaerts gerichteter Ausdruck loeste
    # trotzdem nach vorn auf ("letzte fuenf Wochen" ergab ein Datum fuenf
    # Wochen in der ZUKUNFT). Seit Phase 2 steht die Auswertung hier, im
    # gemeinsamen Weg — jeder Aufrufer bekommt sie, auch die, die nur
    # `zeit_parsen` benutzen (`agents/timeline/suche.py`, `agents/kzg/magnete.py`).
    #
    # Ein berechneter Wert ohne Wirkung ist schlimmer als keiner: Er sieht
    # im Rueckgabewert nach einer getroffenen Entscheidung aus.
    zukunft: bool = zukunft_bevorzugt and not befund.rueckwaerts

    # Schritt 4: Drei Parse-Pfade — `tz` und `referenz_lokal` stehen oben.
    settings: dict = {
        "RELATIVE_BASE": referenz_lokal.replace(tzinfo=None),
        "PREFER_DATES_FROM": "future" if zukunft else "past",
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
    m = re.match(r'^(\d{4}-\d{2}-\d{2})\s+(\d{1,2}):(\d{2})$', norm_stripped)
    if m:
        # Zusammengesetzt statt ueber `fromisoformat`: Das Muster erlaubt eine
        # EINSTELLIGE Stunde, `fromisoformat` verlangt zwei. "morgen um 9 Uhr"
        # normalisiert zu "2026-08-01 9:00" und riss damit eine unbehandelte
        # ValueError bis zum Aufrufer hoch — gemessen am 31.07.2026. Zweistellige
        # Uhrzeiten kamen durch, einstellige stuerzten ab; deshalb fiel es nie
        # jemandem als Muster auf. Pfad 1b baut sein Datum laengst so.
        jahr, monat, tag = (int(teil) for teil in m.group(1).split("-"))
        ergebnis = datetime(
            jahr, monat, tag, int(m.group(2)), int(m.group(3)), tzinfo=tz,
        )
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

    # Pfad 1c — Nackte Uhrzeit ohne jede Tagesangabe.
    #
    # Der Tag wird hier selbst gerechnet und NICHT von dateparser erfragt.
    # Grund, instrumentiert gemessen am 31.07.2026 an dateparser 1.4.1:
    #
    # Dessen Addition ist korrekt — `_correct_for_time_frame` rechnet fuer eine
    # bereits vergangene Uhrzeit `dateobj + timedelta(days=1)` und traegt sauber
    # ueber die Monatsgrenze. UNMITTELBAR DANACH laeuft `_correct_for_month`,
    # und die rechnet nicht, sondern weist zu:
    #
    #     date_obj.replace(month=<Monat des Bezugsmoments>)
    #
    # Diese Korrektur soll ein NICHT GENANNTES Monatsfeld befuellen. Zu ihrem
    # Zeitpunkt ist das Feld aber kein Default mehr, sondern das Ergebnis der
    # Addition — und ein `datetime` traegt keine Herkunft, an der sie das
    # unterscheiden koennte. Der Uebertrag wird damit ueberschrieben, der Tag 1
    # bleibt stehen:
    #
    #     31.07. 14:27 + "02:30"  ->  01.08. (Addition)  ->  01.07. (Zuweisung)
    #     31.12. 14:27 + "02:30"  ->  01.01.2027         ->  01.12.2027
    #
    # Der Silvester-Fall zeigt die Bauart: Das JAHR ueberlebt, weil nur das
    # Monatsfeld zugewiesen wird — elf Monate daneben, nicht zwoelf. Eine
    # fehlerhafte Addition koennte dieses Muster nicht erzeugen.
    #
    # Reichweite, instrumentiert: Fuer Wochentage, Dauern und deiktische Worte
    # wird die Monatskorrektur gar nicht erst gerufen; sie tragen korrekt ueber
    # die Grenze. Die nackte Uhrzeit ist der einzige Ausdruck, der dort ankommt.
    # Der Plausibilitaets-Check unten greift erst ab zwei Jahren, und an den
    # uebrigen 29 Tagen des Monats rechnet dateparser richtig — deshalb ist der
    # Defekt einem Test gegen `date.today()` nie begegnet.
    #
    # Die Regel hier ist die, die dateparser meint: heute, wenn die Uhrzeit
    # noch kommt, sonst der Nachbartag in der gefragten Richtung.
    if ergebnis is None:
        m = re.match(r'^(\d{1,2}):(\d{2})$', norm_stripped)
        if m:
            stunde, minute = int(m.group(1)), int(m.group(2))
            if stunde < 24 and minute < 60:
                kandidat: datetime = referenz_lokal.replace(
                    hour=stunde, minute=minute, second=0, microsecond=0,
                )
                if zukunft and kandidat <= referenz_lokal:
                    kandidat += timedelta(days=1)
                elif not zukunft and kandidat > referenz_lokal:
                    kandidat -= timedelta(days=1)
                ergebnis = kandidat
                pfad = 1
            else:
                logger.error(
                    f"Zeitparser: '{norm_stripped}' sieht aus wie eine Uhrzeit, "
                    f"ist aber keine ({stunde}:{minute:02d}) — an dateparser "
                    f"weitergereicht"
                )

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
        return None, befund, korrigiert, normalisiert

    logger.info(
        f"Zeitparser: '{text}' -> {ergebnis.isoformat()} (Pfad {pfad}, "
        f"Richtung {befund.richtung}, Regeln {befund.regel_ids or '-'})"
    )

    # Schritt 4b: "uebernaechste Woche" -> +7 Tage
    if befund.versatz_tage:
        ergebnis = ergebnis + timedelta(days=befund.versatz_tage)
        logger.info(f"Zeitparser: Versatz {befund.versatz_tage} Tage")

    # Schritt 4: Plausibilitaets-Check
    diff: timedelta = ergebnis - referenz

    # Mehr als 2 Jahre in der Vergangenheit?
    if diff.days < -730:
        logger.warning(
            f"Zeitparser: '{text}' -> {ergebnis.isoformat()} "
            f"liegt > 2 Jahre in der Vergangenheit, verwerfe"
        )
        return None, befund, korrigiert, normalisiert

    # Mehr als 5 Jahre in der Zukunft?
    if diff.days > 1825:
        logger.warning(
            f"Zeitparser: '{text}' -> {ergebnis.isoformat()} "
            f"liegt > 5 Jahre in der Zukunft, verwerfe"
        )
        return None, befund, korrigiert, normalisiert

    return ergebnis, befund, korrigiert, normalisiert


def zeit_parsen_vektor(
    text: str,
    referenz: Optional[datetime] = None,
    zukunft_bevorzugt: bool = True,
    sprechzeitpunkt: Optional[datetime] = None,
) -> ZeitVektor:
    """
    Parst einen Zeitausdruck und meldet zurueck, welche Komponenten erkannt wurden.

    Fuer Timeline-Updates: Ermoeglicht Kombination mit bestehendem Termin.
    'Freitag' -> tag_erkannt=True, uhrzeit_erkannt=False
    '15 Uhr' -> tag_erkannt=False, uhrzeit_erkannt=True
    'Freitag um 10 Uhr' -> tag_erkannt=True, uhrzeit_erkannt=True

    Seit Phase 2 laeuft der Text EINMAL durch: `_aufloesen` liefert Datum,
    Markerbefund und beide Textzustaende zurueck. Der frueher noetige zweite
    Regex-Durchlauf auf dem korrigierten Text entfaellt — mit ihm die
    Moeglichkeit, dass beide Durchlaeufe auseinanderlaufen.

    Args:
        referenz: Anker fuer relative **Dauern**. Der Update-Pfad reicht hier
            die Zeit des bestehenden Termins durch.
        sprechzeitpunkt: Anker fuer deiktische **Tagesworte**. Default: die
            echte Uhr, nicht `referenz` — sonst schoebe "verschieb ihn auf
            morgen" einen Termin im August auf den Tag nach jenem Termin.
            Ausfuehrlich an der Referenz-Drehung in `_aufloesen`.
    """
    # ── Eingabe ─────────────────────────────────
    if not text or not text.strip():
        return ZeitVektor(
            datum=None, tag_erkannt=False, uhrzeit_erkannt=False,
            referenz_modus="relativ",
        )

    # ── Verarbeitung ────────────────────────────
    datum, befund, korrigiert, normalisiert = _aufloesen(
        text, referenz, zukunft_bevorzugt, sprechzeitpunkt,
    )

    # Uhrzeit-Erkennung: Nach der Normalisierung sind alle Uhrzeitformen
    # ("15 Uhr", "halb drei", "dreiviertel acht") in HH:MM umgewandelt.
    uhrzeit_erkannt: bool = bool(re.search(r'\d{1,2}:\d{2}', normalisiert))

    # Tag-Erkennung auf dem korrigierten Text — der Rumpf hat die Praefixe
    # nicht mehr, der korrigierte Text schon.
    korrigiert_lower: str = korrigiert.lower()
    tag_erkannt: bool = (
        any(tag in korrigiert_lower for tag in _WOCHENTAGE)
        or any(rel in korrigiert_lower for rel in [
            "heute", "morgen", "übermorgen", "uebermorgen", "gestern", "vorgestern",
        ])
        or bool(re.search(r'\d{1,2}\.\d{1,2}\.', korrigiert))
        or bool(re.search(r'\d{4}-\d{2}-\d{2}', korrigiert))
    )

    # ── Ausgabe ─────────────────────────────────
    return ZeitVektor(
        datum=datum,
        tag_erkannt=tag_erkannt,
        uhrzeit_erkannt=uhrzeit_erkannt,
        referenz_modus=befund.als_referenz_modus(),
    )
