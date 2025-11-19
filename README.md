# My Everything Widget

A lightweight, modern desktop widget application for quick access to your favorite applications, organized by categories. Built with PySide6 for cross-platform desktop support.

## Features

### Core Features
- **Application Launcher** - Quick access to your favorite apps with icon grid
- **Category Tabs** - Organize apps into categories (All, Web, Dev, Media, etc.)
- **Notion-style Icon Picker** - Choose from emojis, material icons, or upload custom images
- **Always-on-top** - Keep the widget visible while working
- **Drag-to-move** - Custom title bar for easy window positioning
- **Dynamic App Management** - Add, edit, rename, and delete apps on the fly
- **Dynamic Category Management** - Add, edit, and delete categories with context menu

### UI/UX
- **Modern Design** - Clean, Material Design-inspired interface
- **Smooth Interactions** - Hover effects, click feedback, and smooth transitions
- **Context Menus** - Right-click on app cards and tabs for quick actions
- **Smart Tooltips** - Automatic tooltips for long app names
- **Responsive Layout** - 3-column grid layout (Android/Windows Explorer style)

## Quick Start

### Prerequisites

- Python 3.10 or higher
- PySide6 6.6.0 or higher

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/MyEverythingWidget.git
   cd MyEverythingWidget
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Windows CMD
   python -m venv venv
   venv\Scripts\activate.bat
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   # Quick launcher (Windows)
   .\run.bat          # CMD
   .\run.ps1          # PowerShell
   
   # Manual
   python main.py
   ```

## Project Structure

```
MyEverythingWidget/
├── main.py                 # Application entry point
├── models/                 # Data models
│   ├── app_shortcut.py    # AppShortcut and LaunchType
│   └── category.py        # AppCategory
├── window/                 # Window components
│   ├── main_window.py     # Main application window
│   └── app_state.py       # Global state management
├── widgets/                # UI widgets
│   ├── custom_title_bar.py
│   ├── app_card.py
│   ├── add_app_button.py
│   ├── app_picker_dialog.py
│   └── icon_picker_dialog.py
├── services/               # Business logic
│   └── app_launcher_service.py
├── tests/                  # Unit and visual tests
│   ├── test_app_state.py
│   ├── test_app_card.py
│   └── visual/            # Visual regression tests
├── flutter_version/        # Flutter implementation (legacy)
└── docs/                   # Documentation
```

## Testing

### Unit Tests

The project has comprehensive unit tests covering:
- App state management (add, update, remove apps/categories)
- App card creation with various icon types (emoji, image, default)
- Main window tab switching and state changes
- Tab management operations

```bash
# Run all unit tests
python -m pytest tests/ -v --ignore=tests/visual

# Run specific test file
python -m pytest tests/test_app_state.py -v
python -m pytest tests/test_app_card.py -v
python -m pytest tests/test_main_window.py -v

# Run with coverage
python -m pytest tests/ -v --cov=. --cov-report=html
```

**Test Coverage:**
- `test_app_state.py` - State management tests
- `test_app_card.py` - Widget creation with all icon types
- `test_main_window.py` - Window operations, tab switching, state changes
- `test_tab_management.py` - Tab creation, removal, updates

## Architecture

### Clean Code Principles

- **Single Responsibility**: Each class has one clear purpose
- **Separation of Concerns**: Models, views, and services are separated
- **DRY**: No code duplication
- **Descriptive Names**: Clear, self-documenting code
- **Small Methods**: Methods are focused and testable

### OOP Principles

- **Encapsulation**: Private attributes with public interfaces
- **Inheritance**: Widget classes inherit from PySide6 base classes
- **Polymorphism**: Interface-based design
- **Abstraction**: Clear separation between interface and implementation

## Development

### Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all public methods and classes
- Keep methods small and focused (< 50 lines)

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Write tests first (TDD approach)
3. Implement feature
4. Ensure all tests pass
5. Update documentation
6. Submit pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Acknowledgments

- Built with [PySide6](https://www.qt.io/qt-for-python) - Qt for Python
- Inspired by modern desktop widget applications

---

**Status:** Active Development  
**Platform:** Windows, Linux, macOS  
**Language:** Python 3.10+
