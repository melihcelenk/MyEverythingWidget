"""
Custom draggable title bar with window controls
Features:
- Drag to move window
- Always-on-top toggle
- Close button
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QIcon, QMouseEvent


class CustomTitleBar(QWidget):
    """Custom title bar widget"""
    
    def __init__(self, title: str, is_always_on_top: bool,
                 on_always_on_top_toggle, on_close, parent=None):
        super().__init__(parent)
        self._title = title
        self._is_always_on_top = is_always_on_top
        self._on_always_on_top_toggle = on_always_on_top_toggle
        self._on_close = on_close
        self._drag_position = QPoint()
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        self.setFixedHeight(40)
        self.setStyleSheet("""
            CustomTitleBar {
                background-color: #e3f2fd;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 4, 0)
        layout.setSpacing(0)
        
        # Title
        title_label = QLabel(self._title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Always on top button
        self._pin_button = QPushButton()
        self._pin_button.setFixedSize(32, 32)
        self._pin_button.setToolTip("Always on top")
        self._pin_button.clicked.connect(self._on_always_on_top_toggle)
        self._update_pin_button()
        layout.addWidget(self._pin_button)
        
        # Close button
        close_button = QPushButton("✕")
        close_button.setFixedSize(32, 32)
        close_button.setToolTip("Close")
        close_button.clicked.connect(self._on_close)
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
        layout.addWidget(close_button)
    
    def _update_pin_button(self):
        """Update pin button icon"""
        if self._is_always_on_top:
            self._pin_button.setText("📌")
        else:
            self._pin_button.setText("📍")
        self._pin_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
    
    def update_always_on_top(self, is_always_on_top: bool):
        """Update always on top state"""
        self._is_always_on_top = is_always_on_top
        self._update_pin_button()

