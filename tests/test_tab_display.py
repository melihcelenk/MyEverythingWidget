"""
Tests for tab display - text visibility, width, and scrolling
"""
import os
import uuid

import pytest
from PySide6.QtCore import Qt, QPoint

from models.category import AppCategory
from window.main_window import MainWindow


class TestTabDisplay:
    """Test tab display properties"""

    @pytest.fixture
    def main_window(self, qtbot, tmp_path):
        """Create main window for testing"""
        state_file = tmp_path / "app_state.json"
        os.environ["MEW_STATE_PATH"] = str(state_file)
        window = MainWindow()
        qtbot.addWidget(window)
        try:
            yield window
        finally:
            os.environ.pop("MEW_STATE_PATH", None)

    def test_tab_text_not_elided_for_short_names(self, main_window):
        """Tab text should be fully visible for short category names"""
        tab_bar = main_window._tab_widget.tabBar()

        # Check "Web" tab (index 0) - should show full text
        tab_text = tab_bar.tabText(0)
        assert "Web" in tab_text, f"Tab text should contain 'Web', got: {tab_text}"

        # Tab width should be enough to show the text
        tab_rect = tab_bar.tabRect(0)
        assert tab_rect.width() >= 50, f"Tab width should be >= 50px, got: {tab_rect.width()}"

    def test_tab_minimum_width(self, main_window):
        """Each tab should have minimum width for text visibility"""
        tab_bar = main_window._tab_widget.tabBar()

        # Check all category tabs (not the + button)
        for i in range(main_window._tab_widget.count() - 1):
            tab_rect = tab_bar.tabRect(i)
            # Minimum width should be at least 50px for text visibility
            assert tab_rect.width() >= 50, f"Tab {i} width should be >= 50px, got: {tab_rect.width()}"

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

    def test_tab_bar_supports_many_tabs(self, main_window):
        """Tab bar should support many tabs without crashing"""
        tab_bar = main_window._tab_widget.tabBar()

        # Add many categories to exceed window width
        for i in range(10):
            new_category = AppCategory(
                id=str(uuid.uuid4()),
                name=f"Category{i}",
                icon="📁"
            )
            main_window._app_state.add_category(new_category)

        # Tab bar should have all tabs
        # Original categories + 10 new + 1 add button
        expected_count = len(main_window._app_state.categories) + 1
        assert tab_bar.count() == expected_count, f"Expected {expected_count} tabs, got {tab_bar.count()}"

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

    def test_scroll_buttons_enabled(self, main_window):
        """Tab bar should have scroll buttons for overflow tabs"""
        tab_bar = main_window._tab_widget.tabBar()
        # Scroll buttons should be enabled to access overflow tabs
        assert tab_bar.usesScrollButtons(), "Tab bar should use scroll buttons"

    def test_tab_bar_mouse_tracking(self, main_window):
        """Tab bar should have mouse tracking for drag scrolling"""
        tab_bar = main_window._tab_widget.tabBar()
        assert tab_bar.hasMouseTracking(), "Tab bar should have mouse tracking enabled"

    def test_drag_scroll_changes_tab(self, main_window, qtbot):
        """Dragging on tab bar should change tabs"""
        from PySide6.QtCore import QPoint

        # Add more categories to have something to scroll to
        for i in range(5):
            new_category = AppCategory(
                id=str(uuid.uuid4()),
                name=f"Cat{i}",
                icon="📁"
            )
            main_window._app_state.add_category(new_category)

        tab_bar = main_window._tab_widget.tabBar()
        initial_index = tab_bar.currentIndex()

        # Simulate drag: press, move left (negative delta), release
        start_pos = QPoint(150, 15)
        end_pos = QPoint(50, 15)  # Drag left by 100px

        # Mouse press
        qtbot.mousePress(tab_bar, Qt.MouseButton.LeftButton, pos=start_pos)

        # Mouse move (drag)
        qtbot.mouseMove(tab_bar, pos=end_pos)

        # Mouse release
        qtbot.mouseRelease(tab_bar, Qt.MouseButton.LeftButton, pos=end_pos)

        # Tab should have changed (moved to next tab when dragging left)
        new_index = tab_bar.currentIndex()
        assert new_index != initial_index or initial_index == tab_bar.count() - 2, \
            f"Tab should change after drag, was {initial_index}, now {new_index}"

    def test_click_without_drag_selects_tab(self, main_window, qtbot):
        """Clicking without dragging should select the clicked tab"""
        tab_bar = main_window._tab_widget.tabBar()

        # Get position of second tab
        tab_rect = tab_bar.tabRect(1)
        click_pos = tab_rect.center()

        # Simple click (no drag)
        qtbot.mouseClick(tab_bar, Qt.MouseButton.LeftButton, pos=click_pos)

        # Should select the clicked tab
        assert tab_bar.currentIndex() == 1, f"Should select tab 1, got {tab_bar.currentIndex()}"

    def test_add_button_preserved_after_category_add(self, main_window):
        """Adding a category should preserve the + button"""
        from models.category import AppCategory

        tab_bar = main_window._tab_widget.tabBar()
        initial_count = tab_bar.count()

        # Add a new category programmatically
        new_category = AppCategory(
            id=str(uuid.uuid4()),
            name="NewCat",
            icon="📁"
        )
        main_window._app_state.add_category(new_category)

        # Tab count should increase by 1
        new_count = tab_bar.count()
        assert new_count == initial_count + 1, f"Tab count should be {initial_count + 1}, got {new_count}"

        # Last tab should still be + button
        last_tab_text = tab_bar.tabText(tab_bar.count() - 1)
        assert last_tab_text == "+", f"Last tab should be '+', got '{last_tab_text}'"

    def test_wheel_scroll_to_last_shows_add_button(self, main_window, qtbot):
        """Mouse wheel scroll to last category should keep current index"""
        from PySide6.QtGui import QWheelEvent
        from PySide6.QtCore import QPointF

        # Add many categories to ensure overflow
        for i in range(8):
            new_category = AppCategory(
                id=str(uuid.uuid4()),
                name=f"Cat{i}",
                icon="📁"
            )
            main_window._app_state.add_category(new_category)

        tab_bar = main_window._tab_widget.tabBar()
        last_category_index = tab_bar.count() - 2

        # Go to last category
        tab_bar.setCurrentIndex(last_category_index)
        assert tab_bar.currentIndex() == last_category_index

        # Simulate wheel scroll down (should try to show + button)
        wheel_event = QWheelEvent(
            QPointF(50, 15),  # pos
            QPointF(50, 15),  # globalPos
            QPoint(0, 0),  # pixelDelta
            QPoint(0, -120),  # angleDelta (scroll down)
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False
        )
        tab_bar.wheelEvent(wheel_event)

        add_button_index = tab_bar.count() - 1
        assert tab_bar.currentIndex() == add_button_index, \
            f"Should move to add button {add_button_index}, got {tab_bar.currentIndex()}"

    def test_add_tab_button_emits_signal(self, main_window, qtbot, monkeypatch):
        """Clicking + button should emit tabBarClicked signal"""
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent

        # Mock the dialog to prevent it from appearing
        monkeypatch.setattr(
            main_window._dialog_manager,
            'show_add_category_dialog',
            lambda: False
        )

        tab_bar = main_window._tab_widget.tabBar()
        add_button_index = tab_bar.count() - 1

        # Get add button position
        add_rect = tab_bar.tabRect(add_button_index)
        click_pos = add_rect.center()

        # Track signal emission
        clicked_indices = []
        tab_bar.tabBarClicked.connect(lambda idx: clicked_indices.append(idx))

        # Simulate mouse press (this emits tabBarClicked)
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            click_pos.toPointF(),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        tab_bar.mousePressEvent(press_event)

        # tabBarClicked should be emitted with add button index
        assert len(clicked_indices) > 0, "tabBarClicked should be emitted"
        assert clicked_indices[-1] == add_button_index, \
            f"Should emit index {add_button_index}, got {clicked_indices[-1]}"
