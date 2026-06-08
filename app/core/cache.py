import json
import time
from typing import Any, Optional

import redis

from app.core.env import get_env


class RedisCache:
    _instance: Optional["RedisCache"] = None

    def __init__(self, redis_client: redis.Redis):
        self._client = redis_client

    @classmethod
    def get_instance(cls) -> "RedisCache":
        if cls._instance is None:
            env = get_env()
            client = redis.from_url(env.REDIS_URL, decode_responses=True)
            cls._instance = cls(client)
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        value = self._client.get(key)
        if value is None:
            return None
        return json.loads(value)

    def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        self._client.setex(key, ttl_seconds, json.dumps(value))

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def invalidate_prefix(self, prefix: str) -> None:
        cursor = 0
        while True:
            cursor, keys = self._client.scan(cursor=cursor, match=f"{prefix}*", count=100)
            if keys:
                self._client.delete(*keys)
            if cursor == 0:
                break


class InMemoryCache:
    """Fallback cache for testing (no Redis required)."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        self._store[key] = (value, time.time() + ttl_seconds)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def invalidate_prefix(self, prefix: str) -> None:
        keys_to_delete = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_delete:
            del self._store[k]


def _create_cache() -> RedisCache | InMemoryCache:
    env = get_env()
    if env.APP_ENVIRONMENT == "testing":
        return InMemoryCache()
    try:
        client = redis.from_url(env.REDIS_URL, decode_responses=True)
        client.ping()
        return RedisCache(client)
    except (redis.ConnectionError, redis.RedisError):
        return InMemoryCache()


cache = _create_cache()
