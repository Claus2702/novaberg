"""
Radar-Diagramm-Widget auf Basis von ``Gtk.DrawingArea`` und Cairo.

Zeichnet eine beliebige Zahl von Achsen auf einem Stern. Jede Achse zeigt
einen Wert (0.0–1.0); die Datenpunkte werden als geschlossenes,
halbtransparent gefülltes Polygon verbunden.

**Das Widget kennt seinen Gegenstand nicht.** Die Achsen-Beschriftungen
kommen vom Aufrufer und bestimmen zugleich, wie viele Achsen gezeichnet
werden — acht Plutchik-Sektoren im Emotionen-Panel, zwölf bzw. zehn
Charakter-Speichen im Charakter-Panel. Eine feste Achsenzahl im Widget
hiesse, es fuer jeden weiteren Gegenstand zu kopieren.

Sprach-Regeln: Code/Bezeichner englisch, UI-Texte deutsch.
"""

import logging
import math

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from config import (  # noqa: E402
    RADAR_DATA_DOT_COLOR,
    RADAR_DATA_FILL_COLOR,
    RADAR_DATA_STROKE_COLOR,
    RADAR_GRID_COLOR,
    RADAR_LABEL_COLOR,
    RADAR_NABE_COLOR,
    RADAR_TITLE_COLOR,
)


logger = logging.getLogger(__name__)


# Weniger als drei Achsen ergeben kein Polygon, sondern eine Strecke.
_MIN_AXES: int = 3


class RadarChart(Gtk.DrawingArea):
    """Radar-Diagramm mit so vielen Achsen, wie Beschriftungen übergeben wurden."""

    def __init__(self, labels: list[str], title: str = "", size: int = 160):
        """Erstellt ein Radar-Diagramm über den übergebenen Achsen.

        Args:
            labels: Kurzformen der Achsen, in Zeichenreihenfolge (oben
                beginnend, im Uhrzeigersinn). Ihre Anzahl ist die Achsenzahl.
            title: Überschrift über dem Diagramm (z.B. "Session", "KZG").
            size: Breite und Höhe in Pixel.

        Raises:
            ValueError: Bei weniger als drei Beschriftungen.
        """
        # ── Eingabe ──────────────────────────────────────────────────
        if len(labels) < _MIN_AXES:
            raise ValueError(
                f"RadarChart braucht mindestens {_MIN_AXES} Achsen, "
                f"bekam {len(labels)}"
            )

        # ── Verarbeitung ─────────────────────────────────────────────
        super().__init__()
        self._labels: list[str] = list(labels)
        self._num_axes: int = len(self._labels)
        self._title: str = title
        self._size: int = size
        # ``None`` heisst "keine Daten" und ist von einem Vektor aus Nullen
        # verschieden: Ein Nullpolygon sieht aus wie eine Messung, die
        # ueberall nichts gefunden hat. Nur ``set_data`` fuellt dieses Feld.
        self._values: list[float] | None = None
        self._leer_grund: str = "noch nicht geladen"
        # Anteil, um den das gerechnete Ergebnis von der Nabe abliegt:
        # -1.0 volle Auslenkung zur zweiten Haelfte, +1.0 zur ersten,
        # 0.0 genau auf der Nabe. ``None`` heisst "gilt hier nicht".
        self._nabe_versatz: float | None = None

        self.set_content_width(size)
        self.set_content_height(size)
        self.set_draw_func(self._on_draw)

    def set_data(self, axis_values: list[float]) -> None:
        """Setzt die Achsenwerte (0.0–1.0) und löst Neuzeichnung aus.

        Args:
            axis_values: Liste mit genau so vielen Floats, wie das Diagramm
                Achsen hat, in derselben Reihenfolge wie die Beschriftungen.

        Raises:
            ValueError: Wenn die Anzahl nicht zur Achsenzahl passt. Ein zu
                kurzer Vektor wird **nicht** mit Nullen aufgefüllt — eine
                aufgefüllte Achse sähe aus wie eine gemessene Null.
        """
        # ── Eingabe ──────────────────────────────────────────────────
        if len(axis_values) != self._num_axes:
            raise ValueError(
                f"RadarChart '{self._title}'.set_data erwartet "
                f"{self._num_axes} Werte, bekam {len(axis_values)}"
            )

        # ── Verarbeitung ─────────────────────────────────────────────
        self._values = [max(0.0, min(1.0, float(v))) for v in axis_values]
        logger.info(
            f"RadarChart '{self._title}' Achsenwerte: "
            + ", ".join(
                f"{k}={v:.2f}" for k, v in zip(self._labels, self._values)
            )
        )
        self.queue_draw()

    def set_nabe_versatz(self, anteil: float | None) -> None:
        """Zeigt, wie weit das gerechnete Ergebnis von der Nabe abliegt.

        Die erste Hälfte der Achsen zieht nach oben, die zweite nach unten;
        bei geradzahliger Achsenzahl trennt sie eine senkrechte Linie. Der
        Versatz wird deshalb **waagerecht** aufgetragen: nach rechts zur
        ersten Hälfte, nach links zur zweiten.

        Er ist bewusst kein Schwerpunkt der Fläche. Der Wert des Rades ist
        eine gewichtete Summe — jede Speiche zieht mit ihrem eigenen Betrag —,
        und ein geometrischer Schwerpunkt wäre eine andere Zahl, die nur so
        aussähe wie diese. Gezeichnet wird der abgelegte Wert selbst.

        Args:
            anteil: Abstand von der Nabe als Anteil der Spanne auf der
                jeweiligen Seite, im Bereich −1.0 bis +1.0. ``None``
                blendet die Anzeige aus.
        """
        if anteil is None:
            self._nabe_versatz = None
            self.queue_draw()
            return

        self._nabe_versatz = max(-1.0, min(1.0, float(anteil)))
        logger.info(
            f"RadarChart '{self._title}' Nabenversatz: {self._nabe_versatz:+.3f}"
        )
        self.queue_draw()

    def set_unbekannt(self, grund: str) -> None:
        """Verwirft die Daten und zeichnet nur Gitter, Achsen und den Grund.

        Für den Fall, dass keine Messung vorliegt — Zeile fehlt, JSON nicht
        lesbar, nie erhoben. Ein Diagramm mit lauter Nullen wäre an dieser
        Stelle keine Darstellung des Nichtwissens, sondern eine Behauptung.

        Args:
            grund: Kurzer Text, der im Zentrum steht (z.B. "nicht erhoben").
        """
        self._values = None
        self._leer_grund = grund
        # Ohne Speichen gibt es auch keine Bilanz aus ihnen.
        self._nabe_versatz = None
        logger.warning(f"RadarChart '{self._title}': ohne Daten — {grund}")
        self.queue_draw()

    def _on_draw(
        self, area: Gtk.DrawingArea, cr, width: int, height: int
    ) -> None:
        """Zeichnet Titel, Gitter, Datenfläche und Labels."""
        # Titel oben, klein und grau.
        title_height: float = 16.0
        if self._title:
            cr.select_font_face("Sans")
            cr.set_font_size(11)
            cr.set_source_rgba(*RADAR_TITLE_COLOR)
            extents = cr.text_extents(self._title)
            tx: float = (width - extents.width) / 2.0 - extents.x_bearing
            ty: float = 12.0
            cr.move_to(tx, ty)
            cr.show_text(self._title)

        # Radar-Bereich unterhalb des Titels, zentriert.
        radar_area_top: float = title_height
        radar_area_height: float = height - radar_area_top
        cx: float = width / 2.0
        cy: float = radar_area_top + radar_area_height / 2.0
        radius: float = max(10.0, (min(width, radar_area_height) - 40.0) / 2.0)

        self._draw_grid(cr, cx, cy, radius)
        if self._values is None:
            self._draw_leer(cr, cx, cy)
        else:
            self._draw_data(cr, cx, cy, radius)
        # Nach der Flaeche, damit die Bilanz nicht darunter verschwindet.
        self._draw_nabe(cr, cx, cy, radius)
        self._draw_labels(cr, cx, cy, radius)

    def _axis_angle(self, i: int) -> float:
        """Winkel der Achse ``i`` (0-basiert), Start oben, im Uhrzeigersinn."""
        return i * (2.0 * math.pi / self._num_axes) - math.pi / 2.0

    def _draw_grid(self, cr, cx: float, cy: float, radius: float) -> None:
        """Zeichnet konzentrische Ringe und die Achsen vom Zentrum nach außen."""
        cr.set_source_rgba(*RADAR_GRID_COLOR)
        cr.set_line_width(1.0)

        # Drei konzentrische Ringe bei 33 %, 66 %, 100 %.
        for frac in (0.33, 0.66, 1.0):
            r: float = radius * frac
            for i in range(self._num_axes):
                angle: float = self._axis_angle(i)
                x: float = cx + r * math.cos(angle)
                y: float = cy + r * math.sin(angle)
                if i == 0:
                    cr.move_to(x, y)
                else:
                    cr.line_to(x, y)
            cr.close_path()
            cr.stroke()

        # Achsen vom Zentrum nach außen.
        for i in range(self._num_axes):
            angle = self._axis_angle(i)
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            cr.move_to(cx, cy)
            cr.line_to(x, y)
            cr.stroke()

    def _draw_leer(self, cr, cx: float, cy: float) -> None:
        """Schreibt statt eines Polygons den Grund ins Zentrum."""
        cr.select_font_face("Sans")
        cr.set_font_size(9)
        cr.set_source_rgba(*RADAR_LABEL_COLOR)
        extents = cr.text_extents(self._leer_grund)
        cr.move_to(
            cx - extents.width / 2.0 - extents.x_bearing,
            cy + extents.height / 2.0,
        )
        cr.show_text(self._leer_grund)

    def _draw_data(self, cr, cx: float, cy: float, radius: float) -> None:
        """Zeichnet Datenpolygon (Füllung + Rand) und Datenpunkte."""
        points: list[tuple[float, float]] = []
        for i, value in enumerate(self._values):
            angle: float = self._axis_angle(i)
            r: float = radius * value
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

        # Füllung.
        cr.set_source_rgba(*RADAR_DATA_FILL_COLOR)
        for i, (x, y) in enumerate(points):
            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)
        cr.close_path()
        cr.fill_preserve()

        # Rand.
        cr.set_source_rgba(*RADAR_DATA_STROKE_COLOR)
        cr.set_line_width(1.5)
        cr.stroke()

        # Datenpunkte.
        cr.set_source_rgba(*RADAR_DATA_DOT_COLOR)
        for x, y in points:
            cr.arc(x, y, 3.0, 0.0, 2.0 * math.pi)
            cr.fill()

    def _draw_nabe(self, cr, cx: float, cy: float, radius: float) -> None:
        """Zeichnet die Nabe als Ring und das Ergebnis als versetzten Punkt.

        Der Ring sitzt immer im Zentrum und ist der Nullpunkt; der Punkt
        liegt waagerecht daneben. Beide werden auch bei Versatz 0.0
        gezeichnet — dass ein Ergebnis **genau** auf der Nabe liegt, ist
        eine Aussage und kein Grund, nichts zu zeigen.
        """
        if self._nabe_versatz is None:
            return

        cr.set_source_rgba(*RADAR_NABE_COLOR)
        cr.set_line_width(1.2)

        # Die Nabe: ein hohler Ring im Zentrum als Bezugspunkt.
        cr.arc(cx, cy, 3.0, 0.0, 2.0 * math.pi)
        cr.stroke()

        px: float = cx + radius * self._nabe_versatz

        # Die Strecke macht den Versatz als Versatz sichtbar; ohne sie waere
        # der Punkt nur ein Punkt an einer Stelle.
        if abs(self._nabe_versatz) > 0.01:
            cr.move_to(cx, cy)
            cr.line_to(px, cy)
            cr.stroke()

        cr.arc(px, cy, 4.0, 0.0, 2.0 * math.pi)
        cr.fill()

    def _draw_labels(self, cr, cx: float, cy: float, radius: float) -> None:
        """Schreibt die Kurznamen am Ende jeder Achse."""
        cr.select_font_face("Sans")
        cr.set_font_size(9)
        cr.set_source_rgba(*RADAR_LABEL_COLOR)

        label_radius: float = radius + 12.0
        for i, label in enumerate(self._labels):
            angle: float = self._axis_angle(i)
            lx: float = cx + label_radius * math.cos(angle)
            ly: float = cy + label_radius * math.sin(angle)
            extents = cr.text_extents(label)
            tx: float = lx - extents.width / 2.0 - extents.x_bearing
            ty: float = ly + extents.height / 2.0
            cr.move_to(tx, ty)
            cr.show_text(label)
