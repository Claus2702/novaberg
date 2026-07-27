"""Tests fuer den Rollen-Switch am Salienz-Prompt (SALIENZ-PROMPT-NUTZER-SCHABLONE).

Befund: Bis Chat 112 ging derselbe, durchgehend aus der Nutzerperspektive
geschriebene Prompt an alle drei Graphen. `salienz.rules.txt` wies woertlich
an, die Salienz ausschliesslich anhand der Eingabe des Nutzers zu bewerten und
die Antwort der Assistentin als Hintergrund zu behandeln. Im CharacterGraph
steht die Nutzereingabe aber im [LAGEBILD] und Novas Aeusserung im
[BEWERTUNGSOBJEKT] — **die Anweisung war exakt invertiert**. Im AgentGraph ist
das Lagebild leer; dort wurde angewiesen, etwas zu bewerten, das es nicht gibt.

Das wiegt seit der Salienz-Formel schwerer, nicht leichter: Die Lesung des
Segmenttexts ist der einzige Antrieb des Eigen-Pfads, der heute etwas
beitraegt, und die einzige segmentweite Groesse im System.

Geprueft wird der zusammengebaute Prompt, nicht die Modellantwort. Ob das
Modell der richtigen Schablone folgt, kann nur eine Messung zeigen; ob es die
richtige Schablone ueberhaupt zu sehen bekommt, gehoert hierher.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import pathlib
import unittest
from unittest.mock import MagicMock

from config import ASSISTANT_NAME
from graph.nodes.salience import _build_salienz_prompt, _aufgaben_block_name
from tests.test_salienz_human_transport import _lauf

# Der Satz, der die Inversion trug. Er darf in keiner Salienz-Prompt-Datei
# mehr vorkommen — auch nicht in einem Connector-Override.
INVERTIERTE_ANWEISUNG: str = "AUSSCHLIESSLICH anhand der EINGABE DES NUTZERS"

# Kennsaetze der drei Lagen, je einer.
NUTZER_LAGE:    str = "was der Nutzer gerade gesagt hat"
ANTWORT_LAGE:   str = "sie hat eben geantwortet"
IMPULS_LAGE:    str = "noch niemandem gesagt"


def _prompt(rolle: str) -> str:
    """Nur den Prompt-Text, ohne den mitgelieferten Blocknamen."""
    return _build_salienz_prompt(rolle)[0]


class RollenBlockTest(unittest.TestCase):
    """Jede Rolle zieht ihren eigenen Aufgaben-Block."""

    def test_jede_rolle_bekommt_ihre_lage(self):
        self.assertIn(NUTZER_LAGE,  _prompt("human"))
        self.assertIn(ANTWORT_LAGE, _prompt("character"))
        self.assertIn(IMPULS_LAGE,  _prompt("agent"))

    def test_keine_rolle_bekommt_eine_fremde_lage(self):
        """Der eigentliche Befund: Der CharacterGraph bekam die Nutzerlage."""
        character: str = _prompt("character")
        self.assertNotIn(NUTZER_LAGE, character)
        self.assertNotIn(IMPULS_LAGE, character)

        agent: str = _prompt("agent")
        self.assertNotIn(NUTZER_LAGE,  agent)
        self.assertNotIn(ANTWORT_LAGE, agent)

        human: str = _prompt("human")
        self.assertNotIn(ANTWORT_LAGE, human)
        self.assertNotIn(IMPULS_LAGE,  human)

    def test_die_drei_prompts_sind_verschieden(self):
        drei: set = {_prompt("human"), _prompt("character"), _prompt("agent")}
        self.assertEqual(len(drei), 3)

    def test_blockname_kommt_mit_dem_prompt_zurueck(self):
        """Ein Rueckgabewert statt zweier Ableitungen — sonst kann das Log eine
        Schablone melden, die nie gezogen wurde."""
        for rolle in ("human", "character", "agent"):
            _, block = _build_salienz_prompt(rolle)
            self.assertEqual(block, _aufgaben_block_name(rolle), rolle)

    def test_geteilte_bloecke_stehen_in_allen_dreien(self):
        """Dimensionen und Regeln haengen nicht an der Rolle — sonst waeren
        die zehn Felder dreimal gepflegt und liefen auseinander."""
        for rolle in ("human", "character", "agent"):
            prompt: str = _prompt(rolle)
            self.assertIn("[DIMENSIONEN]", prompt, f"Rolle {rolle}")
            self.assertIn("[REGELN]",      prompt, f"Rolle {rolle}")
            self.assertIn("ZEITAUSDRUCK_ROH", prompt, f"Rolle {rolle}")

    def test_traeger_wird_ersetzt(self):
        """Ein stehengebliebener Platzhalter wuerde dem Modell woertlich
        vorgelegt."""
        for rolle in ("character", "agent"):
            prompt: str = _prompt(rolle)
            self.assertNotIn("{traeger}", prompt, f"Rolle {rolle}")
            self.assertIn(ASSISTANT_NAME, prompt, f"Rolle {rolle}")

    def test_unbekannte_rolle_faellt_auf_nutzer_zurueck_und_meldet(self):
        with self.assertLogs("ki_server.salience", level="WARNING") as protokoll:
            prompt, block = _build_salienz_prompt("charakter")   # Tippfehler
        self.assertIn("unbekannte graph_rolle", "\n".join(protokoll.output))
        self.assertIn(NUTZER_LAGE, prompt)
        self.assertEqual(block, "salienz.task")

    def test_blockname_und_prompt_stimmen_ueberein(self):
        """Die Abbildung Rolle -> Block wird an zwei Stellen gebraucht. Laufen
        sie auseinander, steht im Log eine Schablone, die nicht gezogen wurde."""
        self.assertEqual(_aufgaben_block_name("human"),     "salienz.task")
        self.assertEqual(_aufgaben_block_name("character"), "salienz.assistant_task")
        self.assertEqual(_aufgaben_block_name("agent"),     "salienz.impuls_task")


class InvertierteAnweisungTest(unittest.TestCase):
    """Der Satz, der den Defekt trug, ist nirgends mehr — auch nicht in einem
    Override."""

    @staticmethod
    def _salienz_dateien() -> list[pathlib.Path]:
        wurzel = pathlib.Path(__file__).resolve().parent.parent / "prompts"
        return sorted(wurzel.glob("*/salienz*.txt"))

    def test_messgeraet_sieht_die_dateien(self):
        """Positivkontrolle vor der Null-Aussage: Ein leerer Glob wuerde die
        Pruefung darunter bestehen lassen, ohne irgendetwas geprueft zu haben."""
        dateien = self._salienz_dateien()
        self.assertGreaterEqual(len(dateien), 6)
        gelesen: str = "\n".join(d.read_text(encoding="utf-8") for d in dateien)
        self.assertIn("[REGELN]", gelesen)

    def test_kein_prompt_traegt_die_invertierte_anweisung(self):
        treffer: list[str] = [
            d.name for d in self._salienz_dateien()
            if INVERTIERTE_ANWEISUNG in d.read_text(encoding="utf-8")
        ]
        self.assertEqual(treffer, [])

    def test_regeln_verweisen_auf_das_bewertungsobjekt(self):
        """Der Ersatz ist rollenneutral: Er nennt den Block, nicht die Person."""
        for datei in self._salienz_dateien():
            if not datei.name.endswith("salienz.rules.txt"):
                continue
            text: str = datei.read_text(encoding="utf-8")
            self.assertIn("[BEWERTUNGSOBJEKT]", text, datei.name)
            self.assertIn("[LAGEBILD]",         text, datei.name)

    def test_skala_liegt_nicht_mehr_in_den_regeln(self):
        """Sie lag dort in zwei Kopien, beide auf die Nutzerlage geschrieben.
        Eine Skala je Lage gehoert in den Lage-Block."""
        for datei in self._salienz_dateien():
            if not datei.name.endswith("salienz.rules.txt"):
                continue
            text: str = datei.read_text(encoding="utf-8")
            self.assertNotIn("Smalltalk, Gruss, Hoeflichkeiten", text, datei.name)


class BlockImPipelineLogTest(unittest.TestCase):
    """Welche Schablone lief, ist ohne Container-Log beantwortbar."""

    @staticmethod
    def _switch(eintraege: list) -> dict:
        return [e for e in eintraege if e.art == "switch"][0].inhalt

    def test_switch_nennt_den_gezogenen_block(self):
        for rolle, erwartet in (
            ("human",     "salienz.task"),
            ("character", "salienz.assistant_task"),
            ("agent",     "salienz.impuls_task"),
        ):
            eintraege, _ = _lauf(rolle, [0.5])
            self.assertEqual(self._switch(eintraege)["aufgaben_block"], erwartet, rolle)

    def test_block_und_rolle_stehen_in_derselben_zeile(self):
        """Getrennt waeren sie beim Auswerten nicht zu korrelieren."""
        eintraege, _ = _lauf("character", [0.5])
        inhalt: dict = self._switch(eintraege)
        self.assertEqual(inhalt["graph_rolle"],    "character")
        self.assertEqual(inhalt["aufgaben_block"], "salienz.assistant_task")


class PromptAmModellTest(unittest.TestCase):
    """Was wirklich ans Modell geht — nicht, was daneben gebaut wird.

    Diese Klasse gibt es, weil die erste Gegenprobe gruen blieb: Der Node zog
    testweise fuer jede Rolle die Nutzer-Schablone, und kein Test merkte es.
    Die Log-Zeile leitete den Blocknamen unabhaengig vom Prompt ab und meldete
    weiterhin das Richtige. Geprueft wurde damit eine zweite Ableitung, nicht
    die Wirkung.
    """

    def test_charactergraph_schickt_die_assistenten_schablone(self):
        _, ergebnis = _lauf("character", [0.5])
        system: str = ergebnis["_system_prompts"][0]
        self.assertIn(ANTWORT_LAGE, system)
        self.assertNotIn(NUTZER_LAGE, system)

    def test_agentgraph_schickt_die_impuls_schablone(self):
        _, ergebnis = _lauf("agent", [0.5])
        system: str = ergebnis["_system_prompts"][0]
        self.assertIn(IMPULS_LAGE, system)
        self.assertNotIn(NUTZER_LAGE, system)

    def test_humangraph_schickt_die_nutzer_schablone(self):
        """Positiver Zwilling zu den beiden darueber."""
        _, ergebnis = _lauf("human", [0.5])
        system: str = ergebnis["_system_prompts"][0]
        self.assertIn(NUTZER_LAGE, system)
        self.assertNotIn(ANTWORT_LAGE, system)

    def test_jedes_segment_bekommt_dieselbe_schablone(self):
        """Die Rolle gilt fuer den Turn, nicht fuer das einzelne Segment."""
        _, ergebnis = _lauf("character", [0.5, 0.7, 0.3])
        prompts: list = ergebnis["_system_prompts"]
        self.assertEqual(len(prompts), 3)
        self.assertEqual(len(set(prompts)), 1)
        self.assertIn(ANTWORT_LAGE, prompts[0])

    def test_gemeldeter_block_und_gesendeter_prompt_passen_zusammen(self):
        """Der eigentliche Riss: Log und Prompt duerfen nicht auseinanderlaufen."""
        for rolle, kennsatz in (
            ("human",     NUTZER_LAGE),
            ("character", ANTWORT_LAGE),
            ("agent",     IMPULS_LAGE),
        ):
            eintraege, ergebnis = _lauf(rolle, [0.5])
            gemeldet: str = [e for e in eintraege if e.art == "switch"][0].inhalt["aufgaben_block"]
            system:   str = ergebnis["_system_prompts"][0]

            self.assertEqual(gemeldet, _aufgaben_block_name(rolle), rolle)
            self.assertIn(kennsatz, system, rolle)


if __name__ == "__main__":
    unittest.main()
