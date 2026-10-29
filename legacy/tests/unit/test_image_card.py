"""
Tests for ImageCard widget
"""
import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication


class TestImageCard:
    """Tests for ImageCard widget"""

    @pytest.fixture
    def qapp(self):
        """Create QApplication for tests"""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    @pytest.fixture
    def sample_pixmap(self, qapp):
        """Create a sample pixmap for testing"""
        pixmap = QPixmap(200, 100)  # 2:1 aspect ratio
        pixmap.fill(Qt.GlobalColor.blue)
        return pixmap

    @pytest.fixture
    def square_pixmap(self, qapp):
        """Create a square pixmap for testing"""
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.red)
        return pixmap

    def test_image_card_creation(self, qapp, sample_pixmap):
        """Test ImageCard can be created"""
        from widgets.image_card import ImageCard

        card = ImageCard(
            image_id="test-id",
            pixmap=sample_pixmap,
            on_delete=lambda id: None
        )
        assert card is not None

    def test_image_card_stores_id(self, qapp, sample_pixmap):
        """Test ImageCard stores image ID"""
        from widgets.image_card import ImageCard

        card = ImageCard(
            image_id="test-123",
            pixmap=sample_pixmap,
            on_delete=lambda id: None
        )
        assert card.image_id == "test-123"

    def test_image_card_displays_image(self, qapp, sample_pixmap):
        """Test ImageCard displays the image"""
        from widgets.image_card import ImageCard

        card = ImageCard(
            image_id="test-id",
            pixmap=sample_pixmap,
            on_delete=lambda id: None
        )

        # Card should have the image displayed
        assert card._image_label is not None
        assert not card._image_label.pixmap().isNull()

    def test_image_card_context_menu_has_delete(self, qapp, sample_pixmap):
        """Test ImageCard context menu has delete option"""
        from widgets.image_card import ImageCard

        deleted_ids = []
        card = ImageCard(
            image_id="test-id",
            pixmap=sample_pixmap,
            on_delete=lambda id: deleted_ids.append(id)
        )

        # Card should have context menu policy
        assert card.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu

    def test_image_card_calculates_span(self, qapp, sample_pixmap):
        """Test ImageCard calculates grid span from image"""
        from widgets.image_card import ImageCard

        card = ImageCard(
            image_id="test-id",
            pixmap=sample_pixmap,  # 200x100 = 2:1 ratio
            on_delete=lambda id: None
        )

        # 2:1 ratio should give 3x2 span
        assert card.col_span == 3
        assert card.row_span == 2

    def test_square_image_card_span(self, qapp, square_pixmap):
        """Test square image gets 2x2 span"""
        from widgets.image_card import ImageCard

        card = ImageCard(
            image_id="test-id",
            pixmap=square_pixmap,
            on_delete=lambda id: None
        )

        # Square should be 2x2
        assert card.col_span == 2
        assert card.row_span == 2

    def test_image_card_scales_image(self, qapp, sample_pixmap):
        """Test ImageCard scales image to fit cell size"""
        from widgets.image_card import ImageCard

        card = ImageCard(
            image_id="test-id",
            pixmap=sample_pixmap,
            on_delete=lambda id: None
        )

        # Image should be scaled (not original size)
        displayed_pixmap = card._image_label.pixmap()
        # Scaled size should be reasonable for grid
        assert displayed_pixmap.width() <= 300
        assert displayed_pixmap.height() <= 300

    def test_image_card_has_border_radius(self, qapp, sample_pixmap):
        """Test ImageCard has rounded corners style"""
        from widgets.image_card import ImageCard

        card = ImageCard(
            image_id="test-id",
            pixmap=sample_pixmap,
            on_delete=lambda id: None
        )

        # Check stylesheet contains border-radius
        style = card.styleSheet()
        assert "border-radius" in style
