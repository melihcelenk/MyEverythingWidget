"""
Global application state
Manages categories, apps, notes, and selected category
"""
import logging
from typing import List, Optional

from PySide6.QtCore import QObject, Signal

from models.app_shortcut import AppShortcut, LaunchType
from models.category import AppCategory
from services.storage_service import StorageService
from window.models.note import Note


class AppState(QObject):
    """Global application state manager"""

    state_changed = Signal()
    _logger = logging.getLogger(__name__)

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
        if self._selected_category is None:
            return self.apps
        return [app for app in self._apps if app.category == self._selected_category.name]

    @property
    def filtered_notes(self) -> List[Note]:
        if self._selected_category is None:
            return self.notes
        return [note for note in self._notes if note.category == self._selected_category.name]

    def _load_initial_data(self):
        """Initialize with empty state - no default data."""
        self._categories = []
        self._apps = []
        self._notes = []
        self._selected_category = None

    def _load_from_storage(self) -> bool:
        payload = self._storage.load()
        if not payload:
            return False
            
        categories = payload.get("categories", [])
        apps = payload.get("apps", [])
        notes = payload.get("notes", [])

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
                    order=app.get("order", 0),
                    grid_row=app.get("grid_row"),
                    grid_col=app.get("grid_col"),
                    col_span=app.get("col_span", 1),
                    row_span=app.get("row_span", 1),
                )
                for app in apps
            ]
            self._notes = [Note.from_dict(note_dict) for note_dict in notes]
        except KeyError:
            return False

        self._selected_category = self._categories[0] if self._categories else None

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
            "order": app.order,
            "grid_row": app.grid_row,
            "grid_col": app.grid_col,
            "col_span": app.col_span,
            "row_span": app.row_span,
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

        self._categories = [c for c in self._categories if c.id != category_id]

        # Move apps to first available category
        first_category = self._categories[0].name if self._categories else "Web"
        for index, app in enumerate(self._apps):
            if app.category == category.name:
                self._apps[index] = AppShortcut(
                    id=app.id,
                    name=app.name,
                    icon_path=app.icon_path,
                    target=app.target,
                    category=first_category,
                    type=app.type,
                )

        if self._selected_category and self._selected_category.id == category_id:
            self._selected_category = self._categories[0] if self._categories else None

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
        for i, note in enumerate(self._notes):
            if note.id == updated_note.id:
                self._notes[i] = updated_note
                self._logger.info("UPDATE_NOTE: %s -> row=%s, col=%s", updated_note.id, updated_note.grid_row,
                                  updated_note.grid_col)
                self._persist_state()
                return

    def remove_note(self, note_id: str):
        self._notes = [note for note in self._notes if note.id != note_id]
        self._persist_state()

