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
                # Create new instance to ensure immutability
                from dataclasses import replace
                self._apps[i] = replace(app, **updated_app.__dict__)
                self.state_changed.emit()
                return
    
    def remove_app(self, app_id: str):
        """Remove an app from the list"""
        self._apps = [app for app in self._apps if app.id != app_id]
        self.state_changed.emit()
    
    def add_category(self, category: AppCategory):
        """Add a new category"""
        # Check if category with same name exists
        if any(c.name == category.name for c in self._categories):
            raise ValueError(f"Category '{category.name}' already exists")
        self._categories.append(category)
        self.state_changed.emit()
    
    def remove_category(self, category_id: str):
        """Remove a category"""
        # Don't allow removing "All" category
        category = next((c for c in self._categories if c.id == category_id), None)
        if category and category.name == 'All':
            raise ValueError("Cannot remove 'All' category")
        
        # Remove category and move apps to "All" category
        self._categories = [c for c in self._categories if c.id != category_id]
        
        # Move apps from deleted category to "All"
        apps_to_update = [app for app in self._apps if app.category == category.name]
        for app in apps_to_update:
            updated_app = AppShortcut(
                id=app.id,
                name=app.name,
                icon_path=app.icon_path,
                target=app.target,
                category='All',
                type=app.type,
            )
            self.update_app(updated_app)
        
        # If deleted category was selected, select "All"
        if self._selected_category and self._selected_category.id == category_id:
            self._selected_category = next((c for c in self._categories if c.name == 'All'), None)
        
        self.state_changed.emit()
    
    def update_category(self, updated_category: AppCategory):
        """Update an existing category"""
        for i, category in enumerate(self._categories):
            if category.id == updated_category.id:
                old_name = category.name
                self._categories[i] = updated_category
                
                # Update apps that belong to this category
                apps_to_update = [app for app in self._apps if app.category == old_name]
                for app in apps_to_update:
                    updated_app = AppShortcut(
                        id=app.id,
                        name=app.name,
                        icon_path=app.icon_path,
                        target=app.target,
                        category=updated_category.name,
                        type=app.type,
                    )
                    self.update_app(updated_app)
                
                # Update selected category if it was updated
                if self._selected_category and self._selected_category.id == updated_category.id:
                    self._selected_category = updated_category
                
                self.state_changed.emit()
                return

