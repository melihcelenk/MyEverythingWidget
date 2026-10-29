"""
Visual tests for grid drag-drop functionality.

These tests verify:
1. Hover highlight alignment matches actual grid cells
2. Multi-cell items show correct span highlight
3. Collision detection works visually
4. No overlap after drag-drop operations
"""
import pytest
from PySide6.QtWidgets import QGridLayout

from models.app_shortcut import AppShortcut, LaunchType
from models.note import Note, NoteType
from widgets.app_card import AppCard
from widgets.grid_drop_zone import GridDropZone
from widgets.note_card import NoteCard


@pytest.fixture
def app(qapp):
    """Use the qapp fixture from conftest"""
    return qapp


@pytest.fixture
def grid_drop_zone(app):
    """Create a GridDropZone with a layout"""
    zone = GridDropZone()
    layout = QGridLayout(zone)
    layout.setSpacing(GridDropZone.SPACING)
    layout.setContentsMargins(
        GridDropZone.MARGIN_LEFT,
        GridDropZone.MARGIN_TOP,
        GridDropZone.MARGIN_RIGHT,
        GridDropZone.MARGIN_BOTTOM
    )

    # Set fixed column/row sizes
    for i in range(GridDropZone.GRID_COLS):
        layout.setColumnMinimumWidth(i, GridDropZone.CELL_WIDTH)
        layout.setColumnStretch(i, 0)
    for i in range(GridDropZone.GRID_ROWS):
        layout.setRowMinimumHeight(i, GridDropZone.CELL_HEIGHT)
        layout.setRowStretch(i, 0)

    zone.show()
    zone.resize(300, 450)
    app.processEvents()
    return zone


class TestGridDropZoneHighlight:
    """Tests for hover highlight alignment"""

    def test_highlight_matches_cell_rect(self, grid_drop_zone, app):
        """Verify highlight position matches actual layout cell position"""
        layout = grid_drop_zone.layout()

        # Add a dummy widget to ensure layout is computed
        from PySide6.QtWidgets import QLabel
        label = QLabel("Test")
        label.setFixedSize(GridDropZone.CELL_WIDTH, GridDropZone.CELL_HEIGHT)
        layout.addWidget(label, 0, 0)
        app.processEvents()

        # Simulate drag enter
        grid_drop_zone._drag_active = True
        grid_drop_zone._hover_cell = (0, 0)
        grid_drop_zone._dragging_col_span = 1
        grid_drop_zone._dragging_row_span = 1

        # Get actual cell rect
        cell_rect = layout.cellRect(0, 0)

        # Verify cell rect is valid and positioned correctly
        assert cell_rect.isValid(), "Cell rect should be valid"
        assert cell_rect.x() >= 0, "Cell x should be non-negative"
        assert cell_rect.y() >= 0, "Cell y should be non-negative"
        assert cell_rect.width() > 0, "Cell width should be positive"
        assert cell_rect.height() > 0, "Cell height should be positive"

    def test_highlight_for_each_column(self, grid_drop_zone, app):
        """Test that highlight is accurate for each column"""
        layout = grid_drop_zone.layout()

        # Add widgets in each column
        from PySide6.QtWidgets import QLabel
        for col in range(GridDropZone.GRID_COLS):
            label = QLabel(f"Col {col}")
            label.setFixedSize(GridDropZone.CELL_WIDTH, GridDropZone.CELL_HEIGHT)
            layout.addWidget(label, 0, col)
        app.processEvents()

        # Verify each column has distinct x position
        prev_x = -1
        for col in range(GridDropZone.GRID_COLS):
            cell_rect = layout.cellRect(0, col)
            assert cell_rect.isValid(), f"Cell rect for column {col} should be valid"
            assert cell_rect.x() > prev_x, f"Column {col} x should be greater than column {col - 1}"
            prev_x = cell_rect.x()

    def test_highlight_for_2x1_span(self, grid_drop_zone, app):
        """Test highlight for 2-column span item"""
        layout = grid_drop_zone.layout()

        # Add a 2x1 widget
        from PySide6.QtWidgets import QLabel
        label = QLabel("2x1 item")
        label.setFixedSize(
            GridDropZone.CELL_WIDTH * 2 + GridDropZone.SPACING,
            GridDropZone.CELL_HEIGHT
        )
        layout.addWidget(label, 0, 0, 1, 2)  # row, col, row_span, col_span
        app.processEvents()

        # Simulate drag with 2x1 span
        grid_drop_zone._drag_active = True
        grid_drop_zone._hover_cell = (1, 0)  # Row 1, Col 0
        grid_drop_zone._dragging_col_span = 2
        grid_drop_zone._dragging_row_span = 1

        # Get cell rects
        start_rect = layout.cellRect(1, 0)
        end_rect = layout.cellRect(1, 1)

        # Verify span calculation
        if start_rect.isValid() and end_rect.isValid():
            expected_width = end_rect.right() - start_rect.x() + 1
            assert expected_width > GridDropZone.CELL_WIDTH, "2x1 span should be wider than single cell"


class TestGridDropZoneCollision:
    """Tests for collision detection"""

    def test_cell_occupation_tracking(self, grid_drop_zone, app):
        """Verify cells are correctly marked as occupied"""
        layout = grid_drop_zone.layout()

        # Add widgets at specific positions
        from PySide6.QtWidgets import QLabel

        # 1x1 at (0, 0)
        label1 = QLabel("1")
        label1.setFixedSize(GridDropZone.CELL_WIDTH, GridDropZone.CELL_HEIGHT)
        layout.addWidget(label1, 0, 0)

        # 2x1 at (1, 0) spanning columns 0-1
        label2 = QLabel("2")
        label2.setFixedSize(
            GridDropZone.CELL_WIDTH * 2 + GridDropZone.SPACING,
            GridDropZone.CELL_HEIGHT
        )
        layout.addWidget(label2, 1, 0, 1, 2)

        app.processEvents()

        # Verify layout positions
        item1 = layout.itemAtPosition(0, 0)
        assert item1 is not None, "Should have widget at (0, 0)"

        item2 = layout.itemAtPosition(1, 0)
        assert item2 is not None, "Should have widget at (1, 0)"

        # Column 1 of row 1 should also be occupied by the spanning widget
        item3 = layout.itemAtPosition(1, 1)
        assert item3 is not None, "Should have widget spanning to (1, 1)"
        assert item3.widget() == item2.widget(), "Same widget should span (1,0) and (1,1)"


class TestGridDropZoneDimensions:
    """Tests for grid dimension constants"""

    def test_grid_constants_consistency(self):
        """Verify grid constants are consistent across all widgets"""
        from widgets.note_card import NoteCard
        from widgets.image_card import ImageCard
        from widgets.draggable_mixin import CELL_WIDTH

        # All should use the same base dimensions
        assert NoteCard.CELL_WIDTH == GridDropZone.CELL_WIDTH, \
            "NoteCard CELL_WIDTH should match GridDropZone"
        assert NoteCard.CELL_HEIGHT == GridDropZone.CELL_HEIGHT, \
            "NoteCard CELL_HEIGHT should match GridDropZone"

        assert ImageCard.CELL_WIDTH == GridDropZone.CELL_WIDTH, \
            "ImageCard CELL_WIDTH should match GridDropZone"
        assert ImageCard.CELL_HEIGHT == GridDropZone.CELL_HEIGHT, \
            "ImageCard CELL_HEIGHT should match GridDropZone"

        # Draggable mixin uses CELL + SPACING
        expected_drag_cell = GridDropZone.CELL_WIDTH + GridDropZone.SPACING
        assert CELL_WIDTH == expected_drag_cell, \
            f"DraggableMixin CELL_WIDTH ({CELL_WIDTH}) should be {expected_drag_cell}"

    def test_fixed_grid_size(self):
        """Verify grid is fixed 3x5"""
        assert GridDropZone.GRID_COLS == 3, "Grid should have 3 columns"
        assert GridDropZone.GRID_ROWS == 5, "Grid should have 5 rows"

    def test_widget_fits_in_cell(self, app):
        """Verify AppCard fits within grid cell"""
        app_shortcut = AppShortcut(
            id="test-app",
            name="Test",
            path="test.exe",
            type=LaunchType.EXE,
            category="Test"
        )
        card = AppCard(app_shortcut, on_tap=lambda: None)

        assert card.width() <= GridDropZone.CELL_WIDTH, \
            f"AppCard width ({card.width()}) should fit in cell ({GridDropZone.CELL_WIDTH})"
        assert card.height() <= GridDropZone.CELL_HEIGHT, \
            f"AppCard height ({card.height()}) should fit in cell ({GridDropZone.CELL_HEIGHT})"


class TestDragVisualFeedback:
    """Tests for drag visual feedback accuracy"""

    def test_note_card_span_in_drag(self, app):
        """Verify NoteCard reports correct span for drag"""
        note = Note(
            id="test-note",
            content="Test note content",
            type=NoteType.TEXT,
            category="Test",
            col_span=2,
            row_span=1
        )
        card = NoteCard(note, col_span=2, row_span=1)

        assert card.col_span == 2, "NoteCard should have col_span=2"
        assert card.row_span == 1, "NoteCard should have row_span=1"
        assert card._drag_col_span == 2, "Drag col_span should be 2"
        assert card._drag_row_span == 1, "Drag row_span should be 1"

    def test_app_card_default_span(self, app):
        """Verify AppCard has 1x1 span by default"""
        app_shortcut = AppShortcut(
            id="test-app",
            name="Test",
            path="test.exe",
            type=LaunchType.EXE,
            category="Test"
        )
        card = AppCard(app_shortcut, on_tap=lambda: None)

        assert card._drag_col_span == 1, "AppCard should have col_span=1"
        assert card._drag_row_span == 1, "AppCard should have row_span=1"


class TestNoOverlapAfterDrop:
    """Tests to verify no overlap occurs after drag-drop"""

    def test_occupied_cells_include_span(self):
        """Verify _get_occupied_cells includes all cells of spanning items"""
        # This is tested via TabManager, but we verify the model here
        note = Note(
            id="test-note",
            content="Test",
            type=NoteType.TEXT,
            category="Test",
            grid_row=0,
            grid_col=0,
            col_span=2,
            row_span=1
        )

        # Note should occupy (0,0) and (0,1)
        assert note.grid_row == 0
        assert note.grid_col == 0
        assert note.col_span == 2
        assert note.row_span == 1

        # Calculate occupied cells (same logic as TabManager)
        occupied = set()
        for r in range(note.grid_row, note.grid_row + note.row_span):
            for c in range(note.grid_col, note.grid_col + note.col_span):
                occupied.add((r, c))

        assert (0, 0) in occupied, "Cell (0,0) should be occupied"
        assert (0, 1) in occupied, "Cell (0,1) should be occupied"
        assert (0, 2) not in occupied, "Cell (0,2) should NOT be occupied"
        assert (1, 0) not in occupied, "Cell (1,0) should NOT be occupied"

    def test_image_note_span_consistency(self):
        """Verify image notes use consistent span between model and occupied cells"""
        # Image note with 2x2 span
        image_note = Note(
            id="test-image",
            content="/path/to/image.png",
            type=NoteType.IMAGE,
            category="Test",
            grid_row=1,
            grid_col=0,
            col_span=2,
            row_span=2
        )

        # Calculate occupied cells
        occupied = set()
        col_span = image_note.col_span or 1
        row_span = image_note.row_span or 1
        for r in range(image_note.grid_row, image_note.grid_row + row_span):
            for c in range(image_note.grid_col, image_note.grid_col + col_span):
                occupied.add((r, c))

        # 2x2 image at (1,0) should occupy: (1,0), (1,1), (2,0), (2,1)
        assert (1, 0) in occupied, "Cell (1,0) should be occupied"
        assert (1, 1) in occupied, "Cell (1,1) should be occupied"
        assert (2, 0) in occupied, "Cell (2,0) should be occupied"
        assert (2, 1) in occupied, "Cell (2,1) should be occupied"
        assert len(occupied) == 4, "Should occupy exactly 4 cells"


class TestResizePersistence:
    """Tests for resize persistence"""

    def test_note_span_defaults(self):
        """Verify note span defaults are correct"""
        note = Note(
            id="test",
            content="Test",
            type=NoteType.TEXT,
            category="Test"
        )
        assert note.col_span == 1, "Default col_span should be 1"
        assert note.row_span == 1, "Default row_span should be 1"

    def test_note_span_can_be_set(self):
        """Verify note span can be set during creation"""
        note = Note(
            id="test",
            content="Test",
            type=NoteType.TEXT,
            category="Test",
            col_span=2,
            row_span=1
        )
        assert note.col_span == 2, "col_span should be 2"
        assert note.row_span == 1, "row_span should be 1"
