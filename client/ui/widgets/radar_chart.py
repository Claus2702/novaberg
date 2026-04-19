"""
Radar-Diagramm-Widget auf Basis von ``Gtk.DrawingArea`` und Cairo.

Zeichnet 8 Plutchik-Sektoren auf einem Achsen-Stern. Jede Achse zeigt
einen Sektor-Wert (0.0–1.0); die 8 Datenpunkte werden als geschlossenes,
halbtransparent gefülltes Polygon verbunden.

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
    RADAR_TITLE_COLOR,
)


logger = logging.getLogger(__name__)


# Kurzformen für die 8 Plutchik-Sektoren (Reihenfolge 1–8).
_SEKTOR_KURZ: list[str] = ["Fr", "Zv", "An", "Üb", "Tr", "En", "Är", "Ne"]

_NUM_AXES: int = 8


class RadarChart(Gtk.DrawingArea):
    """Radar-Diagramm mit 8 Achsen für Plutchik-Sektoren."""

    def __init__(self, title: str = "", size: int = 160):
        """Erstellt ein Radar-Diagramm mit 8 Achsen (Plutchik-Sektoren).

        Args:
            title: Überschrift über dem Diagramm (z.B. "Session", "KZG").
            size: Breite und Höhe in Pixel.
        """
        super().__init__()
        self._title: str = title
        self._size: int = size
        self._values: list[float] = [0.0] * _NUM_AXES

        self.set_content_width(size)
        self.set_content_height(size)
        self.set_draw_func(self._on_draw)

    def set_data(self, sector_values: list[float]) -> None:
        """Setzt die 8 Sektorwerte (0.0–1.0) und löst Neuzeichnung aus.

        Args:
            sector_values: Liste mit genau 8 Floats, Reihenfolge Sektor 1–8:
                [Freude, Zuversicht, Angst, Überraschung, Trauer,
                 Enttäuschung, Ärger, Neugier]
        """
        if len(sector_values) != _NUM_AXES:
            raise ValueError(
                f"RadarChart.set_data erwartet {_NUM_AXES} Werte, "
                f"bekam {len(sector_values)}"
            )
        self._values = [max(0.0, min(1.0, float(v))) for v in sector_values]
        logger.info(
            f"RadarChart '{self._title}' Sektorwerte: "
            + ", ".join(
                f"{k}={v:.2f}" for k, v in zip(_SEKTOR_KURZ, self._values)
            )
        )
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
        self._draw_data(cr, cx, cy, radius)
        self._draw_labels(cr, cx, cy, radius)

    def _axis_angle(self, i: int) -> float:
        """Winkel der Achse ``i`` (0-basiert), Start oben, im Uhrzeigersinn."""
        return i * (2.0 * math.pi / _NUM_AXES) - math.pi / 2.0

    def _draw_grid(self, cr, cx: float, cy: float, radius: float) -> None:
        """Zeichnet konzentrische Ringe und 8 Achsen."""
        cr.set_source_rgba(*RADAR_GRID_COLOR)
        cr.set_line_width(1.0)

        # Drei konzentrische Ringe bei 33 %, 66 %, 100 %.
        for frac in (0.33, 0.66, 1.0):
            r: float = radius * frac
            for i in range(_NUM_AXES):
                angle: float = self._axis_angle(i)
                x: float = cx + r * math.cos(angle)
                y: float = cy + r * math.sin(angle)
                if i == 0:
                    cr.move_to(x, y)
                else:
                    cr.line_to(x, y)
            cr.close_path()
            cr.stroke()

        # 8 Achsen vom Zentrum nach außen.
        for i in range(_NUM_AXES):
            angle = self._axis_angle(i)
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            cr.move_to(cx, cy)
            cr.line_to(x, y)
            cr.stroke()

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

    def _draw_labels(self, cr, cx: float, cy: float, radius: float) -> None:
        """Schreibt die Kurznamen am Ende jeder Achse."""
        cr.select_font_face("Sans")
        cr.set_font_size(9)
        cr.set_source_rgba(*RADAR_LABEL_COLOR)

        label_radius: float = radius + 12.0
        for i, label in enumerate(_SEKTOR_KURZ):
            angle: float = self._axis_angle(i)
            lx: float = cx + label_radius * math.cos(angle)
            ly: float = cy + label_radius * math.sin(angle)
            extents = cr.text_extents(label)
            tx: float = lx - extents.width / 2.0 - extents.x_bearing
            ty: float = ly + extents.height / 2.0
            cr.move_to(tx, ty)
            cr.show_text(label)
