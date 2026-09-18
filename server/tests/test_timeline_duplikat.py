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
        ergebnis = suche.find_duplicates(target, zeit, "", "pruefer")
    _finden.gelesen = lesen.called
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


class AnlegenTest(unittest.TestCase):

    def test_ohne_titel_meldet_die_suche_nicht_mehr_abgeschlossen(self) -> None:
        """Vorher: Uebersicht → irgendein Eintrag → "bereits eingetragen", abgeschlossen."""
        state = {"parameter": {"action": "create", "target": "", "zeitausdruck": ""},
                 "kontext": {"user_id": "pruefer"}, "aufgabe": "Gerne", "schritte": []}
        with patch("memory.repositories.timeline_repository.TimelineRepository.find_by_date_range",
                   return_value=[_eintrag("Erinnerungs-Anker 19.09.2026", "erinnerungs_anker")]):
            ergebnis = suche.suchen(state)
        self.assertNotEqual(ergebnis["status"], "abgeschlossen")


if __name__ == "__main__":
    unittest.main()
