"""Die Wanderung — was liegt draussen, was steht im Index, was fehlt.

Spezifikation: docs/novaberg-agent-dateien_k.md §5.1, §5.2, §5.5.

Dieses Modul entscheidet **nur die drei Faelle** und ruft dafuer kein
Modell. Es liest Dateinamen, Groessen, Zeiten und Pruefsummen — das ist
Rechenarbeit. Das Indizieren selbst steht in `indizieren.py` und kostet je
Datei einen Modellaufruf; die Trennung ist der Grund, warum die
Aenderungserkennung ueberhaupt lohnt.

**Kein Schreibpfad ins Dateisystem.** Auch dieses Modul importiert keinen.
"""

import hashlib
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from config import DATEIEN_INDEX_ENDUNGEN, DATEIEN_INDEX_MAX_BYTES

logger = logging.getLogger("ki_server.agents.dateien_index.wandern")

#: Die drei Faelle aus §5.1, als geschlossene Menge.
FALL_NEU: str = "neu"
FALL_GEAENDERT: str = "geaendert"
FALL_UNVERAENDERT: str = "unveraendert"
FAELLE: frozenset[str] = frozenset({FALL_NEU, FALL_GEAENDERT, FALL_UNVERAENDERT})

#: Die Werte der Spalte `dateien_index.grund` — der **letzte Uebergang** einer
#: Zeile, nicht das Urteil des laufenden Durchgangs. Englisch, weil sie neu
#: sind und innerhalb ihrer Spalte einsprachig bleiben; die Menge spiegelt den
#: CHECK-Riegel in `init.sql`, und wer hier einen Wert ergaenzt, ergaenzt ihn
#: dort auch — sonst weist die Datenbank den Schreibvorgang ab.
GRUND_ANGELEGT: str = "created"
GRUND_GEAENDERT: str = "changed"
GRUND_GELOESCHT: str = "deleted"
GRUND_AUSSERHALB: str = "excluded"
GRUENDE: frozenset[str] = frozenset({
    GRUND_ANGELEGT, GRUND_GEAENDERT, GRUND_GELOESCHT, GRUND_AUSSERHALB,
})

#: Die Zuordnung Fall → Grund fuer die beiden Faelle, die geschrieben werden.
#: `unveraendert` steht nicht darin: Ein Lauf ohne Uebergang ruehrt `grund`
#: und `grund_am` nicht an, damit sie sagen koennen, **seit wann** der
#: Zustand gilt.
GRUND_JE_FALL: dict[str, str] = {
    FALL_NEU: GRUND_ANGELEGT,
    FALL_GEAENDERT: GRUND_GEAENDERT,
}

#: Der Grund, aus dem ein Verzeichnis mit fuehrendem Punkt nicht betreten wird.
#: Er steht als Konstante da, weil ihn zwei Seiten brauchen — die Wanderung
#: schreibt ihn, der Zeuge prueft ihn — und eine frei getippte Zeichenkette an
#: zwei Stellen laeuft auseinander, ohne dass etwas rot wird.
GRUND_VERBORGENES_VERZEICHNIS: str = "Verzeichnis mit fuehrendem Punkt — nicht betreten"

#: Dasselbe fuer die Einzeldatei. Getrennt gehalten, weil die beiden Faelle
#: verschieden ausgehen: Das Verzeichnis wird gar nicht erst betreten, die
#: Datei wird gesehen und mit Grund uebergangen.
GRUND_VERBORGENE_DATEI: str = "verborgen (fuehrender Punkt)"


@dataclass(frozen=True)
class Fund:
    """Eine Datei auf der Platte, mit allem, was ohne Modell erhebbar ist."""

    pfad_relativ: str
    pfad_absolut: Path
    name: str
    groesse: int
    zeilen: int
    inhalt_hash: str
    geaendert_am: float
    fall: str


@dataclass
class Wanderung:
    """Das Ergebnis eines Laufs ueber eine Wurzel — vier Mengen und zwei Gruende.

    `uebergangen` traegt die Dateien, die **mit Grund** nicht indiziert
    werden. Sie sind kein Fehler und kein Leerfall: Eine PDF oder ein Bild
    ist eine Datei, die dieser Dienst nicht liest, und das gehoert gesagt
    statt verschwiegen (§9 Punkt 4).
    """

    neu: list[Fund] = field(default_factory=list)
    geaendert: list[Fund] = field(default_factory=list)
    unveraendert: list[Fund] = field(default_factory=list)
    verschwunden: list[dict] = field(default_factory=list)
    #: Zeilen des Bestands, deren Datei **dort liegt, wo sie lag**, die der
    #: Lauf aber nicht bewertet hat — weil ein Filter sie ausschliesst oder
    #: ihr Ast nicht betreten wurde. Sie stehen neben `verschwunden` und
    #: nicht darin, und das ist der ganze Punkt: *die Datei ist fort* und
    #: *wir sehen nicht mehr hin* sind zwei Auskuenfte, und nur die erste
    #: darf `wo war das noch` mit `sie ist weg` beantworten.
    ausserhalb: list[dict] = field(default_factory=list)
    uebergangen: list[tuple[str, str]] = field(default_factory=list)
    #: Verzeichnisse, in die der Lauf nicht abgestiegen ist — (Pfad, Grund).
    #: Sie stehen NEBEN `uebergangen` und nicht darin: Dort zaehlen Dateien,
    #: hier Verzeichnisse, und eine Zahl, die beides addiert, beantwortet
    #: keine der beiden Fragen. Ein abgeschnittener Ast ist auch kein
    #: Sonderfall des Uebergehens — die Dateien darunter hat niemand gesehen.
    uebergangene_verzeichnisse: list[tuple[str, str]] = field(default_factory=list)

    def zahlen(self) -> dict[str, int]:
        """Die Bilanz eines Laufs, in einer Zeile nachrechenbar."""
        return {
            "neu": len(self.neu),
            "geaendert": len(self.geaendert),
            "unveraendert": len(self.unveraendert),
            "verschwunden": len(self.verschwunden),
            "ausserhalb": len(self.ausserhalb),
            "uebergangen": len(self.uebergangen),
            "uebergangene_verzeichnisse": len(self.uebergangene_verzeichnisse),
        }


def _hash_und_zeilen(datei: Path) -> tuple[str, int]:
    """Liest eine Datei einmal und liefert Pruefsumme und Zeilenzahl.

    Vorbedingung: `datei` existiert und ist lesbar.
    Nachbedingung: (sha256-Hexwert, Zeilenzahl). Beides aus **einem** Lesen —
    zweimal zu lesen waere bei 667 Dateien der doppelte Durchsatz fuer eine
    Zahl, die dabei abfaellt.
    """
    roh: bytes = datei.read_bytes()
    # Die letzte Zeile zaehlt mit, auch wenn sie ohne Umbruch endet.
    zeilen: int = roh.count(b"\n") + (1 if roh and not roh.endswith(b"\n") else 0)
    return hashlib.sha256(roh).hexdigest(), zeilen


def _uebergehen(datei: Path, groesse: int) -> str:
    """Nennt den Grund, aus dem eine Datei nicht indiziert wird — oder nichts.

    Vorbedingung: `datei` existiert.
    Nachbedingung: Leerer Text heisst "wird indiziert". Sonst der Grund im
    Klartext, damit er in der Bilanz stehen kann.

    **Die Pruefung nennt den Grund und verschweigt die Datei nicht.** Ein
    stiller Uebersprung machte eine unlesbare Datei von einer nicht
    vorhandenen ununterscheidbar.
    """
    # Der Punkt steht vor der Endung, weil er die genauere Auskunft gibt:
    # `.DS_Store` mit "Endung ist kein Text" abzuweisen ist richtig und sagt
    # das Falsche — die Datei ist nicht wegen ihres Formats draussen, sondern
    # weil sie zur Werkzeugschicht gehoert und nicht zum Bestand.
    if datei.name.startswith("."):
        return GRUND_VERBORGENE_DATEI
    if datei.suffix.lower() not in DATEIEN_INDEX_ENDUNGEN:
        return f"Endung '{datei.suffix or '(keine)'}' ist kein Text"
    if groesse > DATEIEN_INDEX_MAX_BYTES:
        return f"{groesse} Bytes ueber der Grenze {DATEIEN_INDEX_MAX_BYTES}"
    if groesse == 0:
        return "leer"
    return ""


def _pruefen(
    absolut: Path, relativ: str, wurzel_aufgeloest: Path,
) -> tuple[os.stat_result | None, str]:
    """Entscheidet, ob eine gefundene Datei ueberhaupt verarbeitet wird.

    Vorbedingung: `absolut` stammt aus einem Lauf ueber `wurzel_aufgeloest`.
    Nachbedingung: Entweder (Dateizustand, "") oder (None, Grund). Genau
    eine der beiden Haelften traegt etwas — ein Grund ohne None waere ein
    stiller Durchlauf.

    **Die Randpruefung steht vor der Existenzpruefung**, wie am Aussenrand
    (§7 Regel 3c): Erst aufloesen, dann halten. `os.walk(followlinks=False)`
    sperrt den Abstieg in ein verlinktes Verzeichnis; eine verlinkte
    Einzeldatei steht danach trotzdem in der Liste.
    """
    aufgeloest: Path = absolut.resolve(strict=False)
    if not aufgeloest.is_relative_to(wurzel_aufgeloest):
        logger.error(
            "Waechter: '%s' zeigt auf '%s' und damit aus der Wurzel '%s' "
            "heraus — uebergangen", relativ, aufgeloest, wurzel_aufgeloest,
        )
        return None, f"zeigt aus der Wurzel heraus auf {aufgeloest}"

    try:
        zustand: os.stat_result = absolut.stat()
    except OSError as fehler:
        logger.exception(
            "Waechter: '%s' nicht lesbar (%s) — uebergangen",
            relativ, type(fehler).__name__,
        )
        return None, f"nicht lesbar: {fehler}"

    grund: str = _uebergehen(absolut, zustand.st_size)
    if grund:
        return None, grund

    return zustand, ""


def _fall_bestimmen(zeile: dict | None, pruefsumme: str) -> str:
    """Ordnet eine vorgefundene Datei ihrem Fall zu — und schliesst die Kette.

    Vorbedingung: `zeile` ist die Bestandszeile zu diesem Pfad oder None;
    `pruefsumme` ist der Hash der Datei, die gerade dort liegt.
    Nachbedingung: Einer der drei Faelle aus `FAELLE`.

    **Ein Grabstein mit anderem Inhalt ist eine Neuanlage, keine Aenderung.**
    Das ist der Fall, den die frueheren Fassungen nicht kannten: Wird `x`
    geloescht und spaeter ein anderes `x` angelegt, traegt die alte Zeile
    `grund = 'deleted'` und einen Hash, der nicht mehr passt. Als
    *geaendert* behandelt, setzte sie die Geschichte der geloeschten Datei
    fort — samt `entitaet_ids`, `timeline_id` und `zuletzt_gelernt_hash`,
    die der UPSERT nicht anfasst. Als *neu* behandelt, beginnt der Zyklus
    von vorn, und `zeile_schreiben` raeumt die drei Spalten.

    **Derselbe Hash ist dagegen dieselbe Datei**, gleich wie sie gegangen
    ist: Ein zurueckgenommener Filter oder eine wiederhergestellte Datei
    setzen fort, was sie waren.
    """
    if zeile is None:
        return FALL_NEU

    gleicher_inhalt: bool = zeile["inhalt_hash"] == pruefsumme
    if gleicher_inhalt and zeile.get("aktiv"):
        return FALL_UNVERAENDERT

    if (not zeile.get("aktiv")
            and zeile.get("grund") == GRUND_GELOESCHT
            and not gleicher_inhalt):
        return FALL_NEU

    return FALL_GEAENDERT


def _liegt_noch_da(wurzel_aufgeloest: Path, relativ: str) -> bool:
    """Sagt, ob die Datei zu einer Bestandszeile heute noch am Platz liegt.

    Vorbedingung: `relativ` stammt aus dem eigenen Index und ist damit ein
    Pfad unterhalb der Wurzel.
    Nachbedingung: True, wenn dort etwas liegt — auch wenn ein Filter es
    heute uebergeht. **Die Frage ist die Existenz, nicht die Eignung.**

    Der Aufloesungsschritt ist derselbe Riegel wie in `_pruefen`: Eine Zeile
    mit `..` im Pfad — wie auch immer sie entstanden waere — darf nicht
    dazu fuehren, dass hier ausserhalb der Wurzel nachgesehen wird.
    """
    absolut: Path = (wurzel_aufgeloest / relativ).resolve(strict=False)
    if not absolut.is_relative_to(wurzel_aufgeloest):
        logger.error(
            "Waechter: Bestandszeile '%s' zeigt aus der Wurzel heraus — als "
            "fort behandelt", relativ,
        )
        return False
    # `lexists`: Ein toter Zeiger ist kein Inhalt, aber er ist auch nicht
    # nichts — er liegt da und wird von `_pruefen` mit Grund abgewiesen.
    return os.path.lexists(absolut)


def _unbeantwortete_einordnen(
    ergebnis: Wanderung, bestand: dict[str, dict],
    gesehen: set[str], wurzel_aufgeloest: Path,
) -> None:
    """Teilt die Bestandszeilen, die der Lauf nicht bewertet hat, in zwei Mengen.

    Vorbedingung: `gesehen` traegt die relativen Pfade, die der Lauf
    bewertet hat; `ergebnis.verschwunden` und `.ausserhalb` sind leer.
    Nachbedingung: Jede **aktive** Bestandszeile, die nicht in `gesehen`
    steht, liegt danach in genau einer der beiden Mengen. Stillgelegte
    Zeilen bleiben unberuehrt — sie sind bereits beschieden.

    **Nicht gesehen ist nicht fort.** Der Lauf sieht nur, was innerhalb
    seines Auftrags liegt: Ein Punkt-Ast wird nicht betreten, eine fremde
    Endung nicht geoeffnet, eine zu grosse Datei nicht gelesen. Aus
    "diesmal nicht gesehen" auf "geloescht" zu schliessen, war der Defekt
    VERSCHWUNDEN-DURCH-FILTERWECHSEL — gemessen am 23.08.2026 traf er
    **fuenf** Klassen vorhandener Dateien, nicht die eine, die der Befund
    nannte.

    Die Unterscheidung braucht keinen Buchhaltungsapparat ueber die
    Filter, sondern die direkte Frage: **Liegt die Datei noch da?** Sie
    kostet einen Zugriff je unbeantworteter Bestandszeile — also nur fuer
    die, die der Lauf nicht ohnehin in der Hand hatte.
    """
    # ── Verarbeitung ────────────────────────────
    for pfad, zeile in bestand.items():
        if pfad in gesehen or not zeile.get("aktiv"):
            continue
        if _liegt_noch_da(wurzel_aufgeloest, pfad):
            ergebnis.ausserhalb.append(zeile)
        else:
            ergebnis.verschwunden.append(zeile)

    # ── Ausgabe-Verifikation ────────────────────
    offen: int = sum(
        1 for pfad, zeile in bestand.items()
        if pfad not in gesehen and zeile.get("aktiv")
    )
    beschieden: int = len(ergebnis.ausserhalb) + len(ergebnis.verschwunden)
    if beschieden != offen:
        logger.error(
            "Waechter: %d unbeantwortete Bestandszeilen, %d beschieden — eine "
            "Zeile steht weiter als vorhanden im Index", offen, beschieden,
        )


def wandern(wurzel: Path, bestand: dict[str, dict]) -> Wanderung:
    """Laeuft eine Wurzel ab und ordnet jede Datei einem der Faelle zu.

    Vorbedingung: `wurzel` ist ein aufgeloester, existierender, lesbarer
    Pfad — die Pruefung liegt beim Aufrufer (der Waechter haelt ihn gegen
    den Aussenrand). `bestand` bildet den relativen Pfad auf die
    Indexzeile ab.
    Nachbedingung: Eine `Wanderung`, in der **jede** gefundene Datei in
    genau einer Menge steht — indiziert oder mit Grund uebergangen. Aktive
    Zeilen des Bestands, die der Lauf nicht bewertet hat, stehen unter
    `verschwunden`, **wenn die Datei fort ist**, und sonst unter
    `ausserhalb`; die Probe darauf ist ein Blick auf die Platte und nicht
    die Buchfuehrung des Laufs.
    **Gefunden ist, was ausserhalb verborgener Verzeichnisse liegt:** Ein
    Verzeichnis mit fuehrendem Punkt wird nicht betreten und steht unter
    `uebergangene_verzeichnisse`; die Dateien darunter tauchen nirgends auf,
    weil sie niemand gesehen hat. Eine verborgene EINZELDATEI wird dagegen
    gesehen und wandert mit Grund nach `uebergangen`.

    **Jeder Pfad wird nach der Aufloesung gegen die Wurzel geprueft** — und
    zwar zusaetzlich zu `followlinks=False`. Die beiden decken verschiedene
    Faelle: `followlinks=False` verhindert den ABSTIEG in ein verlinktes
    Verzeichnis, eine verlinkte DATEI steht danach trotzdem in der Liste und
    wuerde voll verarbeitet.

    `[gemessen]` — 18.08.2026, von der zweiten Kontrolle hergestellt: Ein
    Zeiger `/files/zeiger.md` auf eine Datei ausserhalb wurde als `neu`
    eingeordnet, mit Groesse, Zeilenzahl und Pruefsumme der FREMDEN Datei.
    Die einzige Stelle, die es bemerkte, war `struktur_analysieren` — und ihr
    `ValueError` wird eine Ebene hoeher als "keine Blockstruktur" gefangen,
    was im Bestand der Normalfall ist. Der Randbruch sah aus wie eine Datei
    ohne Ueberschriften.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not wurzel.is_dir():
        logger.error(
            "Waechter: Wurzel '%s' ist kein Verzeichnis — Lauf uebersprungen", wurzel,
        )
        return Wanderung()

    wurzel_aufgeloest: Path = wurzel.resolve(strict=False)
    ergebnis = Wanderung()
    gesehen: set[str] = set()

    # ── Verarbeitung ────────────────────────────
    for ordner, unter, dateien in os.walk(wurzel, followlinks=False):
        # **Der Ast wird abgeschnitten, nicht Blatt fuer Blatt begruendet.**
        # Ein Verzeichnis mit fuehrendem Punkt ist Werkzeugschicht — eine
        # Editor-Einstellung, ein Zwischenspeicher, eine Arbeitskopie —, und
        # es traegt seinen Inhalt fuer ein Programm, nicht fuer einen Leser.
        # Der Abstieg kostet dort nicht nur Arbeit, er erzeugt in JEDEM Lauf
        # dieselbe Liste von Absagen: `.obsidian` allein stand am 20.08.2026
        # mit sechs Zeilen in der Bilanz, und keine davon wird je eine
        # andere. `os.walk` erlaubt die Kuerzung nur ueber die Liste selbst —
        # deshalb `unter[:]` und nicht `unter = `.
        verborgen: list[str] = [name for name in sorted(unter) if name.startswith(".")]
        for name in verborgen:
            relativ_verzeichnis: str = str((Path(ordner) / name).relative_to(wurzel))
            logger.info(
                "Waechter: '%s' nicht betreten — %s",
                relativ_verzeichnis, GRUND_VERBORGENES_VERZEICHNIS,
            )
            ergebnis.uebergangene_verzeichnisse.append(
                (relativ_verzeichnis, GRUND_VERBORGENES_VERZEICHNIS),
            )
        unter[:] = [name for name in unter if not name.startswith(".")]

        for dateiname in sorted(dateien):
            absolut: Path = Path(ordner) / dateiname
            relativ: str = str(absolut.relative_to(wurzel))

            zustand, grund = _pruefen(absolut, relativ, wurzel_aufgeloest)
            if zustand is None:
                ergebnis.uebergangen.append((relativ, grund))
                continue

            gesehen.add(relativ)
            zeile: dict | None = bestand.get(relativ)

            # **Jede Datei wird gehasht — es gibt keinen Vorfilter ueber Zeit
            # und Groesse.** Der erste Entwurf hatte einen; ein Zeuge hat ihn
            # widerlegt, und das Konzept nennt den Grund selbst zuerst: Ein
            # Werkzeug kann eine Datei mit gleicher Zeit und gleicher Groesse
            # neu schreiben (§5.2). Ein Vorfilter darauf laesst genau diese
            # Aenderung durch, und sie faellt danach nie wieder auf.
            #
            # Der Verzicht kostet fast nichts: Teuer ist der Modellaufruf je
            # geaenderter Datei, nicht das Lesen. Bei einer Obergrenze von
            # einem Megabyte je Datei ist das Hashen Ein-/Ausgabe von
            # Sekundenbruchteilen — die Stunden, von denen §5.2 spricht,
            # entstehen beim Indizieren und werden weiterhin vom Hash
            # bewacht.
            try:
                pruefsumme, zeilen = _hash_und_zeilen(absolut)
            except OSError as fehler:
                logger.exception(
                    "Waechter: '%s' nicht lesbar beim Hashen (%s) — uebergangen",
                    relativ, type(fehler).__name__,
                )
                ergebnis.uebergangen.append((relativ, f"nicht lesbar: {fehler}"))
                gesehen.discard(relativ)
                continue

            fall: str = _fall_bestimmen(zeile, pruefsumme)
            eintrag: Fund = _fund(
                relativ, absolut, zustand, (pruefsumme, zeilen), fall,
            )
            if fall == FALL_NEU:
                ergebnis.neu.append(eintrag)
            elif fall == FALL_GEAENDERT:
                ergebnis.geaendert.append(eintrag)
            else:
                ergebnis.unveraendert.append(eintrag)

    _unbeantwortete_einordnen(ergebnis, bestand, gesehen, wurzel_aufgeloest)

    # ── Ausgabe-Verifikation ────────────────────
    zahlen: dict[str, int] = ergebnis.zahlen()
    behandelt: int = zahlen["neu"] + zahlen["geaendert"] + zahlen["unveraendert"]
    if behandelt != len(gesehen):
        logger.error(
            "Waechter: %d Dateien gesehen, aber %d einsortiert — eine Datei "
            "faellt zwischen die Faelle", len(gesehen), behandelt,
        )

    logger.info(
        "Waechter: '%s' — neu %d, geaendert %d, unveraendert %d, "
        "verschwunden %d, ausserhalb %d, uebergangen %d, "
        "Verzeichnisse uebergangen %d",
        wurzel, zahlen["neu"], zahlen["geaendert"], zahlen["unveraendert"],
        zahlen["verschwunden"], zahlen["ausserhalb"], zahlen["uebergangen"],
        zahlen["uebergangene_verzeichnisse"],
    )
    return ergebnis


def _fund(relativ: str, absolut: Path, zustand: os.stat_result,
          inhalt: tuple[str, int], fall: str) -> Fund:
    """Baut einen Fund aus dem, was ohne Modellaufruf feststeht.

    `inhalt` ist das Paar aus `_hash_und_zeilen` — Pruefsumme und
    Zeilenzahl stammen aus **einem** Lesen und reisen deshalb zusammen.
    """
    pruefsumme, zeilen = inhalt
    return Fund(
        pfad_relativ=relativ,
        pfad_absolut=absolut,
        name=absolut.name,
        groesse=zustand.st_size,
        zeilen=zeilen,
        inhalt_hash=pruefsumme,
        geaendert_am=zustand.st_mtime,
        fall=fall,
    )
