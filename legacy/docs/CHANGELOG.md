# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Grid-based Layout System**: Drag-and-drop grid layout for apps, notes, and images
- **Notes Feature**: Create, edit, resize, and manage notes with persistent storage
- **Images Feature**: Paste and manage images with grid layout
- **Humanized UI Testing**: DSL-based UI testing system for automated drag-and-drop tests
- **ContentManager**: Central coordinator replacing TabManager wrapper
- **Resizable Items**: Notes and images can be resized (1x1, 2x1, 1x2, 2x2)
- **Quick Note Entry**: Fast note creation via quick entry widget
- **Test State Management**: Isolated test state using `tests/state/initial_test_state.json`
- **Scripts Organization**: Utility scripts moved to `scripts/` directory
- **Documentation Organization**: Documentation moved to `docs/general/` directory

### Changed

- **Architecture**: Migrated from TabManager wrapper to ContentManager coordinator
- **Grid System**: Implemented collision detection and automatic positioning
- **State Management**: Enhanced state persistence with span information (row_span, col_span)
- **Test System**: Standardized test file naming to `snake_case.dsl` format
- **Project Structure**: Reorganized to standard GitHub repository structure
- **Virtual Environment**: Standardized to `.venv` directory

### Fixed

- **Span Preservation**: Fixed bug where 2x1 notes became 1x1 after drag
- **Test Automation**: Fixed manual input requirement in category creation tests
- **State Isolation**: Fixed test state pollution by using isolated temporary files

## [1.0.0] - 2025-01-XX

### Added

- Initial release
- Application launcher with icon grid
- Category tabs (All, Web, Dev, Media)
- Notion-style icon picker (Emoji, Icons, Upload)
- Dynamic app management (Add, Edit, Rename, Delete)
- Context menu for app cards
- Always-on-top window
- Drag-to-move window
- Custom title bar
- Unit tests
- Visual regression tests

[Unreleased]: https://github.com/yourusername/MyEverythingWidget/compare/v1.0.0...HEAD

[1.0.0]: https://github.com/yourusername/MyEverythingWidget/releases/tag/v1.0.0

