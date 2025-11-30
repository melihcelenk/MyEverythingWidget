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
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import pyautogui

    pyautogui.FAILSAFE = True  # Move mouse to screen corner to stop
    pyautogui.PAUSE = 0.1
except ImportError:
    print("ERROR: pyautogui not installed. Run: pip install pyautogui")
    sys.exit(1)

try:
    import pygetwindow as gw
except ImportError:
    print("ERROR: pygetwindow not installed. Run: pip install pygetwindow")
    sys.exit(1)

# Import from new package structure
from tests.humanized.runner.constants import (
    CELL_WIDTH, CELL_HEIGHT, SPACING, MARGIN_LEFT,
    Colors
)

# Import safety utilities (after Colors is imported)
from tests.humanized.utils.safety import check_user_interrupt, safe_sleep
from tests.humanized.runner.models import (
    GridItem, CreateAction, DragAction, LaunchAction, TestCase
)
from tests.humanized.runner.state_manager import StateManager
from tests.humanized.runner.process_manager import ProcessManager
from tests.humanized.runner.parser import DSLParser

# State file paths
INITIAL_STATE_FILE = PROJECT_ROOT / "tests" / "state" / "initial_test_state.json"
TMP_DIR = PROJECT_ROOT / "tests" / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = TMP_DIR / "app_state.json"
BACKUP_FILE = TMP_DIR / "app_state_backup.json"
MOCK_APPS_DIR = TMP_DIR / "mock_apps"
MOCK_APPS_DIR.mkdir(parents=True, exist_ok=True)

# Initialize managers
state_manager = StateManager(INITIAL_STATE_FILE, STATE_FILE, BACKUP_FILE)
process_manager = ProcessManager(PROJECT_ROOT, STATE_FILE)

# Initialize interactors and executors
from tests.humanized.interactors.coordinate_calculator import CoordinateCalculator
from tests.humanized.interactors.dialog_interactor import DialogInteractor
from tests.humanized.actions.create_executor import CreateExecutor

coordinate_calculator = CoordinateCalculator()
dialog_interactor = DialogInteractor(coordinate_calculator)
create_executor = CreateExecutor(dialog_interactor, coordinate_calculator, MOCK_APPS_DIR)


# Parser now uses DSLParser class
def parse_test_file(filepath: Path) -> TestCase:
    """Parse a humanized test file."""
    return DSLParser.parse_file(filepath)


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


# State backup/restore functions now use StateManager
def backup_state():
    """No backup needed - we use separate test state file."""
    state_manager.backup_state()


def restore_state():
    """Reset test state by copying from initial state file."""
    state_manager.restore_state()


# State management functions now use StateManager
def create_test_state(test: TestCase) -> dict:
    """Create test state from test case."""
    return state_manager.create_test_state(test)


def write_test_state(state: dict):
    """Write state to state.json."""
    state_manager.write_state(state)


# Process management functions now use ProcessManager
def kill_all_mew_processes() -> bool:
    """Kill all running instances of the application. Returns True if successful within 5 seconds."""
    return process_manager.kill_all_processes(5.0)


def start_app() -> subprocess.Popen:
    """Start the application in TEST MODE."""
    return process_manager.start_app(5.0)


def find_window() -> Tuple[int, int, int, int]:
    """Find window and return (x, y, width, height)."""
    return process_manager.find_window()


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

    # Build content-to-ID and name-to-ID mappings from Create actions
    content_to_id = {}
    name_to_id = {}
    for action in test.actions:
        if isinstance(action, CreateAction):
            if action.item_type == 'NOTE':
                content_to_id[action.content] = action.item_id
            elif action.item_type == 'APP':
                name_to_id[action.content] = action.item_id

    for app in state.get("apps", []):
        app_id = app["id"]
        app_name = app.get("name", "")

        # Try to match by name first (for apps created during test)
        short_id = name_to_id.get(app_name)

        # If not found, try ID prefix
        if short_id is None:
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
        note_content = note.get("content", "")

        # Try to match by content first (for notes created during test)
        short_id = content_to_id.get(note_content)

        # If not found, try ID prefix
        if short_id is None:
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
        # Check span as well
        if exp.row_span != act.row_span or exp.col_span != act.col_span:
            return False
    return True


def show_differences(expected: Dict[str, GridItem], actual: Dict[str, GridItem]):
    """Show differences between expected and actual."""
    for item_id, exp in expected.items():
        if item_id not in actual:
            print(f"  {Colors.RED}{item_id}: not found in actual{Colors.RESET}")
        else:
            act = actual[item_id]
            errors = []
            if exp.row != act.row or exp.col != act.col:
                errors.append(f"position: expected ({exp.row},{exp.col}) but got ({act.row},{act.col})")
            if exp.row_span != act.row_span or exp.col_span != act.col_span:
                errors.append(f"span: expected {exp.col_span}x{exp.row_span} but got {act.col_span}x{act.row_span}")
            if errors:
                print(f"  {Colors.RED}{item_id}: {', '.join(errors)}{Colors.RESET}")


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


def create_mock_executable(app_name: str) -> Path:
    """Create a mock executable file for testing."""
    # Create a simple .bat file that echoes the app name
    safe_name = "".join(c for c in app_name if c.isalnum() or c in ('-', '_'))
    mock_file = MOCK_APPS_DIR / f"{safe_name}.bat"

    # Write a simple batch file
    mock_file.write_text(f'@echo off\necho {app_name}\n', encoding='utf-8')

    print(f"  {Colors.CYAN}Created mock executable: {mock_file}{Colors.RESET}")
    return mock_file


def cleanup_mock_executables():
    """Clean up all mock executable files."""
    if MOCK_APPS_DIR.exists():
        for file in MOCK_APPS_DIR.glob("*.bat"):
            try:
                file.unlink()
            except Exception as e:
                print(f"  {Colors.YELLOW}Warning: Could not delete {file}: {e}{Colors.RESET}")


def perform_create_note(content: str, win_x: int, win_y: int, main_window_bounds=None):
    """Perform create note operation."""
    # Use same constants as cell_to_pixel for consistency
    TITLE_BAR_HEIGHT = 32
    TAB_HEIGHT = 32
    QUICK_NOTE_HEIGHT = 40

    # Quick note entry is below title bar and tabs
    # Input field is on the left side of quick note entry
    # Quick note entry has 8px margins, input field is wide
    quick_note_y = win_y + TITLE_BAR_HEIGHT + TAB_HEIGHT
    input_y = quick_note_y + QUICK_NOTE_HEIGHT // 2  # Middle of quick note entry

    # Input field is on the left, with some margin
    input_x = win_x + MARGIN_LEFT + 100  # Left side, past margin (input field is wide)

    print(f"  {Colors.YELLOW}Creating note: '{content}'{Colors.RESET}")
    print(f"  {Colors.YELLOW}Clicking input at ({input_x}, {input_y}){Colors.RESET}")

    # Click on input field area
    check_user_interrupt(main_window_bounds)
    pyautogui.click(input_x, input_y)
    safe_sleep(0.5, main_window_bounds)  # Wait for focus

    # Clear any existing text (Ctrl+A, Delete)
    check_user_interrupt(main_window_bounds)
    pyautogui.hotkey('ctrl', 'a')
    safe_sleep(0.1, main_window_bounds)
    pyautogui.press('delete')
    safe_sleep(0.1, main_window_bounds)

    # Type content
    pyautogui.write(content, interval=0.05)
    safe_sleep(0.3, main_window_bounds)

    # Press Enter to submit
    check_user_interrupt(main_window_bounds)
    pyautogui.press('enter')
    safe_sleep(1.0, main_window_bounds)  # Wait longer for note to be created and state to save


def perform_create_app(app_name: str, win_x: int, win_y: int, main_window_bounds=None) -> Path:
    """Perform create app operation using CreateExecutor."""
    # Use CreateExecutor to create app (directly call _create_app to get mock_file)
    return create_executor._create_app(app_name, win_x, win_y, main_window_bounds)


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


def perform_launch_app(app_item: GridItem, win_x: int, win_y: int, app_name: str = None):
    """Perform app launch operation by clicking on app card."""
    app_x, app_y = cell_to_pixel(app_item.row, app_item.col, win_x, win_y)

    print(f"  {Colors.YELLOW}Launching app {app_item.id} at ({app_x}, {app_y}){Colors.RESET}")

    # Get process count before launch (for .bat files, we'll track cmd.exe processes)
    try:
        import psutil
        initial_cmd_count = len(
            [p for p in psutil.process_iter(['pid', 'name']) if 'cmd.exe' in p.info.get('name', '').lower()])
    except ImportError:
        psutil = None
        initial_cmd_count = 0
        print(f"  {Colors.YELLOW}psutil not available, process tracking limited{Colors.RESET}")

    # Click on app card
    pyautogui.click(app_x, app_y)
    time.sleep(1.0)  # Wait for app to launch

    # Try to find the launched process
    launched_proc = None
    if psutil:
        time.sleep(0.5)  # Give process time to start
        current_cmd_count = len(
            [p for p in psutil.process_iter(['pid', 'name']) if 'cmd.exe' in p.info.get('name', '').lower()])
        if current_cmd_count > initial_cmd_count:
            # Find the new cmd.exe process (most recent)
            cmd_processes = []
            for p in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    if 'cmd.exe' in p.info.get('name', '').lower():
                        cmd_processes.append(p)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if cmd_processes:
                # Sort by create_time, get most recent
                cmd_processes.sort(key=lambda p: p.info.get('create_time', 0) or 0, reverse=True)
                new_process = cmd_processes[0]
                try:
                    print(f"  {Colors.GREEN}App launch detected (PID: {new_process.info['pid']}){Colors.RESET}")
                    launched_proc = new_process
                except Exception as e:
                    print(f"  {Colors.YELLOW}Could not track process: {e}{Colors.RESET}")
        else:
            print(f"  {Colors.YELLOW}No new process detected (app may have launched and exited quickly){Colors.RESET}")
    else:
        print(f"  {Colors.GREEN}App launch triggered{Colors.RESET}")

    return launched_proc


def cleanup_launched_processes(processes: List):
    """Clean up launched processes."""
    try:
        import psutil
    except ImportError:
        psutil = None

    for proc in processes:
        try:
            if proc is None:
                continue

            if psutil and hasattr(proc, 'info'):  # psutil.Process object
                try:
                    if proc.is_running():
                        proc.terminate()
                        time.sleep(0.5)
                        if proc.is_running():
                            proc.kill()
                        print(f"  {Colors.CYAN}Killed process PID: {proc.pid}{Colors.RESET}")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    print(f"  {Colors.YELLOW}Process already terminated or access denied: {e}{Colors.RESET}")
            elif hasattr(proc, 'poll'):  # subprocess.Popen object
                if proc.poll() is None:  # Still running
                    proc.terminate()
                    time.sleep(0.5)
                    if proc.poll() is None:  # Still running, force kill
                        proc.kill()
            elif isinstance(proc, int):  # PID only
                try:
                    if psutil:
                        p = psutil.Process(proc)
                        if p.is_running():
                            p.terminate()
                            time.sleep(0.5)
                            if p.is_running():
                                p.kill()
                    else:
                        # Fallback: use taskkill on Windows
                        if sys.platform == 'win32':
                            subprocess.run(['taskkill', '/F', '/PID', str(proc)],
                                           capture_output=True, timeout=2)
                except (psutil.NoSuchProcess, psutil.AccessDenied, subprocess.TimeoutExpired) as e:
                    print(f"  {Colors.YELLOW}Could not kill process {proc}: {e}{Colors.RESET}")
        except Exception as e:
            print(f"  {Colors.YELLOW}Warning: Could not kill process: {e}{Colors.RESET}")


def run_ui_test(test: TestCase) -> bool:
    """Run a single UI test."""
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}  TEST: {test.name}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")

    # Track launched processes for cleanup
    launched_processes: List[subprocess.Popen] = []

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

    # Print actions
    if test.actions:
        print(f"\n{Colors.YELLOW}Action:{Colors.RESET}")
        for action in test.actions:
            if isinstance(action, DragAction):
                print(f"  Drag({action.item_id}) to R{action.target_row + 1}C{action.target_col + 1}")
            elif isinstance(action, CreateAction):
                print(f"  Create({action.item_type}, \"{action.content}\", {action.item_id})")
            elif isinstance(action, LaunchAction):
                print(f"  Launch({action.item_id})")
    elif test.action_item:
        # Legacy support
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

    # Reset state from initial template (copy initial to tmp)
    restore_state()
    
    try:
        # Create test state (starts from initial state)
        state = create_test_state(test)
        write_test_state(state)

        # Start app (with 5s timeout)
        try:
            proc = start_app()
        except RuntimeError as e:
            print(f"  {Colors.RED}Failed to start app: {e}{Colors.RESET}")
            return False

        # Find window
        win_x, win_y, win_width, win_height = find_window()
        print(f"  {Colors.GREEN}Window at ({win_x}, {win_y}), size: {win_width}x{win_height}{Colors.RESET}")

        # Store window bounds for interrupt checking
        main_window_bounds = (win_x, win_y, win_width, win_height)

        # Click Test tab
        click_test_tab(win_x, win_y)

        # Perform actions
        if test.actions:
            print(f"\n{Colors.YELLOW}Performing actions...{Colors.RESET}")
            for action in test.actions:
                if isinstance(action, CreateAction):
                    if action.item_type == 'NOTE':
                        perform_create_note(action.content, win_x, win_y, main_window_bounds)
                        # After creating, read state to get the created item's position
                        safe_sleep(1.0, main_window_bounds)  # Wait longer for state to save
                        created_state = state_manager.read_state()
                        # Find the created note (should be the last one or match content)
                        created_note = None
                        notes = created_state.get("notes", [])
                        print(f"  {Colors.CYAN}Found {len(notes)} notes in state{Colors.RESET}")
                        for note in notes:
                            print(
                                f"  {Colors.CYAN}Note: id={note.get('id')}, content='{note.get('content')}', row={note.get('grid_row')}, col={note.get('grid_col')}{Colors.RESET}")
                            if note.get("content") == action.content:
                                created_note = note
                                break
                        if created_note:
                            # Get position - if None, wait a bit more for auto-placement
                            grid_row = created_note.get('grid_row')
                            grid_col = created_note.get('grid_col')

                            # If position is None, wait a bit more and re-read state
                            if grid_row is None or grid_col is None:
                                print(
                                    f"  {Colors.YELLOW}Note position not set yet, waiting for auto-placement...{Colors.RESET}")
                                safe_sleep(1.0, main_window_bounds)
                                state_content = STATE_FILE.read_text(encoding='utf-8')
                                created_state = json.loads(state_content)
                                for note in created_state.get("notes", []):
                                    if note.get("id") == created_note.get("id"):
                                        grid_row = note.get('grid_row')
                                        grid_col = note.get('grid_col')
                                        break

                            # If still None, use first available cell (0, 0) as fallback
                            if grid_row is None:
                                grid_row = 0
                            if grid_col is None:
                                grid_col = 0

                            # Add to initial_items so Drag can find it
                            test.initial_items[action.item_id] = GridItem(
                                id=action.item_id,
                                item_type='note',
                                row=grid_row,
                                col=grid_col,
                                row_span=created_note.get('row_span', 1),
                                col_span=created_note.get('col_span', 1)
                            )
                            print(
                                f"  {Colors.GREEN}Created note {action.item_id} at ({grid_row}, {grid_col}){Colors.RESET}")
                        else:
                            print(
                                f"  {Colors.RED}Note with content '{action.content}' not found in state{Colors.RESET}")
                    elif action.item_type == 'APP':
                        mock_file = perform_create_app(action.content, win_x, win_y, main_window_bounds)

                        # CRITICAL: First verify dialog closed
                        print(f"  {Colors.CYAN}Verifying dialog closed...{Colors.RESET}")
                        dialog_closed = False
                        for check in range(3):
                            safe_sleep(0.5, main_window_bounds)
                            try:
                                dialog_windows = gw.getWindowsWithTitle("Add Item")
                                if not dialog_windows:
                                    dialog_closed = True
                                    print(f"  {Colors.GREEN}Dialog closed successfully{Colors.RESET}")
                                    break
                                else:
                                    print(f"  {Colors.YELLOW}Dialog still open (check {check + 1}/3){Colors.RESET}")
                            except Exception:
                                dialog_closed = True  # Assume closed if we can't check
                                break

                        if not dialog_closed:
                            print(f"  {Colors.RED}ERROR: Dialog did not close after clicking Add button{Colors.RESET}")
                            print(f"  {Colors.RED}App creation failed. Aborting test.{Colors.RESET}")
                            return False  # Abort test completely

                        # After dialog closed, verify app was added to state
                        # Retry mechanism: wait and retry if app not found
                        created_app = None
                        max_retries = 5
                        for retry in range(max_retries):
                            safe_sleep(0.5 if retry > 0 else 1.0, main_window_bounds)  # Wait longer on first attempt
                            state_content = STATE_FILE.read_text(encoding='utf-8')
                            created_state = json.loads(state_content)
                            apps = created_state.get("apps", [])
                            print(
                                f"  {Colors.CYAN}Found {len(apps)} apps in state (attempt {retry + 1}/{max_retries}){Colors.RESET}")
                            for app in apps:
                                print(
                                    f"  {Colors.CYAN}App: id={app.get('id')}, name='{app.get('name')}', row={app.get('grid_row')}, col={app.get('grid_col')}{Colors.RESET}")
                                if app.get("name") == action.content:
                                    created_app = app
                                    break
                            if created_app:
                                break
                            if retry < max_retries - 1:
                                print(f"  {Colors.YELLOW}App not found yet, retrying...{Colors.RESET}")

                        if not created_app:
                            print(
                                f"  {Colors.RED}ERROR: App '{action.content}' not found in state after {max_retries} attempts{Colors.RESET}")
                            print(f"  {Colors.RED}App creation failed. Aborting test.{Colors.RESET}")
                            return False  # Abort test completely
                        
                        if created_app:
                            # Get position - if None, wait a bit more for auto-placement
                            grid_row = created_app.get('grid_row')
                            grid_col = created_app.get('grid_col')

                            # If position is None, wait a bit more and re-read state
                            if grid_row is None or grid_col is None:
                                print(
                                    f"  {Colors.YELLOW}App position not set yet, waiting for auto-placement...{Colors.RESET}")
                                time.sleep(1.0)
                                state_content = STATE_FILE.read_text(encoding='utf-8')
                                created_state = json.loads(state_content)
                                for app in created_state.get("apps", []):
                                    if app.get("id") == created_app.get("id"):
                                        grid_row = app.get('grid_row')
                                        grid_col = app.get('grid_col')
                                        break

                            # If still None, use first available cell (0, 0) as fallback
                            if grid_row is None:
                                grid_row = 0
                            if grid_col is None:
                                grid_col = 0

                            # Add to initial_items so Drag can find it
                            test.initial_items[action.item_id] = GridItem(
                                id=action.item_id,
                                item_type='app',
                                row=grid_row,
                                col=grid_col,
                                row_span=created_app.get('row_span', 1),
                                col_span=created_app.get('col_span', 1)
                            )
                            print(
                                f"  {Colors.GREEN}Created app {action.item_id} at ({grid_row}, {grid_col}){Colors.RESET}")
                        else:
                            print(
                                f"  {Colors.RED}App with name '{action.content}' not found in state{Colors.RESET}")
                    else:
                        print(f"  {Colors.RED}Unsupported create type: {action.item_type}{Colors.RESET}")
                elif isinstance(action, DragAction):
                    source_item = test.initial_items.get(action.item_id)
                    if source_item:
                        perform_drag(source_item, action.target_row, action.target_col, win_x, win_y)
                    else:
                        print(f"  {Colors.RED}Source item not found: {action.item_id}{Colors.RESET}")
                elif isinstance(action, LaunchAction):
                    app_item = test.initial_items.get(action.item_id)
                    if app_item and app_item.item_type == 'app':
                        # Get app name from state for better process tracking
                        state_content = STATE_FILE.read_text(encoding='utf-8')
                        current_state = json.loads(state_content)
                        app_name = None
                        for app in current_state.get("apps", []):
                            # Match by position or ID
                            if (app.get("grid_row") == app_item.row and
                                    app.get("grid_col") == app_item.col):
                                app_name = app.get("name")
                                break

                        proc = perform_launch_app(app_item, win_x, win_y, app_name)
                        if proc:
                            launched_processes.append(proc)
                    else:
                        print(f"  {Colors.RED}App item not found: {action.item_id}{Colors.RESET}")
        elif test.action_item:
            # Legacy support
            source_item = test.initial_items.get(test.action_item)
            if source_item:
                print(f"\n{Colors.YELLOW}Performing drag-drop...{Colors.RESET}")
                perform_drag(source_item, test.action_target_row, test.action_target_col, win_x, win_y)

        # Wait for state to save
        time.sleep(2)

        # Read actual state
        print(f"\n  {Colors.CYAN}Reading state from: {STATE_FILE}{Colors.RESET}")
        actual_state = state_manager.read_state()

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
        # Cleanup launched processes
        cleanup_launched_processes(launched_processes)
        # Restore state
        restore_state()
        # Cleanup mock executables
        cleanup_mock_executables()


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
            # Only accept .dsl files
            if not filename.endswith('.dsl'):
                continue
            filepath = Path(root) / filename
            if test_name:
                # Match by full filename or stem (without extension)
                if filename == test_name or filepath.stem == test_name:
                    files.append(filepath)
            else:
                files.append(filepath)

    return files


def main():
    """Main entry point for test runner."""
    # Fix Windows console encoding for Unicode characters
    if sys.platform == 'win32':
        try:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass
        os.system('color')
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass

    # Check if app is running and kill if needed (5s timeout)
    print(f"{Colors.CYAN}Checking for running application instances...{Colors.RESET}")

    try:
        windows = gw.getWindowsWithTitle("My Everything")
        if windows or gw.getWindowsWithTitle("Already Running"):
            print(f"{Colors.CYAN}Found running instance, killing...{Colors.RESET}")
            if not kill_all_mew_processes():
                print(f"{Colors.RED}Failed to kill existing processes. Aborting test.{Colors.RESET}")
                sys.exit(1)
    except Exception:
        pass

    # Cleanup mock executables at start
    cleanup_mock_executables()

    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    test_name = args[0] if args else None

    files = find_test_files(test_name)

    if not files:
        if test_name:
            print(f"{Colors.RED}Test not found: {test_name}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}No test files found in tests/humanized/{Colors.RESET}")
        sys.exit(1)

    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}  HUMANIZED UI TEST RUNNER{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"\n  This will:")
    print(f"  1. Backup your current state")
    print(f"  2. Create test items")
    print(f"  3. Open the app")
    print(f"  4. Perform drag-drop")
    print(f"  5. Restore your state")
    print(f"\n  {Colors.YELLOW}SAFETY: Move mouse to screen corner to stop{Colors.RESET}", end="")
    try:
        from tests.humanized.utils.safety import KEYBOARD_METHOD as kb_method
        if kb_method:
            print(f" | Press any key to stop ({kb_method})")
        else:
            print(f" | Keyboard not available (install: pip install keyboard or pynput)")
    except:
        print()
    print()
    
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
        finally:
            # Cleanup mock executables
            cleanup_mock_executables()


if __name__ == '__main__':
    main()
