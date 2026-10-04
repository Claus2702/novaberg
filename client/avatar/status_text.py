"""Der Text der Phasenanzeige: aus einem `IdleStatus` die Zeilen unter dem Gesicht.

Ohne GTK. Zahlen mit Komma. `status_due` hält den Takt der Anzeige.
"""

import math
from dataclasses import dataclass

from avatar.idle_catalog import IdleState
from avatar.idle_status import (
    NOTE_AFTERGLOW,
    NOTE_INHALING,
    NOTE_PLAYBACK,
    NOTE_WAITING,
    IdleStatus,
)

STATUS_INTERVAL_S = 0.12  # die Anzeige zieht höchstens alle 120 ms nach
SIDE_LIMIT = 0.12  # |x| darüber heißt seitlich
VERTICAL_LIMIT = 0.15  # |y| darüber heißt oben oder unten
STATE_NAMES = {
    IdleState.NOISE: "Rauschen", IdleState.THINKING: "Nachdenken",
    IdleState.ANSWER: "Antwort", IdleState.AFTERGLOW: "Nachklang",
}
_PLAN_ANSWER = "answer"
_PLAN_INHALE = "inhale"


@dataclass(frozen=True)
class BandSegment:
    """Ein Abschnitt des Bandes: Kennung, Anteil an der Gesamtdauer, ob die Form läuft."""

    form_id: str
    share: float
    running: bool


@dataclass(frozen=True)
class StatusLines:
    """Die vier Textzeilen der Anzeige: Zustand, Form, Fortgang der Form, Spanne."""

    state: str
    form: str
    progress: str
    span: str


def fmt(value: float, digits: int = 1) -> str:
    """Eine Zahl mit Komma; eine nicht endliche ergibt einen Strich.

    Vorbedingung: eine Zahl.
    Nachbedingung: Text ohne Punkt.
    """
    # ── Eingabe-Validierung ──
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"fmt: keine Zahl: {type(value).__name__}")

    # ── Verarbeitung ──
    if not math.isfinite(value):
        return "–"
    return f"{value:.{digits}f}".replace(".", ",")


def direction_text(gaze_x: float, gaze_y: float) -> str:
    """Die Blickrichtung als Text: oben/unten ab 0,15, seitlich ab 0,12, sonst zum Betrachter.

    Vorbedingung: endliche Koordinaten.
    Nachbedingung: `oben`, `unten`, `seitlich`, `oben-seitlich`, `unten-seitlich` oder
    `zum Betrachter`.
    """
    # ── Eingabe-Validierung ──
    if not (math.isfinite(gaze_x) and math.isfinite(gaze_y)):
        raise ValueError(f"direction_text: Blick ({gaze_x}, {gaze_y}) nicht endlich")

    # ── Verarbeitung ──
    vertical = "oben" if gaze_y < -VERTICAL_LIMIT else "unten" if gaze_y > VERTICAL_LIMIT else ""
    side = "seitlich" if abs(gaze_x) > SIDE_LIMIT else ""
    if vertical and side:
        return f"{vertical}-seitlich"
    return vertical or side or "zum Betrachter"


def _note_text(status: IdleStatus) -> str:
    """Die Angabe zum Zustand als Text, mit führendem Trennzeichen; leer im Rauschen.

    Vorbedingung: ein `IdleStatus`, dessen Sekunden zur Angabe passen.
    Nachbedingung: Text oder leer.
    """
    # ── Eingabe-Validierung ──
    note, seconds = status.note, status.note_s
    if note in (NOTE_INHALING, NOTE_PLAYBACK, NOTE_AFTERGLOW) and seconds is None:
        raise ValueError(f"_note_text: Angabe {note} ohne Sekunden")

    # ── Verarbeitung ──
    if note == NOTE_WAITING:
        return " · wartet auf die Antwort"
    if note == NOTE_INHALING:
        return f" · atmet ein, spricht in {fmt(seconds)} s"
    if note == NOTE_PLAYBACK:
        return f" · Wiedergabe, noch {fmt(seconds)} s"
    if note == NOTE_AFTERGLOW:
        total = fmt(status.note_total_s if status.note_total_s is not None else math.nan, 0)
        return f" · zurück ins Rauschen in {fmt(seconds, 0)} s (Dauer {total} s)"
    return ""


def _state_line(status: IdleStatus) -> str:
    """Die Zeile zum Zustand mit Angabe und Emotion.

    Vorbedingung: ein `IdleStatus`.
    Nachbedingung: `<Zustand> · seit <s> s<Angabe> · Emotion: <Quelle> — <Sektor>, Arousal <a>`.
    """
    # ── Eingabe-Validierung ──
    if status.state not in STATE_NAMES:
        raise ValueError(f"_state_line: Zustand {status.state!r} ohne Namen")

    # ── Verarbeitung ──
    return (f"{STATE_NAMES[status.state]} · seit {fmt(status.elapsed_s, 0)} s{_note_text(status)}"
            f" · Emotion: {status.source} — {status.sector_name}, Arousal {fmt(status.arousal, 2)}")


def _progress_line(status: IdleStatus) -> str:
    """Wie lange die Form steht, wohin der Blick geht, was als nächstes kommt.

    Vorbedingung: ein `IdleStatus`.
    Nachbedingung: `steht <s> von <d> s · Blick <Richtung> · nächste: <F> <Name> in <s> s`.
    """
    # ── Eingabe-Validierung ──
    form, following = status.form, status.next_form
    if form.duration_s < 0:
        raise ValueError(f"_progress_line: Dauer {form.duration_s} negativ")

    # ── Verarbeitung ──
    if following is None:
        upcoming = f"neuer Zyklus in {fmt(form.duration_s - form.elapsed_s)} s"
    else:
        upcoming = f"{following.form_id} {following.name} in {fmt(following.in_s)} s"
    return (f"steht {fmt(form.elapsed_s)} von {fmt(form.duration_s)} s"
            f" · Blick {direction_text(form.gaze_x, form.gaze_y)} · nächste: {upcoming}")


def _span_line(status: IdleStatus) -> str:
    """Die Spanne des Zyklus mit den gezogenen Dauern, bei Antwort und Einatmen deren Art.

    Vorbedingung: ein `IdleStatus`.
    Nachbedingung: eine Zeile.
    """
    # ── Eingabe-Validierung ──
    count = len(status.band)
    if count == 0:
        raise ValueError("_span_line: leeres Band")

    # ── Verarbeitung ──
    span = status.span
    if span is not None:
        drawn = " · ".join(f"{item.form_id} {fmt(item.duration_s)}" for item in status.band)
        return (f"x_c {fmt(span.xc)} s · Spanne {fmt(span.lo)}–{fmt(span.hi)} s"
                f" · n {span.count} · gezogen: {drawn}")
    if status.plan_kind == _PLAN_ANSWER:
        return f"Antwort: Wechsel nach Sprecherregel · {count} Aktionen"
    if status.plan_kind == _PLAN_INHALE:
        return "Einatmen: eine Aktion vor dem Sprechen"
    raise ValueError(f"_span_line: Plan {status.plan_kind!r} ohne Spanne")


def status_lines(status: IdleStatus) -> StatusLines:
    """Die Zeilen der Anzeige: Zustand, Form, Fortgang, Spanne.

    Vorbedingung: ein `IdleStatus`.
    Nachbedingung: vier nicht leere Zeilen; die Zeile der Form ist `<Kennung> <Name>`.
    Fehlerfälle: TypeError ohne `IdleStatus`.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(status, IdleStatus):
        raise TypeError(f"status_lines: kein IdleStatus: {type(status).__name__}")

    # ── Verarbeitung ──
    lines = StatusLines(
        state=_state_line(status), form=f"{status.form.form_id} {status.form.name}",
        progress=_progress_line(status), span=_span_line(status))

    # ── Ausgabe-Verifikation ──
    if not all((lines.state, lines.form, lines.progress, lines.span)):
        raise RuntimeError("status_lines: leere Zeile")
    return lines


def band_segments(status: IdleStatus) -> list[BandSegment]:
    """Das Band: je Form Kennung, Anteil an der Gesamtdauer und ob sie läuft.

    Vorbedingung: ein `IdleStatus` mit Band positiver Gesamtdauer.
    Nachbedingung: die Anteile ergeben 1, genau ein Abschnitt läuft.
    Fehlerfälle: TypeError ohne `IdleStatus`, ValueError bei Gesamtdauer 0.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(status, IdleStatus):
        raise TypeError(f"band_segments: kein IdleStatus: {type(status).__name__}")
    total = sum(item.duration_s for item in status.band)
    if not total > 0:
        raise ValueError(f"band_segments: Gesamtdauer {total} nicht positiv")

    # ── Verarbeitung ──
    segments = [BandSegment(item.form_id, item.duration_s / total, i == status.position)
                for i, item in enumerate(status.band)]

    # ── Ausgabe-Verifikation ──
    if not math.isclose(sum(s.share for s in segments), 1.0, abs_tol=1e-9):
        raise RuntimeError("band_segments: Anteile ergeben nicht 1")
    if sum(s.running for s in segments) != 1:
        raise RuntimeError("band_segments: nicht genau eine laufende Form")
    return segments


def status_due(last_s: float | None, now_s: float, interval_s: float = STATUS_INTERVAL_S) -> bool:
    """Ob die Anzeige jetzt nachzieht: beim ersten Bild und je `interval_s` danach.

    Vorbedingung: `now_s` endlich; `last_s` die Zeit der letzten Aktualisierung oder None.
    Nachbedingung: wahr, wenn noch nie aktualisiert wurde oder das Intervall verstrichen ist.
    Fehlerfälle: nicht endliche Zeit, Zeit vor der letzten Aktualisierung.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(now_s) or interval_s <= 0:
        raise ValueError(f"status_due: Zeit {now_s} oder Intervall {interval_s} ungültig")
    if last_s is not None and now_s < last_s:
        raise ValueError(f"status_due: Zeit {now_s} vor der letzten Aktualisierung {last_s}")

    # ── Verarbeitung ──
    return last_s is None or now_s - last_s >= interval_s
