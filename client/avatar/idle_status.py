"""Die Lese-Sicht des Leerlaufs: in welcher Phase das Gesicht gerade ist.

Reine Werte ohne Logik — `IdleLogic.status` füllt sie, `status_text` macht Zeilen daraus.
Zeiten stehen in Sekunden.
"""

import math
from dataclasses import dataclass

from avatar.idle_catalog import IdleState

NOTE_WAITING = "waiting"  # Nachdenken, die Antwort steht noch aus
NOTE_INHALING = "inhaling"  # Nachdenken, die Antwort ist da: Einatmen, dann Sprechen
NOTE_PLAYBACK = "playback"  # Antwort: Wiedergabe läuft
NOTE_AFTERGLOW = "afterglow"  # Nachklang: Rückweg ins Rauschen
NOTES = (NOTE_WAITING, NOTE_INHALING, NOTE_PLAYBACK, NOTE_AFTERGLOW)

SOURCE_NOVA = "Nova"
SOURCE_PIXIE = "Pixie"


@dataclass(frozen=True)
class StatusForm:
    """Die laufende Form: Kennung, Name, wie lange sie steht, ihre Dauer, ihr Blickpunkt."""

    form_id: str
    name: str
    elapsed_s: float
    duration_s: float
    gaze_x: float
    gaze_y: float


@dataclass(frozen=True)
class StatusNext:
    """Die nächste Form des Plans und in wie vielen Sekunden sie beginnt."""

    form_id: str
    name: str
    in_s: float


@dataclass(frozen=True)
class BandItem:
    """Eine Form des Plans im Band: Kennung und Dauer."""

    form_id: str
    duration_s: float


@dataclass(frozen=True)
class StatusSpan:
    """Die Spanne, mit der ein Zyklus geplant wurde: x_c, Grenzen und Zahl der Formen."""

    xc: float
    lo: float
    hi: float
    count: int


@dataclass(frozen=True)
class IdleStatus:
    """Die Phase des Leerlaufs zu einer Zeit.

    `since_ms` ist die Zeit, ab der der Zustand gilt, `elapsed_s` seine Dauer bis jetzt.
    `note` ist die Angabe zum Zustand (eine der `NOTES`, im Rauschen None) mit `note_s`
    (Sekunden bis zum Sprechen, bis zum Ende der Antwort, bis zurück ins Rauschen) und
    `note_total_s` (Dauer des Nachklangs). `source` sagt, wessen Emotion gilt. `band`
    sind die Formen des Plans, `position` die laufende darin. `plan_kind` ist `cycle`,
    `answer` oder `inhale`; nur ein Zyklus hat eine `span`; `next_form` ist None an der
    letzten Form des Plans (danach folgt ein neuer Zyklus).
    """

    state: IdleState
    since_ms: float
    elapsed_s: float
    note: str | None
    note_s: float | None
    note_total_s: float | None
    source: str
    sector_name: str
    arousal: float
    form: StatusForm
    next_form: StatusNext | None
    band: tuple[BandItem, ...]
    position: int
    plan_kind: str
    span: StatusSpan | None

    def __post_init__(self) -> None:
        """Weist einen Wert ab, der in sich nicht stimmt."""
        # ── Eingabe-Validierung ──
        if self.note is not None and self.note not in NOTES:
            raise ValueError(f"IdleStatus: unbekannte Angabe {self.note!r}")
        if self.source not in (SOURCE_NOVA, SOURCE_PIXIE):
            raise ValueError(f"IdleStatus: unbekannte Quelle {self.source!r}")
        if not 0 <= self.position < len(self.band):
            raise ValueError(f"IdleStatus: Stelle {self.position} außerhalb des Bandes")
        if self.band[self.position].form_id != self.form.form_id:
            raise ValueError("IdleStatus: die Stelle im Band ist nicht die laufende Form")
        if not math.isfinite(self.arousal):
            raise ValueError(f"IdleStatus: Arousal {self.arousal!r} nicht endlich")
