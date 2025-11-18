"""
Fully automated test and fix script for icon picker.
Runs the app, takes screenshots, tests, and fixes issues iteratively.
"""
import os
import sys
import time
import subprocess
from pathlib import Path
import pyautogui
import pygetwindow as gw

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def find_flutter_window():
    """Find the Flutter app window."""
    windows = gw.getWindowsWithTitle("My Everything")
    if windows:
        return windows[0]
    return None

def click_add_button():
    """Click the add button to open app picker."""
    print("Looking for add button...")
    # The add button is in the bottom right, green circle with plus
    # Try to find it by color or position
    screen_width, screen_height = pyautogui.size()
    # Bottom right area
    region = (screen_width - 200, screen_height - 200, 200, 200)
    
    try:
        # Look for green button
        button_location = pyautogui.locateOnScreen(None, region=region, confidence=0.7)
        if button_location:
            center = pyautogui.center(button_location)
            pyautogui.click(center)
            print(f"Clicked add button at {center}")
            return True
    except:
        pass
    
    # Fallback: click at estimated position
    print("Using fallback: clicking at estimated position")
    pyautogui.click(screen_width - 100, screen_height - 100)
    time.sleep(0.5)
    return True

def open_icon_picker():
    """Open the icon picker dialog."""
    print("Opening icon picker...")
    # After clicking add, there should be a dialog
    # Look for "Select Icon" button or icon selector
    time.sleep(1)
    
    # Try to find and click icon selector area
    # This is a bit tricky, we might need to click on the icon preview area
    screen = pyautogui.screenshot()
    # Look for text "Select Icon" or icon area
    # For now, just try clicking in the dialog area
    screen_width, screen_height = pyautogui.size()
    # Center of screen where dialog usually appears
    pyautogui.click(screen_width // 2, screen_height // 2 - 100)
    time.sleep(1)
    return True

def switch_to_emoji_tab():
    """Switch to emoji tab in icon picker."""
    print("Switching to emoji tab...")
    screen_width, screen_height = pyautogui.size()
    # Emoji tab is usually on the left
    # Click slightly left of center, in the tab area
    pyautogui.click(screen_width // 2 - 150, screen_height // 2 - 150)
    time.sleep(1)

def take_screenshot(filename):
    """Take a screenshot and save it."""
    print(f"Taking screenshot: {filename}")
    img = pyautogui.screenshot()
    img.save(filename)
    print(f"Screenshot saved to {filename}")
    return filename

def run_visual_test(emoji_screenshot, icon_screenshot=None):
    """Run the visual test and return success status."""
    script_dir = Path(__file__).parent
    test_script = script_dir / "visual_icon_test.py"
    
    cmd = [sys.executable, str(test_script), "--emoji-screenshot", emoji_screenshot]
    if icon_screenshot:
        cmd.extend(["--icon-screenshot", icon_screenshot])
    
    result = subprocess.run(cmd, cwd=script_dir, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0

def main():
    print("="*60)
    print("AUTOMATED ICON PICKER TEST AND FIX")
    print("="*60)
    
    script_dir = Path(__file__).parent
    
    # Wait for app to start
    print("\nWaiting for Flutter app to start...")
    time.sleep(5)
    
    # Find window
    window = find_flutter_window()
    if window:
        print(f"Found window: {window.title}")
        window.activate()
        time.sleep(1)
    else:
        print("Warning: Could not find Flutter window, continuing anyway...")
    
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'='*60}")
        print(f"ITERATION {iteration}/{max_iterations}")
        print(f"{'='*60}")
        
        try:
            # Open icon picker
            click_add_button()
            time.sleep(2)
            open_icon_picker()
            time.sleep(2)
            switch_to_emoji_tab()
            time.sleep(2)
            
            # Take screenshot
            emoji_screenshot = str(script_dir / "screenshot_emoji.png")
            take_screenshot(emoji_screenshot)
            
            # Run test
            print("\nRunning visual test...")
            success = run_visual_test(emoji_screenshot)
            
            if success:
                print("\n[SUCCESS] All emojis are visible!")
                break
            else:
                print(f"\n[FAIL] Test failed on iteration {iteration}")
                print("Need to fix the code...")
                # Close dialog
                pyautogui.press('escape')
                time.sleep(1)
                
        except Exception as e:
            print(f"Error in iteration {iteration}: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(2)
    
    if iteration >= max_iterations:
        print(f"\n[FAIL] Reached max iterations ({max_iterations})")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

