@echo off
REM Run Flutter app, wait for user to take screenshots, then run visual tests

echo Starting Flutter app...
start /B C:\tools\flutter\bin\flutter.bat run -d windows

echo Waiting for app to start...
timeout /t 5 /nobreak >nul

echo.
echo ==========================================
echo Please:
echo 1. Open the icon picker dialog
echo 2. Switch to Emoji tab
echo 3. Take screenshot and save as: test\visual\screenshots\emoji_grid.png
echo 4. Switch to Icons tab
echo 5. Take screenshot and save as: test\visual\screenshots\icon_grid.png
echo 6. Press Enter when done...
echo ==========================================
pause

echo Running visual tests...
python test\visual\run_visual_tests.py

REM Kill Flutter processes
taskkill /F /IM flutter.exe /T >nul 2>&1

