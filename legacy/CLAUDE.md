# Development Guidelines for AI Assistant (legacy Python version)

> This folder holds the original PySide6 version, kept as reference while the WinUI rewrite (MEW-4) replaces it.
> Run every command below from `legacy/`. The current app and its rules are in the repository root `CLAUDE.md`.

This document provides guidelines and references for AI assistants working on this project.

## Documentation

All project documentation is located in the `legacy/docs/` directory:

- **[Development Guidelines](docs/DEVELOPMENT.md)** - UI testing system, test DSL format, and testing workflow
- **[Architecture Documentation](docs/ARCHITECTURE.md)** - Project structure, component architecture, and design
  principles
- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute, code style, and development setup
- **[Changelog](docs/CHANGELOG.md)** - Project history and version changes

## Key Principles

### Testing

- **DO NOT** ask the user to manually test
- **DO** write humanized UI tests using the DSL format (see [Development Guidelines](docs/DEVELOPMENT.md))
- **DO** run tests automatically using `tests\test_humanized_ui.bat`
- **DO** verify tests pass or correctly identify bugs before fixing

### Code Quality

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for public methods and classes
- Keep methods small and focused (< 50 lines)
- Follow clean code principles (see [Architecture Documentation](docs/ARCHITECTURE.md))

### Project Structure

- Source code in root: `models/`, `services/`, `widgets/`, `window/`
- Tests in `tests/` directory (including test runner scripts)
- Scripts in `scripts/` directory (application scripts)
- Documentation in `docs/` directory
- Virtual environment: `.venv` (not `venv`)

### State Management

- Application state managed by `AppState` class
- UI coordination handled by `ContentManager`
- State persisted to JSON file (default: `%LOCALAPPDATA%\MyEverythingWidget\app_state.json`)
- Test state isolated in `tests/tmp/app_state.json` (gitignored)

## Quick Reference

### Running Tests

```bash
# Unit tests
pytest tests/ -v --ignore=tests/visual

# Humanized UI tests
.\tests\test_humanized_ui.bat

# Specific test
.\tests\test_humanized_ui.bat test_name
```

### Test File Format

Humanized tests use `.dsl` extension and `snake_case` naming:

- Location: `tests/humanized/drag/`, `tests/humanized/tabs/`, etc.
- Format: See [Development Guidelines - Test File Format](docs/DEVELOPMENT.md#test-file-format)

### Main Components

- **ContentManager**: Main UI coordinator (use this, not TabManager wrapper)
- **AppState**: Global state manager
- **GridPopulator**: Populates grid with items
- **ItemMover**: Handles drag-and-drop operations
- **NoteActions**: Manages note-related actions

For detailed architecture, see [Architecture Documentation](docs/ARCHITECTURE.md).

## Important Notes

1. **Never commit or push** - User rule: "Never commit, never push"
2. **Code must be clean** - Follow clean code principles
3. **Test-driven development** - Write tests first, then implement
4. **No Turkish comments** - All code comments must be in English
5. **Automated testing** - Always use automated tests, never ask for manual testing

## When in Doubt

- Check [Development Guidelines](docs/DEVELOPMENT.md) for testing procedures
- Check [Architecture Documentation](docs/ARCHITECTURE.md) for component structure
- Check [Contributing Guide](docs/CONTRIBUTING.md) for code style and setup
- Check existing code for patterns and conventions

