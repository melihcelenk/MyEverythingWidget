"""
ContentManager - Coordinates all content-related components.

This is the main entry point used by MainWindow.
Coordinates: TabManager, CategoryPages, GridPopulator, ItemMover, NoteActions.
"""
import logging
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QTabWidget

from window.grid import GridPopulator, ItemMover
from window.ui.notes import NoteActions
from window.ui.tabs import TabManager, CategoryPage

if TYPE_CHECKING:
    from window.app_state import AppState


class ContentManager:
    """Coordinates tab management, grid population, and item actions."""

    _logger = logging.getLogger(__name__)

    def __init__(self, app_state: 'AppState'):
        self._app_state = app_state

        # UI Components
        self._tab_manager = TabManager(app_state)
        self._note_actions = NoteActions(app_state)

        # Grid components
        self._populator = GridPopulator(app_state)
        self._mover = ItemMover(
            app_state,
            self._populator.get_occupied_cells,
            self._populator.get_cells_for_item
        )

        # Wire up callbacks
        self._note_actions.on_refresh = self._quick_refresh
        self._mover.on_refresh = self._quick_refresh

        # External callbacks (set by MainWindow)
        self._on_app_tap: Callable = None
        self._on_app_edit: Callable = None
        self._on_app_rename: Callable = None
        self._on_app_change_icon: Callable = None
        self._on_app_delete: Callable = None

    def set_app_callbacks(self, on_tap, on_edit, on_rename, on_change_icon, on_delete):
        """Set callbacks for app card actions."""
        self._on_app_tap = on_tap
        self._on_app_edit = on_edit
        self._on_app_rename = on_rename
        self._on_app_change_icon = on_change_icon
        self._on_app_delete = on_delete

        # Wire to populator
        self._populator.on_app_tap = on_tap
        self._populator.on_app_edit = on_edit
        self._populator.on_app_rename = on_rename
        self._populator.on_app_change_icon = on_change_icon
        self._populator.on_app_delete = on_delete

    def set_category_callbacks(self, on_add, on_edit, on_delete):
        """Set callbacks for category actions."""
        self._tab_manager.on_add_category = on_add
        self._tab_manager.on_edit_category = on_edit
        self._tab_manager.on_delete_category = on_delete

    def create_tab_widget(self) -> QTabWidget:
        """Create the main tab widget with all category tabs."""
        widget = self._tab_manager.create_widget()

        # Wire populator callbacks
        self._populator.on_edit_note = self._note_actions.edit_note
        self._populator.on_relocate_note = self._note_actions.relocate_note
        self._populator.on_resize_card = self._note_actions.resize_card

        self.update_tabs()
        self._tab_manager.select_tab(0)

        return widget

    @property
    def tab_widget(self) -> QTabWidget:
        return self._tab_manager.widget

    def update_tabs(self):
        """Rebuild all tabs from current categories."""
        self._tab_manager.clear_tabs()

        for category in self._app_state.categories:
            page = CategoryPage(category, self._app_state)
            page.set_populator(self._populator)
            page.connect_drop_handler(self._mover.handle_grid_drop)
            page.populate()

            self._tab_manager.add_category_tab(category, page)

        self._tab_manager.add_plus_tab()

    def refresh_current_tab(self):
        """Refresh the currently visible tab."""
        index = self._tab_manager.current_index
        if index < 0 or index >= len(self._app_state.categories):
            return

        category = self._app_state.categories[index]
        page = self._tab_manager.get_page(category.id)
        if page and hasattr(page, 'populate'):
            page.populate()

    def refresh_all_tabs(self):
        """Refresh all category tabs."""
        for category in self._app_state.categories:
            page = self._tab_manager.get_page(category.id)
            if page and hasattr(page, 'populate'):
                page.populate()

    def _quick_refresh(self):
        """Schedule refresh on next event loop iteration."""
        QTimer.singleShot(0, self.refresh_current_tab)

    # Backward compatibility methods (used by tests)
    def _reorder_note(self, note, target_note):
        """Swap note positions."""
        self._mover._swap_notes(note, target_note)

    def _reorder_app(self, app, target_app):
        """Swap app positions."""
        self._mover._swap_apps(app, target_app)
