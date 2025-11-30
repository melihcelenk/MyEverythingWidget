"""
Memory leak test for tab switching
"""
import gc
import sys
import tracemalloc

import pytest
from PySide6.QtWidgets import QApplication

from window.app_state import AppState
from window.tab_manager import TabManager


class TestMemoryLeak:
    """Test memory usage during tab switching"""

    @pytest.fixture
    def app(self):
        """Create QApplication"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app

    @pytest.fixture
    def tab_manager(self, app):
        """Create TabManager with mock callbacks"""
        app_state = AppState()

        # Mock callbacks
        noop = lambda *args: None

        manager = TabManager(
            app_state=app_state,
            on_app_tap=noop,
            on_app_edit=noop,
            on_app_rename=noop,
            on_app_change_icon=noop,
            on_app_delete=noop,
            on_add_category=noop,
            on_edit_category=noop,
            on_delete_category=noop,
        )

        tab_widget = manager.create_tab_widget()
        yield manager

        # Cleanup
        tab_widget.deleteLater()
        app.processEvents()

    def test_tab_switching_memory_leak(self, app, tab_manager):
        """Test that switching tabs doesn't cause memory leak"""
        tracemalloc.start()

        # Force garbage collection before starting
        gc.collect()
        app.processEvents()

        # Get initial memory
        snapshot1 = tracemalloc.take_snapshot()
        initial_mem = sum(stat.size for stat in snapshot1.statistics('lineno'))

        # Switch tabs 50 times
        tab_widget = tab_manager.tab_widget
        num_tabs = len(tab_manager._app_state.categories)

        for i in range(50):
            tab_index = i % num_tabs
            tab_widget.setCurrentIndex(tab_index)
            app.processEvents()

        # Force garbage collection
        gc.collect()
        app.processEvents()

        # Get final memory
        snapshot2 = tracemalloc.take_snapshot()
        final_mem = sum(stat.size for stat in snapshot2.statistics('lineno'))

        tracemalloc.stop()

        # Calculate memory increase
        mem_increase = final_mem - initial_mem
        mem_increase_mb = mem_increase / (1024 * 1024)

        print(f"\nInitial memory: {initial_mem / 1024:.2f} KB")
        print(f"Final memory: {final_mem / 1024:.2f} KB")
        print(f"Memory increase: {mem_increase_mb:.2f} MB")

        # Memory increase should be minimal (less than 1 MB for 50 switches)
        assert mem_increase_mb < 1.0, f"Memory leak detected: {mem_increase_mb:.2f} MB increase"

    def test_tab_switching_widget_count(self, app, tab_manager):
        """Test that widget count stays stable during tab switching"""
        tab_widget = tab_manager.tab_widget
        num_tabs = len(tab_manager._app_state.categories)

        # Get initial widget count
        def count_widgets():
            count = 0
            for cat_id, grid in tab_manager._category_grids.items():
                count += grid.count()
            return count

        initial_count = count_widgets()
        print(f"\nInitial widget count: {initial_count}")

        # Switch tabs 20 times
        for i in range(20):
            tab_index = i % num_tabs
            tab_widget.setCurrentIndex(tab_index)
            app.processEvents()

        final_count = count_widgets()
        print(f"Final widget count: {final_count}")

        # Widget count should remain the same
        assert final_count == initial_count, f"Widget count changed: {initial_count} -> {final_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
