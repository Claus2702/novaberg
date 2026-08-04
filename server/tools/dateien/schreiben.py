"""Schreibpfad des Wissensspeichers — Pfadwaechter und Modusbits.

Zwei Zusicherungen, die dieses Modul und nur dieses Modul traegt:

**Kein Schreibziel liegt im Arbeitsbaum.** Die Dateien der Bibliothek tragen
aus Gespraechen abgeleitete Recherchen. Laegen sie unterhalb des
Repositoriums, veroeffentlichte jeder Push sie. Der Waechter macht die
Grenze zu einer Eigenschaft des Codes statt zu einer Regel, an die sich
jemand erinnern muss (docs/novaberg-autonomous-wissen_k.md §11.1).

**Der Wirtsnutzer kann die Dateien bearbeiten.** Der Behaelter schreibt unter
fremder Kennung; ohne gesetzte Modusbits erscheinen die Dateien auf dem Wirt
mit Modus 644 unter fremdem Eigentuemer, und ein Fenster darauf ist der halbe
Zweck des Speichers. Gemessen am 04.08.2026: ohne die Bits scheitern Anhaengen
und Neuanlage mit `Keine Berechtigung`, mit ihnen funktioniert beides.

Die Modusbits stehen als Konstanten in config.py, nicht als Literale hier —
sie sind ein gemessener Betriebsparameter und gehoeren dorthin, wo die
uebrigen kalibrierten Werte stehen.
"""

import logging
import os
from pathlib import Path

from config import (
    WISSENSSPEICHER_DATEI_MODUS,
    WISSENSSPEICHER_VERZEICHNIS_MODUS,
    WISSENSSPEICHER_WURZEL,
)

logger = logging.getLogger("ki_server.tools.dateien.schreiben")

# Das Anwendungsverzeichnis, aus der Lage dieses Moduls abgeleitet:
# server/tools/dateien/schreiben.py -> parents[2] ist server/ bzw. /app.
# Bewusst abgeleitet und nicht konfiguriert — ein Waechter, den eine
# Umgebungsvariable verschieben kann, bewacht nichts.
ARBEITSBAUM: Path = Path(__file__).resolve().parents[2]


def schreibziel_pruefen(ziel: Path) -> Path:
    """Prueft ein Schreibziel gegen die Veroeffentlichungsgrenze.

    Vorbedingung: `ziel` ist ein Pfad; er muss nicht existieren.
    Nachbedingung: Der zurueckgegebene Pfad ist aufgeloest, liegt unterhalb
    der konfigurierten Wurzel und nicht unterhalb des Anwendungsverzeichnisses.
    Fehlerfaelle: leerer Pfad, Ziel ausserhalb der Wurzel, Ziel im
    Arbeitsbaum — alle drei als ValueError an den Aufrufer.

    Aufgeloest wird vor der Pruefung, damit weder `..` noch eine
    symbolische Verknuepfung an der Wurzel vorbeifuehrt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not str(ziel).strip():
        meldung: str = "schreibziel_pruefen: leerer Pfad uebergeben"
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    # strict=False: Die Datei darf noch nicht existieren, die Aufloesung
    # folgt trotzdem allen vorhandenen Verknuepfungen der Elternkette.
    aufgeloest: Path = Path(ziel).resolve(strict=False)
    wurzel: Path = Path(WISSENSSPEICHER_WURZEL).resolve(strict=False)

    # ── Ausgabe-Verifikation ────────────────────
    if not aufgeloest.is_relative_to(wurzel):
        meldung = (
            f"schreibziel_pruefen: Ziel liegt ausserhalb der Wurzel — "
            f"Ziel {aufgeloest}, Wurzel {wurzel}"
        )
        raise ValueError(meldung)

    if aufgeloest.is_relative_to(ARBEITSBAUM):
        meldung = (
            f"schreibziel_pruefen: Ziel liegt im Arbeitsbaum und wuerde beim "
            f"naechsten Push veroeffentlicht — Ziel {aufgeloest}, "
            f"Arbeitsbaum {ARBEITSBAUM}"
        )
        raise ValueError(meldung)

    return aufgeloest


def datei_schreiben(ziel: Path, inhalt: str) -> int:
    """Schreibt eine Datei der Bibliothek und gibt die Zahl der Bytes zurueck.

    Legt fehlende Elternverzeichnisse mit an. Vorhandener Inhalt wird
    ersetzt — die Wissen-Datei ist ein lebendes Dokument, ihr Fortschreiben
    ist Sache des Aufrufers.

    Vorbedingung: `ziel` besteht den Pfadwaechter, `inhalt` ist nicht leer.
    Nachbedingung: Die Datei existiert, ihre Groesse entspricht der Laenge
    des kodierten Inhalts, und ihre Modusbits sind gesetzt.
    Fehlerfaelle: verletzter Waechter oder leerer Inhalt (ValueError),
    Schreibfehler (OSError), abweichende Groesse nach dem Schreiben
    (RuntimeError) — alle an den Aufrufer, keiner geschluckt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not inhalt:
        meldung: str = f"datei_schreiben: leerer Inhalt fuer {ziel}"
        raise ValueError(meldung)

    geprueft: Path = schreibziel_pruefen(ziel)
    roh: bytes = inhalt.encode("utf-8")

    # ── Verarbeitung ────────────────────────────
    # umask 0 waehrend des Schreibens: Sonst zieht die Maske des Prozesses
    # die gewuenschten Bits wieder ab, und das Ergebnis saehe wie ein
    # gesetzter Modus aus, ohne einer zu sein.
    alte_maske: int = os.umask(0)
    try:
        geprueft.parent.mkdir(parents=True, exist_ok=True, mode=WISSENSSPEICHER_VERZEICHNIS_MODUS)
        geprueft.write_bytes(roh)
        os.chmod(geprueft, WISSENSSPEICHER_DATEI_MODUS)
    finally:
        os.umask(alte_maske)

    # ── Ausgabe-Verifikation ────────────────────
    # Ein gelungener Aufruf ist nicht dasselbe wie eine geschriebene Datei.
    geschrieben: int = geprueft.stat().st_size
    if geschrieben != len(roh):
        meldung = (
            f"datei_schreiben: {geprueft} traegt {geschrieben} Bytes, "
            f"geschrieben wurden {len(roh)}"
        )
        raise RuntimeError(meldung)

    modus_ist: int = geprueft.stat().st_mode & 0o777
    if modus_ist != WISSENSSPEICHER_DATEI_MODUS:
        # Kein Abbruch: Die Datei steht und ist vollstaendig. Aber der
        # Wirtsnutzer kann sie womoeglich nicht bearbeiten, und das waere
        # sonst erst am Obsidian-Fenster zu bemerken.
        logger.error(
            f"datei_schreiben: {geprueft} hat Modus {modus_ist:o}, "
            f"erwartet {WISSENSSPEICHER_DATEI_MODUS:o} — "
            f"der Wirtsnutzer kann die Datei moeglicherweise nicht bearbeiten"
        )

    logger.info(f"datei_schreiben: {geprueft} — {geschrieben} Bytes, Modus {modus_ist:o}")
    return geschrieben


def datei_lesen(ziel: Path) -> str:
    """Liest eine Datei der Bibliothek; gibt eine leere Zeichenkette zurueck, wenn sie fehlt.

    Der Waechter gilt auch beim Lesen: Ein Lesepfad, der aus der Wurzel
    heraustritt, ist derselbe Defekt wie ein Schreibpfad, der es tut — er
    macht ein Verzeichnis ausserhalb der Bibliothek zu ihrem Bestandteil.

    Vorbedingung: `ziel` besteht den Pfadwaechter.
    Nachbedingung: Der Rueckgabewert ist der Dateiinhalt oder leer, wenn die
    Datei nicht existiert. Fehlende Datei ist hier KEIN Fehler — die
    INDEX.md eines neuen Charakters gibt es beim ersten Schreiben noch nicht.
    Fehlerfaelle: verletzter Waechter (ValueError), Lesefehler (OSError).
    """
    # ── Eingabe-Validierung ─────────────────────
    geprueft: Path = schreibziel_pruefen(ziel)

    # ── Verarbeitung ────────────────────────────
    if not geprueft.is_file():
        return ""

    inhalt: str = geprueft.read_text(encoding="utf-8")

    # ── Ausgabe-Verifikation ────────────────────
    # Eine vorhandene, aber leere Datei ist ein anderer Fall als eine
    # fehlende: Der Aufrufer sieht beide als leere Zeichenkette, deshalb
    # steht der Unterschied wenigstens im Log.
    if not inhalt:
        logger.warning(f"datei_lesen: {geprueft} existiert, ist aber leer")

    return inhalt
