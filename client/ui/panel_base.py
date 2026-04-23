"""
Abstrakte Basisklasse für alle Panels.

Ein Panel ist ein ``Gtk.Box`` mit drei Zonen (Header / Content / Footer):

    ┌────────────────────────────────────────────┐
    │ [User: meister ▼] [↻]                      │  ← Header (optional)
    ├────────────────────────────────────────────┤
    │                                            │
    │   Panel-Inhalt (von Subklasse befüllt)     │  ← content_area
    │                                            │
    ├────────────────────────────────────────────┤
    │ Letzte Aktualisierung: HH:MM:SS            │  ← Footer
    └────────────────────────────────────────────┘

Subklassen überschreiben die Klassen-Attribute (``PANEL_ID``,
``PANEL_LABEL``, …) und implementieren :meth:`load_data` sowie
:meth:`_update_ui`. Das Threading-Muster (REST-Aufruf im Hintergrund-
Thread, UI-Update via ``GLib.idle_add``) lebt hier in der Basisklasse.

Sprach-Regeln: Code/Bezeichner englisch, UI-Texte und Log-Meldungen
deutsch.
"""

import datetime
import logging
import threading

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402

from config import (  # noqa: E402
    DEFAULT_USER_ID,
    GespraechsPerspektive,
    PERSPEKTIVEN,
)


logger = logging.getLogger(__name__)


class PanelBase(Gtk.Box):
    """Gemeinsame Basis für alle Nova-Panels.

    Subklassen müssen die Klassen-Attribute überschreiben und in
    :meth:`_build_content` ihre eigene Darstellung in :attr:`content_area`
    einhängen. Daten-Ladung erfolgt in :meth:`load_data`, UI-Update in
    :meth:`_update_ui`.
    """

    # ─── Klassen-Attribute (von Subklassen überschrieben) ────────────
    PANEL_ID: str = ""
    PANEL_LABEL: str = ""
    UNIQUE: bool = True
    CATEGORY: str = "on_demand"  # turn_reactive | on_demand | query | log_stream
    NEEDS_USER_SELECTOR: bool = True
    DEFAULT_WIDTH: int = 500
    DEFAULT_HEIGHT: int = 400

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        logger.debug(
            f"Panel '{self.PANEL_ID}' wird initialisiert "
            f"(UNIQUE={self.UNIQUE}, CATEGORY={self.CATEGORY})"
        )

        # Einheitliche Ränder für alle Panels.
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_spacing(6)

        self._user_dropdown: Gtk.DropDown | None = None
        self._footer_label: Gtk.Label = Gtk.Label()
        self._footer_label.set_xalign(0.0)

        self._build_header()
        self._build_content_area()
        self._build_footer()

        # Subklassen haken ihre eigene Darstellung in content_area ein.
        self._build_content()

    # ═══════════════════════════════════════════════════════════════
    # UI-Aufbau
    # ═══════════════════════════════════════════════════════════════
    def _build_header(self) -> None:
        """Legt Header-Zeile mit Perspektive-Selector und Aktualisieren-Button an."""
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        if self.NEEDS_USER_SELECTOR:
            label = Gtk.Label(label="Perspektive:")
            header.append(label)

            string_list = Gtk.StringList()
            for p in PERSPEKTIVEN:
                string_list.append(p.label)

            self._user_dropdown = Gtk.DropDown(model=string_list)
            # Vorauswahl: erste Perspektive mit user_id == DEFAULT_USER_ID
            # und beobachter == "user", sonst der erste Eintrag.
            default_index: int = 0
            for idx, p in enumerate(PERSPEKTIVEN):
                if p.user_id == DEFAULT_USER_ID and p.beobachter == "user":
                    default_index = idx
                    break
            self._user_dropdown.set_selected(default_index)
            self._user_dropdown.connect("notify::selected", self._on_user_changed)
            header.append(self._user_dropdown)

        # Spacer zwischen Dropdown und Refresh-Button.
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        header.append(spacer)

        refresh_button = Gtk.Button(label="↻")
        refresh_button.set_tooltip_text("Aktualisieren")
        refresh_button.connect("clicked", lambda _btn: self.refresh())
        header.append(refresh_button)

        self.append(header)
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

    def _build_content_area(self) -> None:
        """Platzhalter-Box, die Subklassen befüllen."""
        self.content_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.content_area.set_vexpand(True)
        self.content_area.set_hexpand(True)
        self.append(self.content_area)

    def _build_footer(self) -> None:
        """Footer-Zeile mit Zeitstempel."""
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        self._footer_label.set_text("Noch nicht geladen")
        self._footer_label.add_css_class("dim-label")
        self._footer_label.set_margin_top(2)
        self.append(self._footer_label)

    def _build_content(self) -> None:
        """Von Subklasse überschreiben — befüllt :attr:`content_area`."""
        pass

    # ═══════════════════════════════════════════════════════════════
    # Öffentliche API
    # ═══════════════════════════════════════════════════════════════
    @property
    def current_perspektive(self) -> GespraechsPerspektive:
        """Liefert die aktuell gewählte Gesprächspaar-Perspektive."""
        if self._user_dropdown is None:
            return PERSPEKTIVEN[0]

        index: int = self._user_dropdown.get_selected()
        if 0 <= index < len(PERSPEKTIVEN):
            return PERSPEKTIVEN[index]
        return PERSPEKTIVEN[0]

    @property
    def user_id(self) -> str:
        """API-``user_id`` der aktuellen Perspektive (für Logausgaben)."""
        return self.current_perspektive.user_id

    def _get_api_params(self) -> dict:
        """Liefert die API-Parameter für die aktuell gewählte Perspektive."""
        p: GespraechsPerspektive = self.current_perspektive
        return {
            "user_id":      p.user_id,
            "character_id": p.character_id,
            "beobachter":   p.beobachter,
        }

    def refresh(self) -> None:
        """Lädt Panel-Daten in einem Hintergrund-Thread neu."""
        logger.debug(
            f"Panel '{self.PANEL_ID}' wird aktualisiert "
            f"(perspektive='{self.current_perspektive.label}')"
        )
        thread = threading.Thread(
            target=self._load_in_thread,
            name=f"panel-{self.PANEL_ID}-refresh",
            daemon=True,
        )
        thread.start()

    def load_data(self):
        """Abstrakt — lädt Daten vom Server. Blockiert, läuft im Thread."""
        raise NotImplementedError(
            f"Panel '{self.PANEL_ID}' muss load_data() implementieren"
        )

    def on_turn_received(self, turn_data: dict) -> None:
        """Wird bei jedem SSE-Answer aufgerufen. Default: nichts tun.

        Turn-reactive Panels überschreiben diese Methode, um sich bei
        neuen Turns selbst zu aktualisieren.
        """
        pass

    # ═══════════════════════════════════════════════════════════════
    # Threading-Infrastruktur
    # ═══════════════════════════════════════════════════════════════
    def _load_in_thread(self) -> None:
        """Ruft :meth:`load_data` auf und delegiert UI-Update an den UI-Thread."""
        try:
            data = self.load_data()
            GLib.idle_add(self._handle_loaded, data)
        except Exception as fehler:
            logger.error(f"Panel '{self.PANEL_ID}': Laden fehlgeschlagen: {fehler}")
            GLib.idle_add(self._show_error, str(fehler))

    def _handle_loaded(self, data) -> bool:
        """UI-Thread: Daten an Subklasse geben und Footer aktualisieren."""
        try:
            self._update_ui(data)
            self._update_footer_timestamp()
            logger.info(f"Panel '{self.PANEL_ID}' aktualisiert")
        except Exception as fehler:
            logger.error(f"Panel '{self.PANEL_ID}': UI-Update fehlgeschlagen: {fehler}")
            self._show_error(str(fehler))
        return False  # idle_add: nur einmal ausführen

    def _update_ui(self, data) -> None:
        """Von Subklasse überschreiben — baut die Inhalte in :attr:`content_area`."""
        pass

    def _show_error(self, message: str) -> bool:
        """UI-Thread: Fehler im Footer anzeigen."""
        self._footer_label.set_text(f"Fehler: {message}")
        return False

    def _update_footer_timestamp(self) -> None:
        """Aktualisiert den Zeitstempel im Footer auf HH:MM:SS."""
        now: str = datetime.datetime.now().strftime("%H:%M:%S")
        self._footer_label.set_text(f"Aktualisiert: {now}")

    # ═══════════════════════════════════════════════════════════════
    # Signal-Handler
    # ═══════════════════════════════════════════════════════════════
    def _on_user_changed(self, *args) -> None:
        """Wird ausgelöst, wenn der Perspektive-Selector umgeschaltet wird."""
        logger.debug(
            f"Panel '{self.PANEL_ID}': Perspektive gewechselt auf "
            f"'{self.current_perspektive.label}'"
        )
        self.refresh()
