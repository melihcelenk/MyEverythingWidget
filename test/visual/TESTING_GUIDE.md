# Visual Icon Picker Testing Guide

## Overview

This directory contains visual regression tests for the icon picker dialog. These tests use screenshot analysis to verify:
- ✅ All emojis/icons are visible
- ✅ No overlapping containers
- ✅ Proper spacing between items
- ✅ Icons/emojis are centered within their containers
- ✅ Proper padding around icons/emojis

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Flutter app is built:
```bash
flutter pub get
```

## Running Visual Tests

### Method 1: Automated (Windows)

```bash
test\visual\run_flutter_and_test.bat
```

This will:
1. Start the Flutter app
2. Wait for you to take screenshots
3. Run visual tests
4. Clean up

### Method 2: Manual

1. Run Flutter app:
```bash
flutter run -d windows
```

2. Open icon picker dialog
3. Take screenshots:
   - Emoji tab: `test/visual/screenshots/emoji_grid.png`
   - Icons tab: `test/visual/screenshots/icon_grid.png`

4. Run tests:
```bash
python test/visual/run_visual_tests.py
```

## What the Tests Check

### Red Border Detection
- Finds all red borders (test mode indicator)
- Verifies each container has a red border

### Overlap Detection
- Checks that no two red-bordered containers overlap
- Allows 2px tolerance for border rendering

### Centering Detection
- Verifies icon/emoji is centered within container
- Checks offset from container center (max 2px tolerance)

### Padding Detection
- Measures distance from icon/emoji to container edges
- Verifies padding is between 2-20px

## Test Results

Tests output detailed information:
- Number of containers found
- Overlap issues (if any)
- Centering issues (if any)
- Padding issues (if any)

## Troubleshooting

### "No red borders found"
- Ensure test mode is enabled (red borders should be visible)
- Check screenshot quality and format (PNG recommended)

### "Overlapping containers"
- Check grid spacing configuration
- Verify `mainAxisSpacing` and `crossAxisSpacing` are at least 8px

### "Mis-centered icons"
- Check Container alignment
- Verify Center widget is used

### "Padding issues"
- Check Container padding
- Verify icon/emoji size vs container size

