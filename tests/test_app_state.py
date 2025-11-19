"""
Tests for AppState
"""
import pytest
from window.app_state import AppState
from models.app_shortcut import AppShortcut, LaunchType


class TestAppState:
    """Test AppState functionality"""
    
    def test_add_app(self):
        """Test adding a new app"""
        app_state = AppState()
        initial_count = len(app_state.apps)
        
        new_app = AppShortcut(
            id='999',
            name='New App',
            icon_path='',
            target='https://example.com',
            category='Web',
            type=LaunchType.URL,
        )
        
        app_state.add_app(new_app)
        
        assert len(app_state.apps) == initial_count + 1
        assert app_state.apps[-1] == new_app
    
    def test_update_app(self):
        """Test updating an existing app"""
        app_state = AppState()
        original_app = app_state.apps[0]
        
        updated_app = AppShortcut(
            id=original_app.id,
            name='Updated Name',
            icon_path=original_app.icon_path,
            target=original_app.target,
            category=original_app.category,
            type=original_app.type,
        )
        
        app_state.update_app(updated_app)
        
        assert app_state.apps[0].name == 'Updated Name'
    
    def test_remove_app(self):
        """Test removing an app"""
        app_state = AppState()
        initial_count = len(app_state.apps)
        app_id = app_state.apps[0].id
        
        app_state.remove_app(app_id)
        
        assert len(app_state.apps) == initial_count - 1
        assert not any(app.id == app_id for app in app_state.apps)
    
    def test_filtered_apps_all_category(self):
        """Test filtered apps for All category"""
        app_state = AppState()
        all_category = app_state.categories[0]  # All category
        app_state.select_category(all_category)
        
        filtered = app_state.filtered_apps
        assert len(filtered) == len(app_state.apps)
    
    def test_filtered_apps_specific_category(self):
        """Test filtered apps for specific category"""
        app_state = AppState()
        dev_category = next(c for c in app_state.categories if c.name == 'Dev')
        app_state.select_category(dev_category)
        
        filtered = app_state.filtered_apps
        assert all(app.category == 'Dev' for app in filtered)
    
    def test_add_app_to_category_filter(self):
        """Test adding app to filtered category"""
        app_state = AppState()
        dev_category = next(c for c in app_state.categories if c.name == 'Dev')
        app_state.select_category(dev_category)
        
        initial_count = len(app_state.filtered_apps)
        
        new_app = AppShortcut(
            id='999',
            name='New Dev Tool',
            icon_path='',
            target='https://example.com',
            category='Dev',
            type=LaunchType.URL,
        )
        
        app_state.add_app(new_app)
        
        assert len(app_state.filtered_apps) == initial_count + 1
        assert new_app in app_state.filtered_apps
    
    def test_add_app_to_different_category_filter(self):
        """Test adding app to different category doesn't show in current filter"""
        app_state = AppState()
        media_category = next(c for c in app_state.categories if c.name == 'Media')
        app_state.select_category(media_category)
        
        initial_count = len(app_state.filtered_apps)
        
        new_app = AppShortcut(
            id='999',
            name='New Web App',
            icon_path='',
            target='https://example.com',
            category='Web',
            type=LaunchType.URL,
        )
        
        app_state.add_app(new_app)
        
        # Media count should not change
        assert len(app_state.filtered_apps) == initial_count
        assert new_app not in app_state.filtered_apps

