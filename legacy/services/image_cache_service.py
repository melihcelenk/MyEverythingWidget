"""
Image cache service
Caches QPixmap objects to prevent repeated disk reads
"""
from PySide6.QtGui import QPixmap
from typing import Optional
import logging


class ImageCacheService:
    """Singleton service to cache loaded images"""

    _instance: Optional['ImageCacheService'] = None
    _logger = logging.getLogger(__name__)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
            cls._instance._max_size = 100  # Maximum cached images
        return cls._instance

    def get(self, path: str) -> Optional[QPixmap]:
        """Get cached pixmap or load from disk"""
        if path in self._cache:
            self._logger.debug("Cache hit: %s", path)
            return self._cache[path]

        # Load from disk
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self._logger.warning("Failed to load image: %s", path)
            return None

        # Add to cache (with simple LRU eviction)
        if len(self._cache) >= self._max_size:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._logger.debug("Evicted from cache: %s", oldest_key)

        self._cache[path] = pixmap
        self._logger.debug("Cached image: %s", path)
        return pixmap

    def invalidate(self, path: str):
        """Remove specific image from cache"""
        if path in self._cache:
            del self._cache[path]
            self._logger.debug("Invalidated cache: %s", path)

    def clear(self):
        """Clear all cached images"""
        self._cache.clear()
        self._logger.debug("Cache cleared")

    @property
    def size(self) -> int:
        """Number of cached images"""
        return len(self._cache)
