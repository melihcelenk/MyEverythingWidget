"""
Global application state
Manages categories, apps, and selected category
"""
from typing import List, Optional
from PySide6.QtCore import QObject, Signal
from models.app_shortcut import AppShortcut
from models.category import AppCategory


class AppState(QObject):
    """Global application state manager"""
    
    # Signals
    state_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self._categories: List[AppCategory] = []
        self._apps: List[AppShortcut] = []
        self._selected_category: Optional[AppCategory] = None
        self._load_initial_data()
    
    @property
    def categories(self) -> List[AppCategory]:
        """Get all categories"""
        return list(self._categories)
    
    @property
    def apps(self) -> List[AppShortcut]:
        """Get all apps"""
        return list(self._apps)
    
    @property
    def selected_category(self) -> Optional[AppCategory]:
        """Get selected category"""
        return self._selected_category
    
    @property
    def filtered_apps(self) -> List[AppShortcut]:
        """Get apps filtered by selected category"""
        if self._selected_category is None or self._selected_category.name == 'All':
            return self.apps
        return [app for app in self._apps if app.category == self._selected_category.name]
    
    def _load_initial_data(self):
        """Load initial categories and apps"""
        # Load categories
        self._categories = [
            AppCategory(id='1', name='All', icon='📱'),
            AppCategory(id='2', name='Web', icon='🌐'),
            AppCategory(id='3', name='Dev', icon='💻'),
            AppCategory(id='4', name='Media', icon='🎵'),
        ]
        
        # Load apps
        from models.app_shortcut import LaunchType
        self._apps = [
            AppShortcut(
                id='1',
                name='Google Chrome',
                icon_path='',
                target='https://google.com',
                category='Web',
                type=LaunchType.URL,
            ),
            AppShortcut(
                id='2',
                name='GitHub Desktop',
                icon_path='',
                target='https://github.com',
                category='Dev',
                type=LaunchType.URL,
            ),
            AppShortcut(
                id='3',
                name='YouTube Music',
                icon_path='',
                target='https://music.youtube.com',
                category='Media',
                type=LaunchType.URL,
            ),
            AppShortcut(
                id='4',
                name='Spotify Premium',
                icon_path='',
                target='https://spotify.com',
                category='Media',
                type=LaunchType.URL,
            ),
            AppShortcut(
                id='5',
                name='Stack Overflow Community',
                icon_path='',
                target='https://stackoverflow.com',
                category='Dev',
                type=LaunchType.URL,
            ),
            AppShortcut(
                id='6',
                name='Gmail',
                icon_path='',
                target='https://gmail.com',
                category='Web',
                type=LaunchType.URL,
            ),
            AppShortcut(
                id='7',
                name='Visual Studio Code',
                icon_path='',
                target='https://code.visualstudio.com',
                category='Dev',
                type=LaunchType.URL,
            ),
            AppShortcut(
                id='8',
                name='CodePen Playground',
                icon_path='',
                target='https://codepen.io',
                category='Dev',
                type=LaunchType.URL,
            ),
            AppShortcut(
                id='9',
                name='MDN Web Docs',
                icon_path='',
                target='https://developer.mozilla.org',
                category='Dev',
                type=LaunchType.URL,
            ),
            AppShortcut(
                id='10',
                name='Docker Hub Registry',
                icon_path='',
                target='https://hub.docker.com',
                category='Dev',
                type=LaunchType.URL,
            ),
            AppShortcut(
                id='11',
                name='NPM Package Manager',
                icon_path='',
                target='https://npmjs.com',
                category='Dev',
                type=LaunchType.URL,
            ),
            AppShortcut(
                id='12',
                name='Git Version Control',
                icon_path='',
                target='https://git-scm.com',
                category='Dev',
                type=LaunchType.URL,
            ),
        ]
        
        # Set default category
        self._selected_category = self._categories[0]
    
    def select_category(self, category: AppCategory):
        """Select a category"""
        self._selected_category = category
        self.state_changed.emit()
    
    def add_app(self, app: AppShortcut):
        """Add a new app to the list"""
        self._apps.append(app)
        self.state_changed.emit()
    
    def update_app(self, updated_app: AppShortcut):
        """Update an existing app"""
        for i, app in enumerate(self._apps):
            if app.id == updated_app.id:
                self._apps[i] = updated_app
                self.state_changed.emit()
                return
    
    def remove_app(self, app_id: str):
        """Remove an app from the list"""
        self._apps = [app for app in self._apps if app.id != app_id]
        self.state_changed.emit()

