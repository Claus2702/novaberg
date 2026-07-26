"""Tests fuer die Herkunft des Reizes im Responder-Prompt.

Ziel: Nova nimmt einen Pixie-Impuls als ihren eigenen Gedanken wahr — nicht
als Aeusserung des Nutzers.

Gemessen am 26.07.2026: Auf einen eigenen Impuls antwortete sie mit „Deine
Synthese ist absolut brillant — du schlaegst hier eine Bruecke…". Der Reiz
reist auf dem user_prompt-Platz, und ohne Marker liest der Responder ihn als
fremde Aeusserung.

Abgegrenzt wird gegen den Thinker-Retry: der traegt dieselbe event_source,
wiederholt aber eine echte Nutzer-Aeusserung und darf den Block NICHT bekommen.
"""

import unittest

from graph.nodes.responder import _build_system_prompt, _reiz_ist_eigener_gedanke

MARKER: str = "[EIGENER GEDANKE]"
KOPF_EIGEN: str = "So ist deine eigene Verfassung gerade:"
KOPF_FREMD: str = "So nimmt der Nutzer gerade am Gespraech teil:"


def _state(payload: dict | None = None, event_source: str = "user") -> dict:
    """Minimaler ConversationState, wie ihn der Responder liest."""
    return {
        "user_prompt":      "Ein Reiz.",
        "event_source":     event_source,
        "event_payload":    payload if payload is not None else {},
        "external":         None,
        "internal":         None,
        "task_block":       "",
        "emotions_verlauf": [],
        "user_intentionen": [],
        "gv_hypothese":     "",
        # Der Prompt-Bau greift auf diese beiden direkt zu, nicht ueber .get()
        "memory_context":   "",
        "web_context":      "",
    }


class ReizHerkunftTest(unittest.TestCase):
    """Der Marker entscheidet, nicht die event_source."""

    def test_eigener_impuls_wird_erkannt(self):
        self.assertTrue(_reiz_ist_eigener_gedanke(
            _state({"reiz_herkunft": "eigener_impuls"}, event_source="character")
        ))

    def test_nutzer_turn_ist_kein_eigener_gedanke(self):
        self.assertFalse(_reiz_ist_eigener_gedanke(_state()))

    def test_thinker_retry_ist_kein_eigener_gedanke(self):
        """Gleiche event_source, aber eine wiederholte NUTZER-Aeusserung."""
        self.assertFalse(_reiz_ist_eigener_gedanke(
            _state({"thinker_unsicher_retry": True, "turn_id": "t-1"},
                   event_source="character")
        ))

    def test_fehlender_payload_gilt_als_fremd(self):
        zustand = _state()
        zustand["event_payload"] = None
        self.assertFalse(_reiz_ist_eigener_gedanke(zustand))


class ResponderPromptTest(unittest.TestCase):
    """Der Block steht im Prompt — und nur dann, wenn er hingehoert."""

    def test_impuls_bekommt_den_block(self):
        prompt: str = _build_system_prompt(
            _state({"reiz_herkunft": "eigener_impuls"}, event_source="character")
        )
        self.assertIn(MARKER, prompt)

    def test_nutzer_turn_bekommt_den_block_nicht(self):
        prompt: str = _build_system_prompt(_state())
        self.assertNotIn(MARKER, prompt)

    def test_thinker_retry_bekommt_den_block_nicht(self):
        prompt: str = _build_system_prompt(
            _state({"thinker_unsicher_retry": True}, event_source="character")
        )
        self.assertNotIn(MARKER, prompt)

    def test_kommunikations_kopf_nennt_den_richtigen_traeger(self):
        """external ist beim Impuls eine Kopie von internal (db_zugriff)."""
        eigen: str = _build_system_prompt(
            _state({"reiz_herkunft": "eigener_impuls"}, event_source="character")
        )
        fremd: str = _build_system_prompt(_state())

        self.assertIn(KOPF_EIGEN, eigen)
        self.assertNotIn(KOPF_FREMD, eigen)
        self.assertIn(KOPF_FREMD, fremd)
        self.assertNotIn(KOPF_EIGEN, fremd)

    def test_der_block_verbietet_die_zuschreibung_an_den_nutzer(self):
        """Der gemessene Defekt war eine Zuschreibung — der Block adressiert sie."""
        prompt: str = _build_system_prompt(
            _state({"reiz_herkunft": "eigener_impuls"}, event_source="character")
        )
        # Bis zum Beginn des naechsten Blocks — der Block selbst enthaelt
        # Leerzeilen, ein Split auf "\n\n" wuerde ihn mittendrin abschneiden.
        block: str = prompt.split(MARKER, 1)[1].split("\n\n[", 1)[0]
        self.assertIn("schreibe sie ihm nicht zu", block)
        self.assertIn("DEINER", block)

    def test_beide_prompts_bleiben_im_blockschema(self):
        for payload, name in (({"reiz_herkunft": "eigener_impuls"}, "impuls"),
                              ({}, "nutzer")):
            with self.subTest(fall=name):
                prompt: str = _build_system_prompt(_state(payload, "character"))
                self.assertIn("[IDENTITAET]", prompt)
                self.assertIn("[KOMMUNIKATION]", prompt)
                self.assertIn("[REGELN]", prompt)


if __name__ == "__main__":
    unittest.main()
