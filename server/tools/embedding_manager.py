"""EmbeddingManager — Embedding-Erzeugung über Ollama, zustandslos."""

import logging
import numpy as np
from config import ollama_gpu_client as _embed_client, EMBED_MODEL

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Kapselt Embedding-Erzeugung. Zustandslos pro Aufruf.

    Verwendet die Ollama-Client-API: client.embeddings(model=..., prompt=...)
    Rückgabe: response["embedding"] (einzelner Vektor, Singular).
    """

    def __init__(self, client, model: str):
        self._client = client
        self._model = model

    def embed(self, text: str) -> list[float]:
        """Erzeugt ein Embedding für den gegebenen Text."""
        response = self._client.embeddings(model=self._model, prompt=text)
        return response["embedding"]

    def similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Cosine Similarity zwischen zwei Vektoren."""
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        dot = np.dot(a, b)
        norm = np.linalg.norm(a) * np.linalg.norm(b)
        if norm == 0:
            return 0.0
        return float(dot / norm)


# Modul-Level-Instanz
embedding_manager = EmbeddingManager(client=_embed_client, model=EMBED_MODEL)
