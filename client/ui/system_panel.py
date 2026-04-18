"""
System Panel — Health-Check und Konfiguration.

Zeigt den Status aller Dienste (Server, Redis, Postgres, Ollama)
mit manueller Aktualisierung über den Refresh-Button.
"""

import requests

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame

from ui.icons import IC


# ─────────────────────────────────────────────
# SystemPanel — Health-Check Übersicht
# ─────────────────────────────────────────────
class SystemPanel(QWidget):
    """System-Panel mit Dienst-Status und manuellem Health-Check."""

    # ─────────────────────────────────────────
    # Initialisierung und UI-Aufbau
    # ─────────────────────────────────────────
    def __init__(self, server_url: str) -> None:
        super().__init__()
        self._server_url: str = server_url

        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # -- Titel --
        titel: QLabel = QLabel("  System")
        titel.setStyleSheet("font-size: 27px; font-weight: bold; color: #4da6ff; padding: 4px;")
        layout.addWidget(titel)

        # -- Dienst-Status-Zeilen --
        dienst_tokens: dict[str, str] = {
            "server":   "dienst.server",
            "redis":    "dienst.redis",
            "postgres": "dienst.postgres",
            "ollama":   "dienst.ollama",
        }
        self._health_icons:  dict[str, QLabel] = {}
        self._health_texte:  dict[str, QLabel] = {}

        for dienst, token in dienst_tokens.items():
            zeile: QHBoxLayout = QHBoxLayout()

            name: QLabel = QLabel(f"  {dienst.capitalize()}")
            name.setStyleSheet("color: #b0b0b0; font-size: 14px; min-width: 120px;")

            icon_lbl: QLabel = QLabel()
            icon_lbl.setPixmap(IC.pixmap("pruefe", 18))
            icon_lbl.setFixedSize(22, 22)

            status_text: QLabel = QLabel("Pruefe...")
            status_text.setStyleSheet("color: #666666; font-size: 21px;")

            self._health_icons[dienst] = icon_lbl
            self._health_texte[dienst] = status_text

            zeile.addWidget(name)
            zeile.addWidget(icon_lbl)
            zeile.addWidget(status_text)
            zeile.addStretch()
            layout.addLayout(zeile)

        # -- Refresh-Button --
        refresh: QPushButton = QPushButton("  Health-Check ausfuehren")
        refresh.setIcon(IC["health"])
        refresh.setIconSize(QSize(20, 20))
        refresh.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #b0b0b0;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #ffffff;
            }
        """)
        refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh.clicked.connect(self._health_check)
        layout.addWidget(refresh)

        layout.addStretch()

        # Initialer Check nach 500ms
        QTimer.singleShot(500, self._health_check)

    # ─────────────────────────────────────────
    # Health-Check durchführen (GET /health)
    # ─────────────────────────────────────────
    def _health_check(self) -> None:
        """Fragt /health ab und aktualisiert alle Dienst-Icons und -Texte."""

        try:
            response = requests.get(f"{self._server_url}/health", timeout=5)
            daten: dict = response.json()

            for dienst in self._health_icons:
                status: str = daten.get(dienst, "unbekannt")
                icon_lbl: QLabel = self._health_icons[dienst]
                text_lbl: QLabel = self._health_texte[dienst]

                if status == "ok":
                    icon_lbl.setPixmap(IC.pixmap("ok", 18))
                    text_lbl.setText("Online")
                    text_lbl.setStyleSheet("color: #4caf50; font-size: 14px;")
                else:
                    icon_lbl.setPixmap(IC.pixmap("fehler", 18))
                    text_lbl.setText(status)
                    text_lbl.setStyleSheet("color: #ff6b6b; font-size: 14px;")

        except requests.exceptions.ConnectionError:
            for dienst in self._health_icons:
                self._health_icons[dienst].setPixmap(IC.pixmap("offline", 18))
                self._health_texte[dienst].setText("Nicht erreichbar")
                self._health_texte[dienst].setStyleSheet("color: #ff6b6b; font-size: 14px;")

        except Exception as fehler:
            for dienst in self._health_icons:
                self._health_icons[dienst].setPixmap(IC.pixmap("warnung", 18))
                self._health_texte[dienst].setText(str(fehler))
                self._health_texte[dienst].setStyleSheet("color: #ffa726; font-size: 14px;")
