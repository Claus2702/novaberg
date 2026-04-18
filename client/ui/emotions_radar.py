"""
Emotions-Radar — QPainter Oktagon-Radar fuer 8 Plutchik-Sektoren.

Zeichnet ein Oktagon mit 4 konzentrischen Ringen (25%, 50%, 75%, 100%),
8 Achsen mit farbigen Labels, ein Werte-Polygon und Datenpunkte.
"""

import math

from PySide6.QtCore    import Qt, QPointF
from PySide6.QtGui     import QPainter, QPen, QColor, QFont, QPolygonF, QBrush
from PySide6.QtWidgets import QWidget


# ── Plutchik-Sektoren (synchron mit EMOTION_SEKTOR_MAP in server/config.py) ──

RADAR_SEKTOR_MAP: dict[str, int] = {
    # Sektor 1 — Freude
    "begeisterung": 1, "freude": 1,
    # Sektor 2 — Zuversicht
    "dankbarkeit": 2, "zufriedenheit": 2,
    # Sektor 3 — Angst
    "stress": 3, "unsicherheit": 3,
    # Sektor 4 — Überraschung
    "ueberrascht": 4, "verwundert": 4,
    # Sektor 5 — Trauer
    "verzweiflung": 5, "traurigkeit": 5,
    # Sektor 6 — Enttäuschung
    "frustration": 6, "enttaeuschung": 6,
    # Sektor 7 — Ärger
    "wut": 7, "aerger": 7,
    # Sektor 8 — Neugier
    "hoffnung": 8, "neugierig": 8,
}

RADAR_SEKTOR_LABELS: list[str] = [
    "Freude",        # Sektor 1
    "Zuversicht",    # Sektor 2
    "Angst",         # Sektor 3
    "Überraschung",  # Sektor 4
    "Trauer",        # Sektor 5
    "Enttäuschung",  # Sektor 6
    "Ärger",         # Sektor 7
    "Neugier",       # Sektor 8
]

# Farben pro Sektor (Plutchik-inspiriert)
SEKTOR_FARBEN: list[str] = [
    "#4caf50",  # Freude — Gruen
    "#42a5f5",  # Zuversicht — Blau
    "#ffa726",  # Angst — Orange
    "#ff7043",  # Überraschung — Koralle
    "#ab47bc",  # Trauer — Violett
    "#78909c",  # Enttäuschung — Blaugrau
    "#ef5350",  # Ärger — Rot
    "#26c6da",  # Neugier — Cyan
]

SEKTOR_ANZAHL: int = 8
WINKEL_SCHRITT: float = 2 * math.pi / SEKTOR_ANZAHL  # 45°
START_WINKEL: float = -math.pi / 2                     # -90° = oben (12 Uhr)


def sektor_winkel(sektor: int) -> float:
    """Winkel in Radiant fuer Sektor 1–8 (Uhrzeigersinn ab 12 Uhr)."""
    return START_WINKEL + (sektor - 1) * WINKEL_SCHRITT


def vertex_position(cx: float, cy: float,
                    radius: float, sektor: int) -> QPointF:
    """Berechnet die Position eines Vertex auf dem Oktagon."""
    winkel = sektor_winkel(sektor)
    x = cx + radius * math.cos(winkel)
    y = cy + radius * math.sin(winkel)
    return QPointF(x, y)


def emotionen_zu_sektoren(emotions_daten: dict[str, float]) -> dict[int, float]:
    """Mappt Emotions-Gewichte auf 8 Plutchik-Sektoren.

    Pro Sektor: Hoechster Wert der zugehoerigen Emotionen (max, nicht Summe).
    """
    sektoren: dict[int, float] = {s: 0.0 for s in range(1, 9)}

    for emotion, gewicht in emotions_daten.items():
        sektor = RADAR_SEKTOR_MAP.get(emotion)
        if sektor is not None:
            sektoren[sektor] = max(sektoren[sektor], gewicht)

    return sektoren


class EmotionsRadar(QWidget):
    """Oktagonales Radar-Widget fuer 8 Plutchik-Emotionssektoren."""

    def __init__(self, titel: str = "", parent=None) -> None:
        super().__init__(parent)
        self._titel:  str  = titel
        self._werte:  dict = {}
        self._anzahl: int  = 0

        self.setMinimumSize(280, 300)

    def werte_setzen(self, werte: dict, anzahl: int) -> None:
        """Setzt die Radar-Werte und loest Neuzeichnung aus."""
        self._werte  = werte
        self._anzahl = anzahl
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w: int = self.width()
        h: int = self.height()

        # Zentrum und Radius
        cx: float = w / 2
        cy: float = h / 2 + 10
        radius: float = min(w, h) * 0.4 - 20

        # --- Titel ---
        if self._titel:
            painter.setPen(QColor("#cccccc"))
            painter.setFont(QFont("sans-serif", 11, QFont.Weight.Bold))
            painter.drawText(0, 0, w, 30, Qt.AlignmentFlag.AlignCenter, self._titel)

        # --- 4 konzentrische Oktagone (25%, 50%, 75%, 100%) ---
        ring_pen = QPen(QColor("#333333"), 1)
        painter.setPen(ring_pen)

        for stufe in (0.25, 0.50, 0.75, 1.0):
            polygon = QPolygonF()
            r: float = radius * stufe
            for s in range(1, SEKTOR_ANZAHL + 1):
                polygon.append(vertex_position(cx, cy, r, s))
            polygon.append(polygon[0])
            painter.drawPolyline(polygon)

        # --- Achsenlinien + Labels ---
        label_font = QFont("sans-serif", 9)
        painter.setFont(label_font)

        for s in range(1, SEKTOR_ANZAHL + 1):
            punkt = vertex_position(cx, cy, radius, s)

            # Achsenlinie
            painter.setPen(QPen(QColor("#444444"), 1))
            painter.drawLine(QPointF(cx, cy), punkt)

            # Label — ausserhalb des Oktagons
            winkel = sektor_winkel(s)
            ist_diagonal = s in (2, 4, 6, 8)
            label_offset = 22 if ist_diagonal else 18
            lx = cx + (radius + label_offset) * math.cos(winkel)
            ly = cy + (radius + label_offset) * math.sin(winkel)

            name = RADAR_SEKTOR_LABELS[s - 1]
            farbe = SEKTOR_FARBEN[s - 1]
            painter.setPen(QColor(farbe))

            # Alignment je nach Position
            rect_w, rect_h = 80, 16
            if s == 1:      # oben
                flags = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
                rect_x = int(lx) - rect_w // 2
                rect_y = int(ly) - rect_h
            elif s == 5:    # unten
                flags = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
                rect_x = int(lx) - rect_w // 2
                rect_y = int(ly)
            elif s == 3:    # rechts
                flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                rect_x = int(lx)
                rect_y = int(ly) - rect_h // 2
            elif s == 7:    # links
                flags = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                rect_x = int(lx) - rect_w
                rect_y = int(ly) - rect_h // 2
            elif s == 2:    # rechts-oben
                flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
                rect_x = int(lx)
                rect_y = int(ly) - rect_h
            elif s == 4:    # rechts-unten
                flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
                rect_x = int(lx)
                rect_y = int(ly)
            elif s == 6:    # links-unten
                flags = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
                rect_x = int(lx) - rect_w
                rect_y = int(ly)
            else:           # s == 8, links-oben
                flags = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
                rect_x = int(lx) - rect_w
                rect_y = int(ly) - rect_h

            painter.drawText(rect_x, rect_y, rect_w, rect_h, flags, name)

        # --- Werte-Polygon ---
        if self._werte:
            sektoren = emotionen_zu_sektoren(self._werte)
            wert_polygon = QPolygonF()
            wert_punkte: list[QPointF] = []

            for s in range(1, SEKTOR_ANZAHL + 1):
                wert: float = min(max(sektoren[s], 0.0), 1.0)
                punkt = vertex_position(cx, cy, radius * wert, s)
                wert_polygon.append(punkt)
                wert_punkte.append(punkt)

            wert_polygon.append(wert_polygon[0])

            # Gefuelltes Polygon
            painter.setPen(QPen(QColor(77, 166, 255, 120), 2))
            painter.setBrush(QBrush(QColor(77, 166, 255, 40)))
            painter.drawPolygon(wert_polygon)

            # Datenpunkte
            for s_idx, punkt in enumerate(wert_punkte):
                farbe = QColor(SEKTOR_FARBEN[s_idx])
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(farbe))
                painter.drawEllipse(punkt, 4, 4)

        # --- Anzahl-Hinweis ---
        painter.setPen(QColor("#666666"))
        painter.setFont(QFont("sans-serif", 8))
        painter.drawText(
            0, h - 18, w, 16,
            Qt.AlignmentFlag.AlignCenter,
            f"n = {self._anzahl}",
        )

        painter.end()
