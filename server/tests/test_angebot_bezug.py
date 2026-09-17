"""Tests: Eine Zustimmung ist nur dann ein Auftrag, wenn ein Angebot offen ist (Scheibe 12 E1).

Anlass `[gemessen 17.09.2026, Betrieb]`: Nova fragte nach einer Nebensache
(Gleis, Dauer), das folgende *"Gerne"* legte trotzdem den Termin an — 2 von 2.
Der `[LAGE]`-Block machte jede Zustimmung zum Auftrag, weil niemand festhielt,
ob ueberhaupt etwas angeboten worden war.

Zeugen dieser Datei:
  * **Das Angebot wird erkannt** — in den Formen, in denen Nova anbietet, und
    nicht in einer Rueckfrage nach einer Nebensache.
  * **Die blanke Zustimmung** — "Gerne" ja, "Ja, trag den Zahnarzt ein" nein.
  * **Der offene Punkt** — ablegen, lesen, entfernen; ein unlesbarer Eintrag
    gilt als keiner.
  * **Der Riegel im Empfang** — blanke Zustimmung ohne Angebot stellt nicht zu,
    mit Angebot schon, und ein eigener Auftrag geht immer durch.

**Was diese Tests NICHT koennen:** ob das Modell dem Zustimmungssatz folgt.
Das misst die Reihe in labor/.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import inspect
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from graph.nodes import dispatcher, router
from utils.offers import (
    Offer,
    find_offers,
    is_bare_consent,
    offer_clear,
    offer_key,
    offer_load,
    offer_matches,
    offer_store,
)


class FakeRedis:
    """Ein Speicher, der sich wie die benutzten vier Redis-Aufrufe verhaelt."""

    def __init__(self, inhalt: dict[str, str] | None = None) -> None:
        self.inhalt: dict[str, str] = dict(inhalt or {})
        self.ttl: dict[str, int] = {}

    def setex(self, key: str, ttl: int, wert: str) -> None:
        self.inhalt[key] = wert
        self.ttl[key] = ttl

    def get(self, key: str) -> str | None:
        return self.inhalt.get(key)

    def delete(self, key: str) -> int:
        return 1 if self.inhalt.pop(key, None) is not None else 0


class AngebotErkennenTest(unittest.TestCase):

    def test_die_formen_in_denen_nova_anbietet(self) -> None:
        for satz in (
            "Soll ich dir den Termin eintragen?",
            "Moechtest du, dass ich das notiere?",
            "Willst du, dass ich es festhalte?",
            "Ich kann dir das gern auf die Liste setzen.",
            "Wenn du magst, kann ich das vormerken.",
        ):
            with self.subTest(satz=satz):
                self.assertEqual(find_offers(satz), [satz])

    def test_eine_rueckfrage_nach_einer_nebensache_ist_kein_angebot(self) -> None:
        """Der gemessene Fall: Nova fragt nach dem Gleis, nicht nach dem Eintragen."""
        for satz in (
            "Und sag mal, welches Gleis wird denn nun genau besetzt?",
            "Weisst du schon, wie lange sie dauern wird?",
            "Das klingt nach einem langen Tag.",
        ):
            with self.subTest(satz=satz):
                self.assertEqual(find_offers(satz), [])

    def test_kein_text_kein_befund(self) -> None:
        for text in ("", "   ", None, 42, ["Soll ich das eintragen?"]):
            with self.subTest(text=text):
                self.assertEqual(find_offers(text), [])


class BlankeZustimmungTest(unittest.TestCase):

    def test_zustimmung_ohne_eigene_sache(self) -> None:
        for text in ("Gerne", "gerne!", "Ja, bitte", "Mach das", "Ok, gern", "Klar"):
            with self.subTest(text=text):
                self.assertTrue(is_bare_consent(text))

    def test_ein_auftrag_mit_eigener_sache_ist_keine_blanke_zustimmung(self) -> None:
        for text in (
            "Ja, trag den Zahnarzt ein",
            "Gerne, und setz Spuelmittel auf die Liste",
            "Schreib das auf",
            "",
        ):
            with self.subTest(text=text):
                self.assertFalse(is_bare_consent(text))


class OffenerPunktTest(unittest.TestCase):

    def _angebot(self) -> Offer:
        return Offer(sentence="Soll ich dir den Termin eintragen?", objects=("Zahnarzttermin",),
                     services=("timeline",), turn_id="t1", time=1.0)

    def test_ablegen_lesen_entfernen(self) -> None:
        speicher = FakeRedis()
        self.assertTrue(offer_store(speicher, "meister", "nova", self._angebot(), 900))
        self.assertEqual(speicher.ttl[offer_key("meister", "nova")], 900)
        gelesen = offer_load(speicher, "meister", "nova")
        self.assertEqual(gelesen.sentence, "Soll ich dir den Termin eintragen?")
        self.assertEqual(gelesen.objects, ("Zahnarzttermin",))
        offer_clear(speicher, "meister", "nova", "Test")
        self.assertIsNone(offer_load(speicher, "meister", "nova"))

    def test_unlesbares_gilt_als_keines(self) -> None:
        for roh in ("kein json", json.dumps({"objekte": []}), ""):
            with self.subTest(roh=roh):
                speicher = FakeRedis({offer_key("meister", "nova"): roh})
                self.assertIsNone(offer_load(speicher, "meister", "nova"))

    def test_die_sachen_reisen_vollstaendig_mit(self) -> None:
        """Nicht nur Namen: Klasse und Gedecktes, weil die Lage weiterzieht."""
        speicher = FakeRedis()
        angebot = Offer(sentence="Soll ich dir die Abholung eintragen?", objects=("Abholung",),
                        services=("timeline",), turn_id="t1", time=1.0,
                        details=({"name": "Abholung", "klasse": "vorgang",
                                  "gedeckt": {"Tag": "Samstag", "Uhrzeit": "10 Uhr"}},))
        offer_store(speicher, "meister", "nova", angebot, 900)
        gelesen = offer_load(speicher, "meister", "nova")
        self.assertEqual(gelesen.details[0]["gedeckt"], {"Tag": "Samstag", "Uhrzeit": "10 Uhr"})

    def test_ein_offenes_angebot_traegt_die_zustimmung(self) -> None:
        angebot = self._angebot()
        self.assertTrue(offer_matches(angebot, ["Zahnarzttermin"]))
        self.assertTrue(offer_matches(angebot, ["Einkaufsliste"]))  # Lage weitergezogen
        self.assertFalse(offer_matches(None, ["Zahnarzttermin"]))
        ohne_gegenstand = Offer(sentence="Soll ich das notieren?", objects=(), services=(),
                                turn_id="t1", time=1.0)
        # Seit dem 17.09.2026, nach der Messung: Die Lage entscheidet NICHT mit.
        # Ist die angebotene Sache nicht mehr akut, steht der Satz trotzdem —
        # der Gegenstand kommt aus dem Angebot, nicht aus der Lage.
        from graph.nodes.router import build_situation_block
        lage = {"herkunft": "fortgeschrieben",
                "objekte": [{"name": "Zahnarzttermin", "klasse": "vorgang", "akut": True, "gedeckt": {}, "offen": []}]}
        fremd = Offer(sentence="Soll ich die Abholung eintragen?", objects=("Abholung",),
                      services=("timeline",), turn_id="t1", time=1.0)
        self.assertIn("Zustimmung", build_situation_block(lage, {}, offer=fremd))
        self.assertIn("Soll ich die Abholung eintragen?", build_situation_block(lage, {}, offer=fremd))
        self.assertNotIn("Zustimmung", build_situation_block(lage, {}, offer=None))
        self.assertTrue(offer_matches(ohne_gegenstand, ["Irgendwas"]))
        self.assertTrue(offer_matches(ohne_gegenstand, []))


class VerdrahtungImDispatcherTest(unittest.TestCase):
    """Wer den offenen Punkt anlegt: der Turn, nachdem die Antwort steht."""

    SACHLAGE = {"herkunft": "fortgeschrieben",
                "objekte": [{"name": "Zahnarzttermin", "klasse": "vorgang", "akut": True,
                             "gedeckt": {"Tag": "Donnerstag"}, "offen": []}]}
    URTEIL = {"ergebnis": "gerechnet", "objekte": [{"name": "Zahnarzttermin", "empfaenger": ["timeline"]}]}

    def _merken(self, antwort: str, speicher: FakeRedis) -> None:
        state = {"response": antwort, "sachlage": self.SACHLAGE, "objekt_urteil": self.URTEIL,
                 "turn_id": "t1"}
        with patch.object(dispatcher, "cfg_redis_client", speicher):
            dispatcher._angebot_merken(state, "meister", "nova")

    def test_ein_angebot_in_der_antwort_wird_offener_punkt(self) -> None:
        speicher = FakeRedis()
        self._merken("Das ist ja bald. Soll ich dir den Termin eintragen?", speicher)
        angebot = offer_load(speicher, "meister", "nova")
        self.assertEqual(angebot.objects, ("Zahnarzttermin",))
        self.assertEqual(angebot.services, ("timeline",))
        self.assertIn("Soll ich", angebot.sentence)

    def test_der_dispatcher_ruft_das_merken_wirklich_auf(self) -> None:
        """Verdrahtung: ohne diesen Aufruf entsteht nie ein offener Punkt.

        Am Quelltext geprueft und nicht am Lauf — der Turn-Roh-Schreiber haengt
        an Postgres, Redis und dem halben Zustand. Die Gegenprobe (Aufruf
        entfernt) blieb ohne diesen Zeugen gruen.
        """
        quelle = inspect.getsource(dispatcher._turn_roh_schreiben)
        self.assertIn("_angebot_merken(state, user_id, character_id)", quelle)

    def test_eine_antwort_ohne_angebot_raeumt_den_alten_punkt_weg(self) -> None:
        """Ein Angebot gilt fuer den naechsten Turn, nicht auf Dauer."""
        speicher = FakeRedis()
        self._merken("Soll ich dir den Termin eintragen?", speicher)
        self._merken("Wie war dein Tag?", speicher)
        self.assertIsNone(offer_load(speicher, "meister", "nova"))


class RiegelImEmpfangTest(unittest.TestCase):
    """Der deterministische Teil der Regel — er haengt nicht am Modell."""

    ANTWORT = {"needs_memory": False, "needs_web": False, "needs_timeline": False,
               "momentum": "mid", "management_action": "agent", "management_target": "timeline",
               "management_target_typ": "titel"}

    def _route(self, reiz: str, angebot: Offer | None) -> dict:
        state = {"user_id": "pruefer", "character_id": "nova", "turn_id": "t2",
                 "user_prompt": reiz, "event_payload": {}, "node_annotations": [],
                 "agent_results": [], "sachlage": {"herkunft": "fortgeschrieben", "objekte": []}}
        stell = SimpleNamespace(chat=SimpleNamespace(submit_sync=lambda request, timeout=None: SimpleNamespace(
            text=json.dumps(self.ANTWORT), token_total=0, thinking="", parsed=dict(self.ANTWORT))))
        with patch.object(router, "model_service", stell), \
             patch.object(router, "session_turns_retrieve", return_value=[]), \
             patch.object(router, "shadow_nearness", return_value={"ergebnis": "ohne_akute_objekte"}), \
             patch.object(router, "offer_load", return_value=angebot), \
             patch("tools.redis_manager.redis_manager.get_json", return_value=None):
            return router.route(dict(state))

    def test_blanke_zustimmung_ohne_angebot_stellt_nicht_zu(self) -> None:
        ergebnis = self._route("Gerne", None)
        self.assertEqual(ergebnis["management_action"], "")
        self.assertEqual(ergebnis["management_target"], "")

    def test_mit_offenem_angebot_bleibt_die_zustellung(self) -> None:
        angebot = Offer(sentence="Soll ich dir den Termin eintragen?", objects=("Zahnarzttermin",),
                        services=("timeline",), turn_id="t1", time=1.0)
        ergebnis = self._route("Gerne", angebot)
        self.assertEqual(ergebnis["management_action"], "agent")
        self.assertEqual(ergebnis["management_target"], "timeline")

    def test_ein_eigener_auftrag_geht_auch_ohne_angebot_durch(self) -> None:
        ergebnis = self._route("Trag mir den Zahnarzt am Donnerstag um 15 Uhr ein.", None)
        self.assertEqual(ergebnis["management_action"], "agent")


if __name__ == "__main__":
    unittest.main()
