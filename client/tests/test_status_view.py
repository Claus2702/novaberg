"""Zeugen für die Zeilen der Phasenanzeige: kein Umbruch, das Gesicht behält seine Größe.

Brauchen GTK. Ohne Anzeige scheitern sie laut und überspringen nichts.
"""

import unittest

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango  # noqa: E402

from ui.status_label import set_status_text, status_label  # noqa: E402

SHORT = "Rauschen"
LONGEST = (
    "Nachklang · seit 14 s · zurück ins Rauschen in 1 s (Dauer 15 s)"
    " · Emotion: Nova — Freude, Arousal 0,60"
)
NARROW = 150  # Breite in Pixeln, schmaler als jede lange Zeile


def natural_height(label: Gtk.Label, width: int) -> int:
    """Die natürliche Höhe des Labels bei fester Breite."""
    _minimum, natural, _min_baseline, _nat_baseline = label.measure(Gtk.Orientation.VERTICAL, width)
    return natural


class StatusLabelTest(unittest.TestCase):
    """Eine Zeile bleibt eine Zeile, der volle Text steht im Tooltip."""

    @classmethod
    def setUpClass(cls) -> None:
        if not Gtk.init_check():
            raise RuntimeError("GTK startet nicht (keine Anzeige): Zeuge kann nicht prüfen")

    def test_no_wrap_and_ellipsis_at_end(self) -> None:
        label = status_label()
        self.assertFalse(label.get_wrap())
        self.assertEqual(label.get_ellipsize(), Pango.EllipsizeMode.END)

    def test_height_is_the_same_for_short_and_longest_text(self) -> None:
        label = status_label()
        label.set_text(SHORT)
        short_height = natural_height(label, NARROW)
        label.set_text(LONGEST)
        self.assertEqual(natural_height(label, NARROW), short_height)

    def test_twin_wrapped_label_is_higher_for_the_longest_text(self) -> None:
        """Zwilling: Mit Umbruch wäre die Höhe beim langen Text größer."""
        label = Gtk.Label()
        label.set_wrap(True)
        label.set_text(SHORT)
        short_height = natural_height(label, NARROW)
        label.set_text(LONGEST)
        self.assertGreater(natural_height(label, NARROW), short_height)

    def test_tooltip_carries_the_full_text(self) -> None:
        label = status_label()
        set_status_text(label, LONGEST)
        self.assertEqual(label.get_tooltip_text(), LONGEST)

    def test_bold_line_keeps_the_plain_text_in_the_tooltip(self) -> None:
        label = status_label()
        set_status_text(label, "Form <a> & b", bold=True)
        self.assertEqual(label.get_tooltip_text(), "Form <a> & b")

    def test_empty_text_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            set_status_text(status_label(), "")


if __name__ == "__main__":
    unittest.main()
