"""Tests: Bei einer Zustimmung sagt der Prompt, WORAUF sie sich bezieht.

Anlass `[gemessen 17.09.2026, Betrieb]`: Die Timeline bekam nach einer
Zustimmung genau die angebotene Sache als Objektbezug (*"Abholung der Schwester
am Bahnhof"*, Samstag 10 Uhr) — und klassifizierte trotzdem auf `target=
'Zahnarzt'` aus dem Verlauf, `zeit=''`, Ausgang `fehler`. Der `[OBJEKT]`-Block
greift nur, wenn die Aeusserung selbst nichts nennt; steht im Verlauf eine
andere Sache, gewinnt der Verlauf.

Der neue Block steht NUR bei einer Zustimmung — sonst waere er eine Behauptung
ueber einen Auftrag, den niemand gegeben hat.

**Was diese Tests NICHT koennen:** ob das Modell dem Block folgt. Das misst die
Reihe in labor/.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.notizen import klassifikation as notizen_klassifikation
from agents.timeline import klassifikation as timeline_klassifikation

BEZUG = [{"name": "Abholung der Schwester am Bahnhof", "klasse": "vorgang",
          "gedeckt": {"Tag": "Samstag", "Uhrzeit": "10 Uhr"}}]
SATZ = "Soll ich dir die Abholung eintragen?"


class ZustimmungsBlockTest(unittest.TestCase):

    def test_beide_dienste_tragen_den_block_bei_zustimmung(self) -> None:
        for modul in (timeline_klassifikation, notizen_klassifikation):
            with self.subTest(modul=modul.__name__):
                prompt = modul._build_classify_prompt(None, None, BEZUG, angebot_satz=SATZ)
                self.assertIn("[ZUSTIMMUNG]", prompt)
                self.assertIn(SATZ, prompt)
                self.assertIn("Abholung der Schwester am Bahnhof", prompt)
                self.assertIn("nicht aus dem Verlauf", prompt)

    def test_ohne_zustimmung_kein_block(self) -> None:
        for modul in (timeline_klassifikation, notizen_klassifikation):
            with self.subTest(modul=modul.__name__):
                self.assertNotIn("[ZUSTIMMUNG]", modul._build_classify_prompt(None, None, BEZUG))
                self.assertNotIn("[ZUSTIMMUNG]", modul._build_classify_prompt(None, None, None, angebot_satz=SATZ))

    def test_der_block_steht_hinter_dem_objektblock(self) -> None:
        """Erst die Sache, dann die Bindung an sie — sonst zeigt die Bindung ins Leere."""
        prompt = timeline_klassifikation._build_classify_prompt(None, None, BEZUG, angebot_satz=SATZ)
        self.assertLess(prompt.index("[OBJEKT]"), prompt.index("[ZUSTIMMUNG]"))


class BindungImCodeTest(unittest.TestCase):
    """Was feststeht, wird gesetzt — nicht erbeten (gemessen 17.09.2026)."""

    def test_ziel_und_zeit_kommen_aus_der_zugestimmten_sache(self) -> None:
        from agents.object_nearness import consent_fields
        self.assertEqual(consent_fields(BEZUG), ("Abholung der Schwester am Bahnhof", "Samstag 10 Uhr"))

    def test_ohne_zeitangabe_bleibt_die_zeit_leer(self) -> None:
        from agents.object_nearness import consent_fields
        self.assertEqual(consent_fields([{"name": "Einkaufsliste", "klasse": "objekt", "gedeckt": {"Bedarf": "Mehl"}}]),
                         ("Einkaufsliste", ""))

    def test_ohne_sache_wird_nichts_geraten(self) -> None:
        from agents.object_nearness import consent_fields
        for bezug in ([], [None], [{}]):
            with self.subTest(bezug=bezug):
                self.assertEqual(consent_fields(bezug), ("", "") if bezug != [{}] else ("", ""))

    def _klassifizieren(self, modul, antwort: dict, angebot_satz: str) -> dict:
        """Laesst die echte Klassifikation laufen, mit einem Modell, das leere Felder liefert."""
        stell = SimpleNamespace(chat=SimpleNamespace(submit_sync=lambda request, timeout=None: SimpleNamespace(
            text=json.dumps(antwort), token_total=0, thinking="", parsed=dict(antwort))))
        state = {"aufgabe": "Gerne", "aufgabe_typ": "workflow", "agent_name": "dienst",
                 "kontext": {"user_id": "", "character_id": "nova", "memory_context": "",
                             "objekt_bezug": BEZUG, "angebot_satz": angebot_satz},
                 "parameter": {"action": "agent"}, "schritte": [], "ergebnis": None,
                 "status": "laufend", "rueckfrage": None, "fehler": None}
        with patch.object(modul, "model_service", stell):
            return modul.klassifizieren(state)["parameter"]

    def test_die_timeline_fuellt_ziel_und_zeit_aus_der_sache(self) -> None:
        """Der gemessene Fall: action create, target und zeit leer."""
        leer = {"action": "create", "target": "", "zeitausdruck": "", "event_type": "termin", "normalisiert": ""}
        gefuellt = self._klassifizieren(timeline_klassifikation, leer, SATZ)
        self.assertEqual(gefuellt["target"], "Abholung der Schwester am Bahnhof")
        self.assertEqual(gefuellt["zeitausdruck"], "Samstag 10 Uhr")

    def test_ohne_zustimmung_bleibt_leer_was_leer_ist(self) -> None:
        leer = {"action": "create", "target": "", "zeitausdruck": "", "event_type": "termin", "normalisiert": ""}
        ohne = self._klassifizieren(timeline_klassifikation, leer, "")
        self.assertEqual(ohne["target"], "")
        self.assertEqual(ohne["zeitausdruck"], "")

    def test_bei_blanker_zustimmung_gewinnt_die_sache_nicht_der_verlauf(self) -> None:
        """Gemessen 18.09.2026: Titel aus dem Verlauf, Zeit aus der Sache — ein Mischtermin."""
        aus_dem_verlauf = {"action": "create", "target": "Zahnarzttermin am Donnerstag um 15 Uhr",
                           "zeitausdruck": "", "event_type": "termin", "normalisiert": ""}
        ergebnis = self._klassifizieren(timeline_klassifikation, aus_dem_verlauf, SATZ)
        self.assertEqual(ergebnis["target"], "Abholung der Schwester am Bahnhof")
        self.assertEqual(ergebnis["zeitausdruck"], "Samstag 10 Uhr")

    def test_ohne_zustimmung_bleibt_was_das_modell_nennt(self) -> None:
        eigen = {"action": "create", "target": "Zahnarzt", "zeitausdruck": "Donnerstag 15 Uhr",
                 "event_type": "termin", "normalisiert": ""}
        ergebnis = self._klassifizieren(timeline_klassifikation, eigen, "")
        self.assertEqual((ergebnis["target"], ergebnis["zeitausdruck"]), ("Zahnarzt", "Donnerstag 15 Uhr"))

    def test_die_notizen_fuellen_das_ziel_aus_der_sache(self) -> None:
        leer = {"action": "add_content", "target": "", "target_typ": "titel", "normalisiert": ""}
        gefuellt = self._klassifizieren(notizen_klassifikation, leer, SATZ)
        self.assertEqual(gefuellt["target"], "Abholung der Schwester am Bahnhof")


class VerdrahtungTest(unittest.TestCase):

    def test_der_satz_kommt_aus_dem_kontext_des_dienstes(self) -> None:
        import inspect
        for modul in (timeline_klassifikation, notizen_klassifikation):
            with self.subTest(modul=modul.__name__):
                quelle = inspect.getsource(modul.klassifizieren)
                self.assertIn('state["kontext"].get("angebot_satz")', quelle)

    def test_der_dispatch_legt_den_satz_in_den_kontext(self) -> None:
        import inspect

        from agents.notizen import dispatch as notizen_dispatch
        from agents.timeline import dispatch as timeline_dispatch
        for modul in (timeline_dispatch, notizen_dispatch):
            with self.subTest(modul=modul.__name__):
                self.assertIn('"angebot_satz": state.get("angebot_satz")', inspect.getsource(modul))


if __name__ == "__main__":
    unittest.main()
