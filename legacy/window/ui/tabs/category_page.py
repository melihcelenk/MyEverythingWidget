"""
CategoryPage - Content widget for a category tab.

Single Responsibility: Create and manage category page content (grid + note entry).
"""
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout

from widgets.grid_drop_zone import GridDropZone
from window.grid import GRID_COLS, GRID_ROWS, CELL_WIDTH, CELL_HEIGHT, SPACING
from window.grid.populator import GridPopulator
from window.ui.notes.quick_entry import QuickNoteEntry

if TYPE_CHECKING:
    from window.app_state import AppState


class CategoryPage(QWidget):
    """Content widget for a category tab.
    
    Contains:
    - QuickNoteEntry at top
    - GridDropZone with cards
    """

    def __init__(self, category, app_state: 'AppState', parent=None):
        super().__init__(parent)
        self._category = category
        self._app_state = app_state

        self._populator: GridPopulator = None
        self._grid_layout: QGridLayout = None
        self._drop_zone: GridDropZone = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Quick note entry
        note_entry = QuickNoteEntry(self._category.name, self._app_state)
        layout.addWidget(note_entry)

        # Grid drop zone
        self._drop_zone = GridDropZone()

        self._grid_layout = QGridLayout(self._drop_zone)
        self._grid_layout.setSpacing(SPACING)
        self._grid_layout.setContentsMargins(
            GridDropZone.MARGIN_LEFT,
            GridDropZone.MARGIN_TOP,
            GridDropZone.MARGIN_RIGHT,
            GridDropZone.MARGIN_BOTTOM
        )

        for i in range(GRID_COLS):
            self._grid_layout.setColumnMinimumWidth(i, CELL_WIDTH)
            self._grid_layout.setColumnStretch(i, 0)

        for i in range(GRID_ROWS):
            self._grid_layout.setRowMinimumHeight(i, CELL_HEIGHT)
            self._grid_layout.setRowStretch(i, 0)

        # Left-align the drop zone (no centering)
        layout.addWidget(self._drop_zone, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addStretch()

    def set_populator(self, populator: GridPopulator):
        """Set the grid populator."""
        self._populator = populator

    def connect_drop_handler(self, handler: Callable):
        """Connect grid drop signal to handler."""
        self._drop_zone.gridDropped.connect(handler)

    def populate(self):
        """Populate the grid with cards."""
        if self._populator:
            self._populator.populate_grid(self._category, self._grid_layout)

    @property
    def grid_layout(self) -> QGridLayout:
        return self._grid_layout

    @property
    def drop_zone(self) -> GridDropZone:
        return self._drop_zone

    @property
    def category(self):
        return self._category
