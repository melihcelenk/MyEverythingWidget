#!/bin/bash

# Run Unit and Integration Tests (pytest-based)
# NOTE: This does NOT run humanized UI tests. Use test_humanized_ui.bat for UI tests.
# Usage: ./run_all_tests.sh [options]

cd "$(dirname "$0")/.."

echo "Running unit and integration tests (pytest)..."
echo "NOTE: This does NOT include humanized UI tests. Use test_humanized_ui.bat for UI tests."
echo

.venv/bin/python -m pytest tests/unit/ tests/integration/ -v "$@"

if [ $? -eq 0 ]; then
    echo
    echo "All tests passed!"
else
    echo
    echo "Some tests failed."
    exit $?
fi

