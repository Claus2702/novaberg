"""Tests fuer die Graph-Rolle — wer laeuft, und was folgt daraus.

Ziel: Der AgentGraph bewertet den Reiz statt einer Reaktion, die er nie
erzeugt, ist im pipeline_log vom CharacterGraph unterscheidbar und schreibt
keinen Session-Turn.

Hintergrund (gemessen 26.07.2026): Der Switch im Salienz-Node hing an
`ei_calc_rolle`. Der AgentGraph setzt die auf "character", damit der KZG-Eintrag
`beobachter='assistant'` bekommt — und landete dadurch im Reaktions-Zweig. In
jedem AgentGraph-Lauf stand `bewertungs_laenge=0`; das Wissensstueck lag
ungelesen im Lagebild. Ein Fachtext ueber Quark-Gluon-Plasma wurde dabei als
"Soziale Interaktion, Begruessung" abgelegt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from graph.state import pipeline_quelle
from graph.nodes.salience import analyze

SALIENZ_LOGGER: str = "ki_server.salience"

REIZ:     str = "Hainbuchen durchwurzeln verdichteten Boden ueber Jahre wieder locker."
REAKTION: str = "Das ist ein langsamer Prozess, aber er traegt sich selbst."


def _state(graph_rolle: str, user_prompt: str = REIZ, response: str = REAKTION) -> dict:
    return {
        "graph_rolle":    graph_rolle,
        "ei_calc_rolle":  "character" if graph_rolle in ("character", "agent") else "user",
        "user_prompt":    user_prompt,
        "response":       response,
        "pending_writes": [],
        "token_total":    0,
        "turn_id":        "t-rolle",
        "character_id":   "nova",
    }


class PipelineQuelleTest(unittest.TestCase):
    """Bestandswerte bleiben, der AgentGraph wird unterscheidbar."""

    def test_bestandswerte_unveraendert(self):
        self.assertEqual(pipeline_quelle(_state("human")),     "user")
        self.assertEqual(pipeline_quelle(_state("character")), "character")

    def test_agentgraph_ist_eigene_quelle(self):
        self.assertEqual(pipeline_quelle(_state("agent")), "agent")

    def test_fehlende_rolle_gilt_als_humangraph(self):
        self.assertEqual(pipeline_quelle({}), "user")


class SalienzBewertungsobjektTest(unittest.TestCase):
    """Wer bewertet was — die Frage, an der es hing."""

    def _bewertet(self, graph_rolle: str, **kw) -> str:
        """Faengt den Analyse-Prompt ab und gibt das Bewertungsobjekt zurueck."""
        antwort = MagicMock()
        antwort.parsed = {"salienz": 0.9, "themen": ["T"], "dimension": "kontext"}
        antwort.token_total = 0
        antwort.text = "{}"

        with patch("graph.nodes.salience._prompt_segmentieren", side_effect=lambda t: [t]):
            with patch.object(
                __import__("services.model_services", fromlist=["model_service"]).model_service.chat,
                "submit_sync", return_value=antwort,
            ) as ruf:
                analyze(_state(graph_rolle, **kw), MagicMock(), "meister")

        nachricht: str = ruf.call_args.args[0].messages[0]["content"]
        return nachricht.split("[BEWERTUNGSOBJEKT]", 1)[1]

    def test_charactergraph_bewertet_die_reaktion(self):
        objekt: str = self._bewertet("character")
        self.assertIn(REAKTION, objekt)
        self.assertNotIn(REIZ, objekt)

    def test_humangraph_bewertet_den_reiz(self):
        objekt: str = self._bewertet("human")
        self.assertIn(REIZ, objekt)
        self.assertNotIn(REAKTION, objekt)

    def test_agentgraph_bewertet_den_reiz_nicht_die_leere_antwort(self):
        """Der Kern des Fixes: kein Responder, also nichts zu reagieren."""
        objekt: str = self._bewertet("agent", response="")
        self.assertIn(REIZ, objekt)
        self.assertIn("Eigener Gedanke der Assistentin", objekt)

    def test_agentgraph_traegt_kein_lagebild(self):
        antwort = MagicMock()
        antwort.parsed = {"salienz": 0.9, "themen": ["T"], "dimension": "kontext"}
        antwort.token_total = 0
        antwort.text = "{}"
        with patch("graph.nodes.salience._prompt_segmentieren", side_effect=lambda t: [t]):
            with patch.object(
                __import__("services.model_services", fromlist=["model_service"]).model_service.chat,
                "submit_sync", return_value=antwort,
            ) as ruf:
                analyze(_state("agent", response=""), MagicMock(), "meister")
        nachricht: str = ruf.call_args.args[0].messages[0]["content"]
        self.assertNotIn("[LAGEBILD]", nachricht)


class LeeresBewertungsobjektTest(unittest.TestCase):
    """Fail loud statt Unsinn klassifizieren."""

    def test_leerer_reiz_erzeugt_error_und_keinen_write(self):
        with self.assertLogs(SALIENZ_LOGGER, level="ERROR") as log:
            ergebnis = analyze(_state("agent", user_prompt="", response=""), MagicMock(), "meister")

        self.assertEqual(ergebnis["pending_writes"], [])
        fehler = [r for r in log.records if r.levelname == "ERROR"]
        self.assertEqual(len(fehler), 1)
        self.assertIn("Bewertungsobjekt leer", fehler[0].getMessage())

    def test_kein_llm_call_bei_leerem_objekt(self):
        with patch.object(
            __import__("services.model_services", fromlist=["model_service"]).model_service.chat,
            "submit_sync",
        ) as ruf:
            with self.assertLogs(SALIENZ_LOGGER, level="ERROR"):
                analyze(_state("character", user_prompt=REIZ, response=""), MagicMock(), "meister")
        self.assertEqual(ruf.call_count, 0)


if __name__ == "__main__":
    unittest.main()
