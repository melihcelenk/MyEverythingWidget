"""
Mixin for drag-and-drop support in grid cards
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QMimeData, Signal
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from typing import Optional


class DraggableMixin:
    """Mixin to add drag-and-drop functionality to cards.

    This mixin is intended to be used with QWidget subclasses.
    """

    # Signal emitted when item is dropped (item_id, target_item_id)
    # target_item_id is the ID of the item that was dropped onto
    itemDropped = Signal(str, str)

    # Type hints for instance attributes (initialized in init_draggable)
    _drag_item_id: str
    _drag_item_type: str
    _drag_start_pos: Optional[object]
    _is_drag_over: bool
    _original_style: Optional[str]

    def init_draggable(self, item_id: str, item_type: str):
        """Initialize draggable functionality

        Args:
            item_id: Unique identifier for the item
            item_type: Type of item (app, note, image)
        """
        self._drag_item_id = item_id
        self._drag_item_type = item_type
        self._drag_start_pos = None
        self._is_drag_over = False
        self._original_style = None

        # Enable drop
        if isinstance(self, QWidget):
            self.setAcceptDrops(True)

    def start_drag(self, widget: QWidget):
        """Start a drag operation with visual feedback"""
        drag = QDrag(widget)
        mime_data = QMimeData()

        # Set custom MIME type with item info
        mime_data.setText(f"{self._drag_item_type}:{self._drag_item_id}")
        drag.setMimeData(mime_data)

        # Create drag pixmap with better visual feedback
        pixmap = widget.grab()

        # Create semi-transparent version with border
        drag_pixmap = QPixmap(pixmap.size())
        drag_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(drag_pixmap)
        painter.setOpacity(0.7)
        painter.drawPixmap(0, 0, pixmap)

        # Add a subtle blue border to indicate dragging
        painter.setOpacity(1.0)
        pen_color = QColor(33, 150, 243, 200)  # Material Blue
        painter.setPen(pen_color)
        painter.drawRect(0, 0, pixmap.width() - 1, pixmap.height() - 1)
        painter.end()

        drag.setPixmap(drag_pixmap)
        drag.setHotSpot(widget.rect().center())

        # Execute drag
        drag.exec(Qt.DropAction.MoveAction)

    def handle_drag_mouse_press(self, event) -> bool:
        """Handle mouse press for drag initiation"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.position().toPoint()
        return False

    def handle_drag_mouse_move(self, event, widget: QWidget) -> bool:
        """Handle mouse move for drag detection"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return False

        if self._drag_start_pos is None:
            return False

        # Check if moved enough to start drag
        distance = (event.position().toPoint() - self._drag_start_pos).manhattanLength()
        if distance < 10:  # Minimum drag distance
            return False

        self.start_drag(widget)
        self._drag_start_pos = None
        return True

    def handle_drag_enter(self, event) -> bool:
        """Handle drag enter event with visual feedback"""
        mime_data = event.mimeData()
        if mime_data.hasText():
            text = mime_data.text()
            if ":" in text:
                event.acceptProposedAction()
                self._is_drag_over = True
                # Show drop indicator
                self._show_drop_indicator()
                return True
        event.ignore()
        return False

    def handle_drag_leave(self, event) -> bool:
        """Handle drag leave event"""
        self._is_drag_over = False
        self._hide_drop_indicator()
        return True

    def _show_drop_indicator(self):
        """Show visual indicator that this is a valid drop target"""
        if not isinstance(self, QWidget):
            return
        # Store original style if not already stored
        if self._original_style is None:
            self._original_style = self.styleSheet()
        # Add drop indicator style (blue dashed border)
        current_style = self._original_style or ""
        # Append indicator style
        self.setStyleSheet(current_style + """
            * {
                border: 2px dashed #2196F3 !important;
            }
        """)

    def _hide_drop_indicator(self):
        """Hide the drop indicator and restore original style"""
        if not isinstance(self, QWidget):
            return
        if self._original_style is not None:
            self.setStyleSheet(self._original_style)
            self._original_style = None

    def handle_drop(self, event, target_index: int) -> tuple:
        """Handle drop event

        Returns:
            Tuple of (item_type, item_id) or (None, None) if invalid
        """
        # Hide drop indicator
        self._is_drag_over = False
        self._hide_drop_indicator()

        mime_data = event.mimeData()
        if mime_data.hasText():
            text = mime_data.text()
            if ":" in text:
                item_type, item_id = text.split(":", 1)
                event.acceptProposedAction()
                return item_type, item_id

        event.ignore()
        return None, None
