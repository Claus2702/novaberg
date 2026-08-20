"""Der Zoom des lesenden Dienstes — Karte, Block, Nadel.

Spezifikation: docs/novaberg-agent-dateien_k.md §6.4.

**Die drei Stufen sind ein Zoom und keine Suche.** Sie beantworten nicht
*„welche Datei"* — das hat `suche.py` schon getan —, sondern *„wo in dieser
Datei"*. Jede Stufe kostet mehr als die vorige, und deshalb ist die
Reihenfolge Teil der Zusicherung:

| Stufe | Frage | Kosten |
|---|---|---|
| **Karte** | welche Abschnitte hat die Datei | **keiner** — die Karte steht im Index |
| **Block** | was steht in diesem Abschnitt | ein Dateizugriff, gefenstert |
| **Nadel** | wo steht dieser Satz | ein Dateizugriff, zeilenweise |

**Die Karte ist umsonst, und das ist der Grund für ihre Existenz.** Beim
Indizieren hat `struktur_analysieren` die Blockkarte einmal erhoben und in
`dateien_index.struktur` abgelegt; sie hier erneut zu erheben hieße, für eine
Antwort zu bezahlen, die schon in der Zeile steht.

**Kein Schreibpfad.** Dieses Modul importiert aus `tools/dateien/` genau die
lesenden Operationen — nicht `redaktion`, nicht `versionierung`. Ein Recht,
das nicht im Modul liegt, kann kein Prompt herbeireden (§7 Regel 2).
"""

import json
import logging
from pathlib import Path

from tools.dateien.operationen import block_lesen, datei_grep

logger = logging.getLogger("ki_server.agents.dateien.zoom")

#: Die drei Stufen als geschlossene Menge. Ein unbekannter Wert ist ein
#: Defekt und kein stiller Durchlauf.
STUFE_KARTE: str = "karte"
STUFE_BLOCK: str = "block"
STUFE_NADEL: str = "nadel"
STUFEN: frozenset[str] = frozenset({STUFE_KARTE, STUFE_BLOCK, STUFE_NADEL})


def karte_lesen(kandidat: dict) -> list[dict]:
    """Stufe 1 — die Blockkarte aus dem Index, ohne die Datei anzufassen.

    Vorbedingung: `kandidat` stammt aus `suche.py` und trägt `struktur`.
    Nachbedingung: Eine Liste von Blöcken; **leer, wenn die Zeile keine Karte
    trägt** — das ist eine Auskunft über den Index und kein Fehler des Zooms.
    Fehlerfaelle: Eine Karte, die sich nicht lesen lässt, wird laut gemeldet
    und als leer behandelt; sie stillschweigend zu übergehen hieße, eine
    fehlende Karte von einer kaputten nicht unterscheiden zu können.

    **Die leere Rückgabe hat drei Ursachen, und sie werden getrennt
    protokolliert** (20.08.2026). Seit der Index `NULL` schreibt, wenn die
    Gliederung nicht erhoben werden konnte, ist *„die Datei hat keine
    Überschriften"* nicht mehr dasselbe wie *„wir konnten nicht nachsehen"*.
    Der Rückgabewert kann beide nicht unterscheiden — der Zoom weicht in
    jedem Fall auf `zeilen_lesen` aus —, **das Protokoll muss es.** Sonst ist
    die Trennung genau an der Stelle wieder aufgehoben, an der jemand
    nachschaut, warum eine Datei keinen Zoom bekommt.

    **Kein Dateizugriff.** Wer hier die Datei öffnet, bezahlt für etwas, das
    beim Indizieren schon bezahlt wurde.
    """
    # ── Eingabe-Validierung ─────────────────────
    # `struktur IS NULL` heisst seit dem 20.08.2026 NICHT ERHOBEN und ist
    # damit ein Befund ueber unseren Erkenner, nicht ueber die Datei. Vorher
    # schrieb der Index in jedem Fall eine Liste, und `None` konnte nur eine
    # fehlende Spalte sein — deshalb stand hier `info`.
    if "struktur" not in kandidat:
        logger.error(
            "Zoom: Kandidat %s trägt das Feld 'struktur' nicht — die Abfrage in "
            "suche.py liefert es nicht mehr",
            kandidat.get("pfad"),
        )
        return []

    roh = kandidat["struktur"]
    if roh is None:
        logger.warning(
            "Zoom: Gliederung von %s wurde beim Indizieren NICHT ERHOBEN "
            "(Format ohne Erkenner oder defekte Auszeichnung) — Stufe 1 "
            "liefert nichts, und das ist kein Befund über die Datei",
            kandidat.get("pfad"),
        )
        return []

    # ── Verarbeitung ────────────────────────────
    # `jsonb` kommt je nach Treiber schon als Liste oder noch als Text.
    if isinstance(roh, str):
        try:
            roh = json.loads(roh)
        except json.JSONDecodeError:
            logger.exception(
                "Zoom: Blockkarte von %s ist kein lesbares JSON — als leer behandelt",
                kandidat.get("pfad"),
            )
            return []

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(roh, list):
        logger.error(
            "Zoom: Blockkarte von %s ist %s statt einer Liste — als leer behandelt",
            kandidat.get("pfad"), type(roh).__name__,
        )
        return []

    if not roh:
        logger.info(
            "Zoom: %s trägt eine erhobene, aber leere Karte — die Datei hat "
            "keine Überschriften; Stufe 1 liefert nichts",
            kandidat.get("pfad"),
        )
        return []

    logger.info("Zoom: Karte von %s → %d Blöcke", kandidat.get("pfad"), len(roh))
    return roh


def block_holen(kandidat: dict, header: str) -> dict | None:
    """Stufe 2 — ein Abschnitt der Datei, gefenstert.

    Vorbedingung: `kandidat` trägt `pfad` und `wurzel`; `header` ist die
    Überschrift eines Blocks aus der Karte.
    Nachbedingung: Das Ergebnis der Operation samt `inhalt` — oder None, wenn
    der Header unbekannt oder mehrdeutig ist.
    Fehlerfaelle: **Ein mehrdeutiger Header ist ein Fehler und kein Griff zum
    ersten Treffer** — die Werkzeugschicht wirft, und dieses Modul reicht die
    Meldung weiter, statt sie zu einer Auswahl zu machen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not header.strip():
        logger.error("Zoom: leerer Header — kein Blockzugriff")
        return None

    pfad, wurzel = _ort(kandidat)
    if pfad is None:
        return None

    # ── Verarbeitung ────────────────────────────
    try:
        ergebnis: dict = block_lesen(pfad, wurzel, header.strip())
    except (ValueError, OSError) as fehler:
        logger.warning(
            "Zoom: Block '%s' in %s nicht lesbar (%s: %s)",
            header.strip(), pfad, type(fehler).__name__, fehler,
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    if not ergebnis.get("inhalt", "").strip():
        logger.warning(
            "Zoom: Block '%s' in %s ist leer — als kein Treffer behandelt",
            header.strip(), pfad,
        )
        return None

    logger.info(
        "Zoom: Block '%s' aus %s → %s Zeilen, Rest %s",
        header.strip(), pfad, ergebnis.get("block_zeilen"), ergebnis.get("rest"),
    )
    return ergebnis


def nadel_suchen(kandidat: dict, suchbegriff: str) -> dict | None:
    """Stufe 3 — die Fundstelle mit Zeilennummer.

    Vorbedingung: `kandidat` trägt `pfad` und `wurzel`; `suchbegriff` ist
    nicht leer.
    Nachbedingung: Das Ergebnis samt `treffer`, `anzahl` und `gekappt` — oder
    None, wenn die Datei nicht lesbar ist. **Null Treffer sind kein None**:
    „nichts gefunden" und „nicht nachgesehen" sind zwei verschiedene
    Auskünfte, und der Aufrufer muss sie unterscheiden können.
    Fehlerfaelle: unlesbare Datei, ungültiges Muster — gemeldet, None.

    **Die Kappung wird weitergereicht, nicht verschluckt.** Eine
    stillschweigend gekürzte Trefferliste ist von einer vollständigen nicht
    zu unterscheiden, und der Mensch schließt aus ihr auf den Bestand.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not suchbegriff.strip():
        logger.error("Zoom: leerer Suchbegriff — keine Nadelsuche")
        return None

    pfad, wurzel = _ort(kandidat)
    if pfad is None:
        return None

    # ── Verarbeitung ────────────────────────────
    try:
        ergebnis: dict = datei_grep(pfad, wurzel, suchbegriff.strip())
    except (ValueError, OSError) as fehler:
        logger.warning(
            "Zoom: Nadelsuche in %s fehlgeschlagen (%s: %s)",
            pfad, type(fehler).__name__, fehler,
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        "Zoom: Nadel '%s' in %s → %s Treffer%s",
        suchbegriff.strip(), pfad, ergebnis.get("anzahl"),
        " (gekappt)" if ergebnis.get("gekappt") else "",
    )
    return ergebnis


def _ort(kandidat: dict) -> tuple[Path | None, Path | None]:
    """Bestimmt den absoluten Dateipfad und seine Wurzel.

    Vorbedingung: `kandidat` stammt aus `suche.py`.
    Nachbedingung: Beide Pfade — oder zweimal None mit Fehlermeldung.

    **Der Pfad im Index ist relativ zur Wurzel** (§4). Er wird hier
    zusammengesetzt und **nicht** aufgelöst: Die Auflösung samt Randprüfung
    ist Sache der Werkzeugschicht, die sie bei jedem Zugriff erzwingt. Wer
    hier schon auflöst, hat zwei Prüfungen an zwei Orten und weiß beim
    nächsten Defekt nicht mehr, welche gegriffen hat.
    """
    # ── Eingabe-Validierung ─────────────────────
    pfad_relativ: str = (kandidat.get("pfad") or "").strip()
    wurzel_text:  str = (kandidat.get("wurzel") or "").strip()
    if not pfad_relativ or not wurzel_text:
        logger.error(
            "Zoom: Kandidat ohne Ort (pfad=%r, wurzel=%r) — kein Dateizugriff",
            pfad_relativ, wurzel_text,
        )
        return None, None

    # ── Ausgabe ─────────────────────────────────
    wurzel = Path(wurzel_text)
    return wurzel / pfad_relativ, wurzel
