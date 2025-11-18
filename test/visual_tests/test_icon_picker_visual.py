"""
Visual regression tests for Icon Picker Dialog
Tests actual pixel rendering, not just widget logic
"""
import cv2
import numpy as np
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


class IconPickerVisualTest:
    """Visual tests for icon picker dialog"""

    def __init__(self, screenshot_path: str):
        """
        Initialize test with screenshot path

        Args:
            screenshot_path: Path to screenshot PNG file
        """
        self.screenshot_path = Path(screenshot_path)
        self.img = None
        self.results = []

    def load_screenshot(self) -> bool:
        """Load screenshot image"""
        if not self.screenshot_path.exists():
            print(f"❌ ERROR: Screenshot not found: {self.screenshot_path}")
            return False

        self.img = cv2.imread(str(self.screenshot_path))
        if self.img is None:
            print(f"❌ ERROR: Failed to load image: {self.screenshot_path}")
            return False

        print(f"✅ Loaded screenshot: {self.img.shape[1]}x{self.img.shape[0]}px")
        return True

    def find_red_borders(self) -> list:
        """
        Find all red bordered containers in screenshot

        Returns:
            List of (x, y, w, h) tuples for each red bordered box
        """
        # Convert to HSV for better red detection
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        # Red color range (two ranges because red wraps around in HSV)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        # Create masks
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2

        # Find contours
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter for rectangular shapes
        boxes = []
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            # If roughly rectangular (4-6 corners) and reasonably sized
            if 4 <= len(approx) <= 6:
                x, y, w, h = cv2.boundingRect(contour)
                # Filter by size (50x50 to 150x150 pixels)
                if 50 <= w <= 150 and 50 <= h <= 150:
                    boxes.append((x, y, w, h))

        print(f"🔍 Found {len(boxes)} red bordered containers")
        return boxes

    def check_emoji_visibility(self, boxes: list) -> dict:
        """
        Check if emojis are visible inside red bordered boxes

        Args:
            boxes: List of (x, y, w, h) tuples for red borders

        Returns:
            Dict with test results
        """
        visible_count = 0
        empty_count = 0
        details = []

        for i, (x, y, w, h) in enumerate(boxes):
            # Extract region inside border (with small margin to avoid border pixels)
            margin = 5
            roi = self.img[y+margin:y+h-margin, x+margin:x+w-margin]

            if roi.size == 0:
                continue

            # Convert to grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Check if region is mostly empty (uniform color)
            # Standard deviation of pixel values - low means uniform/empty
            std_dev = np.std(gray)
            mean_brightness = np.mean(gray)

            # Check for content
            # Empty boxes have low std deviation and similar brightness
            is_empty = std_dev < 5 and (mean_brightness > 200 or mean_brightness < 50)

            if is_empty:
                empty_count += 1
                status = "❌ EMPTY"
            else:
                visible_count += 1
                status = "✅ HAS CONTENT"

            details.append({
                'index': i + 1,
                'box': (x, y, w, h),
                'status': status,
                'std_dev': std_dev,
                'brightness': mean_brightness
            })

        return {
            'total': len(boxes),
            'visible': visible_count,
            'empty': empty_count,
            'details': details
        }

    def check_icon_containment(self, boxes: list) -> dict:
        """
        Check if content is contained within red borders
        Looks for dark pixels (icons/emoji) that exceed border bounds

        Args:
            boxes: List of (x, y, w, h) tuples for red borders

        Returns:
            Dict with test results
        """
        contained_count = 0
        overflow_count = 0
        details = []

        for i, (x, y, w, h) in enumerate(boxes):
            # Check area just outside border (2px margin)
            margin = 2
            overflow_detected = False

            # Check top, bottom, left, right margins
            checks = [
                ('top', self.img[max(0, y-margin):y, x:x+w]),
                ('bottom', self.img[y+h:min(self.img.shape[0], y+h+margin), x:x+w]),
                ('left', self.img[y:y+h, max(0, x-margin):x]),
                ('right', self.img[y:y+h, x+w:min(self.img.shape[1], x+w+margin)])
            ]

            overflow_sides = []
            for side, region in checks:
                if region.size == 0:
                    continue

                # Convert to grayscale
                gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

                # Check for dark pixels (potential content overflow)
                # Dark pixels < 100 brightness
                dark_pixels = np.sum(gray < 100)
                total_pixels = gray.size

                # If more than 5% dark pixels, content is overflowing
                if total_pixels > 0 and (dark_pixels / total_pixels) > 0.05:
                    overflow_detected = True
                    overflow_sides.append(side)

            if overflow_detected:
                overflow_count += 1
                status = f"❌ OVERFLOW ({', '.join(overflow_sides)})"
            else:
                contained_count += 1
                status = "✅ CONTAINED"

            details.append({
                'index': i + 1,
                'box': (x, y, w, h),
                'status': status
            })

        return {
            'total': len(boxes),
            'contained': contained_count,
            'overflow': overflow_count,
            'details': details
        }

    def generate_annotated_screenshot(self, boxes: list, emoji_results: dict, output_path: str):
        """
        Generate annotated screenshot with test results overlaid

        Args:
            boxes: List of red bordered boxes
            emoji_results: Results from emoji visibility test
            output_path: Where to save annotated image
        """
        annotated = self.img.copy()

        for i, detail in enumerate(emoji_results['details']):
            x, y, w, h = detail['box']

            # Draw box number
            color = (0, 255, 0) if '✅' in detail['status'] else (0, 0, 255)
            cv2.putText(annotated, str(i + 1), (x + 5, y + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Draw border highlight
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

        # Save annotated image
        cv2.imwrite(output_path, annotated)
        print(f"📸 Saved annotated screenshot: {output_path}")

    def run_all_tests(self):
        """Run all visual tests"""
        print("\n" + "="*60)
        print("🎨 VISUAL REGRESSION TEST - Icon Picker Dialog")
        print("="*60 + "\n")

        # Load screenshot
        if not self.load_screenshot():
            return False

        # Find red borders
        boxes = self.find_red_borders()
        if not boxes:
            print("❌ FAIL: No red bordered containers found!")
            return False

        # Test 1: Emoji visibility
        print("\n📊 TEST 1: Emoji Visibility")
        print("-" * 60)
        emoji_results = self.check_emoji_visibility(boxes)

        print(f"Total boxes: {emoji_results['total']}")
        print(f"✅ Visible: {emoji_results['visible']}")
        print(f"❌ Empty: {emoji_results['empty']}")

        if emoji_results['empty'] > 0:
            print(f"\n⚠️  WARNING: {emoji_results['empty']} boxes are empty!")
            print("First 5 empty boxes:")
            empty_boxes = [d for d in emoji_results['details'] if '❌' in d['status']][:5]
            for detail in empty_boxes:
                print(f"  Box #{detail['index']}: {detail['status']} "
                      f"(std={detail['std_dev']:.1f}, brightness={detail['brightness']:.1f})")

        # Test 2: Icon containment
        print("\n📊 TEST 2: Icon Containment (Within Red Borders)")
        print("-" * 60)
        containment_results = self.check_icon_containment(boxes)

        print(f"Total boxes: {containment_results['total']}")
        print(f"✅ Contained: {containment_results['contained']}")
        print(f"❌ Overflow: {containment_results['overflow']}")

        if containment_results['overflow'] > 0:
            print(f"\n⚠️  WARNING: {containment_results['overflow']} boxes have content overflow!")
            overflow_boxes = [d for d in containment_results['details'] if '❌' in d['status']][:5]
            for detail in overflow_boxes:
                print(f"  Box #{detail['index']}: {detail['status']}")

        # Generate annotated screenshot
        output_path = str(self.screenshot_path.parent / f"{self.screenshot_path.stem}_annotated.png")
        self.generate_annotated_screenshot(boxes, emoji_results, output_path)

        # Final verdict
        print("\n" + "="*60)
        all_visible = emoji_results['empty'] == 0
        all_contained = containment_results['overflow'] == 0

        if all_visible and all_contained:
            print("✅ ALL TESTS PASSED")
        else:
            print("❌ TESTS FAILED")
            if not all_visible:
                print(f"   - {emoji_results['empty']} emojis not visible")
            if not all_contained:
                print(f"   - {containment_results['overflow']} icons overflow borders")

        print("="*60 + "\n")

        return all_visible and all_contained


def main():
    """Main test runner"""
    import argparse

    parser = argparse.ArgumentParser(description='Visual regression test for Icon Picker')
    parser.add_argument('screenshot', help='Path to screenshot PNG file')
    args = parser.parse_args()

    # Run tests
    tester = IconPickerVisualTest(args.screenshot)
    success = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
