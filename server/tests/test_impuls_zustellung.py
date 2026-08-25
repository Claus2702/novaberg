"""Tests fuer die Zustellung eines Pixie-Impulses an die Clients.

Ziel: Ein Impuls ist beim Empfaenger als Impuls erkennbar, ohne dass er einen
eigenen Nachrichtentyp braucht.

Vor dem Umbau erkannte der Client einen Impuls daran, dass sein Nachrichtentyp
(`shadow_impuls`) ihm unbekannt war und im Auffangzweig landete. Seit der
Impuls durch den vollen CharacterGraph laeuft, traegt er denselben Typ wie jede
andere Antwort — das Merkmal muss also ausdruecklich mitreisen.

Geprueft wird das Payload, das der Event-Consumer baut. Die Darstellung im
Client haengt daran; sie hat keinen Testlauf im Server-Image.
"""

import unittest
from unittest.mock import MagicMock, patch

from services.shadow_delivery import _impuls_in_den_charaktergraph


class ImpulsHerkunftImPayloadTest(unittest.TestCase):
    """Der Marker entsteht in der Delivery und muss bis zum Client tragen."""

    def test_delivery_setzt_den_herkunfts_marker(self):
        eintrag: dict = {"thema": "T", "aufgabe": "recherche", "inhalt": "Wissen",
                         "emotion": "neugierig", "modus": "fachgespraech"}
        with patch("services.shadow_delivery.event_erzeugen", return_value="ev") as ruf:
            _impuls_in_den_charaktergraph(MagicMock(), "meister", "t-1", "Wissen", eintrag)

        payload: dict = ruf.call_args.kwargs["payload"]
        self.assertEqual(payload["reiz_herkunft"], "eigener_impuls")

    def test_marker_ueberlebt_die_json_runde(self):
        """Das Payload reist als JSON durch Redis — ein Objekt darin braeche es."""
        import json
        eintrag: dict = {"thema": "T", "aufgabe": "recherche", "inhalt": "W"}
        with patch("services.shadow_delivery.event_erzeugen", return_value="ev") as ruf:
            _impuls_in_den_charaktergraph(MagicMock(), "meister", "t-2", "W", eintrag)

        payload: dict = ruf.call_args.kwargs["payload"]
        wieder: dict = json.loads(json.dumps(payload, ensure_ascii=False))
        self.assertEqual(wieder["reiz_herkunft"], "eigener_impuls")


class KeineRueckfallebeneTest(unittest.TestCase):
    """Was nicht gedacht wurde, wird nicht gesprochen."""

    def test_delivery_formuliert_selbst_nichts_mehr(self):
        """Der eigene LLM-Call und sein Prompt sind entfernt, nicht stillgelegt."""
        import services.shadow_delivery as sd

        self.assertFalse(hasattr(sd, "_delivery_formulieren"))
        self.assertFalse(hasattr(sd, "DELIVERY_SYSTEM_PROMPT"))

    def test_delivery_sendet_nicht_mehr_selbst(self):
        """Kein broadcast, kein eigener Session-Turn — beides macht der Graph."""
        import services.shadow_delivery as sd

        self.assertFalse(hasattr(sd, "broadcast"))
        self.assertFalse(hasattr(sd, "session_turn_store"))

    def test_kein_eigener_nachrichtentyp_mehr(self):
        """shadow_impuls existiert nirgends mehr im Modul."""
        import inspect

        import services.shadow_delivery as sd

        quelle: str = inspect.getsource(sd)
        self.assertNotIn("shadow_impuls", quelle)


if __name__ == "__main__":
    unittest.main()
