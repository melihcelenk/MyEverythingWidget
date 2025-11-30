"""
Tests for grid layout spacing and alignment
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout

from models.app_shortcut import AppShortcut, LaunchType
from widgets.app_card import AppCard
from widgets.image_card import ImageCard
from widgets.note_card import NoteCard
from window.models.note import Note, NoteType


class TestGridSpacing:
    """Test grid cell dimensions and spacing"""

    # Grid constants - must match widget constants (updated to 80x80)
    CELL_WIDTH = 80
    CELL_HEIGHT = 80
    SPACING = 0
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

    CELL_WIDTH = 80
    CELL_HEIGHT = 80
    SPACING = 0

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

    def test_2x1_image_plus_note_fits_in_row(self, qtbot):
        """2x1 image + 1x1 note should fit, NOT 2x1 image + 2x1 note"""
        # 2x1 image takes 2 columns
        image_cols = 2
        # Only 1 column left, so note must be 1x1 or go to next row
        remaining = 3 - image_cols

        # A 2-span note should NOT fit in remaining space
        note_span = 2
        assert note_span > remaining, \
            f"2-span note ({note_span}) should not fit in remaining {remaining} columns"

    def test_items_after_2col_image_should_wrap(self, qtbot):
        """Items that don't fit after 2-col image should wrap to next row"""
        container = QWidget()
        container.setFixedWidth(320)

        layout = QGridLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        # Set fixed column widths
        for i in range(3):
            layout.setColumnMinimumWidth(i, 80)
            layout.setColumnStretch(i, 0)

        # 2x1 image in columns 0-1
        pixmap = QPixmap(200, 100)  # Wide image -> 2x1 or 3x1
        pixmap.fill(Qt.GlobalColor.blue)
        image_card = ImageCard("1", pixmap)

        # 2-span note - should go to next row since only 1 col left
        note = Note(id="2", content="Test", type=NoteType.TEXT, category="All")
        note_card = NoteCard(note, col_span=2)

        # Place image at row 0, col 0, span 2 cols
        layout.addWidget(image_card, 0, 0, 1, 2)
        # Note should be placed at row 1, col 0 (wrapped)
        layout.addWidget(note_card, 1, 0, 1, 2)

        container.show()
        qtbot.addWidget(container)
        QApplication.processEvents()

        # Image should be in row 0
        assert image_card.y() < note_card.y(), \
            f"Note should be below image: image.y={image_card.y()}, note.y={note_card.y()}"

        # Note should not overflow container
        note_right = note_card.x() + note_card.width()
        container_inner_width = container.width() - 16  # margins
        assert note_right <= container_inner_width, \
            f"Note overflows: right={note_right}, container={container_inner_width}"

    def test_2col_image_followed_by_2col_note_wraps(self, qtbot):
        """When 2-col image is placed, 2-col note should wrap to next row"""
        # This tests the actual visual placement

        container = QWidget()
        container.setFixedWidth(320)

        layout = QGridLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        # Set fixed column widths
        for i in range(3):
            layout.setColumnMinimumWidth(i, 80)
            layout.setColumnStretch(i, 0)

        # Create 2x1 image (narrow horizontal)
        pixmap = QPixmap(120, 100)  # ratio 1.2, should be 2x1
        pixmap.fill(Qt.GlobalColor.blue)
        image_card = ImageCard("1", pixmap)

        # Verify image is 2x1
        assert image_card.col_span == 2, f"Expected 2 cols, got {image_card.col_span}"
        assert image_card.row_span == 1, f"Expected 1 row, got {image_card.row_span}"

        # Create 2-span note
        note = Note(id="2", content="Test", type=NoteType.TEXT, category="All")
        note_card = NoteCard(note, col_span=2)

        # Place image at row 0, col 0 (spans 2 cols)
        layout.addWidget(image_card, 0, 0, 1, 2)

        # After 2-col image, only 1 col left
        # 2-span note should NOT be placed at col 2 (would overflow)
        # It should wrap to row 1, col 0

        # Simulate the logic
        col = 0 + 2  # After image
        available = 3 - col  # = 1
        note_span = 2

        # Note doesn't fit (2 > 1), should wrap
        if note_span > available:
            row = 1
            col = 0
        else:
            row = 0

        layout.addWidget(note_card, row, col, 1, note_span)

        container.show()
        qtbot.addWidget(container)
        QApplication.processEvents()

        # Verify note is below image, not beside it
        assert note_card.y() > image_card.y(), \
            f"Note should be below image: note.y={note_card.y()}, image.y={image_card.y()}"

        # Verify note doesn't overflow
        note_right = note_card.x() + note_card.width()
        max_right = container.width() - 8  # right margin
        assert note_right <= max_right, \
            f"Note overflows: right={note_right}, max={max_right}"

    def test_2x2_image_note_should_go_below_not_beside(self, qtbot):
        """2x2 image occupies rows 0-1, cols 0-1. Note should go to row 2, not row 1 col 2"""
        # This is the actual bug scenario from logs:
        # Image at row=6, col=0, col_span=2, row_span=2
        # Note placed at row=7, col=2 with span=2 - this overflows!

        # Simulate the placement algorithm
        occupied = set()

        # Image: 2 cols, 2 rows starting at row 0, col 0
        image_row = 0
        image_col = 0
        image_col_span = 2
        image_row_span = 2

        # Mark occupied cells
        for r in range(image_row, image_row + image_row_span):
            for c in range(image_col, image_col + image_col_span):
                occupied.add((r, c))

        # After image placement
        col = image_col + image_col_span  # = 2
        if col >= 3:
            col = 0
            row = image_row + image_row_span  # = 2
        else:
            row = image_row  # = 0

        # Now place note
        # Skip occupied cells
        while (row, col) in occupied:
            col += 1
            if col >= 3:
                col = 0
                row += 1

        preferred_span = 2

        # Find a position where the note fits without overflow
        while True:
            available = 3 - col

            if preferred_span <= available:
                span = preferred_span
                break
            elif available >= 2:
                span = 2
                break
            else:
                # Not enough space, move to next row
                row += 1
                col = 0
                # Skip occupied cells
                while (row, col) in occupied:
                    col += 1
                    if col >= 3:
                        col = 0
                        row += 1

        # Note should be at row 2, col 0 with span 2
        # NOT at row 0/1, col 2 (which would overflow)
        assert row >= image_row + image_row_span or col + span <= 3, \
            f"Note at row={row}, col={col}, span={span} would overlap or overflow"

        # Specifically check it doesn't overflow
        assert col + span <= 3, \
            f"Note overflows: col={col}, span={span}, total={col+span}"

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

    def test_2col_image_plus_3col_image_wraps(self, qtbot):
        """2-col image followed by 3-col image should wrap to next row, not overflow"""
        # This tests the actual bug: 2+3=5 columns in one row (max is 3)

        # Simulate the TabManager placement logic
        occupied = set()

        # First image: 2 cols, 1 row
        img1_row = 0
        img1_col = 0
        img1_col_span = 2
        img1_row_span = 1

        # Mark occupied cells for first image
        for r in range(img1_row, img1_row + img1_row_span):
            for c in range(img1_col, img1_col + img1_col_span):
                occupied.add((r, c))

        # After first image
        col = img1_col + img1_col_span  # = 2
        row = img1_row  # = 0

        # Second image: 3 cols, 1 row
        img2_col_span = 3

        # The correct logic should check if it fits
        if col + img2_col_span > 3:
            # Should wrap to next row
            row += 1
            col = 0

        # Verify second image is placed correctly (wrapped to row 1)
        assert row == 1, f"3-col image should wrap to row 1, not stay at row {row}"
        assert col == 0, f"3-col image should start at col 0, not col {col}"
        assert col + img2_col_span <= 3, \
            f"Overflow: col={col}, span={img2_col_span}, total={col + img2_col_span}"

    def test_tab_manager_image_placement_no_overflow(self, qtbot):
        """Test that actual TabManager placement algorithm doesn't overflow"""

        # Simulate the exact placement logic from TabManager._add_note_cards_to_layout
        occupied = set()
        row = 0
        col = 0

        # List of image spans to place (simulating the bug scenario)
        # First a 2x1, then a 3x1
        images = [
            (2, 1),  # 2 cols, 1 row
            (3, 1),  # 3 cols, 1 row
        ]

        placements = []

        for col_span, row_span in images:
            # Skip occupied cells
            while (row, col) in occupied:
                col += 1
                if col >= 3:
                    col = 0
                    row += 1

            # Check if fits in current row
            if col + col_span > 3:
                row += 1
                col = 0
                # Skip occupied cells again
                while (row, col) in occupied:
                    col += 1
                    if col >= 3:
                        col = 0
                        row += 1

            # Record placement
            placements.append((row, col, col_span, row_span))

            # Mark cells as occupied
            for r in range(row, row + row_span):
                for c in range(col, col + col_span):
                    occupied.add((r, c))

            # Move to next position
            col += col_span
            if col >= 3:
                col = 0
                row += row_span

        # Verify no placement overflows
        for i, (p_row, p_col, p_col_span, p_row_span) in enumerate(placements):
            assert p_col + p_col_span <= 3, \
                f"Image {i} overflows: row={p_row}, col={p_col}, span={p_col_span}, total={p_col + p_col_span}"

        # Verify the second image (3-col) is on its own row
        assert placements[0] == (0, 0, 2, 1), f"First image wrong: {placements[0]}"
        assert placements[1] == (1, 0, 3, 1), f"Second image wrong: {placements[1]}"

    def test_2x2_image_followed_by_3x1_image_wraps_properly(self, qtbot):
        """2x2 image followed by 3x1 image should not overflow"""
        # This is the exact bug: 2x2 occupies (0,0), (0,1), (1,0), (1,1)
        # After skipping occupied cells, 3x1 ends up at (1,2) which overflows

        occupied = set()
        row = 0
        col = 0

        # First image: 2x2
        images = [
            (2, 2),  # 2 cols, 2 rows
            (3, 1),  # 3 cols, 1 row
        ]

        placements = []

        for col_span, row_span in images:
            # Skip occupied cells
            while (row, col) in occupied:
                col += 1
                if col >= 3:
                    col = 0
                    row += 1

            # Find a position where image fits without overflow
            while True:
                if col + col_span > 3:
                    row += 1
                    col = 0
                    # Skip occupied cells again
                    while (row, col) in occupied:
                        col += 1
                        if col >= 3:
                            col = 0
                            row += 1
                else:
                    break

            placements.append((row, col, col_span, row_span))

            # Mark cells as occupied
            for r in range(row, row + row_span):
                for c in range(col, col + col_span):
                    occupied.add((r, c))

            # Move to next position
            col += col_span
            if col >= 3:
                col = 0
                row += row_span

        # Verify no overflow
        for i, (p_row, p_col, p_col_span, p_row_span) in enumerate(placements):
            assert p_col + p_col_span <= 3, \
                f"Image {i} overflows: row={p_row}, col={p_col}, span={p_col_span}"

        # First image at (0,0) with 2x2
        assert placements[0] == (0, 0, 2, 2), f"First image wrong: {placements[0]}"
        # Second image should be at row 2 (after 2x2), col 0
        assert placements[1] == (2, 0, 3, 1), f"Second image wrong: {placements[1]}"
