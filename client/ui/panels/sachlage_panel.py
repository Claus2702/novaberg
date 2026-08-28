"""
Kontext-Panel — zeigt die fortgeschriebene Sachlage des Gespraechs.

Das Panel ist ``turn_reactive`` und holt seine Daten ueber
``GET /drive/sachlage``. Der Sachlage-Knoten (server:
``graph/nodes/sachlage.py``, Konzept ``novaberg-thinking-lage_k.md``)
schreibt die Sachlage je Turn fortgeschrieben nach Redis; das Panel laedt
beim Oeffnen und nach jedem Turn neu.

Anzeige (kompakt):

    Kontext                                    fortgeschrieben · vor 12 s
    Worum es geht:   Ein anstehender Geburtstag
    Nutzerziel:      vermutlich Planung und Vorbereitung
    Ausdrucksweise:  begeistert

    ● Geburtstag  (vorgang, akut)
      ✓ anlass: erwaehnt im Turn
      ○ wer  ○ wann  ○ geschenk

    ○ Rasen  (objekt, latent)

Latente Objekte stehen ohne offene Eigenschaften — die Smalltalk-Schranke
des Knotens leert sie serverseitig; das Panel zeigt nur, was ankommt.

Sprach-Regeln: Code/Bezeichner englisch, UI-Texte und Logs deutsch.
"""

import logging

import requests

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from config import PANEL_REQUEST_TIMEOUT, SERVER_URL  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402


logger = logging.getLogger(__name__)


class SachlagePanel(PanelBase):
    """Anzeige der Sachlage: Gegenstand, Nutzerziel, Referenzobjekte."""

    PANEL_ID    = "sachlage"
    PANEL_LABEL = "🫧 Kontext"
    UNIQUE      = True
    CATEGORY    = "turn_reactive"
    NEEDS_USER_SELECTOR = False
    DEFAULT_WIDTH  = 480
    DEFAULT_HEIGHT = 520

    def _build_content(self) -> None:
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self._outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        scroll.set_child(self._outer_box)

        placeholder = Gtk.Label(label="Noch keine Sachlage empfangen")
        placeholder.set_xalign(0.0)
        placeholder.add_css_class("dim-label")
        self._outer_box.append(placeholder)

        self.content_area.append(scroll)

    def load_data(self) -> dict:
        """Holt die aktuelle Sachlage vom Server (Redis-Snapshot)."""
        url: str = f"{SERVER_URL}/drive/sachlage"
        logger.debug(f"SachlagePanel: GET {url}")
        response = requests.get(url, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json() or {}

    def _update_ui(self, data: dict) -> None:
        """Baut Kopf und Objekt-Sektionen aus der aktuellen Sachlage neu auf."""
        _clear_box(self._outer_box)

        if not data:
            placeholder = Gtk.Label(label="Noch keine Sachlage empfangen")
            placeholder.set_xalign(0.0)
            placeholder.add_css_class("dim-label")
            self._outer_box.append(placeholder)
            return

        self._outer_box.append(_build_head_section(data))

        objekte: list = data.get("objekte") or []
        for objekt in objekte:
            if isinstance(objekt, dict):
                self._outer_box.append(_build_object_section(objekt))
        if not objekte:
            leer = Gtk.Label(label="Keine Referenzobjekte im Raum")
            leer.set_xalign(0.0)
            leer.add_css_class("dim-label")
            self._outer_box.append(leer)

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


def _alter_text(sekunden: float) -> str:
    """Menschlich lesbares Alter des Snapshots."""
    if sekunden < 90:
        return f"vor {sekunden:.0f} s"
    if sekunden < 5400:
        return f"vor {sekunden / 60:.0f} min"
    return f"vor {sekunden / 3600:.1f} h"


def _build_head_section(data: dict) -> Gtk.Box:
    """Kopfblock: Ueberschrift mit Herkunft/Alter, drei Verstehens-Zeilen."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    kopf = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    header = Gtk.Label(label="Kontext")
    header.set_xalign(0.0)
    header.set_hexpand(True)
    header.add_css_class("heading")
    kopf.append(header)

    herkunft: str = str(data.get("herkunft", ""))
    alter = data.get("alter_sekunden")
    meta_teile: list[str] = [t for t in (
        herkunft,
        _alter_text(float(alter)) if alter is not None else "",
    ) if t]
    if meta_teile:
        meta = Gtk.Label(label=" · ".join(meta_teile))
        meta.add_css_class("dim-label")
        kopf.append(meta)
    section.append(kopf)

    for titel, schluessel in (
        ("Worum es geht", "gegenstand"),
        ("Nutzerziel", "nutzerziel"),
        ("Ausdrucksweise", "ausdrucksweise"),
    ):
        wert: str = str(data.get(schluessel) or "—")
        zeile = Gtk.Label(label=f"{titel}:  {wert}")
        zeile.set_xalign(0.0)
        zeile.set_wrap(True)
        section.append(zeile)

    return section


def _build_object_section(objekt: dict) -> Gtk.Box:
    """Ein Referenzobjekt: Name, Klasse, Akutheit, gedeckte/offene Eigenschaften."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    akut: bool = bool(objekt.get("akut"))
    marker: str = "●" if akut else "○"
    zustand: str = "akut" if akut else "latent"
    klasse: str = str(objekt.get("klasse") or "?")

    titel = Gtk.Label(
        label=f"{marker} {objekt.get('name', '?')}  ({klasse}, {zustand})")
    titel.set_xalign(0.0)
    titel.add_css_class("heading" if akut else "dim-label")
    section.append(titel)

    gedeckt: dict = objekt.get("gedeckt") or {}
    for eigenschaft, wert in list(gedeckt.items())[:6]:
        zeile = Gtk.Label(label=f"  ✓ {eigenschaft}: {wert}")
        zeile.set_xalign(0.0)
        zeile.set_wrap(True)
        section.append(zeile)

    offen: list = objekt.get("offen") or []
    if offen:
        zeile = Gtk.Label(
            label="  " + "  ".join(f"○ {o}" for o in offen[:5]))
        zeile.set_xalign(0.0)
        zeile.set_wrap(True)
        section.append(zeile)

    return section
