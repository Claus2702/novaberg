"""Zeugen für die Leerlauf-Logik des Avatars: dieselbe Planung wie der Referenzgenerator.

Die Verläufe unter `avatar_reference/idle.json` sind vom Referenzgenerator erzeugt
(elf Fälle × drei Startwerte) und werden nicht von Hand geändert. Eine Abweichung
davon wäre im Bild still: Das Gesicht sähe lebendig aus und plante doch anders.

Charakterisierung: Die Eingänge eines Laufs werden auf ganze ms gerundet wie im
Generator, nach Zeit stabil sortiert und eingespielt; Pixies Aufträge mit t ≤ 0
laufen schon beim Start. Geschritten wird im 20-ms-Raster bis `sim_ms`, mit dem
Blick (0, 0) — der Generator lässt in der Simulation keine Feder laufen, sein
Gesicht steht beim Start neutral.

Die Dauer der Wiedergabe einer Antwort steht nicht in den Eingängen (dort steht
der Text). Sie folgt aus dem Verlauf: `wiedergabe_endet` minus Beginn des
Zustands Antwort; eine abgelöste Antwort meldet kein Ende, dann aus ihrer Grenze
`bis` = Beginn + Dauer + 400 ms. Eine Antwort, die nie gesprochen wird (im
Einatmen ersetzt, von einem Turn verworfen), bekommt eine Platzhalterdauer — sie
wird nie gelesen.

Toleranzen: Zeiten und Dauern 1e-6 ms, Blickpunkte 1e-9, Ziele, Kopfziele, Lid, ω
und k 1e-3 (die Referenz rundet sie auf vier Stellen). Die Kopffeder der Proben
(`kopf`, `kopf0`) und `kopf_ende` vergleicht dieser Zeuge nicht: Die Feder führt
nicht die Logik, sondern die Puppe. Die kleinste fachliche Abweichung —
eine Ziehung mehr, eine andere Form — verschiebt Zeiten um Millisekunden.
"""

import bisect
import json
import math
import unittest
from collections.abc import Callable, Iterator
from dataclasses import replace
from pathlib import Path
from typing import NamedTuple

from avatar import idle_catalog as catalog
from avatar.face import PROTOTYPE_KEYS
from avatar.idle import (
    AnswerArrives,
    IdleEvent,
    IdleFrame,
    IdleLogic,
    IdleTrace,
    ImpulseThinks,
    Mood,
    Mulberry32,
    PixieJob,
    TracedEvent,
    TracedForm,
    TracedState,
    TurnBegins,
    TurnFailed,
    blink_rate,
    head_seed,
)
from avatar.idle_catalog import BASE_WEIGHTS, DRAWABLE, FORMS, GROUP_FACTORS, IdleState

REFERENCE_PATH = Path(__file__).parent / "avatar_reference" / "idle.json"
RUN_COUNT = 33  # elf Fälle × drei Startwerte
STEP_MS = 20
TIME_TOLERANCE = 1e-6
GAZE_TOLERANCE = 1e-9
TARGET_TOLERANCE = 1e-3
PLAYBACK_TAIL_MS = 400.0
UNSPOKEN_PLAYBACK_MS = 1000.0
_KEY_TO_FIELD = {key: name for name, key in PROTOTYPE_KEYS.items()}
YAW_KEY = "yaw"  # das Ziel der Kopfdrehung: kein Feld des Gesichts, sondern `IdleFrame.head_yaw`
_Span = tuple[TracedState, TracedState | None, list[TracedForm]]


def _load_reference() -> dict:
    """Die Verläufe des Referenzgenerators."""
    with REFERENCE_PATH.open(encoding="utf-8") as handle:
        reference = json.load(handle)
    if len(reference["laeufe"]) != RUN_COUNT:
        raise AssertionError(f"idle.json: {len(reference['laeufe'])} Läufe statt {RUN_COUNT}")
    return reference


class _Step(NamedTuple):
    """Was die Prüfpunkte aus einem Schritt brauchen — klein, damit alle Läufe Platz haben."""

    t: int
    state: IdleState
    form_id: str
    targets: tuple[float, ...]  # in der Reihenfolge von STEP_KEYS
    face_omega: float
    head_yaw: float
    plan: int  # Prüfsumme des Bilds ohne yaw: für den Zwilling ohne Drehung (Y5)


STEP_KEYS = ("mw", "mo", "jaw", "eo", "gy", "ps", "bli", "bri", "blo", "bro", "mc")
_Run = tuple[IdleTrace, list[tuple[int, IdleFrame]], list[_Step]]
REFERENCE = _load_reference()
_SIMULATIONS: dict[int, _Run] = {}


def _round_ms(seconds: float) -> int:
    """Eine Zeit in s auf ganze ms wie `Math.round(t * 1000)` im Generator."""
    if not math.isfinite(seconds):
        raise AssertionError(f"Eingang mit Zeit {seconds!r}")
    return math.floor(seconds * 1000 + 0.5)


def _first_step(t_ms: float) -> int:
    """Der erste Schritt, der nicht vor t liegt — dort wird behandelt, was bei t eintrifft."""
    if not math.isfinite(t_ms):
        raise AssertionError(f"Zeit {t_ms!r}")
    return max(STEP_MS, math.ceil(t_ms / STEP_MS) * STEP_MS)


def _label(index: int) -> str:
    """Fall und Startwert eines Laufs, für Meldungen."""
    run = REFERENCE["laeufe"][index]
    if "fall" not in run or "seed" not in run:
        raise AssertionError(f"Lauf {index} ohne Fall oder Startwert")
    return f"Fall {run['fall']}, Startwert {run['seed']}"


def _sorted_inputs(run: dict) -> list[tuple[int, dict]]:
    """Die Eingänge auf ganze ms gerundet, stabil nach Zeit sortiert."""
    inputs = sorted(((_round_ms(e["t"]), e) for e in run["eingang"]), key=lambda pair: pair[0])
    if len(inputs) != len(run["eingang"]):
        raise AssertionError("Eingänge verloren")
    return inputs


def _playbacks(run: dict, inputs: list[tuple[int, dict]]) -> dict[int, float]:
    """Die Dauer der Wiedergabe je gesprochener Antwort, nach ihrer Stelle in `inputs`.

    Je Zustand Antwort bei T gehört die letzte `antwort` mit Zeit ≤ T dazu. Die Dauer ist
    `wiedergabe_endet` minus T, wenn die Wiedergabe in diesem Zustand endet; nur eine
    abgelöste Antwort meldet kein Ende, dann gilt `bis` − T − Nachlauf.
    """
    ends = [e["t"] for e in run["ereignisse"] if e["typ"] == "wiedergabe_endet"]
    states = run["zustaende"]
    playbacks: dict[int, float] = {}
    for index, state in enumerate(states):
        if state["z"] != IdleState.ANSWER.value:
            continue
        start = state["t"]
        until = states[index + 1]["t"] if index + 1 < len(states) else math.inf
        position = max(i for i, (t, e) in enumerate(inputs)
                       if e["typ"] == "antwort" and t <= start)
        reported = [t for t in ends if start <= t < until]
        if len(reported) > 1:
            raise AssertionError(f"Antwort {position} mit {len(reported)} Enden der Wiedergabe")
        playback = reported[0] - start if reported else state["bis"] - start - PLAYBACK_TAIL_MS
        if abs(playbacks.get(position, playback) - playback) > TIME_TOLERANCE:
            raise AssertionError(f"Antwort {position} mit zwei Dauern der Wiedergabe")
        playbacks[position] = playback
    return playbacks


def _event(at_ms: int, entry: dict, playback_ms: float) -> IdleEvent:
    """Ein Eingang der Referenz als Ereignis des Clients."""
    kind = entry["typ"]
    if kind == "turn_beginnt":
        return TurnBegins(float(at_ms))
    if kind == "turn_gescheitert":
        return TurnFailed(float(at_ms))
    if kind == "impuls_denkt":
        return ImpulseThinks(float(at_ms), entry["phase"])
    if kind == "antwort":
        return AnswerArrives(float(at_ms), entry["emotion"], entry["arousal"], playback_ms)
    if kind == "pixie_auftrag":
        return PixieJob(float(at_ms), entry["phase"], entry["spur"], entry.get("art", ""),
                        entry.get("emotion"), entry.get("arousal"))
    raise AssertionError(f"Eingang unbekannten Typs {kind!r}")


def _replay(index: int, trace: IdleTrace, head_turn: bool) -> Iterator[tuple[int, IdleFrame]]:
    """Spielt den Lauf `index` im Client ein und liefert jedes Bild im 20-ms-Raster."""
    run = REFERENCE["laeufe"][index]
    inputs = _sorted_inputs(run)
    playbacks = _playbacks(run, inputs)
    events = [_event(t, e, playbacks.get(i, UNSPOKEN_PLAYBACK_MS))
              for i, (t, e) in enumerate(inputs)]
    running = 0
    while running < len(events) and isinstance(events[running], PixieJob) and (
            events[running].at_ms <= 0):
        running += 1
    nova = Mood(run["nova_beginn"]["emotion"], run["nova_beginn"]["arousal"])
    logic = IdleLogic(run["seed"], nova, events[:running], trace, head_turn=head_turn)
    for event in events[running:]:
        logic.post(event)
    for t in range(STEP_MS, run["sim_ms"] + 1, STEP_MS):
        yield t, logic.step(float(t), 0.0, 0.0)


def _simulation(index: int) -> _Run:
    """Der Lauf `index` im Client: Verlauf, Bilder an den Proben, alle Schritte.

    Jeder Lauf wird einmal gerechnet.
    """
    if index in _SIMULATIONS:
        return _SIMULATIONS[index]
    trace = IdleTrace()
    probe_ms = REFERENCE["probe_ms"]
    probes: list[tuple[int, IdleFrame]] = []
    steps: list[_Step] = []
    for t, frame in _replay(index, trace, True):
        if t % probe_ms == 0:
            probes.append((t, frame))
        values = tuple(getattr(frame.targets, _KEY_TO_FIELD[k]) for k in STEP_KEYS)
        steps.append(_Step(t, frame.state, frame.form_id, values, frame.face_omega,
                           frame.head_yaw, hash(replace(frame, head_yaw=0.0))))
    _SIMULATIONS[index] = (trace, probes, steps)
    return _SIMULATIONS[index]


def _all_traces() -> Iterator[tuple[int, IdleTrace]]:
    """Die Verläufe des Clients für alle Läufe der Referenz."""
    count = len(REFERENCE["laeufe"])
    if count == 0:
        raise AssertionError("keine Läufe")
    for index in range(count):
        yield index, _simulation(index)[0]


def _same(expected: object, actual: object, tolerance: float | None) -> bool:
    """Gleichheit eines Felds: exakt ohne Toleranz, sonst im Betrag; Folgen je Element."""
    if tolerance is not None and tolerance < 0:
        raise AssertionError(f"Toleranz {tolerance}")
    if isinstance(expected, tuple | list):
        return (isinstance(actual, tuple | list) and len(actual) == len(expected)
                and all(_same(e, a, tolerance) for e, a in zip(expected, actual, strict=True)))
    if tolerance is None or expected is None or actual is None:
        return expected == actual
    return abs(float(expected) - float(actual)) <= tolerance


def _first_mismatch(name: str, expected: list[tuple], actual: list[tuple],
                    tolerances: tuple[float | None, ...]) -> str | None:
    """Das erste abweichende Element zweier Folgen von Einträgen, oder None."""
    for i, (want, got) in enumerate(zip(expected, actual, strict=False)):
        if len(want) != len(tolerances) or len(got) != len(tolerances):
            raise AssertionError(f"{name}[{i}]: Einträge passen nicht zu den Toleranzen")
        if not all(_same(w, g, tol) for w, g, tol in zip(want, got, tolerances, strict=True)):
            return f"{name}[{i}]: Referenz {want}, Client {got}"
    if len(expected) != len(actual):
        return f"{name}: {len(expected)} Einträge in der Referenz, {len(actual)} im Client"
    return None


def _channel(frame: IdleFrame, key: str) -> float:
    """Das Ziel eines Kanals der Referenz im Bild: yaw aus dem Kopf, sonst aus dem Gesicht."""
    if key == YAW_KEY:
        return frame.head_yaw
    return getattr(frame.targets, _KEY_TO_FIELD[key])


def _run_mismatch(index: int) -> str | None:
    """Das erste abweichende Element des Laufs `index` über alle Teile des Verlaufs."""
    run = REFERENCE["laeufe"][index]
    trace, probes, _ = _simulation(index)
    keys = REFERENCE["kanaele"]
    if set(keys) != set(_KEY_TO_FIELD) | {YAW_KEY}:
        raise AssertionError("die Kanäle der Referenz sind nicht die des Prototyps und yaw")
    t, g, v = TIME_TOLERANCE, GAZE_TOLERANCE, TARGET_TOLERANCE
    parts = (
        ("zustaende", [(s["t"], s["z"], s["bis"]) for s in run["zustaende"]],
         [(s.at_ms, s.state.value, s.until_ms) for s in trace.states], (t, None, t)),
        ("formen", [(f["t"], f["z"], f["id"], f["t0"], f["d"], f["x"], f["y"], f["mo"])
                    for f in run["formen"]],
         [(f.at_ms, f.state.value, f.form_id, f.t0, f.duration, f.gaze_x, f.gaze_y,
           f.mouth_open_max) for f in trace.forms], (t, None, None, t, t, g, g, v)),
        ("lid", [(b["t"], b["z"], b["art"], b["gekoppelt"], b["beginn"], b["zu"], b["halt"],
                  b["auf"]) for b in run["lid"]],
         [(b.at_ms, b.state.value, b.kind, b.coupled, b.begin_ms, b.close_ms, b.hold_ms,
           b.open_ms) for b in trace.blinks],
         (t, None, None, None, t, t, t, t)),
        ("ereignisse", [(e["t"], e["typ"], e["behandelt"]) for e in run["ereignisse"]],
         [(e.at_ms, e.event_type, e.handled_ms) for e in trace.events], (t, None, t)),
        ("kopf", [(h["t"], h["ziel"], h["art"], h["x"], h["blick"]) for h in run["kopf"]],
         [(h.at_ms, h.target, h.kind, h.gaze_x, h.gaze_change_ms) for h in trace.heads],
         (t, v, None, g, t)),
        ("proben", [(p["t"], p["z"], p["id"], p["ziele"], p["lid"], p["wGesicht"], p["k"],
                     p["akt"]) for p in run["proben"]],
         [(at, f.state.value, f.form_id, [_channel(f, k) for k in keys],
           f.lid_open, f.face_omega, f.amplitude, f.activity) for at, f in probes],
         (None, None, None, v, v, v, v, g)),
    )
    for name, expected, actual, tolerances in parts:
        mismatch = _first_mismatch(name, expected, actual, tolerances)
        if mismatch is not None:
            return mismatch
    return None


def _averted(form: TracedForm) -> bool:
    """Abgewandt wie im Generator: |x| > 0,12 oder |y| > 0,15."""
    if not (math.isfinite(form.gaze_x) and math.isfinite(form.gaze_y)):
        raise AssertionError(f"Blick von {form.form_id} nicht endlich")
    return abs(form.gaze_x) > 0.12 or abs(form.gaze_y) > 0.15


def _spans(trace: IdleTrace, state: IdleState) -> Iterator[_Span]:
    """Je Zustand `state`: der Eintrag, der nächste Zustand und die Formen dazwischen."""
    if not isinstance(state, IdleState):
        raise TypeError(f"kein Zustand: {state!r}")
    for i, entry in enumerate(trace.states):
        if entry.state is not state:
            continue
        following = trace.states[i + 1] if i + 1 < len(trace.states) else None
        until = following.at_ms if following is not None else math.inf
        forms = [f for f in trace.forms if f.state is state and entry.at_ms <= f.at_ms < until]
        yield entry, following, forms


def _turn_draws(seed: int, gaze: tuple[float, float]) -> tuple[int, TracedForm]:
    """Ein Turn im ersten Schritt mit dem Blick `gaze`: Zahl der Ziehungen, erste Form."""
    if not all(math.isfinite(x) for x in gaze):
        raise AssertionError(f"Blick {gaze}")
    trace = IdleTrace()
    logic = IdleLogic(seed, trace=trace)
    logic.post(TurnBegins(20.0))
    logic.step(20.0, *gaze)
    first = next(f for f in trace.forms if f.state is IdleState.THINKING)
    return logic._rng.draws, first


def _answer_frames(emotion: str) -> list[IdleFrame]:
    """Ein Turn, eine Antwort mit `emotion` nach 1 s; die Bilder der ersten 6 s."""
    if not emotion:
        raise AssertionError("leere Emotion")
    logic = IdleLogic(5)
    logic.post(TurnBegins(20.0))
    logic.post(AnswerArrives(1000.0, emotion, 0.6, 2000.0))
    return [logic.step(float(t), 0.0, 0.0) for t in range(STEP_MS, 6001, STEP_MS)]


def _value(step: _Step, key: str) -> float:
    """Ein Ziel aus der Schrittspur."""
    if key not in STEP_KEYS:
        raise AssertionError(f"{key} steht nicht in der Schrittspur")
    return step.targets[STEP_KEYS.index(key)]


def _all_runs() -> Iterator[tuple[int, _Run]]:
    """Alle Läufe der Referenz im Client: Verlauf, Proben, Schritte."""
    for index in range(len(REFERENCE["laeufe"])):
        yield index, _simulation(index)


def _steps_in(steps: list[_Step], entry: TracedState,
              following: TracedState | None) -> list[_Step]:
    """Die Schritte eines Zustands: ab seinem Beginn bis zum nächsten."""
    until = following.at_ms if following is not None else math.inf
    return [s for s in steps if entry.at_ms <= s.t < until]


def _answer_arousal(index: int, answer_at: float) -> float:
    """Novas Arousal der Antwort, die ab `answer_at` gesprochen wird: der letzten davor."""
    arrived = [e for t, e in _sorted_inputs(REFERENCE["laeufe"][index])
               if e["typ"] == "antwort" and t <= answer_at]
    if not arrived:
        raise AssertionError(f"{_label(index)}: keine Antwort vor {answer_at} ms")
    return float(arrived[-1]["arousal"])


def _forms_with_fixed_basis(trace: IdleTrace) -> set[int]:
    """Die Formen, in deren Innerem kein Ereignis behandelt wird und kein Zustand wechselt.

    Ein Auftrag Pixies, eine Antwort oder ein Zustandswechsel ändert die Basis;
    G3 setzt eine feste Basis voraus.
    """
    breaks = sorted([e.handled_ms for e in trace.events] + [s.at_ms for s in trace.states])
    ends = [f.at_ms for f in trace.forms[1:]] + [math.inf]
    fixed = set()
    for index, (form, end) in enumerate(zip(trace.forms, ends, strict=True)):
        first = bisect.bisect_right(breaks, form.at_ms)
        if first == len(breaks) or breaks[first] >= end:
            fixed.add(index)
    return fixed


def _still_window(values: list[tuple[int, float]], span_ms: float, limit: float) -> int | None:
    """Der Beginn des ersten Fensters von `span_ms`, in dem der Wert um ≤ `limit` schwankt."""
    end = 0
    for start in range(len(values)):
        while end < len(values) and values[end][0] - values[start][0] < span_ms:
            end += 1
        if end == len(values):
            return None
        window = [v for _, v in values[start:end + 1]]
        if max(window) - min(window) <= limit:
            return values[start][0]
    return None


def _longest_pause_median_ms(rate: float, span_ms: float) -> float:
    """Median der längsten Pause in `span_ms`, alle Lidschläge aus dem Poisson-Prozess.

    Abstand wie in der Logik: Sperrzeit + Gamma(3) mit dem Mittel 60000/rate − Sperrzeit.
    Bei n = span·rate/60000 unabhängigen Abständen ist der Median des längsten das
    Quantil 0,5^(1/n) eines Abstands. Gamma(3) mit Skala θ: P(> θ·x) = e^−x·(1 + x + x²/2).
    """
    if not (math.isfinite(rate) and rate > 0 and math.isfinite(span_ms) and span_ms > 0):
        raise AssertionError(f"Rate {rate}, Dauer {span_ms}")
    mean = max(200.0, 60000 / rate - catalog.BLINK_REFRACTORY_MS)
    tail = 1 - 0.5 ** (60000 / (span_ms * rate))
    low, high = 0.0, 100.0
    for _ in range(100):
        x = (low + high) / 2
        if math.exp(-x) * (1 + x + x * x / 2) > tail:
            low = x
        else:
            high = x
    return catalog.BLINK_REFRACTORY_MS + low * mean / 3


def _longest_thinking_pause_ms(trace: IdleTrace) -> float:
    """Die längste Pause zwischen zwei Lidschlägen vom Beginn des Nachdenkens bis zur Antwort.

    Wie im Prüfer des Generators: ohne zwei Lidschläge gilt die ganze Spanne als Pause.
    """
    thinking = next(s.at_ms for s in trace.states if s.state is IdleState.THINKING)
    answer = next(s.at_ms for s in trace.states
                  if s.state is IdleState.ANSWER and s.at_ms > thinking)
    times = [b.at_ms for b in trace.blinks if thinking <= b.at_ms < answer]
    if times != sorted(times):
        raise AssertionError("Lidschläge nicht nach der Zeit geordnet")
    return max((b - a for a, b in zip(times, times[1:])), default=answer - thinking)


class CharacterizationTest(unittest.TestCase):
    """Gleichheit mit dem Referenzgenerator, je Lauf ein Zeuge (Methoden unten erzeugt)."""


def _make_run_test(index: int) -> Callable[[unittest.TestCase], None]:
    """Der Zeuge für den Lauf `index`: Zustände, Formen, Lid, Ereignisse, Proben."""
    if not 0 <= index < len(REFERENCE["laeufe"]):
        raise AssertionError(f"kein Lauf {index}")

    def test(self: unittest.TestCase) -> None:
        """Der Lauf plant und setzt dasselbe wie der Generator."""
        mismatch = _run_mismatch(index)
        self.assertIsNone(mismatch, f"{_label(index)}: {mismatch}")

    return test


for _index, _run in enumerate(REFERENCE["laeufe"]):
    setattr(CharacterizationTest, f"test_run_{_run['fall']}_seed_{_run['seed']}",
            _make_run_test(_index))


class CheckpointTest(unittest.TestCase):
    """Die Prüfpunkte des Generators an den Verläufen des Clients."""

    def test_thinking_has_no_f14_and_no_open_mouth_except_e1(self) -> None:
        thinking = [f for _, trace in _all_traces() for f in trace.forms
                    if f.state is IdleState.THINKING]
        self.assertNotIn("F14", {f.form_id for f in thinking})
        opened = [(f.at_ms, f.form_id, f.mouth_open_max) for f in thinking
                  if f.form_id != "E1" and f.mouth_open_max > 4]
        self.assertEqual(opened, [])

    def test_inhale_opens_the_mouth_over_4(self) -> None:
        # Zwilling: Das Maß der Öffnung sieht einen offenen Mund im Nachdenken.
        inhales = [f.mouth_open_max for _, trace in _all_traces() for f in trace.forms
                   if f.state is IdleState.THINKING and f.form_id == "E1"]
        self.assertTrue(any(value > 4 for value in inhales), inhales)

    def test_f14_occurs_in_noise(self) -> None:
        # Zwilling: F14 ist im Katalog ziehbar und kommt außerhalb des Nachdenkens vor.
        noise = {f.form_id for _, trace in _all_traces() for f in trace.forms
                 if f.state is IdleState.NOISE}
        self.assertIn("F14", noise)

    def test_inhale_begins_at_arrival_and_lasts_700_to_900_ms(self) -> None:
        inhales = 0
        for index, trace in _all_traces():
            arrivals = {_first_step(e.at_ms) for e in trace.events if e.event_type == "antwort"}
            for form in (f for f in trace.forms if f.form_id == "E1"):
                inhales += 1
                with self.subTest(run=_label(index), at=form.at_ms):
                    self.assertIn(form.at_ms, arrivals)
                    self.assertEqual(form.t0, form.at_ms)
                    self.assertTrue(700.0 <= form.duration <= 900.0, form.duration)
        self.assertGreater(inhales, 0)

    def test_answer_begins_when_the_inhale_ends(self) -> None:
        answers = 0
        for index, trace in _all_traces():
            inhales = [f for f in trace.forms if f.form_id == "E1"]
            for state in (s for s in trace.states if s.reason == "nach dem Einatmen"):
                answers += 1
                inhale = [f for f in inhales if f.t0 <= state.at_ms][-1]
                with self.subTest(run=_label(index), at=state.at_ms):
                    self.assertEqual(state.at_ms, _first_step(inhale.t0 + inhale.duration))
        self.assertGreater(answers, 0)

    def test_afterglow_ends_at_its_duration(self) -> None:
        ended = 0
        for index, trace in _all_traces():
            for entry, following, _ in _spans(trace, IdleState.AFTERGLOW):
                limit = _first_step(entry.until_ms)
                by_duration = following is not None and following.reason == "Nachklang vorbei"
                ended += by_duration
                with self.subTest(run=_label(index), at=entry.at_ms):
                    self.assertTrue(following is None or following.at_ms <= limit)
                    self.assertTrue(not by_duration or following.at_ms == limit)
        self.assertGreater(ended, 0)

    def test_answer_begins_averted_and_ends_at_the_viewer(self) -> None:
        finished = 0
        for index, trace in _all_traces():
            for entry, following, forms in _spans(trace, IdleState.ANSWER):
                regular = following is not None and following.reason == "Wiedergabe beendet"
                finished += regular
                with self.subTest(run=_label(index), at=entry.at_ms):
                    self.assertEqual((forms[0].form_id, forms[0].at_ms), ("A0", entry.at_ms))
                    self.assertTrue(_averted(forms[0]), forms[0])
                    self.assertTrue(not regular or not _averted(forms[-1]), forms[-1])
        self.assertGreater(finished, 0)


class PlanAndAnswerCheckpointTest(unittest.TestCase):
    """E1, G2, O1–O3, G3, N1 an den Läufen der Referenz im Client.

    Jeder Zeuge verlangt als Zwilling, dass mindestens ein Fall geprüft wurde.
    """

    def test_e1_inhale_opens_the_mouth_to_7_to_11(self) -> None:
        inhales = [(index, f) for index, (trace, _, _) in _all_runs() for f in trace.forms
                   if f.form_id == "E1"]
        wrong = [(_label(i), f.at_ms, f.mouth_open_max) for i, f in inhales
                 if not 7.0 <= f.mouth_open_max <= 11.0]
        self.assertEqual(wrong, [])
        self.assertGreater(len(inhales), 0)

    def test_g2_f9_in_thinking_is_planned_2_to_3_s(self) -> None:
        accents = [(index, f) for index, (trace, _, _) in _all_runs() for f in trace.forms
                   if f.form_id == "F9" and f.state is IdleState.THINKING]
        wrong = [(_label(i), f.at_ms, f.duration) for i, f in accents
                 if not 2000.0 <= f.duration <= 3000.0]
        self.assertEqual(wrong, [])
        self.assertGreater(len(accents), 0)

    def test_o1_the_answer_glides_over_a0(self) -> None:
        # Ziel ist die letzte Probe der Antwort;
        # geprüft, wo A0 ≤ 40 % der Antwort und der Weg ≥ 0,05
        checked, wrong = 0, []
        for index, (trace, _, steps) in _all_runs():
            for entry, following, forms in _spans(trace, IdleState.ANSWER):
                span = _steps_in(steps, entry, following)
                before = [s for s in steps if s.t < entry.at_ms]
                a0 = forms[0].duration
                if not before or not span or span[-1].t - entry.at_ms < a0 / 0.4:
                    continue
                v0, v1 = _value(before[-1], "mw"), _value(span[-1], "mw")
                if abs(v1 - v0) < 0.05:
                    continue
                checked += 1
                for s in span:
                    u, share = s.t - entry.at_ms, (_value(s, "mw") - v0) / (v1 - v0)
                    early = a0 >= 1450 and u < 500 and share > 0.30
                    hasty = u < 0.7 * a0 and share >= 0.9
                    late = u >= a0 + STEP_MS and abs(share - 1) > 0.01
                    if early or hasty or late:
                        wrong.append((_label(index), s.t, round(share, 4), a0))
        self.assertEqual(wrong[:5], [])
        self.assertGreater(checked, 0)

    def test_o2_mouth_and_jaw_stay_small_in_the_answer(self) -> None:
        answering = [(index, s) for index, (_, _, steps) in _all_runs() for s in steps
                     if s.state is IdleState.ANSWER]
        wrong = [(_label(i), s.t, _value(s, "mo"), _value(s, "jaw")) for i, s in answering
                 if _value(s, "mo") > 2.0001 or _value(s, "jaw") > 1.5001]
        self.assertEqual(wrong[:5], [])
        self.assertGreater(len(answering), 0)

    def test_o3_brows_and_mouth_corners_never_stand_still_for_5_s(self) -> None:
        checked, wrong = 0, []
        for index, (trace, _, steps) in _all_runs():
            for entry, following, _ in _spans(trace, IdleState.ANSWER):
                if entry.until_ms is None or entry.until_ms - entry.at_ms <= 10000:
                    continue
                checked += 1
                span = [s for s in _steps_in(steps, entry, following) if s.t < entry.until_ms]
                for key in catalog.NOISE_IN_ANSWER:
                    still = _still_window([(s.t, _value(s, key)) for s in span], 5000, 0.05)
                    if still is not None:
                        wrong.append((_label(index), key, still))
        self.assertEqual(wrong, [])
        self.assertGreater(checked, 0)

    def test_g3_upper_lid_rises_with_the_gaze_up(self) -> None:
        # je Form im Rauschen und Nachdenken (außer F9) mit fester Basis:
        # eo − 0,08·max(0, −gy) konstant
        moved, wrong = 0, []
        for index, (trace, _, steps) in _all_runs():
            starts = [f.at_ms for f in trace.forms]
            fixed = _forms_with_fixed_basis(trace)
            groups: dict[int, list[tuple[float, float]]] = {}
            for s in steps:
                form = bisect.bisect_right(starts, s.t) - 1
                if (s.state in (IdleState.NOISE, IdleState.THINKING) and s.form_id != "F9"
                        and form in fixed):
                    up = max(0.0, -_value(s, "gy"))
                    groups.setdefault(form, []).append((_value(s, "eo"), up))
            for form, values in groups.items():
                if len(values) < 2 or min(eo for eo, _ in values) <= 0.3001:
                    continue
                up = [u for _, u in values]
                moved += max(up) - min(up) >= 0.02
                rest = [eo - catalog.EYE_OPEN_GAZE_UP * u for eo, u in values]
                if max(rest) - min(rest) > 0.0005:
                    wrong.append((_label(index), trace.forms[form].at_ms))
        self.assertEqual(wrong[:5], [])
        self.assertGreater(moved, 0)

    def test_g3_counts_only_forms_with_a_fixed_basis(self) -> None:
        # Zwilling zu G3: Pixies Auftrag in der ersten Form, die zweite ohne Ereignis
        def form(at_ms: float) -> TracedForm:
            return TracedForm(at_ms, IdleState.NOISE, "F4", at_ms, 5000.0, 0.0, 0.0)

        trace = IdleTrace(
            states=[TracedState(0.0, IdleState.NOISE, "Start", None)],
            forms=[form(0.0), form(5000.0), form(10000.0)],
            events=[TracedEvent(2000.0, "pixie_auftrag", 2020.0),
                    TracedEvent(10000.0, "pixie_auftrag", 10000.0)],
        )
        self.assertEqual(_forms_with_fixed_basis(trace), {1, 2})

    def test_n1_energy_fades_in_the_afterglow(self) -> None:
        # E aus ω des Gesichts: ω = 5·(1 + 0,8·E); bis 60 % der Dauer E = A·(1 − 0,5·p/0,6)
        checked, wrong = 0, []
        for index, (trace, _, steps) in _all_runs():
            for entry, following, _ in _spans(trace, IdleState.AFTERGLOW):
                answer_at = max(s.at_ms for s in trace.states
                                if s.state is IdleState.ANSWER and s.at_ms < entry.at_ms)
                arousal = _answer_arousal(index, answer_at)
                duration = entry.until_ms - entry.at_ms
                for s in _steps_in(steps, entry, following):
                    p = (s.t - entry.at_ms) / duration
                    if p > 0.6:
                        continue
                    checked += 1
                    energy = (s.face_omega / 5 - 1) / 0.8
                    if abs(energy - arousal * (1 - 0.5 * p / 0.6)) > 1e-6:
                        wrong.append((_label(index), s.t, round(energy, 6)))
        self.assertEqual(wrong[:5], [])
        self.assertGreater(checked, 0)


class BlinkCheckpointTest(unittest.TestCase):
    """L-4, L-5 und L-6 an den Läufen der Referenz im Client."""

    def test_l4_exactly_one_blink_at_the_insight(self) -> None:
        insights, wrong = 0, []
        for index, (trace, _, _) in _all_runs():
            for form in (f for f in trace.forms if f.form_id == "F9"):
                insights += 1
                n = sum(1 for b in trace.blinks if form.at_ms <= b.at_ms < form.at_ms + 1000)
                if n != 1:
                    wrong.append((_label(index), form.at_ms, n))
        self.assertEqual(wrong, [])
        self.assertGreater(insights, 0)

    def test_l5_the_eye_closes_40_ms_or_the_next_blink_sets_on(self) -> None:
        checked, wrong = 0, []
        for index, (trace, _, _) in _all_runs():
            blinks = trace.blinks
            for blink, following in zip(blinks, [*blinks[1:], None], strict=True):
                checked += 1
                closed_until = blink.begin_ms + blink.close_ms + blink.hold_ms
                if blink.hold_ms < catalog.BLINK_HOLD_MS - 1e-6:
                    wrong.append((_label(index), blink.at_ms, "kurz zu"))
                elif (following is not None and following.at_ms < closed_until
                      and following.at_ms != blink.at_ms
                      and not following.begin_ms < following.at_ms):
                    wrong.append((_label(index), following.at_ms, "springt auf"))
        self.assertEqual(wrong, [])
        self.assertGreater(checked, 0)

    def test_l6_longest_pause_in_long_thinking_has_median_at_most_10_s(self) -> None:
        pauses = [_longest_thinking_pause_ms(trace) for index, (trace, _, _) in _all_runs()
                  if REFERENCE["laeufe"][index]["fall"] == "nachdenken_lang"]
        self.assertEqual(len(pauses), 3)  # drei Startwerte mit 120 s Nachdenken
        self.assertLessEqual(sorted(pauses)[1], 10000.0)


class HeadCheckpointTest(unittest.TestCase):
    """Y1–Y4 an den Kopfzielen der Läufe, Y5 als Zwilling ohne Drehung über alle Läufe."""

    ART_MAX = {catalog.HEAD_SMALL: 9.0, catalog.HEAD_DEEP_KIND: 11.0, catalog.HEAD_BACK: 0.0}

    def test_y1_to_y4_head_targets_follow_the_rule(self) -> None:
        heads, wrong = 0, []
        for index, (trace, _, steps) in _all_runs():
            wrong += [(_label(index), s.t, "Y1 yaw", s.head_yaw) for s in steps
                      if abs(s.head_yaw) > catalog.YAW_MAX]
            for h in trace.heads:
                heads += 1
                delay = (catalog.HEAD_RETURN_MS if h.kind == catalog.HEAD_BACK
                         else catalog.HEAD_FOLLOWS_MS)
                after = h.at_ms - h.gaze_change_ms
                same_side = h.target != 0 and (h.target > 0) == (h.gaze_x > 0)
                checks = (
                    ("Y1", abs(h.target) <= self.ART_MAX[h.kind] + 1e-9),
                    ("Y2", abs(h.gaze_x) <= 0.12 or same_side),
                    ("Y3", delay <= after < catalog.HEAD_FOLLOWS_MS + 2 * STEP_MS),
                    ("Y4", h.gaze_x != 0 or h.target == 0),
                )
                wrong += [(_label(index), h.at_ms, name) for name, ok in checks if not ok]
        self.assertEqual(wrong[:5], [])
        self.assertGreater(heads, 0)

    def test_y5_without_head_turn_the_plan_is_the_same(self) -> None:
        moved = 0
        for index, (trace, _, steps) in _all_runs():
            twin_trace = IdleTrace()
            differing = still = 0
            for step, (t, frame) in zip(steps, _replay(index, twin_trace, False), strict=True):
                differing += step.t != t or step.plan != hash(frame)
                still += frame.head_yaw != 0.0
            moved += any(abs(s.head_yaw) > 1.0 for s in steps)
            with self.subTest(run=_label(index)):
                self.assertEqual((differing, still), (0, 0))
                self.assertEqual(twin_trace, trace)
        self.assertGreater(moved, 0)


class RuleTest(unittest.TestCase):
    """Was nur über viele Läufe gilt (G1, B5, L-1 … L-3, L-6), an der Regel geprüft.

    Dazu die Konstanten von L-4 und L-5. Y6 schreibt der Generator nicht vor, er
    berichtet ihn nur; dafür steht hier kein Zeuge.
    """

    # L-6 in der Lage mit 120 s Nachdenken: Nova mit Freude 0,65, Form F1.
    L6_THINKING_MS = 120000.0
    L6_ENERGY = 0.65
    # Schranke für das Modell: L-6 (10 s) mit 30 % Reserve. Das Modell kennt weder die
    # Pause in F5 noch die Untergrenze rate/4 bei vielen gekoppelten Lidschlägen; in den
    # drei langen Läufen der Referenz liegt der Median 1,2 s über dem Modell.
    L6_MODEL_BOUND_MS = 7000.0

    def test_b5_afterglow_blinks_less_than_the_answer(self) -> None:
        for sector in range(9):
            for tenth in range(10):
                with self.subTest(sector=sector, energy=tenth / 10):
                    self.assertLess(blink_rate(IdleState.AFTERGLOW, sector, tenth / 10, "F1"),
                                    blink_rate(IdleState.ANSWER, sector, tenth / 10, "F1"))

    def test_g1_thinking_looks_into_the_void(self) -> None:
        f5 = FORMS["F5"].gaze
        self.assertGreater(abs(f5.x), 0.12)  # F5 abgewandt
        self.assertEqual(catalog.ACCENT_THINKING_SHARE, 0.5)  # F16 im Nachdenken halb so oft
        low, lo, hi = catalog.F9_THINKING_MS
        self.assertEqual((low + lo, low + hi), (2000.0, 3000.0))  # F9 ein kurzer Akzent

    def test_l_refractory_periods_and_closed_phase(self) -> None:
        self.assertEqual(catalog.BLINK_REFRACTORY_MS, 800.0)  # L-1, L-2: dahinter Gamma(3)
        self.assertEqual(catalog.BLINK_REFRACTORY_INSIGHT_MS, 1000.0)  # L-4
        self.assertEqual(catalog.BLINK_REFRACTORY_END_MS, 1500.0)  # L-3
        self.assertEqual(catalog.BLINK_HOLD_MS, 40.0)  # L-5

    def test_l6_longest_pause_in_thinking_stays_below_the_bound(self) -> None:
        # gerechnet: Rate 19,8 je Minute → Median der längsten Pause 6,53 s
        rate = blink_rate(IdleState.THINKING, catalog.SECTOR_BY_NAME["freude"],
                          self.L6_ENERGY, "F1")
        median = _longest_pause_median_ms(rate, self.L6_THINKING_MS)
        self.assertLessEqual(median, self.L6_MODEL_BOUND_MS)

    def test_twin_l6_a_base_rate_30_percent_lower_exceeds_the_bound(self) -> None:
        # gerechnet: Rate 16,2 je Minute → 8,00 s
        rate = blink_rate(IdleState.THINKING, catalog.SECTOR_BY_NAME["freude"],
                          self.L6_ENERGY, "F1")
        lower = rate - 0.3 * catalog.BLINK_BASE_RATE[IdleState.THINKING]
        median = _longest_pause_median_ms(lower, self.L6_THINKING_MS)
        self.assertGreater(median, self.L6_MODEL_BOUND_MS)


class PupilTest(unittest.TestCase):
    """P-1 an der Regel (nur die Energie anders), P-2 an Läufen mit Angst und Überraschung."""

    def test_p1_energy_widens_the_pupil_by_0_12_e(self) -> None:
        logic = IdleLogic(1)
        logic.step(20.0, 0.0, 0.0)
        inputs, inst = logic._inputs(20.0), logic._current()
        field = _KEY_TO_FIELD["ps"]
        for state in (IdleState.NOISE, IdleState.THINKING, IdleState.ANSWER):
            low = logic._targets(20.0, replace(inputs, state=state, energy=0.3), inst)
            high = logic._targets(20.0, replace(inputs, state=state, energy=0.9), inst)
            widened = getattr(high, field) - getattr(low, field)
            with self.subTest(state=state.value):
                self.assertAlmostEqual(widened, 0.072, delta=1e-9)

    def test_p2_fear_and_surprise_never_narrow_the_pupil_below_1(self) -> None:
        field = _KEY_TO_FIELD["ps"]
        for emotion in ("stress", "ueberrascht"):
            for seed in (1, 2, 3):
                logic = IdleLogic(seed, Mood(emotion, 0.9))
                logic.post(TurnBegins(20.0))
                logic.post(AnswerArrives(4000.0, emotion, 0.9, 4000.0))
                frames = [logic.step(float(t), 0.0, 0.0) for t in range(STEP_MS, 9001, STEP_MS)]
                checked = [f for f in frames if f.state in (IdleState.THINKING, IdleState.ANSWER)]
                with self.subTest(emotion=emotion, seed=seed):
                    self.assertGreater(len(checked), 0)
                    self.assertEqual([getattr(f.targets, field) for f in checked
                                      if getattr(f.targets, field) < 1], [])


class BlinkRateTest(unittest.TestCase):
    """Die Rate der Lidschläge je Zustand: Nachdenken < Rauschen < Antwort."""

    def test_order_at_equal_energy(self) -> None:
        for sector in range(9):
            for tenth in range(10):
                energy = tenth / 10
                with self.subTest(sector=sector, energy=energy):
                    thinking = blink_rate(IdleState.THINKING, sector, energy, "F1")
                    noise = blink_rate(IdleState.NOISE, sector, energy, "F1")
                    answer = blink_rate(IdleState.ANSWER, sector, energy, "F1")
                    self.assertLess(thinking, noise)
                    self.assertLess(noise, answer)

    def test_rates_at_half_energy(self) -> None:
        # gerechnet: Grundrate 12 · 15 · 20 je Minute + 12 · 0,5
        self.assertEqual(blink_rate(IdleState.THINKING, 0, 0.5, "F1"), 18.0)
        self.assertEqual(blink_rate(IdleState.NOISE, 0, 0.5, "F1"), 21.0)
        self.assertEqual(blink_rate(IdleState.ANSWER, 0, 0.5, "F1"), 26.0)


class RandomTest(unittest.TestCase):
    """mulberry32 mit Startwert: dieselbe Folge wie der Generator."""

    def test_seed_1(self) -> None:
        rng = Mulberry32(1)
        values = [rng.next() for _ in range(5)]
        self.assertEqual(values, [0.6270739405881613, 0.002735721180215478, 0.5274470399599522,
                                  0.9810509674716741, 0.9683778982143849])
        self.assertEqual(rng.draws, 5)

    def test_seed_7(self) -> None:
        rng = Mulberry32(7)
        values = [rng.next() for _ in range(5)]
        self.assertEqual(values, [0.011704753153026104, 0.06195825757458806, 0.97690763277933,
                                  0.6990287057124078, 0.5214452685322613])

    def test_gamma3_is_three_exponential_draws_in_order(self) -> None:
        # gegen die Definition des Generators: expo(m/3) + expo(m/3) + expo(m/3), von links
        rng, by_hand = Mulberry32(1), Mulberry32(1)
        value = rng.gamma3(900.0)
        third = 300.0
        expected = by_hand.exponential(third) + by_hand.exponential(third)
        expected += by_hand.exponential(third)
        self.assertEqual(value, expected)
        self.assertEqual(rng.draws, 3)

    def test_twin_gamma3_is_not_one_exponential_draw(self) -> None:
        self.assertNotEqual(Mulberry32(1).gamma3(900.0), Mulberry32(1).exponential(900.0))

    def test_head_seed_as_in_the_generator(self) -> None:
        # (imul(1, 0x9E3779B1) ^ 0x85EBCA6B) >>> 0, von Hand gerechnet
        self.assertEqual(head_seed(1), 0x1BDCB3DA)
        self.assertEqual(head_seed(0), head_seed(1))  # Startwert 0 gilt als 1
        self.assertNotEqual(head_seed(2), head_seed(1))


class CatalogTest(unittest.TestCase):
    """Der Katalog ist vollständig."""

    def test_forms(self) -> None:
        expected = {f"F{i}" for i in range(1, 18)} | {"E1", "A0", "A1", "A2"}
        self.assertEqual(set(FORMS), expected)
        self.assertEqual(set(DRAWABLE), set(BASE_WEIGHTS))
        self.assertNotIn("F16", BASE_WEIGHTS)

    def test_every_weighted_form_in_every_group(self) -> None:
        for state, group in GROUP_FACTORS.items():
            with self.subTest(state=state.value):
                self.assertEqual(set(group), set(BASE_WEIGHTS))
                self.assertTrue(all(len(BASE_WEIGHTS[f]) == 9 for f in group))
                self.assertTrue(all(f in FORMS for f in group))


class InputTest(unittest.TestCase):
    """Eingänge von außen: eine unbekannte Emotion, der Blick des Gesichts."""

    def test_unknown_emotion_is_neutral_with_error_line(self) -> None:
        with self.assertLogs("avatar.idle", level="ERROR") as logs:
            unknown = _answer_frames("unbekannt")
        self.assertTrue(any("nicht im Kanon" in line for line in logs.output), logs.output)
        with self.assertNoLogs("avatar.idle", level="ERROR"):
            neutral = _answer_frames("neutral")
        self.assertEqual([f.targets for f in unknown], [f.targets for f in neutral])

    def test_known_emotion_changes_the_targets(self) -> None:
        # Zwilling: eine Emotion des Kanons wirkt auf die Ziele.
        joy = _answer_frames("freude")
        neutral = _answer_frames("neutral")
        self.assertNotEqual([f.targets for f in joy], [f.targets for f in neutral])

    def test_gaze_of_the_face_decides_the_blink_draw(self) -> None:
        shifted = 0
        for seed in range(1, 11):
            draws_neutral, form = _turn_draws(seed, (0.0, 0.0))
            draws_same, form_same = _turn_draws(seed, (form.gaze_x, form.gaze_y))
            shift = math.hypot(form.gaze_x, form.gaze_y) > 0.4 and form.form_id != "F9"
            shifted += shift
            with self.subTest(seed=seed):
                self.assertEqual((form_same.form_id, form_same.gaze_x, form_same.gaze_y),
                                 (form.form_id, form.gaze_x, form.gaze_y))
                self.assertIn(draws_neutral - draws_same, (1, 3) if shift else (0,))
        self.assertGreater(shifted, 0)


if __name__ == "__main__":
    unittest.main()
