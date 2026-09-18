"""Tests: Der Ausgang einer Schreibung folgt ihrer Verifikation.

`DIENST-MELDET-ABGESCHLOSSEN-OHNE-VERIFIKATION`: Die Empfangsdienste pruefen nach
jedem Schreiben, ob die Zeile dasteht — und meldeten danach unbedingt
`abgeschlossen`. `[gemessen 17.09.2026, Betrieb]` Die Timeline meldete
`abgeschlossen`, und in `timeline` stand keine Zeile.

Zeugen dieser Datei:
  * **Der Baustein** — bestaetigt: unveraendert; nicht bestaetigt: `fehler`, mit
    Begruendung, ohne Erfolgssatz.
  * **Ein echter Durchlauf** — das Anlegen eines Termins mit einer Verifikation,
    die scheitert, meldet `fehler`.
  * **Die Struktur** — in den vier Diensten steht keine verifizierende Rueckgabe
    mehr, die `abgeschlossen` ohne den Baustein meldet. Am Syntaxbaum gezaehlt,
    nicht am Text.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import unittest
from pathlib import Path
from unittest.mock import patch

from agents.timeline import crud as timeline_crud
from agents.write_outcome import verified_outcome

ERFOLG = {"ergebnis": "Termin 'Zahnarzt' eingetragen fuer 24.09.2026 15:00", "status": "abgeschlossen",
          "schritte": [{"node": "ausfuehren", "verifiziert": False}]}


class BausteinTest(unittest.TestCase):

    def test_bestaetigt_bleibt_unveraendert(self) -> None:
        self.assertIs(verified_outcome(ERFOLG, True), ERFOLG)

    def test_nicht_bestaetigt_ist_ein_fehler_ohne_zusage(self) -> None:
        with self.assertLogs("ki_server.agents.write_outcome", level="ERROR"):
            ausgang = verified_outcome(ERFOLG, False)
        self.assertEqual(ausgang["status"], "fehler")
        self.assertIn("nicht bestaetigt", ausgang["fehler"])
        self.assertIn("Zahnarzt", ausgang["fehler"])          # der Beleg bleibt lesbar
        self.assertNotIn("eingetragen", ausgang["ergebnis"])  # keine Zusage
        self.assertEqual(ausgang["schritte"], ERFOLG["schritte"])

    def test_andere_ausgaenge_werden_nicht_umgedeutet(self) -> None:
        rueckfrage = {"status": "rueckfrage", "rueckfrage": "Welcher?"}
        with self.assertLogs("ki_server.agents.write_outcome", level="ERROR"):
            self.assertIs(verified_outcome(rueckfrage, False), rueckfrage)


class TimelineDurchlaufTest(unittest.TestCase):

    def _anlegen(self, verifiziert: bool) -> dict:
        state = {"aufgabe": "Trag den Zahnarzt ein", "kontext": {"user_id": "pruefer"},
                 "parameter": {"action": "create", "target": "Zahnarzt",
                               "zeitausdruck": "24.09.2026 15:00", "event_type": "termin"},
                 "schritte": []}
        with patch("memory.repositories.timeline_repository.TimelineRepository.insert", return_value=4711), \
             patch.object(timeline_crud, "_verifizieren_termin", return_value=verifiziert):
            return timeline_crud._create(state)

    def test_gescheiterte_verifikation_meldet_fehler(self) -> None:
        ausgang = self._anlegen(False)
        self.assertEqual(ausgang["status"], "fehler")
        self.assertNotIn("eingetragen", ausgang["ergebnis"])

    def test_bestaetigte_schreibung_bleibt_abgeschlossen(self) -> None:
        self.assertEqual(self._anlegen(True)["status"], "abgeschlossen")


class NotizUmbenennenTest(unittest.TestCase):
    """Zweite Kontrolle 18.09.2026: der einzige Schreibpfad ohne Pruefung."""

    def _umbenennen(self, gelesen: str) -> dict:
        from agents.notizen import crud as notizen_crud
        state = {"parameter": {"notiz": {"id": 7, "name": "Alt"}, "target": "Neu"}, "schritte": []}
        with patch("tools.db_manager.db_manager.execute", return_value=1), \
             patch("tools.db_manager.db_manager.select_one", return_value={"name": gelesen}):
            return notizen_crud._rename(state)

    def test_bestaetigt(self) -> None:
        self.assertEqual(self._umbenennen("Neu")["status"], "abgeschlossen")

    def test_nicht_bestaetigt_meldet_fehler(self) -> None:
        self.assertEqual(self._umbenennen("Alt")["status"], "fehler")


class StrukturTest(unittest.TestCase):
    """Jede Rueckgabe mit `abgeschlossen` und `verifiziert` laeuft durch den Baustein."""

    DATEIEN = ("agents/timeline/crud.py", "agents/notizen/crud.py",
               "agents/direktiven/crud.py", "agents/charakter_identitaet/crud.py")

    @staticmethod
    def _ist_erfolg_mit_verifikation(knoten: ast.Dict) -> bool:
        schluessel = {k.value for k in knoten.keys if isinstance(k, ast.Constant)}
        status = next((v for k, v in zip(knoten.keys, knoten.values, strict=True)
                       if isinstance(k, ast.Constant) and k.value == "status"), None)
        return (isinstance(status, ast.Constant) and status.value == "abgeschlossen"
                and "verifiziert" in ast.dump(knoten) and "ergebnis" in schluessel)

    def test_keine_ungeschuetzte_erfolgsmeldung(self) -> None:
        wurzel = Path(__file__).resolve().parent.parent
        geschuetzt = ungeschuetzt = 0
        for datei in self.DATEIEN:
            baum = ast.parse((wurzel / datei).read_text(encoding="utf-8"))
            for knoten in ast.walk(baum):
                if isinstance(knoten, ast.Return) and knoten.value is not None:
                    wert = knoten.value
                    if isinstance(wert, ast.Dict) and self._ist_erfolg_mit_verifikation(wert):
                        ungeschuetzt += 1
                    elif (isinstance(wert, ast.Call) and getattr(wert.func, "id", "") == "verified_outcome"
                          and isinstance(wert.args[0], ast.Dict)):
                        geschuetzt += 1
        self.assertEqual(ungeschuetzt, 0)
        self.assertEqual(geschuetzt, 19)   # 18.09.2026: 3 + 5 + 4 + 6, dazu _rename der Notizen


if __name__ == "__main__":
    unittest.main()
