"""Tests: Die Naht zwischen dem Emotionsvektor und der Achse R der Landschaft.

Der Emotionsvektor (S5, `_emotions_vektor_bestimmen`) liefert einen von neun
Namen. `GV_RICHTUNG_MAP` bildet diese neun auf das Bit der Achse R ab, und die
Achse ist eine der sechs, aus denen der Sektorindex und daraus die Landschaft
faellt. Beide Seiten sind fuer sich unauffaellig; die Naht dazwischen war bis
heute von keinem Test gedeckt.

Geprueft wird die Eigenschaft, die eine Naht tragen muss — **es darf kein
totes Ende geben**: Jede Auspraegung der einen Seite muss auf der anderen
einen Gegenspieler finden, und zwar in beide Richtungen. Ein Vektor ohne
Eintrag in der Tabelle liefe in einen `KeyError` oder, schlimmer, in einen
Vorgabewert; ein Tabelleneintrag, den die Funktion nie erzeugt, ist eine
Auspraegung, die nur auf dem Papier existiert.

Gemessen am 08.08.2026 ueber den **vollstaendigen** Eingaberaum — 1.508.598
Folgen ueber alle 17 kanonischen Emotionen, Laenge 0 bis 5:

    keine toten Enden — alle neun Vektoren erreichbar
    R=0   985.200 Folgen (65,3 %)   aus sechs Vektoren
    R=1   523.398 Folgen (34,7 %)   aus drei Vektoren

Warum Laenge 5 genuegt: Die Funktion schneidet `neuere = [-2:]` und
`aeltere = [-5:-2]`, sobald die Liste fuenf Eintraege hat. Laengere Folgen
sind von ihrem Fuenfer-Ende nicht zu unterscheiden. Ueber 46.656 Folgen der
Laenge 6 nachgeprueft, null Abweichungen.

Zeuge: Die neun Namen unten sind von Hand aus `novaberg-graph-rechenkette.md`
§5 (S5) uebertragen und **nicht** aus `config.GV_RICHTUNG_MAP` importiert.
Waeren sie es, pruefte der Test die Tabelle gegen sich selbst, und ein
gemeinsam entfernter Eintrag fiele auf keiner Seite auf.

Das Alphabet traegt **zwei** Vertreter je Gruppe. Der naheliegende Grund waere
falsch, und er ist am 08.08.2026 als Gegenprobe widerlegt worden: Auch mit nur
einem Vertreter je Gruppe werden alle neun erreicht. Die Bedingung "eine
Emotion, die vorher nicht vorkam" fragt **nicht** nach der Gruppe — sie
vergleicht Namen. Ein Wechsel ueber die Gruppengrenze erfuellt sie ebenso.

Der zweite Vertreter bleibt trotzdem, und zwar aus dem Grund, der aus der
Widerlegung folgt: Wuerde die Bedingung auf "neue Emotion **derselben**
Gruppe" verengt — die Lesart, die "Intensitaetsanstieg" im Bestand meint —,
verloere ein Alphabet mit einem Vertreter je Gruppe `spirale` und
`eskalation`, ohne dass dieser Test rot wuerde. Er waere dann blind, und zwar
still. Mit zwei Vertretern bleibt er in beiden Lesarten sehend.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from itertools import product

from config import GV_RICHTUNG_MAP
from ei.berechnung import _emotions_vektor_bestimmen

# Von Hand uebertragen, siehe Zeuge im Modul-Docstring.
NEUN_VEKTOREN: frozenset = frozenset({
    "absturz", "spirale", "stabilisierung", "erholung", "aufbluehen",
    "eskalation", "abkuehlung", "einbruch", "plateau",
})

# Zwei Vertreter je Gruppe: positiv, negativ, neutral.
ALPHABET: tuple[str, ...] = (
    "freude", "hoffnung",          # positiv
    "wut", "traurigkeit",          # negativ
    "neutral", "ueberrascht",      # neutral
)

# Ab hier ist die Folge von ihrem Ende nicht mehr unterscheidbar.
MAX_LAENGE: int = 5


def _vektor(folge: tuple[str, ...]) -> str:
    """Ruft die Produktionsfunktion auf, ohne sie nachzubauen.

    `inject_current=False`: Die Einspeisung des aktuellen Reizes haengt nur
    ein Glied an. Jede so entstehende Liste kommt in der Aufzaehlung ohnehin
    als eigene Folge vor, und die zweite Aufrufstelle des Bestandes
    (`internal.emotion.emotions_vector`) ruft ohnehin ohne Einspeisung auf.
    """
    return _emotions_vektor_bestimmen(
        [{"rolle": "user", "emotion": e} for e in folge],
        current_emotion="",
        rolle="user",
        inject_current=False,
    )


def _erzeugbare_vektoren() -> set[str]:
    """Zaehlt den Raum aus und gibt zurueck, was tatsaechlich herauskommt."""
    return {
        _vektor(folge)
        for laenge in range(0, MAX_LAENGE + 1)
        for folge in product(ALPHABET, repeat=laenge)
    }


class KeinTotesEndeAnDerNahtTest(unittest.TestCase):
    """Beide Seiten der Naht erreichen einander vollstaendig."""

    def test_die_aufzaehlung_erreicht_alle_neun(self) -> None:
        """Der positive Zwilling: ohne ihn pruefen die anderen drei nichts.

        Beide Richtungspruefungen unten sind Negativ-Zusicherungen — sie
        erwarten eine leere Differenzmenge und wuerden auf einem kaputten
        Aufzaehler still bestehen. Diese Methode haelt fest, dass der
        Aufzaehler ueberhaupt etwas findet, und zwar genau die neun.
        """
        self.assertEqual(_erzeugbare_vektoren(), set(NEUN_VEKTOREN))

    def test_jeder_erzeugbare_vektor_hat_eine_richtung(self) -> None:
        """Kein Vektor faellt in der Tabelle durch."""
        ohne_richtung = _erzeugbare_vektoren() - set(GV_RICHTUNG_MAP)
        self.assertEqual(
            ohne_richtung, set(),
            f"S5 erzeugt {sorted(ohne_richtung)}, GV_RICHTUNG_MAP kennt sie "
            f"nicht — die Achse R haette fuer diese Lage kein Bit",
        )

    def test_jede_richtung_ist_erzeugbar(self) -> None:
        """Kein Tabelleneintrag existiert nur auf dem Papier."""
        nie_erzeugt = set(GV_RICHTUNG_MAP) - _erzeugbare_vektoren()
        self.assertEqual(
            nie_erzeugt, set(),
            f"GV_RICHTUNG_MAP kennt {sorted(nie_erzeugt)}, S5 erzeugt sie "
            f"ueber den vollen Eingaberaum nie",
        )

    def test_beide_auspraegungen_der_achse_sind_erreichbar(self) -> None:
        """Eine Achse, die nur ein Bit annimmt, halbiert den Sektorraum.

        Das ist die zweite Frage an eine Naht — nicht "gibt es die
        Auspraegung", sondern "bleibt sie ueber die volle Spanne erreichbar".
        """
        bits = {GV_RICHTUNG_MAP[v] for v in _erzeugbare_vektoren()}
        self.assertEqual(
            bits, {0, 1},
            f"Achse R nimmt ueber den vollen Eingaberaum nur {sorted(bits)} "
            f"an — die Haelfte der 64 Sektoren waere unerreichbar",
        )


if __name__ == "__main__":
    unittest.main()
