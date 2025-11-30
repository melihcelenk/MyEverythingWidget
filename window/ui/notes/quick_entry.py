"""
QuickNoteEntry - Widget for adding quick text notes.

Single Responsibility: Provide UI for quick note input.
"""
import uuid
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton

from window.models.note import Note, NoteType

if TYPE_CHECKING:
    from window.app_state import AppState


class QuickNoteEntry(QWidget):
    """Widget for quickly adding text notes."""

    def __init__(self, category_name: str, app_state: 'AppState', parent=None):
        super().__init__(parent)
        self._category_name = category_name
        self._app_state = app_state
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self._line_edit = QLineEdit()
        self._line_edit.setPlaceholderText("Add a quick note...")
        self._line_edit.returnPressed.connect(self._add_note)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self._add_note)

        layout.addWidget(self._line_edit)
        layout.addWidget(add_button)

    def _add_note(self):
        """Add note from input field."""
        content = self._line_edit.text().strip()
        if not content:
            return

        note = Note(
            id=str(uuid.uuid4()),
            content=content,
            type=NoteType.TEXT,
            category=self._category_name,
        )
        self._app_state.add_note(note)
        self._line_edit.clear()
