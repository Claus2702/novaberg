"""
Model-Services — Microservice-Architektur für Modell-Aufrufe.

Public API:
    from services.model_services import (
        model_service,
        EmbedRequest, EmbedResponse,
        ChatRequest, ChatResponse,
        BackgroundRequest, BackgroundResponse,
    )

    response = await model_service.embed.submit(EmbedRequest(text="..."))
    antwort  = await model_service.chat.submit(ChatRequest(messages=[...]))
    antwort  = await model_service.background.submit(BackgroundRequest(...))

Architektur-Doku: novaberg/docs/novaberg-microservice-modell-queue_k.md
"""

from services.model_services.registry import model_service
from services.model_services.types import (
    BackgroundRequest,
    BackgroundResponse,
    ChatRequest,
    ChatResponse,
    EmbedRequest,
    EmbedResponse,
)

__all__ = [
    "model_service",
    "EmbedRequest", "EmbedResponse",
    "ChatRequest", "ChatResponse",
    "BackgroundRequest", "BackgroundResponse",
]
