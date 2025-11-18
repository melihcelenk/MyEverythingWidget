#!/bin/bash
# Run Flutter app, wait for user to take screenshots, then run visual tests

echo "Starting Flutter app..."
flutter run -d windows &
FLUTTER_PID=$!

echo "Waiting for app to start..."
sleep 5

echo ""
echo "=========================================="
echo "Please:"
echo "1. Open the icon picker dialog"
echo "2. Switch to Emoji tab"
echo "3. Take screenshot and save as: test/visual/screenshots/emoji_grid.png"
echo "4. Switch to Icons tab"
echo "5. Take screenshot and save as: test/visual/screenshots/icon_grid.png"
echo "6. Press Enter when done..."
echo "=========================================="
read

echo "Running visual tests..."
python test/visual/run_visual_tests.py

# Kill Flutter app
kill $FLUTTER_PID 2>/dev/null

