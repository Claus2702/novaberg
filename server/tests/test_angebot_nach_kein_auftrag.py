"""Tests: Eine Ablehnung als Nicht-Auftrag sperrt weder das Gespraech noch das Angebot.

Anlass `[gelesen 19.09.2026]`: Seit die Notizen-Vorpruefung Bedarfsaussagen
ablehnt (*"Ich brauche noch Mehl"*), stellt der Empfang sie zu, die
Klassifikation lehnt als Nicht-Auftrag ab — und dann baute der Planner einen
Aufgabenblock mit Kontext-Schnitt (der Verfasser lief nicht, Nova antwortete mit
*"Sage, welche Liste gemeint ist"*), und `offer_candidate` meldete
`auftrag_laeuft` oder `dienst_lief`. Entschieden ist: Eine Aussage wird nicht
festgehalten, Nova darf sie nach ihrem Pflichtbewusstsein anbieten.

Zeugen dieser Datei:
  * **Das Kennzeichen** — die Klassifikations-Ablehnungen der Dienste tragen
    `Korrektur.kein_auftrag`, die Ablehnung in der Sache nicht.
  * **Der Planner** — keine Block, kein Schnitt, wenn nur Nicht-Auftraege
    abgelehnt wurden; eine Ablehnung in der Sache bleibt ein Block.
  * **Das Angebot** — nach einer Nicht-Auftrags-Ablehnung ist die Sache
    Kandidat, nach einer Ablehnung in der Sache nicht.

**Was diese Tests NICHT koennen:** ob das Modell dann anbietet.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import pathlib
import unittest
from unittest.mock import patch

from agents.base import AgentResult, Korrektur
from agents.notizen import dispatch as notizen_dispatch
from agents.timeline import dispatch as timeline_dispatch
from graph.nodes import planner
from utils.offers import offer_candidate

SACHLAGE = {"objekte": [{"name": "Mehl und Hefe", "klasse": "objekt", "akut": True, "gedeckt": {}}]}
URTEIL = {"ergebnis": "gerechnet",
          "objekte": [{"name": "Mehl und Hefe", "empfaenger": ["notizen"],
                       "naehe": {"notizen": 0.5}}]}


def _ablehnung(kein_auftrag: bool) -> AgentResult:
    korrektur = Korrektur(befund="b", beleg="k", vorschlag="v", kein_auftrag=kein_auftrag)
    return AgentResult(agent_name="notizen", ergebnis=None, status="abgelehnt", korrektur=korrektur)


class _Agent:
    def invoke(self, state: dict) -> dict:
        schritt = {"ergebnis": "rejected/Aussage ueber einen Bedarf"}
        return {**state, "status": "rejected", "schritte": [schritt]}


class KennzeichenTest(unittest.TestCase):
    """Die Ablehnungen der Klassifikation tragen das Kennzeichen."""

    def _durch(self, modul: object, name: str) -> AgentResult:
        state = {"user_id": "pruefer", "character_id": "nova",
                 "user_prompt": "Ich brauche noch Mehl.", "event_payload": {},
                 "management_action": "agent", "management_target": name, "agent_results": []}
        with patch.object(modul, "AgentRegistry") as reg:
            reg.finden.return_value = _Agent()
            return getattr(modul, f"dispatch_{name}")(state)["agent_results"][-1]

    def test_notizen_und_timeline_markieren_die_ablehnung_der_klassifikation(self) -> None:
        for modul, name in ((notizen_dispatch, "notizen"), (timeline_dispatch, "timeline")):
            with self.subTest(dienst=name):
                r = self._durch(modul, name)
                self.assertEqual(r.status, "abgelehnt")
                self.assertTrue(r.korrektur.kein_auftrag)

    def test_jede_ablehnung_der_klassifikation_traegt_das_kennzeichen(self) -> None:
        """Am Quelltext: jede Korrektur mit Beleg "Klassifikation: ..." setzt kein_auftrag=True.

        Das Merkmal ist der Beleg, nicht der Befund: Der Befund der Dateien
        sagt "nicht als Frage", und ein Kriterium am Wortlaut "nicht als
        Auftrag" fand ihn nicht (zweite Kontrolle, 19.09.2026).
        """
        wurzel = pathlib.Path(__file__).resolve().parents[1] / "agents"
        stellen = 0
        for datei in wurzel.rglob("*.py"):
            zeilen = datei.read_text(encoding="utf-8").splitlines()
            for i, zeile in enumerate(zeilen):
                if "beleg=" in zeile and "Klassifikation: {" in zeile:
                    stellen += 1
                    with self.subTest(datei=str(datei.relative_to(wurzel)), zeile=i + 1):
                        self.assertIn("kein_auftrag=True", "\n".join(zeilen[max(0, i - 2):i + 3]))
        self.assertGreaterEqual(stellen, 6)

    def test_ohne_angabe_ist_eine_ablehnung_eine_in_der_sache(self) -> None:
        self.assertFalse(Korrektur(befund="b", beleg="k", vorschlag="v").kein_auftrag)


class GedaechtnisTest(unittest.TestCase):
    """Das Kurzzeitgedaechtnis fuehrt einen Nicht-Auftrag nicht als abgelehnt."""

    def test_ein_nicht_auftrag_wird_keine_abgelehnte_tatsache_im_kern(self) -> None:
        from agents.kzg.dispatch import abgelehnte_ausgaenge
        self.assertEqual(abgelehnte_ausgaenge({"agent_results": [_ablehnung(True)]}), [])
        self.assertEqual(len(abgelehnte_ausgaenge({"agent_results": [_ablehnung(False)]})), 1)


class PlannerTest(unittest.TestCase):
    """Der Planner baut fuer einen Nicht-Auftrag keinen Block."""

    def test_nur_nicht_auftraege_kein_block_kein_schnitt(self) -> None:
        ergebnisse = [_ablehnung(True), _ablehnung(True)]
        self.assertEqual(planner._build_task_block(ergebnisse, "", ""), ("", False))

    def test_eine_ablehnung_in_der_sache_bleibt_ein_block_mit_schnitt(self) -> None:
        block, cut = planner._build_task_block([_ablehnung(False)], "", "")
        self.assertTrue(block)
        self.assertTrue(cut)


class AngebotTest(unittest.TestCase):
    """Das Angebot nach einer Ablehnung."""

    def test_nach_einer_nicht_auftrags_ablehnung_ist_die_sache_kandidat(self) -> None:
        k = offer_candidate(SACHLAGE, URTEIL, [_ablehnung(True)], "agent")
        self.assertEqual((k.name, k.reason), ("Mehl und Hefe", "anbieten"))

    def test_nach_einer_ablehnung_in_der_sache_nicht(self) -> None:
        in_der_sache = [_ablehnung(False)]
        mit_auftrag = offer_candidate(SACHLAGE, URTEIL, in_der_sache, "agent")
        self.assertEqual(mit_auftrag.reason, "auftrag_laeuft")
        self.assertEqual(offer_candidate(SACHLAGE, URTEIL, in_der_sache, "").reason, "dienst_lief")

    def test_ein_laufender_auftrag_ohne_ergebnis_sperrt_weiter(self) -> None:
        self.assertEqual(offer_candidate(SACHLAGE, URTEIL, [], "agent").reason, "auftrag_laeuft")

    def test_als_dict_wie_im_zustand_nach_redis(self) -> None:
        korrektur = {"befund": "b", "beleg": "k", "vorschlag": "v", "kein_auftrag": True}
        r = {"status": "abgelehnt", "korrektur": korrektur}
        self.assertEqual(offer_candidate(SACHLAGE, URTEIL, [r], "agent").reason, "anbieten")


if __name__ == "__main__":
    unittest.main()
