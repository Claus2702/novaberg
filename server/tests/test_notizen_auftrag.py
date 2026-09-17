"""Tests: Die Notizen-Klassifikation lehnt eine Aussage ueber einen Bedarf oder eine Sache ab.

Ziel: Eine Aussage ohne Bitte ist fuer die Fachabteilung kein Auftrag. Entschieden
am 17.09.2026 — wie fuer die Timeline am 13.09.2026: festgehalten wird nur, worum
der Nutzer ausdruecklich bittet.

Gebaut ist nur die Sperre der Fachabteilung. Dieselbe Regel im Aushang am Empfang
wurde gemessen und nicht uebernommen: Sie hielt die Aussagen zurueck, nahm aber
einer Zustimmung das Ziel (labor/2026-09-17_notizen_auftrag/).

Die Nomen der Beispiele stehen in keiner Messreihe — sonst waere die Messung
geschoent. Den Satzbau ("ich brauche noch ...") teilen sie mit den Messfaellen:
er ist die Klasse, die abgelehnt werden soll, und laesst sich nicht vermeiden.

**Was dieser Test NICHT kann:** ob das Modell dem Satz folgt. Das misst die Reihe.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from agents.notizen.klassifikation import _build_classify_prompt


class FachabteilungTest(unittest.TestCase):

    def test_vorpruefung_sagt_dass_eine_aussage_kein_auftrag_ist(self) -> None:
        prompt = _build_classify_prompt(None, None)
        self.assertIn("worum der User ausdruecklich bittet", prompt)

    def test_aussage_steht_unter_rejected(self) -> None:
        prompt = _build_classify_prompt(None, None)
        rejected = prompt[prompt.index("Beispiele fuer rejected:"):prompt.index("Beispiele fuer ECHTE Auftraege")]
        self.assertIn("Aussage ueber einen Bedarf, keine Bitte", rejected)
        self.assertIn("Aussage ueber eine Sache, keine Bitte", rejected)

    def test_die_beispiele_stehen_in_keiner_messreihe(self) -> None:
        prompt = _build_classify_prompt(None, None)
        for messfall in ("Mehl und Hefe", "Reifengroesse", "Zaehlerstand", "Erdnuesse", "Spuelmittel", "Hausmeister", "Muellbeutel"):
            with self.subTest(messfall=messfall):
                self.assertNotIn(messfall, prompt)


if __name__ == "__main__":
    unittest.main()
