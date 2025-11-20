"""
Note card widget displays a note preview with copy/delete actions.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
    QWidget,
)
from PySide6.QtCore import Signal, Qt

from window.models.note import Note


class NoteCard(QFrame):
    """Widget representing a single note entry."""

    copyRequested = Signal(str)
    deleteRequested = Signal(str)

    def __init__(self, note: Note, parent: QWidget | None = None):
        super().__init__(parent)
        self.note = note
        self._clipboard = QApplication.clipboard()
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("NoteCard")
        self._build_ui()

    def _build_ui(self):
        icon_label = QLabel(self.note.type.value.upper())
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedWidth(40)

        self._text_label = QLabel(self.note.content)
        self._text_label.setWordWrap(True)
        self._text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._text_label.setToolTip(self.note.content)

        copy_button = QPushButton("Copy")
        delete_button = QPushButton("Delete")

        copy_button.clicked.connect(self._on_copy)
        delete_button.clicked.connect(self._on_delete)

        button_layout = QVBoxLayout()
        button_layout.addWidget(copy_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch(1)

        content_layout = QVBoxLayout()
        content_layout.addWidget(self._text_label)
        content_layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.addWidget(icon_label)
        main_layout.addLayout(content_layout)
        main_layout.addLayout(button_layout)

    def _on_copy(self):
        self._clipboard.setText(self.note.content)
        self.copyRequested.emit(self.note.id)

    def _on_delete(self):
        self.deleteRequested.emit(self.note.id)

    def update_note(self, note: Note):
        self.note = note
        self._text_label.setText(note.content)
        self._text_label.setToolTip(note.content)

