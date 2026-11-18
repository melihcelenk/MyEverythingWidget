"""
TabManager - Manages QTabWidget for category tabs.

Single Responsibility: Create tabs, handle tab events.
Does NOT handle grid population or note actions.
"""
import logging
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTabWidget, QTabBar, QWidget, QMenu

from widgets.draggable_tab_bar import DraggableTabBar
from widgets.styled_tab_widget import StyledTabWidget

if TYPE_CHECKING:
    from window.app_state import AppState


class TabManager:
    """Manages the main tab widget for category tabs."""

    _logger = logging.getLogger(__name__)

    # Additional stylesheet for '+' tab (appended to base style)
    PLUS_TAB_STYLE = """
        QTabBar::tab:last {
            max-width: 30px;
            padding: 6px 6px;
        }
    """

    def __init__(self, app_state: 'AppState'):
        self._app_state = app_state
        self._tab_widget: StyledTabWidget = None
        self._category_pages: dict = {}  # category_id -> CategoryPage

        # Callbacks
        self.on_add_category: Callable = None
        self.on_edit_category: Callable = None
        self.on_delete_category: Callable = None

    def create_widget(self) -> QTabWidget:
        """Create and configure the tab widget."""
        self._tab_widget = StyledTabWidget(compact=False)

        # Replace tab bar with draggable version
        tab_bar = DraggableTabBar()
        self._tab_widget.setTabBar(tab_bar)
        tab_bar.setExpanding(False)

        # Add '+' tab specific styling
        current_style = self._tab_widget.styleSheet()
        self._tab_widget.setStyleSheet(current_style + self.PLUS_TAB_STYLE)

        # Connect signals
        tab_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self._on_context_menu)
        tab_bar.tabBarClicked.connect(self._on_tab_clicked)

        return self._tab_widget

    @property
    def widget(self) -> QTabWidget:
        return self._tab_widget

    @property
    def current_index(self) -> int:
        return self._tab_widget.currentIndex()

    def add_category_tab(self, category, page_widget: QWidget):
        """Add a tab for a category."""
        display_name = self._truncate_name(category.name)
        self._tab_widget.addTab(page_widget, f"{category.icon} {display_name}")
        self._category_pages[category.id] = page_widget

    def add_plus_tab(self):
        """Add the '+' tab for adding new categories."""
        add_widget = QWidget()
        add_widget.setFixedHeight(0)
        self._tab_widget.addTab(add_widget, "+")

        tab_bar = self._tab_widget.tabBar()
        add_index = self._tab_widget.count() - 1
        tab_bar.setTabButton(add_index, QTabBar.ButtonPosition.LeftSide, None)
        tab_bar.setTabButton(add_index, QTabBar.ButtonPosition.RightSide, None)

    def clear_tabs(self):
        """Remove all tabs."""
        while self._tab_widget.count() > 0:
            self._tab_widget.removeTab(0)
        self._category_pages.clear()

    def get_page(self, category_id: str):
        """Get the page widget for a category."""
        return self._category_pages.get(category_id)

    def select_tab(self, index: int):
        """Select a tab by index."""
        self._tab_widget.setCurrentIndex(index)

    def _truncate_name(self, name: str, max_length: int = 10) -> str:
        return name[:max_length] + "..." if len(name) > max_length else name

    def _on_tab_clicked(self, index: int):
        """Handle tab click - check if '+' tab clicked."""
        if index == self._tab_widget.count() - 1:
            previous = max(0, self.current_index - 1) if self.current_index == index else self.current_index

            if self.on_add_category:
                self.on_add_category()

            if self.current_index == index:
                self.select_tab(previous)

    def _on_context_menu(self, position):
        """Show context menu for tab."""
        tab_bar = self._tab_widget.tabBar()
        index = tab_bar.tabAt(position)

        # Skip '+' tab and invalid indices
        if index == self._tab_widget.count() - 1 or index < 0:
            return

        if index >= len(self._app_state.categories):
            return

        category = self._app_state.categories[index]

        menu = QMenu()
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")

        action = menu.exec(tab_bar.mapToGlobal(position))

        if action == rename_action and self.on_edit_category:
            self.on_edit_category(category)
        elif action == delete_action and self.on_delete_category:
            self.on_delete_category(category)
