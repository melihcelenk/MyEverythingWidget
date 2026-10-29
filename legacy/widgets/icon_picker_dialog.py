"""
Notion-style icon picker dialog
Allows selecting emoji, material icons, or uploading custom images
"""
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QGridLayout, QScrollArea,
    QFileDialog, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont
from dataclasses import dataclass
from enum import Enum


class IconType(Enum):
    """Icon type enumeration"""
    EMOJI = "emoji"
    MATERIAL_ICON = "materialIcon"
    IMAGE = "image"


@dataclass
class IconPickerResult:
    """Icon selection result"""
    type: IconType
    value: str


class IconPickerDialog(QDialog):
    """Icon picker dialog widget"""
    
    # Emoji list - commonly used emojis for app icons
    EMOJIS = [
        '📱', '💻', '🌐', '📁', '📝', '📊', '📈', '📉',
        '🎵', '🎮', '🎨', '🎬', '📷', '📹', '🎤', '🎧',
        '⚙️', '🔧', '🔨', '🛠️', '⚡', '🔥', '💡', '🔒',
        '📧', '💬', '📞', '🌟', '⭐', '❤️', '💚',
        '🚀', '✈️', '🚗', '🚲', '⚽', '🏀', '🎯', '🎲',
        '☀️', '🌙', '🌈', '🔔', '🎁', '🏆', '👍',
    ]
    
    def __init__(self, parent=None, current_icon: str = None):
        super().__init__(parent)
        self._current_icon = current_icon
        self._result = None
        self._search_query = ""
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Select Icon")
        self.setFixedSize(650, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Select Icon")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        close_button = QPushButton("✕")
        close_button.setFixedSize(32, 32)
        close_button.clicked.connect(self.reject)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #ff5252;
                color: white;
            }
        """)
        header_layout.addWidget(close_button)
        layout.addLayout(header_layout)
        
        # Search bar
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Filter...")
        self._search_edit.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_edit)
        
        # Tab widget
        self._tab_widget = QTabWidget()
        self._tab_widget.addTab(self._create_emoji_tab(), "Emoji")
        self._tab_widget.addTab(self._create_icon_tab(), "Icons")
        self._tab_widget.addTab(self._create_upload_tab(), "Upload")
        layout.addWidget(self._tab_widget)
    
    def _create_emoji_tab(self) -> QWidget:
        """Create emoji tab"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        grid_layout = QGridLayout(content_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(8, 8, 8, 8)
        
        # Add emoji buttons (filtered by search query if any)
        filtered_emojis = self._get_filtered_emojis()
        row = 0
        col = 0
        for emoji in filtered_emojis:
            button = QPushButton(emoji)
            button.setFixedSize(60, 60)
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.05);
                    border: 1px solid red;
                    border-radius: 6px;
                    font-size: 40px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.1);
                }
            """)
            button.clicked.connect(lambda checked, e=emoji: self._select_emoji(e))
            grid_layout.addWidget(button, row, col)
            col += 1
            if col >= 6:
                col = 0
                row += 1
        
        scroll_area.setWidget(content_widget)
        return scroll_area
    
    def _create_icon_tab(self) -> QWidget:
        """Create material icon tab"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        grid_layout = QGridLayout(content_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(8, 8, 8, 8)
        
        # Material icons (using emoji representation for simplicity)
        icons = ['📱', '🌐', '📁', '📝', '⚙️', '🏠', '💼', '🎓',
                 '🎵', '🎬', '🖼️', '📷', '📧', '💬', '📞',
                 '❤️', '⭐', '🛒', '💳', '📊', '📈', '📉', '📅',
                 '⏰', '⏱️', '☁️', '⬇️', '⬆️', '🔗', '✏️', '🗑️',
                 '➕', '➖', '🔍', '🔽', '🔼', '📋', '🔔', '🔖',
                 '🚩', '🏷️']
        
        row = 0
        col = 0
        for icon in icons:
            button = QPushButton(icon)
            button.setFixedSize(60, 60)
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.05);
                    border: 1px solid red;
                    border-radius: 6px;
                    font-size: 24px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.1);
                }
            """)
            button.clicked.connect(lambda checked, i=icon: self._select_material_icon(i))
            grid_layout.addWidget(button, row, col)
            col += 1
            if col >= 6:
                col = 0
                row += 1
        
        scroll_area.setWidget(content_widget)
        return scroll_area
    
    def _create_upload_tab(self) -> QWidget:
        """Create upload tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        upload_widget = QWidget()
        upload_layout = QVBoxLayout(upload_widget)
        upload_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_layout.setSpacing(12)
        
        # Upload icon
        upload_label = QLabel("☁️")
        upload_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_label.setStyleSheet("font-size: 48px;")
        upload_layout.addWidget(upload_label)
        
        # Title
        title_label = QLabel("Upload Custom Icon")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        upload_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Drag & drop an image or click to browse")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("color: #666; font-size: 12px;")
        upload_layout.addWidget(desc_label)
        
        # Browse button
        browse_button = QPushButton("Choose File")
        browse_button.clicked.connect(self._upload_image)
        browse_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        upload_layout.addWidget(browse_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        upload_widget.setStyleSheet("""
            QWidget {
                border: 1px solid #ccc;
                border-radius: 12px;
                padding: 24px;
            }
        """)
        
        layout.addWidget(upload_widget)
        return widget
    
    def _on_search_changed(self, text: str):
        """Handle search query change"""
        self._search_query = text.lower()
        # Note: For simplicity, search filtering is not implemented
        # Future enhancement: rebuild tabs on search change

    def _get_filtered_emojis(self):
        """Get emojis filtered by search query"""
        if self._search_query:
            return [e for e in self.EMOJIS if self._search_query in e]
        return self.EMOJIS
    
    def _select_emoji(self, emoji: str):
        """Handle emoji selection"""
        self._result = IconPickerResult(type=IconType.EMOJI, value=emoji)
        self.accept()
    
    def _select_material_icon(self, icon: str):
        """Handle material icon selection"""
        # For simplicity, using emoji representation
        # In real implementation, would use icon code points
        self._result = IconPickerResult(type=IconType.EMOJI, value=icon)
        self.accept()
    
    def _upload_image(self):
        """Handle image upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Icon Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.webp);;All Files (*)"
        )
        
        if file_path:
            icon_file = Path(file_path)
            if icon_file.exists():
                self._result = IconPickerResult(type=IconType.IMAGE, value=file_path)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "File not found")
    
    def get_result(self) -> IconPickerResult:
        """Get the selected icon result"""
        return self._result

