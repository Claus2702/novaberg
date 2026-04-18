"""
Chat Panel — Eingabe, Verlauf, SSE-Stream-Kommunikation mit dem Server.

Zeigt Pipeline-Stages live an und empfängt die Antwort als SSE-Event.
WebSocket empfängt Novas proaktive Impulse (Shadow Delivery).

Aufbau:
  [ Titel                                     ]
  [ Nachrichtenverlauf (ScrollArea)            ]
  [   User-Nachricht (rechtsbündig, blau)      ]
  [   Stage-Container (Pipeline-Fortschritt)   ]
  [   Assistant-Antwort (linksbündig, grün)     ]
  [   Nova-Impuls (linksbündig, grün)           ]
  [ Eingabezeile + Senden-Button              ]
"""

import json
import logging

from PySide6.QtCore       import Qt, QSize, QThread, Signal, QTimer
from PySide6.QtWidgets    import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFrame, QTextBrowser
)

import markdown

from ui.icons import IC, icon_label

logger = logging.getLogger("ki_client.chat")


def _markdown_zu_html(text: str, farbe: str = "#b0d0b0") -> str:
    """Konvertiert Markdown zu HTML mit Color-Emoji-Font-Fallback."""
    html_body: str = markdown.markdown(text)
    return (
        f'<div style="color: {farbe}; font-family: sans-serif, \'Noto Color Emoji\'; font-size: 20px;">'
        f'{html_body}'
        f'</div>'
    )


# ─────────────────────────────────────────────
# SSE-Stream-Worker (Chat-Anfrage → Server)
# ─────────────────────────────────────────────
class ChatStreamWorker(QThread):
    """
    Hintergrund-Thread: Sendet POST /chat/stream und parst SSE-Events.

    Signale:
      stage_erhalten   — Pipeline-Stage-Update (node, label, detail)
      antwort_erhalten — Finale Antwort (antwort, modell, token_total)
      fehler_erhalten  — Fehlermeldung als String
    """

    stage_erhalten   = Signal(dict)
    antwort_erhalten = Signal(dict)
    fehler_erhalten  = Signal(str)

    def __init__(self, server_url: str, prompt: str, user_id: str) -> None:
        super().__init__()
        self._server_url: str = server_url
        self._prompt:     str = prompt
        self._user_id:    str = user_id

    # ── SSE-Stream lesen und Events emittieren ──
    def run(self) -> None:
        import requests

        try:
            response = requests.post(
                f"{self._server_url}/chat/stream",
                json={"prompt": self._prompt, "user_id": self._user_id},
                stream=True,
                timeout=180
            )
            response.raise_for_status()

            event_type: str = ""
            data_buffer: str = ""

            for line in response.iter_lines(decode_unicode=True):
                if line is None:
                    continue

                if line.startswith("event: "):
                    event_type = line[7:].strip()
                    data_buffer = ""

                elif line.startswith("data: "):
                    data_buffer = line[6:]

                elif line == "" and event_type and data_buffer:
                    # Leere Zeile = Event komplett
                    try:
                        daten: dict = json.loads(data_buffer)

                        if event_type == "stage":
                            self.stage_erhalten.emit(daten)
                        elif event_type == "answer":
                            self.antwort_erhalten.emit(daten)
                        elif event_type == "error":
                            self.fehler_erhalten.emit(daten.get("fehler", "Unbekannter Fehler"))

                    except json.JSONDecodeError as fehler:
                        logger.warning(f"SSE JSON-Fehler: {fehler}")

                    event_type = ""
                    data_buffer = ""

        except Exception as fehler:
            self.fehler_erhalten.emit(f"Verbindungsfehler: {fehler}")


# ─────────────────────────────────────────────
# WebSocket-Worker (Novas proaktive Impulse)
# ─────────────────────────────────────────────
class WebSocketWorker(QThread):
    """
    Hintergrund-Thread: Hält eine WebSocket-Verbindung zum Server.
    Empfängt Shadow-Impulse (typ: "shadow_impuls") und emittiert sie.
    Reconnect bei Verbindungsverlust (5s Pause).

    Signale:
      impuls_erhalten — Shadow-Impuls-Dict (nachricht, thema, aufgabe)
      verbunden       — Verbindung hergestellt
      getrennt        — Verbindung verloren
    """

    impuls_erhalten = Signal(dict)
    verbunden       = Signal()
    getrennt        = Signal()

    def __init__(self, server_url: str, user_id: str) -> None:
        super().__init__()

        # http → ws
        ws_url: str = server_url.replace("http://", "ws://").replace("https://", "wss://")
        self._ws_url: str = f"{ws_url}/ws/{user_id}"
        self._aktiv:  bool = True

    # ── WebSocket-Empfangsschleife mit Reconnect ──
    def run(self) -> None:
        import websocket
        import time

        print(f"WebSocket-Worker: Versuche Verbindung zu {self._ws_url}")

        while self._aktiv:
            try:
                ws = websocket.WebSocket()
                ws.connect(self._ws_url, timeout=30)
                ws.settimeout(None)
                self.verbunden.emit()

                logger.info(f"WebSocket verbunden: {self._ws_url}")

                while self._aktiv:
                    try:
                        raw: str = ws.recv()

                        if not raw:
                            continue

                        print(f"[WS-DEBUG] Empfangen: {raw[:100]}")

                        daten: dict = json.loads(raw)

                        if daten.get("typ") == "shadow_impuls":
                            print(f"[WS-DEBUG] Impuls erkannt, emit Signal")
                            self.impuls_erhalten.emit(daten)

                    except json.JSONDecodeError:
                        continue
                    except websocket.WebSocketConnectionClosedException:
                        logger.info("WebSocket: Verbindung vom Server geschlossen")
                        break
                    except Exception as fehler:
                        logger.warning(f"WebSocket recv-Fehler: {type(fehler).__name__}: {fehler}")
                        break

                ws.close()

            except Exception as fehler:
                logger.warning(f"WebSocket-Fehler: {fehler}")
                self.getrennt.emit()

            # Reconnect-Pause
            if self._aktiv:
                time.sleep(5)

    def stoppen(self) -> None:
        """Beendet den Worker sauber."""
        self._aktiv = False


# ─────────────────────────────────────────────
# Styles: Chat-Nachrichten, Eingabe, Pipeline-Stages
# ─────────────────────────────────────────────
CHAT_STYLE: str = """
    QWidget {
        background-color: #121212;
        color: #e0e0e0;
    }
"""

NACHRICHT_USER_STYLE: str = """
    QLabel {
        background-color: #1a3a5c;
        color: #e0e0e0;
        border-radius: 10px;
        border-right: 3px solid #4da6ff;
        padding: 10px 14px;
        font-size: 20px;
        font-family: sans-serif, 'Noto Color Emoji', 'Noto Emoji';
    }
"""

NACHRICHT_ASSISTANT_STYLE: str = """
    QLabel {
        background-color: #1a2a1a;
        color: #b0d0b0;
        border-radius: 10px;
        border-left: 3px solid #4caf50;
        padding: 10px 14px;
        font-size: 20px;
        font-family: sans-serif, 'Noto Color Emoji', 'Noto Emoji';
    }
"""

EINGABE_STYLE: str = """
    QLineEdit {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #444444;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 20px;
    }
    QLineEdit:focus {
        border-color: #4da6ff;
    }
"""

SENDEN_STYLE: str = """
    QPushButton {
        background-color: #4da6ff;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 20px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #3a8fd4;
    }
    QPushButton:disabled {
        background-color: #333333;
        color: #666666;
    }
"""

STAGE_STYLE: str = """
    QLabel {
        color: #4da6ff;
        font-size: 11px;
        padding: 0px 14px;
        line-height: 1.0;
        font-family: monospace;
    }
"""

STAGE_DONE_STYLE: str = """
    QLabel {
        color: #4caf50;
        font-size: 11px;
        padding: 0px 14px;
        line-height: 1.0;
        font-family: monospace;
    }
"""


# ─────────────────────────────────────────────
# ChatPanel — Hauptwidget
# ─────────────────────────────────────────────
class ChatPanel(QWidget):
    """Chat-Panel mit Nachrichtenverlauf, SSE-Stream und Pipeline-Anzeige."""

    def __init__(self, server_url: str) -> None:
        super().__init__()

        self._server_url: str = server_url
        self._user_id:    str = "meister"
        self._worker:     ChatStreamWorker = None
        self._stage_labels: list[QWidget] = []

        self.setStyleSheet(CHAT_STYLE)
        self._ui_erstellen()

        # WebSocket für Novas proaktive Nachrichten
        self._ws_worker: WebSocketWorker = WebSocketWorker(self._server_url, self._user_id)
        self._ws_worker.impuls_erhalten.connect(self._impuls_verarbeiten)
        self._ws_worker.start()

    # ─────────────────────────────────────────
    # UI aufbauen (Titel, Verlauf, Eingabezeile)
    # ─────────────────────────────────────────
    def _ui_erstellen(self) -> None:
        """Erstellt Titel, Scroll-Verlauf und Eingabezeile."""

        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # -- Titel --
        titel: QLabel = QLabel("  Chat")
        titel.setStyleSheet("font-size: 27px; font-weight: bold; color: #4da6ff; padding: 4px;")
        layout.addWidget(titel)

        # -- Nachrichtenverlauf (ScrollArea) --
        self._scroll_area: QScrollArea = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #121212;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #444444;
                border-radius: 4px;
            }
        """)

        self._verlauf_widget: QWidget = QWidget()
        self._verlauf_layout: QVBoxLayout = QVBoxLayout(self._verlauf_widget)
        self._verlauf_layout.setContentsMargins(0, 0, 0, 0)
        self._verlauf_layout.setSpacing(8)
        self._verlauf_layout.addStretch()

        self._scroll_area.setWidget(self._verlauf_widget)
        layout.addWidget(self._scroll_area, stretch=1)

        # -- Eingabezeile + Senden-Button --
        eingabe_layout: QHBoxLayout = QHBoxLayout()
        eingabe_layout.setSpacing(8)

        self._eingabe: QLineEdit = QLineEdit()
        self._eingabe.setPlaceholderText("Nachricht eingeben...")
        self._eingabe.setStyleSheet(EINGABE_STYLE)
        self._eingabe.returnPressed.connect(self._nachricht_senden)

        self._senden_button: QPushButton = QPushButton("Senden")
        self._senden_button.setIcon(IC["senden"])
        self._senden_button.setIconSize(QSize(20, 20))
        self._senden_button.setStyleSheet(SENDEN_STYLE)
        self._senden_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._senden_button.clicked.connect(self._nachricht_senden)

        eingabe_layout.addWidget(self._eingabe, stretch=1)
        eingabe_layout.addWidget(self._senden_button)

        layout.addLayout(eingabe_layout)

    # ─────────────────────────────────────────
    # Nachricht senden (SSE-Stream starten)
    # ─────────────────────────────────────────
    def _nachricht_senden(self) -> None:
        """Sendet die Eingabe an den Server via SSE-Stream."""

        text: str = self._eingabe.text().strip()

        if not text:
            return

        self._eingabe.clear()
        self._eingabe.setEnabled(False)
        self._senden_button.setEnabled(False)

        # User-Nachricht anzeigen
        self._nachricht_anzeigen(text, ist_user=True)

        # Stage-Container für Pipeline-Anzeige
        self._stage_container: QFrame = QFrame()
        self._stage_container.setStyleSheet("background-color: #1a1a1a; border-radius: 8px; padding: 4px;")
        self._stage_container_layout: QVBoxLayout = QVBoxLayout(self._stage_container)
        self._stage_container_layout.setContentsMargins(8, 4, 8, 4)
        self._stage_container_layout.setSpacing(0)
        self._stage_labels = []

        self._verlauf_layout.addWidget(self._stage_container)
        self._nach_unten_scrollen()

        # Worker starten
        self._worker = ChatStreamWorker(self._server_url, text, self._user_id)
        self._worker.stage_erhalten.connect(self._stage_verarbeiten)
        self._worker.antwort_erhalten.connect(self._antwort_verarbeiten)
        self._worker.fehler_erhalten.connect(self._fehler_verarbeiten)
        self._worker.start()

    # ─────────────────────────────────────────
    # Pipeline-Stage-Updates anzeigen
    # ─────────────────────────────────────────
    def _stage_verarbeiten(self, daten: dict) -> None:
        """Zeigt einen Pipeline-Stage-Update an (vorherige Stage → fertig-Icon)."""

        node:   str = daten.get("node", "")
        label:  str = daten.get("label", node)
        detail: str = daten.get("detail", "")

        # Vorherige Stage als erledigt markieren
        if self._stage_labels:
            letzte = self._stage_labels[-1]
            self._stage_icon_setzen(letzte, "stage.fertig")

        # Neue Stage anzeigen
        detail_str: str = f" -- {detail}" if detail else ""
        stage_widget = icon_label("stage.aktiv", f"{label}{detail_str}", icon_size=14, font_size=11)
        stage_widget.setStyleSheet("background-color: transparent;")

        self._stage_labels.append(stage_widget)
        self._stage_container_layout.addWidget(stage_widget)
        self._nach_unten_scrollen()

    # ─────────────────────────────────────────
    # Finale Antwort empfangen und anzeigen
    # ─────────────────────────────────────────
    def _stage_icon_setzen(self, widget: QWidget, token: str) -> None:
        """Ersetzt das Icon im ersten QLabel (Pixmap) eines icon_label-Widgets."""
        for child in widget.children():
            if isinstance(child, QLabel) and child.pixmap() and not child.pixmap().isNull():
                child.setPixmap(IC.pixmap(token, 14))
                break

    def _antwort_verarbeiten(self, daten: dict) -> None:
        """Zeigt die finale Antwort an, markiert letzte Stage als fertig."""

        # Letzte Stage als erledigt markieren
        if self._stage_labels:
            letzte = self._stage_labels[-1]
            self._stage_icon_setzen(letzte, "stage.fertig")

        # Antwort anzeigen
        antwort: str = daten.get("antwort", "Keine Antwort erhalten.")
        self._nachricht_anzeigen(antwort, ist_user=False)

        # Token-Info unter der Antwort
        token: int = daten.get("token_total", 0)
        modell: str = daten.get("modell", "")
        if token > 0:
            info: QLabel = QLabel(f"    {modell}  |  {token} Tokens")
            info.setStyleSheet("color: #444444; font-size: 16px; padding: 0 14px;")
            self._verlauf_layout.addWidget(info)

        self._eingabe.setEnabled(True)
        self._senden_button.setEnabled(True)
        self._eingabe.setFocus()
        self._nach_unten_scrollen()

    # ─────────────────────────────────────────
    # Fehlermeldung anzeigen
    # ─────────────────────────────────────────
    def _fehler_verarbeiten(self, fehler: str) -> None:
        """Zeigt eine Fehlermeldung im Verlauf an und gibt die Eingabe frei."""

        fehler_widget = icon_label("fehler", fehler, icon_size=20, font_size=20, text_color="#ff6b6b")
        self._verlauf_layout.addWidget(fehler_widget)

        self._eingabe.setEnabled(True)
        self._senden_button.setEnabled(True)
        self._eingabe.setFocus()
        self._nach_unten_scrollen()

    # ─────────────────────────────────────────
    # Delivery in den Chat einspeisen (Nova-Impulse via WebSocket)
    # ─────────────────────────────────────────
    def _impuls_verarbeiten(self, daten: dict) -> None:
        """Zeigt einen proaktiven Shadow-Impuls von Nova als Chat-Nachricht an."""

        print(f"[WS-DEBUG] _impuls_verarbeiten aufgerufen: {daten}")

        try:
            nachricht: str = daten.get("nachricht", "")
            thema:     str = daten.get("thema", "")

            if not nachricht:
                return

            browser: QTextBrowser = QTextBrowser()
            browser.setOpenExternalLinks(True)
            browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            browser.setFrameShape(QFrame.Shape.NoFrame)

            from PySide6.QtGui import QTextOption
            browser.document().setDefaultTextOption(
                QTextOption(Qt.AlignmentFlag.AlignLeft)
            )
            browser.document().setDocumentMargin(0)

            browser.setHtml(_markdown_zu_html(nachricht, "#b0d0b0"))
            browser.setStyleSheet(NACHRICHT_ASSISTANT_STYLE.replace("QLabel", "QTextBrowser"))

            # Höhe an Inhalt anpassen (verzögert, nach Layout)
            def hoehe_anpassen():
                breite: int = browser.viewport().width()
                if breite < 100:
                    breite = browser.width() - 30
                if breite < 100:
                    breite = 600
                browser.document().setTextWidth(breite)
                doc_height: int = int(browser.document().size().height()) + 30
                browser.setFixedHeight(doc_height)
                self._nach_unten_scrollen()

            QTimer.singleShot(50, hoehe_anpassen)

            container: QWidget = QWidget()
            container_layout: QHBoxLayout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)
            container_layout.addWidget(browser, 4)
            container_layout.addStretch(1)

            self._verlauf_layout.addWidget(container)
            self._nach_unten_scrollen()

            logger.info(f"Nova-Impuls angezeigt: '{thema[:40]}'")

        except Exception as fehler:
            logger.error(f"Impuls-Anzeige fehlgeschlagen: {fehler}")

    # ─────────────────────────────────────────
    # Nachricht im Verlauf anzeigen (User / Assistant)
    # ─────────────────────────────────────────
    def _nachricht_anzeigen(self, text: str, ist_user: bool) -> None:
        """Zeigt eine Nachricht an: User rechtsbündig (blau), Assistant linksbündig (grün)."""

        browser: QTextBrowser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        browser.setFrameShape(QFrame.Shape.NoFrame)

        # Linksbündig statt Blocksatz
        from PySide6.QtGui import QTextOption
        browser.document().setDefaultTextOption(
            QTextOption(Qt.AlignmentFlag.AlignLeft)
        )
        # HTML-Margins eliminieren
        browser.document().setDocumentMargin(0)

        if ist_user:
            browser.setPlainText(text)
            browser.setStyleSheet(NACHRICHT_USER_STYLE.replace("QLabel", "QTextBrowser"))
        else:
            browser.setHtml(_markdown_zu_html(text, "#b0d0b0"))
            browser.setStyleSheet(NACHRICHT_ASSISTANT_STYLE.replace("QLabel", "QTextBrowser"))

        # Höhe an Inhalt anpassen (verzögert, nach Layout)
        def hoehe_anpassen():
            breite: int = browser.viewport().width()
            if breite < 100:
                breite = browser.width() - 30
            if breite < 100:
                breite = 600
            browser.document().setTextWidth(breite)
            doc_height: int = int(browser.document().size().height()) + 30
            browser.setFixedHeight(doc_height)
            self._nach_unten_scrollen()

        QTimer.singleShot(50, hoehe_anpassen)

        # Container für Ausrichtung (80% Breite)
        container: QWidget = QWidget()
        container_layout: QHBoxLayout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        if ist_user:
            container_layout.addStretch(1)
            container_layout.addWidget(browser, 4)
        else:
            container_layout.addWidget(browser, 4)
            container_layout.addStretch(1)

        self._verlauf_layout.addWidget(container)

    # ─────────────────────────────────────────
    # Auto-Scroll nach unten
    # ─────────────────────────────────────────
    def _nach_unten_scrollen(self) -> None:
        """Scrollt den Verlauf nach unten (50ms Verzögerung für Layout-Update)."""

        QTimer.singleShot(50, lambda: self._scroll_area.verticalScrollBar().setValue(
            self._scroll_area.verticalScrollBar().maximum()
        ))
