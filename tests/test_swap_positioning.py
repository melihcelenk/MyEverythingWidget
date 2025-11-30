"""
Tests for swap positioning - ensuring items land at correct positions.

TDD: These tests define the expected behavior for multi-span item swaps.
"""
from unittest.mock import MagicMock

import pytest

from window.grid.mover import ItemMover
from window.models.note import Note, NoteType


@pytest.fixture
def mock_app_state():
    """Create a mock AppState."""
    state = MagicMock()
    state.apps = []
    state.notes = []
    state.blockSignals = MagicMock()
    return state


@pytest.fixture
def get_cells_for_item():
    """Helper to get cells for an item."""

    def _get_cells(item):
        if item.grid_row is None or item.grid_col is None:
            return set()
        row_span = getattr(item, 'row_span', 1)
        col_span = getattr(item, 'col_span', 1)
        return {(r, c) for r in range(item.grid_row, item.grid_row + row_span)
                for c in range(item.grid_col, item.grid_col + col_span)}

    return _get_cells


class TestSwapPositioning:
    """Test swap positioning for different item sizes."""

    def test_2x1_note_swap_with_1x1_app_at_right_edge(self, mock_app_state, get_cells_for_item):
        """
        Scenario: 2x1 note swaps with 1x1 app at right edge.
        
        Grid: 5 columns
        Before:
        - 2x1 note at (1, 0)-(1, 1)
        - 1x1 app at (1, 4)
        
        Action: Drop 2x1 note at (1, 3) - should occupy (1, 3)-(1, 4)
        
        After:
        - 2x1 note at (1, 3)-(1, 4)
        - 1x1 app at (1, 0) or (1, 1) - source position
        """
        # Setup
        note = Note(
            id="note-1",
            content="Test Note",
            type=NoteType.TEXT,
            category="Test",
            grid_row=1,
            grid_col=0,
            col_span=2,
            row_span=1
        )

        app = MagicMock()
        app.id = "app-1"
        app.category = "Test"
        app.grid_row = 1
        app.grid_col = 4
        app.col_span = 1
        app.row_span = 1
        app.name = "Test App"

        mock_app_state.notes = [note]
        mock_app_state.apps = [app]

        def get_occupied(category):
            cells = set()
            for n in mock_app_state.notes:
                if n.category == category:
                    cells.update(get_cells_for_item(n))
            for a in mock_app_state.apps:
                if a.category == category:
                    cells.update(get_cells_for_item(a))
            return cells

        mover = ItemMover(mock_app_state, get_occupied, get_cells_for_item)
        mover.on_refresh = MagicMock()

        # Capture the updated note
        updated_notes = []

        def capture_update(n):
            updated_notes.append(n)

        mock_app_state.update_note = capture_update

        # Action: Drop 2x1 note at (1, 3)
        mover.handle_grid_drop("note-1", target_row=1, target_col=3)

        # Assert: Note should be at (1, 3)
        assert len(updated_notes) > 0, "Note should have been updated"
        final_note = updated_notes[-1]
        assert final_note.grid_row == 1, f"Note row should be 1, got {final_note.grid_row}"
        assert final_note.grid_col == 3, f"Note col should be 3, got {final_note.grid_col}"

        # Assert: App should be at note's original position (1, 0)
        assert app.grid_row == 1, f"App row should be 1, got {app.grid_row}"
        assert app.grid_col == 0, f"App col should be 0, got {app.grid_col}"

    def test_1x1_app_swap_with_1x1_app(self, mock_app_state, get_cells_for_item):
        """Simple 1x1 swap should work correctly."""
        app1 = MagicMock()
        app1.id = "app-1"
        app1.category = "Test"
        app1.grid_row = 0
        app1.grid_col = 0
        app1.col_span = 1
        app1.row_span = 1
        app1.name = "App 1"

        app2 = MagicMock()
        app2.id = "app-2"
        app2.category = "Test"
        app2.grid_row = 0
        app2.grid_col = 2
        app2.col_span = 1
        app2.row_span = 1
        app2.name = "App 2"

        mock_app_state.apps = [app1, app2]
        mock_app_state.notes = []

        def get_occupied(category):
            cells = set()
            for a in mock_app_state.apps:
                if a.category == category:
                    cells.update(get_cells_for_item(a))
            return cells

        mover = ItemMover(mock_app_state, get_occupied, get_cells_for_item)
        mover.on_refresh = MagicMock()

        # Action: Drop app1 at (0, 2)
        mover.handle_grid_drop("app-1", target_row=0, target_col=2)

        # Assert: App1 should be at (0, 2)
        assert app1.grid_row == 0
        assert app1.grid_col == 2

        # Assert: App2 should be at (0, 0)
        assert app2.grid_row == 0
        assert app2.grid_col == 0

    def test_2x1_note_move_to_empty_space(self, mock_app_state, get_cells_for_item):
        """2x1 note should move correctly to empty space."""
        note = Note(
            id="note-1",
            content="Test Note",
            type=NoteType.TEXT,
            category="Test",
            grid_row=0,
            grid_col=0,
            col_span=2,
            row_span=1
        )

        mock_app_state.notes = [note]
        mock_app_state.apps = []

        def get_occupied(category):
            cells = set()
            for n in mock_app_state.notes:
                if n.category == category:
                    cells.update(get_cells_for_item(n))
            return cells

        mover = ItemMover(mock_app_state, get_occupied, get_cells_for_item)
        mover.on_refresh = MagicMock()

        updated_notes = []
        mock_app_state.update_note = lambda n: updated_notes.append(n)

        # Action: Move to (1, 3) - should occupy (1, 3)-(1, 4)
        mover.handle_grid_drop("note-1", target_row=1, target_col=3)

        # Assert
        assert len(updated_notes) == 1
        assert updated_notes[0].grid_row == 1
        assert updated_notes[0].grid_col == 3

    def test_swap_rejected_when_colliding_item_doesnt_fit(self, mock_app_state, get_cells_for_item):
        """Swap should be rejected if colliding item doesn't fit at source."""
        # 1x1 note at (0, 0)
        note = Note(
            id="note-1",
            content="Test Note",
            type=NoteType.TEXT,
            category="Test",
            grid_row=0,
            grid_col=0,
            col_span=1,
            row_span=1
        )

        # 2x1 app at (0, 3)-(0, 4) - wouldn't fit at (0, 0) if there's another item at (0, 1)
        app = MagicMock()
        app.id = "app-1"
        app.category = "Test"
        app.grid_row = 0
        app.grid_col = 3
        app.col_span = 2
        app.row_span = 1
        app.name = "Wide App"

        # Blocker at (0, 1)
        blocker = MagicMock()
        blocker.id = "blocker"
        blocker.category = "Test"
        blocker.grid_row = 0
        blocker.grid_col = 1
        blocker.col_span = 1
        blocker.row_span = 1
        blocker.name = "Blocker"

        mock_app_state.notes = [note]
        mock_app_state.apps = [app, blocker]

        def get_occupied(category):
            cells = set()
            for n in mock_app_state.notes:
                if n.category == category:
                    cells.update(get_cells_for_item(n))
            for a in mock_app_state.apps:
                if a.category == category:
                    cells.update(get_cells_for_item(a))
            return cells

        mover = ItemMover(mock_app_state, get_occupied, get_cells_for_item)
        mover.on_refresh = MagicMock()

        updated_notes = []
        mock_app_state.update_note = lambda n: updated_notes.append(n)

        # Action: Try to drop note at (0, 3)
        mover.handle_grid_drop("note-1", target_row=0, target_col=3)

        # Assert: Note should NOT have moved (swap rejected)
        assert len(updated_notes) == 0, "Note should not have moved - swap not possible"


class TestSwapPerformance:
    """Test swap operation performance."""

    def test_swap_completes_quickly(self, mock_app_state, get_cells_for_item):
        """Swap operation should complete in under 50ms."""
        import time

        app1 = MagicMock()
        app1.id = "app-1"
        app1.category = "Test"
        app1.grid_row = 0
        app1.grid_col = 0
        app1.col_span = 1
        app1.row_span = 1
        app1.name = "App 1"

        app2 = MagicMock()
        app2.id = "app-2"
        app2.category = "Test"
        app2.grid_row = 0
        app2.grid_col = 1
        app2.col_span = 1
        app2.row_span = 1
        app2.name = "App 2"

        mock_app_state.apps = [app1, app2]
        mock_app_state.notes = []

        def get_occupied(category):
            return {(0, 0), (0, 1)}

        mover = ItemMover(mock_app_state, get_occupied, get_cells_for_item)
        mover.on_refresh = MagicMock()

        start = time.perf_counter()
        mover.handle_grid_drop("app-1", target_row=0, target_col=1)
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 50, f"Swap took {elapsed:.2f}ms, should be under 50ms"

    def test_multiple_swaps_dont_accumulate_delay(self, mock_app_state, get_cells_for_item):
        """Multiple consecutive swaps should not slow down."""
        import time

        apps = []
        for i in range(5):
            app = MagicMock()
            app.id = f"app-{i}"
            app.category = "Test"
            app.grid_row = 0
            app.grid_col = i
            app.col_span = 1
            app.row_span = 1
            app.name = f"App {i}"
            apps.append(app)

        mock_app_state.apps = apps
        mock_app_state.notes = []

        def get_occupied(category):
            return {(0, i) for i in range(5)}

        mover = ItemMover(mock_app_state, get_occupied, get_cells_for_item)
        mover.on_refresh = MagicMock()

        times = []
        for i in range(5):
            target = (i + 1) % 5
            start = time.perf_counter()
            mover.handle_grid_drop(f"app-{i}", target_row=0, target_col=target)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        assert avg_time < 30, f"Average swap time {avg_time:.2f}ms should be under 30ms"
        assert max_time < 100, f"Max swap time {max_time:.2f}ms should be under 100ms"
