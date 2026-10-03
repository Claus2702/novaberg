"""Zeugen für die Puppe des Avatars und die Umsetzung einer Antwort in eine Äußerung.

Ohne GTK und ohne Cairo: Die Zeit treiben die Zeugen selbst, in festen Schritten,
den Startwert des Leerlaufs setzen sie über das `random.Random` der Puppe fest.

Die Puppe nimmt die Ziele des Leerlaufs. Geprüft wird das gegen einen Zwilling:
eine zweite `IdleLogic` mit demselben Startwert, denselben Ereignissen und genau
dem Blick, den die Feder der Puppe vor jedem Schritt zeigt — über die Fälle der
Referenz (`avatar_reference/idle.json`, `eingang`, je Fall der erste Startwert).
Gegen die Referenz selbst prüft `test_avatar_idle.py`: Sie plant mit dem Blick
(0, 0), die Puppe mit dem Blick der Feder, und davon hängt eine Ziehung ab.

Die Feder je Kanalgruppe rechnen die Zeugen selbst nach, mit ω als Zahl (Blick 35,
Pupille 5, alle übrigen Kanäle das ω des Gesichts aus dem Leerlauf), nicht aus dem
Modul gelesen.

Die Zuordnung Name → Sektor steht hier als eigene Tabelle, abgeschrieben aus den
Schlüsselbildern des Prototyps (`hi` und `lo` je Sektor), nicht aus dem Modul
gelesen: Eine falsche Zuordnung zeigte still ein falsches Gesicht.
"""

import json
import math
import random
import unittest
from collections.abc import Iterator
from dataclasses import dataclass, field, fields, replace
from pathlib import Path

from avatar import idle_catalog
from avatar.animator import spring_step_each
from avatar.face import NEUTRAL, FaceState
from avatar.idle import (
    AnswerArrives,
    IdleFrame,
    IdleLogic,
    ImpulseThinks,
    PixieJob,
    TurnBegins,
    TurnFailed,
)
from avatar.idle_catalog import IdleState
from avatar.pose import Pose
from avatar.puppet import (
    NAME_BY_SECTOR,
    SECTOR_BY_NAME,
    Puppet,
    Utterance,
    new_puppet,
    puppet_cue,
    puppet_event,
    puppet_step,
    utterance_from_turn,
)
from avatar.speech import speech_timeline, text_to_phonemes

STEP_S = 0.01
CASE_STEP_S = 0.02  # Schritt der Fälle aus der Referenz, wie dort
START_S = 100.0
LOGGER = "avatar.puppet"
GAZE_OMEGA = 35.0
PUPIL_OMEGA = 5.0
BLEND_OMEGA = 12.0  # 1/s, Feder des Sprechanteils
SLACK = 1e-9  # Rundung der Gleitkommarechnung, weit unter jeder Bewegung
CHANNELS: tuple[str, ...] = tuple(f.name for f in fields(FaceState))
REFERENCE_PATH = Path(__file__).parent / "avatar_reference" / "idle.json"

# Aus dem Prototyp abgeschrieben: { id, name, hi, lo } je Sektor.
PROTOTYPE_NAMES: dict[str, int | None] = {
    "neutral": None,
    "begeisterung": 1,
    "freude": 1,
    "dankbarkeit": 2,
    "zufriedenheit": 2,
    "stress": 3,
    "unsicherheit": 3,
    "ueberrascht": 4,
    "verwundert": 4,
    "verzweiflung": 5,
    "traurigkeit": 5,
    "frustration": 6,
    "enttaeuschung": 6,
    "wut": 7,
    "aerger": 7,
    "hoffnung": 8,
    "neugierig": 8,
}

SPOKEN = "Mama malt am Abend, Papa baut ein Boot."
OTHER = "Neue Worte."

# Die Wechsel, an denen die Feder stetig bleiben muss (Einatmen → Antwort ist
# Nachdenken → Antwort: das Einatmen gehört zum Nachdenken).
TRANSITIONS = frozenset({
    (IdleState.NOISE, IdleState.THINKING),
    (IdleState.THINKING, IdleState.ANSWER),
    (IdleState.ANSWER, IdleState.AFTERGLOW),
    (IdleState.AFTERGLOW, IdleState.NOISE),
})


def _turn(emotion: object = "freude", arousal: object = 0.5, text: object = "Hallo") -> dict:
    """Eine Antwort, wie sie beim Client ankommt."""
    return {"nova_emotion": emotion, "nova_arousal": arousal, "antwort": text}


def _channels(face: FaceState) -> tuple[float, ...]:
    """Alle Kanäle eines Gesichts in fester Reihenfolge."""
    return tuple(getattr(face, name) for name in CHANNELS)


def _idle_seed(seed: int) -> int:
    """Der Startwert des Leerlaufs einer Puppe mit `random.Random(seed)`: 32 Bit daraus."""
    return random.Random(seed).getrandbits(32)


def _logic_ms(now: float) -> float:
    """Die Zeit des Leerlaufs: ms ab dem ersten Bild der Puppe bei `START_S`."""
    return (now - START_S) * 1000.0


def _playback(text: str) -> float:
    """Die Dauer der Wiedergabe eines Texts: das Ende seiner Zeitachse, 0 ohne Text."""
    return speech_timeline(text_to_phonemes(text))[1] if text.strip() else 0.0


def _omega(name: str, face_omega: float) -> float:
    """ω des Kanals `name`: Blick 35, Pupille 5, sonst das ω des Gesichts."""
    if name in ("gaze_x", "gaze_y"):
        return GAZE_OMEGA
    return PUPIL_OMEGA if name == "pupil_size" else face_omega


def _spring(x: float, v: float, goal: float, omega: float, dt: float) -> tuple[float, float]:
    """Die kritisch gedämpfte Feder über `dt`, exakt gelöst — nachgerechnet, nicht importiert."""
    decay = math.exp(-omega * dt)
    offset = x - goal
    tmp = (v + omega * offset) * dt
    return goal + (offset + tmp) * decay, (v - omega * tmp) * decay


def _jumps(x0: float, v0: float, x1: float, v1: float, goal: float, omega: float,
           dt: float) -> bool:
    """Wahr, wenn ein Schritt der Feder Lage oder Geschwindigkeit springen lässt.

    Für die Feder gilt mit `d0 = x0 - ziel` und `e = exp(-ω·dt)`:
    `x1 - x0 = d0·(e - 1) + (v0 + ω·d0)·dt·e` und
    `v1 - v0 = v0·(e - 1) - ω·(v0 + ω·d0)·dt·e`; mit `1 - e ≤ ω·dt` folgt
    `|x1 - x0| ≤ dt·(|v0| + 2ω·|d0|)` und `|v1 - v0| ≤ ω·dt·(2|v0| + ω·|d0|)`.
    Das gilt für jedes Ziel, auch eines, das gerade gewechselt hat. Wer darüber liegt,
    hat die Feder nicht fortgeschrieben, sondern neu gesetzt.
    Erkennen kann die Schranke einen Sprung nur, wo `2ω·dt < 1` ist. Für den Blick
    (ω 35) ist sie bei 20 ms blind: `2ω·dt` = 1,4, ein Sprung aufs Ziel (`|d0|`) und
    ein Zurücksetzen der Geschwindigkeit (`|v0|`) bleiben darunter. Pupille und
    Gesicht (ω bis 9, `2ω·dt` ≤ 0,36) deckt sie. Hinnehmbar, weil `_spring_mismatch`
    jeden Kanal, den Blick eingeschlossen, in jedem Schritt gegen die geschlossene
    Form hält: Eine neu gesetzte Feder weicht davon ab.
    """
    d0 = abs(x0 - goal)
    position_bound = dt * (abs(v0) + 2 * omega * d0) + SLACK
    velocity_bound = omega * dt * (2 * abs(v0) + omega * d0) + SLACK
    return abs(x1 - x0) > position_bound or abs(v1 - v0) > velocity_bound


class _Driver:
    """Treibt eine Puppe in festen Schritten und prüft jede Pose."""

    def __init__(self, case: unittest.TestCase, seed: int = 7, start: float = START_S) -> None:
        self.case = case
        self.now = start
        self.puppet: Puppet = new_puppet(start, random.Random(seed))

    def step(self) -> Pose:
        """Ein Schritt von `STEP_S`; die Pose muss gültig sein."""
        self.now += STEP_S
        pose = puppet_step(self.puppet, self.now)
        values = (*_channels(pose.face), pose.tongue, pose.blink, pose.breath)
        self.case.assertTrue(all(math.isfinite(v) for v in values), f"bei {self.now}")
        self.case.assertTrue(0.0 <= pose.blink <= 1.0)
        self.case.assertTrue(0.0 <= pose.tongue <= 1.0)
        self.case.assertTrue(-1.0 <= pose.breath <= 1.0)
        self.case.assertIsInstance(pose.boil_tick, int)
        self.case.assertGreaterEqual(pose.boil_tick, 0)
        return pose

    def run(self, seconds: float) -> list[Pose]:
        """Schritte über `seconds`; die Posen in Reihenfolge."""
        return [self.step() for _ in range(round(seconds / STEP_S))]

    def state(self) -> IdleState:
        """Der Zustand des Leerlaufs im letzten Schritt."""
        if self.puppet.frame is None:
            raise AssertionError("noch kein Schritt")
        return self.puppet.frame.state

    def answer(self, text: str, thinking_s: float = 1.0) -> float:
        """Turn, nach `thinking_s` die Antwort mit `text`; die Zeit ihres Eintreffens."""
        puppet_event(self.puppet, TurnBegins, self.now)
        self.run(thinking_s)
        arrives = self.now
        puppet_cue(self.puppet, Utterance(1, 0.6, text), arrives)
        return arrives

    def until_answer(self, limit_s: float = 2.0) -> list[Pose]:
        """Schritte, bis der Leerlauf die Antwort beginnt; die Posen dieser Schritte."""
        poses = []
        while self.state() is not IdleState.ANSWER:
            self.case.assertLess(len(poses) * STEP_S, limit_s, "keine Antwort begonnen")
            poses.append(self.step())
        return poses


# ---------------------------------------------------------------- die Fälle ---


def _load_cases() -> list[dict]:
    """Je Fall der Referenz der erste Lauf (erster Startwert)."""
    with REFERENCE_PATH.open(encoding="utf-8") as handle:
        runs = json.load(handle)["laeufe"]
    cases: dict[str, dict] = {}
    for run in runs:
        cases.setdefault(run["fall"], run)
    if len(cases) < 3:
        raise AssertionError(f"idle.json: nur {len(cases)} Fälle")
    return list(cases.values())


CASES = _load_cases()


@dataclass(frozen=True)
class _Step:
    """Ein Schritt eines Falls: die Puppe danach, ihr Stand davor, die Bilder der Zwillinge."""

    now: float
    dt: float
    puppet: Puppet
    pose: Pose
    face_before: FaceState
    velocity_before: FaceState
    frame: IdleFrame  # Zwilling mit dem Blick der Feder
    zero_frame: IdleFrame  # Zwilling mit dem Blick (0, 0)


def _event_of(entry: dict) -> tuple[type, dict]:
    """Typ und Felder eines Eingangs der Referenz, der keine Antwort ist."""
    kind = entry["typ"]
    if kind == "turn_beginnt":
        return TurnBegins, {}
    if kind == "turn_gescheitert":
        return TurnFailed, {}
    if kind == "impuls_denkt":
        return ImpulseThinks, {"phase": entry["phase"]}
    if kind == "pixie_auftrag":
        return PixieJob, {"phase": entry["phase"], "track": entry["spur"],
                          "job_kind": entry.get("art", ""), "emotion": entry.get("emotion"),
                          "arousal": entry.get("arousal")}
    raise AssertionError(f"Eingang unbekannten Typs {kind!r}")


def _deliver(puppet: Puppet, twins: tuple[IdleLogic, ...], entry: dict, at: float) -> None:
    """Ein Eingang zur Zeit `at`: an die Puppe wie vom Panel, an die Zwillinge direkt."""
    at_ms = _logic_ms(at)
    if entry["typ"] == "antwort":
        emotion, arousal, text = entry["emotion"], entry["arousal"], entry["text"]
        puppet_cue(puppet, Utterance(PROTOTYPE_NAMES[emotion], arousal, text), at)
        events = [AnswerArrives(at_ms, emotion, arousal, _playback(text)) for _ in twins]
    else:
        event_type, data = _event_of(entry)
        puppet_event(puppet, event_type, at, **data)
        events = [event_type(at_ms, **data) for _ in twins]
    for twin, event in zip(twins, events, strict=True):
        twin.post(event)


def _case_steps(run: dict, step_s: float, seconds: float) -> Iterator[_Step]:
    """Treibt Puppe und Zwillinge durch einen Fall; jeder Schritt einmal."""
    puppet = new_puppet(START_S, random.Random(run["seed"]))
    twin, zero = IdleLogic(_idle_seed(run["seed"])), IdleLogic(_idle_seed(run["seed"]))
    inputs = sorted(run["eingang"], key=lambda entry: entry["t"])
    delivered, last = 0, START_S
    for k in range(1, round(seconds / step_s) + 1):
        now = START_S + k * step_s
        while delivered < len(inputs) and START_S + inputs[delivered]["t"] <= now:
            _deliver(puppet, (twin, zero), inputs[delivered], START_S + inputs[delivered]["t"])
            delivered += 1
        face, velocity = puppet.face, puppet.velocity
        pose = puppet_step(puppet, now)
        frame = twin.step(_logic_ms(now), face.gaze_x, face.gaze_y)
        zero_frame = zero.step(_logic_ms(now), 0.0, 0.0)
        yield _Step(now, now - last, puppet, pose, face, velocity, frame, zero_frame)
        last = now


@dataclass
class _CaseResult:
    """Was ein Fall ergab: je Prüfung die erste Abweichung (None = keine)."""

    targets: str | None = None
    spring: str | None = None
    lid: str | None = None
    jump: str | None = None
    diverged_from_zero: bool = False
    transitions: set[tuple[IdleState, IdleState]] = field(default_factory=set)
    caught_snaps: set[tuple[IdleState, IdleState]] = field(default_factory=set)
    answers_begun: int = 0
    lowest_lid: float = 1.0


_RESULTS: dict[int, _CaseResult] = {}


def _same_frame(got: IdleFrame | None, want: IdleFrame) -> bool:
    """Ziele, Lid, ω, Zustand und gesprochene Antwort gleich — exakt, ohne Toleranz."""
    if got is None:
        return False
    return (got.targets == want.targets and got.lid_open == want.lid_open
            and got.face_omega == want.face_omega and got.state is want.state
            and got.answer_at_ms == want.answer_at_ms)


def _spring_mismatch(step: _Step) -> str | None:
    """Der erste Kanal, dessen Feder nicht exakt mit ω seiner Gruppe zum Ziel lief."""
    for name in CHANNELS:
        omega = _omega(name, step.frame.face_omega)
        x, v = _spring(getattr(step.face_before, name), getattr(step.velocity_before, name),
                       getattr(step.frame.targets, name), omega, step.dt)
        got_x, got_v = getattr(step.puppet.face, name), getattr(step.puppet.velocity, name)
        if abs(got_x - x) > SLACK * max(1.0, abs(x)) or abs(got_v - v) > SLACK * max(1.0, abs(v)):
            return f"{name} bei {step.now:.2f} s: {got_x} statt {x}"
    return None


def _jump_of(step: _Step, snapped: bool) -> str | None:
    """Der erste Kanal mit Sprung; `snapped` prüft eine Feder, die aufs Ziel spränge."""
    for name in CHANNELS:
        x0, v0 = getattr(step.face_before, name), getattr(step.velocity_before, name)
        goal = getattr(step.puppet.targets, name)
        x1 = goal if snapped else getattr(step.puppet.face, name)
        v1 = v0 if snapped else getattr(step.puppet.velocity, name)
        if _jumps(x0, v0, x1, v1, goal, _omega(name, step.frame.face_omega), step.dt):
            return f"{name} bei {step.now:.2f} s"
    return None


def _record(result: _CaseResult, step: _Step, previous: IdleState | None) -> None:
    """Hält die Prüfungen eines Schritts fest; je Prüfung zählt die erste Abweichung."""
    at = f"{step.now:.2f} s"
    if result.targets is None and not _same_frame(step.puppet.frame, step.frame):
        result.targets = f"Ziele, Lid, ω, Zustand oder Antwort abweichend bei {at}"
    if result.spring is None:
        result.spring = _spring_mismatch(step)
    if result.lid is None and step.pose.blink != step.frame.lid_open:
        result.lid = f"Pose.blink {step.pose.blink} statt Lid {step.frame.lid_open} bei {at}"
    if result.jump is None:
        result.jump = _jump_of(step, snapped=False)
    changed = previous is not None and previous is not step.frame.state
    if changed:
        result.transitions.add((previous, step.frame.state))
    if changed and _jump_of(step, snapped=True) is not None:
        result.caught_snaps.add((previous, step.frame.state))
    result.diverged_from_zero |= step.zero_frame.targets != step.puppet.targets
    result.lowest_lid = min(result.lowest_lid, step.pose.blink)


def _case_result(index: int) -> _CaseResult:
    """Der Fall `index` aus `CASES`, einmal gerechnet."""
    if index in _RESULTS:
        return _RESULTS[index]
    run = CASES[index]
    result = _CaseResult()
    previous: IdleState | None = None
    speaking: float | None = None
    for step in _case_steps(run, CASE_STEP_S, run["sim_ms"] / 1000.0):
        _record(result, step, previous)
        previous = step.frame.state
        began = step.frame.answer_at_ms
        result.answers_begun += began is not None and began != speaking
        speaking = began if began is not None else speaking
    _RESULTS[index] = result
    return result


def _case_index(name: str) -> int:
    """Die Stelle des Falls `name` in `CASES`."""
    for index, run in enumerate(CASES):
        if run["fall"] == name:
            return index
    raise AssertionError(f"Fall {name!r} fehlt in der Referenz")


# ---------------------------------------------------------------- Zeugen -------


class NameToSectorTest(unittest.TestCase):
    """Der Name der Emotion wird zum Sektor der Schlüsselbilder — alle 17."""

    def test_all_17_names_give_the_prototype_sector(self) -> None:
        self.assertEqual(len(PROTOTYPE_NAMES), 17)
        for name, sector in PROTOTYPE_NAMES.items():
            with self.subTest(name=name):
                self.assertEqual(utterance_from_turn(_turn(name, 0.5)).sector, sector)

    def test_module_table_has_exactly_the_prototype_names(self) -> None:
        """Ein zusätzlicher Name im Modul wäre eine Zuordnung, die kein Zeuge kennt."""
        self.assertEqual(set(SECTOR_BY_NAME), set(PROTOTYPE_NAMES))

    def test_each_sector_has_two_names(self) -> None:
        for sector in range(1, 9):
            names = [n for n, s in PROTOTYPE_NAMES.items() if s == sector]
            self.assertEqual(len(names), 2, sector)
            for name in names:
                self.assertEqual(utterance_from_turn(_turn(name)).sector, sector, name)

    def test_known_name_logs_no_error(self) -> None:
        """Zwilling der Abweisungen: ein gültiger Turn bleibt still im Log."""
        with self.assertNoLogs(LOGGER, level="WARNING"):
            utterance = utterance_from_turn(_turn("wut", 0.8, "Nein."))
        self.assertEqual(utterance, Utterance(7, 0.8, "Nein."))

    def test_unknown_name_gives_neutral_with_error(self) -> None:
        for name in ("glueck", "Freude", "überrascht", ""):
            with self.subTest(name=name), self.assertLogs(LOGGER, level="ERROR"):
                self.assertIsNone(utterance_from_turn(_turn(name, 0.9)).sector)

    def test_name_that_is_no_string_gives_neutral_with_error(self) -> None:
        with self.assertLogs(LOGGER, level="ERROR"):
            self.assertIsNone(utterance_from_turn(_turn(3, 0.9)).sector)

    def test_each_sector_reaches_the_idle_logic_as_its_sector(self) -> None:
        """Die Puppe gibt dem Leerlauf einen Namen zurück; er führt dort zum selben Sektor."""
        for name, sector in PROTOTYPE_NAMES.items():
            with self.subTest(name=name):
                expected = 0 if sector is None else sector
                self.assertEqual(idle_catalog.SECTOR_BY_NAME[NAME_BY_SECTOR[sector]], expected)


class TurnFieldsTest(unittest.TestCase):
    """Fehlende und falsche Felder: Error-Zeile und neutral, kein Absturz."""

    def test_missing_emotion_gives_neutral_with_error(self) -> None:
        turn = _turn()
        del turn["nova_emotion"]
        with self.assertLogs(LOGGER, level="ERROR"):
            utterance = utterance_from_turn(turn)
        self.assertIsNone(utterance.sector)
        self.assertEqual(utterance.text, "Hallo")

    def test_missing_arousal_gives_neutral_with_error(self) -> None:
        turn = _turn()
        del turn["nova_arousal"]
        with self.assertLogs(LOGGER, level="ERROR"):
            utterance = utterance_from_turn(turn)
        self.assertEqual((utterance.sector, utterance.arousal), (None, 0.0))

    def test_arousal_no_number_gives_neutral_with_error(self) -> None:
        for value in ("hoch", None, True, math.nan):
            with self.subTest(value=value), self.assertLogs(LOGGER, level="ERROR"):
                utterance = utterance_from_turn(_turn("freude", value))
            self.assertEqual((utterance.sector, utterance.arousal), (None, 0.0))

    def test_missing_text_gives_silence_with_error_and_keeps_the_emotion(self) -> None:
        turn = _turn("freude", 0.7)
        del turn["antwort"]
        with self.assertLogs(LOGGER, level="ERROR"):
            utterance = utterance_from_turn(turn)
        self.assertEqual(utterance, Utterance(1, 0.7, ""))

    def test_turn_that_is_no_mapping_gives_neutral_with_error(self) -> None:
        with self.assertLogs(LOGGER, level="ERROR"):
            self.assertEqual(utterance_from_turn(["freude"]), Utterance(None, 0.0, ""))

    def test_arousal_is_clamped(self) -> None:
        for value, expected in ((1.7, 1.0), (-0.3, 0.0), (2, 1.0)):
            with self.subTest(value=value), self.assertLogs(LOGGER, level="WARNING"):
                utterance = utterance_from_turn(_turn("freude", value))
            self.assertEqual(utterance.arousal, expected)
            self.assertEqual(utterance.sector, 1)

    def test_arousal_inside_range_is_kept(self) -> None:
        """Zwilling der Begrenzung."""
        for value in (0.0, 0.42, 1.0):
            with self.subTest(value=value), self.assertNoLogs(LOGGER, level="WARNING"):
                self.assertEqual(utterance_from_turn(_turn("freude", value)).arousal, value)


class IdleTargetsTest(unittest.TestCase):
    """Die Puppe nimmt die Ziele des Leerlaufs unverändert — gegen den Zwilling, je Fall."""

    def test_cases_cover_an_answer_an_answer_in_the_answer_and_pixie(self) -> None:
        """Die Fälle tragen, was die Zeugen unten brauchen — sonst prüften sie weniger."""
        kinds = [{entry["typ"] for entry in run["eingang"]} for run in CASES]
        self.assertGreaterEqual(len(CASES), 3)
        self.assertTrue(any("antwort" in k for k in kinds))
        self.assertTrue(any("pixie_auftrag" in k and "antwort" not in k for k in kinds))
        replaced = _case_result(_case_index("antwort_ohne_nachdenken"))
        self.assertGreaterEqual(replaced.answers_begun, 2)  # die zweite löst die erste ab

    def test_puppet_takes_the_targets_of_the_idle_logic_unchanged(self) -> None:
        """Alle Kanäle exakt, in jedem Zustand — auch der Mund in der Antwort."""
        for index, run in enumerate(CASES):
            with self.subTest(fall=run["fall"]):
                self.assertIsNone(_case_result(index).targets)

    def test_the_gaze_of_the_spring_changes_the_plan(self) -> None:
        """Zwilling: mit dem Blick (0, 0) plant der Leerlauf in mindestens einem Fall anders.

        Ohne diese Abweichung könnte der Zeuge oben nicht unterscheiden, welchen Blick
        die Puppe übergibt.
        """
        diverged = [i for i in range(len(CASES)) if _case_result(i).diverged_from_zero]
        self.assertTrue(diverged)

    def test_new_puppet_begins_in_the_noise(self) -> None:
        driver = _Driver(self)
        driver.run(2.0)
        self.assertIs(driver.state(), IdleState.NOISE)

    def test_turn_begins_leads_into_thinking(self) -> None:
        """Zwilling: ein Ereignis über `puppet_event` erreicht den Leerlauf."""
        driver = _Driver(self)
        driver.run(0.5)
        puppet_event(driver.puppet, TurnBegins, driver.now)
        driver.step()
        self.assertIs(driver.state(), IdleState.THINKING)


class SpringTest(unittest.TestCase):
    """Die Feder je Kanalgruppe: Blick ω 35, Pupille ω 5, sonst ω des Gesichts; kein Versatz."""

    def test_each_channel_follows_its_target_with_the_omega_of_its_group(self) -> None:
        """Jeder Kanal, jeder Schritt, jeder Fall — auch der Mund ohne Versatz."""
        for index, run in enumerate(CASES):
            with self.subTest(fall=run["fall"]):
                self.assertIsNone(_case_result(index).spring)

    def test_one_second_in_10_and_in_60_steps_ends_the_same(self) -> None:
        """Bei festem Ziel hängt der Endstand nicht von der Bildrate ab."""
        omegas = {name: _omega(name, 9.0) for name in CHANNELS}
        target = FaceState(**{name: getattr(NEUTRAL, name) + 1.0 for name in CHANNELS})
        ends = []
        for count in (10, 60):
            face, velocity = NEUTRAL, FaceState(**dict.fromkeys(CHANNELS, 2.0))
            for _ in range(count):
                face, velocity = spring_step_each(face, velocity, target, omegas, 1.0 / count)
            ends.append((_channels(face), _channels(velocity)))
        for got, want in zip(ends[0][0] + ends[0][1], ends[1][0] + ends[1][1], strict=True):
            self.assertAlmostEqual(got, want, delta=1e-9)
        moved = [abs(a - b) for a, b in zip(ends[0][0], _channels(NEUTRAL), strict=True)]
        self.assertGreater(min(moved), 0.5)  # Zwilling: die Feder hat sich bewegt

    def test_gaze_reaches_95_percent_after_0_14_s(self) -> None:
        """ω 35: (1 + 4,9)·e^−4,9 ≈ 0,044 Rest nach 0,14 s; ω 5 ließe 0,84."""
        omegas = {name: _omega(name, 5.0) for name in CHANNELS}
        target = replace(NEUTRAL, gaze_x=0.8, pupil_size=1.3)
        face, velocity = spring_step_each(
            NEUTRAL, FaceState(**dict.fromkeys(CHANNELS, 0.0)), target, omegas, 0.14)
        self.assertGreater(face.gaze_x, 0.95 * 0.8)
        self.assertLess(face.pupil_size - 1.0, 0.5 * 0.3)  # Zwilling: die Pupille noch nicht

    def test_face_reaches_the_target_after_2_s_and_not_after_half_a_second(self) -> None:
        """ω 5: nach 2 s Rest (1 + 10)·e^−10 ≈ 5e−4, nach 0,5 s (1 + 2,5)·e^−2,5 ≈ 0,29."""
        omegas = {name: _omega(name, 5.0) for name in CHANNELS}
        target = replace(NEUTRAL, mouth_curve=NEUTRAL.mouth_curve + 10.0)
        still = FaceState(**dict.fromkeys(CHANNELS, 0.0))
        late, _ = spring_step_each(NEUTRAL, still, target, omegas, 2.0)
        early, _ = spring_step_each(NEUTRAL, still, target, omegas, 0.5)
        self.assertLess(abs(late.mouth_curve - target.mouth_curve), 0.01 * 10.0)
        self.assertGreater(abs(early.mouth_curve - target.mouth_curve), 0.2 * 10.0)

    def test_no_jump_at_any_change_of_state(self) -> None:
        """Lage und Geschwindigkeit bleiben unter der Schranke aus ω und dem Zeitschritt.

        Für den Blick ist die Schranke bei 20 ms blind (`_jumps`); ihn deckt die
        geschlossene Form in `test_each_channel_follows_its_target_with_the_omega_of_its_group`.
        """
        seen: set[tuple[IdleState, IdleState]] = set()
        for index, run in enumerate(CASES):
            result = _case_result(index)
            seen |= result.transitions
            with self.subTest(fall=run["fall"]):
                self.assertIsNone(result.jump)
        self.assertLessEqual(TRANSITIONS, seen)

    def test_a_jump_at_a_change_of_state_is_caught(self) -> None:
        """Zwilling: je Art des Wechsels läge ein Sprung aufs Ziel in einem Fall über der Schranke.

        Nicht an jedem Wechsel: Stehen alle Federn nahe am Ziel, ist ein Sprung aufs Ziel
        kleiner als die Schranke, und das hängt vom Plan ab, nicht von der Puppe.
        """
        caught: set[tuple[IdleState, IdleState]] = set()
        for index in range(len(CASES)):
            caught |= _case_result(index).caught_snaps
        self.assertLessEqual(TRANSITIONS, caught)


class LidTest(unittest.TestCase):
    """Das Lid ist das des Leerlaufs; das feste Blinzeln schweigt."""

    def test_blink_follows_the_lid_of_the_idle_logic(self) -> None:
        for index, run in enumerate(CASES):
            with self.subTest(fall=run["fall"]):
                result = _case_result(index)
                self.assertIsNone(result.lid)
                self.assertLess(result.lowest_lid, 0.5)  # Zwilling: es wird geblinzelt

    def test_no_blink_for_60_s_without_a_blink_of_the_idle_logic(self) -> None:
        driver = _Driver(self)
        driver.puppet.idle = _OpenEyedLogic(_idle_seed(7))
        self.assertTrue(all(pose.blink == 1.0 for pose in driver.run(60.0)))

    def test_the_same_puppet_blinks_within_60_s(self) -> None:
        """Zwilling: mit dem Lidschlag des Leerlaufs schließt sich das Auge."""
        driver = _Driver(self)
        self.assertLess(min(pose.blink for pose in driver.run(60.0)), 0.5)

    def test_same_seed_blinks_the_same(self) -> None:
        self.assertEqual(self._blinks(7), self._blinks(7))

    def test_other_seed_blinks_otherwise(self) -> None:
        """Zwilling: der Startwert wirkt — ein anderes `rng` ergibt andere Lidschläge."""
        self.assertNotEqual(self._blinks(7), self._blinks(8))

    def _blinks(self, seed: int) -> list[float]:
        """Das Lid über 30 s einer Puppe mit `random.Random(seed)`."""
        return [pose.blink for pose in _Driver(self, seed=seed).run(30.0)]


class _OpenEyedLogic(IdleLogic):
    """Ein Leerlauf, dessen Lid offen bleibt; alles andere wie im echten."""

    def step(self, now_ms: float, gaze_x: float, gaze_y: float) -> IdleFrame:
        """Das Bild des Leerlaufs mit offenem Lid."""
        return replace(super().step(now_ms, gaze_x, gaze_y), lid_open=1.0)


class CueTest(unittest.TestCase):
    """Eingang einer Antwort und der übrigen Ereignisse: Zeit und Vertrag."""

    def test_cue_before_the_last_step_is_rejected(self) -> None:
        driver = _Driver(self)
        driver.run(0.2)
        with self.assertRaises(ValueError):
            puppet_cue(driver.puppet, Utterance(1, 0.5, ""), driver.now - STEP_S)
        puppet_cue(driver.puppet, Utterance(1, 0.5, ""), driver.now)  # Zwilling: gleiche Zeit

    def test_utterance_outside_the_contract_is_rejected(self) -> None:
        driver = _Driver(self)
        for bad in (Utterance(0, 0.5, ""), Utterance(9, 0.5, ""), Utterance(1, 1.5, "")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                puppet_cue(driver.puppet, bad, driver.now)
        puppet_cue(driver.puppet, Utterance(8, 0.0, ""), driver.now)  # Zwilling

    def test_event_outside_the_contract_is_rejected(self) -> None:
        driver = _Driver(self)
        driver.run(0.2)
        with self.assertRaises(TypeError):
            puppet_event(driver.puppet, AnswerArrives, driver.now, emotion="freude",
                         arousal=0.5, playback_ms=100.0)
        with self.assertRaises(TypeError):
            puppet_event(driver.puppet, TurnBegins, driver.now, at_ms=0.0)
        with self.assertRaises(ValueError):
            puppet_event(driver.puppet, TurnBegins, driver.now - STEP_S)
        puppet_event(driver.puppet, ImpulseThinks, driver.now, phase="beginn")  # Zwilling


class SpeechTest(unittest.TestCase):
    """Das Sprechen beginnt mit der Antwort des Leerlaufs und endet mit ihrer Wiedergabe."""

    def _speaking(self, text: str) -> tuple[_Driver, float]:
        """Eine Puppe im ersten Schritt der Antwort mit `text`; das Ende des Sprechens."""
        driver = _Driver(self)
        driver.run(0.2)
        driver.answer(text)
        driver.until_answer()
        speech = driver.puppet.speech
        return driver, (speech.start_ms + speech.end_ms) / 1000.0

    def test_speech_waits_for_the_inhale(self) -> None:
        driver = _Driver(self)
        driver.run(0.2)
        arrives = driver.answer(SPOKEN)
        while driver.state() is not IdleState.ANSWER:
            self.assertFalse(driver.puppet.speech.active, f"bei {driver.now}")
            self.assertLess(driver.puppet.speech.blend, 1e-9)
            self.assertLess(driver.now - arrives, 2.0, "keine Antwort begonnen")
            driver.step()
        self.assertGreaterEqual(driver.now - arrives, 0.7 - 1e-9)  # E1 dauert 0,7–0,9 s

    def test_speech_begins_with_the_answer_of_the_idle_logic(self) -> None:
        """Zwilling: im ersten Schritt der Antwort spricht die Puppe, ab genau diesem Schritt."""
        driver, _ = self._speaking(SPOKEN)
        self.assertTrue(driver.puppet.speech.active)
        self.assertEqual(driver.puppet.speech.start_ms, driver.now * 1000.0)
        self.assertEqual(driver.puppet.speech.end_ms, _playback(SPOKEN))

    def test_speech_ends_where_the_idle_logic_ends_the_playback(self) -> None:
        """Die Antwort endet 0,4 s nach der Wiedergabe; das Sprechen einen Schritt genau dort."""
        driver, end = self._speaking(SPOKEN)
        self.assertGreater(end - driver.now, 1.0)  # der Satz trägt mehr als eine Sekunde
        while driver.puppet.speech.active:
            driver.step()
        silent_at = driver.now
        while driver.state() is IdleState.ANSWER:
            driver.step()
        self.assertIs(driver.state(), IdleState.AFTERGLOW)
        self.assertLessEqual(abs((driver.now - 0.4) - silent_at), STEP_S + 1e-9)
        self.assertLessEqual(abs(silent_at - end), STEP_S + 1e-9)

    def test_text_is_spoken_while_it_lasts(self) -> None:
        driver, end = self._speaking(SPOKEN)
        driver.run(0.25)
        openings = []
        while driver.now + STEP_S < end:
            pose = driver.step()
            self.assertGreater(driver.puppet.speech.blend, 0.5, f"bei {driver.now}")
            openings.append(pose.face.mouth_open)
        low, high = min(openings), max(openings)
        self.assertGreater(high - low, 2.0)
        middle = (low + high) / 2
        pairs = zip(openings, openings[1:], strict=False)
        crossings = sum(1 for a, b in pairs if (a - middle) * (b - middle) < 0)
        self.assertGreaterEqual(crossings, 4)  # auf und zu, mindestens zweimal

    def test_mouth_rests_after_the_text(self) -> None:
        """Nach Ende + 0,6 s ist der Sprechanteil fast null (BLEND_OMEGA 12: (1+7,2)·e^−7,2)."""
        driver, end = self._speaking(SPOKEN)
        while driver.now < end + 0.6:
            driver.step()
        self.assertLess(driver.puppet.speech.blend, 0.01)
        self.assertFalse(driver.puppet.speech.active)

    def test_answer_without_text_is_an_answer_without_speaking(self) -> None:
        """Zwilling: ohne Text beginnt die Antwort, der Sprechanteil bleibt null."""
        driver = _Driver(self)
        driver.run(0.2)
        driver.answer("   ")
        driver.until_answer()
        driver.run(0.3)
        self.assertFalse(driver.puppet.speech.active)
        self.assertLess(driver.puppet.speech.blend, 1e-9)

    def test_second_answer_in_the_inhale_speaks_only_its_text(self) -> None:
        driver = _Driver(self)
        driver.run(0.2)
        driver.answer(SPOKEN)
        driver.run(0.2)  # noch im Einatmen (0,7–0,9 s)
        self.assertIs(driver.state(), IdleState.THINKING)
        puppet_cue(driver.puppet, Utterance(4, 0.5, OTHER), driver.now)
        driver.until_answer()
        own = speech_timeline(text_to_phonemes(OTHER))[0]
        self.assertNotEqual(_playback(OTHER), _playback(SPOKEN))  # Zwilling: die Texte trennen
        self.assertEqual(driver.puppet.speech.end_ms, _playback(OTHER))
        self.assertEqual(driver.puppet.speech.segments, own)
        self.assertEqual(driver.puppet.texts, {})

    def test_answer_in_the_answer_takes_over_without_a_jump(self) -> None:
        driver, _ = self._speaking(SPOKEN)
        before = driver.run(0.4)[-1]
        puppet_cue(driver.puppet, Utterance(1, 0.9, OTHER), driver.now)
        same_time = puppet_step(driver.puppet, driver.now)
        pairs = zip(CHANNELS, _channels(before.face), _channels(same_time.face), strict=True)
        for name, a, b in pairs:
            self.assertAlmostEqual(a, b, delta=1e-9, msg=name)
        self.assertAlmostEqual(before.tongue, same_time.tongue, delta=1e-9)

    def test_answer_in_the_answer_takes_over(self) -> None:
        """Zwilling: der neue Text gilt — sein Beginn ist die Zeit der neuen Antwort."""
        driver, _ = self._speaking(SPOKEN)
        driver.run(0.4)
        cue_at = driver.now
        puppet_cue(driver.puppet, Utterance(1, 0.9, OTHER), cue_at)
        driver.run(0.1)
        self.assertEqual(driver.puppet.speech.start_ms, (cue_at + STEP_S) * 1000.0)
        self.assertEqual(driver.puppet.speech.end_ms, _playback(OTHER))
        self.assertTrue(driver.puppet.speech.active)
        self.assertIs(driver.state(), IdleState.ANSWER)

    def test_a_new_turn_in_the_answer_ends_the_speaking_without_a_jump(self) -> None:
        """Ein Turn mitten im Satz: das Sprechen endet im selben Schritt und läuft stetig aus."""
        driver, end = self._speaking(SPOKEN)
        driver.run(0.4)
        before, before_s = driver.puppet.speech, driver.now
        puppet_event(driver.puppet, TurnBegins, driver.now)
        driver.step()
        after = driver.puppet.speech
        self.assertIs(driver.state(), IdleState.THINKING)
        self.assertLess(driver.now, end)
        self.assertFalse(after.active)
        # Der Anteil der Sprechschicht folgt seiner Feder von der alten Lage zur Ruhe —
        # derselbe Weg wie am regulären Ende, kein Zurücksetzen.
        dt = driver.now - before_s
        blend, blend_velocity = _spring(before.blend, before.blend_velocity, 0.0, BLEND_OMEGA, dt)
        self.assertGreater(before.blend, 0.5)
        self.assertAlmostEqual(after.blend, blend, delta=SLACK)
        self.assertAlmostEqual(after.blend_velocity, blend_velocity, delta=SLACK)
        driver.run(0.6)
        self.assertFalse(driver.puppet.speech.active)
        self.assertLess(driver.puppet.speech.blend, 0.01)

    def test_an_answer_without_text_in_the_answer_ends_the_speaking_without_a_jump(self) -> None:
        """Eine Antwort ohne Text löst ab: das alte Sprechen endet und läuft stetig aus.

        Zwilling ist `test_answer_in_the_answer_takes_over`: mit Text spricht die Ablösung.
        """
        driver, end = self._speaking(SPOKEN)
        driver.run(0.4)
        before, before_s = driver.puppet.speech, driver.now
        first_at = driver.puppet.speaking_at_ms
        puppet_cue(driver.puppet, Utterance(1, 0.9, ""), driver.now)
        driver.step()
        after = driver.puppet.speech
        self.assertIs(driver.state(), IdleState.ANSWER)
        self.assertNotEqual(driver.puppet.frame.answer_at_ms, first_at)  # die neue Antwort
        self.assertLess(driver.now, end)
        self.assertFalse(after.active)
        dt = driver.now - before_s
        blend, blend_velocity = _spring(before.blend, before.blend_velocity, 0.0, BLEND_OMEGA, dt)
        self.assertGreater(before.blend, 0.5)
        self.assertAlmostEqual(after.blend, blend, delta=SLACK)
        self.assertAlmostEqual(after.blend_velocity, blend_velocity, delta=SLACK)
        driver.run(0.6)
        self.assertFalse(driver.puppet.speech.active)
        self.assertLess(driver.puppet.speech.blend, 0.01)

    def test_cue_at_the_time_of_the_answer_just_begun_is_rejected(self) -> None:
        """Eine Antwort zur Zeit der eben begonnenen bricht ab, statt den alten Text zu sprechen."""
        driver, _ = self._speaking(SPOKEN)
        driver.run(0.4)
        puppet_cue(driver.puppet, Utterance(1, 0.9, OTHER), driver.now)
        puppet_step(driver.puppet, driver.now)  # die Ablösung beginnt zur selben Zeit
        self.assertEqual(driver.puppet.speech.start_ms, driver.now * 1000.0)
        with self.assertRaises(ValueError):
            puppet_cue(driver.puppet, Utterance(1, 0.9, SPOKEN), driver.now)
        driver.step()
        puppet_cue(driver.puppet, Utterance(1, 0.9, SPOKEN), driver.now)  # Zwilling: später

    def test_the_same_answer_without_a_turn_speaks_to_its_end(self) -> None:
        """Zwilling: ohne Turn spricht dieselbe Antwort an derselben Stelle weiter."""
        driver, end = self._speaking(SPOKEN)
        driver.run(0.4)
        driver.step()
        self.assertIs(driver.state(), IdleState.ANSWER)
        while driver.now + STEP_S < end:
            self.assertTrue(driver.puppet.speech.active, f"bei {driver.now}")
            driver.step()
        self.assertGreater(driver.puppet.speech.blend, 0.5)


class StepTest(unittest.TestCase):
    """Atem, Takt und Zeit."""

    def test_breath_and_boil_tick_follow_the_time_since_the_first_frame(self) -> None:
        driver = _Driver(self)
        pose = driver.run(1.0)[-1]
        t_ms = (driver.now - START_S) * 1000.0
        self.assertAlmostEqual(pose.breath, math.sin(t_ms / 950.0), delta=1e-9)
        self.assertEqual(pose.boil_tick, math.floor(t_ms / 110.0))

    def test_step_back_in_time_is_rejected(self) -> None:
        driver = _Driver(self)
        driver.run(0.1)
        with self.assertRaises(ValueError):
            puppet_step(driver.puppet, driver.now - STEP_S)
        puppet_step(driver.puppet, driver.now)  # Zwilling: gleiche Zeit

    def test_long_pause_stays_finite(self) -> None:
        """Nach einer Pause (Panel verdeckt) geht es ohne Sprung ins Unendliche weiter."""
        driver = _Driver(self)
        driver.answer(SPOKEN, thinking_s=0.3)
        driver.run(1.0)
        driver.now += 30.0
        driver.run(0.5)


if __name__ == "__main__":
    unittest.main()
