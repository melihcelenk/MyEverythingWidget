"""
StyledTabWidget - Reusable styled tab widget.

Provides a consistent tab appearance across the application.
Used by category tabs and add-item modal tabs.
"""
from PySide6.QtWidgets import QTabWidget, QTabBar


class StyledTabWidget(QTabWidget):
    """A QTabWidget with consistent application styling.
    
    This widget provides:
    - Consistent tab appearance (colors, borders, padding)
    - Optional compact mode for modals
    - Configurable tab bar behavior
    """

    # Default stylesheet for normal tabs (category tabs)
    DEFAULT_STYLESHEET = """
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
            padding: 6px 8px;
            margin-right: 1px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            max-width: 70px;
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
    """

    # Compact stylesheet for modals (no max-width, smaller padding)
    COMPACT_STYLESHEET = """
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
            margin-right: 1px;
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
    """

    def __init__(self, compact: bool = False, parent=None):
        """Initialize the styled tab widget.
        
        Args:
            compact: If True, uses compact styling suitable for modals.
            parent: Parent widget.
        """
        super().__init__(parent)

        self._compact = compact
        self._setup_style()

    def _setup_style(self):
        """Apply the appropriate stylesheet."""
        stylesheet = self.COMPACT_STYLESHEET if self._compact else self.DEFAULT_STYLESHEET
        self.setStyleSheet(stylesheet)

        # Configure tab bar
        self.setTabsClosable(False)
        self.tabBar().setExpanding(False)

    def add_tab_with_icon(self, widget, icon: str, name: str) -> int:
        """Add a tab with an icon prefix.
        
        Args:
            widget: The widget to add as tab content.
            icon: Icon/emoji to show before the name.
            name: Tab name.
            
        Returns:
            Index of the added tab.
        """
        return self.addTab(widget, f"{icon} {name}")

    def set_tab_enabled(self, index: int, enabled: bool):
        """Enable or disable a tab.
        
        Args:
            index: Tab index.
            enabled: Whether the tab should be enabled.
        """
        self.setTabEnabled(index, enabled)

    @property
    def tab_bar(self) -> QTabBar:
        """Get the tab bar widget."""
        return self.tabBar()
