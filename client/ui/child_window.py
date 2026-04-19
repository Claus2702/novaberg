"""
Fenster-Wrapper für ein einzelnes Panel.

Ein :class:`ChildWindow` ist ein ``Gtk.Window``, das genau ein
:class:`PanelBase`-Widget enthält. Beim Schließen wird die
:class:`PanelRegistry` benachrichtigt, damit sie die Instanz aus dem
Tracking entfernt (nur für ``UNIQUE``-Panels relevant).
"""

import logging
from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from ui.panel_base import PanelBase  # noqa: E402

if TYPE_CHECKING:
    from ui.panel_registry import PanelRegistry


logger = logging.getLogger(__name__)


class ChildWindow(Gtk.Window):
    """Toplevel-Fenster, das ein Panel trägt."""

    def __init__(self, panel: PanelBase, registry: "PanelRegistry") -> None:
        super().__init__()
        logger.debug(
            f"ChildWindow wird erzeugt (Panel='{panel.PANEL_ID}', "
            f"Label='{panel.PANEL_LABEL}', "
            f"Größe={panel.DEFAULT_WIDTH}x{panel.DEFAULT_HEIGHT})"
        )

        self.panel: PanelBase = panel
        self._registry = registry

        self.set_title(panel.PANEL_LABEL)
        self.set_default_size(panel.DEFAULT_WIDTH, panel.DEFAULT_HEIGHT)
        self.set_child(panel)

        self.connect("close-request", self._on_close_request)

    def _on_close_request(self, window: Gtk.Window) -> bool:
        """Schließen: Registry informieren und Fenster selbst zerstören.

        Return ``True``, damit GTK das Default-Close-Handling unterdrückt —
        wir rufen :meth:`destroy` selbst auf.
        """
        logger.info(f"Panel-Fenster schließt ({self.panel.PANEL_ID})")
        self._registry.on_panel_closed(self.panel)
        self.destroy()
        return True
