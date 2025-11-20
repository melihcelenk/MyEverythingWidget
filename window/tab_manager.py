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
from widgets.draggable_tab_bar import DraggableTabBar
from widgets.app_card import AppCard
from widgets.note_card import NoteCard
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
        self._notes_layout = None
        self._note_input = None
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

        self._refresh_notes_tab()
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

        note_tab = self._create_notes_tab()
        self._tab_widget.addTab(note_tab, "Notes")

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

        grid_layout = QGridLayout(content_widget)
        grid_layout.setSpacing(4)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

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
            layout.addWidget(app_card, row, col,
                           alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _create_notes_tab(self):
        """Create the notes tab content."""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(4)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 8, 8, 8)
        header_layout.setSpacing(4)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Add quick note...")
        add_button = QPushButton("Add Note")
        add_button.clicked.connect(self._on_add_note_clicked)

        header_layout.addWidget(line_edit)
        header_layout.addWidget(add_button)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        scroll_area.setWidget(content)

        container_layout.addWidget(header)
        container_layout.addWidget(scroll_area)

        self._note_input = line_edit
        self._notes_layout = layout

        self._refresh_notes_tab()
        return container

    def _refresh_notes_tab(self):
        """Rebuild note cards inside the notes tab."""
        if not self._notes_layout:
            return

        while self._notes_layout.count():
            item = self._notes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        notes = self._app_state.notes
        if not notes:
            placeholder = QLabel("No notes yet")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._notes_layout.addWidget(placeholder)
        else:
            for note in notes:
                card = NoteCard(note)
                card.copyRequested.connect(lambda note_id: None)
                card.deleteRequested.connect(self._app_state.remove_note)
                self._notes_layout.addWidget(card)

        self._notes_layout.addStretch(1)

    def refresh_notes_tab(self):
        """Expose note refresh for external callers."""
        self._refresh_notes_tab()

    def _on_add_note_clicked(self):
        """Handle new note submission from the notes tab."""
        if not self._note_input:
            return

        content = self._note_input.text().strip()
        if not content:
            return

        category = (
            self._app_state.selected_category.name
            if self._app_state.selected_category
            else "All"
        )
        note = Note(
            id=str(uuid.uuid4()),
            content=content,
            type=NoteType.TEXT,
            category=category,
        )
        self._app_state.add_note(note)
        self._note_input.clear()

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
