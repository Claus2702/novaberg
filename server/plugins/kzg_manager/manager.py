"""
KZG-Manager — Schreibt/verstärkt Kurzzeitgedächtnis-Einträge in Redis.
Immer aktiv: Jeder Turn wird analysiert und ggf. gespeichert.
Nutzt die Speicherlogik aus memory/kzg.py.
"""

import logging

import redis

from plugins.base import BaseManager
from memory.kzg   import kzg_store

logger = logging.getLogger("ki_server.plugins.kzg")


class KzgManager(BaseManager):

    @property
    def ziel(self) -> str:
        return "kzg"

    @property
    def immer_aktiv(self) -> bool:
        return True

    def execute(
        self,
        writes:        list[dict],
        user_id:       str,
        redis_client:  redis.Redis,
        postgres_url:  str,
        embed_client  = None,
        embed_model:   str = ""
    ) -> int:
        """Speichert oder verstärkt KZG-Einträge."""

        verarbeitet: int = 0

        for write in writes:
            daten:       dict        = write.get("daten", {})
            salienz_obj: dict        = daten.get("salienz_obj", {})
            embedding:   list[float] = daten.get("embedding", [])

            if not salienz_obj or not embedding:
                logger.warning("KZG-Manager: salienz_obj oder embedding fehlt — übersprungen")
                continue

            status: str = kzg_store(redis_client, user_id, salienz_obj, embedding)
            logger.info(f"KZG-Manager: Status = {status}")
            verarbeitet += 1

        return verarbeitet