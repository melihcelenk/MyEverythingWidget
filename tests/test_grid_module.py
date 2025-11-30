"""
Tests for the grid module.

Tests CollisionDetector, CellCalculator, and GridManager classes.
"""
import pytest

from window.grid.cell_calculator import CellCalculator
from window.grid.collision_detector import CollisionDetector, GridItem
from window.grid.constants import GRID_COLS, GRID_ROWS, CELL_WIDTH, CELL_HEIGHT
from window.grid.grid_manager import GridManager


class TestGridConstants:
    """Test grid constants are properly defined."""

    def test_grid_dimensions(self):
        """Grid should be 4x5."""
        assert GRID_COLS == 4
        assert GRID_ROWS == 5

    def test_cell_dimensions(self):
        """Cell should be 80x80."""
        assert CELL_WIDTH == 80
        assert CELL_HEIGHT == 80


class TestGridItem:
    """Test GridItem dataclass."""

    def test_single_cell_item(self):
        """1x1 item should occupy one cell."""
        item = GridItem(id="test", row=0, col=0)
        cells = item.get_cells()
        assert cells == {(0, 0)}

    def test_2x1_item(self):
        """2x1 item should occupy two horizontal cells."""
        item = GridItem(id="test", row=0, col=0, col_span=2)
        cells = item.get_cells()
        assert cells == {(0, 0), (0, 1)}

    def test_2x2_item(self):
        """2x2 item should occupy four cells."""
        item = GridItem(id="test", row=1, col=1, row_span=2, col_span=2)
        cells = item.get_cells()
        assert cells == {(1, 1), (1, 2), (2, 1), (2, 2)}


class TestCollisionDetector:
    """Test CollisionDetector class."""

    @pytest.fixture
    def detector(self):
        return CollisionDetector()

    def test_add_item_success(self, detector):
        """Adding item to empty grid should succeed."""
        item = GridItem(id="test", row=0, col=0)
        assert detector.add_item(item) is True

    def test_add_item_collision(self, detector):
        """Adding item to occupied cell should fail."""
        item1 = GridItem(id="item1", row=0, col=0)
        item2 = GridItem(id="item2", row=0, col=0)

        assert detector.add_item(item1) is True
        assert detector.add_item(item2) is False

    def test_add_spanning_item_collision(self, detector):
        """2x1 item should collide with item in second cell."""
        item1 = GridItem(id="item1", row=0, col=1)  # At (0,1)
        item2 = GridItem(id="item2", row=0, col=0, col_span=2)  # Spans (0,0) and (0,1)

        assert detector.add_item(item1) is True
        assert detector.add_item(item2) is False

    def test_remove_item(self, detector):
        """Removing item should free its cells."""
        item = GridItem(id="test", row=0, col=0)
        detector.add_item(item)
        detector.remove_item("test")

        # Should be able to add another item at same position
        item2 = GridItem(id="test2", row=0, col=0)
        assert detector.add_item(item2) is True

    def test_check_collision_empty(self, detector):
        """No collision on empty grid."""
        collision = detector.check_collision(0, 0)
        assert collision == set()

    def test_check_collision_occupied(self, detector):
        """Should detect collision with occupied cell."""
        item = GridItem(id="test", row=0, col=0)
        detector.add_item(item)

        collision = detector.check_collision(0, 0)
        assert collision == {(0, 0)}

    def test_check_collision_exclude_self(self, detector):
        """Should exclude self from collision check."""
        item = GridItem(id="test", row=0, col=0)
        detector.add_item(item)

        collision = detector.check_collision(0, 0, exclude_id="test")
        assert collision == set()

    def test_find_colliding_item(self, detector):
        """Should find which item occupies a cell."""
        item = GridItem(id="my-item", row=0, col=0, col_span=2)
        detector.add_item(item)

        # Check both cells
        assert detector.find_colliding_item({(0, 0)}) == "my-item"
        assert detector.find_colliding_item({(0, 1)}) == "my-item"
        assert detector.find_colliding_item({(0, 2)}) is None

    def test_is_valid_position(self, detector):
        """Should validate position within grid bounds."""
        assert detector.is_valid_position(0, 0) is True
        assert detector.is_valid_position(4, 3) is True  # Last valid cell (4x5 grid)
        assert detector.is_valid_position(5, 0) is False  # Row overflow
        assert detector.is_valid_position(0, 4) is False  # Col overflow (4 cols: 0-3)
        assert detector.is_valid_position(-1, 0) is False  # Negative row

    def test_is_valid_position_with_span(self, detector):
        """Should validate span doesn't overflow."""
        assert detector.is_valid_position(0, 0, row_span=2, col_span=2) is True
        assert detector.is_valid_position(4, 0, row_span=2) is False  # Would overflow rows
        assert detector.is_valid_position(0, 3, col_span=2) is False  # Would overflow cols (4 cols)


class TestCellCalculator:
    """Test CellCalculator class."""

    def test_find_first_available_empty(self):
        """First available should be (0,0) on empty grid."""
        cell = CellCalculator.find_first_available_cell(set())
        assert cell == (0, 0)

    def test_find_first_available_with_occupied(self):
        """Should skip occupied cells."""
        occupied = {(0, 0), (0, 1), (0, 2), (0, 3)}  # First row full (4 cols)
        cell = CellCalculator.find_first_available_cell(occupied)
        assert cell == (1, 0)  # First cell of second row

    def test_find_first_available_for_2x1(self):
        """Should find space for 2-column item."""
        occupied = {(0, 0)}  # First cell occupied
        cell = CellCalculator.find_first_available_cell(occupied, col_span=2)
        assert cell == (0, 1)  # (0,1) and (0,2) are free

    def test_find_first_available_no_space(self):
        """Should return None if grid is full."""
        # Fill entire grid
        occupied = set()
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                occupied.add((r, c))

        cell = CellCalculator.find_first_available_cell(occupied)
        assert cell is None

    def test_cell_to_pos(self):
        """Should convert cell to pixel position."""
        x, y = CellCalculator.cell_to_pos(0, 0)
        assert x == 4  # MARGIN_LEFT
        assert y == 4  # MARGIN_TOP

        x, y = CellCalculator.cell_to_pos(0, 1)
        assert x == 4 + 80  # MARGIN_LEFT + CELL_WIDTH (no spacing)

    def test_pos_to_cell(self):
        """Should convert pixel position to cell."""
        row, col = CellCalculator.pos_to_cell(6, 4)  # Top-left corner
        assert row == 0
        assert col == 0

        row, col = CellCalculator.pos_to_cell(100, 100)
        assert row == 1
        assert col == 1

    def test_pos_to_cell_clamps(self):
        """Should clamp position to valid bounds."""
        row, col = CellCalculator.pos_to_cell(-10, -10)
        assert row == 0
        assert col == 0

        row, col = CellCalculator.pos_to_cell(1000, 1000)
        assert row == GRID_ROWS - 1
        assert col == GRID_COLS - 1

    def test_get_cell_size(self):
        """Should calculate correct pixel size for span."""
        w, h = CellCalculator.get_cell_size(1, 1)
        assert w == 80
        assert h == 80

        w, h = CellCalculator.get_cell_size(2, 1)
        assert w == 80 + 80  # Two cells (no spacing)
        assert h == 80

    def test_clamp_position(self):
        """Should clamp position to ensure item fits."""
        row, col = CellCalculator.clamp_position(10, 10)
        assert row == 4  # GRID_ROWS - 1
        assert col == 3  # GRID_COLS - 1 (4 cols: 0-3)

        # With span
        row, col = CellCalculator.clamp_position(4, 3, row_span=2, col_span=2)
        assert row == 3  # Max row for 2-row item
        assert col == 2  # Max col for 2-col item (4 - 2 = 2)


class TestGridManager:
    """Test GridManager class - main grid management."""

    @pytest.fixture
    def manager(self):
        return GridManager()

    def test_add_item_success(self, manager):
        """Adding item to empty grid should succeed."""
        result = manager.add_item("item1", row=0, col=0)
        assert result.success is True
        assert result.row == 0
        assert result.col == 0

    def test_add_item_with_span(self, manager):
        """Adding 2x1 item should occupy two cells."""
        result = manager.add_item("item1", row=0, col=0, col_span=2)
        assert result.success is True

        # Second item at (0,1) should fail
        result2 = manager.add_item("item2", row=0, col=1)
        assert result2.success is False

    def test_add_item_collision(self, manager):
        """Adding item to occupied cell should fail."""
        manager.add_item("item1", row=0, col=0)
        result = manager.add_item("item2", row=0, col=0)
        assert result.success is False

    def test_add_item_out_of_bounds(self, manager):
        """Adding item out of bounds should fail."""
        result = manager.add_item("item1", row=10, col=0)
        assert result.success is False

    def test_remove_item(self, manager):
        """Removing item should free its cells."""
        manager.add_item("item1", row=0, col=0)
        removed = manager.remove_item("item1")
        assert removed is True

        # Should be able to add again
        result = manager.add_item("item2", row=0, col=0)
        assert result.success is True

    def test_auto_place(self, manager):
        """Auto-place should find first available cell."""
        result = manager.auto_place_item("item1")
        assert result.success is True
        assert result.row == 0
        assert result.col == 0

        # Second item
        result2 = manager.auto_place_item("item2")
        assert result2.success is True
        assert result2.col == 1

    def test_auto_place_with_span(self, manager):
        """Auto-place 2x1 item should skip single cells."""
        manager.add_item("item1", row=0, col=0)  # Block (0,0)

        result = manager.auto_place_item("item2", col_span=2)
        assert result.success is True
        assert result.row == 0
        assert result.col == 1  # Fits at (0,1)-(0,2)

    def test_move_item(self, manager):
        """Moving item should update its position."""
        manager.add_item("item1", row=0, col=0)
        result = manager.move_item("item1", target_row=1, target_col=1)

        assert result.success is True
        item = manager.get_item("item1")
        assert item.row == 1
        assert item.col == 1

    def test_move_item_collision(self, manager):
        """Moving to occupied cell should fail."""
        manager.add_item("item1", row=0, col=0)
        manager.add_item("item2", row=1, col=1)

        result = manager.move_item("item1", target_row=1, target_col=1)
        assert result.success is False

    def test_swap_to_empty(self, manager):
        """Swapping to empty cell should just move."""
        manager.add_item("item1", row=0, col=0)

        success, swapped = manager.try_swap("item1", target_row=1, target_col=1)
        assert success is True
        assert swapped is None  # No swap, just move

    def test_swap_items(self, manager):
        """Swapping two 1x1 items should work."""
        manager.add_item("item1", row=0, col=0)
        manager.add_item("item2", row=1, col=1)

        success, swapped = manager.try_swap("item1", target_row=1, target_col=1)
        assert success is True
        assert swapped == "item2"

        # Check positions
        item1 = manager.get_item("item1")
        item2 = manager.get_item("item2")
        assert item1.row == 1 and item1.col == 1
        assert item2.row == 0 and item2.col == 0

    def test_swap_different_sizes_fails(self, manager):
        """Swapping items of different sizes should fail if target doesn't fit."""
        # 2x1 item at (0,0)-(0,1)
        manager.add_item("item1", row=0, col=0, col_span=2)
        # 1x1 item at (0,3) - last column
        manager.add_item("item2", row=0, col=3)

        # Try to move 2x1 to (0,3) - won't fit (would need col 3-4, but only 0-3 exist)
        success, swapped = manager.try_swap("item1", target_row=0, target_col=3)
        # 2x1 at (0,3) would overflow column (need 2 cols but only 1 left)
        assert success is False

    def test_get_item_at(self, manager):
        """Should find item at specific cell."""
        manager.add_item("item1", row=1, col=2)

        found = manager.get_item_at(1, 2)
        assert found == "item1"

        empty = manager.get_item_at(0, 0)
        assert empty is None

    def test_get_items_in_area(self, manager):
        """Should find all items in an area."""
        manager.add_item("item1", row=0, col=0)
        manager.add_item("item2", row=0, col=2)
        manager.add_item("item3", row=1, col=1)

        # Area covering first row
        items = manager.get_items_in_area(0, 0, row_span=1, col_span=3)
        assert set(items) == {"item1", "item2"}

    def test_grid_stats(self, manager):
        """Should return correct grid statistics."""
        manager.add_item("item1", row=0, col=0, col_span=2)  # 2 cells
        manager.add_item("item2", row=1, col=0)  # 1 cell

        stats = manager.get_stats()
        assert stats["total_cells"] == 20  # 4x5
        assert stats["occupied_cells"] == 3
        assert stats["free_cells"] == 17
        assert stats["item_count"] == 2

    def test_clear(self, manager):
        """Clear should remove all items."""
        manager.add_item("item1", row=0, col=0)
        manager.add_item("item2", row=1, col=1)

        manager.clear()

        assert manager.is_empty() is True
        assert manager.get_occupied_count() == 0


class TestDropHandler:
    """Test DropHandler class - drag-drop operations."""

    @pytest.fixture
    def manager(self):
        return GridManager()

    @pytest.fixture
    def handler(self, manager):
        from window.grid.drop_handler import DropHandler
        return DropHandler(manager)

    def test_drop_to_empty(self, manager, handler):
        """Dropping to empty cell should move item."""
        from window.grid.drop_handler import DropAction

        manager.add_item("item1", row=0, col=0)
        result = handler.handle_drop("item1", target_row=1, target_col=1)

        assert result.success is True
        assert result.action == DropAction.MOVE
        assert result.target_row == 1
        assert result.target_col == 1

    def test_drop_swap(self, manager, handler):
        """Dropping on another item should swap."""
        from window.grid.drop_handler import DropAction

        manager.add_item("item1", row=0, col=0)
        manager.add_item("item2", row=1, col=1)

        result = handler.handle_drop("item1", target_row=1, target_col=1)

        assert result.success is True
        assert result.action == DropAction.SWAP
        assert result.swapped_id == "item2"

    def test_drop_same_position_rejected(self, manager, handler):
        """Dropping on same position should be rejected."""
        from window.grid.drop_handler import DropAction

        manager.add_item("item1", row=0, col=0)
        result = handler.handle_drop("item1", target_row=0, target_col=0)

        assert result.success is False
        assert result.action == DropAction.REJECT

    def test_drop_out_of_bounds_clamped(self, manager, handler):
        """Dropping out of bounds should clamp to valid position."""
        manager.add_item("item1", row=0, col=0)
        result = handler.handle_drop("item1", target_row=10, target_col=10)

        # Should clamp to (4,3) - last valid position for 1x1 (4 cols: 0-3)
        assert result.success is True
        assert result.target_row == 4
        assert result.target_col == 3

    def test_can_drop_empty(self, manager, handler):
        """can_drop should return True for empty cell."""
        manager.add_item("item1", row=0, col=0)

        assert handler.can_drop("item1", target_row=1, target_col=1) is True

    def test_can_drop_swap(self, manager, handler):
        """can_drop should return True when swap is possible."""
        manager.add_item("item1", row=0, col=0)
        manager.add_item("item2", row=1, col=1)

        assert handler.can_drop("item1", target_row=1, target_col=1) is True

    def test_can_drop_same_position(self, manager, handler):
        """can_drop should return False for same position."""
        manager.add_item("item1", row=0, col=0)

        assert handler.can_drop("item1", target_row=0, target_col=0) is False

    def test_move_callback(self, manager, handler):
        """Move callback should be called on move."""
        manager.add_item("item1", row=0, col=0)

        moved = []
        handler.set_move_callback(lambda id, r, c: moved.append((id, r, c)))

        handler.handle_drop("item1", target_row=1, target_col=1)

        assert moved == [("item1", 1, 1)]

    def test_swap_callback(self, manager, handler):
        """Swap callback should be called on swap."""
        manager.add_item("item1", row=0, col=0)
        manager.add_item("item2", row=1, col=1)

        swapped = []
        handler.set_swap_callback(
            lambda id1, r1, c1, id2, r2, c2: swapped.append((id1, r1, c1, id2, r2, c2))
        )

        handler.handle_drop("item1", target_row=1, target_col=1)

        assert len(swapped) == 1
        assert swapped[0][0] == "item1"
        assert swapped[0][3] == "item2"

    def test_get_drop_preview(self, manager, handler):
        """get_drop_preview should return correct area."""
        manager.add_item("item1", row=0, col=0, col_span=2)

        row, col, row_span, col_span = handler.get_drop_preview("item1", 1, 1)

        assert row == 1
        assert col == 1  # clamped to fit 2x1
        assert row_span == 1
        assert col_span == 2
