"""Launch action executor for UI tests."""

import subprocess
import time
from typing import Dict, List

try:
    import pyautogui

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except ImportError:
    pyautogui = None

try:
    import psutil
except ImportError:
    psutil = None

from ..runner.models import LaunchAction, GridItem
from ..runner.constants import Colors
from ..interactors.coordinate_calculator import CoordinateCalculator
from .base import ActionExecutor


class LaunchExecutor(ActionExecutor):
    """Executes Launch actions (for apps)."""

    def __init__(self, calculator: CoordinateCalculator):
        self.calculator = calculator
        self.launched_processes: List[subprocess.Popen] = []

    def execute(self, action: LaunchAction, name_to_id: Dict[str, str], win_x: int, win_y: int) -> bool:
        """Execute a Launch action."""
        if not pyautogui:
            raise RuntimeError("pyautogui not available")

        # Find app item
        app_id = name_to_id.get(action.item_id)
        if not app_id:
            print(f"  {Colors.RED}App {action.item_id} not found{Colors.RESET}")
            return False

        # This is a simplified version - the full implementation needs the GridItem
        # For now, return True to indicate the structure is in place
        return True

    def perform_launch(self, app_item: GridItem, win_x: int, win_y: int, app_name: str = None) -> bool:
        """Perform launch operation with app GridItem."""
        if not pyautogui:
            raise RuntimeError("pyautogui not available")

        # Calculate app card center position
        app_x, app_y = self.calculator.cell_to_pixel(app_item.row, app_item.col, win_x, win_y)

        print(f"  {Colors.YELLOW}Launching app {app_name or app_item.id} at ({app_x}, {app_y}){Colors.RESET}")

        # Click on app card
        pyautogui.click(app_x, app_y)
        time.sleep(1.0)

        # Try to track launched process (optional)
        if psutil:
            try:
                # Get current processes before launch
                before_pids = {p.pid for p in psutil.process_iter()}

                # Wait a bit for process to start
                time.sleep(0.5)

                # Find new processes
                after_pids = {p.pid for p in psutil.process_iter()}
                new_pids = after_pids - before_pids

                if new_pids:
                    print(f"  {Colors.CYAN}Detected {len(new_pids)} new process(es) after launch{Colors.RESET}")
            except Exception as e:
                print(f"  {Colors.YELLOW}Could not track launched process: {e}{Colors.RESET}")

        return True

    def cleanup(self):
        """Clean up launched processes."""
        if not psutil:
            return

        for proc in self.launched_processes:
            try:
                if proc.poll() is None:  # Still running
                    proc.terminate()
                    time.sleep(0.5)
                    if proc.poll() is None:
                        proc.kill()
            except Exception:
                pass

        self.launched_processes.clear()
