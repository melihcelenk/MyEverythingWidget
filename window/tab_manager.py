"""
Tab management for main window
Handles tab creation, updates, and context menu
"""
import logging
import uuid

from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import (
    QTabWidget, QTabBar, QGridLayout, QWidget, QMenu,
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
)

from services.image_cache_service import ImageCacheService
from widgets.app_card import AppCard
from widgets.draggable_tab_bar import DraggableTabBar
from widgets.grid_drop_zone import GridDropZone
from widgets.image_card import ImageCard
from widgets.note_card import NoteCard
from window.models.note import Note, NoteType


class TabManager:
    """Manages tab widget and category tabs"""

    _logger = logging.getLogger(__name__)

    TAB_STYLESHEET = """
        QTabWidget::pane {
            border: 1px solid #ddd;
            border-top: none;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #f5f5f5;
            color: #666;
            border: 1px solid #ddd;
            border-bottom: none;
            padding: 6px 8px;
            margin-right: 1px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            max-width: 70px;
        }
        QTabBar::tab:hover {
            background-color: #e8e8e8;
            color: #333;
        }
        QTabBar::tab:selected {
            background-color: white;
            color: #2196F3;
            border-bottom: 2px solid #2196F3;
            font-weight: bold;
        }
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        QTabBar::tab:last {
            max-width: 30px;
            padding: 6px 6px;
        }
    """

    def __init__(self, app_state, on_app_tap, on_app_edit, on_app_rename,
                 on_app_change_icon, on_app_delete, on_add_category,
                 on_edit_category, on_delete_category):
        self._app_state = app_state
        self._on_app_tap = on_app_tap
        self._on_app_edit = on_app_edit
        self._on_app_rename = on_app_rename
        self._on_app_change_icon = on_app_change_icon
        self._on_app_delete = on_app_delete
        self._on_add_category = on_add_category
        self._on_edit_category = on_edit_category
        self._on_delete_category = on_delete_category

        self._category_tabs = {}
        self._category_grids = {}
        self._category_scroll_areas = {}  # Store scroll areas for each category
        self._category_drop_zones = {}  # Store GridDropZone widgets for each category
        self._note_inputs = {}
        self._tab_widget = None
        self._image_cache = ImageCacheService()
        self._dirty_tabs = set()  # Tabs that need refresh when activated

    # Grid utility methods for Android-like grid positioning

    def _pos_to_grid_cell(self, pos: QPoint, grid_layout: QGridLayout) -> tuple[int, int] | None:
        """Convert mouse position to grid cell coordinates.

        Args:
            pos: Mouse position in grid widget coordinates
            grid_layout: The QGridLayout to calculate cells for

        Returns:
            (row, col) tuple or None if position is outside grid
        """
        if grid_layout.count() == 0:
            return (0, 0)

        # Get grid geometry info (must match GridDropZone constants)
        CELL_WIDTH = GridDropZone.CELL_WIDTH + GridDropZone.SPACING
        CELL_HEIGHT = GridDropZone.CELL_HEIGHT + GridDropZone.SPACING

        col = pos.x() // CELL_WIDTH
        row = pos.y() // CELL_HEIGHT

        # Clamp to valid range
        col = max(0, min(col, GridDropZone.GRID_COLS - 1))
        row = max(0, min(row, GridDropZone.GRID_ROWS - 1))

        return (row, col)

    def _get_occupied_cells(self, category_name: str) -> set[tuple[int, int]]:
        """Get set of occupied grid cells for a category.

        Args:
            category_name: Name of the category to check

        Returns:
            Set of (row, col) tuples representing occupied cells
        """
        occupied = set()

        # Check apps with explicit grid positions
        for app in self._app_state.apps:
            if app.category != category_name:
                continue
            if app.grid_row is not None and app.grid_col is not None:
                # Mark all cells occupied by this app (accounting for span)
                for r in range(app.grid_row, app.grid_row + app.row_span):
                    for c in range(app.grid_col, app.grid_col + app.col_span):
                        occupied.add((r, c))

        # Check notes with explicit grid positions
        for note in self._app_state.notes:
            if note.category != category_name:
                continue
            if note.grid_row is not None and note.grid_col is not None:
                # Mark all cells occupied by this note (accounting for span)
                col_span = getattr(note, 'col_span', 1) or 1
                row_span = getattr(note, 'row_span', 1) or 1
                for r in range(note.grid_row, note.grid_row + row_span):
                    for c in range(note.grid_col, note.grid_col + col_span):
                        occupied.add((r, c))

        return occupied

    def _get_cells_for_item(self, item) -> set[tuple[int, int]]:
        """Get all grid cells occupied by an item.

        Args:
            item: AppShortcut or Note instance

        Returns:
            Set of (row, col) tuples occupied by this item
        """
        cells = set()

        # Check if item has grid position
        if not hasattr(item, 'grid_row') or item.grid_row is None:
            return cells
        if not hasattr(item, 'grid_col') or item.grid_col is None:
            return cells

        row = item.grid_row
        col = item.grid_col

        # Get span (default to 1x1 if not present)
        row_span = getattr(item, 'row_span', 1)
        col_span = getattr(item, 'col_span', 1)

        # Mark all cells occupied by this item
        for r in range(row, row + row_span):
            for c in range(col, col + col_span):
                cells.add((r, c))

        return cells

    def _find_first_available_cell(self, occupied: set[tuple[int, int]],
                                   row_span: int = 1, col_span: int = 1) -> tuple[int, int] | None:
        """Find the first available grid cell that can fit an item.

        Fixed 3x5 grid - returns None if no space available.

        Args:
            occupied: Set of already occupied (row, col) cells
            row_span: Number of rows the item needs
            col_span: Number of columns the item needs

        Returns:
            (row, col) tuple for the first available position, or None if grid is full
        """
        for row in range(GridDropZone.GRID_ROWS):
            for col in range(GridDropZone.GRID_COLS):
                # Check if item would overflow grid bounds
                if col + col_span > GridDropZone.GRID_COLS:
                    continue
                if row + row_span > GridDropZone.GRID_ROWS:
                    continue

                # Check if all required cells are free
                can_fit = True
                for r in range(row, row + row_span):
                    for c in range(col, col + col_span):
                        if (r, c) in occupied:
                            can_fit = False
                            break
                    if not can_fit:
                        break

                if can_fit:
                    return (row, col)

        return None  # Grid is full

    def create_tab_widget(self) -> QTabWidget:
        """Create and configure tab widget"""
        self._tab_widget = QTabWidget()
        self._tab_widget.setTabsClosable(False)

        # Use custom draggable tab bar
        custom_tab_bar = DraggableTabBar()
        self._tab_widget.setTabBar(custom_tab_bar)
        custom_tab_bar.setExpanding(False)

        self._tab_widget.setStyleSheet(self.TAB_STYLESHEET)

        # Connect tab bar signals
        tab_bar = self._tab_widget.tabBar()
        tab_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self._on_context_menu)
        tab_bar.tabBarClicked.connect(self._on_tab_clicked)
        self._tab_widget.currentChanged.connect(self._on_tab_changed)

        # Create initial tabs
        self.update_tabs()
        self._tab_widget.setCurrentIndex(0)

        return self._tab_widget

    @property
    def tab_widget(self) -> QTabWidget:
        return self._tab_widget

    def update_tabs(self):
        """Update tabs based on current categories"""
        # Clear existing tabs
        while self._tab_widget.count() > 0:
            self._tab_widget.removeTab(0)

        self._category_tabs = {}
        self._category_grids = {}

        # Add category tabs
        for category in self._app_state.categories:
            tab_content, grid_layout = self._create_category_tab(category)
            display_name = self._truncate_name(category.name)
            self._tab_widget.addTab(tab_content, f"{category.icon} {display_name}")
            self._category_tabs[category.id] = tab_content
            self._category_grids[category.id] = grid_layout
            self._category_scroll_areas[category.id] = tab_content  # tab_content is scroll_area

        add_tab_widget = QWidget()
        add_tab_widget.setFixedHeight(0)
        self._tab_widget.addTab(add_tab_widget, "+")

        # Remove close buttons from add tab
        tab_bar = self._tab_widget.tabBar()
        add_tab_index = self._tab_widget.count() - 1
        tab_bar.setTabButton(add_tab_index, QTabBar.ButtonPosition.LeftSide, None)
        tab_bar.setTabButton(add_tab_index, QTabBar.ButtonPosition.RightSide, None)

    def _truncate_name(self, name: str, max_length: int = 10) -> str:
        """Truncate name with ellipsis if too long"""
        return name[:max_length] + "..." if len(name) > max_length else name

    def _create_category_tab(self, category):
        """Create a tab content widget for a category

        Uses fixed 3x5 grid (Android-like) with no scrolling.
        """
        # Main container (no scroll)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Quick note entry at top
        content_layout.addWidget(self._create_note_entry(category))

        # GridDropZone is the fixed 3x5 grid container
        grid_container = GridDropZone()
        grid_container.gridDropped.connect(self._on_grid_drop)

        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(GridDropZone.SPACING)
        grid_layout.setContentsMargins(
            GridDropZone.MARGIN_LEFT,
            GridDropZone.MARGIN_TOP,
            GridDropZone.MARGIN_RIGHT,
            GridDropZone.MARGIN_BOTTOM
        )

        # Set fixed column widths (3 columns)
        for i in range(GridDropZone.GRID_COLS):
            grid_layout.setColumnMinimumWidth(i, GridDropZone.CELL_WIDTH)
            grid_layout.setColumnStretch(i, 0)

        # Set fixed row heights (5 rows)
        for i in range(GridDropZone.GRID_ROWS):
            grid_layout.setRowMinimumHeight(i, GridDropZone.CELL_HEIGHT)
            grid_layout.setRowStretch(i, 0)

        # Store references
        self._category_drop_zones[category.id] = grid_container
        self._category_scroll_areas[category.id] = content_widget  # For compatibility

        content_layout.addWidget(grid_container)
        content_layout.addStretch()  # Push grid to top

        self._populate_category_grid(category, grid_layout)

        return content_widget, grid_layout

    def _populate_category_grid(self, category, layout):
        """Populate category grid with app cards respecting explicit grid positions"""
        # Clear existing widgets - use setParent(None) for immediate cleanup
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                widget = child.widget()
                widget.setParent(None)
                widget.deleteLater()

        # Filter apps by category
        apps = [app for app in self._app_state.apps if app.category == category.name]

        # Track occupied cells
        occupied = set()

        # First, place apps with explicit grid positions
        apps_with_grid = [a for a in apps if a.grid_row is not None and a.grid_col is not None]
        apps_without_grid = [a for a in apps if a.grid_row is None or a.grid_col is None]

        for app in apps_with_grid:
            app_card = AppCard(
                app=app,
                on_tap=lambda a=app: self._on_app_tap(a),
                on_edit=lambda a=app: self._on_app_edit(a),
                on_rename=lambda a=app: self._on_app_rename(a),
                on_change_icon=lambda a=app: self._on_app_change_icon(a),
                on_delete=lambda a=app: self._on_app_delete(a),
            )
            # Disable drop acceptance - only GridDropZone handles drops now
            app_card.setAcceptDrops(False)

            # Use explicit grid position
            layout.addWidget(
                app_card,
                app.grid_row,
                app.grid_col,
                app.row_span,
                app.col_span
            )

            # Mark cells as occupied
            for r in range(app.grid_row, app.grid_row + app.row_span):
                for c in range(app.grid_col, app.grid_col + app.col_span):
                    occupied.add((r, c))

        # Auto-place apps without explicit grid positions (for backward compat)
        for app in sorted(apps_without_grid, key=lambda a: a.order):
            # Find first available cell
            cell = self._find_first_available_cell(occupied, app.row_span, app.col_span)
            if cell is None:
                self._logger.warning("Grid full, cannot place app: %s", app.name)
                continue

            row, col = cell

            # IMPORTANT: Assign grid position NOW so it persists
            app.grid_row = row
            app.grid_col = col

            app_card = AppCard(
                app=app,
                on_tap=lambda a=app: self._on_app_tap(a),
                on_edit=lambda a=app: self._on_app_edit(a),
                on_rename=lambda a=app: self._on_app_rename(a),
                on_change_icon=lambda a=app: self._on_app_change_icon(a),
                on_delete=lambda a=app: self._on_app_delete(a),
            )
            # Disable drop acceptance - only GridDropZone handles drops now
            app_card.setAcceptDrops(False)
            layout.addWidget(app_card, row, col, app.row_span, app.col_span)

            # Mark cells as occupied
            for r in range(row, row + app.row_span):
                for c in range(col, col + app.col_span):
                    occupied.add((r, c))

        # Save state if we assigned any grid positions
        if apps_without_grid:
            self._app_state.state_changed.emit()

        self._add_note_cards_to_layout(category, layout, occupied)

    def _create_note_entry(self, category):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Add a quick note...")
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self._on_add_note_clicked(category.id))

        layout.addWidget(line_edit)
        layout.addWidget(add_button)

        self._note_inputs[category.id] = line_edit
        return container

    def _on_add_note_clicked(self, category_id: str):
        line_edit = self._note_inputs.get(category_id)
        if line_edit is None:
            return

        content = line_edit.text().strip()
        if not content:
            return

        category = next(
            (cat for cat in self._app_state.categories if cat.id == category_id),
            self._app_state.categories[0] if self._app_state.categories else None,
        )
        category_name = category.name if category else "All"

        note = Note(
            id=str(uuid.uuid4()),
            content=content,
            type=NoteType.TEXT,
            category=category_name,
        )
        self._app_state.add_note(note)
        line_edit.clear()

    def _add_note_cards_to_layout(self, category, layout, occupied: set):
        """Add note cards to layout, respecting explicit grid positions.

        Uses Note's col_span/row_span values from the model.
        Auto-places notes without positions and saves their positions.

        Args:
            category: Category object
            layout: QGridLayout to add cards to
            occupied: Set of already occupied (row, col) cells
        """
        from dataclasses import replace

        notes = [note for note in self._app_state.notes if note.category == category.name]

        if not notes:
            return

        # Separate notes with/without explicit grid positions
        notes_with_grid = [n for n in notes if n.grid_row is not None and n.grid_col is not None]
        notes_without_grid = [n for n in notes if n.grid_row is None or n.grid_col is None]

        notes_to_update = []  # Collect notes that need position updates

        # First, place notes with explicit grid positions
        for note in notes_with_grid:
            col_span = note.col_span
            row_span = note.row_span

            if note.type == NoteType.IMAGE:
                pixmap = self._image_cache.get(note.content)
                if pixmap is not None:
                    card = ImageCard(
                        image_id=note.id,
                        pixmap=pixmap,
                        on_delete=self._app_state.remove_note
                    )
                    card.set_categories(self._app_state.categories, category.name)
                    card.resizeRequested.connect(lambda c_span, r_span, c=card: self._on_resize_card(c, c_span, r_span))
                    card.relocateRequested.connect(self._on_relocate_note)
                    card.setAcceptDrops(False)

                    # Use image card's calculated span (based on aspect ratio)
                    col_span = card.col_span
                    row_span = card.row_span

                    layout.addWidget(card, note.grid_row, note.grid_col, row_span, col_span)

                    # Mark cells as occupied
                    for r in range(note.grid_row, note.grid_row + row_span):
                        for c in range(note.grid_col, note.grid_col + col_span):
                            occupied.add((r, c))
            else:
                # Text note - use span from model
                card = NoteCard(note, col_span=col_span, row_span=row_span)
                card.set_categories(self._app_state.categories)
                card.copyRequested.connect(lambda note_id: None)
                card.deleteRequested.connect(self._app_state.remove_note)
                card.editRequested.connect(self._on_edit_note)
                card.resizeRequested.connect(lambda c_span, r_span, c=card: self._on_resize_card(c, c_span, r_span))
                card.relocateRequested.connect(self._on_relocate_note)
                card.setAcceptDrops(False)

                layout.addWidget(card, note.grid_row, note.grid_col, row_span, col_span)

                # Mark cells as occupied
                for r in range(note.grid_row, note.grid_row + row_span):
                    for c in range(note.grid_col, note.grid_col + col_span):
                        occupied.add((r, c))

        # Auto-place notes without explicit grid positions
        for note in sorted(notes_without_grid, key=lambda n: n.order):
            col_span = note.col_span
            row_span = note.row_span

            # Default span for new text notes
            if note.type == NoteType.TEXT and col_span == 1:
                col_span = 2  # Default text notes to 2 columns wide

            if note.type == NoteType.IMAGE:
                pixmap = self._image_cache.get(note.content)
                if pixmap is not None:
                    card = ImageCard(
                        image_id=note.id,
                        pixmap=pixmap,
                        on_delete=self._app_state.remove_note
                    )
                    card.set_categories(self._app_state.categories, category.name)
                    card.resizeRequested.connect(lambda c_span, r_span, c=card: self._on_resize_card(c, c_span, r_span))
                    card.relocateRequested.connect(self._on_relocate_note)
                    card.setAcceptDrops(False)

                    # Use image card's calculated span
                    col_span = card.col_span
                    row_span = card.row_span

                    # Find first available cell
                    cell = self._find_first_available_cell(occupied, row_span, col_span)
                    if cell is None:
                        self._logger.warning("Grid full, cannot place image note")
                        continue

                    row, col = cell

                    # Save grid position to note
                    updated_note = replace(note, grid_row=row, grid_col=col,
                                           col_span=col_span, row_span=row_span)
                    notes_to_update.append(updated_note)

                    # Mark cells as occupied
                    for r in range(row, row + row_span):
                        for c in range(col, col + col_span):
                            occupied.add((r, c))

                    layout.addWidget(card, row, col, row_span, col_span)
                    continue

            # Text note
            cell = self._find_first_available_cell(occupied, row_span, col_span)
            if cell is None:
                self._logger.warning("Grid full, cannot place text note")
                continue

            row, col = cell

            # Save grid position to note
            updated_note = replace(note, grid_row=row, grid_col=col,
                                   col_span=col_span, row_span=row_span)
            notes_to_update.append(updated_note)

            card = NoteCard(updated_note, col_span=col_span, row_span=row_span)
            card.set_categories(self._app_state.categories)
            card.copyRequested.connect(lambda note_id: None)
            card.deleteRequested.connect(self._app_state.remove_note)
            card.editRequested.connect(self._on_edit_note)
            card.resizeRequested.connect(lambda c_span, r_span, c=card: self._on_resize_card(c, c_span, r_span))
            card.relocateRequested.connect(self._on_relocate_note)
            card.itemDropped.connect(self._on_item_dropped)
            layout.addWidget(card, row, col, row_span, col_span)

            # Mark cells as occupied
            for r in range(row, row + row_span):
                for c in range(col, col + col_span):
                    occupied.add((r, c))

        # Batch update notes with new grid positions
        if notes_to_update:
            self._app_state.blockSignals(True)
            try:
                for note in notes_to_update:
                    self._app_state.update_note(note)
            finally:
                self._app_state.blockSignals(False)
            self._app_state.state_changed.emit()

    def _on_edit_note(self, note_id: str):
        """Handle edit note request"""
        note = next((n for n in self._app_state.notes if n.id == note_id), None)
        if note is None:
            return
        # TODO: Implement note editing dialog
        self._logger.debug("Edit note requested: %s", note_id)

    def _on_relocate_note(self, note_id: str, new_category: str):
        """Handle note relocation to a new category"""
        from dataclasses import replace
        note = next((n for n in self._app_state.notes if n.id == note_id), None)
        if note is None:
            return
        updated_note = replace(note, category=new_category)
        self._app_state.update_note(updated_note)
        self.refresh_all_tabs()

    def _on_grid_drop(self, item_id: str, target_row: int, target_col: int):
        """Handle grid-based drop (Android-like behavior).

        Rules:
        1. Fixed 3x5 grid - no overflow allowed
        2. If target is empty, move item there
        3. If target is occupied by ONE item that fits in source, swap
        4. If swap not possible, reject the drop (no displacement)

        Args:
            item_id: ID of the item being dragged
            target_row: Target grid row
            target_col: Target grid column
        """

        self._logger.info(
            "Grid drop: item=%s to row=%d col=%d",
            item_id, target_row, target_col
        )

        # Find the dragged item (app or note)
        dragged_app = next((a for a in self._app_state.apps if a.id == item_id), None)
        dragged_note = None if dragged_app else next(
            (n for n in self._app_state.notes if n.id == item_id), None
        )

        if dragged_app is None and dragged_note is None:
            self._logger.warning("Dropped item not found: %s", item_id)
            return

        dragged_item = dragged_app or dragged_note
        category_name = dragged_item.category

        # Get span of dragged item
        row_span = getattr(dragged_item, 'row_span', 1)
        col_span = getattr(dragged_item, 'col_span', 1)

        # Check grid bounds (3x5 fixed grid)
        if target_col + col_span > GridDropZone.GRID_COLS:
            self._logger.warning("Drop would overflow grid columns")
            return
        if target_row + row_span > GridDropZone.GRID_ROWS:
            self._logger.warning("Drop would overflow grid rows")
            return

        # Calculate target cells
        target_cells = set()
        for r in range(target_row, target_row + row_span):
            for c in range(target_col, target_col + col_span):
                target_cells.add((r, c))

        # Get source cells (dragged item's current position)
        source_cells = self._get_cells_for_item(dragged_item)
        source_row = dragged_item.grid_row
        source_col = dragged_item.grid_col

        # Get all occupied cells except the dragged item
        occupied = self._get_occupied_cells(category_name) - source_cells

        # Check for collision
        collision_cells = target_cells & occupied

        if not collision_cells:
            # No collision - just move the item
            self._logger.info("No collision, moving item")
            self._move_item(dragged_item, target_row, target_col)
            self._quick_refresh_current_tab()
            return

        # Collision detected - find the colliding item
        colliding_item = self._find_item_at_cells(category_name, collision_cells, item_id)

        if colliding_item is None:
            self._logger.warning("Collision detected but no item found")
            return

        # Check if swap is possible
        # Swap is possible if:
        # 1. There's exactly one colliding item
        # 2. The colliding item can fit in the source position

        colliding_span_row = getattr(colliding_item, 'row_span', 1)
        colliding_span_col = getattr(colliding_item, 'col_span', 1)

        # Check if colliding item fits at source position
        if source_row is not None and source_col is not None:
            if (source_col + colliding_span_col <= GridDropZone.GRID_COLS and
                    source_row + colliding_span_row <= GridDropZone.GRID_ROWS):
                # Swap is possible
                self._logger.info("Swapping items")
                self._move_item(dragged_item, target_row, target_col)
                self._move_item(colliding_item, source_row, source_col)
                self._quick_refresh_current_tab()
                return

        # Swap not possible - reject the drop
        self._logger.warning("Cannot swap - colliding item doesn't fit at source")

    def _move_item(self, item, row: int, col: int):
        """Move an item to a new grid position."""
        from dataclasses import replace

        if hasattr(item, 'name'):  # AppShortcut (has 'name' attribute)
            item.grid_row = row
            item.grid_col = col
            self._app_state.state_changed.emit()
        else:  # Note
            updated = replace(item, grid_row=row, grid_col=col)
            self._app_state.update_note(updated)

    def _find_item_at_cells(self, category: str, cells: set, exclude_id: str = None):
        """Find the item occupying any of the given cells."""
        for app in self._app_state.apps:
            if app.category != category or app.id == exclude_id:
                continue
            app_cells = self._get_cells_for_item(app)
            if app_cells & cells:
                return app

        for note in self._app_state.notes:
            if note.category != category or note.id == exclude_id:
                continue
            note_cells = self._get_cells_for_item(note)
            if note_cells & cells:
                return note

        return None

    def _on_item_dropped(self, item_id: str, target_item_id: str):
        """Handle item drop for reordering

        Args:
            item_id: ID of the item being dragged
            target_item_id: ID of the item that was dropped onto
        """
        self._logger.info("Item dropped: id=%s onto target=%s", item_id, target_item_id)

        # Find the dragged item
        app = next((a for a in self._app_state.apps if a.id == item_id), None)
        if app:
            target_app = next((a for a in self._app_state.apps if a.id == target_item_id), None)
            if target_app:
                self._reorder_app(app, target_app)
            return

        note = next((n for n in self._app_state.notes if n.id == item_id), None)
        if note:
            target_note = next((n for n in self._app_state.notes if n.id == target_item_id), None)
            if target_note:
                self._reorder_note(note, target_note)
            return

    def _reorder_app(self, app, target_app):
        """Swap app positions using grid coordinates (Android-like behavior)

        Swaps both grid positions AND order values for backward compatibility.
        """
        if app.id == target_app.id:
            return

        # Store target's position and order
        target_row = target_app.grid_row
        target_col = target_app.grid_col
        target_order = target_app.order

        # Store source's position and order
        source_row = app.grid_row
        source_col = app.grid_col
        source_order = app.order

        # Swap positions AND orders
        app.grid_row = target_row
        app.grid_col = target_col
        app.order = target_order

        target_app.grid_row = source_row
        target_app.grid_col = source_col
        target_app.order = source_order

        self._app_state.state_changed.emit()
        self._quick_refresh_current_tab()

    def _reorder_note(self, note, target_note):
        """Swap note positions using grid coordinates (Android-like behavior)

        Swaps both grid positions AND order values for backward compatibility.
        Handles cases where grid positions may be None (legacy notes).
        """
        from dataclasses import replace

        if note.id == target_note.id:
            return

        # Store target's position and order
        target_row = target_note.grid_row
        target_col = target_note.grid_col
        target_order = target_note.order
        target_col_span = target_note.col_span
        target_row_span = target_note.row_span

        # Store source's position and order
        source_row = note.grid_row
        source_col = note.grid_col
        source_order = note.order
        source_col_span = note.col_span
        source_row_span = note.row_span

        # Update both notes with swapped positions AND orders
        updated_note = replace(
            note,
            grid_row=target_row,
            grid_col=target_col,
            order=target_order
        )
        updated_target = replace(
            target_note,
            grid_row=source_row,
            grid_col=source_col,
            order=source_order
        )

        self._app_state.blockSignals(True)
        try:
            self._app_state.update_note(updated_note)
            self._app_state.update_note(updated_target)
        finally:
            self._app_state.blockSignals(False)

        self._app_state.state_changed.emit()
        self._quick_refresh_current_tab()

    def _on_resize_card(self, card, col_span: int, row_span: int):
        """Handle card resize request"""
        self._logger.debug("Resize card: col=%d, row=%d", col_span, row_span)

        # Update the card's size
        card.set_span(col_span, row_span)
        card.disable_resize_mode()

        # Refresh the grid to update layout
        # TODO: Update note/image span in app_state for persistence

    def _quick_refresh_current_tab(self):
        """Fast refresh - uses QTimer to batch updates and avoid blocking UI"""
        from PySide6.QtCore import QTimer
        # Schedule refresh on next event loop iteration
        QTimer.singleShot(0, self.refresh_notes_tab)

    def refresh_notes_tab(self):
        """Refresh note cards in active category tab only"""
        # Only refresh the currently active tab for performance
        current_index = self._tab_widget.currentIndex()
        if current_index < 0 or current_index >= len(self._app_state.categories):
            return

        category = self._app_state.categories[current_index]
        if category.id in self._category_grids:
            grid_layout = self._category_grids[category.id]
            self._populate_category_grid(category, grid_layout)

    def refresh_all_tabs(self):
        """Force refresh all category tabs"""
        for category in self._app_state.categories:
            if category.id in self._category_grids:
                grid_layout = self._category_grids[category.id]
                self._populate_category_grid(category, grid_layout)
        self._dirty_tabs = set()

    def _create_notes_tab(self):
        """Create the notes tab content."""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(4)
        return container

    def _on_tab_changed(self, index: int):
        """Handle tab change - no refresh needed, tabs are pre-populated"""
        # Tab content is already loaded, no need to refresh on switch
        pass

    def _on_tab_clicked(self, index: int):
        """Handle tab bar click"""
        self._logger.debug(
            "_on_tab_clicked: index=%d tab_count=%d",
            index,
            self._tab_widget.count(),
        )
        if index == self._tab_widget.count() - 1:
            previous_index = self._tab_widget.currentIndex()
            if previous_index == index:
                previous_index = max(0, index - 1)

            self._on_add_category()

            if self._tab_widget.currentIndex() == index:
                self._tab_widget.setCurrentIndex(previous_index)

    def _on_context_menu(self, position):
        """Show context menu for tab"""
        tab_bar = self._tab_widget.tabBar()
        index = tab_bar.tabAt(position)

        # Don't show for add button or invalid index
        if index == self._tab_widget.count() - 1 or index < 0:
            return

        if index >= len(self._app_state.categories):
            return

        category = self._app_state.categories[index]

        menu = QMenu()
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")

        action = menu.exec(tab_bar.mapToGlobal(position))

        if action == rename_action:
            self._on_edit_category(category)
        elif action == delete_action:
            self._on_delete_category(category)
