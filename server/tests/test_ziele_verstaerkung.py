"""Zeugen fuer die Verstaerkung mittelfristiger Ziele bei Begegnung.

**Konzept:** `docs/novaberg-thinking-drive_k.md` §3.2 (*Verfall verstaerkt durch
wiederholte Begegnung*) und §10.2. Zieht ein mittelfristiges Ziel einen Turn
ueber `GRAVITATIONS_SCHWELLE`, beginnt seine Vergessenskurve von vorn: Der
Ankerzeitpunkt wird jetzt, der Anker bleibt. Kurz- und langfristige Ziele und
Ziele unter der Schwelle bleiben, wie sie sind.

Die Zeugen laufen ohne Datenbank. Der Lader liefert Ziele aus einem
Speicher im Test, der Schreibweg ist ein Doppel, das denselben Speicher
beschreibt wie `ziel_motivation_anpassen` die Zeile — danach rechnet der echte
`ziele_live_bewerten` den Wert von jetzt. Durch die echte Gravitation laeuft
der Turn, nicht durch eine Nachbildung: Das Tor ist ihre Schwelle.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from ei.gravitation import ActivatedGoal
from graph.nodes import enricher as enricher_mod
from memory.ziele import ziele_live_bewerten

NOW = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)
ANCHOR = 0.8
TURN_EMBEDDING = [1.0, 0.0]
NEAR = [1.0, 0.0]
FAR = [0.0, 1.0]
# Kosinus 0,707 zum Turn: bei zehn Tagen (Live-Wert 0,488) Staerke 0,345 — unter dem Tor.
MID = [1.0, 1.0]
GOALS_LOGGER = "ki_server.memory.ziele"


def _goal(
    goal_id: int, horizon: str, embedding: list[float], days_old: float,
    anchor: float | None = ANCHOR,
) -> dict:
    """Baut eine Zeile der Tabelle `ziele`, deren Anker `days_old` Tage zurueckliegt."""
    anchor_at = NOW - timedelta(days=days_old) if anchor is not None else None
    return {
        "id": goal_id, "ziel_typ": horizon, "zielsatz": f"Ziel {goal_id}",
        "motivation": anchor, "emotion": "", "arousal": 0.5, "embedding": embedding,
        "erstellt_am": anchor_at, "thema": "", "motivation_basis": anchor,
        "motivation_basis_am": anchor_at,
    }


class _Setup(unittest.TestCase):
    """Ein Speicher statt der Tabelle `ziele`, ein Doppel statt des UPDATE."""

    def setUp(self) -> None:
        self.store: list[dict] = []
        self.write_calls: list[tuple] = []
        self.entries: list[dict] = []
        self.writer_result = True

        def writer(postgres_url: str, goal_id: int, new_motivation: float) -> bool:
            self.write_calls.append((goal_id, new_motivation))
            if not self.writer_result:
                return False
            for row in self.store:
                if row["id"] == goal_id:
                    row["motivation"] = new_motivation
                    row["motivation_basis"] = new_motivation
                    row["motivation_basis_am"] = NOW
            return True

        def loader(postgres_url: str, user_id: str, character_id: str) -> list[dict]:
            return ziele_live_bewerten([dict(z) for z in self.store], jetzt=NOW)

        def entry(**fields: object) -> None:
            self.entries.append(fields)

        for patcher in (
            patch("memory.ziele.ziel_motivation_anpassen", side_effect=writer),
            patch.object(enricher_mod, "ziele_aktive_laden", side_effect=loader),
            patch.object(enricher_mod, "log_berechnung", side_effect=entry),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def _turn(self) -> tuple:
        return enricher_mod._compute_ziele_und_gravitation(
            TURN_EMBEDDING, "postgresql://doppel", "mensch", "nova", spur=("t1", None),
        )

    def _live(self, goal_id: int) -> float:
        rows = [z for z in ziele_live_bewerten(self.store, jetzt=NOW) if z["id"] == goal_id]
        return rows[0]["motivation"]


class TheReinforcementTest(_Setup):
    """Ziel: aktiviert ein Turn ein mittelfristiges Ziel, beginnt seine Kurve neu."""

    def test_the_pulled_goal_restarts_at_the_anchor_the_other_keeps_fading(self) -> None:
        self.store = [
            _goal(1, "mittelfristig", NEAR, days_old=10),
            _goal(2, "mittelfristig", FAR, days_old=10),
        ]
        before = self._live(1)

        self._turn()

        self.assertAlmostEqual(before, ANCHOR * 2 ** (-10 / 14), places=6)
        self.assertAlmostEqual(self._live(1), ANCHOR, places=6)
        self.assertAlmostEqual(self._live(2), ANCHOR * 2 ** (-10 / 14), places=6)

    def test_the_anchor_stays_and_is_not_raised(self) -> None:
        self.store = [_goal(1, "mittelfristig", NEAR, days_old=10, anchor=0.7)]

        self._turn()

        self.assertEqual(self.write_calls, [(1, 0.7)])
        self.assertEqual(self.store[0]["motivation_basis"], 0.7)

    def test_this_turn_computes_with_the_value_from_before_the_write(self) -> None:
        self.store = [_goal(1, "mittelfristig", NEAR, days_old=10)]

        activated, _, _ = self._turn()

        self.assertAlmostEqual(activated[0].motivation, ANCHOR * 2 ** (-10 / 14), places=6)

    def test_a_goal_is_written_at_most_once_per_turn(self) -> None:
        self.store = [_goal(1, "mittelfristig", NEAR, days_old=10)]

        self._turn()

        self.assertEqual(len(self.write_calls), 1)


class TheCounterCasesTest(_Setup):
    """Negativ-Zusicherungen; der positive Zwilling steht in `TheReinforcementTest`."""

    def test_a_medium_term_goal_below_the_threshold_is_not_written(self) -> None:
        # Prueft die Gravitation: Das lebende Ziel (Live-Wert 0,488) steht in der geladenen
        # Liste, aber die Aehnlichkeit 0,707 drueckt die Staerke auf 0,345 < 0,40, es wird nicht
        # aktiviert. Der Schreibweg wird dabei nicht erreicht (keine Aktivierung, frueher
        # Ruecklauf); die Schwellenpruefung des Schreibwegs bezeugen die drei Zeugen mit einem
        # gezogenen und einem nicht gezogenen Ziel nebeneinander.
        self.store = [_goal(1, "mittelfristig", MID, days_old=10)]

        activated, _, _ = self._turn()

        self.assertEqual(activated, [])
        self.assertEqual(self.write_calls, [])

    def test_a_short_term_goal_above_the_threshold_is_not_written(self) -> None:
        self.store = [_goal(1, "kurzfristig", NEAR, days_old=1 / 24)]

        activated, _, _ = self._turn()

        self.assertEqual([g.ziel_id for g in activated], [1])
        self.assertGreaterEqual(activated[0].aktivierungs_staerke, 0.4)
        self.assertEqual(self.write_calls, [])

    def test_a_long_term_goal_above_the_threshold_is_not_written(self) -> None:
        self.store = [_goal(1, "langfristig", NEAR, days_old=300)]

        activated, _, _ = self._turn()

        self.assertEqual([g.ziel_id for g in activated], [1])
        self.assertEqual(self.write_calls, [])

    def test_all_three_counter_cases_beside_a_pulled_goal_write_exactly_one(self) -> None:
        self.store = [
            _goal(1, "mittelfristig", NEAR, days_old=10),
            _goal(2, "mittelfristig", MID, days_old=10),
            _goal(3, "kurzfristig", NEAR, days_old=1 / 24),
            _goal(4, "langfristig", NEAR, days_old=300),
        ]

        self._turn()

        self.assertEqual([call[0] for call in self.write_calls], [1])


class TheEntryPerTurnTest(_Setup):
    """Die Nachmessung zaehlt aus dem Eintrag, sie raet den Bestand nicht."""

    def test_the_entry_names_exactly_the_reinforced_goals_with_the_old_anchor_time(self) -> None:
        self.store = [
            _goal(1, "mittelfristig", NEAR, days_old=10),
            _goal(2, "mittelfristig", FAR, days_old=10),
            _goal(3, "langfristig", NEAR, days_old=300),
        ]
        old_anchor_at = self.store[0]["motivation_basis_am"].isoformat()

        self._turn()

        self.assertEqual(len(self.entries), 1)
        entry = self.entries[0]
        self.assertEqual(entry["turn_id"], "t1")
        self.assertEqual(entry["quelle"], "ziele_verstaerkung")
        self.assertEqual(
            entry["inhalt"]["verstaerkt"],
            [{"ziel_id": 1, "anker": ANCHOR, "anker_am_alt": old_anchor_at}],
        )

    def test_a_turn_without_reinforcement_writes_no_entry(self) -> None:
        self.store = [_goal(1, "mittelfristig", FAR, days_old=10)]

        self._turn()

        self.assertEqual(self.entries, [])


class TheTurnDoesNotTearTest(_Setup):
    """Ein Fehler des Schreibwegs wird gemeldet, der Turn laeuft weiter."""

    def test_a_failed_write_is_loud_and_named_in_the_entry(self) -> None:
        self.store = [_goal(1, "mittelfristig", NEAR, days_old=10)]
        self.writer_result = False

        with self.assertLogs(GOALS_LOGGER, level="ERROR") as logged:
            activated, _, _ = self._turn()

        self.assertEqual(len(activated), 1)
        self.assertIn("Schreibvorgang gescheitert", "\n".join(logged.output))
        self.assertEqual(self.entries[0]["inhalt"]["fehlgeschlagen"], [1])
        self.assertEqual(self.entries[0]["inhalt"]["verstaerkt"], [])

    def test_an_exception_in_the_write_path_does_not_tear_the_turn(self) -> None:
        self.store = [_goal(1, "mittelfristig", NEAR, days_old=10)]

        with patch("memory.ziele.ziel_motivation_anpassen", side_effect=RuntimeError("weg")), \
             self.assertLogs("ki_server.enricher", level="ERROR") as logged:
            activated, _, _ = self._turn()

        self.assertEqual(len(activated), 1)
        self.assertIn("Ziele verstaerken fehlgeschlagen", "\n".join(logged.output))

    def test_a_goal_without_anchor_is_skipped_loudly(self) -> None:
        # Ohne Anker gilt der materialisierte Wert (Warnung des Laders); das Ziel zieht trotzdem.
        row = _goal(1, "mittelfristig", NEAR, days_old=0, anchor=None)
        row["motivation"] = 0.9
        self.store = [row]

        with self.assertLogs(GOALS_LOGGER, level="ERROR") as logged:
            self._turn()

        self.assertIn("ohne Anker", "\n".join(logged.output))
        self.assertEqual(self.write_calls, [])
        self.assertEqual(self.entries[0]["inhalt"]["ohne_anker"], [1])


class TheCountPerHorizonTest(unittest.TestCase):
    """`aktivierte_ziele_count` mischt zwei Tore; die Trennung macht ihn lesbar."""

    def _pulled(self, horizon: str, strength: float) -> ActivatedGoal:
        return ActivatedGoal(
            ziel_id=1, ziel_typ=horizon, zielsatz="x", motivation=0.5, emotion="",
            arousal=0.5, similarity=0.5, aktivierungs_staerke=strength,
        )

    def test_a_short_term_goal_below_the_threshold_counts_activated_but_not_above(self) -> None:
        report = enricher_mod._aktivierungen_je_horizont([
            self._pulled("kurzfristig", 0.2),
            self._pulled("mittelfristig", 0.5),
            self._pulled("langfristig", 0.4),
        ])

        self.assertEqual(
            report["aktiviert_je_horizont"],
            {"langfristig": 1, "mittelfristig": 1, "kurzfristig": 1},
        )
        self.assertEqual(
            report["ueber_schwelle_je_horizont"],
            {"langfristig": 1, "mittelfristig": 1, "kurzfristig": 0},
        )

    def test_without_activation_all_horizons_stand_at_zero(self) -> None:
        report = enricher_mod._aktivierungen_je_horizont([])

        self.assertEqual(sum(report["aktiviert_je_horizont"].values()), 0)
        self.assertEqual(sum(report["ueber_schwelle_je_horizont"].values()), 0)


if __name__ == "__main__":
    unittest.main()
