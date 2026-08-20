"""Leseschicht des Dateizugriffs — Karte, Block, Fenster, Fundstelle.

Deterministische Navigation in Textdateien, ohne sie vollstaendig zu laden.
Kein Modellaufruf: Der Agent entscheidet, das Werkzeug fuehrt aus.

Drei Zusicherungen, die dieses Modul traegt:

**Jeder Pfad wird gegen eine ausdrueckliche Wurzel geprueft.** Die Wurzel ist
ein Pflichtargument und hat keinen Vorgabewert — ein Lesewerkzeug, das ohne
Angabe der Zone aufgerufen werden kann, ist eine Zone ohne Grenze. Aufgeloest
wird vor der Pruefung, damit weder `..` noch eine symbolische Verknuepfung
daran vorbeifuehrt (docs/novaberg-agent-dateien_k.md §7).

**Ueberschriften in Codebloecken sind keine Ueberschriften.** Eine Zeile mit
fuehrendem `#` innerhalb eines ```-Blocks ist Inhalt. Wer das uebergeht, baut
eine Karte mit Blockgrenzen, die im Text nicht existieren — und `block_lesen`
liefert danach einen Ausschnitt, den niemand nachvollziehen kann.

**Eine Datei ohne Blockstruktur ist kein Fehler, sondern ein Befund.**
Gemessen am 17.08.2026 tragen **223 von 223** Wissensdateien keine
`##`-Ueberschrift, waehrend 461 von 462 uebrigen Dateien welche haben. Die
Karte meldet das als leere Blockliste und protokolliert es; der Aufrufer
faellt dann auf `zeilen_lesen` zurueck. Stillschweigend eine Ein-Block-Karte
zu erfinden waere die teurere Variante — sie saehe aus wie Struktur.

**Und davon getrennt: eine Gliederung, die nicht erhoben werden konnte, ist
kein Befund.** Die leere Liste sagt *„nachgesehen, es gibt keine"*. Sie darf
deshalb nicht auch *„ich verstehe dieses Format nicht"* und nicht *„die
Auszeichnung dieser Datei geht nicht auf"* heissen — beides sind Ausfaelle
und werfen `StrukturUnklarError` (`22_STILLE_FEHLER` §5).
`[gemessen]` — 20.08.2026: Ein einzelner durchgestrichener Codezaun
(`~~` gefolgt vom Zaun, dessen schliessendes Gegenstueck der Erkenner sah)
liess in `novaberg-agent-dateien_k.md` von **83 Ueberschriften nur 5**
uebrig; 1158 von 1236 Zeilen galten als Code. Die Karte war nicht leer,
sondern falsch, und sah wie eine kurze Datei aus.

Zeilennummern sind durchgehend **1-basiert**, weil `datei_grep` und
`zeilen_lesen` ihre Ergebnisse an Menschen und an ein Sprachmodell geben und
beide Seiten so zaehlen.
"""

import fnmatch
import logging
import re
from collections.abc import Callable
from pathlib import Path

from markdown_it import MarkdownIt

logger = logging.getLogger("ki_server.tools.dateien.operationen")

# Hoechstzahl Zeilen je Lesevorgang. Der Wert begrenzt den Kontextverbrauch
# eines einzelnen Aufrufs, nicht die Datei — wer mehr braucht, ruft mit
# hoeherem `offset` erneut. Gehoert nach config.py, sobald der Dienst gebaut
# wird; bis dahin steht er hier, damit dieses Modul ohne Abhaengigkeit
# pruefbar bleibt.
BLOCK_LIMIT: int = 200

# Obergrenze fuer `datei_grep`, damit eine ungluecklich gewaehlte Suche nicht
# die halbe Datei zurueckgibt. Ein abgeschnittenes Ergebnis wird ausgewiesen,
# nicht stillschweigend gekuerzt.
GREP_LIMIT: int = 100


class StrukturUnklarError(Exception):
    """Die Gliederung dieser Datei ist NICHT erhoben.

    Ausdruecklich verschieden von der leeren Blockliste: Die sagt
    *„nachgesehen, die Datei hat keine Ueberschriften"*. Diese Ausnahme sagt
    *„nicht nachgesehen"* oder *„nachgesehen und es geht nicht auf"*. Wer
    beides auf denselben Rueckgabewert abbildet, macht einen Ausfall von
    einem Befund ununterscheidbar — und der Ausfall gewinnt, weil er wie das
    haeufigere Ergebnis aussieht.
    """


class FormatOhneErkennerError(StrukturUnklarError):
    """Fuer diese Dateiendung ist kein Gliederungs-Erkenner registriert."""


class StrukturDefektError(StrukturUnklarError):
    """Die Datei ist im erkannten Format nicht schluessig ausgezeichnet."""


_CODEZAUN: re.Pattern = re.compile(r"^\s*(```|~~~)")
_UEBERSCHRIFT: re.Pattern = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_METAZEILE: re.Pattern = re.compile(r"^\*\*(?P<feld>[^:*]+):\*\*\s*(?P<wert>.*\S)\s*$")

#: Der Markdown-Parser, einmal je Prozess. `commonmark` ist die strenge
#: Grundfassung ohne Erweiterungen — sie deckt genau das ab, was ein
#: handgeschriebener Zeilenautomat einzeln nachbauen muesste: Setext-Ueber-
#: schriften, eingerueckte Codebloecke, Zaeune aus vier und mehr Zeichen,
#: verschachtelte Zaeune, Ueberschriften mit bis zu drei Leerzeichen Einzug.
_MARKDOWN: MarkdownIt = MarkdownIt("commonmark")


def pfad_pruefen(pfad: Path | str, wurzel: Path | str) -> Path:
    """Loest einen Pfad auf und prueft, dass er innerhalb der Wurzel liegt.

    Vorbedingung: Beide Angaben sind nicht leer. `pfad` muss existieren —
    ein Lesewerkzeug auf einer fehlenden Datei ist ein Aufruffehler und kein
    Leerergebnis.
    Nachbedingung: Der Rueckgabewert ist aufgeloest, existiert und liegt
    unterhalb der aufgeloesten Wurzel.
    Fehlerfaelle: leere Angabe, Ziel ausserhalb der Wurzel, fehlende Datei —
    alle drei als ValueError an den Aufrufer, keiner geschluckt.

    Die Aufloesung geschieht VOR der Pruefung. Umgekehrt prueft man eine
    Zeichenkette und nicht ein Verzeichnis.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not str(pfad).strip():
        meldung: str = "pfad_pruefen: leerer Pfad uebergeben"
        raise ValueError(meldung)
    if not str(wurzel).strip():
        meldung = f"pfad_pruefen: leere Wurzel fuer Pfad {pfad}"
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    aufgeloest: Path = Path(pfad).resolve(strict=False)
    wurzel_auf: Path = Path(wurzel).resolve(strict=False)

    # ── Ausgabe-Verifikation ────────────────────
    if not aufgeloest.is_relative_to(wurzel_auf):
        meldung = (
            f"pfad_pruefen: Ziel liegt ausserhalb der Wurzel — "
            f"Ziel {aufgeloest}, Wurzel {wurzel_auf}"
        )
        raise ValueError(meldung)

    if not aufgeloest.is_file():
        meldung = f"pfad_pruefen: {aufgeloest} ist keine lesbare Datei"
        raise ValueError(meldung)

    return aufgeloest


def _zeilen_laden(pfad: Path, wurzel: Path | str) -> list[str]:
    """Liest eine geprueft Datei als Zeilenliste ohne Zeilenenden."""
    geprueft: Path = pfad_pruefen(pfad, wurzel)
    return geprueft.read_text(encoding="utf-8").splitlines()


def _ueberschriften_markdown(zeilen: list[str]) -> list[tuple[int, int, str]]:
    """Findet Markdown-Ueberschriften ausserhalb von Codebloecken.

    Vorbedingung: `zeilen` sind die Zeilen einer Markdown-Datei, ohne
    Zeilenenden.
    Nachbedingung: Liste aus (Zeilennummer 1-basiert, Ebene,
    Ueberschriftentext), in Dateireihenfolge.
    Fehlerfaelle: eine ungerade Zahl Codezaeune (`StrukturDefektError`).

    **Die Erkennung macht `markdown-it-py` (CommonMark), nicht dieses
    Modul.** Der Grund ist keine Bequemlichkeit: Ein Zeilenautomat kennt die
    Regeln, die jemand hineingeschrieben hat, und die Datei, die er nicht
    kennt, ist immer die naechste. Setext-Ueberschriften, eingerueckte
    Codebloecke, Zaeune aus vier Zeichen und verschachtelte Zaeune sind vier
    Faelle, die einzeln nachzubauen waeren.

    **Die Zaunbilanz bleibt trotzdem, und zwar VOR dem Parser.** Sie ist
    keine doppelte Absicherung, sondern faengt einen Fall, den auch
    CommonMark falsch beantwortet: Am 20.08.2026 fand der Zeilenautomat in
    einer Datei mit unpaarigem Zaun 5 von 83 Ueberschriften, der Parser
    45 von 83. Beide Karten sind falsch — und eine falsche Karte ist teurer
    als eine fehlende, weil der Aufrufer ihr folgt statt auszuweichen.
    """
    # ── Eingabe-Validierung: die Zaunbilanz ─────
    # Sie steht VOR dem Parser und nicht statt seiner. Der Parser macht
    # denselben Fehler, nur schwaecher: An der defekten Fassung vom
    # 20.08.2026 fand der Zeilenautomat 5 von 83 Ueberschriften, CommonMark
    # 45 von 83 — beides ist eine falsche Karte, und eine falsche Karte ist
    # teurer als gar keine. Die Bilanz kostet einen Durchlauf und ist ohne
    # jede Kenntnis des Inhalts pruefbar.
    im_zaun: bool = False
    zaeune: int = 0
    letzter_zaun: int = 0
    for nr, zeile in enumerate(zeilen, start=1):
        if _CODEZAUN.match(zeile):
            zaeune += 1
            letzter_zaun = nr
            im_zaun = not im_zaun

    if im_zaun:
        meldung: str = (
            f"_ueberschriften_markdown: {zaeune} Codezaeune sind eine ungerade "
            f"Zahl, der letzte in Zeile {letzter_zaun} von {len(zeilen)} — ab "
            f"dort gilt der Rest der Datei als Code, und jede Karte darueber "
            f"waere kuerzer als das Dokument"
        )
        raise StrukturDefektError(meldung)

    # ── Verarbeitung ────────────────────────────
    treffer: list[tuple[int, int, str]] = []
    for marke in _MARKDOWN.parse("\n".join(zeilen)):
        if marke.type != "heading_open" or not marke.map:
            continue
        # `level > 0` heisst: die Ueberschrift steht INNERHALB eines anderen
        # Blocks, im Bestand durchweg in einem Blockzitat. Sie gehoert zum
        # zitierten Text und ist kein Gliederungspunkt der Datei — ihr Block
        # liefe bis zur naechsten gleichrangigen Ueberschrift und damit ueber
        # das Zitat hinaus. Das ist dieselbe Zusicherung wie beim Codezaun:
        # eine Blockgrenze, die im Dokument nicht existiert, ist schlimmer
        # als eine fehlende. Am 20.08.2026 ueber den Bestand gezaehlt: acht
        # solche Ueberschriften in acht Dateien.
        if marke.level != 0:
            continue
        # `map` ist 0-basiert und haelt [Anfang, Ende); die Zeilennummern
        # dieses Moduls sind durchgehend 1-basiert. Bei einer
        # Setext-Ueberschrift zeigt `map[0]` auf die Textzeile, nicht auf
        # ihre Unterstreichung — genau die Zeile, die der Header traegt.
        zeilennummer: int = marke.map[0] + 1
        ebene: int = int(marke.tag[1])
        treffer.append((zeilennummer, ebene, zeilen[marke.map[0]].rstrip()))

    # ── Ausgabe-Verifikation ────────────────────
    for zeilennummer, ebene, _text in treffer:
        if not 1 <= zeilennummer <= len(zeilen):
            meldung = (
                f"_ueberschriften_markdown: Ueberschrift in Zeile "
                f"{zeilennummer} liegt ausserhalb der Datei ({len(zeilen)} "
                f"Zeilen)"
            )
            raise StrukturDefektError(meldung)
        if not 1 <= ebene <= 6:
            meldung = (
                f"_ueberschriften_markdown: Ebene {ebene} in Zeile "
                f"{zeilennummer} liegt ausserhalb von 1 bis 6"
            )
            raise StrukturDefektError(meldung)

    return treffer


#: Welcher Erkenner fuer welche Endung zustaendig ist.
#:
#: **Der Index laesst mehr Endungen zu, als hier stehen** — heute
#: `.md,.txt,.rst,.org,.adoc` (`DATEIEN_INDEX_ENDUNGEN`), erkannt wird allein
#: Markdown. Die Luecke steht deshalb als Ausnahme im Weg und nicht als leere
#: Karte: In reStructuredText steht die Ueberschrift ueber einer
#: Unterstreichung, in Org-Mode beginnt sie mit `*`, in AsciiDoc mit `=` —
#: keine davon traegt ein `#`, und alle drei ergaeben eine leere Liste, also
#: die Aussage *„durchgehender Text"* ueber eine gegliederte Datei.
_ERKENNER: dict[str, Callable[[list[str]], list[tuple[int, int, str]]]] = {
    ".md": _ueberschriften_markdown,
}


def struktur_analysieren(pfad: Path | str, wurzel: Path | str) -> list[dict]:
    """Erkennt die Blockstruktur einer Datei, ohne ihren Inhalt zu liefern.

    Ein Block reicht von seiner Ueberschrift bis zur naechsten Ueberschrift
    gleicher oder hoeherer Ebene, sonst bis zum Dateiende.

    Vorbedingung: `pfad` besteht die Wurzelpruefung und traegt eine Endung,
    fuer die ein Erkenner registriert ist.
    Nachbedingung: Jeder Eintrag traegt `header`, `ebene`, `start`, `ende`
    und `zeilen`; die Bereiche ueberlappen nicht und `ende >= start`.
    Fehlerfaelle: verletzte Wurzelpruefung (ValueError), Lesefehler (OSError),
    Endung ohne Erkenner (`FormatOhneErkennerError`), unschluessige Auszeichnung
    (`StrukturDefektError`). Die letzten beiden sind `StrukturUnklarError` und heissen
    *nicht erhoben* — der Aufrufer darf sie nicht auf die leere Liste
    abbilden.

    Eine leere Liste bedeutet: **die Datei hat keine Blockstruktur.** Das ist
    ein gueltiges Ergebnis und wird protokolliert; der Aufrufer arbeitet dann
    mit `zeilen_lesen`.
    """
    # ── Eingabe-Validierung ─────────────────────
    endung: str = Path(pfad).suffix.lower()
    erkenner = _ERKENNER.get(endung)
    if erkenner is None:
        hinweis: str = (
            f"struktur_analysieren: fuer '{endung or '(ohne Endung)'}' ist kein "
            f"Gliederungs-Erkenner registriert ({pfad}) — bekannt sind "
            f"{sorted(_ERKENNER)}. Eine leere Karte waere hier die Aussage "
            f"'durchgehender Text' ueber eine Datei, die niemand angesehen hat"
        )
        raise FormatOhneErkennerError(hinweis)

    zeilen: list[str] = _zeilen_laden(Path(pfad), wurzel)

    # ── Verarbeitung ────────────────────────────
    ueberschriften: list[tuple[int, int, str]] = erkenner(zeilen)
    bloecke: list[dict] = []

    for i, (start, ebene, text) in enumerate(ueberschriften):
        ende: int = len(zeilen)
        for folge_start, folge_ebene, _ in ueberschriften[i + 1:]:
            if folge_ebene <= ebene:
                ende = folge_start - 1
                break
        bloecke.append({
            "header": text,
            "ebene":  ebene,
            "start":  start,
            "ende":   ende,
            "zeilen": ende - start + 1,
        })

    # ── Ausgabe-Verifikation ────────────────────
    for block in bloecke:
        if block["ende"] < block["start"]:
            meldung: str = (
                f"struktur_analysieren: Block {block['header']!r} in {pfad} "
                f"endet bei {block['ende']} vor seinem Anfang {block['start']}"
            )
            raise RuntimeError(meldung)

    if not bloecke:
        logger.info(
            f"struktur_analysieren: {pfad} hat keine Blockstruktur "
            f"({len(zeilen)} Zeilen) — Aufrufer muss auf zeilen_lesen ausweichen"
        )

    return bloecke


def block_lesen(
    pfad:   Path | str,
    wurzel: Path | str,
    header: str,
    offset: int = 0,
    limit:  int = BLOCK_LIMIT,
) -> dict:
    """Liest einen Block gefenstert.

    Vorbedingung: `pfad` besteht die Wurzelpruefung, `header` ist nicht leer,
    `offset` und `limit` sind nicht negativ, `limit` ist groesser null.
    Nachbedingung: Das Ergebnis traegt `inhalt`, `block_zeilen`,
    `gelesen_von`, `gelesen_bis` und `rest`; `rest` ist nie negativ.
    Fehlerfaelle: unbekannter oder mehrdeutiger Header, ungueltiges Fenster —
    als ValueError an den Aufrufer.

    Der Header wird exakt verglichen, nach Abschneiden der Randleerzeichen.
    Ein mehrdeutiger Header ist ein Fehler und **kein** Griff zum ersten
    Treffer: Sonst liefert derselbe Aufruf morgen einen anderen Block, sobald
    jemand eine gleichnamige Ueberschrift ergaenzt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not header.strip():
        meldung: str = f"block_lesen: leerer Header fuer {pfad}"
        raise ValueError(meldung)
    if offset < 0 or limit <= 0:
        meldung = (
            f"block_lesen: ungueltiges Fenster fuer {pfad} — "
            f"offset={offset}, limit={limit}"
        )
        raise ValueError(meldung)

    zeilen: list[str] = _zeilen_laden(Path(pfad), wurzel)
    bloecke: list[dict] = struktur_analysieren(pfad, wurzel)

    gesucht: str = header.strip()
    passende: list[dict] = [b for b in bloecke if b["header"].strip() == gesucht]

    if not passende:
        vorhanden: str = ", ".join(b["header"].strip() for b in bloecke) or "keine"
        meldung = (
            f"block_lesen: Header {gesucht!r} nicht in {pfad} — "
            f"vorhandene Bloecke: {vorhanden}"
        )
        raise ValueError(meldung)

    if len(passende) > 1:
        stellen: str = ", ".join(str(b["start"]) for b in passende)
        meldung = (
            f"block_lesen: Header {gesucht!r} kommt in {pfad} {len(passende)}-mal "
            f"vor (Zeilen {stellen}) — mehr Kontext noetig, kein Griff zum ersten"
        )
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    block: dict = passende[0]
    # Der Rumpf beginnt nach der Ueberschriftenzeile; `start` ist 1-basiert.
    rumpf: list[str] = zeilen[block["start"]:block["ende"]]
    ausschnitt: list[str] = rumpf[offset:offset + limit]
    rest: int = max(0, len(rumpf) - (offset + len(ausschnitt)))

    ergebnis: dict = {
        "inhalt":       "\n".join(ausschnitt),
        "block_zeilen": len(rumpf),
        "gelesen_von":  offset,
        "gelesen_bis":  offset + len(ausschnitt),
        "rest":         rest,
    }

    # ── Ausgabe-Verifikation ────────────────────
    if ergebnis["gelesen_bis"] - ergebnis["gelesen_von"] != len(ausschnitt):
        meldung = (
            f"block_lesen: Fensterangabe passt nicht zum Inhalt in {pfad} — "
            f"von {ergebnis['gelesen_von']} bis {ergebnis['gelesen_bis']}, "
            f"aber {len(ausschnitt)} Zeilen"
        )
        raise RuntimeError(meldung)

    return ergebnis


def zeilen_lesen(
    pfad:   Path | str,
    wurzel: Path | str,
    von:    int,
    bis:    int,
) -> dict:
    """Liest einen Zeilenbereich — der Rueckfallweg ohne Blockstruktur.

    Vorbedingung: `pfad` besteht die Wurzelpruefung, `von` ist mindestens 1
    und `bis` nicht kleiner als `von`.
    Nachbedingung: Das Ergebnis traegt `inhalt`, `datei_zeilen`,
    `gelesen_von`, `gelesen_bis` und `rest`.
    Fehlerfaelle: ungueltiger Bereich (ValueError).

    `bis` ist einschliesslich. Ein Bereich ueber das Dateiende hinaus ist
    **kein** Fehler — er wird gekappt und die tatsaechlich gelesene Grenze
    ausgewiesen, damit der Aufrufer den Unterschied sieht.
    """
    # ── Eingabe-Validierung ─────────────────────
    if von < 1:
        meldung: str = f"zeilen_lesen: von={von} ist kleiner als 1 ({pfad})"
        raise ValueError(meldung)
    if bis < von:
        meldung = f"zeilen_lesen: bis={bis} liegt vor von={von} ({pfad})"
        raise ValueError(meldung)

    zeilen: list[str] = _zeilen_laden(Path(pfad), wurzel)

    # ── Verarbeitung ────────────────────────────
    letzte: int = min(bis, len(zeilen))
    ausschnitt: list[str] = zeilen[von - 1:letzte] if von <= len(zeilen) else []

    ergebnis: dict = {
        "inhalt":       "\n".join(ausschnitt),
        "datei_zeilen": len(zeilen),
        "gelesen_von":  von,
        "gelesen_bis":  letzte if ausschnitt else von - 1,
        "rest":         max(0, len(zeilen) - letzte),
    }

    # ── Ausgabe-Verifikation ────────────────────
    if ausschnitt and len(ausschnitt) != ergebnis["gelesen_bis"] - ergebnis["gelesen_von"] + 1:
        meldung = (
            f"zeilen_lesen: {len(ausschnitt)} Zeilen gelesen, aber Bereich "
            f"{ergebnis['gelesen_von']}–{ergebnis['gelesen_bis']} in {pfad}"
        )
        raise RuntimeError(meldung)

    return ergebnis


def datei_grep(
    pfad:        Path | str,
    wurzel:      Path | str,
    suchbegriff: str,
    regex:       bool = False,
) -> dict:
    """Sucht zeilenweise und gibt Fundstellen mit Zeilennummer zurueck.

    Vorbedingung: `pfad` besteht die Wurzelpruefung, `suchbegriff` ist nicht
    leer. Bei `regex=True` muss das Muster uebersetzbar sein.
    Nachbedingung: Das Ergebnis traegt `treffer` (Liste aus Zeilennummer und
    Zeile), `anzahl` und `gekappt`.
    Fehlerfaelle: leerer Suchbegriff, ungueltiges Muster (ValueError).

    **Ein gekapptes Ergebnis wird ausgewiesen.** Eine stillschweigend
    gekuerzte Trefferliste ist von einer vollstaendigen nicht zu
    unterscheiden, und der Aufrufer schliesst aus ihr auf den Bestand.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not suchbegriff:
        meldung: str = f"datei_grep: leerer Suchbegriff fuer {pfad}"
        raise ValueError(meldung)

    muster: re.Pattern | None = None
    if regex:
        try:
            muster = re.compile(suchbegriff)
        except re.error as fehler:
            meldung = f"datei_grep: ungueltiges Muster {suchbegriff!r} — {fehler}"
            raise ValueError(meldung) from fehler

    zeilen: list[str] = _zeilen_laden(Path(pfad), wurzel)

    # ── Verarbeitung ────────────────────────────
    alle: list[tuple[int, str]] = []
    for nr, zeile in enumerate(zeilen, start=1):
        gefunden: bool = bool(muster.search(zeile)) if muster else (suchbegriff in zeile)
        if gefunden:
            alle.append((nr, zeile))

    gekappt: bool = len(alle) > GREP_LIMIT
    treffer: list[tuple[int, str]] = alle[:GREP_LIMIT]

    if gekappt:
        logger.warning(
            f"datei_grep: {len(alle)} Treffer fuer {suchbegriff!r} in {pfad}, "
            f"auf {GREP_LIMIT} gekappt — das Ergebnis ist unvollstaendig"
        )

    # ── Ausgabe-Verifikation ────────────────────
    for nr, _ in treffer:
        if not 1 <= nr <= len(zeilen):
            meldung = (
                f"datei_grep: Zeilennummer {nr} liegt ausserhalb der Datei "
                f"{pfad} mit {len(zeilen)} Zeilen"
            )
            raise RuntimeError(meldung)

    return {"treffer": treffer, "anzahl": len(alle), "gekappt": gekappt}


def metadaten_lesen(pfad: Path | str, wurzel: Path | str) -> dict[str, str]:
    """Liest den Metadatenkopf einer Datei — Zeilen der Form `**Feld:** Wert`.

    Vorbedingung: `pfad` besteht die Wurzelpruefung.
    Nachbedingung: Ein Woerterbuch der gefundenen Felder; leer, wenn keins
    vorhanden ist.
    Fehlerfaelle: verletzte Wurzelpruefung (ValueError).

    Gelesen wird nur der Kopf — bis zur ersten Trennlinie `---` oder zur
    ersten Ueberschrift nach der Titelzeile. Sonst zoege eine gleich
    geformte Zeile aus dem Fliesstext ein Feld herein, das keins ist.
    """
    # ── Eingabe-Validierung ─────────────────────
    zeilen: list[str] = _zeilen_laden(Path(pfad), wurzel)

    # ── Verarbeitung ────────────────────────────
    felder: dict[str, str] = {}
    for nr, zeile in enumerate(zeilen, start=1):
        blank: str = zeile.strip()
        if blank.startswith("---"):
            break
        if nr > 1 and _UEBERSCHRIFT.match(zeile):
            break
        passung = _METAZEILE.match(blank)
        if passung:
            felder[passung.group("feld").strip()] = passung.group("wert").strip()

    # ── Ausgabe-Verifikation ────────────────────
    for feld, wert in felder.items():
        if not feld or not wert:
            meldung: str = (
                f"metadaten_lesen: leeres Feld oder leerer Wert in {pfad} — "
                f"{feld!r}: {wert!r}"
            )
            raise RuntimeError(meldung)

    return felder


def datei_suchen(verzeichnis: Path | str, wurzel: Path | str, muster: str) -> list[str]:
    """Sucht Dateien nach Namensmuster und gibt sortierte Pfade zurueck.

    Vorbedingung: `verzeichnis` liegt innerhalb der Wurzel und existiert,
    `muster` ist nicht leer.
    Nachbedingung: Sortierte Liste absoluter Pfade; jeder liegt innerhalb
    der Wurzel.
    Fehlerfaelle: leeres Muster, Verzeichnis ausserhalb der Wurzel oder
    nicht vorhanden (ValueError).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not muster.strip():
        meldung: str = f"datei_suchen: leeres Muster fuer {verzeichnis}"
        raise ValueError(meldung)

    ordner: Path = Path(verzeichnis).resolve(strict=False)
    wurzel_auf: Path = Path(wurzel).resolve(strict=False)

    if not ordner.is_relative_to(wurzel_auf):
        meldung = (
            f"datei_suchen: {ordner} liegt ausserhalb der Wurzel {wurzel_auf}"
        )
        raise ValueError(meldung)
    if not ordner.is_dir():
        meldung = f"datei_suchen: {ordner} ist kein Verzeichnis"
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    gefunden: list[str] = sorted(
        str(p) for p in ordner.rglob("*")
        if p.is_file() and fnmatch.fnmatch(p.name, muster)
    )

    # ── Ausgabe-Verifikation ────────────────────
    for eintrag in gefunden:
        if not Path(eintrag).resolve(strict=False).is_relative_to(wurzel_auf):
            meldung = (
                f"datei_suchen: Treffer {eintrag} liegt ausserhalb der Wurzel "
                f"{wurzel_auf} — vermutlich eine symbolische Verknuepfung"
            )
            raise RuntimeError(meldung)

    return gefunden
