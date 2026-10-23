"""Zeugen: eine faellige Wiedervorlage aus der Timeline traegt Titel und Details ihres Termins.

Die Tabelle `timeline` hat die Spalten `title` und `details`. Gelesen wurden
frueher `titel` und `beschreibung`, die es nicht gibt: Jede faellige Timeline-
Wiedervorlage trug deshalb einen leeren Titel und leere Details.

Zeugen dieser Datei:
  * Titel und Details kommen aus `title` und `details`.
  * Sind die Details leer, tritt der Titel an ihre Stelle (Zwilling).
  * Eine Zeile ohne `title` erzeugt keinen Eintrag und einen Fehler im Log.
  * Neben der defekten Zeile bleibt eine heile Zeile erhalten.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.wiedervorlage.agent import WiedervorlageAgent

_AGENT: str = "agents.wiedervorlage.agent"


def _sammeln(timeline_zeilen: list[dict]) -> list[dict]:
    """Ruft `_faellige_sammeln`; Timeline liefert die Zeilen, die anderen Quellen nichts."""
    with (
        patch(f"{_AGENT}.EntitaetenRepository.find_wiedervorlage_faellig", return_value=[]),
        patch(f"{_AGENT}.FaktenRepository.find_wiedervorlage_faellig", return_value=[]),
        patch(f"{_AGENT}.NotizenRepository.find_wiedervorlage_faellig", return_value=[]),
        patch(
            f"{_AGENT}.TimelineRepository.find_wiedervorlage_faellig",
            return_value=timeline_zeilen,
        ),
    ):
        return WiedervorlageAgent._faellige_sammeln("nutzer_a")


class TestTimelineWiedervorlage(unittest.TestCase):
    """Die Timeline-Zeile in der Form der Tabelle wird richtig gelesen."""

    def test_titel_und_details_aus_den_spalten(self) -> None:
        zeilen = [{"id": 7, "title": "Zahnarzt anrufen", "details": "Termin fuer Kontrolle"}]
        eintraege = _sammeln(zeilen)
        self.assertEqual(len(eintraege), 1)
        self.assertEqual(eintraege[0]["tabelle"], "timeline")
        self.assertEqual(eintraege[0]["id"], 7)
        self.assertEqual(eintraege[0]["titel"], "Zahnarzt anrufen")
        self.assertEqual(eintraege[0]["details"], "Termin fuer Kontrolle")

    def test_leere_details_nehmen_den_titel(self) -> None:
        for details in ("", None):
            with self.subTest(details=details):
                eintraege = _sammeln([{"id": 8, "title": "Steuererklaerung", "details": details}])
                self.assertEqual(len(eintraege), 1)
                self.assertEqual(eintraege[0]["titel"], "Steuererklaerung")
                self.assertEqual(eintraege[0]["details"], "Steuererklaerung")

    def test_zeile_ohne_title_wird_laut_verworfen(self) -> None:
        with self.assertLogs("ki_server.agents.wiedervorlage", level="ERROR") as protokoll:
            eintraege = _sammeln([{"id": 9, "details": "Details ohne Titel"}])
        self.assertEqual(eintraege, [])
        self.assertIn("9", "\n".join(protokoll.output))

    def test_leerer_title_wird_laut_verworfen(self) -> None:
        with self.assertLogs("ki_server.agents.wiedervorlage", level="ERROR"):
            eintraege = _sammeln([{"id": 10, "title": "  ", "details": "x"}])
        self.assertEqual(eintraege, [])

    def test_heile_zeile_neben_defekter_bleibt(self) -> None:
        zeilen = [
            {"id": 11, "details": "ohne Titel"},
            {"id": 12, "title": "Geburtstag Tom", "details": "Geschenk besorgen"},
        ]
        with self.assertLogs("ki_server.agents.wiedervorlage", level="ERROR"):
            eintraege = _sammeln(zeilen)
        self.assertEqual([e["id"] for e in eintraege], [12])
        self.assertEqual(eintraege[0]["titel"], "Geburtstag Tom")


if __name__ == "__main__":
    unittest.main()
