"""
Pytest configuration
"""
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QInputDialog, QMessageBox

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def mock_dialogs(monkeypatch):
    """
    Automatically mock dialogs to prevent tests from waiting for user input.
    - QInputDialog.getText: Returns default category name "TestCategory" with ok=True
    - QMessageBox.information: Silently accepts (no dialog shown)
    """

    def mock_get_text(parent, title, label, text="", echo=None, flags=None):
        """Mock QInputDialog.getText - returns default test category name."""
        return ("TestCategory", True)

    def mock_message_box_information(parent, title, text, buttons=QMessageBox.StandardButton.Ok,
                                     defaultButton=QMessageBox.StandardButton.NoButton):
        """Mock QMessageBox.information - silently accepts without showing dialog."""
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QInputDialog, "getText", mock_get_text)
    monkeypatch.setattr(QMessageBox, "information", mock_message_box_information)
