"""
Clipboard service for handling image paste operations
"""
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
from typing import Optional


class ClipboardService:
    """Service for clipboard operations"""

    def has_image(self) -> bool:
        """Check if clipboard contains an image"""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data is None:
            return False

        return mime_data.hasImage()

    def get_image(self) -> Optional[QPixmap]:
        """
        Get image from clipboard as QPixmap.

        Returns:
            QPixmap if clipboard has image, None otherwise
        """
        if not self.has_image():
            return None

        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()

        if pixmap.isNull():
            return None

        return pixmap
