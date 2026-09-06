"""
Statuszeile am unteren Fensterrand.

Zeigt den Verbindungsstatus (links), die Kosten (Mitte) und den
Pixie-Zustand (rechts).
Die Labels werden über dedizierte Setter aktualisiert, die aus dem
UI-Thread aufgerufen werden müssen (GLib.idle_add beim Aufruf aus Threads).
"""

import logging

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from ui.formatierung import kosten_zeile  # noqa: E402


logger = logging.getLogger(__name__)


class StatusBar(Gtk.Box):
    """Kleine, dreispaltige Statuszeile (Verbindung · Kosten · Pixie)."""

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

        # Mittleres Label — was der Betrieb kostet
        #
        # **Drei Zahlen, die nicht dasselbe messen.** Der Turn zaehlt nur
        # den Gespraechsdurchlauf; Tag und Monat zaehlen **jeden** Aufruf,
        # auch Pixie und den Tageslauf. Die Tagessumme ist deshalb groesser
        # als die Summe der Turns — das ist der Hintergrund, nicht ein
        # Rechenfehler. Bis zur ersten Antwort steht ein Strich und keine
        # Null: nicht ermittelt ist nicht dasselbe wie kostenlos.
        self._kosten_label = Gtk.Label(label="Turn: — · Heute: — · Monat: —")
        self._kosten_label.set_xalign(0.5)
        self._kosten_label.add_css_class("nova-statusbar-label")

        # Rechtes Label — Pixie-Zustand
        self._pixie_label = Gtk.Label(label="Pixie: idle")
        self._pixie_label.set_xalign(1.0)
        self._pixie_label.add_css_class("nova-statusbar-label")

        self.append(self._connection_label)
        self.append(self._kosten_label)
        self.append(self._pixie_label)

        logger.debug("StatusBar initialisiert (Verbindung + Kosten + Pixie-Zustand)")

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

    def set_kosten(
        self,
        turn:  float | None,
        heute: float | None,
        monat: float | None,
    ) -> None:
        """Die drei Betraege (mittleres Label) setzen.

        Vorbedingung: keine — `None` heisst *nicht ermittelt* und wird als
        Strich gezeigt.
        Nachbedingung: Das Label traegt drei Posten.
        Fehlerfaelle: keine.

        **Ein Strich ist keine Null.** Faellt die Abfrage aus, stuende dort
        sonst `$0.0000` — und ein Betrieb, der nichts kostet, sieht aus wie
        einer, der nicht laeuft.

        Args:
            turn: Kosten des letzten Turns in USD.
            heute: Kosten des laufenden Tages (UTC), Hintergrund eingerechnet.
            monat: Kosten des laufenden Kalendermonats.
        """
        # Die Form steht in `ui/formatierung.py` — dort ist sie ohne GTK
        # pruefbar, und die Statusleiste bleibt eine Anzeige.
        text: str = kosten_zeile(turn, heute, monat)
        logger.debug(f"StatusBar: Kosten -> '{text}'")
        self._kosten_label.set_text(text)
