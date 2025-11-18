"""
Add app button widget
Displays a circular floating button with + icon for adding new apps
"""
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon


class AddAppButton(QPushButton):
    """Add app button widget"""
    
    def __init__(self, on_tap, parent=None):
        super().__init__("+", parent)
        self._on_tap = on_tap
        
        self.setFixedSize(48, 48)
        self.setStyleSheet("""
            QPushButton {
                background-color: #81C784;
                border: none;
                border-radius: 24px;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
            QPushButton:pressed {
                background-color: #4CAF50;
            }
        """)
        
        self.clicked.connect(self._on_tap)

