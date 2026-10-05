"""Zeugen für das Label des Untertitels: immer zwei Zeilen hoch, das Gesicht springt nicht.

Brauchen GTK. Ohne Anzeige scheitern sie laut und überspringen nichts.
"""

import unittest

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango  # noqa: E402

from avatar.subtitle import Subtitle, subtitle_markup  # noqa: E402
from ui.subtitle_label import set_subtitle_markup, subtitle_label  # noqa: E402

SHORT = Subtitle(("Na", "siehst", "du"), 1)
LONGEST = Subtitle(tuple(f"Wort{i}" for i in range(14)), 5)  # 14 Wörter: weit über zwei Zeilen
NARROW = 150  # Breite in Pixeln, schmaler als jede Tafel
WIDE = 480  # Standardbreite des Panels


def natural_height(label: Gtk.Label, width: int) -> int:
    """Die natürliche Höhe des Labels bei fester Breite."""
    _minimum, natural, _min_baseline, _nat_baseline = label.measure(Gtk.Orientation.VERTICAL, width)
    return natural


class SubtitleLabelTest(unittest.TestCase):
    """Der Untertitel ist zwei Zeilen hoch, ob leer, kurz oder zu lang."""

    @classmethod
    def setUpClass(cls) -> None:
        if not Gtk.init_check():
            raise RuntimeError("GTK startet nicht (keine Anzeige): Zeuge kann nicht prüfen")

    def test_wrap_two_lines_and_ellipsis_at_end(self) -> None:
        label = subtitle_label()
        self.assertTrue(label.get_wrap())
        self.assertEqual(label.get_lines(), 2)
        self.assertEqual(label.get_ellipsize(), Pango.EllipsizeMode.END)

    def test_the_empty_label_already_has_a_height(self) -> None:
        for width in (NARROW, WIDE):
            self.assertGreater(natural_height(subtitle_label(), width), 0)

    def test_height_is_the_same_empty_short_and_longest(self) -> None:
        for width in (NARROW, WIDE):
            label = subtitle_label()
            empty = natural_height(label, width)
            set_subtitle_markup(label, subtitle_markup(SHORT))
            self.assertEqual(natural_height(label, width), empty)
            set_subtitle_markup(label, subtitle_markup(LONGEST))
            self.assertEqual(natural_height(label, width), empty)
            set_subtitle_markup(label, "")
            self.assertEqual(natural_height(label, width), empty)

    def test_twin_a_plain_wrapped_label_is_higher_for_the_longest_text(self) -> None:
        """Zwilling: ohne Begrenzung auf zwei Zeilen wüchse das Label mit dem Text."""
        label = Gtk.Label()
        label.set_wrap(True)
        label.set_text("Na")
        short_height = natural_height(label, NARROW)
        label.set_text(" ".join(LONGEST.words))
        self.assertGreater(natural_height(label, NARROW), short_height)

    def test_the_underline_is_in_the_markup_the_label_shows(self) -> None:
        label = subtitle_label()
        set_subtitle_markup(label, subtitle_markup(SHORT))
        self.assertEqual(label.get_text(), "Na siehst du")
        self.assertIn("<u>siehst</u>", label.get_label())

    def test_markup_of_the_text_is_not_taken_for_markup(self) -> None:
        label = subtitle_label()
        set_subtitle_markup(label, subtitle_markup(Subtitle(("a", "<b>", "&"), None)))
        self.assertEqual(label.get_text(), "a <b> &")

    def test_a_label_that_is_none_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            set_subtitle_markup(None, "")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
