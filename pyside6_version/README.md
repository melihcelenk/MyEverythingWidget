# My Everything Widget - PySide6 Version

PySide6 implementation of My Everything Widget desktop application.

## Features Implemented ✅

### Core Features
- ✅ Main window with custom title bar
- ✅ Drag-to-move window functionality
- ✅ Always-on-top toggle
- ✅ Category tabs (All, Web, Dev, Media)
- ✅ Scrollable app grid (3 columns)
- ✅ Dynamic app cards with icons

### App Management
- ✅ Add new apps via dialog
- ✅ Edit existing apps
- ✅ Rename apps
- ✅ Delete apps (via context menu)
- ✅ Browse button for file selection
- ✅ Auto-fill app name from file name

### Icon System
- ✅ Notion-style icon picker
- ✅ Emoji selection (48 emojis)
- ✅ Material icon selection
- ✅ Custom image upload
- ✅ Icon preview in dialogs
- ✅ Context menu for icon change

### UI/UX
- ✅ App card tooltips (500ms delay, only for truncated text)
- ✅ Context menu (right-click) on app cards
- ✅ Floating add button (bottom right)
- ✅ Clean, modern UI styling
- ✅ Responsive layout

## Project Structure

```
pyside6_version/
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
└── tests/                  # Unit tests
    ├── test_app_state.py
    └── test_app_card.py
```

## Setup

### Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r tests/visual/requirements.txt

# Run application
python main.py

# Run tests
pytest tests/
```

### Without Virtual Environment

```bash
# Install dependencies (may require admin rights)
pip install --user -r requirements.txt
pip install --user -r tests/visual/requirements.txt

# Run application
python main.py

# Run tests
pytest tests/
```

## Quick Start (After Setup)

**IMPORTANT**: Always activate virtual environment first!

```powershell
# Method 1: Quick launcher (recommended)
.\run.bat          # Windows CMD
.\run.ps1          # Windows PowerShell

# Method 2: Manual
.\venv\Scripts\Activate.ps1    # Activate venv
python main.py                 # Run app
```

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

## Comparison with Flutter Version

| Feature | Flutter | PySide6 |
|---------|---------|---------|
| Development Speed | Fast | Moderate |
| Memory Usage | 70-100 MB | 40-60 MB |
| Binary Size | 15-25 MB | 50-70 MB |
| Store Deployment | ⭐⭐⭐⭐⭐ Automated | ⭐⭐ Manual |
| Cross-Platform | ✅ Excellent | ✅ Excellent |
| Code Quality | Clean | Clean |

## Notes

- This is a parallel implementation matching the Flutter version's functionality
- All core features from Flutter version are implemented
- Test-driven development approach used
- Code follows clean code and OOP principles
