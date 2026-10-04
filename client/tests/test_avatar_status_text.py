"""Zeugen des Textes der Phasenanzeige: Richtung, Zahlen, Zeilen, Band und Takt.

Ohne GTK: geprüft wird `avatar.status_text`; das Panel ruft nur diese Funktionen.
"""

import dataclasses
import math
import unittest

from avatar.idle_catalog import IdleState
from avatar.idle_status import (
    NOTE_AFTERGLOW,
    NOTE_INHALING,
    NOTE_PLAYBACK,
    NOTE_WAITING,
    SOURCE_NOVA,
    SOURCE_PIXIE,
    BandItem,
    IdleStatus,
    StatusForm,
    StatusNext,
    StatusSpan,
)
from avatar.status_text import (
    band_segments,
    direction_text,
    fmt,
    status_due,
    status_lines,
)


def _status(**changes: object) -> IdleStatus:
    """Ein Status im Nachdenken zu F3 mit vier Formen; `changes` ersetzt Felder."""
    band = (BandItem("F3", 4.2), BandItem("F14", 3.6), BandItem("F5", 3.5), BandItem("F9", 3.9))
    base = IdleStatus(
        state=IdleState.THINKING, since_ms=0.0, elapsed_s=12.4, note=NOTE_WAITING, note_s=None,
        note_total_s=None, source=SOURCE_NOVA, sector_name="Freude", arousal=0.5,
        form=StatusForm("F3", "Vorstellen", 3.8, 4.2, 0.3, -0.4),
        next_form=StatusNext("F14", "Mund offen", 0.4), band=band, position=0,
        plan_kind="cycle", span=StatusSpan(3.9, 2.5, 5.3, 4))
    return dataclasses.replace(base, **changes)


class DirectionTest(unittest.TestCase):
    """Die Richtung nach `richtungText`, an den Grenzen mit Zwilling auf der anderen Seite."""

    def test_side_begins_above_0_12(self) -> None:
        self.assertEqual(direction_text(0.12, 0.0), "zum Betrachter")
        self.assertEqual(direction_text(0.121, 0.0), "seitlich")
        self.assertEqual(direction_text(-0.121, 0.0), "seitlich")
        self.assertEqual(direction_text(-0.12, 0.0), "zum Betrachter")

    def test_up_and_down_begin_beyond_0_15(self) -> None:
        self.assertEqual(direction_text(0.0, -0.15), "zum Betrachter")
        self.assertEqual(direction_text(0.0, -0.151), "oben")
        self.assertEqual(direction_text(0.0, 0.15), "zum Betrachter")
        self.assertEqual(direction_text(0.0, 0.151), "unten")

    def test_both_axes_join(self) -> None:
        self.assertEqual(direction_text(0.5, -0.5), "oben-seitlich")
        self.assertEqual(direction_text(-0.5, 0.5), "unten-seitlich")

    def test_the_viewer_at_the_centre(self) -> None:
        self.assertEqual(direction_text(0.0, 0.0), "zum Betrachter")

    def test_a_gaze_not_finite_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            direction_text(math.nan, 0.0)


class NumberTest(unittest.TestCase):
    """Zahlen mit Komma, nicht endliche als Strich."""

    def test_comma_instead_of_point(self) -> None:
        self.assertEqual(fmt(3.84), "3,8")
        self.assertEqual(fmt(0.5, 2), "0,50")
        self.assertEqual(fmt(11.6, 0), "12")

    def test_not_finite_is_a_dash(self) -> None:
        self.assertEqual(fmt(math.inf), "–")
        self.assertEqual(fmt(math.nan, 2), "–")

    def test_no_number_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            fmt("3,8")  # type: ignore[arg-type]

    def test_no_line_carries_a_decimal_point(self) -> None:
        lines = status_lines(_status())
        for text in (lines.state, lines.progress, lines.span):
            self.assertNotRegex(text, r"\d\.\d")


class LineTest(unittest.TestCase):
    """Die Zeile zum Zustand je Zustand, dazu die Zeilen der Form und der Spanne."""

    def test_thinking_waits(self) -> None:
        self.assertEqual(
            status_lines(_status()).state,
            "Nachdenken · seit 12 s · wartet auf die Antwort"
            " · Emotion: Nova — Freude, Arousal 0,50")

    def test_thinking_inhales(self) -> None:
        line = status_lines(_status(note=NOTE_INHALING, note_s=0.8)).state
        self.assertIn(" · atmet ein, spricht in 0,8 s · ", line)
        self.assertNotIn("wartet", line)

    def test_answer_plays_back(self) -> None:
        line = status_lines(_status(state=IdleState.ANSWER, note=NOTE_PLAYBACK, note_s=1.27)).state
        self.assertTrue(line.startswith("Antwort · seit 12 s · Wiedergabe, noch 1,3 s"), line)

    def test_afterglow_returns_to_noise(self) -> None:
        status = _status(state=IdleState.AFTERGLOW, note=NOTE_AFTERGLOW, note_s=4.4,
                         note_total_s=9.0)
        self.assertIn(" · zurück ins Rauschen in 4 s (Dauer 9 s) · ", status_lines(status).state)

    def test_noise_has_no_note_and_names_pixie(self) -> None:
        status = _status(state=IdleState.NOISE, note=None, source=SOURCE_PIXIE,
                         sector_name="Neutral", arousal=0.0)
        self.assertEqual(status_lines(status).state,
                         "Rauschen · seit 12 s · Emotion: Pixie — Neutral, Arousal 0,00")

    def test_a_note_without_seconds_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            status_lines(_status(note=NOTE_PLAYBACK, note_s=None))

    def test_the_form_line_and_progress_line_follow_the_generator(self) -> None:
        lines = status_lines(_status())
        self.assertEqual(lines.form, "F3 Vorstellen")
        self.assertEqual(
            lines.progress,
            "steht 3,8 von 4,2 s · Blick oben-seitlich · nächste: F14 Mund offen in 0,4 s")

    def test_the_last_form_announces_a_new_cycle(self) -> None:
        status = _status(next_form=None)
        self.assertIn("nächste: neuer Zyklus in 0,4 s", status_lines(status).progress)

    def test_a_cycle_shows_its_span_and_the_drawn_durations(self) -> None:
        self.assertEqual(
            status_lines(_status()).span,
            "x_c 3,9 s · Spanne 2,5–5,3 s · n 4 · gezogen: F3 4,2 · F14 3,6 · F5 3,5 · F9 3,9")

    def test_an_answer_plan_shows_its_kind_instead_of_a_span(self) -> None:
        status = _status(plan_kind="answer", span=None)
        self.assertEqual(status_lines(status).span,
                         "Antwort: Wechsel nach Sprecherregel · 4 Aktionen")

    def test_a_plan_of_unknown_kind_without_span_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            status_lines(_status(plan_kind="unbekannt", span=None))

    def test_no_status_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            status_lines(None)  # type: ignore[arg-type]


class BandTest(unittest.TestCase):
    """Die Anteile ergeben 1, genau eine Form läuft."""

    def test_shares_sum_to_one_and_one_form_runs(self) -> None:
        for position in range(4):
            with self.subTest(position=position):
                segments = band_segments(_status(position=position, form=StatusForm(
                    ("F3", "F14", "F5", "F9")[position], "x", 0.0, 1.0, 0.0, 0.0)))
                self.assertAlmostEqual(sum(s.share for s in segments), 1.0, places=9)
                self.assertEqual([s.running for s in segments].count(True), 1)
                self.assertTrue(segments[position].running)

    def test_the_width_follows_the_duration(self) -> None:
        segments = band_segments(_status())
        self.assertAlmostEqual(segments[0].share, 4.2 / 15.2)
        self.assertGreater(segments[0].share, segments[2].share)
        self.assertEqual([s.form_id for s in segments], ["F3", "F14", "F5", "F9"])

    def test_a_band_without_duration_is_refused(self) -> None:
        status = _status(band=(BandItem("F3", 0.0),), position=0)
        with self.assertRaises(ValueError):
            band_segments(status)


class RhythmTest(unittest.TestCase):
    """Die Anzeige zieht höchstens alle 120 ms nach."""

    def _updates(self, times: list[float]) -> int:
        last = None
        count = 0
        for now in times:
            if status_due(last, now):
                last = now
                count += 1
        return count

    def test_two_frames_50_ms_apart_update_once(self) -> None:
        self.assertEqual(self._updates([10.0, 10.05]), 1)

    def test_two_frames_130_ms_apart_update_twice(self) -> None:
        self.assertEqual(self._updates([10.0, 10.13]), 2)

    def test_the_first_frame_always_updates(self) -> None:
        self.assertTrue(status_due(None, 0.0))

    def test_a_steady_clock_updates_every_120_ms_not_every_frame(self) -> None:
        times = [i * 0.016 for i in range(126)]  # rund 2 s bei 62,5 Bildern/s
        updates = self._updates(times)
        self.assertGreater(updates, 10)
        self.assertLess(updates, 20)

    def test_time_before_the_last_update_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            status_due(5.0, 4.0)

    def test_time_not_finite_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            status_due(None, math.inf)


if __name__ == "__main__":
    unittest.main()
