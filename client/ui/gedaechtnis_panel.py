"""
Gedächtnis Panel — Zeigt KZG, LZG, Charakter-Profile und Session-Kontext an.

Fuenf Tabs mit Live-Daten vom Server:
  Tab 1: Session          — Zusammenfassung + aktuelle Turns
  Tab 2: KZG (Kurzzeit)   — Aktuelle Themen mit Salienz, Dimension, TTL
  Tab 3: LZG (Langzeit)   — Destillierte Einträge mit Gewicht und Häufigkeit
  Tab 4: Charakter         — 5 Profile (Kern, Adaptiv, Intentionen, Emotionen, Beziehung)
  Tab 5: Emotionen         — Hexagon-Radar fuer Session und KZG Emotionscluster

Globaler Toggle Meister/Nova in der Kopfzeile schaltet alle Tabs um.
"""

import json
import logging
import time

import requests

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QScrollArea, QFrame, QTextEdit
)

from ui.icons import IC
from ui.emotions_radar import EmotionsRadar

logger = logging.getLogger("ki_client.gedaechtnis")


# ─────────────────────────────────────────────
# Styles: Panel, Tabs, Einträge, Hash-Textfelder
# ─────────────────────────────────────────────
PANEL_STYLE: str = """
    QWidget {
        background-color: #121212;
        color: #e0e0e0;
    }
"""

TAB_STYLE: str = """
    QTabWidget::pane {
        border: 1px solid #333333;
        background-color: #121212;
        border-radius: 4px;
    }
    QTabBar::tab {
        background-color: #1a1a1a;
        color: #b0b0b0;
        padding: 10px 20px;
        font-size: 18px;
        border: 1px solid #333333;
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    QTabBar::tab:selected {
        background-color: #1a3a5c;
        color: #4da6ff;
        font-weight: bold;
    }
    QTabBar::tab:hover {
        background-color: #2a2a2a;
        color: #ffffff;
    }
"""

EINTRAG_STYLE: str = """
    QFrame {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 8px;
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

HASH_STYLE: str = """
    QTextEdit {
        background-color: #1a1a1a;
        color: #e0e0e0;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 12px;
        font-size: 18px;
        line-height: 1.6;
    }
"""

HASH_LABEL_STYLE: str = """
    QLabel {
        background-color: #1a1a1a;
        color: #e0e0e0;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 12px;
        font-size: 18px;
    }
"""

SESSION_TURN_USER_STYLE: str = """
    QLabel {
        background-color: #1a3a5c;
        color: #e0e0e0;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 16px;
    }
"""

SESSION_TURN_ASSISTANT_STYLE: str = """
    QLabel {
        background-color: #2a2a2a;
        color: #e0e0e0;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 16px;
    }
"""

TOGGLE_AKTIV_STYLE: str = """
    QPushButton {
        background-color: #1a3a5c;
        color: #4da6ff;
        border: 1px solid #4da6ff;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 18px;
        font-weight: bold;
    }
"""

TOGGLE_INAKTIV_STYLE: str = """
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

KOMPAKT_EINTRAG_STYLE: str = """
    QFrame {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        padding: 2px;
    }
"""

LEER_STYLE: str = "color: #666666; font-size: 18px; padding: 20px;"


# ─────────────────────────────────────────────
# GedaechtnisPanel — Hauptwidget mit 4 Tabs
# ─────────────────────────────────────────────
class GedaechtnisPanel(QWidget):
    """Gedächtnis-Panel mit Tabs für Session, KZG, LZG und Charakter."""

    def __init__(self, server_url: str) -> None:
        super().__init__()

        self._server_url:   str = server_url
        self._aktiver_user: str = "meister"

        self.setStyleSheet(PANEL_STYLE)
        self._ui_erstellen()

    # ─────────────────────────────────────────
    # UI aufbauen (Kopfzeile + 4 Tabs)
    # ─────────────────────────────────────────
    def _ui_erstellen(self) -> None:
        """Erstellt Kopfzeile mit Toggle und vier Tabs: Session, KZG, LZG, Charakter."""

        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # -- Kopfzeile (Titel + Toggle + Refresh) --
        kopf: QHBoxLayout = QHBoxLayout()

        titel: QLabel = QLabel("  Gedaechtnis")
        titel.setStyleSheet("font-size: 27px; font-weight: bold; color: #4da6ff; padding: 4px;")

        self._toggle_meister: QPushButton = QPushButton("Meister")
        self._toggle_meister.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_meister.setStyleSheet(TOGGLE_AKTIV_STYLE)
        self._toggle_meister.clicked.connect(lambda: self._user_wechseln("meister"))

        self._toggle_nova: QPushButton = QPushButton("Nova")
        self._toggle_nova.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_nova.setStyleSheet(TOGGLE_INAKTIV_STYLE)
        self._toggle_nova.clicked.connect(lambda: self._user_wechseln("nova"))

        self._refresh_button: QPushButton = QPushButton("  Aktualisieren")
        self._refresh_button.setIcon(IC["refresh"])
        self._refresh_button.setIconSize(QSize(18, 18))
        self._refresh_button.setStyleSheet(REFRESH_STYLE)
        self._refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh_button.clicked.connect(self._alle_laden)

        kopf.addWidget(titel)
        kopf.addWidget(self._toggle_meister)
        kopf.addWidget(self._toggle_nova)
        kopf.addStretch()
        kopf.addWidget(self._refresh_button)
        layout.addLayout(kopf)

        # -- Tab-Widget --
        self._tabs: QTabWidget = QTabWidget()
        self._tabs.setStyleSheet(TAB_STYLE)

        # ── Tab 1: Session-Kontext ─────────────
        self._session_widget: QWidget = QWidget()
        self._session_layout: QVBoxLayout = QVBoxLayout(self._session_widget)
        self._session_layout.setContentsMargins(8, 8, 8, 8)
        self._session_layout.setSpacing(12)

        self._session_summary_label: QLabel = QLabel("Zusammenfassung aelterer Turns:")
        self._session_summary_label.setStyleSheet("color: #4da6ff; font-size: 18px; font-weight: bold;")
        self._session_summary_text: QTextEdit = QTextEdit()
        self._session_summary_text.setReadOnly(True)
        self._session_summary_text.setStyleSheet(HASH_STYLE)
        self._session_summary_text.setMaximumHeight(150)

        self._session_turns_label: QLabel = QLabel("Aktuelle Turns:")
        self._session_turns_label.setStyleSheet("color: #4da6ff; font-size: 18px; font-weight: bold;")

        self._session_scroll: QScrollArea = QScrollArea()
        self._session_scroll.setWidgetResizable(True)
        self._session_scroll.setStyleSheet("border: none;")
        self._session_turns_widget: QWidget = QWidget()
        self._session_turns_layout: QVBoxLayout = QVBoxLayout(self._session_turns_widget)
        self._session_turns_layout.setContentsMargins(0, 0, 0, 0)
        self._session_turns_layout.setSpacing(4)
        self._session_turns_layout.addStretch()
        self._session_scroll.setWidget(self._session_turns_widget)

        self._session_layout.addWidget(self._session_summary_label)
        self._session_layout.addWidget(self._session_summary_text)
        self._session_layout.addWidget(self._session_turns_label)
        self._session_layout.addWidget(self._session_scroll, stretch=1)

        self._tabs.addTab(self._session_widget, "Session")

        # ── Tab 2: KZG (Kurzzeit) ─────────────
        self._kzg_scroll: QScrollArea = QScrollArea()
        self._kzg_scroll.setWidgetResizable(True)
        self._kzg_scroll.setStyleSheet("border: none;")
        self._kzg_widget: QWidget = QWidget()
        self._kzg_layout: QVBoxLayout = QVBoxLayout(self._kzg_widget)
        self._kzg_layout.setContentsMargins(8, 8, 8, 8)
        self._kzg_layout.setSpacing(8)
        self._kzg_layout.addStretch()
        self._kzg_scroll.setWidget(self._kzg_widget)
        self._tabs.addTab(self._kzg_scroll, "KZG (Kurzzeit)")

        # ── Tab 3: LZG (Langzeit) ─────────────
        self._lzg_scroll: QScrollArea = QScrollArea()
        self._lzg_scroll.setWidgetResizable(True)
        self._lzg_scroll.setStyleSheet("border: none;")
        self._lzg_widget: QWidget = QWidget()
        self._lzg_layout: QVBoxLayout = QVBoxLayout(self._lzg_widget)
        self._lzg_layout.setContentsMargins(8, 8, 8, 8)
        self._lzg_layout.setSpacing(8)
        self._lzg_layout.addStretch()
        self._lzg_scroll.setWidget(self._lzg_widget)
        self._tabs.addTab(self._lzg_scroll, "LZG (Langzeit)")

        # ── Tab 4: Charakter ──────────────────
        self._hash_scroll: QScrollArea = QScrollArea()
        self._hash_scroll.setWidgetResizable(True)
        self._hash_scroll.setStyleSheet("border: none;")
        self._hash_widget: QWidget = QWidget()
        self._hash_layout: QVBoxLayout = QVBoxLayout(self._hash_widget)
        self._hash_layout.setContentsMargins(8, 8, 8, 8)
        self._hash_layout.setSpacing(12)

        # -- 5 Profil-Sektionen erstellen --
        self._kern_label: QLabel = QLabel("Kern-Hash (stabil)")
        self._kern_label.setStyleSheet("color: #4da6ff; font-size: 18px; font-weight: bold;")
        self._kern_text: QLabel = QLabel("(noch nicht destilliert)")
        self._kern_text.setWordWrap(True)
        self._kern_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._kern_text.setStyleSheet(HASH_LABEL_STYLE)
        self._kern_datum: QLabel = QLabel("")
        self._kern_datum.setStyleSheet("color: #666666; font-size: 14px;")

        self._adaptiv_label: QLabel = QLabel("Adaptiv-Hash (dynamisch)")
        self._adaptiv_label.setStyleSheet("color: #4da6ff; font-size: 18px; font-weight: bold;")
        self._adaptiv_text: QLabel = QLabel("(noch nicht destilliert)")
        self._adaptiv_text.setWordWrap(True)
        self._adaptiv_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._adaptiv_text.setStyleSheet(HASH_LABEL_STYLE)
        self._adaptiv_datum: QLabel = QLabel("")
        self._adaptiv_datum.setStyleSheet("color: #666666; font-size: 14px;")

        self._intentions_label: QLabel = QLabel("Intentions-Profil")
        self._intentions_label.setStyleSheet("color: #4da6ff; font-size: 18px; font-weight: bold;")
        self._intentions_text: QLabel = QLabel("(noch nicht destilliert)")
        self._intentions_text.setWordWrap(True)
        self._intentions_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._intentions_text.setStyleSheet(HASH_LABEL_STYLE)

        self._emotions_label: QLabel = QLabel("Emotions-Profil")
        self._emotions_label.setStyleSheet("color: #4da6ff; font-size: 18px; font-weight: bold;")
        self._emotions_text: QLabel = QLabel("(noch nicht destilliert)")
        self._emotions_text.setWordWrap(True)
        self._emotions_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._emotions_text.setStyleSheet(HASH_LABEL_STYLE)

        self._beziehung_label: QLabel = QLabel("Beziehungs-Profil")
        self._beziehung_label.setStyleSheet("color: #4da6ff; font-size: 18px; font-weight: bold;")
        self._beziehung_text: QLabel = QLabel("(noch nicht destilliert)")
        self._beziehung_text.setWordWrap(True)
        self._beziehung_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._beziehung_text.setStyleSheet(HASH_LABEL_STYLE)

        self._hash_layout.addWidget(self._kern_label)
        self._hash_layout.addWidget(self._kern_text)
        self._hash_layout.addWidget(self._kern_datum)
        self._hash_layout.addWidget(self._adaptiv_label)
        self._hash_layout.addWidget(self._adaptiv_text)
        self._hash_layout.addWidget(self._adaptiv_datum)
        self._hash_layout.addWidget(self._intentions_label)
        self._hash_layout.addWidget(self._intentions_text)
        self._hash_layout.addWidget(self._emotions_label)
        self._hash_layout.addWidget(self._emotions_text)
        self._hash_layout.addWidget(self._beziehung_label)
        self._hash_layout.addWidget(self._beziehung_text)
        self._hash_layout.addStretch()

        self._hash_scroll.setWidget(self._hash_widget)
        self._tabs.addTab(self._hash_scroll, "Charakter")

        # ── Tab 5: Emotionen (Radar) ────────────
        self._emo_widget: QWidget = QWidget()
        self._emo_layout: QHBoxLayout = QHBoxLayout(self._emo_widget)
        self._emo_layout.setContentsMargins(8, 8, 8, 8)
        self._emo_layout.setSpacing(16)

        self._radar_session: EmotionsRadar = EmotionsRadar("Session")
        self._radar_kzg:     EmotionsRadar = EmotionsRadar("KZG")

        self._emo_layout.addWidget(self._radar_session, stretch=1)
        self._emo_layout.addWidget(self._radar_kzg, stretch=1)

        self._tabs.addTab(self._emo_widget, "Emotionen")

        layout.addWidget(self._tabs, stretch=1)

        # Initialer Ladevorgang
        QTimer.singleShot(500, self._alle_laden)

    # ─────────────────────────────────────────
    # Alle Bereiche laden (Refresh-Button)
    # ─────────────────────────────────────────
    def _alle_laden(self) -> None:
        """Lädt alle fuenf Bereiche neu."""
        self._kzg_laden()
        self._lzg_laden()
        self._hash_laden()
        self._session_laden()
        self._emotionen_laden()

    # ─────────────────────────────────────────
    # KZG-Einträge laden (GET /gedaechtnis/kzg/{user_id})
    # ─────────────────────────────────────────
    def _kzg_laden(self) -> None:
        """Lädt KZG-Einträge und zeigt sie als Karten an."""

        self._layout_leeren(self._kzg_layout)

        try:
            response = requests.get(
                f"{self._server_url}/gedaechtnis/kzg/{self._aktiver_user}",
                timeout=10
            )
            daten: dict = response.json()
            eintraege: list = daten.get("eintraege", [])

            if not eintraege:
                leer: QLabel = QLabel("Keine KZG-Eintraege vorhanden.")
                leer.setStyleSheet(LEER_STYLE)
                leer.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._kzg_layout.insertWidget(0, leer)
                return

            # -- KZG-Einträge kompakt rendern (1 Zeile pro Eintrag) --
            for eintrag in eintraege:
                frame: QFrame = QFrame()
                frame.setStyleSheet(KOMPAKT_EINTRAG_STYLE)
                frame_layout: QHBoxLayout = QHBoxLayout(frame)
                frame_layout.setContentsMargins(8, 4, 8, 4)
                frame_layout.setSpacing(8)

                # Salienz (farbig, feste Breite)
                salienz: float = eintrag.get("salienz", 0)
                salienz_farbe: str = "#4caf50" if salienz >= 0.7 else "#ffa726" if salienz >= 0.5 else "#666666"
                salienz_label: QLabel = QLabel(f"{salienz:.2f}")
                salienz_label.setFixedWidth(45)
                salienz_label.setStyleSheet(f"color: {salienz_farbe}; font-size: 15px; font-weight: bold;")

                # Themen + Inhalt (gekürzt)
                themen: str = eintrag.get("themen", "")
                inhalt: str = eintrag.get("inhalt", "")
                inhalt_kurz: str = inhalt[:80] + "..." if len(inhalt) > 80 else inhalt
                text_label: QLabel = QLabel(f"<b>{themen}</b> — {inhalt_kurz}")
                text_label.setStyleSheet("color: #b0b0b0; font-size: 15px;")
                text_label.setTextFormat(Qt.TextFormat.RichText)

                # Meta (rechts, grau)
                dimension:   str = eintrag.get("dimension", "")
                haeufigkeit: int = eintrag.get("haeufigkeit", 1)
                ttl:         int = eintrag.get("ttl_sekunden", 0)
                ttl_tage:    float = ttl / 86400 if ttl > 0 else 0
                meta_label: QLabel = QLabel(f"{dimension} | H:{haeufigkeit} | {ttl_tage:.1f}d")
                meta_label.setStyleSheet("color: #555555; font-size: 13px;")
                meta_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                frame_layout.addWidget(salienz_label)
                frame_layout.addWidget(text_label, stretch=1)
                frame_layout.addWidget(meta_label)

                self._kzg_layout.insertWidget(self._kzg_layout.count() - 1, frame)

        except Exception as fehler:
            logger.error(f"KZG laden fehlgeschlagen: {fehler}")
            leer: QLabel = QLabel(f"Fehler: {fehler}")
            leer.setStyleSheet("color: #ff6b6b; font-size: 18px; padding: 20px;")
            self._kzg_layout.insertWidget(0, leer)

    # ─────────────────────────────────────────
    # LZG-Einträge laden (GET /gedaechtnis/lzg/{user_id})
    # ─────────────────────────────────────────
    def _lzg_laden(self) -> None:
        """Lädt LZG-Einträge und zeigt sie als Karten an."""

        self._layout_leeren(self._lzg_layout)

        try:
            response = requests.get(
                f"{self._server_url}/gedaechtnis/lzg/{self._aktiver_user}",
                timeout=10
            )
            daten: dict = response.json()
            eintraege: list = daten.get("eintraege", [])

            if not eintraege:
                leer: QLabel = QLabel("Keine LZG-Eintraege vorhanden.")
                leer.setStyleSheet(LEER_STYLE)
                leer.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._lzg_layout.insertWidget(0, leer)
                return

            # -- LZG-Einträge kompakt rendern (1 Zeile pro Eintrag) --
            for eintrag in eintraege:
                frame: QFrame = QFrame()
                frame.setStyleSheet(KOMPAKT_EINTRAG_STYLE)
                frame_layout: QHBoxLayout = QHBoxLayout(frame)
                frame_layout.setContentsMargins(8, 4, 8, 4)
                frame_layout.setSpacing(8)

                # Gewicht (farbig, feste Breite)
                gewicht: float = eintrag.get("gewicht", 0)
                gewicht_farbe: str = "#4caf50" if gewicht >= 0.7 else "#ffa726" if gewicht >= 0.5 else "#666666"
                gewicht_label: QLabel = QLabel(f"{gewicht:.2f}")
                gewicht_label.setFixedWidth(45)
                gewicht_label.setStyleSheet(f"color: {gewicht_farbe}; font-size: 15px; font-weight: bold;")

                # Dimension + Inhalt (gekürzt)
                dimension: str = eintrag.get("dimension", "").upper()
                inhalt: str = eintrag.get("inhalt", "")
                inhalt_kurz: str = inhalt[:80] + "..." if len(inhalt) > 80 else inhalt
                text_label: QLabel = QLabel(f"<b>{dimension}</b> — {inhalt_kurz}")
                text_label.setStyleSheet("color: #b0b0b0; font-size: 15px;")
                text_label.setTextFormat(Qt.TextFormat.RichText)

                # Meta (rechts, grau)
                haeufigkeit: int = eintrag.get("haeufigkeit", 1)
                verstaerkt:  str = eintrag.get("verstaerkt_am", "")[:10]
                meta_label: QLabel = QLabel(f"H:{haeufigkeit} | {verstaerkt}")
                meta_label.setStyleSheet("color: #555555; font-size: 13px;")
                meta_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                frame_layout.addWidget(gewicht_label)
                frame_layout.addWidget(text_label, stretch=1)
                frame_layout.addWidget(meta_label)

                self._lzg_layout.insertWidget(self._lzg_layout.count() - 1, frame)

        except Exception as fehler:
            logger.error(f"LZG laden fehlgeschlagen: {fehler}")
            leer: QLabel = QLabel(f"Fehler: {fehler}")
            leer.setStyleSheet("color: #ff6b6b; font-size: 18px; padding: 20px;")
            self._lzg_layout.insertWidget(0, leer)

    # ─────────────────────────────────────────
    # Globale User-Umschaltung (Meister / Nova)
    # ─────────────────────────────────────────
    def _user_wechseln(self, user_id: str) -> None:
        """Wechselt den aktiven User und lädt alle Tabs neu."""
        self._aktiver_user = user_id

        if user_id == "meister":
            self._toggle_meister.setStyleSheet(TOGGLE_AKTIV_STYLE)
            self._toggle_nova.setStyleSheet(TOGGLE_INAKTIV_STYLE)
        else:
            self._toggle_meister.setStyleSheet(TOGGLE_INAKTIV_STYLE)
            self._toggle_nova.setStyleSheet(TOGGLE_AKTIV_STYLE)

        self._alle_laden()

    # ─────────────────────────────────────────
    # Charakter-Hash laden (GET /gedaechtnis/hash/{user_id})
    # ─────────────────────────────────────────
    def _hash_laden(self) -> None:
        """Lädt alle 5 Charakter-Profile und zeigt sie in Textfeldern an."""

        try:
            response = requests.get(
                f"{self._server_url}/gedaechtnis/hash/{self._aktiver_user}",
                timeout=10
            )
            daten: dict = response.json()

            # Mapping: Instanz-Feld → API-Key
            felder: list[tuple[QLabel, str]] = [
                (self._kern_text,       "kern_hash"),
                (self._adaptiv_text,    "adaptive_hash"),
                (self._intentions_text, "intentions_profil"),
                (self._emotions_text,   "emotions_profil"),
                (self._beziehung_text,  "beziehungsprofil"),
            ]

            for label, key in felder:
                inhalt: str = daten.get(key, "")
                label.setText(inhalt if inhalt else "(noch nicht destilliert)")

            # Datums-Labels
            kern_datum: str = daten.get("kern_aktualisiert", "")[:19].replace("T", " ")
            adaptiv_datum: str = daten.get("adaptive_aktualisiert", "")[:19].replace("T", " ")
            self._kern_datum.setText(f"Aktualisiert: {kern_datum}" if kern_datum else "")
            self._adaptiv_datum.setText(f"Aktualisiert: {adaptiv_datum}" if adaptiv_datum else "")

        except Exception as fehler:
            logger.error(f"Hash laden fehlgeschlagen: {fehler}")
            self._kern_text.setText(f"Fehler: {fehler}")

    # ─────────────────────────────────────────
    # Session-Kontext laden (GET /session/kontext/{user_id})
    # ─────────────────────────────────────────
    def _session_laden(self) -> None:
        """Lädt Zusammenfassung und aktuelle Turns der Session."""

        self._layout_leeren(self._session_turns_layout)

        try:
            response = requests.get(
                f"{self._server_url}/session/kontext/{self._aktiver_user}",
                timeout=10
            )
            daten: dict = response.json()

            # -- Zusammenfassung älterer Turns --
            summary: str = daten.get("zusammenfassung", "")
            self._session_summary_text.setText(summary if summary else "(Noch keine Zusammenfassung)")

            # -- Aktuelle Turns --
            turns: list = daten.get("turns", [])
            anzahl: int = daten.get("anzahl_turns", 0)
            self._session_turns_label.setText(f"Aktuelle Turns ({anzahl}):")

            if not turns:
                leer: QLabel = QLabel("Keine aktive Session.")
                leer.setStyleSheet(LEER_STYLE)
                leer.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._session_turns_layout.insertWidget(0, leer)
                return

            # -- Turn-Labels rendern (User blau, Assistant grau) --
            for turn in turns:
                rolle: str = turn.get("rolle", "")
                inhalt: str = turn.get("inhalt", "")
                zeit: float = turn.get("zeit", 0)

                # Zeitstempel formatieren
                if zeit:
                    from datetime import datetime
                    zeit_str: str = datetime.fromtimestamp(zeit).strftime("%H:%M:%S")
                else:
                    zeit_str: str = ""

                label: QLabel = QLabel(f"[{zeit_str}] {inhalt}")
                label.setWordWrap(True)
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

                if rolle == "user":
                    label.setStyleSheet(SESSION_TURN_USER_STYLE)
                else:
                    label.setStyleSheet(SESSION_TURN_ASSISTANT_STYLE)

                self._session_turns_layout.insertWidget(
                    self._session_turns_layout.count() - 1, label
                )

        except Exception as fehler:
            logger.error(f"Session laden fehlgeschlagen: {fehler}")
            self._session_summary_text.setText(f"Fehler: {fehler}")

    # ─────────────────────────────────────────
    # Emotionen laden (GET /gedaechtnis/emotionen/{user_id})
    # ─────────────────────────────────────────
    def _emotionen_laden(self) -> None:
        """Lädt Emotions-Radar-Daten und aktualisiert beide Radar-Widgets."""

        try:
            response = requests.get(
                f"{self._server_url}/gedaechtnis/emotionen/{self._aktiver_user}",
                timeout=10
            )
            daten: dict = response.json()

            self._radar_session.werte_setzen(
                daten.get("session", {}),
                daten.get("session_turns", 0),
            )
            self._radar_kzg.werte_setzen(
                daten.get("kzg", {}),
                daten.get("kzg_eintraege", 0),
            )

        except Exception as fehler:
            logger.error(f"Emotionen laden fehlgeschlagen: {fehler}")

    # ─────────────────────────────────────────
    # Hilfsfunktion: Layout leeren (Stretch behalten)
    # ─────────────────────────────────────────
    def _layout_leeren(self, layout: QVBoxLayout) -> None:
        """Entfernt alle Widgets aus einem Layout, behält den Stretch am Ende."""

        while layout.count() > 1:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
