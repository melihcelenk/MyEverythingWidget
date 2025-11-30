@echo off
setlocal enabledelayedexpansion

REM Humanized Test Runner for Windows
REM Usage: test_humanized.bat [test_name]

cd /d "%~dp0"

if "%1"=="" (
    .\.venv\Scripts\python.exe tests\humanized_runner.py
) else (
    .\.venv\Scripts\python.exe tests\humanized_runner.py %1
)

