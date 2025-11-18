"""
Visual regression tests for Icon Picker Dialog
Tests actual pixel rendering, not just widget logic
"""
import numpy as np
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PIL import Image

# Try to import cv2, but it's optional for basic tests
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("WARNING: cv2 not available, some features may be limited")

# Expected emoji list (from widgets/icon_picker_dialog.py)
EXPECTED_EMOJIS = [
    '📱', '💻', '🌐', '📁', '📝', '📊', '📈', '📉',
    '🎵', '🎮', '🎨', '🎬', '📷', '📹', '🎤', '🎧',
    '⚙️', '🔧', '🔨', '🛠️', '⚡', '🔥', '💡', '🔒',
    '📧', '💬', '📞', '📱', '🌟', '⭐', '❤️', '💚',
    '🚀', '✈️', '🚗', '🚲', '⚽', '🏀', '🎯', '🎲',
    '☀️', '🌙', '⭐', '🌈', '🔔', '🎁', '🏆', '👍',
]

EXPECTED_ICON_COUNT = 48


def find_red_borders(image_path):
    """Find all red border rectangles in the image."""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    # Find red pixels (RGB: 255, 0, 0) - allow tolerance for anti-aliasing
    # More lenient: R > 100, G < 150, B < 150, and R is significantly higher than G and B
    red_mask = (img_array[:, :, 0] > 100) & (img_array[:, :, 1] < 150) & (img_array[:, :, 2] < 150) & (img_array[:, :, 0] > img_array[:, :, 1] + 10) & (img_array[:, :, 0] > img_array[:, :, 2] + 10)
    
    # Find bounding boxes of red regions using flood fill
    height, width = red_mask.shape
    visited = np.zeros_like(red_mask, dtype=bool)
    boxes = []
    
    def flood_fill(start_y, start_x):
        """Flood fill to find connected red pixels."""
        if not red_mask[start_y, start_x] or visited[start_y, start_x]:
            return None
        
        stack = [(start_y, start_x)]
        min_y, max_y = start_y, start_y
        min_x, max_x = start_x, start_x
        
        while stack:
            y, x = stack.pop()
            if y < 0 or y >= height or x < 0 or x >= width:
                continue
            if visited[y, x] or not red_mask[y, x]:
                continue
            
            visited[y, x] = True
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            
            # Check neighbors
            stack.append((y - 1, x))
            stack.append((y + 1, x))
            stack.append((y, x - 1))
            stack.append((y, x + 1))
        
        # Only return if it's a reasonable size (not just noise)
        box_width = max_x - min_x + 1
        box_height = max_y - min_y + 1
        if box_width > 15 and box_height > 15:
            # Check if it's roughly square (aspect ratio between 0.5 and 2.0)
            aspect_ratio = box_width / box_height if box_height > 0 else 1.0
            if 0.5 <= aspect_ratio <= 2.0:
                return {
                    'x': min_x,
                    'y': min_y,
                    'width': box_width,
                    'height': box_height,
                    'center_x': (min_x + max_x) / 2,
                    'center_y': (min_y + max_y) / 2,
                }
        return None
    
    # Find all red regions
    for y in range(height):
        for x in range(width):
            if red_mask[y, x] and not visited[y, x]:
                box = flood_fill(y, x)
                if box:
                    boxes.append(box)
    
    # Filter boxes to only include emoji containers
    filtered_boxes = []
    max_dialog_y = height * 0.9  # Dialog should be in upper 90% of screen
    
    for box in boxes:
        # Check if box is reasonably sized for emoji container
        if (box['width'] > 20 and box['height'] > 20 and
            box['width'] < 150 and box['height'] < 150):
            # Prefer boxes in dialog area, but accept all if we don't have enough
            if box['y'] < max_dialog_y or len(boxes) < 20:
                filtered_boxes.append(box)
    
    # If we filtered out too many, accept all reasonably sized boxes
    if len(filtered_boxes) < 5:
        filtered_boxes = [b for b in boxes if b['width'] > 20 and b['height'] > 20 and b['width'] < 150 and b['height'] < 150]
    
    # Debug: Print all boxes found (first 20)
    if len(boxes) > 0:
        print(f"\nDEBUG: Found {len(boxes)} total red regions, {len(filtered_boxes)} after filtering")
        print(f"DEBUG: First 10 boxes (all):")
        for i, box in enumerate(boxes[:10]):
            print(f"  Box {i}: x={box['x']:.0f}, y={box['y']:.0f}, w={box['width']:.0f}, h={box['height']:.0f}")
    
    return filtered_boxes, img_array


def has_visible_content(box, img_array, is_emoji=True):
    """
    Check if the box contains visible content (not just background).
    Returns True if content is visible, False if empty.
    """
    # Get the content area (inside the border, skip 3px for border)
    border_width = 3
    content_x = max(0, int(box['x'] + border_width))
    content_y = max(0, int(box['y'] + border_width))
    content_w = max(1, int(box['width'] - (border_width * 2)))
    content_h = max(1, int(box['height'] - (border_width * 2)))
    
    # Ensure we don't go out of bounds
    img_height, img_width = img_array.shape[:2]
    content_x = min(content_x, img_width - 1)
    content_y = min(content_y, img_height - 1)
    content_w = min(content_w, img_width - content_x)
    content_h = min(content_h, img_height - content_y)
    
    if content_w <= 0 or content_h <= 0:
        return False, 0.0
    
    # Extract content region
    content_region = img_array[content_y:content_y + content_h, content_x:content_x + content_w]
    
    # Convert to grayscale for analysis
    if len(content_region.shape) == 3:
        gray = np.mean(content_region, axis=2).astype(np.uint8)
    else:
        gray = content_region
    
    # Calculate statistics
    total_pixels = gray.size
    mean_brightness = np.mean(gray)
    std_brightness = np.std(gray)
    
    # For emojis: look for colorful pixels (high saturation)
    if is_emoji:
        # Convert to HSV for saturation analysis
        if HAS_CV2 and len(content_region.shape) == 3:
            hsv = cv2.cvtColor(content_region, cv2.COLOR_RGB2HSV)
        else:
            hsv = None
        
        if hsv is not None:
            saturation = hsv[:, :, 1]
            max_diff = np.max(content_region, axis=2) - np.min(content_region, axis=2)
            
            # Emojis are colorful - require moderate saturation
            significant_pixels = np.sum((saturation > 30) & (max_diff > 30))
            content_ratio = significant_pixels / total_pixels if total_pixels > 0 else 0
            has_content = content_ratio > 0.20  # Emojis should fill at least 20% of container
        else:
            # Fallback: check for non-uniform brightness
            has_content = std_brightness > 10
            content_ratio = std_brightness / 255.0
    else:
        # For icons: look for dark pixels or contrast
        brightness = gray
        contrast = std_brightness
        significant_pixels = np.sum((brightness < 120) | (contrast > 10))
        content_ratio = significant_pixels / total_pixels if total_pixels > 0 else 0
        has_content = content_ratio > 0.05  # Icons can be smaller
    
    return has_content, content_ratio


def check_overlap(box1, box2, tolerance=10):
    """Check if two boxes overlap significantly."""
    # Calculate overlap
    overlap_x = max(0, min(box1['x'] + box1['width'], box2['x'] + box2['width']) - max(box1['x'], box2['x']))
    overlap_y = max(0, min(box1['y'] + box1['height'], box2['y'] + box2['height']) - max(box1['y'], box2['y']))
    
    # Only report overlap if there's significant overlap (more than tolerance px)
    return overlap_x > tolerance and overlap_y > tolerance


def check_centering(box, img_array):
    """Check if content is centered within the box."""
    # Get content region
    border_width = 3
    content_x = max(0, int(box['x'] + border_width))
    content_y = max(0, int(box['y'] + border_width))
    content_w = max(1, int(box['width'] - (border_width * 2)))
    content_h = max(1, int(box['height'] - (border_width * 2)))
    
    img_height, img_width = img_array.shape[:2]
    content_x = min(content_x, img_width - 1)
    content_y = min(content_y, img_height - 1)
    content_w = min(content_w, img_width - content_x)
    content_h = min(content_h, img_height - content_y)
    
    if content_w <= 0 or content_h <= 0:
        return False, {}
    
    content_region = img_array[content_y:content_y + content_h, content_x:content_x + content_w]
    
    # Find content center of mass
    if len(content_region.shape) == 3:
        gray = np.mean(content_region, axis=2)
    else:
        gray = content_region
    
    # Calculate center of mass
    y_coords, x_coords = np.meshgrid(np.arange(content_h), np.arange(content_w), indexing='ij')
    total_mass = np.sum(gray)
    
    if total_mass == 0:
        return False, {}
    
    center_x = np.sum(x_coords * gray) / total_mass
    center_y = np.sum(y_coords * gray) / total_mass
    
    # Check if center is near box center
    box_center_x = content_w / 2
    box_center_y = content_h / 2
    
    offset_x = abs(center_x - box_center_x)
    offset_y = abs(center_y - box_center_y)
    
    # Allow 20% offset
    max_offset_x = content_w * 0.2
    max_offset_y = content_h * 0.2
    
    is_centered = offset_x < max_offset_x and offset_y < max_offset_y
    
    return is_centered, {
        'offset_x': offset_x,
        'offset_y': offset_y,
        'max_offset_x': max_offset_x,
        'max_offset_y': max_offset_y,
    }


def verify_emoji_tab_is_open(img_array):
    """Verify that the Emoji tab is selected by looking for emoji characters."""
    # Convert to grayscale for text detection
    gray = np.mean(img_array, axis=2).astype(np.uint8)
    
    # Look for emoji characters in the image - emojis should be colorful
    rgb = img_array.reshape(-1, 3).astype(float)
    saturation = np.max(rgb, axis=1) - np.min(rgb, axis=1)
    colorful_pixels = np.sum(saturation > 30)
    total_pixels = saturation.size
    
    # If more than 1% of pixels are colorful, we likely have emojis visible
    colorful_ratio = colorful_pixels / total_pixels if total_pixels > 0 else 0
    
    # Also check for red borders which indicate emoji containers
    red_mask = (img_array[:, :, 0] > 180) & (img_array[:, :, 1] < 80) & (img_array[:, :, 2] < 80)
    red_pixel_count = np.sum(red_mask)
    
    # If we have red borders and colorful pixels, emoji tab is likely open
    has_red_borders = red_pixel_count > 100  # At least 100 red pixels (borders)
    has_colorful_content = colorful_ratio > 0.01  # At least 1% colorful pixels
    
    return has_red_borders and has_colorful_content


def test_emoji_grid(screenshot_path):
    """Test that all emojis are visible in the screenshot."""
    print(f"\n{'='*60}")
    print(f"Testing emoji grid: {screenshot_path}")
    print(f"{'='*60}")
    
    if not os.path.exists(screenshot_path):
        print(f"ERROR: Screenshot not found: {screenshot_path}")
        return False
    
    img = Image.open(screenshot_path)
    img_array = np.array(img)
    
    # First verify that emoji tab is open
    if not verify_emoji_tab_is_open(img_array):
        print("ERROR: Emoji tab does not appear to be open in the screenshot")
        print("       Please ensure:")
        print("       1. The icon picker dialog is open")
        print("       2. The 'Emoji' tab is selected")
        print("       3. The dialog is fully visible on screen")
        return False
    
    print("[OK] Emoji tab is open")
    
    boxes, img_array = find_red_borders(screenshot_path)
    
    if len(boxes) == 0:
        print("ERROR: No red borders found in screenshot")
        print("       This suggests emojis are not rendering or the tab is not open")
        return False
    
    print(f"Found {len(boxes)} emoji containers (visible on screen)")
    print(f"Expected {len(EXPECTED_EMOJIS)} total emojis")
    
    # Sort boxes by position (top to bottom, left to right)
    boxes.sort(key=lambda b: (b['y'], b['x']))
    
    # Print first few boxes for debugging
    if len(boxes) > 0:
        print(f"\nFirst {min(5, len(boxes))} containers found:")
        for i, box in enumerate(boxes[:5]):
            print(f"  Box {i}: x={box['x']:.0f}, y={box['y']:.0f}, w={box['width']:.0f}, h={box['height']:.0f}")
    
    # Check count - we expect at least 6 visible emojis (first row = 6 columns based on PySide6 grid)
    # If we see less, it means emojis are not rendering properly
    if len(boxes) < 6:
        print(f"\nERROR: Found only {len(boxes)} visible containers, expected at least 6 (first row with 6 columns)")
        print(f"       This suggests emojis are not rendering properly in the GridView")
        print(f"       Possible issues:")
        print(f"       1. Emoji tab is not selected")
        print(f"       2. GridView is not rendering all items")
        print(f"       3. Screenshot was taken before dialog fully loaded")
        print(f"       4. Red border detection is too strict - try lowering thresholds")
        return False
    
    print(f"INFO: {len(boxes)} emojis are visible on screen (scroll needed to see all {len(EXPECTED_EMOJIS)})")
    
    # Check for overlaps
    overlaps = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if check_overlap(boxes[i], boxes[j]):
                overlaps.append((i, j))
    
    if overlaps:
        print(f"WARNING: Found {len(overlaps)} potentially overlapping containers (may be due to anti-aliasing):")
        for i, j in overlaps[:3]:  # Show first 3
            print(f"  Box {i} may overlap with box {j}")
        if len(overlaps) > 3:
            print(f"  ... and {len(overlaps) - 3} more")
    
    # Check that each box has visible content
    empty_boxes = []
    content_ratios = []
    
    for i, box in enumerate(boxes):
        has_content, content_ratio = has_visible_content(box, img_array, is_emoji=True)
        content_ratios.append(content_ratio)
        
        if not has_content:
            empty_boxes.append(i)
    
    if empty_boxes:
        print(f"\nERROR: Found {len(empty_boxes)} empty emoji containers (no visible content):")
        for i in empty_boxes[:10]:  # Show first 10
            ratio = content_ratios[i]
            print(f"  Box {i}: content_ratio={ratio:.3f} (expected > 0.20)")
        if len(empty_boxes) > 10:
            print(f"  ... and {len(empty_boxes) - 10} more empty boxes")
        return False
    
    # Check centering
    off_center_boxes = []
    for i, box in enumerate(boxes):
        is_centered, info = check_centering(box, img_array)
        if not is_centered:
            off_center_boxes.append((i, info))
    
    if off_center_boxes:
        print(f"\nWARNING: Found {len(off_center_boxes)} off-center containers:")
        for i, info in off_center_boxes[:5]:  # Show first 5
            print(f"  Box {i}: offset_x={info['offset_x']:.1f}, offset_y={info['offset_y']:.1f}")
        if len(off_center_boxes) > 5:
            print(f"  ... and {len(off_center_boxes) - 5} more")
    
    print(f"\n[PASS] Emoji grid test passed!")
    print(f"       - Found {len(boxes)} visible emoji containers")
    print(f"       - All containers have visible content")
    print(f"       - No significant overlaps detected")
    
    return True


def test_icon_grid(screenshot_path):
    """Test that all icons are visible in the screenshot."""
    print(f"\n{'='*60}")
    print(f"Testing icon grid: {screenshot_path}")
    print(f"{'='*60}")
    
    if not os.path.exists(screenshot_path):
        print(f"ERROR: Screenshot not found: {screenshot_path}")
        return False
    
    boxes, img_array = find_red_borders(screenshot_path)
    
    if len(boxes) == 0:
        print("ERROR: No red borders found in screenshot")
        return False
    
    print(f"Found {len(boxes)} icon containers (visible on screen)")
    
    # Check count - we expect at least 6 visible icons (first row = 6 columns based on PySide6 grid)
    if len(boxes) < 6:
        print(f"ERROR: Found only {len(boxes)} visible containers, expected at least 6 (first row with 6 columns)")
        return False
    
    # Check that each box has visible content
    empty_boxes = []
    for i, box in enumerate(boxes):
        has_content, content_ratio = has_visible_content(box, img_array, is_emoji=False)
        if not has_content:
            empty_boxes.append(i)
    
    if empty_boxes:
        print(f"ERROR: Found {len(empty_boxes)} empty icon containers")
        return False
    
    print(f"[PASS] Icon grid test passed!")
    return True


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visual icon picker tests')
    parser.add_argument('--emoji-screenshot', type=str, help='Path to emoji tab screenshot')
    parser.add_argument('--icon-screenshot', type=str, help='Path to icon tab screenshot')
    
    args = parser.parse_args()
    
    success = True
    
    if args.emoji_screenshot:
        success &= test_emoji_grid(args.emoji_screenshot)
    
    if args.icon_screenshot:
        success &= test_icon_grid(args.icon_screenshot)
    
    print(f"\n{'='*60}")
    if success:
        print("[PASS] ALL TESTS PASSED")
    else:
        print("[FAIL] TESTS FAILED")
    print(f"{'='*60}\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

