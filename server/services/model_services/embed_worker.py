"""
EmbedWorker — bedient die Rolle `embed` (Embedding-Modell auf GPU).

Konkrete Eigenschaften:
  - Modell: nomic-embed-text-v2-moe (aus config.EMBED_MODEL; seit A4
    Chat 107 — v1 war casing-blind, siehe EMBEDDING-CASING-BLIND).
    Ohne Task-Praefixe — die Messung schlaegt das Datenblatt.
  - Endpoint: config.ollama_gpu_embed (Port 11434, eigener Riegel)
  - API-Stil: client.embed(model=..., input=...)["embeddings"][0]
    (neuere Ollama-API; die alte .embeddings(prompt=...)["embedding"] ist
    deprecated)
  - Geteilt zwischen Nova und Pixie — FIFO-Queue serialisiert Anfragen.
"""

from __future__ import annotations

import asyncio
import logging
import time

from config import EMBED_MODEL, ollama_gpu_embed
from services.model_services.types import (
    EmbedBatchRequest,
    EmbedBatchResponse,
    EmbedRequest,
    EmbedResponse,
)
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
        self._client = ollama_gpu_embed
        self._model = EMBED_MODEL
        logger.info(
            "EmbedWorker konfiguriert: Modell='%s', Host=%s",
            self._model,
            self._client._host if hasattr(self._client, "_host") else "?",
        )

    async def _call_model(
        self, request: EmbedRequest | EmbedBatchRequest,
    ) -> EmbedResponse | EmbedBatchResponse:
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
        if isinstance(request, EmbedBatchRequest):
            return await self._call_batch(request)

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

    async def _call_batch(self, request: EmbedBatchRequest) -> EmbedBatchResponse:
        """
        Bettet mehrere Texte in einem Ollama-Aufruf ein.

        Vorbedingung: `texts` ist nicht leer, jeder Text ist eine nicht leere
            Zeichenkette.
        Nachbedingung: genau ein Vektor je Text, in Eingabereihenfolge, alle
            gleich lang.
        Fehlerfaelle: `ValueError` bei verletzter Vorbedingung, `RuntimeError`,
            wenn Ollama eine andere Zahl oder Form von Vektoren liefert —
            ein Stapel, dessen Zuordnung nicht stimmt, ist schlimmer als keiner.

        Args:
            request: EmbedBatchRequest mit den Texten.

        Returns:
            EmbedBatchResponse mit einem Vektor je Text.

        Raises:
            ValueError: bei leerem Stapel oder leerem Text.
            RuntimeError: bei falscher Anzahl oder Form der Vektoren.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not request.texts or any(not isinstance(t, str) or not t.strip() for t in request.texts):
            raise ValueError(
                f"EmbedWorker: Stapel {request.request_id} leer oder mit leerem Text "
                f"({len(request.texts)} Eintraege)"
            )

        # ── Verarbeitung ────────────────────────────
        start = time.time()
        response = await asyncio.to_thread(
            self._client.embed,
            model=self._model,
            input=list(request.texts),
        )
        embeddings = response.get("embeddings")

        # ── Ausgabe-Verifikation ────────────────────
        if not isinstance(embeddings, list) or len(embeddings) != len(request.texts):
            raise RuntimeError(
                f"EmbedWorker: Stapel {request.request_id} — {len(request.texts)} Texte, "
                f"aber {len(embeddings) if isinstance(embeddings, list) else 'keine'} Vektoren"
            )
        laengen = {len(e) for e in embeddings}
        if len(laengen) != 1 or 0 in laengen:
            raise RuntimeError(
                f"EmbedWorker: Stapel {request.request_id} — Vektorlaengen {sorted(laengen)}"
            )
        duration = time.time() - start
        logger.info(
            "EmbedWorker: Stapel %s erfolgreich (%d Texte, Dauer: %.3fs)",
            request.request_id, len(embeddings), duration,
        )
        return EmbedBatchResponse(
            embeddings=embeddings,
            model_name=self._model,
            duration_seconds=duration,
            request_id=request.request_id,
        )
