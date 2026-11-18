"""Process management for humanized UI tests."""

import os
import platform
import subprocess
import time
from pathlib import Path

try:
    import pygetwindow as gw
except ImportError:
    gw = None

from .constants import Colors


class ProcessManager:
    """Manages application processes for tests."""

    def __init__(self, project_root: Path, state_file: Path):
        self.project_root = project_root
        self.state_file = state_file

    def kill_all_processes(self, timeout: float = 5.0) -> bool:
        """Kill all running instances of the application. Returns True if successful within timeout."""
        start_time = time.time()

        # On Windows, find and kill only My Everything processes
        if platform.system() == 'Windows':
            try:
                # Find processes by window title instead of killing all Python processes
                if gw:
                    windows = gw.getWindowsWithTitle("My Everything")
                    for win in windows:
                        try:
                            if win.isMinimized:
                                win.restore()
                            win.close()
                        except Exception:
                            pass
                
                time.sleep(0.5)  # Brief wait

                if time.time() - start_time > timeout:
                    return False
            except Exception:
                pass

        # Then close any remaining windows (quick check)
        if gw:
            try:
                all_windows = gw.getAllWindows()
                for win in all_windows:
                    if time.time() - start_time > timeout:
                        break
                    try:
                        title = win.title.lower()
                        if 'my everything' in title or 'already running' in title:
                            try:
                                if win.isMinimized:
                                    win.restore()
                                win.close()
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass

        return time.time() - start_time <= timeout

    def start_app(self, timeout: float = 5.0) -> subprocess.Popen:
        """Start the application in TEST MODE. Returns process handle."""
        # Kill any existing instances first
        self.kill_all_processes(timeout)

        print(f"  {Colors.CYAN}Starting app in test mode...{Colors.RESET}")

        # Set environment variable for test state
        os.environ["MEW_STATE_PATH"] = str(self.state_file)

        # Start new instance
        python_exe = str(self.project_root / ".venv" / "Scripts" / "python.exe")
        main_py = str(self.project_root / "main.py")

        proc = subprocess.Popen(
            f'"{python_exe}" "{main_py}"',
            shell=True,
            cwd=str(self.project_root)
        )

        # Wait for window - with timeout
        print(f"  {Colors.CYAN}Waiting for window ({timeout}s timeout)...{Colors.RESET}")
        start_time = time.time()
        for i in range(int(timeout * 10)):  # Check every 0.1s
            if time.time() - start_time > timeout:
                try:
                    proc.terminate()
                except Exception:
                    pass
                raise RuntimeError(f"App window did not appear within {timeout} seconds")

            time.sleep(0.1)

            if gw:
                try:
                    windows = gw.getWindowsWithTitle("My Everything")
                    if windows:
                        print(f"  {Colors.GREEN}Window found!{Colors.RESET}")
                        return proc
                except Exception:
                    pass

        try:
            proc.terminate()
        except Exception:
            pass
        raise RuntimeError(f"App window did not appear within {timeout} seconds")

    def find_window(self) -> tuple[int, int, int, int]:
        """Find the application window and return its position and size (left, top, width, height)."""
        if not gw:
            raise RuntimeError("pygetwindow not available")

        try:
            windows = gw.getWindowsWithTitle("My Everything")
            if windows:
                win = windows[0]
                try:
                    win.activate()
                except Exception:
                    pass  # Activation may fail, but we can still get position

                # Get window dimensions
                width = win.width if hasattr(win, 'width') and win.width else 320  # Default width
                height = win.height if hasattr(win, 'height') and win.height else 500  # Default height

                return win.left, win.top, width, height
        except Exception:
            pass

        raise RuntimeError("Could not find application window")
