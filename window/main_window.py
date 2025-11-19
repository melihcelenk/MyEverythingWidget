"""
Main application window
Manages window state and displays primary content
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTabBar,
    QScrollArea, QGridLayout, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QPoint, Signal, QSize
from PySide6.QtGui import QMouseEvent, QKeyEvent
from window.app_state import AppState
from services.app_launcher_service import AppLauncherService
from widgets.custom_title_bar import CustomTitleBar
from widgets.app_card import AppCard
from widgets.add_app_button import AddAppButton
from widgets.app_picker_dialog import AppPickerDialog
from widgets.icon_picker_dialog import IconPickerDialog, IconPickerResult
from models.app_shortcut import AppShortcut


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self._is_always_on_top = True
        self._app_state = AppState()
        self._launcher_service = AppLauncherService()
        self._drag_position = QPoint()
        
        self._init_ui()
        self._setup_window()
        self._connect_signals()
    
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
        
        # Tab widget with modern styling
        self._tab_widget = QTabWidget()
        self._tab_widget.setTabsClosable(False)
        self._tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-top: none;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                color: #666;
                border: 1px solid #ddd;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:hover {
                background-color: #e8e8e8;
                color: #333;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2196F3;
                border-bottom: 2px solid #2196F3;
                font-weight: bold;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            QTabBar::tab:last-child {
                min-width: 30px;
                max-width: 30px;
                padding: 8px 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self._tab_widget)
        
        # Connect tab bar signals for context menu and add button
        tab_bar = self._tab_widget.tabBar()
        tab_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self._on_tab_context_menu)
        tab_bar.tabBarClicked.connect(self._on_tab_bar_clicked)
        
        # Create tabs for each category
        self._category_tabs = {}
        self._category_grids = {}
        self._update_tabs()
        
        # Set default tab
        self._tab_widget.setCurrentIndex(0)
        
        # Add floating add button
        self._add_button = AddAppButton(on_tap=self._show_add_app_dialog)
        self._add_button.setParent(central_widget)
        self._add_button.raise_()
    
    def _create_category_tab(self, category):
        """Create a tab content widget for a category"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Align scroll area content to top-left (not centered)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        # Grid layout for app cards
        grid_layout = QGridLayout(content_widget)
        grid_layout.setSpacing(4)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        # Align items to top-left (not centered)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Add app cards
        self._update_category_tab(category, grid_layout)
        
        return scroll_area, grid_layout
    
    def _update_category_tab(self, category, layout):
        """Update category tab with app cards"""
        # Clear existing widgets
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Filter apps by category
        if category.name == 'All':
            apps = self._app_state.apps
        else:
            apps = [app for app in self._app_state.apps if app.category == category.name]
        
        # Add app cards in grid (3 columns)
        # Cards start from top-left, fill left to right, top to bottom
        row = 0
        col = 0
        for app in apps:
            app_card = AppCard(
                app=app,
                on_tap=lambda a=app: self._launch_app(a),
                on_edit=lambda a=app: self._edit_app(a),
                on_rename=lambda a=app: self._rename_app(a),
                on_change_icon=lambda a=app: self._change_icon(a),
            )
            # Add widget with alignment to top-left
            layout.addWidget(app_card, row, col, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Note: Add button will be positioned in main window layout
    
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
    
    def _update_tabs(self):
        """Update tabs based on current categories"""
        # Clear existing tabs
        while self._tab_widget.count() > 0:
            self._tab_widget.removeTab(0)
        
        self._category_tabs = {}
        self._category_grids = {}
        
        # Add category tabs
        for category in self._app_state.categories:
            tab_content, grid_layout = self._create_category_tab(category)
            self._tab_widget.addTab(tab_content, f"{category.icon} {category.name}")
            self._category_tabs[category.id] = tab_content
            self._category_grids[category.id] = grid_layout
        
        # Add "+" tab at the end (narrower than other tabs)
        add_tab_widget = QWidget()
        add_tab_widget.setFixedHeight(0)  # Hidden content
        self._tab_widget.addTab(add_tab_widget, "+")
        
        # Style the add tab to be narrower
        tab_bar = self._tab_widget.tabBar()
        add_tab_index = self._tab_widget.count() - 1
        tab_bar.setTabButton(add_tab_index, QTabBar.ButtonPosition.LeftSide, None)
        tab_bar.setTabButton(add_tab_index, QTabBar.ButtonPosition.RightSide, None)
        
        # Apply custom styling to add tab
        self._tab_widget.setStyleSheet(self._tab_widget.styleSheet() + """
            QTabBar::tab:last-child {
                min-width: 30px;
                max-width: 30px;
                padding: 8px 8px;
            }
        """)
    
    def _on_state_changed(self):
        """Handle app state changes"""
        # Get current selected tab index before updating
        current_index = self._tab_widget.currentIndex()
        current_category_id = None

        # Find current category ID (skip add button tab)
        if 0 <= current_index < len(self._app_state.categories):
            current_category = self._app_state.categories[current_index]
            current_category_id = current_category.id

        # Block signals to prevent recursive updates during tab recreation
        self._tab_widget.blockSignals(True)
        try:
            # Update tabs (recreate them)
            self._update_tabs()

            # Restore selection
            if current_category_id:
                for i, category in enumerate(self._app_state.categories):
                    if category.id == current_category_id:
                        self._tab_widget.setCurrentIndex(i)
                        break
            else:
                # If no valid selection, select first tab
                if self._tab_widget.count() > 1:
                    self._tab_widget.setCurrentIndex(0)
        finally:
            self._tab_widget.blockSignals(False)
    
    def _on_tab_changed(self, index):
        """Handle tab change"""
        if 0 <= index < len(self._app_state.categories):
            category = self._app_state.categories[index]
            self._app_state.select_category(category)
    
    def _on_tab_bar_clicked(self, index: int):
        """Handle tab bar click - check if add button was clicked"""
        # Check if clicked tab is the last one (add button)
        if index == self._tab_widget.count() - 1:
            self._show_add_category_dialog()
            # Prevent switching to add tab
            # Restore previous selection
            if self._tab_widget.count() > 1:
                self._tab_widget.setCurrentIndex(self._tab_widget.count() - 2)
    
    def _on_tab_context_menu(self, position):
        """Show context menu for tab"""
        tab_bar = self._tab_widget.tabBar()
        index = tab_bar.tabAt(position)
        
        # Don't show context menu for add button tab
        if index == self._tab_widget.count() - 1 or index < 0:
            return
        
        # Don't allow editing/deleting "All" category
        if index >= len(self._app_state.categories):
            return
        
        category = self._app_state.categories[index]
        if category.name == 'All':
            return
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(tab_bar.mapToGlobal(position))
        
        if action == edit_action:
            self._show_edit_category_dialog(category)
        elif action == delete_action:
            self._show_delete_category_dialog(category)
    
    def _show_add_category_dialog(self):
        """Show dialog to add a new category"""
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        from models.category import AppCategory
        import uuid
        
        name, ok = QInputDialog.getText(
            self,
            "Add Category",
            "Category name:",
        )
        
        if ok and name.strip():
            # Simple validation
            if len(name.strip()) < 1:
                QMessageBox.warning(self, "Error", "Category name cannot be empty")
                return
            
            # Check if category already exists
            if any(c.name == name.strip() for c in self._app_state.categories):
                QMessageBox.warning(self, "Error", f"Category '{name.strip()}' already exists")
                return
            
            # Create new category
            new_category = AppCategory(
                id=str(uuid.uuid4()),
                name=name.strip(),
                icon='📁'  # Default icon
            )
            
            try:
                self._app_state.add_category(new_category)
                # Select the new category
                self._tab_widget.setCurrentIndex(len(self._app_state.categories) - 1)
                QMessageBox.information(self, "Success", f"Category '{name.strip()}' added successfully")
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
    
    def _show_edit_category_dialog(self, category):
        """Show dialog to edit a category"""
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        from models.category import AppCategory
        
        name, ok = QInputDialog.getText(
            self,
            "Edit Category",
            "Category name:",
            text=category.name
        )
        
        if ok and name.strip() and name.strip() != category.name:
            # Check if new name already exists
            if any(c.name == name.strip() and c.id != category.id for c in self._app_state.categories):
                QMessageBox.warning(self, "Error", f"Category '{name.strip()}' already exists")
                return
            
            updated_category = AppCategory(
                id=category.id,
                name=name.strip(),
                icon=category.icon
            )
            
            try:
                self._app_state.update_category(updated_category)
                QMessageBox.information(self, "Success", f"Category updated to '{name.strip()}'")
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
    
    def _show_delete_category_dialog(self, category):
        """Show confirmation dialog and delete category"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Delete Category",
            f"Are you sure you want to delete category '{category.name}'?\n\nApps in this category will be moved to 'All' category.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self._app_state.remove_category(category.id)
                QMessageBox.information(self, "Success", f"Category '{category.name}' deleted")
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
    
    def _toggle_always_on_top(self):
        """Toggle always on top"""
        self._is_always_on_top = not self._is_always_on_top
        if self._is_always_on_top:
            self.setWindowFlags(
                self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
            )
        else:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
            )
        self.show()
        self._title_bar.update_always_on_top(self._is_always_on_top)
    
    def _launch_app(self, app: AppShortcut):
        """Launch an application"""
        success = self._launcher_service.launch(app)
        if not success:
            QMessageBox.warning(self, "Error", f"Failed to launch {app.name}")
    
    def _show_add_app_dialog(self):
        """Show add app dialog"""
        dialog = AppPickerDialog(self)
        if dialog.exec():
            app = dialog.get_app()
            if app:
                self._app_state.add_app(app)
                QMessageBox.information(self, "Success", f"{app.name} added successfully")
    
    def _edit_app(self, app: AppShortcut):
        """Edit an app"""
        dialog = AppPickerDialog(self, editing_app=app)
        if dialog.exec():
            updated_app = dialog.get_app()
            if updated_app:
                self._app_state.update_app(updated_app)
                QMessageBox.information(self, "Success", f"{updated_app.name} updated successfully")
    
    def _rename_app(self, app: AppShortcut):
        """Rename an app"""
        from PySide6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self, "Rename Application", "App Name:", text=app.name
        )
        if ok and new_name and new_name != app.name:
            updated_app = AppShortcut(
                id=app.id,
                name=new_name,
                icon_path=app.icon_path,
                target=app.target,
                category=app.category,
                type=app.type,
            )
            self._app_state.update_app(updated_app)
            QMessageBox.information(self, "Success", f"Renamed to {new_name}")
    
    def _change_icon(self, app: AppShortcut):
        """Change app icon"""
        dialog = IconPickerDialog(self, current_icon=app.icon_path)
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
                QMessageBox.information(self, "Success", "Icon updated successfully")
    
    def resizeEvent(self, event):
        """Handle window resize to position add button"""
        super().resizeEvent(event)
        if hasattr(self, '_add_button'):
            self._add_button.move(self.width() - 64, self.height() - 64)
    
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

