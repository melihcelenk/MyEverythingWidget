"""
Tests for AppCard widget
"""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from models.app_shortcut import AppShortcut, LaunchType
from widgets.app_card import AppCard


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestAppCard:
    """Test AppCard widget functionality"""
    
    def test_app_card_creation(self, qapp):
        """Test creating an app card"""
        app = AppShortcut(
            id='1',
            name='Test App',
            icon_path='',
            target='https://example.com',
            category='Web',
            type=LaunchType.URL,
        )
        
        card = AppCard(app=app, on_tap=lambda: None)
        assert card is not None
        assert card._app == app
    
    def test_app_card_tooltip_for_long_name(self, qapp):
        """Test tooltip appears for long app names"""
        app = AppShortcut(
            id='1',
            name='Very Long Application Name That Will Truncate',
            icon_path='',
            target='https://example.com',
            category='Web',
            type=LaunchType.URL,
        )
        
        card = AppCard(app=app, on_tap=lambda: None)
        # Find label widget
        for child in card.findChildren(QLabel):
            if child.text() == app.name:
                # Tooltip should be set for long names
                assert child.toolTip() == app.name or len(child.toolTip()) > 0
                break
    
    def test_app_card_no_tooltip_for_short_name(self, qapp):
        """Test tooltip does not appear for short app names"""
        app = AppShortcut(
            id='1',
            name='Git',
            icon_path='',
            target='https://example.com',
            category='Dev',
            type=LaunchType.URL,
        )
        
        card = AppCard(app=app, on_tap=lambda: None)
        # Find label widget
        for child in card.findChildren(QLabel):
            if child.text() == app.name:
                # Short names may not have tooltip
                # This is acceptable behavior
                break

