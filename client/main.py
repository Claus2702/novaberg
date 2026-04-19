"""
Einstiegspunkt für den Nova GTK4-Client.

Startet eine :class:`Gtk.Application` mit der ID ``de.novaberg.client``
und öffnet im ``activate``-Handler das Hauptfenster. Das Logging wird
aus :mod:`config` konfiguriert; zusätzliche Argumente werden bewusst
nicht geparst — alle Einstellungen leben in config.py.
"""

import logging
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gtk  # noqa: E402

# Projekt-Root in den sys.path aufnehmen, damit ``from config import ...``
# auch beim Start als Modul (``python3 -m client.main``) funktioniert.
# Wenn die Datei direkt aufgerufen wird, ist das Verzeichnis ohnehin schon drin.
from pathlib import Path  # noqa: E402

_CLIENT_ROOT = Path(__file__).resolve().parent
if str(_CLIENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_CLIENT_ROOT))

from config            import LOG_FORMAT, LOG_LEVEL  # noqa: E402
from ui.main_window    import MainWindow            # noqa: E402


logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    """Root-Logger gemäß config.py aufsetzen."""
    level: int = getattr(logging, LOG_LEVEL.upper(), logging.DEBUG)
    logging.basicConfig(format=LOG_FORMAT, level=level)
    logger.debug(f"Logging konfiguriert (Level={LOG_LEVEL})")


class NovaApplication(Gtk.Application):
    """Kleiner Wrapper um Gtk.Application mit eigenem Lifecycle-Log."""

    def __init__(self) -> None:
        super().__init__(application_id="de.novaberg.client")
        logger.debug("NovaApplication erzeugt (application_id='de.novaberg.client')")
        self._main_window: MainWindow | None = None

        self.connect("activate", self._on_activate)
        self.connect("shutdown", self._on_shutdown)

    def _on_activate(self, app: Gtk.Application) -> None:
        """Wird bei jedem Start aktiviert — legt Fenster an und zeigt es."""
        logger.info("Application.activate — MainWindow wird angezeigt")
        if self._main_window is None:
            self._main_window = MainWindow(application=self)
        self._main_window.present()

    def _on_shutdown(self, app: Gtk.Application) -> None:
        """Wird einmal beim Beenden gefeuert — hier greift das close-request bereits."""
        logger.info("Application.shutdown")


def main() -> int:
    """Programmstart: Logging + Application.run()."""
    _configure_logging()
    logger.info("Nova-Client startet")

    app = NovaApplication()
    # ``Gtk.Application.run`` erwartet die Programmargumente und gibt den
    # Exit-Code zurück. Wir reichen sys.argv durch, damit GTK-Argumente
    # (z.B. --display) weiterhin funktionieren.
    exit_code: int = app.run(sys.argv)
    logger.info(f"Nova-Client beendet (Exit-Code={exit_code})")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
