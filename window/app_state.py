"""
Global application state
Manages categories, apps, notes, and selected category
"""
from typing import List, Optional

from PySide6.QtCore import QObject, Signal
from models.app_shortcut import AppShortcut, LaunchType
from models.category import AppCategory
from services.storage_service import StorageService
from window.models.note import Note, NoteType


class AppState(QObject):
    """Global application state manager"""

    state_changed = Signal()

    def __init__(self, storage_service: Optional[StorageService] = None):
        super().__init__()
        self._storage = storage_service or StorageService()
        self._categories: List[AppCategory] = []
        self._apps: List[AppShortcut] = []
        self._notes: List[Note] = []
        self._selected_category: Optional[AppCategory] = None

        if not self._load_from_storage():
            self._load_initial_data()

        self._save_state()

    @property
    def categories(self) -> List[AppCategory]:
        return list(self._categories)

    @property
    def apps(self) -> List[AppShortcut]:
        return list(self._apps)

    @property
    def notes(self) -> List[Note]:
        """Get all notes"""
        return list(self._notes)

    @property
    def selected_category(self) -> Optional[AppCategory]:
        return self._selected_category

    @property
    def filtered_apps(self) -> List[AppShortcut]:
        if self._selected_category is None or self._selected_category.name == 'All':
            return self.apps
        return [app for app in self._apps if app.category == self._selected_category.name]

    @property
    def filtered_notes(self) -> List[Note]:
        if self._selected_category is None or self._selected_category.name == 'All':
            return self.notes
        return [note for note in self._notes if note.category == self._selected_category.name]

    def _load_initial_data(self):
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

        self._notes = [
            Note(
                id='note-1',
                content='Welcome to My Everything Widget notes',
                type=NoteType.TEXT,
                category='All',
            )
        ]

        self._selected_category = self._categories[0]

    def _load_from_storage(self) -> bool:
        payload = self._storage.load()
        categories = payload.get("categories", [])
        apps = payload.get("apps", [])
        notes = payload.get("notes", [])

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
            self._notes = [Note.from_dict(note_dict) for note_dict in notes]
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

    def _note_to_dict(self, note: Note) -> dict:
        return note.to_dict()

    def _save_state(self):
        categories_payload = [self._category_to_dict(cat) for cat in self._categories]
        apps_payload = [self._app_to_dict(app) for app in self._apps]
        notes_payload = [self._note_to_dict(note) for note in self._notes]
        self._storage.save(categories_payload, apps_payload, notes_payload)

    def _persist_state(self):
        self._save_state()
        self.state_changed.emit()

    def select_category(self, category: AppCategory):
        self._selected_category = category
        self.state_changed.emit()

    def add_app(self, app: AppShortcut):
        self._apps.append(app)
        self._persist_state()

    def update_app(self, updated_app: AppShortcut):
        for i, app in enumerate(self._apps):
            if app.id == updated_app.id:
                from dataclasses import replace

                self._apps[i] = replace(app, **updated_app.__dict__)
                self._persist_state()
                return

    def remove_app(self, app_id: str):
        self._apps = [app for app in self._apps if app.id != app_id]
        self._persist_state()

    def add_category(self, category: AppCategory):
        if any(c.name == category.name for c in self._categories):
            raise ValueError(f"Category '{category.name}' already exists")
        self._categories.append(category)
        self._persist_state()

    def remove_category(self, category_id: str):
        category = next((c for c in self._categories if c.id == category_id), None)
        if category is None:
            return

        if category.name == 'All':
            raise ValueError("Cannot remove 'All' category")

        self._categories = [c for c in self._categories if c.id != category_id]

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

        if self._selected_category and self._selected_category.id == category_id:
            self._selected_category = next((c for c in self._categories if c.name == 'All'), None)

        self._persist_state()

    def update_category(self, updated_category: AppCategory):
        for i, category in enumerate(self._categories):
            if category.id == updated_category.id:
                old_name = category.name
                self._categories[i] = updated_category

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

                if self._selected_category and self._selected_category.id == updated_category.id:
                    self._selected_category = updated_category

                self._persist_state()
                return

    def add_note(self, note: Note):
        self._notes.append(note)
        self._persist_state()

    def update_note(self, updated_note: Note):
        from dataclasses import replace

        for i, note in enumerate(self._notes):
            if note.id == updated_note.id:
                self._notes[i] = replace(note, **updated_note.__dict__)
                self._persist_state()
                return

    def remove_note(self, note_id: str):
        self._notes = [note for note in self._notes if note.id != note_id]
        self._persist_state()

