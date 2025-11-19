# Visual Tests for PySide6 Version

Visual regression tests for Icon Picker Dialog using screenshot analysis.

## Setup

```bash
# Make sure you're in the virtual environment
# Activate it first if not already activated:
# Windows PowerShell: .\venv\Scripts\Activate.ps1
# Windows CMD: venv\Scripts\activate.bat

# Install visual test dependencies
pip install -r requirements.txt
```

## Running Tests

### Manual Screenshot Method (Recommended)

1. **Start the PySide6 app:**
   ```bash
   python main.py
   ```

2. **Open the icon picker dialog:**
   - Click the green '+' button to add an app
   - Click the icon selector (icon preview area) to open icon picker dialog
   - Make sure you're on the 'Emoji' tab (should be selected by default)

3. **Run the visual test:**
   ```bash
   # Windows
   python run_visual_test.py
   # or
   .\run_tests.bat
   
   # Linux/Mac
   python run_visual_test.py
   # or
   chmod +x run_tests.sh
   ./run_tests.sh
   ```

4. **Follow the prompts:**
   - The script will wait 10 seconds for you to prepare
   - It will take a screenshot of the emoji tab
   - Then wait 3 seconds for you to switch to the Icons tab
   - It will take a screenshot of the icons tab
   - Finally, it will run the visual tests

### Automated Method (Future)

The `run_tests_auto.py` script attempts to automatically take screenshots, but requires the app to be running in the same process. This is more complex and may not work reliably.

## Test Coverage

- ✅ Emoji tab verification
- ✅ Red border detection (1px solid red borders on emoji/icon containers)
- ✅ Emoji container visibility (at least 6 visible in first row)
- ✅ Content visibility within containers (emojis/icons must be visible)
- ✅ Overlap detection (containers should not overlap)
- ✅ Centering validation (content should be centered within containers)
- ✅ Icon grid validation

## Expected Results

- **Emoji Tab:**
  - At least 6 emoji containers visible (first row with 6 columns)
  - All containers have visible emoji content (colorful pixels)
  - No significant overlaps (tolerance: 10px)
  - Content is centered within containers (20% tolerance)

- **Icon Tab:**
  - At least 6 icon containers visible (first row with 6 columns)
  - All containers have visible icon content (dark pixels or contrast)
  - No significant overlaps

## Test Output

The test will print:
- `[OK]` for successful checks
- `ERROR:` for failures
- `WARNING:` for non-critical issues
- `DEBUG:` information for troubleshooting

## Troubleshooting

### "No red borders found"
- Make sure the icon picker dialog is open
- Make sure you're on the Emoji or Icons tab
- Check that the dialog has red borders (1px solid red) on emoji/icon containers

### "Found only X visible containers, expected at least 6"
- The GridView may not be rendering properly
- Try scrolling down to see if more containers appear
- Check that the dialog is fully visible on screen

### "Found X empty containers"
- Emojis/icons may not be rendering
- Check font rendering on your system
- Verify that emoji font is installed (Windows: Segoe UI Emoji)

### Screenshot not found
- Make sure the script is run from the `tests/visual/` directory
- Check that screenshots are being saved correctly
- Verify file permissions

## Integration with Development Workflow

These visual tests should be run:
1. **Before committing** - Ensure UI changes don't break rendering
2. **After UI changes** - Verify emojis/icons still render correctly
3. **During debugging** - When emoji/icon rendering issues are reported

## Notes

- Screenshots are saved in `tests/visual/` directory
- Screenshots are automatically ignored by git (see `.gitignore`)
- The test uses computer vision (OpenCV, NumPy) to analyze screenshots
- Red borders are used for visual testing and should remain in the code during development
