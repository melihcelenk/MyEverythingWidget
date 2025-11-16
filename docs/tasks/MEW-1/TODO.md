# MEW-1: Development Tasks

## 📋 Task Overview

This document outlines the development tasks for MyEverythingWidget v1.0 MVP.

---

## 🚀 Phase 1: Project Setup & Core Window

### Task 1.1: Environment Setup
- [ ] Verify Flutter installation (`flutter doctor`)
- [ ] Create Flutter project (`flutter create my_everything_widget --platforms=windows,linux`)
- [ ] Initialize Git repository
- [ ] Add required packages to `pubspec.yaml`
  - `window_manager: ^0.3.7`
  - `provider: ^6.1.0`
  - `clipboard_watcher: ^0.2.0`
  - `msix: ^3.16.0`

### Task 1.2: Main Window Implementation
- [ ] Create `lib/screens/main_window.dart`
- [ ] Implement custom title bar
- [ ] Add drag-to-move functionality
- [ ] Configure always-on-top toggle
- [ ] Set window size to 320x500
- [ ] Test: Window opens and is draggable

---

## 🎯 Phase 2: Application Launcher

### Task 2.1: Data Models
- [ ] Create `lib/models/app_shortcut.dart`
- [ ] Define `AppShortcut` class with properties:
  - `id`, `name`, `iconPath`, `target`, `category`, `type`
- [ ] Define `LaunchType` enum (exe, uwp, url)

### Task 2.2: App Card Widget
- [ ] Create `lib/widgets/app_card.dart`
- [ ] Implement icon + text layout
- [ ] Add tap gesture handler
- [ ] Style card with Material Design

### Task 2.3: App Launcher Service
- [ ] Create `lib/services/app_launcher.dart`
- [ ] Implement launch logic for different types:
  - EXE: `Process.start()`
  - URL: `url_launcher` package
- [ ] Add error handling

### Task 2.4: Grid Layout
- [ ] Create `lib/widgets/category_view.dart`
- [ ] Implement `GridView.builder` with 3 columns
- [ ] Add hardcoded app shortcuts (3-4 apps)
- [ ] Test: Icons display and apps launch

---

## 📑 Phase 3: Tab System

### Task 3.1: State Management Setup
- [ ] Create `lib/providers/app_state.dart`
- [ ] Implement Provider pattern
- [ ] Add categories list (Music, Notes, AI)
- [ ] Add selected category tracking

### Task 3.2: Tab Bar Implementation
- [ ] Add `TabBar` to main window
- [ ] Add `TabBarView` with category views
- [ ] Implement category filtering logic
- [ ] Test: Tabs switch and filter content

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
- ❌ Application picker (+ button)
- ❌ Settings page
- ❌ System tray integration
- ❌ Global hotkeys
- ❌ SQLite persistence
- ❌ Cloud sync

---

## 🐛 Known Issues

### UI Layout Issues
- [ ] **Tab bar overflow**: Media tab is cut off at window edge
- [ ] **App card text overflow**: "Stack Overflow" second word not visible
- [ ] **Window width**: Consider increasing from 320px to accommodate content

### Suggested Fixes
1. Increase window width to 380px or make tabs scrollable
2. Reduce app card text size or use smaller font
3. Add ellipsis for long app names

---

## 📊 Progress Tracking

**Current Phase:** Phase 3 (Tab System)
**Completion:** 60%

### Phase Checklist
- [x] Phase 1: Project Setup & Core Window
- [x] Phase 2: Application Launcher
- [x] Phase 3: Tab System
- [ ] Phase 4: Notes Feature
- [ ] Phase 5: Clipboard Paste
- [ ] Phase 6: Polish & Testing
- [ ] Phase 7: Deployment

---

## 🔗 Related Documents
- [ANALYSIS.md](./ANALYSIS.md) - Technical analysis and platform selection
- [README.md](../../../README.md) - Project overview

---

**Commit Format:** `[MEW-1] Description`
**Example:** `[MEW-1] Setup Flutter project structure`