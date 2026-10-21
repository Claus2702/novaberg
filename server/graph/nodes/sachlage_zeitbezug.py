"""Der Zeitbezug am Objekt der Sachlage — woraus das Kalenderfenster entsteht.

**Konzept:** `docs/novaberg-thinking-lage_e.md` Nr. 36 und 37. Das Angebot der
Sachlage las den Kalender bisher aus dem **Namen** eines akuten Objekts. Den
Namen vergibt das Modell frei (*Novemberereignisse*, *Zahnarzttermin*), und
weder `named_period` noch eine Titelsuche nach dem ganzen Namen trifft ihn
(`SACHLAGE-KALENDER-VERFEHLT-OBJEKTNAMEN`). Das Fenster kommt deshalb aus
einem Feld, das **nur der Server** schreibt: `zeitbezug`, abgeleitet aus der
Aeusserung und dem Namen und an akuten Objekten weitergetragen. **Gibt es
keinen Zeitbezug, gibt es kein Fenster** — die Eigenschaft bleibt offen.

Die zwei Formen des Feldes:

    {"art": "zeitraum", "von": "2026-11-01", "bis": "2026-11-30", "wortlaut": "im November"}
    {"art": "titel", "stichwort": "Zahnarzt", "wortlaut": "Zahnarzt"}

**Zeitraum vor Titel.** Ein Zeitraum ist eine Wortfolge der Aeusserung, die
`named_period` liest, und deren Zeitraumwort im Namen steht. `von` und `bis`
sind absolut, gerechnet am Tag, an dem der Satz fiel — wer nach Mitternacht
weiterfragt, liest denselben Monat, nicht den naechsten. Ein Titel ist das
laengste Wort der Aeusserung mit mindestens vier Buchstaben, das im Namen
steht und kein Zeitwort ist (*morgen* in *Morgenroutine* ist kein Titel).

**Ein Titel nur aus einer Frage nach dem Zeitpunkt.** Den Namen nimmt das
Modell meist aus der Aeusserung; ein Wort der Aeusserung im Namen trifft
deshalb fast jedes akute Objekt. Ein Titel gilt nur, wenn die Aeusserung
fragt, wann die Sache ist (*wann*, *um wie viel Uhr*, *an welchem Tag*). Eine
Aussage (*Morgen hole ich meine Schwester ab*) oder eine Frage nach etwas
anderem (*Wie lange dauert das?*) traegt keinen Titel. Der Zeitraum braucht
keine Frage: Sein Wort muss ohnehin im Namen stehen.

**Warum das Zeitraumwort im Vokabular stehen muss:** `named_period`
korrigiert ein unbekanntes letztes Wort mit Levenshtein 2 zu einem
Monatsnamen — *was* und *bei* werden zu *Mai*. Alle Monatsnamen stehen im
Vokabular des Parsers; ein Wort, das dort fehlt und trotzdem einen ganzen
Monat ergibt, ist eine Korrektur und kein Zeitraum. Das einzige Zeitraumwort
ausserhalb des Vokabulars, *Wochenende*, ergibt zwei Tage.

**Warum der Stamm ohne -e zaehlt:** Die Kompositionsfuge wirft das *-e* ab
(*Wochenendplanung*, *Wochenplan*). Ein Zeitraumwort auf *-e* steht deshalb
auch mit seinem Stamm im Namen.
"""

import calendar
import logging
import re
from dataclasses import dataclass
from datetime import date, datetime

from graph.appointments import (
    DIRECTION_BOTH,
    KIND_RANGE,
    KIND_SEARCH,
    AppointmentWindow,
    range_window,
    search_window,
)
from memory.sachlage_properties import text_key
from utils.zeitparser import TIME_VOCABULARY, named_period

logger = logging.getLogger("ki_server.sachlage.zeitbezug")

#: Der Schluessel am Objekt. Ein Feld des Servers: Aus dem Modell wird es
#: entfernt (`sachlage_form.SERVER_OWNED_OBJECT_FIELDS`).
TIME_REFERENCE_FIELD: str = "zeitbezug"

KIND_PERIOD: str = "zeitraum"
KIND_TITLE: str = "titel"

#: Ein kuerzeres Wort traegt keinen Titel: *Tee* steht in *Teestunde*, aber
#: auch in *Kaffeetee* und *Teenager*.
TITLE_MIN_LETTERS: int = 4

_PERIOD_KEYS: frozenset[str] = frozenset({"art", "von", "bis", "wortlaut"})
_TITLE_KEYS: frozenset[str] = frozenset({"art", "stichwort", "wortlaut"})
#: Eine Frage nach dem Zeitpunkt der Sache. Ohne sie kein Titel (Nr. 36:
#: ohne Zeitbezug keiner). *Wie lange* fragt nach der Dauer, nicht danach.
_TIME_QUESTION: re.Pattern = re.compile(
    r"\bwann\b|\bwie\s*viel\s+uhr\b|\bwelche[mnrs]?\s+(?:uhrzeit|tag|datum)\b",
    re.IGNORECASE,
)
_ISO_DATE: re.Pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
_WORD: re.Pattern = re.compile(r"[^\W_]+")
_UMLAUTS: tuple[tuple[str, str], ...] = (("ä", "ae"), ("ö", "oe"), ("ü", "ue"))
_YEAR_LENGTH: int = 4


def _fold(text: str) -> str:
    """Der Vergleichsschluessel fuer Wort und Name: `text_key` mit Umschrift der Umlaute.

    Vorbedingung: `text` ist ein Text.
    Nachbedingung: casefold, Leerraum zusammengezogen, ä/ö/ü als ae/oe/ue.
    Fehlerfaelle: ein `text`, der kein Text ist, wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(text, str):
        msg: str = f"Sachlage-Zeitbezug: Vergleich ohne Text ({type(text).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    folded: str = text_key(text)
    for umlaut, ersatz in _UMLAUTS:
        folded = folded.replace(umlaut, ersatz)

    # ── Ausgabe-Verifikation ────────────────────
    if any(umlaut in folded for umlaut, _ in _UMLAUTS):
        msg = f"Sachlage-Zeitbezug: Umlaut nach der Umschrift in {folded!r}"
        raise RuntimeError(msg)
    return folded


#: Die Zeitwoerter des Parsers, gefaltet: Ein Zeitraumwort ausserhalb davon
#: ist eine Tippfehlerkorrektur oder *Wochenende*, ein Titel nie eines davon.
_VOCABULARY: frozenset[str] = frozenset(_fold(word) for word in TIME_VOCABULARY.words)


@dataclass(frozen=True)
class _Span:
    """Eine Wortfolge der Aeusserung, die einen Zeitraum nennt.

    `start` und `end` zaehlen Woerter (`end` ausgeschlossen), `anchor` ist der
    Index des Zeitraumworts, `first` und `last` der Zeitraum.
    """

    start: int
    end: int
    anchor: int
    first: date
    last: date

    def __post_init__(self) -> None:
        """Haelt die Folge auf ihre Form: das Zeitraumwort darin, der Zeitraum geordnet.

        Vorbedingung: die Felder kommen aus `_period_span`.
        Nachbedingung: `start <= anchor < end` und `first <= last`.
        Fehlerfaelle: jede Abweichung wirft `ValueError`.
        """
        # ── Eingabe-Validierung ─────────────────────
        ordered: bool = self.start <= self.anchor < self.end

        # ── Verarbeitung ────────────────────────────
        period_ordered: bool = self.first <= self.last

        # ── Ausgabe-Verifikation ────────────────────
        if not (ordered and period_ordered):
            msg: str = f"Sachlage-Zeitbezug: Wortfolge ausser Form: {self}"
            raise ValueError(msg)


def _whole_month(first: date, last: date) -> bool:
    """Ob ein Zeitraum genau ein Kalendermonat ist.

    Vorbedingung: `first <= last`.
    Nachbedingung: wahr, wenn `first` der Erste und `last` der Letzte
        desselben Monats ist.
    Fehlerfaelle: `first` nach `last` wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if first > last:
        msg: str = f"Sachlage-Zeitbezug: Zeitraum {first} nach {last}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    month_end: int = calendar.monthrange(first.year, first.month)[1]
    whole: bool = (
        first.day == 1 and (last.year, last.month, last.day)
        == (first.year, first.month, month_end)
    )

    # ── Ausgabe-Verifikation ────────────────────
    if whole and (last - first).days + 1 != month_end:
        msg = f"Sachlage-Zeitbezug: Monat {first} bis {last} ohne {month_end} Tage"
        raise RuntimeError(msg)
    return whole


def _is_period_word(word: str, today: date) -> bool:
    """Ob ein einzelnes Wort ein Zeitraumwort ist — und keine Tippfehlerkorrektur.

    Vorbedingung: `word` ist ein Wort der Aeusserung; `today` der Tag des Satzes.
    Nachbedingung: wahr, wenn `named_period` das Wort allein liest und es im
        Vokabular des Parsers steht oder keinen ganzen Monat ergibt
        (*Wochenende*). *was* → *Mai* ist falsch.
    Fehlerfaelle: ein leeres Wort wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not word.strip():
        msg: str = "Sachlage-Zeitbezug: leeres Wort als Zeitraumwort"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    period: tuple[date, date] | None = named_period(word, today)
    if period is None:
        return False
    known: bool = _fold(word) in _VOCABULARY

    # ── Ausgabe-Verifikation ────────────────────
    if period[0] > period[1]:
        msg = f"Sachlage-Zeitbezug: '{word}' nennt {period[0]} nach {period[1]}"
        raise RuntimeError(msg)
    return known or not _whole_month(*period)


def _period_span(
    utterance: str, words: list[re.Match], anchor: int, today: date,
) -> _Span | None:
    """Die laengste Wortfolge, die mit dem Zeitraumwort endet und einen Zeitraum nennt.

    Ein Jahr direkt hinter dem Wort zaehlt mit (*im November 2026*). Bei
    gleicher Laenge gewinnt die fruehere Folge.

    Vorbedingung: `words` sind die Worttreffer von `utterance`; `anchor` ist
        der Index eines Zeitraumworts (`_is_period_word`).
    Nachbedingung: eine Folge mit `start <= anchor < end`, deren Text
        `named_period` liest; `None`, wenn keine liest.
    Fehlerfaelle: ein `anchor` ausserhalb von `words` wirft `IndexError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not 0 <= anchor < len(words):
        msg: str = f"Sachlage-Zeitbezug: Zeitraumwort {anchor} ausserhalb von {len(words)}"
        raise IndexError(msg)
    ends: list[int] = [anchor + 1]
    following: str = words[anchor + 1].group(0) if anchor + 1 < len(words) else ""
    if len(following) == _YEAR_LENGTH and following.isdigit():
        ends.insert(0, anchor + 2)

    # ── Verarbeitung ────────────────────────────
    candidates: list[tuple[int, int]] = sorted(
        ((start, end) for start in range(anchor + 1) for end in ends),
        key=lambda c: (c[0] - c[1], c[0]),
    )
    span: _Span | None = None
    for start, end in candidates:
        text: str = utterance[words[start].start():words[end - 1].end()]
        period: tuple[date, date] | None = named_period(text, today)
        if period is not None:
            span = _Span(start=start, end=end, anchor=anchor, first=period[0], last=period[1])
            break

    # ── Ausgabe-Verifikation ────────────────────
    if span is not None and not span.start <= anchor < span.end:
        msg = f"Sachlage-Zeitbezug: Folge {span} ohne das Zeitraumwort {anchor}"
        raise RuntimeError(msg)
    return span


def _word_in_name(word: str, folded_name: str) -> bool:
    """Ob ein Zeitraumwort im Namen steht, auch ohne sein -e in der Fuge.

    Vorbedingung: `folded_name` ist gefaltet (`_fold`).
    Nachbedingung: wahr, wenn das gefaltete Wort oder — endet es auf *-e* —
        sein Stamm ohne *-e* als Teilzeichenkette im Namen steht.
    Fehlerfaelle: ein leeres Wort wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    folded: str = _fold(word)
    if not folded:
        msg: str = "Sachlage-Zeitbezug: leeres Wort im Namen gesucht"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    forms: list[str] = [folded]
    if folded.endswith("e") and len(folded) > 1:
        forms.append(folded[:-1])

    # ── Ausgabe-Verifikation ────────────────────
    if not all(forms):
        msg = f"Sachlage-Zeitbezug: leere Form aus '{word}'"
        raise RuntimeError(msg)
    return any(form in folded_name for form in forms)


def checked_time_reference(raw: object, name: str) -> dict | None:
    """Haelt ein Feld `zeitbezug` auf seine Form; eine falsche Form wird laut verworfen.

    Vorbedingung: `raw` ist der Wert am Objekt, aus Redis oder frisch
        abgeleitet; `name` der Name des Objekts fuer das Log.
    Nachbedingung: eine Kopie mit genau den Schluesseln seiner Art — bei
        `zeitraum` `von` und `bis` als ISO-Datum mit `von <= bis`, bei `titel`
        ein nicht leeres `stichwort`; beide mit nicht leerem `wortlaut`.
        Sonst `None` und eine ERROR-Zeile.
    Fehlerfaelle: keine Ausnahme — eine falsche Form ist ein Befund im Log,
        und das Objekt bleibt ohne Fenster.
    """
    # ── Eingabe-Validierung ─────────────────────
    defect: str = _form_defect(raw)
    if defect:
        logger.error(
            f"Sachlage-Zeitbezug: Feld an '{str(name)[:40]}' {defect} — verworfen"
        )
        return None

    # ── Verarbeitung ────────────────────────────
    checked: dict = {key: str(value).strip() for key, value in raw.items()}

    # ── Ausgabe-Verifikation ────────────────────
    expected: frozenset[str] = _PERIOD_KEYS if checked["art"] == KIND_PERIOD else _TITLE_KEYS
    if set(checked) != expected:
        msg: str = f"Sachlage-Zeitbezug: geprueftes Feld mit Schluesseln {sorted(checked)}"
        raise RuntimeError(msg)
    return checked


def hold_time_reference(objekt: dict, name: str) -> dict:
    """Haelt das Feld eines Objekts aus Redis auf seine Form: ersetzt oder entfernt.

    Vorbedingung: `objekt` ist ein Objekt der vorigen Blase; `name` sein Name.
    Nachbedingung: dasselbe Objekt; traegt es `zeitbezug`, hat das Feld seine
        Form (`checked_time_reference`) — ein falsches ist laut entfernt.
    Fehlerfaelle: ein Objekt, das kein dict ist, wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(objekt, dict):
        msg: str = f"Sachlage-Zeitbezug: Objekt ist {type(objekt).__name__}"
        raise TypeError(msg)
    if TIME_REFERENCE_FIELD not in objekt:
        return objekt

    # ── Verarbeitung ────────────────────────────
    checked: dict | None = checked_time_reference(objekt[TIME_REFERENCE_FIELD], name)
    if checked is None:
        del objekt[TIME_REFERENCE_FIELD]
    else:
        objekt[TIME_REFERENCE_FIELD] = checked

    # ── Ausgabe-Verifikation ────────────────────
    if TIME_REFERENCE_FIELD in objekt and objekt[TIME_REFERENCE_FIELD] is not checked:
        msg = f"Sachlage-Zeitbezug: Feld an '{name[:40]}' nicht ersetzt"
        raise RuntimeError(msg)
    return objekt


def _form_defect(raw: object) -> str:
    """Was an der Form eines Feldes `zeitbezug` nicht stimmt — leer, wenn nichts.

    Vorbedingung: keine.
    Nachbedingung: ein leerer Text, wenn `raw` eine der zwei Formen hat; sonst
        die Abweichung in Worten.
    Fehlerfaelle: keine — die Abweichung ist das Ergebnis.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(raw, dict):
        return f"ist {type(raw).__name__} statt dict"
    art: object = raw.get("art")
    keys: frozenset[str] | None = {KIND_PERIOD: _PERIOD_KEYS, KIND_TITLE: _TITLE_KEYS}.get(art)
    if keys is None:
        return f"hat die unbekannte Art {art!r}"
    if set(raw) != keys:
        return f"der Art {art} hat die Schluessel {sorted(raw)} statt {sorted(keys)}"
    empty: list[str] = [
        k for k in sorted(keys) if not isinstance(raw[k], str) or not raw[k].strip()
    ]
    if empty:
        return f"der Art {art} hat leere oder fremde Werte in {empty}"

    # ── Verarbeitung ────────────────────────────
    defect: str = ""
    if art == KIND_PERIOD:
        defect = _period_defect(raw["von"].strip(), raw["bis"].strip())

    # ── Ausgabe-Verifikation ────────────────────
    if defect and not defect.strip():
        msg: str = "Sachlage-Zeitbezug: Abweichung ohne Worte"
        raise RuntimeError(msg)
    return defect


def _period_defect(first: str, last: str) -> str:
    """Was an `von` und `bis` eines Zeitraums nicht stimmt — leer, wenn nichts.

    Vorbedingung: `first` und `last` sind nicht leere Texte.
    Nachbedingung: leer, wenn beide ein ISO-Datum `JJJJ-MM-TT` sind und
        `first <= last`; sonst die Abweichung in Worten.
    Fehlerfaelle: keine — die Abweichung ist das Ergebnis.
    """
    # ── Eingabe-Validierung ─────────────────────
    unreadable: list[str] = [
        text for text in (first, last) if not _ISO_DATE.fullmatch(text)
    ]
    if unreadable:
        return f"traegt kein ISO-Datum in {unreadable}"

    # ── Verarbeitung ────────────────────────────
    try:
        span: tuple[date, date] = (date.fromisoformat(first), date.fromisoformat(last))
    except ValueError as fehler:
        return f"traegt ein unmoegliches Datum ({fehler})"

    # ── Ausgabe-Verifikation ────────────────────
    if span[1] < span[0]:
        return f"endet vor seinem Beginn ({first} bis {last})"
    return ""


def derive_time_reference(name: str, utterance: str, today: date) -> dict | None:
    """Der Zeitbezug, den die Aeusserung fuer ein Objekt dieses Namens nennt.

    **Zeitraum:** Unter den Zeitraumwoertern der Aeusserung, die im Namen
    stehen (`_word_in_name`), gilt das mit der laengsten Folge, die
    `named_period` liest; bei Gleichstand das erste. **Sonst Titel**, aber
    nur, wenn die Aeusserung nach dem Zeitpunkt fragt (`_TIME_QUESTION`): das
    laengste Wort mit mindestens `TITLE_MIN_LETTERS` Buchstaben, das im Namen
    steht, in keiner Zeitraumfolge liegt und kein Zeitwort ist; bei
    Gleichstand das erste.

    Vorbedingung: `name` nicht leer; `today` der Tag, an dem der Satz fiel.
    Nachbedingung: ein Feld in der Form von `checked_time_reference`, mit
        `von`/`bis` gerechnet an `today` und `wortlaut` wie geschrieben;
        `None`, wenn die Aeusserung keins nennt.
    Fehlerfaelle: ein leerer Name wirft `ValueError`, ein Name oder eine
        Aeusserung, die kein Text ist, `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(name, str) or not isinstance(utterance, str):
        msg: str = "Sachlage-Zeitbezug: Name oder Aeusserung ist kein Text"
        raise TypeError(msg)
    if not name.strip():
        msg = "Sachlage-Zeitbezug: Zeitbezug zu einem Objekt ohne Namen"
        raise ValueError(msg)
    words: list[re.Match] = list(_WORD.finditer(utterance))
    folded_name: str = _fold(name)

    # ── Verarbeitung ────────────────────────────
    spans: list[_Span] = [
        span for span in (
            _period_span(utterance, words, i, today)
            for i, w in enumerate(words) if _is_period_word(w.group(0), today)
        ) if span is not None
    ]
    in_name: list[_Span] = [
        s for s in spans if _word_in_name(words[s.anchor].group(0), folded_name)
    ]
    reference: dict | None = None
    if in_name:
        best: _Span = max(in_name, key=lambda s: s.end - s.start)
        reference = {
            "art": KIND_PERIOD, "von": best.first.isoformat(), "bis": best.last.isoformat(),
            "wortlaut": utterance[words[best.start].start():words[best.end - 1].end()],
        }
    elif _TIME_QUESTION.search(utterance) is not None:
        covered: set[int] = {i for s in spans for i in range(s.start, s.end)}
        titles: list[str] = [
            w.group(0) for i, w in enumerate(words)
            if i not in covered and sum(c.isalpha() for c in w.group(0)) >= TITLE_MIN_LETTERS
            and _fold(w.group(0)) not in _VOCABULARY and _fold(w.group(0)) in folded_name
        ]
        if titles:
            keyword: str = max(titles, key=len)
            reference = {"art": KIND_TITLE, "stichwort": keyword, "wortlaut": keyword}

    # ── Ausgabe-Verifikation ────────────────────
    if reference is not None and checked_time_reference(reference, name) is None:
        msg = f"Sachlage-Zeitbezug: abgeleitetes Feld ausser Form: {reference}"
        raise RuntimeError(msg)
    return reference


def carry_time_references(
    artifact: dict, previous: dict | None, utterance: str, now: datetime,
) -> dict:
    """Setzt `zeitbezug` an den akuten Objekten: neu abgeleitet oder aus der vorigen Blase.

    Nennt die Aeusserung einen Zeitbezug fuer das Objekt, ersetzt er das
    alte Feld. Sonst traegt das Objekt das Feld des gleichnamigen Objekts der
    vorigen Blase weiter (`text_key` des Namens). Latente Objekte tragen nie
    eins. Eine INFO-Zeile zaehlt abgeleitet, weitergetragen und ohne.

    Vorbedingung: `artifact` ist validiert und traegt kein Feld aus dem
        Modell (`normalize_object_form`); `previous` ein Artefakt oder None;
        `now` zeitzonenbewusst in Ortszeit — sein Tag ist der Tag des Satzes.
    Nachbedingung: dasselbe Artefakt; jedes Feld steht an einem akuten
        Objekt und hat seine Form.
    Fehlerfaelle: ein naiver Zeitpunkt wirft `ValueError`, ein Artefakt ohne
        Liste `objekte` `TypeError`; ein Feld ausser Form am Ende wirft
        `RuntimeError`. Ein falsches Feld der vorigen Blase wird laut verworfen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if now.tzinfo is None:
        msg: str = "Sachlage-Zeitbezug: Weitertragen mit Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)
    objekte: object = artifact.get("objekte")
    if not isinstance(objekte, list):
        msg = f"Sachlage-Zeitbezug: Artefakt mit objekte={type(objekte).__name__}"
        raise TypeError(msg)
    inherited: dict[str, dict | None] = {
        text_key(o.get("name", "")):
            checked_time_reference(o[TIME_REFERENCE_FIELD], str(o.get("name", "")))
        for o in (previous or {}).get("objekte") or []
        if isinstance(o, dict) and TIME_REFERENCE_FIELD in o
    }
    counts: dict[str, int] = {"abgeleitet": 0, "weitergetragen": 0, "ohne": 0}

    # ── Verarbeitung ────────────────────────────
    for objekt in (o for o in objekte if isinstance(o, dict)):
        objekt.pop(TIME_REFERENCE_FIELD, None)
        name: str = str(objekt.get("name", "")).strip()
        if objekt.get("akut") is not True:
            continue
        fresh: dict | None = derive_time_reference(name, utterance, now.date()) if name else None
        carried: dict | None = inherited.get(text_key(name))
        if fresh is not None:
            objekt[TIME_REFERENCE_FIELD] = fresh
            counts["abgeleitet"] += 1
        elif carried is not None:
            objekt[TIME_REFERENCE_FIELD] = dict(carried)
            counts["weitergetragen"] += 1
        else:
            counts["ohne"] += 1
    logger.info(
        f"Sachlage-Zeitbezug: {counts['abgeleitet']} abgeleitet, "
        f"{counts['weitergetragen']} weitergetragen, {counts['ohne']} akute ohne"
    )

    # ── Ausgabe-Verifikation ────────────────────
    for objekt in (o for o in objekte if isinstance(o, dict) and TIME_REFERENCE_FIELD in o):
        if objekt.get("akut") is not True or checked_time_reference(
            objekt[TIME_REFERENCE_FIELD], str(objekt.get("name", ""))
        ) is None:
            msg = f"Sachlage-Zeitbezug: Feld ausser Form oder latent an '{objekt.get('name')}'"
            raise RuntimeError(msg)
    return artifact


def time_reference_window(objekt: dict, now: datetime, limit: int) -> AppointmentWindow | None:
    """Das Kalenderfenster aus dem Zeitbezug eines Objekts — ohne Feld keins.

    `zeitraum` liest `von` bis `bis` (`range_window`) und rechnet **nie** neu
    aus dem heutigen Tag; `titel` sucht das Stichwort (`search_window`). Beide
    in beide Richtungen: Ein vergangener Termin steht gekennzeichnet da.

    Vorbedingung: `objekt` ist ein Objekt der Sachlage; `now` zeitzonenbewusst;
        `limit` die Trefferzahl einer Titelsuche.
    Nachbedingung: ein Fenster der Art `range` oder `search` mit Richtung
        `both`; `None`, wenn das Objekt kein Feld oder ein falsches traegt
        (dann laut im Log).
    Fehlerfaelle: ein naiver Zeitpunkt wirft `ValueError`; eine Trefferzahl
        ausserhalb von 1 bis 10 wirft `ValueError` aus `search_window`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if now.tzinfo is None:
        msg: str = "Sachlage-Zeitbezug: Fenster mit Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)
    if TIME_REFERENCE_FIELD not in objekt:
        return None
    name: str = str(objekt.get("name", ""))
    reference: dict | None = checked_time_reference(objekt[TIME_REFERENCE_FIELD], name)
    if reference is None:
        return None

    # ── Verarbeitung ────────────────────────────
    window: AppointmentWindow
    expected: str
    if reference["art"] == KIND_PERIOD:
        query: dict = {
            "from": reference["von"], "to": reference["bis"], "direction": DIRECTION_BOTH,
        }
        window, expected = range_window(query, now), KIND_RANGE
    else:
        query = {"keyword": reference["stichwort"], "limit": limit, "direction": DIRECTION_BOTH}
        window, expected = search_window(query), KIND_SEARCH

    # ── Ausgabe-Verifikation ────────────────────
    if window.kind != expected or window.direction != DIRECTION_BOTH:
        msg = (
            f"Sachlage-Zeitbezug: Fenster {window.kind}/{window.direction} "
            f"zu '{name[:40]}' statt {expected}/{DIRECTION_BOTH}"
        )
        raise RuntimeError(msg)
    return window
