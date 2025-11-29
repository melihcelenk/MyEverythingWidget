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

    MIME data format: "type:id:col_span:row_span"
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
        self._dragging_col_span = 1
        self._dragging_row_span = 1

        # Grid configuration (matches TabManager settings)
        self.CELL_WIDTH = 90 + 4  # column width + spacing
        self.CELL_HEIGHT = 90 + 4  # approximate height + spacing
        self.GRID_COLS = 3

        # No need to set transparent - we ARE the container
        # Background is transparent during normal use, highlighted during drag
        self.setStyleSheet("background: white;")

    def dragEnterEvent(self, event):
        """Handle drag enter - check if we accept this drag

        MIME format: "type:id:col_span:row_span" or legacy "type:id"
        """
        mime_data = event.mimeData()

        if mime_data.hasText() and ':' in mime_data.text():
            text = mime_data.text()
            parts = text.split(':')

            if len(parts) >= 2:
                self._drag_active = True
                # parts[0] = type, parts[1] = id
                self._dragging_item_id = parts[1]

                # Parse span (new format) or default to 1x1 (legacy)
                if len(parts) >= 4:
                    try:
                        self._dragging_col_span = int(parts[2])
                        self._dragging_row_span = int(parts[3])
                    except (ValueError, IndexError):
                        self._dragging_col_span = 1
                        self._dragging_row_span = 1
                else:
                    self._dragging_col_span = 1
                    self._dragging_row_span = 1

                event.acceptProposedAction()
                self.update()  # Trigger repaint
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move - update hover cell for visual feedback

        Adjusts target column if item would overflow grid columns.
        """
        if not self._drag_active:
            event.ignore()
            return

        # Convert mouse position to grid cell
        pos = event.position().toPoint()
        cell = self._pos_to_cell(pos)

        if cell is not None:
            row, col = cell

            # Adjust column if item would overflow (col + span > GRID_COLS)
            if col + self._dragging_col_span > self.GRID_COLS:
                col = self.GRID_COLS - self._dragging_col_span
                col = max(0, col)  # Ensure non-negative

            adjusted_cell = (row, col)

            if adjusted_cell != self._hover_cell:
                self._hover_cell = adjusted_cell
                self.update()  # Trigger repaint to show new hover cell

        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """Handle drag leave - clear visual feedback"""
        self._drag_active = False
        self._hover_cell = None
        self._dragging_item_id = None
        self._dragging_col_span = 1
        self._dragging_row_span = 1
        self.update()  # Clear visual feedback
        event.accept()

    def dropEvent(self, event):
        """Handle drop - emit signal with grid coordinates

        Uses the adjusted hover cell (accounts for span overflow).
        """
        if not self._drag_active or self._dragging_item_id is None:
            event.ignore()
            return

        # Use the hover cell (already adjusted for overflow in dragMoveEvent)
        if self._hover_cell is not None:
            row, col = self._hover_cell
            self.gridDropped.emit(self._dragging_item_id, row, col)
            event.acceptProposedAction()
        else:
            event.ignore()

        # Clear drag state
        self._drag_active = False
        self._hover_cell = None
        self._dragging_item_id = None
        self._dragging_col_span = 1
        self._dragging_row_span = 1
        self.update()  # Clear visual feedback

    def paintEvent(self, event):
        """Paint visual feedback during drag

        Highlights all cells that the item will occupy (based on span).
        """
        super().paintEvent(event)

        if not self._drag_active or self._hover_cell is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        row, col = self._hover_cell
        col_span = self._dragging_col_span
        row_span = self._dragging_row_span

        # Calculate total highlight area (all cells the item will occupy)
        x = col * self.CELL_WIDTH
        y = row * self.CELL_HEIGHT
        total_width = col_span * self.CELL_WIDTH - 4  # Subtract last spacing
        total_height = row_span * self.CELL_HEIGHT - 4

        # Semi-transparent blue highlight for entire span area
        painter.fillRect(
            x, y,
            total_width,
            total_height,
            QColor(33, 150, 243, 80)  # #2196F3 with alpha
        )

        # Draw border around entire span area
        pen = QPen(QColor(33, 150, 243), 2)  # #2196F3
        painter.setPen(pen)
        painter.drawRect(
            x, y,
            total_width,
            total_height
        )

        # Optionally draw grid lines for individual cells within the span
        if col_span > 1 or row_span > 1:
            pen.setStyle(Qt.PenStyle.DotLine)
            pen.setWidth(1)
            painter.setPen(pen)

            # Vertical lines between columns
            for c in range(1, col_span):
                line_x = x + c * self.CELL_WIDTH
                painter.drawLine(line_x, y, line_x, y + total_height)

            # Horizontal lines between rows
            for r in range(1, row_span):
                line_y = y + r * self.CELL_HEIGHT
                painter.drawLine(x, line_y, x + total_width, line_y)

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
