"""Smoke-Tests fuer den ChatWorker (Block 2 Phase 2).

Scope: FIFO-Verhalten, Future-Befuellung, Exception-Propagation, sync-Bruecke
aus Worker-Thread (Loop-Binding-Lesson), JSON-Parsing.
Backend wird durch FakeProvider gemockt — kein laufender Ollama- oder
Claude-Endpunkt noetig.
"""

from __future__ import annotations

import asyncio
import unittest
from json import JSONDecodeError

from services.model_services.chat_worker import ChatWorker
from services.model_services.types import ChatRequest, ChatResponse
from tests.services.model_services.fake_provider import FakeProvider


class _BaseChatWorkerTest(unittest.IsolatedAsyncioTestCase):
    """Gemeinsamer Lifecycle-Wrapper fuer alle ChatWorker-Tests."""

    backend_contents: list[str] = ["Antwort"]
    backend_exception: BaseException | None = None

    async def asyncSetUp(self) -> None:
        self.backend = FakeProvider(
            contents=list(self.backend_contents),
            exception=self.backend_exception,
        )
        self.worker = ChatWorker(name="chat-test", backend=self.backend)
        await self.worker.start()

    async def asyncTearDown(self) -> None:
        await self.worker.shutdown()


class ChatWorkerBasicSubmitTest(_BaseChatWorkerTest):
    """Test 1 — submit liefert die erwartete Response."""

    backend_contents = ["Hallo Welt"]

    async def test_basic_submit(self) -> None:
        request = ChatRequest(messages=[{"role": "user", "content": "Hi"}])
        response: ChatResponse = await self.worker.submit(request)

        self.assertIsInstance(response, ChatResponse)
        self.assertEqual(response.text, "Hallo Welt")
        self.assertIsNone(response.parsed)
        self.assertEqual(response.token_total, self.backend.token_total)
        self.assertEqual(len(self.backend.aufrufe), 1)
        self.assertEqual(self.backend.aufrufe[0]["caller"], "chat_worker")
        self.assertFalse(self.backend.aufrufe[0]["format_json"])


class ChatWorkerFifoTest(_BaseChatWorkerTest):
    """Test 2 — drei Requests parallel, Reihenfolge im Worker bleibt FIFO."""

    backend_contents = ["A-Antwort", "B-Antwort", "C-Antwort"]

    async def test_fifo_order(self) -> None:
        requests = [
            ChatRequest(messages=[{"role": "user", "content": "A"}], caller="A"),
            ChatRequest(messages=[{"role": "user", "content": "B"}], caller="B"),
            ChatRequest(messages=[{"role": "user", "content": "C"}], caller="C"),
        ]

        ergebnisse = await asyncio.gather(*(
            self.worker.submit(req) for req in requests
        ))

        self.assertEqual(
            [a["caller"] for a in self.backend.aufrufe],
            ["A", "B", "C"],
        )
        self.assertEqual(
            [r.text for r in ergebnisse],
            ["A-Antwort", "B-Antwort", "C-Antwort"],
        )


class ChatWorkerExceptionTest(_BaseChatWorkerTest):
    """Test 3 — Backend wirft, Worker propagiert via Future (kein silent skip)."""

    class _BackendFehler(RuntimeError):
        pass

    backend_exception = _BackendFehler("Backend kaputt")
    backend_contents = ["dummy"]  # wird nie verwendet

    async def test_exception_propagation(self) -> None:
        request = ChatRequest(messages=[{"role": "user", "content": "X"}])

        with self.assertRaises(self._BackendFehler) as cm:
            await self.worker.submit(request)

        self.assertIn("Backend kaputt", str(cm.exception))


class ChatWorkerSubmitSyncTest(_BaseChatWorkerTest):
    """Test 4 — submit_sync brueckt aus Worker-Thread in den Haupt-Loop.

    Loop-Binding-Lesson: future muss im Haupt-Loop angelegt werden, sonst
    bricht der Aufruf aus einem to_thread-Worker mit
    'attached to a different loop' ab.
    """

    backend_contents = ["Sync-Antwort"]

    async def test_submit_sync_from_thread(self) -> None:
        def sync_caller() -> ChatResponse:
            request = ChatRequest(messages=[{"role": "user", "content": "T"}])
            return self.worker.submit_sync(request, timeout=5.0)

        response: ChatResponse = await asyncio.to_thread(sync_caller)

        self.assertEqual(response.text, "Sync-Antwort")
        self.assertEqual(response.token_total, self.backend.token_total)


class ChatWorkerExpectJsonOkTest(_BaseChatWorkerTest):
    """Test 5 — JSON in Codefences wird sauber geparst."""

    backend_contents = ['```json\n{"k": "v", "n": 7}\n```']

    async def test_expect_json_ok(self) -> None:
        request = ChatRequest(
            messages=[{"role": "user", "content": "?"}],
            expect_json=True,
        )
        response = await self.worker.submit(request)

        self.assertEqual(response.parsed, {"k": "v", "n": 7})
        self.assertIn('"k"', response.text)


class ChatWorkerExpectJsonFailTest(_BaseChatWorkerTest):
    """Test 6 — kaputtes, unreparierbares JSON propagiert JSONDecodeError."""

    backend_contents = ["das ist gar kein json :///"]

    async def test_expect_json_fail(self) -> None:
        request = ChatRequest(
            messages=[{"role": "user", "content": "?"}],
            expect_json=True,
        )

        with self.assertRaises(JSONDecodeError):
            await self.worker.submit(request)


if __name__ == "__main__":
    unittest.main()
