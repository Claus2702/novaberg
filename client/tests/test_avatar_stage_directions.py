"""Zeugen zu `avatar.stage_directions`: der Mund spricht keine Regieanweisungen.

Ohne GTK, ohne Netz. Der Text der Äußerung wird gefiltert, nicht erst die Laute;
deshalb prüfen die Zeugen den Text und rechnen die Dauer mit der Zeitachse nach.
"""

import unittest

from avatar.puppet import Utterance, utterance_from_turn
from avatar.speech import speech_timeline, text_to_phonemes
from avatar.stage_directions import spoken_text

EXAMPLE = "Gurken und Zucchini! *Sie lacht kurz.* Na siehst du mal!"


def _turn(text: object) -> dict:
    """Eine Antwort, wie sie beim Client ankommt."""
    return {"emotion": "freude", "arousal": 0.5, "antwort": text}


def _words(text: str) -> list[str]:
    """Die Wörter eines Texts in Kleinschreibung, ohne Satzzeichen."""
    return "".join(c if c.isalnum() else " " for c in text.lower()).split()


def _playback(text: str) -> float:
    """Die Dauer der Wiedergabe eines Texts: das Ende seiner Zeitachse, 0 ohne Text."""
    return speech_timeline(text_to_phonemes(text))[1] if text.strip() else 0.0


class RemovedTest(unittest.TestCase):
    """Was der Chat kursiv setzt, fällt weg."""

    def test_star_emphasis_is_removed(self) -> None:
        self.assertEqual(_words(spoken_text("Ja *Sie nickt.* nein")), ["ja", "nein"])

    def test_underscore_emphasis_is_removed(self) -> None:
        self.assertEqual(_words(spoken_text("Ja _Sie nickt._ nein")), ["ja", "nein"])

    def test_bold_italic_is_removed(self) -> None:
        self.assertEqual(_words(spoken_text("Ja ***Sie nickt.*** nein")), ["ja", "nein"])

    def test_emphasis_over_a_line_break_is_removed(self) -> None:
        self.assertEqual(_words(spoken_text("Ja *Sie nickt\nlangsam.* nein")), ["ja", "nein"])

    def test_two_directions_in_one_sentence_are_removed(self) -> None:
        text = "Ja *lacht* und *nickt* nein"
        self.assertEqual(_words(spoken_text(text)), ["ja", "und", "nein"])

    def test_emphasis_does_not_reach_over_a_blank_line(self) -> None:
        """Zwilling zum Umbruch: Über einen Absatz hinweg ist es keine Hervorhebung."""
        text = "Ja *eins\n\nzwei* nein"
        self.assertEqual(spoken_text(text), text)

    def test_a_direction_without_spaces_around_it_leaves_two_words(self) -> None:
        """Die Stelle wird zu Leerraum: `Ja` und `nein` wachsen nicht zusammen."""
        self.assertEqual(spoken_text("Ja*sie nickt*nein"), "Ja nein")

    def test_the_same_direction_with_spaces_gives_the_same_words(self) -> None:
        """Zwilling: Mit Leerraum um die Anweisung bleiben dieselben zwei Wörter."""
        self.assertEqual(_words(spoken_text("Ja *sie nickt* nein")), ["ja", "nein"])
        self.assertEqual(_words(spoken_text("Ja*sie nickt*nein")), ["ja", "nein"])

    def test_an_underscore_inside_a_word_is_no_emphasis(self) -> None:
        """Der schließende Unterstrich steht im Wort: Der Text bleibt, wie er ist."""
        text = "Ja _sie nickt_nein"
        self.assertEqual(spoken_text(text), text)


class KeptTest(unittest.TestCase):
    """Was bleibt, bleibt: nur Hervorhebung fällt weg."""

    def test_bold_is_spoken_without_the_stars(self) -> None:
        self.assertEqual(spoken_text("Das ist **fett** gesagt"), "Das ist fett gesagt")

    def test_underscore_in_a_word_stays(self) -> None:
        text = "Das ist snake_case und my_var_name"
        self.assertEqual(spoken_text(text), text)

    def test_single_star_without_partner_stays(self) -> None:
        for text in ("5 * 3 ist 15", "Ja *Sie lacht", "Sie lacht* nein"):
            with self.subTest(text=text):
                self.assertEqual(spoken_text(text), text)

    def test_text_without_markers_comes_out_unchanged(self) -> None:
        text = "  Hallo, Welt!\nZweite Zeile.  "
        self.assertEqual(spoken_text(text), text)

    def test_bold_around_a_direction_leaves_the_rest(self) -> None:
        text = "**Achtung *Sie flüstert* jetzt**"
        self.assertEqual(_words(spoken_text(text)), ["achtung", "jetzt"])

    def test_input_that_is_no_text_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            spoken_text(None)  # type: ignore[arg-type]
        self.assertEqual(spoken_text(""), "")  # Zwilling


class SpokenAnswerTest(unittest.TestCase):
    """In `utterance_from_turn`: der Text der Äußerung ist der gesprochene."""

    def test_the_example_keeps_the_words_outside_the_direction(self) -> None:
        utterance = utterance_from_turn(_turn(EXAMPLE))
        want = ["gurken", "und", "zucchini", "na", "siehst", "du", "mal"]
        self.assertEqual(_words(utterance.text), want)
        self.assertNotIn("*", utterance.text)

    def test_the_words_around_a_direction_do_not_grow_together(self) -> None:
        self.assertEqual(
            text_to_phonemes(utterance_from_turn(_turn(EXAMPLE)).text),
            text_to_phonemes("Gurken und Zucchini! Na siehst du mal!"),
        )

    def test_a_sentence_end_before_the_direction_stays(self) -> None:
        self.assertIn("!", utterance_from_turn(_turn(EXAMPLE)).text)

    def test_an_answer_of_only_directions_is_silent(self) -> None:
        utterance = utterance_from_turn(_turn("*Sie nickt.*"))
        self.assertEqual(utterance, Utterance(utterance.sector, 0.5, ""))
        self.assertEqual(_playback(utterance.text), 0.0)

    def test_the_playback_is_shorter_and_equals_the_hand_written_text(self) -> None:
        spoken = utterance_from_turn(_turn(EXAMPLE)).text
        self.assertLess(_playback(spoken), _playback(EXAMPLE))
        self.assertEqual(_playback(spoken), _playback("Gurken und Zucchini! Na siehst du mal!"))

    def test_an_answer_without_markers_is_unchanged(self) -> None:
        self.assertEqual(utterance_from_turn(_turn("Hallo")).text, "Hallo")


if __name__ == "__main__":
    unittest.main()
