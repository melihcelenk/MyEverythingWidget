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
    QMenu,
    QStyle,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Qt

from window.models.note import Note


class NoteCard(QFrame):
    """Widget representing a single note entry."""

    copyRequested = Signal(str)
    deleteRequested = Signal(str)
    editRequested = Signal(str)

    # Grid cell size constants
    CELL_WIDTH = 90
    CELL_HEIGHT = 100
    SPACING = 4

    def __init__(self, note: Note, col_span: int = 2, parent: QWidget | None = None):
        super().__init__(parent)
        self.note = note
        self._col_span = col_span
        self._clipboard = QApplication.clipboard()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setObjectName("NoteCard")

        # Set fixed size based on span (2 or 3 columns)
        total_width = (self.CELL_WIDTH * col_span) + (self.SPACING * (col_span - 1))
        self.setFixedSize(total_width, self.CELL_HEIGHT)

        self._build_ui()

    @property
    def col_span(self) -> int:
        return self._col_span

    def _build_ui(self):
        # Note emoji icon
        icon_label = QLabel("📝")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedWidth(24)
        icon_label.setStyleSheet("font-size: 14px;")

        # Note text content
        self._text_label = QLabel(self.note.content)
        self._text_label.setWordWrap(True)
        self._text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._text_label.setToolTip(self.note.content)
        self._text_label.setStyleSheet("font-size: 11px;")

        # Small square copy button
        copy_button = QPushButton("📋")
        copy_button.setToolTip("Copy")
        copy_button.setFixedSize(20, 20)
        copy_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f5f5f5;
                font-size: 10px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        copy_button.clicked.connect(self._on_copy)

        # Layout: icon on left, text in middle, copy button top-right
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        # Left side: icon
        main_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignTop)

        # Middle: text content
        main_layout.addWidget(self._text_label, stretch=1)

        # Right side: copy button at top
        button_container = QVBoxLayout()
        button_container.addWidget(copy_button)
        button_container.addStretch(1)
        button_container.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(button_container)

        # Card styling
        self.setStyleSheet("""
            NoteCard {
                background-color: #fffde7;
                border: 1px solid #fff59d;
                border-radius: 6px;
            }
        """)

    def _on_copy(self):
        self._clipboard.setText(self.note.content)
        self.copyRequested.emit(self.note.id)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        action = menu.exec(event.globalPos())
        if action == edit_action:
            self.editRequested.emit(self.note.id)
        elif action == delete_action:
            self.deleteRequested.emit(self.note.id)

    def update_note(self, note: Note):
        self.note = note
        self._text_label.setText(note.content)
        self._text_label.setToolTip(note.content)

