"""Zeugen für die Leerlauf-Logik des Avatars: dieselbe Planung wie der Referenzgenerator.

Die Verläufe unter `avatar_reference/idle.json` sind vom Referenzgenerator erzeugt
(zehn Fälle × drei Startwerte) und werden nicht von Hand geändert. Eine Abweichung
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

Toleranzen: Zeiten und Dauern 1e-6 ms, Blickpunkte 1e-9, Ziele, Lid, ω und k 1e-3
(die Referenz rundet sie auf vier Stellen). Die kleinste fachliche Abweichung —
eine Ziehung mehr, eine andere Form — verschiebt Zeiten um Millisekunden.
"""

import json
import math
import unittest
from collections.abc import Callable, Iterator
from pathlib import Path

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
    TracedForm,
    TracedState,
    TurnBegins,
    TurnFailed,
    blink_rate,
)
from avatar.idle_catalog import BASE_WEIGHTS, DRAWABLE, FORMS, GROUP_FACTORS, IdleState

REFERENCE_PATH = Path(__file__).parent / "avatar_reference" / "idle.json"
STEP_MS = 20
TIME_TOLERANCE = 1e-6
GAZE_TOLERANCE = 1e-9
TARGET_TOLERANCE = 1e-3
PLAYBACK_TAIL_MS = 400.0
UNSPOKEN_PLAYBACK_MS = 1000.0
_KEY_TO_FIELD = {key: name for name, key in PROTOTYPE_KEYS.items()}
_Span = tuple[TracedState, TracedState | None, list[TracedForm]]


def _load_reference() -> dict:
    """Die Verläufe des Referenzgenerators."""
    with REFERENCE_PATH.open(encoding="utf-8") as handle:
        reference = json.load(handle)
    if len(reference["laeufe"]) != 30:
        raise AssertionError(f"idle.json: {len(reference['laeufe'])} Läufe statt 30")
    return reference


REFERENCE = _load_reference()
_SIMULATIONS: dict[int, tuple[IdleTrace, list[tuple[int, IdleFrame]]]] = {}


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


def _simulation(index: int) -> tuple[IdleTrace, list[tuple[int, IdleFrame]]]:
    """Der Lauf `index` im Client: Verlauf und die Bilder an den Proben (einmal gerechnet)."""
    if index in _SIMULATIONS:
        return _SIMULATIONS[index]
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
    trace = IdleTrace()
    logic = IdleLogic(run["seed"], nova, events[:running], trace)
    for event in events[running:]:
        logic.post(event)
    probe_ms = REFERENCE["probe_ms"]
    probes: list[tuple[int, IdleFrame]] = []
    for t in range(STEP_MS, run["sim_ms"] + 1, STEP_MS):
        frame = logic.step(float(t), 0.0, 0.0)
        if t % probe_ms == 0:
            probes.append((t, frame))
    _SIMULATIONS[index] = (trace, probes)
    return trace, probes


def _all_traces() -> Iterator[tuple[int, IdleTrace]]:
    """Die Verläufe des Clients für alle 30 Läufe."""
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


def _run_mismatch(index: int) -> str | None:
    """Das erste abweichende Element des Laufs `index` über alle Teile des Verlaufs."""
    run = REFERENCE["laeufe"][index]
    trace, probes = _simulation(index)
    keys = REFERENCE["kanaele"]
    if set(keys) != set(_KEY_TO_FIELD):
        raise AssertionError("die Kanäle der Referenz sind nicht die des Prototyps")
    t, g, v = TIME_TOLERANCE, GAZE_TOLERANCE, TARGET_TOLERANCE
    parts = (
        ("zustaende", [(s["t"], s["z"], s["bis"]) for s in run["zustaende"]],
         [(s.at_ms, s.state.value, s.until_ms) for s in trace.states], (t, None, t)),
        ("formen", [(f["t"], f["z"], f["id"], f["t0"], f["d"], f["x"], f["y"], f["mo"])
                    for f in run["formen"]],
         [(f.at_ms, f.state.value, f.form_id, f.t0, f.duration, f.gaze_x, f.gaze_y,
           f.mouth_open_max) for f in trace.forms], (t, None, None, t, t, g, g, v)),
        ("lid", [(b["t"], b["z"], b["gekoppelt"], b["zu"], b["auf"]) for b in run["lid"]],
         [(b.at_ms, b.state.value, b.coupled, b.close_ms, b.open_ms) for b in trace.blinks],
         (t, None, None, t, t)),
        ("ereignisse", [(e["t"], e["typ"], e["behandelt"]) for e in run["ereignisse"]],
         [(e.at_ms, e.event_type, e.handled_ms) for e in trace.events], (t, None, t)),
        ("proben", [(p["t"], p["z"], p["id"], p["ziele"], p["lid"], p["wGesicht"], p["k"],
                     p["akt"]) for p in run["proben"]],
         [(at, f.state.value, f.form_id, [getattr(f.targets, _KEY_TO_FIELD[k]) for k in keys],
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
