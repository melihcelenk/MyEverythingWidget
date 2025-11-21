"""
Mixin for drag-and-drop support in grid cards
"""
from PySide6.QtCore import Qt, QMimeData, Signal
from PySide6.QtGui import QDrag, QPixmap, QPainter
from PySide6.QtWidgets import QWidget


class DraggableMixin:
    """Mixin to add drag-and-drop functionality to cards"""

    # Signal emitted when item is dropped (item_id, target_index)
    itemDropped = Signal(str, int)

    def init_draggable(self, item_id: str, item_type: str):
        """Initialize draggable functionality

        Args:
            item_id: Unique identifier for the item
            item_type: Type of item (app, note, image)
        """
        self._drag_item_id = item_id
        self._drag_item_type = item_type
        self._drag_start_pos = None

        # Enable drop
        if isinstance(self, QWidget):
            self.setAcceptDrops(True)

    def start_drag(self, widget: QWidget):
        """Start a drag operation"""
        drag = QDrag(widget)
        mime_data = QMimeData()

        # Set custom MIME type with item info
        mime_data.setText(f"{self._drag_item_type}:{self._drag_item_id}")
        drag.setMimeData(mime_data)

        # Create drag pixmap (semi-transparent snapshot)
        pixmap = widget.grab()
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), Qt.GlobalColor.transparent)
        painter.end()

        # Make it semi-transparent
        transparent = QPixmap(pixmap.size())
        transparent.fill(Qt.GlobalColor.transparent)
        painter = QPainter(transparent)
        painter.setOpacity(0.7)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        drag.setPixmap(transparent)
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
        """Handle drag enter event"""
        mime_data = event.mimeData()
        if mime_data.hasText():
            text = mime_data.text()
            if ":" in text:
                event.acceptProposedAction()
                return True
        event.ignore()
        return False

    def handle_drop(self, event, target_index: int) -> tuple:
        """Handle drop event

        Returns:
            Tuple of (item_type, item_id) or (None, None) if invalid
        """
        mime_data = event.mimeData()
        if mime_data.hasText():
            text = mime_data.text()
            if ":" in text:
                item_type, item_id = text.split(":", 1)
                event.acceptProposedAction()
                return (item_type, item_id)

        event.ignore()
        return (None, None)
