"""Tests: Der Bezug reist mit der Zustimmung, und die Rueckfrage nimmt keinen fremden Auftrag an.

Beide Zeugen gehen auf dieselbe Betriebsmessung zurueck (17.09.2026):

  * **E1c** — Bei zwei akuten Sachen nahm die Klassifikation den Titel aus der
    einen und den Zeitpunkt aus keiner (*"Konnte kein Datum ermitteln"*). Stimmt
    der Mensch einem Angebot zu, reisen jetzt nur dessen Sachen zum Dienst.
  * **E1d** — Eine offene Rueckfrage der Notizen verschluckte den Auftrag
    *"Trag mir den Zahnarzt am Donnerstag um 15 Uhr ein"*, meldete
    `abgeschlossen` und schrieb nichts.

**Was diese Tests NICHT koennen:** ob das Modell mit dem geschnittenen Bezug
besser klassifiziert. Das misst die Reihe in labor/.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from graph.nodes import router
from graph.nodes.planner import _bezug_zuschneiden
from utils.offers import Offer, carries_own_request

ZAHNARZT = {"name": "Zahnarzttermin", "klasse": "vorgang", "gedeckt": {"Tag": "Donnerstag"}}
ABHOLUNG = {"name": "Abholung der Schwester", "klasse": "vorgang", "gedeckt": {"Tag": "Samstag"}}


class BezugZuschneidenTest(unittest.TestCase):

    def test_ohne_angebot_bleibt_der_bezug(self) -> None:
        self.assertEqual(_bezug_zuschneiden([ZAHNARZT, ABHOLUNG], []), [ZAHNARZT, ABHOLUNG])

    def test_mit_angebot_nur_dessen_sache(self) -> None:
        self.assertEqual(_bezug_zuschneiden([ZAHNARZT, ABHOLUNG], ["Abholung der Schwester"]), [ABHOLUNG])

    def test_gross_und_kleinschreibung_trennt_nicht(self) -> None:
        self.assertEqual(_bezug_zuschneiden([ZAHNARZT], ["  zahnarzttermin "]), [ZAHNARZT])

    def test_faende_der_schnitt_nichts_bleibt_der_volle_bezug(self) -> None:
        """Ohne Sachen im Angebot: ein leerer Bezug waere schlechter als ein breiter."""
        with self.assertLogs("ki_server.planner", level="WARNING"):
            self.assertEqual(_bezug_zuschneiden([ZAHNARZT], ["Einkaufsliste"]), [ZAHNARZT])

    def test_die_lage_ist_weitergezogen_dann_traegt_das_angebot(self) -> None:
        """Der gemessene Fall (17.09.2026): zwei Turns spaeter ist die Sache nicht mehr akut."""
        aus_dem_angebot = [{"name": "Abholung der Schwester", "klasse": "vorgang",
                            "gedeckt": {"Tag": "Samstag", "Uhrzeit": "10 Uhr"}}]
        self.assertEqual(_bezug_zuschneiden([], ["Abholung der Schwester"], aus_dem_angebot), aus_dem_angebot)
        self.assertEqual(_bezug_zuschneiden([ZAHNARZT], ["Abholung der Schwester"], aus_dem_angebot), aus_dem_angebot)


class EigenerAuftragTest(unittest.TestCase):

    def test_auftragsformen(self) -> None:
        for text in (
            "Trag mir den Zahnarzt am Donnerstag um 15 Uhr ein.",
            "Schreib Spuelmittel auf die Einkaufsliste.",
            "Notier dir die Reifengroesse.",
            "Merk dir das WLAN-Passwort.",
            "Erinnere mich am Samstag um 10.",
            "Verschieb den Termin auf Freitag.",
            "Leg eine Einkaufsliste an.",
        ):
            with self.subTest(text=text):
                self.assertTrue(carries_own_request(text))

    def test_eine_antwort_auf_eine_rueckfrage_ist_kein_auftrag(self) -> None:
        for text in ("Gerne", "Ja, bitte", "Die erste", "Nein, lass mal", "Die Einkaufsliste", ""):
            with self.subTest(text=text):
                self.assertFalse(carries_own_request(text))


class RueckfrageImEmpfangTest(unittest.TestCase):

    ANTWORT = {"needs_memory": False, "needs_web": False, "needs_timeline": False,
               "momentum": "mid", "management_action": "agent", "management_target": "timeline",
               "management_target_typ": "titel"}

    def _route(self, reiz: str, pending: dict | None) -> tuple[dict, list]:
        geloescht: list[str] = []
        state = {"user_id": "pruefer", "character_id": "nova", "turn_id": "t3",
                 "user_prompt": reiz, "event_payload": {}, "node_annotations": [],
                 "agent_results": [], "sachlage": {"herkunft": "fortgeschrieben", "objekte": []}}
        stell = SimpleNamespace(chat=SimpleNamespace(submit_sync=lambda request, timeout=None: SimpleNamespace(
            text=json.dumps(self.ANTWORT), token_total=0, thinking="", parsed=dict(self.ANTWORT))))
        with patch.object(router, "model_service", stell), \
             patch.object(router, "session_turns_retrieve", return_value=[]), \
             patch.object(router, "shadow_nearness", return_value={"ergebnis": "ohne_akute_objekte"}), \
             patch.object(router, "offer_load", return_value=None), \
             patch("tools.redis_manager.redis_manager.get_json", return_value=pending), \
             patch("tools.redis_manager.redis_manager.delete", side_effect=lambda k: geloescht.append(k)):
            return router.route(dict(state)), geloescht

    def test_eine_antwort_geht_an_den_wartenden_dienst(self) -> None:
        ergebnis, geloescht = self._route("Die erste", {"agent_name": "notizen"})
        self.assertEqual(ergebnis["management_action"], "resume")
        self.assertEqual(geloescht, [])

    def test_ein_eigener_auftrag_verwirft_die_rueckfrage(self) -> None:
        ergebnis, geloescht = self._route("Trag mir den Zahnarzt am Donnerstag um 15 Uhr ein.",
                                          {"agent_name": "notizen"})
        self.assertNotEqual(ergebnis["management_action"], "resume")
        self.assertEqual(geloescht, ["pending_agent:pruefer"])


class ZustimmungSetztDieSachenTest(unittest.TestCase):
    """Die Verdrahtung: Was der Router bei einer Zustimmung in den Zustand legt."""

    def _route(self, reiz: str, angebot: Offer | None) -> dict:
        state = {"user_id": "pruefer", "character_id": "nova", "turn_id": "t4",
                 "user_prompt": reiz, "event_payload": {}, "node_annotations": [],
                 "agent_results": [], "sachlage": {"herkunft": "fortgeschrieben", "objekte": []}}
        antwort = {"needs_memory": False, "needs_web": False, "needs_timeline": False,
                   "momentum": "mid", "management_action": "", "management_target": "",
                   "management_target_typ": "titel"}
        stell = SimpleNamespace(chat=SimpleNamespace(submit_sync=lambda request, timeout=None: SimpleNamespace(
            text=json.dumps(antwort), token_total=0, thinking="", parsed=dict(antwort))))
        with patch.object(router, "model_service", stell), \
             patch.object(router, "session_turns_retrieve", return_value=[]), \
             patch.object(router, "shadow_nearness", return_value={"ergebnis": "ohne_akute_objekte"}), \
             patch.object(router, "offer_load", return_value=angebot), \
             patch("tools.redis_manager.redis_manager.get_json", return_value=None):
            return router.route(dict(state))

    def test_zustimmung_traegt_die_sachen_des_angebots(self) -> None:
        angebot = Offer(sentence="Soll ich dir den Termin eintragen?",
                        objects=("Abholung der Schwester",), services=("timeline",),
                        turn_id="t3", time=1.0,
                        details=({"name": "Abholung der Schwester", "klasse": "vorgang",
                                  "gedeckt": {"Tag": "Samstag"}},))
        ergebnis = self._route("Gerne", angebot)
        self.assertEqual(ergebnis["angebot_objekte"], ["Abholung der Schwester"])
        self.assertEqual(ergebnis["angebot_bezug"], [{"name": "Abholung der Schwester", "klasse": "vorgang",
                                                      "gedeckt": {"Tag": "Samstag"}}])
        # Der Satz selbst reist mit: Die Fachabteilung liest, worauf zugestimmt wurde.
        self.assertEqual(ergebnis["angebot_satz"], "Soll ich dir den Termin eintragen?")

    def test_ohne_angebot_und_ohne_zustimmung_bleibt_es_leer(self) -> None:
        angebot = Offer(sentence="Soll ich dir den Termin eintragen?", objects=("Abholung der Schwester",),
                        services=("timeline",), turn_id="t3", time=1.0)
        self.assertEqual(self._route("Gerne", None)["angebot_objekte"], [])
        self.assertEqual(self._route("Gerne", None)["angebot_satz"], "")
        self.assertEqual(self._route("Und wie lange dauert das?", angebot)["angebot_objekte"], [])
        self.assertEqual(self._route("Und wie lange dauert das?", angebot)["angebot_satz"], "")


if __name__ == "__main__":
    unittest.main()
