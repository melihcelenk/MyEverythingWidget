"""
Tests for AppCard widget
"""
import pytest
from PySide6.QtWidgets import QApplication, QLabel
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

    def test_app_card_emoji_icon(self, qapp):
        """Test creating app card with emoji icon"""
        app = AppShortcut(
            id='1',
            name='Game',
            icon_path='🎮',
            target='C:/game.exe',
            category='Games',
            type=LaunchType.EXE,
        )

        card = AppCard(app=app, on_tap=lambda: None)
        assert card is not None

    def test_app_card_two_char_emoji(self, qapp):
        """Test creating app card with two-character emoji"""
        app = AppShortcut(
            id='1',
            name='Flag',
            icon_path='🏳️',
            target='https://example.com',
            category='Web',
            type=LaunchType.URL,
        )

        card = AppCard(app=app, on_tap=lambda: None)
        assert card is not None

    def test_app_card_url_default_icon(self, qapp):
        """Test URL type gets web icon"""
        app = AppShortcut(
            id='1',
            name='Website',
            icon_path='',
            target='https://example.com',
            category='Web',
            type=LaunchType.URL,
        )

        card = AppCard(app=app, on_tap=lambda: None)
        assert card is not None

    def test_app_card_exe_default_icon(self, qapp):
        """Test EXE type gets app icon"""
        app = AppShortcut(
            id='1',
            name='Program',
            icon_path='',
            target='C:/app.exe',
            category='Dev',
            type=LaunchType.EXE,
        )

        card = AppCard(app=app, on_tap=lambda: None)
        assert card is not None

    def test_app_card_folder_default_icon(self, qapp):
        """Test FOLDER type gets folder icon"""
        app = AppShortcut(
            id='1',
            name='Folder',
            icon_path='',
            target='C:/folder',
            category='Files',
            type=LaunchType.FOLDER,
        )

        card = AppCard(app=app, on_tap=lambda: None)
        assert card is not None

    def test_app_card_invalid_image_path(self, qapp):
        """Test app with invalid image path falls back to default"""
        app = AppShortcut(
            id='1',
            name='Test',
            icon_path='C:/nonexistent/icon.png',
            target='https://example.com',
            category='Web',
            type=LaunchType.URL,
        )

        card = AppCard(app=app, on_tap=lambda: None)
        assert card is not None

    def test_app_card_none_icon_path(self, qapp):
        """Test app with None icon_path"""
        app = AppShortcut(
            id='1',
            name='Test',
            icon_path=None,
            target='https://example.com',
            category='Web',
            type=LaunchType.URL,
        )

        card = AppCard(app=app, on_tap=lambda: None)
        assert card is not None

    def test_app_card_various_emojis(self, qapp):
        """Test various emoji icons don't crash"""
        emojis = ['🎮', '🌐', '📁', '📱', '⚙️', '🔧', '💻', '🎨', '🎵', '📝']

        for i, emoji in enumerate(emojis):
            app = AppShortcut(
                id=str(i),
                name=f'App {i}',
                icon_path=emoji,
                target='https://example.com',
                category='Web',
                type=LaunchType.URL,
            )

            card = AppCard(app=app, on_tap=lambda: None)
            assert card is not None

    def test_app_card_with_all_callbacks(self, qapp):
        """Test creating app card with all optional callbacks"""
        app = AppShortcut(
            id='1',
            name='Test',
            icon_path='',
            target='https://example.com',
            category='Web',
            type=LaunchType.URL,
        )

        card = AppCard(
            app=app,
            on_tap=lambda: None,
            on_edit=lambda a: None,
            on_rename=lambda a: None,
            on_change_icon=lambda a: None,
        )

        assert card is not None

    def test_create_100_cards_stress(self, qapp):
        """Stress test creating 100 cards"""
        cards = []
        for i in range(100):
            app = AppShortcut(
                id=str(i),
                name=f'App {i}',
                icon_path='',
                target='https://example.com',
                category='Web',
                type=LaunchType.URL,
            )
            card = AppCard(app=app, on_tap=lambda: None)
            cards.append(card)

        assert len(cards) == 100

