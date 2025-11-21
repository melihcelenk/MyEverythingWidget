"""
Main application window
Manages window state and displays primary content
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox, QPushButton
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent, QKeyEvent
from window.app_state import AppState
from window.tab_manager import TabManager
from window.dialog_manager import DialogManager
from window.models.note import Note, NoteType
from services.app_launcher_service import AppLauncherService
from services.clipboard_service import ClipboardService
from services.image_storage_service import ImageStorageService
from widgets.custom_title_bar import CustomTitleBar
from widgets.add_app_button import AddAppButton
from models.app_shortcut import AppShortcut
import uuid


class MainWindow(QMainWindow):
    """Main application window"""

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

        # Floating add image button
        self._add_image_button = QPushButton("🖼️", central_widget)
        self._add_image_button.setFixedSize(40, 40)
        self._add_image_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self._add_image_button.clicked.connect(self._on_add_image_clicked)
        self._add_image_button.raise_()

        # Floating add app button
        self._add_button = AddAppButton(
            on_tap=lambda: self._dialog_manager.show_add_app_dialog()
        )
        self._add_button.setParent(central_widget)
        self._add_button.raise_()

    def _setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("My Everything Widget")
        self.setFixedSize(320, 500)
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
        """Handle tab change"""
        if 0 <= index < len(self._app_state.categories):
            category = self._app_state.categories[index]
            self._app_state.select_category(category)

    def _on_add_category(self):
        """Handle add category button click"""
        if self._dialog_manager.show_add_category_dialog():
            self._tab_widget.setCurrentIndex(len(self._app_state.categories) - 1)

    def _on_add_image_clicked(self):
        """Handle add image button click"""
        current_index = self._tab_widget.currentIndex()
        category_name = self._app_state.categories[0].name if self._app_state.categories else "Web"
        if 0 <= current_index < len(self._app_state.categories):
            category_name = self._app_state.categories[current_index].name
        self._dialog_manager.show_add_image_dialog(category_name)

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
        """Handle window resize to position floating buttons"""
        super().resizeEvent(event)
        if hasattr(self, '_add_button'):
            self._add_button.move(self.width() - 64, self.height() - 64)
        if hasattr(self, '_add_image_button'):
            # Position above add app button
            self._add_image_button.move(self.width() - 54, self.height() - 114)

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

        # Get current category
        current_index = self._tab_widget.currentIndex()
        category_name = self._app_state.categories[0].name if self._app_state.categories else "Web"
        if 0 <= current_index < len(self._app_state.categories):
            category_name = self._app_state.categories[current_index].name

        # Create note with image type
        note = Note(
            id=str(uuid.uuid4()),
            content=file_path,
            type=NoteType.IMAGE,
            category=category_name
        )
        self._app_state.add_note(note)
