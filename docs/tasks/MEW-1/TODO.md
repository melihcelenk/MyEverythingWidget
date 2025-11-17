# MEW-1: Development Tasks

## 📋 Task Overview

This document outlines the development tasks for MyEverythingWidget v1.0 MVP.

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

### Task 2.5: Dynamic App Cards with Add Button ⭐ **PRIORITY TODAY**
- [x] Add "+" button card to grid layout
- [x] Implement app picker dialog/modal
- [x] Add method to `AppState` to add new app shortcuts
- [x] Update state management to support dynamic app list
- [x] Test: Add button opens picker, new apps appear in grid
- [x] All tests passing (28/28 tests)

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

### Task 3.3: Scrollable Tabs ⭐ **PRIORITY TODAY**
- [ ] Make `TabBar` scrollable when tabs overflow
- [ ] Add `isScrollable: true` to `TabBar` widget
- [ ] Test: Multiple tabs scroll horizontally when needed
- [ ] Ensure tab indicator works correctly with scrolling

---

## 📝 Phase 4: Notes Feature

### Task 4.1: Note Model
- [ ] Create `lib/models/note.dart`
- [ ] Define `Note` class with properties:
  - `id`, `content`, `type`, `category`, `createdAt`, `updatedAt`
- [ ] Define `NoteType` enum (text, image)

### Task 4.2: Note Card Widget
- [ ] Create `lib/widgets/note_card.dart`
- [ ] Implement note display with text content
- [ ] Add copy button with `Clipboard.setData()`
- [ ] Show SnackBar confirmation ("Copied!")
- [ ] Test: Copy functionality works

### Task 4.3: Note List
- [ ] Add hardcoded notes to state
- [ ] Display notes in category view
- [ ] Implement scrollable list
- [ ] Test: Notes display correctly

---

## 📋 Phase 5: Clipboard Paste (Ctrl+V)

### Task 5.1: Keyboard Handler
- [ ] Create `lib/services/clipboard_service.dart`
- [ ] Implement `KeyboardListener` for Ctrl+V
- [ ] Add focus management

### Task 5.2: Text Paste
- [ ] Implement text clipboard detection
- [ ] Create new note from pasted text
- [ ] Add note to current category
- [ ] Test: Ctrl+V pastes text

### Task 5.3: Image Paste
- [ ] Implement image clipboard detection
- [ ] Save image to local storage
- [ ] Create note with image path
- [ ] Test: Ctrl+V pastes images

---

## ✨ Phase 6: Polish & Testing

### Task 6.1: Theme Support
- [ ] Implement light/dark theme toggle
- [ ] Apply theme to all widgets
- [ ] Persist theme preference

### Task 6.2: Manual Testing
- [ ] Window functionality checklist
- [ ] Application launcher checklist
- [ ] Tab system checklist
- [ ] Notes feature checklist
- [ ] Document any issues

### Task 6.3: Bug Fixes
- [ ] Address issues found during testing
- [ ] Optimize performance if needed
- [ ] Clean up code and comments

---

## 📦 Phase 7: Deployment

### Task 7.1: MSIX Configuration
- [ ] Configure `msix_config` in `pubspec.yaml`
- [ ] Add application logo and assets
- [ ] Set display name and publisher info

### Task 7.2: Build & Package
- [ ] Run `flutter build windows --release`
- [ ] Generate MSIX package (`flutter pub run msix:create`)
- [ ] Test MSIX installation
- [ ] Verify app launches from Start Menu

### Task 7.3: Documentation
- [ ] Update README.md with features
- [ ] Add screenshots
- [ ] Document installation instructions
- [ ] Add contribution guidelines

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

**Current Phase:** Phase 3 (Tab System) - In Progress
**Completion:** 75%

### Phase Checklist
- [x] Phase 1: Project Setup & Core Window ✅
- [x] Phase 2: Application Launcher ✅ (Task 2.5 in progress)
- [x] Phase 3: Tab System (Task 3.3 in progress)
- [ ] Phase 4: Notes Feature
- [ ] Phase 5: Clipboard Paste
- [ ] Phase 6: Polish & Testing
- [ ] Phase 7: Deployment

### Today's Priority Tasks
1. ⭐ **Task 3.3**: Scrollable Tabs
2. ⭐ **Task 2.5**: Dynamic App Cards with Add Button

---

## 🔗 Related Documents
- [ANALYSIS.md](./ANALYSIS.md) - Technical analysis and platform selection
- [README.md](../../../README.md) - Project overview

---

**Commit Format:** `[MEW-1] Description`
**Example:** `[MEW-1] Setup Flutter project structure`