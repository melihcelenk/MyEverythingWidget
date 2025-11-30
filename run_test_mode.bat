@echo off
REM Run app in TEST MODE with separate state file

set MEW_STATE_PATH=%~dp0tests\tmp\app_state.json
.\.venv\Scripts\python.exe main.py

