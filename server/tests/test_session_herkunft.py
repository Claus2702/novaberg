"""Tests: Ein Session-Turn traegt, welcher Vorgang ihn erzeugt hat.

Ziel: Antwort und Eigen-Impuls sind in den Daten unterscheidbar, nicht nur im
Laufzeit-Protokoll.

Befund, aus dem das entstand (Chat 119): Zwei Vorgaenge schreiben Eintraege
derselben Form in denselben Verlauf — die Antwort auf eine Nutzeraeusserung
und Novas eigener Impuls. Beide landeten mit `rolle='assistant'` und ohne
Herkunftsfeld im Speicher. Die Unterscheidung existierte ausschliesslich als
Zeile im Log des Event-Consumers und wurde nicht mitgeschrieben.

Die Folge war nicht theoretisch: Ein Turn ging verloren, ein Impuls fuellte die
Luecke, und der Verlauf sah aus dem Speicher heraus vollstaendig aus. Die
Oberflaeche des Clients konnte die beiden an der Darstellung unterscheiden —
die Daten konnten es nicht.

Zeuge dieser Datei: Die erwarteten Werte stammen aus dem Ereignis-Payload
(`reiz_herkunft`), den der Delivery-Pfad setzt und den der Responder bereits
liest — nicht aus dem Code, der sie in den Turn schreibt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from unittest.mock import MagicMock

from memory.session import session_turn_store

USER: str = "meister"
CHAR: str = "nova"


def _geschrieben(client: MagicMock) -> dict:
    """Liest den Turn, den session_turn_store nach Redis geschoben hat."""
    args = client.rpush.call_args.args
    return json.loads(args[1])


class HerkunftWirdMitgeschrieben(unittest.TestCase):
    """Der Wert landet unveraendert im Turn."""

    def test_nutzer_turn(self) -> None:
        """Die Antwort auf eine Nutzeraeusserung."""
        client = MagicMock()
        session_turn_store(client, USER, CHAR, "assistant", "Antwort",
                           herkunft="nutzer_turn")
        self.assertEqual(_geschrieben(client)["herkunft"], "nutzer_turn")

    def test_eigener_impuls(self) -> None:
        """Novas selbst angestossene Aeusserung — derselbe rolle-Wert."""
        client = MagicMock()
        session_turn_store(client, USER, CHAR, "assistant", "Impuls",
                           herkunft="eigener_impuls")
        turn = _geschrieben(client)
        self.assertEqual(turn["herkunft"], "eigener_impuls")
        self.assertEqual(turn["rolle"], "assistant")

    def test_die_beiden_sind_unterscheidbar(self) -> None:
        """Der Kern, und der positive Zwilling zu beiden Tests oben.

        Ohne diese Zusicherung bestuenden sie auch dann, wenn das Feld einen
        konstanten Wert traege — und genau die Ununterscheidbarkeit ist der
        Befund, den diese Datei schliesst.
        """
        a, b = MagicMock(), MagicMock()
        session_turn_store(a, USER, CHAR, "assistant", "x", herkunft="nutzer_turn")
        session_turn_store(b, USER, CHAR, "assistant", "y", herkunft="eigener_impuls")
        self.assertNotEqual(_geschrieben(a)["herkunft"], _geschrieben(b)["herkunft"])


class LeerHeisstUnbekannt(unittest.TestCase):
    """Ein Default haette rueckwirkend eine Aussage erfunden."""

    def test_ohne_angabe_bleibt_das_feld_leer(self) -> None:
        """Nicht 'nutzer_turn'.

        Turns von vor dieser Aenderung tragen das Feld nicht. Ein Default
        wuerde aus ihnen eine Herkunft machen, die niemand erhoben hat — und
        damit denselben Fehler eine Ebene tiefer wiederholen.
        """
        client = MagicMock()
        session_turn_store(client, USER, CHAR, "assistant", "Antwort")
        self.assertEqual(_geschrieben(client)["herkunft"], "")

    def test_das_feld_ist_immer_vorhanden(self) -> None:
        """Vorhanden und leer ist etwas anderes als gar nicht da.

        Ein fehlender Schluessel zwingt jeden Leser zu einem eigenen Default —
        genau die Stelle, an der sich zwei Leser unterschiedlich entscheiden.
        """
        client = MagicMock()
        session_turn_store(client, USER, CHAR, "user", "Frage")
        self.assertIn("herkunft", _geschrieben(client))


class DerDispatcherReichtSieWeiter(unittest.TestCase):
    """Die Verdrahtung, nicht der Baustein.

    Die Tests oben pruefen `session_turn_store`. Sie waren alle gruen, als dem
    Dispatcher testweise das `herkunft=`-Argument entfernt wurde — also als die
    Herkunft wieder nirgends ankam. **Ein Netz, das den Baustein prueft und
    nicht seinen Aufruf, laesst genau den Defekt durch, den es schliessen
    soll.** Zum zweiten Mal an einem Tag dieselbe Luecke.
    """

    @staticmethod
    def _zustand(payload: dict | None) -> dict:
        """Baut den Dispatcher-State eines Assistant-Turns."""
        return {
            "user_id":       USER,
            "character_id":  CHAR,
            "response":      "Eine Antwort.",
            "event_payload": payload,
            "external":      None,
            "internal":      None,
        }

    def _herkunft(self, payload: dict | None) -> str:
        """Faehrt den Dispatcher und liest das herkunft-Argument ab."""
        from unittest.mock import patch

        import graph.nodes.dispatcher as modul

        # `session_summarize_if_needed` laeuft danach und vergleicht eine
        # Redis-Laenge gegen eine Zahl. Es gehoert nicht zum Prueffall und
        # wird stillgelegt, nicht mitgemessen.
        with patch.object(modul, "session_turn_store") as store, \
             patch.object(modul, "session_summarize_if_needed", MagicMock()), \
             patch.object(modul, "cfg_redis_client", MagicMock()):
            modul._session_turn_schreiben(self._zustand(payload))

        return store.call_args.kwargs["herkunft"]

    def test_ein_impuls_kommt_als_impuls_an(self) -> None:
        """Der Wert aus dem Ereignis erreicht den Speicher."""
        self.assertEqual(
            self._herkunft({"reiz_herkunft": "eigener_impuls"}), "eigener_impuls",
        )

    def test_ein_nutzer_turn_kommt_als_nutzer_turn_an(self) -> None:
        """Der Schluessel fehlt dort — das ist der Regelfall, kein Ausfall."""
        self.assertEqual(self._herkunft({"turn_id": "t-1"}), "nutzer_turn")

    def test_ohne_payload_ebenfalls_nutzer_turn(self) -> None:
        """Ein Lauf ohne Ereignis-Nutzlast ist kein Impuls."""
        self.assertEqual(self._herkunft(None), "nutzer_turn")

    def test_die_beiden_wege_sind_unterscheidbar(self) -> None:
        """Der positive Zwilling zur Verdrahtung.

        Ohne ihn bestuenden die drei oben auch dann, wenn der Dispatcher einen
        konstanten Wert durchreichte.
        """
        self.assertNotEqual(
            self._herkunft({"reiz_herkunft": "eigener_impuls"}),
            self._herkunft({"turn_id": "t-1"}),
        )
