"""
AddItemDialog - Unified dialog for adding App, Note, or Image.

Uses StyledTabWidget for consistent tab appearance.
"""
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QWidget, QLabel, QPushButton,
    QHBoxLayout, QLineEdit, QTextEdit, QFileDialog
)

from widgets.icon_picker_dialog import IconPickerDialog
from widgets.styled_tab_widget import StyledTabWidget

if TYPE_CHECKING:
    pass


class AddItemDialog(QDialog):
    """Dialog with tabs for adding App, Note, or Image."""

    # Signals emitted when items are added
    appAdded = Signal(dict)  # {name, path, ...}
    noteAdded = Signal(str)  # note content
    imageAdded = Signal(str)  # image path

    def __init__(self, category_name: str, parent=None):
        super().__init__(parent)
        self._category_name = category_name

        self._setup_ui()
        self._setup_window()

    def _setup_window(self):
        """Configure dialog window."""
        self.setWindowTitle("Add Item")
        self.setMinimumWidth(320)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint
        )

    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab widget with compact styling
        self._tab_widget = StyledTabWidget(compact=True)

        # Add tabs
        self._app_tab = self._create_app_tab()
        self._note_tab = self._create_note_tab()
        self._image_tab = self._create_image_tab()

        self._tab_widget.addTab(self._app_tab, "📱 App")
        self._tab_widget.addTab(self._note_tab, "📝 Note")
        self._tab_widget.addTab(self._image_tab, "🖼️ Image")

        layout.addWidget(self._tab_widget)

    def _create_app_tab(self) -> QWidget:
        """Create the App tab content."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Name input
        name_label = QLabel("App Name:")
        self._app_name_input = QLineEdit()
        self._app_name_input.setPlaceholderText("Enter app name...")
        layout.addWidget(name_label)
        layout.addWidget(self._app_name_input)

        # Path input with browse button
        path_label = QLabel("Path / URL:")
        path_row = QHBoxLayout()
        self._app_path_input = QLineEdit()
        self._app_path_input.setPlaceholderText("Path to executable or URL...")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_app_path)
        path_row.addWidget(self._app_path_input)
        path_row.addWidget(browse_btn)
        layout.addWidget(path_label)
        layout.addLayout(path_row)

        # Icon selection
        icon_label = QLabel("Icon:")
        icon_row = QHBoxLayout()
        self._app_icon_path = ""
        self._app_icon_preview = QLabel("📱")
        self._app_icon_preview.setStyleSheet("font-size: 24px;")
        icon_btn = QPushButton("Change Icon...")
        icon_btn.clicked.connect(self._pick_icon)
        icon_row.addWidget(self._app_icon_preview)
        icon_row.addWidget(icon_btn)
        icon_row.addStretch()
        layout.addWidget(icon_label)
        layout.addLayout(icon_row)

        layout.addStretch()

        # Add button
        add_btn = QPushButton("Add App")
        add_btn.setStyleSheet(self._get_add_button_style())
        add_btn.clicked.connect(self._on_add_app)
        layout.addWidget(add_btn)

        return widget

    def _create_note_tab(self) -> QWidget:
        """Create the Note tab content."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Note content
        content_label = QLabel("Note Content:")
        self._note_content_input = QTextEdit()
        self._note_content_input.setPlaceholderText("Enter your note...")
        self._note_content_input.setMinimumHeight(100)
        layout.addWidget(content_label)
        layout.addWidget(self._note_content_input)

        layout.addStretch()

        # Add button
        add_btn = QPushButton("Add Note")
        add_btn.setStyleSheet(self._get_add_button_style())
        add_btn.clicked.connect(self._on_add_note)
        layout.addWidget(add_btn)

        return widget

    def _create_image_tab(self) -> QWidget:
        """Create the Image tab content."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Image selection
        self._image_path_label = QLabel("No image selected")
        self._image_path_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self._image_path_label)

        # Browse button
        browse_btn = QPushButton("📁 Select Image...")
        browse_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                font-size: 14px;
            }
        """)
        browse_btn.clicked.connect(self._browse_image)
        layout.addWidget(browse_btn)

        # Or paste hint
        paste_hint = QLabel("Or paste from clipboard (Ctrl+V)")
        paste_hint.setStyleSheet("color: #999; font-size: 11px;")
        paste_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(paste_hint)

        layout.addStretch()

        # Add button
        self._add_image_btn = QPushButton("Add Image")
        self._add_image_btn.setStyleSheet(self._get_add_button_style())
        self._add_image_btn.setEnabled(False)
        self._add_image_btn.clicked.connect(self._on_add_image)
        layout.addWidget(self._add_image_btn)

        self._selected_image_path = None

        return widget

    def _get_add_button_style(self) -> str:
        """Get stylesheet for add buttons."""
        return """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """

    def _browse_app_path(self):
        """Open file browser for app path."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Application",
            "", "Executables (*.exe);;All Files (*.*)"
        )
        if path:
            self._app_path_input.setText(path)
            if not self._app_name_input.text():
                # Auto-fill name from filename
                import os
                name = os.path.splitext(os.path.basename(path))[0]
                self._app_name_input.setText(name)

    def _pick_icon(self):
        """Open icon picker dialog."""
        dialog = IconPickerDialog(self, current_icon=self._app_icon_path)
        if dialog.exec():
            result = dialog.get_result()
            if result:
                self._app_icon_path = result.value
                # Show emoji or image indicator
                if result.type.value == "image":
                    self._app_icon_preview.setText("🖼️")
                else:
                    self._app_icon_preview.setText(result.value)

    def _browse_image(self):
        """Open file browser for image."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image",
            "", "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;All Files (*.*)"
        )
        if path:
            self._selected_image_path = path
            self._image_path_label.setText(f"Selected: {path.split('/')[-1]}")
            self._image_path_label.setStyleSheet("color: #333;")
            self._add_image_btn.setEnabled(True)

    def _on_add_app(self):
        """Handle add app button click."""
        name = self._app_name_input.text().strip()
        path = self._app_path_input.text().strip()
        icon_path = getattr(self, '_app_icon_path', '')

        if name and path:
            self.appAdded.emit({
                "name": name,
                "path": path,
                "icon_path": icon_path
            })
            self.accept()

    def _on_add_note(self):
        """Handle add note button click."""
        content = self._note_content_input.toPlainText().strip()

        if content:
            self.noteAdded.emit(content)
            self.accept()

    def _on_add_image(self):
        """Handle add image button click."""
        if self._selected_image_path:
            self.imageAdded.emit(self._selected_image_path)
            self.accept()

    @property
    def category_name(self) -> str:
        """Get the target category name."""
        return self._category_name

    def select_tab(self, tab_name: str):
        """Select a tab by name (app, note, image)."""
        tab_map = {"app": 0, "note": 1, "image": 2}
        if tab_name.lower() in tab_map:
            self._tab_widget.setCurrentIndex(tab_map[tab_name.lower()])
