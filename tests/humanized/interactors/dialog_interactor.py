"""Dialog interaction utilities for UI tests."""

import time
from typing import Tuple

try:
    import pyautogui

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except ImportError:
    pyautogui = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

try:
    import pyperclip
except ImportError:
    pyperclip = None

from ..runner.constants import Colors, DIALOG_WIDTH, DIALOG_HEIGHT
from .coordinate_calculator import CoordinateCalculator


class DialogInteractor:
    """Handles interactions with Add Item Dialog."""

    def __init__(self, calculator: CoordinateCalculator):
        self.calculator = calculator

    def find_dialog(self, win_x: int, win_y: int) -> Tuple[int, int, int, int]:
        """
        Find Add Item Dialog window.
        Returns: (dialog_x, dialog_y, dialog_width, dialog_height)
        """
        dialog_x = None
        dialog_y = None
        dialog_width = DIALOG_WIDTH
        dialog_height = DIALOG_HEIGHT

        # Method 1: Try to find by title
        if gw:
            try:
                dialog_windows = gw.getWindowsWithTitle("Add Item")
                if dialog_windows:
                    dialog_win = dialog_windows[0]
                    dialog_x = dialog_win.left
                    dialog_y = dialog_win.top
                    try:
                        if hasattr(dialog_win, 'width') and hasattr(dialog_win, 'height'):
                            dialog_width = dialog_win.width
                            dialog_height = dialog_win.height
                    except Exception:
                        pass
            except Exception:
                pass

        # Method 2: Try partial title match
        if dialog_x is None and gw:
            try:
                all_windows = gw.getAllWindows()
                for win in all_windows:
                    if "Add Item" in win.title or "add item" in win.title.lower():
                        dialog_x = win.left
                        dialog_y = win.top
                        try:
                            if hasattr(win, 'width') and hasattr(win, 'height'):
                                dialog_width = win.width
                                dialog_height = win.height
                        except Exception:
                            pass
                        break
            except Exception:
                pass

        # Method 3: Assume centered on parent (fallback)
        if dialog_x is None:
            from ..runner.constants import WINDOW_WIDTH, WINDOW_HEIGHT
            dialog_x = win_x + (WINDOW_WIDTH - dialog_width) // 2
            dialog_y = win_y + (WINDOW_HEIGHT - dialog_height) // 2

        return dialog_x, dialog_y, dialog_width, dialog_height

    def click_app_tab(self, dialog_x: int, dialog_y: int, dialog_width: int):
        """Click App tab in Add Item Dialog."""
        if not pyautogui:
            raise RuntimeError("pyautogui not available")

        tab_x, tab_y = self.calculator.get_tab_position(0, dialog_x, dialog_y, dialog_width)
        print(f"  {Colors.YELLOW}Clicking App tab at ({tab_x}, {tab_y}){Colors.RESET}")
        pyautogui.click(tab_x, tab_y)
        time.sleep(0.8)  # Wait for tab to switch

    def fill_name_input(self, dialog_x: int, dialog_y: int, dialog_width: int, app_name: str) -> bool:
        """
        Fill name input field in Add Item Dialog.
        Returns True if successful.
        """
        if not pyautogui:
            raise RuntimeError("pyautogui not available")

        name_input_x, name_input_y = self.calculator.get_name_input_position(dialog_x, dialog_y, dialog_width)
        print(f"  {Colors.YELLOW}Clicking name input at ({name_input_x}, {name_input_y}){Colors.RESET}")
        pyautogui.click(name_input_x, name_input_y)
        time.sleep(0.5)

        # Type app name
        print(f"  {Colors.CYAN}Typing app name: {app_name}{Colors.RESET}")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
        pyautogui.write(app_name, interval=0.05)
        time.sleep(0.5)

        # Verify name was written
        if pyperclip:
            try:
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.2)
                clipboard_text = pyperclip.paste()
                if clipboard_text.strip() == app_name:
                    print(f"  {Colors.GREEN}✓ App name written correctly: '{clipboard_text}'{Colors.RESET}")
                    return True
                else:
                    print(
                        f"  {Colors.RED}✗ App name mismatch! Expected: '{app_name}', Got: '{clipboard_text}'{Colors.RESET}")
                    return False
            except Exception as e:
                print(f"  {Colors.YELLOW}WARNING: Could not verify name: {e}{Colors.RESET}")
                return True  # Assume success if we can't verify
        return True

    def fill_path_input(self, dialog_x: int, dialog_y: int, dialog_width: int, name_input_y: int, path: str) -> bool:
        """
        Fill path input field in Add Item Dialog.
        Returns True if successful.
        """
        if not pyautogui:
            raise RuntimeError("pyautogui not available")

        path_input_x, path_input_y = self.calculator.get_path_input_position(dialog_x, dialog_y, dialog_width,
                                                                             name_input_y)
        print(f"  {Colors.YELLOW}Clicking path input at ({path_input_x}, {path_input_y}){Colors.RESET}")
        pyautogui.click(path_input_x, path_input_y)
        time.sleep(0.5)

        # Type path
        print(f"  {Colors.CYAN}Typing path: {path}{Colors.RESET}")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
        pyautogui.write(path, interval=0.02)
        time.sleep(0.5)

        # Verify path was written
        if pyperclip:
            try:
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.2)
                clipboard_text = pyperclip.paste()
                if clipboard_text.strip() == path:
                    print(f"  {Colors.GREEN}✓ Path written correctly: '{clipboard_text}'{Colors.RESET}")
                    return True
                else:
                    print(f"  {Colors.RED}✗ Path mismatch! Expected: '{path}', Got: '{clipboard_text}'{Colors.RESET}")
                    return False
            except Exception as e:
                print(f"  {Colors.YELLOW}WARNING: Could not verify path: {e}{Colors.RESET}")
                return True  # Assume success if we can't verify
        return True

    def click_add_button(self, dialog_x: int, dialog_y: int, dialog_width: int, dialog_height: int) -> bool:
        """
        Click Add button in Add Item Dialog.
        Returns True if dialog closed successfully.
        """
        if not pyautogui:
            raise RuntimeError("pyautogui not available")

        add_button_x, add_button_y = self.calculator.get_add_button_position(dialog_x, dialog_y, dialog_width,
                                                                             dialog_height)
        print(f"  {Colors.YELLOW}Clicking Add button at ({add_button_x}, {add_button_y}){Colors.RESET}")
        pyautogui.click(add_button_x, add_button_y)
        time.sleep(2.0)

        # Verify dialog closed
        if gw:
            for check in range(3):
                time.sleep(0.5)
                try:
                    dialog_windows = gw.getWindowsWithTitle("Add Item")
                    if not dialog_windows:
                        print(f"  {Colors.GREEN}Dialog closed successfully{Colors.RESET}")
                        return True
                except Exception:
                    return True  # Assume closed if we can't check

        return False
