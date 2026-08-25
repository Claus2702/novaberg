"""Zeugen dafuer, dass eine Bestaetigung kein Datum erfindet.

Ziel: Nennt die Antwort ein Datum, das kein Dienst dieses Turns eingetragen
hat, loest das dieselbe Korrekturrunde aus wie ein widerspruechlicher
Wochentag.

Hintergrund (`RESPONDER-ERFINDET-DATUM`, 17.08.2026): Der Dienst meldete
`Termin 'Meeting mit dem Chef' eingetragen fuer 19.08.2026 14:00`, die Antwort
nannte *„Mittwoch, 20.08., 14:00 Uhr"*. Der Mensch suchte am falschen Tag,
fand nichts und hielt den Schreibpfad fuer defekt — er war es nie.

**Warum es einen zweiten Pruefer braucht.** `widersprueche_finden` faengt den
gemeldeten Fall, weil er einen Wochentag traegt: Der 20.08.2026 ist ein
Donnerstag. Am 22.08.2026 gemessen — derselbe Satz **ohne** Wochentag
(*„am 20.08. um 14 Uhr"*) ergibt **0 Befunde**. Die Pruefung braucht das Paar;
das erfundene Datum allein sieht sie nicht.

**Die Bedingung ist eng, und die Fehlalarm-Zeugen sind der Grund.** Gemeldet
wird nur, wenn eine Quelle ein Datum nennt und die Antwort **keines** der
Quelldaten trifft. Ein zweites Datum neben dem richtigen ist ein Satz ueber
etwas anderes, kein Widerspruch — und ein Fehlalarm schickt eine richtige
Antwort in die Korrekturschleife.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import date
from types import SimpleNamespace

from utils.datum_pruefung import (
    bestaetigung_pruefen,
    bestaetigungsauftrag,
    datumsangaben,
)

# Der Turn vom 17.08.2026, mit seinen echten Werten.
HEUTE:   date = date(2026, 8, 17)
QUELLE:  str  = "Termin 'Meeting mit dem Chef' eingetragen fuer 19.08.2026 14:00"
BELEGT:  date = date(2026, 8, 19)
ERFUNDEN: date = date(2026, 8, 20)


class DatumsangabenTest(unittest.TestCase):
    """Was als Datum erkannt wird — und was nicht."""

    def test_mit_jahr(self) -> None:
        self.assertEqual(datumsangaben("am 19.08.2026 um 14 Uhr", HEUTE), {BELEGT})

    def test_ohne_jahr_nimmt_das_naechstliegende(self) -> None:
        """Ein Datum ohne Jahr meint fast immer das naechstliegende."""
        self.assertEqual(datumsangaben("am 19.08. um 14 Uhr", HEUTE), {BELEGT})

    def test_einstellige_zahlen(self) -> None:
        self.assertEqual(datumsangaben("am 1.9.", HEUTE), {date(2026, 9, 1)})

    def test_unmoegliches_datum_faellt_heraus(self) -> None:
        """32.13. ist kein Datum und erlaubt keine Aussage ueber die Antwort."""
        self.assertEqual(datumsangaben("am 32.13.2026", HEUTE), set())

    def test_ohne_datum_leere_menge(self) -> None:
        self.assertEqual(datumsangaben("Bis gleich!", HEUTE), set())


class BestaetigungPruefenTest(unittest.TestCase):
    """Der Fall selbst — und die vier Lagen, in denen nichts zu melden ist."""

    def test_erfundenes_datum_ohne_wochentag_wird_gefunden(self) -> None:
        """Die Luecke, wegen der dieser Pruefer existiert."""
        abweichungen = bestaetigung_pruefen(
            "Ich habe ihn am 20.08. um 14 Uhr eingetragen.", [QUELLE], HEUTE
        )
        self.assertEqual(len(abweichungen), 1)
        self.assertEqual(abweichungen[0].genannt, ERFUNDEN)
        self.assertEqual(abweichungen[0].belegt, (BELEGT,))

    def test_richtiges_datum_meldet_nichts(self) -> None:
        self.assertEqual(
            bestaetigung_pruefen("Er steht am 19.08. um 14 Uhr.", [QUELLE], HEUTE), []
        )

    def test_richtiges_datum_plus_zweites_meldet_nichts(self) -> None:
        """Der teuerste Fehlalarm waere dieser — eine richtige Antwort.

        *„Der Termin steht am 19.08. — der 25.08. waere mir lieber gewesen."*
        Eine Regel *„jedes Datum muss belegt sein"* schickte diesen Satz in
        die Korrekturschleife.
        """
        self.assertEqual(
            bestaetigung_pruefen(
                "Er steht am 19.08.; der 25.08. waere mir lieber.", [QUELLE], HEUTE
            ), []
        )

    def test_quelle_ohne_datum_meldet_nichts(self) -> None:
        """Ohne Eintrag gibt es nichts zu bestaetigen — jedes Datum der Antwort
        gehoert dann einem anderen Satz.
        """
        self.assertEqual(
            bestaetigung_pruefen(
                "Am 20.08. ist es soweit.", ["Keine Termine gefunden."], HEUTE
            ), []
        )

    def test_ohne_quellen_meldet_nichts(self) -> None:
        """Kein Turn muss Dienste gerufen haben."""
        self.assertEqual(bestaetigung_pruefen("Am 20.08.", [], HEUTE), [])

    def test_leere_antwort_meldet_nichts(self) -> None:
        self.assertEqual(bestaetigung_pruefen("", [QUELLE], HEUTE), [])

    def test_auftrag_nennt_den_belegten_wert(self) -> None:
        """Wer nur erfaehrt, dass etwas falsch war, erfindet den naechsten Wert."""
        abweichungen = bestaetigung_pruefen(
            "Ich habe ihn am 20.08. eingetragen.", [QUELLE], HEUTE
        )
        auftrag = bestaetigungsauftrag(abweichungen)
        self.assertIn("ZEITANGABE FALSCH", auftrag)
        self.assertIn("19.08.2026", auftrag)
        self.assertIn("20.08.2026", auftrag)

    def test_auftrag_ohne_abweichung_ist_leer_und_laut(self) -> None:
        with self.assertLogs("ki_server.datum_pruefung", level="ERROR"):
            self.assertEqual(bestaetigungsauftrag([]), "")


class VerdrahtungImTribunalTest(unittest.TestCase):
    """Den Baustein zu pruefen genuegt nicht — die Verdrahtung ist der Defekt."""

    def _ergebnis(self, status: str, text: str) -> SimpleNamespace:
        """Ein AgentResult, so weit das Tribunal es liest."""
        return SimpleNamespace(agent_name="timeline", status=status, ergebnis=text)

    def _auswerten(self, response: str, results: list) -> dict:
        """Ruft die Auswertung des Tribunals mit drei neutralen Voten."""
        from graph.nodes.tribunal import evaluate
        state: dict = {
            "response":      response,
            "agent_results": results,
            "tribunal_votes": [
                {"agent": a, "vote": "ok", "reasoning": ""}
                for a in ("jurist", "psychologe", "ethik")
            ],
        }
        return evaluate(state)

    def test_erfundenes_datum_hebt_das_urteil_und_erreicht_den_corrector(self) -> None:
        """Ein Befund ohne Eintrag in der Zusammenfassung waere folgenlos —
        der Corrector liest ausschliesslich sie.
        """
        state = self._auswerten(
            "Ich habe ihn am 20.08. um 14 Uhr eingetragen.",
            [self._ergebnis("abgeschlossen", QUELLE)],
        )
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertIn("ZEITANGABE FALSCH", state["tribunal_summary"])
        self.assertIn("19.08.2026", state["tribunal_summary"])

    def test_richtiges_datum_bleibt_ok(self) -> None:
        state = self._auswerten(
            "Er steht am 19.08. um 14 Uhr.",
            [self._ergebnis("abgeschlossen", QUELLE)],
        )
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(state["tribunal_summary"], "")

    def test_abgelehntes_ergebnis_belegt_nichts(self) -> None:
        """Was ein Dienst abgelehnt hat, wurde nicht eingetragen.

        Zaehlte es als Quelle, waere ein abgelehnter Termin ein Beleg fuer
        genau das Datum, das nicht eingetragen wurde — die Pruefung stuende
        dann auf dem Kopf.
        """
        state = self._auswerten(
            "Ich habe ihn am 20.08. eingetragen.",
            [self._ergebnis("abgelehnt", QUELLE)],
        )
        self.assertEqual(state["tribunal_verdict"], "ok")


if __name__ == "__main__":
    unittest.main()
