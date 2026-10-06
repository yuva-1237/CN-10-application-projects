"""Utilities and Cache manager for DNS Resolver."""
import logging
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

@dataclass
class CacheEntry:
    value: Any
    expires_at: float

class DNSCache:
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached result if not expired."""
        with self.lock:
            entry = self.cache.get(key)
            if entry:
                if time.time() < entry.expires_at:
                    self.hits += 1
                    return entry.value
                else:
                    del self.cache[key]
            self.misses += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store key-value with TTL."""
        valid_ttl = ttl if ttl is not None else self.default_ttl
        with self.lock:
            self.cache[key] = CacheEntry(value=value, expires_at=time.time() + valid_ttl)

    def clear(self) -> None:
        """Flush the entire cache."""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> Dict[str, Any]:
        """Return cache health metrics."""
        with self.lock:
            active = sum(1 for e in self.cache.values() if time.time() < e.expires_at)
            return {
                "active_entries": active,
                "hits": self.hits,
                "misses": self.misses,
                "hit_ratio": (self.hits / (self.hits + self.misses)) if (self.hits + self.misses) > 0 else 0.0
            }

def setup_logger(name: str, log_file: Path | None = None) -> logging.Logger:
    """Configure a standard logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
