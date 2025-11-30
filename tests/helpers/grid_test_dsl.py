"""
GridTestDSL - Domain Specific Language for Grid Tests.

Allows writing readable grid tests with visual notation.

Example:
    ```
    Rows: 5
    Columns: 5

    Initial:
    A1 A2 .  .  .
    .  N1 N1 .  A3
    .  .  .  .  .

    Action: Drag(N1) to R2C4

    Expected:
    A1 A2 .  .  .
    .  A3 .  N1 N1
    .  .  .  .  .
    ```
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from unittest.mock import MagicMock

from models.note import Note, NoteType


@dataclass
class GridItem:
    """Represents an item in the grid."""
    id: str
    item_type: str  # 'app', 'note', 'image'
    row: int
    col: int
    row_span: int = 1
    col_span: int = 1


@dataclass
class DragAction:
    """Represents a drag action."""
    item_id: str
    target_row: int
    target_col: int


@dataclass
class CreateAction:
    """Represents a create action."""
    item_type: str  # 'NOTE' or 'APP'
    content: str  # Note content or app name
    item_id: str  # ID to assign (e.g., 'N1', 'A1')


@dataclass
class GridState:
    """Represents grid state."""
    rows: int
    cols: int
    items: Dict[str, GridItem] = field(default_factory=dict)

    def get_item_at(self, row: int, col: int) -> Optional[GridItem]:
        """Find item at position."""
        for item in self.items.values():
            for r in range(item.row, item.row + item.row_span):
                for c in range(item.col, item.col + item.col_span):
                    if r == row and c == col:
                        return item
        return None

    def to_grid_string(self) -> str:
        """Convert state to visual grid string."""
        grid = [['.' for _ in range(self.cols)] for _ in range(self.rows)]

        for item in self.items.values():
            for r in range(item.row, item.row + item.row_span):
                for c in range(item.col, item.col + item.col_span):
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        grid[r][c] = item.id

        lines = []
        for row in grid:
            lines.append(' '.join(f'{cell:2}' for cell in row))
        return '\n'.join(lines)


class GridTestDSL:
    """Parser and executor for grid test DSL."""

    def __init__(self):
        self.rows = 5
        self.cols = 5
        self.initial_state: GridState = None
        self.expected_state: GridState = None
        self.actions: List[DragAction | CreateAction] = []

    def parse(self, dsl_text: str) -> 'GridTestDSL':
        """Parse DSL text and return self for chaining."""
        lines = dsl_text.strip().split('\n')

        current_section = None
        section_lines = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Check for section headers
            if line.startswith('Rows:'):
                self.rows = int(line.split(':')[1].strip())
            elif line.startswith('Columns:'):
                self.cols = int(line.split(':')[1].strip())
            elif line.startswith('Initial:'):
                current_section = 'initial'
                section_lines = []
            elif line.startswith('Expected:'):
                if current_section == 'initial' and section_lines:
                    self.initial_state = self._parse_grid(section_lines)
                current_section = 'expected'
                section_lines = []
            elif line.startswith('Action:'):
                if current_section == 'initial' and section_lines:
                    self.initial_state = self._parse_grid(section_lines)
                current_section = 'action'
                section_lines = []
            elif current_section == 'action':
                # Parse action line
                action = self._parse_action(line)
                if action:
                    self.actions.append(action)
            elif current_section in ('initial', 'expected'):
                section_lines.append(line)

        # Parse final section based on what's left
        if section_lines:
            if current_section == 'expected':
                self.expected_state = self._parse_grid(section_lines)
            elif current_section == 'initial':
                self.initial_state = self._parse_grid(section_lines)

        return self

    def _parse_grid(self, lines: List[str]) -> GridState:
        """Parse grid lines into GridState."""
        state = GridState(rows=self.rows, cols=self.cols)

        # Track multi-cell items
        item_positions: Dict[str, List[Tuple[int, int]]] = {}

        for row_idx, line in enumerate(lines):
            if row_idx >= self.rows:
                break

            cells = line.split()
            for col_idx, cell in enumerate(cells):
                if col_idx >= self.cols:
                    break

                if cell in ('.', 'x', '_'):
                    continue

                if cell not in item_positions:
                    item_positions[cell] = []
                item_positions[cell].append((row_idx, col_idx))

        # Create items from positions
        for item_id, positions in item_positions.items():
            if not positions:
                continue

            # Determine item type from prefix
            if item_id.startswith('A'):
                item_type = 'app'
            elif item_id.startswith('N'):
                item_type = 'note'
            elif item_id.startswith('I'):
                item_type = 'image'
            else:
                item_type = 'unknown'

            # Calculate bounds
            min_row = min(p[0] for p in positions)
            max_row = max(p[0] for p in positions)
            min_col = min(p[1] for p in positions)
            max_col = max(p[1] for p in positions)

            state.items[item_id] = GridItem(
                id=item_id,
                item_type=item_type,
                row=min_row,
                col=min_col,
                row_span=max_row - min_row + 1,
                col_span=max_col - min_col + 1
            )

        return state

    def _parse_action(self, line: str) -> Optional[DragAction | CreateAction]:
        """Parse action line."""
        line = line.strip()
        if not line:
            return None

        # Format: Drag(N1) to R2C4
        drag_match = re.search(r'Drag\((\w+)\).*?R(\d+)C(\d+)', line)
        if drag_match:
            item_id = drag_match.group(1)
            # Convert to 0-based index
            target_row = int(drag_match.group(2)) - 1
            target_col = int(drag_match.group(3)) - 1
            return DragAction(item_id, target_row, target_col)

        # Format: Create(NOTE, "content", N1) or Create(APP, "name", A1)
        create_match = re.search(r'Create\((\w+),\s*"([^"]+)",\s*(\w+)\)', line)
        if create_match:
            item_type = create_match.group(1)
            content = create_match.group(2)
            item_id = create_match.group(3)
            return CreateAction(item_type, content, item_id)
        
        return None

    def create_mock_state(self) -> MagicMock:
        """Create mock AppState from initial state."""
        mock_state = MagicMock()
        mock_state.apps = []
        mock_state.notes = []
        mock_state.blockSignals = MagicMock()

        for item in self.initial_state.items.values():
            if item.item_type == 'app':
                app = MagicMock()
                app.id = item.id
                app.category = "Test"
                app.grid_row = item.row
                app.grid_col = item.col
                app.col_span = item.col_span
                app.row_span = item.row_span
                app.name = f"App {item.id}"
                mock_state.apps.append(app)
            elif item.item_type in ('note', 'image'):
                note_type = NoteType.IMAGE if item.item_type == 'image' else NoteType.TEXT
                note = Note(
                    id=item.id,
                    content=f"Content {item.id}",
                    type=note_type,
                    category="Test",
                    grid_row=item.row,
                    grid_col=item.col,
                    col_span=item.col_span,
                    row_span=item.row_span
                )
                mock_state.notes.append(note)

        return mock_state

    def get_cells_for_item(self, item) -> Set[Tuple[int, int]]:
        """Get cells occupied by an item."""
        if item.grid_row is None or item.grid_col is None:
            return set()
        row_span = getattr(item, 'row_span', 1)
        col_span = getattr(item, 'col_span', 1)
        return {(r, c) for r in range(item.grid_row, item.grid_row + row_span)
                for c in range(item.grid_col, item.grid_col + col_span)}

    def get_occupied_cells(self, mock_state, category: str) -> Set[Tuple[int, int]]:
        """Get all occupied cells."""
        cells = set()
        for app in mock_state.apps:
            if app.category == category:
                cells.update(self.get_cells_for_item(app))
        for note in mock_state.notes:
            if note.category == category:
                cells.update(self.get_cells_for_item(note))
        return cells

    def verify_expected(self, mock_state, updated_notes: List) -> Tuple[bool, str]:
        """Verify state matches expected."""
        errors = []

        # Build actual state
        actual_items = {}

        for app in mock_state.apps:
            actual_items[app.id] = GridItem(
                id=app.id,
                item_type='app',
                row=app.grid_row,
                col=app.grid_col,
                row_span=getattr(app, 'row_span', 1),
                col_span=getattr(app, 'col_span', 1)
            )

        # Use updated notes if available
        note_map = {n.id: n for n in mock_state.notes}
        for updated in updated_notes:
            note_map[updated.id] = updated

        for note in note_map.values():
            actual_items[note.id] = GridItem(
                id=note.id,
                item_type='note' if note.type == NoteType.TEXT else 'image',
                row=note.grid_row,
                col=note.grid_col,
                row_span=getattr(note, 'row_span', 1),
                col_span=getattr(note, 'col_span', 1)
            )

        # Compare with expected
        for item_id, expected in self.expected_state.items.items():
            if item_id not in actual_items:
                errors.append(f"Item {item_id} not found in actual state")
                continue

            actual = actual_items[item_id]
            if actual.row != expected.row:
                errors.append(f"{item_id}: row {actual.row} != expected {expected.row}")
            if actual.col != expected.col:
                errors.append(f"{item_id}: col {actual.col} != expected {expected.col}")

        if errors:
            # Build visual comparison
            actual_state = GridState(rows=self.rows, cols=self.cols, items=actual_items)
            comparison = f"\nExpected:\n{self.expected_state.to_grid_string()}\n\nActual:\n{actual_state.to_grid_string()}"
            return False, '\n'.join(errors) + comparison

        return True, "OK"
