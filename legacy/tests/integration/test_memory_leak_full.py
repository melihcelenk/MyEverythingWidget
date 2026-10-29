"""
Full application memory leak test
"""
import gc
import sys
import tracemalloc

import pytest
from PySide6.QtWidgets import QApplication

from window.main_window import MainWindow


class TestFullMemoryLeak:
    """Test memory usage with full application"""

    @pytest.fixture
    def app(self):
        """Create QApplication"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app

    @pytest.fixture
    def main_window(self, app):
        """Create MainWindow"""
        window = MainWindow()
        window.show()
        app.processEvents()
        yield window
        window.close()
        app.processEvents()

    def test_tab_switching_process_memory(self, app, main_window):
        """Test actual process memory during tab switching"""
        tracemalloc.start()

        # Force garbage collection
        gc.collect()
        app.processEvents()

        snapshot1 = tracemalloc.take_snapshot()
        initial_mem = sum(stat.size for stat in snapshot1.statistics('lineno'))
        print(f"\nInitial memory: {initial_mem / 1024:.2f} KB")

        # Get tab widget
        tab_widget = main_window._tab_widget
        num_tabs = tab_widget.count() - 1  # Exclude + tab

        # Switch tabs with memory check - fail fast if leak detected
        max_mem_mb = 10  # Fail if memory exceeds 10 MB (strict limit)
        for i in range(30):  # Only 30 switches needed to detect leak
            tab_index = i % num_tabs
            tab_widget.setCurrentIndex(tab_index)
            app.processEvents()

            # Log and check every 10 switches
            if (i + 1) % 10 == 0:
                gc.collect()
                snapshot = tracemalloc.take_snapshot()
                current_mem = sum(stat.size for stat in snapshot.statistics('lineno'))
                current_mem_mb = current_mem / (1024 * 1024)
                print(f"After {i + 1} switches: {current_mem_mb:.2f} MB")

                # Fail fast if memory leak detected
                if current_mem_mb > max_mem_mb:
                    tracemalloc.stop()
                    pytest.fail(f"Memory leak detected: {current_mem_mb:.2f} MB exceeds {max_mem_mb} MB limit")

        # Final garbage collection
        gc.collect()
        app.processEvents()

        snapshot2 = tracemalloc.take_snapshot()
        final_mem = sum(stat.size for stat in snapshot2.statistics('lineno'))
        mem_increase = (final_mem - initial_mem) / (1024 * 1024)

        # Show top memory consumers
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        print("\nTop 10 memory consumers:")
        for stat in top_stats[:10]:
            print(stat)

        print(f"\nFinal memory: {final_mem / 1024:.2f} KB")
        print(f"Memory increase: {mem_increase:.2f} MB")

        tracemalloc.stop()

        # Memory increase should be less than 5 MB for 100 switches
        assert mem_increase < 5.0, f"Memory leak detected: {mem_increase:.2f} MB increase"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
