"""
Application card widget
Displays app icon and name in a clickable card with context menu
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMenu, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QTimer, Signal
from PySide6.QtGui import QPixmap, QIcon, QFont, QContextMenuEvent, QMouseEvent
from pathlib import Path
from models.app_shortcut import AppShortcut, LaunchType


class AppCard(QWidget):
    """Application card widget"""
    
    def __init__(self, app: AppShortcut, on_tap, on_edit=None,
                 on_rename=None, on_change_icon=None, parent=None):
        super().__init__(parent)
        self._app = app
        self._on_tap = on_tap
        self._on_edit = on_edit
        self._on_rename = on_rename
        self._on_change_icon = on_change_icon
        
        self.setFixedSize(90, 100)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Icon
        icon_widget = self._build_icon()
        layout.addWidget(icon_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Label
        label_widget = self._build_label()
        layout.addWidget(label_widget)
        
        # Set style
        self.setStyleSheet("""
            AppCard {
                background-color: transparent;
                border: none;
            }
            AppCard:hover {
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 8px;
            }
        """)
    
    def _build_icon(self) -> QWidget:
        """Build icon widget"""
        icon_widget = QLabel()
        icon_widget.setFixedSize(40, 40)
        icon_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Check if custom icon exists
        if self._app.icon_path:
            # Try emoji (single character or up to 2 chars)
            if len(self._app.icon_path) <= 2:
                icon_widget.setText(self._app.icon_path)
                icon_widget.setStyleSheet("""
                    QLabel {
                        background-color: rgba(33, 150, 243, 0.2);
                        border-radius: 10px;
                        font-size: 24px;
                    }
                """)
                return icon_widget
            
            # Try image file
            icon_file = Path(self._app.icon_path)
            if icon_file.exists() and icon_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.ico']:
                pixmap = QPixmap(str(icon_file))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon_widget.setPixmap(scaled_pixmap)
                    icon_widget.setStyleSheet("border-radius: 10px;")
                    return icon_widget
        
        # Fallback to default type-based icon
        icon_widget.setText(self._get_icon_for_type())
        icon_widget.setStyleSheet("""
            QLabel {
                background-color: #2196F3;
                border-radius: 10px;
                font-size: 20px;
                color: white;
            }
        """)
        return icon_widget
    
    def _build_label(self) -> QWidget:
        """Build label widget with tooltip support"""
        label = QLabel(self._app.name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setMaximumHeight(40)
        label.setStyleSheet("font-size: 11px;")
        
        # Check if text will overflow (simple heuristic)
        font_metrics = label.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self._app.name)
        max_width = 74  # 90px card - 16px padding
        
        if text_width > max_width * 2:  # More than 2 lines
            label.setToolTip(self._app.name)
            # Add tooltip delay (500ms)
            label.setToolTipDuration(500)
        
        return label
    
    def _get_icon_for_type(self) -> str:
        """Get icon for app type"""
        if self._app.type == LaunchType.EXE:
            return "📱"
        elif self._app.type == LaunchType.URL:
            return "🌐"
        elif self._app.type == LaunchType.FOLDER:
            return "📁"
        return "📱"
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_tap()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPos())
    
    def _show_context_menu(self, position):
        """Show context menu"""
        menu = QMenu(self)
        
        open_action = menu.addAction("Open")
        open_action.triggered.connect(self._on_tap)
        
        if self._on_change_icon:
            change_icon_action = menu.addAction("Change Icon")
            change_icon_action.triggered.connect(lambda: self._on_change_icon(self._app))
        
        if self._on_edit:
            edit_action = menu.addAction("Edit")
            edit_action.triggered.connect(lambda: self._on_edit(self._app))
        
        if self._on_rename:
            rename_action = menu.addAction("Rename")
            rename_action.triggered.connect(lambda: self._on_rename(self._app))
        
        menu.exec(position)

