"""Unit-Test fuer _standard_interpretieren (Phase 0).

Scope: Nur die Keyword-Klassifikation der User-Antwort.
Routing, Strategy-Hook und End-to-End-Flow sind NICHT abgedeckt
(kommt mit Phase 1).

Bekannter Edge-Case (Backlog): Substring-Match von 'nicht' triggert
bei 'vernichten', 'nichtsdestotrotz' etc. faelschlich ABLEHNUNG.
Analog notizen/resume.py. Fix via Word-Split-Match in Phase 1.
"""

import unittest

from agents.charakter_identitaet.resume import (
    ABLEHNUNG,
    BESTAETIGUNG,
    UNKLAR,
    _standard_interpretieren,
)


class StandardInterpretierenTest(unittest.TestCase):

    def test_nein_gross(self):
        self.assertEqual(_standard_interpretieren("Nein"), ABLEHNUNG)

    def test_nein_klein(self):
        self.assertEqual(_standard_interpretieren("nein"), ABLEHNUNG)

    def test_nein_mit_begruendung(self):
        self.assertEqual(
            _standard_interpretieren("Nein, ich muss das korrigieren"),
            ABLEHNUNG,
        )

    def test_ja(self):
        self.assertEqual(_standard_interpretieren("Ja"), BESTAETIGUNG)

    def test_ok_mach(self):
        self.assertEqual(_standard_interpretieren("ok mach"), BESTAETIGUNG)

    def test_vielleicht_ist_unklar(self):
        self.assertEqual(_standard_interpretieren("vielleicht"), UNKLAR)

    def test_leer_ist_unklar(self):
        self.assertEqual(_standard_interpretieren(""), UNKLAR)


if __name__ == "__main__":
    unittest.main()
