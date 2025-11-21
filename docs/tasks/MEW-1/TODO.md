# MEW-1: Development Tasks

## 📋 Task Overview

This document outlines the development tasks for MyEverythingWidget v1.0 MVP.

> **Note:** Project migrated from Flutter to PySide6 (Python). Flutter code preserved in `flutter_version/` for reference.

---

## 🎯 Current Status (PySide6)

**Platform:** PySide6 6.10.0
**Tests:** 52 tests passing
**Status:** Core features working, no crashes

### Recent Fixes
- [x] Fixed SystemError in tab switching (recursive signal emission)
- [x] Added signal blocking during tab updates
- [x] Comprehensive test coverage for:
  - App card creation (all icon types)
  - Tab switching operations
  - State management
  - Category operations

---

## 🚀 Phase 1: Project Setup & Core Window

### Task 1.1: Environment Setup
- [x] Verify Flutter installation (`flutter doctor`)
- [x] Create Flutter project (`flutter create my_everything_widget --platforms=windows,linux`)
- [x] Initialize Git repository
- [x] Add required packages to `pubspec.yaml`
  - `window_manager: ^0.3.7`
  - `provider: ^6.1.0`
  - `clipboard_watcher: ^0.2.0`
  - `msix: ^3.16.0`

### Task 1.2: Main Window Implementation
- [x] Create `lib/screens/main_window.dart`
- [x] Implement custom title bar
- [x] Add drag-to-move functionality
- [x] Configure always-on-top toggle
- [x] Set window size to 320x500
- [x] Test: Window opens and is draggable

---

## 🎯 Phase 2: Application Launcher

### Task 2.1: Data Models
- [x] Create `lib/models/app_shortcut.dart`
- [x] Define `AppShortcut` class with properties:
  - `id`, `name`, `iconPath`, `target`, `category`, `type`
- [x] Define `LaunchType` enum (exe, uwp, url)

### Task 2.2: App Card Widget
- [x] Create `lib/widgets/app_card.dart`
- [x] Implement icon + text layout
- [x] Add tap gesture handler
- [x] Style card with Material Design
- [x] Add tooltip for truncated text (500ms wait duration)

### Task 2.3: App Launcher Service
- [x] Create `lib/services/app_launcher.dart`
- [x] Implement launch logic for different types:
  - EXE: `Process.start()`
  - URL: `url_launcher` package
- [x] Add error handling

### Task 2.4: Grid Layout
- [x] Create `lib/widgets/category_view.dart`
- [x] Implement `GridView.builder` with 3 columns
- [x] Add hardcoded app shortcuts (3-4 apps)
- [x] Test: Icons display and apps launch

### Task 2.5: Dynamic App Cards with Add Button ⭐ **COMPLETED**
- [x] Add "+" button card to grid layout
- [x] Implement app picker dialog/modal
- [x] Add method to `AppState` to add new app shortcuts
- [x] Update state management to support dynamic app list
- [x] Test: Add button opens picker, new apps appear in grid
- [x] All tests passing (28/28 tests)
- [x] **Browse Button Feature:**
  - Added "Browse" button next to URL/Path field
  - File picker for .exe, .lnk, .bat, .cmd files
  - Auto-fill app name from file name
  - Clean file name formatting (remove underscores, capitalize)
  - Error handling for file browsing
  - **Clean Code applied:**
    - `_browseFile()` - File selection logic
    - `_populateFieldsFromFile()` - Populate form fields
    - `_extractFileName()` - Extract file name
    - `_cleanFileName()` - Clean up file name
    - `_showError()` - Error handling
  - All 41 tests passing
- [x] **Notion-Style Icon Picker ⭐ COMPLETED:**
  - Three-tab icon picker dialog (Emoji / Icons / Upload)
  - **Emoji Tab:** 48 commonly used emojis in grid layout (10 columns, rounded rectangles)
  - **Icons Tab:** Material Design icons collection (48 icons, 10 columns)
  - **Upload Tab:** Custom image upload with drag & drop support
  - Search/filter functionality for finding icons
  - Icon preview in App Picker Dialog (compact 40x40 size)
  - **Context Menu:** "Change Icon" option added
  - **Add/Edit Dialog:** Icon selector integrated with scrollable content
  - **AppCard Rendering:** Supports emoji, material icons, and custom images
  - **UI/UX Improvements:**
    - Wider dialog (650px) for better grid visibility
    - Larger emojis (32px) and icons (28px) for better readability
    - Rounded rectangles instead of circles (Notion-style)
    - **Proper spacing (8px)** between grid items (fixed overlap issues)
    - Compact icon preview (40x40) in forms
    - **Real drag & drop** using `desktop_drop` package
    - SingleChildScrollView for overflow prevention
    - **Red borders** added for visual testing (test mode)
    - **LayoutBuilder** added for proper grid rendering in TabBarView
    - **AlwaysScrollableScrollPhysics** for proper scrolling
  - **Visual Testing Infrastructure ⭐ NEW:**
    - **Python visual matching tests** (`test/visual/visual_icon_test.py`)
    - Screenshot-based validation
    - Red border detection and overlap checking
    - Centering and padding validation
    - Automated test runner (`run_visual_tests.py`)
    - Windows batch script for easy testing (`run_flutter_and_test.bat`)
  - **Overflow Testing:**
    - Automated overflow detection tests added
    - All overflow issues resolved (75/75 tests passing)
    - Tests automatically catch layout issues
    - **Visual validation tests** added for spacing/overlap
  - **Clean Code applied:**
    - `IconPickerDialog` - Separate widget with single responsibility
    - `IconPickerResult` - Data model for icon selection
    - `IconType` enum - Type safety for icon types
    - `_buildIconPreview()` - Icon preview widget
    - `_selectIcon()` - Icon selection handler
    - Icon rendering extracted to separate methods in AppCard
    - Overflow tests ensure robustness
  - All 75 tests passing (56 Flutter + 5 visual validation + 14 golden)
- [x] **Icon Infrastructure Prepared:**
  - `IconExtractionService` created for future enhancement
  - `AppShortcut.iconPath` field ready for custom icons
  - Win32 package added for Windows API access
  - Currently using Material Design icons (type-based)
  - **Future Enhancement:** Full icon extraction from .exe files

---

## 📑 Phase 3: Tab System

### Task 3.1: State Management Setup
- [x] Create `lib/providers/app_state.dart`
- [x] Implement Provider pattern
- [x] Add categories list (Music, Notes, AI)
- [x] Add selected category tracking

### Task 3.2: Tab Bar Implementation
- [x] Add `TabBar` to main window
- [x] Add `TabBarView` with category views
- [x] Implement category filtering logic
- [x] Test: Tabs switch and filter content

### Task 3.3: Scrollable Tabs ⭐ **COMPLETED**
- [x] Make `TabBar` scrollable when tabs overflow
- [x] Add `isScrollable: true` to `TabBar` widget
- [x] Test: Multiple tabs scroll horizontally when needed
- [x] Ensure tab indicator works correctly with scrolling
- [x] Replaced ChoiceChip with TabBar/TabController
- [x] All 5 scrollable tab tests passing
- [x] Mouse wheel navigation (scroll to switch tabs)
- [x] Mouse drag navigation (click and drag)
- [x] Touch swipe support
- [x] **Refactored with Clean Code principles:**
  - Extracted `_handleTabScroll()` for event handling
  - Extracted `_navigateToTab()` for navigation logic
  - Extracted `_buildTabBarDecoration()` for styling
  - Extracted `_buildScrollBehavior()` for scroll config
  - Extracted `_buildTabs()` for tab widget creation
  - Single Responsibility Principle applied
  - OOP best practices followed

### Task 3.4: Persistence & Observability ⭐ **COMPLETED**
- [x] Implement `services/storage_service.py` to read/write `%LOCALAPPDATA%\MyEverythingWidget\app_state.json`
- [x] Update `AppState` to load saved tabs/apps and persist on add/update/remove (env var `MEW_STATE_PATH` supported)
- [x] Document persistence behavior and logging guidance in `README.md`
- [x] Add logging hooks for tab clicks, wheel navigation, and scroll buttons to trace navigation flow
- [ ] Wheel scroll still feels delayed compared to scroll buttons; track smoothing fix

---

## 📝 Phase 4: Notes Feature

### Task 4.1: Note Model
- [x] Create `window/models/note.py` (or equivalent) for Python implementation
- [x] Define `Note` dataclass with `id`, `content`, `type`, `category`, `created_at`, `updated_at`
- [x] Define `NoteType` enum (text, image, link, file) plus helper properties
- [x] Implement serialization helpers that round-trip to JSON/dict for storage
- [x] Write unit tests covering defaults, equality, serialization, and validation hooks

### Task 4.2: Note Card Widget
- [x] Create `widgets/note_card.py` with `NoteCard` QWidget that takes a `Note`
- [x] Render icon/emoji + truncated text, show tooltip with full content on hover
- [x] Add copy-to-clipboard button and optional delete button/hamburger menu
- [x] Support drag handles anchor for future reorder phase
- [x] Cover widget with pytest-qt tests verifying layout, tooltip, copy/delete signals

### Task 4.3: Note List
- [x] Extend `AppState` to store an ordered list of notes, persist them with storage service
- [x] Add filtering helpers and command objects for copying/deleting notes
- [x] Build a dedicated notes tab/view showing `NoteCard` widgets in a scrollable flow layout
- [x] Support swipe/drag gestures, context menu (copy/delete), and placeholder when empty
- [x] Add integration tests covering rendering, filtering, persistence, and placeholder state
- [x] Refactor phase 4 artifacts to confirm each class/method maintains a single responsibility and clean OOP boundaries
- [ ] Replace the standalone notes tab with an in-grid overlay: allow notes to span multiple columns, use an icon-only copy button, expose edit/delete via the tab context menu, and address the timezone-aware datetime/Qt reference warnings before moving on

---

## 📋 Phase 5: Clipboard Paste (Ctrl+V) ✅ COMPLETED

### Task 5.1: Keyboard Handler ✅
- [x] Create `services/clipboard_service.py` to normalize clipboard mime types (text/image)
- [x] Hook `MainWindow.keyPressEvent` to detect `Ctrl+V` when widget is focused
- [x] 6 unit tests passing for clipboard service

### Task 5.2: Image Paste ✅
- [x] Detect image data on clipboard
- [x] Save to `data/images/` with UUID names
- [x] Create `NoteType.IMAGE` entry referencing stored file
- [x] Auto-calculate grid span based on aspect ratio (ImageGridCalculator)
- [x] 12 tests for grid calculator, 8 tests for ImageCard

### Task 5.3: Add Image Button ✅
- [x] Floating button (🖼️) to add images from file
- [x] File dialog for PNG, JPG, JPEG, BMP, GIF
- [x] Integration with DialogManager

**Total: 26 new tests passing**

---

## 🔧 Phase 5.5: Note Widget Fixes (IN PROGRESS)

### Kritik Hatalar
- [x] Add a quick note satırı bazı sekmelerde aşağı kaymış - düzelt
- [x] App card'lar ile note input arasında çok fazla boşluk var - düzelt
- [x] Note'larda "TEXT" yazısı görünüyor - kaldır
- [x] Note boyutu içeriğe göre değişiyor - sabit boyut olmalı (2x1 veya 3x1)
- [x] Notes sekmesi kaldırıldı (gereksiz)
- [ ] Grid spacing - görseller arası çok boşluk var, düzgün oturmuyor
- [ ] App card ile note arasında fazla boşluk var

### Özellik Düzeltmeleri
- [x] Notes ayrı sayfa olmayacak - normal sekmelerde grid üstüne eklenecek
- [x] Copy butonu küçük kare ikon olacak
- [x] Delete butonu note üzerinde olmayacak - sağ tık menüsünde olacak
- [x] Edit butonu sağ tık menüsünde olacak
- [x] Not boyutu sabit: 2 veya 3 card genişliğinde

### Grid Kuralları
- Note genişlik: 2x1 veya 3x1 (sabit)
- Image genişlik: aspect ratio'ya göre (1x1, 1x2, 2x1, 2x2, 3x1, 3x2, vb.)
- App card: 1x1 (sabit)

### Performans Sorunları (KRİTİK)
- [ ] **7GB RAM kullanımı** - Hedef: 100MB
- [ ] **%8 CPU kullanımı** - Sekmeler arası geçiş çok yavaş
- [ ] Debug logları veya memory leak olabilir
- [ ] Tab switch optimize edilmeli

---

## ✨ Phase 6: Polish & Testing

### Task 6.1: Theme Support
- [ ] Introduce `ThemeMode` enum (light/dark/auto) and `ThemeManager` service
- [ ] Apply palette/style updates via shared stylesheet helper for windows, tabs, notes, dialogs
- [ ] Persist choice in storage, emit signal for UI components to refresh
- [ ] Add tests verifying theme persistence and palette changes

### Task 6.2: Manual Testing
- [ ] Maintain checklist documentation covering: window drag, launcher, tabs, notes, clipboard
- [ ] Automate screenshot capture/logging for critical flows (tab scroll, note view, clipboard)
- [ ] Document regression issues discovered during nightly runs and tag in tracker

- [ ] Prioritize and triage logged issues (wheel lag, persistence, clipboard)
- [ ] Improve test coverage for uncovered flows (notes persistence, clipboard, theme)
- [ ] Refactor/cleanup once functionality stabilized

### Task 6.4: Automated Testing
- [ ] Ensure pytest suite covers AppState, notes, clipboard, main window integration
- [ ] Add fixture-driven visual regression harness referencing `tests/visual` for future expansion
- [ ] Refactor automated testing helpers so each fixture and utility class stays focused and stateless

## 🧩 Phase 7: Drag & Drop Reordering

### Task 7.1: App/Card Reordering
- [ ] Allow app cards to be drag-and-drop re-sequenced within each category grid
- [ ] Persist ordering in `AppState` and storage service
- [ ] Add tests simulating drag events and verifying ordering/persistence

### Task 7.2: Note Reordering
- [ ] Enable drag handles on `NoteCard` to reorder notes within a category
- [ ] Support keyboard reorder shortcuts (Ctrl+↑/Ctrl+↓)
- [ ] Write integration tests covering drag, keyboard commands, and UI re-rendering

### Task 7.3: Image Note Reordering
- [ ] Allow image notes to be repositioned via drag/drop
- [ ] Ensure scoped drop targets to avoid mixing with app grid
- [ ] Verify persistence and state restoration for reordered image notes
- [ ] Validate drag/drop classes and handlers follow clean-OOP single-responsibility boundaries
---

## 📦 Phase 8: Deployment

### Task 8.1: MSIX Configuration
- [ ] Configure `msix_config` in `pubspec.yaml`
- [ ] Add application logo and assets
- [ ] Set display name and publisher info

### Task 8.2: Build & Package
- [ ] Run `flutter build windows --release`
- [ ] Generate MSIX package (`flutter pub run msix:create`)
- [ ] Test MSIX installation
- [ ] Verify app launches from Start Menu

### Task 8.3: Documentation
- [ ] Update README.md with features
- [ ] Add screenshots
- [ ] Document installation instructions
- [ ] Add contribution guidelines
- [ ] Refactor deployment-related docs/tools to ensure they stay modular and versioned separately

---

## ✅ Completion Criteria

### MVP Must-Haves
- [ ] Window is draggable and always-on-top
- [ ] 3-4 hardcoded applications display in grid
- [ ] Clicking app icons launches applications
- [ ] 3 tabs exist (Music, Notes, AI)
- [ ] Tab switching filters content correctly
- [ ] Notes display with copy button
- [ ] Copy button copies to clipboard
- [ ] Ctrl+V pastes text content
- [ ] Ctrl+V pastes images
- [ ] MSIX package builds successfully

### Out of Scope for v1.0
- ❌ Command runner
- ❌ Settings page
- ❌ System tray integration
- ❌ Global hotkeys
- ❌ SQLite persistence
- ❌ Cloud sync

---

## 🐛 Known Issues

### Future Enhancements (Not in Current Sprint)
- [ ] **Settings page**: Theme toggle, startup options (Phase 6.1)
- [ ] **System tray integration**: Minimize to tray functionality (Phase 6+)
- [ ] **SQLite persistence**: Save apps and notes to database (Phase 6+)
- [ ] **Command runner**: Execute system commands (Future Phase)

---

## 📊 Progress Tracking

**Current Phase:** Phase 3 (Tab System) - COMPLETED ✅
**Completion:** 100% (Phase 3)
**Recent Completion:** Notion-Style Icon Picker ⭐

### Phase Checklist
- [x] Phase 1: Project Setup & Core Window ✅
- [x] Phase 2: Application Launcher ✅
- [x] Phase 3: Tab System ✅
- [ ] Phase 4: Notes Feature
- [ ] Phase 5: Clipboard Paste
- [ ] Phase 6: Polish & Testing
- [ ] Phase 7: Deployment

### Today's Priority Tasks ✅ COMPLETED
1. ✅ **Task 3.3**: Scrollable Tabs - DONE
2. ✅ **Task 2.5**: Dynamic App Cards with Add Button - DONE
3. ✅ **Icon Picker Feature**: Notion-style Icon Selection - DONE
4. ✅ **Icon Picker UX**: Overflow fixes, larger emojis, drag & drop - DONE

---

## 🔗 Related Documents
- [ANALYSIS.md](./ANALYSIS.md) - Technical analysis and platform selection
- [README.md](../../../README.md) - Project overview

---

**Commit Format:** `[MEW-1] Description`
**Example:** `[MEW-1] Setup Flutter project structure`