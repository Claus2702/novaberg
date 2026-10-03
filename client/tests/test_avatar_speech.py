"""Zeugen für das Sprechen des Avatars: Laute, Zeiten und Mundkanäle aus einem Text.

Die Referenzwerte unter `avatar_reference/speech.json` sind aus dem Prototyp erzeugt
(vier synthetische Sätze: Laute, Zeitachse, Ziele der Koartikulation alle 20 ms,
Federschritte bei 60 Bildern je Sekunde, für Satz 1 der Mund zusammen mit Freude bei
Arousal 0,85) und werden nicht von Hand geändert. Eine Abweichung wäre im Bild still:
Der Mund bewegte sich nur ein wenig anders.

Toleranz 1e-9 in den Einheiten der Kanäle (Pixel, 0..1, ms): Die Referenz ist auf
1e-9 gerundet, das trägt bis 5e-10 bei. Python und der Prototyp rechnen dieselben
Operationen in derselben Reihenfolge mit IEEE-754-Doppelgenauigkeit; Addition,
Multiplikation und Division sind dort exakt gleich, nur `exp` darf um eine Einheit der
letzten Stelle abweichen (bei Werten bis 72 Pixel rund 1e-14). Die kleinste fachliche
Abweichung — eine Lücke von 30 statt 25 ms, eine andere Reichweite der Öffnung — liegt
bei 1e-3 und mehr. Laute, Dauern, Amplituden und Bezeichnungen werden exakt verglichen.
"""

import ast
import json
import math
import unittest
from pathlib import Path

from avatar import speech, speech_tables
from avatar.expression import face_target
from avatar.face import NEUTRAL, PROTOTYPE_KEYS
from avatar.speech import (
    SILENT,
    SPEECH_PROTOTYPE_KEYS,
    Phone,
    SpeechChannels,
    SpeechState,
    coart_target,
    mouth_state_combine,
    speech_step,
    speech_timeline,
    start_speech,
    text_to_phonemes,
    word_to_phonemes,
)
from avatar.speech_tables import SPEECH_KEYS

TOLERANCE = 1e-9
FPS = 60
REFERENCE_PATH = Path(__file__).parent / "avatar_reference" / "speech.json"
ALLOWED_IMPORTS = frozenset({
    "collections.abc", "dataclasses", "logging", "math", "re", "types",
    "avatar.face", "avatar.speech_tables",
})


def _load_reference() -> dict:
    """Die Referenzwerte des Prototyps."""
    with REFERENCE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _run(text: str, extra_ms: float = 500.0) -> list[tuple[float, SpeechState]]:
    """Schritte wie im Prototyp: ab 0 ms, 60 Bilder je Sekunde, bis `extra_ms` nach dem Ende."""
    state = start_speech(SILENT, text, 0.0)
    steps = []
    i = 0
    while i * 1000 / FPS <= state.end_ms + extra_ms:
        now = i * 1000 / FPS
        state = speech_step(state, now, 1 / FPS)
        steps.append((now, state))
        i += 1
    return steps


def _off(value: float, expected: float) -> bool:
    """Wahr, wenn `value` außerhalb der Toleranz liegt — auch, wenn es keine Zahl ist."""
    return not abs(value - expected) <= TOLERANCE


def _channel_mismatches(channels: SpeechChannels, expected: dict, where: str) -> list[str]:
    """Je Sprechkanal außerhalb der Toleranz eine Zeile."""
    return [
        f"{where} {key}: {getattr(channels, name)!r} statt {expected[key]!r}"
        for name, key in SPEECH_PROTOTYPE_KEYS.items()
        if _off(getattr(channels, name), expected[key])
    ]


def _imports(module: object) -> set[str]:
    """Die Namen aller Module, die die Quelldatei von `module` importiert."""
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module)
    return names


class ReferenceTest(unittest.TestCase):
    """Gleichheit mit dem Prototyp für alle vier Sätze."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.reference = _load_reference()
        cls.sentences = cls.reference["saetze"]
        cls.steps = {s["text"]: _run(s["text"]) for s in cls.sentences}

    def test_channels_and_settings_match_the_prototype(self) -> None:
        self.assertEqual(list(SPEECH_KEYS), self.reference["kanaele"])
        self.assertEqual(list(SPEECH_PROTOTYPE_KEYS.values()), self.reference["kanaele"])
        self.assertEqual(self.reference["sprechtempo"], 1.0)
        self.assertEqual(self.reference["bilder_je_sekunde"], FPS)
        self.assertEqual(len(self.sentences), 4)

    def test_phonemes_match_exactly(self) -> None:
        for sentence in self.sentences:
            with self.subTest(text=sentence["text"]):
                phones = text_to_phonemes(sentence["text"])
                got = [(p.code, p.duration_ms, p.amplitude) for p in phones]
                expected = [(p["v"], p["ms"], p["amp"]) for p in sentence["laute"]]
                self.assertEqual(got, expected)

    def test_segments_and_end_match(self) -> None:
        for sentence in self.sentences:
            with self.subTest(text=sentence["text"]):
                segments, end_ms = speech_timeline(text_to_phonemes(sentence["text"]))
                reference = sentence["segmente"]
                self.assertEqual([s.code for s in segments], [s["v"] for s in reference])
                bad = [
                    f"{index} {key}: {value!r} statt {expected[key]!r}"
                    for index, (segment, expected) in enumerate(zip(segments, reference, strict=True))
                    for key, value in (
                        ("t0", segment.start_ms), ("t1", segment.end_ms), ("c", segment.center_ms),
                        ("d", segment.duration_ms), ("amp", segment.amplitude),
                    )
                    if _off(value, expected[key])
                ]
                self.assertEqual(bad, [])
                self.assertFalse(_off(end_ms, sentence["ende_ms"]), end_ms)

    def test_targets_match_per_channel_and_label(self) -> None:
        for sentence in self.sentences:
            with self.subTest(text=sentence["text"]):
                segments, _ = speech_timeline(text_to_phonemes(sentence["text"]))
                self.assertGreater(len(sentence["ziele"]), 100)
                bad, labels = [], []
                for entry in sentence["ziele"]:
                    target, label = coart_target(segments, entry["t"])
                    bad += _channel_mismatches(target, entry["target"], f"t={entry['t']}")
                    if label != entry["label"]:
                        labels.append(f"t={entry['t']}: {label!r} statt {entry['label']!r}")
                self.assertEqual(bad[:10], [])
                self.assertEqual(labels[:10], [])

    def test_steps_match_per_channel_and_blend(self) -> None:
        for sentence in self.sentences:
            with self.subTest(text=sentence["text"]):
                steps = self.steps[sentence["text"]]
                self.assertEqual(len(steps), len(sentence["schritte"]))
                bad = []
                for (now, state), entry in zip(steps, sentence["schritte"], strict=True):
                    where = f"t={entry['t']}"
                    if _off(now, entry["t"]):
                        bad.append(f"{where}: Zeit {now!r}")
                    bad += _channel_mismatches(state.current, entry["cur"], where)
                    if _off(state.blend, entry["blend"]):
                        bad.append(f"{where} blend: {state.blend!r} statt {entry['blend']!r}")
                self.assertEqual(bad[:10], [])

    def test_mouth_with_joy_matches_for_sentence_one(self) -> None:
        sentence = self.sentences[0]
        mixed = sentence["gemischt"]
        joy = face_target(mixed["sektor"], mixed["arousal"])
        samples = self.steps[sentence["text"]][::6]
        self.assertEqual(len(samples), len(mixed["werte"]))
        self.assertGreater(len(samples), 20)
        bad = []
        for (now, state), entry in zip(samples, mixed["werte"], strict=True):
            face, tongue = mouth_state_combine(joy, state)
            where = f"t={entry['t']}"
            self.assertFalse(_off(now, entry["t"]), where)
            bad += [
                f"{where} {key}: {getattr(face, name)!r} statt {entry['face'][key]!r}"
                for name, key in PROTOTYPE_KEYS.items()
                if _off(getattr(face, name), entry["face"][key])
            ]
            if _off(tongue, entry["face"].get("tng", 0.0)):
                bad.append(f"{where} tng: {tongue!r} statt {entry['face'].get('tng')!r}")
        self.assertEqual(bad[:10], [])


class BehaviourTest(unittest.TestCase):
    """Randfälle, Lippenschluss und das Ausblenden nach dem Ende."""

    def test_empty_text_is_only_the_closing_pause(self) -> None:
        # Der Prototyp hängt jedem Text eine Pause an; ohne Text bleibt nur sie: 300 ms Ruhe.
        self.assertEqual(text_to_phonemes(""), (Phone("REST", 300.0, 1.0),))
        segments, end_ms = speech_timeline(text_to_phonemes(""))
        self.assertEqual(end_ms, 300.0)
        target, label = coart_target(segments, 150.0)
        self.assertEqual(label, "REST")
        self.assertEqual(target, SpeechChannels(*(0.0 for _ in SPEECH_KEYS)))
        last = _run("")[-1][1]
        self.assertFalse(last.active)
        self.assertEqual(last.current.mouth_open, 0.0)

    def test_single_vowel_opens_the_mouth(self) -> None:
        # Zwilling zum leeren Text: derselbe Weg mit einem Laut öffnet den Mund.
        segments, _ = speech_timeline(text_to_phonemes("a"))
        self.assertEqual([s.code for s in segments], ["a:", "REST"])
        target, label = coart_target(segments, segments[0].center_ms)
        self.assertEqual(label, "a:")
        self.assertGreater(target.mouth_open, 10.0)

    def test_punctuation_only_is_one_pause_per_mark(self) -> None:
        # Jedes Satzzeichen ist eine Pause, dazu die Schlusspause; Sternchen sind kein Laut.
        self.assertEqual([p.code for p in text_to_phonemes("?!*")], ["REST", "REST", "REST"])
        _, end_ms = speech_timeline(text_to_phonemes("?!*"))
        self.assertEqual(end_ms, 900.0)
        self.assertFalse(_run("?!")[-1][1].active)

    def test_lips_close_in_the_middle_of_m_b_p(self) -> None:
        checked = 0
        for sentence in _load_reference()["saetze"]:
            segments, _ = speech_timeline(text_to_phonemes(sentence["text"]))
            for segment in segments:
                if segment.code in speech_tables.BILABIAL_CODES:
                    target, _ = coart_target(segments, segment.center_ms)
                    self.assertGreaterEqual(target.lip_press, 0.9, (sentence["text"], segment))
                    checked += 1
        self.assertGreaterEqual(checked, 8)

    def test_vowel_between_m_stays_open(self) -> None:
        # Zwilling zum Lippenschluss: In der Mitte des a: zwischen zwei m pressen die Lippen nicht.
        segments, _ = speech_timeline(text_to_phonemes("Mama"))
        self.assertEqual([s.code for s in segments[:3]], ["m", "a:", "m"])
        target, _ = coart_target(segments, segments[1].center_ms)
        self.assertLess(target.lip_press, 0.9)

    def test_speech_layer_fades_out_after_the_end(self) -> None:
        steps = _run("Mama baut Papas Boot!", extra_ms=2000.0)
        last = steps[-1][1]
        self.assertFalse(last.active)
        self.assertLess(last.blend, 1e-6)
        _, tongue = mouth_state_combine(NEUTRAL, last)
        self.assertEqual(tongue, 0.0)

    def test_speech_layer_is_on_while_speaking(self) -> None:
        # Zwilling zum Ausblenden: mitten in der Äußerung ist die Sprechschicht fast ganz da.
        steps = _run("Mama baut Papas Boot!", extra_ms=2000.0)
        middle = steps[len(steps) // 4][1]
        self.assertTrue(middle.active)
        self.assertGreater(middle.blend, 0.9)

    def test_rate_scales_the_timeline(self) -> None:
        phones = text_to_phonemes("Hallo, ich bin Nova.")
        _, normal = speech_timeline(phones)
        _, fast = speech_timeline(phones, 2.0)
        self.assertAlmostEqual(fast, normal / 2, delta=TOLERANCE)

    def test_zero_step_keeps_the_channels(self) -> None:
        state = _run("Mama")[10][1]
        same = speech_step(state, 200.0, 0.0)
        for name in SPEECH_PROTOTYPE_KEYS:
            before, after = getattr(state.current, name), getattr(same.current, name)
            self.assertAlmostEqual(after, before, delta=1e-12, msg=name)

    def test_no_clock_no_randomness_no_gui(self) -> None:
        for module in (speech, speech_tables):
            with self.subTest(module=module.__name__):
                self.assertEqual(_imports(module) - ALLOWED_IMPORTS, set())

    def test_import_scan_finds_imports(self) -> None:
        # Zwilling zum Importverbot: Der Scan findet, was dasteht.
        self.assertIn("math", _imports(speech))
        self.assertIn("avatar.speech_tables", _imports(speech))


class RejectionTest(unittest.TestCase):
    """Falsche Eingaben werden laut abgewiesen; je Abweisung ein Zwilling, der durchgeht."""

    def test_text_that_is_no_str_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            text_to_phonemes(None)
        self.assertEqual(len(text_to_phonemes("ja")), 3)

    def test_word_with_capitals_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            word_to_phonemes("Hallo")
        self.assertEqual([p.code for p in word_to_phonemes("hallo")], ["h", "a", "l", "o:"])

    def test_bad_rate_is_rejected(self) -> None:
        phones = text_to_phonemes("ja")
        for rate in (0, -1.0, math.nan, math.inf):
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                speech_timeline(phones, rate)
        with self.assertRaises(TypeError):
            speech_timeline(phones, True)
        self.assertGreater(speech_timeline(phones, 0.5)[1], 0)

    def test_unknown_phone_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            speech_timeline((Phone("Q", 50.0, 1.0),))
        self.assertEqual(speech_timeline((Phone("a", 50.0, 1.0),))[1], 50.0)

    def test_negative_or_bad_step_is_rejected(self) -> None:
        state = start_speech(SILENT, "ja", 0.0)
        with self.assertRaises(ValueError):
            speech_step(state, 10.0, -0.01)
        with self.assertRaises(ValueError):
            speech_step(state, math.nan, 0.01)
        with self.assertRaises(TypeError):
            speech_step({"active": True}, 10.0, 0.01)
        self.assertTrue(speech_step(state, 10.0, 0.01).active)

    def test_time_that_is_not_finite_is_rejected_by_coart(self) -> None:
        segments, _ = speech_timeline(text_to_phonemes("ja"))
        with self.assertRaises(ValueError):
            coart_target(segments, math.inf)
        self.assertEqual(coart_target(segments, 0.0)[1], "j")

    def test_combine_without_face_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            mouth_state_combine({"mo": 0.0}, SILENT)
        face, tongue = mouth_state_combine(NEUTRAL, SILENT)
        self.assertEqual(face, NEUTRAL)
        self.assertEqual(tongue, 0.0)


if __name__ == "__main__":
    unittest.main()
