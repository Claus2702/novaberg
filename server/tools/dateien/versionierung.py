"""Versionierung im Dokument — Marken im Text, Ruempfe am Ende.

Ein Wissenstext, der ueber Monate waechst, ist ein Verlauf und kein Zustand.
Ein Ersetzen ist endgueltig: Was ueberschrieben wird, ist weg. Die Vorbilder
aus der Werkzeugliteratur brauchen dafuer nichts, weil sie in einem
Repositorium arbeiten — hier gibt es keins.

Drei Marken, und die Pfeilrichtung sagt, wo man ist:

    [cN>]   Change  — der Absatz wurde geaendert; unten steht der Absatz davor
    [dN>]   Delete  — der Absatz wurde entfernt; unten steht der entfernte
    [iN>]   Insert  — der Absatz kam hinzu; unten steht nichts

Der Eintrag traegt `[<TypNummer_Version_Datum]` und keine Leerzeichen: Eine
Marke, die an einem Leerzeichen zerfaellt, ist nach einem Zeilenumbruch nicht
mehr sicher zu finden.

Drei Zusicherungen, die dieses Modul traegt:

**Archiveintraege sind gewoehnlicher Text und duerfen Marken tragen.** Daraus
entsteht die Kette: Ein Absatz, der geaendert und spaeter geloescht wurde,
haelt beide Vorgaenge, und der Loescheintrag enthaelt die Aenderungsmarke.

**Die Position sagt, ob eine Fassung lebt.** Steht eine Marke im laufenden
Text, ist sie die geltende Fassung; steht dieselbe Marke innerhalb eines
Archiveintrags, gehoert sie zu einer abgeloesten. Es braucht kein
Gueltigkeitsfeld — die Marke steht dort, wo ihr Text steht.

**Jede Marke hat genau einen Eintrag und umgekehrt.** Das ist eine Invariante
ueber eine einzelne Datei, ohne Modell und ohne Kontext pruefbar — und der
erste Detektor, den dieser Bereich ueberhaupt bekommt. Eine vergessene
Markierung in Prosa faellt niemandem auf; eine gerissene Paarung sieht ein
Script sofort.
"""

import logging
import re
from datetime import date
from pathlib import Path
from typing import NamedTuple

from tools.dateien.operationen import pfad_pruefen

logger = logging.getLogger("ki_server.tools.dateien.versionierung")

# Die beiden tragenden Bloecke. Sie sind ein **Paar**: Jeder sagt, was der
# andere ist. "HISTORIE" allein liesse offen, ob alles Uebrige aktuell ist
# oder nur nicht einsortiert; mit "AKTUELL" daneben ist die Trennung im
# Dokument selbst ausgesprochen und nicht bloss Konvention.
#
# Der Gewinn liegt beim **Lesen**: Der lebende Text hat damit eine Adresse.
# `block_lesen(pfad, LEBENDBLOCK)` liefert genau ihn, und die Historie wird
# nie geladen, solange niemand nach ihr fragt.
LEBENDBLOCK: str = "## AKTUELL"
ARCHIVBLOCK: str = "## HISTORIE"

TYPEN: tuple[str, ...] = ("c", "d", "i")


class Fassung(NamedTuple):
    """Version und Datum eines Eingriffs — sie reisen immer zusammen.

    Die Version ist die, in der die Aenderung geschah, **nicht** die des
    archivierten Textes. Ohne diese Festlegung ist bei jeder Rekonstruktion
    offen, ob eine Zahl den Zustand vorher oder nachher benennt.
    """

    version: str
    datum:   str | None = None


_MARKE: re.Pattern = re.compile(r"\[([cdi])(\d+)>\]")
_EINTRAG: re.Pattern = re.compile(
    r"^\[<([cdi])(\d+)_(?P<version>[^\s_\]]+)_(?P<datum>\d{4}-\d{2}-\d{2})\]$"
)


def marken_finden(text: str) -> list[tuple[str, int]]:
    """Findet alle Marken der Form `[cN>]` in einem Text.

    Returns:
        Liste aus (Typ, Nummer) in Reihenfolge des Auftretens.
    """
    return [(t, int(n)) for t, n in _MARKE.findall(text)]


def aktuell_lesen(pfad: Path | str, wurzel: Path | str) -> str:
    """Liefert den lebenden Teil einer Datei — alles vor der Historie.

    Vorbedingung: `pfad` liegt in der Wurzel.
    Nachbedingung: Der Text ohne Historienblock, ohne abschliessende
    Leerzeilen.
    Fehlerfaelle: verletzte Wurzelpruefung (ValueError).

    Das ist der Zugriff, den ein Leser fast immer will: was gilt, nicht was
    galt. Er kostet keinen Umweg ueber die Karte und funktioniert auch bei
    Dateien ohne Historienblock — dann ist der lebende Teil die ganze Datei.
    """
    # ── Eingabe-Validierung ─────────────────────
    _, _, zeilen = _laden(pfad, wurzel)

    # ── Verarbeitung ────────────────────────────
    text, _ = _teilen(zeilen)
    while text and not text[-1].strip():
        text.pop()

    # ── Ausgabe-Verifikation ────────────────────
    if ARCHIVBLOCK in "\n".join(text):
        meldung: str = (
            f"aktuell_lesen: {pfad} traegt die Historienueberschrift noch im "
            f"lebenden Teil — die Trennung hat nicht gegriffen"
        )
        raise RuntimeError(meldung)

    return "\n".join(text)


def _teilen(zeilen: list[str]) -> tuple[list[str], list[str]]:
    """Trennt laufenden Text und Archivblock.

    Returns:
        (Zeilen vor dem Archivblock, Zeilen ab der Archivueberschrift).
    """
    for i, zeile in enumerate(zeilen):
        if zeile.strip() == ARCHIVBLOCK:
            return zeilen[:i], zeilen[i:]
    return zeilen, []


def _naechste_nummer(zeilen: list[str]) -> int:
    """Ermittelt die naechste freie Nummer — je Datei, nicht je Block.

    Der Zaehler laeuft ueber die ganze Datei, sonst kollidieren `[c1>]` aus
    zwei Bloecken im Archivteil.
    """
    ganz: str = "\n".join(zeilen)
    benutzt: list[int] = [n for _, n in marken_finden(ganz)]
    benutzt += [int(m.group(2)) for m in _EINTRAG.finditer(ganz) if m]
    for zeile in zeilen:
        passung = _EINTRAG.match(zeile.strip())
        if passung:
            benutzt.append(int(passung.group(2)))
    return max(benutzt, default=0) + 1


def _eintrag_kopf(typ: str, nummer: int, version: str, datum: str) -> str:
    """Baut die Kopfzeile eines Archiveintrags."""
    return f"[<{typ}{nummer}_{version}_{datum}]"


def _archiv_einfuegen(
    archiv:  list[str],
    kopf:    str,
    rumpf:   list[str],
) -> list[str]:
    """Setzt einen Eintrag an den Anfang des Archivblocks.

    Der juengste Eintrag steht oben: Wer wissen will, was zuletzt geschah,
    liest die erste Zeile des Blocks und nicht die letzte.
    """
    if not archiv:
        archiv = [ARCHIVBLOCK, ""]
    neu: list[str] = [kopf, *rumpf, ""]
    # archiv[0] ist die Ueberschrift, archiv[1] die Leerzeile darunter.
    return [archiv[0], "", *neu, *archiv[2:]]


def _zusammenfuegen(text: list[str], archiv: list[str]) -> list[str]:
    """Setzt laufenden Text und Archivblock mit genau einer Leerzeile zusammen.

    Ohne sie stuende die Archivueberschrift unmittelbar unter dem letzten
    Absatz. Markdown verlangt die Leerzeile zwischen Absatz und Ueberschrift,
    und ohne sie liest ein Parser die Ueberschrift als Teil des Absatzes —
    dann faende `struktur_analysieren` den Archivblock nicht mehr, und der
    Verlauf waere unerreichbar.
    """
    if not archiv:
        return text
    gekuerzt: list[str] = list(text)
    while gekuerzt and not gekuerzt[-1].strip():
        gekuerzt.pop()
    return [*gekuerzt, "", *archiv]


def _laden(pfad: Path | str, wurzel: Path | str) -> tuple[Path, str, list[str]]:
    """Liest eine geprueft Datei und gibt Pfad, Rohtext und Zeilen zurueck."""
    ziel: Path = pfad_pruefen(pfad, wurzel)
    roh: str = ziel.read_text(encoding="utf-8")
    return ziel, roh, roh.splitlines()


def _sichern(ziel: Path, zeilen: list[str], roh: str) -> int:
    """Schreibt zurueck und verifiziert am neu gelesenen Text."""
    neu: str = "\n".join(zeilen)
    if roh.endswith("\n"):
        neu += "\n"
    ziel.write_text(neu, encoding="utf-8")
    gelesen: str = ziel.read_text(encoding="utf-8")
    if gelesen != neu:
        meldung: str = (
            f"_sichern: {ziel} traegt {len(gelesen)} Zeichen, "
            f"geschrieben wurden {len(neu)}"
        )
        raise RuntimeError(meldung)
    return len(neu)


def _pruefen_gemeinsam(absatz: str, fassung: Fassung) -> str:
    """Prueft die Angaben, die alle drei Vorgaenge teilen; gibt das Datum zurueck."""
    if not absatz.strip():
        meldung: str = "versionierung: leerer Absatz uebergeben"
        raise ValueError(meldung)
    if not fassung.version.strip():
        meldung = "versionierung: leere Version uebergeben"
        raise ValueError(meldung)
    gesetzt: str = fassung.datum or date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", gesetzt):
        meldung = f"versionierung: Datum {gesetzt!r} ist nicht ISO-formatiert"
        raise ValueError(meldung)
    return gesetzt


def absatz_aendern(
    pfad:    Path | str,
    wurzel:  Path | str,
    alt:     str,
    neu:     str,
    fassung: Fassung,
) -> dict:
    """Aendert einen Absatz und legt seinen bisherigen Wortlaut ins Archiv.

    Vorbedingung: `alt` kommt im laufenden Text **genau einmal** vor; `neu`
    ist nicht leer und unterscheidet sich von `alt`.
    Nachbedingung: Der laufende Text traegt `neu` samt Marke `[cN>]`, das
    Archiv einen Eintrag `[<cN_...]` mit dem alten Wortlaut, und die Paarung
    ist vollstaendig.
    Fehlerfaelle: leere Angaben, unveraenderter Absatz (ValueError). Ein
    nicht oder mehrfach gefundener Absatz ist ein **Ergebnis**, kein
    Ausnahmefall — mit `erfolg=False` und einem Hinweis zurueck.
    """
    # ── Eingabe-Validierung ─────────────────────
    gesetzt: str = _pruefen_gemeinsam(alt, fassung)
    if not neu.strip():
        meldung: str = "absatz_aendern: leerer neuer Absatz"
        raise ValueError(meldung)
    if alt == neu:
        meldung = "absatz_aendern: alter und neuer Absatz sind gleich"
        raise ValueError(meldung)

    ziel, roh, zeilen = _laden(pfad, wurzel)
    text, archiv = _teilen(zeilen)
    laufend: str = "\n".join(text)

    anzahl: int = laufend.count(alt)
    if anzahl != 1:
        grund: str = "nicht_gefunden" if anzahl == 0 else "nicht_eindeutig"
        logger.info(f"absatz_aendern: Anker {grund} in {ziel} ({anzahl}x)")
        return {
            "erfolg": False, "grund": grund, "anzahl": anzahl,
            "hinweis": (
                "Der Absatz steht so nicht genau einmal im laufenden Text. "
                "Zeichengenau kopieren und bei Mehrdeutigkeit mehr Kontext geben."
            ),
        }

    # ── Verarbeitung ────────────────────────────
    nummer: int = _naechste_nummer(zeilen)
    marke: str = f"[c{nummer}>]"
    ersetzt: str = laufend.replace(alt, f"{neu} {marke}", 1)
    kopf: str = _eintrag_kopf("c", nummer, fassung.version, gesetzt)
    archiv_neu: list[str] = _archiv_einfuegen(archiv, kopf, alt.splitlines())

    groesse: int = _sichern(ziel, _zusammenfuegen(ersetzt.split("\n"), archiv_neu), roh)

    # ── Ausgabe-Verifikation ────────────────────
    befund: dict = paarung_pruefen(ziel, wurzel)
    if befund["befunde"]:
        meldung = (
            f"absatz_aendern: {ziel} hat nach dem Eingriff eine gerissene "
            f"Paarung — {befund['befunde']}"
        )
        raise RuntimeError(meldung)

    logger.info(f"absatz_aendern: {ziel} — {marke}, Version {fassung.version}, {gesetzt}")
    return {"erfolg": True, "marke": marke, "nummer": nummer, "zeichen": groesse}


def absatz_loeschen(
    pfad:    Path | str,
    wurzel:  Path | str,
    absatz:  str,
    fassung: Fassung,
) -> dict:
    """Entfernt einen Absatz und legt ihn vollstaendig ins Archiv.

    Vorbedingung: `absatz` kommt im laufenden Text genau einmal vor.
    Nachbedingung: An seiner Stelle steht nur noch die Marke `[dN>]`; der
    Wortlaut steht im Archiv, **einschliesslich der Marken, die er trug** —
    daraus entsteht die Kette.
    Fehlerfaelle: wie `absatz_aendern`.

    Die Marke bleibt stehen und wird nicht mitgeloescht: Sonst ist „hier
    stand etwas" nicht von „hier stand nie etwas" zu unterscheiden.
    """
    # ── Eingabe-Validierung ─────────────────────
    gesetzt: str = _pruefen_gemeinsam(absatz, fassung)

    ziel, roh, zeilen = _laden(pfad, wurzel)
    text, archiv = _teilen(zeilen)
    laufend: str = "\n".join(text)

    anzahl: int = laufend.count(absatz)
    if anzahl != 1:
        grund: str = "nicht_gefunden" if anzahl == 0 else "nicht_eindeutig"
        logger.info(f"absatz_loeschen: Anker {grund} in {ziel} ({anzahl}x)")
        return {
            "erfolg": False, "grund": grund, "anzahl": anzahl,
            "hinweis": "Der Absatz steht so nicht genau einmal im laufenden Text.",
        }

    # ── Verarbeitung ────────────────────────────
    nummer: int = _naechste_nummer(zeilen)
    marke: str = f"[d{nummer}>]"
    ersetzt: str = laufend.replace(absatz, marke, 1)
    kopf: str = _eintrag_kopf("d", nummer, fassung.version, gesetzt)
    archiv_neu: list[str] = _archiv_einfuegen(archiv, kopf, absatz.splitlines())

    groesse: int = _sichern(ziel, _zusammenfuegen(ersetzt.split("\n"), archiv_neu), roh)

    # ── Ausgabe-Verifikation ────────────────────
    befund: dict = paarung_pruefen(ziel, wurzel)
    if befund["befunde"]:
        meldung: str = (
            f"absatz_loeschen: {ziel} hat nach dem Eingriff eine gerissene "
            f"Paarung — {befund['befunde']}"
        )
        raise RuntimeError(meldung)

    logger.info(f"absatz_loeschen: {ziel} — {marke}, Version {fassung.version}, {gesetzt}")
    return {"erfolg": True, "marke": marke, "nummer": nummer, "zeichen": groesse}


def absatz_einfuegen(
    pfad:    Path | str,
    wurzel:  Path | str,
    absatz:  str,
    fassung: Fassung,
    nach:    str | None = None,
) -> dict:
    """Fuegt einen Absatz ein und vermerkt den Zusatz mit leerem Rumpf.

    `nach=None` haengt den Absatz ans Ende des laufenden Textes, sonst hinter
    das genannte Vorbild.

    Vorbedingung: `absatz` ist nicht leer; `nach` kommt, falls gesetzt, genau
    einmal vor.
    Nachbedingung: Der Absatz steht mit Marke `[iN>]` im Text, und das Archiv
    traegt einen Eintrag **mit leerem Rumpf**.
    Fehlerfaelle: leere Angaben (ValueError); unauffindbares Vorbild als
    Ergebnis mit `erfolg=False`.

    Der leere Eintrag steht nicht aus Symmetrie: Sobald ein Typ ohne Eintrag
    zulaessig waere, liesse sich ein fehlender Eintrag nicht mehr von einem
    erlaubten Fall unterscheiden — und die Invariante, die den einzigen
    Detektor dieses Bereichs traegt, waere keine mehr.
    """
    # ── Eingabe-Validierung ─────────────────────
    gesetzt: str = _pruefen_gemeinsam(absatz, fassung)

    ziel, roh, zeilen = _laden(pfad, wurzel)
    text, archiv = _teilen(zeilen)
    laufend: str = "\n".join(text)

    if nach is not None:
        anzahl: int = laufend.count(nach)
        if anzahl != 1:
            grund: str = "nicht_gefunden" if anzahl == 0 else "nicht_eindeutig"
            logger.info(f"absatz_einfuegen: Vorbild {grund} in {ziel} ({anzahl}x)")
            return {
                "erfolg": False, "grund": grund, "anzahl": anzahl,
                "hinweis": "Das Vorbild steht so nicht genau einmal im Text.",
            }

    # ── Verarbeitung ────────────────────────────
    nummer: int = _naechste_nummer(zeilen)
    marke: str = f"[i{nummer}>]"
    eingefuegt: str = f"{absatz} {marke}"

    if nach is None:
        neuer_text: str = laufend.rstrip("\n") + "\n\n" + eingefuegt
    else:
        neuer_text = laufend.replace(nach, f"{nach}\n\n{eingefuegt}", 1)

    kopf: str = _eintrag_kopf("i", nummer, fassung.version, gesetzt)
    archiv_neu: list[str] = _archiv_einfuegen(archiv, kopf, [])

    groesse: int = _sichern(ziel, _zusammenfuegen(neuer_text.split("\n"), archiv_neu), roh)

    # ── Ausgabe-Verifikation ────────────────────
    befund: dict = paarung_pruefen(ziel, wurzel)
    if befund["befunde"]:
        meldung: str = (
            f"absatz_einfuegen: {ziel} hat nach dem Eingriff eine gerissene "
            f"Paarung — {befund['befunde']}"
        )
        raise RuntimeError(meldung)

    logger.info(f"absatz_einfuegen: {ziel} — {marke}, Version {fassung.version}, {gesetzt}")
    return {"erfolg": True, "marke": marke, "nummer": nummer, "zeichen": groesse}


def _marken_sammeln(zeilen: list[str]) -> tuple[dict[int, str], list[int]]:
    """Sammelt die Marken des laufenden Textes und meldet doppelte Nummern."""
    marken: dict[int, str] = {}
    doppelt: list[int] = []
    for typ, nummer in marken_finden("\n".join(zeilen)):
        if nummer in marken:
            doppelt.append(nummer)
        marken[nummer] = typ
    return marken, doppelt


def _eintraege_sammeln(zeilen: list[str]) -> tuple[dict[int, str], list[int]]:
    """Sammelt die Archiveintraege und meldet doppelte Nummern."""
    eintraege: dict[int, str] = {}
    doppelt: list[int] = []
    for zeile in zeilen:
        passung = _EINTRAG.match(zeile.strip())
        if passung:
            nr: int = int(passung.group(2))
            if nr in eintraege:
                doppelt.append(nr)
            eintraege[nr] = passung.group(1)
    return eintraege, doppelt


def paarung_pruefen(pfad: Path | str, wurzel: Path | str) -> dict:
    """Prueft die Invariante: eine Marke, ein Eintrag — und umgekehrt.

    Vorbedingung: `pfad` liegt in der Wurzel.
    Nachbedingung: Ein Bericht mit `marken`, `eintraege` und `befunde`;
    `befunde` ist leer, wenn die Datei in Ordnung ist.
    Fehlerfaelle: verletzte Wurzelpruefung (ValueError).

    Vier Befundarten, jede mit eigener Bedeutung:

    * `marke_ohne_eintrag`  — die Auslagerung ist verlorengegangen
    * `eintrag_ohne_marke`  — der Text wurde ersetzt, ohne die Marke mitzunehmen
    * `nummer_doppelt`      — der Zaehler ist gerissen
    * `typ_widerspruch`     — Marke und Eintrag nennen verschiedene Vorgaenge
    """
    # ── Eingabe-Validierung ─────────────────────
    _, _, zeilen = _laden(pfad, wurzel)

    # ── Verarbeitung ────────────────────────────
    marken, doppelt_m = _marken_sammeln(zeilen)
    eintraege, doppelt_e = _eintraege_sammeln(zeilen)
    doppelt: list[int] = doppelt_m + doppelt_e

    befunde: list[dict] = []
    for nr in sorted(set(marken) - set(eintraege)):
        befunde.append({"art": "marke_ohne_eintrag", "nummer": nr, "typ": marken[nr]})
    for nr in sorted(set(eintraege) - set(marken)):
        befunde.append({"art": "eintrag_ohne_marke", "nummer": nr, "typ": eintraege[nr]})
    for nr in sorted(set(doppelt)):
        befunde.append({"art": "nummer_doppelt", "nummer": nr, "typ": marken.get(nr, "?")})
    for nr in sorted(set(marken) & set(eintraege)):
        if marken[nr] != eintraege[nr]:
            befunde.append({
                "art": "typ_widerspruch", "nummer": nr,
                "typ": f"Marke {marken[nr]}, Eintrag {eintraege[nr]}",
            })

    # ── Ausgabe-Verifikation ────────────────────
    if befunde:
        logger.warning(
            f"paarung_pruefen: {pfad} — {len(befunde)} Befund(e): "
            f"{[b['art'] for b in befunde]}"
        )

    return {"marken": len(marken), "eintraege": len(eintraege), "befunde": befunde}


def _archiv_zerlegen(archiv: list[str]) -> list[dict]:
    """Zerlegt den Archivblock in Eintraege samt Rumpf."""
    eintraege: list[dict] = []
    laufend: dict | None = None
    for zeile in archiv:
        passung = _EINTRAG.match(zeile.strip())
        if passung:
            if laufend:
                eintraege.append(laufend)
            laufend = {
                "typ":     passung.group(1),
                "nummer":  int(passung.group(2)),
                "version": passung.group("version"),
                "datum":   passung.group("datum"),
                "rumpf":   [],
            }
        elif laufend is not None:
            laufend["rumpf"].append(zeile)
    if laufend:
        eintraege.append(laufend)

    for eintrag in eintraege:
        while eintrag["rumpf"] and not eintrag["rumpf"][-1].strip():
            eintrag["rumpf"].pop()
        eintrag["rumpf"] = "\n".join(eintrag["rumpf"])
    return eintraege


def verlauf_lesen(pfad: Path | str, wurzel: Path | str) -> list[dict]:
    """Liest die Archiveintraege in ihrer Reihenfolge, juengster zuerst.

    Vorbedingung: `pfad` liegt in der Wurzel.
    Nachbedingung: Liste aus `typ`, `nummer`, `version`, `datum` und `rumpf`;
    `rumpf` ist bei einem Zusatz leer.
    Fehlerfaelle: verletzte Wurzelpruefung (ValueError).
    """
    # ── Eingabe-Validierung ─────────────────────
    _, _, zeilen = _laden(pfad, wurzel)
    _, archiv = _teilen(zeilen)

    # ── Verarbeitung ────────────────────────────
    eintraege: list[dict] = _archiv_zerlegen(archiv)

    # ── Ausgabe-Verifikation ────────────────────
    for eintrag in eintraege:
        if eintrag["typ"] not in TYPEN:
            meldung: str = (
                f"verlauf_lesen: Eintrag {eintrag['nummer']} in {pfad} traegt "
                f"den unbekannten Typ {eintrag['typ']!r}"
            )
            raise RuntimeError(meldung)
        if eintrag["typ"] == "i" and eintrag["rumpf"]:
            meldung = (
                f"verlauf_lesen: Zusatz i{eintrag['nummer']} in {pfad} traegt "
                f"einen Rumpf — ein Insert hat kein Davor"
            )
            raise RuntimeError(meldung)

    return eintraege
