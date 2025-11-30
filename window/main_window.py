"""
Main application window
Manages window state and displays primary content
"""
import uuid

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent, QKeyEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox, QPushButton

from models.app_shortcut import AppShortcut
from services.app_launcher_service import AppLauncherService
from services.clipboard_service import ClipboardService
from services.image_storage_service import ImageStorageService
from widgets.add_item_dialog import AddItemDialog
from widgets.custom_title_bar import CustomTitleBar
from window.app_state import AppState
from window.dialog_manager import DialogManager
from window.grid.constants import TOTAL_WIDTH, TOTAL_HEIGHT
from window.models.note import Note, NoteType
from window.tab_manager import TabManager


class MainWindow(QMainWindow):
    """Main application window"""

    # Floating action button dimensions
    FAB_SIZE = 40
    FAB_MARGIN = 12  # Margin from window edge

    def __init__(self):
        super().__init__()
        self._is_always_on_top = True
        self._app_state = AppState()
        self._launcher_service = AppLauncherService()
        self._drag_position = QPoint()

        self._clipboard_service = ClipboardService()
        self._image_storage = ImageStorageService()

        self._init_managers()
        self._init_ui()
        self._setup_window()
        self._connect_signals()

    def _init_managers(self):
        """Initialize manager objects"""
        self._dialog_manager = DialogManager(self, self._app_state)
        self._tab_manager = TabManager(
            app_state=self._app_state,
            on_app_tap=self._launch_app,
            on_app_edit=lambda app: self._dialog_manager.show_edit_app_dialog(app),
            on_app_rename=lambda app: self._dialog_manager.show_rename_app_dialog(app),
            on_app_change_icon=lambda app: self._dialog_manager.show_change_icon_dialog(app),
            on_app_delete=lambda app: self._dialog_manager.show_delete_app_dialog(app),
            on_add_category=self._on_add_category,
            on_edit_category=lambda cat: self._dialog_manager.show_edit_category_dialog(cat),
            on_delete_category=lambda cat: self._dialog_manager.show_delete_category_dialog(cat),
        )

    def _init_ui(self):
        """Initialize UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        self._title_bar = CustomTitleBar(
            title="My Everything",
            is_always_on_top=self._is_always_on_top,
            on_always_on_top_toggle=self._toggle_always_on_top,
            on_close=self.close,
        )
        layout.addWidget(self._title_bar)

        # Tab widget
        self._tab_widget = self._tab_manager.create_tab_widget()
        layout.addWidget(self._tab_widget)

        # Floating add button (unified: App/Note/Image)
        self._add_button = QPushButton("+", central_widget)
        self._add_button.setFixedSize(self.FAB_SIZE, self.FAB_SIZE)
        border_radius = self.FAB_SIZE // 2
        self._add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: {border_radius}px;
                font-size: 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
            QPushButton:pressed {{
                background-color: #1565C0;
            }}
        """)
        self._add_button.clicked.connect(self._on_add_button_clicked)
        self._add_button.raise_()

    def _setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("My Everything Widget")
        # Window size based on grid constants + extra for title bar and padding
        window_width = TOTAL_WIDTH + 10  # Small padding
        window_height = TOTAL_HEIGHT + 100  # Title bar + quick note entry
        self.setFixedSize(window_width, window_height)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

    def _connect_signals(self):
        """Connect signals"""
        self._app_state.state_changed.connect(self._on_state_changed)
        self._tab_widget.currentChanged.connect(self._on_tab_changed)

    # === Event Handlers ===

    def _on_state_changed(self):
        """Handle app state changes"""
        current_index = self._tab_widget.currentIndex()
        current_category_id = None

        if 0 <= current_index < len(self._app_state.categories):
            current_category_id = self._app_state.categories[current_index].id

        self._tab_widget.blockSignals(True)
        try:
            self._tab_manager.update_tabs()

            if current_category_id:
                for i, category in enumerate(self._app_state.categories):
                    if category.id == current_category_id:
                        self._tab_widget.setCurrentIndex(i)
                        break
            elif self._tab_widget.count() > 1:
                self._tab_widget.setCurrentIndex(0)
            self._tab_manager.refresh_notes_tab()
        finally:
            self._tab_widget.blockSignals(False)

    def _on_tab_changed(self, index):
        """Handle tab change - no state update needed, just track selection"""
        # Don't call select_category here as it triggers state_changed
        # which causes update_tabs() and recreates all widgets (memory leak)
        pass

    def _on_add_category(self):
        """Handle add category button click"""
        if self._dialog_manager.show_add_category_dialog():
            self._tab_widget.setCurrentIndex(len(self._app_state.categories) - 1)

    def _on_add_button_clicked(self):
        """Handle unified add button click - show AddItemDialog."""
        category_name = self._get_current_category_name()
        if not category_name:
            return

        dialog = AddItemDialog(category_name, self)
        dialog.appAdded.connect(self._on_app_added)
        dialog.noteAdded.connect(self._on_note_added)
        dialog.imageAdded.connect(self._on_image_added)
        dialog.exec()

    def _on_app_added(self, data: dict):
        """Handle app added from dialog."""
        category_name = self._get_current_category_name()
        if category_name:
            data["category"] = category_name
            self._dialog_manager.add_app_from_data(data)

    def _on_note_added(self, content: str):
        """Handle note added from dialog."""
        category_name = self._get_current_category_name()
        if category_name:
            note = Note(
                id=str(uuid.uuid4()),
                content=content,
                type=NoteType.TEXT,
                category=category_name
            )
            self._app_state.add_note(note)

    def _on_image_added(self, image_path: str):
        """Handle image added from dialog."""
        category_name = self._get_current_category_name()
        if category_name:
            self._add_image_from_path(image_path, category_name)

    def _get_current_category_name(self) -> str | None:
        """Get the name of the currently selected category."""
        if not self._app_state.categories:
            return None
        current_index = self._tab_widget.currentIndex()
        if 0 <= current_index < len(self._app_state.categories):
            return self._app_state.categories[current_index].name
        return self._app_state.categories[0].name

    # === Actions ===

    def _launch_app(self, app: AppShortcut):
        """Launch an application"""
        if not self._launcher_service.launch(app):
            QMessageBox.warning(self, "Error", f"Failed to launch {app.name}")

    def _toggle_always_on_top(self):
        """Toggle always on top"""
        self._is_always_on_top = not self._is_always_on_top
        if self._is_always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        self._title_bar.update_always_on_top(self._is_always_on_top)

    # === Window Events ===

    def resizeEvent(self, event):
        """Handle window resize to position floating button"""
        super().resizeEvent(event)
        # Position FAB at bottom-right corner
        fab_x = self.width() - self.FAB_SIZE - self.FAB_MARGIN
        fab_y = self.height() - self.FAB_SIZE - self.FAB_MARGIN

        if hasattr(self, '_add_button'):
            self._add_button.move(fab_x, fab_y)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events"""
        # Ctrl+V for paste
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
            self._handle_paste()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _handle_paste(self):
        """Handle paste from clipboard"""
        if not self._clipboard_service.has_image():
            return

        pixmap = self._clipboard_service.get_image()
        if pixmap is None:
            return

        # Save image to storage
        file_path = self._image_storage.save_image(pixmap)
        if file_path is None:
            QMessageBox.warning(self, "Error", "Failed to save image")
            return

        # Get current category and add image
        category_name = self._get_current_category_name()
        if category_name:
            self._add_image_note(file_path, category_name)

    def _add_image_from_path(self, image_path: str, category_name: str):
        """Add an image from file path (copy to storage first)."""
        from PySide6.QtGui import QPixmap

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Error", f"Failed to load image: {image_path}")
            return

        # Save to our storage
        file_path = self._image_storage.save_image(pixmap)
        if file_path is None:
            QMessageBox.warning(self, "Error", "Failed to save image")
            return

        self._add_image_note(file_path, category_name)

    def _add_image_note(self, file_path: str, category_name: str):
        """Create an image note in the given category."""
        note = Note(
            id=str(uuid.uuid4()),
            content=file_path,
            type=NoteType.IMAGE,
            category=category_name
        )
        self._app_state.add_note(note)
