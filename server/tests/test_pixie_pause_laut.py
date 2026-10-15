"""Tests: Ein stehender Pausenschalter steht im Log auf `warning`.

**Ein vergessener Schalter soll im Log schreien, nicht schweigen.** `[gemessen]`
Ein Schalter stand zehn Tage, und jeder Zyklus verwarf sich mit einer
`debug`-Zeile — im Log war nichts davon zu sehen. Die Zeile nennt seither den
Schalter und seit wann er steht, und sie kommt je Schalter einmal je
Drosselintervall, nicht je Zyklus.

Zeugen dieser Datei:
  * **Der echte Heartbeat und die echte Zustellschleife laufen**, nur Redis ist
    ein Doppel mit Uhr: Ein Zeuge auf die Hilfsfunktion allein bliebe gruen,
    wenn sie nie gerufen wuerde.
  * **Jede Abweisung hat einen Zwilling:** Ohne Schalter keine Zeile, mit einem
    anderen Schalter keine Zeile fuer diesen.
  * **Die Drossel wird ueber die Uhr des Doppels belegt**, nicht ueber die
    Konstante: Der Zeuge rechnet das Intervall nicht aus dem Wert, den er prueft.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import asyncio
import unittest
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from api import admin
from config import (
    PIXIE_AGENTEN_PAUSE_SCHLUESSEL,
    PIXIE_DELIVERY_PAUSE_SCHLUESSEL,
    PIXIE_PAUSE_SCHLUESSEL,
    PIXIE_PAUSE_WARNUNG_SEKUNDEN,
)
from services import shadow_delivery
from services.pixie import pause, scheduler

LOGGER: str = "ki_server.pixie"


class _Redis:
    """Ein Redis mit Uhr: Schluessel laufen nach `ex` Sekunden ab."""

    def __init__(self) -> None:
        """Beginnt bei Uhrzeit null mit leerem Speicher."""
        self.clock: float = 0.0
        self.values: dict[str, str] = {}
        self.expiry: dict[str, float] = {}

    def _alive(self, key: str) -> bool:
        if key in self.expiry and self.expiry[key] <= self.clock:
            del self.values[key]
            del self.expiry[key]
        return key in self.values

    def exists(self, key: str) -> int:
        return 1 if self._alive(key) else 0

    def get(self, key: str) -> str | None:
        return self.values[key] if self._alive(key) else None

    def set(self, key: str, value: str, nx: bool = False, ex: int | None = None) -> bool:
        if nx and self._alive(key):
            return False
        self.values[key] = value
        if ex is not None:
            self.expiry[key] = self.clock + ex
        else:
            self.expiry.pop(key, None)
        return True

    def delete(self, key: str) -> None:
        self.values.pop(key, None)
        self.expiry.pop(key, None)

    def llen(self, key: str) -> int:
        return 0

    def lrange(self, key: str, start: int, end: int) -> list:
        return []


def _warnings(logs: "unittest.case._AssertLogsContext") -> list[str]:
    """Die `warning`-Zeilen eines `assertLogs`-Laufs."""
    return [r.getMessage() for r in logs.records if r.levelname == "WARNING"]


def _heartbeat(redis: _Redis, track: str = "llm") -> None:
    """Ein echter Heartbeat-Zyklus gegen das Doppel, ohne Kandidaten."""
    with patch.object(scheduler, "redis_client", redis), \
         patch.object(scheduler, "kandidaten_sammeln", return_value=[]):
        asyncio.run(scheduler.pixie_heartbeat(MagicMock(), spur=track))


class SwitchInHeartbeat(unittest.TestCase):
    """Der Heartbeat meldet einen stehenden Schalter auf `warning`."""

    def test_two_cycles_in_interval_give_exactly_one_warning(self) -> None:
        redis = _Redis()
        pause.set_pause(redis, PIXIE_PAUSE_SCHLUESSEL,
                        datetime(2026, 10, 3, 12, 26, tzinfo=UTC))

        with self.assertLogs(LOGGER, level="DEBUG") as logs:
            _heartbeat(redis)
            redis.clock += 120
            _heartbeat(redis)

        lines = _warnings(logs)
        self.assertEqual(1, len(lines), f"Erwartet genau eine Warnung: {lines}")
        self.assertIn(PIXIE_PAUSE_SCHLUESSEL, lines[0])
        self.assertIn("2026-10-03T12:26:00+00:00", lines[0])

    def test_next_warning_comes_after_interval(self) -> None:
        redis = _Redis()
        pause.set_pause(redis, PIXIE_PAUSE_SCHLUESSEL)

        with self.assertLogs(LOGGER, level="DEBUG") as logs:
            _heartbeat(redis)
            redis.clock += PIXIE_PAUSE_WARNUNG_SEKUNDEN - 1
            _heartbeat(redis)
            redis.clock += 1
            _heartbeat(redis)

        self.assertEqual(2, len(_warnings(logs)), _warnings(logs))

    def test_both_tracks_share_the_throttle(self) -> None:
        redis = _Redis()
        pause.set_pause(redis, PIXIE_PAUSE_SCHLUESSEL)

        with self.assertLogs(LOGGER, level="DEBUG") as logs:
            _heartbeat(redis, track="llm")
            _heartbeat(redis, track="cpu")

        self.assertEqual(1, len(_warnings(logs)), _warnings(logs))

    def test_switch_without_moment_is_since_unknown(self) -> None:
        """Altbestand: gesetzt vor dem Nebenschluessel — nie als *jetzt* gemeldet."""
        redis = _Redis()
        redis.set(PIXIE_PAUSE_SCHLUESSEL, "1")

        with self.assertLogs(LOGGER, level="DEBUG") as logs:
            _heartbeat(redis)

        lines = _warnings(logs)
        self.assertEqual(1, len(lines), lines)
        self.assertIn("seit unbekannt", lines[0])
        self.assertNotIn("2026", lines[0], "Ein Zeitpunkt wurde erfunden")

    def test_unreadable_moment_is_named_instead_of_guessed(self) -> None:
        redis = _Redis()
        redis.set(PIXIE_PAUSE_SCHLUESSEL, "1")
        redis.set(PIXIE_PAUSE_SCHLUESSEL + pause.SINCE_SUFFIX, "gestern abend")

        with self.assertLogs(LOGGER, level="DEBUG") as logs:
            _heartbeat(redis)

        lines = _warnings(logs)
        self.assertIn("seit unbekannt (unlesbar: 'gestern abend')", lines[0])

    def test_without_switch_no_warning_and_the_cycle_runs(self) -> None:
        """Der Zwilling: Ohne Pause sammelt der Heartbeat Kandidaten wie heute."""
        redis = _Redis()
        collect = MagicMock(return_value=[])

        with patch.object(scheduler, "redis_client", redis), \
             patch.object(scheduler, "kandidaten_sammeln", collect), \
             self.assertNoLogs(LOGGER, level="WARNING"):
            asyncio.run(scheduler.pixie_heartbeat(MagicMock(), spur="llm"))

        collect.assert_called_once()

    def test_standing_switch_keeps_the_cycle_stopped(self) -> None:
        """Die Lautstaerke aendert die Pause nicht."""
        redis = _Redis()
        pause.set_pause(redis, PIXIE_PAUSE_SCHLUESSEL)
        collect = MagicMock(return_value=[])

        with patch.object(scheduler, "redis_client", redis), \
             patch.object(scheduler, "kandidaten_sammeln", collect), \
             self.assertLogs(LOGGER, level="DEBUG") as logs:
            asyncio.run(scheduler.pixie_heartbeat(MagicMock(), spur="llm"))

        collect.assert_not_called()
        self.assertTrue([r for r in logs.records if r.levelname == "DEBUG"],
                        "Die debug-Zeile je verworfenem Zyklus ist weggefallen")

    def test_agents_pause_has_its_own_witness(self) -> None:
        redis = _Redis()
        pause.set_pause(redis, PIXIE_AGENTEN_PAUSE_SCHLUESSEL)

        with self.assertLogs(LOGGER, level="DEBUG") as logs:
            _heartbeat(redis)

        lines = _warnings(logs)
        self.assertEqual(1, len(lines), lines)
        self.assertIn(PIXIE_AGENTEN_PAUSE_SCHLUESSEL, lines[0])

    def test_delivery_pause_neither_stops_nor_reports_in_the_heartbeat(self) -> None:
        """Der Zwilling zur Agentenpause: Der Heartbeat betrifft sie nicht."""
        redis = _Redis()
        pause.set_pause(redis, PIXIE_DELIVERY_PAUSE_SCHLUESSEL)
        collect = MagicMock(return_value=[])

        with patch.object(scheduler, "redis_client", redis), \
             patch.object(scheduler, "kandidaten_sammeln", collect), \
             self.assertNoLogs(LOGGER, level="WARNING"):
            asyncio.run(scheduler.pixie_heartbeat(MagicMock(), spur="llm"))

        collect.assert_called_once()

    def test_two_switches_give_one_warning_each(self) -> None:
        """Die Drossel gilt je Schalter, nicht fuer alle zusammen."""
        redis = _Redis()
        pause.set_pause(redis, PIXIE_PAUSE_SCHLUESSEL)
        pause.set_pause(redis, PIXIE_AGENTEN_PAUSE_SCHLUESSEL)

        with self.assertLogs(LOGGER, level="DEBUG") as logs:
            _heartbeat(redis)

        lines = _warnings(logs)
        self.assertEqual(2, len(lines), lines)
        self.assertTrue(any(PIXIE_PAUSE_SCHLUESSEL + " " in z for z in lines))
        self.assertTrue(any(PIXIE_AGENTEN_PAUSE_SCHLUESSEL in z for z in lines))


class SwitchInDeliveryLoop(unittest.TestCase):
    """Die Zustellschleife meldet die Zustellpause und den Vollschalter."""

    def _cycle(self, redis: _Redis) -> None:
        stop_event = MagicMock()
        stop_event.is_set.side_effect = [False, True, True, True]
        with patch.object(shadow_delivery, "PRÜF_INTERVALL", 0.0), \
             patch.object(shadow_delivery, "shutdown_event", stop_event):
            asyncio.run(shadow_delivery.shadow_delivery_loop(
                redis_client=redis,
                websocket_map={"meister": object()},
                graph_run_lock=None,
            ))

    def test_delivery_pause_is_on_warning(self) -> None:
        redis = _Redis()
        pause.set_pause(redis, PIXIE_DELIVERY_PAUSE_SCHLUESSEL)

        with self.assertLogs(LOGGER, level="DEBUG") as logs:
            self._cycle(redis)

        lines = _warnings(logs)
        self.assertEqual(1, len(lines), lines)
        self.assertIn(PIXIE_DELIVERY_PAUSE_SCHLUESSEL, lines[0])

    def test_agents_pause_is_silent_for_delivery(self) -> None:
        """Der Zwilling: Die Zustellung laeuft, also meldet sie nichts."""
        redis = _Redis()
        pause.set_pause(redis, PIXIE_AGENTEN_PAUSE_SCHLUESSEL)

        with self.assertNoLogs(LOGGER, level="WARNING"):
            self._cycle(redis)

    def test_heartbeat_and_delivery_share_the_throttle_of_the_full_switch(self) -> None:
        redis = _Redis()
        pause.set_pause(redis, PIXIE_PAUSE_SCHLUESSEL)

        with self.assertLogs(LOGGER, level="DEBUG") as logs:
            _heartbeat(redis)
            self._cycle(redis)

        self.assertEqual(1, len(_warnings(logs)), _warnings(logs))


class MomentIsRemembered(unittest.TestCase):
    """`set_pause` und die Admin-Endpunkte merken den Zeitpunkt und raeumen ihn ab."""

    def test_set_pause_remembers_the_moment_and_keeps_the_value(self) -> None:
        redis = _Redis()
        pause.set_pause(redis, PIXIE_PAUSE_SCHLUESSEL,
                        datetime(2026, 10, 14, 8, 0, tzinfo=UTC))

        self.assertEqual("1", redis.get(PIXIE_PAUSE_SCHLUESSEL))
        self.assertEqual("2026-10-14T08:00:00+00:00",
                         redis.get(PIXIE_PAUSE_SCHLUESSEL + pause.SINCE_SUFFIX))

    def test_second_set_keeps_the_first_moment(self) -> None:
        redis = _Redis()
        pause.set_pause(redis, PIXIE_PAUSE_SCHLUESSEL,
                        datetime(2026, 10, 14, 8, 0, tzinfo=UTC))
        pause.set_pause(redis, PIXIE_PAUSE_SCHLUESSEL,
                        datetime(2026, 10, 15, 8, 0, tzinfo=UTC))

        self.assertEqual("2026-10-14T08:00:00+00:00",
                         redis.get(PIXIE_PAUSE_SCHLUESSEL + pause.SINCE_SUFFIX))

    def test_set_on_legacy_switch_does_not_make_it_now(self) -> None:
        redis = _Redis()
        redis.set(PIXIE_PAUSE_SCHLUESSEL, "1")
        pause.set_pause(redis, PIXIE_PAUSE_SCHLUESSEL)

        self.assertIsNone(redis.get(PIXIE_PAUSE_SCHLUESSEL + pause.SINCE_SUFFIX))

    def test_unknown_key_is_rejected_loudly(self) -> None:
        redis = _Redis()
        with self.assertRaises(pause.PauseError):
            pause.set_pause(redis, "pixie:running:llm")
        with self.assertRaises(pause.PauseError):
            pause.clear_pause(redis, "pixie:running:llm")
        with self.assertRaises(pause.PauseError):
            pause.check_pauses(redis, ("pixie:running:llm",))
        self.assertFalse(redis.values)

    def test_endpoint_pause_remembers_and_resume_clears(self) -> None:
        for key, do_pause, do_resume in (
            (PIXIE_PAUSE_SCHLUESSEL, admin.pixie_pausieren, admin.pixie_fortsetzen),
            (PIXIE_AGENTEN_PAUSE_SCHLUESSEL,
             admin.pixie_agenten_pausieren, admin.pixie_agenten_fortsetzen),
            (PIXIE_DELIVERY_PAUSE_SCHLUESSEL,
             admin.pixie_delivery_pausieren, admin.pixie_delivery_fortsetzen),
        ):
            with self.subTest(key=key):
                redis = _Redis()
                with patch.object(admin, "redis_client", redis):
                    do_pause()
                    self.assertEqual("1", redis.get(key))
                    self.assertIsNotNone(redis.get(key + pause.SINCE_SUFFIX))
                    redis.set(key + pause.WARNING_SUFFIX, "1", ex=900)

                    do_resume()
                self.assertFalse(redis.values, f"Es blieb stehen: {redis.values}")

    def test_after_resume_the_next_switch_starts_with_a_fresh_throttle(self) -> None:
        redis = _Redis()
        with patch.object(admin, "redis_client", redis):
            admin.pixie_pausieren()
            with self.assertLogs(LOGGER, level="DEBUG") as first:
                _heartbeat(redis)
            admin.pixie_fortsetzen()
            admin.pixie_pausieren()
            with self.assertLogs(LOGGER, level="DEBUG") as second:
                _heartbeat(redis)

        self.assertEqual(1, len(_warnings(first)))
        self.assertEqual(1, len(_warnings(second)))


if __name__ == "__main__":
    unittest.main()
