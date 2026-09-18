"""Tests: Nova bietet von sich aus an — Scheibe 12 E2.

Entscheidung des Eigentuemers (17.09.2026): Nova bietet nur bei sehr hohem
Pflichtbewusstsein an, *"bei 0,9 und darueber"*, fuer Notizen wie fuer die
Timeline — sonst wird es aufdringlich. Erst ein Angebot macht ein spaeteres
*"Gerne"* zum Auftrag (E1).

Zeugen dieser Datei:
  * **Der Kandidat** — eine Sache am Zettel eines schreibenden Dienstes; kein
    Kandidat, wenn ein Auftrag laeuft oder ein Dienst schon lief.
  * **Die Weiche** — Schwelle, Ablehnung (E3), nicht lesbares Rad; jeder Ausgang
    steht als Entscheidung im Log.
  * **Der Kreis** — der Beispielsatz des Prompts ist einer, den `find_offers`
    als Angebot erkennt; sonst boete Nova an, und niemand merkte es.

**Was diese Tests NICHT koennen:** ob das Modell den Satz wirklich schreibt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from config import PROMPTS
from graph.nodes import verfasser
from utils.offers import find_offers, offer_candidate

SACHLAGE = {"objekte": [{"name": "Abholung der Schwester", "klasse": "vorgang", "akut": True,
                         "gedeckt": {"Tag": "Samstag"}}]}
URTEIL = {"ergebnis": "gerechnet", "objekte": [{"name": "Abholung der Schwester", "empfaenger": ["timeline"]}]}


class KandidatTest(unittest.TestCase):

    def test_eine_sache_am_zettel_der_timeline(self) -> None:
        k = offer_candidate(SACHLAGE, URTEIL, [], "")
        self.assertEqual((k.name, k.service, k.verb, k.reason),
                         ("Abholung der Schwester", "timeline", "eintragen", "anbieten"))

    def test_kein_angebot_wenn_gebeten_oder_gehandelt_wurde(self) -> None:
        self.assertEqual(offer_candidate(SACHLAGE, URTEIL, [], "agent").reason, "auftrag_laeuft")
        self.assertEqual(offer_candidate(SACHLAGE, URTEIL, [{"status": "abgeschlossen"}], "").reason, "dienst_lief")

    def test_ohne_naehe_oder_ohne_schreibenden_dienst_kein_kandidat(self) -> None:
        self.assertEqual(offer_candidate(SACHLAGE, {"ergebnis": "ausfall"}, [], "").reason, "keine_naehe")
        fremd = {"ergebnis": "gerechnet", "objekte": [{"name": "Abholung der Schwester", "empfaenger": ["wissen"]}]}
        self.assertEqual(offer_candidate(SACHLAGE, fremd, [], "").reason, "keine_sache_am_zettel")


class WeicheTest(unittest.TestCase):

    def _block(self, rad: dict | None, abgelehnt: set[str] | None = None) -> tuple[str, list[dict]]:
        eintraege: list[dict] = []
        state = {"user_id": "pruefer", "character_id": "nova", "turn_id": "t1",
                 "objekt_urteil": URTEIL, "agent_results": [], "management_action": ""}
        with patch.object(verfasser, "nutzer_gewichtung_rad_laden", return_value=(rad, "destilliert")), \
             patch.object(verfasser, "declined_objects", return_value=abgelehnt or set()), \
             patch.object(verfasser, "log_decision", lambda **kw: eintraege.append(kw)):
            return verfasser._offer_block(state, SACHLAGE), eintraege

    def test_ueber_der_schwelle_bietet_sie_an(self) -> None:
        block, eintraege = self._block({"pflicht": 0.95})
        self.assertIn("Abholung der Schwester", block)
        self.assertIn("eintragen", block)
        self.assertEqual(eintraege[0]["outcome"], "angeboten")

    def test_unter_der_schwelle_nicht_und_das_steht_im_log(self) -> None:
        """0,773 ist der Wert des Paares meister × nova am 18.09.2026."""
        block, eintraege = self._block({"pflicht": 0.773})
        self.assertEqual(block, "")
        self.assertEqual(eintraege[0]["outcome"], "unter_schwelle")
        self.assertEqual(eintraege[0]["inputs"]["pflicht"], 0.773)

    def test_eine_abgelehnte_sache_wird_nicht_wieder_angeboten(self) -> None:
        block, eintraege = self._block({"pflicht": 1.0}, {"Abholung der Schwester"})
        self.assertEqual(block, "")
        self.assertEqual(eintraege[0]["outcome"], "abgelehnt")

    def test_ohne_lesbares_rad_kein_angebot_und_laut(self) -> None:
        with self.assertLogs("ki_server.verfasser", level="ERROR"):
            block, eintraege = self._block(None)
        self.assertEqual(block, "")
        self.assertEqual(eintraege[0]["outcome"], "pflicht_unbekannt")


class VerdrahtungTest(unittest.TestCase):
    """Der Block steht im Prompt, den der Verfasser wirklich baut — nicht auf einem Impuls."""

    def _prompt(self, reiz_herkunft: str) -> str:
        state = {"user_id": "pruefer", "character_id": "nova", "turn_id": "t1", "user_prompt": "Samstag hole ich sie ab",
                 "event_payload": {"herkunft": reiz_herkunft} if reiz_herkunft else {},
                 "sachlage": SACHLAGE, "objekt_urteil": URTEIL, "agent_results": [], "node_annotations": []}
        with patch.object(verfasser, "_offer_block", return_value="[ANGEBOT]\nPRUEFMARKE"), \
             patch.object(verfasser, "reiz_ist_eigener_gedanke", return_value=reiz_herkunft == "impuls"):
            return verfasser._build_system_prompt(state)

    def test_der_block_steht_im_prompt(self) -> None:
        with self.assertLogs("ki_server.verfasser", level="ERROR"):   # ohne Haltung: laut, aber weiter
            self.assertIn("PRUEFMARKE", self._prompt(""))

    def test_auf_einem_impuls_bietet_sie_nichts_an(self) -> None:
        with self.assertLogs("ki_server.verfasser", level="ERROR"):
            self.assertNotIn("PRUEFMARKE", self._prompt("impuls"))


class KreisTest(unittest.TestCase):

    def test_der_beispielsatz_ist_ein_erkanntes_angebot(self) -> None:
        for verb in ("eintragen", "notieren"):
            with self.subTest(verb=verb):
                block = PROMPTS["verfasser.angebot"].format(sache="X", verb=verb)
                beispiel = block.split('zum Beispiel: "', 1)[1].split('"', 1)[0]
                self.assertEqual(find_offers(beispiel), [beispiel])


if __name__ == "__main__":
    unittest.main()
