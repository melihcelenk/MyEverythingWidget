"""
Resizable widget mixin
Provides drag-to-resize functionality with grid snapping
"""
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QRect, Signal, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QMouseEvent, QCursor, QBrush


class ResizableMixin:
    """
    Mixin class to add resize functionality to widgets.

    Usage:
        class MyWidget(QWidget, ResizableMixin):
            def __init__(self):
                super().__init__()
                self.init_resizable(min_col=1, max_col=3, min_row=1, max_row=3)
    """

    # Signals (defined in implementing class)
    resizeRequested = Signal(int, int)  # col_span, row_span

    # Grid cell constants
    CELL_WIDTH = 90
    CELL_HEIGHT = 100
    SPACING = 4

    # Resize handle size
    HANDLE_SIZE = 12

    def init_resizable(self, min_col=1, max_col=3, min_row=1, max_row=3):
        """Initialize resizable functionality"""
        self._resize_enabled = False
        self._is_resizing = False
        self._resize_start_pos = QPoint()
        self._resize_start_size = None
        self._original_col = 0
        self._original_row = 0
        self._min_col = min_col
        self._max_col = max_col
        self._min_row = min_row
        self._max_row = max_row
        self._preview_col = 0
        self._preview_row = 0

        # Set mouse tracking for cursor changes
        self.setMouseTracking(True)

    def enable_resize_mode(self):
        """Enable resize mode with red border"""
        self._resize_enabled = True
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def disable_resize_mode(self):
        """Disable resize mode"""
        self._resize_enabled = False
        self._is_resizing = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def is_resize_enabled(self) -> bool:
        """Check if resize mode is enabled"""
        return self._resize_enabled

    def _get_resize_handle_rect(self) -> QRect:
        """Get the resize handle rectangle (bottom-right corner)"""
        return QRect(
            self.width() - self.HANDLE_SIZE,
            self.height() - self.HANDLE_SIZE,
            self.HANDLE_SIZE,
            self.HANDLE_SIZE
        )

    def _is_in_resize_handle(self, pos) -> bool:
        """Check if position is within resize handle"""
        return self._get_resize_handle_rect().contains(pos)

    def _calculate_span_from_size(self, width, height):
        """Calculate col/row span from pixel dimensions"""
        # Calculate column span
        col_span = max(1, round((width + self.SPACING) / (self.CELL_WIDTH + self.SPACING)))
        col_span = max(self._min_col, min(self._max_col, col_span))

        # Calculate row span
        row_span = max(1, round((height + self.SPACING) / (self.CELL_HEIGHT + self.SPACING)))
        row_span = max(self._min_row, min(self._max_row, row_span))

        return col_span, row_span

    def _calculate_size_from_span(self, col_span, row_span):
        """Calculate pixel dimensions from col/row span"""
        width = (self.CELL_WIDTH * col_span) + (self.SPACING * (col_span - 1))
        height = (self.CELL_HEIGHT * row_span) + (self.SPACING * (row_span - 1))
        return width, height

    def paint_resize_overlay(self, painter: QPainter):
        """Paint resize mode overlay (red border and handle)"""
        if not self._resize_enabled:
            return

        # Draw red border
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

        # Draw resize handle
        handle_rect = self._get_resize_handle_rect()
        painter.fillRect(handle_rect, QColor(255, 0, 0))

        # Draw diagonal lines in handle
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        for i in range(3):
            offset = 3 + i * 3
            painter.drawLine(
                handle_rect.right() - offset, handle_rect.bottom(),
                handle_rect.right(), handle_rect.bottom() - offset
            )

        # Draw preview size label if resizing
        if self._is_resizing and self._preview_col > 0:
            # Draw size label in center of current widget
            label = f"{self._preview_col}x{self._preview_row}"
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setBrush(QColor(255, 0, 0, 200))

            # Draw label background
            label_rect = painter.fontMetrics().boundingRect(label)
            label_x = (self.width() - label_rect.width()) // 2 - 4
            label_y = (self.height() - label_rect.height()) // 2 - 2
            painter.drawRect(label_x, label_y, label_rect.width() + 8, label_rect.height() + 4)

            # Draw label text
            painter.drawText(label_x + 4, label_y + label_rect.height(), label)

    def handle_resize_mouse_press(self, event: QMouseEvent) -> bool:
        """Handle mouse press for resize. Returns True if handled."""
        if not self._resize_enabled:
            return False

        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_in_resize_handle(event.position().toPoint()):
                self._is_resizing = True
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_size = self.size()
                self._original_col = getattr(self, '_col_span', 1)
                self._original_row = getattr(self, '_row_span', 1)
                self._preview_col = self._original_col
                self._preview_row = self._original_row
                return True

        return False

    def handle_resize_mouse_move(self, event: QMouseEvent) -> bool:
        """Handle mouse move for resize. Returns True if handled."""
        if not self._resize_enabled:
            return False

        # Update cursor based on position
        if self._is_in_resize_handle(event.position().toPoint()):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        if self._is_resizing:
            # Calculate delta
            delta = event.globalPosition().toPoint() - self._resize_start_pos

            # Calculate new size
            new_width = self._resize_start_size.width() + delta.x()
            new_height = self._resize_start_size.height() + delta.y()

            # Calculate and store preview span
            self._preview_col, self._preview_row = self._calculate_span_from_size(
                new_width, new_height
            )

            # Temporarily resize widget to show preview
            preview_width, preview_height = self._calculate_size_from_span(
                self._preview_col, self._preview_row
            )
            self.setFixedSize(preview_width, preview_height)

            self.update()
            return True

        return False

    def handle_resize_mouse_release(self, event: QMouseEvent) -> bool:
        """Handle mouse release for resize. Returns True if handled."""
        if not self._resize_enabled:
            return False

        if event.button() == Qt.MouseButton.LeftButton and self._is_resizing:
            self._is_resizing = False

            # Emit resize signal with new span
            if hasattr(self, 'resizeRequested'):
                self.resizeRequested.emit(self._preview_col, self._preview_row)

            self.update()
            return True

        return False
