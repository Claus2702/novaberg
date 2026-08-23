"""Das Etikett einer Fundstelle — was ein Pfad ueber die Geltung sagt.

Spezifikation: docs/novaberg-agent-dateien_k.md §5.6.

**Kein Lesezugriff, kein Schreibzugriff.** Dieses Modul sieht nur den
relativen Pfad an; es oeffnet keine Datei und fragt keine Datenbank.

**Deshalb `utils/` und nicht `tools/dateien/`.** Der erste Entwurf legte es
neben die Dateiwerkzeuge, weil es von Dateien handelt — aber `tools/` ist
die Infrastrukturschicht, und ein Geschaeftsablauf darf sie nicht
importieren (`15_ARCHITEKTUR` §1). Die Wand vor dem Commit hat den Uebertritt
abgewiesen, und sie hatte recht: Was hier steht, ist eine Zeichenketten-
Regel ohne Zugriff auf irgendetwas. Der Gegenstand, von dem eine Funktion
handelt, bestimmt nicht ihre Schicht — ihr Zugriff tut es.

**Warum eine eigene Stelle.** Zwei Ausgabewege nennen dieselbe Datei —
`agents/dateien_index/aufzeichnungen.py` fuer den Enricher und
`agents/dateien/auskunft.py` fuer den lesenden Dienst. Beide bauen ihre
Herkunftsangabe selbst. Eine Regel, die an zwei Stellen getippt wird,
laeuft auseinander, ohne dass etwas rot wird — und die Haelfte, die das
Etikett verliert, ist genau die, die eine archivierte Datei als geltende
ausgibt.
"""

import logging
from pathlib import PurePosixPath

logger = logging.getLogger("ki_server.utils.etikett")

#: Die Verzeichnisnamen, die einen Bestand als abgelegt kennzeichnen.
#: Sie stehen hier und nicht in `config.py`, weil sie keine Einstellung sind,
#: sondern eine Ablagekonvention: `docs/archive/`.
#:
#: **Zwei Schreibungen und ohne Ansehen der Gross-/Kleinschreibung**, und der
#: Grund ist der Bestand: `/docs` folgt der englischen Konvention des
#: Repositoriums, aber die Freigaben 1 und 3 sind der Dateibaum eines
#: Menschen und der einer Figur. Dort ist `Archiv` die wahrscheinlichere
#: Benennung, und ein Verzeichnis, das so heisst, ist eines.
ARCHIV_VERZEICHNISSE: frozenset[str] = frozenset({"archive", "archiv"})

#: Was an einer Fundstelle steht, deren Datei archiviert ist. **In der
#: Sprache der Ausgabe** (`12_NAMENSGEBUNG` §1): Der Text erreicht das
#: Sprachmodell und ueber es den Menschen.
ETIKETT_ARCHIVIERT: str = "archiviert"


def ist_archiviert(pfad: str) -> bool:
    """Sagt, ob ein relativer Pfad unterhalb eines Archivverzeichnisses liegt.

    Vorbedingung: `pfad` ist relativ zur Wurzel, wie er im Index steht.
    Nachbedingung: True, wenn **ein Verzeichnisglied** `archive` heisst.

    **Geprueft wird das Glied, nicht der Anfang.** Ein `startswith("archive/")`
    fande nur die oberste Ebene und liesse `konzepte/archive/alt.md` durch;
    ein `"archive" in pfad` traefe dagegen `archivelogik_k.md`. Der Pfad wird
    deshalb zerlegt.

    Die Datei selbst zaehlt nicht als Glied: `archive.md` ist ein Dokument
    ueber Archive, kein archiviertes.

    **Verglichen wird kleingeschrieben.** `Archiv/` und `ARCHIVE/` sind
    dasselbe Verzeichnis wie `archive/`; wer die Schreibung mitpruefte,
    liesse den Bestand entscheiden, was das Etikett bekommt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not pfad or not pfad.strip():
        logger.error(
            "Etikett: leerer Pfad — die Geltung einer namenlosen Datei ist "
            "nicht bestimmbar, sie gilt als nicht archiviert",
        )
        return False

    # ── Verarbeitung ────────────────────────────
    glieder: tuple[str, ...] = PurePosixPath(pfad.strip()).parts
    # Das letzte Glied ist der Dateiname und wird ausgenommen.
    return any(glied.lower() in ARCHIV_VERZEICHNISSE for glied in glieder[:-1])


def etikett(pfad: str) -> str:
    """Das Etikett einer Datei, oder ein leerer Text.

    Vorbedingung: `pfad` ist relativ zur Wurzel.
    Nachbedingung: `ETIKETT_ARCHIVIERT` oder `""`. Der leere Text ist eine
    Aussage: **die Datei gilt.**
    """
    return ETIKETT_ARCHIVIERT if ist_archiviert(pfad) else ""


def mit_etikett(fundstelle: str, pfad: str) -> str:
    """Haengt das Etikett an eine fertige Herkunftsangabe.

    Vorbedingung: `fundstelle` ist der Ort, wie ein Mensch ihn nennt;
    `pfad` ist derselbe Pfad relativ zur Wurzel.
    Nachbedingung: Die Fundstelle, bei einer archivierten Datei gefolgt von
    ihrem Etikett in Klammern. Sonst unveraendert.

    **Das Etikett steht an der Fundstelle und nicht im Thema.** Wer den
    Auszug liest, hat den Ort schon gelesen; wer nur den Ort zitiert, traegt
    die Einschraenkung mit.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not fundstelle.strip():
        logger.error(
            "Etikett: leere Fundstelle zu Pfad %r — es gibt nichts zu "
            "etikettieren", pfad,
        )
        return fundstelle

    # ── Verarbeitung ────────────────────────────
    marke: str = etikett(pfad)
    return f"{fundstelle} ({marke})" if marke else fundstelle
