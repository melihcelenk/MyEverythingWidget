@echo off
REM Quick launcher script for PySide6 app
cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py
pause

