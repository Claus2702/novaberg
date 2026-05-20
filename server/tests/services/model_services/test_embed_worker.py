"""Smoke-Tests fuer den EmbedWorker (Phase 2 + 3).

Scope: FIFO-Verhalten, Future-Befuellung, Exception-Propagation,
sync-Bruecke aus Worker-Thread (submit_sync, Phase 3).
Echte Ollama-Calls werden gemockt — kein laufender Server noetig.

Test-Konvention orientiert sich an tests/agents/charakter_identitaet/test_resume.py:
unittest.TestCase als Basis; async-faehige Tests via IsolatedAsyncioTestCase.
"""

import asyncio
import unittest
from unittest.mock import patch

from services.model_services.embed_worker import EmbedWorker
from services.model_services.types import EmbedRequest, EmbedResponse


class EmbedWorkerBasicTest(unittest.IsolatedAsyncioTestCase):
    """Worker-Lifecycle und Resultat-Form."""

    async def asyncSetUp(self):
        self.worker = EmbedWorker()
        await self.worker.start()

    async def asyncTearDown(self):
        await self.worker.shutdown()

    async def test_embed_worker_basic_submit(self):
        """submit() liefert EmbedResponse mit nicht-leerem Vektor."""
        fake_vektor: list[float] = [0.1, 0.2, 0.3, 0.4]

        with patch.object(
            self.worker, "_client",
        ) as mock_client:
            mock_client.embed.return_value = {"embeddings": [fake_vektor]}

            request = EmbedRequest(text="Testtext")
            response: EmbedResponse = await self.worker.submit(request)

            self.assertIsInstance(response, EmbedResponse)
            self.assertEqual(response.embedding, fake_vektor)
            self.assertEqual(response.model_name, self.worker._model)
            self.assertEqual(response.request_id, request.request_id)
            self.assertGreaterEqual(response.duration_seconds, 0.0)

            mock_client.embed.assert_called_once_with(
                model=self.worker._model,
                input="Testtext",
            )


class EmbedWorkerFifoTest(unittest.IsolatedAsyncioTestCase):
    """Drei Requests parallel — Reihenfolge im Worker ist FIFO."""

    async def asyncSetUp(self):
        self.worker = EmbedWorker()
        await self.worker.start()

    async def asyncTearDown(self):
        await self.worker.shutdown()

    async def test_embed_worker_fifo_order(self):
        """client.embed() wird in Einreich-Reihenfolge aufgerufen."""
        aufruf_reihenfolge: list[str] = []

        def fake_embed(model: str, input: str) -> dict:
            aufruf_reihenfolge.append(input)
            return {"embeddings": [[0.0] * 4]}

        with patch.object(self.worker, "_client") as mock_client:
            mock_client.embed.side_effect = fake_embed

            requests = [
                EmbedRequest(text="A"),
                EmbedRequest(text="B"),
                EmbedRequest(text="C"),
            ]

            ergebnisse = await asyncio.gather(*(
                self.worker.submit(req) for req in requests
            ))

            self.assertEqual(aufruf_reihenfolge, ["A", "B", "C"])
            self.assertEqual(len(ergebnisse), 3)
            self.assertEqual(
                [r.request_id for r in ergebnisse],
                [req.request_id for req in requests],
            )


class EmbedWorkerExceptionTest(unittest.IsolatedAsyncioTestCase):
    """Exceptions aus _call_model werden ueber die Future propagiert."""

    async def asyncSetUp(self):
        self.worker = EmbedWorker()
        await self.worker.start()

    async def asyncTearDown(self):
        await self.worker.shutdown()

    async def test_embed_worker_exception_propagation(self):
        """submit() raised die Original-Exception, kein silent skip."""

        class OllamaSimulierterFehler(RuntimeError):
            pass

        with patch.object(self.worker, "_client") as mock_client:
            mock_client.embed.side_effect = OllamaSimulierterFehler(
                "Ollama nicht erreichbar"
            )

            request = EmbedRequest(text="X")

            with self.assertRaises(OllamaSimulierterFehler) as cm:
                await self.worker.submit(request)

            self.assertIn("Ollama nicht erreichbar", str(cm.exception))


class EmbedWorkerSubmitSyncTest(unittest.IsolatedAsyncioTestCase):
    """submit_sync brueckt aus Worker-Thread zurueck in den Haupt-Loop."""

    async def asyncSetUp(self):
        self.worker = EmbedWorker()
        await self.worker.start()

    async def asyncTearDown(self):
        await self.worker.shutdown()

    async def test_embed_worker_submit_sync_from_thread(self):
        """
        Verifiziert, dass submit_sync aus einem Worker-Thread funktioniert.

        Pattern: Eine sync-Funktion ruft submit_sync auf, wir starten sie
        über asyncio.to_thread aus dem Async-Test. Das simuliert genau die
        Situation des Enrichers (LangGraph-Node sync, in to_thread-Worker).
        """
        # Mock so, dass embed eine deterministische Antwort liefert
        mock_embedding = [0.1] * 768
        mock_response = {"embeddings": [mock_embedding]}

        with patch.object(self.worker, "_client") as mock_client:
            mock_client.embed.return_value = mock_response

            # Sync-Funktion, die aus dem Worker-Thread läuft
            def sync_caller():
                request = EmbedRequest(text="Test aus Worker-Thread")
                response = self.worker.submit_sync(request, timeout=5.0)
                return response

            # Aus to_thread heraus aufrufen — Haupt-Loop läuft, sync_caller
            # läuft im Worker-Thread, submit_sync brückt zurück
            response = await asyncio.to_thread(sync_caller)

            self.assertEqual(response.embedding, mock_embedding)
            self.assertEqual(response.model_name, self.worker._model)
            self.assertGreaterEqual(response.duration_seconds, 0.0)


if __name__ == "__main__":
    unittest.main()
