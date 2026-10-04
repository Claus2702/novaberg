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
    new_puppet,
    puppet_status,
    puppet_step,
    utterance_from_turn,
)
from avatar.status_text import (  # noqa: E402
    BandSegment,
    band_segments,
    status_due,
    status_lines,
)
from config import AVATAR_IMAGE_DIR  # noqa: E402
from ui.avatar_feed import AvatarFeed  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402
from ui.status_label import set_status_text, status_label  # noqa: E402
from ui.work_events import WorkEvent  # noqa: E402

logger = logging.getLogger(__name__)

MICROSECONDS = 1_000_000  # Frame-Clock zählt in Mikrosekunden
BAND_HEIGHT = 22  # Höhe des Bandes in Pixeln
BAND_FONT = 11.0
BAND_RUNNING = (0.35, 0.60, 0.90, 0.95)  # die laufende Form
BAND_IDLE = (0.50, 0.50, 0.50, 0.35)  # die übrigen Formen
BAND_TEXT = (0.95, 0.95, 0.95, 1.0)


class AvatarPanel(PanelBase):
    """Novas Gesicht: Emotion aus der Antwort, Mund nach dem Text, Leben ohne Antwort."""

    PANEL_ID = "avatar"
    PANEL_LABEL = "🙂 Avatar"
    UNIQUE = True
    CATEGORY = "turn_reactive"
    REACTS_TO_IMPULSE = True
    REACTS_TO_WORK = True
    NEEDS_USER_SELECTOR = False
    DEFAULT_WIDTH = 480
    DEFAULT_HEIGHT = 540

    def _build_content(self) -> None:
        """Lädt die Bildebenen und baut die Zeichenfläche oder die Meldung ohne Bilder."""
        # ── Eingabe-Validierung ──
        self._layers: AvatarLayers | None = None
        self._puppet: Puppet | None = None
        self._feed = AvatarFeed()
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
        self._build_status_view()

        # ── Ausgabe-Verifikation ──
        if self._area.get_parent() is not self.content_area:
            raise RuntimeError("AvatarPanel: Zeichenfläche nicht eingehängt")

    def _build_status_view(self) -> None:
        """Hängt die Phasenanzeige unter das Gesicht: vier Zeilen und das Band.

        Vorbedingung: `content_area` und die Zeichenfläche des Gesichts stehen.
        Nachbedingung: die Anzeige hängt leer unter dem Gesicht (`_band` leer, `_status_at`
        None, `_band_area` das Band), oder `_status_labels` ist None und eine Error-Zeile
        steht im Log; das Gesicht läuft in beiden Fällen weiter.
        """
        # ── Eingabe-Validierung ──
        self._status_labels: list[Gtk.Label] | None = None
        self._status_at: float | None = None
        self._band: list[BandSegment] = []

        # ── Verarbeitung ──
        try:
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            labels = [status_label() for _ in range(4)]  # Zustand, Form, Fortgang, Spanne
            self._band_area = Gtk.DrawingArea()
            self._band_area.set_content_height(BAND_HEIGHT)
            self._band_area.set_hexpand(True)
            self._band_area.set_draw_func(self._on_draw_band)
            for child in (labels[0], labels[1], labels[2], self._band_area, labels[3]):
                box.append(child)
            self.content_area.append(box)
        except Exception as error:
            logger.exception(f"AvatarPanel: Phasenanzeige nicht gebaut: {error}")
            return
        self._status_labels = labels

        # Keine Ausgabe-Verifikation: Ohne Anzeige läuft das Gesicht weiter, der Fehler steht
        # schon im Log.

    def _refresh_status(self, now: float) -> None:
        """Zieht die Anzeige nach, höchstens alle 120 ms; ein Fehler schaltet nur die Anzeige ab.

        Vorbedingung: `now` ist die Zeit des Bildes, das `puppet_step` eben gerechnet hat.
        Nachbedingung: die Anzeige zeigt die Phase zu `now`, wenn das Intervall verstrichen
        war; sonst blieb sie stehen. Bei einem Fehler steht er im Log und in der ersten Zeile.
        """
        # ── Eingabe-Validierung ──
        if self._status_labels is None or self._puppet is None:
            return
        if not status_due(self._status_at, now):
            return

        # ── Verarbeitung ──
        self._status_at = now
        try:
            status = puppet_status(self._puppet, now)
            lines = status_lines(status)
            self._band = band_segments(status)
            texts = (lines.state, lines.form, lines.progress, lines.span)
            for index, (label, text) in enumerate(zip(self._status_labels, texts, strict=True)):
                set_status_text(label, text, bold=index == 1)
            self._band_area.queue_draw()
        except Exception as error:
            logger.exception(f"AvatarPanel: Phasenanzeige bei {now:.3f} s fehlgeschlagen: {error}")
            self._status_labels[0].set_text(f"Phasenanzeige angehalten — Fehler: {error}")
            self._status_labels = None
        # Keine Ausgabe-Verifikation: Der Fehlerweg meldet im Log und im Panel.

    def _on_draw_band(self, _area: Gtk.DrawingArea, cr: object, width: int, height: int) -> None:
        """Zeichnet das Band: Breite nach Dauer, die laufende Form hervorgehoben.

        Vorbedingung: `_band` trägt Abschnitte, deren Anteile 1 ergeben.
        Nachbedingung: ein Kasten je Form mit ihrer Kennung; ohne Band wird nichts gezeichnet.
        """
        # ── Eingabe-Validierung ──
        if not self._band or width <= 0 or height <= 0:
            return

        # ── Verarbeitung ──
        cr.set_font_size(BAND_FONT)
        left = 0.0
        for segment in self._band:
            span = segment.share * width
            if segment.running:
                cr.set_source_rgba(*BAND_RUNNING)
            else:
                cr.set_source_rgba(*BAND_IDLE)
            cr.rectangle(left + 1, 0, max(span - 2, 1), height)
            cr.fill()
            cr.set_source_rgba(*BAND_TEXT)
            cr.move_to(left + 4, height - 6)
            cr.show_text(segment.form_id)
            left += span
        # Keine Ausgabe-Verifikation: `band_segments` hat die Anteile geprüft.

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
        """Ein Bild: Zeit aus der Frame-Clock, Wartendes in Reihenfolge übergeben, Pose rechnen.

        Ein Fehler hält den Takt an und ersetzt das Gesicht durch eine Meldung — ein
        stehendes Gesicht ohne Meldung sähe aus wie ein ruhiges.
        """
        # ── Eingabe-Validierung ──
        now = frame_clock.get_frame_time() / MICROSECONDS

        # ── Verarbeitung ──
        try:
            if self._puppet is None:
                self._puppet = new_puppet(now, self._rng)
            self._feed.deliver(self._puppet, now)
            self._pose = puppet_step(self._puppet, now)
        except Exception as error:
            logger.exception(f"AvatarPanel: Bild bei {now:.3f} s fehlgeschlagen: {error}")
            self._tick_id = None
            self._show_message(f"Avatar angehalten — Fehler im Takt.\n{error}")
            return GLib.SOURCE_REMOVE
        widget.queue_draw()
        self._refresh_status(now)

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
        self._feed.add(utterance)
        # Keine Ausgabe-Verifikation: `add` prüft selbst, dass der Eintrag vorgemerkt ist.
        logger.debug(
            f"AvatarPanel: Äußerung vorgemerkt (Sektor {utterance.sector}, "
            f"Arousal {utterance.arousal:.2f}, {len(utterance.text)} Zeichen)"
        )

    def on_work_event(self, event: WorkEvent) -> None:
        """Merkt das Ereignis hinter den bisherigen vor; der nächste Takt übergibt es."""
        # Keine Eingabe-Validierung und keine Ausgabe-Verifikation: `add` weist ab, was kein
        # Arbeitsereignis ist, und prüft selbst, dass der Eintrag vorgemerkt ist.
        self._feed.add(event)
        logger.debug(f"AvatarPanel: {type(event).__name__} vorgemerkt")
