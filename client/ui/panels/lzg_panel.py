"""
LZG-Panel — Langzeitgedächtnis-Einträge aus PostgreSQL.

Liest ``GET /gedaechtnis/lzg/{user_id}`` und zeigt alle Einträge als
scrollbare Karten-Liste, sortiert nach ``verstaerkt_am`` absteigend
(wie vom Server geliefert).

Response-Format (siehe ``server/api/gedaechtnis.py``):

    {
        "eintraege": [
            {
                "dimension":     str,
                "inhalt":        str,
                "gewicht":       float,
                "haeufigkeit":   int,
                "erstellt_am":   str,   # ISO-8601 oder ""
                "verstaerkt_am": str,   # ISO-8601 oder ""
            }, ...
        ],
        "anzahl": int,
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


class LzgPanel(PanelBase):
    """Scrollbare Liste aller LZG-Einträge für einen User."""

    PANEL_ID = "lzg"
    PANEL_LABEL = "LZG"
    UNIQUE = True
    CATEGORY = "on_demand"
    NEEDS_USER_SELECTOR = True
    DEFAULT_WIDTH = 600
    DEFAULT_HEIGHT = 500

    def _build_content(self) -> None:
        """Scroll-Container mit vertikaler Karten-Liste."""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self._list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        scroll.set_child(self._list_box)

        placeholder = Gtk.Label(label="Lade LZG …")
        placeholder.set_xalign(0.0)
        placeholder.add_css_class("dim-label")
        self._list_box.append(placeholder)

        self.content_area.append(scroll)

    # ═══════════════════════════════════════════════════════════════
    # Daten-Ladung
    # ═══════════════════════════════════════════════════════════════
    def load_data(self) -> dict:
        """Holt alle LZG-Einträge der aktuell gewählten Perspektive."""
        params: dict = self._get_api_params()
        url: str = f"{SERVER_URL}/gedaechtnis/lzg/{params['user_id']}"
        query: dict = {
            "character_id": params["character_id"],
            "beobachter":   params["beobachter"],
        }
        logger.debug(f"LzgPanel: GET {url} {query}")
        response = requests.get(url, params=query, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    # ═══════════════════════════════════════════════════════════════
    # UI-Update
    # ═══════════════════════════════════════════════════════════════
    def _update_ui(self, data: dict) -> None:
        """Baut eine Karte pro Eintrag, Trennlinien dazwischen."""
        eintraege: list = data.get("eintraege") or []
        anzahl: int = int(data.get("anzahl", len(eintraege)))
        logger.info(
            f"LzgPanel '{self.user_id}': {anzahl} LZG-Einträge erhalten"
        )

        _clear_box(self._list_box)

        if not eintraege:
            leer = Gtk.Label(label="(keine LZG-Einträge)")
            leer.set_xalign(0.0)
            leer.add_css_class("dim-label")
            leer.set_margin_top(8)
            self._list_box.append(leer)
            return

        for idx, eintrag in enumerate(eintraege):
            if idx > 0:
                self._list_box.append(
                    Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                )
            self._list_box.append(_build_entry_card(eintrag))


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen
# ═══════════════════════════════════════════════════════════════════
def _clear_box(box: Gtk.Box) -> None:
    """Entfernt alle Kind-Widgets aus einem Box-Container."""
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _build_entry_card(eintrag: dict) -> Gtk.Box:
    """Baut eine Karte für einen einzelnen LZG-Eintrag."""
    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    card.set_margin_top(6)
    card.set_margin_bottom(6)

    # Kopfzeile: Gewicht-Badge + Dimension (fett) + verstärkt-Zeitstempel rechts.
    head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    gewicht: float = float(eintrag.get("gewicht", 0.0))
    badge = Gtk.Label(label=f"{gewicht:.2f}")
    badge.add_css_class("heading")
    badge.set_xalign(0.0)
    head.append(badge)

    dimension: str = str(eintrag.get("dimension", "") or "—")
    dim_label = Gtk.Label(label=dimension)
    dim_label.set_xalign(0.0)
    dim_label.set_hexpand(True)
    dim_label.set_wrap(True)
    dim_label.set_ellipsize(False)  # type: ignore[attr-defined]
    dim_label.add_css_class("heading")
    head.append(dim_label)

    verstaerkt: str = _format_timestamp(str(eintrag.get("verstaerkt_am", "") or ""))
    if verstaerkt:
        vs_label = Gtk.Label(label=f"verstärkt: {verstaerkt}")
        vs_label.add_css_class("dim-label")
        vs_label.set_xalign(1.0)
        head.append(vs_label)

    card.append(head)

    # Inhalt als umbrechender Fließtext.
    inhalt: str = str(eintrag.get("inhalt", "") or "")
    if inhalt:
        text_label = Gtk.Label(label=inhalt)
        text_label.set_xalign(0.0)
        text_label.set_wrap(True)
        text_label.set_selectable(True)
        card.append(text_label)

    # Tag-Zeile: erstellt · häufigkeit.
    tags: list[str] = []
    erstellt: str = _format_timestamp(str(eintrag.get("erstellt_am", "") or ""))
    haeufigkeit: int = int(eintrag.get("haeufigkeit", 0))

    if erstellt:
        tags.append(f"erstellt: {erstellt}")
    if haeufigkeit:
        tags.append(f"×{haeufigkeit}")

    if tags:
        tag_label = Gtk.Label(label="  ·  ".join(tags))
        tag_label.set_xalign(0.0)
        tag_label.add_css_class("dim-label")
        card.append(tag_label)

    return card


def _format_timestamp(iso: str) -> str:
    """Kürzt einen ISO-Zeitstempel auf 'YYYY-MM-DD HH:MM'."""
    if not iso:
        return ""
    s: str = iso.replace("T", " ")
    # Sekunden/Millisekunden/Zeitzone abschneiden, falls vorhanden.
    if len(s) >= 16:
        return s[:16]
    return s
