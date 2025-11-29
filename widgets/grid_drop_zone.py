"""
Grid drop zone widget for Android-like drag and drop

Android Launcher Grid System:
- Fixed grid size (3 columns x 5 rows)
- Items have explicit (row, col) positions
- Gaps are preserved - no auto-compacting
- Collision detection prevents overlap
- No scrolling (fixed viewport)
"""
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget


class GridDropZone(QWidget):
    """Widget that accepts grid-based drops and provides visual feedback.

    This widget is the container for the grid layout and handles drop events,
    converting mouse positions to grid cell coordinates.

    MIME data format: "type:id:col_span:row_span"
    """

    # Emitted when an item is dropped: (item_id, target_row, target_col)
    gridDropped = Signal(str, int, int)

    # Fixed grid dimensions (Android-like)
    GRID_COLS = 3
    GRID_ROWS = 5

    # Cell dimensions (must match actual widget sizes)
    CELL_WIDTH = 90
    CELL_HEIGHT = 100
    SPACING = 4

    # Layout margins (must match QGridLayout margins)
    MARGIN_LEFT = 8
    MARGIN_TOP = 4
    MARGIN_RIGHT = 8
    MARGIN_BOTTOM = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        # Visual feedback state
        self._drag_active = False
        self._hover_cell = None  # (row, col) tuple
        self._dragging_item_id = None
        self._dragging_col_span = 1
        self._dragging_row_span = 1

        # Set fixed size for 3x5 grid
        total_width = self.MARGIN_LEFT + self.GRID_COLS * (
                    self.CELL_WIDTH + self.SPACING) - self.SPACING + self.MARGIN_RIGHT
        total_height = self.MARGIN_TOP + self.GRID_ROWS * (
                    self.CELL_HEIGHT + self.SPACING) - self.SPACING + self.MARGIN_BOTTOM

        self.setMinimumSize(total_width, total_height)
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
                self.update()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move - update hover cell for visual feedback

        Clamps to valid grid bounds (3x5) and adjusts for item span.
        """
        if not self._drag_active:
            event.ignore()
            return

        # Convert mouse position to grid cell
        pos = event.position().toPoint()
        cell = self._pos_to_cell(pos)

        if cell is not None:
            row, col = cell

            # Clamp column so item doesn't overflow right edge
            max_col = self.GRID_COLS - self._dragging_col_span
            col = max(0, min(col, max_col))

            # Clamp row so item doesn't overflow bottom edge
            max_row = self.GRID_ROWS - self._dragging_row_span
            row = max(0, min(row, max_row))

            adjusted_cell = (row, col)

            if adjusted_cell != self._hover_cell:
                self._hover_cell = adjusted_cell
                self.update()

        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """Handle drag leave - clear visual feedback"""
        self._drag_active = False
        self._hover_cell = None
        self._dragging_item_id = None
        self._dragging_col_span = 1
        self._dragging_row_span = 1
        self.update()
        event.accept()

    def dropEvent(self, event):
        """Handle drop - emit signal with grid coordinates

        Uses the adjusted hover cell (accounts for span and grid bounds).
        """
        if not self._drag_active or self._dragging_item_id is None:
            event.ignore()
            return

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
        self.update()

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

        # Calculate pixel position (accounting for margins)
        x = self.MARGIN_LEFT + col * (self.CELL_WIDTH + self.SPACING)
        y = self.MARGIN_TOP + row * (self.CELL_HEIGHT + self.SPACING)

        # Calculate total size (accounting for spacing between cells)
        total_width = col_span * self.CELL_WIDTH + (col_span - 1) * self.SPACING
        total_height = row_span * self.CELL_HEIGHT + (row_span - 1) * self.SPACING

        # Semi-transparent blue highlight
        painter.fillRect(
            x, y,
            total_width,
            total_height,
            QColor(33, 150, 243, 80)
        )

        # Draw border
        pen = QPen(QColor(33, 150, 243), 2)
        painter.setPen(pen)
        painter.drawRect(x, y, total_width, total_height)

        # Draw grid lines for multi-cell items
        if col_span > 1 or row_span > 1:
            pen.setStyle(Qt.PenStyle.DotLine)
            pen.setWidth(1)
            painter.setPen(pen)

            for c in range(1, col_span):
                line_x = x + c * (self.CELL_WIDTH + self.SPACING)
                painter.drawLine(line_x, y, line_x, y + total_height)

            for r in range(1, row_span):
                line_y = y + r * (self.CELL_HEIGHT + self.SPACING)
                painter.drawLine(x, line_y, x + total_width, line_y)

    def _pos_to_cell(self, pos: QPoint) -> tuple[int, int] | None:
        """Convert mouse position to grid cell coordinates.

        Accounts for margins and spacing.

        Args:
            pos: Mouse position in widget coordinates

        Returns:
            (row, col) tuple or None if outside grid
        """
        # Subtract margins
        x = pos.x() - self.MARGIN_LEFT
        y = pos.y() - self.MARGIN_TOP

        if x < 0 or y < 0:
            return (0, 0)

        # Calculate cell (accounting for spacing)
        cell_with_spacing = self.CELL_WIDTH + self.SPACING
        col = x // cell_with_spacing

        cell_height_with_spacing = self.CELL_HEIGHT + self.SPACING
        row = y // cell_height_with_spacing

        # Clamp to grid bounds
        col = max(0, min(col, self.GRID_COLS - 1))
        row = max(0, min(row, self.GRID_ROWS - 1))

        return (row, col)
