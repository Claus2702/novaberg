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
    Fehlerfaelle: Fehlender Trenner, fehlende Felder oder ein Wert ausserhalb
        der Wertemenge fuehren zu `geliefert=False`; der Aufrufer meldet das
        laut. Kein Vorgabewert auf eine gueltige Bewertung: Ein geratenes
        Urteil waere von einem gefaellten nicht zu unterscheiden und wuerde in
        der Fallenbatterie als Messwert gezaehlt.

    Returns:
        (Einwandsurteil, Prosa). Bei Fehlschlag ein leeres Urteil und `roh`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not roh or not roh.strip():
        return Einwandsurteil(), ""

    # ── Verarbeitung ────────────────────────────
    # Der Trenner steht allein auf seiner Zeile. Ein `---` mitten in der Prosa
    # (Gedankenstrich, Tabelle) trifft das Muster deshalb nicht.
    teilung = re.split(rf"^\s*{re.escape(_TRENNER)}\s*$", roh, maxsplit=1, flags=re.M)
    if len(teilung) != 2:
        return Einwandsurteil(), roh.strip()

    kopf, prosa = teilung[0], teilung[1].strip()

    urteil: Einwandsurteil | None = _kopf_deuten(kopf)
    if urteil is None:
        return Einwandsurteil(), prosa or roh.strip()

    # ── Ausgabe-Verifikation ────────────────────
    # Ohne Prosa ist der Turn ohne Antwort. Das ist ein Ausfall, kein Urteil:
    # Ein Kopfblock allein ist nichts, was der Nutzer lesen kann.
    if not prosa:
        return Einwandsurteil(), ""

    return urteil, prosa


#: Die fuenf Feldnamen des Kopfblocks, in ihrer ASCII-Form.
_KOPFFELDER: frozenset[str] = frozenset(
    {"EINWAND", "GEPRUEFT", "BEWERTUNG", "STAERKE", "QUELLE"}
)

#: Umlaute auf ihre ASCII-Doppel. Der Prompt schreibt `GEPRUEFT` vor, das
#: Modell schreibt deutsch.
_UMLAUTE: dict[int, str] = str.maketrans({
    "Ä": "AE", "Ö": "OE", "Ü": "UE", "ä": "AE", "ö": "OE", "ü": "UE", "ß": "SS",
})


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


def _kopf_deuten(kopf: str) -> Einwandsurteil | None:
    """Liest die fuenf Felder aus dem Kopfblock und prueft sie gegen ihre Menge.

    Vorbedingung: `kopf` ist der Text vor der Trennlinie.
    Nachbedingung: Ein vollstaendiges Urteil, oder None, wenn ein Feld fehlt
        oder einen Wert ausserhalb seiner Menge traegt.
    Fehlerfaelle: None statt eines teilweise gefuellten Urteils. Ein halbes
        Urteil waere schlimmer als keines — es saehe gefaellt aus.
    """
    felder: dict[str, str] = {}
    for zeile in kopf.splitlines():
        treffer = re.match(r"^\s*([A-ZÄÖÜa-zäöü]+)\s*:\s*(.*)$", zeile.strip())
        if treffer:
            name: str = _feldname(treffer.group(1))
            if name in _KOPFFELDER:
                felder[name] = treffer.group(2).strip()

    if set(felder) != _KOPFFELDER:
        return None

    bewertung: str = felder["BEWERTUNG"].lower()
    quelle:    str = felder["QUELLE"].lower()
    einwand:   str = felder["EINWAND"].lower()
    if bewertung not in BEWERTUNGEN or quelle not in QUELLEN:
        return None
    if einwand not in ("ja", "nein"):
        return None

    try:
        staerke: float = float(felder["STAERKE"].replace(",", "."))
    except ValueError:
        return None
    if not 0.0 <= staerke <= 1.0:
        return None

    return Einwandsurteil(
        geliefert = True,
        vorhanden = einwand == "ja",
        geprueft  = felder["GEPRUEFT"],
        bewertung = bewertung,
        staerke   = staerke,
        quelle    = quelle,
    )
