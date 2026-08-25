"""Tests: eine zugestellte Antwort nennt den Reiz, auf den sie antwortet.

Am 01.08.2026 blieb eine Antwort aus, und der Client zeigte die Antwort des
**naechsten** Turns als Antwort auf die unbeantwortete Nachricht an — fluessig,
geschlossen, zum falschen Thema (novaberg-bugs.md -> ANTWORT-OHNE-ZUORDNUNG).
Die Zustellung trug keine Turn-Zuordnung; der Client ordnet der letzten
Nachricht zu, was ankommt. Solange jeder Turn antwortet, stimmt das. Sobald
einer ausfaellt, verschiebt sich alles um eins.

Zeugen dieser Datei:
  * Die `turn_id` des Reizes steht im Event-Payload, gesetzt vom Erzeuger des
    Turns (novaberg-convention-event-model.md 3.1.1). Sie ist der Wert, gegen
    den geprueft wird — nicht ein Wert, den die Zustellung selbst gebildet hat.
  * Die Antwort-Nutzlast muss die Reiz-Kennung tragen, **nicht** die aus dem
    Ergebnis-Zustand. Deshalb tragen beide im Test verschiedene Werte: Ein Bau,
    der die naheliegende falsche Quelle liest, wird rot.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import inspect
import json
import unittest
from unittest.mock import MagicMock, patch

import api.chat as chat_mod
import services.event_consumer as ec_mod

CONSUMER_LOGGER: str = "ki_server.event_consumer"

# Die Kennung des Reizes — unverwechselbar, damit kein anderes Feld der
# Nutzlast versehentlich denselben Wert traegt.
REIZ_TURN_ID:  str = "reiz-4f1c9a"
# Die Kennung im Ergebnis-Zustand. Sie ist bewusst eine andere: Wer sie
# ausliefert, hat die falsche Quelle gelesen.
STATE_TURN_ID: str = "state-77bb02"
# Die Kennung einer einzelnen Aeusserung, wie der Endpunkt sie vergibt.
NACHRICHT_ID:  str = "nachricht-1a2b3c"


def _event(turn_id: str = REIZ_TURN_ID, **payload_felder: object) -> dict:
    """Ein Nutzer-Event, wie es der Chat-Endpunkt in die Queue legt."""
    payload: dict = {
        "turn_id":     turn_id,
        "user_prompt": "Wie entsteht ein Gammablitz?",
    }
    payload.update(payload_felder)
    return {
        "event_id":      "ev-1",
        "user_id":       "meister",
        "character_id":  "nova",
        "source":        "user",
        "typ":           "message",
        "payload":       payload,
        "trigger_count": 0,
    }


def _graph_ergebnis(response: str = "Ein Gammablitz entsteht, wenn ...") -> dict:
    """Das Ergebnis eines CharacterGraph-Laufs, so weit die Zustellung es liest."""
    return {
        "response":    response,
        "turn_id":     STATE_TURN_ID,
        "internal":    None,
        "model":       "qwen3:30b",
        "token_total": 1177,
    }


class _Zustellung:
    """Faengt ab, was `broadcast` an die Clients geben wuerde."""

    def __init__(self) -> None:
        self.nutzlasten: list[dict] = []

    async def __call__(self, user_id: str, nachricht: str, character_id: str = "") -> None:
        self.nutzlasten.append(json.loads(nachricht))


class _EventVerarbeitenLauf(unittest.IsolatedAsyncioTestCase):
    """Faehrt den Aufrufer, nicht den Nutzlast-Bau allein.

    Der Defekt sass nicht in einer Funktion, sondern in der Zeile, die die
    Nutzlast zusammensetzt. Ein Test auf einen herausgeloesten Bauer haette ihn
    nicht gefunden.
    """

    async def _zustellen(self, event: dict, ergebnis: dict) -> list[dict]:
        """Laesst den Consumer ein Event verarbeiten und gibt die Nutzlasten zurueck."""
        zustellung = _Zustellung()
        graph = MagicMock()

        with patch.object(ec_mod, "broadcast", zustellung), \
             patch.object(ec_mod, "_graph_streamen", return_value=ergebnis):
            await ec_mod._event_verarbeiten(
                event            = event,
                user_id          = "meister",
                character_id     = "nova",
                redis_client     = MagicMock(),
                character_graph  = graph,
                compiled_character = MagicMock(),
                websocket_map    = {"meister": ["ws"]},
                llm_lock         = MagicMock(),
            )

        return zustellung.nutzlasten


class AntwortNenntIhrenReizTest(_EventVerarbeitenLauf):
    """Der positive Fall: die Zuordnung reist mit."""

    async def test_antwort_traegt_die_turn_id_des_reizes(self) -> None:
        """Der Kernfall: die Antwort nennt den Reiz, den sie beantwortet."""
        nutzlasten: list[dict] = await self._zustellen(_event(), _graph_ergebnis())

        self.assertEqual(len(nutzlasten), 1)
        self.assertEqual(nutzlasten[0]["turn_id"], REIZ_TURN_ID)

    async def test_nicht_die_kennung_aus_dem_ergebnis_zustand(self) -> None:
        """Die naheliegende falsche Quelle liegt im selben Griffbereich."""
        nutzlasten: list[dict] = await self._zustellen(_event(), _graph_ergebnis())

        self.assertNotEqual(nutzlasten[0]["turn_id"], STATE_TURN_ID)

    async def test_zuordnung_ueberlebt_die_json_runde(self) -> None:
        """Die Nutzlast reist als JSON — geprueft wird das, was ankommt."""
        nutzlasten: list[dict] = await self._zustellen(_event(), _graph_ergebnis())

        wieder: dict = json.loads(json.dumps(nutzlasten[0], ensure_ascii=False))
        self.assertEqual(wieder["turn_id"], REIZ_TURN_ID)

    async def test_ein_eigener_impuls_traegt_seine_eigene_kennung(self) -> None:
        """Ein Impuls beantwortet keine Frage, hat aber einen eigenen Turn."""
        event: dict = _event(turn_id="impuls-9c3d", reiz_herkunft="eigener_impuls")

        nutzlasten: list[dict] = await self._zustellen(event, _graph_ergebnis())

        self.assertEqual(nutzlasten[0]["turn_id"], "impuls-9c3d")
        self.assertEqual(nutzlasten[0]["reiz_herkunft"], "eigener_impuls")


class FehlendeZuordnungWirdLautTest(_EventVerarbeitenLauf):
    """Leer ist nicht dasselbe wie unbekannt — und keins von beidem ist still."""

    async def test_fehlende_turn_id_wird_als_fehler_gemeldet(self) -> None:
        """Ein Event ohne Kennung ist ein Defekt und wird nicht verschwiegen."""
        with self.assertLogs(CONSUMER_LOGGER, level="ERROR") as protokoll:
            await self._zustellen(_event(turn_id=""), _graph_ergebnis())

        meldungen: str = "\n".join(protokoll.output)
        self.assertIn("turn_id", meldungen)

    async def test_fehlende_turn_id_wird_nicht_erfunden(self) -> None:
        """Ein Platzhalter waere schlimmer als die Luecke: er sieht gueltig aus."""
        nutzlasten: list[dict] = await self._zustellen(_event(turn_id=""), _graph_ergebnis())

        self.assertEqual(nutzlasten[0]["turn_id"], "")

    async def test_die_antwort_wird_trotzdem_zugestellt(self) -> None:
        """Der Turn zu verwerfen kostet mehr als die fehlende Zuordnung."""
        nutzlasten: list[dict] = await self._zustellen(_event(turn_id=""), _graph_ergebnis())

        self.assertEqual(len(nutzlasten), 1)
        self.assertTrue(nutzlasten[0]["nachricht"])

    async def test_ohne_antwort_wird_der_ausfall_zugestellt(self) -> None:
        """Ein gescheiterter Turn meldet sich — er stellt keine Antwort zu, aber auch keine Stille.

        **Diese Zusicherung ist am 25.08.2026 umgedreht worden, nicht
        geloescht** (`20_TESTS/zusicherung-umdrehen.md`). Sie lautete
        *„ohne Antwort wird nichts zugestellt"* und hielt damit den Defekt
        fest: Der Server wusste vom Ausfall, der Mensch nicht. Der Client
        blieb auf der letzten Stufenmeldung stehen, die Eingabe wurde
        freigegeben — von einem Haenger nicht zu unterscheiden.

        Was bleibt: **keine Antwort.** Was neu ist: eine Meldung darueber.
        Der Typ ist ausdruecklich ein anderer, damit der Ausfall nicht als
        Aeusserung Novas erscheint.
        """
        nutzlasten: list[dict] = await self._zustellen(_event(), _graph_ergebnis(response=""))

        self.assertEqual(len(nutzlasten), 1)
        self.assertEqual(nutzlasten[0]["typ"], "turn_gescheitert")
        self.assertNotEqual(
            nutzlasten[0]["typ"], "character_response",
            "ein Ausfall darf nicht wie eine Antwort aussehen",
        )
        self.assertTrue(nutzlasten[0]["nachricht"], "die Meldung ist leer")


class BestaetigungNenntDieNachrichtTest(unittest.TestCase):
    """Der Endpunkt sagt dem Client, welche Kennung seine Aeusserung bekam.

    Ohne sie hat der Client nichts, wogegen er die ankommende Antwort halten
    koennte — die Zuordnung in der Antwort allein reicht nicht. Es ist die
    Kennung der **Nachricht**, nicht die des Turns: Der Turn entsteht erst im
    Prompt-Consumer und kann mehrere Aeusserungen umfassen.
    """

    def test_bestaetigung_traegt_die_nachrichten_id(self) -> None:
        """Der Client braucht die Kennung seiner eigenen Aeusserung."""
        nutzlast: dict = chat_mod._bestaetigungs_nutzlast(NACHRICHT_ID)

        self.assertEqual(nutzlast["nachrichten_id"], NACHRICHT_ID)

    def test_bestaetigung_traegt_weiterhin_den_status(self) -> None:
        """Charakterisierung: der Vertrag, den der Client heute liest."""
        nutzlast: dict = chat_mod._bestaetigungs_nutzlast(NACHRICHT_ID)

        self.assertEqual(nutzlast["status"], "processing")
        self.assertIn("WebSocket", nutzlast["nachricht"])

    def test_keine_perzeptionswerte_mehr(self) -> None:
        """Der Endpunkt rechnet nicht — er darf nichts behaupten, was er nicht weiss."""
        nutzlast: dict = chat_mod._bestaetigungs_nutzlast(NACHRICHT_ID)

        self.assertNotIn("emotion", nutzlast)
        self.assertNotIn("arousal", nutzlast)

    def test_leere_kennung_wird_gemeldet_und_nicht_erfunden(self) -> None:
        """Ein Platzhalter saehe gueltig aus."""
        with self.assertLogs("ki_server.chat", level="ERROR"):
            nutzlast: dict = chat_mod._bestaetigungs_nutzlast("")

        self.assertEqual(nutzlast["nachrichten_id"], "")


class BeideEndpunkteRufenDenBauerTest(unittest.TestCase):
    """Die Verdrahtung ist der Zeuge — ein Endpunkt, der selbst baut, driftet.

    Geprueft wird ueber den Syntaxbaum, ob der Aufruf da ist. Ein Grep faende
    auch den Docstring; eine gefahrene Anfrage kostet den halben Server.
    """

    def _gerufene_namen(self, funktionsname: str) -> set[str]:
        baum: ast.Module = ast.parse(inspect.getsource(chat_mod))

        for knoten in ast.walk(baum):
            ist_funktion: bool = isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef))
            if ist_funktion and knoten.name == funktionsname:
                return {
                    ruf.func.id
                    for ruf in ast.walk(knoten)
                    if isinstance(ruf, ast.Call) and isinstance(ruf.func, ast.Name)
                }

        self.fail(f"Funktion '{funktionsname}' nicht gefunden")
        return set()

    def test_synchroner_endpunkt_ruft_den_bauer(self) -> None:
        """Der synchrone Pfad baut die Bestaetigung nicht mehr selbst."""
        self.assertIn("_bestaetigungs_nutzlast", self._gerufene_namen("chat_senden"))

    def test_streamender_endpunkt_ruft_den_bauer(self) -> None:
        """Der streamende Pfad ebenso — er ist der, den der Client benutzt."""
        self.assertIn("_bestaetigungs_nutzlast", self._gerufene_namen("event_generator"))

    def test_der_bauer_wird_nicht_an_dritter_stelle_nachgebaut(self) -> None:
        """Positiver Zwilling: genau zwei Aufrufer, nicht null und nicht drei."""
        baum: ast.Module = ast.parse(inspect.getsource(chat_mod))

        aufrufe: int = sum(
            1
            for knoten in ast.walk(baum)
            if isinstance(knoten, ast.Call)
            and isinstance(knoten.func, ast.Name)
            and knoten.func.id == "_bestaetigungs_nutzlast"
        )

        self.assertEqual(aufrufe, 2)


if __name__ == "__main__":
    unittest.main()
