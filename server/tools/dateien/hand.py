"""Die Hand — der Weg, auf dem Nova selbst eine Datei aendert.

Bis hierher schreibt eine Pipeline fuer sie: Der Recherche-Pfad legt eine
Wissensdatei ab, das Gate sagt nur ja oder nein. Sie liefert ein Destillat,
und Code legt es hin. **Sie hat keine Hand, sie hat einen Ausgang.**

Dieses Modul ist der Ausgang, den sie selbst bedienen kann. Es nimmt einen
Auftrag in JSON entgegen, prueft ihn und fuehrt ihn aus.

**Warum JSON und nicht die vorhandene Konvention.** Der Denkknoten bietet
Werkzeuge ueber `TOOL: name(parameter)` an und zerlegt die Zeile an der
Klammer. Das traegt genau einen Parameter. Ein Eingriff in eine Datei
braucht vier, davon zwei mehrzeilig, mit Anfuehrungszeichen und
Zeilenumbruechen darin — durch eine Klammerzerlegung passt das nicht.

**Die Form ist gemessen, nicht geraten.** Am 17.08.2026 wurde genau diese
Nutzlast an 30 echten Wissensdateien erhoben: `gemma4-gpu` lieferte 30 von 30
zeichengenaue, eindeutige Anker (Median 1,7 s), `qwen36-cpu` ebenfalls 30 von
30 (Median 17,9 s). Kein Fehlgriff, kein mehrdeutiger Anker, kein kaputtes
JSON.

Drei Zusicherungen, die dieses Modul traegt:

**Geschrieben wird ausschliesslich in ihrer eigenen Zone.** Die Wurzel ist
ein Pflichtargument; freigegebene Fremdverzeichnisse haben hier keinen Weg
hinein. Ein Recht, das nicht im Modul liegt, kann kein Prompt herbeireden.

**Ein misslungener Auftrag ist ein Ergebnis, kein Absturz.** Was sie falsch
macht — Anker nicht gefunden, mehrdeutig, unbekannte Aktion —, kommt als
Antwort zurueck, die sie lesen und beantworten kann. Das ist die Bedingung
dafuer, dass sie es beim zweiten Versuch besser macht.

**Jede Aenderung wird versioniert.** Wer ueber diese Hand schreibt, laesst
eine Marke und einen Archiveintrag zurueck; der Verlauf bleibt umkehrbar.
"""

import json
import logging
from pathlib import Path

from tools.dateien.operationen import (
    block_lesen,
    datei_grep,
    struktur_analysieren,
    zeilen_lesen,
)
from tools.dateien.versionierung import (
    Fassung,
    absatz_aendern,
    absatz_einfuegen,
    absatz_loeschen,
    aktuell_lesen,
    paarung_pruefen,
    verlauf_lesen,
)

logger = logging.getLogger("ki_server.tools.dateien.hand")

# Der Kanon der Aktionen. Geschlossen und geprueft: Ein unbekannter Name ist
# ein Befund und kein stiller Fehlschlag — sonst ist ein Tippfehler von einer
# nicht gebauten Aktion nicht zu unterscheiden.
LESEND:     tuple[str, ...] = ("aktuell", "karte", "block", "zeilen", "suchen", "verlauf", "pruefen")
SCHREIBEND: tuple[str, ...] = ("aendern", "loeschen", "einfuegen")
AKTIONEN:   tuple[str, ...] = LESEND + SCHREIBEND

ANLEITUNG: str = """[DATEIEN]
Du kannst in deinen eigenen Wissensdateien lesen und schreiben.
Schreibe dazu eine Zeile, die mit DATEI: beginnt, gefolgt von JSON:

DATEI: {"aktion": "karte", "pfad": "<datei>"}

Lesen:
  aktuell  — der geltende Text ohne Historie (der Normalfall)
  karte    — welche Bloecke hat die Datei
  block    — {"aktion":"block","pfad":"...","header":"## Titel"}
  zeilen   — {"aktion":"zeilen","pfad":"...","von":1,"bis":40}
  suchen   — {"aktion":"suchen","pfad":"...","begriff":"..."}
  verlauf  — was frueher an dieser Datei geaendert wurde

Schreiben (jede Aenderung wird versioniert und bleibt umkehrbar):
  aendern   — {"aktion":"aendern","pfad":"...","alt":"<zeichengenau>","neu":"...","version":"2.3"}
  loeschen  — {"aktion":"loeschen","pfad":"...","absatz":"<zeichengenau>","version":"2.3"}
  einfuegen — {"aktion":"einfuegen","pfad":"...","absatz":"...","version":"2.3"}

WICHTIG fuer `alt` und `absatz`: zeichengenau aus der Datei kopieren, mit
allen Anfuehrungszeichen und Gedankenstrichen, und lang genug, um nur einmal
vorzukommen. Bekommst du "nicht_eindeutig" zurueck, gib mehr Kontext."""


def _objekt_ende(rumpf: str) -> int:
    """Findet das Ende des ersten JSON-Objekts, Klammern in Text ignorierend.

    Die Zeile kann hinter dem Objekt weitergehen; gelesen wird bis zur
    schliessenden Klammer der aeussersten Ebene. Anfuehrungszeichen und
    Rueckstriche werden beachtet, weil `alt` und `neu` regelmaessig beides
    enthalten — ein naiver Klammerzaehler zerschnitte genau die Auftraege,
    auf die es ankommt.

    Returns:
        Position hinter der schliessenden Klammer, oder -1.
    """
    tiefe: int = 0
    in_text: bool = False
    schutz: bool = False
    for i, zeichen in enumerate(rumpf):
        if schutz:
            schutz = False
        elif zeichen == "\\":
            schutz = True
        elif zeichen == '"':
            in_text = not in_text
        elif in_text:
            continue
        elif zeichen == "{":
            tiefe += 1
        elif zeichen == "}":
            tiefe -= 1
            if tiefe == 0:
                return i + 1
    return -1


def auftrag_lesen(zeile: str) -> dict | None:
    """Holt den JSON-Auftrag aus einer `DATEI:`-Zeile.

    Vorbedingung: keine — die Eingabe ist Modellausgabe und damit die
    unzuverlaessigste Quelle im System.
    Nachbedingung: Ein Woerterbuch oder `None`, wenn die Zeile keinen
    verwertbaren Auftrag traegt.
    Fehlerfaelle: keine nach aussen; kaputtes JSON ist ein `None` mit
    Protokolleintrag, damit ein Formfehler nicht wie ein fehlender Aufruf
    aussieht.
    """
    # ── Eingabe-Validierung ─────────────────────
    if "DATEI:" not in zeile:
        return None

    rumpf: str = zeile.split("DATEI:", 1)[1].strip()
    if not rumpf.startswith("{"):
        logger.warning(f"auftrag_lesen: kein JSON nach DATEI: — {rumpf[:80]!r}")
        return None

    # ── Verarbeitung ────────────────────────────
    ende: int = _objekt_ende(rumpf)
    if ende < 0:
        logger.warning(f"auftrag_lesen: unvollstaendiges JSON — {rumpf[:80]!r}")
        return None

    try:
        auftrag: dict = json.loads(rumpf[:ende])
    except json.JSONDecodeError as fehler:
        logger.warning(f"auftrag_lesen: JSON nicht lesbar — {fehler}")
        return None

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(auftrag, dict):
        logger.warning(f"auftrag_lesen: JSON ist kein Objekt — {type(auftrag).__name__}")
        return None

    return auftrag


def _fehler(grund: str, hinweis: str) -> dict:
    """Baut eine Antwort, die das Modell lesen und beantworten kann."""
    return {"erfolg": False, "grund": grund, "hinweis": hinweis}


def _pflicht(auftrag: dict, felder: tuple[str, ...]) -> dict | None:
    """Prueft Pflichtfelder und nennt bei Fehlen den Bestand."""
    fehlend: list[str] = [f for f in felder if not str(auftrag.get(f, "")).strip()]
    if fehlend:
        return _fehler(
            "feld_fehlt",
            f"Es fehlen: {', '.join(fehlend)}. Vorhanden sind: "
            f"{', '.join(sorted(auftrag)) or 'nichts'}.",
        )
    return None


def _lesen_ausfuehren(auftrag: dict, pfad: str, wurzel: Path | str) -> dict:
    """Fuehrt die lesenden Aktionen aus."""
    aktion: str = auftrag["aktion"]

    if aktion == "aktuell":
        return {"erfolg": True, "text": aktuell_lesen(pfad, wurzel)}

    if aktion == "karte":
        return {"erfolg": True, "bloecke": struktur_analysieren(pfad, wurzel)}

    if aktion == "block":
        mangel: dict | None = _pflicht(auftrag, ("header",))
        if mangel:
            return mangel
        return {"erfolg": True, **block_lesen(pfad, wurzel, auftrag["header"])}

    if aktion == "zeilen":
        von: int = int(auftrag.get("von", 1))
        bis: int = int(auftrag.get("bis", von + 39))
        return {"erfolg": True, **zeilen_lesen(pfad, wurzel, von, bis)}

    if aktion == "suchen":
        mangel = _pflicht(auftrag, ("begriff",))
        if mangel:
            return mangel
        return {"erfolg": True, **datei_grep(pfad, wurzel, auftrag["begriff"])}

    if aktion == "verlauf":
        return {"erfolg": True, "eintraege": verlauf_lesen(pfad, wurzel)}

    return {"erfolg": True, **paarung_pruefen(pfad, wurzel)}


def _schreiben_ausfuehren(auftrag: dict, pfad: str, wurzel: Path | str) -> dict:
    """Fuehrt die schreibenden Aktionen aus; jede wird versioniert."""
    aktion: str = auftrag["aktion"]
    fassung: Fassung = Fassung(str(auftrag["version"]), auftrag.get("datum"))

    if aktion == "aendern":
        mangel: dict | None = _pflicht(auftrag, ("alt", "neu"))
        if mangel:
            return mangel
        return absatz_aendern(pfad, wurzel, auftrag["alt"], auftrag["neu"], fassung)

    if aktion == "loeschen":
        mangel = _pflicht(auftrag, ("absatz",))
        if mangel:
            return mangel
        return absatz_loeschen(pfad, wurzel, auftrag["absatz"], fassung)

    mangel = _pflicht(auftrag, ("absatz",))
    if mangel:
        return mangel
    return absatz_einfuegen(
        pfad, wurzel, auftrag["absatz"], fassung, nach=auftrag.get("nach"),
    )


def auftrag_ausfuehren(auftrag: dict, wurzel: Path | str) -> dict:
    """Fuehrt einen geprueften Auftrag aus und gibt eine lesbare Antwort.

    Vorbedingung: `auftrag` ist ein Woerterbuch aus `auftrag_lesen`; `wurzel`
    benennt die Zone, in der gearbeitet werden darf, und hat keinen
    Vorgabewert.
    Nachbedingung: Das Ergebnis traegt immer `erfolg`; bei `False` zusaetzlich
    `grund` und `hinweis`.
    Fehlerfaelle: **keine nach aussen.** Jeder Fehlgriff des Modells wird zu
    einer Antwort, die es lesen kann — genau das macht den zweiten Versuch
    moeglich. Ein Programmfehler dieses Moduls wird protokolliert und als
    `grund="werkzeugfehler"` gemeldet, nicht verschluckt.
    """
    # ── Eingabe-Validierung ─────────────────────
    aktion: str = str(auftrag.get("aktion", "")).strip()
    if aktion not in AKTIONEN:
        return _fehler(
            "unbekannte_aktion",
            f"{aktion!r} gibt es nicht. Moeglich sind: {', '.join(AKTIONEN)}.",
        )

    mangel: dict | None = _pflicht(auftrag, ("pfad",))
    if mangel:
        return mangel

    if aktion in SCHREIBEND:
        mangel = _pflicht(auftrag, ("version",))
        if mangel:
            return mangel

    pfad: str = str(auftrag["pfad"])

    # ── Verarbeitung ────────────────────────────
    try:
        if aktion in LESEND:
            ergebnis: dict = _lesen_ausfuehren(auftrag, pfad, wurzel)
        else:
            ergebnis = _schreiben_ausfuehren(auftrag, pfad, wurzel)
    except ValueError as fehler:
        # Erwartbar: Pfad ausserhalb der Wurzel, unbekannter Header, leere
        # Angabe. Das ist eine Auskunft an sie und kein Defekt.
        logger.info(f"auftrag_ausfuehren: {aktion} abgewiesen — {fehler}")
        return _fehler("abgewiesen", str(fehler))
    except (OSError, RuntimeError) as fehler:
        logger.exception(f"{type(fehler).__name__}: auftrag_ausfuehren: {aktion} auf {pfad}")
        return _fehler(
            "werkzeugfehler",
            f"Das Werkzeug ist gescheitert: {fehler}. Das liegt nicht an dir.",
        )

    # ── Ausgabe-Verifikation ────────────────────
    if "erfolg" not in ergebnis:
        meldung: str = (
            f"auftrag_ausfuehren: Antwort auf {aktion!r} traegt kein Feld "
            f"'erfolg' — {sorted(ergebnis)}"
        )
        raise RuntimeError(meldung)

    logger.info(
        f"auftrag_ausfuehren: {aktion} auf {pfad} — "
        f"{'erfolg' if ergebnis['erfolg'] else ergebnis.get('grund')}"
    )
    return ergebnis


def antwort_formulieren(ergebnis: dict) -> str:
    """Formt die Antwort so, dass das Modell sie im naechsten Zug lesen kann.

    Vorbedingung: `ergebnis` traegt ein Feld `erfolg`.
    Nachbedingung: Eine nicht leere Zeichenkette.
    Fehlerfaelle: fehlendes `erfolg` (ValueError) — eine Antwort ohne
    Ausgang waere keine.
    """
    # ── Eingabe-Validierung ─────────────────────
    if "erfolg" not in ergebnis:
        meldung: str = f"antwort_formulieren: kein Feld 'erfolg' in {sorted(ergebnis)}"
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    if not ergebnis["erfolg"]:
        text: str = (
            f"Datei-Werkzeug: {ergebnis.get('grund', 'fehlgeschlagen')} — "
            f"{ergebnis.get('hinweis', '')}".strip()
        )
        if "anzahl" in ergebnis:
            text += f" (gefunden: {ergebnis['anzahl']}x)"
        return text

    knapp: dict = {k: v for k, v in ergebnis.items() if k != "erfolg"}
    return f"Datei-Werkzeug: {json.dumps(knapp, ensure_ascii=False, default=str)}"
