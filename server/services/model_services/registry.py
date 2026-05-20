"""
Worker-Registry — verwaltet Lifecycle aller Model-Worker.

Diese Modul stellt die zentrale Anlaufstelle für Konsumenten dar:

    from services.model_services.registry import model_service

    response = await model_service.embed.submit(EmbedRequest(text="..."))

Beim Server-Startup wird `model_service.startup()` gerufen, beim Shutdown
entsprechend `shutdown()`.
"""

from __future__ import annotations

import logging

from services.model_services.embed_worker import EmbedWorker

logger = logging.getLogger(__name__)


class ModelServiceRegistry:
    """
    Container für alle Model-Worker.

    In Phase 2 nur EmbedWorker. Spätere Blöcke ergänzen ChatWorker und
    BackgroundWorker auf demselben Pattern.
    """

    def __init__(self) -> None:
        self.embed: EmbedWorker = EmbedWorker()
        # self.chat = ChatWorker()       # Block 2
        # self.background = BackgroundWorker()  # Block 2
        logger.info("ModelServiceRegistry initialisiert (Worker: embed)")

    async def startup(self) -> None:
        """
        Startet alle Worker. Wird vom FastAPI-Lifespan beim Server-Start
        aufgerufen.
        """
        logger.info("ModelServiceRegistry: startup() beginnt")
        await self.embed.start()
        logger.info("ModelServiceRegistry: alle Worker gestartet")

    async def shutdown(self) -> None:
        """
        Beendet alle Worker sauber. Wird vom FastAPI-Lifespan beim
        Server-Shutdown aufgerufen.
        """
        logger.info("ModelServiceRegistry: shutdown() beginnt")
        await self.embed.shutdown()
        logger.info("ModelServiceRegistry: alle Worker beendet")


# Singleton-Instanz für globalen Zugriff
model_service = ModelServiceRegistry()
