@echo off
echo Running tests...
venv\Scripts\python -m pytest tests/ --tb=short --ignore=tests/visual -q
pause
