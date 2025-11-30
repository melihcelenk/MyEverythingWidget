"""
Tests for AddItemDialog - unified add dialog for App/Note/Image.
"""
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication

from widgets.add_item_dialog import AddItemDialog


@pytest.fixture(scope="module")
def app():
    """Create QApplication for tests."""
    application = QApplication.instance()
    if application is None:
        application = QApplication([])
    yield application


@pytest.fixture
def dialog(app):
    """Create AddItemDialog for testing."""
    dlg = AddItemDialog("TestCategory")
    yield dlg
    dlg.close()


class TestAddItemDialogStructure:
    """Test dialog structure and tabs."""

    def test_dialog_has_three_tabs(self, dialog):
        """Dialog should have App, Note, Image tabs."""
        tab_widget = dialog._tab_widget
        assert tab_widget.count() == 3

    def test_tab_names(self, dialog):
        """Tabs should be named correctly."""
        tab_widget = dialog._tab_widget
        assert "App" in tab_widget.tabText(0)
        assert "Note" in tab_widget.tabText(1)
        assert "Image" in tab_widget.tabText(2)

    def test_category_name_stored(self, dialog):
        """Category name should be stored."""
        assert dialog.category_name == "TestCategory"

    def test_select_tab_by_name(self, dialog):
        """Should be able to select tab by name."""
        dialog.select_tab("note")
        assert dialog._tab_widget.currentIndex() == 1

        dialog.select_tab("image")
        assert dialog._tab_widget.currentIndex() == 2

        dialog.select_tab("app")
        assert dialog._tab_widget.currentIndex() == 0


class TestAppTab:
    """Test App tab functionality."""

    def test_app_name_input_exists(self, dialog):
        """App tab should have name input."""
        assert hasattr(dialog, '_app_name_input')
        assert dialog._app_name_input is not None

    def test_app_path_input_exists(self, dialog):
        """App tab should have path input."""
        assert hasattr(dialog, '_app_path_input')
        assert dialog._app_path_input is not None

    def test_app_icon_preview_exists(self, dialog):
        """App tab should have icon preview."""
        assert hasattr(dialog, '_app_icon_preview')
        assert dialog._app_icon_preview is not None

    def test_app_added_signal_emitted(self, dialog):
        """appAdded signal should be emitted with correct data."""
        received_data = []
        dialog.appAdded.connect(lambda d: received_data.append(d))

        dialog._app_name_input.setText("Test App")
        dialog._app_path_input.setText("C:\\test\\app.exe")
        dialog._app_icon_path = "📱"

        dialog._on_add_app()

        assert len(received_data) == 1
        assert received_data[0]["name"] == "Test App"
        assert received_data[0]["path"] == "C:\\test\\app.exe"
        assert received_data[0]["icon_path"] == "📱"

    def test_app_not_added_without_name(self, dialog):
        """App should not be added without name."""
        received_data = []
        dialog.appAdded.connect(lambda d: received_data.append(d))

        dialog._app_name_input.setText("")
        dialog._app_path_input.setText("C:\\test\\app.exe")

        dialog._on_add_app()

        assert len(received_data) == 0

    def test_app_not_added_without_path(self, dialog):
        """App should not be added without path."""
        received_data = []
        dialog.appAdded.connect(lambda d: received_data.append(d))

        dialog._app_name_input.setText("Test App")
        dialog._app_path_input.setText("")

        dialog._on_add_app()

        assert len(received_data) == 0


class TestNoteTab:
    """Test Note tab functionality."""

    def test_note_content_input_exists(self, dialog):
        """Note tab should have content input."""
        assert hasattr(dialog, '_note_content_input')
        assert dialog._note_content_input is not None

    def test_note_added_signal_emitted(self, dialog):
        """noteAdded signal should be emitted with content."""
        received_content = []
        dialog.noteAdded.connect(lambda c: received_content.append(c))

        dialog._note_content_input.setPlainText("Test note content")
        dialog._on_add_note()

        assert len(received_content) == 1
        assert received_content[0] == "Test note content"

    def test_note_not_added_when_empty(self, dialog):
        """Note should not be added when content is empty."""
        received_content = []
        dialog.noteAdded.connect(lambda c: received_content.append(c))

        dialog._note_content_input.setPlainText("")
        dialog._on_add_note()

        assert len(received_content) == 0


class TestImageTab:
    """Test Image tab functionality."""

    def test_image_add_button_disabled_initially(self, dialog):
        """Add image button should be disabled initially."""
        assert dialog._add_image_btn.isEnabled() is False

    def test_image_added_signal_emitted(self, dialog):
        """imageAdded signal should be emitted with path."""
        received_paths = []
        dialog.imageAdded.connect(lambda p: received_paths.append(p))

        dialog._selected_image_path = "C:\\test\\image.png"
        dialog._on_add_image()

        assert len(received_paths) == 1
        assert received_paths[0] == "C:\\test\\image.png"

    def test_image_not_added_without_selection(self, dialog):
        """Image should not be added without selection."""
        received_paths = []
        dialog.imageAdded.connect(lambda p: received_paths.append(p))

        dialog._selected_image_path = None
        dialog._on_add_image()

        assert len(received_paths) == 0


class TestIconPicker:
    """Test icon picker integration."""

    @patch('widgets.add_item_dialog.IconPickerDialog')
    def test_pick_icon_updates_preview(self, mock_dialog_class, dialog):
        """Picking icon should update preview."""
        # Mock the dialog
        mock_instance = MagicMock()
        mock_instance.exec.return_value = True
        mock_result = MagicMock()
        mock_result.value = "🚀"
        mock_result.type.value = "emoji"
        mock_instance.get_result.return_value = mock_result
        mock_dialog_class.return_value = mock_instance

        dialog._pick_icon()

        assert dialog._app_icon_path == "🚀"
        assert dialog._app_icon_preview.text() == "🚀"

    @patch('widgets.add_item_dialog.IconPickerDialog')
    def test_pick_image_icon_shows_indicator(self, mock_dialog_class, dialog):
        """Picking image icon should show image indicator."""
        mock_instance = MagicMock()
        mock_instance.exec.return_value = True
        mock_result = MagicMock()
        mock_result.value = "C:\\path\\to\\icon.png"
        mock_result.type.value = "image"
        mock_instance.get_result.return_value = mock_result
        mock_dialog_class.return_value = mock_instance

        dialog._pick_icon()

        assert dialog._app_icon_path == "C:\\path\\to\\icon.png"
        assert dialog._app_icon_preview.text() == "🖼️"
