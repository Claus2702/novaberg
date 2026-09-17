"""Tests: Der Router liest die Lage (Scheibe 12 D2a).

Ziel: Steht ein akutes Objekt in der Lage, sieht der Empfang es mit dem, was ueber
es bekannt ist, und mit den Diensten, an deren Zettel die gerechnete Naehe es
stellt — damit ein "Gerne" auf ein Angebot als Auftrag an diesen Dienst lesbar ist.

Zeugen dieser Datei:
  * **Kein Objekt, kein Block** — keine akuten Objekte, keine Sachlage, eine
    Sachlage vom Vorturn nach einem Ausfall.
  * **Schweigen ist kein Nein:** Ein Objekt ohne Empfaenger steht ohne Dienst da,
    nicht mit einer Verneinung.
  * **Die Verdrahtung:** Der Block steht im System-Prompt, den der Router baut,
    zwischen Verlauf und Aushaengen.

Was dieser Test NICHT kann: ob das Modell die Zustimmung als Auftrag liest. Das
misst die Reihe in labor/.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from graph.nodes import router
from graph.nodes.router import build_situation_block
from utils.offers import Offer


def _sachlage(*objekte: dict) -> dict:
    return {"herkunft": "fortgeschrieben", "objekte": list(objekte)}


ZAHNARZT = {"name": "Zahnarzttermin", "klasse": "vorgang", "akut": True,
            "gedeckt": {"Tag": "Donnerstag", "Uhrzeit": "15 Uhr"}, "offen": []}
URTEIL = {"ergebnis": "gerechnet", "herkunft": "fortgeschrieben",
          "objekte": [{"name": "Zahnarzttermin", "empfaenger": ["timeline"], "naehe": {"timeline": 0.52}}]}


class BlockTest(unittest.TestCase):

    def test_objekt_mit_bekanntem_und_dienst(self) -> None:
        block = build_situation_block(_sachlage(ZAHNARZT), URTEIL)
        self.assertTrue(block.startswith("[LAGE]"))
        self.assertIn("- Zahnarzttermin (vorgang) — bekannt: Tag: Donnerstag; Uhrzeit: 15 Uhr — am Aushang: timeline", block)

    def test_der_zustimmungssatz_haengt_am_angebot(self) -> None:
        """Seit E1 (17.09.2026): ohne offenes Angebot kein Satz ueber Zustimmung."""
        ohne = build_situation_block(_sachlage(ZAHNARZT), URTEIL)
        self.assertNotIn("Zustimmung", ohne)
        mit = build_situation_block(_sachlage(ZAHNARZT), URTEIL, offer=Offer(
            sentence="Soll ich dir den Termin eintragen?", objects=("Zahnarzttermin",),
            services=("timeline",), turn_id="t1", time=0.0))
        self.assertIn("Zustimmung", mit)
        self.assertIn("Soll ich dir den Termin eintragen?", mit)

    def test_ohne_empfaenger_keine_verneinung(self) -> None:
        block = build_situation_block(_sachlage(ZAHNARZT), {"ergebnis": "gerechnet", "objekte": []})
        zeile = next(z for z in block.splitlines() if z.startswith("- Zahnarzttermin"))
        self.assertNotIn("am Aushang", zeile)
        self.assertNotIn("kein", zeile.lower())

    def test_kein_akutes_objekt_kein_block(self) -> None:
        latent = {**ZAHNARZT, "akut": False}
        for sachlage in (None, {}, {"herkunft": "frisch"}, _sachlage(), _sachlage(latent)):
            with self.subTest(sachlage=sachlage):
                self.assertEqual(build_situation_block(sachlage, URTEIL), "")

    def test_nach_einem_ausfall_kein_block(self) -> None:
        self.assertEqual(build_situation_block(_sachlage(ZAHNARZT), {**URTEIL, "herkunft": "ausfall_uebernommen"}), "")

    def test_ausfall_der_sachlage_auch_ohne_herkunft_im_urteil(self) -> None:
        sachlage = {**_sachlage(ZAHNARZT), "herkunft": "ausfall_uebernommen"}
        for urteil in ({"ergebnis": "ausfall"}, None, URTEIL):
            with self.subTest(urteil=urteil):
                self.assertEqual(build_situation_block(sachlage, urteil), "")

    def test_hoechstens_fuenf_objekte(self) -> None:
        objekte = [{**ZAHNARZT, "name": f"Objekt {i}"} for i in range(8)]
        block = build_situation_block(_sachlage(*objekte), None)
        self.assertEqual(sum(1 for z in block.splitlines() if z.startswith("- Objekt")), 5)


class VerdrahtungTest(unittest.TestCase):

    def test_der_block_steht_zwischen_verlauf_und_aushaengen(self) -> None:
        state = {"sachlage": _sachlage(ZAHNARZT), "objekt_urteil": URTEIL}
        with patch.object(router, "aushaenge_sammeln", return_value="BRETT"):
            prompt = router._build_router_prompt(state, session_turns="[1] Nutzer: hallo")
        self.assertLess(prompt.index("[KONTEXT]"), prompt.index("[LAGE]"))
        self.assertLess(prompt.index("[LAGE]"), prompt.index("[AGENTEN]"))

    def test_auf_einem_impuls_kein_block(self) -> None:
        state = {"sachlage": _sachlage(ZAHNARZT), "objekt_urteil": URTEIL,
                 "event_payload": {"reiz_herkunft": "eigener_impuls"}}
        with patch.object(router, "aushaenge_sammeln", return_value="BRETT"):
            prompt = router._build_router_prompt(state, session_turns=None)
        self.assertNotIn("[LAGE]", prompt)

    def test_ohne_lage_kein_block_im_prompt(self) -> None:
        with patch.object(router, "aushaenge_sammeln", return_value="BRETT"):
            prompt = router._build_router_prompt({"sachlage": _sachlage()}, session_turns=None)
        self.assertNotIn("[LAGE]", prompt)


if __name__ == "__main__":
    unittest.main()
