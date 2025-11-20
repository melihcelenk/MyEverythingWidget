"""
Image card widget
Displays an image in the grid with delete option
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from services.image_grid_calculator import ImageGridCalculator


class ImageCard(QWidget):
    """Widget to display an image in the grid"""

    # Signals
    deleteRequested = Signal(str)

    # Base size for one grid cell
    CELL_WIDTH = 90
    CELL_HEIGHT = 100
    SPACING = 4

    def __init__(self, image_id: str, pixmap: QPixmap, on_delete=None, parent=None):
        super().__init__(parent)
        self._image_id = image_id
        self._pixmap = pixmap
        self._on_delete = on_delete

        # Calculate span based on aspect ratio
        calculator = ImageGridCalculator()
        self._col_span, self._row_span = calculator.calculate_span(
            pixmap.width(), pixmap.height()
        )

        self._init_ui()

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
        """Show context menu with delete option"""
        menu = QMenu(self)

        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(self._on_delete_clicked)

        menu.exec(self.mapToGlobal(position))

    def _on_delete_clicked(self):
        """Handle delete action"""
        self.deleteRequested.emit(self._image_id)
        if self._on_delete:
            self._on_delete(self._image_id)
