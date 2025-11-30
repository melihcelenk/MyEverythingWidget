"""
Dialog management for main window
Handles all dialog operations for categories and apps
"""
import uuid

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMessageBox, QInputDialog, QFileDialog

from models.app_shortcut import AppShortcut
from models.category import AppCategory
from services.image_storage_service import ImageStorageService
from widgets.app_picker_dialog import AppPickerDialog
from widgets.icon_picker_dialog import IconPickerDialog
from window.models.note import Note, NoteType


class DialogManager:
    """Manages all dialogs for the application"""

    def __init__(self, parent, app_state):
        self._parent = parent
        self._app_state = app_state
        self._image_storage = ImageStorageService()

    # === Category Dialogs ===

    def show_add_category_dialog(self) -> bool:
        """Show dialog to add a new category. Returns True if category was added."""
        name, ok = QInputDialog.getText(
            self._parent, "Add Category", "Category name:"
        )

        if not ok or not name.strip():
            return False

        name = name.strip()

        if len(name) < 1:
            QMessageBox.warning(self._parent, "Error", "Category name cannot be empty")
            return False

        if any(c.name == name for c in self._app_state.categories):
            QMessageBox.warning(self._parent, "Error", f"Category '{name}' already exists")
            return False

        new_category = AppCategory(
            id=str(uuid.uuid4()),
            name=name,
            icon='📁'
        )

        try:
            self._app_state.add_category(new_category)
            QMessageBox.information(self._parent, "Success", f"Category '{name}' added successfully")
            return True
        except ValueError as e:
            QMessageBox.warning(self._parent, "Error", str(e))
            return False

    def show_edit_category_dialog(self, category: AppCategory) -> bool:
        """Show dialog to edit a category. Returns True if category was updated."""
        name, ok = QInputDialog.getText(
            self._parent, "Edit Category", "Category name:", text=category.name
        )

        if not ok or not name.strip() or name.strip() == category.name:
            return False

        name = name.strip()

        if any(c.name == name and c.id != category.id for c in self._app_state.categories):
            QMessageBox.warning(self._parent, "Error", f"Category '{name}' already exists")
            return False

        updated_category = AppCategory(
            id=category.id,
            name=name,
            icon=category.icon
        )

        try:
            self._app_state.update_category(updated_category)
            QMessageBox.information(self._parent, "Success", f"Category updated to '{name}'")
            return True
        except ValueError as e:
            QMessageBox.warning(self._parent, "Error", str(e))
            return False

    def show_delete_category_dialog(self, category: AppCategory) -> bool:
        """Show confirmation and delete category. Returns True if deleted."""
        reply = QMessageBox.question(
            self._parent,
            "Delete Category",
            f"Are you sure you want to delete category '{category.name}'?\n\n"
            "Apps in this category will be moved to the first category.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return False

        try:
            self._app_state.remove_category(category.id)
            QMessageBox.information(self._parent, "Success", f"Category '{category.name}' deleted")
            return True
        except ValueError as e:
            QMessageBox.warning(self._parent, "Error", str(e))
            return False

    # === App Dialogs ===

    def show_add_app_dialog(self) -> bool:
        """Show dialog to add a new app. Returns True if app was added."""
        dialog = AppPickerDialog(self._parent)
        if dialog.exec():
            app = dialog.get_app()
            if app:
                self._app_state.add_app(app)
                QMessageBox.information(self._parent, "Success", f"{app.name} added successfully")
                return True
        return False

    def add_app_from_data(self, data: dict) -> bool:
        """Add app from data dict (name, target, icon_path). Returns True if added."""
        import uuid
        from models.app_shortcut import AppShortcut, LaunchType

        name = data.get("name", "").strip()
        target = data.get("path", "").strip()
        icon_path = data.get("icon_path", "")

        if not name or not target:
            return False

        # Determine launch type based on actual path
        from pathlib import Path as FilePath
        target_path = FilePath(target)

        if target.startswith(("http://", "https://")):
            launch_type = LaunchType.URL
        elif target_path.is_file():
            # It's a file - check if executable
            if target_path.suffix.lower() in ['.exe', '.bat', '.cmd', '.msi']:
                launch_type = LaunchType.EXE
            else:
                launch_type = LaunchType.EXE  # Try to run it anyway
        elif target_path.is_dir():
            launch_type = LaunchType.FOLDER
        elif target.endswith((".exe", ".bat", ".cmd")):
            launch_type = LaunchType.EXE
        else:
            launch_type = LaunchType.FOLDER

        # Get category from data or use first available
        category = data.get("category", "")
        if not category:
            categories = self._app_state.categories
            category = categories[0].name if categories else "General"

        app = AppShortcut(
            id=str(uuid.uuid4()),
            name=name,
            icon_path=icon_path,
            target=target,
            category=category,
            type=launch_type
        )

        self._app_state.add_app(app)
        return True

    def show_edit_app_dialog(self, app: AppShortcut) -> bool:
        """Show dialog to edit an app. Returns True if app was updated."""
        dialog = AppPickerDialog(self._parent, editing_app=app)
        if dialog.exec():
            updated_app = dialog.get_app()
            if updated_app:
                self._app_state.update_app(updated_app)
                QMessageBox.information(self._parent, "Success", f"{updated_app.name} updated successfully")
                return True
        return False

    def show_rename_app_dialog(self, app: AppShortcut) -> bool:
        """Show dialog to rename an app. Returns True if renamed."""
        new_name, ok = QInputDialog.getText(
            self._parent, "Rename Application", "App Name:", text=app.name
        )

        if not ok or not new_name or new_name == app.name:
            return False

        updated_app = AppShortcut(
            id=app.id,
            name=new_name,
            icon_path=app.icon_path,
            target=app.target,
            category=app.category,
            type=app.type,
        )
        self._app_state.update_app(updated_app)
        QMessageBox.information(self._parent, "Success", f"Renamed to {new_name}")
        return True

    def show_delete_app_dialog(self, app: AppShortcut) -> bool:
        """Show confirmation and delete app. Returns True if deleted."""
        reply = QMessageBox.question(
            self._parent,
            "Delete Application",
            f"Are you sure you want to delete '{app.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return False

        self._app_state.remove_app(app.id)
        QMessageBox.information(self._parent, "Success", f"'{app.name}' deleted")
        return True

    def show_change_icon_dialog(self, app: AppShortcut) -> bool:
        """Show dialog to change app icon. Returns True if icon was changed."""
        dialog = IconPickerDialog(self._parent, current_icon=app.icon_path)
        if dialog.exec():
            result = dialog.get_result()
            if result:
                updated_app = AppShortcut(
                    id=app.id,
                    name=app.name,
                    icon_path=result.value,
                    target=app.target,
                    category=app.category,
                    type=app.type,
                )
                self._app_state.update_app(updated_app)
                QMessageBox.information(self._parent, "Success", "Icon updated successfully")
                return True
        return False

    # === Image Dialogs ===

    def show_add_image_dialog(self, category_name: str) -> bool:
        """Show file dialog to add an image. Returns True if image was added."""
        file_path, _ = QFileDialog.getOpenFileName(
            self._parent,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )

        if not file_path:
            return False

        # Load and validate image
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(self._parent, "Error", "Failed to load image")
            return False

        # Save to storage
        saved_path = self._image_storage.save_image(pixmap)
        if saved_path is None:
            QMessageBox.warning(self._parent, "Error", "Failed to save image")
            return False

        # Create note with image type
        note = Note(
            id=str(uuid.uuid4()),
            content=saved_path,
            type=NoteType.IMAGE,
            category=category_name
        )
        self._app_state.add_note(note)
        return True
