"""
Image storage service for saving pasted images
"""
import os
import uuid
from pathlib import Path
from PySide6.QtGui import QPixmap
from typing import Optional


class ImageStorageService:
    """Service for saving and loading images"""

    def __init__(self, storage_dir: str = "data/images"):
        self._storage_dir = Path(storage_dir)
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure storage directory exists"""
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def save_image(self, pixmap: QPixmap) -> Optional[str]:
        """
        Save pixmap to storage and return file path.

        Returns:
            File path if saved successfully, None otherwise
        """
        if pixmap.isNull():
            return None

        # Generate unique filename
        filename = f"{uuid.uuid4()}.png"
        file_path = self._storage_dir / filename

        # Save as PNG
        if pixmap.save(str(file_path), "PNG"):
            return str(file_path)

        return None

    def delete_image(self, file_path: str) -> bool:
        """
        Delete image file.

        Returns:
            True if deleted, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
        except Exception:
            pass
        return False

    def load_image(self, file_path: str) -> Optional[QPixmap]:
        """
        Load image from file path.

        Returns:
            QPixmap if loaded successfully, None otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    return pixmap
        except Exception:
            pass
        return None
