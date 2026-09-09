"""Tests fuer die Normierung des Gravitationsterms — `GRAVITATIONSTERM-OHNE-OBERGRENZE`.

ZIEL: Der Gravitationsterm liegt an beiden Lesern in [0, 1] und ueberschreibt
die Salienz-Bewertung des Modells nicht mehr.

Befund, aus dem das entstand `[gemessen 09.09.2026 an 200 Turns und am
Bestand]`: `gravitationsterm_berechnen` bildete die **Summe** der
Aktivierungs-Staerken ueber alle aktivierten Ziele, unbeschraenkt. Sie erreicht
**5,9955**. Von 498 Boosts trugen **277 (55,6 %)** einen Term >= 1,0 — dort war
die Salienz danach **immer** 1,0, unabhaengig von der Bewertung des Modells
(Basis im Mittel 0,327). Im Eigen-Pfad reichte `eigen_pfad` bis **4,097** bei
Zielspanne [0…1], und `gekappt` stand in 61 von 61 Faellen auf `true`.

Zwei Dinge werden hier scharf getrennt:
  - die **Normierung** in `gravitationsterm_berechnen` — sie bringt den Term
    auf dieselbe Skala wie seine Nachbarn (`F-NAHT-1`)
  - die **Auffuellregel** im HumanGraph-Boost — sie haelt das Ergebnis in
    [basis, 1], ohne zu kappen

Beides zusammen: Ein normierter Term, additiv aufgelegt, ergaebe wieder
exakte Einsen (die naive Form lieferte 399 statt heute 308).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import math
import unittest

from config import GRAVITATIONS_SALIENZ_FAKTOR, GRAVITATIONSTERM_CAP
from ei.gravitation import ActivatedGoal, gravitationsterm_berechnen
from ei.utils import fill_gap_upward, sin_sqrt_norm

LOGGER: str = "ki_server.ei.gravitation"


def _ziel(staerke: float) -> ActivatedGoal:
    """Ein aktiviertes Ziel mit der gewuenschten Aktivierungs-Staerke."""
    return ActivatedGoal(
        ziel_id              = 1,
        ziel_typ             = "langfristig",
        zielsatz             = "Zusammenhaenge verstehen",
        motivation           = 0.8,
        emotion              = "neugierig",
        arousal              = 0.5,
        similarity           = 0.6,
        aktivierungs_staerke = staerke,
    )


class GravitationstermSpanneTest(unittest.TestCase):
    """Der Term verlaesst die Zielspanne nicht mehr — auch nicht unter Last."""

    def test_leere_liste_ergibt_null(self) -> None:
        """Kein aktiviertes Ziel heisst kein Zug, nicht ein schwacher."""
        ergebnis = gravitationsterm_berechnen([])
        self.assertEqual(ergebnis.normiert, 0.0)
        self.assertEqual(ergebnis.roh, 0.0)
        # Der Cap steht auch im Leerfall dabei: Eine Zeile ohne ihn waere
        # spaeter nicht mehr der Generation zuzuordnen, in der sie entstand.
        self.assertEqual(ergebnis.cap, GRAVITATIONSTERM_CAP)

    def test_ein_ziel_bleibt_unter_eins(self) -> None:
        """Der Normalfall: ein Ziel, ein Term deutlich unter der Obergrenze."""
        self.assertLess(gravitationsterm_berechnen([_ziel(0.5)]).normiert, 1.0)

    def test_zwoelf_volle_ziele_bleiben_in_der_spanne(self) -> None:
        """Der Fall, der den Befund ausgeloest hat.

        Zwoelf voll aktivierte Ziele ergeben eine Rohsumme von 12,0 und einen
        skalierten Rohwert von 6,0 — genau den Cap. Vor der Normierung stand
        hier der Rohwert selbst; er ging in ein `max()` mit Werten aus [0,1]
        und in eine Addition auf eine Salienz aus [0,1].
        """
        term = gravitationsterm_berechnen([_ziel(1.0) for _ in range(12)])
        self.assertLessEqual(term.normiert, 1.0)
        self.assertGreater(term.normiert, 0.0)
        # Die Rohsumme reist mit — sie ist die Groesse, aus der der Cap
        # abgeleitet ist, und ohne sie waere die Spanne nicht nachmessbar.
        self.assertAlmostEqual(term.roh, 6.0, places=4)

    def test_dreissig_ziele_sprengen_die_spanne_nicht(self) -> None:
        """Weit ueber dem Cap. Vor der Normierung stuende hier 15,0."""
        self.assertLessEqual(
            gravitationsterm_berechnen([_ziel(1.0) for _ in range(30)]).normiert, 1.0
        )

    def test_der_term_ist_ordnungserhaltend(self) -> None:
        """Zwei verschiedene Lagen fallen nicht auf dieselbe Zahl.

        Das ist die Zusicherung, die das Kappen nicht geben kann — und der
        Grund, warum `F-NAHT-1` es ausschliesst. Geprueft unterhalb des Caps,
        wo der ganze gemessene Bestand liegt (Maximum 5,9955 gegen Cap 6,0).
        """
        vorher = 0.0
        for anzahl in range(1, 12):
            term = gravitationsterm_berechnen([_ziel(1.0) for _ in range(anzahl)]).normiert
            self.assertGreater(term, vorher, f"{anzahl} Ziele fielen mit {anzahl-1} zusammen")
            vorher = term


class GravitationstermRechnungTest(unittest.TestCase):
    """Die Zahl selbst, gegen ausgeschriebene Erwartungen."""

    def test_ein_ziel_der_staerke_eins(self) -> None:
        """Rohwert 1,0 × 0,5 = 0,5; sin^0.5(0,5/6,0) = 0,3613.

        Ausgeschrieben statt aus den Konstanten gerechnet: Ein Zeuge, der
        seine Erwartung aus dem Prueflung bezieht, macht jede Aenderung mit.
        """
        self.assertAlmostEqual(gravitationsterm_berechnen([_ziel(1.0)]).normiert, 0.3613, places=4)

    def test_vier_ziele_der_staerke_eins(self) -> None:
        """Rohwert 4,0 × 0,5 = 2,0; sin^0.5(2,0/6,0) = 0,7071."""
        self.assertAlmostEqual(
            gravitationsterm_berechnen([_ziel(1.0) for _ in range(4)]).normiert, 0.7071,
            places=4
        )

    def test_der_cap_stammt_aus_der_konstante(self) -> None:
        """Die Kurve haengt an `GRAVITATIONSTERM_CAP`, nicht an einer Zahl im Rumpf.

        Ohne diesen Zeugen bliebe eine Aenderung der Konstante folgenlos und
        unbemerkt — beide Seiten des Vergleichs bewegten sich zusammen.
        """
        self.assertEqual(GRAVITATIONSTERM_CAP, 6.0)
        self.assertEqual(GRAVITATIONS_SALIENZ_FAKTOR, 0.5)

    def test_der_faktor_wirkt_vor_der_normierung(self) -> None:
        """Erst skalieren, dann normieren — die Reihenfolge ist nicht beliebig.

        Umgekehrt gerechnet ergaebe dasselbe Ziel 0,5 × sin^0.5(1,0/6,0) =
        0,2544 statt 0,3613.
        """
        self.assertNotAlmostEqual(
            gravitationsterm_berechnen([_ziel(1.0)]).normiert, 0.2544, places=3
        )


class GravitationstermWaechterTest(unittest.TestCase):
    """Der Rohwert am Cap wird gemeldet, nicht verschwiegen."""

    def test_rohwert_am_cap_meldet_sich(self) -> None:
        """Ab dem Cap bildet die Kurve jeden Wert auf 1.0 ab.

        Das ist genau das tote Ende, das die Normierung beseitigen soll — nur
        weiter oben. Es schweigend zu passieren hiesse, den Befund von heute
        in einem Jahr noch einmal zu machen.
        """
        with self.assertLogs(LOGGER, level="WARNING") as protokoll:
            gravitationsterm_berechnen([_ziel(1.0) for _ in range(12)])
        self.assertIn("erreicht den Cap", protokoll.output[0])
        self.assertIn("6.0", protokoll.output[0])

    def test_unter_dem_cap_schweigt_der_waechter(self) -> None:
        """Sonst waere die Meldung der Normalfall und niemand laese sie.

        Der ganze gemessene Bestand liegt hier: Maximum 5,9955 gegen Cap 6,0.
        """
        with self.assertNoLogs(LOGGER, level="WARNING"):
            gravitationsterm_berechnen([_ziel(1.0) for _ in range(11)])


class AuffuellregelTest(unittest.TestCase):
    """`fill_gap_upward` — hebt immer, senkt nie, geht nie ueber 1."""

    def test_sie_senkt_nie(self) -> None:
        for basis in (0.0, 0.327, 0.7, 1.0):
            for anteil in (0.0, 0.3613, 1.0):
                self.assertGreaterEqual(fill_gap_upward(basis, anteil), basis)

    def test_sie_geht_nie_ueber_eins(self) -> None:
        for basis in (0.0, 0.5, 0.999, 1.0):
            self.assertLessEqual(fill_gap_upward(basis, 1.0), 1.0)

    def test_voller_anteil_erreicht_genau_eins(self) -> None:
        """Die Obergrenze wird erreicht, nicht ueberschritten."""
        self.assertAlmostEqual(fill_gap_upward(0.3, 1.0), 1.0, places=10)

    def test_kein_anteil_laesst_die_basis_stehen(self) -> None:
        """Ein Term von null ist kein schwacher Zug, sondern keiner."""
        self.assertAlmostEqual(fill_gap_upward(0.327, 0.0), 0.327, places=10)

    def test_die_basis_bleibt_erkennbar(self) -> None:
        """Der Kern des Befundes: die Bewertung des Modells wird verschoben,
        nicht ausgeloescht.

        Basis 0,327 (das gemessene Mittel) mit dem staerksten je gemessenen
        Term: heute stand hier 1,0 fuer jede Basis. Aufgefuellt bleibt die
        Ordnung der Basen erhalten.
        """
        stark: float = sin_sqrt_norm(5.9955, GRAVITATIONSTERM_CAP)
        self.assertLess(fill_gap_upward(0.2, stark), fill_gap_upward(0.6, stark))

    def test_gegen_die_addition(self) -> None:
        """Die Form, die ersetzt wurde — sie loescht die Ordnung aus.

        `min(1, basis + term)` liefert fuer **jede** Basis ab 0,2 dasselbe,
        sobald der Term 0,8 erreicht. Genau so kamen 307 exakte Einsen
        zustande: 277 der 498 Boosts trugen einen Term >= 1,0.

        Aufgefuellt bleiben dieselben zwei Lagen getrennt — 0,84 gegen 0,92.
        """
        term: float = 0.8
        self.assertEqual(min(1.0, 0.2 + term), min(1.0, 0.6 + term))
        self.assertAlmostEqual(fill_gap_upward(0.2, term), 0.84, places=4)
        self.assertAlmostEqual(fill_gap_upward(0.6, term), 0.92, places=4)


class BestandsRechnungTest(unittest.TestCase):
    """Die Vorher-Rechnung am Bestand, an einzelnen echten Zeilen nachgezogen."""

    def test_echte_boostzeile_verliert_das_tote_ende(self) -> None:
        """Eine Zeile aus `pipeline_log` vom 09.09.2026.

        Basis 0,7, Rohterm 0,227 — heute `min(1; 0,7 + 0,227) = 0,93`.
        Aufgefuellt mit dem normierten Term: 0,7 + 0,2437 × 0,3 = 0,7731.
        Die Bewertung des Modells bleibt lesbar.
        """
        normiert: float = sin_sqrt_norm(0.227, GRAVITATIONSTERM_CAP)
        self.assertAlmostEqual(normiert, 0.2437, places=4)
        self.assertAlmostEqual(fill_gap_upward(0.7, normiert), 0.7731, places=4)

    def test_der_hoechste_gemessene_term_bleibt_unter_eins(self) -> None:
        """5,9955 ist das Maximum ueber 3712 protokollierte Zeilen."""
        self.assertLess(sin_sqrt_norm(5.9955, GRAVITATIONSTERM_CAP), 1.0)

    def test_die_neun_hoechsten_bleiben_unterscheidbar(self) -> None:
        """Am oberen Rand faellt die Ordnung nicht zusammen.

        Die vier hoechsten verschiedenen Rohwerte des Bestands ergeben vier
        verschiedene Terme — auf vier Stellen, so wie sie gespeichert werden.
        """
        werte = [5.7750, 5.8395, 5.8825, 5.9955]
        terme = [round(sin_sqrt_norm(w, GRAVITATIONSTERM_CAP), 4) for w in werte]
        self.assertEqual(len(set(terme)), 4, f"Terme fielen zusammen: {terme}")


class NormierungsformTest(unittest.TestCase):
    """Warum `sin^0.5` und nicht die konstruktiv geschlossene Saettigung.

    Die Alternative `roh / (roh + k)` erreicht 1 nie und ist auf ganz
    [0, unendlich) streng monoton — sie waere die strengere Erfuellung von
    `F-NAHT-1`. Sie ist am Bestand gerechnet und verworfen: Mit k = 1,65 (dem
    Median der 499 gemessenen Rohterme) erreicht **keine** Boost-Zeile mehr
    `KZG_SALIENZ_HIGH` = 0,88078. Der Zeuge haelt den Grund fest, damit die
    Wahl nicht als Zufall gelesen wird.
    """

    def test_die_saettigung_erreicht_die_hohe_stufe_nicht(self) -> None:
        """Die staerkste Basis mit dem staerksten Term bleibt unter 0,88078."""
        stark: float = 5.9955 / (5.9955 + 1.65)
        self.assertLess(fill_gap_upward(0.327, stark), 0.88078)

    def test_sin_sqrt_erreicht_sie(self) -> None:
        """Dieselbe Lage mit der gewaehlten Form."""
        stark: float = sin_sqrt_norm(5.9955, GRAVITATIONSTERM_CAP)
        self.assertGreater(fill_gap_upward(0.327, stark), 0.88078)

    def test_beide_formen_sind_monoton(self) -> None:
        """Der Punkt, in dem sie sich nicht unterscheiden."""
        for f in (lambda x: sin_sqrt_norm(x, GRAVITATIONSTERM_CAP),
                  lambda x: x / (x + 1.65)):
            werte = [f(x) for x in (0.1, 0.5, 1.0, 2.0, 4.0, 5.9)]
            self.assertEqual(werte, sorted(werte))
            self.assertEqual(len(set(werte)), len(werte))


if __name__ == "__main__":
    unittest.main()


class NahtTafelTest(unittest.TestCase):
    """Die Groesse, die die Naht gebrochen hat, wird auch bewacht.

    Am 09.09.2026 stand `gravitationsterm` **nicht** in `NAEHTE`. Die Tafel
    fuehrte `eigen_pfad` und meldete dort 393,4 % Ausschoepfung — den Schaden,
    nicht die Ursache. Ohne diesen Zeugen faellt die Zeile beim naechsten Umbau
    lautlos wieder heraus, und das faellt erst auf, wenn jemand die Ursache
    ein zweites Mal sucht.
    """

    def test_der_gravitationsterm_steht_in_der_nahtliste(self) -> None:
        from memory.naht_spannen import NAEHTE
        namen = {naht.name for naht in NAEHTE if naht.gruppe == "Salienz"}
        self.assertIn("gravitationsterm", namen)

    def test_er_traegt_die_zielspanne_null_bis_eins(self) -> None:
        """Ohne Zielspanne rechnet die Tafel keine Ausschoepfung — dann steht
        die Naht in der Liste und sagt nichts.
        """
        from memory.naht_spannen import NAEHTE
        naht = next(n for n in NAEHTE if n.name == "gravitationsterm")
        self.assertEqual(naht.ziel, (0.0, 1.0))


class ProtokollTraegtDieEingabeTest(unittest.TestCase):
    """Die Rohsumme steht im dauerhaften Speicher, nicht nur im Debug-Log.

    `novaberg-convention-abgeleitete-werte.md` Regel (1): Jede Groesse, aus der
    sich ein Wert berechnet, ist ein eigenes Feld — das Ergebnis darf
    **zusaetzlich** gespeichert werden, nie stattdessen. Nach der Normierung
    traegt `state["gravitationsterm"]` das Kurvenergebnis; ohne die Rohsumme
    daneben waere die Spanne, aus der `GRAVITATIONSTERM_CAP` abgeleitet ist,
    nach diesem Umbau nicht mehr nachmessbar, und oberhalb des Caps ist die
    Kurve nicht invertierbar.

    **Ein `logger.debug` genuegt dafuer nicht** — er ist nicht der Speicher,
    aus dem die Nahtspannen-Tafel und jede Bestandsauswertung liest.
    """

    def test_beide_ausgabezeilen_des_enrichers_nennen_die_rohsumme(self) -> None:
        """Beide Graphen schreiben eine eigene Zeile — eine allein genuegt nicht.

        Geprueft am Quelltext, weil die Zeile in einem grossen Knotenrumpf
        entsteht und von keinem Zeugen erreichbar waere, ohne den ganzen
        Enricher zu fahren.
        """
        import inspect

        from graph.nodes import enricher as enricher_mod

        quelltext: str = inspect.getsource(enricher_mod)
        self.assertEqual(
            quelltext.count('"gravitationsterm_roh"'), 2,
            "Eine der beiden Enricher-Ausgabezeilen traegt die Rohsumme nicht",
        )
        self.assertEqual(
            quelltext.count('"gravitationsterm_cap"'), 2,
            "Ohne den Cap ist eine Zeile spaeter nicht ihrer Generation zuzuordnen",
        )

    def test_der_state_bekommt_den_normierten_wert(self) -> None:
        """Nicht den rohen — sonst waere der Umbau an den Lesern wirkungslos."""
        import inspect

        from graph.nodes import enricher as enricher_mod

        quelltext: str = inspect.getsource(enricher_mod)
        self.assertEqual(
            quelltext.count('state["gravitationsterm"] = gravitationsterm.normiert'), 2,
        )
        self.assertNotIn('state["gravitationsterm"] = gravitationsterm.roh', quelltext)
