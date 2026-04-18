"""
Schatten Panel — Platzhalter fuer Hintergrund-Agent Status und Log.

Geplant: Live-Ansicht der Pixie-Aktivitaeten, Queue-Status,
Stack-Eintraege und Verarbeitungs-Log.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from ui.icons import IC


# ─────────────────────────────────────────────
# SchattenPanel — Platzhalter
# ─────────────────────────────────────────────
class SchattenPanel(QWidget):
    """Platzhalter-Panel fuer Schatten-Agent-Uebersicht (noch nicht implementiert)."""

    def __init__(self, server_url: str) -> None:
        super().__init__()
        self._server_url: str = server_url

        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        titel: QLabel = QLabel("  Schatten-Agent")
        titel.setStyleSheet("font-size: 27px; font-weight: bold; color: #4da6ff; padding: 4px;")
        layout.addWidget(titel)

        platzhalter: QLabel = QLabel("Hintergrund-Aktivitaeten und Erkenntnisse erscheinen hier.")
        platzhalter.setStyleSheet("color: #666666; font-size: 20px; padding: 20px;")
        platzhalter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(platzhalter, stretch=1)
