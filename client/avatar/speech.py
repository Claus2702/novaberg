"""Sprechen: aus einem Text Laute, Lautzeiten und Mundkanäle, zusammengeführt mit der Emotion.

Der Weg ist der des Prototyps: Text → Laute (regelbasiert, Standarddeutsch) →
Zeitachse aus Abschnitten je Laut → Koartikulation nach dem Dominanzmodell → je
Kanal eine kritisch gedämpfte Feder → Zusammenführung mit dem Ziel der Emotion.
Eine Tonausgabe gibt es nicht; der Mund spricht nach den Lautzeiten aus dem Text.

Die Zeit des Sprechens zählt in Millisekunden wie im Prototyp, der Federschritt
`dt_s` in Sekunden. Beides kommt von außen, von derselben Uhr wie der Animator; das
Modul liest keine Uhr und kennt keinen Zufall. Millisekunden, weil die Grenzen der
Laute auf ganzen Millisekunden liegen: Ob ein Zeitpunkt genau auf einer Grenze liegt,
entscheidet über den angezeigten Laut und über das Ende, und eine Umrechnung aus
Sekunden verschöbe solche Punkte um eine Rundungsstelle.

Regieanweisungen (Text in `*…*` oder `_…_`, im Chat kursiv) entfallen vor dem Sprechen:
`avatar.stage_directions.spoken_text` filtert den Text in `utterance_from_turn`, bevor er
hierher kommt. Dieses Modul spricht, was es bekommt; ein Sternchen darin ist kein Laut.
"""

import logging
import math
import re
from collections.abc import Sequence
from dataclasses import dataclass, field, fields

from avatar.face import PROTOTYPE_KEYS, FaceState
from avatar.speech_tables import (
    BILABIAL_CODES,
    PHONE_CLASSES,
    PHONEMES,
    SPEECH_KEYS,
    VOWEL_CODES,
)

logger = logging.getLogger(__name__)

GAP_MS = 25  # Lücke an einer Wortgrenze
OPEN_REACH = 0.25  # Anteil der Reichweite für Öffnung und Kiefer: der Silbenrhythmus bleibt
SPEECH_OPEN_GAIN = 1.7  # an Video kalibriert: Öffnung an Silbenspitzen ~0,25, dazwischen ~0,12
DOMINANCE_FLOOR = 1e-6  # Startwert der Gewichtssumme je Kanal: kein Teilen durch null
REACH_CUTOFF = 4  # Laute weiter als vier Reichweiten entfernt wirken nicht mehr
CLOSURE_SPAN = 0.6  # Anteil der Lautdauer, über den m, b, p das Pressen erzwingen
CLOSURE_GAIN = 1.6
# Federn je Kanal (1/s): Kiefer träger als Lippen, Pressen sehr schnell, Zungenspitze am schnellsten
SPRING_OMEGA: dict[str, float] = {
    "mo": 45, "jaw": 30, "up": 30, "lo": 30, "str": 18,
    "pk": 16, "fn": 16, "press": 45, "fv": 30, "tng": 40,
}
BLEND_OMEGA = 12  # 1/s, Feder des Sprechanteils
BLEND_THRESHOLD = 0.002  # darunter bleibt der Mund der Emotion unberührt
LABEL_NONE = "–"  # kein Laut, etwa nach dem Ende
GAP_CODE = "GAP"
REST_CODE = "REST"

_MOUTH_AU: tuple[str, ...] = (
    "au10L", "au10R", "au12L", "au12R", "au15L", "au15R", "au16L", "au16R",
    "au20L", "au20R", "au17", "au18", "au22", "au23", "au24", "au28",
)
_FIELD_BY_KEY: dict[str, str] = {key: name for name, key in PROTOTYPE_KEYS.items()}
_OPEN_KEYS = frozenset({"mo", "jaw"})

# ── Text → Laute ──
# Vokallänge: Doppelvokal, Dehnungs-h, ie → lang; ein Folgekonsonant → lang (offene Silbe);
# zwei und mehr → kurz; unbetonte Silben kurz. Endungen -e/-en/-el/-em → Schwa, -er und r
# nach Vokal → vokalisiertes r. Betonung: erster Vokal, nach Vorsilbe be-/ge-/ver-/zer-/
# ent-/emp- der zweite. Bewusst einfach; Ausnahmen werden falsch.
_LETTER_VOWELS = "aeiouäöüy"
_SHORT_WORDS = frozenset({
    "das", "was", "es", "des", "in", "im", "an", "am", "um", "ab",
    "ob", "mit", "hat", "man", "bis", "hin", "von", "bin", "ins", "ans",
})
_VOWEL_MAP: dict[str, tuple[str, str]] = {  # Buchstabe auf das Paar kurz, lang
    "a": ("a", "a:"), "e": ("E", "e:"), "i": ("I", "i:"), "o": ("O", "o:"), "u": ("U", "u:"),
    "ä": ("E", "E:"), "ö": ("9", "2:"), "ü": ("Y", "y:"), "y": ("Y", "y:"),
}
_BACK_VOWELS = frozenset({"a", "a:", "o:", "O", "u:", "U"})  # danach wird ch zum ach-Laut
_SCHWA_ENDINGS = frozenset({"e", "en", "el", "em", "es", "et"})
_DIPHTHONGS: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (re.compile("ei|ai|ey|ay"), "a", "I"),
    (re.compile("au"), "a", "U"),
    (re.compile("eu|äu"), "O", "Y"),
)
# Buchstabenfolgen in der Reihenfolge des Prototyps; ch (leer) hängt am Vokal davor
_CLUSTERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("tsch", ("t", "S")), ("sch", ("S",)), ("chs", ("k", "s")), ("ch", ()), ("ck", ("k",)),
    ("ng", ("N",)), ("nk", ("N", "k")), ("pf", ("p", "f")), ("ph", ("f",)),
    ("qu", ("k", "v")), ("th", ("t",)), ("tz", ("t", "s")),
)
_SIMPLE_LETTERS: dict[str, tuple[str, ...]] = {
    "z": ("t", "s"), "x": ("k", "s"), "ß": ("s",), "v": ("f",), "w": ("v",),
}
_WORD = re.compile("[a-zäöüß]+")
_VOWEL_GROUP = re.compile("[aeiouäöüy]+")
_PREFIX = re.compile("be|ge|ver|zer|ent|emp")
_LONG_DOUBLE = re.compile("aa|ee|oo")
_ST_SP = re.compile("s[pt]")
# Leerraum wie `\s` im Prototyp (JavaScript), nicht wie in Python
_SPACE_CLASS = "\t\n\v\f\r    -     　﻿"
_PUNCTUATION_CLASS = ".,;:!?–\\-"
_TOKEN = re.compile(f"[a-zäöüß]+|[{_PUNCTUATION_CLASS}]|[{_SPACE_CLASS}]+")
_SPACE = re.compile(f"[{_SPACE_CLASS}]+")
_PUNCTUATION = re.compile(f"[{_PUNCTUATION_CLASS}]")


@dataclass(frozen=True)
class Phone:
    """Ein Laut im Text: SAMPA-Kürzel (oder `GAP` für die Wortlücke), Dauer, Amplitude."""

    code: str
    duration_ms: float
    amplitude: float


@dataclass(frozen=True)
class Segment:
    """Ein Laut auf der Zeitachse: Beginn, Ende, Mitte und Dauer in ms ab Sprechbeginn."""

    code: str
    start_ms: float  # im Prototyp t0
    end_ms: float  # im Prototyp t1
    center_ms: float  # im Prototyp c
    duration_ms: float  # im Prototyp d
    amplitude: float


@dataclass(frozen=True)
class SpeechChannels:
    """Die Sprechkanäle: Öffnung und Kiefer in Pixeln, Lippenmuskeln und Zunge in 0..1."""

    mouth_open: float  # mo
    jaw: float  # jaw
    upper_lip_raise: float  # up, AU10
    lower_lip_depress: float  # lo, AU16
    lip_stretch: float  # str, AU20
    lip_pucker: float  # pk, AU18
    lip_funnel: float  # fn, AU22
    lip_press: float  # press, AU24
    lip_bite: float  # fv, AU28
    tongue: float  # tng: 0 Mundboden, 1 Spitze am Gaumen


@dataclass(frozen=True)
class SpeechState:
    """Der Sprechzustand: die laufende Äußerung, die Federn der Kanäle, der Sprechanteil.

    `segments` und `end_ms` beschreiben die Äußerung ab `start_ms`; `active` ist wahr,
    bis ihr Ende überschritten ist. `blend` ist der Anteil der Sprechschicht am Mund
    (0..1), `blend_velocity` seine Geschwindigkeit je Sekunde.
    """

    segments: tuple[Segment, ...]
    end_ms: float
    start_ms: float
    active: bool
    current: SpeechChannels
    velocity: SpeechChannels
    blend: float
    blend_velocity: float


@dataclass
class _WordBuilder:
    """Arbeitsstand beim Zerlegen eines Worts: das Wort, seine Betonung, die Laute bisher."""

    word: str
    groups: int
    prefix: str
    stress_no: int
    vowel_no: int = 0
    phones: list[Phone] = field(default_factory=list)


SPEECH_PROTOTYPE_KEYS: dict[str, str] = dict(
    zip((f.name for f in fields(SpeechChannels)), SPEECH_KEYS, strict=True)
)
_SPEECH_FIELDS: tuple[str, ...] = tuple(SPEECH_PROTOTYPE_KEYS)
_ZERO_CHANNELS = SpeechChannels(*(0.0 for _ in SPEECH_KEYS))
_REST_TARGET = SpeechChannels(*PHONEMES[REST_CODE].values)

SILENT = SpeechState(
    segments=(),
    end_ms=0.0,
    start_ms=0.0,
    active=False,
    current=_ZERO_CHANNELS,
    velocity=_ZERO_CHANNELS,
    blend=0.0,
    blend_velocity=0.0,
)


def _channel_values(channels: SpeechChannels) -> tuple[float, ...]:
    """Die Kanäle in der Reihenfolge `SPEECH_KEYS`."""
    # ── Eingabe-Validierung ──
    if not isinstance(channels, SpeechChannels):
        raise TypeError(f"_channel_values: kein SpeechChannels: {type(channels).__name__}")

    # ── Verarbeitung ──
    return tuple(getattr(channels, name) for name in _SPEECH_FIELDS)


def _clamp01(x: float) -> float:
    """`x` begrenzt auf 0..1."""
    # ── Eingabe-Validierung ──
    # NaN fiele sonst still auf 1,0
    if not math.isfinite(x):
        raise ValueError(f"_clamp01: {x!r} ist nicht endlich")

    # ── Verarbeitung ──
    return max(0.0, min(1.0, x))


def _check_number(value: float, label: str) -> None:
    """Wirft, wenn `value` keine endliche Zahl ist."""
    # ── Eingabe-Validierung ──
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"{label} {value!r} ist keine Zahl")
    if not math.isfinite(value):
        raise ValueError(f"{label} {value!r} ist nicht endlich")


def _check_channels(channels: SpeechChannels, label: str) -> None:
    """Wirft, wenn ein Sprechkanal nicht endlich ist."""
    # ── Eingabe-Validierung ──
    bad = [name for name in _SPEECH_FIELDS if not math.isfinite(getattr(channels, name))]
    if bad:
        raise RuntimeError(f"{label}: Sprechkanäle nicht endlich: {bad}")


def _check_state(state: SpeechState) -> None:
    """Wirft, wenn `state` kein `SpeechState` ist."""
    # ── Eingabe-Validierung ──
    if not isinstance(state, SpeechState):
        raise TypeError(f"Sprechzustand ist kein SpeechState: {type(state).__name__}")


def _check_word_index(word: str, index: int, label: str) -> None:
    """Wirft, wenn `word` kein Text oder `index` keine ganze Zahl ist."""
    # ── Eingabe-Validierung ──
    if not isinstance(word, str):
        raise TypeError(f"{label}: Wort ist kein Text: {type(word).__name__}")
    if isinstance(index, bool) or not isinstance(index, int):
        raise TypeError(f"{label}: Stelle {index!r} ist keine ganze Zahl")


def _check_builder_index(builder: _WordBuilder, i: int, label: str) -> None:
    """Wirft, wenn `builder` kein `_WordBuilder` ist oder `i` nicht im Wort liegt."""
    # ── Eingabe-Validierung ──
    if not isinstance(builder, _WordBuilder):
        raise TypeError(f"{label}: kein _WordBuilder: {type(builder).__name__}")
    _check_word_index(builder.word, i, label)
    if not 0 <= i < len(builder.word):
        raise IndexError(f"{label}: Stelle {i} außerhalb von {builder.word!r}")


def _letter_is_vowel(word: str, index: int) -> bool:
    """Wahr, wenn an `index` ein Vokalbuchstabe steht; außerhalb des Worts falsch."""
    # ── Eingabe-Validierung ──
    _check_word_index(word, index, "_letter_is_vowel")

    # ── Verarbeitung ──
    return 0 <= index < len(word) and word[index] in _LETTER_VOWELS


def _letter_at(word: str, index: int) -> str:
    """Der Buchstabe an `index`, außerhalb des Worts der leere Text."""
    # ── Eingabe-Validierung ──
    _check_word_index(word, index, "_letter_at")

    # ── Verarbeitung ──
    return word[index] if 0 <= index < len(word) else ""


def _consonants_after(word: str, index: int) -> tuple[int, bool]:
    """Konsonantenbuchstaben ab `index` bis zum nächsten Vokal und ob das Wort dort endet.

    ch, ck und sch zählen doppelt: Davor ist der Vokal kurz.
    """
    # ── Eingabe-Validierung ──
    _check_word_index(word, index, "_consonants_after")
    if index < 0:
        raise IndexError(f"_consonants_after: Stelle {index} vor dem Wort")

    # ── Verarbeitung ──
    count = 0
    while index < len(word) and not _letter_is_vowel(word, index):
        if word.startswith("sch", index):
            count, index = count + 2, index + 3
        elif word.startswith("ch", index) or word.startswith("ck", index):
            count, index = count + 2, index + 2
        else:
            count, index = count + 1, index + 1
    return count, index >= len(word)


def _add_consonants(builder: _WordBuilder, *codes: str) -> None:
    """Hängt Konsonanten mit der Grunddauer ihrer Klasse an."""
    # ── Eingabe-Validierung ──
    unknown = [code for code in codes if code not in PHONEMES]
    if unknown:
        raise ValueError(f"_add_consonants: unbekannte Laute {unknown}")

    # ── Verarbeitung ──
    for code in codes:
        duration = PHONE_CLASSES[PHONEMES[code].phone_class].duration_ms
        builder.phones.append(Phone(code, float(duration), 1.0))


def _add_vowel(builder: _WordBuilder, code: str, duration_ms: float | None = None) -> None:
    """Hängt einen Vokal an: Schwa 0,5, vokalisiertes r 0,7, betont 1, sonst 0,8."""
    # ── Eingabe-Validierung ──
    if code not in PHONEMES:
        raise ValueError(f"_add_vowel: unbekannter Laut {code!r}")

    # ── Verarbeitung ──
    if code == "@":
        amplitude = 0.5
    elif code == "6":
        amplitude = 0.7
    else:
        amplitude = 1.0 if builder.vowel_no == builder.stress_no else 0.8
    if duration_ms is None:
        duration_ms = PHONE_CLASSES[PHONEMES[code].phone_class].duration_ms
    builder.phones.append(Phone(code, float(duration_ms), amplitude))
    builder.vowel_no += 1


def _last_vowel(builder: _WordBuilder) -> str:
    """Der letzte Vokallaut bisher, sonst der leere Text."""
    # ── Eingabe-Validierung ──
    if not isinstance(builder, _WordBuilder):
        raise TypeError(f"_last_vowel: kein _WordBuilder: {type(builder).__name__}")

    # ── Verarbeitung ──
    for phone in reversed(builder.phones):
        if phone.code in VOWEL_CODES:
            return phone.code
    return ""


def _vowel_cluster(builder: _WordBuilder, i: int) -> int | None:
    """Diphthong, ie, Doppelvokal, Dehnungs-h ab `i`; die neue Stelle oder `None`."""
    # ── Eingabe-Validierung ──
    _check_builder_index(builder, i, "_vowel_cluster")

    # ── Verarbeitung ──
    word = builder.word
    rest = word[i:]
    for pattern, first, second in _DIPHTHONGS:
        if pattern.match(rest):
            # zwei Ziele mit Gleitbewegung, betont wie ein Vokal
            _add_vowel(builder, first, 110)
            builder.vowel_no -= 1
            _add_vowel(builder, second, 90)
            return i + 2
    if rest.startswith("ie"):
        _add_vowel(builder, "i:")
        return i + 3 if _letter_at(word, i + 2) == "h" else i + 2
    if _LONG_DOUBLE.match(rest):
        _add_vowel(builder, _VOWEL_MAP[word[i]][1])
        return i + 2
    # Dehnungs-h vor Konsonant oder Wortende, vor Vokal nur nicht am Wortanfang
    if _letter_at(word, i + 1) == "h" and (not _letter_is_vowel(word, i + 2) or i > 0):
        _add_vowel(builder, _VOWEL_MAP[word[i]][1])
        return i + 2
    return None


def _vowel_ending(builder: _WordBuilder, i: int) -> int | None:
    """Schwa, vokalisiertes -er, e der Vorsilbe, -ig ab `i`; die neue Stelle oder `None`."""
    # ── Eingabe-Validierung ──
    _check_builder_index(builder, i, "_vowel_ending")

    # ── Verarbeitung ──
    word, c = builder.word, builder.word[i]
    rest = word[i:]
    unstressed_end = (
        c == "e"
        and builder.groups > 1
        and builder.vowel_no == builder.groups - 1
        and builder.vowel_no > builder.stress_no
    )
    if unstressed_end and rest in _SCHWA_ENDINGS:
        _add_vowel(builder, "@")
        return i + 1
    if unstressed_end and rest == "er":
        _add_vowel(builder, "6", 90)
        return i + 2
    if c == "e" and builder.prefix and i < len(builder.prefix):
        _add_vowel(builder, "@")
        return i + 1
    if c == "i" and rest == "ig" and builder.groups > 1:
        _add_vowel(builder, "I")
        _add_consonants(builder, "C")
        return i + 2
    return None


def _plain_vowel(builder: _WordBuilder, i: int) -> int:
    """Ein einfacher Vokal ab `i`, lang oder kurz nach den Konsonanten danach."""
    # ── Eingabe-Validierung ──
    _check_builder_index(builder, i, "_plain_vowel")

    # ── Verarbeitung ──
    word, c = builder.word, builder.word[i]
    count, at_end = _consonants_after(word, i + 1)
    is_long = count in (0, 1)
    if at_end and builder.groups == 1 and word in _SHORT_WORDS:
        is_long = False
    if builder.vowel_no != builder.stress_no and builder.groups > 1:
        is_long = count == 0  # unbetont: kurz
    if _letter_at(word, i + 1) == "r" and count == 1 and at_end:
        is_long = True  # der, vor, für
    _add_vowel(builder, _VOWEL_MAP[c][1 if is_long else 0])
    return i + 1


def _consonant_cluster(builder: _WordBuilder, i: int) -> int | None:
    """Doppelkonsonant, Buchstabenfolge, st/sp am Wortstamm ab `i`; neue Stelle oder `None`."""
    # ── Eingabe-Validierung ──
    _check_builder_index(builder, i, "_consonant_cluster")

    # ── Verarbeitung ──
    word = builder.word
    rest = word[i:]
    if i > 0 and word[i] == word[i - 1]:
        return i + 1  # Doppelkonsonant zählt einfach
    for letters, codes in _CLUSTERS:
        if rest.startswith(letters):
            if not codes:
                codes = ("x",) if _last_vowel(builder) in _BACK_VOWELS else ("C",)
            _add_consonants(builder, *codes)
            return i + len(letters)
    if _ST_SP.match(rest) and (i == 0 or i == len(builder.prefix)):
        _add_consonants(builder, "S", rest[1])
        return i + 2
    return None


def _single_consonant(builder: _WordBuilder, i: int) -> int:
    """Ein einzelner Konsonantenbuchstabe an `i`; ein Buchstabe ohne Laut ergibt nichts."""
    # ── Eingabe-Validierung ──
    _check_builder_index(builder, i, "_single_consonant")

    # ── Verarbeitung ──
    # je Buchstabe eine frühe Rückkehr statt einer elif-Kette: flacher, gleiche Wirkung
    word, c = builder.word, builder.word[i]
    following = _letter_at(word, i + 1)
    if c in _SIMPLE_LETTERS:
        _add_consonants(builder, *_SIMPLE_LETTERS[c])
        return i + 1
    if c == "s":
        _add_consonants(builder, "z" if _letter_is_vowel(word, i + 1) else "s")
        return i + 1
    if c == "c":
        # wie im Prototyp auch am Wortende: der leere Folgebuchstabe zählt als e, i, ä
        _add_consonants(builder, *(("t", "s") if following in "eiä" else ("k",)))
        return i + 1
    if c == "r":
        after_vowel = i > 0 and _letter_is_vowel(word, i - 1)
        if after_vowel and not _letter_is_vowel(word, i + 1) and following != "r":
            builder.phones.append(Phone("6", 60.0, 0.7))  # vokalisiert
        else:
            _add_consonants(builder, "R")
        return i + 1
    if c in PHONEMES:
        _add_consonants(builder, c)
    return i + 1


def word_to_phonemes(word: str) -> tuple[Phone, ...]:
    """Die Laute eines Worts aus Kleinbuchstaben a–z, ä, ö, ü, ß, regelbasiert wie im Prototyp.

    Ein Wort, das keinen Laut ergibt (etwa nur `q`), liefert nichts.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(word, str):
        raise TypeError(f"word_to_phonemes: Wort ist kein Text: {type(word).__name__}")
    if not _WORD.fullmatch(word):
        raise ValueError(f"word_to_phonemes: {word!r} ist kein Wort aus Kleinbuchstaben")

    # ── Verarbeitung ──
    groups = len(_VOWEL_GROUP.findall(word))
    prefix_match = _PREFIX.match(word) if groups > 1 and len(word) >= 6 else None
    prefix = prefix_match.group(0) if prefix_match else ""
    builder = _WordBuilder(word, groups, prefix, 1 if prefix else 0)
    i = 0
    while i < len(word):
        if word[i] in _LETTER_VOWELS:
            step = _vowel_cluster(builder, i)
            step = _vowel_ending(builder, i) if step is None else step
            i = _plain_vowel(builder, i) if step is None else step
        else:
            step = _consonant_cluster(builder, i)
            i = _single_consonant(builder, i) if step is None else step
    result = tuple(builder.phones)

    # ── Ausgabe-Verifikation ──
    unknown = [p.code for p in result if p.code not in PHONEMES]
    if unknown:
        raise RuntimeError(f"word_to_phonemes: {word!r} ergab unbekannte Laute {unknown}")
    if any(p.duration_ms <= 0 or not 0 < p.amplitude <= 1 for p in result):
        raise RuntimeError(f"word_to_phonemes: {word!r} ergab einen Laut ohne Dauer oder Stärke")
    return result


def text_to_phonemes(text: str) -> tuple[Phone, ...]:
    """Die Laute eines Texts: Satzzeichen als Pause, Wortgrenze als Lücke, am Ende eine Pause.

    Was weder Buchstabe, Satzzeichen noch Leerraum ist (Ziffern, Sternchen,
    Anführungszeichen), ergibt keinen Laut. Ein leerer Text ergibt nur die Schlusspause.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(text, str):
        raise TypeError(f"text_to_phonemes: Text ist kein str: {type(text).__name__}")

    # ── Verarbeitung ──
    rest_ms = float(PHONE_CLASSES["rest"].duration_ms)
    phones: list[Phone] = []
    for token in _TOKEN.findall(text.lower()):
        if _SPACE.fullmatch(token):
            phones.append(Phone(GAP_CODE, float(GAP_MS), 1.0))
        elif _PUNCTUATION.fullmatch(token):
            phones.append(Phone(REST_CODE, rest_ms, 1.0))
        else:
            phones.extend(word_to_phonemes(token))
    phones.append(Phone(REST_CODE, rest_ms, 1.0))
    result = tuple(phones)

    # ── Ausgabe-Verifikation ──
    if result[-1].code != REST_CODE:
        raise RuntimeError("text_to_phonemes: die Schlusspause fehlt")
    return result


def speech_timeline(
    phones: Sequence[Phone], rate: float = 1.0
) -> tuple[tuple[Segment, ...], float]:
    """Die Zeitachse ab 0 ms: je Laut ein Abschnitt, Dauer geteilt durch das Tempo; dazu das Ende.

    Die Wortlücke trägt Zeit, aber keinen Abschnitt.
    """
    # ── Eingabe-Validierung ──
    _check_number(rate, "speech_timeline: Sprechtempo")
    if rate <= 0:
        raise ValueError(f"speech_timeline: Sprechtempo {rate!r} muss positiv sein")
    if not all(isinstance(p, Phone) for p in phones):
        raise TypeError("speech_timeline: ein Eintrag ist kein Phone")
    if not phones:
        raise ValueError("speech_timeline: keine Laute")
    unknown = [p.code for p in phones if p.code != GAP_CODE and p.code not in PHONEMES]
    if unknown:
        raise ValueError(f"speech_timeline: unbekannte Laute {unknown}")

    # ── Verarbeitung ──
    elapsed = 0.0
    segments = []
    for phone in phones:
        d = phone.duration_ms / rate
        if phone.code != GAP_CODE:
            segments.append(
                Segment(phone.code, elapsed, elapsed + d, elapsed + d / 2, d, phone.amplitude)
            )
        elapsed += d
    result = tuple(segments)

    # ── Ausgabe-Verifikation ──
    if not math.isfinite(elapsed) or elapsed <= 0:
        raise RuntimeError(f"speech_timeline: Ende {elapsed!r} ist keine positive Zahl")
    return result, elapsed


def start_speech(state: SpeechState, text: str, now_ms: float, rate: float = 1.0) -> SpeechState:
    """Beginnt eine Äußerung zur Zeit `now_ms`; Federn und Sprechanteil laufen stetig weiter."""
    # ── Eingabe-Validierung ──
    _check_state(state)
    _check_number(now_ms, "start_speech: Zeit")

    # ── Verarbeitung ──
    segments, end_ms = speech_timeline(text_to_phonemes(text), rate)
    result = SpeechState(
        segments=segments,
        end_ms=end_ms,
        start_ms=float(now_ms),
        active=True,
        current=state.current,
        velocity=state.velocity,
        blend=state.blend,
        blend_velocity=state.blend_velocity,
    )
    logger.debug(f"Sprechen: {' '.join(s.code for s in segments)} | Dauer {round(end_ms)} ms")

    # ── Ausgabe-Verifikation ──
    if not result.segments or result.segments[-1].code != REST_CODE:
        raise RuntimeError("start_speech: Äußerung ohne Schlusspause")
    return result


def _lip_closure(segments: Sequence[Segment], t_ms: float, press: float) -> float:
    """Das Pressen, erzwungen in der Mitte von m, b und p: die Lippen schließen wirklich."""
    # ── Eingabe-Validierung ──
    if not math.isfinite(t_ms) or not math.isfinite(press):
        raise ValueError(f"_lip_closure: Zeit {t_ms!r} oder Pressen {press!r} nicht endlich")

    # ── Verarbeitung ──
    for segment in segments:
        if segment.code not in BILABIAL_CODES:
            continue
        closure = 1 - abs(t_ms - segment.center_ms) / (segment.duration_ms * CLOSURE_SPAN)
        if closure > 0:
            press = max(press, min(1.0, closure * CLOSURE_GAIN))
    return press


def coart_target(segments: Sequence[Segment], t_ms: float) -> tuple[SpeechChannels, str]:
    """Das Ziel der Sprechkanäle zur Zeit `t_ms` ab Sprechbeginn und der Laut darin.

    Je Kanal der dominanzgewichtete Mittelwert aller Laute im Umkreis (Cohen und
    Massaro 1993): innerhalb eines Lauts volle Dominanz, außerhalb fällt sie exponentiell
    mit der Reichweite. Öffnung und Kiefer haben nur `OPEN_REACH` der Reichweite, damit
    der Silbenrhythmus erhalten bleibt; die Lippenform läuft durch die Konsonanten. Der
    Laut ist der erste, in dem `t_ms` liegt, sonst `LABEL_NONE`.
    """
    # ── Eingabe-Validierung ──
    _check_number(t_ms, "coart_target: Zeit")
    if not all(isinstance(s, Segment) for s in segments):
        raise TypeError("coart_target: ein Abschnitt ist kein Segment")
    unknown = [s.code for s in segments if s.code not in PHONEMES]
    if unknown:
        raise ValueError(f"coart_target: Abschnitte unbekannter Laute {unknown}")

    # ── Verarbeitung ──
    sums = dict.fromkeys(SPEECH_KEYS, 0.0)
    weights = dict.fromkeys(SPEECH_KEYS, DOMINANCE_FLOOR)
    label, best = LABEL_NONE, -1.0
    for segment in segments:
        dist = max(0.0, abs(t_ms - segment.center_ms) - segment.duration_ms / 2)
        phoneme = PHONEMES[segment.code]
        reach = phoneme.reach_ms
        if dist > reach * REACH_CUTOFF:
            continue
        fall_shape = math.exp(-dist / reach)
        fall_open = math.exp(-dist / (reach * OPEN_REACH))
        for index, key in enumerate(SPEECH_KEYS):
            if key in _OPEN_KEYS:
                weight = phoneme.dominance[index] * fall_open
                value = phoneme.values[index] * segment.amplitude * SPEECH_OPEN_GAIN
            else:
                weight = phoneme.dominance[index] * fall_shape
                value = phoneme.values[index]
            sums[key] += weight * value
            weights[key] += weight
        if dist == 0 and fall_shape > best:
            best, label = fall_shape, segment.code
    target = {key: sums[key] / weights[key] for key in SPEECH_KEYS}
    target["press"] = _lip_closure(segments, t_ms, target["press"])
    result = SpeechChannels(*(target[key] for key in SPEECH_KEYS))

    # ── Ausgabe-Verifikation ──
    _check_channels(result, "coart_target")
    return result, label


def speech_step(state: SpeechState, now_ms: float, dt_s: float) -> SpeechState:
    """Ein Schritt des Sprechens zur Zeit `now_ms` über `dt_s` Sekunden.

    Solange die Äußerung läuft, folgen die Kanäle dem Ziel der Koartikulation, danach
    der Ruhe; ist ihr Ende überschritten, wird sie inaktiv. Eine Zeit knapp vor dem
    Sprechbeginn zählt als Beginn. Jeder Kanal folgt seiner Feder aus `SPRING_OMEGA`,
    der Sprechanteil der Feder `BLEND_OMEGA` zu 1 (aktiv) oder 0.
    """
    # ── Eingabe-Validierung ──
    _check_state(state)
    _check_number(now_ms, "speech_step: Zeit")
    _check_number(dt_s, "speech_step: Zeitschritt")
    if dt_s < 0:
        raise ValueError(f"speech_step: Zeitschritt {dt_s!r} muss >= 0 sein")

    # ── Verarbeitung ──
    target, active = _REST_TARGET, state.active
    if active:
        t_ms = max(0.0, now_ms - state.start_ms)
        if t_ms > state.end_ms:
            active = False
        else:
            target, _ = coart_target(state.segments, t_ms)
    channels = zip(
        SPEECH_KEYS,
        _channel_values(target),
        _channel_values(state.current),
        _channel_values(state.velocity),
        strict=True,
    )
    positions, velocities = [], []
    for key, goal, position, speed in channels:
        omega = SPRING_OMEGA[key]
        decay = math.exp(-omega * dt_s)
        offset = position - goal
        tmp = (speed + omega * offset) * dt_s
        positions.append(goal + (offset + tmp) * decay)
        velocities.append((speed - omega * tmp) * decay)
    blend_goal = 1.0 if active else 0.0
    blend_decay = math.exp(-BLEND_OMEGA * dt_s)
    blend_offset = state.blend - blend_goal
    blend_tmp = (state.blend_velocity + BLEND_OMEGA * blend_offset) * dt_s
    result = SpeechState(
        segments=state.segments,
        end_ms=state.end_ms,
        start_ms=state.start_ms,
        active=active,
        current=SpeechChannels(*positions),
        velocity=SpeechChannels(*velocities),
        blend=blend_goal + (blend_offset + blend_tmp) * blend_decay,
        blend_velocity=(state.blend_velocity - BLEND_OMEGA * blend_tmp) * blend_decay,
    )

    # ── Ausgabe-Verifikation ──
    _check_channels(result.current, "speech_step: Position")
    _check_channels(result.velocity, "speech_step: Geschwindigkeit")
    if not math.isfinite(result.blend) or not math.isfinite(result.blend_velocity):
        raise RuntimeError(f"speech_step: Sprechanteil nicht endlich: {result.blend!r}")
    return result


def _speak_into(mouth: dict[str, float], share: float, voice: dict[str, float]) -> float:
    """Legt die Sprechschicht mit dem Anteil `share` auf `mouth`; liefert die Zunge."""
    # ── Eingabe-Validierung ──
    if not 0 <= share <= 1:
        raise ValueError(f"_speak_into: Sprechanteil {share!r} außerhalb 0..1")
    missing = [key for key in SPEECH_KEYS if key not in voice]
    if missing:
        raise KeyError(f"_speak_into: Sprechkanäle fehlen: {missing}")

    # ── Verarbeitung ──
    emotion = dict(mouth)
    mouth["mo"] = emotion["mo"] + share * (voice["mo"] - emotion["mo"])
    mouth["jaw"] = emotion["jaw"] + share * (voice["jaw"] - emotion["jaw"])
    for side in ("L", "R"):
        mouth["au10" + side] = emotion["au10" + side] + share * voice["up"]
        mouth["au16" + side] = emotion["au16" + side] + share * voice["lo"]
        mouth["au20" + side] = emotion["au20" + side] + share * voice["str"]
    mouth["au18"] = emotion["au18"] + share * voice["pk"]
    mouth["au22"] = emotion["au22"] + share * voice["fn"]
    mouth["au24"] = emotion["au24"] + share * _clamp01(voice["press"])
    mouth["au28"] = emotion["au28"] + share * voice["fv"]
    return share * _clamp01(voice["tng"])


def mouth_state_combine(face: FaceState, state: SpeechState) -> tuple[FaceState, float]:
    """Der Mund aus Emotion und Sprechen, dazu die Zungenhöhe in 0..1.

    Öffnung und Kiefer gehen mit dem Sprechanteil vom Wert der Emotion zum Wert des
    Lauts, die Muskelkanäle kommen additiv dazu; alle Mundmuskeln werden auf 0..1
    begrenzt. Schließende Muskeln wirken danach immer auf die Öffnung (Pressen,
    Unterlippe einziehen, Spannen, Kinn heben), Spitzen und Pressen dämpfen das Lächeln.
    Unter `BLEND_THRESHOLD` bleibt der Mund der Emotion, die Zunge liegt am Mundboden (0).
    """
    # ── Eingabe-Validierung ──
    if not isinstance(face, FaceState):
        raise TypeError(f"mouth_state_combine: Gesicht ist kein FaceState: {type(face).__name__}")
    _check_state(state)
    bad = [name for name in PROTOTYPE_KEYS if not math.isfinite(getattr(face, name))]
    if bad:
        raise ValueError(f"mouth_state_combine: Kanäle des Gesichts nicht endlich: {bad}")

    # ── Verarbeitung ──
    share = _clamp01(state.blend)
    out = {key: getattr(face, name) for name, key in PROTOTYPE_KEYS.items()}
    tongue = 0.0
    if share >= BLEND_THRESHOLD:
        voice = dict(zip(SPEECH_KEYS, _channel_values(state.current), strict=True))
        tongue = _speak_into(out, share, voice)
    for key in _MOUTH_AU:
        out[key] = _clamp01(out[key])
    out["mo"] *= (
        (1 - out["au24"]) * (1 - 0.7 * out["au28"]) * (1 - 0.35 * out["au23"])
        * (1 - 0.3 * out["au17"])
    )
    out["jaw"] *= (1 - 0.8 * out["au24"]) * (1 - 0.4 * out["au28"])
    out["mc"] = out["mc"] * (1 - 0.5 * min(1.0, out["au18"] + out["au22"]) - 0.3 * out["au24"])
    result = FaceState(**{_FIELD_BY_KEY[key]: float(value) for key, value in out.items()})

    # ── Ausgabe-Verifikation ──
    bad = [key for key, value in out.items() if not math.isfinite(value)]
    if bad:
        raise RuntimeError(f"mouth_state_combine: Kanäle nicht endlich: {bad}")
    if not 0 <= tongue <= 1:
        raise RuntimeError(f"mouth_state_combine: Zunge {tongue!r} außerhalb 0..1")
    return result, tongue
