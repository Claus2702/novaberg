"""Untertitel: der gesprochene Text in Tafeln, das gesprochene Wort unterstrichen.

Reine Logik ohne GTK und ohne Uhr. Die Zeitfenster der Wörter stammen aus derselben
Zeitachse wie der Mund (`speech_timeline(text_to_phonemes(text))`, Tempo 1): Ein Wort
reicht vom Beginn des ersten bis zum Ende des letzten Lauts, den seine Buchstaben
erzeugen; die Pausen seiner Satzzeichen gehören nicht dazu. Ein Wort ohne Laut (`42`,
`–`) hat kein Fenster und wird nie unterstrichen.

Der Text steht in Tafeln von höchstens `BOARD_LIMIT` Zeichen; nach einem Satzende beginnt
eine neue. Die Tafel wechselt mit dem ersten Fenster ihres ersten Worts mit Laut. Das
gesprochene Wort ist das letzte, dessen Fenster begonnen hat; in einer Pause zwischen
zwei Wörtern bleibt es unterstrichen. Nach dem Ende der Wiedergabe steht die letzte Tafel
noch `HOLD_MS`, ohne Unterstrich, dann ist der Untertitel leer.
"""

import math
from dataclasses import dataclass
from xml.sax.saxutils import escape

from avatar.speech import Segment, WrittenWord, speech_timeline, text_to_phonemes, text_to_words

BOARD_LIMIT = 80  # Zeichen je Tafel: zwei Zeilen zu etwa 40 bei 480 px Breite
HOLD_MS = 1500.0  # so lange steht die letzte Tafel nach dem Ende der Wiedergabe
_SENTENCE_END = ".!?…"
_CLOSERS = "\"'“”’»«)]}›‹"  # dürfen hinter dem Satzzeichen stehen


@dataclass(frozen=True)
class SubtitleWord:
    """Ein Wort des Untertitels, wie es dasteht, mit Fenster in ms ab Sprechbeginn.

    `start_ms` und `end_ms` sind beide None, wenn das Wort keinen Laut hat.
    """

    text: str
    start_ms: float | None
    end_ms: float | None


@dataclass(frozen=True)
class SubtitleRun:
    """Der Untertitel einer Äußerung: Wörter mit Fenstern, Tafeln, Beginn und Dauer.

    `boards` sind Spannen `[von, bis)` in `words`, lückenlos und in Reihenfolge.
    `start_ms` ist die Zeit des Sprechbeginns auf der Uhr der Puppe, `duration_ms` das
    Ende der Wiedergabe ab dort.
    """

    words: tuple[SubtitleWord, ...]
    boards: tuple[tuple[int, int], ...]
    start_ms: float
    duration_ms: float


@dataclass(frozen=True)
class Subtitle:
    """Was zu sehen ist: die Wörter der Tafel, `spoken` der Index des gesprochenen darin."""

    words: tuple[str, ...]
    spoken: int | None


def _window(word: WrittenWord, segments: tuple[Segment, ...], offset: int) -> SubtitleWord:
    """Das Wort mit seinem Fenster; `offset` ist die Zahl der Abschnitte vor dem Wort."""
    # ── Eingabe-Validierung ──
    if offset < 0 or offset + len(word.phones) > len(segments):
        raise ValueError(f"_window: Abschnitte ab {offset} liegen außerhalb der Zeitachse")

    # ── Verarbeitung ──
    if word.letters is None:
        return SubtitleWord(word.text, None, None)
    first = segments[offset + word.letters[0]]
    last = segments[offset + word.letters[1] - 1]

    # ── Ausgabe-Verifikation ──
    if first.code != word.phones[word.letters[0]].code or first.start_ms > last.end_ms:
        raise RuntimeError(f"_window: Fenster von {word.text!r} liegt nicht auf seinen Lauten")
    return SubtitleWord(word.text, first.start_ms, last.end_ms)


def subtitle_words(text: str) -> tuple[SubtitleWord, ...]:
    """Die Wörter des Texts mit ihren Fenstern auf der Zeitachse des Mundes (Tempo 1).

    Vorbedingung: `text` ist ein str.
    Nachbedingung: ein Eintrag je Wort in Schreibweise und Reihenfolge; die Fenster
    steigen und überlappen nicht.
    Fehlerfälle: TypeError ohne str; RuntimeError, wenn Zerlegung und Zeitachse nicht
    zueinander passen.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(text, str):
        raise TypeError(f"subtitle_words: Text ist kein str: {type(text).__name__}")

    # ── Verarbeitung ──
    written = text_to_words(text)
    segments, _ = speech_timeline(text_to_phonemes(text))
    if len(segments) != sum(len(w.phones) for w in written) + 1:
        raise RuntimeError("subtitle_words: Wörter und Zeitachse haben verschiedene Laute")
    words = []
    offset = 0
    for word in written:
        words.append(_window(word, segments, offset))
        offset += len(word.phones)
    result = tuple(words)

    # ── Ausgabe-Verifikation ──
    ends = [w.end_ms for w in result if w.end_ms is not None]
    starts = [w.start_ms for w in result if w.start_ms is not None]
    if any(start < end for start, end in zip(starts[1:], ends, strict=False)):
        raise RuntimeError("subtitle_words: Fenster überlappen oder fallen zurück")
    return result


def _ends_sentence(text: str) -> bool:
    """Wahr, wenn das Wort mit `.`, `!`, `?` oder `…` endet, auch vor schließenden Zeichen."""
    # ── Eingabe-Validierung ──
    if not isinstance(text, str):
        raise TypeError(f"_ends_sentence: Text ist kein str: {type(text).__name__}")

    # ── Verarbeitung ──
    core = text.rstrip(_CLOSERS)
    return core.endswith(tuple(_SENTENCE_END))


def subtitle_boards(
    words: tuple[SubtitleWord, ...], limit: int = BOARD_LIMIT
) -> tuple[tuple[int, int], ...]:
    """Teilt die Wörter in Tafeln: höchstens `limit` Zeichen, nach einem Satzende eine neue.

    Ein Wort, das allein länger ist als `limit`, steht allein auf seiner Tafel.
    Vorbedingung: `words` ist ein Tupel von `SubtitleWord`, `limit` eine ganze Zahl > 0.
    Nachbedingung: Spannen `[von, bis)`, lückenlos von 0 bis zur Zahl der Wörter, keine leer.
    Fehlerfälle: TypeError und ValueError bei falscher Eingabe.
    """
    # ── Eingabe-Validierung ──
    if not all(isinstance(w, SubtitleWord) for w in words):
        raise TypeError("subtitle_boards: ein Eintrag ist kein SubtitleWord")
    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise ValueError(f"subtitle_boards: Grenze {limit!r} muss eine ganze Zahl > 0 sein")

    # ── Verarbeitung ──
    boards: list[tuple[int, int]] = []
    start = 0
    length = 0
    for index, word in enumerate(words):
        size = len(word.text)
        if index > start and length + 1 + size > limit:
            boards.append((start, index))
            start = index
        length = length + 1 + size if index > start else size
        if _ends_sentence(word.text):
            boards.append((start, index + 1))
            start, length = index + 1, 0
    if start < len(words):
        boards.append((start, len(words)))
    result = tuple(boards)

    # ── Ausgabe-Verifikation ──
    edges = [0, *(end for _, end in result)]
    joined = all(a == b for a, (b, _) in zip(edges[:-1], result, strict=True))
    if not joined or edges[-1] != len(words) or any(a >= b for a, b in result):
        raise RuntimeError("subtitle_boards: die Tafeln decken die Wörter nicht lückenlos")
    return result


def subtitle_run(text: str, start_ms: float) -> SubtitleRun:
    """Der Untertitel einer Äußerung, die zur Zeit `start_ms` beginnt.

    Vorbedingung: `text` ist ein str mit mindestens einem Wort, `start_ms` endlich.
    Nachbedingung: Wörter mit Fenstern, Tafeln und die Dauer der Wiedergabe, dieselbe,
    die `start_speech` für den Text ansetzt.
    Fehlerfälle: TypeError ohne str, ValueError ohne Wort oder bei ungültiger Zeit.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(start_ms, int | float) or isinstance(start_ms, bool):
        raise ValueError(f"subtitle_run: Zeit {start_ms!r} ist keine Zahl")
    if not math.isfinite(start_ms):
        raise ValueError(f"subtitle_run: Zeit {start_ms!r} ist nicht endlich")

    # ── Verarbeitung ──
    words = subtitle_words(text)
    if not words:
        raise ValueError("subtitle_run: Text ohne Wort")
    result = SubtitleRun(
        words=words,
        boards=subtitle_boards(words),
        start_ms=float(start_ms),
        duration_ms=speech_timeline(text_to_phonemes(text))[1],
    )

    # ── Ausgabe-Verifikation ──
    if result.duration_ms <= 0 or not result.boards:
        raise RuntimeError("subtitle_run: Untertitel ohne Dauer oder ohne Tafel")
    return result


def _last_started(words: tuple[SubtitleWord, ...], t_ms: float) -> int | None:
    """Der Index des letzten Worts mit Fenster, das zur Zeit `t_ms` begonnen hat; sonst None."""
    # ── Eingabe-Validierung ──
    if t_ms < 0:
        raise ValueError(f"_last_started: Zeit {t_ms!r} vor dem Sprechbeginn")

    # ── Verarbeitung ──
    found = None
    for index, word in enumerate(words):
        if word.start_ms is None:
            continue
        if word.start_ms > t_ms:
            break
        found = index
    return found


def _board_of(boards: tuple[tuple[int, int], ...], index: int) -> tuple[int, int]:
    """Die Tafel, die das Wort mit dem Index `index` enthält."""
    # ── Eingabe-Validierung ──
    if not boards or not 0 <= index < boards[-1][1]:
        raise ValueError(f"_board_of: Wort {index!r} liegt in keiner Tafel")

    # ── Verarbeitung ──
    return next(board for board in boards if board[0] <= index < board[1])


def subtitle_at(run: SubtitleRun, now_ms: float) -> Subtitle | None:
    """Der Untertitel zur Zeit `now_ms` auf der Uhr von `run.start_ms`; None, wenn er leer ist.

    Während der Wiedergabe zeigt er die Tafel des gesprochenen Worts, vor dem ersten Fenster
    die erste Tafel. Ab dem Ende der Wiedergabe steht die letzte Tafel ohne Unterstrich,
    bis `HOLD_MS` verstrichen sind: bei `Ende + HOLD_MS - 1` noch da, bei `Ende + HOLD_MS` leer.
    Vorbedingung: `run` ist ein `SubtitleRun`, `now_ms` nicht vor `run.start_ms`.
    Fehlerfälle: TypeError ohne `SubtitleRun`, ValueError bei Zeit vor dem Beginn.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(run, SubtitleRun):
        raise TypeError(f"subtitle_at: kein SubtitleRun: {type(run).__name__}")
    t_ms = now_ms - run.start_ms
    if t_ms < 0:
        raise ValueError(f"subtitle_at: Zeit {now_ms!r} liegt vor dem Beginn {run.start_ms!r}")

    # ── Verarbeitung ──
    if t_ms >= run.duration_ms + HOLD_MS:
        return None
    spoken = _last_started(run.words, t_ms) if t_ms < run.duration_ms else None
    if t_ms >= run.duration_ms:
        first, end = run.boards[-1]
    else:
        first, end = _board_of(run.boards, 0 if spoken is None else spoken)
    result = Subtitle(
        words=tuple(w.text for w in run.words[first:end]),
        spoken=None if spoken is None else spoken - first,
    )

    # ── Ausgabe-Verifikation ──
    if not result.words:
        raise RuntimeError("subtitle_at: Tafel ohne Wörter")
    return result


def subtitle_markup(subtitle: Subtitle | None) -> str:
    """Die Tafel als Pango-Markup: genau ein `<u>` um das gesprochene Wort, der Text escaped.

    Vorbedingung: `subtitle` ist None (leer) oder ein `Subtitle` mit `spoken` None oder im
    Bereich seiner Wörter.
    Nachbedingung: der leere Text für None; sonst die Wörter mit Leerzeichen, `&`, `<` und
    `>` des Texts als Entitäten.
    Fehlerfälle: ValueError bei einem Index außerhalb der Tafel.
    """
    # ── Eingabe-Validierung ──
    if subtitle is None:
        return ""
    if subtitle.spoken is not None and not 0 <= subtitle.spoken < len(subtitle.words):
        raise ValueError(f"subtitle_markup: Wort {subtitle.spoken!r} nicht in der Tafel")

    # ── Verarbeitung ──
    parts = [escape(word) for word in subtitle.words]
    if subtitle.spoken is not None:
        parts[subtitle.spoken] = f"<u>{parts[subtitle.spoken]}</u>"
    result = " ".join(parts)

    # ── Ausgabe-Verifikation ──
    if result.count("<u>") != (subtitle.spoken is not None):
        raise RuntimeError("subtitle_markup: nicht genau ein Unterstrich um das Wort")
    return result
