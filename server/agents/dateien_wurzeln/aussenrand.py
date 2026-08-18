"""Der Aussenrand — die Schranke, die kein Gespraech verschieben kann.

Spezifikation: docs/novaberg-agent-dateien_k.md §7, Regel 3.

Eine Verzeichnis-Freigabe entsteht aus einer Aeusserung. Damit bestimmt ein
gesprochener Satz einen Pfad im Dateisystem — die Stelle, an der ein Dienst
mit Dateizugriff gefaehrlich wird. Ein Bestaetigungstor allein genuegt dort
nicht, weil der Mensch am Tor die Zeichenkette sieht und nicht das
Verzeichnis, in dem sie landet.

Drei Regeln, und die Reihenfolge ist die Regel:

**a) Der Rand steht in der Konfiguration, nicht im Gespraech.** Ausserhalb
wird abgewiesen, auch auf Bestaetigung. Ein leerer Rand heisst "nichts ist
freigebbar" und nicht "alles" — der Wachtposten faellt geschlossen aus.

**b) Aufgeloest wird VOR der Pruefung.** Wer erst prueft und dann aufloest,
hat eine Zeichenkette bewacht. `..` und symbolische Verknuepfungen sind an
dieser Stelle bereits weg.

**c) Bestaetigt wird das Ergebnis der Aufloesung.** Deshalb traegt der
Befund den aufgeloesten Pfad und die Dateizahl — nicht die Eingabe. Wer
`../..` sagt, sieht, wo er landet, und wer sich vertippt hat, sieht es an
der Zahl.

Dieses Modul hat keinen Schreibpfad ins Dateisystem und importiert keinen.
Das ist die Zusicherung aus §7 Regel 2: Ein Recht, das nicht im Modul liegt,
kann kein Prompt herbeireden.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from config import DATEIEN_AUSSENRAND, DATEIEN_WURZEL_ZAEHLGRENZE

logger = logging.getLogger("ki_server.agents.dateien_wurzeln.aussenrand")


@dataclass(frozen=True)
class WurzelBefund:
    """Das Ergebnis der Randpruefung — der Beleg fuer das Tor.

    `dateizahl` ist die Zahl der Dateien unterhalb des aufgeloesten Pfades.
    Wurde die Zaehlgrenze erreicht, steht `gezaehlt_vollstaendig` auf False;
    das Tor sagt dann "mindestens N" statt einer Endzahl, die es nicht hat.

    `grund` ist bei `ok=False` die Begruendung in der Sprache des Menschen —
    sie geht in die Ablehnung und traegt den aufgeloesten Pfad, weil eine
    Ablehnung ohne ihn nicht nachvollziehbar ist.
    """

    ok: bool
    aufgeloest: Path | None
    dateizahl: int
    gezaehlt_vollstaendig: bool
    rand: str
    grund: str


def _rand_aufloesen() -> list[Path]:
    """Loest die konfigurierten Elternverzeichnisse auf.

    Vorbedingung: keine.
    Nachbedingung: Liste der aufgeloesten Randpfade; leer, wenn nichts
    konfiguriert ist. Ein leerer Rand ist ein Betriebszustand und kein
    Absturz — er wird gemeldet und laesst nichts durch.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not DATEIEN_AUSSENRAND:
        logger.error(
            "Aussenrand: DATEIEN_AUSSENRAND ist leer — es kann kein "
            "Verzeichnis freigegeben werden. Das ist der geschlossene "
            "Ausfall und nicht 'alles erlaubt'"
        )
        return []

    # ── Verarbeitung ────────────────────────────
    return [Path(eintrag).resolve(strict=False) for eintrag in DATEIEN_AUSSENRAND]


def _dateien_zaehlen(verzeichnis: Path) -> tuple[int, bool]:
    """Zaehlt die Dateien unterhalb eines Verzeichnisses bis zur Grenze.

    Vorbedingung: `verzeichnis` existiert und ist ein Verzeichnis.
    Nachbedingung: (Zahl, vollstaendig). `vollstaendig` ist False, sobald die
    Zaehlgrenze erreicht wurde — dann ist die Zahl eine Untergrenze.

    Symbolischen Verknuepfungen wird nicht gefolgt: Ein Verweis aus dem
    freigegebenen Baum heraus wuerde sonst Dateien mitzaehlen, die gar nicht
    dort liegen, und die Zahl am Tor waere eine falsche Auskunft.
    """
    gezaehlt: int = 0
    for _wurzel, _ordner, dateien in os.walk(verzeichnis, followlinks=False):
        gezaehlt += len(dateien)
        if gezaehlt >= DATEIEN_WURZEL_ZAEHLGRENZE:
            logger.warning(
                "Aussenrand: Zaehlgrenze %d bei '%s' erreicht — die Zahl am "
                "Tor ist eine Untergrenze, keine Endzahl",
                DATEIEN_WURZEL_ZAEHLGRENZE, verzeichnis,
            )
            return DATEIEN_WURZEL_ZAEHLGRENZE, False

    return gezaehlt, True


def wurzel_pruefen(eingabe: str) -> WurzelBefund:
    """Loest einen genannten Pfad auf und haelt ihn gegen den Aussenrand.

    Vorbedingung: `eingabe` ist der Pfad, wie der Mensch ihn genannt hat —
    ungeprueft, moeglicherweise relativ, mit `..` oder ueber eine
    symbolische Verknuepfung.
    Nachbedingung: Bei `ok=True` liegt `aufgeloest` unterhalb eines
    konfigurierten Randes, existiert, ist ein Verzeichnis und ist lesbar;
    `dateizahl` ist erhoben. Bei `ok=False` traegt `grund` die Begruendung
    samt aufgeloestem Pfad und geltendem Rand.

    Fehlerfaelle geben immer einen Befund zurueck und werfen nicht: Die
    Ablehnung ist hier ein Urteil des Dienstes und keine Stoerung — sie geht
    ueber den vierten Ausgang an den Auftraggeber (§8.2a).
    """
    # ── Eingabe-Validierung ─────────────────────
    rand: list[Path] = _rand_aufloesen()
    rand_anzeige: str = ", ".join(str(p) for p in rand) if rand else "(keiner konfiguriert)"

    if not eingabe or not eingabe.strip():
        logger.error("Aussenrand: leerer Pfad uebergeben — abgewiesen")
        return WurzelBefund(
            ok=False, aufgeloest=None, dateizahl=0, gezaehlt_vollstaendig=True,
            rand=rand_anzeige,
            grund="Es wurde kein Verzeichnis genannt.",
        )

    if not rand:
        return WurzelBefund(
            ok=False, aufgeloest=None, dateizahl=0, gezaehlt_vollstaendig=True,
            rand=rand_anzeige,
            grund=(
                "Es ist kein zulaessiger Bereich konfiguriert — solange das so "
                "ist, kann kein Verzeichnis freigegeben werden."
            ),
        )

    # ── Verarbeitung ────────────────────────────
    # strict=False, damit ein nicht existierender Pfad hier nicht wirft: Die
    # Existenz ist ein eigener Befund mit eigener Begruendung, und der Mensch
    # soll erfahren, WO sein Pfad gelandet waere.
    aufgeloest: Path = Path(eingabe.strip()).resolve(strict=False)

    # ── Ausgabe-Verifikation ────────────────────
    innerhalb: bool = any(aufgeloest.is_relative_to(grenze) for grenze in rand)
    if not innerhalb:
        logger.error(
            "Aussenrand: '%s' loest auf zu '%s' und liegt ausserhalb des "
            "zulaessigen Bereichs (%s) — abgewiesen, auch mit Bestaetigung",
            eingabe, aufgeloest, rand_anzeige,
        )
        return WurzelBefund(
            ok=False, aufgeloest=aufgeloest, dateizahl=0,
            gezaehlt_vollstaendig=True, rand=rand_anzeige,
            grund=(
                f"'{eingabe}' fuehrt zu {aufgeloest}, und das liegt ausserhalb "
                f"des zulaessigen Bereichs ({rand_anzeige})."
            ),
        )

    if not aufgeloest.exists():
        logger.error(
            "Aussenrand: '%s' loest auf zu '%s' — existiert nicht", eingabe, aufgeloest,
        )
        return WurzelBefund(
            ok=False, aufgeloest=aufgeloest, dateizahl=0,
            gezaehlt_vollstaendig=True, rand=rand_anzeige,
            grund=f"Unter {aufgeloest} liegt nichts.",
        )

    if not aufgeloest.is_dir():
        logger.error(
            "Aussenrand: '%s' loest auf zu '%s' — kein Verzeichnis", eingabe, aufgeloest,
        )
        return WurzelBefund(
            ok=False, aufgeloest=aufgeloest, dateizahl=0,
            gezaehlt_vollstaendig=True, rand=rand_anzeige,
            grund=f"{aufgeloest} ist eine Datei, kein Verzeichnis.",
        )

    if not os.access(aufgeloest, os.R_OK | os.X_OK):
        logger.error(
            "Aussenrand: '%s' ist nicht lesbar — Freigabe waere wirkungslos", aufgeloest,
        )
        return WurzelBefund(
            ok=False, aufgeloest=aufgeloest, dateizahl=0,
            gezaehlt_vollstaendig=True, rand=rand_anzeige,
            grund=f"{aufgeloest} ist fuer mich nicht lesbar.",
        )

    dateizahl, vollstaendig = _dateien_zaehlen(aufgeloest)
    logger.info(
        "Aussenrand: '%s' -> '%s' innerhalb von %s, %d Dateien%s",
        eingabe, aufgeloest, rand_anzeige, dateizahl,
        "" if vollstaendig else " (Untergrenze, Zaehlgrenze erreicht)",
    )

    return WurzelBefund(
        ok=True, aufgeloest=aufgeloest, dateizahl=dateizahl,
        gezaehlt_vollstaendig=vollstaendig, rand=rand_anzeige, grund="",
    )


def rand_text() -> str:
    """Nennt den geltenden Aussenrand in lesbarer Form.

    Vorbedingung: keine.
    Nachbedingung: Die aufgeloesten Randpfade, durch Komma getrennt, oder
    ein ausdruecklicher Hinweis, dass keiner konfiguriert ist. Die Angabe
    gehoert in jede Ablehnung — eine Grenze, die man nicht nennt, kann
    niemand einhalten.
    """
    rand: list[Path] = _rand_aufloesen()
    if not rand:
        return "(keiner konfiguriert)"
    return ", ".join(str(pfad) for pfad in rand)


def dateizahl_text(befund: WurzelBefund) -> str:
    """Formuliert die Dateizahl fuer das Tor.

    Vorbedingung: `befund.ok` ist True.
    Nachbedingung: Ein Satzteil, der eine Untergrenze als Untergrenze
    ausweist — eine gekappte Zahl als Endzahl auszugeben waere genau die
    stille Kappung, gegen die die Zaehlgrenze gebaut ist.
    """
    if befund.gezaehlt_vollstaendig:
        return f"{befund.dateizahl} Dateien"
    return f"mindestens {befund.dateizahl} Dateien"
