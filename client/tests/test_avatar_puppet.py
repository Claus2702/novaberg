"""Zeugen für die Puppe des Avatars und die Umsetzung einer Antwort in eine Äußerung.

Ohne GTK und ohne Cairo: Die Zeit treiben die Zeugen selbst, in Schritten von
10 ms, den Zufall der Blinzelabstände setzen sie fest.

Die Zuordnung Name → Sektor steht hier als eigene Tabelle, abgeschrieben aus den
Schlüsselbildern des Prototyps (`hi` und `lo` je Sektor), nicht aus dem Modul
gelesen: Eine falsche Zuordnung zeigte still ein falsches Gesicht.
"""

import math
import random
import unittest
from dataclasses import fields

from avatar.expression import face_target
from avatar.face import NEUTRAL, FaceState
from avatar.pose import Pose
from avatar.puppet import (
    SECTOR_BY_NAME,
    Puppet,
    Utterance,
    new_puppet,
    puppet_cue,
    puppet_step,
    utterance_from_turn,
)
from avatar.speech import mouth_state_combine, speech_timeline, text_to_phonemes

STEP_S = 0.01
LOGGER = "avatar.puppet"

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


def _turn(emotion: object = "freude", arousal: object = 0.5, text: object = "Hallo") -> dict:
    """Eine Antwort, wie sie beim Client ankommt."""
    return {"nova_emotion": emotion, "nova_arousal": arousal, "antwort": text}


def _channels(face: FaceState) -> tuple[float, ...]:
    """Alle Kanäle eines Gesichts in fester Reihenfolge."""
    return tuple(getattr(face, f.name) for f in fields(FaceState))


class _Driver:
    """Treibt eine Puppe in festen Schritten und prüft jede Pose."""

    def __init__(self, case: unittest.TestCase, seed: int = 7, start: float = 100.0) -> None:
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


class CueTest(unittest.TestCase):
    """Neues Ziel: am Ziel nach 2 s, der Mund erst nach 150 ms unterwegs."""

    def _cued(self) -> tuple[_Driver, Pose]:
        driver = _Driver(self)
        driver.run(0.5)
        before = driver.step()
        puppet_cue(driver.puppet, Utterance(1, 1.0, ""), driver.now)
        return driver, before

    def _target_pose_face(self, driver: _Driver) -> FaceState:
        face, _ = mouth_state_combine(face_target(1, 1.0), driver.puppet.speech)
        return face

    def test_face_reaches_the_target_after_2_s(self) -> None:
        driver, _ = self._cued()
        pose = driver.run(2.0)[-1]
        target = self._target_pose_face(driver)
        names = [f.name for f in fields(FaceState)]
        triples = zip(_channels(pose.face), _channels(target), _channels(NEUTRAL), strict=True)
        for name, (got, want, rest) in zip(names, triples, strict=True):
            tolerance = 0.01 * max(1.0, abs(want - rest))
            self.assertLessEqual(abs(got - want), tolerance, name)

    def test_face_is_not_yet_at_the_target_after_half_a_second(self) -> None:
        """Zwilling: die Toleranz trennt — eine halbe Sekunde reicht nicht."""
        driver, _ = self._cued()
        pose = driver.run(0.5)[-1]
        target = self._target_pose_face(driver)
        self.assertGreater(abs(pose.face.mouth_curve - target.mouth_curve), 1.0)
        self.assertGreater(abs(pose.face.eye_open - target.eye_open), 0.01)

    def test_mouth_waits_150_ms_while_eyes_follow_at_once(self) -> None:
        driver, before = self._cued()
        poses = driver.run(0.14)
        self.assertGreater(abs(poses[-1].face.eye_open - before.face.eye_open), 0.02)
        for pose in poses:
            self.assertAlmostEqual(pose.face.mouth_curve, before.face.mouth_curve, delta=1e-9)
            self.assertAlmostEqual(pose.face.mouth_open, before.face.mouth_open, delta=1e-9)

    def test_mouth_moves_after_150_ms(self) -> None:
        """Zwilling des Versatzes: danach ist der Mund unterwegs."""
        driver, before = self._cued()
        pose = driver.run(0.3)[-1]
        self.assertGreater(pose.face.mouth_curve - before.face.mouth_curve, 1.0)

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


class SpeechTest(unittest.TestCase):
    """Der Text wird gesprochen: Sprechanteil hoch, Öffnung wechselt, danach Ruhe."""

    def _speaking(self, text: str) -> tuple[_Driver, float]:
        driver = _Driver(self)
        driver.run(0.2)
        cue_at = driver.now
        puppet_cue(driver.puppet, Utterance(None, 0.0, text), cue_at)
        _, end_ms = speech_timeline(text_to_phonemes(text))
        return driver, cue_at + end_ms / 1000.0

    def test_text_is_spoken_while_it_lasts(self) -> None:
        driver, end = self._speaking(SPOKEN)
        self.assertGreater(end - driver.now, 1.0)  # der Satz trägt mehr als eine Sekunde
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

    def test_empty_text_does_not_speak(self) -> None:
        """Zwilling: ohne Text bleibt der Sprechanteil null."""
        driver = _Driver(self)
        puppet_cue(driver.puppet, Utterance(None, 0.0, "   "), driver.now)
        driver.run(0.5)
        self.assertFalse(driver.puppet.speech.active)
        self.assertLess(driver.puppet.speech.blend, 1e-9)

    def test_new_text_mid_speech_starts_without_a_jump(self) -> None:
        driver, _ = self._speaking(SPOKEN)
        before = driver.run(0.4)[-1]
        puppet_cue(driver.puppet, Utterance(1, 0.9, "Neue Worte."), driver.now)
        same_time = puppet_step(driver.puppet, driver.now)
        names = [f.name for f in fields(FaceState)]
        pairs = zip(_channels(before.face), _channels(same_time.face), strict=True)
        for name, (a, b) in zip(names, pairs, strict=True):
            self.assertAlmostEqual(a, b, delta=1e-9, msg=name)
        self.assertAlmostEqual(before.tongue, same_time.tongue, delta=1e-9)

    def test_new_text_mid_speech_takes_over(self) -> None:
        """Zwilling: der neue Text gilt — sein Beginn ist die Zeit der neuen Äußerung."""
        driver, _ = self._speaking(SPOKEN)
        driver.run(0.4)
        cue_at = driver.now
        puppet_cue(driver.puppet, Utterance(1, 0.9, "Neue Worte."), cue_at)
        driver.run(0.1)
        self.assertEqual(driver.puppet.speech.start_ms, cue_at * 1000.0)
        self.assertTrue(driver.puppet.speech.active)


class BlinkTest(unittest.TestCase):
    """Blinzeln: das erste nach 1,8 s, 160 ms lang, dann alle 2,4–5,6 s; mit Seed gleich."""

    def _blinks(self, seed: int, seconds: float = 15.0) -> list[float]:
        driver = _Driver(self, seed=seed)
        return [pose.blink for pose in driver.run(seconds)]

    @staticmethod
    def _onsets(blinks: list[float]) -> list[float]:
        """Zeiten in s, ab denen das Auge sich schließt (erstes Bild mit blink < 1)."""
        return [
            (i + 1) * STEP_S
            for i in range(1, len(blinks))
            if blinks[i] < 1.0 and blinks[i - 1] == 1.0
        ]

    def test_first_blink_at_1_8_s(self) -> None:
        blinks = self._blinks(7, 2.2)
        self.assertTrue(all(b == 1.0 for b in blinks[: round(1.79 / STEP_S)]))
        window = blinks[round(1.85 / STEP_S): round(1.95 / STEP_S)]
        self.assertLess(min(window), 0.5)
        self.assertEqual(blinks[-1], 1.0)  # nach 160 ms wieder offen

    def test_blinks_repeat_within_2_4_to_5_6_s(self) -> None:
        onsets = self._onsets(self._blinks(7, 30.0))
        self.assertGreaterEqual(len(onsets), 4)
        for earlier, later in zip(onsets, onsets[1:], strict=False):
            gap = later - earlier
            self.assertGreaterEqual(gap, 0.16 + 2.4 - STEP_S)
            self.assertLessEqual(gap, 0.16 + 5.6 + 2 * STEP_S)

    def test_same_seed_blinks_the_same(self) -> None:
        self.assertEqual(self._blinks(7), self._blinks(7))

    def test_other_seed_blinks_otherwise(self) -> None:
        """Zwilling: der Zufall wirkt — ein anderer Seed ergibt andere Abstände."""
        self.assertNotEqual(self._blinks(7), self._blinks(8))


class StepTest(unittest.TestCase):
    """Atem, Takt und Zeit."""

    def test_breath_and_boil_tick_follow_the_time_since_the_first_frame(self) -> None:
        driver = _Driver(self)
        pose = driver.run(1.0)[-1]
        t_ms = (driver.now - 100.0) * 1000.0
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
        puppet_cue(driver.puppet, Utterance(3, 1.0, SPOKEN), driver.now)
        driver.run(0.3)
        driver.now += 30.0
        driver.run(0.5)


if __name__ == "__main__":
    unittest.main()
