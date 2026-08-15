"""Tests: Eine verworfene Verbindung erfaehrt davon, und ein Warten verwirft keine.

Am 14.08.2026 war der Telegram-Client elfeinhalb Stunden lang vom Server
abgemeldet, ohne es zu wissen. Dreimal — 21:19:56, 22:02:43, 22:24:24 UTC —
stand im Serverlog dieselbe Zeile, jedes Mal **mit leerem Fehlertext**:

    WebSocket-Send (threadsafe) fehlgeschlagen fuer 'meister' (client=telegram):
    Kaputte Verbindung (threadsafe) entfernt: 'meister' (client=telegram)

Zwei Defekte in einer Zeile:

**Erstens war die Verbindung nicht kaputt.** Der leere Text stammt von einem
`concurrent.futures.TimeoutError` — `str()` darauf ist die leere Zeichenkette.
Die Frist von 5 s lief ab, weil der Haupt-Loop mit einem Turn beschaeftigt war;
die Zustellung selbst gelang **14 bis 23 ms spaeter**, belegt durch das
Client-Log der Gegenseite. Die Frist misst die Auslastung des Loops, nicht die
Gesundheit der Leitung.

**Zweitens erfuhr die Gegenseite nichts davon.** Die Verbindung wurde aus der
Liste genommen, der Socket aber nie geschlossen. Fuer den Client blieb alles
gesund — sein Keepalive bekam weiter Antworten, denn die kommen aus der
Protokollschicht, nicht aus der Anwendung. Er wartete auf einer Leitung, die
niemand mehr bediente, und erreichte seinen Reconnect-Pfad nie.

Zeugen dieser Datei:
  * **Beide Richtungen.** Dass ein Timeout die Verbindung stehen laesst, ist
    erst eine Aussage, wenn ein echter Fehler sie verwirft — sonst waere auch
    eine Funktion gruen, die nie etwas verwirft.
  * **Der Zeuge sitzt an der Schicht, die handelt.** Geprueft wird
    `api.websocket`, wo entfernt und geschlossen wird, nicht ein Aufrufer
    darueber.
  * **Die Zustellung wird beim Timeout nicht abgebrochen.** Die Coroutine liegt
    im Loop und laeuft dort weiter; ein `cancel()` wuerde genau die Nachricht
    verwerfen, die gerade unterwegs ist.
  * **Der Ausnahmetyp steht in der Meldung.** Der urspruengliche Defekt war
    zwei Monate lang unsichtbar, weil die Zeile ihn nicht nannte.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import concurrent.futures
import unittest
from collections.abc import Callable
from unittest.mock import AsyncMock, MagicMock, patch

from api import websocket as ws

USER: str = "meister"
NACHRICHT: str = '{"typ": "character_response", "nachricht": "…"}'


def _verbindung(client_id: str = "telegram") -> ws.ClientConnection:
    """Eine Verbindung, deren Socket sich beobachten laesst."""
    return ws.ClientConnection(
        client_id=client_id,
        character_id="nova",
        websocket=AsyncMock(),
    )


def _einstellen(fehler: BaseException | None = None) -> Callable[..., MagicMock]:
    """Ersetzt run_coroutine_threadsafe: schliesst die Coroutine, liefert einen Future.

    Die uebergebene Coroutine wird geschlossen, damit kein „never awaited"
    zurueckbleibt. `fehler` wird beim Warten auf das Ergebnis geworfen.
    """
    def _fake(coro: object, loop: object) -> MagicMock:
        coro.close()
        future = MagicMock()
        if fehler is not None:
            future.result.side_effect = fehler
        return future

    return _fake


class TimeoutVerwirftKeineVerbindungTest(unittest.TestCase):
    """Die abgelaufene Frist ist eine Aussage ueber den Loop, nicht ueber die Leitung."""

    def setUp(self) -> None:
        """Beginnt mit leerer Verbindungsliste — der Zustand ist global."""
        ws.aktive_verbindungen.clear()

    def tearDown(self) -> None:
        """Laesst keine Verbindung fuer den naechsten Test stehen."""
        ws.aktive_verbindungen.clear()

    def test_timeout_laesst_die_verbindung_stehen(self) -> None:
        """Die Frist lief ab, die Leitung ist gesund — sie bleibt in der Liste."""
        conn = _verbindung()
        ws.aktive_verbindungen[USER] = [conn]

        with patch.object(
            ws.asyncio, "run_coroutine_threadsafe",
            side_effect=_einstellen(concurrent.futures.TimeoutError()),
        ):
            ws.broadcast_threadsafe(USER, NACHRICHT, MagicMock())

        self.assertIn(conn, ws.aktive_verbindungen.get(USER, []))

    def test_timeout_stellt_kein_schliessen_ein(self) -> None:
        """Nur der Send wird eingestellt — kein zweiter Aufruf fuer das Schliessen."""
        ws.aktive_verbindungen[USER] = [_verbindung()]

        with patch.object(
            ws.asyncio, "run_coroutine_threadsafe",
            side_effect=_einstellen(concurrent.futures.TimeoutError()),
        ) as eingestellt:
            ws.broadcast_threadsafe(USER, NACHRICHT, MagicMock())

        self.assertEqual(1, eingestellt.call_count)

    def test_timeout_bricht_die_zustellung_nicht_ab(self) -> None:
        """Die Coroutine liegt im Loop und soll dort zu Ende laufen."""
        ws.aktive_verbindungen[USER] = [_verbindung()]
        futures: list[MagicMock] = []

        def _sammelnd(coro: object, loop: object) -> MagicMock:
            coro.close()
            future = MagicMock()
            future.result.side_effect = concurrent.futures.TimeoutError()
            futures.append(future)
            return future

        with patch.object(ws.asyncio, "run_coroutine_threadsafe", side_effect=_sammelnd):
            ws.broadcast_threadsafe(USER, NACHRICHT, MagicMock())

        self.assertEqual(1, len(futures))
        futures[0].cancel.assert_not_called()


class EchterFehlerVerwirftUndSchliesstTest(unittest.TestCase):
    """Der positive Zwilling: Was wirklich kaputt ist, wird verworfen und geschlossen."""

    def setUp(self) -> None:
        """Beginnt mit leerer Verbindungsliste — der Zustand ist global."""
        ws.aktive_verbindungen.clear()

    def tearDown(self) -> None:
        """Laesst keine Verbindung fuer den naechsten Test stehen."""
        ws.aktive_verbindungen.clear()

    def test_sendefehler_entfernt_die_verbindung(self) -> None:
        """Ein echter Sendefehler nimmt die Verbindung aus der Liste."""
        ws.aktive_verbindungen[USER] = [_verbindung()]

        with patch.object(
            ws.asyncio, "run_coroutine_threadsafe",
            side_effect=_einstellen(RuntimeError("Leitung tot")),
        ):
            ws.broadcast_threadsafe(USER, NACHRICHT, MagicMock())

        self.assertEqual([], ws.aktive_verbindungen.get(USER, []))

    def test_sendefehler_stellt_das_schliessen_ein(self) -> None:
        """Zwei Aufrufe: der Send und das Schliessen der verworfenen Leitung."""
        ws.aktive_verbindungen[USER] = [_verbindung()]

        with patch.object(
            ws.asyncio, "run_coroutine_threadsafe",
            side_effect=_einstellen(RuntimeError("Leitung tot")),
        ) as eingestellt:
            ws.broadcast_threadsafe(USER, NACHRICHT, MagicMock())

        self.assertEqual(2, eingestellt.call_count)


class SocketWirdGeschlossenTest(unittest.IsolatedAsyncioTestCase):
    """Der async-Pfad schliesst den Socket, damit die Gegenseite reconnecten kann."""

    def setUp(self) -> None:
        """Beginnt mit leerer Verbindungsliste — der Zustand ist global."""
        ws.aktive_verbindungen.clear()

    def tearDown(self) -> None:
        """Laesst keine Verbindung fuer den naechsten Test stehen."""
        ws.aktive_verbindungen.clear()

    async def test_sendefehler_schliesst_den_socket(self) -> None:
        """Ohne close() bliebe die Gegenseite auf einer toten Leitung stehen."""
        conn = _verbindung()
        conn.websocket.send_text.side_effect = RuntimeError("Leitung tot")
        ws.aktive_verbindungen[USER] = [conn]

        await ws.broadcast(USER, NACHRICHT)

        conn.websocket.close.assert_awaited_once()

    async def test_gesunde_verbindung_wird_nicht_geschlossen(self) -> None:
        """Der positive Zwilling: Wer zustellt, bleibt verbunden."""
        conn = _verbindung()
        ws.aktive_verbindungen[USER] = [conn]

        await ws.broadcast(USER, NACHRICHT)

        conn.websocket.close.assert_not_awaited()
        self.assertIn(conn, ws.aktive_verbindungen.get(USER, []))


class MeldungNenntDenAusnahmetypTest(unittest.IsolatedAsyncioTestCase):
    """Ein Fehler ohne Typ und Text ist zwei Monate lang niemandem aufgefallen."""

    def setUp(self) -> None:
        """Beginnt mit leerer Verbindungsliste — der Zustand ist global."""
        ws.aktive_verbindungen.clear()

    def tearDown(self) -> None:
        """Laesst keine Verbindung fuer den naechsten Test stehen."""
        ws.aktive_verbindungen.clear()

    async def test_typ_steht_in_der_warnung(self) -> None:
        """Die Meldung nennt den Ausnahmetyp, nicht nur einen (womoeglich leeren) Text."""
        conn = _verbindung()
        conn.websocket.send_text.side_effect = RuntimeError("Leitung tot")
        ws.aktive_verbindungen[USER] = [conn]

        with self.assertLogs("ki_server.websocket", level="WARNING") as protokoll:
            await ws.broadcast(USER, NACHRICHT)

        self.assertIn("RuntimeError", "\n".join(protokoll.output))


if __name__ == "__main__":
    unittest.main()
