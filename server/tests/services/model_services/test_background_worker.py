"""Smoke-Tests fuer den BackgroundWorker (Block 2 Phase 2).

Scope analog zu test_chat_worker plus:
    - Dual-Backend-Routing (modus="analyse" vs "sprache")
    - CJK-Guard mit Retry und finalem strip_cjk

Backends werden durch FakeProvider gemockt — kein laufender Ollama- oder
Claude-Endpunkt noetig.
"""

from __future__ import annotations

import asyncio
import unittest
from json import JSONDecodeError

from services.model_services.background_worker import BackgroundWorker
from services.model_services.types import BackgroundRequest, BackgroundResponse
from tests.services.model_services.fake_provider import FakeProvider


def _make_worker(
    analyse_contents:  list[str] | None = None,
    sprache_contents:  list[str] | None = None,
    analyse_exception: BaseException | None = None,
    sprache_exception: BaseException | None = None,
    max_cjk_retries:   int = 2,
) -> tuple[BackgroundWorker, FakeProvider, FakeProvider]:
    """Baut Worker mit zwei FakeProvider-Instanzen — gibt Worker + Backends zurueck."""
    analyse = FakeProvider(
        contents=list(analyse_contents or ["analyse-antwort"]),
        exception=analyse_exception,
        model="fake-analyse",
    )
    sprache = FakeProvider(
        contents=list(sprache_contents or ["sprache-antwort"]),
        exception=sprache_exception,
        model="fake-sprache",
    )
    worker = BackgroundWorker(
        name="background-test",
        analyse_backend=analyse,
        sprache_backend=sprache,
        max_cjk_retries=max_cjk_retries,
    )
    return worker, analyse, sprache


class _BaseBackgroundWorkerTest(unittest.IsolatedAsyncioTestCase):
    """Gemeinsamer Lifecycle-Wrapper — Subklassen ueberschreiben _build_worker."""

    async def _build_worker(self) -> None:
        self.worker, self.analyse, self.sprache = _make_worker()

    async def asyncSetUp(self) -> None:
        await self._build_worker()
        await self.worker.start()

    async def asyncTearDown(self) -> None:
        await self.worker.shutdown()


class BackgroundWorkerBasicSubmitTest(_BaseBackgroundWorkerTest):
    """Test 1 — submit liefert Response (analyse-Standard)."""

    async def _build_worker(self) -> None:
        self.worker, self.analyse, self.sprache = _make_worker(
            analyse_contents=["Analyse-Ergebnis"],
        )

    async def test_basic_submit(self) -> None:
        request = BackgroundRequest(
            messages=[{"role": "user", "content": "Was ist 1+1?"}],
            modus="analyse",
        )
        response: BackgroundResponse = await self.worker.submit(request)

        self.assertIsInstance(response, BackgroundResponse)
        self.assertEqual(response.text, "Analyse-Ergebnis")
        self.assertEqual(len(self.analyse.aufrufe), 1)
        self.assertEqual(len(self.sprache.aufrufe), 0)


class BackgroundWorkerFifoTest(_BaseBackgroundWorkerTest):
    """Test 2 — drei Requests, Reihenfolge bleibt FIFO."""

    async def _build_worker(self) -> None:
        self.worker, self.analyse, self.sprache = _make_worker(
            analyse_contents=["A1", "A2", "A3"],
        )

    async def test_fifo_order(self) -> None:
        requests = [
            BackgroundRequest(
                messages=[{"role": "user", "content": "A"}],
                modus="analyse",
                caller="A",
            ),
            BackgroundRequest(
                messages=[{"role": "user", "content": "B"}],
                modus="analyse",
                caller="B",
            ),
            BackgroundRequest(
                messages=[{"role": "user", "content": "C"}],
                modus="analyse",
                caller="C",
            ),
        ]
        ergebnisse = await asyncio.gather(*(
            self.worker.submit(req) for req in requests
        ))

        self.assertEqual(
            [a["caller"] for a in self.analyse.aufrufe],
            ["A", "B", "C"],
        )
        self.assertEqual([r.text for r in ergebnisse], ["A1", "A2", "A3"])


class BackgroundWorkerExceptionTest(_BaseBackgroundWorkerTest):
    """Test 3 — Backend wirft, Worker propagiert via Future (kein silent skip)."""

    class _BackendFehler(RuntimeError):
        pass

    async def _build_worker(self) -> None:
        self.worker, self.analyse, self.sprache = _make_worker(
            analyse_exception=self._BackendFehler("Analyse kaputt"),
        )

    async def test_exception_propagation(self) -> None:
        request = BackgroundRequest(
            messages=[{"role": "user", "content": "X"}],
            modus="analyse",
        )
        with self.assertRaises(self._BackendFehler) as cm:
            await self.worker.submit(request)
        self.assertIn("Analyse kaputt", str(cm.exception))


class BackgroundWorkerSubmitSyncTest(_BaseBackgroundWorkerTest):
    """Test 4 — submit_sync bruecke aus to_thread (Loop-Binding-Lesson)."""

    async def _build_worker(self) -> None:
        self.worker, self.analyse, self.sprache = _make_worker(
            analyse_contents=["Sync-Hintergrund"],
        )

    async def test_submit_sync_from_thread(self) -> None:
        def sync_caller() -> BackgroundResponse:
            request = BackgroundRequest(
                messages=[{"role": "user", "content": "T"}],
                modus="analyse",
            )
            return self.worker.submit_sync(request, timeout=5.0)

        response = await asyncio.to_thread(sync_caller)
        self.assertEqual(response.text, "Sync-Hintergrund")


class BackgroundWorkerExpectJsonOkTest(_BaseBackgroundWorkerTest):
    """Test 5 — JSON in Codefences wird sauber geparst."""

    async def _build_worker(self) -> None:
        self.worker, self.analyse, self.sprache = _make_worker(
            analyse_contents=['```json\n{"x": 1, "y": "ja"}\n```'],
        )

    async def test_expect_json_ok(self) -> None:
        request = BackgroundRequest(
            messages=[{"role": "user", "content": "?"}],
            modus="analyse",
            expect_json=True,
        )
        response = await self.worker.submit(request)
        self.assertEqual(response.parsed, {"x": 1, "y": "ja"})


class BackgroundWorkerExpectJsonFailTest(_BaseBackgroundWorkerTest):
    """Test 6 — invalides JSON propagiert JSONDecodeError."""

    async def _build_worker(self) -> None:
        self.worker, self.analyse, self.sprache = _make_worker(
            analyse_contents=["nix json hier."],
        )

    async def test_expect_json_fail(self) -> None:
        request = BackgroundRequest(
            messages=[{"role": "user", "content": "?"}],
            modus="analyse",
            expect_json=True,
        )
        with self.assertRaises(JSONDecodeError):
            await self.worker.submit(request)


class BackgroundWorkerModusRoutingTest(_BaseBackgroundWorkerTest):
    """Test 7 — modus="analyse" trifft Analyse-Backend, "sprache" das Sprach-Backend."""

    async def _build_worker(self) -> None:
        self.worker, self.analyse, self.sprache = _make_worker(
            analyse_contents=["aus-analyse"],
            sprache_contents=["aus-sprache"],
        )

    async def test_modus_routing(self) -> None:
        analyse_req = BackgroundRequest(
            messages=[{"role": "user", "content": "A"}],
            modus="analyse",
        )
        sprache_req = BackgroundRequest(
            messages=[{"role": "user", "content": "S"}],
            modus="sprache",
        )

        ergebnis_analyse = await self.worker.submit(analyse_req)
        ergebnis_sprache = await self.worker.submit(sprache_req)

        self.assertEqual(ergebnis_analyse.text, "aus-analyse")
        self.assertEqual(ergebnis_sprache.text, "aus-sprache")
        self.assertEqual(len(self.analyse.aufrufe), 1)
        self.assertEqual(len(self.sprache.aufrufe), 1)
        self.assertEqual(self.analyse.aufrufe[0]["messages"][-1]["content"], "A")
        self.assertEqual(self.sprache.aufrufe[0]["messages"][-1]["content"], "S")


class BackgroundWorkerCjkRetryTest(_BaseBackgroundWorkerTest):
    """Test 8a — CJK beim 1. Versuch, sauber beim Retry. Ergebnis CJK-frei."""

    async def _build_worker(self) -> None:
        # 1. Versuch: enthaelt chinesische Zeichen (jeder Buchstabe in CJK-Range)
        # 2. Versuch: rein deutsch
        self.worker, self.analyse, self.sprache = _make_worker(
            analyse_contents=["Hallo 你好 Welt", "Hallo deutsche Welt"],
            max_cjk_retries=2,
        )

    async def test_cjk_retry_recovers(self) -> None:
        request = BackgroundRequest(
            messages=[{"role": "user", "content": "Sag Hallo"}],
            modus="analyse",
        )
        response = await self.worker.submit(request)

        # Ergebnis ist CJK-frei
        self.assertNotIn("你", response.text)
        self.assertNotIn("好", response.text)
        self.assertEqual(response.text, "Hallo deutsche Welt")

        # Backend wurde zweimal aufgerufen (Original + Retry)
        self.assertEqual(len(self.analyse.aufrufe), 2)

        # Retry-Call hat den Nachfasser an die letzte user-Message gehaengt
        retry_user_content: str = self.analyse.aufrufe[1]["messages"][-1]["content"]
        self.assertIn("Sag Hallo", retry_user_content)
        self.assertIn("AUSSCHLIESSLICH auf Deutsch", retry_user_content)


class BackgroundWorkerCjkStripFallbackTest(_BaseBackgroundWorkerTest):
    """Test 8b — dauerhaft CJK → strip_cjk greift, Ergebnis ist CJK-frei."""

    async def _build_worker(self) -> None:
        # Alle Versuche enthalten CJK — Worker muss am Ende strippen
        self.worker, self.analyse, self.sprache = _make_worker(
            analyse_contents=[
                "Hallo 你好 (1)",
                "Hallo 你好 (2)",
                "Hallo 你好 (3)",
            ],
            max_cjk_retries=2,
        )

    async def test_cjk_strip_after_retries_exhausted(self) -> None:
        request = BackgroundRequest(
            messages=[{"role": "user", "content": "Test"}],
            modus="analyse",
        )
        response = await self.worker.submit(request)

        self.assertNotIn("你", response.text)
        self.assertNotIn("好", response.text)
        # max_cjk_retries=2 → 3 Versuche insgesamt
        self.assertEqual(len(self.analyse.aufrufe), 3)


if __name__ == "__main__":
    unittest.main()
