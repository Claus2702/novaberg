"""Das Urteil des Verfassers ueber einen Einwand des Nutzers.

Bauteil B1 des Sykophanz-Sprints (`novaberg-sykophanz-eindaemmung_k.md` §7).

**Warum das Urteil vor dem Text steht.** Ein Sprachmodell legt sich mit dem
ersten Token fest. Die gemessenen Ausfaelle *beginnen* mit der Zustimmung —
danach ist der Rest der Antwort deren Begruendung. Steht die Pruefung vor dem
Urteil und das Urteil vor dem Text, kann die Zustimmung nicht mehr vor der
Pruefung fallen. Ein Satz in Prosa laesst sich weichspuelen, ein
Aufzaehlungswert nicht.

**Warum ein Kopfblock und kein JSON.** Der Verfasser liefert Prosa, gemessen
bis ueber 3800 Zeichen. In JSON gepresst haengt der ganze Turn daran, dass das
Modell einen langen Freitext fehlerfrei maskiert — und dieser Ausfall ist im
Bestand belegt: Die Salienz-Bewertung scheitert an LaTeX in der Modellantwort,
`expect_json` wirft dann, und es gaebe weder Urteil noch Antwort. Der Kopfblock
haelt die Prosa aus dem Parser heraus; misslingt er, ist nur das Urteil weg,
nicht die Antwort.

**Was hier NICHT steht:** die Ausbausperre. Sie ist eine Anweisung an das
Modell und lebt im Prompt; hier steht nur, was zurueckkommt.

**Geltungsgrenze:** Auf dem Aufgabenpfad laeuft der Verfasser nicht
(`novaberg-node-verfasser_k.md` §5.1) — dort entsteht kein Urteil, und das ist
keine Luecke dieses Moduls, sondern eine des Pfades.
"""

import re
from dataclasses import dataclass

from utils.canon import UMLAUT_MAP

# ── Die einzige Quelle der gueltigen Werte ──────────────────────
#
# Sie stehen hier und NUR hier. Der Prompt bekommt sie zur Laufzeit eingesetzt
# (siehe `KOPF_ANWEISUNG`), statt sie ein zweites Mal auszuschreiben: Zwei
# Stellen, die dieselbe Werteliste fuehren, driften auch dann, wenn heute
# niemand die zweite liest.

BEWERTUNGEN: tuple[str, ...] = ("trifft_zu", "trifft_nicht_zu", "abweichend")
# trifft_zu       — der Einwand des Nutzers ist richtig
# trifft_nicht_zu — der Einwand ist falsch
# abweichend      — der Nutzer widerspricht seiner eigenen frueheren Angabe;
#                   wer recht hat, ist damit nicht entschieden

QUELLEN: tuple[str, ...] = ("fakt", "haltung", "beides")
# Woran der Einwand haengt. Steht heute immer auf `fakt` — die Haltungsseite
# ist nicht gebaut (`novaberg-thinking-opinion_k.md` §2). Das Feld ist
# trotzdem von Anfang an dabei, damit der Willensstrang es spaeter ohne
# Migration mitbenutzen kann.

_TRENNER: str = "---"

#: Die Gruende, aus denen `urteil_lesen` kein Urteil liefert. Benannt, damit
#: jeder Ausfall im Log eine Ursache traegt und nicht nur eine Sammelzeile —
#: aus einer Sammelzeile laesst sich nicht zaehlen, woran der Kopfblock
#: scheitert. Die drei Feldgruende tragen den Feldnamen hinter einem
#: Doppelpunkt (`wert_ausserhalb:EINWAND`).
AUSFALLGRUENDE: tuple[str, ...] = (
    "antwort_leer",          # die Modellantwort ist leer
    "trenner_fehlt",         # keine Zeile, die nur die Trennlinie traegt
    "feld_fehlt",            # ein Feld des Kopfblocks fehlt, mit Feldnamen
    "wert_ausserhalb",       # das erste Wort ist kein Wert der Menge, mit Feldnamen
    "mehrdeutig",            # mehr als ein Wert der Menge im Feld, gleich wo, mit Feldnamen
    "staerke_keine_zahl",    # STAERKE beginnt nicht mit einer Zahl
    "staerke_ausserhalb",    # STAERKE liegt nicht zwischen 0.0 und 1.0
    "prosa_fehlt",           # nach der Trennlinie steht nichts
)


@dataclass
class Einwandsurteil:
    """Was der Verfasser ueber einen Einwand des Nutzers geurteilt hat.

    Reiner Datencontainer. Erzeugt wird er aus dem Kopfblock der
    Modellantwort (`urteil_lesen`), gelesen von der Vorzeichenpruefung (B4)
    und der Vorzeichenregel des Responders (B3).

    **Die Defaults sind als Defaults erkennbar.** `geliefert=False` mit
    durchgehend `None` heisst „das Modell hat kein Urteil abgegeben" — nicht
    „es hat keinen Einwand gesehen". Ohne diese Unterscheidung waere ein
    ausgefallener Kopfblock von einem unstrittigen Turn nicht zu trennen, und
    die Rate aus der Fallenbatterie zaehlte Ausfaelle als Erfolge.
    """

    geliefert: bool = False
    # Kam ein lesbarer Kopfblock zurueck? Begleitfeld zu allen anderen:
    # Ist es False, sagen die uebrigen Felder nichts aus.

    vorhanden: bool | None = None
    # Enthaelt die Nutzeraeusserung ueberhaupt einen Einwand?
    # None = nicht geliefert.

    geprueft: str = ""
    # Die Pruefung in einem Satz, in Prosa. Steht VOR der Bewertung, damit das
    # Modell erst hinsieht und dann urteilt. Leer = nicht geliefert.

    bewertung: str | None = None
    # Einer aus BEWERTUNGEN. None = nicht geliefert oder unbekannter Wert.
    # Dieser Wert traegt die Ausbausperre — er ist der diskrete Teil des
    # Urteils und bleibt maschinell pruefbar.

    staerke: float | None = None
    # Wie deutlich der Vorbehalt klingen soll, 0.0 bis 1.0.
    # 0.0 = kaum hoerbar, 1.0 = unmissverstaendlich.
    # Beschreibt nur den Ton; sie entscheidet nichts. Eine Fliesskommazahl ist
    # weicher als Prosa, nicht haerter — die Sperre haengt am
    # Aufzaehlungswert, nicht an ihr.

    quelle: str | None = None
    # Einer aus QUELLEN. None = nicht geliefert oder unbekannter Wert.

    ausfall: str | None = None
    # Warum kein Urteil geliefert wurde: ein Grund aus AUSFALLGRUENDE, bei
    # den Feldgruenden mit `:<FELD>`. Gesetzt bei jedem `geliefert=False` aus
    # `urteil_lesen`; None bei einem gefaellten Urteil und bei der
    # Vorbelegung, die nie gelesen wurde.


def kopf_anweisung() -> str:
    """Baut den Prompt-Abschnitt, der den Kopfblock verlangt.

    Die gueltigen Werte werden aus `BEWERTUNGEN` und `QUELLEN` eingesetzt, nicht
    im Prompttext wiederholt — sonst gaebe es zwei Orte fuer dieselbe Liste.

    Vorbedingung: keine.
    Nachbedingung: Ein Textblock, der Reihenfolge, Feldnamen und Wertemenge
        nennt und mit der Trennlinie endet.
    Fehlerfaelle: keine.
    """
    return (
        "[URTEIL VOR DEM TEXT]\n"
        "Beginne JEDE Antwort mit genau diesen fuenf Zeilen, in dieser\n"
        "Reihenfolge, danach eine Zeile mit " + _TRENNER + " und erst dann der\n"
        "Inhalt selbst:\n\n"
        "EINWAND: ja oder nein — widerspricht PERSON B etwas, das frueher\n"
        "  gesagt wurde, oder etwas Nachpruefbarem?\n"
        "GEPRUEFT: ein Satz. Was stand frueher da, was steht jetzt da?\n"
        "BEWERTUNG: " + " oder ".join(BEWERTUNGEN) + "\n"
        "STAERKE: eine Zahl zwischen 0.0 und 1.0 — wie deutlich der Vorbehalt\n"
        "  klingen soll. Sie steuert nur den Ton.\n"
        "QUELLE: " + " oder ".join(QUELLEN) + "\n"
        + _TRENNER + "\n\n"
        "Pruefe, bevor du urteilst, und urteile, bevor du schreibst. Die\n"
        "Reihenfolge ist der Zweck: Wer erst zustimmt und dann prueft, hat\n"
        "sich schon festgelegt.\n\n"
        "Bei BEWERTUNG: abweichend gilt fuer den Inhalt danach:\n"
        "Der abweichende Wert darf ZITIERT werden — „Person B nennt jetzt\n"
        "800k\" — aber er wird NICHT Grundlage einer Ableitung. Keine\n"
        "Empfehlung, keine Folgerung, keine Handlungsanweisung, die auf ihm\n"
        "steht. „Damit hat sie einen Anker\" ist verboten, auch wenn der\n"
        "Vorbehalt danebensteht. Ein Gebaeude auf einem falschen Wert\n"
        "ueberlebt jede spaetere Korrektur des Werts."
    )


def urteil_lesen(roh: str) -> tuple[Einwandsurteil, str]:
    """Trennt den Kopfblock von der Prosa und liest das Urteil.

    Vorbedingung: `roh` ist die ungekuerzte Modellantwort.
    Nachbedingung: Tupel (Urteil, Prosa). Die Prosa ist immer das, was der
        Nutzer lesen soll — auch wenn der Kopfblock fehlt oder unbrauchbar
        ist. **Ein misslungener Kopfblock kostet das Urteil, nicht die
        Antwort.**
    Fehlerfaelle: Fehlender Trenner, fehlende Felder, ein erstes Wort
        ausserhalb der Wertemenge, eine wiederholte Wertliste oder eine
        unbrauchbare Staerke fuehren zu
        `geliefert=False` mit einem Grund aus `AUSFALLGRUENDE` in `ausfall`;
        der Aufrufer meldet das laut. Kein Vorgabewert auf eine gueltige
        Bewertung: Ein geratenes Urteil waere von einem gefaellten nicht zu
        unterscheiden und wuerde in der Fallenbatterie als Messwert gezaehlt.

    Returns:
        (Einwandsurteil, Prosa). Bei Fehlschlag ein leeres Urteil mit Grund
        und `roh`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not roh or not roh.strip():
        return _ausfall("antwort_leer"), ""

    # ── Verarbeitung ────────────────────────────
    # Der Trenner steht allein auf seiner Zeile. Ein `---` mitten in der Prosa
    # (Gedankenstrich, Tabelle) trifft das Muster deshalb nicht.
    teilung = re.split(rf"^\s*{re.escape(_TRENNER)}\s*$", roh, maxsplit=1, flags=re.M)
    if len(teilung) != 2:
        return _ausfall("trenner_fehlt"), roh.strip()

    kopf, prosa = teilung[0], teilung[1].strip()

    urteil: Einwandsurteil = _kopf_deuten(kopf)
    if not urteil.geliefert:
        return urteil, prosa or roh.strip()

    # ── Ausgabe-Verifikation ────────────────────
    # Ohne Prosa ist der Turn ohne Antwort. Das ist ein Ausfall, kein Urteil:
    # Ein Kopfblock allein ist nichts, was der Nutzer lesen kann.
    if not prosa:
        return _ausfall("prosa_fehlt"), ""

    return urteil, prosa


#: Die fuenf Feldnamen des Kopfblocks, in ihrer ASCII-Form.
_KOPFFELDER: frozenset[str] = frozenset(
    {"EINWAND", "GEPRUEFT", "BEWERTUNG", "STAERKE", "QUELLE"}
)

#: Umlaute auf ihre ASCII-Doppel. Der Prompt schreibt `GEPRUEFT` vor, das
#: Modell schreibt deutsch.
#:
#: **Die Abbildung steht seit dem 05.09.2026 in `utils/canon.py`** und wird
#: hier nur noch geholt. Zwei Tabellen fuer dieselbe Sache laufen auseinander,
#: sobald eine von beiden ein Zeichen dazubekommt — und die Abweichung faellt
#: an genau der Stelle auf, an der sie teuer ist.
_UMLAUTE: dict[int, str] = UMLAUT_MAP


def _feldname(roh: str) -> str:
    """Bringt einen Feldnamen des Kopfblocks auf seine ASCII-Form.

    **Warum das noetig ist, und es ist gemessen.** Der Prompt verlangt
    `GEPRUEFT` und `STAERKE`; das Modell schreibt die deutschen Formen
    `GEPRÜFT` und `STÄRKE`. Ein Feldname ausserhalb der erwarteten Menge
    liess `_kopf_deuten` bis zum 22.08.2026 das **ganze** Urteil verwerfen —
    ein Umlaut kostete alle fuenf Felder.

    `[gemessen]` — 22.08.2026 ueber 36 Stunden Betriebslog: Von fuenf echten
    Ausfaellen des Kopfblocks trugen **vier** `GEPRÜFT` mit Umlaut.

    Vorbedingung: `roh` ist der Text links vom Doppelpunkt.
    Nachbedingung: derselbe Name in Grossbuchstaben, Umlaute aufgeloest.
        Unbekannte Namen kommen unveraendert zurueck und werden vom Aufrufer
        verworfen — diese Funktion entscheidet nicht, was ein Feld ist.
    """
    return roh.upper().translate(_UMLAUTE)


#: Die fuenf Feldnamen in der Reihenfolge des Prompts. Danach richtet sich,
#: welcher Ausfall gemeldet wird, wenn mehrere Felder unbrauchbar sind.
_FELDREIHENFOLGE: tuple[str, ...] = ("EINWAND", "GEPRUEFT", "BEWERTUNG", "STAERKE", "QUELLE")

#: Die Werte von EINWAND. Der Prompt schreibt sie als „ja oder nein“ aus.
_EINWAND_WERTE: tuple[str, ...] = ("ja", "nein")

#: Das erste Wort eines Feldwerts: fuehrende Satzzeichen, Gedankenstriche und
#: Anfuehrungszeichen fallen weg, dann zaehlt die Folge von Wortzeichen. Der
#: Unterstrich gehoert zum Wort, sonst zerfiele `trifft_zu` in zwei.
_ERSTES_WORT: re.Pattern[str] = re.compile(r"^\W*(\w+)")

#: Die Zahl am Anfang von STAERKE. Fuehrend nur Leerraum und
#: Anfuehrungszeichen — ein Minus wird nicht abgeschnitten, sonst wuerde -0.3
#: als 0.3 gelesen. Dahinter darf kein Wortzeichen und keine weitere
#: Dezimalstelle folgen (`0.3abc`, `0.3.5`, `1e-1` sind keine Zahl).
_STAERKE_ZAHL: re.Pattern[str] = re.compile(
    r"^[\s\"'„“”‚‘’»«*]*([+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+))(?!\w|[.,]\d)"
)


def _ausfall(grund: str, feld: str | None = None) -> Einwandsurteil:
    """Baut das leere Urteil eines Ausfalls mit seinem benannten Grund.

    Vorbedingung: `grund` steht in `AUSFALLGRUENDE`; `feld` ist ein Feldname
        des Kopfblocks oder eine Komma-Liste davon, oder None.
    Nachbedingung: `geliefert=False`, alle Urteilsfelder unbesetzt, `ausfall`
        traegt `grund` oder `grund:feld`.
    Fehlerfaelle: Ein Grund ausserhalb der Menge ist ein Programmierfehler und
        wirft — ein unbenannter Grund waere die Sammelzeile, die er ersetzt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if grund not in AUSFALLGRUENDE:
        raise ValueError(f"Einwandsurteil: unbenannter Ausfallgrund {grund!r}")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    urteil: Einwandsurteil = Einwandsurteil(ausfall=f"{grund}:{feld}" if feld else grund)

    # ── Ausgabe-Verifikation ────────────────────
    # Ein Ausfall, der als geliefert gilt, saehe gefaellt aus.
    if urteil.geliefert:
        raise ValueError(f"Einwandsurteil: Ausfall {grund!r} gilt als geliefert")  # noqa: TRY003
    return urteil


def _aufzaehlung_lesen(wert: str, menge: tuple[str, ...]) -> tuple[str | None, str | None]:
    """Liest das erste Wort eines Aufzaehlungsfelds und prueft es gegen seine Menge.

    **Warum nur das erste Wort.** Der Prompt formuliert EINWAND als Frage, und
    das Modell schreibt die Erlaeuterung hinter den Wert: `nein — widerspricht
    PERSON B nichts.` Verlangt war bis dahin der nackte Wert, und das ganze
    Urteil fiel aus. Gelesen wird der Rest der Zeile nicht — ein Wert, der
    erst in der Mitte steht, ist keine Antwort auf das Feld. Gezaehlt wird er
    (unten).

    **Warum zwei Werte keine Antwort sind.** Nennt das Feld mehr als einen
    verschiedenen Wert seiner Menge — meist, weil das Modell die Vorlage
    wiederholt (`ja oder nein — …`, `fakt / haltung / beides`) —, ist das
    erste Wort zwar ein Wert, aber keine Entscheidung: Es steht nur vorn, weil
    die Vorlage es vorn fuehrt. Gelesen gaebe es ein Urteil aus einer
    Nicht-Antwort. Gezaehlt wird deshalb die Menge, nicht der Trenner:
    `ja oder nein`, `ja/nein`, `**ja** oder **nein**` und `nein — oder ja?`
    sind gleich mehrdeutig; jede Aufzaehlung von Trennern liesse den naechsten
    durch. Ein Wert zaehlt als ganzes Wort, ohne Gross- und Kleinschreibung —
    `abweichender` ist nicht `abweichend`. Derselbe Wert zweimal (`ja oder
    ja`) ist ein Wert.

    **Warum die Mehrdeutigkeit vor dem ersten Wort geprueft wird.** Sie
    beschreibt das ganze Feld, das erste Wort nur seinen Anfang: Bei
    `entweder ja oder nein` ist die Ursache das Echo, nicht das Wort
    `entweder`, und der Grund soll die Ursache nennen.

    Vorbedingung: `wert` ist der Text rechts vom Doppelpunkt; `menge` ist die
        nicht leere Wertemenge des Felds, kleingeschrieben.
    Nachbedingung: (Wert, None) mit einem Wert aus `menge`, sonst (None, Grund)
        mit `mehrdeutig` oder `wert_ausserhalb`. `neinsagen` ist nicht `nein` —
        ein Wort, das einen Wert nur enthaelt, ist nicht der Wert. Ein Wert
        einer anderen Menge (`nein oder fakt` bei EINWAND) zaehlt nicht.
    Fehlerfaelle: als Grund zurueckgegeben, nie geworfen — ein unbrauchbarer
        Wert ist eine erwartete Modellausgabe. Ein Feldwert, der kein Text
        ist, oder eine leere Menge ist ein Programmierfehler und wirft; ebenso
        ein gelesenes erstes Wort, das die Zaehlung nicht findet.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(wert, str):
        raise TypeError(f"Einwandsurteil: Feldwert {type(wert).__name__}")  # noqa: TRY003
    if not menge:
        raise ValueError("Einwandsurteil: leere Wertemenge")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    treffer: re.Match[str] | None = _ERSTES_WORT.match(wert)
    wort: str = treffer.group(1).lower() if treffer else ""
    genannt: set[str] = {
        kandidat for kandidat in menge
        if re.search(rf"(?<!\w){re.escape(kandidat)}(?!\w)", wert, re.IGNORECASE)
    }

    # ── Ausgabe-Verifikation ────────────────────
    if len(genannt) > 1:
        return None, "mehrdeutig"
    if wort not in menge:
        return None, "wert_ausserhalb"
    # Das erste Wort ist ein ganzes Wort; fehlt es in der Zaehlung, lesen
    # beide Wege nach verschiedenen Regeln.
    if wort not in genannt:
        raise RuntimeError(f"Einwandsurteil: {wort!r} gelesen, aber nicht gezaehlt")  # noqa: TRY003
    return wort, None


def _staerke_lesen(wert: str) -> tuple[float | None, str | None]:
    """Liest die Zahl am Anfang von STAERKE und prueft sie gegen 0.0 bis 1.0.

    **Dasselbe Kriterium wie bei den Aufzaehlungsfeldern.** Der Prompt erklaert
    auch STAERKE hinter einem Gedankenstrich; schreibt das Modell `0.3 — leise`,
    zaehlt die Zahl, der Rest wird verworfen. Streng bleibt die Zahl selbst:
    Komma oder Punkt als Dezimaltrenner, kein Exponent, nichts ausserhalb der
    Spanne.

    Vorbedingung: `wert` ist der Text rechts vom Doppelpunkt.
    Nachbedingung: (Staerke, None) bei einer Zahl in [0.0, 1.0], sonst
        (None, Grund) mit `staerke_keine_zahl` oder `staerke_ausserhalb`.
    Fehlerfaelle: als Grund zurueckgegeben, nie geworfen — eine unbrauchbare
        Staerke ist eine erwartete Modellausgabe.
    """
    # ── Eingabe-Validierung ─────────────────────
    treffer: re.Match[str] | None = _STAERKE_ZAHL.match(wert)
    if treffer is None:
        return None, "staerke_keine_zahl"

    # ── Verarbeitung ────────────────────────────
    staerke: float = float(treffer.group(1).replace(",", "."))

    # ── Ausgabe-Verifikation ────────────────────
    if not 0.0 <= staerke <= 1.0:
        return None, "staerke_ausserhalb"
    return staerke, None


def _kopf_deuten(kopf: str) -> Einwandsurteil:
    """Liest die fuenf Felder aus dem Kopfblock und prueft sie gegen ihre Menge.

    Gelesen wird je Aufzaehlungsfeld das erste Wort (`_aufzaehlung_lesen`),
    bei STAERKE die erste Zahl (`_staerke_lesen`); die Erlaeuterung dahinter
    zaehlt nicht, ein Feld mit mehr als einem Wert seiner Menge ist ein Ausfall.

    Vorbedingung: `kopf` ist der Text vor der Trennlinie.
    Nachbedingung: Ein vollstaendiges Urteil ohne `ausfall`, oder ein Ausfall
        mit dem Grund des ersten unbrauchbaren Felds in Prompt-Reihenfolge.
    Fehlerfaelle: Ausfall statt eines teilweise gefuellten Urteils. Ein halbes
        Urteil waere schlimmer als keines — es saehe gefaellt aus.
    """
    # ── Eingabe-Validierung ─────────────────────
    felder: dict[str, str] = {}
    for zeile in kopf.splitlines():
        treffer = re.match(r"^\s*([A-ZÄÖÜa-zäöü]+)\s*:\s*(.*)$", zeile.strip())
        if treffer and _feldname(treffer.group(1)) in _KOPFFELDER:
            felder[_feldname(treffer.group(1))] = treffer.group(2).strip()

    fehlend: list[str] = [name for name in _FELDREIHENFOLGE if name not in felder]
    if fehlend:
        return _ausfall("feld_fehlt", ",".join(fehlend))

    # ── Verarbeitung ────────────────────────────
    einwand, einwand_grund = _aufzaehlung_lesen(felder["EINWAND"], _EINWAND_WERTE)
    bewertung, bewertung_grund = _aufzaehlung_lesen(felder["BEWERTUNG"], BEWERTUNGEN)
    staerke, staerke_grund = _staerke_lesen(felder["STAERKE"])
    quelle, quelle_grund = _aufzaehlung_lesen(felder["QUELLE"], QUELLEN)

    # ── Ausgabe-Verifikation ────────────────────
    # Jedes Feld traegt das Urteil mit; ein einziges unbrauchbares verwirft es
    # ganz. Gemeldet wird das erste in Prompt-Reihenfolge, gleich, in welcher
    # Lage das Modell die Zeilen schrieb.
    gruende: tuple[tuple[str | None, str | None], ...] = (
        (einwand_grund,   "EINWAND"),
        (bewertung_grund, "BEWERTUNG"),
        (staerke_grund,   None),
        (quelle_grund,    "QUELLE"),
    )
    for grund, feld in gruende:
        if grund is not None:
            return _ausfall(grund, feld)

    return Einwandsurteil(
        geliefert = True,
        vorhanden = einwand == "ja",
        geprueft  = felder["GEPRUEFT"],
        bewertung = bewertung,
        staerke   = staerke,
        quelle    = quelle,
    )
