"""
Service for launching applications and URLs
"""
import subprocess
import platform
import webbrowser
from pathlib import Path
from typing import Optional
from models.app_shortcut import AppShortcut, LaunchType


class AppLauncherService:
    """Service for launching applications and URLs"""

    def launch(self, shortcut: AppShortcut) -> bool:
        """Launch an application shortcut"""
        try:
            if shortcut.type == LaunchType.EXE:
                return self._launch_executable(shortcut.target)
            elif shortcut.type == LaunchType.URL:
                return self._launch_url(shortcut.target)
            elif shortcut.type == LaunchType.FOLDER:
                return self._open_folder(shortcut.target)
            return False
        except Exception:
            return False

    def _launch_executable(self, path: str) -> bool:
        """Launch an executable file"""
        try:
            if platform.system() == "Windows":
                subprocess.Popen([path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS)
            else:
                subprocess.Popen([path], start_new_session=True)
            return True
        except Exception:
            return False

    def _launch_url(self, url: str) -> bool:
        """Launch a URL in default browser"""
        try:
            webbrowser.open(url)
            return True
        except Exception:
            return False

    def _open_folder(self, path: str) -> bool:
        """Open a folder in file explorer"""
        try:
            if platform.system() == "Windows":
                subprocess.Popen(['explorer.exe', path], shell=True)
            elif platform.system() == "Linux":
                subprocess.Popen(['xdg-open', path])
            else:
                subprocess.Popen(['open', path])  # macOS
            return True
        except Exception:
            return False

