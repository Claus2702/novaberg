"""RedisManager — Redis-Zugriff, nativ threadsafe."""

import json
import logging
from config import redis_client as _redis

logger = logging.getLogger(__name__)


class RedisManager:
    """Kapselt Redis-Zugriff. Redis-Clients sind von Haus aus threadsafe.

    Hinweis: Der redis_client aus config.py hat decode_responses=True,
    d.h. alle Rückgaben sind bereits str (kein .decode() nötig).
    """

    def __init__(self, client):
        self._client = client

    def get(self, key: str) -> str | None:
        """Wert lesen."""
        return self._client.get(key)

    def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        """Wert setzen, optional mit TTL."""
        if ttl_seconds:
            self._client.setex(key, ttl_seconds, value)
        else:
            self._client.set(key, value)

    def delete(self, key: str) -> int:
        """Schlüssel löschen, gibt Anzahl gelöschter Schlüssel zurück."""
        return self._client.delete(key)

    def exists(self, key: str) -> bool:
        """Prüft ob Schlüssel existiert."""
        return bool(self._client.exists(key))

    def get_json(self, key: str) -> dict | list | None:
        """JSON-Wert lesen und parsen."""
        val = self.get(key)
        if val:
            return json.loads(val)
        return None

    def set_json(self, key: str, value: dict | list, ttl_seconds: int | None = None) -> None:
        """Wert als JSON speichern."""
        self.set(key, json.dumps(value, ensure_ascii=False), ttl_seconds)

    def keys(self, pattern: str) -> list[str]:
        """Schlüssel nach Pattern suchen."""
        return self._client.keys(pattern)

    def hset(self, key: str, mapping: dict) -> int:
        """Hash-Felder setzen."""
        return self._client.hset(key, mapping=mapping)

    def hget(self, key: str, field: str) -> str | None:
        """Einzelnes Hash-Feld lesen."""
        return self._client.hget(key, field)

    def hgetall(self, key: str) -> dict:
        """Alle Hash-Felder lesen."""
        return self._client.hgetall(key)

    def publish(self, channel: str, message: str) -> int:
        """Nachricht auf Channel publizieren."""
        return self._client.publish(channel, message)

    def expire(self, key: str, seconds: int) -> bool:
        """TTL auf Schlüssel setzen."""
        return self._client.expire(key, seconds)

    @property
    def client(self):
        """Direkter Zugriff auf den Redis-Client für erweiterte Operationen (z.B. FT.SEARCH)."""
        return self._client


# Modul-Level-Instanz
redis_manager = RedisManager(client=_redis)
