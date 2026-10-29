"""
Tests for clipboard paste functionality
"""
import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication


class TestClipboardPaste:
    """Tests for clipboard image paste functionality"""

    @pytest.fixture
    def qapp(self):
        """Create QApplication for tests"""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    def test_clipboard_service_creation(self, qapp):
        """Test ClipboardService can be created"""
        from services.clipboard_service import ClipboardService

        service = ClipboardService()
        assert service is not None

    def test_has_image_returns_false_when_empty(self, qapp):
        """Test has_image returns False when clipboard is empty"""
        from services.clipboard_service import ClipboardService

        # Clear clipboard
        clipboard = QApplication.clipboard()
        clipboard.clear()

        service = ClipboardService()
        assert service.has_image() is False

    def test_has_image_returns_true_when_image_present(self, qapp):
        """Test has_image returns True when clipboard has image"""
        from services.clipboard_service import ClipboardService

        # Put image in clipboard
        clipboard = QApplication.clipboard()
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.blue)
        clipboard.setPixmap(pixmap)

        service = ClipboardService()
        assert service.has_image() is True

    def test_get_image_returns_pixmap(self, qapp):
        """Test get_image returns pixmap from clipboard"""
        from services.clipboard_service import ClipboardService

        # Put image in clipboard
        clipboard = QApplication.clipboard()
        original = QPixmap(200, 150)
        original.fill(Qt.GlobalColor.red)
        clipboard.setPixmap(original)

        service = ClipboardService()
        result = service.get_image()

        assert result is not None
        assert not result.isNull()
        assert result.width() == 200
        assert result.height() == 150

    def test_get_image_returns_none_when_no_image(self, qapp):
        """Test get_image returns None when no image in clipboard"""
        from services.clipboard_service import ClipboardService

        # Clear clipboard
        clipboard = QApplication.clipboard()
        clipboard.clear()

        service = ClipboardService()
        result = service.get_image()

        assert result is None

    def test_has_text_ignores_text(self, qapp):
        """Test has_image returns False when only text in clipboard"""
        from services.clipboard_service import ClipboardService

        # Put text in clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText("Hello world")

        service = ClipboardService()
        assert service.has_image() is False
