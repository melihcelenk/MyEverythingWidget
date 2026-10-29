# Contributing to My Everything Widget

Thank you for your interest in contributing to My Everything Widget! This document provides guidelines and instructions
for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/MyEverythingWidget/issues)
2. If not, create a new issue with:
    - Clear title and description
    - Steps to reproduce
    - Expected vs actual behavior
    - Environment details (OS, Python version, etc.)
    - Screenshots if applicable

### Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue with:
    - Clear description of the feature
    - Use case and benefits
    - Possible implementation approach (optional)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Follow coding standards:**
    - Follow PEP 8 style guide
    - Use type hints where appropriate
    - Write docstrings for public methods/classes
    - Keep methods small and focused

4. **Write tests:**
    - Add unit tests for new features
    - Ensure all existing tests pass
    - Aim for good test coverage

5. **Update documentation:**
    - Update README if needed
    - Add docstrings to new code
    - Update [CHANGELOG.md](CHANGELOG.md)
    - Update [ARCHITECTURE.md](ARCHITECTURE.md) if structure changes

6. **Commit your changes:**
   ```bash
   git commit -m "feat: add your feature description"
   ```

   Use conventional commit messages:
    - `feat:` for new features
    - `fix:` for bug fixes
    - `docs:` for documentation
    - `test:` for tests
    - `refactor:` for refactoring
    - `style:` for formatting

7. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request:**
    - Provide clear description
    - Reference related issues
    - Wait for review and feedback

## Development Setup

1. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/MyEverythingWidget.git
   cd MyEverythingWidget
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r tests/visual/requirements.txt
   ```

4. **Run tests:**
   ```bash
   # Run all unit and integration tests
   pytest tests/unit/ tests/integration/ -v
   
   # Or use the test runner script
   .\tests\run_all_tests.bat
   
   # Run only unit tests
   pytest tests/unit/ -v
   
   # Run only integration tests
   pytest tests/integration/ -v
   
   # Run humanized UI tests
   .\tests\test_humanized_ui.bat
   
   # Run specific test file
   pytest tests/unit/test_app_state.py -v
   ```

## Code Style

- **PEP 8**: Follow Python PEP 8 style guide
- **Type Hints**: Use type hints for function parameters and return types
- **Docstrings**: Use Google-style docstrings
- **Line Length**: Maximum 100 characters
- **Imports**: Group imports (stdlib, third-party, local)

Example:

```python
"""Module docstring."""

from typing import List, Optional
from PySide6.QtWidgets import QWidget

from models.app_shortcut import AppShortcut


class MyWidget(QWidget):
    """Widget class docstring."""

    def __init__(self, parent=None):
        """Initialize widget.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
```

## Testing Guidelines

- Write tests for all new features
- Maintain or improve test coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

Example:

```python
def test_app_card_creation():
    """Test creating an app card."""
    # Arrange
    app = AppShortcut(...)

    # Act
    card = AppCard(app=app, on_tap=lambda: None)

    # Assert
    assert card is not None
    assert card._app == app
```

## Questions?

Feel free to open an issue for questions or reach out to maintainers.

Thank you for contributing! 🎉

