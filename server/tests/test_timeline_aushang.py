"""Tests: Eingetragen wird nur, worum der Nutzer ausdruecklich bittet.

Ziel: Eine Aussage oder beilaeufige Erwaehnung mit Zeitpunkt legt keinen
Termin an; ein ausdruecklicher Auftrag oder eine Frage an die Zeitachse
erreicht den TimelineAgent. Entschieden am 13.09.2026 — der Aushang nannte bis
dahin Aussagen und beilaeufige Erwaehnungen als Ausloeser, die Klassifikation
wertete sie als `create`, und der offene Defekt `TIMELINE-SCHREIBT-OHNE-AUFTRAG`
verlangte das Gegenteil.

Zwei Sperren, jede fuer sich bezeugt:
  * **Der Empfang** — der Timeline-Zettel nennt keine Aussage als Ausloeser und
    fuehrt die Erwaehnung als Negativfall.
  * **Die Fachabteilung** — die Vorpruefung der Klassifikation weist die
    Erwaehnung als `rejected` aus, nicht als `create`. Der Empfang stellt im
    Zweifel zu; ohne diese zweite Sperre schriebe jeder Zweifelsfall.

**Was dieser Test NICHT kann:** ob das Modell den Saetzen folgt. Das
entscheidet ein Lauf gegen das Gespraechsmodell, kein Zeuge.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
import unittest

from agents import AgentRegistry, discover_agents
from agents.nmcp import aushaenge_sammeln
from agents.timeline.dispatch import REJECTION_SUGGESTION
from agents.timeline.klassifikation import _build_classify_prompt
from config import PROMPTS
from plugins import discover_managers


def _timeline_block(brett: str) -> str:
    """Schneidet den Zettel mit der Marke TIMELINE-ERKENNUNG aus dem Brett.

    Vorbedingung: `brett` ist der Text von `aushaenge_sammeln`.
    Nachbedingung: der Text von der Marke bis zur naechsten Marke oder zum Ende;
    leer, wenn die Marke fehlt.
    """
    treffer = re.search(
        r"^TIMELINE-ERKENNUNG:.*?(?=^[A-Z][A-Z-]+-ERKENNUNG:|^[A-Z ]+:\n|\Z)",
        brett, re.M | re.S,
    )
    return treffer.group(0) if treffer else ""


class EmpfangTest(unittest.TestCase):
    """Der Timeline-Zettel verlangt einen Auftrag."""

    @classmethod
    def setUpClass(cls) -> None:
        """Faehrt den Bestand — das Brett entsteht aus den registrierten Diensten."""
        discover_managers()
        discover_agents()
        cls.block = _timeline_block(aushaenge_sammeln("user"))

    def test_zettel_steht_im_brett(self) -> None:
        """Ohne Zettel pruefen die folgenden Zeugen einen leeren Text."""
        self.assertTrue(self.block, "Das Brett traegt keinen TIMELINE-ERKENNUNG-Zettel")

    def test_zettel_nennt_keine_aussage_als_ausloeser(self) -> None:
        """Die frueheren Ausloeser-Zeilen fuer Aussage und Erwaehnung sind weg."""
        for zeile in ("- Aussagen:", "- Beilaeufig:", "- Mit Uhrzeit:"):
            self.assertNotIn(zeile, self.block)

    def test_zettel_sagt_dass_zeitangabe_allein_kein_auftrag_ist(self) -> None:
        """Der Satz, an dem das Modell die Erwaehnung vom Auftrag trennt."""
        self.assertIn("Eine\nZeitangabe allein ist kein Auftrag", self.block)

    def test_erwaehnung_ist_negativfall(self) -> None:
        """Die Erwaehnung steht in derselben Form wie die anderen Negativfaelle."""
        agent = AgentRegistry.finden("timeline")
        self.assertIsNotNone(agent)
        erwaehnung = [f for f in agent.negativfaelle if "beilaeufige Erwaehnung" in f]
        self.assertEqual(len(erwaehnung), 1)
        self.assertIn(erwaehnung[0], self.block)


class FachabteilungTest(unittest.TestCase):
    """Die Klassifikation lehnt die Erwaehnung ab."""

    def setUp(self) -> None:
        """Die Vorpruefung, wie sie in den Prompt geht."""
        self.task = PROMPTS["classify_timeline.task"]

    def test_erwaehnung_steht_unter_rejected(self) -> None:
        """Die Beispiele, die bis zum 13.09.2026 unter create standen."""
        rejected = self.task.split("Beispiele fuer rejected:")[1].split("Beispiele fuer ECHTE")[0]
        for beispiel in ("Morgen um 10 Uhr geht es los", "Am Donnerstag habe ich Zahnarzt",
                         "Morgen muss ich Getraenke kaufen"):
            self.assertIn(beispiel, rejected)

    def test_create_nimmt_keine_beilaeufige_erwaehnung_mehr(self) -> None:
        """Die Zeile, die die Erwaehnung ausdruecklich zum Auftrag erklaerte."""
        self.assertNotIn("AUCH beilaeufige Erwaehnung", self.task)
        self.assertNotIn('"Am Donnerstag habe ich Zahnarzt" -> create', self.task)

    def test_zusammengesetzter_prompt_fuehrt_keine_aussage_als_create(self) -> None:
        """Der Prompt, den das Modell sieht, nicht nur der Vorpruefungs-Block.

        Die Fachsprache steht im selben System-Prompt und fuehrte bis zum
        14.09.2026 eine Aussage als `create`-Beispiel — der Zeuge auf den
        Vorpruefungs-Block allein sah das nicht (zweite Kontrolle).
        """
        prompt = _build_classify_prompt(None, None)
        beispiele = re.findall(r'User: "([^"]+)" -> "create:', prompt)
        self.assertTrue(beispiele, "Keine create-Beispiele im zusammengesetzten Prompt")
        for satz in beispiele:
            with self.subTest(satz=satz):
                self.assertRegex(
                    satz.lower(), r"^(hau|trag|merk|erinner|notier|leg)",
                    f"create-Beispiel ohne Bitte: {satz}",
                )

    def test_gegenangebot_nennt_eine_bitte(self) -> None:
        """Eine Ablehnung schickt den Nutzer nicht in die naechste Ablehnung."""
        self.assertIn("Trag mir", REJECTION_SUGGESTION)
        self.assertNotIn("Nenne einen Zeitpunkt und das Ereignis", REJECTION_SUGGESTION)


if __name__ == "__main__":
    unittest.main()
