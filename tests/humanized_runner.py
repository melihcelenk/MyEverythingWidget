#!/usr/bin/env python3
"""
Humanized Test Runner

Runs grid tests written in human-readable DSL format.
Usage:
    python humanized_runner.py                    # Run all tests
    python humanized_runner.py swapNoteAndApp     # Run specific test
"""
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from unittest.mock import MagicMock, patch

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from window.models.note import Note, NoteType
from window.grid.mover import ItemMover


# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


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
class TestCase:
    """Parsed test case."""
    name: str
    rows: int = 5
    cols: int = 5
    initial_items: Dict[str, GridItem] = field(default_factory=dict)
    action_type: str = "drag"  # "drag" or "drop_pixel"
    action_item: str = ""
    action_target_row: int = 0
    action_target_col: int = 0
    action_pixel_x: int = 0
    action_pixel_y: int = 0
    expected_items: Dict[str, GridItem] = field(default_factory=dict)


def parse_test_file(filepath: Path) -> TestCase:
    """Parse a humanized test file."""
    test = TestCase(name=filepath.stem)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.strip().split('\n')
    current_section = None
    grid_lines = []

    for line in lines:
        line = line.rstrip()

        # Skip comments
        if line.strip().startswith('#'):
            continue

        # Parse headers
        if line.startswith('Rows:'):
            test.rows = int(line.split(':')[1].strip())
        elif line.startswith('Columns:'):
            test.cols = int(line.split(':')[1].strip())
        elif line.startswith('Initial:'):
            if current_section == 'expected' and grid_lines:
                test.expected_items = parse_grid(grid_lines, test.rows, test.cols)
            current_section = 'initial'
            grid_lines = []
        elif line.startswith('Action:'):
            if current_section == 'initial' and grid_lines:
                test.initial_items = parse_grid(grid_lines, test.rows, test.cols)
            current_section = 'action'
            grid_lines = []
        elif line.startswith('Expected:'):
            if current_section == 'initial' and grid_lines:
                test.initial_items = parse_grid(grid_lines, test.rows, test.cols)
            current_section = 'expected'
            grid_lines = []
        elif current_section == 'action' and line.strip():
            # Parse DropAtPixel(N1, x=350, y=90)
            pixel_match = re.search(r'DropAtPixel\((\w+),\s*x=(\d+),\s*y=(\d+)\)', line)
            if pixel_match:
                test.action_type = "drop_pixel"
                test.action_item = pixel_match.group(1)
                test.action_pixel_x = int(pixel_match.group(2))
                test.action_pixel_y = int(pixel_match.group(3))
            else:
                # Parse action: Drag(N1,R2C4) or Drag(N1) to R2C4
                match = re.search(r'Drag\((\w+)[,\s]+R(\d+)C(\d+)\)', line)
                if not match:
                    match = re.search(r'Drag\((\w+)\).*?R(\d+)C(\d+)', line)
                if match:
                    test.action_type = "drag"
                    test.action_item = match.group(1)
                    test.action_target_row = int(match.group(2)) - 1  # Convert to 0-indexed
                    test.action_target_col = int(match.group(3)) - 1
        elif current_section in ('initial', 'expected') and line.strip():
            grid_lines.append(line)

    # Parse final section
    if current_section == 'expected' and grid_lines:
        test.expected_items = parse_grid(grid_lines, test.rows, test.cols)
    elif current_section == 'initial' and grid_lines:
        test.initial_items = parse_grid(grid_lines, test.rows, test.cols)

    return test


def parse_grid(lines: List[str], rows: int, cols: int) -> Dict[str, GridItem]:
    """Parse grid lines into items."""
    items: Dict[str, GridItem] = {}
    item_positions: Dict[str, List[Tuple[int, int]]] = {}

    for row_idx, line in enumerate(lines):
        if row_idx >= rows:
            break

        cells = line.split()
        for col_idx, cell in enumerate(cells):
            if col_idx >= cols:
                break

            if cell in ('.', 'x', '_'):
                continue

            if cell not in item_positions:
                item_positions[cell] = []
            item_positions[cell].append((row_idx, col_idx))

    for item_id, positions in item_positions.items():
        if not positions:
            continue

        # Determine type from prefix
        if item_id.startswith('A'):
            item_type = 'app'
        elif item_id.startswith('N'):
            item_type = 'note'
        elif item_id.startswith('I'):
            item_type = 'image'
        else:
            item_type = 'unknown'

        min_row = min(p[0] for p in positions)
        max_row = max(p[0] for p in positions)
        min_col = min(p[1] for p in positions)
        max_col = max(p[1] for p in positions)

        items[item_id] = GridItem(
            id=item_id,
            item_type=item_type,
            row=min_row,
            col=min_col,
            row_span=max_row - min_row + 1,
            col_span=max_col - min_col + 1
        )

    return items


def create_mock_state(test: TestCase):
    """Create mock state from test case."""
    mock_state = MagicMock()
    mock_state.apps = []
    mock_state.notes = []
    mock_state.blockSignals = MagicMock()
    mock_state.state_changed = MagicMock()

    for item in test.initial_items.values():
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


def get_cells_for_item(item) -> Set[Tuple[int, int]]:
    """Get cells occupied by an item."""
    if item.grid_row is None or item.grid_col is None:
        return set()
    row_span = getattr(item, 'row_span', 1)
    col_span = getattr(item, 'col_span', 1)
    return {(r, c) for r in range(item.grid_row, item.grid_row + row_span)
            for c in range(item.grid_col, item.grid_col + col_span)}


def pos_to_cell(x: int, y: int, margin_left: int, margin_top: int,
                cell_width: int, cell_height: int, spacing: int,
                grid_cols: int, grid_rows: int) -> Tuple[int, int]:
    """Convert pixel position to grid cell - mirrors GridDropZone._pos_to_cell"""
    # Subtract margins
    x = x - margin_left
    y = y - margin_top

    if x < 0 or y < 0:
        return (0, 0)

    # Calculate cell
    cell_with_spacing = cell_width + spacing
    col = x // cell_with_spacing

    cell_height_with_spacing = cell_height + spacing
    row = y // cell_height_with_spacing

    # Clamp to grid bounds
    col = max(0, min(col, grid_cols - 1))
    row = max(0, min(row, grid_rows - 1))

    return (int(row), int(col))


def run_test(test: TestCase) -> Tuple[bool, Dict[str, GridItem], List[str]]:
    """Run a single test and return (passed, actual_items, errors)."""
    mock_state = create_mock_state(test)

    def get_occupied_cells(category):
        cells = set()
        for app in mock_state.apps:
            if app.category == category:
                cells.update(get_cells_for_item(app))
        for note in mock_state.notes:
            if note.category == category:
                cells.update(get_cells_for_item(note))
        return cells

    # Track updates
    updated_notes = []

    def capture_note_update(n):
        updated_notes.append(n)
        for i, existing in enumerate(mock_state.notes):
            if existing.id == n.id:
                mock_state.notes[i] = n
                break

    mock_state.update_note = capture_note_update

    # Grid constants (matching constants.py)
    CELL_WIDTH = 80
    CELL_HEIGHT = 80
    SPACING = 0
    MARGIN_LEFT = 4
    MARGIN_TOP = 4

    # Determine target row/col
    if test.action_type == "drop_pixel":
        # Convert pixel to cell like GridDropZone does
        row, col = pos_to_cell(
            test.action_pixel_x, test.action_pixel_y,
            MARGIN_LEFT, MARGIN_TOP,
            CELL_WIDTH, CELL_HEIGHT, SPACING,
            test.cols, test.rows
        )

        # Get item's span for clamping
        item = test.initial_items.get(test.action_item)
        if item:
            col_span = item.col_span
            row_span = item.row_span

            # Clamp like GridDropZone.dragMoveEvent does
            max_col = test.cols - col_span
            col = max(0, min(col, max_col))

            max_row = test.rows - row_span
            row = max(0, min(row, max_row))

        target_row = row
        target_col = col
    else:
        target_row = test.action_target_row
        target_col = test.action_target_col

    # Create mover with patched constants
    with patch('window.grid.mover.GRID_COLS', test.cols), \
            patch('window.grid.mover.GRID_ROWS', test.rows):

        item_mover = ItemMover(mock_state, get_occupied_cells, get_cells_for_item)
        item_mover.handle_grid_drop(
            test.action_item,
            target_row,
            target_col
        )

    # Build actual state
    actual_items: Dict[str, GridItem] = {}

    for app in mock_state.apps:
        actual_items[app.id] = GridItem(
            id=app.id,
            item_type='app',
            row=app.grid_row,
            col=app.grid_col,
            row_span=getattr(app, 'row_span', 1),
            col_span=getattr(app, 'col_span', 1)
        )

    for note in mock_state.notes:
        actual_items[note.id] = GridItem(
            id=note.id,
            item_type='note' if note.type == NoteType.TEXT else 'image',
            row=note.grid_row,
            col=note.grid_col,
            row_span=getattr(note, 'row_span', 1),
            col_span=getattr(note, 'col_span', 1)
        )

    # Compare with expected
    errors = []
    for item_id, expected in test.expected_items.items():
        if item_id not in actual_items:
            errors.append(f"{item_id}: not found in actual")
            continue

        actual = actual_items[item_id]
        if actual.row != expected.row or actual.col != expected.col:
            errors.append(
                f"{item_id}: position ({actual.row},{actual.col}) != expected ({expected.row},{expected.col})"
            )

    return len(errors) == 0, actual_items, errors


def grid_to_string(items: Dict[str, GridItem], rows: int, cols: int) -> List[List[str]]:
    """Convert items to grid representation."""
    grid = [['.' for _ in range(cols)] for _ in range(rows)]

    for item in items.values():
        for r in range(item.row, item.row + item.row_span):
            for c in range(item.col, item.col + item.col_span):
                if 0 <= r < rows and 0 <= c < cols:
                    grid[r][c] = item.id

    return grid


def print_comparison(test: TestCase, actual_items: Dict[str, GridItem], errors: List[str]):
    """Print expected vs actual with color highlighting."""
    expected_grid = grid_to_string(test.expected_items, test.rows, test.cols)
    actual_grid = grid_to_string(actual_items, test.rows, test.cols)

    print(f"\n{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}Test: {test.name}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")

    # Print Initial
    print(f"\n{Colors.BLUE}Initial:{Colors.RESET}")
    initial_grid = grid_to_string(test.initial_items, test.rows, test.cols)
    for row in initial_grid:
        print('  ' + ' '.join(f'{cell:2}' for cell in row))

    # Print Action
    print(f"\n{Colors.YELLOW}Action:{Colors.RESET}")
    print(f"  Drag({test.action_item}) to R{test.action_target_row + 1}C{test.action_target_col + 1}")

    # Print Expected with highlighting
    print(f"\n{Colors.GREEN}Expected:{Colors.RESET}")
    for r, row in enumerate(expected_grid):
        line = '  '
        for c, cell in enumerate(row):
            actual_cell = actual_grid[r][c] if r < len(actual_grid) and c < len(actual_grid[r]) else '?'
            if cell != actual_cell:
                line += f'{Colors.RED}{Colors.BOLD}{cell:2}{Colors.RESET} '
            else:
                line += f'{cell:2} '
        print(line)

    # Print Actual
    print(f"\n{Colors.WHITE}Actual:{Colors.RESET}")
    for r, row in enumerate(actual_grid):
        line = '  '
        for c, cell in enumerate(row):
            expected_cell = expected_grid[r][c] if r < len(expected_grid) and c < len(expected_grid[r]) else '?'
            if cell != expected_cell:
                line += f'{Colors.RED}{Colors.BOLD}{cell:2}{Colors.RESET} '
            else:
                line += f'{cell:2} '
        print(line)

    # Print errors
    if errors:
        print(f"\n{Colors.RED}Errors:{Colors.RESET}")
        for error in errors:
            print(f"  • {error}")


def find_test_files(test_name: Optional[str] = None) -> List[Path]:
    """Find test files in humanized directory."""
    humanized_dir = Path(__file__).parent / 'humanized'

    if not humanized_dir.exists():
        return []

    files = []
    for root, dirs, filenames in os.walk(humanized_dir):
        for filename in filenames:
            # Skip hidden files and __pycache__
            if filename.startswith('.') or '__pycache__' in root:
                continue

            filepath = Path(root) / filename

            if test_name:
                if filename == test_name or filepath.stem == test_name:
                    files.append(filepath)
            else:
                files.append(filepath)

    return files


def main():
    """Main entry point."""
    # Enable ANSI colors on Windows
    if sys.platform == 'win32':
        os.system('color')
        # Enable VT100 escape sequences
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    # Parse arguments
    verbose = '-v' in sys.argv or '--verbose' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    test_name = args[0] if args else None

    files = find_test_files(test_name)

    if not files:
        if test_name:
            print(f"{Colors.RED}Test not found: {test_name}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}No test files found in tests/humanized/{Colors.RESET}")
        sys.exit(1)

    passed = 0
    failed = 0

    for filepath in files:
        try:
            test = parse_test_file(filepath)
            success, actual_items, errors = run_test(test)

            if success:
                print(f"{Colors.GREEN}✓ {test.name}{Colors.RESET}")
                if verbose:
                    print_comparison(test, actual_items, errors)
                passed += 1
            else:
                print(f"{Colors.RED}✗ {test.name}{Colors.RESET}")
                print_comparison(test, actual_items, errors)
                failed += 1

        except Exception as e:
            print(f"{Colors.RED}✗ {filepath.stem}: {e}{Colors.RESET}")
            import traceback
            if verbose:
                traceback.print_exc()
            failed += 1

    print(f"\n{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    print(f"Results: {Colors.GREEN}{passed} passed{Colors.RESET}, {Colors.RED}{failed} failed{Colors.RESET}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
