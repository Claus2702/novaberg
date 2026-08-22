"""Zeugen dafuer, dass die Verdichtung den Ausgang des Turns sieht.

Ziel: Hat ein Dienst in diesem Turn **abgelehnt**, steht das im Prompt der
Verdichtung — als Tatsache neben dem Text, nicht als Regel.

Hintergrund (`FALSCHE-BESTAETIGUNG-WIRD-ERINNERUNG`, 18.08.2026): Nach einem
misslungenen Notizauftrag antwortete die Figur *„Ich habe es notiert … Aber da
gab es ein kleines technisches Stolpern"* — ein Satz, der sich in zwei Saetzen
selbst widerspricht. **Verdichtet wurde die falsche Haelfte:** *„Nova hat
notiert, dass der Gasvertrag gekuendigt werden soll."* Beim naechsten Abruf
steht dieser Satz ohne den widersprechenden Nachsatz da, und damit ist aus
einer falschen Bestaetigung eine dauerhafte Erinnerung geworden.

Die Ursache ist eine Sichtluecke, kein Denkfehler des Modells: Die Verdichtung
bekam `reiz` und `response` — den Text der Aeusserung und den Text der Antwort.
Was in dem Turn *geschah*, stand in keinem von beiden.

**Was diese Zeugen pruefen und was nicht.** Sie pruefen, dass der Block steht
und was er traegt — das ist zusicherbar. Ob das Modell ihm folgt, ist keine
Zusicherung und gehoert in eine Messung am echten Turn; sie steht am Eintrag.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from agents.base import AgentResult, Korrektur
from agents.kzg.dispatch import abgelehnte_ausgaenge
from agents.kzg.verdichtung import verdichten

# Der Fall vom 18.08.2026, in seiner Struktur nachgebaut: Der Dienst lehnt ab,
# die Antwort behauptet die Handlung trotzdem.
BEFUND: str = "Kein konkreter Auftrag erkennbar; lediglich eine Feststellung."
ANTWORT_MIT_FALSCHER_BESTAETIGUNG: str = (
    "Ich habe es notiert. Aber da gab es ein kleines technisches Stolpern."
)


def _ergebnis(agent: str, status: str, mit_korrektur: bool = True) -> AgentResult:
    """Ein AgentResult, das die Pflichtfeld-Pruefung seines Kanons besteht."""
    return AgentResult(
        agent_name = agent,
        ergebnis   = None,
        status     = status,
        fehler     = "Zeitueberschreitung" if status == "fehler" else None,
        rueckfrage = "Welchen Termin meinst du?" if status == "rueckfrage" else None,
        korrektur  = Korrektur(
            befund    = BEFUND,
            beleg     = "Der Auftrag nennt keinen Zeitpunkt.",
            vorschlag = "Formuliere den Auftrag als Notiz ohne Frist.",
        ) if (status == "abgelehnt" and mit_korrektur) else None,
    )


def _state(ausgaenge: list) -> dict:
    """Der AgentState, wie ihn `dispatch_kzg` an die Verdichtung reicht."""
    return {
        "parameter": {
            "reiz":            "Notier mir bitte den Gasvertrag.",
            "response":        ANTWORT_MIT_FALSCHER_BESTAETIGUNG,
            "segment":         ANTWORT_MIT_FALSCHER_BESTAETIGUNG,
            "segment_index":   0,
            "segment_gesamt":  1,
            "agent_ausgaenge": ausgaenge,
        },
        "kontext":  {"beobachter": "assistant", "graph_rolle": "character"},
        "schritte": [],
    }


class AusgaengeSammelnTest(unittest.TestCase):
    """`abgelehnte_ausgaenge` — welcher Ausgang zaehlt und welcher nicht."""

    def test_abgelehnt_wird_mit_befund_uebernommen(self) -> None:
        ausgaenge = abgelehnte_ausgaenge(
            {"agent_results": [_ergebnis("timeline", "abgelehnt")]}
        )
        self.assertEqual(ausgaenge, [{"agent": "timeline", "befund": BEFUND}])

    def test_abgeschlossen_erzeugt_keinen_ausgang(self) -> None:
        """Der haeufige Fall bleibt unberuehrt — sonst traegt jeder Turn den Block."""
        ausgaenge = abgelehnte_ausgaenge(
            {"agent_results": [_ergebnis("timeline", "abgeschlossen")]}
        )
        self.assertEqual(ausgaenge, [])

    def test_fehler_ist_keine_ablehnung(self) -> None:
        """Eine Stoerung geht den Betreiber an, ein Urteil den Auftraggeber.

        Die Trennung ist der Kern der vier Ausgaenge (`agents/base.py`). Wer
        den Fehler mitnimmt, schreibt eine Betriebsstoerung ins Gedaechtnis
        eines Menschen.
        """
        ausgaenge = abgelehnte_ausgaenge(
            {"agent_results": [_ergebnis("timeline", "fehler")]}
        )
        self.assertEqual(ausgaenge, [])

    def test_rejected_zaehlt_nicht_als_ablehnung(self) -> None:
        """Die Vorform ohne Begruendung bleibt aussen vor, wie beim Planner.

        `rejected` ist eine Ablehnung, die ihren Grund nicht nennt
        (`agents/base.py:70`). Ein Ausgangsblock ohne Begruendung saehe im
        Prompt aus wie eine Tatsache und traege keine — und `graph/nodes/
        planner.py:60` laesst ihn aus demselben Grund unbehandelt.
        """
        ausgaenge = abgelehnte_ausgaenge(
            {"agent_results": [_ergebnis("timeline", "rejected")]}
        )
        self.assertEqual(ausgaenge, [])

    def test_ohne_agent_results_leere_liste(self) -> None:
        """Kein Turn muss Agenten gerufen haben."""
        self.assertEqual(abgelehnte_ausgaenge({}), [])

    def test_ablehnung_ohne_korrektur_faellt_laut_aus(self) -> None:
        """Der Riegel gegen ein Objekt, das an der Pflichtpruefung vorbeikam.

        `AgentResult.__post_init__` erzwingt die Korrektur — deshalb wird sie
        hier nachtraeglich entfernt, statt ein ungueltiges Objekt zu bauen.
        """
        kaputt = _ergebnis("timeline", "abgelehnt")
        kaputt.korrektur = None
        with self.assertLogs("ki_server.agents.kzg.dispatch", level="ERROR") as log:
            ausgaenge = abgelehnte_ausgaenge({"agent_results": [kaputt]})
        self.assertEqual(ausgaenge, [])
        self.assertIn("ohne Korrektur", "\n".join(log.output))

    def test_zwei_ablehnungen_in_der_reihenfolge_der_ergebnisse(self) -> None:
        ausgaenge = abgelehnte_ausgaenge({"agent_results": [
            _ergebnis("timeline", "abgelehnt"),
            _ergebnis("notizen", "abgeschlossen"),
            _ergebnis("dateien", "abgelehnt"),
        ]})
        self.assertEqual([a["agent"] for a in ausgaenge], ["timeline", "dateien"])


class AusgangImPromptTest(unittest.TestCase):
    """Der Block steht im Prompt — oder er steht nicht, wenn nichts abgelehnt wurde."""

    def _verdichten(self, ausgaenge: list) -> str:
        """Ruft die Verdichtung und liefert die abgesetzte Nutzernachricht."""
        antwort = MagicMock()
        antwort.text = "Nova wollte notieren, der Dienst lehnte ab."
        with patch("agents.kzg.verdichtung.model_service") as dienst:
            dienst.chat.submit_sync.return_value = antwort
            verdichten(_state(ausgaenge))
            anfrage = dienst.chat.submit_sync.call_args[0][0]
        return anfrage.messages[0]["content"]

    def test_ablehnung_setzt_den_block_mit_dienst_und_grund(self) -> None:
        nachricht = self._verdichten([{"agent": "timeline", "befund": BEFUND}])
        self.assertIn("[TATSAECHLICHER AUSGANG]", nachricht)
        self.assertIn("timeline", nachricht)
        self.assertIn("ABGELEHNT", nachricht)
        self.assertIn(BEFUND, nachricht)

    def test_ohne_ablehnung_kein_block(self) -> None:
        """Die Gegenprobe: Der haeufige Turn traegt den Block nicht."""
        nachricht = self._verdichten([])
        self.assertNotIn("[TATSAECHLICHER AUSGANG]", nachricht)

    def test_block_steht_vor_dem_bewertungsobjekt(self) -> None:
        """Die Tatsache kommt vor dem Text, ueber den sie urteilt.

        Steht sie dahinter, liest das Modell zuerst die Behauptung und danach
        den Widerspruch — und die Reihenfolge entscheidet bei einem Prompt
        mehr als bei einer Funktion.
        """
        nachricht = self._verdichten([{"agent": "timeline", "befund": BEFUND}])
        self.assertLess(
            nachricht.index("[TATSAECHLICHER AUSGANG]"),
            nachricht.index("[BEWERTUNGSOBJEKT]"),
        )

    def test_zwei_dienste_stehen_beide_im_block(self) -> None:
        nachricht = self._verdichten([
            {"agent": "timeline", "befund": BEFUND},
            {"agent": "notizen",  "befund": "Kein Text zum Ablegen."},
        ])
        self.assertIn("timeline", nachricht)
        self.assertIn("notizen", nachricht)
        self.assertIn("Kein Text zum Ablegen.", nachricht)


if __name__ == "__main__":
    unittest.main()
