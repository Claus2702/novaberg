"""Tests: eine leere Modellantwort ist ein Fehlschlag, kein Ergebnis.

Am 01.08.2026 gingen zwei Turns verloren, vierzehn Minuten auseinander. Das
Modell lieferte 4936 bzw. 3753 Token und **null Zeichen**; die Ausgabe-
Verifikation des Workers bestand aus einer Logzeile, die die Laenge meldete
statt sie zu pruefen, und die Erfolgsmeldung des Responders zaehlte Token
statt Zeichen. Erst die Salienz brach zwei Knoten spaeter ab
(novaberg-bugs.md -> RESPONDER-LEERE-ANTWORT-STILL).

Zeugen dieser Datei:
  * Die Forderung stammt aus dem EVA-Grundsatz: Eine Ausgabe, die nicht
    verifiziert wird, ist keine Ausgabe-Verifikation.
  * Dass `thinking` die Ursache entscheidet, steht im Bug-Eintrag: gefuellt
    heisst "gedacht und nichts gesagt", leer heisst "die Aufbereitung war es".

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from contextlib import AbstractContextManager
from unittest.mock import MagicMock, patch

from graph.nodes import responder as resp_mod

RESPONDER_LOGGER: str = "ki_server.responder"


class _Antwort:
    """Attrappe einer Modellantwort — Text und Tokenzahl frei setzbar."""

    def __init__(self, text: str, token_total: int = 4936) -> None:
        self.text: str = text
        self.token_total: int = token_total
        self.parsed = None
        self.thinking: str = ""


def _state(**felder: object) -> dict:
    """Zustand, der fuer den Responder ausreicht."""
    basis: dict = {
        "user_prompt": "Wie entsteht ein Gammablitz?",
        "user_id": "meister", "character_id": "nova", "turn_id": "t",
        "memory_context": "", "web_context": "", "session_turns": [],
        "task_block": "", "task_context_cut": False,
        "gespraechsvektor": "", "gv_detail": {},
        "antwort_inhalt": "x" * 1149,
        "emotions_verlauf": [], "nova_emotions_verlauf": [],
        "external": None, "internal": None,
        "response": "", "token_total": 0,
    }
    basis.update(felder)
    return basis


class EineLeereAntwortWirdLautTest(unittest.TestCase):
    """Der Ausfall wird dort gemeldet, wo er entsteht — nicht zwei Knoten spaeter."""

    def _antworten(self, text: str) -> AbstractContextManager[MagicMock]:
        """Ersetzt den Modellaufruf durch eine Antwort mit gesetztem Text."""
        return patch.object(
            resp_mod.model_service.chat, "submit_sync", return_value=_Antwort(text),
        )

    def test_leere_antwort_erzeugt_eine_fehlerzeile(self) -> None:
        """Vierstellige Tokenzahl bei null Zeichen — der teure Fall."""
        with self._antworten(""):
            with self.assertLogs(RESPONDER_LOGGER, level="ERROR") as protokoll:
                resp_mod.respond(_state())

        self.assertIn("LEERE Antwort", "\n".join(protokoll.output))

    def test_die_fehlerzeile_nennt_den_bereitgestellten_inhalt(self) -> None:
        """1149 Zeichen Inhalt und nichts daraus gemacht — das gehoert dazu."""
        with self._antworten("   \n  "):
            with self.assertLogs(RESPONDER_LOGGER, level="ERROR") as protokoll:
                resp_mod.respond(_state())

        self.assertIn("1149", "\n".join(protokoll.output))

    def test_der_turn_bricht_nicht_ab(self) -> None:
        """Abzubrechen hiesse, die Nutzeraeusserung zu verlieren.

        Die ist der teurere Verlust; die Stufen dahinter sehen die leere
        Antwort und koennen sie behandeln.
        """
        with self._antworten(""):
            with self.assertLogs(RESPONDER_LOGGER, level="ERROR"):
                ergebnis = resp_mod.respond(_state())

        self.assertEqual("", ergebnis["response"])
        self.assertEqual(4936, ergebnis["token_total"])

    def test_eine_gefuellte_antwort_meldet_zeichen_statt_token(self) -> None:
        """Die alte Meldung nannte Token — und die waren beim Ausfall vierstellig."""
        # Von Hand gezaehlt: "Kurz und gut." hat dreizehn Zeichen.
        with self._antworten("Kurz und gut."):
            with self.assertLogs(RESPONDER_LOGGER, level="INFO") as protokoll:
                resp_mod.respond(_state())

        meldung: str = "\n".join(
            z for z in protokoll.output if "Antwort generiert" in z
        )
        self.assertIn("13 Zeichen", meldung)

    def test_eine_gefuellte_antwort_erzeugt_keinen_leer_befund(self) -> None:
        """Der positive Zwilling zur Negativ-Zusicherung oben.

        Geprueft wird auf die Leer-Meldung, nicht auf Fehlerfreiheit: Der
        Attrappen-Zustand traegt kein `internal`, und der Responder meldet
        das zu Recht. Ein `assertNoLogs` ueber alle Fehler pruefte die
        Attrappe statt das Pruefobjekt.
        """
        with self._antworten("Kurz und gut."):
            with self.assertLogs(RESPONDER_LOGGER, level="ERROR") as protokoll:
                resp_mod.respond(_state())

        self.assertNotIn("LEERE Antwort", "\n".join(protokoll.output))


if __name__ == "__main__":
    unittest.main()
