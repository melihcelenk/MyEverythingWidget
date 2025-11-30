@echo off
REM Run app in TEST MODE with separate state file

cd /d "%~dp0\.."
set MEW_STATE_PATH=%~dp0..\tests\tmp\app_state.json
.\.venv\Scripts\python.exe main.py

