@echo off
REM Run all tests including visual tests
cd /d "%~dp0\..\.."
echo Running unit tests...
.\venv\Scripts\python.exe -m pytest tests/ -v
echo.
echo Running visual tests...
echo Make sure the app is running and icon picker dialog is open!
cd tests\visual
.\venv\Scripts\python.exe run_visual_test.py
pause

