"""Tests: Der Zugriffsknoten wendet den Verfall an — und der Impuls loest keinen aus.

Die Kurve fuer sich ist in `test_eigenzeit_verfall.py` geprueft. Hier steht der
Zeuge an der Schicht, die **handelt**: `_zustand_verfallen` in
`graph/nodes/db_zugriff.py`. Ein Zeuge eine Schicht darueber koennte nicht rot
werden.

Die scharfe Zusicherung ist die dritte: **Auf einem Impuls-Turn findet kein
Verfall statt.** Liefe die Uhr auf jedem Turn, setzte der stuendliche Impuls
sie zurueck und die Nacht waere nie eine Pause — dann traefe der Morgen
dieselbe aufgedrehte Nova wie bisher, obwohl der ganze Bauteil gebaut ist.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import time
import unittest
from unittest.mock import MagicMock, patch

from config import EIGENZEIT_AROUSAL_RUHE
from graph.nodes import db_zugriff as db_zugriff_modul
from graph.nodes.db_zugriff import Protokollkopf, _zustand_verfallen
from graph.personality import Emotion

STUNDE: float = 3600.0


def _kopf() -> Protokollkopf:
    """Ein Protokollkopf fuer das produktive Paar."""
    return Protokollkopf(
        turn_id      = "zeuge-eigenzeit",
        quelle       = "character",
        span_id      = "",
        user_id      = "meister",
        character_id = "nova",
    )


def _zustand() -> Emotion:
    """Eine aufgedrehte Nova, wie sie eine Nacht ueberdauert."""
    return Emotion(
        emotion            = "begeistert",
        arousal            = 0.95,
        mode               = "fachgespraech",
        language_style     = "poetisch",
        tone               = "warm",
        relationship_dynamic = "vertraut",
    )


def _hash(pause_stunden: float | None) -> dict:
    """Der nova_state-Hash mit einer Nutzeraeusserung vor `pause_stunden`."""
    if pause_stunden is None:
        return {}
    return {"nutzer_zeit": str(time.time() - pause_stunden * STUNDE)}


class DerVerfallImZugriffTest(unittest.TestCase):
    """Was der Knoten mit dem geladenen Zustand macht."""

    def test_kurze_pause_laesst_alles_stehen(self) -> None:
        """Wer zehn Minuten weg war, findet dieselbe Person wieder.

        „Dieselbe Person" heisst wiedererkennbar, nicht bitgleich: Die
        Kategorien stehen unveraendert, und die Erregung bewegt sich um
        weniger als ein Fuenfzigstel des Wertebereichs. Gemessen sind es
        0,0075 — die Kurve ist in der ersten Stunde absichtlich flach.
        """
        ergebnis = _zustand_verfallen(_kopf(), _zustand(), _hash(1 / 6), "nutzer_turn")

        self.assertLess(abs(0.95 - ergebnis.arousal), 0.02)
        self.assertEqual("fachgespraech", ergebnis.mode)
        self.assertEqual("begeistert",    ergebnis.emotion)

    def test_lange_pause_senkt_und_laesst_springen(self) -> None:
        """Nach vier Stunden: Erregung in der Ruhelage, Kategorien neutral."""
        ergebnis = _zustand_verfallen(_kopf(), _zustand(), _hash(4.0), "nutzer_turn")

        self.assertAlmostEqual(EIGENZEIT_AROUSAL_RUHE, ergebnis.arousal, places=4)
        self.assertEqual("alltag",   ergebnis.mode)
        self.assertEqual("neutral",  ergebnis.emotion)
        self.assertEqual("neutral",  ergebnis.language_style)
        self.assertEqual("sachlich", ergebnis.tone)

    def test_der_impuls_ist_keine_pause(self) -> None:
        """Die Bedingung, an der der Bauteil scheitert, wenn man sie uebersieht."""
        ergebnis = _zustand_verfallen(
            _kopf(), _zustand(), _hash(4.0), "eigener_impuls",
        )

        self.assertAlmostEqual(0.95, ergebnis.arousal, places=2)
        self.assertEqual("fachgespraech", ergebnis.mode)

    def test_die_bindende_spalte_bleibt(self) -> None:
        """Naehe traegt die Bindung, nicht die Energie — sie faellt nicht mit."""
        ergebnis = _zustand_verfallen(_kopf(), _zustand(), _hash(4.0), "nutzer_turn")

        self.assertEqual("vertraut", ergebnis.relationship_dynamic)

    def test_ohne_zeitstempel_wird_nicht_gedaempft(self) -> None:
        """Ein fehlender Wert ist unbekannt und keine Pause von null."""
        ergebnis = _zustand_verfallen(_kopf(), _zustand(), _hash(None), "nutzer_turn")

        self.assertAlmostEqual(0.95, ergebnis.arousal, places=2)
        self.assertEqual("fachgespraech", ergebnis.mode)

    def test_unlesbarer_zeitstempel_meldet_sich_und_daempft_nicht(self) -> None:
        """Kaputt ist nicht dasselbe wie frisch — und es wird laut."""
        with self.assertLogs("ki_server.db_zugriff", level="ERROR") as protokoll:
            ergebnis = _zustand_verfallen(
                _kopf(), _zustand(), {"nutzer_zeit": "vorgestern"}, "nutzer_turn",
            )

        self.assertAlmostEqual(0.95, ergebnis.arousal, places=2)
        self.assertIn("nutzer_zeit", "\n".join(protokoll.output))


class DieVerdrahtungTest(unittest.TestCase):
    """Der Ladepfad ruft den Verfall — sonst ist der Bauteil tot und still.

    Dieser Zeuge existiert wegen einer **gruenen** Gegenprobe: Am 15.08.2026
    wurde der Aufruf in `_nova_zustand_laden` testweise ausgeklinkt, und alle
    1363 Tests blieben gruen. Die Zusicherungen darueber pruefen
    `_zustand_verfallen` direkt und haetten den toten Bauteil nie bemerkt.
    """

    def test_der_ladepfad_wendet_den_verfall_an(self) -> None:
        """Vier Stunden Pause im Hash, gesenkter Zustand am Ausgang."""
        hash_mit_pause: dict = {
            "emotion":        "begeistert",
            "arousal":        "0.95",
            "mode":           "fachgespraech",
            "language_style": "poetisch",
            "tone":           "warm",
            "nutzer_zeit":    str(time.time() - 4 * STUNDE),
        }
        redis_mock = MagicMock()
        redis_mock.hgetall.return_value = hash_mit_pause

        with patch.object(db_zugriff_modul, "redis_client", redis_mock):
            emotion, _raum = db_zugriff_modul._nova_zustand_laden(
                _kopf(), "nutzer_turn",
            )

        self.assertAlmostEqual(EIGENZEIT_AROUSAL_RUHE, emotion.arousal, places=4)
        self.assertEqual("alltag", emotion.mode)

    def test_der_ladepfad_laesst_den_impuls_in_ruhe(self) -> None:
        """Der positive Zwilling: derselbe Hash, andere Herkunft, kein Verfall."""
        hash_mit_pause: dict = {
            "emotion":     "begeistert",
            "arousal":     "0.95",
            "mode":        "fachgespraech",
            "nutzer_zeit": str(time.time() - 4 * STUNDE),
        }
        redis_mock = MagicMock()
        redis_mock.hgetall.return_value = hash_mit_pause

        with patch.object(db_zugriff_modul, "redis_client", redis_mock):
            emotion, _raum = db_zugriff_modul._nova_zustand_laden(
                _kopf(), "eigener_impuls",
            )

        self.assertAlmostEqual(0.95, emotion.arousal, places=2)
        self.assertEqual("fachgespraech", emotion.mode)


if __name__ == "__main__":
    unittest.main()
