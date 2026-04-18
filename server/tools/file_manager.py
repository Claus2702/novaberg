"""FileManager — Dateisystem-Zugriff mit Lock-Dict pro Dateipfad."""

import asyncio
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileManager:
    """Kapselt Dateisystem-Zugriff. Lock-Dict für Schreibschutz pro Datei."""

    def __init__(self):
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock_fuer(self, pfad: str) -> asyncio.Lock:
        """Ein Lock pro Dateipfad, lazy erzeugt."""
        if pfad not in self._locks:
            self._locks[pfad] = asyncio.Lock()
        return self._locks[pfad]

    async def schreiben(self, pfad: str, inhalt: str) -> None:
        """Datei schreiben mit Lock-Schutz."""
        async with self._lock_fuer(pfad):
            Path(pfad).parent.mkdir(parents=True, exist_ok=True)
            Path(pfad).write_text(inhalt, encoding="utf-8")

    def lesen(self, pfad: str) -> str:
        """Datei lesen. Kein Lock nötig — atomare Operation."""
        return Path(pfad).read_text(encoding="utf-8")

    def existiert(self, pfad: str) -> bool:
        """Prüft ob Datei existiert."""
        return Path(pfad).exists()

    def hash(self, pfad: str) -> str:
        """SHA-256 Hash für Änderungs-Erkennung."""
        return hashlib.sha256(Path(pfad).read_bytes()).hexdigest()

    def auflisten(self, verzeichnis: str, muster: str = "*") -> list[str]:
        """Dateien in Verzeichnis auflisten."""
        return [str(p) for p in Path(verzeichnis).rglob(muster) if p.is_file()]

    def suchen(self, verzeichnis: str, suchtext: str) -> list[str]:
        """Grep-artige Textsuche, gibt Dateipfade mit Treffern zurück."""
        treffer = []
        for datei in Path(verzeichnis).rglob("*"):
            if datei.is_file():
                try:
                    inhalt = datei.read_text(encoding="utf-8", errors="ignore")
                    if suchtext in inhalt:
                        treffer.append(str(datei))
                except (OSError, UnicodeDecodeError):
                    continue
        return treffer


# Modul-Level-Instanz
file_manager = FileManager()
