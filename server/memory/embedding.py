"""
Embedding-Erzeugung via Ollama.
"""

import logging

import ollama

logger = logging.getLogger("ki_server.memory.embedding")

EMBEDDING_DIM: int = 768


def embedding_create(
    text:          str,
    embed_client: ollama.Client,
    embed_model:   str = "nomic-embed-text"
) -> list[float]:
    """Erzeugt einen Embedding-Vektor für den gegebenen Text."""

    response = embed_client.embeddings(
        model  = embed_model,
        prompt = text,
    )

    embedding: list[float] = response["embedding"]
    logger.info(f"Embedding erzeugt ({len(embedding)} Dimensionen)")

    return embedding
