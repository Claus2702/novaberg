"""Tests fuer das Query Rewriting — der Suchschluessel traegt den Gegenstand.

Ziel: Ein Turn, der seinen Gegenstand nur als Rueckbezug nennt (*„und wie
weist man das nach?"*), sucht nicht mehr ohne ihn. Der Enricher formt aus dem
Verlauf eine eigenstaendige Suchanfrage und bettet **die** ein.

Hintergrund und Messung: Gegen 306 Ausarbeitungen und zehn Verlaeufe mit
anaphorischem Schlussturn erreicht die rohe Aeusserung in **0 von 10** Faellen
die Abrufschwelle (Median-Kosinus 0,1865); das Rewrite auf Frageform in
**5 von 10** (0,4173). Beidseitig gesondet: Bei drei Themenwechseln bleibt der
alte Gegenstand 3/3 unter der Schwelle, bei fuenf fremden Alltagsverlaeufen
kommt in 15/15 Kombinationen nichts darueber.

Die Zeugen:

  * **Der Rueckfall ist der Hauptgegenstand, nicht der Gluecksfall.** Fuenf
    der sieben Zeugen fahren einen Ausgang, in dem das Modell nichts
    Verwertbares liefert — jeder davon muss die rohe Aeusserung ergeben und
    seine Herkunft benennen. Ein Rueckfall, der still dieselbe Zeichenkette
    liefert wie ein Erfolg, waere von aussen nicht unterscheidbar.
  * **Die Argumente werden ueber ihren Namen geprueft, nicht ueber ihre
    Position.** Ein Zeuge, der `call_args.args[0]` liest, faellt auch dann,
    wenn nur die Aufrufform sich aendert.
  * Der Aufruf traegt Frist **und** Ausgabegrenze — beide werden gelesen,
    nicht nur ihre Anwesenheit geprueft.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from config import QUERY_REWRITE_FRIST_S, QUERY_REWRITE_MAX_ZEICHEN
from graph.nodes.enricher import _suchtext_bauen

# Die Feldnamen sind die der Session (`rolle`/`inhalt`), nicht die des
# Chat-Formats. Am 20.08.2026 im Betrieb gemessen: Eine Attrappe mit
# `role`/`content` liess jeden Zeugen gruen und den Verlauf leer beim Modell
# ankommen. Wer hier die Namen aendert, aendert sie am Gegenstand vorbei.
VERLAUF: list[dict] = [
    {"rolle": "user",      "inhalt": "Erklaer mir das Informationsparadoxon."},
    {"rolle": "assistant", "inhalt": "Information geht nach heutigem Stand nicht verloren."},
    {"rolle": "user",      "inhalt": "Und wie weist man das nach?"},
]
ROH = "Und wie weist man das nach?"


def _state() -> dict:
    return {"user_prompt": ROH, "eigener_gedanke": ""}


def _antwort(text: str) -> MagicMock:
    antwort = MagicMock()
    antwort.text = text
    return antwort


class QueryRewriteTest(unittest.TestCase):

    def test_der_rueckbezug_wird_aufgeloest(self) -> None:
        """Der Erfolgsfall: Was das Modell liefert, wird der Suchtext."""
        with patch("graph.nodes.enricher.model_service") as dienst:
            dienst.chat.submit_sync.return_value = _antwort(
                "Wie weist man das Informationsparadoxon nach?"
            )
            text, herkunft = _suchtext_bauen(_state(), VERLAUF)
        self.assertEqual(herkunft, "rewrite")
        self.assertEqual(text, "Wie weist man das Informationsparadoxon nach?")
        self.assertNotEqual(text, ROH)

    def test_der_aufruf_traegt_frist_und_ausgabegrenze(self) -> None:
        """Beide stehen an der Aufrufstelle, nicht am Worker."""
        with patch("graph.nodes.enricher.model_service") as dienst:
            dienst.chat.submit_sync.return_value = _antwort("Eine Suchanfrage")
            _suchtext_bauen(_state(), VERLAUF)
            aufruf = dienst.chat.submit_sync.call_args
        # Ueber den Namen, nicht ueber die Position.
        self.assertEqual(aufruf.kwargs["timeout"], QUERY_REWRITE_FRIST_S)
        self.assertEqual(aufruf.args[0].max_output_tokens, 64)
        self.assertEqual(aufruf.args[0].caller, "query_rewrite")

    def test_der_verlauf_steht_vollstaendig_im_prompt(self) -> None:
        """Kein festes Fenster: Was die Session traegt, sieht das Modell."""
        with patch("graph.nodes.enricher.model_service") as dienst:
            dienst.chat.submit_sync.return_value = _antwort("Eine Suchanfrage")
            _suchtext_bauen(_state(), VERLAUF)
            inhalt = dienst.chat.submit_sync.call_args.args[0].messages[0]["content"]
        for turn in VERLAUF:
            self.assertIn(turn["inhalt"], inhalt)

    def test_zu_wenig_verlauf_bleibt_bei_der_rohen_aeusserung(self) -> None:
        """Ein erster Turn hat keinen Rueckbezug — und kostet keinen Aufruf."""
        with patch("graph.nodes.enricher.model_service") as dienst:
            text, herkunft = _suchtext_bauen(_state(), VERLAUF[:1])
        self.assertEqual((text, herkunft), (ROH, "zu_wenig_verlauf"))
        dienst.chat.submit_sync.assert_not_called()

    def test_leere_antwort_faellt_zurueck(self) -> None:
        with patch("graph.nodes.enricher.model_service") as dienst:
            dienst.chat.submit_sync.return_value = _antwort("   \n  ")
            text, herkunft = _suchtext_bauen(_state(), VERLAUF)
        self.assertEqual((text, herkunft), (ROH, "leer"))

    def test_zu_lange_antwort_faellt_zurueck(self) -> None:
        """Was laenger ist als die Grenze, ist eine Erklaerung, keine Anfrage."""
        with patch("graph.nodes.enricher.model_service") as dienst:
            dienst.chat.submit_sync.return_value = _antwort(
                "x" * (QUERY_REWRITE_MAX_ZEICHEN + 1)
            )
            text, herkunft = _suchtext_bauen(_state(), VERLAUF)
        self.assertEqual((text, herkunft), (ROH, "zu_lang"))

    def test_ein_gescheiterter_aufruf_faellt_zurueck(self) -> None:
        """Jede Stoerung des Aufrufs endet im Rueckfall, nicht im roten Turn."""
        with patch("graph.nodes.enricher.model_service") as dienst:
            dienst.chat.submit_sync.side_effect = TimeoutError("Frist gerissen")
            text, herkunft = _suchtext_bauen(_state(), VERLAUF)
        self.assertEqual((text, herkunft), (ROH, "aufruf_gescheitert"))

    def test_praefix_und_anfuehrungszeichen_fallen_weg(self) -> None:
        """Modelle stellen gern eine Beschriftung davor — sie gehoert nicht in den Vektor."""
        with patch("graph.nodes.enricher.model_service") as dienst:
            dienst.chat.submit_sync.return_value = _antwort(
                '"Suchanfrage: Wie weist man das Informationsparadoxon nach?"\nErklaerung folgt'
            )
            text, herkunft = _suchtext_bauen(_state(), VERLAUF)
        self.assertEqual(herkunft, "rewrite")
        self.assertEqual(text, "Wie weist man das Informationsparadoxon nach?")

    def test_turns_mit_fremden_feldnamen_sind_ein_defekt(self) -> None:
        """Der Riegel gegen den Fehler, den erst der Betrieb gefunden hat.

        Turns unter `role`/`content` statt `rolle`/`inhalt` ergeben einen
        leeren Verlauf. Ohne diesen Riegel ginge das als Rewrite durch: Das
        Modell bekaeme die Aufgabe ohne Verlauf, fragte danach — und **die
        Rueckfrage wuerde der Suchschluessel**. Genau so am 20.08.2026 im
        Betrieb passiert.
        """
        fremd = [{"role": "user", "content": "Erklaer mir das Informationsparadoxon."},
                 {"role": "user", "content": "Und wie weist man das nach?"}]
        with patch("graph.nodes.enricher.model_service") as dienst:
            text, herkunft = _suchtext_bauen(_state(), fremd)
        self.assertEqual((text, herkunft), (ROH, "verlauf_leer"))
        dienst.chat.submit_sync.assert_not_called()

    def test_ein_leerer_reiz_ist_ein_defekt(self) -> None:
        """Ohne Reiz gibt es keinen Suchtext — und das soll wie ein Defekt aussehen."""
        with self.assertRaises(ValueError):
            _suchtext_bauen({"user_prompt": "", "eigener_gedanke": ""}, VERLAUF)


if __name__ == "__main__":
    unittest.main()
