"""Arbeitszustand: was gerade läuft, und der Text der Statuszeile daraus.

Das Modul importiert kein GTK und liest keine Uhr: Die Zeit kommt als Argument, jede
Funktion gibt einen neuen Zustand zurück. Der Zustand hält

* die laufenden Aufträge Pixies, höchstens einen je Spur;
* ob der CharacterGraph für einen Turn denkt — solange eine offene Nachricht ohne Antwort
  bleibt — und ob er für einen Impuls denkt.

Ein Turn oder Impuls, der `WATCHDOG_SECONDS` ohne Antwort oder Ende denkt, gilt als
beendet. Die Aufträge Pixies haben keinen Wächter: Der Server sendet `ende` auch nach
einem Fehler; geht ein `ende` verloren, bleibt der Auftrag stehen.
"""

import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace

from ui.work_events import (
    PHASE_BEGIN,
    PHASE_END,
    TRACKS,
    WORK_EVENT_TYPES,
    ImpulseThinking,
    PixieWork,
    TurnFailure,
    TurnStarted,
    WorkEvent,
)

logger = logging.getLogger(__name__)

WATCHDOG_SECONDS = 600.0
IDLE_TEXT = "idle"
THINKING_TEXT = "Charakter-Berechnung"

# Die geschlossene Menge der Aufgaben des Routers, lesbar.
JOB_TEXTS = {
    "recherche": "Recherche",
    "vertiefen": "Vertiefung",
    "nachfragen": "Nachfrage",
    "wiedervorlage": "Wiedervorlage",
    "wissen_rueckweg": "Wissensablage",
    "wissen_verweis": "Wissensverweis",
    "lzg_promotion": "Gedächtnis-Promotion",
    "delegation": "Delegation",
}


@dataclass(frozen=True)
class RunningJob:
    """Ein Auftrag Pixies, der in einer Spur läuft."""

    track: str
    job_kind: str
    topic: str | None = None


@dataclass(frozen=True)
class WorkState:
    """Was läuft: Turn (seit wann, welche Nachrichten offen), Impuls, Aufträge Pixies.

    `turn_since` und `impulse_since` sind die Zeit des Beginns, None heißt: denkt nicht.
    Offene Nachrichten gibt es nur, solange ein Turn denkt; die Aufträge sind nach Spur
    geordnet, höchstens einer je Spur.
    """

    turn_since: float | None = None
    open_ids: frozenset[str] = frozenset()
    impulse_since: float | None = None
    jobs: tuple[RunningJob, ...] = ()

    def __post_init__(self) -> None:
        """Weist einen Zustand ab, der in sich nicht stimmt."""
        # ── Eingabe-Validierung ──
        if self.open_ids and self.turn_since is None:
            raise ValueError("WorkState: offene Nachrichten ohne denkenden Turn")
        tracks = [job.track for job in self.jobs]
        if len(set(tracks)) != len(tracks) or not set(tracks) <= set(TRACKS):
            raise ValueError(f"WorkState: Spuren {tracks} sind doppelt oder unbekannt")

    @property
    def thinking(self) -> bool:
        """Wahr, wenn der CharacterGraph für einen Turn oder einen Impuls denkt."""
        return self.turn_since is not None or self.impulse_since is not None


@dataclass(frozen=True)
class StatusText:
    """Der Text der Statuszeile und der Tooltip dazu (leer, wenn es nichts zu sagen gibt)."""

    text: str
    tooltip: str


def _check_inputs(state: WorkState, now: float | None = None) -> None:
    """Weist einen falschen Zustand oder eine falsche Zeit mit TypeError ab."""
    # ── Eingabe-Validierung ──
    if not isinstance(state, WorkState):
        raise TypeError(f"state ist {type(state).__name__}, kein WorkState")
    if now is None:
        return
    if isinstance(now, bool) or not isinstance(now, int | float):
        raise TypeError(f"now ist {type(now).__name__}, keine Zahl")

    # Keine Ausgabe-Verifikation: Die Prüfung oben ist die Aussage.


def _advance_impulse(state: WorkState, event: ImpulseThinking, now: float) -> WorkState:
    """Impuls `beginn` setzt den Beginn, `ende` löscht ihn; eine andere Phase ist ValueError."""
    # ── Eingabe-Validierung ──
    if event.phase not in (PHASE_BEGIN, PHASE_END):
        raise ValueError(f"impuls_denkt: Phase {event.phase!r} ist unbekannt")

    # ── Verarbeitung ──
    since = now if event.phase == PHASE_BEGIN else None

    # Keine Ausgabe-Verifikation: `WorkState` prüft sich selbst.
    return replace(state, impulse_since=since)


def _advance_job(state: WorkState, event: PixieWork) -> WorkState:
    """Ein Auftrag beginnt in seiner Spur oder endet dort; eine andere Phase ist ValueError."""
    # ── Eingabe-Validierung ──
    if event.phase not in (PHASE_BEGIN, PHASE_END):
        raise ValueError(f"pixie_auftrag: Phase {event.phase!r} ist unbekannt")

    # ── Verarbeitung ──
    running = [job for job in state.jobs if job.track == event.track]
    others = [job for job in state.jobs if job.track != event.track]
    if event.phase == PHASE_BEGIN:
        if running:
            logger.warning(
                f"Arbeitszustand: Spur {event.track} beginnt '{event.job_kind}', "
                f"'{running[0].job_kind}' lief noch — ein `ende` ging verloren"
            )
        others.append(RunningJob(event.track, event.job_kind, event.topic))
    elif not running:
        logger.warning(f"Arbeitszustand: Spur {event.track} endet ohne laufenden Auftrag")
    jobs = tuple(sorted(others, key=lambda job: TRACKS.index(job.track)))

    # Keine Ausgabe-Verifikation: `WorkState` prüft Spuren und Ordnung selbst.
    return replace(state, jobs=jobs)


def advance(state: WorkState, event: WorkEvent, now: float) -> WorkState:
    """Schreibt den Zustand um ein Ereignis der Arbeitszyklen fort.

    Vorbedingung: `event` ist ein Ereignis aus `ui.work_events`, `now` die Zeit in Sekunden.
    Nachbedingung: Turn beginnt → der Turn denkt ab `now`; Turn gescheitert → er denkt
    nicht mehr, nichts ist offen; Impuls und Pixie wie in den Hilfen. Der Zustand
    des Arguments bleibt unverändert.
    Fehlerfall: TypeError bei einem anderen Typ oder einer falschen Zeit.
    """
    # ── Eingabe-Validierung ──
    _check_inputs(state, now)
    if not isinstance(event, WORK_EVENT_TYPES):
        raise TypeError(f"advance: {type(event).__name__} ist kein Arbeitsereignis")

    # ── Verarbeitung ──
    if isinstance(event, TurnStarted):
        result = replace(state, turn_since=now)
    elif isinstance(event, TurnFailure):
        result = replace(state, turn_since=None, open_ids=frozenset())
    elif isinstance(event, ImpulseThinking):
        result = _advance_impulse(state, event, now)
    else:
        result = _advance_job(state, event)

    # Keine Ausgabe-Verifikation: `WorkState` prüft sich bei der Bildung selbst.
    return result


def message_opened(state: WorkState, message_id: str) -> WorkState:
    """Nimmt eine Kennung als offen auf, die der Server für eine gesendete Nachricht nannte.

    Vorbedingung: `message_id` ist ein nichtleerer Text.
    Nachbedingung: Denkt kein Turn (er endete schon, etwa durch Scheitern), bleibt der
    Zustand unverändert und eine Info-Zeile sagt es; sonst ist die Kennung offen.
    Fehlerfall: TypeError bei einem falschen Zustand, ValueError bei einer leeren Kennung.
    """
    # ── Eingabe-Validierung ──
    _check_inputs(state)
    if not isinstance(message_id, str) or not message_id:
        raise ValueError("message_opened: Kennung fehlt oder ist kein Text")

    # ── Verarbeitung ──
    if state.turn_since is None:
        logger.info("Arbeitszustand: Kennung bestätigt, aber kein Turn denkt — nicht aufgenommen")
        return state
    result = replace(state, open_ids=state.open_ids | {message_id})

    # ── Ausgabe-Verifikation ──
    if message_id not in result.open_ids:
        raise RuntimeError("message_opened: Kennung nicht aufgenommen")
    return result


def named_ids(meta: Mapping) -> frozenset[str]:
    """Liest `nachrichten_ids` aus den Daten einer Antwort.

    Nachbedingung: die nichtleeren Texte der Liste; fehlt das Feld oder ist es keine Liste,
    eine leere Menge und eine Warning-Zeile — der Server nannte dann keine Kennung.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(meta, Mapping):
        raise TypeError(f"named_ids: meta ist {type(meta).__name__}, kein Mapping")

    # ── Verarbeitung ──
    raw = meta.get("nachrichten_ids")
    if not isinstance(raw, list | tuple):
        logger.warning("Arbeitszustand: Antwort ohne Liste nachrichten_ids — keine Kennung genannt")
        return frozenset()

    # Keine Ausgabe-Verifikation: Die Auswahl der Texte ist die Aussage.
    return frozenset(item for item in raw if isinstance(item, str) and item)


def turn_answered(state: WorkState, ids: Iterable[str]) -> WorkState:
    """Nimmt die Kennungen einer Antwort aus den offenen; ist keine mehr offen, endet der Turn.

    Vorbedingung: `ids` sind die Kennungen aus `named_ids`.
    Nachbedingung: Denkt kein Turn, bleibt der Zustand gleich. Sonst endet der Turn genau dann,
    wenn nach dem Abzug keine Kennung offen ist; eine Antwort, die nur Fremdes nennt, lässt
    offene Nachrichten offen.
    Fehlerfall: TypeError bei einem falschen Zustand oder bei Kennungen, die kein Text sind.
    """
    # ── Eingabe-Validierung ──
    _check_inputs(state)
    if isinstance(ids, str):
        raise TypeError("turn_answered: ids ist ein Text, keine Sammlung von Kennungen")
    named = frozenset(ids)
    if not all(isinstance(item, str) for item in named):
        raise TypeError("turn_answered: Kennungen müssen Texte sein")

    # ── Verarbeitung ──
    if state.turn_since is None:
        return state
    remaining = state.open_ids - named
    if remaining:
        return replace(state, open_ids=remaining)

    # Keine Ausgabe-Verifikation: `WorkState` prüft sich bei der Bildung selbst.
    return replace(state, turn_since=None, open_ids=frozenset())


def impulse_answered(state: WorkState) -> WorkState:
    """Beendet das Denken eines Impulses, weil Nova aus ihm gesprochen hat; ein Turn bleibt."""
    # ── Eingabe-Validierung ──
    _check_inputs(state)

    # Keine Ausgabe-Verifikation: `WorkState` prüft sich bei der Bildung selbst.
    return replace(state, impulse_since=None)


def expire(state: WorkState, now: float) -> WorkState:
    """Beendet einen Turn oder Impuls, der `WATCHDOG_SECONDS` ohne Antwort oder Ende denkt.

    Vorbedingung: `now` ist die Zeit in Sekunden auf der Uhr, die auch der Zustand benutzte.
    Nachbedingung: Bei genau `WATCHDOG_SECONDS` gilt er als beendet, bei weniger nicht. Jedes
    Ende schreibt eine Warning-Zeile. Aufträge Pixies bleiben unberührt.
    """
    # ── Eingabe-Validierung ──
    _check_inputs(state, now)

    # ── Verarbeitung ──
    result = state
    if state.turn_since is not None and now - state.turn_since >= WATCHDOG_SECONDS:
        logger.warning(
            f"Arbeitszustand: Turn denkt seit {now - state.turn_since:.0f} s ohne Antwort — "
            f"gilt als beendet ({len(state.open_ids)} Nachricht(en) offen)"
        )
        result = replace(result, turn_since=None, open_ids=frozenset())
    if state.impulse_since is not None and now - state.impulse_since >= WATCHDOG_SECONDS:
        logger.warning(
            f"Arbeitszustand: Impuls denkt seit {now - state.impulse_since:.0f} s ohne Ende — "
            "gilt als beendet"
        )
        result = replace(result, impulse_since=None)

    # Keine Ausgabe-Verifikation: `WorkState` prüft sich bei der Bildung selbst.
    return result


def opening_event(state: WorkState) -> WorkEvent | None:
    """Das Ereignis, das ein Panel beim Öffnen bekommt, damit es im Nachdenken beginnt.

    Nachbedingung: `TurnStarted`, wenn ein Turn denkt, sonst `ImpulseThinking` `beginn`, wenn
    ein Impuls denkt, sonst None. Laufende Aufträge Pixies liefert niemand nach.
    """
    # ── Eingabe-Validierung ──
    _check_inputs(state)

    # Keine Ausgabe-Verifikation: Die Wahl ist die Aussage.
    if state.turn_since is not None:
        return TurnStarted()
    if state.impulse_since is not None:
        return ImpulseThinking(phase=PHASE_BEGIN)
    return None


def job_text(job_kind: str) -> str:
    """Die lesbare Art eines Auftrags; eine Art ohne Text ist ValueError statt des Schlüssels."""
    # ── Eingabe-Validierung ──
    if job_kind not in JOB_TEXTS:
        raise ValueError(f"Art {job_kind!r} hat keinen Text (bekannt: {', '.join(JOB_TEXTS)})")

    # Keine Ausgabe-Verifikation: Die Tabelle ist die Aussage.
    return JOB_TEXTS[job_kind]


def _thinking_detail(state: WorkState) -> list[str]:
    """Die Tooltipzeilen zum Denken des CharacterGraphs, je Anlass eine."""
    # ── Eingabe-Validierung ──
    _check_inputs(state)

    # Keine Ausgabe-Verifikation: Die Zeilen sind die Aussage.
    lines = []
    if state.turn_since is not None:
        lines.append(f"Nova: {THINKING_TEXT} (Turn, {len(state.open_ids)} offen)")
    if state.impulse_since is not None:
        lines.append(f"Nova: {THINKING_TEXT} (Impuls)")
    return lines


def status_text(state: WorkState) -> StatusText:
    """Bildet Text und Tooltip der Statuszeile aus dem Zustand.

    Nachbedingung: `IDLE_TEXT` steht genau dann, wenn nichts läuft. Sonst steht für den
    CharacterGraph „Nova: Charakter-Berechnung“ und für Pixie „Pixie:“ mit der Art jeder
    laufenden Spur; das Thema steht nur im Tooltip.
    Fehlerfall: TypeError bei einem falschen Zustand, ValueError bei einer Art ohne Text.
    """
    # ── Eingabe-Validierung ──
    _check_inputs(state)

    # ── Verarbeitung ──
    parts = []
    details = _thinking_detail(state)
    if state.thinking:
        parts.append(f"Nova: {THINKING_TEXT}")
    if state.jobs:
        kinds = ", ".join(job_text(job.job_kind) for job in state.jobs)
        parts.append(f"Pixie: {kinds}")
    for job in state.jobs:
        topic = f" — {job.topic}" if job.topic else ""
        details.append(f"Pixie ({job.track}): {job_text(job.job_kind)}{topic}")

    # ── Ausgabe-Verifikation ──
    running = state.thinking or bool(state.jobs)
    if running != bool(parts):
        raise RuntimeError("status_text: Text und Zustand widersprechen sich")
    return StatusText(" · ".join(parts) if parts else IDLE_TEXT, "\n".join(details))
