import time
from typing import Any, Optional


class InMemoryCache:
    _instance: Optional["InMemoryCache"] = None

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    @classmethod
    def get_instance(cls) -> "InMemoryCache":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

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


cache = InMemoryCache.get_instance()
