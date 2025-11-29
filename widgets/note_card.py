"""
Note card widget displays a note preview with copy/delete actions.
"""
from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter, QMouseEvent
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
)

from widgets.draggable_mixin import DraggableMixin
from widgets.resizable_mixin import ResizableMixin
from window.models.note import Note


class NoteCard(QFrame, ResizableMixin, DraggableMixin):
    """Widget representing a single note entry."""

    copyRequested = Signal(str)
    deleteRequested = Signal(str)
    editRequested = Signal(str)
    resizeRequested = Signal(int, int)  # col_span, row_span
    relocateRequested = Signal(str, str)  # note_id, new_category
    itemDropped = Signal(str, str)  # item_id, target_item_id

    # Grid cell size constants
    CELL_WIDTH = 90
    CELL_HEIGHT = 100
    SPACING = 4

    def __init__(self, note: Note, col_span: int = 2, row_span: int = 1, parent: QWidget | None = None):
        super().__init__(parent)
        self.note = note
        self._col_span = col_span
        self._row_span = row_span
        self._clipboard = QApplication.clipboard()
        self._categories = []  # Available categories for relocation
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setObjectName("NoteCard")

        # Initialize resizable mixin
        self.init_resizable(min_col=2, max_col=3, min_row=1, max_row=2)

        # Initialize draggable mixin
        self.init_draggable(note.id, "note")

        # Set fixed size based on span
        self._update_size()
        self._build_ui()

    def set_categories(self, categories: list):
        """Set available categories for relocation"""
        self._categories = categories

    def _update_size(self):
        """Update widget size based on current span"""
        total_width = (self.CELL_WIDTH * self._col_span) + (self.SPACING * (self._col_span - 1))
        total_height = (self.CELL_HEIGHT * self._row_span) + (self.SPACING * (self._row_span - 1))
        self.setFixedSize(total_width, total_height)

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
        resize_action = menu.addAction("Resize")

        # Relocate submenu
        relocate_menu = menu.addMenu("Relocate")
        category_actions = {}
        for cat in self._categories:
            if cat.name != self.note.category and cat.name != "All":
                action = relocate_menu.addAction(f"{cat.icon} {cat.name}")
                category_actions[action] = cat.name

        delete_action = menu.addAction("Delete")
        action = menu.exec(event.globalPos())

        if action == edit_action:
            self.editRequested.emit(self.note.id)
        elif action == resize_action:
            if self.is_resize_enabled():
                self.disable_resize_mode()
            else:
                self.enable_resize_mode()
        elif action == delete_action:
            self.deleteRequested.emit(self.note.id)
        elif action in category_actions:
            self.relocateRequested.emit(self.note.id, category_actions[action])

    def paintEvent(self, event):
        """Override to draw resize overlay"""
        super().paintEvent(event)
        if self._resize_enabled:
            painter = QPainter(self)
            self.paint_resize_overlay(painter)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if self.handle_resize_mouse_press(event):
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.handle_drag_mouse_press(event)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        if self.handle_resize_mouse_move(event):
            event.accept()
            return
        if self.handle_drag_mouse_move(event, self):
            event.accept()
            return
        event.accept()  # Always accept to prevent window dragging

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if self.handle_resize_mouse_release(event):
            return
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        """Handle drag enter"""
        self.handle_drag_enter(event)

    def dragLeaveEvent(self, event):
        """Handle drag leave"""
        self.handle_drag_leave(event)

    def dropEvent(self, event):
        """Handle drop"""
        # Extract dragged item info from drop event
        item_type, item_id = self.handle_drop(event, 0)  # index not used
        if item_type and item_id:
            # Emit signal with dragged item ID and this card's ID (target)
            self.itemDropped.emit(item_id, self.note.id)

    @property
    def row_span(self) -> int:
        return self._row_span

    def set_span(self, col_span: int, row_span: int):
        """Set new span and update size"""
        self._col_span = col_span
        self._row_span = row_span
        self._update_size()
        self.update()

    def update_note(self, note: Note):
        self.note = note
        self._text_label.setText(note.content)
        self._text_label.setToolTip(note.content)

