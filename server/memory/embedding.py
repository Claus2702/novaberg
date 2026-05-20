"""
Embedding-Erzeugung via Ollama.

Hinweis: Die frühere Funktion ``embedding_create`` wurde im Block 1
Cleanup-Sprint (Phase 5) entfernt. Embeddings laufen jetzt zentral über
``services.model_services.model_service.embed``.
"""

EMBEDDING_DIM: int = 768
