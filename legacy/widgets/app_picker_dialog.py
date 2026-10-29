"""
App picker dialog
Allows user to add or edit an application with name, URL/path, and category
"""
import uuid
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFileDialog, QMessageBox, QFormLayout,
    QWidget, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from models.app_shortcut import AppShortcut, LaunchType
from widgets.icon_picker_dialog import IconPickerDialog, IconPickerResult, IconType


class AppPickerDialog(QDialog):
    """App picker dialog widget"""
    
    def __init__(self, parent=None, editing_app: AppShortcut = None):
        super().__init__(parent)
        self._editing_app = editing_app
        self._selected_icon = None
        self._selected_icon_type = None
        self._app_result = None
        
        self._init_ui()
        self._load_editing_data()
    
    def _init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Edit Application" if self._editing_app else "Add Application")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        form_layout = QFormLayout(content_widget)
        form_layout.setSpacing(16)
        
        # Icon selector
        icon_widget = self._create_icon_selector()
        form_layout.addRow("Icon:", icon_widget)
        
        # Name field
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g., Visual Studio Code")
        form_layout.addRow("App Name:", self._name_edit)
        
        # Target field with browse button
        target_layout = QHBoxLayout()
        self._target_edit = QLineEdit()
        self._target_edit.setPlaceholderText("https://example.com or C:\\App.exe")
        browse_button = QPushButton("Browse")
        browse_button.setToolTip("Browse")
        browse_button.clicked.connect(self._browse_file)
        target_layout.addWidget(self._target_edit)
        target_layout.addWidget(browse_button)
        form_layout.addRow("URL or Path:", target_layout)
        
        # Category dropdown
        self._category_combo = QComboBox()
        self._category_combo.addItems(['Web', 'Dev', 'Media', 'All'])
        form_layout.addRow("Category:", self._category_combo)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        save_button = QPushButton("Save" if self._editing_app else "Add")
        save_button.clicked.connect(self._submit)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
    
    def _create_icon_selector(self) -> QWidget:
        """Create icon selector widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon preview
        self._icon_preview = QLabel()
        self._icon_preview.setFixedSize(40, 40)
        self._icon_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_preview.setStyleSheet("""
            QLabel {
                background-color: #e0e0e0;
                border-radius: 6px;
                border: 1px solid #ccc;
            }
        """)
        self._update_icon_preview()
        
        # Icon label
        icon_label = QLabel("Click to change")
        icon_label.setStyleSheet("color: #666; font-size: 11px;")
        
        # Select button
        select_button = QPushButton("Select Icon")
        select_button.clicked.connect(self._select_icon)
        
        layout.addWidget(self._icon_preview)
        layout.addWidget(icon_label)
        layout.addStretch()
        layout.addWidget(select_button)
        
        return widget
    
    def _update_icon_preview(self):
        """Update icon preview"""
        if self._selected_icon and self._selected_icon_type:
            if self._selected_icon_type == IconType.EMOJI:
                self._icon_preview.setText(self._selected_icon)
                self._icon_preview.setStyleSheet("""
                    QLabel {
                        background-color: rgba(33, 150, 243, 0.2);
                        border-radius: 6px;
                        border: 1px solid #ccc;
                        font-size: 24px;
                    }
                """)
            elif self._selected_icon_type == IconType.IMAGE:
                icon_file = Path(self._selected_icon)
                if icon_file.exists():
                    pixmap = QPixmap(str(icon_file))
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        self._icon_preview.setPixmap(scaled_pixmap)
            else:
                self._icon_preview.setText("📱")
        else:
            self._icon_preview.setText("📱")
            self._icon_preview.setStyleSheet("""
                QLabel {
                    background-color: #e0e0e0;
                    border-radius: 6px;
                    border: 1px solid #ccc;
                    font-size: 20px;
                }
            """)
    
    def _load_editing_data(self):
        """Load data if editing"""
        if self._editing_app:
            self._name_edit.setText(self._editing_app.name)
            self._target_edit.setText(self._editing_app.target)
            index = self._category_combo.findText(self._editing_app.category)
            if index >= 0:
                self._category_combo.setCurrentIndex(index)
            
            if self._editing_app.icon_path:
                self._selected_icon = self._editing_app.icon_path
                # Detect icon type
                if Path(self._editing_app.icon_path).exists():
                    self._selected_icon_type = IconType.IMAGE
                elif self._editing_app.icon_path.isdigit():
                    self._selected_icon_type = IconType.MATERIAL_ICON
                elif len(self._editing_app.icon_path) <= 2:
                    self._selected_icon_type = IconType.EMOJI
                self._update_icon_preview()
    
    def _browse_file(self):
        """Browse and select an executable file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Application",
            "",
            "Executable Files (*.exe *.lnk *.bat *.cmd);;All Files (*)"
        )
        
        if file_path:
            self._target_edit.setText(file_path)
            
            # Auto-fill app name from file name if empty
            if not self._name_edit.text():
                file_name = self._extract_file_name(file_path)
                self._name_edit.setText(file_name)
    
    def _extract_file_name(self, file_path: str) -> str:
        """Extract clean file name from path"""
        file = Path(file_path)
        file_name = file.stem
        
        # Clean up common patterns
        return self._clean_file_name(file_name)
    
    def _clean_file_name(self, name: str) -> str:
        """Clean up file name for display"""
        return name.replace('_', ' ').replace('-', ' ').strip().title()
    
    def _select_icon(self):
        """Show icon picker dialog"""
        dialog = IconPickerDialog(self, current_icon=self._selected_icon)
        if dialog.exec():
            result = dialog.get_result()
            if result:
                self._selected_icon = result.value
                self._selected_icon_type = result.type
                self._update_icon_preview()
    
    def _detect_launch_type(self, target: str) -> LaunchType:
        """Detect launch type from target"""
        if target.startswith('http://') or target.startswith('https://'):
            return LaunchType.URL
        return LaunchType.EXE
    
    def _submit(self):
        """Submit form"""
        name = self._name_edit.text().strip()
        target = self._target_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter app name")
            return
        
        if not target:
            QMessageBox.warning(self, "Error", "Please enter URL or path")
            return
        
        app_id = self._editing_app.id if self._editing_app else str(uuid.uuid4())
        
        self._app_result = AppShortcut(
            id=app_id,
            name=name,
            icon_path=self._selected_icon or (self._editing_app.icon_path if self._editing_app else ''),
            target=target,
            category=self._category_combo.currentText(),
            type=self._detect_launch_type(target),
        )
        
        self.accept()
    
    def get_app(self) -> AppShortcut:
        """Get the created/edited app"""
        return self._app_result

