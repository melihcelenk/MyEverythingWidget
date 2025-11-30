# Architecture Documentation

## Overview

My Everything Widget follows a clean architecture pattern with clear separation of concerns:

- **Models**: Data structures and business entities
- **Services**: Business logic and external integrations
- **Window**: Application state management
- **Widgets**: UI components (views)
- **Tests**: Unit and integration tests

## Design Principles

### Clean Code

1. **Single Responsibility Principle (SRP)**
    - Each class has one reason to change
    - Example: `AppCard` only handles app card display, not app launching

2. **Open/Closed Principle (OCP)**
    - Open for extension, closed for modification
    - Example: New icon types can be added without modifying `IconPickerDialog`

3. **Dependency Inversion Principle (DIP)**
    - Depend on abstractions, not concretions
    - Example: `MainWindow` depends on `AppState` interface, not implementation

### OOP Principles

1. **Encapsulation**
    - Private attributes (prefixed with `_`)
    - Public methods for controlled access
    - Example: `AppState._apps` is private, accessed via `filtered_apps` property

2. **Inheritance**
    - Widget classes inherit from PySide6 base classes
    - Example: `AppCard(QWidget)`, `MainWindow(QMainWindow)`

3. **Polymorphism**
    - Interface-based design
    - Example: All widgets implement consistent interfaces

4. **Abstraction**
    - Clear separation between interface and implementation
    - Example: `AppLauncherService` abstracts platform-specific launching

## Component Architecture

### Models Layer

**Purpose**: Define data structures and business entities

**Location**: `models/` and `window/models/`

**Components**:

- `AppShortcut`: Represents an application shortcut (EXE, URL, FOLDER)
- `AppCategory`: Represents a category for organizing apps
- `LaunchType`: Enum for different launch types (EXE, URL, FOLDER)
- `Note`: Represents a note with content, position, and span information

**Responsibilities**:

- Data validation
- Business rule enforcement
- Immutability where appropriate

### Services Layer

**Purpose**: Handle business logic and external integrations

**Location**: `services/`

**Components**:

- `AppLauncherService`: Launches applications, URLs, and folders
- `StorageService`: Manages persistent state storage (JSON)
- `ClipboardService`: Handles clipboard operations
- `ImageCacheService`: Manages image caching
- `ImageStorageService`: Handles image storage
- `ImageGridCalculator`: Calculates image grid dimensions

**Responsibilities**:

- Platform-specific operations
- External system integration
- Error handling
- Data persistence

### Window Layer

**Purpose**: Manage application state and coordinate components

**Location**: `window/`

**Components**:

- `AppState`: Global application state manager (categories, apps, notes)
- `ContentManager`: Main coordinator for UI components (replaces TabManager wrapper)
- `MainWindow`: Main application window controller
- `DialogManager`: Manages all dialog operations
- `TabManager`: Tab management (located in `window/ui/tabs/`)
- `GridPopulator`: Populates grid with items
- `ItemMover`: Handles drag-and-drop operations
- `NoteActions`: Manages note-related actions

**Responsibilities**:

- State management
- Component coordination
- Event handling
- Grid layout management

### Widgets Layer

**Purpose**: UI components and user interaction

**Location**: `widgets/`

**Components**:

- `CustomTitleBar`: Custom window title bar with drag-to-move
- `AppCard`: Individual app card display
- `NoteCard`: Individual note card display
- `ImageCard`: Individual image card display
- `AddItemDialog`: Unified dialog for adding apps, notes, and images
- `AppPickerDialog`: Dialog for editing apps
- `IconPickerDialog`: Dialog for selecting icons (emoji, material icons, custom)
- `DraggableTabBar`: Draggable tab bar for categories
- `GridDropZone`: Grid drop zone for drag-and-drop
- `DraggableMixin`: Mixin for draggable widgets
- `ResizableMixin`: Mixin for resizable widgets

**Responsibilities**:

- UI rendering
- User input handling
- Visual feedback
- Drag-and-drop interactions

## Data Flow

```
User Action
    ↓
Widget (UI)
    ↓
ContentManager (Coordinator)
    ↓
AppState (State Manager)
    ↓
Service (Business Logic)
    ↓
External System / State Update
    ↓
Signal Emission (state_changed)
    ↓
ContentManager Refresh
    ↓
UI Update (GridPopulator, TabManager)
```

## State Management

### AppState Pattern

`AppState` uses Qt's signal/slot mechanism for reactive updates:

1. **State Changes**: Methods like `add_app()`, `remove_app()` modify state
2. **Signal Emission**: `state_changed` signal is emitted
3. **UI Updates**: Connected slots update UI components

### Example Flow

```python
# User adds app via AddItemDialog
dialog = AddItemDialog()
if dialog.exec():
    app = dialog.get_app()
    app_state.add_app(app)  # Modifies state
    # state_changed signal emitted
    # ContentManager._on_state_changed() called
    # GridPopulator refreshes grid
    # UI updated automatically
```

## Error Handling

### Strategy

1. **Service Layer**: Catches and logs platform-specific errors
2. **Window Layer**: Shows user-friendly error messages
3. **Widget Layer**: Handles UI-specific errors gracefully

### Example

```python
# Service layer
def launch(self, shortcut: AppShortcut) -> bool:
    try:
        # Platform-specific code
        return True
    except Exception as e:
        logger.error(f"Failed to launch {shortcut.name}: {e}")
        return False


# Window layer
def _launch_app(self, app: AppShortcut):
    success = self._launcher_service.launch(app)
    if not success:
        QMessageBox.warning(self, "Error", f"Failed to launch {app.name}")
```

## Testing Strategy

### Unit Tests

- Test individual components in isolation
- Mock dependencies
- Focus on business logic

### Integration Tests

- Test component interactions
- Verify state management
- Check UI updates

### Visual Tests

- Screenshot-based regression tests
- Verify rendering correctness
- Detect visual regressions

## Extension Points

### Adding New Launch Types

1. Add enum value to `LaunchType`
2. Update `AppLauncherService.launch()`
3. Update `AppCard._get_icon_for_type()`

### Adding New Widgets

1. Inherit from appropriate PySide6 base class
2. Follow widget naming conventions
3. Add to `widgets/__init__.py`
4. Write tests
5. If draggable/resizable, use `DraggableMixin`/`ResizableMixin`

### Adding New Categories

1. Categories are managed dynamically via `AppState.add_category()`
2. UI updates automatically via signals
3. Categories are persisted to JSON state file

### Adding New Item Types

1. Add model class (e.g., `Image` in `window/models/`)
2. Update `AppState` to manage the new type
3. Create card widget (e.g., `ImageCard`)
4. Update `CardFactory` to create the new card type
5. Update `GridPopulator` to handle the new type
6. Update `AddItemDialog` to support creating the new type

## Performance Considerations

1. **Lazy Loading**: Load apps only when needed
2. **Signal Optimization**: Minimize signal emissions
3. **Widget Reuse**: Reuse widgets where possible
4. **Memory Management**: Proper cleanup of widgets

## Security Considerations

1. **Input Validation**: Validate all user inputs
2. **Path Sanitization**: Sanitize file paths
3. **Error Messages**: Don't expose sensitive information
4. **Platform Security**: Follow platform security best practices

