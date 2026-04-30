"""
Gesprächsvektor-Panel — zeigt GV4-Debug-Daten nach jedem Turn.

Das Panel ist ``turn_reactive`` und holt seine Daten ueber
``GET /drive/gv_detail``. Der Dispatcher schreibt ``gv_detail`` nach jedem
Turn nach Redis; das Panel laedt beim Oeffnen und nach jedem Turn neu.

Anzeige (kompakt):

    Sprünge:    ██░░  2/3
    Neugier:    ████░ 0.63  (Schwelle: 0.15)
    Strategie:  aktiv

    Wissenslücken (3):
      ● Pflänzchen hegen           KZG  rel=1.577
      ● Person zum Lachen bringen  KZG  rel=0.714
      ● Respektvolles Siezen       KZG  rel=0.545

    Farbton:
      Der Nutzer verfolgt einen Wissenspfad ...

Sprach-Regeln: Code/Bezeichner englisch, UI-Texte und Logs deutsch.
"""

import logging

import requests

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango  # noqa: E402

from config import PANEL_REQUEST_TIMEOUT, SERVER_URL  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402


logger = logging.getLogger(__name__)


_GV_LAENGE_MAX:        int   = 3
_GV_LUECKEN_RELEVANZ:  float = 0.15  # GV_LUECKEN_MIN_RELEVANZ aus dem Server


class GvPanel(PanelBase):
    """Anzeige fuer GV4 (Sprünge, Neugier, Strategie, Wissenslücken, Farbton)."""

    PANEL_ID    = "gv"
    PANEL_LABEL = "🧭 Gesprächsvektor"
    UNIQUE      = True
    CATEGORY    = "turn_reactive"
    NEEDS_USER_SELECTOR = False
    DEFAULT_WIDTH  = 520
    DEFAULT_HEIGHT = 600

    def _build_content(self) -> None:
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self._outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        scroll.set_child(self._outer_box)

        placeholder = Gtk.Label(label="Noch kein Turn empfangen")
        placeholder.set_xalign(0.0)
        placeholder.add_css_class("dim-label")
        self._outer_box.append(placeholder)

        self.content_area.append(scroll)

    def load_data(self) -> dict:
        """Holt das aktuelle ``gv_detail`` vom Server (Redis-Snapshot)."""
        url: str = f"{SERVER_URL}/drive/gv_detail"
        logger.debug(f"GvPanel: GET {url}")
        response = requests.get(url, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json() or {}

    def _update_ui(self, data: dict) -> None:
        """Baut die Sektionen aus dem aktuellen ``gv_detail`` neu auf."""
        _clear_box(self._outer_box)

        if not data:
            placeholder = Gtk.Label(label="Noch kein Turn empfangen")
            placeholder.set_xalign(0.0)
            placeholder.add_css_class("dim-label")
            self._outer_box.append(placeholder)
            return

        laenge:            int   = int(data.get("laenge", 0) or 0)
        effektive_neugier: float = float(data.get("effektive_neugier", 0.0) or 0.0)
        strategie_aktiv:   bool  = bool(data.get("strategie_aktiv", False))
        wissensluecken:    list  = data.get("wissensluecken") or []
        farbton:           str   = str(data.get("farbton") or "")

        logger.info(
            f"GvPanel: laenge={laenge}, neugier={effektive_neugier:.3f}, "
            f"strategie={strategie_aktiv}, luecken={len(wissensluecken)}"
        )

        self._outer_box.append(_build_kennzahlen(
            laenge=laenge,
            neugier=effektive_neugier,
            strategie_aktiv=strategie_aktiv,
        ))
        self._outer_box.append(_build_luecken_section(wissensluecken))
        self._outer_box.append(_build_farbton_section(farbton))

    # ═══════════════════════════════════════════════════════════════
    # Turn-Reactive: nach jedem Turn neu vom Server laden
    # ═══════════════════════════════════════════════════════════════
    def on_turn_received(self, turn_data: dict) -> None:
        """Wird nach jedem Turn aufgerufen — Refresh holt frische Daten via REST."""
        self.refresh()


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen — Layout
# ═══════════════════════════════════════════════════════════════════
def _clear_box(box: Gtk.Box) -> None:
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _build_kennzahlen(laenge: int, neugier: float, strategie_aktiv: bool) -> Gtk.Box:
    """Drei-Zeilen-Block: Sprünge | Neugier | Strategie."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    header = Gtk.Label(label="Gesprächsvektor")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    # Sprünge
    laenge_clamped: int = max(0, min(_GV_LAENGE_MAX, laenge))
    spr_row = _build_metric_row(
        label_text="Sprünge",
        bar_min=0.0,
        bar_max=float(_GV_LAENGE_MAX),
        bar_value=float(laenge_clamped),
        wert_text=f"{laenge_clamped}/{_GV_LAENGE_MAX}",
    )
    section.append(spr_row)

    # Neugier
    neugier_clamped: float = max(0.0, min(1.0, neugier))
    neu_row = _build_metric_row(
        label_text="Neugier",
        bar_min=0.0,
        bar_max=1.0,
        bar_value=neugier_clamped,
        wert_text=f"{neugier:.2f}",
        zusatz_text=f"(Schwelle: {_GV_LUECKEN_RELEVANZ:.2f})",
    )
    section.append(neu_row)

    # Strategie
    strat_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    strat_label = Gtk.Label(label="Strategie")
    strat_label.set_xalign(0.0)
    strat_label.set_width_chars(11)
    strat_label.add_css_class("caption")
    strat_row.append(strat_label)

    status_label = Gtk.Label(label="aktiv" if strategie_aktiv else "—")
    status_label.set_xalign(0.0)
    status_label.set_hexpand(True)
    if strategie_aktiv:
        status_label.add_css_class("success")
    else:
        status_label.add_css_class("dim-label")
    strat_row.append(status_label)

    section.append(strat_row)

    return section


def _build_metric_row(
    label_text: str,
    bar_min:    float,
    bar_max:    float,
    bar_value:  float,
    wert_text:  str,
    zusatz_text: str = "",
) -> Gtk.Box:
    """Eine Zeile: Label | LevelBar | Wert | (optional) Zusatz."""
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    name = Gtk.Label(label=label_text)
    name.set_xalign(0.0)
    name.set_width_chars(11)
    name.add_css_class("caption")
    row.append(name)

    bar = Gtk.LevelBar()
    bar.set_min_value(bar_min)
    bar.set_max_value(bar_max)
    bar.set_value(bar_value)
    bar.set_hexpand(True)
    bar.set_valign(Gtk.Align.CENTER)
    row.append(bar)

    wert = Gtk.Label(label=wert_text)
    wert.set_xalign(1.0)
    wert.set_width_chars(6)
    wert.add_css_class("caption")
    row.append(wert)

    if zusatz_text:
        zusatz = Gtk.Label(label=zusatz_text)
        zusatz.set_xalign(0.0)
        zusatz.add_css_class("dim-label")
        zusatz.add_css_class("caption")
        row.append(zusatz)

    return row


def _build_luecken_section(luecken: list) -> Gtk.Box:
    """Sektion 'Wissenslücken (N)' mit kompakten Eintraegen."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    header = Gtk.Label(label=f"Wissenslücken ({len(luecken)})")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    if not luecken:
        leer = Gtk.Label(label="(keine qualifizierten Lücken in diesem Turn)")
        leer.set_xalign(0.0)
        leer.add_css_class("dim-label")
        section.append(leer)
        return section

    for luecke in luecken:
        section.append(_build_luecken_row(luecke))

    return section


def _build_luecken_row(luecke: dict) -> Gtk.Box:
    """● Konzept (gekuerzt)  QUELLE  rel=1.234"""
    konzept:  str   = str(luecke.get("konzept") or "")
    quelle:   str   = str(luecke.get("quelle") or "?").upper()
    relevanz: float = float(luecke.get("relevanz", 0.0) or 0.0)

    auszug: str = konzept if len(konzept) <= 80 else konzept[:77] + "…"

    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    bullet = Gtk.Label(label="●")
    bullet.add_css_class("accent")
    row.append(bullet)

    konzept_label = Gtk.Label(label=auszug)
    konzept_label.set_xalign(0.0)
    konzept_label.set_hexpand(True)
    konzept_label.set_wrap(True)
    konzept_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    row.append(konzept_label)

    quelle_label = Gtk.Label(label=quelle)
    quelle_label.set_width_chars(4)
    quelle_label.add_css_class("caption")
    quelle_label.add_css_class("dim-label")
    row.append(quelle_label)

    rel_label = Gtk.Label(label=f"rel={relevanz:.3f}")
    rel_label.set_xalign(1.0)
    rel_label.add_css_class("caption")
    row.append(rel_label)

    return row


def _build_farbton_section(farbton: str) -> Gtk.Box:
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    header = Gtk.Label(label="Farbton")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    frame = Gtk.Frame()
    frame.set_margin_top(2)

    inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    inner.set_margin_start(8)
    inner.set_margin_end(8)
    inner.set_margin_top(6)
    inner.set_margin_bottom(6)

    if farbton:
        text_label = Gtk.Label(label=farbton)
        text_label.set_xalign(0.0)
        text_label.set_wrap(True)
        text_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        text_label.set_selectable(True)
    else:
        text_label = Gtk.Label(label="(kein Farbton in diesem Turn)")
        text_label.set_xalign(0.0)
        text_label.add_css_class("dim-label")

    inner.append(text_label)
    frame.set_child(inner)
    section.append(frame)

    return section
