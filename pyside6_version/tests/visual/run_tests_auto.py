"""
Automated visual test runner that integrates with PySide6 app.
Takes screenshots automatically when icon picker dialog opens.
"""
import os
import sys
import time
import subprocess
from pathlib import Path
import pyautogui
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QObject, Signal

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ScreenshotTaker(QObject):
    """Helper class to take screenshots from Qt event loop"""
    screenshot_taken = Signal(str)
    
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
    
    def take_screenshot(self):
        """Take screenshot and emit signal"""
        img = pyautogui.screenshot()
        img.save(self.filename)
        self.screenshot_taken.emit(self.filename)
        QApplication.instance().quit()


def take_screenshot_after_delay(filename, delay_seconds=3):
    """Take a screenshot after a delay"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    taker = ScreenshotTaker(filename)
    timer = QTimer()
    timer.timeout.connect(taker.take_screenshot)
    timer.setSingleShot(True)
    timer.start(delay_seconds * 1000)
    
    app.exec()


def main():
    print("="*60)
    print("Automated Visual Icon Picker Test Runner - PySide6")
    print("="*60)
    print("\nThis script will:")
    print("1. Wait for you to open the icon picker dialog")
    print("2. Automatically take screenshots of Emoji and Icons tabs")
    print("3. Run visual tests on the screenshots")
    print("\nInstructions:")
    print("1. Run the PySide6 app: python main.py")
    print("2. Click the green '+' button to add an app")
    print("3. Click the icon selector to open icon picker dialog")
    print("4. Make sure you're on the 'Emoji' tab")
    print("5. This script will take a screenshot in 5 seconds...")
    print("\nWaiting 5 seconds...")
    
    script_dir = Path(__file__).parent
    
    # Take emoji screenshot
    emoji_screenshot = str(script_dir / "screenshot_emoji.png")
    print(f"\nTaking screenshot of emoji tab: {emoji_screenshot}")
    take_screenshot_after_delay(emoji_screenshot, delay_seconds=5)
    print(f"Screenshot saved: {emoji_screenshot}")
    
    print("\nNow switch to the Icons tab...")
    print("Waiting 3 seconds...")
    time.sleep(3)
    
    # Take icon screenshot
    icon_screenshot = str(script_dir / "screenshot_icons.png")
    print(f"\nTaking screenshot of icon tab: {icon_screenshot}")
    take_screenshot_after_delay(icon_screenshot, delay_seconds=2)
    print(f"Screenshot saved: {icon_screenshot}")
    
    print("\n" + "="*60)
    print("Running visual tests...")
    print("="*60 + "\n")
    
    # Run the visual test
    test_script = script_dir / "test_icon_picker_visual.py"
    result = subprocess.run([
        sys.executable,
        str(test_script),
        "--emoji-screenshot", emoji_screenshot,
        "--icon-screenshot", icon_screenshot,
    ], cwd=script_dir)
    
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())

