"""Tests: Die Timeline prueft vor dem Anlegen, ob derselbe Termin schon steht — Scheibe 12 F.

`[gemessen 17.09.2026, Betrieb]` Ohne Ziel und Zeit fiel die Suche in die
Uebersicht (±14 Tage), und **jeder** Eintrag galt als Duplikat — auch ein
Erinnerungs-Anker der KZG. Der Dienst meldete *"bereits eingetragen"* fuer
etwas anderes, `abgeschlossen`, und legte nichts an.

Ein Duplikat ist jetzt: ein aktiver Termin am selben Tag mit einem gemeinsamen
tragenden Wort im Titel, kein Anker.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from agents.timeline import suche

TZ = ZoneInfo("Europe/Berlin")
SAMSTAG_10 = datetime(2026, 9, 19, 10, 0, tzinfo=TZ)


def _eintrag(titel: str, typ: str = "termin", aktiv: bool = True) -> dict:
    return {"title": titel, "event_type": typ, "aktiv": aktiv, "event_time": SAMSTAG_10, "precision": "minute"}


def _finden(target: str, bestand: list[dict], zeit: str = "19.09.2026 10 Uhr") -> list[dict]:
    with patch("memory.repositories.timeline_repository.TimelineRepository.find_by_date_range",
               return_value=bestand) as lesen:
        ergebnis = suche.find_duplicates(target, zeit, "", "pruefer", "nova")
    _finden.gelesen = lesen.called
    _finden.paar = lesen.call_args.args[1:3] if lesen.called else None
    return ergebnis


class DuplikatTest(unittest.TestCase):

    def test_derselbe_termin_am_selben_tag_ist_ein_duplikat(self) -> None:
        self.assertEqual(len(_finden("Schwester am Bahnhof abholen",
                                     [_eintrag("Abholung der Schwester am Bahnhof")])), 1)

    def test_ein_anker_ist_kein_duplikat(self) -> None:
        """Der gemessene Fall: der Erinnerungs-Anker der KZG."""
        self.assertEqual(_finden("Schwester abholen",
                                 [_eintrag("Erinnerungs-Anker 19.09.2026 Schwester", "erinnerungs_anker")]), [])

    def test_ein_anderer_termin_am_selben_tag_ist_keins(self) -> None:
        self.assertEqual(_finden("Zahnarzt", [_eintrag("Elternabend")]), [])

    def test_ein_inaktiver_termin_ist_keins(self) -> None:
        self.assertEqual(_finden("Zahnarzt", [_eintrag("Zahnarzt", aktiv=False)]), [])

    def test_ohne_titel_wird_nichts_als_duplikat_gewertet(self) -> None:
        self.assertEqual(_finden("", [_eintrag("Irgendwas")]), [])
        self.assertFalse(_finden.gelesen)

    def test_die_pruefung_liest_im_paar(self) -> None:
        """Ein Termin bei einer anderen Figur doppelt den neuen nicht — gelesen wird im Paar."""
        _finden("Zahnarzt", [])
        self.assertEqual(_finden.paar, ("pruefer", "nova"))


class AnlegenTest(unittest.TestCase):

    def _suchen(self, kontext: dict) -> dict:
        state = {"parameter": {"action": "create", "target": "", "zeitausdruck": ""},
                 "kontext": kontext, "aufgabe": "Gerne", "schritte": []}
        with patch("memory.repositories.timeline_repository.TimelineRepository.find_by_date_range",
                   return_value=[_eintrag("Erinnerungs-Anker 19.09.2026", "erinnerungs_anker")]):
            return suche.suchen(state)

    def test_ohne_titel_meldet_die_suche_nicht_mehr_abgeschlossen(self) -> None:
        """Vorher: Uebersicht → irgendein Eintrag → "bereits eingetragen", abgeschlossen."""
        ergebnis = self._suchen({"user_id": "pruefer", "character_id": "nova"})
        self.assertNotEqual(ergebnis["status"], "abgeschlossen")
        self.assertNotEqual(ergebnis["schritte"][-1]["ergebnis"], "ohne_character_id")

    def test_ohne_figur_wird_nichts_gesucht_und_nichts_geschrieben(self) -> None:
        with patch.object(suche, "raw_matches", wraps=suche.raw_matches) as lesen:
            ergebnis = self._suchen({"user_id": "pruefer"})
        self.assertEqual(ergebnis["status"], "fehler")
        self.assertEqual(ergebnis["schritte"][-1]["ergebnis"], "ohne_character_id")
        lesen.assert_not_called()

    def test_zwilling_mit_figur_wird_im_paar_gesucht(self) -> None:
        with patch.object(suche, "raw_matches", wraps=suche.raw_matches) as lesen:
            self._suchen({"user_id": "pruefer", "character_id": "nova"})
        self.assertEqual(lesen.call_args.args[2:4], ("pruefer", "nova"))


if __name__ == "__main__":
    unittest.main()
