"""Tests: Ein Termin mit Spanne bekommt sein Ende — Scheibe 12 D.

Die Spalte `event_ende` wurde nie geschrieben; die Absicht des Eigentuemers
(14.09.2026) nennt Zeitraeume mit Start- und Endzeitpunkt ausdruecklich. Das
Ende muss nach dem Anfang liegen — eine Frist (*"bis Freitag abgeben"*) bleibt
ohne Ende.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from agents.timeline import crud as timeline_crud
from utils.time_span import span_end, span_start_text

TZ = ZoneInfo("Europe/Berlin")
SA_10 = datetime(2026, 9, 19, 10, 0, tzinfo=TZ)


class SpanneTest(unittest.TestCase):

    def test_uhrzeiten(self) -> None:
        for ausdruck, stunde in (("von 10 bis 12 Uhr", 12), ("10–12 Uhr", 12), ("bis 16 Uhr", 16),
                                 ("10:00 - 11:30 Uhr", 11)):
            with self.subTest(ausdruck=ausdruck):
                self.assertEqual(span_end(ausdruck, SA_10).hour, stunde)

    def test_dauern(self) -> None:
        self.assertEqual(span_end("für zwei Stunden", SA_10), SA_10.replace(hour=12))
        self.assertEqual(span_end("drei Stunden lang", SA_10), SA_10.replace(hour=13))
        self.assertEqual(span_end("für 90 Minuten", SA_10), SA_10.replace(hour=11, minute=30))

    def test_mehrtaegig(self) -> None:
        start = datetime(2026, 10, 3, 0, 0, tzinfo=TZ)
        ende = span_end("vom 3. bis 5. Oktober", start)
        self.assertEqual((ende.day, ende.month), (5, 10))

    def test_eine_frist_ist_keine_spanne(self) -> None:
        freitag = datetime(2026, 9, 18, 0, 0, tzinfo=TZ)
        with patch("utils.zeitparser.zeit_parsen_vektor") as parser:
            parser.return_value.datum = freitag
            parser.return_value.tag_erkannt = True
            parser.return_value.uhrzeit_erkannt = False
            self.assertIsNone(span_end("bis Freitag", freitag.replace(hour=23, minute=59)))

    def test_ohne_spanne_kein_ende(self) -> None:
        for ausdruck in ("Samstag um 10", "", "morgen"):
            with self.subTest(ausdruck=ausdruck):
                self.assertIsNone(span_end(ausdruck, SA_10))


class AnfangTest(unittest.TestCase):

    def test_der_endteil_faellt_fuer_den_anfang(self) -> None:
        self.assertEqual(span_start_text("19.09.2026 von 10 bis 12 Uhr"), "19.09.2026 10 Uhr")
        self.assertEqual(span_start_text("vom 3. bis 5. Oktober"), "3. Oktober")
        self.assertEqual(span_start_text("Samstag um 10 Uhr"), "Samstag um 10 Uhr")


class AnlegenTest(unittest.TestCase):

    def test_das_ende_erreicht_die_tabelle(self) -> None:
        state = {"aufgabe": "Trag den Flohmarkt ein", "kontext": {"user_id": "pruefer"},
                 "parameter": {"action": "create", "target": "Flohmarkt",
                               "zeitausdruck": "19.09.2026 von 10 bis 12 Uhr", "event_type": "termin"},
                 "schritte": []}
        with patch("memory.repositories.timeline_repository.TimelineRepository.insert",
                   return_value=4711) as einfuegen, \
             patch.object(timeline_crud, "_verifizieren_termin", return_value=True):
            timeline_crud._create(state)
        ende = einfuegen.call_args.kwargs["event_ende"]
        self.assertIsNotNone(ende)
        self.assertEqual(ende.hour, 12)


if __name__ == "__main__":
    unittest.main()
