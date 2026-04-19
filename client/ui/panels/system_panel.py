"""
System-Panel — Health-Dashboard aller Dienste.

Pilot-Panel für die Panel-Infrastruktur. Zeigt den Status aller Dienste
aus dem ``/health``-Endpoint (Server, Redis, PostgreSQL, Ollama, SearXNG)
und den aktuellen Shadow/Pixie-Zustand.

Darstellung:

    ┌──────────────────────────────────┐
    │                      [↻]         │  ← Header (ohne User-Selector)
    ├──────────────────────────────────┤
    │  🟢 Server         Läuft         │
    │  🟢 Redis          Läuft         │
    │  🟢 PostgreSQL     Läuft         │
    │  🔴 Ollama         Fehler        │
    │  🔴 SearXNG        Fehler        │
    │  ────────────────                │
    │  Pixie: idle                     │
    ├──────────────────────────────────┤
    │ Aktualisiert: HH:MM:SS           │
    └──────────────────────────────────┘

Status-Mapping (Server-Feldwert → Indikator/Text):
* ``ok``      → 🟢 Läuft
* ``fehler``  → 🔴 Fehler
* sonst       → 🟡 Unbekannt
"""

import logging

import requests

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from config import HEALTH_URL, PANEL_REQUEST_TIMEOUT  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402


logger = logging.getLogger(__name__)


# Reihenfolge und deutsche Anzeigenamen der Dienste im Panel.
_SERVICE_ROWS: list[tuple[str, str]] = [
    ("server",   "Server"),
    ("redis",    "Redis"),
    ("postgres", "PostgreSQL"),
    ("ollama",   "Ollama"),
    ("searxng",  "SearXNG"),
]

# Spaltenbreite des Dienstnamens, damit der Status in allen Zeilen
# bündig rechts davon erscheint.
_NAME_COLUMN_WIDTH = 14


class SystemPanel(PanelBase):
    """System-Health-Dashboard (GET /health)."""

    PANEL_ID = "system"
    PANEL_LABEL = "System"
    UNIQUE = True
    CATEGORY = "on_demand"
    NEEDS_USER_SELECTOR = False
    # -1 = GTK benutzt die natürliche Mindestgröße des Inhalts.
    DEFAULT_WIDTH = -1
    DEFAULT_HEIGHT = -1

    def _build_content(self) -> None:
        """Legt einen vertikalen Container für die Dienst-Zeilen an."""
        self._rows_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.content_area.append(self._rows_box)

        # Initial-Anzeige, bevor Daten geladen sind.
        placeholder = Gtk.Label(label="Lade Systemstatus …")
        placeholder.set_xalign(0.0)
        placeholder.add_css_class("dim-label")
        self._rows_box.append(placeholder)

    # ═══════════════════════════════════════════════════════════════
    # Daten-Ladung
    # ═══════════════════════════════════════════════════════════════
    def load_data(self) -> dict:
        """Holt den aktuellen Health-Status per GET /health (blockiert)."""
        logger.debug(f"SystemPanel: GET {HEALTH_URL}")
        response = requests.get(HEALTH_URL, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    # ═══════════════════════════════════════════════════════════════
    # UI-Update (läuft im UI-Thread via GLib.idle_add)
    # ═══════════════════════════════════════════════════════════════
    def _update_ui(self, data: dict) -> None:
        """Baut die Dienst-Zeilen und den Pixie-Status auf."""
        logger.debug(f"SystemPanel: UI-Update mit {len(data)} Feldern")

        # Bestehende Zeilen entfernen.
        child = self._rows_box.get_first_child()
        while child is not None:
            self._rows_box.remove(child)
            child = self._rows_box.get_first_child()

        # Pro Dienst eine Zeile.
        for feld, anzeige in _SERVICE_ROWS:
            status: str = str(data.get(feld, "unbekannt"))
            emoji, text = _status_to_indicator(status)
            self._rows_box.append(_build_service_row(anzeige, emoji, text))

        # Trenner vor dem Pixie-Status.
        self._rows_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # Pixie / Shadow-Zustand.
        shadow: dict = data.get("shadow") or {}
        zustand: str = str(shadow.get("zustand", "idle"))
        thema: str = str(shadow.get("thema", ""))

        pixie_text: str = f"Pixie: {zustand}"
        if thema:
            pixie_text += f" — {thema}"

        pixie_label = Gtk.Label(label=pixie_text)
        pixie_label.set_xalign(0.0)
        self._rows_box.append(pixie_label)


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen (modullokal)
# ═══════════════════════════════════════════════════════════════════
def _status_to_indicator(status: str) -> tuple[str, str]:
    """Mappt einen Server-Statuswert auf (Emoji, Anzeigetext)."""
    if status == "ok":
        return "🟢", "Läuft"
    if status == "fehler":
        return "🔴", "Fehler"
    return "🟡", status or "Unbekannt"


def _build_service_row(name: str, emoji: str, status_text: str) -> Gtk.Box:
    """Baut eine einzelne Dienst-Zeile: [emoji] [name] [status]."""
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    emoji_label = Gtk.Label(label=emoji)
    emoji_label.set_xalign(0.0)
    row.append(emoji_label)

    name_label = Gtk.Label(label=name)
    name_label.set_xalign(0.0)
    name_label.set_width_chars(_NAME_COLUMN_WIDTH)
    row.append(name_label)

    status_label = Gtk.Label(label=status_text)
    status_label.set_xalign(0.0)
    status_label.set_hexpand(True)
    row.append(status_label)

    return row
