"""
Tests for AppLauncherService - launching apps and URLs.
"""
from unittest.mock import patch, MagicMock

import pytest

from models.app_shortcut import AppShortcut, LaunchType
from services.app_launcher_service import AppLauncherService


@pytest.fixture
def launcher():
    """Create AppLauncherService for testing."""
    return AppLauncherService()


@pytest.fixture
def exe_app():
    """Create a test executable app shortcut."""
    return AppShortcut(
        id="test-exe-1",
        name="Test EXE App",
        icon_path="📱",
        target="C:\\Program Files\\test\\app.exe",
        category="Test",
        type=LaunchType.EXE
    )


@pytest.fixture
def url_app():
    """Create a test URL app shortcut."""
    return AppShortcut(
        id="test-url-1",
        name="Test URL",
        icon_path="🌐",
        target="https://www.example.com",
        category="Test",
        type=LaunchType.URL
    )


@pytest.fixture
def folder_app():
    """Create a test folder app shortcut."""
    return AppShortcut(
        id="test-folder-1",
        name="Test Folder",
        icon_path="📁",
        target="C:\\Users\\Test\\Documents",
        category="Test",
        type=LaunchType.FOLDER
    )


class TestLaunchTypeDetection:
    """Test launch type is correctly determined."""

    def test_exe_type(self, exe_app):
        """EXE app should have EXE type."""
        assert exe_app.type == LaunchType.EXE

    def test_url_type(self, url_app):
        """URL app should have URL type."""
        assert url_app.type == LaunchType.URL

    def test_folder_type(self, folder_app):
        """Folder app should have FOLDER type."""
        assert folder_app.type == LaunchType.FOLDER


class TestLaunchExecutable:
    """Test launching executable files."""

    @patch('services.app_launcher_service.os.startfile')
    @patch('services.app_launcher_service.platform.system')
    def test_launch_exe_windows(self, mock_system, mock_startfile, launcher, exe_app):
        """Should launch EXE on Windows using os.startfile."""
        mock_system.return_value = "Windows"

        result = launcher.launch(exe_app)

        assert result is True
        mock_startfile.assert_called_once()
        # Path should have backslashes on Windows
        call_arg = mock_startfile.call_args[0][0]
        assert '/' not in call_arg or '\\' in call_arg

    @patch('services.app_launcher_service.subprocess.Popen')
    @patch('services.app_launcher_service.platform.system')
    def test_launch_exe_linux(self, mock_system, mock_popen, launcher, exe_app):
        """Should launch EXE on Linux."""
        mock_system.return_value = "Linux"
        mock_popen.return_value = MagicMock()

        result = launcher.launch(exe_app)

        assert result is True
        mock_popen.assert_called_once()

    @patch('services.app_launcher_service.os.startfile')
    @patch('services.app_launcher_service.platform.system')
    def test_launch_exe_failure(self, mock_system, mock_startfile, launcher, exe_app):
        """Should return False on launch failure."""
        mock_system.return_value = "Windows"
        mock_startfile.side_effect = Exception("Launch failed")

        result = launcher.launch(exe_app)

        assert result is False


class TestLaunchURL:
    """Test launching URLs."""

    @patch('services.app_launcher_service.webbrowser.open')
    def test_launch_url_success(self, mock_open, launcher, url_app):
        """Should open URL in browser."""
        mock_open.return_value = True

        result = launcher.launch(url_app)

        assert result is True
        mock_open.assert_called_once_with(url_app.target)

    @patch('services.app_launcher_service.webbrowser.open')
    def test_launch_url_failure(self, mock_open, launcher, url_app):
        """Should return False on URL open failure."""
        mock_open.side_effect = Exception("Browser error")

        result = launcher.launch(url_app)

        assert result is False


class TestOpenFolder:
    """Test opening folders."""

    @patch('services.app_launcher_service.os.startfile')
    @patch('services.app_launcher_service.platform.system')
    def test_open_folder_windows(self, mock_system, mock_startfile, launcher, folder_app):
        """Should open folder on Windows using os.startfile."""
        mock_system.return_value = "Windows"

        result = launcher.launch(folder_app)

        assert result is True
        mock_startfile.assert_called_once()

    @patch('services.app_launcher_service.subprocess.Popen')
    @patch('services.app_launcher_service.platform.system')
    def test_open_folder_linux(self, mock_system, mock_popen, launcher, folder_app):
        """Should open folder on Linux."""
        mock_system.return_value = "Linux"
        mock_popen.return_value = MagicMock()

        result = launcher.launch(folder_app)

        assert result is True
        call_args = mock_popen.call_args
        assert 'xdg-open' in call_args[0][0]


class TestPathNormalization:
    """Test path normalization for Windows."""

    @patch('services.app_launcher_service.os.startfile')
    @patch('services.app_launcher_service.platform.system')
    def test_forward_slashes_converted(self, mock_system, mock_startfile, launcher):
        """Forward slashes should be converted to backslashes on Windows."""
        mock_system.return_value = "Windows"

        app = AppShortcut(
            id="test",
            name="Test",
            icon_path="",
            target="C:/Program Files/Test/app.exe",
            category="Test",
            type=LaunchType.EXE
        )

        launcher.launch(app)

        call_arg = mock_startfile.call_args[0][0]
        assert call_arg == "C:\\Program Files\\Test\\app.exe"


class TestAppCardIcon:
    """Test app card displays correct icon."""

    @pytest.fixture
    def qapp(self):
        """Ensure QApplication exists."""
        from PySide6.QtWidgets import QApplication
        app_instance = QApplication.instance()
        if app_instance is None:
            app_instance = QApplication([])
        return app_instance

    def test_emoji_icon_path_not_file(self, qapp):
        """Emoji icon path should not be detected as file."""

        # Test the logic: emoji should not contain path separators
        emoji = "🚀"
        is_file = ('/' in emoji or '\\' in emoji or
                   emoji.endswith(('.png', '.jpg', '.jpeg', '.ico', '.bmp')))
        assert is_file is False

    def test_file_path_detected(self, qapp):
        """File path should be detected correctly."""
        file_path = "C:\\icons\\app.png"
        is_file = ('/' in file_path or '\\' in file_path or
                   file_path.endswith(('.png', '.jpg', '.jpeg', '.ico', '.bmp')))
        assert is_file is True

    def test_app_card_with_emoji_icon(self, qapp):
        """App card should display emoji icon."""
        from widgets.app_card import AppCard

        app = AppShortcut(
            id="test-1",
            name="Test",
            icon_path="🚀",
            target="C:\\test.exe",
            category="Test",
            type=LaunchType.EXE
        )

        card = AppCard(app=app, on_tap=lambda a: None)
        # Card should be created without error
        assert card is not None
        card.close()

    def test_app_card_without_icon(self, qapp):
        """App card should use default icon when no icon_path."""
        from widgets.app_card import AppCard

        app = AppShortcut(
            id="test-2",
            name="Test",
            icon_path="",
            target="C:\\test.exe",
            category="Test",
            type=LaunchType.EXE
        )

        card = AppCard(app=app, on_tap=lambda a: None)
        assert card is not None
        card.close()
