"""
Fakten Panel — Zeigt Entitäten und ihre Relationen an.

Lädt Entitäten (Person, Tier, Objekt, Ort, Organisation) vom Server
und stellt sie als Karten mit Schlüssel-Wert-Paaren dar.
Jeder Fakt zeigt Status (gesichert/ungesichert), Relevanz und Häufigkeit.
"""

import logging

import requests

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)

from ui.icons import IC

logger = logging.getLogger("ki_client.fakten")


# ─────────────────────────────────────────────
# Styles: Panel, Entitäts-Karten, Buttons
# ─────────────────────────────────────────────
PANEL_STYLE: str = """
    QWidget {
        background-color: #121212;
        color: #e0e0e0;
    }
"""

ENTITAET_STYLE: str = """
    QFrame {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 10px;
    }
"""

REFRESH_STYLE: str = """
    QPushButton {
        background-color: #2a2a2a;
        color: #b0b0b0;
        border: 1px solid #444444;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 18px;
    }
    QPushButton:hover {
        background-color: #333333;
        color: #ffffff;
    }
"""

LEER_STYLE: str = "color: #666666; font-size: 18px; padding: 20px;"


class FaktenPanel(QWidget):
    """Fakten-Panel — Entitäten und ihre Schlüssel-Wert-Fakten."""

    def __init__(self, server_url: str) -> None:
        super().__init__()

        self._server_url: str = server_url
        self._user_id:    str = "meister"

        self.setStyleSheet(PANEL_STYLE)
        self._ui_erstellen()

    # ─────────────────────────────────────────
    # UI aufbauen (Kopfzeile + Scrollbereich)
    # ─────────────────────────────────────────
    def _ui_erstellen(self) -> None:
        """Erstellt Kopfzeile mit Refresh-Button und scrollbaren Inhalt."""

        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # -- Kopfzeile (Titel + Refresh) --
        kopf: QHBoxLayout = QHBoxLayout()

        titel: QLabel = QLabel("  Fakten")
        titel.setStyleSheet("font-size: 27px; font-weight: bold; color: #4da6ff; padding: 4px;")

        self._refresh_button: QPushButton = QPushButton("  Aktualisieren")
        self._refresh_button.setIcon(IC["refresh"])
        self._refresh_button.setIconSize(QSize(18, 18))
        self._refresh_button.setStyleSheet(REFRESH_STYLE)
        self._refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh_button.clicked.connect(self._fakten_laden)

        kopf.addWidget(titel)
        kopf.addStretch()
        kopf.addWidget(self._refresh_button)
        layout.addLayout(kopf)

        # -- Scrollbereich für Entitäts-Karten --
        self._scroll: QScrollArea = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("border: none;")

        self._content_widget: QWidget = QWidget()
        self._content_layout: QVBoxLayout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(10)
        self._content_layout.addStretch()

        self._scroll.setWidget(self._content_widget)
        layout.addWidget(self._scroll, stretch=1)

        # Initialer Ladevorgang
        QTimer.singleShot(500, self._fakten_laden)

    # ─────────────────────────────────────────
    # Fakten vom Server laden (GET /fakten/{user_id})
    # ─────────────────────────────────────────
    def _fakten_laden(self) -> None:
        """Lädt Entitäten vom Server und baut die Karten-Ansicht auf."""

        # Alte Einträge entfernen
        while self._content_layout.count() > 1:
            item = self._content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        try:
            response = requests.get(
                f"{self._server_url}/fakten/{self._user_id}",
                timeout=10
            )
            daten: dict = response.json()
            entitaeten: list = daten.get("entitaeten", [])

            if not entitaeten:
                leer: QLabel = QLabel("Keine Entitaeten vorhanden.")
                leer.setStyleSheet(LEER_STYLE)
                leer.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._content_layout.insertWidget(0, leer)
                return

            # -- Entitäts-Karten rendern --
            for entitaet in entitaeten:
                frame: QFrame = QFrame()
                frame.setStyleSheet(ENTITAET_STYLE)
                frame_layout: QVBoxLayout = QVBoxLayout(frame)
                frame_layout.setContentsMargins(10, 8, 10, 8)
                frame_layout.setSpacing(6)

                # Kopfzeile: Name + Typ (farbcodiert)
                kopf: QHBoxLayout = QHBoxLayout()

                name: str = entitaet.get("name", "")
                typ: str = entitaet.get("typ", "")
                typ_farben: dict = {
                    "person": "#4da6ff",
                    "tier":   "#4caf50",
                    "objekt": "#ffa726",
                    "ort":    "#ce93d8",
                    "organisation": "#ff8a65"
                }
                typ_farbe: str = typ_farben.get(typ, "#b0b0b0")

                name_label: QLabel = QLabel(f"{name}")
                name_label.setStyleSheet(f"color: {typ_farbe}; font-size: 20px; font-weight: bold;")

                typ_label: QLabel = QLabel(f"({typ})")
                typ_label.setStyleSheet(f"color: {typ_farbe}; font-size: 16px;")

                kopf.addWidget(name_label)
                kopf.addWidget(typ_label)
                kopf.addStretch()
                frame_layout.addLayout(kopf)

                # Fakten-Zeilen (Schlüssel = Wert + Meta)
                fakten: list = entitaet.get("fakten", [])
                for fakt in fakten:
                    fakt_layout: QHBoxLayout = QHBoxLayout()

                    schluessel: str = fakt.get("schluessel", "")
                    wert: str = fakt.get("wert", "")
                    gesichert: bool = fakt.get("gesichert", False)
                    relevanz: float = fakt.get("relevanz", 0)
                    haeufigkeit: int = fakt.get("haeufigkeit", 1)

                    status_token: str = "fakt.gesichert" if gesichert else "fakt.ungesichert"
                    status_farbe: str = "#4caf50" if gesichert else "#666666"

                    schluessel_label: QLabel = QLabel(f"  {schluessel}")
                    schluessel_label.setStyleSheet("color: #888888; font-size: 16px; min-width: 140px;")

                    wert_label: QLabel = QLabel(f"= {wert}")
                    wert_label.setStyleSheet("color: #e0e0e0; font-size: 16px;")
                    wert_label.setWordWrap(True)

                    status_icon_lbl: QLabel = QLabel()
                    status_icon_lbl.setPixmap(IC.pixmap(status_token, 14))
                    status_icon_lbl.setFixedSize(18, 18)

                    meta_label: QLabel = QLabel(f"{relevanz:.2f} x{haeufigkeit}")
                    meta_label.setStyleSheet(f"color: {status_farbe}; font-size: 14px;")
                    meta_label.setAlignment(Qt.AlignmentFlag.AlignRight)

                    fakt_layout.addWidget(schluessel_label)
                    fakt_layout.addWidget(wert_label, stretch=1)
                    fakt_layout.addWidget(status_icon_lbl)
                    fakt_layout.addWidget(meta_label)
                    frame_layout.addLayout(fakt_layout)

                self._content_layout.insertWidget(
                    self._content_layout.count() - 1, frame
                )

        except Exception as fehler:
            logger.error(f"Fakten laden fehlgeschlagen: {fehler}")
            leer: QLabel = QLabel(f"Fehler: {fehler}")
            leer.setStyleSheet("color: #ff6b6b; font-size: 18px; padding: 20px;")
            self._content_layout.insertWidget(0, leer)
