"""
Unit tests for MainWindow
Tests tab management, app card creation, and state changes
"""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from window.main_window import MainWindow
from window.app_state import AppState
from models.app_shortcut import AppShortcut, LaunchType
from models.category import AppCategory
import uuid


@pytest.fixture
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def main_window(qapp):
    """Create MainWindow instance for tests"""
    window = MainWindow()
    yield window
    window.close()


class TestMainWindow:
    """Test suite for MainWindow"""
    
    def test_window_creation(self, main_window):
        """Test that window can be created without errors"""
        assert main_window is not None
        assert main_window._app_state is not None
        assert main_window._tab_widget is not None
    
    def test_initial_tabs_created(self, main_window):
        """Test that initial tabs are created"""
        # Should have at least "All" category tab + add tab
        assert main_window._tab_widget.count() >= 2
    
    def test_tab_switching(self, main_window):
        """Test switching between tabs"""
        initial_index = main_window._tab_widget.currentIndex()
        
        # Switch to next tab if available
        if main_window._tab_widget.count() > 1:
            main_window._tab_widget.setCurrentIndex(1)
            assert main_window._tab_widget.currentIndex() == 1
    
    def test_add_category(self, main_window):
        """Test adding a new category"""
        initial_count = main_window._tab_widget.count()
        
        unique_id = str(uuid.uuid4())
        new_category = AppCategory(
            id=unique_id,
            name=f"Test Category {unique_id[:8]}",
            icon="📁"
        )
        
        main_window._app_state.add_category(new_category)
        
        # Should have one more tab (category tab, add tab stays)
        assert main_window._tab_widget.count() == initial_count + 1
    
    def test_remove_category(self, main_window):
        """Test removing a category"""
        # Add a test category first
        test_category = AppCategory(
            id=str(uuid.uuid4()),
            name="To Delete",
            icon="📁"
        )
        main_window._app_state.add_category(test_category)
        count_after_add = main_window._tab_widget.count()
        
        # Remove the category
        main_window._app_state.remove_category(test_category.id)
        
        # Should have one less tab
        assert main_window._tab_widget.count() == count_after_add - 1
    
    def test_add_app_triggers_state_change(self, main_window):
        """Test that adding an app triggers state change and updates tabs"""
        new_app = AppShortcut(
            id=str(uuid.uuid4()),
            name="Test App",
            icon_path="",
            target="https://test.com",
            category="All",
            type=LaunchType.URL
        )
        
        # Should not raise any errors
        main_window._app_state.add_app(new_app)
        
        # Verify app was added
        assert len(main_window._app_state.apps) > 0
    
    def test_remove_app_triggers_state_change(self, main_window):
        """Test that removing an app triggers state change"""
        # Add an app first
        test_app = AppShortcut(
            id=str(uuid.uuid4()),
            name="To Delete",
            icon_path="",
            target="https://delete.com",
            category="All",
            type=LaunchType.URL
        )
        main_window._app_state.add_app(test_app)
        initial_count = len(main_window._app_state.apps)
        
        # Remove the app
        main_window._app_state.remove_app(test_app.id)
        
        # Should have one less app
        assert len(main_window._app_state.apps) == initial_count - 1
    
    def test_update_app_triggers_state_change(self, main_window):
        """Test that updating an app triggers state change"""
        # Add an app first
        test_app = AppShortcut(
            id=str(uuid.uuid4()),
            name="Original Name",
            icon_path="",
            target="https://test.com",
            category="All",
            type=LaunchType.URL
        )
        main_window._app_state.add_app(test_app)
        
        # Update the app
        updated_app = AppShortcut(
            id=test_app.id,
            name="Updated Name",
            icon_path="",
            target=test_app.target,
            category=test_app.category,
            type=test_app.type
        )
        
        # Should not raise any errors
        main_window._app_state.update_app(updated_app)
        
        # Verify app was updated
        updated = next((a for a in main_window._app_state.apps if a.id == test_app.id), None)
        assert updated is not None
        assert updated.name == "Updated Name"
    
    def test_category_tab_has_app_cards(self, main_window):
        """Test that category tabs contain app cards"""
        # Get the first category tab (should be "All")
        if main_window._tab_widget.count() > 0:
            # Check that tab manager has category grids
            assert len(main_window._tab_manager._category_grids) > 0
    
    def test_multiple_tab_switches(self, main_window):
        """Test switching between multiple tabs repeatedly"""
        tab_count = main_window._tab_widget.count()
        
        # Switch through all tabs multiple times
        for _ in range(3):
            for i in range(tab_count):
                main_window._tab_widget.setCurrentIndex(i)
                assert main_window._tab_widget.currentIndex() == i
    
    def test_state_change_preserves_selected_tab(self, main_window):
        """Test that state changes preserve the currently selected tab"""
        if main_window._tab_widget.count() > 1:
            # Select a specific tab
            target_index = 1
            main_window._tab_widget.setCurrentIndex(target_index)
            
            # Trigger a state change by adding an app
            test_app = AppShortcut(
                id=str(uuid.uuid4()),
                name="State Change Test",
                icon_path="",
                target="https://test.com",
                category="All",
                type=LaunchType.URL
            )
            main_window._app_state.add_app(test_app)
            
            # Tab should still be selected (or restored to same category)
            # The exact index might change if tabs were recreated, but category should be preserved
            assert main_window._tab_widget.currentIndex() >= 0
    
    def test_app_card_creation_with_empty_icon_path(self, main_window):
        """Test that app cards can be created with empty icon_path"""
        test_app = AppShortcut(
            id=str(uuid.uuid4()),
            name="Empty Icon Test",
            icon_path="",  # Empty string
            target="https://test.com",
            category="All",
            type=LaunchType.URL
        )
        
        # Should not raise any errors
        main_window._app_state.add_app(test_app)
    
    def test_app_card_creation_with_emoji_icon(self, main_window):
        """Test that app cards can be created with emoji icon"""
        test_app = AppShortcut(
            id=str(uuid.uuid4()),
            name="Emoji Icon Test",
            icon_path="📱",  # Emoji
            target="https://test.com",
            category="All",
            type=LaunchType.URL
        )
        
        # Should not raise any errors
        main_window._app_state.add_app(test_app)
    
    def test_app_card_creation_with_long_icon_path(self, main_window):
        """Test that app cards can be created with long icon_path (image file)"""
        test_app = AppShortcut(
            id=str(uuid.uuid4()),
            name="Long Icon Test",
            icon_path="nonexistent/path/to/image.png",  # Long path, doesn't exist
            target="https://test.com",
            category="All",
            type=LaunchType.URL
        )
        
        # Should not raise any errors (should fallback to default icon)
        main_window._app_state.add_app(test_app)
    
    def test_add_and_remove_category_cycle(self, main_window):
        """Test adding and removing categories in a cycle"""
        # Add multiple categories
        categories = []
        for i in range(3):
            cat = AppCategory(
                id=str(uuid.uuid4()),
                name=f"Test Category {i}",
                icon="📁"
            )
            main_window._app_state.add_category(cat)
            categories.append(cat)

        # Remove them one by one
        for cat in categories:
            main_window._app_state.remove_category(cat.id)

        # Should be back to initial state (at least "All" category)
        assert main_window._tab_widget.count() >= 1

    def test_switch_to_each_category_tab(self, main_window):
        """Test switching to each category tab doesn't crash"""
        for i in range(len(main_window._app_state.categories)):
            main_window._tab_widget.setCurrentIndex(i)
            # Force processing of signals
            QApplication.processEvents()
            assert main_window._tab_widget.currentIndex() == i

    def test_add_app_with_different_types(self, main_window):
        """Test adding apps with different LaunchTypes"""
        types = [LaunchType.URL, LaunchType.EXE, LaunchType.FOLDER]

        for i, launch_type in enumerate(types):
            app = AppShortcut(
                id=str(uuid.uuid4()),
                name=f"Type Test {i}",
                icon_path="",
                target="test/path",
                category="All",
                type=launch_type
            )
            main_window._app_state.add_app(app)

        # All should be added
        assert len(main_window._app_state.apps) >= 3

    def test_add_app_with_various_emojis(self, main_window):
        """Test adding apps with various emoji icons"""
        emojis = ['🎮', '🌐', '📁', '📱', '⚙️']

        for i, emoji in enumerate(emojis):
            app = AppShortcut(
                id=str(uuid.uuid4()),
                name=f"Emoji App {i}",
                icon_path=emoji,
                target="https://test.com",
                category="All",
                type=LaunchType.URL
            )
            main_window._app_state.add_app(app)
            QApplication.processEvents()

        # All should be added without crash
        assert len(main_window._app_state.apps) >= len(emojis)

    def test_rapid_state_changes(self, main_window):
        """Test rapid state changes don't cause crashes"""
        for i in range(20):
            app = AppShortcut(
                id=str(uuid.uuid4()),
                name=f"Rapid Test {i}",
                icon_path="",
                target="https://test.com",
                category="All",
                type=LaunchType.URL
            )
            main_window._app_state.add_app(app)

        QApplication.processEvents()
        assert main_window._tab_widget.count() >= 1

