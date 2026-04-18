"""
Hauptfenster — Zentrales Fenster mit Sidebar-Navigation und Panel-Wechsel.

Aufbau:
  [ Sidebar (220px) ][ StackedWidget (Panels)          ]
  [  Titel           ][  Chat / Gedächtnis / Timeline   ]
  [  Nav-Buttons     ][  Fakten / Schatten / System     ]
  [  Version         ][                                  ]
  [                  ][ StatusLeiste                     ]
"""

import sys

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame
)

from ui.icons             import IC
from ui.chat_panel        import ChatPanel
from ui.fakten_panel      import FaktenPanel
from ui.gedaechtnis_panel import GedaechtnisPanel
from ui.schatten_panel    import SchattenPanel
from ui.status_bar        import StatusLeiste
from ui.system_panel      import SystemPanel
from ui.timeline_panel    import TimelinePanel


# ─────────────────────────────────────────────
# Styles: Sidebar und Hauptfenster
# ─────────────────────────────────────────────
SIDEBAR_BUTTON_STYLE: str = """
    QPushButton {
        background-color: transparent;
        color: #b0b0b0;
        border: none;
        border-radius: 6px;
        padding: 12px 16px;
        text-align: left;
        font-size: 20px;
    }
    QPushButton:hover {
        background-color: #2a2a2a;
        color: #ffffff;
    }
    QPushButton:checked {
        background-color: #1a3a5c;
        color: #4da6ff;
        font-weight: bold;
    }
"""

SIDEBAR_STYLE: str = """
    QFrame {
        background-color: #1a1a1a;
        border-right: 1px solid #333333;
    }
"""

MAIN_STYLE: str = """
    QMainWindow {
        background-color: #121212;
    }
    QStackedWidget {
        background-color: #121212;
    }
"""


class Hauptfenster(QMainWindow):
    """Hauptfenster mit Sidebar und wechselndem Main-Panel."""

    def __init__(self) -> None:
        super().__init__()

        self._server_url: str = "http://localhost:8000"

        self._fenster_einrichten()
        self._sidebar_erstellen()
        self._panels_erstellen()
        self._status_leiste_erstellen()
        self._layout_zusammenbauen()

        # Erstes Panel aktivieren (Chat)
        self._panel_wechseln(0)

    # ─────────────────────────────────────────
    # Fenster konfigurieren
    # ─────────────────────────────────────────
    def _fenster_einrichten(self) -> None:
        """Titel, Mindestgröße, Dark-Theme-Style."""

        self.setWindowTitle("KI-Assistent — Lokaler Denkpartner")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.setStyleSheet(MAIN_STYLE)

    # ─────────────────────────────────────────
    # Sidebar erstellen (Titel + Nav-Buttons + Version)
    # ─────────────────────────────────────────
    def _sidebar_erstellen(self) -> None:
        """Erstellt die linke Sidebar mit Navigations-Buttons."""

        self._sidebar: QFrame = QFrame()
        self._sidebar.setFixedWidth(220)
        self._sidebar.setStyleSheet(SIDEBAR_STYLE)

        self._sidebar_layout: QVBoxLayout = QVBoxLayout(self._sidebar)
        self._sidebar_layout.setContentsMargins(8, 12, 8, 12)
        self._sidebar_layout.setSpacing(4)

        # -- Titel --
        titel: QLabel = QLabel("KI-Assistent")
        titel.setStyleSheet("color: #4da6ff; font-size: 24px; font-weight: bold; padding: 8px;")
        titel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sidebar_layout.addWidget(titel)

        trennlinie: QFrame = QFrame()
        trennlinie.setFrameShape(QFrame.Shape.HLine)
        trennlinie.setStyleSheet("color: #333333;")
        self._sidebar_layout.addWidget(trennlinie)

        # -- Navigations-Buttons --
        self._nav_buttons: list[QPushButton] = []
        nav_eintraege: list[tuple[str, str]] = [
            ("nav.chat",        "Chat"),
            ("nav.gedaechtnis", "Gedaechtnis"),
            ("nav.timeline",    "Timeline"),
            ("nav.fakten",      "Fakten"),
            ("nav.schatten",    "Schatten"),
            ("nav.system",      "System"),
        ]

        for index, (token, text) in enumerate(nav_eintraege):
            button: QPushButton = QPushButton(f"  {text}")
            button.setIcon(IC[token])
            button.setIconSize(QSize(22, 22))
            button.setCheckable(True)
            button.setStyleSheet(SIDEBAR_BUTTON_STYLE)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked, idx=index: self._panel_wechseln(idx))
            self._nav_buttons.append(button)
            self._sidebar_layout.addWidget(button)

        self._sidebar_layout.addStretch()

        # -- Version --
        version: QLabel = QLabel("v0.1.0")
        version.setStyleSheet("color: #555555; font-size: 16px; padding: 8px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sidebar_layout.addWidget(version)

    # ─────────────────────────────────────────
    # Panels erstellen (StackedWidget befüllen)
    # ─────────────────────────────────────────
    def _panels_erstellen(self) -> None:
        """Erstellt alle Panel-Instanzen und registriert sie im StackedWidget."""

        self._stack: QStackedWidget = QStackedWidget()

        self._chat_panel:        ChatPanel        = ChatPanel(self._server_url)
        self._gedaechtnis_panel: GedaechtnisPanel = GedaechtnisPanel(self._server_url)
        self._timeline_panel:    TimelinePanel    = TimelinePanel(self._server_url)
        self._fakten_panel:      FaktenPanel      = FaktenPanel(self._server_url)
        self._schatten_panel:    SchattenPanel    = SchattenPanel(self._server_url)
        self._system_panel:      SystemPanel      = SystemPanel(self._server_url)

        self._stack.addWidget(self._chat_panel)
        self._stack.addWidget(self._gedaechtnis_panel)
        self._stack.addWidget(self._timeline_panel)
        self._stack.addWidget(self._fakten_panel)
        self._stack.addWidget(self._schatten_panel)
        self._stack.addWidget(self._system_panel)

    # ─────────────────────────────────────────
    # StatusLeiste erstellen
    # ─────────────────────────────────────────
    def _status_leiste_erstellen(self) -> None:
        """Erstellt die Statusleiste am unteren Rand."""

        self._status_leiste: StatusLeiste = StatusLeiste(self._server_url)

    # ─────────────────────────────────────────
    # Layout zusammenbauen (Sidebar links, Stack + Status rechts)
    # ─────────────────────────────────────────
    def _layout_zusammenbauen(self) -> None:
        """Baut das Gesamtlayout zusammen: Sidebar | Panels + StatusLeiste."""

        zentral: QWidget = QWidget()
        self.setCentralWidget(zentral)

        layout: QHBoxLayout = QHBoxLayout(zentral)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Rechte Seite: Stack + Statusleiste
        rechts: QVBoxLayout = QVBoxLayout()
        rechts.setContentsMargins(0, 0, 0, 0)
        rechts.setSpacing(0)
        rechts.addWidget(self._stack, stretch=1)
        rechts.addWidget(self._status_leiste)

        rechts_widget: QWidget = QWidget()
        rechts_widget.setLayout(rechts)

        layout.addWidget(self._sidebar)
        layout.addWidget(rechts_widget, stretch=1)

    # ─────────────────────────────────────────
    # Panel-Navigation (Sidebar-Button → StackedWidget)
    # ─────────────────────────────────────────
    def _panel_wechseln(self, index: int) -> None:
        """Wechselt das aktive Panel und aktualisiert die Sidebar-Buttons."""

        self._stack.setCurrentIndex(index)

        for i, button in enumerate(self._nav_buttons):
            button.setChecked(i == index)
