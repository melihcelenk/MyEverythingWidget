"""
Tab management for main window
Handles tab creation, updates, and context menu
"""
import logging

from PySide6.QtWidgets import (
    QTabWidget, QTabBar, QScrollArea, QGridLayout, QWidget, QMenu,
    QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from widgets.draggable_tab_bar import DraggableTabBar
from widgets.app_card import AppCard
from widgets.note_card import NoteCard
from widgets.image_card import ImageCard
from window.models.note import Note, NoteType
import uuid


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
        self._note_inputs = {}
        self._tab_widget = None

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
        """Create a tab content widget for a category"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self._create_note_entry(category))

        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(4)
        grid_layout.setContentsMargins(8, 4, 8, 8)

        # Set fixed column widths to prevent stretching
        for i in range(3):
            grid_layout.setColumnMinimumWidth(i, 90)
            grid_layout.setColumnStretch(i, 0)

        content_layout.addWidget(grid_container)

        self._populate_category_grid(category, grid_layout)

        return scroll_area, grid_layout

    def _populate_category_grid(self, category, layout):
        """Populate category grid with app cards"""
        # Clear existing widgets
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Filter apps by category
        if category.name == 'All':
            apps = self._app_state.apps
        else:
            apps = [app for app in self._app_state.apps if app.category == category.name]

        # Add app cards in grid (3 columns)
        row = 0
        col = 0
        for app in apps:
            app_card = AppCard(
                app=app,
                on_tap=lambda a=app: self._on_app_tap(a),
                on_edit=lambda a=app: self._on_app_edit(a),
                on_rename=lambda a=app: self._on_app_rename(a),
                on_change_icon=lambda a=app: self._on_app_change_icon(a),
                on_delete=lambda a=app: self._on_app_delete(a),
            )
            layout.addWidget(app_card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        self._add_note_cards_to_layout(category, layout, row, col)

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

    def _add_note_cards_to_layout(self, category, layout, start_row, start_col):
        notes = (
            self._app_state.notes
            if category.name == 'All'
            else [note for note in self._app_state.notes if note.category == category.name]
        )

        if not notes:
            return

        # Start on new row after apps
        row = start_row + (1 if start_col > 0 else 0)
        col = 0

        # Track which cells are occupied (for multi-row spans)
        occupied = set()
        span_options = [2, 3]

        for idx, note in enumerate(notes):
            # Skip occupied cells
            while (row, col) in occupied:
                col += 1
                if col >= 3:
                    col = 0
                    row += 1

            # Check if this is an image note
            if note.type == NoteType.IMAGE:
                pixmap = QPixmap(note.content)
                if not pixmap.isNull():
                    card = ImageCard(
                        image_id=note.id,
                        pixmap=pixmap,
                        on_delete=self._app_state.remove_note
                    )
                    card.resizeRequested.connect(lambda c_span, r_span, c=card: self._on_resize_card(c, c_span, r_span))
                    col_span = card.col_span
                    row_span = card.row_span
                    self._logger.debug(
                        "Placing image: row=%d, col=%d, col_span=%d, row_span=%d",
                        row, col, col_span, row_span
                    )

                    # Check if fits in current row
                    if col + col_span > 3:
                        row += 1
                        col = 0
                        # Skip occupied cells again
                        while (row, col) in occupied:
                            col += 1
                            if col >= 3:
                                col = 0
                                row += 1

                    # Mark cells as occupied for multi-row spans
                    for r in range(row, row + row_span):
                        for c in range(col, col + col_span):
                            occupied.add((r, c))

                    layout.addWidget(card, row, col, row_span, col_span)
                    col += col_span
                    if col >= 3:
                        col = 0
                        row += row_span  # Move past all rows occupied by image
                    continue

            # Text note - use NoteCard
            preferred_span = span_options[idx % len(span_options)]

            # Find a position where the note fits without overflow
            while True:
                available = 3 - col

                if preferred_span <= available:
                    span = preferred_span
                    break
                elif available >= 2:
                    span = 2
                    break
                else:
                    # Not enough space, move to next row
                    row += 1
                    col = 0
                    # Skip occupied cells
                    while (row, col) in occupied:
                        col += 1
                        if col >= 3:
                            col = 0
                            row += 1

            self._logger.debug(
                "Placing note: row=%d, col=%d, span=%d, available=%d",
                row, col, span, available
            )
            card = NoteCard(note, col_span=span)
            card.copyRequested.connect(lambda note_id: None)
            card.deleteRequested.connect(self._app_state.remove_note)
            card.editRequested.connect(self._on_edit_note)
            card.resizeRequested.connect(lambda c_span, r_span, c=card: self._on_resize_card(c, c_span, r_span))
            layout.addWidget(card, row, col, 1, span)
            col += span
            if col >= 3:
                row += 1
                col = 0

    def _on_edit_note(self, note_id: str):
        """Handle edit note request"""
        note = next((n for n in self._app_state.notes if n.id == note_id), None)
        if note is None:
            return
        # TODO: Implement note editing dialog
        self._logger.debug("Edit note requested: %s", note_id)

    def _on_resize_card(self, card, col_span: int, row_span: int):
        """Handle card resize request"""
        self._logger.debug("Resize card: col=%d, row=%d", col_span, row_span)

        # Update the card's size
        card.set_span(col_span, row_span)
        card.disable_resize_mode()

        # Refresh the grid to update layout
        # TODO: Update note/image span in app_state for persistence

    def refresh_notes_tab(self):
        """Refresh note cards in all category tabs"""
        for category in self._app_state.categories:
            if category.id in self._category_grids:
                grid_layout = self._category_grids[category.id]
                self._populate_category_grid(category, grid_layout)

    def _create_notes_tab(self):
        """Create the notes tab content."""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(4)
        return container

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
        if category.name == 'All':
            return

        menu = QMenu()
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")

        action = menu.exec(tab_bar.mapToGlobal(position))

        if action == rename_action:
            self._on_edit_category(category)
        elif action == delete_action:
            self._on_delete_category(category)
