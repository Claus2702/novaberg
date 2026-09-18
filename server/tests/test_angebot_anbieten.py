"""Tests: Nova bietet von sich aus an — Scheibe 12 E2.

Entscheidung des Eigentuemers (18.09.2026, loest die feste Schwelle 0,9 vom
17.09. ab): Unter Pflichtbewusstsein 0,33 bietet Nova nie an; darueber steigt
die Wahrscheinlichkeit je Turn linear von 0 % auf 100 % bei 1,0 — 0,67 ergibt
50 %. Fuer Notizen wie fuer die Timeline. Erst ein Angebot macht ein spaeteres
*"Gerne"* zum Auftrag (E1).

Zeugen dieser Datei:
  * **Der Kandidat** — eine Sache am Zettel eines schreibenden Dienstes; kein
    Kandidat, wenn ein Auftrag laeuft oder ein Dienst schon lief.
  * **Die Kurve** — 0 am Boden, 50 % bei 0,67, 100 % bei 1,0.
  * **Die Weiche** — Boden, Zug, Ablehnung (E3), nicht lesbares Rad; jeder
    Ausgang steht als Entscheidung im Log, mit Wahrscheinlichkeit und Zug.
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


class KurveTest(unittest.TestCase):
    """Die Wahrscheinlichkeit aus dem Pflichtbewusstsein."""

    def test_die_eckpunkte_der_entscheidung(self) -> None:
        """Die drei Eckpunkte der Entscheidung vom 18.09.2026.

        Die Gerade durch 0,33 und 1,0 trifft 0,67 bei 50,7 % — die Vorgabe
        "0,67 ist 50 %" ist gerundet, deshalb ein Prozentpunkt Spiel.
        """
        for pflicht, erwartet in ((0.0, 0.0), (0.33, 0.0), (0.67, 0.5), (1.0, 1.0)):
            with self.subTest(pflicht=pflicht):
                self.assertAlmostEqual(verfasser._offer_probability(pflicht), erwartet, delta=0.01)

    def test_ausserhalb_des_rads_begrenzt(self) -> None:
        self.assertEqual(verfasser._offer_probability(-0.2), 0.0)
        self.assertEqual(verfasser._offer_probability(1.3), 1.0)


class WeicheTest(unittest.TestCase):

    def _block(self, rad: dict | None, abgelehnt: set[str] | None = None,
               zug: float = 0.0) -> tuple[str, list[dict]]:
        eintraege: list[dict] = []
        state = {"user_id": "pruefer", "character_id": "nova", "turn_id": "t1",
                 "objekt_urteil": URTEIL, "agent_results": [], "management_action": ""}
        with patch.object(verfasser, "nutzer_gewichtung_rad_laden", return_value=(rad, "destilliert")), \
             patch.object(verfasser, "declined_objects", return_value=abgelehnt or set()), \
             patch.object(verfasser, "log_decision", lambda **kw: eintraege.append(kw)), \
             patch.object(verfasser.random, "random", return_value=zug):
            return verfasser._offer_block(state, SACHLAGE), eintraege

    def test_zug_unter_der_wahrscheinlichkeit_bietet_sie_an(self) -> None:
        """Ein Zug unter der Wahrscheinlichkeit ergibt das Angebot.

        0,773 ist der Wert des Paares meister × nova am 18.09.2026 — unter
        der alten Schwelle 0,9 bot sie hier nie an.
        """
        block, eintraege = self._block({"pflicht": 0.773}, zug=0.60)
        self.assertIn("Abholung der Schwester", block)
        self.assertIn("eintragen", block)
        self.assertEqual(eintraege[0]["outcome"], "angeboten")
        self.assertEqual(eintraege[0]["inputs"]["wahrscheinlichkeit"], 0.661)
        self.assertEqual(eintraege[0]["inputs"]["zug"], 0.6)

    def test_zug_ueber_der_wahrscheinlichkeit_nicht_und_das_steht_im_log(self) -> None:
        block, eintraege = self._block({"pflicht": 0.773}, zug=0.70)
        self.assertEqual(block, "")
        self.assertEqual(eintraege[0]["outcome"], "nicht_gezogen")
        self.assertEqual(eintraege[0]["inputs"]["zug"], 0.7)

    def test_unter_dem_boden_nie_auch_bei_zug_null(self) -> None:
        block, eintraege = self._block({"pflicht": 0.32}, zug=0.0)
        self.assertEqual(block, "")
        self.assertEqual(eintraege[0]["outcome"], "unter_boden")
        self.assertEqual(eintraege[0]["inputs"]["pflicht"], 0.32)

    def test_bei_voller_pflicht_immer(self) -> None:
        block, eintraege = self._block({"pflicht": 1.0}, zug=0.999)
        self.assertEqual(eintraege[0]["outcome"], "angeboten")

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
