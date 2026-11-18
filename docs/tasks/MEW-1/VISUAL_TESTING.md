# Visual Icon Picker Testing

## Overview

Comprehensive visual testing infrastructure for the icon picker dialog, ensuring:
- All emojis/icons are visible
- No overlapping containers
- Proper spacing and alignment
- Centered icons/emojis with appropriate padding

## Test Types

### 1. Flutter Widget Tests
- **Location:** `test/widgets/icon_picker_visual_validation_test.dart`
- **Tests:**
  - Emoji grid displays with red borders
  - Icon grid displays with red borders
  - Grid spacing configuration (8px minimum)
  - Grid delegate validation

### 2. Python Visual Matching Tests
- **Location:** `test/visual/visual_icon_test.py`
- **Tests:**
  - Red border detection in screenshots
  - Overlap detection (no containers touching)
  - Centering validation (2px tolerance)
  - Padding measurement (2-20px range)

### 3. Golden Tests
- **Location:** `test/widgets/icon_picker_golden_test.dart`
- **Tests:**
  - Emoji grid layout snapshot
  - Icon grid layout snapshot
  - Upload area layout snapshot

## Running Tests

### Flutter Tests
```bash
flutter test
```

### Visual Tests (Python)
```bash
# Setup
pip install -r test/visual/requirements.txt

# Run
python test/visual/run_visual_tests.py
```

### Automated (Windows)
```bash
test\visual\run_flutter_and_test.bat
```

## Test Mode Features

### Red Borders
- All emoji/icon containers have red borders (1px width)
- Makes visual validation easier
- Can be toggled off in production if needed

### Spacing Configuration
- **Grid spacing:** 8px (mainAxisSpacing, crossAxisSpacing)
- **Container padding:** 8px outer padding
- **Border width:** 1px red border

## Validation Criteria

### ✅ Pass Conditions
1. All containers have red borders visible
2. No two containers overlap (2px tolerance)
3. Icons/emojis centered within containers (2px tolerance)
4. Padding between 2-20px on all sides
5. Grid spacing at least 8px

### ❌ Fail Conditions
- Missing red borders
- Overlapping containers (>2px² overlap)
- Mis-centered icons (>2px offset)
- Padding outside 2-20px range
- Grid spacing < 8px

## Troubleshooting

### Emojis Not Visible
- Check TabBarView physics (AlwaysScrollableScrollPhysics)
- Verify LayoutBuilder is used
- Check GridView shrinkWrap (should be false)

### Icons Overlapping
- Verify spacing is 8px minimum
- Check container padding
- Ensure GridView padding is zero

### Drag & Drop Not Working
- Verify `desktop_drop` package is installed
- Check DropTarget widget usage
- Ensure file path handling is correct

