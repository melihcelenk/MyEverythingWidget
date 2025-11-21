"""
Image card widget
Displays an image in the grid with delete option
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QMouseEvent
from services.image_grid_calculator import ImageGridCalculator
from widgets.resizable_mixin import ResizableMixin


class ImageCard(QWidget, ResizableMixin):
    """Widget to display an image in the grid"""

    # Signals
    deleteRequested = Signal(str)
    resizeRequested = Signal(int, int)  # col_span, row_span
    relocateRequested = Signal(str, str)  # image_id, new_category

    # Base size for one grid cell
    CELL_WIDTH = 90
    CELL_HEIGHT = 100
    SPACING = 4

    def __init__(self, image_id: str, pixmap: QPixmap, on_delete=None, parent=None):
        super().__init__(parent)
        self._image_id = image_id
        self._pixmap = pixmap
        self._on_delete = on_delete
        self._categories = []  # Available categories for relocation
        self._current_category = ""

        # Calculate span based on aspect ratio
        calculator = ImageGridCalculator()
        self._col_span, self._row_span = calculator.calculate_span(
            pixmap.width(), pixmap.height()
        )

        # Initialize resizable mixin
        self.init_resizable(min_col=1, max_col=3, min_row=1, max_row=3)

        self._init_ui()

    def set_categories(self, categories: list, current_category: str = ""):
        """Set available categories for relocation"""
        self._categories = categories
        self._current_category = current_category

    @property
    def image_id(self) -> str:
        return self._image_id

    @property
    def col_span(self) -> int:
        return self._col_span

    @property
    def row_span(self) -> int:
        return self._row_span

    def _init_ui(self):
        """Initialize UI"""
        # Calculate total size based on span
        total_width = (self.CELL_WIDTH * self._col_span) + (self.SPACING * (self._col_span - 1))
        total_height = (self.CELL_HEIGHT * self._row_span) + (self.SPACING * (self._row_span - 1))

        self.setFixedSize(total_width, total_height)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        # Image label
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Scale image to fit
        scaled_pixmap = self._pixmap.scaled(
            total_width - 8,  # Subtract margins
            total_height - 8,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._image_label.setPixmap(scaled_pixmap)

        layout.addWidget(self._image_label)

        # Style
        self.setStyleSheet("""
            ImageCard {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            ImageCard:hover {
                border: 1px solid #2196F3;
            }
        """)

        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, position):
        """Show context menu with resize, relocate and delete options"""
        menu = QMenu(self)

        resize_action = menu.addAction("Resize")
        resize_action.triggered.connect(self._on_resize_clicked)

        # Relocate submenu
        relocate_menu = menu.addMenu("Relocate")
        for cat in self._categories:
            if cat.name != self._current_category and cat.name != "All":
                action = relocate_menu.addAction(f"{cat.icon} {cat.name}")
                action.triggered.connect(
                    lambda checked, c=cat.name: self._on_relocate(c)
                )

        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(self._on_delete_clicked)

        menu.exec(self.mapToGlobal(position))

    def _on_relocate(self, new_category: str):
        """Handle relocate action"""
        self.relocateRequested.emit(self._image_id, new_category)

    def _on_resize_clicked(self):
        """Toggle resize mode"""
        if self.is_resize_enabled():
            self.disable_resize_mode()
        else:
            self.enable_resize_mode()

    def _on_delete_clicked(self):
        """Handle delete action"""
        self.deleteRequested.emit(self._image_id)
        if self._on_delete:
            self._on_delete(self._image_id)

    def paintEvent(self, event):
        """Override to draw resize overlay"""
        super().paintEvent(event)
        if self._resize_enabled:
            painter = QPainter(self)
            self.paint_resize_overlay(painter)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if self.handle_resize_mouse_press(event):
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        if self.handle_resize_mouse_move(event):
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if self.handle_resize_mouse_release(event):
            return
        super().mouseReleaseEvent(event)

    def set_span(self, col_span: int, row_span: int):
        """Set new span and update size"""
        self._col_span = col_span
        self._row_span = row_span

        # Recalculate size
        total_width = (self.CELL_WIDTH * col_span) + (self.SPACING * (col_span - 1))
        total_height = (self.CELL_HEIGHT * row_span) + (self.SPACING * (row_span - 1))
        self.setFixedSize(total_width, total_height)

        # Re-scale image
        scaled_pixmap = self._pixmap.scaled(
            total_width - 8,
            total_height - 8,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._image_label.setPixmap(scaled_pixmap)
        self.update()
