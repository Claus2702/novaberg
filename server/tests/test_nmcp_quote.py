"""Tests: Der Quotenabgleich ist der Leser, der dem Aushang widersprechen kann.

Ziel: Die Schwellen wirken als Verhaeltnis und damit in beide Richtungen gleich;
unterhalb der Mindest-Stichprobe urteilt der Abgleich nicht; die Richtung der
Abweichung wird als Diagnose benannt; und der Nenner ist je Graph getrennt.

Zeugen dieser Datei:
  * **Die Schwellen stehen als von Hand gerechnete Literale**, aus der
    Konvention uebernommen — nicht aus einem Lauf des Abgleichs gelesen.
  * **Die Symmetrie wird an ihrer Wirkung geprueft.** Geprueft wird, dass eine
    Verwechslung zweier Nachbarstufen in BEIDE Richtungen dasselbe Urteil
    ergibt. Eine Prozentpunkt-Differenz taete das nicht, und genau deshalb
    rechnet der Abgleich ein Verhaeltnis.
  * **Die Mindest-Stichprobe wird an ihrer Grenze gefahren**, nicht in der
    Mitte: bei n = MINDEST_FEHLER - 1 und n = MINDEST_FEHLER.
  * **Der Nenner wird gegengeprueft.** Ein Turn im einen Graphen darf die
    Quote im anderen nicht bewegen — sonst schwankt jede Quote, sobald jemand
    den Takt des Hintergrunds aendert.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from agents.nmcp_quote import (
    FEHLER_OBEN,
    FEHLER_UNTEN,
    MINDEST_FEHLER,
    MINDEST_WARNUNG,
    WARNUNG_OBEN,
    WARNUNG_UNTEN,
    QuotenRegister,
)


def _fahren(
    zugestellt: int,
    turns: int,
    graph: str = "user",
    bearbeitet: int = 0,
    abgelehnt: int = 0,
) -> QuotenRegister:
    """Legt ein Register mit den uebergebenen Zaehlerstaenden an.

    Vorbedingung: `zugestellt` <= `turns`, `abgelehnt` <= `bearbeitet`.
    Nachbedingung: ein Register, dessen Staende genau den Argumenten
    entsprechen.
    """
    r = QuotenRegister()
    for _ in range(turns):
        r.turn_zaehlen(graph)
    for _ in range(zugestellt):
        r.zustellung_zaehlen("dienst", graph)
    for i in range(bearbeitet):
        r.bearbeitung_zaehlen(
            "dienst", graph, "abgelehnt" if i < abgelehnt else "abgeschlossen"
        )
    return r


class SchwellenTest(unittest.TestCase):
    """Die Schwellen sind Verhaeltnisse und wirken symmetrisch."""

    def test_treffer_im_band_stimmt(self) -> None:
        """Gemessen gleich geschaetzt ergibt 'stimmt'."""
        r = _fahren(zugestellt=50, turns=200)     # 25 %
        self.assertEqual(r.abgleichen("dienst", "user", 25).urteil, "stimmt")

    def test_halbe_abweichung_nach_unten_ist_fehler(self) -> None:
        """Geschaetzt 50, gemessen 25 — Verhaeltnis 0.5, die Fehlerschwelle."""
        r = _fahren(zugestellt=50, turns=200)     # 25 %
        abgleich = r.abgleichen("dienst", "user", 50)
        self.assertEqual(abgleich.urteil, "fehler")
        self.assertAlmostEqual(abgleich.gemessen / 50, FEHLER_UNTEN, places=6)

    def test_halbe_abweichung_nach_oben_ist_fehler(self) -> None:
        """Geschaetzt 25, gemessen 50 — Verhaeltnis 2.0, dieselbe Schwelle.

        Das ist der Zeuge fuer die Symmetrie: Dieselbe Verwechslung zweier
        Nachbarstufen ergibt in beide Richtungen 'fehler'. Eine
        Prozentpunkt-Differenz haette hier +100 % und dort -50 % gesehen
        und verschieden geurteilt.
        """
        r = _fahren(zugestellt=100, turns=200)    # 50 %
        abgleich = r.abgleichen("dienst", "user", 25)
        self.assertEqual(abgleich.urteil, "fehler")
        self.assertAlmostEqual(abgleich.gemessen / 25, FEHLER_OBEN, places=6)

    def test_viertel_abweichung_ist_warnung(self) -> None:
        """Verhaeltnis 0.75 bei ausreichender Stichprobe ergibt 'warnung'."""
        # 200 Turns, 75 Zustellungen = 37,5 % gegen geschaetzte 50 %
        r = _fahren(zugestellt=75, turns=200)
        abgleich = r.abgleichen("dienst", "user", 50)
        self.assertEqual(abgleich.urteil, "warnung")
        self.assertAlmostEqual(abgleich.gemessen / 50, WARNUNG_UNTEN, places=6)

    def test_schwellen_sind_paarweise_reziprok(self) -> None:
        """Die Schranken sind Kehrwerte — sonst ist die Symmetrie nur behauptet."""
        self.assertAlmostEqual(WARNUNG_UNTEN * WARNUNG_OBEN, 1.0, places=9)
        self.assertAlmostEqual(FEHLER_UNTEN * FEHLER_OBEN, 1.0, places=9)


class StichprobeTest(unittest.TestCase):
    """Ohne Mindest-Stichprobe urteilt der Abgleich nicht."""

    def test_unter_der_grenze_keine_aussage(self) -> None:
        """Bei n unter MINDEST_FEHLER wird nicht geurteilt.

        Bei einer wahren Rate von 25 % liegt in vier Durchlaeufen mit rund
        einem Drittel Wahrscheinlichkeit keine einzige Zustellung — ein
        Abgleich, der dort urteilt, meldet Rauschen und wird deshalb
        abgeschaltet. Ein Alarm, der zu frueh kommt, ist teurer als keiner.
        """
        r = _fahren(zugestellt=0, turns=MINDEST_FEHLER - 1)
        self.assertEqual(r.abgleichen("dienst", "user", 25).urteil, "keine_aussage")

    def test_an_der_grenze_wird_geurteilt(self) -> None:
        """Ab MINDEST_FEHLER faellt ein Fehlerurteil."""
        r = _fahren(zugestellt=0, turns=MINDEST_FEHLER)
        self.assertEqual(r.abgleichen("dienst", "user", 25).urteil, "fehler")

    def test_viertel_abweichung_braucht_die_groessere_stichprobe(self) -> None:
        """Zwischen den beiden Grenzen ist die Viertel-Abweichung stumm.

        Je groesser die behauptete Abweichung, desto weniger Durchlaeufe
        braucht es, um ihrer sicher zu sein — deshalb sind die Grenzen
        verschieden.
        """
        n = MINDEST_WARNUNG - 20
        self.assertGreater(n, MINDEST_FEHLER)
        r = _fahren(zugestellt=int(n * 0.375), turns=n)   # 37,5 % gegen 50 %
        self.assertEqual(r.abgleichen("dienst", "user", 50).urteil, "keine_aussage")


class NullQuoteTest(unittest.TestCase):
    """Bei null Prozent gelten absolute Schranken."""

    def test_null_und_nie_zugestellt_stimmt_und_bleibt_befund(self) -> None:
        """Konsistent — und die Diagnose sagt trotzdem 'unentschieden'."""
        r = _fahren(zugestellt=0, turns=200)
        abgleich = r.abgleichen("dienst", "user", 0)
        self.assertEqual(abgleich.urteil, "stimmt")
        self.assertIn("unentschieden", abgleich.diagnose)

    def test_null_aber_haeufig_ist_fehler(self) -> None:
        """Als Ausnahme angemeldet und in einem Viertel der Faelle gerufen."""
        r = _fahren(zugestellt=50, turns=200)     # 25 %
        self.assertEqual(r.abgleichen("dienst", "user", 0).urteil, "fehler")


class DiagnoseTest(unittest.TestCase):
    """Die Richtung der Abweichung ist die Diagnose."""

    def test_untererfuellung_wird_als_teuer_benannt(self) -> None:
        """Die unsichtbare Richtung muss im Text erkennbar sein."""
        r = _fahren(zugestellt=10, turns=200)     # 5 % gegen 50 %
        abgleich = r.abgleichen("dienst", "user", 50)
        self.assertIn("uebersehen", abgleich.diagnose)
        self.assertIn("unsichtbare", abgleich.diagnose)

    def test_ueberschreitung_wird_als_behelligt_benannt(self) -> None:
        """Die billige Richtung wird anders benannt als die teure."""
        r = _fahren(zugestellt=150, turns=200)    # 75 % gegen 25 %
        self.assertIn("behelligt", r.abgleichen("dienst", "user", 25).diagnose)

    def test_null_zustellungen_heisst_unerreichbar(self) -> None:
        """Null bei positiver Schaetzung ist ein eigener Befund."""
        r = _fahren(zugestellt=0, turns=200)
        self.assertIn("unerreichbar", r.abgleichen("dienst", "user", 50).diagnose)

    def test_treffende_quote_mit_ablehnungen_meldet_die_grenze(self) -> None:
        """Der Aushang trifft, die Grenzangabe fehlt.

        Das ist die Zeile, die den Abgleich mit dem vierten Ausgang
        verbindet: Ein Dienst, der genau so oft zugestellt wird wie
        geschaetzt und die Haelfte davon ablehnt, hat einen richtigen
        Aushang und eine falsche Grenzangabe. Wer nur die Zustellquote
        betrachtet, sieht dort nichts.
        """
        r = _fahren(zugestellt=50, turns=200, bearbeitet=50, abgelehnt=40)
        abgleich = r.abgleichen("dienst", "user", 25)
        self.assertEqual(abgleich.urteil, "warnung")
        self.assertIn("Grenzangabe", abgleich.diagnose)


class NennerTest(unittest.TestCase):
    """Der Nenner ist je Graph getrennt."""

    def test_fremder_graph_bewegt_die_quote_nicht(self) -> None:
        """Ein Impuls im Hintergrund darf die Nutzer-Quote nicht verschieben.

        Am 14.08.2026 gemessen: 49 von 122 Durchlaeufen waren eigene
        Impulse. Die Impulsrate gehoert dem Zeitgeber und keinem
        Fachdienst — in einem gemeinsamen Nenner schlaegt jede Quote aus,
        sobald jemand den Takt aendert.
        """
        r = _fahren(zugestellt=50, turns=200, graph="user")
        vorher = r.abgleichen("dienst", "user", 25).gemessen
        for _ in range(500):
            r.turn_zaehlen("pixie")
        nachher = r.abgleichen("dienst", "user", 25).gemessen
        self.assertAlmostEqual(vorher, nachher, places=9)

    def test_unbekannter_graph_wird_nicht_gezaehlt(self) -> None:
        """Ein Turn in einem Graphen ausserhalb des Kanons zaehlt nicht."""
        r = QuotenRegister()
        r.turn_zaehlen("erfunden")
        self.assertEqual(r.turns("erfunden"), 0)

    def test_unbekannter_graph_beim_abgleich_scheitert_laut(self) -> None:
        """Ein Abgleich gegen einen unbekannten Graphen ist ein Fehler."""
        with self.assertRaises(ValueError):
            QuotenRegister().abgleichen("dienst", "erfunden", 25)

    def test_quote_ausserhalb_des_kanons_scheitert_laut(self) -> None:
        """37 % ist keine Stufe der Skala."""
        with self.assertRaises(ValueError):
            _fahren(0, 200).abgleichen("dienst", "user", 37)


class ZaehlerTest(unittest.TestCase):
    """Zustellung und Bearbeitung sind zwei Zaehler."""

    def test_zustellverlust_ist_sichtbar(self) -> None:
        """Zugestellt ohne Bearbeitung bleibt als Differenz erkennbar.

        Wer nur `bearbeitet` zaehlt, liest einen Pipeline-Defekt als
        Routing-Problem.
        """
        r = _fahren(zugestellt=50, turns=200, bearbeitet=30)
        stand = r.stand("dienst", "user")
        self.assertEqual(stand.zugestellt, 50)
        self.assertEqual(stand.bearbeitet, 30)
        self.assertEqual(stand.zugestellt - stand.bearbeitet, 20)

    def test_quote_rechnet_gegen_zustellung_nicht_gegen_erfolg(self) -> None:
        """Der Zustellverlust darf die gemessene Quote nicht senken."""
        r = _fahren(zugestellt=50, turns=200, bearbeitet=1)
        self.assertAlmostEqual(
            r.abgleichen("dienst", "user", 25).gemessen, 25.0, places=6
        )

    def test_unbekanntes_paar_hat_leeren_stand(self) -> None:
        """Ein Dienst ohne Zustellung ist selbst eine Auskunft, kein Fehler."""
        stand = QuotenRegister().stand("gibt_es_nicht", "user")
        self.assertEqual(stand.zugestellt, 0)
        self.assertEqual(stand.bearbeitet, 0)


if __name__ == "__main__":
    unittest.main()
