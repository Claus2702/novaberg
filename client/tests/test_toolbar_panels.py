"""Zeugen fuer die Verdrahtung der Panels mit der Toolbar.

Der Anzeigetext ist zugleich der Verbindungsschluessel: Ein Button findet sein
Panel nur bei exakter Uebereinstimmung mit `PANEL_LABEL`. Weicht eine der
beiden Seiten ab, oeffnet der Reiter nichts — **ohne Fehler**. Genau so hing
das Kontext-Panel am 28.08.2026 einen Tag lang registriert und unerreichbar.

Die Richtung der Pruefung ist deshalb *registriert → Button*: Ein Eintrag in
der Toolbar ohne Panel ist ein gewollter Platzhalter, ein Panel ohne Eintrag
ist unerreichbarer Code.
"""

import unittest

from ui.main_window import _TOOLBAR_PANELS
from ui.panel_registry import create_default_registry


class ToolbarWiringTest(unittest.TestCase):
    """Jedes registrierte Panel ist ueber die Toolbar erreichbar."""

    def setUp(self) -> None:
        self.registry = create_default_registry()
        self.labels = {
            panel_class.PANEL_LABEL: panel_class.PANEL_ID
            for panel_class in self.registry.get_panel_types()
        }

    def test_registry_is_not_empty(self) -> None:
        """Ohne diesen Zeugen waere eine leere Registry ein gruener Lauf."""
        self.assertGreaterEqual(len(self.labels), 10)

    def test_every_registered_panel_has_a_button(self) -> None:
        ohne_button = sorted(lbl for lbl in self.labels if lbl not in _TOOLBAR_PANELS)
        self.assertEqual(ohne_button, [], f"registriert, aber ohne Toolbar-Eintrag: {ohne_button}")

    def test_every_panel_has_a_label(self) -> None:
        ohne_label = [c.__name__ for c in self.registry.get_panel_types() if not c.PANEL_LABEL]
        self.assertEqual(ohne_label, [])

    def test_every_panel_has_an_id(self) -> None:
        ohne_id = [c.__name__ for c in self.registry.get_panel_types() if not c.PANEL_ID]
        self.assertEqual(ohne_id, [])

    def test_labels_are_unique(self) -> None:
        alle = [c.PANEL_LABEL for c in self.registry.get_panel_types()]
        self.assertEqual(len(alle), len(set(alle)))

    def test_toolbar_entries_are_unique(self) -> None:
        self.assertEqual(len(_TOOLBAR_PANELS), len(set(_TOOLBAR_PANELS)))

    def test_conversation_context_panel_is_wired(self) -> None:
        """Der Fall vom 28.08.2026 namentlich — er soll nicht zweimal passieren."""
        self.assertIn("🫧 Gesprächskontext", self.labels)
        self.assertIn("🫧 Gesprächskontext", _TOOLBAR_PANELS)


if __name__ == "__main__":
    unittest.main()
