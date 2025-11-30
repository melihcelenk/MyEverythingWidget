@echo off
setlocal enabledelayedexpansion

REM Humanized UI Test Runner - Real UI testing with pyautogui
REM Usage: test_humanized_ui.bat [test_name]

cd /d "%~dp0"

if "%1"=="" (
    .\.venv\Scripts\python.exe tests\humanized_ui_runner.py
) else (
    .\.venv\Scripts\python.exe tests\humanized_ui_runner.py %1
)

