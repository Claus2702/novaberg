"""
Charakter-Panel — 5 destillierte Profile des Users.

Liest ``GET /gedaechtnis/hash/{user_id}`` und rendert die 5 Profile
("Kern", "Adaptiv", "Intentionen", "Emotionen", "Beziehung") als
scrollbare Sektionen.

Response-Format (siehe ``server/api/gedaechtnis.py``):

    {
        "kern_hash":             str,
        "adaptive_hash":         str,
        "intentions_profil":     str,
        "emotions_profil":       str,
        "beziehungsprofil":      str,
        "kern_aktualisiert":     str,   # ISO-Timestamp
        "adaptive_aktualisiert": str,
    }
"""

import logging

import requests

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from config import PANEL_REQUEST_TIMEOUT, SERVER_URL  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402


logger = logging.getLogger(__name__)


# (Überschrift, Daten-Schlüssel, Schlüssel des Timestamps — "" falls keiner).
_SECTIONS: list[tuple[str, str, str]] = [
    ("Kern",        "kern_hash",         "kern_aktualisiert"),
    ("Adaptiv",     "adaptive_hash",     "adaptive_aktualisiert"),
    ("Intentionen", "intentions_profil", ""),
    ("Emotionen",   "emotions_profil",   ""),
    ("Beziehung",   "beziehungsprofil",  ""),
]


class CharacterPanel(PanelBase):
    """Zeigt die 5 Profile des Charakter-Hash."""

    PANEL_ID = "charakter"
    PANEL_LABEL = "Charakter"
    UNIQUE = True
    CATEGORY = "on_demand"
    NEEDS_USER_SELECTOR = True
    DEFAULT_WIDTH = 500
    DEFAULT_HEIGHT = 600

    def _build_content(self) -> None:
        """Scroll-Container mit Platz für die 5 Sektionen."""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self._outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scroll.set_child(self._outer_box)

        placeholder = Gtk.Label(label="Lade Charakter …")
        placeholder.set_xalign(0.0)
        placeholder.add_css_class("dim-label")
        self._outer_box.append(placeholder)

        self.content_area.append(scroll)

    # ═══════════════════════════════════════════════════════════════
    # Daten-Ladung
    # ═══════════════════════════════════════════════════════════════
    def load_data(self) -> dict:
        """Holt Charakter-Hash-Profile für den aktuellen User."""
        url: str = f"{SERVER_URL}/gedaechtnis/hash/{self.user_id}"
        logger.debug(f"CharacterPanel: GET {url}")
        response = requests.get(url, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    # ═══════════════════════════════════════════════════════════════
    # UI-Update
    # ═══════════════════════════════════════════════════════════════
    def _update_ui(self, data: dict) -> None:
        """Baut pro Profil eine Sektion, getrennt durch Separatoren."""
        befuellte: int = sum(1 for _, key, _ in _SECTIONS if data.get(key))
        logger.info(
            f"CharacterPanel '{self.user_id}': "
            f"{befuellte}/{len(_SECTIONS)} Profile befüllt"
        )

        _clear_box(self._outer_box)

        for idx, (titel, data_key, ts_key) in enumerate(_SECTIONS):
            if idx > 0:
                self._outer_box.append(
                    Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                )

            inhalt: str = str(data.get(data_key, "") or "")
            timestamp: str = str(data.get(ts_key, "") or "") if ts_key else ""

            self._outer_box.append(_build_profile_section(titel, inhalt, timestamp))


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen
# ═══════════════════════════════════════════════════════════════════
def _clear_box(box: Gtk.Box) -> None:
    """Entfernt alle Kind-Widgets aus einem Box-Container."""
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _build_profile_section(titel: str, inhalt: str, timestamp: str) -> Gtk.Box:
    """Baut eine Profil-Sektion: Überschrift [+ Zeitstempel] + Fließtext."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    # Kopfzeile: Titel (fett) + optional Zeitstempel rechts.
    head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    title_label = Gtk.Label(label=titel)
    title_label.set_xalign(0.0)
    title_label.set_hexpand(True)
    title_label.add_css_class("heading")
    head.append(title_label)

    if timestamp:
        ts_label = Gtk.Label(label=f"aktualisiert: {timestamp}")
        ts_label.set_xalign(1.0)
        ts_label.add_css_class("dim-label")
        head.append(ts_label)

    section.append(head)

    # Inhalt — umbrechend, selektierbar. Bei leerem Profil dim-Hinweis.
    if inhalt:
        body = Gtk.Label(label=inhalt)
        body.set_xalign(0.0)
        body.set_wrap(True)
        body.set_selectable(True)
        section.append(body)
    else:
        leer = Gtk.Label(label="(leer)")
        leer.set_xalign(0.0)
        leer.add_css_class("dim-label")
        section.append(leer)

    return section
