"""
Tests for tab display - text visibility, width, and scrolling
"""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from window.main_window import MainWindow
from window.app_state import AppState
from models.category import AppCategory
import uuid


class TestTabDisplay:
    """Test tab display properties"""

    @pytest.fixture
    def main_window(self, qtbot):
        """Create main window for testing"""
        window = MainWindow()
        qtbot.addWidget(window)
        return window

    def test_tab_text_not_elided_for_short_names(self, main_window):
        """Tab text should be fully visible for short category names"""
        tab_bar = main_window._tab_widget.tabBar()

        # Check "All" tab (index 0) - should show full text
        tab_text = tab_bar.tabText(0)
        assert "All" in tab_text, f"Tab text should contain 'All', got: {tab_text}"

        # Tab width should be enough to show the text
        tab_rect = tab_bar.tabRect(0)
        assert tab_rect.width() >= 50, f"Tab width should be >= 50px, got: {tab_rect.width()}"

    def test_tab_minimum_width(self, main_window):
        """Each tab should have minimum width for text visibility"""
        tab_bar = main_window._tab_widget.tabBar()

        # Check all category tabs (not the + button)
        for i in range(main_window._tab_widget.count() - 1):
            tab_rect = tab_bar.tabRect(i)
            # Minimum width should be at least 60px for text visibility
            assert tab_rect.width() >= 60, f"Tab {i} width should be >= 60px, got: {tab_rect.width()}"

    def test_tab_text_contains_category_name(self, main_window):
        """Tab text should contain the category name (or truncated version)"""
        tab_bar = main_window._tab_widget.tabBar()
        categories = main_window._app_state.categories

        for i, category in enumerate(categories):
            tab_text = tab_bar.tabText(i)
            # Tab text should contain the category name (or first 10 chars if truncated)
            expected_name = category.name[:10] if len(category.name) > 10 else category.name
            assert expected_name in tab_text, f"Tab {i} should contain '{expected_name}', got: '{tab_text}'"

    def test_add_button_tab_is_narrow(self, main_window):
        """The + button tab should be narrower than category tabs"""
        tab_bar = main_window._tab_widget.tabBar()

        # Get add button tab (last tab)
        add_tab_index = main_window._tab_widget.count() - 1
        add_tab_rect = tab_bar.tabRect(add_tab_index)

        # Get first category tab
        first_tab_rect = tab_bar.tabRect(0)

        # Add button should be narrower
        assert add_tab_rect.width() <= first_tab_rect.width(), \
            f"Add button ({add_tab_rect.width()}px) should be <= first tab ({first_tab_rect.width()}px)"

    def test_tab_bar_scrollable_with_many_tabs(self, main_window):
        """Tab bar should be scrollable when there are many tabs"""
        tab_bar = main_window._tab_widget.tabBar()

        # Add many categories to exceed window width
        for i in range(10):
            new_category = AppCategory(
                id=str(uuid.uuid4()),
                name=f"Category{i}",
                icon="📁"
            )
            main_window._app_state.add_category(new_category)

        # Tab bar should have scroll buttons enabled
        assert tab_bar.usesScrollButtons(), "Tab bar should use scroll buttons"

    def test_long_category_name_truncated(self, main_window):
        """Long category names should be truncated with ellipsis"""
        # Add category with very long name
        long_name = "VeryLongCategoryNameThatShouldBeTruncated"
        new_category = AppCategory(
            id=str(uuid.uuid4()),
            name=long_name,
            icon="📁"
        )
        main_window._app_state.add_category(new_category)

        tab_bar = main_window._tab_widget.tabBar()

        # Find the new tab
        new_tab_index = len(main_window._app_state.categories) - 1
        tab_rect = tab_bar.tabRect(new_tab_index)

        # Tab should have reasonable max width (not expand infinitely)
        assert tab_rect.width() <= 120, f"Long name tab should be <= 120px, got: {tab_rect.width()}"

    def test_tab_text_readable_width(self, main_window):
        """Tab should be wide enough to show at least a few characters"""
        tab_bar = main_window._tab_widget.tabBar()

        # Add a category with moderate name (unique name)
        new_category = AppCategory(
            id=str(uuid.uuid4()),
            name="Games",
            icon="🎮"
        )
        main_window._app_state.add_category(new_category)

        # Find the new tab
        new_tab_index = len(main_window._app_state.categories) - 1
        tab_rect = tab_bar.tabRect(new_tab_index)

        # Should be wide enough to show icon + some text
        assert tab_rect.width() >= 60, f"Tab should be >= 60px for readability, got: {tab_rect.width()}"

    def test_context_menu_available(self, main_window):
        """Tab bar should have custom context menu policy"""
        tab_bar = main_window._tab_widget.tabBar()
        assert tab_bar.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu, \
            "Tab bar should have CustomContextMenu policy for right-click menu"
