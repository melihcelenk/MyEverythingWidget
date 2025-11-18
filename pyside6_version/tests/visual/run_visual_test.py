"""
Automated visual test runner for icon picker.
Takes screenshots and runs visual tests.
"""
import os
import sys
import time
import subprocess
from pathlib import Path
import pyautogui

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def take_screenshot(filename):
    """Take a screenshot and save it."""
    print(f"Taking screenshot: {filename}")
    img = pyautogui.screenshot()
    img.save(filename)
    print(f"Screenshot saved to {filename}")
    return filename


def main():
    print("="*60)
    print("Visual Icon Picker Test Runner - PySide6 Version")
    print("="*60)
    print("\nInstructions:")
    print("1. Make sure the PySide6 app is running (python main.py)")
    print("2. Click the green '+' button to add an app")
    print("3. Click the icon selector (icon preview area) to open icon picker dialog")
    print("4. Make sure you're on the 'Emoji' tab (should be selected by default)")
    print("5. Wait for the dialog to fully load (all emojis visible)")
    print("6. This script will take a screenshot in 10 seconds...")
    print("\nWaiting 10 seconds for you to prepare...")
    
    for i in range(10, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print("\nTaking screenshot of emoji tab...")
    script_dir = Path(__file__).parent
    emoji_screenshot = str(script_dir / "screenshot_emoji.png")
    take_screenshot(emoji_screenshot)
    print(f"\nScreenshot saved to: {emoji_screenshot}")
    
    print("\nNow switch to the Icons tab...")
    print("Waiting 3 seconds...")
    time.sleep(3)
    
    # Take icon screenshot
    icon_screenshot = str(script_dir / "screenshot_icons.png")
    take_screenshot(icon_screenshot)
    
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

