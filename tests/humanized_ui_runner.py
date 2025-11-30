#!/usr/bin/env python3
"""
Humanized UI Test Runner

Runs grid tests with REAL UI:
1. Creates test category and items
2. Opens the app
3. Performs drag-drop
4. Verifies result
"""
import json
import os
import re
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except ImportError:
    print("ERROR: pyautogui not installed. Run: pip install pyautogui")
    sys.exit(1)

try:
    import pygetwindow as gw
except ImportError:
    print("ERROR: pygetwindow not installed. Run: pip install pygetwindow")
    sys.exit(1)

from window.grid.constants import (
    CELL_WIDTH, CELL_HEIGHT, SPACING,
    MARGIN_LEFT
)

# State file path - use test-specific state in project folder
STATE_FILE = PROJECT_ROOT / "tests" / "test_app_state.json"
BACKUP_FILE = PROJECT_ROOT / "tests" / "test_app_state_backup.json"


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
    id: str
    item_type: str
    row: int
    col: int
    row_span: int = 1
    col_span: int = 1


@dataclass
class TestCase:
    name: str
    rows: int = 5
    cols: int = 5
    initial_items: Dict[str, GridItem] = field(default_factory=dict)
    action_item: str = ""
    action_target_row: int = 0
    action_target_col: int = 0
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
        if line.strip().startswith('#'):
            continue

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
            match = re.search(r'Drag\((\w+)[,\s]+R(\d+)C(\d+)\)', line)
            if not match:
                match = re.search(r'Drag\((\w+)\).*?R(\d+)C(\d+)', line)
            if match:
                test.action_item = match.group(1)
                test.action_target_row = int(match.group(2)) - 1
                test.action_target_col = int(match.group(3)) - 1
        elif current_section in ('initial', 'expected') and line.strip():
            grid_lines.append(line)

    if grid_lines:
        if current_section == 'expected':
            test.expected_items = parse_grid(grid_lines, test.rows, test.cols)
        elif current_section == 'initial':
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


def backup_state():
    """No backup needed - we use separate test state file."""
    pass


def restore_state():
    """Reset test state to empty."""
    STATE_FILE.write_text('{"categories":[],"apps":[],"notes":[]}', encoding='utf-8')
    print(f"  {Colors.CYAN}Test state reset{Colors.RESET}")


def create_test_state(test: TestCase) -> dict:
    """Create CLEAN state.json with ONLY test data - removes all existing categories."""
    test_category_id = "test-category-" + str(uuid.uuid4())[:8]

    # Only Test category - nothing else
    categories = [
        {"id": test_category_id, "name": "Test", "icon": "🧪"}
    ]

    apps = []
    notes = []

    now = datetime.now(timezone.utc).isoformat()

    for item_id, item in test.initial_items.items():
        if item.item_type == 'app':
            apps.append({
                "id": f"test-app-{item_id}",
                "name": f"App {item_id}",
                "icon_path": "📱",
                "target": "https://example.com",
                "category": "Test",
                "type": "url",
                "order": 0,
                "grid_row": item.row,
                "grid_col": item.col,
                "col_span": item.col_span,
                "row_span": item.row_span
            })
        elif item.item_type in ('note', 'image'):
            notes.append({
                "id": f"test-note-{item_id}",
                "content": f"Note {item_id}",
                "type": "image" if item.item_type == 'image' else "text",
                "category": "Test",
                "created_at": now,
                "updated_at": now,
                "order": 0,
                "grid_row": item.row,
                "grid_col": item.col,
                "col_span": item.col_span,
                "row_span": item.row_span
            })

    # Return ONLY test data - this completely replaces the old state
    return {
        "categories": categories,
        "apps": apps,
        "notes": notes
    }


def write_test_state(state: dict):
    """Write state to state.json."""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)
    print(f"  {Colors.GREEN}Test state created{Colors.RESET}")


def start_app() -> subprocess.Popen:
    """Start the application in TEST MODE."""
    print(f"  {Colors.CYAN}Starting app in test mode...{Colors.RESET}")

    # Set environment variable for test state
    os.environ["MEW_STATE_PATH"] = str(STATE_FILE)

    # Start new instance using shell
    python_exe = str(PROJECT_ROOT / ".venv" / "Scripts" / "python.exe")
    main_py = str(PROJECT_ROOT / "main.py")

    proc = subprocess.Popen(
        f'"{python_exe}" "{main_py}"',
        shell=True,
        cwd=str(PROJECT_ROOT)
    )

    # Wait for window
    print(f"  {Colors.CYAN}Waiting for window...{Colors.RESET}")
    for i in range(50):  # 5 seconds timeout
        time.sleep(0.1)
        try:
            windows = gw.getWindowsWithTitle("My Everything")
            if windows:
                time.sleep(0.5)
                print(f"  {Colors.GREEN}Window found!{Colors.RESET}")
                return proc
        except Exception:
            pass

    raise RuntimeError("App window did not appear")


def find_window() -> Tuple[int, int]:
    """Find window and return (x, y)."""
    windows = gw.getWindowsWithTitle("My Everything")
    if not windows:
        raise RuntimeError("Window not found")

    win = windows[0]
    try:
        win.activate()
    except Exception:
        pass  # Ignore activation errors
    time.sleep(0.3)

    return win.left, win.top


def click_test_tab(win_x: int, win_y: int):
    """Click on the Test tab."""
    # Tab is approximately at y=45 from window top
    # First tab starts at x~40
    tab_x = win_x + 50
    tab_y = win_y + 55

    print(f"  {Colors.CYAN}Clicking Test tab at ({tab_x}, {tab_y})...{Colors.RESET}")
    pyautogui.click(tab_x, tab_y)
    time.sleep(0.3)


def build_actual_items(state: dict, test: TestCase) -> Dict[str, GridItem]:
    """Build GridItem dict from actual state."""
    items = {}

    for app in state.get("apps", []):
        # Extract ID suffix (e.g., "test-app-A1" -> "A1")
        app_id = app["id"]
        if app_id.startswith("test-app-"):
            short_id = app_id.replace("test-app-", "")
        else:
            short_id = app_id

        items[short_id] = GridItem(
            id=short_id,
            item_type='app',
            row=app.get("grid_row", 0),
            col=app.get("grid_col", 0),
            row_span=app.get("row_span", 1),
            col_span=app.get("col_span", 1)
        )

    for note in state.get("notes", []):
        note_id = note["id"]
        if note_id.startswith("test-note-"):
            short_id = note_id.replace("test-note-", "")
        else:
            short_id = note_id

        items[short_id] = GridItem(
            id=short_id,
            item_type='note',
            row=note.get("grid_row", 0),
            col=note.get("grid_col", 0),
            row_span=note.get("row_span", 1),
            col_span=note.get("col_span", 1)
        )

    return items


def compare_results(expected: Dict[str, GridItem], actual: Dict[str, GridItem]) -> bool:
    """Compare expected and actual items."""
    for item_id, exp in expected.items():
        if item_id not in actual:
            return False
        act = actual[item_id]
        if exp.row != act.row or exp.col != act.col:
            return False
    return True


def show_differences(expected: Dict[str, GridItem], actual: Dict[str, GridItem]):
    """Show differences between expected and actual."""
    for item_id, exp in expected.items():
        if item_id not in actual:
            print(f"  {Colors.RED}{item_id}: not found in actual{Colors.RESET}")
        else:
            act = actual[item_id]
            if exp.row != act.row or exp.col != act.col:
                print(
                    f"  {Colors.RED}{item_id}: expected ({exp.row},{exp.col}) but got ({act.row},{act.col}){Colors.RESET}")


def cell_to_pixel(row: int, col: int, win_x: int, win_y: int) -> Tuple[int, int]:
    """Convert grid cell to screen pixel coordinates."""
    TITLE_BAR_HEIGHT = 32
    TAB_HEIGHT = 32
    QUICK_NOTE_HEIGHT = 40
    
    grid_offset_y = TITLE_BAR_HEIGHT + TAB_HEIGHT + QUICK_NOTE_HEIGHT
    grid_offset_x = MARGIN_LEFT
    
    cell_stride_w = CELL_WIDTH + SPACING
    cell_stride_h = CELL_HEIGHT + SPACING

    x = win_x + grid_offset_x + col * cell_stride_w + CELL_WIDTH // 2
    y = win_y + grid_offset_y + row * cell_stride_h + CELL_HEIGHT // 2
    
    return x, y


def perform_drag(source: GridItem, target_row: int, target_col: int, win_x: int, win_y: int):
    """Perform drag-drop operation."""
    source_x, source_y = cell_to_pixel(source.row, source.col, win_x, win_y)
    target_x, target_y = cell_to_pixel(target_row, target_col, win_x, win_y)

    print(f"  {Colors.YELLOW}Dragging from ({source_x}, {source_y}) to ({target_x}, {target_y}){Colors.RESET}")

    pyautogui.moveTo(source_x, source_y, duration=0.3)
    time.sleep(0.1)

    pyautogui.mouseDown()
    time.sleep(0.1)

    pyautogui.moveTo(target_x, target_y, duration=0.4)
    time.sleep(0.1)

    pyautogui.mouseUp()
    time.sleep(0.3)


def run_ui_test(test: TestCase) -> bool:
    """Run a single UI test."""
    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}  TEST: {test.name}{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")

    # Print initial state
    print(f"\n{Colors.BLUE}Initial:{Colors.RESET}")
    for r in range(test.rows):
        row_str = "  "
        for c in range(test.cols):
            found = None
            for item_id, item in test.initial_items.items():
                if item.row <= r < item.row + item.row_span and item.col <= c < item.col + item.col_span:
                    found = item_id
                    break
            row_str += f"{found or '.':3}"
        print(row_str)

    # Print action
    source_item = test.initial_items.get(test.action_item)
    print(
        f"\n{Colors.YELLOW}Action: Drag({test.action_item}) to R{test.action_target_row + 1}C{test.action_target_col + 1}{Colors.RESET}")

    # Print expected
    print(f"\n{Colors.GREEN}Expected:{Colors.RESET}")
    for r in range(test.rows):
        row_str = "  "
        for c in range(test.cols):
            found = None
            for item_id, item in test.expected_items.items():
                if item.row <= r < item.row + item.row_span and item.col <= c < item.col + item.col_span:
                    found = item_id
                    break
            row_str += f"{found or '.':3}"
        print(row_str)

    print(f"\n{Colors.CYAN}Setting up...{Colors.RESET}")

    # Backup state
    backup_state()
    
    try:
        # Create test state
        state = create_test_state(test)
        write_test_state(state)

        # Start app
        proc = start_app()

        # Find window
        win_x, win_y = find_window()
        print(f"  {Colors.GREEN}Window at ({win_x}, {win_y}){Colors.RESET}")

        # Click Test tab
        click_test_tab(win_x, win_y)

        # Perform drag
        if source_item:
            print(f"\n{Colors.YELLOW}Performing drag-drop...{Colors.RESET}")
            perform_drag(source_item, test.action_target_row, test.action_target_col, win_x, win_y)

        # Wait for state to save
        time.sleep(2)

        # Read actual state
        print(f"\n  {Colors.CYAN}Reading state from: {STATE_FILE}{Colors.RESET}")
        state_content = STATE_FILE.read_text(encoding='utf-8')
        actual_state = json.loads(state_content)

        # Debug: show actual positions
        for note in actual_state.get("notes", []):
            print(
                f"  {Colors.CYAN}Note {note['id']}: row={note.get('grid_row')}, col={note.get('grid_col')}{Colors.RESET}")
        actual_items = build_actual_items(actual_state, test)

        # Print actual result
        print(f"\n{Colors.WHITE}Actual:{Colors.RESET}")
        for r in range(test.rows):
            row_str = "  "
            for c in range(test.cols):
                found = None
                for item_id, item in actual_items.items():
                    if item.row <= r < item.row + item.row_span and item.col <= c < item.col + item.col_span:
                        found = item_id
                        break
                row_str += f"{found or '.':3}"
            print(row_str)

        # Compare and show result
        passed = compare_results(test.expected_items, actual_items)

        if passed:
            print(f"\n{Colors.GREEN}✓ TEST PASSED{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}✗ TEST FAILED{Colors.RESET}")
            show_differences(test.expected_items, actual_items)

        # Kill app
        proc.terminate()
        time.sleep(0.3)

        return passed

    finally:
        # Restore state
        restore_state()


def find_test_files(test_name: Optional[str] = None) -> List[Path]:
    """Find test files in humanized directory."""
    humanized_dir = Path(__file__).parent / 'humanized'

    if not humanized_dir.exists():
        return []

    files = []
    for root, dirs, filenames in os.walk(humanized_dir):
        for filename in filenames:
            if filename.startswith('.') or '__pycache__' in root or filename.endswith('_REAL'):
                continue
            filepath = Path(root) / filename
            if test_name:
                if filename == test_name or filepath.stem == test_name:
                    files.append(filepath)
            else:
                files.append(filepath)

    return files


def main():
    if sys.platform == 'win32':
        os.system('color')
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass

    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    test_name = args[0] if args else None

    files = find_test_files(test_name)

    if not files:
        if test_name:
            print(f"{Colors.RED}Test not found: {test_name}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}No test files found in tests/humanized/{Colors.RESET}")
        sys.exit(1)

    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}  HUMANIZED UI TEST RUNNER{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"\n  This will:")
    print(f"  1. Backup your current state")
    print(f"  2. Create test items")
    print(f"  3. Open the app")
    print(f"  4. Perform drag-drop")
    print(f"  5. Restore your state\n")
    
    for filepath in files:
        try:
            test = parse_test_file(filepath)
            run_ui_test(test)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Stopped by user.{Colors.RESET}")
            restore_state()
            break
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
            import traceback
            traceback.print_exc()
            restore_state()


if __name__ == '__main__':
    main()
