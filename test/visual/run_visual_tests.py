"""
Visual Icon Picker Test Runner
Takes screenshots and validates icon/emoji layout using image analysis.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from visual_icon_test import test_emoji_grid, test_icon_grid

def take_screenshot(window_title, output_path):
    """Take screenshot of Flutter app window."""
    # On Windows, use PowerShell to take screenshot
    if sys.platform == 'win32':
        try:
            # Use Windows API to capture window
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot.save(output_path)
            return True
        except ImportError:
            print("WARNING: pyautogui not installed. Install with: pip install pyautogui")
            print(f"Please manually take screenshot of '{window_title}' and save to: {output_path}")
            return False
    else:
        # Linux/Mac - use import or scrot
        print(f"Please manually take screenshot and save to: {output_path}")
        return False

def main():
    """Main test runner."""
    screenshots_dir = Path(__file__).parent / 'screenshots'
    screenshots_dir.mkdir(exist_ok=True)
    
    emoji_screenshot = screenshots_dir / 'emoji_grid.png'
    icon_screenshot = screenshots_dir / 'icon_grid.png'
    
    print("=" * 60)
    print("Visual Icon Picker Test Runner")
    print("=" * 60)
    print()
    print("Instructions:")
    print("1. Run the Flutter app: flutter run -d windows")
    print("2. Open the icon picker dialog")
    print("3. Take screenshots:")
    print(f"   - Emoji tab: {emoji_screenshot}")
    print(f"   - Icons tab: {icon_screenshot}")
    print("4. Press Enter when screenshots are ready...")
    print()
    
    input("Press Enter to continue...")
    
    # Check if screenshots exist
    if not emoji_screenshot.exists():
        print(f"ERROR: Emoji screenshot not found: {emoji_screenshot}")
        return 1
    
    if not icon_screenshot.exists():
        print(f"ERROR: Icon screenshot not found: {icon_screenshot}")
        return 1
    
    print()
    print("Running visual tests...")
    print()
    
    # Run tests
    emoji_result = test_emoji_grid(str(emoji_screenshot))
    print()
    icon_result = test_icon_grid(str(icon_screenshot))
    
    print()
    print("=" * 60)
    if emoji_result and icon_result:
        print("✓ All visual tests passed!")
        return 0
    else:
        print("✗ Some visual tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())

