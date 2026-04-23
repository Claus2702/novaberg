"""
KZG-Panel — Kurzzeitgedächtnis-Einträge aus Redis.

Liest ``GET /gedaechtnis/kzg/{user_id}`` und zeigt alle Einträge als
scrollbare Karten-Liste, sortiert nach Salienz (wie vom Server geliefert).

Response-Format (siehe ``server/api/gedaechtnis.py``):

    {
        "eintraege": [
            {
                "key":            str,
                "themen":         str,
                "inhalt":         str,
                "salienz":        float,
                "haeufigkeit":    int,
                "dimension":      str,
                "gedaechtnistyp": str,
                "ttl_sekunden":   int,
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


class KzgPanel(PanelBase):
    """Scrollbare Liste aller KZG-Einträge für einen User."""

    PANEL_ID = "kzg"
    PANEL_LABEL = "KZG"
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

        placeholder = Gtk.Label(label="Lade KZG …")
        placeholder.set_xalign(0.0)
        placeholder.add_css_class("dim-label")
        self._list_box.append(placeholder)

        self.content_area.append(scroll)

    # ═══════════════════════════════════════════════════════════════
    # Daten-Ladung
    # ═══════════════════════════════════════════════════════════════
    def load_data(self) -> dict:
        """Holt alle KZG-Einträge der aktuell gewählten Perspektive."""
        params: dict = self._get_api_params()
        url: str = f"{SERVER_URL}/gedaechtnis/kzg/{params['user_id']}"
        query: dict = {
            "character_id": params["character_id"],
            "beobachter":   params["beobachter"],
        }
        logger.debug(f"KzgPanel: GET {url} {query}")
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
            f"KzgPanel '{self.user_id}': {anzahl} KZG-Einträge erhalten"
        )

        _clear_box(self._list_box)

        if not eintraege:
            leer = Gtk.Label(label="(keine KZG-Einträge)")
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


_BEOBACHTER_BADGE: dict[str, str] = {
    "user":      "👤",
    "assistant": "🤖",
}


def _build_entry_card(eintrag: dict) -> Gtk.Box:
    """Baut eine Karte für einen einzelnen KZG-Eintrag."""
    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    card.set_margin_top(6)
    card.set_margin_bottom(6)

    # Kopfzeile: Beobachter-Badge + Salienz + Themen + TTL.
    head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    beobachter: str = str(eintrag.get("beobachter", "") or "")
    beob_icon: str = _BEOBACHTER_BADGE.get(beobachter, "")
    if beob_icon:
        beob_label = Gtk.Label(label=beob_icon)
        beob_label.set_tooltip_text(f"Beobachter: {beobachter}")
        beob_label.set_xalign(0.0)
        head.append(beob_label)

    salienz: float = float(eintrag.get("salienz", 0.0))
    badge = Gtk.Label(label=f"{salienz:.2f}")
    badge.add_css_class("heading")
    badge.set_xalign(0.0)
    head.append(badge)

    themen: str = str(eintrag.get("themen", "") or "—")
    themen_label = Gtk.Label(label=themen)
    themen_label.set_xalign(0.0)
    themen_label.set_hexpand(True)
    themen_label.set_wrap(True)
    themen_label.set_ellipsize(False)  # type: ignore[attr-defined]
    themen_label.add_css_class("heading")
    head.append(themen_label)

    ttl_text: str = _format_ttl(int(eintrag.get("ttl_sekunden", -1)))
    if ttl_text:
        ttl_label = Gtk.Label(label=ttl_text)
        ttl_label.add_css_class("dim-label")
        ttl_label.set_xalign(1.0)
        head.append(ttl_label)

    card.append(head)

    # Inhalt/Zusammenfassung als umbrechender Fließtext.
    inhalt: str = str(eintrag.get("inhalt", "") or "")
    if inhalt:
        text_label = Gtk.Label(label=inhalt)
        text_label.set_xalign(0.0)
        text_label.set_wrap(True)
        text_label.set_selectable(True)
        card.append(text_label)

    # Tag-Zeile: dimension · gedaechtnistyp · häufigkeit.
    tags: list[str] = []
    dimension: str = str(eintrag.get("dimension", "") or "")
    gtyp: str = str(eintrag.get("gedaechtnistyp", "") or "")
    haeufigkeit: int = int(eintrag.get("haeufigkeit", 0))

    if dimension:
        tags.append(f"dim: {dimension}")
    if gtyp:
        tags.append(f"typ: {gtyp}")
    if haeufigkeit:
        tags.append(f"×{haeufigkeit}")

    if tags:
        tag_label = Gtk.Label(label="  ·  ".join(tags))
        tag_label.set_xalign(0.0)
        tag_label.add_css_class("dim-label")
        card.append(tag_label)

    return card


def _format_ttl(sekunden: int) -> str:
    """Formatiert eine TTL in Sekunden als kompaktes Kürzel (z.B. '3d 2h')."""
    if sekunden < 0:
        return ""
    if sekunden == 0:
        return "0s"

    tage:     int = sekunden // 86400
    stunden:  int = (sekunden % 86400) // 3600
    minuten:  int = (sekunden % 3600) // 60

    if tage > 0:
        return f"TTL {tage}d {stunden}h"
    if stunden > 0:
        return f"TTL {stunden}h {minuten}m"
    return f"TTL {minuten}m"
