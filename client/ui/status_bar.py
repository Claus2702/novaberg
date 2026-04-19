"""
Statuszeile am unteren Fensterrand.

Zeigt den Verbindungsstatus (links) und den Pixie-Zustand (rechts).
Beide Labels werden über dedizierte Setter aktualisiert, die aus dem
UI-Thread aufgerufen werden müssen (GLib.idle_add beim Aufruf aus Threads).
"""

import logging

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


logger = logging.getLogger(__name__)


class StatusBar(Gtk.Box):
    """Kleine, zweispaltige Statuszeile (Verbindung · Pixie)."""

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        logger.debug("StatusBar wird initialisiert")

        # Kompakte Darstellung: wenig Padding, dezente Farbe über CSS-Klasse
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(4)
        self.set_margin_bottom(4)
        self.add_css_class("nova-statusbar")

        # Linkes Label — Verbindungsstatus
        self._connection_label = Gtk.Label(label="Getrennt")
        self._connection_label.set_xalign(0.0)
        self._connection_label.set_hexpand(True)
        self._connection_label.add_css_class("nova-statusbar-label")

        # Rechtes Label — Pixie-Zustand
        self._pixie_label = Gtk.Label(label="Pixie: idle")
        self._pixie_label.set_xalign(1.0)
        self._pixie_label.add_css_class("nova-statusbar-label")

        self.append(self._connection_label)
        self.append(self._pixie_label)

        logger.debug("StatusBar initialisiert (Verbindung + Pixie-Zustand)")

    # ───────────────────────────────
    # Setter (müssen im UI-Thread aufgerufen werden)
    # ───────────────────────────────
    def set_connection_status(self, text: str) -> None:
        """Verbindungsstatus (linkes Label) setzen."""
        logger.debug(f"StatusBar: Verbindungsstatus -> '{text}'")
        self._connection_label.set_text(text)

    def set_pixie_status(self, text: str) -> None:
        """Pixie-Zustand (rechtes Label) setzen."""
        logger.debug(f"StatusBar: Pixie-Status -> '{text}'")
        self._pixie_label.set_text(text)
