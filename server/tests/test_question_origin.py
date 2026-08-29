"""Zeugen: der Rueckfrage-Gegenstand kennt seine Herkunft — Blase oder Novas eigener Zug.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 3 (Nachtrag
29.08.2026). Gemessen ueber 20 Betriebsturns: 17 Gegenstaende kamen aus dem
staerksten Kurzziel, und nach einem Themenwechsel zog das alte — die
Gravitation, gewollt. Die Rueckfrage-Zeile gab Novas Zug aber als Frage an
den Nutzer zu seiner Sache aus. Jetzt traegt der Gegenstand seine Herkunft,
und die Zeile fuehrt bei eigenem Zug.

Zeugen dieser Datei:
  * **`question_target_origin` liefert Blase oder eigenen Zug** — eine
    `nutzer`-Eigenschaft und ein Kurzziel zu einem akuten Objekt sind Blase,
    ein Kurzziel ausserhalb der Blase ist eigener Zug; `question_target`
    bleibt wortgleich.
  * **Die Rueckfrage-Zeile fuehrt nur bei eigenem Zug** und traegt kein
    Verbot; ohne Gegenstand steht sie wie bisher.
  * **Der Verfasser reicht die Herkunft durch** (Verdrahtung).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from ei.haltung import haltung_berechnen
from ei.haltungssprache import stoffzeilen
from graph.nodes import verfasser as verf_mod
from graph.nodes.sachlage import (
    GEGENSTAND_AUS_BLASE,
    GEGENSTAND_EIGENER_ZUG,
    TRAEGER_NUTZER,
    TRAEGER_WELT,
    question_target,
    question_target_origin,
)

RAD_FRAGEND: dict[str, float] = {"wissbegier": 0.87, "aufmerksamkeit": 0.91}


def _bubble(name: str = "Gamma-Oszillationen", offen: list[str] | None = None,
            traeger: dict | None = None) -> dict:
    return {
        "thema": name, "gegenstand": name, "nutzerziel": "verstehen", "ausdrucksweise": "pruefend",
        "objekte": [{"name": name, "klasse": "vorgang", "akut": True, "gedeckt": {},
                     "offen": list(offen or []), "traeger": dict(traeger or {}), "sprecher": {}}],
    }


def _goal(objekt: str) -> dict:
    return {"ziel_typ": "kurzfristig",
            "zielsatz": f"Ich möchte dem Nutzer bei seinem Vorhaben helfen: {objekt} — verstehen"}


class OriginTest(unittest.TestCase):
    """Woher der Gegenstand stammt."""

    def test_user_property_comes_from_the_bubble(self) -> None:
        b = _bubble(offen=["wer"], traeger={"wer": TRAEGER_NUTZER})
        self.assertEqual(
            question_target_origin(b, [_goal("Magnetar")]),
            ("Gamma-Oszillationen — was dazu noch offen ist: wer", GEGENSTAND_AUS_BLASE),
        )

    def test_goal_on_an_acute_object_comes_from_the_bubble(self) -> None:
        b = _bubble(offen=["Mechanismus"], traeger={"Mechanismus": TRAEGER_WELT})
        self.assertEqual(question_target_origin(b, [_goal("gamma-oszillationen")]),
                         ("wie es mit gamma-oszillationen weitergeht", GEGENSTAND_AUS_BLASE))

    def test_goal_outside_the_bubble_is_novas_own_pull(self) -> None:
        # `[gemessen]` 29.08.2026: »wie es mit Magnetar weitergeht« bei den Gamma-Oszillationen.
        b = _bubble(offen=["Mechanismus"], traeger={"Mechanismus": TRAEGER_WELT})
        self.assertEqual(question_target_origin(b, [_goal("Magnetar")]),
                         ("wie es mit Magnetar weitergeht", GEGENSTAND_EIGENER_ZUG))

    def test_no_target_without_user_property_and_goal(self) -> None:
        b = _bubble(offen=["Mechanismus"], traeger={"Mechanismus": TRAEGER_WELT})
        self.assertIsNone(question_target_origin(b, []))

    def test_question_target_stays_the_same_string(self) -> None:
        b = _bubble(offen=["Mechanismus"], traeger={"Mechanismus": TRAEGER_WELT})
        self.assertEqual(question_target(b, [_goal("Magnetar")]), "wie es mit Magnetar weitergeht")
        self.assertIsNone(question_target(b, []))


class LineTest(unittest.TestCase):
    """Die Rueckfrage-Zeile fuehrt bei eigenem Zug — und nur dann."""

    def _line(self, gegenstand: str | None, eigener_zug: bool) -> str:
        haltung = haltung_berechnen("werkstatt", RAD_FRAGEND)
        return stoffzeilen(haltung, 120, (), gegenstand, eigener_zug)[1]

    def test_own_pull_leads_whose_goal_it_is(self) -> None:
        zeile = self._line("wie es mit Magnetar weitergeht", True)
        self.assertIn("ihr Gegenstand: wie es mit Magnetar weitergeht", zeile)
        self.assertIn("das ist Person As eigenes Ziel, nicht die Sache von Person B", zeile)
        self.assertIn("laesst ihm die Wahl, mitzugehen", zeile)

    def test_bubble_target_carries_no_own_pull_guidance(self) -> None:
        zeile = self._line("wie es mit Magnetar weitergeht", False)
        self.assertIn("ihr Gegenstand: wie es mit Magnetar weitergeht", zeile)
        self.assertNotIn("eigenes Ziel", zeile)

    def test_line_without_target_is_unchanged_and_carries_no_prohibition(self) -> None:
        zeile = self._line(None, True)
        self.assertNotIn("Gegenstand", zeile)
        for verbot in ("Frage nicht", "keine Rueckfrage zu seiner Sache", "nicht als Rueckfrage"):
            with self.subTest(verbot=verbot):
                self.assertNotIn(verbot, self._line("x", True))


class WiringTest(unittest.TestCase):
    """Der Verfasser reicht die Herkunft an die Zeile durch."""

    def _state(self, goal_object: str) -> dict:
        return {
            "user_prompt": "Wie entstehen die Oszillationen?", "event_source": "user",
            "event_payload": {},
            "user_id": "u", "character_id": "c", "turn_id": "t",
            "memory_context": "", "web_context": "", "session_turns": [], "task_block": "",
            "gespraechsvektor": "", "gv_detail": {}, "node_annotations": {},
            "sachlage": {
                **_bubble(offen=["Mechanismus"], traeger={"Mechanismus": TRAEGER_WELT}),
                "herkunft": "frisch",
            },
            "haltung": haltung_berechnen("werkstatt", RAD_FRAGEND),
            "aktivierte_ziele": [_goal(goal_object)],
        }

    def test_prompt_leads_when_the_goal_lies_outside_the_bubble(self) -> None:
        prompt = verf_mod._build_system_prompt(self._state("Magnetar"))
        self.assertIn(
            "ihr Gegenstand: wie es mit Magnetar weitergeht; das ist Person As eigenes Ziel",
            prompt,
        )

    def test_prompt_stays_plain_when_the_goal_belongs_to_the_bubble(self) -> None:
        prompt = verf_mod._build_system_prompt(self._state("Gamma-Oszillationen"))
        self.assertIn("ihr Gegenstand: wie es mit Gamma-Oszillationen weitergeht", prompt)
        self.assertNotIn("eigenes Ziel", prompt)


if __name__ == "__main__":
    unittest.main()
