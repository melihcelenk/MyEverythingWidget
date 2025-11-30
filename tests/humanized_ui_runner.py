#!/usr/bin/env python3
"""
Humanized UI Test Runner

Runs grid tests with REAL UI - opens the app, performs drag-drop, shows results.
Usage:
    python humanized_ui_runner.py                    # Run all tests
    python humanized_ui_runner.py swapNoteAndApp     # Run specific test
"""
import os
import re
import sys
import time
from dataclasses import dataclass, field
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
    from PIL import ImageGrab
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

from window.grid.constants import (
    CELL_WIDTH, CELL_HEIGHT, SPACING,
    MARGIN_LEFT
)


# ANSI colors
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
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


def cell_to_pixel(row: int, col: int, window_x: int, window_y: int) -> Tuple[int, int]:
    """Convert grid cell to screen pixel coordinates."""
    # Window title bar offset (approximate)
    TITLE_BAR_HEIGHT = 70
    TAB_HEIGHT = 40
    QUICK_NOTE_HEIGHT = 35

    grid_offset_y = TITLE_BAR_HEIGHT + TAB_HEIGHT + QUICK_NOTE_HEIGHT
    grid_offset_x = MARGIN_LEFT + 5

    cell_stride_w = CELL_WIDTH + SPACING
    cell_stride_h = CELL_HEIGHT + SPACING

    x = window_x + grid_offset_x + col * cell_stride_w + CELL_WIDTH // 2
    y = window_y + grid_offset_y + row * cell_stride_h + CELL_HEIGHT // 2

    return x, y


def find_window(title: str) -> Optional[Tuple[int, int, int, int]]:
    """Find window by title and return (x, y, width, height)."""
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title)
        if windows:
            win = windows[0]
            return (win.left, win.top, win.width, win.height)
    except:
        pass
    return None


def run_ui_test(test: TestCase):
    """Run a single UI test."""
    print(f"\n{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}Test: {test.name}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")

    # Print test details
    print(f"\n{Colors.BLUE}Initial State:{Colors.RESET}")
    for item_id, item in test.initial_items.items():
        print(f"  {item_id}: ({item.row},{item.col}) span={item.col_span}x{item.row_span}")

    print(f"\n{Colors.YELLOW}Action:{Colors.RESET}")
    source_item = test.initial_items.get(test.action_item)
    if source_item:
        print(
            f"  Drag {test.action_item} from ({source_item.row},{source_item.col}) to ({test.action_target_row},{test.action_target_col})")

    print(f"\n{Colors.GREEN}Expected:{Colors.RESET}")
    for item_id, item in test.expected_items.items():
        print(f"  {item_id}: ({item.row},{item.col})")

    # Find window
    print(f"\n{Colors.CYAN}Looking for 'My Everything' window...{Colors.RESET}")

    win_info = find_window("My Everything")
    if not win_info:
        print(f"{Colors.RED}Window not found! Make sure the app is running.{Colors.RESET}")
        return False

    win_x, win_y, win_w, win_h = win_info
    print(f"  Found at ({win_x}, {win_y})")

    # Bring window to front
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle("My Everything")
        if windows:
            windows[0].activate()
            time.sleep(0.3)
    except:
        pass

    if not source_item:
        print(f"{Colors.RED}Source item {test.action_item} not found in initial state!{Colors.RESET}")
        return False

    # Calculate pixel positions
    source_x, source_y = cell_to_pixel(source_item.row, source_item.col, win_x, win_y)
    target_x, target_y = cell_to_pixel(test.action_target_row, test.action_target_col, win_x, win_y)

    print(f"\n{Colors.CYAN}Performing drag-drop:{Colors.RESET}")
    print(f"  From pixel: ({source_x}, {source_y})")
    print(f"  To pixel: ({target_x}, {target_y})")

    # Perform drag-drop
    print(f"\n{Colors.YELLOW}>>> Moving mouse to source...{Colors.RESET}")
    pyautogui.moveTo(source_x, source_y, duration=0.3)
    time.sleep(0.2)

    print(f"{Colors.YELLOW}>>> Starting drag...{Colors.RESET}")
    pyautogui.mouseDown()
    time.sleep(0.1)

    print(f"{Colors.YELLOW}>>> Dragging to target...{Colors.RESET}")
    pyautogui.moveTo(target_x, target_y, duration=0.5)
    time.sleep(0.2)

    print(f"{Colors.YELLOW}>>> Dropping...{Colors.RESET}")
    pyautogui.mouseUp()
    time.sleep(0.3)

    print(f"\n{Colors.GREEN}Done! Check the UI to verify the result.{Colors.RESET}")

    return True


def find_test_files(test_name: Optional[str] = None) -> List[Path]:
    """Find test files in humanized directory."""
    humanized_dir = Path(__file__).parent / 'humanized'

    if not humanized_dir.exists():
        return []

    files = []
    for root, dirs, filenames in os.walk(humanized_dir):
        for filename in filenames:
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
    # Enable ANSI colors on Windows
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

    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}  HUMANIZED UI TEST RUNNER{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"\nMake sure 'My Everything' app is running!")
    print(f"Tests will perform REAL drag-drop operations.\n")

    for filepath in files:
        try:
            test = parse_test_file(filepath)
            run_ui_test(test)

            print(f"\n{Colors.YELLOW}Press Enter to continue to next test (or Ctrl+C to stop)...{Colors.RESET}")
            input()

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Stopped by user.{Colors.RESET}")
            break
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
