"""Die Warteschlange des Avatar-Panels: Antworten und Arbeitsereignisse in Reihenfolge.

Das Modul importiert kein GTK. Das Panel hat zwischen zwei Bildern keine Uhr; was in
dieser Zeit eintrifft, wartet hier und geht im nächsten Bild mit dessen Zeit an die
Puppe. Eine Antwort bleibt dabei an ihrem Platz zwischen den Ereignissen.
"""

import logging
from collections import deque

from avatar.idle import ImpulseThinks, PixieJob, TurnBegins, TurnFailed
from avatar.puppet import Puppet, Utterance, puppet_cue, puppet_event
from ui.work_events import (
    WORK_EVENT_TYPES,
    ImpulseThinking,
    PixieWork,
    TurnFailure,
    TurnStarted,
    WorkEvent,
)

logger = logging.getLogger(__name__)


def idle_call(event: WorkEvent) -> tuple[type, dict]:
    """Übersetzt ein Arbeitsereignis in Typ und Felder des Leerlaufs, ohne Zeit.

    Vorbedingung: `event` ist ein Ereignis aus `ui.work_events`.
    Nachbedingung: der Typ aus `avatar.idle` und seine Felder ohne `at_ms`; bei
    `PixieWork` ohne das Thema — das ist für die Statuszeile bestimmt, nicht für das Gesicht.
    Fehlerfall: TypeError bei einem anderen Typ.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(event, WORK_EVENT_TYPES):
        raise TypeError(f"idle_call: {type(event).__name__} ist kein Arbeitsereignis")

    # ── Verarbeitung ──
    if isinstance(event, TurnStarted):
        return TurnBegins, {}
    if isinstance(event, TurnFailure):
        return TurnFailed, {}
    if isinstance(event, ImpulseThinking):
        return ImpulseThinks, {"phase": event.phase}
    if not isinstance(event, PixieWork):
        raise TypeError(f"idle_call: {type(event).__name__} ohne Übersetzung")

    # Keine Ausgabe-Verifikation: Jede Rückgabe trägt ihren Typ und seine Felder.
    return PixieJob, {
        "phase": event.phase,
        "track": event.track,
        "job_kind": event.job_kind,
        "emotion": event.emotion,
        "arousal": event.arousal,
    }


class AvatarFeed:
    """Hält Antworten und Arbeitsereignisse vor, bis das nächste Bild sie übergibt."""

    def __init__(self) -> None:
        """Beginnt leer."""
        self._items: deque[Utterance | WorkEvent] = deque()

    def __len__(self) -> int:
        """Zahl der vorgemerkten Einträge."""
        return len(self._items)

    def add(self, item: Utterance | WorkEvent) -> None:
        """Merkt eine Antwort oder ein Arbeitsereignis hinter den bisherigen vor.

        Fehlerfall: TypeError bei allem anderen.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(item, (Utterance, *WORK_EVENT_TYPES)):
            raise TypeError(f"AvatarFeed: {type(item).__name__} ist weder Äußerung noch Ereignis")

        # ── Verarbeitung ──
        before = len(self._items)
        self._items.append(item)

        # ── Ausgabe-Verifikation ──
        if len(self._items) != before + 1 or self._items[-1] is not item:
            raise RuntimeError("AvatarFeed: Eintrag nicht hinter den bisherigen vorgemerkt")

    def deliver(self, puppet: Puppet, now: float) -> int:
        """Übergibt alles Vorgemerkte in der Reihenfolge des Eintreffens mit der Zeit `now`.

        Vorbedingung: `puppet` ist die Puppe des Panels, `now` die Zeit seines Bildes.
        Nachbedingung: Rückgabe ist die Zahl der übergebenen Einträge; die Schlange ist leer.
        Fehlerfall: Was die Puppe abweist, geht durch; der Eintrag, an dem sie scheiterte,
        ist aus der Schlange genommen, die folgenden bleiben stehen.
        """
        # ── Eingabe-Validierung ──
        if not isinstance(puppet, Puppet):
            raise TypeError(f"AvatarFeed.deliver: {type(puppet).__name__} ist keine Puppe")

        # ── Verarbeitung ──
        delivered = 0
        while self._items:
            item = self._items.popleft()
            if isinstance(item, Utterance):
                puppet_cue(puppet, item, now)
            else:
                event_type, fields = idle_call(item)
                puppet_event(puppet, event_type, now, **fields)
            delivered += 1

        # ── Ausgabe-Verifikation ──
        if self._items:
            raise RuntimeError(f"AvatarFeed.deliver: {len(self._items)} Einträge blieben stehen")
        return delivered
