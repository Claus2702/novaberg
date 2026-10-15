"""Zeugen: die volle Faszination des Turns rechnet den Strangzug je Traeger.

Ziel: Die Zeile `faszination` des Praegungsknotens nennt den Strangzug jedes
Traegers (§10.3a) und rechnet ihn mit; ein Traeger im Zentrum eines Strangs
steht ueber einem gleichen am Rand.

**Fehlerweg:** Wirft das Lesen der Strangnaehe, wird der Traeger neutral
(1.0) gerechnet, der Fehler geloggt, und die Zeile sagt, dass der Strangzug
*fehlte* — sie traegt `None`, nicht 1.0. Einen Fehler, den die Store-Funktion
selbst abfaengt (`{}`), sieht der Knoten nicht; er zaehlt als kein Strangbezug.

Diese Zeugen fassen die Datenbank nicht an: Beide Lesefunktionen sind ersetzt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

NODE: str = "graph.nodes.praegung"
LOGGER: str = "ki_server.praegung_node"


def _emotion() -> MagicMock:
    """Ein Emotionsobjekt mit den Feldern, die die Modulatoren lesen."""
    emotion = MagicMock()
    emotion.arousal = 0.5
    emotion.emotion = "neugierig"
    emotion.emotions_vector = "plateau"
    emotion.intent = "knowledge"
    emotion.mode = "alltag"
    return emotion


def _state(node_ids: list[int]) -> dict:
    """Ein Turn-Zustand mit gelesenen Erinnerungen."""
    external, internal = MagicMock(), MagicMock()
    external.emotion = _emotion()
    internal.emotion = _emotion()
    return {
        "turn_id": "t-1", "user_id": "meister", "character_id": "nova",
        "external": external, "internal": internal,
        "lzg_resonanz": {"erinnerungen": [{"knoten_id": k} for k in node_ids]},
    }


def _carrier() -> dict:
    """Ein Traegerdatensatz — fuer alle Traeger dieser Zeugen derselbe."""
    return {
        "tage": 3, "turns": 3, "eigenimpuls": 0.5,
        "profil": {"komplexitaet": 0.8, "weite": 0.4},
    }


def _run(proximity: dict | Exception, pull: float = 1.0) -> dict:
    """Fuehrt den Protokollierer fuer die Traeger 11 und 12 und gibt die Zeile zurueck.

    `proximity` ist das Ergebnis der ersetzten Strangnaehe oder eine Ausnahme.
    """
    stub = (
        {"return_value": proximity} if isinstance(proximity, dict)
        else {"side_effect": proximity}
    )
    with patch(f"{NODE}.log_berechnung") as written, \
         patch(f"{NODE}.traegerdaten_lesen",
               return_value={11: _carrier(), 12: _carrier()}), \
         patch(f"{NODE}.traeger_strangnaehe", **stub):
        from graph.nodes.praegung import _faszination_protokollieren

        _faszination_protokollieren(_state([11, 12]), "meister", "nova", pull)
    return written.call_args.kwargs["inhalt"]


CENTRE: dict = {11: {"strang_id": 1, "naehe": 0.9, "faden_zahl": 20, "valenz": None}}


class StrangzugInTurnComputedTest(unittest.TestCase):
    """Ein Traeger im Zentrum eines Strangs steht ueber einem am Rand."""

    def test_carrier_at_centre_ranks_above_one_without_strand(self) -> None:
        content = _run(CENTRE)
        self.assertGreater(content["rohe"]["11"], content["rohe"]["12"])

    def test_line_names_strangzug_per_carrier(self) -> None:
        from ei.fascination import strangzug

        content = _run(CENTRE)
        self.assertEqual(round(strangzug(0.9, 20), 4), content["strangzug"]["11"])
        self.assertGreater(content["strangzug"]["11"], 1.0)
        self.assertEqual(1.0, content["strangzug"]["12"])
        self.assertIsNone(content["strang_ausfall"])

    def test_twins_without_strand_stand_equal(self) -> None:
        """Zwilling zur ersten Abweisung: ohne Strang unterscheidet nichts."""
        content = _run({})
        self.assertEqual(content["rohe"]["11"], content["rohe"]["12"])
        self.assertEqual({"11": 1.0, "12": 1.0}, content["strangzug"])

    def test_raw_value_is_neutral_value_times_strangzug(self) -> None:
        """Nachrechenbar: roh mit Strang = roh ohne Strang x Strangzug."""
        with_strand = _run(CENTRE)
        without = _run({})
        self.assertAlmostEqual(
            without["rohe"]["11"] * with_strand["strangzug"]["11"],
            with_strand["rohe"]["11"],
            delta=0.001,
        )

    def test_proximity_is_asked_for_all_read_carriers(self) -> None:
        with patch(f"{NODE}.log_berechnung"), \
             patch(f"{NODE}.traegerdaten_lesen",
                   return_value={11: _carrier(), 12: _carrier()}), \
             patch(f"{NODE}.traeger_strangnaehe", return_value={}) as read:
            from graph.nodes.praegung import _faszination_protokollieren

            _faszination_protokollieren(_state([11, 12]), "meister", "nova", 1.0)
        self.assertEqual([11, 12], read.call_args.args[1])


class FailureIsStatedTest(unittest.TestCase):
    """Neutral gerechnet, aber nicht als 1.0 ausgegeben."""

    def test_unreadable_means_none_and_names_the_error(self) -> None:
        with self.assertLogs(LOGGER, level="ERROR"):
            content = _run(RuntimeError("Verbindung weg"))
        self.assertEqual({"11": None, "12": None}, content["strangzug"])
        self.assertEqual("RuntimeError", content["strang_ausfall"])

    def test_unreadable_keeps_computing_neutral(self) -> None:
        """Der Ausfall loescht keinen Traeger: Werte wie ohne Strangbezug."""
        neutral = _run({})
        with self.assertLogs(LOGGER, level="ERROR"):
            failed = _run(RuntimeError("Verbindung weg"))
        self.assertEqual(neutral["rohe"], failed["rohe"])
        self.assertEqual(neutral["werte"], failed["werte"])
        self.assertEqual(2, len(failed["werte"]))

    def test_readable_reports_no_failure_and_no_error(self) -> None:
        """Zwilling: ohne Ausnahme kein ERROR im Log."""
        with self.assertNoLogs(LOGGER, level="ERROR"):
            content = _run(CENTRE)
        self.assertIsNone(content["strang_ausfall"])


class AnlageStaysOpenTest(unittest.TestCase):
    """`f_anlage` ist bewusst halbseitig — dieser Bau schliesst die Schleife nicht."""

    def test_wissbegier_stays_none(self) -> None:
        from ei.fascination import modulatoren_aus_turn

        with patch(f"{NODE}.modulatoren_aus_turn",
                   wraps=modulatoren_aus_turn) as called:
            _run(CENTRE)
        self.assertIsNone(called.call_args.kwargs["wissbegier"])


if __name__ == "__main__":
    unittest.main()
