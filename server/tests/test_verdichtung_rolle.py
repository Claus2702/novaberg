"""Tests fuer den Rollen-Switch der KZG-Verdichtung (Sprint NOVA-SAGT-ICH).

Ziel: Ein KZG-Eintrag mit beobachter='assistant' fasst Novas eigene Aeusserung
zusammen und nennt Nova als Subjekt.

Zwei Ursachen, zwei Testgruppen:
  VerdichtungDatenpfadTest — welcher Text ins [BEWERTUNGSOBJEKT] geht.
  VerdichtungPromptTest    — welcher Aufgaben-Block dazu geladen wird.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from config import ASSISTANT_NAME
from agents.kzg.verdichtung import _build_verdichtung_prompt, verdichten
from services.model_services import model_service

VERDICHTUNG_LOGGER: str = "ki_server.agents.kzg.verdichtung"

USER_TEXT: str = "Ich habe heute drei Apfelbaeume der Sorte Boskoop gepflanzt."
NOVA_TEXT: str = "Boskoop ist eine alte Winterapfelsorte und braucht einen Befruchter."


def _state(beobachter: str | None) -> dict:
    """Baut einen AgentState wie ihn dispatch_kzg an den Subgraphen uebergibt."""
    kontext: dict = {"user_id": "meister", "character_id": "nova", "turn_id": "t-1"}
    if beobachter is not None:
        kontext["beobachter"] = beobachter
    return {
        "aufgabe":    "kzg_verarbeitung",
        "kontext":    kontext,
        "parameter":  {"user_prompt": USER_TEXT, "response": NOVA_TEXT},
        "schritte":   [],
        "ergebnis":   None,
        "status":     "laufend",
        "rueckfrage": None,
        "fehler":     None,
    }


class VerdichtungDatenpfadTest(unittest.TestCase):
    """Ursache A: Pfad 2 verdichtete den User-Prompt statt Novas Antwort."""

    def _anfrage(self, beobachter: str | None):
        """Ruft verdichten() auf und gibt den abgefangenen ChatRequest zurueck."""
        antwort = SimpleNamespace(text="  ein Kern-Satz  ")
        with patch.object(model_service.chat, "submit_sync", return_value=antwort) as ruf:
            ergebnis: dict = verdichten(_state(beobachter))
        self.assertEqual(ergebnis["parameter"]["kern"], "ein Kern-Satz")
        self.assertEqual(ruf.call_count, 1)
        return ruf.call_args.args[0]

    def test_assistant_verdichtet_novas_antwort(self):
        request = self._anfrage("assistant")
        nachricht: str = request.messages[0]["content"]

        bewertungsobjekt: str = nachricht.split("[BEWERTUNGSOBJEKT]", 1)[1]
        lagebild:         str = nachricht.split("[BEWERTUNGSOBJEKT]", 1)[0]

        self.assertIn(NOVA_TEXT, bewertungsobjekt)
        self.assertNotIn(USER_TEXT, bewertungsobjekt)
        self.assertIn(USER_TEXT, lagebild)
        self.assertIn("Antwort der Assistentin:", bewertungsobjekt)

    def test_user_verdichtet_den_user_prompt(self):
        request = self._anfrage("user")
        nachricht: str = request.messages[0]["content"]

        bewertungsobjekt: str = nachricht.split("[BEWERTUNGSOBJEKT]", 1)[1]
        lagebild:         str = nachricht.split("[BEWERTUNGSOBJEKT]", 1)[0]

        self.assertIn(USER_TEXT, bewertungsobjekt)
        self.assertNotIn(NOVA_TEXT, bewertungsobjekt)
        self.assertIn(NOVA_TEXT, lagebild)
        self.assertIn("Eingabe des Nutzers:", bewertungsobjekt)

    def test_beide_pfade_bewerten_verschiedene_texte(self):
        """Der Kern des Sprints: derselbe Turn, zwei verschiedene Bewertungsobjekte."""
        als_user      = self._anfrage("user").messages[0]["content"]
        als_assistent = self._anfrage("assistant").messages[0]["content"]
        self.assertNotEqual(
            als_user.split("[BEWERTUNGSOBJEKT]", 1)[1],
            als_assistent.split("[BEWERTUNGSOBJEKT]", 1)[1],
        )

    def test_fehlender_beobachter_warnt_und_faellt_auf_user_zurueck(self):
        antwort = SimpleNamespace(text="kern")
        with patch.object(model_service.chat, "submit_sync", return_value=antwort) as ruf:
            with self.assertLogs(VERDICHTUNG_LOGGER, level="WARNING") as log:
                verdichten(_state(None))

        warnungen = [r for r in log.records if r.levelname == "WARNING"]
        self.assertEqual(len(warnungen), 1)
        self.assertIn("beobachter fehlt", warnungen[0].getMessage())

        nachricht: str = ruf.call_args.args[0].messages[0]["content"]
        self.assertIn(USER_TEXT, nachricht.split("[BEWERTUNGSOBJEKT]", 1)[1])


class VerdichtungPromptTest(unittest.TestCase):
    """Ursache B: ein Prompt fuer beide Laeufe, sechs Beispiele auf den Nutzer."""

    def test_beide_rollen_bekommen_verschiedene_prompts(self):
        self.assertNotEqual(
            _build_verdichtung_prompt("user"),
            _build_verdichtung_prompt("assistant"),
        )

    def test_assistenten_prompt_nennt_nova_als_subjekt(self):
        prompt: str = _build_verdichtung_prompt("assistant")
        self.assertIn(ASSISTANT_NAME, prompt)
        self.assertNotIn("{traeger}", prompt)
        # Mindestens ein GUT-Beispiel setzt den Assistenten-Namen ans Satzende
        # eines Subjekts — ein Beispiel schlaegt eine Anweisung.
        self.assertIn(f"GUT: \"{ASSISTANT_NAME} hat", prompt)

    def test_nutzer_prompt_nennt_nova_nicht_als_subjekt(self):
        prompt: str = _build_verdichtung_prompt("user")
        # Auf die Struktur pruefen, nicht auf den Beispieltext: welcher Name im
        # Beispiel steht, gehoert nicht hierher, sondern in
        # test_prompt_beispielnamen.py.
        self.assertIn('GUT: "Der Nutzer heisst ', prompt)
        self.assertNotIn(f"GUT: \"{ASSISTANT_NAME} hat", prompt)

    def test_unbekannter_beobachter_bekommt_den_nutzer_block(self):
        self.assertEqual(
            _build_verdichtung_prompt("irgendwas"),
            _build_verdichtung_prompt("user"),
        )

    def test_beide_prompts_tragen_identitaet_und_regeln(self):
        for rolle in ("user", "assistant"):
            with self.subTest(rolle=rolle):
                prompt: str = _build_verdichtung_prompt(rolle)
                self.assertIn("[IDENTITAET]", prompt)
                self.assertIn("[AUFGABE]", prompt)
                self.assertIn("[REGELN]", prompt)


if __name__ == "__main__":
    unittest.main()
