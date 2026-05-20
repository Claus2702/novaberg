"""
Model-Services — Microservice-Architektur für Modell-Aufrufe.

Public API:
    from services.model_services import model_service, EmbedRequest

    response = await model_service.embed.submit(EmbedRequest(text="..."))

Architektur-Doku: novaberg/docs/novaberg-microservice-modell-queue_k.md
"""

from services.model_services.registry import model_service
from services.model_services.types import EmbedRequest, EmbedResponse

__all__ = ["model_service", "EmbedRequest", "EmbedResponse"]
