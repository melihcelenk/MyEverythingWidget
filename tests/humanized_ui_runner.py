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

# Import from new package structure
from tests.humanized.runner.constants import (
    CELL_WIDTH, CELL_HEIGHT, SPACING, MARGIN_LEFT,
    Colors
)
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


def find_window() -> Tuple[int, int]:
    """Find window and return (x, y)."""
    return process_manager.find_window()

    # Bring window to front and ensure it's visible
    try:
        if win.isMinimized:
            win.restore()
        win.activate()
        win.moveTo(100, 100)  # Move to visible position
    except Exception as e:
        print(f"  {Colors.YELLOW}Warning: Could not activate window: {e}{Colors.RESET}")

    time.sleep(0.5)

    # Refresh window position
    win = gw.getWindowsWithTitle("My Everything")[0]
    
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


def perform_create_note(content: str, win_x: int, win_y: int):
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
    pyautogui.click(input_x, input_y)
    time.sleep(0.5)  # Wait for focus

    # Clear any existing text (Ctrl+A, Delete)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.press('delete')
    time.sleep(0.1)

    # Type content
    pyautogui.write(content, interval=0.05)
    time.sleep(0.3)

    # Press Enter to submit
    pyautogui.press('enter')
    time.sleep(1.0)  # Wait longer for note to be created and state to save


def perform_create_app(app_name: str, win_x: int, win_y: int) -> Path:
    """Perform create app operation."""
    # Create mock executable
    mock_file = create_mock_executable(app_name)

    # Window dimensions
    WINDOW_WIDTH = 320
    WINDOW_HEIGHT = 500
    FAB_SIZE = 40
    FAB_MARGIN = 12

    # FAB is at bottom-right corner
    fab_x = win_x + WINDOW_WIDTH - FAB_SIZE - FAB_MARGIN
    fab_y = win_y + WINDOW_HEIGHT - FAB_SIZE - FAB_MARGIN

    print(f"  {Colors.YELLOW}Creating app: '{app_name}'{Colors.RESET}")
    print(f"  {Colors.YELLOW}Clicking FAB at ({fab_x}, {fab_y}){Colors.RESET}")

    # Click FAB button
    pyautogui.click(fab_x, fab_y)
    time.sleep(2.0)  # Wait longer for dialog to open

    # Try to find dialog window - Qt dialogs may not show up in pygetwindow
    # Try multiple methods
    dialog_x = None
    dialog_y = None
    DIALOG_WIDTH = 320
    DIALOG_HEIGHT = 400  # Default dialog height

    # Method 1: Try to find by title
    real_dialog_width = DIALOG_WIDTH
    real_dialog_height = DIALOG_HEIGHT
    try:
        dialog_windows = gw.getWindowsWithTitle("Add Item")
        if dialog_windows:
            dialog_win = dialog_windows[0]
            dialog_x = dialog_win.left
            dialog_y = dialog_win.top
            # Try to get real dimensions
            try:
                if hasattr(dialog_win, 'width') and hasattr(dialog_win, 'height'):
                    real_dialog_width = dialog_win.width
                    real_dialog_height = dialog_win.height
            except Exception:
                pass
            print(
                f"  {Colors.CYAN}Found dialog at ({dialog_x}, {dialog_y}), size: {real_dialog_width}x{real_dialog_height}{Colors.RESET}")
    except Exception:
        pass

    # Method 2: Try to find by partial title match
    if dialog_x is None:
        try:
            all_windows = gw.getAllWindows()
            for win in all_windows:
                if "Add Item" in win.title or "add item" in win.title.lower():
                    dialog_x = win.left
                    dialog_y = win.top
                    print(f"  {Colors.CYAN}Found dialog by partial match at ({dialog_x}, {dialog_y}){Colors.RESET}")
                    break
        except Exception:
            pass

    # Method 3: Assume dialog is centered on parent window (Qt default behavior)
    if dialog_x is None:
        # Qt dialogs are typically centered on parent window
        # Dialog center = parent window center
        # Parent window center: (win_x + WINDOW_WIDTH/2, win_y + WINDOW_HEIGHT/2)
        # Dialog top-left = center - (dialog_width/2, dialog_height/2)
        dialog_x = win_x + (WINDOW_WIDTH - DIALOG_WIDTH) // 2
        dialog_y = win_y + (WINDOW_HEIGHT - DIALOG_HEIGHT) // 2
        print(
            f"  {Colors.YELLOW}Using estimated dialog position (centered on parent): ({dialog_x}, {dialog_y}){Colors.RESET}")
        print(f"  {Colors.YELLOW}Parent window: ({win_x}, {win_y}), size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}{Colors.RESET}")

    # Dialog dimensions (from AddItemDialog)
    # Note: Actual dialog may be slightly different due to window decorations
    # From test output, actual dialog is often 336x380
    DIALOG_WIDTH = 336  # Actual observed width
    DIALOG_HEIGHT = 380  # Actual observed height

    # App tab is first tab (index 0), tab height ~32px
    TAB_HEIGHT = 32
    TAB_WIDTH = real_dialog_width // 3  # 3 tabs
    app_tab_x = dialog_x + TAB_WIDTH // 2
    app_tab_y = dialog_y + TAB_HEIGHT // 2

    print(f"  {Colors.CYAN}Calculated App tab position: ({app_tab_x}, {app_tab_y}){Colors.RESET}")
    print(
        f"  {Colors.CYAN}  Dialog: ({dialog_x}, {dialog_y}), size: {real_dialog_width}x{real_dialog_height}{Colors.RESET}")
    print(f"  {Colors.CYAN}  Tab width: {TAB_WIDTH}px, tab center offset: {TAB_WIDTH // 2}px{Colors.RESET}")

    # Click App tab (first tab)
    print(f"  {Colors.YELLOW}Clicking App tab at ({app_tab_x}, {app_tab_y}){Colors.RESET}")
    pyautogui.click(app_tab_x, app_tab_y)
    time.sleep(0.8)  # Wait for tab to switch

    # Re-find dialog to get real position and dimensions after tab switch
    # Wait a bit for dialog to fully render
    time.sleep(0.5)
    try:
        dialog_windows = gw.getWindowsWithTitle("Add Item")
        if dialog_windows:
            dialog_win = dialog_windows[0]
            dialog_x = dialog_win.left
            dialog_y = dialog_win.top
            # Try to get real dimensions - pygetwindow may not have width/height, use size if available
            try:
                if hasattr(dialog_win, 'width') and hasattr(dialog_win, 'height'):
                    real_dialog_width = dialog_win.width
                    real_dialog_height = dialog_win.height
                elif hasattr(dialog_win, 'size'):
                    # Some versions have size as (width, height)
                    size = dialog_win.size
                    if size and len(size) >= 2:
                        real_dialog_width = size[0]
                        real_dialog_height = size[1]
            except Exception:
                pass
            print(
                f"  {Colors.CYAN}Dialog position after tab switch: ({dialog_x}, {dialog_y}), size: {real_dialog_width}x{real_dialog_height}{Colors.RESET}")
    except Exception:
        pass

    # App name input - below tabs, with margins
    # From screenshot analysis: name input is below "App Name:" label
    # Try multiple coordinate calculations and test which one works
    TAB_HEIGHT = 32
    LABEL_HEIGHT = 20
    MARGIN_TOP = 16
    INPUT_HEIGHT = 25
    GAP = 12

    # Try center of dialog first (most likely)
    name_input_x = dialog_x + real_dialog_width // 2
    # Calculate Y: tab + margin + label + gap + half input height
    name_input_y = dialog_y + TAB_HEIGHT + MARGIN_TOP + LABEL_HEIGHT + GAP + (INPUT_HEIGHT // 2)

    print(f"  {Colors.CYAN}Calculated name input position: ({name_input_x}, {name_input_y}){Colors.RESET}")
    print(
        f"  {Colors.CYAN}  Dialog: ({dialog_x}, {dialog_y}), size: {real_dialog_width}x{real_dialog_height}{Colors.RESET}")
    print(
        f"  {Colors.CYAN}  Offset from dialog top: {TAB_HEIGHT + MARGIN_TOP + LABEL_HEIGHT + GAP + (INPUT_HEIGHT // 2)}px{Colors.RESET}")

    # Click name input directly
    print(f"  {Colors.YELLOW}Clicking name input at ({name_input_x}, {name_input_y}){Colors.RESET}")
    pyautogui.click(name_input_x, name_input_y)
    time.sleep(0.5)  # Wait for focus

    # Click name input directly with mouse
    print(f"  {Colors.YELLOW}Clicking name input at ({name_input_x}, {name_input_y}){Colors.RESET}")
    pyautogui.click(name_input_x, name_input_y)
    time.sleep(0.5)  # Wait for focus

    # Verify focus by typing test character
    print(f"  {Colors.YELLOW}Verifying focus on name input...{Colors.RESET}")
    pyautogui.write('X', interval=0.05)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.2)

    try:
        import pyperclip
        test_text = pyperclip.paste()
        if test_text.strip() == 'X':
            print(f"  {Colors.GREEN}✓ Name input has focus{Colors.RESET}")
            # Clear the test character
            pyautogui.press('delete')
            time.sleep(0.1)
        else:
            print(f"  {Colors.RED}✗ Focus check failed, got: '{test_text}'{Colors.RESET}")
            print(f"  {Colors.RED}ERROR: Cannot proceed - name input focus failed{Colors.RESET}")
            return mock_file
    except Exception as e:
        print(f"  {Colors.YELLOW}Could not verify focus: {e}{Colors.RESET}")
    
    # Clear and type app name
    print(f"  {Colors.CYAN}Typing app name: {app_name}{Colors.RESET}")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.press('delete')
    time.sleep(0.1)
    pyautogui.write(app_name, interval=0.05)
    time.sleep(0.5)  # Wait longer for name to be written

    # STEP 1: Verify app name was written correctly
    print(f"  {Colors.CYAN}STEP 1: Verifying app name was written...{Colors.RESET}")
    pyautogui.hotkey('ctrl', 'a')  # Select all
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'c')  # Copy to clipboard
    time.sleep(0.2)

    # Read from clipboard
    try:
        import pyperclip
        clipboard_text = pyperclip.paste()
        if clipboard_text.strip() == app_name:
            print(f"  {Colors.GREEN}✓ App name written correctly: '{clipboard_text}'{Colors.RESET}")
        else:
            print(f"  {Colors.RED}✗ App name mismatch! Expected: '{app_name}', Got: '{clipboard_text}'{Colors.RESET}")
            print(f"  {Colors.RED}ERROR: Cannot proceed - app name not written correctly{Colors.RESET}")
            return mock_file
    except ImportError:
        print(f"  {Colors.YELLOW}WARNING: pyperclip not available, skipping name verification{Colors.RESET}")
    except Exception as e:
        print(f"  {Colors.YELLOW}WARNING: Could not verify name: {e}{Colors.RESET}")

    # Path input - below name input
    # From screenshot: path input is below name input
    # Layout: name input (25px) + spacing (12px) + "Path / URL:" label (~20px) + gap (12px) + path input (25px)
    # Path input center is approximately: name_input_y + (INPUT_HEIGHT // 2) + 12 (spacing) + 20 (label) + 12 (gap) + 12 (half input height)
    PATH_INPUT_OFFSET = 12 + LABEL_HEIGHT + GAP + (INPUT_HEIGHT // 2)
    path_input_x = dialog_x + real_dialog_width // 2  # Center of dialog (same as name input)
    path_input_y = name_input_y + (INPUT_HEIGHT // 2) + PATH_INPUT_OFFSET

    print(f"  {Colors.CYAN}Calculated path input position: ({path_input_x}, {path_input_y}){Colors.RESET}")
    print(f"  {Colors.CYAN}  Offset from name input: {PATH_INPUT_OFFSET}px{Colors.RESET}")

    # Click path input
    print(f"  {Colors.YELLOW}Clicking path input at ({path_input_x}, {path_input_y}){Colors.RESET}")
    pyautogui.click(path_input_x, path_input_y)
    time.sleep(0.5)  # Wait for focus

    # STEP 2: Type path (only if name was written correctly)
    path_str = str(mock_file.absolute())
    print(f"  {Colors.CYAN}STEP 2: Typing path: {path_str}{Colors.RESET}")
    # Verify file exists
    if not mock_file.exists():
        print(f"  {Colors.RED}ERROR: Mock file does not exist: {mock_file}{Colors.RESET}")
        return mock_file
    
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.press('delete')
    time.sleep(0.1)
    pyautogui.write(path_str, interval=0.02)
    time.sleep(0.5)  # Wait longer for path to be written

    # Verify path was written correctly
    print(f"  {Colors.CYAN}STEP 2: Verifying path was written...{Colors.RESET}")
    pyautogui.hotkey('ctrl', 'a')  # Select all
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'c')  # Copy to clipboard
    time.sleep(0.2)

    # Read from clipboard
    try:
        import pyperclip
        clipboard_text = pyperclip.paste()
        if clipboard_text.strip() == path_str:
            print(f"  {Colors.GREEN}✓ Path written correctly: '{clipboard_text}'{Colors.RESET}")
        else:
            print(f"  {Colors.RED}✗ Path mismatch! Expected: '{path_str}', Got: '{clipboard_text}'{Colors.RESET}")
            print(f"  {Colors.RED}ERROR: Cannot proceed - path not written correctly{Colors.RESET}")
            return mock_file
    except ImportError:
        print(f"  {Colors.YELLOW}WARNING: pyperclip not available, skipping path verification{Colors.RESET}")
    except Exception as e:
        print(f"  {Colors.YELLOW}WARNING: Could not verify path: {e}{Colors.RESET}")

    # Try to find dialog window again after typing (in case it moved)
    # Then use coordinate-based clicking on Add button (more reliable)
    time.sleep(0.3)  # Brief wait after typing

    # Try to find dialog again - verify it's still open and get real dimensions
    dialog_still_open = False
    real_dialog_width = DIALOG_WIDTH
    real_dialog_height = DIALOG_HEIGHT
    try:
        dialog_windows = gw.getWindowsWithTitle("Add Item")
        if dialog_windows:
            dialog_win = dialog_windows[0]
            dialog_x = dialog_win.left
            dialog_y = dialog_win.top
            # Try to get real dimensions if available
            try:
                real_dialog_width = dialog_win.width if hasattr(dialog_win, 'width') else DIALOG_WIDTH
                real_dialog_height = dialog_win.height if hasattr(dialog_win, 'height') else DIALOG_HEIGHT
            except Exception:
                pass
            dialog_still_open = True
            print(
                f"  {Colors.CYAN}Dialog still open at ({dialog_x}, {dialog_y}), size: {real_dialog_width}x{real_dialog_height}{Colors.RESET}")
        else:
            print(f"  {Colors.RED}WARNING: Dialog not found after typing path{Colors.RESET}")
    except Exception as e:
        print(f"  {Colors.YELLOW}Could not verify dialog: {e}{Colors.RESET}")

    if not dialog_still_open:
        print(f"  {Colors.RED}ERROR: Dialog closed unexpectedly{Colors.RESET}")
        return mock_file
    
    # Add button - at bottom of dialog
    # Button is at the bottom of the dialog, centered horizontally
    # Dialog has padding/margins, button is typically 30-40px from bottom edge
    # Button height is typically 30-35px, so center is at (height - 30 - 15) = height - 45
    BUTTON_HEIGHT = 35
    BUTTON_MARGIN_BOTTOM = 15  # Margin from bottom
    ADD_BUTTON_Y_CENTER = real_dialog_height - BUTTON_MARGIN_BOTTOM - (BUTTON_HEIGHT // 2)
    add_button_x = dialog_x + real_dialog_width // 2
    add_button_y = dialog_y + ADD_BUTTON_Y_CENTER

    print(
        f"  {Colors.CYAN}Calculated Add button position: ({add_button_x}, {add_button_y}) using dialog size {real_dialog_width}x{real_dialog_height}{Colors.RESET}")
    print(f"  {Colors.CYAN}Button center offset from dialog top: {ADD_BUTTON_Y_CENTER}px{Colors.RESET}")

    # STEP 3: Click Add button (only if name and path were written correctly)
    print(f"  {Colors.CYAN}STEP 3: Clicking Add button...{Colors.RESET}")

    # Take screenshot to verify dialog and find Add button position
    # Save screenshot for debugging
    try:
        screenshot_path = TMP_DIR / "dialog_screenshot.png"
        screenshot = pyautogui.screenshot(region=(dialog_x, dialog_y, real_dialog_width, real_dialog_height))
        screenshot.save(screenshot_path)
        print(f"  {Colors.CYAN}Screenshot saved to {screenshot_path} for debugging{Colors.RESET}")
    except Exception as e:
        print(f"  {Colors.YELLOW}Could not take screenshot: {e}{Colors.RESET}")

    # Try to locate "Add App" text on screen using pyautogui's locateOnScreen
    # This is more reliable than coordinate-based clicking
    try:
        # Try to find Add button by text (if pyautogui supports it)
        # Alternative: Use image recognition if we have a reference image
        print(f"  {Colors.YELLOW}Attempting to locate Add button...{Colors.RESET}")

        # Method: Use Tab navigation to focus on Add button, then get its position
        # Tab order from path input: Browse button -> Change Icon button -> Add App button
        # But we need to be careful - there might be more tab stops
        print(f"  {Colors.YELLOW}Tab navigation: Moving from path input to Add button...{Colors.RESET}")
        pyautogui.press('tab')  # Move to Browse button
        time.sleep(0.2)
        pyautogui.press('tab')  # Move to Change Icon button  
        time.sleep(0.2)
        pyautogui.press('tab')  # Move to Add App button (hopefully)
        time.sleep(0.5)  # Wait longer for focus to settle

        # Try Space key first (sometimes works better than Enter for buttons)
        print(f"  {Colors.YELLOW}Add button should have focus, trying Space key...{Colors.RESET}")
        pyautogui.press('space')
        time.sleep(1.0)

        # If that didn't work, try Enter
        try:
            remaining_dialogs = gw.getWindowsWithTitle("Add Item")
            if remaining_dialogs:
                print(f"  {Colors.YELLOW}Dialog still open after Space, trying Enter...{Colors.RESET}")
                pyautogui.press('enter')
                time.sleep(1.0)
        except Exception:
            pass

        # If that didn't work, try clicking at calculated position
        try:
            remaining_dialogs = gw.getWindowsWithTitle("Add Item")
            if remaining_dialogs:
                print(
                    f"  {Colors.YELLOW}Dialog still open after Tab+Enter, trying click at ({add_button_x}, {add_button_y})...{Colors.RESET}")
                # Move mouse to button position first to verify it's visible
                pyautogui.moveTo(add_button_x, add_button_y, duration=0.2)
                time.sleep(0.2)
                pyautogui.click(add_button_x, add_button_y)
                time.sleep(1.0)
        except Exception as e:
            print(f"  {Colors.YELLOW}Click failed: {e}{Colors.RESET}")
    except Exception as e:
        print(f"  {Colors.YELLOW}Tab navigation failed: {e}{Colors.RESET}")
        # Fallback: Try clicking at calculated position
        print(
            f"  {Colors.YELLOW}Falling back to coordinate-based click at ({add_button_x}, {add_button_y})...{Colors.RESET}")
        pyautogui.click(add_button_x, add_button_y)
        time.sleep(1.0)

    time.sleep(1.0)  # Final wait for app to be created and dialog to close
    
    return mock_file


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
        win_x, win_y = find_window()
        print(f"  {Colors.GREEN}Window at ({win_x}, {win_y}){Colors.RESET}")

        # Click Test tab
        click_test_tab(win_x, win_y)

        # Perform actions
        if test.actions:
            print(f"\n{Colors.YELLOW}Performing actions...{Colors.RESET}")
            for action in test.actions:
                if isinstance(action, CreateAction):
                    if action.item_type == 'NOTE':
                        perform_create_note(action.content, win_x, win_y)
                        # After creating, read state to get the created item's position
                        time.sleep(1.0)  # Wait longer for state to save
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
                                time.sleep(1.0)
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
                        mock_file = perform_create_app(action.content, win_x, win_y)

                        # CRITICAL: First verify dialog closed
                        print(f"  {Colors.CYAN}Verifying dialog closed...{Colors.RESET}")
                        dialog_closed = False
                        for check in range(3):
                            time.sleep(0.5)
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
                            time.sleep(0.5 if retry > 0 else 1.0)  # Wait longer on first attempt
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
        finally:
            # Cleanup mock executables
            cleanup_mock_executables()


if __name__ == '__main__':
    main()
