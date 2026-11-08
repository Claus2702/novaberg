"""Zeugen: Faellt eine GV4-Quelle aus, ist das von *keine Knoten gefunden* unterscheidbar.

Ziel: Ein Ausfall von LZG, KZG oder Einbettung steht als Fehler im Log und wird an
das Pipeline-Protokoll gegeben, und nur ein Lauf ohne Ausfall meldet *„GV4: Keine
Knoten gefunden"*. Die Suche der anderen Quelle laeuft weiter; ihr Ergebnis zaehlt
aber nur bei warmem Zwischenspeicher der Gewichte (Frist
`GV_GEWICHT_VERTEILUNG_TTL_S`, 600 s). Beim echten
Datenbankausfall kann das Pipeline-Protokoll nicht schreiben, dann steht der Fehler
nur im Log. Beides bilden diese Zeugen nicht: Sie ersetzen die Gewichte und
`log_fehler`. Bis dahin fingen die beiden Suchen jede Ausnahme, schrieben eine
Warnung und gaben eine leere Liste zurueck: Ein Ausfall sah aus wie ein Gespraech
ohne Luecken.

**Ersetzt wird an der Grenze zum Speicher** (`psycopg2.connect`,
`redis_client_bytes.execute_command`), nicht an den Suchen. Nur so laeuft der echte
Rumpf der Suchen mit, und eine Suche, die wieder selbst faengt, wird rot.

Ein Programmierfehler ist kein Ausfall: `AProgrammingErrorIsNoOutage` verlangt, dass
er durchgeht. Alles andere aus der Einbettung zaehlt als Ausfall (`EmbeddingFails`).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import math
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import ollama
import psycopg2
import psycopg2.errors
import pydantic
import redis

from ei.gap_topics import UserTopics
from ei.wissensluecken import (
    _report_outage,
    _search_sources,
    kzg_kandidaten_suchen,
    lzg_kandidaten_suchen,
    wissensluecken_finden,
)

LOGGER: str = "ki_server.ei.wissensluecken"
NO_NODES: str = "GV4: Keine Knoten gefunden"
OWN_LINE: str = "GV4: Keine Luecken in diesem Turn"

TURN: list[float] = [1.0] + [0.0] * 7
LZG_TOPIC: str = "Rotation eines Pulsars"
KZG_TOPIC: str = "Gezeitenverformung dichter Materie"
#: Beide Quellen mit Rang 0,8 fuer die Gewichte unten — genug fuer die Untergrenze.
WEIGHTS: dict[str, list[float]] = {
    "lzg": [3.0, 3.2, 3.5, 3.8, 4.0, 5.0, 7.0, 8.0, 9.5, 10.0],
    "kzg": [0.45, 0.7, 0.85, 0.9, 0.95, 0.97, 0.98, 0.99, 1.0, 1.0],
}

LZG_ROW: tuple = ("Nova hat die Rotation erklaert", 0.6, 8.0, 0.3, [LZG_TOPIC])
KZG_REPLY: list = [1, b"kzg:a", [
    b"inhalt", b"Nova hat Gezeitenkraefte beschrieben", b"salienz", b"0.99",
    b"arousal", b"0.3", b"score", b"0.4", b"themen", KZG_TOPIC.encode(),
]]
KZG_EMPTY: list = [0]


def state(**more: object) -> dict:
    """Ein Turn, wie ihn die Lueckensuche liest, ohne Kern."""
    base: dict = {
        "user_prompt": "Ein Reiz ueber Neutronensterne", "user_id": "mensch",
        "character_id": "figur", "prompt_embedding": TURN, "internal": None,
        "session_turns": [], "turn_id": "t-ausfall",
    }
    base.update(more)
    return base


def topic_vector() -> list[float]:
    """Ein Themenvektor mit Naehe 0,6 zum Turn."""
    return [0.6, math.sqrt(1.0 - 0.36)] + [0.0] * 6


def connection(rows: list[tuple]) -> MagicMock:
    """Eine Verbindung, deren Cursor `rows` liefert."""
    conn: MagicMock = MagicMock()
    conn.cursor.return_value.fetchall.return_value = rows
    return conn


def rejecting_connection(error: Exception) -> MagicMock:
    """Eine Verbindung, die steht, deren Abfrage aber mit `error` abgewiesen wird."""
    conn: MagicMock = connection([])
    conn.cursor.return_value.execute.side_effect = error
    return conn


def double(outcome: object) -> dict:
    """Die `patch`-Argumente: eine Ausnahme wird geworfen, alles andere zurueckgegeben."""
    return {"side_effect" if isinstance(outcome, Exception) else "return_value": outcome}


@contextmanager
def stores(
    lzg: MagicMock | Exception, kzg: list | Exception,
) -> Iterator[SimpleNamespace]:
    """Ersetzt beide Speicher an ihrer Grenze und alles hinter den Suchen."""
    connect_mock: dict = double(lzg)
    search_mock: dict = double(kzg)
    with patch("ei.wissensluecken.psycopg2.connect", **connect_mock) as connect, \
         patch("ei.wissensluecken.redis_client_bytes.execute_command", **search_mock) as search, \
         patch("ei.wissensluecken.load_weight_distributions", return_value=WEIGHTS), \
         patch("ei.wissensluecken.load_user_topics", return_value=UserTopics(set(), set())), \
         patch("ei.wissensluecken.embed_topics",
               side_effect=lambda topics: {t: topic_vector() for t in topics}), \
         patch("ei.wissensluecken.log_berechnung"), \
         patch("ei.wissensluecken.log_fehler") as protocol:
        yield SimpleNamespace(connect=connect, search=search, protocol=protocol)


class OneSourceFails(unittest.TestCase):
    """Eine Quelle faellt aus: gemeldet, und die andere liefert."""

    def run_finder(self, lzg: MagicMock | Exception, kzg: list | Exception) -> tuple:
        with stores(lzg, kzg) as doubles, self.assertLogs(LOGGER, level="INFO") as logs:
            result = wissensluecken_finden(state(), aufnahmebereitschaft=1.0)
        return result, doubles.protocol, logs.output

    def test_lzg_down_kzg_delivers(self) -> None:
        result, protocol, lines = self.run_finder(
            psycopg2.OperationalError("connection refused"), KZG_REPLY,
        )
        self.assertEqual([k["quelle"] for k in result], ["kzg"])
        self.assertEqual(protocol.call_count, 1)
        self.assertEqual(protocol.call_args.kwargs["inhalt"]["ausgefallen"], "lzg")
        self.assertTrue(any(ln.startswith("ERROR") and "Quelle lzg" in ln for ln in lines), lines)

    def test_kzg_down_lzg_delivers(self) -> None:
        result, protocol, lines = self.run_finder(
            connection([LZG_ROW]), redis.ConnectionError("connection refused"),
        )
        self.assertEqual([k["quelle"] for k in result], ["lzg"])
        self.assertEqual(protocol.call_count, 1)
        self.assertEqual(protocol.call_args.kwargs["inhalt"]["ausgefallen"], "kzg")
        self.assertTrue(any(ln.startswith("ERROR") and "Quelle kzg" in ln for ln in lines), lines)

    def test_redis_timeout_is_an_outage(self) -> None:
        result, protocol, _ = self.run_finder(connection([LZG_ROW]), redis.TimeoutError("frist"))
        self.assertEqual([k["quelle"] for k in result], ["lzg"])
        self.assertEqual(protocol.call_count, 1)

    def test_the_entry_names_turn_pair_and_kind_of_error(self) -> None:
        _, protocol, _ = self.run_finder(psycopg2.OperationalError("weg"), KZG_REPLY)
        call = protocol.call_args.kwargs
        self.assertEqual(call["turn_id"], "t-ausfall")
        self.assertEqual(call["node"], "wissensluecken")
        self.assertEqual(call["quelle"], "user")
        self.assertEqual((call["user_id"], call["character_id"]), ("mensch", "figur"))
        self.assertEqual(call["inhalt"]["fehler_typ"], "OperationalError")
        self.assertEqual(call["inhalt"]["fehler"], "weg")

    def test_one_down_the_other_empty_is_not_no_nodes(self) -> None:
        result, protocol, lines = self.run_finder(
            psycopg2.OperationalError("weg"), KZG_EMPTY,
        )
        self.assertEqual(result, [])
        self.assertEqual(protocol.call_count, 1)
        self.assertTrue(any(OWN_LINE in ln and "lzg" in ln for ln in lines), lines)
        self.assertFalse(any(NO_NODES in ln for ln in lines), lines)

    def test_kzg_down_the_lzg_empty_is_not_no_nodes(self) -> None:
        """Der Spiegel: Auch ein Ausfall des KZG neben leerem LZG heisst nicht *keine Knoten*."""
        result, protocol, lines = self.run_finder(
            connection([]), redis.ConnectionError("weg"),
        )
        self.assertEqual(result, [])
        self.assertEqual(protocol.call_count, 1)
        self.assertTrue(any(OWN_LINE in ln and "kzg" in ln for ln in lines), lines)
        self.assertFalse(any(NO_NODES in ln for ln in lines), lines)


class BothSourcesFail(unittest.TestCase):
    """Beide weg: zwei Eintraege, die eigene Zeile, nicht *keine Knoten*."""

    def setUp(self) -> None:
        down = (psycopg2.OperationalError("weg"), redis.ConnectionError("weg"))
        with stores(*down) as doubles, self.assertLogs(LOGGER, level="INFO") as logs:
            self.result = wissensluecken_finden(state(), aufnahmebereitschaft=1.0)
        self.protocol = doubles.protocol
        self.lines = logs.output

    def test_no_gaps(self) -> None:
        self.assertEqual(self.result, [])

    def test_two_entries_one_per_source(self) -> None:
        sources = [c.kwargs["inhalt"]["ausgefallen"] for c in self.protocol.call_args_list]
        self.assertEqual(sources, ["lzg", "kzg"])

    def test_the_own_line_names_both_and_is_an_error(self) -> None:
        own = [ln for ln in self.lines if OWN_LINE in ln]
        self.assertEqual(len(own), 1, self.lines)
        self.assertTrue(own[0].startswith("ERROR"), own)
        self.assertIn("lzg, kzg", own[0])

    def test_no_nodes_is_not_reported(self) -> None:
        self.assertFalse(any(NO_NODES in ln for ln in self.lines), self.lines)


class EmbeddingFails(unittest.TestCase):
    """Fehlt der Vektor des Turns und faellt die Einbettung aus: ein Eintrag, keine Suche."""

    def run_finder(self, outcome: object) -> tuple:
        with stores(connection([]), KZG_EMPTY) as doubles, \
             patch("ei.wissensluecken.model_service.embed.submit_sync", **double(outcome)), \
             self.assertLogs(LOGGER, level="INFO") as logs:
            result = wissensluecken_finden(state(prompt_embedding=None), aufnahmebereitschaft=1.0)
        return result, doubles, logs.output

    def test_each_kind_of_outage_gives_one_entry(self) -> None:
        outages: list[Exception] = [
            RuntimeError("Worker nicht gestartet"), TimeoutError("frist"),
            ConnectionError("ollama weg"), ollama.ResponseError("modell weg"),
            httpx.ReadTimeout("frist"),
        ]
        for outage in outages:
            with self.subTest(outage=type(outage).__name__):
                result, doubles, lines = self.run_finder(outage)
                self.assertEqual(result, [])
                self.assertEqual(doubles.protocol.call_count, 1)
                inhalt: dict = doubles.protocol.call_args.kwargs["inhalt"]
                self.assertEqual(inhalt["ausgefallen"], "einbettung")
                self.assertTrue(any(ln.startswith("ERROR") for ln in lines), lines)
                self.assertFalse(any(NO_NODES in ln for ln in lines), lines)

    def assert_embedding_outage(self, outcome: object, kind: str) -> None:
        """Ein Eintrag `einbettung` mit `kind`, keine Suche, keine Luecken."""
        result, doubles, lines = self.run_finder(outcome)
        self.assertEqual(result, [])
        self.assertEqual(doubles.protocol.call_count, 1)
        entry: dict = doubles.protocol.call_args.kwargs["inhalt"]
        self.assertEqual((entry["ausgefallen"], entry["fehler_typ"]), ("einbettung", kind))
        doubles.connect.assert_not_called()
        doubles.search.assert_not_called()
        self.assertTrue(any("Quelle einbettung" in ln for ln in lines), lines)

    def test_an_answer_that_is_no_json(self) -> None:
        self.assert_embedding_outage(
            json.JSONDecodeError("Expecting value", "<html>", 0), "JSONDecodeError",
        )

    def test_an_answer_of_the_wrong_shape(self) -> None:
        shape = pydantic.ValidationError.from_exception_data(
            "EmbedResponse", [{"type": "list_type", "loc": ("embeddings",), "input": "kein"}],
        )
        self.assert_embedding_outage(shape, "ValidationError")

    def test_a_request_the_client_refuses(self) -> None:
        self.assert_embedding_outage(ollama.RequestError("must provide a model"), "RequestError")

    def test_an_empty_vector(self) -> None:
        """Der Worker liefert `[]`: Bis dahin wies `_search_sources` ihn ab, der Turn endete."""
        empty = SimpleNamespace(embedding=[], duration_seconds=0.1)
        self.assert_embedding_outage(empty, "ValueError")

    def test_no_search_runs_without_a_vector(self) -> None:
        _, doubles, _ = self.run_finder(RuntimeError("weg"))
        doubles.connect.assert_not_called()
        doubles.search.assert_not_called()

    def test_a_working_embedding_reaches_the_sources(self) -> None:
        """Der Zwilling: Die Einbettung liefert, beide Suchen laufen, kein Eintrag."""
        answer = SimpleNamespace(embedding=TURN, duration_seconds=0.1)
        result, doubles, lines = self.run_finder(answer)
        self.assertEqual(result, [])
        doubles.connect.assert_called_once()
        doubles.search.assert_called_once()
        doubles.protocol.assert_not_called()
        self.assertTrue(any(NO_NODES in ln for ln in lines), lines)


class NoOutage(unittest.TestCase):
    """Der Zwilling aller Abweisungen: Ohne Ausfall bleibt *keine Knoten* eine Auskunft."""

    def test_both_empty_is_info_without_an_entry(self) -> None:
        with stores(connection([]), KZG_EMPTY) as doubles, \
             self.assertLogs(LOGGER, level="INFO") as logs:
            result = wissensluecken_finden(state(), aufnahmebereitschaft=1.0)
        self.assertEqual(result, [])
        doubles.protocol.assert_not_called()
        self.assertTrue(any(ln.startswith("INFO") and NO_NODES in ln for ln in logs.output))
        self.assertFalse(any(OWN_LINE in ln for ln in logs.output), logs.output)
        self.assertFalse(any(ln.startswith("ERROR") for ln in logs.output), logs.output)

    def test_both_deliver_without_an_entry(self) -> None:
        with stores(connection([LZG_ROW]), KZG_REPLY) as doubles:
            result = wissensluecken_finden(state(), aufnahmebereitschaft=1.0)
        self.assertEqual(sorted(k["quelle"] for k in result), ["kzg", "lzg"])
        doubles.protocol.assert_not_called()


class TheSearchesCatchNothing(unittest.TestCase):
    """Die Suchen selbst lassen den Ausfall durch; gefangen wird eine Ebene hoeher."""

    def test_lzg_search_lets_the_outage_through(self) -> None:
        with patch("ei.wissensluecken.psycopg2.connect",
                   side_effect=psycopg2.OperationalError("weg")), \
             self.assertRaises(psycopg2.OperationalError):
            lzg_kandidaten_suchen(TURN, "mensch", "figur")

    def test_kzg_search_lets_the_outage_through(self) -> None:
        with patch("ei.wissensluecken.redis_client_bytes.execute_command",
                   side_effect=redis.ConnectionError("weg")), \
             self.assertRaises(redis.ConnectionError):
            kzg_kandidaten_suchen(TURN, "mensch", "figur")


class TheConnectionIsClosed(unittest.TestCase):
    """Die Verbindung schliesst auf beiden Wegen; die Suche faengt dabei weiter nichts."""

    def test_after_a_failed_statement(self) -> None:
        conn: MagicMock = rejecting_connection(psycopg2.ProgrammingError("abgewiesen"))
        with patch("ei.wissensluecken.psycopg2.connect", return_value=conn), \
             self.assertRaises(psycopg2.ProgrammingError):
            lzg_kandidaten_suchen(TURN, "mensch", "figur")
        conn.close.assert_called_once_with()

    def test_after_a_normal_search(self) -> None:
        conn: MagicMock = connection([LZG_ROW])
        with patch("ei.wissensluecken.psycopg2.connect", return_value=conn):
            nodes = lzg_kandidaten_suchen(TURN, "mensch", "figur")
        self.assertEqual([k["quelle"] for k in nodes], ["lzg"])
        conn.close.assert_called_once_with()


class TheLoopKeepsItsPairs(unittest.TestCase):
    """Die Schleife ueber die Quellen vertauscht nichts, und jeder Tausch ist still.

    Vertauschte Kennungen fragen ein Paar ab, das es nicht gibt: Beide Speicher antworten
    leer, und der Turn meldet *keine Knoten*. Attrappen antworten auf jede Abfrage; deshalb
    liest der erste Zeuge, was am Speicher ankommt, statt das Ergebnis zu pruefen.
    """

    def test_each_search_gets_the_pair_in_its_place(self) -> None:
        conn: MagicMock = connection([LZG_ROW])
        with stores(conn, KZG_REPLY) as doubles:
            wissensluecken_finden(state(), aufnahmebereitschaft=1.0)
        conn.cursor.return_value.execute.assert_called_once()
        sql, params = conn.cursor.return_value.execute.call_args.args
        self.assertLess(sql.index("user_id = %s"), sql.index("character_id = %s"), sql)
        self.assertEqual(params[1:3], ("mensch", "figur"))
        doubles.search.assert_called_once()
        query: str = doubles.search.call_args.args[2]
        self.assertIn("@user_id:{mensch}", query)
        self.assertIn("@character_id:{figur}", query)

    def test_each_source_is_reported_with_its_own_kind_of_error(self) -> None:
        down = (psycopg2.OperationalError("weg"), redis.ConnectionError("weg"))
        with stores(*down) as doubles, self.assertLogs(LOGGER, level="ERROR"):
            wissensluecken_finden(state(), aufnahmebereitschaft=1.0)
        entries: list[dict] = [c.kwargs["inhalt"] for c in doubles.protocol.call_args_list]
        self.assertEqual(
            [(e["ausgefallen"], e["fehler_typ"]) for e in entries],
            [("lzg", "OperationalError"), ("kzg", "ConnectionError")],
        )

    def test_the_kind_of_the_other_source_is_not_caught(self) -> None:
        """Der Fehler der einen Art geht bei der anderen Quelle durch: Das waere ein Codefehler."""
        cases: tuple = (
            (redis.ConnectionError("fremd"), KZG_REPLY, redis.ConnectionError),
            (ValueError("fremd"), KZG_REPLY, ValueError),
            (connection([]), psycopg2.OperationalError("fremd"), psycopg2.OperationalError),
        )
        for lzg, kzg, error in cases:
            with self.subTest(error=error.__name__), stores(lzg, kzg) as doubles:
                with self.assertRaises(error):
                    wissensluecken_finden(state(), aufnahmebereitschaft=1.0)
                doubles.protocol.assert_not_called()


class TheHelpersGuardTheirInput(unittest.TestCase):
    """Die Zusicherungen der beiden Helfer, je mit gueltigem Zwilling."""

    def test_an_unknown_source_is_rejected(self) -> None:
        with patch("ei.wissensluecken.log_fehler") as protocol, \
             self.assertRaises(ValueError):
            _report_outage("hdd", OSError("weg"), state(), "mensch", "figur")
        protocol.assert_not_called()

    def test_a_known_source_is_reported(self) -> None:
        with patch("ei.wissensluecken.log_fehler") as protocol, \
             self.assertLogs(LOGGER, level="ERROR"):
            _report_outage("einbettung", OSError("weg"), state(), "mensch", "figur")
        protocol.assert_called_once()

    def test_an_empty_vector_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _search_sources([], state(), "mensch", "figur")

    def test_a_vector_reaches_both_sources(self) -> None:
        with stores(connection([LZG_ROW]), KZG_REPLY):
            nodes, down = _search_sources(TURN, state(), "mensch", "figur")
        self.assertEqual([k["quelle"] for k in nodes], ["lzg", "kzg"])
        self.assertEqual(down, [])


class AProgrammingErrorIsNoOutage(unittest.TestCase):
    """Was der Code verschuldet, geht durch und wird nicht als Ausfall gemeldet."""

    def assert_passes_through(
        self, error: type[Exception], lzg: MagicMock | Exception, kzg: list | Exception,
    ) -> None:
        with stores(lzg, kzg) as doubles:
            with self.assertRaises(error):
                wissensluecken_finden(state(), aufnahmebereitschaft=1.0)
        doubles.protocol.assert_not_called()

    def test_a_type_error_in_the_lzg_search(self) -> None:
        self.assert_passes_through(TypeError, TypeError("falsch gerufen"), KZG_REPLY)

    def test_a_type_error_in_the_kzg_search(self) -> None:
        self.assert_passes_through(TypeError, connection([]), TypeError("falsch gerufen"))

    def test_a_type_error_in_the_embedding(self) -> None:
        with stores(connection([]), KZG_EMPTY) as doubles, \
             patch("ei.wissensluecken.model_service.embed.submit_sync",
                   side_effect=TypeError("falsch gerufen")):
            with self.assertRaises(TypeError):
                wissensluecken_finden(state(prompt_embedding=None), aufnahmebereitschaft=1.0)
        doubles.protocol.assert_not_called()

    def test_the_other_faults_in_the_embedding(self) -> None:
        """Die Einbettung faengt jede `Exception` — ausser diesen beiden und `TypeError`."""
        for error in (AttributeError, NameError):
            with self.subTest(error=error.__name__), \
                 stores(connection([]), KZG_EMPTY) as doubles, \
                 patch("ei.wissensluecken.model_service.embed.submit_sync",
                       side_effect=error("falsch")):
                with self.assertRaises(error):
                    wissensluecken_finden(state(prompt_embedding=None), aufnahmebereitschaft=1.0)
                doubles.protocol.assert_not_called()

    def test_the_other_faults_of_the_own_code(self) -> None:
        for error in (AttributeError, NameError):
            with self.subTest(error=error.__name__, source="lzg"):
                self.assert_passes_through(error, error("falsch"), KZG_REPLY)
            with self.subTest(error=error.__name__, source="kzg"):
                self.assert_passes_through(error, connection([]), error("falsch"))


class AnUnusableAnswerIsAnOutage(unittest.TestCase):
    """Eine abgewiesene Abfrage oder ein unlesbarer Eintrag beendet den Turn nicht.

    Umgedreht am 07.11.2026. Bis dahin verlangten diese Zeugen, dass all das durchgeht,
    damit es nicht aussieht wie eine Datenbank, die neu startet. Durchgehen hiess aber:
    Ueber dem Knoten faengt nur der Graphlauf, und der Turn endet ohne Antwort. Die
    Trennung vom Neustart traegt
    jetzt `fehler_typ`, und der Fehler im eigenen Code geht weiter durch (Klasse oben).
    """

    def assert_outage(
        self, lzg: MagicMock | Exception, kzg: list | Exception,
        down: str, kind: str, delivering: str,
    ) -> None:
        with stores(lzg, kzg) as doubles, self.assertLogs(LOGGER, level="ERROR") as logs:
            result = wissensluecken_finden(state(), aufnahmebereitschaft=1.0)
        self.assertEqual([k["quelle"] for k in result], [delivering])
        self.assertEqual(doubles.protocol.call_count, 1)
        entry: dict = doubles.protocol.call_args.kwargs["inhalt"]
        self.assertEqual((entry["ausgefallen"], entry["fehler_typ"]), (down, kind))
        self.assertTrue(any(f"Quelle {down}" in ln for ln in logs.output), logs.output)

    def test_a_rejected_sql_statement(self) -> None:
        rejected = psycopg2.ProgrammingError("column does not exist")
        self.assert_outage(
            rejecting_connection(rejected), KZG_REPLY, "lzg", "ProgrammingError", "kzg",
        )

    def test_a_vector_of_another_dimension(self) -> None:
        """Der Treiber wirft die Unterklasse, und `fehler_typ` traegt sie, nicht `DataError`."""
        rejected = psycopg2.errors.DataException("different vector dimensions 1024 and 768")
        self.assertIsInstance(rejected, psycopg2.DataError)
        self.assert_outage(
            rejecting_connection(rejected), KZG_REPLY, "lzg", "DataException", "kzg",
        )

    def test_a_rejected_redis_query(self) -> None:
        rejected = redis.ResponseError("Syntax error at offset 12")
        self.assert_outage(connection([LZG_ROW]), rejected, "kzg", "ResponseError", "lzg")

    def test_a_blob_that_breaks_decoding(self) -> None:
        """Der Fall vom 12.09.2026: Bytes, die kein UTF-8 sind, leeren die Suche nicht mehr."""
        broken: list = [1, b"kzg:a", [b"inhalt", b"\xff\xfe"]]
        self.assert_outage(connection([LZG_ROW]), broken, "kzg", "UnicodeDecodeError", "lzg")

    def test_an_entry_with_an_unreadable_number(self) -> None:
        broken: list = [1, b"kzg:a", [b"inhalt", b"Ein Satz", b"salienz", b"hoch"]]
        self.assert_outage(connection([LZG_ROW]), broken, "kzg", "ValueError", "lzg")


if __name__ == "__main__":
    unittest.main()
