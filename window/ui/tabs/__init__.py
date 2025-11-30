"""
Tab management components.

- TabManager: Manages QTabWidget (add/remove tabs, tab events)
- CategoryPage: Content of a category tab (grid + note entry)
"""
from window.ui.tabs.category_page import CategoryPage
from window.ui.tabs.tab_manager import TabManager

__all__ = ['TabManager', 'CategoryPage']
