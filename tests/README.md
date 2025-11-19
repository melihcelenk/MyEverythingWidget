# Testing Guide

## Overview

This project uses pytest for unit testing and visual regression testing for UI components.

## Running Tests

### Unit Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test file
pytest tests/test_app_state.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Visual Tests

Visual regression tests for icon picker dialog:

```bash
cd tests/visual
pip install -r requirements.txt
python run_visual_test.py
```

## Test Structure

```
tests/
├── test_app_state.py      # AppState unit tests
├── test_app_card.py       # AppCard widget tests
└── visual/                # Visual regression tests
    ├── test_icon_picker_visual.py
    └── run_visual_test.py
```

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

### Widget Test Example

```python
def test_app_card_creation(qapp):
    """Test creating an app card."""
    app = AppShortcut(...)
    card = AppCard(app=app, on_tap=lambda: None)
    
    assert card is not None
    assert card._app == app
```

## Test Coverage

Current coverage:
- AppState: ✅ Complete
- AppCard: ✅ Basic coverage
- Services: ⚠️ Needs improvement
- Widgets: ⚠️ Needs improvement

## Best Practices

1. **AAA Pattern**: Arrange, Act, Assert
2. **Descriptive Names**: Test names should describe what they test
3. **One Assertion**: One concept per test
4. **Isolation**: Tests should not depend on each other
5. **Fast**: Tests should run quickly

