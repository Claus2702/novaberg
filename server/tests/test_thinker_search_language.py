"""Zeugen: die eine Websuche des Thinkers ist deutsch formuliert.

Anlass (Fundliste 29.08.2026): Der Thinker suchte *»nearest known magnetar
distance«* gegen die deutsche Wikipedia-Volltextsuche — die einzige
antwortende Engine — und lud eine Liste von Doppelsternen nach. Seit der
Suchdisziplin ist das die einzige Suche des Turns. In der Kettenmessung
waren 7 von 23 Suchbegriffen englisch.

Zeugen dieser Datei:
  * **Die Regeln des Thinkers fuehren zur deutschen Suche** — die Zeile
    steht im geladenen Prompt, nicht nur in der Datei.
  * **Der Pflichtblock bei `needs_web` verlangt Deutsch** — im Eingang, den
    `think()` dem Modell wirklich gibt (Verdrahtung).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from config import PROMPTS
from graph.nodes import thinker as thinker_mod
from graph.nodes.thinker import _build_thinker_prompt, think


class RulesLeadToGermanSearchTest(unittest.TestCase):
    """Die Regelzeile ist im geladenen Prompt und im gebauten System-Prompt."""

    def test_loaded_rules_carry_the_line(self) -> None:
        self.assertIn("Der Suchbegriff ist deutsch", PROMPTS["thinker.rules"])

    def test_system_prompt_carries_the_line(self) -> None:
        self.assertIn("Der Suchbegriff ist deutsch", _build_thinker_prompt("heute"))


class WebSearchBlockDemandsGermanTest(unittest.TestCase):
    """Der [WEBSUCHE]-Block, den think() bei needs_web baut, verlangt Deutsch."""

    def test_block_reaches_the_model(self) -> None:
        state: dict = {
            "response":         "Der naechste bekannte Magnetar ist rund 9.000 Lichtjahre weg.",
            "user_prompt":      "Wie weit ist der naechste bekannte Magnetar von uns entfernt?",
            "needs_web":        True,
            "event_payload":    {},
            "node_annotations": [],
            "token_total":      0,
            "character_id":     "nova",
            "agent_results":    [],
            "memory_context":   "",
            "sachlage":         None,
        }
        antwort = MagicMock(text="ERGEBNIS: OK", thinking="", token_total=0)
        normalizer = MagicMock()
        normalizer.pruefen.return_value = MagicMock(braucht_nachfass=False)
        with patch.object(thinker_mod.model_service.chat, "submit_sync",
                          return_value=antwort) as chat, \
                patch.object(thinker_mod, "get_thinking_normalizer", return_value=normalizer):
            think(state, redis_client=MagicMock(),
                  postgres_url="postgresql://unbenutzt", user_id="u")
        eingang: str = chat.call_args.args[0].messages[0]["content"]
        self.assertIn("[WEBSUCHE]", eingang)
        self.assertIn("aus der FRAGE DES NUTZERS, auf Deutsch", eingang)


if __name__ == "__main__":
    unittest.main()
