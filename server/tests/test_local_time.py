"""Zeugen: Jeder Knoten mit einem *heute* nimmt den Ortstag mit deutschem Wochentag.

Eingefroren ist ein Zeitpunkt kurz nach Mitternacht Ortszeit, der in UTC noch
der Vortag ist: 31.12.2026 23:30 UTC ist in Berlin Freitag, der 01.01.2027,
00:30 Uhr. Ein Knoten, der `datetime.now()` ohne Zeitzone liest, nennt im
Behaelter den Donnerstag, den 31.12.2026 — und zwischen den beiden Tagen
urteilt das Tribunal ueber ein Datum mit einem anderen *heute* als der Prompt,
in dem es entstand.

Der Jahreswechsel ist mit Absicht gewaehlt: Eine Datumsangabe ohne Jahr bekommt
das naechstliegende Jahr zum *heute*, und das heute entscheidet hier ueber das
Jahr, also ueber den Wochentag. Der 02.07. liegt vom 31.12.2026 aus im Jahr 2026
naeher (ein Donnerstag), vom 01.01.2027 aus im Jahr 2027 (ein Freitag).

Die Zeugen brauchen keine Datenbank.
"""

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from graph.nodes import perzeption, router, tribunal
from graph.nodes import thinker as thinker_mod
from graph.nodes import verfasser as composer_mod
from utils import local_time

# Kurz nach Mitternacht Ortszeit; in UTC noch der Vortag.
_UTC_FROZEN: datetime = datetime(2026, 12, 31, 23, 30, tzinfo=timezone.utc)


def _frozen(utc: datetime) -> type:
    """Baut eine `datetime`-Klasse, deren `now()` den Zeitpunkt `utc` liefert.

    Ohne Zeitzone liefert sie die UTC-Wanduhr als naiven Wert — so verhielte
    sich der Behaelter.
    """
    class Frozen(datetime):
        @classmethod
        def now(cls, tz: ZoneInfo | None = None) -> datetime:
            return utc.astimezone(tz) if tz else utc.replace(tzinfo=None)

    return Frozen


class _WithFrozenClock(unittest.TestCase):
    """Friert die Uhr der gemeinsamen Hilfsfunktion ein, Zone Berlin."""

    utc: datetime = _UTC_FROZEN

    def setUp(self) -> None:
        for p in (
            patch.object(local_time, "datetime", _frozen(self.utc)),
            patch.object(local_time, "TIMEZONE", "Europe/Berlin"),
        ):
            p.start()
            self.addCleanup(p.stop)


class HelperTest(_WithFrozenClock):
    """Die Hilfsfunktionen: Ortstag statt UTC-Tag, Wochentag aus der Tabelle."""

    def test_local_day_instead_of_utc_day(self) -> None:
        now = local_time.now_local()
        self.assertEqual((now.year, now.month, now.day), (2027, 1, 1))
        self.assertEqual((now.hour, now.minute), (0, 30))
        self.assertEqual(str(now.tzinfo), "Europe/Berlin")

    def test_twin_midday_same_day(self) -> None:
        """Wo Ortstag und UTC-Tag zusammenfallen, aendert nur die Stunde."""
        with patch.object(local_time, "datetime",
                          _frozen(datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc))):
            now = local_time.now_local()
        self.assertEqual((now.month, now.day, now.hour), (7, 1, 12))

    def test_weekday_german_from_the_table(self) -> None:
        self.assertEqual(local_time.weekday_name(local_time.now_local()), "Freitag")
        self.assertEqual(
            [local_time.weekday_name(datetime(2026, 10, 12 + i)) for i in range(7)],
            ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
        )

    def test_weekday_wrong_type_is_loud(self) -> None:
        with self.assertRaises(TypeError):
            local_time.weekday_name("Freitag")  # type: ignore[arg-type]


class VerfasserTest(_WithFrozenClock):
    """Der Prompt des Verfassers nennt den Ortstag und einen deutschen Wochentag."""

    def test_prompt_names_local_day_and_german_weekday(self) -> None:
        state: dict = {
            "user_prompt": "Wie entsteht ein Gammablitz?",
            "user_id": "u", "character_id": "c", "turn_id": "t",
            "memory_context": "", "web_context": "",
            "session_turns": [], "task_block": "",
            "event_payload": {}, "event_source": "user",
            "gespraechsvektor": "", "gv_detail": {},
        }
        prompt: str = composer_mod._build_system_prompt(state)
        self.assertIn("Heute ist Freitag, 01.01.2027, es ist 00:30 Uhr.", prompt)
        self.assertNotIn("Friday", prompt)
        self.assertNotIn("31.12.2026", prompt)


class RouterTest(_WithFrozenClock):
    """Der Prompt des Routers nennt den Ortstag."""

    def test_prompt_names_local_day(self) -> None:
        with patch.object(router, "aushaenge_sammeln", return_value="BRETT"):
            prompt: str = router._build_router_prompt({}, session_turns=None)
        self.assertIn("01.01.2027, 00:30 Uhr", prompt)
        self.assertNotIn("31.12.2026", prompt)


class ThinkerTest(_WithFrozenClock):
    """Der Thinker reicht den Ortstag an seinen Prompt weiter."""

    def test_prompt_gets_local_day(self) -> None:
        state: dict = {
            "response":         "Der naechste bekannte Magnetar ist rund 9.000 Lichtjahre weg.",
            "user_prompt":      "Wie weit ist der naechste bekannte Magnetar von uns entfernt?",
            "needs_web":        True,
            "event_payload":    {},
            "node_annotations": [],
            "token_total":      0,
            "character_id":     "nova",
            "agent_results":    [],
            "memory_context":   "",
            "sachlage":         None,
        }
        reply = MagicMock(text="ERGEBNIS: OK", thinking="", token_total=0)
        normalizer = MagicMock()
        normalizer.pruefen.return_value = MagicMock(braucht_nachfass=False)
        with patch.object(thinker_mod.model_service.chat, "submit_sync", return_value=reply), \
                patch.object(thinker_mod, "get_thinking_normalizer", return_value=normalizer), \
                patch.object(thinker_mod, "_build_thinker_prompt",
                             wraps=thinker_mod._build_thinker_prompt) as build:
            thinker_mod.think(state, redis_client=MagicMock(),
                              postgres_url="postgresql://unbenutzt", user_id="u")
        self.assertEqual(build.call_args.args[0], "01.01.2027, 00:30 Uhr")


class PerceptionTest(_WithFrozenClock):
    """Die Perzeption reicht den Ortstag an ihren System-Prompt weiter."""

    def test_prompt_gets_local_day(self) -> None:
        # Eine echte Wahrnehmung: die Logzeile am Ende von `perceive` formatiert `arousal`.
        perception = perzeption.Wahrnehmung()
        with patch.object(perzeption, "_session_kontext_laden", return_value=("", "ok")), \
                patch.object(perzeption, "_record_decision"), \
                patch.object(perzeption, "_wahrnehmung_erheben",
                             return_value=(perception, "modell")), \
                patch.object(perzeption, "_ausreisser_protokollieren", return_value=0), \
                patch.object(perzeption, "_wahrnehmung_schreiben"), \
                patch.object(perzeption, "_ziel_personality"), \
                patch.object(perzeption, "_build_system_prompt",
                             wraps=perzeption._build_system_prompt) as build:
            perzeption.perceive({"user_prompt": "Hallo", "user_id": "u", "character_id": "c"})
        self.assertEqual(build.call_args.args[0], "01.01.2027, 00:30 Uhr")


class TribunalTest(_WithFrozenClock):
    """Das Datum ohne Jahr bekommt das Jahr des *heute* — das des Ortstags."""

    def _evaluate(self, response: str, sources: list[str]) -> dict:
        state: dict = {
            "response":      response,
            "agent_results": [
                MagicMock(agent_name="timeline", status="abgeschlossen", ergebnis=q)
                for q in sources
            ],
            "tribunal_votes": [
                {"agent": a, "vote": "ok", "reasoning": ""}
                for a in ("jurist", "psychologe", "ethik")
            ],
        }
        return tribunal.evaluate(state)

    def test_weekday_for_the_local_day_stays_ok(self) -> None:
        """Freitag, 02.07. ist 2027 richtig — 2026 war es ein Donnerstag."""
        state = self._evaluate("Wir treffen uns am Freitag, 02.07. um 14 Uhr.", [])
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(state["tribunal_summary"], "")

    def test_twin_wrong_weekday_is_found(self) -> None:
        """Der 02.07.2027 ist ein Freitag — ein Donnerstag dazu ist ein Widerspruch."""
        state = self._evaluate("Wir treffen uns am Donnerstag, 02.07. um 14 Uhr.", [])
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertIn("ZEITANGABE FALSCH", state["tribunal_summary"])

    def test_confirmation_against_the_service_takes_the_year_of_the_local_day(self) -> None:
        source: str = "Termin 'Zahnarzt' eingetragen fuer 02.07.2027 14:00"
        state = self._evaluate("Er steht am 02.07. um 14 Uhr.", [source])
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(state["tribunal_summary"], "")

    def test_twin_confirmation_of_another_day_is_found(self) -> None:
        source: str = "Termin 'Zahnarzt' eingetragen fuer 02.07.2027 14:00"
        state = self._evaluate("Er steht am 03.07. um 14 Uhr.", [source])
        self.assertEqual(state["tribunal_verdict"], "warnung")


if __name__ == "__main__":
    unittest.main()
