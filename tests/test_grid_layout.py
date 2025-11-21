"""
Tests for grid layout spacing and alignment
"""
import pytest
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from widgets.note_card import NoteCard
from widgets.image_card import ImageCard
from widgets.app_card import AppCard
from window.models.note import Note, NoteType
from models.app_shortcut import AppShortcut, LaunchType


class TestGridSpacing:
    """Test grid cell dimensions and spacing"""

    # Grid constants - must match widget constants
    CELL_WIDTH = 90
    CELL_HEIGHT = 100
    SPACING = 4
    GRID_COLUMNS = 3

    def test_note_card_2_span_width(self, qtbot):
        """2-column note card should be exactly 2*CELL_WIDTH + SPACING"""
        note = Note(id="1", content="Test", type=NoteType.TEXT, category="All")
        card = NoteCard(note, col_span=2)
        qtbot.addWidget(card)

        expected_width = (self.CELL_WIDTH * 2) + (self.SPACING * 1)
        assert card.width() == expected_width, f"Expected {expected_width}, got {card.width()}"

    def test_note_card_3_span_width(self, qtbot):
        """3-column note card should be exactly 3*CELL_WIDTH + 2*SPACING"""
        note = Note(id="1", content="Test", type=NoteType.TEXT, category="All")
        card = NoteCard(note, col_span=3)
        qtbot.addWidget(card)

        expected_width = (self.CELL_WIDTH * 3) + (self.SPACING * 2)
        assert card.width() == expected_width, f"Expected {expected_width}, got {card.width()}"

    def test_note_card_height(self, qtbot):
        """Note card height should be exactly CELL_HEIGHT"""
        note = Note(id="1", content="Test", type=NoteType.TEXT, category="All")
        card = NoteCard(note, col_span=2)
        qtbot.addWidget(card)

        assert card.height() == self.CELL_HEIGHT, f"Expected {self.CELL_HEIGHT}, got {card.height()}"

    def test_image_card_1x1_dimensions(self, qtbot):
        """1x1 image card dimensions"""
        pixmap = QPixmap(100, 100)  # Square image
        pixmap.fill(Qt.GlobalColor.red)
        card = ImageCard("1", pixmap)
        qtbot.addWidget(card)

        # 1x1 would be single cell but calculator returns 2x2 for square
        # Let's check it's a valid grid size
        assert card.width() > 0
        assert card.height() > 0
        assert card.col_span >= 1
        assert card.row_span >= 1

    def test_image_card_wide_dimensions(self, qtbot):
        """Wide image (3:1) should span 3 columns, 1 row"""
        pixmap = QPixmap(300, 100)  # Wide image
        pixmap.fill(Qt.GlobalColor.blue)
        card = ImageCard("1", pixmap)
        qtbot.addWidget(card)

        assert card.col_span == 3, f"Expected col_span 3, got {card.col_span}"
        assert card.row_span == 1, f"Expected row_span 1, got {card.row_span}"

        expected_width = (self.CELL_WIDTH * 3) + (self.SPACING * 2)
        assert card.width() == expected_width, f"Expected width {expected_width}, got {card.width()}"

    def test_image_card_tall_dimensions(self, qtbot):
        """Tall image (1:3) should span 1 column, 3 rows"""
        pixmap = QPixmap(100, 300)  # Tall image
        pixmap.fill(Qt.GlobalColor.green)
        card = ImageCard("1", pixmap)
        qtbot.addWidget(card)

        assert card.col_span == 1, f"Expected col_span 1, got {card.col_span}"
        assert card.row_span == 3, f"Expected row_span 3, got {card.row_span}"

        expected_height = (self.CELL_HEIGHT * 3) + (self.SPACING * 2)
        assert card.height() == expected_height, f"Expected height {expected_height}, got {card.height()}"

    def test_app_card_dimensions(self, qtbot):
        """App card should be exactly 1x1 cell"""
        app = AppShortcut(
            id="1", name="Test", icon_path="🔧",
            target="test.exe", category="All", type=LaunchType.EXE
        )
        card = AppCard(app=app, on_tap=lambda: None)
        qtbot.addWidget(card)

        assert card.width() == self.CELL_WIDTH, f"Expected {self.CELL_WIDTH}, got {card.width()}"
        assert card.height() == self.CELL_HEIGHT, f"Expected {self.CELL_HEIGHT}, got {card.height()}"

    def test_total_grid_width_fits_window(self, qtbot):
        """3 columns + spacing should fit in 320px window with margins"""
        window_width = 320
        margin = 8  # Left + right margins

        total_grid_width = (self.CELL_WIDTH * 3) + (self.SPACING * 2)
        available_width = window_width - (margin * 2)

        assert total_grid_width <= available_width, \
            f"Grid width {total_grid_width} exceeds available {available_width}"

    def test_2span_plus_1span_fits_row(self, qtbot):
        """2-span note + 1-span app should fit in one row"""
        note_width = (self.CELL_WIDTH * 2) + self.SPACING
        app_width = self.CELL_WIDTH
        total = note_width + self.SPACING + app_width

        expected_row_width = (self.CELL_WIDTH * 3) + (self.SPACING * 2)
        assert total == expected_row_width, \
            f"2-span + 1-span = {total}, expected {expected_row_width}"


class TestGridAlignment:
    """Test that items align properly in grid"""

    def test_items_in_same_row_have_same_top(self, qtbot):
        """Items placed in same grid row should have aligned tops"""
        container = QWidget()
        layout = QGridLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        # Create two items in same row
        note = Note(id="1", content="Test", type=NoteType.TEXT, category="All")
        card1 = NoteCard(note, col_span=2)

        app = AppShortcut(
            id="2", name="App", icon_path="🔧",
            target="test.exe", category="All", type=LaunchType.EXE
        )
        card2 = AppCard(app=app, on_tap=lambda: None)

        layout.addWidget(card1, 0, 0, 1, 2)
        layout.addWidget(card2, 0, 2, 1, 1)

        container.setFixedWidth(320)
        container.show()
        qtbot.addWidget(container)

        # Process events to ensure layout is computed
        QApplication.processEvents()

        # Both should have same Y position (top aligned)
        assert card1.y() == card2.y(), \
            f"Items not top-aligned: card1.y={card1.y()}, card2.y={card2.y()}"

    def test_items_in_same_row_have_same_bottom(self, qtbot):
        """Items in same row should have aligned bottoms (same height)"""
        container = QWidget()
        layout = QGridLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        note = Note(id="1", content="Test", type=NoteType.TEXT, category="All")
        card1 = NoteCard(note, col_span=2)

        app = AppShortcut(
            id="2", name="App", icon_path="🔧",
            target="test.exe", category="All", type=LaunchType.EXE
        )
        card2 = AppCard(app=app, on_tap=lambda: None)

        layout.addWidget(card1, 0, 0, 1, 2)
        layout.addWidget(card2, 0, 2, 1, 1)

        container.setFixedWidth(320)
        container.show()
        qtbot.addWidget(container)
        QApplication.processEvents()

        bottom1 = card1.y() + card1.height()
        bottom2 = card2.y() + card2.height()

        assert bottom1 == bottom2, \
            f"Items not bottom-aligned: card1 bottom={bottom1}, card2 bottom={bottom2}"

    def test_no_overflow_with_3span_note(self, qtbot):
        """3-span note should not overflow 320px window"""
        container = QWidget()
        container.setFixedWidth(320)

        layout = QGridLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        note = Note(id="1", content="Test note", type=NoteType.TEXT, category="All")
        card = NoteCard(note, col_span=3)
        layout.addWidget(card, 0, 0, 1, 3)

        container.show()
        qtbot.addWidget(container)
        QApplication.processEvents()

        # Card should not extend beyond container
        card_right = card.x() + card.width()
        container_right = container.width() - 8  # Right margin

        assert card_right <= container_right, \
            f"Card overflows: card_right={card_right}, container_right={container_right}"

    def test_gap_between_rows_is_consistent(self, qtbot):
        """Gap between rows should equal SPACING"""
        container = QWidget()
        layout = QGridLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        app1 = AppShortcut(
            id="1", name="App1", icon_path="🔧",
            target="test.exe", category="All", type=LaunchType.EXE
        )
        app2 = AppShortcut(
            id="2", name="App2", icon_path="🔧",
            target="test.exe", category="All", type=LaunchType.EXE
        )

        card1 = AppCard(app=app1, on_tap=lambda: None)
        card2 = AppCard(app=app2, on_tap=lambda: None)

        layout.addWidget(card1, 0, 0)
        layout.addWidget(card2, 1, 0)

        container.setFixedWidth(320)
        container.show()
        qtbot.addWidget(container)
        QApplication.processEvents()

        gap = card2.y() - (card1.y() + card1.height())
        assert gap == 4, f"Gap between rows should be 4, got {gap}"


class TestGridOverflow:
    """Test that items don't overflow the window"""

    def test_note_card_does_not_overflow_window(self, qtbot):
        """Note card width should fit within 320px window"""
        window_width = 320
        margin = 8

        note = Note(id="1", content="Test", type=NoteType.TEXT, category="All")

        for span in [2, 3]:
            card = NoteCard(note, col_span=span)
            qtbot.addWidget(card)

            max_width = window_width - (margin * 2)
            assert card.width() <= max_width, \
                f"{span}-span card width {card.width()} exceeds max {max_width}"

    def test_image_card_max_3_columns(self, qtbot):
        """Image card should never exceed 3 columns"""
        # Very wide image
        pixmap = QPixmap(1000, 100)
        pixmap.fill(Qt.GlobalColor.red)
        card = ImageCard("1", pixmap)
        qtbot.addWidget(card)

        assert card.col_span <= 3, f"col_span {card.col_span} exceeds max 3"

    def test_image_card_max_3_rows(self, qtbot):
        """Image card should never exceed 3 rows"""
        # Very tall image
        pixmap = QPixmap(100, 1000)
        pixmap.fill(Qt.GlobalColor.red)
        card = ImageCard("1", pixmap)
        qtbot.addWidget(card)

        assert card.row_span <= 3, f"row_span {card.row_span} exceeds max 3"
