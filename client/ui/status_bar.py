"""
Statusleiste — Zeigt Server-, Ollama-, DB- und Pixie-Status permanent an.

Liegt am unteren Rand des Hauptfensters. Pollt alle 5 Sekunden
den /health-Endpoint und aktualisiert die vier Status-Labels.
"""

import requests

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from ui.icons import IC


# ─────────────────────────────────────────────
# Style: Dunkle Leiste mit Trennlinie oben
# ─────────────────────────────────────────────
STATUS_STYLE: str = """
    QWidget {
        background-color: #0d0d0d;
        border-top: 1px solid #333333;
    }
"""


class StatusLeiste(QWidget):
    """Statusleiste mit fünf Indikatoren: Server, Ollama, DB, Web, Pixie."""

    # ─────────────────────────────────────────
    # Initialisierung und UI-Aufbau
    # ─────────────────────────────────────────
    def __init__(self, server_url: str) -> None:
        super().__init__()
        self._server_url: str = server_url

        self.setFixedHeight(32)
        self.setStyleSheet(STATUS_STYLE)

        layout: QHBoxLayout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(20)

        # -- Status-Labels anlegen (Icon + Text) --
        self._server_icon:  QLabel = QLabel()
        self._server_text:  QLabel = QLabel("Server")
        self._ollama_icon:  QLabel = QLabel()
        self._ollama_text:  QLabel = QLabel("Ollama")
        self._db_icon:      QLabel = QLabel()
        self._db_text:      QLabel = QLabel("DB")
        self._searxng_icon: QLabel = QLabel()
        self._searxng_text: QLabel = QLabel("Web")
        self._schatten_icon: QLabel = QLabel()
        self._schatten_text: QLabel = QLabel("Pixie: idle")

        self._status_paare: list[tuple[QLabel, QLabel, str]] = [
            (self._server_icon,  self._server_text,  "dienst.server"),
            (self._ollama_icon,  self._ollama_text,  "dienst.ollama"),
            (self._db_icon,      self._db_text,      "dienst.postgres"),
            (self._searxng_icon, self._searxng_text, "dienst.searxng"),
            (self._schatten_icon, self._schatten_text, "dienst.pixie"),
        ]

        for icon_lbl, text_lbl, token in self._status_paare:
            icon_lbl.setPixmap(IC.pixmap("pruefe", 16))
            icon_lbl.setFixedSize(20, 20)
            text_lbl.setStyleSheet("color: #666666; font-size: 16px;")
            layout.addWidget(icon_lbl)
            layout.addWidget(text_lbl)
            layout.addSpacing(12)

        layout.addStretch()

        # -- Periodischer Health-Check (alle 5 Sekunden) --
        self._timer: QTimer = QTimer()
        self._timer.timeout.connect(self._status_aktualisieren)
        self._timer.start(5000)

        # Initialer Check nach 1 Sekunde
        QTimer.singleShot(1000, self._status_aktualisieren)

    # ─────────────────────────────────────────
    # Health-Check durchführen (GET /health)
    # ─────────────────────────────────────────
    def _status_aktualisieren(self) -> None:
        """Fragt /health ab und aktualisiert alle Status-Icons und -Texte."""

        try:
            response = requests.get(f"{self._server_url}/health", timeout=5)
            daten: dict = response.json()

            self._dienst_setzen(self._server_icon,  self._server_text,  "Server", daten.get("server", "?"))
            self._dienst_setzen(self._ollama_icon,  self._ollama_text,  "Ollama", daten.get("ollama", "?"))
            self._dienst_setzen(self._db_icon,      self._db_text,      "DB",     daten.get("postgres", "?"))
            self._dienst_setzen(self._searxng_icon, self._searxng_text, "Web",    daten.get("searxng", "?"))

            # -- Pixie-Status (Shadow Agent) --
            schatten: dict = daten.get("shadow", {})
            zustand:  str  = schatten.get("zustand", "idle")

            if zustand == "idle":
                self._schatten_icon.setPixmap(IC.pixmap("idle", 16))
                self._schatten_text.setText("Pixie: idle")
                self._schatten_text.setStyleSheet("color: #666666; font-size: 16px;")
            else:
                thema: str = schatten.get("thema", "")
                anzeige: str = f"Pixie: {zustand}"
                if thema:
                    anzeige += f" {thema[:30]}"
                self._schatten_icon.setPixmap(IC.pixmap("ok", 16))
                self._schatten_text.setText(anzeige)
                self._schatten_text.setStyleSheet("color: #4da6ff; font-size: 16px;")

        except Exception:
            self._server_icon.setPixmap(IC.pixmap("fehler", 16))
            self._server_text.setText("Server")
            self._server_text.setStyleSheet("color: #ff6b6b; font-size: 16px;")

    # ─────────────────────────────────────────
    # Einzelnen Dienst-Status setzen (Icon + Text)
    # ─────────────────────────────────────────
    def _dienst_setzen(self, icon_lbl: QLabel, text_lbl: QLabel, name: str, status: str) -> None:
        """Setzt Icon und Text eines Dienst-Status-Paares."""

        if status == "ok":
            icon_lbl.setPixmap(IC.pixmap("ok", 16))
            text_lbl.setText(name)
            text_lbl.setStyleSheet("color: #4caf50; font-size: 16px;")
        else:
            icon_lbl.setPixmap(IC.pixmap("fehler", 16))
            text_lbl.setText(name)
            text_lbl.setStyleSheet("color: #ff6b6b; font-size: 16px;")
