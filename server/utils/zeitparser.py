"""
Zeitparser -- Loest natuerlichsprachliche Zeitausdruecke in datetime auf.

Dreistufig:
1. Fuzzy-Korrektur: Tippfehler in Wochentagen/Monaten erkennen
2. dateparser: Deutschsprachige relative/absolute Ausdruecke aufloesen
3. Plausibilitaets-Check: Ergebnis im sinnvollen Fenster?

Prinzip: LLM extrahiert den Zeitausdruck als String,
Python loest ihn deterministisch auf.
"""

import calendar
import logging
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from types import MappingProxyType
from typing import ClassVar, Optional
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
class TimeReading:
    """Welche Stunden und welche Tage des Monats ein Auftrag nennt.

    Gelesen fuer das Verschieben eines Termins (`read_time`): Dort wird eine
    neue Uhrzeit nur geschrieben, wenn sie nicht geraten ist. Der Vektor
    liefert dafuer zu wenig — er nimmt bei zwei Uhrzeiten die erste, zaehlt
    eine nackte Stunde nicht ("zwischen 10 und 11 Uhr") und kennt "den 20."
    nicht als Tag.

    `hours`: jede Stunde als (Stunde, Minute), geschrieben ("11:30"), als
    nackte Zahl 0..24 oder als Zahlwort ("elf"); `stated`: die Stunde, die
    ein Text als neue nennt (`_read_time`, Lage (a) oder (b)); `undecided`:
    ein Text nennt Stunden, aber keine davon als neue; `days`: die genannten
    Tage des Monats, auch als Ordinalzahl ("den zehnten"); `doubtful`: eine
    Zahl mit Punkt, die Tag oder Stunde sein kann ("auf 11."), eine
    Ordinalzahl ohne Artikel und Monat ("zehnten 11:00"), ein Tag, den es
    nicht gibt ("den 31." vor einem Monat mit 30 Tagen), eine Stunde hinter
    "halb"/"viertel", die nicht umgerechnet ist, oder Minuten als Zahlwort
    ("elf Uhr dreissig").
    """

    hours: frozenset[tuple[int, int]] = frozenset()
    stated: frozenset[tuple[int, int]] = frozenset()
    undecided: bool = False
    days: frozenset[date] = frozenset()
    doubtful: bool = False

    def merged(self, other: "TimeReading") -> "TimeReading":
        """Beide Lesungen zusammen — Aeusserung und Zeitausdruck desselben Auftrags.

        Vorbedingung: `other` ist eine `TimeReading`.
        Nachbedingung: jede Menge ist die Vereinigung, jede Marke das Oder.
        Fehlerfaelle: etwas anderes als eine `TimeReading` wirft `TypeError`.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not isinstance(other, TimeReading):
            msg: str = f"TimeReading.merged: keine TimeReading ({type(other).__name__})"
            raise TypeError(msg)

        # ── Verarbeitung ────────────────────────────
        both: TimeReading = TimeReading(
            hours=self.hours | other.hours,
            stated=self.stated | other.stated,
            undecided=self.undecided or other.undecided,
            days=self.days | other.days,
            doubtful=self.doubtful or other.doubtful,
        )

        # ── Ausgabe ─────────────────────────────────
        return both

    def clock_time(self) -> Optional[time]:
        """Die neue Uhrzeit, wenn sie nicht geraten ist — sonst None.

        Die Lage liest `_read_time` je Text und legt die neue Stunde in
        `stated`: (a) der Text traegt genau eine Stunde; (b) er traegt genau
        zwei in der Form "von X auf Y" oder "von X nach Y". Hier gilt sie nur,
        wenn alle Texte zusammen genau eine nennen und keiner unentschieden ist.

        Vorbedingung: keine.
        Nachbedingung: die eine Stunde aus `stated` als gueltige Uhrzeit;
            sonst None.
        Fehlerfaelle: None geben ein Text mit Stunden, aber ohne Lage (a) oder
            (b) (`undecided`: "auf 10 oder 11 Uhr", "von 10 bis 12 Uhr", "auf
            11 Uhr und den Friseur auf 14 Uhr"), zwei verschiedene neue
            Stunden aus Satz und Zeitausdruck, eine Zahl im Zweifel und eine
            unmoegliche Uhrzeit ("25 Uhr").
        """
        # ── Verarbeitung ────────────────────────────
        if self.doubtful or self.undecided or len(self.stated) != 1:
            return None
        ((hour, minute),) = self.stated

        # ── Ausgabe-Verifikation ────────────────────
        if hour > 23 or minute > 59:
            return None
        return time(hour, minute)

    def day(self) -> Optional[date]:
        """Der eine genannte Tag des Monats, oder None, wenn keiner oder mehrere.

        Vorbedingung: keine.
        Nachbedingung: ein Tag aus `days`, wenn es genau einer ist.
        """
        # ── Verarbeitung ────────────────────────────
        named: Optional[date] = next(iter(self.days)) if len(self.days) == 1 else None

        # ── Ausgabe ─────────────────────────────────
        return named

    def unclear(self) -> bool:
        """Ob der Auftrag eine Zeit oder einen Tag nennt, ohne dass klar ist, welche.

        Vorbedingung: keine.
        Nachbedingung: wahr bei Zweifel, bei mehr als einem Tag und bei
            Stunden ohne `clock_time` — der Aufrufer fragt dann zurueck.
        """
        # ── Verarbeitung ────────────────────────────
        is_unclear: bool = (
            self.doubtful or len(self.days) > 1 or (bool(self.hours) and self.clock_time() is None)
        )

        # ── Ausgabe ─────────────────────────────────
        return is_unclear


@dataclass(frozen=True)
class TimeVocabulary:
    """Das Vokabular des Zeitparsers, fuer wen aus ihm ableitet (`TIME_VOCABULARY`).

    Abgeleitet aus den Listen des Parsers, nicht abgeschrieben: Aendert sich
    eine Liste, aendert sich das Vokabular mit. `words`: jedes Wort, das der
    Parser als Zeitbezug fuehrt (Wochentage, Monate und ihre Kurzformen,
    Tageswoerter, Tageszeiten, Zeiteinheiten, relative Praefixe, geschuetzte
    Woerter, Zahlwoerter, Stunden als Zahlwort, Ordinaltage, "mittag",
    "nacht"); `hour_words`: Stunde als Zahlwort mit ihrem Wert, ohne "ein";
    `ordinal_days`, `relative_prefixes`, `weekdays`: die Formen je Liste;
    `dayparts`: jede Tageszeit mit dem Versatz, mit dem der Parser eine Stunde
    an ihr rechnet (0 oder 12, "nachmittags" -> 12).

    Vorbedingung: jede Folge nicht leer und nur aus nicht leeren Texten, jede
        Stunde 0..24, jeder Versatz 0 oder 12.
    Nachbedingung: ein unveraenderliches Vokabular.
    Fehlerfaelle: eine leere Folge, ein leeres Wort, eine Stunde ausserhalb
        0..24 oder ein anderer Versatz wirft `ValueError`.
    """

    words: tuple[str, ...]
    hour_words: Mapping[str, int]
    ordinal_days: tuple[str, ...]
    relative_prefixes: tuple[str, ...]
    weekdays: tuple[str, ...]
    dayparts: Mapping[str, int]

    def __post_init__(self) -> None:
        """Prueft die Vorbedingung der Klasse; wirft `ValueError`, wenn sie verletzt ist."""
        # ── Eingabe-Validierung ─────────────────────
        for name in ("words", "hour_words", "ordinal_days", "relative_prefixes", "weekdays",
                     "dayparts"):
            values: object = getattr(self, name)
            if not values or not all(isinstance(word, str) and word for word in values):
                msg: str = f"TimeVocabulary: {name} leer oder mit leerem Wort ({values!r})"
                raise ValueError(msg)
        if not all(isinstance(hour, int) and 0 <= hour <= 24 for hour in self.hour_words.values()):
            msg = f"TimeVocabulary: Stunde ausserhalb 0..24 ({dict(self.hour_words)!r})"
            raise ValueError(msg)
        if not all(isinstance(offset, int) and offset in (0, 12)
                   for offset in self.dayparts.values()):
            msg = f"TimeVocabulary: Versatz nicht 0 oder 12 ({dict(self.dayparts)!r})"
            raise ValueError(msg)

    def ascii_form(self, text: str) -> str:
        """Ein Text in der ASCII-Umschrift des Parsers ("märz" -> "maerz").

        Dieselbe Umschrift, aus der der Parser die ASCII-Formen seiner Listen
        bildet; wer aus dem Vokabular ableitet, schreibt damit um.

        Vorbedingung: `text` ist ein Text, leer erlaubt.
        Nachbedingung: kein "ä", "ö", "ü", "ß" mehr im Text.
        Fehlerfaelle: kein Text wirft `TypeError`.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not isinstance(text, str):
            msg: str = f"TimeVocabulary.ascii_form: kein Text ({type(text).__name__})"
            raise TypeError(msg)

        # ── Verarbeitung ────────────────────────────
        result: str = _ascii_umschrift(text)

        # ── Ausgabe ─────────────────────────────────
        return result


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


_RELATIVE_DAYS: dict[str, int] = {
    "heute": 0,
    "morgen": 1,
    "übermorgen": 2,
    "uebermorgen": 2,
    "vorgestern": -2,
    "gestern": -1,
}

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

#: Die Namen der Dauer-Einheiten, Einzahl und Mehrzahl.
#:
#: **Sie muessen geschuetzt sein, weil die kurzen Einzahlformen in
#: Levenshtein-Reichweite eines Monats- oder Wochentagsnamens liegen.**
#: Gemessen am 25.08.2026: `Tag` -> `Mai` und `Monat` -> `Montag`, beide auf
#: Distanz 2 und damit innerhalb von `max_distanz`. Danach parste `in einem
#: Tag` als *im Mai* (01.05.2027) und `in einem Monat` als *am Montag*
#: (01.07.2026 — 29 Tage RUECKWAERTS, obwohl die Zukunft bevorzugt wird).
#:
#: **Die Mehrzahlformen waren nie betroffen** und darum fiel es nicht auf:
#: `Tagen` und `Monaten` sind lang genug, dass keine Korrektur greift. Der
#: Defekt sah deshalb aus wie ein Einzahl-Problem und war eines der
#: Wortlaenge. Kennung: `ZEIT-EINZAHL-GREIFT-DANEBEN`.
#:
#: Aufgenommen sind auch die heute unauffaelligen Einheiten. Was eine
#: Zeiteinheit benennt, ist nie ein verschriebener Monatsname — die Regel
#: haengt nicht daran, welche Distanz eine einzelne Form gerade hat.
_ZEITEINHEITEN: set[str] = {
    "sekunde", "sekunden", "minute", "minuten", "stunde", "stunden",
    "tag", "tage", "tagen", "woche", "wochen",
    "monat", "monate", "monaten", "jahr", "jahre", "jahren",
}

_GESCHUETZTE_WOERTER: set[str] = {
    "morgens", "vormittags", "vormittag", "mittags", "nachmittags", "nachmittag",
    "abends", "abend", "nachts", "früh",
    "eins", "zwei", "drei", "vier", "fünf",
    "sechs", "sieben", "acht", "neun", "zehn",
    "elf", "zwölf", "halb", "viertel", "dreiviertel",
    "vor", "nach", "um", "am", "in", "an",
} | set(_RELATIVE_PRAEFIXE) | _ZEITEINHEITEN



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

# Die Einzahl ohne -s steht neben der Mehrzahl, weil sie nach einem Tageswort
# die gesprochene Form ist: "heute abend", "morgen nachmittag". Bis zum
# 15.09.2026 kannte die Tabelle nur "Abend" (fuer die Rueckfall-Uhrzeit), und
# "morgen nachmittag um 3" loeste zu nichts auf.
#
# "nacht" fehlt mit Absicht: "heute Nacht um 2" meint den Morgen des Folgetags,
# und diese Rechnung kann der Parser nicht. Ohne Eintrag bleibt der Ausdruck
# unaufgeloest, statt still auf heute 02:00 zu fallen.
_TAGESZEITEN: dict[str, int] = {
    "morgens": 0,
    "früh": 0,
    "vormittags": 0,
    "vormittag": 0,
    "mittags": 12,
    "nachmittags": 12,
    "nachmittag": 12,
    "abends": 12,
    "abend": 12,
    "nachts": 0,
}

_TAGESZEIT_UHRZEITEN: dict[str, str] = {
    "früh": "06:00",
    "morgens": "08:00",
    "vormittags": "10:00",
    "vormittag": "10:00",
    "mittags": "12:00",
    "nachmittags": "15:00",
    "nachmittag": "15:00",
    "abends": "18:00",
    "Abend": "18:00",
    "nachts": "22:00",
}

#: Mengen und Vergleiche, hinter denen eine Zahl nach "um" keine Uhrzeit ist:
#: "um 10 Minuten verschieben", "um 10 Prozent", "um 3 Grad", "um 2.50 teurer".
#: Waehrungen, Masse und Vergleiche der zweiten Zeile kamen am 15.09.2026 aus
#: erzeugten Eingaben dazu. **Die Liste bleibt eine Liste:** Steht hinter der
#: Zahl nichts oder ein anderes Wort ("Version um 2.10"), ist sie nicht von
#: "Treffen um 9.30" zu trennen und wird als Uhrzeit gelesen.
_QUANTITIES_AFTER_UM: str = _wortgruppe(
    "sekunde", "sekunden", "minute", "minuten", "min", "stunde", "stunden", "std",
    "tag", "tage", "tagen", "woche", "wochen", "monat", "monate", "monaten",
    "jahr", "jahre", "jahren", "prozent", "prozentpunkte", "euro", "cent", "grad",
    "mal", "punkte", "stück", "kilo", "kilometer", "km", "meter", "cm",
    "dollar", "eur", "franken", "teurer", "billiger", "liter", "kilogramm", "kg",
    "zentimeter", "promille", "prozentpunkt",
)

#: Monate und ihre Kurzformen: Vor ihnen ist eine Zahl ein Tag, keine Stunde
#: ("um 15. Mai").
_MONTHS_AFTER_UM: str = _wortgruppe(
    *_MONATE, "jan", "feb", "mär", "apr", "jun", "jul", "aug", "sep", "sept",
    "okt", "nov", "dez",
)

#: "um" und eine Stunde ohne "Uhr": "übermorgen um 9", "Donnerstag um 14",
#: "abends um 8", "um 10 rum". Das Wort danach darf keine Menge und kein Monat
#: sein, und ein Punkt danach nur, wenn keine Ziffer folgt ("um 10.30" ist eine
#: andere Form). Ein Satzpunkt direkt hinter der Stunde gehoert zum Treffer und
#: faellt mit weg.
_HOUR_AFTER_UM = re.compile(
    r"\bum\s+(\d{1,2})(?:\s+(?:herum|rum))?(?:\.(?!\d))?"
    r"(?=\s*$|\s*[,;!?)]|\s+(?!(?:" + _QUANTITIES_AFTER_UM + "|" + _MONTHS_AFTER_UM
    + r")\b)(?![%€°]))",
    re.IGNORECASE,
)

#: Eine nackte Stunde direkt vor einer Tageszeit: "3 nachmittags". Nicht der
#: Minutenteil einer Uhrzeit ("15:00 nachmittags", "3 Uhr 15 nachmittags") und
#: nicht der Tag eines Datums ("01.07. nachmittags").
_HOUR_BEFORE_DAYPART = re.compile(
    r"(?<![:\d.])(?<!uhr\s)\b(\d{1,2})\s+(" + "|".join(_TAGESZEITEN.keys()) + r")\b",
    re.IGNORECASE,
)

#: Eine Uhrzeit mit Punkt als Trenner vor "Uhr": "9.30 Uhr", "15.09.2026 10.00
#: Uhr". Vor "Uhr" ist sie immer eine Uhrzeit, auch "25.00 Uhr" — die verwirft
#: danach die Pruefung auf unmoegliche Werte. Nicht hinter einer Ziffer, einem
#: Punkt oder Doppelpunkt: Das waere der Rest eines Datums oder einer Uhrzeit.
_DOTTED_BEFORE_UHR = re.compile(r"(?<![\d.:])(\d{1,2})\.(\d{2})(?=\s*uhr\b)", re.IGNORECASE)

#: Dieselbe Form nach "um", ohne "Uhr": "um 9.30". Hier nur, wenn sie eine
#: Uhrzeit sein kann — die Spanne prueft `_read_dotted_clock_time` —, denn
#: "um 31.12" kann ein Datum meinen. Nicht vor einem Punkt ("um 1.10." ist der
#: 1. Oktober), nicht vor einer Menge oder einem Monat ("um 2.50 Euro"), und
#: nicht vor "Uhr" — die Form gehoert `_DOTTED_BEFORE_UHR`, sonst zaehlte
#: dieselbe Stelle zweimal.
_DOTTED_AFTER_UM = re.compile(
    r"(?<=\bum\s)(\d{1,2})\.(\d{2})(?!\s*uhr\b)"
    r"(?=\s*$|\s*[,;!?)]|\s+(?!(?:" + _QUANTITIES_AFTER_UM + "|" + _MONTHS_AFTER_UM
    + r")\b)(?![%€°]))",
    re.IGNORECASE,
)

#: Eine geschriebene Uhrzeit. Die Leser zaehlen damit nach, ob jeder Kandidat
#: als Uhrzeit ankam — mit einem anderen Muster als dem, das die Kandidaten
#: fand.
_WRITTEN_CLOCK_TIME = re.compile(r"\d{1,2}:\d{2}")

#: Datum und Uhrzeit im normalisierten Text, so wie die Pfade in `_aufloesen`
#: sie lesen. Ein Datum lesen sie nur verankert, als ganzen Text — dafuer
#: genuegen Grenzen. Ein ISO-Datum direkt hinter einem Punkt ("43.2026-07-31",
#: aus einem Tageswort in einem Wortsalat) ist keines. **Eine Uhrzeit sucht
#: Pfad 2 ohne Grenzen**, und die Pruefung muss dasselbe lesen: Mit Grenzen
#: uebersah sie `38:99` in "9838:99", der Pfad fand es und stuerzte ab
#: (15.09.2026, 17 von 12 000 erzeugten Eingaben).
_DATE_DMY = re.compile(r"(?<![\d.])(\d{1,2})\.(\d{1,2})\.(\d{4})(?!\d)")
_DATE_ISO = re.compile(r"(?<![\d.-])(\d{4})-(\d{2})-(\d{2})(?![\d-])")
_CLOCK_TIME = re.compile(r"(\d{1,2}):(\d{2})")

#: Die Muster von `_read_time`. Gelesen wird der Text, wie die Normalisierung
#: ihn schreibt: Ihr Schritt 2 nimmt das Leerzeichen hinter "Uhr" mit, aus
#: "10 Uhr auf 11 Uhr" wird "10:00auf 11:00". Deshalb gilt ein Wort auch direkt
#: hinter einer Ziffer, mitten in einem Wort ("Ablauf") nicht.
#:
#: Ein Datum aus Ziffern: ISO (auch angeklebt, "10:002026-10-16") und
#: Tag.Monat. mit oder ohne Jahr. Seine Zahlen sind keine Stunden.
_DATE_DIGITS = re.compile(r"\d{4}-\d{2}-\d{2}|(?<![\d.])\d{1,2}\.\d{1,2}\.(?:\d{4})?(?!\d)")

#: Ein Tag des Monats: eine Zahl mit Punkt ("den 20.") oder vor einem Monat
#: ("20. Oktober", "20 Okt"). Gruppe 2 ist der Monat, wenn einer folgt.
_DAY_OF_MONTH = re.compile(
    r"(?<![\d.,:])(\d{1,2})(?:\.(?!\d)\s*|\s+(?=(?:" + _MONTHS_AFTER_UM + r")\b))"
    r"(?:(" + _MONTHS_AFTER_UM + r")\b\.?)?",
    re.IGNORECASE,
)

#: Das Wort vor einem Tag des Monats, das ihn zum Tag macht: "auf den 20.".
_ARTICLE_BEFORE = re.compile(r"\b(?:den|dem|zum|vom|am)\s+$", re.IGNORECASE)

#: Eine nackte Zahl, die eine Stunde sein kann: nicht Teil eines Wortes, einer
#: Uhrzeit oder einer Kommazahl, keine Menge ("3 Tage", "10 Euro") — dieselben
#: Wortlisten wie `_HOUR_AFTER_UM`. Den Bereich 0..24 prueft der Leser.
_BARE_NUMBER = re.compile(
    r"(?<![\w.,:])(\d{1,2})(?![\w:]|[.,]\d)"
    r"(?!\s*(?:" + _QUANTITIES_AFTER_UM + r")\b)(?!\s*[%€°])",
    re.IGNORECASE,
)

#: Die Form "von X auf Y" / "von X nach Y" (Lage (b) von `_read_time`), in
#: drei Stuecken: "von" unmittelbar vor X; zwischen X und Y nichts als "auf"
#: oder "nach" — auch an X geklebt ("10:00auf 11:00"); hinter Y kein Wort,
#: das eine weitere Zeit, eine Wahl oder eine Verneinung anschliesst.
_FROM_BEFORE = re.compile(r"\bvon\s+$", re.IGNORECASE)
_TO_BETWEEN = re.compile(r"\s*(?:auf|nach)\s+", re.IGNORECASE)
_AFTER_TO_BREAK = re.compile(
    r"(?:(?<=\d)|\b)(?:auf|nach|oder|bzw|beziehungsweise|statt|anstatt|nicht|sonst|und)\b",
    re.IGNORECASE,
)

#: "auf" oder "nach" unmittelbar vor einer nackten Zahl: Sie ist die neue
#: Stunde ("auf 11"); allein ohne das Wort waere sie geraten ("Meeting 2").
_NEW_TIME_WORD_BEFORE = re.compile(r"\b(?:auf|nach)\s+$", re.IGNORECASE)

#: Die Einer der Zahlwoerter, fuer "einundzwanzig" bis "neunundzwanzig".
_UNIT_WORDS: tuple[str, ...] = (
    "ein", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun",
)

#: Eine Stunde als Zahlwort, null bis vierundzwanzig, je mit ASCII-Umschrift
#: ("zwoelf", "fuenfzehn"). Ohne "ein": Allein ist es ein Artikel ("ein
#: Termin"), und "ein Uhr" schreibt die Normalisierung schon als "1:00".
_HOUR_WORDS: dict[str, int] = {
    form: value
    for word, value in (
        ("null", 0), ("eins", 1), ("zwei", 2), ("zwo", 2), ("drei", 3), ("vier", 4),
        ("fünf", 5), ("sechs", 6), ("sieben", 7), ("acht", 8), ("neun", 9), ("zehn", 10),
        ("elf", 11), ("zwölf", 12), ("dreizehn", 13), ("vierzehn", 14), ("fünfzehn", 15),
        ("sechzehn", 16), ("siebzehn", 17), ("achtzehn", 18), ("neunzehn", 19),
        ("zwanzig", 20),
        *((f"{unit}undzwanzig", 21 + i) for i, unit in enumerate(_UNIT_WORDS[:4])),
    )
    for form in (word, _ascii_umschrift(word))
}

#: Ein Tag des Monats als Ordinalzahl ("den zehnten", "der erste"), mit jeder
#: Endung und ASCII-Umschrift. Keine Stunde: Die Grenze hinter dem Zahlwort
#: trennt "zehnten" von "zehn".
_ORDINAL_DAYS: dict[str, int] = {
    form + ending: value
    for stem, value in (
        ("erst", 1), ("zweit", 2), ("dritt", 3), ("viert", 4), ("fünft", 5), ("sechst", 6),
        ("siebt", 7), ("siebent", 7), ("acht", 8), ("neunt", 9), ("zehnt", 10), ("elft", 11),
        ("zwölft", 12), ("dreizehnt", 13), ("vierzehnt", 14), ("fünfzehnt", 15),
        ("sechzehnt", 16), ("siebzehnt", 17), ("achtzehnt", 18), ("neunzehnt", 19),
        ("zwanzigst", 20), ("dreißigst", 30), ("einunddreißigst", 31),
        *((f"{unit}undzwanzigst", 21 + i) for i, unit in enumerate(_UNIT_WORDS)),
    )
    for form in (stem, _ascii_umschrift(stem))
    for ending in ("e", "en", "er", "es", "em")
}

#: Ein Zahlwort, das eine Stunde sein kann: nicht Teil eines Wortes ("elfte",
#: "vierzehn" ist nicht "vier"), keine Menge ("zwei Stunden", "drei Tage").
_HOUR_WORD = re.compile(
    r"(?<![\w.,:])(" + _wortgruppe(*_HOUR_WORDS) + r")\b"
    r"(?!\s*(?:" + _QUANTITIES_AFTER_UM + r")\b)",
    re.IGNORECASE,
)

#: Minuten als Zahlwort ("dreissig", "fuenfzehn"), die keine Form der
#: Normalisierung aufnimmt: "elf Uhr dreissig" wird "11:00dreissig".
_MINUTE_WORD: str = r"(?:\w*(?:zig|ßig|ssig)|" + _wortgruppe(*_HOUR_WORDS) + r")\b"

#: Hinter einer geschriebenen Uhrzeit, auch angeklebt: Minuten als Zahlwort.
_MINUTES_AFTER_CLOCK = re.compile(r"\s*" + _MINUTE_WORD, re.IGNORECASE)

#: Hinter einer Stunde als Zahlwort: "Uhr" ("dreizehn Uhr"), Gruppe 1 sind
#: Minuten dahinter, als Ziffer oder Zahlwort ("dreizehn Uhr 30").
_UHR_AFTER_WORD = re.compile(r"\s+uhr\b(\s+(?:\d|" + _MINUTE_WORD + r"))?", re.IGNORECASE)

#: "halb", "viertel", "dreiviertel" (auch mit "vor"/"nach") vor einer Stunde,
#: die die Normalisierung nicht umgerechnet hat ("viertel nach 11", "halb
#: dreizehn"): Die Stunde allein waere eine andere Uhrzeit.
_FRACTION_BEFORE = re.compile(
    r"\b(?:halb|viertel|dreiviertel)(?:\s+(?:vor|nach))?\s+$", re.IGNORECASE,
)

#: Ein Tag des Monats als Ordinalzahl, dahinter ein Monat (Gruppe 2) oder das
#: Ende, ein Satzzeichen oder eine Ziffer ("den zehnten 11:00"). Folgt ein
#: anderes Wort, ist es ein Beiwort ("den ersten Termin") und kein Tag.
_ORDINAL_DAY = re.compile(
    r"\b(" + _wortgruppe(*_ORDINAL_DAYS) + r")"
    r"(?:\s+(" + _MONTHS_AFTER_UM + r")\b\.?|(?=\s*(?:$|[.,;!?)]|\d)))",
    re.IGNORECASE,
)

#: Ein Wochentag als Wort, fuer die Pruefung gegen ein Datum aus einem Tageswort.
_WEEKDAY_WORD = re.compile(r"\b(" + "|".join(_WOCHENTAGE) + r")\b", re.IGNORECASE)

#: Die Muster von `day_phrase`, aus denselben Listen wie die Fuzzy-Korrektur
#: und die Marker, je mit ASCII-Umschrift ("naechsten"). Ein Tag als Wort mit
#: seinen relativen Praefixen davor ("naechsten Freitag", "morgen").
_DAY_PHRASE = re.compile(
    r"\b(?:(?:" + _wortgruppe(*_RELATIVE_PRAEFIXE, *map(_ascii_umschrift, _RELATIVE_PRAEFIXE))
    + r")\s+)*(?:" + _wortgruppe(*_WOCHENTAGE, *_RELATIVE) + r")\b",
    re.IGNORECASE,
)

#: Jedes andere Wort, das an einem Tag mitrechnet: Tag, Monat, Einheit,
#: Praefix, Tageszeit ("Freitag naechste Woche", "Freitag abends") — und ein
#: Datum aus Ziffern.
_OTHER_DAY_WORD = re.compile(
    r"\b(?:" + _wortgruppe(*{
        form
        for word in (*_WOCHENTAGE, *_RELATIVE, *_MONATE, *_ZEITEINHEITEN,
                     *_RELATIVE_PRAEFIXE, *_TAGESZEITEN, "nacht")
        for form in (word, _ascii_umschrift(word))
    }) + r")\b|\d{1,2}\.\d{1,2}\.|\d{4}-\d{2}-\d{2}",
    re.IGNORECASE,
)

#: Das Vokabular des Parsers fuer wen aus ihm ableitet — heute die Positivform
#: des Verschiebens beim Timeline-Agenten. `words` ist jedes Wort, das der
#: Zeitparser als Zeitbezug fuehrt, abgeleitet aus seinen Listen, nicht
#: abgeschrieben: Wochentage, Monate und ihre Kurzformen, Tageswoerter,
#: Tageszeiten (auch die der Rueckfall-Uhrzeiten), Zeiteinheiten, relative
#: Praefixe, die geschuetzten Woerter der Fuzzy-Korrektur, Zahlwoerter,
#: Stunden als Zahlwort und Ordinaltage; dazu "mittag" und "nacht" wie in
#: `_OTHER_DAY_WORD`. `dayparts` sind die Tageszeiten aus `_TAGESZEITEN` mit
#: ihrem Versatz, unveraenderlich; der Parser selbst liest weiter
#: `_TAGESZEITEN`. Aendert sich eine Liste, aendert sich das Vokabular mit.
TIME_VOCABULARY: TimeVocabulary = TimeVocabulary(
    words=(
        *_WOCHENTAGE, *_MONATE, *_MONTHS_AFTER_UM.split("|"), *_RELATIVE, *_RELATIVE_DAYS,
        *_TAGESZEITEN, *_TAGESZEIT_UHRZEITEN, *_ZEITEINHEITEN, *_RELATIVE_PRAEFIXE,
        *_GESCHUETZTE_WOERTER, *_ZAHLWOERTER, *_HOUR_WORDS, *_ORDINAL_DAYS, "mittag", "nacht",
    ),
    hour_words=MappingProxyType(dict(_HOUR_WORDS)),
    ordinal_days=tuple(_ORDINAL_DAYS),
    relative_prefixes=_RELATIVE_PRAEFIXE,
    weekdays=tuple(_WOCHENTAGE),
    dayparts=MappingProxyType(dict(_TAGESZEITEN)),
)

#: Eine Uhrzeit mit Punkt, die kein Datum sein kann: Minuten 13..59, also kein
#: Monat ("11.30", "11.30." am Satzende). Nicht vor einer Menge oder einem Monat
#: ("2.50 Euro"), nicht als Teil einer laengeren Zahl ("11.30.2026") oder eines
#: Wortes ("11.30h"). "20.10." und "11.10" bleiben: Sie koennen ein Datum sein.
_DOTTED_CLOCK_TIME = re.compile(
    r"(?<![\w.,:])([01]?\d|2[0-3])\.(1[3-9]|[2-5]\d)(?!\w|[.,:]\d)"
    r"(?!\s*(?:" + _QUANTITIES_AFTER_UM + "|" + _MONTHS_AFTER_UM + r")\b)(?!\s*[%€°])",
    re.IGNORECASE,
)


class _HourReadingError(ValueError):
    """Ein Stundenleser hat seine eigene Zusicherung verletzt.

    Kein Eingabefehler: `_replace_hours` prueft die Stunde vorher, loest die
    Tageszeit ueber `_daypart_key` auf, und die Zaehlung geht per Bauart auf.
    Wer das hier sieht, hat eine Tabelle oder ein Muster geaendert, ohne die
    andere Seite mitzuziehen.
    """

    _MESSAGES: ClassVar[dict[str, str]] = {
        "hour_range": "Stunde {value!r} liegt ausserhalb 0..23",
        "daypart_unknown": "Tageszeit {value!r} steht nicht in _TAGESZEITEN",
        "count_mismatch": "Treffer und hinzugekommene Uhrzeiten weichen ab: {value!r}",
    }

    def __init__(self, kind: str, value: object) -> None:
        """Baut die Meldung aus der Art des Verstosses und dem Wert, der ihn zeigt."""
        super().__init__(self._MESSAGES[kind].format(value=value))


def _shift_hour_by_daypart(hour: int, daypart: str) -> int:
    """Verschiebt eine Stunde in die Tageshaelfte, die ihre Tageszeit nennt.

    Die Regel von Block 2 fuer *„3 Uhr nachmittags"*: Eine Stunde unter 12 mit
    einer Tageszeit ab Mittag bekommt 12 dazu, und *„12 nachts"* ist 0 Uhr. Die
    neuen Formen ohne "Uhr" rechnen hier, damit sie genau so lesen wie ihr
    Zwilling mit "Uhr".

    Vorbedingung: `hour` liegt in 0..23; `daypart` ist leer oder ein
    Schluessel aus `_TAGESZEITEN`. Der Aufrufer `_replace_hours` prueft beides
    vorher — ein Verstoss ist ein Programmfehler und wirft `_HourReadingError`.
    Nachbedingung: die Stunde in 0..23.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    if not 0 <= hour <= 23:
        raise _HourReadingError("hour_range", hour)
    if daypart and daypart not in _TAGESZEITEN:
        raise _HourReadingError("daypart_unknown", daypart)

    # ── Verarbeitung ─────────────────────────────────────────────────
    offset: int = _TAGESZEITEN[daypart] if daypart else 0
    if hour < 12 and offset >= 12:
        hour += offset
    elif hour == 12 and daypart == "nachts":
        hour = 0

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if not 0 <= hour <= 23:
        raise _HourReadingError("hour_range", (hour, daypart))
    return hour


def _daypart_key(word: str) -> str:
    """Der Schluessel aus `_TAGESZEITEN`, den ein Tageszeit-Treffer meint.

    Die Muster vergleichen mit `re.IGNORECASE`, und `re` faltet dabei weiter
    als `str.lower()`: `ı` (U+0131) und `İ` (U+0130) treffen ein `i`, `ſ`
    (U+017F) ein `s`, aber `lower()` fuehrt von dort nicht zum Schluessel
    zurueck. Bis zum 15.09.2026 warf *„morgen um 3 nachmıttags"* deshalb
    `_HourReadingError` — gefunden von der zweiten Kontrolle. Aufgeloest wird
    mit derselben Faltung, mit der das Muster traf.

    Vorbedingung: `word` hat unter `re.IGNORECASE` einen Schluessel aus
        `_TAGESZEITEN` getroffen.
    Nachbedingung: der Schluessel, den `word` unter derselben Faltung
        vollstaendig trifft — sonst `_HourReadingError`.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    for key in _TAGESZEITEN:
        if re.fullmatch(re.escape(key), word, re.IGNORECASE):
            return key

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    raise _HourReadingError("daypart_unknown", word)


def _replace_hours(text: str, pattern: re.Pattern, daypart: Optional[str]) -> str:
    """Schreibt jeden Stundentreffer eines Musters als `H:00`.

    Der gemeinsame Rumpf von `_read_hour_before_daypart` und `_read_hour_after_um`.
    Das Muster liefert die Stunde in Gruppe 1; die Tageszeit kommt entweder
    aus Gruppe 2 des Treffers (`daypart` ist dann None) oder aus dem
    Ausdruck als Ganzem.

    Vorbedingung: `pattern` hat die Stunde in Gruppe 1, bei `daypart=None`
        die Tageszeit in Gruppe 2; sonst ist `daypart` leer oder ein
        Schluessel aus `_TAGESZEITEN`.
    Nachbedingung: Jeder Treffer mit Stunde 0..23 steht als `H:00`, jeder mit
        einer groesseren Zahl unberuehrt. Nachgezaehlt mit
        `_WRITTEN_CLOCK_TIME`: Das Ergebnis traegt genau so viele Uhrzeiten
        mehr, wie es Treffer gab — sonst `_HourReadingError`.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    candidates: int = sum(1 for m in pattern.finditer(text) if int(m.group(1)) <= 23)
    if candidates == 0:
        return text

    # ── Verarbeitung ─────────────────────────────────────────────────
    def replace(match: re.Match) -> str:
        hour: int = int(match.group(1))
        if hour > 23:
            return match.group(0)
        word: str = _daypart_key(match.group(2)) if daypart is None else daypart
        return f"{_shift_hour_by_daypart(hour, word)}:00"

    result: str = pattern.sub(replace, text)

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    added: int = len(_WRITTEN_CLOCK_TIME.findall(result)) - len(_WRITTEN_CLOCK_TIME.findall(text))
    if added != candidates:
        raise _HourReadingError("count_mismatch", (candidates, added, text, result))
    return result


def _impossible_values(normalized: str) -> list[str]:
    """Die Datums- und Uhrzeitangaben im normalisierten Text, die es nicht gibt.

    Die Pfade in `_aufloesen` bauen ihr `datetime` aus dem normalisierten Text,
    ohne die Werte zu pruefen. Bis zum 15.09.2026 riss deshalb ein unmoeglicher
    Tag oder eine unmoegliche Uhrzeit eine `ValueError` bis zum Aufrufer:
    *„am 31.09. um 10"*, *„29.02.2027"*, *„morgen um 24 Uhr"*, *„morgen 14:75"*.
    Der Termindienst faengt sie nicht; statt der Rueckfrage nach dem Datum kam
    ein Fehler des Dispatch.

    Vorbedingung: `normalized` ist das Ergebnis von `_text_normalisieren`.
    Nachbedingung: je unmoeglicher Angabe ihr Wortlaut, in der Reihenfolge
        Datum (Tag.Monat.Jahr), Datum (ISO), Uhrzeit; sonst leer.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    def is_calendar_day(year: int, month: int, day: int) -> bool:
        if not (1 <= year <= 9999 and 1 <= month <= 12):
            return False
        return 1 <= day <= calendar.monthrange(year, month)[1]

    found: list[str] = [
        f"{d}.{m}.{y}" for d, m, y in _DATE_DMY.findall(normalized)
        if not is_calendar_day(int(y), int(m), int(d))
    ]
    found += [
        f"{y}-{m}-{d}" for y, m, d in _DATE_ISO.findall(normalized)
        if not is_calendar_day(int(y), int(m), int(d))
    ]
    found += [
        f"{h}:{mi}" for h, mi in _CLOCK_TIME.findall(normalized)
        if int(h) > 23 or int(mi) > 59
    ]

    # ── Ausgabe ──────────────────────────────────────────────────────
    return found


def _day_of_month(day: int, month_word: Optional[str], today: date) -> Optional[date]:
    """Der Tag, den "den 20." oder "20. Oktober" meint — der naechste ab heute.

    Ohne Monat: dieser Monat, wenn der Tag noch kommt, sonst der naechste.
    Mit Monat: dieses Jahr, wenn der Tag noch kommt, sonst das naechste.

    Vorbedingung: `month_word` ist leer oder ein Treffer aus `_MONTHS_AFTER_UM`.
    Nachbedingung: ein Kalendertag ab `today`, oder None.
    Fehlerfaelle: None fuer einen Tag, den es nicht gibt ("den 31." vor einem
        Monat mit 30 Tagen, "den 0.") — der Aufrufer zaehlt ihn als Zweifel.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not 1 <= day <= 31:
        return None
    month: int = 0
    if month_word:
        month = 1 + [name[:3] for name in _MONATE].index(month_word.lower()[:3])

    # ── Verarbeitung ────────────────────────────
    year: int = today.year
    if not month:
        month = today.month if day >= today.day else today.month % 12 + 1
        year += 1 if month < today.month else 0
    elif (month, day) < (today.month, today.day):
        year += 1

    # ── Ausgabe-Verifikation ────────────────────
    if day > calendar.monthrange(year, month)[1]:
        return None
    return date(year, month, day)


def _spelled_hours(rest: str) -> tuple[list[tuple[int, int, tuple[int, int], bool]], bool]:
    """Die Stunden als Zahlwort im Rest der Lesung ("auf elf", "dreizehn Uhr").

    Gezaehlt wird jedes Zahlwort null bis vierundzwanzig aus `_HOUR_WORD`:
    nicht Teil eines Wortes, also keine Ordinalzahl ("zehnten"), und keine
    Menge ("zwei Stunden"). "ein" zaehlt nicht. Steht "Uhr" dahinter, ist die
    Stunde geschrieben, und ihre Stelle reicht bis hinter "Uhr" ("von dreizehn
    Uhr auf vierzehn Uhr" ist dann die Form "von X auf Y"). Bis "zwoelf Uhr"
    hat die Normalisierung das schon als Uhrzeit geschrieben.

    Vorbedingung: `rest` ist der normalisierte Text mit ausgeblendeten
        Uhrzeiten, Daten und Tagen des Monats.
    Nachbedingung: je Zahlwort (Anfang, Ende, (Stunde, 0), geschrieben) mit
        Stellen in `rest`; dazu wahr, wenn hinter "Uhr" Minuten stehen, die
        keine Uhrzeit aufgenommen hat ("dreizehn Uhr dreissig") — ein Zweifel.
    Fehlerfaelle: kein Text wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(rest, str):
        msg: str = f"_spelled_hours: kein Text ({type(rest).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    found: list[tuple[int, int, tuple[int, int], bool]] = []
    doubt: bool = False
    for match in _HOUR_WORD.finditer(rest):
        uhr: Optional[re.Match] = _UHR_AFTER_WORD.match(rest, match.end())
        end: int = match.end()
        if uhr:
            end = uhr.start(1) if uhr.group(1) else uhr.end()
            doubt = doubt or bool(uhr.group(1))
        found.append((match.start(), end, (_HOUR_WORDS[match.group(1).lower()], 0), bool(uhr)))

    # ── Ausgabe-Verifikation ────────────────────
    if any(not 0 <= start < end <= len(rest) for start, end, _, _ in found):
        msg = f"_spelled_hours: Stelle ausserhalb des Textes ({found}, {rest!r})"
        raise ValueError(msg)
    return found, doubt


def _ordinal_days(normalized: str, today: date) -> list[Optional[date]]:
    """Die Tage des Monats als Ordinalzahl ("auf den zehnten", "zehnten Oktober").

    Ein Tag ist die Ordinalzahl aus `_ORDINAL_DAY`, wenn ein Monat folgt oder
    ein Artikel davor steht ("den", "zum"); steht keiner davor ("zehnten
    11:00", aus "am zehnten um 11 Uhr" — die Normalisierung nimmt "am"
    heraus), ist sie ein Zweifel. Folgt ein anderes Wort, ist sie ein Beiwort
    ("den ersten Termin") und zaehlt nicht.

    Vorbedingung: `normalized` ist das Ergebnis von `_text_normalisieren`.
    Nachbedingung: je Ordinalzahl ein Tag ab `today` (`_day_of_month`), oder
        None fuer einen Zweifel und einen Tag, den es nicht gibt.
    Fehlerfaelle: kein Text wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(normalized, str):
        msg: str = f"_ordinal_days: kein Text ({type(normalized).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    named: list[Optional[date]] = [
        _day_of_month(_ORDINAL_DAYS[m.group(1).lower()], m.group(2), today)
        if m.group(2) or _ARTICLE_BEFORE.search(normalized[:m.start()]) else None
        for m in _ORDINAL_DAY.finditer(normalized)
    ]

    # ── Ausgabe-Verifikation ────────────────────
    if any(day is not None and day < today for day in named):
        msg = f"_ordinal_days: Tag vor heute ({named}, {today})"
        raise ValueError(msg)
    return named


def _stated_hour(
    normalized: str, found: list[tuple[int, int, tuple[int, int], bool]],
) -> frozenset[tuple[int, int]]:
    """Die Stunde, die ein Text als neue nennt — leer, wenn er keine so nennt.

    Zwei Lagen, keine weitere:
    (a) Der Text traegt genau eine Stunde; dieselbe zweimal ist eine. Sie ist
        die neue, wenn sie geschrieben ist ("11 Uhr", "um 11", "11:30") oder
        als nackte Zahl unmittelbar hinter "auf"/"nach" steht ("auf 11"). Eine
        nackte Zahl sonst ("Meeting 2") nennt keine.
    (b) Der Text traegt genau zwei Stunden in der Form "von X auf Y" oder "von
        X nach Y": "von" unmittelbar vor X, zwischen X und Y nichts als "auf"
        oder "nach", hinter Y kein "auf", "nach", "oder", "bzw.", "statt",
        "nicht", "sonst" oder "und". Y ist die neue. Was vor "von" steht,
        zaehlt nicht ("auf Freitag von 10 auf 11 Uhr").
    Jede andere Lage mit Stunden nennt keine — auch eine Form, die hier nicht
    steht ("auf 10 oder 11 Uhr", "auf 11, nicht auf 10 Uhr", "von 10 bis 12").

    Vorbedingung: `found` sind die Stunden aus `_read_time` als (Anfang, Ende,
        (Stunde, Minute), geschrieben), mit Stellen in `normalized`.
    Nachbedingung: leer oder genau eine Stunde aus `found`.
    Fehlerfaelle: eine Stelle ausserhalb des Textes wirft `ValueError` — die
        Woerter um die Stunde waeren sonst falsch gelesen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if any(not 0 <= start < end <= len(normalized) for start, end, _, _ in found):
        msg: str = f"_stated_hour: Stelle ausserhalb des Textes ({found}, {normalized!r})"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    ordered: list[tuple[int, int, tuple[int, int], bool]] = sorted(found)
    values: frozenset[tuple[int, int]] = frozenset(hour for _, _, hour, _ in ordered)
    stated: frozenset[tuple[int, int]] = frozenset()
    if len(values) == 1 and any(
        written or _NEW_TIME_WORD_BEFORE.search(normalized[:start])
        for start, _, _, written in ordered
    ):
        stated = values
    elif len(ordered) == 2:
        (x_start, x_end, _, _), (y_start, y_end, y_hour, _) = ordered
        if (
            _FROM_BEFORE.search(normalized[:x_start])
            and _TO_BETWEEN.fullmatch(normalized[x_end:y_start])
            and not _AFTER_TO_BREAK.search(normalized[y_end:])
        ):
            stated = frozenset({y_hour})

    # ── Ausgabe-Verifikation ────────────────────
    if len(stated) > 1 or not stated <= values:
        msg = f"_stated_hour: keine Stunde des Textes ({stated}, {values})"
        raise ValueError(msg)
    return stated


def _read_time(normalized: str, today: date) -> TimeReading:
    """Liest Stunden und Tage des Monats aus dem normalisierten Text.

    Als Stunde zaehlt jede Form:
    - jede geschriebene Uhrzeit (`H:MM` — die Normalisierung macht daraus
      "11 Uhr", "um 11", "elf Uhr", "halb elf", "viertel nach elf",
      "dreiviertel elf");
    - jede nackte Zahl 0..24, die kein Datum, keine Menge und nicht Teil eines
      Wortes ist ("von 10 bis 12 Uhr", "zwischen 10 und 11 Uhr", "10–12 Uhr");
    - jedes Zahlwort "null" bis "vierundzwanzig" (ausser "ein"), das keine
      Menge und nicht Teil eines Wortes ist ("auf zehn, nicht auf elf Uhr",
      "dreizehn Uhr") — `_spelled_hours`.
    Keine Stunde sind: "20.10.", ein ISO-Datum, eine Zahl mit Punkt oder vor
    einem Monat, und eine Ordinalzahl ("den zehnten", `_ordinal_days`). Sie
    sind ein Tag ("auf den 20.", "20. Oktober", "auf den zehnten"), wenn ein
    Artikel davor oder ein Monat danach steht, sonst ein Zweifel ("auf 11.").
    Ein Zweifel ist auch: eine Stunde hinter "halb", "viertel" oder
    "dreiviertel", die die Normalisierung nicht umgerechnet hat ("viertel nach
    11"), und Minuten als Zahlwort hinter einer Uhrzeit ("elf Uhr dreissig").

    Welche Stunde der Text als neue nennt, entscheidet `_stated_hour` an den
    Stellen der Stunden: Lage (a) genau eine, Lage (b) genau zwei in der Form
    "von X auf Y". Nennt der Text Stunden, aber keine davon so, ist er
    unentschieden.

    Vorbedingung: `normalized` ist das Ergebnis von `_text_normalisieren`.
    Nachbedingung: eine `TimeReading`; `stated` ist leer oder traegt eine
        Stunde aus `hours`; `undecided` ist wahr genau dann, wenn `hours`
        nicht leer und `stated` leer ist.
    Fehlerfaelle: kein Text wirft `TypeError`. Ein Ausblenden, das die Laenge
        aendert, wirft `ValueError` — die Stellen der Stunden zeigten sonst
        neben "von", "auf" und "nach".
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(normalized, str):
        msg: str = f"_read_time: kein Text ({type(normalized).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    dates_blanked: str = _DATE_DIGITS.sub(lambda m: " " * len(m.group(0)), normalized)
    written_at: list[tuple[int, int, tuple[int, int], bool]] = [
        (m.start(), m.end(), (int(m.group(1)), int(m.group(2))), True)
        for m in _CLOCK_TIME.finditer(dates_blanked)
    ]
    rest: str = _CLOCK_TIME.sub(lambda m: " " * len(m.group(0)), dates_blanked)
    named: list[Optional[date]] = [
        _day_of_month(int(m.group(1)), m.group(2), today)
        if m.group(2) or _ARTICLE_BEFORE.search(rest[:m.start()]) else None
        for m in _DAY_OF_MONTH.finditer(rest)
    ]
    rest = _DAY_OF_MONTH.sub(lambda m: " " * len(m.group(0)), rest)
    spelled, minutes_doubt = _spelled_hours(rest)
    every: list[tuple[int, int, tuple[int, int], bool]] = written_at + spelled + [
        (m.start(1), m.end(1), (int(m.group(1)), 0), False)
        for m in _BARE_NUMBER.finditer(rest) if int(m.group(1)) <= 24
    ]
    named += _ordinal_days(normalized, today)
    doubt: bool = (
        None in named or minutes_doubt
        or any(_MINUTES_AFTER_CLOCK.match(dates_blanked, end) for _, end, _, _ in written_at)
        or any(_FRACTION_BEFORE.search(normalized[:start]) for start, _, _, _ in every)
    )
    stated: frozenset[tuple[int, int]] = _stated_hour(normalized, every)
    reading: TimeReading = TimeReading(
        hours=frozenset(hour for _, _, hour, _ in every),
        stated=stated,
        undecided=bool(every) and not stated,
        days=frozenset(day for day in named if day is not None),
        doubtful=doubt,
    )

    # ── Ausgabe-Verifikation ────────────────────
    if len(rest) != len(normalized):
        msg = f"_read_time: Ausblenden aenderte die Laenge ({normalized!r} -> {rest!r})"
        raise ValueError(msg)
    return reading


def read_time(text: str, today: Optional[date] = None) -> TimeReading:
    """Welche Stunden und Tage des Monats ein Auftrag nennt — fuer das Verschieben.

    Gelesen wird der Text ohne Fuzzy-Korrektur: Die zieht "und" auf Distanz 2
    zu "juni", und aus "zwischen 10 und 11 Uhr" wuerde ein Datum mit einer
    Uhrzeit. Die Umlaute werden wie dort hergestellt ("zwoelf Uhr").

    Vorbedingung: `text` ist ein Text, leer erlaubt.
    Nachbedingung: die `TimeReading` von `_read_time`; leer fuer leeren Text.
    Fehlerfaelle: kein Text wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(text, str):
        msg: str = f"read_time: kein Text ({type(text).__name__})"
        raise TypeError(msg)
    if not text.strip():
        return TimeReading()

    # ── Verarbeitung ────────────────────────────
    day: date = today or _heute_lokal()
    reading: TimeReading = _read_time(
        _text_normalisieren(_umlaute_herstellen(text), heute=day), day,
    )

    # ── Ausgabe ─────────────────────────────────
    return reading


def day_phrase(text: str) -> str:
    """Der Tagesausdruck eines Satzes allein ("Freitag"), wenn er der einzige Zeitbezug ist.

    dateparser liest nur einen Zeitausdruck, keinen Satz: Fuer "Verschieb den
    Zahnarzt auf Freitag." gibt `zeit_parsen_vektor` einen erkannten Tag ohne
    Datum. Der Tagesausdruck allein ist das, was die Klassifikation sonst als
    Zeitausdruck liefert. Herausgeschnitten wird er nur, wenn ausserhalb kein
    weiteres Wort am Tag mitrechnet — sonst waere der Tag geraten ("Freitag
    naechste Woche", "heute Freitag"). Uhrzeiten zaehlen nicht mit: Die liest
    `read_time`.

    Vorbedingung: `text` ist ein Text, leer erlaubt.
    Nachbedingung: ein Wochentag oder Tageswort mit seinen relativen Praefixen,
        so wie er im Text steht; leer, wenn es keinen gibt oder ausserhalb ein
        weiteres Tageswort, eine Einheit, ein Monat, eine Tageszeit oder ein
        Datum aus Ziffern steht.
    Fehlerfaelle: kein Text wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(text, str):
        msg: str = f"day_phrase: kein Text ({type(text).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    found: Optional[re.Match[str]] = _DAY_PHRASE.search(text)
    rest: str = f"{text[:found.start()]} {text[found.end():]}" if found else ""
    phrase: str = found.group(0) if found and not _OTHER_DAY_WORD.search(rest) else ""

    # ── Ausgabe ─────────────────────────────────
    return phrase


#: Der Versatz je Stamm eines relativen Praefixes, in Zeitraeumen. Die
#: Schluessel sind die Staemme aus `_RELATIVE_PRAEFIX_STAEMME`; ein Stamm, der
#: dort hinzukommt und hier fehlt, haelt den Import an (unten).
_PERIOD_STEM_OFFSETS: dict[str, int] = {
    "übernächste": 2, "nächste": 1, "kommende": 1,
    "letzte": -1, "vorige": -1, "vergangene": -1,
}
if set(_PERIOD_STEM_OFFSETS) != set(_RELATIVE_PRAEFIX_STAEMME):
    _msg: str = (
        "zeitparser: _PERIOD_STEM_OFFSETS und _RELATIVE_PRAEFIX_STAEMME nennen "
        "verschiedene Staemme"
    )
    raise RuntimeError(_msg)

#: Jede Form eines relativen Praefixes in ASCII-Umschrift mit ihrem Versatz,
#: abgeleitet aus den Staemmen und Endungen, nicht abgeschrieben.
_PERIOD_PREFIX_OFFSETS: dict[str, int] = {
    _ascii_umschrift(stem + ending): offset
    for stem, offset in _PERIOD_STEM_OFFSETS.items()
    for ending in _PRAEFIX_ENDUNGEN
}

#: Worte, die einen Zeitraum begleiten, ohne ihn zu verschieben.
_PERIOD_FILLERS: frozenset[str] = frozenset({
    "im", "in", "am", "an", "fuer", "ueber", "uebers", "den", "die", "das", "der", "dem",
    "des", "diese", "diesen", "dieser", "dieses", "diesem",
    "ganze", "ganzen", "ganzer", "ganzes", "ganzem",
})

#: Zahlwoerter eines Abstands ("in zwei Wochen"), abgeleitet aus `_ZAHLWOERTER`.
_PERIOD_COUNTS: dict[str, int] = {
    **{_ascii_umschrift(word): value for word, value in _ZAHLWOERTER.items()},
    "eine": 1, "einer": 1, "einem": 1,
}

#: Die Monatsnamen in ASCII-Umschrift mit ihrer Nummer, abgeleitet aus `_MONATE`.
_PERIOD_MONTHS: dict[str, int] = {
    _ascii_umschrift(name): number for number, name in enumerate(_MONATE, start=1)
}

_PERIOD_WEEK: frozenset[str] = frozenset({"woche", "wochen"})
_PERIOD_MONTH: frozenset[str] = frozenset({"monat", "monate", "monaten"})
_PERIOD_PLURALS: frozenset[str] = frozenset({"wochen", "monate", "monaten"})
_PERIOD_WEEKEND: str = "wochenende"
_PERIOD_NOUNS: frozenset[str] = (
    _PERIOD_WEEK | _PERIOD_MONTH | {_PERIOD_WEEKEND} | frozenset(_PERIOD_MONTHS)
)

#: Ein Jahr hinter einem Monatsnamen ("November 2026").
_PERIOD_YEAR_LENGTH: int = 4


def _shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    """Jahr und Monat, um `offset` Monate verschoben, ueber Jahresgrenzen.

    Vorbedingung: `month` liegt in 1 bis 12.
    Nachbedingung: `(jahr, monat)` mit `monat` in 1 bis 12.
    Fehlerfaelle: ein Monat ausserhalb von 1 bis 12 wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not 1 <= month <= 12:
        msg: str = f"_shift_month: Monat {month} ausserhalb von 1 bis 12"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    index: int = year * 12 + (month - 1) + offset
    shifted: tuple[int, int] = (index // 12, index % 12 + 1)

    # ── Ausgabe-Verifikation ────────────────────
    if not 1 <= shifted[1] <= 12:
        msg = f"_shift_month: Ergebnis {shifted} ohne gueltigen Monat"
        raise RuntimeError(msg)
    return shifted


def _period_offset(words: list[str]) -> Optional[tuple[int, bool]]:
    """Der Versatz der Worte vor dem Zeitraum, und ob er ein Abstand ist.

    Vorbedingung: `words` sind die Worte vor dem Zeitraum, klein, in
        ASCII-Umschrift.
    Nachbedingung: `(versatz, abstand)` — `abstand` ist wahr bei "in zwei
        Wochen"; `None`, wenn ein Wort weder Fuellwort noch Praefix noch Zahl
        ist, wenn zwei verschieben oder eine Zahl ohne "in" steht.
    Fehlerfaelle: keine — ein unbekanntes Wort heisst *kein Zeitraum*.
    """
    # ── Eingabe-Validierung ─────────────────────
    unknown: list[str] = [
        w for w in words
        if w not in _PERIOD_FILLERS and w not in _PERIOD_PREFIX_OFFSETS
        and w not in _PERIOD_COUNTS and not w.isdigit()
    ]
    if unknown:
        return None

    # ── Verarbeitung ────────────────────────────
    offsets: list[int] = [_PERIOD_PREFIX_OFFSETS[w] for w in words if w in _PERIOD_PREFIX_OFFSETS]
    counts: list[int] = [
        _PERIOD_COUNTS[w] if w in _PERIOD_COUNTS else int(w)
        for w in words if w in _PERIOD_COUNTS or w.isdigit()
    ]
    if len(offsets) + len(counts) > 1 or (counts and "in" not in words):
        return None
    result: tuple[int, bool] = (counts[0], True) if counts else (sum(offsets), False)

    # ── Ausgabe-Verifikation ────────────────────
    if result[1] and result[0] < 1:
        msg: str = f"_period_offset: Abstand {result[0]} aus {words}"
        raise RuntimeError(msg)
    return result


def _period_request(words: list[str], year: Optional[int]) -> Optional[tuple[str, int]]:
    """Welcher Zeitraum mit welchem Versatz gemeint ist — oder keiner.

    Das letzte Wort ist der Zeitraum (ein verschriebener Monatsname wird
    korrigiert), die Worte davor verschieben ihn (`_period_offset`). Ein
    Abstand ("in zwei Wochen") gilt nur fuer Woche und Monat, eine Mehrzahl
    ("Wochen") nur mit Abstand, ein Jahr nur hinter einem Monatsnamen ohne
    Praefix.

    Vorbedingung: `words` klein, in ASCII-Umschrift, ohne das Jahr.
    Nachbedingung: `(zeitraum, versatz)` mit `zeitraum` aus `_PERIOD_NOUNS`;
        `None`, wenn die Worte keinen Zeitraum nennen.
    Fehlerfaelle: keine — was nicht passt, ist *kein Zeitraum*.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not words:
        return None
    noun: str = words[-1]
    if noun not in _PERIOD_NOUNS:
        noun = _ascii_umschrift(_fuzzy_korrektur(noun).lower())
    shift: Optional[tuple[int, bool]] = _period_offset(words[:-1])
    if noun not in _PERIOD_NOUNS or shift is None:
        return None

    # ── Verarbeitung ────────────────────────────
    offset, is_distance = shift
    fits: bool = (
        (not is_distance or noun in _PERIOD_WEEK | _PERIOD_MONTH)
        and (is_distance or noun not in _PERIOD_PLURALS)
        and (year is None or (noun in _PERIOD_MONTHS and offset == 0))
        and (noun not in _PERIOD_MONTHS or abs(offset) <= 1)
    )

    # ── Ausgabe-Verifikation ────────────────────
    if not fits:
        return None
    if noun not in _PERIOD_NOUNS:
        msg: str = f"_period_request: {noun!r} ist kein Zeitraum"
        raise RuntimeError(msg)
    return noun, offset


def _month_name_year(month: int, offset: int, year: Optional[int], today: date) -> int:
    """Das Jahr eines Monatsnamens, gelesen in der Richtung seines Praefixes.

    Vorbedingung: `month` liegt in 1 bis 12, `offset` in -1 bis 1
        (`_period_request`).
    Nachbedingung: ohne Praefix `year` oder das laufende Jahr; mit *naechsten*
        das Jahr des naechsten Vorkommens nach dem laufenden Monat, mit
        *letzten* das des letzten davor.
    Fehlerfaelle: ein `month` oder `offset` ausserhalb wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not 1 <= month <= 12 or abs(offset) > 1:
        msg: str = f"_month_name_year: Monat {month} oder Versatz {offset} ausserhalb"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    base_year: int = year if year is not None else today.year
    period_year: int = base_year
    if offset == 1 and month <= today.month:
        period_year += 1
    elif offset == -1 and month >= today.month:
        period_year -= 1

    # ── Ausgabe-Verifikation ────────────────────
    if abs(period_year - base_year) > 1:
        msg = f"_month_name_year: Jahr {period_year} zu weit von {base_year}"
        raise RuntimeError(msg)
    return period_year


def _period_dates(
    noun: str, offset: int, year: Optional[int], today: date,
) -> tuple[date, date]:
    """Erster und letzter Tag eines Zeitraums, gezaehlt von `today`.

    Vorbedingung: `noun` und `offset` kommen aus `_period_request`.
    Nachbedingung: `(erster, letzter)`, beide eingeschlossen, `erster <= letzter`.
    Fehlerfaelle: ein `noun` ausserhalb von `_PERIOD_NOUNS` wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if noun not in _PERIOD_NOUNS:
        msg: str = f"_period_dates: {noun!r} ist kein Zeitraum"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    week_start: date = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    if noun in _PERIOD_WEEK:
        period: tuple[date, date] = (week_start, week_start + timedelta(days=6))
    elif noun == _PERIOD_WEEKEND:
        period = (week_start + timedelta(days=5), week_start + timedelta(days=6))
    else:
        if noun in _PERIOD_MONTH:
            period_year, month = _shift_month(today.year, today.month, offset)
        else:
            month = _PERIOD_MONTHS[noun]
            period_year = _month_name_year(month, offset, year, today)
        period = (date(period_year, month, 1),
                  date(period_year, month, calendar.monthrange(period_year, month)[1]))

    # ── Ausgabe-Verifikation ────────────────────
    if period[1] < period[0]:
        msg = f"_period_dates: {period[0]} nach {period[1]}"
        raise RuntimeError(msg)
    return period


def named_period(text: str, today: date) -> Optional[tuple[date, date]]:
    """Der Zeitraum, den ein Ausdruck nennt: Woche, Wochenende, Monat, Monatsname.

    Ein Zeitraum ist kein Tag: *im November* sind alle Tage des Novembers,
    *diese Woche* Montag bis Sonntag, *am Wochenende* Samstag und Sonntag. Ein
    Ausdruck, der einen Tag nennt (*morgen*, *am Freitag*, *am 17.10.*,
    *6. November*), nennt hier keinen — den liest `zeit_parsen`. Gelesen wird
    der ganze Ausdruck: Steht ein Wort darin, das weder Zeitraum noch Praefix
    noch Fuellwort ist, nennt er keinen Zeitraum.

    Die Richtung: Ohne Praefix gilt der laufende Zeitraum, bei einem
    Monatsnamen der des laufenden Jahres — auch wenn er vorbei ist (*im
    September*, gefragt im Oktober, ist dieser September). *naechste*,
    *kommende* schieben einen Zeitraum vor, *uebernaechste* zwei, *letzte*,
    *vorige*, *vergangene* einen zurueck. Ein Monatsname mit *naechsten* ist
    sein naechstes Vorkommen nach dem laufenden Monat, mit *letzten* das
    letzte davor. *in zwei Wochen* ist die Woche, *in drei Monaten* der
    Monat, in die der Abstand faellt. Das Wochenende ist das der Woche, in
    der `today` liegt, *naechstes Wochenende* das der naechsten Woche.

    Vorbedingung: `text` ist ein Text; `today` ist der heutige Tag in Ortszeit.
    Nachbedingung: `(erster, letzter)` mit `erster <= letzter`, beide
        eingeschlossen, hoechstens 31 Tage; `None`, wenn der Ausdruck keinen
        Zeitraum nennt.
    Fehlerfaelle: ein `text`, der kein Text ist, oder ein `today`, das kein
        `date` ist, wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(text, str):
        msg: str = f"named_period: kein Text ({type(text).__name__})"
        raise TypeError(msg)
    if not isinstance(today, date):
        msg = f"named_period: kein Datum ({type(today).__name__})"
        raise TypeError(msg)
    words: list[str] = re.findall(r"[a-z0-9]+", _ascii_umschrift(text.lower()))
    year: Optional[int] = None
    if words and len(words[-1]) == _PERIOD_YEAR_LENGTH and words[-1].isdigit():
        year = int(words.pop())
    request: Optional[tuple[str, int]] = _period_request(words, year)
    if request is None:
        return None

    # ── Verarbeitung ────────────────────────────
    period: tuple[date, date] = _period_dates(request[0], request[1], year, today)

    # ── Ausgabe-Verifikation ────────────────────
    if not 0 <= (period[1] - period[0]).days <= 30:
        msg = f"named_period: Zeitraum {period[0]} bis {period[1]} aus {text!r}"
        raise RuntimeError(msg)
    logger.debug(f"Zeitparser: '{text}' nennt den Zeitraum {period[0]} bis {period[1]}")
    return period


def dotted_clock_times(text: str) -> str:
    """Schreibt eine Uhrzeit mit Punkt, die kein Datum sein kann, mit Doppelpunkt.

    Fuer das Verschieben: Aus "auf 11.30." am Satzende macht die
    Normalisierung das Datum "11.30.2026", und der Parser meldet einen Tag,
    den es nicht gibt. Umgeschrieben wird nur `_DOTTED_CLOCK_TIME`: Stunde
    0..23, Minuten 13..59, also nie ein Monat. "20.10." und "11.10" bleiben,
    sie koennen ein Datum sein. Die Positivform des Verschiebens (beim
    Timeline-Agenten) liest den Text davor.

    Vorbedingung: `text` ist ein Text, leer erlaubt.
    Nachbedingung: jede solche Form steht als `H:MM`, sonst ist der Text gleich.
    Fehlerfaelle: kein Text wirft `TypeError`; weicht die Zahl der neuen
        Uhrzeiten von der der Treffer ab, wirft es `_HourReadingError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(text, str):
        msg: str = f"dotted_clock_times: kein Text ({type(text).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    count: int = len(_DOTTED_CLOCK_TIME.findall(text))
    result: str = _DOTTED_CLOCK_TIME.sub(r"\1:\2", text)

    # ── Ausgabe-Verifikation ────────────────────
    added: int = len(_WRITTEN_CLOCK_TIME.findall(result)) - len(_WRITTEN_CLOCK_TIME.findall(text))
    if added != count:
        raise _HourReadingError("count_mismatch", (count, added, text, result))
    return result


def _iso_dates_as_dmy(text: str) -> str:
    """Schreibt jedes ISO-Datum als Tag.Monat.Jahr, bevor der Text an dateparser geht.

    Block 0b schreibt ein Tageswort als ISO-Datum, und Pfad 1 liest das
    selbst. Die Pfade 2 und 3 geben es an dateparser — und der liest es unter
    `DATE_ORDER: DMY` als Jahr-Tag-Monat: `2026-08-01` ergab den 08.01.2026,
    `2026-07-31` nichts (dateparser 1.4.2, gemessen 15.09.2026). Getroffen hat
    es jeden Ausdruck mit der Uhrzeit vor dem Tageswort, *„9 Uhr morgen"*.

    Vorbedingung: `text` geht als Naechstes an dateparser.
    Nachbedingung: kein ISO-Datum mehr im Text; je ersetztem eines mehr in
        der Form Tag.Monat.Jahr — sonst `_HourReadingError`.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    iso: int = len(_DATE_ISO.findall(text))
    if iso == 0:
        return text

    # ── Verarbeitung ─────────────────────────────────────────────────
    result: str = _DATE_ISO.sub(lambda m: f"{m.group(3)}.{m.group(2)}.{m.group(1)}", text)

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    added: int = len(_DATE_DMY.findall(result)) - len(_DATE_DMY.findall(text))
    if _DATE_ISO.search(result) or added != iso:
        raise _HourReadingError("count_mismatch", (iso, added, text, result))
    return result


def _weekday_contradiction(normalized: str) -> str:
    """Ein ISO-Datum, dem ein genannter Wochentag widerspricht — sonst leer.

    Block 0b schreibt ein Tageswort als ISO-Datum, ein Wochentag bleibt als Wort
    stehen. **Nennt der Ausdruck beides und ist es nicht derselbe Tag, gibt es
    keine richtige Wahl** — und dateparser traf eine: Am 14.09.2026, einem
    Montag, kam im Betrieb ein Termin mit Tageswort und einem anderen
    Wochentag an; richtig gelesen haette das Datum den Dienstag gewaehlt,
    gemeint war nach dem Verlauf der Wochentag. Nur ISO-Daten werden
    geprueft: Ein Datum ohne Jahr bekommt in Block 0c das laufende Jahr, und
    der Wochentag kann ein spaeteres meinen.

    Vorbedingung: `normalized` traegt nur gueltige Daten (Schritt 3b lief).
    Nachbedingung: leer, wenn kein Wochentag genannt ist oder jedes ISO-Datum
        auf einen genannten Wochentag faellt; sonst Datum, sein Wochentag und
        die genannten.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    named: set[str] = {w.lower() for w in _WEEKDAY_WORD.findall(normalized)}
    if not named:
        return ""
    for year, month, day in _DATE_ISO.findall(normalized):
        weekday: str = _WOCHENTAGE[date(int(year), int(month), int(day)).weekday()]
        if weekday not in named:
            return (
                f"{day}.{month}.{year} ist ein {weekday.capitalize()}, "
                f"genannt: {', '.join(sorted(w.capitalize() for w in named))}"
            )

    # ── Ausgabe ──────────────────────────────────────────────────────
    return ""


def _stated_time_missing(normalized: str, result: datetime) -> str:
    """Die im Ausdruck erkannten Uhrzeiten, wenn keine davon im Ergebnis steht.

    `zeit_parsen_vektor` meldet eine Uhrzeit als erkannt, sobald der
    normalisierte Text `H:MM` traegt, und der Termindienst legt den Eintrag
    dann mit Genauigkeit Minute an. Ein Ergebnis mit einer anderen Uhrzeit ist
    ein Termin zur falschen Zeit, der wie ein richtiger aussieht. **So entstand
    der Fall vom 14.09.2026:** Die Pfade scheiterten am normalisierten Text,
    der Rueckfall gab dateparser den Originaltext, und der verwarf die Uhrzeit,
    die er nicht lesen konnte, still — es blieb die Sprechzeit.

    Verglichen wird die Wanduhr in der Ortszone. Eine Uhrzeit in der Luecke
    der Umstellung auf Sommerzeit prueft das nicht: *„um 2:30"* am 28.03.2027
    kommt als 02:30 mit dem Versatz der Winterzeit zurueck (gemessen
    15.09.2026) — sie steht im Ergebnis, das es so nicht gibt.

    Vorbedingung: `normalized` ist der Text, aus dem `result` aufgeloest wurde;
        `result` ist zeitzonenbewusst.
    Nachbedingung: leer, wenn der Text keine Uhrzeit traegt oder eine davon die
        Wanduhr des Ergebnisses ist; sonst die erkannten Uhrzeiten, kommagetrennt.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    stated: list[str] = _WRITTEN_CLOCK_TIME.findall(normalized)
    local: datetime = result.astimezone(ZoneInfo(TIMEZONE))
    if not stated or any(
        (int(t.split(":")[0]), int(t.split(":")[1])) == (local.hour, local.minute) for t in stated
    ):
        return ""

    # ── Ausgabe ──────────────────────────────────────────────────────
    return ", ".join(stated)


def _read_dotted_clock_time(text: str) -> str:
    """Liest eine Uhrzeit mit Punkt als Trenner so wie eine mit Doppelpunkt.

    **Der Fall, gemessen am 14.09.2026 im Betrieb:** Eine Zeitangabe mit Punkt
    als Trenner kam beim Parser an, und Block 2 las in *„9.00 Uhr"* die `00 Uhr`
    als Stunde. Der Text wurde `9.0:00`, und der Rueckfall auf den Originaltext
    lieferte den Tag **zur aktuellen Uhrzeit**. Mit anderen Minuten stuerzte der
    Parser ab: In *„9.30 Uhr"* wurde `30 Uhr` die Stunde 30.

    Vorbedingung: `text` ist der fuzzy-korrigierte Ausdruck, vor jeder
        Normalisierung.
    Nachbedingung: Jede Form `H.MM` vor "Uhr" steht als `H:MM`; nach "um" ohne
        "Uhr" nur, wenn Stunde 0..23 und Minute 0..59. Nachgezaehlt mit
        `_WRITTEN_CLOCK_TIME` — sonst `_HourReadingError`.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    before_uhr: int = len(_DOTTED_BEFORE_UHR.findall(text))
    after_um: int = sum(
        1 for m in _DOTTED_AFTER_UM.finditer(text)
        if int(m.group(1)) <= 23 and int(m.group(2)) <= 59
    )
    if before_uhr == 0 and after_um == 0:
        return text

    # ── Verarbeitung ─────────────────────────────────────────────────
    def replace_after_um(match: re.Match) -> str:
        if int(match.group(1)) > 23 or int(match.group(2)) > 59:
            return match.group(0)
        return f"{match.group(1)}:{match.group(2)}"

    result: str = _DOTTED_BEFORE_UHR.sub(r"\1:\2", text)
    result = _DOTTED_AFTER_UM.sub(replace_after_um, result)

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    added: int = len(_WRITTEN_CLOCK_TIME.findall(result)) - len(_WRITTEN_CLOCK_TIME.findall(text))
    if added != before_uhr + after_um:
        raise _HourReadingError("count_mismatch", (before_uhr + after_um, added, text, result))
    logger.debug(f"Zeitparser: Uhrzeit mit Punkt gelesen '{text}' -> '{result}'")
    return result


def _read_hour_before_daypart(text: str) -> str:
    """Liest "3 nachmittags" als Uhrzeit, bevor die Tageszeit herausgenommen wird.

    Die Tageszeit-Extraktion am Anfang der Normalisierung schneidet das Wort
    heraus und merkt sich nur seine Rueckfall-Uhrzeit. Stand die Stunde davor,
    blieb sie allein zurueck und wurde zum Monatstag — *„3 nachmittags"* ergab
    den 03. des Monats um 15:00. Deshalb wird dieses Paar zuerst gelesen. Bis
    zum 15.09.2026 stand dafuer ein Block hinter der Extraktion; er bekam das
    Paar nur noch zu sehen, wenn der Ausdruck eine zweite Tageszeit trug.

    Vorbedingung: `text` ist der fuzzy-korrigierte Ausdruck.
    Nachbedingung: Jedes Paar aus nackter Stunde (0..23) und Tageszeit steht
    als `H:00`; eine Stunde ueber 23 bleibt unberuehrt.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    result: str = _replace_hours(text, _HOUR_BEFORE_DAYPART, None)

    # ── Ausgabe ──────────────────────────────────────────────────────
    if result != text:
        logger.debug(f"Zeitparser: Stunde vor Tageszeit gelesen '{text}' -> '{result}'")
    return result


def _read_hour_after_um(text: str, daypart: str) -> str:
    """Liest eine Stunde nach "um" ohne "Uhr" als Uhrzeit.

    **Der Fall, gemessen am 14.09.2026 im Betrieb:** Ein Terminauftrag mit
    Tageswort, "um" und nackter Stunde erreichte den Parser woertlich; die
    Normalisierung liess *„um H"* stehen, und der Rueckfall auf den
    Originaltext lieferte den Folgetag **zur aktuellen Uhrzeit**. Ohne
    Tagesangabe wurde die Zahl zum Monatstag, auch mit Wochentag: *„Donnerstag
    um 14"* ergab den 14. des Monats, in der Vergangenheit.

    **Die Stunde wird so gelesen wie mit "Uhr"** — *„um 3"* ist 03:00 wie
    *„um 3 Uhr"*. Eine Tageszeit im Ausdruck verschiebt sie wie dort
    (*„abends um 8"* -> 20:00). Welche Tageshaelfte ohne Tageszeit gemeint ist,
    entscheidet diese Funktion nicht.

    Vorbedingung: `text` ist normalisiert bis vor die Entfernung des verwaisten
    "um"; `daypart` ist die gemerkte Tageszeit des Ausdrucks oder leer.
    Nachbedingung: Jedes "um" mit Stunde 0..23 ohne Menge oder Monat danach
    steht als `H:00`; eine Stunde ueber 23 bleibt unberuehrt.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    result: str = _replace_hours(text, _HOUR_AFTER_UM, daypart)

    # ── Ausgabe ──────────────────────────────────────────────────────
    if result != text:
        logger.debug(f"Zeitparser: Stunde nach 'um' gelesen '{text}' -> '{result}'")
    return result


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

    ergebnis: str = _read_hour_before_daypart(_read_dotted_clock_time(text))
    tageszeit_woerter: str = "|".join(_TAGESZEITEN.keys())

    # ── Tageszeit extrahieren (Fallback fuer spaeter) ──
    # NUR wenn das Wort NICHT direkt nach "Uhr" steht.
    #
    # Gemerkt wird seit dem 15.09.2026 auch das Wort selbst, nicht nur seine
    # Rueckfall-Uhrzeit: Eine vorangestellte Tageszeit verschiebt die Stunde,
    # die ihr folgt ("abends um 8", "nachmittags um 3 Uhr") — bis dahin ging
    # die Verschiebung mit dem herausgeschnittenen Wort verloren.
    gemerkte_uhrzeit: str = ""
    gemerkte_tageszeit: str = ""
    for wort, uhrzeit in _TAGESZEIT_UHRZEITEN.items():
        if re.search(r'(?<![Uu]hr\s)\b' + wort + r'\b', ergebnis, flags=re.IGNORECASE):
            gemerkte_uhrzeit = uhrzeit
            gemerkte_tageszeit = wort.lower()
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

    for wort, offset in _RELATIVE_DAYS.items():
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
        tageszeit: str = (match.group(2) or "").lower().strip() or gemerkte_tageszeit

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
        tageszeit: str = (match.group(3) or "").lower().strip() or gemerkte_tageszeit

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

    # ── 3. Stunde vor Tageszeit ohne "Uhr" ──
    # Seit dem 15.09.2026 in `_read_hour_before_daypart`, VOR der Extraktion oben.
    # Hier war die Tageszeit schon herausgeschnitten; der Block traf nur noch,
    # wenn der Ausdruck eine zweite Tageszeit trug.

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

    # ── 8b. Stunde nach "um" ohne "Uhr" ──
    ergebnis = _read_hour_after_um(ergebnis, gemerkte_tageszeit)

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

    # Schritt 3b: Was es nicht gibt, bekommt kein Datum — und keinen Absturz.
    # Die Pfade unten bauen ihr datetime ungeprueft; ein unmoeglicher Wert riss
    # bis zum 15.09.2026 eine ValueError bis zum Aufrufer. Kein Rueckfall auf
    # dateparser: Ein unmoegliches Datum lehnt er ab, eine unmoegliche Uhrzeit
    # nicht — "morgen 14:75" ergibt dort morgen zur aktuellen Uhrzeit (gemessen
    # an dateparser 1.4.2, 15.09.2026).
    impossible: list[str] = _impossible_values(normalisiert)
    if impossible:
        logger.warning(
            f"Zeitparser: '{text}' nennt, was es nicht gibt ({', '.join(impossible)}) — kein Datum"
        )
        return None, befund, korrigiert, normalisiert

    # Schritt 3c: Widersprechen sich Tageswort und Wochentag, gibt es keine
    # richtige Wahl — kein Datum statt einer (`_weekday_contradiction`).
    contradiction: str = _weekday_contradiction(normalisiert)
    if contradiction:
        logger.warning(f"Zeitparser: '{text}' widerspricht sich ({contradiction}) — kein Datum")
        return None, befund, korrigiert, normalisiert

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
            # Stunde und Minute sind in Schritt 3b geprueft. Bis zum 15.09.2026
            # stand hier die Pruefung selbst, mit Rueckfall auf dateparser.
            stunde, minute = int(m.group(1)), int(m.group(2))
            kandidat: datetime = referenz_lokal.replace(
                hour=stunde, minute=minute, second=0, microsecond=0,
            )
            if zukunft and kandidat <= referenz_lokal:
                kandidat += timedelta(days=1)
            elif not zukunft and kandidat > referenz_lokal:
                kandidat -= timedelta(days=1)
            ergebnis = kandidat
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
                    _iso_dates_as_dmy(datum_teil), languages=["de"], settings=settings,
                )
                if datum_ergebnis:
                    ergebnis = datum_ergebnis.replace(
                        hour=stunde, minute=minute, second=0, microsecond=0,
                    )
                    pfad = 2

    # Pfad 3 — Fallback (alles an dateparser)
    if ergebnis is None:
        ergebnis = dateparser.parse(
            _iso_dates_as_dmy(normalisiert), languages=["de"], settings=settings,
        )
        if ergebnis:
            pfad = 3

    # Letzter Fallback: Originaler Text, falls Normalisierung dateparser verwirrt hat
    if ergebnis is None and normalisiert != korrigiert:
        logger.info("Zeitparser: Normalisierter Text fehlgeschlagen, versuche Original...")
        ergebnis = dateparser.parse(
            _iso_dates_as_dmy(korrigiert), languages=["de"], settings=settings,
        )
        if ergebnis:
            pfad = 3

    # Schritt 4c: Eine erkannte Uhrzeit muss im Ergebnis stehen — sonst kein
    # Datum statt eines Termins zur falschen Zeit (`_stated_time_missing`).
    if ergebnis is not None:
        missing: str = _stated_time_missing(normalisiert, ergebnis)
        if missing:
            logger.warning(
                f"Zeitparser: '{text}' -> {ergebnis.isoformat()} (Pfad {pfad}) traegt "
                f"keine der genannten Uhrzeiten ({missing}) — kein Datum"
            )
            return None, befund, korrigiert, normalisiert

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
