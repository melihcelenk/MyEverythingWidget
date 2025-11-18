"""
Take screenshot of emoji tab with scrolling to see all emojis.
"""
import pyautogui
import time
import sys
from pathlib import Path

def take_screenshot_with_scroll():
    """Take screenshot after scrolling to see all emojis."""
    print("="*60)
    print("Emoji Tab Screenshot Tool")
    print("="*60)
    print("\nInstructions:")
    print("1. Open the app and click the add button (green + button)")
    print("2. Click on the icon selector to open icon picker dialog")
    print("3. Make sure you're on the 'Emoji' tab (should be selected by default)")
    print("4. Wait for the dialog to fully load")
    print("5. This script will take a screenshot in 10 seconds...")
    print("\nWaiting 10 seconds for you to prepare...")
    
    for i in range(10, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print("\nTaking screenshot...")
    script_dir = Path(__file__).parent
    screenshot_path = str(script_dir / "screenshot_emoji.png")
    
    # Take screenshot
    img = pyautogui.screenshot()
    img.save(screenshot_path)
    print(f"\nScreenshot saved to: {screenshot_path}")
    print("\nNow running visual test...")
    
    return screenshot_path

if __name__ == '__main__':
    take_screenshot_with_scroll()

