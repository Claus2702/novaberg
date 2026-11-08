"""Tests: Das Verteilen einer Aeusserung haelt die Event-Schleife nicht an.

`_block_verarbeiten` ist eine Coroutine und rief `broadcast_threadsafe` direkt.
Das stellt die Zustellung in die Schleife ein und wartet mit einer Frist auf sie
— auf der Schleife, auf der es selbst steht. Die Coroutine kam erst dran, wenn
die Frist abgelaufen war: Bis dahin lief dort nichts, sobald ein zweiter Client
des Nutzers verbunden war, und die Warnung nannte die Auslastung als Grund.

Zeugen dieser Datei:
  * **Echte Schleife, echte Zustellung.** Ersetzt ist nur der Socket. Ein
    ersetzter Broadcast saehe das Warten nicht, denn es entsteht erst darin.
  * **Der Stillstand wird gemessen,** von einer parallelen Coroutine, die tickt.
    Steht die Schleife, steht auch sie.
  * **Beide Seiten der Abweisung.** Auf der eigenen Schleife scheitert der
    Aufruf; aus einem Thread und von einer fremden Schleife gelingt er.
  * **Das Warten im Thread bleibt.** Die Warnung, die auf der Schleife nicht
    mehr entstehen darf, entsteht dort weiter — sonst sagte ihr Ausbleiben nichts.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import asyncio
import json
import logging
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import services.prompt_consumer as consumer
from api import websocket as ws

USER: str = "user-broadcast"
CHARACTER: str = "nova"
TURN: str = "t-broadcast"
UTTERANCE: str = "Wie entstehen die Ringe des Saturn?"
PAYLOAD: str = '{"typ": "character_response", "nachricht": "…"}'
SENDER: str = "desktop"
OTHER: str = "telegram"

# Wortlaut der Warnung, die eine abgelaufene Frist meldet.
DEADLINE_LINE: str = "nicht innerhalb von"
# Takt und groesste erlaubte Luecke der parallelen Coroutine, in Sekunden.
TICK: float = 0.05
MAX_GAP: float = 0.5
# Obergrenze fuer eine Abweisung, in Sekunden.
MAX_REFUSAL: float = 0.1

BLOCK: list[dict] = [{
    "nachrichten_id": "n-1",
    "prompt":         UTTERANCE,
    "empfangen_am":   1_754_000_000.0,
    "client_id":      SENDER,
}]


class RecordingSocket:
    """Socket-Doppel: Es haelt fest, was gesendet wurde."""

    def __init__(self) -> None:
        """Beginnt ohne gesendete Nachricht."""
        self.sent: list[str] = []

    async def send_text(self, text: str) -> None:
        """Nimmt eine Nachricht an."""
        self.sent.append(text)

    def utterances(self) -> list[str]:
        """Die Texte der gesendeten Aeusserungen, ohne Stufenmeldungen."""
        messages: list[dict] = [json.loads(text) for text in self.sent]
        return [m["nachricht"] for m in messages if m["typ"] == "user_message"]


class HeldSocket(RecordingSocket):
    """Socket-Doppel, dessen Senden wartet, bis der Zeuge es freigibt."""

    def __init__(self) -> None:
        """Beginnt gesperrt."""
        super().__init__()
        self.release: asyncio.Event = asyncio.Event()
        self.done: asyncio.Event = asyncio.Event()

    async def send_text(self, text: str) -> None:
        """Nimmt eine Nachricht erst nach der Freigabe an."""
        await self.release.wait()
        await super().send_text(text)
        self.done.set()


class LineCollector(logging.Handler):
    """Sammelt Protokollzeilen, auch aus Worker-Threads."""

    def __init__(self) -> None:
        """Beginnt ohne Zeile."""
        super().__init__(level=logging.WARNING)
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Haelt den Text einer Zeile fest."""
        self.lines.append(record.getMessage())

    def deadline_lines(self) -> list[str]:
        """Die Zeilen, die eine abgelaufene Frist melden."""
        return [line for line in self.lines if DEADLINE_LINE in line]


def _state() -> dict:
    """Baut einen Pfad-1-Zustand mit gefuellter Perzeption."""
    return {
        "external": SimpleNamespace(emotion=SimpleNamespace(
            emotion="neugierig", arousal=0.6, mode="fachgespraech",
            intent="knowledge", tone="sachlich", language_style="fachlich",
            relationship_dynamic="vertrauen", emotions_vector="plateau",
            prompt_topic="Saturnringe",
        )),
        "salienz_human":    0.7,
        "user_intentionen": ["information_erfragen"],
    }


class ConnectionCase(unittest.IsolatedAsyncioTestCase):
    """Gemeinsamer Rahmen: leere Verbindungsliste und mitgeschriebenes Protokoll."""

    def setUp(self) -> None:
        """Beginnt ohne Verbindung; der Zustand ist global."""
        ws.aktive_verbindungen.clear()
        self.addCleanup(ws.aktive_verbindungen.clear)

        self.log: LineCollector = LineCollector()
        logger: logging.Logger = logging.getLogger("ki_server.websocket")
        logger.addHandler(self.log)
        self.addCleanup(logger.removeHandler, self.log)

    def connect(self, client_id: str, socket: RecordingSocket | None = None) -> RecordingSocket:
        """Meldet einen Client des Nutzers an und gibt seinen Socket zurueck."""
        used: RecordingSocket = socket if socket is not None else RecordingSocket()
        ws.aktive_verbindungen.setdefault(USER, []).append(
            ws.ClientConnection(client_id=client_id, character_id=CHARACTER, websocket=used),
        )
        return used


class RefusalOnOwnLoopTest(ConnectionCase):
    """`broadcast_threadsafe` scheitert auf der eigenen Schleife, sonst nirgends."""

    async def test_call_on_own_loop_fails_fast_and_loud(self) -> None:
        """Der Aufruf scheitert sofort mit Grund, statt bis zur Frist zu warten."""
        socket: RecordingSocket = self.connect(OTHER)

        started: float = time.monotonic()
        with self.assertLogs("ki_server.websocket", level="ERROR"), \
             self.assertRaises(RuntimeError) as refused:
            ws.broadcast_threadsafe(USER, PAYLOAD, asyncio.get_running_loop())
        elapsed: float = time.monotonic() - started

        self.assertLess(elapsed, MAX_REFUSAL)
        self.assertIn("asyncio.to_thread", str(refused.exception))
        self.assertEqual([], socket.sent)

    async def test_refusal_needs_no_connection(self) -> None:
        """Der falsche Aufrufer faellt auch auf, solange niemand verbunden ist."""
        with self.assertLogs("ki_server.websocket", level="ERROR"), \
             self.assertRaises(RuntimeError):
            ws.broadcast_threadsafe(USER, PAYLOAD, asyncio.get_running_loop())

    async def test_call_from_worker_thread_delivers(self) -> None:
        """Der Zwilling: Aus `asyncio.to_thread` wird zugestellt, ohne Warnung."""
        socket: RecordingSocket = self.connect(OTHER)

        await asyncio.to_thread(
            ws.broadcast_threadsafe, USER, PAYLOAD, asyncio.get_running_loop(),
        )

        self.assertEqual([PAYLOAD], socket.sent)
        self.assertEqual([], self.log.deadline_lines())

    async def test_foreign_running_loop_is_allowed(self) -> None:
        """Abgewiesen wird die eigene Schleife, nicht jede laufende.

        Die Zielschleife laeuft in einem eigenen Thread und wird vom Warten des
        Aufrufers nicht beruehrt.
        """
        socket: RecordingSocket = self.connect(OTHER)
        target: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        runner: threading.Thread = threading.Thread(target=target.run_forever, daemon=True)
        runner.start()

        try:
            ws.broadcast_threadsafe(USER, PAYLOAD, target)
        finally:
            target.call_soon_threadsafe(target.stop)
            runner.join(timeout=5.0)
            target.close()

        self.assertEqual([PAYLOAD], socket.sent)

    async def test_wait_in_worker_thread_still_ends_in_the_warning(self) -> None:
        """Im Thread bleibt alles: Warnung, Verbindung und weiterlaufende Zustellung.

        Der Zwilling zur Zusicherung, dass die Warnung auf der Schleife ausbleibt.
        """
        socket: HeldSocket = HeldSocket()
        self.connect(OTHER, socket)

        with patch.object(ws, "SEND_TIMEOUT", 0.05):
            await asyncio.to_thread(
                ws.broadcast_threadsafe, USER, PAYLOAD, asyncio.get_running_loop(),
            )

        self.assertEqual(1, len(self.log.deadline_lines()))
        self.assertEqual(1, len(ws.aktive_verbindungen[USER]))
        self.assertEqual([], socket.sent)

        socket.release.set()
        await asyncio.wait_for(socket.done.wait(), timeout=5.0)

        self.assertEqual([PAYLOAD], socket.sent)


class BlockDistributionTest(ConnectionCase):
    """`_block_verarbeiten` verteilt die Aeusserung, ohne die Schleife anzuhalten."""

    async def _run_block(self, event: MagicMock) -> None:
        """Faehrt einen Block mit echter Zustellung; ersetzt ist die Umgebung."""
        graph: MagicMock = MagicMock()
        graph.stream.return_value = iter([{"perzeption": _state()}])

        with patch.object(consumer, "event_erzeugen", event), \
             patch.object(consumer, "redis_client", MagicMock()), \
             patch.object(consumer, "shadow_burst_reset", MagicMock()), \
             patch.object(consumer, "_audit_log", MagicMock()), \
             patch.object(consumer, "turn_beenden", MagicMock()):
            await consumer._block_verarbeiten(
                BLOCK, (USER, CHARACTER), TURN,
                MagicMock(create_state=MagicMock(return_value={})),
                graph,
            )

    async def test_loop_keeps_ticking_while_the_second_client_gets_it(self) -> None:
        """Das ZIEL: Der zweite Client hat die Aeusserung, und die Schleife lief weiter."""
        self.connect(SENDER)
        other: RecordingSocket = self.connect(OTHER)

        gaps: list[float] = []
        stop: asyncio.Event = asyncio.Event()

        async def tick() -> None:
            """Misst die Abstaende, in denen die Schleife an die Reihe kommt."""
            last: float = time.monotonic()
            while not stop.is_set():
                await asyncio.sleep(TICK)
                now: float = time.monotonic()
                gaps.append(now - last)
                last = now

        ticker: asyncio.Task = asyncio.create_task(tick())
        await self._run_block(MagicMock())
        stop.set()
        await ticker

        self.assertGreater(len(gaps), 0)
        self.assertLess(max(gaps), MAX_GAP)
        self.assertEqual([UTTERANCE], other.utterances())
        self.assertEqual([], self.log.deadline_lines())

    async def test_utterance_is_out_before_the_event_exists(self) -> None:
        """Die Antwort kann die Aeusserung nicht ueberholen: Ihr Ereignis kommt danach."""
        self.connect(SENDER)
        other: RecordingSocket = self.connect(OTHER)
        seen_at_event: list[list[str]] = []

        def event(**_: object) -> None:
            """Haelt fest, was der zweite Client beim Entstehen des Ereignisses hat."""
            seen_at_event.append(other.utterances())

        await self._run_block(MagicMock(side_effect=event))

        self.assertEqual([[UTTERANCE]], seen_at_event)

    async def test_only_a_second_client_causes_a_delivery(self) -> None:
        """Ohne zweiten Client kein Aufruf, mit ihm genau einer."""
        sender: RecordingSocket = self.connect(SENDER)

        with patch.object(consumer, "_stufe_senden", MagicMock()), \
             patch.object(
                 ws.asyncio, "run_coroutine_threadsafe",
                 wraps=asyncio.run_coroutine_threadsafe,
             ) as delivery:
            await self._run_block(MagicMock())
            alone: int = delivery.call_count

            self.connect(OTHER)
            await self._run_block(MagicMock())

        self.assertEqual(0, alone)
        self.assertEqual(1, delivery.call_count)
        self.assertEqual([], sender.utterances())

    async def test_failed_delivery_costs_no_turn(self) -> None:
        """Ein misslungener Broadcast kostet eine Anzeige; das Ereignis entsteht."""
        event: MagicMock = MagicMock()

        with patch.object(consumer, "_stufe_senden", MagicMock()), \
             patch.object(
                 consumer, "broadcast_threadsafe", MagicMock(side_effect=OSError("Leitung tot")),
             ), \
             self.assertLogs("ki_server.prompt_consumer", level="WARNING"):
            await self._run_block(event)

        event.assert_called_once()


if __name__ == "__main__":
    unittest.main()
