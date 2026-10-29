"""Create action executor for UI tests."""

from pathlib import Path
from typing import Dict

try:
    import pyautogui

    pyautogui.FAILSAFE = True  # Move mouse to corner to stop
    pyautogui.PAUSE = 0.1
except ImportError:
    pyautogui = None

from ..runner.models import CreateAction
from ..runner.constants import Colors
from ..interactors.dialog_interactor import DialogInteractor
from ..interactors.coordinate_calculator import CoordinateCalculator
from ..utils.safety import check_user_interrupt, safe_sleep
from .base import ActionExecutor


class CreateExecutor(ActionExecutor):
    """Executes Create actions (NOTE, APP)."""

    def __init__(self, dialog_interactor: DialogInteractor, calculator: CoordinateCalculator, mock_apps_dir: Path):
        self.dialog_interactor = dialog_interactor
        self.calculator = calculator
        self.mock_apps_dir = mock_apps_dir
        self.mock_apps_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, action: CreateAction, name_to_id: Dict[str, str], win_x: int, win_y: int,
                main_window_bounds=None) -> bool:
        """Execute a Create action."""
        if action.item_type == 'NOTE':
            return self._create_note(action.content, win_x, win_y, main_window_bounds)
        elif action.item_type == 'APP':
            return self._create_app(action.content, win_x, win_y, main_window_bounds)
        else:
            print(f"  {Colors.RED}Unknown create type: {action.item_type}{Colors.RESET}")
            return False

    def _create_note(self, content: str, win_x: int, win_y: int, main_window_bounds=None) -> bool:
        """Create a note."""
        if not pyautogui:
            raise RuntimeError("pyautogui not available")

        # Input field is at left side, below tabs
        # Tabs are ~50px from top, input is ~80px from top
        input_y = win_y + 80
        input_x = win_x + 100  # Left side, past margin

        print(f"  {Colors.YELLOW}Creating note: '{content}'{Colors.RESET}")
        print(f"  {Colors.YELLOW}Clicking input at ({input_x}, {input_y}){Colors.RESET}")

        check_user_interrupt(main_window_bounds)
        pyautogui.click(input_x, input_y)
        safe_sleep(0.5, main_window_bounds)

        # Clear and type
        check_user_interrupt(main_window_bounds)
        pyautogui.hotkey('ctrl', 'a')
        safe_sleep(0.1, main_window_bounds)
        pyautogui.press('delete')
        safe_sleep(0.1, main_window_bounds)
        pyautogui.write(content, interval=0.05)
        safe_sleep(0.3, main_window_bounds)

        # Submit
        check_user_interrupt(main_window_bounds)
        pyautogui.press('enter')
        safe_sleep(1.0, main_window_bounds)

        return True

    def _create_app(self, app_name: str, win_x: int, win_y: int, main_window_bounds=None) -> Path:
        """Create an app. Returns mock_file path."""
        if not pyautogui:
            raise RuntimeError("pyautogui not available")

        # Create mock executable
        mock_file = self._create_mock_executable(app_name)

        # Get actual window size from pygetwindow
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle("My Everything")
            if windows:
                win = windows[0]
                actual_width = win.width if hasattr(win, 'width') else None
                actual_height = win.height if hasattr(win, 'height') else None
                if actual_width and actual_height:
                    print(f"  {Colors.CYAN}Window actual size: {actual_width}x{actual_height}{Colors.RESET}")
                    # Recalculate FAB position with actual window size
                    from ..runner.constants import FAB_SIZE, FAB_MARGIN
                    fab_x = win.left + actual_width - FAB_SIZE - FAB_MARGIN
                    fab_y = win.top + actual_height - FAB_SIZE - FAB_MARGIN
                    print(
                        f"  {Colors.CYAN}Recalculated FAB position using actual window size: ({fab_x}, {fab_y}){Colors.RESET}")
        except Exception as e:
            print(f"  {Colors.YELLOW}Could not get actual window size: {e}{Colors.RESET}")
            fab_x, fab_y = self.calculator.get_fab_position(win_x, win_y)
        
        print(f"  {Colors.YELLOW}Creating app: '{app_name}'{Colors.RESET}")
        print(f"  {Colors.CYAN}STEP 0: Clicking FAB (Add Item button) at ({fab_x}, {fab_y}){Colors.RESET}")
        print(f"  {Colors.YELLOW}TIP: Press any key or move mouse to screen corner to stop{Colors.RESET}")

        # Try clicking FAB at calculated position and nearby positions
        fab_clicked = False
        for offset_x in [0, -5, 5, -10, 10, -15, 15, -20, 20]:
            for offset_y in [0, -5, 5, -10, 10, -15, 15, -20, 20]:
                check_user_interrupt(main_window_bounds)  # Allow user to stop
                test_fab_x = fab_x + offset_x
                test_fab_y = fab_y + offset_y
                print(f"  {Colors.YELLOW}Trying FAB at ({test_fab_x}, {test_fab_y})...{Colors.RESET}")
                pyautogui.click(test_fab_x, test_fab_y)
                safe_sleep(1.5, main_window_bounds)  # Wait for dialog to open (with interrupt check)

                # Check if dialog opened
                try:
                    import pygetwindow as gw
                    dialog_windows = gw.getWindowsWithTitle("Add Item")
                    if dialog_windows:
                        print(
                            f"  {Colors.GREEN}✓ FAB click successful at ({test_fab_x}, {test_fab_y}) - dialog opened!{Colors.RESET}")
                        fab_clicked = True
                        break
                except Exception:
                    pass
            if fab_clicked:
                break

        if not fab_clicked:
            print(
                f"  {Colors.RED}✗ ERROR: FAB click failed - dialog did not open after trying multiple positions!{Colors.RESET}")
            print(f"  {Colors.RED}ERROR: Cannot proceed - FAB button not working{Colors.RESET}")
            print(
                f"  {Colors.RED}Window position: ({win_x}, {win_y}), FAB calculated: ({fab_x}, {fab_y}){Colors.RESET}")
            return mock_file

        # Find dialog
        dialog_x, dialog_y, dialog_width, dialog_height = self.dialog_interactor.find_dialog(win_x, win_y)

        # Click App tab
        self.dialog_interactor.click_app_tab(dialog_x, dialog_y, dialog_width, main_window_bounds)

        # Fill name input
        print(f"  {Colors.CYAN}STEP 1: Filling name input...{Colors.RESET}")
        if not self.dialog_interactor.fill_name_input(dialog_x, dialog_y, dialog_width, app_name, main_window_bounds):
            print(f"  {Colors.RED}ERROR: Failed to fill name input{Colors.RESET}")
            return mock_file

        # Get name input Y for path calculation
        name_input_x, name_input_y = self.calculator.get_name_input_position(dialog_x, dialog_y, dialog_width)

        # Fill path input
        print(f"  {Colors.CYAN}STEP 2: Filling path input...{Colors.RESET}")
        path_str = str(mock_file.absolute())
        if not self.dialog_interactor.fill_path_input(dialog_x, dialog_y, dialog_width, name_input_y, path_str,
                                                      main_window_bounds):
            print(f"  {Colors.RED}ERROR: Failed to fill path input{Colors.RESET}")
            return mock_file

        # Click Add button
        print(f"  {Colors.CYAN}STEP 3: Clicking Add button...{Colors.RESET}")
        if not self.dialog_interactor.click_add_button(dialog_x, dialog_y, dialog_width, dialog_height,
                                                       main_window_bounds):
            print(f"  {Colors.RED}ERROR: Dialog did not close after clicking Add button{Colors.RESET}")
            return mock_file

        print(f"  {Colors.GREEN}✓ Add button clicked successfully!{Colors.RESET}")
        return mock_file

    def _create_mock_executable(self, app_name: str) -> Path:
        """Create a mock executable file for testing."""
        # Sanitize app name for filename
        safe_name = "".join(c for c in app_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '')
        if not safe_name:
            safe_name = "TestApp"

        mock_file = self.mock_apps_dir / f"{safe_name}.bat"
        mock_file.write_text("@echo off\necho Mock app: {}\n".format(app_name), encoding='utf-8')
        print(f"  {Colors.CYAN}Created mock executable: {mock_file}{Colors.RESET}")
        return mock_file
