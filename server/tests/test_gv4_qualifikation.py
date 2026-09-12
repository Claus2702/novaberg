"""Zeugen: der Filter, der zwanzig Kandidaten verschwinden liess.

Ziel: `[gemessen 12.09.2026]` **40 Turns** mit offenem Strategie-Tor, **0**
GV4-Luecken — bei 10 Kandidaten aus dem Langzeit- und 10 aus dem
Kurzzeitgedaechtnis je Lauf. Weder *„Keine Kandidaten gefunden"* noch *„alle
bereits erwaehnt"* kam je vor: Es scheiterte **nach** der Suche, an einer
Auswahl ohne Ausgabe.

**Die Schwelle war ein ungemessener Startwert.** `GV_CHARAKTER_RESONANZ_SCHWELLE`
stand auf 0,40 und trug im Code den Vermerk *„begruendeter Startwert, kein
Messergebnis. Nach Live-Betrieb pruefen."* Nachgeholt: ueber **150 echte
Nutzer-Turns** liegt `cosine(turn, kern)` bei median **0,228**, p99 0,413,
**max 0,421** — die alte Schwelle lag zwischen p99 und Maximum und liess 1,3 %
durch. Seit dem 12.09.2026 steht sie auf **0,30** (17,3 %).

~~**Die zweite Schwelle misst etwas anderes als die erste, und nur eine ist
kandidateneigen.** `charakter_resonanz` ist fuer alle gleich, weil der Aufrufer
dort die Naehe des **Turns** zum Kern einsetzt — ein einzelner Kandidat kann an
ihr nicht scheitern, ohne dass alle scheitern.~~

→ **Seit dem 12.09.2026 sind beide Schwellen kandidateneigen.** Die Naehe zum
Kern entsteht je Kandidat in der Suche: im LZG als zweiter Abstandsausdruck
derselben Abfrage, im KZG aus dem mitgelieferten Vektor. **Kein weiterer
Modellaufruf** — die Vektoren liegen gespeichert.

**Der Anlass war gemessen.** Ueber sieben Paare lag `cosine(turn, kern)` im
Median zwischen 0,097 und 0,282, und bei **zwei** Paaren passierte **kein
einziger** Turn die Schwelle — der Filter war dort nicht streng, sondern aus.
Auf der Kandidaten-Naehe liegen die Mediane bei 0,405 bis 0,548, und die
Schwelle trennt bei jedem Paar (`[vorher gerechnet ueber 4232 aktive Knoten]`).

**Der Zeuge, der das festhaelt, war unter dem alten Code unmoeglich:** zwei
Kandidaten im selben Turn, einer passiert, einer nicht.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from config import GV_CHARAKTER_RESONANZ_SCHWELLE, GV_LUECKEN_MIN_RELEVANZ
from ei.wissensluecken import _qualifizieren, _resonanz_pruefbar


def kandidat(relevanz: float, resonanz: float = 0.9) -> dict:
    """Ein Kandidat, wie ihn die Relevanzrechnung hinterlaesst."""
    return {"relevanz": relevanz, "charakter_resonanz": resonanz, "inhalt": "x"}


class BeideSchwellenGreifen(unittest.TestCase):
    """Relevanz und Resonanz entscheiden, und zwar getrennt."""

    def test_ueber_beiden_schwellen_bleibt(self) -> None:
        behalten = _qualifizieren([kandidat(0.5, 0.5)], resonanz_pruefbar=True)
        self.assertEqual(len(behalten), 1)

    def test_unter_der_relevanz_faellt(self) -> None:
        schwach = GV_LUECKEN_MIN_RELEVANZ - 0.01
        self.assertEqual(_qualifizieren([kandidat(schwach, 0.9)], True), [])

    def test_unter_der_resonanz_faellt(self) -> None:
        fern = GV_CHARAKTER_RESONANZ_SCHWELLE - 0.01
        self.assertEqual(_qualifizieren([kandidat(0.9, fern)], True), [])

    def test_genau_auf_der_schwelle_bleibt(self) -> None:
        """`>=`, nicht `>` — ein Grenzwert gehoert zur durchgelassenen Seite."""
        behalten = _qualifizieren(
            [kandidat(GV_LUECKEN_MIN_RELEVANZ, GV_CHARAKTER_RESONANZ_SCHWELLE)], True,
        )
        self.assertEqual(len(behalten), 1)


class OhnePruefbareResonanzEntfaelltNurDieseSchwelle(unittest.TestCase):
    """Cold-Start: kein Kern, aber die Relevanz gilt weiter."""

    def test_ferne_resonanz_schadet_nicht(self) -> None:
        behalten = _qualifizieren([kandidat(0.9, 0.01)], resonanz_pruefbar=False)
        self.assertEqual(len(behalten), 1)

    def test_die_relevanz_greift_trotzdem(self) -> None:
        schwach = GV_LUECKEN_MIN_RELEVANZ - 0.01
        self.assertEqual(_qualifizieren([kandidat(schwach, 0.9)], False), [])


class DieReihenfolgeBleibt(unittest.TestCase):
    """Sortiert wird erst danach — diese Funktion ordnet nicht um."""

    def test_eingangsreihenfolge(self) -> None:
        eins, zwei = kandidat(0.3), kandidat(0.8)
        self.assertEqual(_qualifizieren([eins, zwei], True), [eins, zwei])


class DerAusfallStehtImLog(unittest.TestCase):
    """Ohne diese Zeile war der Filter wochenlang unsichtbar."""

    def test_beide_gruende_werden_gezaehlt(self) -> None:
        with patch("ei.wissensluecken.logger") as log:
            _qualifizieren(
                [kandidat(0.01, 0.9), kandidat(0.9, 0.01), kandidat(0.9, 0.9)], True,
            )
            werte = log.info.call_args[0][1:]
        # behalten, gesamt, …, zu_schwach, …, zu_fern
        self.assertEqual(werte[0], 1)
        self.assertEqual(werte[1], 3)
        self.assertIn(1, werte)

    def test_auch_ohne_treffer_wird_gemeldet(self) -> None:
        """Null ist eine Auskunft — genau hier fehlte sie."""
        with patch("ei.wissensluecken.logger") as log:
            _qualifizieren([kandidat(0.01)], True)
            self.assertTrue(log.info.called)

    def test_die_leere_menge_meldet_ebenfalls(self) -> None:
        with patch("ei.wissensluecken.logger") as log:
            self.assertEqual(_qualifizieren([], True), [])
            self.assertTrue(log.info.called)

    def test_nicht_pruefbare_resonanz_steht_in_der_zeile(self) -> None:
        """Sonst sieht ein Cold-Start aus wie ein bestandener Filter."""
        with patch("ei.wissensluecken.logger") as log:
            _qualifizieren([kandidat(0.9)], resonanz_pruefbar=False)
            self.assertIn("nicht pruefbar", log.info.call_args[0][-1])


class DieResonanzIstKandidateneigen(unittest.TestCase):
    """Zwei Kandidaten, ein Turn, zwei Ausgaenge — vorher unmoeglich.

    Unter der alten Bauart trug jeder Kandidat denselben Wert, weil der
    Aufrufer die Naehe des Turns einsetzte. Dieser Zeuge faellt also nicht nur
    bei einem Defekt der Schwelle, sondern auch bei einem Rueckbau auf die
    Turn-Naehe — und das ist sein Zweck.
    """

    def test_einer_passiert_und_einer_nicht(self) -> None:
        nah  = kandidat(0.9, GV_CHARAKTER_RESONANZ_SCHWELLE + 0.10)
        fern = kandidat(0.9, GV_CHARAKTER_RESONANZ_SCHWELLE - 0.10)
        behalten = _qualifizieren([nah, fern], resonanz_pruefbar=True)
        self.assertEqual(behalten, [nah])

    def test_die_reihenfolge_der_beiden_aendert_nichts(self) -> None:
        """Die Gegenprobe zum Zeugen darueber: nicht die Stellung entscheidet."""
        nah  = kandidat(0.9, GV_CHARAKTER_RESONANZ_SCHWELLE + 0.10)
        fern = kandidat(0.9, GV_CHARAKTER_RESONANZ_SCHWELLE - 0.10)
        self.assertEqual(_qualifizieren([fern, nah], True), [nah])

    def test_drei_verschiedene_werte_teilen_sich_auf(self) -> None:
        """Kein Alles-oder-nichts mehr: aus drei werden zwei."""
        a = kandidat(0.9, GV_CHARAKTER_RESONANZ_SCHWELLE + 0.20)
        b = kandidat(0.9, GV_CHARAKTER_RESONANZ_SCHWELLE + 0.01)
        c = kandidat(0.9, GV_CHARAKTER_RESONANZ_SCHWELLE - 0.01)
        self.assertEqual(_qualifizieren([a, b, c], True), [a, b])


class DiePruefbarkeitBrauchtJedenWert(unittest.TestCase):
    """`_resonanz_pruefbar` — die Regel, die vorher inline stand."""

    def test_ohne_kern_nicht_pruefbar(self) -> None:
        self.assertFalse(_resonanz_pruefbar([kandidat(0.9)], None))

    def test_mit_kern_und_allen_werten_pruefbar(self) -> None:
        self.assertTrue(_resonanz_pruefbar([kandidat(0.9), kandidat(0.8)], [0.1, 0.2]))

    def test_ein_fehlender_wert_schaltet_die_schwelle_ab(self) -> None:
        """Nicht nur fuer diesen Kandidaten — fuer den ganzen Turn.

        Die Alternative waere, ihn durchzulassen oder zu verwerfen; beides
        entscheidet etwas anderes als die Schwelle behauptet, und beides waere
        im Log nicht zu sehen.
        """
        ohne = {"relevanz": 0.9, "inhalt": "x"}
        self.assertFalse(_resonanz_pruefbar([kandidat(0.9), ohne], [0.1, 0.2]))

    def test_der_leerfall_ist_pruefbar(self) -> None:
        """Es gibt nichts, was ungeprueft durchkaeme."""
        self.assertTrue(_resonanz_pruefbar([], [0.1, 0.2]))


class DieSchwelleIstGemessen(unittest.TestCase):
    """Der Wert selbst — sein Band steht im Kommentar der Konstante.

    **Beide Grenzen stammen aus der Verteilung der Turn-Naehe** (150 Turns,
    11.09.2026) und damit aus einer Groesse, die die Schwelle seit dem
    12.09.2026 nicht mehr misst. Sie bleiben stehen, solange der Wert
    unveraendert ist, und sind **beim naechsten Setzen neu zu bilden** — aus der
    Verteilung der Kandidaten-Naehe, die die `gv4_kern_resonanz`-Zeile des
    Pipeline-Logs erhebt (`20_TESTS/beispiel-gerechnet.md`).
    """

    def test_sie_liegt_unter_dem_alten_startwert(self) -> None:
        """0,40 lag zwischen p99 (0,413) und Maximum (0,421) der Verteilung."""
        self.assertLess(GV_CHARAKTER_RESONANZ_SCHWELLE, 0.40)

    def test_sie_liegt_ueber_dem_median(self) -> None:
        """Median 0,228 — eine Schwelle darunter liesse fast alles durch."""
        self.assertGreater(GV_CHARAKTER_RESONANZ_SCHWELLE, 0.228)


if __name__ == "__main__":
    unittest.main()
