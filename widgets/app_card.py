"""
Application card widget
Displays app icon and name in a clickable card with context menu
"""
from pathlib import Path

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QMenu, QSizePolicy
)

from models.app_shortcut import AppShortcut, LaunchType
from widgets.draggable_mixin import DraggableMixin


class AppCard(QWidget, DraggableMixin):
    """Application card widget"""

    # Signals for drag-drop
    itemDropped = Signal(str, str)  # item_id, target_item_id

    def __init__(self, app: AppShortcut, on_tap, on_edit=None,
                 on_rename=None, on_change_icon=None, on_delete=None, parent=None):
        super().__init__(parent)
        self._app = app
        self._on_tap = on_tap
        self._on_edit = on_edit
        self._on_rename = on_rename
        self._on_change_icon = on_change_icon
        self._on_delete = on_delete

        self.setFixedSize(90, 100)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Initialize drag-drop
        self.init_draggable(app.id, "app")

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
        
        # Set style with modern hover and click effects
        self.setStyleSheet("""
            AppCard {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
            }
            AppCard:hover {
                background-color: rgba(0, 0, 0, 0.08);
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }
        """)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        self._is_pressed = False
    
    def _build_icon(self) -> QWidget:
        """Build icon widget"""
        icon_widget = QLabel()
        icon_widget.setFixedSize(QSize(40, 40))
        icon_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Check if custom icon exists
        if self._app.icon_path and isinstance(self._app.icon_path, str) and len(self._app.icon_path) > 0:
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
            try:
                icon_file = Path(self._app.icon_path)
                if icon_file.exists() and icon_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.ico']:
                    pixmap = QPixmap(str(icon_file))
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(QSize(40, 40), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        icon_widget.setPixmap(scaled_pixmap)
                        icon_widget.setStyleSheet("border-radius: 10px;")
                        return icon_widget
            except (ValueError, OSError, TypeError):
                # Invalid path or file error, fall through to default icon
                pass
        
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
    
    def enterEvent(self, event):
        """Handle mouse enter - enhance hover effect"""
        super().enterEvent(event)
        # Add subtle scale effect via style
        self.setStyleSheet("""
            AppCard {
                background-color: rgba(0, 0, 0, 0.08);
                border: 1px solid rgba(0, 0, 0, 0.15);
                border-radius: 8px;
            }
        """)
    
    def leaveEvent(self, event):
        """Handle mouse leave - reset style"""
        super().leaveEvent(event)
        if not self._is_pressed:
            self.setStyleSheet("""
                AppCard {
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 8px;
                }
            """)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press with visual feedback"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.handle_drag_mouse_press(event)
            # Visual feedback: darker background
            self.setStyleSheet("""
                AppCard {
                    background-color: rgba(0, 0, 0, 0.15);
                    border: 1px solid rgba(0, 0, 0, 0.2);
                    border-radius: 8px;
                }
            """)
            event.accept()  # Prevent event from propagating to parent (window)
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPos())
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for drag detection"""
        if self.handle_drag_mouse_move(event, self):
            self._is_pressed = False
            event.accept()
            return
        event.accept()  # Always accept to prevent window dragging
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release - reset pressed state"""
        super().mouseReleaseEvent(event)
        if self._is_pressed:
            self._is_pressed = False
            # Execute tap on release (not drag)
            if event.button() == Qt.MouseButton.LeftButton:
                self._execute_tap()
            # Reset to hover state if mouse is still over
            if self.rect().contains(event.pos()):
                self.setStyleSheet("""
                    AppCard {
                        background-color: rgba(0, 0, 0, 0.08);
                        border: 1px solid rgba(0, 0, 0, 0.15);
                        border-radius: 8px;
                    }
                """)
            else:
                self.setStyleSheet("""
                    AppCard {
                        background-color: transparent;
                        border: 1px solid transparent;
                        border-radius: 8px;
                    }
                """)

    def dragEnterEvent(self, event):
        """Handle drag enter"""
        self.handle_drag_enter(event)

    def dragLeaveEvent(self, event):
        """Handle drag leave"""
        self.handle_drag_leave(event)

    def dropEvent(self, event):
        """Handle drop"""
        # Extract dragged item info from drop event
        item_type, item_id = self.handle_drop(event, 0)  # index not used
        if item_type and item_id:
            # Emit signal with dragged item ID and this card's ID (target)
            self.itemDropped.emit(item_id, self._app.id)
    
    def _execute_tap(self):
        """Execute tap callback"""
        self._on_tap()
    
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

        if self._on_delete:
            menu.addSeparator()
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self._on_delete(self._app))

        menu.exec(position)

