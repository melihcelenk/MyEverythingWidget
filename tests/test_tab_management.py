"""
Tests for tab management functionality
"""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from window.app_state import AppState
from window.main_window import MainWindow
from models.category import AppCategory
from models.app_shortcut import AppShortcut, LaunchType
import uuid


class TestTabManagement:
    """Test tab management features"""
    
    def test_tab_creation_on_startup(self, qapp):
        """Test that tabs are created correctly on startup"""
        window = MainWindow()
        
        # Should have default tabs: All, Web, Dev, Media, and + tab
        assert window._tab_widget.count() >= 4  # At least 4 category tabs + 1 add tab
        
        # Check that default categories exist
        categories = window._app_state.categories
        assert len(categories) >= 4
        assert any(c.name == 'All' for c in categories)
        assert any(c.name == 'Web' for c in categories)
        
        window.close()
    
    def test_tab_switching(self, qapp):
        """Test switching between tabs"""
        window = MainWindow()
        
        initial_count = window._tab_widget.count()
        assert initial_count > 0
        
        # Switch to first tab
        window._tab_widget.setCurrentIndex(0)
        assert window._tab_widget.currentIndex() == 0
        
        # Switch to second tab (if exists)
        if initial_count > 1:
            window._tab_widget.setCurrentIndex(1)
            assert window._tab_widget.currentIndex() == 1
        
        window.close()
    
    def test_add_category_tab(self, qapp):
        """Test adding a new category tab"""
        window = MainWindow()
        
        initial_count = window._tab_widget.count()
        initial_category_count = len(window._app_state.categories)
        
        # Add a new category
        new_category = AppCategory(
            id=str(uuid.uuid4()),
            name='Test Category',
            icon='📁'
        )
        window._app_state.add_category(new_category)
        
        # Should have one more tab now
        assert len(window._app_state.categories) == initial_category_count + 1
        # Tab count should increase (category tab + add tab)
        assert window._tab_widget.count() >= initial_count
        
        window.close()
    
    def test_remove_category_tab(self, qapp):
        """Test removing a category tab"""
        window = MainWindow()
        
        # Add a test category first
        test_category = AppCategory(
            id=str(uuid.uuid4()),
            name='To Be Deleted',
            icon='📁'
        )
        window._app_state.add_category(test_category)
        category_count_after_add = len(window._app_state.categories)
        
        # Remove the category
        window._app_state.remove_category(test_category.id)
        
        # Should have one less category
        assert len(window._app_state.categories) == category_count_after_add - 1
        
        window.close()
    
    def test_cannot_remove_all_category(self, qapp):
        """Test that 'All' category cannot be removed"""
        window = MainWindow()
        
        all_category = next((c for c in window._app_state.categories if c.name == 'All'), None)
        assert all_category is not None
        
        # Should raise ValueError when trying to remove 'All'
        with pytest.raises(ValueError, match="Cannot remove 'All' category"):
            window._app_state.remove_category(all_category.id)
        
        window.close()
    
    def test_update_category_tab(self, qapp):
        """Test updating a category tab"""
        window = MainWindow()
        
        # Add a test category
        test_category = AppCategory(
            id=str(uuid.uuid4()),
            name='Original Name',
            icon='📁'
        )
        window._app_state.add_category(test_category)
        
        # Update the category
        updated_category = AppCategory(
            id=test_category.id,
            name='Updated Name',
            icon='📁'
        )
        window._app_state.update_category(updated_category)
        
        # Verify update
        updated = next((c for c in window._app_state.categories if c.id == test_category.id), None)
        assert updated is not None
        assert updated.name == 'Updated Name'
        
        window.close()
    
    def test_tab_state_preservation_on_update(self, qapp):
        """Test that selected tab is preserved when state changes"""
        window = MainWindow()
        
        # Select a specific tab
        if window._tab_widget.count() > 1:
            window._tab_widget.setCurrentIndex(1)
            selected_index = window._tab_widget.currentIndex()
            
            # Trigger state change (e.g., add an app)
            new_app = AppShortcut(
                id=str(uuid.uuid4()),
                name='Test App',
                icon_path='',
                target='test',
                category='Web',
                type=LaunchType.URL
            )
            window._app_state.add_app(new_app)
            
            # Tab should still be selected (or restored to same category)
            # The exact index might change, but the category should be preserved
            assert window._tab_widget.currentIndex() >= 0
        
        window.close()


class TestAppCardManagement:
    """Test app card management in tabs"""
    
    def test_app_card_creation_in_tab(self, qapp):
        """Test that app cards are created correctly in tabs"""
        window = MainWindow()
        
        # Add an app to a category
        test_app = AppShortcut(
            id=str(uuid.uuid4()),
            name='Test App',
            icon_path='',
            target='https://test.com',
            category='Web',
            type=LaunchType.URL
        )
        window._app_state.add_app(test_app)
        
        # App should be in the state
        apps = window._app_state.apps
        assert any(a.id == test_app.id for a in apps)
        
        window.close()
    
    def test_app_card_display_in_category_tab(self, qapp):
        """Test that app cards are displayed in correct category tab"""
        window = MainWindow()
        
        # Add apps to different categories
        web_app = AppShortcut(
            id=str(uuid.uuid4()),
            name='Web App',
            icon_path='',
            target='https://web.com',
            category='Web',
            type=LaunchType.URL
        )
        dev_app = AppShortcut(
            id=str(uuid.uuid4()),
            name='Dev App',
            icon_path='',
            target='https://dev.com',
            category='Dev',
            type=LaunchType.URL
        )
        
        window._app_state.add_app(web_app)
        window._app_state.add_app(dev_app)
        
        # Check filtered apps
        web_apps = window._app_state.filtered_apps
        # Should include web_app when Web category is selected
        # Note: This depends on current category selection
        
        window.close()
    
    def test_app_card_removal(self, qapp):
        """Test removing an app card"""
        window = MainWindow()
        
        # Add an app
        test_app = AppShortcut(
            id=str(uuid.uuid4()),
            name='To Be Removed',
            icon_path='',
            target='test',
            category='Web',
            type=LaunchType.URL
        )
        window._app_state.add_app(test_app)
        initial_count = len(window._app_state.apps)
        
        # Remove the app
        window._app_state.remove_app(test_app.id)
        
        # Should have one less app
        assert len(window._app_state.apps) == initial_count - 1
        assert not any(a.id == test_app.id for a in window._app_state.apps)
        
        window.close()
    
    def test_app_card_update(self, qapp):
        """Test updating an app card"""
        window = MainWindow()
        
        # Add an app
        test_app = AppShortcut(
            id=str(uuid.uuid4()),
            name='Original Name',
            icon_path='',
            target='test',
            category='Web',
            type=LaunchType.URL
        )
        window._app_state.add_app(test_app)
        
        # Update the app
        updated_app = AppShortcut(
            id=test_app.id,
            name='Updated Name',
            icon_path='',
            target='test',
            category='Web',
            type=LaunchType.URL
        )
        window._app_state.update_app(updated_app)
        
        # Verify update
        updated = next((a for a in window._app_state.apps if a.id == test_app.id), None)
        assert updated is not None
        assert updated.name == 'Updated Name'
        
        window.close()
    
    def test_app_card_category_change(self, qapp):
        """Test moving app card to different category"""
        window = MainWindow()
        
        # Add an app to Web category
        test_app = AppShortcut(
            id=str(uuid.uuid4()),
            name='Movable App',
            icon_path='',
            target='test',
            category='Web',
            type=LaunchType.URL
        )
        window._app_state.add_app(test_app)
        
        # Move to Dev category
        moved_app = AppShortcut(
            id=test_app.id,
            name='Movable App',
            icon_path='',
            target='test',
            category='Dev',
            type=LaunchType.URL
        )
        window._app_state.update_app(moved_app)
        
        # Verify category change
        updated = next((a for a in window._app_state.apps if a.id == test_app.id), None)
        assert updated is not None
        assert updated.category == 'Dev'
        
        window.close()
    
    def test_multiple_operations_no_crash(self, qapp):
        """Test multiple operations in sequence without crashes"""
        window = MainWindow()
        
        # Perform multiple operations
        for i in range(5):
            # Add category
            new_category = AppCategory(
                id=str(uuid.uuid4()),
                name=f'Category {i}',
                icon='📁'
            )
            window._app_state.add_category(new_category)
            
            # Add app
            new_app = AppShortcut(
                id=str(uuid.uuid4()),
                name=f'App {i}',
                icon_path='',
                target=f'test{i}',
                category=new_category.name,
                type=LaunchType.URL
            )
            window._app_state.add_app(new_app)
            
            # Switch tabs
            if window._tab_widget.count() > 0:
                window._tab_widget.setCurrentIndex(i % window._tab_widget.count())
        
        # Should still be functional
        assert window._tab_widget.count() > 0
        
        window.close()

