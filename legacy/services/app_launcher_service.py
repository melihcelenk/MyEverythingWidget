"""
Service for launching applications and URLs
"""
import logging
import os
import platform
import subprocess
import webbrowser

from models.app_shortcut import AppShortcut, LaunchType


class AppLauncherService:
    """Service for launching applications and URLs"""

    _logger = logging.getLogger(__name__)

    def launch(self, shortcut: AppShortcut) -> bool:
        """Launch an application shortcut"""
        self._logger.info(f"Launching: {shortcut.name}, type={shortcut.type}, target={shortcut.target}")
        try:
            if shortcut.type == LaunchType.EXE:
                return self._launch_executable(shortcut.target)
            elif shortcut.type == LaunchType.URL:
                return self._launch_url(shortcut.target)
            elif shortcut.type == LaunchType.FOLDER:
                return self._open_folder(shortcut.target)
            self._logger.warning(f"Unknown launch type: {shortcut.type}")
            return False
        except Exception as e:
            self._logger.error(f"Launch failed: {e}")
            return False

    def _launch_executable(self, path: str) -> bool:
        """Launch an executable file"""
        try:
            # Normalize path for Windows
            if platform.system() == "Windows":
                path = path.replace('/', '\\')
                self._logger.debug(f"Launching executable: {path}")
                # Use os.startfile for better Windows compatibility
                os.startfile(path)
            else:
                subprocess.Popen([path], start_new_session=True)
            return True
        except Exception as e:
            self._logger.error(f"Failed to launch executable {path}: {e}")
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
            # Normalize path for Windows
            if platform.system() == "Windows":
                path = path.replace('/', '\\')
                self._logger.debug(f"Opening folder: {path}")
                os.startfile(path)
            elif platform.system() == "Linux":
                subprocess.Popen(['xdg-open', path])
            else:
                subprocess.Popen(['open', path])  # macOS
            return True
        except Exception as e:
            self._logger.error(f"Failed to open folder {path}: {e}")
            return False

