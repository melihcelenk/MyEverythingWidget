"""
Grid swap tests using DSL format.

Tests the 2x1 note swap positioning bug reported by user.
"""
from unittest.mock import patch

from tests.helpers.grid_test_dsl import GridTestDSL
from window.grid.mover import ItemMover


def create_item_mover(dsl):
    """Create ItemMover with proper callbacks for DSL-based testing."""
    mock_state = dsl.create_mock_state()

    def get_occupied_cells(category):
        cells = set()
        for app in mock_state.apps:
            if app.category == category:
                cells.update(dsl.get_cells_for_item(app))
        for note in mock_state.notes:
            if note.category == category:
                cells.update(dsl.get_cells_for_item(note))
        return cells

    def get_cells_for_item(item):
        return dsl.get_cells_for_item(item)

    item_mover = ItemMover(mock_state, get_occupied_cells, get_cells_for_item)

    return mock_state, item_mover


class TestSwapWithDSL:
    """Tests using Grid DSL format."""

    @patch('window.grid.mover.GRID_COLS', 5)
    @patch('window.grid.mover.GRID_ROWS', 5)
    def test_2x1_note_swap_with_1x1_app_at_right_edge(self):
        """
        2x1 notu en sağa taşırken 1x1 app ile swap.
        Not col 3-4'e gitmeli (0-indexed), app notun eski yerine gitmeli.
        """
        dsl = GridTestDSL().parse("""
            Rows: 5
            Columns: 5
            
            Initial:
            .  .  .  .  .
            N1 N1 .  .  A1
            .  .  .  .  .
            .  .  .  .  .
            .  .  .  .  .
            
            Action: Drag(N1) to R2C4
            
            Expected:
            .  .  .  .  .
            A1 .  .  N1 N1
            .  .  .  .  .
            .  .  .  .  .
            .  .  .  .  .
        """)

        # Verify parse worked
        assert dsl.initial_state is not None
        assert 'N1' in dsl.initial_state.items
        assert 'A1' in dsl.initial_state.items

        n1 = dsl.initial_state.items['N1']
        assert n1.row == 1
        assert n1.col == 0
        assert n1.col_span == 2

        a1 = dsl.initial_state.items['A1']
        assert a1.row == 1
        assert a1.col == 4

        # Create mock state and mover
        mock_state, item_mover = create_item_mover(dsl)

        # Track updates
        updated_notes = []
        original_update_note = mock_state.update_note

        def capture_update(n):
            updated_notes.append(n)
            # Also update mock_state.notes for consistency
            for i, existing in enumerate(mock_state.notes):
                if existing.id == n.id:
                    mock_state.notes[i] = n
                    break

        mock_state.update_note = capture_update

        # Get the note to drag
        note = [n for n in mock_state.notes if n.id == 'N1'][0]

        # Perform drag - target is R2C4 (0-indexed: row=1, col=3)
        target_row = dsl.action.target_row  # 1
        target_col = dsl.action.target_col  # 3

        item_mover.handle_grid_drop('N1', target_row, target_col)

        # Verify positions
        success, message = dsl.verify_expected(mock_state, updated_notes)
        assert success, message

    @patch('window.grid.mover.GRID_COLS', 3)
    @patch('window.grid.mover.GRID_ROWS', 3)
    def test_simple_1x1_swap(self):
        """İki 1x1 app swap testi."""
        dsl = GridTestDSL().parse("""
            Rows: 3
            Columns: 3
            
            Initial:
            A1 .  A2
            .  .  .
            .  .  .
            
            Action: Drag(A1) to R1C3
            
            Expected:
            A2 .  A1
            .  .  .
            .  .  .
        """)

        mock_state, item_mover = create_item_mover(dsl)

        item_mover.handle_grid_drop('A1', 0, 2)

        # A1 should be at (0, 2)
        a1 = [a for a in mock_state.apps if a.id == 'A1'][0]
        assert a1.grid_row == 0
        assert a1.grid_col == 2

        # A2 should be at (0, 0)
        a2 = [a for a in mock_state.apps if a.id == 'A2'][0]
        assert a2.grid_row == 0
        assert a2.grid_col == 0

    @patch('window.grid.mover.GRID_COLS', 3)
    @patch('window.grid.mover.GRID_ROWS', 3)
    def test_move_to_empty_cell(self):
        """Boş hücreye taşıma testi."""
        dsl = GridTestDSL().parse("""
            Rows: 3
            Columns: 3
            
            Initial:
            A1 .  .
            .  .  .
            .  .  .
            
            Action: Drag(A1) to R2C2
            
            Expected:
            .  .  .
            .  A1 .
            .  .  .
        """)

        mock_state, item_mover = create_item_mover(dsl)

        item_mover.handle_grid_drop('A1', 1, 1)

        a1 = [a for a in mock_state.apps if a.id == 'A1'][0]
        assert a1.grid_row == 1
        assert a1.grid_col == 1

    @patch('window.grid.mover.GRID_COLS', 5)
    @patch('window.grid.mover.GRID_ROWS', 5)
    def test_2x1_move_to_empty(self):
        """2x1 notu boş alana taşıma."""
        dsl = GridTestDSL().parse("""
            Rows: 5
            Columns: 5
            
            Initial:
            N1 N1 .  .  .
            .  .  .  .  .
            .  .  .  .  .
            .  .  .  .  .
            .  .  .  .  .
            
            Action: Drag(N1) to R2C4
            
            Expected:
            .  .  .  .  .
            .  .  .  N1 N1
            .  .  .  .  .
            .  .  .  .  .
            .  .  .  .  .
        """)

        mock_state, item_mover = create_item_mover(dsl)

        updated_notes = []

        def capture_update(n):
            updated_notes.append(n)
            for i, existing in enumerate(mock_state.notes):
                if existing.id == n.id:
                    mock_state.notes[i] = n
                    break

        mock_state.update_note = capture_update

        item_mover.handle_grid_drop('N1', 1, 3)

        # Note should be at row 1, col 3-4
        assert len(updated_notes) > 0
        final_note = updated_notes[-1]
        assert final_note.grid_row == 1
        assert final_note.grid_col == 3

    @patch('window.grid.mover.GRID_COLS', 3)
    @patch('window.grid.mover.GRID_ROWS', 3)
    def test_swap_rejected_when_overflow(self):
        """2x1 grid dışına taşıyamaz."""
        dsl = GridTestDSL().parse("""
            Rows: 3
            Columns: 3
            
            Initial:
            N1 N1 A1
            .  .  .
            .  .  .
            
            Action: Drag(N1) to R1C3
            
            Expected:
            N1 N1 A1
            .  .  .
            .  .  .
        """)

        mock_state, item_mover = create_item_mover(dsl)

        # Try to move 2x1 note to col 2 - would need cols 2-3, but col 3 is out of bounds
        item_mover.handle_grid_drop('N1', 0, 2)

        # Should be rejected - 2x1 can't fit at col 2 (would overflow)
        n1 = mock_state.notes[0]
        assert n1.grid_row == 0
        assert n1.grid_col == 0  # Should stay at original position


class TestDSLParser:
    """Test DSL parser functionality."""

    def test_parse_grid_dimensions(self):
        """Grid boyutları parse edilmeli."""
        dsl = GridTestDSL().parse("""
            Rows: 3
            Columns: 4
            
            Initial:
            .  .  .  .
            .  .  .  .
            .  .  .  .
        """)

        assert dsl.rows == 3
        assert dsl.cols == 4

    def test_parse_single_items(self):
        """Tekli itemlar parse edilmeli."""
        dsl = GridTestDSL().parse("""
            Rows: 3
            Columns: 3
            
            Initial:
            A1 .  A2
            .  N1 .
            I1 .  .
        """)

        assert len(dsl.initial_state.items) == 4

        assert dsl.initial_state.items['A1'].row == 0
        assert dsl.initial_state.items['A1'].col == 0

        assert dsl.initial_state.items['A2'].row == 0
        assert dsl.initial_state.items['A2'].col == 2

        assert dsl.initial_state.items['N1'].row == 1
        assert dsl.initial_state.items['N1'].col == 1

        assert dsl.initial_state.items['I1'].row == 2
        assert dsl.initial_state.items['I1'].col == 0

    def test_parse_multi_span_horizontal(self):
        """Yatay span parse edilmeli."""
        dsl = GridTestDSL().parse("""
            Rows: 3
            Columns: 5
            
            Initial:
            N1 N1 N1 .  .
            .  .  .  .  .
            .  .  .  .  .
        """)

        n1 = dsl.initial_state.items['N1']
        assert n1.row == 0
        assert n1.col == 0
        assert n1.col_span == 3
        assert n1.row_span == 1

    def test_parse_multi_span_vertical(self):
        """Dikey span parse edilmeli."""
        dsl = GridTestDSL().parse("""
            Rows: 3
            Columns: 3
            
            Initial:
            N1 .  .
            N1 .  .
            .  .  .
        """)

        n1 = dsl.initial_state.items['N1']
        assert n1.row == 0
        assert n1.col == 0
        assert n1.col_span == 1
        assert n1.row_span == 2

    def test_parse_action(self):
        """Action parse edilmeli."""
        dsl = GridTestDSL().parse("""
            Rows: 3
            Columns: 3
            
            Initial:
            A1 .  .
            .  .  .
            .  .  .
            
            Action: Drag(A1) to R2C3
            
            Expected:
            .  .  .
            .  .  A1
            .  .  .
        """)

        assert dsl.action is not None
        assert dsl.action.item_id == 'A1'
        assert dsl.action.target_row == 1  # R2 = index 1
        assert dsl.action.target_col == 2  # C3 = index 2

    def test_grid_to_string(self):
        """Grid state görsel formata dönüştürülebilmeli."""
        dsl = GridTestDSL().parse("""
            Rows: 2
            Columns: 3
            
            Initial:
            A1 N1 N1
            .  .  .
        """)

        grid_str = dsl.initial_state.to_grid_string()
        assert 'A1' in grid_str
        assert 'N1' in grid_str
