# Testing Guide

## Quick Start

**Most common commands:**

```bash
# Run unit and integration tests (pytest-based tests)
.\tests\run_all_tests.bat

# Run humanized UI tests (drag-and-drop, DSL format) ⭐ MAIN UI TESTS
.\tests\test_humanized_ui.bat

# Run app in test mode (uses test state file)
.\tests\run_test_mode.bat
```

**Note:** `run_all_tests.bat` only runs unit and integration tests. It does NOT run humanized UI tests. Use
`test_humanized_ui.bat` for UI tests.

## Test Scripts Overview

### Main Test Runners

| Script                      | Purpose                                  | When to Use                                                      |
|-----------------------------|------------------------------------------|------------------------------------------------------------------|
| `run_all_tests.bat`         | Runs unit and integration tests (pytest) | Before committing, to verify pytest tests work                   |
| `run_all_tests.sh`          | Same as above, for Linux/Mac             | Linux/Mac users                                                  |
| **`test_humanized_ui.bat`** | **Runs humanized UI tests (DSL format)** | **Testing drag-and-drop, UI interactions - MAIN UI TEST SYSTEM** |
| `run_test_mode.bat`         | Launches app with test state file        | Manual testing with isolated state                               |

**Important:** `run_all_tests.bat` does NOT include humanized UI tests. Use `test_humanized_ui.bat` separately for UI
tests.

### Python Files in tests/

| File                     | Purpose                                            | Notes                                                            |
|--------------------------|----------------------------------------------------|------------------------------------------------------------------|
| `__init__.py`            | Makes `tests/` a Python package                    | Empty file, just marks directory as package                      |
| `conftest.py`            | **Pytest configuration**                           | Automatically loaded by pytest. Sets up paths and mocks dialogs. |
| `humanized_ui_runner.py` | **Python script that executes humanized UI tests** | Called by `test_humanized_ui.bat` - **MAIN UI TEST RUNNER**      |

## Test Structure

```
tests/
├── __init__.py              # Python package marker (must be in root)
├── conftest.py              # Pytest configuration (must be in root for all tests)
├── humanized_ui_runner.py   # Humanized UI test runner script
├── README.md                # This file
│
├── unit/                    # Unit tests (isolated component tests)
│   ├── test_app_state.py
│   ├── test_app_card.py
│   └── ...
├── integration/             # Integration tests (component interaction)
│   ├── test_main_window.py
│   ├── test_drag_drop.py
│   └── ...
├── humanized/               # Humanized UI tests (DSL format)
│   └── drag/
│       ├── swap_note_and_app.dsl
│       └── 2x1_note_right_edge.dsl
├── visual/                  # Visual regression tests
│   └── ...
├── helpers/                 # Test helper utilities
│   └── grid_test_dsl.py
├── state/                   # Test state templates
│   └── initial_test_state.json
└── tmp/                     # Temporary test files (gitignored)
    └── app_state.json
```

**File Location Notes:**

- `__init__.py` - **Must be in root** (makes tests/ a Python package)
- `conftest.py` - **Must be in root** (pytest automatically loads it for all tests)
- `humanized_ui_runner.py` - **Can stay in root** (runner script, called by .bat files)

## Running Tests

### Unit and Integration Tests (Pytest-based)

**Note:** These are pytest-based tests. They do NOT include humanized UI tests.

```bash
# Run all unit and integration tests (pytest only)
.\tests\run_all_tests.bat

# Or using pytest directly
pytest tests/unit/ tests/integration/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/unit/test_app_state.py -v
```

### Humanized UI Tests ⭐ **MAIN TEST SYSTEM**

These tests use a DSL (Domain-Specific Language) format for testing UI interactions. **This is the primary test system
for UI operations.**

```bash
# Run all humanized UI tests
.\tests\test_humanized_ui.bat

# Run specific test
.\tests\test_humanized_ui.bat swap_note_and_app
# or
.\tests\test_humanized_ui.bat swap_note_and_app.dsl
```

**Test files are located in `tests/humanized/drag/` and use the `.dsl` extension.**

See [Development Guidelines](../docs/general/DEVELOPMENT.md) for DSL format details.

### Visual Regression Tests

```bash
cd tests/visual
pip install -r requirements.txt
python run_visual_test.py
```

### Test Mode (Manual Testing)

Run the application with a test state file (isolated from your real data):

```bash
.\tests\run_test_mode.bat
```

This sets `MEW_STATE_PATH` to `tests/tmp/app_state.json` so your real app state won't be affected.

## Test Types

### Unit Tests (`tests/unit/`)

Isolated component tests:

- `test_app_state.py` - State management
- `test_app_card.py` - Widget creation
- `test_app_launcher.py` - Service logic
- `test_clipboard_paste.py` - Service logic
- `test_grid_layout.py` - Grid calculations
- `test_note_model.py` - Model logic
- And more...

### Integration Tests (`tests/integration/`)

Component interaction tests:

- `test_main_window.py` - Window with multiple components
- `test_drag_drop.py` - Grid drag-and-drop with state
- `test_memory_leak.py` - Memory management

### Humanized UI Tests (`tests/humanized/`)

DSL-based UI interaction tests for drag-and-drop operations.

### Visual Tests (`tests/visual/`)

Screenshot-based visual regression tests.

## Test State Management

- **Template state**: `tests/state/initial_test_state.json` (git committed)
- **Working state**: `tests/tmp/app_state.json` (created during tests, gitignored)
- Tests automatically copy template to working state before running
- Test mode uses `tests/tmp/app_state.json` to avoid affecting real app state

## Writing Tests

### Unit Test Example

```python
def test_add_app():
    """Test adding a new app."""
    app_state = AppState()
    initial_count = len(app_state.apps)
    
    new_app = AppShortcut(...)
    app_state.add_app(new_app)
    
    assert len(app_state.apps) == initial_count + 1
```

### Humanized UI Test Example

Create a `.dsl` file in `tests/humanized/drag/`:

**Example 1: Drag and Drop**
```
Rows: 5
Columns: 5

Initial:
.  .  .  .  .
N1 N1 .  .  A1
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .

Action:
Drag(N1,R1C3)

Expected:
.  .  .  .  .
A1 .  .  N1 N1
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
```

**Example 2: Create and Drag**

```
Rows: 5
Columns: 5

Initial:
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .

Action:
Create(NOTE, "Test Note", N1)
Create(APP, "Test App", A1)
Drag(N1, R1C2)

Expected:
.  .  .  .  .
.  .  N1 .  A1
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
```

**Example 3: Create, Launch, and Drag**

```
Rows: 5
Columns: 5

Initial:
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .

Action:
Create(APP, "Test App", A1)
Launch(A1)
Create(NOTE, "Test Note", N1)

Expected:
.  .  .  .  .
A1 .  .  .  N1
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
```

## Best Practices

1. **AAA Pattern**: Arrange, Act, Assert
2. **Descriptive Names**: Test names should describe what they test
3. **One Assertion**: One concept per test
4. **Isolation**: Tests should not depend on each other
5. **Fast**: Tests should run quickly
6. **Automated**: Never ask users to manually test - write automated tests

## Need Help?

- See [Development Guidelines](../docs/general/DEVELOPMENT.md) for detailed testing procedures
- See [Contributing Guide](../docs/general/CONTRIBUTING.md) for code style and setup
