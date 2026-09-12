"""Tests: Eine Summe genau auf der halben Stufe bekommt den hoeheren Schritt.

Ziel: `_vektor_laenge_berechnen` rundet zur **naechsten** Zahl, nicht zur
geraden. Bis zum 12.09.2026 schloss die Funktion mit `round(laenge)`, und
Pythons `round` rundet halbe Werte zur geraden Zahl. Das kostete an beiden
Kanten je einen Schritt, und an keiner war es entschieden:

    unten   `round(0.5) → 0`   kein Vorausdenken, obwohl 0,5 gerechnet war
    oben    `round(2.5) → 2`   kein dritter Schritt, nie, in drei Modi

Die obere Kante ist die folgenreichere. Bei Modus-Zuschlag −0.3
(`fachgespraech`, `lernmodus`, `philosophischer_austausch`) ist die beste
erreichbare Summe **exakt 2.5** — positive Emotion bei Arousal 1.0, `vertrauen`,
`locker`. Mit der alten Regel war die Laenge 3 dort bei **jeder** Faktorstellung
ausgeschlossen, und in diesen drei Modi liegen 794 von 1434 Rohturns.

Vorher gerechnet (12.09.2026, 1434 Rohturns aus `pipeline_log`): Die Umstellung
bewegt **68 Turns (4,7 %)** — 43 von 0 auf 1, 25 von 2 auf 3 — und es kippt
ausschliesslich an den Summen +0,50 und +2,50. Die Quote des Strategie-Tors
bleibt dabei unveraendert bei 36,6 %, weil keiner der Wechsel die Schwelle 2
ueberschreitet.

Zeuge: Die Summen sind von Hand aus den Beitraegen gebildet, die
`novaberg-node-gv_k.md` nennt — Grundwert 1,0, positive Emotion
`0,5 + arousal × 0,5`, Dynamik ±0,5, Modus-Zuschlag, Stil +0,3 / −0,2. Die
Erwartung stammt damit aus dem Konzept und nicht aus dem Code, der sie erfuellt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from graph.nodes.gespraechsvektor import _vektor_laenge_berechnen
from graph.personality import Emotion, Personality


def _laenge(**felder: str | float) -> int:
    """Die Laenge fuer eine Perzeption, durch die Produktionsfunktion."""
    return _vektor_laenge_berechnen({"external": Personality(emotion=Emotion(**felder))})


class HalbeStufeGehtNachObenTest(unittest.TestCase):
    """Die beiden Kanten, an denen die alte Regel einen Schritt verschluckte."""

    def test_untere_kante_summe_null_komma_fuenf_ergibt_eins(self) -> None:
        """1,0 − 0,5 (distanz) = 0,5 → ein Schritt, nicht keiner.

        Die haeufigste Lage dieser Art im Bestand: `berichtend` (Zuschlag 0),
        Emotion ohne Valenzgruppe, `fachlich` (kein Stilbeitrag).
        """
        self.assertEqual(
            _laenge(emotion="neutral", arousal=0.5, mode="berichtend",
                    relationship_dynamic="distanz", language_style="fachlich"),
            1,
        )

    def test_obere_kante_summe_zwei_komma_fuenf_ergibt_drei(self) -> None:
        """1,0 + 1,0 + 0,5 + 0,3 − 0,3 = 2,5 → drei Schritte.

        Das ist die beste Stellung in einem fachlichen Modus. Mit der alten
        Regel war die 3 dort unerreichbar.
        """
        self.assertEqual(
            _laenge(emotion="freude", arousal=1.0, mode="fachgespraech",
                    relationship_dynamic="vertrauen", language_style="locker"),
            3,
        )

    def test_obere_kante_auch_ohne_stilbeitrag(self) -> None:
        """1,0 + 1,0 + 0,5 = 2,5 in einem Modus mit Zuschlag null."""
        self.assertEqual(
            _laenge(emotion="freude", arousal=1.0, mode="alltag",
                    relationship_dynamic="vertrauen", language_style="neutral"),
            3,
        )


class ZwischenDenStufenBleibtAllesWieEsWarTest(unittest.TestCase):
    """Die Umstellung betrifft die halben Stufen und sonst nichts."""

    def test_summe_unter_der_mitte_rundet_weiter_ab(self) -> None:
        """1,0 + 0,725 + 0,5 − 0,3 = 1,925 → 2, wie vorher."""
        self.assertEqual(
            _laenge(emotion="neugierig", arousal=0.45,
                    mode="philosophischer_austausch",
                    relationship_dynamic="vertrauen", language_style="fachlich"),
            2,
        )

    def test_summe_ueber_der_mitte_rundet_weiter_auf(self) -> None:
        """1,0 + 0,725 − 0,3 = 1,425 → 1, wie vorher."""
        self.assertEqual(
            _laenge(emotion="neugierig", arousal=0.45,
                    mode="philosophischer_austausch",
                    relationship_dynamic="neutral", language_style="fachlich"),
            1,
        )


class DieGrenzenDerFunktionBleibenTest(unittest.TestCase):
    """Deckel, Boden und Notbremse sind von der Rundung unberuehrt."""

    def test_der_deckel_bleibt_bei_drei(self) -> None:
        """1,0 + 1,0 + 0,5 + 0,3 + 0,3 = 3,1 → 3, nicht 4."""
        self.assertEqual(
            _laenge(emotion="freude", arousal=1.0, mode="kreativ",
                    relationship_dynamic="vertrauen", language_style="locker"),
            3,
        )

    def test_eine_negative_summe_bleibt_null(self) -> None:
        """1,0 − 0,5 − 0,5 − 0,2 − 0,3 = −0,5 → 0."""
        self.assertEqual(
            _laenge(emotion="frustration", arousal=1.0, mode="fachgespraech",
                    relationship_dynamic="distanz", language_style="formell"),
            0,
        )

    def test_die_krise_bleibt_null_und_rechnet_nicht(self) -> None:
        """Spirale bei hohem Arousal setzt 0, bevor irgendeine Summe entsteht.

        Die Stellung waere sonst 1,0 + 1,0 + 0,5 + 0,3 = 2,8 und damit 3 —
        der Zeuge trennt die Notbremse von der Arithmetik.
        """
        self.assertEqual(
            _laenge(emotion="freude", arousal=1.0, mode="alltag",
                    relationship_dynamic="vertrauen", language_style="locker",
                    emotions_vector="spirale"),
            0,
        )


if __name__ == "__main__":
    unittest.main()
