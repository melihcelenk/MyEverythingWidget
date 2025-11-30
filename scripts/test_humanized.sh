#!/bin/bash

# Humanized Test Runner for Unix/Linux/Mac
# Usage: ./test_humanized.sh [test_name]

cd "$(dirname "$0")/.."

if [ -z "$1" ]; then
    ./.venv/bin/python tests/humanized_runner.py
else
    ./.venv/bin/python tests/humanized_runner.py "$1"
fi

