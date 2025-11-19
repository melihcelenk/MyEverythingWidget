"""
My Everything Widget - PySide6 Version
Main entry point
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from window.main_window import MainWindow


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("My Everything Widget")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

