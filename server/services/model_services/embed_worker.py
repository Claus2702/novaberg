"""
EmbedWorker — bedient die Rolle `embed` (Nomic-Embed-Text auf GPU).

Konkrete Eigenschaften:
  - Modell: nomic-embed-text (aus config.EMBED_MODEL)
  - Endpoint: config.ollama_gpu_client (Port 11434)
  - API-Stil: client.embed(model=..., input=...)["embeddings"][0]
    (neuere Ollama-API; die alte .embeddings(prompt=...)["embedding"] ist
    deprecated)
  - Geteilt zwischen Nova und Pixie — FIFO-Queue serialisiert Anfragen.
"""

from __future__ import annotations

import asyncio
import logging
import time

from config import EMBED_MODEL, ollama_gpu_client
from services.model_services.types import EmbedRequest, EmbedResponse
from services.model_services.worker_base import ModelWorker

logger = logging.getLogger(__name__)


class EmbedWorker(ModelWorker[EmbedRequest, EmbedResponse]):
    """
    FIFO-Worker für Embedding-Anfragen.

    Konsumenten rufen `model_service.embed.submit(EmbedRequest(text=...))` auf
    und bekommen über das Future einen EmbedResponse zurück.
    """

    def __init__(self) -> None:
        super().__init__(name="embed")
        self._client = ollama_gpu_client
        self._model = EMBED_MODEL
        logger.info(
            "EmbedWorker konfiguriert: Modell='%s', Host=%s",
            self._model,
            self._client._host if hasattr(self._client, "_host") else "?",
        )

    async def _call_model(self, request: EmbedRequest) -> EmbedResponse:
        """
        Führt den eigentlichen Embedding-Call gegen Ollama aus.

        Verwendet die neuere Ollama-API: client.embed(input=...) liefert
        response["embeddings"] als list[list[float]]; wir geben den ersten
        Vektor zurück.

        Args:
            request: EmbedRequest mit Text.

        Returns:
            EmbedResponse mit Embedding-Vektor und Metadaten.

        Raises:
            RuntimeError: Wenn Ollama keinen Embedding-Vektor liefert.
            Sonstige Exceptions vom Ollama-Client werden propagiert.
        """
        start = time.time()
        text_preview = request.text[:60].replace("\n", " ")
        logger.debug(
            "EmbedWorker: Anfrage %s startet (Text-Länge: %d, Preview: '%s...')",
            request.request_id,
            len(request.text),
            text_preview,
        )

        # Ollama-Client ist sync — in Thread auslagern, damit die
        # Worker-Schleife nicht blockiert
        response = await asyncio.to_thread(
            self._client.embed,
            model=self._model,
            input=request.text,
        )

        embeddings = response.get("embeddings")
        if not embeddings or not isinstance(embeddings, list) or len(embeddings) == 0:
            raise RuntimeError(
                f"EmbedWorker: Ollama lieferte kein gültiges 'embeddings'-Feld "
                f"(Response-Keys: {list(response.keys())})"
            )

        embedding = embeddings[0]
        duration = time.time() - start

        logger.info(
            "EmbedWorker: Anfrage %s erfolgreich (Dauer: %.3fs, Dim: %d)",
            request.request_id,
            duration,
            len(embedding),
        )

        return EmbedResponse(
            embedding=embedding,
            model_name=self._model,
            duration_seconds=duration,
            request_id=request.request_id,
        )
