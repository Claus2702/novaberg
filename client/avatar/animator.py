"""Animator: der sichtbare Zustand folgt dem Ziel stetig.

Jeder Kanal folgt seinem Ziel wie eine kritisch gedämpfte Feder, exakt gelöst je
Zeitschritt — das Ergebnis hängt nicht davon ab, in wie viele Schritte eine Spanne
zerlegt wird. Ein neues Ziel darf jederzeit kommen; Position und Geschwindigkeit
laufen stetig weiter.

Brauen und Augen übernehmen ein neues Ziel sofort, die Kanäle des Mundes erst
`MOUTH_DELAY_MS` später. Jeder Zielwechsel bekommt dafür einen eigenen Zeitpunkt:
Kommen Wechsel schneller als der Versatz, übernimmt der Mund sie nacheinander,
statt auf den letzten zu warten.

Das Modul liest keine Uhr. Jede Funktion bekommt die Zeit in Sekunden von außen,
von einer einzigen Uhr für Animation und Sprechen.
"""

import math
from dataclasses import dataclass, fields, replace

from avatar.face import FaceState

MOUTH_DELAY_MS = 150
DEFAULT_OMEGA = 5.0  # 1/s: rund 95 % des Wegs nach etwa 1 s

MOUTH_CHANNELS: frozenset[str] = frozenset({
    "mouth_curve", "mouth_open", "jaw", "mouth_width", "mouth_asym",
    "au10_left", "au10_right", "au12_left", "au12_right", "au15_left", "au15_right",
    "au16_left", "au16_right", "au20_left", "au20_right",
    "au17", "au18", "au22", "au23", "au24", "au28",
})

_CHANNELS: tuple[str, ...] = tuple(f.name for f in fields(FaceState))
_AT_REST = FaceState(**dict.fromkeys(_CHANNELS, 0.0))


@dataclass(frozen=True)
class PendingMouth:
    """Ein Ziel für den Mund, das ab `due_s` gilt."""

    due_s: float
    target: FaceState


@dataclass(frozen=True)
class AnimatorState:
    """Der Zustand des Animators zur Zeit `time_s`.

    `target` ist das Ziel, dem die Feder gerade folgt; die Mundkanäle darin wechseln
    erst, wenn ein Eintrag aus `pending` fällig wird. `velocity` trägt je Kanal die
    Geschwindigkeit in Einheiten des Kanals je Sekunde.
    """

    time_s: float
    current: FaceState
    velocity: FaceState
    target: FaceState
    pending: tuple[PendingMouth, ...]


def _check_time(time_s: float, earliest: float) -> None:
    """Wirft, wenn `time_s` keine endliche Zahl ist oder vor `earliest` liegt."""
    # ── Eingabe-Validierung ──
    is_number = isinstance(time_s, int | float) and not isinstance(time_s, bool)
    if not is_number or not math.isfinite(time_s):
        raise ValueError(f"Zeit {time_s!r} ist keine endliche Zahl")
    if time_s < earliest:
        raise ValueError(f"Zeit {time_s} liegt vor dem Stand des Animators ({earliest})")


def _check_omega(omega: float) -> None:
    """Wirft, wenn `omega` keine endliche positive Zahl ist."""
    # ── Eingabe-Validierung ──
    if isinstance(omega, bool) or not isinstance(omega, int | float):
        raise TypeError(f"omega {omega!r} ist keine Zahl")
    if not math.isfinite(omega) or omega <= 0:
        raise ValueError(f"omega {omega!r} muss endlich und positiv sein")


def _check_face(face: FaceState, label: str) -> None:
    """Wirft, wenn `face` kein `FaceState` mit endlichen Werten ist."""
    # ── Eingabe-Validierung ──
    if not isinstance(face, FaceState):
        raise TypeError(f"{label} ist kein FaceState: {type(face).__name__}")
    bad = [name for name in _CHANNELS if not math.isfinite(getattr(face, name))]
    if bad:
        raise ValueError(f"{label}: Kanäle nicht endlich: {bad}")


def start(face: FaceState, time_s: float) -> AnimatorState:
    """Ein Animator in Ruhe: sichtbar und Ziel sind `face`, keine Geschwindigkeit."""
    # ── Eingabe-Validierung ──
    _check_face(face, "Startzustand")
    _check_time(time_s, -math.inf)

    # ── Verarbeitung ──
    state = AnimatorState(float(time_s), face, _AT_REST, face, ())

    # ── Ausgabe-Verifikation ──
    if state.current is not state.target or state.pending:
        raise RuntimeError("start: Animator nicht in Ruhe")
    return state


def spring_step(
    current: FaceState, velocity: FaceState, target: FaceState, omega: float, dt: float
) -> tuple[FaceState, FaceState]:
    """Ein exakter Schritt der kritisch gedämpften Feder über `dt` Sekunden, je Kanal.

    Mit `d = x - ziel` und `e = exp(-omega * dt)`: `tmp = (v + omega * d) * dt`,
    `x_neu = ziel + (d + tmp) * e`, `v_neu = (v - omega * tmp) * e`.
    """
    # ── Eingabe-Validierung ──
    _check_omega(omega)
    if not math.isfinite(dt) or dt < 0:
        raise ValueError(f"spring_step: Zeitschritt {dt!r} muss endlich und >= 0 sein")

    # ── Verarbeitung ──
    decay = math.exp(-omega * dt)
    positions, velocities = {}, {}
    for name in _CHANNELS:
        goal = getattr(target, name)
        offset = getattr(current, name) - goal
        speed = getattr(velocity, name)
        tmp = (speed + omega * offset) * dt
        positions[name] = goal + (offset + tmp) * decay
        velocities[name] = (speed - omega * tmp) * decay
    result = FaceState(**positions), FaceState(**velocities)

    # ── Ausgabe-Verifikation ──
    _check_face(result[0], "spring_step: Position")
    _check_face(result[1], "spring_step: Geschwindigkeit")
    return result


def _with_mouth(target: FaceState, mouth: FaceState) -> FaceState:
    """`target` mit den Mundkanälen aus `mouth`."""
    # ── Eingabe-Validierung ──
    if not isinstance(target, FaceState) or not isinstance(mouth, FaceState):
        raise TypeError(
            f"_with_mouth: kein FaceState: {type(target).__name__}, {type(mouth).__name__}"
        )

    # ── Verarbeitung ──
    return replace(target, **{name: getattr(mouth, name) for name in MOUTH_CHANNELS})


def advance(state: AnimatorState, time_s: float, omega: float = DEFAULT_OMEGA) -> AnimatorState:
    """Der Zustand zur Zeit `time_s`.

    Ein Mundziel, das innerhalb der Spanne fällig wird, gilt genau ab seinem
    Zeitpunkt: Die Spanne wird dort geteilt. Damit ist auch der Mundversatz
    unabhängig von der Bildrate.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(state, AnimatorState):
        raise TypeError(f"advance: kein AnimatorState: {type(state).__name__}")
    _check_time(time_s, state.time_s)
    _check_omega(omega)

    # ── Verarbeitung ──
    now, current, velocity, target = state.time_s, state.current, state.velocity, state.target
    pending = list(state.pending)
    while pending and pending[0].due_s <= time_s:
        due = pending.pop(0)
        if due.due_s > now:
            current, velocity = spring_step(current, velocity, target, omega, due.due_s - now)
            now = due.due_s
        target = _with_mouth(target, due.target)
    # Eine Spanne der Länge null rechnet nicht: `ziel + (x - ziel)` träfe `x` nicht
    # immer bitgenau, und ein Zielwechsel soll den sichtbaren Zustand nicht berühren.
    if time_s > now:
        current, velocity = spring_step(current, velocity, target, omega, time_s - now)
    result = AnimatorState(float(time_s), current, velocity, target, tuple(pending))

    # ── Ausgabe-Verifikation ──
    if any(entry.due_s <= time_s for entry in result.pending):
        raise RuntimeError(f"advance: fälliges Mundziel bei {time_s} nicht übernommen")
    return result


def set_target(
    state: AnimatorState, target: FaceState, time_s: float, omega: float = DEFAULT_OMEGA
) -> AnimatorState:
    """Setzt zur Zeit `time_s` ein neues Ziel.

    Der Zustand wird zuerst bis `time_s` fortgeschrieben; von dort aus — vom
    sichtbaren Zustand, nicht vom alten Ziel — folgen Brauen und Augen sofort, die
    Mundkanäle ab `time_s` plus `MOUTH_DELAY_MS`.
    """
    # ── Eingabe-Validierung ──
    _check_face(target, "set_target: Ziel")

    # ── Verarbeitung ──
    moved = advance(state, time_s, omega)
    due_s = moved.time_s + MOUTH_DELAY_MS / 1000
    result = replace(
        moved,
        # Brauen und Augen aus dem neuen Ziel, der Mund behält sein bisheriges.
        target=_with_mouth(target, moved.target),
        pending=(*moved.pending, PendingMouth(due_s, target)),
    )

    # ── Ausgabe-Verifikation ──
    if result.current != moved.current or result.velocity != moved.velocity:
        raise RuntimeError("set_target: Zielwechsel hat den sichtbaren Zustand verändert")
    return result
