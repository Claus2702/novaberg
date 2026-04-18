"""
KI-Assistent — Desktop-Client (PySide6).

Einstiegspunkt: Erstellt die QApplication, setzt die globale Schriftart
(Emoji-fähig) und öffnet das Hauptfenster.
"""

import sys

from PySide6.QtWidgets import QApplication
from ui.hauptfenster import Hauptfenster


# ─────────────────────────────────────────────
# Applikation starten
# ─────────────────────────────────────────────
def main() -> None:
    app: QApplication = QApplication(sys.argv)

    # Schriftart auf Application-Level
    from PySide6.QtGui import QFont

    font: QFont = QFont("Noto Sans")
    font.setFamilies(["Noto Sans", "sans-serif"])
    font.setPointSize(11)
    app.setFont(font)

    fenster: Hauptfenster = Hauptfenster()
    fenster.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
