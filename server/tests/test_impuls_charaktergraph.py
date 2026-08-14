"""Tests fuer den Weg eines Pixie-Impulses in den CharacterGraph.

Ziel: Ein Pixie-Impuls durchlaeuft denselben Weg wie eine Nutzer-Eingabe —
das Wissensstueck ist der Reiz, Nova reagiert im CharacterGraph, und der Turn
ist ueber `verbindung` bis zum Rohturn aufloesbar.

Geprueft wird hier das Feuern des Events: Form, Inhalt und Fehlerverhalten.
Dass der CharacterGraph daraus einen vollstaendigen Rohturn macht, belegt der
Live-Lauf, nicht diese Datei — dafuer muesste der ganze Graph laufen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from config import ASSISTANT_USER_ID
from services.shadow_delivery import _impuls_in_den_charaktergraph

DELIVERY_LOGGER: str = "ki_server.shadow_delivery"

WISSEN: str = (
    "Hainbuchen bilden ein dichtes Wurzelgeflecht, das verdichteten Boden "
    "ueber Jahre wieder durchlaessig macht."
)
EINTRAG: dict = {
    "thema":       "Bodenverdichtung, Hainbuche",
    "aufgabe":     "recherche",
    "inhalt":      WISSEN,
    "emotion":     "neugierig",
    "modus":       "fachgespraech",
    "intentionen": ["information_teilen"],
}


class ImpulsInDenCharaktergraphTest(unittest.TestCase):
    """Das Event ist der Uebergang vom entstehenden zum gedachten Gedanken."""

    def setUp(self) -> None:
        self.redis = MagicMock()

    def _feuern(self, turn_id: str = "t-impuls-1", wissen: str = WISSEN):
        """Ruft die Funktion mit abgefangenem event_erzeugen auf."""
        with patch(
            "services.shadow_delivery.event_erzeugen", return_value="ev-1",
        ) as ruf:
            erfolg: bool = _impuls_in_den_charaktergraph(
                self.redis, "meister", turn_id, wissen, EINTRAG,
            )
        return erfolg, ruf

    # ── Form und Inhalt des Events ───────────────────

    def test_event_traegt_das_wissensstueck_als_reiz(self):
        erfolg, ruf = self._feuern()
        self.assertTrue(erfolg)
        self.assertEqual(ruf.call_count, 1)

        kwargs = ruf.call_args.kwargs
        self.assertEqual(kwargs["source"], "character")
        self.assertEqual(kwargs["typ"], "message")
        self.assertEqual(kwargs["character_id"], ASSISTANT_USER_ID)

        payload: dict = kwargs["payload"]
        self.assertEqual(payload["eigener_gedanke"], WISSEN)
        self.assertEqual(payload["turn_id"], "t-impuls-1")

    def test_der_reiz_platz_bleibt_leer(self) -> None:
        """Was dort staende, waere eine Aeusserung des Menschen — es gab keine.

        Der Schluessel fehlt ganz statt leer dazustehen: Ein leeres Feld
        traegt dieselbe Aussage und laedt zugleich dazu ein, es spaeter wieder
        zu befuellen.
        """
        _, ruf = self._feuern()
        self.assertNotIn("user_prompt", ruf.call_args.kwargs["payload"])

    def test_event_traegt_die_emotion_des_stack_eintrags(self):
        """Pixies Zustand beim Recherchieren ist die Reiz-Haelfte des Paares."""
        _, ruf = self._feuern()
        payload: dict = ruf.call_args.kwargs["payload"]
        self.assertEqual(payload["current_emotion"], "neugierig")
        self.assertEqual(payload["gespraechs_modus"], "fachgespraech")
        self.assertEqual(payload["prompt_thema"], "Bodenverdichtung, Hainbuche")

    def test_keine_erfundenen_ei_dimensionen(self):
        """Was der Stack-Eintrag nicht hat, wird nicht plausibel aufgefuellt."""
        _, ruf = self._feuern()
        payload: dict = ruf.call_args.kwargs["payload"]
        for feld in ("current_arousal", "tone", "sprach_stil",
                     "beziehungs_dynamik", "emotions_vektor"):
            self.assertNotIn(feld, payload)

    def test_das_event_ist_serialisierbar(self):
        """Es geht als JSON in die Redis-Queue — ein Objekt darin braeche sie."""
        _, ruf = self._feuern()
        json.dumps(ruf.call_args.kwargs["payload"], ensure_ascii=False)

    # ── Fehlerpfade ──────────────────────────────────

    def test_ohne_turn_id_kein_event_und_ein_error(self):
        with self.assertLogs(DELIVERY_LOGGER, level="ERROR") as log:
            with patch("services.shadow_delivery.event_erzeugen") as ruf:
                erfolg: bool = _impuls_in_den_charaktergraph(
                    self.redis, "meister", "", WISSEN, EINTRAG,
                )
        self.assertFalse(erfolg)
        self.assertEqual(ruf.call_count, 0)
        self.assertEqual(len(log.records), 1)
        self.assertIn("ohne turn_id", log.records[0].getMessage())

    def test_ohne_inhalt_kein_event_und_ein_error(self):
        with self.assertLogs(DELIVERY_LOGGER, level="ERROR") as log:
            with patch("services.shadow_delivery.event_erzeugen") as ruf:
                erfolg: bool = _impuls_in_den_charaktergraph(
                    self.redis, "meister", "t-impuls-2", "", EINTRAG,
                )
        self.assertFalse(erfolg)
        self.assertEqual(ruf.call_count, 0)
        self.assertEqual(len(log.records), 1)

    def test_redis_fehler_loggt_genau_einen_error_und_wirft_nicht(self):
        with patch(
            "services.shadow_delivery.event_erzeugen",
            side_effect=ConnectionError("Redis weg"),
        ):
            with self.assertLogs(DELIVERY_LOGGER, level="ERROR") as log:
                erfolg: bool = _impuls_in_den_charaktergraph(
                    self.redis, "meister", "t-impuls-3", WISSEN, EINTRAG,
                )
        self.assertFalse(erfolg)
        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, "ERROR")
        self.assertIn("Event fuer den CharacterGraph fehlgeschlagen",
                      log.records[0].getMessage())

    def test_leere_event_id_gilt_als_fehlschlag(self):
        """event_erzeugen ohne ID heisst: nichts liegt in der Queue."""
        with patch("services.shadow_delivery.event_erzeugen", return_value=""):
            with self.assertLogs(DELIVERY_LOGGER, level="ERROR") as log:
                erfolg: bool = _impuls_in_den_charaktergraph(
                    self.redis, "meister", "t-impuls-4", WISSEN, EINTRAG,
                )
        self.assertFalse(erfolg)
        self.assertEqual(len(log.records), 1)
        self.assertIn("keine event_id", log.records[0].getMessage())

    # ── Erfolgsmeldung ───────────────────────────────

    def test_erfolg_nennt_turn_id_und_event_id(self):
        with self.assertLogs(DELIVERY_LOGGER, level="INFO") as log:
            self._feuern(turn_id="t-impuls-5")
        meldungen = [r.getMessage() for r in log.records]
        self.assertTrue(any("turn_id=t-impuls-5" in m for m in meldungen), meldungen)
        self.assertTrue(any("event_id=ev-1" in m for m in meldungen), meldungen)


if __name__ == "__main__":
    unittest.main()
