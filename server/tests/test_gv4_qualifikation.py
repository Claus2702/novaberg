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

**Die zweite Schwelle misst etwas anderes als die erste, und nur eine ist
kandidateneigen.** `relevanz` gehoert zum Kandidaten; `charakter_resonanz` ist
fuer alle gleich, weil der Aufrufer dort die Naehe des **Turns** zum Kern
einsetzt. Diese Zeugen halten beide Faelle fest — auch den, dass ein einzelner
Kandidat an der Resonanz nicht scheitern **kann**, ohne dass alle scheitern.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from config import GV_CHARAKTER_RESONANZ_SCHWELLE, GV_LUECKEN_MIN_RELEVANZ
from ei.wissensluecken import _qualifizieren


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


class DieSchwelleIstGemessen(unittest.TestCase):
    """Der Wert selbst — sein Band steht im Kommentar der Konstante."""

    def test_sie_liegt_unter_dem_alten_startwert(self) -> None:
        """0,40 lag zwischen p99 (0,413) und Maximum (0,421) der Verteilung."""
        self.assertLess(GV_CHARAKTER_RESONANZ_SCHWELLE, 0.40)

    def test_sie_liegt_ueber_dem_median(self) -> None:
        """Median 0,228 — eine Schwelle darunter liesse fast alles durch."""
        self.assertGreater(GV_CHARAKTER_RESONANZ_SCHWELLE, 0.228)


if __name__ == "__main__":
    unittest.main()
