"""
Pytest configuration file

This file is automatically loaded by pytest before running any tests.
It sets up:
1. Python path - Adds project root to sys.path so imports work
2. Dialog mocking - Automatically mocks UI dialogs so tests don't wait for user input

You don't need to import or call anything from this file - pytest does it automatically.
"""
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QInputDialog, QMessageBox

# Add parent directory to path so we can import from project root
# Example: from models.note import Note
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def mock_dialogs(monkeypatch):
    """
    Automatically mock dialogs to prevent tests from waiting for user input.
    
    This fixture runs automatically for ALL tests (autouse=True).
    It replaces:
    - QInputDialog.getText: Returns default category name "TestCategory" with ok=True
    - QMessageBox.information: Silently accepts (no dialog shown)
    
    This means tests can run automatically without user interaction.
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
