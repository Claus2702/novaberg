"""Positivform — die Grammatik des Verschiebens, gelesen auf dem Rohtext.

Die zweite, unabhaengige Pruefung jedes Verschiebens mit Uhrzeit neben der
Lesung des Zeitparsers (`utils.zeitparser.read_time`): Sie liest den Text vor
jeder Normalisierung und kennt nur wenige Formen. Einziger Aufrufer ist
`agents.timeline.crud._raw_form_agrees`.

Vom Zeitparser nimmt sie nur sein Vokabular (`TIME_VOCABULARY`), keine
Normalisierung und keine Stundenlogik: Was der Parser als Zeitbezug fuehrt,
darf ausserhalb der Form nicht stehen.
"""

import re
from dataclasses import dataclass
from datetime import time
from typing import Optional

from utils.zeitparser import TIME_VOCABULARY


@dataclass(frozen=True)
class RawTimeForm:
    """Die Positivform eines Verschiebeauftrags, gelesen auf dem Rohtext (`raw_time_form`).

    Die zweite Pruefung neben der Lesung (`read_time`): Sie liest den Text vor
    jeder Normalisierung und kennt nur wenige Formen. `clock` ist die neue
    Uhrzeit der Form ("auf 11 Uhr" -> 11:00, "von 10 auf 11:30" -> 11:30);
    None, wenn die Form keine nennt ("auf Freitag") oder der Text keinen
    Zeitteil hat.
    """

    clock: Optional[time] = None


def _alternation(*words: str) -> str:
    """Alternation eines Musters aus Woertern, laengste zuerst.

    Laengste zuerst, damit ein kurzes Wort kein laengeres abschneidet
    ("vierzehn" vor "vier"); dieselbe Ordnung wie die Wortgruppen des
    Zeitparsers.

    Vorbedingung: `words` sind nicht leere Texte, mindestens einer.
    Nachbedingung: die Woerter, durch "|" getrennt, absteigend nach Laenge,
        bei gleicher Laenge in der gegebenen Reihenfolge.
    Fehlerfaelle: kein Wort, ein leeres Wort oder keiner Text wirft
        `ValueError` — die Alternation passte sonst auf jeden Text.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not words or not all(isinstance(word, str) and word for word in words):
        msg: str = f"_alternation: kein Wort oder ein leeres ({words!r})"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    pattern: str = "|".join(sorted(words, key=len, reverse=True))

    # ── Ausgabe ─────────────────────────────────
    return pattern


#: Die Muster von `raw_time_form`, auf dem Rohtext vor jeder Normalisierung.
#: Eine Stunde T: Ziffern ("11", "11:30", "11.30") oder ein Zahlwort "eins" bis
#: "vierundzwanzig", je wahlweise mit "Uhr". "ein" nur vor "Uhr" — allein ist
#: es ein Artikel ("ein Treffen"). Keine Ziffer mit Buchstaben dahinter ("11h").
#: `{n}` ist der Name der Gruppen; T steht in der Form an mehreren Stellen.
_RAW_HOUR: str = (
    r"(?:(?<![\w.,:])(?P<{n}_h>\d{{1,2}})(?:[:.](?P<{n}_m>\d{{2}}))?(?!\w|[.,:]\d)"
    r"|\b(?P<{n}_w>ein(?=\s+uhr\b)|" + _alternation(*TIME_VOCABULARY.hour_words)
    + r")\b)(?:\s+uhr\b)?"
)

#: Ein Tag <Tag>: ein Wochentag, wahlweise mit relativem Praefix ("naechsten
#: Freitag" — `tag_erkannt` liest den Wochentag), "heute", "morgen",
#: "uebermorgen", ein Datum mit Punkt ("20.", "20.10.", "20.10.2026") oder eine
#: Ordinalzahl, die beiden letzten wahlweise mit "den". "11.30." ist kein Datum:
#: Es gibt keinen 30. Monat. "naechste Woche" ist kein Tag: Kein Wochentag.
_RAW_DAY: str = (
    r"(?:\bauf\s+)?(?:(?:\bden\s+)?(?:(?<![\w.,:])\d{1,2}\."
    r"(?:(?:0?[1-9]|1[0-2])\.(?:\d{4})?(?!\d)|(?!\d))"
    r"|\b(?:" + _alternation(*TIME_VOCABULARY.ordinal_days) + r")\b)"
    r"|\b(?:(?:" + _alternation(
        *TIME_VOCABULARY.relative_prefixes,
        *map(TIME_VOCABULARY.ascii_form, TIME_VOCABULARY.relative_prefixes),
    )
    + r")\s+)?(?:" + _alternation(*TIME_VOCABULARY.weekdays) + r")\b"
    r"|\b(?:heute|morgen|übermorgen|uebermorgen)\b)"
)

#: Die Positivform, genau eine der fuenf Formen: "[auf|um|nach|gegen] T",
#: "von T auf|nach T", "auf <Tag>", "auf <Tag> [um] T", "auf <Tag> von T
#: auf|nach T". Die neue Stunde steht in der Gruppe y2, t2, y1 oder t1.
_RAW_TIME_FORM = re.compile(
    r"(?P<day>" + _RAW_DAY + r")"
    r"(?:\s+(?:von\s+" + _RAW_HOUR.format(n="x2") + r"\s+(?:auf|nach)\s+"
    + _RAW_HOUR.format(n="y2") + r"|(?:um\s+)?" + _RAW_HOUR.format(n="t2") + r"))?"
    r"|\bvon\s+" + _RAW_HOUR.format(n="x1") + r"\s+(?:auf|nach)\s+" + _RAW_HOUR.format(n="y1")
    + r"|(?:\b(?:auf|um|nach|gegen)\s+)?" + _RAW_HOUR.format(n="t1"),
    re.IGNORECASE,
)

#: Die Gruppen der neuen Stunde, je Form genau eine gesetzt.
_RAW_NEW_HOUR_GROUPS: tuple[str, ...] = ("y2", "t2", "y1", "t1")

#: Der Wert einer Stunde als Zahlwort in der Positivform, "ein" eingeschlossen.
_RAW_HOUR_VALUES: dict[str, int] = {"ein": 1, **TIME_VOCABULARY.hour_words}

#: Woerter aus den geschuetzten Woertern und den Zahlwoertern des Zeitparsers,
#: die allein keinen Zeitbezug tragen: Praepositionen ("nach" gehoert zur Form
#: "von T nach T") und "ein", meist ein Artikel ("ein Treffen"). Die Zeit, auf
#: die sie zeigen, ist selbst ein Wort der Menge unten ("vor 11", "in einer
#: Woche").
_RAW_NO_TIME_WORDS: frozenset[str] = frozenset({"vor", "nach", "um", "am", "in", "an", "ein"})

#: Jedes Wort, das der Zeitparser als Zeitbezug fuehrt (`TIME_VOCABULARY.words`),
#: kleingeschrieben, auch mit ASCII-Umschrift — ohne `_RAW_NO_TIME_WORDS`.
_RAW_TIME_WORDS: frozenset[str] = frozenset(
    form.lower()
    for word in TIME_VOCABULARY.words
    for form in (word, TIME_VOCABULARY.ascii_form(word))
    if word not in _RAW_NO_TIME_WORDS
)

#: Jedes Wort des Vokabulars, kleingeschrieben, auch mit ASCII-Umschrift —
#: einschliesslich `_RAW_NO_TIME_WORDS` ("nach", "vor"). Ein solches Wort und
#: jeder seiner Anfaenge ("nachm", "vorm", "fr") ist nie ein Inhaltswort des
#: Titels.
_RAW_PARSER_WORDS: frozenset[str] = frozenset(
    form.lower()
    for word in TIME_VOCABULARY.words
    for form in (word, TIME_VOCABULARY.ascii_form(word))
)

#: Alles Zeitartige, das ausserhalb der Positivform nicht stehen darf: jedes
#: Wort aus `_RAW_TIME_WORDS`, jede Ziffer, die Zehner "zwanzig" bis "fuenfzig" auch mit Einer
#: ("dreissig", "fuenfundzwanzig"), jedes Wort, das mit "halb", "viertel" oder "dreiviertel"
#: beginnt ("halbe", "Viertelstunde") oder auf "stunde", "tag", "woche", "monat"
#: oder "jahr" endet, auch gebeugt ("Stunden", "Geburtstag", "Wochen"), dazu
#: "Uhr", "oder", "bzw.", "bis", "zwischen", "statt", "nicht", "sonst" und der
#: Gedankenstrich. Ganze Woerter: "Mittagessen" ist kein "Mittag".
_RAW_OTHER_TIME = re.compile(
    r"\d|[–—]|\b(?:\w+und)?(?:zwanzig|dreißig|dreissig|vierzig|fünfzig|fuenfzig)\b"
    r"|\b(?:halb|viertel|dreiviertel)\w*"
    r"|\b\w*(?:stunde|tag|woche|monat|jahr)(?:e|en|n|s|es)?\b"
    r"|\b(?:" + _alternation(*_RAW_TIME_WORDS, *{
        form
        for word in (
            "uhr", "oder", "bzw", "beziehungsweise", "bis", "zwischen", "statt", "anstatt",
            "nicht", "sonst",
        )
        for form in (word, TIME_VOCABULARY.ascii_form(word))
    }) + r")\b",
    re.IGNORECASE,
)

#: Das Verb des Verschiebens in seinen Formen ("verschieb", "verschiebe",
#: "verschieben", "legst", "aendert"), auf dem kleingeschriebenen Wort in
#: ASCII-Umschrift. Zugelassen ausserhalb der Positivform.
_RAW_ADMITTED_VERB = re.compile(
    r"(?:verschieb|verleg|leg|setz|aender|pack|mach)(?:e|en|n|st|est|t|et)?"
)

#: Die Fuellwoerter einer Bitte und eines Bezugs, kleingeschrieben in
#: ASCII-Umschrift: Artikel, Pronomen, Demonstrativa, "mein..."/"dein..."/
#: "unser...", die Bitte ("bitte", "mal", "kannst", "wuerdest"), "Termin" und
#: "Uhrzeit" und die Praepositionen eines Bezugs ("der Termin beim Zahnarzt",
#: "mit Anna", "zum Friseur"). Zugelassen, weil keines eine Zeit traegt; die
#: Praepositionen einer Zeit ("um", "am", "vor", "in", "bis", "von") fehlen mit
#: Absicht, ebenso "und", "oder" und "auf" ausserhalb der Form.
_RAW_ADMITTED_WORDS: frozenset[str] = frozenset({
    "der", "die", "das", "den", "dem", "des",
    "ein", "eine", "einen", "einem", "einer", "eines",
    "ich", "du", "er", "sie", "es", "wir", "ihr", "mir", "mich", "dir", "dich", "ihm", "ihn",
    "uns", "euch", "ihnen",
    *(stem + ending for stem in ("mein", "dein", "unser", "dies")
      for ending in ("", "e", "en", "em", "er", "es")),
    "bitte", "mal", "doch", "noch", "gern", "gerne",
    "kannst", "kann", "koenntest", "koennte", "wuerdest", "wuerde", "magst",
    "termin", "uhrzeit", "bei", "beim", "mit", "fuer", "zum", "zur",
})

#: Ein Wort des Termintitels: nur Buchstaben. Als Bezug zaehlt es nur, wenn es
#: ein Inhaltswort ist (`_RAW_TITLE_MIN_LETTERS`, `_RAW_FUNCTION_WORDS`,
#: `_RAW_PARSER_WORDS`).
_RAW_TITLE_WORD = re.compile(r"[^\W\d_]+")

#: Ein Titelwort mit weniger Buchstaben ist kein Inhaltswort ("Dr", "Ort", "A").
_RAW_TITLE_MIN_LETTERS: int = 4

#: Das Kompositum aus einem Titelwort, das ausserhalb der Form als Bezug
#: zaehlt: Titelwort vorn, "termin" hinten ("Zahnarzttermin").
_RAW_TITLE_COMPOUND_END: str = "termin"

#: Was zwischen Titelwort und "termin" stehen darf: nichts oder das Fugen-s
#: ("Zahnarztstermin"). Eine freie Mitte liesse jedes Wort ein, auch ein
#: Zeitwort ("Zahnarztnachmittagstermin").
_RAW_TITLE_COMPOUND_JOINTS: tuple[str, ...] = ("", "s")

#: Funktionswoerter, kleingeschrieben in ASCII-Umschrift: Praepositionen,
#: Artikel, Pronomen und Konjunktionen. Ein Titelwort aus dieser Menge ist kein
#: Bezug — der Titel "Fahrt nach Hause" liess sonst "nach" und ueber das
#: Teilwort "nachm." zu, und "auf 3 Uhr nachm." schrieb 03:00 statt 15:00.
#: Kuerzere Woerter als `_RAW_TITLE_MIN_LETTERS` stehen hier der Vollstaendigkeit
#: halber; sie scheiden schon an der Laenge aus.
_RAW_FUNCTION_WORDS: frozenset[str] = frozenset({
    # Praepositionen
    "ab", "an", "am", "auf", "aus", "bei", "beim", "bis", "durch", "fuer", "gegen", "hinter",
    "im", "in", "ins", "mit", "nach", "neben", "ohne", "seit", "statt", "anstatt", "ueber",
    "um", "unter", "vom", "von", "vor", "waehrend", "wegen", "zu", "zum", "zur", "zwischen",
    "gegenueber", "innerhalb", "ausserhalb", "binnen", "laut", "trotz", "samt", "mitsamt",
    # Artikel
    "der", "die", "das", "den", "dem", "des",
    "ein", "eine", "einen", "einem", "einer", "eines",
    "kein", "keine", "keinen", "keinem", "keiner", "keines",
    # Pronomen
    "ich", "du", "er", "sie", "es", "wir", "ihr", "mir", "mich", "dir", "dich", "ihm", "ihn",
    "uns", "euch", "ihnen", "sich", "man", "wer", "was", "wen", "wem", "wessen",
    *(stem + ending
      for stem in ("mein", "dein", "sein", "ihr", "unser", "euer", "eur", "dies", "jen",
                   "welch", "jed", "manch", "solch")
      for ending in ("", "e", "en", "em", "er", "es")),
    # Konjunktionen
    "und", "oder", "aber", "sondern", "denn", "doch", "sowie", "sowohl", "als", "wie",
    "dass", "weil", "wenn", "falls", "ob", "obwohl", "damit", "bevor", "nachdem", "bzw",
    "beziehungsweise", "noch", "weder", "entweder",
})


def raw_time_form(text: str, title: str) -> Optional[RawTimeForm]:
    """Die Positivform eines Verschiebeauftrags auf dem Rohtext — oder None.

    Unabhaengig von der Normalisierung: Gelesen wird der Text, wie er kommt.
    Der Zeitteil muss genau eine dieser Formen sein (`_RAW_TIME_FORM`):
    "[auf|um|nach|gegen] T", "von T auf|nach T", "auf <Tag>", "auf <Tag> [um]
    T" oder "auf <Tag> von T auf|nach T". T ist eine Ziffernstunde ("11",
    "11:30", "11.30") oder ein Zahlwort "eins" bis "vierundzwanzig" ("ein" nur
    vor "Uhr"), je wahlweise mit "Uhr"; <Tag> ein Wochentag (auch mit
    relativem Praefix, "naechsten Freitag"), "heute", "morgen", "uebermorgen",
    ein Datum mit Punkt oder eine Ordinalzahl — "naechste Woche" nicht. Das
    "auf" vor <Tag> ist wahlweise: Der Zeitausdruck der Klassifikation lautet
    "Freitag". Ausserhalb der Form darf nur stehen, was zugelassen ist
    (`_raw_outside_admitted`): das Verb des Verschiebens, ein Fuellwort, ein
    Wort gleich einem Inhaltswort von `title` (mindestens vier Buchstaben,
    kein Funktionswort, kein Wort der Parser-Listen und kein Anfang eines
    solchen, also nicht "nachm") oder genau das Kompositum aus einem solchen
    und "termin", wahlweise mit Fugen-s ("Zahnarzttermin", "Zahnarztstermin").
    Zusaetzlich darf dort kein
    Wort stehen, das der Zeitparser als Zeitbezug fuehrt (`_RAW_OTHER_TIME`)
    — auch kein Wort des Titels.

    Vorbedingung: `text` und `title` sind Texte, leer erlaubt.
    Nachbedingung: eine `RawTimeForm` mit der neuen Uhrzeit der Form (Lage
        "von T auf T": die zweite), oder ohne Uhrzeit fuer "auf <Tag>" und
        einen Text ohne Zeitteil.
    Fehlerfaelle: kein Text wirft `TypeError`. None — also die Rueckfrage —
        ergibt ausserhalb der Form jedes Wort, das nicht zugelassen ist,
        auch ein unbekanntes ("Fr.", "vorm.", "flimmerig"), jede Ziffer und
        jedes Wort aus `_RAW_OTHER_TIME`; ebenso eine Stunde ueber 23 oder
        Minuten ueber 59.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(text, str) or not isinstance(title, str):
        msg: str = f"raw_time_form: kein Text ({type(text).__name__}, {type(title).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    found: Optional[re.Match[str]] = _RAW_TIME_FORM.search(text)
    outside: str = f"{text[:found.start()]} {text[found.end():]}" if found else text
    if _RAW_OTHER_TIME.search(outside) or not _raw_outside_admitted(outside, title):
        return None
    hour: Optional[tuple[int, int]] = _raw_new_hour(found) if found else None

    # ── Ausgabe-Verifikation ────────────────────
    if hour is not None and (hour[0] > 23 or hour[1] > 59):
        return None
    return RawTimeForm(clock=time(*hour) if hour is not None else None)


def _raw_outside_admitted(outside: str, title: str) -> bool:
    """Ob jedes Wort ausserhalb der Positivform ausdruecklich zugelassen ist.

    Zugelassen ist, kleingeschrieben in ASCII-Umschrift: das Verb des
    Verschiebens (`_RAW_ADMITTED_VERB`), ein Fuellwort einer Bitte oder eines
    Bezugs (`_RAW_ADMITTED_WORDS`) und ueber den Titel nur zweierlei: ein
    Wort, das einem Inhaltswort des Titels gleich ist ("Fahrt" zu "Fahrt nach
    Hause"), oder genau das Kompositum Inhaltswort + "termin" oder
    Inhaltswort + "s" + "termin" ("Zahnarzttermin", "Zahnarztstermin"), ohne
    weitere Mitte ("Zahnarztnachmittagstermin" nicht). Inhaltswort ist ein
    Titelwort nur aus Buchstaben, mit mindestens `_RAW_TITLE_MIN_LETTERS`
    Buchstaben, das nicht in `_RAW_FUNCTION_WORDS` steht und kein Anfang
    eines Worts aus `_RAW_PARSER_WORDS` ist, auch kein ganzes — "Dr", "nach",
    "vor", "Freitag" und "nachm" (Anfang von "nachmittag") sind keine. Ein
    Teilwort zaehlt nicht: "nachm." ist kein Bezug, auch nicht zu "Fahrt nach
    Hause" oder "Kaffee nachm.". Jedes andere Wort ist nicht zugelassen, auch
    ein unbekanntes. Satzzeichen sind keine Woerter.

    Vorbedingung: `outside` ist der Rohtext ohne die Form, `title` der Titel
        des Termins; beide Texte, leer erlaubt.
    Nachbedingung: wahr genau dann, wenn kein Wort ausserhalb der Form nicht
        zugelassen ist; ein Text ohne Woerter ist zugelassen.
    Fehlerfaelle: kein Text wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(outside, str) or not isinstance(title, str):
        msg: str = f"_raw_outside_admitted: kein Text ({outside!r}, {title!r})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    content_words: set[str] = {
        part for part in _RAW_TITLE_WORD.findall(TIME_VOCABULARY.ascii_form(title.lower()))
        if len(part) >= _RAW_TITLE_MIN_LETTERS
        and part not in _RAW_FUNCTION_WORDS
        and not any(parser_word.startswith(part) for parser_word in _RAW_PARSER_WORDS)
    }
    title_words: set[str] = content_words | {
        part + joint + _RAW_TITLE_COMPOUND_END
        for part in content_words for joint in _RAW_TITLE_COMPOUND_JOINTS
    }
    refused: list[str] = [
        word for word in re.findall(r"\w+", TIME_VOCABULARY.ascii_form(outside.lower()))
        if word not in _RAW_ADMITTED_WORDS
        and not _RAW_ADMITTED_VERB.fullmatch(word)
        and word not in title_words
    ]

    # ── Ausgabe ─────────────────────────────────
    return not refused


def _raw_new_hour(found: re.Match[str]) -> Optional[tuple[int, int]]:
    """Die neue Stunde eines Treffers von `_RAW_TIME_FORM` als (Stunde, Minute).

    Vorbedingung: `found` ist ein Treffer von `_RAW_TIME_FORM`.
    Nachbedingung: die Stunde der gesetzten Gruppe aus `_RAW_NEW_HOUR_GROUPS`
        ("von 10 auf 11" -> die 11), als Zahlwort ihr Wert ("ein" ist 1);
        None fuer "auf <Tag>" ohne Stunde. Den Bereich prueft der Aufrufer.
    Fehlerfaelle: kein Treffer, oder einer mit mehr als einer neuen Stunde,
        wirft `ValueError` — das Muster haette seine Formen vermischt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(found, re.Match) or "t1_h" not in found.re.groupindex:
        msg: str = f"_raw_new_hour: kein Treffer der Positivform ({found!r})"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    hours: list[tuple[int, int]] = []
    for name in _RAW_NEW_HOUR_GROUPS:
        digits: Optional[str] = found.group(f"{name}_h")
        word: Optional[str] = found.group(f"{name}_w")
        if digits:
            hours.append((int(digits), int(found.group(f"{name}_m") or 0)))
        elif word:
            hours.append((_RAW_HOUR_VALUES[word.lower()], 0))

    # ── Ausgabe-Verifikation ────────────────────
    if len(hours) > 1:
        msg = f"_raw_new_hour: mehr als eine neue Stunde ({hours}, {found.group(0)!r})"
        raise ValueError(msg)
    return hours[0] if hours else None
