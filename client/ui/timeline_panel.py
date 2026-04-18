"""
Timeline Panel — Platzhalter fuer Terminuebersicht.

Geplant: Kalender-Integration, Termine, Erinnerungen.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from ui.icons import IC


# ─────────────────────────────────────────────
# TimelinePanel — Platzhalter
# ─────────────────────────────────────────────
class TimelinePanel(QWidget):
    """Platzhalter-Panel fuer Timeline-Uebersicht (noch nicht implementiert)."""

    def __init__(self, server_url: str) -> None:
        super().__init__()
        self._server_url: str = server_url

        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        titel: QLabel = QLabel("  Timeline")
        titel.setStyleSheet("font-size: 27px; font-weight: bold; color: #4da6ff; padding: 4px;")
        layout.addWidget(titel)

        platzhalter: QLabel = QLabel("Terminuebersicht wird in einer spaeteren Version implementiert.")
        platzhalter.setStyleSheet("color: #666666; font-size: 20px; padding: 20px;")
        platzhalter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(platzhalter, stretch=1)
