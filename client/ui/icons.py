"""
Icon-System — Zentrales Mapping von Text-Tokens zu qtawesome-Icons.

Stellt eine einheitliche Schnittstelle bereit, um ueberall im Client
grafische Icons statt ASCII-Symbole ([OK], [X], [>>] etc.) zu verwenden.

Verwendung:
    from ui.icons import IC, icon_label

    button.setIcon(IC["nav.chat"])          # QIcon fuer QPushButton
    widget = icon_label("ok", "Online")     # QWidget mit Icon + Text
"""

import qtawesome as qta

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel


# ─────────────────────────────────────────────
# Token-Mapping: Token → (qtawesome-Name, Standardfarbe)
# ─────────────────────────────────────────────
_MAP: dict[str, tuple[str, str]] = {

    # Navigation (Sidebar)
    "nav.chat":        ("mdi6.chat-outline",            "#4da6ff"),
    "nav.gedaechtnis": ("mdi6.brain",                   "#4da6ff"),
    "nav.timeline":    ("mdi6.timeline-clock-outline",   "#4da6ff"),
    "nav.fakten":      ("mdi6.book-open-variant",       "#4da6ff"),
    "nav.schatten":    ("mdi6.ghost-outline",            "#4da6ff"),
    "nav.system":      ("mdi6.cog-outline",              "#4da6ff"),

    # Status-Indikatoren
    "ok":              ("mdi6.check-circle-outline",     "#4caf50"),
    "fehler":          ("mdi6.close-circle-outline",     "#ff6b6b"),
    "warnung":         ("mdi6.alert-circle-outline",     "#ffa726"),
    "offline":         ("mdi6.wifi-off",                 "#ff6b6b"),
    "pruefe":          ("mdi6.dots-horizontal-circle-outline", "#666666"),
    "idle":            ("mdi6.sleep",                    "#666666"),

    # Aktionen
    "refresh":         ("mdi6.refresh",                  "#b0b0b0"),
    "senden":          ("mdi6.send",                     "#ffffff"),
    "health":          ("mdi6.heart-pulse",              "#b0b0b0"),

    # Pipeline-Stages (Chat)
    "stage.aktiv":     ("mdi6.chevron-double-right",     "#4da6ff"),
    "stage.fertig":    ("mdi6.check",                    "#4caf50"),

    # Dienst-Icons (StatusBar / SystemPanel)
    "dienst.server":   ("mdi6.server-outline",           "#b0b0b0"),
    "dienst.ollama":   ("mdi6.robot-outline",            "#b0b0b0"),
    "dienst.redis":    ("mdi6.memory",                   "#b0b0b0"),
    "dienst.postgres":  ("mdi6.database-outline",        "#b0b0b0"),
    "dienst.pixie":    ("mdi6.ghost-outline",            "#b0b0b0"),

    # Fakten-Panel
    "fakt.gesichert":  ("mdi6.shield-check-outline",     "#4caf50"),
    "fakt.ungesichert": ("mdi6.shield-outline",          "#666666"),
}


# ─────────────────────────────────────────────
# IC — Vorgefertigte QIcon-Instanzen (lazy, gecacht)
# ─────────────────────────────────────────────
class _IconCache:
    """Lazy-Cache: Erzeugt QIcons beim ersten Zugriff und speichert sie."""

    def __init__(self) -> None:
        self._cache: dict[str, QIcon] = {}

    def __getitem__(self, token: str) -> QIcon:
        if token not in self._cache:
            name, color = _MAP[token]
            self._cache[token] = qta.icon(name, color=color)
        return self._cache[token]

    def get(self, token: str, color: str = None, size: int = 0) -> QIcon:
        """Icon mit optionaler Farbüberschreibung (nicht gecacht)."""
        name, default_color = _MAP[token]
        return qta.icon(name, color=color or default_color)

    def pixmap(self, token: str, size: int = 18, color: str = None) -> QPixmap:
        """QPixmap für direkte Darstellung in QLabels."""
        return self.get(token, color).pixmap(QSize(size, size))


IC = _IconCache()


# ─────────────────────────────────────────────
# icon_label — Kompakt-Widget: Icon + Text
# ─────────────────────────────────────────────
def icon_label(
    token: str,
    text: str = "",
    icon_size: int = 18,
    font_size: int = 14,
    color: str = None,
    text_color: str = None,
    spacing: int = 6,
) -> QWidget:
    """
    Erzeugt ein kleines Widget mit Icon (links) + Text (rechts).

    Parameter:
        token      Schluessel aus _MAP (z.B. "ok", "fehler", "stage.aktiv")
        text       Optionaler Text neben dem Icon
        icon_size  Pixelgroesse des Icons
        font_size  Schriftgroesse des Texts
        color      Farbueberschreibung fuer das Icon
        text_color Farbe des Texts (Standard: Icon-Farbe)
        spacing    Abstand zwischen Icon und Text
    """
    _, default_color = _MAP[token]
    farbe: str = color or default_color
    txt_farbe: str = text_color or farbe

    widget: QWidget = QWidget()
    layout: QHBoxLayout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(spacing)

    # Icon als QLabel mit Pixmap
    icon_lbl: QLabel = QLabel()
    icon_lbl.setPixmap(IC.pixmap(token, icon_size, farbe))
    icon_lbl.setFixedSize(icon_size + 2, icon_size + 2)
    layout.addWidget(icon_lbl)

    # Text (optional)
    if text:
        text_lbl: QLabel = QLabel(text)
        text_lbl.setStyleSheet(f"color: {txt_farbe}; font-size: {font_size}px;")
        layout.addWidget(text_lbl)

    layout.addStretch()
    return widget
