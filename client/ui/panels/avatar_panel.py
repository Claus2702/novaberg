"""Avatar-Panel: Novas Gesicht, das ihre Antworten mit Emotion und Lippenbewegung zeigt.

Das Panel lädt nichts vom Server. Jede Antwort wird über `utterance_from_turn` zur
Äußerung und über `puppet_cue` zum neuen Ziel der Puppe; der Mund spricht den Text
nach Lautzeiten, ohne Ton.

Eine Uhr für alles: Allein der Takt des Panels liest die Zeit, aus der Frame-Clock,
und gibt sie an Puppe und Äußerung weiter. Der Takt läuft nur, solange das Panel
sichtbar ist (`map` bis `unmap`) — die Registry baut je Öffnen eine neue Instanz,
einen Abbau-Hook gibt es nicht.

Die Bildebenen lädt das Panel einmal beim Aufbau aus `AVATAR_IMAGE_DIR`. Fehlen sie,
steht eine Meldung im Panel und eine Error-Zeile im Log; ein leeres Gesicht wird
nicht gezeichnet.
"""

import logging
import random

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402

from avatar.base_image import CairoCanvas, WarpCache  # noqa: E402
from avatar.compose import FaceTools, draw_face  # noqa: E402
from avatar.drawing_tools import CairoGradients  # noqa: E402
from avatar.layers import AvatarLayers, LayerError, load_layers  # noqa: E402
from avatar.pose import Pose  # noqa: E402
from avatar.puppet import (  # noqa: E402
    Puppet,
    Utterance,
    new_puppet,
    puppet_cue,
    puppet_step,
    utterance_from_turn,
)
from config import AVATAR_IMAGE_DIR  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402

logger = logging.getLogger(__name__)

MICROSECONDS = 1_000_000  # Frame-Clock zählt in Mikrosekunden


class AvatarPanel(PanelBase):
    """Novas Gesicht: Emotion aus der Antwort, Mund nach dem Text, Leben ohne Antwort."""

    PANEL_ID = "avatar"
    PANEL_LABEL = "🙂 Avatar"
    UNIQUE = True
    CATEGORY = "turn_reactive"
    REACTS_TO_IMPULSE = True
    NEEDS_USER_SELECTOR = False
    DEFAULT_WIDTH = 480
    DEFAULT_HEIGHT = 540

    def _build_content(self) -> None:
        """Lädt die Bildebenen und baut die Zeichenfläche oder die Meldung ohne Bilder."""
        # ── Eingabe-Validierung ──
        self._layers: AvatarLayers | None = None
        self._puppet: Puppet | None = None
        self._pending: Utterance | None = None
        self._pose: Pose | None = None
        self._tick_id: int | None = None
        self._rng = random.Random()
        self._tools = FaceTools(CairoGradients(), CairoCanvas(), WarpCache())
        try:
            self._layers = load_layers(AVATAR_IMAGE_DIR)
        except LayerError as error:
            logger.error(f"AvatarPanel: Bildebenen nicht geladen: {error}")
            self._show_message(f"Avatar nicht verfügbar — die Bildebenen fehlen.\n{error}")
            return

        # ── Verarbeitung ──
        self._area = Gtk.DrawingArea()
        self._area.set_hexpand(True)
        self._area.set_vexpand(True)
        self._area.set_draw_func(self._on_draw)
        self._area.connect("map", self._on_map)
        self._area.connect("unmap", self._on_unmap)
        self.content_area.append(self._area)

        # ── Ausgabe-Verifikation ──
        if self._area.get_parent() is not self.content_area:
            raise RuntimeError("AvatarPanel: Zeichenfläche nicht eingehängt")

    def _show_message(self, text: str) -> None:
        """Ersetzt den Inhalt des Panels durch eine Meldung."""
        # ── Eingabe-Validierung ──
        if not text:
            raise ValueError("AvatarPanel: Meldung ohne Text")

        # ── Verarbeitung ──
        child = self.content_area.get_first_child()
        while child is not None:
            self.content_area.remove(child)
            child = self.content_area.get_first_child()
        label = Gtk.Label(label=text)
        label.set_wrap(True)
        label.set_xalign(0.0)
        label.add_css_class("dim-label")
        self.content_area.append(label)

        # ── Ausgabe-Verifikation ──
        if self.content_area.get_first_child() is not label:
            raise RuntimeError("AvatarPanel: Meldung nicht eingehängt")

    def load_data(self) -> dict:
        """Kein REST: Das Panel lebt von den Antworten; leere Daten halten die Fußzeile ruhig."""
        return {}

    # ═══════════════════════════════════════════════════════════════
    # Takt: von map bis unmap, eine Uhr für alles
    # ═══════════════════════════════════════════════════════════════
    def _on_map(self, _widget: Gtk.Widget) -> None:
        """Startet den Takt, sobald das Panel sichtbar wird."""
        # ── Eingabe-Validierung ──
        if _widget is not self._area:
            raise RuntimeError(f"AvatarPanel: map von fremdem Widget {_widget!r}")

        # ── Verarbeitung ──
        if self._tick_id is None:
            self._tick_id = self._area.add_tick_callback(self._on_tick)
            logger.debug("AvatarPanel: Takt gestartet")

    def _on_unmap(self, _widget: Gtk.Widget) -> None:
        """Hält den Takt an, sobald das Panel nicht mehr sichtbar ist."""
        # ── Eingabe-Validierung ──
        if _widget is not self._area:
            raise RuntimeError(f"AvatarPanel: unmap von fremdem Widget {_widget!r}")

        # ── Verarbeitung ──
        if self._tick_id is not None:
            self._area.remove_tick_callback(self._tick_id)
            self._tick_id = None
            logger.debug("AvatarPanel: Takt angehalten")

    def _on_tick(self, widget: Gtk.Widget, frame_clock: object) -> bool:
        """Ein Bild: Zeit aus der Frame-Clock, wartende Äußerung übergeben, Pose rechnen.

        Ein Fehler hält den Takt an und ersetzt das Gesicht durch eine Meldung — ein
        stehendes Gesicht ohne Meldung sähe aus wie ein ruhiges.
        """
        # ── Eingabe-Validierung ──
        now = frame_clock.get_frame_time() / MICROSECONDS

        # ── Verarbeitung ──
        try:
            if self._puppet is None:
                self._puppet = new_puppet(now, self._rng)
            if self._pending is not None:
                utterance, self._pending = self._pending, None
                puppet_cue(self._puppet, utterance, now)
            self._pose = puppet_step(self._puppet, now)
        except Exception as error:
            logger.exception(f"AvatarPanel: Bild bei {now:.3f} s fehlgeschlagen: {error}")
            self._tick_id = None
            self._show_message(f"Avatar angehalten — Fehler im Takt.\n{error}")
            return GLib.SOURCE_REMOVE
        widget.queue_draw()

        # ── Ausgabe-Verifikation ──
        if self._pose is None:
            raise RuntimeError(f"AvatarPanel: Takt bei {now:.3f} s ohne Pose")
        return GLib.SOURCE_CONTINUE

    def _on_draw(self, _area: Gtk.DrawingArea, cr: object, width: int, height: int) -> None:
        """Zeichnet die letzte Pose quadratisch, mittig und so groß, wie das Fenster erlaubt."""
        # ── Eingabe-Validierung ──
        size = min(width, height)
        if self._pose is None or self._layers is None or size <= 0:
            return

        # ── Verarbeitung ──
        cr.save()
        cr.translate((width - size) / 2, (height - size) / 2)
        try:
            draw_face(cr, size, self._pose, self._layers, self._tools)
        except Exception as error:
            logger.exception(f"AvatarPanel: Zeichnen fehlgeschlagen: {error}")
            self._pose = None
            self._on_unmap(self._area)
            message = f"Avatar angehalten — Fehler beim Zeichnen.\n{error}"
            GLib.idle_add(self._show_message, message)
        finally:
            cr.restore()

        # Keine Ausgabe-Verifikation: draw_face prüft Pose und Ebenen selbst und stellt `cr`
        # wieder her.

    # ═══════════════════════════════════════════════════════════════
    # Turn-Reactive: jede Antwort wird eine Äußerung
    # ═══════════════════════════════════════════════════════════════
    def on_turn_received(self, turn_data: dict) -> None:
        """Merkt die Äußerung vor; der nächste Takt übergibt sie mit der Zeit seines Bildes."""
        # ── Eingabe-Validierung ──
        utterance = utterance_from_turn(turn_data)

        # ── Verarbeitung ──
        self._pending = utterance
        # Keine Ausgabe-Verifikation: Die Zuweisung kann nicht scheitern; die Zeile protokolliert.
        logger.debug(
            f"AvatarPanel: Äußerung vorgemerkt (Sektor {utterance.sector}, "
            f"Arousal {utterance.arousal:.2f}, {len(utterance.text)} Zeichen)"
        )
