"""Zeugen fuer die Pruefung am Eingang von `ModelWorker.submit_sync`.

Auf der Schleife des Workers scheitert der Aufruf sofort und nennt Worker und
Aufrufer. Aus einem Arbeits-Thread und von einer fremden Schleife liefert er das
Ergebnis. Die Frist ist in den Abweisungen 1 s: Ohne die Pruefung wartet der Aufruf
sie ab und endet mit `TimeoutError`, also rot statt haengend.
"""

from __future__ import annotations

import asyncio
import threading
import time
import unittest
from dataclasses import dataclass

from services.model_services.background_worker import BackgroundWorker
from services.model_services.types import BackgroundRequest
from services.model_services.worker_base import ModelWorker
from tests.services.model_services.fake_provider import FakeProvider

WORKER_LOGGER: str = "services.model_services.worker_base"
SHORT_DEADLINE_S: float = 1.0
LONG_DEADLINE_S: float = 5.0


@dataclass
class _Request:
    """Kleinste Anfrage: ein Text und die Future, die `submit` setzt."""

    text: str
    future: asyncio.Future | None = None


class _EchoWorker(ModelWorker[_Request, str]):
    """Worker ohne Modell: merkt sich die Anfragen und spiegelt ihren Text."""

    def __init__(self) -> None:
        super().__init__(name="witness-worker")
        self.seen: list[str] = []

    async def _call_model(self, request: _Request) -> str:
        self.seen.append(request.text)
        return f"echo:{request.text}"


class _LoopThreadBase(unittest.IsolatedAsyncioTestCase):
    """Startet einen Test-Worker auf der Schleife des Tests."""

    async def asyncSetUp(self) -> None:
        self.worker = _EchoWorker()
        await self.worker.start()

    async def asyncTearDown(self) -> None:
        await self.worker.shutdown()


class SubmitSyncOnWorkerLoopTest(_LoopThreadBase):
    """Die Abweisung: Der Aufruf steht auf der Schleife des Workers."""

    async def test_on_worker_loop_raises_at_once(self) -> None:
        started: float = time.monotonic()
        with self.assertRaises(RuntimeError) as case:
            self.worker.submit_sync(_Request("a"), timeout=SHORT_DEADLINE_S)
        elapsed: float = time.monotonic() - started

        self.assertLess(elapsed, 0.1)
        message: str = str(case.exception)
        self.assertIn("witness-worker", message)
        self.assertIn("test_on_worker_loop_raises_at_once", message)
        self.assertEqual(self.worker._queue.qsize(), 0)
        await asyncio.sleep(0)
        self.assertEqual(self.worker.seen, [])

    async def test_refusal_stands_in_the_log(self) -> None:
        """Der Log traegt sie auch dann, wenn ein Aufrufer `Exception` faengt."""
        with self.assertLogs(WORKER_LOGGER, level="ERROR") as logs:
            with self.assertRaises(RuntimeError) as case:
                self.worker.submit_sync(_Request("a"), timeout=SHORT_DEADLINE_S)

        self.assertEqual([r.getMessage() for r in logs.records], [str(case.exception)])

    async def test_sync_function_between_names_that_function(self) -> None:
        """Ein Aufruf ueber eine sync-Zwischenfunktion nennt die Zwischenfunktion."""

        def embed_helper() -> str:
            return self.worker.submit_sync(_Request("a"), timeout=SHORT_DEADLINE_S)

        with self.assertRaises(RuntimeError) as case:
            embed_helper()

        self.assertIn("embed_helper", str(case.exception))

    async def test_stopped_worker_keeps_its_own_message(self) -> None:
        """Nach `shutdown` steht `_loop` noch: Der Grund bleibt *nicht gestartet*."""
        await self.worker.shutdown()

        with self.assertRaises(RuntimeError) as case:
            self.worker.submit_sync(_Request("a"), timeout=SHORT_DEADLINE_S)

        self.assertIn("nicht gestartet", str(case.exception))


class SubmitSyncSubclassBridgeTest(unittest.IsolatedAsyncioTestCase):
    """Eine Unterklasse mit eigener Bruecke erscheint nicht als Aufrufer."""

    async def test_background_override_is_not_the_caller(self) -> None:
        worker = BackgroundWorker(
            name="witness-background",
            analyse_backend=FakeProvider(contents=["a"]),
            sprache_backend=FakeProvider(contents=["s"]),
        )
        await worker.start()
        self.addAsyncCleanup(worker.shutdown)
        request = BackgroundRequest(
            messages=[{"role": "user", "content": "T"}],
            modus="analyse",
        )

        with self.assertRaises(RuntimeError) as case:
            worker.submit_sync(request, timeout=SHORT_DEADLINE_S)

        message: str = str(case.exception)
        self.assertIn("witness-background", message)
        self.assertIn("test_background_override_is_not_the_caller", message)
        self.assertNotIn("background_worker:", message)


class SubmitSyncAwayFromWorkerLoopTest(_LoopThreadBase):
    """Die Zwillinge: Ausserhalb der Schleife des Workers kommt das Ergebnis."""

    def _from_thread(self, text: str) -> tuple[str, str]:
        """Ruft die Bruecke in einem Thread ohne Schleife, nennt Ergebnis und Thread."""
        result: str = self.worker.submit_sync(_Request(text), timeout=LONG_DEADLINE_S)
        return result, threading.current_thread().name

    def _from_other_loop(self, text: str) -> tuple[str, str]:
        """Ruft die Bruecke aus einer Coroutine auf einer eigenen, zweiten Schleife."""

        async def on_other_loop() -> str:
            return self.worker.submit_sync(_Request(text), timeout=LONG_DEADLINE_S)

        result: str = asyncio.run(on_other_loop())
        return result, threading.current_thread().name

    async def test_from_to_thread_returns_the_result(self) -> None:
        with self.assertNoLogs(WORKER_LOGGER, level="ERROR"):
            result, _ = await asyncio.to_thread(self._from_thread, "b")

        self.assertEqual(result, "echo:b")
        self.assertEqual(self.worker.seen, ["b"])

    async def test_from_other_loop_returns_the_result(self) -> None:
        with self.assertNoLogs(WORKER_LOGGER, level="ERROR"):
            result, _ = await asyncio.to_thread(self._from_other_loop, "c")

        self.assertEqual(result, "echo:c")
        self.assertEqual(self.worker.seen, ["c"])

    def _bridge_line(self, records: list) -> str:
        """Die eine Debug-Zeile der Bruecke aus den aufgezeichneten Saetzen."""
        lines: list[str] = [
            r.getMessage() for r in records if "submit_sync" in r.getMessage()
        ]
        self.assertEqual(len(lines), 1, lines)
        return lines[0]

    async def test_log_line_names_thread_without_foreign_loop(self) -> None:
        with self.assertLogs(WORKER_LOGGER, level="DEBUG") as logs:
            _, thread_name = await asyncio.to_thread(self._from_thread, "d")

        line: str = self._bridge_line(logs.records)
        self.assertIn(f"Thread '{thread_name}'", line)
        self.assertIn("fremde Schleife: nein", line)
        self.assertNotIn("aus Worker-Thread", line)

    async def test_log_line_names_thread_with_foreign_loop(self) -> None:
        with self.assertLogs(WORKER_LOGGER, level="DEBUG") as logs:
            _, thread_name = await asyncio.to_thread(self._from_other_loop, "e")

        line: str = self._bridge_line(logs.records)
        self.assertIn(f"Thread '{thread_name}'", line)
        self.assertIn("fremde Schleife: ja", line)


if __name__ == "__main__":
    unittest.main()
