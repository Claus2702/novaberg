"""Zeugen des Untertitels: Fenster der Wörter, Tafeln, Zustand zu einer Zeit, Markup, Puppe.

Ohne GTK: geprüft wird `avatar.subtitle` und, was die Puppe daraus hält; das Panel ruft nur
`puppet_subtitle` und `subtitle_markup`.
"""

import unittest

from avatar.idle import TurnBegins
from avatar.idle_catalog import IdleState
from avatar.puppet import Utterance, puppet_cue, puppet_event, puppet_subtitle, utterance_from_turn
from avatar.speech import GAP_CODE, REST_CODE, speech_timeline, text_to_phonemes, text_to_words
from avatar.subtitle import (
    HOLD_MS,
    Subtitle,
    SubtitleWord,
    subtitle_at,
    subtitle_boards,
    subtitle_markup,
    subtitle_run,
    subtitle_words,
)
from tests.test_avatar_puppet import STEP_S, _Driver, _turn

TEXT = "„Gurken und Zucchini! Na siehst du mal!“"
OTHER = "Neue Worte."


def _plain(*texts: str) -> tuple[SubtitleWord, ...]:
    """Wörter ohne Fenster, für die Tafeln."""
    return tuple(SubtitleWord(text, None, None) for text in texts)


def _board_texts(text: str) -> list[tuple[str, ...]]:
    """Die Tafeln eines Texts als Wörter."""
    words = _plain(*text.split())
    return [tuple(w.text for w in words[a:b]) for a, b in subtitle_boards(words)]


class WordsTest(unittest.TestCase):
    """Die Zerlegung in Wörter ist die des Mundes."""

    def test_the_words_carry_their_spelling(self) -> None:
        words = text_to_words(TEXT)
        self.assertEqual([w.text for w in words], TEXT.split())
        self.assertEqual(words[0].text, "„Gurken")
        self.assertEqual(words[2].text, "Zucchini!")

    def test_the_phones_of_the_words_are_the_phones_of_the_mouth_without_the_gaps(self) -> None:
        flat = [p for w in text_to_words(TEXT) for p in w.phones]
        flat.append([p for p in text_to_phonemes(TEXT) if p.code == REST_CODE][-1])
        mouth = [p for p in text_to_phonemes(TEXT) if p.code != GAP_CODE]
        self.assertEqual(flat, mouth)

    def test_twin_a_gap_is_in_the_mouth_but_in_no_word(self) -> None:
        self.assertTrue(any(p.code == GAP_CODE for p in text_to_phonemes(TEXT)))
        self.assertFalse(any(p.code == GAP_CODE for w in text_to_words(TEXT) for p in w.phones))

    def test_a_text_without_words_gives_none(self) -> None:
        self.assertEqual(text_to_words(" \n "), ())

    def test_a_text_that_is_no_str_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            text_to_words(None)  # type: ignore[arg-type]


class WindowsTest(unittest.TestCase):
    """Die Fenster liegen auf der Zeitachse des Mundes."""

    def setUp(self) -> None:
        self.words = subtitle_words(TEXT)
        self.segments, self.end_ms = speech_timeline(text_to_phonemes(TEXT))

    def test_the_words_carry_their_spelling(self) -> None:
        self.assertEqual([w.text for w in self.words], ["„Gurken", "und", "Zucchini!", "Na",
                                                         "siehst", "du", "mal!“"])

    def test_windows_ascend_and_do_not_overlap(self) -> None:
        windows = [(w.start_ms, w.end_ms) for w in self.words if w.start_ms is not None]
        self.assertEqual(len(windows), len(self.words))
        for (_, end), (start, _) in zip(windows, windows[1:], strict=False):
            self.assertLessEqual(end, start)
        self.assertTrue(all(start < end for start, end in windows))

    def test_every_sound_but_the_pauses_lies_in_exactly_one_window(self) -> None:
        sounds = [s for s in self.segments if s.code != REST_CODE]
        self.assertGreater(len(sounds), 20)
        for segment in sounds:
            holding = [
                w for w in self.words
                if w.start_ms <= segment.start_ms and segment.end_ms <= w.end_ms
            ]
            self.assertEqual(len(holding), 1, f"{segment.code} bei {segment.start_ms}")

    def test_the_m_of_mal_lies_in_the_window_of_mal(self) -> None:
        (m,) = [s for s in self.segments if s.code == "m"]
        owners = [w.text for w in self.words if w.start_ms <= m.start_ms < w.end_ms]
        self.assertEqual(owners, ["mal!“"])

    def test_twin_a_window_does_not_cover_the_pause_of_its_punctuation(self) -> None:
        zucchini = self.words[2]
        pauses = [s for s in self.segments if s.code == REST_CODE]
        after = [s for s in pauses if s.start_ms == zucchini.end_ms]
        self.assertEqual(len(after), 1)  # die Pause von „!“ beginnt, wo das Fenster endet

    def test_a_one_word_text_spans_first_to_last_sound(self) -> None:
        segments, _ = speech_timeline(text_to_phonemes("Hallo"))
        sounds = [s for s in segments if s.code != REST_CODE]
        (word,) = subtitle_words("Hallo")
        self.assertEqual((word.start_ms, word.end_ms), (sounds[0].start_ms, sounds[-1].end_ms))

    def test_a_word_without_a_sound_has_no_window_but_its_neighbours_do(self) -> None:
        words = subtitle_words("Es sind 42 Sterne")
        self.assertEqual([w.text for w in words], ["Es", "sind", "42", "Sterne"])
        self.assertEqual(
            [w.start_ms is None for w in words], [False, False, True, False])

    def test_a_word_without_a_sound_is_never_underlined(self) -> None:
        run = subtitle_run("Es sind 42 Sterne", 0.0)
        shown = set()
        for t in range(0, int(run.duration_ms + HOLD_MS), 5):
            subtitle = subtitle_at(run, float(t))
            if subtitle is not None and subtitle.spoken is not None:
                shown.add(subtitle.words[subtitle.spoken])
        self.assertEqual(shown, {"Es", "sind", "Sterne"})

    def test_a_dash_has_no_window(self) -> None:
        words = subtitle_words("Ja – nein")
        self.assertIsNone(words[1].start_ms)
        self.assertIsNotNone(words[2].start_ms)

    def test_a_hyphenated_word_is_one_window(self) -> None:
        words = subtitle_words("Garten-Fantasie ist schön")
        self.assertEqual(words[0].text, "Garten-Fantasie")
        self.assertLessEqual(words[0].end_ms, words[1].start_ms)


class BoardsTest(unittest.TestCase):
    """Tafeln: höchstens 80 Zeichen, nach einem Satzende eine neue."""

    def test_no_board_is_longer_than_80_characters(self) -> None:
        boards = _board_texts(" ".join(["wort"] * 50))
        self.assertGreater(len(boards), 2)
        self.assertTrue(all(len(" ".join(board)) <= 80 for board in boards))
        self.assertEqual(len(boards[0]), 16)  # 16 · 4 + 15 = 79; ein 17. Wort ergäbe 84

    def test_a_sentence_end_ends_a_board(self) -> None:
        boards = _board_texts("Hallo Welt. Wie geht es dir? Gut!“ Danke")
        self.assertEqual(
            boards,
            [("Hallo", "Welt."), ("Wie", "geht", "es", "dir?"), ("Gut!“",), ("Danke",)],
        )

    def test_twin_without_a_sentence_end_the_words_stay_on_one_board(self) -> None:
        self.assertEqual(len(_board_texts("Hallo Welt wie geht es dir Gut Danke")), 1)

    def test_an_ellipsis_and_a_closing_bracket_end_a_board(self) -> None:
        boards = _board_texts("Na ja… (sagt sie.) Weiter")
        self.assertEqual(boards, [("Na", "ja…"), ("(sagt", "sie.)"), ("Weiter",)])

    def test_a_comma_does_not_end_a_board(self) -> None:
        self.assertEqual(len(_board_texts("Hallo, Welt, wie geht es")), 1)

    def test_a_word_longer_than_a_board_stands_alone(self) -> None:
        long = "langwort" * 13
        self.assertGreater(len(long), 80)
        boards = _board_texts(f"Hallo {long} Ende")
        self.assertEqual(boards, [("Hallo",), (long,), ("Ende",)])

    def test_all_boards_together_are_all_words_in_order_without_a_double(self) -> None:
        words = subtitle_words(TEXT * 3)
        covered = [i for a, b in subtitle_boards(words) for i in range(a, b)]
        self.assertEqual(covered, list(range(len(words))))

    def test_no_words_give_no_boards(self) -> None:
        self.assertEqual(subtitle_boards(()), ())

    def test_a_limit_below_one_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            subtitle_boards(_plain("a"), 0)


class AtTest(unittest.TestCase):
    """Der Zustand zu einer Zeit."""

    def setUp(self) -> None:
        self.run = subtitle_run(TEXT, 5000.0)
        self.words = self.run.words

    def _at(self, t_ms: float) -> Subtitle | None:
        return subtitle_at(self.run, self.run.start_ms + t_ms)

    def _spoken(self, t_ms: float) -> str | None:
        subtitle = self._at(t_ms)
        assert subtitle is not None
        return None if subtitle.spoken is None else subtitle.words[subtitle.spoken]

    def test_in_each_window_that_word_is_underlined(self) -> None:
        for word in self.words:
            self.assertEqual(self._spoken((word.start_ms + word.end_ms) / 2), word.text)

    def test_between_two_windows_the_last_word_stays_underlined(self) -> None:
        und, zucchini = self.words[1], self.words[2]
        self.assertLess(und.end_ms, zucchini.start_ms)
        self.assertEqual(self._spoken(und.end_ms + 1.0), "und")
        self.assertEqual(self._spoken(zucchini.start_ms - 1.0), "und")

    def test_the_board_changes_with_the_first_window_of_the_next(self) -> None:
        na = self.words[3]
        before, after = self._at(na.start_ms - 0.5), self._at(na.start_ms)
        self.assertEqual(before.words, ("„Gurken", "und", "Zucchini!"))
        self.assertEqual(before.spoken, 2)
        self.assertEqual(after.words, ("Na", "siehst", "du", "mal!“"))
        self.assertEqual(after.spoken, 0)

    def test_before_the_first_window_the_first_board_shows_nothing_underlined(self) -> None:
        run = subtitle_run(". Hallo", 0.0)
        first = run.words[1].start_ms
        self.assertGreater(first, 0.0)
        early = subtitle_at(run, first - 0.5)
        self.assertEqual((early.words, early.spoken), ((".",), None))
        late = subtitle_at(run, first)
        self.assertEqual((late.words, late.spoken), (("Hallo",), 0))

    def test_after_the_end_the_last_board_stays_without_an_underline(self) -> None:
        subtitle = self._at(self.run.duration_ms)
        self.assertEqual(subtitle.words, ("Na", "siehst", "du", "mal!“"))
        self.assertIsNone(subtitle.spoken)

    def test_just_before_the_end_the_last_word_is_still_underlined(self) -> None:
        self.assertEqual(self._spoken(self.run.duration_ms - 0.5), "mal!“")

    def test_the_hold_ends_at_one_and_a_half_seconds(self) -> None:
        run = subtitle_run(TEXT, 0.0)
        end = run.duration_ms
        self.assertEqual(HOLD_MS, 1500.0)
        self.assertIsNotNone(subtitle_at(run, end + 1499.0))
        self.assertIsNone(subtitle_at(run, end + 1500.0))

    def test_a_time_before_the_beginning_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            subtitle_at(self.run, self.run.start_ms - 1.0)

    def test_something_that_is_no_run_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            subtitle_at(None, 0.0)  # type: ignore[arg-type]

    def test_a_text_without_a_word_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            subtitle_run("  ", 0.0)


class MarkupTest(unittest.TestCase):
    """Das Markup: ein Unterstrich um das gesprochene Wort, der Text escaped."""

    def test_exactly_one_underline_around_the_spoken_word(self) -> None:
        markup = subtitle_markup(Subtitle(("Na", "siehst", "du"), 1))
        self.assertEqual(markup, "Na <u>siehst</u> du")
        self.assertEqual((markup.count("<u>"), markup.count("</u>")), (1, 1))

    def test_without_a_spoken_word_there_is_no_underline(self) -> None:
        markup = subtitle_markup(Subtitle(("Na", "siehst"), None))
        self.assertEqual(markup, "Na siehst")
        self.assertNotIn("<u>", markup)

    def test_nothing_gives_the_empty_text(self) -> None:
        self.assertEqual(subtitle_markup(None), "")

    def test_the_text_is_escaped_so_that_it_forms_no_markup(self) -> None:
        run = subtitle_run("a < b & c > <u>d", 0.0)
        for t in range(0, int(run.duration_ms), 10):
            markup = subtitle_markup(subtitle_at(run, float(t)))
            bare = markup.replace("<u>", "").replace("</u>", "")
            self.assertNotIn("<", bare)
            self.assertNotIn(">", bare)
            self.assertNotIn("& ", bare)
        self.assertEqual(
            subtitle_markup(subtitle_at(run, 0.0)),
            "<u>a</u> &lt; b &amp; c &gt; &lt;u&gt;d",
        )

    def test_twin_an_underlined_word_is_escaped_too(self) -> None:
        self.assertEqual(subtitle_markup(Subtitle(("a", "<"), 1)), "a <u>&lt;</u>")

    def test_a_word_outside_the_board_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            subtitle_markup(Subtitle(("a",), 1))


class PuppetSubtitleTest(unittest.TestCase):
    """Die Puppe hält den Untertitel der Antwort, die sie spricht."""

    def _speaking(self, text: str) -> _Driver:
        """Eine Puppe im ersten Schritt der Antwort mit `text`."""
        driver = _Driver(self)
        driver.run(0.2)
        driver.answer(text)
        driver.until_answer()
        return driver

    def _spoken(self, driver: _Driver) -> str | None:
        subtitle = puppet_subtitle(driver.puppet, driver.now)
        assert subtitle is not None
        return None if subtitle.spoken is None else subtitle.words[subtitle.spoken]

    def test_before_any_answer_there_is_no_subtitle(self) -> None:
        driver = _Driver(self)
        driver.run(0.3)
        self.assertIsNone(puppet_subtitle(driver.puppet, driver.now))

    def test_at_the_m_of_mal_the_word_mal_is_underlined(self) -> None:
        driver = self._speaking(TEXT)
        speech = driver.puppet.speech
        (m,) = [s for s in speech.segments if s.code == "m"]
        while driver.now * 1000.0 < speech.start_ms + m.start_ms:
            driver.step()
        self.assertLess(driver.now * 1000.0, speech.start_ms + m.end_ms)
        self.assertEqual(self._spoken(driver), "mal!“")

    def test_twin_early_in_the_answer_another_word_is_underlined(self) -> None:
        driver = self._speaking(TEXT)
        self.assertNotEqual(self._spoken(driver), "mal!“")

    def test_the_subtitle_follows_the_clock_of_the_mouth(self) -> None:
        driver = self._speaking(TEXT)
        start = driver.puppet.speech.start_ms
        run = subtitle_run(TEXT, start)
        for _ in range(150):
            driver.step()
            self.assertEqual(
                puppet_subtitle(driver.puppet, driver.now), subtitle_at(run, driver.now * 1000.0))

    def test_a_new_answer_replaces_the_subtitle(self) -> None:
        driver = self._speaking(TEXT)
        driver.run(0.4)
        self.assertIsNotNone(puppet_subtitle(driver.puppet, driver.now))
        puppet_cue(driver.puppet, Utterance(1, 0.9, OTHER), driver.now)
        driver.run(0.1)
        subtitle = puppet_subtitle(driver.puppet, driver.now)
        self.assertEqual(subtitle.words, ("Neue", "Worte."))

    def test_a_new_turn_in_the_answer_empties_it_at_once(self) -> None:
        driver = self._speaking(TEXT)
        driver.run(0.4)
        self.assertIsNotNone(puppet_subtitle(driver.puppet, driver.now))  # Zwilling: es läuft
        puppet_event(driver.puppet, TurnBegins, driver.now)
        driver.step()
        self.assertIs(driver.state(), IdleState.THINKING)
        self.assertIsNone(puppet_subtitle(driver.puppet, driver.now))

    def test_after_the_end_the_last_board_stays_one_and_a_half_seconds(self) -> None:
        driver = self._speaking(TEXT)
        speech = driver.puppet.speech
        end_s = (speech.start_ms + speech.end_ms) / 1000.0
        while driver.now < end_s + 1.0:
            driver.step()
        self.assertIsNot(driver.state(), IdleState.ANSWER)  # die Antwort ist schon verlassen
        subtitle = puppet_subtitle(driver.puppet, driver.now)
        self.assertEqual(subtitle.words, ("Na", "siehst", "du", "mal!“"))
        self.assertIsNone(subtitle.spoken)
        while driver.now < end_s + 1.5 + STEP_S:
            driver.step()
        self.assertIsNone(puppet_subtitle(driver.puppet, driver.now))

    def test_an_answer_made_of_stage_directions_has_no_subtitle(self) -> None:
        spoken = utterance_from_turn(_turn(text="*Sie lacht kurz.*")).text
        self.assertEqual(spoken, "")
        driver = self._speaking(spoken)
        driver.run(0.3)
        self.assertIsNone(puppet_subtitle(driver.puppet, driver.now))

    def test_an_answer_without_text_ends_the_subtitle_of_the_one_before(self) -> None:
        driver = self._speaking(TEXT)
        driver.run(0.4)
        puppet_cue(driver.puppet, Utterance(1, 0.9, ""), driver.now)
        driver.run(0.1)
        self.assertIsNone(puppet_subtitle(driver.puppet, driver.now))

    def test_the_puppet_reads_only(self) -> None:
        driver = self._speaking(TEXT)
        held = driver.puppet.subtitle
        puppet_subtitle(driver.puppet, driver.now)
        self.assertIs(driver.puppet.subtitle, held)

    def test_a_time_before_the_last_step_is_rejected(self) -> None:
        driver = self._speaking(TEXT)
        with self.assertRaises(ValueError):
            puppet_subtitle(driver.puppet, driver.now - 1.0)


if __name__ == "__main__":
    unittest.main()
