"""Create action executor for UI tests."""

import time
from pathlib import Path
from typing import Dict

try:
    import pyautogui

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except ImportError:
    pyautogui = None

from ..runner.models import CreateAction
from ..runner.constants import Colors
from ..interactors.dialog_interactor import DialogInteractor
from ..interactors.coordinate_calculator import CoordinateCalculator
from .base import ActionExecutor


class CreateExecutor(ActionExecutor):
    """Executes Create actions (NOTE, APP)."""

    def __init__(self, dialog_interactor: DialogInteractor, calculator: CoordinateCalculator, mock_apps_dir: Path):
        self.dialog_interactor = dialog_interactor
        self.calculator = calculator
        self.mock_apps_dir = mock_apps_dir
        self.mock_apps_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, action: CreateAction, name_to_id: Dict[str, str], win_x: int, win_y: int) -> bool:
        """Execute a Create action."""
        if action.item_type == 'NOTE':
            return self._create_note(action.content, win_x, win_y)
        elif action.item_type == 'APP':
            return self._create_app(action.content, win_x, win_y)
        else:
            print(f"  {Colors.RED}Unknown create type: {action.item_type}{Colors.RESET}")
            return False

    def _create_note(self, content: str, win_x: int, win_y: int) -> bool:
        """Create a note."""
        if not pyautogui:
            raise RuntimeError("pyautogui not available")

        # Input field is at left side, below tabs
        # Tabs are ~50px from top, input is ~80px from top
        input_y = win_y + 80
        input_x = win_x + 100  # Left side, past margin

        print(f"  {Colors.YELLOW}Creating note: '{content}'{Colors.RESET}")
        print(f"  {Colors.YELLOW}Clicking input at ({input_x}, {input_y}){Colors.RESET}")

        pyautogui.click(input_x, input_y)
        time.sleep(0.5)

        # Clear and type
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
        pyautogui.write(content, interval=0.05)
        time.sleep(0.3)

        # Submit
        pyautogui.press('enter')
        time.sleep(1.0)

        return True

    def _create_app(self, app_name: str, win_x: int, win_y: int) -> bool:
        """Create an app."""
        if not pyautogui:
            raise RuntimeError("pyautogui not available")

        # Create mock executable
        mock_file = self._create_mock_executable(app_name)

        # Click FAB
        fab_x, fab_y = self.calculator.get_fab_position(win_x, win_y)
        print(f"  {Colors.YELLOW}Creating app: '{app_name}'{Colors.RESET}")
        print(f"  {Colors.YELLOW}Clicking FAB at ({fab_x}, {fab_y}){Colors.RESET}")
        pyautogui.click(fab_x, fab_y)
        time.sleep(2.0)

        # Find dialog
        dialog_x, dialog_y, dialog_width, dialog_height = self.dialog_interactor.find_dialog(win_x, win_y)

        # Click App tab
        self.dialog_interactor.click_app_tab(dialog_x, dialog_y, dialog_width)

        # Fill name input
        if not self.dialog_interactor.fill_name_input(dialog_x, dialog_y, dialog_width, app_name):
            return False

        # Get name input Y for path calculation
        name_input_x, name_input_y = self.calculator.get_name_input_position(dialog_x, dialog_y, dialog_width)

        # Fill path input
        path_str = str(mock_file.absolute())
        if not self.dialog_interactor.fill_path_input(dialog_x, dialog_y, dialog_width, name_input_y, path_str):
            return False

        # Click Add button
        if not self.dialog_interactor.click_add_button(dialog_x, dialog_y, dialog_width, dialog_height):
            print(f"  {Colors.RED}ERROR: Dialog did not close after clicking Add button{Colors.RESET}")
            return False

        return True

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
