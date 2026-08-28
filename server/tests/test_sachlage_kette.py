"""Zeugen fuer den Anfang der Kette — die turn_id erreicht das KZG-Hash und den Auftrag.

**Anlass (28.08.2026):** Nach dem Bau der Sachlage-Bruecke (`novaberg-thinking-lage_k.md`
§4, Scheibe 4) trugen 21 neue Auftraege keine `ausloeser_turn_id`, und **0 von 300
KZG-Hashes** trugen eine `turn_id` — der Salienz-Schreibauftrag reichte sie nicht
durch, das Hash-Mapping kannte das Feld nicht, und beide Erzeuger des Turnbezugs
(KZG-Queues, Synapsen-Promotion) lasen ins Leere. Gefunden vom Bestand, nicht vom Bau.

Je Stelle ein Zeuge, und beide Schreiber desselben Stores (§4n): der
Salienz-Schreibauftrag, das Hash-Mapping (mit Wert und leer), die KZG-Queues,
der Legacy-Manager und der Rueckweg der Promotion.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch


class DieKetteBeginntBeimTurnTest(unittest.TestCase):
    """Glied 0 — der Bestand fand die Luecke am Kettenanfang (28.08.2026):
    0 von 300 KZG-Hashes trugen eine `turn_id`, und 21 Auftraege nach dem
    Bau trugen keine `ausloeser_turn_id`. Die drei Stellen, an denen der
    Turn bis dahin verloren ging, bekommen je einen Zeugen."""

    def test_der_schreibauftrag_der_salienz_traegt_die_turn_id(self) -> None:
        from graph.nodes.salience import analyze
        from services.model_services import model_service

        antwort = MagicMock()
        antwort.parsed = {"salienz": 0.5, "themen": ["Kosmologie"], "dimension": "wissen"}
        antwort.token_total = 0
        antwort.text = "{}"
        zustand: dict = {
            "graph_rolle": "character", "ei_calc_rolle": "character",
            "user_prompt": "Warum leuchten Neutronensterne?", "response": "Restwaerme.",
            "pending_writes": [], "token_total": 0, "turn_id": "t-kette",
            "character_id": "nova", "gravitationsterm": 0.0,
        }
        with patch("graph.nodes.salience._prompt_segmentieren", return_value=["Restwaerme."]), \
             patch.object(model_service.chat, "submit_sync", return_value=antwort):
            writes: list[dict] = analyze(zustand, MagicMock(), "meister")["pending_writes"]

        self.assertTrue(writes)
        self.assertEqual(writes[0]["daten"]["turn_id"], "t-kette")

    def test_der_kzg_hash_traegt_die_turn_id(self) -> None:
        from agents.kzg import speicher

        rc = MagicMock()
        with patch("agents.kzg.speicher.log_db_write"):
            speicher._neu_anlegen(
                rc, "u", "nova", "user",
                {"themen": ["Kosmologie"], "intentionen": []}, "Kern.", [0.1, 0.2],
                0.9, turn_id="t-kette",
            )

        mapping: dict = rc.hset.call_args.kwargs["mapping"]
        self.assertEqual(mapping["turn_id"], "t-kette")

    def test_der_kzg_hash_traegt_das_feld_auch_leer(self) -> None:
        """Leer heisst unbekannt — und ist von »nicht geschrieben« unterscheidbar."""
        from agents.kzg import speicher

        rc = MagicMock()
        with patch("agents.kzg.speicher.log_db_write"):
            speicher._neu_anlegen(
                rc, "u", "nova", "user",
                {"themen": ["x"], "intentionen": []}, "Kern.", [0.1], 0.9,
            )

        self.assertIn("turn_id", rc.hset.call_args.kwargs["mapping"])

    def test_die_queue_bekommt_die_turn_id_des_kontexts(self) -> None:
        from agents.kzg import queues

        zustand: dict = {
            "parameter": {
                "salienz_obj": {"intentionen": ["information_suchen"], "emotion": "neugierig",
                                "modus": "fachgespraech", "arousal": 0.6},
                "speicher_status": "neu", "neue_salienz": 1.0, "kzg_key": "kzg:u:nova:1",
                "kzg_themen_str": "Kosmologie", "kzg_dimension": "wissen", "kern": "Kern.",
            },
            "kontext": {"user_id": "u", "character_id": "nova", "turn_id": "t-kette"},
            "schritte": [],
        }
        with patch("agents.kzg.queues.PIXIE_AKTIV", True), \
             patch("agents.kzg.queues.promotion_queue_push", return_value=True), \
             patch("agents.kzg.queues._aufgabe_aus_intention", return_value="recherche"), \
             patch("agents.kzg.queues.shadow_queue_push") as push:
            queues.queues_befuellen(zustand)

        push.assert_called_once()
        self.assertEqual(push.call_args.kwargs["ausloeser_turn_id"], "t-kette")

    def test_der_legacy_manager_reicht_die_turn_id_weiter(self) -> None:
        """Der zweite Schreiber desselben Stores — sonst hinge der Zeuge oben
        an einem Pfad und der andere bliebe stumm (§4n)."""
        from plugins.kzg_manager.manager import KzgManager

        with patch("plugins.kzg_manager.manager.kzg_store", return_value="neu") as store:
            KzgManager().execute(
                [{"daten": {"salienz_obj": {"themen": ["x"]}, "embedding": [0.1],
                            "turn_id": "t-kette"}}],
                "u", MagicMock(), "postgresql://x",
            )

        self.assertEqual(store.call_args.kwargs["turn_id"], "t-kette")


    def test_der_rueckweg_der_promotion_traegt_die_turn_id(self) -> None:
        """Der dritte Erzeuger — im Betrieb lebt sein Auftrag nur bis zum
        naechsten Pixie-Takt, deshalb steht der Beleg hier und nicht im Bestand."""
        from agents.synapsen_promotion.agent import SynapsenPromotionAgent

        with patch("agents.synapsen_promotion.agent.material_waehlen",
                   return_value=("Material.", "roh")), \
             patch("agents.synapsen_promotion.agent.shadow_queue_push") as push:
            SynapsenPromotionAgent._rueckweg_einreihen(
                kzg_key="kzg:u:nova:1", user_id="u", character_id="nova",
                inhalt="Kern.", themen_str="Pulsare", salienz=0.8, turn_id="t-kette",
            )

        self.assertEqual(push.call_args.kwargs["ausloeser_turn_id"], "t-kette")


if __name__ == "__main__":
    unittest.main()
