"""
Mixin for drag-and-drop support in grid cards
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QMimeData, Signal
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from typing import Optional

# Grid cell dimensions (must match TabManager/GridDropZone)
CELL_WIDTH = 84  # 80 + 4 spacing
CELL_HEIGHT = 84


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
    _drag_col_span: int
    _drag_row_span: int
    _drag_start_pos: Optional[object]
    _is_drag_over: bool
    _original_style: Optional[str]

    def init_draggable(self, item_id: str, item_type: str,
                       col_span: int = 1, row_span: int = 1):
        """Initialize draggable functionality

        Args:
            item_id: Unique identifier for the item
            item_type: Type of item (app, note, image)
            col_span: Number of columns this item spans (default 1)
            row_span: Number of rows this item spans (default 1)
        """
        self._drag_item_id = item_id
        self._drag_item_type = item_type
        self._drag_col_span = col_span
        self._drag_row_span = row_span
        self._drag_start_pos = None
        self._is_drag_over = False
        self._original_style = None

        # Enable drop
        if isinstance(self, QWidget):
            self.setAcceptDrops(True)

    def update_drag_span(self, col_span: int, row_span: int):
        """Update the span values (call when item is resized)"""
        self._drag_col_span = col_span
        self._drag_row_span = row_span

    def start_drag(self, widget: QWidget):
        """Start a drag operation with visual feedback.

        Creates a drag pixmap that matches the item's actual grid size (span).
        MIME data format: "type:id:col_span:row_span"
        """
        drag = QDrag(widget)
        mime_data = QMimeData()

        # Get span values (use instance vars or try to read from widget)
        col_span = getattr(self, '_drag_col_span', 1)
        row_span = getattr(self, '_drag_row_span', 1)

        # Also check widget attributes as fallback
        if hasattr(widget, 'col_span'):
            col_span = widget.col_span
        if hasattr(widget, 'row_span'):
            row_span = widget.row_span

        # Set custom MIME type with item info INCLUDING span
        # Format: "type:id:col_span:row_span"
        mime_data.setText(
            f"{self._drag_item_type}:{self._drag_item_id}:{col_span}:{row_span}"
        )
        drag.setMimeData(mime_data)

        # Calculate target size based on span
        target_width = col_span * CELL_WIDTH - 4  # Subtract spacing
        target_height = row_span * CELL_HEIGHT - 4

        # Grab the widget at its current size
        source_pixmap = widget.grab()

        # Create drag pixmap at the correct span size
        drag_pixmap = QPixmap(target_width, target_height)
        drag_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(drag_pixmap)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setOpacity(0.7)

        # Scale source to fit target if sizes differ significantly
        if abs(source_pixmap.width() - target_width) > 10 or \
                abs(source_pixmap.height() - target_height) > 10:
            # Scale to fit
            scaled = source_pixmap.scaled(
                target_width, target_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            # Center the scaled pixmap
            x_offset = (target_width - scaled.width()) // 2
            y_offset = (target_height - scaled.height()) // 2
            painter.drawPixmap(x_offset, y_offset, scaled)
        else:
            painter.drawPixmap(0, 0, source_pixmap)

        # Add a prominent blue border to indicate dragging
        painter.setOpacity(1.0)
        pen = QPen(QColor(33, 150, 243, 220))  # Material Blue
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(1, 1, target_width - 3, target_height - 3)
        painter.end()

        drag.setPixmap(drag_pixmap)
        # Set hotspot to center of the drag pixmap
        drag.setHotSpot(drag_pixmap.rect().center())

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
