"""Zeugen dafuer, dass das Beziehungsprofil den Wortlaut liest.

**Der Befund, aus dem sie entstanden sind.** Der Beziehungs-Prompt fragt nach
NAEHE — Anrede, Kosenamen, Ton. Gefuettert wurde er mit dem KZG-Inhalt, und
der ist bereits eine Aussage in der dritten Person: Aus »jo« wird »Der Nutzer
weiss nicht, was er hier tun soll«. Die Anrede ueberlebt diese Umwandlung
nicht, und mit ihr der Gegenstand der Frage.

Gemessen am 09.08.2026 in einem Kreuzversuch: `distanz` stand in jeder Zelle
auf 1.00 — bei beiden Materialien und beiden Etiketten. Ein Wert, der sich
unter keiner Bedingung bewegt, misst nichts.

Der teuerste Zeuge hier ist der dritte: **kein stiller Rueckfall.** Faellt
die Funktion ohne Wortlaut auf den KZG-Inhalt zurueck, ist der Defekt
wiederhergestellt — mit einem Umweg und einem gruenen Test.
"""

import unittest
from unittest.mock import patch

from agents.charakter.destillation import beziehungsprofil_destillieren

_MODUL = "agents.charakter.destillation"


def _eintrag(key: str, inhalt: str) -> dict:
    """Ein KZG-Eintrag, wie `_kzg_laden` ihn liefert."""
    return {
        "_key": key, "inhalt": inhalt, "themen": "", "salienz": "0.5",
        "erstellt_am": "0", "modus": "spielerisch", "emotion": "neugierig",
        "beziehungs_dynamik": "neutral", "tone": "direkt",
    }


class WortlautTest(unittest.TestCase):
    """Was im Prompt landet — und was nicht."""

    def test_der_prompt_traegt_die_aeusserung_woertlich(self) -> None:
        """Die gesprochenen Worte stehen drin, nicht die Aussage darueber."""
        with patch(f"{_MODUL}.wortlaut_holen") as holen, \
             patch(f"{_MODUL}._llm_call", return_value="Profil") as ruf:
            holen.return_value = {
                "kzg:leon:nova:1": {
                    "aeusserung": "jo",
                    "antwort": "Na, bist du schon am Ende deiner Kraefte?",
                },
            }
            beziehungsprofil_destillieren(
                [_eintrag("kzg:leon:nova:1", "Der Nutzer ist gelangweilt.")],
                user_id="leon",
            )

        prompt: str = ruf.call_args[0][0]
        self.assertIn("jo", prompt)
        self.assertIn("Na, bist du schon am Ende deiner Kraefte?", prompt)

    def test_die_zusammenfassung_steht_nicht_mehr_im_prompt(self) -> None:
        """Der KZG-Inhalt ist ersetzt, nicht ergaenzt.

        Stuende er daneben, laese das Modell weiterhin die dritte Person —
        und die Frage, welche der beiden Fassungen das Urteil traegt, waere
        nicht mehr entscheidbar.
        """
        with patch(f"{_MODUL}.wortlaut_holen") as holen, \
             patch(f"{_MODUL}._llm_call", return_value="Profil") as ruf:
            holen.return_value = {
                "kzg:leon:nova:1": {"aeusserung": "jo", "antwort": "Na!"},
            }
            beziehungsprofil_destillieren(
                [_eintrag("kzg:leon:nova:1",
                          "Der Nutzer weiss nicht, was er hier tun soll.")],
                user_id="leon",
            )

        prompt: str = ruf.call_args[0][0]
        self.assertNotIn("Der Nutzer weiss nicht", prompt)
        self.assertIn("Tone: direkt", prompt)   # Beiwerk bleibt

    def test_ohne_wortlaut_kein_stiller_rueckfall(self) -> None:
        """Kein Wortlaut heisst kein Profil — laut, nicht ersatzweise.

        Rot, sobald jemand einen Rueckfall auf den KZG-Inhalt einbaut: Dann
        entstuende wieder ein Profil aus der dritten Person, und niemand
        saehe es an.
        """
        with patch(f"{_MODUL}.wortlaut_holen", return_value={}), \
             patch(f"{_MODUL}._llm_call", return_value="Profil") as ruf, \
             self.assertLogs("ki_server", level="ERROR") as gefangen:
            ergebnis = beziehungsprofil_destillieren(
                [_eintrag("kzg:leon:nova:1", "Der Nutzer ist gelangweilt.")],
                user_id="leon",
            )

        self.assertEqual("", ergebnis)
        ruf.assert_not_called()
        self.assertIn("kein Wortlaut erreichbar".split()[0],
                      "\n".join(gefangen.output))

    def test_eintrag_ohne_schluessel_wird_gemeldet(self) -> None:
        """Ein Eintrag ohne `_key` ist eine Luecke und keine Nebensache."""
        with patch(f"{_MODUL}.wortlaut_holen", return_value={}), \
             patch(f"{_MODUL}._llm_call", return_value="Profil"), \
             self.assertLogs("ki_server", level="ERROR") as gefangen:
            beziehungsprofil_destillieren(
                [{"inhalt": "Ohne Schluessel.", "modus": "", "emotion": "",
                  "beziehungs_dynamik": "", "tone": ""}],
                user_id="leon",
            )

        self.assertIn("ohne '_key'", "\n".join(gefangen.output))


class KernWortlautTest(unittest.TestCase):
    """Auch die Grundpersoenlichkeit liest den Wortlaut.

    Der Kern ist die groessere Haelfte der Rad-Quelle — bei Leon 689 von
    1230 Zeichen. Solange er aus Langzeit-Knoten entstand, las das Rad
    mehrheitlich das Worueber, obwohl sein Prompt ausdruecklich das Wie
    verlangt.
    """

    def test_der_kern_prompt_traegt_die_gesprochenen_worte(self) -> None:
        """Die Aeusserung steht im Prompt, nicht ihre Zusammenfassung."""
        from agents.charakter.destillation import kern_hash_destillieren

        with patch(f"{_MODUL}._llm_call", return_value="Profil") as ruf:
            kern_hash_destillieren(
                [{"aeusserung": "jo", "antwort": "Na, alles klar bei dir?"}],
                user_id="leon",
            )

        prompt: str = ruf.call_args[0][0]
        self.assertIn("jo", prompt)
        self.assertIn("Na, alles klar bei dir?", prompt)

    def test_ohne_wortlaut_meldet_der_kern_es(self) -> None:
        """Leere Eingabe ist ein `error`, kein stilles leeres Profil."""
        from agents.charakter.destillation import kern_hash_destillieren

        with patch(f"{_MODUL}._llm_call") as ruf, \
             self.assertLogs("ki_server", level="ERROR"):
            self.assertEqual("", kern_hash_destillieren([], user_id="leon"))
        ruf.assert_not_called()


if __name__ == "__main__":
    unittest.main()
