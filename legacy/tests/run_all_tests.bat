@echo off
setlocal enabledelayedexpansion

REM Run Unit and Integration Tests (pytest-based)
REM NOTE: This does NOT run humanized UI tests. Use test_humanized_ui.bat for UI tests.
REM Usage: run_all_tests.bat [options]

cd /d "%~dp0\.."

echo Running unit and integration tests (pytest)...
echo NOTE: This does NOT include humanized UI tests. Use test_humanized_ui.bat for UI tests.
echo.

.\.venv\Scripts\python.exe -m pytest tests/unit/ tests/integration/ -v %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All tests passed!
) else (
    echo.
    echo Some tests failed.
    exit /b %ERRORLEVEL%
)

