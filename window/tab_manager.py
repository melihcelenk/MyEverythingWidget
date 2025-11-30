"""
TabManager - Backward compatibility wrapper.

This module re-exports ContentManager as TabManager for backward compatibility.
New code should use window.content_manager.ContentManager directly.
"""
from window.content_manager import ContentManager


class TabManager(ContentManager):
    """Backward-compatible TabManager that wraps ContentManager."""

    def __init__(self, app_state, on_app_tap, on_app_edit, on_app_rename,
                 on_app_change_icon, on_app_delete, on_add_category,
                 on_edit_category, on_delete_category):
        super().__init__(app_state)

        # Set app callbacks
        self.set_app_callbacks(
            on_tap=on_app_tap,
            on_edit=on_app_edit,
            on_rename=on_app_rename,
            on_change_icon=on_app_change_icon,
            on_delete=on_app_delete
        )

        # Set category callbacks
        self.set_category_callbacks(
            on_add=on_add_category,
            on_edit=on_edit_category,
            on_delete=on_delete_category
        )

    def create_tab_widget(self):
        """Create the tab widget - delegates to parent."""
        return super().create_tab_widget()

    def refresh_notes_tab(self):
        """Refresh current tab - delegates to parent."""
        return super().refresh_current_tab()

    def refresh_all_tabs(self):
        """Refresh all tabs - delegates to parent."""
        return super().refresh_all_tabs()

    @property
    def _category_grids(self):
        """Backward compatibility: return dict of category_id -> grid_layout."""
        grids = {}
        for category in self._app_state.categories:
            page = self._tab_manager.get_page(category.id)
            if page and hasattr(page, 'grid_layout'):
                grids[category.id] = page.grid_layout
        return grids
