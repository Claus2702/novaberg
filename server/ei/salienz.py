"""
Salienz-Formel — was eine Aeusserung Novas erinnerungswuerdig macht.

    salienz_effektiv  = max( salienz_human × nutzer_gewichtung , salienz_charakter )
    salienz_charakter = max( antriebe ) × (1 + erregungs_zuschlag)

Zwei Gruende, sich etwas zu merken, und es genuegt einer — deshalb max() und
keine Summe. Eine Summe hoebe ein Segment, das beide Pfade schwach beruehrt,
ueber eines, das einen davon voll trifft.

Konzept: novaberg-salienz-berechnung_k.md §§2-4. Bauteile mit ZIEL/TEST/
MESSUNG: novaberg-kzg-salienz_k.md §11, Bauteil 1b.

Zur Bauart — warum hier nirgends ein nackter Multiplikator steht:
Ein Faktor darf nur so viel Einfluss auf das Ergebnis haben, wie seine Skala
ihm zugesteht. Ein Verstaerker, der eigentlich modulieren soll, aber als
blosser Multiplikator vor dem Ergebnis steht, kann es allein auf null ziehen —
und ein unnormierter Antrieb kann es allein saettigen. Beides ist derselbe
Fehler. Deshalb:

  - Die Antriebe stehen in einem max(), nicht in einem Produkt. Ein Antrieb,
    der gerade nichts beitraegt, loescht die uebrigen nicht aus.
  - Der Erregungs-Zuschlag wirkt als (1 + z) mit z >= 0. Er hebt, er kann nie
    ausloeschen.
  - Die Gewichtung liegt in [RAD_MIN, RAD_MAX] und enthaelt die Null nicht.

Wird die Salienz am Ende null, dann weil alle Gruende null waren — nicht,
weil ein einzelner Faktor sie umgelegt hat.
"""

import logging
from dataclasses import dataclass, field

from config import (
    RAD_MIN,
    RAD_MAX,
    SALIENZ_EREGUNG_MAX_ZUSCHLAG,
)

logger = logging.getLogger("ki_server.ei.salienz")


# Antriebe des Eigen-Pfads, die das Konzept vorsieht, die aber heute keinen
# Wert liefern. Sie stehen als Namen hier und wandern in jedes Ergebnis, damit
# im Log sichtbar ist, dass der Eigen-Pfad auf zwei von vier Beinen laeuft.
# Ohne diese Liste saehe ein max() ueber zwei Antriebe genauso aus wie eines
# ueber vier, und die Luecke waere unbeobachtbar.
ANTRIEBE_NICHT_ANGESCHLOSSEN: tuple[str, ...] = (
    "emotionale_gravitation",   # gebaut, aber unnormiert (Werte weit ueber 1.0)
    "neugier",                  # Rueckkopplung Wissensluecken -> Neugier fehlt
)


@dataclass
class SalienzErgebnis:
    """Das Ergebnis der Salienz-Formel samt seiner Herkunft.

    Traegt nicht nur die Zahl, sondern beide Operanden und den Gewinner: Ohne
    sie waere im Nachhinein nicht feststellbar, ob ein Segment erinnert wurde,
    weil es Nova etwas bedeutete oder weil es dem Nutzer etwas bedeutete. Genau
    diese Frage ist der Zweck der ganzen Formel.
    """

    effektiv: float
    # Der Wert, der ueber Erinnern entscheidet, 0.0-1.0.

    pflicht_pfad: float | None
    # salienz_human × nutzer_gewichtung — sein Interesse, durch ihren Charakter
    # gewichtet. None heisst: keine Nutzeraeusserung vorhanden (AgentGraph,
    # eigener Impuls). Das ist NICHT dasselbe wie 0.0 ("gesagt, aber belanglos").

    eigen_pfad: float
    # max(antriebe) × (1 + erregungs_zuschlag) — ihr eigener Antrieb.

    gewinner: str
    # "pflicht" | "eigen" | "gleichstand"

    antriebe: dict[str, float] = field(default_factory=dict)
    # Die angeschlossenen Antriebe mit ihren Werten, benannt. Nicht die Anzahl:
    # Eine Zeile, die nur zaehlt, macht ihre Frage unbeobachtbar.

    nicht_angeschlossen: tuple[str, ...] = ANTRIEBE_NICHT_ANGESCHLOSSEN
    # Die Antriebe, die das Konzept vorsieht und die heute schweigen.

    erregungs_zuschlag: float = 0.0
    # 0.0-0.3, wirkt als (1 + z).

    gekappt: bool = False
    # True, wenn das Ergebnis die Skalenobergrenze 1.0 ueberschritten hatte.


def _erregungs_zuschlag_berechnen(arousal: float) -> float:
    """Rechnet Novas Erregung in einen Verstaerkungs-Zuschlag um.

    Linear auf [0, SALIENZ_EREGUNG_MAX_ZUSCHLAG]. Bewusst linear und bewusst
    gedeckelt: Erregung hebt eine bedeutsame Aussage, macht aus einer
    belanglosen aber keine bedeutsame. Ein ungedeckelter Zuschlag truege jeden
    Ausruf ins Langzeitgedaechtnis.

    Vorbedingung: arousal ist die gemessene Erregung, 0.0-1.0.
    Nachbedingung: Rueckgabe in [0.0, SALIENZ_EREGUNG_MAX_ZUSCHLAG].
    Fehlerfaelle: Werte ausserhalb [0,1] werden gekappt und benannt.
    """

    # ── Eingabe-Validierung ─────────────────────
    if not 0.0 <= arousal <= 1.0:
        logger.warning(
            f"Salienz-Formel: arousal {arousal:.3f} ausserhalb [0,1] — gekappt"
        )
        arousal = max(0.0, min(1.0, arousal))

    # ── Verarbeitung / Ausgabe ──────────────────
    return arousal * SALIENZ_EREGUNG_MAX_ZUSCHLAG


def salienz_effektiv_berechnen(
    sprachlich:        float,
    ziel_gravitation:  float,
    arousal:           float,
    salienz_human:     float | None,
    nutzer_gewichtung: float | None,
) -> SalienzErgebnis:
    """Berechnet die Salienz eines Segments aus Novas Aeusserung.

    Args:
        sprachlich: Die Lesung dieses Segments — der einzige Antrieb, der heute
            je Segment verschieden ausfaellt. Alle uebrigen Groessen sind
            turnweit; ohne ihn bekaemen alle Segmente eines Turns denselben
            Wert, was genau das Symptom von SALIENZ-PROMPT-NUTZER-SCHABLONE
            waere.
        ziel_gravitation: Zug der aktiven Ziele auf diesen Turn, 0.0-1.0.
        arousal: Novas gemessene Erregung, 0.0-1.0.
        salienz_human: Salienz der Nutzeraeusserung desselben Turns, oder None,
            wenn es keine gab.
        nutzer_gewichtung: Faktor des Charakter-Rads, oder None, wenn er nicht
            gelesen werden konnte.

    Vorbedingung: sprachlich und ziel_gravitation sind nicht negativ.
    Nachbedingung: effektiv liegt in [0.0, 1.0]; gewinner benennt den Pfad, aus
        dem der Wert stammt.
    Fehlerfaelle: fehlender Pflicht-Pfad (salienz_human oder Gewichtung None) —
        das Ergebnis faellt auf den Eigen-Pfad zusammen, pflicht_pfad bleibt
        None. Das ist kein Fehler, sondern der dokumentierte Fall des
        AgentGraphen; der Aufrufer entscheidet, ob er ihn erwartet hat.
    """

    # ── Eingabe-Validierung ─────────────────────
    if sprachlich < 0.0:
        logger.warning(f"Salienz-Formel: sprachlich {sprachlich:.3f} negativ — auf 0.0 gesetzt")
        sprachlich = 0.0

    if ziel_gravitation < 0.0:
        logger.warning(
            f"Salienz-Formel: ziel_gravitation {ziel_gravitation:.3f} negativ — auf 0.0 gesetzt"
        )
        ziel_gravitation = 0.0

    # ── Verarbeitung: der Eigen-Pfad ────────────
    antriebe: dict[str, float] = {
        "sprachlich":       round(sprachlich, 4),
        "ziel_gravitation": round(ziel_gravitation, 4),
    }

    zuschlag:   float = _erregungs_zuschlag_berechnen(arousal)
    eigen_pfad: float = max(antriebe.values()) * (1.0 + zuschlag)

    # ── Verarbeitung: der Pflicht-Pfad ──────────
    # Beide Teile muessen da sein. Fehlt einer, gibt es keinen Pflicht-Pfad —
    # und nicht etwa einen mit dem Wert null. Ein fehlender Operand ist keine
    # Messung.
    pflicht_pfad: float | None = None
    if salienz_human is not None and nutzer_gewichtung is not None:
        # Die Gewichtung enthaelt die Null nicht — sie liegt in [0.5, 1.5].
        # Trifft die Pruefung doch zu, stuende hier ein Faktor, den kein Rad
        # erzeugt haben kann, und er koennte den Pfad allein auf null ziehen.
        if not RAD_MIN <= nutzer_gewichtung <= RAD_MAX:
            logger.warning(
                f"Salienz-Formel: nutzer_gewichtung {nutzer_gewichtung:.4f} ausserhalb "
                f"[{RAD_MIN}, {RAD_MAX}] — gekappt"
            )
            nutzer_gewichtung = max(RAD_MIN, min(RAD_MAX, nutzer_gewichtung))

        pflicht_pfad = salienz_human * nutzer_gewichtung

    # ── Verarbeitung: die Wahl ──────────────────
    if pflicht_pfad is None:
        effektiv: float = eigen_pfad
        gewinner: str   = "eigen"
    elif pflicht_pfad > eigen_pfad:
        effektiv = pflicht_pfad
        gewinner = "pflicht"
    elif eigen_pfad > pflicht_pfad:
        effektiv = eigen_pfad
        gewinner = "eigen"
    else:
        effektiv = eigen_pfad
        gewinner = "gleichstand"

    # ── Ausgabe-Verifikation ────────────────────
    # Die Skala endet bei 1.0. Der Faktor kann bis RAD_MAX gehen und der
    # Zuschlag bis 1.3 multiplizieren — das Produkt kann darueber liegen.
    # Die Kappung steht hier, bis Bauteil 1 sie in die Kurve verlegt; sie wird
    # vermerkt, damit sie nicht als Messergebnis durchgeht.
    gekappt: bool = effektiv > 1.0
    if gekappt:
        effektiv = 1.0

    return SalienzErgebnis(
        effektiv           = round(effektiv, 4),
        pflicht_pfad       = round(pflicht_pfad, 4) if pflicht_pfad is not None else None,
        eigen_pfad         = round(eigen_pfad, 4),
        gewinner           = gewinner,
        antriebe           = antriebe,
        erregungs_zuschlag = round(zuschlag, 4),
        gekappt            = gekappt,
    )
