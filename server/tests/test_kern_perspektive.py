"""Tests: Der Kern liest die eigene Seite, und der Träger steht im Material.

Ziel: Das Profil des Menschen entsteht aus seinen Äußerungen, das der Figur
aus ihren Antworten. Nie aus beiden.

Der Anlass ist gemessen: Bis zum 16.08.2026 bekamen beide Perspektiven
denselben Text mit beiden Sprechern, unterschieden allein durch die Anweisung
— und die macht 1,4 % des Prompts aus. Am produktiven Paar stammten **90,5 %
des Materials von der Figur** (Faktor 9,5), und der Träger *„der Nutzer"* kam
im Material **null mal** vor; der Mensch stand dort nur als „Gegenueber".

Die Ursache war eine Signaturverkürzung: Der Umbau vom 10.08.2026 ersetzte
`_lzg_kern_laden(user, character, beobachter)` durch `_turns_laden(user_id)`.
Drei Argumente wurden zu einem, und der Perspektivfilter verschwand mit dem
dritten — im Diff sichtbar, aber als Vereinfachung gelesen.

Zeugen dieser Datei:
  * **Geprüft wird der Prompt, der das Modell erreicht.** Nicht der
    Rückgabewert des Modells — der wäre eine Aussage über das Modell. Die
    Attrappe fängt den Prompt ab; er ist das, was dieser Umbau ändert.
  * **Die Gegenprobe steckt in der Zusicherung selbst:** Der Beitrag der
    jeweils anderen Seite darf im Prompt **nicht** vorkommen. Gegen die alte
    Fassung fällt genau das durch.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.charakter.destillation import kern_hash_destillieren
from config import ASSISTANT_NAME, ASSISTANT_USER_ID

DESTILLATION_LOGGER: str = "ki_server.agents.charakter.destillation"

BEGEGNUNGEN: list[dict] = [
    {"aeusserung": "was macht der garten",
     "antwort":    "Die Kürbisse breiten sich aus wie eine botanische Dominanz."},
    {"aeusserung": "haha schön",
     "antwort":    "Ich freue mich, dass dich das erreicht."},
]


class _Faenger:
    """Faengt den Prompt ab, statt das Modell zu rufen."""

    def __init__(self) -> None:
        self.prompt: str = ""

    def __call__(self, prompt: str, etikett: str = "") -> str:
        self.prompt = prompt
        return "Profiltext"


class TestMaterialTrennung(unittest.TestCase):

    def _prompt_fuer(self, user_id: str) -> str:
        faenger = _Faenger()
        with patch("agents.charakter.destillation._llm_call", faenger):
            kern_hash_destillieren(BEGEGNUNGEN, user_id=user_id)
        return faenger.prompt

    def test_menschenprofil_traegt_nur_seine_aeusserungen(self) -> None:
        prompt = self._prompt_fuer("meister")

        self.assertIn("was macht der garten", prompt)
        self.assertIn("haha schön", prompt)
        self.assertNotIn(
            "botanische Dominanz", prompt,
            "Die Antwort der Figur gehoert nicht in sein Profil",
        )
        self.assertNotIn("Ich freue mich", prompt)

    def test_figurenprofil_traegt_nur_ihre_antworten(self) -> None:
        prompt = self._prompt_fuer(ASSISTANT_USER_ID)

        self.assertIn("botanische Dominanz", prompt)
        self.assertIn("Ich freue mich", prompt)
        self.assertNotIn(
            "was macht der garten", prompt,
            "Die Aeusserung des Menschen gehoert nicht in ihr Profil",
        )

    def test_traeger_steht_im_material(self) -> None:
        """Der Name, nach dem die Anweisung fragt, muss im Text auffindbar sein.

        Vorher stand dort „Gegenueber" — ein relativer Begriff, dessen
        Bezugspunkt die Anweisung gerade verschiebt.
        """
        mensch = self._prompt_fuer("meister")
        figur  = self._prompt_fuer(ASSISTANT_USER_ID)

        self.assertIn("der Nutzer: ", mensch)
        self.assertNotIn("Gegenueber:", mensch)
        self.assertIn(f"{ASSISTANT_NAME}: ", figur)
        self.assertNotIn("Gegenueber:", figur)

    def test_beide_prompts_unterscheiden_sich_im_material(self) -> None:
        """Nicht nur in der Anweisung — das war der ganze Defekt."""
        mensch = self._prompt_fuer("meister")
        figur  = self._prompt_fuer(ASSISTANT_USER_ID)

        # Der Materialteil steht hinter der Marke "Einträge:"
        mensch_material = mensch.split("Einträge:", 1)[-1]
        figur_material  = figur.split("Einträge:", 1)[-1]

        self.assertNotEqual(
            mensch_material, figur_material,
            "Beide Perspektiven duerfen nicht dasselbe Material lesen",
        )

    def test_ohne_beitrag_des_traegers_kein_profil(self) -> None:
        """Begegnungen ohne eigenen Beitrag ergeben kein leeres Profil, sondern
        eine Meldung — sonst sieht ein Ausfall wie ein Ergebnis aus.
        """
        nur_antworten = [{"aeusserung": "", "antwort": "Ich denke nach."}]

        with patch("agents.charakter.destillation._llm_call", _Faenger()):
            with self.assertLogs(DESTILLATION_LOGGER, level="ERROR") as protokoll:
                ergebnis = kern_hash_destillieren(nur_antworten, user_id="meister")

        self.assertEqual(ergebnis, "")
        self.assertTrue(any("kein Profil" in z for z in protokoll.output))

    def test_leere_eingabe_meldet_und_gibt_leer(self) -> None:
        with self.assertLogs(DESTILLATION_LOGGER, level="ERROR"):
            self.assertEqual(kern_hash_destillieren([], user_id="meister"), "")


if __name__ == "__main__":
    unittest.main()
