"""
My Everything Widget - PySide6 Version
Main entry point
"""
import logging
import sys
import tempfile
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QLockFile


def check_single_instance() -> QLockFile:
    """Ensure only one instance of the app runs at a time."""
    lock_path = Path(tempfile.gettempdir()) / "MyEverythingWidget.lock"
    lock = QLockFile(str(lock_path))

    if not lock.tryLock(100):  # 100ms timeout
        # Another instance is running
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.warning(
            None,
            "Already Running",
            "My Everything Widget is already running."
        )
        sys.exit(1)

    return lock


def main():
    """Application entry point"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    # Check for single instance
    lock = check_single_instance()

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("My Everything Widget")

    # Import here to avoid circular imports before QApplication is created
    from window.main_window import MainWindow
    
    # Create and show main window
    window = MainWindow()
    window.show()

    exit_code = app.exec()
    lock.unlock()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

