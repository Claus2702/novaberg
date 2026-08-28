"""Zeugen fuer die Sachlage-Bruecke — der Weg der Ausloeser-turn_id und ihr Leser.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 4, Teil 3. Ein
Impuls beruht auf einem Turn; bei der Zustellung soll der Verfasser beide
Blasen sehen — die aktuelle und die des Ausloesers — und den Uebergang
bauen, statt unvermittelt einzuwerfen.

Die Kette hat vier Glieder, und jedes hat hier einen Zeugen:

  1. **Der Auftrag** traegt `ausloeser_turn_id` (Dataclass und Lesespalten).
  2. **Der Stapel-Eintrag** traegt sie — immer, auch als `None`: Ein
     weggelassenes Feld waere von einem Eintrag alter Bauart nicht zu
     unterscheiden.
  3. **Das Ereignis** traegt sie ins Payload des CharacterGraph.
  4. **Der Knoten** baut die Bruecke: mit harter `turn_id` ueber die
     Verlaufszeile, ohne sie ueber die aehnlichste Zeile — **und markiert
     den Rueckfall**. Ohne beide Enden gibt es keine Bruecke, und der
     Verfasser bekommt keinen Block.

Dazu **`thema` als Pflichtfeld** des Artefakts (Teil 2): Der Anzeigename
der Blase und das Findewort neben dem Vektor, aus demselben Call.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from graph.nodes.sachlage import (
    BRIDGE_VIA_EMBEDDING,
    BRIDGE_VIA_TURN_ID,
    HERKUNFT_FRISCH,
    HERKUNFT_IMPULS,
    _validate_artifact,
    sachlage_assess,
    sachlage_bridge_block,
)
from memory.repositories.shadow_auftrag_repository import LESE_SPALTEN, ShadowAuftrag
from services.pixie import stack as stack_modul
from services.pixie.stack import build_impulse_embed_text
from services.shadow_delivery import _impuls_in_den_charaktergraph

AKTUELL: dict = {
    "thema":          "Rettich-Bewaesserung",
    "gegenstand":     "Die Bewertung von Bewaesserungsmethoden fuer Rettich.",
    "nutzerziel":     "Der Nutzer will die schonendere Methode kennen.",
    "ausdrucksweise": "pruefend",
    "objekte":        [],
}

DAMALS: dict = {
    "turn_id":        "t-ausloeser",
    "thema":          "Hainbuchen-Wurzeln",
    "gegenstand":     "Wie Hainbuchen verdichteten Boden wieder durchlaessig machen.",
    "nutzerziel":     "Der Nutzer wollte die Bodenverdichtung im Garten verstehen.",
    "ausdrucksweise": "erzaehlend",
    "objekte":        [],
    "herkunft":       "frisch",
}

EINTRAG: dict = {
    "thema": "Bodenverdichtung", "aufgabe": "recherche", "inhalt": "Wissen.",
    "emotion": "neugierig", "modus": "fachgespraech", "intentionen": [],
    "ausloeser_turn_id": "t-ausloeser",
}


def _state(**felder: object) -> dict:
    basis: dict = {
        "user_id": "u", "character_id": "c", "turn_id": "t-jetzt",
        "user_prompt": "", "session_turns": [], "event_source": "character",
        "event_payload": {
            "reiz_herkunft": "eigener_impuls", "eigener_gedanke": "Wissen.",
            "prompt_thema": "Bodenverdichtung", "ausloeser_turn_id": "t-ausloeser",
        },
    }
    basis.update(felder)
    return basis


class DerAuftragTraegtDieTurnIdTest(unittest.TestCase):
    """Glied 1: Dataclass und Lesespalten."""

    def test_die_dataclass_kennt_das_feld_und_es_ist_none_ohne_wert(self) -> None:
        auftrag = ShadowAuftrag(
            user_id="u", character_id="c", beobachter="user",
            aufgabe="recherche", thema="x", salienz=0.5,
        )
        self.assertIsNone(auftrag.ausloeser_turn_id)

    def test_die_lesespalten_liefern_das_feld(self) -> None:
        """Sonst kaeme es am Agenten nie an — der Dispatcher reicht die
        gelesene Zeile als Parameter durch.
        """
        self.assertIn("ausloeser_turn_id", LESE_SPALTEN)


class DerStapelEintragTraegtDieTurnIdTest(unittest.TestCase):
    """Glied 2: stack_push legt sie ab — immer, auch leer."""

    def setUp(self) -> None:
        self._embed = patch.object(
            stack_modul.model_service, "embed",
            MagicMock(submit_sync=MagicMock(
                return_value=MagicMock(embedding=[0.1, 0.2], duration_seconds=0.01),
            )),
        )
        self._embed.start()
        self.addCleanup(self._embed.stop)
        self._aktiv = patch.object(stack_modul, "PIXIE_AKTIV", True)
        self._aktiv.start()
        self.addCleanup(self._aktiv.stop)

    def _abgelegt(self, **extra: object) -> dict:
        redis_mock = MagicMock()
        stack_modul.stack_push(
            redis_mock, "u", "recherche", "Bodenverdichtung", "Wissen.", **extra,
        )
        _key, roh = redis_mock.rpush.call_args[0]
        return json.loads(roh)

    def test_mit_wert_steht_er_im_eintrag(self) -> None:
        self.assertEqual(
            self._abgelegt(ausloeser_turn_id="t-ausloeser")["ausloeser_turn_id"],
            "t-ausloeser",
        )

    def test_ohne_wert_steht_none_im_eintrag_nicht_nichts(self) -> None:
        eintrag: dict = self._abgelegt()

        self.assertIn("ausloeser_turn_id", eintrag)
        self.assertIsNone(eintrag["ausloeser_turn_id"])

    def test_der_embed_text_hat_eine_benannte_formel(self) -> None:
        """Der Rueckfall der Bruecke rechnet das Impuls-Embedding nach —
        aus derselben Formel, nicht aus einer Kopie davon.
        """
        self.assertEqual(
            build_impulse_embed_text("Thema", "x" * 300), "Thema " + "x" * 200,
        )


class DasEreignisTraegtDieTurnIdTest(unittest.TestCase):
    """Glied 3: das Payload des CharacterGraph."""

    def _payload(self, eintrag: dict) -> dict:
        with patch(
            "services.shadow_delivery.event_erzeugen", return_value="ev-1",
        ) as ruf:
            _impuls_in_den_charaktergraph(MagicMock(), "u", "t-jetzt", "Wissen.", eintrag)
        return ruf.call_args.kwargs["payload"]

    def test_mit_wert(self) -> None:
        self.assertEqual(self._payload(EINTRAG)["ausloeser_turn_id"], "t-ausloeser")

    def test_ohne_wert_steht_none_im_payload(self) -> None:
        """Ein Eintrag alter Bauart hat das Feld nicht — das Payload hat es
        trotzdem, als None: Der Leser prueft auf None, nicht auf Anwesenheit.
        """
        alt: dict = {k: v for k, v in EINTRAG.items() if k != "ausloeser_turn_id"}

        payload: dict = self._payload(alt)

        self.assertIn("ausloeser_turn_id", payload)
        self.assertIsNone(payload["ausloeser_turn_id"])


class DerKnotenBautDieBrueckeTest(unittest.TestCase):
    """Glied 4: beide Enden, oder keine Bruecke."""

    def _assess(self, zustand: dict, *, per_turn_id, per_embedding) -> dict:
        with patch("graph.nodes.sachlage.sachlage_load",
                   return_value=(dict(AKTUELL), False)), \
             patch("graph.nodes.sachlage.log_berechnung"), \
             patch("graph.nodes.sachlage._persist_history") as schreiben, \
             patch("graph.nodes.sachlage.history_read_turn",
                   return_value=per_turn_id) as lesen, \
             patch("graph.nodes.sachlage._impulse_embedding",
                   return_value=[0.1] * 4), \
             patch("graph.nodes.sachlage.history_nearest",
                   return_value=per_embedding) as suchen:
            state = sachlage_assess(zustand)
        self.schreiben, self.lesen, self.suchen = schreiben, lesen, suchen
        return state

    def test_mit_harter_turn_id_kommt_die_zeile_des_ausloesers(self) -> None:
        state = self._assess(_state(), per_turn_id=dict(DAMALS), per_embedding=None)

        bruecke: dict = state["sachlage_bruecke"]
        self.assertEqual(bruecke["weg"], BRIDGE_VIA_TURN_ID)
        self.assertEqual(bruecke["damals"]["gegenstand"], DAMALS["gegenstand"])
        self.assertEqual(bruecke["ausloeser_turn_id"], "t-ausloeser")
        self.suchen.assert_not_called()

    def test_ohne_turn_id_traegt_der_rueckfall_seine_marke(self) -> None:
        zustand: dict = _state()
        zustand["event_payload"]["ausloeser_turn_id"] = None

        state = self._assess(
            zustand, per_turn_id=None,
            per_embedding={**DAMALS, "kosinus": 0.71},
        )

        bruecke: dict = state["sachlage_bruecke"]
        self.assertEqual(bruecke["weg"], BRIDGE_VIA_EMBEDDING)
        self.assertAlmostEqual(bruecke["kosinus"], 0.71)
        self.lesen.assert_not_called()

    def test_turn_id_ins_leere_faellt_auf_die_suche_zurueck(self) -> None:
        """Die Zeile kann fehlen — der Ausloeser lag vor dem Bau der Tabelle."""
        state = self._assess(
            _state(), per_turn_id=None, per_embedding={**DAMALS, "kosinus": 0.66},
        )

        self.assertEqual(state["sachlage_bruecke"]["weg"], BRIDGE_VIA_EMBEDDING)

    def test_ohne_beide_enden_gibt_es_keine_bruecke(self) -> None:
        state = self._assess(_state(), per_turn_id=None, per_embedding=None)

        self.assertEqual(state["sachlage_bruecke"], {})
        self.assertEqual(state["sachlage"]["herkunft"], HERKUNFT_IMPULS)

    def test_ein_impuls_turn_schreibt_keine_verlaufszeile(self) -> None:
        """Uebernommene Artefakte erzeugen keine Doppelzeile."""
        self._assess(_state(), per_turn_id=dict(DAMALS), per_embedding=None)

        self.schreiben.assert_not_called()

    def test_ein_nutzer_turn_hat_keine_bruecke_und_schreibt_den_verlauf(self) -> None:
        zustand: dict = _state(
            event_source="user", user_prompt="Wie waessert man Rettich?",
            event_payload={},
        )
        with patch("graph.nodes.sachlage.sachlage_load", return_value=(None, False)), \
             patch("graph.nodes.sachlage._derive", return_value=dict(AKTUELL)), \
             patch("graph.nodes.sachlage._sachlage_store"), \
             patch("graph.nodes.sachlage.log_berechnung"), \
             patch("graph.nodes.sachlage._persist_history") as schreiben:
            state = sachlage_assess(zustand)

        self.assertEqual(state["sachlage_bruecke"], {})
        self.assertEqual(state["sachlage"]["herkunft"], HERKUNFT_FRISCH)
        schreiben.assert_called_once()

    def test_ein_ausfall_schreibt_keine_verlaufszeile(self) -> None:
        """Der uebernommene Vorgaenger ist kein neues Faktum."""
        zustand: dict = _state(event_source="user", user_prompt="x", event_payload={})
        with patch("graph.nodes.sachlage.sachlage_load",
                   return_value=(dict(AKTUELL), False)), \
             patch("graph.nodes.sachlage._derive", return_value=None), \
             patch("graph.nodes.sachlage.log_berechnung"), \
             patch("graph.nodes.sachlage._persist_history") as schreiben:
            sachlage_assess(zustand)

        schreiben.assert_not_called()


class ThemaIstPflichtTest(unittest.TestCase):
    """Teil 2: Der Anzeigename der Blase kommt aus demselben Call."""

    def test_ohne_thema_wird_das_artefakt_verworfen(self) -> None:
        ohne: dict = {k: v for k, v in AKTUELL.items() if k != "thema"}

        self.assertIsNone(_validate_artifact(ohne))

    def test_mit_thema_geht_es_durch(self) -> None:
        self.assertIsNotNone(_validate_artifact(dict(AKTUELL)))


class DerVerfasserBekommtDenBlockTest(unittest.TestCase):
    """Der Leser der Bruecke."""

    def test_der_block_nennt_beide_blasen(self) -> None:
        block: str = sachlage_bridge_block({
            "weg": BRIDGE_VIA_TURN_ID, "ausloeser_turn_id": "t-ausloeser",
            "damals": DAMALS, "aktuell": AKTUELL,
        })

        self.assertTrue(block.startswith("[SACHLAGE-BRUECKE]"))
        self.assertIn(DAMALS["gegenstand"], block)
        self.assertIn(AKTUELL["gegenstand"], block)

    def test_der_rueckfall_steht_im_block(self) -> None:
        """Der Verfasser soll wissen, dass der Anlass erschlossen ist."""
        block: str = sachlage_bridge_block({
            "weg": BRIDGE_VIA_EMBEDDING, "kosinus": 0.7,
            "damals": DAMALS, "aktuell": AKTUELL,
        })

        self.assertIn("vermutlich", block)

    def test_der_verfasser_baut_den_block_ein(self) -> None:
        """Am Verhalten gemessen, nicht am Quelltext: Die Gegenprobe vom
        28.08.2026 entfernte das `append`, und ein Grep auf den Namen blieb
        gruen, weil der Import ihn weiter trug.
        """
        from ei.haltung import haltung_berechnen
        from graph.nodes import verfasser

        zustand: dict = {
            "user_prompt": "", "user_id": "u", "character_id": "c",
            "turn_id": "t", "memory_context": "", "web_context": "",
            "session_turns": [], "task_block": "", "event_source": "character",
            "event_payload": {"reiz_herkunft": "eigener_impuls", "eigener_gedanke": "Wissen."},
            "gespraechsvektor": "", "gv_detail": {},
            "sachlage": {**AKTUELL, "herkunft": HERKUNFT_IMPULS},
            "sachlage_bruecke": {
                "weg": BRIDGE_VIA_TURN_ID, "ausloeser_turn_id": "t-ausloeser",
                "damals": DAMALS, "aktuell": AKTUELL,
            },
            "haltung": haltung_berechnen("werkstatt", {}),
        }

        prompt: str = verfasser._build_system_prompt(zustand)

        self.assertIn("[SACHLAGE-BRUECKE]", prompt)
        self.assertIn(DAMALS["gegenstand"], prompt)
        self.assertGreater(prompt.find("[SACHLAGE-BRUECKE]"), prompt.find("[SACHLAGE]"))

    def test_ohne_bruecke_kein_block(self) -> None:
        """Die Gegenprobe: leere Bruecke, kein Block — und keine Fehlerzeile."""
        from ei.haltung import haltung_berechnen
        from graph.nodes import verfasser

        zustand: dict = {
            "user_prompt": "x", "user_id": "u", "character_id": "c",
            "turn_id": "t", "memory_context": "", "web_context": "",
            "session_turns": [], "task_block": "", "event_source": "user",
            "event_payload": {}, "gespraechsvektor": "", "gv_detail": {},
            "sachlage": {**AKTUELL, "herkunft": HERKUNFT_FRISCH},
            "sachlage_bruecke": {},
            "haltung": haltung_berechnen("werkstatt", {}),
        }
        with self.assertNoLogs("ki_server.verfasser", level="ERROR"):
            prompt: str = verfasser._build_system_prompt(zustand)

        self.assertNotIn("[SACHLAGE-BRUECKE]", prompt)

    def test_der_state_kennt_den_kanal(self) -> None:
        """LangGraph verwirft, was nicht deklariert ist — lautlos."""
        from graph.state import ConversationState

        self.assertIn("sachlage_bruecke", ConversationState.__annotations__)


if __name__ == "__main__":
    unittest.main()
