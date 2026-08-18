"""Schreibschicht des Dateizugriffs — die chirurgischen Schnitte.

Ergaenzt `schreiben.py`, das eine Datei nur als Ganzes kennt. Hier stehen die
Eingriffe, die einen Teil aendern und den Rest unberuehrt lassen.

Der Grund ist nicht Bequemlichkeit. Wer eine Datei erweitern will und nur
`datei_schreiben` hat, muss sie vollstaendig durch das Modell schicken und
neu erzeugen — und eine Neuerzeugung, die einen Absatz fallen laesst, sieht
aus wie eine Neuerzeugung. **Auf dem Inhalt einer Wissensdatei steht kein
Zeuge**, also faellt der Verlust niemandem auf.

Drei Zusicherungen, die dieses Modul traegt:

**Ein mehrdeutiger Anker ist ein Fehler, kein Griff zum ersten Treffer.**
`str_ersetzen` prueft die Eindeutigkeit und scheitert laut mit der Zahl der
Vorkommen, damit der Aufrufer mit mehr Kontext erneut ansetzen kann. Das ist
dieselbe Bauart wie bei SWE-agent und Aider und der Grund, warum das Format
ueberhaupt taugt.
`[gemessen]` — 17.08.2026: 30 von 30 Auftraegen an `gemma4-gpu` lieferten
einen zeichengenauen, eindeutigen Anker (Median 1,7 s); an `qwen36-cpu`
ebenfalls 30 von 30 (Median 17,9 s). Die Ankertreue ist keine Annahme.

**Jeder Eingriff verifiziert sein Ergebnis am neu gelesenen Text.** Ein
gelungener Schreibaufruf ist nicht dasselbe wie eine geaenderte Datei.

**Geschrieben wird ausschliesslich innerhalb der uebergebenen Wurzel**, und
die Wurzel ist ein Pflichtargument ohne Vorgabewert. Freigegebene
Fremdverzeichnisse werden nie beschrieben; die Trennung haengt an der Zone,
nicht am Aufrufer (docs/novaberg-agent-dateien_k.md §3a.3).
"""

import logging
from pathlib import Path

from tools.dateien.operationen import pfad_pruefen, struktur_analysieren

logger = logging.getLogger("ki_server.tools.dateien.redaktion")


def _schreiben_zurueck(ziel: Path, zeilen: list[str], urspruenglich: str) -> int:
    """Schreibt Zeilen zurueck und verifiziert das Ergebnis am gelesenen Text.

    Erhaelt das abschliessende Zeilenende, wenn die Vorlage eines hatte —
    sonst wandert bei jedem Eingriff ein Byte aus der Datei, und nach
    zwanzig Schnitten fehlt der Zeilenumbruch, den ein Werkzeug erwartet.
    """
    neu: str = "\n".join(zeilen)
    if urspruenglich.endswith("\n"):
        neu += "\n"

    ziel.write_text(neu, encoding="utf-8")

    # ── Ausgabe-Verifikation ────────────────────
    gelesen: str = ziel.read_text(encoding="utf-8")
    if gelesen != neu:
        meldung: str = (
            f"_schreiben_zurueck: {ziel} traegt nach dem Schreiben "
            f"{len(gelesen)} Zeichen, geschrieben wurden {len(neu)}"
        )
        raise RuntimeError(meldung)

    return len(neu)


def _block_grenzen(pfad: Path, wurzel: Path | str, header: str) -> dict:
    """Findet genau einen Block; scheitert bei keinem und bei mehreren."""
    bloecke: list[dict] = struktur_analysieren(pfad, wurzel)
    gesucht: str = header.strip()
    passende: list[dict] = [b for b in bloecke if b["header"].strip() == gesucht]

    if not passende:
        vorhanden: str = ", ".join(b["header"].strip() for b in bloecke) or "keine"
        meldung: str = (
            f"_block_grenzen: Header {gesucht!r} nicht in {pfad} — "
            f"vorhandene Bloecke: {vorhanden}"
        )
        raise ValueError(meldung)

    if len(passende) > 1:
        stellen: str = ", ".join(str(b["start"]) for b in passende)
        meldung = (
            f"_block_grenzen: Header {gesucht!r} kommt in {pfad} "
            f"{len(passende)}-mal vor (Zeilen {stellen}) — kein Eingriff"
        )
        raise ValueError(meldung)

    return passende[0]


def block_ersetzen(
    pfad:   Path | str,
    wurzel: Path | str,
    header: str,
    inhalt: str,
) -> int:
    """Ersetzt den Rumpf eines Blocks; die Ueberschrift bleibt stehen.

    Vorbedingung: `pfad` liegt in der Wurzel, `header` bezeichnet genau einen
    Block, `inhalt` ist nicht leer.
    Nachbedingung: Der Block traegt den neuen Rumpf, die Zahl der Bloecke ist
    unveraendert, und der Rest der Datei ist Zeichen fuer Zeichen derselbe.
    Fehlerfaelle: unbekannter oder mehrdeutiger Header, leerer Inhalt
    (ValueError); abweichendes Ergebnis nach dem Schreiben (RuntimeError).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not inhalt.strip():
        meldung: str = f"block_ersetzen: leerer Inhalt fuer {header!r} in {pfad}"
        raise ValueError(meldung)

    ziel: Path = pfad_pruefen(pfad, wurzel)
    roh: str = ziel.read_text(encoding="utf-8")
    zeilen: list[str] = roh.splitlines()
    block: dict = _block_grenzen(ziel, wurzel, header)
    vorher_bloecke: int = len(struktur_analysieren(ziel, wurzel))

    # ── Verarbeitung ────────────────────────────
    neu: list[str] = (
        zeilen[:block["start"]]
        + inhalt.splitlines()
        + zeilen[block["ende"]:]
    )
    groesse: int = _schreiben_zurueck(ziel, neu, roh)

    # ── Ausgabe-Verifikation ────────────────────
    nachher_bloecke: int = len(struktur_analysieren(ziel, wurzel))
    if nachher_bloecke != vorher_bloecke:
        meldung = (
            f"block_ersetzen: {pfad} hatte {vorher_bloecke} Bloecke und hat "
            f"jetzt {nachher_bloecke} — der neue Inhalt trug eine Ueberschrift"
        )
        raise RuntimeError(meldung)

    logger.info(f"block_ersetzen: {ziel} — {header!r} ersetzt, {groesse} Zeichen")
    return groesse


def block_anfuegen(
    pfad:   Path | str,
    wurzel: Path | str,
    header: str,
    zusatz: str,
) -> int:
    """Haengt Text an das Ende eines bestehenden Blocks an.

    Vorbedingung: wie `block_ersetzen`.
    Nachbedingung: Der bisherige Rumpf steht unveraendert am Anfang des
    Blocks, der Zusatz dahinter.
    Fehlerfaelle: wie `block_ersetzen`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not zusatz.strip():
        meldung: str = f"block_anfuegen: leerer Zusatz fuer {header!r} in {pfad}"
        raise ValueError(meldung)

    ziel: Path = pfad_pruefen(pfad, wurzel)
    roh: str = ziel.read_text(encoding="utf-8")
    zeilen: list[str] = roh.splitlines()
    block: dict = _block_grenzen(ziel, wurzel, header)

    # ── Verarbeitung ────────────────────────────
    rumpf: list[str] = zeilen[block["start"]:block["ende"]]
    # Genau eine Leerzeile zwischen Bestand und Zusatz — Markdown trennt
    # Absaetze so, und ein Anhaengen ohne Trenner verschmilzt zwei Absaetze
    # zu einem, ohne dass es im Rohtext auffiele.
    while rumpf and not rumpf[-1].strip():
        rumpf.pop()
    erweitert: list[str] = rumpf + ["", *zusatz.splitlines()]

    neu: list[str] = zeilen[:block["start"]] + erweitert + zeilen[block["ende"]:]
    groesse: int = _schreiben_zurueck(ziel, neu, roh)

    # ── Ausgabe-Verifikation ────────────────────
    gelesen: str = ziel.read_text(encoding="utf-8")
    if zusatz.strip().splitlines()[0] not in gelesen:
        meldung = f"block_anfuegen: Zusatz steht nach dem Schreiben nicht in {ziel}"
        raise RuntimeError(meldung)

    logger.info(f"block_anfuegen: {ziel} — an {header!r} angehaengt, {groesse} Zeichen")
    return groesse


def block_einfuegen(
    pfad:        Path | str,
    wurzel:      Path | str,
    neuer_header: str,
    inhalt:      str,
    vor_header:  str | None = None,
) -> int:
    """Fuegt einen neuen Block ein; `vor_header=None` haengt ihn ans Dateiende.

    Vorbedingung: `neuer_header` beginnt mit mindestens einem `#` und kommt in
    der Datei noch nicht vor; `vor_header` bezeichnet, falls gesetzt, genau
    einen bestehenden Block.
    Nachbedingung: Die Datei traegt einen Block mehr, und der neue steht an
    der verlangten Stelle.
    Fehlerfaelle: Header ohne `#`, bereits vorhandener Header, unbekannter
    `vor_header` (ValueError).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not neuer_header.strip().startswith("#"):
        meldung: str = (
            f"block_einfuegen: {neuer_header!r} ist keine Ueberschrift — "
            f"fuehrendes '#' fehlt"
        )
        raise ValueError(meldung)
    if not inhalt.strip():
        meldung = f"block_einfuegen: leerer Inhalt fuer {neuer_header!r}"
        raise ValueError(meldung)

    ziel: Path = pfad_pruefen(pfad, wurzel)
    roh: str = ziel.read_text(encoding="utf-8")
    zeilen: list[str] = roh.splitlines()
    vorhanden: list[dict] = struktur_analysieren(ziel, wurzel)

    if any(b["header"].strip() == neuer_header.strip() for b in vorhanden):
        meldung = (
            f"block_einfuegen: {neuer_header!r} steht bereits in {pfad} — "
            f"ein zweiter gleichnamiger Block macht jeden spaeteren Zugriff "
            f"mehrdeutig"
        )
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    neuer_block: list[str] = [neuer_header.strip(), "", *inhalt.splitlines(), ""]

    if vor_header is None:
        stelle: int = len(zeilen)
    else:
        stelle = _block_grenzen(ziel, wurzel, vor_header)["start"] - 1

    neu: list[str] = zeilen[:stelle] + neuer_block + zeilen[stelle:]
    groesse: int = _schreiben_zurueck(ziel, neu, roh)

    # ── Ausgabe-Verifikation ────────────────────
    nachher: list[dict] = struktur_analysieren(ziel, wurzel)
    if len(nachher) != len(vorhanden) + 1:
        meldung = (
            f"block_einfuegen: {pfad} hatte {len(vorhanden)} Bloecke und hat "
            f"jetzt {len(nachher)} — erwartet waren {len(vorhanden) + 1}"
        )
        raise RuntimeError(meldung)

    logger.info(f"block_einfuegen: {ziel} — {neuer_header!r} eingefuegt, {groesse} Zeichen")
    return groesse


def str_ersetzen(
    pfad:    Path | str,
    wurzel:  Path | str,
    alt:     str,
    neu:     str,
    header:  str | None = None,
) -> dict:
    """Ersetzt eine Zeichenkette; prueft die Eindeutigkeit im Suchraum.

    `header=None` sucht in der ganzen Datei, sonst nur innerhalb des Blocks.
    Gemessen am 17.08.2026 ist der Suchraum bei den heutigen Wissensdateien
    ohnehin die ganze Datei — 223 von 223 tragen keine Bloecke.

    Vorbedingung: `alt` ist nicht leer und unterscheidet sich von `neu`.
    Nachbedingung: Bei Erfolg kommt `alt` im Suchraum nicht mehr und `neu`
    genau einmal vor.
    Fehlerfaelle: leerer oder unveraenderter Anker (ValueError). Ein nicht
    oder mehrfach gefundener Anker ist **kein** Ausnahmefall, sondern ein
    Ergebnis — er kommt als `{"erfolg": False, ...}` zurueck, damit der
    Aufrufer mit mehr Kontext erneut ansetzen kann.

    Returns:
        {"erfolg": True, "zeichen": int} oder
        {"erfolg": False, "grund": "nicht_gefunden" | "nicht_eindeutig",
         "anzahl": int, "hinweis": str}
    """
    # ── Eingabe-Validierung ─────────────────────
    if not alt:
        meldung: str = f"str_ersetzen: leerer Anker fuer {pfad}"
        raise ValueError(meldung)
    if alt == neu:
        meldung = f"str_ersetzen: Anker und Ersatz sind gleich ({pfad})"
        raise ValueError(meldung)

    ziel: Path = pfad_pruefen(pfad, wurzel)
    roh: str = ziel.read_text(encoding="utf-8")
    zeilen: list[str] = roh.splitlines()

    if header is None:
        von, bis = 0, len(zeilen)
    else:
        block: dict = _block_grenzen(ziel, wurzel, header)
        von, bis = block["start"], block["ende"]

    raum: str = "\n".join(zeilen[von:bis])

    # ── Verarbeitung ────────────────────────────
    anzahl: int = raum.count(alt)

    if anzahl == 0:
        logger.info(
            f"str_ersetzen: Anker nicht in {ziel} gefunden "
            f"(Suchraum {'ganze Datei' if header is None else header!r})"
        )
        return {
            "erfolg": False,
            "grund":  "nicht_gefunden",
            "anzahl": 0,
            "hinweis": (
                "Der Anker steht so nicht im Text. Zeichengenau kopieren, "
                "einschliesslich Anfuehrungszeichen und Gedankenstrichen."
            ),
        }

    if anzahl > 1:
        logger.info(f"str_ersetzen: Anker {anzahl}-mal in {ziel} — kein Eingriff")
        return {
            "erfolg": False,
            "grund":  "nicht_eindeutig",
            "anzahl": anzahl,
            "hinweis": (
                f"Der Anker kommt {anzahl}-mal vor. Mehr Kontext mitgeben — "
                f"eine Zeile davor oder danach genuegt meist."
            ),
        }

    ersetzt: str = raum.replace(alt, neu, 1)
    ganz: list[str] = zeilen[:von] + ersetzt.split("\n") + zeilen[bis:]
    groesse: int = _schreiben_zurueck(ziel, ganz, roh)

    # ── Ausgabe-Verifikation ────────────────────
    gelesen: str = ziel.read_text(encoding="utf-8")
    if alt in gelesen and header is None:
        meldung = f"str_ersetzen: Anker steht nach dem Eingriff noch in {ziel}"
        raise RuntimeError(meldung)
    if neu not in gelesen:
        meldung = f"str_ersetzen: Ersatz steht nach dem Eingriff nicht in {ziel}"
        raise RuntimeError(meldung)

    logger.info(f"str_ersetzen: {ziel} — ein Vorkommen ersetzt, {groesse} Zeichen")
    return {"erfolg": True, "zeichen": groesse}


def metadaten_setzen(
    pfad:   Path | str,
    wurzel: Path | str,
    feld:   str,
    wert:   str,
) -> int:
    """Setzt ein Feld im Metadatenkopf; legt es an, wenn es fehlt.

    Vorbedingung: `feld` und `wert` sind nicht leer.
    Nachbedingung: Der Kopf traegt genau eine Zeile `**<feld>:** <wert>`.
    Fehlerfaelle: leeres Feld oder leerer Wert (ValueError); fehlende Zeile
    nach dem Schreiben (RuntimeError).

    Ein neues Feld wird hinter das letzte vorhandene gesetzt, sonst hinter
    die Titelzeile — nie ans Dateiende, wo es kein Kopf mehr waere.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not feld.strip() or not wert.strip():
        meldung: str = (
            f"metadaten_setzen: leeres Feld oder leerer Wert fuer {pfad} — "
            f"{feld!r}: {wert!r}"
        )
        raise ValueError(meldung)

    ziel: Path = pfad_pruefen(pfad, wurzel)
    roh: str = ziel.read_text(encoding="utf-8")
    zeilen: list[str] = roh.splitlines()
    marke: str = f"**{feld.strip()}:**"
    neue_zeile: str = f"{marke} {wert.strip()}"

    # ── Verarbeitung ────────────────────────────
    ersetzt: bool = False
    letzte_meta: int = 0
    for i, zeile in enumerate(zeilen):
        if zeile.strip().startswith("---"):
            break
        if zeile.strip().startswith("**") and ":**" in zeile:
            letzte_meta = i
            if zeile.strip().startswith(marke):
                zeilen[i] = neue_zeile
                ersetzt = True
                break

    if not ersetzt:
        zeilen.insert(letzte_meta + 1, neue_zeile)

    groesse: int = _schreiben_zurueck(ziel, zeilen, roh)

    # ── Ausgabe-Verifikation ────────────────────
    if neue_zeile not in ziel.read_text(encoding="utf-8"):
        meldung = f"metadaten_setzen: {neue_zeile!r} steht nach dem Schreiben nicht in {ziel}"
        raise RuntimeError(meldung)

    logger.info(f"metadaten_setzen: {ziel} — {feld!r} = {wert!r}")
    return groesse
