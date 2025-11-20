"""
Global application state
Manages categories, apps, and selected category
"""
from typing import List, Optional

from PySide6.QtCore import QObject, Signal
from models.app_shortcut import AppShortcut, LaunchType
from models.category import AppCategory
from services.storage_service import StorageService


class AppState(QObject):
    """Global application state manager"""

    # Signals
    state_changed = Signal()

    def __init__(self, storage_service: Optional[StorageService] = None):
        super().__init__()
        self._storage = storage_service or StorageService()
        self._categories: List[AppCategory] = []
        self._apps: List[AppShortcut] = []
        self._selected_category: Optional[AppCategory] = None

        if not self._load_from_storage():
            self._load_initial_data()

        self._save_state()
    
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
        """Load default categories and apps into memory"""
        self._categories = [
            AppCategory(id='1', name='All', icon='📱'),
            AppCategory(id='2', name='Web', icon='🌐'),
            AppCategory(id='3', name='Dev', icon='💻'),
            AppCategory(id='4', name='Media', icon='🎵'),
        ]

        default_apps = [
            ("1", "Google Chrome", "https://google.com", "Web"),
            ("2", "GitHub Desktop", "https://github.com", "Dev"),
            ("3", "YouTube Music", "https://music.youtube.com", "Media"),
            ("4", "Spotify Premium", "https://spotify.com", "Media"),
            ("5", "Stack Overflow Community", "https://stackoverflow.com", "Dev"),
            ("6", "Gmail", "https://gmail.com", "Web"),
            ("7", "Visual Studio Code", "https://code.visualstudio.com", "Dev"),
            ("8", "CodePen Playground", "https://codepen.io", "Dev"),
            ("9", "MDN Web Docs", "https://developer.mozilla.org", "Dev"),
            ("10", "Docker Hub Registry", "https://hub.docker.com", "Dev"),
            ("11", "NPM Package Manager", "https://npmjs.com", "Dev"),
            ("12", "Git Version Control", "https://git-scm.com", "Dev"),
        ]

        self._apps = [
            AppShortcut(
                id=app_id,
                name=name,
                icon_path='',
                target=target,
                category=category,
                type=LaunchType.URL,
            )
            for app_id, name, target, category in default_apps
        ]

        self._selected_category = self._categories[0]

    def _load_from_storage(self) -> bool:
        """Try to hydrate state from the persisted file."""
        payload = self._storage.load()
        categories = payload.get("categories", [])
        apps = payload.get("apps", [])

        if not categories or not apps:
            return False

        try:
            self._categories = [AppCategory(**cat) for cat in categories]
            self._apps = [
                AppShortcut(
                    id=app["id"],
                    name=app["name"],
                    icon_path=app.get("icon_path", ""),
                    target=app["target"],
                    category=app["category"],
                    type=LaunchType(app.get("type") or LaunchType.URL.value),
                )
                for app in apps
            ]
        except KeyError:
            return False

        self._selected_category = next(
            (cat for cat in self._categories if cat.name == 'All'),
            self._categories[0],
        )

        return True

    def _category_to_dict(self, category: AppCategory) -> dict:
        return {"id": category.id, "name": category.name, "icon": category.icon}

    def _app_to_dict(self, app: AppShortcut) -> dict:
        return {
            "id": app.id,
            "name": app.name,
            "icon_path": app.icon_path,
            "target": app.target,
            "category": app.category,
            "type": app.type.value,
        }

    def _save_state(self):
        """Persist the current lists."""
        categories_payload = [self._category_to_dict(cat) for cat in self._categories]
        apps_payload = [self._app_to_dict(app) for app in self._apps]
        self._storage.save(categories_payload, apps_payload)

    def _persist_state(self):
        """Save and notify observers."""
        self._save_state()
        self.state_changed.emit()
    
    def select_category(self, category: AppCategory):
        """Select a category"""
        self._selected_category = category
        self.state_changed.emit()
    
    def add_app(self, app: AppShortcut):
        """Add a new app to the list"""
        self._apps.append(app)
        self._persist_state()
    
    def update_app(self, updated_app: AppShortcut):
        """Update an existing app"""
        for i, app in enumerate(self._apps):
            if app.id == updated_app.id:
                # Create new instance to ensure immutability
                from dataclasses import replace
                self._apps[i] = replace(app, **updated_app.__dict__)
                self._persist_state()
                return
    
    def remove_app(self, app_id: str):
        """Remove an app from the list"""
        self._apps = [app for app in self._apps if app.id != app_id]
        self._persist_state()
    
    def add_category(self, category: AppCategory):
        """Add a new category"""
        # Check if category with same name exists
        if any(c.name == category.name for c in self._categories):
            raise ValueError(f"Category '{category.name}' already exists")
        self._categories.append(category)
        self._persist_state()
    
    def remove_category(self, category_id: str):
        """Remove a category"""
        # Don't allow removing "All" category
        category = next((c for c in self._categories if c.id == category_id), None)
        if category is None:
            return

        if category.name == 'All':
            raise ValueError("Cannot remove 'All' category")

        # Remove category and move apps to "All" category
        self._categories = [c for c in self._categories if c.id != category_id]

        # Move apps from deleted category to "All"
        for index, app in enumerate(self._apps):
            if app.category == category.name:
                self._apps[index] = AppShortcut(
                    id=app.id,
                    name=app.name,
                    icon_path=app.icon_path,
                    target=app.target,
                    category='All',
                    type=app.type,
                )

        # If deleted category was selected, select "All"
        if self._selected_category and self._selected_category.id == category_id:
            self._selected_category = next((c for c in self._categories if c.name == 'All'), None)

        self._persist_state()
    
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

                self._persist_state()
                return

