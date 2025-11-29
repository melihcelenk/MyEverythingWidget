"""
Grid drop zone widget for Android-like drag and drop
"""
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget


class GridDropZone(QWidget):
    """Widget that accepts grid-based drops and provides visual feedback.

    This widget overlays the grid layout and handles drop events, converting
    mouse positions to grid cell coordinates.
    """

    # Emitted when an item is dropped: (item_id, target_row, target_col)
    gridDropped = Signal(str, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        # Visual feedback state
        self._drag_active = False
        self._hover_cell = None  # (row, col) tuple
        self._dragging_item_id = None

        # Grid configuration (matches TabManager settings)
        self.CELL_WIDTH = 90 + 4  # column width + spacing
        self.CELL_HEIGHT = 90 + 4  # approximate height + spacing
        self.GRID_COLS = 3

        # Widget should be transparent to mouse events so clicks pass through
        # to underlying widgets, but we still receive drag events
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        # Make background transparent
        self.setStyleSheet("background: transparent;")

        # Raise to front so we receive drop events
        self.raise_()

    def resizeEvent(self, event):
        """Update size when parent resizes"""
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())

    def dragEnterEvent(self, event):
        """Handle drag enter - check if we accept this drag"""
        mime_data = event.mimeData()

        # Check if this is an item drag (format: "type:id")
        if mime_data.hasText() and ':' in mime_data.text():
            text = mime_data.text()
            parts = text.split(':', 1)
            if len(parts) == 2:
                self._drag_active = True
                self._dragging_item_id = parts[1]  # Extract ID from "type:id"
                event.acceptProposedAction()
                self.update()  # Trigger repaint
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move - update hover cell for visual feedback"""
        if not self._drag_active:
            event.ignore()
            return

        # Convert mouse position to grid cell
        pos = event.position().toPoint()
        cell = self._pos_to_cell(pos)

        if cell != self._hover_cell:
            self._hover_cell = cell
            self.update()  # Trigger repaint to show new hover cell

        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """Handle drag leave - clear visual feedback"""
        self._drag_active = False
        self._hover_cell = None
        self._dragging_item_id = None
        self.update()  # Clear visual feedback
        event.accept()

    def dropEvent(self, event):
        """Handle drop - emit signal with grid coordinates"""
        if not self._drag_active or self._dragging_item_id is None:
            event.ignore()
            return

        # Convert drop position to grid cell
        pos = event.position().toPoint()
        cell = self._pos_to_cell(pos)

        if cell is not None:
            row, col = cell
            self.gridDropped.emit(self._dragging_item_id, row, col)
            event.acceptProposedAction()
        else:
            event.ignore()

        # Clear drag state
        self._drag_active = False
        self._hover_cell = None
        self._dragging_item_id = None
        self.update()  # Clear visual feedback

    def paintEvent(self, event):
        """Paint visual feedback during drag"""
        super().paintEvent(event)

        if not self._drag_active or self._hover_cell is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw highlight for hover cell
        row, col = self._hover_cell
        x = col * self.CELL_WIDTH
        y = row * self.CELL_HEIGHT

        # Semi-transparent blue highlight
        painter.fillRect(
            x, y,
            self.CELL_WIDTH - 4,  # Subtract spacing
            self.CELL_HEIGHT - 4,
            QColor(33, 150, 243, 80)  # #2196F3 with alpha
        )

        # Draw border
        pen = QPen(QColor(33, 150, 243), 2)  # #2196F3
        painter.setPen(pen)
        painter.drawRect(
            x, y,
            self.CELL_WIDTH - 4,
            self.CELL_HEIGHT - 4
        )

    def _pos_to_cell(self, pos: QPoint) -> tuple[int, int] | None:
        """Convert mouse position to grid cell coordinates.

        Args:
            pos: Mouse position in widget coordinates

        Returns:
            (row, col) tuple or None if outside valid grid
        """
        col = pos.x() // self.CELL_WIDTH
        row = pos.y() // self.CELL_HEIGHT

        # Clamp to valid range
        col = max(0, min(col, self.GRID_COLS - 1))
        row = max(0, row)

        return (row, col)
