@echo off
setlocal enabledelayedexpansion

REM Humanized UI Test Runner - Real UI testing with pyautogui
REM Usage: test_humanized_ui.bat [test_name]

cd /d "%~dp0\.."

if "%1"=="" (
    "%~dp0..\.venv\Scripts\python.exe" "%~dp0humanized_ui_runner.py"
) else (
    "%~dp0..\.venv\Scripts\python.exe" "%~dp0humanized_ui_runner.py" %1
)

