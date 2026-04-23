"""
Session-Panel — Gesprächsverlauf der aktuellen Session.

Liest ``GET /session/kontext/{user_id}`` und zeigt die Turn-Liste
chronologisch (älteste oben, neueste unten), plus — falls vorhanden —
die Session-Zusammenfassung als erste Box.

Response-Format (siehe ``server/api/session.py``):

    {
        "zusammenfassung": str,
        "turns": [
            {
                "rolle":       "user" | "assistant",
                "inhalt":      str,
                "zeit":        float,       # Unix-Timestamp
                "intentionen": list[str],
                "emotion":     str,
                "modus":       str,
                "kern":        str,
                # optional: arousal, themen, sprach_stil, ...
            }, ...
        ],
        "anzahl_turns": int,
    }
"""

import datetime
import logging

import requests

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from config import PANEL_REQUEST_TIMEOUT, SERVER_URL  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402


logger = logging.getLogger(__name__)


class SessionPanel(PanelBase):
    """Scrollbare Turn-Liste der aktuellen Session."""

    PANEL_ID = "session"
    PANEL_LABEL = "Session"
    UNIQUE = True
    CATEGORY = "on_demand"
    NEEDS_USER_SELECTOR = True
    DEFAULT_WIDTH = 600
    DEFAULT_HEIGHT = 500

    def _build_content(self) -> None:
        """Scrollbox mit den einzelnen Turn-Karten."""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self._list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scroll.set_child(self._list_box)

        placeholder = Gtk.Label(label="Lade Session …")
        placeholder.set_xalign(0.0)
        placeholder.add_css_class("dim-label")
        self._list_box.append(placeholder)

        self.content_area.append(scroll)

    # ═══════════════════════════════════════════════════════════════
    # Daten-Ladung
    # ═══════════════════════════════════════════════════════════════
    def load_data(self) -> dict:
        """Holt Session-Kontext (Zusammenfassung + Turns) für die Perspektive.

        Im Session-Panel wollen wir beide Seiten des Gesprächspaares sehen,
        deshalb wird ``beobachter`` hier NICHT mitgesendet — der Perspektive-
        Switch ändert nur die Datenquelle (gleiches Paar) und die Filterung
        passiert später im Client, falls nötig.
        """
        params: dict = self._get_api_params()
        url: str = f"{SERVER_URL}/session/kontext/{params['user_id']}"
        query: dict = {"character_id": params["character_id"]}
        logger.debug(f"SessionPanel: GET {url} {query}")
        response = requests.get(url, params=query, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    # ═══════════════════════════════════════════════════════════════
    # UI-Update
    # ═══════════════════════════════════════════════════════════════
    def _update_ui(self, data: dict) -> None:
        """Baut Zusammenfassung + Turn-Karten."""
        zusammenfassung: str = str(data.get("zusammenfassung", "") or "")
        turns: list = data.get("turns") or []
        anzahl: int = int(data.get("anzahl_turns", len(turns)))

        logger.info(
            f"SessionPanel '{self.user_id}': {anzahl} Turns, "
            f"Zusammenfassung: {'ja' if zusammenfassung else 'nein'}"
        )

        _clear_box(self._list_box)

        if zusammenfassung:
            self._list_box.append(_build_summary_card(zusammenfassung))

        if not turns:
            leer = Gtk.Label(label="(keine Turns in der Session)")
            leer.set_xalign(0.0)
            leer.add_css_class("dim-label")
            leer.set_margin_top(8)
            self._list_box.append(leer)
            return

        for turn in turns:
            self._list_box.append(_build_turn_card(turn))


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen
# ═══════════════════════════════════════════════════════════════════
def _clear_box(box: Gtk.Box) -> None:
    """Entfernt alle Kind-Widgets aus einem Box-Container."""
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _build_summary_card(text: str) -> Gtk.Box:
    """Kompakte Karte mit der Session-Zusammenfassung."""
    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    card.add_css_class("frame")

    header = Gtk.Label(label="Zusammenfassung")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    card.append(header)

    body = Gtk.Label(label=text)
    body.set_xalign(0.0)
    body.set_wrap(True)
    body.set_selectable(True)
    card.append(body)

    return card


def _build_turn_card(turn: dict) -> Gtk.Box:
    """Karte für einen einzelnen Turn: Rolle + Zeit + Inhalt + Meta-Tags."""
    rolle: str = str(turn.get("rolle", "") or "")
    inhalt: str = str(turn.get("inhalt", "") or "")

    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    card.set_margin_top(2)
    card.set_margin_bottom(2)

    # Rolle-spezifische CSS-Klasse (dezente Unterscheidung, nicht so auffällig
    # wie im Haupt-Chat).
    if rolle == "user":
        card.add_css_class("session-turn-user")
    elif rolle == "assistant":
        card.add_css_class("session-turn-assistant")

    # Kopfzeile: Rolle · Zeit.
    zeit_str: str = _format_zeit(turn.get("zeit"))
    rolle_anzeige: str = "User" if rolle == "user" else ("Nova" if rolle == "assistant" else rolle)
    head_text: str = f"{rolle_anzeige}  ·  {zeit_str}" if zeit_str else rolle_anzeige

    head_label = Gtk.Label(label=head_text)
    head_label.set_xalign(0.0)
    head_label.add_css_class("heading")
    card.append(head_label)

    # Inhalt — umbrechender Fließtext.
    if inhalt:
        body = Gtk.Label(label=inhalt)
        body.set_xalign(0.0)
        body.set_wrap(True)
        body.set_selectable(True)
        card.append(body)

    # Meta-Tags: Intentionen / Emotion / Modus.
    tag_text: str = _format_turn_meta(turn)
    if tag_text:
        tag_label = Gtk.Label(label=tag_text)
        tag_label.set_xalign(0.0)
        tag_label.add_css_class("dim-label")
        card.append(tag_label)

    return card


def _format_zeit(zeit_wert) -> str:
    """Formatiert einen Unix-Timestamp als HH:MM:SS (leerer String bei Fehler)."""
    if not zeit_wert:
        return ""
    try:
        timestamp: float = float(zeit_wert)
        return datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
    except (TypeError, ValueError):
        return ""


def _format_turn_meta(turn: dict) -> str:
    """Baut einen kompakten Meta-Tag-String aus Intention/Emotion/Modus."""
    parts: list[str] = []

    intentionen = turn.get("intentionen") or []
    if isinstance(intentionen, list) and intentionen:
        parts.append("Int: " + ", ".join(str(i) for i in intentionen))

    emotion: str = str(turn.get("emotion", "") or "")
    if emotion:
        parts.append(f"Emotion: {emotion}")

    modus: str = str(turn.get("modus", "") or "")
    if modus:
        parts.append(f"Modus: {modus}")

    return "  ·  ".join(parts)
