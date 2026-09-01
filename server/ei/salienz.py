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
import math
from dataclasses import dataclass, field

from config import (
    RAD_MAX,
    RAD_MIN,
    SALIENZ_EREGUNG_MAX_ZUSCHLAG,
    SALIENZ_ZUG_G0,
    SALIENZ_ZUG_W,
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

    zielsog: float = 0.0
    # Der staerkste **ungetorte** Zielsog dieses Turns (similarity x motivation).
    # Ungetort, weil das Tor der Aktivierung eine andere Frage beantwortet: was
    # Nova denkt, nicht wie wichtig ihr eine Aeusserung ist.

    zug_staerke: float = 0.0
    # beta(zielsog) — wie viel der Luecke nach oben der Sog schliesst. Steht
    # neben dem Sog, weil aus dem Ergebnis allein nicht abzulesen waere, ob ein
    # schwacher Zug an einem starken Sog lag oder umgekehrt.


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


def zielsog_zug_staerke(zielsog: float) -> float:
    """Wie stark Novas eigener Zielsog an der Salienz zieht — eine Logistische.

    **Der Zug waechst mit dem Sog, und zwar ueberproportional in der Mitte.**
    Ein schwacher Sog soll fast nichts bewirken, ein starker deutlich etwas;
    dazwischen liegt der Bereich, in dem die Entscheidung faellt. Genau das ist
    die Form einer Logistischen: flach an beiden Enden, steil in der Mitte.

        beta(g) = 1 / (1 + exp(-(g - SALIENZ_ZUG_G0) / SALIENZ_ZUG_W))

    **Sie tort sich selbst.** Bei `g = 0` liefert sie 0,001. Eine Schwelle, ab
    der ein Sog "zaehlt", waere eine zweite Entscheidung ueber dieselbe Sache —
    und ein Tor, das ein Gewicht sein sollte, ist genau der Fehler, den die
    alte Fassung machte (`GRAVITATIONS_SCHWELLE` liess 98 % der Turns ohne Sog).

    Vorbedingung: keine — negative Werte werden gekappt und benannt.
    Nachbedingung: Rueckgabe in (0, 1).
    Fehlerfaelle: Keine.

    Args:
        zielsog: Die staerkste ungetorte Zielstaerke des Turns
            (`similarity x motivation`), 0.0-1.0.

    Returns:
        Der Anteil der Luecke nach oben, den der Sog schliesst.
    """
    # ── Eingabe-Validierung ─────────────────────
    if zielsog < 0.0:
        logger.warning(
            f"Salienz-Formel: zielsog {zielsog:.3f} negativ — auf 0.0 gesetzt"
        )
        zielsog = 0.0

    # ── Verarbeitung / Ausgabe ──────────────────
    return 1.0 / (1.0 + math.exp(-(zielsog - SALIENZ_ZUG_G0) / SALIENZ_ZUG_W))


def salienz_effektiv_berechnen(
    *,
    sprachlich:        float,
    ziel_gravitation:  float,
    arousal:           float,
    salienz_human:     float | None,
    nutzer_gewichtung: float | None,
    zielsog:           float = 0.0,
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
        zielsog: Die staerkste **ungetorte** Zielstaerke dieses Turns
            (`similarity x motivation`), 0.0-1.0. Sie zieht den Eigen-Pfad auf
            die Luecke nach oben; wie stark, sagt `zielsog_zug_staerke`.
            Vorgabe 0.0 heisst "kein Sog" und laesst den Pfad unveraendert —
            das ist der Zustand jedes Aufrufers, der sie nicht kennt.

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

    # **Der Zuschlag hebt, und die Normierung haelt die Skala.** Bis zum
    # 24.08.2026 stand hier `max(antriebe) * (1 + zuschlag)` — ein Ausdruck,
    # der die Obergrenze ueberschreiten **muss**, sobald der Antrieb hoch und
    # die Erregung stark ist. Gemessen ueber 2506 protokollierte Turns lief
    # das in **21,3 %** der Faelle in die Kappung; danach trugen 534 Turns
    # denselben Wert 1,0 und waren untereinander nicht mehr unterscheidbar.
    #
    # Die Teilung durch `(1 + MAX_ZUSCHLAG)` macht den Ausdruck auf [0, 1]
    # **geschlossen**: Beide Eingaenge liegen in [0, 1], also liegt auch das
    # Ergebnis darin, und die Kappung wird zur Sicherung statt zum Formteil.
    # Gemessen faellt sie damit auf 1,5 % — der Rest kommt aus dem
    # Pflicht-Pfad, der unveraendert ungebremst multipliziert.
    #
    # **Die Bedeutung der Zahl aendert sich dabei, und das ist Absicht.** Voll
    # erreicht sie nur, wer **beides** traegt: volle Bewertung und volle
    # Erregung. Ein ruhiger Turn behaelt `1/(1+k)` seiner Bewertung — die
    # Erregung vergroessert nicht mehr, sie **teilt die Skala mit**. Die
    # Einseitigkeit aus `novaberg-salienz-berechnung_k.md` §4 bleibt: Der
    # Zuschlag hebt gegenueber einem ruhigen Turn, er loescht nichts aus.
    zuschlag: float = _erregungs_zuschlag_berechnen(arousal)

    # **Der Zielsog zieht, er konkurriert nicht.** Bis zum 01.09.2026 stand er
    # als zweiter Operand im `max()` darueber und entschied dort in **4 von
    # 2786** protokollierten Zeilen — Mittel 0,034 gegen 0,692 beim
    # sprachlichen Antrieb. Ein Antrieb, der rechnet und unter einem `max()`
    # verschwindet, sieht von aussen aus wie einer, der nicht angeschlossen
    # ist.
    #
    # Die Form ist die Auffuellregel der Praegung: Sie schliesst einen Teil der
    # **Luecke nach oben** und kann deshalb nie senken und nie ueber 1 gehen —
    # ohne Normierung, ohne Kappung. Ein Mittelwert taete das Gegenteil: Weil
    # der Sog in 86 % der Turns null ist, halbierte er die Salienz des ganzen
    # Systems (gemessen: Mittel 0,6196 -> 0,3250, Praegungs-Torquote 59 % -> 0 %).
    zug:   float = zielsog_zug_staerke(zielsog)
    basis: float = max(antriebe.values())
    gezogen: float = basis + zug * zielsog * (1.0 - basis)

    eigen_pfad: float = (
        gezogen * (1.0 + zuschlag)
        / (1.0 + SALIENZ_EREGUNG_MAX_ZUSCHLAG)
    )

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
    #
    # Die Kappung bleibt hier (geprueft Chat 113). Der urspruengliche Plan war,
    # sie mit Bauteil 1 in die Salienzkurve zu verlegen. Die Kurve kappt aber
    # nur ihr ERGEBNIS: Sie rechnet anteil = min(roh/CAP, 1.0) und liefert
    # zuverlaessig einen Wert in [0,1] — der Eingangswert selbst wuerde
    # ungeklemmt gespeichert. `salienz_eingang` ist als Feld in [0,1]
    # spezifiziert (novaberg-kzg-salienz_k.md §4); ein Erzeuger, der darueber
    # liefert, verschoebe den Skalenbruch nur eine Ebene tiefer.
    # Der Vermerk bleibt, damit die Kappung nicht als Messergebnis durchgeht.
    gekappt: bool = effektiv > 1.0
    if gekappt:
        effektiv = 1.0

    return SalienzErgebnis(
        effektiv           = round(effektiv, 4),
        pflicht_pfad       = round(pflicht_pfad, 4) if pflicht_pfad is not None else None,
        eigen_pfad         = round(eigen_pfad, 4),
        zielsog            = round(zielsog, 4),
        zug_staerke        = round(zug, 4),
        gewinner           = gewinner,
        antriebe           = antriebe,
        erregungs_zuschlag = round(zuschlag, 4),
        gekappt            = gekappt,
    )
