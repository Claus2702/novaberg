"""Tests: Ein gescheiterter Agent sagt dem Nutzer, dass nichts geschrieben ist.

Ziel: Der `[AUFGABE]`-Block fuer `status="fehler"` traegt **die Tatsache** —
es ist nichts eingetragen — und nicht nur die Stoerungsmeldung. Der Text des
Agenten geht vollstaendig mit, und wo er eine Frage stellt, wird sie
weitergereicht statt erklaert.

Hintergrund, gemessen am 01.09.2026 an einem Gespraech mit mehreren
Terminauftraegen:

    18:48:52  Agent 'timeline'  status=fehler   "Konnte kein Datum erkennen.
                                                 Wann soll ... stattfinden?"
    18:48:52  task_block erstellt (203 Zeichen) — der Block war da
    18:50:20  Antwort bestaetigt den Eintrag als erledigt

Dreimal in Folge derselbe Ausgang (18:48:52, 18:54:59, 18:56:31). **Der Block
erreichte den Prompt jedes Mal und setzte sich kein einziges Mal durch.** Der
alte Wortlaut nannte weder den Schreibvorgang noch seine Folge:

    "Bei der Verarbeitung ist ein Fehler aufgetreten: {fehler_texte}
     Erklaere dem Nutzer kurz was schiefging."

Das Vorbild steht im Haus: `responder.aufgabe_ablehnung` sagt seit dem
20.08.2026 ausdruecklich *„Es wurde nichts eingetragen"* und *„Sag dem Nutzer
beides"* — und ist der Block, der wirkt.

Zeugen dieser Datei:
  * **Geprueft wird die Aussage, nicht der Satzbau.** Dass der Block eine
    Verneinung ueber den Schreibvorgang traegt, ist die Bedingung; welches
    Verb sie waehlt, ist es nicht.
  * **Die Gegenprobe steht daneben.** Der alte Wortlaut ist als Konstante
    mitgefuehrt und faellt an derselben Bedingung durch — ohne ihn bestuende
    der Zeuge auch dann, wenn die Bedingung nichts unterschiede.
  * **Der Agententext ist der Nutzwert.** Er traegt in vier von fuenf
    Fehlerquellen des Timeline-Agenten eine beantwortbare Frage; wird er
    gekuerzt oder umschrieben, ist der Fehlschlag eine Sackgasse.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
import unittest

from agents.base import AgentResult
from graph.nodes import planner as planner_mod

# Der Wortlaut, der am 01.09.2026 dreimal nicht durchkam. Er steht hier als
# Gegenprobe und nicht als Erinnerung: Ein Zeuge, der nur die neue Fassung
# bestaetigt, sagt nichts darueber, ob er die alte abgewiesen haette.
ALTE_FASSUNG: str = (
    "[AUFGABE]\n"
    "Bei der Verarbeitung ist ein Fehler aufgetreten:\n"
    "- Agent 'timeline': Konnte kein Datum erkennen.\n\n"
    "Erklaere dem Nutzer kurz was schiefging."
)

# Eine Verneinung ueber den Schreibvorgang, in den Formen, die der Block
# waehlen darf. Geprueft wird die Aussage; das Verb ist frei.
NICHTS_GESCHRIEBEN: re.Pattern = re.compile(
    r"nichts\s+(eingetragen|geaendert|geloescht|gespeichert|angelegt|notiert)",
    re.IGNORECASE,
)

#: **Synthetisch**, nicht aus einem Gespraech: Der Zeuge prueft, dass der Text
#: des Agenten **unveraendert** durchkommt — welcher Vorgang darin steht, traegt
#: dazu nichts bei (`32_VEROEFFENTLICHUNG` §1a).
AGENTENTEXT: str = (
    "Konnte kein Datum erkennen. Wann soll 'Wartung der Anlage' stattfinden?"
)


def _fehler_result(text: str = AGENTENTEXT) -> AgentResult:
    """Das Ergebnis, das der Timeline-Agent am 01.09.2026 dreimal lieferte."""
    return AgentResult(
        agent_name = "timeline",
        ergebnis   = None,
        status     = "fehler",
        fehler     = text,
    )


class DerBlockNenntDieTatsacheTest(unittest.TestCase):
    """Ohne sie ist der Fehler ein Nebengeraeusch neben der Erfolgsmeldung.

    Genau das war die Bedingung, unter der die Antwort entstand: Der Nutzer
    hatte um einen Eintrag gebeten, der Block meldete eine Stoerung ohne
    Folge, und die Figur erzaehlte den Auftrag zu Ende.
    """

    def test_der_block_sagt_dass_nichts_geschrieben_wurde(self) -> None:
        block: str = planner_mod._build_task_error([_fehler_result()])

        self.assertRegex(block, NICHTS_GESCHRIEBEN)

    def test_die_alte_fassung_faellt_an_derselben_bedingung_durch(self) -> None:
        """Die Gegenprobe: der Zeuge unterscheidet, statt zu bestaetigen."""
        self.assertNotRegex(ALTE_FASSUNG, NICHTS_GESCHRIEBEN)

    def test_der_block_verlangt_die_ansage_an_den_nutzer(self) -> None:
        """Eine Lage ohne Auftrag ist Kontext, und Kontext bindet nicht.

        Dieselbe Bauregel wie beim Verfasser-Auftrag (12./13.08.2026): Ein
        Block, der nur beschreibt, setzt sich gegen den Zug des Modells nicht
        durch.
        """
        block: str = planner_mod._build_task_error([_fehler_result()])

        self.assertRegex(block, r"Sag\s+ihm|Sag\s+es\s+ihm|Sag\s+dem\s+Nutzer")


class DerAgententextGehtVollstaendigMitTest(unittest.TestCase):
    """Er ist der einzige Teil des Blocks, der den Fehlschlag aufloesen kann."""

    def test_der_fehlertext_steht_wortgleich_im_block(self) -> None:
        block: str = planner_mod._build_task_error([_fehler_result()])

        self.assertIn(AGENTENTEXT, block)

    def test_mehrere_fehler_stehen_alle_im_block(self) -> None:
        zweiter: str = "Kein Termin 'Quartalsbericht' gefunden."
        block: str = planner_mod._build_task_error(
            [_fehler_result(), _fehler_result(zweiter)]
        )

        self.assertIn(AGENTENTEXT, block)
        self.assertIn(zweiter, block)

    def test_eine_frage_des_agenten_wird_weitergereicht(self) -> None:
        """Vier von fuenf Fehlerquellen des Timeline-Agenten fragen zurueck.

        `crud.py` 122/206/329 und `suche.py` 131 nennen eine fehlende Angabe;
        nur der unbekannte Dispatch ist eine reine Stoerung. Ein Block, der
        „erklaere was schiefging" verlangt, waehlt fuer alle vier die falsche
        Sprechhandlung.
        """
        block: str = planner_mod._build_task_error([_fehler_result()])

        self.assertRegex(block, r"Frage|frag|stell sie")


class DerFehlerGewinntGegenDenErfolgTest(unittest.TestCase):
    """Die Reihenfolge der Ausgaenge ist Teil der Aussage, nicht Beiwerk."""

    def test_der_fehler_waehlt_den_fehlerblock_und_schneidet_den_kontext(self) -> None:
        block, cut = planner_mod._build_task_block([_fehler_result()])

        self.assertRegex(block, NICHTS_GESCHRIEBEN)
        self.assertTrue(cut)

    def test_fehler_und_erfolg_zusammen_ergeben_den_fehlerblock(self) -> None:
        """Ein Teilerfolg darf den Fehlschlag nicht zudecken."""
        erfolg = AgentResult(
            agent_name = "timeline",
            ergebnis   = "Termin 'Wartung der Anlage' eingetragen fuer 02.09.2026",
            status     = "abgeschlossen",
        )

        block, _ = planner_mod._build_task_block([erfolg, _fehler_result()])

        self.assertRegex(block, NICHTS_GESCHRIEBEN)
        self.assertIn(AGENTENTEXT, block)


if __name__ == "__main__":
    unittest.main()
